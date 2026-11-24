"""Analysis and preregistered decision rule of the orientation-bit case.

The case is written in docs/design/pathion-kernel-map-orientation-bit.md.

The case asks whether the paired character gap lambda_16 - lambda_0 of the ibm_fez kernel map follows the orientation
qubit. For one operand it reads three units of group pathion_kernel_map_orientation over replicas (disjoint chip
regions): ctrl (orientation on bit 4), move (orientation on bit 1) and xtwin (ctrl with one X on data qubit 4 before
readout). Per replica, with lambda_a = c^_obs,a / c^_ideal,a on the Walsh support of the ideal contrast
(nhat_spectral.coefficients, nhat_spectral.unit_spectrum; this module reuses both):

    ctrl   G16  = lambda_16 - lambda_0
    move   G2   = lambda_2 - lambda_0            (character 2^b of the moved orientation bit b = 1)
    move   L16  = c^_obs,16 / c^_obs,0           (character 16 lies outside the ideal support: leakage, ideal 0)
    xtwin  G16  = lambda_16 - lambda_0 against the exchanged ideal
    S = (G16_ctrl + G16_xtwin) / 2               the part that keeps its sign under the exchange (follows the operand)
    D = (G16_ctrl - G16_xtwin) / 2               the part that flips its sign under the exchange (follows the qubit)

Each statistic is a one-sample t test over replicas with n - 1 degrees of freedom, whose standard error is the scatter
of the replica values, so the test holds whatever drift the device has between regions. Two operands and six
statistics make the family of 12 tests; Holm's step-down procedure holds the family error at ALPHA.

Modes:
    "$PYTHON" orientation_bit_analysis.py --self-test        decision rule on injected effects, with controls
    "$PYTHON" orientation_bit_analysis.py --power DIR        replica count from the retained scatter (DIR/power.json)
    "$PYTHON" orientation_bit_analysis.py --analyze COLLECT  verdicts of a collected run (collect.json of live_run)
"""

from __future__ import annotations

import argparse
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
FAMILY = 12
# Regions (disjoint six-qubit tiles) one run places at the retained replica floor, and the runs of the case.
REGIONS_PER_RUN = 5
RUNS = 3
RETAINED_RUN = "ibm_fez kernel map"
# Equivalence bound on the leakage of character 16 in the moved member: a reading inside it counts as none.
LEAKAGE_BOUND = 0.05
STATISTICS = ("ctrl_g16", "move_g2", "move_l16", "xtwin_g16", "keep_s", "flip_d")
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
        "move_l16": co_m[:, 16] / co_m[:, 0],
        "xtwin_g16": g_x,
        "keep_s": (g_c + g_x) / 2.0,
        "flip_d": (g_c - g_x) / 2.0,
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
    """The three readings of one operand and the verdict on A5-242."""
    t = tag(operand)
    sign = RETAINED_SIGN[operand]
    row = {name: tests[f"{name}:{t}"] for name in STATISTICS}
    crit = float(stats.t.isf(0.05, df))
    replicates = bool(row["ctrl_g16"]["reject"] and np.sign(row["ctrl_g16"]["mean"]) == sign)
    flipped = bool(row["ctrl_g16"]["reject"] and np.sign(row["ctrl_g16"]["mean"]) == -sign)
    follows = bool(row["move_g2"]["reject"] and np.sign(row["move_g2"]["mean"]) == sign)
    leak = row["move_l16"]
    leak_none = bool(abs(leak["mean"]) + crit * leak["se"] < LEAKAGE_BOUND)
    stays = bool(leak["reject"] and not row["move_g2"]["reject"])
    keeps, flips = bool(row["keep_s"]["reject"]), bool(row["flip_d"]["reject"])
    state = (
        "mixture" if keeps and flips else "operand-following" if keeps else "state-dependent" if flips else "unresolved"
    )
    if flipped or stays:
        verdict = "refuted"
    elif replicates and follows and leak_none and state == "operand-following":
        verdict = "supported"
    else:
        verdict = "unresolved"
    return {
        "operand": t,
        "replicates_retained_sign": replicates,
        "sign_flipped": flipped,
        "i_gap_follows_orientation_qubit": follows and leak_none,
        "ii_gap_stays_on_bit_4": stays,
        "iii_exchange": state,
        "verdict": verdict,
    }


def units_from_entry(entry: dict[str, Any]) -> dict[str, nb.Unit]:
    """Units of one collected group entry: per unit the ideal sign and the replica contrasts of its two arms."""
    group = pko.pathion_kernel_map_orientation_group()
    if entry["group"] != group.name:
        raise ValueError(f"{entry['group']} is not {group.name}")
    ideal = {m.name: np.asarray(m.ideal, dtype=float) for m in group.members}
    measured = {name: np.asarray(v, dtype=float) for name, v in entry["measured"].items()}
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


def analyze(entry: dict[str, Any]) -> dict[str, Any]:
    units = units_from_entry(entry)
    cross_check(units)
    tests = family_tests(units)
    n = next(iter(tests.values()))["n"]
    return {
        "schema": "orientation-bit-analysis-v1",
        "replicas": n,
        "alpha": ALPHA,
        "family": FAMILY,
        "tests": tests,
        "readings": [readings(tests, operand, n - 1) for operand in pko.OPERANDS],
    }


# ------------------------------------------------------------------------------------------------------- power


def retained_scatter() -> dict[str, dict[str, float]]:
    """Per-replica effect and standard deviation of the character-16 gap of the two case operands in the retained
    ibm_fez run: the replica standard error is minus_zero / minus_zero_t of five replicas."""
    record = json.loads((HERE.parent / "nhat-bias" / "result_spectral.json").read_text())
    run = next(r for r in record["runs"] if r["name"] == RETAINED_RUN)
    out = {}
    for operand, key in RETAINED_KEY.items():
        unit = next(u for u in run["units"] if u["key"] == key)
        c = next(c for c in unit["characters"] if c["character"] == 16)
        se = abs(c["minus_zero"] / c["minus_zero_t"])
        out[tag(operand)] = {"effect": c["minus_zero"], "se_five_replicas": se, "sd_per_replica": se * math.sqrt(5)}
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


def required_replicas(delta: float, sd: float, alpha: float, power: float = POWER, nmax: int = 400) -> int:
    for n in range(2, nmax):
        if power_at(delta, sd, n, alpha) >= power:
            return n
    raise ValueError("no replica count up to nmax reaches the power")


def power_record() -> dict[str, Any]:
    scatter = retained_scatter()
    alpha = ALPHA / FAMILY
    rows = {}
    for name, s in scatter.items():
        full, half = abs(s["effect"]), abs(s["effect"]) / 2.0
        sd = s["sd_per_replica"]
        rows[name] = {
            **s,
            "n_full_effect": required_replicas(full, sd, alpha),
            "n_half_effect": required_replicas(half, sd, alpha),
            # S and D average two gaps of equal scatter; uncorrelated gaps give them scatter sd / sqrt(2). S at the
            # retained effect is the operand-following alternative and D the state-dependent one.
            "n_keep_s_or_flip_d_at_full_effect": required_replicas(full, sd / math.sqrt(2.0), alpha),
        }
    needed = max(r["n_full_effect"] for r in rows.values())
    n = RUNS * REGIONS_PER_RUN
    if n < needed:
        raise ValueError(f"{RUNS} runs of {REGIONS_PER_RUN} regions give {n} replicas, fewer than the {needed} needed")
    for r in rows.values():
        r["power_at_n_full_effect"] = power_at(r["effect"], r["sd_per_replica"], n, alpha)
        r["power_at_n_half_effect"] = power_at(r["effect"] / 2.0, r["sd_per_replica"], n, alpha)
        r["minimum_detectable_effect_at_n"] = next(
            d / 1000.0 for d in range(1, 1000) if power_at(d / 1000.0, r["sd_per_replica"], n, alpha) >= POWER
        )
    return {
        "schema": "orientation-bit-power-v1",
        "alpha_family": ALPHA,
        "tests_in_family": FAMILY,
        "alpha_per_test": alpha,
        "power": POWER,
        "operands": rows,
        "replicas_needed": needed,
        "replicas": n,
        "runs": RUNS,
        "regions_per_run": REGIONS_PER_RUN,
        "source": "nhat-bias/result_spectral.json, run ibm_fez kernel map, character 16",
    }


# --------------------------------------------------------------------------------------------------- self-test


def _noise(n: int, sd: float, phase: int) -> np.ndarray:
    """Deterministic zero-mean replica scatter of standard deviation sd: normal quantiles at (i + 0.5) / n, cyclically
    shifted by phase so different statistics do not share one ordering."""
    q = stats.norm.ppf((np.arange(n) + 0.5) / n)
    q = np.roll(q, phase)
    return sd * (q - q.mean()) / q.std(ddof=1)


def synthetic_entry(
    n: int, sd: float, ctrl: dict[str, float], move: dict[str, float], xtwin: dict[str, float], visibility: float = 0.3
) -> dict[str, Any]:
    """A collect entry whose replicas carry lambda_a = visibility + gap_a + scatter on each unit's ideal support and
    gap_a set per unit (a dict of character to gap, 0 elsewhere): the arms are the ideal laws moved by +-c_obs / 2."""
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
        for r in range(n):
            lam = {a: visibility + gap_here[a] + (_noise(n, sd, phase + a)[r] if a else 0.0) for a in support}
            lam[0] = visibility + _noise(n, sd / 3.0, phase + 7)[r]
            c_obs = sum(lam[a] * ci[a] * walsh[a] for a in support)
            # two arms with selector-zero probability 1/2 -+ c_obs / 4 on each output: contrast c_obs exactly.
            for arm, shift in (("plus", 0.25), ("minus", -0.25)):
                law = np.zeros(64)
                half = ideal[f"{prefix}_{arm}"].size // 2
                weights = np.ones(32) / 32.0
                law[:half] = weights * (0.5 + shift * c_obs * 2.0 / 2.0)
                law[half:] = weights * (0.5 - shift * c_obs * 2.0 / 2.0)
                measured[f"{prefix}_{arm}"].append(law.tolist())
        phase += 3
    return {"group": group.name, "measured": measured}


def self_test() -> list[str]:
    done = []
    n, sd = 40, 0.08
    ops = {tag(o): o for o in pko.OPERANDS}
    follow: dict[str, float] = {}
    for t, o in ops.items():
        delta = 0.12 * RETAINED_SIGN[o]
        follow |= {f"16:{t}": delta}
    ctrl_gap = dict(follow)
    xtwin_gap = dict(follow)  # operand-following: the exchange keeps the sign
    move_gap = {f"2:{t}": 0.12 * RETAINED_SIGN[o] for t, o in ops.items()}
    result = analyze(synthetic_entry(n, sd, ctrl_gap, move_gap, xtwin_gap))
    got = [r["verdict"] for r in result["readings"]]
    nb.expect(got == ["supported", "supported"], f"operand-following effect read as {got}")
    nb.expect(all(r["iii_exchange"] == "operand-following" for r in result["readings"]), "exchange reading")
    done.append("an injected operand-following gap on bit 4 and on bit 1 reads supported on both operands")
    null = analyze(synthetic_entry(n, sd, {}, {}, {}))
    nb.expect(all(r["verdict"] == "unresolved" for r in null["readings"]), "a null run was not unresolved")
    nb.expect(not any(t["reject"] for t in null["tests"].values()), "a null run rejected a test")
    done.append("a run with no gap rejects no test (known-bad input of the rule)")
    stays = analyze(synthetic_entry(n, sd, ctrl_gap, {}, xtwin_gap))
    nb.expect(
        all(r["verdict"] == "unresolved" for r in stays["readings"]), "a moved member without a gap is not refuted"
    )
    done.append("a gap on bit 4 with no gap on bit 1 and no leakage reads unresolved, not supported")
    # Leakage into character 16 of the moved member needs a channel that is not character-diagonal; inject it on the
    # moved unit's contrast directly.
    entry = synthetic_entry(n, sd, ctrl_gap, {}, xtwin_gap)
    bump = 0.2
    for t in ops:
        key = f"kmo_move_{t}"
        for arm, sgn in (("plus", 1.0), ("minus", -1.0)):
            arr = np.asarray(entry["measured"][f"{key}_{arm}"])
            for y in range(32):
                arr[:, y] += sgn * 0.5 * bump * (-1) ** bin(y & 16).count("1") / 32.0 * 0.5
                arr[:, 32 + y] -= sgn * 0.5 * bump * (-1) ** bin(y & 16).count("1") / 32.0 * 0.5
            entry["measured"][f"{key}_{arm}"] = arr.tolist()
    leaked = analyze(entry)
    nb.expect(all(r["verdict"] == "refuted" and r["ii_gap_stays_on_bit_4"] for r in leaked["readings"]), "leakage")
    done.append("leakage into character 16 with no gap on bit 1 reads refuted as stated (reading ii)")
    flip_x = {k: -v for k, v in follow.items()}
    state = analyze(synthetic_entry(n, sd, ctrl_gap, move_gap, flip_x))
    nb.expect(all(r["iii_exchange"] == "state-dependent" for r in state["readings"]), "state-dependent exchange")
    nb.expect(all(r["verdict"] == "unresolved" for r in state["readings"]), "a state-dependent exchange is supported")
    done.append("a gap whose sign flips under the exchange reads state-dependent and leaves A5-242 unresolved")
    inverted = analyze(synthetic_entry(n, sd, {k: -v for k, v in follow.items()}, {}, {}))
    nb.expect(all(r["verdict"] == "refuted" for r in inverted["readings"]), "an inverted retained sign is not refuted")
    done.append("a replicated gap of the opposite sign reads refuted")
    pvalues = {"a": 0.001, "b": 0.02, "c": 0.04, "d": 0.5}
    nb.expect(holm(pvalues) == {"a": True, "b": False, "c": False, "d": False}, "Holm thresholds")
    nb.expect(holm({"a": 0.01, "b": 0.012}) == {"a": True, "b": True}, "Holm step-down")
    done.append("Holm rejects by the step-down thresholds alpha / (m - rank)")
    power = power_record()
    nb.expect(all(r["power_at_n_full_effect"] >= POWER for r in power["operands"].values()), "power at n")
    nb.expect(abs(power_at(0.0, 0.1, 10, 0.05) - 0.05) < 1e-6, "the power at zero effect is the size of the test")
    nb.expect(
        abs(power_at(0.09, 0.1, 12, 0.05) - float(stats.nct.sf(2.2009851, 11, 0.09 * 12**0.5 / 0.1))) < 2e-3,
        "power vs nct",
    )
    nb.expect(power_at(0.03, 0.1, 12, 0.05) < POWER, "a small effect reaches full power: the power function is flat")
    done.append(
        f"{power['replicas']} replicas give power at least {POWER} at the retained effects (exact noncentral t)"
    )
    return done


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--power", type=Path, metavar="DIR")
    mode.add_argument("--analyze", type=Path, metavar="COLLECT")
    args = ap.parse_args()
    if args.self_test:
        for line in self_test():
            print(f"ok: {line}")
        return 0
    if args.power:
        (args.power / "power.json").write_text(json.dumps(power_record(), indent=1, sort_keys=True) + "\n")
        return 0
    collect = json.loads(args.analyze.read_text())
    items = collect if isinstance(collect, list) else [collect]
    entry = next(x for x in items if isinstance(x, dict) and x.get("group") == "pathion_kernel_map_orientation")
    print(json.dumps(analyze(entry), indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
