"""The Ascella mesh-persistence case: retained bytes, verbatim replays, and the reading on synthetic runs."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import numpy as np
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


RUNS = {
    "sim-00": ROOT / "results/quandela/runs/2026-11-07T181127Z-sim_ascella-ascella_pathion_mesh_persistence-sim-00",
    "job-00": ROOT / "results/quandela/runs/2026-11-07T182838Z-qpu_ascella-ascella_pathion_mesh_persistence-job-00",
}


@pytest.mark.parametrize("directory", ["sim-00", "job-00"])
def test_the_submitted_cases_keep_their_bytes(directory: str) -> None:
    import hashlib

    submitted = json.loads((RUNS[directory] / "submission-state.json").read_bytes())
    for data in ((CASES / directory / "cases.json").read_bytes(), (RUNS[directory] / "cases.json").read_bytes()):
        check(submitted["cases_sha256"] == hashlib.sha256(data).hexdigest(), f"{directory} is the submitted request")


def test_replays_send_the_retained_requests_and_fresh_seeds_are_new() -> None:
    manifest = json.loads((CASES / "job-00" / "cases.json").read_bytes())
    retained = {s["name"]: s for s in json.loads((ORIGINAL / "cases.json").read_bytes())["settings"]}
    replays = [s for s in manifest["settings"] if s["kind"] == "replay"]
    check(len(replays) == 52, "52 replay settings")
    for setting in replays:
        before = retained[setting["original_name"]]
        check(setting["compilation_seed"] == before["compilation_seed"], f"{setting['name']} seed")
        check(setting["circuit_params"] == before["circuit_params"], f"{setting['name']} circuit parameters")
    old = {s["compilation_seed"] for s in retained.values()}
    fresh = {s["compilation_seed"] for s in manifest["settings"] if s["kind"] != "replay"}
    check(len(fresh) == case.FRESH_ANCHOR_SEEDS + len(case.FAILING) + 1, "one fresh seed per fresh design")
    check(not fresh & old, "fresh seeds are unused by the original job")
    check(len(manifest["settings"]) == case.ITERATIONS, "iteration count")
    check(manifest["expected_seconds"] <= case.BUDGET_FRACTION * case.MAX_DURATION, "packing margin")


def test_the_persistence_cutoff_is_the_frozen_plans() -> None:
    record = json.loads((ROOT / case.PERSISTENCE_PLAN).read_bytes())
    check(record["persistence_cutoff"] == case.PERSISTENCE_CUTOFF, "cutoff equals the frozen plan")
    check(
        record["persistence_cutoff_without_platform_differing"] == case.PERSISTENCE_CUTOFF_REDUCED,
        "reduced cutoff equals the frozen plan",
    )
    check(case.PREREGISTERED["persistence_cutoff"] == case.PERSISTENCE_CUTOFF, "manifest carries the cutoff")
    power = reading.aligned_power()
    check(power["design_reads_follows_mesh"] < 0.02 and power["mesh_reads_follows_design"] < 0.02, "aligned errors")


@pytest.mark.audit
def test_the_persistence_plan_rebuilds() -> None:
    record = json.loads((ROOT / case.PERSISTENCE_PLAN).read_bytes())
    check(reading.persistence_plan() == record, "persistence_plan.json rebuilds from its draw")


def synthetic_run(tmp_path: Path, directory: str = "job-00", mutate: str = "") -> Path:
    """A run whose every iteration reuses the original job's entry for the same setting and orientation."""
    manifest = json.loads((CASES / directory / "cases.json").read_bytes())
    # A synthetic simulator run reuses the original simulator run's entries, a QPU run the original QPU job's.
    source = ROOT / case.ORIGINAL_SIM_RUN if directory == "sim-00" else ORIGINAL
    original = json.loads((source / "results.json").read_bytes())["iterations"]
    settings = json.loads((source / "cases.json").read_bytes())["settings"]
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
    data = (CASES / directory / "cases.json").read_bytes()
    if mutate == "mesh":
        replay = next(i for i, s in enumerate(manifest["settings"]) if s["kind"] == "replay")
        # The palindrome ends on the same anchor mesh it starts with, so take a sign setting's mesh instead.
        sign = next(i for i, s in enumerate(manifest["settings"]) if s["role"] == "sign")
        entries[replay]["result_fields"]["computed_circuit"] = entries[sign]["result_fields"]["computed_circuit"]
    elif mutate == "platform":
        # The QPU serves a-h-CC o1 a different mesh, as the original QPU job did against the simulator.
        target = next(i for i, s in enumerate(manifest["settings"]) if s.get("original_name") == "a-h-CC-o1-i20")
        sign = next(i for i, s in enumerate(manifest["settings"]) if s["role"] == "sign" and i != target)
        entries[target]["result_fields"]["computed_circuit"] = entries[sign]["result_fields"]["computed_circuit"]
    elif mutate == "missing":
        entries = entries[:-1]
    elif mutate == "duplicate":
        replays = [s for s in manifest["settings"] if s["kind"] == "replay"]
        replays[1]["original_name"] = replays[0]["original_name"]
        data = (json.dumps(manifest, indent=1) + "\n").encode()
    run = tmp_path / "run"
    run.mkdir()
    (run / "cases.json").write_bytes(data)
    (run / "results.json").write_text(json.dumps({"iterations": entries}))
    return run


@pytest.mark.parametrize("mutate", ["", "mesh", "missing", "duplicate"])
def test_mesh_gate_refuses_a_changed_missing_or_duplicated_replay(tmp_path: Path, mutate: str) -> None:
    gate = reading.mesh_gate(synthetic_run(tmp_path, "sim-00", mutate))
    check(gate["passed"] == (mutate == ""), f"mesh gate with mutation {mutate!r}: {gate['problems'] or gate['misses']}")
    if mutate == "":
        check(gate["replay_compared"] == 52, "52 replay meshes compared")


def test_the_qpu_manifest_fails_the_simulator_gate(tmp_path: Path) -> None:
    gate = reading.mesh_gate(synthetic_run(tmp_path, "job-00"))
    check(not gate["passed"] and gate["problems"], "a manifest other than the frozen sim-00 case is refused")


def test_constant_or_non_finite_inputs_are_not_read() -> None:
    check(reading.finite_r(np.ones(9), np.arange(9.0)) is None, "constant input")
    check(reading.finite_r(np.array([0.1, np.nan, 0.3]), np.arange(3.0)) is None, "non-finite input")
    check(reading.finite_r(np.arange(9.0), np.arange(9.0)) == pytest.approx(1.0), "finite input reads")


def test_a_replay_of_the_original_counts_reads_fixed_per_mesh(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    run = synthetic_run(tmp_path)
    monkeypatch.setattr(reading, "ROOT", tmp_path)
    monkeypatch.setattr(case, "ORIGINAL_RUN", str(ORIGINAL))
    for relative in (
        DRAW.relative_to(ROOT),
        Path("docs/evidence/pathion-kernel-map/conjectures/c1_static.npz"),
        (CASES / "job-00" / "cases.json").relative_to(ROOT),
    ):
        (tmp_path / relative).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / relative).write_bytes((ROOT / relative).read_bytes())
    report = reading.analyze(run)
    persistence = report["persistence"]
    check(persistence["r"] == pytest.approx(1.0), "replay r")
    check(persistence["reading"] == "fixed per mesh", "persistence reading")
    check(persistence["replay_failing"] == 9, "nine replay failures")
    check(report["anchor_replay"]["ba"] == pytest.approx(case.ORIGINAL_BA, abs=1e-3), "replayed B/A")
    check(report["correction"]["failing_after"] == 0, "correction")
    # The synthetic fresh items copy the original meshes' counts, so their error follows the design by construction.
    check(report["fresh_failing"]["reading"] == "follows the design", "fresh failing reading")
    check(report["fresh_failing"]["carried_fraction"] == pytest.approx(1.0, abs=1e-3), "carried fraction")
    control = report["within_job_control"]
    check(not control["drift_within_job"], "no drift within the job")
    for half in ("early_half_r", "late_half_r"):
        check(control[half] == pytest.approx(1.0), f"{half} reads the replay of the original counts")
    for model in ("gain", "offset"):
        check(report["frozen_maps"][model]["n_seed_blocks"] == 16, f"{model}: 16 seed blocks")


def test_a_foreign_manifest_is_not_read(tmp_path: Path) -> None:
    run = synthetic_run(tmp_path, "sim-00")
    check(reading.analyze(run)["reading"].startswith("not read"), "a run of another manifest is not read")


def test_a_qpu_mesh_differing_on_a_known_design_is_left_out(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    run = synthetic_run(tmp_path, mutate="platform")
    monkeypatch.setattr(reading, "ROOT", tmp_path)
    monkeypatch.setattr(case, "ORIGINAL_RUN", str(ORIGINAL))
    monkeypatch.setattr(case, "ORIGINAL_SIM_RUN", str(ROOT / case.ORIGINAL_SIM_RUN))
    for relative in (
        DRAW.relative_to(ROOT),
        Path("docs/evidence/pathion-kernel-map/conjectures/c1_static.npz"),
        (CASES / "job-00" / "cases.json").relative_to(ROOT),
    ):
        (tmp_path / relative).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / relative).write_bytes((ROOT / relative).read_bytes())
    report = reading.analyze(run)
    check(report["replay_mesh_identity"]["differing_designs"] == ["a-h-CC"], "a-h-CC differs")
    check(report["persistence"]["pairs"] == 44, "the design's two mirror items leave")
    check(report["persistence"]["cutoff"] == case.PERSISTENCE_CUTOFF_REDUCED, "reduced cutoff applies")


def test_spec_check_bounds_published_imperfections() -> None:
    spec = case.spec_check(limit=2)
    check(spec["worst_level_shift_from_g2_and_indistinguishability"] < 0.005, "g2 and indistinguishability shift")
    check(spec["dark_level_shift_bound"] < 0.005, "dark count bound")
