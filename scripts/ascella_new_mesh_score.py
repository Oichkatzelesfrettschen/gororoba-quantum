"""The preregistered score of Ascella's new-seed meshes against the frozen element offsets.

docs/state/plans/ascella-new-seed-meshes-case.json fixes this contract before acquisition, and the offsets come from
docs/evidence/ascella-order-coefficients/new-mesh-offsets.json (scripts/ascella_new_mesh_offsets.py).

- Mesh identity: a served mesh is its returned computed_circuit with its computed_input, the key of
  ascella_response_geometry.configurations. Settings at compilation seed 0 (the anchors) never enter the primary. A
  perturbed mesh equal to any mesh served by the reference runs (jobs 00, 02 and 03) is excluded, and a mesh served by
  two new jobs counts once, in the earlier job of the argument order. Settings that serve one mesh within a job pool
  their block counts. A job left with fewer than MIN_JOB_MESHES meshes leaves the primary; its meshes count nowhere.
  A run whose results.json lacks counts for any manifest setting, holds a setting with no count in the logical block
  (modes 0 to 3, where the X statistic is undefined), or whose status is not completed, is partial: it stays
  descriptive and enters no primary. ascella_coherence_repeat.attributed_rows refuses an entry whose echoed
  compilation_seed differs from its setting's.
- Acquisition set (enforced by `main`): the references are exactly jobs 00, 02 and 03; each new run's cases.json
  equals its frozen case bytes under results/quandela/cases/ascella_signed_coherence/; the new runs are job-04 alone
  when the job-05 rule admits none, and otherwise job-04 followed by exactly the admitted job-05 variant. A partial
  job-04 reads "not read". A submitted but partial job-05 stays descriptive and the primary reads job-04 alone.
- Job-05 iteration rule: job-04 runs 80 iterations; with its provider-reported status.duration d4 at most
  DURATION_TARGET seconds, job-05 runs 8 floor(min(96, DURATION_TARGET * 80 / d4) / 8) iterations, and a partial
  job-04 or a d4 above DURATION_TARGET admits no job-05. The rule reads completion and duration alone, never an X
  count, and the score refuses a job-05 run of another variant.
- Per mesh: the observed block-conditioned X statistic and its multinomial variance, and each predictor's X from
  static_light of the returned mesh under its frozen offsets (ascella_fixed_mesh_error.mesh_rows).
- Primary, per predictor: Pearson r of predicted with observed X after centering both within each job, one-sided
  against r <= 0 by the t distribution on n - 1 - J degrees of freedom (n meshes, J jobs), carried at p below
  ALPHA_EACH, the Bonferroni share of ALPHA over the two predictors. Not read when n - J - 2 < 1, a centered variable
  is constant, or any input is not finite. r is clamped to [-1, 1]; at an endpoint t is unbounded (recorded as null),
  p is 0 or 1 and both Fisher bounds equal r.
- Bounds and share: the one-sided 1 - ALPHA_EACH Fisher-z bounds tanh(atanh(r) -+ z / sqrt(n - J - 2)), the
  centering counting as J - 1 partialled job indicators. The positive-direction share is r^2 / c^2 with the plug-in
  attenuation ceiling
  c^2 = s_c^2 / (s_c^2 + mean counting variance of the scored meshes), s_c^2 the compilation variance of
  fixed-mesh-confirmation.json, conditional on that retained estimate; a negative bound maps to share 0 and a share
  above 1 clips to 1. A negative correlation carries no positive-direction share; the outcome names it apart.
- Anchor control, per job: the inverse-variance anchor mean X less job-03's, the calibration the predictors were fitted
  under, with its two-sided ANCHOR_LEVEL normal interval from both means' variances. The job reads "steady" when the
  whole interval lies within +-s_c, the compilation-induced X standard deviation, and "moved" otherwise: a gross
  calibration event, against which job-03 reproduced every per-mesh error at the attenuation ceiling across a
  recalibration that moved the anchors by 0.00285 (seed-repeat-reading.json). Requiring every scored job's interval
  to pass is conservative across jobs without a multiplicity adjustment. The control gates only the bounded outcome,
  because centering removes an additive shift and a calibration change between jobs cannot correlate frozen
  predictions with unseen meshes.
- Outcome, one of seven disjoint branches, in this order: "not read" when a predictor is not read; "both carried",
  "P-A carried only", "P-B carried only"; with neither carried, "inconclusive: anticorrelated" when a predictor's
  upper Fisher bound of r lies below 0 (the offsets then predict the sign-reversed error, which no positive-direction
  share describes), "inconclusive: anchors moved" when a scored job's anchors moved, "bounded" when both upper shares
  lie below the held-out point estimate of fixed-mesh-confirmation.json, and "inconclusive" otherwise.
- Secondary, descriptive: Spearman correlation of the centered values, the affine slope of observed on predicted,
  each job's perturbed-over-anchor dispersion ratio. Exploratory: P-A's centered correlation over the new meshes and
  the 28 spent held-out meshes of fixed-mesh-confirmation.json, those 28 forming one more job.

Usage:
  "$PYTHON" scripts/ascella_new_mesh_score.py OFFSETS CONFIRMATION REFERENCE_RUNS... -- NEW_RUNS... OUT [--check]
"""

from __future__ import annotations

import hashlib
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

import ascella_coherence_repeat as repeat  # noqa: E402
import ascella_compilation_reading as reading  # noqa: E402
import ascella_fixed_mesh_error as fixed  # noqa: E402
import ascella_physical_models as models  # noqa: E402
import ascella_response_geometry as geometry  # noqa: E402

from parallel import ordered_map  # noqa: E402

ALPHA = 0.01
ALPHA_EACH = ALPHA / 2
MIN_JOB_MESHES = 3
PREDICTORS = ("exploration", "all-meshes")
LABELS = {"exploration": "P-A", "all-meshes": "P-B"}
# The reference run whose anchors set the calibration baseline: the last acquisition before the new-seed jobs.
BASELINE_JOB = "job-03"
# The seconds job-05 may plan at job-04's realized seconds per iteration: 21 s below the 300 s max_duration, the
# margin of 96 iterations at the 64-iteration bound of 2.90625 s each.
DURATION_TARGET = 279.0
FIRST_ITERATIONS = 80
ANCHOR_LEVEL = 0.99
REFERENCE_JOBS = ("job-00", "job-02", "job-03")
CASES = ROOT / "results/quandela/cases/ascella_signed_coherence"


def mesh_keys(data: dict[str, Any]) -> list[str]:
    return list(geometry.configurations(data["record"]).keys())


def job_05_iterations(first: dict[str, Any]) -> int | None:
    """The job-05 iteration count job-04's summary admits, or None when it admits no job-05."""
    duration = first["duration"]
    if not first["complete"] or not isinstance(duration, int | float) or not 0 < duration <= DURATION_TARGET:
        return None
    return 8 * math.floor(min(96.0, DURATION_TARGET * FIRST_ITERATIONS / duration) / 8)


def returned(path: Path) -> dict[str, Any]:
    """Job name, manifest iteration count, provider status and duration, and whether every setting carries counts."""
    manifest = json.loads((path / "cases.json").read_text(encoding="utf-8"))
    results = json.loads((path / "results.json").read_text(encoding="utf-8"))
    status = results.get("status") or {}
    rows = repeat.attributed_rows(manifest, results)
    empty = sum(row is not None and sum(row[:4]) <= 0 for row in rows)
    return {
        "job": manifest["job"],
        "run": path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.name,
        "cases_sha256": hashlib.sha256((path / "cases.json").read_bytes()).hexdigest(),
        "requested_iterations": manifest["iterations"],
        "returned_iterations": sum(row is not None for row in rows),
        "empty_logical_block": empty,
        "status": status.get("status"),
        "duration": status.get("duration"),
        "complete": status.get("status") == "completed" and all(row is not None for row in rows) and not empty,
    }


def acquisition(summaries: list[dict[str, Any]], frozen: dict[str, str]) -> None:
    """Refuse a new-run set other than the frozen acquisition: frozen case bytes, job-04 first, and the job-05 variant
    the duration rule admits exactly when it admits one. frozen maps a job name to its frozen cases.json digest."""
    names = [summary["job"] for summary in summaries]
    models.require(len(set(names)) == len(names), f"the new runs repeat a job: {names}")
    for summary in summaries:
        expected = frozen.get(summary["job"])
        models.require(expected == summary["cases_sha256"], f"{summary['job']}: cases.json is not the frozen case")
    models.require(names[:1] == ["job-04"], f"the new runs start {names[:1]}, not job-04")
    allowed = job_05_iterations(summaries[0])
    wanted = ["job-04"] if allowed is None else ["job-04", f"job-05-i{allowed}"]
    models.require(names == wanted, f"job-04's duration {summaries[0]['duration']} requires {wanted}, not {names}")


def loaded(item: tuple[Path, bool]) -> dict[str, Any] | None:
    path, complete = item
    return models.job_data(path) if complete else None


def anchor_mean(data: dict[str, Any]) -> tuple[float, float]:
    """Inverse-variance mean X of the seed-0 settings and its variance."""
    z, v = reading.x_statistics(data)
    anchor = reading.anchors_of(data)
    weight = 1 / v[anchor]
    return float((weight * z[anchor]).sum() / weight.sum()), float(1 / weight.sum())


def evaluated(item: tuple[dict[str, Any], dict[str, Any]]) -> list[tuple[float, float, float]]:
    """(observed X, its counting variance, predicted X) of every mesh of a subset under one frozen predictor."""
    part, entry = item
    light, dlight = models.static_light(part, np.array(entry["offsets"]), np.array(entry["free"]))
    rows = fixed.mesh_rows(part, light, dlight)
    models.require(all(len(r) == 1 and r[0][0] == "x" for r in rows), "a new mesh serves one X readout")
    return [(r[0][1], r[0][3], r[0][2]) for r in rows]


def admitted(keys: list[str], perturbed: list[int], seen: set[str]) -> tuple[list[int], list[int]]:
    """The perturbed configurations an earlier run already served, and those the primary admits."""
    return [c for c in perturbed if keys[c] in seen], [c for c in perturbed if keys[c] not in seen]


def job_rows(data: dict[str, Any], keep: list[int], offsets: dict[str, Any]) -> list[dict[str, Any]]:
    """Observed and predicted X of the kept configurations, one row per mesh."""
    settings = np.flatnonzero(np.isin(data["configuration"], keep) & ~reading.anchors_of(data))
    part = reading.subset(data, settings)
    results = ordered_map(evaluated, [(part, offsets[name]) for name in PREDICTORS], min_items=1)
    predicted = {name: [row[2] for row in result] for name, result in zip(PREDICTORS, results, strict=True)}
    observed = [(row[0], row[1]) for row in results[0]]
    return [
        {
            "mesh": list(part["keys"][i]),
            "observed": observed[i][0],
            "counting_variance": observed[i][1],
            **{f"predicted_{name}": predicted[name][i] for name in PREDICTORS},
        }
        for i in range(len(part["keys"]))
    ]


def centered(values: np.ndarray, jobs: np.ndarray) -> np.ndarray:
    out = values.astype(float).copy()
    for job in np.unique(jobs):
        out[jobs == job] -= out[jobs == job].mean()
    return out


def primary(predicted: np.ndarray, observed: np.ndarray, jobs: np.ndarray, ceiling_sq: float) -> dict[str, Any]:
    n, count = len(observed), len(np.unique(jobs))
    finite = bool(np.isfinite(predicted).all() and np.isfinite(observed).all() and math.isfinite(ceiling_sq))
    if not finite or n - count - 2 < 1:
        return {"meshes": n, "jobs": count, "reading": "not read"}
    x, y = centered(predicted, jobs), centered(observed, jobs)
    if not np.any(x) or not np.any(y):
        return {"meshes": n, "jobs": count, "reading": "not read"}
    r = min(max(float((x @ y) / math.sqrt((x @ x) * (y @ y))), -1.0), 1.0)
    dof = n - 1 - count
    t: float | None = None
    if abs(r) == 1.0:
        p = 0.0 if r > 0 else 1.0
        lower = upper = r
    else:
        t = r * math.sqrt(dof / (1 - r * r))
        p = float(stats.t.sf(t, dof))
        quantile = float(stats.norm.ppf(1 - ALPHA_EACH))
        error = 1 / math.sqrt(n - count - 2)
        lower = math.tanh(math.atanh(r) - quantile * error)
        upper = math.tanh(math.atanh(r) + quantile * error)
    slope, intercept = np.polyfit(x, y, 1)
    return {
        "meshes": n,
        "jobs": count,
        "pearson_r": r,
        "t": t,
        "degrees_of_freedom": dof,
        "p_one_sided": p,
        "alpha": ALPHA_EACH,
        "reading": "carried" if p < ALPHA_EACH else "not carried",
        "r_lower": lower,
        "r_upper": upper,
        "share": min(r * r / ceiling_sq, 1.0) if r > 0 else 0.0,
        "share_lower": min(lower * lower / ceiling_sq, 1.0) if lower > 0 else 0.0,
        "share_upper": min(upper * upper / ceiling_sq, 1.0) if upper > 0 else 0.0,
        "spearman": float(stats.spearmanr(x, y).statistic),
        "affine": {"slope": float(slope), "intercept": float(intercept)},
    }


def outcome(readings: dict[str, dict[str, Any]], steady: bool, reference: float) -> str:
    carried = {name: readings[name].get("reading") == "carried" for name in PREDICTORS}
    if any(readings[name].get("reading") == "not read" for name in PREDICTORS):
        return "not read"
    if all(carried.values()):
        return "both carried"
    if carried["exploration"]:
        return "P-A carried only"
    if carried["all-meshes"]:
        return "P-B carried only"
    if any(readings[name]["r_upper"] < 0 for name in PREDICTORS):
        return "inconclusive: anticorrelated"
    if not steady:
        return "inconclusive: anchors moved"
    if all(readings[name]["share_upper"] < reference for name in PREDICTORS):
        return "bounded"
    return "inconclusive"


def frozen_cases() -> dict[str, str]:
    return {
        path.parent.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(CASES.glob("job-0[45]*/cases.json"))
    }


def score(
    offsets_path: Path, confirmation_path: Path, references: list[Path], runs: list[Path], enforce: bool = True
) -> dict[str, Any]:
    """The score record. enforce applies the frozen reference and acquisition sets; the retained-run tests lift it to
    drive the pipeline with earlier jobs standing in for new ones."""
    frozen = json.loads(offsets_path.read_text(encoding="utf-8"))
    offsets = {entry["name"]: entry for entry in frozen["predictors"]}
    models.require(sorted(offsets) == sorted(PREDICTORS), f"{offsets_path.name} holds {sorted(offsets)}")
    confirmation = json.loads(confirmation_path.read_text(encoding="utf-8"))
    reference_data = ordered_map(models.job_data, references)
    by_job = {d["record"]["manifest"]["job"]: d for d in reference_data}
    if enforce:
        models.require(sorted(by_job) == list(REFERENCE_JOBS), f"the references are {sorted(by_job)}")
    models.require(BASELINE_JOB in by_job, f"the reference runs omit {BASELINE_JOB}, the anchor baseline")
    baseline, baseline_variance = anchor_mean(by_job[BASELINE_JOB])
    critical = float(stats.norm.ppf(0.5 + ANCHOR_LEVEL / 2))
    seen = {key for d in reference_data for key in mesh_keys(d)}
    margin = math.sqrt(confirmation["explained_share"]["compilation_variance"])
    summaries = ordered_map(returned, runs)
    if enforce:
        acquisition(summaries, frozen_cases())
    first_partial = enforce and not summaries[0]["complete"]
    datasets = ordered_map(loaded, [(path, summary["complete"]) for path, summary in zip(runs, summaries, strict=True)])
    jobs: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    for summary, data in zip(summaries, datasets, strict=True):
        if data is None:
            jobs.append({**summary, "scored": False})
            continue
        name = summary["job"]
        keys = mesh_keys(data)
        anchor = reading.anchors_of(data)
        perturbed = sorted({int(c) for c in data["configuration"][~anchor]})
        old, keep = admitted(keys, perturbed, seen)
        seen.update(keys)
        mean, variance = anchor_mean(data)
        z, v = reading.x_statistics(data)
        shift = mean - baseline
        half_width = critical * math.sqrt(variance + baseline_variance)
        jobs.append(
            {
                **summary,
                "perturbed_settings": int((~anchor).sum()),
                "distinct_perturbed_meshes": len(perturbed),
                "previously_served": len(old),
                "anchor_control": {
                    "mean": mean,
                    "baseline_mean": baseline,
                    "shift": shift,
                    "half_width": half_width,
                    "level": ANCHOR_LEVEL,
                    "margin": margin,
                    "reading": "steady" if abs(shift) + half_width <= margin else "moved",
                },
                "dispersion_ratio": float(reading.dispersion_ratio(z, v, anchor[None, :])[0]),
                "scored": len(keep) >= MIN_JOB_MESHES,
            }
        )
        if jobs[-1]["scored"]:
            rows.extend({"job": name, **row} for row in job_rows(data, keep, offsets))
    labels = np.array([row["job"] for row in rows])
    observed = np.array([row["observed"] for row in rows])
    compilation = confirmation["explained_share"]["compilation_variance"]
    steady = all(job["anchor_control"]["reading"] == "steady" for job in jobs if job["scored"])
    reference = confirmation["explained_share"]["share_of_ceiling"]
    held = confirmation["rows"]
    # With no scored mesh the ceiling and every correlation are unavailable, and the record says so in place of NaN.
    counting: float | None = None
    ceiling_sq: float | None = None
    unread = {"meshes": 0, "jobs": 0, "reading": "not read"}
    readings = {LABELS[name]: unread for name in PREDICTORS}
    pooled: dict[str, Any] = unread
    if rows and not first_partial:
        counting = float(np.mean([row["counting_variance"] for row in rows]))
        ceiling_sq = compilation / (compilation + counting)
        readings = {
            LABELS[name]: primary(np.array([row[f"predicted_{name}"] for row in rows]), observed, labels, ceiling_sq)
            for name in PREDICTORS
        }
        pooled = primary(
            np.concatenate([[row["predicted_exploration"] for row in rows], [row["predicted"] for row in held]]),
            np.concatenate([observed, [row["observed"] for row in held]]),
            np.concatenate([labels, ["held-out"] * len(held)]),
            ceiling_sq,
        )
    return {
        "schema": "ascella-new-mesh-score-v1",
        "plan": "docs/state/plans/ascella-new-seed-meshes-case.json",
        "offsets": offsets_path.relative_to(ROOT).as_posix(),
        "references": [path.relative_to(ROOT).as_posix() for path in references],
        "alpha": ALPHA,
        "jobs": jobs,
        "ceiling": {
            "compilation_variance": compilation,
            "mean_counting_variance": counting,
            "squared": ceiling_sq,
        },
        "reference_share": reference,
        "primary": readings,
        "outcome": outcome({name: readings[LABELS[name]] for name in PREDICTORS}, steady, reference),
        "exploratory_pooled_with_held_out": pooled,
        "rows": rows,
    }


def main(argv: list[str]) -> int:
    check = argv[-1:] == ["--check"]
    args = argv[:-1] if check else argv
    models.require("--" in args and len(args) >= 6, f"usage: see the module docstring, not {argv}")
    split = args.index("--")
    paths = [Path(arg).resolve() for arg in args]
    out = paths[-1]
    record = score(paths[0], paths[1], paths[2:split], paths[split + 1 : -1])
    text = json.dumps(record, indent=1, sort_keys=True) + "\n"
    if check:
        models.replay(json.loads(text), json.loads(out.read_text(encoding="utf-8")), out.name)
        return 0
    models.require(not out.exists(), f"{out} exists; the score is written once")
    out.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
