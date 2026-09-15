from __future__ import annotations

from _bootstrap import ROOT
from ensitrelvir_pep_cea.io import load_parameter_frame, load_trial_effect_frame


def _number(value: float) -> str:
    return f"{float(value):.8g}"


def _cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def run() -> None:
    parameters = load_parameter_frame()
    parameter_lines = [
        "# Base-case parameter table",
        "",
        "This table is generated from `data/parameters.csv`. The CSV is the analysis source of truth.",
        "",
        "| Parameter ID | Japanese label | Base | Low | High | Unit | Distribution | PSA | DSA | Source | Grade | Notes |",
        "|---|---|---:|---:|---:|---|---|:---:|:---:|---|:---:|---|",
    ]
    for row in parameters.itertuples(index=False):
        parameter_lines.append(
            "| "
            + " | ".join(
                [
                    f"`{_cell(row.parameter_id)}`",
                    _cell(row.label_ja),
                    _number(row.base_value),
                    _number(row.lower_value),
                    _number(row.upper_value),
                    _cell(row.unit),
                    _cell(row.distribution),
                    _cell(row.include_in_psa),
                    _cell(row.include_in_dsa),
                    _cell(row.source_id),
                    _cell(row.evidence_grade),
                    _cell(row.notes),
                ]
            )
            + " |"
        )
    (ROOT / "docs" / "basecase_parameter_table.md").write_text(
        "\n".join(parameter_lines) + "\n",
        encoding="utf-8",
    )

    effects = load_trial_effect_frame()
    effect_lines = [
        "# Trial effect estimates",
        "",
        "This table is generated from `data/trial_effect_estimates.csv`. The CSV is the analysis source of truth for comparative efficacy uncertainty.",
        "",
        "| Population | Outcome | Measure | Estimate | 95% CI | Analysis method | Source | Notes |",
        "|---|---|---|---:|---:|---|---|---|",
    ]
    for row in effects.itertuples(index=False):
        effect_lines.append(
            "| "
            + " | ".join(
                [
                    _cell(row.population),
                    _cell(row.outcome),
                    _cell(row.effect_measure),
                    _number(row.estimate),
                    f"{_number(row.lower_95)} to {_number(row.upper_95)}",
                    _cell(row.analysis_method),
                    _cell(row.source_id),
                    _cell(row.notes),
                ]
            )
            + " |"
        )
    (ROOT / "docs" / "trial_effect_table.md").write_text(
        "\n".join(effect_lines) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    run()
