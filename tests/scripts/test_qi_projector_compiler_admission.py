"""Compiler admission rejects changed instructions, registers and bit destinations."""

from pathlib import Path

import pytest
from qi_projector_compiler_admission import PROPOSAL, normalized_instructions


@pytest.mark.parametrize("source", sorted(PROPOSAL.glob("*/*.cq")))
def test_complete_frozen_instruction_stream(source: Path) -> None:
    compiled = PROPOSAL / "local-compiled" / source.relative_to(PROPOSAL)
    if normalized_instructions(source.read_text()) != normalized_instructions(compiled.read_text()):
        raise AssertionError("full instruction sequence changed")


@pytest.mark.parametrize(
    ("original", "replacement"),
    [
        ("CZ q[1], q[4]", "CZ q[1], q[6]"),
        ("b[17] = measure q[4]", "b[18] = measure q[4]"),
        ("Ry(-0.78539816339744828)", "Ry(0.78539816339744828)"),
        ("H q[8]\nRy(0) q[1]", "Ry(0) q[1]\nH q[8]"),
        ("bit[20]", "bit[21]"),
        ("barrier q\nb[17]", "b[17]"),
    ],
)
def test_changed_stream_is_distinct(original: str, replacement: str) -> None:
    source = (PROPOSAL / "tuna-qualification/geometry.cq").read_text()
    if original not in source:
        raise AssertionError("mutation did not reach source")
    if normalized_instructions(source) == normalized_instructions(source.replace(original, replacement, 1)):
        raise AssertionError("changed instruction stream passed")


@pytest.mark.parametrize(
    "instruction",
    ["Foo q[0]", "Ry(nan) q[0]", "X(1) q[0]", "CZ q[0], q[0]", "H q[2]", "b[2] = measure q[0]"],
)
def test_unknown_or_invalid_instruction_rejected(instruction: str) -> None:
    with pytest.raises(ValueError):
        normalized_instructions("version 3.0\nqubit[2] q\nbit[2] b\n" + instruction)


def test_writer_precision_is_explicit() -> None:
    prefix = "version 3.0\nqubit[2] q\nbit[2] b\n"
    source = normalized_instructions(prefix + "Ry(1.5707963267948966) q[0]")
    compiled = normalized_instructions(prefix + "Ry(1.5707963) q[0]")
    altered = normalized_instructions(prefix + "Ry(1.5707964) q[0]")
    if source != compiled or source == altered:
        raise AssertionError("eight significant digit comparison differs")


def test_retained_receipt_inputs() -> None:
    from qi_projector_compiler_admission import RECEIPT, check_retained

    check_retained(RECEIPT)


def test_corrupt_receipt_stream_rejected(tmp_path: Path) -> None:
    import json

    from qi_projector_compiler_admission import RECEIPT, check_retained

    record = json.loads(RECEIPT.read_text())
    record["circuits"][0]["normalized_instructions"]["instructions"][0][0] = "X"
    altered = tmp_path / "altered.json"
    altered.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="source instruction stream differs"):
        check_retained(altered)
