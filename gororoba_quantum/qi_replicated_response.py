"""Replicated Tuna-17 matched-response analysis: Stein two-stage t test on per-replicate residuals.

A replicate is one batch of three circuits: the two weighted witness circuits (witness-a carries B in
region 1 and F in region 2, witness-b carries F in region 1 and D in region 2) and one readout circuit.
Both witnesses share one calibration window, so a batch-by-region interaction leaves the residual

    r = (p_a2 - p_a1) + (p_b1 - p_b2) = F_R2 - B_R1 + F_R1 - D_R2

of the raw selector-zero frequencies p. Under an affine response p_obs = a_region + g_region * p_ideal with
batch offsets common to both regions, the offsets cancel and r = (g2 - g1) / 2, so a mean residual of zero is
equal products of readout factor and visibility in the two regions. That tests the device response; the
algebra is certified offline.

Stage 1 takes N1 replicates. Their sample standard deviation s1 (N1 - 1 degrees of freedom) alone fixes the
total N = max(N1, ceil(s1^2 / C)); the stage-1 mean never enters the rule. The statistic uses the mean of
all N replicates and s1:

    t = mean_N * sqrt(N) / s1,   reject when abs(t) >= T_CRIT = t_{0.995, N1 - 1}.

Because N depends on s1 only and mean_N is independent of s1 for normal residuals, t = SHIFT_effect + T with T
a central t variable on N1 - 1 degrees of freedom whenever delta sqrt(N) / s1 >= delta / sqrt(C). C is
delta^2 / SHIFT^2 with SHIFT the noncentrality that gives two-sided power POWER at level ALPHA for the
shifted central t law. The level is exact for every sigma; the power is POWER for every sigma whose N stays
at or under CAP, and a case whose rule asks for more than CAP replicates stops after stage 1 undecided.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np

from qi_matched_response import READOUT_ERROR_LIMIT, SELECTORS, _joint_moments

SCHEMA = "qi-replicated-response-analysis-v1"
N1 = 12
CAP = 60
ALPHA = 0.01
POWER = 0.80
DELTA = 0.024
DF = N1 - 1
# t_{0.995, 11}, the noncentrality at which P(abs(SHIFT + T) >= T_CRIT) = POWER for T central t on 11 degrees of
# freedom, and C = DELTA^2 / SHIFT^2. A test compares the three with scipy.
T_CRIT = 3.1058065155392804
SHIFT = 3.9812975678033524
C = 3.6339019606546454e-05
LAG_BOUND = 0.3
WITNESS_A = "witness-a.cq"
WITNESS_B = "witness-b.cq"
READOUT_ZERO = "readout-0.cq"
READOUT_ONE = "readout-1.cq"
WITNESS_CASES = {WITNESS_A: ("bright", "fixture"), WITNESS_B: ("fixture", "dark")}
LABELS = ("F_R2", "B_R1", "F_R1", "D_R2")
WEIGHTS = (1, -1, 1, -1)
SCHEMA_PROPOSAL = "qi-matched-zero-divisor-replicated-proposal-v1"
SCHEMA_MANIFEST = "qi-matched-zero-divisor-replicate-v1"
PROPOSAL_SHA256 = "3be5d6e6ee5e4cbb3cebeed33578009ab6fef3525917001a35e78d8dd384c073"
BATCH = re.compile(r"rep-(\d{2})")


def _require(condition: object, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def batch_name(index: int) -> str:
    return f"rep-{index:02d}"


def schedule(index: int) -> list[str]:
    """Circuit order of replicate index: witnesses swap each replicate, the readout circuit every two."""
    first, second = (WITNESS_A, WITNESS_B) if index % 2 == 0 else (WITNESS_B, WITNESS_A)
    return [first, second, READOUT_ZERO if (index // 2) % 2 == 0 else READOUT_ONE]


def required_replicates(s1: Any) -> Any:
    """Total replicates N = max(N1, ceil(s1^2 / C)); numpy-vectorized, a function of the stage-1 SD alone."""
    return np.maximum(N1, np.ceil(np.asarray(s1, dtype=float) ** 2 / C)).astype(np.int64)


def stein_statistic(mean: Any, s1: Any, n: Any) -> Any:
    """t = mean_N sqrt(N) / s1 with s1 from the first N1 replicates."""
    return np.asarray(mean, dtype=float) * np.sqrt(np.asarray(n, dtype=float)) / np.asarray(s1, dtype=float)


def stein_decision(residuals: Sequence[float]) -> dict[str, Any]:
    """Apply the preregistered rule to the replicate residuals collected so far, in replicate order."""
    values = np.asarray(residuals, dtype=float)
    _require(values.ndim == 1 and bool(np.isfinite(values).all()), "the replicate residuals are not finite")
    count = len(values)
    _require(count >= N1, f"{count} replicates collected; stage 1 needs {N1}")
    s1 = float(np.std(values[:N1], ddof=1))
    _require(s1 > 0, "the stage-1 standard deviation is zero")
    required = int(required_replicates(s1))
    out: dict[str, Any] = {
        "n1": N1,
        "cap": CAP,
        "s1": s1,
        "mean_stage1": float(values[:N1].mean()),
        "required_total": required,
        "collected": count,
        "critical_t": T_CRIT,
        "degrees_of_freedom": DF,
    }
    if required > CAP:
        _require(count == N1, f"the rule stops at the cap after stage 1; {count} replicates differ from {N1}")
        half = T_CRIT * s1 / math.sqrt(N1)
        out.update(
            status="undecided_at_cap",
            n=N1,
            mean=out["mean_stage1"],
            interval_99=[out["mean_stage1"] - half, out["mean_stage1"] + half],
            detectable_effect_power80=SHIFT * s1 / math.sqrt(N1),
        )
        return out
    if count == N1 and required > N1:
        out.update(status="continue", n=N1)
        return out
    _require(count == required, f"{count} replicates differ from the rule's N = {required}")
    mean = float(values.mean())
    half = T_CRIT * s1 / math.sqrt(count)
    statistic = float(stein_statistic(mean, s1, count))
    out.update(
        status="rejected" if abs(statistic) >= T_CRIT else "not_rejected",
        n=count,
        mean=mean,
        t=statistic,
        interval_99=[mean - half, mean + half],
        detectable_effect_power80=SHIFT * s1 / math.sqrt(count),
    )
    return out


def lag1(values: Sequence[float]) -> dict[str, Any]:
    """Lag-1 autocorrelation with its white-noise interval; unreliable when it exceeds LAG_BOUND and its interval."""
    data = np.asarray(values, dtype=float)
    centered = data - data.mean()
    rho = float(centered[:-1] @ centered[1:] / (centered @ centered))
    half = 1.96 / math.sqrt(len(data))
    return {
        "estimate": rho,
        "interval_95": [rho - half, rho + half],
        "bound": LAG_BOUND,
        "unreliable": abs(rho) > LAG_BOUND and abs(rho) > half,
    }


def order_difference(values: Sequence[float]) -> dict[str, Any]:
    """Mean of the even (witness-a first) minus the odd (witness-b first) replicates, Welch interval."""
    from scipy import stats

    data = np.asarray(values, dtype=float)
    even, odd = data[0::2], data[1::2]
    variances = np.array([even.var(ddof=1) / len(even), odd.var(ddof=1) / len(odd)])
    standard_error = math.sqrt(float(variances.sum()))
    freedom = float(variances.sum() ** 2 / (variances**2 / np.array([len(even) - 1, len(odd) - 1])).sum())
    half = float(stats.t.ppf(0.975, freedom)) * standard_error
    difference = float(even.mean() - odd.mean())
    return {
        "difference": difference,
        "standard_error": standard_error,
        "degrees_of_freedom": freedom,
        "interval_95": [difference - half, difference + half],
    }


def proposal_digests(directory: Path) -> dict[str, Any]:
    """sha256 binding of proposal.json, every replicate manifest and every replicate circuit file."""
    _require(
        _digest(directory / "proposal.json") == PROPOSAL_SHA256, "proposal.json differs from the approved proposal"
    )
    proposal = json.loads((directory / "proposal.json").read_text())
    _require(proposal.get("schema") == SCHEMA_PROPOSAL, "proposal schema differs")
    rows = proposal["schedule"]
    _require(len(rows) == CAP, f"the proposal schedule holds {len(rows)} replicates, not {CAP}")
    circuits = {name: row["sha256"] for name, row in proposal["circuits"].items()}
    batches: dict[str, Any] = {}
    for index, row in enumerate(rows):
        name = batch_name(index)
        _require(row["batch"] == name and row["order"] == schedule(index), f"{name}: the schedule differs")
        _require(_digest(directory / name / "cases.json") == row["manifest_sha256"], f"{name}: manifest differs")
        observed = {path.name: _digest(path) for path in sorted((directory / name).glob("*.cq"))}
        expected = {file: circuits[file] for file in row["order"]}
        _require(observed == expected, f"{name}: a circuit differs from the approved proposal")
        batches[name] = {"cases.json": row["manifest_sha256"], "circuits": observed}
    return {"proposal.json": PROPOSAL_SHA256, "batches": batches}


def verify_job_order(name: str, manifest: Mapping[str, Any], jobs: Sequence[tuple[str, Any]]) -> None:
    """Refuse a run whose submitted jobs are not the manifest circuits in manifest order with rising job ids."""
    files = [row["file"] for row in manifest["circuits"]]
    _require([file for file, _ in jobs] == files, f"{name}: the submitted job order differs from the schedule")
    ids = [job for _, job in jobs]
    _require(
        all(isinstance(job, int) and not isinstance(job, bool) for job in ids)
        and all(first < second for first, second in zip(ids, ids[1:], strict=False)),
        f"{name}: job ids do not rise in the schedule order",
    )


def _replicate(
    index: int,
    manifest: Mapping[str, Any],
    shots: Mapping[tuple[str, str], Sequence[str] | None],
    proposal: Mapping[str, Any],
) -> dict[str, Any]:
    name = batch_name(index)
    _require(manifest.get("schema") == SCHEMA_MANIFEST and manifest.get("batch") == name, f"{name}: wrong manifest")
    _require(
        manifest.get("backend") == proposal["backend"] and manifest.get("shots") == proposal["shots_per_job"],
        f"{name}: the manifest differs from the proposal in backend or shots",
    )
    order = schedule(index)
    _require([row["file"] for row in manifest["circuits"]] == order, f"{name}: the circuit order differs")
    _require(manifest.get("replicate") == index, f"{name}: the manifest names another replicate")
    witnesses = {file: tuple(cases) for file, cases in manifest.get("witnesses", {}).items()}
    _require(witnesses == WITNESS_CASES, f"{name}: the witness case assignment differs")
    expected = int(manifest["shots"])
    moments = {
        file: _joint_moments(shots.get((name, file)), SELECTORS, expected, f"{name} {file}")[0] for file in order
    }
    readout = order[2]
    if readout == READOUT_ZERO:
        _require(bool((moments[readout] <= READOUT_ERROR_LIMIT).all()), f"{name}: a selector readout error exceeds")
    else:
        _require(bool((1 - moments[readout] <= READOUT_ERROR_LIMIT).all()), f"{name}: a selector readout error exceeds")
    zero = {file: 1 - moments[file] for file in (WITNESS_A, WITNESS_B)}
    # selector-zero frequency per region: witness-a is (B, F), witness-b is (F, D)
    raw = zero[WITNESS_A][1] - zero[WITNESS_A][0] + zero[WITNESS_B][0] - zero[WITNESS_B][1]
    return {
        "name": name,
        "order": order,
        "readout": readout,
        "witness_read1": {file: moments[file] for file in (WITNESS_A, WITNESS_B)},
        "readout_read1": moments[readout],
        "residual": float(raw),
    }


def _block_corrected(rows: Sequence[dict[str, Any]]) -> list[float]:
    """Exploratory: the residual corrected with the readout pair pooled over each complete block of four."""
    out = []
    for start in range(0, len(rows) - len(rows) % 4, 4):
        block = rows[start : start + 4]
        m0 = np.mean([row["readout_read1"] for row in block if row["readout"] == READOUT_ZERO], axis=0)
        m1 = np.mean([row["readout_read1"] for row in block if row["readout"] == READOUT_ONE], axis=0)
        denominator = m1 - m0
        _require(bool((denominator > 0).all()), "a block readout assignment is singular or reversed")
        _require(bool((m0 + 1 - m1 <= READOUT_ERROR_LIMIT).all()), "a block selector readout error exceeds the bound")
        residuals = []
        for row in block:
            v = {file: (m1 - row["witness_read1"][file]) / denominator for file in (WITNESS_A, WITNESS_B)}
            residuals.append(v[WITNESS_A][1] - v[WITNESS_A][0] + v[WITNESS_B][0] - v[WITNESS_B][1])
        out.append(float(np.mean(residuals)))
    return out


def analyze_replicated_series(
    proposal: Mapping[str, Any],
    manifests: Mapping[str, Mapping[str, Any]],
    shots: Mapping[tuple[str, str], Sequence[str] | None],
    *,
    job_order: Mapping[str, Sequence[tuple[str, Any]]],
) -> dict[str, Any]:
    """Analyze the collected replicates rep-00 .. rep-(n-1) of one replicated proposal."""
    _require(proposal.get("schema") == SCHEMA_PROPOSAL, "the proposal schema differs")
    _require(tuple(proposal["contrast"]["labels"]) == LABELS, "the proposal labels differ from the frozen labels")
    _require(tuple(proposal["contrast"]["weights"]) == WEIGHTS, "the proposal weights differ")
    design = proposal["design"]
    _require(
        (design["n1"], design["cap"], design["critical_t"], design["c"]) == (N1, CAP, T_CRIT, C),
        "the proposal design differs from the frozen rule",
    )
    names = sorted(manifests)
    _require(all(BATCH.fullmatch(name) for name in names), "a manifest name is not a replicate name")
    count = len(names)
    _require(names == [batch_name(index) for index in range(count)], "a replicate is missing or out of sequence")
    _require(count >= N1, f"{count} replicates collected; stage 1 needs {N1}")
    _require(set(job_order) == set(names), "the job orders differ from the replicates")
    rows = []
    for index, name in enumerate(names):
        verify_job_order(name, manifests[name], job_order[name])
        rows.append(_replicate(index, manifests[name], shots, proposal))
    residuals = [row["residual"] for row in rows]
    decision = stein_decision(residuals)
    return {
        "schema": SCHEMA,
        "estimand": "raw residual F_R2 - B_R1 + F_R1 - D_R2 per replicate; null (g2 - g1) / 2 = 0",
        "replicates": [{"batch": row["name"], "order": row["order"], "residual": row["residual"]} for row in rows],
        "decision": decision,
        "exchangeability": {"lag1": lag1(residuals), "order_difference": order_difference(residuals)},
        "exploratory_block_corrected": {
            "label": "exploratory; no decision rests on it",
            "block_residuals": _block_corrected(rows),
            "replicates_outside_complete_blocks": count % 4,
        },
    }
