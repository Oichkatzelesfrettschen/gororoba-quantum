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

Its output, adjudication-<digest>-seed<seed>.json, is named by
analysis_digest, the sha256 of this module and live_run.py, and by the
replay seed, so a later analysis of the same raw files under other code or
another seed is a separate artifact beside the earlier one. The command needs the runtime service only for
the execution-time calibration; it submits nothing.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import sys
from collections import Counter, defaultdict
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
    An rz the table does not carry at that position is a virtual rotation the
    scheduler elided (the null circuits' conditional phases, for one) and is
    passed through without advancing the table. Any other mismatch names the
    instruction and stops the qubit's matching; the caller treats a circuit
    with remaining mismatches as having no schedule-aware view.
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
                if name == "rz":
                    continue
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


def generic_statistics(values: np.ndarray, bits: int) -> dict[str, Any]:
    """Outcome probabilities of a register whose decoder this module does not carry."""
    counts = Counter(int(v) for v in values)
    total = len(values)
    top = counts.most_common(16)
    return {
        "num_bits": bits,
        "modal_outcome": format(top[0][0], f"0{bits}b") if top else None,
        "outcome_probabilities": {format(value, f"0{bits}b"): count / total for value, count in top},
        "statistics": "unsupported member family: outcome probabilities only",
    }


def pub_starts(result_metadata: dict[str, Any], count: int) -> list[list[datetime]]:
    """Each PUB's distinct execution-chunk starts from the result metadata, sorted; empty when no chunk names it.

    A PUB can span several chunks (live_run.pub_windows); a PUB with more than
    one start may have executed under more than one calibration, and its
    shots carry no chunk tag, so the caller withholds its replay.
    """
    chunks = result_metadata.get("executor", {}).get("chunk_timing") or []
    return [
        sorted(
            {
                datetime.fromisoformat(chunk["start"])
                for chunk in chunks
                if any(int(part["idx_item"]) == idx for part in chunk.get("parts", []))
            }
        )
        for idx in range(count)
    ]


def latest_metrics(raw_dir: Path, index: dict[str, Any]) -> dict[str, Any]:
    """The newest job-metrics snapshot the raw index lists (job metrics finalize after the job)."""
    names = index.get("metrics") or ["job_metrics.json"]
    name = index.get("metrics_latest") or names[-1]
    digests = index.get("metrics_sha256") or []
    if name not in names or len(digests) != len(names):
        raise AdjudicationError(f"{raw_dir}/index.json lists no digest for the metrics snapshot {name}")
    if hashlib.sha256((raw_dir / name).read_bytes()).hexdigest() != digests[names.index(name)]:
        raise AdjudicationError(f"{raw_dir / name} differs from its indexed sha256")
    return dict(json.loads((raw_dir / name).read_text()))


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
    qpy_bytes = (run_dir / "isa.qpy").read_bytes()
    expected_qpy = record.get("submission", {}).get("qpy_archive_sha256")
    if hashlib.sha256(qpy_bytes).hexdigest() != expected_qpy:
        raise AdjudicationError("isa.qpy differs from the archive digest checkpointed before submission")
    circuits = {c.name: c for c in qpy.load(io.BytesIO(qpy_bytes))}
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
        metrics = latest_metrics(raw_dir, index)
        backend = service.backend(job_entry["backend"])
        pub_chunk_starts = pub_starts(result_metadata, len(job_entry["pubs"]))
        if any(not own for own in pub_chunk_starts):
            missing = [m["name"] for m, own in zip(job_entry["pubs"], pub_chunk_starts, strict=True) if not own]
            raise AdjudicationError(f"job {job_id}: no execution chunk dates the calibration of {missing}")
        # One calibration, Target, and simulator per distinct chunk start: a
        # PUB executed after a calibration update replays under its own, and
        # a PUB spanning several starts gets no replay at all.
        calibrations: dict[datetime, tuple[Any, Any, Any]] = {}
        replay_seed = seed
        for own in pub_chunk_starts:
            start = own[0]
            if len(own) == 1 and start not in calibrations:
                props = backend.properties(datetime=start)
                target = backend.target_history(datetime=start)
                simulator = live_run.noise_simulator(f"{backend.name}@{start.isoformat()}", target, props)
                calibrations[start] = (props, target, simulator)
        first_start = min(calibrations)
        dt = float(calibrations[first_start][1].dt)
        job_out: dict[str, Any] = {
            "backend": job_entry["backend"],
            "execution_start": first_start.isoformat(),
            "calibrations": {
                start.isoformat(): {"calibration": str(props.last_update_date), "dt_seconds": float(target.dt)}
                for start, (props, target, _sim) in sorted(calibrations.items())
            },
            "metrics": metrics,
            "pubs": {},
            "coherence_us": {},
        }
        used_qubits: dict[datetime, set[int]] = defaultdict(set)
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
            own_starts = pub_chunk_starts[pub_index]
            pub_start = own_starts[0]
            spans_chunks = len(own_starts) > 1
            if spans_chunks:
                calibration_text: str | None = None
                simulator = None
            else:
                props, _target, simulator = calibrations[pub_start]
                calibration_text = str(props.last_update_date)
            pub_out: dict[str, Any] = {
                "components": [],
                "schedule": None,
                "execution_start": pub_start.isoformat(),
                "chunk_starts": [moment.isoformat() for moment in own_starts],
                "calibration": calibration_text,
                "replay_unavailable": (
                    "the PUB's shots span several execution chunks and carry no chunk tag" if spans_chunks else None
                ),
            }
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
                    width = int(bits["num_bits"])
                    hardware = bit_values(bits["bitstrings"])
                    qubits = list(group_replicas[r]["physical_qubits"])
                    if simulator is not None:
                        used_qubits[pub_start].update(qubits)
                    sub = carve_replica(circuit, qubits)
                    aware, mismatches = schedule_aware(sub, tables.get(name, {}))
                    # Every replay call takes the next seed of one advancing
                    # counter, so no two calls share a noise stream.
                    archived_replay = None
                    aware_replay = None
                    if simulator is not None:
                        replay_seed += 1
                        archived_replay = _simulate(simulator, sub, shots, replay_seed)
                        # A circuit the table does not fully match has no
                        # schedule-aware view: a partially delayed replay
                        # would read as an optimistic one.
                        if not mismatches:
                            replay_seed += 1
                            aware_replay = _simulate(simulator, aware, shots, replay_seed)
                    if member.startswith(QPE_PREFIX) and label is not None:
                        decode: Any = lambda v, s=label: qpe_statistics(v, s)  # noqa: E731
                        indicator = (hardware == label).astype(float)
                    elif member.startswith(SHOR_PREFIX):
                        decode = lambda v, w=width: shor_statistics(v, w)  # noqa: E731
                        indicator = ((hardware >> (width - 2)) % 2 == 1).astype(float)
                    else:
                        decode = lambda v, w=width: generic_statistics(v, w)  # noqa: E731
                        modal = Counter(int(v) for v in hardware).most_common(1)[0][0]
                        indicator = (hardware == modal).astype(float)
                    views = {
                        "hardware": decode(hardware),
                        "replay_archived": decode(archived_replay[register]) if archived_replay is not None else None,
                        "replay_schedule_aware": decode(aware_replay[register]) if aware_replay is not None else None,
                    }
                    pub_out["components"].append(
                        {
                            "member": member,
                            "replica": r,
                            "register": register,
                            "physical_qubits": qubits,
                            "schedule_mismatches": mismatches,
                            "schedule_aware_unavailable": bool(mismatches),
                            "inserted_delay_dt": inserted_delay_dt(aware) if not mismatches else None,
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
        # Packed-versus-reference schedules on the replica-0 qubits of the
        # groups the packed PUB carries: the first PUB with no reference
        # component against the first PUB of only reference components.
        packed_manifest = next((m for m in job_entry["pubs"] if not any(c["reference"] for c in m["components"])), None)
        reference = next((m["name"] for m in job_entry["pubs"] if all(c["reference"] for c in m["components"])), None)
        if packed_manifest and reference and packed_manifest["name"] in tables and reference in tables:
            packed = packed_manifest["name"]
            qubits = sorted(
                {q for c in packed_manifest["components"] for q in replicas_by_group[c["group"]][0]["physical_qubits"]}
            )
            job_out["packed_minus_reference_schedule"] = {
                "packed_pub": packed,
                "reference_pub": reference,
                "per_qubit": schedule_offsets(tables[packed], tables[reference], qubits),
            }
        job_out["coherence_us"] = {
            start.isoformat(): {
                str(q): {"t1": calibrations[start][0].t1(q) * 1e6, "t2": calibrations[start][0].t2(q) * 1e6}
                for q in sorted(qubits_used)
            }
            for start, qubits_used in sorted(used_qubits.items())
        }
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
    # One file per analysis digest: a later revision writes beside, never
    # over, an earlier adjudication of the same raw shots.
    target_path = run_dir / f"adjudication-{out['analysis_digest'][:12]}-seed{seed}.json"
    text = json.dumps(out, indent=1, sort_keys=True) + "\n"
    if target_path.exists() and target_path.read_text() != text:
        raise AdjudicationError(f"{target_path} exists with different content under the same analysis digest")
    live_run._write_text_atomically(target_path, text)
    out["path"] = target_path.name
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
    elided = circuit.copy_empty_like()
    for instruction in circuit.data:
        elided.append(instruction)
        if instruction.operation.name == "measure":
            elided.rz(0.25, 1)  # a virtual rotation the scheduler table does not carry
    elided_aware, elided_mismatches = schedule_aware(elided, table)
    if elided_mismatches or inserted_delay_dt(elided_aware) != inserted_delay_dt(aware):
        raise AdjudicationError(f"an elided rz blocks matching: {elided_mismatches}")
    broken = QuantumCircuit(3, 1)
    broken.sx(1)
    broken.x(1)
    if not schedule_aware(broken, table)[1]:
        raise AdjudicationError("an instruction the table lacks passes as matched")
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
    metadata = {
        "executor": {
            "chunk_timing": [
                {
                    "start": "2026-10-11T15:31:50+00:00",
                    "parts": [{"idx_item": 0, "size": 1}, {"idx_item": 1, "size": 1}],
                },
                {"start": "2026-10-11T15:40:00+00:00", "parts": [{"idx_item": 1, "size": 1}]},
            ]
        }
    }
    starts = pub_starts(metadata, 3)
    if len(starts[0]) != 1 or len(starts[1]) != 2 or starts[2] != []:
        raise AdjudicationError(f"PUB chunk starts read {starts}")
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
        print(f"job {job_id}: {len(job['pubs'])} PUBs adjudicated; wrote {out['path']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
