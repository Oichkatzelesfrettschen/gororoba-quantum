"""Hilbert function of the fiber cone of E8-bar -> N- and E8-bar -> N+ by monomial linear algebra.

On the parametrization Phi(w, rho, sigma, e, zeta) of ../arcs put a = t2 and b = (m^2 - 1) omega / m, so that
t8 = -i b and, with A = ((m^2 + 1) a - (m^2 - 1) zeta) / 2 = (m^2 - 1) nu, the conic nu^2 - omega^2 = nu reads

    b^2 = A (A - (m^2 - 1)) / m^2 =: F(w, a, zeta).

The coordinates of the slice are zeta, a, b, the rank-one block in (m rho, m sigma, rho, sigma), t9 = -s9 t / 2 with
t = w^2 / m, and t1 = (-(m^2 - 1) a + (m^2 + 1) zeta + w^2) / (2 m). They generate R = R0 + R0 b with
R0 = k[[t, zeta]] + (rho, sigma, a) k[[w, rho, sigma, zeta, a]] inside P + P b, P = k[[w, rho, sigma, zeta, a]]:
x w^n lies in R0 for x in {rho, sigma, a} by x w^n = t (x w^(n-2) + x w^(n-1)), and F lies in R0. With every variable
and b of weight 1 and n^N the elements of weight at least N,

    r_N(d) = dim A_d - dim B_d  <=  h_d,   A_d = image of I^d,  B_d = image of m_R I^d  in (P + P b) / n^N.

    $PYTHON docs/evidence/a5-exceptional-fibers/monomial-ladder/e8_ladder.py --slug e8-nm --prime 32009 \
        --degree 2 --order 10
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
from pathlib import Path
from typing import Any

import sympy
from flint import Ordering, nmod_mat, nmod_mpoly_ctx

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "kernel-limits"))
sys.path.insert(0, str(HERE.parents[3] / "gororoba_quantum"))

import plucker_limits as limits  # noqa: E402

SIGN = {"e8-nm": 1, "e8-np": -1}
NAMES = ("w", "rho", "sig", "zeta", "a")
Element = tuple[Any, Any]  # p + q b


class Ring:
    """(P + P b) / n^order with b^2 = F."""

    def __init__(self, prime: int, order: int) -> None:
        self.prime, self.order = prime, order
        self.ctx = nmod_mpoly_ctx.get(NAMES, ordering=Ordering.degrevlex, modulus=prime)
        self.zero = self.ctx.from_dict({})
        self.one = self.ctx.from_dict({(0,) * 5: 1})
        w, _, _, zeta, a = self.ctx.gens()
        self.half = pow(2, -1, prime)
        self.u = self.cut(sum(((-w) ** k for k in range(order)), self.zero), order)
        m = 1 + w
        below = w * (w + 2)
        big_a = ((m * m + 1) * a - below * zeta) * self.half
        self.f = self.cut(self.cut(big_a * (big_a - below), order) * self.cut(self.u * self.u, order), order)

    def cut(self, poly: Any, order: int) -> Any:
        return self.ctx.from_dict({e: c for e, c in poly.to_dict().items() if sum(e) < order})

    def mul(self, x: Element, y: Element, order: int) -> Element:
        p = x[0] * y[0]
        if x[1] and y[1]:
            p = p + self.cut(x[1] * y[1], order - 2) * self.f
        return self.cut(p, order), self.cut(x[0] * y[1] + x[1] * y[0], order - 1)

    def add(self, x: Element, y: Element) -> Element:
        return x[0] + y[0], x[1] + y[1]


def generators(slug: str, ring: Ring) -> list[Element]:
    """The header's G on Phi, modulo n^order."""
    order, zero, half = ring.order, ring.zero, ring.half
    w, rho, sig, zeta, a = ring.ctx.gens()
    root = limits.PRIMES[ring.prime]
    m = 1 + w
    t = ring.cut(w * w * ring.u, order)
    values: dict[str, Element] = {
        "t1": (ring.cut((-(w * (w + 2)) * a + (m * m + 1) * zeta + w * w) * ring.u * half, order), zero),
        "t2": (a, zero),
        "t3": (zeta, zero),
        "t4": ((m * rho + sig) * half, zero),
        "t5": ((m * rho - sig) * half, zero),
        "t6": ((m * sig + rho) * half, zero),
        "t7": ((rho - m * sig) * half, zero),
        "t8": (zero, ring.ctx.from_dict({(0,) * 5: (-root) % ring.prime})),
        "t9": (-t * half * SIGN[slug], zero),
    }
    variables, ideal_j, ideal_g = limits.header(slug, ring.prime)
    symbols = sympy.symbols((*variables, "I"))
    values["I"] = (ring.ctx.from_dict({(0,) * 5: root}), zero)
    powers: dict[tuple[str, int], Element] = {}

    def power(name: str, exponent: int) -> Element:
        if (name, exponent) not in powers:
            powers[name, exponent] = (
                values[name] if exponent == 1 else ring.mul(power(name, exponent - 1), values[name], order)
            )
        return powers[name, exponent]

    def evaluate(text: str) -> Element:
        polynomial = sympy.Poly(sympy.parse_expr(text.replace("^", "**")), *symbols)
        total: Element = (zero, zero)
        for exponents, coefficient in polynomial.terms():
            scalar = int(coefficient.p) * pow(int(coefficient.q), -1, ring.prime) % ring.prime
            term: Element = (ring.ctx.from_dict({(0,) * 5: scalar}), zero)
            for name, exponent in zip((*variables, "I"), exponents, strict=True):
                if exponent:
                    term = ring.mul(term, power(name, exponent), order)
            total = ring.add(total, term)
        return total

    for text in ideal_j:
        value = evaluate(text)
        if value[0] or value[1]:
            raise RuntimeError(f"{slug}: a generator of J does not vanish on Phi modulo n^{order}")
    return [evaluate(text) for text in ideal_g]


def ring_basis(ring: Ring, order: int, maximal: bool) -> list[Element]:
    """A basis of R (of m_R when maximal) modulo n^order."""
    w = ring.ctx.gens()[0]
    t = ring.cut(w * w * ring.u, order)
    base: list[Any] = []
    t_powers = [ring.one]
    for _ in range(order // 2 + 1):
        t_powers.append(ring.cut(t_powers[-1] * t, order))
    zeta = ring.ctx.gens()[3]
    for i in range(order // 2 + 1):
        for j in range(order - 2 * i):
            base.append(ring.cut(t_powers[i] * zeta**j, order))
    for exponents in itertools.product(range(order), repeat=5):
        if sum(exponents) < order and exponents[1] + exponents[2] + exponents[4] >= 1:
            base.append(ring.ctx.from_dict({exponents: 1}))
    out: list[Element] = [(p, ring.zero) for p in base if p] + [(ring.zero, ring.cut(p, order - 1)) for p in base]
    out = [x for x in out if x[0] or x[1]]
    return [x for x in out if not (maximal and x[0] == ring.one and not x[1])]


def rank_and_basis(ring: Ring, elements: list[Element], order: int) -> tuple[int, list[Element]]:
    index: dict[tuple[int, ...], int] = {}
    rows = []
    for p, q in elements:
        row = {}
        for flag, poly, limit in ((0, p, order), (1, q, order - 1)):
            for exponents, coefficient in poly.to_dict().items():
                if sum(exponents) < limit:
                    key = (flag, *(int(v) for v in exponents))
                    row[index.setdefault(key, len(index))] = int(coefficient)
        rows.append(row)
    if not index:
        return 0, []
    matrix = nmod_mat(len(rows), len(index), ring.prime)
    for i, row in enumerate(rows):
        for j, value in row.items():
            matrix[i, j] = value
    reduced, rank = matrix.rref()
    keys: list[tuple[int, ...]] = [()] * len(index)
    for key, j in index.items():
        keys[j] = key
    basis = []
    for i in range(rank):
        parts: tuple[dict[tuple[int, ...], int], dict[tuple[int, ...], int]] = ({}, {})
        for j in range(len(index)):
            value = int(reduced[i, j])
            if value:
                parts[keys[j][0]][keys[j][1:]] = value
        basis.append((ring.ctx.from_dict(parts[0]), ring.ctx.from_dict(parts[1])))
    return rank, basis


def ladder(slug: str, prime: int, degree: int, order: int) -> dict[str, Any]:
    started = time.time()
    ring = Ring(prime, order)
    gens = generators(slug, ring)

    def weight(x: Element) -> int:
        return min(
            [sum(e) for e in x[0].to_dict()] + [sum(e) + 1 for e in x[1].to_dict()],
            default=order,
        )

    low = int(min(weight(g) for g in gens))
    start = order - low * degree
    if start < 2:
        raise SystemExit(f"order {order} is below {low * degree + 2}")
    spaces = {"A": ring_basis(ring, start, False), "B": ring_basis(ring, start, True)}
    rows = []
    for d in range(1, degree + 1):
        current = start + low * d
        row = {"degree": d, "order": current}
        for key in ("A", "B"):
            products = [ring.mul(g, b, current) for g in gens for b in spaces[key]]
            row[key], spaces[key] = rank_and_basis(ring, products, current)
        row["r"] = row["A"] - row["B"]
        rows.append(row)
    return {
        "slug": slug,
        "prime": prime,
        "order": order,
        "generators": len(gens),
        "generator_order": low,
        "rows": rows,
        "seconds": round(time.time() - started, 1),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--slug", choices=tuple(SIGN), default="e8-nm")
    parser.add_argument("--prime", type=int, choices=tuple(limits.PRIMES), default=32009)
    parser.add_argument("--degree", type=int, required=True)
    parser.add_argument("--order", type=int, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    record = ladder(args.slug, args.prime, args.degree, args.order)
    if args.out:
        args.out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(record))


if __name__ == "__main__":
    main()
