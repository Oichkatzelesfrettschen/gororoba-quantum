"""The platform-bound Ascella acquisition pair admits only its own request and states the current billing rule."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import ascella_predecessor_acquisition_analysis as analysis
import ascella_predecessor_acquisition_case as acquisition
import ascella_predecessor_analysis as frozen_analysis
import ascella_predecessor_case as original
import ascella_predecessor_current_analysis as current_analysis
import ascella_predecessor_current_case as current
import billing_rule_v2
import pytest
import qd_platform as qd
from billing_rule_v2 import RULE

from qd_records import RecordError

ROOT = original.ROOT
SOURCE_RUN = ROOT / original.MESH_RUNS["job-00"]
# Settings 0 to 7 in schedule order: predecessor, target, predecessor, target, ... Each law lists the number of
# events on single-photon output modes 0, 1, 2 and 3 out of 32768; every other mode holds none. The values are
# chosen so that every contrast below follows by hand from the vectors (0, 1/2, -1/2 arithmetic).
LAWS = (
    (32768, 0, 0, 0),  # 0 predecessor
    (32768, 0, 0, 0),  # 1 target T1 = (1, 0, 0)
    (0, 0, 0, 32768),  # 2 predecessor
    (16384, 16384, 0, 0),  # 3 target T3 = (1/2, 1/2, 0)
    (32768, 0, 0, 0),  # 4 predecessor
    (16384, 0, 16384, 0),  # 5 target T5 = (1/2, 0, 1/2)
    (16384, 0, 0, 16384),  # 6 predecessor
    (32768, 0, 0, 0),  # 7 target T7 = (1, 0, 0)
)


def test_the_request_states_the_current_rule_and_is_admitted_by_its_pair() -> None:
    for platform in acquisition.PLATFORMS:
        manifest = json.loads(acquisition.documents(platform)["cases.json"])
        if manifest["acquisition_admission"] != "ready":
            raise AssertionError("a request with its own analyzer must carry the ready admission")
        if manifest["preregistered"]["credit_basis"] != RULE:
            raise AssertionError("the request does not state the current billing rule")
        if manifest["platforms"] != [platform] or manifest["job"] != f"{platform.replace(':', '-')}-billing-rule":
            raise AssertionError("the request does not bind its platform and job")
        # qd_platform.submit reads an absent key as ready; the explicit value is what the pair adds.
        if manifest.get("acquisition_admission", "ready") != "ready":
            raise AssertionError("qd_platform.submit would refuse the request")
        bound = qd.acquisition_sources(manifest)
        if not set(acquisition.sources(platform)) <= set(bound):
            raise AssertionError("the review packet does not bind the builder, analyzer and shared modules")
        if manifest["preregistered"]["current_case_sources"] != {n: bound[n] for n in acquisition.sources(platform)}:
            raise AssertionError("the registered source digests differ from the verified ones")


def test_the_request_differs_from_the_record_derivation_only_in_admission_platform_job_and_sources() -> None:
    import ascella_predecessor_case_v2 as derivation

    for platform in acquisition.PLATFORMS:
        derived = json.loads(derivation.documents()["cases.json"])
        built = json.loads(acquisition.documents(platform)["cases.json"])
        if derived["acquisition_admission"] != billing_rule_v2.ADMISSION:
            raise AssertionError("the record derivation no longer carries awaiting-analyzer")
        registered = built["preregistered"].pop("current_case_sources")
        for key in ("platforms", "job", "acquisition_admission"):
            derived.pop(key)
            built.pop(key)
        if built != derived:
            raise AssertionError("the request changed a scientific or billing field of the derivation")
        if set(registered) != set(acquisition.sources(platform)):
            raise AssertionError("the bound sources differ")


def test_a_platform_outside_the_chip_is_refused() -> None:
    for platform in ("qpu:belenos", "sim:belenos", "sim:slos"):
        with pytest.raises(ValueError, match="not an admitted platform"):
            acquisition.documents(platform)


def test_check_refuses_a_retained_request_that_differs_or_names_another_platform(tmp_path: Path) -> None:
    request = tmp_path / "request"
    original.publish_case(request, acquisition.documents("sim:ascella"))
    if acquisition.check(request)["platforms"] != ["sim:ascella"]:
        raise AssertionError("a built request does not reproduce")
    manifest = json.loads((request / "cases.json").read_bytes())
    manifest["platforms"] = ["qpu:ascella"]
    (request / "cases.json").write_text(json.dumps(manifest, indent=1) + "\n")
    with pytest.raises(ValueError, match="differs from the source-derived request"):
        acquisition.check(request)


def test_the_current_analyzer_and_the_successor_check_refuse_each_other_s_request(tmp_path: Path) -> None:
    request = tmp_path / "request"
    original.publish_case(request, acquisition.documents("qpu:ascella"))
    with pytest.raises(ValueError, match="differs from the current source-derived request"):
        current_analysis.analyze(request, submission_sha256="0" * 64, results_sha256="0" * 64)
    legacy = tmp_path / "legacy"
    original.publish_case(legacy, current.documents())
    with pytest.raises(ValueError, match="differs from the source-derived request"):
        acquisition.check(legacy)


def synthetic_run(
    tmp_path: Path, platform: str, laws: tuple[tuple[int, ...], ...] = LAWS, same_circuit: bool = True
) -> Path:
    """A completed run of the successor request for `platform`: the retained job-00 body and receipt rebound to the
    request, with the given laws as returned counts. `same_circuit` keeps the retained computed_circuit string, which
    qpu:ascella must return; sim:ascella returns another."""
    import perceval as pcvl
    from perceval.serialization import OutputArchive, Serialization, deserialize, serialize

    request = tmp_path / "request"
    original.publish_case(request, acquisition.documents(platform))
    manifest = acquisition.check(request)
    source_results = json.loads((SOURCE_RUN / "results.json").read_bytes())
    body = json.loads((SOURCE_RUN / "job-body.json").read_bytes())
    computation = deserialize(body["payload"]["computation"])
    observed = []
    for setting, law in zip(manifest["settings"], laws, strict=True):
        previous = source_results["iterations"][setting["source_observation_index"]]
        params = {
            "circuit_params": setting["circuit_params"],
            "compilation_seed": setting["compilation_seed"],
            "max_samples": 32768,
            "max_shots": 32768,
        }
        states = {
            pcvl.BasicState("|" + ",".join("1" if mode == index else "0" for mode in range(12)) + ">"): events
            for index, events in enumerate(law)
            if events
        }
        fields = {**previous["result_fields"], "nb_shots_used": 32768}
        if not same_circuit:
            fields["computed_circuit"] = fields["computed_circuit"] + " "
        observed.append({**fields, "iteration": params, "results": serialize(pcvl.BSCount(states))})
    computation.iterations[:] = [copy.deepcopy(row["iteration"]) for row in observed]
    archive = OutputArchive()
    Serialization.serialize(computation, archive)
    body["payload"].update(computation=archive.to_text(), max_samples=32768, max_shots=32768)
    body.update(max_duration=300, platform_name=platform)
    job_id = "offline-acquisition-fixture"
    raw = {"job_id": job_id, "shots": 32768, "results": json.dumps({"results_list": observed})}
    raw_bytes = json.dumps(raw).encode()
    status = {"status": "completed", "duration": 40, "shots": 32768}
    submission = json.loads((SOURCE_RUN / "submission.json").read_bytes())
    submission.update(
        job_id=job_id,
        platform=platform,
        cases_sha256=frozen_analysis.digest(request / "cases.json"),
        body_sha256=original.sha256_bytes(json.dumps(body, sort_keys=True).encode()),
        approval="synthetic offline fixture",
        submitted_utc="2026-10-28T00:00:00Z",
        credit_ceiling=original.charge(32768),
    )
    result = {
        "schema": qd.COLLECTION_SCHEMA,
        "job_id": job_id,
        "status": status,
        "data": {"payload": body["payload"], "platform_name": platform},
        "result_sha256": original.sha256_bytes(raw_bytes),
        **qd.result_summary(raw_bytes, job_id, status, True, 8),
    }
    run = tmp_path / "run"
    (run / "raw").mkdir(parents=True)
    (run / "raw/result.json").write_bytes(raw_bytes)
    for name in ("cases.json", "circuit.json"):
        (run / name).write_bytes((request / name).read_bytes())
    for name, value in (("job-body.json", body), ("submission.json", submission), ("results.json", result)):
        (run / name).write_text(json.dumps(value))
    return run


def analyze(run: Path) -> dict[str, Any]:
    return analysis.analyze(
        run,
        submission_sha256=frozen_analysis.digest(run / "submission.json"),
        results_sha256=frozen_analysis.digest(run / "results.json"),
    )


@pytest.mark.parametrize("platform", acquisition.PLATFORMS)
def test_a_synthetic_run_reads_the_hand_computed_contrasts(tmp_path: Path, platform: str) -> None:
    run = synthetic_run(tmp_path, platform)
    report = analyze(run)
    # T1 - T3 - T5 + T7 over two: (1 - 1/2 - 1/2 + 1, -1/2, -1/2) / 2 = (1/2, -1/4, -1/4); norm = (1/2 + 1/4 + 1/4) / 2.
    # The reversal weights (-1, 1, -1, 1) / 2 give (0, 1/4, -1/4) and norm 1/4.
    # Predecessor pairs (0, 2) and (4, 6): distance 1 between disjoint laws and 1/2 between (1, 0) and (1/2, 1/2) on
    # modes 0 and 3.
    expected = {
        "schema": "ascella-predecessor-acquisition-analysis-v1",
        "platform": platform,
        "common_vector_exact": ["1/2", "-1/4", "-1/4"] + ["0"] * 9,
        "common_norm_exact": "1/2",
        "reversal_vector_exact": ["0", "1/4", "-1/4"] + ["0"] * 9,
        "reversal_norm_exact": "1/4",
        "predecessor_tvd_exact": ["1", "1/2"],
        "eligible_counts": [32768] * 8,
        "verdict": "descriptive-only",
        "physical_predecessor_attribution": "unavailable",
    }
    if {key: report[key] for key in expected} != expected:
        raise AssertionError({key: (report[key], expected[key]) for key in expected if report[key] != expected[key]})
    if report["cases_sha256"] != frozen_analysis.digest(run / "cases.json"):
        raise AssertionError("the report does not bind the request by its own sha256")
    if set(report["current_case_sources"]) != set(acquisition.sources(platform)):
        raise AssertionError("the report does not bind the successor sources")


def test_a_qpu_run_stops_on_a_returned_compilation_that_differs(tmp_path: Path) -> None:
    run = synthetic_run(tmp_path, "qpu:ascella", same_circuit=False)
    with pytest.raises(ValueError, match="identity differs"):
        analyze(run)


def test_a_simulator_run_reports_the_compilation_identity_it_does_not_require(tmp_path: Path) -> None:
    run = synthetic_run(tmp_path, "sim:ascella", same_circuit=False)
    report = analyze(run)
    matches = [row["identity_matches_preregistration"] for row in report["observations"]]
    if matches != [{"computed_circuit": False, "computed_input": True}] * 8:
        raise AssertionError(f"the identity report differs: {matches[0]}")


def test_a_run_of_another_platform_or_request_is_refused(tmp_path: Path) -> None:
    run = synthetic_run(tmp_path, "sim:ascella")
    receipt = json.loads((run / "submission.json").read_bytes())
    receipt["platform"] = "qpu:ascella"
    (run / "submission.json").write_text(json.dumps(receipt))
    with pytest.raises(RecordError, match="outside cases.json"):
        analyze(run)
    receipt["platform"] = "sim:ascella"
    body = json.loads((run / "job-body.json").read_bytes())
    body["platform_name"] = "qpu:ascella"
    receipt["body_sha256"] = original.sha256_bytes(json.dumps(body, sort_keys=True).encode())
    (run / "job-body.json").write_text(json.dumps(body))
    (run / "submission.json").write_text(json.dumps(receipt))
    with pytest.raises(ValueError, match="names 'qpu:ascella', not sim:ascella"):
        analyze(run)
    changed = synthetic_run(tmp_path / "second", "qpu:ascella")
    manifest = json.loads((changed / "cases.json").read_bytes())
    manifest["max_duration"] += 1
    (changed / "cases.json").write_text(json.dumps(manifest, indent=1) + "\n")
    with pytest.raises(ValueError, match="differs from the source-derived request"):
        analyze(changed)


def test_the_digest_anchors_bind_the_receipt_and_the_result(tmp_path: Path) -> None:
    run = synthetic_run(tmp_path, "qpu:ascella")
    receipt = frozen_analysis.digest(run / "submission.json")
    result = frozen_analysis.digest(run / "results.json")
    (run / "results.json").write_text("{}")
    with pytest.raises(ValueError, match="anchor"):
        analysis.analyze(run, submission_sha256=receipt, results_sha256=result)
