"""The Ascella mesh-persistence case: retained bytes, verbatim replays, and the reading on synthetic runs."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import ascella_pathion_mesh_persistence as case  # noqa: E402
import ascella_pathion_mesh_persistence_analysis as reading  # noqa: E402

CASES = ROOT / "results/quandela/cases/ascella_pathion_mesh_persistence"
DRAW = ROOT / "docs/evidence/anu_qrng/draw-2026-11-07T162910Z.json"
ORIGINAL = ROOT / case.ORIGINAL_RUN


def check(condition: object, statement: str) -> None:
    if not condition:
        raise AssertionError(statement)


@pytest.mark.parametrize(("directory", "platform"), [("sim-00", "sim:ascella"), ("job-00", "qpu:ascella")])
def test_case_directories_rebuild_byte_for_byte(directory: str, platform: str) -> None:
    payload = case.documents(DRAW, "simulator" if platform.startswith("sim:") else "hardware", platform)
    for name, data in payload.items():
        check((CASES / directory / name).read_bytes() == data, "(CASES / directory / name).read_bytes() == data")


def test_replays_send_the_retained_requests_and_fresh_seeds_are_new() -> None:
    manifest = json.loads((CASES / "job-00" / "cases.json").read_bytes())
    retained = {s["name"]: s for s in json.loads((ORIGINAL / "cases.json").read_bytes())["settings"]}
    replays = [s for s in manifest["settings"] if s["kind"] == "replay"]
    check(len(replays) == 52, "len(replays) == 52")
    for setting in replays:
        before = retained[setting["original_name"]]
        check(
            setting["compilation_seed"] == before["compilation_seed"],
            'setting["compilation_seed"] == before["compilation_seed"]',
        )
        check(
            setting["circuit_params"] == before["circuit_params"],
            'setting["circuit_params"] == before["circuit_params"]',
        )
    old = {s["compilation_seed"] for s in retained.values()}
    fresh = {s["compilation_seed"] for s in manifest["settings"] if s["kind"] != "replay"}
    check(
        len(fresh) == case.FRESH_ANCHOR_SEEDS + len(case.FAILING) + 1,
        "len(fresh) == case.FRESH_ANCHOR_SEEDS + len(case.FAILING) + 1",
    )
    check(not fresh & old, "not fresh & old")
    check(len(manifest["settings"]) == case.ITERATIONS, 'len(manifest["settings"]) == case.ITERATIONS')
    check(
        manifest["expected_seconds"] <= case.BUDGET_FRACTION * case.MAX_DURATION,
        'manifest["expected_seconds"] <= case.BUDGET_FRACTION * case.MAX_DURATION',
    )


def synthetic_run(tmp_path: Path, perturb: bool = False) -> Path:
    """A run whose every iteration reuses the original job's entry for the same setting and orientation."""
    manifest = json.loads((CASES / "job-00" / "cases.json").read_bytes())
    original = json.loads((ORIGINAL / "results.json").read_bytes())["iterations"]
    settings = json.loads((ORIGINAL / "cases.json").read_bytes())["settings"]
    by_name = {s["name"]: e for s, e in zip(settings, original, strict=True)}
    by_design = {(s["setting"], s["orientation"]): e for s, e in zip(settings, original, strict=True)}
    entries = []
    for setting in manifest["settings"]:
        if setting["kind"] == "replay":
            entry = copy.deepcopy(by_name[setting["original_name"]])
        else:
            # The original job read its dark in orientation 0 only.
            key = (setting["setting"], setting["orientation"])
            entry = copy.deepcopy(by_design.get(key, by_design[(setting["setting"], 0)]))
        entry["iteration"]["compilation_seed"] = setting["compilation_seed"]
        entry["iteration"]["circuit_params"] = setting["circuit_params"]
        entries.append(entry)
    if perturb:
        replay = next(i for i, s in enumerate(manifest["settings"]) if s["kind"] == "replay")
        # The palindrome ends on the same anchor mesh it starts with, so take a sign setting's mesh instead.
        sign = next(i for i, s in enumerate(manifest["settings"]) if s["role"] == "sign")
        entries[replay]["result_fields"]["computed_circuit"] = entries[sign]["result_fields"]["computed_circuit"]
    run = tmp_path / "run"
    run.mkdir()
    (run / "cases.json").write_bytes((CASES / "job-00" / "cases.json").read_bytes())
    (run / "results.json").write_text(json.dumps({"iterations": entries}))
    return run


def test_mesh_gate_passes_identical_meshes_and_refuses_a_changed_one(tmp_path: Path) -> None:
    check(reading.mesh_gate(synthetic_run(tmp_path))["passed"], 'reading.mesh_gate(synthetic_run(tmp_path))["passed"]')
    other = tmp_path / "other"
    other.mkdir()
    check(
        not reading.mesh_gate(synthetic_run(other, perturb=True))["passed"],
        'not reading.mesh_gate(synthetic_run(other, perturb=True))["passed"]',
    )


def test_a_replay_of_the_original_counts_reads_fixed_per_mesh(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    run = synthetic_run(tmp_path)
    monkeypatch.setattr(reading, "ROOT", tmp_path)
    monkeypatch.setattr(case, "ORIGINAL_RUN", str(ORIGINAL))
    (tmp_path / "docs/evidence/anu_qrng").mkdir(parents=True)
    (tmp_path / "docs/evidence/anu_qrng" / DRAW.name).write_bytes(DRAW.read_bytes())
    (tmp_path / "docs/evidence/pathion-kernel-map/conjectures").mkdir(parents=True)
    maps = ROOT / "docs/evidence/pathion-kernel-map/conjectures/c1_static.npz"
    (tmp_path / "docs/evidence/pathion-kernel-map/conjectures/c1_static.npz").write_bytes(maps.read_bytes())
    report = reading.analyze(run)
    check(
        report["persistence_calibrated"]["r"] == pytest.approx(1.0),
        'report["persistence_calibrated"]["r"] == pytest.approx(1.0)',
    )
    check(
        report["persistence_calibrated"]["reading"] == "fixed per mesh",
        'report["persistence_calibrated"]["reading"] == "fixed per mesh"',
    )
    check(
        report["persistence_calibrated"]["replay_failing"] == 9,
        'report["persistence_calibrated"]["replay_failing"] == 9',
    )
    check(
        report["anchor_replay"]["ba"] == pytest.approx(case.ORIGINAL_BA, abs=1e-3),
        'report["anchor_replay"]["ba"] == pytest.approx(case.ORIGINAL_BA, abs=1e-3)',
    )
    check(report["correction"]["failing_after"] == 0, 'report["correction"]["failing_after"] == 0')
    check(set(report["frozen_maps"]) == {"gain", "offset"}, 'set(report["frozen_maps"]) == {"gain", "offset"}')


def test_plan_and_spec_check_run() -> None:
    out = subprocess.run(
        [sys.executable, str(ROOT / "scripts/ascella_pathion_mesh_persistence.py"), "--spec-check"],
        check=True,
        capture_output=True,
        text=True,
    )
    spec = json.loads(out.stdout)
    check(
        spec["worst_level_shift_from_g2_and_indistinguishability"] < 0.005,
        'spec["worst_level_shift_from_g2_and_indistinguishability"] < 0.005',
    )
    check(spec["dark_level_shift_bound"] < 0.005, 'spec["dark_level_shift_bound"] < 0.005')
