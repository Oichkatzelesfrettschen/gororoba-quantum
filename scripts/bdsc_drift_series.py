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
  centered on that run's unweighted class mean, which removes a
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
  "$PYTHON" scripts/bdsc_drift_series.py --write
  "$PYTHON" scripts/bdsc_drift_series.py --check
  "$PYTHON" scripts/bdsc_drift_series.py --write-diagnostic
  "$PYTHON" scripts/bdsc_drift_series.py --check-diagnostic

--write writes the readout of the seven retained series runs (READOUT_RUNS)
to READOUT, a runner-image record (ci/runner_image_records.json); --check
proves READOUT equals a fresh readout of those runs byte for byte.
--write-diagnostic and --check-diagnostic do the same for DIAGNOSTIC, the
exploratory readings chosen after the readout: the unweighted superposition
class means with their counting errors; the pair excess with the counting
variance of the centered change subtracted (centered_counting_variances; the
readout's excess subtracts the uncentered variance and reads low by mean
var / 16); the Spearman correlation of that excess with lag against every
relabeling of the run times; the six-state sum rules of every template and
seed group; and the mode-5 share against the plan-time mode-5 dark rate.
--sensitivity prints the share of seeded synthetic series (SENSITIVITY_SEED,
SENSITIVITY_REPLICATES per scenario) that the primary reads resolved, at the
retained reference error, for white jitter shared within each group of four
settings and for random walks of several step sizes; the written case quotes
it.
"""

from __future__ import annotations

import argparse
import functools
import itertools
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import norm, rankdata

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
# Replicates per pooled block of --sensitivity: a block's (block, 16, 5040) work arrays stay near 16 MB.
BLOCK = 25
STATE_DIR = ROOT / "results/quandela/schedules/bdsc-drift-series"
DARK_DIR = ROOT / "results/quandela/bdsc_drift_series_dark"
READOUT = ROOT / "results/quandela/bdsc_drift_series_readout_pinned.json"
DIAGNOSTIC = ROOT / "results/quandela/bdsc_drift_series_diagnostic_pinned.json"
READOUT_RUNS = (
    "2026-10-24T070006Z-qpu_belenos-bdsc_drift_series-t1",
    "2026-10-24T090005Z-qpu_belenos-bdsc_drift_series-t2",
    "2026-10-24T110005Z-qpu_belenos-bdsc_drift_series-t3",
    "2026-10-24T130006Z-qpu_belenos-bdsc_drift_series-t4",
    "2026-10-24T150006Z-qpu_belenos-bdsc_drift_series-t5",
    "2026-10-24T170006Z-qpu_belenos-bdsc_drift_series-t6",
    "2026-10-24T190006Z-qpu_belenos-bdsc_drift_series-t7",
)
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


def require_passed_receipt(run: Path) -> None:
    """The series admits a run only with its slot's passed scheduler receipt naming this directory."""
    match = SERIES_RUN.fullmatch(run.name)
    require(match is not None, f"{run}: not a series run directory")
    path = STATE_DIR / f"{match[1] if match else ''}.receipt.json"
    require(path.is_file(), f"{run}: no scheduler receipt {st.rel(path)}")
    receipt = json.loads(path.read_text(encoding="utf-8"))
    require(receipt.get("run") == run.name, f"{run}: {st.rel(path)} names {receipt.get('run')!r}")
    require(receipt.get("outcome") == "passed", f"{run}: {st.rel(path)} reads {receipt.get('outcome')!r}")


def load_run(run: Path, frozen: dict[str, Any], validate: bool = True) -> dict[str, Any]:
    """One admitted b1-j1 run: start time, plan-time dark counts and the per-instance detector_absent fractions."""
    manifest, result, submission = st.admit(run, validate, frozen)
    require(manifest["job"] == JOB, f"{run}: job {manifest['job']!r}, the series reads {JOB} runs")
    status = result.get("status", {}).get("status")
    require(status == "completed", f"{run}: the job ended {status!r}")
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


@functools.cache
def adjacency(n: int) -> tuple[tuple[tuple[int, int], ...], np.ndarray]:
    """The run pairs (i, j), i < j, and for every ordering of n runs (identity first) whether i and j are adjacent.

    The successive-difference sum of an ordering is the sum of the squared differences of its adjacent pairs, so
    every ordering reads from one table of pair differences, and a reversed ordering has the same row.
    """
    pairs = tuple(itertools.combinations(range(n), 2))
    index = {pair: k for k, pair in enumerate(pairs)}
    table = np.zeros((math.factorial(n), len(pairs)))
    for row, order in enumerate(itertools.permutations(range(n))):
        for a, b in itertools.pairwise(order):
            table[row, index[(min(a, b), max(a, b))]] = 1.0
    return pairs, table


def ordering_statistics(residuals: np.ndarray) -> np.ndarray:
    """Mean von Neumann ratio over the settings of residuals (..., settings, runs) for every ordering of the runs.

    Element 0 of the last axis is the identity ordering, the observed statistic. Every sum runs elementwise in a
    fixed order over runs, pairs and settings, so a stack of series returns, bit for bit, what each series returns
    alone.
    """
    n = residuals.shape[-1]
    pairs, table = adjacency(n)
    mean = residuals[..., 0].copy()
    for t in range(1, n):
        mean = mean + residuals[..., t]
    mean = mean / n
    spread = (residuals[..., 0] - mean) ** 2
    for t in range(1, n):
        spread = spread + (residuals[..., t] - mean) ** 2
    require(bool(np.all(spread > 0)), "a constant series has no von Neumann ratio")
    steps = np.zeros((*residuals.shape[:-1], table.shape[0]))
    for k, (i, j) in enumerate(pairs):
        steps = steps + ((residuals[..., i] - residuals[..., j]) ** 2)[..., None] * table[:, k]
    ratios = steps / spread[..., None]
    total = ratios[..., 0, :].copy()
    for row in range(1, ratios.shape[-2]):
        total = total + ratios[..., row, :]
    return np.asarray(total / ratios.shape[-2])


def permutation_p(residuals: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(observed statistic, exact one-sided p over all orderings of the runs) of each series in the stack."""
    stats = ordering_statistics(residuals)
    observed = stats[..., :1]
    return stats[..., 0], (stats <= observed * (1 + TIE)).sum(axis=-1) / stats.shape[-1]


def center(values: dict[int, dict[str, Any]]) -> float:
    """Unweighted mean of one run's superposition values.

    Equal weights subtract a shift common to every setting exactly; inverse-variance weights move with the shifted
    fractions and would leave part of a common drift in every residual.
    """
    members = [v["p"] for v in values.values() if diag.class_of(v["label"]) == "superposition"]
    return math.fsum(members) / len(members)


def centered(series: list[dict[str, Any]]) -> tuple[list[int], np.ndarray]:
    """The superposition settings and their residuals about each run's unweighted class mean (settings x runs)."""
    centers = [center(run["values"]) for run in series]
    indices = sorted(i for i, v in series[0]["values"].items() if diag.class_of(v["label"]) == "superposition")
    rows = [[run["values"][i]["p"] - c for run, c in zip(series, centers, strict=True)] for i in indices]
    return indices, np.array(rows)


def primary(series: list[dict[str, Any]]) -> dict[str, Any]:
    """Pooled von Neumann ratio of the class-centered superposition residuals, against every run ordering."""
    n = len(series)
    if n < MIN_POINTS:
        return {"reading": "not run", "reason": f"{n} completed series runs, the primary needs {MIN_POINTS}", "n": n}
    indices, residuals = centered(series)
    observed, p = permutation_p(residuals)
    statistic, p_value = float(observed), float(p)
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


def _synthetic_p(draws: np.ndarray) -> np.ndarray:
    """The primary's p for a stack of synthetic series (..., settings, runs), each centered on its runs' means."""
    settings = draws.shape[-2]
    center = draws[..., 0, :].copy()
    for row in range(1, settings):
        center = center + draws[..., row, :]
    return permutation_p(draws - (center / settings)[..., None, :])[1]


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
    stacked = np.array(draws)
    blocks = [stacked[k : k + BLOCK] for k in range(0, len(stacked), BLOCK)]
    ps = [float(p) for block in parallel.ordered_map(_synthetic_p, blocks) for p in block]
    out = {}
    for k, name in enumerate(scenarios):
        chosen = ps[k * replicates : (k + 1) * replicates]
        out[name] = sum(1 for p in chosen if p < diag.ALPHA) / replicates
    return out


def pair_excess(first: dict[str, Any], second: dict[str, Any]) -> float:
    """Mean over the superposition settings of the class-centered squared change less its counting variance."""
    shift = center(second["values"]) - center(first["values"])
    terms = [
        (second["values"][i]["p"] - v["p"] - shift) ** 2 - v["se"] ** 2 - second["values"][i]["se"] ** 2
        for i, v in first["values"].items()
        if diag.class_of(v["label"]) == "superposition"
    ]
    return math.fsum(terms) / len(terms)


def _load(item: tuple[Path, dict[str, Any], bool]) -> dict[str, Any]:
    return load_run(*item)


def load_runs(
    anchors: list[Path], series: list[Path], frozen: dict[str, Any], validate: bool
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """load_run of the anchors and the series runs through one order-preserving pool."""
    loaded = parallel.ordered_map(_load, [(run, frozen, validate) for run in [*anchors, *series]])
    return loaded[: len(anchors)], loaded[len(anchors) :]


def centered_counting_variances(first: dict[str, Any], second: dict[str, Any]) -> dict[int, float]:
    """Each superposition setting's counting variance of its class-centered change, for independent setting errors.

    Centering subtracts the mean change of the n settings, so setting s keeps var_s (1 - 2 / n) + sum_j var_j / n^2
    of the pair's counting variance var_s = se1^2 + se2^2; pair_excess subtracts var_s itself, and its mean over the
    settings is low by mean var / n.
    """
    variances = {
        i: v["se"] ** 2 + second["values"][i]["se"] ** 2
        for i, v in first["values"].items()
        if diag.class_of(v["label"]) == "superposition"
    }
    n = len(variances)
    total = math.fsum(variances.values())
    return {i: var * (1 - 2 / n) + total / n**2 for i, var in variances.items()}


def pair_excess_centered(first: dict[str, Any], second: dict[str, Any]) -> float:
    """pair_excess with the counting variance of the centered change (centered_counting_variances) subtracted."""
    shift = center(second["values"]) - center(first["values"])
    variances = centered_counting_variances(first, second)
    terms = [(second["values"][i]["p"] - first["values"][i]["p"] - shift) ** 2 - var for i, var in variances.items()]
    return math.fsum(terms) / len(terms)


def spearman_over(x: list[float], ys: np.ndarray) -> np.ndarray:
    """Spearman correlation of x with each row of ys, average ranks for ties."""
    rx = rankdata(x)
    rx = rx - rx.mean()
    ry = rankdata(ys, axis=1)
    ry = ry - ry.mean(axis=1, keepdims=True)
    return np.asarray((ry @ rx) / np.sqrt((ry**2).sum(axis=1) * float(rx @ rx)))


def lag_trend(series: list[dict[str, Any]]) -> dict[str, Any]:
    """Spearman correlation of each series pair's centered excess with its lag, against every relabeling of run times.

    Memory makes the excess grow with lag; exchangeable runs leave the pairing of excesses to lags arbitrary, so the
    share of the n! relabelings whose correlation reaches the observed one is an exact upper-tail p (row 0 of the
    relabelings is the identity).
    """
    pairs = list(itertools.combinations(range(len(series)), 2))
    excess = [pair_excess_centered(series[i], series[j]) for i, j in pairs]
    starts = np.array([run["start"] for run in series])
    orderings = np.array(list(itertools.permutations(range(len(series)))))
    first, second = (np.array(side) for side in zip(*pairs, strict=True))
    rho = spearman_over(excess, np.abs(starts[orderings[:, second]] - starts[orderings[:, first]]))
    return {
        "pairs": len(pairs),
        "orderings": len(orderings),
        "spearman": float(rho[0]),
        "p_value": float((rho >= rho[0] - TIE).mean()),
    }


def stray_rate_correlation(runs: list[dict[str, Any]]) -> dict[str, Any]:
    """Spearman correlation of each run's mean mode-5 share with its plan-time mode-5 dark rate, exact two-sided p."""
    share = [run["stray_share"]["mean"] for run in runs]
    rate = np.array([run["stray_rate_at_plan"] for run in runs])
    orderings = np.array(list(itertools.permutations(range(len(runs)))))
    rho = spearman_over(share, rate[orderings])
    return {
        "runs": len(runs),
        "spearman": float(rho[0]),
        "p_value_two_sided": float((np.abs(rho) >= abs(rho[0]) - TIE).mean()),
    }


def sum_rules(values: dict[int, dict[str, Any]]) -> list[dict[str, Any]]:
    """Delta_R = p_+ + p_- - p_f - p_g and Delta_I = p_+i + p_-i - p_f - p_g of each template-and-seed group.

    A group is the six consecutive instances index // 6 of diag.instances(), one per state of the bank; every fixed
    linear effect gives both sums zero (docs/design/bdsc-qualification.md, First qualification case).
    """
    groups: dict[int, dict[str, float]] = {}
    for index, v in values.items():
        groups.setdefault(index // 6, {})[v["label"]] = v["p"]
    out = []
    for group, p in sorted(groups.items()):
        require(sorted(p) == sorted(("f", "g", "+", "-", "+i", "-i")), f"group {group} is not one six-state bank")
        base = p["f"] + p["g"]
        out.append({"group": group, "delta_r": p["+"] + p["-"] - base, "delta_i": p["+i"] + p["-i"] - base})
    return out


def diagnostic(series_dirs: list[Path], validate: bool = True) -> dict[str, Any]:
    """Exploratory readings of the series, chosen after the preregistered readout and reported beside it."""
    frozen = st.documents()
    for run in series_dirs:
        require_passed_receipt(run)
    anchors, series = load_runs([st.RUNS_DIR / name for name in ANCHORS], series_dirs, frozen, validate)
    means = []
    for record in series:
        members = [v for v in record["values"].values() if diag.class_of(v["label"]) == "superposition"]
        se = math.sqrt(math.fsum(v["se"] ** 2 for v in members)) / len(members)
        means.append({"run": record["run"], "mean": center(record["values"]), "se": se})
    centers = [m["mean"] for m in means]
    average = math.fsum(centers) / len(centers)
    by_lag: dict[int, list[float]] = {}
    for a, b in itertools.combinations(series, 2):
        by_lag.setdefault(round((b["start"] - a["start"]) / 3600), []).append(pair_excess_centered(a, b))
    rules = [{"run": record["run"], "groups": sum_rules(record["values"])} for record in series]
    deltas = [g[key] for r in rules for g in r["groups"] for key in ("delta_r", "delta_i")]
    return {
        "schema": "bdsc-drift-series-diagnostic-v1",
        "standing": "exploratory: chosen after the preregistered readout, which no reading here revises",
        "superposition_unweighted_means": {
            "runs": means,
            "sample_sd": math.sqrt(math.fsum((c - average) ** 2 for c in centers) / (len(centers) - 1)),
            "range": max(centers) - min(centers),
            "von_neumann": von_neumann(centers),
        },
        "lag_profile_centered": [
            {"lag_hours": lag, "pairs": len(v), "mean_excess": math.fsum(v) / len(v)}
            for lag, v in sorted(by_lag.items())
        ],
        "lag_trend": lag_trend(series),
        "sum_rules": {
            "runs": rules,
            "contrasts": len(deltas),
            "negative": sum(d < 0 for d in deltas),
            "min": min(deltas),
            "max": max(deltas),
            "mean": math.fsum(deltas) / len(deltas),
        },
        "stray_share_against_plan_rate": {
            "all_runs": stray_rate_correlation(anchors + series),
            "series_runs": stray_rate_correlation(series),
        },
    }


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
        require_passed_receipt(run)
    anchors, series = load_runs([st.RUNS_DIR / name for name in ANCHORS], series_dirs, frozen, validate)
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

    supers = [center(run["values"]) for run in series]
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
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--write-diagnostic", action="store_true")
    group.add_argument("--check-diagnostic", action="store_true")
    args = parser.parse_args()
    if args.sensitivity:
        print(json.dumps(sensitivity(), indent=1, sort_keys=True))
    elif args.write or args.check or args.write_diagnostic or args.check_diagnostic:
        build, path = (readout, READOUT) if args.write or args.check else (diagnostic, DIAGNOSTIC)
        text = json.dumps(build([st.RUNS_DIR / run for run in READOUT_RUNS]), indent=1, sort_keys=True) + "\n"
        name = path.relative_to(ROOT).as_posix()
        if args.write or args.write_diagnostic:
            path.write_text(text, encoding="utf-8")
            print(f"bdsc drift series: wrote {name}")
        else:
            require(path.is_file() and path.read_text(encoding="utf-8") == text, f"{name} differs from a fresh build")
            print(f"bdsc drift series: {name} matches a fresh build from its retained runs")
    else:
        print(json.dumps(readout([run.resolve() for run in args.readout]), indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
