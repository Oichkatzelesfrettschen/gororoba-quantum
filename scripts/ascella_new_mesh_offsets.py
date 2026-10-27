"""Frozen element offsets for Ascella's new-seed meshes, fixed before those meshes are served.

docs/state/plans/ascella-new-seed-meshes-case.json scores two predictors of the heater_0.3_coupler_0.1_offsets
family of scripts/ascella_fixed_mesh_error.py on meshes that no fit has seen. The served mesh is known only from
the returned computed_circuit, so the plan freezes each predictor's offsets rather than its predictions, and a
predicted X statistic is static_light of the returned phases and couplers under those offsets.

- exploration: the fit on job-00 plus the 28 exploration meshes of mesh-split.json, the fit whose held-out
  predictions plan ascella-fixed-mesh-confirmation froze;
- all-meshes: the fit on job-00 plus all 56 perturbed meshes of jobs 02 and 03, each pooled over both jobs by
  setting name.

Each entry carries the free-parameter mask and the posterior-mode offsets, the only fit outputs a prediction uses;
`--check` refits both and requires every offset within the fit replay bounds of ascella_physical_models.replay.

Usage:
  "$PYTHON" scripts/ascella_new_mesh_offsets.py JOB_00 JOB_02 JOB_03 SPLIT OUT [--check]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ascella_compilation_reading as reading  # noqa: E402
import ascella_fixed_mesh_confirmation as confirmation  # noqa: E402
import ascella_fixed_mesh_error as fixed  # noqa: E402
import ascella_physical_models as models  # noqa: E402

from parallel import ordered_map  # noqa: E402

PLAN = "docs/state/plans/ascella-new-seed-meshes-case.json"


def training_sets(paths: list[Path]) -> list[tuple[str, dict[str, Any]]]:
    a, b, c = (models.job_data(path) for path in paths[:3])
    jobs = [d["record"]["manifest"]["job"] for d in (a, b, c)]
    models.require(jobs == ["job-00", "job-02", "job-03"], f"the runs are {jobs}, not jobs 00, 02 and 03")
    split = json.loads(paths[3].read_text(encoding="utf-8"))
    explore, held = fixed.halves(fixed.joined(b, c), split)
    meshes = reading.combined(explore, held)
    return [("exploration", reading.combined(a, explore)), ("all-meshes", reading.combined(a, meshes))]


def predictor(item: tuple[str, dict[str, Any]]) -> dict[str, Any]:
    name, train = item
    offsets, _ = fixed.fit((confirmation.FAMILY, train))
    _, free = fixed.free_widths(train, confirmation.FAMILY)
    return {
        "name": name,
        "meshes": len(train["keys"]),
        "free": [bool(f) for f in free],
        "offsets": [float(x) for x in offsets],
    }


def freeze(paths: list[Path]) -> dict[str, Any]:
    return {
        "schema": "ascella-new-mesh-offsets-v1",
        "plan": PLAN,
        "family": confirmation.FAMILY,
        "runs": [path.relative_to(ROOT).as_posix() for path in paths[:3]],
        "split": paths[3].relative_to(ROOT).as_posix(),
        "predictors": ordered_map(predictor, training_sets(paths), min_items=1),
    }


def main(argv: list[str]) -> int:
    check = argv[-1:] == ["--check"]
    args = argv[:-1] if check else argv
    if len(args) != 5:
        raise ValueError(f"usage: see the module docstring, not {argv}")
    paths = [Path(arg).resolve() for arg in args]
    confirmation.emit(freeze(paths[:4]), paths[4], check)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
