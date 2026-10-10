"""Credential-free contract checks for dynamic Runtime orchestration helpers."""

from __future__ import annotations

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit.primitives import StatevectorSampler
from qiskit_ibm_runtime.fake_provider import FakeManilaV2

import hybrid_shor  # noqa: F401 - proves the digest ignores module load order
from live_run import LiveRunError, _distribution, _is_dynamic, _ops, _pub_counts, configure_sampler, experiment_digest
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
    counts = _pub_counts(pub, circuit)
    if counts != {"01": 8}:
        raise RuntimeError(f"multi-register counts decode as {counts}")
    distribution = _distribution(counts, circuit.num_clbits)
    if distribution[1] != 1.0:
        raise RuntimeError(f"multi-register distribution places probability at {distribution.argmax()}")


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
    first_digest = experiment_digest()
    second_digest = experiment_digest()
    if len(first_digest) != 64 or first_digest != second_digest:
        raise RuntimeError("experiment source manifest digest is unstable")
    print("runtime contracts: dynamic classification, nested operations, register order, and digest pass")


if __name__ == "__main__":
    _verify()
