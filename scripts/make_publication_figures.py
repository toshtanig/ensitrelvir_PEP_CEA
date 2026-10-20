"""Draw the three publication figures from the generated model outputs.

Figure 1: decision-analytic model structure (schematic; no model output needed).
Figure 2: one-way sensitivity analysis (tornado) of non-price inputs from
          outputs/tables/dsa_results.csv.
Figure 3: cost-effectiveness acceptability curve from outputs/tables/ceac.csv.
Figure 4: two-way price thresholds from outputs/tables/two_way_threshold_*.csv.

Figures are written to outputs/figures/publication/ as 600-dpi PNG files.
Journal-specific conversion (for example CMYK TIFF) is done outside this script.
"""

from __future__ import annotations

import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from _bootstrap import FIGURES, TABLES

OUT = FIGURES / "publication"
BASE_WTP = 5_000_000.0

DSA_LABELS = {
    "postacute_qaly_loss_per_surviving_symptomatic_case": "Post-acute QALY loss per surviving case",
    "postacute_cost_per_surviving_symptomatic_case": "Post-acute direct medical cost per surviving case",
    "trial_control_symptomatic_risk": "Symptomatic COVID-19 risk without PEP",
    "additional_pep_access_cost": "Additional PEP access cost",
    "trial_relative_risk_symptomatic_covid": "Relative risk of symptomatic COVID-19",
    "administration_cost_pep": "PEP delivery cost",
    "incremental_ae_cost_pep": "Incremental adverse-event cost",
    "cost_hospitalization": "Cost per hospitalization",
    "p_hospital_given_symptomatic": "Hospitalization risk after symptomatic COVID-19",
    "hospitalization_attribution_fraction": "Hospitalization attribution fraction",
    "p_death_given_hospital": "In-hospital mortality",
    "symptom_duration_outpatient_days": "Duration of outpatient symptoms",
    "incremental_ae_qaly_loss_pep": "Incremental adverse-event QALY loss",
    "remaining_qaly_if_acute_death": "QALYs lost per acute death",
    "acute_cost_price_adjustment_factor": "Acute cost price adjustment factor",
    "disutility_outpatient": "Outpatient acute utility decrement",
    "cost_outpatient": "Outpatient symptomatic care cost",
    "discount_rate_qaly": "QALY discount rate",
    "disutility_hospital": "Inpatient utility decrement",
    "los_hospital_days": "Hospital length of stay",
    "discount_rate_cost": "Cost discount rate",
    "drug_cost_pep": "Ensitrelvir acquisition cost",
}


def _box(ax, x, y, w, h, text, fontsize=8.5):
    patch = FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.0,rounding_size=0.015",
        linewidth=1.0, edgecolor="black", facecolor="white",
    )
    ax.add_patch(patch)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize, wrap=True)
    return (x, y, w, h)


def _arrow(ax, p_from, p_to, label=None, frac=0.5, fontsize=8):
    x0, y0, w0, h0 = p_from
    x1, y1, w1, h1 = p_to
    start = (x0 + w0 / 2, y0)
    end = (x1 - w1 / 2, y1)
    ax.annotate(
        "", xy=end, xytext=start,
        arrowprops=dict(arrowstyle="-|>", linewidth=1.0, color="black", shrinkA=0, shrinkB=0),
    )
    if label:
        mx = start[0] + frac * (end[0] - start[0])
        my = start[1] + frac * (end[1] - start[1])
        ax.text(mx, my, label, ha="center", va="center", fontsize=fontsize, style="italic",
                bbox=dict(boxstyle="square,pad=0.15", facecolor="white", edgecolor="none"))


def figure1_model_structure() -> None:
    fig, ax = plt.subplots(figsize=(13, 7.5))
    ax.set_xlim(0, 1.0)
    ax.set_ylim(-0.06, 1.01)
    ax.axis("off")
    H = 0.13

    root = _box(ax, 0.10, 0.50, 0.18, 0.20,
                "High-risk household contact\nwithin 72 hours of index-case\nsymptom onset")
    pep = _box(ax, 0.31, 0.75, 0.15, 0.14, "Ensitrelvir PEP\n5-day course")
    nop = _box(ax, 0.31, 0.25, 0.15, 0.14, "No pharmacologic\nprophylaxis")
    _arrow(ax, root, pep)
    _arrow(ax, root, nop)

    pep_no = _box(ax, 0.53, 0.92, 0.15, H, "No symptomatic\nCOVID-19")
    pep_sym = _box(ax, 0.53, 0.60, 0.15, H, "Symptomatic\nCOVID-19")
    nop_sym = _box(ax, 0.53, 0.40, 0.15, H, "Symptomatic\nCOVID-19")
    nop_no = _box(ax, 0.53, 0.08, 0.15, H, "No symptomatic\nCOVID-19")
    _arrow(ax, pep, pep_no, r"$1 - p_E$", 0.55)
    _arrow(ax, pep, pep_sym, r"$p_E$", 0.55)
    _arrow(ax, nop, nop_sym, r"$p_C$", 0.55)
    _arrow(ax, nop, nop_no, r"$1 - p_C$", 0.55)

    care = _box(ax, 0.80, 0.50, 0.20, 0.20,
                "Conditional care pathway\nafter symptomatic infection,\nidentical in both strategies")
    _arrow(ax, pep_sym, care)
    _arrow(ax, nop_sym, care)

    outp = _box(ax, 0.80, 0.89, 0.20, 0.15, "Outpatient course\nacute and post-acute burden")
    hosp = _box(ax, 0.80, 0.11, 0.20, 0.15, "Hospitalization\ncost, morbidity, survival or death")
    ax.annotate("", xy=(0.80, outp[1] - outp[3] / 2), xytext=(0.80, care[1] + care[3] / 2),
                arrowprops=dict(arrowstyle="-|>", linewidth=1.0, color="black"))
    ax.text(0.815, 0.705, r"$1 - p_H \times AF$", ha="left", va="center", fontsize=8, style="italic")
    ax.annotate("", xy=(0.80, hosp[1] + hosp[3] / 2), xytext=(0.80, care[1] - care[3] / 2),
                arrowprops=dict(arrowstyle="-|>", linewidth=1.0, color="black"))
    ax.text(0.815, 0.295, r"$p_H \times AF$", ha="left", va="center", fontsize=8, style="italic")

    ax.text(0.0, -0.05,
            "Ensitrelvir was assumed to affect hospitalization, death and post-acute outcomes only through "
            "prevention of symptomatic COVID-19. After a breakthrough symptomatic infection,\nconditional risks "
            "and consequences were identical between strategies. Admissions not attributed to COVID-19 "
            "(fraction 1 - AF) follow the outpatient course.",
            ha="left", va="bottom", fontsize=7.5)
    fig.savefig(OUT / "Figure1_Model_Structure.png", dpi=600, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def figure2_tornado() -> None:
    dsa = pd.read_csv(TABLES / "dsa_results.csv")
    base = pd.read_csv(TABLES / "basecase_incremental_results.csv").iloc[0]
    base_inmb = float(base["incremental_net_monetary_benefit_jpy"]) / 1000.0
    top = (
        dsa.loc[dsa["parameter_id"] != "drug_cost_pep"]
        .head(10)
        .sort_values("inmb_span_jpy", ascending=True)
        .copy()
    )
    labels = [DSA_LABELS.get(p, p) for p in top["parameter_id"]]
    low = top["inmb_min_jpy"] / 1000.0
    width = (top["inmb_max_jpy"] - top["inmb_min_jpy"]) / 1000.0

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(labels, width, left=low, color="#1f77b4", height=0.6)
    ax.axvline(0.0, linestyle="--", linewidth=1.0, color="#1f77b4", label="Cost-effectiveness threshold")
    ax.axvline(base_inmb, linestyle=":", linewidth=1.0, color="#1f77b4", label="Base-case INMB")
    ax.set_xlabel("Incremental net monetary benefit at JPY 5 million/QALY\n(JPY thousands per exposed contact)")
    ax.legend(loc="lower right", fontsize=8, frameon=True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "Figure2_One_Way_Sensitivity.png", dpi=600, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def figure3_ceac() -> None:
    ceac = pd.read_csv(TABLES / "ceac.csv")
    x = ceac["wtp_jpy_per_qaly"] / 1e6
    y = ceac["probability_cost_effective"]

    def prob_at(value: float) -> float:
        return float(ceac.loc[ceac["wtp_jpy_per_qaly"] == value, "probability_cost_effective"].iloc[0])

    p5 = prob_at(5_000_000)
    p10 = prob_at(10_000_000)

    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    ax.plot(x, y, color="#1f77b4", linewidth=1.8)
    ax.axvline(5, linestyle="--", linewidth=1.0, color="#1f77b4")
    ax.axvline(10, linestyle=":", linewidth=1.0, color="#1f77b4")
    ax.plot([5], [p5], "o", color="#1f77b4", markersize=4)
    ax.plot([10], [p10], "o", color="#1f77b4", markersize=4)
    ax.annotate(f"{p5 * 100:.2f}% at JPY 5 million/QALY", xy=(5, p5), xytext=(1.0, 0.18),
                fontsize=8, arrowprops=dict(arrowstyle="->", linewidth=0.8))
    ax.annotate(f"{p10 * 100:.2f}% at JPY 10 million/QALY", xy=(10, p10), xytext=(12.5, 0.25),
                fontsize=8, arrowprops=dict(arrowstyle="->", linewidth=0.8))
    ax.set_xlim(0, 50)
    ax.set_ylim(0, 1.02)
    ax.set_xlabel("Willingness-to-pay threshold (JPY millions per QALY)")
    ax.set_ylabel("Probability cost-effective")
    ax.grid(True, linewidth=0.4, alpha=0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "Figure3_CEAC.png", dpi=600, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def figure4_two_way_thresholds() -> None:
    a = pd.read_csv(TABLES / "two_way_threshold_control_risk.csv")
    b = pd.read_csv(TABLES / "two_way_threshold_hospital_risk.csv")
    ref = pd.read_csv(TABLES / "two_way_threshold_reference_points.csv").set_index("point")
    base = pd.read_csv(TABLES / "basecase_incremental_results.csv").iloc[0]
    params = pd.read_csv(TABLES.parent.parent / "data" / "parameters.csv").set_index("parameter_id")
    current_price = float(params.loc["drug_cost_pep", "base_value"])
    base_hosp = float(params.loc["p_hospital_given_symptomatic", "base_value"])
    order = ["Base case (months 1-12)", "Through 6 months only", "Halved", "No post-acute benefit"]
    styles = {
        "Base case (months 1-12)": ("-", 1.8),
        "Through 6 months only": ("--", 1.4),
        "Halved": ("-.", 1.4),
        "No post-acute benefit": (":", 1.4),
    }
    color = "#1f77b4"

    fig, axes = plt.subplots(1, 2, figsize=(12, 5.2))
    ax = axes[0]
    for label in order:
        g = a.loc[a["postacute_label"] == label]
        ls, lw = styles[label]
        ax.plot(g["control_symptomatic_risk"] * 100, g["drug_cost_threshold_jpy"] / 1000,
                linestyle=ls, linewidth=lw, color=color, label=label)
    ax.axhline(current_price / 1000, color="black", linewidth=1.0)
    ax.text(29.5, current_price / 1000 - 1.2, "Current acquisition cost (JPY 49,630)", fontsize=8, va="top", ha="right")
    ax.axhline(0, color="grey", linewidth=0.6)
    hr = ref.loc["high_risk_subgroup"]
    jp = ref.loc["japan_region_with_high_risk_rr"]
    ax.plot([hr["control_symptomatic_risk"] * 100], [hr["drug_cost_threshold_jpy"] / 1000], "o", color=color, markersize=5)
    ax.plot([jp["control_symptomatic_risk"] * 100], [jp["drug_cost_threshold_jpy"] / 1000], "s", color=color, markersize=5)
    ax.annotate("High-risk subgroup\n(9.9%; JPY 11,466)", xy=(hr["control_symptomatic_risk"] * 100, hr["drug_cost_threshold_jpy"] / 1000),
                xytext=(13.0, 3.0), fontsize=8, arrowprops=dict(arrowstyle="->", linewidth=0.8),
                bbox=dict(boxstyle="square,pad=0.2", facecolor="white", edgecolor="none"))
    ax.annotate("Japan region\n(23.0%; JPY 37,205)", xy=(jp["control_symptomatic_risk"] * 100, jp["drug_cost_threshold_jpy"] / 1000),
                xytext=(12.5, 43.0), fontsize=8, arrowprops=dict(arrowstyle="->", linewidth=0.8),
                bbox=dict(boxstyle="square,pad=0.2", facecolor="white", edgecolor="none"))
    ax.set_xlim(0, 30)
    ax.set_ylim(-6, 56)
    ax.set_xlabel("Symptomatic COVID-19 risk without PEP (%)")
    ax.set_ylabel("Value-based drug acquisition cost threshold\n(JPY thousands per course)")
    ax.set_title("A. Baseline attack rate (relative risk 0.24)", loc="left", fontsize=10)
    ax.legend(title="Post-acute QALY loss", fontsize=8, title_fontsize=8, loc="upper left", frameon=True)
    ax.grid(True, linewidth=0.4, alpha=0.5)

    ax = axes[1]
    for label in order:
        g = b.loc[b["postacute_label"] == label]
        ls, lw = styles[label]
        ax.plot(g["p_hospital_given_symptomatic"] * 100, g["drug_cost_threshold_jpy"] / 1000,
                linestyle=ls, linewidth=lw, color=color, label=label)
    ax.axhline(current_price / 1000, color="black", linewidth=1.0)
    ax.text(0.3, current_price / 1000 + 2.0, "Current acquisition cost (JPY 49,630)", fontsize=8, va="bottom")
    ax.axhline(0, color="grey", linewidth=0.6)
    ax.axvline(base_hosp * 100, color="grey", linestyle="--", linewidth=0.8)
    ax.text(base_hosp * 100 + 0.3, 90, "Base case\n(0.785%)", fontsize=8, va="top")
    ax.set_xlim(0, 20)
    ax.set_ylim(-6, 100)
    ax.set_xlabel("Hospitalization risk after symptomatic COVID-19 (%)")
    ax.set_ylabel("Value-based drug acquisition cost threshold\n(JPY thousands per course)")
    ax.set_title("B. Hospitalization risk (high-risk subgroup attack rates)", loc="left", fontsize=10)
    ax.grid(True, linewidth=0.4, alpha=0.5)
    for a_ in axes:
        a_.spines["top"].set_visible(False)
        a_.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "Figure4_Price_Thresholds.png", dpi=600, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def run() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    figure1_model_structure()
    figure2_tornado()
    figure3_ceac()
    figure4_two_way_thresholds()
    print(f"Wrote publication figures to {OUT}")


if __name__ == "__main__":
    run()
