"""Analysis and preregistered decision rule of the orientation-bit case.

The case is written in docs/design/pathion-kernel-map-orientation-bit.md.

The case asks whether the paired character gap lambda_16 - lambda_0 of the ibm_fez kernel map follows the orientation
qubit. For one operand it reads three units of group pathion_kernel_map_orientation over replicas (disjoint chip
regions): ctrl (orientation on bit 4), move (orientation on bit 1) and xtwin (ctrl with one X on data qubit 4 before
readout). Per replica, with lambda_a = c^_obs,a / c^_ideal,a on the Walsh support of the ideal contrast
(nhat_spectral.coefficients, nhat_spectral.unit_spectrum; this module reuses both):

    ctrl   G16  = lambda_16 - lambda_0
    move   G2   = lambda_2 - lambda_0            (character 2^b of the moved orientation bit b = 1)
    move   leak = c^_obs,16                      (character 16 lies outside the ideal support: leakage, ideal 0; it
                                                  needs a channel that is not character-diagonal, so it is reported
                                                  and tested but cannot decide the verdict)
    xtwin  G16  = lambda_16 - lambda_0 against the exchanged ideal
    S = (G16_ctrl + G16_xtwin) / 2               the part that keeps its sign under the exchange (follows the operand)
    D = (G16_ctrl - G16_xtwin) / 2               the part that flips its sign under the exchange
    C = G16_ctrl - G2_move                       zero when the gap moves with the orientation qubit at equal size

What D sees. The xtwin compiles to the control's schedule plus one virtual rz on the data-bit-4 wire after the SELECT
(identical cz sequence, identical measure mapping; tests/gororoba_quantum/test_pathion_kernel_map_orientation.py), so
D is zero under every error that acts before that frame, including the SELECT-decay hypothesis of row A5-242, and
responds only to an asymmetric readout of the bit-4 physical qubit or a coherent angle error on that wire's final
single-qubit tail. D isolates the readout-asymmetry half of the row's open "relaxation or asymmetric readout"
question; it does not resolve the relaxation half.

Each statistic is a one-sample t test over replicas with n - 1 degrees of freedom, whose standard error is the scatter
of the replica values, so the test holds whatever drift the device has between regions. Two operands and seven
statistics make the family of 14 tests; Holm's step-down procedure holds the family error at ALPHA.

Row rule (preregistered). Ledger row A5-242 reads supported only when both operands read supported, refuted when either
operand reads refuted, and unresolved otherwise (row_verdict). The two operands were chosen after the data as the
largest retained effect at each nullity among those with a retained twin, so the retained effects carry a winner's
curse that the replication test, not the retained sizes, answers.

Dead-region rule (preregistered). A region is dead when its visibility, the mean over its six units of the estimator's
signed visibility V_hat (nhat_bias.estimate, the quantity behind the retained 0.004 and -0.033), is below
DEAD_VISIBILITY. When more than one third of the regions are dead the analysis runs a second time over the live regions
and a verdict counts only when both runs read it; fewer than MIN_LIVE live regions leave every verdict unresolved.

Exploratory output (outside the family, the power calculation and the verdict). With --readout-errors, one calibration
readout error of the bit-4 physical qubit per replica, the analysis reports the correlation of the replica's control
gap G16 with it. A per-qubit readout flip predicts negative gaps at both nullities, so the nullity-12 positive sign is
the sign that readout cannot produce.

Modes:
    "$PYTHON" orientation_bit_analysis.py --self-test        decision rule on injected effects, with controls
    "$PYTHON" orientation_bit_analysis.py --power DIR --retained-collect PATH   replica count (DIR/power.json)
    "$PYTHON" orientation_bit_analysis.py --analyze COLLECT [--readout-errors JSON]
                                                              verdicts of a collected run (collect.json of live_run)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy import integrate, stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "nhat-bias"))

import nhat_bias as nb  # noqa: E402
import nhat_spectral as ns  # noqa: E402

import pathion_kernel_map as pkm  # noqa: E402
import pathion_kernel_map_orientation as pko  # noqa: E402

ALPHA = 0.05
POWER = 0.8
FAMILY = 14
# Replicas (disjoint six-qubit regions) the case plans, and the regions one run placed at the retained replica floor.
DEAD_VISIBILITY = 0.05
MIN_LIVE = 3
PLANNED_REPLICAS = 15
REGIONS_PER_RUN = 5
RETAINED_RUN = "ibm_fez kernel map"
STATISTICS = ("ctrl_g16", "move_g2", "move_leak16", "xtwin_g16", "keep_s", "flip_d", "diff_cm")
RETAINED_COLLECT = "results/live/2026-11-06T183538.809814Z/collect.json"
RETAINED_TWIN = {"kmap_e1pe26": "kmap_twin_e17me10", "kmap_e1pe18": "kmap_twin_e17me2"}
# Sign of the retained gap per operand: negative at nullity 4, positive at nullity 12 (ledger row A5-242).
RETAINED_SIGN = {(1, 26, 1): -1, (1, 18, 1): +1}
RETAINED_KEY = {(1, 26, 1): "kmap_e1pe26", (1, 18, 1): "kmap_e1pe18"}


def tag(operand: tuple[int, int, int]) -> str:
    return pkm.operand_tag(operand)


def replica_lambdas(unit: nb.Unit) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Walsh coefficients of the replica contrasts (replicas x bins), of the ideal sign, and lambda_a on the support
    (NaN off it)."""
    ci = ns.coefficients(unit.sign)
    co = ns.coefficients(unit.contrast)
    lam = np.full_like(co, np.nan)
    support = np.abs(ci) > ns.SUPPORT
    lam[:, support] = co[:, support] / ci[support]
    return co, ci, lam


def replica_statistics(units: dict[str, nb.Unit], operand: tuple[int, int, int]) -> dict[str, np.ndarray]:
    """The six per-replica statistics of one operand, each an array over replicas."""
    t = tag(operand)
    ctrl, move, xtwin = (units[f"kmo_{role}_{t}"] for role in pko.ROLES)
    _, _, lam_c = replica_lambdas(ctrl)
    co_m, ci_m, lam_m = replica_lambdas(move)
    _, _, lam_x = replica_lambdas(xtwin)
    moved = 2**pko.MOVED_BIT
    if np.isnan(lam_c[:, 16]).any() or np.isnan(lam_x[:, 16]).any() or np.isnan(lam_m[:, moved]).any():
        raise ValueError(f"{t}: a gap character lies outside the ideal support")
    if abs(ci_m[16]) > ns.SUPPORT:
        raise ValueError(f"{t}: character 16 lies inside the moved support, so it has no leakage reading")
    g_c = lam_c[:, 16] - lam_c[:, 0]
    g_x = lam_x[:, 16] - lam_x[:, 0]
    return {
        "ctrl_g16": g_c,
        "move_g2": lam_m[:, moved] - lam_m[:, 0],
        "move_leak16": co_m[:, 16],
        "xtwin_g16": g_x,
        "keep_s": (g_c + g_x) / 2.0,
        "flip_d": (g_c - g_x) / 2.0,
        "diff_cm": g_c - (lam_m[:, moved] - lam_m[:, 0]),
    }


def one_sample(values: np.ndarray) -> dict[str, float]:
    n = len(values)
    mean = float(values.mean())
    se = float(values.std(ddof=1) / math.sqrt(n))
    t = mean / se if se > 0 else math.copysign(math.inf, mean)
    p = float(2.0 * stats.t.sf(abs(t), n - 1)) if math.isfinite(t) else 0.0
    return {"n": n, "mean": mean, "se": se, "t": t, "p": p}


def holm(pvalues: dict[str, float], alpha: float = ALPHA) -> dict[str, bool]:
    """Holm's step-down procedure: the key is rejected when it and every smaller p pass their thresholds."""
    order = sorted(pvalues, key=lambda k: pvalues[k])
    m = len(order)
    out = dict.fromkeys(order, False)
    for rank, key in enumerate(order):
        if pvalues[key] > alpha / (m - rank):
            break
        out[key] = True
    return out


def family_tests(units: dict[str, nb.Unit]) -> dict[str, dict[str, Any]]:
    """Every test of the family, keyed <statistic>:<operand tag>, with its Holm decision."""
    tests: dict[str, dict[str, Any]] = {}
    for operand in pko.OPERANDS:
        for name, values in replica_statistics(units, operand).items():
            tests[f"{name}:{tag(operand)}"] = one_sample(values)
    if len(tests) != FAMILY:
        raise ValueError(f"family holds {len(tests)} tests, expected {FAMILY}")
    decided = holm({k: v["p"] for k, v in tests.items()})
    for key, row in tests.items():
        row["reject"] = decided[key]
    return tests


def readings(tests: dict[str, dict[str, Any]], operand: tuple[int, int, int], df: int) -> dict[str, Any]:
    """The three readings of one operand and the verdict on A5-242 (df is kept for the signature of the family)."""
    del df
    t = tag(operand)
    sign = RETAINED_SIGN[operand]
    row = {name: tests[f"{name}:{t}"] for name in STATISTICS}
    replicates = bool(row["ctrl_g16"]["reject"] and np.sign(row["ctrl_g16"]["mean"]) == sign)
    flipped = bool(row["ctrl_g16"]["reject"] and np.sign(row["ctrl_g16"]["mean"]) == -sign)
    follows = bool(row["move_g2"]["reject"] and np.sign(row["move_g2"]["mean"]) == sign)
    differs = bool(row["diff_cm"]["reject"])
    # (ii): the control's gap replicates and the moved member's gap differs from it without following it.
    stays = bool(replicates and differs and not follows)
    keeps, flips = bool(row["keep_s"]["reject"]), bool(row["flip_d"]["reject"])
    state = (
        "mixture" if keeps and flips else "operand-following" if keeps else "state-dependent" if flips else "unresolved"
    )
    if flipped or stays:
        verdict = "refuted"
    elif replicates and follows and not differs and state == "operand-following":
        verdict = "supported"
    else:
        verdict = "unresolved"
    return {
        "operand": t,
        "replicates_retained_sign": replicates,
        "sign_flipped": flipped,
        "i_gap_follows_orientation_qubit": bool(follows and not differs),
        "ii_gap_stays_on_bit_4": stays,
        "iii_exchange": state,
        "leakage_into_character_16": bool(row["move_leak16"]["reject"]),
        "verdict": verdict,
    }


def units_from_entry(entry: dict[str, Any], keep: list[int] | None = None) -> dict[str, nb.Unit]:
    """Units of one collected group entry: per unit the ideal sign and the replica contrasts of its two arms, over the
    replicas listed in keep (all when None)."""
    group = pko.pathion_kernel_map_orientation_group()
    if entry["group"] != group.name:
        raise ValueError(f"{entry['group']} is not {group.name}")
    ideal = {m.name: np.asarray(m.ideal, dtype=float) for m in group.members}
    measured = {name: np.asarray(v, dtype=float) for name, v in entry["measured"].items()}
    if keep is not None:
        measured = {name: v[keep] for name, v in measured.items()}
    units: dict[str, nb.Unit] = {}
    for member in group.members:
        if not member.name.endswith("_plus"):
            continue
        prefix = member.name[: -len("_plus")]
        sign = np.sign(pkm.output_contrast(ideal[f"{prefix}_plus"], ideal[f"{prefix}_minus"]))
        observed = np.array(
            [
                pkm.output_contrast(p, m)
                for p, m in zip(measured[f"{prefix}_plus"], measured[f"{prefix}_minus"], strict=True)
            ]
        )
        role = prefix.split("_")[1]
        units[prefix] = nb.Unit(prefix, "kmo", prefix.split("_", 2)[2], role, None, sign, observed)
    return units


def cross_check(units: dict[str, nb.Unit]) -> None:
    """The per-replica gaps reproduce nhat_spectral.unit_spectrum's minus_zero and t on every unit of the family."""
    for operand in pko.OPERANDS:
        t = tag(operand)
        for role, key, character in (("ctrl", "ctrl_g16", 16), ("xtwin", "xtwin_g16", 16), ("move", "move_g2", 2)):
            unit = units[f"kmo_{role}_{t}"]
            row = ns.unit_spectrum(unit)
            reference = next(c for c in row["characters"] if c["character"] == character)
            mine = one_sample(replica_statistics(units, operand)[key])
            nb.expect(abs(reference["minus_zero"] - mine["mean"]) < 1e-9, f"{unit.key}: gap mean differs")
            nb.expect(abs(reference["minus_zero_t"] - mine["t"]) < 1e-6, f"{unit.key}: gap t differs")


def row_verdict(verdicts: list[str]) -> str:
    """Verdict of ledger row A5-242 from its operands' verdicts: supported when all read supported, refuted when any
    reads refuted, otherwise unresolved."""
    if "refuted" in verdicts:
        return "refuted"
    if verdicts and all(v == "supported" for v in verdicts):
        return "supported"
    return "unresolved"


def region_visibilities(units: dict[str, nb.Unit]) -> np.ndarray:
    """Per replica, the mean over the six units of the signed visibility V_hat of nhat_bias.estimate."""
    per_unit = [[nb.estimate(contrast, unit.sign).visibility for contrast in unit.contrast] for unit in units.values()]
    return np.asarray(per_unit).mean(axis=0)


def _readings(units: dict[str, nb.Unit]) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]], int]:
    cross_check(units)
    tests = family_tests(units)
    n = next(iter(tests.values()))["n"]
    return tests, [readings(tests, operand, n - 1) for operand in pko.OPERANDS], n


def readout_correlation(units: dict[str, nb.Unit], readout_errors: list[float]) -> dict[str, Any]:
    """Exploratory: per operand, the Pearson and Spearman correlation over replicas of the control gap G16 with the
    calibration readout error of the bit-4 physical qubit of each replica's region."""
    out: dict[str, Any] = {"status": "exploratory, outside the family and the verdict", "operands": {}}
    for operand in pko.OPERANDS:
        gap = replica_statistics(units, operand)["ctrl_g16"]
        if len(readout_errors) != len(gap):
            raise ValueError(f"{len(readout_errors)} readout errors for {len(gap)} replicas")
        pearson = stats.pearsonr(gap, readout_errors)
        spearman = stats.spearmanr(gap, readout_errors)
        out["operands"][tag(operand)] = {
            "n": len(gap),
            "pearson_r": float(pearson.statistic),
            "pearson_p": float(pearson.pvalue),
            "spearman_rho": float(spearman.statistic),
            "spearman_p": float(spearman.pvalue),
        }
    return out


def analyze(entry: dict[str, Any], readout_errors: list[float] | None = None) -> dict[str, Any]:
    units = units_from_entry(entry)
    tests, reads, n = _readings(units)
    visibility = region_visibilities(units)
    dead = [int(i) for i in np.nonzero(visibility < DEAD_VISIBILITY)[0]]
    rule_applies = 3 * len(dead) > n
    live = [i for i in range(n) if i not in dead]
    for row in reads:
        row["verdict_all_regions"] = row["verdict"]
    if rule_applies:
        if len(live) >= MIN_LIVE:
            _, live_reads, _ = _readings(units_from_entry(entry, live))
        else:
            live_reads = [{"verdict": "unresolved"} for _ in reads]
        for row, live_row in zip(reads, live_reads, strict=True):
            row["verdict_live_regions"] = live_row["verdict"]
            if live_row["verdict"] != row["verdict"]:
                row["verdict"] = "unresolved"
    result = {
        "schema": "orientation-bit-analysis-v2",
        "replicas": n,
        "alpha": ALPHA,
        "family": FAMILY,
        "tests": tests,
        "readings": reads,
        "row": {"id": "A5-242", "verdict": row_verdict([r["verdict"] for r in reads])},
        "regions": {
            "visibility": [float(v) for v in visibility],
            "dead_below": DEAD_VISIBILITY,
            "dead": dead,
            "rule_applied": rule_applies,
        },
    }
    if readout_errors is not None:
        result["exploratory_readout_correlation"] = readout_correlation(units, readout_errors)
    return result


# ------------------------------------------------------------------------------------------------------- power


def retained_scatter(collect: Any) -> dict[str, dict[str, float]]:
    """Effect and scatter of the character-16 gap of the two case operands in the retained ibm_fez run.

    sd_per_replica is the replica standard error minus_zero / minus_zero_t of result_spectral.json times sqrt(5);
    sd_pair_difference is the standard deviation over the five replicas of G16 of the primary minus G16 of its
    quarter-turn twin read on the same region, the retained stand-in for the scatter of ctrl minus moved (two different
    circuits on one region), computed from the retained collect.json."""
    record = json.loads((HERE.parent / "nhat-bias" / "result_spectral.json").read_text())
    run = next(r for r in record["runs"] if r["name"] == RETAINED_RUN)
    units = {u.key: u for u in nb.run_units("kmap", collect)[0]}

    def gap16(key: str) -> np.ndarray:
        _, _, lam = replica_lambdas(units[key])
        return np.asarray(lam[:, 16] - lam[:, 0])

    out = {}
    for operand, key in RETAINED_KEY.items():
        unit = next(u for u in run["units"] if u["key"] == key)
        c = next(c for c in unit["characters"] if c["character"] == 16)
        se = abs(c["minus_zero"] / c["minus_zero_t"])
        pair = gap16(key) - gap16(RETAINED_TWIN[key])
        out[tag(operand)] = {
            "effect": c["minus_zero"],
            "se_five_replicas": se,
            "sd_per_replica": se * math.sqrt(5),
            "sd_pair_difference": float(pair.std(ddof=1)),
        }
    return out


def power_at(delta: float, sd: float, n: int, alpha: float) -> float:
    """Power of the two-sided one-sample t test: T = (Z + nc) / sqrt(V / df) with V ~ chi-square(df), so
    P(T > c) = E_V[Phi(nc - c sqrt(V / df))] and P(T < -c) = E_V[Phi(-nc - c sqrt(V / df))]; scipy's nct.sf returns NaN
    at large noncentrality, so the expectation over V is integrated directly."""
    df = n - 1
    crit = float(stats.t.isf(alpha / 2.0, df))
    nc = abs(delta) * math.sqrt(n) / sd

    def integrand(v: float) -> float:
        root = crit * math.sqrt(v / df)
        return float(stats.chi2.pdf(v, df) * (stats.norm.cdf(nc - root) + stats.norm.cdf(-nc - root)))

    value, _ = integrate.quad(integrand, 0.0, float(stats.chi2.isf(1e-12, df)), limit=200)
    return float(value)


def _first_true(predicate: Any, low: int, high: int) -> int | None:
    """Smallest integer in [low, high) with predicate true, for a predicate that is monotone (false, then true), by
    bisection; None when the predicate is false at high - 1."""
    if not predicate(high - 1):
        return None
    top = high - 1
    while low < top:
        mid = (low + top) // 2
        if predicate(mid):
            top = mid
        else:
            low = mid + 1
    return low


def required_replicas(delta: float, sd: float, alpha: float, power: float = POWER, nmax: int = 400) -> int:
    """Smallest replica count whose power reaches `power`; the power rises with n, so the search bisects."""
    found = _first_true(lambda n: power_at(delta, sd, n, alpha) >= power, 2, nmax)
    if found is None:
        raise ValueError("no replica count up to nmax reaches the power")
    return found


def power_record(collect: Any) -> dict[str, Any]:
    scatter = retained_scatter(collect)
    alpha = ALPHA / FAMILY
    rows = {}
    for name, s in scatter.items():
        full, half = abs(s["effect"]), abs(s["effect"]) / 2.0
        sd, sd_diff = s["sd_per_replica"], s["sd_pair_difference"]
        rows[name] = {
            **s,
            "n_full_effect": required_replicas(full, sd, alpha),
            "n_half_effect": required_replicas(half, sd, alpha),
            # C = ctrl - moved at the alternative that the moved gap is zero, so its mean is the full effect; S and D
            # at the retained effect, with the scatter of one gap (the conservative bound for a correlated pair).
            "n_diff_at_full_effect": required_replicas(full, sd_diff, alpha),
        }
    needed = max(max(r["n_full_effect"], r["n_diff_at_full_effect"]) for r in rows.values())
    n = PLANNED_REPLICAS
    if n < needed:
        raise ValueError(f"{n} planned replicas are fewer than the {needed} needed")
    for r in rows.values():
        r["power_at_n_full_effect"] = power_at(r["effect"], r["sd_per_replica"], n, alpha)
        r["power_at_n_half_effect"] = power_at(r["effect"] / 2.0, r["sd_per_replica"], n, alpha)
        r["power_diff_at_n_full_effect"] = power_at(r["effect"], r["sd_pair_difference"], n, alpha)
        sd_gap = r["sd_per_replica"]
        mde = _first_true(lambda d, sd=sd_gap: power_at(d / 1000.0, sd, n, alpha) >= POWER, 1, 1000)
        if mde is None:
            raise ValueError("no effect below 1 reaches the power")
        r["minimum_detectable_effect_at_n"] = mde / 1000.0
    return {
        "schema": "orientation-bit-power-v1",
        "alpha_family": ALPHA,
        "tests_in_family": FAMILY,
        "alpha_per_test": alpha,
        "power": POWER,
        "operands": rows,
        "replicas_needed": needed,
        "replicas": n,
        "regions_per_run": REGIONS_PER_RUN,
        "runs_at_regions_per_run": -(-n // REGIONS_PER_RUN),
        "source": "nhat-bias/result_spectral.json and the retained collect.json, run ibm_fez kernel map, character 16",
    }


# --------------------------------------------------------------------------------------------------- self-test


def _noise(n: int, sd: float, phase: int) -> np.ndarray:
    """Deterministic zero-mean replica scatter of standard deviation sd: normal quantiles at (i + 0.5) / n, cyclically
    shifted by phase so different statistics do not share one ordering."""
    q = stats.norm.ppf((np.arange(n) + 0.5) / n)
    q = np.roll(q, phase)
    return sd * (q - q.mean()) / q.std(ddof=1)


def synthetic_entry(
    n: int,
    sd: float,
    ctrl: dict[str, float],
    move: dict[str, float],
    xtwin: dict[str, float],
    visibility: float = 0.3,
    leak_sd: float = 0.016,
    leak_mean: float = 0.0,
    dead: tuple[int, ...] = (),
    gap_regions: str = "all",
) -> dict[str, Any]:
    """A collect entry whose replicas carry lambda_a = visibility + gap_a + scatter on each unit's ideal support, gap_a
    set per unit (a dict of "character:operand" to gap, 0 elsewhere), and on the moved unit a coefficient of character
    16 with mean leak_mean and scatter leak_sd (the shot-noise scale of 32 bins at 16,384 shots). The arms are laws
    whose selector-zero probability is 1/2 -+ c_obs / 2 on every output, so their contrast is c_obs. Replicas listed in
    dead carry the visibility -0.1 and gap_regions ("all", "dead" or "live") names the replicas that carry the gaps."""
    group = pko.pathion_kernel_map_orientation_group()
    ideal = {m.name: np.asarray(m.ideal, dtype=float) for m in group.members}
    measured: dict[str, list[list[float]]] = {m.name: [] for m in group.members}
    gaps = {"ctrl": ctrl, "move": move, "xtwin": xtwin}
    phase = 0
    for member in group.members:
        if not member.name.endswith("_plus"):
            continue
        prefix = member.name[: -len("_plus")]
        role, op = prefix.split("_")[1], prefix.split("_", 2)[2]
        sign = np.sign(pkm.output_contrast(ideal[f"{prefix}_plus"], ideal[f"{prefix}_minus"]))
        ci = ns.coefficients(sign)
        walsh = ns.walsh_matrix(len(sign))
        support = [a for a in range(len(sign)) if abs(ci[a]) > ns.SUPPORT]
        gap_here = {a: gaps[role].get(f"{a}:{op}", 0.0) for a in support}
        leak = _noise(n, leak_sd, phase + 11) + leak_mean
        scatter = {a: _noise(n, sd, phase + a) for a in support if a}
        scatter[0] = _noise(n, sd / 3.0, phase + 7)
        for r in range(n):
            here = -0.1 if r in dead else visibility
            carries = gap_regions == "all" or (gap_regions == "dead") == (r in dead)
            lam = {a: here + (gap_here[a] if carries else 0.0) + scatter[a][r] for a in support if a}
            lam[0] = here + scatter[0][r]
            c_obs = sum(lam[a] * ci[a] * walsh[a] for a in support)
            if role == "move":
                c_obs = c_obs + leak[r] * walsh[16]
            for arm, shift in (("plus", 0.5), ("minus", -0.5)):
                law = np.zeros(64)
                half = ideal[f"{prefix}_{arm}"].size // 2
                weights = np.ones(32) / 32.0
                law[:half] = weights * (0.5 + shift * c_obs)
                law[half:] = weights * (0.5 - shift * c_obs)
                measured[f"{prefix}_{arm}"].append(law.tolist())
        phase += 3
    return {"group": group.name, "measured": measured}


def self_test(collect: Any) -> list[str]:
    done = []
    n, sd = 40, 0.08
    ops = {tag(o): o for o in pko.OPERANDS}
    follow: dict[str, float] = {f"16:{t}": 0.12 * RETAINED_SIGN[o] for t, o in ops.items()}
    ctrl_gap = dict(follow)
    xtwin_gap = dict(follow)  # operand-following: the exchange keeps the sign
    move_gap = {f"2:{t}": 0.12 * RETAINED_SIGN[o] for t, o in ops.items()}
    result = analyze(synthetic_entry(n, sd, ctrl_gap, move_gap, xtwin_gap))
    got = [r["verdict"] for r in result["readings"]]
    nb.expect(got == ["supported", "supported"], f"operand-following effect read as {got}")
    nb.expect(all(r["iii_exchange"] == "operand-following" for r in result["readings"]), "exchange reading")
    nb.expect(not any(r["leakage_into_character_16"] for r in result["readings"]), "shot-scale leakage was rejected")
    done.append("an injected operand-following gap on bit 4 and on bit 1 reads supported on both operands")
    null = analyze(synthetic_entry(n, sd, {}, {}, {}))
    nb.expect(all(r["verdict"] == "unresolved" for r in null["readings"]), "a null run was not unresolved")
    nb.expect(not any(t["reject"] for t in null["tests"].values()), "a null run rejected a test")
    done.append("a run with no gap rejects no test of the 14 (known-bad input of the rule)")
    stays = analyze(synthetic_entry(n, sd, ctrl_gap, {}, xtwin_gap))
    nb.expect(all(r["verdict"] == "refuted" and r["ii_gap_stays_on_bit_4"] for r in stays["readings"]), "stays on 16")
    nb.expect(not any(r["leakage_into_character_16"] for r in stays["readings"]), "stays: spurious leakage")
    done.append("a replicated gap on bit 4 with none on bit 1 reads refuted as stated (reading ii), through C")
    smaller = analyze(synthetic_entry(n, sd, ctrl_gap, {k: v / 3.0 for k, v in move_gap.items()}, xtwin_gap))
    nb.expect(all(r["verdict"] != "supported" for r in smaller["readings"]), "a third-size moved gap was supported")
    done.append("a moved gap of one third the size is not read as supported")
    leaked = analyze(synthetic_entry(n, sd, ctrl_gap, move_gap, xtwin_gap, leak_mean=0.1))
    nb.expect(all(r["leakage_into_character_16"] for r in leaked["readings"]), "leakage of 0.1 was not rejected")
    nb.expect(all(r["verdict"] == "supported" for r in leaked["readings"]), "leakage alone changed the verdict")
    done.append("leakage into character 16 is reported and leaves the verdict to G2 and C")
    flip_x = {k: -v for k, v in follow.items()}
    state = analyze(synthetic_entry(n, sd, ctrl_gap, move_gap, flip_x))
    nb.expect(all(r["iii_exchange"] == "state-dependent" for r in state["readings"]), "state-dependent exchange")
    nb.expect(all(r["verdict"] == "unresolved" for r in state["readings"]), "a state-dependent exchange is supported")
    done.append("a gap whose sign flips under the exchange reads state-dependent and leaves A5-242 unresolved")
    inverted = analyze(synthetic_entry(n, sd, {k: -v for k, v in follow.items()}, {}, {}))
    nb.expect(all(r["verdict"] == "refuted" for r in inverted["readings"]), "an inverted retained sign is not refuted")
    done.append("a replicated gap of the opposite sign reads refuted")
    nb.expect(row_verdict(["supported", "supported"]) == "supported", "row rule: both supported")
    nb.expect(row_verdict(["supported", "unresolved"]) == "unresolved", "row rule: one supported")
    nb.expect(row_verdict(["supported", "refuted"]) == "refuted", "row rule: one refuted")
    nb.expect(row_verdict(["unresolved", "refuted"]) == "refuted", "row rule: refuted outranks unresolved")
    nb.expect(result["row"]["verdict"] == "supported" and null["row"]["verdict"] == "unresolved", "analyze row")
    done.append("the row reads supported only when both operands do, refuted when either is, else unresolved")
    dead = tuple(range(0, n, 5)) + tuple(range(1, n, 5))  # 40 percent of the regions
    live_gap = analyze(synthetic_entry(n, sd, ctrl_gap, move_gap, xtwin_gap, dead=dead, gap_regions="live"))
    nb.expect(live_gap["regions"]["dead"] == sorted(dead) and live_gap["regions"]["rule_applied"], "dead regions")
    nb.expect(all(r["verdict"] == "supported" for r in live_gap["readings"]), "live-region effect was lost")
    done.append("a gap carried by the live regions survives the dead-region rule (more than one third dead)")
    big = [{k: 2.5 * v for k, v in g.items()} for g in (ctrl_gap, move_gap, xtwin_gap)]
    dead_gap = analyze(synthetic_entry(n, sd, big[0], big[1], big[2], dead=dead, gap_regions="dead"))
    nb.expect(all(r["verdict_all_regions"] == "supported" for r in dead_gap["readings"]), "all-region run: no gap")
    nb.expect(all(r["verdict_live_regions"] == "unresolved" for r in dead_gap["readings"]), "live run read a gap")
    nb.expect(all(r["verdict"] == "unresolved" for r in dead_gap["readings"]), "a dead-region gap counted")
    nb.expect(dead_gap["row"]["verdict"] == "unresolved", "the row counted a dead-region gap")
    done.append("a gap carried only by regions with visibility under 0.05 is not counted when they exceed one third")
    few = analyze(synthetic_entry(n, sd, big[0], big[1], big[2], dead=dead[:2], gap_regions="dead"))
    nb.expect(not few["regions"]["rule_applied"], "two dead regions of forty applied the rule")
    done.append("the dead-region rule stays off at or below one third of the regions")
    pvalues = {"a": 0.001, "b": 0.02, "c": 0.04, "d": 0.5}
    nb.expect(holm(pvalues) == {"a": True, "b": False, "c": False, "d": False}, "Holm thresholds")
    nb.expect(holm({"a": 0.01, "b": 0.012}) == {"a": True, "b": True}, "Holm step-down")
    done.append("Holm rejects by the step-down thresholds alpha / (m - rank)")
    nb.expect(abs(power_at(0.0, 0.1, 10, 0.05) - 0.05) < 1e-6, "the power at zero effect is the size of the test")
    nb.expect(
        abs(power_at(0.09, 0.1, 12, 0.05) - float(stats.nct.sf(2.2009851, 11, 0.09 * 12**0.5 / 0.1))) < 2e-3,
        "power vs nct",
    )
    nb.expect(power_at(0.03, 0.1, 12, 0.05) < POWER, "a small effect reaches full power: the power function is flat")
    done.append("the power function equals the noncentral t at 0.09 / 0.1 and the size of the test at zero effect")
    if collect is not None:
        power = power_record(collect)
        nb.expect(all(r["power_at_n_full_effect"] >= POWER for r in power["operands"].values()), "power at n")
        nb.expect(all(r["power_diff_at_n_full_effect"] >= POWER for r in power["operands"].values()), "diff power")
        done.append(f"{power['replicas']} replicas give power at least {POWER} for the gaps and for C")
    return done


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--power", type=Path, metavar="DIR")
    mode.add_argument("--analyze", type=Path, metavar="COLLECT")
    ap.add_argument("--retained-collect", type=Path, help=f"{RETAINED_COLLECT}, read by --power and --self-test")
    ap.add_argument("--readout-errors", type=Path, help="JSON list: readout error of the bit-4 qubit per replica")
    args = ap.parse_args()
    retained = json.loads(args.retained_collect.read_text()) if args.retained_collect else None
    if args.self_test:
        for line in self_test(retained):
            print(f"ok: {line}")
        return 0
    if args.power:
        if retained is None:
            ap.error("--power needs --retained-collect")
        record = power_record(retained)
        record["retained_collect_sha256"] = hashlib.sha256(args.retained_collect.read_bytes()).hexdigest()
        (args.power / "power.json").write_text(json.dumps(record, indent=1, sort_keys=True) + "\n")
        return 0
    collect = json.loads(args.analyze.read_text())
    items = collect if isinstance(collect, list) else [collect]
    entry = next(x for x in items if isinstance(x, dict) and x.get("group") == "pathion_kernel_map_orientation")
    errors = json.loads(args.readout_errors.read_text()) if args.readout_errors else None
    print(json.dumps(analyze(entry, errors), indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
