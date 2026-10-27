"""Frozen element offsets for Ascella's replication meshes, fixed before those meshes' seeds are drawn.

docs/state/plans/ascella-replication-meshes-case.json scores two predictors of the heater_0.3_coupler_0.1_offsets
family of scripts/ascella_fixed_mesh_error.py on meshes that no fit has seen:

- all-meshes: the predictor that carried on the new-seed meshes (new-seed-score.json), copied from
  new-mesh-offsets.json unchanged, the fit on job-00 plus the 56 perturbed meshes of jobs 02 and 03;
- all-served: the same family refitted on job-00, those 56 meshes and the 147 scored meshes of the new-seed jobs 04
  and 05, every perturbed mesh the retained runs hold, so its reading tests whether more training meshes carry more of
  the per-mesh error.

The scored new-seed meshes are those new-seed-score.json scored: perturbed settings whose served mesh no earlier run
served, a mesh served by both new jobs counting once, in job-04. `--check` refits all-served within the fit replay
bounds of ascella_physical_models.replay and requires all-meshes to equal its new-mesh-offsets.json entry.

Usage:
  "$PYTHON" scripts/ascella_replication_offsets.py JOB_00 JOB_02 JOB_03 SPLIT NEW_MESH_OFFSETS JOB_04 JOB_05 OUT
      [--check]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ascella_compilation_reading as reading  # noqa: E402
import ascella_fixed_mesh_confirmation as confirmation  # noqa: E402
import ascella_fixed_mesh_error as fixed  # noqa: E402
import ascella_new_mesh_offsets as earlier  # noqa: E402
import ascella_new_mesh_score as new_score  # noqa: E402
import ascella_physical_models as models  # noqa: E402

from parallel import ordered_map  # noqa: E402

PLAN = "docs/state/plans/ascella-replication-meshes-case.json"
NEW_JOBS = ("job-04", "job-05-i88")


def unseen(data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Each new job's perturbed settings whose mesh no earlier run served, in job order."""
    seen = {key for d in data[:3] for key in new_score.mesh_keys(d)}
    parts = []
    for d in data[3:]:
        keys = new_score.mesh_keys(d)
        anchor = reading.anchors_of(d)
        _, keep = new_score.admitted(keys, sorted({int(c) for c in d["configuration"][~anchor]}), seen)
        seen.update(keys)
        parts.append(reading.subset(d, np.flatnonzero(np.isin(d["configuration"], keep) & ~anchor)))
    return parts


def training(paths: list[Path]) -> dict[str, Any]:
    data = ordered_map(models.job_data, [paths[0], paths[1], paths[2], paths[5], paths[6]])
    jobs = [d["record"]["manifest"]["job"] for d in data]
    models.require(jobs == ["job-00", "job-02", "job-03", *NEW_JOBS], f"the runs are {jobs}")
    split = json.loads(paths[3].read_text(encoding="utf-8"))
    explore, held = fixed.halves(fixed.joined(data[1], data[2]), split)
    train = reading.combined(data[0], reading.combined(explore, held))
    for part in unseen(data):
        train = reading.combined(train, part)
    return train


def freeze(paths: list[Path]) -> dict[str, Any]:
    earlier_record = json.loads(paths[4].read_text(encoding="utf-8"))
    carried = next(entry for entry in earlier_record["predictors"] if entry["name"] == "all-meshes")
    refit = earlier.predictor(("all-served", training(paths)))
    return {
        "schema": "ascella-replication-offsets-v1",
        "plan": PLAN,
        "family": confirmation.FAMILY,
        "runs": [path.relative_to(ROOT).as_posix() for path in (*paths[:3], *paths[5:7])],
        "split": paths[3].relative_to(ROOT).as_posix(),
        "carried_from": paths[4].relative_to(ROOT).as_posix(),
        "predictors": [carried, refit],
    }


def main(argv: list[str]) -> int:
    check = argv[-1:] == ["--check"]
    args = argv[:-1] if check else argv
    if len(args) != 8:
        raise ValueError(f"usage: see the module docstring, not {argv}")
    paths = [Path(arg).resolve() for arg in args]
    record = freeze(paths[:7])
    if check:
        retained = json.loads(paths[7].read_text(encoding="utf-8"))
        models.require(retained["predictors"][0] == record["predictors"][0], "all-meshes differs from its source")
    confirmation.emit(record, paths[7], check)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
