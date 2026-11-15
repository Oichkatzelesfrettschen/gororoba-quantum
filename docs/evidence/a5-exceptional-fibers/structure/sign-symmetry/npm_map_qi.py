"""Compare the E8-bar -> N+ and N- fiber inputs over Q(i) under sigma = (t8, t9) -> (-t8, -t9).

The producer's phase-one script (`fiber_inputs.py`, through `rees._phase_one_script`) runs over Q(i) instead of
F_p: both rings become (0,I) with minpoly I^2 + 1, the rewrite `base_locus.py` applies for its field q. Singular
prints every term of the reduced J and G as a coefficient string and an exponent vector; the coefficients are parsed
as elements a + b i of Q(i) with exact rationals. Three checks follow:

- identity: for every generator f of J+ and G+ some generator g of J- or G- satisfies f(sigma) = c g with c a unit
  of Z[i], read coefficient by coefficient, and the matching is a bijection;
- control: the sign change t9 -> -t9 alone, which `sign_search.log` records as moving G+ off G- at the primes,
  fails the G identity;
- reduction: substituting I -> root and reducing modulo p gives the tracked F_p header of the same slug at
  (32009, 10754) and (32029, 9115): G generator by generator up to a nonzero scalar, and J as an ideal (each side
  reduces to zero modulo a standard basis of the other in Singular over F_p, since the char-0 and char-p standard
  bases differ in their tail reduction), so the Q(i) headers are the producer's own.

Usage, from the repository root:
"$PYTHON" docs/evidence/a5-exceptional-fibers/structure/sign-symmetry/npm_map_qi.py OUT.json
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "docs" / "evidence" / "a5-kernel-attachments"))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import fiber_inputs as fi  # noqa: E402

import parallel  # noqa: E402

INPUTS = ROOT / "docs" / "evidence" / "a5-exceptional-fibers" / "working" / "build" / "inputs"
SURVIVORS = INPUTS / "survivors"
SLUGS = ("e8-np", "e8-nm")
NVARS = 9
SIGMA = (1, 1, 1, 1, 1, 1, 1, -1, -1)
CONTROL = (1, 1, 1, 1, 1, 1, 1, 1, -1)
SPECIALIZATIONS = ((32009, 10754), (32029, 9115))
SCAFFOLD_PRIME, SCAFFOLD_ROOT = 32009, 10754
TIMEOUT_SECONDS = 3600
TERMS = """for(int k=1;k<=size(ReducedJ);k++){for(int m=1;m<=size(ReducedJ[k]);m++){
  "TERM J",k,string(leadcoef(ReducedJ[k][m])),"|",string(leadexp(ReducedJ[k][m]));}}
for(int k=1;k<=size(ReducedG);k++){for(int m=1;m<=size(ReducedG[k]);m++){
  "TERM G",k,string(leadcoef(ReducedG[k][m])),"|",string(leadexp(ReducedG[k][m]));}}
"RESULT ring",varstr(basering);
quit;"""


class Gauss:
    """An element re + im * i of Q(i) with exact rational parts."""

    __slots__ = ("re", "im")

    def __init__(self, re: Fraction | int = 0, im: Fraction | int = 0) -> None:
        self.re, self.im = Fraction(re), Fraction(im)

    def _lift(self, other: object) -> Gauss:
        if isinstance(other, Gauss):
            return other
        if isinstance(other, (int, Fraction)):
            return Gauss(other)
        raise TypeError(f"no Q(i) value for {other!r}")

    def __add__(self, other: object) -> Gauss:
        o = self._lift(other)
        return Gauss(self.re + o.re, self.im + o.im)

    __radd__ = __add__

    def __neg__(self) -> Gauss:
        return Gauss(-self.re, -self.im)

    def __sub__(self, other: object) -> Gauss:
        return self + (-self._lift(other))

    def __rsub__(self, other: object) -> Gauss:
        return self._lift(other) - self

    def __mul__(self, other: object) -> Gauss:
        o = self._lift(other)
        return Gauss(self.re * o.re - self.im * o.im, self.re * o.im + self.im * o.re)

    __rmul__ = __mul__

    def __truediv__(self, other: object) -> Gauss:
        o = self._lift(other)
        n = o.re * o.re + o.im * o.im
        if n == 0:
            raise ZeroDivisionError("division by zero in Q(i)")
        return self * Gauss(o.re / n, -o.im / n)

    def __rtruediv__(self, other: object) -> Gauss:
        return self._lift(other) / self

    def __pow__(self, k: int) -> Gauss:
        out = Gauss(1)
        for _ in range(k):
            out = out * self
        return out

    def __eq__(self, other: object) -> bool:
        o = self._lift(other)
        return self.re == o.re and self.im == o.im

    def __hash__(self) -> int:
        return hash((self.re, self.im))

    def text(self) -> str:
        return f"{self.re}+{self.im}*i"


COEFFICIENT = re.compile(r"[0-9I+\-*/^() ]+")


def gauss(text: str) -> Gauss:
    """Parse a Singular Q(i) coefficient: integers, I, + - * / ^ and parentheses only."""
    if not COEFFICIENT.fullmatch(text):
        raise ValueError(f"unexpected coefficient text {text!r}")
    expr = re.sub(r"(?<!\*\*)(\d+)", r"Fraction(\1)", text.replace("^", "**"))
    value = eval(expr, {"__builtins__": {}}, {"Fraction": Fraction, "I": Gauss(0, 1)})  # noqa: S307
    return value if isinstance(value, Gauss) else Gauss(value)


Poly = dict[tuple[int, ...], Gauss]


def qi_script(slug: str) -> str:
    spec = fi.SPEC_BY_SLUG[slug]
    task = fi._task(spec.incidence)
    data = fi.basepoints._schur_coordinates(fi.rees._base_task(task))
    candidates = fi._candidates(task, data, SURVIVORS)
    text = fi.rees._phase_one_script(
        SCAFFOLD_ROOT, task, data, tuple(candidates), prime=SCAFFOLD_PRIME, embedding=False
    )
    text, count = re.subn(
        rf"ring (\w+)={SCAFFOLD_PRIME},\(([^)]*)\),dp;\nnumber I={SCAFFOLD_ROOT};",
        r"ring \1=(0,I),(\2),dp; minpoly=I^2+1;",
        text,
    )
    if count != 2 or str(SCAFFOLD_PRIME) in text or re.search(rf"\b{SCAFFOLD_ROOT}\b", text):
        raise RuntimeError(f"{slug}: the Q(i) rewrite left the scaffold prime or root ({count} rings rewritten)")
    text = text.replace("quit;", "").rstrip() + "\n" + TERMS + "\n"
    return text


def run(slug: str) -> dict:
    script = qi_script(slug)
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp, f"{slug}.sing")
        src.write_text(script, encoding="utf-8")
        res = subprocess.run(
            ["Singular", "-q", "--no-rc", src.name],
            cwd=tmp,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            check=False,
        )
    bad = [ln for ln in res.stdout.splitlines() if ln.lstrip().startswith("?")]
    if res.returncode != 0 or bad:
        raise RuntimeError(f"{slug}: Singular exit {res.returncode}; {bad[:3]}")
    polys: dict[str, dict[int, Poly]] = {"J": {}, "G": {}}
    results: dict[str, str] = {}
    for ln in res.stdout.splitlines():
        if ln.startswith("TERM "):
            head, exps = ln[5:].split("|")
            kind, k, coef = head.split(None, 2)
            exp = tuple(int(e) for e in exps.strip().split(","))
            if len(exp) != NVARS:
                raise RuntimeError(f"{slug}: exponent vector of length {len(exp)}")
            polys[kind].setdefault(int(k), {})[exp] = gauss(coef.strip())
        elif ln.startswith("RESULT "):
            key, _, value = ln[7:].partition(" ")
            results.setdefault(key, value.strip())
    return {
        "slug": slug,
        "script_sha256": hashlib.sha256(script.encode()).hexdigest(),
        "J": [polys["J"][k] for k in sorted(polys["J"])],
        "G": [polys["G"][k] for k in sorted(polys["G"])],
        "selected": [int(results[f"selected_{i}"]) for i in range(1, int(results["selected_count"]) + 1)],
        "eliminated": [results[f"eliminated_{i}"] for i in range(1, int(results["eliminated_count"]) + 1)],
        "germ_dimension": int(results["germ_dimension"]),
        "ring": results["ring"],
    }


def act(poly: Poly, signs: tuple[int, ...]) -> Poly:
    out = {}
    for m, c in poly.items():
        odd = sum(e for e, s in zip(m, signs, strict=True) if s < 0) % 2
        out[m] = -c if odd else c
    return out


def ratio(a: Poly, b: Poly) -> Gauss | None:
    """The scalar c with a = c b, or None."""
    if a.keys() != b.keys() or not a:
        return None
    m0 = next(iter(a))
    c = a[m0] / b[m0]
    return c if all(a[m] == c * b[m] for m in a) else None


UNITS = {Gauss(1): "1", Gauss(-1): "-1", Gauss(0, 1): "i", Gauss(0, -1): "-i"}


def identity(src: list[Poly], dst: list[Poly], signs: tuple[int, ...]) -> dict:
    hits: list[list | None] = []
    for a in src:
        moved = act(a, signs)
        hit = None
        for j, b in enumerate(dst):
            c = ratio(moved, b)
            if c is not None:
                hit = [j + 1, UNITS.get(c, c.text())]
                break
        hits.append(hit)
    images = [h[0] for h in hits if h is not None]
    return {
        "map": hits,
        "bijection_by_units": all(h is not None and h[1] in UNITS.values() for h in hits)
        and len(set(images)) == len(dst) == len(src),
    }


def reduce_mod(poly: Poly, p: int, root: int) -> dict[tuple[int, ...], int]:
    out = {}
    for m, c in poly.items():

        def red(q: Fraction) -> int:
            return q.numerator * pow(q.denominator, -1, p) % p

        v = (red(c.re) + red(c.im) * root) % p
        if v:
            out[m] = v
    return out


def parse_header(path: Path) -> tuple[int, list[dict], list[dict]]:
    text = path.read_text(encoding="utf-8")
    p = int(re.search(r"ring r=(\d+),", text).group(1))  # type: ignore[union-attr]
    names = re.search(r"ring r=\d+,\(([^)]*)\)", text).group(1).split(",")  # type: ignore[union-attr]

    def parse(body_text: str) -> dict:
        poly: dict = {}
        for sign, body in re.findall(r"([+-]?)([^+-]+)", body_text.replace(" ", "").replace("\n", "")):
            coef, exps = 1, [0] * NVARS
            for f in body.split("*"):
                if re.fullmatch(r"\d+", f):
                    coef *= int(f)
                else:
                    v, _, e = f.partition("^")
                    exps[int(names[names.index(v)][1:]) - 1] += int(e) if e else 1
            m = tuple(exps)
            poly[m] = (poly.get(m, 0) + (-coef if sign == "-" else coef)) % p
        return {m: c for m, c in poly.items() if c}

    J = [parse(g) for g in re.search(r"ideal J=([^;]*);", text).group(1).split(",")]  # type: ignore[union-attr]
    G = [parse(g) for g in re.search(r"ideal G=([^;]*);", text).group(1).split(",")]  # type: ignore[union-attr]
    return p, J, G


def proportional_mod(a: dict, b: dict, p: int) -> bool:
    if a.keys() != b.keys() or not a:
        return False
    m0 = next(iter(a))
    c = a[m0] * pow(b[m0], -1, p) % p
    return all(a[m] == c * b[m] % p for m in a)


def poly_text(poly: dict[tuple[int, ...], int]) -> str:
    terms = []
    for m, c in sorted(poly.items()):
        mono = "*".join(f"t{i + 1}^{e}" for i, e in enumerate(m) if e)
        terms.append(f"{c}*{mono}" if mono else str(c))
    return "+".join(terms) if terms else "0"


def ideal_equal_mod(mine: list[dict], header: list[dict], p: int) -> bool:
    """Mutual reduction of two ideals of F_p[t1..t9] in Singular, global ordering dp."""
    script = (
        f"ring r={p},(t1,t2,t3,t4,t5,t6,t7,t8,t9),dp;\n"
        f"ideal A={','.join(poly_text(f) for f in mine)};\n"
        f"ideal B={','.join(poly_text(f) for f in header)};\n"
        'ideal sA=std(A); ideal sB=std(B);\n"RESULT equal",size(reduce(A,sB))==0 && size(reduce(B,sA))==0;\nquit;\n'
    )
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp, "eq.sing")
        src.write_text(script, encoding="utf-8")
        res = subprocess.run(
            ["Singular", "-q", "--no-rc", src.name],
            cwd=tmp,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            check=False,
        )
    lines = [ln.split() for ln in res.stdout.splitlines() if ln.startswith("RESULT equal")]
    if res.returncode != 0 or len(lines) != 1 or any(ln.lstrip().startswith("?") for ln in res.stdout.splitlines()):
        raise RuntimeError(f"ideal comparison at {p}: Singular exit {res.returncode}")
    return lines[0][2] == "1"


def reduction(row: dict, p: int, root: int) -> dict:
    path = INPUTS / f"p{p}-r{root}" / f"{row['slug']}.sing"
    hp, hj, hg = parse_header(path)
    if hp != p:
        raise RuntimeError(f"{path.name}: prime {hp}, expected {p}")
    out: dict[str, Any] = {
        "header": f"p{p}-r{root}/{row['slug']}.sing",
        "header_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }
    for kind, header in (("J", hj), ("G", hg)):
        mine = [reduce_mod(f, p, root) for f in row[kind]]
        out[f"{kind}_counts"] = [len(mine), len(header)]
        out[f"{kind}_generatorwise_up_to_scalar"] = sum(
            proportional_mod(a, b, p) for a, b in zip(mine, header, strict=True)
        )
    out["J_ideal_equal"] = ideal_equal_mod([reduce_mod(f, p, root) for f in row["J"]], hj, p)
    out["G_equal_up_to_scalar"] = out["G_generatorwise_up_to_scalar"] == len(row["G"]) == len(hg)
    return out


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    rows = dict(zip(SLUGS, parallel.ordered_map(run, list(SLUGS), min_items=1), strict=True))
    plus, minus = rows["e8-np"], rows["e8-nm"]
    record: dict[str, Any] = {
        "check": "e8-np-nm-coordinate-map-qi",
        "field": "Q(i), minpoly I^2 + 1",
        "sigma": "t8 -> -t8, t9 -> -t9",
        "producer": "fiber_inputs.py phase one through rees._phase_one_script, rings rewritten to (0,I)",
        "inputs": {
            s: {
                "script_sha256": r["script_sha256"],
                "ring": r["ring"],
                "germ_dimension": r["germ_dimension"],
                "selected_one_based": r["selected"],
                "eliminated": r["eliminated"],
                "J_generators": len(r["J"]),
                "G_generators": len(r["G"]),
            }
            for s, r in rows.items()
        },
        "J_identity": identity(plus["J"], minus["J"], SIGMA),
        "G_identity": identity(plus["G"], minus["G"], SIGMA),
        "control_t9_only": {
            "J": identity(plus["J"], minus["J"], CONTROL)["bijection_by_units"],
            "G": identity(plus["G"], minus["G"], CONTROL)["bijection_by_units"],
        },
        "reductions": [reduction(r, p, root) for p, root in SPECIALIZATIONS for r in (plus, minus)],
    }
    p0, r0 = SPECIALIZATIONS[0]
    _, header_j, _ = parse_header(INPUTS / f"p{p0}-r{r0}" / "e8-nm.sing")
    widened = [reduce_mod(f, p0, r0) for f in minus["J"]] + [{(1,) + (0,) * (NVARS - 1): 1}]
    bent = [dict(g) for g in plus["G"]]
    first = next(iter(bent[0]))
    bent[0][first] = bent[0][first] * 2
    record["mutations"] = {
        "J_ideal_equal_after_adding_t1": ideal_equal_mod(widened, header_j, p0),
        "G_identity_after_doubling_one_coefficient": identity(bent, minus["G"], SIGMA)["bijection_by_units"],
    }
    record["sign_identity_over_qi"] = (
        not any(record["mutations"].values())
        and record["J_identity"]["bijection_by_units"]
        and record["G_identity"]["bijection_by_units"]
        and not record["control_t9_only"]["G"]
        and all(r["J_ideal_equal"] and r["G_equal_up_to_scalar"] for r in record["reductions"])
    )
    Path(sys.argv[1]).write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: record[k] for k in ("sign_identity_over_qi", "control_t9_only")}))
    return 0 if record["sign_identity_over_qi"] else 1


if __name__ == "__main__":
    sys.exit(main())
