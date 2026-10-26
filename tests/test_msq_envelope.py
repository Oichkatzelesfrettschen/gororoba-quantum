"""The measurement-sequence envelope: layout rule, plan digest, replan count, fallback trigger and aggregate cap."""

from __future__ import annotations

import math
from typing import Any

import numpy as np
import pytest

import msq_envelope as env


def check(condition: bool, message: str = "check failed") -> None:
    """Raise on a false condition; python -O strips assert, so a check raises explicitly."""
    if not condition:
        raise AssertionError(message)


def row(readout: float, **overrides: float | None) -> dict[str, float | None]:
    values: dict[str, float | None] = {
        "readout_error": readout,
        "sx_error": 2e-4,
        "t1_s": 2e-4,
        "t2_s": 1e-4,
        "prob_meas1_prep0": 0.005,
    }
    values.update(overrides)
    return values


def chain(n: int) -> tuple[dict[int, dict[str, float | None]], list[tuple[int, int]]]:
    """A path of n qubits whose readout error rises with the index, so the scan runs 0, 1, 2, ..."""
    return {q: row(0.001 + 1e-5 * q) for q in range(n)}, [(q, q + 1) for q in range(n - 1)]


def test_layout_keeps_graph_distance_three() -> None:
    qubits, edges = chain(60)
    layout = env.layout_rule(qubits, (), edges, 16)
    check(layout == [3 * k for k in range(16)], f"distance-3 scan of a path keeps every third qubit: {layout}")


def test_layout_distance_two_is_refused() -> None:
    qubits, edges = chain(5)
    near = env.coupling_distances(edges, 0, env.RULE_MIN_GRAPH_DISTANCE - 1)
    check(sorted(near) == [0, 1, 2], f"distance-2 neighborhood of a path end: {sorted(near)}")


def test_layout_orders_by_readout_then_index() -> None:
    qubits, edges = chain(60)
    qubits[30]["readout_error"] = 1e-4
    qubits[45]["readout_error"] = 1e-4
    layout = env.layout_rule(qubits, (), edges, 16)
    check(layout[:2] == [30, 45], f"lowest readout error first, ties by index: {layout[:2]}")


@pytest.mark.parametrize(
    "field, value",
    [
        ("readout_error", 0.011),
        ("sx_error", 1.1e-3),
        ("t1_s", 19e-6),
        ("t2_s", 19e-6),
        ("prob_meas1_prep0", 0.021),
        ("prob_meas1_prep0", None),
        ("prob_meas1_prep0", math.nan),
    ],
)
def test_layout_screens_each_threshold(field: str, value: float | None) -> None:
    check(env.qubit_eligibility(row(0.005, **{field: value})) is not None, f"{field}={value} must fail the rule")
    check(env.qubit_eligibility(row(0.005)) is None, "the base row is eligible")


def test_layout_respects_exclusions_and_refuses_short() -> None:
    qubits, edges = chain(60)
    layout = env.layout_rule(qubits, {0}, edges, 16)
    check(0 not in layout and layout[0] == 1, f"an excluded qubit is skipped: {layout[:3]}")
    with pytest.raises(env.EnvelopeError, match="only"):
        env.layout_rule(*chain(40)[:1], (), chain(40)[1], 16)
    with pytest.raises(env.EnvelopeError, match="tier"):
        env.layout_rule(qubits, (), edges, 20)


def plan(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "layout": [1, 4, 7],
        "qpy_sha256": "a" * 64,
        "execution_pubs": [{"name": "p", "components": []}],
        "sampler_options": {"init_qubits": True, "twirling": False},
        "rep_delay": 2e-5,
        "shots": 8192,
        "planner_seconds": 14.2,
    }
    base.update(overrides)
    return base


@pytest.mark.parametrize(
    "field, value",
    [
        ("layout", [1, 4, 8]),
        ("qpy_sha256", "b" * 64),
        ("execution_pubs", [{"name": "q", "components": []}]),
        ("sampler_options", {"init_qubits": True, "twirling": True}),
        ("rep_delay", 5e-5),
        ("planner_seconds", 14.3),
    ],
)
def test_plan_digest_moves_with_every_plan_field(field: str, value: Any) -> None:
    check(env.plan_digest(plan()) != env.plan_digest(plan(**{field: value})), f"{field} must move the digest")
    check(env.plan_digest(plan()) == env.plan_digest(plan()), "the digest is deterministic")


def test_plan_digest_requires_every_field() -> None:
    incomplete = plan()
    del incomplete["sampler_options"]
    with pytest.raises(env.EnvelopeError, match="sampler_options"):
        env.plan_digest(incomplete)


def test_replan_count_counts_any_digest_change() -> None:
    check(env.count_replans(["a", "a", "b", "b", "c", "d"]) == 3, "three changes are allowed")
    with pytest.raises(env.EnvelopeError, match="4 times"):
        env.count_replans(["a", "b", "c", "d", "e"])


@pytest.mark.parametrize(
    "status, code, circuit_ns, billed, permitted",
    [
        ("ERROR", 1305, 0, 2.0, True),  # the zero-delay jobs: no circuit, overhead billed
        ("ERROR", 1305, None, 2.0, True),
        ("ERROR", 1305, 0, 5.0, False),  # billed past the overhead
        ("ERROR", 1305, 1_000_000, 2.0, False),  # executed circuit time: an overrun ceiling
        ("ERROR", 1305, 0, None, False),  # unattributed charge
        ("ERROR", 1602, 1_000_000, 5.0, True),
        ("ERROR", 8030, None, None, True),
        ("ERROR", 8045, 0, 2.0, False),
        ("ERROR", None, 0, 2.0, False),
        ("DONE", None, 1_000_000, 4.0, False),
        ("CANCELLED", 1305, 0, 2.0, False),
    ],
)
def test_fallback_trigger(status: str, code: int | None, circuit_ns: int | None, billed: float | None, permitted: bool):
    check(
        env.fallback_permitted(status, code, circuit_ns, billed) is permitted, f"{status} {code} {circuit_ns} {billed}"
    )


def test_aggregate_cap_bounds_both_attempts() -> None:
    check(env.attempt_admission(1, 400.0, 60.0, 40.0, 20.0) == [], "attempt 1 admitted with the cap available")
    check(env.attempt_admission(1, 90.0, 60.0, 40.0, 20.0) != [], "attempt 1 needs the whole cap")
    check(env.attempt_admission(2, 400.0, 60.0, 40.0, 20.0, 20.0) == [], "attempt 2 within the cap")
    check(env.attempt_admission(2, 400.0, 60.0, 40.0, 20.0, 20.5) != [], "attempt 1 charge plus ceiling past the cap")
    check(env.attempt_admission(2, 75.0, 60.0, 40.0, 20.0, 2.0) != [], "attempt 2 ceiling past the quota")
    check(env.attempt_admission(1, 400.0, 60.0, 40.0, 20.0, 2.0) != [], "attempt 1 has no earlier charge")
    check(env.attempt_admission(3, 400.0, 60.0, 40.0, 20.0) != [], "no third attempt")
    check(env.attempt_admission(1, math.inf, 60.0, 40.0, 20.0) != [], "non-finite input refused")


def test_canonical_snapshot_is_order_free() -> None:
    first = env.canonical_snapshot({"b": 1, "a": [1, 2]}, {"q": {"x": 0.5}}, 3)
    second = env.canonical_snapshot({"a": [1, 2], "b": 1}, {"q": {"x": 0.5}}, 3)
    check(first == second, "key order must not move the canonical bytes")
    with pytest.raises(env.EnvelopeError):
        env.canonical_snapshot({}, {}, -1)


def envelope_groups(qubits: list[int]) -> list[Any]:
    import diagnostic_experiments as de

    per = {q: 545 for q in qubits}
    return de.msqe_groups(
        qubits, per, {q: 500 for q in qubits}, {q: 500 for q in qubits}, [0, 5000, 12500, 25000, 50000]
    )


def test_envelope_new_members_match_their_exact_oracle() -> None:
    """The reset controls, the patterns and a terminal-reset member of each arm against the exact oracle; planning
    proves every compiled member (qpu_planning.check_compiled_ideals), the 16-step members included."""
    import qpu_planning

    groups = envelope_groups([3, 9])
    for group in groups:
        for member in group.members:
            if member.circuit.num_clbits > 3:
                continue
            law = qpu_planning.ideal_compiled_probabilities(member.circuit)
            check(
                bool(np.allclose(law, member.ideal, rtol=0, atol=1e-10)),
                f"{member.name}: exact oracle {law} differs from the labeled ideal {member.ideal}",
            )


def test_envelope_members_are_dynamic_and_end_in_reset() -> None:
    import local_compute

    for group in envelope_groups([3, 9]):
        for member in group.members:
            check(local_compute.is_dynamic(member.circuit), f"{member.name} must run in the dynamic job")
            last = member.circuit.data[-1].operation.name
            check(last == "reset", f"{member.name} must end in a reset, ends in {last}")


def test_envelope_rows_align_across_qubits() -> None:
    import diagnostic_experiments as de

    groups = envelope_groups([3, 9, 27])
    base = 4 * len(de.MSQ_STEPS) + 4 + 1 + len(de.MSQ_T1_MICROSECONDS) + 4 * len(de.MSQ_DYNAMIC_STEPS) + 4
    patterns = de.MSQE_PATTERN_DESIGNS[16][0]
    lengths = {len(group.members) for group in groups}
    check(lengths == {base + 2 + patterns}, f"members per qubit {lengths}")
    for row in range(base + 2 + patterns):
        stems = {group.members[row].name.rsplit("_q", 1)[0] for group in groups}
        check(len(stems) == 1, f"row {row} fuses different members {stems}")


@pytest.mark.parametrize("width", [16, 24, 32, 5])
def test_envelope_patterns_are_an_orthogonal_design(width: int) -> None:
    """Every column holds K / 2 ones and every two columns agree in exactly K / 2 rows, so within either own state
    every other qubit sits in |1> in exactly K / 4 patterns; identical or complementary columns cannot occur."""
    import diagnostic_experiments as de

    bits = np.asarray(de.msqe_pattern_bits(width))
    order = de.MSQE_PATTERN_DESIGNS[de.msqe_pattern_tier(width)][0]
    check(bits.shape == (order, width), f"shape {bits.shape}")
    signs = 1 - 2 * bits
    check(bool((signs.sum(axis=0) == 0).all()), "a column is unbalanced")
    gram = signs.T @ signs
    check(bool((gram == order * np.eye(width, dtype=np.int64)).all()), "two columns are not orthogonal")
    for target in range(width):
        for state in (0, 1):
            rows = bits[:, target] == state
            for other in range(width):
                if other != target:
                    ones = int(bits[rows, other].sum())
                    check(ones == order // 4, f"rank {other} is in |1> {ones} times at rank {target} state {state}")


def test_envelope_pattern_design_refuses_bad_inputs() -> None:
    import diagnostic_experiments as de

    with pytest.raises(ValueError):
        de.msqe_pattern_bits(de.MSQE_MAX_WIDTH + 1)
    with pytest.raises(ValueError):
        de.paley_hadamard(1, 13)


def test_envelope_leaves_the_main_family_unchanged() -> None:
    import diagnostic_experiments as de

    static, dynamic = de.msq_members(5, 545, 500, 500, (0, 5000, 12500, 25000, 50000))
    check(
        all(m.circuit.data[-1].operation.name == "measure" for m in (*static, *dynamic)),
        "the main family gained a reset",
    )


def test_job_error_code_parses_the_service_text() -> None:
    import live_run

    check(live_run.job_error_code("Error code 1305; Job ran longer than 5 s.") == 1305, "1305")
    check(live_run.job_error_code("error code 8030: Repetition delay not supported") == 8030, "8030")
    check(live_run.job_error_code(None) is None and live_run.job_error_code("no code") is None, "absent code")


def test_recovery_tags_separate_attempts_and_keep_retained_tags() -> None:
    import live_run

    base = ("2026-10-26T00:00:00+00:00", "ibm_kingston", "dynamic", 1, 1, [{"name": "p"}], "a" * 64)
    retained = live_run._recovery_tags(*base)
    first = live_run._recovery_tags(*base, {"rep_delay": 2e-5, "attempt_index": 1, "envelope_sha256": "e" * 64})
    second = live_run._recovery_tags(*base, {"rep_delay": 5e-5, "attempt_index": 2, "envelope_sha256": "e" * 64})
    check(retained == live_run._recovery_tags(*base, None), "a record without an attempt keeps its tags")
    check(len({retained[2], first[2], second[2]}) == 3, "each attempt has its own batch tag")
    with pytest.raises(live_run.LiveRunError):
        live_run._recovery_tags(*base, {"attempt_index": 1})


def approved_envelope(tmp_path: Any, **record_overrides: Any) -> tuple[Any, str, dict[str, Any]]:
    import hashlib
    import json

    import live_run

    record: dict[str, Any] = {
        "state": "planned",
        "experiment_digest": "d" * 64,
        "schema_version": 9,
        "shots": 8192,
        "policy": {"rep_delay_seconds": 2e-5, "max_execution_seconds": 30.0},
        "versions": {"qiskit": "2"},
        "instance_sha256_12": "i" * 12,
        "family_configuration": {
            "name": "measurement-sequence-envelope",
            "layout_width": 16,
            "layout_source": "msq_envelope.layout_rule",
            "qubits": list(range(16)),
            "arms": {"measure": "m"},
            "steps": [1, 2],
        },
        "envelope": {
            "contract": {
                "fallback_rep_delay_seconds": 5e-5,
                "ceiling_seconds": {"attempt_1": 30.0, "attempt_2": 60.0},
                "envelope_cap_seconds": 90.0,
            }
        },
        "groups": [{"backend": "ibm_kingston", "seed_transpiler": live_run.SEED_TRANSPILER}],
        "execution_pubs": [{"name": f"p{k}"} for k in range(3)],
    }
    record.update(record_overrides)
    directory = tmp_path / "approved"
    directory.mkdir()
    data = json.dumps(record).encode()
    (directory / "record.json").write_bytes(data)
    return directory, hashlib.sha256(data).hexdigest(), record


def test_envelope_mismatches_admit_a_moved_layout_only(tmp_path: Any) -> None:
    import copy

    import live_run

    directory, sha, approved = approved_envelope(tmp_path)
    fresh = copy.deepcopy(approved)
    fresh["family_configuration"]["qubits"] = list(range(100, 116))
    check(live_run.approved_envelope_mismatches(directory, fresh, sha) == [], "a moved layout stays inside")
    for mutate in (
        lambda r: r["policy"].update(rep_delay_seconds=5e-5),
        lambda r: r["family_configuration"].update(layout_width=24),
        lambda r: r["family_configuration"].update(qubits=list(range(15))),
        lambda r: r.update(experiment_digest="x" * 64),
        lambda r: r["envelope"]["contract"].update(envelope_cap_seconds=95.0),
        lambda r: r["groups"][0].update(backend="ibm_fez"),
        lambda r: r["execution_pubs"].pop(),
    ):
        changed = copy.deepcopy(fresh)
        mutate(changed)
        check(live_run.approved_envelope_mismatches(directory, changed, sha) != [], "a bound field moved")
    check(live_run.approved_envelope_mismatches(directory, fresh, "0" * 64) != [], "a wrong digest refuses")


def test_envelope_attempt_two_reads_the_fallback_delay_and_ceiling(tmp_path: Any) -> None:
    import copy

    import live_run

    directory, sha, approved = approved_envelope(tmp_path)
    second = copy.deepcopy(approved)
    second["envelope"]["attempt"] = 2
    second["policy"] = {"rep_delay_seconds": 5e-5, "max_execution_seconds": 60.0}
    check(live_run.approved_envelope_mismatches(directory, second, sha) == [], "attempt 2 policy matches")
    second["policy"]["max_execution_seconds"] = 61.0
    check(live_run.approved_envelope_mismatches(directory, second, sha) != [], "attempt 2 past its ceiling")


class FakeJob:
    def __init__(self, status: str, message: str | None, circuit_ns: int | None, billed: int | None) -> None:
        self._status, self._message = status, message
        usage = {"status": "complete", "qpu_charge_time_seconds": billed} if billed is not None else None
        self._metrics: dict[str, Any] = {"usage": usage} if usage else {}
        if circuit_ns is not None:
            self._metrics["circuits_execution_time_ns"] = circuit_ns
        self._billed = billed

    def status(self) -> str:
        return self._status

    def error_message(self) -> str | None:
        return self._message

    def metrics(self) -> dict[str, Any]:
        return self._metrics

    def usage(self, partial: bool = False) -> float:
        return float(self._billed or 0)


class FakeService:
    def __init__(self, job: FakeJob, remaining: float) -> None:
        self._job, self._remaining = job, remaining

    def job(self, job_id: str) -> FakeJob:
        return self._job

    def usage(self) -> dict[str, Any]:
        return {"usage_remaining_seconds": self._remaining}


@pytest.mark.parametrize(
    "job, remaining, admitted",
    [
        (FakeJob("ERROR", "Error code 1305; ran longer", None, 2), 400.0, True),
        (FakeJob("ERROR", "Error code 1305; ran longer", 1_000_000, 2), 400.0, False),
        (FakeJob("ERROR", "Error code 1305; ran longer", None, 5), 400.0, False),
        (FakeJob("ERROR", "Error code 8045; buffer", None, 2), 400.0, False),
        (FakeJob("DONE", None, 1_000_000, 4), 400.0, False),
        (FakeJob("ERROR", "Error code 1602; range", 0, 2), 400.0, True),
        (FakeJob("ERROR", "Error code 1305; ran longer", None, 2), 50.0, False),  # ceiling 2 past the quota
    ],
)
def test_envelope_fallback_setup(tmp_path: Any, job: FakeJob, remaining: float, admitted: bool) -> None:
    import argparse
    import json

    import live_run

    directory, sha, approved = approved_envelope(tmp_path)
    approved["envelope"]["contract"]["reserve_seconds"] = 0.0
    data = json.dumps(approved).encode()
    (directory / "record.json").write_bytes(data)
    import hashlib

    sha = hashlib.sha256(data).hexdigest()
    first = tmp_path / "first"
    first.mkdir()
    (first / "record.json").write_text(
        json.dumps(
            {
                "shots": 8192,
                "approved_record": {"run": "approved", "record_sha256": sha, "envelope": True},
                "submission": {"jobs": [{"job_id": "j1", "pubs": [{"name": "p"}]}]},
            }
        )
    )
    args = argparse.Namespace(envelope_fallback=first)
    if admitted:
        evidence = live_run.envelope_fallback_setup(FakeService(job, remaining), args)
        check(args.rep_delay == 5e-5 and args.max_execution_seconds == 60.0 and args.submit, "attempt 2 settings")
        check(args.envelope_attempt["attempt_index"] == 2 and evidence["attempt_1_job"] == "j1", "attempt identity")
    else:
        with pytest.raises(live_run.LiveRunError):
            live_run.envelope_fallback_setup(FakeService(job, remaining), args)


def test_reset_screen_is_an_equivalence_bound() -> None:
    import msq_envelope_analysis as ea

    ro0, ro1 = (80, 8192), (8100, 8192)
    clean = ea.reset_screen((90, 8192), (82, 8192), ro0, ro1, 16)
    check(clean["passes"] and clean["upper_bound"] < ea.RESET_MARGIN, f"a near-zero residual passes: {clean}")
    leaky = ea.reset_screen((160, 8192), (82, 8192), ro0, ro1, 16)
    check(not leaky["passes"], f"a 0.01 residual difference fails: {leaky}")
    # An estimate below the margin whose upper bound crosses it still fails: the rule demands equivalence.
    edge = ea.reset_screen((82 + 60, 8192), (82, 8192), ro0, ro1, 32)
    check(edge["difference"] < ea.RESET_MARGIN and not edge["passes"], f"the bound, not the estimate, decides: {edge}")
    check(not ea.reset_screen((90, 8192), (82, 8192), ro1, ro0, 16)["passes"], "a reversed contrast fails")


def test_pattern_screen_reads_each_own_state_separately() -> None:
    import msq_envelope_analysis as ea

    bits = [0, 1] * 10
    asymmetric = [(80, 8192) if b == 0 else (8192 - 160, 8192) for b in bits]
    result = ea.pattern_screen(bits, asymmetric, 16)
    check(result["passes"], f"P(1|0) != P(0|1) alone is not crosstalk: {result['states']}")
    shifted = [(80 + (60 if k % 4 == 0 else 0), 8192) if b == 0 else (8192 - 160, 8192) for k, b in enumerate(bits)]
    check(not ea.pattern_screen(bits, shifted, 16)["passes"], "a configuration-dependent shift fails")
    flat = [(0, 8192) if b == 0 else (8192, 8192) for b in bits]
    check(ea.pattern_screen(bits, flat, 16)["states"]["0"]["statistic"] == 0.0, "a zero error rate tests nothing")


def eligible_evidence(**overrides: float) -> dict[str, Any]:
    coherence = {"T1": 200.0, "T2": 100.0, "readout_error": 0.005, "prob_meas1_prep0": 0.004}
    gate = {"sx_error": 2e-4, "sx_duration_s": 3.2e-8, "measure_duration_s": 2.2e-6}
    coherence.update({k: v for k, v in overrides.items() if k in coherence})
    gate.update({k: v for k, v in overrides.items() if k in gate})
    return {"placed_qubit_calibration": {"7": coherence}, "placed_gate_calibration": {"7": gate}}


def test_execution_eligibility_fails_closed() -> None:
    import msq_envelope_analysis as ea

    good = {"a_q7": eligible_evidence(), "b_q7": eligible_evidence()}
    check(ea.execution_eligibility(good, 7, ["a_q7", "b_q7"]) is None, "an eligible qubit passes")
    check(ea.execution_eligibility({"a_q7": eligible_evidence(readout_error=0.02)}, 7, ["a_q7"]) is not None, "ro")
    check(ea.execution_eligibility({"a_q7": eligible_evidence(T2=10.0)}, 7, ["a_q7"]) is not None, "T2")
    moved = {"a_q7": eligible_evidence(), "b_q7": eligible_evidence(readout_error=0.006)}
    check(ea.execution_eligibility(moved, 7, ["a_q7", "b_q7"]) is not None, "a calibration change between PUBs")
    check(ea.execution_eligibility({"a_q7": {}}, 7, ["a_q7"]) is not None, "missing evidence fails")


def test_count_rule_scales_with_width() -> None:
    import msq_envelope_analysis as ea

    check([ea.count_rule(w) for w in (8, 16, 24, 32)] == [2, 2, 3, 4], "max(2, ceil(0.1 W))")


def test_null_upper_bound_is_clopper_pearson() -> None:
    import msq_envelope_null as null

    check(abs(null.upper_bound(0, 400) - (1 - 0.05 ** (1 / 400))) < 1e-12, "zero fires: 1 - alpha^(1/n)")
    check(null.upper_bound(0, 300) >= null.FALSE_FIRE_CEILING, "300 clean replicates cannot reach 0.01")
    check(null.upper_bound(0, 400) < null.FALSE_FIRE_CEILING, "400 clean replicates reach 0.01")
    check(null.upper_bound(5, 5) == 1.0, "all fired")
