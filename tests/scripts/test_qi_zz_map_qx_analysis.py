"""The QX preflight successor reads acquisitions through qi_records and keeps the design's own conditions."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import qi_zz_map_qx
import qi_zz_map_qx_analysis as analysis

import qi_records


def _check(condition: object, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_ideal_fixture_passes_and_binds_its_sources(tmp_path: Path) -> None:
    plan, runs = analysis.synthetic_case(tmp_path)
    verdict = analysis.analyze(plan, runs)
    expected = [{"file": "fixture.cq", "job": "synthetic-job", "failures": []}]
    _check(verdict["passes"] and verdict["circuits"] == expected, f"ideal fixture verdict {verdict['circuits']}")
    _check(set(verdict["source_digests"]) == {"analyzer", "reader", "criteria"}, "source digests incomplete")
    criteria = qi_records.digest(Path(qi_zz_map_qx.__file__).read_bytes())
    _check(verdict["source_digests"]["criteria"] == criteria, "criteria digest is not the pinned producer's")
    _check("batch-000/raw/fixture.cq.json" in verdict["input_sha256"], "raw file digest absent from the inputs")


def test_relocated_acquisition_reads_identically(tmp_path: Path) -> None:
    plan_a, runs_a = analysis.synthetic_case(tmp_path / "a")
    plan_b, runs_b = analysis.synthetic_case(tmp_path / "b" / "nested")
    a, b = analysis.analyze(plan_a, runs_a), analysis.analyze(plan_b, runs_b)
    _check(a["circuits"] == b["circuits"] and a["input_sha256"] == b["input_sha256"], "relocation changed the reading")


def test_failed_job_indexes_but_fails_the_design(tmp_path: Path) -> None:
    plan, runs = analysis.synthetic_case(tmp_path, status="failed")
    acquisition = qi_records.read_run(runs / "batch-000")
    _check(acquisition.statuses == {"failed": 1}, f"statuses {acquisition.statuses}")
    with pytest.raises(ValueError, match="QX job incomplete"):
        analysis.analyze(plan, runs)


def test_changed_circuit_roles_rejected(tmp_path: Path) -> None:
    plan, runs = analysis.synthetic_case(tmp_path)
    value = json.loads(plan.read_bytes())
    value["circuits"][0]["quadrature"] = "x"
    plan.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ValueError, match="circuit roles differ"):
        analysis.analyze(plan, runs)


def test_wrong_job_identity_rejected_by_the_reader(tmp_path: Path) -> None:
    plan, runs = analysis.synthetic_case(tmp_path)
    path = runs / "batch-000/results.json"
    value = json.loads(path.read_bytes())
    value["jobs"][0]["job"]["id"] = "another-job"
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ValueError, match="results.json jobs differ"):
        analysis.analyze(plan, runs)


def test_biased_y_probe_fails_the_familywise_bound(tmp_path: Path) -> None:
    plan, runs = analysis.synthetic_case(tmp_path, histogram={"11": qi_zz_map_qx.SHOTS})
    verdict = analysis.analyze(plan, runs)
    _check(not verdict["passes"], "a Y probe pinned to one outcome passed")
    _check("familywise" in verdict["circuits"][0]["failures"][0], f"failures {verdict['circuits'][0]['failures']}")
