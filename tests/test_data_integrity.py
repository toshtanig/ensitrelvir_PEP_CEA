from __future__ import annotations

from ensitrelvir_pep_cea.validation import validate_repository_inputs


def test_repository_input_integrity() -> None:
    errors = [issue for issue in validate_repository_inputs() if issue.severity == "error"]
    assert not errors, "\n".join(f"{issue.check_id}: {issue.message}" for issue in errors)


def test_traceability_check_output_is_not_labeled_external_validation() -> None:
    from ensitrelvir_pep_cea.analysis import input_traceability_table

    frame = input_traceability_table()
    assert set(frame["check_type"]) == {"input_traceability", "external_face_validity"}
