"""Two-way threshold analysis: value-based drug price as a function of baseline risk.

For each post-acute assumption (base case, through 6 months, halved, none), the
drug acquisition cost at which incremental net monetary benefit is zero at the
reference value is computed across a grid of

* the symptomatic COVID-19 risk without PEP (panel A), holding the high-risk
  subgroup relative risk of 0.24 fixed; and
* the hospitalization risk after symptomatic COVID-19 (panel B), holding the
  high-risk subgroup arm risks fixed.

All other inputs stay at their base-case values. The threshold is
``drug_cost_pep + INMB`` because INMB is linear in the drug cost with slope -1.

Outputs: outputs/tables/two_way_threshold_control_risk.csv and
outputs/tables/two_way_threshold_hospital_risk.csv.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from _bootstrap import TABLES
from ensitrelvir_pep_cea.analysis import run_scenario
from ensitrelvir_pep_cea.io import apply_scenario_overrides, trial_effect_estimate
from ensitrelvir_pep_cea.sampling import _evaluate_profile_incremental_fast

POSTACUTE_VARIANTS = [
    ("base_high_risk", "Base case (months 1-12)"),
    ("high_risk_postacute_through6m", "Through 6 months only"),
    ("high_risk_postacute_half", "Halved"),
    ("high_risk_no_postacute", "No post-acute benefit"),
]


def _threshold(params: dict[str, float], p_sym: dict[str, float]) -> float:
    result = _evaluate_profile_incremental_fast(params, p_sym)
    return float(params["drug_cost_pep"]) + float(
        result["incremental_net_monetary_benefit_jpy"]
    )


def run() -> None:
    base_run = run_scenario("base_high_risk")
    base_params = dict(base_run.parameters)
    base_p_sym = dict(
        (k, float(v))
        for k, v in base_run.result.arm_results["symptomatic_covid"].items()
    )
    rr = float(
        trial_effect_estimate(
            population="high_risk",
            outcome="symptomatic_covid_day10",
            effect_measure="risk_ratio",
        )["estimate"]
    )

    control_grid = np.linspace(0.0, 0.30, 301)
    hospital_grid = np.linspace(0.0, 0.20, 201)
    rows_a: list[dict[str, float | str]] = []
    rows_b: list[dict[str, float | str]] = []
    for scenario_id, label in POSTACUTE_VARIANTS:
        params = apply_scenario_overrides(base_params, scenario_id) if scenario_id != "base_high_risk" else dict(base_params)
        for risk in control_grid:
            p_sym = {"no_pep": float(risk), "pep": min(1.0, float(risk) * rr)}
            rows_a.append(
                {
                    "postacute_variant": scenario_id,
                    "postacute_label": label,
                    "control_symptomatic_risk": float(risk),
                    "relative_risk": rr,
                    "drug_cost_threshold_jpy": _threshold(params, p_sym),
                }
            )
        for p_hosp in hospital_grid:
            p = dict(params)
            p["p_hospital_given_symptomatic"] = float(p_hosp)
            rows_b.append(
                {
                    "postacute_variant": scenario_id,
                    "postacute_label": label,
                    "p_hospital_given_symptomatic": float(p_hosp),
                    "drug_cost_threshold_jpy": _threshold(p, base_p_sym),
                }
            )
    pd.DataFrame(rows_a).to_csv(
        TABLES / "two_way_threshold_control_risk.csv", index=False, encoding="utf-8-sig"
    )
    pd.DataFrame(rows_b).to_csv(
        TABLES / "two_way_threshold_hospital_risk.csv", index=False, encoding="utf-8-sig"
    )
    # Reference points for annotation
    ref = pd.DataFrame(
        [
            {"point": "high_risk_subgroup", "control_symptomatic_risk": float(base_p_sym["no_pep"]),
             "drug_cost_threshold_jpy": _threshold(base_params, base_p_sym)},
            {"point": "japan_region_with_high_risk_rr", "control_symptomatic_risk": 62 / 270,
             "drug_cost_threshold_jpy": _threshold(base_params, {"no_pep": 62 / 270, "pep": 62 / 270 * rr})},
        ]
    )
    ref.to_csv(TABLES / "two_way_threshold_reference_points.csv", index=False, encoding="utf-8-sig")
    print(ref.to_string(index=False))


if __name__ == "__main__":
    run()
