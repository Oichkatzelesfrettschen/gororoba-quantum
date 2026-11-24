"""Analyze collected run directories of the replicated Tuna-17 matched-response proposal.

Reads the proposal bytes and the collected Quantum Inspire run directories, binds each run to its replicate by the
sha256 of its cases.json, and applies gororoba_quantum/qi_replicated_response.py. No provider call. Modes:

  --stage1 RUN_DIR... [--out FILE]   exactly rep-00 .. rep-11; prints the verdict (continue, undecided-at-cap or
                                     final) and the rule's total N from the stage-1 standard deviation alone, and
                                     writes the stage-1 decision record (s1, N, digests). The stage-1 mean, the
                                     residuals and the diagnostics appear in neither the output nor the record.
  --final RUN_DIR... --out FILE      rep-00 .. rep-(N-1) for the rule's N (12 at the cap); writes the analysis;
                                     --stage1-decision FILE cross-checks it against the stage-1 record.
  --binding RUN_DIR                  one replicate: manifest and circuit digests, job order, readout sanity. No
                                     witness frequency or residual is printed.

The decision rule is fixed in docs/design/tuna17-matched-response-replicated.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import qi_replicated_response as rule  # noqa: E402
from qi_matched_response import verify_run_binding  # noqa: E402
from qi_records import load_run, validate_run  # noqa: E402

PROPOSAL = ROOT / "results/quantum_inspire/proposals/tuna17-zero-divisor-matched-response-replicated-q11"
STAGE1_SCHEMA = "qi-replicated-stage1-decision-v1"


def _require(condition: object, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_series(directories: list[Path], proposal_dir: Path) -> dict[str, Any]:
    """Load, validate and bind the run directories; the replicate of a run is the one whose manifest digest it holds."""
    expected = rule.proposal_digests(proposal_dir)
    proposal = json.loads((proposal_dir / "proposal.json").read_text())
    owner = {row["cases.json"]: name for name, row in expected["batches"].items()}
    manifests: dict[str, Any] = {}
    shots: dict[tuple[str, str], Any] = {}
    job_order: dict[str, list[tuple[str, Any]]] = {}
    batch_jobs: dict[str, Any] = {}
    bound: dict[str, Any] = {}
    for directory in directories:
        record = load_run(directory)
        acquisition = validate_run(record, f"Quantum Inspire run {directory.name}")
        name = owner.get(record["cases_sha256"])
        if name is None:
            raise ValueError(f"{directory.name}: the manifest is not a replicate of this proposal")
        _require(name not in manifests, f"{directory.name}: replicate {name} appears twice")
        _require(acquisition.completed, f"{directory.name}: not every job completed")
        _require(acquisition.backend == proposal["backend"], f"{directory.name}: the run used another backend")
        _require(acquisition.shots == proposal["shots_per_job"], f"{directory.name}: the run used another shot count")
        bound[name] = verify_run_binding(expected, name, record)
        manifests[name] = record["cases"]
        job_order[name] = [(job.file, job.job_id) for job in acquisition.jobs]
        batch_jobs[name] = acquisition.batch_job
        for job in acquisition.jobs:
            shots[name, job.file] = job.raw
    return {
        "expected": expected,
        "proposal": proposal,
        "manifests": manifests,
        "shots": shots,
        "job_order": job_order,
        "batch_jobs": batch_jobs,
        "bound": bound,
    }


def analyze(series: dict[str, Any]) -> dict[str, Any]:
    return rule.analyze_replicated_series(
        series["proposal"],
        series["manifests"],
        series["shots"],
        job_order=series["job_order"],
        batch_jobs=series["batch_jobs"],
    )


def stage1_record(series: dict[str, Any]) -> dict[str, Any]:
    """The verdict and total of the rule after stage 1; the stage-1 mean and the residuals stay out of it."""
    _require(
        sorted(series["manifests"]) == [rule.batch_name(i) for i in range(rule.N1)],
        f"stage 1 takes exactly rep-00 .. rep-{rule.N1 - 1:02d}",
    )
    decision = analyze(series)["decision"]
    required = decision["required_total"]
    if decision["status"] == "undecided_at_cap":
        verdict = "undecided-at-cap"
    elif decision["status"] == "continue":
        verdict = "continue"
    else:
        verdict = "final"
    return {
        "schema": STAGE1_SCHEMA,
        "verdict": verdict,
        "s1": decision["s1"],
        "n": required if verdict == "continue" else rule.N1,
        "required_total": required,
        "proposal_sha256": series["expected"]["proposal.json"],
        "replicates": {name: row["cases.json"] for name, row in sorted(series["bound"].items())},
        "batch_jobs": dict(sorted(series["batch_jobs"].items())),
    }


def binding_report(series: dict[str, Any]) -> dict[str, Any]:
    """Binding and readout sanity of one replicate; the witness frequencies and the residual stay out."""
    _require(len(series["manifests"]) == 1, "--binding takes exactly one run directory")
    (name,) = series["manifests"]
    index = int(name.removeprefix("rep-"))
    manifest = series["manifests"][name]
    rule.verify_job_order(name, manifest, series["job_order"][name])
    rule.verify_distinct_ids([job for _, job in series["job_order"][name]], [series["batch_jobs"][name]])
    row = rule._replicate(index, manifest, series["shots"], series["proposal"])  # noqa: SLF001
    read1 = row["readout_read1"]
    error = float(read1.max() if row["readout"] == rule.READOUT_ZERO else (1 - read1).max())
    return {
        "batch": name,
        "cases_sha256": series["bound"][name]["cases.json"],
        "circuits": series["bound"][name]["circuits"],
        "batch_job": series["batch_jobs"][name],
        "jobs": series["job_order"][name],
        "readout": row["readout"],
        "readout_error": error,
        "readout_error_limit": rule.READOUT_ERROR_LIMIT,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--stage1", nargs="+", type=Path, metavar="RUN_DIR")
    mode.add_argument("--final", nargs="+", type=Path, metavar="RUN_DIR")
    mode.add_argument("--binding", type=Path, metavar="RUN_DIR")
    parser.add_argument("--proposal", type=Path, default=PROPOSAL)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--stage1-decision", type=Path)
    arguments = parser.parse_args()
    try:
        if arguments.stage1 is not None:
            record = stage1_record(load_series(arguments.stage1, arguments.proposal))
            if arguments.out is not None:
                arguments.out.write_text(json.dumps(record, indent=1) + "\n")
            print(f"verdict: {record['verdict']}")
            print(f"N: {record['n']}")
        elif arguments.final is not None:
            if arguments.out is None:
                raise ValueError("--final needs --out FILE")
            series = load_series(arguments.final, arguments.proposal)
            analysis = analyze(series)
            if arguments.stage1_decision is not None:
                first = {name: series["manifests"][name] for name in sorted(series["manifests"])[: rule.N1]}
                held = json.loads(arguments.stage1_decision.read_text())
                _require(held.get("schema") == STAGE1_SCHEMA, "the stage-1 decision record schema differs")
                _require(
                    held["proposal_sha256"] == series["expected"]["proposal.json"]
                    and held["s1"] == analysis["decision"]["s1"]
                    and held["required_total"] == analysis["decision"]["required_total"]
                    and held["replicates"] == {n: series["bound"][n]["cases.json"] for n in first},
                    "the stage-1 decision record differs from the series",
                )
            analysis["binding"] = {"proposal": series["expected"]["proposal.json"], "runs": series["bound"]}
            arguments.out.write_text(json.dumps(analysis, indent=1) + "\n")
            print(f"status: {analysis['decision']['status']}")
            print(f"N: {analysis['decision']['n']}")
        else:
            print(json.dumps(binding_report(load_series([arguments.binding], arguments.proposal)), indent=1))
    except ValueError as error:
        print(f"refused: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
