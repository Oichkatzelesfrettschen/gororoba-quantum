"""Capture commitments must bind ordered receipts to exact retained bytes."""

import hashlib
import json
from dataclasses import replace

import pytest


def test_capture_commitment_binds_checkpoint_receipts_and_order() -> None:
    from qi_tuna_capture_commitment import capture_commitment, verify_capture_commitment
    from qi_tuna_readback_collection import ReadbackCapture
    from qi_tuna_readback_transport import Readback

    checkpoint = b'{"job":11}'
    first_body = b'{"id":11}'
    second_body = b'{"id":12}'
    first = Readback("/jobs/11", (), 200, "application/json", first_body, hashlib.sha256(first_body).hexdigest())
    second = Readback("/files/12", (), 200, "application/json", second_body, hashlib.sha256(second_body).hexdigest())
    receipts = (first, second, first, second)
    capture = ReadbackCapture(checkpoint, receipts)
    description = {
        "schema": "qi-capture-commitment-v1",
        "checkpoint_length": len(checkpoint),
        "checkpoint_sha256": hashlib.sha256(checkpoint).hexdigest(),
        "readbacks": [
            {
                "path": receipt.path,
                "query": receipt.query,
                "status": receipt.status,
                "content_type": receipt.content_type,
                "body_length": len(receipt.body),
                "body_sha256": hashlib.sha256(receipt.body).hexdigest(),
            }
            for receipt in receipts
        ],
    }
    canonical = json.dumps(description, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    expected = hashlib.sha256(b"gororoba-qi-capture-v1\0" + canonical).hexdigest()
    if capture_commitment(capture) != expected:
        raise AssertionError("capture commitment differs from independently encoded receipt description")
    verify_capture_commitment(capture, expected)
    for changed in (
        replace(capture, checkpoint_bytes=checkpoint + b" "),
        replace(capture, readbacks=(second, first, first, second)),
        replace(capture, readbacks=(replace(first, path="/jobs/99"), second, first, second)),
        replace(capture, readbacks=(replace(first, query=(("id", 11),)), second, first, second)),
        replace(
            capture, readbacks=(replace(first, content_type="application/json; charset=utf-8"), second, first, second)
        ),
        replace(capture, readbacks=(replace(first, body=b"{}"), second, first, second)),
        replace(capture, readbacks=(replace(first, body_sha256="é" * 64), second, first, second)),
        replace(capture, readbacks=(replace(first, status=True), second, first, second)),
        replace(capture, readbacks=(first, second, first)),
    ):
        with pytest.raises(ValueError):
            verify_capture_commitment(changed, expected)
    for invalid in ("", "0" * 63, "G" * 64, "A" * 64):
        with pytest.raises(ValueError):
            verify_capture_commitment(capture, invalid)


@pytest.mark.parametrize("position", range(4))
def test_fixed_literal_commitment_rejects_coherent_receipt_replacements(position: int) -> None:
    from qi_tuna_capture_commitment import capture_commitment, verify_capture_commitment
    from qi_tuna_readback_collection import ReadbackCapture
    from qi_tuna_readback_transport import Readback

    original_body = b'{"id":11}'
    substitute_body = b'{"id":22}'
    original = Readback(
        "/jobs/11", (), 200, "application/json", original_body, hashlib.sha256(original_body).hexdigest()
    )
    original_capture = ReadbackCapture(b'{"job":11}', (original,) * 4)
    fixed_commitment = "f668a16ca6618657dfbb87ae034081653df9ca324d5c9f06c28b892654c2fe20"
    verify_capture_commitment(original_capture, fixed_commitment)
    for replacement in (
        replace(original, body=substitute_body, body_sha256=hashlib.sha256(substitute_body).hexdigest()),
        replace(original, status=201),
    ):
        receipts = list(original_capture.readbacks)
        receipts[position] = replacement
        with pytest.raises(ValueError):
            verify_capture_commitment(replace(original_capture, readbacks=tuple(receipts)), fixed_commitment)
    replacement = replace(
        original, path="/jobs/22", body=substitute_body, body_sha256=hashlib.sha256(substitute_body).hexdigest()
    )
    replacement_capture = ReadbackCapture(b'{"job":22}', (replacement,) * 4)
    with pytest.raises(ValueError):
        verify_capture_commitment(replacement_capture, fixed_commitment)
    verify_capture_commitment(replacement_capture, capture_commitment(replacement_capture))


def test_canonical_capture_vector_with_unicode_escapes_and_ordered_query() -> None:
    from qi_tuna_capture_commitment import capture_commitment
    from qi_tuna_readback_collection import ReadbackCapture
    from qi_tuna_readback_transport import Readback

    receipt = Readback(
        "/qé\n",
        (('quote"', 1), ("tab\t", 2)),
        200,
        "text/é",
        b"a",
        "ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb",
    )
    capture = ReadbackCapture(b"x", (receipt,) * 4)
    expected = "f1ec857e2781615b8d049718cfdb6b68369d36efbdb6b54f252b4825c55a1342"
    canonical_receipt = (
        rb'{"body_length":1,"body_sha256":"ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb",'
        rb'"content_type":"text/\u00e9","path":"/q\u00e9\n","query":[["quote\"",1],["tab\t",2]],"status":200}'
    )
    canonical = (
        rb'{"checkpoint_length":1,"checkpoint_sha256":"2d711642b726b04401627ca9fbac32f5c8530fb1903cc4db02258717921a4881",'
        rb'"readbacks":[' + b",".join((canonical_receipt,) * 4) + rb'],"schema":"qi-capture-commitment-v1"}'
    )
    if hashlib.sha256(b"gororoba-qi-capture-v1\0" + canonical).hexdigest() != expected:
        raise AssertionError("literal canonical bytes differ from the retained digest")
    if capture_commitment(capture) != expected:
        raise AssertionError("capture differs from the literal canonical-byte vector hashed with OpenSSL")


def test_direct_capture_rejects_oversized_envelope_metadata() -> None:
    from qi_tuna_capture_commitment import capture_commitment
    from qi_tuna_readback_collection import ReadbackCapture
    from qi_tuna_readback_transport import MAX_BODY, Readback

    body = b"{}"
    receipt = Readback("/jobs/11", (), 200, "application/json", body, hashlib.sha256(body).hexdigest())
    replacements = (
        replace(receipt, path="x" * 257),
        replace(receipt, content_type="x" * (MAX_BODY + 1)),
        replace(receipt, query=(("a", 1), ("b", 2), ("c", 3), ("d", 4))),
        replace(receipt, query=(("x" * (MAX_BODY + 1), 1),)),
        replace(receipt, query=(("id", 1 << (MAX_BODY * 3 + 1)),)),
    )
    for changed in replacements:
        with pytest.raises(ValueError):
            capture_commitment(ReadbackCapture(b"{}", (changed, receipt, receipt, receipt)))


def test_query_integer_bound_and_escaped_aggregate() -> None:
    from qi_tuna_capture_commitment import MAX_QUERY_INTEGER_BITS, capture_commitment
    from qi_tuna_readback_collection import ReadbackCapture
    from qi_tuna_readback_transport import MAX_BODY, Readback

    body = b"{}"
    receipt = Readback("/jobs/11", (), 200, "application/json", body, hashlib.sha256(body).hexdigest())
    for value in (0, -1, (1 << MAX_QUERY_INTEGER_BITS) - 1, -((1 << MAX_QUERY_INTEGER_BITS) - 1)):
        changed = replace(receipt, query=(("id", value),))
        capture_commitment(ReadbackCapture(b"{}", (changed, receipt, receipt, receipt)))
    for value in (1 << MAX_QUERY_INTEGER_BITS, -(1 << MAX_QUERY_INTEGER_BITS)):
        changed = replace(receipt, query=(("id", value),))
        with pytest.raises(ValueError):
            capture_commitment(ReadbackCapture(b"{}", (changed, receipt, receipt, receipt)))

    for content_type in ("x" * (MAX_BODY // 3), "\U0001f600" * (MAX_BODY // 24)):
        changed = replace(receipt, content_type=content_type)
        with pytest.raises(ValueError, match="metadata is oversized"):
            capture_commitment(ReadbackCapture(b"{}", (changed,) * 4))


def test_escaped_size_matches_canonical_json_across_character_classes() -> None:
    from qi_tuna_capture_commitment import _escaped_size

    characters = "".join(chr(codepoint) for codepoint in range(256)) + "\ud800\udfff\ue000\uffff\U0001f600"
    for value in ("", characters, characters[::-1], '"\\\n\t'):
        expected = len(json.dumps(value, ensure_ascii=True).encode("ascii"))
        if _escaped_size(value) != expected:
            raise AssertionError("preflight size differs from escaped canonical JSON")


def test_oversized_escaped_metadata_is_rejected_before_json_serialization(monkeypatch: pytest.MonkeyPatch) -> None:
    import qi_tuna_capture_commitment
    from qi_tuna_readback_collection import ReadbackCapture
    from qi_tuna_readback_transport import MAX_BODY, Readback

    body = b"{}"
    receipt = Readback("/jobs/11", (), 200, "\U0001f600" * (MAX_BODY // 24), body, hashlib.sha256(body).hexdigest())

    def forbidden_serialization(*_args: object, **_kwargs: object) -> str:
        raise AssertionError("oversized metadata reached JSON serialization")

    monkeypatch.setattr(qi_tuna_capture_commitment.json, "dumps", forbidden_serialization)
    with pytest.raises(ValueError, match="metadata is oversized"):
        qi_tuna_capture_commitment.capture_commitment(ReadbackCapture(b"{}", (receipt,) * 4))


def test_fixed_metadata_reserve_covers_maximum_schema_overhead() -> None:
    from qi_tuna_capture_commitment import FIXED_METADATA_RESERVE, MAX_QUERY_INTEGER_BITS, _escaped_size
    from qi_tuna_readback_transport import MAX_BODY

    number = -((1 << MAX_QUERY_INTEGER_BITS) - 1)
    path, content_type = "/jobs/1", "application/json"
    query = (("a", number), ("b", number), ("c", number))
    receipt = {
        "path": path,
        "query": query,
        "status": 599,
        "content_type": content_type,
        "body_length": MAX_BODY,
        "body_sha256": "f" * 64,
    }
    description = {
        "schema": "qi-capture-commitment-v1",
        "checkpoint_length": MAX_BODY,
        "checkpoint_sha256": "f" * 64,
        "readbacks": [receipt] * 4,
    }
    encoded = json.dumps(description, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    variable_bytes = 4 * (
        _escaped_size(path)
        + _escaped_size(content_type)
        + sum(_escaped_size(key) + len(str(value)) for key, value in query)
    )
    if len(encoded) - variable_bytes > FIXED_METADATA_RESERVE:
        raise AssertionError("fixed metadata reserve fails to cover the maximum schema overhead")
