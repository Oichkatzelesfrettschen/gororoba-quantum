"""Overlap and isolation of the installed algebra packages, checked against cd_core.

Two modes, following scripts/algebra_package_tables.py:

- --extract (local only) imports every installed package, reads native basis
  multiplication tables (Cayley-Dickson levels D = 2 to 32, split levels,
  dual numbers, the three quaternion packages, Cl(p, q, r) for p + q + r <= 3
  from clifford, kingdon and galgebra, and SageMath quaternion and octonion
  algebras through one short `sage -c` call), records the dependency probes
  (which package multiplies through which), and writes interplay_tables.json
  beside this file.
- --check (CI) imports cd_core alone. It rebuilds the references from
  cd_core.cd_sign (the ordinary algebras), from the split doubling
  (a, b)(c, d) = (ac + conj(d) b, da + b conj(c)) on a cd_core parent, and
  the dual numbers, then verifies every declared relation in RELATIONS:
  identical tables, signed relabelings with their exact count, opposite
  algebras, subalgebras on named basis elements, and non-isomorphism by a
  named invariant (associativity, basis-square signature, commutativity).

A signed relabeling is T(e_p) = (-1)^eta(p) e_pi(p) with T(e_p e_q) =
T(e_p) T(e_q) on every basis pair. Its count is the number of such maps;
cd_core onto itself admits 24 at D = 4 and 1344 at D = 8 (the signed
permutation automorphisms), which the check requires first as a calibration
of the search.
"""

from __future__ import annotations

import argparse
import importlib
import itertools
import json
import subprocess
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from cd_core import cd_sign  # noqa: E402

EVIDENCE = HERE / "interplay_tables.json"
SCHEMA = "algebra-interplay-v1"

Table = dict[str, Any]
Coefficients = Callable[[int, int], Sequence[Any]]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


# --------------------------------------------------------------------------
# Reference algebras from cd_core
# --------------------------------------------------------------------------


def cd_table(dim: int) -> Table:
    return {
        "signs": [[cd_sign(dim, p, q) for q in range(dim)] for p in range(dim)],
        "index": [[p ^ q for q in range(dim)] for p in range(dim)],
    }


def split_table(dim: int) -> Table:
    """One split doubling on top of the cd_core parent of dimension dim / 2.

    The split doubling changes the sign of (0, b)(0, d) = (+conj(d) b, 0), so
    the sign flips exactly where both indices lie in the upper half.
    """
    half = dim // 2
    signs = [[cd_sign(dim, p, q) * (-1 if p >= half and q >= half else 1) for q in range(dim)] for p in range(dim)]
    return {"signs": signs, "index": [[p ^ q for q in range(dim)] for p in range(dim)]}


def dual_table() -> Table:
    """The dual numbers R[eps], eps^2 = 0, on (1, eps)."""
    return {"signs": [[1, 1], [1, 0]], "index": [[0, 1], [1, 0]]}


REFERENCES: dict[str, Callable[[], Table]] = {
    "C": lambda: cd_table(2),
    "H": lambda: cd_table(4),
    "O": lambda: cd_table(8),
    "S": lambda: cd_table(16),
    "CD32": lambda: cd_table(32),
    "split-C": lambda: split_table(2),
    "split-H": lambda: split_table(4),
    "split-O": lambda: split_table(8),
    "split-S": lambda: split_table(16),
    "dual": dual_table,
}


# --------------------------------------------------------------------------
# Table algebra: products, invariants, relabelings
# --------------------------------------------------------------------------


def size(table: Table) -> int:
    return len(table["signs"])


def mul(table: Table, p: int, q: int) -> tuple[int, int]:
    """(sign, index) of e_p e_q; sign 0 is the zero product."""
    sign = table["signs"][p][q]
    return sign, table["index"][p][q] if sign else 0


def transpose(table: Table) -> Table:
    """The opposite algebra: x *op y = y x."""
    dim = size(table)
    return {
        "signs": [[table["signs"][q][p] for q in range(dim)] for p in range(dim)],
        "index": [[table["index"][q][p] for q in range(dim)] for p in range(dim)],
    }


def restrict(table: Table, elements: Sequence[int]) -> Table:
    """The subalgebra on the listed basis elements, reindexed in list order; it must close."""
    position = {element: k for k, element in enumerate(elements)}
    signs, index = [], []
    for p in elements:
        srow, irow = [], []
        for q in elements:
            sign, r = mul(table, p, q)
            require(sign == 0 or r in position, f"basis set {list(elements)} is not closed: e{p} e{q} = e{r}")
            srow.append(sign)
            irow.append(position[r] if sign else 0)
        signs.append(srow)
        index.append(irow)
    return {"signs": signs, "index": index}


def same(a: Table, b: Table) -> bool:
    dim = size(a)
    return size(b) == dim and all(mul(a, p, q) == mul(b, p, q) for p in range(dim) for q in range(dim))


def nonassociative_triples(table: Table) -> int:
    """Basis triples with (e_p e_q) e_r != e_p (e_q e_r)."""
    dim = size(table)
    count = 0
    for p, q, r in itertools.product(range(dim), repeat=3):
        s1, i1 = mul(table, p, q)
        left = (0, 0) if s1 == 0 else mul(table, i1, r)
        s2, i2 = mul(table, q, r)
        right = (0, 0) if s2 == 0 else mul(table, p, i2)
        left = (s1 * left[0], left[1] if s1 * left[0] else 0)
        right = (s2 * right[0], right[1] if s2 * right[0] else 0)
        count += left != right
    return count


def associator(table: Table, p: int, q: int, r: int) -> list[int]:
    """(e_p e_q) e_r - e_p (e_q e_r) as an integer coefficient vector."""
    out = [0] * size(table)
    s1, i1 = mul(table, p, q)
    if s1:
        s, i = mul(table, i1, r)
        out[i] += s1 * s
    s2, i2 = mul(table, q, r)
    if s2:
        s, i = mul(table, p, i2)
        out[i] -= s2 * s
    return out


def alternativity_failures(table: Table) -> int:
    """Basis triples violating the linearized alternative laws (x, y, z) + (y, x, z) = 0 = (x, y, z) + (x, z, y).

    The associator is trilinear, so these basis identities hold exactly when (x, x, y) = (x, y, y) = 0 for
    all x and y: alternativity is decided by the table.
    """
    dim = size(table)
    failures = 0
    for p, q, r in itertools.product(range(dim), repeat=3):
        base = associator(table, p, q, r)
        left = associator(table, q, p, r)
        right = associator(table, p, r, q)
        failures += any(a + b for a, b in zip(base, left, strict=True)) or any(
            a + b for a, b in zip(base, right, strict=True)
        )
    return failures


def quadratic(table: Table) -> bool:
    """Every imaginary unit squares to a nonzero scalar and distinct imaginary units anticommute.

    Such a table has the diagonal norm n(x) = sum_p n(e_p) x_p^2 with n(e_0) = 1 and n(e_p) = -e_p^2,
    and every element satisfies x^2 - t(x) x + n(x) = 0.
    """
    dim = size(table)
    for p in range(1, dim):
        if mul(table, p, p) not in ((1, 0), (-1, 0)):
            return False
        for q in range(p + 1, dim):
            (s1, i1), (s2, i2) = mul(table, p, q), mul(table, q, p)
            if s1 == 0 or i1 != i2 or s1 != -s2:
                return False
    return True


def invariants(table: Table) -> dict[str, Any]:
    dim = size(table)
    squares = [mul(table, p, p) for p in range(1, dim)]
    minus = sum(s == (-1, 0) for s in squares)
    plus = sum(s == (1, 0) for s in squares)
    return {
        "dim": dim,
        "unit_e0": all(mul(table, 0, q) == (1, q) and mul(table, q, 0) == (1, q) for q in range(dim)),
        "squares_minus_one": minus,
        "squares_plus_one": plus,
        "squares_zero": sum(s[0] == 0 for s in squares),
        "quadratic": quadratic(table),
        "norm_signature": (1 + minus, plus) if quadratic(table) else None,
        "commutative": all(mul(table, p, q) == mul(table, q, p) for p in range(dim) for q in range(dim)),
        "nonassociative_triples": nonassociative_triples(table),
        "alternativity_failures": alternativity_failures(table),
    }


def generators(table: Table) -> list[int]:
    """Greedy generating set: the smallest basis element outside the span of the products so far."""
    dim = size(table)
    reached = {0}
    chosen: list[int] = []
    while len(reached) < dim:
        nxt = min(set(range(dim)) - reached)
        chosen.append(nxt)
        reached.add(nxt)
        grew = True
        while grew:
            grew = False
            for p, q in itertools.product(sorted(reached), repeat=2):
                sign, r = mul(table, p, q)
                if sign and r not in reached:
                    reached.add(r)
                    grew = True
    return chosen


def _close(a: Table, b: Table, image: dict[int, tuple[int, int]]) -> bool:
    """Extend the partial map by T(e_p e_q) = T(e_p) T(e_q); False on any conflict."""
    used = {target for target, _ in image.values()}
    grew = True
    while grew:
        grew = False
        for p, q in itertools.product(list(image), repeat=2):
            (ip, sp), (iq, sq) = image[p], image[q]
            sa, r = mul(a, p, q)
            sb, k = mul(b, ip, iq)
            if (sa == 0) != (sb == 0):
                return False
            if sa == 0:
                continue
            target = (k, sa * sp * sq * sb)
            if r in image:
                if image[r] != target:
                    return False
            else:
                if k in used:
                    return False
                image[r] = target
                used.add(k)
                grew = True
    return True


def relabelings(a: Table, b: Table) -> list[tuple[list[int], list[int]]]:
    """Every signed relabeling (pi, eta) carrying the products of a onto b, e_0 fixed."""
    dim = size(a)
    if size(b) != dim:
        return []
    gens = generators(a)
    found = []
    for targets in itertools.permutations(range(1, dim), len(gens)):
        for flips in itertools.product((1, -1), repeat=len(gens)):
            image = {0: (0, 1)}
            consistent = True
            for gen, target, flip in zip(gens, targets, flips, strict=True):
                if gen in image:
                    consistent = image[gen] == (target, flip)
                else:
                    image[gen] = (target, flip)
                if not consistent or not _close(a, b, image):
                    consistent = False
                    break
            if consistent and len(image) == dim and _close(a, b, image):
                pi = [image[p][0] for p in range(dim)]
                eta = [0 if image[p][1] > 0 else 1 for p in range(dim)]
                found.append((pi, eta))
    return found


# --------------------------------------------------------------------------
# Extraction (local only): package imports happen inside these functions
# --------------------------------------------------------------------------


def unit_table(dim: int, product: Coefficients) -> Table:
    """Read e_p e_q from a coefficient-returning product: a signed basis unit or zero."""
    signs, index = [], []
    for p in range(dim):
        srow, irow = [], []
        for q in range(dim):
            coeffs = [float(c) for c in product(p, q)]
            require(len(coeffs) == dim, f"e{p} e{q}: {len(coeffs)} coefficients, expected {dim}")
            nonzero = [k for k, c in enumerate(coeffs) if abs(c) > 1e-12]
            if not nonzero:
                srow.append(0)
                irow.append(0)
                continue
            require(len(nonzero) == 1 and abs(abs(coeffs[nonzero[0]]) - 1) < 1e-12, f"e{p} e{q} is not a unit")
            srow.append(1 if coeffs[nonzero[0]] > 0 else -1)
            irow.append(nonzero[0])
        signs.append(srow)
        index.append(irow)
    return {"signs": signs, "index": index}


def int_table(signs: Any, index: Any) -> Table:
    return {"signs": [[int(x) for x in row] for row in signs], "index": [[int(x) for x in row] for row in index]}


def unit(index: int, dim: int) -> list[int]:
    return [1 if k == index else 0 for k in range(dim)]


def blade_masks(names: Sequence[str]) -> list[int]:
    """Bitmask of each blade name such as 'e12', 'e1^e3' or 'e0'; generator k in index order is bit k."""
    digits = [[int(c) for c in name if c.isdigit()] for name in names]
    order = sorted({d for row in digits for d in row})
    return [sum(1 << order.index(d) for d in row) for row in digits]


def hypercomplex_tables() -> dict[str, Table]:
    import hypercomplex

    out = {}
    for n in range(1, 6):
        algebra = hypercomplex.cayley_dickson_algebra(n)

        def product(p: int, q: int, a: Any = algebra) -> Sequence[Any]:
            return (a.e(p) * a.e(q)).coefficients()

        out[f"hypercomplex/D{2**n}"] = unit_table(2**n, product)
    return out


def engine_tables() -> dict[str, Table]:
    import hypercomplex_engine as he

    out = {f"hypercomplex-engine/standard-n{n}": int_table(*he.build_table("standard", n)) for n in range(1, 6)}
    for n in range(1, 5):
        out[f"hypercomplex-engine/split-n{n}"] = int_table(*he.build_table("split", n))
    for n in range(1, 4):
        # multiply(kind, a, b, dim=n): the keyword is the exponent n of D = 2^n, as build_table's n.
        signs, index = [], []
        for p in range(2**n):
            pairs = [he.multiply("split", (1, p), (1, q), dim=n) for q in range(2**n)]
            signs.append([int(s) for s, _ in pairs])
            index.append([int(k) for _, k in pairs])
        out[f"hypercomplex-engine/split-multiply-dim{n}"] = {"signs": signs, "index": index}
    signs, index, eps = he.build_table("dual", 0)
    out["hypercomplex-engine/dual-n0"] = {
        "signs": [[int(x) for x in row] for row in signs],
        "index": [
            [int(i) + 1 * int(e) for i, e in zip(irow, erow, strict=True)]
            for irow, erow in zip(index, eps, strict=True)
        ],
    }
    return out


def expression_tables() -> dict[str, Table]:
    import hypercomplex_algebra as ha

    def parse(text: str) -> tuple[int, int]:
        sign = -1 if text.startswith("-") else 1
        body = text.lstrip("-")
        return sign, 0 if body == "1" else int(body[1:])

    out = {}
    for key, dim, call in (
        ("hypercomplex-algebra/standard-D8", 8, lambda a, b: ha.multiply_expressions(a, b)),
        ("hypercomplex-algebra/split-dim2", 4, lambda a, b: ha.multiply_split_expressions(a, b, 2)),
    ):
        signs, index = [], []
        for p in range(dim):
            pairs = [parse(call(f"e{p}", f"e{q}")) for q in range(dim)]
            signs.append([s for s, _ in pairs])
            index.append([k for _, k in pairs])
        out[key] = {"signs": signs, "index": index}
    return out


CALCULATOR_CLASSES = (
    (2, "compl_mod", "Complex"),
    (4, "quat_mod", "Quaternion"),
    (8, "octonion_mod", "Octonion"),
    (16, "sedenion_mod", "Sedenion"),
    (32, "pathion_mod", "Pathion"),
)


def calculator_tables(split: bool, dims: Sequence[int]) -> dict[str, Table]:
    """Cayley-Calculator levels read through its Mods modules, whose names do not collide."""
    import Cayley_Calculator  # noqa: F401  (puts Mods, Linear, Special and Test on sys.path)
    import gamma_mod

    out = {}
    try:
        if split:
            gamma_mod.set_split()
        for dim, module, cls_name in CALCULATOR_CLASSES:
            if dim not in dims:
                continue
            cls = getattr(importlib.import_module(module), cls_name)

            def product(p: int, q: int, c: Any = cls, d: int = dim) -> Sequence[Any]:
                return list((c(*unit(p, d)) * c(*unit(q, d))).components)

            out[f"Cayley-Calculator/{'split-' if split else ''}D{dim}"] = unit_table(dim, product)
    finally:
        gamma_mod.set_gamma()
    return out


CALCULATOR_WITHOUT_QUATERNION = """
import json, sys
sys.modules["quaternion"] = None
import Cayley_Calculator
import quat_mod, sedenion_mod
def e(p):
    return sedenion_mod.Sedenion(*[1 if k == p else 0 for k in range(16)])
rows = [[[float(c) for c in (e(p) * e(q)).components] for q in range(16)] for p in range(16)]
print(json.dumps({"QUAT_FOUND": [quat_mod.QUAT_FOUND, sedenion_mod.QUAT_FOUND], "rows": rows}))
"""


def calculator_without_quaternion() -> tuple[Table, list[bool]]:
    """Cayley-Calculator sedenions in a process where `import quaternion` raises ImportError."""
    run = subprocess.run(
        [sys.executable, "-W", "ignore", "-c", CALCULATOR_WITHOUT_QUATERNION],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(run.stdout.strip().splitlines()[-1])
    return unit_table(16, lambda p, q: data["rows"][p][q]), data["QUAT_FOUND"]


def cayley_dickson_tables() -> dict[str, Table]:
    import cayley_dickson

    out = {}
    basis: list[Any] = [1]
    for n in range(1, 6):
        basis = list(cayley_dickson.expand_basis(basis))

        def product(p: int, q: int, b: list[Any] = basis) -> Sequence[Any]:
            return list(b[p] * b[q])

        out[f"cayley-dickson/D{2**n}"] = unit_table(2**n, product)
    return out


def torch_octonion_tables() -> dict[str, Table]:
    import octonion
    import torch
    from octonion import _cayley_dickson

    def tensor(p: int, dim: int) -> Any:
        return torch.tensor(unit(p, dim), dtype=torch.float64)

    constants = octonion.STRUCTURE_CONSTANTS.detach().cpu().numpy()
    tower_c = lambda p, q: (octonion.Complex(tensor(p, 2)) * octonion.Complex(tensor(q, 2))).components.tolist()  # noqa: E731
    tower_h = lambda p, q: (octonion.Quaternion(tensor(p, 4)) * octonion.Quaternion(tensor(q, 4))).components.tolist()  # noqa: E731
    return {
        "octonion/fano-D8": unit_table(8, lambda p, q: constants[p, q]),
        "octonion/octonion_mul-D8": unit_table(
            8, lambda p, q: octonion.octonion_mul(tensor(p, 8), tensor(q, 8)).tolist()
        ),
        "octonion/cayley_dickson_mul-D8": unit_table(
            8, lambda p, q: octonion.cayley_dickson_mul(tensor(p, 8), tensor(q, 8)).tolist()
        ),
        "octonion/raw-baez-D8": unit_table(
            8, lambda p, q: _cayley_dickson._raw_cayley_dickson_mul(tensor(p, 8), tensor(q, 8)).tolist()
        ),
        "octonion/tower-Complex-D2": unit_table(2, tower_c),
        "octonion/tower-Quaternion-D4": unit_table(4, tower_h),
    }


def pyoctonion_tables() -> tuple[dict[str, Table], int]:
    """pyoctonion at D = 8, and the count of pyquaternion products one octonion product makes."""
    import pyoctonion
    import pyquaternion

    def product(p: int, q: int) -> list[float]:
        x = pyoctonion.Octonion(*unit(p, 8)) * pyoctonion.Octonion(*unit(q, 8))
        return [x.x_0, x.x_1, x.x_2, x.x_3, x.x_4, x.x_5, x.x_6, x.x_7]

    table = unit_table(8, product)
    original = pyquaternion.Quaternion.__mul__
    calls = 0

    def counting(self: Any, other: Any) -> Any:
        nonlocal calls
        calls += 1
        return original(self, other)

    pyquaternion.Quaternion.__mul__ = counting
    try:
        pyoctonion.Octonion(1, 2, 3, 4, 5, 6, 7, 8) * pyoctonion.Octonion(8, 7, 6, 5, 4, 3, 2, 1)
    finally:
        pyquaternion.Quaternion.__mul__ = original
    return {"pyoctonion/D8": table}, calls


def octonion_sedenion_tables() -> tuple[dict[str, Table], str]:
    """Octonion_Sedenion at D = 8 and 16; the sedenion module imports with its own octonion module bound."""
    own = importlib.import_module("Octonion_Sedenion.octonion")
    saved = sys.modules.get("octonion")
    sys.modules["octonion"] = own
    try:
        sedenion = importlib.import_module("Octonion_Sedenion.sedenion")
    finally:
        if saved is None:
            sys.modules.pop("octonion", None)
        else:
            sys.modules["octonion"] = saved
    half_type = type(own.Octonion(1, 2, 3, 4, 5, 6, 7, 8).z1)
    out = {
        "Octonion-Sedenion/D8": unit_table(
            8, lambda p, q: (own.Octonion(*unit(p, 8)) * own.Octonion(*unit(q, 8))).components
        ),
        "Octonion-Sedenion/D16": unit_table(
            16, lambda p, q: (sedenion.Sedenion(*unit(p, 16)) * sedenion.Sedenion(*unit(q, 16))).components
        ),
    }
    return out, f"{half_type.__module__}.{half_type.__name__}"


def splitoct_tables() -> dict[str, Table]:
    import SplitOct

    return {
        "splitoct/D8": unit_table(
            8, lambda p, q: (SplitOct.SplitOctonion(unit(p, 8)) * SplitOct.SplitOctonion(unit(q, 8))).x
        )
    }


def quaternion_tables() -> dict[str, Table]:
    import pyquaternion
    import quaternion
    import quaternionic

    return {
        "numpy-quaternion/D4": unit_table(
            4,
            lambda p, q: quaternion.as_float_array(
                quaternion.quaternion(*unit(p, 4)) * quaternion.quaternion(*unit(q, 4))
            ),
        ),
        "quaternionic/D4": unit_table(
            4, lambda p, q: (quaternionic.array(unit(p, 4)) * quaternionic.array(unit(q, 4))).ndarray.tolist()
        ),
        "pyquaternion/D4": unit_table(
            4, lambda p, q: (pyquaternion.Quaternion(*unit(p, 4)) * pyquaternion.Quaternion(*unit(q, 4))).elements
        ),
    }


# (p, q, r): p generators square to +1, q to -1, r to 0.
SIGNATURES = (
    (0, 1, 0),
    (1, 0, 0),
    (0, 0, 1),
    (0, 2, 0),
    (1, 1, 0),
    (2, 0, 0),
    (0, 3, 0),
    (1, 2, 0),
    (2, 1, 0),
    (3, 0, 0),
)


def signature_name(sig: Sequence[int]) -> str:
    return f"Cl({sig[0]},{sig[1]})" if sig[2] == 0 else f"Cl({sig[0]},{sig[1]},{sig[2]})"


def bitmask_table(dim: int, names: Sequence[str], product: Coefficients) -> Table:
    """A Clifford table in bitmask order: blade names give each native position its bitmask."""
    masks = blade_masks(names)
    require(sorted(masks) == list(range(dim)), f"blades {list(names)} do not cover the bitmasks")
    native = {mask: k for k, mask in enumerate(masks)}

    def by_mask(p: int, q: int) -> list[float]:
        coeffs = [float(c) for c in product(native[p], native[q])]
        return [coeffs[native[m]] for m in range(dim)]

    return unit_table(dim, by_mask)


def clifford_tables() -> dict[str, Table]:
    import clifford
    import galgebra.ga
    import kingdon
    import sympy

    out = {}
    for sig in SIGNATURES:
        dim = 2 ** sum(sig)
        name = signature_name(sig)
        layout, blades = clifford.Cl(*sig)
        basis = [layout.scalar] + [blades[n] for n in layout.names[1:]]

        def clifford_product(p: int, q: int, b: list[Any] = basis) -> Sequence[Any]:
            return list((b[p] * b[q]).value)

        out[f"clifford/{name}"] = bitmask_table(dim, ["e"] + list(layout.names[1:]), clifford_product)
        algebra = kingdon.Algebra(*sig, pretty_blade="e")
        keys = list(algebra.blades.keys())
        kbasis = [algebra.blades[k] for k in keys]
        # A product's keys are kingdon's blade bitmasks; each basis blade carries its own single key.
        native = {blade.keys()[0]: k for k, blade in enumerate(kbasis)}

        def kingdon_product(
            p: int, q: int, b: list[Any] = kbasis, d: int = dim, at: dict[int, int] = native
        ) -> list[float]:
            prod = b[p] * b[q]
            coeffs = [0.0] * d
            for key, value in zip(prod.keys(), prod.values(), strict=True):
                coeffs[at[key]] += float(value)
            return coeffs

        # kingdon names a null generator e0 (start index 0 when r > 0) and the others from e1.
        out[f"kingdon/{name}"] = bitmask_table(dim, keys, kingdon_product)
        if sum(sig) >= 2:
            metric = [1] * sig[0] + [-1] * sig[1] + [0] * sig[2]
            symbols = " ".join(f"e{k + 1}" for k in range(len(metric)))
            ga, *gens = galgebra.ga.Ga.build(symbols, g=metric)
            gbasis = [ga.mv(sympy.S.One, "scalar")]
            gnames = ["e"]
            for grade in range(1, len(gens) + 1):
                for combo in itertools.combinations(range(len(gens)), grade):
                    blade = gens[combo[0]]
                    for k in combo[1:]:
                        blade = blade ^ gens[k]
                    gbasis.append(blade)
                    gnames.append("e" + "".join(str(k + 1) for k in combo))

            def galgebra_product(p: int, q: int, b: list[Any] = gbasis) -> Sequence[Any]:
                return [float(c) for c in (b[p] * b[q]).blade_coefs(b)]

            out[f"galgebra/{name}"] = bitmask_table(dim, gnames, galgebra_product)
    return out


SAGE_PROGRAM = """
import json
from sage.all import QQ, QuaternionAlgebra, OctonionAlgebra
def table(A):
    B = list(A.basis())
    pos = {b: k for k, b in enumerate(B)}
    signs, index = [], []
    for x in B:
        srow, irow = [], []
        for y in B:
            terms = list((x * y).monomial_coefficients().items()) if hasattr(x * y, "monomial_coefficients") else None
            if terms is None:
                v = list((x * y).coefficient_tuple())
                terms = [(k, c) for k, c in enumerate(v) if c]
            else:
                terms = [(list(A.basis().keys()).index(k), c) for k, c in terms if c]
            assert len(terms) == 1 and abs(terms[0][1]) == 1
            srow.append(int(terms[0][1])); irow.append(int(terms[0][0]))
        signs.append(srow); index.append(irow)
    return {"labels": [str(b) for b in B], "signs": signs, "index": index}
print(json.dumps({
    "sagemath/octonion(-1,-1,-1)": table(OctonionAlgebra(QQ)),
    "sagemath/octonion(1,1,1)": table(OctonionAlgebra(QQ, 1, 1, 1)),
    "sagemath/quaternion(-1,-1)": table(QuaternionAlgebra(QQ, -1, -1)),
    "sagemath/quaternion(1,1)": table(QuaternionAlgebra(QQ, 1, 1)),
}))
"""


def sage_tables() -> dict[str, Table]:
    run = subprocess.run(["sage", "-c", SAGE_PROGRAM], capture_output=True, text=True, check=True)
    data: dict[str, Table] = json.loads(run.stdout.strip().splitlines()[-1])
    return data


def mathdunders_probe() -> dict[str, list[str]]:
    """Which hypercomplex classes carry the mathdunders-generated dunder methods."""
    import hypercomplex

    def generated(cls: type) -> list[str]:
        return sorted(
            name
            for name, value in vars(cls).items()
            if callable(value) and getattr(value, "__qualname__", "").endswith("make_dunder.<locals>.dunder")
        )

    return {
        "reals": generated(hypercomplex.R),
        "complex": generated(hypercomplex.C),
        "octonion": generated(hypercomplex.O),
    }


def expression_engine_calls() -> int:
    """Engine index evaluations during one hypercomplex-algebra product of two two-term expressions."""
    import hypercomplex_algebra
    import hypercomplex_engine

    original = hypercomplex_engine.FastStandard.multiply_indices
    calls = 0

    def counting(self: Any, i: int, j: int) -> Any:
        nonlocal calls
        calls += 1
        return original(self, i, j)

    hypercomplex_engine.FastStandard.multiply_indices = counting
    try:
        hypercomplex_algebra.ExpressionMultiplier(kind="standard").multiply("e1 + e2", "e3 - e4")
    finally:
        hypercomplex_engine.FastStandard.multiply_indices = original
    return calls


def extract() -> dict[str, Any]:
    tables: dict[str, Table] = {}
    tables |= hypercomplex_tables()
    tables |= engine_tables()
    tables |= expression_tables()
    tables |= calculator_tables(False, (2, 4, 8, 16, 32))
    tables |= calculator_tables(True, (2, 4, 8, 16))
    without, quat_found = calculator_without_quaternion()
    tables["Cayley-Calculator/D16-without-numpy-quaternion"] = without
    tables |= cayley_dickson_tables()
    tables |= torch_octonion_tables()
    pyoct, pyquaternion_calls = pyoctonion_tables()
    tables |= pyoct
    os_tables, os_half_type = octonion_sedenion_tables()
    tables |= os_tables
    tables |= splitoct_tables()
    tables |= quaternion_tables()
    tables |= clifford_tables()
    tables |= sage_tables()
    probes = {
        "pyoctonion_pyquaternion_mul_calls_per_product": pyquaternion_calls,
        "octonion_sedenion_half_type": os_half_type,
        "cayley_calculator_quat_found_without_numpy_quaternion": quat_found,
        "mathdunders_generated_dunders": mathdunders_probe(),
        "hypercomplex_algebra_engine_calls_per_two_term_product": expression_engine_calls(),
    }
    return {"schema": SCHEMA, "tables": tables, "probes": probes}


# --------------------------------------------------------------------------
# Declared relations (--check)
# --------------------------------------------------------------------------

# kind: identical | relabeling (count) | opposite (count) | subalgebra (elements, then identical or relabeling)
#       | not-isomorphic (invariant)
RELATIONS: list[dict[str, Any]] = [
    # Ordinary Cayley-Dickson levels.
    *(
        {"table": f"hypercomplex/D{d}", "ref": r, "kind": "identical"}
        for d, r in ((2, "C"), (4, "H"), (8, "O"), (16, "S"), (32, "CD32"))
    ),
    *(
        {"table": f"hypercomplex-engine/standard-n{n}", "ref": r, "kind": "identical"}
        for n, r in ((1, "C"), (2, "H"), (3, "O"), (4, "S"), (5, "CD32"))
    ),
    {"table": "hypercomplex-algebra/standard-D8", "ref": "O", "kind": "identical"},
    *(
        {"table": f"Cayley-Calculator/D{d}", "ref": r, "kind": "identical"}
        for d, r in ((2, "C"), (4, "H"), (8, "O"), (16, "S"), (32, "CD32"))
    ),
    {"table": "Cayley-Calculator/D16-without-numpy-quaternion", "ref": "S", "kind": "identical"},
    *(
        {"table": f"cayley-dickson/D{d}", "ref": r, "kind": "identical"}
        for d, r in ((2, "C"), (4, "H"), (8, "O"), (16, "S"), (32, "CD32"))
    ),
    {"table": "pyoctonion/D8", "ref": "O", "kind": "identical"},
    {"table": "Octonion-Sedenion/D8", "ref": "O", "kind": "identical"},
    {"table": "Octonion-Sedenion/D16", "ref": "S", "kind": "identical"},
    {"table": "octonion/tower-Complex-D2", "ref": "C", "kind": "identical"},
    {"table": "octonion/tower-Quaternion-D4", "ref": "H", "kind": "identical"},
    {"table": "octonion/octonion_mul-D8", "ref": "octonion/fano-D8", "kind": "identical"},
    {"table": "octonion/cayley_dickson_mul-D8", "ref": "octonion/fano-D8", "kind": "identical"},
    {"table": "octonion/fano-D8", "ref": "O", "kind": "relabeling", "count": 1344},
    {"table": "octonion/raw-baez-D8", "ref": "O", "kind": "relabeling", "count": 1344},
    {"table": "octonion/raw-baez-D8", "ref": "O", "kind": "not-identical"},
    {"table": "octonion/raw-baez-D8", "ref": "O", "kind": "opposite-not-identical"},
    {"table": "sagemath/octonion(-1,-1,-1)", "ref": "O", "kind": "opposite", "count": 1344},
    {"table": "sagemath/quaternion(-1,-1)", "ref": "H", "kind": "identical"},
    # Quaternion packages.
    *(
        {"table": f"{pkg}/D4", "ref": "H", "kind": "identical"}
        for pkg in ("numpy-quaternion", "quaternionic", "pyquaternion")
    ),
    # Split levels.
    *(
        {"table": f"hypercomplex-engine/split-n{n}", "ref": r, "kind": "identical"}
        for n, r in ((1, "split-C"), (2, "split-H"), (3, "split-O"), (4, "split-S"))
    ),
    *(
        {"table": f"hypercomplex-engine/split-multiply-dim{n}", "ref": r, "kind": "identical"}
        for n, r in ((1, "split-C"), (2, "split-H"), (3, "split-O"))
    ),
    {"table": "hypercomplex-algebra/split-dim2", "ref": "split-H", "kind": "identical"},
    {"table": "splitoct/D8", "ref": "split-O", "kind": "identical"},
    {"table": "Cayley-Calculator/split-D2", "ref": "split-C", "kind": "identical"},
    {"table": "Cayley-Calculator/split-D4", "ref": "split-H", "kind": "relabeling"},
    {"table": "Cayley-Calculator/split-D8", "ref": "split-O", "kind": "relabeling"},
    # All gammas +1 at D = 16 against one split doubling over the octonions: the same norm signature (8, 8)
    # and 1848 nonassociative basis triples, and no signed relabeling. The even-parity basis elements of the
    # former close into a positive-definite quadratic algebra that is not alternative, so not the octonions.
    {"table": "Cayley-Calculator/split-D16", "ref": "split-S", "kind": "no-signed-relabeling"},
    {
        "table": "Cayley-Calculator/split-D16",
        "ref": "O",
        "kind": "not-isomorphic",
        "invariant": "alternativity",
        "elements": [0, 3, 5, 6, 9, 10, 12, 15],
    },
    {"table": "split-S", "ref": "O", "kind": "subalgebra", "elements": list(range(8))},
    {"table": "sagemath/quaternion(1,1)", "ref": "split-H", "kind": "relabeling"},
    {"table": "sagemath/octonion(1,1,1)", "ref": "split-O", "kind": "relabeling"},
    {"table": "split-O", "ref": "O", "kind": "not-isomorphic", "invariant": "norm-signature"},
    # Dual numbers.
    {"table": "hypercomplex-engine/dual-n0", "ref": "dual", "kind": "identical"},
    # Clifford algebras: one-generator and two-generator signatures.
    *(
        {"table": f"{pkg}/{sig}", "ref": ref, "kind": kind}
        for pkg in ("clifford", "kingdon")
        for sig, ref, kind in (
            ("Cl(0,1)", "C", "identical"),
            ("Cl(1,0)", "split-C", "identical"),
            ("Cl(0,0,1)", "dual", "identical"),
        )
    ),
    *(
        {"table": f"{pkg}/{sig}", "ref": ref, "kind": kind}
        for pkg in ("clifford", "kingdon", "galgebra")
        for sig, ref, kind in (
            ("Cl(0,2)", "H", "identical"),
            ("Cl(1,1)", "split-H", "relabeling"),
            ("Cl(2,0)", "split-H", "relabeling"),
        )
    ),
    # Three generators: associative, so neither octonions nor split octonions; even subalgebras.
    *(
        {"table": f"{pkg}/{sig}", "ref": ref, "kind": "not-isomorphic", "invariant": "associativity"}
        for pkg in ("clifford", "kingdon", "galgebra")
        for sig in ("Cl(0,3)", "Cl(1,2)", "Cl(2,1)", "Cl(3,0)")
        for ref in ("O", "split-O")
    ),
    *(
        {"table": f"{pkg}/{sig}", "ref": ref, "kind": "subalgebra", "elements": [0, 3, 5, 6]}
        for pkg in ("clifford", "kingdon", "galgebra")
        for sig, ref in (("Cl(0,3)", "H"), ("Cl(3,0)", "H"), ("Cl(1,2)", "split-H"), ("Cl(2,1)", "split-H"))
    ),
    *(
        {"table": f"{pkg}/{sig}", "ref": ref, "kind": "subalgebra", "elements": [0, 3]}
        for pkg in ("clifford", "kingdon", "galgebra")
        for sig, ref in (("Cl(0,2)", "C"), ("Cl(1,1)", "split-C"), ("Cl(2,0)", "C"))
    ),
    # Quaternion and complex levels inside every larger cd_core level.
    {"table": "O", "ref": "H", "kind": "subalgebra", "elements": [0, 1, 2, 3]},
    {"table": "S", "ref": "O", "kind": "subalgebra", "elements": list(range(8))},
    {"table": "CD32", "ref": "S", "kind": "subalgebra", "elements": list(range(16))},
    {"table": "split-O", "ref": "H", "kind": "subalgebra", "elements": [0, 1, 2, 3]},
    {"table": "split-O", "ref": "split-H", "kind": "subalgebra", "elements": [0, 1, 4, 5]},
    {"table": "split-O", "ref": "split-C", "kind": "subalgebra", "elements": [0, 4]},
]
CALIBRATION = (("H", 24), ("O", 1344))


def resolve(name: str, tables: dict[str, Table]) -> Table:
    return REFERENCES[name]() if name in REFERENCES else tables[name]


def check_relation(relation: dict[str, Any], tables: dict[str, Table]) -> str:
    table = resolve(relation["table"], tables)
    ref = resolve(relation["ref"], tables)
    kind = relation["kind"]
    label = f"{relation['table']} -> {relation['ref']}"
    if kind != "subalgebra" and "elements" in relation:
        table = restrict(table, relation["elements"])
        label = f"{relation['table']} on e{relation['elements']} -> {relation['ref']}"
    if kind == "subalgebra":
        sub = restrict(table, relation["elements"])
        if same(sub, ref):
            return f"{label}: subalgebra on e{relation['elements']} identical"
        maps = relabelings(sub, ref)
        require(bool(maps), f"{label}: subalgebra on {relation['elements']} carries no signed relabeling")
        return f"{label}: subalgebra on e{relation['elements']} by {len(maps)} signed relabelings, first {maps[0]}"
    if kind == "identical":
        require(same(table, ref), f"{label}: not identical")
        return f"{label}: identical"
    if kind == "not-identical":
        require(not same(table, ref), f"{label}: identical")
        return f"{label}: not identical in its own basis order"
    if kind == "opposite-not-identical":
        require(not same(transpose(table), ref), f"{label}: the opposite table is identical")
        return f"{label}: not the opposite table in its own basis order"
    if kind in ("relabeling", "opposite"):
        source = transpose(table) if kind == "opposite" else table
        require(not same(source, ref) or kind == "opposite", f"{label}: identical, declared as a relabeling")
        maps = relabelings(source, ref)
        require(bool(maps), f"{label}: no signed relabeling")
        if "count" in relation:
            require(len(maps) == relation["count"], f"{label}: {len(maps)} relabelings, expected {relation['count']}")
        prefix = "opposite algebra " if kind == "opposite" else ""
        return f"{label}: {prefix}{len(maps)} signed relabelings, first {maps[0]}"
    if kind == "not-isomorphic":
        a, b = invariants(table), invariants(ref)
        if relation["invariant"] == "associativity":
            require(
                a["nonassociative_triples"] == 0 and b["nonassociative_triples"] > 0,
                f"{label}: associativity does not separate {a} from {b}",
            )
            return f"{label}: not isomorphic, 0 versus {b['nonassociative_triples']} nonassociative basis triples"
        if relation["invariant"] == "alternativity":
            require(
                a["alternativity_failures"] > 0 and b["alternativity_failures"] == 0,
                f"{label}: alternativity does not separate {a} from {b}",
            )
            return f"{label}: not isomorphic, {a['alternativity_failures']} versus 0 basis triples break alternativity"
        require(relation["invariant"] == "norm-signature", f"{label}: unknown invariant {relation['invariant']}")
        require(
            a["quadratic"] and b["quadratic"] and a["norm_signature"] != b["norm_signature"],
            f"{label}: the norm-form signature does not separate {a} from {b}",
        )
        return f"{label}: not isomorphic, norm-form signatures {a['norm_signature']} versus {b['norm_signature']}"
    if kind == "no-signed-relabeling":
        require(not relabelings(table, ref), f"{label}: a signed relabeling exists")
        a, b = invariants(table), invariants(ref)
        return (
            f"{label}: no signed relabeling; norm signatures {a['norm_signature']} and {b['norm_signature']},"
            f" nonassociative basis triples {a['nonassociative_triples']} and {b['nonassociative_triples']}"
        )
    raise RuntimeError(f"unknown relation kind {kind}")


def check(data: dict[str, Any]) -> list[str]:
    require(data.get("schema") == SCHEMA, "unknown evidence schema")
    tables: dict[str, Table] = data["tables"]
    lines = []
    for name, count in CALIBRATION:
        found = len(relabelings(REFERENCES[name](), REFERENCES[name]()))
        require(found == count, f"calibration: {found} automorphisms of {name}, expected {count}")
        lines.append(f"calibration: cd_core {name} has {found} signed-relabeling automorphisms")
    for relation in RELATIONS:
        lines.append(check_relation(relation, tables))
    for pkg_a, pkg_b in (("clifford", "kingdon"), ("clifford", "galgebra")):
        for sig in SIGNATURES:
            name = signature_name(sig)
            if f"{pkg_b}/{name}" in tables:
                require(
                    same(tables[f"{pkg_a}/{name}"], tables[f"{pkg_b}/{name}"]), f"{pkg_a} and {pkg_b} differ on {name}"
                )
    lines.append("clifford, kingdon and galgebra: identical bitmask-order tables on every shared signature")
    for name, table in sorted(tables.items()):
        inv = invariants(table)
        require(inv["unit_e0"], f"{name}: e0 is not the identity")
        if name.split("/")[0] in ("clifford", "kingdon", "galgebra"):
            require(inv["nonassociative_triples"] == 0, f"{name}: a Clifford table is nonassociative")
        elif inv["squares_zero"] == 0:
            # Every Cayley-Dickson-type table up to D = 8 is alternative; from D = 16 on none is.
            require((inv["alternativity_failures"] == 0) == (inv["dim"] <= 8), f"{name}: alternativity differs")
            require(inv["quadratic"], f"{name}: not a quadratic table")
        lines.append(
            f"invariants {name}: D={inv['dim']} squares(-1,+1,0)=({inv['squares_minus_one']},{inv['squares_plus_one']},"
            f"{inv['squares_zero']}) norm={inv['norm_signature']} commutative={inv['commutative']}"
            f" nonassociative_triples={inv['nonassociative_triples']}"
            f" alternativity_failures={inv['alternativity_failures']}"
        )
    probes = data["probes"]
    require(probes["pyoctonion_pyquaternion_mul_calls_per_product"] > 0, "pyoctonion multiplies without pyquaternion")
    require(
        probes["octonion_sedenion_half_type"] == "quaternion.quaternion",
        "Octonion-Sedenion halves are not numpy-quaternion",
    )
    require(
        probes["cayley_calculator_quat_found_without_numpy_quaternion"] == [False, False],
        "Cayley-Calculator found quaternion",
    )
    require(
        probes["hypercomplex_algebra_engine_calls_per_two_term_product"] > 0, "hypercomplex-algebra bypasses the engine"
    )
    generated = probes["mathdunders_generated_dunders"]
    require(
        bool(generated["reals"]) and not generated["complex"] and not generated["octonion"], "mathdunders scope differs"
    )
    for key, value in probes.items():
        lines.append(f"probe {key}: {value}")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--extract", action="store_true", help="import the installed packages and retain their tables")
    mode.add_argument("--check", action="store_true", help="verify the retained tables against cd_core")
    parser.add_argument("--verbose", action="store_true", help="print every relation and invariant line")
    args = parser.parse_args()
    if args.extract:
        EVIDENCE.write_text(json.dumps(extract(), indent=None, separators=(",", ":"), sort_keys=True) + "\n")
        print(f"wrote {EVIDENCE.relative_to(ROOT)}")
    lines = check(json.loads(EVIDENCE.read_text()))
    if args.verbose:
        print("\n".join(lines))
    print(
        f"algebra interplay: {len(RELATIONS)} relations and {len(lines) - len(RELATIONS)}"
        " calibration, invariant and probe lines hold"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
