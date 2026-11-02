"""Belenos herald-leak pattern analysis: does a compiled mesh change where herald clicks land.

docs/design/belenos-herald-leak-analysis.md preregisters the data, the conditional composition test, the same-mesh
null arm, the decision rule and the exploratory filter link. Each retained iteration's results.json counts are
classified by qd_teleportation_rehearsal.classify under the run's layout; a herald event is a three-click event on the
logical modes that clicks h0 or h1, and its pattern is the set of clicked logical modes. Per input, the herald patterns
of block A (job-02 and its replay) and block B (job-03) form a two-row table, and mesh_selection.composition_test
decides whether the rows share one composition; job-02 against its replay is the same-mesh null arm.

Usage:
  "$PYTHON" scripts/belenos_herald_leak.py --out results/quandela/belenos-herald-leak.json \\
      --seed qrng:docs/evidence/anu_qrng/draw-2026-11-01T054809Z.json#0
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import binom

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import qd_teleportation_rehearsal as tr  # noqa: E402

import mesh_selection as ms  # noqa: E402
import qrng_seeds  # noqa: E402
from parallel import ordered_map  # noqa: E402

RUNS = ROOT / "results/quandela/runs"
RUN_NAMES = {
    "job-02": "2026-10-31T035736Z-qpu_belenos-teleportation_rehearsal-job-02",
    "job-02-replay": "2026-10-31T042633Z-qpu_belenos-teleportation_rehearsal-job-02-replay",
    "job-03": "2026-10-31T040337Z-qpu_belenos-teleportation_rehearsal-job-03",
}
BLOCKS = {"job-02": "A", "job-02-replay": "A", "job-03": "B"}
LABELS = ("+Z", "-Z", "+X", "-X", "+Y", "-Y")
MODE_NAMES = ("q0", "q1", "a0", "a1", "b0", "b1", "h0", "h1")
# Every three-mode subset of the logical modes that clicks a herald mode: C(8, 3) - C(6, 3) = 36 patterns.
PATTERNS = tuple(
    combo for combo in itertools.combinations(range(tr.LOGICAL), tr.MIN_CLICKS) if set(combo) & set(tr.HERALD_MODES)
)
DRAWS = 20_000
ALPHA = 0.05
# Two-sided 0.05 Bonferroni over the 36 patterns: Phi^-1(1 - 0.025 / 36) = 3.20.
RESIDUAL_LIMIT = 3.20
LEAK_SHARE = 0.5
LEAK_INPUTS = 3
OTHER_REASONS = tuple(reason for reason in tr.REJECTIONS if reason != "herald")


def pattern_name(pattern: Sequence[int]) -> str:
    return "+".join(MODE_NAMES[mode] for mode in pattern)


def iteration_row(item: tuple[str, Mapping[str, Any], Sequence[Mapping[str, Any]], Sequence[int]]) -> dict[str, Any]:
    """One iteration's label, samples, correct and wrong counts, rejections by reason and herald pattern counts."""
    run, entry, settings, layout = item
    setting = settings[tr.bound_setting(settings, entry)]
    label = setting["label"]
    basis = next(basis for name, _, basis, _ in tr.SIX_STATES if name == label)
    herald = dict.fromkeys(PATTERNS, 0)
    correct = wrong = 0
    rejected = dict.fromkeys(tr.REJECTIONS, 0)
    for key, count in entry["counts"].items():
        clicks = tr.event_vector(key)
        outcome, pattern, raw = tr.classify(clicks, layout)
        if outcome == "accepted" and pattern is not None and raw is not None:
            x, z = tr.frames()[pattern]
            if tr.decode_bit(basis, raw, x, z) == tr.expected_bit(label):
                correct += count
            else:
                wrong += count
            continue
        if outcome == "below":
            raise ValueError(f"{run} {label}: an event below the {tr.MIN_CLICKS}-click filter")
        rejected[outcome] += count
        if outcome == "herald":
            logical = tuple(index for index, mode in enumerate(layout) if clicks[mode])
            herald[logical] += count
    if sum(herald.values()) != rejected["herald"]:
        raise ValueError(f"{run} {label}: herald patterns do not sum to the herald rejections")
    return {
        "run": run,
        "block": BLOCKS[run],
        "label": label,
        "compilation_seed": setting["compilation_seed"],
        "samples": sum(entry["counts"].values()),
        "correct": correct,
        "wrong": wrong,
        "rejected": rejected,
        "herald": [herald[p] for p in PATTERNS],
    }


def load_rows(runs: Mapping[str, Path]) -> list[dict[str, Any]]:
    """Every iteration of the selected runs, classified on the pool, checked against each run's analysis.json."""
    items: list[tuple[str, Mapping[str, Any], Sequence[Mapping[str, Any]], Sequence[int]]] = []
    for run, directory in runs.items():
        cases = json.loads((directory / "cases.json").read_text(encoding="utf-8"))
        results = json.loads((directory / "results.json").read_text(encoding="utf-8"))
        layout = tuple(cases["layout"]["chip_modes"])
        items.extend((run, entry, cases["settings"], layout) for entry in results["iterations"])
    rows = ordered_map(iteration_row, items, min_items=1)
    for run, directory in runs.items():
        analysis = json.loads((directory / "analysis.json").read_text(encoding="utf-8"))
        retained = {row["label"]: row for row in analysis["iterations"]}
        for row in (r for r in rows if r["run"] == run):
            kept = retained[row["label"]]
            same = (row["correct"], row["wrong"], row["samples"], row["rejected"]) == (
                kept["correct"],
                kept["wrong"],
                kept["samples"],
                kept["rejected"],
            )
            if not same or row["compilation_seed"] != kept["compilation_seed"]:
                raise ValueError(f"{run} {row['label']}: the classification departs from the retained analysis")
    return rows


def pooled(rows: Sequence[Mapping[str, Any]], label: str, runs: Sequence[str]) -> dict[str, Any]:
    picked = [r for r in rows if r["label"] == label and r["run"] in runs]
    if len(picked) != len(runs):
        raise ValueError(f"{label}: {len(picked)} iterations for runs {list(runs)}")
    return {
        "samples": sum(r["samples"] for r in picked),
        "correct": sum(r["correct"] for r in picked),
        "wrong": sum(r["wrong"] for r in picked),
        "rejected": {k: sum(r["rejected"][k] for r in picked) for k in tr.REJECTIONS},
        "herald": np.sum([r["herald"] for r in picked], axis=0),
    }


def localize(table: np.ndarray) -> dict[str, Any]:
    """The pattern carrying the largest share of the table's chi-square, its share and adjusted residual."""
    columns = np.flatnonzero(table.sum(axis=0) > 0)
    kept = table[:, columns].astype(float)
    n = kept.sum()
    expected = kept.sum(axis=1, keepdims=True) * kept.sum(axis=0, keepdims=True) / n
    contribution = ((kept - expected) ** 2 / expected).sum(axis=0)
    residual = ms.adjusted_residuals(kept)[0]
    top = int(np.argmax(contribution))
    pattern = PATTERNS[columns[top]]
    share = float(contribution[top] / contribution.sum())
    leak = share >= LEAK_SHARE and abs(float(residual[top])) > RESIDUAL_LIMIT
    return {
        "pattern": pattern_name(pattern),
        "herald_modes": [MODE_NAMES[m] for m in pattern if m in tr.HERALD_MODES],
        "chi_square_share": share,
        "adjusted_residual_first_row": float(residual[top]),
        "specific_leak": bool(leak),
    }


def comparison(rows: Sequence[Mapping[str, Any]], first: Sequence[str], second: Sequence[str], seed: Any) -> dict:
    """Composition test, localization, filter link and rejection rates of first-row runs against second-row runs."""
    cells = {label: (pooled(rows, label, first), pooled(rows, label, second)) for label in LABELS}
    tables = [np.vstack([a["herald"], b["herald"]]) for a, b in cells.values()]
    test = ms.composition_test(tables, DRAWS, seed)
    per_input = {}
    matches = 0
    for label, table in zip(LABELS, tables, strict=True):
        a, b = cells[label]

        def rate(cell: Mapping[str, Any], key: str) -> float:
            value = cell[key] if key in ("correct", "wrong") else cell["rejected"].get(key)
            if key == "other":
                value = sum(cell["rejected"][r] for r in OTHER_REASONS)
            return float(value) / cell["samples"]

        delta = {key: rate(b, key) - rate(a, key) for key in ("correct", "wrong", "herald", "other")}
        match = (
            np.sign(delta["herald"]) == -np.sign(delta["wrong"])
            and delta["wrong"] != 0
            and abs(delta["correct"]) < abs(delta["wrong"])
        )
        matches += int(match)
        per_input[label] = {
            "herald_events": [int(a["herald"].sum()), int(b["herald"].sum())],
            "chi_square": test["per_table"][LABELS.index(label)],
            "localization": localize(table),
            "second_minus_first_per_sample": delta,
            "filter_reading_matches": bool(match),
            "rates_per_sample": {
                side: {
                    "correct": rate(cell, "correct"),
                    "wrong": rate(cell, "wrong"),
                    **{reason: cell["rejected"][reason] / cell["samples"] for reason in tr.REJECTIONS},
                }
                for side, cell in (("first", a), ("second", b))
            },
        }
    return {
        "first": list(first),
        "second": list(second),
        "chi_square_sum": test["statistic"],
        "p": test["p"],
        "draws": test["draws"],
        "rejects": test["p"] < ALPHA,
        "per_input": per_input,
        "filter_matches": matches,
        "filter_sign_test_p": float(binom.sf(matches - 1, len(LABELS), 0.5)),
    }


def verdict(primary: Mapping[str, Any], null: Mapping[str, Any]) -> dict[str, Any]:
    """The preregistered decision table and, for a mesh-dependent composition, the specific-leak rule."""
    if not primary["rejects"]:
        return {"composition": "broad loss: herald composition does not depend on the mesh at this power"}
    if null["rejects"]:
        return {"composition": "composition drifts within one mesh; the mesh contrast is not attributable"}
    leaks = [label for label, cell in primary["per_input"].items() if cell["localization"]["specific_leak"]]
    common = set(MODE_NAMES[m] for m in tr.HERALD_MODES)
    for label in leaks:
        common &= set(primary["per_input"][label]["localization"]["herald_modes"])
    specific = len(leaks) >= LEAK_INPUTS and bool(common)
    return {
        "composition": "the mesh changes the herald composition",
        "inputs_with_specific_leak": leaks,
        "common_herald_modes": sorted(common) if leaks else [],
        "leak": "specific leak" if specific else "broad change of composition",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--out", type=Path, required=True)
    qrng_seeds.add_seed_argument(parser, "--seed", help="reallocation seed, qrng:<draw>#<index>")
    args = parser.parse_args()
    if args.seed is None:
        parser.error("--seed is required")
    rows = load_rows({run: RUNS / name for run, name in RUN_NAMES.items()})
    primary_seed, null_seed = np.random.SeedSequence(args.seed).spawn(2)
    primary = comparison(rows, ("job-02", "job-02-replay"), ("job-03",), primary_seed)
    null = comparison(rows, ("job-02",), ("job-02-replay",), null_seed)
    record = {
        "schema": "belenos-herald-leak-v1",
        "design": "docs/design/belenos-herald-leak-analysis.md",
        "runs": {run: f"results/quandela/runs/{name}" for run, name in RUN_NAMES.items()},
        "seed_source": qrng_seeds.seed_record(
            "scripts/belenos_herald_leak.py", "--seed", "belenos-herald-leak-composition", args.seed_source
        ),
        "patterns": [pattern_name(p) for p in PATTERNS],
        "alpha": ALPHA,
        "residual_limit": RESIDUAL_LIMIT,
        "primary_mesh_contrast": primary,
        "null_arm_same_mesh": null,
        "verdict": verdict(primary, null),
        "iterations": [
            {
                **{k: v for k, v in row.items() if k != "herald"},
                "herald": dict(zip(map(pattern_name, PATTERNS), row["herald"], strict=True)),
            }
            for row in rows
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"primary_p": primary["p"], "null_p": null["p"], "verdict": record["verdict"]}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
