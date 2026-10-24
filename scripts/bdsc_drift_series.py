"""Belenos drift series of one frozen request: the preregistered readout of seven spaced repeats of b1-j1.

The series submits results/quandela/cases/bdsc_stationarity/b1-j1/ unchanged
seven times, two hours apart, from the schedule
results/quandela/schedules/bdsc-drift-series.json, so every run passes
bdsc_stationarity.admit() byte for byte and its matched check. The two
retained 100000-sample runs of the same request (bdsc_stationarity.CONTRAST_RUNS,
either side of a Belenos calibration on 2026-10-23) are the anchors.
Every reading is under the primary stray-detector veto (detector_absent).

The stationarity readout left an excess variance tau of about 0.0021 in the
superposition class's matched changes. A white run-to-run jitter and a drift
that accumulates with elapsed time both produce it at a single lag; the
series separates them by the order of the residuals in time.

- Primary (instance-specific drift). Each run's superposition values are
  centered on that run's inverse-variance class mean, which removes a
  common shift of the class. For each of the 16 superposition settings the
  von Neumann ratio eta = sum (x[t+1] - x[t])^2 / sum (x[t] - mean x)^2 runs
  over the completed series runs in start order, and the statistic is the
  mean of the 16 ratios. A drift that persists between runs lowers it. The
  null is exact: one permutation of the run order, shared by every setting,
  is applied to all n! orderings, and p is the share of orderings whose
  statistic is at or below the observed one. Per-run centering commutes with
  a permutation of the runs, and a shared permutation keeps any correlation
  between settings (the four settings of one template and seed share a
  compilation), so exchangeable runs give an exact test whatever the jitter
  level or its correlation. A series and its reverse read alike, so the
  smallest attainable p is 2 / n!. A resolved reading (p < 0.01) names
  instance-specific drift; consistent (p >= 0.05) names run-to-run jitter
  without memory. Fewer than MIN_POINTS completed series runs leave the
  primary not run. The independent-setting normal reference, mean 2 and
  variance 4 (n - 2) / ((n - 1) (n + 1)) / 16, is reported beside it.
- Reported only: each class's run mean per run and the von Neumann ratio of
  the superposition class mean; the mean excess square of the class-centered
  change (d^2 - se1^2 - se2^2) of the superposition settings for every pair of
  runs, anchors included, against the pair's lag; the calibration epoch of each
  run (runs whose plan-time dark-count vectors are equal share an epoch) and
  the mean excess of within-epoch against between-epoch pairs; the mode-5
  share of each run against its plan-time and post-collection dark-count rate.

Usage:
  "$PYTHON" scripts/bdsc_drift_series.py --readout SERIES_RUN_DIR...
  "$PYTHON" scripts/bdsc_drift_series.py --sensitivity

--sensitivity prints the share of seeded synthetic series (SENSITIVITY_SEED,
SENSITIVITY_REPLICATES per scenario) that the primary reads resolved, at the
retained reference error, for white jitter shared within each group of four
settings and for random walks of several step sizes; the written case quotes
it.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import bdsc_stationarity as st  # noqa: E402

import parallel  # noqa: E402

diag = st.diag
veto = st.veto
JOB = "b1-j1"
# The series run directories, STAMP-RUN_NAME as qd_schedule.py stages them, one per slot t1 to t7.
SERIES_RUN = re.compile(r"\d{4}-\d\d-\d\dT\d{6}Z-qpu_belenos-bdsc_drift_series-(t[1-7])")
ANCHORS = st.CONTRAST_RUNS
# The primary needs this many completed series runs: its smallest p is 2 / n!, which is below 0.01 from n = 6
# (2 / 720) and 0.017 at n = 5, so one skipped slot still leaves a decidable test.
MIN_POINTS = 6
# A permuted statistic within this relative distance of the observed one counts as tied, since a reversed ordering
# sums the same squares in another order.
TIE = 1e-12
SENSITIVITY_SEED = 20261024
SENSITIVITY_REPLICATES = 2000
# The retained reference error of one superposition value at 100000 samples (half the matched-change variance of
# results/quandela/bdsc_stationarity_calibration_contrast.json, median 0.0025 / sqrt 2).
SENSITIVITY_SE = 0.0018
GROUP = 4
DARK_DIR = ROOT / "results/quandela/bdsc_drift_series_dark"
CLASSES = tuple(diag.CLASSES)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def post_collection_stray(run: Path) -> float | None:
    """Mode 5's dark-count rate in the after-job snapshot the schedule wrote for this run, if any."""
    match = SERIES_RUN.fullmatch(run.name)
    path = DARK_DIR / f"after-{match[1] if match else ''}" / "catalogue.json"
    if match is None or not path.is_file():
        return None
    catalogue = json.loads(path.read_text(encoding="utf-8"))
    perfs = catalogue.get("processors", {}).get(st.PLATFORM, {}).get("perfs") or {}
    return st.mode_rates(perfs.get(st.DARK), st.rel(path))[st.STRAY]


def load_run(run: Path, frozen: dict[str, Any], validate: bool = True) -> dict[str, Any]:
    """One admitted b1-j1 run: start time, plan-time dark counts and the per-instance detector_absent fractions."""
    manifest, result, submission = st.admit(run, validate, frozen)
    require(manifest["job"] == JOB, f"{run}: job {manifest['job']!r}, the series reads {JOB} runs")
    items = diag.observations(manifest, result, st.TRIALS)
    if validate:
        retained = st.retained_circuits(JOB)
        require(all(i["circuit_sha256"] == retained[x] for x, i in items.items()), f"{run}: a circuit recompiled")
    _, absent, stray = veto.tallies(manifest, result, items)
    rates = st.dark_rates(submission.get("perfs_at_plan") or {}, f"{run}: plan")
    labels = {i["index"]: i["label"] for i in diag.instances()}
    values = {}
    for index, tally in sorted(absent.items()):
        p = tally["selected"] / tally["eligible"]
        values[index] = {"label": labels[index], "p": p, "se": diag.reference_se(p, tally["eligible"])}
    shares = [s["share"] for s in stray.values()]
    return {
        "run": st.rel(run),
        "start": diag.utc(result["data"]["start_time"]),
        "dark": rates,
        "values": values,
        "stray_share": {"mean": math.fsum(shares) / len(shares), "min": min(shares), "max": max(shares)},
        "stray_rate_at_plan": rates[st.STRAY],
        "stray_rate_after": post_collection_stray(run),
    }


def class_mean(values: dict[int, dict[str, Any]], name: str) -> tuple[float, float]:
    """Inverse-variance mean and standard error of one class's values in one run."""
    members = [v for v in values.values() if diag.class_of(v["label"]) == name]
    weights = [1 / v["se"] ** 2 for v in members]
    total = math.fsum(weights)
    return math.fsum(w * v["p"] for w, v in zip(weights, members, strict=True)) / total, 1 / math.sqrt(total)


def von_neumann(series: list[float]) -> float:
    """sum (x[t+1] - x[t])^2 / sum (x[t] - mean)^2 of one series in time order."""
    mean = math.fsum(series) / len(series)
    spread = math.fsum((x - mean) ** 2 for x in series)
    require(spread > 0, "a constant series has no von Neumann ratio")
    return math.fsum((b - a) ** 2 for a, b in itertools.pairwise(series)) / spread


def null_variance(n: int) -> float:
    """Variance of the von Neumann ratio of n independent, identically distributed normal values."""
    return 4 * (n - 2) / ((n - 1) * (n + 1))


def ordering_statistics(residuals: np.ndarray) -> np.ndarray:
    """Mean von Neumann ratio over the rows of residuals (settings x runs) for every ordering of the runs.

    Row 0 of itertools.permutations is the identity, so element 0 is the observed statistic. The denominator of
    each ratio does not depend on the order, so only the successive differences are permuted.
    """
    n = residuals.shape[1]
    orders = np.array(list(itertools.permutations(range(n))))
    spread = ((residuals - residuals.mean(axis=1, keepdims=True)) ** 2).sum(axis=1)
    require(bool(np.all(spread > 0)), "a constant series has no von Neumann ratio")
    permuted = residuals[:, orders]
    steps = ((permuted[:, :, 1:] - permuted[:, :, :-1]) ** 2).sum(axis=2)
    return np.asarray((steps / spread[:, None]).mean(axis=0))


def permutation_p(residuals: np.ndarray) -> tuple[float, float]:
    """(observed statistic, exact one-sided p over all orderings of the runs)."""
    stats = ordering_statistics(residuals)
    return float(stats[0]), float(np.mean(stats <= stats[0] * (1 + TIE)))


def centered(series: list[dict[str, Any]]) -> tuple[list[int], np.ndarray]:
    """The superposition settings and their residuals about each run's class mean (settings x runs)."""
    centers = [class_mean(run["values"], "superposition")[0] for run in series]
    indices = sorted(i for i, v in series[0]["values"].items() if diag.class_of(v["label"]) == "superposition")
    rows = [[run["values"][i]["p"] - c for run, c in zip(series, centers, strict=True)] for i in indices]
    return indices, np.array(rows)


def primary(series: list[dict[str, Any]]) -> dict[str, Any]:
    """Pooled von Neumann ratio of the class-centered superposition residuals, against every run ordering."""
    n = len(series)
    if n < MIN_POINTS:
        return {"reading": "not run", "reason": f"{n} completed series runs, the primary needs {MIN_POINTS}", "n": n}
    indices, residuals = centered(series)
    statistic, p_value = permutation_p(residuals)
    reference = null_variance(n) / len(indices)
    z = (statistic - 2) / math.sqrt(reference)
    return {
        "test": "pooled von Neumann ratio of class-centered superposition residuals under detector_absent",
        "null": f"exact, all {math.factorial(n)} orderings of the runs shared by every setting",
        "n_runs": n,
        "n_settings": len(indices),
        "mean_ratio": statistic,
        "p_value": p_value,
        "smallest_attainable_p": 2 / math.factorial(n),
        "reading": diag.reading(p_value),
        "independent_reference": {"mean": 2.0, "variance_of_mean": reference, "z": z, "p_value": float(norm.cdf(z))},
        "ratios": {
            series[0]["values"][i]["label"] + f"#{i}": von_neumann(list(row))
            for i, row in zip(indices, residuals, strict=True)
        },
    }


def _synthetic_p(draw: np.ndarray) -> float:
    """The primary's p for one synthetic series (settings x runs), centered on each run's mean as the readout is."""
    return permutation_p(draw - draw.mean(axis=0, keepdims=True))[1]


def sensitivity(
    replicates: int = SENSITIVITY_REPLICATES, seed: int = SENSITIVITY_SEED, runs: int = 7
) -> dict[str, float]:
    """Share of seeded synthetic series that the primary reads resolved, per scenario.

    Every value carries the reference error SENSITIVITY_SE. White jitter adds one draw per run shared by the
    GROUP settings of a template and seed and one per setting; a walk adds an independent random walk per setting
    with the named step SD per two-hour slot. All scenarios' inputs are drawn first, in order, then mapped.
    """
    rng = np.random.default_rng(seed)
    settings = 16
    scenarios = {
        "no drift": (0.0, 0.0, 0.0),
        "white jitter 0.0015, shared in groups": (0.0015, 0.0, 0.0),
        "walk step 0.0021": (0.0, 0.0, 0.0021),
        "walk step 0.0015": (0.0, 0.0, 0.0015),
        "walk step 0.0010": (0.0, 0.0, 0.0010),
    }
    draws = []
    for shared, own, step in scenarios.values():
        for _ in range(replicates):
            noise = rng.standard_normal((settings, runs)) * SENSITIVITY_SE
            group = np.repeat(rng.standard_normal((settings // GROUP, runs)), GROUP, axis=0) * shared
            jitter = rng.standard_normal((settings, runs)) * own
            walk = np.cumsum(rng.standard_normal((settings, runs)) * step, axis=1)
            draws.append(noise + group + jitter + walk)
    ps = parallel.ordered_map(_synthetic_p, draws)
    out = {}
    for k, name in enumerate(scenarios):
        chosen = ps[k * replicates : (k + 1) * replicates]
        out[name] = sum(1 for p in chosen if p < diag.ALPHA) / replicates
    return out


def pair_excess(first: dict[str, Any], second: dict[str, Any]) -> float:
    """Mean over the superposition settings of the class-centered squared change less its counting variance."""
    shift = class_mean(second["values"], "superposition")[0] - class_mean(first["values"], "superposition")[0]
    terms = [
        (second["values"][i]["p"] - v["p"] - shift) ** 2 - v["se"] ** 2 - second["values"][i]["se"] ** 2
        for i, v in first["values"].items()
        if diag.class_of(v["label"]) == "superposition"
    ]
    return math.fsum(terms) / len(terms)


def epochs(runs: list[dict[str, Any]]) -> list[int]:
    """Calibration epoch of each run in start order: a new epoch begins wherever the plan-time dark vector changes."""
    out = [0]
    for earlier, later in itertools.pairwise(runs):
        out.append(out[-1] + (later["dark"] != earlier["dark"]))
    return out


def readout(series_dirs: list[Path], validate: bool = True) -> dict[str, Any]:
    """The preregistered readout of the completed series runs beside the two anchors."""
    frozen = st.documents()
    for run in series_dirs:
        require(SERIES_RUN.fullmatch(run.name) is not None, f"{run}: not a series run directory")
    anchors = [load_run(st.RUNS_DIR / name, frozen, validate) for name in ANCHORS]
    series = [load_run(run, frozen, validate) for run in series_dirs]
    every = anchors + series
    starts = [run["start"] for run in every]
    require(starts == sorted(starts) and len(set(starts)) == len(starts), "the runs are not in start order")
    labels = epochs(every)
    pairs = []
    for (a, ea), (b, eb) in itertools.combinations(zip(every, labels, strict=True), 2):
        pairs.append(
            {
                "first": a["run"],
                "second": b["run"],
                "lag_hours": (b["start"] - a["start"]) / 3600,
                "same_epoch": ea == eb,
                "excess_mean_square": pair_excess(a, b),
            }
        )

    def mean_excess(same: bool) -> float | None:
        chosen = [p["excess_mean_square"] for p in pairs if p["same_epoch"] is same]
        return math.fsum(chosen) / len(chosen) if chosen else None

    supers = [class_mean(run["values"], "superposition")[0] for run in series]
    return {
        "schema": "bdsc-drift-series-readout-v1",
        "primary": primary(series),
        "runs": [
            {
                "run": run["run"],
                "role": "anchor" if k < len(anchors) else "series",
                "start_utc": run["start"],
                "epoch": labels[k],
                "class_means": {
                    name: dict(zip(("mean", "se"), class_mean(run["values"], name), strict=True)) for name in CLASSES
                },
                "stray_share": run["stray_share"],
                "stray_rate_at_plan": run["stray_rate_at_plan"],
                "stray_rate_after": run["stray_rate_after"],
            }
            for k, run in enumerate(every)
        ],
        "superposition_mean_ratio": von_neumann(supers) if len(supers) >= MIN_POINTS else None,
        "pairs": pairs,
        "epoch_excess": {"within": mean_excess(True), "between": mean_excess(False)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--readout", type=Path, nargs="+", metavar="SERIES_RUN_DIR")
    group.add_argument("--sensitivity", action="store_true")
    args = parser.parse_args()
    if args.sensitivity:
        print(json.dumps(sensitivity(), indent=1, sort_keys=True))
    else:
        print(json.dumps(readout([run.resolve() for run in args.readout]), indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
