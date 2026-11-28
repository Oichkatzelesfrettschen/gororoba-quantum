"""Carried chip architecture for seeded Belenos cases: plan admission when the live record omits specs.architecture,
and the collect-time coupler check (qd_platform.live_architecture, couplers_state, collect)."""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import qd_belenos_mesh as mesh  # noqa: E402
import qd_platform  # noqa: E402

import qd_records  # noqa: E402


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


CHIP = mesh.CHIP
OFFCONE = ROOT / "results/quandela/cases/belenos_offcone_mechanisms/job-00"
CATALOGUE = mesh.load_catalogue()
RETAINED = CATALOGUE["processors"][CHIP]["specs"]["architecture"]
OTHER = CATALOGUE["processors"]["qpu:ascella"]["specs"]["architecture"]


def live(blob: Any) -> dict[str, Any]:
    return {"status": "available", "specs": {"architecture": blob}}


def test_a_live_record_without_specs_architecture_is_admitted_on_the_carried_catalogue() -> None:
    expected = {
        "architecture_source": "carried",
        "architecture_catalogue_sha256": hashlib.sha256(mesh.CATALOGUE.read_bytes()).hexdigest(),
        "architecture_sha256": hashlib.sha256(RETAINED.encode()).hexdigest(),
        "architecture_observed_utc": CATALOGUE["architecture_observed_utc"][CHIP],
    }
    records: tuple[dict[str, Any], ...] = (
        {"specs": {}},
        {"specs": None},
        {},
        {"specs": {"architecture": None}},
        live(""),
    )
    for record in records:
        require(
            qd_platform.live_architecture(record, CHIP) == expected,
            "qd_platform.live_architecture(record, CHIP) == expected",
        )


def test_a_live_record_with_the_retained_couplers_keeps_the_comparison_and_names_its_source() -> None:
    got = qd_platform.live_architecture(live(RETAINED), CHIP)
    require(
        got is not None and got["architecture_source"] == "live",
        'got is not None and got["architecture_source"] == "live"',
    )


def test_a_live_blob_that_differs_refuses() -> None:
    with pytest.raises(qd_platform.PlatformError, match="differs from the retained catalogue"):
        qd_platform.live_architecture(live(OTHER), CHIP)


def test_another_platform_is_untouched() -> None:
    require(
        qd_platform.live_architecture({"specs": {}}, "sim:belenos") is None,
        'qd_platform.live_architecture({"specs": {}}, "sim:belenos") is None',
    )


def test_a_retained_catalogue_without_its_stamp_or_chip_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    for change in (
        lambda c: c["architecture_observed_utc"].pop(CHIP),
        lambda c: c["architecture_observed_utc"].update({CHIP: "yesterday"}),
        lambda c: c["processors"][CHIP]["specs"].pop("architecture"),
    ):
        catalogue = json.loads(json.dumps(CATALOGUE))
        change(catalogue)
        monkeypatch.setattr(mesh, "load_catalogue", lambda c=catalogue: c)
        with pytest.raises(qd_platform.PlatformError):
            qd_platform.live_architecture({"specs": {}}, CHIP)


def test_a_mesh_case_still_refuses_a_record_without_specs_architecture() -> None:
    with pytest.raises(qd_platform.PlatformError, match="no specs.architecture"):
        qd_platform.live_mesh({"specs": {}}, {"architecture": {}}, CHIP)


def submission_for(source: str = "carried") -> dict[str, Any]:
    return {"architecture_source": source, "architecture_sha256": hashlib.sha256(RETAINED.encode()).hexdigest()}


@pytest.mark.parametrize(
    ("record", "submission", "want"),
    [
        (live(RETAINED), submission_for(), "live-match"),
        (live(OTHER), submission_for(), "live-differ"),
        ({"specs": {}}, submission_for(), "unread"),
        ({"specs": {"architecture": None}}, submission_for("live"), "unread"),
        (live(RETAINED), {**submission_for(), "architecture_sha256": "0" * 64}, "unread"),
    ],
)
def test_couplers_state_branches(record: dict[str, Any], submission: dict[str, Any], want: str) -> None:
    state = qd_platform.couplers_state(submission, CHIP, lambda: record)
    require(state["couplers_checked"] == want, 'state["couplers_checked"] == want')
    require(
        state["architecture_source"] == submission["architecture_source"],
        'state["architecture_source"] == submission["architecture_source"]',
    )


def collect_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, record: dict[str, Any]) -> Path:
    case = tmp_path / "job-00"
    case.mkdir()
    for name in ("cases.json", "circuit.json"):
        shutil.copy(OFFCONE / name, case / name)
    manifest, _, digest = qd_platform.load_case(case)
    receipt = {
        "schema": qd_platform.SUBMISSION_SCHEMA,
        "cases_sha256": digest,
        "job_id": "job-a",
        "platform": CHIP,
        **submission_for(),
    }
    (case / "submission.json").write_text(json.dumps(receipt), encoding="utf-8")

    def request(method: str, route: str, auth: bool = True, body: Any = None, raw: bool = False) -> Any:
        if route.endswith("/status"):
            return {"status": "completed", "shots": 10}
        if route.endswith("/data"):
            return {"job_id": "job-a"}
        if route.endswith("/result"):
            return b"{}"
        if route == qd_platform.platform_route(CHIP):
            return record
        if route == "/api/tokens/usage/report":
            return []
        raise AssertionError(route)

    monkeypatch.setattr(qd_platform, "request", request)
    monkeypatch.setattr(qd_platform, "result_summary", lambda *a, **k: {"samples": 1})
    require(manifest["platforms"] == [CHIP], 'manifest["platforms"] == [CHIP]')
    return case


@pytest.mark.parametrize(("blob", "want"), [(RETAINED, "live-match"), (None, "unread")])
def test_collect_writes_couplers_checked(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, blob: str | None, want: str
) -> None:
    case = collect_fixture(tmp_path, monkeypatch, live(blob))
    collected = qd_platform.collect(case, 0.0, 5.0)
    require(
        collected["couplers_checked"] == want and collected["architecture_source"] == "carried",
        'collected["couplers_checked"] == want and collected["architecture_source"] == "carried"',
    )
    require(
        json.loads((case / "results.json").read_text(encoding="utf-8"))["couplers_checked"] == want,
        'json.loads((case / "results.json").read_text(encoding="utf-8"))["couplers_checked"] == want',
    )


def test_collect_fails_on_differing_live_couplers_after_retaining_the_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = collect_fixture(tmp_path, monkeypatch, live(OTHER))
    with pytest.raises(qd_platform.PlatformError, match="live-differ"):
        qd_platform.collect(case, 0.0, 5.0)
    require((case / "raw/result.json").read_bytes() == b"{}", '(case / "raw/result.json").read_bytes() == b"{}"')
    require(
        json.loads((case / "results.json").read_text(encoding="utf-8"))["couplers_checked"] == "live-differ",
        'json.loads((case / "results.json").read_text(encoding="utf-8"))["couplers_checked"] == "live-differ"',
    )
    with pytest.raises(qd_platform.PlatformError, match="live-differ"):
        qd_platform.collect(case, 0.0, 5.0)


def test_the_reader_refuses_live_differ_and_an_unchecked_carried_run() -> None:
    check = qd_records.check_couplers
    check("run", submission_for(), {"couplers_checked": "live-match"})
    check("run", submission_for(), {"couplers_checked": "unread"})
    check("run", {}, {})
    for collected in ({"couplers_checked": "live-differ"}, {}):
        with pytest.raises(qd_records.RecordError):
            check("run", submission_for(), collected)
