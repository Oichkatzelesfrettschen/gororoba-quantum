"""Analyze the collected batches of the Tuna-17 matched zero-divisor response series.

Reads the proposal record and the three collected batch runs, writes or prints
the analysis of gororoba_quantum/qi_matched_response.py. The decision rule is
fixed in docs/design/tuna17-matched-response-analysis.md. No provider call.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from qi_matched_zero_divisor import matched_response_contrast  # noqa: E402

from qi_matched_response import analyze_matched_series, proposal_digests, verify_run_binding  # noqa: E402
from qi_records import load_run, validate_run  # noqa: E402

PROPOSAL = ROOT / "results/quantum_inspire/proposals/tuna17-zero-divisor-matched-response-ordered-map-cancel"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runs", nargs=3, type=Path, help="collected run directories, one per batch")
    parser.add_argument("--proposal", type=Path, default=PROPOSAL)
    parser.add_argument("--out", type=Path)
    arguments = parser.parse_args()
    proposal = json.loads((arguments.proposal / "proposal.json").read_text())
    expected = proposal_digests(arguments.proposal)
    manifests = {}
    shots = {}
    bound = {}
    for directory in arguments.runs:
        record = load_run(directory)
        acquisition = validate_run(record, f"Quantum Inspire run {directory.name}")
        if not acquisition.completed:
            raise ValueError(f"{directory.name}: not every job completed")
        manifest = json.loads((directory / "cases.json").read_text())
        name = manifest["batch"]
        if name in manifests:
            raise ValueError(f"{directory.name}: batch {name} appears twice")
        if acquisition.backend != proposal["backend"]:
            raise ValueError(f"{directory.name}: the run used another backend")
        bound[name] = verify_run_binding(expected, name, record)
        manifests[name] = manifest
        for job in acquisition.jobs:
            shots[name, job.file] = job.raw
    analysis = analyze_matched_series(proposal, manifests, shots, contrast=matched_response_contrast)
    analysis["binding"] = {"proposal": expected, "runs": bound}
    rendered = json.dumps(analysis, indent=1)
    if arguments.out is None:
        print(rendered)
    else:
        arguments.out.write_text(rendered + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
