# Analysis plan: ensitrelvir post-exposure prophylaxis, v0.3.2

## Objective

Compare ensitrelvir post-exposure prophylaxis with no pharmacologic prophylaxis among high-risk household contacts in Japan from the public healthcare payer perspective. Report costs, QALYs, ICERs, incremental net monetary benefit, and events prevented.

## Base case

The model uses randomized symptomatic COVID-19 risks from the high-risk SCORPIO-PEP subgroup. Ensitrelvir changes only the probability of symptomatic disease. Conditional hospitalization, mortality, acute utility, and post-acute utility are equal between arms after a breakthrough symptomatic infection.

The conditional hospitalization probability is 0.785%, based on 28-day all-cause hospitalization among untreated Japanese high-risk outpatients. The base-case COVID-19 attribution fraction is 1.0, with mandatory analyses at 0.5 and 0.0. In-hospital mortality is 12%. Remaining QALYs lost per death are calibrated from a proxy cohort aged 82 years with 54% men. Surviving symptomatic cases receive an integrated one-year post-acute loss of 0.03225 QALYs.

## Costs

The modeled acquisition cost is JPY 49,630/course and the base delivery cost is JPY 8,100/contact. The FY2026 two-point outpatient inflation add-on, equivalent to JPY 20, is omitted because its effect is immaterial. Facility-dependent wage add-ons are also excluded. Transferred outpatient and inpatient costs retain their 2023 and 2021 source-year nominal values.

## Sensitivity analyses

Required analyses include overall-trial efficacy, no mortality benefit, reduced or excluded post-acute utility, hospitalization attribution, alternative delivery pathways, post-acute costs, age and immunocompromised risk scenarios, 50% post-diagnosis treatment uptake, static downstream-case bounds, and threshold analyses. The 10% conditional hospitalization scenario is hypothetical. Downstream cases receive the same high-risk conditional outcomes and therefore represent an upper bound rather than a dynamic transmission estimate.

## Probabilistic analysis

Run 10,000 simulations with seed `20260825`. Sample untreated symptomatic risk from a Jeffreys beta posterior and the published relative risk from a log-normal distribution. Treat their unknown covariance as zero and report this as a limitation.

## Verification and release

Run input validation, independent derived-input audits, unit tests, and the complete analysis workflow. These are verification and traceability procedures, not predictive external validation. The tagged GitHub release and Zenodo DOI must identify the exact computational record used by the manuscript. A SHA-256 checksum may be retained as an optional integrity check for the final archive.
