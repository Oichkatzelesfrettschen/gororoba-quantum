"""Counter table of every retained Quandela run: outer, per-iteration and requested counters side by side.

Reads results/quandela/runs/*/raw/result.json and submission.json without writing them, decodes the inner Perceval
result (one result or a results_list), and records, per iteration, nb_shots_used, the returned sample sum of its
BSCount, physical_perf and logical_perf beside the outer shots and duration, the submission's max_shots and
max_samples, and the min_detected_photons filter the run's case records state. `--check` recomputes the table and
fails when the retained JSON differs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zlib
from base64 import b64decode
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
RUNS = ROOT / "results/quandela/runs"
OUT = Path(__file__).with_name("quandela_counter_table.json")
SCHEMA = "quandela-counter-table-v1"


def unzip(text: str) -> str:
    """Perceval serializes a compressed payload as ':PCVL:zip:' plus base64 zlib bytes."""
    prefix = ":PCVL:zip:"
    while text.startswith(prefix):
        text = zlib.decompress(b64decode(text[len(prefix) :])).decode()
    return text


def sample_sum(results: str) -> tuple[int, int]:
    """Sum of BSCount counts and the number of distinct states."""
    pairs = re.findall(r"\|[0-9,]+>=(\d+)", unzip(results))
    return sum(int(n) for n in pairs), len(pairs)


def number(value: Any) -> Any:
    return value if isinstance(value, int | float) and not isinstance(value, bool) else None


def filters(run: Path) -> list[int]:
    """Every min_detected_photons value the run's case, circuit and submission records state."""
    values: set[int] = set()
    for name in ("cases.json", "circuit.json", "submission.json"):
        path = run / name
        if path.is_file():
            values |= {int(v) for v in re.findall(r'"min_detected_photons": *(\d+)', path.read_text(encoding="utf-8"))}
    return sorted(values)


def run_row(run: Path) -> dict[str, Any]:
    raw = run / "raw/result.json"
    outer = json.loads(raw.read_text(encoding="utf-8"))
    submission_path = run / "submission.json"
    submission = json.loads(submission_path.read_text(encoding="utf-8")) if submission_path.exists() else {}
    row: dict[str, Any] = {
        "run": run.name,
        "raw_sha256": hashlib.sha256(raw.read_bytes()).hexdigest(),
        "platform": submission.get("platform"),
        "outer_shots": number(outer.get("shots")),
        "outer_duration_s": number(outer.get("duration")),
        "submission_max_shots": number(submission.get("max_shots")),
        "submission_max_samples": number(submission.get("max_samples")),
        "submission_estimated_shots": number(submission.get("estimated_shots")),
        "min_detected_photons": filters(run),
    }
    payload = outer.get("results")
    if not isinstance(payload, str):
        row["iterations"] = []
        row["inner"] = "absent"
        return row
    inner = json.loads(payload)
    listed = "results_list" in inner
    entries = inner.get("results_list") or [inner]
    iterations = []
    for entry in entries:
        fields = entry
        results = entry.get("results")
        samples, states = sample_sum(results) if isinstance(results, str) else (None, None)
        iterations.append(
            {
                "nb_shots_used": number(fields.get("nb_shots_used")),
                "samples": samples,
                "distinct_states": states,
                "physical_perf": number(fields.get("physical_perf")),
                "logical_perf": number(fields.get("logical_perf")),
            }
        )
    row["inner"] = "results_list" if listed else "single"
    row["iterations"] = iterations
    used = [i["nb_shots_used"] for i in iterations]
    returned = [i["samples"] for i in iterations]
    row["sum_nb_shots_used"] = sum(used) if used and None not in used else None
    row["sum_samples"] = sum(returned) if returned and None not in returned else None
    row["every_used_equals_samples"] = bool(iterations) and all(
        u is not None and u == s for u, s in zip(used, returned, strict=True)
    )
    return row


def table() -> dict[str, Any]:
    runs = sorted(p.parent.parent for p in RUNS.glob("*/raw/result.json"))
    rows = [run_row(run) for run in runs]
    return {"schema": SCHEMA, "runs": rows, "run_count": len(rows)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = json.dumps(table(), indent=1, sort_keys=True) + "\n"
    if args.check:
        if OUT.read_text(encoding="utf-8") != text:
            print(f"{OUT.relative_to(ROOT)} differs from the recomputed table", file=sys.stderr)
            return 1
        return 0
    OUT.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
