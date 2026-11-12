"""The retained quadratic map of fiber_plucker_map.py: serialization and normalization of the fitted matrix, its
coordinate provenance, and the absence of the map from the default record."""

from __future__ import annotations

import hashlib
import itertools
import json
import sys
from pathlib import Path
from typing import Any

import pytest

pytest.importorskip("flint")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "docs/evidence/a5-exceptional-fibers/kernel-limits"))

import fiber_plucker_map as fpm  # noqa: E402
import vb_limit_span as span  # noqa: E402
from flint import nmod_mat  # noqa: E402

PRIME = 32009
VARIABLES = 3
PLUCKER_COORDINATES = 7
TRAIN = 12
HELD = 3


def _check(condition: bool) -> None:
    if not condition:
        raise AssertionError


def _point(s: int) -> list[int]:
    return [(1 + s) % PRIME, (2 + s * s) % PRIME, (3 + s**3) % PRIME]


def _matrix() -> list[list[int]]:
    """A fixed 6 x 7 matrix T over the monomials of degree 2 in three variables; its entries are hashes of the fixed
    integers (i, j), and its rank is 6 (checked by the t_rank assertion of the tests)."""
    return [
        [int.from_bytes(hashlib.sha256(f"t:{i}:{j}".encode()).digest()[:8], "big") % PRIME for j in range(7)]
        for i in range(6)
    ]


def _sample(s: int, arc: int) -> dict[str, Any]:
    """The Plucker vector (s + 2) * v_2(y) T is an exact quadratic function of y."""
    y = _point(s)
    v = fpm.veronese(y, 2, PRIME)
    t = _matrix()
    plucker = [(s + 2) * sum(v[i] * t[i][j] for i in range(6)) % PRIME for j in range(PLUCKER_COORDINATES)]
    return {"kind": "q", "arc": arc, "y": y, "plucker": plucker}


def _samples() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows = [_sample(s, s - 1) for s in range(1, TRAIN + HELD + 1)]
    return rows[:TRAIN], rows[TRAIN:]


def _proportional(a: list[int], b: list[int]) -> bool:
    return any(a) and any(b) and nmod_mat([a, b], PRIME).rank() == 1


def test_default_fit_validates_and_carries_no_map() -> None:
    samples, held = _samples()
    out = fpm.fit(samples, held, PRIME, 3)
    _check(out["verdict"] == "degree_2_fit_validated")
    _check(out["delta"] == 2 and out["solution_dimension"] == 1 and out["t_rank"] == 6)
    _check("map" not in out)
    _check(fpm.fit(samples, held, PRIME, 3, retain_map=False) == out)


def test_retained_map_reproduces_the_digest_and_the_samples() -> None:
    samples, held = _samples()
    plain = fpm.fit(samples, held, PRIME, 3)
    out = fpm.fit(samples, held, PRIME, 3, retain_map=True)
    retained = out.pop("map")
    _check(out == plain)
    _check(retained["field_prime"] == PRIME and retained["degree"] == 2)
    rows = retained["matrix_rows"]
    _check(len(rows) == len(retained["monomial_indices"]) == out["t_rank"])
    _check(all(len(row) == retained["plucker_coordinate_count"] == PLUCKER_COORDINATES for row in rows))
    # The first nonzero entry in row-major order is 1, and the entries digest to t_sha256 under the documented text.
    flat = [v for row in rows for v in row]
    _check(next(v for v in flat if v) == 1 and all(0 <= v < PRIME for v in flat))
    text = f"{len(rows)}x{len(rows[0])}:" + ",".join(str(v) for v in flat)
    _check(hashlib.sha256(text.encode()).hexdigest() == out["t_sha256"])
    _check(fpm.matrix_digest(rows) == out["t_sha256"])
    # monomial_indices select the rows of v_2(y) in veronese() order: v_2(y)[indices] times the matrix is proportional
    # to the Plucker vector of every fitted and held-out sample.
    monomials = list(itertools.combinations_with_replacement(range(VARIABLES), 2))
    _check(retained["monomials"] == [list(monomials[j]) for j in retained["monomial_indices"]])
    matrix = nmod_mat(rows, PRIME)
    for sample in (*samples, *held):
        v = fpm.veronese(sample["y"], 2, PRIME)
        image = nmod_mat([[v[j] for j in retained["monomial_indices"]]], PRIME) * matrix
        _check(_proportional([int(image[0, j]) for j in range(image.ncols())], sample["plucker"]))


def test_normalization_scales_the_first_nonzero_entry_to_one() -> None:
    t = nmod_mat([[0, 0, 4], [6, 8, 0]], PRIME)
    rows = fpm.normalized_entries(t, PRIME)
    inverse = pow(4, -1, PRIME)
    _check(rows == [[0, 0, 1], [6 * inverse % PRIME, 8 * inverse % PRIME, 0]])
    _check(fpm.normalized_digest(t, PRIME) == fpm.normalized_digest(nmod_mat(rows, PRIME), PRIME))
    scaled = nmod_mat([[0, 0, 12], [18, 24, 0]], PRIME)
    _check(fpm.normalized_digest(scaled, PRIME) == fpm.normalized_digest(t, PRIME))


def test_plucker_subsets_match_the_columns_span_plucker_emits() -> None:
    subsets = fpm.plucker_subsets(6, 3)
    _check(subsets["count"] == 20 and subsets["ground"] == 6 and subsets["size"] == 3)
    listed = [list(c) for c in itertools.combinations(range(6), 3)]
    _check(subsets["sha256"] == hashlib.sha256(json.dumps(listed, separators=(",", ":")).encode()).hexdigest())
    # A 6-dimensional kernel with a 3-plane: span.plucker returns one minor per 3-subset of the 6 basis coordinates.
    basis = [tuple(int(i == j) for j in range(8)) for i in range(6)]
    plane = [basis[0], basis[2], tuple(a + b for a, b in zip(basis[1], basis[4], strict=True))]
    _check(len(span.plucker(plane, basis, PRIME)) == subsets["count"])
    _check(fpm.plucker_subsets(6, 2)["sha256"] != subsets["sha256"])
    # The retained Iso map has 16 basis vectors and 8-planes: C(16, 8) columns.
    _check(fpm.plucker_subsets(16, 8)["count"] == 12870)


def test_input_digests_name_the_header_and_sources_relative_to_the_repository() -> None:
    files = fpm.input_files("iso-nm", PRIME)
    names = fpm.file_digests(files)
    header = "docs/evidence/a5-exceptional-fibers/working/build/inputs/p32009-r10754/iso-nm.sing"
    _check(header in names)
    _check("docs/evidence/a5-exceptional-fibers/kernel-limits/fiber_plucker_map.py" in names)
    _check("docs/evidence/a5-kernel-attachments/nullity16-basepoints-result.json" in names)
    _check(all(not name.startswith("/") and len(digest) == 64 for name, digest in names.items()))
    _check(names[header] == hashlib.sha256((ROOT / header).read_bytes()).hexdigest())
    _check(list(names) == sorted(names))
    # The other prime's header changes the digested set.
    other = fpm.file_digests(fpm.input_files("iso-nm", 32029))
    _check("docs/evidence/a5-exceptional-fibers/working/build/inputs/p32029-r9115/iso-nm.sing" in other)


def test_map_provenance_binds_generators_basis_and_subsets() -> None:
    basis = [tuple(int(i == j) for j in range(32)) for i in range(16)]
    record = fpm.map_provenance("iso-nm", PRIME, list(basis))
    _, _, generators = fpm.limits.header("iso-nm", PRIME)
    _check(record["header_slug"] == "iso-nm")
    _check(record["generators"]["count"] == len(generators))
    _check(record["generators"]["sha256"] == hashlib.sha256(json.dumps(generators).encode()).hexdigest())
    _check(record["boundary_kernel_basis"] == [list(row) for row in basis])
    _check(record["plucker_subsets"] == fpm.plucker_subsets(16, 16 - fpm.limits.SOURCE_NULLITY))
    reordered = fpm.map_provenance("iso-nm", PRIME, [basis[1], basis[0], *basis[2:]])
    _check(reordered["boundary_kernel_basis_sha256"] != record["boundary_kernel_basis_sha256"])
    json.dumps(record)
