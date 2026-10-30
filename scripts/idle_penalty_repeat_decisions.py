"""Preregistered repeat decisions of results/live/IDLE_PENALTY_REPEAT_CASE.md over two idle_penalty reports.

Reads two `idle-penalty-report.json` files (scripts/idle_penalty_report.py --out) and writes the decisions the
case adds to `--compare`:

- admission: the repeat counts as a calibration change only when the reported T1 and the reported T2 each differ
  from the first run's on at least half the shared qubits, because every multiplier normalizes against them;
- replication: the first run's single-run verdicts (optimistic_t1, echo_gain, readout_shift with its sign) read
  again in the repeat;
- mean visibility loss: both contrasts' pair-mean t statistics below the one-sided CHI2_ALPHA quantile of t, with
  the quiet null other than "present"; a readout_dephasing "present" without it reads "pairwise heterogeneity";
- pair pattern of the readout shift: Pearson r of the pairs' shift_khz across runs, against STABLE_CORRELATION.

Usage:
    "$PYTHON" scripts/idle_penalty_repeat_decisions.py FIRST.json SECOND.json --out OUT.json
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import idle_penalty_report as report  # noqa: E402
import numpy as np  # noqa: E402
from scipy import stats  # noqa: E402

# A reported value that moved by less than this many microseconds counts as carried forward from the earlier
# calibration; the backend reports T1 and T2 to many more digits than any refresh leaves unchanged.
CARRIED_US = 1e-6


def admission(first: dict[str, Any], second: dict[str, Any]) -> dict[str, Any]:
    shared = sorted(set(first["qubits"]) & set(second["qubits"]), key=int)
    moved = {
        key: sum(
            1
            for q in shared
            if abs(first["qubits"][q][f"{key}_reported_us"] - second["qubits"][q][f"{key}_reported_us"]) > CARRIED_US
        )
        for key in ("t1", "t2")
    }
    admitted = bool(shared) and all(2 * count >= len(shared) for count in moved.values())
    return {"shared": len(shared), "t1_moved": moved["t1"], "t2_moved": moved["t2"], "admitted": admitted}


def _sign(value: float) -> str:
    return "negative" if value < 0 else "positive"


def replication(first: dict[str, Any], second: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key in ("optimistic_t1", "echo_gain"):
        a, b = first["pooled"][key], second["pooled"][key]
        out[key] = {"first": a, "second": b, "replicated": a == b}
    readings = []
    for pooled in (first["pooled"], second["pooled"]):
        block = pooled["readout_shift"]
        signs = {_sign(block["vs_after"]["mean"]), _sign(block["vs_quiet"]["mean"])}
        readings.append((block["decision"], signs.pop() if len(signs) == 1 else "mixed"))
    out["readout_shift"] = {
        "first": list(readings[0]),
        "second": list(readings[1]),
        "replicated": readings[0] == readings[1] and readings[0][0] == "present",
    }
    return out


def mean_visibility_loss(pooled: dict[str, Any]) -> str:
    block = pooled["readout_dephasing"]
    after, quiet = block["vs_after"], block["vs_quiet"]
    quantile = stats.t.ppf(report.CHI2_ALPHA, after["n"] - 1)
    if after["t"] < quantile and quiet["t"] < quantile and block["null"]["verdict"] != "present":
        return "mean loss present"
    if block["decision"] == "present":
        return "pairwise heterogeneity"
    return f"no mean loss ({block['decision']})"


def pair_pattern(first: dict[str, Any], second: dict[str, Any]) -> dict[str, Any]:
    def keyed(rep: dict[str, Any]) -> dict[tuple[int, int], float]:
        return {(p["target"], p["spectator"]): p["shift_khz"] for p in rep["pairs"]}

    a, b = keyed(first), keyed(second)
    common = sorted(set(a) & set(b))
    if len(common) < 3:
        return {"n": len(common), "verdict": "unresolved"}
    r = float(np.corrcoef([a[k] for k in common], [b[k] for k in common])[0, 1])
    both_present = all(rep["pooled"]["readout_shift"]["decision"] == "present" for rep in (first, second))
    if not math.isfinite(r):
        verdict = "unresolved"
    elif r >= report.STABLE_CORRELATION:
        verdict = "pair pattern stable"
    elif both_present:
        verdict = "effect stable, pattern not"
    else:
        verdict = "unresolved"
    return {"n": len(common), "pearson_r": r, "verdict": verdict}


def decisions(first: dict[str, Any], second: dict[str, Any]) -> dict[str, Any]:
    return {
        "first": first["identity"]["run"],
        "second": second["identity"]["run"],
        "admission": admission(first, second),
        "replication": replication(first, second),
        "visibility": {
            "first": mean_visibility_loss(first["pooled"]),
            "second": mean_visibility_loss(second["pooled"]),
        },
        "shift_pair_pattern": pair_pattern(first, second),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("first", type=Path)
    parser.add_argument("second", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    result = decisions(*(json.loads(path.read_text()) for path in (args.first, args.second)))
    text = json.dumps(result, indent=1, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text)
    print(text, end="")
    return 0 if result["admission"]["admitted"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
