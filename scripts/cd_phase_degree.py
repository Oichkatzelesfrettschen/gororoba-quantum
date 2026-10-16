"""Algebraic degree of Cayley-Dickson sign rows and associator phases.

phi_n(a, x) = [cd_sign(2^n, a, x) = -1] in F_2. The sign row of L_{e_m} is
f_m = phi_n(m, .), and the associator phase of W_ij = L_{e_i e_j}^dagger
L_{e_i} L_{e_j} (predict.associator_phase) is

    g_ij(x) = phi_n(j, x) + phi_n(i, j^x) + phi_n(i^j, x) + phi_n(i, j).

docs/notes/cd_phase_degree.md proves deg f_m = n - 1 for n >= 2 and m != 0,
and deg g_ij = max(1, bitlen(max(i, j)) - 2) for n >= 3 and distinct nonzero
i, j. Index bit n-1 is the last doubling, x = (y, xi) with y the low n-1 bits.
For each n up to --max-n the checker asserts every identity the proof uses,
cell by cell against tables built from cd_sign, and the statements:

  recursion   (R) phi_n((a', alpha), (y, xi)) = phi^(xi)(a', y) + alpha (N(y) + xi)
  lemma0      phi_n(0, x) = phi_n(x, 0) = 0
  commutator  phi(c, y) + phi(y, c) = N(c) + delta_0(y) + delta_c(y)
  involution  phi(a, x) + phi(a, a^x) = N(a), so phi(a, a) = N(a)
  two-point   deg(delta_p + delta_q) = k - 1 for p != q in F_2^k, deg N = k
  sign cases  f_m from f_{m'} in the three cases (a), (b), (c)
  sign degree deg f_m = n - 1 for every m != 0 (n >= 2)
  degenerate  g_0j = g_i0 = g_ii = 0 and g_ij(0) = 0
  slice D0    g_ij(y, 0) = g'(y) + beta (C(i', j'^y) + C(i', j')) + alpha (N(y) + N(y^j') + N(j'))
  slice D1    g_ij(y, 1) - g_ij(y, 0) = N(i') + N(j') + N(i'^j')
  closed form A = g' + delta_u + delta_v + const with u != v for an upper pair
  degree      deg g_ij = max(1, bitlen(max(i, j)) - 2) on every ordered pair (n >= 3)
  census      unordered pairs of degree n - 2 added at level n: 3 2^(n-2) (2^(n-1) - 1)

Stdout is byte-deterministic; --timing adds per-level seconds on stderr.
--mutate replaces one branch of cd_sign by a wrong one and inverts the
verdict: the run exits 0 only when a check catches the mutation.
"""

from __future__ import annotations

import argparse
import sys
import time
from collections.abc import Callable
from pathlib import Path

import numpy as np
import numpy.typing as npt

Table = npt.NDArray[np.uint8]


class Mismatch(Exception):
    pass


def _require(ok: bool, message: str) -> None:
    if not ok:
        raise Mismatch(message)


MUTATIONS = ("high-low-unconditional", "high-high-no-early-return")


def _mutated_sign(mutation: str) -> Callable[[int, int, int], int]:
    """cd_sign with one branch replaced: the high-low branch negates even when
    q = 0, or the both-high branch skips its early return at q' = 0."""

    def sign(dim: int, p: int, q: int) -> int:
        s = 1
        half = dim >> 1
        while half > 0:
            p_hi, q_hi = p >= half, q >= half
            if not p_hi and q_hi:
                p, q = q - half, p
            elif p_hi and not q_hi:
                p -= half
                if q != 0 or mutation == "high-low-unconditional":
                    s = -s
            elif p_hi and q_hi:
                qh, ph = q - half, p - half
                if qh == 0 and mutation != "high-high-no-early-return":
                    return -s
                p, q = qh, ph
            half >>= 1
        return s

    return sign


def phi_table(n: int, sign: Callable[[int, int, int], int]) -> Table:
    dim = 1 << n
    return np.array([[sign(dim, a, x) < 0 for x in range(dim)] for a in range(dim)], dtype=np.uint8)


def anf_degrees(rows: Table) -> npt.NDArray[np.int64]:
    """ANF degree of each row of a 0/1 truth-table matrix (Moebius transform over F_2)."""
    a = rows.astype(np.uint8, copy=True)
    count, size = a.shape
    k = size.bit_length() - 1
    for b in range(k):
        a = a.reshape(count, -1, 2, 1 << b)
        a[:, :, 1, :] ^= a[:, :, 0, :]
        a = a.reshape(count, size)
    weight = np.array([m.bit_count() for m in range(size)], dtype=np.int64)
    return np.where(a.any(axis=1), (a * weight).max(axis=1), 0)


def check_two_point(k: int) -> None:
    size = 1 << k
    y = np.arange(size)
    delta = (y[:, None] == y[None, :]).astype(np.uint8)
    p, q = np.triu_indices(size, 1)
    degrees = anf_degrees(delta[p] ^ delta[q])
    _require(bool((degrees == k - 1).all()), f"two-point: delta_p + delta_q off degree {k - 1} at k = {k}")
    _require(int(anf_degrees((y != 0).astype(np.uint8)[None, :])[0]) == k, f"two-point: deg N != {k} at k = {k}")


def check_level(n: int, phi: Table, low: Table) -> tuple[int, int]:
    """Assert every identity at level n from the level-(n-1) table; return (new pairs, their degree)."""
    dim, half = 1 << n, 1 << (n - 1)
    x = np.arange(dim)
    y = np.arange(half)
    nz_low = (y != 0).astype(np.uint8)
    delta_low = (y[:, None] == y[None, :]).astype(np.uint8)

    # (R): alpha selects the row block, xi the column block.
    blocks = {
        (0, 0): low,
        (0, 1): low.T,
        (1, 0): low ^ nz_low[None, :],
        (1, 1): low.T ^ (1 - nz_low)[None, :],
    }
    for (row_bit, col_bit), want in blocks.items():
        got = phi[row_bit * half : (row_bit + 1) * half, col_bit * half : (col_bit + 1) * half]
        _require(bool((got == want).all()), f"recursion: n = {n} block alpha = {row_bit}, xi = {col_bit}")

    _require(not phi[0].any() and not phi[:, 0].any(), f"lemma0: n = {n}")
    nz = (x != 0).astype(np.uint8)
    delta = (x[:, None] == x[None, :]).astype(np.uint8)
    commutator = phi ^ phi.T
    _require(bool((commutator == (nz[:, None] ^ delta[0][None, :] ^ delta)).all()), f"commutator: n = {n}")
    involution = phi ^ phi[x[:, None], x[:, None] ^ x[None, :]]
    _require(bool((involution == nz[:, None]).all()), f"involution: n = {n}")
    _require(bool((np.diag(phi) == nz).all()), f"involution: phi(a, a) != N(a) at n = {n}")

    # Sign rows: f_m(y, xi) = f_{m'}(y) + xi (N(m') + delta_0 + delta_{m'}) + mu (N(y) + xi).
    xi = (x >= half).astype(np.uint8)
    ylow = x & (half - 1)
    for m in range(1, dim):
        m_low, mu = m & (half - 1), m >> (n - 1)
        want = (
            low[m_low, ylow]
            ^ (xi & (int(m_low != 0) ^ delta_low[0, ylow] ^ delta_low[m_low, ylow]))
            ^ (mu * (nz_low[ylow] ^ xi))
        )
        _require(bool((phi[m] == want).all()), f"sign cases: n = {n}, m = {m}")
    if n >= 2:
        degrees = anf_degrees(phi[1:])
        _require(bool((degrees == n - 1).all()), f"sign degree: n = {n} rows of degree {sorted(set(degrees))}")

    # Associator phases on every ordered pair, degenerate ones included.
    i, j = (a.ravel() for a in np.meshgrid(x, x, indexing="ij"))
    g = phi[j[:, None], x[None, :]] ^ phi[i[:, None], j[:, None] ^ x[None, :]] ^ phi[(i ^ j)[:, None], x[None, :]]
    g ^= phi[i, j][:, None]
    degenerate = (i == 0) | (j == 0) | (i == j)
    _require(not g[degenerate].any(), f"degenerate: n = {n}")
    _require(not g[:, 0].any(), f"degenerate: g_ij(0) != 0 at n = {n}")

    ip, alpha, jp, beta = i & (half - 1), i >> (n - 1), j & (half - 1), j >> (n - 1)
    kp = ip ^ jp
    g_low = (
        low[jp[:, None], y[None, :]]
        ^ low[ip[:, None], jp[:, None] ^ y[None, :]]
        ^ low[kp[:, None], y[None, :]]
        ^ low[ip, jp][:, None]
    )

    def comm(c: npt.NDArray[np.int64], arg: npt.NDArray[np.int64]) -> Table:
        return (c != 0).astype(np.uint8)[:, None] ^ (arg == 0).astype(np.uint8) ^ (arg == c[:, None]).astype(np.uint8)

    def nzu(v: npt.NDArray[np.int64]) -> Table:
        return (v != 0).astype(np.uint8)

    shifted = jp[:, None] ^ y[None, :]
    d0 = (
        g_low
        ^ beta[:, None].astype(np.uint8) * (comm(ip, shifted) ^ comm(ip, jp[:, None]))
        ^ alpha[:, None].astype(np.uint8) * (nzu(y)[None, :] ^ nzu(shifted) ^ nzu(jp)[:, None])
    )
    _require(bool((g[:, :half] == d0).all()), f"slice D0: n = {n}")
    c = nzu(ip) ^ nzu(jp) ^ nzu(kp)
    _require(bool(((g[:, half:] ^ g[:, :half]) == c[:, None]).all()), f"slice D1: n = {n}")

    upper = ~degenerate & ((alpha == 1) | (beta == 1))
    if upper.any():
        u = np.where(alpha[upper] == 0, jp[upper], 0)
        v = np.where(beta[upper] == 0, jp[upper], kp[upper])
        _require(bool((u != v).all()), f"closed form: u = v at n = {n}")
        rest = g[upper, :half] ^ g_low[upper] ^ delta_low[u] ^ delta_low[v]
        _require(bool((rest == rest[:, :1]).all()), f"closed form: A - g' - delta_u - delta_v not constant at n = {n}")

    new = 0
    if n >= 3:
        pairs = ~degenerate
        degrees = anf_degrees(g[pairs])
        top = np.maximum(i[pairs], j[pairs])
        bitlen = np.floor(np.log2(top)).astype(np.int64) + 1
        want_deg = np.maximum(1, bitlen - 2)
        bad = np.flatnonzero(degrees != want_deg)
        _require(bad.size == 0, f"degree: n = {n}, {bad.size} pairs off max(1, bitlen - 2)")
        new = int(((top >= half) & (i[pairs] < j[pairs])).sum())
        _require(new == 3 * (1 << (n - 2)) * (half - 1), f"census: n = {n}, {new} new unordered pairs")
    elif n == 2:
        _require(not g.any(), "degree: the quaternion associator phases are not all zero")
    return new, max(1, n - 2)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--max-n", type=int, default=8, help="largest n = log2(dim), at least 3")
    parser.add_argument("--timing", action="store_true", help="print per-level seconds on stderr")
    parser.add_argument("--mutate", choices=MUTATIONS, help="replace one cd_sign branch; exit 0 only if caught")
    args = parser.parse_args()
    if args.max_n < 3:
        parser.error("--max-n must be at least 3")

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gororoba_quantum"))
    from cd_core import cd_sign

    sign = _mutated_sign(args.mutate) if args.mutate else cd_sign
    print("n dim sign_row_degree new_pairs new_pair_degree")
    try:
        low = phi_table(0, sign)
        for n in range(1, args.max_n + 1):
            start = time.perf_counter()
            phi = phi_table(n, sign)
            check_two_point(n)
            new, degree = check_level(n, phi, low)
            if n >= 3:
                print(f"{n} {1 << n} {n - 1} {new} {degree}")
            if args.timing:
                print(f"n={n}: {time.perf_counter() - start:.2f} s", file=sys.stderr)
            low = phi
    except Mismatch as exc:
        if args.mutate:
            print(f"mutation {args.mutate} caught: {exc}")
            return 0
        print(f"mismatch: {exc}", file=sys.stderr)
        return 1
    if args.mutate:
        print(f"mutation {args.mutate} survived every check through n={args.max_n}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
