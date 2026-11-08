"""C3 (iii) with a shared source: one source bit whose true state shifts the flip probability of every other bit.
Source and targets are named in physical qubits (the same five qubits in every template) or in logical roles;
8 parameters (d0, d1 per target) in each frame, 24 raw bins."""

import numpy as np
from c3_corr import KEYS, NAMES, OBS, QUBITS, ROLES, T, flip_matrix, match_rho, ordered_map
from scipy.optimize import least_squares


def total_matrix(n, frame, source, params):
    roles = T[n]["roles"]
    idx = (
        (lambda q: [k for k, v in enumerate(KEYS) if roles[v] == q][0])
        if frame == "physical"
        else (lambda r: KEYS.index(r))
    )
    a = idx(source)
    M = np.eye(32)
    targets = [t for t in (QUBITS if frame == "physical" else ROLES) if t != source]
    for t, (d0, d1) in zip(targets, params.reshape(-1, 2), strict=True):
        M = flip_matrix(a, idx(t), d0, d1) @ M
    return M


def chi2_multi(params, frame, source):
    tot = 0.0
    for n in NAMES:
        extra = total_matrix(n, frame, source, params)
        rho, V, r = match_rho(n, extra)
        tot += float((((OBS[n]["r"] - r) / OBS[n]["se"]) ** 2).sum())
    return tot


def fit_multi(task):
    frame, source = task
    # QRNG seed: docs/evidence/anu_qrng/draw-2026-10-25T015224Z.json index 12
    rng = np.random.default_rng(34580)
    best = None
    for _ in range(5):
        x0 = rng.uniform(-0.01, 0.05, 8)
        res = least_squares(
            lambda p: np.sqrt(chi2_multi(p, frame, source)) * np.ones(1),
            x0,
            bounds=(-0.05, 0.4),
            diff_step=0.02,
            max_nfev=40,
        )
        c = chi2_multi(res.x, frame, source)
        if best is None or c < best[0]:
            best = (c, res.x)
    return frame, source, best


if __name__ == "__main__":
    tasks = [("physical", q) for q in QUBITS] + [("logical", r) for r in ROLES]
    for frame, source, (c, _x) in ordered_map(fit_multi, tasks, min_items=1):
        print(f"{frame:8s} source {source!s:9s} chi2 {c:7.1f} (24 bins, 8 parameters)")
