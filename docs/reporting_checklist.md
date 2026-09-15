# Reproducible reporting checklist, v0.3.0

- [ ] Define the Japanese target population, age, sex, and risk-factor criteria.
- [ ] State the index-case and contact eligibility rules and the 72-hour initiation window.
- [ ] Distinguish trial-observed symptomatic efficacy from modeled severe-outcome benefits.
- [ ] Report that the hospitalization source endpoint was all-cause.
- [ ] Report 0%, 50%, and 100% COVID-19 hospitalization-attribution analyses.
- [ ] Report the source, period, and population for hospitalization, mortality, and cost separately.
- [ ] Report the age-82 mortality-QALY proxy and age-75 and age-85 scenarios.
- [ ] Describe the one-year post-acute QALY integral rather than calling it a diagnosed PCC count.
- [ ] Report that post-acute direct medical cost is zero in the payer base case because of an evidence gap.
- [ ] Report PEP microcost components and no-test and telemedicine scenarios.
- [ ] Present disaggregated intervention, acute, post-acute, morbidity, and mortality results.
- [ ] Present DSA using incremental net monetary benefit.
- [ ] Present PSA distributions, seed, simulation count, cost-effectiveness plane, and CEAC.
- [ ] Present drug-price, hospitalization-risk, mortality, post-acute QALY, and post-acute cost thresholds.
- [ ] Run `python scripts/validate_inputs.py` and `python scripts/audit_derived_inputs.py`.
- [ ] Run `python -m pytest -q` in a clean environment.
- [ ] Archive inputs, code, outputs, package lock, analysis date, Git commit, release tag, and Zenodo DOI. An optional SHA-256 checksum may be retained for the final archive.
- [ ] Update author, affiliation, repository, and DOI fields in `CITATION.cff`.

## Review-response checks added in v0.3.0

- [ ] Describe the post-acute utility source as a retrospective online recall survey, not a prospective longitudinal cohort.
- [ ] Report the overall-trial RR scenario and the 6-month, 50%, and zero post-acute utility scenarios.
- [ ] Report mixed source price years and the lack of full 2026 re-pricing for transferred costs.
- [ ] Use verification and input traceability terminology unless an independent predictive validation dataset is used.
- [ ] Explain that PERT distributions were used when only a base value and plausible range were available.
- [ ] Report CEAC probabilities of 0%, 0.02%, and 2.28% at JPY 5, 7.5, and 10 million/QALY.
