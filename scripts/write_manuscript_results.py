from __future__ import annotations

import math

import pandas as pd

from _bootstrap import ROOT, TABLES


def _number(value: float, digits: int = 2) -> str:
    if math.isnan(value):
        return "not reached"
    return f"{value:,.{digits}f}"


def _scenario(frame: pd.DataFrame, scenario_id: str) -> pd.Series:
    selected = frame.loc[frame["scenario_id"] == scenario_id]
    if len(selected) != 1:
        raise ValueError(f"Expected one scenario row for {scenario_id}.")
    return selected.iloc[0]


def run() -> None:
    base = pd.read_csv(
        TABLES / "basecase_incremental_results.csv", encoding="utf-8-sig"
    ).iloc[0]
    components = pd.read_csv(
        TABLES / "basecase_component_decomposition.csv", encoding="utf-8-sig"
    )
    scenarios = pd.read_csv(TABLES / "scenario_results.csv", encoding="utf-8-sig")
    psa = pd.read_csv(TABLES / "psa_summary.csv", encoding="utf-8-sig").iloc[0]
    thresholds = pd.read_csv(TABLES / "threshold_summary.csv", encoding="utf-8-sig")

    mortality = components.loc[
        (components["outcome_type"] == "qaly")
        & (components["component"] == "Acute mortality")
    ].iloc[0]
    no_mortality = _scenario(scenarios, "high_risk_no_mortality")
    no_postacute = _scenario(scenarios, "high_risk_no_postacute")
    attribution_50 = _scenario(
        scenarios, "high_risk_hospital_attribution_50pct"
    )
    attribution_0 = _scenario(
        scenarios, "high_risk_hospital_attribution_0pct"
    )
    age65 = _scenario(scenarios, "high_risk_age65_hospital_risk")
    bcell = _scenario(scenarios, "high_risk_bcell_depleting_airr510")

    threshold_map = thresholds.set_index("parameter_id")["zero_inmb_crossing"]
    drug_threshold = float(threshold_map.loc["drug_cost_pep"])
    hospital_threshold = float(
        threshold_map.loc["p_hospital_given_symptomatic"]
    )

    text = f"""# Manuscript results draft generated from model outputs

This text is generated automatically and requires clinical and statistical review after parameter lock. It describes a public-healthcare-payer research analysis and is not a reimbursement conclusion.

## Base-case results

Among 1,000 high-risk exposed household contacts, ensitrelvir post-exposure prophylaxis was projected to prevent {_number(float(base['symptomatic_cases_prevented']) * 1000, 2)} symptomatic COVID-19 cases, {_number(float(base['hospitalizations_prevented']) * 1000, 3)} COVID-19-attributable hospitalizations, and {_number(float(base['deaths_prevented']) * 1000, 4)} acute deaths. It also prevented {_number(float(base['postacute_profile_cases_prevented']) * 1000, 2)} surviving symptomatic cases to which the Japanese one-year post-acute utility profile would otherwise apply.

The incremental cost was JPY {_number(float(base['incremental_cost_jpy']), 0)} and the incremental QALY gain was {_number(float(base['incremental_qaly']), 6)} per exposed contact, yielding an ICER of JPY {_number(float(base['icer_jpy_per_qaly']), 0)} per QALY gained. Incremental net monetary benefit at JPY {_number(float(base['wtp_jpy_per_qaly']), 0)} per QALY was JPY {_number(float(base['incremental_net_monetary_benefit_jpy']), 0)} per contact.

Acute mortality avoidance contributed {_number(float(mortality['incremental_value']), 6)} QALYs per contact, or {_number(float(mortality['share_of_total_qaly_gain']) * 100, 1)}% of the total gain. This mortality benefit was extrapolated rather than observed in SCORPIO-PEP.

## Probabilistic sensitivity analysis

Across {int(psa['iterations']):,} simulations, mean incremental cost was JPY {_number(float(psa['mean_incremental_cost_jpy']), 0)} and mean incremental QALYs were {_number(float(psa['mean_incremental_qaly']), 6)}. The corresponding 95% simulation intervals were JPY {_number(float(psa['q025_incremental_cost_jpy']), 0)} to JPY {_number(float(psa['q975_incremental_cost_jpy']), 0)}, and {_number(float(psa['q025_incremental_qaly']), 6)} to {_number(float(psa['q975_incremental_qaly']), 6)} QALYs. The probability of cost-effectiveness at JPY 5 million per QALY was {_number(float(psa['probability_cost_effective_at_base_wtp']) * 100, 2)}%.

## Structural analyses

Excluding acute mortality produced an ICER of JPY {_number(float(no_mortality['icer_jpy_per_qaly']), 0)} per QALY. Excluding the one-year post-acute utility profile produced JPY {_number(float(no_postacute['icer_jpy_per_qaly']), 0)} per QALY. Attributing 50% and 0% of observed 28-day all-cause admissions to COVID-19 produced ICERs of JPY {_number(float(attribution_50['icer_jpy_per_qaly']), 0)} and JPY {_number(float(attribution_0['icer_jpy_per_qaly']), 0)} per QALY, respectively.

Using the directly observed untreated hospitalization risk among patients aged at least 65 years produced an ICER of JPY {_number(float(age65['icer_jpy_per_qaly']), 0)} per QALY. An exploratory B-cell-depleting-therapy extrapolation produced JPY {_number(float(bcell['icer_jpy_per_qaly']), 0)} per QALY.

Holding other delivery costs fixed, the drug acquisition-cost threshold for zero incremental net monetary benefit was JPY {_number(drug_threshold, 0)} per course. At the current modeled drug and delivery costs, the hospitalization probability conditional on symptomatic COVID-19 would need to reach approximately {_number(hospital_threshold * 100, 1)}% for zero incremental net monetary benefit, when a crossing occurred within the prespecified range.

## Interpretation constraints

The randomized evidence identifies prevention of symptomatic COVID-19, not hospitalization or mortality. The base absolute hospitalization risk comes from 28-day all-cause hospitalization in diagnosed Japanese high-risk outpatients, while mortality comes from a separate contemporary hospitalized cohort. The base-case linkage is therefore an explicit extrapolation. Direct Japanese incremental post-acute medical cost remains an evidence gap and is set to zero in the payer base case, with prespecified positive-cost scenarios.
"""
    (ROOT / "outputs" / "manuscript_results_draft.md").write_text(
        text, encoding="utf-8"
    )
    print("Wrote outputs/manuscript_results_draft.md")


if __name__ == "__main__":
    run()
