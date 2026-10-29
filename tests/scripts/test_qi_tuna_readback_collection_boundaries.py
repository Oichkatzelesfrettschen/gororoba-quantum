"""Exercise every readback position at the receipt and retention boundaries."""

import hashlib
from dataclasses import replace
from typing import Any

import pytest


@pytest.mark.parametrize("position", range(4))
@pytest.mark.parametrize("field", ["path", "query", "status", "content_type", "body", "body_sha256"])
def test_each_receipt_rejects_mutated_envelope_before_decode(position: int, field: str, monkeypatch: Any) -> None:
    import qi_tuna_readback_collection as collection
    from qi_tuna_readback_transport import Readback

    body = b"{}"
    digest = hashlib.sha256(body).hexdigest()
    receipts = (
        Readback("/jobs/11", (), 200, "application/json", body, digest),
        Readback("/batch_jobs", (("id", 14), ("page", 1), ("size", 100)), 200, "application/json", body, digest),
        Readback("/files/12", (), 200, "application/json", body, digest),
        Readback("/results/job/11", (("page", 1), ("size", 100)), 200, "application/json", body, digest),
    )
    capture = collection.ReadbackCapture(b'{"job":11,"file":12,"batch":14,"result":21}', receipts)
    sentinel = {"validated": True}
    monkeypatch.setattr(collection, "decode_associated_complete_bytes", lambda *args: sentinel)
    arguments = (b"catalogue", "digest", 1, "baseline", b"manifest", b"source")
    if collection.decode_captured_complete(capture, *arguments) is not sentinel:
        raise AssertionError("valid receipt sequence did not reach the association decoder")
    values: dict[str, Any] = {
        "path": "/jobs/99",
        "query": (("unexpected", 99),),
        "status": 201,
        "content_type": "text/plain",
        "body": b"changed",
        "body_sha256": "0" * 64,
    }
    changed = list(receipts)
    changed[position] = replace(changed[position], **{field: values[field]})
    with pytest.raises(ValueError):
        collection.decode_captured_complete(replace(capture, readbacks=tuple(changed)), *arguments)


@pytest.mark.parametrize("failure_position", range(4))
def test_each_retention_failure_stops_before_next_request(failure_position: int) -> None:
    from qi_tuna_readback_collection import capture_complete_readbacks

    class Response:
        status_code = 200
        headers = {"Content-Type": "application/json"}

        def iter_content(self, chunk_size: int) -> list[bytes]:
            return [b"{}"]

        def close(self) -> None:
            pass

    class Session:
        def __init__(self) -> None:
            self.requests: list[tuple[str, dict[str, int]]] = []

        def request(self, method: str, url: str, **options: Any) -> Response:
            self.requests.append((url.removeprefix("https://api.quantum-inspire.com"), options["params"]))
            return Response()

    session = Session()
    retained: list[object] = []

    def retain(receipt: object) -> None:
        if len(retained) == failure_position:
            raise OSError("fixture persistence failure")
        retained.append(receipt)

    with pytest.raises(OSError, match="fixture persistence failure"):
        capture_complete_readbacks(
            b'{"job":11,"file":12,"batch":14,"result":21}',
            session,
            lambda _force: None,
            lambda: None,
            lambda _checkpoint: None,
            retain,
            timeout_seconds=1.0,
        )
    expected = [
        ("/jobs/11", {}),
        ("/batch_jobs", {"id": 14, "page": 1, "size": 100}),
        ("/files/12", {}),
        ("/results/job/11", {"page": 1, "size": 100}),
    ]
    if session.requests != expected[: failure_position + 1] or len(retained) != failure_position:
        raise AssertionError("collection continued after failed persistence or changed the request sequence")


@pytest.mark.parametrize("expiry_position", range(4))
def test_expiry_after_response_keeps_receipt_and_stops_next_request(expiry_position: int) -> None:
    from qi_tuna_readback_collection import capture_complete_readbacks

    expired = False
    retained: list[object] = []

    class Response:
        status_code = 200
        headers = {"Content-Type": "application/json"}

        def __init__(self, position: int) -> None:
            self.position = position

        def iter_content(self, chunk_size: int) -> list[bytes]:
            return [b"{}"]

        def close(self) -> None:
            nonlocal expired
            if self.position == expiry_position:
                expired = True

    class Session:
        def __init__(self) -> None:
            self.count = 0

        def request(self, method: str, url: str, **options: Any) -> Response:
            response = Response(self.count)
            self.count += 1
            return response

    def check_clock() -> None:
        if expired:
            raise TimeoutError("fixture boundary expired")

    session = Session()
    with pytest.raises(TimeoutError, match="fixture boundary expired"):
        capture_complete_readbacks(
            b'{"job":11,"file":12,"batch":14,"result":21}',
            session,
            lambda _force: None,
            check_clock,
            lambda _checkpoint: None,
            retained.append,
            timeout_seconds=1.0,
        )
    if session.count != expiry_position + 1 or len(retained) != expiry_position + 1:
        raise AssertionError("an obtained response was discarded or another read started after expiry")
