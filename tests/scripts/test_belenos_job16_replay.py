"""Belenos job-16 byte replay case: bytes, seeds by name, budgets and the offline plan."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import belenos_job16_replay as replay
import belenos_offcone_mechanisms_analyze as analysis
import pytest
import qd_belenos_mesh as mesh

ROOT = Path(__file__).resolve().parents[2]
CASE = ROOT / "results/quandela/cases/belenos_job16_replay/job-00"


def test_the_retained_case_equals_the_builders_bytes() -> None:
    for name, data in replay.documents().items():
        if (CASE.parent / name).read_bytes() != data:
            raise AssertionError(name)


def test_the_circuit_is_job_16s_byte_for_byte() -> None:
    circuit = (CASE / "circuit.json").read_bytes()
    if (
        hashlib.sha256(circuit).hexdigest() != replay.CIRCUIT_SHA256
        or circuit != (replay.SOURCE / "circuit.json").read_bytes()
    ):
        raise AssertionError("circuit.json differs from belenos_mesh/job-16")


def test_the_settings_alternate_the_two_retained_seeds_by_name() -> None:
    manifest = json.loads((CASE / "cases.json").read_text(encoding="utf-8"))
    seeds = [s["compilation_seed"] for s in manifest["settings"]]
    if seeds != [mesh.DWELL_Q1_SEED, replay.SEED_REFERENCE["value"]] * 5 or set(seeds) != {20, 46667}:
        raise AssertionError(seeds)
    if any(set(s) != {"name", "compilation_seed"} for s in manifest["settings"]) or "mitigations" in manifest:
        raise AssertionError("an entry overrides the input mode or the mitigations")


def test_the_budgets_follow_the_builder_rules() -> None:
    manifest = json.loads((CASE / "cases.json").read_text(encoding="utf-8"))
    if (manifest["iterations"], manifest["max_samples"], manifest["max_shots"]) != (10, 100000, 200000):
        raise AssertionError(manifest)
    if (
        manifest["expected_seconds"] != 81.16
        or manifest["max_credits"] != 1.02
        or manifest["platforms"] != ["qpu:belenos"]
    ):
        raise AssertionError(manifest)


def test_the_envelope_is_the_analyzers_job_16_baseline() -> None:
    base = analysis.baseline()
    if (base["in_block_cone"]["min"], base["tvd_cone_from_ideal"]["max"]) != (
        replay.ENVELOPE["in_block_cone_min"],
        replay.ENVELOPE["tvd_cone_from_ideal_max"],
    ):
        raise AssertionError(base)


def test_the_offline_plan_prices_the_case_without_a_provider_read() -> None:
    pytest.importorskip("perceval")
    planned = replay.offline_plan()
    if (planned["estimated_shots"], planned["credit_ceiling"], planned["expected_seconds"]) != (100000, 1.02, 81.16):
        raise AssertionError(planned)
