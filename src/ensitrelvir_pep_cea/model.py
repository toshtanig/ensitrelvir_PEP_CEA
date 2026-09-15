from __future__ import annotations

from dataclasses import dataclass
from math import exp, isfinite
from typing import Mapping

import pandas as pd


VALID_STRUCTURAL_MODES = {
    "symptomatic_mediation_profile",
    "symptomatic_mediation",
    "acute_no_pcc",
    "symptom_only",
    "any_infection_pcc",
}


@dataclass(frozen=True)
class ModelResult:
    """Deterministic expected-value results per exposed household contact."""

    arm_results: pd.DataFrame
    incremental_results: pd.DataFrame


def _require_probability(name: str, value: float) -> None:
    if not isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1; received {value}.")


def _require_nonnegative(name: str, value: float) -> None:
    if not isfinite(value) or value < 0.0:
        raise ValueError(f"{name} must be nonnegative; received {value}.")


def validate_inputs(
    params: Mapping[str, float],
    symptomatic_probabilities: Mapping[str, float],
    any_infection_probabilities: Mapping[str, float] | None,
    structural_mode: str,
) -> None:
    if structural_mode not in VALID_STRUCTURAL_MODES:
        raise ValueError(
            f"Unknown structural mode '{structural_mode}'. "
            f"Expected one of {sorted(VALID_STRUCTURAL_MODES)}."
        )

    for arm in ("pep", "no_pep"):
        if arm not in symptomatic_probabilities:
            raise KeyError(f"Missing symptomatic probability for arm '{arm}'.")
        _require_probability(
            f"symptomatic_probabilities[{arm}]", symptomatic_probabilities[arm]
        )

    if structural_mode == "any_infection_pcc":
        if any_infection_probabilities is None:
            raise ValueError("any_infection_probabilities are required for any_infection_pcc.")
        for arm in ("pep", "no_pep"):
            if arm not in any_infection_probabilities:
                raise KeyError(f"Missing any-infection probability for arm '{arm}'.")
            _require_probability(
                f"any_infection_probabilities[{arm}]",
                any_infection_probabilities[arm],
            )
            if any_infection_probabilities[arm] < symptomatic_probabilities[arm]:
                raise ValueError(
                    f"Any-infection probability must be at least the symptomatic "
                    f"probability in arm '{arm}'."
                )

    probability_parameters = [
        "p_hospital_given_symptomatic",
        "hospitalization_attribution_fraction",
        "p_death_given_hospital",
        "p_death_outpatient",
        "p_icu_given_hospital",
        "p_mv_given_icu",
        "p_death_ward",
        "p_death_icu_no_mv",
        "p_death_icu_mv",
        "p_pcc_outpatient",
        "p_pcc_asymptomatic",
        "discount_rate_cost",
        "discount_rate_qaly",
    ]
    for name in probability_parameters:
        _require_probability(name, float(params[name]))

    nonnegative_parameters = [
        "drug_cost_pep",
        "administration_cost_pep",
        "additional_pep_access_cost",
        "incremental_ae_cost_pep",
        "incremental_ae_qaly_loss_pep",
        "symptom_duration_outpatient_days",
        "disutility_outpatient",
        "disutility_hospital",
        "disutility_ward",
        "disutility_icu",
        "remaining_qaly_if_acute_death",
        "cost_outpatient",
        "cost_hospitalization",
        "cost_ward_per_day",
        "cost_icu_no_mv_per_day",
        "cost_icu_mv_per_day",
        "los_hospital_days",
        "los_ward_days",
        "los_icu_no_mv_days",
        "los_icu_mv_days",
        "postacute_qaly_loss_per_surviving_symptomatic_case",
        "postacute_cost_per_surviving_symptomatic_case",
        "acute_cost_price_adjustment_factor",
        "pcc_hospital_multiplier",
        "pcc_mean_duration_months",
        "disutility_pcc",
        "cost_pcc_annual",
        "pcc_horizon_months",
        "wtp_per_qaly",
        "secondary_symptomatic_case_multiplier",
    ]
    for name in nonnegative_parameters:
        _require_nonnegative(name, float(params[name]))


def expected_pcc_burden_per_incident_case(
    params: Mapping[str, float]
) -> tuple[float, float, float]:
    """Return discounted legacy PCC cost, QALY loss, and occupied years per case.

    This incidence-duration module is retained for structural sensitivity analysis.
    The publication base case instead uses a directly integrated one-year utility
    profile from a Japanese Omicron-period controlled cohort.
    """

    mean_months = float(params["pcc_mean_duration_months"])
    horizon = int(round(float(params["pcc_horizon_months"])))
    if mean_months <= 0.0 or horizon <= 0:
        return 0.0, 0.0, 0.0

    monthly_stay = exp(-1.0 / mean_months)
    annual_cost = float(params["cost_pcc_annual"])
    disutility = float(params["disutility_pcc"])
    discount_cost = float(params["discount_rate_cost"])
    discount_qaly = float(params["discount_rate_qaly"])
    mid_cycle_multiplier = 0.5 * (1.0 + monthly_stay)

    def geometric_sum(ratio: float, cycles: int) -> float:
        if abs(1.0 - ratio) < 1e-14:
            return float(cycles)
        return (1.0 - ratio**cycles) / (1.0 - ratio)

    cost_discount_half_cycle = (1.0 + discount_cost) ** (-0.5 / 12.0)
    qaly_discount_half_cycle = (1.0 + discount_qaly) ** (-0.5 / 12.0)
    cost_ratio = monthly_stay * (1.0 + discount_cost) ** (-1.0 / 12.0)
    qaly_ratio = monthly_stay * (1.0 + discount_qaly) ** (-1.0 / 12.0)

    discounted_cost = (
        mid_cycle_multiplier
        * cost_discount_half_cycle
        * geometric_sum(cost_ratio, horizon)
        * annual_cost
        / 12.0
    )
    discounted_qaly_loss = (
        mid_cycle_multiplier
        * qaly_discount_half_cycle
        * geometric_sum(qaly_ratio, horizon)
        * disutility
        / 12.0
    )
    occupied_years = (
        mid_cycle_multiplier * geometric_sum(monthly_stay, horizon) / 12.0
    )
    return discounted_cost, discounted_qaly_loss, occupied_years


def _weighted_inpatient_cost(params: Mapping[str, float]) -> float:
    p_icu = float(params["p_icu_given_hospital"])
    p_mv = float(params["p_mv_given_icu"])
    ward = float(params["cost_ward_per_day"]) * float(params["los_ward_days"])
    icu_no_mv = float(params["cost_icu_no_mv_per_day"]) * float(
        params["los_icu_no_mv_days"]
    )
    icu_mv = float(params["cost_icu_mv_per_day"]) * float(
        params["los_icu_mv_days"]
    )
    return (1.0 - p_icu) * ward + p_icu * (
        (1.0 - p_mv) * icu_no_mv + p_mv * icu_mv
    )


def _weighted_inpatient_los(params: Mapping[str, float]) -> float:
    p_icu = float(params["p_icu_given_hospital"])
    p_mv = float(params["p_mv_given_icu"])
    return (1.0 - p_icu) * float(params["los_ward_days"]) + p_icu * (
        (1.0 - p_mv) * float(params["los_icu_no_mv_days"])
        + p_mv * float(params["los_icu_mv_days"])
    )


def _intervention_burden(
    arm: str, params: Mapping[str, float]
) -> tuple[float, float]:
    if arm == "no_pep":
        return 0.0, 0.0
    intervention_cost = (
        float(params["drug_cost_pep"])
        + float(params["administration_cost_pep"])
        + float(params["additional_pep_access_cost"])
        + float(params["incremental_ae_cost_pep"])
    )
    return intervention_cost, float(params["incremental_ae_qaly_loss_pep"])


def _evaluate_profile_arm(
    arm: str,
    params: Mapping[str, float],
    symptomatic_probability: float,
) -> dict[str, float | str]:
    """Publication base-case arm using direct Japanese post-acute utility profiles.

    Ensitrelvir affects only the probability of symptomatic COVID-19. Conditional
    risks and burdens after a breakthrough symptomatic case are assumed equal in
    both arms. Death is restricted to the hospitalized pathway.
    """

    p_sym = float(symptomatic_probability)
    secondary_multiplier = float(params["secondary_symptomatic_case_multiplier"])
    secondary_symptomatic = p_sym * secondary_multiplier
    total_symptomatic_burden = p_sym + secondary_symptomatic
    observed_all_cause_hospitalizations = (
        total_symptomatic_burden * float(params["p_hospital_given_symptomatic"])
    )
    p_hospital = (
        observed_all_cause_hospitalizations
        * float(params["hospitalization_attribution_fraction"])
    )
    p_outpatient = total_symptomatic_burden - p_hospital
    deaths_total = p_hospital * float(params["p_death_given_hospital"])
    surviving_symptomatic = max(0.0, total_symptomatic_burden - deaths_total)

    intervention_cost, ae_qaly_loss = _intervention_burden(arm, params)
    cost_factor = float(params["acute_cost_price_adjustment_factor"])
    outpatient_cost = p_outpatient * float(params["cost_outpatient"]) * cost_factor
    hospital_cost = p_hospital * float(params["cost_hospitalization"]) * cost_factor
    acute_healthcare_cost = outpatient_cost + hospital_cost

    outpatient_qaly_loss = (
        p_outpatient
        * float(params["disutility_outpatient"])
        * float(params["symptom_duration_outpatient_days"])
        / 365.25
    )
    hospital_qaly_loss = (
        p_hospital
        * float(params["disutility_hospital"])
        * float(params["los_hospital_days"])
        / 365.25
    )
    acute_morbidity_qaly_loss = outpatient_qaly_loss + hospital_qaly_loss
    mortality_qaly_loss = deaths_total * float(params["remaining_qaly_if_acute_death"])

    postacute_profile_cases = surviving_symptomatic
    postacute_cost = postacute_profile_cases * float(
        params["postacute_cost_per_surviving_symptomatic_case"]
    )
    postacute_qaly_loss = postacute_profile_cases * float(
        params["postacute_qaly_loss_per_surviving_symptomatic_case"]
    )

    total_cost = intervention_cost + acute_healthcare_cost + postacute_cost
    total_qaly_loss = (
        acute_morbidity_qaly_loss
        + mortality_qaly_loss
        + postacute_qaly_loss
        + ae_qaly_loss
    )

    return {
        "arm": arm,
        "symptomatic_covid": p_sym,
        "secondary_symptomatic_covid": secondary_symptomatic,
        "total_symptomatic_covid": total_symptomatic_burden,
        "observed_all_cause_hospitalizations": observed_all_cause_hospitalizations,
        "hospitalizations": p_hospital,
        "outpatient_cases": p_outpatient,
        "icu_admissions": 0.0,
        "mechanical_ventilation": 0.0,
        "deaths": deaths_total,
        "pcc_cases": 0.0,
        "pcc_person_years": 0.0,
        "postacute_profile_cases": postacute_profile_cases,
        "intervention_cost_jpy": intervention_cost,
        "acute_healthcare_cost_jpy": acute_healthcare_cost,
        "pcc_cost_jpy": postacute_cost,
        "postacute_cost_jpy": postacute_cost,
        "total_cost_jpy": total_cost,
        "acute_morbidity_qaly_loss": acute_morbidity_qaly_loss,
        "mortality_qaly_loss": mortality_qaly_loss,
        "pcc_qaly_loss": postacute_qaly_loss,
        "postacute_qaly_loss": postacute_qaly_loss,
        "adverse_event_qaly_loss": ae_qaly_loss,
        "total_qaly_loss": total_qaly_loss,
        "weighted_inpatient_cost_jpy": float(params["cost_hospitalization"])
        * cost_factor,
        "weighted_inpatient_los_days": float(params["los_hospital_days"]),
    }


def _evaluate_legacy_arm(
    arm: str,
    params: Mapping[str, float],
    symptomatic_probability: float,
    structural_mode: str,
    any_infection_probability: float | None = None,
) -> dict[str, float | str]:
    """Evaluate one arm using the v0.1 acute tree plus incidence-duration PCC model."""

    p_sym = float(symptomatic_probability)
    p_hospital_conditional = float(params["p_hospital_given_symptomatic"])
    p_death_outpatient = float(params["p_death_outpatient"])

    if structural_mode == "symptom_only":
        p_hospital_conditional = 0.0
        p_death_outpatient = 0.0

    p_hospital = p_sym * p_hospital_conditional
    p_outpatient = p_sym - p_hospital
    p_icu = float(params["p_icu_given_hospital"])
    p_mv = float(params["p_mv_given_icu"])
    p_ward = p_hospital * (1.0 - p_icu)
    p_icu_no_mv = p_hospital * p_icu * (1.0 - p_mv)
    p_icu_mv = p_hospital * p_icu * p_mv

    deaths_outpatient = p_outpatient * p_death_outpatient
    deaths_ward = p_ward * float(params["p_death_ward"])
    deaths_icu_no_mv = p_icu_no_mv * float(params["p_death_icu_no_mv"])
    deaths_icu_mv = p_icu_mv * float(params["p_death_icu_mv"])
    deaths_total = deaths_outpatient + deaths_ward + deaths_icu_no_mv + deaths_icu_mv

    survivors_outpatient = p_outpatient - deaths_outpatient
    survivors_ward = p_ward - deaths_ward
    survivors_icu_no_mv = p_icu_no_mv - deaths_icu_no_mv
    survivors_icu_mv = p_icu_mv - deaths_icu_mv
    survivors_hospital = survivors_ward + survivors_icu_no_mv + survivors_icu_mv
    intervention_cost, ae_qaly_loss = _intervention_burden(arm, params)

    outpatient_cost = p_outpatient * float(params["cost_outpatient"])
    ward_cost = p_ward * float(params["cost_ward_per_day"]) * float(
        params["los_ward_days"]
    )
    icu_no_mv_cost = p_icu_no_mv * float(params["cost_icu_no_mv_per_day"]) * float(
        params["los_icu_no_mv_days"]
    )
    icu_mv_cost = p_icu_mv * float(params["cost_icu_mv_per_day"]) * float(
        params["los_icu_mv_days"]
    )
    acute_healthcare_cost = outpatient_cost + ward_cost + icu_no_mv_cost + icu_mv_cost

    outpatient_qaly_loss = (
        p_outpatient
        * float(params["disutility_outpatient"])
        * float(params["symptom_duration_outpatient_days"])
        / 365.25
    )
    ward_qaly_loss = (
        p_ward
        * float(params["disutility_ward"])
        * float(params["los_ward_days"])
        / 365.25
    )
    icu_no_mv_qaly_loss = (
        p_icu_no_mv
        * float(params["disutility_icu"])
        * float(params["los_icu_no_mv_days"])
        / 365.25
    )
    icu_mv_qaly_loss = (
        p_icu_mv
        * float(params["disutility_icu"])
        * float(params["los_icu_mv_days"])
        / 365.25
    )
    acute_morbidity_qaly_loss = (
        outpatient_qaly_loss + ward_qaly_loss + icu_no_mv_qaly_loss + icu_mv_qaly_loss
    )
    mortality_qaly_loss = deaths_total * float(params["remaining_qaly_if_acute_death"])

    pcc_cases_outpatient = 0.0
    pcc_cases_hospital = 0.0
    pcc_cases_asymptomatic = 0.0
    if structural_mode in {"symptomatic_mediation", "any_infection_pcc"}:
        pcc_probability_outpatient = float(params["p_pcc_outpatient"])
        pcc_probability_hospital = min(
            1.0,
            pcc_probability_outpatient * float(params["pcc_hospital_multiplier"]),
        )
        pcc_cases_outpatient = survivors_outpatient * pcc_probability_outpatient
        pcc_cases_hospital = survivors_hospital * pcc_probability_hospital

        if structural_mode == "any_infection_pcc":
            if any_infection_probability is None:
                raise ValueError(
                    "any_infection_probability is required for any_infection_pcc."
                )
            asymptomatic_infections = max(0.0, any_infection_probability - p_sym)
            pcc_cases_asymptomatic = asymptomatic_infections * float(
                params["p_pcc_asymptomatic"]
            )

    pcc_cases_total = pcc_cases_outpatient + pcc_cases_hospital + pcc_cases_asymptomatic
    pcc_cost_per_case, pcc_qaly_loss_per_case, pcc_years_per_case = (
        expected_pcc_burden_per_incident_case(params)
    )
    pcc_cost = pcc_cases_total * pcc_cost_per_case
    pcc_qaly_loss = pcc_cases_total * pcc_qaly_loss_per_case
    total_cost = intervention_cost + acute_healthcare_cost + pcc_cost
    total_qaly_loss = (
        acute_morbidity_qaly_loss + mortality_qaly_loss + pcc_qaly_loss + ae_qaly_loss
    )

    return {
        "arm": arm,
        "symptomatic_covid": p_sym,
        "secondary_symptomatic_covid": 0.0,
        "total_symptomatic_covid": p_sym,
        "observed_all_cause_hospitalizations": p_hospital,
        "hospitalizations": p_hospital,
        "outpatient_cases": p_outpatient,
        "icu_admissions": p_icu_no_mv + p_icu_mv,
        "mechanical_ventilation": p_icu_mv,
        "deaths": deaths_total,
        "pcc_cases": pcc_cases_total,
        "pcc_person_years": pcc_cases_total * pcc_years_per_case,
        "postacute_profile_cases": 0.0,
        "intervention_cost_jpy": intervention_cost,
        "acute_healthcare_cost_jpy": acute_healthcare_cost,
        "pcc_cost_jpy": pcc_cost,
        "postacute_cost_jpy": pcc_cost,
        "total_cost_jpy": total_cost,
        "acute_morbidity_qaly_loss": acute_morbidity_qaly_loss,
        "mortality_qaly_loss": mortality_qaly_loss,
        "pcc_qaly_loss": pcc_qaly_loss,
        "postacute_qaly_loss": pcc_qaly_loss,
        "adverse_event_qaly_loss": ae_qaly_loss,
        "total_qaly_loss": total_qaly_loss,
        "weighted_inpatient_cost_jpy": _weighted_inpatient_cost(params),
        "weighted_inpatient_los_days": _weighted_inpatient_los(params),
    }


def evaluate_arm(
    arm: str,
    params: Mapping[str, float],
    symptomatic_probability: float,
    structural_mode: str,
    any_infection_probability: float | None = None,
) -> dict[str, float | str]:
    """Evaluate one arm under the requested structural model."""

    if arm not in {"pep", "no_pep"}:
        raise ValueError("arm must be 'pep' or 'no_pep'.")
    if structural_mode == "symptomatic_mediation_profile":
        return _evaluate_profile_arm(arm, params, symptomatic_probability)
    return _evaluate_legacy_arm(
        arm=arm,
        params=params,
        symptomatic_probability=symptomatic_probability,
        structural_mode=structural_mode,
        any_infection_probability=any_infection_probability,
    )


def _icer_label(incremental_cost: float, incremental_qaly: float) -> tuple[float, str]:
    tolerance = 1e-15
    if incremental_qaly > tolerance and incremental_cost < -tolerance:
        return float("nan"), "dominant"
    if incremental_qaly < -tolerance and incremental_cost > tolerance:
        return float("nan"), "dominated"
    if abs(incremental_qaly) <= tolerance:
        return float("nan"), "no_incremental_qaly"
    return incremental_cost / incremental_qaly, "icer"


def evaluate_model(
    params: Mapping[str, float],
    symptomatic_probabilities: Mapping[str, float],
    structural_mode: str = "symptomatic_mediation_profile",
    any_infection_probabilities: Mapping[str, float] | None = None,
    scenario_id: str = "unspecified",
) -> ModelResult:
    """Run the model and return arm-specific and incremental results."""

    validate_inputs(
        params,
        symptomatic_probabilities,
        any_infection_probabilities,
        structural_mode,
    )
    rows: list[dict[str, float | str]] = []
    for arm in ("pep", "no_pep"):
        p_any = None
        if any_infection_probabilities is not None:
            p_any = float(any_infection_probabilities[arm])
        rows.append(
            evaluate_arm(
                arm=arm,
                params=params,
                symptomatic_probability=float(symptomatic_probabilities[arm]),
                structural_mode=structural_mode,
                any_infection_probability=p_any,
            )
        )

    arm_results = pd.DataFrame(rows).set_index("arm")
    pep = arm_results.loc["pep"]
    no_pep = arm_results.loc["no_pep"]
    incremental_cost = float(pep["total_cost_jpy"] - no_pep["total_cost_jpy"])
    incremental_qaly = float(no_pep["total_qaly_loss"] - pep["total_qaly_loss"])
    icer, icer_status = _icer_label(incremental_cost, incremental_qaly)
    wtp = float(params["wtp_per_qaly"])
    inmb = wtp * incremental_qaly - incremental_cost

    cases_prevented = float(no_pep["symptomatic_covid"] - pep["symptomatic_covid"])
    secondary_cases_prevented = float(
        no_pep["secondary_symptomatic_covid"] - pep["secondary_symptomatic_covid"]
    )
    total_cases_prevented = float(
        no_pep["total_symptomatic_covid"] - pep["total_symptomatic_covid"]
    )
    observed_all_cause_hospitalizations_prevented = float(
        no_pep["observed_all_cause_hospitalizations"]
        - pep["observed_all_cause_hospitalizations"]
    )
    hospitalizations_prevented = float(
        no_pep["hospitalizations"] - pep["hospitalizations"]
    )
    deaths_prevented = float(no_pep["deaths"] - pep["deaths"])
    pcc_cases_prevented = float(no_pep["pcc_cases"] - pep["pcc_cases"])
    postacute_profile_cases_prevented = float(
        no_pep["postacute_profile_cases"] - pep["postacute_profile_cases"]
    )
    nnt = float("inf") if cases_prevented <= 0 else 1.0 / cases_prevented
    cost_per_case_prevented = (
        float("nan") if cases_prevented <= 0 else incremental_cost / cases_prevented
    )
    current_intervention_cost = float(pep["intervention_cost_jpy"])
    threshold_total_intervention_cost = current_intervention_cost + inmb
    threshold_drug_cost = float(params["drug_cost_pep"]) + inmb

    incremental = pd.DataFrame(
        [
            {
                "scenario_id": scenario_id,
                "structural_mode": structural_mode,
                "incremental_cost_jpy": incremental_cost,
                "incremental_qaly": incremental_qaly,
                "icer_jpy_per_qaly": icer,
                "icer_status": icer_status,
                "incremental_net_monetary_benefit_jpy": inmb,
                "wtp_jpy_per_qaly": wtp,
                "symptomatic_cases_prevented": cases_prevented,
                "secondary_symptomatic_cases_prevented": secondary_cases_prevented,
                "total_symptomatic_cases_prevented": total_cases_prevented,
                "observed_all_cause_hospitalizations_prevented": (
                    observed_all_cause_hospitalizations_prevented
                ),
                "hospitalizations_prevented": hospitalizations_prevented,
                "deaths_prevented": deaths_prevented,
                "pcc_cases_prevented": pcc_cases_prevented,
                "postacute_profile_cases_prevented": postacute_profile_cases_prevented,
                "number_needed_to_treat": nnt,
                "incremental_cost_per_symptomatic_case_prevented_jpy": cost_per_case_prevented,
                "threshold_total_pep_intervention_cost_jpy": threshold_total_intervention_cost,
                "threshold_drug_cost_jpy_holding_other_pep_costs_fixed": threshold_drug_cost,
                "cost_effective_at_wtp": bool(inmb >= 0.0),
            }
        ]
    )
    return ModelResult(arm_results=arm_results, incremental_results=incremental)
