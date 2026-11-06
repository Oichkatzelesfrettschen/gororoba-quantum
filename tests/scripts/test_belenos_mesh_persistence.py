"""Bounded fixtures for the Belenos mesh-persistence case: replay rows, bounds and the analysis of a run."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import belenos_mesh_persistence as bmp
import numpy as np
import pytest

from mesh_selection import persistence


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


def fake_unitary(circuit: Any) -> np.ndarray:
    """The decoder of the synthetic circuits. Mesh m<j> is the 3-mode identity with j added to one entry, so two
    meshes differ in one entry of nine; "modes" sets another mode count and "offset" moves that one entry."""
    modes = circuit.get("modes", 3)
    unitary = np.eye(modes)
    unitary[0, modes - 1] += float(circuit["mesh"][1:]) + circuit.get("offset", 0.0)
    return unitary


def retained_fixture(keys: list[tuple[str, int]], old: dict[tuple[str, int], list[int]], slots: list[int]) -> Any:
    total = 1000
    return {
        "digests": [mesh_digest(f"m{j}") for j in range(4)],
        "circuits": [{"mesh": f"m{j}"} for j in range(4)],
        "blocks": [
            {
                "block": list(key),
                "slot": slot,
                "cells": [
                    {"hit": old[key][j] * 2 if j == 0 else old[key][j], "n": 2 * total if j == 0 else total}
                    for j in range(4)
                ],
            }
            for key, slot in zip(keys, slots, strict=True)
        ],
    }


def test_analyze_matches_blocks_by_key_and_stops_on_a_changed_mesh(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    settings = json.loads((bmp.CASE / "cases.json").read_text(encoding="utf-8"))["settings"]
    # The retained group lists blocks in reverse slot order, and each block carries its own deviation pattern, so a
    # positional match would pair unlike blocks and miss slope 1.
    keys = [(json.dumps(b["m"]), b["t"]) for b in settings[0]["blocks"]][::-1]
    total = 1000
    old = {key: [300 + 40 * i + 25 * ((j + i) % 4) for j in range(4)] for i, key in enumerate(keys)}
    monkeypatch.setattr(bmp, "retained_group", lambda: retained_fixture(keys, old, [5 - i for i in range(len(keys))]))
    monkeypatch.setattr(bmp, "mesh_unitary", fake_unitary)
    mesh_of = [0, 1, 2, 3, 0]
    hits = [{key: old[key][j] for key in keys} for j in mesh_of]
    record = bmp.analyze(synthetic_run(tmp_path, [f"m{j}" for j in mesh_of], hits, total))
    if record["reading"] != "persists" or record["persistence"]["slope"] != pytest.approx(1.0):
        raise AssertionError(record)
    if any(
        not row["same_mesh"] or not row["same_bytes"] or row["unitary_distance"] != 0.0 for row in record["identity"]
    ):
        raise AssertionError(record["identity"])
    # Slots 4 and 5 hold two blocks of four meshes (576 relabelings); dropping slot 5 leaves five blocks.
    secondary = record["secondary"]
    if secondary["slots_4_and_5"]["p_value"] != pytest.approx(1 / 576):
        raise AssertionError(secondary)
    if secondary["without_slot_5"]["p_value"] != pytest.approx(1 / 24**5):
        raise AssertionError(secondary)
    if any(part["slope"] != pytest.approx(1.0) for part in secondary.values()):
        raise AssertionError(secondary)
    # A positional pairing of the new cells with the retained blocks would not recover the slope.
    scrambled = np.array([[old[key][j] for j in range(4)] for key in keys[::-1]], dtype=float)
    aligned = np.array([[old[key][j] for j in range(4)] for key in keys], dtype=float)
    if persistence(aligned, scrambled, bmp.ALPHA, bmp.USEFUL_SLOPE)["slope"] == pytest.approx(1.0):
        raise AssertionError("the fixture cannot tell key matching from positional matching")
    for name, meshes in (("replicate", (0, 9, 2, 3, 0)), ("second-primary", (0, 1, 2, 3, 9))):
        changed = tmp_path / name
        changed.mkdir()
        record = bmp.analyze(synthetic_run(changed, [f"m{j}" for j in meshes], hits, total))
        if record["reading"] != "seed does not reproduce its mesh" or "persistence" in record:
            raise AssertionError((name, record))
        if [row["same_mesh"] for row in record["identity"]] != [j != 9 for j in meshes]:
            raise AssertionError((name, record["identity"]))
    # A returned circuit serialized another way decodes to the retained unitary: the mesh is kept, and the record
    # shows the byte comparison beside it.
    recoded = tmp_path / "recoded"
    recoded.mkdir()
    run = synthetic_run(recoded, [f"m{j}" for j in mesh_of], hits, total)
    results = json.loads((run / "results.json").read_text(encoding="utf-8"))
    results["iterations"][1]["result_fields"]["computed_circuit"]["encoding"] = "second serializer"
    (run / "results.json").write_text(json.dumps(results), encoding="utf-8")
    record = bmp.analyze(run)
    if record["reading"] != "persists" or [row["same_bytes"] for row in record["identity"]] != [
        True,
        False,
        True,
        True,
        True,
    ]:
        raise AssertionError(record)
    if not all(row["same_mesh"] for row in record["identity"]):
        raise AssertionError(record["identity"])


def test_mesh_distance_is_the_largest_entry_difference_and_infinite_across_mode_counts(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(bmp, "mesh_unitary", fake_unitary)
    one = {"mesh": "m1"}
    # One entry of nine differs by 2, so a mean over the entries would give 2/9.
    if bmp.mesh_distance(one, {"mesh": "m3"}) != pytest.approx(2.0) or bmp.mesh_distance(one, dict(one)) != 0.0:
        raise AssertionError(bmp.mesh_distance(one, {"mesh": "m3"}))
    if bmp.mesh_distance(one, {"mesh": "m1", "modes": 4}) != float("inf"):
        raise AssertionError("two mode counts read as a finite distance")


def test_analyze_keeps_a_mesh_at_the_tolerance_and_drops_it_beyond(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    settings = json.loads((bmp.CASE / "cases.json").read_text(encoding="utf-8"))["settings"]
    keys = [(json.dumps(b["m"]), b["t"]) for b in settings[0]["blocks"]]
    total = 1000
    old = {key: [300 + 40 * i + 25 * ((j + i) % 4) for j in range(4)] for i, key in enumerate(keys)}
    monkeypatch.setattr(bmp, "retained_group", lambda: retained_fixture(keys, old, list(range(len(keys)))))
    monkeypatch.setattr(bmp, "mesh_unitary", fake_unitary)
    mesh_of = [0, 1, 2, 3, 0]
    hits = [{key: old[key][j] for key in keys} for j in mesh_of]
    # Mesh m0 keeps every entry exact under an added offset, so the distance is the offset itself.
    for name, offset, same in (("at", bmp.MESH_TOLERANCE, True), ("beyond", 2 * bmp.MESH_TOLERANCE, False)):
        where = tmp_path / name
        where.mkdir()
        run = synthetic_run(where, [f"m{j}" for j in mesh_of], hits, total)
        results = json.loads((run / "results.json").read_text(encoding="utf-8"))
        results["iterations"][0]["result_fields"]["computed_circuit"]["offset"] = offset
        (run / "results.json").write_text(json.dumps(results), encoding="utf-8")
        record = bmp.analyze(run)
        if record["identity"][0]["same_mesh"] is not same or record["identity"][0]["unitary_distance"] != offset:
            raise AssertionError((name, record["identity"][0]))
        if (record["reading"] == "seed does not reproduce its mesh") is same:
            raise AssertionError((name, record["reading"]))
    silent = tmp_path / "silent"
    silent.mkdir()
    run = synthetic_run(silent, [f"m{j}" for j in mesh_of], hits, total)
    results = json.loads((run / "results.json").read_text(encoding="utf-8"))
    del results["iterations"][2]["result_fields"]
    (run / "results.json").write_text(json.dumps(results), encoding="utf-8")
    record = bmp.analyze(run)
    if record["reading"] != "an iteration returned no computed_circuit" or "persistence" in record:
        raise AssertionError(record)
    if record["unreported"] != [settings[2]["name"]]:
        raise AssertionError(record)


def test_the_frozen_case_states_the_thresholds_the_script_applies() -> None:
    preregistered = json.loads((bmp.CASE / "cases.json").read_text(encoding="utf-8"))["preregistered"]
    if (bmp.ALPHA, bmp.DRIFT_ALPHA, bmp.USEFUL_SLOPE) != (0.05, 0.01, 0.5):
        raise AssertionError((bmp.ALPHA, bmp.DRIFT_ALPHA, bmp.USEFUL_SLOPE))
    if bmp.MESH_TOLERANCE != 1e-4:
        raise AssertionError(bmp.MESH_TOLERANCE)
    stated = {
        "reading": (
            "q(0.5) < 0.05 places the upper bound on beta below 0.5",
            "recurs below the useful slope when also p < 0.05, redrawn when p >= 0.05",
            "persists when p < 0.05 and beta >= 0.5",
        ),
        "drift": ("on 6 degrees of freedom", "p < 0.01"),
        "slope": ("0.95 upper bound on beta is the largest b with q(b) >= 0.05", "24^6 within-block relabelings"),
        "identity": ("largest entry difference is at most 0.0001",),
    }
    missing = [(field, text) for field, texts in stated.items() for text in texts if text not in preregistered[field]]
    if missing:
        raise AssertionError(missing)


def test_analyze_withholds_the_reading_when_the_primary_repeats_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    settings = json.loads((bmp.CASE / "cases.json").read_text(encoding="utf-8"))["settings"]
    keys = [(json.dumps(b["m"]), b["t"]) for b in settings[0]["blocks"]]
    total = 1000
    old = {key: [300 + 40 * i + 25 * j for j in range(4)] for i, key in enumerate(keys)}
    monkeypatch.setattr(bmp, "retained_group", lambda: retained_fixture(keys, old, list(range(len(keys)))))
    monkeypatch.setattr(bmp, "mesh_unitary", fake_unitary)
    mesh_of = [0, 1, 2, 3, 0]
    hits = [{key: old[key][j] for key in keys} for j in mesh_of]
    # The second primary repeat reads 150 hits per 1000 above the first in every block.
    hits[4] = {key: old[key][0] + 150 for key in keys}
    record = bmp.analyze(synthetic_run(tmp_path, [f"m{j}" for j in mesh_of], hits, total))
    if record["reading"] != "drift within the new job withholds the reading" or "persistence" in record:
        raise AssertionError(record)
    if record["drift"]["dof"] != 6 or record["drift"]["p_value"] >= bmp.DRIFT_ALPHA:
        raise AssertionError(record["drift"])


def test_analyze_withholds_the_reading_when_an_iteration_has_no_counts_in_a_block(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    settings = json.loads((bmp.CASE / "cases.json").read_text(encoding="utf-8"))["settings"]
    keys = [(json.dumps(b["m"]), b["t"]) for b in settings[0]["blocks"]]
    total = 1000
    old = {key: [300 + 40 * i + 25 * j for j in range(4)] for i, key in enumerate(keys)}
    monkeypatch.setattr(bmp, "retained_group", lambda: retained_fixture(keys, old, list(range(len(keys)))))
    monkeypatch.setattr(bmp, "mesh_unitary", fake_unitary)
    mesh_of = [0, 1, 2, 3, 0]
    hits = [{key: old[key][j] for key in keys} for j in mesh_of]
    run = synthetic_run(tmp_path, [f"m{j}" for j in mesh_of], hits, total)
    # Blank the first block's modes in every state of the second primary repeat: that block then has no
    # single-click sample, while every other block keeps its counts.
    results = json.loads((run / "results.json").read_text(encoding="utf-8"))
    block = settings[4]["blocks"][0]
    blanked: dict[str, int] = {}
    for state, count in results["iterations"][4]["counts"].items():
        modes = state.split(",")
        modes[block["offset"] : block["offset"] + len(block["roles"])] = ["0"] * len(block["roles"])
        blanked[",".join(modes)] = blanked.get(",".join(modes), 0) + count
    results["iterations"][4]["counts"] = blanked
    (run / "results.json").write_text(json.dumps(results), encoding="utf-8")
    record = bmp.analyze(run)
    if record["reading"] != "an iteration returned no single-click counts in a block" or "persistence" in record:
        raise AssertionError(record)
    if record["missing"] != {"block": list(keys[0]), "settings": [settings[4]["name"]]} or "drift" in record:
        raise AssertionError(record)


@pytest.mark.audit
def test_the_power_record_replays_from_its_ledgered_seed() -> None:
    """results/quandela/belenos-mesh-persistence-power.json follows from its seed draw and the retained counts."""
    record = json.loads((bmp.ROOT / "results/quandela/belenos-mesh-persistence-power.json").read_text(encoding="utf-8"))
    seed, _ = bmp.qrng_seeds.parse_value(record["seed_source"]["sources"][0], [])
    replay = bmp.power(seed, record["power"]["mesh_sigma"])
    if replay != record["power"]:
        raise AssertionError(replay)
    # The readings the design document rests on: under every error model a fresh draw reads persists, and the
    # useful slope reads below itself, within sampling error of alpha (three binomial standard errors at 2,000).
    limit = bmp.ALPHA + 3 * (bmp.ALPHA * (1 - bmp.ALPHA) / record["power"]["replicates"]) ** 0.5
    for model in record["power"]["models"]:
        rows = {row["slope"]: row for row in model["rows"]}
        below = rows[bmp.USEFUL_SLOPE]["redrawn"] + rows[bmp.USEFUL_SLOPE]["recurs below the useful slope"]
        if rows[0.0]["persists"] > limit or below > limit:
            raise AssertionError((model["error"], rows[0.0]["persists"], below, limit))

    if (record["bound_seconds"], record["credit_ceiling"]) != (bmp.bound_seconds(), bmp.credit_ceiling()):
        raise AssertionError((record["bound_seconds"], record["credit_ceiling"]))


@pytest.mark.audit
def test_retained_circuits_decode_to_distinct_unitaries_and_survive_rounded_phases() -> None:
    """Perceval decodes the retained computed circuits: the four meshes of the group are pairwise distinct far
    beyond the tolerance, and a circuit serialized with its phases rounded to single precision stays one mesh."""
    from perceval.serialization import deserialize, serialize

    circuits = bmp.retained_group()["circuits"]
    distances = [bmp.mesh_distance(a, b) for i, a in enumerate(circuits) for b in circuits[i + 1 :]]
    if len(distances) != 6 or min(distances) <= 1e3 * bmp.MESH_TOLERANCE:
        raise AssertionError(distances)
    rounded = deserialize(circuits[0])
    for parameter in rounded.get_parameters(all_params=True):
        parameter.set_value(float(np.float32(float(parameter))), force=True)
    again = serialize(rounded)
    distance = bmp.mesh_distance(again, circuits[0])
    if again == circuits[0] or not 0.0 < distance <= bmp.MESH_TOLERANCE:
        raise AssertionError(distance)


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
