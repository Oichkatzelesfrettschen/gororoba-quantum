"""Gateway failures cannot certify that a remote mutation had no effect."""

import io
import json
import urllib.error
from pathlib import Path

import pytest
import qd_platform as qd


@pytest.mark.parametrize("status", [408, 500, 502, 503, 504])
def test_mutation_gateway_failure_preserves_unknown_outcome(status: int, monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(*args, **kwargs):
        raise urllib.error.HTTPError("https://example.invalid/api/jobs", status, "gateway", {}, io.BytesIO(b"error"))

    monkeypatch.setattr(qd.OPENER, "open", fail)
    with pytest.raises(qd.UnansweredError, match=f"HTTP {status}"):
        qd.request("POST", "/api/jobs", auth=False, body={})


@pytest.mark.parametrize("status", [401, 403, 404, 422, 429])
def test_explicit_client_rejection_retains_http_status(status: int, monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(*args, **kwargs):
        raise urllib.error.HTTPError("https://example.invalid/api/jobs", status, "refused", {}, io.BytesIO(b"error"))

    monkeypatch.setattr(qd.OPENER, "open", fail)
    with pytest.raises(qd.RefusedError) as rejected:
        qd.request("POST", "/api/jobs", auth=False, body={})
    if rejected.value.code != status:
        raise AssertionError("the client rejection lost its HTTP status")


def test_job_gateway_failure_keeps_checkpoint_and_blocks_duplicate_post(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv(qd.TOKEN_ENV, str(tmp_path / "synthetic-token"))
    monkeypatch.setattr(qd, "token", lambda: "synthetic-token")
    monkeypatch.setattr(qd, "load_case", lambda directory: ({}, {}, "synthetic-digest"))
    body = {"payload": {"command": "sample_count"}}
    monkeypatch.setattr(
        qd,
        "plan",
        lambda *args: {"body": body, "body_sha256": "synthetic-body", "cases_sha256": "synthetic-digest"},
    )
    monkeypatch.setattr(qd, "get", lambda route: [])
    attempts = []

    def fail(call, **kwargs):
        attempts.append(call.method)
        raise urllib.error.HTTPError("https://example.invalid/api/jobs", 503, "gateway", {}, io.BytesIO(b"error"))

    monkeypatch.setattr(qd.OPENER, "open", fail)
    with pytest.raises(qd.UnansweredError):
        qd.submit(tmp_path, "qpu:ascella", "synthetic approval; provider access stubbed", 1.1, 180, 1)
    state = json.loads((tmp_path / "submission-state.json").read_text())
    if state["phase"] != "post_outcome_unknown":
        raise AssertionError(f"gateway failure incorrectly certified the job outcome: {state['phase']}")
    with pytest.raises(qd.PlatformError, match="never resubmit"):
        qd.submit(tmp_path, "qpu:ascella", "synthetic approval; provider access stubbed", 1.1, 180, 1)
    if attempts != ["POST"]:
        raise AssertionError(f"duplicate submission crossed the HTTP boundary: {attempts}")
