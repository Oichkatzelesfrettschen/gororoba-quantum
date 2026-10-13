"""Nested likelihood fits of the six orbit distributions of this record.

Each context (nominal, window_barrier, window_echo) fits its feedback and
no-feedback arms jointly. The exact law prepares e1 in the order-3 orbit
{1, 4, 16}; round 1 applies controlled U^2 with kickback phase phi1, the
control is measured to b0, and round 2 applies controlled U with kickback
phase phi2 and the (-i)^b0 correction on the feedback arm. A global
depolarization lam mixes toward uniform; e0 and e1 are 1 -> 0 report flips
on b0 and b1. Models: bias (lam, e0, e1) and phase+bias (adds phi1, phi2).
Usage: python orbit_refit.py RECORD_DIR
"""

import itertools
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize
from scipy.stats import chi2

U = np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]], dtype=complex)
E1 = np.array([1, 0, 0], dtype=complex)


def law(phi1: float, phi2: float, feedback: bool) -> np.ndarray:
    p = np.zeros(4)
    for b0, b1 in itertools.product((0, 1), repeat=2):
        v = (np.eye(3) + (-1) ** b0 * np.exp(1j * phi1) * U @ U) @ E1
        corr = (-1j) ** b0 if feedback else 1
        a = (np.eye(3) + (-1) ** b1 * np.exp(1j * phi2) * corr * U) @ v
        p[b0 + 2 * b1] = np.vdot(a, a).real / 16
    return p


def observe(p: np.ndarray, lam: float, e0: float, e1: float) -> np.ndarray:
    q = (1 - lam) * p + lam / 4
    out = np.zeros(4)
    for k in range(4):
        b0, b1 = k & 1, k >> 1
        for r0 in ((b0,) if b0 == 0 else (1, 0)):
            for r1 in ((b1,) if b1 == 0 else (1, 0)):
                w = (1 - e0 if (b0 and r0) else e0 if b0 else 1) * (1 - e1 if (b1 and r1) else e1 if b1 else 1)
                out[r0 + 2 * r1] += q[k] * w
    return out


def nll(theta: np.ndarray, counts: dict[bool, np.ndarray], phase: bool) -> float:
    phi1, phi2 = (theta[3], theta[4]) if phase else (0.0, 0.0)
    lam, e0, e1 = theta[:3]
    total = 0.0
    for fb, n in counts.items():
        q = np.clip(observe(law(phi1, phi2, fb), lam, e0, e1), 1e-12, 1)
        total -= float(n @ np.log(q))
    return total


def fit(counts: dict[bool, np.ndarray], phase: bool) -> tuple[float, list[float]]:
    bounds = [(0, 1), (0, 0.5), (0, 0.5)] + ([(-np.pi, np.pi)] * 2 if phase else [])
    best = None
    starts = [(0.1, 0.02, 0.02, a, b) for a in np.linspace(-3, 3, 7) for b in np.linspace(-3, 3, 7)] if phase else [(0.1, 0.02, 0.02)]
    for s in starts:
        r = minimize(nll, np.array(s), args=(counts, phase), bounds=bounds, method="L-BFGS-B")
        if best is None or r.fun < best.fun:
            best = r
    return float(best.fun), [float(x) for x in best.x]


def main() -> None:
    record = Path(sys.argv[1])
    fm = json.loads((record / "collect.json").read_text())[0]["family_measurements"]
    out = {}
    for ctx in ("nominal", "window_barrier", "window_echo"):
        counts = {}
        for fb in (True, False):
            m = fm[f"orbit_{ctx}_{'feedback' if fb else 'no_feedback'}"]
            counts[fb] = np.rint(np.array(m["replica_probabilities"][0]) * m["execution"]["shots"])
        sat = -sum(float(n @ np.log(np.clip(n / n.sum(), 1e-12, 1))) for n in counts.values())
        b_nll, b_x = fit(counts, False)
        p_nll, p_x = fit(counts, True)
        lr = 2 * (b_nll - p_nll)
        out[ctx] = {
            "bias": {"params": dict(zip(("lam", "e0", "e1"), b_x)), "deviance": 2 * (b_nll - sat), "dof": 6 - 3},
            "phase_bias": {"params": dict(zip(("lam", "e0", "e1", "phi1", "phi2"), p_x)), "deviance": 2 * (p_nll - sat), "dof": 6 - 5},
            "phase_lr": lr,
            "phase_lr_p": float(chi2.sf(max(lr, 0), 2)),
        }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
