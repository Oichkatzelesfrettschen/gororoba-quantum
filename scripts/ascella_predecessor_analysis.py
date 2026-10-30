"""Analyze the frozen Ascella target-slot contrast from retained provider files.

The default output is descriptive. Conditional confidence envelopes require
an externally digest-anchored, pre-acquisition sampling contract. The analyzer
never identifies physical predecessor causation from returned iterator order.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import tempfile
from datetime import datetime
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Any

import ascella_predecessor_case as case
import qd_platform as qd
from ascella_experiment_analysis import attribute_iteration, validate_sent_body
from experiment_analysis import decode_photonic_counts

from parallel import ordered_map

PROFILE = {"samples_per_setting": case.SAMPLES_PER_ITERATION, "detected_shot_cap_per_setting": case.SHOTS_PER_ITERATION}
TARGETS = (1, 3, 5, 7)
COMMON = (Fraction(1, 2), Fraction(-1, 2), Fraction(-1, 2), Fraction(1, 2))
REVERSAL = (Fraction(-1, 2), Fraction(1, 2), Fraction(-1, 2), Fraction(1, 2))
MODEL = "iid-categorical-returned-events-within-each-iteration"
STOPPING = "fixed-returned-event-count-with-conditional-single-photon-eligibility"
EVIDENCE_CLAIMS = {"sampling-model-review", "stopping-rule-review", "temporal-limitations-review"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reject_constant(value: str) -> None:
    raise ValueError(f"nonfinite JSON constant {value}")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for name, value in pairs:
        if name in result:
            raise ValueError(f"duplicate JSON member {name}")
        result[name] = value
    return result


def _parse_json(data: bytes, label: str) -> dict[str, Any]:
    value = json.loads(data, parse_constant=_reject_constant, object_pairs_hook=_unique_object)
    if not isinstance(value, dict):
        raise ValueError(f"{label}: a JSON object is required")
    return value


def read_json(path: Path) -> dict[str, Any]:
    return _parse_json(path.read_bytes(), path.name)


def _manifest_bytes(manifest: dict[str, Any]) -> bytes:
    """Reconstruct the exact serialization verified by the case builder."""
    return (json.dumps(manifest, indent=1) + "\n").encode()


def _anchor(path: Path, expected: str) -> bytes:
    if (
        not isinstance(expected, str)
        or len(expected) != 64
        or any(character not in "0123456789abcdef" for character in expected)
    ):
        raise ValueError("an external expected sha256 must be 64 lowercase hexadecimal characters")
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError(f"{path.name}: external digest anchor differs")
    return data


def _time(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ValueError("contract and submission timestamps must be timezone-aware ISO strings")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("contract and submission timestamps require a timezone")
    return parsed


def validate_contract(path: Path, expected: str, manifest: dict[str, Any], submitted: str) -> dict[str, Any]:
    """Check an externally supplied anchor; hashes establish consistency, not evidence truth."""
    contract = _parse_json(_anchor(path, expected), path.name)
    required = {
        "schema": "ascella-predecessor-sampling-contract-v1",
        "cases_sha256": hashlib.sha256(_manifest_bytes(manifest)).hexdigest(),
        "analysis_sources": manifest["analysis_sources"],
        "sampling_model": MODEL,
        "stopping_rule": STOPPING,
        "eligibility": manifest["eligibility"],
        "scope": "hypothesis-conditional-target-slot-response",
        "physical_predecessor_attribution": "unavailable",
        "family_alpha": "0.05",
        "delta_tvd": "0.1",
    }
    if any(contract.get(key) != value for key, value in required.items()):
        raise ValueError("the sampling contract changes the frozen model, source, family or scope")
    if _time(contract.get("frozen_utc")) >= _time(submitted):
        raise ValueError("the sampling contract must freeze before submission")
    evidence = contract.get("evidence")
    if not isinstance(evidence, list) or len(evidence) != len(EVIDENCE_CLAIMS):
        raise ValueError("the sampling contract requires all three reviewed evidence bindings")
    claims: set[str] = set()
    for binding in evidence:
        if not isinstance(binding, dict) or binding.get("claim") not in EVIDENCE_CLAIMS:
            raise ValueError("a contract evidence binding has an unknown claim")
        claims.add(binding["claim"])
        filename = binding.get("file")
        if not isinstance(filename, str) or not filename or Path(filename).is_absolute():
            raise ValueError("contract evidence paths must be relative")
        artifact = path.parent / filename
        if not artifact.resolve().is_relative_to(path.parent.resolve()):
            raise ValueError("contract evidence escapes its declared directory")
        _anchor(artifact, binding.get("sha256", ""))
    if claims != EVIDENCE_CLAIMS:
        raise ValueError("the sampling contract omits a reviewed evidence claim")
    return contract


def _law(counts: list[int]) -> list[Fraction]:
    if len(counts) != case.MODES or any(type(number) is not int or number < 0 for number in counts):
        raise ValueError("an eligible law requires twelve nonnegative integer counts")
    total = sum(counts)
    if total < 1:
        raise ValueError("an eligible law needs at least one single-photon event")
    return [Fraction(number, total) for number in counts]


def signed_contrast(laws: list[list[Fraction]], weights: tuple[Fraction, ...]) -> list[Fraction]:
    if len(laws) != 4 or len(weights) != 4 or any(len(law) != case.MODES for law in laws):
        raise ValueError("the signed contrast requires four twelve-mode laws")
    return [
        sum((weight * law[mode] for weight, law in zip(weights, laws, strict=True)), Fraction()) for mode in range(12)
    ]


def variation(vector: list[Fraction]) -> Fraction:
    return sum(map(abs, vector), Fraction()) / 2


def radius(events: int) -> Decimal:
    """Round the eight-law subset-Hoeffding radius upward at every operation."""
    if type(events) is not int or events < 1:
        raise ValueError("a radius requires a positive eligible event count")
    with localcontext() as context:
        context.prec = 60
        context.rounding = ROUND_CEILING
        log_two = Decimal(2).ln().next_plus()
        log_family = (Decimal(8) / Decimal("0.05")).ln().next_plus()
        squared = (Decimal(12) * log_two + log_family) / Decimal(2 * events)
        return squared.sqrt().next_plus()


def _decimal(number: Fraction, rounding: str) -> Decimal:
    with localcontext() as context:
        context.prec = 60
        context.rounding = rounding
        return Decimal(number.numerator) / Decimal(number.denominator)


def envelope(observed: Fraction, uncertainty: Decimal) -> list[str]:
    with localcontext() as context:
        context.prec = 60
        context.rounding = ROUND_FLOOR
        lower = max(Decimal(0), _decimal(observed, ROUND_FLOOR) - uncertainty)
        context.rounding = ROUND_CEILING
        upper = min(Decimal(1), _decimal(observed, ROUND_CEILING) + uncertainty)
    return [str(lower), str(upper)]


def describe(counts: list[list[int]]) -> dict[str, Any]:
    if len(counts) != 8:
        raise ValueError("the frozen case requires eight attributed distributions")
    laws = [_law(row) for row in counts]
    targets = [laws[index] for index in TARGETS]
    common = signed_contrast(targets, COMMON)
    reversal = signed_contrast(targets, REVERSAL)
    pairs = [
        variation([a - b for a, b in zip(laws[left], laws[right], strict=True)]) for left, right in ((0, 2), (4, 6))
    ]
    return {
        "common_vector_exact": list(map(str, common)),
        "reversal_vector_exact": list(map(str, reversal)),
        "common_norm_exact": str(variation(common)),
        "reversal_norm_exact": str(variation(reversal)),
        "predecessor_tvd_exact": list(map(str, pairs)),
        "eligible_counts": [sum(row) for row in counts],
        "verdict": "descriptive-only",
        "physical_predecessor_attribution": "unavailable",
        "temporal_boundary": (
            "returned position attributes settings; physical order, target time spacing and carryover are unestablished"
        ),
        "drift_boundary": "quadratic symmetric drift can produce a positive common contrast and zero reversal contrast",
    }


def conditional_envelopes(description: dict[str, Any]) -> dict[str, Any]:
    """Give simultaneous model-conditional response bounds, never a physical-history verdict."""
    radii = [radius(events) for events in description["eligible_counts"]]
    with localcontext() as context:
        context.prec = 60
        context.rounding = ROUND_CEILING
        contrast_radius = sum((radii[index] / 2 for index in TARGETS), Decimal(0))
        predecessor_radii = [radii[0] + radii[2], radii[4] + radii[6]]
    common = envelope(Fraction(description["common_norm_exact"]), contrast_radius)
    reversal = envelope(Fraction(description["reversal_norm_exact"]), contrast_radius)
    predecessors = [
        envelope(Fraction(observed), uncertainty)
        for observed, uncertainty in zip(description["predecessor_tvd_exact"], predecessor_radii, strict=True)
    ]
    return {
        "common_norm_bounds": common,
        "reversal_norm_bounds": reversal,
        "predecessor_tvd_bounds": predecessors,
        "contrast_radius_upper_decimal": str(contrast_radius),
        "familywise_confidence": "0.95 conditional on the frozen sampling model",
        "coverage": "one simultaneous eight-law event covers every displayed deterministic contrast",
    }


def _conditional_decision(envelopes: dict[str, Any]) -> str:
    separated = all(Decimal(bounds[0]) > Decimal("0.1") for bounds in envelopes["predecessor_tvd_bounds"])
    common = envelopes["common_norm_bounds"]
    if separated and Decimal(common[0]) > Decimal("0.1"):
        return "conditional-slot-response-above-0.1-tvd"
    if separated and Decimal(common[1]) < Decimal("0.1"):
        return "conditional-slot-response-below-0.1-tvd"
    return "conditional-inconclusive"


def _entry(setting: dict[str, Any], entry: dict[str, Any], identities: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(entry, dict):
        raise ValueError("an attributed iteration requires an object")
    attribute_iteration({**setting, "setting_id": setting["name"]}, entry, PROFILE)
    fields = entry.get("result_fields", {})
    if not isinstance(fields, dict):
        raise ValueError("an attributed iteration requires returned metadata")
    expected = (
        identities["target"] if setting["role"] == "target" else identities["predecessors"][setting["source_name"]]
    )
    for name in ("computed_circuit", "computed_input"):
        returned = fields.get(name)
        if not isinstance(returned, str) or case.sha256_text(returned) != expected[f"{name}_sha256"]:
            raise ValueError(f"{setting['name']}: returned {name} identity differs")
    counts = entry.get("counts")
    if not isinstance(counts, dict):
        raise ValueError("an attributed iteration requires counted outcomes")
    ports, invalid = decode_photonic_counts(counts, case.MODES)
    total = sum(ports) + sum(invalid.values())
    if entry.get("samples") != total or type(entry.get("samples")) is not int or total != case.SAMPLES_PER_ITERATION:
        raise ValueError("every iteration must reach the fixed returned-event count")
    detected = fields.get("nb_shots_used")
    if type(detected) is not int or not total <= detected <= case.SHOTS_PER_ITERATION:
        raise ValueError("detected shots differ from the frozen budget")
    _law(ports)
    return {
        "name": setting["name"],
        "eligible_port_counts": ports,
        "invalid_event_counts": invalid,
        "returned_events": total,
    }


def _entry_worker(arguments: tuple[dict[str, Any], dict[str, Any], dict[str, Any]]) -> dict[str, Any]:
    return _entry(*arguments)


def analyze(
    directory: Path,
    *,
    submission_sha256: str,
    results_sha256: str,
    contract_path: Path | None = None,
    contract_sha256: str | None = None,
) -> dict[str, Any]:
    """Read immutable run files against caller-held anchors and the frozen source case."""
    if (contract_path is None) != (contract_sha256 is None):
        raise ValueError("a sampling contract requires both its file and external expected digest")
    manifest = case.check()
    retained_case = (directory / "cases.json").read_bytes()
    if retained_case != _manifest_bytes(manifest):
        raise ValueError("the run changes the frozen case bytes")
    artifacts = {
        "cases.json": retained_case,
        "circuit.json": (directory / "circuit.json").read_bytes(),
        "submission.json": _anchor(directory / "submission.json", submission_sha256),
        "job-body.json": (directory / "job-body.json").read_bytes(),
        "results.json": _anchor(directory / "results.json", results_sha256),
        "raw/result.json": (directory / "raw/result.json").read_bytes(),
    }
    raw = _parse_json(artifacts["raw/result.json"], "raw/result.json")
    if isinstance(raw.get("results"), str):
        json.loads(raw["results"], parse_constant=_reject_constant, object_pairs_hook=_unique_object)
    with tempfile.TemporaryDirectory(prefix="ascella-predecessor-snapshot-") as temporary:
        snapshot = Path(temporary) / "run"
        (snapshot / "raw").mkdir(parents=True)
        for filename, data in artifacts.items():
            (snapshot / filename).write_bytes(data)
        qd.run_facts(snapshot)
    submission = _parse_json(artifacts["submission.json"], "submission.json")
    results = _parse_json(artifacts["results.json"], "results.json")
    status = results.get("status", {})
    if not isinstance(status, dict):
        raise ValueError("the collected result requires status metadata")
    duration = status.get("duration")
    if (
        status.get("status") != "completed"
        or isinstance(duration, bool)
        or not isinstance(duration, int | float)
        or not math.isfinite(duration)
        or not 0 <= duration <= case.MAX_DURATION
    ):
        raise ValueError("a complete acquisition within the frozen duration is required")
    validate_sent_body(_parse_json(artifacts["job-body.json"], "job-body.json"), manifest, PROFILE)
    entries = results.get("iterations")
    if not isinstance(entries, list) or len(entries) != len(case.ORDER):
        raise ValueError("the result requires all eight iterations")
    observations = ordered_map(
        _entry_worker,
        [
            (setting, entry, manifest["preregistered"]["compilation_identity"])
            for setting, entry in zip(manifest["settings"], entries, strict=True)
        ],
    )
    description = describe([row["eligible_port_counts"] for row in observations])
    report: dict[str, Any] = {
        "schema": "ascella-predecessor-analysis-v1",
        "job_id": results["job_id"],
        "cases_sha256": hashlib.sha256(artifacts["cases.json"]).hexdigest(),
        "source_sha256": manifest["analysis_sources"],
        "run_bindings": {filename: hashlib.sha256(data).hexdigest() for filename, data in artifacts.items()},
        "anchor_boundary": (
            "caller-held expected hashes bind bytes; the analyzer does not authenticate the caller or provider"
        ),
        "observations": observations,
        **description,
    }
    if contract_path is not None and contract_sha256 is not None:
        validate_contract(contract_path, contract_sha256, manifest, submission["submitted_utc"])
        envelopes = conditional_envelopes(description)
        report.update(envelopes)
        report["verdict"] = _conditional_decision(envelopes)
        report["sampling_contract_sha256"] = contract_sha256
        report["sampling_boundary"] = (
            "coverage assumes the reviewed IID model; evidence hashes establish consistency "
            "rather than physical independence or historical freeze time"
        )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("run", type=Path)
    parser.add_argument("--submission-sha256", required=True)
    parser.add_argument("--results-sha256", required=True)
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--contract-sha256")
    args = parser.parse_args()
    report = analyze(
        args.run,
        submission_sha256=args.submission_sha256,
        results_sha256=args.results_sha256,
        contract_path=args.contract,
        contract_sha256=args.contract_sha256,
    )
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
