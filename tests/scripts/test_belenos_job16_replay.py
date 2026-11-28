"""Belenos job-16 byte replay case: bytes, seeds by name, budgets and the offline plan."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
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


def test_the_offline_plan_digest_without_process_id_agrees_across_processes() -> None:
    pytest.importorskip("perceval")
    script = ROOT / "scripts/belenos_job16_replay.py"
    plans = [
        json.loads(
            subprocess.run(
                [sys.executable, str(script), "--offline-plan"],
                check=True,
                capture_output=True,
                text=True,
                env=dict(os.environ),
                cwd=ROOT,
            ).stdout
        )
        for _ in range(2)
    ]
    stripped = [plan["body_sha256_without_process_id"] for plan in plans]
    if stripped[0] != stripped[1]:
        raise AssertionError(stripped)
    if plans[0]["body_sha256"] == plans[1]["body_sha256"]:
        raise AssertionError("the raw body digest no longer varies with process_id; the stripped digest is unneeded")


def test_the_readings_order_compiler_changed_ahead_of_neither_and_the_exclusion_is_stated() -> None:
    readings = replay.preregistered()["readings"]
    if list(readings) != ["chip_or_server_changed", "case_property", "compiler_changed", "neither"]:
        raise AssertionError(list(readings))
    if "29dc6ef8" not in readings["compiler_changed"] or "14a96ca6" not in readings["compiler_changed"]:
        raise AssertionError(readings["compiler_changed"])
    void = replay.preregistered()["void"]
    if "excluded from the post-load count" not in void or "void seed-46667" not in void:
        raise AssertionError(void)
