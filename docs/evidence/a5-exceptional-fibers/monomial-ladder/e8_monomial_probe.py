"""Probe: is the truncated ideal I of the E8-bar slice ring a span of monomials in some coordinate system?

The ring is P + P b, P = k[[w, rho, sig, zeta, a]], b^2 = F = X (X - s), X = A / m, s = w (w + 2) / m.
Coordinate systems tried (each an automorphism of P that fixes b, so the filtration by weight is kept):

    orig   (w, rho, sig, zeta, a)
    x      (w, rho, sig, zeta, X)            a = (2 m X + (m^2 - 1) zeta) / (m^2 + 1)
    xy     (Y, rho, sig, zeta, X)            Y = X - s, so b^2 = X Y (the A1 toric cover u^2, v^2, u v)
    xs     (s, rho, sig, zeta, X)            s in place of w
    xyt    xy with b replaced by b - X       (b - X)(b + X) = -s X

A subspace is a monomial span exactly when every row of its reduced echelon form has one nonzero entry.

    $PYTHON docs/evidence/a5-exceptional-fibers/monomial-ladder/e8_monomial_probe.py ORDER [PRIME] [SLUG] [--rows]
"""

import sys

import e8_ladder as lad
from flint import nmod_mat

N = int(sys.argv[1])
p = int(sys.argv[2]) if len(sys.argv) > 2 else 32009
slug = sys.argv[3] if len(sys.argv) > 3 else "e8-nm"
ring = lad.Ring(p, N)
ctx = ring.ctx
gens = lad.generators(slug, ring)
w, rho, sig, zeta, a = ctx.gens()
one = ring.one
half = ring.half


def cut(q, n=N):
    return ring.cut(q, n)


def series_inverse(q):
    """1 / q for q with constant term 1, modulo n^N."""
    e = one - q
    out, term = one, one
    for _ in range(N):
        term = cut(term * e)
        out = out + term
    return out


m = 1 + w
u = ring.u  # 1 / m
s_of_w = cut(w * (w + 2) * u)
# a in terms of (w, zeta, X): a = (2 m X + w (w + 2) zeta) / (m^2 + 1); m^2 + 1 = 2 (1 + w + w^2 / 2)
inv = series_inverse(one + w + w * w * half)
a_of_x = cut((m * a + w * (w + 2) * zeta * half) * inv)  # the variable named a now stands for X


def reversion(series):
    """g with series(g(w)) = w, for series = c w + ..., in the single variable w, modulo n^N."""
    c = int(series.to_dict()[(1, 0, 0, 0, 0)])
    g = ctx.from_dict({(1, 0, 0, 0, 0): pow(c, -1, p)})
    for _ in range(N):
        g = cut(g - (substitute(series, {0: g}) - w) * pow(c, -1, p))
    return g


def substitute(q, images):
    """q with variable i replaced by images[i] (others kept), modulo n^N."""
    table = {}

    def power(i, k):
        if (i, k) not in table:
            table[i, k] = one if k == 0 else cut(power(i, k - 1) * images[i])
        return table[i, k]

    out = ring.zero
    for e, c in q.to_dict().items():
        rest = list(e)
        term = None
        for i in images:
            rest[i] = 0
        term = ctx.from_dict({tuple(rest): int(c)})
        for i in images:
            if e[i]:
                term = cut(term * power(i, int(e[i])))
        out = out + term
    return cut(out)


w_of_s = reversion(s_of_w)  # w as a series in the variable named w, which now stands for s
systems = {
    "orig": {},
    "x": {4: a_of_x},
}
# xs: w -> w_of_s, then a -> a_of_x evaluated at that w
systems["xs"] = {0: w_of_s, 4: substitute(a_of_x, {0: w_of_s})}
# xy: s = X - Y with Y the variable named w and X the variable named a
w_of_xy = substitute(w_of_s, {0: a - w})
systems["xy"] = {0: w_of_xy, 4: substitute(a_of_x, {0: w_of_xy})}


def echelon(elements):
    index = {}
    rows = []
    for x in elements:
        row = {}
        for flag, poly, limit in ((0, x[0], N), (1, x[1], N - 1)):
            for e, c in poly.to_dict().items():
                if sum(e) < limit:
                    row[index.setdefault((flag, *(int(v) for v in e)), len(index))] = int(c)
        if row:
            rows.append(row)
    mat = nmod_mat(len(rows), len(index), p)
    for i, row in enumerate(rows):
        for j, v in row.items():
            mat[i, j] = v
    red, r = mat.rref()
    keys = [None] * len(index)
    for k, j in index.items():
        keys[j] = k
    return red, r, keys


def report(label, elements):
    red, r, keys = echelon(elements)
    sizes = [sum(1 for j in range(len(keys)) if int(red[i, j])) for i in range(r)]
    single = sum(v == 1 for v in sizes)
    print(
        slug, p, "order", N, label, "rank", r, "single-monomial rows", single, "largest support", max(sizes), flush=True
    )
    return single == r


for label, maximal in (("I", False), ("m_R I", True)):
    span = [ring.mul(g, x, N) for g in gens for x in lad.ring_basis(ring, N, maximal)]
    span = [x for x in span if x[0] or x[1]]
    for name, images in systems.items():
        moved = [(substitute(x[0], images), cut(substitute(x[1], images), N - 1)) for x in span] if images else span
        report(f"{label} [{name}]", moved)
        if name == "xy":
            # b -> b + X: p + q b becomes (p + q X) + q b
            shifted = [(cut(x[0] + x[1] * a), x[1]) for x in moved]
            report(f"{label} [xy, b - X]", shifted)

if "--rows" in sys.argv:
    span = [ring.mul(g, x, N) for g in gens for x in lad.ring_basis(ring, N, False)]
    red, r, keys = echelon([x for x in span if x[0] or x[1]])
    print("columns are (b flag, w, rho, sig, zeta, a)")
    for i in range(r):
        row = [(keys[j], int(red[i, j])) for j in range(len(keys)) if int(red[i, j])]
        if len(row) > 1:
            print(" ", row)
    print("generators (lowest-weight parts):")
    for g in gens:
        low = min([sum(e) for e in g[0].to_dict()] + [sum(e) + 1 for e in g[1].to_dict()])
        print(
            "  weight",
            low,
            {e: int(c) for e, c in g[0].to_dict().items() if sum(e) == low},
            "b*",
            {e: int(c) for e, c in g[1].to_dict().items() if sum(e) + 1 == low},
        )
