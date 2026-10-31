"""The QX preflight successor reads acquisitions through qi_records and keeps the design's own conditions."""

from __future__ import annotations

import json
from pathlib import Path

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
    expected = [{"file": "fixture.cq", "job": "synthetic-job", "failures": []}]
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
