"""Frozen Ascella screening preserves attribution, denominators and uncertainty."""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

import ascella_experiment_analysis as analysis
import pytest

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = Path("docs/evidence/ascella-cancellation-transition-acquisition")


def registered_seed() -> int:
    case = json.loads((ROOT / BUNDLE / "cases/sedenion-cancellation-dark/cases.json").read_text())
    return int(case["settings"][0]["compilation_seed"])


def profile() -> dict[str, Any]:
    return {
        "schema": "ascella-experiment-qualification-v1",
        "cohort_id": "ascella-cancellation-transition-screening",
        "familywise_confidence": 0.95,
        "endpoints": 243,
        "precision": 0.01,
        "samples_per_setting": 65536,
        "detected_shot_cap_per_setting": 131072,
        "leakage_includes_invalid": True,
        "thresholds": {
            "compilation_tv": 0.01,
            "dark_herald_upper": 0.02,
            "bright_herald_lower": 0.98,
            "fixture_lower": 0.47,
            "fixture_upper": 0.53,
            "repeat_difference": 0.01,
            "identity_lower": 0.95,
            "cross_basis_tv_upper": 0.05,
            "leakage_upper": 0.02,
        },
    }


def setting(**changes: Any) -> dict[str, Any]:
    return {
        "cohort_id": "ascella-cancellation-transition-screening",
        "setting_id": "mub-six/computational-to-computational-input-0",
        "pilot_role": "identity",
        "iteration_index": 0,
        "sequence_position": 5,
        "compilation_seed": registered_seed(),
        "circuit_params": {"theta": 0.1},
        "requested_probabilities": [1.0] + [0.0] * 11,
        "native_probabilities": [1.0] + [0.0] * 11,
        "active_outputs": list(range(6)),
        "leakage_outputs": list(range(6, 12)),
        "success_outputs": [],
        **changes,
    }


def test_profile_refuses_nonfinite_and_changed_family() -> None:
    analysis.validate_profile(profile())
    for change in ({"endpoints": 242}, {"precision": float("nan")}, {"familywise_confidence": float("inf")}):
        with pytest.raises(ValueError):
            analysis.validate_profile({**profile(), **change})
    corrupted = profile()
    corrupted["thresholds"]["leakage_upper"] = float("nan")
    with pytest.raises(ValueError):
        analysis.validate_profile(corrupted)


def test_iterator_attribution_requires_echoed_seed_parameters_and_budgets() -> None:
    row = setting()
    echoed = {
        "circuit_params": row["circuit_params"],
        "compilation_seed": row["compilation_seed"],
        "max_samples": 65536,
        "max_shots": 131072,
    }
    analysis.attribute_iteration(row, {"iteration": echoed}, profile())
    for key, value in (
        ("compilation_seed", row["compilation_seed"] + 1),
        ("circuit_params", {"theta": 0.2}),
        ("max_samples", 65535),
        ("max_shots", 131071),
    ):
        changed = copy.deepcopy(echoed)
        changed[key] = value
        with pytest.raises(ValueError, match="echoed"):
            analysis.attribute_iteration(row, {"iteration": changed}, profile())
    with pytest.raises(ValueError, match="echoed"):
        analysis.attribute_iteration(row, {}, profile())


def test_qualification_counts_invalid_events_in_leakage_and_preserves_detection_denominator() -> None:
    row = setting()
    counts = {"1,0,0,0,0,0,0,0,0,0,0,0": 64000, "0,0,0,0,0,0,1,0,0,0,0,0": 1000, "1,1,0,0,0,0,0,0,0,0,0,0": 536}
    result = analysis.qualify_setting(row, counts, {"nb_shots_used": 131072}, profile())
    if result["accepted_events"] != 65536 or result["invalid_events"] != 536 or result["leakage_count"] != 1536:
        raise AssertionError(result)
    if result["provider_detected_shots"] != 131072 or result["accepted_vs_detected_fraction"] != 0.5:
        raise AssertionError("detected events and accepted samples need distinct denominators")
    if result["incident_shots"] is not None or result["photon_loss_fraction"] is not None:
        raise AssertionError("detected shots do not count source pulses")
    if result["qualification"] != "fail":
        raise AssertionError("invalid and outside-logical events must participate in leakage qualification")


def test_missing_returned_mesh_keeps_attribution_inconclusive() -> None:
    result = analysis.qualify_setting(setting(), {"1,0,0,0,0,0,0,0,0,0,0,0": 65536}, {}, profile())
    if result["qualification"] != "inconclusive" or result["requested_to_returned_tv"] is not None:
        raise AssertionError("a missing returned operator cannot qualify compilation")


def test_cross_basis_device_criterion_uses_the_returned_mesh_reference(monkeypatch: pytest.MonkeyPatch) -> None:
    row = setting(
        setting_id="mub-six/product_fourier-to-product_chirped-input-0",
        pilot_role="cross-basis",
        requested_probabilities=[1 / 6] * 6 + [0.0] * 6,
    )
    returned = [1.0] + [0.0] * 11
    monkeypatch.setattr(
        analysis,
        "remote_compiled_prediction",
        lambda fields, width: {
            "status": "reconstructed",
            "probabilities": returned,
            "computed_circuit_sha256": "different-returned-mesh",
            "computed_input_sha256": "source-zero",
        },
    )
    result = analysis.qualify_setting(row, {"1,0,0,0,0,0,0,0,0,0,0,0": 65536}, {}, profile())
    if result["criteria"]["cross_basis_tv"]["status"] != "pass":
        raise AssertionError("device conformance must compare observed counts with the returned mesh")
    if result["criteria"]["compilation"]["status"] != "fail" or result["qualification"] != "fail":
        raise AssertionError("the requested-to-returned compilation discrepancy remains a separate failure")
    if result["observed_to_returned_tv_upper"] >= 0.05 or result["observed_to_requested_tv_upper"] <= 0.8:
        raise AssertionError("requested and returned references were conflated")


def test_cross_basis_returned_mesh_criterion_is_inconclusive_when_the_mesh_is_absent() -> None:
    row = setting(
        setting_id="mub-six/product_fourier-to-product_chirped-input-0",
        pilot_role="cross-basis",
        requested_probabilities=[1 / 6] * 6 + [0.0] * 6,
    )
    result = analysis.qualify_setting(row, accepted_counts(row["requested_probabilities"], 65536), {}, profile())
    if result["criteria"]["cross_basis_tv"]["status"] != "inconclusive":
        raise AssertionError("a requested law cannot stand in for an absent returned mesh")
    if result["observed_to_returned_tv_upper"] is not None:
        raise AssertionError("an absent returned mesh cannot supply a device-reference bound")


def save(path: Path, value: Any) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def campaign_copy(root: Path) -> Path:
    destination = root / BUNDLE
    destination.mkdir(parents=True)
    for name in ("campaign.json", "qualification-profile.json"):
        shutil.copyfile(ROOT / BUNDLE / name, destination / name)
    shutil.copytree(ROOT / BUNDLE / "cases", destination / "cases")
    return destination / "campaign.json"


def accepted_counts(probabilities: list[float], samples: int) -> dict[str, int]:
    by_port = [int(probability * samples) for probability in probabilities]
    largest = max(range(12), key=lambda index: probabilities[index])
    by_port[largest] += samples - sum(by_port)
    return {
        ",".join(str(int(index == port)) for index in range(12)): count for port, count in enumerate(by_port) if count
    }


def retain_run(
    root: Path, campaign_path: Path, index: int, *, echo_change: str | None = None, failed: bool = False
) -> Path:
    """Retain a synthetic SDK iterator and matching provider collector-format records."""
    import perceval as pcvl
    import qd_platform
    from perceval.providers.rpc_based_communication_layer import RPCBasedCommunicationLayer

    campaign = json.loads(campaign_path.read_text())
    case_row = campaign["cases"][index]
    original = campaign_path.parent / case_row["manifest"]
    manifest = json.loads(original.read_text())
    circuit_document = json.loads((original.parent / "circuit.json").read_text())
    case = root / case_row["directory"]
    case.mkdir(parents=True)
    shutil.copyfile(original.parent / "circuit.json", case / "circuit.json")
    review = root / "docs/reviewed-screening.md"
    review.parent.mkdir(exist_ok=True, parents=True)
    review.write_text("Reviewed fixture case.\n", encoding="utf-8")
    manifest.update(
        acquisition_admission="ready",
        source_case_sha256=case_row["sha256"],
        reviewed_case={"file": "docs/reviewed-screening.md", "sha256": hashlib.sha256(review.read_bytes()).hexdigest()},
    )
    case_hash = save(case / "cases.json", manifest)
    experiment, _ = qd_platform.template_experiment(manifest, circuit_document)
    command = pcvl.Command(
        "sample_count", [("max_samples", int, False), ("max_shots", int, False), ("compilation_seed", int, False)]
    )
    computation = pcvl.Computation(command, experiment)
    computation.add_params(max_samples=65536, max_shots=131072)
    iterator = pcvl.ComputationIterator(computation)
    entries = []
    for row in manifest["settings"]:
        parameters = {
            "circuit_params": row["circuit_params"],
            "compilation_seed": row["compilation_seed"],
            "max_samples": 65536,
            "max_shots": 131072,
        }
        iterator.add_iteration(**parameters)
        physical = experiment.unitary_circuit()
        for parameter in physical.get_parameters():
            parameter.set_value(parameters["circuit_params"][parameter.name])
        histogram = accepted_counts(row["requested_probabilities"], 65536)
        serialized_counts = (
            ":PCVL:BSCount:{" + ";".join(f"|{state}>={count}" for state, count in histogram.items()) + "}"
        )
        entries.append(
            {
                "iteration": copy.deepcopy(parameters),
                "results": serialized_counts,
                "nb_shots_used": 131072,
                "computed_circuit": pcvl.serialization.serialize(physical),
                "computed_input": ":PCVL:BasicState:|1,0,0,0,0,0,0,0,0,0,0,0>",
            }
        )
    body = {
        "platform_name": "qpu:ascella",
        "max_duration": 300,
        "payload": {
            "command": "sample_count",
            "max_samples": 65536,
            "max_shots": 131072,
            "computation": RPCBasedCommunicationLayer._serialize(iterator),
            "mitigations": RPCBasedCommunicationLayer._serialize([]),
        },
    }
    save(case / "job-body.json", body)
    job_id = f"synthetic-{index}"
    submission = {
        "schema": "qd-submission-v1",
        "cases_sha256": case_hash,
        "job_id": job_id,
        "platform": "qpu:ascella",
        "approval": "synthetic fixture approval",
        "submitted_utc": f"2026-10-27T12:{index:02d}:00+00:00",
        "body_sha256": hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest(),
        "per_job_credits": 1.0,
        "platform_at_plan": {"price_per_shot": 1e-6},
    }
    save(case / "submission.json", submission)
    if echo_change == "seed":
        entries[0]["iteration"]["compilation_seed"] += 1
    elif echo_change == "parameters":
        key = next(iter(entries[0]["iteration"]["circuit_params"]))
        entries[0]["iteration"]["circuit_params"][key] += 0.1
    elif echo_change == "samples":
        entries[0]["iteration"]["max_samples"] -= 1
    elif echo_change == "shots":
        entries[0]["iteration"]["max_shots"] -= 1
    elif echo_change == "reorder":
        entries.reverse()
    status = {
        "status": "error" if failed else "completed",
        "duration": 10,
        "shots": 131072,
        "start_time": 1793102400 + index * 60,
    }
    answer = {"job_id": job_id, "shots": 131072, "results": json.dumps({"results_list": [] if failed else entries})}
    save(case / "raw/result.json", answer)
    raw = (case / "raw/result.json").read_bytes()
    summary = qd_platform.result_summary(raw, job_id, status, complete=not failed, expected=len(entries))
    collected = {
        "schema": "qd-collection-v1",
        "job_id": job_id,
        "status": status,
        "collected_utc": f"2026-10-27T12:{index:02d}:20+00:00",
        "data": {"payload": body["payload"]},
        "result_sha256": hashlib.sha256(raw).hexdigest(),
        **summary,
    }
    save(case / "results.json", collected)
    return case


def test_missing_campaign_keeps_all_243_endpoints_and_all_settings(tmp_path: Path) -> None:
    campaign = campaign_copy(tmp_path)
    report = analysis.analyze_campaign(campaign, [], root=tmp_path)
    if report["complete"] or report["qualification"]["full_expansion_eligible"]:
        raise AssertionError("missing acquisitions qualified expansion")
    if len(report["settings"]) != 17 or report["confidence_family"]["endpoints"] != 243:
        raise AssertionError("the confidence family shrank to the observed subset")


def test_single_collected_diagnostic_preserves_the_frozen_missing_family(tmp_path: Path) -> None:
    campaign = campaign_copy(tmp_path)
    case = retain_run(tmp_path, campaign, 0)
    report = analysis.analyze_campaign(campaign, [case], root=tmp_path)
    collected = [row for row in report["settings"] if row["status"] == "collected"]
    if len(collected) != 1 or not collected[0]["interface_complete"]:
        raise AssertionError("the collected singleton must retain its attributed result interface")
    if collected[0]["herald"]["observed"] != 0 or collected[0]["herald"]["denominator"] != 65536:
        raise AssertionError("the dark diagnostic must retain its zero herald over all accepted events")
    if sum(row["status"] == "missing" for row in report["settings"]) != 16:
        raise AssertionError("the remaining sixteen settings must remain explicitly missing")
    if report["complete"] or report["qualification"]["full_expansion_eligible"]:
        raise AssertionError("a single valid diagnostic cannot complete or expand the campaign")
    if report["confidence_family"]["endpoints"] != 243:
        raise AssertionError("the simultaneous family must include missing settings")


@pytest.mark.audit
def test_complete_iterator_cohort_qualifies_pilot_and_separates_temporal_balance(tmp_path: Path) -> None:
    campaign = campaign_copy(tmp_path)
    runs = [retain_run(tmp_path, campaign, index) for index in range(6)]
    report = analysis.analyze_campaign(campaign, runs, root=tmp_path)
    if not report["complete"] or not report["qualification"]["full_expansion_eligible"]:
        raise AssertionError(report["jobs"] if not report["complete"] else report["qualification"])
    if sum(row["endpoint_count"] for row in report["settings"]) != 243:
        raise AssertionError("aggregate endpoint accounting changed")
    if report["qualification"]["temporal_balance"]["linear_drift_cancellation"] != "unassessed":
        raise AssertionError("a requested iterator order was turned into a shot-timing certificate")
    if any(row["incident_shots"] is not None for row in report["settings"]):
        raise AssertionError("provider detection counts became source-pulse counts")


@pytest.mark.parametrize("change", ["seed", "parameters", "samples", "shots", "reorder"])
def test_raw_echo_mutations_and_reordered_iterator_refuse_attribution(tmp_path: Path, change: str) -> None:
    campaign = campaign_copy(tmp_path)
    case = retain_run(tmp_path, campaign, 5, echo_change=change)
    report = analysis.analyze_campaign(campaign, [case], root=tmp_path)
    job = next(row for row in report["jobs"] if row["directory"] == str(case.relative_to(tmp_path)))
    if job["status"] != "refused" or "echoed" not in job["reason"]:
        raise AssertionError(job)
    if report["qualification"]["full_expansion_eligible"]:
        raise AssertionError("unattributed counts qualified the pilot")


def test_failed_diagnostic_remains_visible_and_cannot_qualify_interface(tmp_path: Path) -> None:
    campaign = campaign_copy(tmp_path)
    case = retain_run(tmp_path, campaign, 0, failed=True)
    report = analysis.analyze_campaign(campaign, [case], root=tmp_path)
    if report["jobs"][0]["status"] != "failed" or report["qualification"]["pilot_start_eligible"]:
        raise AssertionError(report["jobs"][0])
