"""The measurement-sequence pinching case: exact ideals, circuit structure, the analysis and reproducible bytes.

Tests that read the retained case, its calibration set or the retained runs carry `audit`; the unmarked tests build
their input here (a synthetic qubit calibration and a two-qubit excerpt).
"""

import math
from typing import Any

import iqm_measurement_sequence as case
import pytest

CAL = {"t1_s": 4.5e-5, "t2_s": 1.0e-5, "prx_p": 1.0e-3, "e01": 0.01, "e10": 0.02}


def synthetic_excerpt() -> dict[str, Any]:
    qubits = {
        q: {**CAL, "probe_duration_s": 4.0e-7, "acquisition_delay_s": 3.0e-7, "integration_length_s": 1.0e-6}
        for q in ("QB1", "QB2")
    }
    return {
        "schema": "synthetic",
        "calibration_set": "synthetic-set",
        "source_sha256": {},
        "selection": {},
        "couplers_among_qubits": [],
        "qubits": qubits,
    }


def test_ideal_laws_and_pair_composition_hold() -> None:
    if [round(case.ideal_measure(n), 4) for n in case.STEPS] != [0.0302, 0.5151, 0.6722, 0.8040, 0.8914]:
        raise AssertionError("the ideal measure-arm P0 changed")
    case.check_pairs()


def pooled_inputs() -> tuple[float, float, float, float, float]:
    """(t1, t2, tau of the measure arm, q, window) for CAL at the planning excitation."""
    return (
        CAL["t1_s"],
        min(CAL["t2_s"], 2 * CAL["t1_s"]),
        case.tau_of("measure", case.MEASURE_WINDOW_SECONDS),
        case.PLANNING_Q,
        case.MEASURE_WINDOW_SECONDS,
    )


def test_sign_pooled_response_is_the_per_sign_mean_and_even_in_the_advance() -> None:
    t1, t2, tau, q, _ = pooled_inputs()
    for arm in ("measure", "unitary"):
        args = (arm, case.TOP_STEPS, t1, t2, case.tau_of(arm, case.MEASURE_WINDOW_SECONDS), 0.0, CAL["prx_p"], q)
        pooled = case.pooled_corrected_z(*args, advance=0.02)
        explicit = sum(case.corrected_z(*args, advance=0.02, sign=sign) for sign in case.SIGNS) / len(case.SIGNS)
        if abs(pooled - explicit) > 1e-15:
            raise AssertionError(f"{arm}: pooled {pooled} against the per-sign mean {explicit}")
        # The reflection x -> -x maps sign -1 at advance d onto sign +1 at advance -d.
        if abs(case.corrected_z(*args, advance=0.02, sign=-1) - case.corrected_z(*args, advance=-0.02, sign=1)) > 1e-12:
            raise AssertionError(f"{arm}: the reflection does not map the signs onto each other")
        if abs(case.pooled_corrected_z(*args, advance=0.02) - case.pooled_corrected_z(*args, advance=-0.02)) > 1e-12:
            raise AssertionError(f"{arm}: the pooled response is not even in the advance")
        # A nominal axis phase makes the signs identical, which the +1 chain stands for.
        if abs(case.corrected_z(*args, advance=1e-9, sign=-1) - case.corrected_z(*args, sign=1)) > 1e-7:
            raise AssertionError(f"{arm}: the signs differ at a nominal axis phase")


def test_pooled_axis_ratio_has_no_first_order_term_and_other_classes_are_unchanged() -> None:
    t1, t2, _, q, window = pooled_inputs()
    one = case.gate_class_ratios(t1, t2, q, window, CAL["prx_p"])
    pooled = case.gate_class_ratios(t1, t2, q, window, CAL["prx_p"], pooled=True)
    h = case.GATE_CLASSES["axis_phase"][1]
    first = {}
    for arm in ("measure", "unitary"):
        args = (arm, case.TOP_STEPS, t1, t2, case.tau_of(arm, window), 0.0, CAL["prx_p"], q)
        first[arm] = (case.pooled_corrected_z(*args, advance=h) - case.pooled_corrected_z(*args, advance=-h)) / 2
    if abs(first["unitary"]) > 1e-12 or abs(first["measure"]) > 1e-12:
        raise AssertionError(f"the pooled first-order axis response is {first}")
    if not (math.isfinite(pooled["axis_phase"]) and 0 < abs(pooled["axis_phase"]) < 0.1 and one["axis_phase"] > 0.2):
        raise AssertionError(f"axis ratio: pooled {pooled['axis_phase']}, one-sign {one['axis_phase']}")
    for name in ("drive_dephasing", "composite_angle", "depolarizing"):
        if abs(pooled[name] - one[name]) > 1e-9:
            raise AssertionError(f"{name}: pooled {pooled[name]}, one-sign {one[name]}")


def test_device_counts_give_each_signed_circuit_its_own_chain() -> None:
    skewed = case.device_counts({"Q": case.device_model(CAL, advance=0.02)})
    nominal = case.device_counts({"Q": case.device_model(CAL)})
    unitary = [skewed[name]["final"]["Q"][0] for name in case.group_names("unitary", case.TOP_STEPS)]
    flat = [nominal[name]["final"]["Q"][0] for name in case.group_names("unitary", case.TOP_STEPS)]
    if len(set(flat)) != 1:
        raise AssertionError(f"the nominal device differs between signs: {flat}")
    if unitary[0] != unitary[3] or unitary[1] != unitary[2] or unitary[0] == unitary[1]:
        raise AssertionError(f"an axis phase does not separate the signs: {unitary}")


def test_gate_model_error_widens_the_departure_without_flagging_it() -> None:
    nominal = case.analyze_model(CAL)["departure_n16"]
    skewed = case.analyze_model(CAL, drive_t2_scale=0.5)
    if abs(skewed["departure_n16"]["se"] - nominal["se"]) > 1e-3:
        raise AssertionError("a residual under the floor moves the departure standard error")
    if not case.analyze_model(CAL, advance=0.05)["departure_n16"]["se"] > 1.5 * nominal["se"]:
        raise AssertionError("a unitary-arm residual above the floor does not widen the departure standard error")
    if skewed["decisions"]["departure"]["outcome"] != "consistent":
        raise AssertionError("a gate-model error reads as a departure")
    eps = case.eps_for_shift(CAL, 4 * skewed["departure_n16"]["se"], drive_t2_scale=0.5)
    hit = case.analyze_model(CAL, eps=eps, drive_t2_scale=0.5)
    if hit["decisions"]["departure"]["outcome"] != "departs_below":
        raise AssertionError("an injected departure of four standard errors is missed")


def test_broken_gate_reads_uninformative() -> None:
    broken = case.analyze_model(CAL, **case.BROKEN_GATE)
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


def test_billing_models_differ_by_the_per_record_term() -> None:
    circuits = [case.circuit("measure-n16-s0p", ["QB1"], "measure", 16, 1), case.ro_circuit("ro0", ["QB1"])]
    low, high = case.billing(circuits, 3000, "v1"), case.billing(circuits, 3000, "v2")
    if not high["execution_seconds"] > low["execution_seconds"]:
        raise AssertionError("the per-record term does not raise a measure-heavy prediction")
    if case.billing_model_of({"billing_fit": {}}) != "v1" or (
        case.billing_model_of({"billing_fit": {"execution_per_mid_record_seconds": 1e-6}}) != "v2"
    ):
        raise AssertionError("the billing model of a prediction is misread")


def sweep_inputs() -> tuple[dict[str, str], dict[str, Any], list[dict[str, Any]]]:
    excerpt = synthetic_excerpt()
    return case.build_files(excerpt, "v1"), excerpt, case.sweep_cases(True)


def test_sweep_case_returns_its_row_and_restores_run_facts() -> None:
    files, excerpt, specs = sweep_inputs()
    original = case.run_facts
    models = {q: case.injected_model(cal, specs[0]) for q, cal in excerpt["qubits"].items()}
    row = case.sweep_case((files, excerpt, specs[0], models, "preregistered"))
    if case.run_facts is not original:
        raise AssertionError("a sweep case leaves run_facts substituted")
    if (
        row["label"] != "planning"
        or row["usable"] != len(excerpt["qubits"])
        or row["device_status"]["departs_below"] != "none"
    ):
        raise AssertionError(f"{row['label']} {row['usable']} {row['device_status']}")
    if [row] != case.run_sweep(files, excerpt, specs[:1]):
        raise AssertionError("run_sweep differs from its case worker")


@pytest.mark.audit
def test_pooled_sweep_rows_equal_the_serial_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    files, excerpt, specs = sweep_inputs()
    pooled = case.run_sweep(files, excerpt, specs)
    monkeypatch.setattr(case, "ordered_map", lambda function, items, min_items=2: [function(item) for item in items])
    serial = case.run_sweep(files, excerpt, specs)
    if pooled != serial or [row["label"] for row in pooled] != ["planning", "corner"]:
        raise AssertionError("the pooled sweep rows differ from the serial ones")


@pytest.mark.audit
def test_pooled_diagnostic_projection_equals_the_serial_one(monkeypatch: pytest.MonkeyPatch) -> None:
    analysis = case.load_json(case.DIAGNOSTIC_ANALYSIS)
    excerpt = case.load_json(case.DIAGNOSTIC_EXCERPT)
    serial = case.project_diagnostic(analysis, excerpt)
    pool = case.ordered_map
    monkeypatch.setattr(case, "ordered_map", lambda function, items, min_items=1: pool(function, items, min_items=1))
    pooled = case.project_diagnostic(analysis, excerpt)
    if pooled != serial or list(pooled) != list(analysis["qubits"]):
        raise AssertionError("the pooled diagnostic projection differs from the serial one")


@pytest.mark.audit
def test_self_test_holds() -> None:
    if "measurement sequence pinching" not in case.self_test(with_sweep=False):
        raise AssertionError("the self-test summary changed")


@pytest.mark.audit
def test_estimator_sweep_passes_at_the_reduced_grid() -> None:
    rows = case.sweep(reduced=True)
    if [row["label"] for row in rows] != ["planning", "corner"]:
        raise AssertionError(f"the reduced grid ran {[row['label'] for row in rows]}")


@pytest.mark.audit
def test_retained_case_checks_and_holds_six_uncoupled_qubits() -> None:
    retained = case.ROOT / "results/iqm/cases" / case.CASE
    excerpt = case.load_json(retained / case.EXCERPT)
    case.check(retained)
    if len(excerpt["qubits"]) != case.QUBIT_COUNT or excerpt["couplers_among_qubits"]:
        raise AssertionError("the retained case does not hold six uncoupled qubits")
    if set(case.EXCLUDED_QUBITS) & set(excerpt["qubits"]):
        raise AssertionError("the retained case holds an excluded qubit")


@pytest.mark.audit
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


@pytest.mark.audit
def test_billing_fit_covers_the_measure_heavy_run_and_the_retained_case_keeps_its_model() -> None:
    if "per mid-circuit record" not in case.check_billing_fit():
        raise AssertionError("the billing fit lost its per-record term")
    retained = case.load_json(case.ROOT / "results/iqm/cases" / case.CASE / "prediction.json")
    if case.billing_model_of(retained) != "v1":
        raise AssertionError("the retained case no longer carries the billing it ran under")


@pytest.mark.audit
def test_selector_reproduces_the_retained_analyses_byte_for_byte() -> None:
    root = case.ROOT / "results/iqm"
    run = root / "runs/2026-10-26T004701Z-garnet-measurement-sequence-pinching-pinching"
    for gate_model, name in (
        ("preregistered", "measurement_sequence_pinching_analysis.json"),
        ("sign-pooled", "measurement_sequence_pinching_sign_pooled_analysis.json"),
    ):
        text = case.dump(case.analyze(run, gate_model=gate_model))
        if (root / name).read_text(encoding="utf-8") != text:
            raise AssertionError(f"{gate_model}: {name} differs from the recomputation")


def test_a_fresh_build_is_admissible_under_the_corrected_billing() -> None:
    files = case.build_files(synthetic_excerpt())
    job = case.json.loads(files["cases.json"])["jobs"][0]
    bill = case.json.loads(files["prediction.json"])["billing"]
    if job["max_credits"] != case.MAX_CREDITS or bill["cancel_margin_seconds"] < case.RUNTIME_MARGIN_SECONDS:
        raise AssertionError(f"{job['max_credits']} {bill}")
    retained = case.build_files(synthetic_excerpt(), "v1")
    if case.json.loads(retained["cases.json"])["jobs"][0]["max_credits"] != case.RETAINED_MAX_CREDITS:
        raise AssertionError("a v1 build does not carry the retained ceiling")


def test_the_build_threshold_floors_like_collect() -> None:
    from datetime import UTC, datetime, timedelta

    import iqm_jobs

    circuits = case.circuits_of(["QB1"])
    bill = case.billing(circuits, case.SHOTS, "v2", max_credits=5.71)
    start = datetime(2026, 10, 26, tzinfo=UTC)
    record = {"timeline": [{"status": "compilation_started", "timestamp": start.isoformat()}]}
    at = lambda seconds: iqm_jobs.ceiling_breach(record, 5.71, 0.5, start + timedelta(seconds=seconds))  # noqa: E731
    threshold = bill["cancel_threshold_seconds"]
    if threshold != 10.0 or at(threshold) is None or at(threshold - 0.01) is not None:
        raise AssertionError(f"build threshold {threshold} against collect")
    if abs(bill["cancel_margin_seconds"] - (threshold - bill["worst_case_runtime_seconds"])) > 1e-12:
        raise AssertionError("the build margin is not measured from the collect threshold")


def test_tally_counts_match_a_shot_by_shot_loop() -> None:
    qubits = ["QB1", "QB2"]
    circuit = case.circuit("measure-n2-s0p", qubits, "measure", 2, 1)
    shots = 7
    keys = ["m0", "m1", case.FINAL_KEY]
    result = {k: [[(shot + i + j) % 2 for j in range(2)] for shot in range(shots)] for i, k in enumerate(keys)}
    row = case.tally([circuit], [result])["measure-n2-s0p"]
    expected_final = {q: [0, 0] for q in qubits}
    for shot in result[case.FINAL_KEY]:
        for position, q in enumerate(qubits):
            expected_final[q][shot[position]] += 1
    expected_flips = {
        q: [sum(1 for x, y in zip(result["m0"], result["m1"], strict=True) if x[p] != y[p]), shots]
        for p, q in enumerate(qubits)
    }
    if row["final"] != expected_final or row["flips"] != expected_flips or row["shots"] != shots:
        raise AssertionError(f"{row}")
    bad = {**result, case.FINAL_KEY: [[0, 2]] * shots}
    try:
        case.tally([circuit], [bad])
    except ValueError as error:
        if "outcome 2" not in str(error):
            raise AssertionError(str(error)) from error
    else:
        raise AssertionError("an outcome of 2 is counted")


@pytest.mark.audit
def test_retained_calibration_set_reproduces_the_selection_and_the_case() -> None:
    root = case.ROOT / "results/iqm"
    folder = root / "calibration-sets/garnet/be070414-7624-4943-ac7e-1e2678f05684"
    excerpt = case.load_json(root / "cases" / case.CASE / case.EXCERPT)
    for name, digest in excerpt["source_sha256"].items():
        if case.sha256((folder / name).read_bytes()) != digest:
            raise AssertionError(f"{name} differs from the digest the case excerpt records")
    case.check(root / "cases" / case.CASE, folder)
