"""Source and detector families of the Ascella twelve-output likelihood, scored on job-02's exploration meshes.

docs/state/plans/ascella-mesh-response-decomposition.json fixes the protocol: each family is fitted on job-00 alone
and scored on the exploration half of job-02's perturbed meshes (scripts/ascella_mesh_decomposition.py split) by
the quadratic form of scripts/ascella_twelve_output.py. The families act on each output's intensity after the mesh
(ascella_twelve_output.Family):

- detector_efficiency: eleven relative log-efficiencies, a per-mode transmittance being the same parameter;
- platform_g2: photon bunching at the gamma that Perceval's NoiseModel gives for the g2 of job-00's platform record
  at plan (`perfs_at_plan`), no free parameter;
- efficiency_and_platform_g2: both;
- efficiency_and_free_bunching: the efficiencies with gamma free.

Every served mesh of job-02 realizes the same target column from input mode 0, so these families predict the same
light on every mesh: only the background weight, profiled per iteration, moves their block fractions. They answer
the mesh-independent part of job-02's response, the exploration-mean X deficit, and cannot carry its spread. The
record states both limits as numbers:

- mean: the exploration-mean observed X less the family's, in standard errors of the observed mean (the sample
  standard deviation over meshes over the square root of their count); below the two-sided 0.01 normal quantile
  it reads "mean reproduced", otherwise "mean missed";
- floor: the counting-covariance quadratic form of the observed block fractions against one constant fraction
  vector, minimized over that vector; at or above the shortfall threshold no model with constant block fractions
  can be kept, whatever its mean. These families' fractions move only through the per-iteration background
  weight, so the floor bounds them up to that motion.

Usage:
  "$PYTHON" scripts/ascella_source_detector.py JOB_00 JOB_02 SPLIT OUT [--check]
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats
from scipy.optimize import minimize

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ascella_physical_models as models  # noqa: E402
import ascella_twelve_output as twelve  # noqa: E402

from parallel import ordered_map  # noqa: E402

MEAN_QUANTILE = 0.995


def families(g2: float) -> dict[str, twelve.Family]:
    gamma = twelve.bunching_weight(g2)
    return {
        "nominal": twelve.FAMILIES["nominal"],
        "detector_efficiency": twelve.Family(efficiency=True),
        "platform_g2": twelve.Family(bunching=gamma),
        "efficiency_and_platform_g2": twelve.Family(efficiency=True, bunching=gamma),
        "efficiency_and_free_bunching": twelve.Family(efficiency=True, bunching="free"),
    }


def observed_fractions(data: dict[str, Any]) -> np.ndarray:
    counts = data["record"]["counts"][:, : models.LOGICAL]
    out: np.ndarray = counts / counts.sum(axis=1, keepdims=True)
    return out


def constant_form(fractions: np.ndarray, observed: np.ndarray, totals: np.ndarray) -> float:
    """sum_i N_i r_i^T S^-1 r_i over the block coordinates, r_i = o_i - p and S = diag(p) - p p^T, for one constant
    block-fraction vector p (coordinates 0, 1 and 2; mode 3 takes the rest)."""
    residual = observed - fractions[None, :]
    scatter = (totals[:, None, None] * residual[:, :, None] * residual[:, None, :]).sum(axis=0)
    covariance = np.diag(fractions) - np.outer(fractions, fractions)
    return float(np.trace(np.linalg.solve(covariance, scatter)))


def floor(data: dict[str, Any]) -> dict[str, Any]:
    """The counting-covariance quadratic form of the observed block fractions against one constant fraction vector,
    at the exploration mean and minimized over the vector: no model whose block fractions stay constant over the
    meshes scores below the minimum."""
    counts = data["record"]["counts"][:, : models.LOGICAL]
    totals = counts.sum(axis=1)
    coordinates = list(twelve.COORDINATES)
    observed = (counts / totals[:, None])[:, coordinates]
    mean = observed.mean(axis=0)

    def objective(fractions: np.ndarray) -> float:
        if fractions.min() <= 0 or fractions.sum() >= 1:
            return math.inf
        return constant_form(fractions, observed, totals)

    result = minimize(objective, mean, method="Nelder-Mead", options={"xatol": 1e-12, "fatol": 1e-9, "maxiter": 20000})
    models.require(bool(result.success), f"the constant-fraction floor did not converge: {result.message}")
    dof = len(coordinates) * len(observed)
    threshold = float(stats.chi2.ppf(twelve.SHORTFALL_QUANTILE, dof))
    return {
        "at_exploration_mean": constant_form(mean, observed, totals),
        "minimized": float(result.fun),
        "minimizing_fractions": [float(value) for value in result.x],
        "coordinates": dof,
        "shortfall_threshold": threshold,
        "any_constant_fraction_model_kept": float(result.fun) < threshold,
    }


def mean_reading(row: dict[str, Any], observed_x: np.ndarray) -> dict[str, Any]:
    error = float(observed_x.std(ddof=1)) / math.sqrt(len(observed_x))
    z = (row["exploration"]["x_observed_mean"] - row["exploration"]["x_model_mean"]) / error
    critical = float(stats.norm.ppf(MEAN_QUANTILE))
    return {
        "standard_error": error,
        "z": z,
        "critical": critical,
        "reading": ("mean reproduced" if abs(z) < critical else "mean missed"),
    }


def build(a_dir: Path, c_dir: Path, split_path: Path) -> dict[str, Any]:
    a, explore = twelve.runs(a_dir, c_dir, split_path)
    g2_percent = float(json.loads((a_dir / "submission.json").read_text(encoding="utf-8"))["perfs_at_plan"]["g2 (%)"])
    specs = families(g2_percent / 100)
    train_unitary, test_unitary = twelve.unitaries(a), twelve.unitaries(explore)
    rows = ordered_map(
        twelve.fit,
        [(name, a, explore, train_unitary, test_unitary, spec) for name, spec in specs.items()],
        min_items=1,
    )
    observed = observed_fractions(explore)
    observed_x = observed[:, 0] - observed[:, 3]
    nominal = rows[0]["job_00_negative_log_posterior"]
    for row in rows:
        row["job_00_gain_over_nominal"] = nominal - row["job_00_negative_log_posterior"]
        row["mean"] = mean_reading(row, observed_x)
    return {
        "schema": "ascella-source-detector-v1",
        "plan": "docs/state/plans/ascella-mesh-response-decomposition.json",
        "runs": [a_dir.relative_to(ROOT).as_posix(), c_dir.relative_to(ROOT).as_posix()],
        "split": split_path.relative_to(ROOT).as_posix(),
        "exploration_meshes": len(explore["keys"]),
        "g2_at_plan": g2_percent / 100,
        "bunching_gamma": specs["platform_g2"].bunching,
        "efficiency_width": twelve.EFFICIENCY_WIDTH,
        "bunching_width": twelve.BUNCHING_WIDTH,
        "observed_x_sd": float(observed_x.std(ddof=1)),
        "floor": floor(explore),
        "families": rows,
        "kept": [row["family"] for row in rows if row["exploration"]["reading"] == "kept"],
        "mean_reproduced": [row["family"] for row in rows if row["mean"]["reading"] == "mean reproduced"],
    }


def main(argv: list[str]) -> int:
    check = argv[-1:] == ["--check"]
    args = argv[:-1] if check else argv
    if len(args) != 4:
        raise ValueError(f"usage: see the module docstring, not {argv}")
    record = build(Path(args[0]).resolve(), Path(args[1]).resolve(), Path(args[2]).resolve())
    out = Path(args[3]).resolve()
    text = json.dumps(record, indent=1, sort_keys=True) + "\n"
    if check:
        models.replay(json.loads(text), json.loads(out.read_text(encoding="utf-8")), out.name)
        return 0
    models.require(not out.exists() or out.read_text(encoding="utf-8") == text, f"{out} differs from the recomputed")
    out.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
