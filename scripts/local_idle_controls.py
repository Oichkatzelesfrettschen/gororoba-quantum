"""Matched-noise controls for local idle padding: idle scale, CZ factor, mid-circuit flips and a placement placebo.

local_idle_falsifier.py shows that padding a replica with its as-soon-as-possible idle moves the exact law toward
hardware. Any added decoherence moves an optimistic model toward hardware, so that pass fixes the direction and leaves
the mechanism open. This script places, on the same restricted replicas, execution snapshots and exact laws
(dynamic_density.probabilities after scheduled_idle_replay.relaxed), competing ways of spending added error:

- ``kappa``: every inserted delay of idle_padding.pad scaled by kappa (0 is the unpadded law, 1 the falsifier's
  padded law); the circuit's own delays stay as they are;
- ``alap``: every inserted delay of the ALAP placement (idle_padding.alap, the order IBM's scheduler plays) scaled
  by kappa;
- ``cz``: every reported CZ error times c (ghost_error_scale.scaled, readout factor 1), unpadded;
- ``cz_pad``: the CZ factor c on the padded replica (kappa 1);
- ``front`` and ``permuted``: placement placebos at kappa 1 and 3. ``front`` puts each qubit's own inserted total in
  one delay right after its first played instruction; ``permuted`` does the same with the totals cyclically shifted
  one place along the replica's played qubits in ascending order. Padding that beats ``front`` carries information in
  where the idle falls; ``front`` beating ``permuted`` carries information in which qubit waits;
- ``event``: the padded replica (kappa 1) with ghost_event_scale.with_events, an X flip of probability m before
  every mid-circuit measurement and after every reset, on replicas that hold such an event.

Each point reports the mean TV distance to the measured law over the run's replicas. Exact laws carry no shot noise
and the placebos are deterministic, so the script draws no seed.

``--service-replay RUN`` compares local padding with the service schedule on a run that retains
scheduled_idle_replay.py's ``idle-replay.json``. Both arms carry the record's declared prep excitation
(dynamic_density.with_prep_excitation), as that replay does, so the unpadded laws of the two sources coincide; the
report gives each replica's unpadded, locally padded (ASAP and ALAP) and service-padded TV distance to hardware,
and requires pad()'s inserted idle plus the circuit's own delays to equal scheduled_idle_replay.list_schedule_idle
on every qubit.

Usage:
    "$PYTHON" scripts/local_idle_controls.py --runs RUN[,RUN] --out docs/evidence/local_idle_padding/controls.json
    "$PYTHON" scripts/local_idle_controls.py --service-replay results/live/2026-10-18T090603.530638Z --out OUT
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ghost_error_scale  # noqa: E402
import ghost_event_scale  # noqa: E402
import ghost_run  # noqa: E402
import local_idle_falsifier  # noqa: E402
import numpy as np  # noqa: E402
from qiskit import QuantumCircuit, qpy  # noqa: E402
from qiskit.circuit import Delay  # noqa: E402
from scheduled_idle_replay import list_schedule_idle, relaxed  # noqa: E402

import calibration_snapshot  # noqa: E402
import idle_padding  # noqa: E402
import parallel  # noqa: E402

SCHEMA = "local-idle-padding-controls-v1"
KAPPAS = (0.0, 1.0, 2.0, 3.0, 5.0)
ALAP_KAPPAS = (1.0, 2.0, 3.0, 5.0)
CZ_FACTORS = (1.5, 2.0, 3.0, 5.0, 8.0)
CZ_PAD_FACTORS = (1.5, 2.0, 3.0)
PLACEBO_KAPPAS = (1.0, 3.0)
EVENT_ERRORS = (0.01, 0.02, 0.05, 0.1)

Point = tuple[str, float]


def grid(has_event: bool) -> list[Point]:
    points: list[Point] = [("kappa", k) for k in KAPPAS] + [("alap", k) for k in ALAP_KAPPAS]
    points += [("cz", c) for c in CZ_FACTORS] + [("cz_pad", c) for c in CZ_PAD_FACTORS]
    points += [(mode, k) for mode in ("front", "permuted") for k in PLACEBO_KAPPAS]
    if has_event:
        points += [("event", m) for m in EVENT_ERRORS]
    return points


def scaled_pad(circuit: QuantumCircuit, duration: idle_padding.Duration, kappa: float) -> QuantumCircuit:
    return idle_padding.pad(circuit, duration, kappa)[0]


def placebo(circuit: QuantumCircuit, duration: idle_padding.Duration, kappa: float, permute: bool) -> QuantumCircuit:
    """Each played qubit's inserted total (times kappa) as one delay after its first played instruction."""
    _, inserted = idle_padding.pad(circuit, duration)
    played: list[int] = []
    for instruction in circuit.data:
        if instruction.operation.name in idle_padding.VIRTUAL:
            continue
        for bit in instruction.qubits:
            q = circuit.find_bit(bit).index
            if q not in played:
                played.append(q)
    order = sorted(played)
    totals = {q: inserted.get(q, 0) for q in order}
    if permute:
        totals = {q: totals[order[(k + 1) % len(order)]] for k, q in enumerate(order)}
    out = circuit.copy_empty_like()
    started: set[int] = set()
    for instruction in circuit.data:
        out.append(instruction)
        if instruction.operation.name in idle_padding.VIRTUAL:
            continue
        for bit in instruction.qubits:
            q = circuit.find_bit(bit).index
            if q in started:
                continue
            started.add(q)
            length = round(totals[q] * kappa)
            if length > 0:
                out.append(Delay(length, unit="dt"), [bit])
    return out


def with_events(circuit: QuantumCircuit, probability: float) -> QuantumCircuit:
    """ghost_event_scale.with_events on a circuit whose qubits may sit outside its registers.

    restrict_circuit keeps the original physical Qubit objects as loose bits, which a circuit rebuilt from the
    registers alone does not hold; copy_empty_like keeps every bit.
    """
    from qiskit_aer.noise import pauli_error

    positions = dict(ghost_event_scale.event_positions(circuit))
    error = pauli_error([("X", probability), ("I", 1.0 - probability)])
    out = circuit.copy_empty_like()
    for position, inst in enumerate(circuit.data):
        event = positions.get(position)
        if event is not None and inst.operation.name == "measure":
            out.append(error, [circuit.qubits[event]])
        out.append(inst)
        if event is not None and inst.operation.name == "reset":
            out.append(error, [circuit.qubits[event]])
    return out


def point_tvd(item: tuple[local_idle_falsifier.Item, Point]) -> float:
    import dynamic_density

    (payload, snapshot, measured), (mode, value) = item
    circuit = qpy.load(io.BytesIO(payload))[0]
    if mode in ("cz", "cz_pad"):
        snapshot = ghost_error_scale.scaled(snapshot, value, 1.0)
    view, noise = calibration_snapshot.noise_model(snapshot)
    duration = idle_padding.target_duration(view.target)
    if mode == "kappa":
        built = scaled_pad(circuit, duration, value)
    elif mode == "alap":
        built = idle_padding.pad(circuit, duration, value, "alap")[0]
    elif mode == "cz":
        built = circuit
    elif mode in ("cz_pad", "event"):
        built = scaled_pad(circuit, duration, 1.0)
    else:
        built = placebo(circuit, duration, value, mode == "permuted")
    law_circuit = relaxed(built, noise)
    if mode == "event":
        law_circuit = with_events(law_circuit, value)
    law = dynamic_density.probabilities(law_circuit, noise)
    return round(ghost_run.tv(np.asarray(measured), law), 9)


def run_controls(name: str, index: dict[str, Any]) -> dict[str, Any]:
    header, keys, items = local_idle_falsifier.eligible_items(name, index)
    if not items:
        return {**header, "out": header.get("out", "no member with an exact law")}
    events = [ghost_event_scale.event_count(qpy.load(io.BytesIO(item[0]))[0]) > 0 for item in items]
    plans = [grid(has_event) for has_event in events]
    jobs = [(item, point) for item, points in zip(items, plans, strict=True) for point in points]
    flat = iter(parallel.ordered_map(point_tvd, jobs, min_items=2))
    per_replica = [{f"{mode}:{value:g}": next(flat) for mode, value in points} for points in plans]
    labels = list(dict.fromkeys(label for row in per_replica for label in row))
    means = {label: round(float(np.mean([row[label] for row in per_replica if label in row])), 9) for label in labels}
    return {
        **header,
        "replicas": len(items),
        "event_replicas": int(sum(events)),
        "mean_tvd": means,
        "per_replica": [{"member": m, "replica": k, "tvd": row} for (m, k), row in zip(keys, per_replica, strict=True)],
    }


def _service_item(item: tuple[local_idle_falsifier.Item, float]) -> dict[str, Any]:
    import dynamic_density

    (payload, snapshot, measured), excitation = item
    circuit = qpy.load(io.BytesIO(payload))[0]
    view, noise = calibration_snapshot.noise_model(snapshot)
    duration = idle_padding.target_duration(view.target)
    padded, inserted = idle_padding.pad(circuit, duration)
    late, late_inserted = idle_padding.pad(circuit, duration, placement="alap")
    own: dict[int, int] = {}
    for instruction in circuit.data:
        if instruction.operation.name == "delay":
            q = circuit.find_bit(instruction.qubits[0]).index
            own[q] = own.get(q, 0) + int(instruction.operation.duration)
    scheduled = list_schedule_idle(circuit, duration, list(range(circuit.num_qubits)))
    total = {q: inserted.get(q, 0) + own.get(q, 0) for q in sorted(set(inserted) | set(own) | set(scheduled))}
    if any(total[q] != scheduled.get(q, 0) for q in total):
        raise RuntimeError(f"pad idle {total} differs from list_schedule_idle {scheduled}")
    laws = [
        dynamic_density.probabilities(dynamic_density.with_prep_excitation(relaxed(c, noise), excitation), noise)
        for c in (circuit, padded, late)
    ]
    return {
        "inserted_dt": {str(q): v for q, v in sorted(inserted.items())},
        "unpadded_law": [round(float(v), 12) for v in laws[0]],
        "local_padded_law": [round(float(v), 12) for v in laws[1]],
        "alap_inserted_dt": {str(q): v for q, v in sorted(late_inserted.items())},
        "alap_padded_law": [round(float(v), 12) for v in laws[2]],
        "measured": list(measured),
    }


def service_replay(name: str, index: dict[str, Any]) -> dict[str, Any]:
    """Local and service padding of one run on matched baselines (the record's prep excitation in both)."""
    retained_path = ROOT / name / "idle-replay.json"
    retained = json.loads(retained_path.read_text(encoding="utf-8"))
    excitation = float(retained["prep_excitation"])
    header, keys, items = local_idle_falsifier.eligible_items(name, index)
    rows = parallel.ordered_map(_service_item, [(item, excitation) for item in items], min_items=2)
    replicas = []
    for (member, k), row in zip(keys, rows, strict=True):
        hardware = np.asarray(row.pop("measured"))
        unpadded = np.asarray(row["unpadded_law"])
        service_unpadded = np.asarray(retained["exact_laws"]["unpadded"][member][k])
        service = np.asarray(retained["exact_laws"]["idle_padded"][member][k])
        local = np.asarray(row["local_padded_law"])
        replicas.append(
            {
                "member": member,
                "replica": k,
                **row,
                "unpadded_to_service_unpadded_tvd": round(ghost_run.tv(unpadded, service_unpadded), 9),
                "unpadded_tvd": round(ghost_run.tv(hardware, unpadded), 9),
                "local_padded_tvd": round(ghost_run.tv(hardware, local), 9),
                "service_padded_tvd": round(ghost_run.tv(hardware, service), 9),
                "local_to_service_tvd": round(ghost_run.tv(local, service), 9),
                "alap_padded_tvd": round(ghost_run.tv(hardware, np.asarray(row["alap_padded_law"])), 9),
                "alap_to_service_tvd": round(ghost_run.tv(np.asarray(row["alap_padded_law"]), service), 9),
                "service_inserted_dt": retained["inserted_idle_dt"][member][k],
            }
        )
    digest = hashlib.sha256(retained_path.read_bytes()).hexdigest()
    return {
        **header,
        "idle_replay": {"path": retained_path.relative_to(ROOT).as_posix(), "sha256": digest},
        "prep_excitation": excitation,
        "replicas": replicas,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs", help="comma-separated run directories")
    parser.add_argument("--service-replay", help="a run directory that retains idle-replay.json")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    index = json.loads(ghost_run.INDEX.read_text(encoding="utf-8"))
    if args.service_replay:
        report = {
            "schema": "local-idle-padding-service-comparison-v1",
            "versions": local_idle_falsifier.versions(),
            **service_replay(args.service_replay, index),
        }
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        return 0
    if not args.runs:
        parser.error("--runs or --service-replay is required")
    runs = []
    for name in args.runs.split(","):
        summary = run_controls(name, index)
        runs.append(summary)
        print(json.dumps({k: v for k, v in summary.items() if k != "per_replica"}), flush=True)
    grids = {
        "kappa": list(KAPPAS),
        "alap": list(ALAP_KAPPAS),
        "cz": list(CZ_FACTORS),
        "cz_pad": list(CZ_PAD_FACTORS),
        "placebo_kappa": list(PLACEBO_KAPPAS),
        "event": list(EVENT_ERRORS),
    }
    result = {"schema": SCHEMA, "versions": local_idle_falsifier.versions(), "grid": grids, "runs": runs}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
