"""Compile the Heron multiprogramming circuits for the standard and the fractional-gate Target and compare them.

use_fractional_gates=True adds rx(theta) for any theta and rzz(theta) for 0 < theta <= pi/2 to the Target
(docs/notes/ibm_quantum/fractional-gates.md). The comparison builds both Targets from the retained snapshot
docs/evidence/heron_platform/targets.json, which holds the standard and the fractional instruction sets of every
Heron r2 backend with per-qubit and per-coupler durations and errors, so it needs no network and no account. For each
circuit it reports the gate counts, the critical-path duration, the summed gate-error budget -sum log(1 - e) over the
gates and every rzz outside (0, pi/2], which the service rejects.

The comparison is a compile measurement. It changes no live_run.py default: a fractional decomposition is an
intervention with its own controls, and the runtime refuses Pauli twirling, probabilistic error cancellation and
probabilistic error amplification on fractional circuits (TREX stays supported).

Usage:
    "$PYTHON" scripts/ibm_fractional_compare.py --backend ibm_fez [--out FILE]
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

from qiskit import QuantumCircuit
from qiskit.circuit import Delay, IfElseOp, Parameter, Reset
from qiskit.circuit.library import CZGate, IGate, Measure, RXGate, RZGate, RZZGate, SXGate, XGate
from qiskit.transpiler import InstructionProperties, Target
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

SNAPSHOT = ROOT / "docs/evidence/heron_platform/targets.json"
RZZ_MAX = math.pi / 2
CONTROL_FLOW = frozenset({"if_else", "while_loop", "for_loop", "switch_case"})
ANGLE_EPS = 1e-9
# Runtime functions that fail on fractional circuits (docs/notes/ibm_quantum/fractional-gates.md).
FRACTIONAL_INCOMPATIBLE = ("pauli_twirling", "probabilistic_error_cancellation", "probabilistic_error_amplification")


def target_from_snapshot(entry: dict[str, Any], fractional: bool) -> Target:
    """Target of one snapshot backend.

    The snapshot's fractional block lists only the instructions that differ from the standard set (cz, sx, rx and
    rzz), so the fractional Target takes every other instruction (x, measure) from the standard block.
    """
    instructions = dict(entry["instructions"])
    if fractional:
        instructions.update(entry["fractional_instructions"])
    qubits = range(entry["num_qubits"])
    target = Target(num_qubits=entry["num_qubits"], dt=entry["dt"])
    gates: dict[str, Any] = {
        "cz": CZGate(),
        "sx": SXGate(),
        "x": XGate(),
        "rx": RXGate(Parameter("theta")),
        "rzz": RZZGate(Parameter("theta")),
        "measure": Measure(),
    }
    for name, gate in gates.items():
        if name not in instructions:
            continue
        rows = instructions[name]
        target.add_instruction(
            gate,
            {
                tuple(q): InstructionProperties(duration=d, error=e)
                for q, d, e in zip(rows["qargs"], rows["duration"], rows["error"], strict=True)
            },
        )
    target.add_instruction(
        RZGate(Parameter("phi")), {(q,): InstructionProperties(duration=0.0, error=0.0) for q in qubits}
    )
    target.add_instruction(IGate(), {(q,): None for q in qubits})
    target.add_instruction(Delay(Parameter("t")), {(q,): None for q in qubits})
    target.add_instruction(Reset(), {(q,): None for q in qubits})
    target.add_instruction(IfElseOp, name="if_else")
    return target


def ising_chain(width: int = 6, steps: int = 3) -> QuantumCircuit:
    """Trotterized transverse-field Ising chain, the rzz and rx workload of IBM's fractional-gates guide."""
    qc = QuantumCircuit(width, width)
    for step in range(steps):
        theta = 0.3 + 0.1 * step
        for q in range(0, width - 1, 2):
            qc.rzz(theta, q, q + 1)
        for q in range(1, width - 1, 2):
            qc.rzz(theta, q, q + 1)
        for q in range(width):
            qc.rx(0.7 + 0.05 * step, q)
    qc.measure(range(width), range(width))
    return qc


def named_circuits() -> dict[str, QuantumCircuit]:
    import heron_multiprogramming as hm

    def measured(qc: QuantumCircuit) -> QuantumCircuit:
        out = qc.copy()
        if out.num_clbits == 0:
            out.measure_all()
        return out

    return {
        "k5_lcu_zero_product_witness": measured(hm.lcu_zero_product_witness()),
        "k10_steane_z_syndrome_patch": measured(hm.steane_z_syndrome_patch()),
        "k2_bell_delay_probe": measured(hm.bell_delay_probe()),
        "k7_sedenion_associator_witness": measured(hm.sedenion_associator_witness()),
        "ising_rzz_rx_chain": ising_chain(),
    }


def error_budget(circuit: QuantumCircuit, target: Target) -> float:
    """-sum log(1 - e) over the gates the Target gives an error."""
    total = 0.0
    for inst in circuit.data:
        name = inst.operation.name
        qargs = tuple(circuit.find_bit(q).index for q in inst.qubits)
        if name in {"measure", "barrier", "delay", "rz"} or name not in target:
            continue
        props = target[name].get(qargs)
        if props is not None and props.error:
            total += -math.log1p(-props.error)
    return total


def rzz_outside_range(circuit: QuantumCircuit) -> int:
    """Count of rzz gates with a bound angle outside (0, pi/2]."""
    count = 0
    for inst in circuit.data:
        if inst.operation.name != "rzz":
            continue
        angle = float(inst.operation.params[0])
        if not (ANGLE_EPS < angle <= RZZ_MAX + ANGLE_EPS):
            count += 1
    return count


def compile_arm(circuit: QuantumCircuit, target: Target, fractional: bool, seed: int | None) -> QuantumCircuit:
    manager = generate_preset_pass_manager(
        optimization_level=1,
        target=target,
        translation_method="ibm_dynamic_and_fractional" if fractional else None,
        seed_transpiler=seed,
    )
    out = manager.run(circuit)
    return out if isinstance(out, QuantumCircuit) else out[0]


def summarize(circuit: QuantumCircuit, target: Target) -> dict[str, Any]:
    ops = {k: int(v) for k, v in sorted(circuit.count_ops().items())}
    return {
        "ops": ops,
        "two_qubit_gates": int(sum(v for k, v in ops.items() if k in {"cz", "rzz"})),
        "depth": circuit.depth(),
        "duration_dt": None if CONTROL_FLOW & set(ops) else int(circuit.estimate_duration(target, unit="dt")),
        "error_budget": round(error_budget(circuit, target), 6),
        "rzz_outside_range": rzz_outside_range(circuit),
    }


def compare(entry: dict[str, Any], seed_transpiler: int | None = None) -> dict[str, Any]:
    standard = target_from_snapshot(entry, fractional=False)
    fractional = target_from_snapshot(entry, fractional=True)
    out: dict[str, Any] = {}
    for name, circuit in named_circuits().items():
        row: dict[str, Any] = {"input_ops": {k: int(v) for k, v in sorted(circuit.count_ops().items())}}
        for label, target, flag in (("standard", standard, False), ("fractional", fractional, True)):
            row[label] = summarize(compile_arm(circuit, target, flag, seed_transpiler), target)
        base, frac = row["standard"]["duration_dt"], row["fractional"]["duration_dt"]
        row["duration_ratio"] = None if base is None or frac is None else frac / base
        row["error_budget_ratio"] = row["fractional"]["error_budget"] / row["standard"]["error_budget"]
        out[name] = row
    return out


def format_report(backend: str, calibration: str, rows: dict[str, Any]) -> str:
    lines = [f"{backend}  snapshot calibration {calibration}"]
    for name, row in rows.items():
        lines.append(name)
        for label in ("standard", "fractional"):
            s = row[label]
            lines.append(
                f"  {label:10s} 2q {s['two_qubit_gates']:3d}  depth {s['depth']:3d}  duration {s['duration_dt']} dt  "
                f"budget {s['error_budget']:.4f}  rzz out of range {s['rzz_outside_range']}  {s['ops']}"
            )
        ratio = row["duration_ratio"]
        shown = "n/a (control flow)" if ratio is None else f"{ratio:.3f}"
        lines.append(f"  ratios fractional/standard: duration {shown}  budget {row['error_budget_ratio']:.3f}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    import qrng_seeds

    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--backend", default="ibm_fez", choices=("ibm_fez", "ibm_kingston", "ibm_marrakesh"))
    parser.add_argument("--snapshot", type=Path, default=SNAPSHOT)
    qrng_seeds.add_seed_argument(parser, "--seed-transpiler", help="transpiler seed, qrng:<draw>#<index>")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    if args.seed_transpiler is None:
        parser.error("--seed-transpiler takes a qrng:<draw>#<index> value")
    snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
    entry = snapshot["backends"][args.backend]
    rows = compare(entry, args.seed_transpiler)
    print(format_report(args.backend, entry["calibration"], rows))
    if args.out:
        record = {
            "backend": args.backend,
            "calibration": entry["calibration"],
            "incompatible_with_fractional": list(FRACTIONAL_INCOMPATIBLE),
            "circuits": rows,
        }
        args.out.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
