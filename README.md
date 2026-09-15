# Ensitrelvir post-exposure prophylaxis cost-effectiveness model for Japan

Version **0.3.2**

This repository contains the fully reproducible Python model for a cost-utility analysis of ensitrelvir as post-exposure prophylaxis for COVID-19 among high-risk household contacts in Japan. The base-case analysis adopts the Japanese public healthcare payer perspective.

> **Research-use notice:** This repository supports a health-economic manuscript and planned medRxiv preprint. It is not clinical guidance.

## Associated manuscript

- **Article title:** Cost-Effectiveness of Ensitrelvir for COVID-19 Post-Exposure Prophylaxis Among High-Risk Household Contacts in Japan: A Model-Based Cost-Utility Analysis
- **Target journal:** Applied Health Economics and Health Policy
- **Authors:** `Toshibumi Taniguchi, Misuzu Yahaba, Hiroshi Yoshikawa, Hidetoshi Igari, Daisuke Sato`
- **Affiliations:** `Department of Infectious Diseases, Chiba University Hospital, Chiba, Japan; Hospital and Health Administration, Fujita Health University, Toyoake, Japan`
- **Corresponding author:** `tosh-tanig@chiba-u.jp`

Complete these fields before the public release so that the repository archive also satisfies the journal's supplementary-information identification requirements.

## Research question and causal structure

The model compares a 5-day course of ensitrelvir with no pharmacologic post-exposure prophylaxis among household contacts with at least one risk factor for severe COVID-19. SCORPIO-PEP supplies randomized symptomatic COVID-19 risks through day 10. Because the trial observed no COVID-19-related hospitalization or death, ensitrelvir is assumed to affect hospitalization, mortality, and post-acute health only by preventing symptomatic disease.

## Base-case results

| Outcome | Result |
|---|---:|
| Incremental cost | JPY 54,945/contact |
| Incremental QALYs | 0.003267/contact |
| ICER | JPY 16.82 million/QALY |
| INMB at JPY 5 million/QALY | JPY -38,609/contact |
| Probability cost-effective at JPY 5 million/QALY | 0.00% |
| Probability cost-effective at JPY 10 million/QALY | 2.28% |
| Acquisition-cost threshold | JPY 11,021/course |

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
- Drug acquisition and delivery use 2026 values. Transferred outpatient and inpatient costs retain 2023 and 2021 source-year nominal values.
- The FY2026 two-point outpatient inflation add-on, equivalent to JPY 20, is omitted because its effect is immaterial. Facility-dependent wage add-ons are separately excluded.

## Public release workflow

Before publishing the final tagged release:

1. Edit `release_metadata.yml` with the real authors, affiliations, ORCID iDs, GitHub URLs, and reserved Zenodo DOI.
2. Run `python scripts/finalize_release_metadata.py --metadata release_metadata.yml`.
3. Run `python scripts/check_release_readiness.py`.
4. Commit the finalized files and create tag `v0.3.2`.
5. Run `python scripts/build_release_archive.py` and upload the generated archive to the reserved Zenodo record.

Detailed instructions are in `ZENODO_RELEASE_WORKFLOW.md`.

Current placeholders:

- GitHub repository: `https://github.com/toshtanig/ensitrelvir_PEP_CEA`
- GitHub release: `https://github.com/toshtanig/ensitrelvir_PEP_CEA/releases/tag/v0.3.2`
- Zenodo DOI: `https://doi.org/10.5281/zenodo.22107356`
- medRxiv preprint: `Not yet posted`

## Citation

GitHub reads `CITATION.cff`; Zenodo reads `.zenodo.json` when present. Both are finalized from `release_metadata.yml`.

## License

Original source code and documentation are released under the [MIT License](LICENSE). Source-derived parameter values and bibliographic materials remain subject to the original source terms. See `THIRD_PARTY_NOTICES.md`.

## Contributing

See `CONTRIBUTING.md`. Please report reproducible numerical or methodological issues without including private health information.
