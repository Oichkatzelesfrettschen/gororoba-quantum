"""Contract for qd_box_kite_analysis.runs_under: the selection follows each run's case schema and the exclusion
globs, so a run of another case family never reaches the box-kite analysis.
"""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
import qd_box_kite_analysis as analysis


def make_run(root: Path, name: str, schema: str) -> None:
    (root / name).mkdir()
    (root / name / "cases.json").write_text(json.dumps({"schema": schema}))


def test_selection_follows_case_schema_and_exclusions() -> None:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        make_run(root, "b-sim_belenos-box_kite_photonic_single-job-00", "qd-box-kite-cases-v1")
        make_run(root, "a-sim_belenos-belenos_mesh-job-00", "qd-belenos-mesh-cases-v1")
        make_run(root, "c-qpu_belenos-belenos_mesh-job-03", "qd-belenos-mesh-cases-v1")
        make_run(root, "d-qpu_belenos-bdsc_qualification-tc-def-e1", "qd-bdsc-cases-v1")
        (root / "e-no-case").mkdir()
        selected = [run.name for run in analysis.runs_under(root, ["*-qpu_belenos-belenos_mesh-*"])]
        if selected != ["a-sim_belenos-belenos_mesh-job-00", "b-sim_belenos-box_kite_photonic_single-job-00"]:
            raise AssertionError(selected)


def test_empty_selection_fails() -> None:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        make_run(root, "d-qpu_belenos-bdsc_qualification-tc-def-e1", "qd-bdsc-cases-v1")
        with pytest.raises(SystemExit):
            analysis.runs_under(root, [])
