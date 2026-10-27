"""Freeze three nominal-one destination controls with an explicit queue-aware request horizon."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from qi_tuna_destination_sequential_cases import PROPOSAL as PREDECESSOR
from qi_tuna_destination_sequential_cases import generate as generate_predecessor
from qi_tuna_readout_mapping_cases import ROOT, encoded, sha

PROPOSAL = ROOT / "results/quantum_inspire/proposals/tuna-readout-destination-one"
ANALYZER = "scripts/qi_tuna_destination_one_analysis.py"
RUNNER = "scripts/qi_tuna_destination_one_run.py"
ANALYSIS_NOTE = "docs/evidence/tuna-projector-geometry/destination-one-response-uncertainty.md"
ARMS = ("baseline-before", "rotated-destinations", "baseline-after")
PREPARATIONS = ("prepared-one",)


def build(predecessor_files: dict[str, str]) -> dict[str, str]:
    """Select the three one-preparation manifests without changing their source or manifest bytes."""
    predecessor = json.loads(predecessor_files["campaign.json"])
    batches = [row for row in predecessor["batches"] if row["prepared_label"] == 1]
    if [row["name"] for row in batches] != [f"prepared-one-{arm}" for arm in ARMS]:
        raise ValueError("predecessor nominal-one sequence differs")
    files: dict[str, str] = {}
    for batch in batches:
        for filename in ("cases.json", "backend.json", batch["source_file"]):
            relative = f"{batch['name']}/{filename}"
            files[relative] = predecessor_files[relative]
        if sha(files[f"{batch['name']}/cases.json"]) != batch["cases_sha256"]:
            raise ValueError("predecessor manifest digest differs")
        relative = f"local-compiled/{batch['name']}/{batch['source_file']}"
        files[relative] = predecessor_files[relative]
    compiler = json.loads(predecessor_files["compiler-admission.json"])
    selected = {f"{batch['name']}/{batch['source_file']}" for batch in batches}
    compiler.update(
        schema="qi-tuna-destination-one-compiler-v1",
        command='"$QI_PYTHON" scripts/qi_tuna_destination_one_cases.py --check',
        circuits=[row for row in compiler["circuits"] if row["source"] in selected],
        predecessor_compiler_receipt_sha256=sha(predecessor_files["compiler-admission.json"]),
    )
    if {row["source"] for row in compiler["circuits"]} != selected:
        raise ValueError("compiler receipt lacks a selected source")
    files["compiler-admission.json"] = encoded(compiler)
    inputs = (
        Path(__file__).relative_to(ROOT).as_posix(),
        RUNNER,
        "scripts/qi_tuna_destination_sequential_cases.py",
        "scripts/qi_tuna_destination_sequential_run.py",
        "scripts/qi_tuna_readout_mapping_cases.py",
        "scripts/qi_tuna_readout_destination_analysis.py",
        "scripts/qi_projector_compiler_admission.py",
        "scripts/qi_toolchain_check.py",
        "scripts/qi_projector_live_admission.py",
        "scripts/qi_platform.py",
        "scripts/qi_platform_submission_deadline.py",
        "scripts/acquisition_decisions.py",
        "gororoba_quantum/parallel.py",
        "gororoba_quantum/qi_stack.py",
    )
    files["campaign.json"] = encoded(
        {
            "schema": "qi-tuna-destination-one-campaign-v1",
            "status": "frozen-for-review",
            "provider_execution_authorized": False,
            "scope": "Separate nominal-one predictable-response comparison; causal attribution remains unresolved.",
            "batches": batches,
            "ordering": "Three single-job batches; collect and validate each job before creating its successor.",
            "shots_per_circuit": 4096,
            "shots_total": 12288,
            "circuits_total": 3,
            "expected_execution_seconds_decimal": "14.688660",
            "provider_execution_ceiling_seconds": 900,
            "expected_credits": 0,
            "minimum_interjob_pause_seconds": 30,
            "minimum_internal_pauses": 2,
            "heartbeat_max_age_seconds": 120,
            "campaign_request_initiation_timeout_seconds": 7200,
            "queue_horizon_basis": {
                "observed_queue_maximum_seconds": 1680,
                "three_waits_plus_execution_ceiling_and_pauses_seconds": 6000,
                "additional_admission_collection_allowance_seconds": 1200,
                "boundary": "Observed waits motivate an operator allowance; future queue waits remain unbounded.",
            },
            "admission_max_age_seconds": 60,
            "admission_age_origin": "request_started_utc; includes policy reads, API reads and submit-lock wait",
            "timing_boundary": "Execution estimate excludes queue, compilation, collection, and account pauses.",
            "stopping": (
                "Stop operational invalidity, ambiguity, structural drift or charges; no statistical early stop."
            ),
            "analysis_contract": {
                "file": ANALYZER,
                "sha256": sha((ROOT / ANALYZER).read_bytes()),
                "mathematical_note": {"file": ANALYSIS_NOTE, "sha256": sha((ROOT / ANALYSIS_NOTE).read_bytes())},
            },
            "producer_inputs": {name: sha((ROOT / name).read_bytes()) for name in inputs},
            "compiler_receipt_sha256": sha(files["compiler-admission.json"]),
            "predecessor_campaign": {
                "file": (PREDECESSOR / "campaign.json").relative_to(ROOT).as_posix(),
                "sha256": sha(predecessor_files["campaign.json"]),
                "boundary": "Separate execution and primary decision; predecessor missing jobs stay unsubmitted.",
            },
        }
    )
    return files


def generate() -> dict[str, str]:
    return build(generate_predecessor())


def check(proposal: Path) -> dict[str, Any]:
    files = generate()
    actual = {path.relative_to(proposal).as_posix(): path.read_text() for path in proposal.rglob("*") if path.is_file()}
    if actual != files:
        raise ValueError("nominal-one proposal differs from full source/compiler replay")
    return json.loads(files["campaign.json"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", nargs="?", type=Path, const=PROPOSAL)
    args = parser.parse_args()
    if args.check:
        check(args.check)
        print("three nominal-one cases and compiler evidence replay; execution requires separate exact-case approval")
    else:
        files = generate()
        args.out.mkdir(parents=True, exist_ok=False)
        for relative, content in files.items():
            path = args.out / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("x", encoding="utf-8") as destination:
                destination.write(content)


if __name__ == "__main__":
    main()
