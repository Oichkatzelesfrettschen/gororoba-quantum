"""Replay reduced QX parser and one-shot outputs locally, without provider access."""

from __future__ import annotations

import argparse
import datetime
import json
import sys
import warnings
from importlib.metadata import version
from pathlib import Path
from typing import Any

from qi_tuna_qx_destination import PROPOSAL, ROOT, SOURCES, digest

sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from parallel import ordered_map  # noqa: E402


def replay_source(item: tuple[str, str, str]) -> dict[str, Any]:
    """Parse and simulate one exact source under the pinned local QI stack."""
    warnings.simplefilter("error")
    warnings.filterwarnings("ignore", r"builtin type \w+ has no __module__ attribute", DeprecationWarning)
    import cqasm.v3x as v3
    import qxelarator

    name, expected_hash, expected = item
    path = PROPOSAL / f"{name}.cq"
    if digest(path) != expected_hash:
        raise ValueError("local replay source digest differs")
    source = path.read_text(encoding="utf-8")
    parsed = json.loads(v3.Analyzer().analyze_string_to_json(source), strict=False)
    errors = parsed.get("errors", [])
    if errors:
        raise ValueError(f"local parser rejected {name}: {errors}")
    simulation = qxelarator.execute_string(source, iterations=1)
    if simulation.shots_done != 1 or simulation.results != {expected: 1}:
        raise ValueError(f"local simulator output differs for {name}")
    return {
        "name": name,
        "source_sha256": expected_hash,
        "parser_errors": errors,
        "shots": 1,
        "counts": simulation.results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    operation = parser.add_mutually_exclusive_group(required=True)
    operation.add_argument("--out", type=Path)
    operation.add_argument("--check", type=Path)
    arguments = parser.parse_args()
    versions = {name: version(name) for name in ("libqasm", "qxelarator")}
    if versions != {"libqasm": "1.2.1", "qxelarator": "0.10.0"} or sys.version_info[:2] != (3, 13):
        raise ValueError("local replay requires the pinned Python 3.13 Quantum Inspire stack")
    started = datetime.datetime.now(datetime.UTC)
    rows = ordered_map(replay_source, list(SOURCES), min_items=2)
    report = {
        "schema": "qi-qx-destination-local-replay-v1",
        "started_utc": started.isoformat(),
        "finished_utc": datetime.datetime.now(datetime.UTC).isoformat(),
        "python_version": sys.version.split()[0],
        "versions": versions,
        "producer_sha256": digest(Path(__file__)),
        "command": '"$QI_PYTHON" scripts/qi_tuna_qx_local_replay.py --out OUTPUT',
        "rows": rows,
        "boundary": "Local parser and one-shot simulator replay; no provider execution or Tuna measurement.",
    }
    if arguments.check:
        retained = json.loads(arguments.check.read_bytes())
        for field in ("started_utc", "finished_utc"):
            report.pop(field)
            retained.pop(field)
        if retained != report:
            raise ValueError("local QX semantic replay differs from retained observation")
        print("Local QX parser and one-shot outputs match the retained observation.")
    else:
        with arguments.out.open("x", encoding="utf-8") as destination:
            json.dump(report, destination, indent=2, sort_keys=True)
            destination.write("\n")


if __name__ == "__main__":
    main()
