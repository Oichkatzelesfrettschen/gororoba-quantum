"""Check the existing archived-PUB ownership boundary for global barriers."""

import pytest
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

from live_run import LiveRunError, _validate_archived_pub


def fixture(operation: str) -> tuple[dict[str, object], QuantumCircuit]:
    quantum = QuantumRegister(2, "q")
    first = ClassicalRegister(1, "first")
    second = ClassicalRegister(1, "second")
    circuit = QuantumCircuit(quantum, first, second, name="shared-register")
    circuit.x(0)
    circuit.x(1)
    if operation == "global_barrier":
        circuit.barrier(0, 1)
    elif operation == "cross_component_cz":
        circuit.cz(0, 1)
    elif operation == "local_barriers":
        circuit.barrier(0)
        circuit.barrier(1)
    else:
        raise ValueError("unknown fixture operation")
    circuit.measure(0, first[0])
    circuit.measure(1, second[0])
    manifest: dict[str, object] = {
        "name": "shared-register",
        "backend": "fixture-backend",
        "kind": "static",
        "components": [
            {
                "member": "first",
                "register_prefix": "first",
                "registers_by_replica": [["first"]],
                "physical_qubits": [0],
            },
            {
                "member": "second",
                "register_prefix": "second",
                "registers_by_replica": [["second"]],
                "physical_qubits": [1],
            },
        ],
    }
    return manifest, circuit


def test_component_local_barriers_pass_current_ownership_check() -> None:
    manifest, circuit = fixture("local_barriers")
    _validate_archived_pub(manifest, circuit, "fixture-backend", "static")


@pytest.mark.parametrize("operation", ["global_barrier", "cross_component_cz"])
def test_current_ownership_check_rejects_cross_component_operations(operation: str) -> None:
    manifest, circuit = fixture(operation)
    with pytest.raises(LiveRunError, match="owners"):
        _validate_archived_pub(manifest, circuit, "fixture-backend", "static")
