"""Contract of the Quandela record watch: the held file names every retained read of the held qpu:belenos state,
and the classifier separates held, changed, unscorable and missing records."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import qd_record_watch as watch

ROOT = Path(__file__).resolve().parents[2]
HELD = ROOT / "results/quandela/watch/qpu-belenos-held.json"
READS = (
    "results/quandela/runs/2026-10-25T184636Z-qpu_ascella-ascella_signed_coherence-job-02/platform-before/catalogue.json",
    "results/quandela/cases/teleportation_rehearsal/job-00/platform-read/catalogue.json",
    "results/quandela/runs/2026-10-26T025336Z-qpu_belenos-teleportation_rehearsal-job-00/platform-before/catalogue.json",
    "results/quandela/runs/2026-10-26T025336Z-qpu_belenos-teleportation_rehearsal-job-00/platform-after/catalogue.json",
)


def perfs_of(path: str) -> dict[str, object]:
    perfs: dict[str, object] = json.loads((ROOT / path).read_text(encoding="utf-8"))["processors"]["qpu:belenos"][
        "perfs"
    ]
    return perfs


@pytest.mark.parametrize("path", READS)
def test_held_digest_names_every_retained_read_of_the_held_state(path: str) -> None:
    held = json.loads(HELD.read_text(encoding="utf-8"))
    if watch.digest(perfs_of(path)) != held["perfs_sha256"]:
        raise AssertionError(f"{path} departs from the held state")
    if held["figures"] != {"HOM (%)": 83.8, "g2 (%)": 16.7, "Transmittance (%)": 0.05}:
        raise AssertionError(held["figures"])


def test_a_refreshing_read_departs_from_the_held_state() -> None:
    held = json.loads(HELD.read_text(encoding="utf-8"))
    anchor = (
        "results/quandela/runs/2026-10-24T153028Z-qpu_ascella-ascella_signed_coherence-job-01/platform-after/"
        "catalogue.json"
    )
    record = {"status": "available", "perfs": perfs_of(anchor)}
    if watch.classify(record, held) != "changed":
        raise AssertionError("the 2026-10-24 read classifies as held")


def test_the_maintenance_record_is_unscorable_and_keeps_the_watch_armed() -> None:
    held = json.loads(HELD.read_text(encoding="utf-8"))
    read = ROOT / "docs/evidence/quandela/live-processor-qpu-belenos-2026-10-26T12-58-09Z.json"
    record = json.loads(read.read_text(encoding="utf-8"))["record"]
    report = watch.check(held, lambda _platform: record, watch.model_at)
    if report["state"] != "unscorable" or "emission_probability * g2" not in report["model_error"]:
        raise AssertionError(report)
    if report["figures"]["g2 (%)"] != 66.7 or "model" in report:
        raise AssertionError(report)


def test_self_test_passes() -> None:
    if watch.self_test() != 0:
        raise AssertionError("the self-test failed")


def test_held_file_takes_the_catalogue_time_unless_an_earlier_read_is_named(tmp_path: Path) -> None:
    catalogue = ROOT / READS[-1]
    out = tmp_path / "held.json"
    watch.write_held(catalogue, "qpu:belenos", out)
    retrieved = json.loads(catalogue.read_text(encoding="utf-8"))["retrieved_utc"]
    if json.loads(out.read_text(encoding="utf-8"))["first_seen_utc"] != retrieved:
        raise AssertionError("the held file ignores the catalogue's retrieval time")
    watch.write_held(catalogue, "qpu:belenos", out, "2026-10-25T18:47:04+00:00")
    if json.loads(out.read_text(encoding="utf-8"))["first_seen_utc"] != "2026-10-25T18:47:04+00:00":
        raise AssertionError("the held file ignores --first-seen")


def test_model_at_matches_the_live_model_on_one_snapshot(monkeypatch: pytest.MonkeyPatch) -> None:
    import qd_platform
    import qd_teleportation_rehearsal as rehearsal

    perfs = perfs_of(READS[-1])
    monkeypatch.setattr(qd_platform, "get", lambda route, auth=True: {"perfs": perfs})
    if rehearsal.live_model() != rehearsal.model_at(perfs):
        raise AssertionError("live_model and model_at differ on the same perfs object")


MAINTENANCE_READ = ROOT / "docs/evidence/quandela/live-processor-qpu-belenos-2026-10-26T12-58-09Z.json"
BOOKING = ROOT / "results/quandela/watch/qpu-belenos-booking.json"


def maintenance_row() -> dict[str, object]:
    explorer = json.loads(MAINTENANCE_READ.read_text(encoding="utf-8"))["explorer"]
    window = {name: explorer["maintenance"].get(name) for name in watch.BOOKING_FIELDS}
    return {"status": explorer["status"], "maintenance": window}


def test_the_booking_file_names_the_retained_maintenance_window() -> None:
    booking = json.loads(BOOKING.read_text(encoding="utf-8"))
    window = maintenance_row()["maintenance"]
    if not isinstance(window, dict):
        raise AssertionError("the retained read lists no maintenance window")
    if (booking["start_time"], booking["end_time"]) != (window["start_time"], window["end_time"]):
        raise AssertionError(f"{booking} departs from the retained window {window}")
    if booking["source"] != MAINTENANCE_READ.relative_to(ROOT).as_posix():
        raise AssertionError(booking["source"])


def window_with(**fields: object) -> dict[str, object]:
    row = maintenance_row()
    window = row["maintenance"]
    if not isinstance(window, dict):
        raise AssertionError("the retained read lists no maintenance window")
    return {**row, "maintenance": {**window, **fields}}


@pytest.mark.parametrize(
    ("row", "now", "key"),
    [
        (maintenance_row(), "2026-10-26T12:58:09+00:00", None),
        (maintenance_row(), "2026-10-29T11:29:59+00:00", None),
        (maintenance_row(), "2026-10-29T11:30:00+00:00", "overran:2026-10-26T08:30:00Z:2026-10-29T11:30:00Z"),
        (window_with(maintenance_ended=True), "2026-10-29T09:00:00+00:00", "ended:2026-10-26T08:30:00Z"),
        ({"status": "available", "maintenance": None}, "2026-10-29T12:41:00+00:00", "ended:2026-10-26T08:30:00Z"),
        (
            window_with(start_time="2026-11-05T08:30:00Z", end_time="2026-11-05T12:00:00Z", maintenance_started=False),
            "2026-10-29T12:41:00+00:00",
            "ended:2026-10-26T08:30:00Z",
        ),
        ({**maintenance_row(), "status": "available"}, "2026-10-28T10:41:00+00:00", "ended:2026-10-26T08:30:00Z"),
        (
            window_with(end_time="2026-10-30T11:30:00Z"),
            "2026-10-29T12:41:00+00:00",
            "moved:2026-10-26T08:30:00Z:2026-10-30T11:30:00Z",
        ),
        (
            window_with(end_time="2026-10-30T11:30:00Z"),
            "2026-10-30T12:41:00+00:00",
            "overran:2026-10-26T08:30:00Z:2026-10-30T11:30:00Z",
        ),
    ],
)
def test_booking_events_key_on_the_window_and_never_on_the_read_time(
    row: dict[str, object], now: str, key: str | None
) -> None:
    booking = json.loads(BOOKING.read_text(encoding="utf-8"))
    event = watch.booking_event(booking, row, watch.utc(now))
    if (event and event["key"]) != key:
        raise AssertionError(f"{row} at {now} gives {event}, expected {key}")


def test_a_booking_comment_carries_its_marker_and_the_record_class() -> None:
    held = json.loads(HELD.read_text(encoding="utf-8"))
    record = json.loads(MAINTENANCE_READ.read_text(encoding="utf-8"))["record"]
    report = watch.check(held, lambda _platform: record, watch.model_at)
    booking = json.loads(BOOKING.read_text(encoding="utf-8"))
    watch.add_booking(
        report, booking, lambda _platform: window_with(maintenance_ended=True), watch.utc(booking["end_time"])
    )
    body = watch.booking_summary(report)
    if not body.startswith("<!-- qd-record-watch:booking:ended:2026-10-26T08:30:00Z -->"):
        raise AssertionError(body)
    for phrase in ("ended at the read", "`unscorable`", "g2 (%) 66.7", "job-01 stays held"):
        if phrase not in body:
            raise AssertionError(f"the booking comment omits {phrase!r}")


def test_an_explorer_failure_keeps_the_record_classification() -> None:
    held = json.loads(HELD.read_text(encoding="utf-8"))
    report = watch.check(held, lambda _platform: {"status": "available"}, watch.model_at)

    def broken(_platform: str) -> dict[str, object]:
        raise OSError("explorer unreachable")

    watch.add_booking(
        report, json.loads(BOOKING.read_text(encoding="utf-8")), broken, watch.utc("2026-10-29T12:41:00Z")
    )
    if report["state"] != "missing" or "explorer unreachable" not in report["booking"]["error"]:
        raise AssertionError(report)
