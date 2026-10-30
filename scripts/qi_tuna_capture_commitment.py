"""Commit to the exact bytes and ordered envelopes of a readback capture.

The caller authenticates the expected commitment and establishes durable
retention, request identity, timing and scientific admission separately.
"""

import hashlib
import hmac
import json
import re

from qi_tuna_readback_collection import ReadbackCapture
from qi_tuna_readback_transport import MAX_BODY, Readback

DOMAIN = b"gororoba-qi-capture-v1\0"
MAX_QUERY_INTEGER_BITS = 256
FIXED_METADATA_RESERVE = 2048


def _escaped_size(value: str) -> int:
    """Count ASCII JSON string bytes without allocating its escaped form."""
    size = 2
    for character in value:
        codepoint = ord(character)
        if character in ('"', "\\") or codepoint in (8, 9, 10, 12, 13):
            size += 2
        elif codepoint < 32 or 127 <= codepoint <= 0xFFFF:
            size += 6
        elif codepoint > 0xFFFF:
            size += 12
        else:
            size += 1
        if size > MAX_BODY:
            raise ValueError("capture envelope metadata is oversized")
    return size


def _validated_envelopes(capture: ReadbackCapture, *, complete: bool) -> list[dict[str, object]]:
    if (
        type(capture) is not ReadbackCapture
        or type(capture.checkpoint_bytes) is not bytes
        or not 0 < len(capture.checkpoint_bytes) <= MAX_BODY
        or type(capture.readbacks) is not tuple
        or not 1 <= len(capture.readbacks) <= 4
        or (complete and len(capture.readbacks) != 4)
    ):
        raise ValueError("capture shape differs")
    envelopes: list[dict[str, object]] = []
    # Reserve space for the fixed schema, field names, punctuation and digests.
    metadata_size = FIXED_METADATA_RESERVE
    for receipt in capture.readbacks:
        if (
            type(receipt) is not Readback
            or type(receipt.path) is not str
            or not receipt.path
            or len(receipt.path) > 256
            or type(receipt.query) is not tuple
            or len(receipt.query) > 3
            or any(
                type(item) is not tuple
                or len(item) != 2
                or type(item[0]) is not str
                or len(item[0]) > MAX_BODY
                or type(item[1]) is not int
                or item[1].bit_length() > MAX_QUERY_INTEGER_BITS
                for item in receipt.query
            )
            or type(receipt.status) is not int
            or not 100 <= receipt.status <= 599
            or type(receipt.content_type) is not str
            or len(receipt.content_type) > MAX_BODY
            or type(receipt.body) is not bytes
            or not 0 < len(receipt.body) <= MAX_BODY
            or type(receipt.body_sha256) is not str
            or re.fullmatch(r"[0-9a-f]{64}", receipt.body_sha256) is None
            or not hmac.compare_digest(hashlib.sha256(receipt.body).hexdigest(), receipt.body_sha256)
        ):
            raise ValueError("receipt envelope or body differs")
        metadata_size += _escaped_size(receipt.path) + _escaped_size(receipt.content_type)
        metadata_size += sum(_escaped_size(name) + len(str(value)) for name, value in receipt.query)
        if metadata_size > MAX_BODY:
            raise ValueError("capture envelope metadata is oversized")
        envelopes.append(
            {
                "path": receipt.path,
                "query": receipt.query,
                "status": receipt.status,
                "content_type": receipt.content_type,
                "body_length": len(receipt.body),
                "body_sha256": receipt.body_sha256,
            }
        )
    return envelopes


def validate_capture_prefix(capture: ReadbackCapture) -> None:
    """Validate the retained prefix against the complete capture budget."""
    _validated_envelopes(capture, complete=False)


def capture_commitment(capture: ReadbackCapture) -> str:
    """Hash a complete four-receipt byte snapshot without authenticating it."""
    envelopes = _validated_envelopes(capture, complete=True)
    description = {
        "schema": "qi-capture-commitment-v1",
        "checkpoint_length": len(capture.checkpoint_bytes),
        "checkpoint_sha256": hashlib.sha256(capture.checkpoint_bytes).hexdigest(),
        "readbacks": envelopes,
    }
    canonical = json.dumps(description, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    if len(canonical) > MAX_BODY:
        raise ValueError("capture commitment metadata is oversized")
    return hashlib.sha256(DOMAIN + canonical).hexdigest()


def verify_capture_commitment(capture: ReadbackCapture, expected: str) -> None:
    """Compare with an externally authenticated lowercase SHA-256 commitment."""
    if type(expected) is not str or re.fullmatch(r"[0-9a-f]{64}", expected) is None:
        raise ValueError("expected commitment must be lowercase SHA-256")
    if not hmac.compare_digest(capture_commitment(capture), expected):
        raise ValueError("capture differs from expected commitment")
