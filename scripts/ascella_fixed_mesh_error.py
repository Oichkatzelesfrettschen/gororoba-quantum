"""Static element offsets of the Ascella mesh, fitted on served meshes and scored on held-out served meshes.

docs/state/plans/ascella-fixed-mesh-error-model.json fixes the families, training set and readings. Job-03 repeats
job-02's settings under the same names and compilation seeds, so `joined` appends job-03's settings to job-02's
configurations by name, and every mesh's X statistic pools both jobs' block counts. The training set is job-00 plus
the exploration meshes of docs/evidence/ascella-order-coefficients/mesh-split.json; the held-out meshes enter only
the power step and, for a family that passes both gates, one held-out reading.

- F1: heater offsets under N(0, 0.3^2) and coupler offsets under N(0, 0.1^2);
- F2: coupler offsets under N(0, 0.1^2).

Each family is the block-conditioned static fit of scripts/ascella_physical_models.py at its posterior mode, with
the posterior Hessian's inverse C as the fit covariance.

- power: every held-out mesh's prediction variance g C g^T against the counting variance of the pooled X statistic
  at the predicted block counts. The held-out settings' sample totals and outside-block counts enter; their block
  split does not. A median ratio above 1 bars the family from reading predicted, so its held-out reading is not run.
- exploration leave-one-out: each exploration mesh leaves the training set with both jobs' copies, the family is
  refitted from zero and predicts that mesh, and a sum of the squared standardized residuals below the chi-square
  0.999 quantile on the mesh count lets the family proceed. The folds share all but one training mesh, so their
  residuals are dependent and the quantile is the plan's fixed threshold, not the sum's calibrated distribution.
- held-out reading: scripts/ascella_compilation_reading.py mesh_score, and the scatter form that adds one free
  constant to every held-out X under a flat prior, r^T (S^-1 - S^-1 1 1^T S^-1 / 1^T S^-1 1) r on one fewer degree
  of freedom, because a mesh-independent deficit belongs to no element offset.
- distance spread: the coefficient of variation of the exploration meshes' pairwise circular phase distances
  sum_h |angle(e^{i (phi_ih - phi_jh)})|. Below MANTEL_SPREAD the meshes are close to equidistant and a
  distance-based screen has no power, so the Mantel screen is not run.

Usage:
  "$PYTHON" scripts/ascella_fixed_mesh_error.py JOB_00 JOB_02 JOB_03 SPLIT OUT [--check]
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
import ascella_physical_models as models  # noqa: E402
import ascella_response_geometry as geometry  # noqa: E402

from parallel import ordered_map  # noqa: E402

# (record name, heater tau, coupler tau); a tau of None leaves that kind out.
FAMILIES: tuple[tuple[str, float | None, float | None], ...] = (
    ("heater_0.3_coupler_0.1_offsets", 0.3, 0.1),
    ("coupler_0.1_offsets", None, 0.1),
)
PROCEED_QUANTILE = 0.999
MANTEL_SPREAD = 0.1


def joined(b: dict[str, Any], c: dict[str, Any]) -> dict[str, Any]:
    """Job-02 with job-03's settings appended to the configurations of the same setting names."""
    settings_b = b["record"]["manifest"]["settings"]
    settings_c = c["record"]["manifest"]["settings"]
    of = {s["name"]: int(k) for s, k in zip(settings_b, b["configuration"], strict=True)}
    models.require(sorted(of) == sorted(s["name"] for s in settings_c), "job-03 does not hold job-02's settings")
    configuration = np.array([of[s["name"]] for s in settings_c])
    for index, k in enumerate(configuration):
        same = np.array_equal(b["phases"][k], c["phases"][int(c["configuration"][index])])
        models.require(same, f"{settings_c[index]['name']}: job-03 served another mesh than job-02")
    record = {**b["record"], "manifest": {**b["record"]["manifest"]}}
    record["manifest"]["settings"] = settings_b + settings_c
    return {
        **b,
        "record": record,
        "configuration": np.concatenate([b["configuration"], configuration]),
        "block": np.concatenate([b["block"], c["block"]]),
        "background": np.concatenate([b["background"], c["background"]]),
    }


def halves(data: dict[str, Any], split: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    seeds = np.array([int(s["compilation_seed"]) for s in data["record"]["manifest"]["settings"]])
    explore = reading.subset(data, np.flatnonzero(np.isin(seeds, split["exploration_seeds"])))
    held = reading.subset(data, np.flatnonzero(np.isin(seeds, split["held_out_seeds"])))
    models.require(
        len(explore["keys"]) == len(split["exploration_seeds"]) and len(held["keys"]) == len(split["held_out_seeds"]),
        "a split seed serves no mesh or shares one",
    )
    return explore, held


def free_widths(data: dict[str, Any], name: str) -> tuple[np.ndarray, np.ndarray]:
    _, heater, coupler = next(f for f in FAMILIES if f[0] == name)
    widths = models.prior_widths(data, heater, coupler)
    free = widths > 0
    return widths[free], free


def fit(item: tuple[str, dict[str, Any]]) -> tuple[np.ndarray, np.ndarray]:
    """A family's posterior mode on the training run and the inverse posterior Hessian."""
    name, train = item
    tau, free = free_widths(train, name)
    offsets, hessian = models.static_mode(train, tau, free)
    return offsets, np.linalg.inv(hessian)


class MeshRows:
    """One held-out mesh's scored readout rows of holdout.left_out_rows, each followed by the counting variance of its
    statistic at the predicted block counts, which no held-out block split enters."""

    def __init__(self, held: dict[str, Any], light: np.ndarray, dlight: np.ndarray) -> None:
        self.held, self.light, self.dlight = held, light, dlight
        total = held["block"].sum(axis=1)
        self.expected = models.setting_probabilities(held, light) * total[:, None]

    def __call__(self, mesh: int) -> list[tuple[Any, ...]]:
        settings = self.held["record"]["manifest"]["settings"]
        out = []
        for row in holdout.left_out_rows(self.held, self.light, self.dlight, mesh):
            chosen = [i for i in np.flatnonzero(self.held["configuration"] == mesh) if settings[i]["readout"] == row[0]]
            out.append((*row, float(geometry.statistic(self.expected[chosen].sum(axis=0), row[0])[1])))
        return out


def mesh_rows(held: dict[str, Any], light: np.ndarray, dlight: np.ndarray) -> list[list[tuple[Any, ...]]]:
    """MeshRows of every held-out mesh, in mesh order."""
    return ordered_map(MeshRows(held, light, dlight), list(range(len(held["keys"]))), min_items=1)


def power(name: str, train: dict[str, Any], held: dict[str, Any], offsets: np.ndarray, covariance: np.ndarray) -> dict:
    """Prediction-to-counting variance ratios over the held-out meshes, the counting variance taken at the
    predicted block counts so no held-out block split enters."""
    _, free = free_widths(train, name)
    light, dlight = models.static_light(held, offsets, free)
    ratios = [float(row[4] @ covariance @ row[4]) / row[5] for rows in mesh_rows(held, light, dlight) for row in rows]
    median = float(np.median(ratios))
    return {
        "median_variance_ratio": median,
        "ratio_range": [float(min(ratios)), float(max(ratios))],
        "may_read_predicted": median <= 1,
    }


def without_mesh(data: dict[str, Any], mesh: int) -> tuple[dict[str, Any], dict[str, Any]]:
    """The run without one configuration's settings, and that configuration alone."""
    inside = data["configuration"] == mesh
    return reading.subset(data, np.flatnonzero(~inside)), reading.subset(data, np.flatnonzero(inside))


def fold(item: tuple[str, dict[str, Any], dict[str, Any], int]) -> dict[str, Any]:
    """Refit without one exploration mesh (both jobs' copies) and predict its pooled X."""
    name, a, explore, mesh = item
    rest, alone = without_mesh(explore, mesh)
    train = reading.combined(a, rest)
    offsets, covariance = fit((name, train))
    _, free = free_widths(train, name)
    light, dlight = models.static_light(alone, offsets, free)
    rows = holdout.left_out_rows(alone, light, dlight, 0)
    models.require(len(rows) == 1 and rows[0][0] == "x", "an exploration mesh serves one X readout")
    _, z, model, variance, gradient = rows[0]
    prediction = float(gradient @ covariance @ gradient)
    return {
        "mesh": list(explore["keys"][mesh]),
        "observed": z,
        "predicted": model,
        "counting_variance": variance,
        "prediction_variance": prediction,
        "standardized_residual": (z - model) / math.sqrt(variance + prediction),
    }


def leave_one_out(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = float(sum(row["standardized_residual"] ** 2 for row in rows))
    threshold = float(stats.chi2.ppf(PROCEED_QUANTILE, len(rows)))
    observed = np.array([row["observed"] for row in rows])
    predicted = np.array([row["predicted"] for row in rows])
    return {
        "meshes": len(rows),
        "sum": total,
        "proceed_threshold": threshold,
        "proceeds": total < threshold,
        "x_correlation": float(np.corrcoef(predicted, observed)[0, 1]),
        "rows": rows,
    }


def scatter_form(score: dict[str, Any], dlight_rows: np.ndarray, covariance: np.ndarray) -> dict[str, Any]:
    """The held-out quadratic form with one free constant on every mesh's X, profiled under a flat prior."""
    rows = score["rows"]
    residual = np.array([row["observed"] - row["predicted"] for row in rows])
    joint = np.diag([row["counting_variance"] for row in rows]) + dlight_rows @ covariance @ dlight_rows.T
    ones = np.ones(len(rows))
    solved_r, solved_1 = np.linalg.solve(joint, residual), np.linalg.solve(joint, ones)
    total = float(residual @ solved_r - (ones @ solved_r) ** 2 / (ones @ solved_1))
    dof = len(rows) - 1
    shortfall = float(stats.chi2.ppf(reading.SHORTFALL_QUANTILE, dof))
    predicted = float(stats.chi2.ppf(reading.PREDICTED_QUANTILE, dof))
    if total >= shortfall:
        verdict = "shortfall"
    elif total < predicted and score["median_variance_ratio"] <= 1:
        verdict = "predicted"
    else:
        verdict = "between the thresholds"
    return {
        "degrees_of_freedom": dof,
        "quadratic_form": total,
        "constant": float((ones @ solved_r) / (ones @ solved_1)),
        "shortfall_threshold": shortfall,
        "predicted_threshold": predicted,
        "reading": verdict,
    }


def held_out_reading(
    name: str, train: dict[str, Any], held: dict[str, Any], offsets: np.ndarray, covariance: np.ndarray
) -> dict[str, Any]:
    _, free = free_widths(train, name)
    light, dlight = models.static_light(held, offsets, free)
    score = reading.mesh_score(name, held, light, dlight, covariance)
    gradients = np.array([row[4] for rows in mesh_rows(held, light, dlight) for row in rows])
    predicted = np.array([row["predicted"] for row in score["rows"]])
    observed = np.array([row["observed"] for row in score["rows"]])
    return {
        "full": score,
        "scatter": scatter_form(score, gradients, covariance),
        "x_correlation": float(np.corrcoef(predicted, observed)[0, 1]),
    }


def distance_spread(explore: dict[str, Any]) -> dict[str, Any]:
    phases = explore["phases"]
    distance = np.abs(np.angle(np.exp(1j * (phases[:, None, :] - phases[None, :, :])))).sum(axis=2)
    pairs = distance[np.triu_indices(len(phases), 1)]
    spread = float(pairs.std() / pairs.mean())
    return {
        "pairs": len(pairs),
        "mean": float(pairs.mean()),
        "sd": float(pairs.std()),
        "range": [float(pairs.min()), float(pairs.max())],
        "coefficient_of_variation": spread,
        "threshold": MANTEL_SPREAD,
        "mantel": (
            "not run: the served meshes are close to equidistant in phase"
            if spread < MANTEL_SPREAD
            else "the plan's Mantel screen applies"
        ),
    }


def build(a_dir: Path, b_dir: Path, c_dir: Path, split_path: Path) -> dict[str, Any]:
    a, b, c = models.job_data(a_dir), models.job_data(b_dir), models.job_data(c_dir)
    jobs = [d["record"]["manifest"]["job"] for d in (a, b, c)]
    models.require(jobs == ["job-00", "job-02", "job-03"], f"the runs are {jobs}, not jobs 00, 02 and 03")
    split = json.loads(split_path.read_text(encoding="utf-8"))
    explore, held = halves(joined(b, c), split)
    train = reading.combined(a, explore)
    names = [name for name, _, _ in FAMILIES]
    fits = ordered_map(fit, [(name, train) for name in names], min_items=1)
    meshes = len(explore["keys"])
    folds = ordered_map(fold, [(name, a, explore, k) for name in names for k in range(meshes)], min_items=1)
    families = []
    for index, name in enumerate(names):
        offsets, covariance = fits[index]
        row: dict[str, Any] = {
            "family": name,
            "parameters": len(offsets),
            "offset_rms": float(math.sqrt(float((offsets * offsets).mean()))),
            "power": power(name, train, held, offsets, covariance),
            "leave_one_out": leave_one_out(folds[index * meshes : (index + 1) * meshes]),
        }
        if not row["power"]["may_read_predicted"]:
            row["held_out"] = "not run: the median held-out variance ratio exceeds 1"
        elif not row["leave_one_out"]["proceeds"]:
            row["held_out"] = "not run: the exploration leave-one-out sum reaches the 0.999 quantile"
        else:
            row["held_out"] = held_out_reading(name, train, held, offsets, covariance)
        families.append(row)
    return {
        "schema": "ascella-fixed-mesh-error-v1",
        "plan": "docs/state/plans/ascella-fixed-mesh-error-model.json",
        "runs": [d.relative_to(ROOT).as_posix() for d in (a_dir, b_dir, c_dir)],
        "split": split_path.relative_to(ROOT).as_posix(),
        "training": "job-00 plus the exploration meshes of jobs 02 and 03",
        "exploration_meshes": meshes,
        "held_out_meshes": len(held["keys"]),
        "distance_spread": distance_spread(explore),
        "families": families,
    }


def main(argv: list[str]) -> int:
    check = argv[-1:] == ["--check"]
    args = argv[:-1] if check else argv
    if len(args) != 5:
        raise ValueError(f"usage: see the module docstring, not {argv}")
    paths = [Path(arg).resolve() for arg in args]
    record = build(*paths[:4])
    out = paths[4]
    text = json.dumps(record, indent=1, sort_keys=True) + "\n"
    if check:
        models.replay(json.loads(text), json.loads(out.read_text(encoding="utf-8")), out.name)
        return 0
    models.require(not out.exists() or out.read_text(encoding="utf-8") == text, f"{out} differs from the recomputed")
    out.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
