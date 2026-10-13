"""Second analysis of a collected folded-correction run under the current schedule rule.

A collected run keeps its collect.json, isa.qpy and raw/<job_id>/pub_XX.json
files; collect refuses to rerun at a source digest other than the run's own.
This module re-reads those preserved files, applies the current
correction_schedule.qualify_pair rule and the preregistered
correction_statistics.analyze_counts decision, and writes
analysis-<digest12>.json beside them. The digest covers the analysis sources
and every input file, so a later rule writes a new file beside this one.

The replay accepts only a run whose collect.json withheld its decision at the
schedule step: every acquisition, calibration and archive gate before it
passed in the original collection. --check recomputes and compares bytes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

from qiskit import qpy

import correction_circuits
import correction_schedule
from correction_collection import MEMBERS, SHOTS, integer_counts
from correction_statistics import analyze_counts

SCHEMA = "folded-correction-second-analysis-v1"
ANALYSIS_SOURCES = (
    "correction_reanalysis.py",
    "correction_schedule.py",
    "correction_circuits.py",
    "correction_statistics.py",
    "correction_collection.py",
)
# Pairs as (label, feedback PUB index, independent PUB index) in MEMBERS order.
PAIRS = ((1, 0, 1), (3, 3, 2))
SCHEDULE_WITHHELD = "correction acquisition or schedule evidence: then and else corrections occupy different time slots"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _scheduler_timing(node: Any) -> dict[str, Any] | None:
    if isinstance(node, dict):
        if "scheduler_timing" in node:
            return dict(node["scheduler_timing"])
        children = list(node.values())
    elif isinstance(node, list):
        children = node
    else:
        return None
    for child in children:
        found = _scheduler_timing(child)
        if found is not None:
            return found
    return None


def _counts(family: dict[str, Any], collected: Any) -> dict[str, list[int]]:
    """Return the integer counts collect.json retained for each member."""

    def find(node: Any, key: str) -> Any:
        if isinstance(node, dict):
            if key in node and isinstance(node[key], list) and len(node[key]) == 4:
                return node[key]
            for child in node.values():
                found = find(child, key)
                if found is not None:
                    return found
        elif isinstance(node, list):
            for child in node:
                found = find(child, key)
                if found is not None:
                    return found
        return None

    counts = {}
    for name in MEMBERS:
        value = find(collected, name)
        if not (isinstance(value, list) and all(type(item) is int for item in value) and sum(value) == SHOTS):
            raise ValueError(f"collect.json lacks integer counts for {name}")
        counts[name] = value
    return counts


def _raw_counts(payload: dict[str, Any]) -> list[int]:
    """Histogram the single two-bit classical register of one raw PUB."""
    registers = payload["registers"]
    if len(registers) != 1:
        raise ValueError("a correction PUB retains exactly one classical register")
    (register,) = registers.values()
    if register["num_bits"] != 2 or register["num_shots"] != SHOTS:
        raise ValueError("raw register shape differs from the correction protocol")
    histogram: dict[str, int] = {}
    for bits in register["bitstrings"]:
        histogram[bits] = histogram.get(bits, 0) + 1
    return integer_counts(histogram)


def analyze(run: Path) -> tuple[str, dict[str, Any]]:
    collect_path, qpy_path, record_path = run / "collect.json", run / "isa.qpy", run / "record.json"
    collected = json.loads(collect_path.read_text())
    family = collected[0]["family_analysis"]
    if family.get("decision_available") is not False or family.get("withheld") != SCHEDULE_WITHHELD:
        raise ValueError("replay applies only to a run withheld at the equal-start schedule rule")
    jobs = collected[0]["jobs"]
    if len(jobs) != 1:
        raise ValueError("correction replay requires exactly one collected job")
    (job_id,) = jobs
    raw = run / "raw" / job_id
    pubs = [raw / f"pub_{index:02d}.json" for index in range(len(MEMBERS))]
    retained = json.loads((raw / "index.json").read_text())["files"]
    if any(_sha256(path) != retained.get(path.name) for path in pubs):
        raise ValueError("a raw PUB differs from the sha256 retained by collection")
    record = json.loads(record_path.read_text())
    backend = record["submission"]["jobs"][0]["backend"]
    dt_seconds = record["family_configuration"]["dt_seconds"]
    with qpy_path.open("rb") as handle:
        circuits = qpy.load(handle)
    payloads = [json.loads(path.read_text()) for path in pubs]
    found = [_scheduler_timing(payload) for payload in payloads]
    timings = [timing for timing in found if timing is not None]
    if len(timings) != len(MEMBERS) or len(circuits) != len(MEMBERS):
        raise ValueError("raw scheduler timing or archived circuits are incomplete")
    pairs = {}
    for label, feedback, independent in PAIRS:
        report = correction_circuits.validate_bound_correction_pair(circuits[feedback], circuits[independent], label)
        pairs[str(label)] = correction_schedule.qualify_pair(
            timings[feedback], timings[independent], dt_seconds=dt_seconds, circuit_pair_report=report
        )
    counts = {name: _raw_counts(payload) for name, payload in zip(MEMBERS, payloads, strict=True)}
    if counts != _counts(family, collected):
        raise ValueError("raw shot histograms differ from the counts collect.json retained")
    here = Path(__file__).resolve().parent
    inputs = {
        "collect.json": _sha256(collect_path),
        "isa.qpy": _sha256(qpy_path),
        "record.json": _sha256(record_path),
        **{f"raw/{job_id}/{path.name}": _sha256(path) for path in pubs},
    }
    sources = {name: _sha256(here / name) for name in ANALYSIS_SOURCES}
    digest = hashlib.sha256(json.dumps({"inputs": inputs, "sources": sources}, sort_keys=True).encode()).hexdigest()
    result = {
        "schema": SCHEMA,
        "analysis_digest": digest,
        "job_id": job_id,
        "backend": backend,
        "inputs_sha256": inputs,
        "analysis_sources_sha256": sources,
        "original_withheld": family["withheld"],
        "schedule_pairs": pairs,
        "decision_available": all(pair["qualified"] for pair in pairs.values()),
        "integer_counts": counts,
        "statistical_decision": analyze_counts(counts, expected_shots=SHOTS, alpha=0.05, minimum_gain=0.01),
    }
    return f"analysis-{digest[:12]}.json", result


RETAINED_RUN = Path(__file__).resolve().parent.parent / "results/live/2026-10-13T020454.599853Z"


# The analysis digest names the file and binds the sources that produced it;
# reproduction compares the computed content, so a later source revision or a
# different platform's last-bit floating point still reproduces a retained file.
DIGEST_FIELDS = ("analysis_digest", "analysis_sources_sha256")
FLOAT_TOLERANCE = 1e-12


def _same(left: Any, right: Any) -> bool:
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(_same(left[key], right[key]) for key in left)
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(_same(a, b) for a, b in zip(left, right, strict=True))
    if isinstance(left, float) or isinstance(right, float):
        return (
            isinstance(left, (int, float))
            and isinstance(right, (int, float))
            and not isinstance(left, bool)
            and not isinstance(right, bool)
            and math.isclose(left, right, rel_tol=FLOAT_TOLERANCE, abs_tol=FLOAT_TOLERANCE)
        )
    return bool(left == right)


def reproduces(run: Path, result: dict[str, Any]) -> list[Path]:
    """Retained analyses in run whose computed content matches result."""
    fresh = {key: value for key, value in result.items() if key not in DIGEST_FIELDS}
    matches = []
    for path in sorted(run.glob("analysis-*.json")):
        retained = json.loads(path.read_text())
        if _same({key: value for key, value in retained.items() if key not in DIGEST_FIELDS}, fresh):
            matches.append(path)
    return matches


def _verify() -> None:
    """Replay the retained run, reject a tampered raw shot, and keep analyses write-once."""
    import shutil
    import tempfile

    _name, result = analyze(RETAINED_RUN)
    if not reproduces(RETAINED_RUN, result):
        raise RuntimeError("retained second analysis does not reproduce")
    with tempfile.TemporaryDirectory(prefix="correction-reanalysis-") as directory:
        copy = Path(directory) / RETAINED_RUN.name
        shutil.copytree(RETAINED_RUN, copy)
        (pub,) = (copy / "raw").glob("*/pub_00.json")
        payload = json.loads(pub.read_text())
        (register,) = payload["registers"].values()
        register["bitstrings"][0] = "00" if register["bitstrings"][0] != "00" else "11"
        pub.write_text(json.dumps(payload))
        try:
            analyze(copy)
        except ValueError:
            pass
        else:
            raise RuntimeError("a tampered raw shot passed the replay")
        clean = Path(directory) / "write-once" / RETAINED_RUN.name
        shutil.copytree(RETAINED_RUN, clean)
        for retained in clean.glob("analysis-*.json"):
            retained.unlink()
        if main([str(clean)]) != 0 or main([str(clean)]) == 0:
            raise RuntimeError("a fresh analysis was refused or an existing analysis was overwritten")
    print("correction reanalysis: replay, raw tamper rejection, and write-once checks pass")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path, nargs="?", help="collected folded-correction run directory")
    parser.add_argument("--check", action="store_true", help="compare recomputed bytes with the retained analysis")
    parser.add_argument("--self-check", action="store_true", help="verify the replay against the retained run")
    arguments = parser.parse_args(argv)
    if arguments.self_check:
        _verify()
        return 0
    if arguments.run is None:
        parser.error("a run directory is required")
    name, result = analyze(arguments.run)
    text = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    target = arguments.run / name
    if arguments.check:
        if not reproduces(arguments.run, result):
            print(f"no retained analysis in {arguments.run} matches the recomputed analysis")
            return 1
        print(f"{name}: decision {result['statistical_decision']['decision']} reproduced")
    elif target.exists():
        print(f"{target} exists; analyses are write-once")
        return 1
    else:
        target.write_text(text)
        print(f"{name}: decision {result['statistical_decision']['decision']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
