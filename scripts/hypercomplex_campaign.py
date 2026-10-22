"""Plan or execute a frozen Quantum Inspire campaign through qi_platform.

Execution requires the written approval text and the digest printed by plan.
Every batch passes the existing account-wide pacing and durable submission
guards. A partially created batch stops execution for read-only reconciliation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from hypercomplex_dynamics import shot_diagnostics  # noqa: E402


def campaign_plan(directory: Path) -> dict[str, Any]:
    paths = sorted(directory.glob("*/cases.json"))
    if not paths:
        raise ValueError("campaign has no batch manifests")
    bindings: dict[str, str] = {}
    shots_total = 0
    execution_seconds = 0.0
    native_errors = []
    for path in paths:
        data = path.read_bytes()
        manifest = json.loads(data)
        rows = manifest["circuits"]
        if manifest.get("schema") != "qi-hypercomplex-cases-v1" or len(rows) != 3:
            raise ValueError("a hypercomplex batch needs exactly three circuits")
        if manifest["backend_type_id"] != 7 or manifest["backend"] != "tuna_17":
            raise ValueError("the frozen campaign must bind Tuna-17 explicitly")
        shots = manifest["shots"]
        if type(shots) is not int or not 1 <= shots <= 131072 or manifest["hardware_pause_seconds"] != 120:
            raise ValueError("batch shot or pause policy differs from the admitted limits")
        if manifest["job_execution_time_limit"] != 300:
            raise ValueError("the admitted per-circuit execution limit is 300 seconds")
        if rows[0].get("prepared") != 0 or rows[1].get("prepared") != 1:
            raise ValueError("each batch needs its own ordered readout references")
        names = [row["file"] for row in rows]
        if len(set(names)) != 3 or any(Path(name).name != name or not name.endswith(".cq") for name in names):
            raise ValueError("batch circuits need three distinct local cQASM filenames")
        bindings[path.relative_to(directory).as_posix()] = hashlib.sha256(data).hexdigest()
        for row in rows:
            circuit = path.parent / row["file"]
            digest = hashlib.sha256(circuit.read_bytes()).hexdigest()
            if digest != row["sha256"]:
                raise ValueError("circuit differs from its manifest digest")
            bindings[circuit.relative_to(directory).as_posix()] = digest
        native_errors.append(rows[2]["operator_error"])
        seconds = 2.6 + 0.00053 * shots
        if seconds > 240:
            raise ValueError("estimated circuit duration leaves less than sixty seconds of headroom")
        execution_seconds += 3 * seconds
        shots_total += 3 * shots
    digest = hashlib.sha256(json.dumps(bindings, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {
        "schema": "qi-hypercomplex-plan-v1",
        "plan_sha256": digest,
        "bindings": bindings,
        "batch_count": len(paths),
        "circuits": 3 * len(paths),
        "shots_total": shots_total,
        "modeled_execution_seconds": execution_seconds,
        "minimum_interbatch_pause_seconds": 120 * (len(paths) - 1),
        "maximum_native_operator_error": max(native_errors),
        "metered_credit_debit": "no tariff inferred from empty ledger",
        "interpretation": "complex-encoded device conformance; requested and quantized operators are distinct",
    }


def analyze_batch(directory: Path) -> dict[str, Any]:
    import qi_platform

    receipt_path = directory / "submission.json"
    receipt = json.loads(receipt_path.read_text())
    if receipt.get("schema") != qi_platform.SUBMISSION_SCHEMA:
        raise ValueError("hypercomplex acquisitions require the current digest-bound submission receipt")
    qi_platform._check_submission_manifest(directory, receipt, require_enqueued=True)
    manifest = json.loads((directory / "cases.json").read_text())
    science = manifest["circuits"][2]
    path = directory / "raw" / f"{science['file']}.json"
    shots = json.loads(path.read_text())
    width = science["nqubits"]
    if len(shots) != manifest["shots"] or any(
        not isinstance(shot, str) or len(shot) != width or set(shot) - {"0", "1"} for shot in shots
    ):
        raise ValueError("Tuna science shots need the declared full bit-register width")
    reference_probabilities = []
    raw_digests = {}
    for row in manifest["circuits"][:2]:
        reference_path = directory / "raw" / f"{row['file']}.json"
        reference = json.loads(reference_path.read_text())
        raw_digests[row["file"]] = hashlib.sha256(reference_path.read_bytes()).hexdigest()
        if len(reference) != manifest["shots"] or any(
            not isinstance(shot, str) or len(shot) != width or set(shot) - {"0", "1"} for shot in reference
        ):
            raise ValueError("each contemporaneous readout reference needs all requested valid shots")
        reference_probabilities.append(
            [sum(shot[-1 - qubit] == "1" for shot in reference) / len(reference) for qubit in range(width)]
        )
    physical_contrasts = [high - low for low, high in zip(*reference_probabilities, strict=True)]
    mapping = science["measurement_mapping"]
    if sorted(mapping) != list(range(width)):
        raise ValueError("science measurement mapping must permute the physical register")
    contrasts = [physical_contrasts[physical] for physical in mapping]
    if min(contrasts[1:]) < 0.2:
        raise ValueError("readout-reference contrast falls below the preregistered 0.2 quality boundary")
    counts = Counter(int(shot, 2) // 2 for shot in shots)
    count_vector = [counts[index] for index in range(2 ** (width - 1))]
    observed = [count / len(shots) for count in count_vector]
    predictions = {}
    residuals = {}
    for label in ("requested", "native"):
        resolved = science[f"{label}_probabilities"]
        if len(resolved) != 2**width or any(not math.isfinite(value) or value < 0 for value in resolved):
            raise ValueError("predicted probabilities need finite nonnegative full-register values")
        grouped = [sum(resolved[index : index + 2]) for index in range(0, len(resolved), 2)]
        if not math.isclose(sum(grouped), 1, abs_tol=1e-12, rel_tol=0):
            raise ValueError("predicted probabilities must have unit total")
        predictions[label] = grouped
        residuals[label] = [actual - expected for actual, expected in zip(observed, grouped, strict=True)]
    diagnostics = shot_diagnostics([int(int(shot, 2) // 2 != 0) for shot in shots]) if len(shots) >= 16 else None
    return {
        "schema": "hypercomplex-measured-frame-v1",
        "evidence_kind": "hardware-measurement",
        "time": science["setting"].get("time", 0),
        "setting": science["setting"],
        "counts": count_vector,
        "probabilities": observed,
        "grouped_predictions": predictions,
        "observed_minus_predicted": residuals,
        "total_variation_residual": {
            label: sum(abs(value) for value in values) / 2 for label, values in residuals.items()
        },
        "raw_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "reference_raw_sha256": raw_digests,
        "receipt_sha256": hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
        "manifest_sha256": hashlib.sha256((directory / "cases.json").read_bytes()).hexdigest(),
        "ordered_shots": diagnostics,
        "operator_error": science["operator_error"],
        "readout_contrasts": contrasts,
        "physical_readout_contrasts": physical_contrasts,
        "physical_readout_one_probabilities": reference_probabilities,
        "logical_readout_one_probabilities": [
            [row[physical] for physical in mapping] for row in reference_probabilities
        ],
        "inference_scope": "descriptive acquisition; conformance, equivalence and ray invariance unestablished",
        "acquisition_quality": "output readout contrast >=0.2 only; no bias correction or scientific acceptance",
        "scientific_continuation_admitted": False,
        "job_id": next(row["job"] for row in receipt["jobs"] if row["file"] == science["file"]),
    }


def measured_wave(directory: Path) -> dict[str, Any]:
    """Collect the seventeen distinct primary wave times from retained raw batches."""
    frames = []
    for path in sorted(directory.glob("*/cases.json")):
        manifest = json.loads(path.read_text())
        setting = manifest["circuits"][2]["setting"]
        if setting.get("coupling") == 1 and setting.get("representative") == 0 and "time" in setting:
            retained_path = path.parent / "hypercomplex-analysis.json"
            retained = json.loads(retained_path.read_text())
            if analyze_batch(path.parent) != retained:
                raise ValueError("raw acquisition differs from its retained per-batch analysis")
            frames.append(retained)
    frames.sort(key=lambda frame: frame["time"])
    if [frame["time"] for frame in frames] != [index / 8 for index in range(17)]:
        raise ValueError("measured wave rendering requires all seventeen distinct preregistered primary times")
    return {
        "evidence_kind": "hardware-measurement",
        "frames": frames,
        "provenance": "Quantum Inspire Tuna-17 raw acquisitions; paired encoding channels; phase unmeasured",
        "phase_measured": False,
    }


def execute(directory: Path, approval: str, approved_sha256: str, max_wait_seconds: float) -> None:
    if not approval.strip():
        raise ValueError("written case approval is required")
    plan = campaign_plan(directory)
    if approved_sha256 != plan["plan_sha256"]:
        raise ValueError("the approved plan digest differs from the current cases")
    if not math.isfinite(max_wait_seconds) or max_wait_seconds <= 0:
        raise ValueError("max wait must be finite and positive")
    import qi_platform

    container = {
        "schema": "qi-campaign-v1",
        "plan_sha256": approved_sha256,
        "batches": {
            Path(name).parent.name: digest for name, digest in plan["bindings"].items() if name.endswith("/cases.json")
        },
    }
    container_path = directory / "campaign.json"
    container_text = json.dumps(container, indent=1) + "\n"
    if container_path.exists():
        if container_path.read_text() != container_text:
            raise ValueError("campaign container differs from the approved batch identities")
    else:
        qi_platform._write_json(container_path, container, exclusive=True)
    deadline = time.monotonic() + max_wait_seconds
    for path in sorted(directory.glob("*/cases.json")):
        batch = path.parent
        if campaign_plan(directory)["plan_sha256"] != approved_sha256:
            raise ValueError("campaign changed after approval")
        if (batch / "submission-state.json").exists() and not (batch / "submission.json").exists():
            raise ValueError("partial submission requires read-only reconciliation before continuation")
        if not (batch / "submission.json").exists():
            while True:
                if time.monotonic() >= deadline:
                    raise TimeoutError("account hardware wait exceeded the approved execution window")
                client = qi_platform.Client()
                try:
                    remaining = qi_platform.hardware_pause_left(client)
                except SystemExit as error:
                    message = str(error)
                    if "wait until" not in message:
                        raise
                    remaining = 30
                if remaining == 0:
                    break
                print(f"account hardware pause: {remaining} seconds remaining", flush=True)
                time.sleep(min(30, remaining))
            intent = {
                "schema": "qi-campaign-intent-v1",
                "plan_sha256": approved_sha256,
                "cases_sha256": plan["bindings"][path.relative_to(directory).as_posix()],
            }
            intent_path = batch / "execution-intent.json"
            if intent_path.exists():
                if json.loads(intent_path.read_text()) != intent:
                    raise ValueError("batch execution intent differs from the approved identities")
            else:
                qi_platform._write_json(intent_path, intent, exclusive=True)
            if (batch / "preflight-refusal.json").exists():
                raise ValueError("a retained preflight refusal requires a separately recorded retry")
            try:
                qi_platform.submit(
                    batch, 7, approval, expected_cases_sha256=intent["cases_sha256"], execution_deadline=deadline
                )
            except BaseException:
                with qi_platform.token_lock(qi_platform.SUBMIT_LOCK):
                    if qi_platform.pre_dispatch_refused(batch, intent["cases_sha256"]) or not any(
                        (batch / name).exists()
                        for name in ("submission-state.json", "submission.json", "results.json", "raw")
                    ):
                        # The submitter syncs its creation state and checks refusals under the same lock.
                        refusal = {**intent, "schema": "qi-campaign-refusal-v1", "phase": "preflight-refused"}
                        refusal_path = batch / "preflight-refusal.json"
                        if refusal_path.exists():
                            if json.loads(refusal_path.read_text()) != refusal:
                                raise ValueError(
                                    "retained preflight refusal differs from the approved identities"
                                ) from None
                        else:
                            qi_platform._write_json(refusal_path, refusal, exclusive=True)
                raise
        qi_platform.collect(batch, poll=10, timeout=max_wait_seconds, execution_deadline=deadline)
        analysis = analyze_batch(batch)
        analysis_path = batch / "hypercomplex-analysis.json"
        text = json.dumps(analysis, indent=1) + "\n"
        if analysis_path.exists() and analysis_path.read_text() != text:
            raise ValueError("retained analysis differs; preserve it and use a separately versioned analysis")
        if not analysis_path.exists():
            analysis_path.write_text(text)
        print(f"collected and checked {batch.name}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--measured-wave", type=Path)
    parser.add_argument("--approval", default="")
    parser.add_argument("--approved-plan-sha256", default="")
    parser.add_argument("--max-wait-seconds", type=float, default=7200)
    args = parser.parse_args()
    if args.measured_wave:
        if args.execute:
            parser.error("measurement rendering and execution are separate operations")
        payload = json.dumps(measured_wave(args.directory), indent=1) + "\n"
        if args.measured_wave.exists() and args.measured_wave.read_text() != payload:
            raise ValueError("refusing to overwrite a different measured-wave record")
        args.measured_wave.write_text(payload)
    elif args.execute:
        execute(args.directory, args.approval, args.approved_plan_sha256, args.max_wait_seconds)
    else:
        print(json.dumps(campaign_plan(args.directory), indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
