"""A packing witness proves connected, disjoint patches, rather than device independence."""

from __future__ import annotations

import importlib
from typing import Any

import pytest


def packing() -> Any:
    try:
        return importlib.import_module("provider_patch_packing")
    except ModuleNotFoundError:
        pytest.fail("the source-bound packing witness producer is absent")


def test_path_graph_packing_attains_the_dimension_bound() -> None:
    result = packing().pack("path", list(range(8)), [(n, n + 1) for n in range(7)], 8)
    patches = result["patches"]
    if result["dimension_upper_bound"] != 2 or len(patches) != 2 or not result["attains_dimension_bound"]:
        raise AssertionError("a connected eight-vertex path lost its two four-qubit patches")
    used = [qubit for patch in patches for qubit in patch["qubits"]]
    if len(set(used)) != 8:
        raise AssertionError("patches overlap")
    for patch in patches:
        if len(patch["roles"]) != 4 or len(patch["preparation_edges"]) != 2:
            raise AssertionError("the patch lacks a three-qubit GHZ tree and a sector qubit")


def test_report_withholds_optimality_when_witness_misses_bound() -> None:
    result = packing().pack("disconnected", list(range(4)), [(0, 1), (1, 2)], 4)
    if result["patches"] or result["attains_dimension_bound"]:
        raise AssertionError("a missing connected four-qubit witness became a packing proof")


def test_replay_search_attains_the_frozen_iqm_patch_bounds() -> None:
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[2] / "docs/evidence/provider-api-audit"
    result = json.loads((root / "packing.json").read_text())
    packing().validate(root, result)
    rows = {row["backend"]: row for row in result["rows"]}
    if len(rows["iqm:garnet"]["patches"]) != 5 or len(rows["iqm:emerald"]["patches"]) != 13:
        raise AssertionError("the frozen IQM graphs did not reach their witnessed dimension bounds")


def test_witness_validation_rejects_overlapping_patches() -> None:
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[2] / "docs/evidence/provider-api-audit"
    result = json.loads((root / "packing.json").read_text())
    result["rows"][0]["patches"][1] = result["rows"][0]["patches"][0]
    with pytest.raises(ValueError, match="overlap"):
        packing().validate(root, result)
