"""Verify both source alternatives at every prospective Tuna assignment position."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest


def test_all_slots_bind_both_alternatives_without_an_order(tmp_path: Path) -> None:
    """Catch omitted alternatives, selected orders, changed source bytes or shared slot identities."""
    import qi_tuna_destination_slot_cases as cases

    output = tmp_path / "proposal"
    cases.write_proposal(output)
    catalogue = cases.check_proposal(output)
    if catalogue["provider_execution_authorized"] is not False or catalogue["slots"] != 24:
        raise AssertionError("the proposal must describe 24 slots without provider authority")
    if len(catalogue["alternatives"]) != 48 or "assignments" in catalogue:
        raise AssertionError("each slot must have two alternatives and no selected sequence")
    manifests = []
    expected_sources = {
        "baseline": ("baseline-before.cq", "3ab15a468b5eaa4811a2a06f297754269976f6901dde12370cf3d5fad593f267", 19),
        "rotated": ("rotated-destinations.cq", "3084eef16a0d32a23d7b3fa41c92f27fa3ce4f3d84791d128a10246728ad6d5d", 18),
    }
    for slot in range(1, 25):
        for arm in ("baseline", "rotated"):
            directory = output / f"slot-{slot:02d}" / arm
            manifest = json.loads((directory / "cases.json").read_bytes())
            if (manifest["slot"], manifest["comparison_arm"], manifest["shots"], manifest["backend_type_id"]) != (
                slot,
                arm,
                4096,
                7,
            ):
                raise AssertionError("slot identity, arm or provider envelope differs")
            if len(manifest["circuits"]) != 1 or manifest["provider_execution_authorized"] is not False:
                raise AssertionError("each alternative must be one unapproved circuit")
            filename, expected_hash, q6_bit = expected_sources[arm]
            row = manifest["circuits"][0]
            if row["file"] != filename or row["sha256"] != expected_hash:
                raise AssertionError("the arm source identity must match its independently specified bytes")
            if hashlib.sha256((directory / filename).read_bytes()).hexdigest() != expected_hash:
                raise AssertionError("the slot source bytes must match the approved historical identity")
            if row["measurement_to_bit_map"][2] != {"qubit": 6, "classical_bit": q6_bit}:
                raise AssertionError("early q6 must use the declared arm-specific destination")
            manifests.append((directory / "cases.json").read_bytes())
    if len(set(manifests)) != 48:
        raise AssertionError("each slot and arm must have a distinct manifest identity")


def test_proposal_check_rejects_tampering_or_extra_files(tmp_path: Path) -> None:
    """Catch modified source bytes, altered slot records and unlisted files."""
    import qi_tuna_destination_slot_cases as cases

    output = tmp_path / "proposal"
    cases.write_proposal(output)
    path = output / "slot-01" / "baseline" / "baseline-before.cq"
    original = path.read_bytes()
    path.write_bytes(original + b"\n")
    with pytest.raises(ValueError, match="proposal differs"):
        cases.check_proposal(output)
    path.write_bytes(original)
    (output / "unexpected.json").write_text("{}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="proposal differs"):
        cases.check_proposal(output)


def test_proposal_rejects_symlinks_and_extra_directories(tmp_path: Path) -> None:
    """Catch redirected source bytes and unlisted directory entries."""
    import qi_tuna_destination_slot_cases as cases

    output = tmp_path / "proposal"
    cases.write_proposal(output)
    extra = output / "unlisted"
    extra.mkdir()
    with pytest.raises(ValueError, match="proposal differs"):
        cases.check_proposal(output)
    extra.rmdir()
    source = output / "slot-01" / "baseline" / "baseline-before.cq"
    moved = tmp_path / "source.cq"
    source.rename(moved)
    source.symlink_to(moved)
    with pytest.raises(ValueError, match="proposal differs"):
        cases.check_proposal(output)


def test_proposal_rejects_hardlinked_source(tmp_path: Path) -> None:
    """Catch a source that can be changed through a second filesystem name."""
    import qi_tuna_destination_slot_cases as cases

    output = tmp_path / "proposal"
    cases.write_proposal(output)
    source = output / "slot-01" / "baseline" / "baseline-before.cq"
    os.link(source, tmp_path / "second-name.cq")
    with pytest.raises(ValueError, match="proposal differs"):
        cases.check_proposal(output)
