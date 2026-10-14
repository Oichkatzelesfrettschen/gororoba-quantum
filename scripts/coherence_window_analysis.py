"""Analysis of a collected coherence-window run: branch-signed work coherence per context.

Counts bind to the submission through patch_window_analysis._bound_counts
(record, raw ledger, PUB manifest and circuit archive digests). Two layers:

- Preregistered: the five precision endpoints of
  coherence_window.coherence_contracts, evaluated by
  experiment_optimizer.analyze_observations with the planner's grouped
  Hoeffding bounds, from the record's own contracts and PUB grouping.
- Descriptive: per context, C = (S_XX + S_YY + i (S_XY - S_YX)) / 4 with
  S_PQ = E[(-1)^(b0 + a + b)], its modulus and argument, the rotation and
  modulus ratio between adjacent contexts, the branch-unsigned coherence (the
  negative control, zero on an ideal device), and the ZZ setting's one-hot
  and spectator-sector populations.
- Timing: each context's executed exposure of each work qubit
  (free-precession time of the physical qubits read into the work clbits,
  from the record's readout_qubits map and the returned scheduler timing),
  per Pauli setting and averaged over them, and each job's execution
  timestamps. The relative phase of the work pair advances as
  delta_B t_B - delta_A t_A, a signed combination of the two qubits'
  exposures, so the measure_reset rotation is corrected by the part of its
  exposure change that is collinear with the idle-versus-immediate change;
  the orthogonal part and the per-setting departures enter a bias bound at
  the design's aliasing detuning, pi over the window, and every idle winding
  that bound admits gives a candidate. The correction crosses
  jobs, so it bounds a measurement-induced phase only together with the
  jobs' execution times; timestamps record provenance and correct no drift.
- Inference: each +-1 score has the Laplace-adjusted per-shot variance
  4 p (1 - p), p the adjusted fraction of +1 outcomes, and circuits are
  independent. Re C and Im C come from disjoint settings, so their joint
  region is the ellipse re^2/var_re + im^2/var_im <= chi2_2; an argument is
  reported only where that region at family-wise level FAMILY_ALPHA over
  the contexts excludes the origin, with the region's angular extent as its
  phase region. Comparison and correction intervals are 95 percent normal
  (delta method) per quantity.

Usage: "$PYTHON" scripts/coherence_window_analysis.py RUN_DIR [--out FILE]
       "$PYTHON" scripts/coherence_window_analysis.py --self-check
"""

from __future__ import annotations

import argparse
import cmath
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
from coherence_window import (  # noqa: E402
    CLBITS,
    COHERENCE_PRECISION,
    CONTEXTS,
    PAULI_SETTINGS,
    READ_A,
    READ_B,
    SECTOR,
    coherence_circuit,
    coherence_contracts,
    signed_parity,
    unsigned_parity,
)
from experiment_optimizer import (  # noqa: E402
    ObservableContract,
    ObservableTerm,
    ObservedPub,
    analyze_observations,
)
from patch_characterization import WORK_B  # noqa: E402

Z95 = 1.959963984540054
FAMILY_ALPHA = 0.05
# Chi-square(2) survival is exp(-x / 2): one origin test per context at FAMILY_ALPHA / len(CONTEXTS).
CHI2_IDENTIFY = -2.0 * math.log(FAMILY_ALPHA / len(CONTEXTS))


def _estimate(dist: np.ndarray, shots: int, score: tuple[float, ...]) -> tuple[float, float]:
    """Mean of a +-1 score and its variance over shots independent shots.

    The variance uses the Laplace-adjusted fraction (n p + 1) / (n + 2) of +1
    outcomes, 4 p (1 - p) / n, which stays positive when every shot agrees, so
    the joint region and its angular extent remain defined at saturation.
    """
    mean = float(np.asarray(score) @ dist)
    adjusted = (shots * (1 + mean) / 2 + 1) / (shots + 2)
    return mean, 4 * adjusted * (1 - adjusted) / shots


def context_coherence(
    dists: dict[str, np.ndarray], shots: dict[str, int], context: str, score: tuple[float, ...]
) -> dict[str, Any]:
    s = {
        p: _estimate(dists[f"coherence_{context}_{p}"], shots[f"coherence_{context}_{p}"], score)
        for p in PAULI_SETTINGS
    }
    re, im = (s["xx"][0] + s["yy"][0]) / 4, (s["xy"][0] - s["yx"][0]) / 4
    var_re, var_im = (s["xx"][1] + s["yy"][1]) / 16, (s["xy"][1] + s["yx"][1]) / 16
    modulus = math.hypot(re, im)
    var_mod = (re * re * var_re + im * im * var_im) / modulus**2 if modulus > 0 else var_re + var_im
    statistic = re * re / var_re + im * im / var_im if var_re > 0 and var_im > 0 else 0.0
    out: dict[str, Any] = {
        "re": re,
        "im": im,
        "re_ci": [re - Z95 * math.sqrt(var_re), re + Z95 * math.sqrt(var_re)],
        "im_ci": [im - Z95 * math.sqrt(var_im), im + Z95 * math.sqrt(var_im)],
        "modulus": modulus,
        "modulus_ci": [modulus - Z95 * math.sqrt(var_mod), modulus + Z95 * math.sqrt(var_mod)],
        "origin_statistic": statistic,
        "origin_threshold": CHI2_IDENTIFY,
        "_var": (var_re, var_im),
    }
    if statistic > CHI2_IDENTIFY:
        arg = math.atan2(im, re)
        out["argument"] = arg
        out["argument_region"] = list(angular_extent(re, im, var_re, var_im, CHI2_IDENTIFY))
        out["_var_arg"] = (re * re * var_im + im * im * var_re) / modulus**4
    return out


def _wrap(angle: float) -> float:
    return (angle + math.pi) % (2 * math.pi) - math.pi


def angular_extent(re: float, im: float, var_re: float, var_im: float, level: float) -> tuple[float, float]:
    """Angles of the two rays from the origin tangent to the joint region, unwrapped around arg C.

    The region (x - re)^2 / var_re + (y - im)^2 / var_im <= level becomes a unit
    disc centered at (re / sa, im / sb) after scaling by sa = sqrt(level var_re)
    and sb = sqrt(level var_im); that positive diagonal map keeps rays from the
    origin and their order, so the tangent directions phi0 -+ asin(1 / R) map
    back to the region's angular extent, which spans less than pi.
    """
    sa, sb = math.sqrt(level * var_re), math.sqrt(level * var_im)
    a, b = re / sa, im / sb
    radius = math.hypot(a, b)
    if radius <= 1.0:
        raise ValueError("the joint region contains the origin")
    center, half = math.atan2(b, a), math.asin(1.0 / radius)
    arg = math.atan2(im, re)
    lo, hi = (
        arg + _wrap(math.atan2(sb * math.sin(phi), sa * math.cos(phi)) - arg) for phi in (center - half, center + half)
    )
    return lo, hi


def compare(later: dict[str, Any], earlier: dict[str, Any]) -> dict[str, Any]:
    """Rotation arg(C_later / C_earlier) and modulus ratio, where both arguments are defined."""
    if "argument" not in later or "argument" not in earlier:
        return {"rotation": None, "reason": "a modulus interval reaches zero; the argument is undefined"}
    rotation = cmath.phase(complex(later["re"], later["im"]) / complex(earlier["re"], earlier["im"]))
    half = Z95 * math.sqrt(later["_var_arg"] + earlier["_var_arg"])
    ratio = later["modulus"] / earlier["modulus"]
    var_ratio = ratio**2 * (
        ((later["modulus_ci"][1] - later["modulus"]) / Z95 / later["modulus"]) ** 2
        + ((earlier["modulus_ci"][1] - earlier["modulus"]) / Z95 / earlier["modulus"]) ** 2
    )
    return {
        "rotation": rotation,
        "rotation_ci": [rotation - half, rotation + half],
        "modulus_ratio": ratio,
        "modulus_ratio_ci": [ratio - Z95 * math.sqrt(var_ratio), ratio + Z95 * math.sqrt(var_ratio)],
    }


def _setting_deviation(exposure: dict[str, Any]) -> float:
    """Sum over the two work qubits of the largest per-setting departure from their mean exposure."""
    per_setting = exposure.get("per_setting")
    if not per_setting:
        return 0.0
    means = (exposure["read_a"], exposure["read_b"])
    return sum(max(abs(pair[q] - means[q]) for pair in per_setting.values()) for q in (0, 1))


def _setting_bias(coherence: dict[str, Any], exposure: dict[str, Any], detuning_bound: float) -> float | None:
    """Bound on a context's argument shift from setting-specific exposure, or None when it is unbounded.

    Each Pauli setting's pair rotation departs from the mean-exposure rotation
    by at most eps = detuning_bound * _setting_deviation. That moves Re C and
    Im C each by at most (|C| + 1/2) eps, the 1/2 bounding the even coherence
    rho_00,11 that enters XX and YY with opposite signs, so the argument moves
    by at most asin(sqrt2 (|C| + 1/2) eps / |C|), evaluated at the lower end of
    the modulus interval. A ratio of 1 or more leaves the argument unbounded.
    """
    eps = detuning_bound * _setting_deviation(exposure)
    if eps == 0.0:
        return 0.0
    lower = coherence["modulus_ci"][0]
    if lower <= 0.0:
        return None
    ratio = math.sqrt(2.0) * (lower + 0.5) * eps / lower
    return math.asin(ratio) if ratio < 1.0 else None


def _holds_multiple_of_2pi(lo: float, hi: float) -> bool:
    return math.floor(hi / (2 * math.pi)) >= math.ceil(lo / (2 * math.pi))


def excess_rotation(
    signed: dict[str, dict[str, Any]], exposure: dict[str, dict[str, Any]], detuning_bound: float
) -> dict[str, Any] | None:
    """measure_reset rotation net of the idle rotation carried over along the collinear part of its exposure change.

    The pair phase is w . (t_A, t_B) with w = (-delta_A, delta_B) and each
    |delta| at most detuning_bound. With d_idle = t_mi - t_imm and
    d_win = t_mr - t_mi per qubit, k = (d_win . d_idle) / |d_idle|^2 and
    o = d_win - k d_idle, the value arg C_mr - (1 + k) arg C_mi + k arg C_imm
    equals the measurement-induced phase plus w . o, so |w . o| <=
    detuning_bound (|o_A| + |o_B|) bounds that bias; each context's
    setting-specific exposure adds its _setting_bias with weight (1, 1 + k,
    |k|). The measured idle rotation is known only modulo 2 pi while the true
    one can reach detuning_bound (|d_idle_A| + |d_idle_B|), so every winding n
    within that reach gives a candidate value - 2 pi k n. Both comparisons
    contain the matched idle, so its argument variance enters once with weight
    (1 + k)^2: Var = v_mr + (1 + k)^2 v_mi + k^2 v_imm. A phase is attributed
    only when every candidate interval, widened by the bias bound, excludes
    every multiple of 2 pi.
    """
    if any("argument" not in signed[context] for context in CONTEXTS):
        return None
    t = {c: np.array([exposure[c]["read_a"], exposure[c]["read_b"]], dtype=float) for c in CONTEXTS}
    d_idle = t["matched_idle"] - t["immediate"]
    d_win = t["measure_reset"] - t["matched_idle"]
    if float(d_idle.mean()) <= 0.05:
        return None
    k = float(d_win @ d_idle) / float(d_idle @ d_idle)
    orthogonal = d_win - k * d_idle
    setting_bias = {c: _setting_bias(signed[c], exposure[c], detuning_bound) for c in CONTEXTS}
    weights = {"measure_reset": 1.0, "matched_idle": abs(1.0 + k), "immediate": abs(k)}
    value_of = {context: complex(signed[context]["re"], signed[context]["im"]) for context in CONTEXTS}
    idle = cmath.phase(value_of["matched_idle"] / value_of["immediate"])
    window = cmath.phase(value_of["measure_reset"] / value_of["matched_idle"])
    value = window - k * idle
    variance = (
        signed["measure_reset"]["_var_arg"]
        + (1 + k) ** 2 * signed["matched_idle"]["_var_arg"]
        + k**2 * signed["immediate"]["_var_arg"]
    )
    reach = detuning_bound * float(np.abs(d_idle).sum()) + Z95 * math.sqrt(
        signed["matched_idle"]["_var_arg"] + signed["immediate"]["_var_arg"]
    )
    span = math.ceil(reach / (2 * math.pi)) + 1
    windings = [n for n in range(-span, span + 1) if abs(idle + 2 * math.pi * n) <= reach]
    candidates = [value - 2 * math.pi * k * n for n in windings]
    out: dict[str, Any] = {
        "idle_rate_rad_per_us": idle / float(d_idle.mean()),
        "collinear_ratio": k,
        "orthogonal_exposure_us": orthogonal.tolist(),
        "setting_deviation_us": {c: _setting_deviation(exposure[c]) for c in CONTEXTS},
        "detuning_bound_rad_per_us": detuning_bound,
        "idle_windings": windings,
        "excess_rotation": value,
        "excess_candidates": candidates,
    }
    if any(bias is None for bias in setting_bias.values()):
        out.update(attributed=False, withheld="setting-specific exposure leaves a context's argument unbounded")
        return out
    bias = detuning_bound * float(np.abs(orthogonal).sum()) + sum(
        weights[c] * (setting_bias[c] or 0.0) for c in CONTEXTS
    )
    half = Z95 * math.sqrt(variance) + bias
    out.update(
        bias_bound_rad=bias,
        excess_rotation_ci=[value - half, value + half],
        candidate_intervals=[[v - half, v + half] for v in candidates],
    )
    if not windings:
        out.update(attributed=False, withheld="no idle winding fits the detuning bound")
        return out
    out["attributed"] = not any(_holds_multiple_of_2pi(v - half, v + half) for v in candidates)
    return out


def populations(dist: np.ndarray) -> dict[str, float]:
    one_hot = sum(float(p) for o, p in enumerate(dist) if ((o >> READ_A) ^ (o >> READ_B)) & 1)
    sector = sum(float(p) for o, p in enumerate(dist) if not (o >> SECTOR) & 1)
    return {"one_hot": one_hot, "spectator_ground": sector}


def analyze(
    dists: dict[str, np.ndarray],
    shots: dict[str, int],
    contracts: tuple[ObservableContract, ...],
    pubs: dict[str, list[str]],
    exposure: dict[str, dict[str, Any]] | None = None,
    jobs: list[dict[str, Any]] | None = None,
    detuning_bound: float | None = None,
) -> dict[str, Any]:
    observed = tuple(
        ObservedPub(name, {member: (tuple(float(x) for x in dists[member]),) for member in members}, shots[members[0]])
        for name, members in pubs.items()
    )
    prereg = analyze_observations(observed, contracts)
    signed = {c: context_coherence(dists, shots, c, signed_parity()) for c in CONTEXTS}
    unsigned = {c: context_coherence(dists, shots, c, unsigned_parity()) for c in CONTEXTS}
    comparisons = {
        "matched_idle_vs_immediate": compare(signed["matched_idle"], signed["immediate"]),
        "measure_reset_vs_matched_idle": compare(signed["measure_reset"], signed["matched_idle"]),
    }
    result: dict[str, Any] = {
        "preregistered": [
            {"name": row.name, "estimate": row.estimate, "interval": [row.lo, row.hi], "alpha": row.alpha}
            for row in prereg.observables
        ],
        "signed_coherence": {c: {k: v for k, v in s.items() if not k.startswith("_")} for c, s in signed.items()},
        "comparisons": comparisons,
        "unsigned_coherence_negative_control": {
            c: {k: u[k] for k in ("re", "im", "re_ci", "im_ci")} for c, u in unsigned.items()
        },
        "zz_populations": {c: populations(dists[f"coherence_{c}_zz"]) for c in CONTEXTS},
        "executed_exposure_us": exposure,
        "jobs": jobs,
        "identification": {"family_alpha": FAMILY_ALPHA, "contexts": len(CONTEXTS), "chi2_2_threshold": CHI2_IDENTIFY},
    }
    if exposure is not None and detuning_bound is not None:
        result["measure_reset_net_of_idle_detuning"] = excess_rotation(signed, exposure, detuning_bound)
    return result


def from_run(run: Path) -> dict[str, Any]:
    from patch_window_analysis import _bound_counts, executed_idle_us

    from adjudicate import latest_metrics

    record = json.loads((run / "record.json").read_text())
    counts = _bound_counts(run)
    configuration = record["family_configuration"]
    readout = configuration["readout_qubits"]
    work = (readout["read_a"], readout["read_b"])
    # A static detuning above pi over the window aliases, so the design resolves rotations only below it.
    detuning_bound = math.pi / (configuration["window_dt"] * configuration["dt_seconds"] * 1e6)
    exposure: dict[str, dict[str, Any]] | None = {}
    for context in CONTEXTS:
        per_setting = {
            setting: [
                executed_idle_us(f"coherence_{context}_{setting}", qubit, configuration["dt_seconds"]) for qubit in work
            ]
            for setting in PAULI_SETTINGS
        }
        if exposure is None or any(v is None for pair in per_setting.values() for v in pair):
            exposure = None
            continue
        exposure[context] = {
            "read_a": float(np.mean([pair[0] for pair in per_setting.values()])),
            "read_b": float(np.mean([pair[1] for pair in per_setting.values()])),
            "per_setting": per_setting,
        }
    jobs = []
    for job in record["submission"]["jobs"]:
        # The index names the newest metrics snapshot and its digest; reading
        # through it keeps the reported timing bound to the raw evidence.
        raw_dir = run / "raw" / job["job_id"]
        metrics = latest_metrics(raw_dir, json.loads((raw_dir / "index.json").read_text()))
        jobs.append(
            {
                "job_id": job["job_id"],
                "kind": job["kind"],
                "members": job["members"],
                "timestamps": metrics.get("timestamps"),
            }
        )
    dists, shots = {}, {}
    for member, counter in counts.items():
        total = sum(counter.values())
        vector = np.zeros(1 << CLBITS)
        for bits, n in counter.items():
            vector[int(bits, 2)] += n
        dists[member], shots[member] = vector / total, total
    contracts = tuple(
        ObservableContract(
            c["name"],
            tuple(ObservableTerm(t["member"], tuple(t["values"]), t["sign"]) for t in c["terms"]),
            c["null_value"],
            c["minimum_effect"],
            c["alpha"],
            c["power"],
            c["precision_half_width"],
        )
        for c in record["observable_contracts"]
    )
    pubs = {pub["name"]: [component["member"] for component in pub["components"]] for pub in record["execution_pubs"]}
    return analyze(dists, shots, contracts, pubs, exposure, jobs, detuning_bound)


def self_check() -> None:
    from qiskit.circuit import CircuitInstruction
    from qiskit.circuit.library import RZGate

    from qpe_diagnostics import ideal_branch_probabilities

    rng = np.random.default_rng(20261014)
    rotation, shrink, epsilon, shots = 0.25, 0.8, 0.05, 400_000
    dists, sizes = {}, {}
    for context in CONTEXTS:
        for setting in (*PAULI_SETTINGS, "zz"):
            circuit = coherence_circuit(context, setting, 1000)
            if context == "measure_reset":
                index = next(i for i, op in enumerate(circuit.data) if op.operation.name == "reset")
                circuit.data.insert(index + 1, CircuitInstruction(RZGate(rotation), (circuit.qubits[WORK_B],)))
            law = np.asarray(ideal_branch_probabilities(circuit), dtype=float)
            if context != "immediate":
                # Dephasing shrinks the work coherence: mix toward the fully dephased law.
                law = shrink * law + (1 - shrink) * _dephased(law, setting)
            flipped = (1 - epsilon) * law
            for outcome, p in enumerate(law):
                flipped[outcome ^ 1] += epsilon * p
            name = f"coherence_{context}_{setting}"
            dists[name], sizes[name] = rng.multinomial(shots, flipped) / shots, shots
    contracts = coherence_contracts(COHERENCE_PRECISION, 0.05, 0.8)
    pubs = {name: [name] for name in dists}
    result = analyze(dists, sizes, contracts, pubs)
    scale = 1 - 2 * epsilon
    immediate = result["signed_coherence"]["immediate"]
    if abs(immediate["modulus"] - 0.5 * scale) > 0.01:
        raise RuntimeError(f"immediate |C| {immediate['modulus']} differs from {0.5 * scale}")
    idle = result["comparisons"]["matched_idle_vs_immediate"]
    window = result["comparisons"]["measure_reset_vs_matched_idle"]
    if abs(idle["rotation"]) > 0.02 or abs(idle["modulus_ratio"] - shrink) > 0.02:
        raise RuntimeError(f"pure dephasing should shrink without rotating: {idle}")
    if abs(window["rotation"] - rotation) > 0.02 or abs(window["modulus_ratio"] - 1.0) > 0.03:
        raise RuntimeError(f"a window rotation should rotate without shrinking: {window}")
    for control in result["unsigned_coherence_negative_control"].values():
        if abs(control["re"]) > 0.01 or abs(control["im"]) > 0.01:
            raise RuntimeError("the branch-unsigned coherence should vanish")
    if [row["name"] for row in result["preregistered"]] != [c.name for c in contracts]:
        raise RuntimeError("the preregistered endpoints differ from the contracts")
    # An idle detuning of 0.1 rad/us on both qubits with 3.3 us of extra idle and
    # 0.4 us more exposure in measure_reset leaves no excess once the rate is
    # subtracted; distinct per-context variances fix the matched idle's
    # (1 + k)^2 weight, and collinear changes leave no bias.
    variances = {"immediate": 1e-4, "matched_idle": 4e-4, "measure_reset": 9e-4}
    arguments = {"immediate": 0.0, "matched_idle": 0.33, "measure_reset": 0.37}
    signed = {
        c: {"re": math.cos(a), "im": math.sin(a), "argument": a, "_var_arg": variances[c]} for c, a in arguments.items()
    }
    equal = {
        c: {"read_a": t, "read_b": t} for c, t in (("immediate", 1.0), ("matched_idle", 4.3), ("measure_reset", 4.7))
    }
    detuned = excess_rotation(signed, equal, 0.94)
    k = 0.4 / 3.3
    half = Z95 * math.sqrt(
        variances["measure_reset"] + (1 + k) ** 2 * variances["matched_idle"] + k**2 * variances["immediate"]
    )
    if (
        detuned is None
        or abs(detuned["excess_rotation"]) > 1e-12
        or abs(detuned["idle_rate_rad_per_us"] - 0.1) > 1e-12
        or detuned["bias_bound_rad"] > 1e-12
        or abs(detuned["excess_rotation_ci"][1] - half) > 1e-12
        or detuned["attributed"]
    ):
        raise RuntimeError(f"the idle-detuning correction is wrong: {detuned}")
    _check_signed_exposure()
    _check_identification(rng)


def _phases(rates: tuple[float, float], exposure: dict[str, dict[str, Any]], window_phase: float) -> dict[str, Any]:
    """Noise-free signed coherences whose pair phase is delta_B t_B - delta_A t_A, plus a phase in measure_reset."""
    out = {}
    for c in CONTEXTS:
        phase = rates[1] * exposure[c]["read_b"] - rates[0] * exposure[c]["read_a"]
        phase += window_phase if c == "measure_reset" else 0.0
        out[c] = {
            "re": math.cos(phase),
            "im": math.sin(phase),
            "argument": math.atan2(math.sin(phase), math.cos(phase)),
            "modulus_ci": [0.99, 1.01],
            "_var_arg": 1e-8,
        }
    return out


def _check_signed_exposure() -> None:
    """Unequal per-qubit exposure changes are not misread as a measurement-induced phase."""
    rates, bound = (0.1, 0.3), 0.94
    # Immediate (0, 0), matched idle (1, 1), measure_reset (2, 0) us: the scalar
    # average sees no window excess and reports -0.4 rad with no measurement phase.
    skewed = {
        "immediate": {"read_a": 0.0, "read_b": 0.0},
        "matched_idle": {"read_a": 1.0, "read_b": 1.0},
        "measure_reset": {"read_a": 2.0, "read_b": 0.0},
    }
    result = excess_rotation(_phases(rates, skewed, 0.0), skewed, bound)
    if result is None or result["attributed"] or abs(result["bias_bound_rad"] - 2 * bound) > 1e-12:
        raise RuntimeError(f"an orthogonal exposure change was attributed to the measurement: {result}")
    lo, hi = result["excess_rotation_ci"]
    if not lo < 0.0 < hi:
        raise RuntimeError(f"the widened interval must contain the true zero phase: {result}")
    # Collinear changes with a real 0.3 rad window phase: attributed and recovered.
    collinear = {
        "immediate": {"read_a": 1.0, "read_b": 1.5},
        "matched_idle": {"read_a": 3.0, "read_b": 4.5},
        "measure_reset": {"read_a": 3.4, "read_b": 5.1},
    }
    result = excess_rotation(_phases(rates, collinear, 0.3), collinear, bound)
    if result is None or not result["attributed"] or abs(result["excess_rotation"] - 0.3) > 1e-9:
        raise RuntimeError(f"a collinear exposure change hid the window phase: {result}")
    # Rates (-0.8, 0.8) rad/us over equal exposures 1/4.3/4.7 us rotate the idle
    # pair by 5.28 rad, which wraps to -1.00; the wrapped value times k = 0.4/3.3
    # alone reads 0.76 rad with no measurement phase, and the 5.28 rad winding
    # the bound admits returns zero.
    equal = {
        c: {"read_a": t, "read_b": t} for c, t in (("immediate", 1.0), ("matched_idle", 4.3), ("measure_reset", 4.7))
    }
    result = excess_rotation(_phases((-0.8, 0.8), equal, 0.0), equal, bound)
    if result is None or result["attributed"] or len(result["idle_windings"]) < 2:
        raise RuntimeError(f"a wrapped idle rotation was attributed to the measurement: {result}")
    # Setting-specific exposure: measure_reset's B exposure 1 us shorter for XX
    # and YY and 1 us longer for XY and YX leaves the mean, and k = 0, unchanged
    # while it can flip the reconstructed coherence; attribution is withheld.
    flipped: dict[str, dict[str, Any]] = {
        "immediate": {"read_a": 1.0, "read_b": 1.0},
        "matched_idle": {"read_a": 2.0, "read_b": 2.0},
        "measure_reset": {
            "read_a": 2.0,
            "read_b": 2.0,
            "per_setting": {"xx": [2.0, 1.0], "yy": [2.0, 1.0], "xy": [2.0, 3.0], "yx": [2.0, 3.0]},
        },
    }
    result = excess_rotation(_phases((0.0, 0.9), flipped, 0.0), flipped, bound)
    if result is None or result["attributed"] or "withheld" not in result:
        raise RuntimeError(f"setting-specific exposure was attributed to the measurement: {result}")


def _two_outcome(score: tuple[float, ...], plus: np.ndarray, shots: int) -> list[np.ndarray]:
    """Distributions on one +1 and one -1 outcome of score with plus/shots weight on the +1 outcome."""
    up, down = score.index(1), score.index(-1)
    out = []
    for count in plus:
        dist = np.zeros(len(score))
        dist[up], dist[down] = count / shots, 1 - count / shots
        out.append(dist)
    return out


def _simulate(rng: np.random.Generator, coherence: complex, shots: int, trials: int) -> list[dict[str, Any]]:
    """context_coherence on trials independent data sets whose settings average to the given C."""
    score = tuple(float(x) for x in signed_parity())
    means = {"xx": 2 * coherence.real, "yy": 2 * coherence.real, "xy": 2 * coherence.imag, "yx": -2 * coherence.imag}
    draws = {p: _two_outcome(score, rng.binomial(shots, (1 + m) / 2, trials), shots) for p, m in means.items()}
    results = []
    for trial in range(trials):
        dists = {f"coherence_immediate_{p}": draws[p][trial] for p in PAULI_SETTINGS}
        sizes = {name: shots for name in dists}
        results.append(context_coherence(dists, sizes, "immediate", score))
    return results


def _check_identification(rng: np.random.Generator) -> None:
    """Null admission at the per-context level, coverage, and a phase region that wraps through pi."""
    trials, shots, level = 20_000, 2048, FAMILY_ALPHA / len(CONTEXTS)
    null = sum("argument" in r for r in _simulate(rng, 0j, shots, trials)) / trials
    tolerance = 4 * math.sqrt(level * (1 - level) / trials)
    if abs(null - level) > tolerance:
        raise RuntimeError(f"zero coherence admits an argument at rate {null}, not {level}")
    truth = math.pi - 0.01
    strong = _simulate(rng, cmath.rect(0.45, truth), shots, 2000)
    if not all("argument" in r for r in strong):
        raise RuntimeError("a coherence of 0.45 must identify its argument")
    covered = sum(
        r["argument_region"][0]
        <= truth + 2 * math.pi * round((r["argument"] - truth) / (2 * math.pi))
        <= r["argument_region"][1]
        for r in strong
    )
    if covered / len(strong) < 1 - level - 4 * math.sqrt(level * (1 - level) / len(strong)):
        raise RuntimeError(f"the phase region covers the true argument in {covered} of {len(strong)}")
    if not any(r["argument_region"][1] > math.pi or r["argument_region"][0] < -math.pi for r in strong):
        raise RuntimeError("a region straddling pi must extend past it rather than split")
    # Saturated XX and YY scores (every shot +1) with balanced XY and YX: C = 1/2.
    score = tuple(float(x) for x in signed_parity())
    plus = {"xx": shots, "yy": shots, "xy": shots // 2, "yx": shots // 2}
    dists = {f"coherence_immediate_{p}": _two_outcome(score, np.array([n]), shots)[0] for p, n in plus.items()}
    saturated = context_coherence(dists, {name: shots for name in dists}, "immediate", score)
    region = saturated.get("argument_region")
    if region is None or not region[0] < 0.0 < region[1] or abs(saturated["argument"]) > 1e-12:
        raise RuntimeError(f"a saturated coherence must identify a finite region around 0: {saturated}")


def _dephased(law: np.ndarray, setting: str) -> np.ndarray:
    """The law after full work dephasing: Pauli X/Y readouts of each work qubit become uniform."""
    if setting == "zz":
        return law
    out = np.zeros_like(law)
    for outcome, p in enumerate(law):
        for a in (0, 1):
            for b in (0, 1):
                moved = outcome & ~((1 << READ_A) | (1 << READ_B)) | (a << READ_A) | (b << READ_B)
                out[moved] += p / 4
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run", nargs="?", type=Path)
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    if args.self_check:
        self_check()
        print(
            "coherence window analysis: dephasing shrinks, a window phase rotates, the unsigned control vanishes, "
            "zero coherence identifies no argument above the family level, and unequal exposure changes are not "
            "attributed to the measurement"
        )
        return 0
    if args.run is None:
        parser.error("a collected run directory or --self-check is required")
    text = json.dumps(from_run(args.run), indent=1) + "\n"
    if args.out:
        args.out.write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
