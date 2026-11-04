# Ensitrelvir post-exposure prophylaxis cost-effectiveness model for Japan

Version **0.3.3**

This repository contains the fully reproducible Python model for a cost-utility analysis of ensitrelvir as post-exposure prophylaxis for COVID-19 among high-risk household contacts in Japan. The base-case analysis adopts the Japanese public healthcare payer perspective.

> **Research-use notice:** This repository supports a health-economic manuscript and its medRxiv preprint. It is not clinical guidance.

## Associated manuscript

- **Article title:** Cost-Effectiveness of Ensitrelvir for COVID-19 Post-Exposure Prophylaxis Among High-Risk Household Contacts in Japan: A Model-Based Cost-Utility Analysis
- **Target journal:** Journal of Medical Virology
- **Authors:** `Toshibumi Taniguchi, Misuzu Yahaba, Hiroshi Yoshikawa, Hidetoshi Igari, Daisuke Sato`
- **Affiliations:** `Department of Infectious Diseases, Chiba University Hospital, Chiba, Japan; Kitasato University Graduate School of Medical Sciences, Sagamihara, Japan`
- **Corresponding author:** `tosh-tanig@chiba-u.jp`


## Research question and causal structure

The model compares a 5-day course of ensitrelvir with no pharmacologic post-exposure prophylaxis among household contacts with at least one risk factor for severe COVID-19. SCORPIO-PEP supplies randomized symptomatic COVID-19 risks through day 10. Because the trial observed no COVID-19-related hospitalization or death, ensitrelvir is assumed to affect hospitalization, mortality, and post-acute health only by preventing symptomatic disease.

## Base-case results

| Outcome | Result |
|---|---:|
| Incremental cost | JPY 54,500/contact |
| Incremental QALYs | 0.003267/contact |
| ICER | JPY 16.68 million/QALY |
| INMB at JPY 5 million/QALY | JPY -38,164/contact |
| Probability cost-effective at JPY 5 million/QALY | 0% (0 of 10,000) |
| Probability cost-effective at JPY 7.5 million/QALY | 0.04% |
| Probability cost-effective at JPY 10 million/QALY | 2.40% |
| Acquisition-cost threshold | JPY 11,466/course |

These values are those in `outputs/tables/` of release v0.3.3. The README packaged in the v0.3.3 archive (GitHub release and Zenodo) still showed an outdated results table from an earlier development run (incremental cost JPY 54,945, ICER JPY 16.82 million/QALY, threshold JPY 11,021); this README was corrected on the main branch on 4 November 2026. Model code, inputs and outputs are unchanged.

## Additional analyses reported in the journal submission

Code and results for the additional robustness analyses of the exploratory immunocompromised joint scenario (Japan-region placebo risk, relative risk 0.24, hospitalization risk 0.00785 x 2.60) are provided in Supporting Information S2 of the manuscript (sheets `Joint_Robustness` and `Joint_Robustness_Code`). These analyses use the unchanged version 0.3.3 model. In their probabilistic analysis, the conditional hospitalization risk is sampled from its base-case PERT distribution and multiplied by the fixed multiplier 2.60 (57.2% of 10,000 simulations cost-effective at JPY 5 million/QALY). The v0.3.3 sampler keeps the base-case PERT bounds when only a scenario mode is supplied, so a scenario value outside those bounds would be clipped; the S2 script therefore scales all three PERT values and checks that every sampled scenario value lies within its bounds.

## Historical documents

`docs/analysis_plan.md` and `docs/reporting_checklist.md` are kept as written during model development. Where they differ from this README, this README and `outputs/tables/` take precedence. In particular, the CEAC probabilities listed in the checklist (0%, 0.02% and 2.28%) are from an earlier development run; the v0.3.3 values are 0%, 0.04% and 2.40% at JPY 5, 7.5 and 10 million/QALY. The inpatient cost is the arithmetic mean for a 2021 cohort expressed at 2022 reimbursement levels, not a 2021 price-year value as the analysis plan states.

## Repository structure

```text
config/                 Base-case configuration
data/                   Parameters, source registers, and scenario definitions
docs/                   Model specification, analysis plan, and reporting notes
outputs/                Versioned tables, figures, PSA draws, and analysis records
scripts/                Analysis, validation, audit, and release utilities
src/                    Python package
tests/                  Unit and integrity tests
.github/workflows/      Continuous integration
```

## Reproduce the analysis

Python 3.10 or later is required.

```bash
python -m venv .venv
source .venv/bin/activate       # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python scripts/run_all.py
python -m pytest -q
```

The complete workflow performs input validation, three independent derived-input audits, deterministic and probabilistic analyses, threshold analysis, traceability checks, manuscript-support outputs, and release-ready reproducibility records. The primary PSA uses 10,000 simulations with seed `20260825`.

## Key interpretation points

- The hospitalization endpoint transferred from Japanese claims data is all-cause hospitalization; an explicit attribution fraction maps it to COVID-19 costs and mortality.
- The post-acute utility profile comes from a retrospective online recall survey with a test-negative comparison group.
- The 10% conditional hospitalization scenario is hypothetical and was not observed in the Japanese sources used by the model.
- Static downstream-case analyses assign the same high-risk conditional outcomes to downstream cases. They are upper-bound calculations, not a dynamic transmission model.
- Drug acquisition and delivery use 2026 values. Transferred outpatient costs retain 2023 source-year values; the inpatient cost is the arithmetic mean for a 2021 cohort expressed at 2022 reimbursement levels (not further repriced to 2026).
- The FY2026 two-point outpatient inflation add-on, equivalent to JPY 20, is omitted because its effect is immaterial. Facility-dependent wage add-ons are separately excluded.

## Public release workflow

Before publishing the final tagged release:

1. Edit `release_metadata.yml` with the real authors, affiliations, ORCID iDs, GitHub URLs, and reserved Zenodo DOI.
2. Run `python scripts/finalize_release_metadata.py --metadata release_metadata.yml`.
3. Run `python scripts/check_release_readiness.py`.
4. Commit the finalized files and create tag `v0.3.3`.
5. Run `python scripts/build_release_archive.py` and upload the generated archive to the reserved Zenodo record.

Detailed instructions are in `ZENODO_RELEASE_WORKFLOW.md`.

Release identifiers:

- GitHub repository: `https://github.com/toshtanig/ensitrelvir_PEP_CEA`
- GitHub release: `https://github.com/toshtanig/ensitrelvir_PEP_CEA/releases/tag/v0.3.3`
- Zenodo DOI (this version, v0.3.3): `https://doi.org/10.5281/zenodo.23494164`
- Previous version v0.3.2 (cited by medRxiv version 1): `https://doi.org/10.5281/zenodo.22107356`
- medRxiv preprint: `https://doi.org/10.64898/2026.09.15.26361876`

## Citation

GitHub reads `CITATION.cff`; Zenodo reads `.zenodo.json` when present. Both are finalized from `release_metadata.yml`.

## License

Original source code and documentation are released under the [MIT License](LICENSE). Source-derived parameter values and bibliographic materials remain subject to the original source terms. See `THIRD_PARTY_NOTICES.md`.

## Contributing

See `CONTRIBUTING.md`. Please report reproducible numerical or methodological issues without including private health information.
