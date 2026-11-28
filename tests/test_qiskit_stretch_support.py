"""Qiskit stretch support that the IBM execution roadmap relies on."""

from __future__ import annotations

import pytest

qiskit = pytest.importorskip("qiskit")
from qiskit import QuantumCircuit, transpile  # noqa: E402
from qiskit.circuit import Duration  # noqa: E402
from qiskit.circuit.classical import expr  # noqa: E402


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_stretch_delay_expressions_build() -> None:
    qc = QuantumCircuit(2)
    s = qc.add_stretch("s")
    qc.delay(s, 0)
    qc.delay(expr.add(expr.mul(s, 2), Duration.dt(160)), 1)
    require(qc.num_stretches == 1, "qc.num_stretches == 1")
    require(
        [inst.operation.name for inst in qc.data] == ["delay", "delay"],
        '[inst.operation.name for inst in qc.data] == ["delay", "dela',
    )


def test_stretch_delay_survives_transpile_on_heron_target() -> None:
    fake = pytest.importorskip("qiskit_ibm_runtime.fake_provider")
    backend = fake.FakeFez()
    qc = QuantumCircuit(2)
    qc.delay(qc.add_stretch("s"), 0)
    qc.x(1)
    out = transpile(qc, backend, optimization_level=1)
    require(out.num_stretches == 1, "out.num_stretches == 1")
    require(dict(out.count_ops()) == {"delay": 1, "x": 1}, 'dict(out.count_ops()) == {"delay": 1, "x": 1}')
