"""Certify topology of the unit pair space over an exact rank-changing path.

The base path is a proper subspace of the full dimension-32 unit zero-divisor
locus. Exact rank and common-kernel certificates identify its incidence space
with a double mapping cylinder. Explicit endpoint nullhomotopies identify a
wedge of spheres, which determines integral homology and the cohomology ring.
The ordinary Cayley-Dickson embedding supplies an all-dimensional induction
for this restricted family; it does not classify the full pair varieties.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Sequence
from typing import Any

import sympy as sp

import parallel
from cd_core import cd_sign
from integral_homology import integral_homology, matrix_record
from rank_attachments import (
    audit_rank_attachments,
    common_kernel_basis,
    endpoint_kernel_basis,
    path_coefficients,
    path_matrix,
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sphere_tree_model(vertex_dimensions: Sequence[int], edges: Sequence[tuple[int, int, int]]) -> dict[str, Any]:
    """Compute invariants of a tree of sphere mapping cylinders with null maps.

    Each edge (source,target,dimension) carries a sphere S^dimension. Strict
    dimension inequalities make both endpoint maps nullhomotopic. The input
    graph is a tree, so collapsing its basepoint intervals gives one wedge.
    A separate geometric certificate identifies a concrete space with this
    mapping-cylinder construction.
    """
    _require(bool(vertex_dimensions), "the sphere tree requires a vertex")
    _require(
        all(type(dimension) is int and dimension >= 2 for dimension in vertex_dimensions), "vertex sphere dimensions"
    )
    parents = list(range(len(vertex_dimensions)))
    adjacency = set()
    incidence = sp.zeros(len(vertex_dimensions), len(edges))
    chain_ranks: Counter[int] = Counter({0: len(vertex_dimensions), 1: len(edges)})
    summands = [{"name": f"vertex_{index}", "degree": dimension} for index, dimension in enumerate(vertex_dimensions)]
    for edge_index, (source, target, dimension) in enumerate(edges):
        _require(type(source) is int and type(target) is int, "edge vertices require integers")
        _require(0 <= source < len(parents) and 0 <= target < len(parents) and source != target, "edge vertex range")
        _require(type(dimension) is int and dimension >= 1, "edge sphere dimension")
        _require(
            dimension < min(vertex_dimensions[source], vertex_dimensions[target]),
            "endpoint maps lack dimension contraction",
        )
        pair = tuple(sorted((source, target)))
        _require(pair not in adjacency, "duplicate sphere-tree edge")
        adjacency.add(pair)
        source_root, target_root = source, target
        while parents[source_root] != source_root:
            source_root = parents[source_root]
        while parents[target_root] != target_root:
            target_root = parents[target_root]
        _require(source_root != target_root, "sphere graph contains a cycle")
        parents[target_root] = source_root
        incidence[source, edge_index] = -1
        incidence[target, edge_index] = 1
        chain_ranks[dimension + 1] += 1
        summands.append({"name": f"edge_{edge_index}_suspension", "degree": dimension + 1})
    _require(len(edges) == len(vertex_dimensions) - 1, "sphere graph is disconnected")
    chain_ranks.update(vertex_dimensions)
    homology = integral_homology(dict(chain_ranks), {1: incidence})
    predicted_ranks = Counter(summand["degree"] for summand in summands)
    predicted_ranks[0] = 1
    for group in homology["homology"]:
        _require(
            group["free_rank"] == predicted_ranks[group["degree"]], "chain homology disagrees with wedge reduction"
        )
        _require(not group["torsion_invariant_factors"], "tree-of-spheres model has unexpected torsion")
    generators = [{"name": "unit", "degree": 0}, *summands]
    products = []
    for first in generators:
        for second in generators:
            value = second["name"] if first["degree"] == 0 else first["name"] if second["degree"] == 0 else None
            products.append({"left": first["name"], "right": second["name"], "result": value, "zero": value is None})
    return {
        "identification": "homotopy equivalence to the listed wedge; no homeomorphism to the wedge is claimed",
        "vertex_sphere_dimensions": list(vertex_dimensions),
        "edge_spheres": [
            {"source": source, "target": target, "dimension": dimension} for source, target, dimension in edges
        ],
        "wedge_summands": summands,
        "chain_ranks": [{"degree": degree, "rank": rank} for degree, rank in sorted(chain_ranks.items())],
        "integral_homology": homology,
        "euler_characteristic": sum((-1) ** (degree % 2) * rank for degree, rank in chain_ranks.items()),
        "cohomology_ring": {
            "coefficient_ring": "Z",
            "justification": (
                "Geometric nullhomotopies and tree collapse give a wedge; chain ranks alone do not determine products."
            ),
            "generators": generators,
            "products": products,
        },
    }


def _endpoint_pole(endpoint: int, common: sp.MatrixBase) -> dict[str, object]:
    """Certify an exact rational direction for contraction of the common sphere."""
    kernel = endpoint_kernel_basis(endpoint)
    gram = common.T * common
    common_projector = common * gram.inv() * common.T
    pole = None
    for column in kernel.columnspace():
        candidate = sp.simplify(column - common_projector * column)
        if candidate != sp.zeros(common.rows, 1):
            pole = candidate
            break
    _require(pole is not None, "endpoint kernel has no direction outside the common kernel")
    assert pole is not None
    squared_norm = (pole.T * pole)[0]
    _require(squared_norm > 0, "contraction pole must be nonzero")
    _require(common.T * pole == sp.zeros(common.cols, 1), "contraction pole is not orthogonal")
    _require(
        path_matrix(sp.Integer(endpoint)) * pole == sp.zeros(common.rows, 1), "contraction pole escapes endpoint kernel"
    )
    parameter = sp.Symbol("s", real=True)
    denominator_squared = (1 - parameter) ** 2 + parameter**2
    _require(
        sp.expand(denominator_squared - (2 * (parameter - sp.Rational(1, 2)) ** 2 + sp.Rational(1, 2))) == 0,
        "nullhomotopy normalization",
    )
    return {
        "endpoint": endpoint,
        "kernel_dimension": kernel.cols,
        "rational_pole": [str(entry) for entry in pole],
        "pole_norm_squared": str(squared_norm),
        "unit_pole": "rational_pole/sqrt(pole_norm_squared)",
        "nullhomotopy": "H(u,s)=((1-s)*u+s*v)/sqrt((1-s)^2+s^2), 0<=s<=1, v the unit pole",
        "denominator_positive_certificate": "(1-s)^2+s^2=2*(s-1/2)^2+1/2",
        "exact_orthogonality_and_kernel_checked": True,
    }


def _endpoint_pole_task(endpoint: int) -> dict[str, object]:
    return _endpoint_pole(endpoint, common_kernel_basis())


def embedded_path_model(stage: int) -> dict[str, Any]:
    """Instantiate the proved zero-padding induction with sparse finite cells.

    The theorem applies to every integer stage >=5. The arithmetic interface
    bounds the stage index to 256, independently of the proof.
    """
    _require(type(stage) is int and 5 <= stage <= 256, "stage must be an integer from 5 through 256")
    common_dimension = 4 * 2 ** (stage - 5)
    special_dimensions = [factor * common_dimension for factor in (2, 3, 4)]
    model = sphere_tree_model(
        [dimension - 1 for dimension in special_dimensions],
        [(0, 1, common_dimension - 1), (1, 2, common_dimension - 1)],
    )
    return {
        "stage": stage,
        "algebra_dimension": 2**stage,
        "space": ("unit zero-product pairs over the zero-padded normalized certified path, t in [0,2]"),
        "full_pair_space_classified": False,
        "embedding": "a_(n+1)(t)=(a_n(t),0)",
        "induction_source": "Biss-Dugger-Isaksen math/0511691v1 Theorem 10.1, alpha=1,beta=0",
        "induction_hypothesis": (
            "a_n(t) perpendicular to C_n; real and distinguished-unit coefficients vanish at every embedding"
        ),
        "kernel_induction": "Ann(a_(n+1)(t))=Ann(a_n(t)) x Ann(a_n(t))",
        "common_kernel_dimension": common_dimension,
        "endpoint_kernel_dimensions": special_dimensions,
        "topological_model": model,
    }


def _embedding_certificate() -> dict[str, object]:
    """Verify the first zero-padding step as a polynomial matrix identity."""
    parameter = sp.Symbol("t", real=True)
    coefficients = list(path_coefficients(parameter)) + [sp.Integer(0)] * 32
    embedded = sp.Matrix(
        64,
        64,
        lambda row, column: coefficients[row ^ column] * cd_sign(64, row ^ column, column),
    )
    original = path_matrix(parameter)
    conjugation = sp.diag(1, *([-1] * 31))
    right_action = -conjugation * original * conjugation
    _require(
        (embedded - sp.diag(original, right_action)).applyfunc(sp.expand) == sp.zeros(64),
        "zero-padding left/right matrix decomposition failed",
    )
    common = common_kernel_basis()
    doubled = sp.diag(common, common)
    _require((embedded * doubled).applyfunc(sp.expand) == sp.zeros(64, 8), "embedded common kernel fails")
    for endpoint in (0, 1, 2):
        kernel = endpoint_kernel_basis(endpoint)
        _require(kernel[0, :] == sp.zeros(1, kernel.cols), "endpoint annihilator must be imaginary")
        _require(
            embedded.subs(parameter, endpoint) * sp.diag(kernel, kernel) == sp.zeros(64, 2 * kernel.cols),
            "embedded endpoint kernel fails",
        )
    return {
        "algebra_dimension": 64,
        "parameter_domain": "all real t, via coefficientwise polynomial identities",
        "block_identity": "L_(a,0)=diag(L_a,R_a), R_a=-C L_a C for the pure path",
        "common_kernel_dimension": doubled.cols,
        "endpoint_kernel_dimensions": [2 * endpoint_kernel_basis(endpoint).cols for endpoint in (0, 1, 2)],
        "rank_equality_reason": "C is invertible; R_a and L_a have identical rank",
        "scope": "The first embedding is checked directly; Theorem 10.1 supplies the general induction.",
    }


def audit_rank_path_topology(stage: int = 5) -> dict[str, object]:
    path_audit = audit_rank_attachments()
    common = common_kernel_basis()
    _require(common.shape == (32, 4) and common.T * common == 4 * sp.eye(4), "common path frame changed")
    parameter = sp.Symbol("t", real=True)
    coefficients = path_coefficients(parameter)
    _require(coefficients[1] == 1, "base-path normalization can vanish")
    _require(sp.expand(coefficients[18] - coefficients[25] - parameter) == 0, "normalized base path loses injectivity")
    _require(coefficients[0] == 0 and coefficients[16] == 0, "ordinary embedding theorem requires C_n perpendicularity")
    model = embedded_path_model(stage)
    poles = parallel.ordered_map(_endpoint_pole_task, (0, 1, 2), min_items=2)
    _require([pole["kernel_dimension"] for pole in poles] == [8, 12, 16], "endpoint dimensions change")
    rejected = 0
    for vertices, edges in (([7, 11], []), ([7, 11], [(0, 1, 7)]), ([7, 11, 15], [(0, 1, 3), (1, 2, 3), (2, 0, 3)])):
        try:
            sphere_tree_model(vertices, edges)
        except ValueError:
            rejected += 1
        else:
            raise RuntimeError("invalid sphere attachment model accepted")
    return {
        "schema": "cayley-dickson-restricted-rank-path-topology-v1",
        "qpu_executed": False,
        "sympy_version": sp.__version__,
        "rank_attachment_certificate": path_audit,
        "common_kernel_gram": matrix_record(common.T * common),
        "base_path_inverse": "t=(x18-x25)/x1; x=a(t)/||a(t)|| and x1>0",
        "quotient_homeomorphism": "constant S(W) x [0,2] glued to endpoint spheres S(K_0),S(K_1),S(K_2) along S(W)",
        "quotient_justification": (
            "continuous bijection from compact quotient to the Hausdorff restricted incidence space"
        ),
        "endpoint_nullhomotopies": poles,
        "homotopy_sources": "Hatcher Algebraic Topology, Propositions 0.17 and 0.18",
        "model": model,
        "first_embedding_certificate": _embedding_certificate(),
        "rejected_invalid_attachment_models": rejected,
        "full_pair_space_model": {
            "status": "unestablished",
            "missing": (
                "coverage and attachment certificates for arbitrary real first operands outside the certified path"
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage", type=int, default=5, help="zero-padded algebra stage, 5 through 256; proof covers every stage >=5"
    )
    arguments = parser.parse_args()
    print(json.dumps(audit_rank_path_topology(arguments.stage), indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
