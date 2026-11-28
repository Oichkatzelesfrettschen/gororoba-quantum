"""Analysis and preregistered decision rule of the orientation-bit case.

The case is written in docs/design/pathion-kernel-map-orientation-bit.md.

The case asks whether the paired character gap lambda_16 - lambda_0 of the ibm_fez kernel map follows the orientation
qubit. For one operand it reads four units of group pathion_kernel_map_orientation over replicas (chip
regions): ctrl (orientation on bit 4), move (orientation on bit 1), xtwin (ctrl with one X on data qubit 4 before
readout) and swap (ctrl with data wires 1 and 4 exchanged, so that bit 4 sits on the physical qubit that carries bit 1
in the other units). Per replica, with lambda_a = c^_obs,a / c^_ideal,a on the Walsh support of the ideal contrast
(nhat_spectral.coefficients, nhat_spectral.unit_spectrum; this module reuses both):

    ctrl   G16  = lambda_16 - lambda_0
    move   G2   = lambda_2 - lambda_0            (character 2^b of the moved orientation bit b = 1)
    move   leak = c^_obs,16                      (character 16 lies outside the ideal support: leakage, ideal 0; it
                                                  needs a channel that is not character-diagonal, so it is reported
                                                  and tested but cannot decide the verdict)
    xtwin  G16  = lambda_16 - lambda_0 against the exchanged ideal
    S = (G16_ctrl + G16_xtwin) / 2               the part that keeps its sign under the exchange (follows the operand)
    D = (G16_ctrl - G16_xtwin) / 2               the part that flips its sign under the exchange
    G16s   = lambda_16 - lambda_0 of the swap unit   the gap of bit 4 read on the physical qubit of bit 1 (swap_g16)
    C  = G16_ctrl - G2_move                      zero when the gap moves with the orientation qubit at equal size
                                                  (diff_cm). Two different circuits make C nonzero without the
                                                  hypothesis: the noise models of case_compile.json predict a floor of
                                                  +0.004 to +0.047 from the circuits alone, a fact of the SELECT and
                                                  oracle structure (the swap unit reads the same floor, diff_sm), so
                                                  C is tested against the band of the model floors, below.

What D sees. The xtwin compiles to the control's schedule plus one virtual rz on the data-bit-4 wire after the SELECT
(identical cz sequence, identical measure mapping; tests/gororoba_quantum/test_pathion_kernel_map_orientation.py), so
D is zero under every error that acts before that frame, including the SELECT-decay hypothesis of row A5-242, and
responds only to an asymmetric readout of the bit-4 physical qubit or a coherent angle error on that wire's final
single-qubit tail. D isolates the readout-asymmetry half of the row's open "relaxation or asymmetric readout"
question; it does not resolve the relaxation half.

Each statistic is a one-sample t test over blocks with n - 1 degrees of freedom, whose standard error is the scatter of
the block values, so the test holds whatever drift the device has between regions. A block is one region: the case
runs two jobs on the same 15 regions (a 156-qubit chip holds at most 26 disjoint six-qubit regions, so 30 disjoint
replicas do not exist), and merge_jobs averages the two replicas of a region (every statistic is linear in the
measured laws) before the test, so n is the number of regions and the test stays valid for any correlation between
the two replicas of a region. Two operands and eight statistics make the family of 16 tests; Holm's step-down
procedure holds the family error at ALPHA.

Floor band (preregistered). The null of C is the band [lower_i, upper_i] of every region i, not zero: upper_i is the
largest and lower_i the smallest, with zero included, of the four model floors of C of that region (the compile_case.py
models on the region's own dry-run calibration: depolarizing with symmetric readout, relaxation alone, asymmetric
readout alone, and all three). The test of C rejects when the region values C_i - upper_i have a positive mean or the
values lower_i - C_i a positive mean, each by a one-sided t test over regions with n - 1 degrees of freedom, and its
p value is twice the smaller of the two (capped at 1). A model floor between zero and its upper edge therefore reads as
unresolved, and only a C beyond every model floor reads as a difference. The floors enter analyze() as a required input
(--floors); the band itself is a modeling choice whose uncertainty the case states: the models reach 21 to 27 percent of
the retained gap, so the band is bounded by the four mixtures that the offline models can build and not by a measured
error of the model.

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
    "$PYTHON" orientation_bit_analysis.py --operating DIR   operating characteristics of the rule under the model
                                                              floors (DIR/operating.json from DIR/power.json and
                                                              DIR/case_compile.json)
    "$PYTHON" orientation_bit_analysis.py --analyze COLLECT... [--regions JSON...] [--readout-errors JSON]
                                                              verdicts of the collected jobs (collect.json of
                                                              live_run); --regions names each job's region qubit
                                                              lists so that replicas of one region merge
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
import pathion_kernel_map_orientation_merged as pkom  # noqa: E402

ORIENTATION_GROUPS = ("pathion_kernel_map_orientation", pkom.GROUP_NAME)
ALPHA = 0.05
POWER = 0.8
FAMILY = 16
# The case plans two jobs on the same 15 disjoint six-qubit regions (30 replicas); a region is the block of its two
# replicas. The retained run placed 5 regions at the retained replica floor.
DEAD_VISIBILITY = 0.05
MIN_LIVE = 3
PLANNED_REGIONS = 15
JOBS = 2
PLANNED_REPLICAS = PLANNED_REGIONS * JOBS
REGIONS_PER_RUN = 5
# Correlation of the two replicas of one region that the power table spans: 0 (independent) and 1 (the second job
# adds nothing), the bounds between which the unknown job-to-job intraclass correlation lies.
RHOS = (0.0, 1.0)
# Median scatter of the off-support coefficient c_obs,16 of the retained units (32 bins at 16,384 shots).
LEAK_SD = 0.017
RETAINED_RUN = "ibm_fez kernel map"
STATISTICS = ("ctrl_g16", "move_g2", "move_leak16", "xtwin_g16", "swap_g16", "keep_s", "flip_d", "diff_cm")
EXPLORATORY = ("diff_sm", "diff_cs")
OLD_STATISTICS = ("ctrl_g16", "move_g2", "move_leak16", "xtwin_g16", "keep_s", "flip_d", "diff_cm")
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
    """The per-replica statistics of one operand (the family and the exploratory ones), each an array over replicas."""
    t = tag(operand)
    ctrl, move, xtwin, swap = (units[f"kmo_{role}_{t}"] for role in pko.ROLES)
    _, _, lam_c = replica_lambdas(ctrl)
    _, _, lam_s = replica_lambdas(swap)
    co_m, ci_m, lam_m = replica_lambdas(move)
    _, _, lam_x = replica_lambdas(xtwin)
    moved = 2**pko.MOVED_BIT
    if any(np.isnan(lam[:, 16]).any() for lam in (lam_c, lam_x, lam_s)) or np.isnan(lam_m[:, moved]).any():
        raise ValueError(f"{t}: a gap character lies outside the ideal support")
    if abs(ci_m[16]) > ns.SUPPORT:
        raise ValueError(f"{t}: character 16 lies inside the moved support, so it has no leakage reading")
    g_c = lam_c[:, 16] - lam_c[:, 0]
    g_x = lam_x[:, 16] - lam_x[:, 0]
    g_s = lam_s[:, 16] - lam_s[:, 0]
    g_m = lam_m[:, moved] - lam_m[:, 0]
    return {
        "ctrl_g16": g_c,
        "move_g2": g_m,
        "move_leak16": co_m[:, 16],
        "xtwin_g16": g_x,
        "swap_g16": g_s,
        "keep_s": (g_c + g_x) / 2.0,
        "flip_d": (g_c - g_x) / 2.0,
        "diff_sm": g_s - g_m,
        "diff_cm": g_c - g_m,
        "diff_cs": g_c - g_s,
    }


def one_sample(values: np.ndarray) -> dict[str, float]:
    n = len(values)
    mean = float(values.mean())
    se = float(values.std(ddof=1) / math.sqrt(n))
    t = mean / se if se > 0 else math.copysign(math.inf, mean)
    p = float(2.0 * stats.t.sf(abs(t), n - 1)) if math.isfinite(t) else 0.0
    return {"n": n, "mean": mean, "se": se, "t": t, "p": p}


def tests_names(tests: dict[str, dict[str, Any]], t: str) -> list[str]:
    return [key.split(":")[0] for key in tests if key.endswith(f":{t}")]


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


def band_test(values: np.ndarray, lower: np.ndarray, upper: np.ndarray) -> dict[str, float]:
    """Test of values against the band [lower, upper] per replica: two one-sided t tests (above upper, below lower),
    p = twice the smaller one-sided p, capped at 1. The row reports the mean of the values and of the excess beyond the
    nearer edge on the side that decides."""
    n = len(values)
    if len(lower) != n or len(upper) != n or np.any(lower > upper):
        raise ValueError("a floor band needs one lower <= upper pair per replica")
    above, below = values - upper, lower - values
    sides = []
    for excess in (above, below):
        se = float(excess.std(ddof=1) / math.sqrt(n))
        t = float(excess.mean() / se) if se > 0 else math.copysign(math.inf, float(excess.mean()))
        sides.append((float(stats.t.sf(t, n - 1)) if math.isfinite(t) else float(t < 0), t, float(excess.mean()), se))
    best = min(sides, key=lambda s: s[0])
    return {
        "n": n,
        "mean": float(values.mean()),
        "se": best[3],
        "t": best[1],
        "p": float(min(1.0, 2.0 * best[0])),
        "excess_mean": best[2],
        "band_upper_mean": float(upper.mean()),
        "band_lower_mean": float(lower.mean()),
    }


def _band_from_summary(mean: float, se: float, n: int, lower: float, upper: float) -> dict[str, float]:
    """band_test for a mean and standard error with constant band edges."""
    ps = []
    for excess in (mean - upper, lower - mean):
        t = excess / se if se > 0 else math.copysign(math.inf, excess)
        ps.append(float(stats.t.sf(t, n - 1)) if math.isfinite(t) else float(t < 0))
    t_best = (mean - upper) / se if ps[0] <= ps[1] else (lower - mean) / se
    return {"n": n, "mean": mean, "se": se, "t": t_best, "p": min(1.0, 2.0 * min(ps))}


def _from_summary(mean: float, se: float, n: int) -> dict[str, float]:
    t = mean / se if se > 0 else math.copysign(math.inf, mean)
    p = float(2.0 * stats.t.sf(abs(t), n - 1)) if math.isfinite(t) else 0.0
    return {"n": n, "mean": mean, "se": se, "t": t, "p": p}


def decide_tests(tests: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Holm decision over every test of the dict, written into each row as reject."""
    decided = holm({k: v["p"] for k, v in tests.items()})
    for key, row in tests.items():
        row["reject"] = decided[key]
    return tests


Floors = dict[str, dict[str, list[float]]]


def zero_floors(n: int) -> Floors:
    """The band [0, 0] of every region: C is tested against zero, as the superseded rule did."""
    return {tag(o): {"lower": [0.0] * n, "upper": [0.0] * n} for o in pko.OPERANDS}


def decide(
    values: dict[tuple[int, int, int], dict[str, np.ndarray]],
    names: tuple[str, ...] = STATISTICS,
    floors: Floors | None = None,
) -> dict[str, dict[str, Any]]:
    """Every test of a family of the named statistics over both operands, keyed <statistic>:<operand tag>, with its
    Holm decision. With floors, diff_cm is tested against the floor band of its operand."""
    tests: dict[str, dict[str, Any]] = {}
    for operand in pko.OPERANDS:
        for name in names:
            if name == "diff_cm" and floors is not None:
                band = floors[tag(operand)]
                tests[f"{name}:{tag(operand)}"] = band_test(
                    values[operand][name],
                    np.asarray(band["lower"], dtype=float),
                    np.asarray(band["upper"], dtype=float),
                )
            else:
                tests[f"{name}:{tag(operand)}"] = one_sample(values[operand][name])
    return decide_tests(tests)


def family_tests(units: dict[str, nb.Unit], floors: Floors) -> dict[str, dict[str, Any]]:
    tests = decide({operand: replica_statistics(units, operand) for operand in pko.OPERANDS}, floors=floors)
    if len(tests) != FAMILY:
        raise ValueError(f"family holds {len(tests)} tests, expected {FAMILY}")
    return tests


def readings(
    tests: dict[str, dict[str, Any]], operand: tuple[int, int, int], df: int, differs_key: str = "diff_cm"
) -> dict[str, Any]:
    """The readings of one operand and the verdict on A5-242 (df is kept for the signature of the family).
    differs_key names the statistic that decides whether the moved gap differs from the gap of bit 4 (diff_cm)."""
    del df
    t = tag(operand)
    sign = RETAINED_SIGN[operand]
    row = {name: tests[f"{name}:{t}"] for name in tests_names(tests, t)}
    replicates = bool(row["ctrl_g16"]["reject"] and np.sign(row["ctrl_g16"]["mean"]) == sign)
    flipped = bool(row["ctrl_g16"]["reject"] and np.sign(row["ctrl_g16"]["mean"]) == -sign)
    follows = bool(row["move_g2"]["reject"] and np.sign(row["move_g2"]["mean"]) == sign)
    differs = bool(row[differs_key]["reject"])
    travels = bool("swap_g16" in row and row["swap_g16"]["reject"] and np.sign(row["swap_g16"]["mean"]) == sign)
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
        "gap_travels_with_bit_4_wire": travels,
        "layout_bound_candidate": bool(replicates and "swap_g16" in row and not travels),
        "ii_gap_stays_on_bit_4": stays,
        "iii_exchange": state,
        "leakage_into_character_16": bool(row["move_leak16"]["reject"]),
        "verdict": verdict,
    }


def entry_group(name: str) -> Any:
    """The group a collected entry names: the retained group or its merged-diagonal successor, whose members carry the
    retained names, order and ideal laws (test_pathion_kernel_map_orientation_merged), so one rule reads both."""
    for group in (pko.pathion_kernel_map_orientation_group(), pkom.pathion_kernel_map_orientation_merged_group()):
        if group.name == name:
            return group
    raise ValueError(f"{name} is not an orientation-bit group")


def units_from_entry(entry: dict[str, Any], keep: list[int] | None = None) -> dict[str, nb.Unit]:
    """Units of one collected group entry: per unit the ideal sign and the replica contrasts of its two arms, over the
    replicas listed in keep (all when None)."""
    group = entry_group(entry["group"])
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
        for role, key, character in (
            ("ctrl", "ctrl_g16", 16),
            ("xtwin", "xtwin_g16", 16),
            ("swap", "swap_g16", 16),
            ("move", "move_g2", 2),
        ):
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


def _readings(units: dict[str, nb.Unit], floors: Floors) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]], int]:
    cross_check(units)
    tests = family_tests(units, floors)
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


def merge_jobs(
    entries: list[dict[str, Any]],
    regions: list[list[list[int]]] | None = None,
    floors: list[Floors] | None = None,
) -> tuple[dict[str, Any], Floors | None]:
    """One collected entry from the entries of the jobs of the case. A region is the block of its replicas: replicas
    whose qubit sets are equal (across jobs) average their measured laws, which leaves every statistic's value the mean
    of the replicas' values because each statistic is linear in the laws. Without regions each entry is one job and
    its replicas are positioned alike (replica i of every job is one region); distinct regions stay separate blocks."""
    if len(entries) == 1 and regions is None:
        return entries[0], None if floors is None else floors[0]
    if floors is not None and len(floors) != len(entries):
        raise ValueError("floors need one entry per job")
    if regions is not None and (
        len(regions) != len(entries) or any(len(r) != len(set(map(tuple, r))) for r in regions)
    ):
        raise ValueError("regions need one list per job, each region once")
    names = list(entries[0]["measured"])
    sizes = {len(next(iter(e["measured"].values()))) for e in entries}
    if regions is not None:
        for e, r in zip(entries, regions, strict=True):
            if len(next(iter(e["measured"].values()))) != len(r):
                raise ValueError("a job's replicas and its regions differ in number")
        keys = [[tuple(sorted(q)) for q in r] for r in regions]
    elif len(sizes) == 1:
        size = sizes.pop()
        keys = [[(i,) for i in range(size)] for _ in entries]
    else:
        raise ValueError("jobs of different replica counts need their regions")
    blocks: dict[tuple[int, ...], list[tuple[int, int]]] = {}
    for j, job_keys in enumerate(keys):
        for i, key in enumerate(job_keys):
            blocks.setdefault(key, []).append((j, i))
    measured = {
        name: [
            np.mean([np.asarray(entries[j]["measured"][name][i], dtype=float) for j, i in members], axis=0).tolist()
            for members in blocks.values()
        ]
        for name in names
    }
    merged_floors: Floors | None = None
    if floors is not None:
        merged_floors = {
            t: {
                edge: [float(np.mean([floors[j][t][edge][i] for j, i in members])) for members in blocks.values()]
                for edge in ("lower", "upper")
            }
            for t in (tag(o) for o in pko.OPERANDS)
        }
    entry = {"group": entries[0]["group"], "measured": measured, "blocks": [len(m) for m in blocks.values()]}
    return entry, merged_floors


def analyze_flat(entry: dict[str, Any], readout_errors: list[float] | None = None) -> dict[str, Any]:
    """analyze() against the band [0, 0] of every region (no model floor), for synthetic entries and the superseded
    rule."""
    n = len(next(iter(entry["measured"].values())))
    return analyze(entry, zero_floors(n), readout_errors)


def analyze(entry: dict[str, Any], floors: Floors, readout_errors: list[float] | None = None) -> dict[str, Any]:
    """Verdicts of one collected entry; floors holds, per operand tag, the lower and upper edge of the floor band of C
    for each region (block) of the entry."""
    units = units_from_entry(entry)
    tests, reads, n = _readings(units, floors)
    visibility = region_visibilities(units)
    dead = [int(i) for i in np.nonzero(visibility < DEAD_VISIBILITY)[0]]
    rule_applies = 3 * len(dead) > n
    live = [i for i in range(n) if i not in dead]
    for row in reads:
        row["verdict_all_regions"] = row["verdict"]
    if rule_applies:
        if len(live) >= MIN_LIVE:
            live_floors = {t: {k: [v[i] for i in live] for k, v in band.items()} for t, band in floors.items()}
            _, live_reads, _ = _readings(units_from_entry(entry, live), live_floors)
        else:
            live_reads = [{"verdict": "unresolved"} for _ in reads]
        for row, live_row in zip(reads, live_reads, strict=True):
            row["verdict_live_regions"] = live_row["verdict"]
            if live_row["verdict"] != row["verdict"]:
                row["verdict"] = "unresolved"
    result = {
        "schema": "orientation-bit-analysis-v3",
        "replicas": n,
        "replicas_per_block": entry.get("blocks"),
        "floors": floors,
        "exploratory": {
            f"{name}:{tag(operand)}": one_sample(replica_statistics(units, operand)[name])
            for operand in pko.OPERANDS
            for name in EXPLORATORY
        },
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
        g_c, g_x = gap16(key), gap16(RETAINED_TWIN[key])
        pair = g_c - g_x
        out[tag(operand)] = {
            "effect": c["minus_zero"],
            "se_five_replicas": se,
            "sd_per_replica": se * math.sqrt(5),
            "sd_pair_difference": float(pair.std(ddof=1)),
            "retained_twin_gap": float(g_x.mean()),
            "sd_twin_gap": float(g_x.std(ddof=1)),
            "retained_keep_s": float(((g_c + g_x) / 2.0).mean()),
            "sd_keep_s": float(((g_c + g_x) / 2.0).std(ddof=1)),
            "retained_flip_d": float(((g_c - g_x) / 2.0).mean()),
            "sd_flip_d": float((pair / 2.0).std(ddof=1)),
            "pair_correlation": float(np.corrcoef(g_c, g_x)[0, 1]),
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


def _design_sd(sd: float, rho: float) -> float:
    """Standard deviation of the mean of the JOBS replicas of one region when the replicas of a region correlate with
    rho: sd * sqrt(rho + (1 - rho) / JOBS)."""
    return sd * math.sqrt(rho + (1.0 - rho) / JOBS)


def statistic_specs(s: dict[str, float], band_upper: float) -> dict[str, tuple[float | None, float]]:
    """(retained effect, standard deviation per replica) of every statistic of the family for one operand, from the
    retained scatter. The gap statistics take the retained gap as their alternative (the gap moves, travels and is
    kept at full size); diff_cm takes the alternative that the moved gap is zero, so its mean is the full effect less
    the upper edge of the floor band (the truth floor is zero in the worst case, so the band edge is all lost), with
    the scatter of the retained primary-minus-twin pair as the stand-in for two circuits on one region; xtwin, S and D
    take the retained twin's own values; leak16 has no retained effect (ideal 0) and takes the shot-noise scatter."""
    return {
        "ctrl_g16": (abs(s["effect"]), s["sd_per_replica"]),
        "move_g2": (abs(s["effect"]), s["sd_per_replica"]),
        "swap_g16": (abs(s["effect"]), s["sd_per_replica"]),
        "diff_cm": (max(abs(s["effect"]) - band_upper, 0.0), s["sd_pair_difference"]),
        "xtwin_g16": (abs(s["retained_twin_gap"]), s["sd_twin_gap"]),
        "keep_s": (abs(s["retained_keep_s"]), s["sd_keep_s"]),
        "flip_d": (abs(s["retained_flip_d"]), s["sd_flip_d"]),
        "move_leak16": (None, LEAK_SD),
    }


def _mde(sd: float, n: int, alpha: float) -> float:
    found = _first_true(lambda d: power_at(d / 1000.0, sd, n, alpha) >= POWER, 1, 1000)
    if found is None:
        raise ValueError("no effect below 1 reaches the power")
    return found / 1000.0


def floor_band_edges(compile_record: dict[str, Any]) -> dict[str, dict[str, float]]:
    """Mean over the regions of the lower and upper edge of the floor band of C, per operand tag."""
    band = compile_record["relaxation"]["floor_band"]
    return {t: {edge: float(np.mean(b[edge])) for edge in ("lower", "upper")} for t, b in band.items()}


def power_record(collect: Any, compile_record: dict[str, Any]) -> dict[str, Any]:
    """Power of every statistic of the family at the planned design: PLANNED_REGIONS regions read JOBS times, the test
    over region means (df = regions - 1) at the correlation rho of a region's replicas in RHOS, and for reference the
    test over all replicas as independent values (df = replicas - 1). The effect is the retained one and half of it."""
    scatter = retained_scatter(collect)
    edges = floor_band_edges(compile_record)
    alpha = ALPHA / FAMILY
    operands: dict[str, Any] = {}
    needed = 0
    for name, s in scatter.items():
        rows: dict[str, Any] = {}
        for stat, (effect, sd) in statistic_specs(s, edges[name]["upper"]).items():
            row: dict[str, Any] = {"effect": effect, "sd_per_replica": sd}
            designs = {f"regions_rho{int(rho)}": (PLANNED_REGIONS, _design_sd(sd, rho)) for rho in RHOS}
            designs["replicas_independent"] = (PLANNED_REPLICAS, sd)
            for label, (n, sd_n) in designs.items():
                cell = {"minimum_detectable_effect": _mde(sd_n, n, alpha)}
                if effect is not None:
                    cell["power_full_effect"] = power_at(effect, sd_n, n, alpha)
                    cell["power_half_effect"] = power_at(effect / 2.0, sd_n, n, alpha)
                row[label] = cell
            if stat in ("ctrl_g16", "move_g2", "swap_g16") and effect is not None:
                needed = max(needed, required_replicas(effect, sd, alpha))
            rows[stat] = row
        operands[name] = {**s, "floor_band_mean": edges[name], "statistics": rows}
    if needed > PLANNED_REGIONS:
        raise ValueError(f"{PLANNED_REGIONS} planned regions are fewer than the {needed} needed")
    return {
        "schema": "orientation-bit-power-v3",
        "alpha_family": ALPHA,
        "tests_in_family": FAMILY,
        "alpha_per_test": alpha,
        "power": POWER,
        "operands": operands,
        "regions_needed_if_replicas_of_a_region_are_identical": needed,
        "planned_regions": PLANNED_REGIONS,
        "jobs": JOBS,
        "replicas": PLANNED_REPLICAS,
        "regions_per_run": REGIONS_PER_RUN,
        "rhos": list(RHOS),
        "leak_sd": LEAK_SD,
        "source": "nhat-bias/result_spectral.json and the retained collect.json, run ibm_fez kernel map, character 16",
    }


# ---------------------------------------------------------------------------------------- operating characteristics

_WEIGHTS = {
    "ctrl_g16": (1, 0, 0, 0, 0),
    "move_g2": (0, 1, 0, 0, 0),
    "xtwin_g16": (0, 0, 1, 0, 0),
    "swap_g16": (0, 0, 0, 1, 0),
    "move_leak16": (0, 0, 0, 0, 1),
    "keep_s": (0.5, 0, 0.5, 0, 0),
    "flip_d": (0.5, 0, -0.5, 0, 0),
    "diff_sm": (0, -1, 0, 1, 0),
    "diff_cm": (1, -1, 0, 0, 0),
}
_VARIABLES = ("ctrl_g16", "move_g2", "xtwin_g16", "swap_g16", "move_leak16")
OPERATING_LOG2_TRIALS = 12


def _normal_quasi(u: np.ndarray) -> np.ndarray:
    return np.asarray(stats.norm.ppf(u))


def _unit_points(dim: int, log2: int) -> np.ndarray:
    """Deterministic points of the unit cube: an unscrambled Sobol sequence shifted by half a cell and wrapped, so no
    coordinate is 0 or 1 and no random seed enters the calculation."""
    from scipy.stats import qmc

    points = qmc.Sobol(dim, scramble=False).random(2**log2)
    return np.mod(points + 0.5 / 2**log2, 1.0)


def _summaries(
    mean: np.ndarray, sd: np.ndarray, corr: float, n: int, points: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Sample mean vectors and sample covariances over n blocks of the five variables, for each row of points (20
    columns): m = mean + L z / sqrt(n) and S = L A A' L' / (n - 1) with A the Bartlett factor, which is the exact
    joint law of the sample mean and covariance of n draws of N(mean, L L')."""
    k = len(mean)
    cov = np.diag(sd**2)
    for i in range(4):
        for j in range(4):
            if i != j:
                cov[i, j] = corr * sd[i] * sd[j]
    chol = np.linalg.cholesky(cov)
    df = n - 1
    z = _normal_quasi(points[:, :k])
    chi = np.stack([np.sqrt(stats.chi2.ppf(points[:, k + i], df - i)) for i in range(k)], axis=1)
    off = _normal_quasi(points[:, 2 * k :]).reshape(len(points), -1)
    factor = np.zeros((len(points), k, k))
    factor[:, np.arange(k), np.arange(k)] = chi
    row, col = np.tril_indices(k, -1)
    factor[:, row, col] = off[:, : len(row)]
    lower = chol @ factor
    means = mean + z @ chol.T / math.sqrt(n)
    covs = lower @ lower.transpose(0, 2, 1) / df
    return means, covs


def operating_characteristics(
    power: dict[str, Any], compile_record: dict[str, Any], log2: int = OPERATING_LOG2_TRIALS
) -> dict[str, Any]:
    """Probability of each reading of the rule, and of the superseded rule that decides (ii) through diff_cm, when the
    truth is a model floor of the compile record (relaxation alone, all three noise models) with and without an
    operand-following effect of the retained size, over PLANNED_REGIONS region means at each rho in RHOS. The scatter is
    the retained one (power['operands']), equicorrelated across the four gaps with the retained pair correlation, the
    scatter of leak16 is LEAK_SD / sqrt(JOBS); the 2 x 20 columns of each trial are deterministic Sobol points."""
    models = compile_record["relaxation"]["statistics"]
    bands = floor_band_edges(compile_record)
    scenarios: dict[str, dict[str, Any]] = {
        "null": {"model": None, "effect": 0.0},
        "relaxation_only": {"model": "relaxation_only", "effect": 0.0},
        "all_three_models": {"model": "depolarizing_relaxation_asymmetric_readout", "effect": 0.0},
        "all_three_models_plus_half_effect": {"model": "depolarizing_relaxation_asymmetric_readout", "effect": 0.5},
        "all_three_models_plus_full_effect": {"model": "depolarizing_relaxation_asymmetric_readout", "effect": 1.0},
    }
    points = _unit_points(40, log2)
    out: dict[str, Any] = {}
    for scenario, spec in scenarios.items():
        for rho in power["rhos"]:
            per_operand = {}
            for oi, operand in enumerate(pko.OPERANDS):
                t = tag(operand)
                s = power["operands"][t]
                sd_gap = _design_sd(s["sd_per_replica"], rho)
                r = float(min(max(s["pair_correlation"], 0.0), 0.9))
                sd_vec = np.array([sd_gap, sd_gap, sd_gap, sd_gap, power["leak_sd"] / math.sqrt(JOBS)])
                mean = np.zeros(5)
                if spec["model"] is not None:
                    mean = np.array([models[spec["model"]][f"{v}:{t}"]["mean"] for v in _VARIABLES])
                mean = mean + np.array([1, 1, 1, 1, 0]) * spec["effect"] * s["effect"]
                per_operand[t] = _summaries(
                    mean, sd_vec, r, power["planned_regions"], points[:, 20 * oi : 20 * oi + 20]
                )
            for rule, names, key in (
                ("band_rule", STATISTICS, "diff_cm"),
                ("superseded_rule", OLD_STATISTICS, "diff_cm"),
            ):
                counts: dict[str, dict[str, int]] = {"row": {}, **{tag(o): {} for o in pko.OPERANDS}}
                stays = {tag(o): 0 for o in pko.OPERANDS}
                n_blocks = power["planned_regions"]
                for trial in range(len(points)):
                    tests: dict[str, dict[str, Any]] = {}
                    for operand in pko.OPERANDS:
                        t = tag(operand)
                        m, cov = per_operand[t][0][trial], per_operand[t][1][trial]
                        lo, hi = (bands[t]["lower"], bands[t]["upper"]) if rule == "band_rule" else (0.0, 0.0)
                        for name in names:
                            w = np.asarray(_WEIGHTS[name], dtype=float)
                            mean_, se_ = float(w @ m), float(math.sqrt(w @ cov @ w / n_blocks))
                            if name == "diff_cm":
                                tests[f"{name}:{t}"] = _band_from_summary(mean_, se_, n_blocks, lo, hi)
                            else:
                                tests[f"{name}:{t}"] = _from_summary(mean_, se_, n_blocks)
                    decide_tests(tests)
                    reads = [readings(tests, o, n_blocks - 1, key) for o in pko.OPERANDS]
                    for o, read in zip(pko.OPERANDS, reads, strict=True):
                        bucket = counts[tag(o)]
                        bucket[read["verdict"]] = bucket.get(read["verdict"], 0) + 1
                        stays[tag(o)] += int(read["ii_gap_stays_on_bit_4"])
                    row = row_verdict([r["verdict"] for r in reads])
                    counts["row"][row] = counts["row"].get(row, 0) + 1
                total = float(len(points))
                out.setdefault(scenario, {}).setdefault(f"rho{int(rho)}", {})[rule] = {
                    "row_verdict": {k: v / total for k, v in sorted(counts["row"].items())},
                    "operands": {
                        t: {
                            "verdict": {k: v / total for k, v in sorted(counts[t].items())},
                            "reading_ii": stays[t] / total,
                        }
                        for t in stays
                    },
                }
    return {
        "schema": "orientation-bit-operating-v1",
        "trials_per_cell": 2**log2,
        "regions": power["planned_regions"],
        "sampling": "exact law of the sample mean and covariance (Bartlett factor) at deterministic Sobol points",
        "model_source": "case_compile.json relaxation block; retained scatter of power.json",
        "scenarios": out,
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
    swap: dict[str, float] | None = None,
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
    dead carry the visibility -0.1 and gap_regions ("all", "dead" or "live") names the replicas that carry the gaps.
    The swap unit carries the control's gaps unless swap is given (a gap that travels with the bit-4 wire)."""
    group = pko.pathion_kernel_map_orientation_group()
    ideal = {m.name: np.asarray(m.ideal, dtype=float) for m in group.members}
    measured: dict[str, list[list[float]]] = {m.name: [] for m in group.members}
    gaps = {"ctrl": ctrl, "move": move, "xtwin": xtwin, "swap": ctrl if swap is None else swap}
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


def self_test(collect: Any, compile_record: dict[str, Any] | None = None) -> list[str]:
    done = []
    n, sd = 40, 0.08
    ops = {tag(o): o for o in pko.OPERANDS}
    follow: dict[str, float] = {f"16:{t}": 0.12 * RETAINED_SIGN[o] for t, o in ops.items()}
    ctrl_gap = dict(follow)
    xtwin_gap = dict(follow)  # operand-following: the exchange keeps the sign
    move_gap = {f"2:{t}": 0.12 * RETAINED_SIGN[o] for t, o in ops.items()}
    result = analyze_flat(synthetic_entry(n, sd, ctrl_gap, move_gap, xtwin_gap))
    got = [r["verdict"] for r in result["readings"]]
    nb.expect(got == ["supported", "supported"], f"operand-following effect read as {got}")
    nb.expect(all(r["iii_exchange"] == "operand-following" for r in result["readings"]), "exchange reading")
    nb.expect(not any(r["leakage_into_character_16"] for r in result["readings"]), "shot-scale leakage was rejected")
    done.append("an injected operand-following gap on bit 4 and on bit 1 reads supported on both operands")
    null = analyze_flat(synthetic_entry(n, sd, {}, {}, {}))
    nb.expect(all(r["verdict"] == "unresolved" for r in null["readings"]), "a null run was not unresolved")
    nb.expect(not any(t["reject"] for t in null["tests"].values()), "a null run rejected a test")
    done.append("a run with no gap rejects no test of the 16 (known-bad input of the rule)")
    stays = analyze_flat(synthetic_entry(n, sd, ctrl_gap, {}, xtwin_gap))
    nb.expect(all(r["verdict"] == "refuted" and r["ii_gap_stays_on_bit_4"] for r in stays["readings"]), "stays on 16")
    nb.expect(not any(r["leakage_into_character_16"] for r in stays["readings"]), "stays: spurious leakage")
    done.append("a replicated gap on bit 4 with none on bit 1 reads refuted as stated (reading ii), through C")
    bound = analyze_flat(synthetic_entry(n, sd, ctrl_gap, {}, xtwin_gap, swap={}))
    nb.expect(
        all(r["layout_bound_candidate"] and not r["gap_travels_with_bit_4_wire"] for r in bound["readings"]), "layout"
    )
    nb.expect(all(r["verdict"] == "refuted" for r in bound["readings"]), "a gap on the physical qubit stayed open")
    done.append("a gap that stays on the physical qubit of bit 4 (none on the swap unit) reads (ii) and layout-bound")
    n2, sd2 = 60, 0.1
    weak_move = {f"2:{t}": 0.03 * RETAINED_SIGN[o] for t, o in ops.items()}
    flat_floor = analyze_flat(synthetic_entry(n2, sd2, ctrl_gap, weak_move, xtwin_gap))
    nb.expect(
        all(r["ii_gap_stays_on_bit_4"] for r in flat_floor["readings"]), "a floor was not read as (ii) at zero band"
    )
    edge = {t: 0.09 * RETAINED_SIGN[o] for t, o in ops.items()}  # C = G16 - G2 of the weak moved gap
    band = {t: {"lower": [min(0.0, e) - 0.03] * n2, "upper": [max(0.0, e) + 0.03] * n2} for t, e in edge.items()}
    banded = analyze(synthetic_entry(n2, sd2, ctrl_gap, weak_move, xtwin_gap), band)
    nb.expect(
        not any(r["ii_gap_stays_on_bit_4"] for r in banded["readings"]), "a floor inside the band was read as (ii)"
    )
    nb.expect(all(r["verdict"] == "unresolved" for r in banded["readings"]), "a floor inside the band was decided")
    narrow = {t: {"lower": [-0.02] * n2, "upper": [0.02] * n2} for t in edge}
    beyond = analyze(synthetic_entry(n2, sd2, ctrl_gap, weak_move, xtwin_gap), narrow)
    nb.expect(all(r["ii_gap_stays_on_bit_4"] for r in beyond["readings"]), "a difference beyond the band was lost")
    short = {t: {"lower": [0.0], "upper": [0.0]} for t in band}
    try:
        analyze(synthetic_entry(n2, sd2, ctrl_gap, weak_move, xtwin_gap), short)
    except ValueError:
        pass
    else:
        raise ValueError("a band of the wrong length was accepted")
    done.append("a floor of C inside its band reads as the gap following; a C beyond the band reads (ii)")
    smaller = analyze_flat(synthetic_entry(n, sd, ctrl_gap, {k: v / 3.0 for k, v in move_gap.items()}, xtwin_gap))
    nb.expect(all(r["verdict"] != "supported" for r in smaller["readings"]), "a third-size moved gap was supported")
    done.append("a moved gap of one third the size is not read as supported")
    leaked = analyze_flat(synthetic_entry(n, sd, ctrl_gap, move_gap, xtwin_gap, leak_mean=0.1))
    nb.expect(all(r["leakage_into_character_16"] for r in leaked["readings"]), "leakage of 0.1 was not rejected")
    nb.expect(all(r["verdict"] == "supported" for r in leaked["readings"]), "leakage alone changed the verdict")
    done.append("leakage into character 16 is reported and leaves the verdict to G2 and C")
    flip_x = {k: -v for k, v in follow.items()}
    state = analyze_flat(synthetic_entry(n, sd, ctrl_gap, move_gap, flip_x))
    nb.expect(all(r["iii_exchange"] == "state-dependent" for r in state["readings"]), "state-dependent exchange")
    nb.expect(all(r["verdict"] == "unresolved" for r in state["readings"]), "a state-dependent exchange is supported")
    done.append("a gap whose sign flips under the exchange reads state-dependent and leaves A5-242 unresolved")
    inverted = analyze_flat(synthetic_entry(n, sd, {k: -v for k, v in follow.items()}, {}, {}))
    nb.expect(all(r["verdict"] == "refuted" for r in inverted["readings"]), "an inverted retained sign is not refuted")
    done.append("a replicated gap of the opposite sign reads refuted")
    nb.expect(row_verdict(["supported", "supported"]) == "supported", "row rule: both supported")
    nb.expect(row_verdict(["supported", "unresolved"]) == "unresolved", "row rule: one supported")
    nb.expect(row_verdict(["supported", "refuted"]) == "refuted", "row rule: one refuted")
    nb.expect(row_verdict(["unresolved", "refuted"]) == "refuted", "row rule: refuted outranks unresolved")
    nb.expect(result["row"]["verdict"] == "supported" and null["row"]["verdict"] == "unresolved", "analyze row")
    done.append("the row reads supported only when both operands do, refuted when either is, else unresolved")
    dead = tuple(range(0, n, 5)) + tuple(range(1, n, 5))  # 40 percent of the regions
    live_gap = analyze_flat(synthetic_entry(n, sd, ctrl_gap, move_gap, xtwin_gap, dead=dead, gap_regions="live"))
    nb.expect(live_gap["regions"]["dead"] == sorted(dead) and live_gap["regions"]["rule_applied"], "dead regions")
    nb.expect(all(r["verdict"] == "supported" for r in live_gap["readings"]), "live-region effect was lost")
    done.append("a gap carried by the live regions survives the dead-region rule (more than one third dead)")
    big = [{k: 2.5 * v for k, v in g.items()} for g in (ctrl_gap, move_gap, xtwin_gap)]
    dead_gap = analyze_flat(synthetic_entry(n, sd, big[0], big[1], big[2], dead=dead, gap_regions="dead"))
    nb.expect(all(r["verdict_all_regions"] == "supported" for r in dead_gap["readings"]), "all-region run: no gap")
    nb.expect(all(r["verdict_live_regions"] == "unresolved" for r in dead_gap["readings"]), "live run read a gap")
    nb.expect(all(r["verdict"] == "unresolved" for r in dead_gap["readings"]), "a dead-region gap counted")
    nb.expect(dead_gap["row"]["verdict"] == "unresolved", "the row counted a dead-region gap")
    done.append("a gap carried only by regions with visibility under 0.05 is not counted when they exceed one third")
    few = analyze_flat(synthetic_entry(n, sd, big[0], big[1], big[2], dead=dead[:2], gap_regions="dead"))
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
    if collect is not None and compile_record is not None:
        power = power_record(collect, compile_record)
        for o in power["operands"].values():
            for stat in ("ctrl_g16", "move_g2", "swap_g16"):
                nb.expect(o["statistics"][stat]["regions_rho1"]["power_full_effect"] >= POWER, f"power of {stat}")
        done.append(f"{PLANNED_REGIONS} regions read {JOBS} times give power at least {POWER} for the three gaps")
    return done


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--power", type=Path, metavar="DIR")
    mode.add_argument("--operating", type=Path, metavar="DIR")
    mode.add_argument("--analyze", type=Path, metavar="COLLECT", nargs="+")
    ap.add_argument("--regions", type=Path, nargs="+", help="JSON list of region qubit lists per collected job")
    ap.add_argument(
        "--floors", type=Path, nargs="+", help="per job, the floors.json of compile_case.py --floors-from (required)"
    )
    ap.add_argument("--retained-collect", type=Path, help=f"{RETAINED_COLLECT}, read by --power and --self-test")
    ap.add_argument("--readout-errors", type=Path, help="JSON list: readout error of the bit-4 qubit per replica")
    args = ap.parse_args()
    retained = json.loads(args.retained_collect.read_text()) if args.retained_collect else None
    if args.self_test:
        compile_path = HERE / "case_compile.json"
        for line in self_test(retained, json.loads(compile_path.read_text()) if compile_path.is_file() else None):
            print(f"ok: {line}")
        return 0
    if args.power:
        if retained is None:
            ap.error("--power needs --retained-collect")
        record = power_record(retained, json.loads((args.power / "case_compile.json").read_text()))
        record["retained_collect_sha256"] = hashlib.sha256(args.retained_collect.read_bytes()).hexdigest()
        (args.power / "power.json").write_text(json.dumps(record, indent=1, sort_keys=True) + "\n")
        return 0
    if args.operating:
        record = operating_characteristics(
            json.loads((args.operating / "power.json").read_text()),
            json.loads((args.operating / "case_compile.json").read_text()),
        )
        (args.operating / "operating.json").write_text(json.dumps(record, indent=1, sort_keys=True) + "\n")
        return 0
    entries = []
    for path in args.analyze:
        collect = json.loads(path.read_text())
        items = collect if isinstance(collect, list) else [collect]
        found = next(x for x in items if isinstance(x, dict) and x.get("group") in ORIENTATION_GROUPS)
        members = {m.name for m in entry_group(found["group"]).members}
        entries.append({**found, "measured": {k: v for k, v in found["measured"].items() if k in members}})
    regions = [json.loads(p.read_text()) for p in args.regions] if args.regions else None
    errors = json.loads(args.readout_errors.read_text()) if args.readout_errors else None
    if not args.floors:
        ap.error("--analyze needs --floors: the floor band of C comes from the dry-run calibration of each region")
    floor_sets = [json.loads(p.read_text()) for p in args.floors]
    entry, floors = merge_jobs(entries, regions, floor_sets)
    if floors is None:
        raise ValueError("no floors")
    print(json.dumps(analyze(entry, floors, errors), indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
