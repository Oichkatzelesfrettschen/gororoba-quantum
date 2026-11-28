"""The Frobenius-orbit decision rule of the E8-bar section test, on synthetic partitions."""

from __future__ import annotations

import a5_e8bar_sections as record


def require(condition: bool) -> None:
    if not condition:
        raise AssertionError


def row(orbits: list[int]) -> dict[str, object]:
    n = sum(orbits)
    return {
        "dim": 0,
        "vdim": n,
        "rad_vdim": n,
        "eliminant_generators": 1,
        "eliminant_degree": n,
        "orbits": orbits,
        "squarefree": True,
    }


def test_retained_partitions_support_irreducibility() -> None:
    rows = [row(p) for p in ([2, 4, 5, 13], [1, 2, 5, 16], [1, 2, 3, 18], [24], [1, 3, 20])]
    require(record.decide(rows, 24)["supports_irreducible_reduced"])


def test_a_rational_extra_component_is_a_common_sub_sum() -> None:
    rows = [row(p) for p in ([1, 2, 4, 5, 13], [1, 1, 2, 5, 16], [1, 24])]
    d = record.decide(rows, 25)
    require(d["common_sub_sums"] == [1, 24] and not d["supports_irreducible_reduced"])


def test_even_orbits_leave_gcd_two() -> None:
    d = record.decide([row([2, 22]), row([4, 20])], 24)
    require(d["orbit_gcd"] == 2 and not d["supports_irreducible_reduced"])


def test_a_non_reduced_section_is_not_clean() -> None:
    bad = row([24])
    bad["rad_vdim"] = 23
    require(not record.decide([bad], 24)["clean_sections"])


def test_sections_are_deterministic_in_the_seed() -> None:
    require(record.section(record.SECTION_SEEDS[0]) == record.section(record.SECTION_SEEDS[0]))
