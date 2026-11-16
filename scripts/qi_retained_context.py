"""Dated per-qubit Tuna-17 figures and job timing from the repository's own retained Quantum Inspire runs.

The provider's per-qubit calibration series are withheld (docs/evidence/quantum_inspire/status-sources-2026-11-15),
so this summary gathers what the repository itself measured, each figure beside the run it comes from:

- per qubit, from results/quantum_inspire/readout_ringdown_tuna_17_device_context.json (written by
  qi_tuna17_device_context.py): the latest readout pair P(1|0) and P(1|1) with its run and wait, the implied T1
  with the two runs it compares, the idle detuning with its standard error, the Ramsey visibility at the map's two
  delays, and the largest coupler strength. The implied T1 carries that record's assumption: the whole P(1|1) drop
  is T1 decay during the wait, and readout fidelity is unchanged between the two runs.
- per qubit, from the analysis row of a characterization series
  (results/quantum_inspire/characterization_tuna_17_analysis.json, written by qi_tuna17_characterization_cases.py):
  the closing readout pair and the fitted T1 of the series. A series newer than the device-context row replaces the
  row's readout and implied_t1 (the figures the dashboard shows), and the device-context readout stays in
  baseline_readout, which qi_tuna17_characterization_cases.py reads as the retained row of its tolerance verdict.
  The fitted T1 is a single-exponential fit to the corrected populations of the series' own delays and readout pair,
  not the implied T1's two-run difference.
- per backend and UTC day, from each retained run's results.json: the job count, the median and largest time from
  a job's creation to its finish, and the median execution time the provider reports.

Every figure is as of its run, dated by the earliest finish time of that run's jobs (a series directory's name
holds the series start, which can precede the shots by hours); none is a current calibration. Runs are the
directories qi_platform.run_directories() names, so a campaign's nested batches count. The output holds no
generation time, so --check recomputes it and compares bytes.

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

sys.path.insert(0, str(Path(__file__).resolve().parent))

from qi_platform import run_directories  # noqa: E402 - standard-library imports only; no SDK is loaded

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = "qi-retained-context-v1"
CONTEXT = "results/quantum_inspire/readout_ringdown_tuna_17_device_context.json"
RUNS = "results/quantum_inspire/runs"
OUT = "docs/evidence/qi-status-context/retained-context.json"
CHARACTERIZATION = "results/quantum_inspire/characterization_tuna_17_analysis.json"
# One wait cycle of the Tuna and Starmon-7 control stack (docs/notes/quantum_inspire/platform-facts.md).
CYCLE_US = 0.02
SIGNIFICANT = 6


def _number(value: Any) -> Any:
    return float(f"{value:.{SIGNIFICANT}g}") if isinstance(value, float) else value


def _instant(text: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(text.replace("Z", "+00:00"))


def run_utc(root: Path, run: str) -> str:
    """The earliest finish time among the jobs of a retained run, given by its repository path."""
    record = json.loads((root / run / "results.json").read_text(encoding="utf-8"))
    stamps = [
        entry["job"]["finished_at"] for entry in record.get("jobs") or [] if (entry.get("job") or {}).get("finished_at")
    ]
    if not stamps:
        raise SystemExit(f"qi_retained_context: {run} records no finished job")
    return min(_instant(stamp) for stamp in stamps).isoformat()


def characterization(root: Path) -> dict[int, dict[str, Any]]:
    """Qubit -> the series' closing readout pair and fitted T1, each with its run instant, or {} without an analysis."""
    path = root / CHARACTERIZATION
    if not path.is_file():
        return {}
    analysis = json.loads(path.read_text(encoding="utf-8"))
    manifests = {
        name: json.loads((root / RUNS / name / "cases.json").read_text(encoding="utf-8")) for name in analysis["runs"]
    }

    def kinds(name: str) -> set[str]:
        return {circuit["kind"] for circuit in manifests[name]["circuits"]}

    paired = [name for name in manifests if "readout" in kinds(name)]
    waited = [name for name in manifests if "t1" in kinds(name)]
    if not paired or not waited:
        return {}
    closing = f"{RUNS}/{paired[-1]}"
    longest = max(circuit.get("wait_cycles", 0) for name in waited for circuit in manifests[name]["circuits"])
    found: dict[int, dict[str, Any]] = {}
    for row in analysis["qubits"]:
        pair = row["readout"][-1]
        entry: dict[str, Any] = {
            "readout": {
                "run": closing,
                "utc": run_utc(root, closing),
                "shots": manifests[paired[-1]]["shots"],
                "wait_before_readout_us": 0.0,
                "p1_given_0": _number(pair["p1_given_0"]),
                "p1_given_1": _number(pair["p1_given_1"]),
            }
        }
        if "t1" in row:
            entry["implied_t1"] = {
                "us": _number(row["t1"]["us"]),
                "wait_us": _number(longest * CYCLE_US),
                "wait_run_utc": run_utc(root, f"{RUNS}/{waited[-1]}"),
                "no_wait_run_utc": run_utc(root, f"{RUNS}/{waited[0]}"),
                "fit_points": row["t1"]["points"],
            }
        found[row["qubit"]] = entry
    return found


def qubits(context: dict[str, Any], root: Path) -> list[dict[str, Any]]:
    """One row per qubit of the device-context record, each figure with the run it comes from."""
    rows = []
    series = characterization(root)
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
                "utc": run_utc(root, last["run"]),
                "shots": last.get("shots"),
                "wait_before_readout_us": last.get("wait_before_readout_us"),
                "p1_given_0": _number(last.get("p1_given_0")),
                "p1_given_1": _number(last.get("p1_given_1")),
            }
        if implied.get("us") is not None:
            row["implied_t1"] = {
                "us": _number(implied["us"]),
                "wait_us": implied.get("wait_us"),
                "wait_run_utc": run_utc(root, implied["wait_run"]),
                "no_wait_run_utc": run_utc(root, implied["no_wait_run"]),
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
        newer = series.get(int(name))
        if newer and (not row.get("readout") or _instant(newer["readout"]["utc"]) > _instant(row["readout"]["utc"])):
            if "readout" in row:
                row["baseline_readout"] = row["readout"]
            row["readout"] = newer["readout"]
            if "implied_t1" in newer:
                if "implied_t1" in row:
                    row["baseline_implied_t1"] = row["implied_t1"]
                row["implied_t1"] = newer["implied_t1"]
        rows.append(row)
    return rows


def jobs(runs: Path) -> dict[str, list[dict[str, Any]]]:
    """Per backend and UTC day of job creation: counts, creation-to-finish seconds and reported execution seconds."""
    days: dict[str, dict[str, list[tuple[float, float, int]]]] = {}
    for run in run_directories(runs):
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
    series = characterization(root)
    return {
        "schema": SCHEMA,
        "profile": context.get("profile"),
        "sources": {
            "device_context": CONTEXT,
            "device_context_sha256": hashlib.sha256(text).hexdigest(),
            "coupler_map_runs_utc": [
                run_utc(root, name) for name in (context.get("coupler_map") or {}).get("runs") or []
            ],
            "job_runs": RUNS,
            "characterization_analysis": CHARACTERIZATION if series else None,
            "characterization_analysis_sha256": hashlib.sha256((root / CHARACTERIZATION).read_bytes()).hexdigest()
            if series
            else None,
        },
        "implied_t1_assumption": "the whole P(1|1) drop between the no-wait and the wait run is T1 decay during the"
        " wait, and readout fidelity is unchanged between the two runs",
        "qubits": qubits(context, root),
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
