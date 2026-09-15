from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import yaml

from _bootstrap import FIGURES, ROOT, TABLES
from ensitrelvir_pep_cea.analysis import one_way_sensitivity


def run() -> None:
    config = yaml.safe_load((ROOT / "config" / "basecase.yaml").read_text(encoding="utf-8"))
    scenario_id = str(config["scenario_id"])
    dsa, base = one_way_sensitivity(scenario_id)
    dsa.to_csv(TABLES / "dsa_results.csv", index=False, encoding="utf-8-sig")

    # Drug price is handled by dedicated threshold analysis and is omitted
    # from the tornado plot so that it does not visually dominate clinical
    # and utility uncertainty. It remains in dsa_results.csv.
    top = (
        dsa.loc[dsa["parameter_id"] != "drug_cost_pep"]
        .head(15)
        .sort_values("inmb_span_jpy", ascending=True)
        .copy()
    )
    base_inmb = float(base["incremental_net_monetary_benefit_jpy"])
    left = top["inmb_min_jpy"] - base_inmb
    width = top["inmb_max_jpy"] - top["inmb_min_jpy"]

    fig, ax = plt.subplots(figsize=(10, max(6, 0.45 * len(top))))
    ax.barh(top["parameter_id"], width, left=left)
    ax.axvline(0.0, linewidth=1)
    ax.set_xlabel("Change in incremental net monetary benefit from base case, JPY")
    ax.set_ylabel("Parameter")
    ax.set_title("One-way sensitivity analysis at JPY 5 million per QALY")
    fig.tight_layout()
    fig.savefig(FIGURES / "tornado_inmb.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    run()
