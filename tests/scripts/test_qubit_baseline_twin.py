"""Unit tests for the Qubit baseline twin simulation."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

from qubit_baseline_twin import (  # noqa: E402
    build_twin_circuit,
    get_character_frequency,
    run_aer_twin,
)


def test_character_frequency_values() -> None:
    if get_character_frequency(1, 2) != 4:
        raise AssertionError("omega for (1, 2) != 4")
    if get_character_frequency(1, 4) != 2:
        raise AssertionError("omega for (1, 4) != 2")
    if get_character_frequency(2, 4) != 1:
        raise AssertionError("omega for (2, 4) != 1")
    if get_character_frequency(3, 5) != 7:
        raise AssertionError("omega for (3, 5) != 7")


def test_twin_circuit_construction() -> None:
    qc_oct = build_twin_circuit(1, 2, "octonion")
    if qc_oct.num_qubits != 3 or qc_oct.num_clbits != 3:
        raise AssertionError("qc_oct dimension mismatch")

    qc_ctrl = build_twin_circuit(1, 2, "clifford_control")
    if qc_ctrl.num_qubits != 3:
        raise AssertionError("qc_ctrl dimension mismatch")


def test_aer_twin_execution() -> None:
    res = run_aer_twin(shots=512)
    if len(res) != 4:
        raise AssertionError("result count != 4")
    for _pair_key, data in res.items():
        if data["d_oct"] != 1.0:
            raise AssertionError(f"d_oct {data['d_oct']} != 1.0")
        if data["d_ctrl"] != -1.0:
            raise AssertionError(f"d_ctrl {data['d_ctrl']} != -1.0")
        if data["delta_character"] != 2.0:
            raise AssertionError(f"delta_character {data['delta_character']} != 2.0")
