# Model specification, v0.3.2

## Decision problem

The model compares a five-day course of ensitrelvir post-exposure prophylaxis with no pharmacologic prophylaxis among high-risk household contacts in Japan. The primary perspective is the Japanese public healthcare payer perspective. Costs are in Japanese yen and health outcomes are measured in QALYs.

## Primary structure

The publication base case uses `symptomatic_mediation_profile`.

1. Each arm begins with its randomized probability of symptomatic COVID-19 through day 10.
2. A symptomatic case may have a COVID-19-attributable hospitalization or be managed outside hospital.
3. Death occurs only after an attributable hospitalization.
4. Surviving symptomatic cases incur a directly integrated one-year post-acute QALY loss.
5. Ensitrelvir changes only the probability of symptomatic COVID-19. Conditional downstream risks are equal between arms.

Legacy ICU, ventilation, and incidence-duration PCC modules remain available only for structural comparison.

## Event equations

For arm \(s\), let \(p_{sym,s}\) denote symptomatic COVID-19 risk, \(p_h\) the observed 28-day all-cause hospitalization risk among symptomatic high-risk outpatients, \(a_h\) the fraction attributable to COVID-19, and \(p_d\) in-hospital mortality.

\[
P(H_{observed,s})=p_{sym,s}p_h
\]

\[
P(H_{COVID,s})=p_{sym,s}p_h a_h
\]

\[
P(D_s)=p_{sym,s}p_h a_h p_d
\]

\[
P(Outpatient_s)=p_{sym,s}-P(H_{COVID,s})
\]

Nonattributable all-cause admissions are omitted from incremental costs and health effects because the prophylaxis is not assumed to prevent them. The model separately reports the source-endpoint admissions associated with prevented symptomatic cases and the attributed admissions used for cost and mortality.

## Acute costs and QALYs

Expected acute payer cost equals outpatient cases multiplied by outpatient cost plus attributable hospitalizations multiplied by hospital cost. A price and practice adjustment factor is included for sensitivity analysis.

Acute morbidity QALY loss is pathway probability multiplied by utility decrement and duration. Mortality QALY loss equals modeled acute deaths multiplied by discounted remaining QALYs lost per death.

## Remaining QALYs lost per death

The base value is recalculated from:

- the 2025 Japanese abridged life table,
- Japanese age-sex EQ-5D-5L population norms,
- an age-82, 54% male hospitalized-case proxy,
- 2% annual QALY discounting.

The calculation uses half-year correction for annual survival occupancy and is implemented in `src/ensitrelvir_pep_cea/life_table.py`. Ages 75 and 85 are prespecified sensitivity scenarios. Survival after age 105 is omitted, and utility at age 90 or older is carried forward from the age 80 to 89 band.

## One-year post-acute profile

The primary model does not estimate a binary PCC event followed by an assumed duration. Instead, it integrates the attributable utility difference between COVID-19 patients and symptomatic test-negative controls across three intervals:

\[
0.069    imesrac{2}{12} +
0.033    imesrac{3}{12} +
0.025    imesrac{6}{12}
=0.03225\ QALY.
\]

This loss is applied to each surviving symptomatic case. The result should be described as a one-year attributable post-acute QALY profile, not as the number of formally diagnosed PCC cases.

## PEP intervention cost

The intervention cost equals drug acquisition cost plus a bottom-up delivery microcost and incremental adverse-event cost. The base delivery pathway includes a face-to-face initial consultation, qualitative antigen testing, specimen collection, test interpretation, prescription, and representative community-pharmacy fees. No-test and telemedicine pathways are modeled as scenarios.

## Cost-effectiveness metrics

Incremental QALYs equal QALY loss under no prophylaxis minus QALY loss under ensitrelvir. Incremental net monetary benefit is:

\[
INMB=\lambda\Delta QALY-\Delta Cost,
\]

with a reference value of JPY 5,000,000 per QALY. Threshold analyses identify values that produce zero INMB when a crossing occurs within the prespecified grid.

## Uncertainty

The untreated symptomatic risk is sampled from a Jeffreys beta posterior. The published risk ratio and 95% confidence interval are used to parameterize a log-normal distribution, and the ensitrelvir risk is the product of sampled control risk and sampled relative risk. Their unavailable covariance is approximated as zero.

Empirical bounded inputs generally use PERT distributions. Positive skewed costs or durations use gamma or log-normal distributions where specified. The hospitalization attribution fraction and post-acute direct cost remain fixed in the primary PSA because no defensible empirical distribution was identified. They are varied structurally.

## Validation

Repository validation checks numeric bounds, trial arithmetic, source foreign keys, scenario execution, and supported structural modes. `scripts/audit_derived_inputs.py` independently recalculates the PEP delivery microcost, integrated post-acute QALY loss, and remaining QALYs lost per death. Unit tests verify randomized risk arithmetic, intervention cost, attribution behavior, structural exclusions, life-table arithmetic, and PSA reproducibility.

External face-validity checks compare modeled hospital cost and length of stay with a Japanese cost cohort, and compare the publication-base length of stay and in-hospital mortality with the contemporary inpatient cohort used as model inputs.


## Release clarifications, v0.3.2

- The FY2026 two-point outpatient inflation add-on, equivalent to JPY 20 for an initial visit, is not included because its effect is immaterial. Facility-dependent wage add-ons are separately excluded because eligibility varies.
- The exploratory breakthrough-treatment scenario includes antiviral acquisition cost and a treated hospitalization risk but omits additional consultation, testing, and dispensing costs. Including those costs would slightly favor prophylaxis and would not change the conclusion.
- Static downstream-case scenarios assign the same conditional hospitalization and post-acute outcomes as the high-risk contact population. They are upper-bound calculations, not a dynamic transmission model.
- The 10% conditional hospitalization scenario is hypothetical and was not observed in the Japanese sources used in the model.
