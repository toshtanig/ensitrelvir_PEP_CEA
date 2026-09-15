.PHONY: install validate audit test parameter-tables basecase scenarios dsa psa thresholds results calibrate all clean

install:
	python -m pip install -e ".[dev]"

validate:
	python scripts/validate_inputs.py

audit:
	python scripts/audit_derived_inputs.py

test:
	pytest

parameter-tables:
	python scripts/write_parameter_tables.py

basecase:
	python scripts/run_basecase.py

scenarios:
	python scripts/run_scenarios.py

dsa:
	python scripts/run_dsa.py

psa:
	python scripts/run_psa.py

thresholds:
	python scripts/run_thresholds.py

results:
	python scripts/write_manuscript_results.py

calibrate:
	python scripts/calibrate_remaining_qaly.py

all:
	python scripts/run_all.py

clean:
	rm -f outputs/tables/* outputs/figures/* outputs/analysis_summary.md outputs/manuscript_results_draft.md outputs/session_info.txt
