"""The primorial live_run campaigns on a pinned three-qubit path: the coherence probes and gap-88 tomography.

docs/design/primorial-cover-defect-probes.md defines the protocol and primorial_tomography the arms and fit:
for each cube edge (j, x) with x_j = 0 an arm prepares (|x> + |x ^ 2^j>)/sqrt2, applies exp(-i gamma H) through
the eight-CNOT parity network at gamma = pi/9 and reads qubit j in X and Y. The campaign runs, per edge and
basis, four members that bind one parametrized circuit, listed in the +, -, -, + order of a contrast:

- ``g88`` and ``g88rep``, the network's seven RZ angles at 2 gamma c_S of the gap-88 cost table;
- ``null`` and ``nullrep``, every angle zero, the identity map with the same CZ count and schedule.

The signal reading averages the two gap-88 executions and the null reading the two null executions, so a
position effect linear in the member order cancels. Each repeated pair is a drift monitor: the fit of one
copy against the other reads zero coefficients unless the device moved between them.

Binding one circuit makes the four members' compiled pulse streams identical by construction
(experiments.Member.binding); they differ only in the zero-duration RZ angles. Eight basis preparations
give the per-qubit assignment channel. Every member carries coherence_probes' structure-preserving
compilation contract, so live_run compiles at optimization level 0 and the zero-angle network stays in the
circuit.

The summary inverts each quadrature through its qubit's assignment channel, fits the null-subtracted
coefficients c_S (primorial_tomography.null_subtracted) and reports each against its exact value, the
largest bias, whether every coefficient sits inside the identification radius 1/16, and the drift monitor's
largest coefficient.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter

import coherence_probes as cp
import parallel
import primorial_tomography as tomography
from coherence_probes import STRUCTURE_PRESERVING_CONTRACT
from experiments import Group, Member

# The +, -, -, + order of each setting's contrast (docs/notes/algebra_circuit_rules.md, Hardware probes).
ARMS = ("g88", "null", "nullrep", "g88rep")
COSTS = {"g88": "gap88", "null": "null", "nullrep": "nullrep", "g88rep": "gap88rep"}


def angles(table: list[int]) -> dict[int, float]:
    c = tomography.coefficients(table)
    return {
        mask: 2.0 * tomography.GRADIENT_GAMMA * c["".join(str(j) for j in range(3) if mask >> j & 1)]
        for mask in range(1, 8)
    }


def parametrized_arm(j: int, x: int, basis: str) -> tuple[QuantumCircuit, dict[int, Parameter]]:
    """gradient_arm's circuit with each network angle a Parameter."""
    parameters = {mask: Parameter(f"a{mask}") for mask in range(1, 8)}
    circuit = QuantumCircuit(3, 3, name=f"g88_{j}_{x}_{basis}")
    for i in range(3):
        if i != j and x >> i & 1:
            circuit.x(i)
    circuit.h(j)
    circuit.barrier()
    tomography.parity_network(circuit, parameters)
    circuit.barrier()
    if basis == "Y":
        circuit.sdg(j)
    circuit.h(j)
    circuit.measure(range(3), range(3))
    circuit.metadata = {"compilation_contract": STRUCTURE_PRESERVING_CONTRACT}
    return circuit, parameters


def readout_arm(label: int) -> QuantumCircuit:
    circuit = tomography.basis_arm(3, label)
    circuit.name = f"g88_readout_{label}"
    circuit.metadata = {"compilation_contract": STRUCTURE_PRESERVING_CONTRACT}
    return circuit


class IdealLaw:
    """Picklable worker: one bound circuit -> its noise-free outcome law."""

    def __call__(self, circuit: QuantumCircuit) -> np.ndarray:
        return cp.ideal_distribution(circuit)


def members() -> tuple[Member, ...]:
    """Every gap-88 member, its ideal law computed through the process pool in member order."""
    signal = angles(tomography.cost_table("gap88"))
    planned: list[tuple[str, QuantumCircuit, dict[Parameter, float] | None, QuantumCircuit]] = []
    for j, x in tomography.edges():
        for basis in ("X", "Y"):
            circuit, parameters = parametrized_arm(j, x, basis)
            for arm in ARMS:
                values = signal if COSTS[arm].startswith("gap88") else dict.fromkeys(signal, 0.0)
                binding = {parameters[mask]: values[mask] for mask in parameters}
                planned.append((f"{arm}_{j}_{x}_{basis}", circuit, binding, circuit.assign_parameters(binding)))
    for label in range(8):
        circuit = readout_arm(label)
        planned.append((circuit.name, circuit, None, circuit))
    ideals = parallel.ordered_map(IdealLaw(), [bound for *_, bound in planned])
    return tuple(
        Member(name, circuit, ideal, binding=binding)
        for (name, circuit, binding, _), ideal in zip(planned, ideals, strict=True)
    )


def rows_of(distributions: Mapping[str, np.ndarray]) -> list[dict[str, Any]]:
    """primorial_tomography rows: gradient arms under costs gap88, null, nullrep and gap88rep, and the readout arms."""
    out: list[dict[str, Any]] = []
    for j, x in tomography.edges():
        for basis in ("X", "Y"):
            for arm in ARMS:
                law = [float(v) for v in distributions[f"{arm}_{j}_{x}_{basis}"]]
                out.append({"family": "gradient", "cost": COSTS[arm], "j": j, "x": x, "basis": basis, "law": law})
    for label in range(8):
        out.append(
            {"family": "readout3", "label": label, "law": [float(v) for v in distributions[f"g88_readout_{label}"]]}
        )
    return out


def summarize(distributions: Mapping[str, np.ndarray]) -> dict[str, float]:
    """Null-subtracted gap-88 coefficients, their biases, identification and the drift monitor."""
    rows = rows_of(distributions)
    flips = tomography.assignment(rows)
    a = np.asarray([flips[j][0] for j, _ in tomography.edges()])
    b = np.asarray([flips[j][1] for j, _ in tomography.edges()])

    def readings(cost: str) -> tuple[np.ndarray, np.ndarray]:
        x_read, y_read = tomography.gradient_readings(rows, cost)
        return tomography.corrected(x_read, a, b), tomography.corrected(y_read, a, b)

    first, again = readings("gap88"), readings("gap88rep")
    zero, zero_again = readings("null"), readings("nullrep")
    signal = ((first[0] + again[0]) / 2, (first[1] + again[1]) / 2)
    null = ((zero[0] + zero_again[0]) / 2, (zero[1] + zero_again[1]) / 2)
    unit = np.ones_like(signal[0])
    fit = tomography.null_subtracted(tomography.cost_table("gap88"), *signal, null, unit, unit)
    exact = tomography.coefficients(tomography.cost_table("gap88"))
    # Each repeat read against its first copy on the zero table: the recovered coefficients are the drift.
    zero_table = tomography.cost_table("null")
    null_drift = tomography.null_subtracted(zero_table, *zero_again, zero, unit, unit)["max_coefficient_bias"]
    signal_drift = tomography.null_subtracted(zero_table, *again, first, unit, unit)["max_coefficient_bias"]
    out: dict[str, float] = {}
    for key, value in fit["recovered_coefficients"].items():
        out[f"c_{key}"] = float(value)
        out[f"bias_{key}"] = float(value - exact[key])
    out["max_bias"] = float(fit["max_coefficient_bias"])
    out["identified"] = float(fit["max_coefficient_bias"] < tomography.IDENTIFY_RADIUS)
    out["drift_null"] = float(null_drift)
    out["drift_signal"] = float(signal_drift)
    out["drift_max"] = float(max(null_drift, signal_drift))
    out["cycle_residual_rms"] = float(fit["cycle_residual_rms"])
    return out


def gap88_group() -> Group:
    return Group("primorial_gap88", members(), summarize)


def coherence_probe_group() -> Group:
    """Every coherence probe on one pinned three-qubit path, the readout calibrations included."""
    probes = cp.circuits()
    ideals = parallel.ordered_map(IdealLaw(), [circuit for _, circuit in probes])
    probe_members = tuple(Member(name, circuit, ideal) for (name, circuit), ideal in zip(probes, ideals, strict=True))
    return Group(
        "coherence_probes", probe_members, cp.summarize, summarize_with_covariance=cp.summarize_with_covariance
    )
