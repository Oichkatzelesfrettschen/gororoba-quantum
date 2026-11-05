"""Header reading and exact F_p polynomial tools of the opposite-sign X arc certificate.

A header is the Singular file `SLUG.sing` of one incidence at one prime. Line 1 is
`ring r=P,(t1,t2,t4,t5,t6,t7,t9),dp;`, line 2 is `number I=ROOT;` with ROOT a square root of -1 modulo P, line 3
holds the 12 generators `ideal J=...;` of the slice V(J) and line 4 the 3 generators `ideal G=...;` of the blow-up
center. The prime and the root come from the first two lines.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import sympy

VARS = ("t1", "t2", "t4", "t5", "t6", "t7", "t9")
NVAR_LOCAL = len(VARS)
HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
INPUTS = EVIDENCE / "working" / "build" / "inputs"
INCIDENCES = {"xp-nm": "X+->N-", "xm-np": "X-->N+"}
# Sign s9 of the t9 coordinate of the parametrization: t9 = s9 * t9xp.
SIGN9 = {"xp-nm": 1, "xm-np": -1}
# Exponent vector of t9 alone.
T9_KEY = (0, 0, 0, 0, 0, 0, 1)
# Index of the generator of J whose t9 term the sign-flip control reverses.
FLIPPED_GENERATOR = 11

Poly = dict[tuple[int, ...], int]

_RING = re.compile(r"ring r=(\d+),\(t1,t2,t4,t5,t6,t7,t9\),dp;")
_ROOT = re.compile(r"number I=(\d+);")


@dataclass(frozen=True)
class Header:
    """The slice (J, G) of one incidence at one prime."""

    slug: str
    path: Path
    prime: int
    root: int
    lines: tuple[str, str, str, str]
    j: tuple[Poly, ...]
    g: tuple[Poly, ...]

    @property
    def preamble(self) -> str:
        """The four header lines that every generated Singular script starts with."""
        return "\n".join(self.lines)


def inv(a: int, p: int) -> int:
    return pow(a % p, -1, p)


def _poly_from_text(text: str, p: int) -> Poly:
    syms = sympy.symbols(VARS)
    expr = sympy.sympify(text.replace("^", "**"), locals=dict(zip(VARS, syms, strict=True)))
    pol = sympy.Poly(expr, *syms, modulus=p)
    out: Poly = {}
    for mon, cf in pol.terms():
        c = int(cf) % p
        if c:
            out[tuple(int(e) for e in mon)] = c
    return out


def _ideal_text(line: str, name: str) -> str:
    m = re.fullmatch(rf"ideal {name}=(.*);", line)
    if m is None:
        raise ValueError(f"line is not `ideal {name}=...;`")
    return m.group(1)


def read_header(path: Path, slug: str, prime: int | None = None, root: int | None = None) -> Header:
    """Parse a header; a given prime or root must equal the header's, and the root must square to -1."""
    if slug not in INCIDENCES:
        raise ValueError(f"unknown incidence {slug}")
    lines = path.read_text().splitlines()
    if len(lines) < 4:
        raise ValueError(f"{path.name}: fewer than four lines")
    ring = _RING.fullmatch(lines[0])
    rt = _ROOT.fullmatch(lines[1])
    if ring is None or rt is None:
        raise ValueError(f"{path.name}: lines 1 and 2 are not the ring and root lines")
    p, i = int(ring.group(1)), int(rt.group(1))
    if not sympy.isprime(p):
        raise ValueError(f"{path.name}: {p} is not prime")
    if (i * i + 1) % p:
        raise ValueError(f"{path.name}: {i} is not a square root of -1 modulo {p}")
    if prime is not None and prime != p:
        raise ValueError(f"{path.name}: header prime {p} differs from the requested {prime}")
    if root is not None and root != i:
        raise ValueError(f"{path.name}: header root {i} differs from the requested {root}")
    j = [_poly_from_text(t, p) for t in _ideal_text(lines[2], "J").split(",")]
    g = [_poly_from_text(t, p) for t in _ideal_text(lines[3], "G").split(",")]
    return Header(slug, path, p, i, (lines[0], lines[1], lines[2], lines[3]), tuple(j), tuple(g))


def find_header_dir(prime: int, root: int | None = None, inputs: Path = INPUTS) -> Path:
    """The single directory `pPRIME-rROOT` of INPUTS that holds the headers of both incidences."""
    pattern = f"p{prime}-r{root}" if root is not None else f"p{prime}-r*"
    found = sorted(d for d in inputs.glob(pattern) if all((d / f"{slug}.sing").is_file() for slug in INCIDENCES))
    if len(found) != 1:
        raise ValueError(f"{len(found)} directories {pattern} under {inputs} hold both incidence headers, not 1")
    return found[0]


def load_headers(prime: int, root: int | None = None, header_dir: Path | None = None) -> dict[str, Header]:
    """Both headers at one prime; the two must agree on prime and root."""
    directory = header_dir if header_dir is not None else find_header_dir(prime, root)
    out = {slug: read_header(directory / f"{slug}.sing", slug, prime, root) for slug in INCIDENCES}
    if len({(h.prime, h.root) for h in out.values()}) != 1:
        raise ValueError("the two headers differ in prime or root")
    return out


def prime_dir(kind: str, prime: int) -> Path:
    """HERE/kind/pPRIME, the home of the logs, scripts, work files and records of one prime."""
    return HERE / kind / f"p{prime}"


def eval_int(poly: Poly, x: tuple[int, ...] | list[int], p: int) -> int:
    tot = 0
    for ex, cf in poly.items():
        t = cf
        for xi, k in zip(x, ex, strict=True):
            if k:
                t = t * pow(xi, k, p) % p
        tot = (tot + t) % p
    return tot
