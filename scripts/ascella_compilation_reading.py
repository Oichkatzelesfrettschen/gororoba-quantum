"""The preregistered reading of the Ascella perturbed-compilation run (job-02).

docs/state/plans/ascella-perturbed-compilation-case.json fixes the readings before the acquisition, and
docs/design/ascella-signed-coherence-conformance.md#perturbed-compilation-case-job-02 states them:

- R1, compilation dependence: per iteration the block-conditioned X statistic z with its multinomial variance v;
  the statistic is the ratio of the perturbed iterations' dispersion sum (z - zbar)^2 / v per degree of freedom to
  the anchors' (seed 0, job-00's mesh), and its p-value the share of PERMUTATIONS relabelings of the 64 iterations
  into 56 and 8 whose ratio reaches the observed one. The relabelings draw from a numpy generator seeded with value
  PERMUTATION_INDEX of the seed draw the run's cases.json names, the first value the request leaves unused;
- R2, prediction: each family of scripts/ascella_compilation_design.py fitted on job-00 predicts every distinct
  perturbed mesh's pooled statistic in counting plus fitted-prediction variance. All meshes share the job-00
  coefficients, so the residuals r carry the covariance diag(v) + G C G^T, G the statistic gradients and C the
  fit covariance; r^T (diag(v) + G C G^T)^{-1} r keeps the shortfall at or above the chi-square 0.999 quantile on
  the mesh count and predicts below its 0.97 quantile with median prediction-to-counting variance ratio at most
  1. The sum of individually standardized squares, which drops the cross-mesh terms, stays as a description;
- R3, identification: each family refitted from the zero start on job-00 plus the perturbed iterations, without
  each of the 19 scored job-00 configurations in turn, scores that configuration as the training-only folds of
  scripts/ascella_configuration_holdout.py do, under the reading of scripts/ascella_drive_response.py. The anchors
  repeat configuration 13's mesh and stay out of R3, so a fold on configuration 13 trains without it.

The served meshes come from each iteration's computed_circuit; iterations that return one mesh form one
configuration, and the record states how many distinct new meshes the 56 seeds realized. R2 and R3 read only
those (new_meshes): a seed that repeats an anchor's or a job-00 configuration's mesh adds no compilation. A
run whose nonzero seeds served no new mesh reads as "seed ignored" and R1 to R3 decide nothing; one new mesh is
a collapsed compilation that the readings still compare with the anchors.

Usage:
  "$PYTHON" scripts/ascella_compilation_reading.py JOB_00 JOB_02 OUT [--check]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ascella_compilation_design as design  # noqa: E402
import ascella_configuration_holdout as holdout  # noqa: E402
import ascella_drive_response as drive  # noqa: E402
import ascella_physical_models as models  # noqa: E402
import ascella_response_geometry as geometry  # noqa: E402

from parallel import ordered_map  # noqa: E402

ALPHA = 0.01
PERMUTATIONS = 20000
# The request consumes values 0..55 of its seed draw; value 56 seeds the R1 relabelings.
PERMUTATION_INDEX = 56
SHORTFALL_QUANTILE = 0.999
PREDICTED_QUANTILE = 0.97


def anchors_of(data: dict[str, Any]) -> np.ndarray:
    """Per setting, whether the request ran it at compilation seed 0."""
    return np.array([setting["compilation_seed"] == 0 for setting in data["record"]["manifest"]["settings"]])


def x_statistics(data: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    return geometry.statistic(data["block"], "x")


def dispersion_ratio(z: np.ndarray, v: np.ndarray, anchor: np.ndarray) -> np.ndarray:
    """Rows of labelings (permutations x iterations, True for an anchor) to the perturbed-over-anchor ratio."""
    weight = 1 / v

    def dispersion(mask: np.ndarray) -> np.ndarray:
        w = weight[None, :] * mask
        centre = (w * z[None, :]).sum(axis=1) / w.sum(axis=1)
        return (w * (z[None, :] - centre[:, None]) ** 2).sum(axis=1) / (mask.sum(axis=1) - 1)

    return dispersion(~anchor) / dispersion(anchor)


def r1(data: dict[str, Any]) -> dict[str, Any]:
    anchor = anchors_of(data)
    z, v = x_statistics(data)
    observed = float(dispersion_ratio(z, v, anchor[None, :])[0])
    draw = data["record"]["manifest"]["compilation_seeds"]["draw"]
    values = json.loads((ROOT / draw).read_text(encoding="utf-8"))["values"]
    generator = np.random.default_rng(int(values[PERMUTATION_INDEX]))
    labels = np.zeros((PERMUTATIONS, len(z)), dtype=bool)
    order = generator.permuted(np.tile(np.arange(len(z)), (PERMUTATIONS, 1)), axis=1)
    np.put_along_axis(labels, order[:, : int(anchor.sum())], True, axis=1)
    ratios = dispersion_ratio(z, v, labels)
    p = float((1 + (ratios >= observed).sum()) / (1 + PERMUTATIONS))
    return {
        "statistic": "perturbed over anchor dispersion of the X statistic per degree of freedom",
        "ratio": observed,
        "p": p,
        "permutations": PERMUTATIONS,
        "seed_draw": draw,
        "seed_index": PERMUTATION_INDEX,
        "reading": "compilation dependent" if p < ALPHA else "no compilation dependence detected",
        "perturbed_mean": float((z[~anchor] / v[~anchor]).sum() / (1 / v[~anchor]).sum()),
        "anchor_mean": float((z[anchor] / v[anchor]).sum() / (1 / v[anchor]).sum()),
        "perturbed_range": [float(z[~anchor].min()), float(z[~anchor].max())],
    }


def new_meshes(a: dict[str, Any], c: dict[str, Any], anchor: np.ndarray) -> set[int]:
    """job-02 configurations a nonzero seed served that neither an anchor nor any job-00 configuration shares.

    A seed that repeats an anchor's or a job-00 configuration's mesh adds no compilation, and in R3 it would put a
    held-out job-00 configuration's mesh back into its own training set under another configuration index."""
    anchor_meshes = {int(m) for m in c["configuration"][anchor]}
    return {
        m
        for m in {int(m) for m in c["configuration"][~anchor]} - anchor_meshes
        if not any(np.array_equal(c["phases"][m], phases) for phases in a["phases"])
    }


def served_reading(count: int) -> str:
    """What the nonzero seeds did to the compilation, from the number of new meshes they served."""
    if count == 0:
        return "seed ignored"
    return "seeds served one new mesh" if count == 1 else "seeds served distinct meshes"


def with_family_basis(data: dict[str, Any], kind: str | None, order: int) -> dict[str, Any]:
    b = design.basis(data["phases"], kind, order)
    return data if b is None else {**data, "heater_basis": b}


def subset(data: dict[str, Any], settings: np.ndarray) -> dict[str, Any]:
    """The listed settings of a run, its configurations renumbered in first-appearance order."""
    kept = sorted({int(c) for c in data["configuration"][settings]})
    renumber = {old: new for new, old in enumerate(kept)}
    record = {**data["record"], "manifest": {**data["record"]["manifest"]}}
    record["manifest"]["settings"] = [data["record"]["manifest"]["settings"][i] for i in settings]
    return {
        **data,
        "record": record,
        "keys": [data["keys"][c] for c in kept],
        "phases": data["phases"][kept],
        "sources": data["sources"][kept],
        "configuration": np.array([renumber[int(c)] for c in data["configuration"][settings]]),
        "block": data["block"][settings],
        "background": data["background"][settings],
    }


def combined(a: dict[str, Any], c: dict[str, Any]) -> dict[str, Any]:
    """job-00 followed by job-02's perturbed settings as further configurations."""
    record = {**a["record"], "manifest": {**a["record"]["manifest"]}}
    record["manifest"]["settings"] = a["record"]["manifest"]["settings"] + c["record"]["manifest"]["settings"]
    return {
        **a,
        "record": record,
        "keys": a["keys"] + c["keys"],
        "phases": np.concatenate([a["phases"], c["phases"]]),
        "sources": np.concatenate([a["sources"], c["sources"]]),
        "configuration": np.concatenate([a["configuration"], c["configuration"] + len(a["keys"])]),
        "block": np.concatenate([a["block"], c["block"]]),
        "background": np.concatenate([a["background"], c["background"]]),
    }


def r2(item: tuple[dict[str, Any], dict[str, Any], dict[str, Any]]) -> dict[str, Any]:
    planted, a, perturbed = item
    _, kind, order, _ = next(f for f in design.FAMILIES if f[0] == planted["family"])
    data = with_family_basis(perturbed, kind, order)
    covariance = np.linalg.inv(planted["hessian"])
    light, dlight = models.static_light(data, planted["offsets"], planted["free"])
    rows = []
    gradients = []
    for k in range(len(data["keys"])):
        for readout, z, model, variance, gradient in holdout.left_out_rows(data, light, dlight, k):
            gradients.append(gradient)
            prediction = float(gradient @ covariance @ gradient)
            rows.append(
                {
                    "readout": readout,
                    "observed": z,
                    "predicted": model,
                    "counting_variance": variance,
                    "prediction_variance": prediction,
                    "standardized_residual": (z - model) / (variance + prediction) ** 0.5,
                }
            )
    diagonal = sum(row["standardized_residual"] ** 2 for row in rows)
    residual = np.array([row["observed"] - row["predicted"] for row in rows])
    g = np.array(gradients)
    joint = np.diag([row["counting_variance"] for row in rows]) + g @ covariance @ g.T
    total = float(residual @ np.linalg.solve(joint, residual))
    ratio = float(np.median([row["prediction_variance"] / row["counting_variance"] for row in rows]))
    meshes = len(rows)
    shortfall = float(stats.chi2.ppf(SHORTFALL_QUANTILE, meshes))
    predicted = float(stats.chi2.ppf(PREDICTED_QUANTILE, meshes))
    if total >= shortfall:
        reading = "shortfall"
    elif total < predicted and ratio <= 1:
        reading = "predicted"
    else:
        reading = "between the thresholds"
    return {
        "family": planted["family"],
        "meshes": meshes,
        "quadratic_form": total,
        "diagonal_sum": diagonal,
        "median_variance_ratio": ratio,
        "shortfall_threshold": shortfall,
        "predicted_threshold": predicted,
        "reading": reading,
        "rows": rows,
    }


def r3_fold(item: tuple[str, str | None, int, Any, dict[str, Any], int]) -> dict[str, Any]:
    name, kind, order, tau, data, left_out = item
    return holdout.configuration_fold((name, (tau, None), with_family_basis(data, kind, order), left_out))


def build(a_dir: Path, c_dir: Path) -> dict[str, Any]:
    a, c = models.job_data(a_dir), models.job_data(c_dir)
    models.require(a["record"]["manifest"]["job"] == "job-00", "the fit run is not job-00")
    models.require(c["record"]["manifest"]["job"] == "job-02", "the reading run is not job-02")
    layout = [(kind, mode) for kind, mode, _ in a["arch"]] == [(kind, mode) for kind, mode, _ in c["arch"]]
    models.require(layout and np.array_equal(a["couplers"], c["couplers"]), "the mesh layouts or couplers differ")
    anchor = anchors_of(c)
    anchor_meshes = {int(m) for m in c["configuration"][anchor]}
    perturbed_meshes = new_meshes(a, c, anchor)
    k = next(i for i, key in enumerate(a["keys"]) if design.SETTING in key)
    anchor_phases = c["phases"][sorted(anchor_meshes)]
    anchor_matches = bool(len(anchor_meshes) == 1 and np.array_equal(anchor_phases[0], a["phases"][k]))
    distance = np.abs(np.angle(np.exp(1j * (c["phases"][sorted(perturbed_meshes)] - a["phases"][k][None, :]))))
    record: dict[str, Any] = {
        "schema": "ascella-perturbed-compilation-reading-v1",
        "runs": [a_dir.relative_to(ROOT).as_posix(), c_dir.relative_to(ROOT).as_posix()],
        "setting": design.SETTING,
        "meshes": {
            "anchor_meshes": len(anchor_meshes),
            "anchor_equals_job_00": anchor_matches,
            "distinct_perturbed": len(perturbed_meshes),
            "perturbed_iterations": int((~anchor).sum()),
            "median_heater_distance": float(np.median(distance)) if len(perturbed_meshes) else 0.0,
        },
        "alpha": ALPHA,
    }
    record["reading"] = served_reading(len(perturbed_meshes))
    if not perturbed_meshes:
        return record
    record["r1"] = r1(c)
    planted = ordered_map(design.fit, [(*family, a) for family in design.FAMILIES], min_items=1)
    perturbed = subset(c, np.flatnonzero([int(m) in perturbed_meshes for m in c["configuration"]]))
    record["r2"] = ordered_map(r2, [(p, a, perturbed) for p in planted], min_items=1)
    both = combined(a, perturbed)
    scored = models.scored_configurations(a)
    folds = ordered_map(r3_fold, [(*family, both, j) for family in design.FAMILIES for j in scored], min_items=1)
    rows = []
    for index, family in enumerate(design.FAMILIES):
        chosen = folds[index * len(scored) : (index + 1) * len(scored)]
        summary = holdout.summarize([entry for fold in chosen for entry in fold["rows"]])
        rows.append({"family": family[0], "folds": chosen, "summary": summary, "reading": drive.reading(summary)})
    record["r3"] = rows
    return record


def main(argv: list[str]) -> int:
    check = argv[-1:] == ["--check"]
    args = argv[:-1] if check else argv
    if len(args) != 3:
        raise ValueError(f"usage: see the module docstring, not {argv}")
    record = build(Path(args[0]).resolve(), Path(args[1]).resolve())
    out = Path(args[2]).resolve()
    text = json.dumps(record, indent=1, sort_keys=True) + "\n"
    if check:
        models.replay(json.loads(text), json.loads(out.read_text(encoding="utf-8")), out.name)
        return 0
    models.require(not out.exists() or out.read_text(encoding="utf-8") == text, f"{out} differs from the recomputed")
    out.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
