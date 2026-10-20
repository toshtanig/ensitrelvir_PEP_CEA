# Release notes v0.3.3

This release responds to an internal pre-submission audit. The model structure is unchanged. The base-case incremental cost, ICER and thresholds change slightly because the hospitalization cost input was changed from the reported median to the arithmetic mean; incremental QALYs are unchanged.

Changes:

- the QALY discount rate now propagates to the discounted remaining QALYs per acute death in one-way sensitivity analysis (regression test added);
- hospitalization cost base value changed from the reported median (JPY 1,304,431) to the arithmetic mean derived from the reported total (JPY 2,056,604);
- exploratory Japan-region scenarios added from the SCORPIO-PEP Japan geographic subgroup (EMA assessment report Table 71);
- two exploratory joint scenarios (Japan-region attack rates with higher hospitalization risk) were added;
- the hypothetical 10% hospitalization scenario is now labeled as also recalibrating remaining QALYs per death to the age-85 proxy;
- superseded v0.2 evidence-register notes are marked as historical;
- a two-way threshold analysis (drug cost threshold versus baseline attack rate and versus hospitalization risk, by post-acute assumption) was added;
- a publication figure script was added (`scripts/make_publication_figures.py`); and
- release metadata was updated (author affiliations and ORCID iDs; target journal).

Base-case results, v0.3.3: incremental cost JPY 54,500; incremental QALYs 0.003267; ICER JPY 16.68 million per QALY; INMB at JPY 5 million per QALY, JPY -38,164; drug acquisition cost threshold JPY 11,466 per course.
