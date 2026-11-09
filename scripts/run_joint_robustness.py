"""Robustness of the exploratory immunocompromised joint scenario (reported in Supporting Information S1, Table S12, of the journal submission).

The joint scenario combines the Japan-region placebo risk (23.0%) with the
high-risk RR 0.24 and the immunocompromised hospitalisation risk (x2.60).
This script re-evaluates it with (a) the overall-trial RR 0.33, (b) post-acute
QALY loss halved, (c) post-acute benefit through 6 months only, and runs a PSA
for the joint scenario. Model code (v0.3.3) is used as is; nothing is modified.
Run in VS Code; edit the settings block below.
"""

import sys
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Settings (edit here)
# ---------------------------------------------------------------------------
MODEL_DIR = Path(__file__).resolve().parents[1]  # repository root
OUTPUT_CSV = MODEL_DIR / "outputs" / "tables" / "joint_scenario_robustness.csv"
PSA_ITERATIONS = 10_000
PSA_SEED = 20_260_825
WTP = 5_000_000
# Override values taken from data/scenario_overrides.csv
IMMUNOCOMPROMISED_MULTIPLIER = 2.60
HOSP_IMMUNOCOMPROMISED = 0.02041     # 0.00785 x 2.60
POSTACUTE_HALF = 0.016125
POSTACUTE_THROUGH_6M = 0.01975
# ---------------------------------------------------------------------------

sys.path.insert(0, str(MODEL_DIR / "src"))
from ensitrelvir_pep_cea.io import (  # noqa: E402
    apply_scenario_overrides, base_parameters, load_parameter_frame, load_scenario, trial_probabilities,
)
from ensitrelvir_pep_cea.model import evaluate_model  # noqa: E402
from ensitrelvir_pep_cea.sampling import run_psa  # noqa: E402

frame = load_parameter_frame()
base = base_parameters(frame)

CASES = [
    # label, trial population, parameter overrides
    ("Joint: Japan region, RR 0.24, immunocompromised (reported)", "japan_region_high_risk_rr",
     {"p_hospital_given_symptomatic": HOSP_IMMUNOCOMPROMISED}),
    ("Joint with overall-trial RR 0.33", "japan_region_overall_rr",
     {"p_hospital_given_symptomatic": HOSP_IMMUNOCOMPROMISED}),
    ("Joint with post-acute QALY loss halved", "japan_region_high_risk_rr",
     {"p_hospital_given_symptomatic": HOSP_IMMUNOCOMPROMISED, "postacute_qaly_loss_per_surviving_symptomatic_case": POSTACUTE_HALF}),
    ("Joint with post-acute benefit through 6 months", "japan_region_high_risk_rr",
     {"p_hospital_given_symptomatic": HOSP_IMMUNOCOMPROMISED, "postacute_qaly_loss_per_surviving_symptomatic_case": POSTACUTE_THROUGH_6M}),
    ("Joint with observed Japan-region pair (RR 0.18)", "japan_region",
     {"p_hospital_given_symptomatic": HOSP_IMMUNOCOMPROMISED}),
]

rows = []
for label, population, overrides in CASES:
    params = dict(base)
    params.update(overrides)
    p_sym = trial_probabilities(population=population, outcome="symptomatic_covid_day10")
    res = evaluate_model(params=params, symptomatic_probabilities=p_sym,
                         structural_mode="symptomatic_mediation_profile", scenario_id=label).incremental_results.iloc[0]
    rows.append({
        "case": label,
        "incremental_cost_jpy": res["incremental_cost_jpy"],
        "incremental_qaly": res["incremental_qaly"],
        "icer_jpy_per_qaly": res["icer_jpy_per_qaly"],
        "inmb_jpy": res["incremental_net_monetary_benefit_jpy"],
        "drug_price_threshold_jpy": res["threshold_drug_cost_jpy_holding_other_pep_costs_fixed"],
    })

# PSA for the reported joint scenario (uses its registered scenario definition).
# The conditional hospitalisation risk is sampled from its base-case PERT
# distribution and multiplied by the fixed immunocompromised multiplier, so the
# lower, modal and upper values are all scaled. (Passing only the scenario mode
# would let the sampler clip 0.02041 to the base-case upper bound 0.01298.)
scenario = load_scenario("japan_region_high_risk_rr_immunocompromised")
params = apply_scenario_overrides(base, scenario.scenario_id)
psa_frame = frame.copy()
row = psa_frame["parameter_id"] == "p_hospital_given_symptomatic"
for col in ("base_value", "lower_value", "upper_value"):
    psa_frame.loc[row, col] = psa_frame.loc[row, col].astype(float) * IMMUNOCOMPROMISED_MULTIPLIER
assert abs(float(psa_frame.loc[row, "base_value"].iloc[0]) - params["p_hospital_given_symptomatic"]) < 1e-5

# Guard: every sampled parameter's scenario value must lie within its PERT bounds.
for _, r in psa_frame.iterrows():
    if str(r["include_in_psa"]).strip().lower() == "yes" and str(r["distribution"]).strip().lower() == "pert":
        v = float(params[str(r["parameter_id"])])
        assert float(r["lower_value"]) - 1e-12 <= v <= float(r["upper_value"]) + 1e-12, (r["parameter_id"], v)

psa = run_psa(psa_frame, params, scenario, n_simulations=PSA_ITERATIONS, seed=PSA_SEED)
nmb_col = "incremental_net_monetary_benefit_jpy"
p_ce = float((psa[nmb_col] > 0).mean())
rows[0]["psa_probability_cost_effective"] = p_ce
rows[0]["psa_mean_incremental_cost_jpy"] = float(psa["incremental_cost_jpy"].mean())
rows[0]["psa_mean_incremental_qaly"] = float(psa["incremental_qaly"].mean())

out = pd.DataFrame(rows)
out.to_csv(OUTPUT_CSV, index=False)
pd.set_option("display.width", 200)
print(out.to_string(index=False))
print(f"PSA column used: {nmb_col}; P(cost-effective) at JPY {WTP:,}/QALY = {p_ce:.3f}")
