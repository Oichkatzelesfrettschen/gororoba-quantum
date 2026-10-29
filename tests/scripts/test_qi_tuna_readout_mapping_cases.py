"""Draft destination controls change classical labels while preserving physical operations."""

import json

import pytest
from qi_tuna_readout_mapping_cases import (
    BASELINE,
    BASELINE_HASHES,
    build,
    measurement_map,
    physical_stream,
    rotate_destinations,
    sha,
)


def test_baseline_sources_and_exact_repeats() -> None:
    files = build()
    for batch, original in (("prepared-zero", "readout-zero.cq"), ("prepared-one", "readout-one.cq")):
        before = files[f"{batch}/baseline-before.cq"]
        after = files[f"{batch}/baseline-after.cq"]
        if before.encode() != (BASELINE / original).read_bytes() or before != after:
            raise AssertionError("A controls must preserve the exact frozen source bytes")
        if sha(before) != BASELINE_HASHES[original]:
            raise AssertionError("baseline identity changed")


def test_complete_physical_stream_and_measurement_map() -> None:
    files = build()
    for batch in ("prepared-zero", "prepared-one"):
        before = files[f"{batch}/baseline-before.cq"]
        rotated = files[f"{batch}/rotated-destinations.cq"]
        if physical_stream(before) != physical_stream(rotated):
            raise AssertionError("destination rotation altered physical operations")
        expected = [
            {"qubit": 4, "classical_bit": 19},
            {"qubit": 11, "classical_bit": 17},
            {"qubit": 6, "classical_bit": 18},
        ]
        expected.extend({"qubit": qubit, "classical_bit": qubit} for qubit in range(17))
        if measurement_map(rotated) != expected:
            raise AssertionError("cyclic early destinations or terminal map differ")
        if (
            rotated.replace("b[19] = measure q[4]", "b[17] = measure q[4]")
            .replace("b[17] = measure q[11]", "b[18] = measure q[11]")
            .replace("b[18] = measure q[6]", "b[19] = measure q[6]")
            != before
        ):
            raise AssertionError("B must differ only in three destination tokens")


def test_canonical_decoder_inverse_permutation() -> None:
    files = build()
    for batch in ("prepared-zero", "prepared-one"):
        manifest = json.loads(files[f"{batch}/cases.json"])
        for entry in manifest["circuits"]:
            metadata = entry["analysis_metadata"]
            for labels in ((0, 0, 1), (1, 0, 0), (0, 1, 0), (1, 1, 1)):
                bits = ["0"] * 20
                for value, bit in zip(labels, metadata["canonical_early_classical_bits"], strict=True):
                    bits[bit] = str(value)
                raw = "".join(reversed(bits))
                decoded = tuple(int(raw[offset]) for offset in metadata["canonical_early_string_offsets"])
                if decoded != labels:
                    raise AssertionError("decoder failed to inverse-permute early classical destinations")


def test_unapproved_bounded_inventory() -> None:
    files = build()
    proposal = json.loads(files["proposal.json"])
    if proposal["shots_total"] != 24576 or proposal["provider_execution_authorized"]:
        raise AssertionError("draft acquisition scope or approval boundary differs")
    for batch in proposal["batches"]:
        manifest = json.loads(files[f"{batch}/cases.json"])
        if manifest["provider_execution_authorized"] or len(manifest["circuits"]) != 3 or manifest["shots"] != 4096:
            raise AssertionError("each draft batch requires three 4096-shot circuits and separate approval")
        if len({row["physical_instruction_stream_sha256"] for row in manifest["circuits"]}) != 1:
            raise AssertionError("batch physical stream hashes must agree")


def test_rotation_rejects_missing_measurement() -> None:
    source = (BASELINE / "readout-zero.cq").read_text()
    with pytest.raises(ValueError, match="exactly three"):
        rotate_destinations(source.replace("b[17] = measure q[4]\n", ""))


def test_physical_stream_retains_gate_and_qubit_changes() -> None:
    source = (BASELINE / "readout-one.cq").read_text()
    if physical_stream(source) == physical_stream(source.replace("X q[0]", "H q[0]")):
        raise AssertionError("physical comparison discarded a gate change")
    if physical_stream(source) == physical_stream(source.replace("b[17] = measure q[4]", "b[17] = measure q[5]")):
        raise AssertionError("physical comparison discarded a measured-qubit change")


def test_measured_estimate_and_provider_ceiling_are_distinct() -> None:
    files = build()
    proposal = json.loads(files["proposal.json"])
    if proposal["expected_execution_seconds_decimal"] != "29.533215":
        raise AssertionError("planning estimate must use the completed control durations")
    if proposal["provider_execution_ceiling_seconds"] != 1800:
        raise AssertionError("six 300-second provider limits differ from an expected duration")
    for batch in proposal["batches"]:
        manifest = json.loads(files[f"{batch}/cases.json"])
        if manifest["statistical_model_status"] != "power-and-dependence-unqualified":
            raise AssertionError("draft case must disclose unqualified inference")
        if manifest["provider_execution_ceiling_seconds"] != 900:
            raise AssertionError("three-job provider ceiling differs")


def test_retained_draft_matches_source_generation() -> None:
    from qi_tuna_readout_mapping_cases import PROPOSAL

    for name, content in build().items():
        if (PROPOSAL / name).read_text() != content:
            raise AssertionError(f"retained draft differs from source generation: {name}")
