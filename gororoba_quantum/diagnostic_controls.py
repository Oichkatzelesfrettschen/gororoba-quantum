"""Two opt-in diagnostic campaigns: the walk scaffold A/B and a delayed single-qubit readout.

scaffold_ab runs the ripple walk template bound to its readout0 and readout1
values beside a measure-only circuit and an X-then-measure circuit on the
same four qubits. The bound template is logically the identity (readout0)
or X on every qubit (readout1), yet it executes the template's full CZ
scaffold, so P(0000) and P(1111) of the template members against the
scaffold-free members isolate the scaffold's loss on one tile under one
calibration.

readout_delay prepares one qubit in |0>, in |1> and in |1> followed by idles
of DELAYS_DT, then measures. A delay-independent loss of the excited state
points to preparation or assignment, and a loss that grows with the idle
points to relaxation. Placed on the correction circuit's first-bit writer, it
tests the mechanism behind that bit's correlation with the terminal outcome.

Both campaigns are static and run one replica without dynamical decoupling,
which would fill the idles with echo pulses.
"""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit

from experiments import Group, Member
from ripple_experiments import _walk_template

WALK_WIDTH = 4
DELAYS_DT = (4000, 12500)


def _point(width: int, outcome: int) -> np.ndarray:
    ideal = np.zeros(1 << width)
    ideal[outcome] = 1.0
    return ideal


def scaffold_circuits() -> tuple[tuple[str, QuantumCircuit, np.ndarray, dict | None], ...]:
    template, _, readout = _walk_template()
    if template.num_qubits != WALK_WIDTH or template.num_clbits != WALK_WIDTH:
        raise ValueError("the walk template no longer measures four qubits into four clbits")
    plain = QuantumCircuit(WALK_WIDTH, WALK_WIDTH, name="scaffold_measure_only")
    plain.measure(range(WALK_WIDTH), range(WALK_WIDTH))
    flipped = QuantumCircuit(WALK_WIDTH, WALK_WIDTH, name="scaffold_x_measure")
    flipped.x(range(WALK_WIDTH))
    flipped.measure(range(WALK_WIDTH), range(WALK_WIDTH))
    everything = (1 << WALK_WIDTH) - 1
    return (
        ("scaffold_template_readout0", template, _point(WALK_WIDTH, 0), dict(readout[0])),
        ("scaffold_template_readout1", template, _point(WALK_WIDTH, everything), dict(readout[1])),
        ("scaffold_measure_only", plain, _point(WALK_WIDTH, 0), None),
        ("scaffold_x_measure", flipped, _point(WALK_WIDTH, everything), None),
    )


def scaffold_ab_group() -> Group:
    members = tuple(
        Member(name, circuit, ideal, binding=binding) for name, circuit, ideal, binding in scaffold_circuits()
    )

    def summarize(distributions: dict[str, np.ndarray]) -> dict[str, float]:
        template0 = float(distributions["scaffold_template_readout0"][0])
        template1 = float(distributions["scaffold_template_readout1"][-1])
        plain0 = float(distributions["scaffold_measure_only"][0])
        plain1 = float(distributions["scaffold_x_measure"][-1])
        return {
            "template_p0000": template0,
            "template_p1111": template1,
            "measure_only_p0000": plain0,
            "x_measure_p1111": plain1,
            "scaffold_loss_ground": plain0 - template0,
            "scaffold_loss_excited": plain1 - template1,
        }

    return Group(
        "scaffold_ab",
        members,
        summarize,
        rate_keys=frozenset({"template_p0000", "template_p1111", "measure_only_p0000", "x_measure_p1111"}),
    )


def readout_delay_circuits() -> tuple[tuple[str, QuantumCircuit, np.ndarray], ...]:
    ground = QuantumCircuit(1, 1, name="readout_ground")
    ground.measure(0, 0)
    excited = QuantumCircuit(1, 1, name="readout_excited")
    excited.x(0)
    excited.measure(0, 0)
    members = [("readout_ground", ground, _point(1, 0)), ("readout_excited", excited, _point(1, 1))]
    for delay in DELAYS_DT:
        circuit = QuantumCircuit(1, 1, name=f"readout_excited_{delay}dt")
        circuit.x(0)
        circuit.delay(delay, 0, unit="dt")
        circuit.measure(0, 0)
        members.append((circuit.name, circuit, _point(1, 1)))
    return tuple(members)


def readout_delay_group() -> Group:
    members = tuple(Member(name, circuit, ideal) for name, circuit, ideal in readout_delay_circuits())

    def summarize(distributions: dict[str, np.ndarray]) -> dict[str, float]:
        summary = {
            "p1_ground": float(distributions["readout_ground"][1]),
            "p0_excited": float(distributions["readout_excited"][0]),
        }
        for delay in DELAYS_DT:
            summary[f"p0_excited_{delay}dt"] = float(distributions[f"readout_excited_{delay}dt"][0])
        return summary

    return Group(
        "readout_delay",
        members,
        summarize,
        rate_keys=frozenset({"p1_ground", "p0_excited", *(f"p0_excited_{delay}dt" for delay in DELAYS_DT)}),
    )


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


if __name__ == "__main__":
    from qiskit.quantum_info import Statevector

    for name, circuit, ideal, binding in scaffold_circuits():
        bound = circuit.assign_parameters(binding) if binding else circuit
        law = Statevector(bound.remove_final_measurements(inplace=False)).probabilities()
        _require(np.allclose(law, ideal, atol=1e-12), f"{name}: law differs from its ideal")
    for name, circuit, ideal in readout_delay_circuits():
        law = Statevector(circuit.remove_final_measurements(inplace=False)).probabilities()
        _require(np.allclose(law, ideal, atol=1e-12), f"{name}: law differs from its ideal")
    for group in (scaffold_ab_group(), readout_delay_group()):
        ideal_summary = group.summarize({member.name: member.ideal for member in group.members})
        _require(all(abs(value) < 1e-12 or abs(value - 1.0) < 1e-12 for value in ideal_summary.values()), group.name)
    print("diagnostic controls: scaffold A/B and delayed readout match their ideal laws")
