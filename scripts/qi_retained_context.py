"""Dated per-qubit Tuna-17 figures and job timing from the repository's own retained Quantum Inspire runs.

The provider's per-qubit calibration series are withheld (docs/evidence/quantum_inspire/status-sources-2026-11-15),
so this summary gathers what the repository itself measured, each figure beside the run it comes from:

- per qubit, from results/quantum_inspire/readout_ringdown_tuna_17_device_context.json (written by
  qi_tuna17_device_context.py): the latest readout pair P(1|0) and P(1|1) with its run and wait, the implied T1
  with the two runs it compares, the idle detuning with its standard error, the Ramsey visibility at the map's two
  delays, and the largest coupler strength. The implied T1 carries that record's assumption: the whole P(1|1) drop
  is T1 decay during the wait, and readout fidelity is unchanged between the two runs.
- per backend and UTC day, from each retained run's results.json: the job count, the median and largest time from
  a job's creation to its finish, and the median execution time the provider reports.

Every figure is as of its run; none is a current calibration. The output holds no generation time, so --check
recomputes it and compares bytes.

Usage: "$PYTHON" scripts/qi_retained_context.py [--check] [--out PATH]
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import statistics
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = "qi-retained-context-v1"
CONTEXT = "results/quantum_inspire/readout_ringdown_tuna_17_device_context.json"
RUNS = "results/quantum_inspire/runs"
OUT = "docs/evidence/qi-status-context/retained-context.json"
SIGNIFICANT = 6


def _number(value: Any) -> Any:
    return float(f"{value:.{SIGNIFICANT}g}") if isinstance(value, float) else value


def run_utc(name: str) -> str:
    """The UTC instant a run directory's name begins with, such as 2026-10-16T221133Z."""
    stamp = Path(name).name.split("-")
    return datetime.datetime.strptime("-".join(stamp[:3]), "%Y-%m-%dT%H%M%SZ").replace(tzinfo=datetime.UTC).isoformat()


def qubits(context: dict[str, Any]) -> list[dict[str, Any]]:
    """One row per qubit of the device-context record, each figure with the run it comes from."""
    rows = []
    for name, entry in sorted(context["qubits"].items(), key=lambda item: int(item[0])):
        mapped = entry.get("coupler_map") or {}
        readout = entry.get("readout") or {}
        runs = readout.get("runs") or []
        implied = readout.get("implied_t1") or {}
        row: dict[str, Any] = {"qubit": int(name)}
        if runs:
            last = runs[-1]
            row["readout"] = {
                "run": last["run"],
                "utc": run_utc(last["run"]),
                "shots": last.get("shots"),
                "wait_before_readout_us": last.get("wait_before_readout_us"),
                "p1_given_0": _number(last.get("p1_given_0")),
                "p1_given_1": _number(last.get("p1_given_1")),
            }
        if implied.get("us") is not None:
            row["implied_t1"] = {
                "us": _number(implied["us"]),
                "wait_us": implied.get("wait_us"),
                "wait_run_utc": run_utc(implied["wait_run"]),
                "no_wait_run_utc": run_utc(implied["no_wait_run"]),
            }
        if mapped:
            row["coupler_map"] = {
                "detuning_hz": _number(mapped.get("omega_hz")),
                "detuning_se_hz": _number(mapped.get("omega_se_hz")),
                "visibility_delays_us": mapped.get("visibility_delays_us"),
                "visibility_zero_sector": [_number(value) for value in mapped.get("visibility_zero_sector") or []],
                "max_abs_j_hz": _number(mapped.get("max_abs_j_hz")),
                "couplers": len(mapped.get("couplers") or []),
            }
        rows.append(row)
    return rows


def _instant(text: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(text.replace("Z", "+00:00"))


def jobs(runs: Path) -> dict[str, list[dict[str, Any]]]:
    """Per backend and UTC day of job creation: counts, creation-to-finish seconds and reported execution seconds."""
    days: dict[str, dict[str, list[tuple[float, float, int]]]] = {}
    for run in sorted(runs.iterdir()) if runs.is_dir() else []:
        cases, results = run / "cases.json", run / "results.json"
        if not (cases.is_file() and results.is_file()):
            continue
        backend = str(json.loads(cases.read_text(encoding="utf-8")).get("backend"))
        for item in json.loads(results.read_text(encoding="utf-8")).get("jobs") or []:
            job = item.get("job") or {}
            if job.get("status") != "completed" or not job.get("created_on") or not job.get("finished_at"):
                continue
            created = _instant(job["created_on"])
            turnaround = (_instant(job["finished_at"]) - created).total_seconds()
            executed = sum(float(row.get("execution_time_in_seconds") or 0.0) for row in item.get("results") or [])
            shots = int(job.get("number_of_shots") or 0)
            days.setdefault(backend, {}).setdefault(created.date().isoformat(), []).append(
                (turnaround, executed, shots)
            )
    return {
        backend: [
            {
                "day": day,
                "jobs": len(rows),
                "shots": sum(row[2] for row in rows),
                "median_turnaround_seconds": _number(float(statistics.median(row[0] for row in rows))),
                "max_turnaround_seconds": _number(float(max(row[0] for row in rows))),
                "median_execution_seconds": _number(float(statistics.median(row[1] for row in rows))),
            }
            for day, rows in sorted(by_day.items())
        ]
        for backend, by_day in sorted(days.items())
    }


def summary(root: Path = ROOT) -> dict[str, Any]:
    source = root / CONTEXT
    text = source.read_bytes()
    context = json.loads(text)
    return {
        "schema": SCHEMA,
        "profile": context.get("profile"),
        "sources": {
            "device_context": CONTEXT,
            "device_context_sha256": hashlib.sha256(text).hexdigest(),
            "coupler_map_runs_utc": [run_utc(name) for name in (context.get("coupler_map") or {}).get("runs") or []],
            "job_runs": RUNS,
        },
        "implied_t1_assumption": "the whole P(1|1) drop between the no-wait and the wait run is T1 decay during the"
        " wait, and readout fidelity is unchanged between the two runs",
        "qubits": qubits(context),
        "jobs": jobs(root / RUNS),
    }


def render(root: Path = ROOT) -> str:
    return json.dumps(summary(root), indent=1, sort_keys=True) + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--check", action="store_true", help="recompute the summary and compare bytes")
    parser.add_argument("--out", type=Path, default=ROOT / OUT)
    args = parser.parse_args(argv)
    text = render()
    if args.check:
        if not args.out.is_file() or args.out.read_text(encoding="utf-8") != text:
            print(
                f"qi_retained_context: {args.out} differs from the retained runs; rerun without --check",
                file=sys.stderr,
            )
            return 1
        return 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
