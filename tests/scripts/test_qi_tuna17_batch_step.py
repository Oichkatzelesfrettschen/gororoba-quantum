"""Contract for scripts/qi_tuna17_batch_step.py: the anchor circuits of the characterization series and the committed
analysis record against the retained runs.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import qi_tuna17_batch_step as step

ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "results/quantum_inspire/characterization_tuna_17_batch_step_analysis.json"
RUNS = sorted((ROOT / "results/quantum_inspire/runs").glob("2026-11-16T0401Z-characterization_tuna_17-*"))


def test_half_width_is_none_at_an_open_end() -> None:
    if step.half_width([1.0, 3.0]) != 1.0 or step.half_width([None, 3.0]) is not None:
        raise AssertionError("half_width")


@pytest.mark.audit
def test_two_circuits_repeat_in_three_batches_each() -> None:
    groups = step.anchor_groups(RUNS)
    found = {step.prepared_state(group): [member["file"] for member in group["jobs"]] for group in groups}
    if found != {
        "one": ["readout-1.cq", "t1-0.cq", "readout-1.cq"],
        "zero": ["readout-0.cq", "x90-0.cq", "readout-0.cq"],
    }:
        raise AssertionError(found)
    for group in groups:
        times = [member["time_s"] for member in group["jobs"]]
        if times != sorted(times) or len({member["run"] for member in group["jobs"]}) != 3:
            raise AssertionError(group["sha256"])


@pytest.mark.audit
def test_committed_record_matches_its_registered_tallies() -> None:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    if record["schema"] != step.SCHEMA or len(record["qubits"]) != 17:
        raise AssertionError("record header")
    summary = record["summary"]
    rows = [row["models"]["single_amplitude_step"] for row in record["qubits"]]
    clear = sum(row["chi_square_per_dof"] <= step.LIMIT for row in rows)
    if summary["three_parameter_step"]["at_most_limit"] != clear or {row["freedom"] for row in rows} != {3}:
        raise AssertionError("the three-parameter tally differs from the per-qubit rows")
    for row in record["qubits"]:
        if row["anchor_prepared0"]["homogeneity"]["freedom"] != 2:
            raise AssertionError(row["qubit"])


@pytest.mark.audit
def test_retained_runs_reproduce_the_committed_rows_of_two_qubits() -> None:
    found = step.analyze(RUNS, qubits=[0, 14])
    committed = json.loads(RECORD.read_text(encoding="utf-8"))
    for row, qubit in zip(found["qubits"], (0, 14), strict=True):
        want = committed["qubits"][qubit]
        for name in ("single_step", "single_amplitude_step"):
            got, expected = row["models"][name]["params"], want["models"][name]["params"]
            if any(abs(got[key] - expected[key]) > 1e-6 * max(1.0, abs(expected[key])) for key in expected):
                raise AssertionError((qubit, name, got, expected))
        if abs(row["anchor_prepared0"]["shift"]["shift"] - want["anchor_prepared0"]["shift"]["shift"]) > 1e-12:
            raise AssertionError(qubit)
