# Parameter and evidence data dictionary

## `data/parameters.csv`

Each row is one model input. The file is UTF-8 with a byte-order mark to support Japanese text in common spreadsheet software.

| Column | Meaning |
|---|---|
| `parameter_id` | Stable machine-readable identifier used by Python. Do not change after analysis lock. |
| `category` | Analysis, intervention cost, acute clinical, utility, healthcare cost, PCC, or safety. |
| `label_ja`, `label_en` | Human-readable labels. |
| `base_value` | Deterministic base-case value. |
| `lower_value`, `upper_value` | Predeclared deterministic sensitivity range. |
| `unit` | Measurement unit and denominator. |
| `distribution` | `fixed`, `pert`, `gamma_cv`, `lognormal_cv`, or `uniform`. |
| `distribution_parameter` | Coefficient of variation when relevant. |
| `include_in_psa`, `include_in_dsa` | Analysis inclusion flags. |
| `source_id` | Foreign key to `data/evidence_register.csv`. |
| `source_type` | Official price, randomized trial, Japanese model, Japanese EHR cost, structural assumption, or evidence gap. |
| `evidence_grade` | Internal provenance grade defined below. |
| `price_year` | Cost year where applicable. |
| `notes` | Transportability, limitations, and replacement instructions. |

## Internal provenance grade

This grade describes fitness for the current model and is not a formal risk-of-bias rating.

- `A`: Direct official Japanese input or randomized efficacy input suitable for the modeled decision problem.
- `B`: Japanese empirical input with reasonable but imperfect transferability.
- `C`: External model input, indirect clinical estimate, or parameter requiring important transportability assumptions.
- `D`: Structural assumption, calibration placeholder, or unresolved evidence gap.

## Other data files

- `trial_event_counts.csv`: randomized events, denominators, and reported arm risks. Exact event counts are used for the symptomatic endpoint. Effective beta counts are used only for exploratory outcomes when exact counts are unavailable.
- `trial_effect_estimates.csv`: published comparative effect estimates, 95% confidence intervals, analysis method, provenance, and limitations. The primary PSA samples the risk ratio from this file.
- `scenarios.csv`: named structural and population scenarios.
- `scenario_overrides.csv`: long-format parameter overrides with rationale.
- `evidence_register.csv`: one row per empirical source or explicitly labeled internal assumption, with citation, URL where applicable, role, access date, and limitations. Every `source_id` in model input files must resolve here.
- `external_validation_targets.csv`: empirical targets used only for face-validity checks.

## Analysis-lock recommendations

Before a manuscript is submitted, freeze a tagged release and record the Git commit hash, analysis date, Python version, package lock file, target population definition, all price-year conversions, and any parameter changes after expert validation. Do not overwrite a locked parameter file. Create a new version and document the change in the release notes.
