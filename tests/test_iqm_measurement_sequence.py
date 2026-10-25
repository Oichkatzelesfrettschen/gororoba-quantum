"""The measurement-sequence pinching case: exact ideals, circuit structure, the analysis and reproducible bytes."""

import iqm_measurement_sequence as case


def test_self_test_holds() -> None:
    if "measurement sequence pinching" not in case.self_test(with_sweep=False):
        raise AssertionError("the self-test summary changed")


def test_estimator_sweep_passes_at_the_reduced_grid() -> None:
    rows = case.sweep(reduced=True)
    if [row["label"] for row in rows] != ["planning", "corner"]:
        raise AssertionError(f"the reduced grid ran {[row['label'] for row in rows]}")


def test_retained_case_checks_and_holds_six_uncoupled_qubits() -> None:
    retained = case.ROOT / "results/iqm/cases" / case.CASE
    excerpt = case.load_json(retained / case.EXCERPT)
    case.check(retained)
    if len(excerpt["qubits"]) != case.QUBIT_COUNT or excerpt["couplers_among_qubits"]:
        raise AssertionError("the retained case does not hold six uncoupled qubits")
    if set(case.EXCLUDED_QUBITS) & set(excerpt["qubits"]):
        raise AssertionError("the retained case holds an excluded qubit")
