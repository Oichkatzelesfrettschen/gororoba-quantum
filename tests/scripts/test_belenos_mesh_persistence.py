"""Bounded fixtures for the Belenos mesh-persistence case: replay rows, exact relabeling test and reading."""

from __future__ import annotations

import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import belenos_mesh_persistence as bmp
import numpy as np
import pytest


def test_replay_rows_are_the_retained_packed_set_4_rows_in_order() -> None:
    retained = bmp.retained_rows()
    replay = bmp.settings()
    if [(r["arm"], r["repeat"]) for r in retained] != list(bmp.ORDER):
        raise AssertionError([(r["arm"], r["repeat"]) for r in retained])
    for index, (old, new) in enumerate(zip(retained, replay, strict=True)):
        changed = {key for key in old if old[key] != new[key]}
        if not changed <= {"name", "observation_index"} or "name" not in changed or new["observation_index"] != index:
            raise AssertionError((index, changed))
    if {r["compilation_seed"] for r in replay if r["arm"] == "primary"} != {bmp.PRIMARY_SEED}:
        raise AssertionError("the primary repeats carry another seed")
    if any(Fraction(block["p_algebra"]) != Fraction(1, 2) for r in replay for block in r["blocks"]):
        raise AssertionError("set 4 holds a block that is not a half block")


def test_the_case_fits_its_duration_margin_and_credit_ceiling() -> None:
    if bmp.bound_seconds() > 270 or bmp.credit_ceiling() != pytest.approx(1.09):
        raise AssertionError((bmp.bound_seconds(), bmp.credit_ceiling()))


def test_exact_upper_p_equals_brute_force_enumeration() -> None:
    per_block = [np.array([0.3, -0.1, 0.2]), np.array([1.0, -1.0]), np.array([0.5, 0.0, -0.5, 0.25])]
    observed = 0.6
    brute = np.mean([sum(c) >= observed - 1e-12 for c in itertools.product(*per_block)])
    if bmp.exact_upper_p(per_block, observed) != pytest.approx(brute):
        raise AssertionError((bmp.exact_upper_p(per_block, observed), brute))


def test_a_recurring_deviation_reads_persists_and_a_reversed_one_does_not() -> None:
    old = np.array(
        [
            [0.60, 0.52, 0.48, 0.40],
            [0.45, 0.55, 0.50, 0.58],
            [0.62, 0.50, 0.41, 0.47],
            [0.51, 0.44, 0.60, 0.53],
            [0.39, 0.47, 0.52, 0.58],
            [0.55, 0.61, 0.43, 0.49],
        ]
    )
    same = bmp.persistence(old, old + 0.03)
    if same["slope"] != pytest.approx(1.0) or same["p_value"] > 0.01 or bmp.read(same) != "persists":
        raise AssertionError(same)
    mirrored = old.mean(axis=1, keepdims=True) - (old - old.mean(axis=1, keepdims=True))
    flipped = bmp.persistence(old, mirrored)
    if flipped["slope"] != pytest.approx(-1.0) or bmp.read(flipped) == "persists":
        raise AssertionError(flipped)
    if bmp.read({"p_value": 0.5, "slope_upper": 0.2}) != "redrawn":
        raise AssertionError("an upper bound below the useful slope does not read redrawn")
    if bmp.read({"p_value": 0.5, "slope_upper": 0.9}) != "indeterminate":
        raise AssertionError("a wide upper bound does not read indeterminate")


def synthetic_counts(setting: dict[str, Any], hits: dict[tuple[str, int], int], total: int) -> dict[str, int]:
    """Counts whose single-click share on each block's algebra modes is hits[block] / total: one state per block
    clicks that block's first algebra mode and every other block's first dilation mode, and one state clicks every
    block's first dilation mode."""

    def state(algebra_block: tuple[str, int] | None) -> str:
        modes = [0] * bmp.swap.MODES
        for block in setting["blocks"]:
            key = (json.dumps(block["m"]), block["t"])
            role = "label_0" if key == algebra_block else "dilation"
            modes[block["offset"] + block["roles"].index(role)] = 1
        return ",".join(map(str, modes))

    counts = {state(key): hit for key, hit in hits.items()}
    counts[state(None)] = total - sum(hits.values())
    return counts


def synthetic_run(tmp_path: Path, meshes: list[str], hits: list[dict[tuple[str, int], int]], total: int) -> Path:
    run = tmp_path / "run"
    run.mkdir()
    (run / "cases.json").write_bytes((bmp.CASE / "cases.json").read_bytes())
    settings = json.loads((bmp.CASE / "cases.json").read_text(encoding="utf-8"))["settings"]
    entries = [
        {
            "iteration": {"circuit_params": s["circuit_params"], "compilation_seed": s["compilation_seed"]},
            "counts": synthetic_counts(s, h, total),
            "result_fields": {"computed_circuit": {"mesh": d}},
        }
        for s, d, h in zip(settings, meshes, hits, strict=True)
    ]
    (run / "results.json").write_text(json.dumps({"iterations": entries}), encoding="utf-8")
    return run


def mesh_digest(name: str) -> str:
    return hashlib.sha256(json.dumps({"mesh": name}, sort_keys=True).encode()).hexdigest()


def test_analyze_matches_blocks_by_key_and_stops_on_a_changed_mesh(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    settings = json.loads((bmp.CASE / "cases.json").read_text(encoding="utf-8"))["settings"]
    # The retained group lists blocks in reverse slot order, so a positional match would pair the wrong blocks.
    keys = [(json.dumps(b["m"]), b["t"]) for b in settings[0]["blocks"]][::-1]
    total = 1000
    old = {key: [300 + 40 * i + 25 * j for j in range(4)] for i, key in enumerate(keys)}
    group = {
        "digests": [mesh_digest(f"m{j}") for j in range(4)],
        "blocks": [
            {
                "block": list(key),
                "slot": 5 - i,
                "cells": [
                    {"hit": old[key][j] * 2 if j == 0 else old[key][j], "n": 2 * total if j == 0 else total}
                    for j in range(4)
                ],
            }
            for i, key in enumerate(keys)
        ],
    }
    monkeypatch.setattr(bmp, "retained_group", lambda: group)
    mesh_of = [0, 1, 2, 3, 0]
    hits = [{key: old[key][j] for key in keys} for j in mesh_of]
    record = bmp.analyze(synthetic_run(tmp_path, [f"m{j}" for j in mesh_of], hits, total))
    if record["reading"] != "persists" or record["persistence"]["slope"] != pytest.approx(1.0):
        raise AssertionError(record)
    changed = tmp_path / "changed"
    changed.mkdir()
    record = bmp.analyze(synthetic_run(changed, [f"m{j}" for j in (0, 9, 2, 3, 0)], hits, total))
    if record["reading"] != "seed does not reproduce its mesh" or "persistence" in record:
        raise AssertionError(record)


@pytest.mark.audit
def test_retained_results_replayed_through_analyze_read_full_persistence(tmp_path: Path) -> None:
    """The retained job-09 and job-10 packed set-4 entries, fed back as a new run, are their own replay."""
    runs = bmp.ROOT / "results/quandela/runs"
    entries = {}
    for job in ("job-09", "job-10"):
        run = next(runs.glob(f"*belenos_mode_swap_interleaved-{job}"))
        manifest = json.loads((run / "cases.json").read_text(encoding="utf-8"))
        bound, _ = bmp.swap.bind_iterations(manifest["settings"], json.loads((run / "results.json").read_text()))
        for index, setting in enumerate(manifest["settings"]):
            if setting["block_set"] == bmp.BLOCK_SET and setting["layout"] == bmp.LAYOUT:
                entries[(setting["arm"], setting["repeat"])] = bound[index]
    replay = tmp_path / "replay"
    replay.mkdir()
    (replay / "cases.json").write_bytes((bmp.CASE / "cases.json").read_bytes())
    ordered = [entries[key] for key in bmp.ORDER]
    (replay / "results.json").write_text(json.dumps({"iterations": ordered}), encoding="utf-8")
    record = bmp.analyze(replay)
    if record["reading"] != "persists" or record["persistence"]["slope"] != pytest.approx(1.0):
        raise AssertionError(record)
