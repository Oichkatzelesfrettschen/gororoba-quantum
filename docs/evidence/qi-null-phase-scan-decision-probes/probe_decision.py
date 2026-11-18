"""Expected-value probes of the phase scan's decision rule in scripts/qi_pathion_null_phase_scan_cases.py.

coverage, coverage-r5: the label of the q12 truth (-0.15 rad) and the coupler truth (-0.25 rad) at every multiple of the
retained CZ damping that the fit computes (FIT_DAMPING, 0 to 3 in steps of 1/16), with each truth's center
visibility. Falsifier of the CASE's coverage statement: a multiple that reads a wrong error world.

nulls, nulls-r5: no injected phase, a selector flip of 0.0166 to 0.05 when d0 reads 0, beside phase damping on
every CZ or every pulse or amplitude damping on every CZ (0.04 to 0.13 per qubit), with the operating characteristics'
static d2 split added. Falsifier of the CASE's null statement: a combination that reads an error world.

q4-zero: the q4 angle at which the contrast reads zero, by root finding on fractional q4 steps, against the
weighted line through the -10, -5, +5 and +10 degree arms. Falsifier: a line error above 0.49 degrees.

The current rule R6 fits the readout flip over FLIP_GRID: coverage writes coverage_r6.json and nulls writes
nulls_r6.json. Rule R5 holds the flip fixed at 0 (flips=(0.0,)); coverage-r5 and nulls-r5 pin it and write the
retained coverage.json and nulls.json, which no other mode writes. q4-zero does not decide and writes q4_zero.json.
Each mode writes beside this file, or into --out DIR. No random draw is used."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from unittest import mock

import numpy as np
from scipy.optimize import brentq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import qi_pathion_null_phase_scan_cases as ps  # noqa: E402

from parallel import ordered_map  # noqa: E402

R5_FLIPS = (0.0,)
# mode -> (probe, readout flips the decision fits, output file); q4-zero runs no decision.
MODES: dict[str, tuple[str, tuple[float, ...], str]] = {
    "coverage": ("coverage", ps.FLIP_GRID, "coverage_r6.json"),
    "nulls": ("nulls", ps.FLIP_GRID, "nulls_r6.json"),
    "coverage-r5": ("coverage", R5_FLIPS, "coverage.json"),
    "nulls-r5": ("nulls", R5_FLIPS, "nulls.json"),
    "q4-zero": ("q4-zero", (), "q4_zero.json"),
}
NULL_FLIPS = (0.0166, 0.025, 0.036, 0.05)
NULL_CHANNELS = ("cz_phase", "pulse_phase", "cz_amplitude")
NULL_STRENGTHS = (0.04, 0.07, 0.10, 0.13)
Q4_ARMS = ("b0-rxz-q4-m10", "b0-rxz-q4-m5", "b0-rxz-q4-p5", "b0-rxz-q4-p10")
Q4_DEGREES = np.array([-10.0, -5.0, 5.0, 10.0])
Q4_TRUTHS = (
    ("q12_phase", -0.18),
    ("q12_phase", 0.18),
    ("q12_phase", -0.15),
    ("q12_phase", 0.15),
    ("coupler_phase", -0.25),
    ("coupler_phase", 0.25),
)


def coverage_one(item: tuple[str, float, float, tuple[float, ...]]) -> dict[str, object]:
    world, theta, multiple, flips = item
    matrix = ps.predecessor_matrix()
    row = ps.truth_row(world, theta, matrix, noise=ps.scaled(ps.CZ_DAMPING, multiple))
    label = ps.decide(ps.planted_batches(row), lambda b: matrix, flips=flips)["label"]
    return {
        "world": world,
        "theta": theta,
        "multiple": multiple,
        "center_visibility": row[ps.CENTER]["visibility"],
        "label": label,
    }


def null_noise(channel: str, strength: float) -> ps.Noise:
    return {
        "cz_phase": (0.0, 0.0, 0.0, strength),
        "pulse_phase": (0.0, strength, 0.0, 0.0),
        "cz_amplitude": (0.0, 0.0, strength, 0.0),
    }[channel]


def null_one(item: tuple[float, str, float, tuple[float, ...]]) -> dict[str, object]:
    flip, channel, strength, flips = item
    matrix = ps.predecessor_matrix()
    batches = ps.planted_batches(ps.truth_row("exact", 0.0, matrix, flip, noise=null_noise(channel, strength)))
    for batch in batches:
        batch["splits"] = [v + ps.OC_SPLIT_OFFSET for v in batch["splits"]]
    decision = ps.decide(batches, lambda b: matrix, flips=flips)
    numbers = decision["numbers"]
    return {
        "flip": flip,
        "channel": channel,
        "strength": strength,
        "label": decision["label"],
        "center_contrast": numbers["center_contrast"][0],
        "chi2": numbers.get("chi2"),
    }


def q4_contrast(world: str, theta: float, steps: float, matrix: np.ndarray) -> float:
    with (
        mock.patch.dict(ps.ARMS, {"q4x": (steps, 0, 0)}),
        mock.patch.object(ps, "ARM_NAMES", (*ps.ARM_NAMES, "q4x")),
    ):
        return float(ps.truth_row(world, theta, matrix)["q4x"]["contrast"])


def q4_one(item: tuple[str, float]) -> dict[str, object]:
    world, theta = item
    matrix = ps.predecessor_matrix()
    row = ps.truth_row(world, theta, matrix)
    center = row[ps.CENTER]["contrast"]
    rise = np.array([row[arm]["contrast"] - center for arm in Q4_ARMS])
    line = float(-center / ((Q4_DEGREES * rise).sum() / (Q4_DEGREES**2).sum()))
    low, high = (0.5, 4.0) if line > 0 else (-4.0, -0.5)
    zero = 5.0 * float(brentq(lambda k: q4_contrast(world, theta, k, matrix), low, high, xtol=1e-6))
    return {"world": world, "theta": theta, "root_degrees": zero, "line_degrees": line, "error": line - zero}


def rows_of(probe: str, flips: tuple[float, ...]) -> list[dict[str, object]]:
    if probe == "coverage":
        items = [
            (w, t, float(k), flips) for w, t in (("q12_phase", -0.15), ("coupler_phase", -0.25)) for k in ps.FIT_DAMPING
        ]
        return ordered_map(coverage_one, items, min_items=2)
    if probe == "nulls":
        items2 = [(f, c, s, flips) for f in NULL_FLIPS for c in NULL_CHANNELS for s in NULL_STRENGTHS]
        return ordered_map(null_one, items2, min_items=2)
    return ordered_map(q4_one, list(Q4_TRUTHS), min_items=2)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("mode", choices=sorted(MODES))
    parser.add_argument("--out", type=Path, default=HERE, help="directory of the record")
    args = parser.parse_args(argv)
    probe, flips, name = MODES[args.mode]
    ps.build_tables()
    rows = rows_of(probe, flips)
    for row in rows:
        print(row, flush=True)
    (args.out / name).write_text(json.dumps(rows, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
