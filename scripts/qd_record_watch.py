"""Watch a Quandela processor record for the end of a held calibration state, read-only.

The qpu:belenos performance record held one state from 2026-10-25 18:47 UTC
(docs/notes/quandela/calibration.md, "Belenos read of 2026-10-25 19:04 UTC"), while on 2026-10-24 it changed at
every two-hourly read. A held file names that state by the sha256 of its canonical perfs object. `check` reads the
live record through qd_platform.get and classifies it:

- held: the perfs object hashes to the held digest;
- missing: the record carries no perfs object or lacks a figure the rehearsal model reads;
- changed: any other perfs object. The noise model of qd_teleportation_rehearsal.live_model then scores the
  rehearsal at the live figures against job-00's F* = 0.86, the watch's trigger. Job-01 is a descriptive
  acquisition preregistered at its own fresh read, prepared whenever its modeled seconds fit max_duration;
- unscorable: any other perfs object whose figures the model rejects with ValueError, as Perceval's source model
  does when emission_probability * g2 exceeds 0.5 (the maintenance record of 2026-10-26 reads g2 66.7 %). The report
  carries the error, and the watch goes on to the next read, so a later scorable record still reports a change.

Every class also records the record's status. The report lands in --report as JSON beside a Markdown summary
(--summary) for the issue the workflow .github/workflows/quandela-record-watch.yml opens on a change. Nothing is
submitted, staged or planned.

With --booking, a booking file names one maintenance window the service published (its explorer row's start_time and
end_time), and the same run reads the platform's row of the public explorer after classifying the record.
`booking_event` turns that row into at most one event per read:

- ended: the row carries no maintenance block, books another window, sets maintenance_ended, or reports a status
  other than maintenance;
- overran: the booking still runs at or after its listed end_time;
- moved: the listed end_time differs from the booked one and has not passed.

Each event has a key built from the window's start_time, its kind and the listed end_time, never from the read time,
so the workflow posts each event once (--booking-summary holds that comment, with the record's class at the same
read). An explorer failure lands in the report as booking.error and leaves the record classification intact.

Usage:
  "$PYTHON" scripts/qd_record_watch.py held CATALOGUE PLATFORM --out HELD [--first-seen UTC]
  "$PYTHON" scripts/qd_record_watch.py check HELD --report REPORT --summary SUMMARY
      [--booking BOOKING --booking-summary BOOKING_SUMMARY]
  "$PYTHON" scripts/qd_record_watch.py --self-test
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Callable, Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

SCHEMA = "qd-record-watch-v1"
FIGURES = ("HOM (%)", "g2 (%)", "Transmittance (%)", "Transmission per mode (%)")
# The explorer row's maintenance fields that describe the window; its staff and booking identifiers stay out.
BOOKING_FIELDS = (
    "maintenance_title",
    "start_time",
    "end_time",
    "maintenance_started",
    "maintenance_ended",
    "time_zone",
)


def digest(perfs: Mapping[str, Any]) -> str:
    """sha256 of the perfs object as sorted, compact JSON."""
    return hashlib.sha256(json.dumps(perfs, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def classify(record: Mapping[str, Any], held: Mapping[str, Any]) -> str:
    perfs = record.get("perfs")
    if not isinstance(perfs, dict) or any(name not in perfs for name in FIGURES):
        return "missing"
    return "held" if digest(perfs) == held["perfs_sha256"] else "changed"


def figures(perfs: Mapping[str, Any]) -> dict[str, Any]:
    return {name: perfs.get(name) for name in FIGURES[:3]}


def summary(report: Mapping[str, Any]) -> str:
    """The Markdown body of the change issue."""
    lines = [
        f"The `{report['platform']}` performance record left the held state of {report['held_first_seen_utc']} "
        f"at the read of {report['read_utc']} (status `{report['status']}`).",
        "",
        "| | held | live |",
        "|---|---|---|",
    ]
    for name, value in report["figures"].items():
        lines.append(f"| {name} | {report['held_figures'].get(name)} | {value} |")
    model = report.get("model")
    if model is not None:
        verdict = "reaches" if model["inside_justified_range"] else "falls below"
        lines += [
            "",
            f"The rehearsal noise model at the live figures gives pooled fidelity {model['pooled_fidelity']:.4f}, "
            f"which {verdict} job-00's F* = {model['mean_score']}. That F* triggers this comment; job-01 is a "
            "descriptive acquisition preregistered at its own fresh read, prepared whenever its modeled seconds fit "
            "the 300 s max_duration.",
        ]
    lines += [
        "",
        "A run on the recovered chip is plan step `recovered-chip-rehearsal` (job-01): a fresh snapshot, "
        "`qd_teleportation_rehearsal.py --prepare job-01` (its compilation seeds are registered), and a written case "
        "quoting that read and its derived credits and seconds, approved by the owner before any submission. This "
        "workflow disabled itself after opening the issue. The procedure is [belenos-recovery-watch.md]"
        "(../blob/main/docs/archive/handoffs/belenos-recovery-watch.md).",
    ]
    return "\n".join(lines) + "\n"


def check(
    held: Mapping[str, Any],
    read: Callable[[str], Mapping[str, Any]],
    model: Callable[[Mapping[str, Any]], Mapping[str, Any]],
) -> dict[str, Any]:
    """Read the record once and classify it; a changed record's model scores that same perfs object."""
    record = read(held["platform"])
    state = classify(record, held)
    raw = record.get("perfs")
    perfs: Mapping[str, Any] = raw if isinstance(raw, dict) else {}
    report: dict[str, Any] = {
        "schema": SCHEMA,
        "platform": held["platform"],
        "read_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "status": record.get("status"),
        "state": state,
        "held_perfs_sha256": held["perfs_sha256"],
        "held_first_seen_utc": held["first_seen_utc"],
        "held_figures": held["figures"],
        "perfs_sha256": digest(perfs) if perfs else None,
        "figures": figures(perfs),
    }
    if state == "changed":
        try:
            report["model"] = dict(model(perfs))
        except ValueError as error:
            report["state"], report["model_error"] = "unscorable", str(error)
    return report


def live_read(platform: str) -> Mapping[str, Any]:
    from qd_platform import get, platform_route, scrub

    answer: Mapping[str, Any] = scrub(get(platform_route(platform)))
    return answer


def model_at(perfs: Mapping[str, Any]) -> Mapping[str, Any]:
    from qd_teleportation_rehearsal import model_at as rehearsal_model

    model: Mapping[str, Any] = rehearsal_model(perfs)
    return model


def explorer_row(platform: str) -> dict[str, Any]:
    """The platform's row of the public explorer: its status and the maintenance window it lists."""
    from qd_platform import get

    rows = get("/api/platforms/public/explorer", auth=False)
    row = next(item for item in rows if isinstance(item, dict) and item.get("name") == platform)
    window = row.get("maintenance")
    return {
        "status": row.get("status"),
        "maintenance": {name: window.get(name) for name in BOOKING_FIELDS} if isinstance(window, dict) else None,
    }


def utc(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def booking_event(booking: Mapping[str, Any], row: Mapping[str, Any], now: datetime) -> dict[str, str] | None:
    """The one event an explorer row shows for the booked window at `now`, or None while it runs as booked."""
    start = booking["start_time"]
    window = row.get("maintenance")
    if not isinstance(window, dict):
        reason = "the explorer row lists no maintenance window"
    elif window.get("start_time") != start:
        reason = f"the explorer row lists another window, from {window.get('start_time')} to {window.get('end_time')}"
    elif window.get("maintenance_ended"):
        reason = "the explorer row sets maintenance_ended"
    elif row.get("status") != "maintenance":
        reason = f"the explorer status reads {row.get('status')}"
    else:
        end = str(window.get("end_time"))
        if now >= utc(end):
            return {"kind": "overran", "key": f"overran:{start}:{end}", "reason": f"the window runs past {end}"}
        if end != booking["end_time"]:
            return {"kind": "moved", "key": f"moved:{start}:{end}", "reason": f"the window now ends at {end}"}
        return None
    return {"kind": "ended", "key": f"ended:{start}", "reason": reason}


def booking_summary(report: Mapping[str, Any]) -> str:
    """The Markdown comment for a booking event, led by the marker the workflow deduplicates on."""
    booking = report["booking"]
    event, booked, row = booking["event"], booking["booked"], booking["explorer"]
    window = row.get("maintenance") or {}
    headline = {
        "ended": "ended",
        "overran": "is running past its listed end",
        "moved": "moved its end",
    }[event["kind"]]
    lines = [
        f"<!-- qd-record-watch:booking:{event['key']} -->",
        f"The `{report['platform']}` maintenance window booked from {booked['start_time']} to {booked['end_time']} "
        f"{headline} at the read of {report['read_utc']}: {event['reason']}.",
        "",
        f"Explorer status `{row.get('status')}`; listed window: {window.get('maintenance_title')} from "
        f"{window.get('start_time')} to {window.get('end_time')}, started {window.get('maintenance_started')}, "
        f"ended {window.get('maintenance_ended')}.",
        "",
        f"The performance record at the same read is `{report['state']}` (status `{report['status']}`) with "
        + ", ".join(f"{name} {value}" for name, value in report["figures"].items())
        + ".",
    ]
    model = report.get("model")
    if model is not None:
        verdict = "reaches" if model["inside_justified_range"] else "falls below"
        lines.append(
            f"The rehearsal noise model gives pooled fidelity {model['pooled_fidelity']:.4f}, which {verdict} "
            f"job-00's F* = {model['mean_score']}, the watch's trigger; the change comment of this run carries the "
            "job-01 decision."
        )
    elif report["state"] == "unscorable":
        lines.append(
            f"The rehearsal model rejects these figures ({report['model_error']}), so job-01 stays held and the watch "
            "stays armed for a scorable record."
        )
    elif report["state"] == "held":
        lines.append("The record still carries the held state, so job-01 stays held and the watch stays armed.")
    lines += [
        "",
        "The procedure for each outcome is [belenos-recovery-watch.md]"
        "(../blob/main/docs/archive/handoffs/belenos-recovery-watch.md).",
    ]
    return "\n".join(lines) + "\n"


def write_held(catalogue: Path, platform: str, out: Path, first_seen: str | None = None) -> int:
    """Name a retained catalogue's processor record as the held state, first seen at `first_seen` (an earlier retained
    read of the same state) or else at the catalogue's retrieved_utc."""
    data = json.loads(catalogue.read_text(encoding="utf-8"))
    perfs = data["processors"][platform]["perfs"]
    held: dict[str, Any] = {
        "schema": SCHEMA,
        "platform": platform,
        "perfs_sha256": digest(perfs),
        "figures": figures(perfs),
        "first_seen_utc": first_seen or data["retrieved_utc"],
        "source": catalogue.relative_to(ROOT).as_posix(),
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(held, indent=1) + "\n", encoding="utf-8")
    print(f"{out}: {platform} held at {held['perfs_sha256'][:12]} since {held['first_seen_utc']}")
    return 0


def add_booking(
    report: dict[str, Any],
    booking: Mapping[str, Any],
    read: Callable[[str], Mapping[str, Any]],
    now: datetime,
) -> None:
    """Attach the explorer read and its booking event to a classified report; a failed read records its error."""
    try:
        row = read(booking["platform"])
    except Exception as error:  # noqa: BLE001 - an explorer failure leaves the record classification standing
        report["booking"] = {"booked": dict(booking), "error": repr(error)}
        return
    report["booking"] = {"booked": dict(booking), "explorer": dict(row), "event": booking_event(booking, row, now)}


def run_check(
    held_path: Path,
    report_path: Path,
    summary_path: Path,
    booking_path: Path | None = None,
    booking_summary_path: Path | None = None,
) -> int:
    held = json.loads(held_path.read_text(encoding="utf-8"))
    report = check(held, live_read, model_at)
    if booking_path is not None:
        add_booking(report, json.loads(booking_path.read_text(encoding="utf-8")), explorer_row, datetime.now(UTC))
    report_path.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    if report["state"] == "changed":
        summary_path.write_text(summary(report), encoding="utf-8")
    print(f"{report['platform']} {report['status']}: {report['state']} {report['figures']}")
    if report["state"] == "unscorable":
        print(f"the rehearsal model rejects the changed figures: {report['model_error']}")
    booking = report.get("booking")
    if booking is not None and "error" in booking:
        print(f"explorer read failed: {booking['error']}")
    elif booking is not None:
        event = booking["event"]
        print(f"booking {booking['booked']['start_time']}: {event['key'] if event else 'running as booked'}")
        if event is not None and booking_summary_path is not None:
            booking_summary_path.write_text(booking_summary(report), encoding="utf-8")
    return 0


def self_test() -> int:
    perfs = {"HOM (%)": 83.8, "g2 (%)": 16.7, "Transmittance (%)": 0.05, "Transmission per mode (%)": {"t_out": [1.0]}}
    held = {
        "platform": "qpu:belenos",
        "perfs_sha256": digest(perfs),
        "figures": figures(perfs),
        "first_seen_utc": "2026-10-25T18:47:04+00:00",
    }
    if digest(dict(reversed(list(perfs.items())))) != digest(perfs):
        raise SystemExit("self-test: the digest depends on key order")
    moved = {**perfs, "g2 (%)": 1.1}
    model = {"pooled_fidelity": 0.87, "mean_score": 0.86, "inside_justified_range": True}
    cases: tuple[tuple[dict[str, Any], str], ...] = (
        ({"status": "available", "perfs": perfs}, "held"),
        ({"status": "maintenance", "perfs": perfs}, "held"),
        ({"status": "available", "perfs": moved}, "changed"),
        ({"status": "available"}, "missing"),
        ({"status": "available", "perfs": {"HOM (%)": 88.8}}, "missing"),
        ({"status": "maintenance", "perfs": {**perfs, "g2 (%)": 66.7}}, "unscorable"),
    )
    for record, want in cases:
        calls: list[int] = []

        def scored(
            seen: Mapping[str, Any], calls: list[int] = calls, record: Mapping[str, Any] = record
        ) -> Mapping[str, Any]:
            if seen != record.get("perfs"):
                raise SystemExit("self-test: the model scored another perfs object than the classified read")
            calls.append(1)
            if seen["g2 (%)"] == 66.7:
                raise ValueError("emission_probability * g2 higher than 0.5 can not be computed")
            return model

        def read(_name: str, record: Mapping[str, Any] = record) -> Mapping[str, Any]:
            return record

        report = check(held, read, scored)
        if report["state"] != want or bool(calls) != (want in ("changed", "unscorable")):
            raise SystemExit(f"self-test: {record} read {report['state']}, expected {want}")
        if want == "changed" and "reaches job-00's F* = 0.86" not in summary(report):
            raise SystemExit("self-test: the summary omits the model verdict")
        if want == "unscorable" and "model" in report:
            raise SystemExit("self-test: an unscorable record carries a model")
    print(
        "qd_record_watch self-test: held, changed, unscorable and missing records classify; the model runs only on "
        "a change"
    )
    return 0


def main(argv: list[str]) -> int:
    if argv == ["--self-test"]:
        return self_test()
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    held = commands.add_parser("held")
    held.add_argument("catalogue", type=Path)
    held.add_argument("platform")
    held.add_argument("--out", type=Path, required=True)
    held.add_argument("--first-seen", help="UTC time of an earlier retained read of the same state")
    checked = commands.add_parser("check")
    checked.add_argument("held", type=Path)
    checked.add_argument("--report", type=Path, required=True)
    checked.add_argument("--summary", type=Path, required=True)
    checked.add_argument("--booking", type=Path, help="booking file naming the maintenance window to watch")
    checked.add_argument("--booking-summary", type=Path, help="where a booking event's comment lands")
    args = parser.parse_args(argv)
    if args.command == "held":
        return write_held(args.catalogue.resolve(), args.platform, args.out.resolve(), args.first_seen)
    if (args.booking is None) != (args.booking_summary is None):
        parser.error("--booking and --booking-summary go together")
    return run_check(args.held, args.report, args.summary, args.booking, args.booking_summary)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
