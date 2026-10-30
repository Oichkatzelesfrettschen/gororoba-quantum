"""Analyze the current-source Ascella target-slot acquisition."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import tempfile
from pathlib import Path
from typing import Any

import ascella_predecessor_analysis as prior
import ascella_predecessor_case as original
import ascella_predecessor_current_case as current
import qd_platform as qd
from ascella_experiment_analysis import validate_sent_body

from parallel import ordered_map


def analyze(directory: Path, *, submission_sha256: str, results_sha256: str) -> dict[str, Any]:
    """Validate source, submission, result and circuit identities before descriptive analysis."""
    manifest = current.check(directory)
    case_bytes = (directory / "cases.json").read_bytes()
    if case_bytes != (json.dumps(manifest, indent=1) + "\n").encode():
        raise ValueError("the run differs from the current case")
    files = {
        "cases.json": case_bytes,
        "circuit.json": (directory / "circuit.json").read_bytes(),
        "submission.json": prior._anchor(directory / "submission.json", submission_sha256),
        "job-body.json": (directory / "job-body.json").read_bytes(),
        "results.json": prior._anchor(directory / "results.json", results_sha256),
        "raw/result.json": (directory / "raw/result.json").read_bytes(),
    }
    raw = prior._parse_json(files["raw/result.json"], "raw/result.json")
    if isinstance(raw.get("results"), str):
        json.loads(raw["results"], parse_constant=prior._reject_constant, object_pairs_hook=prior._unique_object)
    with tempfile.TemporaryDirectory(prefix="ascella-current-analysis-") as temporary:
        snapshot = Path(temporary) / "run"
        (snapshot / "raw").mkdir(parents=True)
        for name, data in files.items():
            (snapshot / name).write_bytes(data)
        qd.run_facts(snapshot)
    results = prior._parse_json(files["results.json"], "results.json")
    status = results.get("status")
    if not isinstance(status, dict):
        raise ValueError("the collected result requires status metadata")
    duration = status.get("duration")
    if (
        status.get("status") != "completed"
        or isinstance(duration, bool)
        or not isinstance(duration, int | float)
        or not math.isfinite(duration)
        or not 0 <= duration <= original.MAX_DURATION
    ):
        raise ValueError("a complete acquisition within the duration limit is required")
    validate_sent_body(prior._parse_json(files["job-body.json"], "job-body.json"), manifest, prior.PROFILE)
    entries = results.get("iterations")
    if not isinstance(entries, list) or len(entries) != len(original.ORDER):
        raise ValueError("the result requires all eight iterations")
    observations = ordered_map(
        prior._entry_worker,
        [
            (setting, entry, manifest["preregistered"]["compilation_identity"])
            for setting, entry in zip(manifest["settings"], entries, strict=True)
        ],
    )
    return {
        "schema": "ascella-predecessor-current-analysis-v1",
        "job_id": results["job_id"],
        "cases_sha256": hashlib.sha256(case_bytes).hexdigest(),
        "source_sha256": manifest["analysis_sources"],
        "current_case_sources": manifest["preregistered"]["current_case_sources"],
        "run_bindings": {name: hashlib.sha256(data).hexdigest() for name, data in files.items()},
        "anchor_boundary": "Caller-held digests bind bytes; they do not authenticate the caller or provider.",
        "observations": observations,
        **prior.describe([row["eligible_port_counts"] for row in observations]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--submission-sha256", required=True)
    parser.add_argument("--results-sha256", required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            analyze(args.run, submission_sha256=args.submission_sha256, results_sha256=args.results_sha256),
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
