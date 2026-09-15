from __future__ import annotations

import numpy as np
import pandas as pd

from ensitrelvir_pep_cea.analysis import run_scenario
from ensitrelvir_pep_cea.io import load_parameter_frame
from ensitrelvir_pep_cea.sampling import (
    EFFICACY_SAMPLING_METHOD,
    run_psa,
    sample_symptomatic_probabilities,
)


def test_psa_is_reproducible_with_fixed_seed() -> None:
    frame = load_parameter_frame()
    scenario_run = run_scenario("base_high_risk", frame)
    first = run_psa(frame, scenario_run.parameters, scenario_run.scenario, n_simulations=20, seed=123)
    second = run_psa(frame, scenario_run.parameters, scenario_run.scenario, n_simulations=20, seed=123)
    pd.testing.assert_frame_equal(first, second)


def test_psa_output_columns() -> None:
    frame = load_parameter_frame()
    scenario_run = run_scenario("base_high_risk", frame)
    output = run_psa(frame, scenario_run.parameters, scenario_run.scenario, n_simulations=5, seed=1)
    assert len(output) == 5
    assert {"incremental_cost_jpy", "incremental_qaly", "cost_effective_at_wtp"}.issubset(output.columns)

def test_trial_efficacy_sampling_is_coherent() -> None:
    rng = np.random.default_rng(42)
    probabilities, risk_ratio = sample_symptomatic_probabilities(
        population="high_risk",
        rng=rng,
    )
    assert EFFICACY_SAMPLING_METHOD == (
        "control_risk_jeffreys_plus_reported_rr_lognormal"
    )
    assert 0.0 <= probabilities["no_pep"] <= 1.0
    assert 0.0 <= probabilities["pep"] <= 1.0
    assert risk_ratio > 0.0
    assert np.isclose(
        probabilities["pep"],
        min(1.0, probabilities["no_pep"] * risk_ratio),
    )

