"""Adjudicate a collected live run from its lossless raw results.

The preregistered analysis in collect.json reduces each replica to a rounded
marginal distribution. This module reads the shot-ordered registers under
raw/<job_id>/ and the backend scheduler tables each PUB carried, and answers
the questions that reduction cannot:

- per-bit structure of the folded-QPE outcomes (the first bit precedes the
  mid-circuit measurement, reset, and feed-forward; the second follows them);
- a schedule-aware replay: the archived circuit of every replica with the
  idle time the backend scheduler table shows inserted as delays, so the
  execution-time noise model charges T1 and T2 relaxation for the time the
  work register waits on measurement, broadcast, and reset;
- drift along the shot order and shot-wise correlation between replicas of
  one PUB;
- the scheduled feed-forward segment (broadcast and receive rows) and the
  packed-minus-reference schedule difference per qubit;
- the distribution-free Hoeffding view of each matched packing endpoint.

Its output, adjudication.json, carries analysis_digest, the sha256 of this
module and live_run.py, so a later analysis of the same raw files under other
code is a separate artifact. The command needs the runtime service only for
the execution-time calibration; it submits nothing.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit, qpy
from qiskit.circuit import Delay

ANALYSIS_SEED = 20261011
BLOCK_SHOTS = 512
QPE_PREFIX = "folded_qpe"
SHOR_PREFIX = "hybrid_shor"

ScheduleTable = dict[int, list[tuple[str, int, int]]]


class AdjudicationError(RuntimeError):
    pass


def analysis_digest() -> str:
    here = Path(__file__).resolve().parent
    digest = hashlib.sha256()
    for name in ("adjudicate.py", "live_run.py"):
        digest.update(name.encode())
        digest.update((here / name).read_bytes())
    return digest.hexdigest()


# --- scheduler table ---------------------------------------------------------


def parse_schedule(timing: str) -> tuple[list[tuple[str, str, str, int, int, str]], ScheduleTable]:
    """Rows (block, op, channel, start, duration, kind) and per-qubit instruction instances of a scheduler table.

    The table lists one row per pulse-level event, several per instruction:
    an sx carries a play row and a zero-length frame row, a measure carries
    stimulus plays, a capture, and trailing plays, a reset a measure plus a
    conditional play that starts after the capture returns. Rows of one
    label fold into one instance; a gate row of positive length that starts
    at or after the current instance's end opens a new instance, so four
    consecutive cz on one pair stay four instances while the frame rows and
    the chained measure rows stay inside theirs.
    """
    rows: list[tuple[str, str, str, int, int, str]] = []
    for line in timing.strip().split("\n"):
        block, op, channel, start_text, duration_text, kind = line.split(",")
        rows.append((block, op, channel, int(start_text), int(duration_text), kind))
    per_qubit: ScheduleTable = defaultdict(list)
    for block, op, _channel, start, duration, _kind in rows:
        if block != "main" or op == "barrier" or op.startswith(("INIT", "FINI", "broadcast", "receive")):
            continue
        gate = not op.startswith(("measure", "reset"))
        for qubit in (int(token) for token in op.split("_")[1:]):
            sequence = per_qubit[qubit]
            if sequence and sequence[-1][0] == op and not (gate and duration > 0 and start >= sequence[-1][2]):
                label, first, last = sequence[-1]
                sequence[-1] = (label, min(first, start), max(last, start + duration))
            else:
                sequence.append((op, start, start + duration))
    return rows, dict(per_qubit)


def feed_forward_segment(rows: list[tuple[str, str, str, int, int, str]]) -> dict[str, Any]:
    """The scheduled classical round trip and the measure-to-reset span of a dynamic PUB."""
    broadcasts = [(start, duration) for _b, op, _c, start, duration, _k in rows if op == "broadcast"]
    receives = [(start, duration) for _b, op, _c, start, duration, _k in rows if op == "receive"]
    measures = [start for _b, op, _c, start, _d, kind in rows if op.startswith("measure") and kind == "capture"]
    resets = [start + duration for _b, op, _c, start, duration, _k in rows if op.startswith("reset")]
    end = max((start + duration for _b, _o, _c, start, duration, _k in rows), default=0)
    return {
        "broadcast_dt": [duration for _s, duration in broadcasts],
        "receive_dt": [duration for _s, duration in receives],
        "round_trip_dt": [
            (r_start + r_dur) - b_start
            for (b_start, _b_dur), (r_start, r_dur) in zip(broadcasts, receives, strict=False)
        ],
        "first_capture_to_last_reset_dt": (max(resets) - min(measures)) if measures and resets else None,
        "circuit_end_dt": end,
    }


def schedule_offsets(packed: ScheduleTable, reference: ScheduleTable, qubits: list[int]) -> dict[str, Any]:
    """Per-qubit start-time offsets of the packed schedule over the reference on identical instruction sequences."""
    out: dict[str, Any] = {}
    for qubit in qubits:
        a = [(label, end - start) for label, start, end in packed.get(qubit, [])]
        b = [(label, end - start) for label, start, end in reference.get(qubit, [])]
        if a != b:
            out[str(qubit)] = {"identical_sequence": False}
            continue
        offsets = [pa[1] - pr[1] for pa, pr in zip(packed[qubit], reference[qubit], strict=True)]
        steps = sorted({offset for offset in offsets})
        out[str(qubit)] = {"identical_sequence": True, "offset_steps_dt": steps, "final_offset_dt": offsets[-1]}
    return out


# --- circuits ------------------------------------------------------------------


def carve_replica(circuit: QuantumCircuit, qubits: list[int]) -> QuantumCircuit:
    """The instructions of one replica, on the full-width circuit, so Aer truncates the rest."""
    wanted = {circuit.qubits[q] for q in qubits}
    out = circuit.copy_empty_like()
    for instruction in circuit.data:
        if instruction.operation.name == "barrier":
            continue
        touched = [q in wanted for q in instruction.qubits]
        if any(touched):
            if not all(touched):
                raise AdjudicationError("an instruction crosses replica boundaries")
            out.append(instruction)
    return out


def schedule_aware(circuit: QuantumCircuit, table: ScheduleTable) -> tuple[QuantumCircuit, list[str]]:
    """circuit with delay(gap) on each qubit before every instruction the scheduler table starts after idle time.

    Each qubit's instructions are walked in circuit order against the
    table's instances of the same label (a cz matches either qubit order).
    The returned mismatches name instructions the table does not carry at
    that position; such a qubit gets no further delays.
    """
    index = {qubit: position for position, qubit in enumerate(circuit.qubits)}
    counters: dict[int, int] = defaultdict(int)
    last_end: dict[int, int] = {}
    blocked: set[int] = set()
    out = circuit.copy_empty_like()
    mismatches: list[str] = []
    for instruction in circuit.data:
        name = instruction.operation.name
        qubits = [index[q] for q in instruction.qubits]
        if name in ("barrier", "if_else", "delay"):
            out.append(instruction)
            continue
        label = f"{name}_" + "_".join(str(q) for q in qubits)
        for qubit in qubits:
            if qubit in blocked:
                continue
            sequence = table.get(qubit, [])
            k = counters[qubit]
            same = k < len(sequence) and (
                sequence[k][0] == label
                or (name == "cz" and set(sequence[k][0].split("_")[1:]) == {str(q) for q in qubits})
            )
            if not same:
                expected = sequence[k][0] if k < len(sequence) else None
                mismatches.append(f"qubit {qubit} instruction {k} {label} vs {expected}")
                blocked.add(qubit)
                continue
            _label, start, end = sequence[k]
            gap = start - last_end.get(qubit, start)
            if gap > 0:
                out.append(Delay(gap, unit="dt"), [circuit.qubits[qubit]])
            last_end[qubit] = end
            counters[qubit] += 1
        out.append(instruction)
    return out, mismatches


def inserted_delay_dt(circuit: QuantumCircuit) -> int:
    return sum(int(inst.operation.duration) for inst in circuit.data if inst.operation.name == "delay")


# --- outcomes ------------------------------------------------------------------


def bit_values(bitstrings: list[str]) -> np.ndarray:
    return np.array([int(bits, 2) for bits in bitstrings], dtype=np.int64)


def qpe_statistics(values: np.ndarray, label: int) -> dict[str, Any]:
    """Correctness of the two-bit folded-QPE outcome and of each bit against the prepared label."""
    bit0 = values & 1
    bit1 = (values >> 1) & 1
    ok0 = bit0 == (label & 1)
    ok1 = bit1 == ((label >> 1) & 1)
    both = ok0 & ok1
    return {
        "p_correct": float(both.mean()),
        "p_bit0_correct": float(ok0.mean()),
        "p_bit1_correct_given_bit0_correct": float(ok1[ok0].mean()) if ok0.any() else None,
        "p_bit1_correct_given_bit0_wrong": float(ok1[~ok0].mean()) if (~ok0).any() else None,
        "distribution": (np.bincount(values, minlength=4) / len(values)).tolist(),
    }


def shor_statistics(values: np.ndarray, phase_bits: int) -> dict[str, Any]:
    """Distribution of the measured phase bits and the factorable fraction for order 4 (odd top pair)."""
    varying = [bit for bit in range(phase_bits) if np.any((values >> bit) & 1)]
    top = (values >> (phase_bits - 2)) & 3
    low = values & ((1 << (phase_bits - 2)) - 1)
    return {
        "varying_bits": varying,
        "p_low_bits_zero": float(np.mean(low == 0)),
        "top_pair_distribution": (np.bincount(top, minlength=4) / len(values)).tolist(),
        "factorable": float(np.mean(top % 2 == 1)),
    }


def hoeffding_interval(difference: float, shots: int, confidence: float = 0.90) -> tuple[float, float]:
    radius = math.sqrt(0.5 * (2.0 / shots) * math.log(2 / (1 - confidence)))
    return difference - radius, difference + radius


def block_means(indicator: np.ndarray, block: int = BLOCK_SHOTS) -> list[float]:
    return [float(indicator[k : k + block].mean()) for k in range(0, len(indicator), block)]


# --- the run ---------------------------------------------------------------------


def _member_label(member: str) -> int | None:
    if member.startswith(QPE_PREFIX):
        if "null" in member:
            return 0
        return int(member.split("_s")[1].split("_")[0])
    return None


def _simulate(simulator: Any, circuit: QuantumCircuit, shots: int, seed: int) -> dict[str, np.ndarray]:
    result = simulator.run(circuit, shots=shots, seed_simulator=seed, memory=True).result()
    names = [register.name for register in circuit.cregs]
    per_register: dict[str, list[int]] = {name: [] for name in names}
    for memory in result.get_memory(circuit):
        for name, part in zip(reversed(names), memory.split(" "), strict=True):
            per_register[name].append(int(part, 2))
    return {name: np.array(values, dtype=np.int64) for name, values in per_register.items()}


def adjudicate(service: Any, run_dir: Path, seed: int = ANALYSIS_SEED) -> dict[str, Any]:
    import live_run

    record = json.loads((run_dir / "record.json").read_text())
    circuits = {c.name: c for c in qpy.load(io.BytesIO((run_dir / "isa.qpy").read_bytes()))}
    jobs = record.get("submission", {}).get("jobs") or []
    if not jobs:
        raise AdjudicationError(f"{run_dir} records no submitted jobs")
    shots = int(record["shots"])
    out: dict[str, Any] = {
        "run": run_dir.name,
        "analysis_digest": analysis_digest(),
        "experiment_digest": record.get("experiment_digest"),
        "seed": seed,
        "jobs": {},
    }
    replicas_by_group = {group["group"]: group["replicas"] for group in record["groups"]}
    for job_entry in jobs:
        job_id = job_entry["job_id"]
        raw_dir = run_dir / live_run.RAW_DIRECTORY / job_id
        if not (raw_dir / "index.json").exists():
            raise AdjudicationError(f"{raw_dir} holds no preserved raw result; run live_run.py --preserve-raw first")
        index = json.loads((raw_dir / "index.json").read_text())
        for name, digest in index["files"].items():
            if hashlib.sha256((raw_dir / name).read_bytes()).hexdigest() != digest:
                raise AdjudicationError(f"{raw_dir / name} differs from its indexed sha256")
        result_metadata = json.loads((raw_dir / "result_metadata.json").read_text())
        metrics = json.loads((raw_dir / "job_metrics.json").read_text())
        chunks = result_metadata.get("executor", {}).get("chunk_timing") or []
        start = datetime.fromisoformat(chunks[0]["start"]) if chunks else None
        backend = service.backend(job_entry["backend"])
        if start is None:
            raise AdjudicationError(f"job {job_id} carries no execution chunk to date its calibration")
        props = backend.properties(datetime=start)
        target = backend.target_history(datetime=start)
        simulator = live_run.noise_simulator(f"{backend.name}@{start.isoformat()}", target, props)
        dt = float(target.dt)
        job_out: dict[str, Any] = {
            "backend": job_entry["backend"],
            "execution_start": start.isoformat(),
            "calibration": str(props.last_update_date),
            "dt_seconds": dt,
            "metrics": metrics,
            "pubs": {},
            "coherence_us": {},
        }
        tables: dict[str, ScheduleTable] = {}
        pub_rows: dict[str, Any] = {}
        pub_raw: dict[str, Any] = {}
        for pub_index, manifest in enumerate(job_entry["pubs"]):
            raw = json.loads((raw_dir / f"pub_{pub_index:02d}.json").read_text())
            pub_raw[manifest["name"]] = raw
            timing = raw["metadata"].get("compilation", {}).get("scheduler_timing", {})
            if "timing" in timing:
                rows, table = parse_schedule(timing["timing"])
                tables[manifest["name"]] = table
                pub_rows[manifest["name"]] = rows
        for pub_index, manifest in enumerate(job_entry["pubs"]):
            name = manifest["name"]
            raw = pub_raw[name]
            circuit = circuits[name]
            pub_out: dict[str, Any] = {"components": [], "schedule": None}
            if name in pub_rows:
                pub_out["schedule"] = feed_forward_segment(pub_rows[name])
                pub_out["schedule"]["circuit_duration_dt"] = raw["metadata"]["compilation"]["scheduler_timing"].get(
                    "circuit_duration"
                )
            for component in manifest["components"]:
                member = component["member"]
                group_replicas = replicas_by_group[component["group"]]
                label = _member_label(member)
                for r, registers in enumerate(component["registers_by_replica"]):
                    register = registers[0]
                    bits = raw["registers"][register]
                    hardware = bit_values(bits["bitstrings"])
                    qubits = list(group_replicas[r]["physical_qubits"])
                    sub = carve_replica(circuit, qubits)
                    aware, mismatches = schedule_aware(sub, tables.get(name, {}))
                    archived_replay = _simulate(simulator, sub, shots, seed + 7 * pub_index + r)
                    aware_replay = _simulate(simulator, aware, shots, seed + 1000 + 7 * pub_index + r)
                    if label is not None:
                        views = {
                            "hardware": qpe_statistics(hardware, label),
                            "replay_archived": qpe_statistics(archived_replay[register], label),
                            "replay_schedule_aware": qpe_statistics(aware_replay[register], label),
                        }
                        indicator = (hardware == label).astype(float)
                    else:
                        phase_bits = int(bits["num_bits"])
                        views = {
                            "hardware": shor_statistics(hardware, phase_bits),
                            "replay_archived": shor_statistics(archived_replay[register], phase_bits),
                            "replay_schedule_aware": shor_statistics(aware_replay[register], phase_bits),
                        }
                        indicator = ((hardware >> (phase_bits - 2)) % 2 == 1).astype(float)
                    pub_out["components"].append(
                        {
                            "member": member,
                            "replica": r,
                            "register": register,
                            "physical_qubits": qubits,
                            "schedule_mismatches": mismatches,
                            "inserted_delay_dt": inserted_delay_dt(aware),
                            "views": views,
                            "shot_blocks": block_means(indicator),
                            "indicator": indicator.tolist(),
                        }
                    )
            job_out["pubs"][name] = pub_out
        # Shot-wise correlation between every pair of replicas of one PUB.
        for pub_out in job_out["pubs"].values():
            components = pub_out["components"]
            correlations: dict[str, float] = {}
            for a in range(len(components)):
                for b in range(a + 1, len(components)):
                    x = np.array(components[a]["indicator"])
                    y = np.array(components[b]["indicator"])
                    if x.std() == 0 or y.std() == 0:
                        continue
                    left = f"{components[a]['member']}/r{components[a]['replica']}"
                    right = f"{components[b]['member']}/r{components[b]['replica']}"
                    correlations[f"{left} ~ {right}"] = float(np.corrcoef(x, y)[0, 1])
            pub_out["shotwise_correlation"] = correlations
            pub_out["shotwise_correlation_null_sd"] = 1 / math.sqrt(shots)
            for component in components:
                del component["indicator"]
        # Packed-versus-reference schedules on the replica-0 qubits of each group.
        packed = next((m["name"] for m in job_entry["pubs"] if len(m["components"]) > 1), None)
        reference = next((m["name"] for m in job_entry["pubs"] if all(c["reference"] for c in m["components"])), None)
        if packed and reference and packed in tables and reference in tables:
            qubits = sorted({q for g in replicas_by_group.values() for q in g[0]["physical_qubits"]})
            job_out["packed_minus_reference_schedule"] = {
                "packed_pub": packed,
                "reference_pub": reference,
                "per_qubit": schedule_offsets(tables[packed], tables[reference], qubits),
            }
        used = sorted({q for g in replicas_by_group.values() for rep in g for q in rep["physical_qubits"]})
        job_out["coherence_us"] = {str(q): {"t1": props.t1(q) * 1e6, "t2": props.t2(q) * 1e6} for q in used}
        charge = metrics.get("usage", {}).get("qpu_charge_time_seconds")
        execution_ns = metrics.get("circuits_execution_time_ns")
        submitted = shots * len(job_entry["pubs"])
        job_out["throughput"] = {
            "submitted_pub_shots": submitted,
            "qpu_charge_time_seconds": charge,
            "circuits_execution_time_ns": execution_ns,
            "execution_seconds_per_shot": (execution_ns / 1e9 / submitted) if execution_ns else None,
            "mean_scheduled_seconds_per_shot": float(
                np.mean([p["schedule"]["circuit_duration_dt"] for p in job_out["pubs"].values() if p["schedule"]]) * dt
            )
            if any(p["schedule"] for p in job_out["pubs"].values())
            else None,
            "default_rep_delay_seconds": getattr(backend.configuration(), "default_rep_delay", None),
        }
        out["jobs"][job_id] = job_out
    live_run._write_text_atomically(run_dir / "adjudication.json", json.dumps(out, indent=1, sort_keys=True) + "\n")
    return out


# --- self-check ------------------------------------------------------------------


def _check() -> None:
    timing = "\n".join(
        [
            "main,barrier,Qubit 1,33,0,barrier",
            "main,INIT_1,Qubit 1,33,64,play",
            "main,rz_1,Qubit 1,100,0,shift_phase",
            "main,sx_1,Qubit 1,100,8,play",
            "main,sx_1,Qubit 1,108,0,shift_phase",
            "main,cz_1_2,Qubit 1,120,17,play",
            "main,cz_1_2,Qubit 2,120,17,play",
            "main,cz_1_2,Qubit 1,137,0,shift_phase",
            "main,cz_1_2,Qubit 1,140,17,play",
            "main,cz_1_2,Qubit 2,140,17,play",
            "main,measure_1,Qubit 1,200,64,play",
            "main,measure_1,Qubit 1,264,108,play",
            "main,measure_1,AWGR0_1,300,325,capture",
            "main,broadcast,Hub,300,533,broadcast",
            "main,receive,Receive,833,7,receive",
            "main,reset_1,Qubit 1,900,64,play",
            "main,reset_1,AWGR0_1,964,325,capture",
            "main,reset_1,Qubit 1,1400,8,play",
            "then,rz_1,Qubit 1,1500,0,shift_phase",
            "main,sx_2,Qubit 2,1500,8,play",
            "main,FINI_1,Qubit 1,1600,64,play",
        ]
    )
    rows, table = parse_schedule(timing)
    labels = [label for label, _s, _e in table[1]]
    if labels != ["rz_1", "sx_1", "cz_1_2", "cz_1_2", "measure_1", "reset_1"]:
        raise AdjudicationError(f"instance grouping reads {labels}")
    if table[1][5] != ("reset_1", 900, 1408) or table[1][4] != ("measure_1", 200, 625):
        raise AdjudicationError(f"measure or reset instance bounds read {table[1][4:]}")
    segment = feed_forward_segment(rows)
    if segment["round_trip_dt"] != [540] or segment["first_capture_to_last_reset_dt"] != 1108:
        raise AdjudicationError(f"feed-forward segment reads {segment}")
    circuit = QuantumCircuit(3, 1)
    circuit.rz(0.5, 1)
    circuit.sx(1)
    circuit.cz(1, 2)
    circuit.cz(2, 1)
    circuit.measure(1, 0)
    circuit.reset(1)
    circuit.sx(2)
    aware, mismatches = schedule_aware(circuit, table)
    if mismatches:
        raise AdjudicationError(f"a matching schedule reports mismatches {mismatches}")
    delays = [
        (aware.find_bit(inst.qubits[0]).index, int(inst.operation.duration))
        for inst in aware.data
        if inst.operation.name == "delay"
    ]
    # Qubit 1 idles 12 dt before its first sx, both qubits 3 dt between the
    # two cz, qubit 1 43 dt before the measure and 275 dt between measure and
    # reset, and qubit 2 waits out the measurement, round trip, and reset.
    if delays != [(1, 12), (2, 3), (1, 3), (1, 43), (1, 275), (2, 1343)]:
        raise AdjudicationError(f"inserted delays read {delays}")
    values = np.array([1, 1, 3, 0, 1, 1, 1, 2])
    stats = qpe_statistics(values, 1)
    if (
        stats["p_correct"] != 0.625
        or stats["p_bit0_correct"] != 0.75
        or stats["p_bit1_correct_given_bit0_correct"] != 5 / 6
    ):
        raise AdjudicationError(f"QPE statistics read {stats}")
    shor = shor_statistics(np.array([0, 64, 128, 192, 192]), 8)
    if shor["varying_bits"] != [6, 7] or shor["factorable"] != 0.6 or shor["p_low_bits_zero"] != 1.0:
        raise AdjudicationError(f"Shor statistics read {shor}")
    low, high = hoeffding_interval(-0.0036, 4096)
    if abs(low + 0.030644) > 1e-5 or abs(high - 0.023444) > 1e-5:
        raise AdjudicationError(f"Hoeffding interval reads {(low, high)}")
    if block_means(np.array([1.0, 0.0, 1.0, 1.0]), 2) != [0.5, 1.0]:
        raise AdjudicationError("block means")
    print("adjudicate self-check passed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run", nargs="?", type=Path, help="run directory with record.json, isa.qpy, and raw/")
    parser.add_argument("--seed", type=int, default=ANALYSIS_SEED)
    parser.add_argument("--check", action="store_true", help="run the self-check on synthetic data and exit")
    args = parser.parse_args()
    if args.check:
        _check()
        return 0
    if args.run is None:
        parser.error("a run directory or --check is required")
    from qiskit_ibm_runtime import QiskitRuntimeService

    try:
        out = adjudicate(QiskitRuntimeService(), args.run, args.seed)
    except AdjudicationError as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    for job_id, job in out["jobs"].items():
        print(f"job {job_id}: {len(job['pubs'])} PUBs adjudicated; analysis digest {out['analysis_digest'][:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
