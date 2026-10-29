"""Retain one readback's attempt callbacks in a private local directory.

The caller supplies an empty trusted directory outside checkouts, serializes
access, authenticates provider and journal context, and quarantines any failed
write across restart. Reload validates parsed metadata and current body digests;
it establishes neither historical bytes, timing, provider truth, durability
nor admission.
"""

import hashlib
import json
import os
from dataclasses import dataclass
from types import TracebackType
from typing import Any, Literal

from qi_tuna_attempt_transport import AttemptIntent, AttemptOutcome
from qi_tuna_private_readbacks import _private_directory, _read_private, _write_exclusive
from qi_tuna_readback_transport import MAX_BODY, _validate_target
from qi_tuna_source_association import _json_object


def _intent_object(intent: AttemptIntent) -> dict[str, Any]:
    if type(intent) is not AttemptIntent or type(intent.attempt) is not int or intent.attempt not in (1, 2):
        raise ValueError("attempt intent identity differs")
    if type(intent.query) is not tuple or any(
        type(pair) is not tuple
        or len(pair) != 2
        or type(pair[0]) is not str
        or len(pair[0]) > MAX_BODY
        or type(pair[1]) is not int
        or pair[1].bit_length() > MAX_BODY * 3
        for pair in intent.query
    ):
        raise ValueError("attempt query differs")
    if (
        len(dict(intent.query)) != len(intent.query)
        or _validate_target(intent.path, dict(intent.query)) != intent.query
    ):
        raise ValueError("attempt locator differs")
    return {"schema": "qi-attempt-intent-v1", "attempt": intent.attempt, "path": intent.path, "query": intent.query}


def _outcome_object(outcome: AttemptOutcome, intent: AttemptIntent) -> dict[str, Any]:
    if type(outcome) is not AttemptOutcome:
        raise ValueError("attempt outcome differs")
    _intent_object(outcome.intent)
    if (
        outcome.intent != intent
        or type(outcome.request_called) is not bool
        or (outcome.status is not None and type(outcome.status) is not int)
        or (outcome.content_type is not None and type(outcome.content_type) is not str)
        or type(outcome.body) is not bytes
        or len(outcome.body) > MAX_BODY
        or type(outcome.complete) is not bool
        or (outcome.error_type is not None and type(outcome.error_type) is not str)
        or (outcome.close_error_type is not None and type(outcome.close_error_type) is not str)
    ):
        raise ValueError("attempt outcome differs")
    if not outcome.request_called and (
        outcome.status is not None
        or outcome.content_type is not None
        or outcome.body
        or outcome.complete
        or outcome.error_type is None
        or outcome.close_error_type is not None
    ):
        raise ValueError("uncalled attempt contains a response or lacks an error")
    if outcome.status is None and (outcome.content_type is not None or outcome.body or outcome.complete):
        raise ValueError("statusless attempt contains response data")
    if outcome.error_type is None and (
        not outcome.request_called
        or not outcome.complete
        or outcome.close_error_type is not None
        or outcome.status not in (200, 401)
        or (outcome.status == 401 and intent.attempt != 1)
        or (
            outcome.status == 200
            and (
                outcome.content_type is None
                or outcome.content_type.split(";", 1)[0].strip().lower() != "application/json"
                or not outcome.body
            )
        )
    ):
        raise ValueError("error-free attempt is not a complete accepted or retryable response")
    return {
        "schema": "qi-attempt-outcome-v1",
        "attempt": intent.attempt,
        "request_called": outcome.request_called,
        "status": outcome.status,
        "content_type": outcome.content_type,
        "body_length": len(outcome.body),
        "body_sha256": hashlib.sha256(outcome.body).hexdigest(),
        "complete": outcome.complete,
        "error_type": outcome.error_type,
        "close_error_type": outcome.close_error_type,
    }


def _json_bytes(value: dict[str, Any]) -> bytes:
    for item in value.values():
        if type(item) is str and len(item) > MAX_BODY:
            raise ValueError("attempt metadata field is oversized")
        if type(item) is int and item.bit_length() > MAX_BODY * 3:
            raise ValueError("attempt metadata integer is oversized")
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii") + b"\n"
    if len(encoded) > MAX_BODY:
        raise ValueError("attempt metadata is oversized")
    return encoded


def _retry_allowed(previous: AttemptOutcome, current: AttemptIntent) -> bool:
    return (
        previous.request_called
        and previous.status == 401
        and previous.complete
        and previous.error_type is None
        and previous.close_error_type is None
        and (current.path, current.query) == (previous.intent.path, previous.intent.query)
    )


class PrivateAttemptJournal:
    """Write at most two attempts in order using exclusive files and syncs."""

    def __init__(self, directory: int) -> None:
        self._directory = _private_directory(directory)
        try:
            if os.listdir(self._directory):
                raise ValueError("private attempt directory must be empty")
        except BaseException:
            os.close(self._directory)
            raise
        self._next = 1
        self._intent: AttemptIntent | None = None
        self._previous: AttemptOutcome | None = None
        self._failed = False
        self._closed = False

    def __enter__(self) -> "PrivateAttemptJournal":
        return self

    def __exit__(
        self, _kind: type[BaseException] | None, _value: BaseException | None, _trace: TracebackType | None
    ) -> None:
        self.close()

    def close(self) -> None:
        if not self._closed:
            self._closed = True
            os.close(self._directory)

    def retain_intent(self, intent: AttemptIntent) -> None:
        if self._closed or self._failed or self._intent is not None or self._next > 2:
            self._failed = True
            raise ValueError("attempt journal cannot accept an intent")
        try:
            value = _intent_object(intent)
            if intent.attempt != self._next:
                raise ValueError("attempt intent is out of order")
            if self._next == 2 and (self._previous is None or not _retry_allowed(self._previous, intent)):
                raise ValueError("retry does not follow an error-free unauthorized response")
            _write_exclusive(self._directory, f"attempt-{self._next:02d}.intent", _json_bytes(value))
            self._intent = intent
        except BaseException:
            self._failed = True
            raise

    def retain_outcome(self, outcome: AttemptOutcome) -> None:
        if self._closed or self._failed or self._intent is None:
            self._failed = True
            raise ValueError("attempt journal cannot accept an outcome")
        try:
            value = _outcome_object(outcome, self._intent)
            metadata = _json_bytes(value)
            if outcome.body:
                _write_exclusive(self._directory, f"attempt-{self._next:02d}.body", outcome.body)
            _write_exclusive(self._directory, f"attempt-{self._next:02d}.outcome", metadata)
            self._previous = outcome
            self._intent = None
            self._next += 1
        except BaseException:
            self._failed = True
            raise


@dataclass(frozen=True)
class JournalReplay:
    """Parsed local events and whether a retry was expected from the first outcome."""

    events: tuple[tuple[AttemptIntent, AttemptOutcome], ...]
    lifecycle: Literal["retry_pending", "terminal"]


def load_attempt_journal(directory: int) -> JournalReplay:
    """Reload local pairs; lifecycle does not establish admission or durability."""
    owned = _private_directory(directory)
    try:
        names = set(os.listdir(owned))
        expected: set[str] = set()
        events: list[tuple[AttemptIntent, AttemptOutcome]] = []
        for ordinal in (1, 2):
            intent_name = f"attempt-{ordinal:02d}.intent"
            outcome_name = f"attempt-{ordinal:02d}.outcome"
            if intent_name not in names:
                break
            expected.update((intent_name, outcome_name))
            raw_intent = _json_object(_read_private(owned, intent_name))
            if (
                set(raw_intent) != {"schema", "attempt", "path", "query"}
                or raw_intent["schema"] != "qi-attempt-intent-v1"
            ):
                raise ValueError("attempt intent shape differs")
            query = raw_intent["query"]
            if type(query) is not list or any(type(pair) is not list or len(pair) != 2 for pair in query):
                raise ValueError("attempt query shape differs")
            intent = AttemptIntent(raw_intent["attempt"], raw_intent["path"], tuple(tuple(pair) for pair in query))
            if intent.attempt != ordinal:
                raise ValueError("attempt order differs")
            _intent_object(intent)
            if ordinal == 2 and (not events or not _retry_allowed(events[-1][1], intent)):
                raise ValueError("retry does not follow an error-free unauthorized response")
            raw = _json_object(_read_private(owned, outcome_name))
            if (
                set(raw)
                != {
                    "schema",
                    "attempt",
                    "request_called",
                    "status",
                    "content_type",
                    "body_length",
                    "body_sha256",
                    "complete",
                    "error_type",
                    "close_error_type",
                }
                or raw["schema"] != "qi-attempt-outcome-v1"
                or type(raw["attempt"]) is not int
                or raw["attempt"] != ordinal
                or type(raw["body_length"]) is not int
                or not 0 <= raw["body_length"] <= MAX_BODY
            ):
                raise ValueError("attempt outcome shape differs")
            body_name = f"attempt-{ordinal:02d}.body"
            if raw["body_length"]:
                expected.add(body_name)
                body = _read_private(owned, body_name)
            else:
                body = b""
            outcome = AttemptOutcome(
                intent,
                raw["request_called"],
                raw["status"],
                raw["content_type"],
                body,
                raw["complete"],
                raw["error_type"],
                raw["close_error_type"],
            )
            if _outcome_object(outcome, intent) != raw:
                raise ValueError("attempt outcome bytes or metadata differ")
            events.append((intent, outcome))
        if not events or expected != names:
            raise ValueError("attempt journal is incomplete or has unexpected entries")
        last = events[-1][1]
        next_intent = AttemptIntent(2, last.intent.path, last.intent.query)
        lifecycle: Literal["retry_pending", "terminal"] = (
            "retry_pending" if len(events) == 1 and _retry_allowed(last, next_intent) else "terminal"
        )
        return JournalReplay(tuple(events), lifecycle)
    finally:
        os.close(owned)
