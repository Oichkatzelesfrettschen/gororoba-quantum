"""Contract for scripts/qi_tuna17_interleaved_cases.py: the three arms obey the provider's batch and shot limits, the
order is a function of one draw and keeps every anchor and delay, the files regenerate byte for byte (or wait for the
draw), the submit path refuses every backend status but idle, the estimator recovers its classes from exact synthetic
series and the phase fit recovers a z rotation it was given. No test draws a random number: the fixture order comes
from a hash stream."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import pytest
import qi_tuna17_interleaved_cases as cases


def retained_fixture() -> dict[str, Any]:
    """Seventeen qubits of retained-shaped inputs: a plateau model on every qubit but one."""
    qubits = []
    for qubit in range(17):
        qubits.append(
            {
                "qubit": qubit,
                "e01": 0.03,
                "e11": 0.96,
                "single_us": 20.0 + qubit,
                "single_interval_us": [19.0 + qubit, 21.0 + qubit],
                "plateau_us": 19.0 + qubit,
                "plateau": 0.0 if qubit == 8 else 0.02,
                "population": {str(c): math.exp(-c * 0.02 / (20.0 + qubit)) for c in (0, 250, 500, 1000, 2000, 4000)},
                "ladder_p0": {"0": 1.0, "32": 0.9, "128": 0.1 if qubit % 2 else 0.7, "256": 0.6},
            }
        )
    return {"qubits": qubits, "tau2": 0.0027**2, "anchor_jobs": 3, "count": 8192}


def draw_record(values: list[int]) -> dict[str, Any]:
    raw = json.dumps({"success": True, "type": "uint16", "length": str(len(values)), "data": values})
    return {
        "schema": "anu-qrng-draw-v1",
        "source": "fixture",
        "retrieved_utc": "2026-01-01T00:00:00Z",
        "raw": raw,
        "raw_sha256": hashlib.sha256(raw.encode()).hexdigest(),
        "type": "uint16",
        "values": values,
    }


def test_budget_and_measurement_limits() -> None:
    for name, profile in cases.PROFILES.items():
        longest = max(cases.job_seconds(profile, row) for row in cases.library(name).values())
        if longest >= 300 or profile["shots"] > (2048 if name == "qx" else 131072):
            raise AssertionError((name, longest))
    budget = cases.budget("tuna_17")
    arms = {a: (r["batches"], r["jobs"], r["shots"], r["expected_execution_seconds"]) for a, r in budget["per_arm"].items()}
    if arms != {
        "interleaved_t1": (18, 54, 442368, 433.7),
        "crosstalk": (8, 24, 196608, 169.2),
        "q12_phase": (4, 12, 49152, 57.3),
    }:
        raise AssertionError(arms)
    total = budget["total"]
    if (total["batches"], total["jobs"], total["shots"]) != (30, 90, 688128):
        raise AssertionError(total)


def test_delays_follow_the_retained_plateau_times_and_the_longest_is_17423_cycles() -> None:
    shape = json.loads(cases.RETAINED_SHAPE.read_text(encoding="utf-8"))["qubits"]
    retained = [round(q["models"]["plateau"]["params"]["T_us"], 6) for q in shape]
    if list(cases.PLATEAU_T_US) != retained:
        raise AssertionError("the frozen plateau times differ from the retained shape analysis")
    if max(cases.t1_delays(17, 12)) != 17423 or cases.t1_delays(17, 12).index(17423) != 10:
        raise AssertionError(cases.t1_delays(17, 12))
    if cases.t1_delays(17, 1)[9] != round(retained[9] * 50) or cases.t1_delays(10, 2) != cases.t1_delays(17, 2)[:10]:
        raise AssertionError("a delay differs from the plateau time or the qx profile reads other times")


def test_every_qubit_waits_the_batch_chain_and_its_own_delay_before_the_barrier() -> None:
    for name in cases.PROFILES:
        if cases.timing_problems(name):
            raise AssertionError(cases.timing_problems(name))
    rows = cases.library("tuna_17")
    chain = max(cases.t1_delays(17, 12))
    if f"wait({chain}) q[10]" not in rows["t1-m12.cq"]["text"] or rows["t1-m12.cq"]["text"].count("wait(") != 33:
        raise AssertionError("the 12 T circuit lacks its pre-wait structure")
    # Known bad: a delay circuit whose after-X wait is short of the qubit's delay, and an anchor with a short chain.
    bad = {k: dict(v) for k, v in rows.items()}
    bad["t1-m12.cq"]["text"] = bad["t1-m12.cq"]["text"].replace("wait(17423) q[10]\n", "wait(17000) q[10]\n")
    bad["readout-0-m12.cq"]["text"] = bad["readout-0-m12.cq"]["text"].replace("wait(17423) q[3]", "wait(17422) q[3]")
    found = cases.timing_problems("tuna_17", bad)
    if not any("t1-m12.cq: qubit 10" in p for p in found) or not any("readout-0-m12.cq: qubit 3" in p for p in found):
        raise AssertionError(found)
    if any("t1-m0.5" in p for p in found):
        raise AssertionError(found)


def test_order_is_a_function_of_the_draw_and_keeps_anchors_and_delays() -> None:
    values = cases.synthetic_values(2000)
    for name in cases.PROFILES:
        plan = cases.schedule(name, values)
        if plan != cases.schedule(name, values) or plan == cases.schedule(name, cases.synthetic_values(2001)[1:]):
            raise AssertionError("the order does not follow the draw")
        for arm, batches in plan["arms"].items():
            if any(len(b["circuits"]) > cases.BATCH_LIMIT for b in batches):
                raise AssertionError(arm)
            if sorted(n for b in batches for n in b["circuits"]) != sorted(cases.usage(name)[arm]):
                raise AssertionError(arm)
        if cases.order_problems(plan["arms"]["interleaved_t1"]):
            raise AssertionError(cases.order_problems(plan["arms"]["interleaved_t1"]))
        for batch in plan["arms"]["interleaved_t1"]:
            if set(batch["circuits"]) != set(cases.interleaved_circuits(batch["multiplier"])):
                raise AssertionError(batch)
    with pytest.raises(ValueError, match="needs more"):
        cases.schedule("tuna_17", values[:10])


def test_blocked_order_rejects_a_repeated_round_a_reshuffled_pair_and_a_stuck_slot() -> None:
    plan = cases.schedule("tuna_17", cases.synthetic_values(2000))["arms"]["interleaved_t1"]
    blocks = len(cases.T1_MULTIPLIERS)
    same = [dict(plan[number % blocks], round=plan[number]["round"]) for number in range(len(plan))]
    if not any("block positions" in p for p in cases.order_problems(same)):
        raise AssertionError(cases.order_problems(same))
    reshuffled = [dict(b) for b in plan]
    first = [i for i, b in enumerate(plan) if b["round"] == 1]
    reshuffled[first[0]], reshuffled[first[2]] = dict(plan[first[2]]), dict(plan[first[0]])
    if not any("pairs" in p for p in cases.order_problems(reshuffled)):
        raise AssertionError(cases.order_problems(reshuffled))
    stuck = [dict(b, circuits=list(cases.interleaved_circuits(b["multiplier"]))) for b in plan]
    if not any("slots" in p for p in cases.order_problems(stuck)):
        raise AssertionError(cases.order_problems(stuck))


def test_rounds_keep_three_pairs_that_move_between_block_positions() -> None:
    plan = cases.schedule("tuna_17", cases.synthetic_values(2000))["arms"]["interleaved_t1"]
    rounds = [[b["multiplier"] for b in plan if b["round"] == r] for r in range(cases.ROUNDS)]
    pairs = [{frozenset(r[k : k + 2]) for k in (0, 2, 4)} for r in rounds]
    if pairs[0] != pairs[1] or pairs[1] != pairs[2] or len(pairs[0]) != 3:
        raise AssertionError(rounds)
    if {frozenset(rounds[1][4:6])} != {frozenset(rounds[0][0:2])} or {frozenset(rounds[2][2:4])} != {
        frozenset(rounds[0][0:2])
    }:
        raise AssertionError(rounds)


def listed_circuits(directory: Path) -> set[str]:
    """Circuit paths that a batch manifest of the directory lists, relative to it."""
    found = set()
    for manifest in directory.rglob("cases.json"):
        for row in json.loads(manifest.read_text(encoding="utf-8")).get("circuits", []):
            found.add((manifest.parent / row["file"]).relative_to(directory).as_posix())
    return found


def test_every_written_circuit_sits_beside_a_manifest_that_lists_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    retained = retained_fixture()
    cases.write(tmp_path / "pending", draw_root=tmp_path, retained=retained)
    pending = cases.case_directory(tmp_path / "pending", "tuna_17")
    if list(pending.rglob("*.cq")):
        raise AssertionError("a pending case wrote a circuit that no batch manifest lists")
    path = "docs/evidence/anu_qrng/draw-2026-01-01T000000Z.json"
    (tmp_path / path).parent.mkdir(parents=True)
    (tmp_path / path).write_text(json.dumps(draw_record(cases.synthetic_values(400))), encoding="utf-8")
    monkeypatch.setattr(cases, "DRAW", path)
    cases.write(tmp_path / "drawn", draw_root=tmp_path, retained=retained)
    for profile_name in cases.PROFILES:
        drawn = cases.case_directory(tmp_path / "drawn", profile_name)
        written = {p.relative_to(drawn).as_posix() for p in drawn.rglob("*.cq")}
        if not written or written != listed_circuits(drawn):
            raise AssertionError(sorted(written ^ listed_circuits(drawn))[:3])
    stray = pending / "stray.cq"
    stray.write_text("stray\n", encoding="utf-8")
    unlisted = {p.relative_to(pending).as_posix() for p in pending.rglob("*.cq")} - listed_circuits(pending)
    if unlisted != {"stray.cq"}:
        raise AssertionError(unlisted)


def test_rejection_keeps_the_modulus_unbiased() -> None:
    stream = cases.Stream([65535, 65534, 7])
    if stream.below(3) != 2 or stream.position != 2:
        raise AssertionError("a value past the last whole multiple of the modulus was kept")
    counts = [0, 0, 0]
    for value in range(65536):
        if value < (65536 // 3) * 3:
            counts[value % 3] += 1
    if len(set(counts)) != 1:
        raise AssertionError(counts)
    if cases.qrng_values_needed("tuna_17") > cases.DRAW_LENGTH:
        raise AssertionError("the request is shorter than the order")


def test_pending_state_writes_no_batches_then_the_draw_creates_them(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    retained = retained_fixture()
    cases.write(tmp_path / "cases", draw_root=tmp_path, retained=retained)
    directory = cases.case_directory(tmp_path / "cases", "tuna_17")
    if (
        (directory / "schedule.json").exists()
        or list(directory.glob("*/batch-*"))
        or not (directory / "qrng_request.json").is_file()
    ):
        raise AssertionError("a pending case holds batches or lacks its request")
    if cases.check(tmp_path / "cases", draw_root=tmp_path, retained=retained):
        raise AssertionError(cases.check(tmp_path / "cases", draw_root=tmp_path, retained=retained))
    (directory / "CASE.md").write_text("handwritten\n", encoding="utf-8")
    (directory / "stray.cq").write_text("stray\n", encoding="utf-8")
    if cases.check(tmp_path / "cases", draw_root=tmp_path, retained=retained) != [
        f"{directory / 'stray.cq'} is not generated"
    ]:
        raise AssertionError("a stray file went unnamed")
    values = cases.synthetic_values(400)
    path = "docs/evidence/anu_qrng/draw-2026-01-01T000000Z.json"
    (tmp_path / path).parent.mkdir(parents=True)
    (tmp_path / path).write_text(json.dumps(draw_record(values)), encoding="utf-8")
    monkeypatch.setattr(cases, "DRAW", path)
    cases.write(tmp_path / "cases2", draw_root=tmp_path, retained=retained)
    ready = cases.case_directory(tmp_path / "cases2", "tuna_17")
    manifest = json.loads((ready / "interleaved_t1" / "batch-00" / "cases.json").read_text(encoding="utf-8"))
    if manifest["arm"] != "interleaved_t1" or manifest["qrng_draw"] != path or len(manifest["circuits"]) != 3:
        raise AssertionError(manifest)
    if len(list(ready.glob("*/batch-*"))) != sum(cases.batch_counts("tuna_17").values()) or (ready / "qrng_request.json").exists():
        raise AssertionError("a drawn case lacks its 65 batches or keeps its request")
    if cases.check(tmp_path / "cases2", draw_root=tmp_path, retained=retained):
        raise AssertionError("a drawn case does not regenerate")
    listed = json.loads((ready / "interleaved_t1" / "batch-03" / "cases.json").read_text(encoding="utf-8"))
    changed = listed["circuits"][0]["file"]
    (ready / "interleaved_t1" / "batch-03" / changed).write_text("changed\n", encoding="utf-8")
    if f"{changed} differs" not in "".join(cases.check(tmp_path / "cases2", draw_root=tmp_path, retained=retained)):
        raise AssertionError("a changed circuit went unnamed")


@pytest.mark.parametrize(
    "document",
    [
        cases.synthetic_status("calibrating"),
        cases.synthetic_status("executing"),
        cases.synthetic_status("offline"),
        cases.synthetic_status("idle", instance="calibrating"),
        cases.synthetic_status("idle", queue=1),
        {"error": "x"},
        {},
        [],
        None,
        {"backend_types": []},
        {"backend_types": [{"id": 7, "status": "idle"}]},
        {
            "backend_types": [
                {"id": 7, "status": "idle", "instances": [{}], "queue_own": {"number_of_jobs_in_queue": 0}}
            ]
        },
    ],
)
def test_submit_path_refuses_every_status_but_idle(tmp_path: Path, document: Any) -> None:
    series, runs = tmp_path / "arm", tmp_path / "runs"
    (series / "batch-00").mkdir(parents=True)
    (series / "batch-00" / "cases.json").write_text("{}", encoding="utf-8")
    called: list[list[str]] = []

    def run_command(argv: list[str]) -> tuple[int, str]:
        called.append(argv)
        return 0, ""

    with pytest.raises(cases.AdmissionRefused):
        cases.submit_series(
            series,
            runs,
            "S",
            "approval",
            7,
            command=["py"],
            read_status=lambda: document,
            run_command=run_command,
            launch=lambda argv: cases.FakeProcess(),
            sleep=lambda s: None,
        )
    if called or runs.exists():
        raise AssertionError("a refused status still reached the submit command or created a run directory")


def test_idle_backend_submits_once_and_records_admission_and_trace(tmp_path: Path) -> None:
    series, runs = tmp_path / "case" / "arm", tmp_path / "runs"
    (series / "batch-00").mkdir(parents=True)
    (series / "batch-00" / "cases.json").write_text("{}", encoding="utf-8")
    called: list[list[str]] = []
    outputs = iter([(1, "refused: wait 7 more seconds"), (0, "")])
    slept: list[float] = []

    def run_command(argv: list[str]) -> tuple[int, str]:
        called.append(argv)
        return next(outputs)

    cases.submit_series(
        series,
        runs,
        "S",
        "approval",
        7,
        command=["py", "platform"],
        read_status=lambda: cases.synthetic_status("idle"),
        run_command=run_command,
        launch=lambda argv: cases.FakeProcess(3),
        sleep=slept.append,
    )
    run = runs / "S-case-arm-batch-00"
    admitted = json.loads((run / "admission.json").read_text(encoding="utf-8"))
    trace = json.loads((run / "status-trace.json").read_text(encoding="utf-8"))["rows"]
    if len(called) != 2 or called[0][:4] != ["py", "platform", "submit", str(run)] or slept[0] != 8:
        raise AssertionError((called, slept))
    if (
        admitted["status"] != "idle"
        or admitted["queue_own"] != 0
        or len(trace) != 5
        or {r["status"] for r in trace} != {"idle"}
    ):
        raise AssertionError((admitted, trace))


def test_status_is_read_again_before_every_retry(tmp_path: Path) -> None:
    series, runs = tmp_path / "case" / "arm", tmp_path / "runs"
    (series / "batch-00").mkdir(parents=True)
    (series / "batch-00" / "cases.json").write_text("{}", encoding="utf-8")
    labels = iter(["idle", "idle", "calibrating"])
    called: list[list[str]] = []

    def run_command(argv: list[str]) -> tuple[int, str]:
        called.append(argv)
        return 1, "refused: wait 5 more seconds"

    with pytest.raises(cases.AdmissionRefused):
        cases.submit_series(
            series,
            runs,
            "S",
            "approval",
            7,
            command=["py"],
            read_status=lambda: cases.synthetic_status(next(labels)),
            run_command=run_command,
            launch=lambda argv: cases.FakeProcess(),
            sleep=lambda s: None,
        )
    if len(called) != 2:
        raise AssertionError(called)
    admitted = json.loads((runs / "S-case-arm-batch-00" / "admission.json").read_text(encoding="utf-8"))
    if admitted["attempt"] != 2:
        raise AssertionError(admitted)


def always_idle() -> dict[str, Any]:
    return cases.synthetic_status("idle")


def accepted(argv: list[str]) -> tuple[int, str]:
    return 0, ""


def test_run_names_carry_the_case_and_a_changed_or_repeated_arm_stops(tmp_path: Path) -> None:
    series, runs = tmp_path / "case_a" / "arm", tmp_path / "runs"
    (series / "batch-00").mkdir(parents=True)
    (series / "batch-00" / "cases.json").write_text("{}", encoding="utf-8")

    def run(stamp: str) -> list[str]:
        return cases.submit_series(
            series,
            runs,
            stamp,
            "approval",
            7,
            command=["py"],
            read_status=always_idle,
            run_command=accepted,
            launch=lambda argv: cases.FakeProcess(),
            sleep=lambda s: None,
        )

    run("S")
    if not (runs / "S-case_a-arm-batch-00" / "status-trace.json").is_file():
        raise AssertionError(sorted(p.name for p in runs.iterdir()))
    with pytest.raises(RuntimeError, match="holds this arm under stamp S"):
        run("T")
    (series / "batch-00" / "cases.json").write_text('{"changed": 1}', encoding="utf-8")
    with pytest.raises(RuntimeError, match="differs from"):
        run("S")


def test_trace_rows_are_kept_across_a_resumed_collection(tmp_path: Path) -> None:
    series, runs = tmp_path / "case" / "arm", tmp_path / "runs"
    (series / "batch-00").mkdir(parents=True)
    (series / "batch-00" / "cases.json").write_text("{}", encoding="utf-8")

    def run(polls: int) -> None:
        cases.submit_series(
            series,
            runs,
            "S",
            "approval",
            7,
            command=["py"],
            read_status=always_idle,
            run_command=accepted,
            launch=lambda argv: cases.FakeProcess(polls),
            sleep=lambda s: None,
        )

    run(2)
    held = runs / "S-case-arm-batch-00"
    first = len(json.loads((held / "status-trace.json").read_text(encoding="utf-8"))["rows"])
    (held / "submission.json").write_text("{}", encoding="utf-8")
    run(1)
    again = len(json.loads((held / "status-trace.json").read_text(encoding="utf-8"))["rows"])
    if again != first + 3:
        raise AssertionError((first, again))


def test_a_plateau_survives_batch_levels_of_the_retained_size() -> None:
    shifts = [0.0145 * math.sin(2.1 * b) for b in range(cases.ROUNDS * len(cases.T1_MULTIPLIERS))]
    for plateau in (0.01, 0.02):
        model = {"shape": "plateau", "theta": [20.0, plateau], "e01": 0.03, "e11": 0.96}
        verdict = cases.analyze_interleaved(cases.synthetic_interleaved([model], shifts))["qubits"][0]["verdict"]
        if verdict != "tail_plateau":
            raise AssertionError((plateau, verdict))


def test_job_level_variance_ignores_a_level_common_to_both_anchors() -> None:
    shifts = [0.01 * math.sin(b) for b in range(20)]
    common = cases.job_level_variance([0.03 + s for s in shifts], [0.96 + s for s in shifts], 8192)
    own = cases.job_level_variance([0.03 + s for s in shifts], [0.96 - s for s in shifts], 8192)
    if common != 0.0 or not 0.5 * 0.01**2 < own < 2 * 0.01**2:
        raise AssertionError((common, own))


def test_start_status_comes_from_the_last_read_within_the_gap(tmp_path: Path) -> None:
    (tmp_path / "status-trace.json").write_text(
        json.dumps(
            {
                "rows": [
                    {"utc": "2026-01-01T00:00:00+00:00", "status": "calibrating"},
                    {"utc": "2026-01-01T00:01:00+00:00", "status": "idle"},
                ]
            }
        ),
        encoding="utf-8",
    )
    jobs = [
        {"file": f, "job": {"queued_at": t}}
        for f, t in (
            ("a", "2026-01-01T00:01:10Z"),
            ("b", "2026-01-01T00:00:30Z"),
            ("c", "2026-01-01T00:03:00Z"),
            ("d", "2025-12-31T23:59:00Z"),
        )
    ]
    (tmp_path / "results.json").write_text(json.dumps({"jobs": jobs}), encoding="utf-8")
    found = {r["file"]: r["status"] for r in cases.execution_start_statuses(tmp_path)}
    if found != {"a": "idle", "b": "calibrating", "c": "unobserved", "d": "unobserved"}:
        raise AssertionError(found)


def write_run(run: Path, rows: list[dict[str, Any]], p1: dict[str, list[float]], shots: int, start: str) -> None:
    """A run directory in the layout of gororoba_quantum/qi_records.py, with P1 per qubit realized as shot lists."""
    from collections import Counter  # noqa: PLC0415

    (run / "raw").mkdir(parents=True)
    nqubits = len(next(iter(p1.values())))
    circuits = []
    for row in rows:
        text = f"circuit {row['file']}\n"
        (run / row["file"]).write_text(text, encoding="utf-8")
        circuits.append({**row, "sha256": hashlib.sha256(text.encode()).hexdigest()})
    manifest = {
        "arm": "interleaved_t1",
        "meta": {},
        "backend": "tuna_17",
        "backend_type_id": 7,
        "nqubits": nqubits,
        "shots": shots,
        "circuits": circuits,
    }
    (run / "cases.json").write_text(json.dumps(manifest), encoding="utf-8")
    identity = sum(run.name.encode()) * 100
    jobs = [{"file": row["file"], "job": identity + i} for i, row in enumerate(rows)]
    receipt = {
        "schema": "qi-submission-v1",
        "approval": "fixture",
        "backend_status_at_submit": "idle",
        "backend": "tuna_17",
        "backend_type_id": 7,
        "shots": shots,
        "batch_job": identity,
        "jobs": jobs,
    }
    (run / "submission.json").write_text(json.dumps(receipt), encoding="utf-8")
    collected = []
    for entry in jobs:
        ones = [round(p * shots) for p in p1[entry["file"]]]
        values = [
            "".join("1" if shot < ones[nqubits - 1 - place] else "0" for place in range(nqubits))
            for shot in range(shots)
        ]
        (run / "raw" / f"{entry['file']}.json").write_text(json.dumps(values), encoding="utf-8")
        job = {
            "id": entry["job"],
            "batch_job_id": identity,
            "number_of_shots": shots,
            "status": "completed",
            "created_on": "2026-01-01T00:00:00Z",
            "queued_at": start,
        }
        result = {
            "job_id": entry["job"],
            "shots_requested": shots,
            "shots_done": shots,
            "results": dict(Counter(values)),
        }
        collected.append({"file": entry["file"], "job": job, "results": [result]})
    (run / "results.json").write_text(json.dumps({"schema": "qi-collection-v1", "jobs": collected}), encoding="utf-8")


def test_sanity_demands_anchors_records_and_a_start_status(tmp_path: Path) -> None:
    rows: list[dict[str, Any]] = [
        {"file": "readout-0.cq", "kind": "anchor0", "driven": []},
        {"file": "t1-0.cq", "kind": "anchor1", "driven": [0, 1, 2, 3, 4]},
        {"file": "t1-250.cq", "kind": "t1", "driven": [0, 1, 2, 3, 4], "wait_cycles": 250},
    ]
    good = {"readout-0.cq": [0.02] * 5, "t1-0.cq": [0.96] * 5, "t1-250.cq": [0.5] * 5}
    run = tmp_path / "run-a"
    write_run(run, rows, good, 200, "2026-01-01T00:01:10+00:00")
    if cases.sanity(run) != [str(p) for p in cases.sanity(run)] or not any(
        "admission.json is missing" in p for p in cases.sanity(run)
    ):
        raise AssertionError(cases.sanity(run))
    (run / "admission.json").write_text("{}", encoding="utf-8")
    trace = {"rows": [{"utc": "2026-01-01T00:01:00+00:00", "status": "idle"}]}
    (run / "status-trace.json").write_text(json.dumps(trace), encoding="utf-8")
    if cases.sanity(run):
        raise AssertionError(cases.sanity(run))
    trace["rows"][0]["status"] = "calibrating"
    (run / "status-trace.json").write_text(json.dumps(trace), encoding="utf-8")
    if "began while the backend status read calibrating" not in "".join(cases.sanity(run)):
        raise AssertionError(cases.sanity(run))
    wrong = tmp_path / "run-b"
    write_run(wrong, rows, {**good, "t1-0.cq": [0.04] * 5}, 200, "2026-01-01T00:01:10+00:00")
    if "read the wrong side of 0.5" not in "".join(cases.sanity(wrong)):
        raise AssertionError(cases.sanity(wrong))


def test_design_identifies_the_batch_level_only_through_the_anchors() -> None:
    delays = [cases.t1_delays(17, m)[9] for m in cases.T1_MULTIPLIERS]
    summary = cases.design_summary(0.03, 0.96, (20.0, 0.02), 0.0027**2, 8192, delays)
    if (
        summary["rank_with_anchors"] != summary["columns_with_anchors"]
        or summary["rank_without_anchors"] >= summary["columns_without_anchors"]
    ):
        raise AssertionError(summary)
    errors = cases.expected_errors(
        0.03, 0.96, {"single_us": 20.0, "plateau_us": 19.0, "plateau": 0.02}, 0.0027**2, 8192, delays
    )
    if not 0.0005 < errors["se_plateau"] < 0.005 or errors["plateau_z"] < 4:
        raise AssertionError(errors)


MODELS = [
    {"shape": "single", "theta": [22.0], "e01": 0.03, "e11": 0.96},
    {"shape": "plateau", "theta": [20.0, 0.03], "e01": 0.03, "e11": 0.96},
    {"shape": "two_rate", "theta": [4.0, 60.0, 0.4], "e01": 0.03, "e11": 0.96},
]


@pytest.mark.parametrize(
    ("model", "shifted", "verdict"),
    [(0, False, "single_exponential"), (0, True, "level_shift"), (1, True, "tail_plateau"), (2, False, "two_rate")],
)
def test_estimator_recovers_its_class_under_batch_levels(model: int, shifted: bool, verdict: str) -> None:
    shifts = [0.012 * math.sin(b) for b in range(cases.ROUNDS * len(cases.T1_MULTIPLIERS))] if shifted else None
    rows = cases.analyze_interleaved(cases.synthetic_interleaved([MODELS[model]], shifts))["qubits"]
    if [r["verdict"] for r in rows] != [verdict]:
        raise AssertionError(rows[0])


def with_third_round(batches: list[dict[str, Any]], offsets: dict[str, float]) -> list[dict[str, Any]]:
    """The batches plus a copy of the first round whose delay circuits read offsets[name] higher on every qubit."""
    first = [b for b in batches if b["meta"]["round"] == 0]
    extra = []
    for number, batch in enumerate(first):
        copy = {**batch, "run": f"batch-extra-{number:02d}", "p1": {k: list(v) for k, v in batch["p1"].items()}}
        for name, offset in offsets.items():
            if name in copy["p1"]:
                copy["p1"][name] = [min(max(p + offset, 0.0), 1.0) for p in copy["p1"][name]]
        extra.append(copy)
    return batches + extra


def uniform(size: float) -> dict[str, float]:
    """A third round whose delay circuits all read size higher, as one job-level shift of that round would."""
    return {f"t1-m{m}.cq": size for m in cases.T1_MULTIPLIERS}


def test_replicate_statistic_reads_every_round_of_a_delay() -> None:
    model = {"shape": "single", "theta": [22.0], "e01": 0.03, "e11": 0.96}
    clean = cases.synthetic_interleaved([model])
    good = cases.analyze_interleaved(with_third_round(clean, {}))["qubits"][0]
    bad = cases.analyze_interleaved(with_third_round(clean, uniform(0.015)))["qubits"][0]
    if good["replicate_probability"] < 0.5 or bad["replicate_probability"] >= cases.LACK_OF_FIT_PROBABILITY:
        raise AssertionError((good["replicate_probability"], bad["replicate_probability"]))


def test_an_accepted_tail_fit_with_scattering_rounds_reads_unresolved() -> None:
    model = {"shape": "plateau", "theta": [20.0, 0.03], "e01": 0.03, "e11": 0.96}
    row = cases.analyze_interleaved(with_third_round(cases.synthetic_interleaved([model]), uniform(0.012)))["qubits"][0]
    fit_probability = row["fits"]["plateau"]["probability"]
    if row["verdict"] != "unresolved" or fit_probability < cases.LACK_OF_FIT_PROBABILITY:
        raise AssertionError(row)
    if row["replicate_probability"] >= cases.LACK_OF_FIT_PROBABILITY:
        raise AssertionError(row)


def test_a_consistent_third_round_leaves_the_tail_label() -> None:
    model = {"shape": "plateau", "theta": [20.0, 0.03], "e01": 0.03, "e11": 0.96}
    row = cases.analyze_interleaved(with_third_round(cases.synthetic_interleaved([model]), {}))["qubits"][0]
    if row["verdict"] != "tail_plateau" or row["replicate_probability"] < 0.5:
        raise AssertionError(row)


def test_tail_statistic_pools_the_gain_of_the_gated_qubits() -> None:
    def fits(single: float, plateau: tuple[float, float], two_rate: tuple[float, float]) -> dict[str, dict[str, Any]]:
        return {
            "single": {"aicc": single, "probability": 0.0},
            "plateau": {"aicc": plateau[0], "probability": plateau[1]},
            "two_rate": {"aicc": two_rate[0], "probability": two_rate[1]},
        }

    # Hand values: 300 - min(100, 90) = 210; 50 - min(60, 70) is negative so 0; a lower-AICc fit that lacks fit and a
    # replicate probability under the bound add 0 each.
    first = cases.tail_contribution(fits(300.0, (100.0, 0.5), (90.0, 0.4)), 0.5)
    second = cases.tail_contribution(fits(50.0, (60.0, 0.5), (70.0, 0.5)), 0.5)
    misfit = cases.tail_contribution(fits(300.0, (100.0, 0.5), (90.0, 0.001)), 0.5)
    scatter = cases.tail_contribution(fits(300.0, (100.0, 0.5), (90.0, 0.4)), 0.005)
    if (first, second, misfit, scatter) != (210.0, 0.0, 0.0, 0.0):
        raise AssertionError((first, second, misfit, scatter))


def test_pooled_tail_verdict_reads_the_summed_gain_not_the_label_count() -> None:
    plateau = {"shape": "plateau", "theta": [20.0, 0.03], "e01": 0.03, "e11": 0.96}
    flat = {"shape": "single", "theta": [22.0], "e01": 0.03, "e11": 0.96}
    pooled = cases.analyze_interleaved(cases.synthetic_interleaved([plateau, flat]))
    rows = pooled["qubits"]
    gain = rows[0]["fits"]["single"]["aicc"] - rows[0]["fits"]["plateau"]["aicc"]
    if (
        [r["verdict"] for r in rows] != ["tail_plateau", "single_exponential"]
        or rows[1]["tail_contribution"] != 0.0
        or abs(pooled["pooled"]["tail_statistic"] - gain) > 1e-9
        or not pooled["pooled"]["tail_confirmed"]
        or pooled["pooled"]["descriptive_single_exponential_rejected"] != 1
    ):
        raise AssertionError(pooled)
    only_flat = cases.analyze_interleaved(cases.synthetic_interleaved([flat, flat]))["pooled"]
    if only_flat["tail_statistic"] != 0.0 or only_flat["tail_confirmed"]:
        raise AssertionError(only_flat)
    scattering = cases.synthetic_interleaved([plateau, plateau])
    scattered = cases.analyze_interleaved(with_third_round(scattering, uniform(0.02)))["pooled"]
    if scattered["tail_statistic"] != 0.0 or scattered["tail_confirmed"]:
        raise AssertionError(scattered)


def test_analysis_records_the_round_and_the_executed_start(tmp_path: Path) -> None:
    flat = {"shape": "single", "theta": [1.0e6], "e01": 0.0, "e11": 1.0}
    batches = cases.synthetic_interleaved([flat])
    for number, batch in enumerate(batches):
        batch["started"] = {name: f"2026-01-01T00:{number:02d}:00Z" for name in batch["rows"]}
    jobs = cases.analyze_interleaved(batches)["jobs"]
    if len(jobs) != 54 or {j["round"] for j in jobs} != {0, 1, 2} or any(j["started_utc"] is None for j in jobs):
        raise AssertionError(jobs[:3])
    run = tmp_path / "run"
    run.mkdir()
    if cases.job_starts(run) != {}:
        raise AssertionError("a run without results reported starts")
    results = {"jobs": [{"file": "a.cq", "job": {"queued_at": "T"}}]}
    (run / "results.json").write_text(json.dumps(results), encoding="utf-8")
    if cases.job_starts(run) != {"a.cq": "T"}:
        raise AssertionError(cases.job_starts(run))


def test_flat_noiseless_series_reads_as_a_single_exponential() -> None:
    flat = {"shape": "single", "theta": [1.0e6], "e01": 0.0, "e11": 1.0}
    pooled = cases.analyze_interleaved(cases.synthetic_interleaved([flat] * 3))
    if [r["verdict"] for r in pooled["qubits"]] != ["single_exponential"] * 3 or pooled["pooled"][
        "descriptive_single_exponential_accepted"
    ] != 3:
        raise AssertionError(pooled)


def test_phase_fit_recovers_a_given_rotation_and_names_the_verdicts() -> None:
    angles = [s * math.pi / 36 for s in cases.PHASE_STEPS]

    def fringe(phase: float, amplitude: float = 0.46) -> list[tuple[float, float, int]]:
        return [(a, round((0.5 + amplitude * math.cos(a + phase)) * 8192) / 8192, 8192) for a in angles]

    for phase, verdict in (
        (-0.15, "supports_target"),
        (0.15, "supports_target_opposite_sign"),
        (0.0, "null"),
        (-0.4, "other"),
        (-0.15, "supports_target"),
    ):
        fit = cases.fringe_fit(fringe(phase))
        if (
            fit is None
            or abs(fit["phase"] - phase) > 0.005
            or cases.phase_verdict(fit) != verdict
            or not 0.003 < fit["phase_se"] < 0.01
        ):
            raise AssertionError((phase, fit))
    flat = cases.fringe_fit(fringe(0.0, 0.0))
    if flat is not None and cases.phase_verdict(flat) != "no_fringe":
        raise AssertionError(flat)


def test_a_fringe_the_cosine_rejects_reads_poor_fit() -> None:
    angles = [s * math.pi / 36 for s in cases.PHASE_STEPS]
    exact = [(a, round((0.5 + 0.46 * math.cos(a - 0.15)) * 8192) / 8192, 8192) for a in angles]
    kinked = [(a, p + (0.06 if i in (2, 5) else 0.0), n) for i, (a, p, n) in enumerate(exact)]
    good = cases.fringe_fit(exact)
    bad = cases.fringe_fit(kinked)
    if good is None or bad is None or cases.phase_verdict(good) != "supports_target":
        raise AssertionError((good, bad))
    if abs(bad["phase"] + 0.15) > 0.05 or bad["phase_se"] > 0.02 or cases.phase_verdict(bad) != "poor_fit":
        raise AssertionError(bad)


def test_phase_triads_sum_to_zero_and_a_batch_level_leaves_the_phase_alone() -> None:
    if cases.triad_problems(cases.PHASE_TRIADS) or sorted(s for t in cases.PHASE_TRIADS for s in t) != sorted(
        cases.PHASE_STEPS
    ):
        raise AssertionError(cases.triad_problems(cases.PHASE_TRIADS))
    if not cases.triad_problems(((0, 12, 24), (36, 48, 60))):
        raise AssertionError("a split that is not a pair of triads passed")

    def fitted(triads: tuple[tuple[int, ...], ...]) -> float:
        points = []
        for number, triad in enumerate(triads):
            for step in triad:
                a = step * math.pi / 36
                p = 0.5 + 0.45 * math.cos(a + cases.PHASE_TARGET) + (0.03 if number else 0.0)
                points.append((a, p, 4096))
        fit = cases.fringe_fit(sorted(points))
        if fit is None:
            raise AssertionError("no fit")
        return fit["phase"]

    good = fitted(cases.PHASE_TRIADS)
    bad = fitted(((0, 12, 24), (36, 48, 60)))
    # The fit weights points by binomial variance, so the triads cut a batch level of 0.03 to about a third of the
    # bias a contiguous split leaves, and not to zero.
    if abs(bad - cases.PHASE_TARGET) < 0.02 or abs(good - cases.PHASE_TARGET) > 0.4 * abs(bad - cases.PHASE_TARGET):
        raise AssertionError((good, bad))


def test_phase_arm_has_four_triad_batches_with_interleaved_waits_and_a_usable_standard_error() -> None:
    plan = cases.schedule("tuna_17", cases.synthetic_values(2000))["arms"]["q12_phase"]
    if [b["wait_cycles"] for b in plan] != [0, 25, 0, 25] or len(cases.usage("tuna_17")["q12_phase"]) != 12:
        raise AssertionError(plan)
    rows = cases.library("tuna_17")
    for batch in plan:
        steps = sorted(rows[name]["step"] for name in batch["circuits"])
        if tuple(steps) != cases.PHASE_TRIADS[batch["triad"]] or {rows[n]["qubit"] for n in batch["circuits"]} != {12}:
            raise AssertionError(batch)
    for wait in cases.PHASE_WAITS:
        used = sorted(b["triad"] for b in plan if b["wait_cycles"] == wait)
        if used != [0, 1]:
            raise AssertionError((wait, used))
    se = cases.phase_expected_se(cases.PROFILES["tuna_17"]["arm_shots"]["q12_phase"])
    if not 0.003 < se < 0.02:
        raise AssertionError(se)
    if cases.PROFILES["tuna_17"]["arm_shots"] != {"interleaved_t1": 8192, "crosstalk": 8192, "q12_phase": 4096}:
        raise AssertionError(cases.PROFILES["tuna_17"]["arm_shots"])
    grid = [r["angle"] / (math.pi / 36) for r in rows.values() if r["kind"] == "ramsey"]
    if len(grid) != 12 or any(abs(g - round(g)) > 1e-9 or round(g) % 12 for g in grid):
        raise AssertionError(grid)


def test_phase_arm_reads_an_exact_series() -> None:
    angles = {s: s * math.pi / 36 for s in cases.PHASE_STEPS}
    ramsey_rows = {f"r{s}": {"kind": "ramsey", "qubit": 12, "wait_cycles": 0, "angle": a} for s, a in angles.items()}
    ramsey_p1 = {f"r{s}": [0.5 + 0.46 * math.cos(a + 0.15)] * 13 for s, a in angles.items()}
    scans = cases.analyze_phase([{"shots": 8192, "rows": ramsey_rows, "p1": ramsey_p1}])["scans"]
    if scans[0]["verdict"] != "supports_target_opposite_sign" or abs(scans[0]["phase"] - 0.15) > 0.005:
        raise AssertionError(scans)


def test_crosstalk_classes_circuits_and_batches() -> None:
    from qi_tuna17_characterization_cases import circuits  # noqa: PLC0415

    retained = circuits(17)
    rows = cases.library("tuna_17")
    a, b = set(cases.CLASS_A["tuna_17"]), set(cases.CLASS_B["tuna_17"])
    if (a, b) != ({0, 4, 5, 6, 10, 11, 12, 16}, {1, 3, 7, 8, 9, 13, 14, 15}) or 2 in a | b or a & b:
        raise AssertionError((a, b))
    for cycles in (250, 1000, 4000):
        if rows[f"xt-t1-{cycles}-all.cq"]["text"] != retained[f"t1-{cycles}.cq"][0]:
            raise AssertionError(cycles)
    for turns in (8, 32, 64):
        if rows[f"xt-x90-{4 * turns}-all.cq"]["text"] != retained[f"x90-{turns}.cq"][0]:
            raise AssertionError(turns)
    for name, row in rows.items():
        if row["kind"] in ("xt_t1", "xt_x90", "xt_prep1") and row["context"] in ("A", "B"):
            others = set(range(17)) - set(row["driven"])
            if any(f"q[{q}]" in row["text"] for q in others):
                raise AssertionError(f"{name} touches an undriven qubit")
    if rows["xt-x90-128-q1.cq"]["text"].count("X90 q[1]") != 128 or "q[2]" in rows["xt-x90-128-q1.cq"]["text"]:
        raise AssertionError("the q1 circuit drives another qubit")
    units = cases.crosstalk_units()
    if len(units) != 8 or any(len(names) != 3 for _, names in units) or len(cases.usage("tuna_17")["crosstalk"]) != 24:
        raise AssertionError(units)
    anchors = dict(units)["anchors"]
    if anchors != ["readout-0.cq", "xt-prep1-A.cq", "xt-prep1-B.cq"]:
        raise AssertionError(anchors)
    if any(q >= cases.PROFILES["qx"]["nqubits"] for q in (*cases.CLASS_A["qx"], *cases.CLASS_B["qx"], *cases.PAIR)):
        raise AssertionError("a qx class exceeds the emulator")


def test_flag_is_the_bonferroni_quantile_and_fires_only_above_it() -> None:
    from statistics import NormalDist  # noqa: PLC0415

    if abs(NormalDist().inv_cdf(1 - 0.05 / 204) - cases.FLAG_Z) > 0.005:
        raise AssertionError(cases.FLAG_Z)
    se = math.sqrt(2 * 0.25 / 8192 + 2 * cases.JOB_LEVEL_SIGMA**2)
    above, below = cases.contrast_z(0.5 + 3.6 * se, 0.5, 8192), cases.contrast_z(0.5 + 3.3 * se, 0.5, 8192)
    if not abs(above) > cases.FLAG_Z > abs(below) or abs(above - 3.6) > 0.05:
        raise AssertionError((above, below))


def test_crosstalk_analysis_flags_a_shifted_class_reading_and_forms_98_contrasts() -> None:
    quiet = cases.analyze_crosstalk(cases.synthetic_crosstalk())
    if quiet["pooled"]["flagged"] != 0 or quiet["pooled"]["contrasts_formed"] != 98:
        raise AssertionError(quiet["pooled"])
    if len(quiet["rows"]) != 96 or {p["qubit"] for p in quiet["pair"]} != {1, 2}:
        raise AssertionError(quiet)
    loud = cases.analyze_crosstalk(cases.synthetic_crosstalk(shift_qubit=5, shift=0.05))
    flagged = [r for r in loud["rows"] if r["flagged"]]
    if len(flagged) != 6 or any(r["qubit"] != 5 or r["context"] != "A" for r in flagged):
        raise AssertionError(flagged)
    if loud["pooled"]["reading"] != "drive-context dependence" or "neighbor" in json.dumps(loud):
        raise AssertionError(loud["pooled"])
    small = cases.analyze_crosstalk(cases.synthetic_crosstalk(shift_qubit=5, shift=0.01))
    if small["pooled"]["flagged"] != 0:
        raise AssertionError(small["pooled"])


def test_local_twin_check_names_a_circuit_off_its_law() -> None:
    rows = cases.library("qx")
    by_text = {row["text"]: row for row in rows.values()}
    nqubits = cases.PROFILES["qx"]["nqubits"]

    def exact(text: str, iterations: int) -> dict[str, int]:
        row = by_text[text]
        driven = set(row["driven"])
        ones = round(row["expected_p1"] * iterations)

        def make(bit: bool) -> str:
            return "".join(("1" if bit and q in driven else "0") for q in reversed(range(nqubits)))

        return (
            {make(True): ones, make(False): iterations - ones}
            if 0 < ones < iterations
            else {make(row["expected_p1"] == 1.0): iterations}
        )

    if cases.local(exact):
        raise AssertionError(cases.local(exact))

    def broken(text: str, iterations: int) -> dict[str, int]:
        return {"0" * nqubits: iterations}

    if not any("t1-250" in p for p in cases.local(broken)):
        raise AssertionError("a circuit off its law went unnamed")


def test_self_test_reports_no_problem() -> None:
    if cases.self_test():
        raise AssertionError(cases.self_test())
