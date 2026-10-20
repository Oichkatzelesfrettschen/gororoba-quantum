"""Box-kite facts recomputed through each Cayley-Dickson package's declared map onto cd_core.

A witness is one package at one dimension with the map the docs/notes/algebra_circuit_rules.md
package table declares: identity, a signed relabeling (python-octonion), the
opposite algebra or the e3/e5/e6 sign flip (SageMath), or the split relation
(same XOR index and associator signs, e4..e7 squaring to +1). Each witness
supplies an exact product of sparse integer elements; `facts_16` and `facts_8`
evaluate the same fact bundle for any product, and a fact is the sha256 of
its canonical JSON, so agreement is digest equality with cd_core and never a
vote among packages.

Two product modes reach a package:

- `element` imports the package and multiplies elements with its own
  arithmetic (exact Fractions in hypercomplex and hyprat, integer KD objects in
  cayley-dickson, float64 in Cayley-Calculator and python-octonion, whose
  coefficients must come back integral). Only `--write` on the build host uses it.
- `table` multiplies through the retained basis table of that package
  (docs/evidence/algebra_packages/tables.json, or the SageMath export) under
  the same declared map; `--check` uses it, so CI imports no package and the
  retained element verdicts must follow from the retained tables.

D = 16 facts: the 210 x 210 two-blade norm table, the kite structure derived
from it (assessors, struts, edge sign types), the Design B products of the
census rows, left and right annihilator nullities of every two-blade, the
twist counts and the associator classes of the kite index triples. D = 8
facts: two-blade zero products and nullities, all 512 associator signs, the
64 basis signs, and the strut lines (u, v, S) of every kite as octonion
triples. The split octonions share the index and associator facts and must
differ on the zero-product facts, which is the negative control.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import sys
from collections.abc import Callable, Sequence
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from cd_core import cd_sign  # noqa: E402

TABLES = ROOT / "docs/evidence/algebra_packages/tables.json"
SAGE_TABLE = ROOT / "docs/evidence/algebra_packages/sagemath_octonion_table.json"
SIGNS = (1, -1)
TORCH_TO_CD_PI = (0, 1, 2, 4, 3, 6, 7, 5)
TORCH_TO_CD_ETA = (0, 0, 0, 0, 0, 0, 1, 0)
SAGE_FLIP = (1, 1, 1, -1, 1, -1, -1, 1)
SPLIT_FACTS_SHARED = ("associator_signs", "strut_lines")
SPLIT_FACTS_DIFFERING = ("two_blade_zero_products", "two_blade_left_nullities")

Product = Callable[[dict[int, int], dict[int, int]], dict[int, int]]

# (witness, package, dimension, map, role, arithmetic, table key, traps); the
# table key names the retained basis table that --check multiplies through.
WITNESSES: tuple[tuple[str, str, int, str, str, str, str | None, str], ...] = (
    (
        "hypercomplex-16",
        "hypercomplex",
        16,
        "identity",
        "independent",
        "exact Fraction, cayley_dickson_algebra(4, Fraction)",
        "16",
        "a basis product costs about 4x more per doubling; inverse() exists for zero divisors",
    ),
    (
        "hyprat-16",
        "hyprat",
        16,
        "identity",
        "independent",
        "exact rationals, Hy.from_array at mu = -1",
        "16",
        "Hy.from_array(coeffs, signs=...) names the algebra, lowest level first",
    ),
    (
        "hypercomplex-engine-16",
        "hypercomplex-engine",
        16,
        "identity",
        "independent",
        "basis sign oracle multiply('standard', (1, p), (1, q)), bilinear",
        "16",
        "takes and returns (sign, index) tuples; dim changes which doubling is split",
    ),
    (
        "cayley-dickson-16",
        "cayley-dickson",
        16,
        "identity",
        "independent",
        "integer KD doubling objects",
        "16",
        "installs a top-level src package; its pandas table reads transposed (not used)",
    ),
    (
        "Cayley-Calculator-16",
        "Cayley-Calculator",
        16,
        "identity",
        "independent",
        "float64 Sedenion, integral coefficients required",
        "16",
        "coerces every coefficient to float64; from octonion import * loads python-octonion",
    ),
    (
        "Octonion-Sedenion-16",
        "Octonion-Sedenion",
        16,
        "identity",
        "independent",
        "Sedenion components, imported with its own octonion module bound",
        "16",
        "sedenion.py imports the top-level octonion, which python-octonion owns, and fails as installed",
    ),
    (
        "hypercomplex-16-wrapper",
        "hypercomplex-algebra",
        16,
        "identity",
        "wrapper",
        "multiply_expressions over hypercomplex-engine",
        None,
        "not an independent witness; multiply_many_expressions folds left",
    ),
    (
        "hypercomplex-8",
        "hypercomplex",
        8,
        "identity",
        "independent",
        "exact Fraction, cayley_dickson_algebra(3, Fraction)",
        "8",
        "a basis product costs about 4x more per doubling",
    ),
    (
        "hyprat-8",
        "hyprat",
        8,
        "identity",
        "independent",
        "exact rationals at mu = -1",
        "8",
        "signs name the algebra, lowest level first",
    ),
    (
        "hypercomplex-engine-8",
        "hypercomplex-engine",
        8,
        "identity",
        "independent",
        "basis sign oracle, bilinear",
        "8",
        "(sign, index) tuples",
    ),
    (
        "cayley-dickson-8",
        "cayley-dickson",
        8,
        "identity",
        "independent",
        "integer KD doubling objects",
        "8",
        "installs a top-level src package",
    ),
    (
        "pyoctonion-8",
        "pyoctonion",
        8,
        "identity",
        "independent",
        "Octonion over pyquaternion halves",
        "8",
        "cal_multiply prints every product, * is used; imports the undeclared pyquaternion",
    ),
    (
        "Octonion-Sedenion-8",
        "Octonion-Sedenion",
        8,
        "identity",
        "independent",
        "Octonion components",
        "8",
        "owns no octonion module name; its sedenion module collides with python-octonion",
    ),
    (
        "octonion-8",
        "octonion",
        8,
        "signed relabeling pi = (0, 1, 2, 4, 3, 6, 7, 5), flip on its e6",
        "independent",
        "torch float64 octonion_mul, integral coefficients required",
        "8",
        "index i is not cd_core e_i; float64 tensors against torch's float32 default; AGPL",
    ),
    (
        "sagemath-8-opposite",
        "sagemath",
        8,
        "opposite algebra in natural order: e_a e_b (cd) = e_b e_a (Sage)",
        "independent",
        "exact rationals, OctonionAlgebra(QQ)",
        "sage",
        "ported code reverses every product unless mapped",
    ),
    (
        "sagemath-8-flip",
        "sagemath",
        8,
        "sign flip on e3, e5, e6 is an isomorphism onto cd_core",
        "independent",
        "exact rationals, OctonionAlgebra(QQ)",
        "sage",
        "ported code reverses every product unless mapped",
    ),
    (
        "splitoct-8",
        "splitoct",
        8,
        "split: identity on indices, e4..e7 square to +1",
        "split control",
        "SymPy-backed SplitOctonion, integral coefficients",
        "8",
        "not the octonions; isotropic elements have no inverse; GPL",
    ),
    (
        "hyprat-split-8",
        "hyprat",
        8,
        "split: signs (-1, -1, +1)",
        "split control",
        "exact rationals, Hy.from_array(signs=(-1, -1, 1))",
        "split-8",
        "signs (-1, -1, +1) give the split octonions",
    ),
    (
        "hypercomplex-engine-split-8",
        "hypercomplex-engine",
        8,
        "split: build_table('split', 3)",
        "split control",
        "basis sign table, bilinear",
        "split-8",
        "dim changes which doubling is split",
    ),
)
SPECS = {w[0]: w for w in WITNESSES}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def integral(value: Any, label: str) -> int:
    """An exact integer from a Fraction, int, float64 or Sage rational; anything else is a failure."""
    if isinstance(value, Fraction):
        require(value.denominator == 1, f"{label}: non-integral {value}")
        return int(value)
    number = float(value)
    require(number == round(number) and abs(number) < 2**40, f"{label}: non-integral {value}")
    return round(number)


def from_dense(coefficients: Sequence[Any], label: str) -> dict[int, int]:
    out = {k: integral(c, label) for k, c in enumerate(coefficients)}
    return {k: v for k, v in out.items() if v}


def sparse_from_table(signs: list[list[int]], index: list[list[int]]) -> Product:
    def product(x: dict[int, int], y: dict[int, int]) -> dict[int, int]:
        out: dict[int, int] = {}
        for p, a in x.items():
            for q, b in y.items():
                r = index[p][q]
                out[r] = out.get(r, 0) + signs[p][q] * a * b
        return {k: v for k, v in sorted(out.items()) if v}

    return product


def cd_product(dim: int) -> Product:
    signs = [[cd_sign(dim, p, q) for q in range(dim)] for p in range(dim)]
    return sparse_from_table(signs, [[p ^ q for q in range(dim)] for p in range(dim)])


def relabeled(dim: int, package_product: Product, pi: Sequence[int], eta: Sequence[int]) -> Product:
    """cd_core product through f_p = (-1)^eta[p] e_{pi[p]}: map in, multiply in the package, map back."""
    inverse = {pi[p]: p for p in range(dim)}

    def product(x: dict[int, int], y: dict[int, int]) -> dict[int, int]:
        def into(v: dict[int, int]) -> dict[int, int]:
            return {inverse[a]: c * (-1) ** eta[inverse[a]] for a, c in v.items()}

        out = package_product(into(x), into(y))
        return {k: v for k, v in sorted({pi[p]: c * (-1) ** eta[p] for p, c in out.items()}.items()) if v}

    return product


def flipped(product_: Product, flip: Sequence[int]) -> Product:
    def product(x: dict[int, int], y: dict[int, int]) -> dict[int, int]:
        out = product_({k: v * flip[k] for k, v in x.items()}, {k: v * flip[k] for k, v in y.items()})
        return {k: v * flip[k] for k, v in out.items()}

    return product


def opposite(product_: Product) -> Product:
    def product(x: dict[int, int], y: dict[int, int]) -> dict[int, int]:
        return product_(y, x)

    return product


def table_product(witness: str) -> Product:
    """The witness's product through its retained basis table and declared map."""
    _, package, dim, _, role, _, key, _ = SPECS[witness]
    require(key is not None, f"{witness} has no retained table")
    if key == "sage":
        record = json.loads(SAGE_TABLE.read_text(encoding="utf-8"))
        rows = record["table"]
        signs = [[sum(rows[a][b]) for b in range(8)] for a in range(8)]
        index = [[next(k for k, c in enumerate(rows[a][b]) if c) for b in range(8)] for a in range(8)]
        sage = sparse_from_table(signs, index)
        return opposite(sage) if witness.endswith("opposite") else flipped(sage, SAGE_FLIP)
    entry = json.loads(TABLES.read_text(encoding="utf-8"))["packages"][package]
    table = entry["tables"][key]
    base = sparse_from_table(table["signs"], table["index"])
    if package == "octonion":
        return relabeled(dim, base, TORCH_TO_CD_PI, TORCH_TO_CD_ETA)
    return base


def element_product(witness: str) -> Product:
    """The witness's product through the package's own element arithmetic (build host only)."""
    _, package, dim, _, _, _, _, _ = SPECS[witness]
    n = dim.bit_length() - 1
    if package == "hypercomplex":
        import hypercomplex

        algebra = hypercomplex.cayley_dickson_algebra(n, Fraction)

        def hc(x: dict[int, int], y: dict[int, int]) -> dict[int, int]:
            a = algebra(*[Fraction(x.get(k, 0)) for k in range(dim)])
            b = algebra(*[Fraction(y.get(k, 0)) for k in range(dim)])
            return from_dense((a * b).coefficients(), witness)

        return hc
    if package == "hyprat":
        import hyprat

        signs = (-1, -1, 1) if "split" in witness else None

        def hy(x: dict[int, int], y: dict[int, int]) -> dict[int, int]:
            a = hyprat.Hy.from_array([Fraction(x.get(k, 0)) for k in range(dim)], signs=signs)
            b = hyprat.Hy.from_array([Fraction(y.get(k, 0)) for k in range(dim)], signs=signs)
            return from_dense((a * b).to_array(), witness)

        return hy
    if package == "hypercomplex-engine":
        import hypercomplex_engine

        if "split" in witness:
            signs, index = hypercomplex_engine.build_table("split", n)
            return sparse_from_table([[int(v) for v in r] for r in signs], [[int(v) for v in r] for r in index])
        table = [[hypercomplex_engine.multiply("standard", (1, p), (1, q)) for q in range(dim)] for p in range(dim)]
        return sparse_from_table(
            [[int(s) for s, _ in row] for row in table], [[int(i) for _, i in row] for row in table]
        )
    if package == "cayley-dickson":
        import cayley_dickson

        basis: list[Any] = [1]
        for _ in range(n):
            basis = list(cayley_dickson.expand_basis(basis))
        zero = basis[0].zero_out()

        def build(v: dict[int, int]) -> Any:
            out = zero
            for k, c in v.items():
                for _ in range(abs(c)):
                    out = out + basis[k] if c > 0 else out - basis[k]
            return out

        def kd(x: dict[int, int], y: dict[int, int]) -> dict[int, int]:
            return from_dense(list(build(x) * build(y)), witness)

        return kd
    if package == "Cayley-Calculator":
        import Cayley_Calculator  # noqa: F401  (adds its module directory to sys.path)
        import sedenion

        def cc(x: dict[int, int], y: dict[int, int]) -> dict[int, int]:
            a = sedenion.Sedenion(*[float(x.get(k, 0)) for k in range(dim)])
            b = sedenion.Sedenion(*[float(y.get(k, 0)) for k in range(dim)])
            return from_dense(list(a * b), witness)

        return cc
    if package == "Octonion-Sedenion":
        import importlib

        own = importlib.import_module("Octonion_Sedenion.octonion")
        if dim == 8:
            cls = own.Octonion
        else:
            saved = sys.modules.get("octonion")
            sys.modules["octonion"] = own
            try:
                cls = importlib.import_module("Octonion_Sedenion.sedenion").Sedenion
            finally:
                if saved is None:
                    sys.modules.pop("octonion", None)
                else:
                    sys.modules["octonion"] = saved

        def os_(x: dict[int, int], y: dict[int, int]) -> dict[int, int]:
            a = cls(*[x.get(k, 0) for k in range(dim)])
            b = cls(*[y.get(k, 0) for k in range(dim)])
            return from_dense((a * b).components, witness)

        return os_
    if package == "pyoctonion":
        import pyoctonion

        def po(x: dict[int, int], y: dict[int, int]) -> dict[int, int]:
            z = pyoctonion.Octonion(*[x.get(k, 0) for k in range(8)]) * pyoctonion.Octonion(
                *[y.get(k, 0) for k in range(8)]
            )
            return from_dense([z.x_0, z.x_1, z.x_2, z.x_3, z.x_4, z.x_5, z.x_6, z.x_7], witness)

        return po
    if package == "octonion":
        import octonion
        import torch

        def to(x: dict[int, int], y: dict[int, int]) -> dict[int, int]:
            a = torch.tensor([float(x.get(k, 0)) for k in range(8)], dtype=torch.float64)
            b = torch.tensor([float(y.get(k, 0)) for k in range(8)], dtype=torch.float64)
            return from_dense(octonion.octonion_mul(a, b).tolist(), witness)

        return relabeled(8, to, TORCH_TO_CD_PI, TORCH_TO_CD_ETA)
    if package == "sagemath":
        from sage.all import QQ, OctonionAlgebra

        algebra = OctonionAlgebra(QQ)
        units = list(algebra.basis())

        def sg(x: dict[int, int], y: dict[int, int]) -> dict[int, int]:
            a = sum((c * units[k] for k, c in x.items()), algebra.zero())
            b = sum((c * units[k] for k, c in y.items()), algebra.zero())
            return from_dense(list((a * b).vector()), witness)

        return opposite(sg) if witness.endswith("opposite") else flipped(sg, SAGE_FLIP)
    if package == "splitoct":
        import SplitOct

        def sp(x: dict[int, int], y: dict[int, int]) -> dict[int, int]:
            a = SplitOct.SplitOctonion([x.get(k, 0) for k in range(8)])
            b = SplitOct.SplitOctonion([y.get(k, 0) for k in range(8)])
            return from_dense(list((a * b).x), witness)

        return sp
    raise RuntimeError(f"{witness}: no element product")


_PRODUCTS: dict[tuple[str, str], Product] = {}


def dimension(witness: str) -> int:
    """The witness's algebra dimension; cd_core-16 and cd_core-8 are the references."""
    return {"cd_core-16": 16, "cd_core-8": 8}[witness] if witness.startswith("cd_core") else SPECS[witness][2]


def product_for(witness: str, mode: str) -> Product:
    key = (witness, mode)
    if key not in _PRODUCTS:
        if witness in ("cd_core-16", "cd_core-8"):
            _PRODUCTS[key] = cd_product(dimension(witness))
        elif mode == "element":
            _PRODUCTS[key] = element_product(witness)
        else:
            _PRODUCTS[key] = table_product(witness)
    return _PRODUCTS[key]


def blades(dim: int) -> list[tuple[int, int, int]]:
    return [(i, j, t) for i, j in itertools.combinations(range(1, dim), 2) for t in SIGNS]


def vec(blade: tuple[int, int, int]) -> dict[int, int]:
    return {blade[0]: 1, blade[1]: blade[2]}


def exact_rank(rows: list[list[int]]) -> int:
    a = [[Fraction(v) for v in row] for row in rows]
    rank = 0
    for col in range(len(a[0]) if a else 0):
        pivot = next((r for r in range(rank, len(a)) if a[r][col] != 0), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        for r in range(len(a)):
            if r != rank and a[r][col] != 0:
                factor = a[r][col] / a[rank][col]
                a[r] = [u - factor * v for u, v in zip(a[r], a[rank], strict=True)]
        rank += 1
    return rank


def nullities(product: Product, dim: int, blade: tuple[int, int, int]) -> list[int]:
    """[dim ker L_b, dim ker R_b] from the products of b with every basis unit."""
    x = vec(blade)
    left = [product(x, {q: 1}) for q in range(dim)]
    right = [product({q: 1}, x) for q in range(dim)]
    out = []
    for columns in (left, right):
        matrix = [[columns[q].get(r, 0) for q in range(dim)] for r in range(dim)]
        out.append(dim - exact_rank(matrix))
    return out


def omega_from(product: Product, i: int, j: int, k: int) -> int:
    left = product(product({i: 1}, {j: 1}), {k: 1})
    right = product({i: 1}, product({j: 1}, {k: 1}))
    require(len(left) == 1 and left.keys() == right.keys(), f"basis triple ({i},{j},{k}) leaves the basis")
    return 1 if left == right else -1


class Task:
    """One slice of a witness's fact bundle; a module-level callable the process pool can pickle."""

    def __init__(
        self,
        mode: str,
        rows: list[tuple[dict[int, int], dict[int, int]]],
        kite_triples: dict[int, list[tuple[str, int, int, int]]],
    ) -> None:
        self.mode = mode
        self.rows = rows
        self.kite_triples = kite_triples

    def __call__(self, item: tuple[str, str, int]) -> Any:
        witness, fact, arg = item
        try:
            product = product_for(witness, self.mode)
        except Exception as failure:  # noqa: BLE001  (an import failure is the retained verdict)
            return {"error": f"{type(failure).__name__}: {failure}"}
        dim = dimension(witness)
        if fact == "norms":
            row_blades = [b for b in blades(dim) if b[0] == arg]
            return [[sum(c * c for c in product(vec(a), vec(b)).values()) for b in blades(dim)] for a in row_blades]
        if fact == "design_b":
            return [sorted(product(x, y).items()) for x, y in self.rows]
        if fact == "nullities":
            return [nullities(product, dim, b) for b in blades(dim) if b[0] == arg]
        if fact == "twist":
            tests = mismatches = zeros = 0
            b = arg
            for big_b in range(9, 16):
                for d in range(1, 8):
                    for big_d in range(9, 16):
                        if b == d or big_b == big_d:
                            continue
                        for sb, s_big_b, sd, s_big_d in itertools.product(SIGNS, repeat=4):
                            lhs = not product({big_b: s_big_b, b: sb}, {big_d: s_big_d, d: sd})
                            rhs = not product({big_b: s_big_b, d: sd}, {big_d: s_big_d, b: -sb})
                            tests += 1
                            mismatches += lhs != rhs
                            zeros += lhs
            return [tests, mismatches, zeros]
        if fact == "associator":
            out = {}
            for strut, triples in sorted(self.kite_triples.items()):
                table: dict[str, list[int]] = {}
                for name, i, j, k in triples:
                    cell = table.setdefault(name, [0, 0])
                    cell[0] += omega_from(product, i, j, k) == -1
                    cell[1] += 1
                out[str(strut)] = dict(sorted(table.items()))
            return out
        if fact == "octonion":
            return facts_8(product)
        raise RuntimeError(f"unknown fact {fact}")


def facts_8(product: Product) -> dict[str, Any]:
    two = blades(8)
    zero_pairs = [[*a, *b] for a in two for b in two if not product(vec(a), vec(b))]
    left_nullities = [nullities(product, 8, b)[0] for b in two]
    assoc = [omega_from(product, i, j, k) for i in range(8) for j in range(8) for k in range(8)]
    basis_signs = []
    for p in range(8):
        for q in range(8):
            terms = product({p: 1}, {q: 1})
            require(list(terms) == [p ^ q], f"e{p} e{q} leaves index {p ^ q}")
            basis_signs.append(terms[p ^ q])
    lines = []
    for strut in range(1, 8):
        for u, v in itertools.combinations([k for k in range(1, 8) if k != strut], 2):
            if u ^ v == strut:
                lines.append([strut, u, v, list(product({u: 1}, {v: 1})) == [strut], omega_from(product, u, v, strut)])
    return {
        "two_blade_zero_products": zero_pairs,
        "two_blade_left_nullities": left_nullities,
        "associator_signs": assoc,
        "basis_signs": basis_signs,
        "strut_lines": lines,
    }


def tasks_for(witness: str) -> list[tuple[str, str, int]]:
    if dimension(witness) == 8:
        return [(witness, "octonion", 0)]
    if SPECS.get(witness, ("", "", 0, "", ""))[4] == "wrapper":
        return []
    items = [(witness, "norms", i) for i in range(1, 15)]
    items += [(witness, "design_b", 0)]
    items += [(witness, "nullities", i) for i in range(1, 15)]
    items += [(witness, "twist", b) for b in range(1, 8)]
    items += [(witness, "associator", 0)]
    return items


def assemble(witness: str, results: list[Any]) -> dict[str, Any]:
    """Fact digests of one witness from its task results, in tasks_for order."""
    errors = [r["error"] for r in results if isinstance(r, dict) and "error" in r]
    if errors:
        return {"error": errors[0]}
    if dimension(witness) == 8:
        facts = results[0]
        return {"facts": {name: digest(value) for name, value in sorted(facts.items())}, "values": facts}
    norms = [row for chunk in results[0:14] for row in chunk]
    design_b = results[14]
    nulls = [row for chunk in results[15:29] for row in chunk]
    twist = [sum(r[k] for r in results[29:36]) for k in range(3)]
    associator = results[36]
    two = blades(16)
    position = {b: n for n, b in enumerate(two)}
    structure = []
    planes = sorted({(a[0], a[1]) for a in two for b in two if norms[position[a]][position[b]] == 0})
    for x in range(9, 16):
        members = [p for p in planes if p[0] ^ p[1] == x]
        pairs = []
        for p, q in itertools.combinations(members, 2):
            zs = sorted([s, t] for s in SIGNS for t in SIGNS if norms[position[(*p, s)]][position[(*q, t)]] == 0)
            pairs.append([list(p), list(q), zs])
        structure.append([x ^ 8, [list(p) for p in members], pairs])
    facts = {
        "two_blade_norms": norms,
        "kite_structure": structure,
        "design_b_products": design_b,
        "annihilator_nullities": nulls,
        "twist_counts": twist,
        "associator_classes": associator,
    }
    return {"facts": {name: digest(value) for name, value in sorted(facts.items())}, "values": facts}
