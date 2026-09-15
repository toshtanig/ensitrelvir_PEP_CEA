# Targeted evidence update strategy, 25 August 2026

## Objective

The search was designed to replace publication-critical placeholders in a Japanese cost-effectiveness model of ensitrelvir post-exposure prophylaxis. It was a targeted model-input review, not a systematic review of all ensitrelvir evidence.

## Sources searched

- PubMed and PubMed Central
- Primary publisher pages for included peer-reviewed studies
- Pharmaceuticals and Medical Devices Agency
- Ministry of Health, Labour and Welfare
- Center for Outcomes Research and Economic Evaluation for Health
- Official Japanese life-table and reimbursement resources

## Search domains

1. SCORPIO-PEP efficacy, safety, subgroup outcomes, and product-label implementation requirements
2. Japanese high-risk outpatient hospitalization after Omicron-period COVID-19
3. Contemporary Japanese inpatient mortality, length of stay, intensive care, and ventilation
4. Japanese acute and post-acute EQ-5D-5L utility
5. Japanese COVID-19 outpatient and inpatient direct medical cost
6. Japanese post-acute incremental healthcare utilization and cost
7. Japanese life tables and age-sex population utility norms
8. FY2026 consultation, testing, prescribing, and dispensing reimbursement
9. Immunocompromised and disease-specific hospitalization multipliers

The machine-readable topic queries and inclusion conclusions are stored in `data/literature_search_log.csv`.

## Inclusion hierarchy

For each input, the preferred hierarchy was:

1. Japanese official sources or Japanese empirical studies in the target period
2. Japanese studies with imperfect population or outcome transferability
3. Previously published Japanese economic-model inputs
4. Explicit internal structural assumptions when no empirical estimate was sufficiently transportable

Randomized ensitrelvir evidence was used only for prophylactic efficacy and safety. Treatment studies were not interpreted as randomized prophylaxis effects.

## Selection criteria

Studies were prioritized when they:

- included Japanese patients or official Japanese prices and tariffs;
- represented the Omicron era or the latest available period;
- reported absolute risks, costs, utilities, or age-sex data usable in a model;
- clearly defined denominator, follow-up, and outcome;
- provided enough information to reproduce the transformation.

Older studies were retained for costs or utilities when no contemporary equivalent was found. Every such use is labeled for transportability.

## Key exclusions

- non-Japanese estimates when a Japanese alternative was available;
- pre-Omicron severity risks for the publication base case;
- antiviral treatment effect estimates used as direct PEP efficacy;
- uncontrolled symptom prevalence used as attributable post-acute QALY loss when a test-negative controlled Japanese study was available;
- illustrative post-acute cost estimates without a Japanese matched comparator;
- hospitalization ratios converted to absolute risks without an explicit transformation and scenario label.

## Evidence gaps after the search

No sufficiently transportable Japanese estimate was identified for:

- the fraction of 28-day all-cause hospitalizations causally attributable to COVID-19 in the selected outpatient source;
- age-sex distribution of acute COVID-19 deaths among eligible PEP contacts;
- matched incremental post-acute direct medical cost per symptomatic case;
- covariance between untreated absolute risk and the household-cluster-adjusted randomized relative effect.

These gaps are represented by structural scenarios, transparent proxy calibration, or fixed evidence-gap parameters. They are not presented as observed Japanese values.

## Data extraction and verification

Each selected source was entered into `data/evidence_register.csv`. Each source-to-target transformation was entered into `data/extrapolation_register.csv`. Derived numerical values were recalculated by code and compared with registered parameters in `outputs/tables/derived_input_audit.csv`. Input foreign keys and numerical ranges were checked by `scripts/validate_inputs.py`.
