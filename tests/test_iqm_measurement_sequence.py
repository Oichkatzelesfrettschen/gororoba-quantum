"""The measurement-sequence pinching case: exact ideals, circuit structure, the analysis and reproducible bytes."""

from pathlib import Path

import iqm_measurement_sequence as case


def test_self_test_holds() -> None:
    if "measurement sequence pinching" not in case.self_test():
        raise AssertionError("the self-test summary changed")


def test_case_bytes_are_reproducible_and_retained_case_checks(tmp_path: Path) -> None:
    retained = case.ROOT / "results/iqm/cases" / case.CASE
    excerpt = case.load_json(retained / case.EXCERPT)
    if case.build_files(excerpt) != case.build_files(excerpt):
        raise AssertionError("two builds from one calibration excerpt differ")
    case.check(retained)
    if len(excerpt["qubits"]) != case.QUBIT_COUNT or excerpt["couplers_among_qubits"]:
        raise AssertionError("the retained case does not hold six uncoupled qubits")
    for name, text in case.build_files(excerpt).items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    case.check(tmp_path)
