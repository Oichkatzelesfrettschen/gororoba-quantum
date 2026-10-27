"""Exact laws of a retained dynamic run with its idle relaxation charged k times over, the family a rate fit reads.

scripts/scheduled_idle_replay.py rebuilds each replica of each fused PUB with the service-scheduled idle inserted
as delays and computes its exact branch-resolved law under the Target and properties in force at the PUB's
execution start. This script reuses that reconstruction unchanged and scales its delays afterwards. It first tags
every delay the ISA states (in a window-dose member these are exactly the dose delays) with the label `isa`, which
`padded_replica` carries through, so each delay of the padded circuit is either stated or inserted scheduler idle.

- `--dose-scales K1,...`: for every member whose ISA states a delay, the stated delays are multiplied by each factor
  and the inserted idle stays as scheduled (`dose_scaled_exact_laws`).
- `--idle-scales K1,...`: for every member, the stated delays and the inserted idle alike are multiplied by each
  factor (`idle_scaled_exact_laws`).

A law the branch-resolved model refuses (its trace check, which a very long relaxation at a large factor can
exceed) is listed under `refused`, and its family is withheld whole. Each qubit's scaled delays of one kind sum to
round(k * their total), the rounding carried from one delay to the next, so a dose split around echo pulses is
charged exactly k times over to the dt. The schedule itself, and so the order of every gate, measurement and branch,
is unchanged.

Usage:
    "$PYTHON" scripts/scheduled_idle_scaling.py RUN_DIR --out RUN_DIR/idle-scaling.json \\
        [--dose-scales K1,K2,...] [--idle-scales K1,K2,...]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import scheduled_idle_replay as replay  # noqa: E402
from qiskit import QuantumCircuit, qpy  # noqa: E402
from qiskit.circuit import Delay  # noqa: E402

STATED = "isa"
Item = tuple[replay.ReplicaItem, float, float]


def tagged(fused: QuantumCircuit) -> QuantumCircuit:
    """fused with every stated delay carrying the label STATED."""
    out = fused.copy_empty_like()
    for instruction in fused.data:
        if instruction.operation.name == "delay":
            delay = Delay(int(instruction.operation.duration), unit="dt")
            delay.label = STATED
            out.append(delay, instruction.qubits)
        else:
            out.append(instruction)
    return out


def scaled(padded: QuantumCircuit, dose_scale: float, idle_scale: float) -> QuantumCircuit:
    """padded with its stated delays scaled by dose_scale and its inserted idle by idle_scale, per qubit and kind."""
    out = padded.copy_empty_like()
    totals: dict[tuple[int, bool], int] = {}
    emitted: dict[tuple[int, bool], int] = {}
    for instruction in padded.data:
        operation = instruction.operation
        if operation.name != "delay":
            out.append(instruction)
            continue
        stated = operation.label == STATED
        (qubit,) = (padded.find_bit(bit).index for bit in instruction.qubits)
        key = (qubit, stated)
        totals[key] = totals.get(key, 0) + int(operation.duration)
        target = round((dose_scale if stated else idle_scale) * totals[key])
        charged = target - emitted.get(key, 0)
        emitted[key] = target
        if charged > 0:
            out.append(Delay(charged, unit="dt"), instruction.qubits)
    return out


def scaled_replica(item: Item) -> bytes:
    """The qpy bytes of one replica's idle-padded circuit at (dose_scale, idle_scale)."""
    (fused, rows, qubits, registers), dose_scale, idle_scale = item
    padded, _ = replay.padded_replica(tagged(fused), rows, qubits, registers)
    return replay._serialized(scaled(padded, dose_scale, idle_scale))


def law_or_refusal(item: tuple[bytes, Any, float]) -> list[float] | str:
    """The exact law, or the reason the branch-resolved model refuses it (a trace beyond its bound)."""
    try:
        return replay._exact_law(item)
    except ValueError as error:
        return str(error)


def has_stated_delay(fused: QuantumCircuit, qubits: list[int]) -> bool:
    keep = set(qubits)
    return any(
        instruction.operation.name == "delay" and {fused.find_bit(bit).index for bit in instruction.qubits} <= keep
        for instruction in fused.data
    )


def scaling(run_dir: Path, out: Path, dose_scales: tuple[float, ...], idle_scales: tuple[float, ...]) -> dict[str, Any]:
    from qiskit_ibm_runtime import QiskitRuntimeService

    import ibm_account
    import live_run
    import local_compute
    import parallel

    record = json.loads((run_dir / "record.json").read_text(encoding="utf-8"))
    collected = json.loads((run_dir / "collect.json").read_text(encoding="utf-8"))
    jobs = collected[0]["jobs"]
    replay.require(len(jobs) == 1, "one job per run")
    job_id, job = next(iter(jobs.items()))
    with (run_dir / "isa.qpy").open("rb") as stream:
        fused_by_name = {circuit.name: circuit for circuit in qpy.load(stream)}
    service = ibm_account.open_service(QiskitRuntimeService)
    ibm_account.require_instance(ibm_account.recorded_instance(run_dir), live_run._instance_hash(service), job_id)
    backend = service.backend(job["backend"])
    prep_excitation = float(record.get("policy", {}).get("design", {}).get("prep_excitation") or 0.0)
    simulators: dict[str, Any] = {}
    keys: list[tuple[str, str, float]] = []
    items: list[Item] = []
    noises: list[Any] = []
    for index, pub in enumerate(record["execution_pubs"]):
        rows = replay.schedule_rows(run_dir / "raw" / job_id / f"pub_{index:02d}.json")
        start = job["pub_timing"][pub["name"]]["execution_window_start"]
        if start not in simulators:
            moment = datetime.fromisoformat(start)
            simulators[start] = live_run.noise_simulator(
                f"{backend.name}@{start}",
                backend.target_history(datetime=moment),
                backend.properties(datetime=moment),
                local_compute.settings(),
            )
        noise = simulators[start].options.noise_model
        fused = fused_by_name[pub["name"]]
        for component in pub["components"]:
            replicas = replay.component_replicas(record, component)
            for qubits, registers in zip(replicas, component["registers_by_replica"], strict=True):
                item = (fused, rows, qubits, registers)
                families = [("idle_scaled_exact_laws", k, k, k) for k in idle_scales]
                if has_stated_delay(fused, qubits):
                    families = [("dose_scaled_exact_laws", k, k, 1.0) for k in dose_scales] + families
                for family, k, dose_scale, idle_scale in families:
                    keys.append((family, component["member"], k))
                    items.append((item, dose_scale, idle_scale))
                    noises.append(noise)
    payloads = parallel.ordered_map(scaled_replica, items, min_items=2)
    laws = parallel.ordered_map(
        law_or_refusal, [(b, n, prep_excitation) for b, n in zip(payloads, noises, strict=True)], min_items=2
    )
    report: dict[str, Any] = {
        "schema": "scheduled-idle-scaling-v1",
        "run": run_dir.relative_to(ROOT).as_posix(),
        "job_id": job_id,
        "prep_excitation": prep_excitation,
        "dose_scaled_exact_laws": {},
        "idle_scaled_exact_laws": {},
        "refused": [],
    }
    for (family, member, k), law in zip(keys, laws, strict=True):
        if isinstance(law, str):
            report["refused"].append({"family": family, "member": member, "scale": k, "reason": law})
            continue
        report[family].setdefault(repr(k), {}).setdefault(member, []).append(law)
    # A family with any refused law is withheld whole: a fit over a partial family would read a different model.
    for family in {row["family"] for row in report["refused"]}:
        report[family] = {}
    out.write_text(json.dumps(report, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return report


def factors(text: str) -> tuple[float, ...]:
    return tuple(float(value) for value in text.split(","))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--dose-scales", type=factors, default=())
    parser.add_argument("--idle-scales", type=factors, default=())
    args = parser.parse_args()
    report = scaling(args.run_dir.resolve(), args.out, args.dose_scales, args.idle_scales)
    print(
        "idle scaling:",
        {family: sorted(report[family]) for family in ("dose_scaled_exact_laws", "idle_scaled_exact_laws")},
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
