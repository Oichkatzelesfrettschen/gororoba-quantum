"""The QX preflight successor reads acquisitions through qi_records and keeps the design's own conditions."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, cast

import pytest
import qi_zz_map_qx
from qi_zz_map_qx_analysis import DESIGN

import qi_records
import qi_zz_preflight


def _check(condition: object, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _case(root: Path, **kwargs: object) -> tuple[Path, Path]:
    return qi_zz_preflight.synthetic_case(root, DESIGN, **kwargs)  # type: ignore[arg-type]


def _analyze(plan: Path, runs: Path) -> dict[str, object]:
    return qi_zz_preflight.analyze(plan, runs, DESIGN)


def test_ideal_fixture_passes_and_binds_its_sources(tmp_path: Path) -> None:
    plan, runs = _case(tmp_path)
    verdict = _analyze(plan, runs)
    expected = [{"batch": "batch-000", "file": "fixture.cq", "job": "synthetic-job", "failures": []}]
    _check(verdict["passes"] and verdict["circuits"] == expected, f"ideal fixture verdict {verdict['circuits']}")
    digests = verdict["source_digests"]
    _check(
        isinstance(digests, dict) and set(digests) == {"analyzer", "reader", "criteria"}, "source digests incomplete"
    )
    criteria = qi_records.digest(Path(qi_zz_map_qx.__file__).read_bytes())
    _check(
        isinstance(digests, dict) and digests["criteria"] == criteria, "criteria digest is not the pinned producer's"
    )
    inputs = verdict["input_sha256"]
    _check(isinstance(inputs, dict) and "batch-000/raw/fixture.cq.json" in inputs, "raw digest absent from the inputs")


def test_relocated_acquisition_reads_identically(tmp_path: Path) -> None:
    plan_a, runs_a = _case(tmp_path / "a")
    plan_b, runs_b = _case(tmp_path / "b" / "nested")
    a, b = _analyze(plan_a, runs_a), _analyze(plan_b, runs_b)
    _check(a["circuits"] == b["circuits"] and a["input_sha256"] == b["input_sha256"], "relocation changed the reading")


def test_failed_job_indexes_but_fails_the_design(tmp_path: Path) -> None:
    plan, runs = _case(tmp_path, status="failed")
    acquisition = qi_records.read_run(runs / "batch-000")
    _check(acquisition.statuses == {"failed": 1}, f"statuses {acquisition.statuses}")
    with pytest.raises(ValueError, match="QX job incomplete"):
        _analyze(plan, runs)


def test_changed_circuit_roles_rejected(tmp_path: Path) -> None:
    plan, runs = _case(tmp_path)
    value = json.loads(plan.read_bytes())
    value["circuits"][0]["quadrature"] = "x"
    plan.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ValueError, match="circuit roles differ"):
        _analyze(plan, runs)


def test_wrong_job_identity_rejected_by_the_reader(tmp_path: Path) -> None:
    plan, runs = _case(tmp_path)
    path = runs / "batch-000/results.json"
    value = json.loads(path.read_bytes())
    value["jobs"][0]["job"]["id"] = "another-job"
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ValueError, match="results.json jobs differ"):
        _analyze(plan, runs)


def test_empty_design_never_passes(tmp_path: Path) -> None:
    plan, _ = _case(tmp_path)
    value = json.loads(plan.read_bytes())
    value.update(circuits=[], batches=[], cost={"total_jobs": 0})
    plan.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ValueError, match="empty or inconsistent preflight design"):
        _analyze(plan, tmp_path / "absent")


def test_circuit_count_must_match_the_declared_jobs(tmp_path: Path) -> None:
    plan, runs = _case(tmp_path)
    value = json.loads(plan.read_bytes())
    value["cost"]["total_jobs"] = 2
    plan.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ValueError, match="empty or inconsistent preflight design"):
        _analyze(plan, runs)


def test_biased_y_probe_fails_the_familywise_bound(tmp_path: Path) -> None:
    plan, runs = _case(tmp_path, histogram={"11": qi_zz_map_qx.SHOTS})
    verdict = _analyze(plan, runs)
    circuits = verdict["circuits"]
    _check(not verdict["passes"], "a Y probe pinned to one outcome passed")
    _check(isinstance(circuits, list) and "familywise" in circuits[0]["failures"][0], f"failures {circuits}")


def test_repeated_filename_across_batches_is_judged_by_its_own_batch(tmp_path: Path) -> None:
    """A biased Y circuit in batch-000 keeps failing when batch-001 holds an X circuit under the same filename."""
    plan, runs = _case(tmp_path, histogram={"11": qi_zz_map_qx.SHOTS})
    shutil.copytree(runs / "batch-000", runs / "batch-001")
    second = runs / "batch-001"
    cases = json.loads((second / "cases.json").read_bytes())
    cases["circuits"][0]["quadrature"] = "x"
    cases_text = json.dumps(cases, indent=1, sort_keys=True) + "\n"
    (second / "cases.json").write_text(cases_text, encoding="utf-8")
    receipt = json.loads((second / "submission.json").read_bytes())
    receipt["cases_sha256"] = qi_records.digest(cases_text.encode())
    receipt["batch_job"] = "synthetic-batch-2"
    receipt["jobs"][0]["job"] = "synthetic-job-2"
    (second / "submission.json").write_text(json.dumps(receipt), encoding="utf-8")
    collected = json.loads((second / "results.json").read_bytes())
    collected["jobs"][0]["job"].update(id="synthetic-job-2", batch_job_id="synthetic-batch-2")
    collected["jobs"][0]["results"][0]["job_id"] = "synthetic-job-2"
    (second / "results.json").write_text(json.dumps(collected), encoding="utf-8")
    value = json.loads(plan.read_bytes())
    value["circuits"].append({**cases["circuits"][0], "batch_directory": "batch-001"})
    value["batches"].append({"directory": "batch-001", "cases_sha256": receipt["cases_sha256"]})
    value["cost"]["total_jobs"] = 2
    plan.write_text(json.dumps(value), encoding="utf-8")
    verdict = _analyze(plan, runs)
    rows = cast(list[dict[str, Any]], verdict["circuits"])
    _check([row["batch"] for row in rows] == ["batch-000", "batch-001"], f"batch order {rows}")
    # Under its own Y row batch-000 fails the familywise bound; under its own X row the same
    # counts fail the deterministic probe rule. A shared lookup would judge both by one row.
    _check("familywise" in rows[0]["failures"][0], f"batch-000 {rows[0]}")
    _check("deterministic q0" in rows[1]["failures"][0], f"batch-001 {rows[1]}")
