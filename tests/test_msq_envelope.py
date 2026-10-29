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
    check({30, 45} <= set(layout) and 29 not in layout and 31 not in layout, f"low readout error keeps first: {layout}")
    check(layout == sorted(layout), "the kept set returns in index order")
    qubits[30]["readout_error"], qubits[45]["readout_error"] = 2e-4, 1e-4
    check(env.layout_rule(qubits, (), edges, 16) == layout, "a reordering among kept qubits moves nothing")


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
    # An unsettled attempt 1 is not yet deducted from the reported quota, so attempt 2 also needs its ceiling there.
    check(env.attempt_admission(2, 85.0, 60.0, 40.0, 20.0, 20.0) == [], "a settled attempt 1 is already deducted")
    check(
        env.attempt_admission(2, 85.0, 60.0, 40.0, 20.0, 20.0, earlier_unsettled=True) != [],
        "an unsettled attempt 1 counts against the reserve",
    )
    check(env.attempt_admission(2, 100.0, 60.0, 40.0, 20.0, 20.0, earlier_unsettled=True) == [], "both fit")


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
    import qpe_diagnostics

    groups = envelope_groups([3, 9])
    for group in groups:
        for member in group.members:
            if member.circuit.num_clbits > 3:
                continue
            law = qpe_diagnostics.ideal_compiled_probabilities(member.circuit)
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


def test_batch_replan_returns_the_record_to_its_admitted_plan() -> None:
    import live_run

    record: dict[str, Any] = {"state": "submission_started", "submission": {"jobs": [], "planned_jobs": [{}]}}
    checkpoints: list[str] = []
    with pytest.raises(live_run.EnvelopeReplan):
        live_run.envelope_batch_replan(
            record, "ibm_kingston: dynamic-1-of-1", "a" * 64, ["layout moved"], lambda: checkpoints.append("x")
        )
    check(record["state"] == "planned", "the next submit() pass meets its planned-state guard")
    check("submission" not in record, "the unsent ledger is dropped")
    check(checkpoints == ["x"], "the restored record reaches disk before the retry")
    check(record["envelope"]["replan_snapshots"][0]["snapshot_sha256"] == "a" * 64, "the moved snapshot is kept")
    check("batch_snapshots" not in record["envelope"], "the moved snapshot claims no sent layout")


def test_batch_replan_refuses_after_an_earlier_batch_was_sent() -> None:
    import live_run

    record: dict[str, Any] = {"state": "submission_started", "submission": {"jobs": [{"job_id": "j1"}]}}
    with pytest.raises(live_run.LiveRunError):
        live_run.envelope_batch_replan(record, "ibm_kingston: dynamic-2-of-2", "b" * 64, ["moved"], lambda: None)
    check(record["state"] == "submission_started" and "submission" in record, "a sent run keeps its ledger")


def test_check_envelope_replays_superseded_planning_snapshots(tmp_path: Any) -> None:
    import json
    import shutil
    from pathlib import Path

    import live_run

    retained = Path(__file__).resolve().parent.parent / "results/live/2026-10-27T012214.435220Z"
    source = json.loads((retained / "record.json").read_text())
    digest = source["envelope"]["planning_snapshot_sha256"]
    layout = source["family_configuration"]["qubits"]
    run = tmp_path / "run"
    (run / live_run.ENVELOPE_SNAPSHOT_DIRECTORY).mkdir(parents=True)
    shutil.copy(
        retained / live_run.ENVELOPE_SNAPSHOT_DIRECTORY / f"{digest}.json",
        run / live_run.ENVELOPE_SNAPSHOT_DIRECTORY / f"{digest}.json",
    )

    def violations(superseded_layout: list[int]) -> list[str]:
        record = {
            "family_configuration": {"layout_width": 32, "qubits": layout},
            "envelope": {
                "planning_snapshot_sha256": digest,
                "superseded_planning": [{"snapshot_sha256": digest, "layout": superseded_layout}],
                "replan_snapshots": [{"batch": "b", "snapshot_sha256": "c" * 64, "moved": ["x"]}],
            },
        }
        (run / "record.json").write_text(json.dumps(record))
        return live_run.envelope_layout_violations(run)

    check(violations(layout) == [], "a superseded snapshot replays the layout it produced")
    found = violations(layout[1:] + [155])
    check(len(found) == 1 and found[0].startswith("superseded planning 0"), f"{found}")


RETAINED_DRY_RUN = "results/live/2026-10-27T012214.435220Z"


def retained_snapshot() -> tuple[dict[str, Any], dict[str, Any]]:
    """The width-32 dry run's record and its planning snapshot document."""
    import json
    from pathlib import Path

    run = Path(__file__).resolve().parent.parent / RETAINED_DRY_RUN
    record = json.loads((run / "record.json").read_text())
    digest = record["envelope"]["planning_snapshot_sha256"]
    return record, json.loads((run / "envelope-snapshots" / f"{digest}.json").read_text())


def test_canonical_graph_drops_couplers_the_runtime_target_drops() -> None:
    import json

    _, document = retained_snapshot()
    date = "2026-10-26T00:00:00-07:00"
    cz = next(g for g in document["properties"]["gates"] if g["gate"] == "cz" and 72 not in g["qubits"])
    cz["parameters"].append({"date": date, "name": "operational", "unit": "", "value": 0})
    before = {tuple(edge) for edge in env.calibration_from_canonical(json.dumps(document).encode())["edges"]}
    document["properties"]["qubits"][72].append({"date": date, "name": "operational", "unit": "", "value": 0})
    rows = env.calibration_from_canonical(json.dumps(document).encode())
    edges = {tuple(edge) for edge in rows["edges"]}
    check(72 in rows["excluded"], "a non-operational qubit is excluded")
    check(not any(72 in edge for edge in edges), "the Target drops every cz on a non-operational qubit")
    # The Target drops only the named orientation of a non-operational cz and keeps its reverse, so the coupler stays.
    check(tuple(sorted(cz["qubits"])) in edges, "the reverse orientation keeps the coupler")
    check(edges == {edge for edge in before if 72 not in edge}, "only qubit 72's couplers leave")


def test_check_envelope_applies_operator_exclusions(tmp_path: Any) -> None:
    import json
    import shutil
    from pathlib import Path

    import live_run

    record, _ = retained_snapshot()
    source = Path(__file__).resolve().parent.parent / RETAINED_DRY_RUN
    run = tmp_path / "run"
    shutil.copytree(source / live_run.ENVELOPE_SNAPSHOT_DIRECTORY, run / live_run.ENVELOPE_SNAPSHOT_DIRECTORY)
    layout = record["family_configuration"]["qubits"]
    base = {
        "family_configuration": {"layout_width": 32, "qubits": layout},
        "envelope": {"planning_snapshot_sha256": record["envelope"]["planning_snapshot_sha256"]},
    }
    (run / "record.json").write_text(json.dumps(base))
    check(live_run.envelope_layout_violations(run) == [], "the retained layout replays")
    excluded = {**base, "policy": {"operator_excluded_qubits": {"ibm_kingston": [layout[0]]}}}
    (run / "record.json").write_text(json.dumps(excluded))
    found = live_run.envelope_layout_violations(run)
    check(len(found) == 1 and found[0].startswith("planning: the rule"), f"an excluded qubit moves the rule: {found}")


def test_approved_structure_resolves_shared_ideal_laws() -> None:
    import live_run

    law = {"encoding": "support", "length": 4, "support": {"0": 0.5, "3": 0.5}}
    group = {"group": "g", "members": [{"name": "m", "ideal": {"law_sha256": "d" * 64}, "replicas": []}]}
    resolved = live_run._approved_structure(group, {"d" * 64: law})
    check(resolved["members"][0]["ideal"] == law, "a shared reference resolves to the encoded law")
    inline = live_run._approved_structure({**group, "members": [{"name": "m", "ideal": law, "replicas": []}]}, {})
    check(inline["members"][0]["ideal"] == law, "an inline law is unchanged")


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
        # An unbilled 1602 counts attempt 1's ceiling (30 s here) against the quota until it settles.
        (FakeJob("ERROR", "Error code 1602; range", 0, None), 400.0, True),
        (FakeJob("ERROR", "Error code 1602; range", 0, None), 80.0, False),
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


def test_send_admission_keeps_an_unbilled_attempt_reserved() -> None:
    import live_run

    contract = {
        "reserve_seconds": 0.0,
        "envelope_cap_seconds": 90.0,
        "ceiling_seconds": {"attempt_1": 30.0, "attempt_2": 60.0},
    }

    def record(billed: float | None) -> dict[str, Any]:
        return {"envelope": {"contract": contract, "attempt": 2, "fallback_evidence": {"billed_seconds": billed}}}

    check(live_run.envelope_send_refusals(record(None), 70.0) != [], "an unbilled attempt 1 needs 90 s, not 60 s")
    check(live_run.envelope_send_refusals(record(None), 90.0) == [], "both ceilings fit")
    check(live_run.envelope_send_refusals(record(2.0), 70.0) == [], "a billed attempt 1 is already deducted")
    first = {"envelope": {"contract": contract}}
    check(live_run.envelope_send_refusals(first, 90.0) == [], "attempt 1 needs the whole cap")
    check(live_run.envelope_send_refusals(first, 89.0) != [], "attempt 1 short of the cap")


def test_envelope_fallback_finds_the_approval_under_another_out(tmp_path: Any) -> None:
    import argparse
    import hashlib
    import json

    import live_run

    directory, _, approved = approved_envelope(tmp_path)
    approved["envelope"]["contract"]["reserve_seconds"] = 0.0
    data = json.dumps(approved).encode()
    (directory / "record.json").write_bytes(data)
    sha = hashlib.sha256(data).hexdigest()
    first = tmp_path / "submits" / "first"
    first.mkdir(parents=True)
    meta = {"run": "approved", "record_sha256": sha, "envelope": True}
    record = {"shots": 8192, "submission": {"jobs": [{"job_id": "j1", "pubs": [{"name": "p"}]}]}}
    (first / "record.json").write_text(json.dumps({**record, "approved_record": meta}))
    job = FakeJob("ERROR", "Error code 1305; ran longer", None, 2)
    with pytest.raises(live_run.LiveRunError, match="not retained beside attempt 1"):
        live_run.envelope_fallback_setup(FakeService(job, 400.0), argparse.Namespace(envelope_fallback=first))
    meta["relative_path"] = "../approved"
    (first / "record.json").write_text(json.dumps({**record, "approved_record": meta}))
    args = argparse.Namespace(envelope_fallback=first)
    live_run.envelope_fallback_setup(FakeService(job, 400.0), args)
    check(args.approved_record == first.parent / "../approved", "the relative path locates the approval")


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
    check(null.upper_bound(0, 298) >= null.FALSE_FIRE_CEILING, "298 clean replicates cannot reach 0.01")
    check(null.upper_bound(0, 299) < null.FALSE_FIRE_CEILING, "299 clean replicates reach 0.01")
    check(null.upper_bound(0, 400) < null.FALSE_FIRE_CEILING, "400 clean replicates reach 0.01")
    check(null.upper_bound(5, 5) == 1.0, "all fired")


def first_difference(a: Any, b: Any, path: str = "") -> str | None:
    """Where two nested results first differ, comparing floats by float.hex and arrays by their bytes."""
    if isinstance(a, dict) and isinstance(b, dict):
        if list(a) != list(b):
            return f"{path}: keys {list(a)} against {list(b)}"
        for key in a:
            found = first_difference(a[key], b[key], f"{path}/{key}")
            if found:
                return found
        return None
    if isinstance(a, np.ndarray) and isinstance(b, np.ndarray):
        same = a.dtype == b.dtype and a.shape == b.shape and a.tobytes() == b.tobytes()
        return None if same else f"{path}: array {a.tolist()} against {b.tolist()}"
    if isinstance(a, (list, tuple)) and type(a) is type(b):
        if len(a) != len(b):
            return f"{path}: length {len(a)} against {len(b)}"
        for i, (x, y) in enumerate(zip(a, b, strict=True)):
            found = first_difference(x, y, f"{path}[{i}]")
            if found:
                return found
        return None
    if isinstance(a, float) and isinstance(b, float):
        return None if a.hex() == b.hex() else f"{path}: {a!r} against {b!r}"
    return None if type(a) is type(b) and a == b else f"{path}: {a!r} against {b!r}"


def test_batched_sums_equal_builtin_and_numpy_rows() -> None:
    import msq_envelope_null as null

    generator = np.random.default_rng(null.NULL_SEED)
    scales = np.array([1e-300, 1e-9, 1.0, 1e9, 1e300, 0.0, -0.0])
    terms = generator.standard_normal((4, 4000)) * generator.choice(scales, size=(4, 4000))
    batched = null.neumaier_rows(list(terms))
    for k in range(4000):
        check(batched[k].hex() == sum(terms[:, k].tolist()).hex(), f"compensated sum of column {k}")
    for rows in (1, 2, 3, 5, 7, 64, 1000):
        block = generator.standard_normal((rows, 5)) * generator.choice(scales[:5], size=(rows, 5))
        check(
            all(a.hex() == np.sum(block[k]).hex() for k, a in enumerate(np.sum(block, axis=1).tolist())),
            f"np.sum over axis 1 of {rows} rows equals the sum of each row",
        )
    values = generator.standard_normal(5000) * 10.0
    squares = null.square_rows(values)
    check(all(a.hex() == (v**2).hex() for a, v in zip(squares.tolist(), values.tolist(), strict=True)), "pow squares")
    exps = null.exp_rows(values)
    check(all(a.hex() == math.exp(v).hex() for a, v in zip(exps.tolist(), values.tolist(), strict=True)), "exp")


def test_batched_minimizer_replays_scipy_bounded_brent() -> None:
    from scipy.optimize import minimize_scalar

    import msq_envelope_null as null

    generator = np.random.default_rng(null.NULL_SEED)
    count = 400
    center = generator.uniform(-8.0, -3.0, count)
    width = generator.uniform(0.05, 3.0, count)
    amplitude = generator.uniform(0.1, 2.0, count)
    family = generator.integers(0, 4, count)

    def objective(u: np.ndarray, rows: np.ndarray) -> np.ndarray:
        d = u - center[rows]
        shapes = [
            amplitude[rows] * d**2,
            amplitude[rows] * np.abs(d) + 0.01 * np.sin(40 * u),
            np.cosh(d * width[rows]) + 0.3 * np.sin(7 * u),
            amplitude[rows] * d**4 + np.exp(-(d**2)),
        ]
        return np.choose(family[rows], shapes)

    seen: dict[int, list[float]] = {row: [] for row in range(count)}

    def recorded(u: np.ndarray, rows: np.ndarray) -> np.ndarray:
        for x, row in zip(u.tolist(), rows.tolist(), strict=True):
            seen[row].append(x)
        return objective(u, rows)

    trace = null.SolverTrace()
    low, high = math.log(1e-6), math.log(1e-2)
    found = null.minimize_rows(recorded, count, low, high, 1e-10, trace)
    for row in range(count):
        points: list[float] = []

        def scalar(u: float, row: int = row, points: list[float] = points) -> float:
            points.append(u)
            return float(objective(np.array([u]), np.array([row]))[0])

        best = minimize_scalar(scalar, bounds=(low, high), method="bounded", options={"xatol": 1e-10})
        check(points == seen[row], f"row {row}: the objective sees SciPy's sequence of points")
        check(float(best.x).hex() == found[row].hex(), f"row {row}: the minimizer")
    for branch in (
        "parabolic",
        "parabolic_clamped",
        "parabolic_rejected",
        "golden",
        "better_up",
        "better_down",
        "worse_down",
        "worse_up",
        "worse_near",
        "worse_far",
    ):
        check(trace.counts.get(branch, 0) > 0, f"the rows take the {branch} branch")


def test_batched_brentq_replays_scipy_brentq() -> None:
    from scipy.optimize import brentq

    import msq_envelope_null as null

    generator = np.random.default_rng(null.NULL_SEED)
    count = 400
    root = generator.uniform(0.0, 0.5, count)
    scale = generator.uniform(0.5, 30.0, count)
    family = generator.integers(0, 4, count)

    def objective(x: np.ndarray, rows: np.ndarray) -> np.ndarray:
        d = x - root[rows]
        shapes = [
            -d * scale[rows],
            -np.sinh(scale[rows] * d),
            -np.tanh(scale[rows] * d) * np.exp(-3 * x),
            -d * (1 + scale[rows] * d**2),
        ]
        return np.choose(family[rows], shapes)

    seen: dict[int, list[float]] = {row: [] for row in range(count)}

    def recorded(x: np.ndarray, rows: np.ndarray) -> np.ndarray:
        for value, row in zip(x.tolist(), rows.tolist(), strict=True):
            seen[row].append(value)
        return objective(x, rows)

    trace = null.SolverTrace()
    found = null.brentq_rows(recorded, np.full(count, -0.05), np.full(count, 0.5), 1e-13, 1e-13, trace)
    for row in range(count):
        points: list[float] = []

        def scalar(x: float, row: int = row, points: list[float] = points) -> float:
            points.append(x)
            return float(objective(np.array([x]), np.array([row]))[0])

        expected = brentq(scalar, -0.05, 0.5, xtol=1e-13, rtol=1e-13)
        check(points == seen[row], f"row {row}: the objective sees SciPy's sequence of points")
        check(float(expected).hex() == found[row].hex(), f"row {row}: the root")
    for branch in ("interpolate", "extrapolate", "bisect_rejected", "bisect", "swap", "minimum_step"):
        check(trace.counts.get(branch, 0) > 0, f"the rows take the {branch} branch")
    with pytest.raises(ValueError):
        null.brentq_rows(lambda x, rows: x * 0 + 1.0, np.zeros(2), np.ones(2), 1e-13, 1e-13)


class NullFixture:
    """A width-8 null block with the scalar pipeline's rows, so the batched tests share one reference."""

    def __init__(self) -> None:
        import measurement_sequence_analysis as msa
        import msq_envelope_null as null

        floor, reason = msa.bound_floor({"ibm_kingston"})
        if floor is None:
            raise AssertionError(str(reason))
        self.width = 8
        self.contexts = null.null_contexts(self.width)
        self.slopes = {q: null.residual_slope(self.contexts[q]) for q in self.contexts}
        self.floor = floor
        self.seeds = np.random.SeedSequence(null.NULL_SEED).spawn(3)
        self.drawn = [null.draw(self.item(seed)) for seed in self.seeds]
        self.planned = msa.with_planning(self.contexts, floor)
        self.qubits = (0, 3, 5)
        self.rows = {
            q: [msa.evaluate_qubit((q, d.counts[q], self.planned[q])) for d in self.drawn] for q in self.qubits
        }
        self.replicates = [null.replicate_detail(self.item(seed)) for seed in self.seeds[:2]]

    def item(self, seed: Any) -> Any:
        return self.width, self.contexts, self.slopes, self.floor, seed


@pytest.fixture(scope="module")
def null_fixture() -> NullFixture:
    return NullFixture()


@pytest.mark.xdist_group("msq-null-batch")
def test_batched_qubit_rows_equal_scalar_rows_and_the_sum_mutant_differs(null_fixture: NullFixture) -> None:
    import msq_envelope_null as null

    fixture = null_fixture

    def mismatches() -> list[str]:
        found = []
        for q in fixture.qubits:
            rows = null.evaluate_qubit_rows(q, fixture.planned[q], [d.counts[q] for d in fixture.drawn])
            found += [m for a, b in zip(fixture.rows[q], rows, strict=True) if (m := first_difference(a, b))]
        return found

    check(mismatches() == [], "every field of every row has the scalar bits")
    original = null.neumaier_rows
    try:
        null.neumaier_rows = lambda terms: sum(terms[1:], terms[0] + 0.0)
        check(len(mismatches()) > 0, "uncompensated sums change a field of a row")
    finally:
        null.neumaier_rows = original


def test_batched_implied_loss_keeps_the_scalar_bits_inside_and_at_the_bracket_edges() -> None:
    import measurement_sequence_analysis as msa
    import msq_envelope_null as null

    ctx = null.null_contexts(1)[0]
    gate = msa.sx_gate(ctx)
    fraction = msa.WINDOW_RELAX_FRACTION
    tau = msa.tau_of("measure", ctx, fraction)
    q = 1 / (1 - 2 * msa.PLANNING_P_INIT)
    low, high = -0.05, 0.5
    cases = []
    for scale in (0.5, 1.0, 2.0):
        t1 = scale * ctx["t1_cal_s"]
        t2 = min(ctx["t2_s"], 2 * t1)
        ends = [msa.corrected_z("measure", msa.TOP_STEPS, t1, t2, tau, eps, gate, q) for eps in (low, high)]
        inside = [ends[0] + f * (ends[1] - ends[0]) for f in (0.1, 0.35, 0.5, 0.8, 0.97)]
        cases += [(t1, t2, z) for z in [ends[0] + 0.1, ends[0], ends[1], ends[1] - 0.1, *inside]]
    t1s, t2s, zs = (np.array(column) for column in zip(*cases, strict=True))
    expected = [msa.implied_loss(z, t1, t2, ctx, q, gate, fraction) for t1, t2, z in cases]
    sx = null.damped_sx(t1s, t2s, null.gate_rows(ctx, 0.0))
    got = null.implied_loss_rows(zs, t1s, t2s, ctx, np.full(len(cases), q), null.gate_rows(ctx, 0.0), fraction, sx)
    for k, (a, b) in enumerate(zip(expected, got.tolist(), strict=True)):
        check(a.hex() == b.hex(), f"row {k}: {a!r} against {b!r}")
    check(low in expected and high in expected, "the cases reach both bracket ends")
    check(any(low < e < high for e in expected), "the cases reach the root solve")


@pytest.mark.xdist_group("msq-null-batch")
def test_batched_block_equals_scalar_replicates(null_fixture: NullFixture) -> None:
    import msq_envelope_null as null

    fixture = null_fixture
    batched = null.analyse_block(fixture.item(fixture.seeds[:2]))
    for expected, got in zip(fixture.replicates, batched, strict=True):
        found = first_difference(list(expected), list(got))
        check(found is None, str(found))
    check(null.replicate_block(fixture.item(fixture.seeds[:1])) == [batched[0][0]], "record row of a block")
    withheld = null.analyse_block((4, null.null_contexts(4), fixture.slopes, fixture.floor, fixture.seeds[:1]))
    check(withheld[0][0]["withheld"] and withheld[0][1] is None, "fewer than MIN_KEPT qubits withhold")


def test_shared_laws_round_trip_and_leave_other_records() -> None:
    import live_run

    big = {"encoding": "support", "length": 1 << 17, "support": {str(k): 1.0 / 2000 for k in range(2000)}}
    members = [{"name": f"m_q{q}", "ideal": big} for q in range(3)] + [{"name": "small", "ideal": [0.5, 0.5]}]
    record = {"family_configuration": {"name": "measurement-sequence-envelope"}, "groups": [{"members": members}]}
    shared = live_run.shared_law_record(record)
    check(len(shared["ideal_laws"]) == 1, "three copies of one law share one entry")
    for original, stored in zip(members, shared["groups"][0]["members"], strict=True):
        check(live_run.stored_ideal(shared, stored) == live_run.stored_ideal(record, original), str(original["name"]))
    check(live_run.shared_law_record(shared) == shared, "sharing an already shared record changes nothing")
    other = {**record, "family_configuration": {"name": "measurement-sequence"}}
    check(live_run.shared_law_record(other) is other, "only envelope records share laws")
    with pytest.raises(live_run.LiveRunError):
        live_run.stored_ideal({}, shared["groups"][0]["members"][0])


# --- schema msq-envelope-v2: delay ladder, budget-derived ceilings, layout rule v2 ---------------------------------


def execution_fixture() -> dict[str, Any]:
    """Two PUBs of 1000 shots at 20 us; the planner charges 10 s of overhead and 5 s of circuit time per PUB."""
    pubs = [{"shots": 1000, "estimated_execution_seconds": 5.0, "repetition_delay_seconds": 20e-6} for _ in range(2)]
    return {"selected_job_costs": [{"overhead_seconds": 10.0, "pubs": pubs}]}


def v2_args(**overrides: Any) -> Any:
    import argparse

    values: dict[str, Any] = {
        "envelope_schema": env.ENVELOPE_SCHEMA,
        "rep_delay": env.REP_DELAY_LADDER_S[0],
        "max_total_execution_seconds": 140.0,
        "reserve_seconds": 60.0,
        "max_execution_seconds": None,
        "fallback_max_execution_seconds": None,
    }
    values.update(overrides)
    return argparse.Namespace(**values)


def test_ladder_and_ceiling_arithmetic() -> None:
    check(env.ENVELOPE_SCHEMA == "msq-envelope-v2" and env.ENVELOPE_SCHEMA_V1 == "msq-envelope-v1", "schema names")
    check(env.REP_DELAY_LADDER_S == (20e-6, 30e-6, 40e-6, 50e-6, 60e-6), f"ladder {env.REP_DELAY_LADDER_S}")
    check([env.delay_key(d) for d in env.REP_DELAY_LADDER_S] == ["2e-05", "3e-05", "4e-05", "5e-05", "6e-05"], "keys")
    # 1.5 * (31.2 + 9e-6 * 160000) = 1.5 * 32.64 = 48.96 -> 49
    check(env.attempt_ceiling(31.2, 160_000) == 49, "ceiling is ceil(1.5 * (planner + 9 us per shot))")
    check(env.attempt_ceiling(0.0, 0) == 0, "zero charge")
    with pytest.raises(env.EnvelopeError):
        env.attempt_ceiling(math.nan, 10)


def test_contract_carries_per_step_ceilings() -> None:
    import live_run

    record = {"execution_contract": execution_fixture(), "family_configuration": {"layout_width": 32}}
    contract = live_run.envelope_contract(record, v2_args())
    check(contract["schema"] == env.ENVELOPE_SCHEMA and "fallback_rep_delay_seconds" not in contract, "v2 fields")
    check(contract["rep_delay_ladder_seconds"] == list(env.REP_DELAY_LADDER_S), "ladder recorded")
    check(contract["ceiling_rule"] == {"factor": 1.5, "per_shot_residual_seconds": 9e-6}, "rule recorded")
    charges, shots = live_run.envelope_ladder(record["execution_contract"])
    check(shots == 2000 and charges["2e-05"] == 20.0, f"planner charges {charges} shots {shots}")
    # 30 us adds 2000 shots * 10 us = 0.02 s of delay to 20 s; the ceiling at 20 us is ceil(1.5 * 20.018) = 31.
    check(contract["ladder_ceiling_seconds"]["2e-05"] == 31, f"{contract['ladder_ceiling_seconds']}")
    check(contract["ceiling_seconds"] == {"attempt_1": 31}, "attempt 1 takes the first ceiling")
    check(contract["envelope_cap_seconds"] == 140.0, "the cap is the approved total")


@pytest.mark.parametrize("cap", [4.0, 241.0, None, math.nan, 30.0])
def test_contract_refuses_a_cap_outside_the_range_or_below_the_first_ceiling(cap: float | None) -> None:
    import live_run

    record = {"execution_contract": execution_fixture(), "family_configuration": {"layout_width": 32}}
    with pytest.raises(live_run.LiveRunError):
        live_run.envelope_contract(record, v2_args(max_total_execution_seconds=cap))
    ceilings = {env.delay_key(d): 31 for d in env.REP_DELAY_LADDER_S}
    check(env.contract_refusals(140.0, ceilings, 30.0) != [], "a bound under the first ceiling refuses")
    check(
        env.contract_refusals(140.0, ceilings, 31.0) == [] and env.contract_refusals(31.0, ceilings, None) == [], "ok"
    )


def test_parser_refuses_v2_flags_the_schema_does_not_take(capsys: Any) -> None:
    import live_run

    base = ["--family", "measurement-sequence-envelope", "--layout-width", "32", "--max-total-execution-seconds", "140"]
    cases = [
        (["--rep-delay", "5e-5"], "ladder's first value"),
        (["--rep-delay", "2e-5", "--fallback-max-execution-seconds", "60"], "msq-envelope-v1 approvals only"),
    ]
    for extra, message in cases:
        with pytest.raises(SystemExit):
            live_run.main([*base, *extra])
        check(message in capsys.readouterr().err, f"refusal names {message}")


V2_LADDER = {"2e-05": 74, "3e-05": 86, "4e-05": 99, "5e-05": 111, "6e-05": 124}


def test_v2_attempt_one_does_not_reserve_attempt_two() -> None:
    check(env.attempt_admission_v2(1, 160.0, 60.0, 140.0, 74.0) == [], "c1 74 fits remaining 160 minus reserve 60")
    check(env.attempt_admission(1, 160.0, 60.0, 147.0, 74.0) != [], "v1 with cap 147 refuses the same quota")
    check(env.attempt_admission_v2(1, 160.0, 60.0, 70.0, 74.0) != [], "ceiling past the cap")
    check(env.attempt_admission_v2(1, 130.0, 60.0, 140.0, 74.0) != [], "ceiling past remaining minus reserve")


def test_v2_fallback_step_is_the_smallest_admitted() -> None:
    step, rejected = env.select_fallback_step(20e-6, V2_LADDER, 158.0, 60.0, 140.0, 2.0, False)
    check(step == (30e-6, 86.0) and rejected == {}, f"billed 2 s picks 30 us: {step}")
    step, rejected = env.select_fallback_step(20e-6, V2_LADDER, 140.0, 60.0, 140.0, 2.0, False)
    check(step is None and list(rejected) == ["3e-05", "4e-05", "5e-05", "6e-05"], f"{rejected}")
    check(all(reasons for reasons in rejected.values()), "every step names its reasons")
    # An unattributed attempt 1 keeps its ceiling 74 reserved: 74 + 86 = 160 <= 220 - 60 admits 30 us, 219 does not.
    step, _ = env.select_fallback_step(20e-6, V2_LADDER, 220.0, 60.0, 240.0, 74.0, True)
    check(step == (30e-6, 86.0), "unattributed earlier at the boundary")
    step, rejected = env.select_fallback_step(20e-6, V2_LADDER, 219.0, 60.0, 240.0, 74.0, True)
    check(step is None and "3e-05" in rejected, "one second short rejects 30 us and every larger step")
    step, rejected = env.select_fallback_step(20e-6, V2_LADDER, 400.0, 60.0, 240.0, 2.0, False, 90.0)
    check(step == (30e-6, 86.0), "a bound of 90 keeps 30 us")
    step, rejected = env.select_fallback_step(20e-6, V2_LADDER, 400.0, 60.0, 240.0, 2.0, False, 80.0)
    check(step is None and "3e-05" in rejected, "a bound under every ceiling leaves no candidate")
    step, _ = env.select_fallback_step(40e-6, V2_LADDER, 400.0, 60.0, 240.0, 2.0, False)
    check(step == (50e-6, 111.0), "only steps above attempt 1's delay are candidates")


def v2_contract() -> dict[str, Any]:
    return {
        "schema": env.ENVELOPE_SCHEMA,
        "rep_delay_seconds": 20e-6,
        "rep_delay_ladder_seconds": list(env.REP_DELAY_LADDER_S),
        "ladder_ceiling_seconds": V2_LADDER,
        "ceiling_seconds": {"attempt_1": 74},
        "ceiling_bound_seconds": None,
        "envelope_cap_seconds": 140.0,
        "reserve_seconds": 60.0,
    }


def test_v2_send_admission_and_v1_unchanged() -> None:
    import live_run

    first = {"envelope": {"contract": v2_contract()}}
    check(live_run.envelope_send_refusals(first, 160.0) == [], "v2 attempt 1 admits")
    check(live_run.envelope_send_refusals(first, 133.0) != [], "v2 attempt 1 short of its ceiling")
    second = {
        "envelope": {
            "contract": v2_contract(),
            "attempt": 2,
            "fallback_evidence": {"billed_seconds": 2.0, "chosen": {"rep_delay_seconds": 3e-5, "ceiling_seconds": 86}},
        }
    }
    check(live_run.envelope_send_refusals(second, 146.0) == [], "attempt 2 needs its chosen ceiling only")
    check(live_run.envelope_send_refusals(second, 145.0) != [], "attempt 2 short of its chosen ceiling")
    v1 = {
        "envelope": {
            "contract": {
                "schema": env.ENVELOPE_SCHEMA_V1,
                "reserve_seconds": 60.0,
                "envelope_cap_seconds": 147.0,
                "ceiling_seconds": {"attempt_1": 74.0, "attempt_2": 73.0},
            }
        }
    }
    check(live_run.envelope_send_refusals(v1, 160.0) != [], "v1 attempt 1 reserves the whole cap")
    check(live_run.envelope_send_refusals(v1, 207.0) == [], "v1 attempt 1 admits with the cap and reserve free")


def v2_approved(tmp_path: Any, billed_job: FakeJob) -> tuple[Any, Any]:
    import hashlib
    import json

    directory, _, approved = approved_envelope(tmp_path)
    approved["envelope"]["contract"] = v2_contract()
    data = json.dumps(approved).encode()
    (directory / "record.json").write_bytes(data)
    first = tmp_path / "first"
    first.mkdir()
    meta = {"run": "approved", "record_sha256": hashlib.sha256(data).hexdigest(), "envelope": True}
    record = {"shots": 8192, "approved_record": meta, "submission": {"jobs": [{"job_id": "j1", "pubs": [{"n": "p"}]}]}}
    (first / "record.json").write_text(json.dumps(record))
    return directory, first


def test_v2_fallback_setup_chooses_a_step_and_records_the_rest(tmp_path: Any) -> None:
    import argparse

    import live_run

    job = FakeJob("ERROR", "Error code 1305; ran longer", None, 2)
    directory, first = v2_approved(tmp_path, job)
    args = argparse.Namespace(envelope_fallback=first)
    evidence = live_run.envelope_fallback_setup(FakeService(job, 158.0), args)
    check(evidence["chosen"] == {"rep_delay_seconds": 3e-5, "ceiling_seconds": 86.0}, f"{evidence}")
    check(
        args.rep_delay == 3e-5 and args.max_execution_seconds == 86.0 and args.envelope_attempt["attempt_index"] == 2,
        "args",
    )
    tight = argparse.Namespace(envelope_fallback=first)
    with pytest.raises(live_run.LiveRunError, match="3e-05"):
        live_run.envelope_fallback_setup(FakeService(job, 140.0), tight)


def test_v2_attempt_two_mismatches_need_an_approved_ladder_step(tmp_path: Any) -> None:
    import copy
    import json

    import live_run

    directory, sha, approved = approved_envelope(tmp_path)
    approved["envelope"]["contract"] = v2_contract()
    (directory / "record.json").write_bytes(json.dumps(approved).encode())
    import hashlib

    sha = hashlib.sha256((directory / "record.json").read_bytes()).hexdigest()
    second = copy.deepcopy(approved)
    second["execution_contract"] = execution_fixture()
    second["envelope"]["attempt"] = 2
    second["envelope"]["fallback_evidence"] = {"chosen": {"rep_delay_seconds": 3e-5, "ceiling_seconds": 86}}
    second["policy"] = {"rep_delay_seconds": 3e-5, "max_execution_seconds": 86}
    check(live_run.approved_envelope_mismatches(directory, second, sha) == [], "an approved ladder step matches")
    second["envelope"]["fallback_evidence"]["chosen"]["ceiling_seconds"] = 87
    second["policy"]["max_execution_seconds"] = 87
    check(live_run.approved_envelope_mismatches(directory, second, sha) != [], "a ceiling the ladder does not hold")
    second["envelope"]["fallback_evidence"]["chosen"] = {"rep_delay_seconds": 3.5e-5, "ceiling_seconds": 86}
    second["policy"]["rep_delay_seconds"] = 3.5e-5
    second["policy"]["max_execution_seconds"] = 86
    check(live_run.approved_envelope_mismatches(directory, second, sha) != [], "a delay off the ladder")


def scaled_execution(circuit_seconds: float) -> dict[str, Any]:
    """execution_fixture with each PUB's planner circuit time set to circuit_seconds."""
    execution = execution_fixture()
    for pub in execution["selected_job_costs"][0]["pubs"]:
        pub["estimated_execution_seconds"] = circuit_seconds
    return execution


def v2_planned(tmp_path: Any) -> tuple[Any, str, dict[str, Any]]:
    """An approved v2 dry run whose contract the ceiling rule derives from execution_fixture."""
    import hashlib
    import json

    import live_run

    directory, _, approved = approved_envelope(tmp_path)
    approved["execution_contract"] = execution_fixture()
    approved["envelope"]["contract"] = live_run.envelope_contract(approved, v2_args())
    approved["policy"] = {**approved["policy"], "max_execution_seconds": 31.0}
    (directory / "record.json").write_bytes(json.dumps(approved).encode())
    return directory, hashlib.sha256((directory / "record.json").read_bytes()).hexdigest(), approved


def test_v2_mismatches_bound_the_ladder_the_fresh_execution_contract_implies(tmp_path: Any) -> None:
    import copy

    import live_run

    directory, sha, approved = v2_planned(tmp_path)
    fresh = copy.deepcopy(approved)
    check(live_run.approved_envelope_mismatches(directory, fresh, sha) == [], "the approved plan matches itself")
    fresh["execution_contract"] = scaled_execution(4.0)
    check(live_run.approved_envelope_mismatches(directory, fresh, sha) == [], "a cheaper fresh plan keeps the approval")
    # The stale contract still holds the approved ceilings; the comparison reads the refreshed execution contract.
    fresh["execution_contract"] = scaled_execution(6.0)
    found = live_run.approved_envelope_mismatches(directory, fresh, sha)
    check(len([m for m in found if "exceeds the approved" in m]) == len(env.REP_DELAY_LADDER_S), f"{found}")
    second = copy.deepcopy(fresh)
    chosen = approved["envelope"]["contract"]["ladder_ceiling_seconds"]["3e-05"]
    second["envelope"]["attempt"] = 2
    second["envelope"]["fallback_evidence"] = {"chosen": {"rep_delay_seconds": 3e-5, "ceiling_seconds": chosen}}
    second["policy"] = {"rep_delay_seconds": 3e-5, "max_execution_seconds": chosen}
    found = live_run.approved_envelope_mismatches(directory, second, sha)
    check(
        any("exceeds the approved" in m for m in found), f"attempt 2 under the approved contract still refuses {found}"
    )
    second["execution_contract"] = {}
    found = live_run.approved_envelope_mismatches(directory, second, sha)
    check(any("no selected job costs" in m for m in found), f"a missing execution contract refuses: {found}")
    fresh["execution_contract"] = scaled_execution(4.0)
    fresh["envelope"]["contract"]["envelope_cap_seconds"] = 150.0
    check(
        "the envelope contract differs" in live_run.approved_envelope_mismatches(directory, fresh, sha), "the cap binds"
    )


def test_refresh_rebinds_attempt_one_to_the_fresh_ladder() -> None:
    import live_run

    record: dict[str, Any] = {
        "execution_contract": execution_fixture(),
        "family_configuration": {"layout_width": 32},
        "policy": {"max_execution_seconds": 31.0},
    }
    args = v2_args(envelope_ceiling_bound=None)
    record["envelope"] = {
        "contract": live_run.envelope_contract(record, args),
        "planner_charge_seconds": {"attempt_1": 20.0, "ladder": {}},
    }
    record["execution_contract"] = scaled_execution(6.0)
    check(live_run.refresh_envelope_ceilings(record, args) == [], "a fresh plan inside the rule refreshes")
    # ceil(1.5 * (10 + 12 + 2000 * 9e-6)) = ceil(33.027) = 34
    check(record["envelope"]["contract"]["ceiling_seconds"] == {"attempt_1": 34}, f"{record['envelope']['contract']}")
    check(args.max_execution_seconds == 34.0 and record["policy"]["max_execution_seconds"] == 34.0, "sent ceiling")
    check(record["envelope"]["planner_charge_seconds"]["attempt_1"] == 22.0, "planner charge follows")
    refused = live_run.refresh_envelope_ceilings(record, v2_args(envelope_ceiling_bound=33.0))
    check(len(refused) == 1 and "ceiling rule" in refused[0], f"a bound under the fresh ceiling refuses: {refused}")
    second = {**record, "envelope": {**record["envelope"], "attempt": 2}}
    check(live_run.refresh_envelope_ceilings(second, v2_args()) == [], "attempt 2 keeps the approved contract")


@pytest.mark.parametrize(
    ("bound", "remaining", "expected"),
    [(None, 160.0, 100.0), (None, 140.0, 80.0), (None, 50.0, 100.0), (None, None, 100.0), (45.0, 160.0, 45.0)],
)
def test_candidate_ceiling_screens_without_a_flag(
    bound: float | None, remaining: float | None, expected: float
) -> None:
    import qpu_planning

    args = v2_args(max_execution_seconds=bound, max_total_execution_seconds=100.0)
    usage = {"usage_remaining_seconds": remaining}
    check(qpu_planning.candidate_ceiling(args, usage) == expected, f"{bound} {remaining}")


def test_dry_run_applies_the_attempt_one_send_admission() -> None:
    import live_run

    def plan_record() -> dict[str, Any]:
        return {
            "execution_contract": execution_fixture(),
            "family_configuration": {"layout_width": 32},
            "policy": {"max_execution_seconds": 30.0},
            "budget_plan": {"admitted": True, "reasons": [], "jobs": []},
        }

    # Contract c1 = 31 s: remaining 90 minus reserve 60 leaves 30 s, so the send would refuse.
    record = plan_record()
    live_run.apply_envelope_ceiling(
        record, [], v2_args(max_execution_seconds=30.0 + 100.0), {"usage_remaining_seconds": 90.0}
    )
    check(record["budget_plan"]["admitted"] is False and record["budget_plan"]["reasons"], f"{record['budget_plan']}")
    record = plan_record()
    live_run.apply_envelope_ceiling(record, [], v2_args(max_execution_seconds=None), {"usage_remaining_seconds": 91.0})
    check(record["budget_plan"]["admitted"] is True and record["policy"]["max_execution_seconds"] == 31.0, "admits")


def test_dry_run_applies_the_send_rule_to_a_v1_plan() -> None:
    import live_run

    record = {
        "execution_contract": execution_fixture(),
        "family_configuration": {"layout_width": 32},
        "policy": {},
        "budget_plan": {"admitted": True, "reasons": [], "jobs": []},
    }
    args = v2_args(
        envelope_schema=env.ENVELOPE_SCHEMA_V1, max_execution_seconds=74.0, fallback_max_execution_seconds=73.0
    )
    live_run.apply_envelope_ceiling(record, [], args, {"usage_remaining_seconds": 160.0})
    check(record["budget_plan"]["admitted"] is False, "remaining 160, reserve 60, cap 147: the send refuses")


def test_layout_rule_v2_reaches_the_maximum_packing_greedy_misses() -> None:
    """A 46-qubit path: errors favor q % 3 == 1, so greedy keeps 15 qubits while {0, 3, ..., 45} packs 16."""
    qubits = {q: row(0.001 if q % 3 == 1 else 0.004) for q in range(46)}
    edges = [(q, q + 1) for q in range(45)]
    with pytest.raises(env.EnvelopeError, match="only 15 qubits"):
        env.layout_rule(qubits, (), edges, 16)
    check(env.layout_rule_v2(qubits, (), edges, 16) == list(range(0, 46, 3)), "v2 keeps the maximum packing")
    with pytest.raises(env.EnvelopeError, match="only 16 qubits"):
        env.layout_rule_v2(qubits, (), edges, 24)


def test_layout_rule_v2_matches_brute_force() -> None:
    import itertools

    import msq_envelope_null as null

    generator = np.random.default_rng(null.NULL_SEED)
    edges = [(q, q + 1) for q in range(13)] + [(2, 9), (5, 11)]
    for _ in range(4):
        qubits = {q: row(float(generator.uniform(0.001, 0.01))) for q in range(14)}
        near = {q: set(env.coupling_distances(edges, q, env.RULE_MIN_GRAPH_DISTANCE - 1)) for q in qubits}
        for width in (3, 4):
            admissible = [
                subset
                for subset in itertools.combinations(sorted(qubits), width)
                if all(b not in near[a] for a, b in itertools.combinations(subset, 2))
            ]
            best = min(admissible, key=lambda s: (sum(float(qubits[q]["readout_error"] or 0.0) for q in s), s))
            result = env.packed_layout(qubits, (), edges, width)
            check(tuple(result) == best, f"width {width}: {result} vs brute force {best}")


def test_layout_rule_v2_ties_resolve_to_the_smallest_index_tuple() -> None:
    qubits = {q: row(0.002) for q in range(9)}
    edges = [(q, q + 1) for q in range(8)]
    check(env.packed_layout(qubits, (), edges, 3) == [0, 3, 6], "equal errors keep the smallest tuple")


def test_place_layout_routes_by_schema_and_v1_is_unchanged() -> None:
    qubits, edges = chain(60)
    v1 = env.place_layout(env.ENVELOPE_SCHEMA_V1, qubits, (), edges, 16)
    check(v1 == env.layout_rule(qubits, (), edges, 16), "v1 keeps the greedy rule")
    v2 = env.place_layout(env.ENVELOPE_SCHEMA, qubits, (), edges, 16)
    check(v2 == env.layout_rule_v2(qubits, (), edges, 16) and len(v2) == 16, "v2 routes to the packing")
    with pytest.raises(env.EnvelopeError):
        env.place_layout("msq-envelope-v0", qubits, (), edges, 16)
