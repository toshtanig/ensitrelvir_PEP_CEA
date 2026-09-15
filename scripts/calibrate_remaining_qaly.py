from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from _bootstrap import ROOT, TABLES
from ensitrelvir_pep_cea.life_table import calculate_discounted_remaining_qaly


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Calculate discounted remaining QALYs lost per acute death from an "
            "age-sex cohort distribution, a life table, and utility norms."
        )
    )
    parser.add_argument(
        "--cohort",
        type=Path,
        default=ROOT / "data" / "acute_death_cohort_japan_2025.csv",
    )
    parser.add_argument(
        "--life-table",
        type=Path,
        default=ROOT / "data" / "life_table_japan_2025.csv",
    )
    parser.add_argument(
        "--utility-norms",
        type=Path,
        default=ROOT / "data" / "utility_norms_japan_eq5d5l_2021.csv",
    )
    parser.add_argument("--discount-rate", type=float, default=0.02)
    parser.add_argument(
        "--output",
        type=Path,
        default=TABLES / "acute_death_qaly_calibration.csv",
    )
    return parser.parse_args()


def run() -> None:
    args = _arguments()
    cohort = pd.read_csv(args.cohort, encoding="utf-8-sig")
    life_table = pd.read_csv(args.life_table, encoding="utf-8-sig")
    utility_norms = pd.read_csv(args.utility_norms, encoding="utf-8-sig")
    results, weighted_mean = calculate_discounted_remaining_qaly(
        cohort=cohort,
        life_table=life_table,
        utility_norms=utility_norms,
        discount_rate=float(args.discount_rate),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(args.output, index=False, encoding="utf-8-sig")
    print(results.to_string(index=False))
    print(f"Weighted discounted remaining QALYs per acute death: {weighted_mean:.6f}")
    print(
        "The default run recalculates the v0.3.2 age-82, 54%-male proxy used in "
        "the base case. Supply explicit files to evaluate another cohort."
    )


if __name__ == "__main__":
    run()
