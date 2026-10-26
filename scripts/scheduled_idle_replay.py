"""Replay a retained dynamic IBM run with the service-scheduled idle written as explicit delays.

`live_run.noise_simulator` builds `NoiseModel.from_backend`, whose relaxation pass charges T1 and T2 only on gate
durations and explicit `delay` instructions. The service scheduler inserts idle the ISA never states: a qubit
waiting through another qubit's mid-circuit measurement and broadcast, or behind routing serialization. Every
retained dynamic PUB carries the service's compiled schedule in `metadata.compilation.scheduler_timing.timing`
(rows `branch,instruction,channel,t0,duration,kind` in cycles of the Target `dt`). This script rebuilds each
replica of each fused PUB on its physical qubits, inserts before every scheduled instruction the delay that
separates it from that qubit's previous instruction, replays the padded circuits under the noise model of the
Target and properties in force at the PUB's execution start, and summarizes them with the run's experiment group.

Matching: on each qubit the ISA instructions and the schedule instances on `Qubit q` in the `main` branch appear
in the same order. INIT, FINI, barrier, broadcast and virtual `rz` rows match nothing; a single-pulse gate (`sx`,
`x`, `cz`) is one instance per play row; a `measure` is one run of contiguous rows; a `reset` is one instance
whose measurement and conditional pulse sit one feed-forward latency apart. An `if_else` occupies the span of its
`then`/`else` rows on that qubit, or starts at the broadcast receive when its body has no rows there. A main-level
`delay` has no rows and advances the cursor by its own duration. A mismatch between the two orders raises.

Each replica also gets its exact branch-resolved law (dynamic_density), padded and unpadded. Aer's relaxation
pass (`NoiseModel._pass_manager`) acts on top-level delays only, so the exact path writes each delay's relaxation
channel in through that pass and then drops every delay, top level and branch body alike; a delay inside an
if_else body carries no noise under Aer either. The unpadded exact law is the control: it reproduces the record's
own exact model where the record keeps one. A record's declared `prep_excitation` runs in both paths, as the
leading X error of the sampled run and the initial bit flip of the exact law. The sampled laws stay beside the
exact ones, and every sampled frequency must lie within the simultaneous Hoeffding radius of its exact law. The
sampled path reuses the record's own replay seed (`live_run.SEED_SIMULATOR`), so it differs from the recorded replay
only by the inserted delays.

The padded replay adds incoherent idle only; the remaining gap to the measured laws is idle-time detuning, ZZ,
leakage and any other effect the Target's T1, T2 and gate errors do not express.

Usage:
    "$PYTHON" scripts/scheduled_idle_replay.py RUN_DIR --out RUN_DIR/idle-replay.json
    "$PYTHON" scripts/scheduled_idle_replay.py RUN_DIR --local-schedule --out RUN_DIR/local-idle-schedule.json
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import numpy as np  # noqa: E402
from qiskit import QuantumCircuit, qpy  # noqa: E402
from qiskit.circuit import Delay  # noqa: E402

SKIPPED_LABELS = ("INIT", "FINI", "barrier", "broadcast", "rz_")
# rz is a virtual frame change: zero duration, listed as shift_phase rows whose order beside a neighbouring
# zero-time row is arbitrary, so it neither consumes a schedule instance nor carries idle.
VIRTUAL = frozenset({"rz", "barrier"})
# Gates that play one pulse: each play row opens an instance, so two back-to-back sx stay two instances, while
# a measure's or reset's contiguous plays of one label form one.
SINGLE_PULSE = frozenset({"sx", "x", "cz", "xslow"})
HOEFFDING_TAIL = 0.01


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def schedule_rows(pub_file: Path) -> list[tuple[str, str, str, int, int, str]]:
    """Every scheduler_timing row of one retained PUB result."""
    payload = json.loads(pub_file.read_text(encoding="utf-8"))

    def find(node: Any) -> Any:
        if isinstance(node, dict):
            for key, value in node.items():
                if key == "scheduler_timing":
                    return value
                found = find(value)
                if found is not None:
                    return found
        elif isinstance(node, list):
            for value in node:
                found = find(value)
                if found is not None:
                    return found
        return None

    timing = find(payload)
    require(timing is not None, f"{pub_file}: no scheduler_timing")
    text = timing["timing"] if isinstance(timing, dict) else timing
    rows = []
    for line in text.splitlines() if isinstance(text, str) else text:
        branch, label, channel, t0, duration, kind = line.split(",")
        rows.append((branch, label, channel, int(t0), int(duration), kind.strip()))
    return rows


def instances(rows: list[tuple[str, str, str, int, int, str]], qubit: int) -> list[tuple[str, int, int]]:
    """Main-branch instances (label, start, end) on one qubit, in schedule order."""
    channel = f"Qubit {qubit}"
    mine = sorted(
        (row for row in rows if row[0] == "main" and row[2] == channel and not row[1].startswith(SKIPPED_LABELS)),
        key=lambda row: (row[3], row[3] + row[4]),
    )
    out: list[tuple[str, int, int]] = []
    for _, label, _, t0, duration, kind in mine:
        single_pulse = label.split("_")[0] in SINGLE_PULSE and kind == "play"
        # A reset is a measurement and a conditional pulse one feed-forward latency later: one instruction.
        joined = label.startswith("reset") or t0 <= (out[-1][2] if out else -1)
        if out and out[-1][0] == label and joined and not single_pulse:
            out[-1] = (label, out[-1][1], max(out[-1][2], t0 + duration))
        else:
            out.append((label, t0, t0 + duration))
    return out


def branch_span(
    rows: list[tuple[str, str, str, int, int, str]], qubit: int, after: int, before: int
) -> tuple[int, int]:
    """Span of then/else rows on a qubit between two main instances, or the broadcast receive if none."""
    channel = f"Qubit {qubit}"
    inner = [row for row in rows if row[0] != "main" and row[2] == channel and after <= row[3] < before]
    if inner:
        return min(row[3] for row in inner), max(row[3] + row[4] for row in inner)
    receives = [row[3] + row[4] for row in rows if row[2] == "Hub" and row[3] + row[4] <= before]
    require(bool(receives), f"qubit {qubit}: if_else without branch rows or a preceding broadcast")
    start = max(max(receives), after)
    return start, start


def padded_replica(
    fused: QuantumCircuit,
    rows: list[tuple[str, str, str, int, int, str]],
    qubits: list[int],
    registers: list[str],
    insert: bool = True,
) -> tuple[QuantumCircuit, dict[int, int]]:
    """The replica's instructions on its physical qubits with the scheduled idle inserted as delays.

    Returns the circuit and the total inserted idle per qubit in dt; insert=False returns the same replica with the
    same matching checks and no inserted delay.
    """
    keep = set(qubits)
    by_name = {register.name: register for register in fused.cregs}
    out = QuantumCircuit(fused.qubits, *(by_name[name] for name in registers), name=f"{fused.name}_idle_padded")
    queue = {q: instances(rows, q) for q in qubits}
    position = dict.fromkeys(qubits, 0)
    # -1 marks a qubit whose first scheduled instruction has not been reached; no idle precedes it.
    cursor = dict.fromkeys(qubits, -1)
    inserted = dict.fromkeys(qubits, 0)
    for instruction in fused.data:
        physical = [fused.find_bit(bit).index for bit in instruction.qubits]
        if not set(physical) <= keep:
            require(not set(physical) & keep, f"{fused.name}: an instruction straddles the replica boundary")
            continue
        name = instruction.operation.name
        if name in VIRTUAL:
            out.append(instruction)
            continue
        if name == "delay":
            for q in physical:
                if cursor[q] >= 0:
                    cursor[q] += int(instruction.operation.duration)
            out.append(instruction)
            continue
        starts: dict[int, tuple[int, int]] = {}
        for q in physical:
            if name == "if_else":
                after = max(cursor[q], 0)
                upcoming = queue[q][position[q]][1] if position[q] < len(queue[q]) else 1 << 62
                starts[q] = branch_span(rows, q, after, upcoming)
            else:
                require(
                    position[q] < len(queue[q]), f"{fused.name}: qubit {q} ran out of scheduled instances at {name}"
                )
                label, t0, t1 = queue[q][position[q]]
                require(label.split("_")[0] == name, f"{fused.name}: qubit {q} expects {name}, schedule has {label}")
                position[q] += 1
                starts[q] = (t0, t1)
        for q in physical:
            t0, t1 = starts[q]
            if cursor[q] >= 0 and t0 > cursor[q]:
                gap = t0 - cursor[q]
                if insert:
                    out.append(Delay(gap, unit="dt"), [fused.qubits[q]])
                inserted[q] += gap
            cursor[q] = max(t1, t0)
        out.append(instruction)
    for q in qubits:
        require(position[q] == len(queue[q]), f"{fused.name}: qubit {q} left {len(queue[q]) - position[q]} instances")
    return out, inserted


def list_schedule_idle(
    circuit: QuantumCircuit, duration: Callable[[str, tuple[int, ...]], int], qubits: list[int]
) -> dict[int, int]:
    """Idle per qubit, in dt, of an as-soon-as-possible list schedule of circuit under duration(name, qubits).

    Each instruction starts once every qubit it acts on is free. An if_else aligns its qubits and plays its true
    body; the measure-to-branch latency is not modeled. Idle is the span from a qubit's first to its last
    instruction minus the time it plays one; a circuit delay counts as idle, as the service schedule counts it.
    """
    cursor: dict[int, int] = {}
    first: dict[int, int] = {}
    busy = dict.fromkeys(qubits, 0)

    def play(name: str, physical: list[int], length: int | None = None) -> None:
        start = max(cursor.get(q, 0) for q in physical)
        span = duration(name, tuple(physical)) if length is None else length
        for q in physical:
            first.setdefault(q, start)
            cursor[q] = start + span
            if length is None:
                busy[q] += span

    for instruction in circuit.data:
        name = instruction.operation.name
        physical = [circuit.find_bit(bit).index for bit in instruction.qubits]
        if name in VIRTUAL:
            continue
        if name == "delay":
            play(name, physical, int(instruction.operation.duration))
        elif name == "if_else":
            aligned = max(cursor.get(q, 0) for q in physical)
            for q in physical:
                cursor[q] = aligned
            body = instruction.operation.blocks[0]
            for inner in body.data:
                inner_name = inner.operation.name
                if inner_name in VIRTUAL:
                    continue
                mapped = [physical[body.find_bit(bit).index] for bit in inner.qubits]
                play(inner_name, mapped, int(inner.operation.duration) if inner_name == "delay" else None)
        else:
            play(name, physical)
    return {q: cursor[q] - first[q] - busy[q] for q in qubits if q in first}


ReplicaItem = tuple[QuantumCircuit, list[tuple[str, str, str, int, int, str]], list[int], list[str]]


Replica = tuple[QuantumCircuit, QuantumCircuit, dict[int, int], bytes, bytes]


def replica_circuits(item: ReplicaItem) -> Replica:
    """The padded and unpadded replica of one (fused circuit, schedule rows, qubits, registers) item.

    Returns both circuits, the inserted idle per qubit and the qpy bytes of each circuit, which the exact path
    loads.
    """
    fused, rows, qubits, registers = item
    padded, inserted = padded_replica(fused, rows, qubits, registers)
    bare, _ = padded_replica(fused, rows, qubits, registers, insert=False)
    return padded, bare, inserted, _serialized(padded), _serialized(bare)


def _schedule_item(item: tuple[ReplicaItem, Any]) -> dict[str, dict[str, int]]:
    replica, target = item

    def duration(name: str, physical: tuple[int, ...]) -> int:
        return round(target[name][physical].duration / target.dt)

    _, bare, service_idle, _, _ = replica_circuits(replica)
    local = list_schedule_idle(bare, duration, replica[2])
    return {"service": {str(q): v for q, v in service_idle.items()}, "local": {str(q): v for q, v in local.items()}}


def local_schedule(run_dir: Path, out: Path) -> dict[str, Any]:
    """The service's inserted idle beside a local list schedule under the execution Target's durations."""
    from qiskit_ibm_runtime import QiskitRuntimeService

    import ibm_account
    import live_run
    import parallel

    record = json.loads((run_dir / "record.json").read_text(encoding="utf-8"))
    collected = json.loads((run_dir / "collect.json").read_text(encoding="utf-8"))
    job_id, job = next(iter(collected[0]["jobs"].items()))
    with (run_dir / "isa.qpy").open("rb") as stream:
        fused_by_name = {circuit.name: circuit for circuit in qpy.load(stream)}
    replicas = [replica["physical_qubits"] for replica in record["groups"][0]["replicas"]]
    service = ibm_account.open_service(QiskitRuntimeService)
    ibm_account.require_instance(ibm_account.recorded_instance(run_dir), live_run._instance_hash(service), job_id)
    backend = service.backend(job["backend"])
    keys: list[str] = []
    items: list[tuple[ReplicaItem, Any]] = []
    for index, pub in enumerate(record["execution_pubs"]):
        rows = schedule_rows(run_dir / "raw" / job_id / f"pub_{index:02d}.json")
        start = job["pub_timing"][pub["name"]]["execution_window_start"]
        target = backend.target_history(datetime=datetime.fromisoformat(start))
        for component in pub["components"]:
            for qubits, registers in zip(replicas, component["registers_by_replica"], strict=True):
                keys.append(component["member"])
                items.append(((fused_by_name[pub["name"]], rows, qubits, registers), target))
    members: dict[str, list[dict[str, dict[str, int]]]] = {}
    for member, row in zip(keys, parallel.ordered_map(_schedule_item, items, min_items=2), strict=True):
        members.setdefault(member, []).append(row)
    report = {"schema": "local-idle-schedule-v1", "run": run_dir.relative_to(ROOT).as_posix(), "members": members}
    out.write_text(json.dumps(report, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return report


def _without_delays(circuit: QuantumCircuit) -> QuantumCircuit:
    out = circuit.copy_empty_like()
    for instruction in circuit.data:
        operation = instruction.operation
        if operation.name == "delay":
            continue
        if operation.name == "if_else":
            blocks = [None if block is None else _without_delays(block) for block in operation.blocks]
            instruction = instruction.replace(operation=operation.replace_blocks(blocks))
        out.append(instruction)
    return out


def relaxed(circuit: QuantumCircuit, noise: Any) -> QuantumCircuit:
    """circuit with the noise model's delay relaxation written in as channels and every delay removed."""
    manager = noise._pass_manager()
    return _without_delays(manager.run(circuit) if manager is not None else circuit)


def _exact_law(item: tuple[bytes, Any, float]) -> list[float]:
    import dynamic_density

    payload, noise, prep_excitation = item
    circuit = qpy.load(io.BytesIO(payload))[0]
    law = dynamic_density.probabilities(relaxed(circuit, noise), noise, prep_excitation=prep_excitation)
    return [float(value) for value in law]


def _serialized(circuit: QuantumCircuit) -> bytes:
    buffer = io.BytesIO()
    qpy.dump(circuit, buffer)
    return buffer.getvalue()


def contract_values(contracts: list[dict[str, Any]], laws: dict[str, list[list[float]]]) -> dict[str, float]:
    """Each observable contract's value: the signed sum of its members' replica-mean scores."""
    values = {}
    for contract in contracts:
        terms = [
            term["sign"]
            * float(np.mean([np.asarray(term["values"]) @ np.asarray(law) for law in laws[term["member"]]]))
            for term in contract["terms"]
        ]
        values[contract["name"]] = float(np.sum(terms))
    return values


def replay(run_dir: Path, out: Path) -> dict[str, Any]:
    from qiskit_ibm_runtime import QiskitRuntimeService

    import dynamic_density
    import ibm_account
    import live_run
    import local_compute
    import parallel
    from experiments import all_experiment_groups

    record = json.loads((run_dir / "record.json").read_text(encoding="utf-8"))
    collected = json.loads((run_dir / "collect.json").read_text(encoding="utf-8"))
    jobs = collected[0]["jobs"]
    require(len(jobs) == 1, "one job per run")
    job_id, job = next(iter(jobs.items()))
    with (run_dir / "isa.qpy").open("rb") as stream:
        fused_by_name = {circuit.name: circuit for circuit in qpy.load(stream)}
    group_entry = record["groups"][0]
    group = next((g for g in all_experiment_groups() if g.name == group_entry["group"]), None)
    replicas = [replica["physical_qubits"] for replica in group_entry["replicas"]]
    service = ibm_account.open_service(QiskitRuntimeService)
    ibm_account.require_instance(ibm_account.recorded_instance(run_dir), live_run._instance_hash(service), job_id)
    backend = service.backend(job["backend"])
    prep_excitation = float(record.get("policy", {}).get("design", {}).get("prep_excitation") or 0.0)
    simulators: dict[str, Any] = {}
    padded: dict[str, list[np.ndarray]] = {}
    idle_dt: dict[str, list[dict[str, int]]] = {}
    exact_keys: list[tuple[str, str]] = []
    exact_items: list[tuple[bytes, Any, float]] = []
    replica_keys: list[str] = []
    replica_items: list[ReplicaItem] = []
    for index, pub in enumerate(record["execution_pubs"]):
        rows = schedule_rows(run_dir / "raw" / job_id / f"pub_{index:02d}.json")
        for component in pub["components"]:
            for qubits, registers in zip(replicas, component["registers_by_replica"], strict=True):
                replica_keys.append(component["member"])
                replica_items.append((fused_by_name[pub["name"]], rows, qubits, registers))
    built: dict[str, list[Replica]] = {}
    for member, triple in zip(replica_keys, parallel.ordered_map(replica_circuits, replica_items), strict=True):
        built.setdefault(member, []).append(triple)
    for pub in record["execution_pubs"]:
        start = job["pub_timing"][pub["name"]]["execution_window_start"]
        if start not in simulators:
            moment = datetime.fromisoformat(start)
            simulators[start] = live_run.noise_simulator(
                f"{backend.name}@{start}",
                backend.target_history(datetime=moment),
                backend.properties(datetime=moment),
                # A new simulation, not a byte replay: the host's current Aer build and policy run it.
                local_compute.settings(),
            )
        for component in pub["components"]:
            noise = simulators[start].options.noise_model
            circuits, gaps = [], []
            for circuit, _, inserted, padded_bytes, bare_bytes in built[component["member"]]:
                circuits.append(circuit)
                gaps.append({str(q): v for q, v in inserted.items()})
                for variant, payload in (("idle_padded", padded_bytes), ("unpadded", bare_bytes)):
                    exact_keys.append((variant, component["member"]))
                    exact_items.append((payload, noise, prep_excitation))
            sampled = (
                [dynamic_density.with_prep_excitation(circuit, prep_excitation) for circuit in circuits]
                if prep_excitation
                else circuits
            )
            result = local_compute.run(simulators[start], sampled, record["shots"], live_run.SEED_SIMULATOR)
            padded[component["member"]] = [
                live_run._distribution(result.get_counts(k), circuit.num_clbits) for k, circuit in enumerate(circuits)
            ]
            idle_dt[component["member"]] = gaps
    exact: dict[str, dict[str, list[list[float]]]] = {"idle_padded": {}, "unpadded": {}}
    for (variant, member), law in zip(exact_keys, parallel.ordered_map(_exact_law, exact_items), strict=True):
        exact[variant].setdefault(member, []).append(law)
    gaps_to_exact = [
        float(np.max(np.abs(np.asarray(sampled) - np.asarray(law))))
        for member, laws in padded.items()
        for sampled, law in zip(laws, exact["idle_padded"][member], strict=True)
    ]
    outcomes = sum(len(law) for laws in padded.values() for law in laws)
    radius = dynamic_density.hoeffding_radius(int(record["shots"]), outcomes, HOEFFDING_TAIL)
    require(
        max(gaps_to_exact) <= radius,
        f"sampled padded laws leave the Hoeffding radius {radius} of the exact laws: {max(gaps_to_exact)}",
    )
    contracts = record.get("observable_contracts", [])
    report: dict[str, Any] = {
        "schema": "scheduled-idle-replay-v1",
        "run": run_dir.relative_to(ROOT).as_posix(),
        "job_id": job_id,
        "group": group_entry["group"],
        "replicas": replicas,
        "inserted_idle_dt": idle_dt,
        "prep_excitation": prep_excitation,
        "idle_padded_laws": {name: [law.tolist() for law in laws] for name, laws in padded.items()},
        "exact_laws": exact,
        "sampled_to_exact": {"max_gap": max(gaps_to_exact), "radius": radius, "tail": HOEFFDING_TAIL},
    }
    if contracts:
        recorded = record.get("exact_model", {}).get("contrasts", {})
        report["contracts"] = {
            "idle_padded_exact": contract_values(contracts, exact["idle_padded"]),
            "unpadded_exact": contract_values(contracts, exact["unpadded"]),
            "idle_padded_sampled": contract_values(
                contracts, {name: [law.tolist() for law in laws] for name, laws in padded.items()}
            ),
            "recorded_exact": {name: entry["exact"] for name, entry in recorded.items()},
        }
    # A family run builds its group from family_configuration; its laws are reported without a group summary.
    if group is not None:

        def summaries(laws: dict[str, Any]) -> list[dict[str, Any]]:
            return [group.summarize({name: np.asarray(v[k]) for name, v in laws.items()}) for k in range(len(replicas))]

        report["summary_per_replica"] = {
            "idle_padded": summaries(padded),
            "idle_padded_exact": summaries(exact["idle_padded"]),
            "unpadded_exact": summaries(exact["unpadded"]),
            "replayed": collected[1]["replayed_statistics"]["summary_per_replica"],
            "measured": collected[1]["measured_statistics"]["summary_per_replica"],
        }
    out.write_text(json.dumps(report, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument(
        "--local-schedule", action="store_true", help="write the service idle beside a local list schedule, no replay"
    )
    args = parser.parse_args()
    if args.local_schedule:
        for member, rows in local_schedule(args.run_dir.resolve(), args.out)["members"].items():
            for row in rows:
                print(member, "service", json.dumps(row["service"]), "local", json.dumps(row["local"]))
        return 0
    report = replay(args.run_dir.resolve(), args.out)
    print("sampled_to_exact", json.dumps(report["sampled_to_exact"]))
    for source, values in report.get("contracts", {}).items():
        print(source, json.dumps(values))
    if "summary_per_replica" not in report:
        for name, laws in report["exact_laws"]["idle_padded"].items():
            print(name, np.round(np.asarray(laws[0])[:8], 4).tolist())
        return 0
    for key in sorted(report["summary_per_replica"]["measured"][0]):
        values = {
            source: float(np.mean([row[key] for row in rows]))
            for source, rows in report["summary_per_replica"].items()
            if all(isinstance(row.get(key), (int, float)) for row in rows)
        }
        if len(values) == len(report["summary_per_replica"]):
            print(f"{key:44s} " + "  ".join(f"{source} {value:+.4f}" for source, value in values.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
