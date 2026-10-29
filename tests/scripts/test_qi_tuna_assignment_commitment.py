"""Exercise the prospective, offline Tuna assignment commitment contract."""

from __future__ import annotations

import hashlib
import json

import pytest


def synthetic_record(values: list[int]) -> bytes:
    """A fabricated fixture exercises parsing without claiming QRNG provenance."""
    raw = json.dumps({"success": True, "type": "uint16", "length": len(values), "data": values})
    record = {
        "schema": "anu-qrng-draw-v1",
        "source": "https://api.quantumnumbers.anu.edu.au?length=24&type=uint16",
        "retrieved_utc": "2026-10-28T000000Z",
        "raw": raw,
        "raw_sha256": hashlib.sha256(raw.encode()).hexdigest(),
        "type": "uint16",
        "values": values,
    }
    return (json.dumps(record, sort_keys=True) + "\n").encode()


def test_opening_binds_draw_salt_catalogue_and_current_releases() -> None:
    """Catch altered commitment inputs and release arms while preserving slot order."""
    from qi_tuna_assignment_commitment import commitment, verify_opening

    record = synthetic_record(list(range(24)))
    salt = bytes(range(32))
    catalogue = bytes(range(32, 64))
    digest = commitment(record, salt, catalogue)
    if digest != "994e19c4baf8eb6c196636c74183e2267efe56d7145d55c9d3d037d88952e228":
        raise AssertionError("the fixed binary encoding must match the independent OpenSSL SHA-256 vector")
    releases = [{"slot": 1, "arm": "baseline"}, {"slot": 2, "arm": "rotated"}]
    verify_opening(record, salt, catalogue, digest, releases)
    complete = [{"slot": index + 1, "arm": "rotated" if index % 2 else "baseline"} for index in range(24)]
    verify_opening(record, salt, catalogue, digest, complete)
    for changed_record, changed_salt, changed_catalogue in (
        (synthetic_record([1, *range(1, 24)]), salt, catalogue),
        (record, bytes(reversed(salt)), catalogue),
        (record, salt, bytes(reversed(catalogue))),
    ):
        with pytest.raises(ValueError):
            verify_opening(changed_record, changed_salt, changed_catalogue, digest, releases)
    for changed in (
        [{"slot": 1, "arm": "rotated"}],
        [{"slot": 2, "arm": "rotated"}],
        [{"slot": 1, "arm": "baseline"}, {"slot": 1, "arm": "baseline"}],
        [{"slot": True, "arm": "baseline"}],
        [{"slot": 1, "arm": "baseline", "unreviewed": True}],
        [{"slot": index + 1, "arm": "rotated" if index % 2 else "baseline"} for index in range(25)],
    ):
        with pytest.raises(ValueError):
            verify_opening(record, salt, catalogue, digest, changed)


def test_refuses_ambiguous_draws_and_invalid_commitment_inputs() -> None:
    """Catch duplicate JSON keys, a non-24-value draw, bad salt and malformed digests."""
    from qi_tuna_assignment_commitment import commitment, verify_opening

    record = synthetic_record(list(range(24)))
    duplicate = record.replace(b'"schema":', b'"schema": "other", "schema":', 1)
    inner = json.loads(record)
    inner["raw"] = inner["raw"].replace('"success": true', '"success": false, "success": true')
    inner["raw_sha256"] = hashlib.sha256(inner["raw"].encode()).hexdigest()
    ambiguous_raw = json.dumps(inner).encode()
    invalid_time = json.loads(record)
    invalid_time["retrieved_utc"] = "2026-1-01T000000Z"
    invalid_source = json.loads(record)
    invalid_source["source"] = "https://example.invalid?length=24&type=uint16"
    for invalid in (
        duplicate,
        ambiguous_raw,
        json.dumps(invalid_time).encode(),
        json.dumps(invalid_source).encode(),
        synthetic_record(list(range(23))),
        synthetic_record([True, *range(1, 24)]),
    ):
        with pytest.raises(ValueError):
            commitment(invalid, bytes(32), bytes(32))
    for salt, catalogue in ((b"", bytes(32)), (bytes(32), b"")):
        with pytest.raises(ValueError):
            commitment(record, salt, catalogue)
    with pytest.raises(ValueError):
        verify_opening(record, bytes(32), bytes(32), "0" * 63, [])


def test_raw_boolean_and_nonobject_cannot_masquerade_as_uint16_response() -> None:
    """Catch Python's bool/int equality and unsupported raw response shapes."""
    from qi_tuna_assignment_commitment import commitment

    for index in (0, 12, 23):
        for alias in (False, True):
            values = list(range(24))
            values[index] = int(alias)
            record = json.loads(synthetic_record(values))
            raw_answer = json.loads(record["raw"])
            raw_answer["data"][index] = alias
            raw = json.dumps(raw_answer)
            record["raw"] = raw
            record["raw_sha256"] = hashlib.sha256(raw.encode()).hexdigest()
            with pytest.raises(ValueError):
                commitment(json.dumps(record).encode(), bytes(32), bytes(32))
    record = json.loads(synthetic_record(list(range(24))))
    for raw in ("[]", "null", '"text"', "5", "true"):
        mutated = dict(record)
        mutated["raw"] = raw
        mutated["raw_sha256"] = hashlib.sha256(raw.encode()).hexdigest()
        with pytest.raises(ValueError):
            commitment(json.dumps(mutated).encode(), bytes(32), bytes(32))


def test_nested_duplicate_key_and_range_mutations_are_rejected() -> None:
    """Catch a parser that checks only top-level keys or only a prefix of raw values."""
    from qi_tuna_assignment_commitment import commitment

    record = json.loads(synthetic_record(list(range(24))))
    raw = record["raw"][:-1] + ', "meta": {"x": 1, "x": 2}}'
    record["raw"] = raw
    record["raw_sha256"] = hashlib.sha256(raw.encode()).hexdigest()
    with pytest.raises(ValueError):
        commitment(json.dumps(record).encode(), bytes(32), bytes(32))
    for index in (0, 12, 23):
        for out_of_range in (-1, 65536):
            values = list(range(24))
            values[index] = out_of_range
            with pytest.raises(ValueError):
                commitment(synthetic_record(values), bytes(32), bytes(32))


def test_exact_field_sizes_source_domain_and_calendar() -> None:
    """Catch variable-size commitments and lookalike source or timestamp labels."""
    from qi_tuna_assignment_commitment import commitment, verify_opening

    record = synthetic_record(list(range(24)))
    for salt, catalogue in (
        (bytes(31), bytes(32)),
        (bytes(33), bytes(32)),
        (bytes(32), bytes(31)),
        (bytes(32), bytes(33)),
    ):
        with pytest.raises(ValueError):
            commitment(record, salt, catalogue)
    for source in (
        "https://api.quantumnumbers.anu.edu.au.evil.invalid?length=24&type=uint16",
        "https://api.quantumnumbers.anu.edu.au?length=24&type=uint16&extra=1",
        "https://api.quantumnumbers.anu.edu.au?type=uint16&length=24",
    ):
        altered = json.loads(record)
        altered["source"] = source
        with pytest.raises(ValueError):
            commitment(json.dumps(altered).encode(), bytes(32), bytes(32))
    altered = json.loads(record)
    altered["retrieved_utc"] = "2026-02-30T000000Z"
    with pytest.raises(ValueError):
        commitment(json.dumps(altered).encode(), bytes(32), bytes(32))
    digest = commitment(record, bytes(32), bytes(32))
    for malformed in (digest.upper(), "g" * 64):
        with pytest.raises(ValueError):
            verify_opening(record, bytes(32), bytes(32), malformed, [])
    legacy = json.loads(record)
    legacy["source"] = "https://qrng.anu.edu.au/API/jsonI.php?length=24&type=uint16"
    commitment(json.dumps(legacy).encode(), bytes(32), bytes(32))


def test_nonstandard_numbers_and_draw_size_are_rejected() -> None:
    """Catch nonstandard JSON constants and values outside the uint16 range."""
    from qi_tuna_assignment_commitment import commitment

    record = synthetic_record(list(range(24)))
    altered = json.loads(record)
    raw = json.loads(altered["raw"])
    raw["unexpected"] = float("nan")
    altered["raw"] = json.dumps(raw)
    altered["raw_sha256"] = hashlib.sha256(altered["raw"].encode()).hexdigest()
    for invalid in (
        json.dumps(altered).encode(),
        synthetic_record(list(range(25))),
        synthetic_record([-1, *range(1, 24)]),
        synthetic_record([65536, *range(1, 24)]),
        b"",
        b" " * (1024 * 1024 + 1),
    ):
        with pytest.raises(ValueError):
            commitment(invalid, bytes(32), bytes(32))


def test_stateless_opening_does_not_prove_unique_or_monotone_release() -> None:
    """Show that replay and rollback need a stateful, independently reviewed guard."""
    from qi_tuna_assignment_commitment import commitment, verify_opening

    record = synthetic_record(list(range(24)))
    digest = commitment(record, bytes(32), bytes(32))
    prefix = [{"slot": 1, "arm": "baseline"}, {"slot": 2, "arm": "rotated"}]
    verify_opening(record, bytes(32), bytes(32), digest, prefix)
    verify_opening(record, bytes(32), bytes(32), digest, prefix)
    verify_opening(record, bytes(32), bytes(32), digest, prefix[:1])
