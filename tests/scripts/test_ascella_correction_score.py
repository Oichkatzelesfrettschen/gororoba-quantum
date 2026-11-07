"""Bounded fixtures for the prospective correction score: the variance-ratio reading and the mesh gate."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ascella_correction_score as score  # noqa: E402

# docs/evidence/anu_qrng/draw-2026-10-31T193354Z.json index 4 (ledger row in
# docs/evidence/qrng_seeds/allocations.json).
FIXTURE_SEED = 29161


def test_a_table_that_matches_the_repeat_holds_and_an_unrelated_one_fails() -> None:
    """A repeat equal to the table plus counting-sized noise reads correction holds at R near its noise limit; a
    repeat independent of the table reads correction fails, since subtracting it adds its variance."""
    generator = np.random.default_rng(FIXTURE_SEED)
    table = generator.normal(0.0, 0.01, 56)
    table -= table.mean()
    matched = table + generator.normal(0.0, 0.002, 56)
    matched -= matched.mean()
    held = score.ratio_reading(matched, table, generator, 4000)
    if held["reading"] != "correction holds" or held["ratio"] != pytest.approx(
        matched.var(ddof=1) / (matched - table).var(ddof=1)
    ):
        raise AssertionError(held)
    unrelated = generator.normal(0.0, 0.01, 56)
    unrelated -= unrelated.mean()
    failed = score.ratio_reading(unrelated, table, generator, 4000)
    if failed["reading"] != "correction fails" or not failed["lower"] <= failed["ratio"] <= failed["upper"]:
        raise AssertionError(failed)


def test_count_resimulation_keeps_a_matched_repeat_above_and_an_unrelated_one_below_the_useful_ratio() -> None:
    """With large block totals, redrawn counts of a repeat that follows job-02 and job-03's shared pattern keep R well
    above USEFUL_RATIO; a repeat whose pattern is unrelated keeps R below 1, since the refitted table adds variance."""
    generator = np.random.default_rng(FIXTURE_SEED)
    meshes, total = 40, 400000
    pattern = generator.normal(0.0, 0.05, meshes)
    other = generator.normal(0.0, 0.05, meshes)

    def block(z: np.ndarray) -> np.ndarray:
        # n0 - n3 = z N over a fixed 0.6 N of signed counts, the rest split over modes 1 and 2.
        signed = 0.6 * total
        n0 = 0.5 * (signed + z * total)
        n3 = signed - n0
        return np.round(np.stack([n0, 0.2 * total * np.ones(meshes), 0.2 * total * np.ones(meshes), n3], axis=1))

    kept = np.ones(meshes, dtype=bool)
    matched = score.resimulated_ratios((block(pattern), block(pattern), block(pattern)), kept, generator, 200)
    unrelated = score.resimulated_ratios((block(pattern), block(pattern), block(other)), kept, generator, 200)
    if matched.min() < 10 * score.USEFUL_RATIO or unrelated.max() >= 1.0:
        raise AssertionError((matched.min(), unrelated.max()))


def served_run(directory: Path, names: list[str], thetas: list[float]) -> Path:
    """A minimal run directory: one setting per name, each serving a two-mode Rx mesh at its angle."""
    import perceval as pcvl
    from perceval.serialization import serialize

    directory.mkdir()
    settings = [{"name": name} for name in names]
    rows = [
        {"result_fields": {"computed_circuit": serialize(pcvl.Circuit(2) // pcvl.BS.Rx(theta))}} for theta in thetas
    ]
    (directory / "cases.json").write_text(json.dumps({"settings": settings}), encoding="utf-8")
    (directory / "results.json").write_text(json.dumps({"iterations": rows}), encoding="utf-8")
    return directory


def test_the_mesh_gate_admits_the_same_meshes_and_refuses_swapped_ones(tmp_path: Path) -> None:
    """A run that serves every name's mesh, in another order, passes the gate; one whose two names exchanged their
    meshes is refused for exactly those two."""
    names, thetas = ["a", "b", "c"], [0.4, 1.1, 1.9]
    reference = served_run(tmp_path / "reference", names, thetas)
    reordered = served_run(tmp_path / "reordered", names[::-1], thetas[::-1])
    if "all 3 served meshes" not in score.mesh_gate(reference, reordered):
        raise AssertionError("a reordered run of the same meshes failed the gate")
    swapped = served_run(tmp_path / "swapped", names, [thetas[1], thetas[0], thetas[2]])
    with pytest.raises(ValueError, match="2 of 3 served meshes left job-02's"):
        score.mesh_gate(reference, swapped)
