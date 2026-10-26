"""Per-item associator norms for check_small.py, importable by parallel.py spawn workers.

Each function reads only module state built from cd_core signs at import,
so a pooled map returns exactly what the serial loop returns.
"""

import numpy as np
from common import sign

S = np.array([[sign(16, p, q) for q in range(16)] for p in range(16)])
S8 = np.array([[sign(8, p, q) for q in range(8)] for p in range(8)])


def Lm(av):
    M = np.zeros((16, 16))
    for p in range(16):
        for q in range(16):
            M[p ^ q, q] += av[p] * S[p, q]
    return M


def _two_term_units():
    two = []
    for i in range(16):
        for j in range(i + 1, 16):
            for s in (1, -1):
                v = np.zeros(16)
                v[i], v[j] = 1, s
                two.append(v / np.sqrt(2))
    return np.array(two)


TWO = _two_term_units()
LS = np.array([Lm(v) for v in TWO])


def row_max(ia):
    """Largest spectral norm of L_{ab} - L_a L_b over every two-term unit b, for the two-term unit a = TWO[ia]."""
    La = LS[ia]
    best = 0.0
    for ib in range(len(TWO)):
        M = Lm(La @ TWO[ib]) - La @ LS[ib]
        best = max(best, float(np.linalg.norm(M, 2)))
    return best


def ascent(seed):
    """One 60-step random ascent of the associator norm from its own child stream of the QRNG seed."""
    rng = np.random.default_rng(seed)
    av, bv = rng.normal(size=16), rng.normal(size=16)
    av /= np.linalg.norm(av)
    bv /= np.linalg.norm(bv)
    mx = 0.0
    for _ in range(60):
        La, Lb = Lm(av), Lm(bv)
        s = float(np.linalg.norm(Lm(La @ bv) - La @ Lb, 2))
        mx = max(mx, s)
        cand_a = av + 0.1 * rng.normal(size=16)
        cand_a /= np.linalg.norm(cand_a)
        if np.linalg.norm(Lm(Lm(cand_a) @ bv) - Lm(cand_a) @ Lb, 2) > s:
            av = cand_a
        cand_b = bv + 0.1 * rng.normal(size=16)
        cand_b /= np.linalg.norm(cand_b)
        if np.linalg.norm(Lm(Lm(av) @ cand_b) - Lm(av) @ Lm(cand_b), 2) > s:
            bv = cand_b
    return mx


def m8(x, y):
    r = np.zeros(8)
    for p in range(8):
        for q in range(8):
            r[p ^ q] += S8[p, q] * x[p] * y[q]
    return r


def octonion_assoc(triple):
    """Associator norm of three octonion units drawn before the map."""
    av, bv, cv = (x / np.linalg.norm(x) for x in triple)
    return float(np.linalg.norm(m8(m8(av, bv), cv) - m8(av, m8(bv, cv))))
