from __future__ import annotations

from pathlib import Path

import pandas as pd

from ensitrelvir_pep_cea.life_table import calculate_discounted_remaining_qaly


EXAMPLES = Path(__file__).resolve().parents[1] / "examples" / "cohort_calibration"


def _inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    cohort = pd.read_csv(EXAMPLES / "cohort_distribution_synthetic.csv")
    life_table = pd.read_csv(EXAMPLES / "life_table_synthetic.csv")
    utility = pd.read_csv(EXAMPLES / "utility_norms_synthetic.csv")
    return cohort, life_table, utility


def test_qaly_calibration_is_positive_and_weighted() -> None:
    cohort, life_table, utility = _inputs()
    output, mean_qaly = calculate_discounted_remaining_qaly(
        cohort, life_table, utility, discount_rate=0.02
    )
    assert mean_qaly > 0.0
    assert abs(output["normalized_weight"].sum() - 1.0) < 1e-12
    assert abs(output["weighted_qaly_contribution"].sum() - mean_qaly) < 1e-12


def test_higher_mortality_hazard_reduces_remaining_qaly() -> None:
    cohort, life_table, utility = _inputs()
    base = cohort.iloc[[0]].copy()
    high = base.copy()
    high["mortality_hazard_ratio"] = 2.0
    _, base_qaly = calculate_discounted_remaining_qaly(base, life_table, utility)
    _, high_qaly = calculate_discounted_remaining_qaly(high, life_table, utility)
    assert high_qaly < base_qaly
