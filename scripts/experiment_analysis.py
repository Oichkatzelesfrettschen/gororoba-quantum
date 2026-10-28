"""Replay experiment counts against mathematical and compiled predictions.

The analyzer reads existing provider receipts and raw files locally. Intervals
describe an explicitly conditional independent-Bernoulli model; ordered qubit
shots and batch contrasts remain visible so drift cannot disappear in pooling.
Use --campaign to check the complete generated inventory rather than only the
supplied runs. Neither analysis nor precision sizing contacts a provider.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import beta

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from parallel import ordered_map  # noqa: E402

SCHEMA = "quantum-experiment-analysis-v1"
DEFAULT_ENDPOINTS = 54 * 12


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _count(value: Any, name: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{name} must be a nonnegative integer")
    return value


def _design(endpoints: int, precision: float, confidence: float) -> None:
    if type(endpoints) is not int or endpoints < 1:
        raise ValueError("endpoints must be a positive integer")
    if not math.isfinite(precision) or not 0 < precision < 0.5:
        raise ValueError("precision must lie strictly between zero and one half")
    if not math.isfinite(confidence) or not 0 < confidence < 1:
        raise ValueError("confidence must lie strictly between zero and one")


def binomial_interval(
    successes: int, trials: int, endpoints: int = DEFAULT_ENDPOINTS, confidence: float = 0.95
) -> list[float]:
    """Bonferroni simultaneous Clopper-Pearson intervals, conditional on IID trials."""
    _count(trials, "trials")
    _count(successes, "successes")
    _design(endpoints, 0.05, confidence)
    if successes > trials:
        raise ValueError("successes exceed trials")
    if trials == 0:
        return [0.0, 1.0]
    tail = (1 - confidence) / (2 * endpoints)
    lower = 0.0 if successes == 0 else float(beta.ppf(tail, successes, trials - successes + 1))
    upper = 1.0 if successes == trials else float(beta.ppf(1 - tail, successes + 1, trials - successes))
    return [lower, upper]


def required_shots(endpoints: int = DEFAULT_ENDPOINTS, precision: float = 0.05, confidence: float = 0.95) -> int:
    """Size bounded Bernoulli mean error using exact binomial tail probabilities.

    The central Clopper-Pearson interval has the maximum width for a fixed
    trial count. Its half-width is a precision target for an interval, rather
    than a guarantee that every estimate lies within precision of the truth.
    Bonferroni controls the declared finite family without requiring endpoints
    to be independent of one another. Trials within each endpoint remain IID.
    """
    _design(endpoints, precision, confidence)

    def meets(trials: int) -> bool:
        lower, upper = binomial_interval(trials // 2, trials, endpoints, confidence)
        return (upper - lower) / 2 <= precision

    upper = 1
    while not meets(upper):
        upper *= 2
        if upper > 2**40:
            raise ValueError("precision design exceeds the supported shot budget")
    lower = 0
    while upper - lower > 1:
        middle = (lower + upper) // 2
        if meets(middle):
            upper = middle
        else:
            lower = middle
    return upper


def split_shots(shots: int, cap: int) -> list[int]:
    """Split a declared trial budget into positive, cap-bounded jobs."""
    _count(shots, "shots")
    if type(cap) is not int or cap < 1:
        raise ValueError("shot cap must be a positive integer")
    complete, remainder = divmod(shots, cap)
    return [cap] * complete + ([remainder] if remainder else [])


def _probabilities(value: Any, label: str) -> list[float]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label} must be a nonempty probability vector")
    if any(isinstance(item, bool) or not isinstance(item, int | float) for item in value):
        raise ValueError(f"{label} contains a nonnumeric probability")
    result = [float(item) for item in value]
    if any(not math.isfinite(item) or item < -1e-12 or item > 1 + 1e-12 for item in result):
        raise ValueError(f"{label} contains a probability outside [0,1]")
    if abs(math.fsum(result) - 1) > 1e-9:
        raise ValueError(f"{label} probabilities must sum to one")
    return result


def _indices(value: Any, width: int, label: str) -> list[int]:
    if not isinstance(value, list) or any(type(item) is not int or not 0 <= item < width for item in value):
        raise ValueError(f"{label} contains an invalid outcome index")
    if len(set(value)) != len(value):
        raise ValueError(f"{label} repeats an outcome index")
    return value


def _reference(row: dict[str, Any]) -> tuple[list[float], list[float], list[int], list[int]]:
    ideal = _probabilities(row.get("requested_probabilities"), "requested")
    compiled = _probabilities(row.get("native_probabilities"), "compiled")
    if len(ideal) != len(compiled):
        raise ValueError("ideal and compiled probability widths differ")
    width = len(ideal)
    active = _indices(row.get("active_outputs"), width, "active_outputs")
    leakage = _indices(row.get("leakage_outputs"), width, "leakage_outputs")
    if not active or set(active) & set(leakage) or set(active) | set(leakage) != set(range(width)):
        raise ValueError("active and leakage outputs must form a complete disjoint partition")
    labels = row.get("logical_output_labels")
    if labels is not None and (not isinstance(labels, list) or len(labels) != width or len(set(labels)) != width):
        raise ValueError("logical output labels must be unique and cover every outcome")
    return ideal, compiled, active, leakage


def decode_qubit_shots(
    row: dict[str, Any], shots: list[str], declared_width: int, *, physical_width: int | None = None
) -> tuple[list[int], list[int]]:
    """Decode explicit terminal register mappings with qubit zero at the right."""
    ideal, _, _, _ = _reference(row)
    logical_qubits = (len(ideal) - 1).bit_length()
    if len(ideal) != 2**logical_qubits:
        raise ValueError("qubit prediction width must be a power of two")
    mapping = row.get("measurement_mapping")
    if not isinstance(mapping, list) or len(mapping) != logical_qubits:
        raise ValueError("measurement mapping must name every logical bit")
    physical_width = declared_width if physical_width is None else physical_width
    if type(physical_width) is not int or physical_width < 1 or type(declared_width) is not int or declared_width < 1:
        raise ValueError("register and physical widths must be positive integers")
    if len(set(mapping)) != logical_qubits or any(
        type(bit) is not int or not 0 <= bit < physical_width for bit in mapping
    ):
        raise ValueError("measurement mapping is not an injective in-register map")
    kind = row.get("register_kind")
    if kind not in {"classical", "qubit"}:
        raise ValueError("register_kind must explicitly name classical or qubit")
    positions = list(range(logical_qubits)) if kind == "classical" else mapping
    if max(positions) >= declared_width:
        raise ValueError("measurement destinations exceed the returned register width")
    counts = [0] * len(ideal)
    outcomes = []
    for shot in shots:
        if not isinstance(shot, str) or len(shot) != declared_width or set(shot) - {"0", "1"}:
            raise ValueError("a raw shot differs from the declared binary register width")
        value = sum((shot[-1 - position] == "1") << logical for logical, position in enumerate(positions))
        counts[value] += 1
        outcomes.append(value)
    return counts, outcomes


def decode_photonic_counts(counts: dict[str, int], width: int) -> tuple[list[int], dict[str, int]]:
    """Keep one-click physical modes, zero-click and other photon-number outcomes."""
    if type(width) is not int or width < 1:
        raise ValueError("photonic width must be positive")
    by_mode = [0] * width
    categories = {"zero_click": 0, "other_photon_number": 0}
    for state, count in counts.items():
        _count(count, "Fock-state count")
        values = state.split(",")
        if len(values) != width or any(not value.isdecimal() for value in values):
            raise ValueError("a Fock state differs from the declared physical mode width")
        occupation = [int(value) for value in values]
        photons = sum(occupation)
        if photons == 1:
            by_mode[occupation.index(1)] += count
        elif photons == 0:
            categories["zero_click"] += count
        else:
            categories["other_photon_number"] += count
    return by_mode, categories


def analyze_counts(
    row: dict[str, Any],
    counts: list[int],
    *,
    other_events: dict[str, int] | None = None,
    incident_shots: int | None = None,
    endpoints: int = DEFAULT_ENDPOINTS,
    precision: float = 0.05,
    confidence: float = 0.95,
    ordered_outcomes: list[int] | None = None,
) -> dict[str, Any]:
    """Report all three prediction layers without correcting observed histograms."""
    _design(endpoints, precision, confidence)
    ideal, compiled, active, leakage = _reference(row)
    if len(counts) != len(ideal):
        raise ValueError("observed and predicted histogram widths differ")
    for count in counts:
        _count(count, "outcome count")
    other = {} if other_events is None else dict(other_events)
    for count in other.values():
        _count(count, "other-event count")
    total = sum(counts) + sum(other.values())
    if incident_shots is not None:
        _count(incident_shots, "incident shots")
        if total > incident_shots:
            raise ValueError("returned events exceed incident shots")
    observed = [count / total for count in counts] if total else None
    model_intervals = ordered_map(_interval_job, [(count, total, endpoints, confidence) for count in counts])
    active_count = sum(counts[index] for index in active)
    reference_active = math.fsum(compiled[index] for index in active)
    conditional = [counts[index] / active_count for index in active] if active_count else None
    conditional_compiled = [compiled[index] / reference_active for index in active] if reference_active > 0 else None
    result: dict[str, Any] = {
        "name": row.get("name", row.get("file")),
        "family": row.get("family"),
        "role": row.get("role", row.get("kind")),
        "counts": counts,
        "other_events": other,
        "returned_event_denominator": total,
        "incident_shots": incident_shots,
        "unreturned_events": None if incident_shots is None else incident_shots - total,
        "unreturned_fraction": (incident_shots - total) / incident_shots if incident_shots else None,
        "denominator_boundary": (
            "observed proportions condition on returned events; incident-shot loss requires its own denominator"
        ),
        "requested_probabilities": ideal,
        "compiled_probabilities": compiled,
        "compiled_prediction_scope": row.get("prediction_scope", "recorded native gate operator"),
        "observed_probabilities": observed,
        "compiled_minus_requested": [native - target for native, target in zip(compiled, ideal, strict=True)],
        "observed_minus_compiled": None
        if observed is None
        else [value - target for value, target in zip(observed, compiled, strict=True)],
        "observed_minus_requested": None
        if observed is None
        else [value - target for value, target in zip(observed, ideal, strict=True)],
        "active_outputs": active,
        "leakage_outputs": leakage,
        "leakage_count": sum(counts[index] for index in leakage),
        "logical_event_denominator": active_count,
        "conditional_logical_probabilities": conditional,
        "conditional_compiled_probabilities": conditional_compiled,
        "iid_model_intervals": model_intervals,
        "iid_model_familywise_confidence": confidence,
        "iid_model_endpoints": endpoints,
        "iid_model_precision_met": bool(
            total and all((upper - lower) / 2 <= precision for lower, upper in model_intervals)
        ),
        "sampling_boundary": (
            "Clopper-Pearson coverage is conditional on independent identically distributed Bernoulli trials; "
            "aggregation does not establish that premise"
        ),
        "verdict": "descriptive" if total else "inconclusive-empty",
    }
    for field in ("acquisition_order", "contrast_weight", "repeat_of"):
        if field in row:
            result[field] = row[field]
    if row.get("success_outputs"):
        success = _indices(row["success_outputs"], len(counts), "success_outputs")
        number = sum(counts[index] for index in success)
        success_interval = binomial_interval(number, total, endpoints, confidence)
        result["success"] = {
            "count": number,
            "denominator": total,
            "denominator_scope": "all returned events, including events outside the logical subspace",
            "observed": number / total if total else None,
            "requested": math.fsum(ideal[index] for index in success),
            "compiled": math.fsum(compiled[index] for index in success),
            "iid_model_interval": success_interval,
        }
        result["iid_model_precision_met"] = (
            result["iid_model_precision_met"] and (success_interval[1] - success_interval[0]) / 2 <= precision
        )
    if ordered_outcomes is not None:
        if len(ordered_outcomes) != total or Counter(ordered_outcomes) != Counter(
            {index: value for index, value in enumerate(counts) if value}
        ):
            raise ValueError("ordered outcomes disagree with the histogram")
        halves = [ordered_outcomes[: total // 2], ordered_outcomes[total // 2 :]]
        half_probabilities = [
            [part.count(index) / len(part) for index in range(len(counts))] if part else None for part in halves
        ]
        result["ordered_shot_diagnostic"] = {
            "first_half": half_probabilities[0],
            "second_half": half_probabilities[1],
            "maximum_half_difference": max(
                abs(first - second) for first, second in zip(*half_probabilities, strict=True)
            )
            if all(part is not None for part in half_probabilities)
            else None,
            "boundary": "a descriptive temporal check; a small difference does not prove independence",
        }
    return result


def _source(path: Path, root: Path) -> dict[str, str]:
    return {"ref": path.relative_to(root).as_posix(), "sha256": digest(path)}


def _interval_job(arguments: tuple[int, int, int, float]) -> list[float]:
    return binomial_interval(*arguments)


def readout_admission(controls: dict[str, Any], minimum: Any, logical_qubits: int) -> dict[str, Any]:
    """Apply the frozen empirical contrast gate without claiming calibration confidence."""
    reasons = []
    prepared: dict[int, dict[str, Any]] = {}
    for control in controls.values():
        if control.get("prepared") not in (0, 1):
            continue
        value = control["prepared"]
        if value in prepared:
            raise ValueError("readout references repeat a prepared state")
        prepared[value] = control
    valid_minimum = (
        isinstance(minimum, int | float)
        and not isinstance(minimum, bool)
        and math.isfinite(minimum)
        and 0 <= minimum <= 1
    )
    if not valid_minimum:
        reasons.append("minimum readout contrast remains unregistered")
    if set(prepared) != {0, 1}:
        reasons.append("both prepared-state readout references are required")
    contrasts = []
    if set(prepared) == {0, 1}:
        for logical in range(logical_qubits):
            probabilities = [prepared[value]["probability_one"][logical] for value in (0, 1)]
            contrast = (
                probabilities[1] - probabilities[0] if all(value is not None for value in probabilities) else None
            )
            contrasts.append(
                {
                    "logical_bit": logical,
                    "p1_given_0": probabilities[0],
                    "p1_given_1": probabilities[1],
                    "contrast": contrast,
                }
            )
            if contrast is None:
                reasons.append(f"logical bit {logical} has empty readout observations")
            elif valid_minimum and contrast < minimum:
                reasons.append(f"logical bit {logical} readout contrast is below its registered minimum")
    return {
        "status": "inconclusive" if reasons else "empirical-controls-met",
        "minimum_contrast": minimum,
        "per_logical_bit": contrasts,
        "reasons": reasons,
        "boundary": (
            "the gate compares observed proportions; it supplies neither an interval for true calibration "
            "nor an IID certificate"
        ),
    }


def remote_compiled_prediction(fields: dict[str, Any], width: int) -> dict[str, Any]:
    """Reconstruct a returned optical operator using the repository's safe circuit parser."""
    from qd_belenos_mesh import coupler, decode, unzip

    text = fields.get("computed_circuit")
    source = fields.get("computed_input")
    if text is None and source is None:
        return {"status": "unavailable", "reason": "the retained result supplies neither compiled circuit nor input"}
    if not isinstance(text, str) or not isinstance(source, str):
        return {"status": "unavailable", "reason": "both computed_circuit and computed_input are required"}
    match = re.fullmatch(r":PCVL:BasicState:\|([01](?:,[01])*)>", source)
    if match is None:
        raise ValueError("returned computed_input must be an explicit one-photon basic state")
    occupation = [int(value) for value in match[1].split(",")]
    if len(occupation) != width or sum(occupation) != 1:
        raise ValueError("returned computed_input differs from the physical one-photon width")
    matrix = np.eye(width, dtype=np.complex128)
    for kind, mode, parameter in decode(text):
        if type(mode) is not int or not 0 <= mode < width:
            raise ValueError("returned compiled circuit addresses an output outside the declared width")
        if kind == "ps":
            if not isinstance(parameter, float) or not math.isfinite(parameter):
                raise ValueError("returned compiled phase must be finite and numerical")
            matrix[mode] *= np.exp(1j * parameter)
        elif kind == "bs":
            if mode + 1 >= width or any(
                not isinstance(angle, float) or not math.isfinite(angle) for angle in parameter
            ):
                raise ValueError("returned compiled coupler exceeds the width or has nonnumerical angles")
            matrix[mode : mode + 2] = coupler(*parameter) @ matrix[mode : mode + 2]
        else:
            raise ValueError("returned compiled circuit has an unsupported optical component")
    if not np.isfinite(matrix).all() or not np.allclose(matrix.conj().T @ matrix, np.eye(width), atol=1e-9, rtol=0):
        raise ValueError("returned compiled operator fails complete unitarity reconstruction")
    probabilities = [float(value) for value in np.abs(matrix[:, occupation.index(1)]) ** 2]
    _probabilities(probabilities, "remote compiled")
    return {
        "status": "reconstructed",
        "probabilities": probabilities,
        "computed_circuit_sha256": hashlib.sha256(unzip(text).encode()).hexdigest(),
        "computed_input_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "input_mode": occupation.index(1),
        "boundary": "the reconstructed returned operator predicts ideal one-photon counts; the device may differ",
    }


def analyze_qi(case: Path, endpoints: int, precision: float, confidence: float) -> dict[str, Any]:
    """Read the guarded QI collector format, including explicit raw shot order."""
    from qi_platform import _check_submission_manifest

    manifest = json.loads((case / "cases.json").read_text(encoding="utf-8"))
    submission = json.loads((case / "submission.json").read_text(encoding="utf-8"))
    _check_submission_manifest(case, submission, require_enqueued=True)
    if submission.get("schema") != "qi-submission-v2" or not submission.get("cases_sha256"):
        raise ValueError("new experiments require a digest-bound v2 submission")
    collected = json.loads((case / "results.json").read_text(encoding="utf-8"))
    if collected.get("schema") != "qi-collection-v1":
        raise ValueError("unexpected QI collection schema")
    jobs = collected.get("jobs")
    if not isinstance(jobs, list) or len({row["file"] for row in jobs}) != len(jobs):
        raise ValueError("collection jobs must have unique circuit filenames")
    by_file = {row["file"]: row for row in jobs}
    expected = {row["file"]: row for row in submission["jobs"]}
    if set(by_file) != set(expected):
        raise ValueError("collection and submission circuit inventories differ")
    sources = [_source(case / name, case) for name in ("cases.json", "submission.json", "results.json")]
    results = []
    missing = []
    readout: dict[str, Any] = {}
    for row in manifest["circuits"]:
        item = by_file[row["file"]]
        job = item["job"]
        if job.get("id") != expected[row["file"]]["job"] or job.get("batch_job_id") != submission["batch_job"]:
            raise ValueError("collection job identity differs from submission")
        if job.get("status") != "completed":
            missing.append({"file": row["file"], "status": job.get("status")})
            continue
        metadata = item.get("results")
        if not isinstance(metadata, list) or len(metadata) != 1:
            raise ValueError("a completed QI job requires one result")
        result = metadata[0]
        if result.get("job_id") != job["id"] or result.get("shots_requested") != manifest["shots"]:
            raise ValueError("QI result identity or requested shots differ")
        raw = case / "raw" / f"{row['file']}.json"
        shots = json.loads(raw.read_text(encoding="utf-8"))
        if not isinstance(shots, list) or len(shots) != result.get("shots_done") or len(shots) > manifest["shots"]:
            raise ValueError("QI raw shot count differs from collector metadata")
        if "results" in result and Counter(shots) != Counter(result["results"]):
            raise ValueError("QI raw histogram differs from collector metadata")
        sources.extend([_source(case / row["file"], case), _source(raw, case)])
        if len(shots) != manifest["shots"]:
            missing.append(
                {
                    "file": row["file"],
                    "status": "short-shot-count",
                    "expected": manifest["shots"],
                    "received": len(shots),
                }
            )
        if row.get("kind") != "science":
            logical_qubits = row.get("logical_qubits", manifest.get("logical_qubits"))
            if (
                type(logical_qubits) is not int
                or logical_qubits < 1
                or type(row.get("prepared")) is not int
                or row["prepared"] not in (0, 1)
            ):
                raise ValueError("readout controls require explicit logical width and prepared bit")
            width = 2**logical_qubits
            law = [float(index == row["prepared"] * (width - 1)) for index in range(width)]
            control_row = {
                **row,
                "requested_probabilities": law,
                "native_probabilities": law,
                "active_outputs": list(range(width)),
                "leakage_outputs": [],
            }
            control_counts, _ = decode_qubit_shots(
                control_row, shots, row["register_width"], physical_width=manifest["nqubits"]
            )
            readout[row["file"]] = {
                "prepared": row["prepared"],
                "shots": len(shots),
                "counts": dict(sorted(Counter(shots).items())),
                "probability_one": [
                    sum(count for outcome, count in enumerate(control_counts) if (outcome >> logical) & 1) / len(shots)
                    if shots
                    else None
                    for logical in range(logical_qubits)
                ],
            }
            continue
        register_width = row.get("register_width")
        if type(register_width) is not int:
            raise ValueError("the experiment row must declare its returned register width")
        counts, outcomes = decode_qubit_shots(row, shots, register_width, physical_width=manifest["nqubits"])
        statistics = analyze_counts(
            row,
            counts,
            incident_shots=len(shots),
            endpoints=endpoints,
            precision=precision,
            confidence=confidence,
            ordered_outcomes=outcomes,
        )
        statistics["execution_envelope"] = {
            "lower": job.get("started_at", job.get("queued_at")),
            "upper": job.get("finished_at"),
            "boundary": "queue entry bounds execution from below; finished_at bounds execution from above",
        }
        statistics["compiled_source_sha256"] = row["sha256"]
        results.append(statistics)
    admission = readout_admission(
        readout, manifest.get("preregistered", {}).get("minimum_output_readout_contrast"), manifest["logical_qubits"]
    )
    reasons = list(admission["reasons"])
    if missing:
        reasons.append("the batch has failed or short acquisitions")
    if not results or any(not result["iid_model_precision_met"] for result in results):
        reasons.append("science counts miss the conditional precision target")
    return {
        "provider": "qi",
        "backend": manifest["backend"],
        "family": manifest.get("family"),
        "settings": results,
        "readout_controls": readout,
        "readout_admission": admission,
        "acquisition_admission": "inconclusive" if reasons else "empirical-controls-met",
        "admission_reasons": reasons,
        "incomplete": missing,
        "sources": sources,
        "batch": case.name,
        "collected_utc": collected.get("collected_utc"),
    }


def analyze_qd(case: Path, endpoints: int, precision: float, confidence: float) -> dict[str, Any]:
    """Validate existing QD raw receipts before decoding terminal one-photon counts."""
    from qd_platform import load_case, run_facts

    run_facts(case)
    manifest, circuit, _ = load_case(case)
    collected = json.loads((case / "results.json").read_text(encoding="utf-8"))
    submission = json.loads((case / "submission.json").read_text(encoding="utf-8"))
    rows = manifest["settings"]
    entries = collected.get("iterations")
    if entries is None:
        if len(rows) != 1:
            raise ValueError("a static optical result cannot represent multiple settings")
        entries = [collected]
    if len(entries) != len(rows):
        raise ValueError("optical result iteration count differs from the setting inventory")
    results = []
    missing = []
    for row, entry in zip(rows, entries, strict=True):
        if "counts" not in entry or not entry["counts"]:
            missing.append({"name": row["name"], "status": "missing-counts"})
            continue
        counts, other = decode_photonic_counts(entry["counts"], circuit["modes"])
        if len(counts) != len(row["requested_probabilities"]):
            raise ValueError("optical predictions must retain every physical output mode")
        # Quandela bills a shot when at least one photon is detected. The
        # accepted samples can be a subset of those events; source pulses and
        # undetected photons need an independently documented counter.
        detected = entry.get("result_fields", {}).get("nb_shots_used")
        if detected is not None:
            _count(detected, "provider detected shots")
            if sum(counts) + sum(other.values()) > detected:
                raise ValueError("accepted optical events exceed provider detected shots")
        remote = remote_compiled_prediction(entry.get("result_fields", {}), circuit["modes"])
        analyzed_row = dict(row)
        if remote["status"] == "reconstructed":
            analyzed_row["native_probabilities"] = remote["probabilities"]
            analyzed_row["prediction_scope"] = "reconstructed returned computed_circuit and computed_input"
        statistics = analyze_counts(
            analyzed_row,
            counts,
            other_events=other,
            incident_shots=None,
            endpoints=endpoints,
            precision=precision,
            confidence=confidence,
        )
        statistics["remote_compiled_prediction"] = remote
        accepted = statistics["returned_event_denominator"]
        statistics["provider_detected_shots"] = detected
        statistics["accepted_vs_detected_fraction"] = accepted / detected if detected else None
        statistics["detected_but_unaccepted_events"] = None if detected is None else detected - accepted
        statistics["denominator_boundary"] = (
            "nb_shots_used counts provider detection events; accepted samples can be a subset. "
            "Incident source pulses and undetected-photon loss remain unknown."
        )
        statistics["execution_envelope"] = {
            "lower": collected.get("status", {}).get("start_time"),
            "upper": collected.get("collected_utc"),
            "boundary": (
                "provider start_time bounds execution from below; terminal collection time bounds it from above"
            ),
        }
        statistics["template_probabilities"] = row["native_probabilities"]
        observed = statistics["observed_probabilities"]
        statistics["observed_minus_template"] = (
            None
            if observed is None
            else [value - template for value, template in zip(observed, row["native_probabilities"], strict=True)]
        )
        if remote["status"] != "reconstructed":
            for key in (
                "compiled_probabilities",
                "compiled_minus_requested",
                "observed_minus_compiled",
                "conditional_compiled_probabilities",
            ):
                statistics[key] = None
            statistics["compiled_prediction_scope"] = "provider compiled operator remains unavailable"
            if "success" in statistics:
                statistics["success"]["template"] = statistics["success"]["compiled"]
                statistics["success"]["compiled"] = None
        results.append(statistics)
    if collected.get("status", {}).get("status") != "completed":
        missing.append({"status": collected.get("status", {}).get("status")})
    names = ["cases.json", manifest["circuit"]["file"], "submission.json", "job-body.json", "results.json"]
    if (case / "raw/result.json").exists():
        names.append("raw/result.json")
    return {
        "provider": "qd",
        "backend": submission["platform"],
        "family": manifest.get("family"),
        "settings": results,
        "readout_controls": {},
        "acquisition_admission": "inconclusive"
        if missing or any(not result["iid_model_precision_met"] for result in results)
        else "unassessed-optical-qualification",
        "admission_reasons": ["the optical instrument qualification has no separately registered pass criterion"],
        "incomplete": missing,
        "sources": [_source(case / name, case) for name in names],
        "batch": case.name,
        "collected_utc": collected.get("collected_utc"),
    }


def _timestamp(value: Any) -> float | None:
    if isinstance(value, int | float) and not isinstance(value, bool):
        return float(value) if math.isfinite(value) else None
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
        return parsed.timestamp() if parsed.tzinfo is not None else None
    return None


def balanced_contrasts(batches: list[dict[str, Any]]) -> dict[str, Any]:
    """Admit a requested +,-,-,+ contrast only through executed order and repeated identity."""
    groups: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]] = defaultdict(list)
    for batch in batches:
        for setting in batch["settings"]:
            if setting.get("family") == "sedenion-lcu" and setting.get("contrast_weight"):
                groups[batch["backend"]].append((batch, setting))
    results = {}
    for backend, entries in groups.items():
        entries.sort(key=lambda item: item[1].get("acquisition_order", -1))
        reasons = []
        settings = [setting for _, setting in entries]
        if [setting.get("acquisition_order") for setting in settings] != [0, 1, 2, 3] or [
            setting.get("contrast_weight") for setting in settings
        ] != [1, -1, -1, 1]:
            reasons.append("the complete registered +,-,-,+ arm sequence is required")
        envelopes = [
            (
                _timestamp(setting.get("execution_envelope", {}).get("lower")),
                _timestamp(setting.get("execution_envelope", {}).get("upper")),
            )
            for setting in settings
        ]
        if any(lower is None or upper is None or lower > upper for lower, upper in envelopes):
            reasons.append("provider execution envelopes are absent or invalid")
        elif any(
            first[1] is not None and second[0] is not None and first[1] > second[0]
            for first, second in zip(envelopes, envelopes[1:], strict=False)
        ):
            reasons.append("execution envelopes do not establish the requested arm order")
        identities = []
        for batch, setting in entries:
            if batch["provider"] == "qi":
                identity = setting.get("compiled_source_sha256")
            else:
                remote = setting.get("remote_compiled_prediction", {})
                identity = (
                    (remote.get("computed_circuit_sha256"), remote.get("computed_input_sha256"))
                    if remote.get("status") == "reconstructed"
                    else None
                )
            identities.append(identity)
            if "success" not in setting or setting["success"]["observed"] is None:
                reasons.append("an arm lacks its all-returned-events herald estimate")
            if batch.get("acquisition_admission") != "empirical-controls-met":
                reasons.append("an arm lacks completed device-control and precision admission")
        if len(identities) == 4 and (
            any(identity is None for identity in identities)
            or identities[0] != identities[3]
            or identities[1] != identities[2]
        ):
            reasons.append("repeated arms lack identical recorded compiled operators and inputs")
        descriptive_estimate = None
        if (
            len(settings) == 4
            and all(setting.get("success", {}).get("observed") is not None for setting in settings)
            and [setting.get("contrast_weight") for setting in settings] == [1, -1, -1, 1]
        ):
            descriptive_estimate = (
                math.fsum(setting["contrast_weight"] * setting["success"]["observed"] for setting in settings) / 2
            )
        results[backend] = {
            "status": "inconclusive" if reasons else "descriptive-contrast-admitted",
            "arms": [setting["name"] for setting in settings],
            "weights": [setting["contrast_weight"] for setting in settings],
            "dark_minus_bright": descriptive_estimate if not reasons else None,
            "descriptive_dark_minus_bright": descriptive_estimate,
            "reasons": sorted(set(reasons)),
            "boundary": (
                "executed order and repeated identity admit a descriptive contrast; unequal timing and device drift "
                "remain explicit limitations"
            ),
        }
    return results


def _analyze_case(arguments: tuple[Path, int, float, float]) -> dict[str, Any]:
    path, endpoints, precision, confidence = arguments
    manifest = json.loads((path / "cases.json").read_text(encoding="utf-8"))
    if manifest.get("schema") == "qi-hypercomplex-cases-v1":
        return analyze_qi(path, endpoints, precision, confidence)
    if manifest.get("schema") == "qd-hypercomplex-cases-v1":
        return analyze_qd(path, endpoints, precision, confidence)
    raise ValueError("unsupported experiment manifest schema")


def analyze_runs(
    directories: list[Path],
    *,
    campaign: Path | None = None,
    endpoints: int = DEFAULT_ENDPOINTS,
    precision: float = 0.05,
    confidence: float = 0.95,
) -> dict[str, Any]:
    """Analyze runs separately and check an optional complete campaign inventory."""
    _design(endpoints, precision, confidence)
    resolved = [path.resolve() for path in directories]
    if len(set(resolved)) != len(resolved):
        raise ValueError("the run directory list repeats an acquisition")
    sources = []
    missing = []
    if campaign is not None:
        index = json.loads(campaign.read_text(encoding="utf-8"))
        if index.get("schema") != "quantum-experiment-campaign-v1":
            raise ValueError("unexpected experiment campaign schema")
        paths = [row["path"] for row in index["cases"]]
        if any(not isinstance(path, str) or Path(path).is_absolute() or ".." in Path(path).parts for path in paths):
            raise ValueError("campaign case paths must remain beneath its directory")
        if len(set(paths)) != len(paths):
            raise ValueError("campaign repeats a case path")
        expected = {(campaign.parent / path).resolve(): path for path in paths}
        for entry in index["cases"]:
            case_manifest = campaign.parent / entry["path"] / "cases.json"
            if not isinstance(entry.get("sha256"), str) or (
                case_manifest.exists() and digest(case_manifest) != entry["sha256"]
            ):
                raise ValueError("campaign case manifest differs from its frozen sha256")
        if set(resolved) - set(expected):
            raise ValueError("a supplied run falls outside the campaign inventory")
        missing = [expected[path] for path in expected if path not in resolved]
        sources = [_source(campaign, campaign.parent)]
    results = ordered_map(_analyze_case, [(path, endpoints, precision, confidence) for path in resolved], min_items=1)
    for path, result in zip(resolved, results, strict=True):
        result["case"] = path.relative_to(campaign.parent.resolve()).as_posix() if campaign else path.name
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    interval_families: dict[str, int] = defaultdict(int)
    for batch in results:
        for setting in batch["settings"]:
            family = f"{batch['backend']}:{setting['family']}"
            interval_families[family] += len(setting["counts"]) + int("success" in setting)
            key = f"{batch['backend']}:{setting['family']}:{setting['name']}"
            groups[key].append(
                {
                    "case": batch["case"],
                    "counts": setting["counts"],
                    "denominator": setting["returned_event_denominator"],
                    "observed_probabilities": setting["observed_probabilities"],
                }
            )
    if any(size > endpoints for size in interval_families.values()):
        raise ValueError("observed endpoint inventory exceeds the declared per-backend per-family interval correction")
    return {
        "schema": SCHEMA,
        "analysis_source_sha256": digest(Path(__file__)),
        "analysis_environment": {
            "python": sys.version.split()[0],
            "numpy": importlib.metadata.version("numpy"),
            "scipy": importlib.metadata.version("scipy"),
        },
        "analysis_dependencies": [
            _source(ROOT / name, ROOT)
            for name in (
                "scripts/qi_platform.py",
                "scripts/qd_platform.py",
                "scripts/qd_belenos_mesh.py",
                "gororoba_quantum/parallel.py",
                "docs/runbooks/quandela-credit-optimization.md",
            )
        ],
        "scope": "campaign-inventory" if campaign else "supplied-cases-only",
        "campaign_sources": sources,
        "missing_cases": missing,
        "complete": bool(results) and not missing and all(not result["incomplete"] for result in results),
        "precision_design": {
            "endpoints": endpoints,
            "family_definition": "one provider backend and scientific family; repeated observations count separately",
            "observed_endpoint_counts": dict(sorted(interval_families.items())),
            "absolute_half_width": precision,
            "familywise_confidence": confidence,
            "iid_shots_per_setting": required_shots(endpoints, precision, confidence),
        },
        "batches": results,
        "balanced_contrasts": balanced_contrasts(results),
        "repeated_setting_batches": dict(sorted(groups.items())),
        "pooling_boundary": (
            "batch histograms remain separate; IID model intervals do not establish temporal independence "
            "or device superiority"
        ),
    }


def self_test() -> None:
    row = {
        "name": "fixture",
        "requested_probabilities": [0.5, 0.5, 0.0, 0.0],
        "native_probabilities": [0.6, 0.4, 0.0, 0.0],
        "active_outputs": [0, 1],
        "leakage_outputs": [2, 3],
        "success_outputs": [0],
    }
    result = analyze_counts(row, [6, 2, 2, 0], endpoints=4)
    if result["leakage_count"] != 2 or result["logical_event_denominator"] != 8 or result["success"]["observed"] != 0.6:
        raise RuntimeError("histogram denominators or success decoding changed")
    if abs(result["compiled_minus_requested"][0] - 0.1) > 1e-12 or result["observed_minus_compiled"][0] != 0:
        raise RuntimeError("mathematical, compiled and observed layers were conflated")
    if sum(split_shots(required_shots(4), 2048)) != required_shots(4):
        raise RuntimeError("shot splitting lost trials")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--analyze", nargs="+", type=Path)
    modes.add_argument("--size", action="store_true")
    modes.add_argument("--self-test", action="store_true")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--campaign", type=Path)
    parser.add_argument("--endpoints", type=int, default=DEFAULT_ENDPOINTS)
    parser.add_argument("--precision", type=float, default=0.05)
    parser.add_argument("--confidence", type=float, default=0.95)
    parser.add_argument("--shot-cap", type=int, default=2048)
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.size:
        shots = required_shots(args.endpoints, args.precision, args.confidence)
        value = {
            "shots_per_setting": shots,
            "jobs": split_shots(shots, args.shot_cap),
            "model": "simultaneous Clopper-Pearson conditional on IID Bernoulli trials",
        }
    else:
        value = analyze_runs(
            args.analyze,
            campaign=args.campaign,
            endpoints=args.endpoints,
            precision=args.precision,
            confidence=args.confidence,
        )
    text = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.check:
        if args.out is None or args.out.read_text(encoding="utf-8") != text:
            raise SystemExit("analysis differs from the retained output")
    elif args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
