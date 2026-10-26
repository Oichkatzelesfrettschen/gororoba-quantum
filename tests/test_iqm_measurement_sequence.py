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


def test_selection_rests_on_calibration_and_measured_failures_only() -> None:
    retained = case.ROOT / "results/iqm/cases" / case.CASE
    selection = case.load_json(retained / case.EXCERPT)["selection"]
    if set(case.EXCLUDED_QUBITS) != {"QB11"}:
        raise AssertionError("an exclusion rests on something other than a measured failure")
    limit = selection["prx_error_limit"]
    if limit is None or any(v <= limit for v in selection["excluded_for_prx_error"].values()):
        raise AssertionError("a qubit under the prx limit is excluded for its prx error")
    prx = {q: row["prx_p"] for q, row in case.load_json(retained / case.EXCERPT)["qubits"].items()}
    if any(v > limit for v in prx.values()):
        raise AssertionError("a chosen qubit exceeds the prx limit")


def test_gate_model_error_widens_the_departure_without_flagging_it() -> None:
    excerpt = case.load_json(case.ROOT / "results/iqm/cases" / case.CASE / case.EXCERPT)
    cal = next(iter(excerpt["qubits"].values()))
    nominal = case.analyze_model(cal)["departure_n16"]
    skewed = case.analyze_model(cal, drive_t2_scale=0.5)
    if not skewed["departure_n16"]["se"] > nominal["se"]:
        raise AssertionError("a unitary-arm residual does not widen the departure standard error")
    if skewed["decisions"]["departure"]["outcome"] != "consistent":
        raise AssertionError("a gate-model error reads as a departure")
    eps = case.eps_for_shift(cal, 4 * skewed["departure_n16"]["se"], drive_t2_scale=0.5)
    hit = case.analyze_model(cal, eps=eps, drive_t2_scale=0.5)
    if hit["decisions"]["departure"]["outcome"] != "departs_below":
        raise AssertionError("an injected departure of four standard errors is missed")
