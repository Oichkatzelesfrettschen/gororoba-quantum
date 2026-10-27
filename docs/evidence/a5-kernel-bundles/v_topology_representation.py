"""Exact topology and compact-stabilizer representations on the open piece ``V``.

The nonzero middle coordinate splits off the global phase.  After dividing by
that coordinate, the remaining family is an affine quadric over
``CP^1 minus {+i,-i}``; the square root of ``1+lambda^2`` has odd monodromy.
This replay computes the mapping-torus invariants and restricts the compact
stabilizers to the complex rank-six kernel on principal, endpoint, and ``VB``
boundary orbits.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Sequence
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import aligned_orbit_moduli as aligned  # noqa: E402
import aligned_stabilizer_representation as aligned_representation  # noqa: E402
import isotropic_orbit_data as isotropic  # noqa: E402
import kernel_symmetry as symmetry  # noqa: E402
import stabilizer_representation as stabilizer  # noqa: E402
import v_orbit_moduli as v_moduli  # noqa: E402

from cd_core import left_mult_matrix_exact  # noqa: E402

DIMENSION = 32
COMPACT_GENERATOR_COUNT = 15
V_MODULI_RESULT = HERE / "v-orbit-moduli-result.json"
V_MODULI_SCRIPT = HERE / "v_orbit_moduli.py"
ALIGNED_REPRESENTATION_RESULT = HERE / "aligned-stabilizer-result.json"
ALIGNED_REPRESENTATION_SCRIPT = HERE / "aligned_stabilizer_representation.py"
ISOTROPIC_RESULT = HERE / "isotropic-orbit-data-result.json"
ISOTROPIC_SCRIPT = HERE / "isotropic_orbit_data.py"

RationalMatrix = symmetry.RationalMatrix


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _abelian_group(free_rank: int, torsion_orders: Sequence[int] = ()) -> str:
    terms: list[str] = []
    if free_rank == 1:
        terms.append("Z")
    elif free_rank > 1:
        terms.append(f"Z^{free_rank}")
    terms.extend(f"Z/{order}" for order in torsion_orders)
    return " + ".join(terms) if terms else "0"


def _circle_mapping_torus_groups(monodromy_degree: int) -> dict[str, Any]:
    """Compute cohomology and K-groups from the two exact Wang maps."""
    top_wang_entry = 1 - monodromy_degree
    mapping_torus_k0: tuple[int, tuple[int, ...]]
    mapping_torus_k1: tuple[int, tuple[int, ...]]
    if top_wang_entry == 0:
        mapping_torus_cohomology = {"0": "Z", "1": "Z", "6": "Z", "7": "Z"}
        mapping_torus_k0 = (2, ())
        mapping_torus_k1 = (2, ())
    else:
        _require(abs(top_wang_entry) == 2, "unexpected antipodal Wang-map entry")
        mapping_torus_cohomology = {"0": "Z", "1": "Z", "7": f"Z/{abs(top_wang_entry)}"}
        mapping_torus_k0 = (1, ())
        mapping_torus_k1 = (1, (abs(top_wang_entry),))

    unit_k0 = (
        mapping_torus_k0[0] + mapping_torus_k1[0],
        (*mapping_torus_k0[1], *mapping_torus_k1[1]),
    )
    unit_k1 = unit_k0
    if monodromy_degree == -1:
        unit_cohomology = {
            "0": "Z",
            "1": "Z^2",
            "2": "Z",
            "7": "Z/2",
            "8": "Z/2",
        }
    else:
        unit_cohomology = {
            "0": "Z",
            "1": "Z^2",
            "2": "Z",
            "6": "Z",
            "7": "Z^2",
            "8": "Z",
        }
    return {
        "mapping_torus_cohomology": mapping_torus_cohomology,
        "mapping_torus_K0": _abelian_group(*mapping_torus_k0),
        "mapping_torus_K1": _abelian_group(*mapping_torus_k1),
        "unit_section_cohomology": unit_cohomology,
        "unit_section_K0": _abelian_group(*unit_k0),
        "unit_section_reduced_K0": _abelian_group(unit_k0[0] - 1, unit_k0[1]),
        "unit_section_K1": _abelian_group(*unit_k1),
    }


def _zero_order(polynomial: sp.Expr, variable: sp.Symbol, root: sp.Expr) -> int:
    derivative = sp.expand(polynomial)
    order = 0
    degree = int(sp.Poly(polynomial, variable).degree())
    while sp.simplify(derivative.subs(variable, root)) == 0:
        order += 1
        _require(order <= degree, "zero-order computation exceeded the polynomial degree")
        derivative = sp.diff(derivative, variable)
    return order


def _square_root_divisor(mutation: str) -> dict[str, Any]:
    projective_ratio = sp.Symbol("lambda")
    coefficient_quadratic = 1 + projective_ratio**2
    if mutation == "trivialize_monodromy":
        coefficient_quadratic = sp.expand(coefficient_quadratic**2)
    orders = {
        "+i": _zero_order(coefficient_quadratic, projective_ratio, sp.I),
        "-i": _zero_order(coefficient_quadratic, projective_ratio, -sp.I),
    }
    _require(len(set(orders.values())) == 1, "deleted points have different divisor orders")
    return {
        "coefficient_polynomial": sp.sstr(coefficient_quadratic),
        "factorization": sp.sstr(sp.factor(coefficient_quadratic, extension=sp.I)),
        "deleted_point_orders": orders,
        "common_order": next(iter(orders.values())),
        "mutation": mutation if mutation == "trivialize_monodromy" else "",
    }


def _topology_certificate(mutation: str = "") -> dict[str, Any]:
    if mutation not in ("", "trivialize_monodromy"):
        raise ValueError(f"unknown topology mutation {mutation!r}")
    divisor = _square_root_divisor(mutation)
    square_root_winding = int(divisor["common_order"])
    monodromy_sign = 1 if square_root_winding % 2 == 0 else -1
    sphere_dimension = 6
    monodromy_degree = monodromy_sign ** (sphere_dimension + 1)
    groups = _circle_mapping_torus_groups(monodromy_degree)
    expected_cohomology = {
        "0": "Z",
        "1": "Z^2",
        "2": "Z",
        "7": "Z/2",
        "8": "Z/2",
    }
    expected = {
        "mapping_torus_K0": "Z",
        "mapping_torus_K1": "Z + Z/2",
        "unit_section_K0": "Z^2 + Z/2",
        "unit_section_reduced_K0": "Z + Z/2",
        "unit_section_K1": "Z^2 + Z/2",
    }
    k_theory_pass = all(groups[key] == value for key, value in expected.items())
    topology_pass = (
        mutation == ""
        and square_root_winding == 1
        and monodromy_sign == -1
        and groups["unit_section_cohomology"] == expected_cohomology
        and k_theory_pass
    )
    return {
        "parameterization": "z=mu*(a,1,lambda*a), q(a)=-1/(1+lambda^2)",
        "global_phase_factor": "mu/abs(mu) in S^1",
        "base": "CP^1 minus {+i,-i}, homotopy equivalent to S^1",
        "square_root_cover": "b=sqrt(1+lambda^2)*a with q(b)=-1",
        "divisor_computation": divisor,
        "divisor_order_around_each_deleted_point": square_root_winding,
        "square_root_monodromy": monodromy_sign,
        "affine_quadric": "q(b)=-1 is diffeomorphic to T S^6 and retracts to S^6",
        "quadric_monodromy": "b -> -b",
        "monodromy_degree_on_H6": monodromy_degree,
        "homotopy_type": "S^1 x mapping_torus(-id:S^6->S^6)",
        "fundamental_group": "Z^2",
        "topology_argument_status": (
            "inferred from the exact divisor order, affine-quadric model, Wang sequence, and Kunneth theorem"
        ),
        **groups,
        "unit_section_cohomology_status": "inferred",
        "wang_map_on_H6": top_wang_entry if (top_wang_entry := 1 - monodromy_degree) else 0,
        "wang_map_on_reduced_K0_of_S6": top_wang_entry,
        "k_theory_pass": k_theory_pass,
        "pass": topology_pass,
    }


def _representation_signature(row: dict[str, Any]) -> tuple[Any, ...]:
    representation = row["representation"]
    return (
        row["stabilizer_lie_algebra"],
        row["complex_kernel_dimension"],
        representation["decomposition"],
        tuple(sorted(representation["casimir_spectrum"].items())),
    )


def _fixture_task(task: tuple[int, int, int, str, Fraction, Fraction, str]) -> dict[str, Any]:
    alpha, beta, split_mu, orbit_type, real_length, imaginary_length, mutation = task
    point_mu = 0 if orbit_type == "VB_boundary" else split_mu
    point = v_moduli._v_point(alpha, beta, point_mu, real_length, imaginary_length)
    invariants = v_moduli._extract_invariants(point)
    compact = stabilizer._compact_triples()
    tangent_rank, _base_stabilizers, coefficient_rows = aligned._stabilizer_data(point, "")
    coefficients = list(coefficient_rows)
    if mutation == "include_moving_direction":
        moving_index = next(
            index for index, (_name, triple) in enumerate(compact) if any(stabilizer._matrix_vector(triple[0], point))
        )
        coefficients[0] = tuple(Fraction(index == moving_index) for index in range(COMPACT_GENERATOR_COUNT))
    elif mutation not in ("", "perturb_fiber_action"):
        raise ValueError(f"unknown representation mutation {mutation!r}")

    base_generators = [triple[0] for _name, triple in compact]
    domain_generators = [triple[1] for _name, triple in compact]
    stabilizer_bases = [stabilizer._linear_combination(row, base_generators) for row in coefficients]
    stabilizer_domains = [stabilizer._linear_combination(row, domain_generators) for row in coefficients]
    point_fixed = [not any(stabilizer._matrix_vector(matrix, point)) for matrix in stabilizer_bases]
    if mutation == "include_moving_direction":
        return {
            "orbit_type": orbit_type,
            "mutation": mutation,
            "point_fixed": point_fixed,
            "pass": all(point_fixed),
        }

    left_matrix = tuple(tuple(row) for row in left_mult_matrix_exact(DIMENSION, tuple(point)))
    complex_structure = aligned_representation._complex_structure()
    adapted_basis = aligned_representation._adapted_kernel_basis(left_matrix, complex_structure, 12)
    kernel_preserved = [
        all(
            not any(stabilizer._matrix_vector(left_matrix, stabilizer._matrix_vector(domain, vector)))
            for vector in adapted_basis
        )
        for domain in stabilizer_domains
    ]
    fiber_matrices = [
        aligned_representation._fiber_matrix(domain, adapted_basis, complex_structure) for domain in stabilizer_domains
    ]
    if mutation == "perturb_fiber_action":
        fiber_matrices[0] = fiber_matrices[0].copy()
        fiber_matrices[0][0, 1] += 1
    commutators_match = aligned_representation._representation_commutators_match(
        stabilizer_domains,
        fiber_matrices,
        adapted_basis,
        complex_structure,
    )
    if mutation == "perturb_fiber_action":
        return {
            "orbit_type": orbit_type,
            "mutation": mutation,
            "point_fixed": point_fixed,
            "kernel_preserved": kernel_preserved,
            "representation_commutators_match": commutators_match,
            "pass": commutators_match,
        }

    derived_domains = aligned_representation._derived_basis(stabilizer_domains)
    casimir, killing = aligned_representation._casimir(derived_domains, adapted_basis, complex_structure)
    derived_representation = [
        aligned_representation._fiber_matrix(domain, adapted_basis, complex_structure) for domain in derived_domains
    ]
    if orbit_type == "collinear_endpoint":
        representation = aligned_representation._endpoint_certificate(derived_representation, casimir)
        expected_tangent_rank = 7
        expected_stabilizer_dimension = 8
        expected_derived_dimension = 8
        stabilizer_label = "su(3)"
    elif orbit_type == "principal":
        representation = aligned_representation._su2_certificate(casimir, 2)
        expected_tangent_rank = 12
        expected_stabilizer_dimension = 3
        expected_derived_dimension = 3
        stabilizer_label = "su(2)"
    elif orbit_type == "VB_boundary":
        boundary = isotropic._representation_check(point, "VB")
        representation = boundary["representation"]
        expected_tangent_rank = 11
        expected_stabilizer_dimension = 4
        expected_derived_dimension = 3
        stabilizer_label = "su(2)+u(1)"
    else:
        raise ValueError(f"unknown orbit type {orbit_type!r}")

    compact_semisimple = aligned._negative_definite(killing)
    expected_membership = orbit_type != "VB_boundary"
    row_pass = (
        tangent_rank == expected_tangent_rank
        and len(coefficients) == expected_stabilizer_dimension
        and len(derived_domains) == expected_derived_dimension
        and compact_semisimple
        and invariants["inside_open_V"] is expected_membership
        and all(point_fixed)
        and all(kernel_preserved)
        and commutators_match
        and representation["pass"]
    )
    return {
        "orbit_type": orbit_type,
        "mutation": mutation,
        "split_projective_coefficients": [alpha, beta],
        "split_projective_ratio_beta_over_alpha": invariants["split_projective_ratio_beta_over_alpha"],
        "rho_squared": invariants["rho_squared"],
        "compact_tangent_rank": tangent_rank,
        "stabilizer_dimension": len(coefficients),
        "stabilizer_derived_dimension": len(derived_domains),
        "stabilizer_lie_algebra": stabilizer_label,
        "derived_killing_negative_definite": compact_semisimple,
        "real_kernel_dimension": len(adapted_basis),
        "complex_kernel_dimension": len(adapted_basis) // 2,
        "point_fixed": point_fixed,
        "kernel_preserved": kernel_preserved,
        "representation_commutators_match": commutators_match,
        "representation": representation,
        "pass": row_pass,
    }


def _load_inputs() -> tuple[dict[str, str], dict[str, Any]]:
    bindings = (
        ("v_orbit_moduli", V_MODULI_RESULT, V_MODULI_SCRIPT, "a5-v-compact-orbit-moduli-v1"),
        (
            "aligned_stabilizer_representation",
            ALIGNED_REPRESENTATION_RESULT,
            ALIGNED_REPRESENTATION_SCRIPT,
            "a5-aligned-nullity-twelve-stabilizer-representation-v1",
        ),
        (
            "isotropic_orbit_data",
            ISOTROPIC_RESULT,
            ISOTROPIC_SCRIPT,
            "a5-isotropic-orbit-data-v1",
        ),
    )
    digests: dict[str, str] = {}
    loaded: dict[str, Any] = {}
    for label, result_path, script_path, schema in bindings:
        result = json.loads(result_path.read_text(encoding="utf-8"))
        script_digest = hashlib.sha256(script_path.read_bytes()).hexdigest()
        _require(result.get("schema") == schema, f"{result_path.name} has an unexpected schema")
        _require(result.get("pass") is True, f"{result_path.name} does not pass")
        _require(result.get("script_sha256") == script_digest, f"{result_path.name} is stale against its producer")
        digests[f"{label}_result_sha256"] = hashlib.sha256(result_path.read_bytes()).hexdigest()
        digests[f"{label}_script_sha256"] = script_digest
        loaded[label] = result
    return digests, loaded


def topology_representation_checks(mutation: str = "") -> dict[str, Any]:
    if mutation not in ("", "trivialize_monodromy", "include_moving_direction", "perturb_fiber_action"):
        raise ValueError(f"unknown mutation {mutation!r}")
    input_digests, inputs = _load_inputs()
    if mutation == "trivialize_monodromy":
        topology = _topology_certificate(mutation)
        return {
            "mutation": mutation,
            "input_digests": input_digests,
            "topology": topology,
            "rows": [],
            "pass": topology["pass"],
        }
    if mutation:
        rows = [_fixture_task((3, 5, 4, "principal", Fraction(3, 4), Fraction(5, 4), mutation))]
        return {
            "mutation": mutation,
            "input_digests": input_digests,
            "topology": _topology_certificate(),
            "rows": rows,
            "pass": all(row["pass"] for row in rows),
        }

    coefficient_fixtures = ((3, 5, 4), (5, 13, 12), (0, 1, 1))
    gram_fixtures = (
        ("collinear_endpoint", Fraction(0), Fraction(1)),
        ("principal", Fraction(3, 4), Fraction(5, 4)),
        ("principal", Fraction(4, 3), Fraction(5, 3)),
        ("VB_boundary", Fraction(1), Fraction(1)),
    )
    tasks = [
        (alpha, beta, split_mu, orbit_type, real_length, imaginary_length, "")
        for alpha, beta, split_mu in coefficient_fixtures
        for orbit_type, real_length, imaginary_length in gram_fixtures
    ]
    rows = symmetry.parallel.ordered_map(_fixture_task, tasks, min_items=1)
    principal_rows = [row for row in rows if row["orbit_type"] == "principal"]
    endpoint_rows = [row for row in rows if row["orbit_type"] == "collinear_endpoint"]
    boundary_rows = [row for row in rows if row["orbit_type"] == "VB_boundary"]
    principal_constant = len({_representation_signature(row) for row in principal_rows}) == 1
    endpoint_constant = len({_representation_signature(row) for row in endpoint_rows}) == 1
    expected_boundary_decomposition = "V_(0,-4) + 2 V_(1,-3) + V_(0,-2)"
    boundary_constant = {row["representation"]["decomposition"] for row in boundary_rows} == {
        expected_boundary_decomposition
    }
    committed_boundary_rows = inputs["isotropic_orbit_data"]["isotropic_orbit_data"]["rows"]
    committed_boundary_decompositions = {
        row["stabilizer_representation"]["representation"]["decomposition"]
        for row in committed_boundary_rows
        if row["orbit"] == "VB"
    }
    boundary_matches_committed = committed_boundary_decompositions == {expected_boundary_decomposition}
    topology = _topology_certificate()
    return {
        "mutation": mutation,
        "input_digests": input_digests,
        "topology": topology,
        "rows": rows,
        "principal_representation": "2 V_0 + 2 V_1",
        "principal_constancy_argument": (
            "the canonical stabilizer fixes the ordered real-imaginary frame and is independent of lambda; its "
            "isotypic multiplicities are locally constant over the connected principal parameter space"
        ),
        "endpoint_representation": "3 + conjugate(3)",
        "boundary_representation": expected_boundary_decomposition,
        "principal_rows_equivalent": principal_constant,
        "endpoint_rows_equivalent": endpoint_constant,
        "boundary_rows_equivalent": boundary_constant,
        "boundary_matches_committed_VB_result": boundary_matches_committed,
        "pass": topology["pass"]
        and all(row["pass"] for row in rows)
        and principal_constant
        and endpoint_constant
        and boundary_constant
        and boundary_matches_committed,
    }


def build_result() -> dict[str, Any]:
    result = topology_representation_checks()
    return {
        "schema": "a5-v-topology-stabilizer-representation-v2",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "v_topology_stabilizer_representation": result,
        "pass": result["pass"],
    }


def _self_test_mutation_task(mutation: str) -> tuple[str, dict[str, Any]]:
    """Build one independent topology or representation mutation for the parent self-test."""
    return mutation, topology_representation_checks(mutation)


def self_test() -> None:
    baseline = topology_representation_checks()
    if not baseline["pass"]:
        raise RuntimeError("baseline V topology and stabilizer-representation check failed")
    mutations = dict(
        symmetry.parallel.ordered_map(
            _self_test_mutation_task,
            ["trivialize_monodromy", "include_moving_direction", "perturb_fiber_action"],
            min_items=1,
        )
    )
    topology_mutation = mutations["trivialize_monodromy"]
    if topology_mutation["pass"] or topology_mutation["topology"]["unit_section_cohomology"].get("8") == "Z/2":
        raise RuntimeError("trivial-monodromy mutation survived the V topology check")
    moving_mutation = mutations["include_moving_direction"]
    if moving_mutation["pass"] or all(moving_mutation["rows"][0]["point_fixed"]):
        raise RuntimeError("moving-generator mutation survived the V point-stabilizer check")
    fiber_mutation = mutations["perturb_fiber_action"]
    if fiber_mutation["pass"] or fiber_mutation["rows"][0]["representation_commutators_match"]:
        raise RuntimeError("fiber-action mutation survived the V representation check")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    if arguments.check is not None and (arguments.self_test or arguments.out is not None):
        parser.error("--check cannot be combined with --self-test or --out")
    if arguments.self_test:
        self_test()
        print("PASS: V topology and stabilizer-representation self-test")
    if arguments.out is not None or arguments.check is not None:
        result = build_result()
        payload = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode()
        if arguments.check is not None:
            if payload != arguments.check.read_bytes():
                raise SystemExit(
                    f"v_topology_representation.py: fresh JSON differs byte-for-byte from {arguments.check}"
                )
            print(f"v_topology_representation.py: fresh JSON matches {arguments.check}")
        else:
            arguments.out.write_bytes(payload)
            print(f"wrote {arguments.out}")
    if not arguments.self_test and arguments.out is None and arguments.check is None:
        parser.error("choose --self-test, --out, or --check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
