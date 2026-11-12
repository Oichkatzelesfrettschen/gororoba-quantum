"""Hilbert function of the fiber cone of the monomial model of the same-sign X slice.

Model (the monomial span that monomial_probe.py finds through order 14): in P = k[[a, rho, sig, w]] the ideal of the
header's G is the monomial ideal
    M = w^2 (a, rho, sig) + w (rho, sig) (a, rho, sig)^2,
and the slice ring R = k[[t]] + (a, rho, sig) P has m_R P-saturated on M: m_R M^d = (w^2, a, rho, sig) M^d.
Then h_d = dim M^d / (w^2, a, rho, sig) M^d counts the monomials of M^d outside (w^2, a, rho, sig) M^d.
Exponents are (a, rho, sig, w).

The script prints [h_1, ..., h_dmax] for the monomial ideal M of the same-sign X slice; dmax is the first command-line
argument (default 10):

    $PYTHON docs/evidence/a5-exceptional-fibers/monomial-ladder/monomial_model.py 8
"""

import itertools
import sys

GENS: list[tuple[int, ...]] = [(1, 0, 0, 2), (0, 1, 0, 2), (0, 0, 1, 2)]
for e in itertools.product(range(4), repeat=3):
    if sum(e) == 3 and e[1] + e[2] >= 1:
        GENS.append((*e, 1))
MAX = [(0, 0, 0, 2), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0)]


def add(x, y):
    return tuple(i + j for i, j in zip(x, y, strict=True))


def divides(g, m):
    return all(i <= j for i, j in zip(g, m, strict=True))


def minimal(monos):
    out = []
    for m in sorted(set(monos), key=sum):
        if not any(divides(g, m) for g in out):
            out.append(m)
    return out


def hilbert(dmax):
    power = [(0, 0, 0, 0)]
    values = []
    for _ in range(dmax):
        power = minimal([add(p, g) for p in power for g in GENS])
        lower = minimal([add(p, x) for p in power for x in MAX])
        # monomials of M^d outside m M^d: multiples p * w^e of minimal generators, e in {0, 1}, and nothing else,
        # since any other multiplier lies in (w^2, a, rho, sig).
        count = set()
        for p in power:
            for e in (0, 1):
                m = add(p, (0, 0, 0, e))
                if not any(divides(g, m) for g in lower):
                    count.add(m)
        values.append(len(count))
    return values


if __name__ == "__main__":
    print(hilbert(int(sys.argv[1]) if len(sys.argv) > 1 else 10))
