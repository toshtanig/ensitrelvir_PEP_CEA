from __future__ import annotations

import numpy as np
import pandas as pd
import yaml
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from _bootstrap import FIGURES, ROOT, TABLES
from ensitrelvir_pep_cea.analysis import run_scenario
from ensitrelvir_pep_cea.io import load_parameter_frame
from ensitrelvir_pep_cea.sampling import (
    EFFICACY_SAMPLING_DESCRIPTION,
    EFFICACY_SAMPLING_METHOD,
    cost_effectiveness_acceptability_curve,
    run_psa,
)


def run() -> None:
    config = yaml.safe_load((ROOT / "config" / "basecase.yaml").read_text(encoding="utf-8"))
    scenario_id = str(config["scenario_id"])
    n = int(config["psa_iterations"])
    seed = int(config["random_seed"])
    configured_method = str(config["efficacy_sampling_method"])
    if configured_method != EFFICACY_SAMPLING_METHOD:
        raise ValueError(
            "Unsupported efficacy sampling method in config: "
            f"{configured_method}"
        )

    parameter_frame = load_parameter_frame()
    scenario_run = run_scenario(scenario_id, parameter_frame)
    psa = run_psa(
        parameter_frame=parameter_frame,
        scenario_params=scenario_run.parameters,
        scenario=scenario_run.scenario,
        n_simulations=n,
        seed=seed,
    )
    psa.to_csv(
        TABLES / "psa_results.csv.gz",
        index=False,
        compression={"method": "gzip", "compresslevel": 9, "mtime": 0},
    )

    summary = pd.DataFrame(
        [
            {
                "scenario_id": scenario_id,
                "iterations": n,
                "seed": seed,
                "efficacy_sampling_method": EFFICACY_SAMPLING_METHOD,
                "efficacy_sampling_description": EFFICACY_SAMPLING_DESCRIPTION,
                "mean_incremental_cost_jpy": psa["incremental_cost_jpy"].mean(),
                "q025_incremental_cost_jpy": psa["incremental_cost_jpy"].quantile(0.025),
                "q975_incremental_cost_jpy": psa["incremental_cost_jpy"].quantile(0.975),
                "mean_incremental_qaly": psa["incremental_qaly"].mean(),
                "q025_incremental_qaly": psa["incremental_qaly"].quantile(0.025),
                "q975_incremental_qaly": psa["incremental_qaly"].quantile(0.975),
                "mean_incremental_nmb_jpy": psa["incremental_net_monetary_benefit_jpy"].mean(),
                "q025_incremental_nmb_jpy": psa["incremental_net_monetary_benefit_jpy"].quantile(0.025),
                "q975_incremental_nmb_jpy": psa["incremental_net_monetary_benefit_jpy"].quantile(0.975),
                "probability_cost_effective_at_base_wtp": psa["cost_effective_at_wtp"].mean(),
                "probability_cost_saving": (psa["incremental_cost_jpy"] < 0).mean(),
                "probability_qaly_gain": (psa["incremental_qaly"] > 0).mean(),
            }
        ]
    )
    summary.to_csv(TABLES / "psa_summary.csv", index=False, encoding="utf-8-sig")

    grid_config = config["wtp_grid_jpy_per_qaly"]
    wtp_grid = np.arange(
        float(grid_config["start"]),
        float(grid_config["stop"]) + float(grid_config["step"]),
        float(grid_config["step"]),
    )
    ceac = cost_effectiveness_acceptability_curve(psa, wtp_grid)
    ceac.to_csv(TABLES / "ceac.csv", index=False, encoding="utf-8-sig")

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(
        psa["incremental_qaly"],
        psa["incremental_cost_jpy"],
        s=8,
        alpha=0.25,
    )
    q_min = min(float(psa["incremental_qaly"].min()), 0.0)
    q_max = max(float(psa["incremental_qaly"].max()), 0.0)
    x = np.linspace(q_min, q_max, 200)
    wtp = float(scenario_run.parameters["wtp_per_qaly"])
    ax.plot(x, wtp * x, linewidth=1)
    ax.axhline(0.0, linewidth=0.8)
    ax.axvline(0.0, linewidth=0.8)
    ax.set_xlabel("Incremental QALYs")
    ax.set_ylabel("Incremental cost, JPY")
    ax.set_title("Cost-effectiveness plane")
    fig.tight_layout()
    fig.savefig(FIGURES / "cost_effectiveness_plane.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(ceac["wtp_jpy_per_qaly"] / 1_000_000, ceac["probability_cost_effective"])
    ax.set_ylim(0.0, 1.0)
    ax.set_xlabel("Willingness-to-pay, million JPY per QALY")
    ax.set_ylabel("Probability cost-effective")
    ax.set_title("Cost-effectiveness acceptability curve")
    fig.tight_layout()
    fig.savefig(FIGURES / "ceac.png", dpi=200, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    run()
