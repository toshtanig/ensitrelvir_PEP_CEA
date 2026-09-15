from __future__ import annotations

import math

import pandas as pd

from _bootstrap import ROOT, TABLES
from ensitrelvir_pep_cea.io import (
    load_acute_death_cohort,
    load_life_table,
    load_parameter_frame,
    load_pep_microcost,
    load_postacute_utility_profile,
    load_utility_norms,
)
from ensitrelvir_pep_cea.life_table import calculate_discounted_remaining_qaly


def _parameter_map() -> dict[str, float]:
    frame = load_parameter_frame()
    return dict(
        zip(
            frame["parameter_id"].astype(str),
            frame["base_value"].astype(float),
            strict=True,
        )
    )


def run() -> None:
    params = _parameter_map()
    records: list[dict[str, object]] = []

    microcost = load_pep_microcost()
    included = microcost["basecase_included"].astype(str).str.lower().eq("yes")
    derived_delivery_cost = float(microcost.loc[included, "cost_jpy"].sum())
    records.append(
        {
            "audit_id": "D01",
            "parameter_id": "administration_cost_pep",
            "derived_value": derived_delivery_cost,
            "registered_value": params["administration_cost_pep"],
            "absolute_difference": abs(
                derived_delivery_cost - params["administration_cost_pep"]
            ),
            "tolerance": 1e-9,
            "source_file": "data/pep_microcost_japan_2026.csv",
            "derivation": "Sum cost_jpy where basecase_included=yes.",
        }
    )

    profile = load_postacute_utility_profile()
    derived_postacute_qaly = float(profile["qaly_loss"].sum())
    records.append(
        {
            "audit_id": "D02",
            "parameter_id": "postacute_qaly_loss_per_surviving_symptomatic_case",
            "derived_value": derived_postacute_qaly,
            "registered_value": params[
                "postacute_qaly_loss_per_surviving_symptomatic_case"
            ],
            "absolute_difference": abs(
                derived_postacute_qaly
                - params["postacute_qaly_loss_per_surviving_symptomatic_case"]
            ),
            "tolerance": 1e-12,
            "source_file": "data/postacute_utility_profile_japan_2025.csv",
            "derivation": "Sum interval-specific control-minus-COVID QALY losses.",
        }
    )

    _, derived_remaining_qaly = calculate_discounted_remaining_qaly(
        cohort=load_acute_death_cohort(),
        life_table=load_life_table(),
        utility_norms=load_utility_norms(),
        discount_rate=params["discount_rate_qaly"],
    )
    records.append(
        {
            "audit_id": "D03",
            "parameter_id": "remaining_qaly_if_acute_death",
            "derived_value": derived_remaining_qaly,
            "registered_value": params["remaining_qaly_if_acute_death"],
            "absolute_difference": abs(
                derived_remaining_qaly - params["remaining_qaly_if_acute_death"]
            ),
            "tolerance": 1e-9,
            "source_file": (
                "data/acute_death_cohort_japan_2025.csv; "
                "data/life_table_japan_2025.csv; "
                "data/utility_norms_japan_eq5d5l_2021.csv"
            ),
            "derivation": "Age-sex weighted lifetime QALY integration at 2% discount.",
        }
    )

    output = pd.DataFrame(records)
    output["passed"] = output["absolute_difference"] <= output["tolerance"]
    output.to_csv(
        TABLES / "derived_input_audit.csv",
        index=False,
        encoding="utf-8-sig",
    )
    print(output.to_string(index=False))
    if not bool(output["passed"].all()):
        failed = output.loc[~output["passed"], "audit_id"].astype(str).tolist()
        raise ValueError(f"Derived-input audit failed: {failed}")


if __name__ == "__main__":
    run()
