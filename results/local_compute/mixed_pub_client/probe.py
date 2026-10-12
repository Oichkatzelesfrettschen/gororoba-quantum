"""Qualify mixed PUB preparation and decoding on a credential-free CPU simulator."""

from __future__ import annotations

import json
from importlib.metadata import version
from typing import Any

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.executor_sampler import Sampler


def validate_counts(counts: list[dict[str, int]]) -> None:
    """Reject changed distributions or PUB order even when assertions are disabled."""
    expected = [{"11": 64}, {"01": 64}]
    if counts != expected:
        raise RuntimeError(f"mixed PUB counts or order differ: expected {expected}, received {counts}")


def run_probe() -> dict[str, Any]:
    backend = AerSimulator(method="stabilizer", device="CPU", max_parallel_threads=1, max_parallel_experiments=1)
    dynamic_circuit = QuantumCircuit(2, 2, name="mixed_probe_dynamic")
    dynamic_circuit.x(0)
    dynamic_circuit.measure(0, 0)
    with dynamic_circuit.if_test((dynamic_circuit.clbits[0], 1)):
        dynamic_circuit.x(1)
    dynamic_circuit.reset(0)
    dynamic_circuit.measure(1, 1)
    static_circuit = QuantumCircuit(2, 2, name="mixed_probe_static")
    static_circuit.x(0)
    static_circuit.measure([0, 1], [0, 1])
    sampler = Sampler(mode=backend)
    sampler.options.twirling.enable_gates = False
    sampler.options.twirling.enable_measure = False
    sampler.options.dynamical_decoupling.enable = False
    sampler.options.simulator.seed_simulator = 7
    job = sampler.run([dynamic_circuit, static_circuit], shots=64)
    result = job.result()
    counts = [pub.data.c.get_counts() for pub in result]
    validate_counts(counts)
    return {
        "versions": {name: version(name) for name in ("qiskit", "qiskit-aer", "qiskit-ibm-runtime")},
        "execution": "credential-free local CPU Aer stabilizer",
        "job_type": type(job).__name__,
        "pub_count": len(result),
        "shots_per_pub": 64,
        "counts_in_submitted_order": counts,
        "twirling_gates": sampler.finalize_options().twirling.enable_gates,
        "twirling_measure": sampler.finalize_options().twirling.enable_measure,
        "dd": sampler.finalize_options().dynamical_decoupling.enable,
    }


if __name__ == "__main__":
    print(json.dumps(run_probe(), indent=2))
