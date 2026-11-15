"""The dim L = 4 point at mu nonzero: the exact identities, the Krawczyk box, the cross-checks and the record rules."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pytest
import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "docs" / "evidence" / "a5-kernel-bundles-residuals"))

import nullity4_real_polar_fiber_four as fiber  # noqa: E402


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


@pytest.mark.parametrize("index", range(14))
def test_derivation_is_skew_block_and_equivariant(index: int) -> None:
    _same(fiber.derivation_identity(index), True)


def test_a_perturbed_derivation_breaks_the_identity(monkeypatch: pytest.MonkeyPatch) -> None:
    # An entry added above the diagonal of D_1 leaves the skew matrices and the equivariance of M.
    bad = [matrix.copy() for matrix in fiber._derivations()]
    bad[0][0, 1] += 1
    monkeypatch.setattr(fiber, "_derivations", lambda: bad)
    _same(fiber.derivation_identity(0), False)


def test_unit_products_anticommute() -> None:
    _same(fiber.unit_products_anticommute(), True)


def test_normal_form_lies_on_the_cone_off_v_q() -> None:
    _same(fiber.normal_form_facts(), fiber.POINT_FACTS)


def test_rank_and_polar_line_facts() -> None:
    _same(fiber.rank_of_M_at_the_normal_form(), 12)
    _same(
        fiber.polar_line_facts(),
        {"in_kernel": True, "stack_rank": 12, "z0_in_C": True, "ranks": [8, 8, 8, 8, 8]},
    )


def test_basis_of_c_holds_the_normal_form_point() -> None:
    z0, line, basis = fiber._exact()
    _same(basis[0], z0)
    _same(len(line), 2)
    _same(len(basis), 3)


def test_krawczyk_box_maps_into_its_interior() -> None:
    result = fiber.krawczyk(fiber.MIDPOINT, fiber.RADIUS_BITS)
    _same(
        result,
        {"interior": True, "contraction_bits": fiber.CONTRACTION_BITS, "pairing_bound_bits": fiber.PAIRING_BOUND_BITS},
    )


def test_krawczyk_rejects_a_shifted_midpoint() -> None:
    # The midpoint moved by 2^-20 lies farther from the zero than the radius 2^-24, so K(X) leaves X.
    shifted = (fiber.MIDPOINT[0] + (1 << (fiber.MIDPOINT_BITS - 20)), *fiber.MIDPOINT[1:])
    _same(fiber.krawczyk(shifted, fiber.RADIUS_BITS)["interior"], False)


def test_krawczyk_rejects_a_box_too_wide_for_the_jacobian() -> None:
    # At radius 2^-1 K(X) leaves X and the ball of the pairing entry contains zero.
    result = fiber.krawczyk(fiber.MIDPOINT, 1)
    _same((result["interior"], result["pairing_bound_bits"]), (False, -1))


def _double_t(midpoint: tuple[int, ...]) -> np.ndarray:
    xi = np.array([float(sp.Rational(fiber.FIXED_NUMERATORS.get(i, 0), 1 << fiber.FIXED_BITS)) for i in range(14)])
    for index, numerator in zip(fiber.SLICE_FREE, midpoint, strict=True):
        xi[index] = float(sp.Rational(numerator, 1 << fiber.MIDPOINT_BITS))
    matrices = np.array([np.array(m.tolist(), dtype=float) for m in fiber._derivations()])
    values, vectors = np.linalg.eigh(1j * np.tensordot(xi, matrices, axes=1))
    pi = (vectors * np.exp(2 * values)) @ vectors.conj().T
    _, line, basis = fiber._exact()
    z = np.array([[complex(sp.N(entry, 30)) for entry in vector] for vector in basis]).T
    columns = np.array([[complex(sp.N(entry, 30)) for entry in vector] for vector in line]).T
    return np.asarray(z.conj().T @ pi @ columns)


def test_interval_evaluation_agrees_with_a_double_precision_evaluation() -> None:
    reference = _double_t(fiber.MIDPOINT)
    serialized, _ = fiber.evaluation((0, fiber.MIDPOINT, fiber.SLICE_FREE[0]))
    found = fiber._de_matrix(serialized)
    scale = np.abs(reference).max()
    for a in range(3):
        for b in range(2):
            entry = complex(float(found[a, b].real.mid()), float(found[a, b].imag.mid()))
            if abs(entry - reference[a, b]) > 1e-9 * scale:
                raise AssertionError((a, b, entry, reference[a, b]))
    # The row F of z_0 and the determinant of the two other rows vanish to double precision at the midpoint.
    _same(bool(np.abs(reference[0]).max() < 1e-9 * scale), True)
    _same(bool(abs(np.linalg.det(reference[1:])) < 1e-9 * scale**2), True)


@pytest.mark.parametrize("column", range(len(fiber.SLICE_FREE)))
def test_jacobian_column_matches_central_differences(column: int) -> None:
    # The block-exponential derivative of a free column agrees with a central difference of f at the midpoint.
    step = 1 << (fiber.MIDPOINT_BITS - 30)
    t, dt = fiber.evaluation((0, fiber.MIDPOINT, fiber.SLICE_FREE[column]))
    _, jacobian = fiber._equations(fiber._de_matrix(t), [fiber._de_matrix(dt)])
    plus = list(fiber.MIDPOINT)
    minus = list(fiber.MIDPOINT)
    plus[column] += step
    minus[column] -= step
    tp, _ = fiber.evaluation((0, tuple(plus), fiber.SLICE_FREE[column]))
    tm, _ = fiber.evaluation((0, tuple(minus), fiber.SLICE_FREE[column]))
    fp, _ = fiber._equations(fiber._de_matrix(tp), [])
    fm, _ = fiber._equations(fiber._de_matrix(tm), [])
    width = 2.0 * step / (1 << fiber.MIDPOINT_BITS)
    for row in range(6):
        numeric = float((fp[row] - fm[row]).mid()) / width
        analytic = float(jacobian[row][0].mid())
        if abs(numeric - analytic) > 1e-5 * max(1.0, abs(analytic)):
            raise AssertionError((column, row, numeric, analytic))


def test_double_precision_dimensions_at_the_midpoint() -> None:
    _same(fiber.double_precision_facts(fiber.MIDPOINT), fiber.DOUBLE_FACTS)


def test_double_precision_dimensions_change_off_the_zero() -> None:
    # Moving a free coordinate by 0.3 leaves conjugate(z).l_z = 0, so P differs from l_z and the fiber dimension moves.
    moved = (fiber.MIDPOINT[0] + int(0.3 * (1 << fiber.MIDPOINT_BITS)), *fiber.MIDPOINT[1:])
    facts = fiber.double_precision_facts(moved)
    _same(facts["fiber_dimension_of_L_z"] == fiber.DOUBLE_FACTS["fiber_dimension_of_L_z"], False)


def _record() -> dict[str, Any]:
    return json.loads(fiber.RECORD.read_text(encoding="utf-8"))


def test_pinned_record_passes_its_rules(monkeypatch: pytest.MonkeyPatch) -> None:
    record = _record()
    retained_inputs = dict(record["inputs"])
    monkeypatch.setattr(fiber, "_inputs", lambda: dict(retained_inputs))
    _same(fiber.verdict(record), [])
    _same(record["pass"], True)
    _same(fiber._serialized(record), fiber.RECORD.read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    ("label", "mutate"),
    [
        ("an identity", lambda r: r["identities"].__setitem__("rank_8_at_five_polar_vectors", False)),
        ("the normal-form point", lambda r: r["point"].__setitem__("mu", "0")),
        ("a rank", lambda r: r["exact"].__setitem__("rank_M_z0", 11)),
        ("the slice", lambda r: r["slice"]["midpoint"].__setitem__(0, 0)),
        ("the containment", lambda r: r["krawczyk"].__setitem__("interior", False)),
        ("the pairing bound", lambda r: r["krawczyk"].__setitem__("pairing_bound_bits", -1)),
        ("a double-precision dimension", lambda r: r["double_precision"].__setitem__("fiber_dimension_of_L_z", 1)),
        ("a claim", lambda r: r["claims"].__setitem__("exact_point", True)),
        ("the verdict flag", lambda r: r.__setitem__("pass", False)),
    ],
)
def test_record_rules_reject_a_planted_mutant(label: str, mutate: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    record = _record()
    retained_inputs = dict(record["inputs"])
    monkeypatch.setattr(fiber, "_inputs", lambda: dict(retained_inputs))
    mutate(record)
    if not fiber.verdict(record):
        raise AssertionError(label)
