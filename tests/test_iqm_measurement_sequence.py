"""The measurement-sequence pinching case: exact ideals, circuit structure, the analysis and reproducible bytes.

Tests that read the retained case, its calibration set or the retained runs carry `audit`; the unmarked tests build
their input here (a synthetic qubit calibration and a two-qubit excerpt).
"""

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
    row = case.sweep_case((files, excerpt, specs[0]))
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
