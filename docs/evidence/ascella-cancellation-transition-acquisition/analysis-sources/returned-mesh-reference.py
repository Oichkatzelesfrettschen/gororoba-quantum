"""Adjudicate the frozen Ascella cancellation diagnostics and twelve-setting transition pilot.

The 243 endpoint family includes absent settings. Provider-detected shots count
detection events; accepted outcome counts supply the categorical denominators.
Qualification remains conditional on the frozen independent-Bernoulli model.
All commands read retained provider artifacts locally and never submit a job.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import sys
from collections import Counter
from datetime import datetime
from functools import cache
from pathlib import Path
from typing import Any

import numpy as np
from experiment_analysis import binomial_interval, decode_photonic_counts, remote_compiled_prediction
from qd_platform import PlatformError, body_mitigations, iteration_form, load_case, run_facts

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from parallel import ordered_map  # noqa: E402

SCHEMA = "ascella-experiment-analysis-v1"
PROFILE_SCHEMA = "ascella-experiment-qualification-v1"
CAMPAIGN_SCHEMA = "ascella-cancellation-transition-campaign-v1"
COHORT = "ascella-cancellation-transition-screening"
THRESHOLDS = {
    "compilation_tv",
    "dark_herald_upper",
    "bright_herald_lower",
    "fixture_lower",
    "fixture_upper",
    "repeat_difference",
    "identity_lower",
    "cross_basis_tv_upper",
    "leakage_upper",
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reject_constant(value: str) -> None:
    raise ValueError(f"nonfinite JSON constant {value} is outside the recorded contract")


def _json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), parse_constant=_reject_constant)


def _finite(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float) or not math.isfinite(value):
        raise ValueError(f"{label} must be a finite number")
    return float(value)


def _integer(value: Any, label: str, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise ValueError(f"{label} must be an integer at least {minimum}")
    return value


def _relative(root: Path, value: Any) -> Path:
    if not isinstance(value, str) or not value or Path(value).is_absolute() or ".." in Path(value).parts:
        raise ValueError("artifact paths must be nonempty relative paths beneath their declared root")
    result = root / value
    if not result.resolve().is_relative_to(root.resolve()):
        raise ValueError("artifact path resolves outside its declared root")
    return result


def validate_profile(profile: dict[str, Any]) -> dict[str, Any]:
    """Validate the complete finite confidence family before reading observations."""
    if profile.get("schema") != PROFILE_SCHEMA or profile.get("cohort_id") != COHORT:
        raise ValueError("the qualification profile belongs to another schema or cohort")
    if type(profile.get("endpoints")) is not int or profile["endpoints"] != 243:
        raise ValueError("the frozen family contains exactly 243 endpoints, including missing settings")
    confidence = _finite(profile.get("familywise_confidence"), "familywise confidence")
    precision = _finite(profile.get("precision"), "precision")
    if not 0 < confidence < 1 or not 0 < precision < 0.5:
        raise ValueError("confidence and precision fall outside their probability ranges")
    if _integer(profile.get("samples_per_setting"), "sample budget", 1) != 65536:
        raise ValueError("the screening sample budget is 65536 accepted events per setting")
    if _integer(profile.get("detected_shot_cap_per_setting"), "detected shot budget", 1) != 131072:
        raise ValueError("the screening detected-shot cap is 131072 per setting")
    if profile.get("leakage_includes_invalid") is not True:
        raise ValueError("the leakage aggregate must include invalid photon-number outcomes")
    thresholds = profile.get("thresholds")
    if not isinstance(thresholds, dict) or set(thresholds) != THRESHOLDS:
        raise ValueError("the qualification profile must register every supported threshold exactly once")
    for name, value in thresholds.items():
        if not 0 <= _finite(value, name) <= 1:
            raise ValueError(f"{name} falls outside [0,1]")
    if thresholds["fixture_lower"] >= thresholds["fixture_upper"]:
        raise ValueError("the fixture acceptance interval must have positive width")
    return profile


def _probabilities(value: Any, label: str) -> list[float]:
    if not isinstance(value, list) or len(value) != 12:
        raise ValueError(f"{label} must cover all twelve physical ports")
    vector = [_finite(item, label) for item in value]
    if any(item < -1e-12 or item > 1 + 1e-12 for item in vector) or abs(math.fsum(vector) - 1) > 1e-9:
        raise ValueError(f"{label} must be a normalized probability vector")
    return vector


def _indices(value: Any, label: str) -> list[int]:
    if not isinstance(value, list) or any(type(index) is not int or not 0 <= index < 12 for index in value):
        raise ValueError(f"{label} must name physical ports")
    if len(set(value)) != len(value):
        raise ValueError(f"{label} repeats a physical port")
    return value


def attribute_iteration(setting: dict[str, Any], entry: dict[str, Any], profile: dict[str, Any]) -> None:
    """Bind returned parameter and budget echoes before associating counts with a setting."""
    expected = {
        "circuit_params": setting["circuit_params"],
        "compilation_seed": setting["compilation_seed"],
        "max_samples": profile["samples_per_setting"],
        "max_shots": profile["detected_shot_cap_per_setting"],
    }
    echoed = entry.get("iteration")
    if not isinstance(echoed, dict) or set(echoed) != set(expected) or echoed != expected:
        raise ValueError(f"{setting['setting_id']}: echoed iteration parameters, seed or budgets differ")
    for name in ("compilation_seed", "max_samples", "max_shots"):
        _integer(echoed[name], f"echoed {name}")
    for name, value in expected["circuit_params"].items():
        if not isinstance(name, str) or not name:
            raise ValueError("parameter names must be nonempty strings")
        _finite(value, "echoed circuit parameter")
        _finite(echoed["circuit_params"][name], "echoed circuit parameter")
    _integer(expected["compilation_seed"], "echoed compilation seed")


def _interval(arguments: tuple[int, int, int, float]) -> list[float]:
    return binomial_interval(*arguments)


def _criterion(value: bool | None, detail: Any) -> dict[str, Any]:
    return {"status": "inconclusive" if value is None else "pass" if value else "fail", "detail": detail}


def qualify_setting(
    setting: dict[str, Any], counts: dict[str, int], fields: dict[str, Any], profile: dict[str, Any]
) -> dict[str, Any]:
    """Qualify a setting with all twelve ports and the invalid-event category retained."""
    validate_profile(profile)
    requested = _probabilities(setting["requested_probabilities"], "requested probabilities")
    active = _indices(setting["active_outputs"], "active outputs")
    leakage_ports = _indices(setting["leakage_outputs"], "leakage outputs")
    if not active or set(active) & set(leakage_ports) or set(active) | set(leakage_ports) != set(range(12)):
        raise ValueError("active and leakage outputs must partition the twelve ports")
    success = _indices(setting.get("success_outputs", []), "herald outputs")
    role = setting.get("pilot_role")
    if role not in {"identity", "cross-basis", "cancellation"}:
        raise ValueError("a setting must register its pilot role")
    if (role == "cancellation") != bool(success):
        raise ValueError("exactly the five cancellation settings carry herald endpoints")
    by_port, invalid_parts = decode_photonic_counts(counts, 12)
    invalid = sum(invalid_parts.values())
    categorical = by_port + [invalid]
    total = sum(categorical)
    if total > profile["samples_per_setting"]:
        raise ValueError("accepted samples exceed the frozen per-setting budget")
    detected = fields.get("nb_shots_used")
    if detected is not None:
        _integer(detected, "provider detected shots")
        if detected > profile["detected_shot_cap_per_setting"] or total > detected:
            raise ValueError("provider detected shots exceed the cap or fall below accepted samples")
    family = profile["endpoints"]
    confidence = profile["familywise_confidence"]
    leakage = invalid + sum(by_port[index] for index in leakage_ports)
    endpoint_counts = categorical + [leakage] + ([sum(by_port[index] for index in success)] if success else [])
    intervals = ordered_map(_interval, [(number, total, family, confidence) for number in endpoint_counts])
    finite_precision = bool(total) and all((upper - lower) / 2 <= profile["precision"] for lower, upper in intervals)

    def tv_upper_bound(probabilities: list[float]) -> float:
        return min(
            1.0,
            math.fsum(
                max(abs(lower - probability), abs(upper - probability))
                for (lower, upper), probability in zip(intervals[:13], probabilities + [0.0], strict=True)
            )
            / 2,
        )

    requested_tv_upper = tv_upper_bound(requested)
    observed = [number / total for number in categorical] if total else None
    remote = remote_compiled_prediction(fields, 12)
    returned_tv_upper = None if remote["status"] != "reconstructed" else tv_upper_bound(remote["probabilities"])
    compilation_tv = (
        None
        if remote["status"] != "reconstructed"
        else math.fsum(abs(first - second) for first, second in zip(requested, remote["probabilities"], strict=True))
        / 2
    )
    thresholds = profile["thresholds"]
    criteria = {
        "precision": _criterion(finite_precision if total else None, {"half_width": profile["precision"]}),
        "leakage": _criterion(intervals[13][1] <= thresholds["leakage_upper"] if total else None, intervals[13]),
        "compilation": _criterion(
            None if compilation_tv is None else compilation_tv <= thresholds["compilation_tv"], compilation_tv
        ),
    }
    herald = None
    if success:
        herald_interval = intervals[14]
        number = endpoint_counts[14]
        herald = {
            "count": number,
            "denominator": total,
            "observed": number / total if total else None,
            "interval": herald_interval,
        }
        name = setting["setting_id"].split("/")[-1]
        if name in {"dark", "dark-repeat"}:
            meets = herald_interval[1] <= thresholds["dark_herald_upper"]
        elif name in {"bright", "bright-repeat"}:
            meets = herald_interval[0] >= thresholds["bright_herald_lower"]
        elif name == "fixture":
            meets = (
                herald_interval[0] >= thresholds["fixture_lower"] and herald_interval[1] <= thresholds["fixture_upper"]
            )
        else:
            raise ValueError("a cancellation setting names an unregistered arm")
        criteria["herald"] = _criterion(meets if total else None, herald_interval)
    elif role == "identity":
        target_port = int(np.argmax(requested))
        if abs(requested[target_port] - 1) > 1e-9:
            raise ValueError("an identity control must target one physical port with probability one")
        criteria["identity"] = _criterion(
            intervals[target_port][0] >= thresholds["identity_lower"] if total else None, intervals[target_port]
        )
    else:
        criteria["cross_basis_tv"] = _criterion(
            returned_tv_upper <= thresholds["cross_basis_tv_upper"]
            if total and returned_tv_upper is not None
            else None,
            returned_tv_upper,
        )
        criteria["cross_basis_tv"]["reference"] = "returned computed_circuit and computed_input"
    status = (
        "fail"
        if any(item["status"] == "fail" for item in criteria.values())
        else "inconclusive"
        if any(item["status"] == "inconclusive" for item in criteria.values())
        else "pass"
    )
    return {
        "setting_id": setting["setting_id"],
        "cohort_id": setting["cohort_id"],
        "pilot_role": role,
        "iteration_index": setting["iteration_index"],
        "sequence_position": setting["sequence_position"],
        "physical_port_counts": by_port,
        "invalid_events": invalid,
        "invalid_components": invalid_parts,
        "accepted_events": total,
        "category_counts": categorical,
        "category_intervals": intervals[:13],
        "leakage_count": leakage,
        "leakage_interval": intervals[13],
        "endpoint_count": len(endpoint_counts),
        "observed_category_probabilities": observed,
        "requested_probabilities": requested,
        "provider_detected_shots": detected,
        "accepted_vs_detected_fraction": total / detected if detected else None,
        "incident_shots": None,
        "photon_loss_fraction": None,
        "remote_compiled_prediction": remote,
        "requested_to_returned_tv": compilation_tv,
        "observed_to_requested_tv_upper": requested_tv_upper,
        "observed_to_returned_tv_upper": returned_tv_upper,
        "herald": herald,
        "precision_met": finite_precision,
        "criteria": criteria,
        "qualification": status,
        "denominator_boundary": (
            "all accepted returned events; provider shots count detected events and leave incident pulses unknown"
        ),
        "confidence_boundary": (
            "the frozen simultaneous coverage is conditional on IID Bernoulli trials within settings"
        ),
    }


@cache
def _computation(text: str) -> Any:
    from perceval.serialization import deserialize

    return deserialize(json.loads(text)["payload"]["computation"])


def _body_entry(arguments: tuple[str, int, dict[str, Any], dict[str, Any]]) -> None:
    text, index, setting, profile = arguments
    computation = _computation(text)
    entry = computation.iterations[index]
    attribute_iteration(setting, {"iteration": entry}, profile)
    experiment = computation.experiment
    if experiment.m != 12 or list(experiment.input_state) != [1] + [0] * 11 or experiment.min_photons_filter != 1:
        raise ValueError("the sent experiment changes its twelve-port input or photon filter")
    circuit = experiment.unitary_circuit()
    parameters = circuit.get_parameters()
    if sorted(parameter.name for parameter in parameters) != sorted(entry["circuit_params"]):
        raise ValueError("the sent iterator parameters differ from its serialized circuit")
    for parameter in parameters:
        parameter.set_value(entry["circuit_params"][parameter.name])
    actual = np.asarray(circuit.compute_unitary(), dtype=np.complex128)
    expected = setting["operator"]
    requested = np.asarray(expected["real"], dtype=float) + 1j * np.asarray(expected["imaginary"], dtype=float)
    if (
        requested.shape != (12, 12)
        or not np.isfinite(requested).all()
        or not np.allclose(actual, requested, atol=1e-9, rtol=0)
    ):
        raise ValueError("the sent computation differs from its complete frozen operator")


def validate_sent_body(body: dict[str, Any], manifest: dict[str, Any], profile: dict[str, Any]) -> None:
    """Validate a retained iterator, including single-entry diagnostic jobs."""
    import perceval as pcvl

    payload = body.get("payload", {})
    if body.get("platform_name") != "qpu:ascella" or payload.get("command") != "sample_count":
        raise ValueError("the sent body changes the platform or command")
    if body_mitigations(body) != manifest.get("mitigations"):
        raise ValueError("the sent body changes the registered mitigation policy")
    if body.get("max_duration") != manifest["max_duration"] or body.get("max_duration") != 300:
        raise ValueError("the sent body changes the frozen execution ceiling")
    for key, expected in (
        ("max_samples", profile["samples_per_setting"]),
        ("max_shots", profile["detected_shot_cap_per_setting"]),
    ):
        if type(payload.get(key)) is not int or payload[key] != expected:
            raise ValueError("the sent payload changes a per-setting budget")
    computation = _computation(json.dumps(body, allow_nan=False))
    if not isinstance(computation, pcvl.ComputationIterator) or len(computation.iterations) != len(
        manifest["settings"]
    ):
        raise ValueError("the sent computation must retain the full frozen iterator")
    if computation.base_computation.command.name != "sample_count":
        raise ValueError("the serialized computation changes the sample-count command")
    ordered_map(
        _body_entry,
        [
            (json.dumps(body, allow_nan=False), index, setting, profile)
            for index, setting in enumerate(manifest["settings"])
        ],
    )


def _bound(root: Path, binding: dict[str, Any]) -> tuple[Path, Any]:
    path = _relative(root, binding.get("file"))
    if not isinstance(binding.get("sha256"), str) or _sha(path) != binding["sha256"]:
        raise ValueError("a bound artifact differs from its recorded sha256")
    return path, _json(path)


def _manifest_for_run(actual: dict[str, Any], frozen: dict[str, Any], root: Path) -> None:
    """Allow only the documented reviewed-case transition from the frozen source case."""
    if actual == frozen:
        return
    expected = dict(frozen)
    reviewed = actual.get("reviewed_case")
    if not isinstance(reviewed, dict):
        raise ValueError("the run manifest differs from its frozen source case")
    reviewed_path = _relative(root, reviewed.get("file"))
    if _sha(reviewed_path) != reviewed.get("sha256"):
        raise ValueError("the reviewed written case differs from its bound digest")
    expected.update(
        acquisition_admission="ready", reviewed_case=reviewed, source_case_sha256=actual.get("source_case_sha256")
    )
    if "prerequisites" in actual:
        prerequisites = actual["prerequisites"]
        if not isinstance(prerequisites, dict):
            raise ValueError("the prerequisite receipt requires a file and digest binding")
        _bound(root, prerequisites)
        expected["prerequisites"] = prerequisites
    if actual != expected:
        raise ValueError("the run manifest changes fields outside the reviewed admission transition")


def _time(value: Any) -> float | None:
    if isinstance(value, int | float) and not isinstance(value, bool):
        return float(value) if math.isfinite(value) else None
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
        return parsed.timestamp() if parsed.tzinfo is not None else None
    return None


def cohort_summary(rows: list[dict[str, Any]], profile: dict[str, Any]) -> dict[str, Any]:
    """Keep optical scientific outcomes separate from execution-interface admission."""
    by_id = {row["setting_id"]: row for row in rows}
    cancellation = [row for row in rows if row.get("pilot_role") == "cancellation"]
    pilot = [row for row in rows if row.get("pilot_role") in {"identity", "cross-basis"}]
    cancellations_complete = len(cancellation) == 5 and all(row.get("interface_complete") for row in cancellation)
    pilot_complete = len(pilot) == 12 and all(row.get("interface_complete") for row in pilot)
    repeat_results = []
    for name in ("dark", "bright"):
        base = by_id.get(f"sedenion-lcu/{name}", {})
        repeat = by_id.get(f"sedenion-lcu/{name}-repeat", {})
        first_herald = base.get("herald")
        repeated_herald = repeat.get("herald")
        interval = None
        identity = False
        if isinstance(first_herald, dict) and isinstance(repeated_herald, dict):
            interval = [
                repeated_herald["interval"][0] - first_herald["interval"][1],
                repeated_herald["interval"][1] - first_herald["interval"][0],
            ]
            meshes = [row.get("remote_compiled_prediction", {}) for row in (base, repeat)]
            identity = all(mesh.get("status") == "reconstructed" for mesh in meshes) and all(
                meshes[0].get(key) == meshes[1].get(key) for key in ("computed_circuit_sha256", "computed_input_sha256")
            )
        repeat_results.append(
            {
                "arm": name,
                "difference_interval": interval,
                "returned_identity_matches": identity,
                "status": "inconclusive"
                if interval is None
                else "pass"
                if identity
                and interval[0] >= -profile["thresholds"]["repeat_difference"]
                and interval[1] <= profile["thresholds"]["repeat_difference"]
                else "fail",
            }
        )
    ordered = sorted(cancellation, key=lambda row: row["sequence_position"])
    arms = [by_id.get(f"sedenion-lcu/{name}", {}) for name in ("dark", "bright", "bright-repeat", "dark-repeat")]
    contrast = None
    if all(row.get("herald", {}).get("observed") is not None for row in arms):
        contrast = (
            math.fsum(weight * row["herald"]["observed"] for weight, row in zip((1, -1, -1, 1), arms, strict=True)) / 2
        )
    envelopes = [
        (_time(row.get("execution_envelope", {}).get("lower")), _time(row.get("execution_envelope", {}).get("upper")))
        for row in ordered
    ]
    order_proven = (
        len(ordered) == 5
        and all(lower is not None and upper is not None and lower <= upper for lower, upper in envelopes)
        and all(
            first[1] is not None and second[0] is not None and first[1] <= second[0]
            for first, second in zip(envelopes, envelopes[1:], strict=False)
        )
    )

    def qualification(items: list[dict[str, Any]], count: int) -> str:
        if any(row.get("qualification") == "fail" for row in items):
            return "fail"
        return (
            "pass"
            if len(items) == count
            and all(row.get("qualification") == "pass" and row.get("interface_complete") for row in items)
            else "inconclusive"
        )

    cancellation_status = qualification(cancellation, 5)
    if any(result["status"] == "fail" for result in repeat_results):
        cancellation_status = "fail"
    elif any(result["status"] != "pass" for result in repeat_results) and cancellation_status == "pass":
        cancellation_status = "inconclusive"
    pilot_status = qualification(pilot, 12)
    return {
        "cancellation_interface_complete": cancellations_complete,
        "cancellation_scientific_qualification": cancellation_status,
        "pilot_interface_complete": pilot_complete,
        "pilot_qualification": pilot_status,
        "pilot_start_eligible": cancellations_complete,
        "full_expansion_eligible": pilot_status == "pass",
        "repeat_checks": repeat_results,
        "contrast_estimable": contrast is not None,
        "descriptive_dark_minus_bright": contrast,
        "temporal_balance": {
            "executed_order_established": order_proven,
            "linear_drift_cancellation": "unassessed",
            "boundary": "execution order does not establish equal shot timing or cancellation of linear drift",
        },
        "expansion_boundary": (
            "only the twelve-setting pilot qualifies expansion; cancellation performance "
            "is a separate scientific outcome"
        ),
    }


def analyze_campaign(campaign_path: Path, directories: list[Path], *, root: Path = ROOT) -> dict[str, Any]:
    """Analyze the frozen seventeen-setting family, preserving absent and failed acquisitions."""
    campaign = _json(campaign_path)
    if campaign.get("schema") != CAMPAIGN_SCHEMA or campaign.get("cohort_id") != COHORT:
        raise ValueError("the campaign belongs to another schema or cohort")
    profile_path, profile = _bound(root, campaign["qualification_profile"])
    validate_profile(profile)
    frozen_settings = campaign.get("settings")
    if not isinstance(frozen_settings, list) or len(frozen_settings) != 17:
        raise ValueError("the campaign must freeze all seventeen settings")
    identities = [row.get("setting_id") for row in frozen_settings]
    positions = [row.get("sequence_position") for row in frozen_settings]
    if Counter(row.get("pilot_role") for row in frozen_settings) != {
        "cancellation": 5,
        "identity": 6,
        "cross-basis": 6,
    }:
        raise ValueError("the family must retain five cancellation, six identity and six cross-basis settings")
    if len(set(identities)) != 17 or sorted(positions) != list(range(17)):
        raise ValueError("the campaign setting identities or sequence positions repeat or omit an entry")
    expected = {row["setting_id"]: row for row in frozen_settings}
    case_rows = campaign.get("cases")
    if not isinstance(case_rows, list) or len(case_rows) != 6:
        raise ValueError("the campaign must freeze five diagnostic jobs and one twelve-setting pilot")
    if len({row["directory"] for row in case_rows}) != 6:
        raise ValueError("the campaign repeats an acquisition directory")
    flattened = [setting_id for row in case_rows for setting_id in row["settings"]]
    if Counter(flattened) != Counter(identities):
        raise ValueError("the campaign case inventory differs from the frozen setting family")
    supplied = [path.resolve() for path in directories]
    if len(set(supplied)) != len(supplied):
        raise ValueError("the supplied acquisition directories repeat a job")
    case_paths = {_relative(root, row["directory"]).resolve(): row for row in case_rows}
    if set(supplied) - set(case_paths):
        raise ValueError("a supplied acquisition directory falls outside the frozen campaign")
    results: dict[str, dict[str, Any]] = {
        setting_id: {
            **expected[setting_id],
            "cohort_id": COHORT,
            "qualification": "inconclusive",
            "interface_complete": False,
            "status": "missing",
        }
        for setting_id in identities
    }
    jobs = []
    for path, case_row in case_paths.items():
        frozen_path = _relative(campaign_path.parent, case_row["manifest"])
        if _sha(frozen_path) != case_row["sha256"]:
            raise ValueError("a frozen source case differs from the campaign digest")
        frozen = _json(frozen_path)
        if frozen.get("qualification_profile") != campaign["qualification_profile"]:
            raise ValueError("a source case uses another qualification profile")
        setting_ids = [row.get("setting_id") for row in frozen["settings"]]
        if (
            setting_ids != case_row["settings"]
            or frozen.get("cohort_id") != COHORT
            or iteration_form(frozen) != "template"
        ):
            raise ValueError("a source case changes its setting inventory, cohort or iterator contract")
        for index, row in enumerate(frozen["settings"]):
            specification = expected[row["setting_id"]]
            if (
                row.get("iteration_index") != index
                or any(
                    row.get(key) != specification[key] for key in ("pilot_role", "sequence_position", "iteration_index")
                )
                or specification["case"] != case_row["directory"]
            ):
                raise ValueError("a source setting changes its frozen attribution metadata")
        if path not in supplied or not (path / "results.json").is_file():
            jobs.append(
                {"directory": case_row["directory"], "status": "uncollected" if path in supplied else "missing"}
            )
            continue
        try:
            actual, circuit, _ = load_case(path)
            _manifest_for_run(actual, frozen, root)
            if actual != frozen and actual.get("source_case_sha256") != case_row["sha256"]:
                raise ValueError("the reviewed run names another source case")
            run_facts(path)
            body = _json(path / "job-body.json")
            validate_sent_body(body, actual, profile)
            collected = _json(path / "results.json")
            duration = _finite(collected.get("status", {}).get("duration"), "provider job duration")
            if not 0 <= duration <= actual["max_duration"]:
                raise ValueError("the provider duration exceeds the frozen runtime cap")
            if collected.get("status", {}).get("status") != "completed":
                jobs.append(
                    {
                        "directory": case_row["directory"],
                        "status": "failed",
                        "duration_seconds": duration,
                        "provider_status": collected.get("status"),
                    }
                )
                continue
            entries = collected.get("iterations")
            if not isinstance(entries, list) or len(entries) != len(actual["settings"]):
                raise ValueError("the collection omits the complete returned iterator inventory")
            qualified = []
            for row, entry in zip(actual["settings"], entries, strict=True):
                attribute_iteration(row, entry, profile)
                statistics = qualify_setting(row, entry.get("counts", {}), entry.get("result_fields", {}), profile)
                statistics.update(
                    status="collected",
                    interface_complete=bool(
                        statistics["accepted_events"] == profile["samples_per_setting"]
                        and statistics["remote_compiled_prediction"]["status"] == "reconstructed"
                    ),
                )
                statistics["execution_envelope"] = {
                    "lower": collected["status"].get("start_time"),
                    "upper": collected.get("collected_utc"),
                }
                statistics["iterator_temporal_order"] = (
                    "unassessed within a packed job" if len(entries) > 1 else "single entry within a separate job"
                )
                qualified.append(statistics)
            for statistics in qualified:
                results[statistics["setting_id"]] = statistics
            jobs.append(
                {
                    "directory": case_row["directory"],
                    "status": "collected",
                    "duration_seconds": duration,
                    "sources": [
                        {"ref": f"{case_row['directory']}/{name}", "sha256": _sha(path / name)}
                        for name in (
                            "cases.json",
                            "submission.json",
                            "job-body.json",
                            "results.json",
                            "raw/result.json",
                        )
                    ],
                }
            )
        except (KeyError, TypeError, ValueError, OSError, PlatformError) as error:
            jobs.append({"directory": case_row["directory"], "status": "refused", "reason": str(error)})
    rows = sorted(results.values(), key=lambda row: row["sequence_position"])
    return {
        "schema": SCHEMA,
        "cohort_id": COHORT,
        "campaign_sha256": _sha(campaign_path),
        "qualification_profile_sha256": _sha(profile_path),
        "analysis_source_sha256": _sha(Path(__file__)),
        "analysis_environment": {
            "python": sys.version.split()[0],
            **{name: importlib.metadata.version(name) for name in ("numpy", "scipy", "perceval-quandela")},
        },
        "analysis_dependencies": [
            {"ref": f"scripts/{name}", "sha256": _sha(Path(__file__).parent / name)}
            for name in ("experiment_analysis.py", "qd_platform.py", "qd_belenos_mesh.py")
        ],
        "confidence_family": {
            "endpoints": 243,
            "familywise_confidence": profile["familywise_confidence"],
            "includes_missing_settings": True,
        },
        "complete": all(row["interface_complete"] for row in rows),
        "jobs": jobs,
        "settings": rows,
        "qualification": cohort_summary(rows, profile),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", type=Path, required=True)
    parser.add_argument("runs", nargs="*", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = analyze_campaign(args.campaign, args.runs)
    text = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.check:
        if args.out.read_text(encoding="utf-8") != text:
            raise SystemExit("the retained screening analysis differs from recomputation")
    else:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
