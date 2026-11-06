"""Sign changes that relate the two incidences: which coordinate signs carry the slice and center of one onto the other.

usage: xarc_flip.py PRIME     (reads both headers of PRIME; prints each sign change matching 10 or more generators of J)
A sign change multiplies the coefficient of a monomial by -1 for each flipped coordinate that occurs to an odd power;
generators compare up to an overall sign.
"""

from __future__ import annotations

import itertools
import sys
from pathlib import Path

from xarc_common import VARS, Header, Poly, load_headers

MIN_MATCHING_J = 10


def canon(poly: Poly, p: int) -> tuple[tuple[tuple[int, ...], int], ...]:
    """The generator up to an overall sign: the lexicographically smaller of the term lists of poly and -poly."""
    a = tuple(sorted(poly.items()))
    b = tuple(sorted((k, (-v) % p) for k, v in poly.items()))
    return min(a, b)


def flipped(poly: Poly, flips: tuple[int, ...], p: int) -> Poly:
    out: Poly = {}
    for ex, cf in poly.items():
        sgn = 1
        for e, f in zip(ex, flips, strict=True):
            if f and e % 2:
                sgn = -sgn
        out[ex] = cf * sgn % p
    return out


def matches(src: Header, dst: Header) -> list[tuple[tuple[int, ...], int, list[tuple[int, int]]]]:
    """(flips, matching J generators, matching G pairs) for every sign change of SRC that relates it to DST."""
    p = src.prime
    dst_j = {canon(j, p) for j in dst.j}
    dst_g = [canon(g, p) for g in dst.g]
    rows = []
    for flips in itertools.product((0, 1), repeat=len(VARS)):
        j_hits = sum(1 for j in src.j if canon(flipped(j, flips, p), p) in dst_j)
        g_hits = [(i, dst_g.index(c)) for i, g in enumerate(src.g) if (c := canon(flipped(g, flips, p), p)) in dst_g]
        if j_hits >= MIN_MATCHING_J or g_hits:
            rows.append((flips, j_hits, g_hits))
    return rows


def main(prime: int, root: int | None = None, header_dir: Path | None = None) -> None:
    headers = load_headers(prime, root, header_dir)
    for flips, j_hits, g_hits in matches(headers["xp-nm"], headers["xm-np"]):
        if j_hits >= MIN_MATCHING_J:
            print("flip", dict(zip(VARS, flips, strict=True)), "matching J gens", j_hits)
        if g_hits:
            print("flip", flips, "G matches", g_hits)


if __name__ == "__main__":
    main(int(sys.argv[1]))
