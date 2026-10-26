"""Preregistered decisions D1-D3 of an N=21 orbit window-dose sweep against its idle-padded exact model.

Data. The run directory holds the submitted record (record.json), the collected result (collect.json), the lossless
shot-ordered registers --collect writes under raw/<job_id>/, and the scheduled-idle replay (idle-replay.json from
`scripts/scheduled_idle_replay.py RUN --out RUN/idle-replay.json --dose-scales` with DOSE_SCALES): each replica's
exact branch-resolved law with the explicit doses and the service-scheduled idle charged under the execution
Target, at the Target's relaxation (exact_laws.idle_padded) and with the dose delays' relaxation multiplied by each
factor of DOSE_SCALES (dose_scaled_exact_laws). A collection whose group carries comparisons_withheld (its PUBs
did not all run under one calibration) is refused.

Estimates. Each member's PUB packs every replica, so one shot measures all replicas together. A shot enters a
replica's estimate when that replica's initialization herald reads all zeros, and the replay laws are conditioned
the same way. A member's per-replica mean score and the covariance across replicas come from the shot-ordered
registers by the delta method (Cov(m_r, m_q) = sum_s psi_rs psi_qs / S^2, psi the herald-conditioned influence), so
common-mode readout or crosstalk within a shot enters the variance. BATCHES contiguous blocks of shots test for
drift within the job: the mean ratio of each member's block dispersion to its shot variance, when above one,
multiplies every covariance. A contract's replica vector is the signed sum of its two members, whose PUBs are
independent; a pooled value is the replica mean with variance 1' C 1 / n^2.

Model. M_r(d; k) is replica r's exact contract value at dose d with the dose relaxation charged k times over (k = 1
is the Target's T1 and T2). The fits interpolate the replica mean, and each replica, in k by PCHIP over DOSE_SCALES
and 1.

Decisions (docs/design/n21-orbit-window-dose-envelope.md):
- D1, idle response: the pooled plain contrast at the largest dose lies below the dose-0 contrast at one-sided 95
  percent. A failure withholds evidence for the drop; it is no equivalence test.
- D2, plain rate: kappa_P, the dose-relaxation multiple that fits the six pooled plain responses measured(d) -
  measured(0) by generalized least squares with their covariance (the shared dose-0 arm included), with its 95
  percent profile interval (delta chi2 3.841). A dose-independent offset cancels in every response. The minimum
  chi2 on five degrees of freedom tests the one-rate shape; below p = 0.01 the dose response is one no single rate
  describes, and the interval is not read. Otherwise an interval that excludes 1 reads as plain idle loss at
  kappa_P times the Target's rate.
- D3, echo refocusing: kappa_P and kappa_E fitted jointly to the six plain and the six echo responses (echo(d) -
  plain(0)), with the 95 percent profile interval of delta = kappa_P - kappa_E and the joint chi2 on ten degrees of
  freedom under the same shape rule. A lower bound above zero reads as idle loss the Hahn echo removes beyond the
  Target model: quasi-static dephasing (a free-induction T2* below the Hahn-echo T2 the Target reports) or static
  detuning, which this design does not separate. An upper bound below zero reads as an echo that costs more than it
  refocuses. MIN_EFFECT is the smallest delta the envelope's replica floor is powered for.
- Each replica's kappa_P,r and its interval are reported, not decided.

Preflight. --preflight RECORD_DIR checks a fresh dry-run record against the approved envelope before it is
submitted: the full design projection (EXPECTED_DESIGN), the planning policy (EXPECTED_POLICY), one dynamic job of
one PUB per member, one routed candidate, an envelope backend, the replica floor and count, the shots, the
repetition delay, the ceilings and the commit. The calibration, layout and model values are the record's own; they
are what the fresh plan adapts.

Usage: "$PYTHON" scripts/n21_dose_decisions.py RUN_DIR [--out FILE]
       "$PYTHON" scripts/n21_dose_decisions.py --preflight RECORD_DIR [--head COMMIT]
       "$PYTHON" scripts/n21_dose_decisions.py --retry-check RUN_DIR
       "$PYTHON" scripts/n21_dose_decisions.py --self-test
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats
from scipy.interpolate import PchipInterpolator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

ONE_SIDED = float(stats.norm.ppf(0.95))
PROFILE_95 = float(stats.chi2.ppf(0.95, 1))
SHAPE_P = 0.01
BATCHES = 16
DOSE_SCALES = (0.25, 0.5, 0.75, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0)
FIT_STEP = 0.01
MIN_EFFECT = 0.3
NAME = re.compile(r"n21_orbit_window_dose(?P<echo>_echo)?_d(?P<dose>\d+)_feedback_contrast")

# The approved envelope a fresh dry-run record must carry (docs/design/n21-orbit-window-dose-envelope.md).
DESIGN_DOSES = [0, 1752, 3500, 5252, 7000, 10500, 14000]
DESIGN_SHOTS = 8192
DESIGN_REP_DELAYS = (2e-05, 5e-05)
DESIGN_CEILING_SECONDS = 30.0
DESIGN_MIN_REPLICAS = 4
DESIGN_REPLICA_FLOOR = 0.45
DESIGN_BACKENDS = {"ibm_fez", "ibm_kingston", "ibm_marrakesh"}
DESIGN_DRAW = "docs/evidence/anu_qrng/draw-2026-10-26T092449Z.json"
DESIGN_DRAW_SHA256 = "df2c0e24a5cf12120dc4739a2565a30d413de562df3c5e05d2bda562f0d8fe85"
DESIGN_SEED_SOURCES = {
    "--seed-transpiler": ["qrng:docs/evidence/anu_qrng/draw-2026-10-26T092449Z.json#0"],
    "--seed-simulator": ["qrng:docs/evidence/anu_qrng/draw-2026-10-26T092449Z.json#1"],
}
EXPECTED_DESIGN: dict[str, Any] = {
    "alpha": 0.05,
    "classical_latency_us": 20.0,
    "cost_scenarios": [],
    "family": "n21-orbit-rca",
    "init_herald": True,
    "job_overhead_seconds": 2.3,
    "max_total_execution_seconds": DESIGN_CEILING_SECONDS,
    "model_method": "sampled",
    "model_shots": 32768,
    "objective": "minimum_charge",
    "optimize": True,
    "optimizer_candidates": 1,
    "patch_qubits": None,
    "power": 0.8,
    "precision": 0.09,
    "replica_tiers": [24],
    "replica_variance_bound": None,
    "reserve_seconds": 0.0,
    "shot_allocation": "uniform",
    "shot_tiers": [DESIGN_SHOTS],
    "simulation_alpha": 0.01,
    "window_doses": DESIGN_DOSES,
}
EXPECTED_POLICY: dict[str, Any] = {
    "max_readout_error": 0.08,
    "max_cz_error": 0.03,
    "max_sx_error": 0.01,
    "min_t1_us": 20.0,
    "min_t2_us": 20.0,
    "max_pending": 200,
    "seeds": 8,
    "joint_candidates": 3,
    "replica_floor": DESIGN_REPLICA_FLOOR,
    "max_replicas": None,
    "isolated_reference": False,
    "cross_group_buffer": True,
    "twirl": False,
    "dd": None,
    "min_remaining_seconds": 60.0,
    "max_execution_seconds": 30,
    "seed_transpiler": DESIGN_SEED_SOURCES["--seed-transpiler"][0],
    "seed_simulator": DESIGN_SEED_SOURCES["--seed-simulator"][0],
    "operator_excluded_qubits": {},
}

Estimate = tuple[np.ndarray, np.ndarray]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def arms(names: Sequence[str]) -> tuple[list[int], dict[int, str], dict[int, str]]:
    """Sorted doses with each dose's plain and echo contract names."""
    plain: dict[int, str] = {}
    echo: dict[int, str] = {}
    for name in names:
        match = NAME.fullmatch(name)
        if match is None:
            continue
        (echo if match["echo"] else plain)[int(match["dose"])] = name
    doses = sorted(plain)
    require(len(doses) >= 3 and doses[0] == 0, f"a dose sweep needs dose 0 and two more plain arms, not {doses}")
    require(set(echo) == set(doses[1:]), f"echo arms {sorted(echo)} do not match the nonzero doses {doses[1:]}")
    return doses, plain, echo


def member_moments(keep: np.ndarray, scores: np.ndarray, batches: int = BATCHES) -> dict[str, Any]:
    """Herald-conditioned replica means, their delta-method covariance and the block dispersion ratio.

    keep and scores are (shots, replicas): whether the shot's herald admits it for that replica, and its score.
    """
    shots, _ = keep.shape
    kept = keep.sum(axis=0)
    require(bool((kept > 0).all()), "a replica keeps no shot")
    weighted = scores * keep
    means = weighted.sum(axis=0) / kept
    psi = keep * (scores - means) / (kept / shots)
    covariance = psi.T @ psi / shots**2
    pooled_variance = float(covariance.sum()) / means.size**2
    # A block in which some replica keeps no shot carries no estimate of that replica and is skipped.
    blocks = []
    count = min(batches, shots)
    for index in np.array_split(np.arange(shots), count):
        block_kept = keep[index].sum(axis=0)
        if bool((block_kept > 0).all()):
            blocks.append(float((weighted[index].sum(axis=0) / block_kept).mean()))
    used = len(blocks)
    dispersion = float(np.var(blocks, ddof=1)) / (count * pooled_variance) if used >= 2 and pooled_variance > 0 else 1.0
    return {"means": means, "covariance": covariance, "dispersion": dispersion, "kept": kept, "blocks": used}


def conditioned_value(law: Sequence[float], values: Sequence[float], phase_bits: int) -> float:
    """The score's expectation under law given an all-zero herald (outcome index below 2**phase_bits)."""
    law_array = np.asarray(law, dtype=float)
    require(law_array.size == len(values), "a law and its score vector differ in length")
    head = law_array[: 1 << phase_bits]
    require(head.sum() > 0, "the law gives the all-zero herald no weight")
    return float(np.asarray(values, dtype=float)[: 1 << phase_bits] @ head / head.sum())


def measured_from_raw(run_dir: Path, record: Mapping[str, Any], collected_laws: Mapping[str, Any]) -> dict[str, Any]:
    """{member: member_moments} from the shot-ordered registers, after binding them to the collected marginals."""
    import law_encoding
    import n21_exact_planning

    contracts = [c for c in record["observable_contracts"] if NAME.fullmatch(c["name"])]
    scores = {term["member"]: law_encoding.dense(term["values"]) for c in contracts for term in c["terms"]}
    components = {}
    for pub in record["execution_pubs"]:
        require(len(pub["components"]) == 1, f"{pub['name']}: a dose PUB holds one member")
        components[pub["components"][0]["member"]] = (pub["name"], pub["components"][0]["registers_by_replica"])
    registers = n21_exact_planning.retained_registers(run_dir, {pub for pub, _ in components.values()})
    out: dict[str, Any] = {}
    for member, values in scores.items():
        pub_name, replicas = components[member]
        require(pub_name in registers, f"{pub_name}: no retained shot-ordered registers")
        keep_columns, score_columns = [], []
        for r, names in enumerate(replicas):
            outcomes = n21_exact_planning.replica_outcomes(registers[pub_name], names)
            frequency = np.bincount(outcomes, minlength=len(values)) / outcomes.size
            marginal = np.asarray(law_encoding.dense(collected_laws[member][r]), dtype=float)
            require(
                np.allclose(frequency, marginal / marginal.sum(), rtol=0.0, atol=1e-12),
                f"{member} replica {r}: register frequencies differ from the collected marginal",
            )
            phase_bits = len(registers[pub_name][names[0]][0])
            keep_columns.append(outcomes >> phase_bits == 0)
            score_columns.append(np.asarray(values, dtype=float)[outcomes])
        moments = member_moments(np.stack(keep_columns, axis=1).astype(float), np.stack(score_columns, axis=1))
        moments["phase_bits"] = phase_bits
        out[member] = moments
    return out


def contract_estimates(
    contracts: Sequence[Mapping[str, Any]], moments: Mapping[str, Mapping[str, Any]]
) -> dict[str, Estimate]:
    """{contract: (replica vector, covariance)}: the signed sum of its members, whose PUBs are independent.

    Each member's covariance is multiplied by its own block dispersion ratio when that exceeds one, so drift in one
    PUB widens that PUB's arms and no other's.
    """
    out: dict[str, Estimate] = {}
    for contract in contracts:
        members = [term["member"] for term in contract["terms"]]
        require(len(set(members)) == len(members), f"{contract['name']}: a member enters twice")
        vector = sum(term["sign"] * moments[term["member"]]["means"] for term in contract["terms"])
        covariance = sum(
            max(1.0, moments[term["member"]]["dispersion"]) * moments[term["member"]]["covariance"]
            for term in contract["terms"]
        )
        out[contract["name"]] = (np.asarray(vector, dtype=float), np.asarray(covariance, dtype=float))
    return out


def contract_models(
    contracts: Sequence[Mapping[str, Any]], replay: Mapping[str, Any], phase_bits: Mapping[str, int]
) -> dict[str, dict[float, np.ndarray]]:
    """{contract: {k: replica vector of herald-conditioned exact values}}; an undosed contract holds k = 1 only."""
    import law_encoding

    base = replay["exact_laws"]["idle_padded"]
    scaled = replay.get("dose_scaled_exact_laws", {})
    out: dict[str, dict[float, np.ndarray]] = {}
    for contract in contracts:
        dose = int(NAME.fullmatch(contract["name"])["dose"])  # type: ignore[index]
        sources = {1.0: base} | ({float(k): scaled[k] for k in scaled} if dose else {})
        if dose:
            require({float(k) for k in scaled} >= set(DOSE_SCALES), f"idle-replay.json lacks the scales {DOSE_SCALES}")
        family: dict[float, np.ndarray] = {}
        for k, laws in sources.items():
            terms = []
            for term in contract["terms"]:
                values = law_encoding.dense(term["values"])
                bits = phase_bits[term["member"]]
                terms.append(
                    term["sign"] * np.asarray([conditioned_value(law, values, bits) for law in laws[term["member"]]])
                )
            family[k] = np.sum(terms, axis=0)
        out[contract["name"]] = family
    return out


def interpolated(family: Mapping[float, np.ndarray], grid: np.ndarray) -> np.ndarray:
    """(len(grid), replicas): each replica's model over grid, PCHIP in k; an undosed model is constant in k."""
    ks = sorted(family)
    if len(ks) == 1:
        return np.repeat(family[ks[0]][None, :], grid.size, axis=0)
    table = np.stack([family[k] for k in ks])
    return np.asarray(PchipInterpolator(np.asarray(ks), table, axis=0)(grid))


def profile_interval(grid: np.ndarray, chi2: np.ndarray) -> dict[str, Any]:
    """The minimum and the 95 percent profile interval, its limits interpolated linearly to the threshold crossing.

    A limit that reaches the grid's end is censored: the interval extends past the grid and the estimate is not read.
    """
    best = int(np.argmin(chi2))
    level = chi2[best] + PROFILE_95
    inside = np.flatnonzero(chi2 <= level)
    lo, hi = int(inside[0]), int(inside[-1])

    def crossing(a: int, b: int) -> float:
        # chi2[a] > level >= chi2[b]: the linear crossing between grid[a] and grid[b].
        return float(grid[a] + (grid[b] - grid[a]) * (chi2[a] - level) / (chi2[a] - chi2[b]))

    censored = lo == 0 or hi == grid.size - 1
    return {
        "estimate": float(grid[best]),
        "lower": float(grid[0]) if lo == 0 else crossing(lo - 1, lo),
        "upper": float(grid[-1]) if hi == grid.size - 1 else crossing(hi + 1, hi),
        "contiguous": bool(hi - lo + 1 == inside.size),
        "censored": bool(censored),
        "chi2_min": float(chi2[best]),
    }


def response_covariance(variances: Sequence[float], shared: float) -> np.ndarray:
    """Covariance of responses y_i = arm_i - plain(0): independent arms plus the shared dose-0 variance."""
    return np.diag(np.asarray(variances, dtype=float)) + shared


def decide(measured: Mapping[str, Estimate], models: Mapping[str, Mapping[float, np.ndarray]]) -> dict[str, Any]:
    """D1-D3 from each contract's (replica vector, covariance) and its exact model family."""
    doses, plain, echo = arms(list(measured))
    nonzero = doses[1:]
    n = {vector.size for vector, _ in measured.values()}
    require(len(n) == 1, f"contracts hold different replica counts {sorted(n)}")
    replicas = n.pop()
    grid = np.round(np.arange(min(DOSE_SCALES), max(DOSE_SCALES) + FIT_STEP / 2, FIT_STEP), 10)
    mean = {name: float(vector.mean()) for name, (vector, _) in measured.items()}
    var = {name: float(cov.sum()) / replicas**2 for name, (_, cov) in measured.items()}
    model_mean = {name: interpolated(family, grid).mean(axis=1) for name, family in models.items()}
    at_one = int(np.argmin(np.abs(grid - 1.0)))
    out: dict[str, Any] = {
        "doses_dt": doses,
        "replicas": replicas,
        "intervals": "conditional on the execution Target's per-qubit T1 and T2 point values",
        "arms": {
            name: {
                "measured": mean[name],
                "sigma": math.sqrt(var[name]),
                "model_at_target": float(model_mean[name][at_one]),
            }
            for name in measured
        },
    }
    zero = plain[0]
    drop = mean[plain[doses[-1]]] - mean[zero]
    drop_sigma = math.sqrt(var[plain[doses[-1]]] + var[zero])
    out["d1_idle_response"] = {
        "difference": drop,
        "sigma": drop_sigma,
        "upper": drop + ONE_SIDED * drop_sigma,
        "holds": drop + ONE_SIDED * drop_sigma < 0,
    }
    y_plain = np.asarray([mean[plain[d]] - mean[zero] for d in nonzero])
    r_plain = np.stack([model_mean[plain[d]] - model_mean[zero] for d in nonzero], axis=1)
    c_plain = response_covariance([var[plain[d]] for d in nonzero], var[zero])
    w_plain = np.linalg.inv(c_plain)
    residual = y_plain[None, :] - r_plain
    chi2_plain = np.einsum("ki,ij,kj->k", residual, w_plain, residual)
    fit = profile_interval(grid, chi2_plain)
    shape_p = float(stats.chi2.sf(fit["chi2_min"], len(nonzero) - 1))
    if fit["censored"] or not fit["contiguous"]:
        verdict = "withheld: the profile interval of kappa_P reaches the edge of the fitted range or splits"
    elif shape_p < SHAPE_P:
        verdict = "no single dose-relaxation rate describes the plain dose response"
    elif fit["lower"] > 1.0 or fit["upper"] < 1.0:
        verdict = "plain idle loss at kappa_P times the Target's rate, the interval excluding 1"
    else:
        verdict = "plain idle loss consistent with the Target's rate"
    out["d2_plain_rate"] = fit | {"shape_p": shape_p, "verdict": verdict}

    y_echo = np.asarray([mean[echo[d]] - mean[zero] for d in nonzero])
    r_echo = np.stack([model_mean[echo[d]] - model_mean[zero] for d in nonzero], axis=1)
    c_joint = response_covariance([var[plain[d]] for d in nonzero] + [var[echo[d]] for d in nonzero], var[zero])
    w = np.linalg.inv(c_joint)
    k = len(nonzero)
    a = y_plain[None, :] - r_plain
    b = y_echo[None, :] - r_echo
    joint = (
        np.einsum("ki,ij,kj->k", a, w[:k, :k], a)[:, None]
        + 2 * a @ w[:k, k:] @ b.T
        + np.einsum("ki,ij,kj->k", b, w[k:, k:], b)[None, :]
    )
    offsets = np.arange(-(grid.size - 1), grid.size)
    profile = np.asarray([np.diagonal(joint, offset=-o).min() for o in offsets])
    delta = offsets * FIT_STEP
    difference = profile_interval(delta, profile)
    i, j = np.unravel_index(int(np.argmin(joint)), joint.shape)
    joint_p = float(stats.chi2.sf(float(joint[i, j]), 2 * k - 2))
    kappa_p = profile_interval(grid, joint.min(axis=1))
    kappa_e = profile_interval(grid, joint.min(axis=0))
    supported = not any(x["censored"] or not x["contiguous"] for x in (kappa_p, kappa_e, difference))
    if not supported:
        verdict = "withheld: a profile interval of kappa_P, kappa_E or their difference reaches the fitted range's edge"
    elif joint_p < SHAPE_P:
        verdict = "no pair of dose-relaxation rates describes the plain and echo dose responses"
    elif difference["lower"] > 0:
        verdict = "the Hahn echo removes idle loss beyond the Target model: quasi-static dephasing or static detuning"
    elif difference["upper"] < 0:
        verdict = "the echo costs more than it refocuses"
    else:
        verdict = "unresolved: the interval of kappa_P - kappa_E contains 0"
    out["d3_echo_refocusing"] = {
        "kappa_p": kappa_p,
        "kappa_e": kappa_e,
        "delta": difference,
        "joint_shape_p": joint_p,
        "minimum_effect": MIN_EFFECT,
        "verdict": verdict,
    }

    per_replica = []
    zero_models = interpolated(models[zero], grid)
    plain_models = {d: interpolated(models[plain[d]], grid) for d in nonzero}
    for r in range(replicas):
        y = np.asarray([measured[plain[d]][0][r] - measured[zero][0][r] for d in nonzero])
        model = np.stack([plain_models[d][:, r] - zero_models[:, r] for d in nonzero], axis=1)
        c = response_covariance([measured[plain[d]][1][r, r] for d in nonzero], measured[zero][1][r, r])
        res = y[None, :] - model
        per_replica.append(profile_interval(grid, np.einsum("ki,ij,kj->k", res, np.linalg.inv(c), res)))
    out["kappa_p_per_replica"] = per_replica
    return out


def analyze(run_dir: Path) -> dict[str, Any]:
    record = json.loads((run_dir / "record.json").read_text(encoding="utf-8"))
    collected = json.loads((run_dir / "collect.json").read_text(encoding="utf-8"))
    replay = json.loads((run_dir / "idle-replay.json").read_text(encoding="utf-8"))
    groups = [g for g in collected if isinstance(g, dict) and "measured" in g]
    require(len(groups) == 1, f"{run_dir}: collect.json holds {len(groups)} measured groups, not one")
    # The collector withholds comparisons across PUBs whose calibration differed or changed during their shots
    # (live_run._comparisons_withheld); a dose response read across such PUBs would include the calibration change.
    withheld = groups[0].get("comparisons_withheld")
    require(withheld is None, f"{run_dir}: the collector withheld the sweep's comparisons: {withheld}")
    contracts = [c for c in record["observable_contracts"] if NAME.fullmatch(c["name"])]
    moments = measured_from_raw(run_dir, record, groups[0]["measured"])
    ratios = {member: m["dispersion"] for member, m in moments.items()}
    df = sum(m["blocks"] - 1 for m in moments.values())
    statistic = sum((m["blocks"] - 1) * m["dispersion"] for m in moments.values())
    measured = contract_estimates(contracts, moments)
    models = contract_models(contracts, replay, {member: m["phase_bits"] for member, m in moments.items()})
    out = decide(measured, models)
    out["drift"] = {
        "batches": BATCHES,
        "dispersion_ratio": ratios,
        "chi2": statistic,
        "df": df,
        "p": float(stats.chi2.sf(statistic, df)),
    }
    out["herald_kept_fraction"] = {
        member: (m["kept"] / int(record["shots"])).round(6).tolist() for member, m in moments.items()
    }
    out["run"] = run_dir.name
    out["model_source"] = "idle-replay.json exact_laws.idle_padded and dose_scaled_exact_laws, herald-conditioned"
    return out


def preflight(record_dir: Path, head: str | None = None) -> dict[str, Any]:
    """The fresh record's binding facts, after requiring every invariant of the approved envelope."""
    record = json.loads((record_dir / "record.json").read_text(encoding="utf-8"))
    policy = record["policy"]
    design = policy["design"]
    require(record["state"] == "planned", f"{record_dir}: state {record['state']}, not planned")
    require(design == EXPECTED_DESIGN, f"design {design} differs from the envelope's {EXPECTED_DESIGN}")
    planning = {key: policy.get(key) for key in EXPECTED_POLICY}
    require(planning == EXPECTED_POLICY, f"planning policy {planning} differs from the envelope's {EXPECTED_POLICY}")
    require(int(record["shots"]) == DESIGN_SHOTS, f"shots {record['shots']}, not {DESIGN_SHOTS}")
    require(policy.get("rep_delay_seconds") in DESIGN_REP_DELAYS, f"repetition delay {policy.get('rep_delay_seconds')}")
    optimization = record["optimization"]
    require(optimization.get("searched_routed_sets") == 1, "the plan searched more than one routed candidate set")
    chosen = [c for c in optimization["candidates"] if c["name"] == optimization["selected"]]
    require(len(chosen) == 1 and chosen[0]["feasible"], "the record selects no feasible candidate")
    charge = float(chosen[0]["estimated_charge_seconds"])
    require(charge <= DESIGN_CEILING_SECONDS, f"estimated charge {charge} s exceeds the ceiling")
    groups = record["groups"]
    require(len(groups) == 1, f"{len(groups)} groups")
    replicas = len(groups[0]["replicas"])
    require(replicas >= DESIGN_MIN_REPLICAS, f"{replicas} replicas, below the design's {DESIGN_MIN_REPLICAS}")
    require(groups[0]["backend"] in DESIGN_BACKENDS, f"backend {groups[0]['backend']} lies outside the envelope")
    members = 2 * (2 * len(DESIGN_DOSES) - 1)
    pubs = record.get("execution_pubs") or []
    require(
        len(pubs) == members and all(len(pub["components"]) == 1 for pub in pubs),
        f"{len(pubs)} PUBs, not one per each of the {members} members",
    )
    jobs = [(job.get("kind"), job.get("pubs")) for job in record.get("budget_plan", {}).get("jobs", [])]
    require(jobs == [("dynamic", members)], f"jobs {jobs}, not one dynamic job of {members} PUBs")
    sources = {row["flag"]: row["sources"] for row in record.get("seed_source") or []}
    require(sources == DESIGN_SEED_SOURCES, f"seed sources {sources}")
    draw_bytes = (ROOT / DESIGN_DRAW).read_bytes()
    require(hashlib.sha256(draw_bytes).hexdigest() == DESIGN_DRAW_SHA256, f"{DESIGN_DRAW} differs from its bound bytes")
    values = json.loads(draw_bytes)["values"]
    require(record.get("seed_simulator") == values[1], "the simulator seed is not the draw's index 1")
    offset = int(groups[0]["seed_transpiler"]) - int(values[0])
    require(0 <= offset < int(EXPECTED_POLICY["seeds"]), "the layout seed is not among the draw's index-0 seeds")
    commit = record.get("code_commit") or {}
    require(commit.get("sources_modified") is False, "the plan was made from a modified source tree")
    if head is not None:
        require(commit.get("head") == head, f"the plan was made at {commit.get('head')}, not the checked-out {head}")
    return {
        "record": record_dir.name,
        "backend": groups[0]["backend"],
        "calibration": groups[0]["calibration"],
        "replicas": replicas,
        "rep_delay_seconds": policy["rep_delay_seconds"],
        "estimated_charge_seconds": charge,
    }


def retry_check(run_dir: Path) -> dict[str, Any]:
    """The facts that admit the envelope's single 50 us retry after the 20 us run in run_dir.

    The run must be a submitted window-dose sweep at a 20 us repetition delay whose one job ended in error 1305 with
    no PUB timing (no shot executed), and the retry must be unused (retry-consumed.json absent).
    """
    record = json.loads((run_dir / "record.json").read_text(encoding="utf-8"))
    collected = json.loads((run_dir / "collect.json").read_text(encoding="utf-8"))
    policy = record["policy"]
    require(record.get("state") == "submitted", f"{run_dir} is a {record.get('state')} record, not a submission")
    require(policy["design"] == EXPECTED_DESIGN, f"{run_dir} is not the envelope's dose sweep")
    require({key: policy.get(key) for key in EXPECTED_POLICY} == EXPECTED_POLICY, f"{run_dir} departs from the policy")
    require(policy.get("rep_delay_seconds") == DESIGN_REP_DELAYS[0], f"{run_dir} did not run at 20 us")
    submitted = [job.get("job_id") for job in record.get("submission", {}).get("jobs", [])]
    groups = [entry for entry in collected if isinstance(entry, dict) and "jobs" in entry]
    require(len(groups) == 1, f"{run_dir} holds {len(groups)} collection entries with jobs")
    jobs = groups[0]["jobs"]
    require(
        len(jobs) == 1 and list(jobs) == submitted, f"collected jobs {list(jobs)} are not the submitted {submitted}"
    )
    job_id, job = next(iter(jobs.items()))
    require(job["usage"]["job_status"] == "ERROR", f"{job_id} ended {job['usage']['job_status']}")
    require("Error code 1305" in str(job.get("result_unavailable", "")), f"{job_id} did not end in error 1305")
    require(not job.get("pub_timing"), f"{job_id} executed PUBs before it failed")
    require(not (run_dir / "retry-consumed.json").exists(), f"the retry after {run_dir} is spent")
    return {"run": run_dir.name, "job_id": job_id, "charged_seconds": job["usage"].get("qpu_charge_time_seconds")}


def synthetic_sweep(
    kappa_p: float, kappa_e: float, replicas: int = 6, sigma: float = 0.006, wobble: float = 0.0
) -> tuple[dict[str, Estimate], dict[str, dict[float, np.ndarray]]]:
    """Measured estimates at the given true rates and their exponential model family, for the self-test."""
    amplitude = np.linspace(0.17, 0.23, replicas)
    floor = np.linspace(-0.01, 0.01, replicas)
    scales = (1.0, *DOSE_SCALES)

    def curve(d: int, k: float, tau: float) -> np.ndarray:
        return np.asarray(amplitude * math.exp(-k * d / tau) + floor)

    measured: dict[str, Estimate] = {}
    models: dict[str, dict[float, np.ndarray]] = {}
    for d in DESIGN_DOSES:
        for name, tau, k in (
            (f"n21_orbit_window_dose_d{d}_feedback_contrast", 9000.0, kappa_p),
            (f"n21_orbit_window_dose_echo_d{d}_feedback_contrast", 14000.0, kappa_e),
        ):
            if "echo" in name and not d:
                continue
            models[name] = {s: curve(d, s, tau) for s in scales} if d else {1.0: curve(0, 1.0, tau)}
            shift = wobble * math.sin(d / 1500.0) if "echo" not in name else 0.0
            measured[name] = (curve(d, k, tau) + shift, sigma**2 * np.eye(replicas))
    return measured, models


def self_test() -> str:
    target = decide(*synthetic_sweep(1.0, 1.0))
    require(target["d1_idle_response"]["holds"], f"a Target-rate sweep shows no drop: {target['d1_idle_response']}")
    rate = target["d2_plain_rate"]
    require(
        rate["lower"] <= 1.0 <= rate["upper"] and rate["verdict"].startswith("plain idle loss consistent"), f"{rate}"
    )
    require(target["d3_echo_refocusing"]["verdict"].startswith("unresolved"), f"{target['d3_echo_refocusing']}")
    refocused = decide(*synthetic_sweep(1.9, 1.2))
    rate = refocused["d2_plain_rate"]
    require(abs(rate["estimate"] - 1.9) < 0.02 and rate["lower"] > 1.0, f"kappa_P 1.9 reads {rate}")
    d3 = refocused["d3_echo_refocusing"]
    require(abs(d3["delta"]["estimate"] - 0.7) < 0.03 and d3["verdict"].startswith("the Hahn echo"), f"{d3}")
    common = decide(*synthetic_sweep(1.5, 1.5))
    require(common["d2_plain_rate"]["lower"] > 1.0, f"a common rate 1.5 reads {common['d2_plain_rate']}")
    require(common["d3_echo_refocusing"]["verdict"].startswith("unresolved"), f"{common['d3_echo_refocusing']}")
    wobbly = decide(*synthetic_sweep(1.0, 1.0, wobble=0.05))
    require(wobbly["d2_plain_rate"]["verdict"].startswith("no single"), f"an oscillating plain arm reads {wobbly}")
    measured, models = synthetic_sweep(1.0, 1.0)
    flat = {
        name: (np.full_like(vector, float(measured["n21_orbit_window_dose_d0_feedback_contrast"][0].mean())), cov)
        for name, (vector, cov) in measured.items()
    }
    require(not decide(flat, models)["d1_idle_response"]["holds"], "a flat sweep shows an idle response")
    beyond = decide(*synthetic_sweep(7.0, 1.0))
    require(beyond["d2_plain_rate"]["verdict"].startswith("withheld"), f"kappa_P 7 reads {beyond['d2_plain_rate']}")
    require(beyond["d3_echo_refocusing"]["verdict"].startswith("withheld"), f"{beyond['d3_echo_refocusing']}")
    return (
        "n21 dose decisions: Target-rate, refocused (1.9 against 1.2), common-rate, oscillating, flat and "
        "beyond-range sweeps decide as stated"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run_dir", type=Path, nargs="?")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--preflight", type=Path, metavar="RECORD_DIR")
    parser.add_argument("--head", help="with --preflight: the commit the plan must have been made at")
    parser.add_argument("--retry-check", type=Path, metavar="RUN_DIR")
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
        return 0
    if args.retry_check is not None:
        print(json.dumps(retry_check(args.retry_check), sort_keys=True))
        return 0
    if args.preflight is not None:
        print(json.dumps(preflight(args.preflight, args.head), sort_keys=True))
        return 0
    if args.run_dir is None:
        parser.error("a run directory or --self-test is required")
    text = json.dumps(analyze(args.run_dir), indent=1, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
