"""The compiled-ideal proof pools its replicas in entry order and fails on the first mismatch."""

from __future__ import annotations

import inspect
import os
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pytest
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

import live_run
import qpu_planning


def check(condition: bool, message: str = "check failed") -> None:
    """Raise on a false condition; python -O strips assert, so a check raises explicitly."""
    if not condition:
        raise AssertionError(message)


def coin() -> QuantumCircuit:
    circuit = QuantumCircuit(QuantumRegister(1, "q"), ClassicalRegister(1, "c"))
    circuit.h(0)
    circuit.measure(0, 0)
    return circuit


def choice(count: int, wrong: tuple[int, ...] = ()) -> SimpleNamespace:
    entries = [
        SimpleNamespace(
            name=f"member_{k}",
            replicas=[coin()],
            ideal=np.asarray([0.9, 0.1]) if k in wrong else np.asarray([0.5, 0.5]),
        )
        for k in range(count)
    ]
    return SimpleNamespace(entries=entries)


def test_passes_when_every_replica_equals_its_ideal() -> None:
    qpu_planning.check_compiled_ideals(live_run, [choice(2 * qpu_planning.IDEAL_PARALLEL_MIN_ITEMS)])


def test_the_first_failing_entry_in_order_is_named_pooled_and_serial() -> None:
    wrong = (5, 3 * qpu_planning.IDEAL_PARALLEL_MIN_ITEMS // 2)
    many = choice(2 * qpu_planning.IDEAL_PARALLEL_MIN_ITEMS, wrong)
    messages = []
    for workers in (None, "1"):
        env = {} if workers is None else {"GOROROBA_WORKERS": workers}
        with patch.dict(os.environ, env), pytest.raises(live_run.LiveRunError) as error:
            qpu_planning.check_compiled_ideals(live_run, [many])
        messages.append(str(error.value))
    check(messages[0] == messages[1] == "member_5: compiled labeled ideal differs from its exact oracle", f"{messages}")


def test_the_submit_path_proves_ideals_through_the_pooled_helper() -> None:
    source = inspect.getsource(live_run.approved_family_design)
    check("check_compiled_ideals" in source and "ideal_compiled_probabilities" not in source)
    check("check_compiled_ideals" in inspect.getsource(qpu_planning.prepare))


def rotation(angle: float, physical: int, name: str) -> QuantumCircuit:
    """rx(angle) and a measurement on device wire physical of a five-wire circuit."""
    circuit = QuantumCircuit(QuantumRegister(5, "q"), ClassicalRegister(1, "c"), name=name)
    circuit.rx(angle, physical)
    circuit.measure(physical, 0)
    return circuit


def test_copies_on_other_wires_share_one_oracle_input() -> None:
    from qpe_diagnostics import compact_ideal_circuit, oracle_key

    keys = {oracle_key(compact_ideal_circuit(rotation(0.7, wire, f"m_q{wire}"))) for wire in range(5)}
    check(len(keys) == 1, f"one member on five wires compacts to one oracle input: {keys}")
    check(oracle_key(compact_ideal_circuit(rotation(0.7000001, 2, "m_q2"))) not in keys, "an angle moves the key")


def test_a_perturbed_copy_fails_alone() -> None:
    """One copy compiled with a perturbed angle fails its own entry; the shared law clears every other copy."""
    angle = 0.7
    law = [np.cos(angle / 2) ** 2, np.sin(angle / 2) ** 2]
    entries = [
        SimpleNamespace(
            name=f"m_q{wire}",
            replicas=[rotation(angle + (0.1 if wire == 3 else 0.0), wire, "m")],
            ideal=np.asarray(law),
        )
        for wire in range(5)
    ]
    with pytest.raises(live_run.LiveRunError, match="m_q3: compiled labeled ideal differs"):
        qpu_planning.check_compiled_ideals(live_run, [SimpleNamespace(entries=entries)])
    entries[3].replicas = [rotation(angle, 3, "m")]
    qpu_planning.check_compiled_ideals(live_run, [SimpleNamespace(entries=entries)])
