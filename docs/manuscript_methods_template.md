# Manuscript methods template, v0.3.0

## Study design and perspective

We developed a decision-analytic cost-utility model comparing ensitrelvir post-exposure prophylaxis with no pharmacologic prophylaxis among household contacts with at least one risk factor for severe COVID-19 in Japan. The analysis adopted the Japanese public healthcare payer perspective. Costs were expressed in Japanese yen and health outcomes in quality-adjusted life-years. A reference value of JPY 5 million per QALY was used for net monetary benefit analyses. Future QALYs were discounted at 2% annually.

## Efficacy

Arm-specific risks of symptomatic COVID-19 through day 10 were obtained from the prespecified high-risk subgroup of SCORPIO-PEP, in which 9 of 382 ensitrelvir recipients and 37 of 374 placebo recipients developed symptomatic COVID-19. Because no COVID-19-related hospitalization or death occurred in the trial, ensitrelvir was assumed to affect downstream outcomes only through prevention of symptomatic COVID-19. Conditional hospitalization, mortality, acute morbidity, and post-acute burden were assumed equal between strategies after a breakthrough symptomatic infection.

## Model structure

For each strategy, symptomatic COVID-19 could be managed outside hospital or result in COVID-19-attributable hospitalization. The source hospitalization input was 28-day all-cause hospitalization among untreated Japanese high-risk outpatients. A separate attributable-fraction parameter mapped that endpoint to hospitalizations assigned COVID-19 cost and mortality. Death was restricted to the hospitalized pathway. Surviving symptomatic cases incurred a one-year post-acute QALY loss integrated directly from a Japanese retrospective online recall EQ-5D-5L survey with test-negative controls.

## Clinical inputs

The base hospitalization risk was 0.785%. The base attribution fraction was 1.0, with 0.5 and 0.0 structural analyses. In-hospital mortality was 12%, based on a Japanese hospital cohort through January 2024. Remaining QALYs lost per acute death were calculated by integrating age-sex survival from the 2025 Japanese abridged life table and Japanese EQ-5D-5L population norms, using an age-82, 54% male proxy cohort and 2% annual discounting.

Acute utility decrement was estimated as the difference between symptomatic test-negative controls and COVID-19 patients in a Japanese Omicron-period cohort. Post-acute loss was calculated as the area between the control and COVID-19 utility profiles from months 1 to 12, yielding 0.03225 QALYs per surviving symptomatic case.

## Costs

The seven-tablet prophylaxis course cost JPY 49,630. Delivery cost was microcosted from the FY2026 Japanese medical and pharmacy fee schedules. The base pathway, totaling JPY 8,100, included a face-to-face initial consultation, qualitative antigen testing, specimen collection, test interpretation, prescription, and representative pharmacy fees. No-test and telemedicine pathways were evaluated in scenarios.

Outpatient cost was taken from a Japanese COVID-19 economic model. Hospitalization cost was JPY 1,304,431 per admission, based on the median in a Japanese hospital cost study. Because no sufficiently transportable Japanese matched incremental post-acute cost estimate was identified, the payer base case assigned zero post-acute direct medical cost and evaluated JPY 50,000, 100,000, and 200,000 per surviving symptomatic case in scenarios.

## Analyses

We calculated expected costs, QALY losses, symptomatic cases, observed source-endpoint hospitalizations, COVID-19-attributable hospitalizations, deaths, incremental cost, incremental QALYs, ICERs, incremental net monetary benefit, and number needed to treat. Outcomes were reported per exposed contact and per 1,000 contacts.

One-way sensitivity analysis used prespecified parameter ranges and ranked inputs by incremental net monetary benefit. In probabilistic sensitivity analysis, untreated symptomatic risk was sampled from a Jeffreys beta posterior, and the published relative risk was sampled from a log-normal distribution derived from its 95% confidence interval. Their unavailable covariance was approximated as zero. We ran 10,000 simulations using seed 20260825.

Structural analyses varied hospitalization attribution, excluded mortality or post-acute burden, changed the PEP delivery pathway, calibrated mortality QALYs at ages 75 and 85, varied post-acute costs, and examined older, immunocompromised, malignancy, renal disease, immunosuppressive drug, and B-cell-depleting therapy scenarios.

## Validation and reproducibility

All parameters, evidence, extrapolations, and scenarios were stored in versioned CSV files. Automated validation checked parameter ranges, trial arithmetic, source foreign keys, and scenario execution. A separate audit recalculated the delivery microcost, post-acute QALY integral, and mortality-QALY value from source tables. Unit tests assessed event arithmetic, structural attribution, intervention cost, life-table calculations, and probabilistic reproducibility. Code, data, generated outputs, environment information, and file hashes were archived with the analysis release.
