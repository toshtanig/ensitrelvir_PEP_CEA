# Residual evidence gaps after the v0.3.0 update

## 1. Causal attribution of hospitalization

The Japanese outpatient source reports 28-day all-cause hospitalization. The base model attributes all such admissions to COVID-19, which may favor prophylaxis if incidental admissions are common. The 50% and 0% scenarios are mandatory. A future claims study should adjudicate diagnosis-related admissions or use cause-specific hospitalization.

## 2. Hospitalization, mortality, and cost are linked across sources

The absolute hospitalization risk, in-hospital mortality, and hospital cost arise from different Japanese cohorts, periods, and care settings. A single linked claims or EHR dataset would permit internally consistent estimation of conditional hospitalization, death, length of stay, and cost by age, vaccination, prior infection, immunocompromise, and calendar period.

## 3. Older and highly vulnerable contacts

The outpatient claims study contains relatively few adults aged 65 years or older. Its subgroup hospitalization risk and comorbidity odds ratios are therefore exploratory. A dedicated cohort of older adults, hematologic malignancy, solid-organ transplant, B-cell-depleting therapy, and other immunocompromised groups is needed.

## 4. Decedent-specific remaining QALYs

The base mortality-QALY calibration uses age and sex of hospitalized cases, not of deaths among eligible PEP contacts. Future work should use age-sex distribution of COVID-19 deaths in the relevant treated and untreated risk groups, with comorbidity-adjusted background mortality where possible.

## 5. Post-acute generalizability

The Japanese retrospective online recall utility survey was younger and less comorbid than the modeled high-risk population, used only 77 test-negative controls, lacked prospective baseline utility, and may be affected by recall and response-selection bias. The directly integrated QALY profile may understate burden after severe disease or overstate attributable loss if high-risk controls have more background symptoms. Severity-specific and age-specific Japanese longitudinal EQ-5D data are needed.

## 6. Post-acute direct medical cost

No sufficiently transportable Japanese matched incremental cost estimate was identified. A study should compare at least 12 months of outpatient visits, diagnostics, rehabilitation, mental health care, prescriptions, emergency care, and hospitalization between infected patients and matched uninfected or test-negative controls.

## 7. Real-world PEP implementation

The fee-schedule microcost does not measure operational delay, urgent delivery, clinician capacity, test availability, or nonreimbursed coordination. A prospective implementation study should record contact-to-prescription time, test pathway, consultation mode, pharmacy category, delivery, adherence, eligibility, drug interactions, and incomplete courses.

## 8. Efficacy covariance and household clustering

The PSA uses the published relative-risk interval and an arm-level Jeffreys posterior for control risk, with independence assumed because their covariance is unavailable. Sponsor-provided cluster-level data, joint bootstrap draws, or the covariance matrix from the fitted household-adjusted model would improve uncertainty propagation.

## 9. Future variants and immunity

Absolute attack risk and hospitalization risk can change with circulating variants, vaccination, and prior infection. The model should be re-locked for a defined calendar period and updated when the target epidemiology changes materially.

## 10. Transmission and societal effects

The payer base case excludes secondary transmission, caregiver health, absenteeism, and productivity. These effects require a separately specified transmission or societal model and should not be added to the static payer model without addressing double counting.

- The acute utility decrement is applied for 7 days and the post-acute profile begins at month 1. Health loss from day 8 through day 30 is omitted, which is conservative for prophylaxis.
