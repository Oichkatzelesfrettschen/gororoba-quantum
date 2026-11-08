"""C1 observed-side tests: statistics, drift, slot offset, multiphoton, repeat identity, predecessor scatter."""

import importlib
from functools import partial
from pathlib import Path
from typing import Any

import numpy as np
from c1_common import MIRROR, bootstrap_diffs, observed_rows, settings, signed_diffs
from c1_mesh import PAIRS, cached
from scipy import stats

HERE = Path(__file__).resolve().parent
# c1_common (through c1_mesh) puts gororoba_quantum/ on sys.path, so parallel resolves only after that import.
parallel = importlib.import_module("parallel")


def main() -> None:
    rows = observed_rows()
    keys, d, table, cal = signed_diffs(rows)
    n = len(keys)
    print(
        f"pairs {n}; failing {(abs(d) > MIRROR).sum()}; |d| median {np.median(abs(d)):.4f} max {abs(d).max():.4f}; rms {np.sqrt(np.mean(d**2)):.4f}"
    )

    # ---- pure statistics: parametric bootstrap of the 12-mode counts (calibration included)
    # QRNG seed: docs/evidence/anu_qrng/draw-2026-10-25T015224Z.json index 2
    rng = np.random.default_rng(34782)
    counts = np.array([r["port_counts"] for r in rows], float)
    B = 600
    # Every replicate's draws are taken first in the scalar loop's order (replicate, then row), so the scoring maps through
    # parallel.py and the bootstrap keeps its bits.
    draws = [[rng.multinomial(int(c.sum()), c / c.sum()) for c in counts] for _draw in range(B)]
    sims: Any = np.array(parallel.ordered_map(partial(bootstrap_diffs, rows), draws))
    se = sims.std(axis=0)
    z = d / se
    print(f"bootstrap se of a mirror difference: median {np.median(se):.4f} range {se.min():.4f}-{se.max():.4f}")
    print(
        f"z = d/se: rms {np.sqrt(np.mean(z**2)):.2f}; chi2 {np.sum(z**2):.0f} on {n} dof; p {stats.chi2.sf(np.sum(z**2), n):.2e}; |z|>3: {(abs(z) > 3).sum()}"
    )
    print(
        f"under pure statistics (bootstrap about observed) |d| median {np.median(abs(sims - sims.mean(0))):.4f}, P(|d|>0.07 for a pair) mean {(abs(sims - sims.mean(0)) > MIRROR).mean():.4f}"
    )

    # ---- slot offset decomposition: item 0 vs item 1 antisymmetry
    item = np.array([k[1] for k in keys])
    sgn = np.where(item == 0, 1.0, -1.0)
    ideal = np.array(
        [[s for s in settings if s["setting"] == k[0]][0]["slots"]["AB"[k[1]]]["ideal_level"] for k in keys]
    )
    c_mean = np.mean(d * sgn)
    print(
        f"item0 mean d {d[item == 0].mean():+.4f} (n {int((item == 0).sum())}), item1 mean d {d[item == 1].mean():+.4f}; slot-offset estimate c = mean(sgn*d) {c_mean:+.4f} +- {np.std(d * sgn, ddof=1) / np.sqrt(n):.4f}"
    )
    print(
        f"after removing c: residual rms {np.sqrt(np.mean((d - c_mean * sgn) ** 2)):.4f}; |resid|>0.07: {(abs(d - c_mean * sgn) > MIRROR).sum()}; residual chi2 {np.sum(((d - c_mean * sgn) / se) ** 2):.0f}"
    )
    # gain version: d = sgn*(c0 + c1*ideal)
    X = np.c_[sgn, sgn * ideal]
    beta, *_ = np.linalg.lstsq(X, d, rcond=None)
    res = d - X @ beta
    print(
        f"offset+gain slot model beta {beta.round(4)}; resid rms {np.sqrt(np.mean(res**2)):.4f}; chi2 {np.sum((res / se) ** 2):.0f}"
    )

    # ---- time separation (drift)
    i0 = np.array([table[k][0][0] for k in keys])
    i1 = np.array([table[k][1][0] for k in keys])
    sep = np.abs(i0 - i1)
    dt = i0 - i1  # iteration units; 3.1 s each
    rho = stats.spearmanr(sep, abs(d))
    print(
        f"separation (iterations) range {sep.min()}-{sep.max()}; spearman(|d|, separation) {rho.statistic:+.3f} p {rho.pvalue:.3f}"
    )
    X = np.c_[dt, sgn]
    beta, *_ = np.linalg.lstsq(X, d, rcond=None)
    res = d - X @ beta
    print(
        f"signed d ~ b*(i0-i1) + c*sgn: b {beta[0]:+.2e}/iteration (x52 = {beta[0] * 52:+.4f} over the job), c {beta[1]:+.4f}; resid rms {np.sqrt(np.mean(res**2)):.4f}; R2 vs d {1 - res.var() / d.var():.3f}"
    )
    rho2 = stats.spearmanr(dt, d)
    print(f"spearman(signed d, i0-i1) {rho2.statistic:+.3f} p {rho2.pvalue:.3f}")
    near = sep <= 10
    far = sep >= 30
    print(
        f"|d| rms: separation<=10 (n {near.sum()}) {np.sqrt(np.mean(d[near] ** 2)):.4f}; >=30 (n {far.sum()}) {np.sqrt(np.mean(d[far] ** 2)):.4f}"
    )
    # time series of the repeated anchors/darks: identical configs at i and 51-i
    for a, b in ((0, 51), (1, 50), (2, 49)):
        ra, rb = rows[a], rows[b]
        sa, sb = settings[a], settings[b]
        same = sa["circuit_params"] == sb["circuit_params"]
        print(
            f"repeat iterations {a} and {b}: same circuit_params {same}; slot A {ra['slot']['A'] / ra['total']:.5f} vs {rb['slot']['A'] / rb['total']:.5f}; slot B {ra['slot']['B'] / ra['total']:.5f} vs {rb['slot']['B'] / rb['total']:.5f}; failure {ra['failure'] / ra['total']:.5f} vs {rb['failure'] / rb['total']:.5f}"
        )
    k, lo, th, ph, perf = cached(PAIRS, "pairs")
    for a, b in ((0, 51), (1, 50), (2, 49)):
        print(
            f"compiled mesh iterations {a}/{b}: max |dphi| {np.abs(np.angle(np.exp(1j * (ph[a] - ph[b])))).max():.3e}, max |dtheta| {np.abs(th[a] - th[b]).max():.3e}"
        )

    # ---- multiphoton / count rate / invalid events
    inv = np.array([sum(r["invalid_events"].values()) / r["events"] for r in rows])
    print(
        f"invalid-event share per iteration: median {np.median(inv):.2e} max {inv.max():.2e}; sentinel share max {max(r['sentinel_share'] for r in rows):.2e}"
    )
    pinv = np.array([max(inv[table[k][0][0]], inv[table[k][1][0]]) for k in keys])
    print(f"spearman(|d|, invalid share) {stats.spearmanr(pinv, abs(d)).statistic:+.3f}")
    pairperf = np.array([abs(perf[table[k][0][0]] - perf[table[k][1][0]]) for k in keys])
    print(
        f"platform physical_perf per iteration: distinct values {sorted(set(perf.round(3)))}; spearman(|d|, |perf0 - perf1|) {stats.spearmanr(pairperf, abs(d)).statistic:+.3f}"
    )
    # detected rate proxy: the share of slot+failure clicks among all clicks is 1-sentinel; shots_used is constant
    print("shots_used values:", sorted({r["shots_used"] for r in rows}))
    # compiled-mesh size effects: which iterations have low perf: modes of the photon
    role_perf: dict[Any, Any] = {}
    for i, s in enumerate(settings):
        role_perf.setdefault(s["role"], []).append(perf[i])
    print({k: (round(min(v), 4), round(max(v), 4)) for k, v in role_perf.items()})
    fail = abs(d) > MIRROR
    print("failing pairs with indices (setting item d se z i0 i1):")
    for j in np.where(fail)[0]:
        print(f"  {keys[j]} d {d[j]:+.4f} se {se[j]:.4f} z {z[j]:+.1f} i0 {i0[j]} i1 {i1[j]}")
    np.savez(
        HERE / "c1_observed.npz",
        d=d,
        se=se,
        sep=sep,
        dt=dt,
        item=item,
        ideal=ideal,
        i0=i0,
        i1=i1,
        keys=np.array([f"{a}|{b}" for a, b in keys]),
    )


if __name__ == "__main__":
    main()
