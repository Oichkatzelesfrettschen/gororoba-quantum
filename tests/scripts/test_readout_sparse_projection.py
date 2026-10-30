"""Validate sparse projections from aligned PUB register shot strings."""

import hashlib
import tracemalloc
from copy import deepcopy

import pytest
import readout_sparse_projection as projection


def fixture() -> tuple[dict, dict]:
    raw = {
        "pub_name": "actor-active",
        "pub_index": 3,
        "registers": {
            "a": {"num_bits": 2, "num_shots": 4, "bitstrings": ["01", "10", "11", "00"]},
            "b": {"num_bits": 1, "num_shots": 4, "bitstrings": ["0", "1", "0", "1"]},
        },
    }
    manifest = {
        "schema": "readout-sparse-projection-v1",
        "condition": "actor-active-input-10",
        "pub_name": "actor-active",
        "pub_index": 3,
        "registers": {"a": 2, "b": 1},
        "bits": [
            {"register": "a", "index": 0, "logical": 0, "physical": 7, "prepared": 1},
            {"register": "a", "index": 1, "logical": 1, "physical": 8, "prepared": 0},
            {"register": "b", "index": 0, "logical": 2, "physical": 9, "prepared": 0},
        ],
        "pairs": [[0, 2]],
        "groups": [[0, 1, 2]],
    }
    return raw, manifest


def test_cross_register_pair_and_group_use_same_shot_indices() -> None:
    raw, manifest = fixture()
    original = deepcopy(raw)
    result = projection.project_pub(raw, manifest)
    if result["pair_counts"] != [{"logical_bits": [0, 2], "error_cells_00_01_10_11": [2, 0, 0, 2]}]:
        raise AssertionError("cross-register pairs must use the same shot index and commanded preparation")
    if result["group_counts"] != [{"logical_bits": [0, 1, 2], "error_parity_even_odd": [2, 2]}]:
        raise AssertionError("the declared group parity must use all three aligned errors")
    if result["num_shots"] != 4 or result["condition"] != manifest["condition"] or raw != original:
        raise AssertionError("the projection must retain the declared condition and leave raw data unchanged")
    if result["register_bitstrings_sha256"]["b"] != hashlib.sha256(b"0101").hexdigest():
        raise AssertionError("the register digest must bind the ordered shot strings")


def test_all_three_bit_outcomes_match_direct_reference() -> None:
    raw, manifest = fixture()
    outcomes = [(first, second, third) for first in (0, 1) for second in (0, 1) for third in (0, 1)]
    raw["registers"]["a"] = {
        "num_bits": 2,
        "num_shots": len(outcomes),
        "bitstrings": [f"{second}{first}" for first, second, _third in outcomes],
    }
    raw["registers"]["b"] = {
        "num_bits": 1,
        "num_shots": len(outcomes),
        "bitstrings": [str(third) for _first, _second, third in outcomes],
    }
    result = projection.project_pub(raw, manifest)
    if result["pair_counts"][0]["error_cells_00_01_10_11"] != [2, 2, 2, 2]:
        raise AssertionError("the projected table must agree with the exhaustive three-bit reference")
    if result["group_counts"][0]["error_parity_even_odd"] != [4, 4]:
        raise AssertionError("the projected parity must agree with the exhaustive three-bit reference")


def test_result_does_not_alias_mutable_manifest_projections() -> None:
    raw, manifest = fixture()
    result = projection.project_pub(raw, manifest)
    manifest["pairs"][0][0] = 1
    manifest["groups"][0][0] = 2
    if result["pair_counts"][0]["logical_bits"] != [0, 2]:
        raise AssertionError("the result's pair must remain bound to the manifest digest")
    if result["group_counts"][0]["logical_bits"] != [0, 1, 2]:
        raise AssertionError("the result's group must remain bound to the manifest digest")


def test_projection_rejects_excessive_aggregate_work(monkeypatch: pytest.MonkeyPatch) -> None:
    raw, manifest = fixture()
    monkeypatch.setattr(projection, "MAX_WORK_UNITS", 31)
    with pytest.raises(ValueError, match="work"):
        projection.project_pub(raw, manifest)


@pytest.mark.parametrize("mutation", ["short", "missing", "duplicate", "bad_bit", "wrong_pub", "missing_map"])
def test_malformed_or_unbound_inputs_are_rejected(mutation: str) -> None:
    raw, manifest = fixture()
    if mutation == "short":
        raw["registers"]["b"]["bitstrings"].pop()
    elif mutation == "missing":
        del raw["registers"]["b"]
    elif mutation == "duplicate":
        manifest["bits"][1]["physical"] = 7
    elif mutation == "bad_bit":
        raw["registers"]["a"]["bitstrings"][2] = "x1"
    elif mutation == "wrong_pub":
        raw["pub_name"] = "other"
    else:
        manifest["bits"].pop()
    with pytest.raises(ValueError):
        projection.project_pub(raw, manifest)


def test_sparse_projection_memory_for_156_bits_and_40000_shots() -> None:
    width, shots = 156, 40000
    raw = {
        "pub_name": "wide",
        "pub_index": 0,
        "registers": {"c": {"num_bits": width, "num_shots": shots, "bitstrings": ["0" * width] * shots}},
    }
    manifest = {
        "schema": "readout-sparse-projection-v1",
        "condition": "wide-ground",
        "pub_name": "wide",
        "pub_index": 0,
        "registers": {"c": width},
        "bits": [
            {"register": "c", "index": bit, "logical": bit, "physical": bit, "prepared": 0} for bit in range(width)
        ],
        "pairs": [[0, 155]],
        "groups": [[0, 1, 155]],
    }
    tracemalloc.start()
    try:
        result = projection.project_pub(raw, manifest)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    if result["pair_counts"][0]["error_cells_00_01_10_11"] != [shots, 0, 0, 0]:
        raise AssertionError("the wide zero record must project to a zero error table")
    if peak >= 16 * 1024 * 1024:
        raise AssertionError(f"projection allocated {peak} traced bytes for a fixed-size batch")
