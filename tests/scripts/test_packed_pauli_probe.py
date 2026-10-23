"""Small-cell operator checks precede composing unsimulated wide reference programs."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from qiskit.quantum_info import Statevector

import bdsc


def probe() -> Any:
    try:
        return importlib.import_module("packed_pauli_probe")
    except ModuleNotFoundError:
        pytest.fail("the source-bound packed response proposal generator is absent")


@pytest.mark.parametrize(("name", "expected"), [("kernel", 0.0), ("bright", 1.0), ("middle", 0.5)])
def test_prepared_cell_has_the_certified_effect_score(name: str, expected: float) -> None:
    state = Statevector.from_instruction(probe().prepare_cell(name)).data
    actual = float(np.vdot(state, bdsc.ideal_effect() @ state).real)
    if abs(actual - expected) > 1e-14:
        raise AssertionError("the prepared cell changed the ideal dark/bright/middle law")


def test_quadruple_readout_preserves_the_joint_score_law() -> None:
    module = probe()
    for name, expected in (("kernel", 0.0), ("bright", 1.0)):
        circuit = module.prepare_cell(name).compose(module.readout_cell("Y"))
        probabilities = Statevector.from_instruction(circuit).probabilities()
        actual = sum(probability * module.score(label) for label, probability in enumerate(probabilities))
        if abs(actual - expected) > 1e-14:
            raise AssertionError("the measurement map changed the target effect")


def test_only_load_preparation_changes_between_reference_programs() -> None:
    module = probe()
    sparse = module.program(5, False)
    dense = module.program(5, True)
    if sparse.num_qubits != 20 or dense.num_qubits != 20 or sparse.num_clbits != dense.num_clbits:
        raise AssertionError("the acquisition changed the joint readout register")
    if sparse.count_ops()["measure"] != 20 or dense.count_ops()["measure"] != 20:
        raise AssertionError("the density intervention changed measurement width")
    if dense.count_ops()["cx"] - sparse.count_ops()["cx"] != 2:
        raise AssertionError("the load cell did not add its two preparation entanglers")


def test_iqm_plan_has_sixteen_randomized_pairs_and_four_references() -> None:
    result = probe().schedule("iqm:emerald")
    science = [row for row in result if row["kind"] == "science"]
    if len(result) != 36 or len(science) != 32:
        raise AssertionError("the acquisition lost paired replication or readout references")
    for offset in range(0, 32, 2):
        if {row["dense"] for row in science[offset : offset + 2]} != {False, True}:
            raise AssertionError("a randomized pair lost an intervention arm")


def test_ion_plan_is_explicitly_small_job_count_under_the_shared_spark_budget() -> None:
    rows = probe().schedule("ionq:forte-1")
    if len(rows) != 4 or any(row["kind"] != "science" for row in rows):
        raise AssertionError("the ion qualification exceeded its four-job case")


@pytest.mark.parametrize(
    ("backend", "proposal"),
    [
        ("iqm:emerald", "results/iqm/proposals/packed-pauli-response-emerald"),
        ("iqm:garnet", "results/iqm/proposals/packed-pauli-response-garnet"),
        ("ionq:forte-1", "results/open_quantum/proposals/packed-pauli-response-ionq"),
        ("rigetti:cepheus-1-108q", "results/open_quantum/proposals/packed-pauli-response-rigetti"),
    ],
)
def test_reference_proposal_replays_from_bound_sources(backend: str, proposal: str) -> None:
    root = Path(__file__).resolve().parents[2]
    probe().check(root / "docs/evidence/provider-api-audit", backend, root / proposal)
