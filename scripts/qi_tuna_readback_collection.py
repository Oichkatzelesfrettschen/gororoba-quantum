"""Collect source-to-result readback bytes without submitting or scoring.

The caller authenticates the session and checkpoint, supplies bounded callbacks,
and makes retention durable. Callback success is not proof of durability. The
capture is a sequence of non-atomic provider observations, not an admission or
evidence that the provider served the recorded physical schedule.
"""

import hashlib
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from qi_tuna_readback_transport import Readback, read_qi_json
from qi_tuna_source_association import _json_object, _positive_integer, decode_associated_complete_bytes


@dataclass(frozen=True)
class ReadbackCapture:
    checkpoint_bytes: bytes
    readbacks: tuple[Readback, ...]


def capture_complete_readbacks(
    checkpoint_bytes: bytes,
    session: Any,
    refresh: Callable[[bool], None],
    check_clock: Callable[[], None],
    retain_checkpoint: Callable[[bytes], None],
    retain_readback: Callable[[Readback], None],
    *,
    timeout_seconds: float,
) -> ReadbackCapture:
    """Read four checkpointed resources, presenting each response for retention."""
    checkpoint = _json_object(checkpoint_bytes)
    job_id = _positive_integer(checkpoint, "job")
    file_id = _positive_integer(checkpoint, "file")
    batch_id = _positive_integer(checkpoint, "batch")
    _positive_integer(checkpoint, "result")
    check_clock()
    retain_checkpoint(checkpoint_bytes)
    check_clock()
    requests: tuple[tuple[str, dict[str, int]], ...] = (
        (f"/jobs/{job_id}", {}),
        ("/batch_jobs", {"id": batch_id, "page": 1, "size": 100}),
        (f"/files/{file_id}", {}),
        (f"/results/job/{job_id}", {"page": 1, "size": 100}),
    )
    readbacks: list[Readback] = []
    for path, params in requests:
        receipt = read_qi_json(session, path, params, refresh, check_clock, timeout_seconds=timeout_seconds)
        retain_readback(receipt)
        check_clock()
        readbacks.append(receipt)
    return ReadbackCapture(checkpoint_bytes, tuple(readbacks))


def decode_captured_complete(
    capture: ReadbackCapture,
    catalogue_bytes: bytes,
    expected_catalogue_sha256: str,
    slot: int,
    arm: str,
    manifest_bytes: bytes,
    source: bytes,
) -> dict[str, Any]:
    """Check receipt locators and bytes before decoding; trust and retention stay external."""
    if type(capture) is not ReadbackCapture or type(capture.readbacks) is not tuple or len(capture.readbacks) != 4:
        raise ValueError("capture must contain four readbacks")
    checkpoint = _json_object(capture.checkpoint_bytes)
    job_id = _positive_integer(checkpoint, "job")
    file_id = _positive_integer(checkpoint, "file")
    batch_id = _positive_integer(checkpoint, "batch")
    _positive_integer(checkpoint, "result")
    expected = (
        (f"/jobs/{job_id}", ()),
        ("/batch_jobs", (("id", batch_id), ("page", 1), ("size", 100))),
        (f"/files/{file_id}", ()),
        (f"/results/job/{job_id}", (("page", 1), ("size", 100))),
    )
    for receipt, (path, query) in zip(capture.readbacks, expected, strict=True):
        if type(receipt) is not Readback or type(receipt.path) is not str or receipt.path != path:
            raise ValueError("readback path differs from checkpoint")
        if (
            type(receipt.query) is not tuple
            or any(
                type(item) is not tuple or len(item) != 2 or type(item[0]) is not str or type(item[1]) is not int
                for item in receipt.query
            )
            or receipt.query != query
            or type(receipt.status) is not int
            or receipt.status != 200
        ):
            raise ValueError("readback query or status differs")
        if (
            type(receipt.content_type) is not str
            or receipt.content_type.split(";", 1)[0].strip().lower() != "application/json"
            or type(receipt.body) is not bytes
            or type(receipt.body_sha256) is not str
            or hashlib.sha256(receipt.body).hexdigest() != receipt.body_sha256
        ):
            raise ValueError("readback content type or body digest differs")
    return decode_associated_complete_bytes(
        catalogue_bytes,
        expected_catalogue_sha256,
        slot,
        arm,
        manifest_bytes,
        source,
        capture.checkpoint_bytes,
        capture.readbacks[0].body,
        capture.readbacks[1].body,
        capture.readbacks[2].body,
        capture.readbacks[3].body,
    )
