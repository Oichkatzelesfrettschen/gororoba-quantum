"""Shot-counter census of the retained gate-model runs: requested, reported and returned shots per record.

A gate-model shot is one circuit execution that writes one classical record, so a supported counter satisfies
returned records = reported shots = requested shots; under IQM all-zeros heralding the returned records are a
nonempty subset of the requested shots, and the census reports their retention range. The census checks those
identities on every retained run: Quantum Inspire (results/quantum_inspire/runs/*/results.json:
job.number_of_shots, shots_requested, shots_done, and the raw shot list), IQM (results/iqm/runs/*: the shots
cases.json names for the submitted job against raw/measurements.json), and IBM (results/live/*/raw/<job>/pub_*.json
register num_shots and bit strings against collect.json submitted_pub_shots). Each run is one item of
parallel.ordered_map. The output records its inventory of runs, the audit's frozen surface; `--check` recomputes
that inventory and compares the retained output, so a run retained later leaves the check valid.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from parallel import ordered_map  # noqa: E402

OUT = Path(__file__).with_name("gate_model_counter_census.json")
SCHEMA = "gate-model-counter-census-v2"
SOURCES = {
    "quantum_inspire": "results/quantum_inspire/runs/*/results.json",
    "iqm": "results/iqm/runs/*/raw/measurements.json",
    "ibm": "results/live/*/collect.json",
}


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def quantum_inspire(path: Path) -> dict[str, Any]:
    rows, mismatches = 0, []
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


def iqm(raw: Path) -> dict[str, Any]:
    run = raw.parent.parent
    name = load(run / "submission.json").get("job")
    case: dict[str, Any] = next((c for c in load(run / "cases.json").get("jobs", []) if c.get("job") == name), {})
    shots = case.get("shots")
    # All-zeros heralding discards each shot whose pre-circuit measurement is not all zeros
    # (iqm_jobs.shots_ok), so a heralded circuit returns a nonempty subset of its requested shots.
    heralded = (case.get("options") or {}).get("heralding_mode") == "zeros"
    rows, unresolved, mismatches = 0, 0, []
    retention: list[float] = []
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
    return {"circuits": rows, "unresolved": unresolved, "retention": retention, "mismatches": mismatches}


def ibm(collect: Path) -> dict[str, Any]:
    record = load(collect)
    jobs, mismatches = 0, []
    for entry in record if isinstance(record, list) else [record]:
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
                        {"run": collect.parent.name, "job": job_id, "pub": pub.name, "register_shots": sorted(shots)}
                    )
                returned += min(shots)
            if submitted is not None and returned != submitted:
                mismatches.append(
                    {"run": collect.parent.name, "job": job_id, "submitted_pub_shots": submitted, "returned": returned}
                )
    return {"jobs": jobs, "mismatches": mismatches}


CENSUS = {"quantum_inspire": quantum_inspire, "iqm": iqm, "ibm": ibm}


def census(item: tuple[str, str]) -> dict[str, Any]:
    provider, path = item
    return CENSUS[provider](ROOT / path)


def record(inventory: dict[str, list[str]] | None = None) -> dict[str, Any]:
    """The census over inventory (provider -> repository-relative paths), or over every retained run when None."""
    if inventory is None:
        inventory = {
            provider: sorted(str(p.relative_to(ROOT)) for p in ROOT.glob(pattern))
            for provider, pattern in SOURCES.items()
        }
    items = [(provider, path) for provider in SOURCES for path in inventory[provider]]
    parts = ordered_map(census, items, min_items=1)
    by: dict[str, list[dict[str, Any]]] = {provider: [] for provider in SOURCES}
    for (provider, _), part in zip(items, parts, strict=True):
        by[provider].append(part)
    retention = [value for part in by["iqm"] for value in part["retention"]]
    return {
        "schema": SCHEMA,
        "inventory": inventory,
        "quantum_inspire": {
            "results": sum(p["results"] for p in by["quantum_inspire"]),
            "mismatches": [m for p in by["quantum_inspire"] for m in p["mismatches"]],
        },
        "iqm": {
            "circuits": sum(p["circuits"] for p in by["iqm"]),
            "heralded_circuits": len(retention),
            "heralded_retention_range": [round(min(retention), 6), round(max(retention), 6)] if retention else None,
            "circuits_without_requested_shots": sum(p["unresolved"] for p in by["iqm"]),
            "mismatches": [m for p in by["iqm"] for m in p["mismatches"]],
        },
        "ibm": {
            "jobs": sum(p["jobs"] for p in by["ibm"]),
            "mismatches": [m for p in by["ibm"] for m in p["mismatches"]],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    inventory = load(OUT)["inventory"] if args.check else None
    text = json.dumps(record(inventory), indent=1, sort_keys=True) + "\n"
    if args.check:
        if OUT.read_text(encoding="utf-8") != text:
            print(f"{OUT.relative_to(ROOT)} differs from the recomputed census", file=sys.stderr)
            return 1
        return 0
    OUT.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
