"""Identity maps from external hypercomplex packages onto cd_core, checked on every basis pair.

AGENTS.md ("Grounding and algebra") admits a package result into evidence
only through a declared map onto `cd_core`, checked on every basis pair.
This module checks the identity map of each package that
docs/notes/hypercomplex-libraries.md lists with that role: the product table
`e_p e_q = sign e_(p xor q)` read from the package equals `cd_core.cd_sign`
at every pair. A package absent from the interpreter skips its cases with the
import name in the reason; the hosted pins hold none of these packages, so
the comparator controls below run everywhere and the package cases run where
the packages import (the exploratory environment of docs/PYTHON.md).
"""

from __future__ import annotations

import importlib
from collections.abc import Callable

import algebra_package_tables as tables
import pytest

import cd_core

Table = dict[str, list[list[int]]]


def identity_mismatches(dim: int, table: Table) -> list[tuple[int, int]]:
    """Every pair (p, q) whose retained sign or index differs from cd_core."""
    bad = []
    for p in range(dim):
        for q in range(dim):
            if table["signs"][p][q] != cd_core.cd_sign(dim, p, q) or table["index"][p][q] != p ^ q:
                bad.append((p, q))
    return bad


def cd_core_table(dim: int) -> Table:
    return {
        "signs": [[cd_core.cd_sign(dim, p, q) for q in range(dim)] for p in range(dim)],
        "index": [[p ^ q for q in range(dim)] for p in range(dim)],
    }


@pytest.mark.parametrize("dim", [4, 8, 16, 32])
def test_comparator_accepts_cd_core_table(dim: int) -> None:
    if identity_mismatches(dim, cd_core_table(dim)):
        raise AssertionError("the cd_core table must match itself on every pair")


@pytest.mark.parametrize("field", ["signs", "index"])
def test_comparator_rejects_one_entry_mutant(field: str) -> None:
    table = cd_core_table(8)
    table[field][3][5] = -table[field][3][5] if field == "signs" else table[field][3][5] ^ 1
    if identity_mismatches(8, table) != [(3, 5)]:
        raise AssertionError("a single changed entry must fail at exactly its pair")


def hypercomplex_table(dim: int) -> Table:
    hypercomplex = importlib.import_module("hypercomplex")
    algebra = hypercomplex.cayley_dickson_algebra(dim.bit_length() - 1)
    return tables.unit_table(dim, lambda p, q: (algebra.e(p) * algebra.e(q)).coefficients())


def engine_table(dim: int) -> Table:
    engine = importlib.import_module("hypercomplex_engine")
    return tables.int_table(*engine.build_table("standard", dim.bit_length() - 1))


def numpy_quaternion_table(dim: int) -> Table:
    quaternion = importlib.import_module("quaternion")
    return tables.unit_table(
        dim,
        lambda p, q: quaternion.as_float_array(
            quaternion.quaternion(*tables.basis(p, dim)) * quaternion.quaternion(*tables.basis(q, dim))
        ),
    )


def quaternionic_table(dim: int) -> Table:
    quaternionic = importlib.import_module("quaternionic")
    return tables.unit_table(
        dim,
        lambda p, q: (
            quaternionic.array(tables.basis(p, dim)) * quaternionic.array(tables.basis(q, dim))
        ).ndarray.tolist(),
    )


def pyquaternion_table(dim: int) -> Table:
    pyquaternion = importlib.import_module("pyquaternion")
    return tables.unit_table(
        dim,
        lambda p, q: (
            (pyquaternion.Quaternion(*tables.basis(p, dim)) * pyquaternion.Quaternion(*tables.basis(q, dim))).elements
        ),
    )


def pyoctonion_table(dim: int) -> Table:
    pyoctonion = pytest.importorskip("pyoctonion", reason="pyoctonion is not installed in this interpreter")

    def product(p: int, q: int) -> list[float]:
        out = pyoctonion.Octonion(*tables.basis(p, 8)) * pyoctonion.Octonion(*tables.basis(q, 8))
        return [out.x_0, out.x_1, out.x_2, out.x_3, out.x_4, out.x_5, out.x_6, out.x_7]

    return tables.unit_table(dim, product)


def octonion_sedenion_rows() -> dict[tuple[str, int], Table]:
    """Octonion-Sedenion tables; the shared builder imports pyoctonion too, so each case has its own gate."""
    for module in ("pyoctonion", "Octonion_Sedenion.octonion"):
        pytest.importorskip(module, reason=f"{module} is not installed in this interpreter")
    return {(name, dim): table for name, dim, table, _ in tables.octonion_and_sedenion_tables()}


# Distribution -> (import name that gates the case, dimensions checked, builder).
FLAT_CASES: dict[str, tuple[str, tuple[int, ...], Callable[[int], Table]]] = {
    "hypercomplex": ("hypercomplex", (4, 8, 16, 32), hypercomplex_table),
    "hypercomplex-engine": ("hypercomplex_engine", (4, 8, 16, 32, 64), engine_table),
    "numpy-quaternion": ("quaternion", (4,), numpy_quaternion_table),
    "quaternionic": ("quaternionic", (4,), quaternionic_table),
    "pyquaternion": ("pyquaternion", (4,), pyquaternion_table),
}


@pytest.mark.parametrize(("name", "dim"), [(name, dim) for name, (_, dims, _) in FLAT_CASES.items() for dim in dims])
def test_package_table_is_identical_to_cd_core(name: str, dim: int) -> None:
    module, _, build = FLAT_CASES[name]
    pytest.importorskip(module, reason=f"{module} is not installed in this interpreter")
    mismatches = identity_mismatches(dim, build(dim))
    if mismatches:
        raise AssertionError(f"{name} D={dim}: {len(mismatches)} of {dim * dim} pairs differ, first {mismatches[0]}")


@pytest.mark.parametrize(("name", "dim"), [("pyoctonion", 8), ("Octonion-Sedenion", 8), ("Octonion-Sedenion", 16)])
def test_octonion_and_sedenion_table_is_identical_to_cd_core(name: str, dim: int) -> None:
    table = pyoctonion_table(dim) if name == "pyoctonion" else octonion_sedenion_rows()[(name, dim)]
    mismatches = identity_mismatches(dim, table)
    if mismatches:
        raise AssertionError(f"{name} D={dim}: {len(mismatches)} of {dim * dim} pairs differ, first {mismatches[0]}")
