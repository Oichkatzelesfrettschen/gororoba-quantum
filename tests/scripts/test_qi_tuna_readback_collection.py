"""Readback collection must retain every response before any decoding."""

import hashlib
import json
import os
from dataclasses import replace
from pathlib import Path
from typing import Any

import pytest


class Response:
    status_code = 200
    headers = {"Content-Type": "application/json"}

    def __init__(self, body: bytes) -> None:
        self.body = body
        self.closed = False

    def iter_content(self, chunk_size: int) -> list[bytes]:
        return [self.body]

    def close(self) -> None:
        self.closed = True


class Session:
    def __init__(self) -> None:
        self.paths: list[str] = []
        self.responses: list[Response] = []

    def request(self, method: str, url: str, **options: Any) -> Response:
        if method != "GET":
            raise AssertionError("readback collection attempted a non-GET")
        self.paths.append(url.removeprefix("https://api.quantum-inspire.com"))
        response = Response(json.dumps({"path": self.paths[-1]}).encode())
        self.responses.append(response)
        return response


def test_collection_returns_four_immutable_readbacks_without_scoring() -> None:
    from qi_tuna_readback_collection import capture_complete_readbacks

    checkpoint = b'{"job":11,"file":12,"batch":14,"result":21}'
    retained: list[object] = []

    class RetentionAwareSession(Session):
        def request(self, method: str, url: str, **options: Any) -> Response:
            if len(retained) != len(self.paths) + 1:
                raise AssertionError("a readback started before the preceding artifact was retained")
            return super().request(method, url, **options)

    session = RetentionAwareSession()
    capture = capture_complete_readbacks(
        checkpoint, session, lambda _force: None, lambda: None, retained.append, retained.append, timeout_seconds=1.0
    )
    if session.paths != ["/jobs/11", "/batch_jobs", "/files/12", "/results/job/11"]:
        raise AssertionError("provider readbacks did not follow the checkpointed chain")
    if capture.checkpoint_bytes != checkpoint or len(capture.readbacks) != 4:
        raise AssertionError("capture lost checkpoint or response records")
    if any(not response.closed for response in session.responses):
        raise AssertionError("capture left a response open")
    if len(retained) != 5 or retained[0] != checkpoint:
        raise AssertionError("capture did not present each artifact for retention")


def test_duplicate_checkpoint_identity_prevents_any_provider_read() -> None:
    from qi_tuna_readback_collection import capture_complete_readbacks

    session = Session()
    with pytest.raises(ValueError):
        capture_complete_readbacks(
            b'{"job":99,"job":11,"file":12,"batch":14,"result":21}',
            session,
            lambda _force: None,
            lambda: None,
            lambda _value: None,
            lambda _value: None,
            timeout_seconds=1.0,
        )
    if session.paths:
        raise AssertionError("malformed checkpoint reached provider readback")


def test_retention_failure_stops_before_the_next_readback() -> None:
    from qi_tuna_readback_collection import capture_complete_readbacks

    session = Session()

    def refuse(_receipt: object) -> None:
        raise OSError("fixture retention failure")

    with pytest.raises(OSError):
        capture_complete_readbacks(
            b'{"job":11,"file":12,"batch":14,"result":21}',
            session,
            lambda _force: None,
            lambda: None,
            lambda _value: None,
            refuse,
            timeout_seconds=1.0,
        )
    if session.paths != ["/jobs/11"]:
        raise AssertionError("capture continued after response retention failed")


def test_captured_bytes_replay_through_association_without_admission(tmp_path: Path) -> None:
    from qi_tuna_capture_commitment import capture_commitment, verify_capture_commitment
    from qi_tuna_private_readbacks import PrivateReadbackStore, load_private_readbacks
    from qi_tuna_readback_collection import capture_complete_readbacks, decode_captured_complete

    root = Path(__file__).resolve().parents[2] / "results/quantum_inspire/proposals/tuna-destination-slot-alternatives"
    catalogue = (root / "catalogue.json").read_bytes()
    catalogue_digest = hashlib.sha256(catalogue).hexdigest()
    manifest = (root / "slot-01/baseline/cases.json").read_bytes()
    source = (root / "slot-01/baseline/baseline-before.cq").read_bytes()
    checkpoint = {
        "job": 11,
        "file": 12,
        "commit": 13,
        "batch": 14,
        "backend_type": 7,
        "shots": 4096,
        "language_id": 8,
        "result": 21,
        "slot": 1,
        "arm": "baseline",
        "cases_sha256": hashlib.sha256(manifest).hexdigest(),
        "catalogue_sha256": catalogue_digest,
        "source_sha256": hashlib.sha256(source).hexdigest(),
    }
    checkpoint_bytes = json.dumps(checkpoint).encode()
    shot = "1" + "0" * 19
    result = {
        "id": 21,
        "job_id": 11,
        "shots_requested": 4096,
        "shots_done": 4096,
        "raw_data": [shot] * 4096,
        "results": {shot: 4096},
    }
    bodies = {
        "/jobs/11": {
            "id": 11,
            "file_id": 12,
            "batch_job_id": 14,
            "number_of_shots": 4096,
            "raw_data_enabled": True,
            "status": "completed",
        },
        "/files/12": {
            "id": 12,
            "commit_id": 13,
            "language_id": 8,
            "compile_stage": "none",
            "compile_properties": {},
            "content": source.decode(),
        },
        "/batch_jobs": {
            "items": [{"id": 14, "backend_type_id": 7, "job_ids": [11]}],
            "total": 1,
            "page": 1,
            "size": 100,
            "pages": 1,
        },
        "/results/job/11": {"items": [result], "total": 1, "page": 1, "size": 100, "pages": 1},
    }

    class EvidenceSession(Session):
        def request(self, method: str, url: str, **options: Any) -> Response:
            path = url.removeprefix("https://api.quantum-inspire.com")
            self.paths.append(path)
            response = Response(json.dumps(bodies[path]).encode())
            self.responses.append(response)
            return response

    directory_path = tmp_path / "private"
    directory_path.mkdir(mode=0o700)
    directory = os.open(directory_path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        with PrivateReadbackStore(directory) as store:
            capture = capture_complete_readbacks(
                checkpoint_bytes,
                EvidenceSession(),
                lambda _force: None,
                lambda: None,
                store.retain_checkpoint,
                store.retain_readback,
                timeout_seconds=1.0,
            )
        reloaded = load_private_readbacks(directory)
    finally:
        os.close(directory)
    if reloaded != capture:
        raise AssertionError("reloaded private capture differs from the captured bytes")
    verify_capture_commitment(reloaded, capture_commitment(capture))
    with pytest.raises(ValueError):
        verify_capture_commitment(reloaded, "0" * 64)
    row = decode_captured_complete(reloaded, catalogue, catalogue_digest, 1, "baseline", manifest, source)
    if row["early_ones"] != 4096 or row["terminal_ones"] != 0:
        raise AssertionError("captured association lost retention or destination mapping")
    for wrong in (
        replace(capture.readbacks[0], path="/jobs/99"),
        replace(capture.readbacks[0], query=(("id", 11),)),
        replace(capture.readbacks[0], status=True),
        replace(capture.readbacks[0], content_type="text/plain"),
        replace(capture.readbacks[0], body=b"{}"),
        capture.readbacks[2],
    ):
        changed_capture = replace(capture, readbacks=(wrong, *capture.readbacks[1:]))
        with pytest.raises(ValueError):
            decode_captured_complete(changed_capture, catalogue, catalogue_digest, 1, "baseline", manifest, source)
