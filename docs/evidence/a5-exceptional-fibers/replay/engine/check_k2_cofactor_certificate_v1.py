"""Independent checker for a5-k2-cofactor-certificate-v1 files (standard library only).

Checks, each exact over F_p:
 1. Header: J and G in the file equal the polynomials parsed from the header file when --header is given.
 2. Identity: for each quadric q, u(0) != 0 and u * q(G) = sum_k a_k J_k + sum b_{i,ab} t_i G_a G_b as polynomials
    in F_p[s] (every product expanded; the sums are grouped as sum_i t_i sum_a G_a (sum_b b_{i,ab} G_b), which is the
    same polynomial).
 3. Groebner basis B in dp (degree reverse lexicographic, y_1 > ... > y_n): each element monic and homogeneous; B is
    reduced (no term of an element is divisible by the leading monomial of another element, nor a non-leading term
    by its own); every S-polynomial of a pair with non-coprime leading monomials reduces to 0 modulo B, so B is a
    Groebner basis of <B>; every quadric reduces to 0 modulo B (K2 contained in <B>); every element of B equals
    sum_j c_j q_j with the recorded cofactors (<B> contained in K2). Together: B is the reduced Groebner basis of K2.
 4. Hilbert function: h_d = number of monomials of degree d outside the leading ideal of B, for d = 1..dmax, equals the
    recorded h_d, and the recorded numerator N satisfies N(t) / (1-t)^n = sum h_d t^d through degree dmax.
 5. With --retained FILE.jsonl, h_d equals the retained k2-hilbert row of the same fiber and prime for every degree the
    row lists.

Usage: check_k2_cofactor_certificate_v1.py CERT.json [--header HEADER.sing] [--retained k2-hilbert.jsonl] [--jobs N]
Exit 0 only when every check passes.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import multiprocessing
import re
import sys
from pathlib import Path

SCHEMA = "a5-k2-cofactor-certificate-v1"


class Reject(Exception):
    pass


def need(cond: bool, msg: str) -> None:
    if not cond:
        raise Reject(msg)


def to_dict(terms: list, p: int) -> dict[tuple[int, ...], int]:
    out: dict[tuple[int, ...], int] = {}
    for c, e in terms:
        k = tuple(e)
        out[k] = (out.get(k, 0) + c) % p
    return {k: c for k, c in out.items() if c}


def pmul(a: dict, b: dict, p: int) -> dict:
    out: dict = {}
    get = out.get
    for ea, ca in a.items():
        for eb, cb in b.items():
            k = tuple(x + y for x, y in zip(ea, eb, strict=False))
            out[k] = (get(k, 0) + ca * cb) % p
    return {k: c for k, c in out.items() if c}


def padd(acc: dict, b: dict, p: int, shift: tuple[int, ...] | None = None) -> None:
    for e, c in b.items():
        k = e if shift is None else tuple(x + y for x, y in zip(e, shift, strict=False))
        v = (acc.get(k, 0) + c) % p
        if v:
            acc[k] = v
        else:
            acc.pop(k, None)


def check_header(doc: dict, header: Path) -> None:
    text = header.read_text().replace("\n", "")
    m = re.search(r"ring r=(\d+),\(([^)]*)\)", text)
    if m is None:
        raise Reject("header has no ring line")
    p, names = int(m.group(1)), m.group(2).split(",")
    need(p == doc["prime"], "prime differs from header")
    need(names == doc["vars"]["s"], "s variables differ from header")
    need(hashlib.sha256(header.read_bytes()).hexdigest() == doc["header"]["sha256"], "header sha256 differs")
    idx = {v: i for i, v in enumerate(names)}
    term = re.compile(r"([+-]?)([^+-]+)")

    def parse(s: str) -> dict:
        acc: dict = {}
        for t in term.finditer("".join(s.split())):
            coef = -1 if t.group(1) == "-" else 1
            ex = [0] * len(names)
            for piece in t.group(2).split("*"):
                if piece.isdigit():
                    coef *= int(piece)
                else:
                    v, _, e = piece.partition("^")
                    ex[idx[v]] += int(e or 1)
            acc[tuple(ex)] = (acc.get(tuple(ex), 0) + coef) % p
        return {k: c for k, c in acc.items() if c}

    for key, nm in (("J", "J"), ("G", "G")):
        sm = re.search(rf"ideal {nm}=([^;]*);", text)
        if sm is None:
            raise Reject(f"header has no ideal {nm}")
        polys = [x for x in sm.group(1).split(",") if x.strip()]
        need(len(polys) == len(doc[key]), f"{key} length differs from header")
        for i, s in enumerate(polys):
            need(parse(s) == to_dict(doc[key][i], p), f"{key}[{i}] differs from header")


class Ctx:
    """Parsed polynomials shared by the identity checks."""

    def __init__(self, doc: dict) -> None:
        self.p = doc["prime"]
        self.ns = len(doc["vars"]["s"])
        self.J = [to_dict(t, self.p) for t in doc["J"]]
        self.G = [to_dict(t, self.p) for t in doc["G"]]
        self.n = len(self.G)
        self.gg: dict[tuple[int, int], dict] = {}

    def pair(self, a: int, b: int) -> dict:
        key = (a, b) if a <= b else (b, a)
        if key not in self.gg:
            self.gg[key] = pmul(self.G[key[0]], self.G[key[1]], self.p)
        return self.gg[key]


def q_of_G(ctx: Ctx, q: list) -> dict:
    acc: dict = {}
    for c, e in q:
        idx = [i for i, k in enumerate(e) for _ in range(k)]
        need(len(idx) == 2, "quadric term is not of degree 2")
        t = ctx.pair(idx[0], idx[1])
        padd(acc, {k: (v * c) % ctx.p for k, v in t.items()}, ctx.p)
    return acc


def check_quadric(ctx: Ctx, entry: dict) -> int:
    """Return the number of cofactor terms expanded; raise Reject when the identity fails."""
    p, ns = ctx.p, ctx.ns
    u = to_dict(entry["u"], p)
    need(u.get((0,) * ns, 0) != 0, "unit has zero constant term")
    lhs = pmul(u, q_of_G(ctx, entry["q"]), p)
    rhs: dict = {}
    count = 0
    for k, terms in entry["a"]:
        need(0 <= k < len(ctx.J), "J index out of range")
        count += len(terms)
        padd(rhs, pmul(to_dict(terms, p), ctx.J[k], p), p)
    by_ia: dict[tuple[int, int], dict] = {}
    for i, a, b, terms in entry["b"]:
        need(0 <= i < ns and 0 <= a <= b < ctx.n, "b index out of range")
        count += len(terms)
        inner = by_ia.setdefault((i, a), {})
        padd(inner, pmul(to_dict(terms, p), ctx.G[b], p), p)
    for (i, a), inner in by_ia.items():
        shift = tuple(1 if x == i else 0 for x in range(ns))
        padd(rhs, pmul(ctx.G[a], inner, p), p, shift)
    need(lhs == rhs, f"identity fails ({len(lhs)} vs {len(rhs)} terms)")
    return count


def _worker(args: tuple) -> tuple[int, int | str]:
    j = args[0]
    try:
        return j, check_quadric(_CTX, _DOC["quadrics"][j])
    except Reject as err:
        return j, str(err)


_CTX: Ctx
_DOC: dict


def check_identities(doc: dict, jobs: int) -> list[int]:
    global _CTX, _DOC
    _CTX, _DOC = Ctx(doc), doc
    ids = range(len(doc["quadrics"]))
    if jobs > 1:
        with multiprocessing.get_context("fork").Pool(jobs) as pool:
            res = pool.map(_worker, [(j,) for j in ids], chunksize=1)
    else:
        res = [_worker((j,)) for j in ids]
    bad = [(j, r) for j, r in res if isinstance(r, str)]
    need(not bad, f"identity rejected for quadrics {bad}")
    return [r for _, r in res if isinstance(r, int)]


# ---- Groebner side -----------------------------------------------------------------------------------------------


def key_dp(e: tuple[int, ...]) -> tuple:
    return (sum(e), tuple(-x for x in reversed(e)))


def lead(poly: dict) -> tuple[int, ...]:
    return max(poly, key=key_dp)


def divides(a: tuple[int, ...], b: tuple[int, ...]) -> bool:
    return all(x <= y for x, y in zip(a, b, strict=False))


def normal_form(poly: dict, basis: list[dict], leads: list[tuple[int, ...]], p: int) -> dict:
    """Full reduction of poly modulo the monic basis (division until no term is divisible by a leading monomial)."""
    rem = dict(poly)
    out: dict = {}
    while rem:
        m = lead(rem)
        c = rem[m]
        for g, lm in zip(basis, leads, strict=False):
            if divides(lm, m):
                s = tuple(x - y for x, y in zip(m, lm, strict=False))
                for e, cg in g.items():
                    k = tuple(x + y for x, y in zip(e, s, strict=False))
                    v = (rem.get(k, 0) - c * cg) % p
                    if v:
                        rem[k] = v
                    else:
                        rem.pop(k, None)
                break
        else:
            out[m] = c
            del rem[m]
    return out


def check_groebner(doc: dict) -> dict:
    p = doc["prime"]
    gbd = doc["groebner"]
    need(gbd["order"] == "dp", "order is not dp")
    n = len(doc["vars"]["y"])
    basis = [to_dict(t, p) for t in gbd["basis"]]
    need(all(basis), "zero element in the basis")
    leads = [lead(g) for g in basis]
    for g, lm in zip(basis, leads, strict=False):
        need(g[lm] == 1, "basis element is not monic")
        need(len({sum(e) for e in g}) == 1, "basis element is not homogeneous")
    for i, g in enumerate(basis):
        for e in g:
            for k, lm in enumerate(leads):
                if k == i and e == lm:
                    continue
                need(not divides(lm, e), f"basis not reduced: term of element {i} divisible by leading monomial {k}")
    for i, j in itertools.combinations(range(len(basis)), 2):
        a, b = leads[i], leads[j]
        if all(min(x, y) == 0 for x, y in zip(a, b, strict=False)):
            continue
        lcm = tuple(max(x, y) for x, y in zip(a, b, strict=False))
        sa = tuple(x - y for x, y in zip(lcm, a, strict=False))
        sb = tuple(x - y for x, y in zip(lcm, b, strict=False))
        s: dict = {}
        padd(s, basis[i], p, sa)
        padd(s, {e: (-c) % p for e, c in basis[j].items()}, p, sb)
        need(not normal_form(s, basis, leads, p), f"S-polynomial of elements {i} and {j} does not reduce to 0")
    quads = [to_dict(e["q"], p) for e in doc["quadrics"]]
    for j, q in enumerate(quads):
        need(not normal_form(q, basis, leads, p), f"quadric {j} does not reduce to 0 modulo the basis")
    for m, cof in enumerate(gbd["cofactors"]):
        acc: dict = {}
        for j, terms in cof:
            padd(acc, pmul(to_dict(terms, p), quads[j], p), p)
        need(acc == basis[m], f"basis element {m} is not the recorded combination of the quadrics")
    # standard monomials by degree
    dmax = max(int(d) for d in gbd["hilbert"]["h"])
    h: dict[int, int] = {}
    for d in range(1, dmax + 1):
        cnt = 0
        for comp in itertools.combinations(range(d + n - 1), n - 1):
            prev, exps = -1, []
            for c in comp:
                exps.append(c - prev - 1)
                prev = c
            exps.append(d + n - 1 - prev - 1)
            if not any(divides(lm, tuple(exps)) for lm in leads):
                cnt += 1
        h[d] = cnt
    for d, v in h.items():
        need(gbd["hilbert"]["h"][str(d)] == v, f"h_{d} recorded {gbd['hilbert']['h'][str(d)]} but the basis gives {v}")
    series = [1] + [h[d] for d in range(1, dmax + 1)]
    binom = [1]
    for k in range(1, n + 1):
        binom.append(binom[-1] * (n - k + 1) // k)
    num = [sum((-1) ** k * binom[k] * series[e - k] for k in range(min(e, n) + 1)) for e in range(dmax + 1)]
    rec = list(gbd["hilbert"]["numerator"]) + [0] * (dmax + 1)
    need(num == rec[: dmax + 1], f"numerator {gbd['hilbert']['numerator']} does not give the series (computed {num})")
    return h


def check_retained(doc: dict, h: dict, path: Path) -> int:
    rows = [json.loads(x) for x in path.read_text().splitlines() if x.strip()]
    rows = [r for r in rows if r["fiber"] == doc["fiber"] and r["prime"] == doc["prime"]]
    need(bool(rows), "no retained row for this fiber and prime")
    n = 0
    for r in rows:
        for d, v in r["h"].items():
            need(h[int(d)] == v, f"h_{d} = {h[int(d)]} but the retained row has {v}")
            n += 1
    return n


def run(path: Path, header: Path | None, retained: Path | None, jobs: int) -> dict:
    doc = json.loads(path.read_text())
    need(doc.get("schema") == SCHEMA, "schema mismatch")
    if header is not None:
        check_header(doc, header)
    counts = check_identities(doc, jobs)
    h = check_groebner(doc)
    out = {"identities": len(counts), "cofactor_terms": sum(counts), "h": h}
    if retained is not None:
        out["retained_degrees_compared"] = check_retained(doc, h, retained)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cert")
    ap.add_argument("--header", default=None)
    ap.add_argument("--retained", default=None)
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    try:
        res = run(Path(a.cert), Path(a.header) if a.header else None, Path(a.retained) if a.retained else None, a.jobs)
    except Reject as err:
        print(f"REJECT: {err}")
        sys.exit(1)
    print("ACCEPT", json.dumps(res))


if __name__ == "__main__":
    main()
