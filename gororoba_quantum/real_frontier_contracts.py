"""Real circle-graph inverses, unreachable planes and integral map controls."""

from __future__ import annotations

import json
from fractions import Fraction
from typing import Any

import sympy as sp

import circle_kernel_attachments as cone
from complex_skew import kernel_to_real
from projective_kernel_limits import cd_skew_path, certify_projective_limit
from real_frontier_graphs import (
    CirclePencil,
    certify_circle_pencil,
    circle_plane,
    collapse_chain_certificate,
    cone_graph_coordinates,
    cone_graph_frame,
    cone_graph_projector,
    cone_pencil,
    double_pencil,
    recover_circle_point,
    symbolic_cone_certificate,
    verify_circle_pencil,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def equal(first: sp.MatrixBase, second: sp.MatrixBase) -> bool:
    return first.shape == second.shape and (first - second).to_DM(extension=True).is_zero_matrix


def projector(frame: sp.MatrixBase) -> sp.Matrix:
    return (frame * (frame.T * frame).inv() * frame.T).applyfunc(sp.cancel)


def audit() -> dict[str, Any]:
    fixed = sp.diag(1, 1, 0, 0, 0, 0)
    first, second = sp.eye(6)[:, 2:4], sp.eye(6)[:, 4:6]
    pencil = certify_circle_pencil(fixed, first, second)
    require(verify_circle_pencil(pencil), "canonical pencil fails")
    points = ((1, 0), (-1, 0), (0, 1), (0, -1), (Fraction(3, 5), Fraction(4, 5)), (sp.sqrt(2) / 2, sp.sqrt(2) / 2))
    for cosine, sine in points:
        plane = circle_plane(pencil, cosine, sine)
        recovered = recover_circle_point(pencil, plane)
        require(recovered is not None, "reachable plane loses inverse")
        require(equal(sp.Matrix(recovered), sp.Matrix([cosine, sine])), "circle inverse differs")
        require(equal(plane * plane, plane) and sp.trace(plane) == 4, "circle plane rank differs")
    damaged = (
        CirclePencil(sp.ImmutableMatrix(2 * fixed), sp.ImmutableMatrix(first), sp.ImmutableMatrix(second)),
        CirclePencil(sp.ImmutableMatrix(fixed), sp.ImmutableMatrix(first), sp.ImmutableMatrix(first)),
        CirclePencil(sp.ImmutableMatrix(fixed), sp.ImmutableMatrix(first * 2), sp.ImmutableMatrix(second)),
    )
    for value in damaged:
        require(not verify_circle_pencil(value), "damaged pencil accepted")
    invalid = (
        lambda: circle_plane(pencil, 0, 0),
        lambda: circle_plane(pencil, sp.Float(1), 0),
        lambda: circle_plane(pencil, sp.I, 0),
        lambda: circle_plane(pencil, sp.Symbol("a", real=True), 0),
        lambda: circle_plane(pencil, True, 0),
        lambda: certify_circle_pencil(sp.zeros(2, 3), first, second),
        lambda: cone_graph_frame(0, 0, 0),
        lambda: cone_graph_coordinates((0, 0), sp.eye(32)),
    )
    for operation in invalid:
        try:
            operation()
        except ValueError:
            continue
        raise RuntimeError("invalid real graph input accepted")
    production = cone_pencil()
    rational_points = ((1, 0, 1), (-1, 0, 1), (3, 4, 5), (3, 4, -5), (0, -1, 1))
    records = []
    for coefficients in rational_points:
        amplitude = coefficients[2]
        cosine, sine = Fraction(coefficients[0], amplitude), Fraction(coefficients[1], amplitude)
        actual = cone_graph_projector(amplitude, cosine, sine)
        baseline = projector(cone.cone_kernel_frame(coefficients))
        require(equal(actual, baseline), "global graph differs from two-chart method")
        graph_recovered = cone_graph_coordinates(coefficients, actual)
        require(
            graph_recovered is not None and equal(sp.Matrix(graph_recovered), sp.Matrix([amplitude, cosine, sine])),
            "graph inverse fails",
        )
        records.append({"coefficients": list(coefficients), "independent_projector_equal": True})
    parameter = sp.Symbol("t", real=True)
    for cosine, sine in ((1, 0), (0, 1), (-1, 0)):
        coordinates = [sp.Integer(0)] * 32
        coordinates[1] = coordinates[18] = sp.Integer(1)
        coordinates[3], coordinates[8], coordinates[27] = parameter * cosine, parameter * sine, parameter
        limit = certify_projective_limit(cd_skew_path(coordinates, parameter), parameter)
        require(
            equal(projector(kernel_to_real(limit.limit_frame)), circle_plane(production, cosine, sine)),
            "projective path limit differs",
        )
    algebraic = cone_graph_projector(sp.sqrt(3), sp.sqrt(2) / 2, sp.sqrt(2) / 2)
    graph_recovered = cone_graph_coordinates((sp.sqrt(6) / 2, sp.sqrt(6) / 2, sp.sqrt(3)), algebraic)
    require(graph_recovered is not None, "algebraic real point loses graph admission")
    unreachable = (
        production.fixed
        + production.first[:, :2] * production.first[:, :2].T
        + production.second[:, 2:] * production.second[:, 2:].T
    )
    center = cone._operator(cone._symbolic_coordinates(0, 0, 0))
    require(
        equal(unreachable * unreachable, unreachable) and sp.trace(unreachable) == 8,
        "unreachable fixture loses plane rank",
    )
    require(equal(center * unreachable, sp.zeros(32)), "unreachable fixture leaves endpoint kernel")
    require(recover_circle_point(production, unreachable) is None, "unreachable endpoint plane admitted")
    require(cone_graph_coordinates((0, 0, 0), unreachable) is None, "unreachable graph vertex admitted")
    require(cone_graph_coordinates((1, 0, 0), circle_plane(production, 1, 0)) is None, "off-cone base admitted")
    require(
        cone_graph_coordinates((1, 0, 1), circle_plane(production, 1, 0)) is None,
        "endpoint plane mistaken for finite-amplitude graph",
    )
    stages = []
    for stage in (5, 6, 7, 8):
        point = circle_plane(production, sp.Rational(3, 5), sp.Rational(4, 5))
        require(
            recover_circle_point(production, point) == (sp.Rational(3, 5), sp.Rational(4, 5)),
            "doubled circle inverse differs",
        )
        stages.append(
            {
                "stage": stage,
                "plane_rank": int(sp.trace(point)),
                "endpoint_rank": int(sp.trace(production.fixed)) + 2 * production.first.cols,
            }
        )
        if stage < 8:
            production = double_pencil(production)
    chains = [
        collapse_chain_certificate(fixed_dimension, rotating_dimension)
        for fixed_dimension, rotating_dimension in ((4, 4), (8, 8), (2, 2), (3, 4))
    ]
    for result in chains:
        require(result["chain_contraction_verified"], "collapse contraction fails")
        require(result["evaluation_map_verified"], "evaluation chain map fails")
        expected = {0: 1}
        for degree in (
            result["fixed_dimension"] + 1,
            result["fixed_dimension"] + result["rotating_dimension"] - 1,
            result["fixed_dimension"] + result["rotating_dimension"],
        ):
            expected[degree] = expected.get(degree, 0) + 1
        actual = {row["degree"]: row["free_rank"] for row in result["homology"] if row["free_rank"]}
        require(actual == expected, "collapse homology differs from the geometric suspension")
        require(all(not row["torsion"] for row in result["homology"]), "collapse introduces torsion")
    return {
        "schema": "real-frontier-graphs-v1",
        "symbolic": symbolic_cone_certificate(),
        "rational_graph_points": records,
        "algebraic_graph_point": True,
        "unreachable_endpoint_plane_rejected": True,
        "rejected_pencils": len(damaged),
        "rejected_inputs": len(invalid),
        "ordinary_embedding_controls": stages,
        "collapse_chain_models": chains,
        "physical_qpu_jobs": 0,
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, sort_keys=True))
