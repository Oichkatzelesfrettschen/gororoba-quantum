"""Bounded fixtures for the long-horizon seed-repeat reading: the ceiling and the power replicate."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ascella_long_horizon_reading as long_horizon  # noqa: E402
import ascella_seed_repeat_reading as seed_repeat  # noqa: E402


def test_the_ceiling_at_job_02_and_job_03_samples_equals_the_seed_repeat_bound() -> None:
    """At 8,192 and 16,384 samples the generalized ceiling is the seed-repeat reading's halved-variance ceiling."""
    general = long_horizon.ceiling(8192, 16384, 56)
    fixed = seed_repeat.fixed_bound(56)
    if general["ceiling"] != pytest.approx(fixed["ceiling"], rel=1e-12):
        raise AssertionError(f"{general} differs from {fixed}")
    if general["bound"] != pytest.approx(fixed["bound"], rel=1e-12):
        raise AssertionError(f"{general} differs from {fixed}")


def test_a_power_replicate_depends_only_on_its_seed() -> None:
    """Two calls on one spawned seed read the same outcome; a fully persistent error reads persists."""
    value = json.loads((ROOT / long_horizon.LONG_REPEAT_ORDER_DRAW).read_text(encoding="utf-8"))["values"]
    seed = np.random.SeedSequence(int(value[long_horizon.POWER_INDEX])).spawn(1)[0]
    first = long_horizon.power_replicate((1.0, seed))
    if first != long_horizon.power_replicate((1.0, seed)) or first != "persists":
        raise AssertionError(f"replicate read {first}")


@pytest.mark.audit
def test_mesh_identity_reads_unitaries_not_serialized_strings() -> None:
    """The sim:ascella replay of job-02 serves job-02's QPU meshes: every unitary lies within MESH_TOLERANCE, while no
    serialized string is byte-equal."""
    runs = ROOT / "results/quandela/runs"
    texts = [
        [
            row["result_fields"]["computed_circuit"]
            for row in json.loads((runs / run / "results.json").read_text())["iterations"]
        ]
        for run in (
            "2026-10-25T184636Z-qpu_ascella-ascella_signed_coherence-job-02",
            "2026-11-06T175319Z-sim_ascella-ascella_signed_coherence-job-02-sim-replay",
        )
    ]
    pairs = list(zip(*texts, strict=True))
    distances = [long_horizon.mesh_distance(pair) for pair in pairs]
    if sum(left == right for left, right in pairs) != 0 or max(distances) > long_horizon.MESH_TOLERANCE:
        raise AssertionError(f"largest distance {max(distances)}")


def test_mesh_distance_admits_float_jitter_and_refuses_a_moved_phase() -> None:
    """A serialized mesh re-serialized with one phase nudged by 1e-9 differs as a string but reads as the same mesh;
    a phase moved by 1e-3 reads as another mesh."""
    from perceval import BS, PS, Circuit
    from perceval.serialization import serialize

    def mesh(phase: float) -> str:
        return str(serialize(Circuit(2) // BS.Rx(theta=1.4535) // (1, PS(phase)) // BS.Rx(theta=1.4467)))

    base, jitter, moved = mesh(0.7), mesh(0.7 + 1e-9), mesh(0.7 + 1e-3)
    if base == jitter:
        raise AssertionError("a 1e-9 phase change left the serialized string unchanged")
    if long_horizon.mesh_distance((base, base)) != 0.0:
        raise AssertionError("equal strings must read distance zero")
    if long_horizon.mesh_distance((base, jitter)) > long_horizon.MESH_TOLERANCE:
        raise AssertionError("float jitter read as another mesh")
    if long_horizon.mesh_distance((base, moved)) <= long_horizon.MESH_TOLERANCE:
        raise AssertionError("a moved phase read as the same mesh")
