from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class Scenario:
    """Scenario metadata loaded from data/scenarios.csv."""

    scenario_id: str
    trial_population: str
    structural_mode: str
    perspective: str
    primary_analysis: bool
    description_ja: str
    description_en: str


def repository_root() -> Path:
    """Return the repository root, assuming a standard src layout."""

    return Path(__file__).resolve().parents[2]


def data_path(filename: str) -> Path:
    return repository_root() / "data" / filename


def _read_csv(filename: str) -> pd.DataFrame:
    path = data_path(filename)
    if not path.exists():
        raise FileNotFoundError(f"Required input file does not exist: {path}")
    return pd.read_csv(path, encoding="utf-8-sig")


def load_parameter_frame() -> pd.DataFrame:
    """Load and validate the long-format parameter register."""

    frame = _read_csv("parameters.csv")
    required = {
        "parameter_id",
        "base_value",
        "lower_value",
        "upper_value",
        "distribution",
        "include_in_psa",
        "include_in_dsa",
    }
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"parameters.csv is missing columns: {sorted(missing)}")
    if frame["parameter_id"].duplicated().any():
        duplicates = frame.loc[frame["parameter_id"].duplicated(), "parameter_id"].tolist()
        raise ValueError(f"Duplicate parameter IDs: {duplicates}")
    for column in ["base_value", "lower_value", "upper_value"]:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    return frame


def base_parameters(parameter_frame: pd.DataFrame | None = None) -> dict[str, float]:
    frame = load_parameter_frame() if parameter_frame is None else parameter_frame
    return dict(zip(frame["parameter_id"], frame["base_value"].astype(float), strict=True))


def load_scenarios() -> pd.DataFrame:
    frame = _read_csv("scenarios.csv")
    required = {
        "scenario_id",
        "trial_population",
        "structural_mode",
        "perspective",
        "primary_analysis",
        "description_ja",
        "description_en",
    }
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"scenarios.csv is missing columns: {sorted(missing)}")
    return frame


def load_scenario(scenario_id: str) -> Scenario:
    frame = load_scenarios()
    matches = frame.loc[frame["scenario_id"] == scenario_id]
    if len(matches) != 1:
        choices = ", ".join(frame["scenario_id"].astype(str).tolist())
        raise KeyError(f"Unknown scenario '{scenario_id}'. Available scenarios: {choices}")
    row = matches.iloc[0]
    return Scenario(
        scenario_id=str(row["scenario_id"]),
        trial_population=str(row["trial_population"]),
        structural_mode=str(row["structural_mode"]),
        perspective=str(row["perspective"]),
        primary_analysis=str(row["primary_analysis"]).strip().lower() == "yes",
        description_ja=str(row["description_ja"]),
        description_en=str(row["description_en"]),
    )


def apply_scenario_overrides(
    params: dict[str, float], scenario_id: str
) -> dict[str, float]:
    """Return a copy of parameters with long-format scenario overrides applied."""

    overrides = _read_csv("scenario_overrides.csv")
    selected = overrides.loc[overrides["scenario_id"] == scenario_id]
    updated = dict(params)
    for row in selected.itertuples(index=False):
        if row.parameter_id not in updated:
            raise KeyError(
                f"Scenario '{scenario_id}' overrides unknown parameter "
                f"'{row.parameter_id}'."
            )
        updated[str(row.parameter_id)] = float(row.override_value)
    return updated


def load_evidence_register() -> pd.DataFrame:
    """Load the source and internal-assumption provenance register."""

    frame = _read_csv("evidence_register.csv")
    required = {"source_id", "citation", "used_for", "limitations"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"evidence_register.csv is missing columns: {sorted(missing)}")
    if frame["source_id"].duplicated().any():
        duplicates = frame.loc[frame["source_id"].duplicated(), "source_id"].tolist()
        raise ValueError(f"Duplicate source IDs: {duplicates}")
    return frame



def load_extrapolation_register() -> pd.DataFrame:
    """Load the parameter-level external-validity and extrapolation register."""

    frame = _read_csv("extrapolation_register.csv")
    required = {
        "extrapolation_id",
        "parameter_id",
        "target_quantity",
        "source_population",
        "target_population",
        "transformation",
        "uncertainty_strategy",
        "residual_risk",
        "source_id",
    }
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(
            f"extrapolation_register.csv is missing columns: {sorted(missing)}"
        )
    if frame["extrapolation_id"].duplicated().any():
        duplicates = frame.loc[
            frame["extrapolation_id"].duplicated(), "extrapolation_id"
        ].tolist()
        raise ValueError(f"Duplicate extrapolation IDs: {duplicates}")
    return frame


def load_pep_microcost() -> pd.DataFrame:
    """Load itemized FY2026 PEP delivery reimbursement components."""

    frame = _read_csv("pep_microcost_japan_2026.csv")
    required = {
        "component_id", "points", "jpy_per_point", "cost_jpy", "source_id",
        "basecase_included"
    }
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"pep_microcost_japan_2026.csv is missing columns: {sorted(missing)}")
    for column in ["points", "jpy_per_point", "cost_jpy"]:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    return frame


def load_postacute_utility_profile() -> pd.DataFrame:
    """Load the Japanese one-year post-acute EQ-5D-5L profile."""

    frame = _read_csv("postacute_utility_profile_japan_2025.csv")
    required = {
        "interval_id", "start_month", "end_month", "duration_months",
        "utility_covid", "utility_control", "utility_decrement", "qaly_loss",
        "source_id"
    }
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(
            f"postacute_utility_profile_japan_2025.csv is missing columns: {sorted(missing)}"
        )
    for column in [
        "start_month", "end_month", "duration_months", "utility_covid",
        "utility_control", "utility_decrement", "qaly_loss"
    ]:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    return frame


def load_acute_death_cohort() -> pd.DataFrame:
    return _read_csv("acute_death_cohort_japan_2025.csv")


def load_life_table() -> pd.DataFrame:
    return _read_csv("life_table_japan_2025.csv")


def load_utility_norms() -> pd.DataFrame:
    return _read_csv("utility_norms_japan_eq5d5l_2021.csv")

def load_input_traceability_targets() -> pd.DataFrame:
    """Load registered values for input traceability and external face-validity checks.

    These checks are verification aids and are not predictive external validation.
    """

    frame = _read_csv("input_traceability_targets.csv")
    required = {
        "check_id",
        "check_type",
        "metric",
        "observed_value",
        "unit",
        "source_id",
        "model_comparison",
        "notes",
    }
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(
            f"input_traceability_targets.csv is missing columns: {sorted(missing)}"
        )
    frame["observed_value"] = pd.to_numeric(frame["observed_value"], errors="raise")
    return frame


def load_external_validation_targets() -> pd.DataFrame:
    """Backward-compatible alias for pre-v0.3 code."""

    return load_input_traceability_targets()


def load_trial_frame() -> pd.DataFrame:
    frame = _read_csv("trial_event_counts.csv")
    required = {
        "population",
        "outcome",
        "arm",
        "n",
        "reported_probability",
    }
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"trial_event_counts.csv is missing columns: {sorted(missing)}")
    frame["n"] = pd.to_numeric(frame["n"], errors="raise")
    frame["reported_probability"] = pd.to_numeric(
        frame["reported_probability"], errors="raise"
    )
    frame["events"] = pd.to_numeric(frame["events"], errors="coerce")
    return frame


def trial_probabilities(
    population: str,
    outcome: str = "symptomatic_covid_day10",
    trial_frame: pd.DataFrame | None = None,
) -> dict[str, float]:
    frame = load_trial_frame() if trial_frame is None else trial_frame
    selected = frame.loc[
        (frame["population"] == population) & (frame["outcome"] == outcome)
    ]
    expected_arms = {"pep", "no_pep"}
    observed_arms = set(selected["arm"].astype(str))
    if observed_arms != expected_arms:
        raise ValueError(
            f"Expected arms {sorted(expected_arms)} for population={population}, "
            f"outcome={outcome}; found {sorted(observed_arms)}."
        )
    return {
        str(row.arm): float(row.reported_probability)
        for row in selected.itertuples(index=False)
    }


def trial_rows(
    population: str,
    outcome: str,
    trial_frame: pd.DataFrame | None = None,
) -> dict[str, dict[str, Any]]:
    """Return arm-specific trial rows for probabilistic sampling."""

    frame = load_trial_frame() if trial_frame is None else trial_frame
    selected = frame.loc[
        (frame["population"] == population) & (frame["outcome"] == outcome)
    ]
    if set(selected["arm"].astype(str)) != {"pep", "no_pep"}:
        raise ValueError(
            f"Trial rows are incomplete for population={population}, outcome={outcome}."
        )
    return {
        str(row["arm"]): row.to_dict()
        for _, row in selected.iterrows()
    }

def load_trial_effect_frame() -> pd.DataFrame:
    """Load published comparative effect estimates used for uncertainty analysis."""

    frame = _read_csv("trial_effect_estimates.csv")
    required = {
        "population",
        "outcome",
        "effect_measure",
        "estimate",
        "lower_95",
        "upper_95",
        "analysis_method",
        "source_id",
    }
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(
            f"trial_effect_estimates.csv is missing columns: {sorted(missing)}"
        )
    for column in ["estimate", "lower_95", "upper_95"]:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    keys = ["population", "outcome", "effect_measure"]
    if frame.duplicated(keys).any():
        duplicates = frame.loc[frame.duplicated(keys, keep=False), keys]
        raise ValueError(
            "Duplicate trial effect estimates: "
            + duplicates.astype(str).agg("/".join, axis=1).str.cat(sep=", ")
        )
    return frame


def trial_effect_estimate(
    population: str,
    outcome: str = "symptomatic_covid_day10",
    effect_measure: str = "risk_ratio",
    effect_frame: pd.DataFrame | None = None,
) -> dict[str, Any]:
    """Return one published effect estimate and confidence interval."""

    frame = load_trial_effect_frame() if effect_frame is None else effect_frame
    selected = frame.loc[
        (frame["population"] == population)
        & (frame["outcome"] == outcome)
        & (frame["effect_measure"] == effect_measure)
    ]
    if len(selected) != 1:
        raise ValueError(
            "Expected one trial effect estimate for "
            f"population={population}, outcome={outcome}, "
            f"effect_measure={effect_measure}; found {len(selected)}."
        )
    return selected.iloc[0].to_dict()

