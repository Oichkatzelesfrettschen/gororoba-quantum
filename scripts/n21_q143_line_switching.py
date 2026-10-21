"""Post hoc switching time of the two frequency lines of a segmented sweep's spectator, from shot order.

A run's 48 PUBs execute column-wise (docs/notes/ibm_quantum/repetition-rate-execution.md):
shot k of every circuit, then shot k + 1, so consecutive shots of one PUB lie
one column period apart, the job's single execution chunk divided by its
shots. The static fit of the run's segmented-sweep analysis gives two lines
f1 and f1 + df with weight a; at an xy delay t with df t near half a cycle the
lines read opposite X and Y signs, so a shot's six reads label its line by the
log-likelihood ratio of its pattern under line 1 (a = 1) against line 2
(a = 0). At a delay with df t a whole number of cycles both lines read alike
and the label carries nothing.

Tests and their readings:

| Outcome | Reading |
|---|---|
| labels at half-cycle delays correlate across shots and decay with lag | the line switches with that time |
| raw reads at whole-cycle delays correlate as well | a drift common to both lines, not two lines |
| labels hold over the whole job | a static environment |
| labels do not correlate across shots | switching between a shot's end and one column period |

The time comes from the mean label autocorrelation of the half-cycle arms at
lags 1 to 4 columns, ln r(k) = ln R - k T / tau, R the squared label
reliability; a moving-block bootstrap over columns (BLOCK columns, REPLICATES
draws, batched across draws) gives its interval. Same-arm lags are exact
multiples of the column period whatever the PUB order within a column.

RUN_DIR ANALYSIS writes RUN_DIR/line-switching.json; --check requires equal
bytes.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gororoba_quantum"))

import n21_orbit_rca as rca  # noqa: E402
import n21_q143_segmented_sweep as sweep  # noqa: E402

SCHEMA = "n21-q143-line-switching-v1"
RETAINED = "line-switching.json"
FIT_LAGS = (1, 2, 3, 4)
REPORT_LAGS = (1, 2, 4, 8, 16, 64)
HALF_CYCLE_TOLERANCE = 0.1
BLOCK = 64
REPLICATES = 400
SEED = 20261021


def column_period_ms(run: Path, pubs: int) -> float:
    """The job's single execution chunk, every PUB in it, divided by the shots per PUB."""
    (job,) = [path for path in (run / "raw").iterdir() if path.is_dir()]
    metadata = json.loads((job / "result_metadata.json").read_text())
    chunks = metadata["executor"]["chunk_timing"]
    if len(chunks) != 1 or sorted(int(part["idx_item"]) for part in chunks[0]["parts"]) != list(range(pubs)):
        raise RuntimeError(f"{run}: the job ran in {len(chunks)} chunks, not one holding all {pubs} PUBs")
    shots = len(json.loads((job / "pub_00.json").read_text())["registers"]["g0_r0_s1_read"]["bitstrings"])
    span = datetime.fromisoformat(chunks[0]["stop"]) - datetime.fromisoformat(chunks[0]["start"])
    return span.total_seconds() * 1e3 / shots


def arm_series(run: Path, fit: dict[str, float]) -> dict[int, dict[str, Any]]:
    """Per xy delay, the per-shot line label and mean X read in shot order, NaN for a dropped shot."""
    from qpe_diagnostics import n21_segment_bases, n21_segmented_key

    params = np.array([fit[name] for name in sweep.names("static")])
    one = sweep.unpack("static", params) | {"a": 1.0}
    two = one | {"a": 0.0}
    members = [member["name"] for member in rca._group(run)["members"]]
    found: dict[int, dict[str, Any]] = {}
    for name, circuit, payload in zip(members, rca._circuits(run), rca.raw_pubs(run), strict=True):
        kind, delay, pre = n21_segmented_key(name) or ("", 0, 0)
        if kind != "xy" or pre:
            continue
        shot = sweep.member_shots(circuit, payload)
        bases = n21_segment_bases(kind, shot["segments"])
        kept = np.array([pattern is not None for pattern in shot["patterns"]])
        patterns = np.array([pattern or (-1,) * shot["segments"] for pattern in shot["patterns"]], dtype=np.int64)
        schedule = sweep.member_schedule(sweep.spectator_stages(payload, shot["spectator"]), shot["segments"])
        gaps = tuple(schedule["gaps_dt"])
        point = sweep.Point(name, kind, delay, 0, bases, gaps, patterns, np.ones(len(patterns)))
        label = sweep.point_log_likelihood("static", one, point) - sweep.point_log_likelihood("static", two, point)
        xs = [k for k, basis in enumerate(bases) if basis == "x"]
        reads = np.where(patterns[:, xs] >= 0, patterns[:, xs], np.nan).astype(float)
        with np.errstate(invalid="ignore"):
            raw = np.nanmean(np.where(np.isnan(reads).all(axis=1, keepdims=True), 0.0, reads), axis=1)
        raw[np.isnan(reads).all(axis=1)] = np.nan
        found[delay] = {
            "cycles": fit["df_mhz"] * delay * sweep.DT_US,
            "label": np.where(kept, label, np.nan),
            "raw": np.where(kept, raw, np.nan),
        }
    return found


def batched_autocorrelation(series: np.ndarray, index: np.ndarray, lag: int) -> np.ndarray:
    """Pearson r of series[:, index[r, :-lag]] against series[:, index[r, lag:]] per draw r and row; NaN pairs drop."""
    first = series[:, index[:, :-lag]]
    second = series[:, index[:, lag:]]
    valid = np.isfinite(first) & np.isfinite(second)
    count = valid.sum(axis=-1)
    a = np.where(valid, first, 0.0)
    b = np.where(valid, second, 0.0)
    mean_a = a.sum(axis=-1) / count
    mean_b = b.sum(axis=-1) / count
    da = np.where(valid, a - mean_a[..., None], 0.0)
    db = np.where(valid, b - mean_b[..., None], 0.0)
    covariance = (da * db).sum(axis=-1)
    with np.errstate(invalid="ignore", divide="ignore"):
        result = covariance / np.sqrt((da * da).sum(axis=-1) * (db * db).sum(axis=-1))
    return np.asarray(result.T)


def switching_fit(series: np.ndarray, index: np.ndarray, period_ms: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Per draw: tau in ms, R, and the mean autocorrelation over rows at FIT_LAGS, from ln r = ln R - k T / tau."""
    mean = np.stack([batched_autocorrelation(series, index, lag).mean(axis=1) for lag in FIT_LAGS], axis=1)
    lags = np.array(FIT_LAGS, dtype=float)
    centered = lags - lags.mean()
    logs = np.log(mean)
    slope = (logs - logs.mean(axis=1, keepdims=True)) @ centered / (centered @ centered)
    intercept = logs.mean(axis=1) - slope * lags.mean()
    return -period_ms / slope, np.exp(intercept), mean


def block_index(shots: int, replicates: int, rng: np.random.Generator) -> np.ndarray:
    """Moving-block bootstrap column indices, one row per draw, BLOCK columns per block."""
    blocks = shots // BLOCK
    starts = rng.integers(0, shots - BLOCK + 1, size=(replicates, blocks))
    return (starts[:, :, None] + np.arange(BLOCK)).reshape(replicates, blocks * BLOCK)


def defined(value: float) -> float | None:
    """value, or None where a constant series leaves the correlation undefined."""
    return float(value) if math.isfinite(value) else None


def report(run: Path, analysis: Path) -> dict[str, Any]:
    fit = json.loads(analysis.read_text())["fits"]["static"]["parameters"]
    arms = arm_series(run, fit)
    pubs = len(rca._group(run)["members"])
    period = column_period_ms(run, pubs)
    shots = len(next(iter(arms.values()))["label"])
    full = np.arange(shots)[None, :]
    per_arm = {}
    for delay, arm in sorted(arms.items()):
        rows = np.stack([arm["label"], arm["raw"]])
        per_arm[str(delay)] = {
            "cycles": arm["cycles"],
            "label_sd": float(np.nanstd(arm["label"])),
            "label_autocorrelation": {
                str(lag): defined(batched_autocorrelation(rows[:1], full, lag)[0, 0]) for lag in REPORT_LAGS
            },
            "raw_x_autocorrelation": {
                str(lag): defined(batched_autocorrelation(rows[1:], full, lag)[0, 0]) for lag in REPORT_LAGS
            },
        }
    half = sorted(d for d, arm in arms.items() if abs(abs(arm["cycles"]) % 1.0 - 0.5) < HALF_CYCLE_TOLERANCE)
    whole = sorted(d for d, arm in arms.items() if min(abs(arm["cycles"]) % 1.0, 1 - abs(arm["cycles"]) % 1.0) < 0.05)
    labels = np.stack([arms[d]["label"] for d in half])
    tau, reliability, mean = switching_fit(labels, full, period)
    draws = switching_fit(labels, block_index(shots, REPLICATES, np.random.default_rng(SEED)), period)[0]
    weight = fit["a"]
    return {
        "schema_version": SCHEMA,
        "analysis": analysis.name,
        "column_period_ms": period,
        "shots": shots,
        "half_cycle_delays_dt": half,
        "whole_cycle_delays_dt": whole,
        "arms": per_arm,
        "tau_ms": float(tau[0]),
        "label_reliability_squared": float(reliability[0]),
        "mean_label_autocorrelation": {str(lag): float(v) for lag, v in zip(FIT_LAGS, mean[0], strict=True)},
        "bootstrap": {
            "block_columns": BLOCK,
            "replicates": REPLICATES,
            "seed": SEED,
            "tau_ms_quantiles": {q: float(np.quantile(draws, float(q))) for q in ("0.025", "0.5", "0.975")},
        },
        "dwell_ms": {"line_1": float(tau[0]) / (1 - weight), "line_2": float(tau[0]) / weight},
        "whole_cycle_raw_lag1_max_abs": max(abs(per_arm[str(d)]["raw_x_autocorrelation"]["1"]) for d in whole),
        "drift_null_standard_error": 1 / math.sqrt(shots),
    }


def serialize(value: dict[str, Any]) -> str:
    return json.dumps(sweep.beat.rounded(value), indent=1, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run", type=Path)
    parser.add_argument("analysis", type=Path, help="the run's segmented-sweep analysis whose static fit labels lines")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    text = serialize(report(args.run, args.analysis))
    target = args.run / RETAINED
    if args.check:
        if target.read_text() != text:
            raise RuntimeError(f"{target} differs from a fresh analysis")
        return 0
    target.write_text(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
