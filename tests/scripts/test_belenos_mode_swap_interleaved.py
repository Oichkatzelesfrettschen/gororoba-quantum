"""Contracts of the Belenos interleaved mode-swap request: frozen cases, seeds, binding, drift and placement."""

from __future__ import annotations

import json
from pathlib import Path

import belenos_mode_swap_interleaved as case
import pytest

ROOT = Path(__file__).resolve().parents[2]


def test_retained_requests_rebuild_and_bind_to_the_packed_and_swapped_unitaries() -> None:
    if case.check() != 0:
        raise AssertionError("the frozen requests do not check")


def test_seeds_are_the_registered_draw_in_index_order_and_repeats_share_one() -> None:
    values = json.loads((ROOT / case.SEED_DRAW).read_text(encoding="utf-8"))["values"]
    if list(case.COMPILATION_SEEDS) != values:
        raise AssertionError("COMPILATION_SEEDS is not the draw in index order")
    for job in case.JOBS:
        manifest = json.loads((case.CASES / job / "cases.json").read_text(encoding="utf-8"))
        by_layout: dict[tuple[int, str], set[int]] = {}
        for setting in manifest["settings"]:
            by_layout.setdefault((setting["block_set"], setting["layout"]), set()).add(setting["compilation_seed"])
        if any(len(seeds) != 1 for seeds in by_layout.values()) or len(by_layout) != 2 * len(case.JOBS[job]):
            raise AssertionError(f"{job}: each set-layout takes exactly one seed for both repeats")
        if [s["layout"] for s in manifest["settings"][:4]] != list(case.ORDER):
            raise AssertionError(f"{job}: the first set does not run in ABBA order")


def _run(
    tmp_path: Path, job: str, share: dict[tuple[str, int], float], same_mesh: bool = True, slot_gain: float = 0.0
) -> Path:
    """A run whose block shares follow share[(layout, repeat)] + slot_gain * slot / 5, 10000 one-click samples per
    block."""
    manifest = json.loads((case.CASES / job / "cases.json").read_text(encoding="utf-8"))
    iterations = []
    for setting in manifest["settings"]:
        counts: dict[str, int] = {}
        for block in setting["blocks"]:
            a = share[(setting["layout"], setting["repeat"])] + slot_gain * (block["offset"] // case.SLOT_WIDTH) / 5
            algebra = next(k for k, role in enumerate(block["roles"]) if role != "dilation")
            dilation = next(k for k, role in enumerate(block["roles"]) if role == "dilation")
            for port, n in ((algebra, round(10000 * a)), (dilation, 10000 - round(10000 * a))):
                state = [0] * case.MODES
                state[block["offset"] + port] = 1
                counts[",".join(map(str, state))] = n
        mesh = f"{setting['layout']}-{setting['block_set']}" + ("" if same_mesh else f"-{setting['repeat']}")
        iterations.append(
            {
                "iteration": {
                    "circuit_params": setting["circuit_params"],
                    "compilation_seed": setting["compilation_seed"],
                },
                "counts": counts,
                "result_fields": {"computed_circuit": mesh},
            }
        )
    run = tmp_path / job
    run.mkdir()
    (run / "cases.json").write_text(json.dumps(manifest), encoding="utf-8")
    (run / "results.json").write_text(json.dumps({"iterations": iterations[::-1]}), encoding="utf-8")
    return run


def test_placement_without_drift_moves_blocks_and_detects_no_drift(tmp_path: Path) -> None:
    share = dict.fromkeys([("packed", 0), ("packed", 1), ("swapped", 0), ("swapped", 1)], 0.40)
    record = case.analyze(_run(tmp_path, "job-00", share, slot_gain=0.1))
    if record["iterations_bound"] != 8 or record["drift"]["detected"] is not False:
        raise AssertionError(record["drift"])
    if record["placement"]["moved"] != record["placement"]["blocks"] or record["placement"]["blocks"] != 12:
        raise AssertionError(record["placement"])


def test_drift_without_placement_is_detected(tmp_path: Path) -> None:
    share = {("packed", 0): 0.40, ("packed", 1): 0.48, ("swapped", 0): 0.48, ("swapped", 1): 0.40}
    record = case.analyze(_run(tmp_path, "job-00", share))
    if record["drift"]["detected"] is not True or record["drift"]["dof"] != 24:
        raise AssertionError(record["drift"])
    if record["placement"]["moved"] != 0:
        raise AssertionError(record["placement"])


def test_repeats_on_different_meshes_leave_drift_descriptive(tmp_path: Path) -> None:
    share = {("packed", 0): 0.40, ("packed", 1): 0.48, ("swapped", 0): 0.48, ("swapped", 1): 0.40}
    record = case.analyze(_run(tmp_path, "job-00", share, same_mesh=False))
    if record["drift"]["dof"] != 0 or record["drift"]["detected"] is not None:
        raise AssertionError(record["drift"])


def test_a_result_iteration_outside_the_case_raises(tmp_path: Path) -> None:
    share = dict.fromkeys([("packed", 0), ("packed", 1), ("swapped", 0), ("swapped", 1)], 0.5)
    run = _run(tmp_path, "job-02", share)
    results = json.loads((run / "results.json").read_text(encoding="utf-8"))
    results["iterations"][0]["iteration"]["compilation_seed"] = 1
    (run / "results.json").write_text(json.dumps(results), encoding="utf-8")
    with pytest.raises(RuntimeError, match="binds to no remaining setting"):
        case.analyze(run)


def test_a_cut_short_job_keeps_its_counted_iterations(tmp_path: Path) -> None:
    share = dict.fromkeys([("packed", 0), ("packed", 1), ("swapped", 0), ("swapped", 1)], 0.5)
    run = _run(tmp_path, "job-02", share)
    results = json.loads((run / "results.json").read_text(encoding="utf-8"))
    results["iterations"][0] = {"missing": True}
    (run / "results.json").write_text(json.dumps(results), encoding="utf-8")
    record = case.analyze(run)
    if (record["iterations_bound"], record["iterations_uncounted"]) != (3, 1):
        raise AssertionError(record)
