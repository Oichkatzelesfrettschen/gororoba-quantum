"""Exact real circle-frontier graphs and the induced unit-partner collapse.

Orthogonal frame identities give a full real-circle inverse on limiting
planes. A global rational cone frame supplies the graph closure through its
vertex. The integral chain contraction records the evaluation map separately
from the topology of its source and target.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

import sympy as sp

import circle_kernel_attachments as cone
from integral_homology import integral_homology, matrix_record

AMPLITUDE, COSINE, SINE = sp.symbols("s a b", real=True)


def _real(value: object) -> sp.Expr:
    try:
        expression = sp.sympify(value)
    except (TypeError, sp.SympifyError) as error:
        raise ValueError("coordinates require exact real algebraic numbers") from error
    if (
        isinstance(value, bool)
        or not isinstance(expression, sp.Expr)
        or expression.has(sp.Float)
        or expression.is_real is not True
        or expression.is_algebraic is not True
        or expression.is_finite is not True
    ):
        raise ValueError("coordinates require exact real algebraic numbers")
    return expression


def _matrix(value: sp.MatrixBase) -> sp.ImmutableMatrix:
    if not isinstance(value, sp.MatrixBase):
        raise ValueError("an exact real algebraic matrix is required")
    return sp.ImmutableMatrix(value.applyfunc(_real))


def _equal(first: sp.MatrixBase, second: sp.MatrixBase) -> bool:
    return first.shape == second.shape and (first - second).to_DM(extension=True).is_zero_matrix


def _zero(value: sp.Expr) -> bool:
    return _equal(sp.Matrix([value]), sp.zeros(1, 1))


@dataclass(frozen=True)
class CirclePencil:
    fixed: sp.ImmutableMatrix
    first: sp.ImmutableMatrix
    second: sp.ImmutableMatrix


def verify_circle_pencil(pencil: CirclePencil) -> bool:
    """Verify an orthogonal fixed plane and two equal-width orthonormal frames."""
    try:
        if not isinstance(pencil, CirclePencil):
            return False
        fixed, first, second = (_matrix(value) for value in (pencil.fixed, pencil.first, pencil.second))
        dimension = fixed.rows
        width = first.cols
        return (
            dimension > 0
            and fixed.shape == (dimension, dimension)
            and width > 0
            and first.rows == dimension
            and second.shape == first.shape
            and _equal(fixed, fixed.T)
            and _equal(fixed * fixed, fixed)
            and _equal(first.T * first, sp.eye(width))
            and _equal(second.T * second, sp.eye(width))
            and _equal(first.T * second, sp.zeros(width))
            and _equal(fixed * first, sp.zeros(dimension, width))
            and _equal(fixed * second, sp.zeros(dimension, width))
        )
    except ValueError, TypeError, AttributeError, sp.polys.polyerrors.BasePolynomialError:
        return False


def certify_circle_pencil(fixed: sp.MatrixBase, first: sp.MatrixBase, second: sp.MatrixBase) -> CirclePencil:
    pencil = CirclePencil(_matrix(fixed), _matrix(first), _matrix(second))
    if not verify_circle_pencil(pencil):
        raise ValueError("circle pencil requires orthogonal projector/frame identities")
    return pencil


def _pencil(pencil: CirclePencil) -> None:
    if not verify_circle_pencil(pencil):
        raise ValueError("an intact circle-pencil certificate is required")


def _point(cosine: object, sine: object) -> tuple[sp.Expr, sp.Expr]:
    first, second = _real(cosine), _real(sine)
    if not _zero(first**2 + second**2 - 1):
        raise ValueError("circle coordinates must satisfy a**2+b**2=1")
    return first, second


def _plane(pencil: CirclePencil, cosine: sp.Expr, sine: sp.Expr) -> sp.ImmutableMatrix:
    first, second = pencil.first, pencil.second
    return sp.ImmutableMatrix(
        pencil.fixed
        + (
            (1 + cosine) * first * first.T
            + (1 - cosine) * second * second.T
            + sine * (first * second.T + second * first.T)
        )
        / 2
    )


def circle_plane(pencil: CirclePencil, cosine: object, sine: object) -> sp.ImmutableMatrix:
    """Return every limiting plane projector on the exact real circle."""
    _pencil(pencil)
    return _plane(pencil, *_point(cosine, sine))


def _angles(pencil: CirclePencil, projector: sp.MatrixBase) -> tuple[sp.Expr, sp.Expr]:
    width = pencil.first.cols
    first, second = pencil.first, pencil.second
    cosine = (sp.trace(first.T * projector * first) - sp.trace(second.T * projector * second)) / width
    sine = 2 * sp.trace(first.T * projector * second) / width
    return sp.cancel(cosine), sp.cancel(sine)


def recover_circle_point(pencil: CirclePencil, projector: sp.MatrixBase) -> tuple[sp.Expr, sp.Expr] | None:
    """Admit a plane exactly when its reconstructed circle projector agrees.

    Endpoint kernel containment alone admits many extra planes. The two trace
    coordinates and the full matrix identity decide the actual circle image.
    Malformed or approximate entries raise ValueError; exact nonmembers return
    None.
    """
    _pencil(pencil)
    candidate = _matrix(projector)
    if candidate.shape != pencil.fixed.shape:
        raise ValueError("candidate projector has the wrong shape")
    cosine, sine = _angles(pencil, candidate)
    if not _zero(cosine**2 + sine**2 - 1) or not _equal(candidate, _plane(pencil, cosine, sine)):
        return None
    return cosine, sine


@lru_cache(maxsize=1)
def cone_pencil() -> CirclePencil:
    _, first, second, fixed = cone._endpoint_frames()
    return certify_circle_pencil(fixed, first / 2, second / 2)


def double_pencil(pencil: CirclePencil) -> CirclePencil:
    """Transport a pure CD family's pencil through ordinary doubling.

    The matrix construction also preserves the pencil identities abstractly;
    its Cayley-Dickson interpretation uses the pure-multiplier hypothesis.
    """
    _pencil(pencil)
    dimension = pencil.fixed.rows
    conjugation = sp.diag(1, *([-1] * (dimension - 1)))
    return certify_circle_pencil(
        sp.diag(pencil.fixed, conjugation * pencil.fixed * conjugation),
        sp.diag(pencil.first, conjugation * pencil.first),
        sp.diag(pencil.second, conjugation * pencil.second),
    )


@lru_cache(maxsize=1)
def _circle_relation() -> Any:
    return sp.groebner([COSINE**2 + SINE**2 - 1], SINE, COSINE, AMPLITUDE, domain=sp.QQ)


def _reduce(value: sp.Expr) -> sp.Expr:
    numerator, denominator = sp.fraction(sp.cancel(value))
    numerator = _circle_relation().reduce(sp.expand(numerator))[1]
    denominator = _circle_relation().reduce(sp.expand(denominator))[1]
    if denominator == 0:
        raise ValueError("circle reduction loses its rational domain")
    return sp.cancel(numerator / denominator)


@lru_cache(maxsize=1)
def _global_graph_data() -> tuple[sp.ImmutableMatrix, sp.ImmutableMatrix, sp.ImmutableMatrix]:
    coordinates = cone._symbolic_coordinates(AMPLITUDE * COSINE, AMPLITUDE * SINE, AMPLITUDE)
    internal = sp.Matrix.hstack(
        *[
            cone._lift(
                representative, cone._local_internal_frame(cone._block(representative, coordinates)).applyfunc(_reduce)
            )
            for representative in cone.INTERNAL_REPRESENTATIVES
        ]
    )
    gram = (internal.T * internal).applyfunc(_reduce)
    internal_projector = (internal * gram.inv(method="DM") * internal.T).applyfunc(_reduce)
    external = cone._global_external_frame(COSINE, SINE)
    frame = internal.row_join(external)
    pencil = cone_pencil()
    projector = internal_projector + _plane(pencil, COSINE, SINE) - pencil.fixed
    return sp.ImmutableMatrix(frame), sp.ImmutableMatrix(projector), sp.ImmutableMatrix(gram)


def cone_graph_frame(amplitude: object, cosine: object, sine: object) -> sp.ImmutableMatrix:
    """Full graph-plane frame, including every reachable vertex plane."""
    scale = _real(amplitude)
    first, second = _point(cosine, sine)
    frame = _global_graph_data()[0]
    return _matrix(frame.subs({AMPLITUDE: scale, COSINE: first, SINE: second}).applyfunc(sp.cancel))


def cone_graph_projector(amplitude: object, cosine: object, sine: object) -> sp.ImmutableMatrix:
    scale = _real(amplitude)
    first, second = _point(cosine, sine)
    projector = _global_graph_data()[1]
    return _matrix(projector.subs({AMPLITUDE: scale, COSINE: first, SINE: second}).applyfunc(sp.cancel))


def cone_graph_coordinates(coefficients: object, projector: sp.MatrixBase) -> tuple[sp.Expr, sp.Expr, sp.Expr] | None:
    """Decide the entire named slice's real rank-24 kernel-graph closure.

    The three coefficients are A,B,C. Arbitrary exact real algebraic values
    are executable; the polynomial inverse proof covers all real values.
    """
    if not isinstance(coefficients, (tuple, list)) or len(coefficients) != 3:
        raise ValueError("cone graph coordinates require three exact coefficients")
    first, second, amplitude = (_real(value) for value in coefficients)
    candidate = _matrix(projector)
    if candidate.shape != (32, 32):
        raise ValueError("the cone graph uses 32-by-32 real projectors")
    cosine, sine = _angles(cone_pencil(), candidate)
    if (
        not _zero(cosine**2 + sine**2 - 1)
        or not _zero(first - amplitude * cosine)
        or not _zero(second - amplitude * sine)
        or not _equal(candidate, cone_graph_projector(amplitude, cosine, sine))
    ):
        return None
    return amplitude, cosine, sine


def _record(matrix: sp.MatrixBase) -> dict[str, object]:
    return {
        "shape": list(matrix.shape),
        "nonzero_entries": [
            [row, column, str(matrix[row, column])]
            for row in range(matrix.rows)
            for column in range(matrix.cols)
            if matrix[row, column] != 0
        ],
    }


def symbolic_cone_certificate() -> dict[str, object]:
    """Prove polynomial identities modulo the circle with positive denominators."""
    frame, projector, gram = _global_graph_data()
    matrix = cone._operator(cone._symbolic_coordinates(AMPLITUDE * COSINE, AMPLITUDE * SINE, AMPLITUDE))
    checks = {
        "full_kernel_action": matrix * frame,
        "projector_action": matrix * projector,
        "projector_idempotence": projector * projector - projector,
        "projector_symmetry": projector - projector.T,
        "projector_trace": sp.Matrix([sp.trace(projector) - 8]),
        "internal_external_orthogonality": frame[:, :4].T * frame[:, 4:],
        "external_orthonormality": frame[:, 4:].T * frame[:, 4:] - sp.eye(4),
        "gram_determinant": sp.Matrix([gram.det() - 16 * (1 + AMPLITUDE**2) ** 2]),
    }
    for label, residual in checks.items():
        if residual.applyfunc(_reduce) != sp.zeros(*residual.shape):
            raise RuntimeError("real graph identity fails: " + label)
    denominator_factors: set[str] = set()
    positive_factor = sp.Poly(1 + AMPLITUDE**2, AMPLITUDE, domain=sp.QQ)
    for entry in (*frame, *projector):
        denominator = sp.Poly(sp.fraction(sp.cancel(entry))[1], AMPLITUDE, domain=sp.QQ)
        for factor, _ in denominator.factor_list()[1]:
            if factor.monic() != positive_factor:
                raise RuntimeError("global frame/projector has an uncertified denominator")
            denominator_factors.add(str(factor.monic().as_expr()))
    pencil = cone_pencil()
    cosine, sine = _angles(pencil, projector)
    if _reduce(cosine - COSINE) != 0 or _reduce(sine - SINE) != 0:
        raise RuntimeError("global graph trace inverse fails")
    if projector.subs(AMPLITUDE, 0) != _plane(pencil, COSINE, SINE):
        raise RuntimeError("global graph endpoint loses circle pencil")
    return {
        "base": "e1+e18+s*a*e3+s*b*e8+s*e27; a**2+b**2=1",
        "identities_verified": sorted(checks),
        "frame_denominator": "1+s**2 > 0",
        "frame_and_projector_denominator_factors": sorted(denominator_factors),
        "internal_gram_determinant": "16*(1+s**2)**2 > 0",
        "internal_frame_numerator": _record((frame[:, :4] * (1 + AMPLITUDE**2)).applyfunc(sp.cancel)),
        "trace_inverse": {"amplitude": "C", "a": "(tr(U.T*P*U)-tr(V.T*P*V))/4", "b": "tr(U.T*P*V)/2"},
        "real_graph_model": "R x S1; each punctured component closure is a half-cylinder",
        "vertex_plane_fiber": "S1, with unique recovered circle coordinates",
        "scope": "complete real graph closure on the named affine slice; ambient coverage remains open",
    }


def collapse_chain_certificate(fixed_dimension: int, rotating_dimension: int) -> dict[str, Any]:
    """Certify the evaluation map via a homotopy-pushout chain contraction.

    An even rotating width supplies a global complex structure and sphere
    frame. The geometric maps are the equatorial inclusion and projection
    from S1 x S^(c-1) to S1 x S^(c+p-1) and S^(c-1).
    """
    if (
        type(fixed_dimension) is not int
        or fixed_dimension < 2
        or type(rotating_dimension) is not int
        or rotating_dimension < 2
        or rotating_dimension % 2
    ):
        raise ValueError("collapse model requires fixed dimension >=2 and positive even rotating dimension")
    fixed_sphere = fixed_dimension - 1
    fiber_sphere = fixed_dimension + rotating_dimension - 1
    cells = {
        "e0": 0,
        "e_circle": 1,
        "e_sphere": fiber_sphere,
        "e_product": fiber_sphere + 1,
        "b0": 0,
        "b_sphere": fixed_sphere,
        "a0": 1,
        "a_circle": 2,
        "a_sphere": fixed_sphere + 1,
        "a_product": fixed_sphere + 2,
    }
    reduced = {name: cells[name] for name in ("e0", "e_sphere", "e_product", "a_product")}
    source = {name: cells[name] for name in ("e0", "e_circle", "e_sphere", "e_product")}
    degrees = sorted(set(cells.values()) | {degree + 1 for degree in cells.values()})
    bases = {degree: [name for name, value in cells.items() if value == degree] for degree in degrees}
    reduced_bases = {degree: [name for name, value in reduced.items() if value == degree] for degree in degrees}
    source_bases = {degree: [name for name, value in source.items() if value == degree] for degree in degrees}
    boundaries = {degree: sp.zeros(len(bases.get(degree - 1, [])), len(bases[degree])) for degree in degrees}
    for domain, codomain, coefficient in (
        ("a0", "e0", 1),
        ("a0", "b0", -1),
        ("a_circle", "e_circle", 1),
        ("a_sphere", "b_sphere", -1),
    ):
        degree = cells[domain]
        boundaries[degree][bases[degree - 1].index(codomain), bases[degree].index(domain)] = coefficient
    projections = {degree: sp.zeros(len(reduced_bases[degree]), len(bases[degree])) for degree in degrees}
    inclusions = {degree: sp.zeros(len(bases[degree]), len(reduced_bases[degree])) for degree in degrees}
    homotopies = {degree: sp.zeros(len(bases.get(degree + 1, [])), len(bases[degree])) for degree in degrees}
    evaluation = {degree: sp.zeros(len(bases[degree]), len(source_bases[degree])) for degree in degrees}
    for name, degree in cells.items():
        if name in reduced:
            row, column = reduced_bases[degree].index(name), bases[degree].index(name)
            projections[degree][row, column] = inclusions[degree][column, row] = 1
        if name in source:
            evaluation[degree][bases[degree].index(name), source_bases[degree].index(name)] = 1
    projections[0][reduced_bases[0].index("e0"), bases[0].index("b0")] = 1
    for domain, codomain, coefficient in (("b0", "a0", -1), ("e_circle", "a_circle", 1), ("b_sphere", "a_sphere", -1)):
        degree = cells[domain]
        homotopies[degree][bases[degree + 1].index(codomain), bases[degree].index(domain)] = coefficient
    for degree in degrees:
        boundary = boundaries[degree]
        previous_homotopy = homotopies.get(degree - 1, sp.zeros(len(bases[degree]), len(bases.get(degree - 1, []))))
        next_boundary = boundaries.get(degree + 1, sp.zeros(len(bases[degree]), len(bases.get(degree + 1, []))))
        if (
            next_boundary * homotopies[degree] + previous_homotopy * boundary
            != sp.eye(len(bases[degree])) - inclusions[degree] * projections[degree]
        ):
            raise RuntimeError("integral collapse homotopy fails")
        if projections[degree] * inclusions[degree] != sp.eye(len(reduced_bases[degree])):
            raise RuntimeError("collapse inverse chain maps fail")
        if boundary * inclusions[degree] != sp.zeros(boundary.rows, len(reduced_bases[degree])):
            raise RuntimeError("reduced generators fail to be cycles")
        if degree > 0 and projections.get(degree - 1, sp.zeros(0, boundary.rows)) * boundary != sp.zeros(
            len(reduced_bases.get(degree - 1, [])), boundary.cols
        ):
            raise RuntimeError("collapse projection fails to be a chain map")
        if boundary * evaluation[degree] != sp.zeros(boundary.rows, len(source_bases[degree])):
            raise RuntimeError("evaluation inclusion fails to be a chain map")
    ranks = {degree: len(basis) for degree, basis in bases.items() if basis}
    homology = integral_homology(ranks, boundaries)
    return {
        "fixed_dimension": fixed_dimension,
        "rotating_dimension": rotating_dimension,
        "chain_contraction_verified": True,
        "evaluation_map_verified": True,
        "source_model": f"S1 x S{fiber_sphere}",
        "target_model": f"S{fixed_sphere} * (S1 x S{rotating_dimension - 1})",
        "homology": [
            {"degree": row["degree"], "free_rank": row["free_rank"], "torsion": row["torsion_invariant_factors"]}
            for row in homology["homology"]
        ],
        "chains": [
            {
                "degree": degree,
                "basis": bases[degree],
                "boundary": matrix_record(boundaries[degree]),
                "projection": matrix_record(projections[degree]),
                "inclusion": matrix_record(inclusions[degree]),
                "homotopy": matrix_record(homotopies[degree]),
                "reduced_basis": reduced_bases[degree],
                "source_basis": source_bases[degree],
                "induced_evaluation": matrix_record(projections[degree] * evaluation[degree]),
            }
            for degree in degrees
            if bases[degree]
        ],
        "source_cohomology_products": {
            "generator_degrees": [1, fiber_sphere, fiber_sphere + 1],
            "u_times_v": "w",
            "v_times_u_sign": (-1) ** fiber_sphere,
            "u_squared": 0,
            "v_squared": 0,
        },
        "target_positive_cup_products": "zero by the suspension cone-cover argument",
        "evaluation_pullback": {"suspended_product_class": "0", "fiber_sphere_class": "v", "top_class": "w=u*v"},
    }
