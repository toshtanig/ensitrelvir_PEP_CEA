# Age-sex-specific calibration of QALYs lost per acute death

The prototype base case uses a scalar parameter, `remaining_qaly_if_acute_death`, because the Japanese implementation cohort has not been fixed. The final manuscript should calculate this parameter from the target cohort's age-sex distribution, Japanese survival, and age-sex utility norms.

## Implemented method

`src/ensitrelvir_pep_cea/life_table.py` calculates expected discounted future QALYs for each age-sex stratum. Annual survival is derived from consecutive `lx` values. A half-cycle approximation is used for person-time alive within each year, age-sex utility is applied at attained age, and future QALYs are discounted at the model rate.

An optional `mortality_hazard_ratio` applies a proportional-hazard approximation to each annual mortality probability. This supports a transparent high-risk mortality scenario but should not be used without empirical justification.

## Required input schemas

Cohort distribution:

```text
age,sex,weight,mortality_hazard_ratio
```

Life table:

```text
age,sex,lx
```

Utility norms:

```text
sex,age_start,age_end,utility
```

Sex values are `male` and `female`. Ages must be consecutive in the life table, and utility bands must cover every attained age used by the calculation.

## Command

```bash
python scripts/calibrate_remaining_qaly.py \
  --cohort path/to/cohort_distribution.csv \
  --life-table path/to/japan_life_table.csv \
  --utility-norms path/to/japan_utility_norms.csv \
  --discount-rate 0.02 \
  --output outputs/tables/cohort_qaly_calibration.csv
```

The default command uses clearly labeled synthetic files in `examples/cohort_calibration/` for code demonstration only. It must not be used to populate the base-case parameter.

## Recommended sources

Use the Ministry of Health, Labour and Welfare complete life tables for survival and Japanese EQ-5D-5L population norms for utility. Record the extraction process, any age-band interpolation, the target cohort source, and the mortality adjustment in the evidence register and analysis protocol.
