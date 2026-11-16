"""Real limit sets of the partner kernel at the nullity-8 to nullity-12 incidences, from the holomorphic fibers.

The bordered matrix of a doubly pure z in C^15 is A(z, conj z) = [[0, -conj(z)^T], [conj(z), C_z]] with C_z skew,
linear in z and C_z z = 0. For z != 0 its kernel is {0} x (ker C_z meet z^perp), the Hermitian complement of z in
ker C_z, so ker C_z = C z (+) ker A. The map P -> P meet z^perp on planes P containing z is continuous in (z, P),
and every limit of ker C_z along z -> z_0 contains z_0. The limits of ker A at z_0 are therefore the planes
P meet z_0^perp, P a limit of the holomorphic kernel. The source closures are cut out by holomorphic polynomials in
z and the real A_5 locus is all of C^15, so the graph of z -> ker C_z is complex constructible and real
semialgebraic: its Zariski closure is its Euclidean closure (Mumford, Red Book, I.10 Corollary 1), and curve selection
(Basu and Roy, Theorem 1, docs/notes/1803.00505.md) gives a real semialgebraic path in the graph to every point of
the closed graph fiber. The record's pass covers the computed checks; these two theorems carry the realization.

This producer verifies the two identities the decomposition rests on, the failure of the decomposition under the
bilinear pairing at an isotropic point, and collects the fourteen computed holomorphic fibers with the retained
checks that the holomorphic limit equals the retained bordered limit plus the boundary line. The same deduction
gives the eight completed incidences from nullity 12 into nullity 16, where ker C_(z_0) has dimension 9.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import holomorphic_kernel_lemma as hk  # noqa: E402
import partner_purity  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "a5-kernel-attachments-real-limit-sets-v2"
NAKAYAMA_RESULT = HERE / "nakayama-rees-fibers-result.json"
BLOWUP_RESULT = HERE / "holomorphic-gauss-fibers-result.json"
NULLITY16_RESULT = HERE / "nullity16-rees-fibers-result.json"
SOURCE_PATHS = (
    HERE / "real_limit_sets.py",
    HERE / "partner_purity.py",
    HERE / "holomorphic_kernel_lemma.py",
    NAKAYAMA_RESULT,
    BLOWUP_RESULT,
    NULLITY16_RESULT,
    ROOT / "gororoba_quantum" / "cd_core.py",
)
INCIDENCE_COUNT = 14
OPEN_INCIDENCE = "E8bar->VB"
# Into nullity 16 the Rees fibers of the eight nullity-12 sources are complete and the ten nullity-8 rows block.
NULLITY16_COMPLETED_COUNT = 8
NULLITY16_BLOCKED_COUNT = 10
# z = e_1 + i e_2 has z^T z = 0 and conj(z)^T z = 2: the bilinear form vanishes on z, the Hermitian form does not.
ISOTROPIC_POINT: hk.GaussianVector = (hk.ONE, hk.I_UNIT, *([hk.ZERO] * (hk.COMPLEX_DIMENSION - 2)))
# z = sum_j j e_j: a rational point with no isotropy, where both pairings split ker C_z.
ANISOTROPIC_POINT: hk.GaussianVector = tuple(
    (Fraction(index), Fraction(0)) for index in range(1, hk.COMPLEX_DIMENSION + 1)
)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hash_path(path: Path) -> tuple[str, str]:
    return path.relative_to(ROOT).as_posix(), _sha256(path)


def _bilinear_pair(left: hk.GaussianVector, right: hk.GaussianVector) -> hk.Gaussian:
    return hk._gaussian_sum(hk._gaussian_multiply(a, b) for a, b in zip(left, right, strict=True))


def _complement(kernel: tuple[hk.GaussianVector, ...], z: hk.GaussianVector, pairing: str) -> list[hk.GaussianVector]:
    """A basis of {u in span(kernel): <z, u> = 0} for the Hermitian or the bilinear pairing with z."""
    pair = hk._hermitian_pair if pairing == "hermitian" else _bilinear_pair
    functional = (tuple(pair(z, vector) for vector in kernel),)
    return [hk._linear_combination(kernel, coefficients) for coefficients in hk._nullspace(functional)]


def _pairing_record(task: tuple[tuple[hk.GaussianVector, ...], hk.GaussianVector, str]) -> dict[str, Any]:
    """The complement of z in span(kernel) under one pairing, and whether C z (+) complement is the whole span."""
    kernel, z, pairing = task
    complement = _complement(kernel, z, pairing)
    span = hk._columns_rank((z, *complement))
    return {
        "complement_dimension": len(complement),
        "span_with_z_dimension": span,
        "direct_sum_is_the_kernel": span == len(kernel) and len(complement) == len(kernel) - 1,
    }


def _split_record(task: tuple[str, hk.GaussianVector]) -> dict[str, Any]:
    """Whether ker C_z = C z (+) {u in ker C_z: <z, u> = 0} for each pairing, at one exact point."""
    name, z = task
    c_matrix = hk._c_matrix(z)
    kernel = hk._nullspace(c_matrix)
    row: dict[str, Any] = {
        "point": name,
        "kernel_dimension": len(kernel),
        "c_z_annihilates_z": all(value == hk.ZERO for value in hk._matrix_vector(c_matrix, z)),
        "bilinear_norm": hk._gaussian_text(_bilinear_pair(z, z)),
        "hermitian_norm": hk._gaussian_text(hk._hermitian_pair(z, z)),
    }
    pairings = ("hermitian", "bilinear")
    splits = parallel.ordered_map(_pairing_record, [(kernel, z, pairing) for pairing in pairings], min_items=1)
    row.update(zip(pairings, splits, strict=True))
    return row


def _nakayama_row(row: dict[str, Any]) -> dict[str, Any]:
    fiber = row["rational"]
    witnessed = sorted({index for arc in fiber["arcs"] for index in arc["component_indices_one_based"]})
    return {
        "incidence": row["incidence"],
        "source_record": NAKAYAMA_RESULT.name,
        "resolution": "Nakayama-reduced Rees fiber",
        "minimal_generator_count": row["nakayama_generator_count"],
        "fiber_projective_dimension_degree_components": [
            fiber["image_projective_dimension"],
            fiber["image_degree"],
            fiber["component_count"],
        ],
        "characteristics_agree": bool(row["characteristic_invariants_agree"]),
        "retained_arc_count": len(row["arc_checks"]),
        "holomorphic_limit_equals_bordered_limit_plus_boundary_line": [
            bool(check["holomorphic_kernel_matches_committed_plane_plus_boundary_line"]) for check in row["arc_checks"]
        ],
        "components_reached_by_a_retained_arc": witnessed,
        "components_without_a_retained_arc": [
            index for index in range(1, fiber["component_count"] + 1) if index not in witnessed
        ],
    }


def _blowup_row(row: dict[str, Any]) -> dict[str, Any]:
    image = row["committed_first_order_image"]
    return {
        "incidence": row["incidence"],
        "source_record": BLOWUP_RESULT.name,
        "resolution": "one ordinary blow-up of the slice origin",
        "minimal_generator_count": None,
        "fiber_projective_dimension_degree_components": [
            image["projective_dimension"],
            image["degree"],
            image["component_count"],
        ],
        "characteristics_agree": bool(row["comparison"]["modular_and_rational_invariants_agree"])
        and bool(row["comparison"]["rational_matches_committed_image"]),
        "retained_arc_count": len(row["canonical_path_checks"]),
        "holomorphic_limit_equals_bordered_limit_plus_boundary_line": [
            bool(check["committed_first_order_plane_matches_retained_limit"]) for check in row["canonical_path_checks"]
        ],
        "components_reached_by_a_retained_arc": None,
        "components_without_a_retained_arc": None,
    }


def _nullity16_row(row: dict[str, Any]) -> dict[str, Any]:
    """One completed incidence from nullity 12 into nullity 16: 7-planes of the 9-dimensional ker C_(z_0)."""
    fiber = row["rational"]
    return {
        "incidence": row["incidence"],
        "source_record": NULLITY16_RESULT.name,
        "resolution": "Nakayama-reduced Rees fiber",
        "minimal_generator_count": row["nakayama_generator_count"],
        "fiber_projective_dimension_degree_components": [
            fiber["image_projective_dimension"],
            fiber["image_degree"],
            fiber["component_count"],
        ],
        "characteristics_agree": bool(row["characteristic_invariants_agree"]) and bool(row["pass"]),
        "retained_arc_count": 0,
    }


def build_record() -> dict[str, Any]:
    identities = partner_purity._case_record("")
    norm = partner_purity._positive_norm_certificate()
    identities_hold = all(
        bool(identities[key])
        for key in (
            "interior_matches_repository_bordered_block",
            "interior_is_skew",
            "right_identity_Cz_z_zero",
            "left_identity_zT_Cz_zero",
            "projected_partner_remainder_zero",
        )
    ) and bool(norm["hermitian_norm_equals_euclidean_norm"])
    anisotropic, isotropic = parallel.ordered_map(
        _split_record, (("sum_j j e_j", ANISOTROPIC_POINT), ("e_1 + i e_2", ISOTROPIC_POINT)), min_items=1
    )
    nakayama = json.loads(NAKAYAMA_RESULT.read_text(encoding="utf-8"))
    blowup = json.loads(BLOWUP_RESULT.read_text(encoding="utf-8"))
    rows = [_blowup_row(row) for row in blowup["incidences"]] + [_nakayama_row(row) for row in nakayama["incidences"]]
    rows.sort(key=lambda row: str(row["incidence"]))
    arc_flags = [flag for row in rows for flag in row["holomorphic_limit_equals_bordered_limit_plus_boundary_line"]]
    nullity16 = json.loads(NULLITY16_RESULT.read_text(encoding="utf-8"))
    completed16 = [row for row in nullity16["incidences"] if row["status"] == "completed"]
    blocked16 = sorted(str(row["incidence"]) for row in nullity16["incidences"] if row["status"] != "completed")
    rows16 = sorted((_nullity16_row(row) for row in completed16), key=lambda row: str(row["incidence"]))
    baseline_pass = (
        identities_hold
        and bool(anisotropic["c_z_annihilates_z"])
        and bool(isotropic["c_z_annihilates_z"])
        and bool(anisotropic["hermitian"]["direct_sum_is_the_kernel"])
        and bool(isotropic["hermitian"]["direct_sum_is_the_kernel"])
        and bool(anisotropic["bilinear"]["direct_sum_is_the_kernel"])
        and len(rows) == INCIDENCE_COUNT
        and len({row["incidence"] for row in rows}) == INCIDENCE_COUNT
        and OPEN_INCIDENCE not in {row["incidence"] for row in rows}
        and bool(nakayama["pass"])
        and bool(blowup["pass"])
        and all(bool(row["characteristics_agree"]) for row in rows)
        and all(arc_flags)
        and len(rows16) == NULLITY16_COMPLETED_COUNT
        and len(blocked16) == NULLITY16_BLOCKED_COUNT
        and all(bool(row["characteristics_agree"]) for row in rows16)
    )
    # The pairing mutation: with z^T u in place of conj(z)^T u the complement of an isotropic z contains z.
    mutation_detected = not bool(isotropic["bilinear"]["direct_sum_is_the_kernel"])
    return {
        "schema": SCHEMA,
        "inputs": dict(parallel.ordered_map(_hash_path, SOURCE_PATHS, min_items=1)),
        "scope": {
            "passage": (
                "the fourteen nullity-8 to nullity-12 incidences with a computed holomorphic fiber, each on its "
                "retained transverse slice germ"
            ),
            "open_incidence": OPEN_INCIDENCE,
            "claim_boundary": (
                "Each fiber is the fiber over the selected path-supported basepoint of the closed holomorphic Gauss "
                "graph of the source germ on the retained transverse slice. The record does not compute the fiber "
                "of E8bar->VB, the variation of a fiber along its boundary orbit, or limits along arcs that leave "
                "the slice beyond the retained arcs."
            ),
        },
        "kernel_decomposition": {
            "identities": {
                key: identities[key]
                for key in (
                    "interior_matches_repository_bordered_block",
                    "interior_is_skew",
                    "right_identity_Cz_z_zero",
                    "left_identity_zT_Cz_zero",
                    "projected_partner_remainder_zero",
                )
            },
            "hermitian_norm_equals_euclidean_norm": norm["hermitian_norm_equals_euclidean_norm"],
            "statement": "for every z != 0: ker A(z, conj z) = {0} x (ker C_z meet z^perp) and ker C_z = C z (+) it",
            "exact_points": [anisotropic, isotropic],
        },
        "inference": {
            "limit_map": (
                "P -> P meet z_0^perp is an isomorphism from the 5-planes of ker C_(z_0) through z_0 onto "
                "Gr(4, K_0), K_0 = ker C_(z_0) meet z_0^perp, and carries the limits of ker C_z onto the limits of "
                "ker A"
            ),
            "realization": (
                "the source closures are cut out by holomorphic polynomials in z and the doubly pure real locus is "
                "all of C^15, so the graph of z -> ker C_z over the source germ is complex constructible and real "
                "semialgebraic; every point of the computed fiber lies in its Euclidean closure and a continuous "
                "semialgebraic path in the graph starts there"
            ),
            "exclusion": "a limit along any arc in the slice germ lies in the closed graph fiber",
            "authorities": [
                "Mumford, The Red Book of Varieties and Schemes, second expanded edition (1999), section I.10, "
                "Corollary 1 of Theorem 1, page 60: a constructible subset of a variety has the same closure in the "
                "Zariski and in the classical topology; Theorem 1, page 58, is the density of a nonempty Zariski-open "
                "subset in the classical topology (statement read in the reading copy with sha256 "
                "28a2ca3ac335162ce26faa3f6e8a081a548e82dc7e8426e8f2b81bd626d2f00b)",
                "Basu and Roy, Quantitative Curve Selection Lemma, Theorem 1 (docs/notes/1803.00505.md): a "
                "continuous semialgebraic path from a closure point into a semialgebraic set",
            ],
            "status": "deductions from the computed checks and the two authorities; pass does not test them",
        },
        "incidences": rows,
        "nullity_16": {
            "passage": (
                "the eight incidences from nullity 12 into nullity 16 with a completed Rees fiber, each on its "
                "retained transverse slice germ at the census-supported N+ or N- basepoint"
            ),
            "limit_map": (
                "P -> P meet z_0^perp from the 7-planes of the 9-dimensional ker C_(z_0) through z_0 onto "
                "Gr(6, K_0), K_0 of dimension 8"
            ),
            "incidences": rows16,
            "blocked_incidences": blocked16,
            "claim_boundary": (
                "No retained arc ends at these basepoints, so no arc comparison enters; the ten incidences from "
                "the nullity-8 sources have no computed fiber."
            ),
        },
        "summary": {
            "incidence_count": len(rows),
            "nullity_16_incidence_count": len(rows16),
            "nullity_16_blocked_count": len(blocked16),
            "retained_arc_count": len(arc_flags),
            "retained_arcs_matching": sum(arc_flags),
            "incidences_with_a_component_no_retained_arc_reaches": [
                row["incidence"] for row in rows if row["components_without_a_retained_arc"]
            ],
        },
        "mutation_control": {
            "name": "bilinear_pairing_at_an_isotropic_point",
            "input_change": "replace conj(z)^T u by z^T u in the complement of z at z = e_1 + i e_2",
            "detected": mutation_detected,
        },
        "falsifier": (
            "C_z is not skew or C_z z is nonzero; the Hermitian complement of z fails to split ker C_z at an exact "
            "point; a retained arc whose holomorphic limit differs from its bordered limit plus the boundary line; "
            "a source closure whose equations involve conj(z); a fiber invariant that the two characteristics "
            "compute differently; or the bilinear pairing splitting ker C_z at the isotropic point."
        ),
        "pass": baseline_pass and mutation_detected,
    }


def _record_bytes(record: dict[str, Any]) -> bytes:
    return (json.dumps(record, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _self_test(record: dict[str, Any]) -> None:
    _require(bool(record["pass"]), "the real-limit-set record failed")
    _require(bool(record["mutation_control"]["detected"]), "the bilinear pairing mutation survived")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="write the deterministic JSON record")
    parser.add_argument("--check", type=Path, help="compare a deterministic record byte for byte")
    parser.add_argument("--self-test", action="store_true", help="run the baseline and mutation checks")
    arguments = parser.parse_args()
    if sum((arguments.out is not None, arguments.check is not None, arguments.self_test)) != 1:
        parser.error("select exactly one of --out, --check, or --self-test")
    record = build_record()
    _self_test(record)
    rendered = _record_bytes(record)
    if arguments.out is not None:
        arguments.out.write_bytes(rendered)
    elif arguments.check is not None:
        _require(arguments.check.read_bytes() == rendered, f"{arguments.check} differs from the regenerated record")


if __name__ == "__main__":
    main()
