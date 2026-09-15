from __future__ import annotations

from _bootstrap import TABLES
from ensitrelvir_pep_cea.validation import issues_to_frame, validate_repository_inputs


def run() -> None:
    issues = validate_repository_inputs()
    report = issues_to_frame(issues)
    report.to_csv(TABLES / "input_validation.csv", index=False, encoding="utf-8-sig")
    print(report.to_string(index=False))
    errors = [issue for issue in issues if issue.severity == "error"]
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    run()
