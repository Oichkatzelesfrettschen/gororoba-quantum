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
    if abs(skewed["departure_n16"]["se"] - nominal["se"]) > 1e-3:
        raise AssertionError("a residual under the floor moves the departure standard error")
    if not case.analyze_model(cal, advance=0.05)["departure_n16"]["se"] > 1.5 * nominal["se"]:
        raise AssertionError("a unitary-arm residual above the floor does not widen the departure standard error")
    if skewed["decisions"]["departure"]["outcome"] != "consistent":
        raise AssertionError("a gate-model error reads as a departure")
    eps = case.eps_for_shift(cal, 4 * skewed["departure_n16"]["se"], drive_t2_scale=0.5)
    hit = case.analyze_model(cal, eps=eps, drive_t2_scale=0.5)
    if hit["decisions"]["departure"]["outcome"] != "departs_below":
        raise AssertionError("an injected departure of four standard errors is missed")


def test_broken_gate_reads_uninformative_and_cancelling_classes_are_not_attributed() -> None:
    excerpt = case.load_json(case.ROOT / "results/iqm/cases" / case.CASE / case.EXCERPT)
    cal = next(iter(excerpt["qubits"].values()))
    broken = case.analyze_model(cal, **case.BROKEN_GATE)
    if broken["decisions"]["mutation_test"]["passes"] or broken["informative"]:
        raise AssertionError("a broken gate stays informative")
    row = {"usable": True, **{k: broken[k] for k in ("informative", "uninformative_reasons")}}
    row |= {
        "departure_n16": broken["departure_n16"],
        "settle_n16": broken["settle_n16"],
        "decisions": broken["decisions"],
    }
    verdict = case.device_verdict({f"QB{n}": row for n in range(6)})
    if verdict["departs_below"]["status"] != "uninformative":
        raise AssertionError(f"{verdict['departs_below']}")


def test_billing_fit_covers_the_measure_heavy_run_and_the_retained_case_keeps_its_model() -> None:
    if "per mid-circuit record" not in case.check_billing_fit():
        raise AssertionError("the billing fit lost its per-record term")
    retained = case.load_json(case.ROOT / "results/iqm/cases" / case.CASE / "prediction.json")
    if case.billing_model_of(retained) != "v1":
        raise AssertionError("the retained case no longer carries the billing it ran under")
    circuits = [
        case.load_json(case.ROOT / "results/iqm/cases" / case.CASE / f"circuits/{name}.json")
        for name in ("measure-n16-s0p", "ro0")
    ]
    low, high = case.billing(circuits, 3000, "v1"), case.billing(circuits, 3000, "v2")
    if not high["execution_seconds"] > low["execution_seconds"]:
        raise AssertionError("the per-record term does not raise a measure-heavy prediction")
