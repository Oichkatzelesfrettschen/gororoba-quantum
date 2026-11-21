"""The Garnet follow-up case: fused generic compile, sedenion sign-row oracles, the mutation and null arms.

Tests that read the retained case carry audit; the others build their input here."""

import json
import shutil
from pathlib import Path

import iqm_garnet_followup as followup
import iqm_grover_line as grover
import numpy as np
import pytest

import iqm_records
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
        for stem in {n for n in names if n.startswith(("m101-k1", "r-m", "s5-", "s10-"))}:
            positions = [i for i, n in enumerate(names) if n == stem]
            if sum(positions) * 2 != (len(names) - 1) * len(positions):
                raise AssertionError(f"{job['job']}: {stem} positions {positions} are not mirrored")


@pytest.mark.audit
def test_each_row_null_shares_the_row_cz_list() -> None:
    case_dir = followup.ROOT / "results/iqm/cases" / followup.CASE

    def loci(name: str) -> list[list[str]]:
        circuit = json.loads((case_dir / "circuits" / f"{name}.json").read_text())
        return [op["locus"] for op in circuit["instructions"] if op["name"] == "cz"]

    for m in followup.ROWS:
        if not loci(f"s{m}-row-c0") == loci(f"s{m}-trunc-c0") == loci(f"s{m}-id-c0") == loci(f"s{m}-id-c1"):
            raise AssertionError(f"e_{m}: the null or truncation runs another CZ list")


@pytest.mark.audit
def test_an_altered_prediction_fails_the_case_binding(tmp_path: Path) -> None:
    case_dir = tmp_path / "case"
    shutil.copytree(followup.ROOT / "results/iqm/cases" / followup.CASE, case_dir)
    iqm_records.load_job(case_dir, "grover")
    prediction = case_dir / "prediction.json"
    prediction.write_text(prediction.read_text().replace('"z_resolve": 3.0', '"z_resolve": 2.0'))
    with pytest.raises(iqm_records.RecordError, match="prediction.json"):
        iqm_records.load_job(case_dir, "grover")


def test_a_bound_prediction_is_checked_on_a_synthetic_case(tmp_path: Path) -> None:
    circuit = json.dumps({"name": "c", "instructions": []}).encode()
    prediction = b'{"decisions": {}}\n'
    case = {
        "schema": iqm_records.CASE_SCHEMA,
        "case": "synthetic",
        "prediction_sha256": iqm_records.sha256(prediction),
        "jobs": [{"job": "j", "circuits": [{"file": "circuits/c.json", "sha256": iqm_records.sha256(circuit)}]}],
    }
    (tmp_path / "circuits").mkdir()
    (tmp_path / "circuits" / "c.json").write_bytes(circuit)
    (tmp_path / "cases.json").write_text(json.dumps(case))
    (tmp_path / "prediction.json").write_bytes(prediction)
    iqm_records.load_job(tmp_path, "j")
    (tmp_path / "prediction.json").write_bytes(b'{"decisions": {"z": 2}}\n')
    with pytest.raises(iqm_records.RecordError, match="prediction.json"):
        iqm_records.load_job(tmp_path, "j")
    (tmp_path / "prediction.json").unlink()
    with pytest.raises(iqm_records.RecordError, match="prediction.json"):
        iqm_records.load_job(tmp_path, "j")
