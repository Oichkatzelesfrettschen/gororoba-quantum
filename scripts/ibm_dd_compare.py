"""Compile a static group with and without dynamical decoupling and simulate both under the Target's noise.

The tool answers one question offline: on the idle windows of a compiled group, what do the native
PadDynamicalDecoupling sequences (XX, XpXm, XY4 of qiskit_ibm_runtime.executor.dynamical_decoupling) change in
the simulated outcome law? live_run.py keeps its defaults and never inserts DD; this tool changes no submission path.

Each member compiles once to an ISA circuit on the Target. The baseline schedules it as late as possible and pads
the idle with delays, which is what the service plays; each DD arm runs the same scheduling pass and the runtime's
own DD pass manager, so the idle windows are identical and only the pulses differ. Both arms simulate on the
density-matrix noise model that live_run.noise_simulator builds from the Target and properties.

That noise model relaxes a qubit by T1 and T2 channels that act at random and carry no memory. A refocusing pulse
cannot undo the dephasing part of such a channel, and on the tested circuit and placement (the idle_ramsey fixture and
the experiment groups on the layouts the compile chose) DD gains no credit. The result does not extend to every
circuit: an XX pair changes how long a qubit occupies the excited state under amplitude damping, and an Aer
thermal-relaxation control at 80 us idle and 100 us T1 raised the excited-state survival from 0.4493 to 0.7192. The
optional --detuning-hz arm adds the mechanism DD exists for: a quasi-static detuning that rotates each idle qubit
about Z by 2 pi f t. The circuit's own X pulses conjugate those rotations, so a pulse sequence refocuses them
without a sign bookkeeping in the tool. The arm is a model input, never a measurement, and the report names it.

Usage:
    "$PYTHON" scripts/ibm_dd_compare.py --group NAME --backend fake:fez \\
        --seed-transpiler qrng:REF --seed-simulator qrng:REF
    "$PYTHON" scripts/ibm_dd_compare.py --self-test
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import RZGate
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import ALAPScheduleAnalysis, PadDelay, TimeUnitConversion
from qiskit_ibm_runtime.executor.dynamical_decoupling import generate_dd_pass_manager
from qiskit_ibm_runtime.options_models.dynamical_decoupling import DynamicalDecouplingOptions

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

SEQUENCES = ("XX", "XpXm", "XY4")
CONTROL_FLOW = frozenset({"if_else", "while_loop", "for_loop", "switch_case"})
DEFAULT_SHOTS = 4000
MAX_ACTIVE_QUBITS = 12
MAX_CLBITS = 12
# 6.25 turns over the fixture's 80 us idle: a quarter-turn residue, so the baseline outcome sits at one half.
QUARTER_TURN_HZ = 78125.0


@dataclass(frozen=True)
class Case:
    """One circuit with the outcome law it ideally produces, indexed by the integer of its classical bits."""

    name: str
    circuit: QuantumCircuit
    ideal: np.ndarray


def cases_from_group(group_name: str) -> list[Case]:
    """The bound circuits of an experiment group with their ideal laws."""
    import experiments

    groups = {g.name: g for g in experiments.all_experiment_groups()}
    if group_name not in groups:
        raise SystemExit(f"unknown group {group_name!r}; known: {', '.join(sorted(groups))}")
    cases = []
    for member in groups[group_name].members:
        circuit = member.circuit
        if member.binding:
            circuit = circuit.assign_parameters(member.binding)
        cases.append(Case(member.name, circuit, np.asarray(member.ideal, dtype=float)))
    return cases


def active_qubits(circuit: QuantumCircuit) -> set[int]:
    return {circuit.find_bit(q).index for inst in circuit.data for q in inst.qubits if inst.operation.name != "barrier"}


def refusal(circuit: QuantumCircuit) -> str | None:
    """Why a circuit stays out of the comparison, or None."""
    ops = set(circuit.count_ops())
    if ops & CONTROL_FLOW:
        return "control flow: the runtime refuses DD on dynamic circuits"
    if circuit.num_clbits > MAX_CLBITS:
        return f"{circuit.num_clbits} classical bits exceed {MAX_CLBITS}"
    if len(active_qubits(circuit)) > MAX_ACTIVE_QUBITS:
        return f"{len(active_qubits(circuit))} active qubits exceed {MAX_ACTIVE_QUBITS}"
    return None


def baseline_manager(view: Any) -> PassManager:
    """ALAP scheduling with delay padding: the idle the service plays, no pulses."""
    target = view.target
    return PassManager(
        [TimeUnitConversion(target=target), ALAPScheduleAnalysis(target=target), PadDelay(target=target)]
    )


def dd_manager(view: Any, sequence: str) -> PassManager:
    options = DynamicalDecouplingOptions(enable=True, sequence_type=sequence, skip_reset_qubits=False)
    return generate_dd_pass_manager(view, options)


def add_quasi_static_detuning(circuit: QuantumCircuit, dt: float, detuning_hz: float) -> QuantumCircuit:
    """circuit with an rz of 2 pi f t after every delay; later X pulses conjugate it as they conjugate a detuning."""
    out = circuit.copy_empty_like()
    for inst in circuit.data:
        out.append(inst.operation, inst.qubits, inst.clbits)
        if inst.operation.name == "delay":
            seconds = float(inst.operation.duration) * dt
            out.append(RZGate(2.0 * math.pi * detuning_hz * seconds), inst.qubits)
    return out


def pulse_and_delay_counts(circuit: QuantumCircuit, qubits: set[int]) -> dict[str, int]:
    """X pulses and idle delay (dt) on the given physical qubits; the scheduler pads every other qubit too."""
    rows = [(i.operation.name, circuit.find_bit(i.qubits[0]).index, i.operation) for i in circuit.data if i.qubits]
    return {
        "x": sum(1 for name, q, _ in rows if name == "x" and q in qubits),
        "delay_dt": sum(int(op.duration) for name, q, op in rows if name == "delay" and q in qubits),
    }


def distribution(counts: dict[str, int], bits: int) -> np.ndarray:
    law = np.zeros(2**bits)
    for key, value in counts.items():
        law[int(key.replace(" ", ""), 2)] += value
    return law / law.sum()


def tvd(p: np.ndarray, q: np.ndarray) -> float:
    return 0.5 * float(np.abs(p - q).sum())


def tvd_standard_error(law: np.ndarray, ideal: np.ndarray, shots: int) -> float:
    """Delta-method standard error of 0.5 sum |law - ideal| from one multinomial sample of shots outcomes.

    With s_i the sign of law_i - ideal_i, the distance is 0.5 sum s_i law_i locally, and the multinomial covariance
    gives Var = 0.25 (sum s_i^2 law_i - (sum s_i law_i)^2) / shots. A deterministic ideal outcome reduces this to the
    binomial error fraction f: 0.5 sqrt(f (1 - f) 4 / shots)."""
    sign = np.sign(law - ideal)
    variance = float((sign**2 * law).sum() - ((sign * law).sum()) ** 2)
    return 0.5 * math.sqrt(max(variance, 0.0) / shots)


def compile_cases(
    cases: list[Case], target: Any, seed_transpiler: int | None, layout: list[int] | None
) -> list[QuantumCircuit]:
    kwargs: dict[str, Any] = {"target": target, "optimization_level": 1}
    if seed_transpiler is not None:
        kwargs["seed_transpiler"] = seed_transpiler
    if layout is not None:
        kwargs["initial_layout"] = layout
    compiled = transpile([c.circuit for c in cases], **kwargs)
    return list(compiled) if isinstance(compiled, list) else [compiled]


def schedule_arms(
    isa: list[QuantumCircuit], name: str, target: Any, sequences: tuple[str, ...], detuning_hz: float
) -> dict[tuple[int, str], QuantumCircuit]:
    """Each ISA circuit scheduled under the baseline and every DD sequence, keyed by (circuit index, arm)."""
    import live_run

    view = live_run.TargetView(name, target)
    managers = {"baseline": baseline_manager(view), **{s: dd_manager(view, s) for s in sequences}}
    arms: dict[tuple[int, str], QuantumCircuit] = {}
    for arm, manager in managers.items():
        scheduled = manager.run(isa)
        scheduled = scheduled if isinstance(scheduled, list) else [scheduled]
        for index, circuit in enumerate(scheduled):
            arms[(index, arm)] = add_quasi_static_detuning(circuit, target.dt, detuning_hz) if detuning_hz else circuit
    return arms


def compare(
    cases: list[Case],
    name: str,
    target: Any,
    props: Any,
    *,
    sequences: tuple[str, ...] = SEQUENCES,
    shots: int = DEFAULT_SHOTS,
    detuning_hz: float = 0.0,
    seed_transpiler: int | None = None,
    seed_simulator: int | None = None,
    layout: list[int] | None = None,
) -> dict[str, Any]:
    """Per case and per arm: pulses, idle, and the simulated distance of the outcome law from the ideal."""
    import live_run

    for sequence in sequences:
        if sequence not in SEQUENCES:
            raise ValueError(f"unknown DD sequence {sequence!r}")
    skipped = {c.name: why for c in cases if (why := refusal(c.circuit)) is not None}
    kept = [c for c in cases if c.name not in skipped]
    report: dict[str, Any] = {
        "backend": name,
        "shots": shots,
        "sequences": list(sequences),
        "detuning_hz": detuning_hz,
        "seed_transpiler": seed_transpiler,
        "seed_simulator": seed_simulator,
        "skipped": skipped,
        "cases": {},
    }
    if not kept:
        return report
    isa = compile_cases(kept, target, seed_transpiler, layout)
    arms = schedule_arms(isa, name, target, sequences, detuning_hz)
    order = sorted(arms)
    simulator = live_run.noise_simulator(name, target, props)
    run_kwargs: dict[str, Any] = {"shots": shots}
    if seed_simulator is not None:
        run_kwargs["seed_simulator"] = seed_simulator
    result = simulator.run([arms[key] for key in order], **run_kwargs).result()
    for position, (index, arm) in enumerate(order):
        case = kept[index]
        law = distribution(result.get_counts(position), arms[(index, arm)].num_clbits)
        entry = report["cases"].setdefault(case.name, {"active_qubits": len(active_qubits(isa[index])), "arms": {}})
        entry["arms"][arm] = {
            "tvd_to_ideal": tvd(law, case.ideal),
            "tvd_standard_error": tvd_standard_error(law, case.ideal, shots),
            "duration_dt": arms[(index, arm)].estimate_duration(target, unit="dt"),
            **pulse_and_delay_counts(arms[(index, arm)], active_qubits(isa[index])),
        }
    for entry in report["cases"].values():
        base = entry["arms"]["baseline"]["tvd_to_ideal"]
        for row in entry["arms"].values():
            row["tvd_gain_over_baseline"] = base - row["tvd_to_ideal"]
    return report


def fake_backend(label: str) -> Any:
    from qiskit_ibm_runtime import fake_provider

    classes = {"fez": "FakeFez", "kingston": "FakeKingston", "marrakesh": "FakeMarrakesh"}
    if label not in classes:
        raise SystemExit(f"fake backend {label!r} is not one of {', '.join(classes)}")
    return getattr(fake_provider, classes[label])()


def load_target(spec: str) -> tuple[str, Any, Any]:
    """(name, Target, properties) of fake:NAME (offline) or live:NAME (a free calibration read of the saved account)."""
    kind, _, label = spec.partition(":")
    if kind == "fake":
        backend = fake_backend(label)
        return f"fake_{label}", backend.target, backend.properties()
    if kind == "live":
        import ibm_account
        import live_run

        snapshot = live_run.take_snapshot(ibm_account.open_service(), label)
        return label, snapshot.backend.target, snapshot.properties
    raise SystemExit("--backend is fake:NAME or live:NAME")


def format_report(report: dict[str, Any]) -> str:
    lines = [f"backend {report['backend']}  shots {report['shots']}  detuning {report['detuning_hz']} Hz"]
    for case, entry in report["cases"].items():
        lines.append(f"{case}  active qubits {entry['active_qubits']}")
        for arm, row in entry["arms"].items():
            lines.append(
                f"  {arm:9s} tvd {row['tvd_to_ideal']:.4f} +- {row['tvd_standard_error']:.4f}  "
                f"gain {row['tvd_gain_over_baseline']:+.4f}  x {row['x']:3d}  idle {row['delay_dt']} dt  "
                f"duration {row['duration_dt']} dt"
            )
    for case, why in report["skipped"].items():
        lines.append(f"{case}  skipped: {why}")
    return "\n".join(lines)


def idle_fixture() -> Case:
    """Qubit 0 holds a superposition while qubit 1 plays a long delay; the ideal outcome of qubit 0 is 1."""
    circuit = QuantumCircuit(2, 1)
    circuit.sx(0)
    circuit.barrier()
    circuit.delay(20000, 1, unit="dt")
    circuit.barrier()
    circuit.sx(0)
    circuit.measure(0, 0)
    return Case("idle_ramsey", circuit, np.array([0.0, 1.0]))


def main(argv: list[str] | None = None) -> int:
    import qrng_seeds

    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--group", help="experiment group name (experiments.all_experiment_groups)")
    parser.add_argument(
        "--backend", default="fake:fez", help="fake:fez|kingston|marrakesh, or live:ibm_fez for a free calibration read"
    )
    parser.add_argument("--sequences", nargs="+", default=list(SEQUENCES), choices=SEQUENCES)
    parser.add_argument("--shots", type=int, default=DEFAULT_SHOTS)
    parser.add_argument(
        "--detuning-hz", type=float, default=0.0, help="modeled quasi-static detuning, never a measurement"
    )
    parser.add_argument("--layout", type=int, nargs="+", help="initial layout, physical qubits in circuit order")
    qrng_seeds.add_seed_argument(parser, "--seed-transpiler", help="transpiler seed, qrng:<draw>#<index>")
    qrng_seeds.add_seed_argument(parser, "--seed-simulator", help="Aer seed, qrng:<draw>#<index>")
    parser.add_argument("--out", type=Path)
    parser.add_argument(
        "--self-test", action="store_true", help="run the fixture circuit offline and check the report shape"
    )
    args = parser.parse_args(argv)
    if args.self_test:
        name, target, props = load_target("fake:fez")
        report = compare([idle_fixture()], name, target, props, shots=200, detuning_hz=QUARTER_TURN_HZ, layout=[0, 1])
        arms = report["cases"]["idle_ramsey"]["arms"]
        if set(arms) != {"baseline", *SEQUENCES} or arms["baseline"]["x"] != 0:
            print("self-test failed: arms or baseline pulses differ from the contract")
            return 1
        print("self-test passed")
        return 0
    if args.group is None:
        parser.error("--group names the experiment group to compare")
    if args.seed_transpiler is None or args.seed_simulator is None:
        parser.error("--seed-transpiler and --seed-simulator take qrng:<draw>#<index> values")
    name, target, props = load_target(args.backend)
    report = compare(
        cases_from_group(args.group),
        name,
        target,
        props,
        sequences=tuple(args.sequences),
        shots=args.shots,
        detuning_hz=args.detuning_hz,
        seed_transpiler=args.seed_transpiler,
        seed_simulator=args.seed_simulator,
        layout=args.layout,
    )
    report["group"] = args.group
    print(format_report(report))
    if args.out:
        args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
