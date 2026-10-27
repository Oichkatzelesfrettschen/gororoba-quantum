"""Shot-counter census of the retained gate-model runs: requested, reported and returned shots per record.

A gate-model shot is one circuit execution that writes one classical record, so a supported counter satisfies
returned records = reported shots = requested shots; under IQM all-zeros heralding the returned records are a
nonempty subset of the requested shots, and the census reports their retention range. The census checks those
identities on every retained run: Quantum Inspire (results/quantum_inspire/runs/*/results.json:
job.number_of_shots, shots_requested, shots_done, and the raw shot list), IQM (results/iqm/runs/*: the shots
cases.json names for the submitted job against raw/measurements.json), and IBM (results/live/*/raw/<job>/pub_*.json
register num_shots and bit strings against collect.json submitted_pub_shots). `--check` recomputes and compares the
retained output.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).with_name("gate_model_counter_census.json")
SCHEMA = "gate-model-counter-census-v1"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def quantum_inspire() -> dict[str, Any]:
    rows, mismatches = 0, []
    for path in sorted((ROOT / "results/quantum_inspire/runs").glob("*/results.json")):
        for entry in load(path).get("jobs", []):
            job = entry.get("job") or {}
            raw = path.parent / "raw" / f"{entry.get('file')}.json"
            returned = len(load(raw)) if raw.is_file() else None
            for result in entry.get("results") or []:
                rows += 1
                values = (job.get("number_of_shots"), result.get("shots_requested"), result.get("shots_done"))
                if len(set(values)) != 1 or (returned is not None and returned != values[2]):
                    mismatches.append(
                        {
                            "run": path.parent.name,
                            "file": entry.get("file"),
                            "counters": values,
                            "raw_records": returned,
                            "status": job.get("status"),
                        }
                    )
    return {"results": rows, "mismatches": mismatches}


def iqm() -> dict[str, Any]:
    rows, unresolved, mismatches = 0, 0, []
    retention: list[float] = []
    for raw in sorted((ROOT / "results/iqm/runs").glob("*/raw/measurements.json")):
        run = raw.parent.parent
        name = load(run / "submission.json").get("job")
        case: dict[str, Any] = next((c for c in load(run / "cases.json").get("jobs", []) if c.get("job") == name), {})
        shots = case.get("shots")
        # All-zeros heralding discards each shot whose pre-circuit measurement is not all zeros
        # (iqm_jobs.shots_ok), so a heralded circuit returns a nonempty subset of its requested shots.
        heralded = (case.get("options") or {}).get("heralding_mode") == "zeros"
        for index, circuit in enumerate(load(raw)):
            lengths = {len(values) for values in circuit.values()}
            rows += 1
            unresolved += shots is None
            (length,) = lengths if len(lengths) == 1 else (None,)
            if heralded and shots is not None and length is not None:
                retention.append(length / shots)
            fits = length is not None and (shots is None or (0 < length <= shots if heralded else length == shots))
            if not fits:
                mismatches.append({"run": run.name, "circuit": index, "requested": shots, "returned": sorted(lengths)})
    return {
        "circuits": rows,
        "heralded_circuits": len(retention),
        "heralded_retention_range": [round(min(retention), 6), round(max(retention), 6)] if retention else None,
        "circuits_without_requested_shots": unresolved,
        "mismatches": mismatches,
    }


def ibm() -> dict[str, Any]:
    jobs, mismatches = 0, []
    for collect in sorted((ROOT / "results/live").glob("*/collect.json")):
        record = load(collect)
        entries = record if isinstance(record, list) else [record]
        for entry in entries:
            for job_id, job in (entry.get("jobs") or {}).items():
                raw = collect.parent / "raw" / job_id
                submitted = (job.get("usage") or {}).get("submitted_pub_shots")
                if not raw.is_dir():
                    continue
                jobs += 1
                returned = 0
                for pub in sorted(raw.glob("pub_*.json")):
                    registers = load(pub)["registers"]
                    shots = {r["num_shots"] for r in registers.values()} | {
                        len(r["bitstrings"]) for r in registers.values()
                    }
                    if len(shots) != 1:
                        mismatches.append(
                            {
                                "run": collect.parent.name,
                                "job": job_id,
                                "pub": pub.name,
                                "register_shots": sorted(shots),
                            }
                        )
                    returned += min(shots)
                if submitted is not None and returned != submitted:
                    mismatches.append(
                        {
                            "run": collect.parent.name,
                            "job": job_id,
                            "submitted_pub_shots": submitted,
                            "returned": returned,
                        }
                    )
    return {"jobs": jobs, "mismatches": mismatches}


def record() -> dict[str, Any]:
    return {"schema": SCHEMA, "quantum_inspire": quantum_inspire(), "iqm": iqm(), "ibm": ibm()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = json.dumps(record(), indent=1, sort_keys=True) + "\n"
    if args.check:
        if OUT.read_text(encoding="utf-8") != text:
            print(f"{OUT.relative_to(ROOT)} differs from the recomputed census", file=sys.stderr)
            return 1
        return 0
    OUT.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
