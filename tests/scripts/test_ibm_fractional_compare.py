"""ibm_fractional_compare: the fractional Target compiles rzz workloads to rzz and keeps every angle in range."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

pytest.importorskip("qiskit")
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import ibm_fractional_compare as fc  # noqa: E402


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


@pytest.fixture(scope="module")
def entry() -> dict[str, Any]:
    snapshot = json.loads(fc.SNAPSHOT.read_text(encoding="utf-8"))
    entry: dict[str, Any] = snapshot["backends"]["ibm_fez"]
    return entry


def test_targets_differ_by_the_fractional_instructions(entry: dict[str, Any]) -> None:
    standard = fc.target_from_snapshot(entry, fractional=False)
    fractional = fc.target_from_snapshot(entry, fractional=True)
    require("rzz" not in standard.operation_names and "rx" not in standard.operation_names, "standard has no rzz or rx")
    require({"rzz", "rx", "measure", "x"} <= set(fractional.operation_names), "fractional keeps the standard measure")


def test_rzz_chain_compiles_to_rzz_without_cz(entry: dict[str, Any]) -> None:
    standard = fc.target_from_snapshot(entry, fractional=False)
    fractional = fc.target_from_snapshot(entry, fractional=True)
    circuit = fc.ising_chain(width=4, steps=2)
    std = fc.summarize(fc.compile_arm(circuit, standard, False, None), standard)
    frac = fc.summarize(fc.compile_arm(circuit, fractional, True, None), fractional)
    require(std["ops"].get("cz", 0) == 2 * frac["ops"].get("rzz", 0), "each rzz costs two cz on the standard Target")
    require(frac["ops"].get("cz", 0) == 0, "no cz remains beside rzz")
    require(frac["rzz_outside_range"] == 0, "every rzz angle lies in (0, pi/2]")
    require(frac["duration_dt"] < std["duration_dt"], "fractional compile is shorter")
    require(frac["error_budget"] < std["error_budget"], "fractional compile spends less gate error")


def test_out_of_range_rzz_is_counted() -> None:
    from qiskit import QuantumCircuit

    circuit = QuantumCircuit(2)
    circuit.rzz(2.0, 0, 1)
    circuit.rzz(0.5, 0, 1)
    require(fc.rzz_outside_range(circuit) == 1, "one angle exceeds pi/2")


def test_control_flow_gates_count_in_ops_budget_and_angles() -> None:
    from qiskit import QuantumCircuit

    circuit = QuantumCircuit(2, 1)
    circuit.measure(0, 0)
    with circuit.if_test((circuit.clbits[0], True)):
        circuit.rzz(2.0, 0, 1)
        circuit.x(1)
    require(circuit.count_ops().get("rzz", 0) == 0, "the top level shows no rzz")
    require(fc.count_ops(circuit).get("rzz") == 1 and fc.count_ops(circuit).get("x") == 1, "blocks are counted")
    require(fc.rzz_outside_range(circuit) == 1, "the angle check descends into the block")


def test_block_qubits_map_to_the_enclosing_instruction() -> None:
    from qiskit import QuantumCircuit

    circuit = QuantumCircuit(3, 1)
    circuit.measure(0, 0)
    with circuit.if_test((circuit.clbits[0], True)):
        circuit.cx(1, 2)
    inner = [qargs for operation, qargs in fc.walk(circuit) if operation.name == "cx"]
    require(inner == [(1, 2)], "the block's qubits are the outer indices")


def test_shared_placement_fixes_the_fractional_layout(entry: dict[str, Any]) -> None:
    rows = fc.compare(entry, None, "shared")
    for name, row in rows.items():
        require(row["standard"]["layout"] == row["fractional"]["layout"], f"{name} shares its layout")
    require(rows["ising_rzz_rx_chain"]["fractional"]["ops"].get("rzz", 0) > 0, "the shared arm keeps rzz")
