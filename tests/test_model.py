from __future__ import annotations

import math

from ensitrelvir_pep_cea.analysis import run_scenario
from ensitrelvir_pep_cea.model import expected_pcc_burden_per_incident_case


def test_basecase_has_expected_trial_absolute_risk_reduction() -> None:
    result = run_scenario("base_high_risk").result.incremental_results.iloc[0]
    expected_arr = 0.09893 - 0.02356
    assert math.isclose(
        float(result["symptomatic_cases_prevented"]),
        expected_arr,
        rel_tol=1e-10,
    )
    assert math.isclose(
        float(result["number_needed_to_treat"]),
        1.0 / expected_arr,
        rel_tol=1e-10,
    )


def test_basecase_intervention_cost_is_course_plus_delivery_microcost() -> None:
    arm = run_scenario("base_high_risk").result.arm_results
    assert math.isclose(
        float(arm.loc["pep", "intervention_cost_jpy"]),
        49_630 + 8_100,
    )
    assert math.isclose(float(arm.loc["no_pep", "intervention_cost_jpy"]), 0.0)


def test_basecase_generates_positive_health_gain() -> None:
    result = run_scenario("base_high_risk").result.incremental_results.iloc[0]
    assert float(result["incremental_qaly"]) > 0.0
    assert float(result["symptomatic_cases_prevented"]) > 0.0
    assert float(result["hospitalizations_prevented"]) > 0.0
    assert float(result["postacute_profile_cases_prevented"]) > 0.0
    assert float(result["pcc_cases_prevented"]) == 0.0


def test_no_postacute_scenario_has_zero_postacute_burden() -> None:
    arm = run_scenario("high_risk_no_postacute").result.arm_results
    assert float(arm["postacute_qaly_loss"].sum()) == 0.0
    assert float(arm["postacute_cost_jpy"].sum()) == 0.0


def test_zero_hospital_attribution_removes_hospital_and_death_benefits() -> None:
    result = run_scenario(
        "high_risk_hospital_attribution_0pct"
    ).result.incremental_results.iloc[0]
    assert float(result["observed_all_cause_hospitalizations_prevented"]) > 0.0
    assert float(result["hospitalizations_prevented"]) == 0.0
    assert float(result["deaths_prevented"]) == 0.0


def test_pcc_module_returns_zero_when_horizon_is_zero() -> None:
    run = run_scenario("base_high_risk")
    params = dict(run.parameters)
    params["pcc_horizon_months"] = 0
    cost, qaly, years = expected_pcc_burden_per_incident_case(params)
    assert (cost, qaly, years) == (0.0, 0.0, 0.0)


def test_overall_trial_rr_scenario_is_more_conservative_than_subgroup_effect() -> None:
    base = run_scenario("base_high_risk").result.incremental_results.iloc[0]
    conservative = run_scenario("high_risk_overall_rr033").result.incremental_results.iloc[0]
    assert float(conservative["symptomatic_cases_prevented"]) < float(
        base["symptomatic_cases_prevented"]
    )
    assert float(conservative["icer_jpy_per_qaly"]) > float(base["icer_jpy_per_qaly"])


def test_secondary_case_bounding_scenario_preserves_direct_trial_effect() -> None:
    base = run_scenario("base_high_risk").result.incremental_results.iloc[0]
    bound = run_scenario("high_risk_secondary_cases_0p5").result.incremental_results.iloc[0]
    assert math.isclose(
        float(bound["symptomatic_cases_prevented"]),
        float(base["symptomatic_cases_prevented"]),
        rel_tol=1e-12,
    )
    assert math.isclose(
        float(bound["secondary_symptomatic_cases_prevented"]),
        0.5 * float(base["symptomatic_cases_prevented"]),
        rel_tol=1e-12,
    )
    assert float(bound["icer_jpy_per_qaly"]) > 5_000_000
