"""Identity, denominator and admission mutants must not inflate evidence."""

from __future__ import annotations

import copy
import hashlib
from typing import Any, cast

import acquisition_decisions as decisions
import evidence_closure as closure
import pytest


def snapshot(name: str, run: str, schema: str = "research-state-v2") -> dict:
    row = {
        "provider": "quandela",
        "job_id": "same-physical-job",
        "run": run,
        "acquisition_id": "a",
        "planned_observations": 1,
        "submitted_shot_ceiling": 100,
        "provider_reported_shots": None,
        "returned_samples": 75,
        "session": None,
        "calibration": None,
        "backend": "qpu:belenos",
    }
    return {
        "source": {"name": name, "commit": "a" * 40},
        "schema": schema,
        "claims": [],
        "observations": [row],
        "declared_unretained_qi": [],
    }


def test_locations_and_schema_migration_do_not_multiply_jobs() -> None:
    first = snapshot("first", "one", "research-state-v1")
    second = snapshot("second", "two")
    view = closure.reconcile([first, second])
    if len(view["identities"]) != 1:
        raise AssertionError("A moved acquisition was counted twice")
    job = view["identities"][0]
    if not {"multi-location execution", "v1-to-v2 migration"} <= set(job["classifications"]):
        raise AssertionError("Location/migration provenance missing")
    if job["denominators"]["returned_samples"]["value"] != 75:
        raise AssertionError("Repeated observations inflated a denominator")


def test_unknown_is_not_zero_and_conflicts_have_no_selected_total() -> None:
    rows: list[dict[str, Any]] = [{"shots": None}, {"shots": 0}]
    if closure.consensus(rows, "shots")["value"] != 0 or closure.consensus(rows[:1], "shots")["value"] is not None:
        raise AssertionError("Unknown and explicit zero were conflated")
    rows += [{"shots": 100}]
    if closure.consensus(rows, "shots")["value"] is not None:
        raise AssertionError("A conflicting observation was silently preferred")


def test_cross_branch_retention_gap_is_not_missing_physical_data() -> None:
    first = snapshot("first", "one")
    first["declared_unretained_qi"] = [123]
    second = snapshot("second", "two")
    second["observations"][0].update(provider="quantum_inspire", job_id="123")
    view = closure.reconcile([first, second])
    if any("retention gap" in item["reason"] for item in view["unresolved"]):
        raise AssertionError("Another branch's retained identity was called missing")


def test_legacy_and_ambiguous_dispatch_stay_unresolved() -> None:
    if closure.classify_record({}, False)["classification"] != "unresolved":
        raise AssertionError("Legacy absence of dispatch metadata was treated as no execution")
    if (
        closure.classify_record({"submission": {"started": "then"}}, False)["classification"]
        != "ambiguously dispatched"
    ):
        raise AssertionError("A dispatch attempt without a job identity was counted as completed")


def test_same_job_scores_are_removed_together() -> None:
    rows = [
        {"file": "one", "case": "dark", "shots": 100, "selector_zero_count": 10},
        {"file": "one", "case": "bright", "shots": 100, "selector_zero_count": 90},
        {"file": "two", "case": "dark", "shots": 100, "selector_zero_count": 20},
        {"file": "two", "case": "bright", "shots": 100, "selector_zero_count": 60},
    ]
    result = closure.raw_visibility_sensitivity(rows)
    expected = [0.4, 0.8]
    actual = [row["raw_contrast"] for row in result["leave_one_compiled_job_out"]]
    if any(abs(a - b) > 1e-12 for a, b in zip(actual, expected, strict=True)):
        raise AssertionError("A shared-shot score was deleted without its partner")


def test_probability_validation_rejects_unormalized_tvd() -> None:
    with pytest.raises(ValueError, match="normalized"):
        closure.tv([2.0, 0.0], [0.0, 1.0])
    if closure.tv([1.0, 0.0], [0.0, 1.0]) != 1:
        raise AssertionError("Disjoint distributions must have TVD one")


def test_cancellation_is_bound_to_job_and_receipt() -> None:
    raw = b"one immutable submission"
    receipt = {
        "schema": "job-cancellation-authority-v1",
        "provider": "quandela",
        "job_id": "owned-job",
        "authority": "explicit user instruction for owned-job",
        "submission_receipt_sha256": hashlib.sha256(raw).hexdigest(),
        "queue_scope_authorizes_other_jobs": False,
    }
    decisions.validate_cancellation(receipt, "quandela", "owned-job", raw)
    with pytest.raises(ValueError, match="exact provider/job"):
        decisions.validate_cancellation(receipt, "quandela", "someone-elses-job", raw)
    with pytest.raises(ValueError, match="different submission"):
        decisions.validate_cancellation(receipt, "quandela", "owned-job", b"different record")


def test_future_case_cannot_omit_power_or_stop_without_retry() -> None:
    case: dict[str, Any] = {
        "schema": "acquisition-decision-v1",
        **{
            k: "specified"
            for k in (
                "case_id",
                "objective",
                "discriminating_observable",
                "trial_definition",
                "observation_chain",
                "dependence_model",
                "layout_timing_identity",
                "processing_policy",
                "end_without_retry",
            )
        },
        "alternatives": ["history", "stable target"],
        "stopping_outcomes": dict.fromkeys(decisions.OUTCOMES, "specified"),
        "power_model": {"status": "qualified", "evidence": "retained local qualification"},
        "shot_ceiling": 100,
        "seconds_ceiling": 1.0,
        "credits_ceiling": 0.0,
        "reserve_seconds": 60.0,
        "retry_authorized": False,
    }
    decisions.validate_decision(case)
    bad = copy.deepcopy(case)
    bad["power_model"]["status"] = "unavailable"
    with pytest.raises(ValueError, match="not qualified"):
        decisions.validate_decision(bad)
    bad = copy.deepcopy(case)
    bad["retry_authorized"] = True
    with pytest.raises(ValueError, match="automatic retry"):
        decisions.validate_decision(bad)


def test_quandela_per_iteration_shots_are_not_a_job_total() -> None:
    class FixtureTree:
        def optional(self, path: str) -> dict:
            if path.endswith("submission.json"):
                return {"job_id": "job", "platform": "qpu:belenos", "max_shots": 50}
            if path.endswith("cases.json"):
                return {"iterations": 2}
            return {
                "job_id": "job",
                "shots": 3,
                "counts": {"1,0": 4, "0,1": 3},
                "status": {"status": "completed"},
                "iterations": [{"result_fields": {"nb_shots_used": 7}}, {"result_fields": {"nb_shots_used": 9}}],
            }

    row = closure.quandela(cast(closure.Tree, FixtureTree()), "run", {"id": "a"})[0]
    if row["provider_reported_shots"] != 16 or row["submitted_shot_ceiling"] != 50:
        raise AssertionError("Iteration ceiling multiplied or used as completed shots")


def test_withdrawal_includes_analytical_and_control_roots() -> None:
    snap = snapshot("main", "run")
    snap["observations"][0].update(execution_kind="hardware", compilation=None)
    snap["claims"] = [
        {
            "id": "hardware-claim",
            "evidence_class": "preregistered hardware inference",
            "status": "established",
            "statement": "bounded observation",
            "boundary": "one job",
            "acquisitions": ["a"],
            "assumptions": [],
            "depends_on": ["ideal-control"],
            "evidence": [{"path": "analysis.json", "sha256": "b" * 64}],
            "gates": {"gate": "replay"},
        }
    ]
    snap["claims"].append(
        {
            "id": "ideal-control",
            "evidence_class": "circuit-conformance check",
            "status": "established",
            "statement": "ideal law",
            "boundary": "ideal only",
            "acquisitions": [],
            "assumptions": [],
            "depends_on": [],
            "evidence": [{"path": "control.json", "sha256": "c" * 64}],
            "gates": {},
        }
    )
    report = closure.dependency_report(closure.reconcile([snap]))["claims"][0]
    roots = [item["root"] for item in report["withdrawal"]]
    if not all(any(root.startswith(prefix) for root in roots) for prefix in ["job:", "analysis:", "gate:", "claim:"]):
        raise AssertionError("A declared support category escaped withdrawal")
    if not report["qualification_gaps"] or any(v["status"] != "unavailable" for v in report["numerical_leave_one_out"]):
        raise AssertionError("Dependency withdrawal was promoted to numerical re-estimation")
    if not any(root.startswith("analysis:control.json:") for root in report["inherited_support_roots"]):
        raise AssertionError("A shared analysis root was lost through transitive support")
