from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd


VALID_SEX_VALUES = {"male", "female"}


def _require_columns(frame: pd.DataFrame, required: Iterable[str], name: str) -> None:
    missing = set(required).difference(frame.columns)
    if missing:
        raise ValueError(f"{name} is missing columns: {sorted(missing)}")


def _utility_for_age(
    utility_norms: pd.DataFrame,
    sex: str,
    age: int,
) -> float:
    matches = utility_norms.loc[
        (utility_norms["sex"].astype(str) == sex)
        & (utility_norms["age_start"].astype(int) <= age)
        & (utility_norms["age_end"].astype(int) >= age)
    ]
    if len(matches) != 1:
        raise ValueError(
            f"Expected one utility norm for sex={sex}, age={age}; found {len(matches)}."
        )
    value = float(matches.iloc[0]["utility"])
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"Utility must be between zero and one; received {value}.")
    return value


def _remaining_qaly_for_stratum(
    start_age: int,
    sex: str,
    mortality_hazard_ratio: float,
    life_table: pd.DataFrame,
    utility_norms: pd.DataFrame,
    discount_rate: float,
) -> float:
    if sex not in VALID_SEX_VALUES:
        raise ValueError(f"sex must be one of {sorted(VALID_SEX_VALUES)}; received '{sex}'.")
    if start_age < 0:
        raise ValueError("Age must be nonnegative.")
    if mortality_hazard_ratio <= 0.0:
        raise ValueError("mortality_hazard_ratio must be positive.")
    if discount_rate < 0.0:
        raise ValueError("discount_rate must be nonnegative.")

    selected = life_table.loc[life_table["sex"].astype(str) == sex].copy()
    selected["age"] = pd.to_numeric(selected["age"], errors="raise").astype(int)
    selected["lx"] = pd.to_numeric(selected["lx"], errors="raise").astype(float)
    selected = selected.sort_values("age").set_index("age")
    if start_age not in selected.index:
        raise ValueError(f"Life table has no row for sex={sex}, age={start_age}.")
    if (selected["lx"] < 0).any() or not selected["lx"].is_monotonic_decreasing:
        raise ValueError(f"Life-table lx values must be nonnegative and nonincreasing for {sex}.")

    max_age = int(selected.index.max())
    survival = 1.0
    qaly = 0.0
    for year, attained_age in enumerate(range(start_age, max_age + 1)):
        lx_current = float(selected.loc[attained_age, "lx"])
        if attained_age < max_age and attained_age + 1 in selected.index and lx_current > 0.0:
            lx_next = float(selected.loc[attained_age + 1, "lx"])
            qx = min(1.0, max(0.0, 1.0 - lx_next / lx_current))
        else:
            qx = 1.0

        # Proportional-hazard approximation for high-risk mortality calibration.
        adjusted_qx = 1.0 - (1.0 - qx) ** mortality_hazard_ratio
        survival_next = survival * (1.0 - adjusted_qx)
        average_alive = 0.5 * (survival + survival_next)
        utility = _utility_for_age(utility_norms, sex, attained_age)
        discount = (1.0 + discount_rate) ** (-(year + 0.5))
        qaly += average_alive * utility * discount
        survival = survival_next
        if survival < 1e-12:
            break
    return float(qaly)


def calculate_discounted_remaining_qaly(
    cohort: pd.DataFrame,
    life_table: pd.DataFrame,
    utility_norms: pd.DataFrame,
    discount_rate: float = 0.02,
) -> tuple[pd.DataFrame, float]:
    """Calculate age-sex weighted discounted QALYs lost per acute death.

    Parameters
    ----------
    cohort:
        Columns: age, sex, weight, and optional mortality_hazard_ratio.
    life_table:
        Columns: age, sex, lx. Ages must be consecutive within each sex.
    utility_norms:
        Columns: sex, age_start, age_end, utility. Exactly one age band must
        match every attained age used by the cohort.
    discount_rate:
        Annual QALY discount rate.

    Returns
    -------
    stratum_results, weighted_mean_qaly
    """

    _require_columns(cohort, ["age", "sex", "weight"], "cohort")
    _require_columns(life_table, ["age", "sex", "lx"], "life_table")
    _require_columns(
        utility_norms,
        ["sex", "age_start", "age_end", "utility"],
        "utility_norms",
    )

    working = cohort.copy()
    working["age"] = pd.to_numeric(working["age"], errors="raise").astype(int)
    working["weight"] = pd.to_numeric(working["weight"], errors="raise").astype(float)
    if "mortality_hazard_ratio" not in working.columns:
        working["mortality_hazard_ratio"] = 1.0
    working["mortality_hazard_ratio"] = pd.to_numeric(
        working["mortality_hazard_ratio"], errors="raise"
    ).astype(float)

    if (working["weight"] < 0.0).any() or float(working["weight"].sum()) <= 0.0:
        raise ValueError("Cohort weights must be nonnegative and sum to a positive value.")
    working["normalized_weight"] = working["weight"] / float(working["weight"].sum())

    qaly_values: list[float] = []
    for row in working.itertuples(index=False):
        qaly_values.append(
            _remaining_qaly_for_stratum(
                start_age=int(row.age),
                sex=str(row.sex),
                mortality_hazard_ratio=float(row.mortality_hazard_ratio),
                life_table=life_table,
                utility_norms=utility_norms,
                discount_rate=float(discount_rate),
            )
        )
    working["discounted_remaining_qaly"] = qaly_values
    working["weighted_qaly_contribution"] = (
        working["normalized_weight"] * working["discounted_remaining_qaly"]
    )
    weighted_mean = float(working["weighted_qaly_contribution"].sum())
    return working, weighted_mean
