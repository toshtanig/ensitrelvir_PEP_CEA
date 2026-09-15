# Evidence update and extrapolation register, 25 August 2026

## Scope

Version 0.2.0 replaces the major publication-critical placeholders in the ensitrelvir post-exposure prophylaxis cost-effectiveness model with Japanese empirical data or explicit, auditable structural assumptions. The primary analysis remains a public-healthcare-payer analysis in high-risk household contacts.

## Replacements

| Domain | v0.1 treatment | v0.2 base-case treatment | Reproducible derivation |
|---|---|---|---|
| PEP delivery | JPY 680 transferred from an antiviral treatment CEA | JPY 8,100 FY2026 face-to-face, antigen-test, prescription, and representative pharmacy pathway | `pep_microcost_japan_2026.csv`; `audit_derived_inputs.py` |
| Hospitalization | 1.77% from a prior treatment CEA | 0.785% 28-day all-cause hospitalization in untreated Japanese high-risk outpatients | E17, with 0%, 50%, and 100% COVID-attribution scenarios |
| In-hospital death | Multiple old ward/ICU branches | 12% conditional mortality from a Japanese cohort through January 2024 | E12 |
| Hospital cost | Per-day pathway model | JPY 1,304,431 per admission, with mild and severe medians as broad bounds | E08 |
| Acute utility | 0.056 transferred decrement | 0.258 control-adjusted acute decrement from a Japanese Omicron cohort | E14 |
| Post-acute utility | PCC incidence and assumed duration | Directly integrated attributable QALY loss 0.03225 from months 1 to 12 | `postacute_utility_profile_japan_2025.csv`; E14 |
| QALYs lost per death | 14.5 placeholder | 6.46949 discounted QALYs from age 82, 54% male proxy | life table and utility integration; E11, E12, E13, E19 |
| Post-acute direct cost | JPY 0 placeholder | JPY 0 evidence-gap base case plus 50k, 100k, and 200k scenarios | A07 and A09 |

## Key extrapolation equations

### Symptomatic cases

The randomized trial provides arm-specific symptomatic risks. All downstream events are mediated through symptomatic COVID-19:

`P(symptomatic, arm) = trial arm risk`.

### Hospitalization and causal attribution

`P(COVID-attributable hospitalization, arm) = P(symptomatic, arm) × 0.00785 × attributable fraction`.

The source endpoint is all-cause hospitalization. The primary analysis uses an attributable fraction of 1.0, while structural analyses use 0.5 and 0.0.

### Acute death

`P(acute death, arm) = P(COVID-attributable hospitalization, arm) × 0.12`.

No direct prophylaxis effect on severity conditional on breakthrough symptomatic COVID-19 is assumed.

### Remaining QALY after acute death

For each age-sex stratum, annual survival is derived from the 2025 Japanese abridged life table, multiplied by age-sex population utility and discounted at 2%. The primary proxy begins at age 82 and weights male and female strata 0.54 and 0.46. Sensitivity scenarios begin at ages 75 and 85.

### Post-acute QALY loss

The model integrates the control-minus-COVID EQ-5D-5L difference over months 1 to 3, 3 to 6, and 6 to 12:

`0.069 × 2/12 + 0.033 × 3/12 + 0.025 × 6/12 = 0.03225 QALY`.

This profile is applied to surviving symptomatic cases. It is not labeled as a diagnosed PCC event count.

## Residual evidence gaps

1. The hospitalization source reports all-cause admissions and underrepresents older adults.
2. The hospitalization and mortality parameters come from different cohorts.
3. The age-sex distribution of COVID-19 decedents among eligible PEP contacts is unavailable; hospitalized-case demographics are used as a proxy.
4. The post-acute utility cohort was younger than the modeled high-risk population.
5. No sufficiently transportable Japanese matched incremental direct medical cost estimate for post-acute illness was identified.
6. The trial observed no COVID-19-related hospitalization or death, so severe-outcome benefits are modeled extrapolations.

These limitations are encoded in `extrapolation_register.csv` and prespecified scenario analyses rather than hidden in narrative assumptions.
