# Changelog

## 0.3.3 - 2026-10-20

- One-way sensitivity analysis of the QALY discount rate now recalculates the discounted remaining QALYs per acute death from the life table, so that the rate change propagates to results (previously the derived input was held fixed and the DSA row showed no effect). A regression test was added.
- Hospitalization cost base value changed from the reported median (JPY 1,304,431) to the arithmetic mean derived from the reported total cost (JPY 678,679,460 / 330 = JPY 2,056,604), which is the appropriate input for an expected-value model. Deterministic bounds are unchanged.
- Added exploratory Japan-region scenarios using the SCORPIO-PEP Japan geographic subgroup (EMA assessment report Table 71): observed arm risks; Japan-region placebo risk with the high-risk subgroup RR 0.24; and Japan-region placebo risk with the overall RR 0.33. The Japan-by-high-risk cross-classification was not reported.
- Added two exploratory joint scenarios combining the Japan-region attack rates with a higher hospitalization risk (age 65 years or older; immunocompromised multiplier 2.60).
- Clarified that the hospitalization cost source expressed 2021 cohort costs at 2022 price levels (price_year updated to 2022).
- Relabeled the hypothetical 10% hospitalization scenario to state that it also recalibrates remaining QALYs per death to the age-85 proxy.
- Marked superseded v0.2 evidence-register notes (E09, A03) as historical.
- Added a two-way threshold analysis (`scripts/run_two_way_thresholds.py`) giving the value-based drug acquisition cost as a function of the baseline attack rate and of the hospitalization risk, for each post-acute assumption (Figure 4).
- Added a publication figure script (`scripts/make_publication_figures.py`) that draws the model structure (Figure 1, with the outpatient branch labeled 1 - pH x AF), the tornado diagram, and the CEAC from the generated outputs.
- Updated release metadata (author affiliations and ORCID iDs; target journal).

## 0.3.2 - 2026-08-26

- Prepared the model for public GitHub and Zenodo release.
- Clarified the FY2026 two-point outpatient inflation add-on and facility-dependent wage add-ons.
- Clarified omitted consultation, testing, and dispensing costs in the breakthrough-treatment scenario.
- Clarified that downstream-case scenarios use high-risk conditional outcomes and are upper-bound static calculations.
- Clarified that the 10% conditional hospitalization scenario is hypothetical.
- Updated documentation and release metadata without changing model equations, input values, or numerical results.
- Removed checksum generation from the routine analysis workflow and made release-archive SHA-256 sidecars optional.
- Removed the file-level checksum manifest from the public release archive to avoid treating checksums as mutable working identifiers.

## 0.3.0 - 2026-08-26

- Corrected the characterization of the Japanese post-acute utility source.
- Added conservative post-acute, overall-trial efficacy, breakthrough-treatment, and static downstream-case scenarios.
- Reclassified circular comparisons as input traceability and face-validity checks.
- Expanded automated testing to 15 tests.

## 0.2.0 - 2026-08-25

- Replaced major publication-critical placeholders with Japanese empirical data or explicit assumptions.
- Added hospitalization attribution, contemporary inpatient mortality, Japanese costs, utility, life-table QALYs, subgroup scenarios, and evidence registers.

## 0.1.0 - 2026-08-25

- Initial reproducible model.
