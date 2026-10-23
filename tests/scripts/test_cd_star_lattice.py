"""Contracts for cd_star_lattice: the dimension-2 lattice is Tuna-17's coupler map, the quaternion boundary has a
reflection-free symmetry group of order 24, and each check rejects a planted defect.
"""

from __future__ import annotations

import cd_star_lattice as lattice
import pytest


def test_dimension_two_lattice_is_the_catalogue_coupler_map() -> None:
    binding = lattice.tuna17_binding()
    if binding["boundary_qubits"] != [0, 6, 10, 16] or not binding["mirror_point_set_differs"]:
        raise AssertionError(binding)


def test_swapped_qubit_coordinates_fail_the_catalogue_binding(monkeypatch: pytest.MonkeyPatch) -> None:
    coordinates = dict(lattice.QUBIT_COORDINATES)
    coordinates[0], coordinates[1] = coordinates[1], coordinates[0]
    monkeypatch.setattr(lattice, "QUBIT_COORDINATES", coordinates)
    with pytest.raises(lattice.CensusError):
        lattice.tuna17_binding()


def test_quaternion_boundary_symmetry_is_reflection_free_of_order_24() -> None:
    facts = lattice.group_facts(4, lattice.stabilizer(4, lattice.cd_boundary(4)))
    if facts["order"] != 24 or not facts["reflection_free"] or facts["stabilizer_of_e0"] != 3:
        raise AssertionError(facts)


def test_one_reoriented_cross_polytope_edge_destroys_the_symmetry() -> None:
    boundary = lattice.cd_boundary(4)
    original = sorted(boundary)[0]
    ((tail, head),) = lattice.boundary_arcs({original})
    partner = lattice.point(4, [(head[1], head[0]), (2 * tail[1], tail[0])])
    mutant = (boundary - {original}) | {partner}
    if not lattice.one_per_edge(4, mutant):
        raise AssertionError("reorienting one edge broke the one-per-edge property")
    order = lattice.group_facts(4, lattice.stabilizer(4, mutant))["order"]
    if order != 1:
        raise AssertionError(f"a reoriented edge left a symmetry group of order {order}")


def test_missing_boundary_point_fails_one_per_edge() -> None:
    boundary = lattice.cd_boundary(4)
    if lattice.one_per_edge(4, boundary - {sorted(boundary)[0]}):
        raise AssertionError("one_per_edge accepted a boundary with an empty edge")


def test_octahedron_admits_no_reflection_free_boundary_beyond_order_four() -> None:
    selections = lattice.octahedron_selections()
    free = {int(k) for k in selections["reflection_free_stabilizer_order_counts"]}
    cyclic = selections["reflection_free_order_and_largest_element_order_counts"].get("4:4")
    if (
        selections["selections"] != 4096
        or max(free) != 4
        or selections["stabilizer_order_counts"].get("24") != 2
        or not cyclic
    ):
        raise AssertionError(selections)


def test_arc_matrix_is_a_skew_conference_matrix_and_one_flipped_entry_breaks_it() -> None:
    w = lattice.arc_matrix(8)
    if not lattice.is_skew_conference(w):
        raise AssertionError("the octonion arc matrix is not a skew conference matrix")
    w[3][0], w[0][3] = -w[3][0], -w[0][3]
    if lattice.is_skew_conference(w):
        raise AssertionError("is_skew_conference accepted a matrix with one flipped skew pair")


def test_octonion_arc_matrix_is_paley_equivalent_and_a_flipped_pair_is_not() -> None:
    paley = lattice.paley_matrix(7)
    if len(lattice.signed_equivalences(lattice.arc_matrix(8), paley)) != 336:
        raise AssertionError("the octonion arc matrix is not equivalent to the Paley matrix of q = 7")
    mutant = lattice.arc_matrix(8)
    mutant[3][0], mutant[0][3] = -mutant[3][0], -mutant[0][3]
    if lattice.signed_equivalences(mutant, paley):
        raise AssertionError("a flipped skew pair stayed Paley-equivalent")


def test_quaternion_group_lifts_to_sl2_3_and_a_corrupted_line_map_fails() -> None:
    group = lattice.stabilizer(4, lattice.cd_boundary(4))
    equivalence = lattice.signed_equivalences(lattice.arc_matrix(4), lattice.paley_matrix(3))[0]
    line = lattice.line_action(group, equivalence)
    if not lattice.is_isomorphic_to_sl2(group, line, 3):
        raise AssertionError("the quaternion boundary group did not lift to SL(2, 3)")
    identity = tuple((axis, 1) for axis in range(4))
    other = next(g for g in group if line[g] != line[identity] and line[g] in lattice.sl2_lifts(3))
    corrupted = dict(line)
    corrupted[max(g for g in group if g not in lattice.generating_set(group) and line[g] != line[other])] = line[other]
    if lattice.is_isomorphic_to_sl2(group, corrupted, 3):
        raise AssertionError("a corrupted projective-line map still certified SL(2, 3)")


def test_quaternion_commutant_is_eisenstein_and_a_subgroup_commutant_is_larger() -> None:
    group = lattice.stabilizer(4, lattice.cd_boundary(4))
    facts = lattice.commutant_facts(4, group)
    if facts != {"dimension": 2, "basis_squares": [-3, 1]}:
        raise AssertionError(facts)
    stabilizer_of_e0 = [g for g in group if g[0] == (0, 1)]
    if len(lattice.commutant_basis(4, stabilizer_of_e0)) <= 2:
        raise AssertionError("the commutant of the order-3 stabilizer is no larger than the full group's")


def test_octonion_table_has_21_permutation_automorphisms() -> None:
    found = lattice.table_automorphisms(8)
    if len(found) != 21 or any(g[0] != (0, 1) for g in found):
        raise AssertionError(f"{len(found)} table automorphisms")
