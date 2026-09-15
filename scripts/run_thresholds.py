from __future__ import annotations

import numpy as np
import pandas as pd
import yaml
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from _bootstrap import FIGURES, ROOT, TABLES
from ensitrelvir_pep_cea.analysis import estimate_zero_nmb_crossing, threshold_grid


def _make_plot(grid: pd.DataFrame, parameter_id: str, output_name: str) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(grid["parameter_value"], grid["incremental_net_monetary_benefit_jpy"])
    ax.axhline(0.0, linewidth=1)
    ax.set_xlabel(parameter_id)
    ax.set_ylabel("Incremental net monetary benefit, JPY")
    ax.set_title(f"Threshold analysis: {parameter_id}")
    fig.tight_layout()
    fig.savefig(FIGURES / output_name, dpi=200, bbox_inches="tight")
    plt.close(fig)


def run() -> None:
    config = yaml.safe_load((ROOT / "config" / "basecase.yaml").read_text(encoding="utf-8"))
    scenario_id = str(config["scenario_id"])
    records: list[dict[str, float | str | None]] = []

    for parameter_id, settings in config["threshold_analyses"].items():
        values = np.linspace(
            float(settings["start"]),
            float(settings["stop"]),
            int(settings["points"]),
        )
        grid = threshold_grid(scenario_id, parameter_id, values)
        filename = f"threshold_{parameter_id}.csv"
        grid.to_csv(TABLES / filename, index=False, encoding="utf-8-sig")
        crossing = estimate_zero_nmb_crossing(grid)
        records.append(
            {
                "scenario_id": scenario_id,
                "parameter_id": parameter_id,
                "zero_inmb_crossing": crossing,
                "grid_min": float(values.min()),
                "grid_max": float(values.max()),
            }
        )
        _make_plot(grid, parameter_id, f"threshold_{parameter_id}.png")

    pd.DataFrame(records).to_csv(
        TABLES / "threshold_summary.csv", index=False, encoding="utf-8-sig"
    )


if __name__ == "__main__":
    run()
