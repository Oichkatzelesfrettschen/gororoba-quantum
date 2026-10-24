"""Markdown body of the nightly audit's tracking issue.

Reads the shard timing records ci/run_gates.py writes with --timings (schema
SHARD_SCHEMA, one ``status`` per gate) and docs/state/research_state.json,
whose claims name the gates their evidence rests on, and lists every failing
gate beside the claims that cite it, then each failing workflow job given on
the command line.

Usage: "$PYTHON" ci/audit_report.py --run-url URL [--failed-job NAME ...] TIMINGS...
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESEARCH_STATE = ROOT / "docs/state/research_state.json"
# The record ci/run_gates.py --timings writes; the merged cost file of
# ci/merge_gate_timings.py shares the artifact pattern under another schema.
SHARD_SCHEMA = "gororoba-gate-timings-v1"


def failing_gates(records: list[dict[str, Any]]) -> list[str]:
    shards = [record for record in records if record.get("schema") == SHARD_SCHEMA]
    return sorted({gate["name"] for record in shards for gate in record["gates"] if gate["status"] != 0})


def citing_claims(state: dict[str, Any], gates: list[str]) -> dict[str, list[str]]:
    cited: dict[str, list[str]] = {gate: [] for gate in gates}
    for claim in state["claims"]:
        for gate in claim.get("gates", {}):
            if gate in cited:
                cited[gate].append(claim["id"])
    return cited


def report(run_url: str, failed_jobs: list[str], records: list[dict[str, Any]], state: dict[str, Any]) -> str:
    gates = failing_gates(records)
    lines = [f"The scheduled audit run {run_url} failed.", ""]
    if gates:
        lines += ["| failing gate | claims citing it |", "| --- | --- |"]
        for gate, claims in citing_claims(state, gates).items():
            lines.append(f"| `{gate}` | {', '.join(f'`{claim}`' for claim in claims) or 'none'} |")
        lines.append("")
    if failed_jobs:
        lines.append("Failing jobs: " + ", ".join(f"`{job}`" for job in sorted(failed_jobs)) + ".")
        lines.append("")
    lines.append("Each cited claim is qualified until its gate passes again on main.")
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--run-url", required=True)
    parser.add_argument("--failed-job", action="append", default=[])
    parser.add_argument("--research-state", type=Path, default=RESEARCH_STATE)
    parser.add_argument("timings", nargs="*", type=Path)
    arguments = parser.parse_args(argv)
    records = [json.loads(path.read_text(encoding="utf-8")) for path in arguments.timings]
    state = json.loads(arguments.research_state.read_text(encoding="utf-8"))
    sys.stdout.write(report(arguments.run_url, arguments.failed_job, records, state))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
