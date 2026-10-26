"""Watch a Quandela processor record for the end of a held calibration state, read-only.

The qpu:belenos performance record held one state from 2026-10-25 18:47 UTC
(docs/notes/quandela/calibration.md, "Belenos read of 2026-10-25 19:04 UTC"), while on 2026-10-24 it changed at
every two-hourly read. A held file names that state by the sha256 of its canonical perfs object. `check` reads the
live record through qd_platform.get and classifies it:

- held: the perfs object hashes to the held digest;
- missing: the record carries no perfs object or lacks a figure the rehearsal model reads;
- changed: any other perfs object. The noise model of qd_teleportation_rehearsal.live_model then scores the
  rehearsal at the live figures, which tells whether job-01's live gate (F* = 0.86) could admit it.

Every class also records the record's status. The report lands in --report as JSON beside a Markdown summary
(--summary) for the issue the workflow .github/workflows/quandela-record-watch.yml opens on a change. Nothing is
submitted, staged or planned.

Usage:
  "$PYTHON" scripts/qd_record_watch.py held CATALOGUE PLATFORM --out HELD
  "$PYTHON" scripts/qd_record_watch.py check HELD --report REPORT --summary SUMMARY
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
            f"which {verdict} F* = {model['mean_score']}.",
        ]
    lines += [
        "",
        "A run on the recovered chip is plan step `recovered-chip-rehearsal` (job-01): new QRNG compilation seeds and "
        "a written case quoting this record, approved by the owner before any submission. This workflow disabled "
        "itself after opening the issue.",
    ]
    return "\n".join(lines) + "\n"


def check(
    held: Mapping[str, Any],
    read: Callable[[str], Mapping[str, Any]],
    model: Callable[[], Mapping[str, Any]],
) -> dict[str, Any]:
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
        report["model"] = dict(model())
    return report


def live_read(platform: str) -> Mapping[str, Any]:
    from qd_platform import get, platform_route, scrub

    answer: Mapping[str, Any] = scrub(get(platform_route(platform)))
    return answer


def live_model() -> Mapping[str, Any]:
    from qd_teleportation_rehearsal import live_model as rehearsal_model

    model: Mapping[str, Any] = rehearsal_model()
    return model


def write_held(catalogue: Path, platform: str, out: Path) -> int:
    """Name a retained catalogue's processor record as the held state."""
    data = json.loads(catalogue.read_text(encoding="utf-8"))
    perfs = data["processors"][platform]["perfs"]
    held: dict[str, Any] = {
        "schema": SCHEMA,
        "platform": platform,
        "perfs_sha256": digest(perfs),
        "figures": figures(perfs),
        "first_seen_utc": "2026-10-25T18:47:04+00:00",
        "source": catalogue.relative_to(ROOT).as_posix(),
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(held, indent=1) + "\n", encoding="utf-8")
    print(f"{out.relative_to(ROOT)}: {platform} held at {held['perfs_sha256'][:12]}")
    return 0


def run_check(held_path: Path, report_path: Path, summary_path: Path) -> int:
    held = json.loads(held_path.read_text(encoding="utf-8"))
    report = check(held, live_read, live_model)
    report_path.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    if report["state"] == "changed":
        summary_path.write_text(summary(report), encoding="utf-8")
    print(f"{report['platform']} {report['status']}: {report['state']} {report['figures']}")
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
    )
    for record, want in cases:
        calls: list[int] = []

        def scored(calls: list[int] = calls) -> Mapping[str, Any]:
            calls.append(1)
            return model

        def read(_name: str, record: Mapping[str, Any] = record) -> Mapping[str, Any]:
            return record

        report = check(held, read, scored)
        if report["state"] != want or bool(calls) != (want == "changed"):
            raise SystemExit(f"self-test: {record} read {report['state']}, expected {want}")
        if want == "changed" and "reaches F* = 0.86" not in summary(report):
            raise SystemExit("self-test: the summary omits the model verdict")
    print("qd_record_watch self-test: held, changed and missing records classify; the model runs only on a change")
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
    checked = commands.add_parser("check")
    checked.add_argument("held", type=Path)
    checked.add_argument("--report", type=Path, required=True)
    checked.add_argument("--summary", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "held":
        return write_held(args.catalogue.resolve(), args.platform, args.out.resolve())
    return run_check(args.held, args.report, args.summary)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
