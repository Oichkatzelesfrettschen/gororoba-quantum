"""Contract for scripts/qi_tuna17_t1_shape.py: the catalogue's coupling map, the wait-line and execution-time readers,
and the committed analysis record against the retained runs of the characterization series.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import qi_tuna17_t1_shape as shape

ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "results/quantum_inspire/characterization_tuna_17_t1_shape_analysis.json"
RUNS = sorted((ROOT / "results/quantum_inspire/runs").glob("2026-11-16T0401Z-characterization_tuna_17-*"))


@pytest.mark.audit
def test_coupling_map_is_the_24_edge_ninja_star() -> None:
    edges = shape.coupling_edges(shape.CATALOGUE)
    degree = [sum(q in edge for edge in edges) for q in range(17)]
    if len(edges) != 24 or sum(degree) != 48 or max(degree) != 4:
        raise AssertionError((len(edges), degree))


def test_execution_slope_reads_the_delay_dependence_of_job_time() -> None:
    cycles = [0, 250, 500, 1000, 2000, 4000]
    rows = [{"cycles": n, "execution_s": 7.0 + n * 20e-9 * 8192, "shots": 8192} for n in cycles]
    found = shape.execution_slope(rows)
    if abs(found["slope_ns_per_cycle_per_shot"] - 20.0) > 1e-6 or found["slope_se_ns"] > 1e-6:
        raise AssertionError(found)


def test_tally_counts_the_qubits_at_the_decision_limit() -> None:
    found = shape.tally([1.0, 3.0, 3.1, None, 50.0])
    if found["qubits"] != 4 or found["at_most_limit"] != 2 or found["maximum"] != 50.0:
        raise AssertionError(found)


@pytest.mark.audit
def test_committed_record_matches_its_decision_rules() -> None:
    record = json.loads(RECORD.read_text(encoding="utf-8"))
    if (
        record["schema"] != shape.SCHEMA
        or len(record["qubits"]) != 17
        or record["delays_cycles"] != [0, 250, 500, 1000, 2000, 4000]
    ):
        raise AssertionError("record header")
    summary = record["summary"]
    passes = sum(
        row["models"]["single"]["chi_square_per_dof"] <= shape.CHI_SQUARE_PER_DOF_LIMIT for row in record["qubits"]
    )
    if summary["h1_readout"]["mean"]["at_most_limit"] != passes:
        raise AssertionError("the H1 tally differs from the per-qubit rows")
    for row in record["qubits"]:
        for name, fit in row["models"].items():
            if fit["freedom"] <= 0 or not fit["deviance"] >= 0.0:
                raise AssertionError((row["qubit"], name))
        low, high = row["models"]["single"]["interval_scaled"]["T_us"]
        if low is None or high is None or not low < row["models"]["single"]["params"]["T_us"] < high:
            raise AssertionError(row["qubit"])


@pytest.mark.audit
def test_retained_runs_reproduce_the_committed_rows_of_two_qubits() -> None:
    retained = json.loads(
        (ROOT / "results/quantum_inspire/characterization_tuna_17_analysis.json").read_text(encoding="utf-8")
    )
    found = shape.analyze(RUNS, retained, shape.coupling_edges(shape.CATALOGUE), qubits=[3, 8])
    committed = json.loads(RECORD.read_text(encoding="utf-8"))
    for row, qubit in zip(found["qubits"], (3, 8), strict=True):
        want = committed["qubits"][qubit]["models"]["single"]["params"]["T_us"]
        if abs(row["models"]["single"]["params"]["T_us"] - want) > 1e-6 * want:
            raise AssertionError((qubit, row["models"]["single"]["params"], want))


@pytest.mark.audit
def test_a_null_standard_error_stays_null_through_the_mechanism_rows() -> None:
    retained = json.loads(
        (ROOT / "results/quantum_inspire/characterization_tuna_17_analysis.json").read_text(encoding="utf-8")
    )
    for row in retained["qubits"]:
        if row["qubit"] == 3:
            row["t1"]["us_se"] = None
    found = shape.analyze(RUNS, retained, shape.coupling_edges(shape.CATALOGUE), qubits=[3, 8])
    null_row, kept_row = found["standard_error_rows"]
    if null_row["qubit"] != 3 or any(
        null_row[key] is not None for key in ("retained_se_us", "scaled_se_us", "spread_over_scaled_se")
    ):
        raise AssertionError(null_row)
    if kept_row["scaled_se_us"] is None or kept_row["spread_over_scaled_se"] is None:
        raise AssertionError(kept_row)
    summary = found["summary"]["standard_error"]
    if summary["qubits"] != 2 or summary["scaled_se_us"]["minimum"] != kept_row["scaled_se_us"]:
        raise AssertionError(summary)
