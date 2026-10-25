"""Shared helpers for the independent DAS MERGUS algebra review checks.

Convention authority: gororoba_quantum/cd_core.py (cd_sign) of the pinned checkout.
Exact arithmetic: python-flint fmpq_mat for real ranks/determinants; Gaussian
rationals are carried as pairs of fmpq.
"""

import os
import random
import sys
from fractions import Fraction

import flint

REPO = os.environ["REVIEW_REPO"]  # a clean checkout of ec75554a1af800496d99c80ab23022e83c5e20ea
sys.path.insert(0, os.path.join(REPO, "gororoba_quantum"))
import cd_core  # noqa: E402

_SIGN = {}


def sign(dim, p, q, mutate=None):
    key = (dim, p, q)
    if key not in _SIGN:
        _SIGN[key] = cd_core.cd_sign(dim, p, q)
    s = _SIGN[key]
    if mutate is not None and (p, q) in mutate:
        s = -s
    return s


def lmat(dim, y, mutate=None):
    """L_y as flint fmpq_mat: (L_y)[r][q] = y[r^q] sigma(r^q, q)."""
    m = flint.fmpq_mat(dim, dim)
    for r in range(dim):
        for q in range(dim):
            v = y[r ^ q]
            if v:
                m[r, q] = v * sign(dim, r ^ q, q, mutate)
    return m


def rmat(dim, y):
    m = flint.fmpq_mat(dim, dim)
    for r in range(dim):
        for p in range(dim):
            v = y[r ^ p]
            if v:
                m[r, p] = v * sign(dim, p, r ^ p)
    return m


def mul(dim, a, b, mutate=None):
    out = [flint.fmpq(0)] * dim
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                if bj:
                    out[i ^ j] += sign(dim, i, j, mutate) * ai * bj
    return out


def nullity(m):
    return m.ncols() - m.rank()


# Gaussian rationals as (re, im) tuples of fmpq
def cadd(a, b):
    return (a[0] + b[0], a[1] + b[1])


def cmul(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def cdiv(a, b):
    d = b[0] * b[0] + b[1] * b[1]
    return ((a[0] * b[0] + a[1] * b[1]) / d, (a[1] * b[0] - a[0] * b[1]) / d)


def cneg(a):
    return (-a[0], -a[1])


def cdot(x, y):
    s = (flint.fmpq(0), flint.fmpq(0))
    for a, b in zip(x, y):
        s = cadd(s, cmul(a, b))
    return s


def cabs2(a):
    return a[0] * a[0] + a[1] * a[1]


def z_from_y(y):
    """z_k = y_k + i y_{16+k}, k=1..15 (chapter 3, G.3)."""
    return [(flint.fmpq(y[k]), flint.fmpq(y[16 + k])) for k in range(1, 16)]


def y_from_z(z):
    y = [flint.fmpq(0)] * 32
    for k in range(1, 16):
        y[k] = z[k - 1][0]
        y[16 + k] = z[k - 1][1]
    return y


def invariants(z):
    u, mu, v = z[0:7], z[7], z[8:15]
    U, V0, W = cdot(u, u), cdot(v, v), cdot(u, v)
    Q = cadd(cadd(U, cmul(mu, mu)), V0)
    Delta = cadd(cmul(U, V0), cneg(cmul(W, W)))
    G = cadd(cmul(Q, Q), cneg(cmul((flint.fmpq(4), flint.fmpq(0)), Delta)))
    N = sum((cabs2(a) for a in z), flint.fmpq(0))
    return {"U": U, "V0": V0, "W": W, "Q": Q, "Delta": Delta, "G": G, "N": N}


def rint(rng, lo, hi):
    return flint.fmpq(rng.randint(lo, hi))


def rgauss(rng, lo=-5, hi=5):
    return (rint(rng, lo, hi), rint(rng, lo, hi))


def frac(x):
    return Fraction(int(x.p), int(x.q))


RNG = random.Random
