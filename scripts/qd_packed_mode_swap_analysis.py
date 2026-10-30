"""Decide whether a packed-block residual belongs to the block or to the chip modes it sat on.

Compares two collected box-kite block series that hold the same blocks on different modes:
box_kite_photonic_packed and box_kite_photonic_packed_swapped. Per block, a = (samples with one click inside the
block that land on an algebra mode) / (samples with exactly one click inside the block), the observable of
qd_box_kite_cases.py. The preregistered `mode_swap` record of the swapped cases.json fixes the statistics.

Usage: python3 scripts/qd_packed_mode_swap_analysis.py PACKED SWAPPED
Each series is either a directory holding job-NN/ with cases.json and results.json, or PLATFORM/FAMILY (for
example qpu_belenos/box_kite_photonic_packed), which selects the retained runs
results/quandela/runs/<UTC>-PLATFORM-FAMILY-job-NN in job order. The registered comparison replays as
qpu_belenos/box_kite_photonic_packed qpu_belenos/box_kite_photonic_packed_swapped.
"""

from __future__ import annotations

import json
import math
import re
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from parallel import ordered_map  # noqa: E402

RUNS = ROOT / "results/quandela/runs"

SLOT_WIDTH = 4
BLOCK_CORRELATION = 0.7
BLOCK_CORRELATION_LOWER = 0.3
Z_CRITICAL = 4.5


def series_jobs(series: str | Path) -> list[Path]:
    """The job directories of one series, in job order: job-NN/ under a directory, or PLATFORM/FAMILY retained runs."""
    path = Path(series)
    if path.is_dir():
        jobs = sorted(path.glob("job-*"))
    else:
        platform, _, family = str(series).partition("/")
        pattern = re.compile(rf"^\d{{4}}-\d{{2}}-\d{{2}}T\d{{6}}Z-{re.escape(platform)}-{re.escape(family)}-job-(\d+)$")
        found = [(int(m.group(1)), run) for run in RUNS.iterdir() if (m := pattern.match(run.name))]
        jobs = [run for _, run in sorted(found)]
    if not jobs:
        raise ValueError(f"no job directories for series {series}")
    return jobs


def _job_blocks(job: Path) -> list[tuple[tuple[str, int], dict[str, Any]]]:
    """One job's blocks: slot, p, one-click count n and algebra-mode share a."""
    manifest = json.loads((job / "cases.json").read_text(encoding="utf-8"))
    counts = json.loads((job / "results.json").read_text(encoding="utf-8"))["counts"]
    parsed = [([int(v) for v in key.split(",")], count) for key, count in counts.items()]
    rows = []
    for block in manifest["blocks"]:
        offset = block["offset"]
        width = len(block["roles"])
        algebra = [k for k, role in enumerate(block["roles"]) if role != "dilation"]
        one = hit = 0
        for modes, count in parsed:
            window = modes[offset : offset + width]
            if sum(window) == 1:
                one += count
                if any(window[k] for k in algebra):
                    hit += count
        rows.append(
            (
                (json.dumps(block["m"]), block["t"]),
                {"slot": offset // SLOT_WIDTH, "p": float(Fraction(block["p_algebra"])), "n": one, "a": hit / one},
            )
        )
    return rows


def collect(series: str | Path) -> dict[tuple[str, int], dict[str, Any]]:
    """Per block, keyed by (sign matrix, t), over every job of the series; each job reduces in its own worker."""
    blocks: dict[tuple[str, int], dict[str, Any]] = {}
    for rows in ordered_map(_job_blocks, series_jobs(series)):
        blocks.update(rows)
    return blocks


def correlation(x: list[float], y: list[float]) -> tuple[float, float, float] | None:
    """Pearson r with its Fisher-z 95% interval; None when either vector is constant and r is undefined."""
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxy = sum((u - mx) * (v - my) for u, v in zip(x, y, strict=True))
    sxx = sum((u - mx) ** 2 for u in x)
    syy = sum((v - my) ** 2 for v in y)
    if sxx == 0 or syy == 0:
        return None
    r = sxy / math.sqrt(sxx * syy)
    half = 1.96 / math.sqrt(n - 3)
    z = math.atanh(min(max(r, -0.999999), 0.999999))
    return r, math.tanh(z - half), math.tanh(z + half)


def decide(
    packed: dict[tuple[str, int], dict[str, Any]], swapped: dict[tuple[str, int], dict[str, Any]]
) -> dict[str, Any]:
    if set(packed) != set(swapped):
        raise ValueError("the two series do not hold the same blocks")
    half = sorted(key for key in packed if packed[key]["p"] == 0.5)
    if len(half) < 4:
        raise ValueError("fewer than four half blocks")
    for key in packed:
        if packed[key]["slot"] == swapped[key]["slot"]:
            raise ValueError(f"block {key} sits on the same slot in both series")
    residual = {key: swapped[key]["a"] - 0.5 for key in half}
    by_slot: dict[int, list[tuple[tuple[str, int], float]]] = {}
    for key in half:
        by_slot.setdefault(packed[key]["slot"], []).append((key, packed[key]["a"] - 0.5))

    def slot_mean(key: tuple[str, int]) -> float:
        others = [r for other, r in by_slot.get(swapped[key]["slot"], []) if other != key]
        if not others:
            raise ValueError(f"no other half block sat on slot {swapped[key]['slot']} in the packed series")
        return sum(others) / len(others)

    target = [residual[key] for key in half]
    block_r = correlation([packed[key]["a"] - 0.5 for key in half], target)
    slot_r = correlation([slot_mean(key) for key in half], target)
    if block_r is None or slot_r is None:
        verdict = "undetermined"
    elif block_r[0] > BLOCK_CORRELATION and block_r[1] > BLOCK_CORRELATION_LOWER and block_r[0] > slot_r[0]:
        verdict = "block"
    elif slot_r[0] > BLOCK_CORRELATION and slot_r[1] > BLOCK_CORRELATION_LOWER and slot_r[0] > block_r[0]:
        verdict = "slot"
    else:
        verdict = "mixed"
    moved = []
    for key in sorted(packed):
        p, s = packed[key], swapped[key]
        se = math.sqrt(p["a"] * (1 - p["a"]) / p["n"] + s["a"] * (1 - s["a"]) / s["n"])
        delta = s["a"] - p["a"]
        if se > 0 and abs(delta) / se > Z_CRITICAL:
            moved.append({"block": key, "from_slot": p["slot"], "to_slot": s["slot"], "delta": delta, "z": delta / se})
    return {"verdict": verdict, "block_predictor": block_r, "slot_predictor": slot_r, "moved": moved}


def main() -> int:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    report = decide(collect(sys.argv[1]), collect(sys.argv[2]))
    print(f"verdict: {report['verdict']}")
    for name in ("block_predictor", "slot_predictor"):
        if report[name] is None:
            print(f"{name}: undefined (a constant residual vector)")
            continue
        r, lo, hi = report[name]
        print(f"{name}: r={r:+.3f} [{lo:+.3f}, {hi:+.3f}]")
    print(f"blocks with |z| > {Z_CRITICAL}: {len(report['moved'])}")
    for row in report["moved"]:
        print(
            f"  {row['block']} slot {row['from_slot']} -> {row['to_slot']} delta={row['delta']:+.4f} z={row['z']:+.1f}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
