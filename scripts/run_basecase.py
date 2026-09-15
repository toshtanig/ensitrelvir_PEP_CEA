from __future__ import annotations

import math
from pathlib import Path

import pandas as pd
import yaml

from _bootstrap import ROOT, TABLES
from ensitrelvir_pep_cea.analysis import input_traceability_table, run_scenario


def _format_number(value: float, digits: int = 3) -> str:
    if math.isnan(value):
        return "NA"
    return f"{value:,.{digits}f}"


def run() -> None:
    config = yaml.safe_load((ROOT / "config" / "basecase.yaml").read_text(encoding="utf-8"))
    scenario_id = str(config["scenario_id"])
    scenario_run = run_scenario(scenario_id)

    arm = scenario_run.result.arm_results.reset_index()
    incremental = scenario_run.result.incremental_results.copy()
    arm.to_csv(TABLES / "basecase_arm_results.csv", index=False, encoding="utf-8-sig")
    incremental.to_csv(
        TABLES / "basecase_incremental_results.csv", index=False, encoding="utf-8-sig"
    )

    outcome_columns = [
        "symptomatic_covid",
        "secondary_symptomatic_covid",
        "total_symptomatic_covid",
        "observed_all_cause_hospitalizations",
        "hospitalizations",
        "icu_admissions",
        "mechanical_ventilation",
        "deaths",
        "pcc_cases",
        "pcc_person_years",
    ]
    per_1000 = arm[["arm", *outcome_columns]].copy()
    per_1000[outcome_columns] = per_1000[outcome_columns] * 1000.0
    per_1000.to_csv(TABLES / "basecase_events_per_1000.csv", index=False, encoding="utf-8-sig")

    traceability = input_traceability_table(scenario_id)
    traceability.to_csv(TABLES / "input_traceability_checks.csv", index=False, encoding="utf-8-sig")

    pep = scenario_run.result.arm_results.loc["pep"]
    no_pep = scenario_run.result.arm_results.loc["no_pep"]
    component_rows: list[dict[str, float | str]] = []
    for component, column in (
        ("PEP intervention", "intervention_cost_jpy"),
        ("Acute healthcare", "acute_healthcare_cost_jpy"),
        ("Post-acute healthcare", "postacute_cost_jpy"),
        ("Total cost", "total_cost_jpy"),
    ):
        component_rows.append(
            {
                "outcome_type": "cost",
                "component": component,
                "pep_value": float(pep[column]),
                "no_pep_value": float(no_pep[column]),
                "incremental_value": float(pep[column] - no_pep[column]),
                "incremental_definition": "PEP minus no PEP; positive values increase cost",
            }
        )
    qaly_components = (
        ("Acute morbidity", "acute_morbidity_qaly_loss"),
        ("Acute mortality", "mortality_qaly_loss"),
        ("Post-acute morbidity", "postacute_qaly_loss"),
        ("Adverse events", "adverse_event_qaly_loss"),
        ("Total QALY", "total_qaly_loss"),
    )
    total_qaly_gain = float(no_pep["total_qaly_loss"] - pep["total_qaly_loss"])
    for component, column in qaly_components:
        gain = float(no_pep[column] - pep[column])
        component_rows.append(
            {
                "outcome_type": "qaly",
                "component": component,
                "pep_value": float(pep[column]),
                "no_pep_value": float(no_pep[column]),
                "incremental_value": gain,
                "incremental_definition": "No PEP QALY loss minus PEP QALY loss; positive values are QALYs gained",
                "share_of_total_qaly_gain": (
                    gain / total_qaly_gain
                    if total_qaly_gain > 0.0 and component != "Total QALY"
                    else float("nan")
                ),
            }
        )
    pd.DataFrame(component_rows).to_csv(
        TABLES / "basecase_component_decomposition.csv",
        index=False,
        encoding="utf-8-sig",
    )

    result = incremental.iloc[0]
    mortality_qaly_gain = float(
        no_pep["mortality_qaly_loss"] - pep["mortality_qaly_loss"]
    )
    mortality_share = mortality_qaly_gain / total_qaly_gain if total_qaly_gain > 0 else float("nan")
    summary = f"""# Base-case analysis summary

- Scenario: `{scenario_id}`
- Perspective: public healthcare payer
- Incremental cost: JPY {_format_number(float(result['incremental_cost_jpy']), 0)} per exposed contact
- Incremental QALYs: {_format_number(float(result['incremental_qaly']), 6)} per exposed contact
- QALY gain attributed to modeled acute mortality avoidance: {_format_number(mortality_qaly_gain, 6)} ({_format_number(mortality_share * 100, 1)}% of total QALY gain)
- ICER: JPY {_format_number(float(result['icer_jpy_per_qaly']), 0)} per QALY
- Incremental net monetary benefit at JPY {_format_number(float(result['wtp_jpy_per_qaly']), 0)}/QALY: JPY {_format_number(float(result['incremental_net_monetary_benefit_jpy']), 0)}
- Cost-effective at the reference threshold: {bool(result['cost_effective_at_wtp'])}
- Symptomatic cases prevented: {_format_number(float(result['symptomatic_cases_prevented']) * 1000, 2)} per 1,000 treated contacts
- Hospitalizations prevented: {_format_number(float(result['hospitalizations_prevented']) * 1000, 3)} per 1,000 treated contacts
- Deaths prevented: {_format_number(float(result['deaths_prevented']) * 1000, 4)} per 1,000 treated contacts
- Surviving symptomatic cases contributing to the post-acute profile prevented: {_format_number(float(result['postacute_profile_cases_prevented']) * 1000, 2)} per 1,000 treated contacts
- Number needed to treat to prevent one symptomatic case: {_format_number(float(result['number_needed_to_treat']), 2)}
- Maximum total PEP intervention cost consistent with zero INMB: JPY {_format_number(float(result['threshold_total_pep_intervention_cost_jpy']), 0)}
- Maximum drug acquisition cost, holding other PEP costs fixed: JPY {_format_number(float(result['threshold_drug_cost_jpy_holding_other_pep_costs_fixed']), 0)}

This is a manuscript-development base case, not a reimbursement conclusion. Severe-outcome effects are indirectly mediated through prevented symptomatic COVID-19 because the randomized trial observed no COVID-19-related hospitalization or death. Remaining QALY loss is derived from an age-82, 54%-male proxy using the 2025 Japanese life table and Japanese EQ-5D-5L norms. The base case attributes all 28-day all-cause admissions in the outpatient claims source to COVID-19; 50% and 0% attribution scenarios quantify this structural uncertainty.
"""
    (ROOT / "outputs" / "analysis_summary.md").write_text(summary, encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    run()
