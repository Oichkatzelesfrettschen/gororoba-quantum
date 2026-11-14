"""The kernel certificates of CdTowerCanonicalKernels.v (gororoba-math, rocq/quantum) against cd_core and the A_5
strata representatives.

docs/evidence/cd-tower-kernel-certificates/certificates.json holds, for the canonical point y of each of the twelve
orbits of nullity 8, 12 and 16, the integer data (d, P, V, C) with L V = 0, d I = P L + V C and C V = d I_n for the
matrix L of z -> y z. The Rocq file proves the same identities for the pair-tower product by vm_compute. The tests
here recompute y from the split coordinates of docs/evidence/a5-strata-regularity/strata_regularity.py and L from
cd_core.cd_sign, check the three identities in integer arithmetic, compare the nullity with the rank of L modulo
primes that do and do not divide d, require the Rocq file to be the rendering of the JSON, and require three
mutated inputs to fail.
"""

import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "docs/evidence/cd-tower-kernel-certificates"))
sys.path.insert(0, str(ROOT / "scripts"))

import exact_rank  # noqa: E402
import kernel_certificates as kc  # noqa: E402
import strata_regularity  # noqa: E402

import parallel  # noqa: E402

PRIMES = (2, 3, 5, 7, 32009, 32029)


def records() -> list[dict[str, Any]]:
    points: list[dict[str, Any]] = json.loads(kc.CERTIFICATES.read_text(encoding="utf-8"))["points"]
    return points


def point_defects(record: dict[str, Any]) -> list[str]:
    """Defects of a record against the point recomputed from the strata representative of its name."""
    split = list(strata_regularity.REPS[str(record["name"])])
    problems = kc.defects(record, kc.point(split))
    if record["split"] != split or record["point"] != kc.point(split):
        problems.append("point")
    return problems


def modular_nullities(record: dict[str, Any]) -> dict[int, int]:
    left = kc.left_matrix(record["point"])
    return {prime: kc.DIM - exact_rank.rank_mod(left, prime) for prime in PRIMES}


def test_the_twelve_points_are_the_strata_representatives_in_order() -> None:
    names = [str(record["name"]) for record in records()]
    if names != list(kc.NULLITY):
        raise AssertionError(f"certificates.json lists {names}")
    missing = [name for name in names if name not in strata_regularity.REPS]
    if missing:
        raise AssertionError(f"no strata representative for {missing}")


def test_every_certificate_satisfies_the_three_identities() -> None:
    found = parallel.ordered_map(point_defects, records(), min_items=1)
    failed = {str(record["name"]): problems for record, problems in zip(records(), found, strict=True) if problems}
    if failed:
        raise AssertionError(f"certificate identities fail: {failed}")


def test_nullities_match_the_strata_table() -> None:
    """Nullity 8, 12 or 16 as recorded for the strata, with 16 at the two points of N_+ and N_-."""
    expected = {**strata_regularity.NULLITY, "Np": 16, "Nm": 16}
    differing = {r["name"]: r["nullity"] for r in records() if r["nullity"] != expected[str(r["name"])]}
    if differing:
        raise AssertionError(f"nullities differ from the strata table: {differing}")


def test_modular_nullity_equals_the_certified_one_exactly_off_the_scalar() -> None:
    """For a prime not dividing d the nullity of L modulo the prime is n; for a prime dividing d it is larger."""
    nullities = parallel.ordered_map(modular_nullities, records(), min_items=1)
    wrong = []
    for record, by_prime in zip(records(), nullities, strict=True):
        scalar, nullity = int(record["scalar"]), int(record["nullity"])
        for prime, value in by_prime.items():
            if (scalar % prime != 0 and value != nullity) or (scalar % prime == 0 and value <= nullity):
                wrong.append((record["name"], prime, value))
    if wrong:
        raise AssertionError(f"modular nullities contradict the certificates: {wrong}")


@pytest.mark.audit
def test_rocq_file_is_the_rendering_of_the_certificates(math_source: Callable[[str], Path]) -> None:
    if math_source("CdTowerCanonicalKernels.v").read_text(encoding="utf-8") != kc.render(records()):
        raise AssertionError(
            "CdTowerCanonicalKernels.v of gororoba-math differs from the rendering of certificates.json"
        )


def test_mutated_inputs_fail_the_identities() -> None:
    """A flipped sign in the point, a changed kernel vector entry and a doubled scalar each break an identity."""
    record = records()[0]
    point = list(record["point"])
    flipped = [-x if index == 27 else x for index, x in enumerate(point)]
    if flipped == point or not kc.defects(record, flipped):
        raise AssertionError("the certificate of W8 must fail at the point with the sign of e_27 flipped")
    vectors = [list(row) for row in record["vectors"]]
    vectors[0][0] += 1
    if not kc.defects({**record, "vectors": vectors}, point):
        raise AssertionError("a certificate with one changed kernel vector entry must fail")
    if not kc.defects({**record, "scalar": 2 * int(record["scalar"])}, point):
        raise AssertionError("a certificate with a doubled scalar must fail")
