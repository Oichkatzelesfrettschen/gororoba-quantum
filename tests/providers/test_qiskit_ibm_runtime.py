"""qiskit-ibm-runtime local paths the repository calls: fake-backend scheduling (transpile with scheduling_method)
and the client-side executor Sampler that live_run.py submits through. Nothing here reads an account."""

from __future__ import annotations

from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime.executor_sampler import Sampler
from qiskit_ibm_runtime.fake_provider import FakeFez, FakeManilaV2


def test_fake_backend_targets_carry_durations_for_scheduling() -> None:
    backend = FakeFez()
    if backend.target.dt is None or not backend.target["cz"]:
        raise AssertionError("the fake target lost dt or its cz edges")
    circuit = QuantumCircuit(2, 2)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.delay(320, 1, "dt")
    circuit.measure([0, 1], [0, 1])
    compiled = transpile(
        circuit,
        backend=backend,
        initial_layout=[3, 4],
        scheduling_method="alap",
        optimization_level=1,
    )
    if compiled.layout.initial_index_layout()[:2] != [3, 4] or compiled.estimate_duration(backend.target) <= 0:
        raise AssertionError("layout or schedule lost")


def test_executor_sampler_runs_locally_on_a_fake_backend() -> None:
    circuit = QuantumCircuit(2, 2)
    circuit.x(0)
    circuit.cx(0, 1)
    circuit.measure([0, 1], [0, 1])
    backend = FakeManilaV2()
    pub = Sampler(mode=backend).run([transpile(circuit, backend)], shots=64).result()[0]
    counts = pub.data.c.get_counts()
    if sum(counts.values()) != 64 or max(counts, key=lambda key: counts[key]) != "11":
        raise AssertionError(counts)
