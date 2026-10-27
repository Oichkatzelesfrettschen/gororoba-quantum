"""Preregistered focal-qubit decisions of results/live/IDLE_PENALTY_FOCAL_CASE.md over idle_penalty reports.

Reads `idle-penalty-report.json` files (scripts/idle_penalty_report.py --out) from runs under one execution
calibration and writes:

- per focal qubit and multiplier (kappa_1, kappa_2star, kappa_2echo): "elevated" when the value less Z_95 standard
  errors exceeds ELEVATED, "nominal" when the value plus or minus Z_95 standard errors lies inside NOMINAL,
  otherwise "unresolved", with the value's rank in the cohort of its own run. The standard errors are the
  analyzer's conditional lower bounds, so "nominal" and "elevated" read narrower than a full error budget would;
- the historical reading for the qubits the retained kappa near 3 could sit on: "supported" when any of them reads
  elevated on kappa_1 or kappa_2star, "weakened" when every one reads nominal on all three multipliers, otherwise
  "unresolved";
- the same-window test: every report's execution calibration stamp, and whether they agree;
- the test-retest floor between every two reports: over qubits that keep role and partner, the Pearson r and the
  order-statistic band of the median second/first ratio, the statistics `--compare` reads across calibrations,
  here under one calibration. They are descriptive and decide nothing.

Usage:
    "$PYTHON" scripts/idle_penalty_focal_decisions.py REPORT... --focal 79,92,93 --context 104,106,124,125,126 \
        --out OUT.json
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import idle_penalty_report as report  # noqa: E402
import numpy as np  # noqa: E402

MULTIPLIERS = ("kappa_1", "kappa_2star", "kappa_2echo")
# optimistic_t1 in idle_penalty_report.pooled reads a cohort median above 1.5 as an optimistic reported T1; one
# qubit is read against the same threshold.
ELEVATED = 1.5
NOMINAL = (0.67, 1.5)
Z_95 = 1.96


def classify(value: float, se: float) -> str:
    if value - Z_95 * se > ELEVATED:
        return "elevated"
    if NOMINAL[0] <= value - Z_95 * se and value + Z_95 * se <= NOMINAL[1]:
        return "nominal"
    return "unresolved"


def focal_entry(rep: dict[str, Any], qubit: str) -> dict[str, Any]:
    entry = rep["qubits"][qubit]
    out: dict[str, Any] = {"run": rep["identity"]["run"], "role": entry["role"], "partner": entry["partner"]}
    for key in MULTIPLIERS:
        if entry.get(key) is None or entry.get(f"{key}_se") is None:
            out[key] = {"verdict": "unresolved", "reason": entry.get(f"{key}_reason", "no fit")}
            continue
        cohort = [q[key] for q in rep["qubits"].values() if q.get(key) is not None]
        out[key] = {
            "value": entry[key],
            "se": entry[f"{key}_se"],
            "verdict": classify(entry[key], entry[f"{key}_se"]),
            "cohort_rank": sum(1 for v in cohort if v < entry[key]) / len(cohort),
        }
    return out


def historical(entries: dict[str, list[dict[str, Any]]]) -> str:
    # A focal qubit no report placed leaves the reading open.
    if not entries or any(not runs for runs in entries.values()):
        return "unresolved"
    readings = [e for runs in entries.values() for e in runs]
    if any(e[key]["verdict"] == "elevated" for e in readings for key in ("kappa_1", "kappa_2star")):
        return "supported"
    if all(e[key]["verdict"] == "nominal" for e in readings for key in MULTIPLIERS):
        return "weakened"
    return "unresolved"


def retest(first: dict[str, Any], second: dict[str, Any]) -> dict[str, Any]:
    def keyed(rep: dict[str, Any]) -> dict[str, tuple[str, int]]:
        return {q: (e["role"], e["partner"]) for q, e in rep["qubits"].items()}

    a, b = keyed(first), keyed(second)
    shared = sorted((q for q in a if b.get(q) == a[q]), key=int)
    out: dict[str, Any] = {"first": first["identity"]["run"], "second": second["identity"]["run"], "n": len(shared)}
    for key in MULTIPLIERS:
        common = [
            q for q in shared if first["qubits"][q].get(key) is not None and second["qubits"][q].get(key) is not None
        ]
        if len(common) < 3:
            out[key] = {"n": len(common)}
            continue
        x = np.array([first["qubits"][q][key] for q in common])
        y = np.array([second["qubits"][q][key] for q in common])
        out[key] = {
            "n": len(common),
            # A constant series has no correlation; corrcoef would divide by its zero spread.
            "pearson_r": float(np.corrcoef(x, y)[0, 1]) if x.std() > 0 and y.std() > 0 else None,
            "ratio": report.median_interval(list(y / x)),
        }
    return out


def decisions(reports: list[dict[str, Any]], focal: list[int], context: list[int]) -> dict[str, Any]:
    def located(qubits: list[int]) -> dict[str, list[dict[str, Any]]]:
        return {str(q): [focal_entry(rep, str(q)) for rep in reports if str(q) in rep["qubits"]] for q in qubits}

    focal_entries = located(focal)
    stamps = {rep["identity"]["run"]: rep["identity"]["calibration"] for rep in reports}
    return {
        "focal": focal_entries,
        "historical_kappa_near_3": historical(focal_entries),
        "context": located(context),
        "calibrations": stamps,
        "same_window": len(set(stamps.values())) == 1,
        "retest": [retest(a, b) for a, b in itertools.combinations(reports, 2)],
    }


def _qubits(text: str) -> list[int]:
    return [int(q) for q in text.split(",") if q]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("reports", type=Path, nargs="+")
    parser.add_argument("--focal", type=_qubits, required=True, help="qubits the historical reading is decided on")
    parser.add_argument("--context", type=_qubits, default=[], help="qubits reported without a decision")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    result = decisions([json.loads(path.read_text()) for path in args.reports], args.focal, args.context)
    text = json.dumps(result, indent=1, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text)
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
