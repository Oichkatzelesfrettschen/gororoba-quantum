"""Freeze six single-job Tuna destination controls with verified serial execution ordering."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from qi_tuna_readout_mapping_cases import PROPOSAL as PRIOR_PROPOSAL
from qi_tuna_readout_mapping_cases import ROOT, encoded, sha
from qi_tuna_readout_mapping_cases import generate as generate_prior

PROPOSAL = ROOT / "results/quantum_inspire/proposals/tuna-readout-destination-sequential"
ANALYZER = "scripts/qi_tuna_readout_destination_analysis.py"
RUNNER = "scripts/qi_tuna_destination_sequential_run.py"
ANALYSIS_NOTE = "docs/evidence/tuna-projector-geometry/destination-response-uncertainty.md"
PREPARATIONS = ("prepared-zero", "prepared-one")
ARMS = ("baseline-before", "rotated-destinations", "baseline-after")


def build(prior_files: dict[str, str]) -> dict[str, str]:
    """Rehouse the reviewed six sources into one circuit per ordered batch."""
    files: dict[str, str] = {}
    batches = []
    compiler = json.loads(prior_files["local-compiler-receipt.json"])
    compiler_rows = {row["source"]: row for row in compiler["circuits"]}
    new_compiler_rows = []
    for preparation in PREPARATIONS:
        old_manifest_path = f"{preparation}/cases.json"
        old_manifest = json.loads(prior_files[old_manifest_path])
        for arm in ARMS:
            row = next(entry for entry in old_manifest["circuits"] if entry["name"] == arm)
            batch = f"{preparation}-{arm}"
            filename = row["file"]
            original = f"{preparation}/{filename}"
            source = prior_files[original]
            if sha(source) != row["sha256"]:
                raise ValueError("source differs from the predecessor manifest")
            manifest = {
                "schema": "qi-tuna-destination-single-job-case-v1",
                "status": "frozen-for-review",
                "provider_execution_authorized": False,
                "backend": "tuna_17",
                "backend_type_id": 7,
                "nqubits": 17,
                "shots": 4096,
                "prepared_label": old_manifest["prepared_label"],
                "comparison_arm": arm,
                "circuits": [row],
                "backend_snapshot": old_manifest["backend_snapshot"],
                "expected_execution_seconds_decimal": "4.948185" if preparation == "prepared-zero" else "4.896220",
                "provider_execution_ceiling_seconds": 300,
                "execution_order_rule": "Collect and validate this sole job before the next batch can be created.",
                "limits": {"circuits_per_batch": 1, "account_queued_batches": 1, "job_seconds": 300},
                "predecessor_manifest": {
                    "file": (PRIOR_PROPOSAL / old_manifest_path).relative_to(ROOT).as_posix(),
                    "sha256": sha(prior_files[old_manifest_path]),
                },
            }
            files[f"{batch}/{filename}"] = source
            files[f"{batch}/backend.json"] = prior_files[f"{preparation}/backend.json"]
            files[f"{batch}/cases.json"] = encoded(manifest)
            compiled = prior_files[f"local-compiled/{original}"]
            files[f"local-compiled/{batch}/{filename}"] = compiled
            new_compiler_rows.append(compiler_rows[original] | {"source": f"{batch}/{filename}"})
            batches.append(
                {
                    "name": batch,
                    "prepared_label": old_manifest["prepared_label"],
                    "comparison_arm": arm,
                    "cases_sha256": sha(encoded(manifest)),
                    "source_file": filename,
                    "source_sha256": row["sha256"],
                }
            )
    compiler.update(
        schema="qi-tuna-destination-sequential-compiler-v1",
        command='"$QI_PYTHON" scripts/qi_tuna_destination_sequential_cases.py --check',
        circuits=new_compiler_rows,
        predecessor_compiler_receipt_sha256=sha(prior_files["local-compiler-receipt.json"]),
    )
    files["compiler-admission.json"] = encoded(compiler)
    inputs = (
        Path(__file__).relative_to(ROOT).as_posix(),
        RUNNER,
        "scripts/qi_projector_live_admission.py",
        "scripts/qi_platform.py",
        "scripts/acquisition_decisions.py",
    )
    files["campaign.json"] = encoded(
        {
            "schema": "qi-tuna-destination-sequential-campaign-v1",
            "status": "frozen-for-review",
            "provider_execution_authorized": False,
            "scope": (
                "Descriptive destination-response comparison under two prepared labels; excludes causal attribution."
            ),
            "batches": batches,
            "ordering": "Six single-job batches; each completed and collected before creation of its successor.",
            "shots_per_circuit": 4096,
            "shots_total": 24576,
            "circuits_total": 6,
            "expected_execution_seconds_decimal": "29.533215",
            "provider_execution_ceiling_seconds": 1800,
            "expected_credits": 0,
            "minimum_interjob_pause_seconds": 30,
            "minimum_internal_pauses": 5,
            "heartbeat_max_age_seconds": 120,
            "campaign_request_initiation_timeout_seconds": 3600,
            "admission_max_age_seconds": 60,
            "admission_age_origin": "request_started_utc; includes policy reads, API reads and submit-lock wait",
            "timing_boundary": "Execution estimate excludes queue, compilation, collection, and account pauses.",
            "stopping": (
                "Stop operational invalidity, ambiguity, structural drift, or charges; no statistical early stop."
            ),
            "analysis_contract": {
                "file": ANALYZER,
                "sha256": sha((ROOT / ANALYZER).read_bytes()),
                "mathematical_note": {"file": ANALYSIS_NOTE, "sha256": sha((ROOT / ANALYSIS_NOTE).read_bytes())},
            },
            "producer_inputs": {name: sha((ROOT / name).read_bytes()) for name in inputs},
            "compiler_receipt_sha256": sha(files["compiler-admission.json"]),
            "predecessor_proposal_sha256": sha(prior_files["proposal.json"]),
        }
    )
    return files


def generate() -> dict[str, str]:
    return build(generate_prior())


def check(proposal: Path) -> dict[str, Any]:
    files = generate()
    actual = {path.relative_to(proposal).as_posix(): path.read_text() for path in proposal.rglob("*") if path.is_file()}
    if actual != files:
        raise ValueError("sequential proposal differs from full source/compiler replay")
    return json.loads(files["campaign.json"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", nargs="?", type=Path, const=PROPOSAL)
    args = parser.parse_args()
    if args.check:
        check(args.check)
        print("six single-job cases and compiler evidence replay; execution requires separate exact-case approval")
    else:
        files = generate()
        args.out.mkdir(parents=True, exist_ok=False)
        for relative, content in files.items():
            path = args.out / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("x", encoding="utf-8") as output:
                output.write(content)


if __name__ == "__main__":
    main()
