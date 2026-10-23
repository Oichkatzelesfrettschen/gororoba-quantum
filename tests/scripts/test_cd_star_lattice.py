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
        raise AssertionError("the reoriented edge still carries one boundary point")
    order = lattice.group_facts(4, lattice.stabilizer(4, mutant))["order"]
    if order == 24:
        raise AssertionError("a reoriented edge kept the order-24 symmetry")


def test_missing_boundary_point_fails_one_per_edge() -> None:
    boundary = lattice.cd_boundary(4)
    if lattice.one_per_edge(4, boundary - {sorted(boundary)[0]}):
        raise AssertionError("one_per_edge accepted a boundary with an empty edge")


def test_octahedron_admits_no_reflection_free_boundary_beyond_order_four() -> None:
    selections = lattice.octahedron_selections()
    free = {int(k) for k in selections["reflection_free_stabilizer_order_counts"]}
    if selections["selections"] != 4096 or max(free) != 4 or selections["stabilizer_order_counts"].get("24") != 2:
        raise AssertionError(selections)
