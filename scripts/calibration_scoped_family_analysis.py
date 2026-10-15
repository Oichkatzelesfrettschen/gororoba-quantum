"""Secondary analysis of a collected matched-family run whose PUBs ran under more than one calibration.

live_run.collect withholds the whole family analysis when its members did
not all execute under one calibration (live_run._comparisons_withheld),
because a calibration update between the PUBs of one comparison would read as
signal. That reason applies per observable: this analysis groups the record's
preregistered observable contracts by the execution calibrations of their
terms, evaluates each single-calibration group with
qpu_planning.measured_family exactly as the collector would, and lists every
contract whose terms span calibrations as withheld. Each contract keeps its
preregistered alpha, so the multiplicity correction still covers the whole
registered family. The measured distributions and execution windows come from
collect.json's family_measurements; collect.json and the raw files are read,
never rewritten.

Usage:
    "$PYTHON" scripts/calibration_scoped_family_analysis.py RUN --out RUN/calibration-scoped-analysis.json
    "$PYTHON" scripts/calibration_scoped_family_analysis.py RUN --check RUN/calibration-scoped-analysis.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import live_run  # noqa: E402
import qpu_planning  # noqa: E402


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def analyze(run: Path) -> dict[str, Any]:
    record = json.loads((run / "record.json").read_text())
    header = json.loads((run / "collect.json").read_text())[0]
    measurements = header["family_measurements"]
    executed = {name: entry["execution"] for name, entry in measurements.items()}
    distributions = {
        name: [np.asarray(p, dtype=float) for p in entry["replica_probabilities"]]
        for name, entry in measurements.items()
    }
    strata: dict[str, list[dict[str, Any]]] = {}
    withheld: list[dict[str, Any]] = []
    for contract in record["observable_contracts"]:
        members = [term["member"] for term in contract["terms"]]
        windows = [executed.get(member) for member in members]
        calibrations = sorted({str(w["calibration"]) for w in windows if w is not None})
        changed = any(w is None or w["calibration"] is None or w["calibration_changed_during_shots"] for w in windows)
        if changed or len(calibrations) != 1:
            withheld.append({"name": contract["name"], "calibrations": calibrations})
            continue
        strata.setdefault(calibrations[0], []).append(contract)
    results: dict[str, Any] = {}
    for calibration, contracts in sorted(strata.items()):
        scoped = {**record, "observable_contracts": contracts}
        results[calibration] = qpu_planning.measured_family(scoped, distributions, executed, live_run)
        if "withheld" in results[calibration]:
            raise ValueError(f"stratum {calibration} withheld: {results[calibration]['withheld']}")
    observables = sorted(
        (observable for result in results.values() for observable in result["observables"]),
        key=lambda observable: observable["name"],
    )
    return {
        "schema": "calibration-scoped-family-analysis-v1",
        "scope": (
            "Secondary analysis. The collector withheld the family analysis because its PUBs ran under more than "
            "one calibration; each preregistered contract here is evaluated only with the PUBs of a single "
            "execution calibration, at its preregistered alpha, and contracts spanning calibrations are withheld."
        ),
        "run": run.name,
        "experiment_digest": record["experiment_digest"],
        "inputs_sha256": {name: digest(run / name) for name in ("record.json", "collect.json")},
        "analysis_source_sha256": digest(Path(__file__)),
        "collector_family_analysis": header["family_analysis"],
        "registered_contracts": len(record["observable_contracts"]),
        "strata": {calibration: len(contracts) for calibration, contracts in sorted(strata.items())},
        "withheld_contracts": withheld,
        "rejected_nulls": sum(bool(observable.get("reject_null")) for observable in observables),
        "observables": observables,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run", type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    arguments = parser.parse_args()
    rendered = json.dumps(analyze(arguments.run), indent=1, sort_keys=True, allow_nan=False) + "\n"
    if arguments.out is not None:
        arguments.out.write_text(rendered)
    elif arguments.check.read_text() != rendered:
        raise SystemExit(f"calibration-scoped analysis differs from {arguments.check}")
    result = json.loads(rendered)
    print(
        f"{arguments.run.name}: {sum(result['strata'].values())} of {result['registered_contracts']} contracts "
        f"in single-calibration strata, {len(result['withheld_contracts'])} withheld, "
        f"{result['rejected_nulls']} reject their nulls"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
