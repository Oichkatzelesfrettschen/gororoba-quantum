"""The measurement-sequence pinching case: exact ideals, circuit structure, the analysis and reproducible bytes."""

import tempfile
from pathlib import Path

import iqm_measurement_sequence as case


def test_self_test_holds() -> None:
    if "measurement sequence pinching" not in case.self_test():
        raise AssertionError("the self-test summary changed")


def test_case_bytes_are_reproducible_and_retained_case_checks() -> None:
    excerpt = case.excerpt_of(case.CALIBRATION_DIR)
    if case.build_files(excerpt) != case.build_files(excerpt):
        raise AssertionError("two builds from one calibration differ")
    with tempfile.TemporaryDirectory() as scratch:
        directory = Path(scratch) / case.CASE
        case.write(directory, case.CALIBRATION_DIR)
        case.check(directory)
    case.check(case.ROOT / "results/iqm/cases" / case.CASE)
