"""Seeded simulation of the Stein two-stage rule of the replicated Tuna-17 matched-response design.

Draws replicate residuals r_i = delta + sigma z_i (z standard normal, common random numbers across delta) for
each sigma, applies gororoba_quantum/qi_replicated_response.py (required_replicates, stein_statistic, CAP,
T_CRIT) to each trial and writes the rejection, undecided-at-cap and uncapped-rule rates. The uncapped column
removes the cap: the first N1 residuals are drawn, N follows from their SD, and the mean of all N residuals
follows from the first-stage sum plus a normal draw for the other N - N1 residuals, so the level and power
of the rule itself are read without the cap.

Seeds: docs/evidence/anu_qrng/draw-2026-11-22T010305Z.json, indices 8, 9, 10, 11 in order.
Usage: "$PYTHON" scripts/qi_replicated_stein_simulation.py [--trials N] [--out FILE]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import qi_replicated_response as rule  # noqa: E402

SIGMAS = (0.01, 0.02, 0.038, 0.08)
SIMULATION_SEEDS = (34644, 40029, 46414, 54363)
TRIALS = 400000
OUT = ROOT / "docs/evidence/quantum_inspire/tuna17-replicated-stein-simulation.json"


def simulate(sigma: float, deltas: tuple[float, ...], trials: int, seed: int) -> list[dict[str, Any]]:
    """Rates of the capped design and of the uncapped rule at one residual SD, for each effect delta."""
    rng = np.random.default_rng(seed)
    z = rng.standard_normal((trials, rule.CAP))
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
                "reject_uncapped_rule": float(uncapped.mean()),
                "median_required_total": float(np.median(required)),
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=TRIALS)
    parser.add_argument("--out", type=Path, default=OUT)
    arguments = parser.parse_args()
    table = []
    for sigma, seed in zip(SIGMAS, SIMULATION_SEEDS, strict=True):
        table += simulate(sigma, (0.0, -rule.DELTA), arguments.trials, seed)
    record = {
        "schema": "qi-replicated-stein-simulation-v1",
        "rule": {"n1": rule.N1, "cap": rule.CAP, "alpha": rule.ALPHA, "power": rule.POWER, "c": rule.C},
        "seed_draw": "docs/evidence/anu_qrng/draw-2026-11-22T010305Z.json",
        "seed_indices": [8, 9, 10, 11],
        "rows": table,
    }
    arguments.out.write_text(json.dumps(record, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
