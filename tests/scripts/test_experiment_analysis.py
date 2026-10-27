"""Experiment analysis preserves physical mappings, denominators and three prediction layers."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

import experiment_analysis as analysis
import pytest


def reference(**changes: Any) -> dict[str, Any]:
    return {
        "name": "transition",
        "family": "mub6",
        "kind": "science",
        "requested_probabilities": [0.5, 0.5, 0.0, 0.0],
        "native_probabilities": [0.6, 0.4, 0.0, 0.0],
        "active_outputs": [0, 1],
        "leakage_outputs": [2, 3],
        "logical_output_labels": ["0", "1", "leak2", "leak3"],
        "success_outputs": [0],
        "measurement_mapping": [0, 1],
        "register_kind": "classical",
        "register_width": 2,
        **changes,
    }


def save(path: Path, value: Any) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def qi_run(path: Path, *, short: bool = False, failed: bool = False) -> None:
    path.mkdir(parents=True)
    source = "version 3.0\nqubit[2] q\nbit[2] b\nb[0] = measure q[0]\nb[1] = measure q[1]\n"
    (path / "science.cq").write_text(source, encoding="utf-8")
    source_hash = hashlib.sha256(source.encode()).hexdigest()
    manifest = {
        "schema": "qi-hypercomplex-cases-v1",
        "backend": "tuna_17",
        "backend_type_id": 7,
        "shots": 4,
        "nqubits": 2,
        "logical_qubits": 2,
        "family": "mub6",
        "circuits": [reference(file="science.cq", sha256=source_hash)],
    }
    cases_hash = save(path / "cases.json", manifest)
    submission = {
        "schema": "qi-submission-v2",
        "cases_sha256": cases_hash,
        "backend": "tuna_17",
        "backend_type_id": 7,
        "shots": 4,
        "state": "enqueued",
        "batch_job": 20,
        "jobs": [{"file": "science.cq", "job": 40, "sha256": source_hash}],
    }
    save(path / "submission.json", submission)
    shots = ["00", "01", "10"] if short else ["00", "00", "01", "10"]
    if not failed:
        save(path / "raw/science.cq.json", shots)
    job = {
        "file": "science.cq",
        "job": {"id": 40, "batch_job_id": 20, "status": "error" if failed else "completed"},
        "results": [] if failed else [{"job_id": 40, "shots_requested": 4, "shots_done": len(shots), "results": shots}],
    }
    save(path / "results.json", {"schema": "qi-collection-v1", "jobs": [job], "transactions": []})


def add_readout_controls(case: Path, zero: list[str], one: list[str]) -> None:
    manifest = json.loads((case / "cases.json").read_text())
    submission = json.loads((case / "submission.json").read_text())
    collection = json.loads((case / "results.json").read_text())
    manifest["preregistered"] = {"minimum_output_readout_contrast": 0.2}
    for prepared, shots in enumerate((zero, one)):
        filename = f"readout-{prepared}.cq"
        (case / filename).write_text(f"// prepared {prepared}\n", encoding="utf-8")
        source_hash = analysis.digest(case / filename)
        manifest["circuits"].append(
            {
                "file": filename,
                "kind": "readout-reference",
                "prepared": prepared,
                "logical_qubits": 2,
                "register_width": 2,
                "register_kind": "classical",
                "measurement_mapping": [0, 1],
                "sha256": source_hash,
            }
        )
        job_id = 41 + prepared
        submission["jobs"].append({"file": filename, "job": job_id, "sha256": source_hash})
        collection["jobs"].append(
            {
                "file": filename,
                "job": {"id": job_id, "batch_job_id": 20, "status": "completed"},
                "results": [{"job_id": job_id, "shots_requested": 4, "shots_done": len(shots), "results": shots}],
            }
        )
        save(case / "raw" / f"{filename}.json", shots)
    submission["cases_sha256"] = save(case / "cases.json", manifest)
    save(case / "submission.json", submission)
    save(case / "results.json", collection)


def qd_run(path: Path, *, detected: int | None = None) -> None:
    """Build real collector-format bytes that qd_platform.run_facts verifies."""
    import qd_platform

    path.mkdir(parents=True)
    circuit = {"schema": "qd-template-circuit-v1", "modes": 4, "input_state": [1, 0, 0, 0], "ops": [], "parameters": 0}
    circuit_hash = save(path / "circuit.json", circuit)
    manifest = {
        "schema": "qd-hypercomplex-cases-v1",
        "family": "mub6",
        "job": "fixture",
        "platforms": ["qpu:ascella"],
        "gate_form": "template",
        "command": "sample_count",
        "iterations": 1,
        "settings": [reference()],
        "max_samples": 10,
        "max_shots": 20,
        "circuit": {"file": "circuit.json", "sha256": circuit_hash},
    }
    cases_hash = save(path / "cases.json", manifest)
    body = {"payload": {"test": "retained-payload"}}
    save(path / "job-body.json", body)
    submission = {
        "schema": "qd-submission-v1",
        "cases_sha256": cases_hash,
        "job_id": "fixture-job",
        "platform": "qpu:ascella",
        "approval": "fixture approval",
        "submitted_utc": "2026-10-27T12:00:00+00:00",
        "body_sha256": hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest(),
        "per_job_credits": 1.0,
        "platform_at_plan": {"price_per_shot": 1e-6},
    }
    save(path / "submission.json", submission)
    fields = {} if detected is None else {"nb_shots_used": detected}
    answer = {
        "job_id": "fixture-job",
        "shots": 20,
        "results": json.dumps({"results": ":PCVL:BSCount:{|1,0,0,0>=6;|0,1,0,0>=2;|0,0,1,0>=2}", **fields}),
    }
    save(path / "raw/result.json", answer)
    raw = (path / "raw/result.json").read_bytes()
    status = {"status": "completed", "shots": 20}
    collected = {
        "schema": "qd-collection-v1",
        "job_id": "fixture-job",
        "status": status,
        "collected_utc": "2026-10-27T12:01:00+00:00",
        "data": {"payload": body["payload"]},
        "result_sha256": hashlib.sha256(raw).hexdigest(),
        **qd_platform.result_summary(raw, "fixture-job", status, expected=None),
    }
    save(path / "results.json", collected)


def test_prediction_layers_and_leakage_denominators() -> None:
    result = analysis.analyze_counts(reference(), [6, 2, 2, 0], endpoints=4)
    if result["observed_minus_compiled"] != [0.0, -0.2, 0.2, 0.0]:
        raise AssertionError(result)
    if result["leakage_count"] != 2 or result["conditional_logical_probabilities"] != [0.75, 0.25]:
        raise AssertionError("conditional logical probabilities discarded leakage")
    if result["incident_shots"] is not None or result["unreturned_fraction"] is not None:
        raise AssertionError("absent incident trials cannot acquire a loss estimate")
    if result["success"]["denominator"] != 10 or result["success"]["observed"] != 0.6:
        raise AssertionError("heralding must use the unconditional returned-event denominator")
    if result["verdict"] != "descriptive" or "independent" not in result["sampling_boundary"]:
        raise AssertionError("count intervals silently certified a sampling assumption")


def test_register_maps_distinguish_tuna_bits_and_qx_qubits() -> None:
    row = reference(measurement_mapping=[11, 13], register_kind="classical")
    counts, ordered = analysis.decode_qubit_shots(row, ["01", "10"], 2, physical_width=17)
    if counts != [0, 1, 1, 0] or ordered != [1, 2]:
        raise AssertionError("Tuna destinations must decode the explicit classical bits")
    row.update(register_kind="qubit", measurement_mapping=[3, 1])
    counts, _ = analysis.decode_qubit_shots(row, ["1000", "0010"], 4)
    if counts != [0, 1, 1, 0]:
        raise AssertionError("QX measurement-register positions must follow physical qubits")
    row["measurement_mapping"] = [1, 1]
    with pytest.raises(ValueError, match="injective"):
        analysis.decode_qubit_shots(row, ["1000"], 4)
    row["measurement_mapping"] = [3, 1]
    with pytest.raises(ValueError, match="binary register width"):
        analysis.decode_qubit_shots(row, ["10000"], 4)


def test_photonic_events_keep_physical_leakage_and_other_clicks() -> None:
    counts, other = analysis.decode_photonic_counts({"1,0,0,0": 4, "0,0,0,1": 2, "0,0,0,0": 3, "1,1,0,0": 1}, 4)
    result = analysis.analyze_counts(reference(), counts, other_events=other, incident_shots=12)
    if result["returned_event_denominator"] != 10 or result["leakage_count"] != 2 or result["unreturned_events"] != 2:
        raise AssertionError(result)
    if result["other_events"] != {"zero_click": 3, "other_photon_number": 1}:
        raise AssertionError("other detector outcomes were discarded")
    with pytest.raises(ValueError, match="exceed incident"):
        analysis.analyze_counts(reference(), counts, other_events=other, incident_shots=9)


@pytest.mark.parametrize(
    "field,value",
    [
        ("active_outputs", [0, 0]),
        ("leakage_outputs", [1, 2, 3]),
        ("native_probabilities", [0.5, float("nan"), 0, 0]),
        ("requested_probabilities", [0.1] * 4),
    ],
)
def test_invalid_reference_contracts_fail(field: str, value: Any) -> None:
    with pytest.raises(ValueError):
        analysis.analyze_counts(reference(**{field: value}), [1, 1, 0, 0])


def test_precision_sizing_is_minimal_under_the_declared_model() -> None:
    shots = analysis.required_shots(endpoints=432)
    if shots != 1499:
        raise AssertionError(shots)
    interval = analysis.binomial_interval(shots // 2, shots, endpoints=432)
    previous = analysis.binomial_interval((shots - 1) // 2, shots - 1, endpoints=432)
    if (interval[1] - interval[0]) / 2 > 0.05 or (previous[1] - previous[0]) / 2 <= 0.05:
        raise AssertionError("precision sizing did not find the minimum admitted trial count")
    if analysis.split_shots(4097, 2048) != [2048, 2048, 1]:
        raise AssertionError("provider cap splitting lost a remainder")
    if analysis.binomial_interval(0, 0) != [0.0, 1.0]:
        raise AssertionError("an empty observation must retain full uncertainty")


def test_empty_and_temporally_changed_data_remain_explicit() -> None:
    result = analysis.analyze_counts(reference(), [0, 0, 0, 0])
    if result["verdict"] != "inconclusive-empty" or result["iid_model_precision_met"]:
        raise AssertionError("empty data passed precision")
    result = analysis.analyze_counts(reference(), [2, 2, 0, 0], ordered_outcomes=[0, 0, 1, 1])
    if result["ordered_shot_diagnostic"]["maximum_half_difference"] != 1:
        raise AssertionError("temporal drift disappeared into pooled counts")
    with pytest.raises(ValueError, match="ordered outcomes"):
        analysis.analyze_counts(reference(), [2, 2, 0, 0], ordered_outcomes=[0, 0, 0, 1])


def test_qi_adapter_binds_actual_raw_bytes_and_collection(tmp_path: Path) -> None:
    case = tmp_path / "run"
    qi_run(case)
    result = analysis.analyze_runs([case])
    if not result["complete"] or result["batches"][0]["settings"][0]["counts"] != [2, 1, 1, 0]:
        raise AssertionError(result)
    raw = case / "raw/science.cq.json"
    if not any(row["sha256"] == analysis.digest(raw) for row in result["batches"][0]["sources"]):
        raise AssertionError("raw provenance digest is absent")
    save(raw, ["00", "00", "00", "00"])
    with pytest.raises(ValueError, match="histogram differs"):
        analysis.analyze_runs([case])


def test_missing_jobs_and_short_counts_cannot_finish_campaign(tmp_path: Path) -> None:
    short = tmp_path / "short"
    failed = tmp_path / "failed"
    qi_run(short, short=True)
    qi_run(failed, failed=True)
    campaign = tmp_path / "campaign.json"
    save(
        campaign,
        {
            "schema": "quantum-experiment-campaign-v1",
            "cases": [
                {
                    "path": name,
                    "sha256": analysis.digest(tmp_path / name / "cases.json") if name != "missing" else "missing",
                }
                for name in ("short", "failed", "missing")
            ],
        },
    )
    result = analysis.analyze_runs([short, failed], campaign=campaign)
    if result["complete"] or result["missing_cases"] != ["missing"]:
        raise AssertionError(result)
    if not all(batch["incomplete"] for batch in result["batches"]):
        raise AssertionError("short and failed acquisitions need explicit incomplete states")


def test_qd_detection_counter_does_not_become_an_incident_photon_denominator(tmp_path: Path) -> None:
    case = tmp_path / "optical"
    qd_run(case, detected=20)
    result = analysis.analyze_runs([case])
    row = result["batches"][0]["settings"][0]
    if row["counts"] != [6, 2, 2, 0] or row["provider_detected_shots"] != 20:
        raise AssertionError(row)
    if row["accepted_vs_detected_fraction"] != 0.5 or row["detected_but_unaccepted_events"] != 10:
        raise AssertionError("twenty detected events and ten accepted samples must report one-half acceptance")
    if any(row[key] is not None for key in ("incident_shots", "unreturned_events", "unreturned_fraction")):
        raise AssertionError("the provider detection counter cannot establish undetected-photon loss")
    collection = json.loads((case / "results.json").read_text())
    collection["result_sha256"] = "corrupted"
    save(case / "results.json", collection)
    import qd_platform

    with pytest.raises(qd_platform.PlatformError, match="recorded sha256"):
        analysis.analyze_runs([case])


def test_qd_top_level_shot_cap_does_not_establish_incident_trials(tmp_path: Path) -> None:
    case = tmp_path / "optical"
    qd_run(case)
    row = analysis.analyze_runs([case])["batches"][0]["settings"][0]
    if row["incident_shots"] is not None or row["unreturned_events"] is not None:
        raise AssertionError("a top-level per-iteration cap was converted into a photon-loss denominator")


def test_manifest_mutation_and_duplicate_runs_are_rejected(tmp_path: Path) -> None:
    case = tmp_path / "run"
    qi_run(case)
    with pytest.raises(ValueError, match="repeats an acquisition"):
        analysis.analyze_runs([case, case])
    manifest = json.loads((case / "cases.json").read_text())
    mutated = copy.deepcopy(manifest)
    mutated["circuits"][0]["native_probabilities"] = [0.5, 0.5, 0, 0]
    save(case / "cases.json", mutated)
    import qi_platform

    with pytest.raises(qi_platform.PlatformError, match="submission receipt digest"):
        analysis.analyze_runs([case])


def test_interval_inventory_includes_success_endpoints(tmp_path: Path) -> None:
    case = tmp_path / "run"
    qi_run(case)
    with pytest.raises(ValueError, match="endpoint inventory exceeds"):
        analysis.analyze_runs([case], endpoints=4)
    result = analysis.analyze_runs([case], endpoints=5)
    if result["precision_design"]["observed_endpoint_counts"] != {"tuna_17:mub6": 5}:
        raise AssertionError("the success estimator was omitted from multiplicity accounting")


def test_campaign_dispatches_independent_case_analyses(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    first, second = tmp_path / "qubit", tmp_path / "optical"
    qi_run(first)
    qd_run(second)
    dispatches = []
    original = analysis.ordered_map

    def dispatch(function: Any, jobs: Any, **options: Any) -> Any:
        dispatches.append((function.__name__, len(jobs), options))
        return original(function, jobs, **options)

    monkeypatch.setenv("GOROROBA_WORKERS", "1")
    monkeypatch.setattr(analysis, "ordered_map", dispatch)
    result = analysis.analyze_runs([first, second])
    if ("_analyze_case", 2, {"min_items": 1}) not in dispatches:
        raise RuntimeError("independent campaign cases must reach the ordered worker pool")
    if [batch["case"] for batch in result["batches"]] != ["qubit", "optical"]:
        raise RuntimeError("case dispatch must preserve requested campaign order")


def test_serial_and_pooled_campaign_reports_match(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    first, second = tmp_path / "qubit", tmp_path / "optical"
    qi_run(first)
    qd_run(second)
    monkeypatch.setenv("GOROROBA_WORKERS", "1")
    serial = analysis.analyze_runs([first, second])
    monkeypatch.setenv("GOROROBA_WORKERS", "2")
    pooled = analysis.analyze_runs([first, second])
    if json.dumps(serial, sort_keys=True) != json.dumps(pooled, sort_keys=True):
        raise RuntimeError("worker allocation changed report identities, denominators or analysis bytes")


def test_empty_success_partition_has_no_estimator_and_optical_default_covers_648() -> None:
    result = analysis.analyze_counts(reference(success_outputs=[]), [1, 1, 0, 0])
    if "success" in result or analysis.DEFAULT_ENDPOINTS != 648 or analysis.required_shots() != 1575:
        raise AssertionError("the primary optical family needs 648 actual physical-output endpoints")


def test_campaign_manifest_digest_binds_the_scientific_setting(tmp_path: Path) -> None:
    case = tmp_path / "run"
    qi_run(case)
    campaign = tmp_path / "campaign.json"
    save(campaign, {"schema": "quantum-experiment-campaign-v1", "cases": [{"path": "run", "sha256": "wrong"}]})
    with pytest.raises(ValueError, match="frozen sha256"):
        analysis.analyze_runs([case], campaign=campaign)


def test_empirical_readout_gate_checks_every_logical_output() -> None:
    controls: dict[str, Any] = {
        "zero": {"prepared": 0, "probability_one": [0.1, 0.8]},
        "one": {"prepared": 1, "probability_one": [0.9, 0.1]},
    }
    result = analysis.readout_admission(controls, 0.2, 2)
    if result["status"] != "inconclusive" or result["per_logical_bit"][1]["contrast"] >= 0:
        raise AssertionError("an inverted output readout passed the empirical contrast gate")
    controls["one"]["probability_one"][1] = 1.0
    controls["zero"]["probability_one"][1] = 0.0
    if analysis.readout_admission(controls, 0.2, 2)["status"] != "empirical-controls-met":
        raise AssertionError("strong empirical readout references failed the registered gate")
    if analysis.readout_admission({}, 0.2, 2)["status"] != "inconclusive":
        raise AssertionError("missing readout controls passed admission")


def test_success_precision_participates_in_the_science_admission_gate() -> None:
    row = reference(
        requested_probabilities=[0.25] * 4,
        native_probabilities=[0.25] * 4,
        active_outputs=[0, 1, 2, 3],
        leakage_outputs=[],
        success_outputs=[0, 1],
    )
    result = analysis.analyze_counts(row, [325] * 4)
    if not all((upper - lower) / 2 < 0.05 for lower, upper in result["iid_model_intervals"]):
        raise AssertionError("fixture needs individually precise output bins")
    if result["iid_model_precision_met"]:
        raise AssertionError("the wider primary herald interval was omitted from precision admission")


def test_readout_job_short_count_is_incomplete_and_binary_strings_are_validated(tmp_path: Path) -> None:
    case = tmp_path / "short-readout"
    qi_run(case)
    add_readout_controls(case, ["00"] * 3, ["11"] * 4)
    result = analysis.analyze_runs([case])
    batch = result["batches"][0]
    if result["complete"] or batch["acquisition_admission"] != "inconclusive":
        raise AssertionError("a short readout job passed the acquisition completeness gate")
    if batch["readout_admission"]["status"] != "empirical-controls-met":
        raise AssertionError("the raw contrast assessment was conflated with missing-count admission")
    raw = case / "raw/readout-0.cq.json"
    save(raw, ["invalid"] * 3)
    collection = json.loads((case / "results.json").read_text())
    collection["jobs"][1]["results"][0]["results"] = ["invalid"] * 3
    save(case / "results.json", collection)
    with pytest.raises(ValueError, match="binary register width"):
        analysis.analyze_runs([case])


def test_optical_template_prediction_does_not_claim_remote_compilation(tmp_path: Path) -> None:
    case = tmp_path / "optical"
    qd_run(case)
    result = analysis.analyze_runs([case])
    row = result["batches"][0]["settings"][0]
    if row["remote_compiled_prediction"]["status"] != "unavailable" or row["observed_minus_compiled"] is not None:
        raise AssertionError("the unavailable physical mesh was replaced by a logical-template prediction")
    if row["observed_minus_template"] != [0.0, -0.2, 0.2, 0.0]:
        raise AssertionError("logical-template conformance should remain observable")
    if result["analysis_source_sha256"] != analysis.digest(Path(analysis.__file__)):
        raise AssertionError("the analysis artifact lacks its exact analyzer identity")


def test_returned_optical_operator_is_reconstructed_without_sampling() -> None:
    import perceval as pcvl

    circuit = pcvl.Circuit(4).add(0, pcvl.BS.Rx(theta=0.0)).add(2, pcvl.PS(0.3))
    text = pcvl.serialization.serialize(circuit)
    fields = {"computed_circuit": text, "computed_input": ":PCVL:BasicState:|0,1,0,0>"}
    result = analysis.remote_compiled_prediction(fields, 4)
    if result["status"] != "reconstructed" or result["probabilities"] != [0.0, 1.0, 0.0, 0.0]:
        raise AssertionError(result)
    fields["computed_input"] = ":PCVL:BasicState:|1,1,0,0>"
    with pytest.raises(ValueError, match="one-photon width"):
        analysis.remote_compiled_prediction(fields, 4)


def test_balanced_contrast_requires_executed_order_and_repeated_identity() -> None:
    batches: list[dict[str, Any]] = []
    for order, (name, weight, source, probability) in enumerate(
        (
            ("dark", 1, "dark-source", 0.1),
            ("bright", -1, "bright-source", 0.9),
            ("bright-repeat", -1, "bright-source", 0.8),
            ("dark-repeat", 1, "dark-source", 0.2),
        )
    ):
        batches.append(
            {
                "provider": "qi",
                "backend": "tuna_17",
                "acquisition_admission": "empirical-controls-met",
                "settings": [
                    {
                        "name": name,
                        "family": "sedenion-lcu",
                        "acquisition_order": order,
                        "contrast_weight": weight,
                        "compiled_source_sha256": source,
                        "execution_envelope": {"lower": 10 + order * 2, "upper": 11 + order * 2},
                        "success": {"observed": probability},
                    }
                ],
            }
        )
    contrast = analysis.balanced_contrasts(batches)["tuna_17"]
    if contrast["status"] != "descriptive-contrast-admitted" or abs(contrast["dark_minus_bright"] + 0.7) > 1e-12:
        raise AssertionError(contrast)
    batches[3]["settings"][0]["compiled_source_sha256"] = "changed-dark"
    changed = analysis.balanced_contrasts(batches)["tuna_17"]
    if changed["dark_minus_bright"] is not None:
        raise AssertionError("a requested repeat cannot certify the returned operator identity")
    if changed["descriptive_dark_minus_bright"] is None:
        raise AssertionError("failed admission must preserve the explicitly descriptive observed contrast")
    batches[3]["settings"][0]["compiled_source_sha256"] = "dark-source"
    batches[3]["settings"][0]["execution_envelope"]["lower"] = 10
    if analysis.balanced_contrasts(batches)["tuna_17"]["status"] != "inconclusive":
        raise AssertionError("overlapping execution envelopes cannot establish the arm order")
