# Trial effect estimates

This table is generated from `data/trial_effect_estimates.csv`. The CSV is the analysis source of truth for comparative efficacy uncertainty.

| Population | Outcome | Measure | Estimate | 95% CI | Analysis method | Source | Notes |
|---|---|---|---:|---:|---|---|---|
| high_risk | symptomatic_covid_day10 | risk_ratio | 0.24 | 0.12 to 0.49 | Prespecified subgroup risk ratio reported by the trial; uncertainty sampled from the published 95% CI | E01 | Primary PSA pairs a Jeffreys posterior for no-PEP risk with a log-normal draw for this reported risk ratio. Independence is an approximation. |
| overall | symptomatic_covid_day10 | risk_ratio | 0.33 | 0.22 to 0.49 | GEE Poisson regression accounting for household clustering | E01 | Primary modified intention-to-treat analysis. The published confidence interval is used directly for effect uncertainty. |
| high_risk_overall_rr | symptomatic_covid_day10 | risk_ratio | 0.33 | 0.22 to 0.49 | Overall-trial GEE risk ratio applied to high-risk baseline risk in an exploratory scenario | E01 | Addresses potential optimism from using the high-risk subgroup point estimate; not a separately randomized comparison. |
| japan_region | symptomatic_covid_day10 | risk_ratio | 0.18 | 0.1 to 0.33 | GEE Poisson regression within the Japan geographic subgroup (EMA assessment report Table 71) | E22 | Exploratory regional subgroup, all risk levels; not powered for within-region inference. |
| japan_region_high_risk_rr | symptomatic_covid_day10 | risk_ratio | 0.24 | 0.12 to 0.49 | High-risk subgroup risk ratio applied to the Japan-region baseline risk in an exploratory scenario | E01 | Combines the Japan-region placebo risk with the prespecified high-risk subgroup effect; the Japan-by-high-risk cross-classification was not reported. |
| japan_region_overall_rr | symptomatic_covid_day10 | risk_ratio | 0.33 | 0.22 to 0.49 | Overall-trial GEE risk ratio applied to the Japan-region baseline risk in an exploratory scenario | E01 | Conservative efficacy assumption for the Japan-region baseline risk. |
