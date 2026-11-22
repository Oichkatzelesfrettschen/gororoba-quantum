"""Three post-hoc tests of the interleaved Tuna-17 series: a level shift against a moving T1, a disturbance common to
all qubits of a batch, and the identifiability of the X90 ladder over-rotation.

Everything below the dividing line was fixed before any retained reading was used. The statements, thresholds and
formulas of this docstring come first; the retained series enters only through main(). The tests read the series through
the analyzer's own functions (scripts/qi_tuna17_interleaved_cases.py: read_batches, interleaved_roles, anchored_point,
fit_shape) in the pattern of round_fits.py. They decide post hoc and register nothing.

Notation. A batch is one round of one delay multiplier m in (0.5, 1, 2, 4, 8, 12) times each qubit's plateau T; three
jobs (the prepared-0 anchor a0, the prepared-1 anchor a1 and the delay circuit p) share it. The anchored point is
x = (p - a0) / (a1 - a0), span s = a1 - a0, and x(q, m, r) is its value for qubit q, multiplier m, round r (three
rounds per multiplier). The replicate variance s2(q, m) is the sample variance of the three rounds (two degrees of
freedom); vb(q, m) is the mean over the rounds of the variance anchored_point returns with its job-level term tau2 = 0
(the binomial part); the excess is e(q, m) = s2 - vb.

Test 1. Moving T1 against an additive level shift.

  H_L (level shift): each job carries its own additive level shift of variance tau^2. anchored_point carries the term
  linearly, so the replicate excess is tau^2 c(q, m) with c = [variance(tau2 = 1) - variance(tau2 = 0)] of
  anchored_point at the model point, c = (1 + (1 - x)^2 + x^2) / s^2. It is positive at every multiplier, including 8
  and 12 where x is near zero.
  H_T (moving T1): T of qubit q differs between rounds with variance sigma_T^2 and no level shift. The replicate excess
  is sigma_T^2 (dx/dT)^2, with dx/dT the central difference of anchored_point's x at p = a0 + s exp(-t / T). With
  x = exp(-t / T) and the delay t at 8 and 12 times the plateau T, x is 3e-4 and 6e-6 and the excess vanishes there.

  Model point. T is the single-exponential fit (fit_shape) to the six replicate-mean points of the qubit; x, a0, a1 and
  t are the model values and the multiplier means of the retained readings.
  Per qubit and profile, one scale (tau^2, or sigma_T^2) is fitted to the six excesses by iteratively reweighted least
  squares with variance (vb + scale * profile)^2, the variance of a two-degree-of-freedom sample variance under a normal
  model; the scale is floored at zero; the goodness of fit is the weighted chi-square on 5 degrees of freedom. A qubit
  where both profiles have probability below 0.01 is a qubit where neither fits.
  Decision statistic. The pooled level estimate over qubits q and multipliers m in (8, 12):
  U = sum w u / sum w with u = e / c and the fixed weight w = c^2 / vb^2 (the inverse null variance of u); its standard
  error is SE = sqrt(sum w^2 var(u)) / sum w with var(u) = (s2^2 / 2) / c^2 (s2^2 / 2 is the unbiased estimate of the
  variance of a two-degree-of-freedom sample variance). Z = U / SE.
  Prediction. H_L: Z > 3 (excess at 8 and 12 positive). H_T: |Z| <= 3. Falsifiers: Z <= 3 falsifies H_L; Z > 3
  falsifies H_T. Z < -3 means the binomial part over-subtracts and neither profile describes the data.

Test 2. A disturbance common to all qubits of a batch.

  H_C: each batch carries a disturbance shared by the qubits, so the residuals of different qubits in one batch
  correlate. H_0: the residuals of a qubit in one multiplier group are exchangeable and independent of the other qubits.
  Residuals r(q, b) = x(q, b) minus the mean over the rounds of the same qubit and multiplier (qubits by 18 batches),
  each qubit's row divided by its root mean square (a per-qubit scale that a permutation within a group leaves
  unchanged). Statistic, chosen before the data: the leading eigenvalue fraction of the batch-by-batch covariance
  C = R^T R / nq across qubits, lambda_1 / trace(C).
  Null: the round labels are permuted independently per qubit within each multiplier group; 10,000 permutations; the
  p-value is (1 + #[null >= observed]) / (1 + 10,000). The permutation seed is PERMUTATION_SEEDS (four values of one
  retained ANU QRNG draw, indices 0 to 3, combined big-endian to 64 bits); permutation k draws from
  random.Random(f"{seed}:{k}"), so the result does not depend on the worker count.
  Prediction. H_C: p <= 0.01. H_0: p > 0.01. Falsifier of H_C: p > 0.01.

Test 3. Ladder over-rotation identifiability.

  Model P = 1/2 (1 + exp(-gamma N) cos(N dtheta)) at N = 32, 128, 256 pulses per context: two parameters, three
  readings. Reparametrize u = gamma * 256 in [0, 3] and phi = dtheta * 32 in [0, pi] (dtheta in [0, pi / 32], the
  interval before the 2 pi / 32 alias; the sign of dtheta never enters P). The readings at the retained standard errors
  (se_N, the median over the record's x90 rows of |half_value - all_value| / |z| / sqrt(2), rows with |z| > 0.05) form
  the noise model.
  Exact symmetries: dtheta -> -dtheta and dtheta -> dtheta + 2 pi / 32 leave the three readings unchanged, so the domain
  bound is an assumption the data cannot supply.
  Search. For each truth on a 7 by 16 lattice of the domain, the search runs over a 31 by 241 grid of the domain for a
  distinct partner (|du| >= 0.25 or |dphi| >= 0.25) whose noiseless readings differ from the truth's by
  sum ((dP_N) / se_N)^2 < 5.99 (the 95% joint region of two parameters). f is the fraction of truths with a partner.
  Prediction. Identifiable: f <= 0.10 (the ladder is then fitted per qubit, context and drive condition on the grid).
  Not identifiable: f > 0.10, recorded as "not decidable from the retained data (issue 941)" with no fit. Falsifier of
  identifiability: f > 0.10.

Self-test. Each test runs on synthetic series built from a SHA-256 stream (no random generator; the permutation test
uses the QRNG seed): Test 1 a planted level shift and a planted T1 that moves between rounds, Test 2 a planted common
batch disturbance and independent noise, Test 3 readings with standard errors of 1e-5 (identifiable) and 0.05 (not),
and a planted truth that the grid fit recovers. The retained run refuses to start unless every check passes.

Seed provenance. PERMUTATION_SEEDS are indices 0 to 3 of docs/evidence/anu_qrng/draw-2026-11-22T010305Z.json (60895,
62322, 9775, 9353), registered in docs/evidence/qrng_seeds/allocations.json.

Usage: "$PYTHON" docs/evidence/qi-tuna17-interleaved-rounds/hypothesis_tests.py --self-test
       "$PYTHON" docs/evidence/qi-tuna17-interleaved-rounds/hypothesis_tests.py OUT.json
"""

from __future__ import annotations

import hashlib
import json
import math
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import qi_tuna17_interleaved_cases as case  # noqa: E402

from parallel import ordered_map  # noqa: E402

SCHEMA = "qi-tuna17-interleaved-hypothesis-tests-v1"
RUNS = "results/quantum_inspire/runs"
PATTERN = "2026-11-19T1735Z-t17-characterization_interleaved_tuna_17-interleaved_t1-batch-*"
ANALYSIS = "results/quantum_inspire/characterization_interleaved_tuna_17_analysis.json"
DRAW = "docs/evidence/anu_qrng/draw-2026-11-22T010305Z.json"
PERMUTATION_SEEDS = (60895, 62322, 9775, 9353)
PERMUTATIONS = 10_000
SELF_TEST_PERMUTATIONS = 1_000
P_DECISION = 0.01
Z_DECISION = 3.0
LONG_MULTIPLIERS = (4, 5)
LACK_OF_FIT = 0.01
FIT_ITERATIONS = 6
ROUNDS = case.ROUNDS
MULTIPLIERS = case.T1_MULTIPLIERS
LADDER_PULSES = (32, 128, 256)
U_POINTS, PHI_POINTS = 31, 241
U_MAX = 3.0
DISTINCT_STEP = 0.25
JOINT_CHI_SQUARE = 5.99
IDENTIFIABLE_FRACTION = 0.10
MIN_RECORD_Z = 0.05
SIGNIFICANT_DIGITS = 12


def seed64() -> int:
    value = 0
    for word in PERMUTATION_SEEDS:
        value = (value << 16) | word
    return value


def clean(value: Any) -> Any:
    """JSON-ready copy with floats rounded to SIGNIFICANT_DIGITS so reruns write identical bytes."""
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    if isinstance(value, (np.floating, float)):
        number = float(value)
        if not math.isfinite(number):
            raise ValueError("a non-finite number reached the record")
        return float(f"{number:.{SIGNIFICANT_DIGITS}g}")
    if isinstance(value, np.integer):
        return int(value)
    return value


@dataclass
class Replicates:
    """The six-multiplier, three-round anchored readings of one qubit; plain lists so it pickles for ordered_map."""

    qubit: int
    count: int
    t_us: list[float]
    x: list[list[float]]
    vb: list[list[float]]
    a0: list[list[float]]
    a1: list[list[float]]


def replicates(batches: list[dict[str, Any]], roles: list[Any], qubit: int) -> Replicates | None:
    """One qubit's anchored points by multiplier and round; None when any batch's anchors lie too close."""
    count = int(batches[0]["shots"])
    size = len(MULTIPLIERS)
    cells: dict[tuple[int, int], tuple[float, float, float, float, float]] = {}
    for batch, role in zip(batches, roles, strict=True):
        a0 = batch["p1"][role[0]][qubit]
        a1 = batch["p1"][role[1]][qubit]
        p = batch["p1"][role[2]][qubit]
        point = case.anchored_point(p, a0, a1, count, 0.0)
        if point is None:
            return None
        multiplier = batch["meta"]["multiplier"]
        key = (MULTIPLIERS.index(multiplier), int(batch["meta"]["round"]))
        if key in cells:
            raise ValueError(f"two batches hold multiplier {multiplier} round {key[1]}")
        cycles = batch["rows"][role[2]]["delays_cycles"][qubit]
        cells[key] = (point[0], point[1], a0, a1, cycles * case.CYCLE_SECONDS * 1e6)
    if len(cells) != size * ROUNDS:
        raise ValueError(f"want {size * ROUNDS} batches, found {len(cells)}")
    try:
        grid = [[cells[(m, r)] for r in range(ROUNDS)] for m in range(size)]
    except KeyError as missing:
        raise ValueError(f"batch {missing} is absent") from missing
    return Replicates(
        qubit=qubit,
        count=count,
        t_us=[grid[m][0][4] for m in range(size)],
        x=[[c[0] for c in row] for row in grid],
        vb=[[c[1] for c in row] for row in grid],
        a0=[[c[2] for c in row] for row in grid],
        a1=[[c[3] for c in row] for row in grid],
    )


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def profile_pair(t_us: float, t1: float, a0: float, a1: float, count: int) -> tuple[float, float]:
    """(c, (dx/dT)^2) of one model point through anchored_point: c is the coefficient of tau2 in its variance."""
    span = a1 - a0

    def point(t1_value: float, tau2: float) -> tuple[float, float]:
        found = case.anchored_point(a0 + span * math.exp(-t_us / t1_value), a0, a1, count, tau2)
        if found is None:
            raise ValueError("anchors too close for the model point")
        return found

    level = point(t1, 1.0)[1] - point(t1, 0.0)[1]
    step = 1e-4 * t1
    slope = (point(t1 + step, 0.0)[0] - point(t1 - step, 0.0)[0]) / (2 * step)
    return level, slope**2


def scale_fit(excess: list[float], profile: list[float], null_variance: list[float]) -> dict[str, Any]:
    """One nonnegative scale of a profile against the excesses; variance (vb + scale * profile)^2 per point."""
    scale = 0.0
    for _ in range(FIT_ITERATIONS):
        weight = [1 / (v + scale * p) ** 2 for v, p in zip(null_variance, profile, strict=True)]
        denominator = sum(w * p * p for w, p in zip(weight, profile, strict=True))
        if denominator <= 0:
            break
        scale = max(0.0, sum(w * e * p for w, e, p in zip(weight, excess, profile, strict=True)) / denominator)
    weight = [1 / (v + scale * p) ** 2 for v, p in zip(null_variance, profile, strict=True)]
    chi = sum(w * (e - scale * p) ** 2 for w, e, p in zip(weight, excess, profile, strict=True))
    dof = len(excess) - 1
    return {
        "scale": scale,
        "chi_square": chi,
        "dof": dof,
        "probability": case.base.chi_square_probability(chi, dof),
    }


class QubitExcess:
    """Test 1 for one qubit: per-multiplier excess and profiles, and the two one-scale fits."""

    def __call__(self, rep: Replicates) -> dict[str, Any]:
        size = len(MULTIPLIERS)
        means = [mean(rep.x[m]) for m in range(size)]
        s2 = [sum((x - means[m]) ** 2 for x in rep.x[m]) / (ROUNDS - 1) for m in range(size)]
        vb = [mean(rep.vb[m]) for m in range(size)]
        fit = case.fit_shape([(rep.t_us[m], means[m], vb[m] / ROUNDS) for m in range(size)], "single")
        t1 = float(fit["params"][0])
        rows = []
        for m in range(size):
            level, moving = profile_pair(rep.t_us[m], t1, mean(rep.a0[m]), mean(rep.a1[m]), rep.count)
            rows.append(
                {
                    "multiplier": MULTIPLIERS[m],
                    "x_mean": means[m],
                    "replicate_variance": s2[m],
                    "binomial_variance": vb[m],
                    "excess": s2[m] - vb[m],
                    "excess_variance": s2[m] ** 2 / 2,
                    "level_profile": level,
                    "t1_profile": moving,
                }
            )
        excess = [r["excess"] for r in rows]
        level_fit = scale_fit(excess, [r["level_profile"] for r in rows], vb)
        moving_fit = scale_fit(excess, [r["t1_profile"] for r in rows], vb)
        neither = level_fit["probability"] < LACK_OF_FIT and moving_fit["probability"] < LACK_OF_FIT
        return {
            "qubit": rep.qubit,
            "t1_us": t1,
            "per_multiplier": rows,
            "level_shift": level_fit | {"tau": math.sqrt(level_fit["scale"])},
            "moving_t1": moving_fit
            | {"sigma_t_us": math.sqrt(moving_fit["scale"]), "sigma_t_over_t": math.sqrt(moving_fit["scale"]) / t1},
            "neither_fits": neither,
        }


def pooled_level(rows: list[dict[str, Any]], indices: tuple[int, ...]) -> dict[str, Any]:
    """U, SE and Z of the pooled level estimate over the qubits' rows at the given multiplier indices."""
    numerator = denominator = variance = 0.0
    for row in rows:
        for m in indices:
            cell = row["per_multiplier"][m]
            c = cell["level_profile"]
            weight = c * c / cell["binomial_variance"] ** 2
            numerator += weight * cell["excess"] / c
            denominator += weight
            variance += weight**2 * cell["excess_variance"] / (c * c)
    estimate = numerator / denominator
    se = math.sqrt(variance) / denominator
    return {
        "multipliers": [MULTIPLIERS[m] for m in indices],
        "terms": len(rows) * len(indices),
        "tau_squared": estimate,
        "se": se,
        "z": estimate / se,
    }


def level_verdict(z: float) -> dict[str, str]:
    if z > Z_DECISION:
        return {"level_shift": "survives", "moving_t1": "falsified", "reading": "excess above 3 SE at 8 and 12 T"}
    if z >= -Z_DECISION:
        return {"level_shift": "falsified", "moving_t1": "survives", "reading": "excess consistent with zero"}
    return {"level_shift": "falsified", "moving_t1": "falsified", "reading": "variance below the binomial part"}


def run_test1(reps: list[Replicates]) -> dict[str, Any]:
    rows = ordered_map(QubitExcess(), reps, min_items=2)
    pooled = pooled_level(rows, LONG_MULTIPLIERS)
    by_multiplier = [pooled_level(rows, (m,)) for m in range(len(MULTIPLIERS))]
    return {
        "decision_multipliers": pooled["multipliers"],
        "pooled": pooled,
        "verdict": level_verdict(pooled["z"]),
        "pooled_by_multiplier": by_multiplier,
        "qubits_where_neither_fits": [r["qubit"] for r in rows if r["neither_fits"]],
        "qubits": rows,
    }


def residual_matrix(x: np.ndarray) -> np.ndarray:
    """Qubits by (multiplier, round) readings to residuals about the multiplier mean, each row scaled to unit RMS."""
    grouped = x.reshape(x.shape[0], len(MULTIPLIERS), ROUNDS)
    residual = (grouped - grouped.mean(axis=2, keepdims=True)).reshape(x.shape[0], -1)
    rms = np.sqrt((residual**2).mean(axis=1))
    keep = rms > 0
    return np.asarray(residual[keep] / rms[keep, None])


def leading_fraction(residual: np.ndarray) -> float:
    covariance = residual.T @ residual / residual.shape[0]
    return float(np.linalg.eigvalsh(covariance)[-1] / np.trace(covariance))


class NullStatistic:
    """Leading eigenvalue fraction of permutation k: round labels shuffled per qubit within each multiplier group."""

    def __init__(self, residual: np.ndarray, seed: int) -> None:
        self.grouped = residual.reshape(residual.shape[0], len(MULTIPLIERS), ROUNDS)
        self.seed = seed

    def __call__(self, k: int) -> float:
        rng = random.Random(f"{self.seed}:{k}")
        shuffled = np.empty_like(self.grouped)
        order = list(range(ROUNDS))
        for q in range(self.grouped.shape[0]):
            for g in range(self.grouped.shape[1]):
                rng.shuffle(order)
                shuffled[q, g] = self.grouped[q, g, order]
        return leading_fraction(shuffled.reshape(self.grouped.shape[0], -1))


def run_test2(x: np.ndarray, permutations: int, qubits: list[int]) -> dict[str, Any]:
    residual = residual_matrix(x)
    observed = leading_fraction(residual)
    null = np.array(ordered_map(NullStatistic(residual, seed64()), list(range(permutations))))
    p_value = (1 + int((null >= observed).sum())) / (1 + permutations)
    covariance = residual.T @ residual / residual.shape[0]
    values, vectors = np.linalg.eigh(covariance)
    leading = vectors[:, -1] * (1 if vectors[np.argmax(np.abs(vectors[:, -1])), -1] > 0 else -1)
    labels = [f"m{MULTIPLIERS[m]}-r{r}" for m in range(len(MULTIPLIERS)) for r in range(ROUNDS)]
    return {
        "statistic": "leading eigenvalue fraction of the batch covariance across qubits",
        "qubits_used": residual.shape[0],
        "qubits_in_series": qubits,
        "batches": residual.shape[1],
        "observed": observed,
        "second_fraction": float(values[-2] / values.sum()),
        "permutations": permutations,
        "null_mean": float(null.mean()),
        "null_quantile_95": float(np.quantile(null, 0.95)),
        "null_quantile_99": float(np.quantile(null, 0.99)),
        "null_maximum": float(null.max()),
        "p_value": p_value,
        "verdict": {
            "common_disturbance": "survives" if p_value <= P_DECISION else "falsified",
            "independent_residuals": "falsified" if p_value <= P_DECISION else "survives",
        },
        "leading_eigenvector": dict(zip(labels, [float(v) for v in leading], strict=True)),
        "seed_draw": DRAW,
        "seed_indices": [0, 1, 2, 3],
        "seed_values": list(PERMUTATION_SEEDS),
    }


def ladder_reading(u: Any, phi: Any) -> np.ndarray:
    """P at the three pulse counts for u = gamma * 256 and phi = dtheta * 32 (arrays broadcast on the last axis)."""
    n = np.array(LADDER_PULSES, dtype=float)
    u_a, phi_a = np.asarray(u, dtype=float)[..., None], np.asarray(phi, dtype=float)[..., None]
    return np.asarray(0.5 * (1 + np.exp(-u_a * n / 256) * np.cos(phi_a * n / 32)))


def ladder_grid() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    u, phi = np.meshgrid(np.linspace(0, U_MAX, U_POINTS), np.linspace(0, math.pi, PHI_POINTS), indexing="ij")
    return u.ravel(), phi.ravel(), ladder_reading(u.ravel(), phi.ravel())


class PartnerSearch:
    """For one truth (u, phi): the distinct grid points inside the joint region of its noiseless reading."""

    def __init__(self, se: list[float]) -> None:
        self.se = np.array(se)
        self.u, self.phi, self.reading = ladder_grid()

    def __call__(self, truth: tuple[float, float]) -> dict[str, Any]:
        y = ladder_reading(truth[0], truth[1])
        chi = (((self.reading - y) / self.se) ** 2).sum(axis=1)
        distinct = (np.abs(self.u - truth[0]) >= DISTINCT_STEP) | (np.abs(self.phi - truth[1]) >= DISTINCT_STEP)
        inside = distinct & (chi < JOINT_CHI_SQUARE)
        return {
            "u": truth[0],
            "phi": truth[1],
            "partners": int(inside.sum()),
            "closest_distinct_chi_square": float(chi[distinct].min()),
        }


def identifiability(se: list[float]) -> dict[str, Any]:
    truths = [(float(u), float(p)) for u in np.linspace(0, U_MAX, 7) for p in np.linspace(0, math.pi, 16)]
    rows = ordered_map(PartnerSearch(se), truths, min_items=2)
    fraction = sum(r["partners"] > 0 for r in rows) / len(rows)
    sign = float(np.abs(ladder_reading(1.0, 0.7) - ladder_reading(1.0, -0.7)).max())
    alias = float(np.abs(ladder_reading(1.0, 0.7) - ladder_reading(1.0, 0.7 + 2 * math.pi)).max())
    return {
        "se": se,
        "truths": len(rows),
        "fraction_with_partner": fraction,
        "identifiable": fraction <= IDENTIFIABLE_FRACTION,
        "exact_symmetry_max_reading_difference": {"sign_of_dtheta": sign, "dtheta_plus_2pi_over_32": alias},
        "truth_rows": rows,
    }


class LadderFit:
    """Grid fit of one three-reading ladder: the (u, phi) of least chi-square and its value (one degree of freedom)."""

    def __init__(self, se: list[float]) -> None:
        self.se = np.array(se)
        self.u, self.phi, self.reading = ladder_grid()

    def __call__(self, readings: list[float]) -> dict[str, float]:
        chi = (((self.reading - np.array(readings)) / self.se) ** 2).sum(axis=1)
        best = int(np.argmin(chi))
        return {"u": float(self.u[best]), "phi": float(self.phi[best]), "chi_square": float(chi[best])}


def record_se(record: dict[str, Any]) -> dict[str, Any]:
    """Standard error of a ladder value per pulse count from the record's contrasts: |difference| / |z| / sqrt(2)."""
    out: dict[str, Any] = {}
    for pulses in LADDER_PULSES:
        found = []
        for row in record["crosstalk"]["rows"]:
            if row["unit"] != f"x90-{pulses}" or "half_value" not in row or abs(row["z"]) <= MIN_RECORD_Z:
                continue
            found.append(abs(row["half_value"] - row["all_value"]) / abs(row["z"]) / math.sqrt(2))
        if not found:
            raise ValueError(f"no usable x90-{pulses} rows")
        found.sort()
        out[str(pulses)] = {"se": found[len(found) // 2], "rows": len(found), "min": found[0], "max": found[-1]}
    return out


def ladder_fits(record: dict[str, Any], se: list[float]) -> list[dict[str, Any]]:
    values: dict[tuple[str, int], dict[str, dict[int, float]]] = {}
    for row in record["crosstalk"]["rows"]:
        if not row["unit"].startswith("x90-") or "half_value" not in row:
            continue
        slot = values.setdefault((row["context"], row["qubit"]), {"half": {}, "all": {}})
        pulses = int(row["unit"].split("-")[1])
        slot["half"][pulses] = row["half_value"]
        slot["all"][pulses] = row["all_value"]
    keys = sorted(k for k, v in values.items() if all(len(v[d]) == len(LADDER_PULSES) for d in v))
    items = [[values[k][d][n] for n in LADDER_PULSES] for k in keys for d in ("half", "all")]
    fits = ordered_map(LadderFit(se), items, min_items=2)
    return [
        {"context": k[0], "qubit": k[1], "drive": d, **fits[2 * i + j]}
        for i, k in enumerate(keys)
        for j, d in enumerate(("half", "all"))
    ]


def run_test3(record: dict[str, Any]) -> dict[str, Any]:
    ses = record_se(record)
    se = [ses[str(n)]["se"] for n in LADDER_PULSES]
    scan = identifiability(se)
    verdict: dict[str, Any]
    if scan["identifiable"]:
        verdict = {"ladder_model": "identifiable", "fits": ladder_fits(record, se)}
    else:
        verdict = {"ladder_model": "not decidable from the retained data (issue 941)", "fits": "none: nothing fitted"}
    return {"record_se": ses, "scan": scan} | verdict


# Synthetic series for the self-test: a SHA-256 stream with a normal shape (twelve uniforms), no random generator.


def gauss(tag: str) -> float:
    digest = hashlib.sha256(tag.encode()).digest()
    return sum((b + 0.5) / 256 for b in digest[:12]) - 6.0


def synthetic_batches(
    level_tau: float, t1_relative: float, nqubits: int = 17, count: int = 8192
) -> list[dict[str, Any]]:
    """Interleaved batches in read_batches's layout with per-job level shifts (sd level_tau), a T1 that moves between
    rounds (relative sd t1_relative, one value per qubit and round) and binomial noise of the shot count."""
    e0, e1 = 0.03, 0.95
    batches = []
    for r in range(ROUNDS):
        for m, multiplier in enumerate(MULTIPLIERS):
            delays = [round(multiplier * case.PLATEAU_T_US[q] * case.CYCLES_PER_US) for q in range(nqubits)]
            reading: dict[str, list[float]] = {"a0": [], "a1": [], "t": []}
            for q in range(nqubits):
                t1 = case.PLATEAU_T_US[q] * (1 + t1_relative * gauss(f"T-{q}-{r}"))
                t_us = delays[q] * case.CYCLE_SECONDS * 1e6
                truth = {"a0": e0, "a1": e1, "t": e0 + (e1 - e0) * math.exp(-t_us / t1)}
                for job, level in truth.items():
                    tag = f"{q}-{r}-{m}-{job}"
                    p = level + level_tau * gauss(f"L-{tag}")
                    p += math.sqrt(max(p * (1 - p), 1e-6) / count) * gauss(f"B-{tag}")
                    reading[job].append(min(1.0, max(0.0, p)))
            batches.append(
                {
                    "run": f"synthetic-{r}-{m}",
                    "arm": "interleaved_t1",
                    "meta": {"round": r, "multiplier": multiplier},
                    "shots": count,
                    "nqubits": nqubits,
                    "rows": {
                        "a0": {"kind": "anchor0"},
                        "a1": {"kind": "anchor1"},
                        "t": {"kind": "t1", "delays_cycles": delays},
                    },
                    "p1": reading,
                }
            )
    return batches


def series_of(batches: list[dict[str, Any]]) -> tuple[list[Replicates], list[int]]:
    roles = [case.interleaved_roles(b) for b in batches]
    found = [(q, replicates(batches, roles, q)) for q in range(batches[0]["nqubits"])]
    return [r for _, r in found if r is not None], [q for q, r in found if r is None]


def matrix_of(reps: list[Replicates]) -> np.ndarray:
    return np.array([[rep.x[m][r] for m in range(len(MULTIPLIERS)) for r in range(ROUNDS)] for rep in reps])


def check(condition: bool, message: str, problems: list[str]) -> None:
    if not condition:
        problems.append(message)


def self_test() -> list[str]:
    problems: list[str] = []
    level = run_test1(series_of(synthetic_batches(0.015, 0.0))[0])
    moving = run_test1(series_of(synthetic_batches(0.0, 0.15))[0])
    check(level["pooled"]["z"] > Z_DECISION, f"planted level shift: Z {level['pooled']['z']:.2f} <= 3", problems)
    check(level["verdict"]["level_shift"] == "survives", "planted level shift: verdict not level shift", problems)
    check(
        abs(moving["pooled"]["z"]) <= Z_DECISION,
        f"planted moving T1: |Z| {abs(moving['pooled']['z']):.2f} > 3",
        problems,
    )
    check(moving["verdict"]["moving_t1"] == "survives", "planted moving T1: verdict not moving T1", problems)
    mean_level_tau = mean([q["level_shift"]["tau"] for q in level["qubits"]])
    check(0.008 < mean_level_tau < 0.03, f"planted tau 0.015 fitted as {mean_level_tau:.4f}", problems)
    mean_sigma_t = mean([q["moving_t1"]["sigma_t_over_t"] for q in moving["qubits"]])
    check(0.05 < mean_sigma_t < 0.4, f"planted sigma_T/T 0.15 fitted as {mean_sigma_t:.4f}", problems)

    # Test 2: a disturbance common to the batches against independent noise, 17 qubits by 18 batches.
    columns = len(MULTIPLIERS) * ROUNDS
    common = np.array(
        [[0.03 * gauss(f"C-{b}") + 0.01 * gauss(f"N-{q}-{b}") for b in range(columns)] for q in range(17)]
    )
    independent = np.array([[0.03 * gauss(f"I-{q}-{b}") for b in range(columns)] for q in range(17)])
    positive = run_test2(common, SELF_TEST_PERMUTATIONS, list(range(17)))
    null = run_test2(independent, SELF_TEST_PERMUTATIONS, list(range(17)))
    check(positive["p_value"] <= P_DECISION, f"planted common disturbance: p {positive['p_value']}", problems)
    check(null["p_value"] > P_DECISION, f"independent noise: p {null['p_value']} <= 0.01", problems)

    # Test 3: identifiability at tiny and at large standard errors, and a grid fit of a planted truth.
    tight = identifiability([1e-5] * 3)
    loose = identifiability([0.05] * 3)
    check(tight["identifiable"], f"se 1e-5: fraction {tight['fraction_with_partner']}", problems)
    check(not loose["identifiable"], f"se 0.05: fraction {loose['fraction_with_partner']}", problems)
    exact = tight["exact_symmetry_max_reading_difference"]
    check(max(exact.values()) < 1e-12, f"the exact symmetries differ by {exact}", problems)
    planted = (1.0, 120 * math.pi / (PHI_POINTS - 1))
    fit = LadderFit([1e-5] * 3)(ladder_reading(planted[0], planted[1]).tolist())
    check(abs(fit["u"] - planted[0]) < 1e-9 and abs(fit["phi"] - planted[1]) < 1e-9, f"planted fit {fit}", problems)
    return problems


def main(out: Path) -> None:
    problems = self_test()
    if problems:
        raise SystemExit("self-test failed: " + "; ".join(problems))
    runs = sorted((ROOT / RUNS).glob(PATTERN))
    if len(runs) != len(MULTIPLIERS) * ROUNDS:
        raise SystemExit(f"want {len(MULTIPLIERS) * ROUNDS} interleaved_t1 runs, found {len(runs)}")
    batches = case.read_batches(runs)
    reps, dropped = series_of(batches)
    record = json.loads((ROOT / ANALYSIS).read_text(encoding="utf-8"))
    result = {
        "schema": SCHEMA,
        "source": "scripts/qi_tuna17_interleaved_cases.py read_batches, interleaved_roles, anchored_point, fit_shape",
        "self_test": "passed",
        "runs": len(runs),
        "qubits_dropped_for_anchor_span": dropped,
        "test1_level_shift_against_moving_t1": run_test1(reps),
        "test2_common_batch_disturbance": run_test2(matrix_of(reps), PERMUTATIONS, [r.qubit for r in reps]),
        "test3_ladder_over_rotation": run_test3(record),
    }
    out.write_text(json.dumps(clean(result), indent=1, allow_nan=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        found = self_test()
        print("self-test: " + ("ok" if not found else "FAILED " + "; ".join(found)))
        raise SystemExit(1 if found else 0)
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(Path(sys.argv[1]))
