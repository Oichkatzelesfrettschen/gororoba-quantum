"""IQM submission receipt: the posted bytes are retained and named by wire_sha256, and records check them."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import iqm_jobs  # noqa: E402
import iqm_platform  # noqa: E402

import iqm_records  # noqa: E402

BODY = {"shots": 100, "circuits": [{"name": "c0", "instructions": []}], "heralding_mode": "none"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def posted(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, bytes]:
    case = tmp_path / "case"
    case.mkdir()
    (case / "cases.json").write_text("{}")
    sent: list[bytes] = []

    def transport(
        method: str, url: str, data: bytes | None, headers: dict[str, str]
    ) -> tuple[int, dict[str, str], bytes]:
        if method == "POST" and url.endswith("/circuit"):
            sent.append(data or b"")
            return 201, {}, b'{"id": "job-1"}'
        return 200, {}, b"{}"

    row: dict[str, Any] = {"expected_seconds": 1.0}
    monkeypatch.setattr(iqm_jobs, "credit", lambda client: {"currentBalance": 1.0})
    monkeypatch.setattr(iqm_jobs, "load_job", lambda directory, job: ({}, row, "a" * 64))
    monkeypatch.setattr(iqm_jobs, "body_of", lambda directory, row, qc: BODY)
    run = tmp_path / "run"
    iqm_jobs.post_job(
        case, run, "kernel", "garnet:mock", "approved", "a" * 64, 1.0, 1.0, iqm_platform.Client("t", transport)
    )
    require(len(sent) == 1, "one POST")
    return run, sent[0]


def test_receipt_names_the_posted_bytes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    run, wire = posted(tmp_path, monkeypatch)
    receipt = json.loads((run / "submission.json").read_text())
    require(receipt["wire_sha256"] == sha(wire), "wire_sha256 is the digest of the bytes the transport received")
    require((run / iqm_records.SENT_BODY).read_bytes() == wire, "the retained file holds the posted bytes")
    require(receipt["body_sha256"] == sha(json.dumps(BODY, sort_keys=True).encode()), "body_sha256 keeps its form")
    state = json.loads((run / "submission-state.json").read_text())
    require(state["wire_sha256"] == receipt["wire_sha256"], "the checkpoint names the same bytes before the POST")
    iqm_records.check_wire(run, receipt)


def test_check_wire_rejects_edited_or_missing_bytes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    run, wire = posted(tmp_path, monkeypatch)
    receipt = json.loads((run / "submission.json").read_text())
    (run / iqm_records.SENT_BODY).write_bytes(wire.replace(b"100", b"101"))
    with pytest.raises(iqm_records.RecordError, match="not the posted body"):
        iqm_records.check_wire(run, receipt)
    (run / iqm_records.SENT_BODY).unlink()
    with pytest.raises(iqm_records.RecordError, match="not the posted body"):
        iqm_records.check_wire(run, receipt)


def test_check_wire_rejects_bytes_of_another_body(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    run, _ = posted(tmp_path, monkeypatch)
    receipt = json.loads((run / "submission.json").read_text())
    other = json.dumps({**BODY, "shots": 7}).encode()
    (run / iqm_records.SENT_BODY).write_bytes(other)
    receipt["wire_sha256"] = sha(other)
    with pytest.raises(iqm_records.RecordError, match="another body"):
        iqm_records.check_wire(run, receipt)


def test_receipt_without_wire_digest_predates_it(tmp_path: Path) -> None:
    iqm_records.check_wire(tmp_path, {"body_sha256": "0" * 64})


def attempt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, answer: tuple[int, bytes], sleeps: list[float] | None = None
) -> tuple[Path, Path, list[bytes]]:
    case = tmp_path / "case"
    case.mkdir()
    (case / "cases.json").write_text("{}")
    sent: list[bytes] = []

    def transport(
        method: str, url: str, data: bytes | None, headers: dict[str, str]
    ) -> tuple[int, dict[str, str], bytes]:
        if method == "POST" and url.endswith("/circuit"):
            sent.append(data or b"")
            return answer[0], {}, answer[1]
        return 200, {}, b"{}"

    row: dict[str, Any] = {"expected_seconds": 1.0}
    monkeypatch.setattr(iqm_jobs, "credit", lambda client: {"currentBalance": 1.0})
    monkeypatch.setattr(iqm_jobs, "load_job", lambda directory, job: ({}, row, "a" * 64))
    monkeypatch.setattr(iqm_jobs, "body_of", lambda directory, row, qc: BODY)
    run = tmp_path / "runs" / "kernel.run"
    run.parent.mkdir()
    try:
        iqm_jobs.post_job(
            case, run, "kernel", "garnet:mock", "approved", "a" * 64, 1.0, 1.0, iqm_platform.Client("t", transport)
        )
    except iqm_platform.PlatformError:
        pass
    return run.parent, run, sent


@pytest.mark.parametrize(
    "body",
    [b'{"detail": "bad circuit"}', b"Bad Request: plain text", b"<html>400</html>"],
    ids=["json", "text", "html"],
)
def test_a_refusal_frees_the_job_whatever_its_body(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, body: bytes
) -> None:
    runs, run, sent = attempt(tmp_path, monkeypatch, (400, body))
    require(len(sent) == 1, "one POST")
    require(not run.exists(), "the run copy with its checkpoint and body goes after a 4xx")
    iqm_jobs.refuse_earlier(runs, ".run", "kernel", "garnet:mock", sha(b"{}"))


def test_a_non_json_success_stays_unconfirmed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runs, run, _ = attempt(tmp_path, monkeypatch, (202, b"accepted"))
    require((run / "submission-state.json").exists(), "the checkpoint stays")
    require((run / "submission-unconfirmed.json").exists(), "the answer is recorded as unconfirmed")
    require(not (run / "submission.json").exists(), "no receipt without a job id")
    with pytest.raises(iqm_platform.PlatformError, match="already has"):
        iqm_jobs.refuse_earlier(runs, ".run", "kernel", "garnet:mock", sha(b"{}"))


def test_a_202_without_an_id_stays_unconfirmed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    runs, run, _ = attempt(tmp_path, monkeypatch, (202, b"{}"))
    require((run / "submission-unconfirmed.json").exists(), "the answer is recorded as unconfirmed")
    with pytest.raises(iqm_platform.PlatformError, match="already has"):
        iqm_jobs.refuse_earlier(runs, ".run", "kernel", "garnet:mock", sha(b"{}"))


def test_a_429_retry_resends_the_same_bytes(monkeypatch: pytest.MonkeyPatch) -> None:
    import urllib.error

    seen: list[bytes] = []
    refusals: list[urllib.error.HTTPError] = []

    class Reply:
        status = 201
        headers: dict[str, str] = {}

        def __enter__(self) -> Reply:
            return self

        def __exit__(self, *exc: object) -> None:
            return None

        def read(self) -> bytes:
            return b'{"id": "job-2"}'

    class Opener:
        def open(self, request: Any, timeout: float) -> Reply:
            seen.append(request.data)
            if len(seen) == 1:
                refusals.append(urllib.error.HTTPError(request.full_url, 429, "slow", {"Retry-After": "0"}, None))  # type: ignore[arg-type]
                raise refusals[-1]
            return Reply()

    monkeypatch.setattr(iqm_platform.time, "sleep", lambda seconds: None)
    client = iqm_platform.Client("t", iqm_platform.urllib_transport(Opener()))  # type: ignore[arg-type]
    wire = iqm_platform.wire_bytes(BODY)
    status, reply = client.post_bytes("api/jobs/garnet/circuit", wire)
    require((status, reply) == (201, {"id": "job-2"}), "the retry succeeds")
    require(seen == [wire, wire], "both attempts carry the retained bytes")
    for refusal in refusals:
        refusal.close()
