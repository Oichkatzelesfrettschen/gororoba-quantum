"""Credential-free contract checks for dynamic Runtime orchestration helpers."""

from __future__ import annotations

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister, transpile
from qiskit.primitives import StatevectorSampler
from qiskit_ibm_runtime.executor_sampler import Sampler
from qiskit_ibm_runtime.fake_provider import FakeFez, FakeManilaV2

import hybrid_shor  # noqa: F401 - proves the digest ignores module load order
import packing
from experiments import MIRROR_SUFFIX, experiment_groups
from live_run import (
    LiveRunError,
    _distribution,
    _is_dynamic,
    _ops,
    _pub_counts,
    configure_sampler,
    experiment_digest,
)
from order_finding import factor_order_finding


def _verify_dynamic_classification() -> None:
    final_measurement = QuantumCircuit(2, 2)
    final_measurement.h(0)
    final_measurement.measure([0, 1], [0, 1])
    if _is_dynamic(final_measurement):
        raise RuntimeError("terminal measurements classify as dynamic")

    later_work = QuantumCircuit(2, 1)
    later_work.measure(0, 0)
    later_work.x(1)
    if not _is_dynamic(later_work):
        raise RuntimeError("measurement followed by work on another qubit classifies as static")


def _verify_nested_operations() -> None:
    nested = QuantumCircuit(2, 1)
    nested.measure(0, 0)
    with nested.if_test((nested.clbits[0], 1)):
        nested.cz(0, 1)
    operations = _ops(nested)
    if operations != [("measure", (0,)), ("cz", (0, 1))]:
        raise RuntimeError(f"nested physical operations decode as {operations}")

    operation_names = ("cswap", "p", "measure", "reset")
    shor_operations = _ops(factor_order_finding(15, 2, 8))
    counts = {name: sum(operation == name for operation, _ in shor_operations) for name in operation_names}
    expected = {"cswap": 5, "p": 1, "measure": 2, "reset": 1}
    if counts != expected:
        raise RuntimeError(f"N=15 dynamic operation coefficients are {counts}")
    null_operations = _ops(factor_order_finding(15, 2, 8, identity=True))
    null_counts = {name: sum(operation == name for operation, _ in null_operations) for name in operation_names}
    expected_null = {"cswap": 0, "p": 1, "measure": 2, "reset": 1}
    if null_counts != expected_null:
        raise RuntimeError(f"N=15 identity-null operation coefficients are {null_counts}")


def _verify_result_register_order() -> None:
    qubits = QuantumRegister(2, "q")
    low = ClassicalRegister(1, "low")
    high = ClassicalRegister(1, "high")
    circuit = QuantumCircuit(qubits, low, high)
    circuit.x(qubits[0])
    circuit.measure(qubits[0], low[0])
    circuit.measure(qubits[1], high[0])
    pub = StatevectorSampler(seed=1).run([circuit], shots=8).result()[0]
    counts = _pub_counts(pub, [register.name for register in circuit.cregs], circuit.name)
    if counts != {"01": 8}:
        raise RuntimeError(f"multi-register counts decode as {counts}")
    distribution = _distribution(counts, circuit.num_clbits)
    if distribution[1] != 1.0:
        raise RuntimeError(f"multi-register distribution places probability at {distribution.argmax()}")


def _verify_packed_replica_split() -> None:
    """Packed replicas of a dynamic circuit split back into each replica's own counts.

    Replicas 0 and 2 start with their first qubit flipped and replica 1 does
    not, so the feed-forward circuit reads 11, 00, 11; a split that mixed
    registers or replicas would read another replica's outcome. The packed
    circuit runs through the client-side Sampler in local mode on FakeFez.
    """
    backend = FakeFez()
    graph = packing.coupling_graph(backend.target, backend.num_qubits)
    phase = ClassicalRegister(2, "phase")
    template = QuantumCircuit(QuantumRegister(2, "q"), phase)
    template.measure(0, phase[0])
    with template.if_test((phase[0], 1)):
        template.x(1)
    template.measure(1, phase[1])
    isa = transpile(template, backend=backend, optimization_level=0, initial_layout=[0, 1])
    used, edges = packing.pattern([("cz", (0, 1))])
    replicas = packing.place(used, edges, graph, lambda _: True, lambda m: 1.0 / (1 + min(m.values())), 1e-9, 3)
    if len(replicas) != 3 or len({q for r in replicas for q in r.qubits}) != 6:
        raise RuntimeError(f"placement returned overlapping or missing replicas: {replicas}")
    packed = packing.pack(isa, replicas, "packed")
    flips = QuantumCircuit(packed.num_qubits)
    flips.x([replicas[0].mapping[0], replicas[2].mapping[0]])
    packed = packed.compose(flips, front=True)
    if [r.name for r in packed.cregs] != [f"r{k}_phase" for k in range(3)]:
        raise RuntimeError(f"packed registers are {[r.name for r in packed.cregs]}")
    pub = Sampler(mode=backend).run([packed], shots=64).result()[0]
    for replica in replicas:
        single = packing.split(packed, replica.prefix, replica.qubits)
        if single.num_clbits != 2 or not _is_dynamic(single):
            raise RuntimeError(f"replica {replica.prefix} splits to {single.num_clbits} clbits")
        counts = _pub_counts(pub, packing.registers(packed, replica.prefix), replica.prefix)
        top = max(counts, key=lambda key: counts[key])
        if top != ("00" if replica.index == 1 else "11") or counts[top] < 48:
            raise RuntimeError(f"replica {replica.prefix} reads {counts}")


def _verify_packed_static_stays_static() -> None:
    """Packing replicas of a static circuit keeps every measurement after every gate.

    The static and dynamic Sampler jobs split on _is_dynamic, so a packed
    static circuit that read as dynamic would lose twirling and dynamical
    decoupling at submission.
    """
    backend = FakeFez()
    graph = packing.coupling_graph(backend.target, backend.num_qubits)
    bell = QuantumCircuit(2, 2)
    bell.h(0)
    bell.cx(0, 1)
    bell.measure([0, 1], [0, 1])
    isa = transpile(bell, backend=backend, optimization_level=1, initial_layout=[0, 1])
    used, edges = packing.pattern([("cz", (0, 1))])
    replicas = packing.place(used, edges, graph, lambda _: True, lambda m: 1.0 / (1 + min(m.values())), 1e-9, 4)
    packed = packing.pack(isa, replicas, "bell")
    if _is_dynamic(isa) or _is_dynamic(packed):
        raise RuntimeError("packing a static circuit produced a dynamic one")


def _verify_rate_keys() -> None:
    """Every declared per-shot rate names a value its group's summary produces.

    A misspelled rate key would silently drop the pooled-shot Wilson bound
    from that value's interval.
    """
    for group in experiment_groups():
        ideals: dict[str, np.ndarray] = {}
        for member in group.members:
            ideals[member.name] = member.ideal
            if member.mirror:
                zeros = np.zeros(len(member.ideal))
                zeros[0] = 1.0
                ideals[member.name + MIRROR_SUFFIX] = zeros
        unknown = set(group.rate_keys) - set(group.summarize(ideals))
        if unknown:
            raise RuntimeError(f"{group.name}: rate keys {sorted(unknown)} are not summary values")


def _verify_twirling_shot_contract() -> None:
    sampler = configure_sampler(FakeManilaV2(), "static", True, None, ["local-contract"], shots=4096)
    if sampler.options.twirling.num_randomizations != 32:
        raise RuntimeError(f"twirling uses {sampler.options.twirling.num_randomizations} randomizations")
    if sampler.options.twirling.shots_per_randomization != 128:
        raise RuntimeError(f"twirling uses {sampler.options.twirling.shots_per_randomization} shots per randomization")
    try:
        configure_sampler(FakeManilaV2(), "static", True, None, ["local-contract"], shots=16)
    except LiveRunError:
        pass
    else:
        raise RuntimeError("twirling accepted a shot count that Runtime 0.50 rounds upward")


def _verify() -> None:
    _verify_dynamic_classification()
    _verify_nested_operations()
    _verify_result_register_order()
    _verify_twirling_shot_contract()
    _verify_packed_replica_split()
    _verify_packed_static_stays_static()
    _verify_rate_keys()
    first_digest = experiment_digest()
    second_digest = experiment_digest()
    if len(first_digest) != 64 or first_digest != second_digest:
        raise RuntimeError("experiment source manifest digest is unstable")
    print(
        "runtime contracts: dynamic classification, nested operations, register order, packed replica split, "
        "packed static classification, rate keys, "
        "and digest pass"
    )


if __name__ == "__main__":
    _verify()
