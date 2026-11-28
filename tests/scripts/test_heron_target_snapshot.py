"""Offline tests of the Target snapshot's summary, coupling and health computations."""

from __future__ import annotations

import json
from pathlib import Path

import heron_target_snapshot as hts
import pytest


def require(condition: bool) -> None:
    if not condition:
        raise AssertionError


def toy_backend() -> dict[str, object]:
    """Five qubits on a path 0-1-2-3-4: qubit 2 dead, coupler 3-4 dead."""
    n = 5
    pairs = [(0, 1), (1, 2), (2, 3), (3, 4)]
    cz_error = {(0, 1): 0.002, (1, 2): 0.003, (2, 3): 0.002, (3, 4): 1.0}
    qargs = [list(p) for p in pairs] + [list(reversed(p)) for p in pairs]
    errors = [cz_error[(min(q), max(q))] for q in qargs]
    one = [[q] for q in range(n)]
    sx = [0.0003, 0.0003, 1.0, 0.0003, 0.0003]
    return {
        "num_qubits": n,
        "faulty_qubits": [],
        "faulty_gates": [],
        "calibration_values": {"t1": [1e-4] * n, "t2": [8e-5, 8e-5, None, 8e-5, 8e-5]},
        "instructions": {
            "sx": {"qargs": one, "duration": [3.2e-8] * n, "error": sx},
            "measure": {"qargs": one, "duration": [2e-6] * n, "error": [0.01] * n},
            "measure_2": {"qargs": one, "duration": [1e-6] * n, "error": [0.02] * n},
            "cz": {"qargs": qargs, "duration": [6.8e-8] * len(qargs), "error": errors},
        },
    }


def test_stats_order_statistics() -> None:
    s = hts.stats([4.0, 1.0, 3.0, 2.0])
    require((s["min"], s["median"], s["max"], s["n"]) == (1.0, 2.5, 4.0, 4.0))


def test_coupling_counts_undirected_edges_and_flags_high_error() -> None:
    b = toy_backend()
    c = hts.coupling(b["instructions"]["cz"])  # type: ignore[index]
    require(len(c["edges"]) == 4)
    require(c["degree_histogram"] == {"1": 2, "2": 3})
    require([h["pair"] for h in c["high_error_couplers"]] == [[3, 4]])


def test_health_finds_dead_qubit_coupler_and_components() -> None:
    h = hts.health(toy_backend())
    require(h["dead_qubits"] == [2])
    require(h["dead_couplers"] == [[3, 4]])
    require(h["healthy_qubits"] == 4)
    require(h["component_sizes"] == [2, 1, 1])
    require(h["largest_cz_error_below_sentinel"] == 0.003)


def test_health_counts_a_high_but_finite_error_as_alive() -> None:
    b = toy_backend()
    b["instructions"]["sx"]["error"][0] = 0.9  # type: ignore[index]
    require(hts.health(b)["dead_qubits"] == [2])


def test_health_adds_the_vendor_faulty_lists() -> None:
    b = toy_backend()
    b["faulty_qubits"] = [0]
    b["faulty_gates"] = [["cz", [1, 2]]]
    h = hts.health(b)
    require(h["dead_qubits"] == [0, 2])
    require(h["dead_couplers"] == [[1, 2], [3, 4]])


def snapshot_file(tmp_path: Path, backend: dict[str, object]) -> Path:
    backend["summary"] = hts.summarize(backend)
    backend["health"] = hts.health(backend)
    backend["coupling"] = hts.coupling(backend["instructions"]["cz"])  # type: ignore[index]
    backend["calibration_values"]["frequency_hz"] = [5e9] * 5  # type: ignore[index]
    path = tmp_path / "caps.json"
    path.write_text(json.dumps({"backends": {name: backend for name in hts.ROSTER}}), encoding="utf-8")
    return path


def test_check_calibration_accepts_a_consistent_backend(tmp_path: Path) -> None:
    b = toy_backend()
    snapshot_file(tmp_path, b)
    hts.check_calibration("toy", b)


def test_check_calibration_rejects_a_tampered_summary(tmp_path: Path) -> None:
    b = toy_backend()
    snapshot_file(tmp_path, b)
    b["summary"]["t1_us"]["median"] = 1.0  # type: ignore[index]
    with pytest.raises(RuntimeError):
        hts.check_calibration("toy", b)


def test_check_calibration_rejects_an_error_inside_the_sentinel_gap(tmp_path: Path) -> None:
    b = toy_backend()
    b["instructions"]["cz"]["error"][0] = b["instructions"]["cz"]["error"][4] = 0.7  # type: ignore[index]
    snapshot_file(tmp_path, b)
    with pytest.raises(RuntimeError, match="sentinel"):
        hts.check_calibration("toy", b)
