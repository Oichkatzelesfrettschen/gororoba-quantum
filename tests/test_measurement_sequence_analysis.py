"""The preregistered measurement-sequence pinching analysis: self-test, device rule, count glue and dispatch."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pytest

import diagnostic_experiments as de
import measurement_sequence_analysis as msa
import qpu_planning


def check(condition: bool, message: str = "check failed") -> None:
    """Raise on a false condition; python -O strips assert, so a check raises explicitly."""
    if not condition:
        raise AssertionError(message)


FEW = msa.FIXTURE_QUBITS[:3]
FLOOR = msa.DEMONSTRATION_SCATTER_FLOOR


def test_self_test_passes() -> None:
    check(msa.self_test(with_sweep=False, qubit_count=len(FEW)).startswith("measurement-sequence pinching analysis"))


def test_constants_follow_the_family() -> None:
    check(msa.THETA == de.MSQ_THETA)
    check(msa.STEPS == de.MSQ_STEPS and msa.MEASURE_STEPS == de.MSQ_MEASURE_STEPS)
    check(msa.T1_COUNT == len(de.MSQ_T1_MICROSECONDS))
    check(msa.ARM_STEPS == {arm: tuple(de.MSQ_ARM_COUNTS[arm]) for arm in msa.ARMS})
    check(msa.member_names("measure", 4, 7) == [de.msq_member("measure", 4, signed, 7) for signed in de.MSQ_SIGNED])
    check(msa.ro0_name(7) == de.msq_ro0_member(7) and msa.t1_names(7)[3] == de.msq_t1_member(3, 7))
    for steps in de.MSQ_MEASURE_STEPS:
        check(math.isclose(msa.ideal_measure(steps), de.msq_pinched_p0(steps), abs_tol=1e-15))
    check(math.isclose(msa.ideal_delay(), de.msq_delay_p0(), abs_tol=1e-15))


def test_ro0_member_is_a_static_zero_pulse_read() -> None:
    circuit = de.msq_ro0_circuit(5, 480)
    check([inst.operation.name for inst in circuit.data] == ["delay", "measure"])
    check(circuit.data[0].operation.duration == 480)
    with pytest.raises(ValueError):
        de.msq_ro0_circuit(5, 0)


@pytest.mark.parametrize(
    "z, verdict", ((-3.01, "departs_below"), (-2.99, "consistent"), (2.99, "consistent"), (3.01, "exceeds_prediction"))
)
def test_departure_thresholds(z: float, verdict: str) -> None:
    check(msa.decide(0.9, 0.01, z * 0.01, 0.01)["departure"]["outcome"] == verdict)


@pytest.mark.parametrize(
    "z, verdict",
    ((3.01, "reduced_by_gap"), (2.99, "unchanged_by_gap"), (-2.99, "unchanged_by_gap"), (-3.01, "deepened_by_gap")),
)
def test_gap_thresholds(z: float, verdict: str) -> None:
    check(msa.classify_gap(z) == verdict)


def test_mutation_threshold() -> None:
    check(msa.decide(0.5301, 0.01, 0.0, 0.01)["mutation_test"]["passes"])
    check(not msa.decide(0.5299, 0.01, 0.0, 0.01)["mutation_test"]["passes"])
    with pytest.raises(msa.AnalysisError):
        msa.decide(0.9, 0.0, 0.0, 0.01)


def _usable(outcome: str, difference: float, gap: str = "unchanged_by_gap") -> dict[str, Any]:
    gap_difference = {"reduced_by_gap": 0.031, "deepened_by_gap": -0.031}.get(gap, 0.0)
    return {
        "usable": True,
        "model_scatter_floor": msa.DEMONSTRATION_SCATTER_FLOOR,
        "departure_n16": {"difference": difference, "se": 0.01, "se_statistical": 0.01, "se_systematic": 0.0},
        "decisions": {"departure": {"outcome": outcome}, "mutation_test": {"passes": True}},
        "settle_n16": {
            "gap_difference": gap_difference,
            "se": 0.01,
            "se_statistical": 0.01,
            "se_systematic": 0.0,
            "verdict": gap,
        },
    }


def _flags(verdict: dict[str, Any]) -> dict[str, bool]:
    return msa.device_flags(verdict)


def test_device_rule_needs_two_qubits_or_a_pooled_z() -> None:
    quiet = {q: _usable("consistent", 0.0) for q in range(8)}
    check(not any(_flags(msa.device_verdict(quiet)).values()))
    one = {**quiet, 0: _usable("departs_below", -0.031, "reduced_by_gap")}
    verdict = msa.device_verdict(one)
    check(not verdict["departs_below"]["device"] and not verdict["settle_reduced_by_gap"]["device"], f"{verdict}")
    two = {**one, 1: _usable("departs_below", -0.031, "reduced_by_gap")}
    verdict = msa.device_verdict(two)
    check(verdict["departs_below"]["device"] and verdict["settle_reduced_by_gap"]["device"], f"{verdict}")
    check(not verdict["exceeds_prediction"]["device"] and not verdict["settle_deepened_by_gap"]["device"])
    # Eight qubits at -0.012 each with se 0.01: no qubit reaches 3 SE, the pooled z is -3.4.
    drift = {q: _usable("consistent", -0.012) for q in range(8)}
    verdict = msa.device_verdict(drift)
    check(verdict["departs_below"]["device"] and verdict["departs_below"]["qubits"] == [], f"{verdict}")
    check(not verdict["exceeds_prediction"]["device"])
    rising = {q: _usable("consistent", 0.012) for q in range(8)}
    check(msa.device_verdict(rising)["exceeds_prediction"]["device"])
    deepening = {q: _usable("consistent", 0.0, "unchanged_by_gap") for q in range(8)}
    deepening[0] = _usable("consistent", 0.0, "deepened_by_gap")
    deepening[1] = _usable("consistent", 0.0, "deepened_by_gap")
    check(msa.device_verdict(deepening)["settle_deepened_by_gap"]["device"])
    unusable = {**quiet, 0: {"usable": False}}
    check(msa.device_verdict(unusable)["usable_qubits"] == list(range(1, 8)))


def test_pooled_z_adds_systematics_linearly() -> None:
    """Independent statistical errors shrink with the qubit count; a systematic shared by the device does not."""
    statistical = [(-0.01, 0.01, 0.0)] * 4
    check(math.isclose(msa.pooled_z(statistical) or 0.0, -2.0, rel_tol=1e-9))
    shared = [(-0.01, 0.0, 0.01)] * 4
    check(math.isclose(msa.pooled_z(shared) or 0.0, -1.0, rel_tol=1e-9))
    mixed = [(-0.02, 0.01, 0.01)] * 4
    check(math.isclose(msa.pooled_z(mixed) or 0.0, -0.02 / math.sqrt(0.01**2 / 4 + 0.01**2), rel_tol=1e-9))
    check(msa.pooled_z([]) is None)


def test_device_verdict_has_no_veto() -> None:
    """The gate-model systematic enters the departure SE; the verdict statuses are none and attributed."""
    quiet = {q: _usable("consistent", 0.0) for q in range(8)}
    two = {**quiet, 0: _usable("departs_below", -0.031), 1: _usable("departs_below", -0.031)}
    verdict = msa.device_verdict(two)
    check(verdict["departs_below"]["status"] == "attributed" and verdict["departs_below"]["device"])
    check({v["status"] for v in verdict.values() if isinstance(v, dict) and "status" in v} <= {"none", "attributed"})


def test_propagation_ratios_at_the_fixture() -> None:
    """Depolarizing error propagates at about -0.8, drive dephasing at about -0.5, a relative axis tilt near
    0 (its first-order effect is odd under the sign and cancels in the pool) and an over-rotation near +0.1; a zero
    residual propagates nothing."""
    ctx = msa.fixture_contexts((91,))[91]
    t1, q = ctx["t1_cal_s"], 1.03
    zero = msa.gate_propagation(msa.gate_curves(t1, q, ctx, msa.WINDOW_RELAX_FRACTION), 0.0)
    check(all(abs(c["measure_shift"]) < 1e-9 for c in zero.values()), f"{zero}")
    shifts = msa.gate_propagation(msa.gate_curves(t1, q, ctx, msa.WINDOW_RELAX_FRACTION), 0.01)
    ratio = {name: c["ratio"] for name, c in shifts.items()}
    check(-0.9 < ratio["depolarizing"] < -0.7, f"{ratio}")
    check(-0.6 < ratio["drive_dephasing"] < -0.4, f"{ratio}")
    check(abs(ratio["axis_phase"]) < 0.1, f"{ratio}")
    check(abs(ratio["angle_error"] or 0.0) < 0.2, f"{ratio}")
    check(all(c["reaches_residual"] for name, c in shifts.items() if name != "angle_error"))


def test_a_common_axis_tilt_is_invisible() -> None:
    ctx = msa.fixture_contexts((91,))[91]
    nominal = msa.corrected_z("unitary", 16, ctx["t1_cal_s"], ctx["t2_s"], 0.0, 0.0, msa.sx_gate(ctx), 1.0)
    for angle in (0.01, 0.1):
        # the relative tilt acts; the common tilt, a frame change about Z, would not.
        tilted = msa.corrected_z(
            "unitary", 16, ctx["t1_cal_s"], ctx["t2_s"], 0.0, 0.0, msa.sx_gate(ctx, axis_phase=angle), 1.0
        )
        check(abs(tilted - nominal) > 1e-3)


def test_unitary_residual_widens_the_departure_se() -> None:
    contexts = msa.fixture_contexts(FEW)
    models = {q: msa.device_model(c, sx_error=3 * c["sx_error"]) for q, c in contexts.items()}
    stressed = msa.evaluate(msa.device_counts(models, contexts, msa.FIXTURE_SHOTS), contexts)
    clean = msa.evaluate(
        msa.device_counts({q: msa.device_model(c) for q, c in contexts.items()}, contexts, msa.FIXTURE_SHOTS), contexts
    )
    for q in contexts:
        check(stressed[q]["gate_systematic_n16"]["unitary_residual"] > 0.01)
        check(stressed[q]["gate_systematic_n16"]["propagated_se"] > clean[q]["gate_systematic_n16"]["propagated_se"])
        check(abs(stressed[q]["decisions"]["departure"]["z"]) < 1.5)


def _rows(labels: tuple[str, ...]) -> dict[str, dict[str, Any]]:
    contexts = msa.fixture_contexts(FEW)
    cases = [case for case in msa.sweep_cases(False) if case["label"] in labels]
    check(len(cases) == len(labels))
    rows = {r["label"]: r for r in msa.run_sweep(contexts, cases, msa.FIXTURE_SHOTS)}
    failures = msa.sweep_failures(list(rows.values()), len(contexts))
    check(not failures, f"{failures}")
    return rows


def test_planning_point_and_injected_effects() -> None:
    rows = _rows(("planning", "no relaxation in the window", "measure eps 0.01", "tail eps 0.01 (measure arm only)"))
    planning = rows["planning"]
    check(planning["mutation_passes"] and not any(planning["device"].values()))
    check(all(abs(z) < 1 for z in planning["departure_z"].values()))
    tail = rows["tail eps 0.01 (measure arm only)"]
    check(tail["device"]["settle_reduced_by_gap"] and all(v == "reduced_by_gap" for v in tail["settle"].values()))
    transition = rows["measure eps 0.01"]
    check(transition["device"]["departs_below"] and not transition["device"]["settle_reduced_by_gap"])
    check(not any(rows["no relaxation in the window"]["device"].values()))


# The gate-model rows split three ways so each test's sweep stays inside the pull-request budget.
def test_scaled_gate_errors_are_never_attributed() -> None:
    """A gate error scaled up is never attributed, and errors that cancel in the unitary arm are not attributed."""
    rows = _rows(("sx x3", "axis tilt 0.02 + sx x3"))
    stress = rows["sx x3"]
    check(not stress["device"]["departs_below"] and not stress["device"]["exceeds_prediction"], f"{stress['device']}")
    check(min(stress["unitary_residual"].values()) > 0.01)
    check(not rows["axis tilt 0.02 + sx x3"]["device"]["departs_below"])


@pytest.mark.parametrize("residual", ("+0.014", "+0.033"))
def test_moderate_model_error_reads_none_and_attributes_a_real_departure(residual: str) -> None:
    """A null device with a moderate model error reads none, and a real departure on that device is attributed."""
    null = f"model error, residual -0.016 to {residual}"
    departure = f"model error -0.016..{residual} + measure eps 0.02"
    rows = _rows((null, departure))
    check(set(rows[null]["device_status"].values()) == {"none"})
    check(rows[departure]["device"]["departs_below"])


def test_large_model_error_reads_uninformative() -> None:
    """A gate-model error of about 0.03 on top of an sx error of three times the Target's widens the departure
    standard error past twice its planning value, so the device reads uninformative rather than none."""
    rows = _rows(("model error -0.016..+0.033 + sx x3",))
    row = rows["model error -0.016..+0.033 + sx x3"]
    check(row["device_overall"] == "uninformative" and set(row["device_status"].values()) == {"uninformative"})
    check(not any(row["device"].values()))


def test_uninformative_qubits_leave_the_count_and_pooled_rules() -> None:
    quiet = {q: _usable("consistent", 0.0) for q in range(8)}
    flagged = {**quiet, 0: _usable("departs_below", -0.031), 1: _usable("departs_below", -0.031)}
    check(msa.device_verdict(flagged)["departs_below"]["device"])
    muted = {q: {**r, "informative": q > 1, "uninformative_reason": "test"} for q, r in flagged.items()}
    verdict = msa.device_verdict(muted)
    check(not verdict["departs_below"]["device"] and verdict["status"] == "informative", f"{verdict}")
    check(sorted(verdict["uninformative_qubits"]) == [0, 1] and verdict["informative_qubits"] == list(range(2, 8)))
    sparse = {q: {**r, "informative": q == 0, "uninformative_reason": "test"} for q, r in quiet.items()}
    verdict = msa.device_verdict(sparse)
    check(verdict["status"] == "uninformative" and verdict["departs_below"]["status"] == "uninformative")
    check(not any(msa.device_flags(verdict).values()))


def test_unmeasured_scatter_floor_leaves_a_departure_unattributed() -> None:
    """With no measured model scatter, a fired departure reads gate_model_unbounded and nothing is attributed."""
    check(msa.MODEL_SCATTER_FLOOR is None)
    contexts = msa.fixture_contexts(FEW, floor=None)
    specs = {case["label"]: case for case in msa.sweep_cases(False)}
    planning = msa.run_row((specs["planning"], contexts, msa.FIXTURE_SHOTS))
    check(set(planning["device_status"].values()) == {"none"})
    injected = msa.run_row((specs["measure eps 0.01"], contexts, msa.FIXTURE_SHOTS))
    check(injected["device_status"]["departs_below"] == "gate_model_unbounded", f"{injected['device_status']}")
    check(not any(injected["device"].values()))
    tail = msa.run_row((specs["tail eps 0.01 (measure arm only)"], contexts, msa.FIXTURE_SHOTS))
    check(tail["device"]["settle_reduced_by_gap"], "the gap verdict compares equal gate counts and needs no floor")


def test_informative_rule() -> None:
    ctx = {"planning_se": 0.008}
    decisions: dict[str, Any] = {"mutation_test": {"passes": True}}
    departure: dict[str, Any] = {"se": 0.0159}
    row: dict[str, Any] = {"usable": True, "decisions": decisions, "departure_n16": departure}
    check(msa.informative(row, ctx) == (True, None))
    departure["se"] = 0.0161
    check(not msa.informative(row, ctx)[0])
    departure["se"] = 0.008
    decisions["mutation_test"]["passes"] = False
    check(msa.informative(row, ctx) == (False, "the mutation test fails"))
    check(not msa.informative({"usable": False, "reason": "floor"}, ctx)[0])


def test_sweep_failures_name_a_missing_withholding() -> None:
    contexts = msa.fixture_contexts(FEW)
    rows = msa.run_sweep(contexts, msa.sweep_cases(True)[:1], msa.FIXTURE_SHOTS)
    check(not msa.sweep_failures(rows, len(contexts)))
    forged = {**rows[0], "expect": "tail"}
    check(any("tail is not caught" in f for f in msa.sweep_failures([forged], len(contexts))))
    check(any("departure" in f for f in msa.sweep_failures([{**rows[0], "expect": "departure"}], len(contexts))))
    check(any("usable" in f for f in msa.sweep_failures(rows, len(contexts) + 1)))


def _distributions(counts: dict[int, dict[str, Any]]) -> dict[str, list[np.ndarray]]:
    """Per-member laws with the expected final-bit marginal and every mid-circuit bit 0."""
    out: dict[str, list[np.ndarray]] = {}
    for rows in counts.values():
        for name, (ones, shots) in rows["final"].items():
            mid = "_measure_" in name or "_settle_" in name
            width = 2 ** (int(name.split("_n")[1].split("_")[0]) + 1) if mid else 2
            law = np.zeros(width)
            law[0], law[1] = 1 - ones / shots, ones / shots
            out[name] = [law]
    return out


def _record_and_executed(contexts: dict[int, dict[str, Any]], shots: int) -> tuple[dict[str, Any], dict[str, Any]]:
    dt = 4e-9
    ctx = next(iter(contexts.values()))
    configuration = {
        "qubits": list(contexts),
        "dt_seconds": dt,
        "measurement_delay_dt": {str(q): round(c["delay_s"] / dt) for q, c in contexts.items()},
        "settle_delay_dt": {str(q): round(c["settle_s"] / dt) for q, c in contexts.items()},
        "prereadout_delay_dt": {str(q): round(c["prereadout_s"] / dt) for q, c in contexts.items()},
        "t1_delays_dt": [round(d / dt) for d in ctx["t1_delays_s"]],
    }
    calibration = {
        str(q): {
            "T1": c["t1_cal_s"] * 1e6,
            "T2": c["t2_s"] * 1e6,
            "prob_meas1_prep0": c["e01"],
            "prob_meas0_prep1": c["e10"],
        }
        for q, c in contexts.items()
    }
    gates = {
        str(q): {
            "sx_error": c["sx_error"],
            "sx_duration_s": c["sx_duration_s"],
            "measure_duration_s": c["window_s"],
        }
        for q, c in contexts.items()
    }
    return {"family_configuration": configuration}, {
        "_template": {"shots": shots, "placed_qubit_calibration": calibration, "placed_gate_calibration": gates}
    }


def test_collected_matches_the_direct_analysis() -> None:
    contexts = msa.fixture_contexts(FEW)
    counts = msa.device_counts({q: msa.device_model(c) for q, c in contexts.items()}, contexts, msa.FIXTURE_SHOTS)
    record, template = _record_and_executed(contexts, msa.FIXTURE_SHOTS)
    distributions = _distributions(counts)
    executed = {name: template["_template"] for name in distributions}
    result = msa.collected(record, distributions, executed, msa.DEMONSTRATION_SCATTER_FLOOR)
    check("withheld" not in result, f"{result.get('withheld')}")
    check(result["schema"] == msa.SCHEMA and sorted(result["qubits"]) == sorted(str(q) for q in contexts))
    check(result["device"]["mutation_test_passes"] and not any(msa.device_flags(result["device"]).values()))
    direct = msa.analyze_members(counts, contexts, msa.DEMONSTRATION_SCATTER_FLOOR)
    for q in contexts:
        a, b = result["qubits"][str(q)], direct["qubits"][str(q)]
        check(math.isclose(a["departure_n16"]["measured"], b["departure_n16"]["measured"], abs_tol=1e-9))


def test_collected_withholds_without_evidence() -> None:
    contexts = msa.fixture_contexts(FEW)
    counts = msa.device_counts({q: msa.device_model(c) for q, c in contexts.items()}, contexts, msa.FIXTURE_SHOTS)
    record, template = _record_and_executed(contexts, msa.FIXTURE_SHOTS)
    distributions = _distributions(counts)
    executed = {name: template["_template"] for name in distributions}
    missing = {k: v for k, v in distributions.items() if k != msa.ro0_name(FEW[0])}
    check("missing measured members" in msa.collected(record, missing, executed, FLOOR)["withheld"])
    short = {k: v for k, v in distributions.items() if k != f"msq_delay_n4_pa_q{FEW[0]}"}
    check("missing measured members" in msa.collected(record, short, executed, FLOOR)["withheld"])
    bare = {name: {"shots": msa.FIXTURE_SHOTS} for name in distributions}
    check("no execution-time calibration" in msa.collected(record, distributions, bare, FLOOR)["withheld"])
    skewed = {k: [np.asarray(v[0]) * 0.99] for k, v in distributions.items()}
    check("whole-shot count" in msa.collected(record, skewed, executed, FLOOR)["withheld"])


def test_collected_withholds_without_a_bound_floor(monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> None:
    contexts = msa.fixture_contexts(FEW)
    counts = msa.device_counts({q: msa.device_model(c) for q, c in contexts.items()}, contexts, msa.FIXTURE_SHOTS)
    record, template = _record_and_executed(contexts, msa.FIXTURE_SHOTS)
    record["groups"] = [{"backend": "ibm_kingston"}]
    distributions = _distributions(counts)
    executed = {name: template["_template"] for name in distributions}
    monkeypatch.setattr(msa, "MODEL_SCATTER_DIAGNOSTIC_SHA256", None)
    check("no model scatter floor" in msa.collected(record, distributions, executed)["withheld"])
    document = tmp_path / "scatter-floor.json"
    body = json.dumps({"schema": msa.SCATTER_FLOOR_SCHEMA, "floor": 0.02, "backend": "ibm_kingston"}).encode()
    document.write_bytes(body)
    monkeypatch.setattr(msa, "MODEL_SCATTER_FLOOR_FILE", str(document))
    monkeypatch.setattr(msa, "MODEL_SCATTER_DIAGNOSTIC_SHA256", "0" * 64)
    check("hashes to" in msa.collected(record, distributions, executed)["withheld"])
    monkeypatch.setattr(msa, "MODEL_SCATTER_DIAGNOSTIC_SHA256", hashlib.sha256(body).hexdigest())
    result = msa.collected(record, distributions, executed)
    check("withheld" not in result, f"{result.get('withheld')}")
    check(all(row["model_scatter_floor"] == 0.02 for row in result["qubits"].values()))
    other = {**record, "groups": [{"backend": "ibm_marrakesh"}]}
    check("not on" in msa.collected(other, distributions, executed)["withheld"])


def test_flip_counts_follow_the_joint_law() -> None:
    qubit = 5
    executed = {}
    distributions = {}
    for steps in de.MSQ_MEASURE_STEPS:
        for name in msa.member_names("measure", steps, qubit):
            distributions[name] = [de.msq_measure_law(steps)]
            executed[name] = {"shots": 1_000_000}
    counts = msa.member_counts_from_distributions(distributions, executed, [qubit])[qubit]
    for steps in de.MSQ_MEASURE_STEPS:
        name = msa.member_names("measure", steps, qubit)[0]
        flips, pairs = counts["flips"][name]
        check(pairs == 1_000_000 * (steps - 1))
        check(abs(flips / pairs - msa.ideal_flip(steps)) < 1e-5, f"N = {steps}: {flips / pairs}")
        agree, shots = counts["repeat_read"][name]
        check(shots == 1_000_000 and abs(agree / shots - 1.0) < 1e-12, "the ideal final read repeats the last bit")
        ones, total = counts["final"][name]
        check(abs(ones / total - (1 - msa.ideal_measure(steps))) < 1e-5)


class _Runtime:
    def __init__(self, reason: str | None) -> None:
        self.reason = reason
        self.seen: list[str] = []

    def _comparisons_withheld(self, names: list[str], executed: dict[str, Any]) -> str | None:
        self.seen = names
        return self.reason


def test_measured_family_attaches_the_pinching_analysis(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(qpu_planning, "_measured_contracts", lambda *a, **k: {"observables": ["precision"]})
    marker = {"schema": msa.SCHEMA, "device": {}}
    monkeypatch.setattr(msa, "collected", lambda record, distributions, executed: marker)
    record = {"family_configuration": {"name": "measurement-sequence"}}
    distributions = {"msq_ro0_q1": [np.zeros(2)], "other": [np.zeros(2)]}
    runtime = _Runtime(None)
    result = qpu_planning.measured_family(record, distributions, {}, runtime)
    check(result == {"observables": ["precision"], "pinching": marker}, f"{result}")
    check(runtime.seen == ["msq_ro0_q1"])
    withheld = qpu_planning.measured_family(record, distributions, {}, _Runtime("calibration changed"))
    check(withheld["pinching"] == {"schema": msa.SCHEMA, "withheld": "calibration changed"})
    check(withheld["observables"] == ["precision"])
    other = qpu_planning.measured_family({"family_configuration": {"name": "x"}}, distributions, {}, runtime)
    check(other == {"observables": ["precision"]})


def _chain_z(arm: str, sign: int, **gate: float) -> float:
    ctx = msa.fixture_contexts((91,))[91]
    t1, q = ctx["t1_cal_s"], 1.03
    chain = msa.chain_matrix(
        arm, 16, t1, min(ctx["t2_s"], 2 * t1), msa.tau_of(arm, ctx, 0.5), 0.0, msa.sx_gate(ctx, **gate), 1.0, sign
    )
    return float(chain[2, 2] + chain[2, 3] * q)


def test_axis_tilt_is_odd_under_the_sign_and_the_pool_is_even() -> None:
    """The relative axis tilt maps the sign -1 chain at d onto the sign +1 chain at -d, so the equal-weight pool of the
    members +, -, -, + has no first-order term; the other classes do not depend on the sign."""
    ctx = msa.fixture_contexts((91,))[91]
    t1, q = ctx["t1_cal_s"], 1.03
    t2 = min(ctx["t2_s"], 2 * t1)
    for arm in ("unitary", "measure"):
        tau = msa.tau_of(arm, ctx, 0.5)
        for d in (0.003, 0.02):
            plus, minus = _chain_z(arm, 1, axis_phase=d), _chain_z(arm, -1, axis_phase=d)
            check(math.isclose(minus, _chain_z(arm, 1, axis_phase=-d), abs_tol=1e-12), f"{arm} d={d}: not a reflection")
            check(abs(plus - minus) > 1e-2 * d / 0.02, f"{arm} d={d}: the two signs agree: {plus} {minus}")
            explicit = (plus + minus) / 2
            gate = msa.sx_gate(ctx, axis_phase=d)
            pooled = msa.corrected_z(arm, 16, t1, t2, tau, 0.0, gate, q)
            check(math.isclose(pooled, explicit, abs_tol=1e-12), f"{arm} d={d}: {pooled} {explicit}")
            even = msa.corrected_z(arm, 16, t1, t2, tau, 0.0, msa.sx_gate(ctx, axis_phase=-d), q)
            check(math.isclose(pooled, even, abs_tol=1e-12), f"{arm} d={d}: the pool is not even")
        for name, value in (("shift", 0.0005), ("dephasing_scale", 3.0), ("angle_error", 0.02)):
            check(
                math.isclose(_chain_z(arm, 1, **{name: value}), _chain_z(arm, -1, **{name: value}), abs_tol=1e-12),
                f"{arm}: {name} depends on the sign",
            )


def test_injected_axis_tilt_generates_each_member_from_its_own_sign() -> None:
    contexts = msa.fixture_contexts(FEW, floor=None)
    ctx = contexts[FEW[0]]
    model = msa.device_model(ctx, axis_phase=0.005)
    final = msa.device_counts({FEW[0]: model}, contexts, msa.FIXTURE_SHOTS)[FEW[0]]["final"]
    t2 = min(model["t2_s"], 2 * model["t1_s"])
    for tag, sign in (("pa", 1), ("ma", -1), ("mb", -1), ("pb", 1)):
        z = msa.bloch_z(
            "unitary",
            16,
            model["t1_s"],
            t2,
            0.0,
            0.0,
            1 - 2 * model["p_init"],
            msa.sx_gate(ctx, axis_phase=0.005),
            1.0,
            sign,
        )
        want = msa.expected_ones(z, 0.0, model, ctx["prereadout_s"], msa.FIXTURE_SHOTS)
        check(final[f"msq_unitary_n16_{tag}_q{FEW[0]}"] == want, f"{tag}: copied from another sign")
    check(final[f"msq_unitary_n16_pa_q{FEW[0]}"] != final[f"msq_unitary_n16_ma_q{FEW[0]}"])
    # The analysis pools the four members: a common tilt moves the pooled unitary P0 only at second order, well below
    # the first-order shift that the sign +1 chain alone shows.
    row = msa.evaluate_qubit((FEW[0], {"final": final}, contexts[FEW[0]]))
    residual = row["gate_systematic_n16"]["unitary_residual"]
    one_sign = (_chain_z("unitary", 1, axis_phase=0.005) - _chain_z("unitary", 1)) / 2
    check(abs(one_sign) > 0.01 and abs(residual) < 0.4 * abs(one_sign), f"pooled {residual}, one sign {one_sign}")


def test_registered_scatter_floor_is_bound_by_digest() -> None:
    """The registered diagnostic file hashes to the constant and gives the floor collected() uses on ibm_kingston."""
    path = Path(msa.__file__).resolve().parents[1] / msa.MODEL_SCATTER_FLOOR_FILE
    check(msa.MODEL_SCATTER_DIAGNOSTIC_SHA256 == hashlib.sha256(path.read_bytes()).hexdigest())
    floor, reason = msa.bound_floor({"ibm_kingston"})
    document = json.loads(path.read_text(encoding="utf-8"))
    if floor is None:
        raise AssertionError(str(reason))
    check(floor == document["floor"] and 0.01 < floor < 0.03, f"{floor}")
    other, why = msa.bound_floor({"ibm_marrakesh"})
    check(other is None and "not on" in str(why))


def test_collected_reads_the_registered_scatter_floor_on_kingston() -> None:
    contexts = msa.fixture_contexts(FEW)
    counts = msa.device_counts({q: msa.device_model(c) for q, c in contexts.items()}, contexts, msa.FIXTURE_SHOTS)
    record, template = _record_and_executed(contexts, msa.FIXTURE_SHOTS)
    record["groups"] = [{"backend": "ibm_kingston"}]
    distributions = _distributions(counts)
    executed = {name: template["_template"] for name in distributions}
    result = msa.collected(record, distributions, executed)
    check("withheld" not in result, f"{result.get('withheld')}")
    floor, _ = msa.bound_floor({"ibm_kingston"})
    check(all(row["model_scatter_floor"] == floor for row in result["qubits"].values()))
    record["groups"] = [{"backend": "ibm_marrakesh"}]
    check("not on" in msa.collected(record, distributions, executed)["withheld"])
