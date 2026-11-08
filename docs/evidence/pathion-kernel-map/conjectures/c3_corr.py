"""C3 (iii): correlated two-qubit readout error. For each ordered pair (source a, target b) add a flip of b's reading with
probability d0 when a is truly 0 and d1 when a is truly 1, on top of the bracket's product readout; fit (d0, d1) to the 24
raw bins of ba, bb and b0 with the contraction of each template fixed by its visibility. The pair is named in physical
qubits (shared across templates) or in logical roles (shared across templates)."""

import numpy as np
from c3_data import KEYS, T, matrix_for, ratio_of, se_ratio
from scipy.optimize import least_squares

from parallel import ordered_map

NAMES = ("ba", "bb", "b0")
SIGN = {n: np.sign(T[n]["ideal_c"]) for n in NAMES}
OBS = {}
for n in NAMES:
    r, V, _ = ratio_of(T[n]["counts"], SIGN[n])
    OBS[n] = dict(r=r, V=V, se=se_ratio(T[n]["counts"], SIGN[n]))
QUBITS = (2, 4, 8, 11, 12)
ROLES = KEYS  # d0 d1 d2 selector coin


def flip_matrix(a, b, d0, d1):
    """32x32 stochastic matrix: bit b flips with probability d0 (d1) when bit a of the true state is 0 (1)."""
    M = np.zeros((32, 32))
    for s in range(32):
        p = d1 if (s >> a) & 1 else d0
        M[s, s] += 1 - p
        M[s ^ (1 << b), s] += p
    return M


def model_ratio(n, extra, rho):
    Mp = matrix_for(n)
    law = extra @ (rho * T[n]["ideal"] + (1 - rho) / 32)
    law = Mp @ law
    return ratio_of(law * 1e6, SIGN[n])


def match_rho(n, extra):
    best = None
    for rho in np.linspace(0.25, 1.0, 76):
        r, V, _ = model_ratio(n, extra, rho)
        if best is None or abs(V - OBS[n]["V"]) < abs(best[1] - OBS[n]["V"]):
            best = (rho, V, r)
    return best


def chi2(params, pair, frame):
    d0, d1 = params
    tot = 0.0
    for n in NAMES:
        roles = T[n]["roles"]
        if frame == "physical":
            qa, qb = pair
            a, b = (
                [k for k, v in enumerate(KEYS) if roles[v] == qa][0],
                [k for k, v in enumerate(KEYS) if roles[v] == qb][0],
            )
        else:
            a, b = KEYS.index(pair[0]), KEYS.index(pair[1])
        extra = flip_matrix(a, b, d0, d1)
        rho, V, r = match_rho(n, extra)
        tot += float((((OBS[n]["r"] - r) / OBS[n]["se"]) ** 2).sum())
    return tot


def fit(task):
    pair, frame = task
    best = None
    for start in ((0.0, 0.03), (0.03, 0.0), (0.0, -0.01), (0.05, 0.05)):
        res = least_squares(
            lambda p: [np.sqrt(chi2(p, pair, frame))],
            start,
            bounds=([-0.05, -0.05], [0.4, 0.4]),
            diff_step=0.02,
            max_nfev=25,
        )
        c = chi2(res.x, pair, frame)
        if best is None or c < best[0]:
            best = (c, res.x)
    return pair, frame, best


def main():
    base = sum(float((((OBS[n]["r"] - match_rho(n, np.eye(32))[2]) / OBS[n]["se"]) ** 2).sum()) for n in NAMES)
    print(f"baseline (bracket product readout + contraction): chi2 {base:.1f} on 24 bins")
    tasks = [((a, b), "physical") for a in QUBITS for b in QUBITS if a != b] + [
        ((a, b), "logical") for a in ROLES for b in ROLES if a != b
    ]
    out = ordered_map(fit, tasks, min_items=1)
    out.sort(key=lambda x: x[2][0])
    for pair, frame, (c, x) in out[:14]:
        print(f"{frame:8s} {pair!s:18s} chi2 {c:7.1f}  d0 {x[0]:+.3f} d1 {x[1]:+.3f}")
    print(
        "best physical:",
        min((o for o in out if o[1] == "physical"), key=lambda o: o[2][0])[:2],
        min(o[2][0] for o in out if o[1] == "physical"),
    )
    print(
        "best logical :",
        min((o for o in out if o[1] == "logical"), key=lambda o: o[2][0])[:2],
        min(o[2][0] for o in out if o[1] == "logical"),
    )


if __name__ == "__main__":
    main()
