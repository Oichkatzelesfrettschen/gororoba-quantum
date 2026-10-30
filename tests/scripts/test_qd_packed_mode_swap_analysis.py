"""Contract for qd_packed_mode_swap_analysis.decide on the generated packed and swapped series: a residual built to
follow the block yields the block verdict, one built to follow the chip modes yields the slot verdict, and a series
that holds different blocks is refused.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
import qd_packed_mode_swap_analysis as analysis

CASES = Path(__file__).resolve().parents[2] / "results/quandela/cases"
SAMPLES = 100_000
# f(slot + 3) = -f(slot): a slot residual anti-correlates with itself after the half-turn.
SLOT_RESIDUAL = (0.04, -0.03, 0.01, -0.04, 0.03, -0.01)


def require(condition: bool, message: object) -> None:
    if not condition:
        raise AssertionError(message)


def block_residual(index: int) -> float:
    return ((index * 7) % 11 - 5) / 100


def synthesize(series: str, root: Path, residual: Callable[[int, int], float]) -> Path:
    """Counts whose single-click algebra share is p + residual(block index, slot) on every half block."""
    target = root / series
    for job in sorted((CASES / series).glob("job-*")):
        (target / job.name).mkdir(parents=True)
        manifest = json.loads((job / "cases.json").read_text(encoding="utf-8"))
        (target / job.name / "cases.json").write_text(json.dumps(manifest), encoding="utf-8")
        counts: dict[str, int] = {}
        for index, block in enumerate(manifest["blocks"]):
            p = float(analysis.Fraction(block["p_algebra"]))
            share = (
                p + residual(index + 6 * int(job.name[-2:]), block["offset"] // analysis.SLOT_WIDTH) if p == 0.5 else p
            )
            algebra = block["roles"].index(next(r for r in block["roles"] if r != "dilation"))
            dilation = block["roles"].index("dilation")
            for mode, weight in ((algebra, share), (dilation, 1 - share)):
                key = [0] * 24
                key[block["offset"] + mode] = 1
                counts[",".join(map(str, key))] = counts.get(",".join(map(str, key)), 0) + round(SAMPLES * weight)
        (target / job.name / "results.json").write_text(json.dumps({"counts": counts}), encoding="utf-8")
    return target


def test_residual_that_follows_the_block_is_a_block_attribute() -> None:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        packed = synthesize("box_kite_photonic_packed", root, lambda index, slot: block_residual(index))
        swapped = synthesize("box_kite_photonic_packed_swapped", root, lambda index, slot: block_residual(index))
        report = analysis.decide(analysis.collect(packed), analysis.collect(swapped))
    require(report["verdict"] == "block", report)
    require(not report["moved"], report["moved"])


def test_residual_that_follows_the_slot_is_a_slot_attribute() -> None:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        packed = synthesize("box_kite_photonic_packed", root, lambda index, slot: SLOT_RESIDUAL[slot])
        swapped = synthesize("box_kite_photonic_packed_swapped", root, lambda index, slot: SLOT_RESIDUAL[slot])
        report = analysis.decide(analysis.collect(packed), analysis.collect(swapped))
    require(report["verdict"] == "slot", report)
    require(bool(report["moved"]), report)


def test_series_with_different_blocks_is_refused() -> None:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        packed = analysis.collect(synthesize("box_kite_photonic_packed", root, lambda index, slot: 0.0))
        swapped = analysis.collect(synthesize("box_kite_photonic_packed_swapped", root, lambda index, slot: 0.0))
    del swapped[next(iter(swapped))]
    with pytest.raises(ValueError, match="same blocks"):
        analysis.decide(packed, swapped)
