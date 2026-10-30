"""Permutation and compilation assignments retain the pilot's mathematical operators."""

from __future__ import annotations

import importlib
import json
from collections import Counter
from typing import Any

import numpy as np
import pytest


def module() -> Any:
    return importlib.import_module("ascella_transition_interventions")


def test_output_permutation_moves_rows_and_preserves_a_unitary() -> None:
    intervention = module()
    source = np.eye(12, dtype=np.complex128)
    permutation = intervention.PORT_MAPS["logical-swap"]
    mapped = intervention.permute_operator(source, permutation)
    if not np.array_equal(mapped[permutation, :], source):
        raise AssertionError("each logical output must land on its named physical port")
    if not np.allclose(mapped.conj().T @ mapped, source, atol=1e-12, rtol=0):
        raise AssertionError("a physical-port permutation must preserve the full unitary")


def test_random_values_are_unique_and_balanced_across_every_condition() -> None:
    intervention = module()
    assignments = intervention.assignments(list(range(100, 400)), {101, 102})
    if len(assignments) != 120 or len({row["draw_index"] for row in assignments}) != 120:
        raise AssertionError("every independent compilation must consume a distinct draw position")
    if len({row["value"] for row in assignments}) != 120:
        raise AssertionError("independent compilation identifiers must be distinct")
    counts = Counter((row["label"], row["port_map"]) for row in assignments)
    if len(counts) != 15 or set(counts.values()) != {8}:
        raise AssertionError("every setting and port map needs eight independent compilations")
    if any(row["value"] in {101, 102} for row in assignments):
        raise AssertionError("fresh compilation identifiers must exclude the retained base meshes")


def test_random_allocation_refuses_an_exhausted_draw() -> None:
    intervention = module()
    with pytest.raises(ValueError, match="distinct"):
        intervention.assignments([100] * 256, set())


def test_group_interval_averages_simultaneous_bounds_without_pooling_meshes() -> None:
    intervention = module()
    if not np.allclose(intervention.average_interval([[0.1, 0.3], [0.4, 0.6]]), [0.25, 0.45]):
        raise AssertionError("the group interval must average individual simultaneous limits")
    with pytest.raises(ValueError):
        intervention.average_interval([])


def test_intervention_metadata_preserves_a_decoded_result() -> None:
    intervention = module()
    setting = {
        "diagnostic_label": "identity-2",
        "port_map": "original",
        "physical_port_permutation": list(range(12)),
        "compilation_kind": "matched-mesh-anchor",
        "requested_probabilities": [0.0, 0.0, 1.0] + [0.0] * 9,
    }
    decoded = {"counts": [0, 0, 10] + [0] * 10, "leakage": 0, "mesh": ["circuit", "input"]}
    result = intervention._measure(setting, decoded)
    if result["target_port"] != 2 or result["counts"] != decoded["counts"] or "target_port" in decoded:
        raise AssertionError("metadata annotation must preserve the independently decoded result")


@pytest.mark.audit
def test_full_cases_bind_every_draw_index_operator_and_anchor() -> None:
    intervention = module()
    files = intervention.build_files()
    campaign = json.loads(files["campaign.json"])
    allocated = json.loads(files["seed-allocation.json"])["allocations"]
    draw = json.loads((intervention.ROOT / intervention.DRAW).read_bytes())["values"]
    source = json.loads((intervention.ROOT / intervention.context.SOURCE).read_bytes())
    originals = {row["name"]: row for row in source["settings"]}
    label_to_name = dict(intervention.context.SELECTION)
    actual_indices = []
    if len(campaign["jobs"]) != 6 or campaign["endpoints"] != 1876:
        raise AssertionError("six cases must retain the complete confidence family")
    for job in campaign["jobs"]:
        manifest = json.loads(files[job["manifest"]])
        if len(manifest["settings"]) != 22:
            raise AssertionError("each job must carry twenty new meshes and two anchors")
        for row in manifest["settings"]:
            original = originals[label_to_name[row["diagnostic_label"]]]
            if row["compilation_kind"] == "matched-mesh-anchor":
                if row["compilation_seed"] != original["compilation_seed"]:
                    raise AssertionError("an anchor must reproduce its original seed identity")
                continue
            index = row["compilation_seed_allocation"]["draw_index"]
            actual_indices.append(index)
            if draw[index] != row["compilation_seed"]:
                raise AssertionError("a compilation identifier differs from its draw position")
            old = np.asarray(original["operator"]["real"]) + 1j * np.asarray(original["operator"]["imaginary"])
            current = np.asarray(row["operator"]["real"]) + 1j * np.asarray(row["operator"]["imaginary"])
            if not np.array_equal(current[row["physical_port_permutation"], :], old):
                raise AssertionError("the full operator does not implement the recorded output permutation")
    if len(actual_indices) != 120 or len(set(actual_indices)) != 120:
        raise AssertionError("the complete intervention must use each fresh draw position once")
    if set(actual_indices) != {row["draw_index"] for row in allocated}:
        raise AssertionError("the manifests differ from the recorded seed allocation")
