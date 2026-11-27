"""Collecting a failed job whose logs read exceeds the request timeout records the logs as unavailable and keeps the
rest of the collection; qi_platform.collect alone ends with the timeout."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import qi_platform
import qi_platform_collect
import requests

BATCH = 31
LOGS_PATH_SECONDS = 90.0


class Response:
    def __init__(self, payload: Any) -> None:
        self.status_code = 200
        self.content = b"x"
        self.text = ""
        self.payload = payload

    def json(self) -> Any:
        return self.payload


class Http:
    """The service as Client.request sees it; a logs read needs LOGS_PATH_SECONDS, so a shorter timeout raises."""

    def __init__(self) -> None:
        self.timeouts: dict[str, float] = {}

    def request(self, method: str, url: str, **options: Any) -> Response:
        path = url.removeprefix(qi_platform.HOST)
        self.timeouts[path] = options["timeout"]
        if path.endswith("/logs"):
            if options["timeout"] < LOGS_PATH_SECONDS:
                raise requests.exceptions.ReadTimeout("fixture: the logs of a failed job answer after 90 s")
            return Response("fixture log")
        if path.startswith("/results/job/"):
            return Response({"items": []})
        if path == "/transactions/":
            return Response({"items": [], "pages": 1})
        job = int(path.rsplit("/", 1)[1])
        return Response(
            {"id": job, "status": "failed", "batch_job_id": BATCH, "number_of_shots": 256, "message": "fixture"}
        )


@pytest.fixture
def case_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    receipt = {"schema": "qi-submission-v2", "state": "enqueued", "batch_job": BATCH, "shots": 256}
    receipt["jobs"] = [{"file": "a.cq", "job": 7}]
    (tmp_path / "submission.json").write_text(json.dumps(receipt), encoding="utf-8")
    monkeypatch.setattr(qi_platform, "_check_submission_manifest", lambda *args, **kwargs: None)
    return tmp_path


def install(monkeypatch: pytest.MonkeyPatch, http: Http, base: type) -> None:
    def init(self: Any) -> None:
        self.expires = float("inf")
        self.refresh = lambda: None
        bound = base is qi_platform_collect.BoundedLogsClient
        self.session = qi_platform_collect.BoundedLogsSession(http, self.logs_timeout) if bound else http

    monkeypatch.setattr(base, "__init__", init)


def same(found: object, wanted: object) -> None:
    if found != wanted:
        raise AssertionError(f"{found!r} differs from {wanted!r}")


def test_the_base_collect_ends_with_the_timeout_of_a_failed_job_logs_read(
    case_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    http = Http()
    install(monkeypatch, http, qi_platform.Client)
    with pytest.raises(requests.exceptions.ReadTimeout):
        qi_platform.collect(case_dir, 0.0, 5.0)
    same((case_dir / "results.json").exists(), False)


def test_the_successor_records_unavailable_logs_after_the_bounded_timeout(
    case_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    http = Http()
    install(monkeypatch, http, qi_platform_collect.BoundedLogsClient)
    qi_platform_collect.collect(case_dir, 0.0, 5.0, logs_timeout=12.5)
    collected = json.loads((case_dir / "results.json").read_text(encoding="utf-8"))
    same(collected["schema"], "qi-collection-v1")
    same(
        [(row["file"], row["job"]["status"], row["logs"]) for row in collected["jobs"]],
        [("a.cq", "failed", "logs: unavailable (timeout)")],
    )
    same(http.timeouts["/jobs/7/logs"], 12.5)
    same(http.timeouts["/jobs/7"], 60)


def test_the_successor_keeps_the_logs_a_service_answers_within_the_bound(
    case_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    http = Http()
    install(monkeypatch, http, qi_platform_collect.BoundedLogsClient)
    qi_platform_collect.collect(case_dir, 0.0, 5.0, logs_timeout=LOGS_PATH_SECONDS)
    collected = json.loads((case_dir / "results.json").read_text(encoding="utf-8"))
    same(collected["jobs"][0]["logs"], "fixture log")


def test_the_binding_is_restored_and_a_nonpositive_bound_is_refused(
    case_dir: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    before = qi_platform.Client
    install(monkeypatch, Http(), qi_platform_collect.BoundedLogsClient)
    qi_platform_collect.collect(case_dir, 0.0, 5.0)
    same(qi_platform.Client, before)
    with pytest.raises(ValueError, match="positive"):
        qi_platform_collect.collect(case_dir, 0.0, 5.0, logs_timeout=0.0)
