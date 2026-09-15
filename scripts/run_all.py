from __future__ import annotations

from collections.abc import Callable

from audit_derived_inputs import run as audit_derived_inputs
from calibrate_remaining_qaly import run as calibrate_remaining_qaly
from run_basecase import run as run_basecase
from run_dsa import run as run_dsa
from run_psa import run as run_psa
from run_scenarios import run as run_scenarios
from run_thresholds import run as run_thresholds
from validate_inputs import run as validate_inputs
from write_parameter_tables import run as write_parameter_tables
from write_manuscript_results import run as write_manuscript_results


def run() -> None:
    steps: list[tuple[str, Callable[[], None]]] = [
        ("validate_inputs", validate_inputs),
        ("audit_derived_inputs", audit_derived_inputs),
        ("calibrate_remaining_qaly", calibrate_remaining_qaly),
        ("parameter_tables", write_parameter_tables),
        ("basecase", run_basecase),
        ("scenarios", run_scenarios),
        ("dsa", run_dsa),
        ("psa", run_psa),
        ("thresholds", run_thresholds),
        ("manuscript_results", write_manuscript_results),
    ]
    for name, function in steps:
        print(f"Running: {name}", flush=True)
        function()


if __name__ == "__main__":
    run()
