"""Bounded fixtures for the prospective correction score: the variance-ratio reading and the mesh gate."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ascella_correction_score as score  # noqa: E402

# docs/evidence/anu_qrng/draw-2026-10-31T193354Z.json index 4 (ledger row in
# docs/evidence/qrng_seeds/allocations.json).
FIXTURE_SEED = 29161
JOB_02 = ROOT / "results/quandela/runs/2026-10-25T184636Z-qpu_ascella-ascella_signed_coherence-job-02"


def test_a_table_that_matches_the_repeat_holds_and_an_unrelated_one_fails() -> None:
    """A repeat equal to the table plus counting-sized noise reads correction holds at R near its noise limit; a
    repeat independent of the table reads correction fails, since subtracting it adds its variance."""
    generator = np.random.default_rng(FIXTURE_SEED)
    table = generator.normal(0.0, 0.01, 56)
    table -= table.mean()
    matched = table + generator.normal(0.0, 0.002, 56)
    matched -= matched.mean()
    held = score.ratio_reading(matched, table, generator, 4000)
    if held["reading"] != "correction holds" or held["ratio"] != pytest.approx(
        matched.var(ddof=1) / (matched - table).var(ddof=1)
    ):
        raise AssertionError(held)
    unrelated = generator.normal(0.0, 0.01, 56)
    unrelated -= unrelated.mean()
    failed = score.ratio_reading(unrelated, table, generator, 4000)
    if failed["reading"] != "correction fails" or not failed["lower"] <= failed["ratio"] <= failed["upper"]:
        raise AssertionError(failed)


def test_the_mesh_gate_admits_job_02_and_refuses_a_swapped_mesh(tmp_path: Path) -> None:
    """job-02 against itself passes the gate; the same run with two settings' served circuits exchanged is refused."""
    if "all 64 served meshes" not in score.mesh_gate(JOB_02, JOB_02):
        raise AssertionError("job-02 failed its own mesh gate")
    run = tmp_path / "swapped"
    run.mkdir()
    shutil.copy(JOB_02 / "cases.json", run / "cases.json")
    results = json.loads((JOB_02 / "results.json").read_text(encoding="utf-8"))
    rows = results["iterations"]
    rows[1]["result_fields"]["computed_circuit"], rows[2]["result_fields"]["computed_circuit"] = (
        rows[2]["result_fields"]["computed_circuit"],
        rows[1]["result_fields"]["computed_circuit"],
    )
    (run / "results.json").write_text(json.dumps(results), encoding="utf-8")
    with pytest.raises(ValueError, match="2 of 64 served meshes left job-02's"):
        score.mesh_gate(JOB_02, run)
