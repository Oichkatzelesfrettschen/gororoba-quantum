"""The sign isomorphism of same-sign X on both slices, and the scalars by which it moves the module maps.

"witnesses.jsonl" of a5-exceptional-fibers retains a sign isomorphism from the header presentation of X- -> N- to the
one of X+ -> N+: negating t9 carries each J and G generator of one header to plus or minus the generator of the same
index of the other, so y_j -> c_j y_j (c the G signs) carries the header-slice quadric ideal K_h(X-) onto K_h(X+).
The slice maps G- and G+ of A5-644 carry the weight-slice ideals K_w(X-), K_w(X+) over Q(i) onto those header ideals.
This program forms the substitution of the 15 weight-slice generators

    S_w = G+^{-1} o S_h o G-        (matrix M- D M+^{-1} on coefficient rows, D = diag(c))

over Q(i), which carries K_w(X-) onto K_w(X+) wherever A5-644 holds, and measures two scalars at 32009, 32029 and
32057. The module map theta of A5-638 (header slice) and A5-640 (weight slice) is the one solution, up to a scalar,
of a linear system that an ideal isomorphism carries to the system of its target, so on each slice

    S(theta-(x)) = lambda * theta+(S(x) modulo the linear forms of K+ : R+)    for the three coordinates x of B-

holds with one scalar: lambda_h for S_h and the retained header-slice maps (free coordinate set to 1), lambda_w for
S_w and the retained weight-slice maps (first image monic). With G-(theta_w-(x)) = c- theta_h-(G-(x)) and the same
for X+ (A5-645), the square G+ S_w = S_h G- gives

    c+ / c- = lambda_h / lambda_w.

The identity is forced and tests nothing by itself. The measured content is the three quantities: lambda_h, lambda_w
and the shape of S_w. Prediction written before the first run, from the retained maps and the retained sign vector:
lambda_h = -1 at every prime (S_h sends y4 -> 2 y6, y10 -> -10501 y5, y15 -> y1 at 32009 to y4 -> 2 y6,
y10 -> 10501 y5, y15 -> -y1, the negative of the retained X+ map); lambda_w = 1, since c+ / c- = -1 (A5-645); and S_w
a diagonal matrix of signs. All three held: S_w is the diagonal of W_SIGNS below, lambda_h = -1 and lambda_w = 1 at the
three primes. The opposite signs of the scalar of A5-645 therefore sit on the header slice: the retained header-slice
maps of X- and X+ differ by a sign under the retained isomorphism, and the retained weight-slice maps do not.
The two scalars can be read off the retained maps and the sign vector without a run, as the prediction was; the run
adds the matrix of S_w, the sign vectors at 32057, the transport of the ideals over Q(i) and the controls. Since S_w
is a real involution and conjugation carries K_w(X-) onto K_w(X+) as well, S_w followed by conjugation is a semilinear
involution that maps K_w(X-) to itself (a deduction from the two measured facts).

The run also reads: the J and G sign vectors of the three header pairs (32057 is not in witnesses.jsonl); the
remainders of S_w(K_w(X-)) against K_w(X+) over Q(i), both ways; the same for the complex conjugate of K_w(X-), which
is a second, semilinear, candidate for the weight-slice counterpart; the square G+ S_w = S_h G- over Q(i) and at each
prime; and, for S_h and for S_w at each prime, which of the 15 substitutions with one more generator negated still
carry ideal to ideal (none does). Controls of each scalar are those of slice_module_map_comparison.py (images
exchanged, map perturbed, generators exchanged), each of which must find no scalar.

Usage, from the repository root: "$PYTHON" docs/evidence/a5-kernel-attachments/x_sign_transport.py --out OUT.json
[--check RETAINED.json]. Ten items of a few seconds each go through parallel.ordered_map.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import warnings
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import slice_module_map_comparison as cmp  # noqa: E402

sys.path.insert(0, str(cmp.FIBERS / "replay" / "engine"))

import fiber_rank_v8 as eng  # noqa: E402
import quadric_and_germ_probes as probes  # noqa: E402
import weight_slice_fiber_relations as ws  # noqa: E402
import weight_slice_module_map as weight_map  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "gororoba.a5.x-sign-transport/1"
N = 15
G = 3
RADICAL = "minAssChar(sK)[1]"
SIDES = [3, 1, 3, 12, 0]
FLIP = ("t9",)
# The G signs of the X- -> X+ rows of witnesses.jsonl (32009 and 32029); header_signs() recomputes them at each prime.
G_SIGNS = (1, 1, 1, 1, 1, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1)
J_SIGNS = (1, -1, -1, -1, -1, -1, -1, -1, 1, 1, 1, 1)
# The diagonal of S_w = G+^{-1} S_h G- that the run finds: the signs of the 15 weight-slice generators.
W_SIGNS = (-1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, -1, -1, -1)
HEADER_INPUTS = {
    32009: "working/build/inputs/p32009-r10754",
    32029: "working/build/inputs/p32029-r9115",
    32057: "third-prime/inputs/p32057-r8059",
}
PRIMES = ((32009, 10754), (32029, 9115), (32057, 8059))
# The scalars of the finding: lambda_h on the header slice, lambda_w on the weight slice.
SCALARS = {"header": -1, "weight": 1}
NORMALIZED = {
    "header": ("imap(r0,AqW),1);", "imap(r0,AqW),0);"),
    "weight": ("imap(r0,AqH),0);", "imap(r0,AqH),1);"),
}
Gaussian = tuple[Fraction, Fraction]
TERM = re.compile(r"([+-]?)(\d+(?:/\d+)?)?(\*?i)?")


def gaussian(text: str) -> Gaussian:
    """A Gaussian rational from the text Singular prints over Q(i): 3, -i, (2*i), (1/2-3*i)."""
    body = text.strip().removeprefix("(").removesuffix(")").replace(" ", "")
    real, imaginary, position = Fraction(0), Fraction(0), 0
    while position < len(body):
        found = TERM.match(body, position)
        if found is None or found.end() == position or not (found.group(2) or found.group(3)):
            raise ValueError(f"not a Gaussian rational: {text!r}")
        value = Fraction(found.group(2) or "1") * (-1 if found.group(1) == "-" else 1)
        if found.group(3):
            imaginary += value
        else:
            real += value
        position = found.end()
    if not body:
        raise ValueError("empty Gaussian rational")
    return real, imaginary


def times(a: Gaussian, b: Gaussian) -> Gaussian:
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def reciprocal(a: Gaussian) -> Gaussian:
    norm = a[0] * a[0] + a[1] * a[1]
    if norm == 0:
        raise ZeroDivisionError("zero Gaussian rational")
    return a[0] / norm, -a[1] / norm


def product(a: list[list[Gaussian]], b: list[list[Gaussian]]) -> list[list[Gaussian]]:
    out = []
    for row in a:
        line = []
        for column in range(len(b[0])):
            real, imaginary = Fraction(0), Fraction(0)
            for k, entry in enumerate(row):
                term = times(entry, b[k][column])
                real, imaginary = real + term[0], imaginary + term[1]
            line.append((real, imaginary))
        out.append(line)
    return out


def inverse(matrix: list[list[Gaussian]]) -> list[list[Gaussian]]:
    """Gauss-Jordan over Q(i); a singular matrix raises."""
    n = len(matrix)
    zero, one = (Fraction(0), Fraction(0)), (Fraction(1), Fraction(0))
    work = [list(row) + [one if i == j else zero for j in range(n)] for i, row in enumerate(matrix)]
    for column in range(n):
        pivot = next((r for r in range(column, n) if work[r][column] != zero), None)
        if pivot is None:
            raise ZeroDivisionError("singular matrix")
        work[column], work[pivot] = work[pivot], work[column]
        scale = reciprocal(work[column][column])
        work[column] = [times(scale, x) for x in work[column]]
        for r in range(n):
            factor = work[r][column]
            if r != column and factor != zero:
                scaled = [times(factor, y) for y in work[column]]
                work[r] = [(x[0] - t[0], x[1] - t[1]) for x, t in zip(work[r], scaled, strict=True)]
    return [row[n:] for row in work]


def conjugate(a: Gaussian) -> Gaussian:
    return a[0], -a[1]


def text_of(a: Gaussian, prime: int, root: int) -> str:
    """The Singular text of a Gaussian rational: over Q(i) for prime 0, else with i sent to the root modulo prime."""
    if prime == 0:
        return f"({a[0]}+({a[1]})*i)"
    value = a[0] + a[1] * root
    return str(value.numerator * pow(value.denominator, -1, prime) % prime)


def shown(a: Gaussian) -> str:
    """A compact text for the record: 0, 1, -1, i, -i, or a+b*i."""
    names = {(1, 0): "1", (-1, 0): "-1", (0, 1): "i", (0, -1): "-i", (0, 0): "0"}
    return names.get((a[0], a[1]), f"{a[0]}+{a[1]}*i")  # type: ignore[arg-type]


def slice_map(minus: list[list[Gaussian]], signs: tuple[int, ...], plus: list[list[Gaussian]]) -> list[list[Gaussian]]:
    """M- D M+^{-1}: row k holds the image of the weight-slice generator y_k of X- in the generators of X+."""
    scaled = [[(s * x[0], s * x[1]) for x, s in zip(row, signs, strict=True)] for row in minus]
    return product(scaled, inverse(plus))


def induced(tag: str) -> dict[str, Any]:
    record = json.loads((cmp.X_INDUCED / f"induced-{tag}.json").read_text(encoding="utf-8"))
    if record.get("pass") is not True or record["relations_sha256"] != record["relations_sha256_retained"]:
        raise RuntimeError(f"induced-{tag}.json is not a passing record bound to the weight-slice digest")
    return record


def matrix_of(record: dict[str, Any]) -> list[list[Gaussian]]:
    return [[gaussian(entry) for entry in row] for row in record["map"]]


def relations(record: dict[str, Any], prime: int, root: int, conj: bool = False) -> str:
    quadrics = []
    for line in record["relations"]:
        terms = []
        for key, coefficient in ws.parse_relation(line):
            value = gaussian(coefficient)
            terms.append(f"{text_of(conjugate(value) if conj else value, prime, root)}*y({key[0]})*y({key[1]})")
        quadrics.append("+".join(terms))
    return ",\n".join(quadrics)


def images(matrix: list[list[Gaussian]], prime: int, root: int) -> str:
    return ",\n".join("+".join(f"{text_of(x, prime, root)}*y({c + 1})" for c, x in enumerate(row)) for row in matrix)


def header_ideal(relative: str) -> str:
    text = (cmp.FIBERS / relative).read_text(encoding="utf-8").strip()
    if text.startswith("ideal"):
        text = text.split("=", 1)[1].rstrip().rstrip(";")
    return text.rstrip(",")


def header_file(tag: str, prime: int) -> str:
    found = [row[4] for row in cmp.X_CELLS if row[1] == tag and row[2] == prime]
    if len(found) != 1:
        raise RuntimeError(f"no single header relation file for {tag} at {prime}")
    return found[0]


def header_signs(prime: int) -> dict[str, Any]:
    """The signs by which negating t9 carries the J and G generators of the X+ header to those of the X- header."""
    directory = cmp.FIBERS / HEADER_INPUTS[prime]
    with warnings.catch_warnings():
        # parse_header of the retained engine leaves its file to the collector, which warns under -W error.
        warnings.simplefilter("ignore", ResourceWarning)
        _, names, j_to, g_to = eng.parse_header(str(directory / "xp-np.sing"))
        _, names_from, j_from, g_from = eng.parse_header(str(directory / "xm-nm.sing"))
    index = [names.index(v) for v in FLIP]

    def signs(left: list[str], right: list[str]) -> list[int]:
        if names != names_from or len(left) != len(right):
            return [0]
        out = []
        for a, b in zip(left, right, strict=True):
            poly, target = eng.parse_poly(a, names, prime), eng.parse_poly(b, names, prime)
            moved = {m: (-c) % prime if sum(m[i] for i in index) % 2 else c for m, c in poly.items()}
            negative = {m: (-c) % prime for m, c in target.items()}
            out.append(1 if moved == target else -1 if moved == negative else 0)
        return out

    return {"item": "signs", "prime": prime, "J_signs": signs(j_to, j_from), "G_signs": signs(g_to, g_from)}


FLIPS = """ideal zH=std(KH); ideal zm=maxideal(1); ideal zi=f(zm); int zq; string zs="";
for(zq=1;zq<=@N@;zq++){ ideal zj=zi; zj[zq]=-zj[zq]; map zf=basering,zj; ideal zk=zf(KW);
  zs=zs+" "+string(size(reduce(zk,zH))==0 and size(reduce(KH,std(zk)))==0); kill zj; kill zf; kill zk; }
print("RESULT one_more_sign"+zs);
"""
SQUARE = """map zp=basering,@GP@;
map zg=basering,@GM@;
map zd=basering,@D@;
ideal za=f(zm); ideal zb=zp(za); ideal zc=zg(zm); ideal ze=zd(zc);
"RESULT square",size(ideal(matrix(zb)-matrix(ze)));
"""


def diagonal(signs: tuple[int, ...]) -> str:
    return ",".join(f"{s}*y({k + 1})" for k, s in enumerate(signs))


def square(prime: int, root: int) -> str:
    plus, minus = matrix_of(induced("xp")), matrix_of(induced("xm"))
    return (
        SQUARE.replace("@GP@", images(plus, prime, root))
        .replace("@GM@", images(minus, prime, root))
        .replace("@D@", diagonal(G_SIGNS))
    )


def script(kind: str, prime: int, root: int) -> str:
    """The Singular text of one item: the Q(i) item, or one slice at one prime with the solver of the comparison."""
    minus, plus = induced("xm"), induced("xp")
    sw = slice_map(matrix_of(minus), G_SIGNS, matrix_of(plus))
    flips = FLIPS.replace("@N@", str(N))
    if kind == "qi":
        return "\n".join(
            [
                f"ring r=(0,i),(y(1..{N})),dp; minpoly=i^2+1; option(redSB);",
                "ideal KW=" + relations(minus, 0, 0) + ";",
                "ideal KH=" + relations(plus, 0, 0) + ";",
                "ideal KC=" + relations(minus, 0, 0, conj=True) + ";",
                "map f=r," + images(sw, 0, 0) + ";",
                "ideal fK=f(KW); ideal sH=std(KH);",
                '"RESULT transported",size(reduce(fK,sH)),size(reduce(KH,std(fK)));',
                '"RESULT identity",size(reduce(KW,sH)),size(reduce(KH,std(KW)));',
                '"RESULT conjugate",size(reduce(KC,sH)),size(reduce(KH,std(KC)));',
                flips + square(0, 0) + '"RESULT done 1";',
                "quit;",
                "",
            ]
        )
    if kind == "header":
        source, target = header_ideal(header_file("xm", prime)), header_ideal(header_file("xp", prime))
        mapping = diagonal(G_SIGNS)
        extra = flips
    else:
        source, target = relations(minus, prime, root), relations(plus, prime, root)
        mapping = images(sw, prime, root)
        extra = flips + square(prime, root)
    old, new = NORMALIZED[kind]
    if cmp.TAIL.count(old) != 1:
        raise RuntimeError("the solver text of slice_module_map_comparison.py changed its normalization line")
    tail = cmp.TAIL.replace(old, new).replace("@P@", str(prime)).replace("@N@", str(N)).replace("@GG@", str(G * G))
    tail = tail.replace("@G@", str(G)).replace("@R@", RADICAL)
    head = (
        f'LIB "primdec.lib"; LIB "matrix.lib";\nring r0={prime},(y(1..{N})),dp; option(redSB);\n'
        f"ideal KW={source};\nideal KH={target};\nmap f=r0,{mapping};\n"
    )
    return head + extra + tail


def singular(text: str) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        source = Path(tmp, "transport.sing")
        source.write_text(text, encoding="utf-8")
        command = ["prlimit", f"--as={ws.SINGULAR_ADDRESS_SPACE_BYTES}", "Singular", "-q", "--no-rc", str(source)]
        run = subprocess.run(
            command, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=cmp.TIMEOUT_SECONDS, check=True
        )
    return run.stdout


def item(task: tuple[str, int, int]) -> dict[str, Any]:
    kind, prime, root = task
    if kind == "signs":
        return header_signs(prime)
    row = cmp.parse(singular(script(kind, prime, root)))
    if kind == "qi":
        row = {k: v for k, v in row.items() if v != []}
        return {"item": "qi"} | row
    renamed = {k.replace("weight_", "from_").replace("header_", "to_"): v for k, v in row.items()}
    return {"item": kind, "prime": prime, "root": root} | renamed


def tasks() -> list[tuple[str, int, int]]:
    out = [("signs", p, r) for p, r in PRIMES] + [("qi", 0, 0)]
    return out + [(kind, p, r) for kind in ("header", "weight") for p, r in PRIMES]


def expected_images(kind: str, tag: str, prime: int, root: int) -> list[list[str]]:
    ring, orbit = cmp.TAGS[tag][0], "N-" if tag == "xm" else "N+"
    if kind == "weight":
        return weight_map.images(tag, orbit, prime, root)
    retained = [row for row in probes.MAPS if row[0] == ring and row[1] == prime]
    if len(retained) != 1:
        raise RuntimeError(f"no single module-map row of the header slice for {ring} at {prime}")
    return probes.expected_map(retained[0])["images"]


def diagonal_text(signs: tuple[int, ...]) -> list[list[str]]:
    """The record text of a diagonal matrix of signs."""
    return [[str(s) if j == k else "0" for j in range(len(signs))] for k, s in enumerate(signs)]


def problems(rows: list[dict[str, Any]], matrix: list[list[str]]) -> list[str]:
    """The departures of the rows and of the matrix of S_w from the finding; an empty list for the retained record."""
    want = tasks()
    if [(r.get("item"), r.get("prime", 0), r.get("root", 0)) for r in rows] != [
        (k, p, r if k not in ("signs", "qi") else 0) for k, p, r in want
    ]:
        return ["the rows are not the ten items in order"]
    found = []
    if matrix != diagonal_text(W_SIGNS):
        found.append("the weight-slice substitution is not the diagonal of signs of the finding")
    for row in rows:
        kind, prime = row["item"], row.get("prime", 0)
        name = f"{kind} at {prime}" if prime else kind
        if kind == "signs":
            if row != {"item": "signs", "prime": prime, "G_signs": list(G_SIGNS), "J_signs": list(J_SIGNS)}:
                found.append(f"{name}: the header sign vectors differ from the retained isomorphism")
            continue
        flips = row.get("one_more_sign")
        if flips != [0] * N:
            found.append(f"{name}: a substitution with one more generator negated carries ideal to ideal")
        if row.get("transported") != [0, 0]:
            found.append(f"{name}: the substitution does not carry the X- ideal onto the X+ ideal")
        if kind != "header" and row.get("square") != [0]:
            found.append(f"{name}: G+ S_w differs from S_h G-")
        if kind == "qi":
            identity = row.get("identity")
            if not (isinstance(identity, list) and len(identity) == 2 and max(identity) > 0):
                found.append("qi: the X- and X+ weight-slice ideals are equal, so the substitution tests nothing")
            if row.get("conjugate") != [0, 0]:
                found.append("qi: the conjugate of the X- ideal is not the X+ ideal")
            if set(row) != {"item", "transported", "identity", "conjugate", "one_more_sign", "square"}:
                found.append("qi: the row holds an unexpected or missing field")
            continue
        root = row["root"]
        fixed = {
            "from_image": expected_images(kind, "xm", prime, root),
            "to_image": expected_images(kind, "xp", prime, root),
            "from_side": SIDES,
            "to_side": SIDES,
            "linear_parts": [0, 0],
            "from_solutions": [1],
            "from_det_nonzero": [1],
            "from_control_solutions": [0],
            "to_solutions": [1],
            "to_det_nonzero": [1],
            "to_control_solutions": [0],
        }
        if {k: row.get(k) for k in fixed} != fixed:
            found.append(f"{name}: a side, a solution count or a retained map differs from the finding")
        value = row.get("scalar")
        if not (isinstance(value, list) and len(value) == 3 and value[:2] == [1, 1]) or (
            (value[2] - SCALARS[kind]) % prime != 0
        ):
            found.append(f"{name}: the transported X- map is not {SCALARS[kind]} times the X+ map")
        for control in cmp.CONTROLS:
            seen = row.get(control)
            if not (isinstance(seen, list) and len(seen) == 3 and seen[1:] == [0, 0]):
                found.append(f"{name}: {control} found a scalar")
        indices = row.get("control_indices")
        if not (isinstance(indices, list) and len(indices) == 3 and min(indices) >= 1 and indices[1] != indices[2]):
            found.append(f"{name}: a control names no generator")
        extra = {"item", "prime", "root", "transported", "one_more_sign", "scalar", "control_indices", *cmp.CONTROLS}
        if set(row) != {*fixed, *extra, *(["square"] if kind == "weight" else [])}:
            found.append(f"{name}: the row holds an unexpected or missing field")
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--out", type=Path, required=True, help="write the JSON record")
    parser.add_argument("--check", type=Path, help="compare the computed record with this retained one")
    args = parser.parse_args()
    banner, version = ws.singular_version()
    sw = slice_map(matrix_of(induced("xm")), G_SIGNS, matrix_of(induced("xp")))
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "tools": {"singular": banner, "singular_version": version},
        "slice_map": [[shown(x) for x in row] for row in sw],
        "rows": list(parallel.ordered_map(item, tasks(), min_items=1)),
    }
    record["problems"] = problems(record["rows"], record["slice_map"])
    args.out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    for row in record["rows"]:
        print(row["item"], row.get("prime", ""), {k: row[k] for k in ("G_signs", "transported", "scalar") if k in row})
    for line in record["problems"]:
        print("PROBLEM", line, file=sys.stderr)
    if args.check is not None:
        kept = json.loads(args.check.read_text(encoding="utf-8"))
        if {k: v for k, v in kept.items() if k != "tools"} != {k: v for k, v in record.items() if k != "tools"}:
            print("PROBLEM the computed record differs from the retained one", file=sys.stderr)
            return 1
    return 0 if record["problems"] == [] else 1


if __name__ == "__main__":
    raise SystemExit(main())
