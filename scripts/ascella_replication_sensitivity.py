"""Exploratory sensitivity of the Ascella replication score, deterministic and post hoc.

docs/evidence/ascella-order-coefficients/replication-score.json is the preregistered reading; this record asks what
its numbers depend on, with no random draw:

- in-block background: models.setting_probabilities adds to each setting the outside-block count of the same
  iteration shared over modes 0 to 3 (ascella_physical_models.job_data), so the scored prediction carries a term read
  from the test counts; each predictor is rescored with that term set to zero, and the returned circuit at zero
  offsets is scored with and without it, and each predictor's increment over that zero-offset prediction is read as
  the correlation of their difference with X and as the partial correlation given it;
- accuracy at the predictors' own scale: the affine slope and the within-job R^2 at slope one, 1 - sum (y - x)^2 /
  sum y^2 over within-job-centered x and y, beside r^2 / c^2 of the score;
- robustness: Spearman correlation, each job's own r, leave-one-out r, and r after dropping the DROPPED rows whose
  removal moves r most;
- a structure-preserving null: every pair of circular shifts of the two jobs' centered outcomes against the fixed
  centered predictions, 84 x 84 = 7,056 alignments counting the observed one, p the share at or above the observed r;
- offset stability: the correlation between R-B's and R-C's fitted offsets, heaters and couplers apart, which shows
  which offsets the two training sets agree on;
- the R-C against R-B difference: Williams t, Steiger z and Meng z for two dependent overlapping correlations, and the
  Zou 95 % interval, on n - (J - 1) effective meshes (docs/notes/papers/diedenhofen-musch-2015-cocor.md, S1 Eq. 12 to
  14, 19 to 26, 31 to 36). The implementation reproduces the article's example before it reads the replication.

Usage:
  "$PYTHON" scripts/ascella_replication_sensitivity.py OFFSETS SCORE REFERENCE_RUNS... -- NEW_RUNS... OUT [--check]
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
import ascella_new_mesh_score as base  # noqa: E402
import ascella_physical_models as models  # noqa: E402
import ascella_replication_score as replication  # noqa: E402

from parallel import ordered_map  # noqa: E402

DROPPED = 5
PREDICTORS = replication.REPLICATION.predictors
LABELS = dict(zip(PREDICTORS, replication.REPLICATION.labels, strict=True))
# Diedenhofen and Musch 2015, the printed example: r_jk, r_jh, r_kh, n, and Williams t, Steiger z, Meng z, Zou interval,
# printed to four decimals, so a reproduction agrees within one unit of the last printed place.
COCOR_EXAMPLE = (0.1038, 0.3213, 0.0257, 291)
COCOR_PRINTED = (-2.7743, -2.7513, -2.7432, -0.3689, -0.0630)


def williams(rjk: float, rjh: float, rkh: float, n: int) -> float:
    rbar = (rjk + rjh) / 2
    det = 1 + 2 * rjk * rjh * rkh - rjk**2 - rjh**2 - rkh**2
    return (rjk - rjh) * math.sqrt((n - 1) * (1 + rkh) / (2 * ((n - 1) / (n - 3)) * det + rbar**2 * (1 - rkh) ** 3))


def steiger(rjk: float, rjh: float, rkh: float, n: int) -> float:
    rbar = (rjk + rjh) / 2
    c = (rkh * (1 - 2 * rbar**2) - 0.5 * rbar**2 * (1 - 2 * rbar**2 - rkh**2)) / (1 - rbar**2) ** 2
    return (math.atanh(rjk) - math.atanh(rjh)) * math.sqrt(n - 3) / math.sqrt(2 - 2 * c)


def meng(rjk: float, rjh: float, rkh: float, n: int) -> float:
    r2 = (rjk**2 + rjh**2) / 2
    f = min((1 - rkh) / (2 * (1 - r2)), 1.0)
    h = (1 - f * r2) / (1 - r2)
    return (math.atanh(rjk) - math.atanh(rjh)) * math.sqrt((n - 3) / (2 * (1 - rkh) * h))


def zou(rjk: float, rjh: float, rkh: float, n: int) -> tuple[float, float]:
    quantile = float(stats.norm.ppf(0.975))

    def limits(r: float) -> tuple[float, float]:
        return math.tanh(math.atanh(r) - quantile / math.sqrt(n - 3)), math.tanh(
            math.atanh(r) + quantile / math.sqrt(n - 3)
        )

    l1, u1 = limits(rjk)
    l2, u2 = limits(rjh)
    c = ((rkh - rjk * rjh / 2) * (1 - rjk**2 - rjh**2 - rkh**2) + rkh**3) / ((1 - rjk**2) * (1 - rjh**2))
    lower = (rjk - rjh) - math.sqrt((rjk - l1) ** 2 + (u2 - rjh) ** 2 - 2 * c * (rjk - l1) * (u2 - rjh))
    upper = (rjk - rjh) + math.sqrt((u1 - rjk) ** 2 + (rjh - l2) ** 2 - 2 * c * (u1 - rjk) * (rjh - l2))
    return lower, upper


def unit_check() -> None:
    computed = (williams(*COCOR_EXAMPLE), steiger(*COCOR_EXAMPLE), meng(*COCOR_EXAMPLE), *zou(*COCOR_EXAMPLE))
    for value, printed in zip(computed, COCOR_PRINTED, strict=True):
        models.require(abs(value - printed) <= 1e-4, f"the cocor example gives {computed}, not {COCOR_PRINTED}")


def correlation(x: np.ndarray, y: np.ndarray) -> float:
    return float(x @ y / math.sqrt((x @ x) * (y @ y)))


def scored_parts(references: list[Path], runs: list[Path]) -> list[dict[str, Any]]:
    """Each new run's scored perturbed settings, selected as ascella_new_mesh_score.score selects them."""
    seen = {key for d in ordered_map(models.job_data, references) for key in base.mesh_keys(d)}
    parts = []
    for data in ordered_map(models.job_data, runs):
        keys = base.mesh_keys(data)
        anchor = reading.anchors_of(data)
        _, keep = base.admitted(keys, sorted({int(c) for c in data["configuration"][~anchor]}), seen)
        seen.update(keys)
        parts.append(reading.subset(data, np.flatnonzero(np.isin(data["configuration"], keep) & ~anchor)))
    return parts


def predictions(item: tuple[dict[str, Any], dict[str, Any], bool]) -> list[float]:
    part, entry, background = item
    data = part if background else {**part, "background": np.zeros_like(part["background"])}
    return [row[2] for row in base.evaluated((data, entry))]


def accuracy(x: np.ndarray, y: np.ndarray, jobs: np.ndarray) -> dict[str, Any]:
    names = sorted(set(jobs))
    r = correlation(x, y)
    loo = [
        correlation(
            base.centered(np.delete(x, i), np.delete(jobs, i)), base.centered(np.delete(y, i), np.delete(jobs, i))
        )
        for i in range(len(y))
    ]
    order = np.argsort(-np.abs(np.array(loo) - r))[:DROPPED]
    kept = np.setdiff1d(np.arange(len(y)), order)
    trimmed_x, trimmed_y = base.centered(x[kept], jobs[kept]), base.centered(y[kept], jobs[kept])
    return {
        "pearson_r": r,
        "spearman": float(stats.spearmanr(x, y).statistic),
        "slope": float((x @ y) / (x @ x)),
        "r2_at_slope_one": float(1 - ((y - x) @ (y - x)) / (y @ y)),
        "per_job_r": {
            name: correlation(base.centered(x[jobs == name], jobs[jobs == name]), y[jobs == name]) for name in names
        },
        "leave_one_out_r": [min(loo), max(loo)],
        "dropped_rows": [int(i) for i in order],
        "r_without_dropped": correlation(trimmed_x, trimmed_y),
    }


def shift_null(x: np.ndarray, y: np.ndarray, jobs: np.ndarray, observed: float) -> dict[str, Any]:
    """Every pair of circular shifts of each job's centered outcomes against the fixed centered predictions."""
    names = sorted(set(jobs))
    dots = []
    for name in names:
        xs, ys = x[jobs == name], y[jobs == name]
        dots.append(np.array([xs @ np.roll(ys, shift) for shift in range(len(ys))]))
    total = (dots[0][:, None] + dots[1][None, :]).ravel()
    r = total / math.sqrt((x @ x) * (y @ y))
    return {
        "alignments": int(r.size),
        "at_or_above": int((r >= observed - 1e-12).sum()),
        "p": float((r >= observed - 1e-12).mean()),
    }


def build(offsets_path: Path, score_path: Path, references: list[Path], runs: list[Path]) -> dict[str, Any]:
    unit_check()
    entries = {entry["name"]: entry for entry in json.loads(offsets_path.read_text(encoding="utf-8"))["predictors"]}
    score = json.loads(score_path.read_text(encoding="utf-8"))
    rows = score["rows"]
    jobs = np.array([row["job"] for row in rows])
    y = base.centered(np.array([row["observed"] for row in rows]), jobs)
    parts = scored_parts(references, runs)
    zero = {"offsets": [0.0] * sum(entries[PREDICTORS[0]]["free"]), "free": entries[PREDICTORS[0]]["free"]}
    cases = [(name, entries[name]) for name in PREDICTORS] + [("zero-offset", zero)]
    items = [(part, entry, background) for _, entry in cases for background in (True, False) for part in parts]
    flat = ordered_map(predictions, items, min_items=1)
    series: dict[tuple[str, bool], np.ndarray] = {}
    for index, (name, background) in enumerate((name, background) for name, _ in cases for background in (True, False)):
        chunk = flat[index * len(parts) : (index + 1) * len(parts)]
        series[(name, background)] = base.centered(np.concatenate([np.array(c) for c in chunk]), jobs)
    for name in PREDICTORS:
        recorded = base.centered(np.array([row[f"predicted_{name}"] for row in rows]), jobs)
        models.require(
            np.allclose(series[(name, True)], recorded, atol=1e-12), f"{name}: the rebuilt predictions differ"
        )
    readings = {}
    for name in PREDICTORS:
        x = series[(name, True)]
        reading_ = accuracy(x, y, jobs)
        reading_["circular_shift_null"] = shift_null(x, y, jobs, reading_["pearson_r"])
        reading_["r_without_background"] = correlation(series[(name, False)], y)
        nominal = series[("zero-offset", True)]
        reading_["r_offset_component"] = correlation(x - nominal, y)
        r_xy, r_xz, r_zy = reading_["pearson_r"], correlation(x, nominal), correlation(nominal, y)
        partial = (r_xy - r_xz * r_zy) / math.sqrt((1 - r_xz**2) * (1 - r_zy**2))
        dof = len(y) - len(set(jobs)) - 2
        reading_["partial_r_given_zero_offset"] = partial
        reading_["partial_p_one_sided"] = float(stats.t.sf(partial * math.sqrt(dof / (1 - partial**2)), dof))
        readings[LABELS[name]] = reading_
    heaters = int(parts[0]["phases"].shape[1])
    fitted = [np.array(entries[name]["offsets"]) for name in PREDICTORS]
    models.require(
        all(entries[name]["free"] == entries[PREDICTORS[0]]["free"] for name in PREDICTORS), "free masks differ"
    )
    stability = {
        "heaters": heaters,
        "couplers": int(fitted[0].size - heaters),
        "heater_offset_r": float(np.corrcoef(fitted[0][:heaters], fitted[1][:heaters])[0, 1]),
        "coupler_offset_r": float(np.corrcoef(fitted[0][heaters:], fitted[1][heaters:])[0, 1]),
    }
    rc, rb = readings["R-C"]["pearson_r"], readings["R-B"]["pearson_r"]
    rkh = correlation(series[(PREDICTORS[0], True)], series[(PREDICTORS[1], True)])
    n = len(y) - (len(set(jobs)) - 1)
    t = williams(rc, rb, rkh, n)
    return {
        "schema": "ascella-replication-sensitivity-v1",
        "plan": replication.REPLICATION.plan,
        "status": "exploratory, post hoc; the preregistered reading is replication-score.json",
        "score": score_path.relative_to(ROOT).as_posix(),
        "meshes": len(y),
        "predictors": readings,
        "offset_stability": stability,
        "zero_offset": {
            "r_with_background": correlation(series[("zero-offset", True)], y),
            "r_without_background": correlation(series[("zero-offset", False)], y),
        },
        "difference_r_c_minus_r_b": {
            "r_c": rc,
            "r_b": rb,
            "r_between_predictors": rkh,
            "effective_meshes": n,
            "williams_t": t,
            "williams_degrees_of_freedom": n - 3,
            "williams_p_two_sided": float(2 * stats.t.sf(abs(t), n - 3)),
            "steiger_z": steiger(rc, rb, rkh, n),
            "meng_z": meng(rc, rb, rkh, n),
            "zou_95": list(zou(rc, rb, rkh, n)),
        },
    }


def main(argv: list[str]) -> int:
    check = argv[-1:] == ["--check"]
    args = argv[:-1] if check else argv
    models.require("--" in args and len(args) >= 6, f"usage: see the module docstring, not {argv}")
    split = args.index("--")
    paths = [Path(arg).resolve() for arg in args]
    record = build(paths[0], paths[1], paths[2:split], paths[split + 1 : -1])
    text = json.dumps(record, indent=1, sort_keys=True) + "\n"
    if check:
        models.replay(json.loads(text), json.loads(paths[-1].read_text(encoding="utf-8")), paths[-1].name)
        return 0
    paths[-1].write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
