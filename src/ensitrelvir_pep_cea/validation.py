from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd

from .analysis import run_scenario
from .io import (
    load_acute_death_cohort,
    load_evidence_register,
    load_extrapolation_register,
    load_input_traceability_targets,
    load_life_table,
    load_parameter_frame,
    load_pep_microcost,
    load_postacute_utility_profile,
    load_scenarios,
    load_trial_effect_frame,
    load_trial_frame,
    load_utility_norms,
    repository_root,
)
from .model import VALID_STRUCTURAL_MODES


@dataclass(frozen=True)
class ValidationIssue:
    severity: str
    check_id: str
    message: str


def _check_source_ids(
    frame: pd.DataFrame,
    column: str,
    valid_source_ids: set[str],
    dataset_name: str,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    observed = set(frame[column].dropna().astype(str))
    missing = sorted(observed.difference(valid_source_ids))
    if missing:
        issues.append(
            ValidationIssue(
                severity="error",
                check_id=f"source_ids_{dataset_name}",
                message=f"Unresolved source IDs in {dataset_name}: {missing}",
            )
        )
    return issues


def validate_repository_inputs() -> list[ValidationIssue]:
    """Run machine-readable integrity checks over all model inputs."""

    issues: list[ValidationIssue] = []
    parameters = load_parameter_frame()
    evidence = load_evidence_register()
    trials = load_trial_frame()
    trial_effects = load_trial_effect_frame()
    scenarios = load_scenarios()
    validation_targets = load_input_traceability_targets()
    extrapolations = load_extrapolation_register()
    microcost = load_pep_microcost()
    postacute_profile = load_postacute_utility_profile()
    acute_death_cohort = load_acute_death_cohort()
    life_table = load_life_table()
    utility_norms = load_utility_norms()
    subgroup_extrapolations = pd.read_csv(
        repository_root() / "data" / "subgroup_hospitalization_extrapolations.csv",
        encoding="utf-8-sig",
    )

    # Numeric parameter bounds and identifiers.
    out_of_bounds = parameters.loc[
        (parameters["base_value"] < parameters["lower_value"])
        | (parameters["base_value"] > parameters["upper_value"])
    ]
    if not out_of_bounds.empty:
        issues.append(
            ValidationIssue(
                severity="error",
                check_id="parameter_bounds",
                message=(
                    "Base values outside deterministic ranges: "
                    + ", ".join(out_of_bounds["parameter_id"].astype(str))
                ),
            )
        )

    if parameters[["base_value", "lower_value", "upper_value"]].isna().any().any():
        issues.append(
            ValidationIssue(
                severity="error",
                check_id="parameter_missing_numeric",
                message="parameters.csv contains missing base or range values.",
            )
        )

    # Evidence provenance is a foreign-key relationship, including internal assumptions.
    valid_source_ids = set(evidence["source_id"].astype(str))
    issues.extend(_check_source_ids(parameters, "source_id", valid_source_ids, "parameters"))
    issues.extend(_check_source_ids(trials, "source_id", valid_source_ids, "trial_event_counts"))
    issues.extend(
        _check_source_ids(
            trial_effects,
            "source_id",
            valid_source_ids,
            "trial_effect_estimates",
        )
    )
    issues.extend(
        _check_source_ids(
            validation_targets,
            "source_id",
            valid_source_ids,
            "input_traceability_targets",
        )
    )
    for dataset_name, frame in (
        ("extrapolation_register", extrapolations),
        ("pep_microcost_japan_2026", microcost),
        ("postacute_utility_profile_japan_2025", postacute_profile),
        ("acute_death_cohort_japan_2025", acute_death_cohort),
        ("life_table_japan_2025", life_table),
        ("utility_norms_japan_eq5d5l_2021", utility_norms),
        ("subgroup_hospitalization_extrapolations", subgroup_extrapolations),
    ):
        issues.extend(
            _check_source_ids(frame, "source_id", valid_source_ids, dataset_name)
        )

    # Exact trial counts must reconcile with displayed probabilities.
    exact = trials.loc[trials["events"].notna()].copy()
    if not exact.empty:
        exact["calculated_probability"] = exact["events"] / exact["n"]
        discordant = exact.loc[
            ~np.isclose(
                exact["calculated_probability"],
                exact["reported_probability"],
                atol=5e-5,
                rtol=0.0,
            )
        ]
        if not discordant.empty:
            keys = discordant[["population", "outcome", "arm"]].astype(str).agg("/".join, axis=1)
            issues.append(
                ValidationIssue(
                    severity="error",
                    check_id="trial_count_probability_reconciliation",
                    message="Trial counts do not reconcile with probabilities: " + ", ".join(keys),
                )
            )

    if ((trials["reported_probability"] < 0) | (trials["reported_probability"] > 1)).any():
        issues.append(
            ValidationIssue(
                severity="error",
                check_id="trial_probability_bounds",
                message="Trial probabilities must be between zero and one.",
            )
        )

    invalid_effects = trial_effects.loc[
        (trial_effects["lower_95"] <= 0)
        | (trial_effects["estimate"] < trial_effects["lower_95"])
        | (trial_effects["estimate"] > trial_effects["upper_95"])
    ]
    if not invalid_effects.empty:
        keys = (
            invalid_effects[["population", "outcome", "effect_measure"]]
            .astype(str)
            .agg("/".join, axis=1)
        )
        issues.append(
            ValidationIssue(
                severity="error",
                check_id="trial_effect_interval_ordering",
                message="Invalid trial effect estimates or confidence intervals: "
                + ", ".join(keys),
            )
        )

    unsupported_effect_measures = sorted(
        set(trial_effects["effect_measure"].astype(str)).difference({"risk_ratio"})
    )
    if unsupported_effect_measures:
        issues.append(
            ValidationIssue(
                severity="error",
                check_id="trial_effect_measure",
                message=(
                    "Unsupported trial effect measures: "
                    f"{unsupported_effect_measures}"
                ),
            )
        )

    trial_keys = set(zip(trials["population"], trials["outcome"], strict=False))
    effect_keys = set(
        zip(trial_effects["population"], trial_effects["outcome"], strict=False)
    )
    missing_trial_rows = sorted(effect_keys.difference(trial_keys))
    if missing_trial_rows:
        issues.append(
            ValidationIssue(
                severity="error",
                check_id="trial_effect_trial_row_link",
                message=f"Effect estimates lack matching trial rows: {missing_trial_rows}",
            )
        )

    # Scenario metadata and override referential integrity.
    invalid_modes = sorted(
        set(scenarios["structural_mode"].astype(str)).difference(VALID_STRUCTURAL_MODES)
    )
    if invalid_modes:
        issues.append(
            ValidationIssue(
                severity="error",
                check_id="scenario_structural_modes",
                message=f"Unknown structural modes: {invalid_modes}",
            )
        )

    root = repository_root()
    overrides = pd.read_csv(root / "data" / "scenario_overrides.csv", encoding="utf-8-sig")
    unknown_scenarios = sorted(
        set(overrides["scenario_id"].astype(str)).difference(
            set(scenarios["scenario_id"].astype(str))
        )
    )
    unknown_parameters = sorted(
        set(overrides["parameter_id"].astype(str)).difference(
            set(parameters["parameter_id"].astype(str))
        )
    )
    if unknown_scenarios:
        issues.append(
            ValidationIssue(
                severity="error",
                check_id="scenario_override_ids",
                message=f"Overrides reference unknown scenarios: {unknown_scenarios}",
            )
        )
    if unknown_parameters:
        issues.append(
            ValidationIssue(
                severity="error",
                check_id="scenario_override_parameters",
                message=f"Overrides reference unknown parameters: {unknown_parameters}",
            )
        )

    # Execute every declared scenario to trigger model-level validation.
    for scenario_id in scenarios["scenario_id"].astype(str):
        try:
            run_scenario(scenario_id, parameters)
        except Exception as exc:  # pragma: no cover: preserves the original validation message
            issues.append(
                ValidationIssue(
                    severity="error",
                    check_id=f"scenario_execution_{scenario_id}",
                    message=f"Scenario '{scenario_id}' failed input validation: {exc}",
                )
            )

    return issues


def issues_to_frame(issues: Iterable[ValidationIssue]) -> pd.DataFrame:
    rows = [issue.__dict__ for issue in issues]
    if not rows:
        rows = [
            {
                "severity": "ok",
                "check_id": "all_input_checks",
                "message": "All repository input checks passed.",
            }
        ]
    return pd.DataFrame(rows)
