# Cohort QALY calibration example

All CSV files in this directory are synthetic and exist only to demonstrate the required schema. They are not used by the base model and must not be cited as Japanese empirical inputs.

For a locked analysis:

1. Replace `life_table_synthetic.csv` with a CSV derived from the Japanese complete life table, with columns `age`, `sex`, and `lx`.
2. Replace `utility_norms_synthetic.csv` with licensed or appropriately transcribed Japanese age-sex utility norms, with columns `sex`, `age_start`, `age_end`, and `utility`.
3. Replace `cohort_distribution_synthetic.csv` with the target PEP cohort distribution. Weights need not sum to one because the script normalizes them.
4. Set `mortality_hazard_ratio` to 1.0 for general-population mortality or use a justified high-risk mortality adjustment.
5. Run `scripts/calibrate_remaining_qaly.py` with explicit input paths and copy the resulting weighted mean into a versioned scenario or parameter file after expert review.
