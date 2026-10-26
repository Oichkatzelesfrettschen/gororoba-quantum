"""Held-out confirmation of the heater and coupler offsets fitted on Ascella's served meshes.

docs/state/plans/ascella-fixed-mesh-confirmation.json fixes the statistic before scoring. `freeze` fits the
heater_0.3_coupler_0.1_offsets family of scripts/ascella_fixed_mesh_error.py on job-00 plus the exploration meshes
of jobs 02 and 03 and writes every held-out mesh's predicted X statistic with its prediction variance; no held-out
block split enters. `score` recomputes those predictions, requires them to equal the frozen file, and reads:

- the primary statistic, Pearson r between the frozen predictions and the held-out meshes' X statistics pooled over
  jobs 02 and 03, one-sided against r <= 0 by the t distribution on (meshes - 2) degrees of freedom at ALPHA. r is
  invariant under an affine map of the predictions, so the overshoot of the predicted spread and the mesh-independent
  mean deficit leave it unchanged;
- the share of the compilation-induced variance the predictions carry, r^2 against the attenuation ceiling
  s_c^2 / (s_c^2 + mean counting variance), s_c^2 the exploration meshes' observed X variance less their mean
  counting variance, as a point estimate and at the one-sided 1 - ALPHA Fisher-z upper bound of r,
  tanh(atanh(r) + z_(1 - ALPHA) / sqrt(meshes - 3));
- the full and scatter quadratic forms of scripts/ascella_fixed_mesh_error.py, which the plan records as an expected
  shortfall because the predicted spread exceeds the observed one.

Usage:
  "$PYTHON" scripts/ascella_fixed_mesh_confirmation.py freeze JOB_00 JOB_02 JOB_03 SPLIT FROZEN [--check]
  "$PYTHON" scripts/ascella_fixed_mesh_confirmation.py score JOB_00 JOB_02 JOB_03 SPLIT FROZEN ERROR OUT [--check]
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ascella_compilation_reading as reading  # noqa: E402
import ascella_configuration_holdout as holdout  # noqa: E402
import ascella_fixed_mesh_error as fixed  # noqa: E402
import ascella_physical_models as models  # noqa: E402

FAMILY = "heater_0.3_coupler_0.1_offsets"
ALPHA = 0.01


def sets(paths: list[Path]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Training run, exploration meshes and held-out meshes."""
    a, b, c = (models.job_data(path) for path in paths[:3])
    jobs = [d["record"]["manifest"]["job"] for d in (a, b, c)]
    models.require(jobs == ["job-00", "job-02", "job-03"], f"the runs are {jobs}, not jobs 00, 02 and 03")
    split = json.loads(paths[3].read_text(encoding="utf-8"))
    explore, held = fixed.halves(fixed.joined(b, c), split)
    return reading.combined(a, explore), explore, held


def predictions(train: dict[str, Any], held: dict[str, Any]) -> tuple[list[dict[str, Any]], Any]:
    offsets, covariance = fixed.fit((FAMILY, train))
    _, free = fixed.free_widths(train, FAMILY)
    light, dlight = models.static_light(held, offsets, free)
    rows = []
    for k in range(len(held["keys"])):
        entries = holdout.left_out_rows(held, light, dlight, k)
        models.require(len(entries) == 1 and entries[0][0] == "x", "a held-out mesh serves one X readout")
        _, _, model, _, gradient = entries[0]
        rows.append(
            {
                "mesh": list(held["keys"][k]),
                "predicted": model,
                "prediction_variance": float(gradient @ covariance @ gradient),
            }
        )
    return rows, (light, dlight, offsets, covariance)


def freeze(paths: list[Path]) -> dict[str, Any]:
    train, _, held = sets(paths)
    rows, _ = predictions(train, held)
    return {
        "schema": "ascella-fixed-mesh-frozen-predictions-v1",
        "plan": "docs/state/plans/ascella-fixed-mesh-confirmation.json",
        "family": FAMILY,
        "runs": [path.relative_to(ROOT).as_posix() for path in paths[:3]],
        "split": paths[3].relative_to(ROOT).as_posix(),
        "training": "job-00 plus the exploration meshes of jobs 02 and 03",
        "held_out": rows,
    }


def ceiling(error: dict[str, Any]) -> dict[str, float]:
    """Attenuation ceiling of r from the exploration meshes' pooled X statistics of the leave-one-out rows."""
    family = next(row for row in error["families"] if row["family"] == FAMILY)
    rows = family["leave_one_out"]["rows"]
    observed = np.array([row["observed"] for row in rows])
    counting = float(np.mean([row["counting_variance"] for row in rows]))
    compilation = float(observed.var()) - counting
    return {
        "compilation_variance": compilation,
        "mean_counting_variance": counting,
        "r_ceiling": math.sqrt(compilation / (compilation + counting)),
    }


def score(paths: list[Path], frozen: dict[str, Any], error: dict[str, Any]) -> dict[str, Any]:
    train, _, held = sets(paths)
    rows, (light, dlight, _, covariance) = predictions(train, held)
    models.replay(
        json.loads(json.dumps(rows)), frozen["held_out"], "the frozen predictions against the recomputed ones"
    )
    full = reading.mesh_score(FAMILY, held, light, dlight, covariance)
    gradients = np.array([holdout.left_out_rows(held, light, dlight, k)[0][4] for k in range(len(held["keys"]))])
    predicted = np.array([row["predicted"] for row in frozen["held_out"]])
    observed = np.array([row["observed"] for row in full["rows"]])
    meshes = len(predicted)
    r = float(np.corrcoef(predicted, observed)[0, 1])
    dof = meshes - 2
    t = r * math.sqrt(dof / (1 - r * r))
    p = float(stats.t.sf(t, dof))
    bound = ceiling(error)
    upper = math.tanh(math.atanh(r) + float(stats.norm.ppf(1 - ALPHA)) / math.sqrt(meshes - 3))
    slope, intercept = np.polyfit(predicted, observed, 1)
    return {
        "schema": "ascella-fixed-mesh-confirmation-v1",
        "plan": "docs/state/plans/ascella-fixed-mesh-confirmation.json",
        "family": FAMILY,
        "meshes": meshes,
        "primary": {
            "pearson_r": r,
            "t": t,
            "degrees_of_freedom": dof,
            "p_one_sided": p,
            "alpha": ALPHA,
            "reading": "carried" if p < ALPHA else "not carried",
        },
        "explained_share": {
            **bound,
            "r_squared": r * r,
            "share_of_ceiling": r * r / bound["r_ceiling"] ** 2,
            "r_upper": upper,
            "share_of_ceiling_upper": upper * upper / bound["r_ceiling"] ** 2,
        },
        "spearman": float(stats.spearmanr(predicted, observed).statistic),
        "affine": {"slope": float(slope), "intercept": float(intercept)},
        "spread": {"predicted_sd": float(predicted.std()), "observed_sd": float(observed.std())},
        "quadratic_forms": {
            "full": {key: full[key] for key in ("quadratic_form", "median_variance_ratio", "reading")},
            "scatter": fixed.scatter_form(full, gradients, covariance),
        },
        "rows": [
            {**row, "observed": float(z), "counting_variance": float(full_row["counting_variance"])}
            for row, z, full_row in zip(frozen["held_out"], observed, full["rows"], strict=True)
        ],
    }


def emit(record: dict[str, Any], out: Path, check: bool) -> None:
    text = json.dumps(record, indent=1, sort_keys=True) + "\n"
    if check:
        models.replay(json.loads(text), json.loads(out.read_text(encoding="utf-8")), out.name)
        return
    models.require(not out.exists() or out.read_text(encoding="utf-8") == text, f"{out} differs from the recomputed")
    out.write_text(text, encoding="utf-8")


def main(argv: list[str]) -> int:
    check = argv[-1:] == ["--check"]
    args = argv[:-1] if check else argv
    if args[:1] == ["freeze"] and len(args) == 6:
        paths = [Path(arg).resolve() for arg in args[1:]]
        emit(freeze(paths[:4]), paths[4], check)
        return 0
    if args[:1] == ["score"] and len(args) == 8:
        paths = [Path(arg).resolve() for arg in args[1:]]
        frozen = json.loads(paths[4].read_text(encoding="utf-8"))
        error = json.loads(paths[5].read_text(encoding="utf-8"))
        emit(score(paths[:4], frozen, error), paths[6], check)
        return 0
    raise ValueError(f"usage: see the module docstring, not {argv}")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
