# Data management

This directory contains the version-controlled source inputs for the model. Generated results are never written here.

## Canonical files

| File | Role |
|---|---|
| `parameters.csv` | One row per numeric model parameter, including base value, DSA range, PSA distribution, units, provenance, price year, and replacement notes. |
| `trial_event_counts.csv` | Randomized arm event counts, denominators, and reported absolute risks. |
| `trial_effect_estimates.csv` | Published comparative effect estimates and 95% confidence intervals used in DSA and PSA. |
| `scenarios.csv` | Named population and structural scenarios. |
| `scenario_overrides.csv` | Long-format changes from the base parameter set. |
| `evidence_register.csv` | Bibliographic provenance and explicitly labeled internal assumptions. |
| `input_traceability_targets.csv` | Source-transfer and face-validity targets. Several values are the same sources used for model inputs and therefore are not independent predictive validation. |

CSV files are encoded as UTF-8 with a byte-order mark so that Japanese text opens reliably in common spreadsheet software. Python code treats the CSV files, not generated Markdown tables, as the source of truth.

## Referential integrity

Every empirical or assumption-based input has a stable `source_id` that must resolve to `evidence_register.csv`. `scripts/validate_inputs.py` checks source keys, numeric bounds, trial count reconciliation, scenario overrides, and executable model scenarios. The continuous-integration workflow runs these checks on every push and pull request.

## Efficacy uncertainty

For the primary PSA, the no-PEP symptomatic risk is sampled from a Jeffreys beta posterior based on the randomized control count. The risk ratio is sampled from a log-normal distribution parameterized from the published estimate and 95% confidence interval in `trial_effect_estimates.csv`. The PEP risk is the product of those draws. The unavailable covariance between absolute risk and relative effect is approximated as zero and is documented as a limitation.

## Editing and release rules

1. Do not overwrite a released parameter set. Create a new tagged version.
2. Keep units explicit and avoid embedding formulas in CSV cells.
3. Add a source or internal-assumption row before assigning a new `source_id`.
4. Record the price year for every cost input and document any indexation.
5. Run `python scripts/validate_inputs.py`, `pytest`, and `python scripts/run_all.py` before release.
6. Regenerate `docs/basecase_parameter_table.md`, `docs/trial_effect_table.md` from scripts rather than editing generated files manually. Do not calculate checksums for mutable working files; an optional archive-level checksum may be generated only after the final release ZIP has been frozen.

## Evidence-update and review-response files

- `extrapolation_register.csv`: parameter-level source-to-target transformations, uncertainty handling, and residual bias.
- `literature_search_log.csv`: reproducible search topics, query concepts, selected sources, and conclusions as of 2026-08-25.
- `subgroup_hospitalization_extrapolations.csv`: observed and transformed hospitalization probabilities for age, malignancy, renal disease, immunosuppression, and immunocompromised scenarios.
- `pep_microcost_japan_2026.csv`: itemized FY2026 medical and pharmacy reimbursement components.
- `postacute_utility_profile_japan_2025.csv`: interval-specific Japanese control-adjusted EQ-5D-5L losses from months 1 to 12.
- `acute_death_cohort_japan_2025.csv`, `life_table_japan_2025.csv`, and `utility_norms_japan_eq5d5l_2021.csv`: auditable remaining-QALY calibration inputs.

- v0.3.0 adds conservative efficacy, post-acute, breakthrough-treatment, and static downstream-case scenarios.
