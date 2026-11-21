"""Sedenion left sign rows as four-qubit phase oracles: exact phase polynomials, minimal CNOT networks on the
four-qubit shapes of a square-lattice coupler graph, and the Walsh distributions the oracles imprint.

The left row of basis element e_m (dimension 16, index bit b on wire b) is the diagonal
diag(cd_sign(16, m, x)). Its phase pi h_m(x) expands over parities [S.x] with angle pi F_S, where F is the
Walsh transform of the sign row; every row carries exactly the eight parities S with S.m odd, each at an odd
multiple of pi/4. A CNOT network that writes each needed parity onto some wire, with a phase gate at the parity's
first appearance, realizes the row up to the final linear relabeling of the wires. Under H on every wire
before and after, the oracle's output distribution is P(y) = W(y)^2 / 256, W the Walsh transform of the sign
row: 9/16 on one string, 1/16 on seven, 0 on eight.

The degree-two truncation of h_m (its F_2 polynomial with the cubic monomials removed) is a quadratic phase on
four of the row's eight parities, so the same network with the other four phases set to zero realizes it:
the same CZ sequence with changed virtual frames. The network with every phase zero is the identity oracle,
whose output is the all-zeros string.
"""

from __future__ import annotations

import math
from collections import deque
from typing import Any

import numpy as np

from boolean_anf import anf_coefficients
from cd_core import cd_sign
from parallel import ordered_map

DIM = 16
WIRES = 4
IDENTITY_WIRES: tuple[int, ...] = (1, 2, 4, 8)
# Undirected couplers of each four-qubit shape on positions 0..3: a path, a T with its center at 0, a square.
SHAPES: dict[str, tuple[tuple[int, int], ...]] = {
    "path": ((0, 1), (1, 2), (2, 3)),
    "T": ((0, 1), (0, 2), (0, 3)),
    "square": ((0, 1), (1, 2), (2, 3), (3, 0)),
}

Network = tuple[tuple[int, int], ...]


def parity(x: int) -> int:
    return bin(x).count("1") & 1


def sign_row(m: int) -> list[int]:
    """cd_sign(16, m, x) for x = 0..15: the left row of e_m."""
    return [int(cd_sign(DIM, m, x)) for x in range(DIM)]


def row_bits(m: int) -> list[int]:
    """h_m(x) in {0, 1} with sign (-1)^h_m."""
    return [(1 - s) // 2 for s in sign_row(m)]


def truncated_bits(bits: list[int]) -> list[int]:
    """The Boolean function with every monomial of degree three or more removed from the F_2 polynomial."""
    anf = anf_coefficients(bits)
    return [sum(1 for t in anf if bin(t).count("1") <= 2 and (t & x) == t) & 1 for x in range(DIM)]


def walsh_numerators(bits: list[int]) -> list[int]:
    """W(S) = sum_x (-1)^(h(x) + S.x), an integer in [-16, 16]."""
    return [sum((-1) ** (bits[x] ^ parity(s & x)) for x in range(DIM)) for s in range(DIM)]


def phase_eighths(bits: list[int]) -> dict[int, int]:
    """Nonzero parity angles of pi h(x) = const + sum_S (pi/8) c_S [S.x], as c_S mod 16 in eighths of pi.

    pi h = pi/2 - (pi/2) sum_S (W(S)/16) (1 - 2[S.x]) gives c_S = 8 W(S) / 16 = W(S) / 2 eighths of pi for S != 0;
    W(S) is even for every Boolean h on four variables, so c_S is an integer."""
    w = walsh_numerators(bits)
    out: dict[int, int] = {}
    for s in range(1, DIM):
        if w[s] % 2:
            raise ValueError(f"W({s}) = {w[s]} is odd")
        c = (w[s] // 2) % 16
        if c:
            out[s] = c
    return out


def diagonal_of(eighths: dict[int, int]) -> np.ndarray:
    """exp(i (pi/8) sum_S c_S [S.x]) for x = 0..15."""
    return np.array([np.exp(1j * math.pi / 8 * sum(c * parity(s & x) for s, c in eighths.items())) for x in range(DIM)])


def network(shape: str, parities: frozenset[int], fixed: bool) -> tuple[Network, tuple[int, ...]]:
    """A shortest CNOT network (control, target) on the shape's couplers, in either direction, after which every
    parity of the set has stood on some wire; fixed ends with each wire holding its input, otherwise any wire
    permutation ends the search. Breadth first, moves in a fixed order, so the result is deterministic."""
    index = {p: n for n, p in enumerate(sorted(parities))}
    full = (1 << len(index)) - 1
    moves = [*SHAPES[shape], *((b, a) for a, b in SHAPES[shape])]

    def cover(wires: tuple[int, ...], mask: int) -> int:
        for w in wires:
            if w in index:
                mask |= 1 << index[w]
        return mask

    start: tuple[tuple[int, ...], int] = (IDENTITY_WIRES, cover(IDENTITY_WIRES, 0))
    parent: dict[tuple[tuple[int, ...], int], tuple[tuple[tuple[int, ...], int], tuple[int, int]] | None] = {
        start: None
    }
    queue = deque([start])
    while queue:
        state = queue.popleft()
        wires, mask = state
        if mask == full and (wires == IDENTITY_WIRES if fixed else tuple(sorted(wires)) == IDENTITY_WIRES):
            steps: list[tuple[int, int]] = []
            key = state
            while (link := parent[key]) is not None:
                key, move = link
                steps.append(move)
            return tuple(reversed(steps)), wires
        for control, target in moves:
            nxt = list(wires)
            nxt[target] ^= nxt[control]
            new = (tuple(nxt), cover((nxt[target],), mask))
            if new not in parent:
                parent[new] = (state, (control, target))
                queue.append(new)
    raise ValueError(f"{shape}: no network covers parities {sorted(parities)}")


def oracle_ops(net: Network, eighths: dict[int, int]) -> tuple[list[tuple[Any, ...]], tuple[int, ...]]:
    """("phase", wire, angle) at each parity's first appearance and ("cnot", control, target) steps, and the
    final wire contents. A parity of the angle set that the network never writes raises."""
    wires = list(IDENTITY_WIRES)
    done: set[int] = set()
    ops: list[tuple[Any, ...]] = []

    def mark() -> None:
        for position, p in enumerate(wires):
            if p in eighths and p not in done:
                done.add(p)
                ops.append(("phase", position, math.pi / 8 * eighths[p]))

    mark()
    for control, target in net:
        wires[target] ^= wires[control]
        ops.append(("cnot", control, target))
        mark()
    if done != set(eighths):
        raise ValueError(f"network misses parities {sorted(set(eighths) - done)}")
    return ops, tuple(wires)


def relabeling(final: tuple[int, ...]) -> np.ndarray:
    """Permutation matrix of the basis map x -> y, y_j = [final_j . x]."""
    p = np.zeros((DIM, DIM))
    for x in range(DIM):
        p[sum(parity(final[j] & x) << j for j in range(WIRES)), x] = 1
    return p


def ops_unitary(ops: list[tuple[Any, ...]]) -> np.ndarray:
    """16 x 16 unitary of the phase and CNOT steps on basis index sum(x_j << j)."""
    u = np.eye(DIM, dtype=complex)
    for op in ops:
        if op[0] == "phase":
            u = np.diag([np.exp(1j * op[2]) if (x >> op[1]) & 1 else 1 for x in range(DIM)]) @ u
        else:
            c, t = op[1], op[2]
            step = np.zeros((DIM, DIM))
            for x in range(DIM):
                step[x ^ (((x >> c) & 1) << t), x] = 1
            u = step @ u
    return u


def residual(ops: list[tuple[Any, ...]], final: tuple[int, ...], diagonal: np.ndarray) -> float:
    """Distance of P^T U from diag(diagonal) up to one global phase; zero when the network realizes the
    diagonal followed by the relabeling P."""
    v = relabeling(final).T @ ops_unitary(ops)
    d = np.diag(v)
    off = float(np.max(np.abs(v - np.diag(d))))
    g = d[0] / diagonal[0]
    return off + float(np.max(np.abs(d - g * diagonal)))


def walsh_distribution(bits: list[int]) -> np.ndarray:
    """P(y) = W(y)^2 / 256: the output of H on every wire, the phase (-1)^h, H on every wire, from |0000>."""
    return np.array([w * w for w in walsh_numerators(bits)], dtype=float) / DIM**2


def census_row(item: tuple[str, int]) -> dict[str, Any]:
    """Minimal fixed and permuted CNOT counts of row m on one shape, each network checked against cd_sign; where
    the degree-two truncation lies on the row's parities, the permuted network also carries it and the identity
    (all phases zero), each checked against its own diagonal."""
    shape, m = item
    bits = row_bits(m)
    eighths = phase_eighths(bits)
    signs = np.array(sign_row(m), dtype=complex)
    trunc = phase_eighths(truncated_bits(bits))
    out: dict[str, Any] = {"shape": shape, "m": m, "parities": sorted(eighths), "truncation_fits": False}
    worst = 0.0
    for fixed in (True, False):
        net, final = network(shape, frozenset(eighths), fixed)
        ops, final_ops = oracle_ops(net, eighths)
        if final_ops != final:
            raise AssertionError(f"{shape} m={m}: the network's final wires disagree")
        worst = max(worst, residual(ops, final, signs))
        out["fixed" if fixed else "permuted"] = len(net)
        if not fixed and set(trunc) < set(eighths):
            out["truncation_fits"] = True
            for angles, diagonal in ((trunc, diagonal_of(trunc)), ({}, np.ones(DIM, dtype=complex))):
                worst = max(worst, residual(oracle_ops(net, angles)[0], final, diagonal))
    if worst > 1e-9:
        raise AssertionError(f"{shape} m={m}: an oracle network differs from its diagonal by {worst}")
    out["residual"] = worst
    return out


def census() -> list[dict[str, Any]]:
    """Every shape and every row m = 1..15, mapped through parallel.py (each item runs for seconds)."""
    return ordered_map(census_row, [(shape, m) for shape in SHAPES for m in range(1, DIM)], min_items=1)


def self_test() -> str:
    """Laws the oracle construction rests on, checked on every row and every shape."""
    for m in range(1, DIM):
        bits = row_bits(m)
        eighths = phase_eighths(bits)
        want = {s for s in range(1, DIM) if parity(s & m)}
        if set(eighths) != want or set(eighths.values()) - {2, 6, 10, 14}:
            raise AssertionError(f"m={m}: parities {sorted(eighths)} angles {sorted(set(eighths.values()))}")
        signs = np.array(sign_row(m), dtype=complex)
        if float(np.max(np.abs(diagonal_of(eighths) / diagonal_of(eighths)[0] - signs / signs[0]))) > 1e-12:
            raise AssertionError(f"m={m}: the parity expansion differs from the sign row")
        p = walsh_distribution(bits)
        if sorted(np.round(p * 16, 9)) != [0.0] * 8 + [1.0] * 7 + [9.0]:
            raise AssertionError(f"m={m}: Walsh distribution {p}")
        if np.array_equal(walsh_distribution(truncated_bits(bits)), p):
            raise AssertionError(f"m={m}: removing the cubic monomials leaves the Walsh distribution unchanged")
    rows = census()
    worst = max(r["residual"] for r in rows)
    best = {m: min(r["permuted"] for r in rows if r["m"] == m) for m in range(1, DIM)}
    # Positions are fixed labels of each shape, so a row's count depends on where its bits sit (the bit of a
    # popcount-one row at the T's center costs 8, on a leaf 9); the minimum over rows of one popcount is the
    # count of the best placement.
    by_popcount = {k: min(best[m] for m in best if bin(m).count("1") == k) for k in range(1, 5)}
    if by_popcount != {1: 8, 2: 8, 3: 9, 4: 10}:
        raise AssertionError(f"minimal permuted CNOT counts by popcount {by_popcount}")
    fits = sorted({r["m"] for r in rows if r["truncation_fits"]})
    if not {5, 10} <= set(fits):
        raise AssertionError(f"the truncation fits the row's network only for rows {fits}")
    return (
        f"sedenion_sign_oracle self-test passed: residual {worst:.1e}, minimal CNOTs by popcount {by_popcount}, "
        f"truncation on the row's parities for rows {fits}"
    )


if __name__ == "__main__":
    print(self_test())
