"""Collect four readbacks with caller-owned attempt journals.

This offline-tested composition does not authenticate the session, checkpoint
or source association, bind effective URLs or clocks, prove callback durability,
coordinate account users, or admit a capture for inference. The caller owns those
unresolved controls and cross-restart quarantine. The legacy decoder must not
receive the wrapper.
"""

import math
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from qi_tuna_attempt_transport import AttemptIntent, AttemptOutcome, read_journaled_qi_json
from qi_tuna_capture_commitment import MAX_QUERY_INTEGER_BITS, capture_commitment, validate_capture_prefix
from qi_tuna_readback_collection import ReadbackCapture
from qi_tuna_readback_transport import Readback, _validate_target
from qi_tuna_source_association import _json_object, _positive_integer


@dataclass(frozen=True)
class JournalCallbacks:
    retain_intent: Callable[[AttemptIntent], None]
    retain_outcome: Callable[[AttemptOutcome], None]


@dataclass(frozen=True)
class UnadmittedCapture:
    """Locally collected bytes that require separate authenticated adjudication."""

    capture: ReadbackCapture


def capture_journaled_readbacks(
    checkpoint_bytes: bytes,
    session: Any,
    refresh: Callable[[bool], None],
    check_clock: Callable[[], None],
    retain_checkpoint: Callable[[bytes], None],
    retain_readback: Callable[[Readback], None],
    journals: tuple[JournalCallbacks, ...],
    *,
    timeout_seconds: float,
) -> UnadmittedCapture:
    """Present each readback and its attempts to separate retention callbacks."""
    if type(timeout_seconds) not in (int, float):
        raise ValueError("request timeout must be a finite positive number")
    try:
        valid_timeout = math.isfinite(timeout_seconds) and timeout_seconds > 0
    except OverflowError:
        valid_timeout = False
    if (
        not valid_timeout
        or type(journals) is not tuple
        or len(journals) != 4
        or any(
            type(journal) is not JournalCallbacks
            or not callable(journal.retain_intent)
            or not callable(journal.retain_outcome)
            for journal in journals
        )
        or any(not callable(callback) for callback in (refresh, check_clock, retain_checkpoint, retain_readback))
    ):
        raise ValueError("collection retention callbacks differ")
    checkpoint = _json_object(checkpoint_bytes)
    job_id = _positive_integer(checkpoint, "job")
    file_id = _positive_integer(checkpoint, "file")
    batch_id = _positive_integer(checkpoint, "batch")
    result_id = _positive_integer(checkpoint, "result")
    if any(identifier.bit_length() > MAX_QUERY_INTEGER_BITS for identifier in (job_id, file_id, batch_id, result_id)):
        raise ValueError("checkpoint identifier exceeds capture limit")
    requests: tuple[tuple[str, dict[str, int]], ...] = (
        (f"/jobs/{job_id}", {}),
        ("/batch_jobs", {"id": batch_id, "page": 1, "size": 100}),
        (f"/files/{file_id}", {}),
        (f"/results/job/{job_id}", {"page": 1, "size": 100}),
    )
    for path, params in requests:
        _validate_target(path, params)
    check_clock()
    retain_checkpoint(checkpoint_bytes)
    check_clock()
    receipts: list[Readback] = []
    for (path, params), journal in zip(requests, journals, strict=True):
        unadmitted = read_journaled_qi_json(
            session,
            path,
            params,
            refresh,
            check_clock,
            journal.retain_intent,
            journal.retain_outcome,
            timeout_seconds=timeout_seconds,
        )
        validate_capture_prefix(ReadbackCapture(checkpoint_bytes, (*receipts, unadmitted.readback)))
        retain_readback(unadmitted.readback)
        check_clock()
        receipts.append(unadmitted.readback)
    capture = ReadbackCapture(checkpoint_bytes, tuple(receipts))
    capture_commitment(capture)
    return UnadmittedCapture(capture)
