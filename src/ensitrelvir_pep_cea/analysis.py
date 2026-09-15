from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd
from scipy.stats import beta as beta_distribution

from .io import (
    Scenario,
    apply_scenario_overrides,
    base_parameters,
    load_input_traceability_targets,
    load_parameter_frame,
    load_scenario,
    load_scenarios,
    trial_effect_estimate,
    trial_probabilities,
    trial_rows,
)
from .model import ModelResult, evaluate_model


@dataclass(frozen=True)
class ScenarioRun:
    scenario: Scenario
    parameters: dict[str, float]
    result: ModelResult


def run_scenario(
    scenario_id: str,
    parameter_frame: pd.DataFrame | None = None,
) -> ScenarioRun:
    frame = load_parameter_frame() if parameter_frame is None else parameter_frame
    scenario = load_scenario(scenario_id)
    params = apply_scenario_overrides(base_parameters(frame), scenario_id)
    p_sym = trial_probabilities(
        population=scenario.trial_population,
        outcome="symptomatic_covid_day10",
    )
    p_any = None
    if scenario.structural_mode == "any_infection_pcc":
        p_any = trial_probabilities(
            population="overall", outcome="any_sars_cov2_infection_day10"
        )
    result = evaluate_model(
        params=params,
        symptomatic_probabilities=p_sym,
        structural_mode=scenario.structural_mode,
        any_infection_probabilities=p_any,
        scenario_id=scenario_id,
    )
    return ScenarioRun(scenario=scenario, parameters=params, result=result)


def run_all_scenarios() -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    scenarios = load_scenarios()
    for scenario_id in scenarios["scenario_id"].astype(str):
        run = run_scenario(scenario_id)
        result = run.result.incremental_results.copy()
        result["trial_population"] = run.scenario.trial_population
        result["perspective"] = run.scenario.perspective
        result["description_ja"] = run.scenario.description_ja
        result["description_en"] = run.scenario.description_en
        rows.append(result)
    return pd.concat(rows, ignore_index=True)


def _evaluate_with_probabilities(
    run: ScenarioRun,
    params: dict[str, float],
    p_sym: dict[str, float],
) -> pd.Series:
    p_any = None
    if run.scenario.structural_mode == "any_infection_pcc":
        p_any = trial_probabilities(
            population="overall", outcome="any_sars_cov2_infection_day10"
        )
    return evaluate_model(
        params=params,
        symptomatic_probabilities=p_sym,
        structural_mode=run.scenario.structural_mode,
        any_infection_probabilities=p_any,
        scenario_id=run.scenario.scenario_id,
    ).incremental_results.iloc[0]


def _trial_effect_dsa_rows(run: ScenarioRun) -> list[dict[str, float | str]]:
    """Create coherent DSA rows for untreated risk and relative risk.

    Jeffreys intervals are used for the untreated arm risk. The randomized
    relative-risk range is taken from the published comparative 95% confidence
    interval, which is preferable to recreating an unclustered two-arm interval.
    """

    rows = trial_rows(
        population=run.scenario.trial_population,
        outcome="symptomatic_covid_day10",
    )
    control = rows["no_pep"]
    event_c = float(control["events"])
    n_c = float(control["n"])
    risk_c = float(control["reported_probability"])
    effect = trial_effect_estimate(
        population=run.scenario.trial_population,
        outcome="symptomatic_covid_day10",
        effect_measure="risk_ratio",
    )
    rr = float(effect["estimate"])
    rr_low = float(effect["lower_95"])
    rr_high = float(effect["upper_95"])

    control_low = float(
        beta_distribution.ppf(0.025, event_c + 0.5, n_c - event_c + 0.5)
    )
    control_high = float(
        beta_distribution.ppf(0.975, event_c + 0.5, n_c - event_c + 0.5)
    )

    result_rows: list[dict[str, float | str]] = []
    specifications = [
        (
            "trial_control_symptomatic_risk",
            "無治療群の症候性COVID-19リスク",
            risk_c,
            control_low,
            control_high,
            lambda value: {
                "no_pep": value,
                "pep": min(1.0, value * rr),
            },
        ),
        (
            "trial_relative_risk_symptomatic_covid",
            "エンシトレルビルの症候性COVID-19相対リスク",
            rr,
            rr_low,
            rr_high,
            lambda value: {
                "no_pep": risk_c,
                "pep": min(1.0, risk_c * value),
            },
        ),
    ]

    for parameter_id, label_ja, base, low, high, probability_builder in specifications:
        evaluated: dict[str, pd.Series] = {}
        for label, value in (("low", low), ("high", high)):
            evaluated[label] = _evaluate_with_probabilities(
                run=run,
                params=dict(run.parameters),
                p_sym=probability_builder(value),
            )
        nmb_low = float(evaluated["low"]["incremental_net_monetary_benefit_jpy"])
        nmb_high = float(evaluated["high"]["incremental_net_monetary_benefit_jpy"])
        result_rows.append(
            {
                "parameter_id": parameter_id,
                "label_ja": label_ja,
                "base_value": base,
                "low_value": low,
                "high_value": high,
                "inmb_low_jpy": nmb_low,
                "inmb_high_jpy": nmb_high,
                "inmb_min_jpy": min(nmb_low, nmb_high),
                "inmb_max_jpy": max(nmb_low, nmb_high),
                "inmb_span_jpy": abs(nmb_high - nmb_low),
                "icer_low_jpy_per_qaly": float(evaluated["low"]["icer_jpy_per_qaly"]),
                "icer_high_jpy_per_qaly": float(evaluated["high"]["icer_jpy_per_qaly"]),
                "source_type": "randomized_trial",
            }
        )
    return result_rows


def one_way_sensitivity(
    scenario_id: str = "base_high_risk",
) -> tuple[pd.DataFrame, pd.Series]:
    parameter_frame = load_parameter_frame()
    run = run_scenario(scenario_id, parameter_frame)
    base_incremental = run.result.incremental_results.iloc[0]
    rows: list[dict[str, float | str]] = []

    for _, parameter_row in parameter_frame.iterrows():
        if str(parameter_row["include_in_dsa"]).strip().lower() != "yes":
            continue
        parameter_id = str(parameter_row["parameter_id"])
        low = float(parameter_row["lower_value"])
        high = float(parameter_row["upper_value"])
        if low == high:
            continue

        values: dict[str, pd.Series] = {}
        for label, value in (("low", low), ("high", high)):
            params = dict(run.parameters)
            params[parameter_id] = value
            p_sym = trial_probabilities(
                population=run.scenario.trial_population,
                outcome="symptomatic_covid_day10",
            )
            values[label] = _evaluate_with_probabilities(
                run=run,
                params=params,
                p_sym=p_sym,
            )

        nmb_low = float(values["low"]["incremental_net_monetary_benefit_jpy"])
        nmb_high = float(values["high"]["incremental_net_monetary_benefit_jpy"])
        rows.append(
            {
                "parameter_id": parameter_id,
                "label_ja": str(parameter_row["label_ja"]),
                "base_value": float(run.parameters[parameter_id]),
                "low_value": low,
                "high_value": high,
                "inmb_low_jpy": nmb_low,
                "inmb_high_jpy": nmb_high,
                "inmb_min_jpy": min(nmb_low, nmb_high),
                "inmb_max_jpy": max(nmb_low, nmb_high),
                "inmb_span_jpy": abs(nmb_high - nmb_low),
                "icer_low_jpy_per_qaly": float(values["low"]["icer_jpy_per_qaly"]),
                "icer_high_jpy_per_qaly": float(values["high"]["icer_jpy_per_qaly"]),
                "source_type": str(parameter_row["source_type"]),
            }
        )

    rows.extend(_trial_effect_dsa_rows(run))
    result = pd.DataFrame(rows).sort_values("inmb_span_jpy", ascending=False)
    return result.reset_index(drop=True), base_incremental


def threshold_grid(
    scenario_id: str,
    parameter_id: str,
    values: Iterable[float],
) -> pd.DataFrame:
    run = run_scenario(scenario_id)
    if parameter_id not in run.parameters:
        raise KeyError(f"Unknown parameter '{parameter_id}'.")
    p_sym = trial_probabilities(
        population=run.scenario.trial_population,
        outcome="symptomatic_covid_day10",
    )
    p_any = None
    if run.scenario.structural_mode == "any_infection_pcc":
        p_any = trial_probabilities(
            population="overall", outcome="any_sars_cov2_infection_day10"
        )

    records: list[dict[str, float | bool | str]] = []
    for value in values:
        params = dict(run.parameters)
        params[parameter_id] = float(value)
        if run.scenario.structural_mode == "symptomatic_mediation_profile":
            from .sampling import _evaluate_profile_incremental_fast

            result = _evaluate_profile_incremental_fast(params, p_sym)
        else:
            result = evaluate_model(
                params=params,
                symptomatic_probabilities=p_sym,
                structural_mode=run.scenario.structural_mode,
                any_infection_probabilities=p_any,
                scenario_id=scenario_id,
            ).incremental_results.iloc[0]
        records.append(
            {
                "parameter_id": parameter_id,
                "parameter_value": float(value),
                "incremental_cost_jpy": float(result["incremental_cost_jpy"]),
                "incremental_qaly": float(result["incremental_qaly"]),
                "icer_jpy_per_qaly": float(result["icer_jpy_per_qaly"]),
                "incremental_net_monetary_benefit_jpy": float(
                    result["incremental_net_monetary_benefit_jpy"]
                ),
                "cost_effective_at_wtp": bool(result["cost_effective_at_wtp"]),
            }
        )
    return pd.DataFrame(records)


def estimate_zero_nmb_crossing(grid: pd.DataFrame) -> float | None:
    """Linearly interpolate the first parameter value at which INMB crosses zero."""

    ordered = grid.sort_values("parameter_value").reset_index(drop=True)
    x = ordered["parameter_value"].to_numpy(dtype=float)
    y = ordered["incremental_net_monetary_benefit_jpy"].to_numpy(dtype=float)
    exact = np.where(np.isclose(y, 0.0))[0]
    if len(exact):
        return float(x[exact[0]])
    signs = np.sign(y)
    for index in range(len(x) - 1):
        if signs[index] == signs[index + 1]:
            continue
        if y[index + 1] == y[index]:
            return float(x[index])
        fraction = -y[index] / (y[index + 1] - y[index])
        return float(x[index] + fraction * (x[index + 1] - x[index]))
    return None


def input_traceability_table(scenario_id: str = "base_high_risk") -> pd.DataFrame:
    """Run verification, input traceability, and limited external face-validity checks.

    This table must not be interpreted as predictive external validation.
    """

    run = run_scenario(scenario_id)
    arm = run.result.arm_results.loc["no_pep"]
    targets = load_input_traceability_targets().set_index("check_id")

    modeled_values = {
        "V01": float(arm["weighted_inpatient_cost_jpy"]),
        "V02": float(run.parameters["cost_icu_mv_per_day"])
        * float(run.parameters["los_icu_mv_days"]),
        "V03": float(arm["weighted_inpatient_los_days"]),
        "V04": float(arm["weighted_inpatient_los_days"]),
        "V05": float(run.parameters["p_death_given_hospital"]),
    }
    comparison_notes = {
        "V01": (
            "Model expectation is a mean-like pathway-weighted value; the external "
            "target is a median."
        ),
        "V02": (
            "The external target is a median for severe 2021 cases and may include "
            "a longer or more resource-intensive pathway."
        ),
        "V03": (
            "Historical single-center LOS comparator; the publication base uses the "
            "contemporary Japanese cohort instead."
        ),
        "V04": "Direct check against the contemporary Japanese cohort median LOS.",
        "V05": "Direct check against contemporary Japanese in-hospital mortality.",
    }

    records: list[dict[str, float | str]] = []
    for check_id, modeled_value in modeled_values.items():
        if check_id not in targets.index:
            raise KeyError(
                f"Missing input traceability target '{check_id}' in "
                "data/input_traceability_targets.csv."
            )
        target = targets.loc[check_id]
        records.append(
            {
                "check_id": check_id,
                "metric": str(target["metric"]),
                "modeled_value": modeled_value,
                "unit": str(target["unit"]),
                "external_target": float(target["observed_value"]),
                "check_type": str(target["check_type"]),
                "source_id": str(target["source_id"]),
                "comparison_note": comparison_notes[check_id],
                "source_notes": str(target["notes"]),
            }
        )
    return pd.DataFrame(records)



def external_validation_table(scenario_id: str = "base_high_risk") -> pd.DataFrame:
    """Backward-compatible alias; use input_traceability_table in new code."""

    return input_traceability_table(scenario_id)
