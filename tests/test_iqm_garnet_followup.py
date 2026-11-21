"""The Garnet follow-up case: fused generic compile, sedenion sign-row oracles, the mutation and null arms.

Tests that read the retained case carry audit; the others build their input here."""

import json

import iqm_garnet_followup as followup
import iqm_grover_line as grover
import numpy as np
import pytest

import sedenion_sign_oracle as sed


def test_fusion_keeps_the_cz_sequence_and_the_distribution() -> None:
    path = ["QA", "QB", "QC"]
    generic = grover.generic("101", path, "g")
    merged = followup.fused(generic, path, "f")
    cz = [op["locus"] for op in generic["instructions"] if op["name"] == "cz"]
    if [op["locus"] for op in merged["instructions"] if op["name"] == "cz"] != cz:
        raise AssertionError("fusion moved a CZ")
    if followup.count(merged, "prx") != 38 or followup.count(generic, "prx") != 68:
        raise AssertionError("prx counts changed")
    if np.max(np.abs(followup.ideal(merged, path) - followup.ideal(generic, path))) > 1e-9:
        raise AssertionError("fusion changed the outcome distribution")


def test_every_row_carries_the_parities_of_odd_overlap() -> None:
    for m in range(1, 16):
        eighths = sed.phase_eighths(sed.row_bits(m))
        if set(eighths) != {s for s in range(1, 16) if sed.parity(s & m)}:
            raise AssertionError(f"m={m}: parities {sorted(eighths)}")


def test_a_flipped_sign_moves_the_walsh_distribution() -> None:
    # The mutation test: the observable must change when the sign table changes.
    bits = sed.row_bits(5)
    flipped = list(bits)
    flipped[3] ^= 1
    if np.array_equal(sed.walsh_distribution(bits), sed.walsh_distribution(flipped)):
        raise AssertionError("one flipped sign leaves the Walsh distribution unchanged")


@pytest.mark.parametrize("m", followup.ROWS)  # type: ignore[untyped-decorator, unused-ignore]
def test_row_truncation_and_identity_share_one_cz_sequence(m: int) -> None:
    square = ["QA", "QB", "QC", "QD"]
    circuits = {kind: followup.sedenion_circuit(m, kind, square, kind) for kind in ("row", "trunc", "id")}
    loci = {kind: [op["locus"] for op in c[0]["instructions"] if op["name"] == "cz"] for kind, c in circuits.items()}
    if not loci["row"] == loci["trunc"] == loci["id"] or len(loci["row"]) != 8:
        raise AssertionError(f"e_{m}: CZ sequences {loci}")
    row = followup.ideal(circuits["row"][0], square)
    top = int(np.argmax(row))
    if abs(row[top] - 9 / 16) > 1e-9 or abs(followup.ideal(circuits["trunc"][0], square)[top] - 0.25) > 1e-9:
        raise AssertionError(f"e_{m}: row peak {row[top]}")
    if followup.ideal(circuits["id"][0], square)[0] < 1 - 1e-9:
        raise AssertionError(f"e_{m}: the identity oracle leaves |0000>")


@pytest.mark.audit
def test_retained_case_mirrors_its_contrasts() -> None:
    case = json.loads((followup.ROOT / "results/iqm/cases" / followup.CASE / "cases.json").read_text())
    for job in case["jobs"]:
        names = [c["file"].split("/")[-1].removesuffix(".json").rsplit("-c", 1)[0] for c in job["circuits"]]
        for stem in {n for n in names if n.startswith(("m101-k1", "s5-", "s10-", "s-id"))}:
            positions = [i for i, n in enumerate(names) if n == stem]
            if sum(positions) * 2 != (len(names) - 1) * len(positions):
                raise AssertionError(f"{job['job']}: {stem} positions {positions} are not mirrored")
