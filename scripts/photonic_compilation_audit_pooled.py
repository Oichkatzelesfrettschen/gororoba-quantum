"""Bind returned-mesh propagation to the pooled photonic readout successor."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import qd_platform as qd
from photonic_compilation_audit import _row
from photonic_repeat_readout_pooled import ROOT, analyze

from parallel import ordered_map


def _results(name: str) -> tuple[str, dict[str, Any]]:
    return name, json.loads((ROOT / "results/quandela/runs" / name / "results.json").read_text())


def audit(path: Path) -> dict[str, Any]:
    from bdsc_certificate import close

    retained = json.loads(path.read_text())
    names = [row["run"] for row in retained["acquisitions"]]
    if any(Path(name).name != name or name in {".", ".."} for name in names):
        raise ValueError("an acquisition must name one retained run directory")
    fresh = analyze([ROOT / "results/quandela/runs" / name for name in names])
    close(retained, fresh, "pooled photonic repeat readout")
    if any(row["backends"] != ["qpu:belenos"] for row in retained["acquisitions"]):
        raise ValueError("the 24-mode compilation audit is qualified for Belenos records")
    results = dict(ordered_map(_results, names, min_items=1))
    arguments = []
    for row in retained["observations"]:
        entries = results[row["run"]]["iterations"]
        index = row["observation_index"]
        arguments.append((row, entries[index], entries[index - 1] if index else None))
    rows = ordered_map(_row, arguments, min_items=1)
    return {
        "schema": "photonic-compilation-measurement-audit-v1",
        "producer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "dependency_sha256": {
            "scripts/photonic_compilation_audit.py": hashlib.sha256(
                (ROOT / "scripts/photonic_compilation_audit.py").read_bytes()
            ).hexdigest()
        },
        "readout": path.resolve().relative_to(ROOT).as_posix(),
        "readout_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "rows": rows,
        "max_compiled_vs_requested_tvd": max(row["compiled_vs_requested_tvd"] for row in rows),
        "max_measured_vs_compiled_tvd": max(row["measured_vs_compiled_tvd"] for row in rows),
        "boundary": (
            "returned numerical meshes are metadata; their agreement with a request does not prove applied controls"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("readout", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    arguments = parser.parse_args()
    record = audit(arguments.readout)
    if arguments.check:
        from bdsc_certificate import close

        close(json.loads(arguments.check.read_text()), record, "pooled compilation audit")
        print("replayed pooled returned-mesh audit")
    elif arguments.out:
        qd.write_json(arguments.out, record, exclusive=True)
    else:
        print(json.dumps(record, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
