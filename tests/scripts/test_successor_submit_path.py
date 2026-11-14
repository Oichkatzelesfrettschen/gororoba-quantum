"""qd_platform.submit reaches its pre-POST checkpoint for each platform a successor request admits, and no other."""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import uuid
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import ascella_predecessor_acquisition_case as ascella
import bdsc_cases
import bdsc_diagnostic as diag
import bdsc_diagnostic_acquisition_case as belenos
import pytest
import qd_platform as qd

from qd_records import RecordError

ROOT = belenos.ROOT
CASES = ("sim:ascella", "qpu:ascella", "sim:belenos", "qpu:belenos")
# max_credits, expected seconds and the largest iteration's max_shots of each family's written case.
BUDGET = {"ascella": (1.032768, 40.0, 32768), "belenos": (1.08, 176.16, diag.MAX_SHOTS)}


class PostReached(Exception):
    """Raised in place of the POST of /api/jobs, so no request leaves the process."""


@pytest.fixture(scope="module")
def draw_directory() -> Iterator[Path]:
    # The QRNG record of a drawn build must sit inside the repository, so it goes under the ignored docs/local.
    scratch = ROOT / "docs/local"
    scratch.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=scratch) as directory:
        yield Path(directory)


def family(platform: str) -> str:
    return platform.split(":")[1]


def case_directory(tmp_path: Path, platform: str, draw_directory: Path) -> Path:
    """A fresh copy of the platform's job directory (b1-j1 for Belenos): submit writes into it."""
    target = tmp_path / "case"
    if family(platform) == "ascella":
        ascella.original.publish_case(target, ascella.documents(platform))
        return target
    tree = draw_directory / platform.replace(":", "-")
    if not tree.exists():
        draw = draw_directory / "draw.json"
        if not draw.exists():
            bdsc_cases.synthetic_draw(draw_directory, diag.DRAW_VALUES // 2)
        belenos.write(tree, platform, draw)
    shutil.copytree(tree / "b1-j1", target)
    return target


def mock_provider(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, platform: str, running: int = 0, queued: int = 0
) -> None:
    """Replace every provider read and the POST with local stand-ins; the case, source and admission checks stay."""
    simulator = platform.startswith("sim:")
    body = {"process_id": str(uuid.uuid4()), "platform_name": platform, "payload": {"command": "sample_count"}}
    row = {
        "name": platform,
        "status": "available",
        "max_duration": 300,
        "price_per_shot": 0.0 if simulator else 1e-6,
        "type": "sim" if simulator else "qpu",
    }

    def get(route: str, auth: bool = True) -> Any:
        return [] if route == "/api/tokens/usage/report" else {"status": "available", "perfs": {}}

    def request(*args: Any, **kwargs: Any) -> Any:
        raise PostReached

    monkeypatch.setenv(qd.TOKEN_ENV, str(tmp_path / "token"))
    monkeypatch.setattr(qd, "explorer_row", lambda name: dict(row))
    monkeypatch.setattr(qd, "get", get)
    monkeypatch.setattr(qd, "request", request)
    monkeypatch.setattr(
        qd,
        "availability",
        lambda: {
            "max_concurrent_jobs": 1,
            "max_jobs_in_queue": 1,
            "num_concurrent_jobs": running,
            "num_jobs_in_queue": queued,
        },
    )
    monkeypatch.setattr(qd, "hom_warning", lambda *args: None)
    monkeypatch.setattr(
        qd,
        "payload",
        lambda *args: {
            "body": json.loads(json.dumps(body)),
            "estimated_shots": 1,
            "versions": {},
            "payload_version_basis": "mock",
            "estimate_perfs": {},
        },
    )


def arguments(platform: str) -> tuple[float, float, float]:
    credits, seconds, _ = BUDGET[family(platform)]
    return credits, seconds, 1.0


@pytest.mark.parametrize("platform", CASES)
def test_submit_reaches_the_checkpoint_for_each_admitted_platform(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, draw_directory: Path, platform: str
) -> None:
    case = case_directory(tmp_path, platform, draw_directory)
    mock_provider(monkeypatch, tmp_path, platform, running=1)
    credits, seconds, per_job = arguments(platform)
    extra: dict[str, Any] = {}
    if family(platform) == "ascella":
        packet = tmp_path / "review.json"
        qd.prepare_acquisition_review(case, platform, credits, seconds, per_job, (), packet)
        extra = {
            "reviewed_packet": packet,
            "reviewed_sha256": hashlib.sha256(packet.read_bytes()).hexdigest(),
        }
    with pytest.raises(PostReached):
        qd.submit(case, platform, "mocked approval", credits, seconds, per_job, **extra)
    state = json.loads((case / "submission-state.json").read_bytes())
    if state["phase"] != "post_outcome_unknown" or state["platform"] != platform:
        raise AssertionError(f"the checkpoint reads {state['phase']} on {state['platform']}")
    if not (case / "job-body.json").is_file():
        raise AssertionError("the body did not precede the POST")


@pytest.mark.parametrize("platform", CASES)
def test_submit_refuses_a_platform_outside_the_request(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, draw_directory: Path, platform: str
) -> None:
    case = case_directory(tmp_path, platform, draw_directory)
    mock_provider(monkeypatch, tmp_path, platform)
    credits, seconds, per_job = arguments(platform)
    others = [other for other in (*CASES, "sim:slos") if other != platform]
    extra: dict[str, Any] = {}
    if family(platform) == "ascella":
        extra = {"reviewed_packet": tmp_path / "unused.json", "reviewed_sha256": "0" * 64}
    for other in others:
        with pytest.raises(qd.PlatformError, match="admits"):
            qd.submit(case, other, "mocked approval", credits, seconds, per_job, **extra)
    if any((case / name).exists() for name in ("submission-state.json", "job-body.json")):
        raise AssertionError("a refused platform left a checkpoint")


def test_submit_refuses_a_belenos_case_whose_bound_sources_changed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, draw_directory: Path
) -> None:
    case = case_directory(tmp_path, "sim:belenos", draw_directory)
    mock_provider(monkeypatch, tmp_path, "sim:belenos")
    manifest = json.loads((case / "cases.json").read_bytes())
    manifest["successor_sources"]["scripts/bdsc_diagnostic.py"] = "0" * 64
    (case / "cases.json").write_text(json.dumps(manifest, indent=1) + "\n")
    credits, seconds, per_job = arguments("sim:belenos")
    with pytest.raises(qd.PlatformError, match="reviewed source changed: scripts/bdsc_diagnostic.py"):
        qd.submit(case, "sim:belenos", "mocked approval", credits, seconds, per_job)


@pytest.mark.parametrize("platform", CASES)
def test_a_successor_case_queues_behind_the_running_job_on_every_platform(
    tmp_path: Path, draw_directory: Path, platform: str
) -> None:
    manifest = json.loads((case_directory(tmp_path, platform, draw_directory) / "cases.json").read_bytes())
    busy = {"max_concurrent_jobs": 1, "max_jobs_in_queue": 1, "num_concurrent_jobs": 1, "num_jobs_in_queue": 0}
    qd.require_token_capacity(manifest, busy)
    with pytest.raises(qd.PlatformError, match="no available queue slot"):
        qd.require_token_capacity(manifest, {**busy, "num_jobs_in_queue": 1})
    with pytest.raises(qd.PlatformError, match="integer"):
        qd.require_token_capacity(manifest, {**busy, "max_jobs_in_queue": None})


def test_a_case_without_bound_successor_sources_still_needs_an_idle_token() -> None:
    busy = {"max_concurrent_jobs": 1, "max_jobs_in_queue": 1, "num_concurrent_jobs": 1, "num_jobs_in_queue": 0}
    for manifest in ({"family": "bdsc", "job": "diagnostic"}, {"family": "ascella_predecessor", "job": "retained"}):
        with pytest.raises(qd.PlatformError, match="running or queued"):
            qd.require_token_capacity(manifest, busy)


@pytest.mark.parametrize("platform", CASES)
def test_submit_refuses_a_successor_case_when_the_token_queue_is_full(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, draw_directory: Path, platform: str
) -> None:
    case = case_directory(tmp_path, platform, draw_directory)
    mock_provider(monkeypatch, tmp_path, platform, running=1)
    credits, seconds, per_job = arguments(platform)
    extra: dict[str, Any] = {}
    if family(platform) == "ascella":
        packet = tmp_path / "review.json"
        qd.prepare_acquisition_review(case, platform, credits, seconds, per_job, (), packet)
        extra = {
            "reviewed_packet": packet,
            "reviewed_sha256": hashlib.sha256(packet.read_bytes()).hexdigest(),
        }
    mock_provider(monkeypatch, tmp_path, platform, running=1, queued=1)
    with pytest.raises((qd.PlatformError, RecordError), match="no available queue slot"):
        qd.submit(case, platform, "mocked approval", credits, seconds, per_job, **extra)
    if any((case / name).exists() for name in ("submission-state.json", "job-body.json")):
        raise AssertionError("a refused submission left a checkpoint")
