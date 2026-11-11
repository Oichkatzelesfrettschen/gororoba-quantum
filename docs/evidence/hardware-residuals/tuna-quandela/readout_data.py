"""Readout-circuit table of every retained Tuna-17 run: prepared state, per-qubit flip counts, midpoint time.

Reads through qi_records.read_run (the repository reader) so receipt binding, circuit digests and raw-histogram
agreement are enforced; a run that fails validation is listed, never silently dropped.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any

import common as c
import numpy as np

import qi_records

X_GATE = re.compile(r"^X q\[(\d+)\]$")
PASS = re.compile(r"^(version 3\.0|qubit\[\d+\] q|bit\[\d+\] b|barrier q|b = measure q|)$")


def parse_circuit(text: str) -> list[int] | None:
    """Prepared-|1> qubit list if the circuit holds only X gates, a barrier and a full measurement; else None."""
    ones: list[int] = []
    for raw in text.splitlines():
        line = raw.strip()
        match = X_GATE.match(line)
        if match:
            ones.append(int(match.group(1)))
        elif not PASS.match(line):
            return None
    return sorted(set(ones))


def iso(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def run_directories() -> list[Path]:
    return sorted(p.parent for p in c.QI_RUNS.rglob("raw") if p.is_dir() and (p.parent / "results.json").exists())


def collect() -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    rows: list[dict[str, Any]] = []
    problems: list[dict[str, str]] = []
    for directory in run_directories():
        relative = str(directory.relative_to(c.QI_RUNS))
        try:
            record = qi_records.load_run(directory)
            sub = record["submission"]
            if sub is None or sub.get("backend_type_id") != 7:
                continue
            acquisition = qi_records.validate_run(record, relative)
        except Exception as error:
            sub = None
            try:
                import json

                sub = json.loads((directory / "submission.json").read_text())
            except Exception:
                pass
            if sub is not None and sub.get("backend_type_id") == 7:
                problems.append({"run": relative, "problem": str(error)[:200]})
            continue
        collected = {row["file"]: row for row in record["results"]["jobs"]}
        for job in acquisition.jobs:
            if job.status != "completed" or job.raw is None:
                continue
            text = (directory / job.file).read_text()
            ones = parse_circuit(text)
            if ones is None:
                continue
            row = collected[job.file]
            result = row["results"][0]
            finished = iso(row["job"]["finished_at"])
            seconds = float(result.get("execution_time_in_seconds") or 0.0)
            midpoint = finished.timestamp() - seconds / 2
            width = len(job.raw[0])
            shots = np.frombuffer("".join(job.raw).encode("ascii"), dtype=np.uint8).reshape(len(job.raw), width)[
                :, ::-1
            ] == ord("1")
            prepared = np.zeros(width, dtype=bool)
            prepared[ones] = True
            flips = (shots != prepared[None, :]).sum(axis=0)
            rows.append(
                {
                    "run": relative,
                    "file": job.file,
                    "series": re.sub(
                        r"-(batch|recal|rerun)-?\d*.*$", "", re.sub(r"^\d{4}-\d\d-\d\dT\d{6}Z-", "", relative)
                    ),
                    "stamp": relative[:17],
                    "t": midpoint,
                    "shots": len(job.raw),
                    "prepared_one": ones,
                    "flips": flips.astype(int).tolist(),
                    "width": width,
                }
            )
    rows.sort(key=lambda r: r["t"])
    return rows, problems


if __name__ == "__main__":
    rows, problems = collect()
    print(len(rows), "readout jobs;", len(problems), "problems")
    for r in rows[:5]:
        print({k: r[k] for k in ("run", "file", "series", "t", "shots", "prepared_one")})
    import collections

    print(collections.Counter((r["series"], tuple(r["prepared_one"])) for r in rows).most_common(40))
