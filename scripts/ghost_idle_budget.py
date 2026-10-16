"""Ghost idle budget: per audited run, the decoherence the replay leaves out by simulating an unscheduled circuit.

ghost_run replays each executed PUB's ISA circuit under
NoiseModel.from_backend, which attaches thermal relaxation to every gate
over its duration and to every explicit ``delay`` (RelaxationNoisePass),
and to nothing else: a qubit that waits while other qubits run gates, a
mid-circuit measurement or a feed-forward broadcast decoheres on hardware
and stays ideal in the replay. The executed schedule is retained: each raw
PUB under ``results/live/RUN/raw/JOB/pub_NN.json`` carries the
``scheduler_timing`` table the backend compiled, one row per pulse with its
channel, start and duration in dt, and ``isa.qpy`` holds the PUB's circuit
in the same order.

Per PUB and per qubit the script takes the window from the qubit's first
operation after initialization to its last before finalization, subtracts
the union of the qubit's play and capture intervals and the explicit delays
the ISA circuit names on it, and charges the remaining idle time t the
average gate infidelity of zero-temperature relaxation,
``r(t) = 1 - (2 F + 1) / 3`` with process fidelity
``F = (1 + exp(-t/T1) + 2 exp(-t/T2)) / 4`` and T2 capped at 2 T1, under the
calibration snapshot in force at the run's execution
(docs/evidence/ghost_runs/result.json). A qubit that idles in |0> loses
nothing on hardware and is charged as an average state, so the budget is an
upper estimate for idle relaxation. Summed over a run it gives the idle
error E_idle beside the run's summed reported CZ error E_cz; a fit that
absorbs the idle error into the CZ channels alone would need the factor
``c_idle = 1 + E_idle / E_cz``. The ghost error-scale sweep
(scripts/ghost_error_scale.py) fits that factor, so a fitted factor well
above c_idle locates error outside idle relaxation. Each run also records
its feed-forward broadcasts, resets and measurement captures, the events
whose errors the replay models as readout flips only.

Usage:
    "$PYTHON" scripts/ghost_idle_budget.py --out docs/evidence/ghost_error_scale/idle_budget.json
    "$PYTHON" scripts/ghost_idle_budget.py --check docs/evidence/ghost_error_scale/idle_budget.json
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

from qiskit import qpy  # noqa: E402

import parallel  # noqa: E402

GHOST_RESULT = ROOT / "docs/evidence/ghost_runs/result.json"
SCHEMA = "ghost-idle-budget-v1"
CHANNEL_QUBIT = re.compile(r"(\d+)$")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relaxation_infidelity(seconds: float, t1: float, t2: float) -> float:
    t2 = min(t2, 2.0 * t1)
    process = (1.0 + math.exp(-seconds / t1) + 2.0 * math.exp(-seconds / t2)) / 4.0
    return 1.0 - (2.0 * process + 1.0) / 3.0


def union_length(intervals: list[tuple[int, int]]) -> int:
    total = 0
    end = -1
    for start, stop in sorted(intervals):
        if start > end:
            total += stop - start
            end = stop
        elif stop > end:
            total += stop - end
            end = stop
    return total


def delays_by_qubit(circuit: Any) -> dict[int, int]:
    """Explicit delay duration in dt per physical qubit of an ISA circuit; the replay already relaxes these."""
    out: dict[int, int] = collections.defaultdict(int)
    for instruction in circuit.data:
        if instruction.operation.name == "delay":
            require(
                instruction.operation.unit == "dt", f"{circuit.name}: delay in {instruction.operation.unit}, not dt"
            )
            for qubit in instruction.qubits:
                out[circuit.find_bit(qubit).index] += int(instruction.operation.duration)
    return out


def pub_budget(timing: str, delays: dict[int, int], snapshot: dict[str, Any]) -> dict[str, Any]:
    dt = snapshot["dt"]
    cz_error = {tuple(entry["qargs"]): entry["error"] for entry in snapshot["instructions"]["cz"]}
    busy: dict[int, list[tuple[int, int]]] = collections.defaultdict(list)
    initialized: set[int] = set()
    cz_events: set[tuple[str, int]] = set()
    counts = {"broadcasts": 0, "resets": 0, "measure_captures": 0}
    e_cz = 0.0
    for row in timing.splitlines():
        branch, instruction, channel, start_text, duration_text, kind = row.split(",")
        head = instruction.split("_")[0]
        if kind == "broadcast":
            counts["broadcasts"] += 1
        if kind == "capture" and head == "reset":
            counts["resets"] += 1
        if kind == "capture" and head == "measure":
            counts["measure_captures"] += 1
        match = CHANNEL_QUBIT.search(channel)
        if match is None or branch != "main":
            continue
        qubit = int(match.group(1))
        start, duration = int(start_text), int(duration_text)
        if head == "INIT":
            initialized.add(qubit)
            continue
        if head == "FINI":
            continue
        if duration and kind in ("play", "capture"):
            busy[qubit].append((start, start + duration))
        if head == "cz" and kind == "play" and (instruction, start) not in cz_events:
            cz_events.add((instruction, start))
            a, b = (int(x) for x in instruction.split("_")[1:3])
            require((a, b) in cz_error or (b, a) in cz_error, f"cz {a}-{b} absent from the snapshot")
            e_cz += cz_error.get((a, b), cz_error.get((b, a), 0.0))
    require(set(delays) <= set(busy), "an ISA delay sits on a qubit the schedule never drives")
    idle_dt = 0
    e_idle = 0.0
    for qubit, intervals in busy.items():
        require(qubit in initialized, f"qubit {qubit} runs without an INIT row")
        window = max(stop for _, stop in intervals) - min(start for start, _ in intervals)
        idle = max(window - union_length(intervals) - delays.get(qubit, 0), 0)
        idle_dt += idle
        e_idle += relaxation_infidelity(idle * dt, snapshot["qubits"][qubit]["t1"], snapshot["qubits"][qubit]["t2"])
    return {"cz": len(cz_events), "e_cz": e_cz, "idle_dt": idle_dt, "e_idle": e_idle, **counts}


def run_budget(item: tuple[str, dict[str, str]]) -> dict[str, Any]:
    """Sum the PUB budgets of one run; each PUB takes the snapshot its replayed members executed under."""
    run, member_snapshot = item
    run_dir = ROOT / run
    with (run_dir / "isa.qpy").open("rb") as handle:
        circuits = {circuit.name: circuit for circuit in qpy.load(handle)}
    record = json.loads((run_dir / "record.json").read_text(encoding="utf-8"))
    members = {pub["name"]: [c["member"] for c in pub["components"]] for pub in record["execution_pubs"]}
    snapshots: dict[str, dict[str, Any]] = {}
    totals: dict[str, Any] = collections.Counter()
    digests = []
    used: set[str] = set()
    for path in sorted(run_dir.glob("raw/*/pub_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        name = data["pub_name"]
        names = {member_snapshot[m] for m in members[name] if m in member_snapshot}
        if not names:
            continue
        require(len(names) == 1, f"{run} {name}: members executed under {len(names)} snapshots")
        snapshot_path = names.pop()
        used.add(snapshot_path)
        if snapshot_path not in snapshots:
            snapshots[snapshot_path] = json.loads((ROOT / snapshot_path).read_text(encoding="utf-8"))
        timing = data["metadata"]["compilation"]["scheduler_timing"]["timing"]
        totals.update(pub_budget(timing, delays_by_qubit(circuits[name]), snapshots[snapshot_path]))
        totals["pubs"] += 1
        digests.append((name, sha256(path)))
    require(totals["pubs"] > 0, f"{run}: no PUB carries a replayed member")
    dt = {snapshots[path]["dt"] for path in used}
    require(len(dt) == 1, f"{run}: snapshots disagree on dt")
    e_cz = totals["e_cz"]
    return {
        "run": run,
        "snapshots": {path: sha256(ROOT / path) for path in sorted(used)},
        "isa_qpy_sha256": sha256(run_dir / "isa.qpy"),
        "raw_pubs_sha256": hashlib.sha256(json.dumps(sorted(digests)).encode()).hexdigest(),
        "pubs": totals["pubs"],
        "cz": totals["cz"],
        "e_cz": round(e_cz, 6),
        "idle_us": round(totals["idle_dt"] * dt.pop() * 1e6, 3),
        "e_idle": round(totals["e_idle"], 6),
        "c_idle": round(1.0 + totals["e_idle"] / e_cz, 4) if e_cz else None,
        "broadcasts": totals["broadcasts"],
        "resets": totals["resets"],
        "measure_captures": totals["measure_captures"],
    }


def audited() -> list[tuple[str, dict[str, str]]]:
    result = json.loads(GHOST_RESULT.read_text(encoding="utf-8"))
    return [(run["run"], run["execution_snapshot"]) for run in result["runs"] if "execution_snapshot" in run]


def build() -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "ghost_runs_sha256": sha256(GHOST_RESULT),
        "runs": parallel.ordered_map(run_budget, audited(), min_items=1),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    require((args.out is None) != (args.check is None), "give exactly one of --out or --check")
    text = json.dumps(build(), indent=1) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
        return 0
    require(args.check.read_text(encoding="utf-8") == text, f"{args.check} differs from the recomputed budget")
    print(f"ghost idle budget: {len(json.loads(text)['runs'])} runs match {args.check}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
