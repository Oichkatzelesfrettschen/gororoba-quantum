"""Signed response contrasts preserve attribution and withhold physical-history claims."""

from __future__ import annotations

import copy
import json
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Any

import ascella_predecessor_analysis as analysis
import ascella_predecessor_case as case
import pytest


def rows(target_counts: list[int], total: int = 32768) -> list[list[int]]:
    targets = iter(target_counts)
    result = []
    for index in range(8):
        first = next(targets) if index % 2 else (total if index in (0, 6) else 0)
        result.append([first, total - first] + [0] * 10)
    return result


def test_linear_drift_cancels_before_the_norm() -> None:
    report = analysis.describe(rows([3277, 8192, 13107, 18022]))
    if Fraction(report["common_norm_exact"]) != 0 or Fraction(report["reversal_norm_exact"]) != Fraction(4915, 32768):
        raise AssertionError(report)
    if report["verdict"] != "descriptive-only" or "common_norm_bounds" in report:
        raise AssertionError("a descriptive projection cannot admit a confidence envelope")
    if (
        analysis._conditional_decision(analysis.conditional_envelopes(report))
        != "conditional-slot-response-below-0.1-tvd"
    ):
        raise AssertionError(report)


def test_quadratic_drift_passes_response_margin_without_causal_attribution() -> None:
    report = analysis.describe(rows([22282, 17039, 17039, 22282]))
    if Fraction(report["reversal_norm_exact"]) != 0 or Fraction(report["common_norm_exact"]) < Fraction(15, 100):
        raise AssertionError(report)
    envelopes = analysis.conditional_envelopes(report)
    bounded = {**report, **envelopes, "verdict": analysis._conditional_decision(envelopes)}
    if bounded["verdict"] != "conditional-slot-response-above-0.1-tvd":
        raise AssertionError(bounded)
    if bounded["physical_predecessor_attribution"] != "unavailable":
        raise AssertionError("a symmetric drift cannot identify physical predecessor causation")


def test_signed_reversal_is_not_erased_by_a_small_common_contrast() -> None:
    report = analysis.describe(rows([24576, 8192, 24576, 8192]))
    if report["common_norm_exact"] != "0" or report["reversal_norm_exact"] != "1/2":
        raise AssertionError(report)
    if (
        analysis._conditional_decision(analysis.conditional_envelopes(report))
        != "conditional-slot-response-below-0.1-tvd"
    ):
        raise AssertionError("the declared equivalence concerns the common contrast alone")


def test_outward_radius_and_bounds_enclose_high_precision_reference() -> None:
    with localcontext() as context:
        context.prec = 100
        reference = ((12 * Decimal(2).ln() + Decimal(160).ln()) / (2 * Decimal(32768))).sqrt()
        exact_point = Decimal(1) / Decimal(3)
        uncertainty = analysis.radius(32768)
        bounds = analysis.envelope(Fraction(1, 3), uncertainty)
        if (
            uncertainty < reference
            or Decimal(bounds[0]) > exact_point - reference
            or Decimal(bounds[1]) < exact_point + reference
        ):
            raise AssertionError((uncertainty, reference, bounds))


def test_unbound_envelopes_cannot_issue_a_decision() -> None:
    result = analysis.conditional_envelopes(analysis.describe(rows([3277, 8192, 13107, 18022])))
    if "verdict" in result:
        raise AssertionError("unbound confidence calculations cannot issue an acquisition decision")


def contract(path: Path) -> dict[str, Any]:
    manifest = case.check()
    evidence = []
    for claim in sorted(analysis.EVIDENCE_CLAIMS):
        artifact = path.parent / f"{claim}.txt"
        artifact.write_text("Synthetic review fixture; the model remains an explicit hypothesis.\n")
        evidence.append({"claim": claim, "file": artifact.name, "sha256": analysis.digest(artifact)})
    record = {
        "schema": "ascella-predecessor-sampling-contract-v1",
        "cases_sha256": analysis.digest(case.CASE / "cases.json"),
        "analysis_sources": manifest["analysis_sources"],
        "sampling_model": analysis.MODEL,
        "stopping_rule": analysis.STOPPING,
        "eligibility": manifest["eligibility"],
        "scope": "hypothesis-conditional-target-slot-response",
        "physical_predecessor_attribution": "unavailable",
        "family_alpha": "0.05",
        "delta_tvd": "0.1",
        "frozen_utc": "2026-10-27T00:00:00Z",
        "evidence": evidence,
    }
    path.write_text(json.dumps(record))
    return record


def test_contract_requires_external_anchor_preacquisition_freeze_and_bound_evidence(tmp_path: Path) -> None:
    path = tmp_path / "contract.json"
    record = contract(path)
    expected = analysis.digest(path)
    manifest = case.check()
    analysis.validate_contract(path, expected, manifest, "2026-10-28T00:00:00Z")
    with pytest.raises(ValueError, match="anchor"):
        analysis.validate_contract(path, "0" * 64, manifest, "2026-10-28T00:00:00Z")
    with pytest.raises(ValueError, match="before submission"):
        analysis.validate_contract(path, expected, manifest, "2026-10-26T00:00:00Z")
    (tmp_path / record["evidence"][0]["file"]).write_text("changed evidence")
    with pytest.raises(ValueError, match="anchor"):
        analysis.validate_contract(path, expected, manifest, "2026-10-28T00:00:00Z")


def test_contract_parses_the_bytes_bound_by_the_external_digest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "contract.json"
    early = contract(path)
    early_bytes = path.read_bytes()
    late = {**early, "frozen_utc": "2026-10-29T00:00:00Z"}
    path.write_text(json.dumps(late))
    late_bytes = path.read_bytes()
    expected = analysis.digest(path)
    manifest = case.check()
    actual_read_bytes = Path.read_bytes
    reads = 0

    def changing_read_bytes(candidate: Path) -> bytes:
        nonlocal reads
        if candidate == path:
            reads += 1
            return late_bytes if reads == 1 else early_bytes
        return actual_read_bytes(candidate)

    monkeypatch.setattr(Path, "read_bytes", changing_read_bytes)
    with pytest.raises(ValueError, match="before submission"):
        analysis.validate_contract(path, expected, manifest, "2026-10-28T00:00:00Z")


def test_contract_uses_verified_manifest_without_rereading_case(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "contract.json"
    contract(path)
    expected = analysis.digest(path)
    manifest = case.check()
    original_digest = analysis.digest

    def forbid_case_reread(candidate: Path) -> str:
        if candidate == case.CASE / "cases.json":
            raise AssertionError("contract validation reopened the frozen case")
        return original_digest(candidate)

    monkeypatch.setattr(analysis, "digest", forbid_case_reread)
    analysis.validate_contract(path, expected, manifest, "2026-10-28T00:00:00Z")


def test_duplicate_json_and_unpaired_contract_arguments_fail_closed(tmp_path: Path) -> None:
    path = tmp_path / "duplicate.json"
    path.write_text('{"sampling_model":"first","sampling_model":"second"}')
    with pytest.raises(ValueError, match="duplicate"):
        analysis.read_json(path)
    with pytest.raises(ValueError, match="both"):
        analysis.analyze(tmp_path, submission_sha256="0" * 64, results_sha256="0" * 64, contract_path=path)


def test_nonstring_evidence_digest_fails_with_a_contract_error(tmp_path: Path) -> None:
    path = tmp_path / "contract.json"
    record = contract(path)
    record["evidence"][0]["sha256"] = 123
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="external expected sha256"):
        analysis.validate_contract(path, analysis.digest(path), case.check(), "2026-10-28T00:00:00Z")


def entry(index: int) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    manifest = case.check()
    setting = manifest["settings"][index]
    source = case.ROOT / case.MESH_RUNS["job-00"]
    previous = json.loads((source / "results.json").read_bytes())["iterations"][setting["source_observation_index"]]
    fields = {**previous["result_fields"], "nb_shots_used": case.SHOTS_PER_ITERATION}
    echoed = {
        "circuit_params": setting["circuit_params"],
        "compilation_seed": setting["compilation_seed"],
        "max_samples": case.SAMPLES_PER_ITERATION,
        "max_shots": case.SHOTS_PER_ITERATION,
    }
    observed = {
        "iteration": echoed,
        "counts": {"1," + "0," * 10 + "0": 32767, "0," * 11 + "0": 1},
        "samples": case.SAMPLES_PER_ITERATION,
        "result_fields": fields,
    }
    return setting, observed, manifest["preregistered"]["compilation_identity"]


@pytest.mark.parametrize("mutation", ["input", "circuit", "seed", "missing", "count", "width"])
def test_entry_refuses_identity_mapping_and_incomplete_count_mutations(mutation: str) -> None:
    setting, observed, identities = entry(1)
    if mutation in {"input", "circuit"}:
        observed["result_fields"][f"computed_{mutation}"] += "changed"
    elif mutation == "seed":
        observed["iteration"]["compilation_seed"] += 1
    elif mutation == "missing":
        observed.pop("counts")
    elif mutation == "count":
        observed["samples"] -= 1
    else:
        observed["counts"] = {"1,0": 32768}
    with pytest.raises(ValueError):
        analysis._entry(setting, observed, identities)


def test_entry_preserves_invalid_event_denominator() -> None:
    setting, observed, identities = entry(1)
    result = analysis._entry(setting, observed, identities)
    if sum(result["eligible_port_counts"]) != 32767 or result["invalid_event_counts"]["zero_click"] != 1:
        raise AssertionError(result)
    if result["returned_events"] != 32768:
        raise AssertionError("ineligible events remain accounted for")


def test_real_serializer_to_offline_analyzer(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import perceval as pcvl
    from perceval.serialization import OutputArchive, Serialization, deserialize, serialize

    manifest = case.check()
    prior = case.ROOT / case.MESH_RUNS["job-00"]
    body = json.loads((prior / "job-body.json").read_bytes())
    computation = deserialize(body["payload"]["computation"])
    observed_entries = [entry(index)[1] for index in range(8)]
    computation.iterations[:] = [copy.deepcopy(observed["iteration"]) for observed in observed_entries]
    archive = OutputArchive()
    Serialization.serialize(computation, archive)
    body["payload"].update(
        computation=archive.to_text(), max_samples=case.SAMPLES_PER_ITERATION, max_shots=case.SHOTS_PER_ITERATION
    )
    body["max_duration"] = case.MAX_DURATION
    returned = []
    for observed in observed_entries:
        counts = pcvl.BSCount({pcvl.BasicState(f"|{state}>"): count for state, count in observed["counts"].items()})
        returned.append({**observed["result_fields"], "iteration": observed["iteration"], "results": serialize(counts)})
    raw: dict[str, Any] = {
        "job_id": "offline-predecessor-fixture",
        "shots": case.SHOTS_PER_ITERATION,
        "results": json.dumps({"results_list": returned}),
    }
    raw_bytes = json.dumps(raw).encode()
    status = {"status": "completed", "duration": 40, "shots": case.SHOTS_PER_ITERATION}
    submission = json.loads((prior / "submission.json").read_bytes())
    submission.update(
        job_id=raw["job_id"],
        cases_sha256=analysis.digest(case.CASE / "cases.json"),
        body_sha256=case.sha256_bytes(json.dumps(body, sort_keys=True).encode()),
        approval="synthetic offline fixture",
        submitted_utc="2026-10-28T00:00:00Z",
        credit_ceiling=case.charge(case.SHOTS_PER_ITERATION),
    )
    result = {
        "schema": analysis.qd.COLLECTION_SCHEMA,
        "job_id": raw["job_id"],
        "status": status,
        "data": {"payload": body["payload"]},
        "result_sha256": case.sha256_bytes(raw_bytes),
        **analysis.qd.result_summary(raw_bytes, raw["job_id"], status, True, 8),
    }
    (tmp_path / "raw").mkdir()
    (tmp_path / "raw/result.json").write_bytes(raw_bytes)
    for name, value in (
        ("cases.json", manifest),
        ("job-body.json", body),
        ("submission.json", submission),
        ("results.json", result),
    ):
        (tmp_path / name).write_bytes(
            (case.CASE / name).read_bytes() if name == "cases.json" else json.dumps(value).encode()
        )
    (tmp_path / "circuit.json").write_bytes((case.CASE / "circuit.json").read_bytes())
    submission_sha = analysis.digest(tmp_path / "submission.json")
    results_sha = analysis.digest(tmp_path / "results.json")
    report = analysis.analyze(tmp_path, submission_sha256=submission_sha, results_sha256=results_sha)
    if report["verdict"] != "descriptive-only" or report["physical_predecessor_attribution"] != "unavailable":
        raise AssertionError(report)
    anchored_results = (tmp_path / "results.json").read_bytes()
    anchor = analysis._anchor

    def change_after_anchor(path: Path, expected: str) -> bytes:
        data = anchor(path, expected)
        if path == tmp_path / "results.json":
            path.write_text("{}")
        return data

    with monkeypatch.context() as patch:
        patch.setattr(analysis, "_anchor", change_after_anchor)
        stable = analysis.analyze(tmp_path, submission_sha256=submission_sha, results_sha256=results_sha)
    (tmp_path / "results.json").write_bytes(anchored_results)
    if stable["common_norm_exact"] != report["common_norm_exact"]:
        raise AssertionError("analysis must use the exact results bytes bound by its external anchor")
    sampling = tmp_path / "sampling.json"
    contract(sampling)
    bounded = analysis.analyze(
        tmp_path,
        submission_sha256=submission_sha,
        results_sha256=results_sha,
        contract_path=sampling,
        contract_sha256=analysis.digest(sampling),
    )
    if "common_norm_bounds" not in bounded or bounded["physical_predecessor_attribution"] != "unavailable":
        raise AssertionError(bounded)
    result["iterations"][0]["counts"] = {"1,0": 32768}
    (tmp_path / "results.json").write_text(json.dumps(result))
    with pytest.raises(ValueError, match="anchor"):
        analysis.analyze(tmp_path, submission_sha256=submission_sha, results_sha256=results_sha)
    with pytest.raises(analysis.qd.PlatformError, match="differs from the raw result"):
        analysis.analyze(
            tmp_path,
            submission_sha256=submission_sha,
            results_sha256=analysis.digest(tmp_path / "results.json"),
        )
