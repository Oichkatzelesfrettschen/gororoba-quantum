"""Per-round single-exponential T1 of the interleaved Tuna-17 series: a descriptive split written after the analysis.

The registered analysis (scripts/qi_tuna17_interleaved_cases.py, --analyze) rejects its replicate check on 16 of 17
qubits: the three rounds of one delay multiplier disagree beyond their variance. Each round holds all six multipliers in
about six minutes. The split asks two questions per qubit: does T1 differ between rounds, and does one exponential
describe each round alone? For each qubit and round it fits the registered single exponential to the round's six
anchored points (the anchored_point and fit_shape the analysis uses) and takes the standard error of T from the
curvature of the weighted sum of squares. Because many round fits fail their lack-of-fit test, the error is also
reported scaled by sqrt(chi-square / dof) where that ratio exceeds one, and the between-round chi-square (two degrees of
freedom against one common T) is given with both errors. The split is post hoc and decides nothing.

Usage: python3 docs/evidence/qi-tuna17-interleaved-rounds/round_fits.py OUT.json
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import qi_tuna17_interleaved_cases as case  # noqa: E402

from parallel import ordered_map  # noqa: E402

RUNS = "results/quantum_inspire/runs"
PATTERN = "2026-11-19T1735Z-t17-characterization_interleaved_tuna_17-interleaved_t1-batch-*"
LACK_OF_FIT = 0.01


def round_fit(points: list[tuple[float, float, float]]) -> dict[str, Any]:
    """Single-exponential fit of one round's (t_us, x, variance) points with the curvature standard error of T and the
    same error scaled by sqrt(chi-square / dof) when that ratio exceeds one."""
    fit = case.fit_shape(points, "single")
    t1 = float(fit["params"][0])

    def wss(value: float) -> float:
        return sum((x - math.exp(-t / value)) ** 2 / v for t, x, v in points)

    step = 1e-3 * t1
    curvature = (wss(t1 + step) - 2 * wss(t1) + wss(t1 - step)) / step**2
    if curvature <= 0:
        raise ValueError("the weighted sum of squares is not convex at the fitted T")
    se = math.sqrt(2 / curvature)
    chi, dof = float(fit["chi_square"]), int(fit["dof"])
    return {
        "t1_us": t1,
        "se_us": se,
        "scaled_se_us": se * math.sqrt(max(1.0, chi / dof)),
        "chi_square": chi,
        "dof": dof,
        "probability": float(fit["probability"]),
    }


def between(rounds: dict[str, dict[str, Any]], key: str) -> dict[str, float]:
    """Inverse-variance mean of the round T values and its chi-square against one common T, with errors from key."""
    values = [r["t1_us"] for r in rounds.values()]
    weights = [1 / r[key] ** 2 for r in rounds.values()]
    mean = sum(w * t for w, t in zip(weights, values, strict=True)) / sum(weights)
    chi = sum(w * (t - mean) ** 2 for w, t in zip(weights, values, strict=True))
    return {
        "mean_t1_us": mean,
        "chi_square": chi,
        "probability": case.base.chi_square_probability(chi, len(values) - 1),
    }


class QubitRounds:
    """Per-round fits of one qubit over the interleaved batches; holds only its inputs so it pickles for ordered_map."""

    def __init__(self, batches: list[dict[str, Any]], roles: list[Any]) -> None:
        self.batches = batches
        self.roles = roles

    def __call__(self, qubit: int) -> dict[str, Any]:
        batches, roles = self.batches, self.roles
        count = batches[0]["shots"]
        a0s = [b["p1"][r[0]][qubit] for b, r in zip(batches, roles, strict=True)]
        a1s = [b["p1"][r[1]][qubit] for b, r in zip(batches, roles, strict=True)]
        tau2 = case.job_level_variance(a0s, a1s, count)
        by_round: dict[int, list[tuple[float, float, float]]] = {}
        starts: dict[int, list[str]] = {}
        for batch, role, a0, a1 in zip(batches, roles, a0s, a1s, strict=True):
            point = case.anchored_point(batch["p1"][role[2]][qubit], a0, a1, count, tau2)
            if point is None:
                continue
            cycles = batch["rows"][role[2]]["delays_cycles"][qubit]
            index = int(batch["meta"]["round"])
            by_round.setdefault(index, []).append((cycles * case.CYCLE_SECONDS * 1e6, point[0], point[1]))
            started = batch.get("started", {}).get(role[2])
            if started:
                starts.setdefault(index, []).append(started)
        rounds = {
            str(k): round_fit(v) | {"first_start": min(starts.get(k, [""])), "last_start": max(starts.get(k, [""]))}
            for k, v in sorted(by_round.items())
        }
        values = [r["t1_us"] for r in rounds.values()]
        return {
            "qubit": qubit,
            "rounds": rounds,
            "between_rounds_fit_errors": between(rounds, "se_us"),
            "between_rounds_scaled_errors": between(rounds, "scaled_se_us"),
            "largest_round_ratio": max(values) / min(values),
        }


def main(out: Path) -> None:
    runs = sorted((ROOT / RUNS).glob(PATTERN))
    if len(runs) != 18:
        raise SystemExit(f"want 18 interleaved_t1 runs, found {len(runs)}")
    batches = case.read_batches(runs)
    roles = [case.interleaved_roles(b) for b in batches]
    rows = ordered_map(QubitRounds(batches, roles), list(range(batches[0]["nqubits"])), min_items=2)
    fits = [r2 for r in rows for r2 in r["rounds"].values()]
    record = {
        "schema": "qi-tuna17-interleaved-round-fits-v2",
        "source": "scripts/qi_tuna17_interleaved_cases.py anchored_point and fit_shape",
        "lack_of_fit_threshold": LACK_OF_FIT,
        "qubits": rows,
        "round_fits": len(fits),
        "round_single_exponential_accepted": sum(f["probability"] >= LACK_OF_FIT for f in fits),
        "between_rounds_rejected_fit_errors": sum(
            r["between_rounds_fit_errors"]["probability"] < LACK_OF_FIT for r in rows
        ),
        "between_rounds_rejected_scaled_errors": sum(
            r["between_rounds_scaled_errors"]["probability"] < LACK_OF_FIT for r in rows
        ),
    }
    out.write_text(json.dumps(record, indent=1) + "\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(Path(sys.argv[1]))
