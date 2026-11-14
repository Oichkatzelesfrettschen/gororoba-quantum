"""Analyze an Ascella target-slot acquisition built by scripts/ascella_predecessor_acquisition_case.py.

The analysis admits a run only when its cases.json equals the successor request for the platform the request names,
so the request's sha256 is the admission key; the frozen analyzer admits its own request alone and refuses this one.
Every check of ascella_predecessor_current_analysis.analyze stays: the anchored receipt and result digests, the
offline run facts, the status and duration, the sent body, the eight iterations and the descriptive statistics.
This module rebinds that function to the successor request (`current`), to a sent-body check that takes the
platform from the request, and, on sim:ascella, to the simulator reader's iteration check, which reports whether the
returned compilation reproduces the preregistered one where the QPU case requires it. qd_platform.run_facts, which
the rebound function calls, refuses a receipt whose platform lies outside the request.

Usage:
  "$PYTHON" scripts/ascella_predecessor_acquisition_analysis.py RUN --submission-sha256 HEX --results-sha256 HEX
"""

from __future__ import annotations

import argparse
import json
import types
from pathlib import Path
from typing import Any

import ascella_predecessor_acquisition_case as acquisition
import ascella_predecessor_analysis as prior
import ascella_predecessor_current_analysis as current_analysis
import ascella_predecessor_simulator as simulator

from rebound import rebound

# The frozen iteration check requires the preregistered compilation; the simulator's reports it.
SIMULATOR_PRIOR = types.SimpleNamespace(**{**vars(prior), "_entry_worker": simulator._entry})
PRIOR = {"qpu:ascella": prior, "sim:ascella": SIMULATOR_PRIOR}


def sent_body(body: dict[str, Any], manifest: dict[str, Any], profile: dict[str, Any]) -> None:
    """The frozen sent-body validation with the request's platform in place of qpu:ascella, which it hard-codes."""
    platform = manifest["platforms"][0]
    if body.get("platform_name") != platform:
        raise ValueError(f"the sent body names {body.get('platform_name')!r}, not {platform}")
    prior.validate_sent_body(body | {"platform_name": "qpu:ascella"}, manifest, profile)


def analyze(directory: Path, *, submission_sha256: str, results_sha256: str) -> dict[str, Any]:
    """Validate the run against the successor request, then describe it; sim:ascella adds the identity report."""
    manifest = acquisition.check(directory)
    platform = manifest["platforms"][0]
    admitted = rebound(
        current_analysis.analyze, current=acquisition, validate_sent_body=sent_body, prior=PRIOR[platform]
    )
    report: dict[str, Any] = admitted(directory, submission_sha256=submission_sha256, results_sha256=results_sha256)
    report["schema"] = "ascella-predecessor-acquisition-analysis-v1"
    report["platform"] = platform
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("run", type=Path)
    parser.add_argument("--submission-sha256", required=True)
    parser.add_argument("--results-sha256", required=True)
    args = parser.parse_args()
    report = analyze(args.run, submission_sha256=args.submission_sha256, results_sha256=args.results_sha256)
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
