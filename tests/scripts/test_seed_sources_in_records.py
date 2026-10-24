"""Retained records keep every QRNG seed reference they consumed and repeat them only where declared."""

from __future__ import annotations

import json
from pathlib import Path

import n21_exact_model_validation as n21
import seed_provenance

import qrng_seeds

ROOT = Path(__file__).resolve().parents[2]


def draw_ref(index: int) -> str:
    draw = sorted((ROOT / "docs/evidence/anu_qrng").glob("draw-*.json"))[-1]
    return f"qrng:{draw.relative_to(ROOT).as_posix()}#{index}"


def test_replay_command_repeats_a_declared_reference(tmp_path: Path) -> None:
    results = tmp_path / "results"
    results.mkdir()
    ref = draw_ref(5)
    record = {
        "replay_command": f'"$PYTHON" gororoba_quantum/compile_evidence.py --seeds {ref}',
        "seed_source": qrng_seeds.seed_record("gororoba_quantum/compile_evidence.py", "--seeds", "results/x", [ref]),
    }
    (results / "kept.json").write_text(json.dumps(record))
    consumed, stray = seed_provenance.runtime_consumption(results)
    if stray or len(consumed) != 1:
        raise AssertionError(f"a declared replay reference read as stray: {stray}, {consumed}")
    draw_file = ref.removeprefix("qrng:").split("#")[0]
    manifest = {"args": ["--seeds", ref], "bundle": {draw_file: "0" * 64}}
    (results / "submission.json").write_text(json.dumps(manifest))
    if seed_provenance.runtime_consumption(results)[1]:
        raise AssertionError("a wrapper manifest repeating a declared reference read as stray")
    if seed_provenance.claimed_records(results):
        raise AssertionError("a bundle inventory beside an indexed reference claimed the whole draw")
    (results / "case.json").write_text(json.dumps({"draw": {"record": draw_file}}))
    if seed_provenance.claimed_records(results) != {Path(draw_file).name}:
        raise AssertionError("a case manifest naming the draw without an index lost its whole-draw claim")
    (results / "case.json").unlink()
    record["note"] = draw_ref(6)
    (results / "kept.json").write_text(json.dumps(record))
    if seed_provenance.runtime_consumption(results)[1] != ["results/kept.json"]:
        raise AssertionError("an undeclared reference was admitted")


def test_merge_keeps_every_shard_seed_source() -> None:
    def shard(seed: int, index: int) -> dict:
        return {
            "schema": n21.SCHEMA,
            "snapshot": "s",
            "isa": "i",
            "seeds": [seed],
            "shots": 1,
            "counts": {"c": [1]},
            "wall_seconds": 0.0,
            "versions": {},
            "seed_source": qrng_seeds.seed_record(
                "scripts/n21_exact_model_validation.py", "--seed", "s i", [draw_ref(index)]
            ),
        }

    merged = n21.merge([shard(2, 1), shard(1, 0)])
    if "seed_source" in merged or [entry["sources"] for entry in merged["seed_sources"]] != [
        [draw_ref(0)],
        [draw_ref(1)],
    ]:
        raise AssertionError(f"merge kept {merged.get('seed_sources')}")
    found = list(seed_provenance.seed_sources(merged))
    if len(found) != 2:
        raise AssertionError("the merged record hides a shard's seed_source from the ledger check")
