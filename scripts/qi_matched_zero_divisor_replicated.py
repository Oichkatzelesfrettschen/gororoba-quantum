"""Replicated Tuna-17 matched-response proposal: one three-circuit batch per replicate, Stein two-stage t test.

The region-2 selector q11 proposal (scripts/qi_matched_zero_divisor_selector_q11.py) keeps its bytes. This producer
copies its routed circuit bytes without a compile: witness-a is the witness of its batch-01 (bright in region 1,
fixture in region 2), witness-b the witness of its batch-02 (fixture in region 1, dark in region 2), and the two
readout circuits are those of any batch. Each replicate batch holds witness-a, witness-b and one readout circuit,
so both weighted witnesses share one calibration window and a batch-by-region interaction leaves the residual
F_R2 - B_R1 + F_R1 - D_R2. The batch order of replicate i is in gororoba_quantum/qi_replicated_response.py.
The rule that fixes the number of replicates from the first 12 is documented there and in
docs/design/tuna17-matched-response-replicated.md. No mode contacts a provider.

Usage: "$PYTHON" scripts/qi_matched_zero_divisor_replicated.py --write DIR | --check DIR
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import qi_matched_response as frozen  # noqa: E402
import qi_replicated_response as rule  # noqa: E402

SOURCE = ROOT / "results/quantum_inspire/proposals/tuna17-zero-divisor-matched-response-region2-selector-q11"
PROPOSAL = ROOT / "results/quantum_inspire/proposals/tuna17-zero-divisor-matched-response-replicated-q11"
CIRCUIT_SOURCE = {
    rule.WITNESS_A: ("batch-01", "witness.cq"),
    rule.WITNESS_B: ("batch-02", "witness.cq"),
    rule.READOUT_ZERO: ("batch-01", "readout-0.cq"),
    rule.READOUT_ONE: ("batch-01", "readout-1.cq"),
}
PAUSE_SECONDS = 120


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json(value: Any) -> str:
    return json.dumps(value, indent=1) + "\n"


def _cost(source: dict[str, Any], replicates: int) -> dict[str, Any]:
    seconds = source["expected_device_seconds"] / source["jobs"]
    jobs = 3 * replicates
    return {
        "replicates": replicates,
        "batches": replicates,
        "jobs": jobs,
        "total_shots": jobs * source["shots_per_job"],
        "expected_device_seconds": round(jobs * seconds, 5),
        "minimum_total_interbatch_pause_seconds": (replicates - 1) * PAUSE_SECONDS,
        "expected_metered_credits": 0,
    }


def build() -> dict[str, str]:
    source = json.loads((SOURCE / "proposal.json").read_text())
    if _sha((SOURCE / "proposal.json").read_bytes()) != frozen.PROPOSAL_SHA256:
        raise ValueError("the q11 proposal.json differs from its frozen digest")
    texts: dict[str, bytes] = {}
    for name, (batch, file) in CIRCUIT_SOURCE.items():
        data = (SOURCE / batch / file).read_bytes()
        if _sha(data) != frozen.CIRCUIT_SHA256[batch][file]:
            raise ValueError(f"{batch}/{file} differs from its frozen digest")
        texts[name] = data
    if frozen.CIRCUIT_SHA256["batch-01"]["readout-0.cq"] != frozen.CIRCUIT_SHA256["batch-02"]["readout-0.cq"]:
        raise ValueError("the readout circuits differ between batches")
    circuits = {name: {"source": "/".join(CIRCUIT_SOURCE[name]), "sha256": _sha(data)} for name, data in texts.items()}
    files: dict[str, str] = {}
    rows = []
    for index in range(rule.CAP):
        batch = rule.batch_name(index)
        order = rule.schedule(index)
        manifest = {
            "schema": rule.SCHEMA_MANIFEST,
            "backend": source["backend"],
            "backend_type_id": 7,
            "nqubits": 17,
            "shots": source["shots_per_job"],
            "batch": batch,
            "replicate": index,
            "stage": 1 if index < rule.N1 else 2,
            "circuits": [{"file": file, "sha256": circuits[file]["sha256"]} for file in order],
            "witnesses": {file: list(cases) for file, cases in rule.WITNESS_CASES.items()},
            "catalogue_sha256": source["catalogue_sha256"],
            "provider_execution_authorized": False,
        }
        text = _json(manifest)
        files[f"{batch}/cases.json"] = text
        for file in order:
            files[f"{batch}/{file}"] = texts[file].decode()
        rows.append({"replicate": index, "batch": batch, "order": order, "manifest_sha256": _sha(text.encode())})
    files["cases.json"] = _json(
        {"schema": "qi-matched-zero-divisor-replicated-series-v1", "batches": [r["batch"] for r in rows]}
    )
    proposal = {
        "schema": rule.SCHEMA_PROPOSAL,
        "backend": source["backend"],
        "shots_per_job": source["shots_per_job"],
        "circuits_per_batch": 3,
        "provider_execution_authorized": False,
        "catalogue_sha256": source["catalogue_sha256"],
        "supersedes": SOURCE.relative_to(ROOT).as_posix(),
        "circuit_source": SOURCE.relative_to(ROOT).as_posix(),
        "circuits": circuits,
        "regions": source["regions"],
        "contrast": {
            "labels": list(rule.LABELS),
            "weights": list(rule.WEIGHTS),
            "estimand": "raw per-replicate residual F_R2 - B_R1 + F_R1 - D_R2; affine null (g2 - g1) / 2 = 0",
        },
        "design": {
            "n1": rule.N1,
            "cap": rule.CAP,
            "alpha": rule.ALPHA,
            "power": rule.POWER,
            "delta": rule.DELTA,
            "degrees_of_freedom": rule.DF,
            "critical_t": rule.T_CRIT,
            "shift": rule.SHIFT,
            "c": rule.C,
            "total_rule": "N = max(n1, ceil(s1^2 / c)) with s1 the sample SD of replicates 0..n1-1 only",
            "statistic": "t = mean(r_0..r_(N-1)) * sqrt(N) / s1; reject when abs(t) >= critical_t",
            "over_cap": "undecided at the cap: stop after stage 1 and report the stage-1 mean with its interval",
        },
        "pause_seconds": PAUSE_SECONDS,
        "cost": {
            "stage_1": _cost(source, rule.N1),
            "cap": _cost(source, rule.CAP),
            "basis": "per-circuit seconds of the q11 proposal expected_device_seconds over its jobs",
        },
        "schedule": rows,
    }
    files["proposal.json"] = _json(proposal)
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path)
    mode.add_argument("--check", type=Path)
    arguments = parser.parse_args()
    destination = arguments.write if arguments.write is not None else arguments.check
    files = build()
    actual = {path.relative_to(destination).as_posix() for path in destination.rglob("*") if path.is_file()}
    if arguments.check and actual != set(files):
        raise ValueError("replicated proposal directory differs in its file set")
    if actual - set(files):
        raise ValueError("replicated proposal directory contains unexpected files")
    for name, text in files.items():
        path = destination / name
        if arguments.check or path.exists():
            if not path.is_file() or path.read_text() != text:
                raise ValueError(f"replicated proposal differs at {name}; retain a separately named successor")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
    print(f"validated {rule.CAP} unsubmitted replicate batches ({rule.N1} in stage 1)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
