"""Contracts of the relaxation prediction and record check of the orientation-bit case.

The thermal-relaxation model is calibrated on a circuit whose decay has a closed form, the record comparison on a
known-equal and known-different pair, and the calibration reader on the retained record it reads.
"""

from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from qiskit import QuantumCircuit

ROOT = Path(__file__).resolve().parents[2]
DIRECTORY = ROOT / "docs/evidence/pathion-kernel-map/orientation-bit"
sys.path.insert(0, str(ROOT / "docs/evidence/pathion-kernel-map/nhat-bias"))
sys.path.insert(0, str(DIRECTORY))
SPEC = importlib.util.spec_from_file_location("orientation_bit_compile_case", DIRECTORY / "compile_case.py")
if SPEC is None or SPEC.loader is None:
    raise ImportError("compile_case.py is not importable")
cc = importlib.util.module_from_spec(SPEC)
sys.modules["orientation_bit_compile_case"] = cc
SPEC.loader.exec_module(cc)


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _calibration() -> Any:
    if not cc.RETAINED_RECORD.is_file():
        pytest.skip("the retained live record is absent from this checkout")
    return cc.load_calibration(cc.RETAINED_RECORD)


def test_record_comparison_accepts_equal_and_rejects_changed_records() -> None:
    record = {"a": [1.0, 2.0], "b": {"c": "x", "d": 3}}
    _expect(cc.differences(record, {"a": [1.0 + 1e-9, 2.0], "b": {"c": "x", "d": 3}}) == [], "equal within 1e-6")
    for changed in (
        {"a": [1.0, 2.1], "b": {"c": "x", "d": 3}},
        {"a": [1.0, 2.0], "b": {"c": "y", "d": 3}},
        {"a": [1.0], "b": {"c": "x", "d": 3}},
        {"a": [1.0, 2.0], "b": {"c": "x"}},
    ):
        _expect(len(cc.differences(record, changed)) == 1, f"{changed}: the change went unreported")


def test_calibration_reader_takes_five_regions_with_asymmetric_readout() -> None:
    cal = _calibration()
    _expect(len(cal.regions) == 5 and all(len(r) == 6 for r in cal.regions), "regions")
    qubits = [q for region in cal.regions for q in region]
    _expect(all(cal.t2[q] <= 2.0 * cal.t1[q] + 1e-18 for q in qubits), "T2 exceeds 2 T1 after the clamp")
    _expect(all(1e-5 < cal.t1[q] < 1e-3 for q in qubits), "T1 outside 10 us to 1 ms: units")
    _expect(all(cal.meas1_prep0[q] != cal.meas0_prep1[q] for q in qubits[:3]), "readout error is symmetric")
    _expect(cal.calibration.startswith("2026-11-06"), cal.calibration)


def test_relaxation_model_reproduces_the_closed_form_decay() -> None:
    """X on one qubit while another runs ten X gates: the ASAP schedule ends all wires together, so the excited qubit
    decays over ten gate durations and P(read 1) = exp(-10 duration / T1) with no other error source."""
    cal = _calibration()
    tile = cc.DisjointTile(0, cal.regions[0], [], [], 0.0, 0.0, 0.0, 0.0, 0.0)
    circuit = QuantumCircuit(6, 2)
    circuit.x(0)
    for _ in range(10):
        circuit.x(1)
    circuit.measure(0, 0)
    circuit.measure(1, 1)
    law = cc.model_laws(circuit, cal, tile, depolarizing=False, relaxation=True, readout="none")
    q0 = tile.qubits[0]
    want = math.exp(-10.0 * cal.x_duration[q0] / cal.t1[q0])
    got = float(law[1] + law[3])  # bit 0 reads 1
    _expect(abs(got - want) < 1e-6, f"P(1) {got} against {want}")
    ideal = cc.model_laws(circuit, cal, tile, depolarizing=False, relaxation=False, readout="none")
    _expect(abs(float(ideal[1] + ideal[3]) - 1.0) < 1e-12, "the noiseless model decays")
    _expect(bool(np.isclose(law.sum(), 1.0)), "the law is not normalized")
