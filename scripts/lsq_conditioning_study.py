"""Least-squares conditioning and arithmetic precision of the atlas_coherent_families fits.

atlas_coherent_families.fit_models solves every identified model of every
lane by np.linalg.lstsq (SVD), on the full design and on each
leave-one-edge-out fold. This study rebuilds those least-squares problems
from the retained docs/evidence/atlas_coherent_families/result.json (bound by
sha256): per lane the ``fitted_slopes`` blocks of each model's families in
atlas_coherent_families.MODELS order, a ones column for a lane-constant model,
and ``measured_offset_rad`` as the data. A rebuilt design carries the retained
nine-decimal slopes and six-decimal offsets, so its bytes are identical on
every host; each design and its exact solution are retained only as sha256
digests beside the per-matrix statistics.

Every float64 is a dyadic rational, so the exact least-squares solution x* of
the stored data solves the normal equations A^T A x = A^T b in
fractions.Fraction (wheel_algebra.fraction_solve; a full-column-rank A makes
A^T A positive definite, so natural-order pivots are nonzero). Against x* the
study measures, per design:

- kappa(A), kappa(A D) with D a power of two per column bringing each column
  norm into [2^-1/2, 2^1/2] (exact scaling), the column-norm spread, and
  rho = ||r*|| / (||A|| ||x*||);
- in float64 numpy, the normal equations, Householder QR (np.linalg.qr and a
  triangular solve), SVD lstsq, and QR and lstsq on A D (x = D y): the
  componentwise relative, absolute and normwise relative errors, the
  prediction error (A x on a full fit, the held-out row a . x on a fold), and
  the margin, tolerance over error, under compare()'s per-value rule
  max(1.5e-6, 1e-9 |v|, eps kappa_rule^2 |v|), kappa_rule the retained
  condition (full fit) or fold_condition_max (fold);
- the SVD solution's drift under seeded perturbations of 2-norm
  3.5e-13 ||A||, the largest measured AOCL-to-OpenBLAS design difference;
- the rank of the integer-scaled design (every entry times a common power of
  two) modulo each prime of PRIMES, the residues of x* modulo each prime, and
  the 2-adic and p-adic valuations of r*.

On the full fit and the worst-conditioned fold of every model (the precision
ladder), one Householder QR code runs in
emulated p-bit binary floating point (every exact dyadic result rounded to p
significand bits, round to nearest even, unbounded exponent) at p = 53, 64,
106 and 113, in Python floats and in np.longdouble; Python floats must equal
p = 53 and longdouble must equal p = nmant + 1 bit for bit, and p = 53's R
factor must match np.linalg.qr within m n eps ||A|| where kappa <= 100. The
same designs are solved over the wheel of fractions (wheel_algebra.solve),
which must equal x*. A rank-deficient control (fourth column the sum of the
first two) gives bottom in every wheel component, rank n - 1 modulo every
prime, and a ZeroDivisionError in Fraction elimination.

``--out`` also runs, with pyadic, a Dixon / Hensel solve of the integer-scaled
normal equations M y = v (M = Ai^T Ai, x = 2^shift y): the inverse modulo
the first prime that leaves M invertible, lifted to p^k with
p^k > 2 max(N, D)^2, N and D Hadamard bounds of the Cramer numerator and
denominator, then rational reconstruction (pyadic.rationalise). rationalise
returns the shortest vector (r, s) of the lattice r = y s mod p^k, whose
determinant is p^k; a vector of norm below sqrt(p^k) is the shortest, and
sqrt(N^2 + D^2) < sqrt(p^k) follows from the bound. The lift of every design,
(prime, k, Y mod p^k), is the witness in padic_witness.json, bound to the
record by its sha256. ``--out`` also captures the real lane-4 designs of
both runs by wrapping atlas_coherent_families.fit_models in-process (bridge:
rebuilt against real designs and exact solutions), and resimulates the
axis_tilt_plus_mean held-out contrast predictions at each fold solution and
at its seeded perturbed solutions (P4). The resimulation section retains its
witness: the real design and offsets, the seed, and every resimulated log
ratio.

``--check FILE`` requires the source and witness digests and recomputes
everything except the pyadic lifting, the bridge and the resimulations. It
compares integers, strings, booleans and values derived from exact or
emulated arithmetic exactly, and condition numbers, norms and rho within
1e-6 relative (an SVD carries relative roundoff of order kappa eps). Every
roundoff measurement of a numpy solver agrees within ROUNDOFF_FACTOR once
both values are raised to the forward-error scale of a backward-stable
solve, eps kappa (eps kappa^2 for the normal equations), times max|x*| for
absolute errors and max|x*| / min|x*| for componentwise ones; margins agree
within the same factor below MARGIN_COMPARE. Below that floor a LAPACK build
sets the error by its own operation order; the README gives the
AOCL-to-OpenBLAS spread ROUNDOFF_FACTOR covers. P1's normal-equations clause
depends on the build, so --check prints it for the host and compares every
other verdict field, the P4 fields and the recommendation text in full.

The p-adic certificate is checked with integers only: each witness lift must
solve M Y = v modulo p^k with p^k above the recomputed bound, and Wang's
half-extended Euclid reconstruction of each component
(rational_reconstruction) must equal the fresh Fraction solution x*, which
itself solves the normal equations exactly. The resimulation summary is
recomputed from its witness (resimulation_summary): the real design must
round to the atlas record's retained slopes and offsets, every unperturbed
resimulation must lie within compare()'s contrast tolerance of the retained
prediction, the fold solutions and their seeded perturbations are solved
afresh for the parameter drifts, and the moves come from the retained log
ratios. ``--self-test`` checks the graded and column-scaled synthetic cases,
the emulator against IEEE double and long double, the rank-deficient
control, that --check rejects corrupted records, that the lift verifier
rejects altered witnesses, and that the resimulation check rejects a
corrupted summary or witness. docs/evidence/lsq_conditioning/README.md
states the predictions P1-P6 and their falsifiers.
"""

from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import json
import math
import operator
import platform
import sys
import time
from collections.abc import Callable, Sequence
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import atlas_coherent_families as acf  # noqa: E402
import numpy as np  # noqa: E402
import scipy.linalg  # noqa: E402

import parallel  # noqa: E402
import wheel_algebra  # noqa: E402

SCHEMA = "lsq-conditioning-study-v1"
SOURCE = ROOT / "docs/evidence/atlas_coherent_families/result.json"
# The Dixon lift of every design, which --check verifies with integers only.
WITNESS = ROOT / "docs/evidence/lsq_conditioning/padic_witness.json"
WITNESS_SCHEMA = "lsq-conditioning-padic-witness-v1"
EPS = acf.LSQ_ROUNDOFF
LADDER = (53, 64, 106, 113)
# Mersenne primes, far above every entry of a scaled design, so a rank drop
# modulo one of them requires it to divide every maximal minor.
PRIMES = (2**61 - 1, 2**89 - 1, 2**107 - 1)
# Largest AOCL-to-OpenBLAS difference of an atlas design, relative to its
# 2-norm (atlas_coherent_families README, cross-substrate agreement).
PERTURBATION = 3.5e-13
TRIALS = 8
SEED = 20261017
# Smallest substrate move of a retained contrast prediction, one unit of the
# sixth retained decimal (atlas_coherent_families README, cross-substrate
# agreement).
SMALLEST_MOVE = 1e-6
ROUNDOFF_FACTOR = 64.0
MARGIN_CAP = 1e8
# --check compares margins up to this value: a margin above it stays far from
# the tolerance / 10 threshold whatever the LAPACK build.
MARGIN_COMPARE = 1e3
# Values through an SVD keep nine digits: rounding then stays below the
# 1e-6 relative tolerance their LAPACK roundoff takes in --check.
CONDITION_DIGITS = 9
# Hex digits kept of the residue digests: a consistency check of values the
# full solution digest already binds.
RESIDUE_DIGEST = 16
# Median AOCL-to-OpenBLAS difference of an atlas design, relative to its
# 2-norm (atlas_coherent_families README, cross-substrate agreement).
MEDIAN_PERTURBATION = 1.3e-14
CONDITION_RELATIVE = 1e-6
# Relative agreement of a parameter drift under a seeded design perturbation:
# the perturbation sets the drift, and LAPACK roundoff, eps kappa against
# PERTURBATION kappa, moves it by below 1e-3 of itself.
DRIFT_RELATIVE = 1e-2
METHODS = ("ne", "qr", "svd", "qr_eq", "svd_eq")
METRICS = ("rel", "abs", "norm", "margin", "pred", "pred_margin")
RESIMULATED_MODEL = "axis_tilt_plus_mean"
MOVED = {"ibm_fez": 1, "ibm_kingston": 0}
BRIDGE_LANE = 4

Problem = tuple[tuple[str, int, str, int], np.ndarray, np.ndarray, int, float]
Dyadic = tuple[int, int]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def digest_fractions(values: Sequence[Fraction]) -> str:
    return sha256_bytes(";".join(f"{v.numerator}/{v.denominator}" for v in values).encode())


def digest_design(design: np.ndarray, data: np.ndarray) -> str:
    body = np.ascontiguousarray(design, dtype="<f8").tobytes() + np.ascontiguousarray(data, dtype="<f8").tobytes()
    return sha256_bytes(f"{design.shape[0]}x{design.shape[1]}:".encode() + body)


def sig(value: float | None, digits: int = 4) -> float | None:
    """A float kept to `digits` significant digits; None for an infinite or undefined value."""
    if value is None or not math.isfinite(value):
        return None
    return float(f"{value:.{digits}g}")


# --- the designs -----------------------------------------------------------


def rebuilt_problems(source: dict[str, Any]) -> list[Problem]:
    """Every identified model's full design and leave-one-out folds, rebuilt from the retained lane records."""
    require(source.get("schema") == acf.SCHEMA, f"{SOURCE}: schema {source.get('schema')}")
    require(
        source["models"] == {k: {"families": list(f), "lane_constant": c} for k, (f, c) in acf.MODELS.items()},
        "the retained model set differs from atlas_coherent_families.MODELS",
    )
    out: list[Problem] = []
    for lane in source["lanes"]:
        n = len(lane["edges"])
        data = np.array(lane["measured_offset_rad"], dtype=float)
        for name, model in lane["models"].items():
            if "unidentified" in model:
                continue
            families, constant = acf.MODELS[name]
            blocks = [np.array(lane["fitted_slopes"][f], dtype=float).reshape(n, -1) for f in families]
            design = np.hstack(blocks + ([np.ones((n, 1))] if constant else []))
            require(design.shape[1] == len(model["columns"]) + constant, f"{name}: column count differs")
            key = (lane["backend"], lane["lane"])
            out.append(((*key, name, -1), design, data, -1, float(model["condition"])))
            for held in range(n):
                keep = [k for k in range(n) if k != held]
                fold = (design[keep], data[keep])
                out.append(((*key, name, held), *fold, held, float(model["fold_condition_max"])))
    return out


def held_row(source_designs: dict[tuple[str, int, str], np.ndarray], problem: Problem) -> np.ndarray | None:
    (backend, lane, name, fold), *_ = problem
    return None if fold < 0 else source_designs[backend, lane, name][fold]


# --- exact arithmetic ------------------------------------------------------


def fractions_of(matrix: np.ndarray) -> list[list[Fraction]]:
    return [[Fraction(v) for v in row] for row in matrix.tolist()]


def normal_equations(a: list[list[Fraction]], b: list[Fraction]) -> tuple[list[list[Fraction]], list[Fraction]]:
    n = len(a[0])
    cols = list(zip(*a, strict=True))
    gram = [
        [sum((x * y for x, y in zip(cols[i], cols[j], strict=True)), Fraction(0)) for j in range(n)] for i in range(n)
    ]
    rhs = [sum((x * y for x, y in zip(cols[i], b, strict=True)), Fraction(0)) for i in range(n)]
    return gram, rhs


def floor_log2(q: Fraction) -> int:
    k = q.numerator.bit_length() - q.denominator.bit_length()
    return k - 1 if Fraction(2) ** k > q else k


def equilibration(a: list[list[Fraction]]) -> list[float]:
    """Per column 2^-e with the column norm in [2^(e - 1/2), 2^(e + 1/2)), from the exact squared norm."""
    out = []
    for col in zip(*a, strict=True):
        squared = sum((v * v for v in col), Fraction(0))
        out.append(math.ldexp(1.0, -((floor_log2(squared) + 1) // 2)))
    return out


def integer_scaled(values: Sequence[Fraction]) -> tuple[list[int], int]:
    """Integers equal to the dyadic values times 2^s, with the smallest such s >= 0."""
    shift = max((v.denominator.bit_length() - 1 for v in values), default=0)
    return [int(v * (1 << shift)) for v in values], shift


def rank_mod(rows: list[list[int]], prime: int) -> int:
    m = [[v % prime for v in row] for row in rows]
    rank, ncols = 0, len(m[0])
    for c in range(ncols):
        pivot = next((i for i in range(rank, len(m)) if m[i][c]), None)
        if pivot is None:
            continue
        m[rank], m[pivot] = m[pivot], m[rank]
        inverse = pow(m[rank][c], -1, prime)
        for i in range(rank + 1, len(m)):
            if m[i][c]:
                f = m[i][c] * inverse % prime
                m[i] = [(x - f * y) % prime for x, y in zip(m[i], m[rank], strict=True)]
        rank += 1
    return rank


def residues(values: Sequence[Fraction], prime: int) -> list[int]:
    return [v.numerator * pow(v.denominator, -1, prime) % prime if v.denominator % prime else -1 for v in values]


def valuation(q: Fraction, prime: int) -> int | None:
    if q == 0:
        return None
    count, num, den = 0, abs(q.numerator), q.denominator
    while num % prime == 0:
        num //= prime
        count += 1
    while den % prime == 0:
        den //= prime
        count -= 1
    return count


def scaled_system(a: list[list[Fraction]], b: list[Fraction]) -> tuple[list[list[int]], list[int], int]:
    """Integer M = Ai^T Ai, v = Ai^T bi with Ai = 2^sa A, bi = 2^sb b, so x = 2^(sa - sb) M^-1 v."""
    flat, sa = integer_scaled([v for row in a for v in row])
    n = len(a[0])
    ai = [flat[i * n : (i + 1) * n] for i in range(len(a))]
    bi, sb = integer_scaled(b)
    cols = list(zip(*ai, strict=True))
    gram = [[sum(x * y for x, y in zip(cols[i], cols[j], strict=True)) for j in range(n)] for i in range(n)]
    rhs = [sum(x * y for x, y in zip(cols[i], bi, strict=True)) for i in range(n)]
    return gram, rhs, sa - sb


def hadamard_bound_bits(gram: list[list[int]], rhs: list[int]) -> int:
    """Bits of 2 max(N, D)^2, D a Hadamard bound on |det M| and N on every Cramer numerator |det M_i|."""
    norms = [math.isqrt(sum(row[j] ** 2 for row in gram)) + 1 for j in range(len(gram))]
    rhs_norm = math.isqrt(sum(v * v for v in rhs)) + 1
    den = math.prod(norms)
    num = math.prod(max(c, rhs_norm) for c in norms)
    return (2 * max(num, den) ** 2).bit_length()


def lift_precision(prime: int, bound_bits: int) -> int:
    """The smallest k with prime^k > 2^bound_bits, which is at least 2 max(N, D)^2."""
    k = 1
    while prime**k <= 1 << bound_bits:
        k += 1
    return k


def rational_reconstruction(residue: int, modulus: int) -> tuple[int, int]:
    """The rational r/s with r = residue s mod modulus and |r|, |s| <= sqrt(modulus / 2): half-extended Euclid.

    Wang's reconstruction runs the extended Euclidean algorithm on
    (modulus, residue), keeping the cofactor of the residue, and stops at the
    first remainder at or below the bound; that remainder over its cofactor
    is the rational, returned as the coprime pair (r, s) with s > 0. Two
    rationals within the bound with the same residue are equal, so the result
    is the only one a lift can reconstruct to.
    """
    bound = math.isqrt(modulus // 2)
    r0, r1, t0, t1 = modulus, residue % modulus, 0, 1
    while r1 > bound:
        q = r0 // r1
        r0, r1 = r1, r0 - q * r1
        t0, t1 = t1, t0 - q * t1
    require(t1 != 0 and abs(t1) <= bound and math.gcd(r1, abs(t1)) == 1, "rational reconstruction fails")
    return (r1, t1) if t1 > 0 else (-r1, -t1)


Lift = tuple[int, int, list[int]]


def verify_lift(
    gram: list[list[int]], rhs: list[int], shift: int, exact: Sequence[Fraction], lift: Lift, where: str
) -> None:
    """A recorded Dixon lift (prime index, k, Y mod p^k) solves M Y = v mod p^k and reconstructs to x*."""
    index, k, lifted = lift
    require(0 <= index < len(PRIMES) and k >= 1, f"{where}: lift prime or precision out of range")
    modulus = PRIMES[index] ** k
    require(modulus > 1 << hadamard_bound_bits(gram, rhs), f"{where}: p^k does not exceed 2 max(N, D)^2")
    require(len(lifted) == len(rhs) and all(0 <= y < modulus for y in lifted), f"{where}: lift is not reduced")
    require(
        all(
            (sum(g * y for g, y in zip(row, lifted, strict=True)) - r) % modulus == 0
            for row, r in zip(gram, rhs, strict=True)
        ),
        f"{where}: the lift does not solve the scaled normal equations modulo p^k",
    )
    scale_num, scale_den = (1 << shift, 1) if shift >= 0 else (1, 1 << -shift)
    for y, x in zip(lifted, exact, strict=True):
        r, t = rational_reconstruction(y, modulus)
        require(
            r * scale_num * x.denominator == x.numerator * t * scale_den,
            f"{where}: the reconstructed lift differs from the Fraction solution",
        )


def encode_lift(lift: Lift) -> list[Any]:
    index, k, lifted = lift
    return [index, k, [base64.b64encode(y.to_bytes(max(1, (y.bit_length() + 7) // 8), "big")).decode() for y in lifted]]


def decode_lift(entry: list[Any]) -> Lift:
    index, k, lifted = entry
    return int(index), int(k), [int.from_bytes(base64.b64decode(y, validate=True), "big") for y in lifted]


def witness_text(lifts: Sequence[Lift]) -> str:
    rows = ",\n".join(json.dumps(encode_lift(lift), separators=(",", ":")) for lift in lifts)
    head = json.dumps({"schema": WITNESS_SCHEMA, "primes": [str(p) for p in PRIMES]})[:-1]
    return f'{head}, "lifts": [\n{rows}\n]}}\n'


def fraction_lift(problem: Problem, prime_index: int = 0) -> Lift:
    """The residues of x* modulo p^k, computed from the Fraction solution with pow(); the self-test's witness."""
    _, design, data, _, _ = problem
    a = fractions_of(design)
    b = [Fraction(v) for v in data.tolist()]
    gram, rhs = normal_equations(a, b)
    exact = wheel_algebra.fraction_solve(gram, rhs)
    scaled_gram, scaled_rhs, shift = scaled_system(a, b)
    prime = PRIMES[prime_index]
    k = lift_precision(prime, hadamard_bound_bits(scaled_gram, scaled_rhs))
    modulus = prime**k
    lifted = []
    for x in exact:
        y = x / Fraction(2) ** shift
        lifted.append(y.numerator * pow(y.denominator, -1, modulus) % modulus)
    return prime_index, k, lifted


# --- emulated p-bit binary floating point ----------------------------------


def round_dyadic(m: int, e: int, p: int) -> Dyadic:
    """m 2^e rounded to p significand bits, ties to even."""
    if m == 0:
        return (0, 0)
    a = -m if m < 0 else m
    shift = a.bit_length() - p
    if shift <= 0:
        return (m, e)
    q = a >> shift
    rem = a - (q << shift)
    half = 1 << (shift - 1)
    if rem > half or (rem == half and q & 1):
        q += 1
        if q.bit_length() > p:
            q >>= 1
            shift += 1
    return (-q if m < 0 else q, e + shift)


class Emulated:
    """Binary floating point with p significand bits and unbounded exponent, on (m, e) pairs meaning m 2^e."""

    def __init__(self, p: int) -> None:
        self.p = p
        self.zero: Dyadic = (0, 0)

    def of(self, value: float) -> Dyadic:
        num, den = value.as_integer_ratio()
        return round_dyadic(num, -(den.bit_length() - 1), self.p)

    def add(self, x: Dyadic, y: Dyadic) -> Dyadic:
        if x[0] == 0:
            return y
        if y[0] == 0:
            return x
        if x[1] >= y[1]:
            return round_dyadic((x[0] << (x[1] - y[1])) + y[0], y[1], self.p)
        return round_dyadic(x[0] + (y[0] << (y[1] - x[1])), x[1], self.p)

    def sub(self, x: Dyadic, y: Dyadic) -> Dyadic:
        return self.add(x, (-y[0], y[1]))

    def mul(self, x: Dyadic, y: Dyadic) -> Dyadic:
        return round_dyadic(x[0] * y[0], x[1] + y[1], self.p)

    def div(self, x: Dyadic, y: Dyadic) -> Dyadic:
        if x[0] == 0:
            return self.zero
        sign = -1 if (x[0] < 0) != (y[0] < 0) else 1
        a, b = abs(x[0]), abs(y[0])
        shift = max(0, self.p + 2 - (a.bit_length() - b.bit_length()))
        q, r = divmod(a << shift, b)
        if r:
            q, shift = (q << 1) | 1, shift + 1
        return round_dyadic(sign * q, x[1] - y[1] - shift, self.p)

    def sqrt(self, x: Dyadic) -> Dyadic:
        m, e = x
        if m == 0:
            return self.zero
        if e % 2:
            m, e = m << 1, e - 1
        shift = max(0, 2 * (self.p + 2) - m.bit_length())
        shift += shift % 2
        m, e = m << shift, e - shift
        s = math.isqrt(m)
        if s * s != m:
            return round_dyadic((s << 1) | 1, e // 2 - 1, self.p)
        return round_dyadic(s, e // 2, self.p)

    def negative(self, x: Dyadic) -> bool:
        return x[0] < 0

    @staticmethod
    def fraction(x: Dyadic) -> Fraction:
        return Fraction(x[0] << x[1]) if x[1] >= 0 else Fraction(x[0], 1 << -x[1])


class Native:
    """The same operations on a hardware type: Python float (IEEE double) or np.longdouble."""

    def __init__(self, kind: type) -> None:
        self.kind = kind
        self.zero = kind(0)
        self.add: Callable[[Any, Any], Any] = operator.add
        self.sub: Callable[[Any, Any], Any] = operator.sub
        self.mul: Callable[[Any, Any], Any] = operator.mul
        self.div: Callable[[Any, Any], Any] = operator.truediv
        self.sqrt: Callable[[Any], Any] = math.sqrt if kind is float else np.sqrt

    def of(self, value: float) -> Any:
        return self.kind(value)

    def negative(self, x: Any) -> bool:
        return bool(x < 0)

    @staticmethod
    def fraction(x: Any) -> Fraction:
        return Fraction(*x.as_integer_ratio())


def householder(design: np.ndarray, data: np.ndarray, ar: Any) -> tuple[list[Any], list[list[Any]]]:
    """Householder QR least squares, every operation in arithmetic `ar`; returns x and R (row-major, upper)."""
    m, n = design.shape
    cols = [[ar.of(float(v)) for v in design[:, j]] for j in range(n)] + [[ar.of(float(v)) for v in data]]
    for k in range(n):
        a = cols[k]
        total = ar.zero
        for i in range(k, m):
            total = ar.add(total, ar.mul(a[i], a[i]))
        norm = ar.sqrt(total)
        alpha = norm if ar.negative(a[k]) else ar.sub(ar.zero, norm)
        v = [ar.sub(a[k], alpha), *a[k + 1 :]]
        vtv = ar.zero
        for vi in v:
            vtv = ar.add(vtv, ar.mul(vi, vi))
        for j in range(k + 1, n + 1):
            c = cols[j]
            dot = ar.zero
            for i in range(k, m):
                dot = ar.add(dot, ar.mul(v[i - k], c[i]))
            f = ar.div(ar.add(dot, dot), vtv)
            for i in range(k, m):
                c[i] = ar.sub(c[i], ar.mul(f, v[i - k]))
        a[k] = alpha
    x: list[Any] = [ar.zero] * n
    for k in reversed(range(n)):
        total = cols[n][k]
        for j in range(k + 1, n):
            total = ar.sub(total, ar.mul(cols[j][k], x[j]))
        x[k] = ar.div(total, cols[k][k])
    r = [[cols[j][k] if j >= k else ar.zero for j in range(n)] for k in range(n)]
    return x, r


# --- per-design measurement -------------------------------------------------


def tolerance(value: Fraction | float, kappa_rule: float) -> float:
    """compare()'s per-value tolerance at the retained conditioning."""
    v = abs(float(value))
    return max(acf.CHECK_TOLERANCE, acf.CHECK_RELATIVE * v, EPS * kappa_rule**2 * v)


def margin_of(tolerances: Sequence[float], errors: Sequence[float]) -> float | None:
    """Smallest tolerance over error, capped at MARGIN_CAP; None where every error is zero."""
    ratios = [t / e for t, e in zip(tolerances, errors, strict=True) if e > 0]
    return sig(min(min(ratios), MARGIN_CAP)) if ratios else None


def solve_methods(design: np.ndarray, data: np.ndarray, scale: np.ndarray) -> dict[str, np.ndarray]:
    def qr(a: np.ndarray) -> np.ndarray:
        q, r = np.linalg.qr(a)
        return scipy.linalg.solve_triangular(r, q.T @ data)

    def svd(a: np.ndarray) -> np.ndarray:
        return np.linalg.lstsq(a, data, rcond=None)[0]

    scaled = design * scale
    return {
        "ne": np.linalg.solve(design.T @ design, design.T @ data),
        "qr": qr(design),
        "svd": svd(design),
        "qr_eq": scale * qr(scaled),
        "svd_eq": scale * svd(scaled),
    }


def error_metrics(
    x: Sequence[Fraction] | np.ndarray,
    exact: Sequence[Fraction],
    kappa_rule: float,
    prediction: tuple[np.ndarray, list[list[Fraction]], list[Fraction]],
) -> dict[str, float | None]:
    """Componentwise relative, absolute and normwise errors against x*, the margin and the prediction error."""
    diffs = [Fraction(v) - q if not isinstance(v, Fraction) else v - q for v, q in zip(x, exact, strict=True)]
    errors = [abs(float(d)) for d in diffs]
    norm = math.sqrt(float(sum((d * d for d in diffs), Fraction(0))))
    exact_norm = math.sqrt(float(sum((q * q for q in exact), Fraction(0))))
    rel = max((e / abs(float(q)) for e, q in zip(errors, exact, strict=True) if q), default=0.0)
    rows, rows_exact, predicted_exact = prediction
    floats = np.array([float(v) for v in x])
    predicted = rows @ floats
    prediction_errors = [abs(float(Fraction(float(p)) - q)) for p, q in zip(predicted, predicted_exact, strict=True)]
    pred_tol = [tolerance(q, kappa_rule) for q in predicted_exact]
    return {
        "rel": sig(rel),
        "abs": sig(max(errors)),
        "norm": sig(norm / exact_norm),
        "margin": margin_of([tolerance(q, kappa_rule) for q in exact], errors),
        "pred": sig(max(prediction_errors)),
        "pred_margin": margin_of(pred_tol, prediction_errors),
    }


ROW_FIELDS = [
    "backend",
    "lane",
    "model",
    "fold",
    "m",
    "n",
    "design_sha256",
    "reference_sha256",
    "kappa_rule",
    "kappa",
    "kappa_eq",
    "norm2",
    "spread",
    "rho",
    "x_max",
    "x_min",
    *[f"{method}_{metric}" for method in METHODS for metric in METRICS],
    "p4_drift",
    "p4_margin",
    "p4_pred",
    "ranks_mod_p",
    "residues_sha256",
    "residual_v2",
    "residual_vp",
    "bound_bits",
    "lift_prime_index",
    "lift_k",
    "lift_verified",
]


class Measure:
    """All float64 and exact measurements of one rebuilt least-squares problem."""

    def __call__(self, item: tuple[Problem, np.ndarray | None, int, Lift | None]) -> list[Any]:
        problem, held, index, lift = item
        (backend, lane, name, fold), design, data, _, kappa_rule = problem
        m, n = design.shape
        a = fractions_of(design)
        b = [Fraction(v) for v in data.tolist()]
        gram, rhs = normal_equations(a, b)
        exact = wheel_algebra.fraction_solve(gram, rhs)
        require(
            all(
                sum((g * x for g, x in zip(row, exact, strict=True)), Fraction(0)) == r
                for row, r in zip(gram, rhs, strict=True)
            ),
            f"{backend} {lane} {name} {fold}: x* misses the normal equations",
        )
        residual = [
            bi - sum((x * y for x, y in zip(row, exact, strict=True)), Fraction(0))
            for row, bi in zip(a, b, strict=True)
        ]
        singular = np.linalg.svd(design, compute_uv=False)
        scale = np.array(equilibration(a))
        singular_eq = np.linalg.svd(design * scale, compute_uv=False)
        col_norms = [math.sqrt(float(sum((v * v for v in col), Fraction(0)))) for col in zip(*a, strict=True)]
        exact_norm = math.sqrt(float(sum((q * q for q in exact), Fraction(0))))
        residual_norm = math.sqrt(float(sum((r * r for r in residual), Fraction(0))))
        if held is None:
            rows, rows_exact = design, a
        else:
            rows, rows_exact = held.reshape(1, -1), [[Fraction(v) for v in held.tolist()]]
        predicted_exact = [sum((x * y for x, y in zip(row, exact, strict=True)), Fraction(0)) for row in rows_exact]
        prediction = (rows, rows_exact, predicted_exact)
        solutions = solve_methods(design, data, scale)
        metrics = {method: error_metrics(x, exact, kappa_rule, prediction) for method, x in solutions.items()}

        rng = np.random.default_rng([SEED, index])
        base = solutions["svd"]
        drift = np.zeros(n)
        pred_drift = 0.0
        for _ in range(TRIALS):
            noise = rng.standard_normal(design.shape)
            noise *= PERTURBATION * singular[0] / np.linalg.norm(noise, 2)
            change = np.linalg.lstsq(design + noise, data, rcond=None)[0] - base
            drift = np.maximum(drift, np.abs(change))
            pred_drift = max(pred_drift, float(np.max(np.abs(rows @ change))))
        tolerances = [tolerance(q, kappa_rule) for q in exact]

        scaled_rows, rhs_int, shift = scaled_system(a, b)
        if lift is not None:
            verify_lift(scaled_rows, rhs_int, shift, exact, lift, f"{backend} {lane} {name} {fold}")
        design_int, _ = integer_scaled([v for row in a for v in row])
        ranks = [rank_mod([design_int[i * n : (i + 1) * n] for i in range(m)], p) for p in PRIMES]
        residue_text = ";".join(",".join(map(str, residues(exact, p))) for p in PRIMES)
        row: list[Any] = [
            backend,
            lane,
            name,
            fold,
            m,
            n,
            digest_design(design, data),
            digest_fractions(exact),
            kappa_rule,
            sig(float(singular[0] / singular[-1]), CONDITION_DIGITS),
            sig(float(singular_eq[0] / singular_eq[-1]), CONDITION_DIGITS),
            sig(float(singular[0]), CONDITION_DIGITS),
            sig(max(col_norms) / min(col_norms)),
            sig(residual_norm / (float(singular[0]) * exact_norm), CONDITION_DIGITS),
            sig(max(abs(float(q)) for q in exact)),
            sig(min(abs(float(q)) for q in exact)),
            *[metrics[method][metric] for method in METHODS for metric in METRICS],
            sig(float(np.max(drift))),
            margin_of(tolerances, [float(d) for d in drift]),
            sig(pred_drift),
            ranks,
            sha256_bytes(residue_text.encode())[:RESIDUE_DIGEST],
            [valuation(r, 2) for r in residual],
            [max((abs(v) for v in (valuation(r, p) for r in residual) if v is not None), default=0) for p in PRIMES],
            hadamard_bound_bits(scaled_rows, rhs_int),
            None if lift is None else lift[0],
            None if lift is None else lift[1],
            lift is not None,
        ]
        return row


LADDER_FIELDS = [
    "backend",
    "lane",
    "model",
    "fold",
    "m",
    "n",
    "kappa",
    *[f"p{p}_{metric}" for p in LADDER for metric in ("rel", "abs", "norm", "margin")],
    "python_float_equals_p53",
    "longdouble_bits",
    "longdouble_equals_emulated",
    "longdouble_norm",
    "numpy_r_ulps",
    "wheel_equals_reference",
    "wheel_kinds",
]


class Ladder:
    """Householder QR at every precision of the ladder, in hardware floats, and the wheel solve, on one design."""

    def __call__(self, item: tuple[Problem, int]) -> list[Any]:
        problem, longdouble_bits = item
        (backend, lane, name, fold), design, data, _, kappa_rule = problem
        m, n = design.shape
        a = fractions_of(design)
        b = [Fraction(v) for v in data.tolist()]
        gram, rhs = normal_equations(a, b)
        exact = wheel_algebra.fraction_solve(gram, rhs)
        tolerances = [tolerance(q, kappa_rule) for q in exact]
        exact_norm = math.sqrt(float(sum((q * q for q in exact), Fraction(0))))
        row: list[Any] = [backend, lane, name, fold, m, n]
        singular = np.linalg.svd(design, compute_uv=False)
        row.append(sig(float(singular[0] / singular[-1]), CONDITION_DIGITS))
        emulated: dict[int, list[Fraction]] = {}
        r53: list[list[Fraction]] = []
        for p in sorted({*LADDER, longdouble_bits}):
            ar = Emulated(p)
            x, r = householder(design, data, ar)
            emulated[p] = [ar.fraction(v) for v in x]
            if p == 53:
                r53 = [[ar.fraction(v) for v in rr] for rr in r]
        for p in LADDER:
            diffs = [v - q for v, q in zip(emulated[p], exact, strict=True)]
            errors = [abs(float(d)) for d in diffs]
            rel = max((e / abs(float(q)) for e, q in zip(errors, exact, strict=True) if q), default=0.0)
            norm = math.sqrt(float(sum((d * d for d in diffs), Fraction(0)))) / exact_norm
            row += [sig(rel), sig(max(errors)), sig(norm), margin_of(tolerances, errors)]
        native = Native(float)
        x_float, _ = householder(design, data, native)
        row.append([native.fraction(v) for v in x_float] == emulated[53])
        long = Native(np.longdouble)
        x_long, _ = householder(design, data, long)
        long_fractions = [long.fraction(v) for v in x_long]
        row.append(longdouble_bits)
        row.append(long_fractions == emulated[longdouble_bits])
        diffs = [v - q for v, q in zip(long_fractions, exact, strict=True)]
        row.append(sig(math.sqrt(float(sum((d * d for d in diffs), Fraction(0)))) / exact_norm))
        r_numpy = np.linalg.qr(design, mode="r")
        signs = np.sign(np.diag(r_numpy)) * np.sign([float(r53[k][k]) for k in range(n)])
        r_emulated = np.array([[float(v) for v in rr] for rr in r53]) * signs[:, None]
        row.append(sig(float(np.max(np.abs(r_numpy - r_emulated))) / (EPS * float(singular[0]))))
        wheel = wheel_algebra.solve(gram, rhs)
        row.append(all(w.finite and w.value() == q for w, q in zip(wheel, exact, strict=True)))
        row.append(sorted({w.kind() for w in wheel}))
        return row


# --- controls and synthetic cases -------------------------------------------


def reflector_product(vectors: np.ndarray) -> list[list[float]]:
    """The product of Householder reflectors I - 2 w w^T / (w . w) of integer vectors, in sequential Python floats.

    Python float operations round once each in IEEE double, so the product
    has the same bits on every host and LAPACK build.
    """
    size = vectors.shape[1]
    q = [[float(i == j) for j in range(size)] for i in range(size)]
    for w in vectors.tolist():
        norm = float(sum(v * v for v in w))
        q = [
            [q[i][j] - 2.0 * sum(q[i][k] * w[k] for k in range(size)) * w[j] / norm for j in range(size)]
            for i in range(size)
        ]
    return q


def graded_case(m: int = 12, n: int = 6) -> tuple[np.ndarray, np.ndarray]:
    """U diag(1, 2^-5, .., 2^-25) V^T, kappa 2^25, with a consistent right side: column scaling keeps its kappa."""
    rng = np.random.default_rng([SEED, 0])
    u = reflector_product(rng.integers(-99, 100, size=(2, m)))
    v = reflector_product(rng.integers(-99, 100, size=(2, n)))
    sigma = [2.0 ** (-5 * k) for k in range(n)]
    design = [[sum(u[i][k] * sigma[k] * v[j][k] for k in range(n)) for j in range(n)] for i in range(m)]
    x = rng.standard_normal(n).tolist()
    data = [sum(design[i][j] * x[j] for j in range(n)) for i in range(m)]
    return np.array(design), np.array(data)


def column_scaled_case(m: int = 12, n: int = 6) -> tuple[np.ndarray, np.ndarray]:
    """A Gaussian design with column scales 1e-5 .. 1e5, two decades apart."""
    rng = np.random.default_rng(SEED + 1)
    scales = np.array([1e-5, 1e-3, 1e-1, 1e1, 1e3, 1e5][:n])
    return rng.standard_normal((m, n)) * scales, rng.standard_normal(m)


def deficient_case(m: int = 12) -> tuple[np.ndarray, np.ndarray]:
    """Integer columns with the fourth equal to the sum of the first two: rank 3 of 4."""
    rng = np.random.default_rng(SEED + 2)
    base = rng.integers(-9, 10, size=(m, 3)).astype(float)
    return np.column_stack([base, base[:, 0] + base[:, 1]]), rng.integers(-9, 10, size=m).astype(float)


def synthetic(design: np.ndarray, data: np.ndarray) -> dict[str, Any]:
    """kappa, kappa(A D), rho and the float64 errors of every method against x* on one synthetic design."""
    m, n = design.shape
    a = fractions_of(design)
    b = [Fraction(v) for v in data.tolist()]
    gram, rhs = normal_equations(a, b)
    exact = wheel_algebra.fraction_solve(gram, rhs)
    residual = [
        bi - sum((x * y for x, y in zip(row, exact, strict=True)), Fraction(0)) for row, bi in zip(a, b, strict=True)
    ]
    scale = np.array(equilibration(a))
    singular = np.linalg.svd(design, compute_uv=False)
    singular_eq = np.linalg.svd(design * scale, compute_uv=False)
    exact_norm = math.sqrt(float(sum((q * q for q in exact), Fraction(0))))
    rho = math.sqrt(float(sum((r * r for r in residual), Fraction(0)))) / (float(singular[0]) * exact_norm)
    errors = {}
    for method, x in solve_methods(design, data, scale).items():
        diffs = [Fraction(float(v)) - q for v, q in zip(x, exact, strict=True)]
        errors[method] = sig(math.sqrt(float(sum((d * d for d in diffs), Fraction(0)))) / exact_norm)
    return {
        "m": m,
        "n": n,
        "kappa": sig(float(singular[0] / singular[-1]), CONDITION_DIGITS),
        "kappa_eq": sig(float(singular_eq[0] / singular_eq[-1]), CONDITION_DIGITS),
        "rho": sig(rho, CONDITION_DIGITS),
        "errors": errors,
    }


def deficient_control() -> dict[str, Any]:
    design, data = deficient_case()
    a = fractions_of(design)
    b = [Fraction(v) for v in data.tolist()]
    gram, rhs = normal_equations(a, b)
    try:
        wheel_algebra.fraction_solve(gram, rhs)
        fraction_outcome = "solved"
    except ZeroDivisionError:
        fraction_outcome = "ZeroDivisionError"
    design_int, _ = integer_scaled([v for row in a for v in row])
    n = design.shape[1]
    rows = [design_int[i * n : (i + 1) * n] for i in range(design.shape[0])]
    return {
        "design_sha256": digest_design(design, data),
        "n": n,
        "fraction_elimination": fraction_outcome,
        "wheel_kinds": [w.kind() for w in wheel_algebra.solve(gram, rhs)],
        "inconsistent_wheel_kinds": [w.kind() for w in wheel_algebra.solve([[1, 1], [1, 1]], [1, 2])],
        "ranks_mod_p": [rank_mod(rows, p) for p in PRIMES],
    }


# --- pyadic (record only) ---------------------------------------------------


class PadicSolve:
    """Dixon / Hensel solve of the integer-scaled normal equations with pyadic; the record's p-adic certificate."""

    def __call__(self, problem: Problem) -> dict[str, Any]:
        from pyadic import ModP, PAdic, rationalise

        (backend, lane, name, fold), design, data, _, _ = problem
        a = fractions_of(design)
        b = [Fraction(v) for v in data.tolist()]
        gram, rhs, shift = scaled_system(a, b)
        n = len(rhs)
        bound_bits = hadamard_bound_bits(gram, rhs)
        for index in range(len(PRIMES)):
            prime = PRIMES[index]
            augmented = [
                [ModP(v, prime) for v in row] + [ModP(int(i == j), prime) for j in range(n)]
                for i, row in enumerate(gram)
            ]
            try:
                for c in range(n):
                    pivot = next(i for i in range(c, n) if int(augmented[i][c]) != 0)
                    augmented[c], augmented[pivot] = augmented[pivot], augmented[c]
                    inverse = 1 / augmented[c][c]
                    augmented[c] = [v * inverse for v in augmented[c]]
                    for i in range(n):
                        if i != c and int(augmented[i][c]) != 0:
                            f = augmented[i][c]
                            augmented[i] = [x - f * y for x, y in zip(augmented[i], augmented[c], strict=True)]
            except StopIteration:
                continue
            break
        else:
            raise SystemExit(f"{backend} {lane} {name} {fold}: the scaled A^T A is singular modulo every prime")
        inverse_rows = [[int(v) for v in row[n:]] for row in augmented]
        k = lift_precision(prime, bound_bits)
        residual = list(rhs)
        lifted = [0] * n
        power = 1
        for _ in range(k):
            digit = [sum(c * r for c, r in zip(row, residual, strict=True)) % prime for row in inverse_rows]
            lifted = [y + d * power for y, d in zip(lifted, digit, strict=True)]
            update = [
                r - sum(g * d for g, d in zip(row, digit, strict=True)) for row, r in zip(gram, residual, strict=True)
            ]
            require(all(u % prime == 0 for u in update), f"{backend} {lane} {name} {fold}: Hensel step is not exact")
            residual = [u // prime for u in update]
            power *= prime
        modulus = prime**k
        padic = [PAdic(y, prime, k) for y in lifted]
        require(
            all(int(v.num * prime**v.n) % modulus == y for v, y in zip(padic, lifted, strict=True)),
            "PAdic lift differs",
        )
        scaled = [rationalise(y, modulus) for y in lifted]
        require(
            all(sum(g * y for g, y in zip(row, scaled, strict=True)) == r for row, r in zip(gram, rhs, strict=True)),
            f"{backend} {lane} {name} {fold}: the reconstruction misses the scaled normal equations",
        )
        solution = [y * Fraction(2) ** shift for y in scaled]
        residual_q = [
            bi - sum((x * y for x, y in zip(row, solution, strict=True)), Fraction(0))
            for row, bi in zip(a, b, strict=True)
        ]
        valuations = [PAdic(r, prime, k).n if r else None for r in residual_q]
        stdlib = [valuation(r, prime) for r in residual_q]
        require(valuations == stdlib, f"{backend} {lane} {name} {fold}: PAdic and integer valuations differ")
        return {"lift": (index, k, lifted), "bound_bits": bound_bits}


# --- bridge to the real designs and the resimulation (record only) ----------


def capture_lane(backend: str, lane: int) -> dict[str, Any]:
    """The arguments atlas_coherent_families.lane_fit passes to fit_models, captured without fitting."""
    captured: dict[str, Any] = {}
    original = acf.fit_models

    def capture(
        models: Any,
        prepared: Any,
        bases: Any,
        responses: Any,
        columns: Any,
        fitted_columns: Any,
        bounds: Any,
        measured: Any,
    ) -> dict[str, Any]:
        captured.update(models=models, prepared=prepared, bases=bases, responses=responses)
        captured.update(fitted_columns=fitted_columns, measured=measured)
        return {}

    retained = {fit["lane"]: fit for fit in json.loads(acf.RETAINED_DETUNING.read_text(encoding="utf-8"))["lanes"]}
    acf.fit_models = capture
    try:
        acf.lane_fit(
            backend,
            lane,
            acf.series_for(backend),
            acf.atlas.Executed(acf.RUNS[backend]),
            None,
            retained[lane] if backend == "ibm_fez" else None,
        )
    finally:
        acf.fit_models = original
    return captured


def exact_solution(design: np.ndarray, data: np.ndarray) -> list[Fraction]:
    gram, rhs = normal_equations(fractions_of(design), [Fraction(v) for v in data.tolist()])
    return wheel_algebra.fraction_solve(gram, rhs)


LEVELS = {"worst": PERTURBATION, "median": MEDIAN_PERTURBATION}


def perturbed_fold_solutions(
    real: np.ndarray, offsets: np.ndarray, seed: list[int]
) -> list[list[tuple[np.ndarray, str]]]:
    """Per held-out edge: the fold solution, then TRIALS seeded perturbations at each LEVELS size, in draw order."""
    rng = np.random.default_rng(seed)
    n = len(offsets)
    out = []
    for held in range(n):
        keep = [k for k in range(n) if k != held]
        fit = np.linalg.lstsq(real[keep], offsets[keep], rcond=None)[0]
        solutions = [(fit, "base")]
        norm = np.linalg.norm(real[keep], 2)
        for level, size in LEVELS.items():
            for _ in range(TRIALS):
                noise = rng.standard_normal(real[keep].shape)
                noise *= size * norm / np.linalg.norm(noise, 2)
                solutions.append((np.linalg.lstsq(real[keep] + noise, offsets[keep], rcond=None)[0], level))
        out.append(solutions)
    return out


def resimulation_summary(witness: dict[str, Any], lane: dict[str, Any]) -> dict[str, Any]:
    """P4's moves, drifts and ranks from a retained resimulation witness, bound to the atlas lane record.

    The real design must round to the lane's retained nine-decimal slopes
    and six-decimal offsets, as atlas_coherent_families wrote them; each
    unperturbed resimulation must lie within compare()'s contrast tolerance
    of the retained prediction. The fold solutions and their perturbations
    are recomputed from the design and the seed, so every parameter drift is
    measured afresh; the resimulated log ratios are the retained amplification
    inputs.
    """
    model = lane["models"][RESIMULATED_MODEL]
    families, constant = acf.MODELS[RESIMULATED_MODEL]
    real = np.array(witness["real_design"], dtype=float)
    offsets = np.array(witness["real_offsets"], dtype=float)
    n = len(offsets)
    slopes = [v for row in np.hstack([np.array(lane["fitted_slopes"][f], dtype=float) for f in families]) for v in row]
    width = len(slopes) // n
    require(real.shape == (n, width + int(constant)), "resimulation design shape differs from the lane")
    require([round(float(v), 9) for v in real[:, :width].ravel()] == slopes, "real design misses the retained slopes")
    require(not constant or bool(np.all(real[:, width] == 1.0)), "real design lane constant is not 1")
    require([round(float(v), 6) for v in offsets] == lane["measured_offset_rad"], "real offsets miss the record")
    ratios = witness["log_ratios"]
    per_fold = 1 + len(LEVELS) * TRIALS
    require(len(ratios) == n and all(len(row) == per_fold for row in ratios), "resimulation witness shape")
    retained = model["contrast"]["predicted_log_ratio"]
    contrast_tolerance = max(
        acf.CHECK_TOLERANCE, EPS * float(model["fold_condition_max"]) ** 2 * max(abs(v) for v in retained)
    )
    base_minus = [float(row[0]) - retained[h] for h, row in enumerate(ratios)]
    require(all(abs(d) <= contrast_tolerance for d in base_minus), "unperturbed resimulation misses the atlas contrast")
    drift: dict[str, list[float]] = {level: [] for level in LEVELS}
    move: dict[str, list[float]] = {level: [] for level in LEVELS}
    for held, solutions in enumerate(perturbed_fold_solutions(real, offsets, witness["seed"])):
        fit = solutions[0][0]
        for level in LEVELS:
            picks = [k for k, (_, name) in enumerate(solutions) if name == level]
            drift[level].append(max(float(np.max(np.abs(solutions[k][0] - fit))) for k in picks))
            move[level].append(max(abs(float(ratios[held][k]) - float(ratios[held][0])) for k in picks))
    moved = witness["moved_prediction"]
    return {
        "contrast_tolerance": sig(contrast_tolerance, CONDITION_DIGITS),
        "base_minus_retained": [sig(d, 3) for d in base_minus],
        "moves": [sig(v, 3) for v in move["worst"]],
        "median_moves": [sig(v, 3) for v in move["median"]],
        "parameter_drift": [sig(v, 3) for v in drift["worst"]],
        "moved_prediction_move": sig(move["worst"][moved], 3),
        "moved_prediction_median_move": sig(move["median"][moved], 3),
        "moved_prediction_rank": 1 + sum(v > move["worst"][moved] for v in move["worst"]),
        "largest_move": sig(max(move["worst"]), 3),
    }


def compare_resimulation(retained: dict[str, Any], fresh: dict[str, Any], path: str) -> None:
    """A retained resimulation summary against the one recomputed from its witness."""
    require(set(retained) == set(fresh), f"{path}: keys differ")
    for key, value in retained.items():
        if key == "parameter_drift":
            for k, (a, b) in enumerate(zip(value, fresh[key], strict=True)):
                require(abs(a - b) <= DRIFT_RELATIVE * abs(a), f"{path}.{key}[{k}]: {a} against {b}")
        elif key == "contrast_tolerance":
            close_condition(value, fresh[key], f"{path}.{key}")
        else:
            require(value == fresh[key], f"{path}.{key}: {value} against {fresh[key]}")


def check_resimulation(retained: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    """Recompute every backend's resimulation summary from its witness and compare it with the retained one."""
    lanes = {(lane["backend"], lane["lane"]): lane for lane in source["lanes"]}
    out = {}
    for backend, entry in retained.items():
        require(entry["model"] == RESIMULATED_MODEL and entry["moved_prediction"] == MOVED[backend], backend)
        witness = {k: v for k, v in entry.items() if k != "summary"}
        summary = resimulation_summary(witness, lanes[backend, BRIDGE_LANE])
        compare_resimulation(entry["summary"], summary, f"resimulation.{backend}.summary")
        out[backend] = {**witness, "summary": summary}
    return out


def bridge_and_resimulation(source: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    bridge: dict[str, Any] = {}
    resim: dict[str, Any] = {}
    lanes = {(lane["backend"], lane["lane"]): lane for lane in source["lanes"]}
    for backend in ("ibm_fez", "ibm_kingston"):
        captured = capture_lane(backend, BRIDGE_LANE)
        lane = lanes[backend, BRIDGE_LANE]
        offsets = np.asarray(captured["measured"]["offset"], dtype=float)
        rebuilt_data = np.array(lane["measured_offset_rad"], dtype=float)
        rows = {}
        for name, model in lane["models"].items():
            if "unidentified" in model:
                continue
            families, constant = acf.MODELS[name]
            n = len(offsets)
            real = np.hstack(
                [captured["responses"][f]["fitted"] for f in families] + ([np.ones((n, 1))] if constant else [])
            )
            rebuilt = np.hstack(
                [np.array(lane["fitted_slopes"][f], dtype=float).reshape(n, -1) for f in families]
                + ([np.ones((n, 1))] if constant else [])
            )
            singular = np.linalg.svd(real, compute_uv=False)
            x_real = exact_solution(real, offsets)
            x_rebuilt = exact_solution(rebuilt, rebuilt_data)
            kappa_rule = float(model["condition"])
            moves = [abs(float(p - q)) / tolerance(q, kappa_rule) for p, q in zip(x_rebuilt, x_real, strict=True)]
            svd = np.linalg.lstsq(real, offsets, rcond=None)[0]
            rows[name] = {
                "design_relative_difference": sig(float(np.max(np.abs(real - rebuilt))) / float(singular[0])),
                "data_max_difference": sig(float(np.max(np.abs(offsets - rebuilt_data)))),
                "kappa_real": sig(float(singular[0] / singular[-1]), CONDITION_DIGITS),
                "kappa_retained": model["condition"],
                "rebuilt_minus_real_exact_over_tolerance": sig(max(moves)),
                "svd_on_real_reproduces_retained_parameters": [round(float(v), 6) for v in svd] == model["parameters"],
            }
        bridge[backend] = rows

        families, constant = acf.MODELS[RESIMULATED_MODEL]
        columns = [c for f in families for c in captured["fitted_columns"][f]]
        n = len(offsets)
        real = np.hstack(
            [captured["responses"][f]["fitted"] for f in families] + ([np.ones((n, 1))] if constant else [])
        )
        seed = [SEED, 1 if backend == "ibm_fez" else 2]
        items = []
        for held, solutions in enumerate(perturbed_fold_solutions(real, offsets, seed)):
            base = captured["bases"][held]
            for values, _ in solutions:
                errors = acf.errors_of(columns, values[: len(columns)])
                items.append((captured["prepared"][held], errors, base["contrast"], base["phase"]))
        simulated = parallel.ordered_map(acf.Resimulate(), items, min_items=2)
        per_fold = 1 + len(LEVELS) * TRIALS
        witness = {
            "model": RESIMULATED_MODEL,
            "moved_prediction": MOVED[backend],
            "seed": seed,
            "real_design": real.tolist(),
            "real_offsets": offsets.tolist(),
            "log_ratios": [[ratio for _, ratio in simulated[h * per_fold : (h + 1) * per_fold]] for h in range(n)],
        }
        resim[backend] = {**witness, "summary": resimulation_summary(witness, lane)}
    return bridge, resim


# --- the study ---------------------------------------------------------------


def environment() -> dict[str, Any]:
    info = np.finfo(np.longdouble)
    out: dict[str, Any] = {
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "machine": platform.machine(),
        "longdouble": {"dtype": str(np.dtype(np.longdouble)), "nmant": int(info.nmant), "eps": float(info.eps)},
    }
    try:
        from importlib.metadata import version

        out["pyadic"] = version("pyadic")
    except Exception:  # noqa: BLE001
        out["pyadic"] = None
    return out


def column(rows: list[list[Any]], fields: list[str], name: str) -> list[Any]:
    index = fields.index(name)
    return [row[index] for row in rows]


def median(values: Sequence[float]) -> float:
    """The median, 0 for an empty list (a criterion over no design fails)."""
    return float(np.median(values)) if len(values) else 0.0


def finite_values(values: Sequence[Any]) -> list[float]:
    return [float(v) for v in values if v is not None]


def verdicts(record: dict[str, Any]) -> dict[str, Any]:
    """P1-P6 pass/fail lines and the recommendation, from the measured record."""
    rows, fields = record["matrices"], record["fields"]
    ladder, lfields = record["ladder"], record["ladder_fields"]

    def get(row: list[Any], name: str) -> Any:
        return row[fields.index(name)]

    def lget(row: list[Any], name: str) -> Any:
        return row[lfields.index(name)]

    qr_ratio, ne_ratio, ne_over_qr = 0.0, 0.0, []
    for row in rows:
        m, n, kappa, rho = get(row, "m"), get(row, "n"), get(row, "kappa"), get(row, "rho")
        bound_qr = m * n * EPS * (kappa + kappa**2 * rho)
        for method in ("qr", "svd"):
            qr_ratio = max(qr_ratio, get(row, f"{method}_norm") / bound_qr)
        ne_ratio = max(ne_ratio, get(row, "ne_norm") / (m * n * EPS * kappa**2))
        if kappa >= 1e4 and get(row, "qr_norm") > 0:
            ne_over_qr.append(get(row, "ne_norm") / get(row, "qr_norm"))
    graded = record["synthetic"]["graded"]
    graded_gain = graded["errors"]["ne"] / graded["errors"]["qr"]
    median_ne = median(ne_over_qr)
    p1_clauses = {
        "qr_svd_bound_holds": qr_ratio <= 1,
        "ne_bound_holds": ne_ratio <= 1,
        "graded_holds": graded_gain >= graded["kappa"] / 100,
        "median_holds": median_ne >= 10,
    }

    vds = max(get(row, "kappa_eq") / (2 * math.sqrt(get(row, "n")) * get(row, "kappa")) for row in rows)
    scaled = record["synthetic"]["column_scaled"]
    scaled_gain = scaled["kappa"] / scaled["kappa_eq"]
    spread_gain = [get(row, "kappa") / get(row, "kappa_eq") for row in rows if get(row, "spread") >= 100]
    median_spread = median(spread_gain)
    worst = max(rows, key=lambda row: get(row, "kappa"))
    p2 = vds <= 1 and scaled_gain >= 100 and median_spread >= 10

    ladder_ratio = 0.0
    for row in ladder:
        base = lget(row, "p53_norm")
        for p in LADDER[1:]:
            if base:
                ladder_ratio = max(ladder_ratio, lget(row, f"p{p}_norm") / (100 * 2.0 ** -(p - 53) * base))
    visible = [
        1 / v
        for v in finite_values(
            column(rows, fields, "svd_margin")
            + column(rows, fields, "svd_pred_margin")
            + column(ladder, lfields, "p53_margin")
        )
    ]
    largest_visible = max(visible, default=0.0)
    emulator = (
        all(column(ladder, lfields, "python_float_equals_p53"))
        and all(column(ladder, lfields, "longdouble_equals_emulated"))
        and all(
            lget(row, "numpy_r_ulps") <= lget(row, "m") * lget(row, "n") for row in ladder if lget(row, "kappa") <= 100
        )
    )
    p3 = ladder_ratio <= 1 and largest_visible < 0.1 and emulator

    resim = record.get("resimulation") or {}
    p4_moves = [float(entry["summary"]["moved_prediction_move"]) for entry in resim.values()]
    p4_largest = max(p4_moves) if p4_moves else None
    if p4_largest is None:
        p4_state = "not run"
    elif p4_largest < SMALLEST_MOVE / 10:
        p4_state = "holds"
    elif p4_largest >= SMALLEST_MOVE:
        p4_state = "falsified"
    else:
        p4_state = "inconclusive"
    p4_drift = max(e["summary"]["parameter_drift"][e["moved_prediction"]] for e in resim.values()) if resim else None

    p5_equal = all(column(rows, fields, "lift_verified"))
    full_rank = all(all(rank == get(row, "n") for rank in get(row, "ranks_mod_p")) for row in rows)
    control = record["control"]
    control_rank = all(rank == control["n"] - 1 for rank in control["ranks_mod_p"])
    p5 = p5_equal and full_rank and control_rank

    p6 = (
        all(column(ladder, lfields, "wheel_equals_reference"))
        and all(kinds == ["finite"] for kinds in column(ladder, lfields, "wheel_kinds"))
        and set(control["wheel_kinds"]) == {"bottom"}
        and control["fraction_elimination"] == "ZeroDivisionError"
    )

    def mover(prefix: str) -> float:
        return max((1 / v for v in finite_values(column(rows, fields, prefix))), default=0.0)

    equilibration_move = max(
        mover("qr_eq_margin"), mover("svd_eq_margin"), mover("qr_eq_pred_margin"), mover("svd_eq_pred_margin")
    )
    precision_move = max((1 / v for v in finite_values(column(ladder, lfields, "p53_margin"))), default=0.0)
    current_move = max(mover("svd_margin"), mover("svd_pred_margin"))
    movers = [
        name
        for name, value in (
            ("column equilibration", equilibration_move),
            ("Householder at p = 53", precision_move),
            ("the current SVD solve", current_move),
        )
        if value > 0.1
    ]
    if movers:
        recommendation = (
            f"replace the solver: {', '.join(movers)} moves a value by more than tolerance / 10 (moves_over_tolerance)"
        )
    else:
        if p4_state in ("falsified", "inconclusive"):
            source = (
                "the conditioning of the model itself: a design difference of the substrate's size moves the "
                f"resimulated contrast predictions by up to {p4_largest:.3g} through the leave-one-out solves, "
                "and no solver or precision change removes a sensitivity of the problem"
            )
        elif p4_state == "holds":
            source = "outside the least squares: the least-squares path moves no contrast prediction visibly"
        else:
            source = "not measured: the resimulation runs only with --out"
        recommendation = (
            "keep SVD lstsq in float64: its distance from the exact solution, the most that equilibration or any "
            "precision step can recover, stays below tolerance / 10 on every value (moves_over_tolerance); "
            f"the dominant error source is {source}"
        )
    return {
        "P1": {
            "holds": all(p1_clauses.values()),
            **p1_clauses,
            "max_qr_svd_error_over_bound": sig(qr_ratio, 4),
            "max_ne_error_over_bound": sig(ne_ratio, 4),
            "graded_ne_over_qr": sig(graded_gain, 4),
            "median_ne_over_qr_kappa_ge_1e4": sig(median_ne, 4),
        },
        "P2": {
            "holds": p2,
            "max_kappa_eq_over_van_der_sluis_bound": sig(vds, 4),
            "column_scaled_gain": sig(scaled_gain, 4),
            "median_gain_spread_ge_100": sig(median_spread, 4),
            "designs_spread_ge_100": len(spread_gain),
            "worst_design": [get(worst, "backend"), get(worst, "lane"), get(worst, "model"), get(worst, "fold")],
            "worst_kappa": get(worst, "kappa"),
            "worst_kappa_eq": get(worst, "kappa_eq"),
        },
        "P3": {
            "holds": p3,
            "max_error_over_scaled_p53": sig(ladder_ratio, 4),
            "largest_error_over_tolerance": sig(largest_visible, 4),
            "emulator_validated": emulator,
        },
        "P4": {
            "state": p4_state,
            "largest_resimulated_move": p4_largest,
            "moved_prediction_parameter_drift": p4_drift,
        },
        "P5": {"holds": p5, "padic_equals_fraction": p5_equal, "full_rank_mod_every_prime": full_rank},
        "P6": {"holds": p6, "control_wheel_kinds": control["wheel_kinds"]},
        "moves_over_tolerance": {
            "equilibration": sig(equilibration_move, 4),
            "precision_p53": sig(precision_move, 4),
            "current_svd": sig(current_move, 4),
        },
        "recommendation": recommendation,
    }


def study(
    selection: Callable[[Problem], bool] | None = None,
    lifts: Sequence[Lift] | None = None,
    padic: bool = False,
    bridge: bool = False,
) -> tuple[dict[str, Any], list[Lift]]:
    """The record, and the lifts it verified: given ones (--check) or pyadic's (padic=True)."""
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    problems = rebuilt_problems(source)
    if selection is not None:
        problems = [p for p in problems if selection(p)]
    designs = {}
    for lane in source["lanes"]:
        n = len(lane["edges"])
        for name, model in lane["models"].items():
            if "unidentified" not in model:
                families, constant = acf.MODELS[name]
                blocks = [np.array(lane["fitted_slopes"][f], dtype=float).reshape(n, -1) for f in families]
                designs[lane["backend"], lane["lane"], name] = np.hstack(
                    blocks + ([np.ones((n, 1))] if constant else [])
                )
    witness: list[Lift] = list(lifts) if lifts is not None else []
    if padic:
        results = parallel.ordered_map(PadicSolve(), problems)
        witness = [r["lift"] for r in results]
    require(not witness or len(witness) == len(problems), "the lift witness does not cover every design")
    items = [(p, held_row(designs, p), index, witness[index] if witness else None) for index, p in enumerate(problems)]
    rows = parallel.ordered_map(Measure(), items)
    worst: dict[tuple[str, int, str], tuple[float, int]] = {}
    for index, row in enumerate(rows):
        key = (row[0], row[1], row[2])
        if row[3] >= 0 and (key not in worst or row[ROW_FIELDS.index("kappa")] > worst[key][0]):
            worst[key] = (row[ROW_FIELDS.index("kappa")], index)
    ladder_problems = [p for index, p in enumerate(problems) if p[0][3] < 0 or worst[p[0][:3]][1] == index]
    longdouble_bits = int(np.finfo(np.longdouble).nmant) + 1
    ladder = parallel.ordered_map(Ladder(), [(p, longdouble_bits) for p in ladder_problems])
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "source": {"path": SOURCE.relative_to(ROOT).as_posix(), "sha256": sha256_bytes(SOURCE.read_bytes())},
        "environment": environment(),
        "constants": {
            "eps": EPS,
            "ladder": list(LADDER),
            "primes": [str(p) for p in PRIMES],
            "perturbation": PERTURBATION,
            "median_perturbation": MEDIAN_PERTURBATION,
            "trials": TRIALS,
            "seed": SEED,
            "smallest_move": SMALLEST_MOVE,
            "roundoff_factor": ROUNDOFF_FACTOR,
            "margin_cap": MARGIN_CAP,
            "check_tolerance": acf.CHECK_TOLERANCE,
            "check_relative": acf.CHECK_RELATIVE,
        },
        "fields": ROW_FIELDS,
        "matrices": rows,
        "ladder_fields": LADDER_FIELDS,
        "ladder": ladder,
        "synthetic": {
            "graded": synthetic(*graded_case()),
            "column_scaled": synthetic(*column_scaled_case()),
        },
        "control": deficient_control(),
    }
    if witness:
        record["padic"] = {
            "primes": [str(p) for p in PRIMES],
            "witness": {
                "path": WITNESS.relative_to(ROOT).as_posix(),
                "sha256": sha256_bytes(witness_text(witness).encode()),
            },
            "lifting_primes_used": sorted({str(PRIMES[lift[0]]) for lift in witness}),
            "k_range": [min(lift[1] for lift in witness), max(lift[1] for lift in witness)],
            "bound_bits_range": [
                min(column(rows, ROW_FIELDS, "bound_bits")),
                max(column(rows, ROW_FIELDS, "bound_bits")),
            ],
        }
    if bridge:
        record["bridge"], record["resimulation"] = bridge_and_resimulation(source)
    record["verdicts"] = verdicts(record)
    return record, witness


# --- --check -----------------------------------------------------------------

CONDITION_FIELDS = frozenset({"kappa", "kappa_eq", "norm2", "rho"})
VERDICT_CLAUSES = (
    ("P1", "qr_svd_bound_holds"),
    ("P1", "graded_holds"),
    ("P1", "median_holds"),
    ("P2", "holds"),
    ("P3", "holds"),
    ("P5", "holds"),
    ("P6", "holds"),
)


def roundoff_field(name: str) -> bool:
    return name.startswith(("ne_", "qr_", "svd_", "p4_"))


def roundoff_floor(name: str, kappa: float, x_max: float, x_min: float) -> float:
    """The forward-error scale of a solve: eps kappa (eps kappa^2 for the normal equations), in the field's units."""
    scale = EPS * (kappa**2 if name.startswith("ne_") else kappa)
    if name.endswith(("_abs", "_pred", "_drift")):
        return scale * x_max
    if name.endswith("_rel"):
        return scale * x_max / x_min if x_min else math.inf
    return scale


def close_roundoff(retained: Any, fresh: Any, floor: float, path: str) -> None:
    """Two roundoff measurements within ROUNDOFF_FACTOR of each other, each raised to the floor."""
    a = max(abs(float(retained or 0.0)), floor)
    b = max(abs(float(fresh or 0.0)), floor)
    if a == b:
        return
    require(max(a, b) <= ROUNDOFF_FACTOR * min(a, b), f"{path}: {retained} against {fresh}")


def close_margin(retained: Any, fresh: Any, path: str) -> None:
    """Two margins within ROUNDOFF_FACTOR, each capped at MARGIN_COMPARE (None is an exact solve)."""
    a = min(MARGIN_COMPARE if retained is None else float(retained), MARGIN_COMPARE)
    b = min(MARGIN_COMPARE if fresh is None else float(fresh), MARGIN_COMPARE)
    require(max(a, b) <= ROUNDOFF_FACTOR * min(a, b), f"{path}: {retained} against {fresh}")


def close_condition(retained: Any, fresh: Any, path: str) -> None:
    if retained is None or fresh is None:
        require(retained == fresh, f"{path}: {retained} against {fresh}")
        return
    require(abs(retained - fresh) <= CONDITION_RELATIVE * abs(retained), f"{path}: {retained} against {fresh}")


def compare_rows(retained: list[list[Any]], fresh: list[list[Any]], fields: list[str], section: str) -> None:
    require(len(retained) == len(fresh), f"{section}: {len(retained)} rows against {len(fresh)}")
    for k, (old, new) in enumerate(zip(retained, fresh, strict=True)):
        context = {key: float(old[fields.index(key)]) for key in ("kappa", "x_max", "x_min") if key in fields}
        for name, a, b in zip(fields, old, new, strict=True):
            path = f"{section}[{k}].{name}"
            if name in CONDITION_FIELDS:
                close_condition(a, b, path)
            elif name == "numpy_r_ulps":
                close_roundoff(a, b, 1.0, path)
            elif roundoff_field(name) and name.endswith("margin"):
                close_margin(a, b, path)
            elif roundoff_field(name):
                floor = roundoff_floor(name, context["kappa"], context["x_max"], context["x_min"])
                close_roundoff(a, b, floor, path)
            else:
                require(a == b, f"{path}: {a!r} against {b!r}")


def compare_synthetic(retained: dict[str, Any], fresh: dict[str, Any], path: str) -> None:
    for key in retained:
        if key in ("kappa", "kappa_eq", "rho"):
            close_condition(retained[key], fresh[key], f"{path}.{key}")
        elif key == "errors":
            for method in retained[key]:
                floor = roundoff_floor(f"{method}_norm", float(retained["kappa"]), 1.0, 1.0)
                close_roundoff(retained[key][method], fresh[key][method], floor, f"{path}.errors.{method}")
        else:
            require(retained[key] == fresh[key], f"{path}.{key}: {retained[key]} against {fresh[key]}")


def compare_verdicts(retained: dict[str, Any], fresh: dict[str, Any]) -> None:
    # P1's normal-equations bound depends on the LAPACK build (README), so
    # its clause and the P1 conjunction are recomputed and printed, not compared.
    for key, clause in VERDICT_CLAUSES:
        require(
            retained[key][clause] == fresh[key][clause],
            f"verdicts.{key}.{clause}: {retained[key]} against {fresh[key]}",
        )
    p4, fresh_p4 = retained["P4"], fresh["P4"]
    require(set(p4) == set(fresh_p4), f"verdicts.P4 keys: {p4} against {fresh_p4}")
    for key, value in p4.items():
        if key == "moved_prediction_parameter_drift" and value is not None and fresh_p4[key] is not None:
            require(abs(value - fresh_p4[key]) <= DRIFT_RELATIVE * abs(value), f"verdicts.P4.{key}: {value}")
        else:
            require(value == fresh_p4[key], f"verdicts.P4.{key}: {value} against {fresh_p4[key]}")
    for key, value in retained["moves_over_tolerance"].items():
        close_roundoff(value, fresh["moves_over_tolerance"][key], 1e-12, f"verdicts.moves_over_tolerance.{key}")
    require(
        retained["recommendation"] == fresh["recommendation"],
        f"verdicts.recommendation: {retained['recommendation']!r} against {fresh['recommendation']!r}",
    )


def check(retained: dict[str, Any], fresh: dict[str, Any]) -> dict[str, Any]:
    """Every number of `retained` against the recomputed `fresh` under the determinism classes of the docstring."""
    require(retained.get("schema") == SCHEMA, f"schema {retained.get('schema')}, expected {SCHEMA}")
    require(retained["source"] == fresh["source"], f"source {retained['source']} against {fresh['source']}")
    require(retained["constants"] == fresh["constants"], "constants differ")
    require(retained["fields"] == fresh["fields"] and retained["ladder_fields"] == fresh["ladder_fields"], "fields")
    compare_rows(retained["matrices"], fresh["matrices"], retained["fields"], "matrices")
    ladder_fields = list(retained["ladder_fields"])
    if retained["environment"]["longdouble"]["nmant"] != fresh["environment"]["longdouble"]["nmant"]:
        print("long double differs from the recording host; its ladder columns are not compared")
        for name in ("longdouble_bits", "longdouble_equals_emulated", "longdouble_norm"):
            ladder_fields[ladder_fields.index(name)] = "skip"
        fresh = copy.deepcopy(fresh)
        for row, old in zip(fresh["ladder"], retained["ladder"], strict=True):
            for k, name in enumerate(ladder_fields):
                if name == "skip":
                    row[k] = old[k]
    compare_rows(retained["ladder"], fresh["ladder"], ladder_fields, "ladder")
    for key in ("graded", "column_scaled"):
        compare_synthetic(retained["synthetic"][key], fresh["synthetic"][key], f"synthetic.{key}")
    require(retained["control"] == fresh["control"], f"control: {retained['control']} against {fresh['control']}")
    require(retained.get("padic") == fresh.get("padic"), f"padic: {retained.get('padic')} against {fresh.get('padic')}")
    resimulation = retained.get("resimulation")
    if resimulation is not None:
        source = json.loads(SOURCE.read_text(encoding="utf-8"))
        resimulation = check_resimulation(resimulation, source)
    fresh_verdicts = verdicts({**fresh, "resimulation": resimulation})
    compare_verdicts(retained["verdicts"], fresh_verdicts)
    return fresh_verdicts


# --- self-test ---------------------------------------------------------------


def self_test() -> int:
    graded = synthetic(*graded_case())
    errors = graded["errors"]
    m, n, kappa, rho = graded["m"], graded["n"], graded["kappa"], graded["rho"]
    require(kappa > 5e6, f"graded case kappa {kappa}")
    require(errors["ne"] >= errors["qr"] * kappa / 100, f"graded: normal equations {errors['ne']} vs QR {errors['qr']}")
    for method in ("qr", "svd"):
        require(errors[method] <= m * n * EPS * (kappa + kappa**2 * rho), f"graded: {method} {errors[method]}")
    require(graded["kappa_eq"] > kappa / 10, "graded: column scaling removed an orthogonal-factor kappa")
    print(
        f"graded kappa {kappa:.3g}: normal equations {errors['ne']:.2e}, QR {errors['qr']:.2e}, SVD {errors['svd']:.2e}"
    )

    scaled = synthetic(*column_scaled_case())
    gain = scaled["kappa"] / scaled["kappa_eq"]
    require(gain > 100, f"column-scaled: equilibration gains {gain:.3g}")
    print(f"column-scaled kappa {scaled['kappa']:.3g} -> {scaled['kappa_eq']:.3g} (gain {gain:.3g})")

    require(round_dyadic(0b1011, 0, 3) == (0b110, 1), "ties to even rounds 11/2 to 6")
    require(round_dyadic(0b1001, 0, 3) == (0b100, 1), "ties to even rounds 9/2 to 4")
    require(round_dyadic(0b1111, 0, 3) == (0b100, 2), "a carry renormalizes")
    rng = np.random.default_rng(SEED + 3)
    e53 = Emulated(53)
    ops: list[tuple[Callable[[Dyadic, Dyadic], Dyadic], Callable[[float, float], float]]] = [
        (e53.add, operator.add),
        (e53.sub, operator.sub),
        (e53.mul, operator.mul),
        (e53.div, operator.truediv),
    ]
    for x, y in rng.standard_normal((500, 2)) * np.exp(rng.uniform(-30, 30, (500, 2))):
        for emulated_op, float_op in ops:
            got = Emulated.fraction(emulated_op(e53.of(float(x)), e53.of(float(y))))
            require(got == Fraction(float_op(float(x), float(y))), f"p = 53 {float_op.__name__}({x}, {y})")
        got = Emulated.fraction(e53.sqrt(e53.of(abs(float(x)))))
        require(got == Fraction(math.sqrt(abs(float(x)))), f"p = 53 sqrt({x})")
    design, data = rng.standard_normal((12, 6)), rng.standard_normal(12)
    x53, r53 = householder(design, data, e53)
    native = Native(float)
    x_float, _ = householder(design, data, native)
    require([e53.fraction(v) for v in x53] == [native.fraction(v) for v in x_float], "p = 53 differs from IEEE double")
    r_numpy = np.linalg.qr(design, mode="r")
    signs = np.sign(np.diag(r_numpy)) * np.sign([float(e53.fraction(r53[k][k])) for k in range(6)])
    r_emulated = np.array([[float(e53.fraction(v)) for v in row] for row in r53]) * signs[:, None]
    ulps = float(np.max(np.abs(r_numpy - r_emulated))) / (EPS * float(np.linalg.norm(design, 2)))
    require(ulps <= 12 * 6, f"p = 53 R differs from np.linalg.qr by {ulps:.3g} ulps of ||A||")
    bits = int(np.finfo(np.longdouble).nmant) + 1
    emulated = Emulated(bits)
    x_emulated, _ = householder(design, data, emulated)
    long = Native(np.longdouble)
    x_long, _ = householder(design, data, long)
    require(
        [emulated.fraction(v) for v in x_emulated] == [long.fraction(v) for v in x_long], f"p = {bits} vs longdouble"
    )
    print(f"emulator: p = 53 equals IEEE double, p = {bits} equals np.longdouble, R within {ulps:.2g} ulps of numpy")

    control = deficient_control()
    require(control["fraction_elimination"] == "ZeroDivisionError", "control: Fraction elimination solved")
    require(set(control["wheel_kinds"]) == {"bottom"}, f"control: wheel {control['wheel_kinds']}")
    require(control["ranks_mod_p"] == [control["n"] - 1] * len(PRIMES), f"control: ranks {control['ranks_mod_p']}")
    require(set(control["inconsistent_wheel_kinds"]) == {"infinity"}, "control: inconsistent system")
    print(f"control: wheel {control['wheel_kinds']}, ranks mod p {control['ranks_mod_p']}")

    def reduced(problem: Problem) -> bool:
        (backend, lane, name, fold), *_ = problem
        return backend == "ibm_fez" and lane == 4 and name in ("lane_mean", RESIMULATED_MODEL) and fold < 2

    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    problems = [p for p in rebuilt_problems(source) if reduced(p)]
    # pyadic is a recording dependency; the residues of x* modulo p^k are the
    # same lift the Dixon iteration produces, so they exercise the verifier.
    lifts = [fraction_lift(problem) for problem in problems]
    record, _ = study(reduced, lifts=lifts)
    fresh, _ = study(reduced, lifts=lifts)
    check(json.loads(json.dumps(record)), fresh)
    fields = record["fields"]
    corruptions: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("source digest", lambda r: r["source"].__setitem__("sha256", "0" * 64)),
        ("reference digest", lambda r: r["matrices"][1].__setitem__(fields.index("reference_sha256"), "f" * 64)),
        (
            "svd error x1e4",
            lambda r: r["matrices"][3].__setitem__(
                fields.index("svd_norm"), r["matrices"][3][fields.index("svd_norm")] * 1e4
            ),
        ),
        (
            "condition number",
            lambda r: r["matrices"][1].__setitem__(
                fields.index("kappa"), r["matrices"][1][fields.index("kappa")] * 1.001
            ),
        ),
        (
            "emulated p113 error",
            lambda r: r["ladder"][0].__setitem__(record["ladder_fields"].index("p113_norm"), 1e-20),
        ),
        ("rank certificate", lambda r: r["matrices"][0].__setitem__(fields.index("ranks_mod_p"), [0, 0, 0])),
        ("witness digest", lambda r: r["padic"]["witness"].__setitem__("sha256", "a" * 64)),
        ("lift precision range", lambda r: r["padic"].__setitem__("k_range", [1, 1])),
        ("verdict", lambda r: r["verdicts"]["P5"].__setitem__("holds", not r["verdicts"]["P5"]["holds"])),
        (
            "recommendation",
            lambda r: r["verdicts"].__setitem__("recommendation", r["verdicts"]["recommendation"] + "."),
        ),
        ("wheel control", lambda r: r["control"].__setitem__("wheel_kinds", ["finite"] * 4)),
    ]
    for label, corrupt in corruptions:
        bad = json.loads(json.dumps(record))
        corrupt(bad)
        try:
            check(bad, fresh)
        except SystemExit:
            continue
        raise SystemExit(f"--check accepted a record with a corrupted {label}")
    print(f"--check accepts the reduced record and rejects {len(corruptions)} corruptions")

    full = problems[3]
    _, design, data, _, _ = full
    svd = np.linalg.lstsq(design, data, rcond=None)[0]
    a = fractions_of(design)
    b = [Fraction(v) for v in data.tolist()]
    _, _, shift = scaled_system(a, b)
    index, k, lifted = lifts[3]
    modulus = PRIMES[index] ** k
    float_lift = [
        (q := Fraction(v) / Fraction(2) ** shift).numerator * pow(q.denominator, -1, modulus) % modulus for v in svd
    ]
    bad_lifts: list[tuple[str, Lift]] = [
        ("one unit added to a lifted component", (index, k, [lifted[0] + 1, *lifted[1:]])),
        ("residues of the float64 SVD solution", (index, k, float_lift)),
        ("precision k = 1", (index, 1, [y % PRIMES[index] for y in lifted])),
        ("another prime", ((index + 1) % len(PRIMES), k, lifted)),
    ]
    for label, lift in bad_lifts:
        try:
            Measure()((full, None, 3, lift))
        except SystemExit:
            continue
        raise SystemExit(f"the lift verifier accepted {label}")
    require(rational_reconstruction(-5 * pow(7, -1, 2**61 - 1) % (2**61 - 1), 2**61 - 1) == (-5, 7), "-5/7")
    print(f"the lift verifier rejects {len(bad_lifts)} altered witnesses")

    retained = json.loads((ROOT / "docs/evidence/lsq_conditioning/result.json").read_text(encoding="utf-8"))
    resimulation = retained["resimulation"]
    check_resimulation(resimulation, source)
    moved = "ibm_fez"
    summary_move = resimulation[moved]["summary"]["moved_prediction_move"]

    def raise_largest_move(r: dict[str, Any]) -> None:
        row = r[moved]["log_ratios"][resimulation[moved]["moved_prediction"]]
        worst = max(range(1, 1 + TRIALS), key=lambda k: abs(row[k] - row[0]))
        row[worst] += 0.1 * (row[worst] - row[0])

    def shift_bases(r: dict[str, Any]) -> None:
        for row in r[moved]["log_ratios"]:
            row[0] += 1.0

    resim_corruptions: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        (
            "moved_prediction_move within its verdict class",
            lambda r: r[moved]["summary"].__setitem__("moved_prediction_move", summary_move * 1.01),
        ),
        ("the log ratio that sets the moved prediction's move", raise_largest_move),
        (
            "a real design entry",
            lambda r: r[moved]["real_design"][0].__setitem__(0, r[moved]["real_design"][0][0] + 1e-6),
        ),
        ("the perturbation seed", lambda r: r[moved].__setitem__("seed", [SEED, 7])),
        ("an unperturbed resimulation", shift_bases),
    ]
    for label, corrupt in resim_corruptions:
        bad = json.loads(json.dumps(resimulation))
        corrupt(bad)
        try:
            check_resimulation(bad, source)
        except SystemExit:
            continue
        raise SystemExit(f"--check accepted a resimulation witness with a corrupted {label}")
    print(f"the resimulation check rejects {len(resim_corruptions)} corruptions")
    print("self-test passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if args.check:
        retained = json.loads(args.check.read_text(encoding="utf-8"))
        require(
            retained.get("source", {}).get("sha256") == sha256_bytes(SOURCE.read_bytes()),
            f"{SOURCE}: sha256 differs from {args.check}",
        )
        recorded = retained["padic"]["witness"]
        require(recorded["path"] == WITNESS.relative_to(ROOT).as_posix(), f"witness path {recorded['path']}")
        witness_bytes = WITNESS.read_bytes()
        require(sha256_bytes(witness_bytes) == recorded["sha256"], f"{WITNESS}: sha256 differs from {args.check}")
        witness = json.loads(witness_bytes)
        require(witness["schema"] == WITNESS_SCHEMA and witness["primes"] == [str(p) for p in PRIMES], "witness")
        start = time.monotonic()
        fresh, _ = study(lifts=[decode_lift(entry) for entry in witness["lifts"]])
        here = check(retained, fresh)
        for label, v in (("retained", retained["verdicts"]), ("this host", here)):
            states = ", ".join(
                f"{k} {v[k].get('holds', v[k].get('state'))}" for k in ("P1", "P2", "P3", "P4", "P5", "P6")
            )
            print(f"{label}: {states}; P1 normal-equations error over bound {v['P1']['max_ne_error_over_bound']}")
        print(f"{args.check}: {len(retained['matrices'])} designs reproduced in {time.monotonic() - start:.1f} s")
        return 0
    require(args.out is not None, "--out, --check or --self-test is required")
    record, lifts = study(padic=True, bridge=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    WITNESS.write_text(witness_text(lifts), encoding="utf-8")
    text = json.dumps(record, separators=(",", ":"))
    args.out.write_text(text.replace("],[", "],\n[") + "\n", encoding="utf-8")
    print(json.dumps(record["verdicts"], indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
