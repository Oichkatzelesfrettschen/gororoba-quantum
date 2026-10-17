"""Analysis of retained Quandela box-kite photonic runs against their exact preregistered ideals.

Each run directory under results/quandela/runs/ holds a case (cases.json,
circuit.json) and a collected result (results.json, raw/result.json); the
counts come from qd_platform.run_facts, so a run whose raw bytes or receipt
fail its rules is never analyzed. Per block the analysis reads only the
modes the block occupies:

- One-photon blocks. A sample with exactly one click inside the block counts
  toward that mode; samples with clicks outside the block or with two or more
  clicks inside it are reported separately (multiphoton emission, dark
  counts, crosstalk). a is the algebra-mode fraction of the one-click
  samples, with a Wilson 95% interval, against the exact p_algebra; in_block
  is the share of all one-click samples that land on the block's modes, the
  chip's routing fidelity for the block, whose ideal is 1; the total
  variation distance compares the one-click histogram with the exact
  |U[k][0]|^2. A dark block reads the floor a_dark, a bright block the
  ceiling a_bright.
- Pair blocks. Among samples with exactly two clicks inside the block, f is
  the share with one click on each label mode, with its Wilson interval. The
  exact two_click terms give f(V) = (V L_ind + (1 - V) L_dist) /
  (V T_ind + (1 - V) T_dist); V_g2_0 inverts that curve, the g2 = 0 limit of
  the preregistered model (multiphoton emission biases it low on a
  suppressed block).

The statistics are exact fractions and floats from the standard library, so
the analysis replays on CI without Perceval. --write RUN_DIR... writes each
run's analysis.json; --check RUN_DIR... recomputes and compares bytes;
--self-test requires a corrupted count, a swapped role and a pair histogram
off its ideal to change the verdicts.

Usage: "$PYTHON" scripts/qd_box_kite_analysis.py (--write | --check) RUN_DIR... | --self-test
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

from qd_platform import PlatformError, load_case, run_facts

SCHEMA = "qd-box-kite-analysis-v1"
Z95 = 1.959963984540054


def wilson(successes: int, trials: int) -> list[float]:
    """The Wilson 95% interval of a binomial proportion; [0, 1] for no trials."""
    if trials == 0:
        return [0.0, 1.0]
    p = successes / trials
    denominator = 1 + Z95 * Z95 / trials
    center = (p + Z95 * Z95 / (2 * trials)) / denominator
    half = Z95 * math.sqrt(p * (1 - p) / trials + Z95 * Z95 / (4 * trials * trials)) / denominator
    return [round(max(0.0, center - half), 9), round(min(1.0, center + half), 9)]


def occupied(state: str) -> list[int]:
    return [k for k, n in enumerate(state.split(",")) if int(n)]


def one_photon(block: dict[str, Any], counts: dict[str, int], ideal: list[float] | None = None) -> dict[str, Any]:
    offset, width = block["offset"], len(block["roles"])
    inside = range(offset, offset + width)
    modes = [0] * width
    multi = outside = other = 0
    leaked: dict[int, int] = {}
    for state, n in counts.items():
        clicks = occupied(state)
        mine = [k for k in clicks if k in inside]
        if len(mine) == 1 and len(clicks) == 1:
            modes[mine[0] - offset] += n
        elif len(clicks) == 1:
            outside += n
            leaked[clicks[0]] = leaked.get(clicks[0], 0) + n
        elif len(mine) > 1:
            multi += n
        else:
            other += n
    total = sum(modes)
    algebra = sum(n for n, role in zip(modes, block["roles"], strict=True) if role != "dilation")
    expected = ideal if ideal is not None else [float(Fraction(p)) for p in block["ideal"]]
    distance = sum(abs(n / total - p) for n, p in zip(modes, expected, strict=True)) / 2 if total else None
    return {
        "config": block["config"],
        "kind": block["kind"],
        "p_algebra": block["p_algebra"],
        "one_click_by_mode": modes,
        "multi_click_in_block": multi,
        "one_click_outside_block": outside,
        "one_click_outside_by_mode": {str(k): v for k, v in sorted(leaked.items())},
        "other_multi_click": other,
        "in_block": round(total / (total + outside), 9) if total + outside else None,
        "in_block_wilson95": wilson(total, total + outside),
        "a": round(algebra / total, 9) if total else None,
        "a_wilson95": wilson(algebra, total),
        "total_variation_from_ideal": round(distance, 9) if distance is not None else None,
    }


def pair(block: dict[str, Any], counts: dict[str, int]) -> dict[str, Any]:
    offset, width = block["offset"], len(block["roles"])
    labels = [offset + k for k, role in enumerate(block["roles"]) if role != "dilation"]
    pairs: dict[str, int] = {}
    other = 0
    for state, n in counts.items():
        clicks = occupied(state)
        mine = [k for k in clicks if offset <= k < offset + width]
        if len(mine) == 2 and len(clicks) == 2:
            key = f"{mine[0] - offset},{mine[1] - offset}"
            pairs[key] = pairs.get(key, 0) + n
        else:
            other += n
    two = sum(pairs.values())
    label = pairs.get(f"{labels[0] - offset},{labels[1] - offset}", 0)
    l_ind, l_dist = (Fraction(x) for x in block["two_click"]["label"])
    t_ind, t_dist = (Fraction(x) for x in block["two_click"]["total"])
    f = label / two if two else None
    v_g2_0 = None
    if f is not None:
        # f (V T_ind + (1 - V) T_dist) = V L_ind + (1 - V) L_dist, solved for V.
        slope = (float(l_ind) - float(l_dist)) - f * (float(t_ind) - float(t_dist))
        if slope:
            v_g2_0 = round((f * float(t_dist) - float(l_dist)) / slope, 9)
    return {
        "config": block["config"],
        "kind": block["kind"],
        "permanent": block["permanent"],
        "two_click_by_mode_pair": dict(sorted(pairs.items())),
        "other_samples": other,
        "f": round(f, 9) if f is not None else None,
        "f_wilson95": wilson(label, two),
        "f_ideal_v1": str(l_ind / t_ind),
        "f_ideal_v0": str(l_dist / t_dist),
        "v_g2_0": v_g2_0,
    }


def q2_float(entry: list[str]) -> float:
    return float(Fraction(entry[0])) + float(Fraction(entry[1])) * math.sqrt(2.0)


def fringe(block: dict[str, Any], iterations: list[dict[str, Any]]) -> dict[str, Any]:
    """a(phi) per iteration and the fit A + B cos phi + C sin phi over phi = k pi/4, k = 0..7.

    Eight equally spaced phases make the least-squares fit closed form:
    A is the mean, B and C are 2/8 of the cosine and sine sums; the visibility
    is sqrt(B^2 + C^2) / A and the phase offset atan2(C, B).
    """
    steps = len(block["iterations"])
    points: list[dict[str, Any] | None] = [None] * steps
    for entry in iterations:
        phi = entry["iteration"].get("circuit_params", {}).get("phi")
        if not isinstance(phi, int | float):
            raise ValueError(f"{block['config']}: an iteration names no phi")
        k = round(phi / (math.pi / 4))
        if not 0 <= k < steps or abs(phi - k * math.pi / 4) > 1e-9 or points[k] is not None:
            raise ValueError(f"{block['config']}: iteration phi {phi} is off the k pi/4 grid or repeats")
        stats = one_photon(
            {**block, "ideal": block["iterations"][k]["ideal"], "p_algebra": block["iterations"][k]["p_algebra"]},
            entry["counts"],
            ideal=[q2_float(x) for x in block["iterations"][k]["ideal"]],
        )
        stats["phi_quarter_pi"] = k
        stats["p_algebra_ideal"] = round(q2_float(block["iterations"][k]["p_algebra"]), 9)
        points[k] = stats
    if any(point is None for point in points):
        raise ValueError(f"{block['config']}: the result lacks an iteration")
    a = [float(point["a"]) for point in points if point is not None]
    mean = sum(a) / steps
    cosine = 2 * sum(v * math.cos(k * math.pi / 4) for k, v in enumerate(a)) / steps
    sine = 2 * sum(v * math.sin(k * math.pi / 4) for k, v in enumerate(a)) / steps
    return {
        "config": block["config"],
        "kind": "fringe",
        "points": points,
        "fit": {
            "A": round(mean, 9),
            "B": round(cosine, 9),
            "C": round(sine, 9),
            "visibility": round(math.hypot(cosine, sine) / mean, 9) if mean else None,
            "phase_offset": round(math.atan2(sine, cosine), 9),
        },
    }


def analyze(run: Path) -> dict[str, Any]:
    facts = run_facts(run)
    manifest, _, cases_sha256 = load_case(run)
    collected = json.loads((run / "results.json").read_text(encoding="utf-8"))
    counts = collected.get("counts", {})
    blocks = []
    for block in manifest["blocks"]:
        if block["kind"] == "pair":
            blocks.append(pair(block, counts))
        elif block["kind"] == "fringe":
            blocks.append(fringe(block, collected.get("iterations", [])))
        else:
            blocks.append(one_photon(block, counts))
    return {
        "schema": SCHEMA,
        "run": run.name,
        "platform": facts["backends"][0],
        "job_id": collected["job_id"],
        "status": collected["status"]["status"],
        "cases_sha256": cases_sha256,
        "result_sha256": collected.get("result_sha256"),
        "samples": collected.get("samples", 0),
        "shots": collected.get("shots"),
        "noise": collected.get("result_fields", {}).get("noise"),
        "physical_perf": collected.get("result_fields", {}).get("physical_perf"),
        "logical_perf": collected.get("result_fields", {}).get("logical_perf"),
        "blocks": blocks,
    }


def text(record: dict[str, Any]) -> str:
    return json.dumps(record, indent=1, sort_keys=True) + "\n"


def self_test() -> int:
    one = {
        "config": "c",
        "kind": "two_label",
        "offset": 0,
        "roles": ["label_0", "label_1", "dilation", "dilation"],
        "ideal": ["0", "0", "1/2", "1/2"],
        "p_algebra": "0",
    }
    dark = {"0,0,1,0": 500, "0,0,0,1": 500}
    base = one_photon(one, dark)
    if base["a"] != 0 or base["total_variation_from_ideal"] != 0:
        raise AssertionError(f"an ideal dark histogram reads {base}")
    leaked = one_photon(one, {**dark, "1,0,0,0": 10})
    if not leaked["a"] or leaked["a_wilson95"][0] <= 0:
        raise AssertionError("a dark-block leak left a at zero")
    swapped = copy.deepcopy(one)
    swapped["roles"] = ["dilation", "dilation", "label_0", "label_1"]
    if one_photon(swapped, dark)["a"] != 1:
        raise AssertionError("swapped roles kept the dark verdict")
    edge = {
        "config": "p",
        "kind": "pair",
        "permanent": 2,
        "offset": 0,
        "roles": ["label_0", "label_1", "dilation", "dilation"],
        "two_click": {"label": ["1/4", "1/8"], "total": ["1/2", "3/4"]},
    }
    ideal_edge = pair(edge, {"1,1,0,0": 500, "0,0,1,1": 250, "1,0,1,0": 250})
    if ideal_edge["f"] != 0.5 or ideal_edge["v_g2_0"] != 1.0:
        raise AssertionError(f"an ideal edge histogram reads {ideal_edge}")
    classical = pair(edge, {"1,1,0,0": 1, "0,0,1,1": 2, "1,0,1,0": 3})
    if classical["v_g2_0"] is None or abs(classical["v_g2_0"]) > 1e-9:
        raise AssertionError(f"a distinguishable edge histogram reads V = {classical['v_g2_0']}")
    edge_block: dict[str, Any] = {
        "config": "f",
        "kind": "fringe",
        "offset": 0,
        "roles": ["label_0", "label_1", "dilation", "dilation"],
        "iterations": [],
    }
    entries = []
    for k in range(8):
        p = (1 + math.cos(k * math.pi / 4)) / 2
        edge_block["iterations"].append(
            {
                "ideal": [[str(p / 2), "0"], [str(p / 2), "0"], [str((1 - p) / 2), "0"], [str((1 - p) / 2), "0"]],
                "p_algebra": [str(p), "0"],
            }
        )
        n = round(4000 * p)
        entries.append(
            {"iteration": {"circuit_params": {"phi": k * math.pi / 4}}, "counts": {"1,0,0,0": n, "0,0,1,0": 4000 - n}}
        )
    fitted = fringe(edge_block, entries)["fit"]
    if abs(fitted["visibility"] - 1) > 1e-3 or abs(fitted["phase_offset"]) > 1e-3:
        raise AssertionError(f"an ideal edge fringe fits as {fitted}")
    try:
        fringe(edge_block, entries[:-1])
    except ValueError:
        pass
    else:
        raise AssertionError("a fringe missing an iteration was analyzed")
    print("qd box-kite analysis self-test: 7 verdicts")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--self-test", action="store_true")
    parser.add_argument("runs", type=Path, nargs="*")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    try:
        for run in args.runs:
            rendered = text(analyze(run))
            path = run / "analysis.json"
            if args.write:
                path.write_text(rendered, encoding="utf-8")
            elif not path.is_file() or path.read_text(encoding="utf-8") != rendered:
                raise SystemExit(f"{path} differs from the recomputed analysis")
            print(f"{run.name}: analysis {'written' if args.write else 'matches'}")
    except PlatformError as error:
        raise SystemExit(str(error)) from None
    return 0


if __name__ == "__main__":
    sys.exit(main())
