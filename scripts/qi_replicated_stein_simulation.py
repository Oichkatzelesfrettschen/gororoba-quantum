"""Seeded simulation of the Stein two-stage rule of the replicated Tuna-17 matched-response design.

Draws replicate residuals r_i = delta + sigma z_i (z standard normal, common random numbers across delta) for
each sigma, applies gororoba_quantum/qi_replicated_response.py (required_replicates, stein_statistic, CAP,
T_CRIT) to each trial and writes the rejection, undecided-at-cap and uncapped-rule rates. The uncapped column
removes the cap: the first N1 residuals are drawn, N follows from their SD, and the mean of all N residuals
follows from the first-stage sum plus a normal draw for the other N - N1 residuals, so the level and power
of the rule itself are read without the cap.

The heavy-tailed row draws Student t residuals on 3 degrees of freedom scaled to SD sigma and reports the capped
design at delta 0; its uncapped column stays empty, because the uncapped shortcut draws the later residuals as one
normal variable.

Seeds: docs/evidence/anu_qrng/draw-2026-11-22T010305Z.json, indices 8, 9, 10, 11, 12 in order.
Usage: "$PYTHON" scripts/qi_replicated_stein_simulation.py [--trials N] [--out FILE] [--check | --overwrite]
Without a flag the run writes a new output file and refuses an existing one; --overwrite replaces it and --check
recomputes the table and compares it with the retained file without writing.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import qi_replicated_response as rule  # noqa: E402

SIGMAS = (0.01, 0.02, 0.038, 0.08)
SIMULATION_SEEDS = (34644, 40029, 46414, 54363)
HEAVY_TAIL_SEED = 33479
HEAVY_TAIL_DF = 3
HEAVY_TAIL_SIGMA = 0.038
TRIALS = 400000
OUT = ROOT / "docs/evidence/quantum_inspire/tuna17-replicated-stein-simulation.json"


def simulate(
    sigma: float, deltas: tuple[float, ...], trials: int, seed: int, tail_df: int | None = None
) -> list[dict[str, Any]]:
    """Rates of the capped design and of the uncapped rule at one residual SD, for each effect delta.

    tail_df selects Student t residuals on that many degrees of freedom, scaled to SD sigma; None selects normal.
    """
    rng = np.random.default_rng(seed)
    if tail_df is None:
        z = rng.standard_normal((trials, rule.CAP))
    else:
        z = rng.standard_t(tail_df, (trials, rule.CAP)) / math.sqrt(tail_df / (tail_df - 2))
    extra = rng.standard_normal(trials)
    rows = []
    for delta in deltas:
        r = delta + sigma * z
        s1 = r[:, : rule.N1].std(axis=1, ddof=1)
        required = rule.required_replicates(s1)
        capped = required > rule.CAP
        used = np.where(capped, rule.N1, required)
        mean = np.cumsum(r, axis=1)[np.arange(trials), used - 1] / used
        reject = (~capped) & (np.abs(rule.stein_statistic(mean, s1, used)) >= rule.T_CRIT)
        # The uncapped rule: sum of the first N1 residuals plus (N - N1) more, drawn as one normal of that variance.
        first = r[:, : rule.N1].sum(axis=1)
        more = (required - rule.N1).astype(float)
        total_mean = (first + more * delta + sigma * np.sqrt(more) * extra) / required
        uncapped = np.abs(rule.stein_statistic(total_mean, s1, required)) >= rule.T_CRIT
        rows.append(
            {
                "sigma": sigma,
                "delta": delta,
                "trials": trials,
                "reject_capped_design": float(reject.mean()),
                "undecided_at_cap": float(capped.mean()),
                "reject_given_within_cap": float(reject.sum() / max(int((~capped).sum()), 1)),
                "reject_uncapped_rule": float(uncapped.mean()) if tail_df is None else None,
                "median_required_total": float(np.median(required)),
            }
        )
    return rows


def _same(left: Any, right: Any) -> bool:
    """Structural equality with a 1e-12 tolerance on floats."""
    if isinstance(left, float) and isinstance(right, float):
        return math.isclose(left, right, rel_tol=0.0, abs_tol=1e-12)
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(_same(left[key], right[key]) for key in left)
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(_same(a, b) for a, b in zip(left, right, strict=True))
    return bool(left == right and type(left) is type(right))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=TRIALS)
    parser.add_argument("--out", type=Path, default=OUT)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--check", action="store_true", help="recompute and compare with the retained file; write nothing"
    )
    mode.add_argument("--overwrite", action="store_true", help="replace an existing output file")
    arguments = parser.parse_args()
    table = []
    for sigma, seed in zip(SIGMAS, SIMULATION_SEEDS, strict=True):
        table += simulate(sigma, (0.0, -rule.DELTA), arguments.trials, seed)
    table += simulate(HEAVY_TAIL_SIGMA, (0.0,), arguments.trials, HEAVY_TAIL_SEED, HEAVY_TAIL_DF)
    for row in table[-1:]:
        row["residuals"] = f"student-t-{HEAVY_TAIL_DF}-scaled-to-sd"
    record = {
        "schema": "qi-replicated-stein-simulation-v1",
        "rule": {"n1": rule.N1, "cap": rule.CAP, "alpha": rule.ALPHA, "power": rule.POWER, "c": rule.C},
        "seed_draw": "docs/evidence/anu_qrng/draw-2026-11-22T010305Z.json",
        "seed_indices": [8, 9, 10, 11, 12],
        "rows": table,
    }
    if arguments.check:
        retained = json.loads(arguments.out.read_text())
        if not _same(json.loads(json.dumps(record)), retained):
            print("simulation differs from the retained file", file=sys.stderr)
            return 1
        print("simulation matches the retained file")
        return 0
    if arguments.out.exists() and not arguments.overwrite:
        print(f"{arguments.out} exists; pass --overwrite to replace it", file=sys.stderr)
        return 2
    arguments.out.write_text(json.dumps(record, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
