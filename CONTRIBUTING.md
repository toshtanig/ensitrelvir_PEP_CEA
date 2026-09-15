# Contributing

Contributions that improve correctness, reproducibility, documentation, or evidence traceability are welcome after the repository becomes public.

Before a pull request, document the scientific rationale, update the evidence and extrapolation registers when inputs change, add tests for logic changes, and run:

```bash
python scripts/validate_inputs.py
python scripts/audit_derived_inputs.py
python -m pytest -q
```

Result-changing changes require the complete workflow and a description of all changed outputs. Preserve the distinction between randomized symptomatic-disease effects and externally modeled downstream outcomes.
