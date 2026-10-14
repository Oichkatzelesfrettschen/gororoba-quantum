"""Nested likelihood fits of the six orbit distributions of this record.

Each context (nominal, window_barrier, window_echo) fits its feedback and
no-feedback arms jointly. The exact law prepares e1 in the order-3 orbit
{1, 4, 16}; round 1 applies controlled U^2 with kickback phase phi1, the
control is measured to b0, and round 2 applies controlled U with kickback
phase phi2 and the (-i)^b0 correction on the feedback arm. A global
depolarization lam mixes toward uniform; e0 and e1 are 1 -> 0 report flips
on b0 and b1. Models: bias (lam, e0, e1); phase+bias (adds phi1, phi2); arm
bias (lam and e1 per arm, shared e0), a non-phase model with the phase+bias
parameter count. Across contexts, one shared (phi1, phi2) with per-context
nuisances is tested against per-context phases (likelihood ratio, 4 dof),
and each context's profile deviance over a (phi1, phi2) grid gives its 95%
region (chi-square, 2 dof) and its deviance at the other contexts' optima.
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


def arm_nll(theta: np.ndarray, counts: dict[bool, np.ndarray]) -> float:
    lam_f, lam_n, e0, e1_f, e1_n = theta
    total = 0.0
    for fb, n in counts.items():
        q = np.clip(observe(law(0.0, 0.0, fb), lam_f if fb else lam_n, e0, e1_f if fb else e1_n), 1e-12, 1)
        total -= float(n @ np.log(q))
    return total


def nuisance_nll(counts: dict[bool, np.ndarray], phi1: float, phi2: float) -> float:
    def f(x: np.ndarray) -> float:
        return nll(np.array([*x, phi1, phi2]), counts, True)

    return float(minimize(f, np.array([0.15, 0.04, 0.06]), bounds=[(0, 1), (0, 0.5), (0, 0.5)], method="L-BFGS-B").fun)


GRID = np.linspace(-np.pi, np.pi, 37)[:-1]
CHI2_2_95 = float(chi2.ppf(0.95, 2))


def main() -> None:
    record = Path(sys.argv[1])
    fm = json.loads((record / "collect.json").read_text())[0]["family_measurements"]
    out: dict = {"contexts": {}}
    data = {}
    for ctx in ("nominal", "window_barrier", "window_echo"):
        counts = {}
        for fb in (True, False):
            m = fm[f"orbit_{ctx}_{'feedback' if fb else 'no_feedback'}"]
            counts[fb] = np.rint(np.array(m["replica_probabilities"][0]) * m["execution"]["shots"])
        data[ctx] = counts
        sat = -sum(float(n @ np.log(np.clip(n / n.sum(), 1e-12, 1))) for n in counts.values())
        b_nll, b_x = fit(counts, False)
        p_nll, p_x = fit(counts, True)
        arm = min(
            (
                minimize(arm_nll, np.array(s0), args=(counts,), bounds=[(0, 1), (0, 1), (0, 0.5), (0, 0.5), (0, 0.5)])
                for s0 in ((0.1, 0.1, 0.02, 0.02, 0.02), (0.3, 0.3, 0.05, 0.08, 0.08), (0.2, 0.4, 0.04, 0.1, 0.03))
            ),
            key=lambda r: r.fun,
        )
        surface = np.array([[nuisance_nll(counts, a, b) for b in GRID] for a in GRID])
        best = float(surface.min())
        region = [(float(GRID[i]), float(GRID[j])) for i, j in zip(*np.where(2 * (surface - best) <= CHI2_2_95), strict=True)]
        out["contexts"][ctx] = {
            "bias": {"params": dict(zip(("lam", "e0", "e1"), b_x)), "deviance": 2 * (b_nll - sat), "dof": 3},
            "phase_bias": {"params": dict(zip(("lam", "e0", "e1", "phi1", "phi2"), p_x)), "deviance": 2 * (p_nll - sat), "dof": 1},
            "arm_bias": {
                "params": dict(zip(("lam_fb", "lam_nf", "e0", "e1_fb", "e1_nf"), map(float, arm.x))),
                "deviance": 2 * (float(arm.fun) - sat),
                "dof": 1,
            },
            "phase_lr": 2 * (b_nll - p_nll),
            "phase_lr_p": float(chi2.sf(max(2 * (b_nll - p_nll), 0), 2)),
            "phase_region_95_grid": region,
            "phase_region_fraction": len(region) / GRID.size**2,
            "_surface": surface,
        }
    for ctx, entry in out["contexts"].items():
        surface = entry.pop("_surface")
        entry["profile_deviance_at_other_optima"] = {}
        for other, oentry in out["contexts"].items():
            if other == ctx:
                continue
            phi = oentry["phase_bias"]["params"]
            entry["profile_deviance_at_other_optima"][other] = 2 * (
                nuisance_nll(data[ctx], phi["phi1"], phi["phi2"]) - surface.min()
            )
    per_context = sum(fit(data[c], True)[0] for c in data)

    def shared(x: np.ndarray) -> float:
        return sum(nuisance_nll(data[c], x[0], x[1]) for c in data)

    shared_best = min(
        (minimize(shared, np.array([a, b]), method="Nelder-Mead") for a in np.linspace(-2.5, 2.5, 5) for b in np.linspace(-2.5, 2.5, 5)),
        key=lambda r: r.fun,
    )
    lr = 2 * (float(shared_best.fun) - per_context)
    out["shared_vs_per_context_phase"] = {
        "shared_phases": [float(v) for v in shared_best.x],
        "lr": lr,
        "dof": 4,
        "p": float(chi2.sf(max(lr, 0), 4)),
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
