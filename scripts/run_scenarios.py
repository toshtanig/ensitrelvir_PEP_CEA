from __future__ import annotations

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from _bootstrap import FIGURES, TABLES
from ensitrelvir_pep_cea.analysis import run_all_scenarios


def run() -> None:
    results = run_all_scenarios()
    results.to_csv(TABLES / "scenario_results.csv", index=False, encoding="utf-8-sig")

    plotting = results.replace([np.inf, -np.inf], np.nan).dropna(subset=["icer_jpy_per_qaly"])
    if not plotting.empty:
        plotting = plotting.sort_values("icer_jpy_per_qaly")
        fig, ax = plt.subplots(figsize=(9, max(4, 0.45 * len(plotting))))
        ax.barh(plotting["scenario_id"], plotting["icer_jpy_per_qaly"] / 1_000_000)
        ax.axvline(5.0, linewidth=1)
        ax.set_xlabel("ICER, million JPY per QALY")
        ax.set_ylabel("Scenario")
        ax.set_title("Scenario analysis")
        fig.tight_layout()
        fig.savefig(FIGURES / "scenario_icers.png", dpi=200, bbox_inches="tight")
        plt.close(fig)


if __name__ == "__main__":
    run()
