from __future__ import annotations

from math import log, sqrt
from typing import Mapping

import numpy as np
import pandas as pd

from .io import Scenario, trial_effect_estimate, trial_rows
from .model import evaluate_model


NORMAL_975 = 1.959963984540054
EFFICACY_SAMPLING_METHOD = (
    "control_risk_jeffreys_plus_reported_rr_lognormal"
)
EFFICACY_SAMPLING_DESCRIPTION = (
    "Jeffreys posterior for no-PEP risk plus log-normal reported risk ratio "
    "from published 95% CI"
)


def _sample_pert(
    rng: np.random.Generator, lower: float, mode: float, upper: float, lam: float = 4.0
) -> float:
    if upper <= lower:
        return float(mode)
    mode = min(max(mode, lower), upper)
    alpha = 1.0 + lam * (mode - lower) / (upper - lower)
    beta = 1.0 + lam * (upper - mode) / (upper - lower)
    return float(lower + (upper - lower) * rng.beta(alpha, beta))


def sample_parameter_row(row: pd.Series, rng: np.random.Generator) -> float:
    base = float(row["base_value"])
    lower = float(row["lower_value"])
    upper = float(row["upper_value"])
    distribution = str(row["distribution"]).strip().lower()
    raw_parameter = row.get("distribution_parameter", "")
    parameter = float(raw_parameter) if pd.notna(raw_parameter) and str(raw_parameter) else 0.0

    if distribution == "fixed":
        return base
    if distribution == "pert":
        return _sample_pert(rng, lower, base, upper)
    if distribution == "gamma_cv":
        cv = parameter if parameter > 0 else 0.20
        if base <= 0:
            return 0.0
        shape = 1.0 / (cv * cv)
        scale = base * cv * cv
        return float(rng.gamma(shape, scale))
    if distribution == "lognormal_cv":
        cv = parameter if parameter > 0 else 0.20
        if base <= 0:
            return 0.0
        sigma = sqrt(log(1.0 + cv * cv))
        mu = log(base) - 0.5 * sigma * sigma
        return float(rng.lognormal(mu, sigma))
    if distribution == "uniform":
        return float(rng.uniform(lower, upper))
    raise ValueError(f"Unsupported distribution '{distribution}' for {row['parameter_id']}.")


def sample_parameter_set(
    parameter_frame: pd.DataFrame,
    scenario_params: Mapping[str, float],
    rng: np.random.Generator,
) -> dict[str, float]:
    sampled = dict(scenario_params)
    for _, row in parameter_frame.iterrows():
        parameter_id = str(row["parameter_id"])
        if str(row["include_in_psa"]).strip().lower() != "yes":
            continue
        mutable_row = row.copy()
        # Preserve scenario-specific modes while retaining source uncertainty bounds.
        mutable_row["base_value"] = float(scenario_params[parameter_id])
        sampled[parameter_id] = sample_parameter_row(mutable_row, rng)
    return sampled


def sample_trial_probability(row: Mapping[str, object], rng: np.random.Generator) -> float:
    """Sample one arm risk using a Jeffreys beta posterior."""

    n = float(row["n"])
    events_raw = row.get("events")
    probability = float(row["reported_probability"])
    if events_raw is None or pd.isna(events_raw):
        events = probability * n
    else:
        events = float(events_raw)
    alpha = events + 0.5
    beta = n - events + 0.5
    return float(rng.beta(alpha, beta))


def _risk_ratio_lognormal_parameters(
    effect: Mapping[str, object],
) -> tuple[float, float]:
    estimate = float(effect["estimate"])
    lower = float(effect["lower_95"])
    upper = float(effect["upper_95"])
    if not (0.0 < lower <= estimate <= upper):
        raise ValueError(
            "Risk-ratio estimate and confidence limits must be positive and ordered."
        )
    log_se = (log(upper) - log(lower)) / (2.0 * NORMAL_975)
    return log(estimate), log_se


def sample_reported_risk_ratio(
    population: str,
    outcome: str,
    rng: np.random.Generator,
    effect: Mapping[str, object] | None = None,
) -> float:
    """Sample a risk ratio from the published estimate and 95% confidence interval.

    A log-normal distribution is parameterized from the reported confidence interval.
    For the primary trial endpoint, this retains the uncertainty from the published
    cluster-aware analysis instead of rebuilding an unclustered two-arm likelihood.
    """

    selected_effect = (
        trial_effect_estimate(
            population=population,
            outcome=outcome,
            effect_measure="risk_ratio",
        )
        if effect is None
        else effect
    )
    log_mean, log_se = _risk_ratio_lognormal_parameters(selected_effect)
    return float(rng.lognormal(mean=log_mean, sigma=log_se))


def sample_symptomatic_probabilities(
    population: str,
    rng: np.random.Generator,
    outcome: str = "symptomatic_covid_day10",
    rows: Mapping[str, Mapping[str, object]] | None = None,
    effect: Mapping[str, object] | None = None,
) -> tuple[dict[str, float], float]:
    """Jointly sample untreated symptomatic risk and the published relative effect.

    The untreated risk is sampled from its arm-level Jeffreys posterior. The relative
    risk is sampled from the reported comparative confidence interval. Their statistical
    dependence is not publicly available and is therefore approximated as independent.
    """

    selected_rows = (
        trial_rows(population=population, outcome=outcome) if rows is None else rows
    )
    no_pep_risk = sample_trial_probability(selected_rows["no_pep"], rng)
    risk_ratio = sample_reported_risk_ratio(
        population,
        outcome,
        rng,
        effect=effect,
    )
    pep_risk = float(np.clip(no_pep_risk * risk_ratio, 0.0, 1.0))
    return {"pep": pep_risk, "no_pep": no_pep_risk}, risk_ratio



def _evaluate_profile_incremental_fast(
    params: Mapping[str, float],
    symptomatic_probabilities: Mapping[str, float],
) -> dict[str, float | bool]:
    """Fast scalar equivalent of the publication profile model for PSA.

    This avoids constructing pandas DataFrames for every simulation while preserving
    the equations used by ``evaluate_model``. It is used only for the
    ``symptomatic_mediation_profile`` structural mode.
    """

    multiplier = float(params["secondary_symptomatic_case_multiplier"])
    p_hosp = float(params["p_hospital_given_symptomatic"])
    attribution = float(params["hospitalization_attribution_fraction"])
    p_death = float(params["p_death_given_hospital"])
    cost_factor = float(params["acute_cost_price_adjustment_factor"])
    outpatient_cost_unit = float(params["cost_outpatient"])
    hospital_cost_unit = float(params["cost_hospitalization"])
    outpatient_qaly_unit = (
        float(params["disutility_outpatient"])
        * float(params["symptom_duration_outpatient_days"])
        / 365.25
    )
    hospital_qaly_unit = (
        float(params["disutility_hospital"])
        * float(params["los_hospital_days"])
        / 365.25
    )
    remaining_qaly = float(params["remaining_qaly_if_acute_death"])
    post_cost_unit = float(params["postacute_cost_per_surviving_symptomatic_case"])
    post_qaly_unit = float(params["postacute_qaly_loss_per_surviving_symptomatic_case"])

    arm_values: dict[str, dict[str, float]] = {}
    for arm in ("pep", "no_pep"):
        direct = float(symptomatic_probabilities[arm])
        secondary = direct * multiplier
        total = direct + secondary
        observed_hosp = total * p_hosp
        hosp = observed_hosp * attribution
        outpatient = total - hosp
        deaths = hosp * p_death
        survivors = max(0.0, total - deaths)
        intervention = 0.0
        ae_qaly = 0.0
        if arm == "pep":
            intervention = (
                float(params["drug_cost_pep"])
                + float(params["administration_cost_pep"])
                + float(params["additional_pep_access_cost"])
                + float(params["incremental_ae_cost_pep"])
            )
            ae_qaly = float(params["incremental_ae_qaly_loss_pep"])
        total_cost = (
            intervention
            + cost_factor
            * (outpatient * outpatient_cost_unit + hosp * hospital_cost_unit)
            + survivors * post_cost_unit
        )
        total_qaly_loss = (
            outpatient * outpatient_qaly_unit
            + hosp * hospital_qaly_unit
            + deaths * remaining_qaly
            + survivors * post_qaly_unit
            + ae_qaly
        )
        arm_values[arm] = {
            "direct": direct,
            "secondary": secondary,
            "total": total,
            "observed_hosp": observed_hosp,
            "hosp": hosp,
            "deaths": deaths,
            "cost": total_cost,
            "qaly_loss": total_qaly_loss,
        }

    pep = arm_values["pep"]
    no_pep = arm_values["no_pep"]
    incremental_cost = pep["cost"] - no_pep["cost"]
    incremental_qaly = no_pep["qaly_loss"] - pep["qaly_loss"]
    inmb = float(params["wtp_per_qaly"]) * incremental_qaly - incremental_cost
    icer = (
        incremental_cost / incremental_qaly
        if incremental_qaly != 0.0
        else float("nan")
    )
    return {
        "incremental_cost_jpy": incremental_cost,
        "incremental_qaly": incremental_qaly,
        "icer_jpy_per_qaly": icer,
        "incremental_net_monetary_benefit_jpy": inmb,
        "cost_effective_at_wtp": bool(inmb >= 0.0),
        "symptomatic_cases_prevented": no_pep["direct"] - pep["direct"],
        "secondary_symptomatic_cases_prevented": no_pep["secondary"] - pep["secondary"],
        "total_symptomatic_cases_prevented": no_pep["total"] - pep["total"],
        "hospitalizations_prevented": no_pep["hosp"] - pep["hosp"],
        "deaths_prevented": no_pep["deaths"] - pep["deaths"],
        "pcc_cases_prevented": 0.0,
    }

def run_psa(
    parameter_frame: pd.DataFrame,
    scenario_params: Mapping[str, float],
    scenario: Scenario,
    n_simulations: int = 10_000,
    seed: int = 20_260_825,
) -> pd.DataFrame:
    """Run probabilistic sensitivity analysis with a reproducible random seed."""

    if n_simulations <= 0:
        raise ValueError("n_simulations must be positive.")
    rng = np.random.default_rng(seed)

    symptom_rows = trial_rows(
        population=scenario.trial_population,
        outcome="symptomatic_covid_day10",
    )
    symptom_effect = trial_effect_estimate(
        population=scenario.trial_population,
        outcome="symptomatic_covid_day10",
        effect_measure="risk_ratio",
    )

    any_rows = None
    if scenario.structural_mode == "any_infection_pcc":
        # High-risk subgroup all-infection counts were not reported in the public source.
        # The exploratory structural scenario therefore uses overall trial probabilities.
        any_rows = trial_rows(
            population="overall", outcome="any_sars_cov2_infection_day10"
        )

    output: list[dict[str, float | int | bool]] = []
    for iteration in range(n_simulations):
        params = sample_parameter_set(parameter_frame, scenario_params, rng)
        p_sym, sampled_rr = sample_symptomatic_probabilities(
            population=scenario.trial_population,
            rng=rng,
            rows=symptom_rows,
            effect=symptom_effect,
        )
        p_any = None
        if any_rows is not None:
            p_any = {
                arm: sample_trial_probability(row, rng)
                for arm, row in any_rows.items()
            }
            for arm in ("pep", "no_pep"):
                p_any[arm] = max(p_any[arm], p_sym[arm])

        if scenario.structural_mode == "symptomatic_mediation_profile":
            result = _evaluate_profile_incremental_fast(params, p_sym)
        else:
            result = evaluate_model(
                params=params,
                symptomatic_probabilities=p_sym,
                structural_mode=scenario.structural_mode,
                any_infection_probabilities=p_any,
                scenario_id=scenario.scenario_id,
            ).incremental_results.iloc[0]
        output.append(
            {
                "iteration": iteration + 1,
                "sampled_symptomatic_risk_pep": p_sym["pep"],
                "sampled_symptomatic_risk_no_pep": p_sym["no_pep"],
                "sampled_relative_risk_symptomatic_covid": sampled_rr,
                "incremental_cost_jpy": float(result["incremental_cost_jpy"]),
                "incremental_qaly": float(result["incremental_qaly"]),
                "icer_jpy_per_qaly": float(result["icer_jpy_per_qaly"]),
                "incremental_net_monetary_benefit_jpy": float(
                    result["incremental_net_monetary_benefit_jpy"]
                ),
                "cost_effective_at_wtp": bool(result["cost_effective_at_wtp"]),
                "symptomatic_cases_prevented": float(
                    result["symptomatic_cases_prevented"]
                ),
                "secondary_symptomatic_cases_prevented": float(
                    result["secondary_symptomatic_cases_prevented"]
                ),
                "total_symptomatic_cases_prevented": float(
                    result["total_symptomatic_cases_prevented"]
                ),
                "hospitalizations_prevented": float(
                    result["hospitalizations_prevented"]
                ),
                "deaths_prevented": float(result["deaths_prevented"]),
                "pcc_cases_prevented": float(result["pcc_cases_prevented"]),
            }
        )
    return pd.DataFrame(output)


def cost_effectiveness_acceptability_curve(
    psa_results: pd.DataFrame,
    wtp_grid: np.ndarray | list[float],
) -> pd.DataFrame:
    records: list[dict[str, float]] = []
    incremental_cost = psa_results["incremental_cost_jpy"].to_numpy(dtype=float)
    incremental_qaly = psa_results["incremental_qaly"].to_numpy(dtype=float)
    for wtp in np.asarray(wtp_grid, dtype=float):
        nmb = wtp * incremental_qaly - incremental_cost
        records.append(
            {
                "wtp_jpy_per_qaly": float(wtp),
                "probability_cost_effective": float(np.mean(nmb >= 0.0)),
                "mean_incremental_nmb_jpy": float(np.mean(nmb)),
            }
        )
    return pd.DataFrame(records)
