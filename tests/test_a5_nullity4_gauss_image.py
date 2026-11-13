"""Image of the nullity-4 kernel Gauss map: the matrix, the samplers, the kernel differential and the record rules."""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "docs" / "evidence" / "a5-kernel-bundles-residuals"))

import nullity4_gauss_image as gauss  # noqa: E402


def _same(found: object, expected: object) -> None:
    if found != expected:
        raise AssertionError((found, expected))


def test_bordered_matrix_is_skew_and_its_conjugate_exchanges_the_two_points() -> None:
    points = gauss.Points("test:matrix")
    z, w = points.vector(), points.vector()
    matrix, conjugate = gauss.bordered([*z, *w]), gauss.conjugate_bordered([*z, *w])
    size = range(gauss.BORDERED)
    _same(all((matrix[a][b] + matrix[b][a]) % gauss.PRIME == 0 for a in size for b in size), True)
    # Conjugation sends i to -i and exchanges the roles: the border reads z', the block reads w'.
    _same(conjugate[0][1], -gauss._twist(z, gauss.ROOT_OF_MINUS_ONE)[0] % gauss.PRIME)
    _same(conjugate[1][2], gauss.SIGNS[1][2] * gauss._twist(w, gauss.PRIME - gauss.ROOT_OF_MINUS_ONE)[2] % gauss.PRIME)


def test_roots_come_from_values_alone() -> None:
    _same(gauss._roots(lambda x: (x - 5) * (x - 7) * (x * x + 1) % gauss.PRIME, 4)[:2], [5, 7])
    _same(gauss._roots(lambda x: 0, 3), [])


def test_each_sampler_lands_on_its_stratum() -> None:
    polynomials = gauss._polynomials()
    expected = {gauss.STRATA[0]: (True, False), gauss.STRATA[1]: (False, True), gauss.STRATA[2]: (True, True)}
    for stratum, membership in expected.items():
        point = gauss.sample(stratum, gauss.Points(f"test:{stratum}"), polynomials)
        found = (gauss._value(polynomials["Q"], point) == 0, gauss._value(polynomials["G"], point) == 0)
        _same((stratum, found), (stratum, membership))


def test_kernel_differential_of_a_known_family() -> None:
    # ker of [[0, t], [-t, 0]] + s * (rank-0 change) on the 3 x 3 skew family [[0, a, b], [-a, 0, c], [-b, -c, 0]]:
    # at (a, b, c) = (1, 0, 0) the kernel is e3, and it moves to (c, -b, a) / a, so d/dc = e1 and d/db = -e2.
    def family(point: Any) -> list[list[int]]:
        a, b, c = point
        return [[0, a, b], [-a % gauss.PRIME, 0, c], [-b % gauss.PRIME, -c % gauss.PRIME, 0]]

    rows, frame = gauss.kernel_differential(family, [1, 0, 0], [[0, 0, 1], [0, 1, 0]], 2)
    _same(frame, [[0], [0], [1]])
    _same(rows, [[1, 0], [0, gauss.PRIME - 1]])


def test_retained_record_passes_its_rules_and_each_mutation_fails_them() -> None:
    record = json.loads(gauss.RECORD.read_text(encoding="utf-8"))
    _same((record["pass"], gauss.verdict(record), len(record["points"])), (True, [], 12))
    changes: dict[str, Callable[[dict[str, Any]], Any]] = {
        "field": lambda r: r.update(field="GF(2)"),
        "lower rank": lambda r: r["points"][0].update(rank_lower_block=14),
        "z outside": lambda r: r["points"][1].update(z_in_lower_kernel=False),
        "bordered rank": lambda r: r["points"][2]["kernels"][0].update(rank_bordered=16),
        "first coordinate": lambda r: r["points"][3]["kernels"][1].update(first_coordinate_zero=False),
        "outside lower kernel": lambda r: r["points"][4]["kernels"][2].update(inside_lower_kernel=False),
        "not orthogonal": lambda r: r["points"][5]["kernels"][3].update(orthogonal_to_w=False),
        "missing kernel": lambda r: r["points"][6].update(kernels=r["points"][6]["kernels"][:3]),
        "tangent": lambda r: r["points"][8].update(tangent_dimension=14),
        "three-plane rank": lambda r: r["points"][0].update(three_plane_map_rank=12),
        "gauss rank": lambda r: r["points"][4].update(gauss_rank_w_free=14, gauss_rank_w_on_conjugate_stratum=14),
        "gauss rank on the stratum": lambda r: r["points"][5].update(gauss_rank_w_on_conjugate_stratum=14),
        "real rank": lambda r: r["points"][9].update(real_rank=22),
        "same point": lambda r: r["points"][1].update(point_sha256=r["points"][0]["point_sha256"]),
        "missing point": lambda r: r.update(points=r["points"][:11]),
        "linear span": lambda r: r["image"][0].update(linear_span_dimension=104),
        "quadrics": lambda r: r["image"][1].update(quadrics_vanishing=1365),
        "coherent quadrics": lambda r: r["image"][1].update(quadric_ranks=[4200, 4200], quadrics_vanishing=1365),
        "growing rank": lambda r: r["image"][2].update(quadric_ranks=[1, r["image"][2]["quadric_ranks"][1]]),
        "few samples": lambda r: r["image"][0].update(quadric_samples=[100, 200]),
        "missing stratum": lambda r: r.update(image=r["image"][:2]),
        "control": lambda r: r["control"].update(rank_bordered=14),
        "fixture": lambda r: r["exact_fixtures"].update(first_coordinate_zero=65),
    }
    for name, change in changes.items():
        mutated = json.loads(json.dumps(record))
        change(mutated)
        if gauss.verdict(mutated) == []:
            raise AssertionError(f"a record mutated at {name} passes")
