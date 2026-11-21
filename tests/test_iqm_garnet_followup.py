"""The Garnet follow-up case: fused generic compile, sedenion sign-row oracles, the mutation and null arms.

Tests that read the retained case carry audit; the others build their input here."""

import json
import shutil
import sys
from pathlib import Path

import iqm_garnet_followup as followup
import iqm_grover_line as grover
import numpy as np
import pytest

import garnet_followup_analysis as analysis
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


def test_a_verdict_resolves_at_three_standard_errors() -> None:
    if [analysis.verdict_of(z) for z in (3.0, 2.99, -3.0, -2.99)] != [
        "positive",
        "unresolved",
        "negative",
        "unresolved",
    ]:
        raise AssertionError("verdict_of misreads the resolution threshold")
    if analysis.verdict_of(3.0, strict=True) != "unresolved" or analysis.verdict_of(3.01, strict=True) != "positive":
        raise AssertionError("the role rule is strict")
    with pytest.raises(analysis.AnalysisError, match="zero variance"):
        analysis.z_of(0.1, 0.0)


def test_outcome_strings_read_character_q_as_bit_q() -> None:
    if (
        analysis.outcome_index("1001") != 9
        or analysis.outcome_key(9, 4) != "1001"
        or analysis.outcome_index("110") != 3
    ):
        raise AssertionError("outcome strings are not little-endian")
    with pytest.raises(analysis.AnalysisError, match="bit string"):
        analysis.outcome_index("10a")


def test_synthetic_shots_keep_their_total_without_a_generator() -> None:
    counts = followup.largest_remainder([0.5, 0.3, 0.2 - 1e-12, 1e-12], 3424)
    if sum(counts) != 3424 or counts != followup.largest_remainder([0.5, 0.3, 0.2 - 1e-12, 1e-12], 3424):
        raise AssertionError(f"largest remainder gave {counts}")
    moved = followup.shifted({"a": 0.5, "b": 0.5}, "a", "b", 0.1)
    if abs(moved["a"] - 0.4) > 1e-12 or abs(sum(moved.values()) - 1.0) > 1e-12:
        raise AssertionError(f"shifted gave {moved}")


@pytest.mark.audit
def test_analysis_decides_synthetic_acquisitions() -> None:
    followup.analysis_checks()


@pytest.mark.audit
def test_analyze_writes_one_record_from_both_runs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    case_dir = followup.RETAINED_CASE.parent / followup.CASE
    runs = [followup.synthetic_run(case_dir, tmp_path / job, job) for job in ("sedenion", "grover")]
    out = tmp_path / "analysis.json"
    monkeypatch.setattr(sys, "argv", ["iqm_garnet_followup.py", "analyze", *map(str, runs), "--out", str(out)])
    if followup.main() != 0:
        raise AssertionError("analyze failed")
    record = json.loads(out.read_text())
    if record["schema"] != analysis.SCHEMA or record["not_run"] or "exploratory" not in record:
        raise AssertionError(f"record keys {sorted(record)}")
    required = {"prx_load_generic", "prx_load_line", "cz_sequence", "depth_law_101", "depth_law_011"}
    if not required | {"role_or_qubit", "sedenion_5", "sedenion_10"} <= set(record["decisions"]):
        raise AssertionError(f"decisions {sorted(record['decisions'])}")
    single = analysis.analyze(runs[:1], case_dir)
    if single["not_run"] != ["grover"] or "sedenion_5" not in single["decisions"]:
        raise AssertionError("a single sedenion run does not analyze alone")
