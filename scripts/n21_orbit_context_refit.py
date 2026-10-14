"""Identifiable refit of the N=21 orbit distributions across window contexts.

The order-3 orbit law with kickback phases phi1 (round 1) and phi2 (round 2)
has amplitude (1 + s t) e1 + t e4 + s e16 for s = (-1)^b0 e^{i phi1},
t = (-1)^b1 e^{i phi2} c_b0 (c = (-i)^b0 with feedback, 1 without), so
every outcome probability depends only on theta = phi1 + phi2:

    p_F(theta) = (2 + cos theta, 2 - sin theta, 2 - cos theta, 2 + sin theta) / 8
    p_N(theta) = (2 + cos theta, 2 - cos theta, 2 - cos theta, 2 + cos theta) / 8

in outcome order b0 + 2 b1. (phi1 + x, phi2 - x) leaves the law unchanged
for every x, so only theta is fitted. Observation nuisances: depolarization
lam toward uniform and 1 -> 0 flips e0, e1 of the reported bits, applied
after the feedback law (e0 relabels the reported first bit; it does not
model a misclassification that selects the wrong correction).

Models per context (both arms jointly, six cell dimensions):
- bias (lam, e0, e1): 3 identifiable parameters;
- phase (lam, e0, e1, theta): 4;
- causal saturated: the two arms share their first-bit marginal (b0 is
  measured before the arms diverge) and are otherwise free: 5. Its deviance
  is the first-bit homogeneity G^2.

Across contexts, one shared theta against per-context theta differs by 2
dimensions. Likelihood ratios are reported with their dimension differences
and, with --bootstrap N, a parametric bootstrap of the shared-theta test;
no chi-square p-value is reported as calibrated.

Counts come from the raw ledger through patch_window_analysis._bound_counts.
--self-check runs the identifiability tests on synthetic data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import brentq, minimize

sys.path.insert(0, str(Path(__file__).resolve().parent))
CONTEXTS = ("nominal", "window_barrier", "window_echo")
THETA_STARTS = np.linspace(-math.pi, math.pi, 13)[:-1]


def law(theta: float, feedback: bool) -> np.ndarray:
    second = math.sin(theta) if feedback else math.cos(theta)
    return np.array([2 + math.cos(theta), 2 - second, 2 - math.cos(theta), 2 + second]) / 8


def two_phase_law(phi1: float, phi2: float, feedback: bool) -> np.ndarray:
    """The unreduced orbit amplitude; used only to certify the reduction to theta."""
    u = np.array([[0, 0, 1], [1, 0, 0], [0, 1, 0]], dtype=complex)
    e1 = np.array([1, 0, 0], dtype=complex)
    p = np.zeros(4)
    for b0 in (0, 1):
        for b1 in (0, 1):
            s = (-1) ** b0 * np.exp(1j * phi1)
            t = (-1) ** b1 * np.exp(1j * phi2) * ((-1j) ** b0 if feedback else 1)
            amp = (np.eye(3) + t * u) @ (np.eye(3) + s * u @ u) @ e1
            p[b0 + 2 * b1] = float(np.vdot(amp, amp).real) / 16
    return p


def observe(p: np.ndarray, lam: float, e0: float, e1: float) -> np.ndarray:
    q = (1 - lam) * p + lam / 4
    out = np.zeros(4)
    for k in range(4):
        b0, b1 = k & 1, k >> 1
        for r0 in (0, 1):
            w0 = (1.0 if r0 == 0 else 0.0) if b0 == 0 else (e0 if r0 == 0 else 1 - e0)
            for r1 in (0, 1):
                w1 = (1.0 if r1 == 0 else 0.0) if b1 == 0 else (e1 if r1 == 0 else 1 - e1)
                out[r0 + 2 * r1] += q[k] * w0 * w1
    return out


def nll(params: np.ndarray, counts: dict[bool, np.ndarray], phase: bool) -> float:
    lam, e0, e1 = params[:3]
    theta = float(params[3]) if phase else 0.0
    total = 0.0
    for feedback, n in counts.items():
        q = np.clip(observe(law(theta, feedback), lam, e0, e1), 1e-12, 1.0)
        total -= float(n @ np.log(q))
    return total


NUISANCE_BOUNDS = [(0.0, 1.0), (0.0, 0.5), (0.0, 0.5)]


def fit(counts: dict[bool, np.ndarray], phase: bool, theta: float | None = None) -> tuple[float, list[float]]:
    """Multistart bounded fit; theta fixed when given. Raises unless an optimizer run converges."""
    best = None
    nuisance_starts = [np.array(v) for v in ((0.15, 0.04, 0.06), (0.3, 0.02, 0.1), (0.05, 0.1, 0.02))]
    if theta is not None:
        starts = nuisance_starts

        def objective(x: np.ndarray) -> float:
            return nll(np.array([*x, theta]), counts, True)

        bounds = NUISANCE_BOUNDS
    else:
        starts = [np.array([*n, t]) for n in nuisance_starts[:1] for t in THETA_STARTS] if phase else nuisance_starts

        def objective(x: np.ndarray) -> float:
            return nll(x, counts, phase)

        bounds = NUISANCE_BOUNDS + ([(-2 * math.pi, 2 * math.pi)] if phase else [])
    for start in starts:
        for method in ("L-BFGS-B", "Powell"):
            result = minimize(objective, start, bounds=bounds, method=method)
            if result.success and (best is None or result.fun < best.fun):
                best = result
    if best is None:
        raise RuntimeError("no optimizer start converged")
    x = [float(v) for v in best.x]
    if phase and theta is None:
        x[3] = math.remainder(x[3], 2 * math.pi)
    return float(best.fun), x


def saturated_nll(counts: dict[bool, np.ndarray]) -> float:
    return -sum(float(n @ np.log(np.clip(n / n.sum(), 1e-300, 1.0))) for n in counts.values())


def causal_saturated_deviance(counts: dict[bool, np.ndarray]) -> float:
    """First-bit homogeneity G^2: both arms share P(b0) and are otherwise free."""
    table = np.array([[n[0] + n[2], n[1] + n[3]] for n in counts.values()], dtype=float)
    expected = table.sum(1, keepdims=True) * table.sum(0, keepdims=True) / table.sum()
    mask = table > 0
    return float(2 * (table[mask] * np.log(table[mask] / expected[mask])).sum())


def profile(counts: dict[bool, np.ndarray], theta_hat: float, best: float, grid: int = 72) -> list[list[float]]:
    """Arcs of theta whose profile deviance stays within 3.84 of the optimum.

    A grid centered on theta_hat brackets each boundary, and brentq places it
    to 1e-6 rad; each arc runs counterclockwise from its first to its second
    endpoint, both reduced to (-pi, pi].
    """
    thetas = theta_hat + np.linspace(-math.pi, math.pi, grid, endpoint=False)

    def excess(t: float) -> float:
        return 2 * (fit(counts, True, theta=t)[0] - best) - 3.84

    inside = [excess(float(t)) <= 0 for t in thetas]
    if all(inside):
        return [[-math.pi, math.pi]]
    first_out = inside.index(False)
    arcs = []
    for step in range(1, grid + 1):
        i, j = (first_out + step - 1) % grid, (first_out + step) % grid
        lo, hi = float(thetas[i]), float(thetas[i]) + 2 * math.pi / grid
        if not inside[i] and inside[j]:
            arcs.append([math.remainder(brentq(excess, lo, hi, xtol=1e-6), 2 * math.pi)])
        elif inside[i] and not inside[j]:
            arcs[-1].append(math.remainder(brentq(excess, lo, hi, xtol=1e-6), 2 * math.pi))
    return arcs


def analyze(contexts: dict[str, dict[bool, np.ndarray]], bootstrap: int = 0, seed: int = 20261014) -> dict[str, Any]:
    out: dict[str, Any] = {"contexts": {}}
    per_context = 0.0
    for name, counts in contexts.items():
        sat = saturated_nll(counts)
        bias_nll, bias_x = fit(counts, False)
        phase_nll, phase_x = fit(counts, True)
        causal = causal_saturated_deviance(counts)
        phase_dev = 2 * (phase_nll - sat)
        out["contexts"][name] = {
            "bias": {"params": dict(zip(("lam", "e0", "e1"), bias_x, strict=True)), "deviance": 2 * (bias_nll - sat)},
            "phase": {
                "params": dict(zip(("lam", "e0", "e1", "theta"), phase_x, strict=True)),
                "deviance": phase_dev,
                "theta_region_arcs": profile(counts, phase_x[3], phase_nll),
            },
            "causal_saturated_deviance": causal,
            "phase_excess_over_causal": phase_dev - causal,
            "aic": {"bias": 2 * (bias_nll - sat) + 6, "phase": phase_dev + 8, "causal_saturated": causal + 10},
            "dimensions": {"bias": 3, "phase": 4, "causal_saturated": 5, "saturated": 6},
        }
        per_context += phase_nll

    shared_theta, shared_nll = fit_shared(contexts, THETA_STARTS)
    lr = 2 * (shared_nll - per_context)
    test: dict[str, Any] = {"shared_theta": shared_theta, "lr": lr, "dimension_difference": len(contexts) - 1}
    if bootstrap:
        rng = np.random.default_rng(seed)
        nuisances = {c: fit(counts, True, theta=shared_theta)[1] for c, counts in contexts.items()}
        exceed = 0
        for _ in range(bootstrap):
            synthetic = {
                c: {
                    fb: rng.multinomial(int(n.sum()), observe(law(shared_theta, fb), *nuisances[c])).astype(float)
                    for fb, n in counts.items()
                }
                for c, counts in contexts.items()
            }
            alternative = sum(fit(synthetic[c], True)[0] for c in synthetic)
            null = fit_shared(synthetic, np.array([shared_theta]))[1]
            exceed += 2 * (null - alternative) >= lr
        test["bootstrap"] = {"replicates": bootstrap, "seed": seed, "replicates_reaching_lr": int(exceed)}
    out["shared_vs_per_context_theta"] = test
    return out


def fit_shared(contexts: dict[str, dict[bool, np.ndarray]], starts: np.ndarray) -> tuple[float, float]:
    """One theta shared by every context, nuisances free per context; returns (theta, negative log-likelihood)."""

    def objective(x: np.ndarray) -> float:
        return sum(fit(counts, True, theta=float(x[0]))[0] for counts in contexts.values())

    best = min((minimize(objective, np.array([t]), method="Nelder-Mead") for t in starts), key=lambda r: r.fun)
    return math.remainder(float(best.x[0]), 2 * math.pi), float(best.fun)


def counts_from_record(run: Path) -> dict[str, dict[bool, np.ndarray]]:
    from patch_window_analysis import _bound_counts

    raw = _bound_counts(run)
    contexts = {}
    for context in CONTEXTS:
        arms = {}
        for feedback in (True, False):
            histogram = raw[f"orbit_{context}_{'feedback' if feedback else 'no_feedback'}"]
            arms[feedback] = np.array([histogram.get(format(label, "02b"), 0) for label in range(4)], dtype=float)
        contexts[context] = arms
    return contexts


def self_check() -> None:
    rng = np.random.default_rng(7)
    for _ in range(200):
        p1, p2, x = rng.uniform(-math.pi, math.pi, 3)
        for feedback in (True, False):
            reduced = law(p1 + p2, feedback)
            if not (
                np.allclose(two_phase_law(p1, p2, feedback), reduced, atol=1e-12)
                and np.allclose(two_phase_law(p1 + x, p2 - x, feedback), reduced, atol=1e-12)
            ):
                raise RuntimeError("the orbit law is not a function of phi1 + phi2")

    def jacobian_rank(f: Any, x: list[float]) -> int:
        x0 = np.array(x)
        columns = [(f(x0 + h) - f(x0 - h)) / 2e-6 for h in np.eye(len(x0)) * 1e-6]
        singular = np.linalg.svd(np.array(columns).T, compute_uv=False)
        return int((singular > 1e-7 * singular[0]).sum())

    def phase_two(x: np.ndarray) -> np.ndarray:
        return np.concatenate([observe(two_phase_law(x[3], x[4], fb), x[0], x[1], x[2]) for fb in (True, False)])

    def arm(x: np.ndarray) -> np.ndarray:
        return np.concatenate(
            [observe(law(0.0, fb), x[0] if fb else x[1], x[2], x[3] if fb else x[4]) for fb in (True, False)]
        )

    if (
        jacobian_rank(phase_two, [0.2, 0.05, 0.07, 0.4, -0.9]) != 4
        or jacobian_rank(arm, [0.2, 0.3, 0.05, 0.07, 0.09]) != 5
    ):
        raise RuntimeError("model dimensions differ from 4 (phase) and 5 (arm bias)")
    planted = 0.6
    counts = {
        fb: rng.multinomial(400_000, observe(law(planted, fb), 0.1, 0.03, 0.05)).astype(float) for fb in (True, False)
    }
    best, params = fit(counts, True)
    theta = params[3]
    if abs(math.remainder(theta - planted, 2 * math.pi)) > 0.05:
        raise RuntimeError(f"planted theta {planted} recovered as {theta}")
    arcs = profile(counts, theta, best)
    if len(arcs) != 1 or not arcs[0][0] < theta < arcs[0][1]:
        raise RuntimeError(f"the profile region {arcs} does not bracket the estimate {theta}")
    for edge in arcs[0]:
        if abs(2 * (fit(counts, True, theta=edge)[0] - best) - 3.84) > 1e-3:
            raise RuntimeError("a profile endpoint misses the 3.84 deviance boundary")
    if causal_saturated_deviance(counts) > 15:
        raise RuntimeError("causally consistent synthetic data fail first-bit homogeneity")


def replicates(text: str) -> int:
    value = int(text)
    if value < 0:
        raise argparse.ArgumentTypeError("the replicate count is a nonnegative integer")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run", nargs="?", type=Path, help="collected record directory")
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--bootstrap", type=replicates, default=0, help="parametric bootstrap replicates (0 skips)")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    if args.self_check:
        self_check()
        print("orbit context refit: theta-only law, dimensions 4 and 5, planted theta and profile boundary recovered")
        return 0
    if args.run is None:
        parser.error("a record directory or --self-check is required")
    contexts = counts_from_record(args.run)
    result = analyze(contexts, args.bootstrap)
    script = Path(__file__).resolve()
    commit = subprocess.run(
        ["git", "-C", str(script.parent), "log", "-1", "--format=%H", "--", script.name],
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()
    result["provenance"] = {
        "script": "scripts/n21_orbit_context_refit.py",
        "script_sha256": hashlib.sha256(script.read_bytes()).hexdigest(),
        "script_last_commit": commit or None,
        "inputs_sha256": {
            name: hashlib.sha256((args.run / name).read_bytes()).hexdigest() for name in ("record.json", "collect.json")
        },
        "counts_order": "outcome index b0 + 2 b1",
        "counts": {
            c: {("feedback" if fb else "no_feedback"): [int(x) for x in n] for fb, n in arms.items()}
            for c, arms in contexts.items()
        },
    }
    text = json.dumps(result, indent=1) + "\n"
    if args.out:
        args.out.write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
