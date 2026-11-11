"""Analysis 3: Belenos per-mode efficiency across plan-time calibration sessions.

Falsifier, fixed before computing. "No structure" is: (a) between runs that returned byte-identical compiled
circuits for every iteration (the frozen BDSC request), the per-mode single-click shares differ only by
multinomial noise, so the generalized Cochran-Mantel-Haenszel statistic of run against detector mode, stratified by
setting, has no excess over its chi-square null; (b) in the model-based fits (scripts/qd_belenos_mesh.fit_efficiency
on the ideal-mesh prediction of each returned circuit) the log-efficiencies of different plan-time sessions agree
within the Fisher interval, widened by the sessions' own jackknife spread; (c) the DetectorBalancing contrast, the
default-mitigation and mitigation-none runs on one plan-time record, differ by no more than binomial noise.

What the counts identify. Quandela returns click counts per output mode. A multiplicative per-mode factor common
to every setting (detector efficiency, output transmission, mode-dependent loss) is identifiable only up to one
overall scale and only relative to the other modes; it is not separable from a static routing offset of the mesh
(the repository's own held-out fits reject the ideal mesh model, strategy.md section 2) or from dark and stray
clicks, which load modes 0, 1 and 5. An absolute efficiency is not identified, because every setting carries a
free scale. Counts passed the service's default DetectorBalancing correction, which uses detector and output-loss
models of its own, so fitted efficiencies describe what remains after that correction.
The frozen-request design separates the two readings: a change in detector efficiency predicts one factor per mode
shared by all 24 settings, a change in mesh phases predicts setting-specific changes.

Nulls are analytic (chi-square, normal). No random draw.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from typing import Any

import common as c
import numpy as np
import qd_belenos_mesh as mesh
from scipy import stats

import qd_records as qd

MODES = 24
STRAY_MODES = (0, 1, 5)


def plan_vectors(submission: dict[str, Any]) -> tuple[list[float], list[float]]:
    perfs = submission.get("perfs_at_plan", {})
    t_out = (perfs.get("Transmission per mode (%)") or {}).get("t_out") or [float("nan")] * MODES
    dark = perfs.get("Dark counts (detection/s)") or [float("nan")] * MODES
    return list(map(float, t_out)), list(map(float, dark))


def read_runs() -> list[dict[str, Any]]:
    runs = []
    arch_ref = None
    for directory in qd.run_directories():
        if "qpu_belenos" not in directory.name:
            continue
        run = qd.read_run(directory)
        its = [i for i in (run.collected.get("iterations") or []) if "counts" in i and i.get("result_fields")]
        if not its or run.collected["status"]["status"] != "completed":
            continue
        inputs = [i["result_fields"]["computed_input"] for i in its]
        if any(sum(int(x) for x in s.split("|")[1].rstrip(">").split(",")) != 1 for s in inputs):
            continue
        circuits = [i["result_fields"]["computed_circuit"] for i in its]
        arch = mesh.run_architecture(mesh.decode(circuits[0]))
        arch_ref = arch_ref or arch
        singles = np.zeros((len(its), MODES))
        other = np.zeros(len(its))
        probs = np.zeros((len(its), MODES))
        for k, it in enumerate(its):
            for state, n in it["counts"].items():
                v = [int(x) for x in state.split(",")]
                if sum(v) == 1:
                    singles[k, v.index(1)] += n
                else:
                    other[k] += n
            src = [int(x) for x in inputs[k].split("|")[1].rstrip(">").split(",")].index(1)
            phases = mesh.mesh_phases(arch_ref, mesh.decode(circuits[k]))
            probs[k] = mesh.propagate(arch_ref, phases, src)[0]
        t_out, dark = plan_vectors(run.submission)
        key = hashlib.sha256(json.dumps([t_out, dark]).encode()).hexdigest()[:6]
        runs.append(
            {
                "run": c.rel(directory),
                "name": directory.name,
                "family": run.manifest.get("family"),
                "submitted": run.submission["submitted_utc"],
                "plan_key": key,
                "t_out": t_out,
                "dark": dark,
                "circuit_hashes": [
                    hashlib.sha256((circuits[k] + inputs[k]).encode()).hexdigest()[:10] for k in range(len(its))
                ],
                "singles": singles,
                "other": other,
                "probs": probs,
                "mitigation": "none" if "-none-" in directory.name else "default",
            }
        )
    runs.sort(key=lambda r: r["submitted"])
    return runs


# ---------- Part 1: identical-circuit contrasts (model-free) ----------


def cmh_pair(a: np.ndarray, b: np.ndarray, min_total: int = 200, exclude: tuple[int, ...] = ()) -> dict[str, Any]:
    """Generalized CMH of run (a, b) against mode, strata = settings, plus per-mode Mantel-Haenszel log odds ratios."""
    allowed = np.array([m_ not in exclude for m_ in range(MODES)])
    a, b = a * allowed, b * allowed
    keep = [i for i in range(a.shape[0]) if a[i].sum() >= min_total and b[i].sum() >= min_total]
    cols = np.flatnonzero((a[keep] + b[keep]).sum(axis=0) > 0)
    delta = np.zeros(len(cols))
    vsum = np.zeros((len(cols), len(cols)))
    q_total = 0.0
    dof_total = 0
    for i in keep:
        row_a, row_b = a[i, cols], b[i, cols]
        n1, n2 = row_a.sum(), row_b.sum()
        t = n1 + n2
        col = row_a + row_b
        e1 = n1 * col / t
        delta += row_a - e1
        vsum += n1 * n2 / (t * t * (t - 1)) * (t * np.diag(col) - np.outer(col, col))
        # Pearson homogeneity of this setting with Cochran pooling of columns expected below 5 in either run
        exp_a, exp_b = n1 * col / t, n2 * col / t
        ok = np.minimum(exp_a, exp_b) >= 5
        if ok.sum() >= 1:
            pa, pb = row_a[ok], row_b[ok]
            ra, rb = n1 - pa.sum(), n2 - pb.sum()
            ea, eb = exp_a[ok], exp_b[ok]
            era, erb = n1 - ea.sum(), n2 - eb.sum()
            terms = [(pa, ea), (pb, eb)]
            q = sum(float((((o - e) ** 2) / e).sum()) for o, e in terms)
            if era >= 5 and erb >= 5:
                q += (ra - era) ** 2 / era + (rb - erb) ** 2 / erb
                dof = int(ok.sum())
            else:
                dof = int(ok.sum()) - 1
            q_total += q
            dof_total += max(dof, 0)
    rank = int(np.linalg.matrix_rank(vsum, tol=1e-8 * max(1.0, np.abs(vsum).max())))
    q_cmh = float(delta @ np.linalg.pinv(vsum, rcond=1e-10) @ delta) if rank else float("nan")
    # Mantel-Haenszel odds ratio of mode m (B against A), Robins-Breslow-Greenland variance
    mh = {}
    for m_ in range(MODES):
        r_sum = s_sum = 0.0
        pr = ps_ = qs = 0.0
        for i in keep:
            x, y = a[i, m_], b[i, m_]
            n1, n2 = a[i].sum(), b[i].sum()
            t = n1 + n2
            r = y * (n1 - x) / t
            s = x * (n2 - y) / t
            p_ = (y + (n1 - x)) / t
            q_ = (x + (n2 - y)) / t
            r_sum += r
            s_sum += s
            pr += p_ * r
            ps_ += p_ * s + q_ * r
            qs += q_ * s
        if r_sum > 0 and s_sum > 0:
            var = pr / (2 * r_sum**2) + ps_ / (2 * r_sum * s_sum) + qs / (2 * s_sum**2)
            mh[m_] = (math.log(r_sum / s_sum), math.sqrt(var))
    return {
        "strata": len(keep),
        "columns": int(len(cols)),
        "q_cmh": q_cmh,
        "cmh_dof": rank,
        "q_total": q_total,
        "total_dof": dof_total,
        "mh": mh,
        "samples_a": float(a[keep].sum()),
        "samples_b": float(b[keep].sum()),
    }


def part1(runs: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    sets: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for r in runs:
        sets[tuple(r["circuit_hashes"])].append(r)
    ledger, details, mode_rows = [], [], []
    for index, (_, members) in enumerate(s for s in sets.items() if len(s[1]) >= 2):
        members.sort(key=lambda r: r["submitted"])
        for left, right in zip(members[:-1], members[1:], strict=True):
            res = cmh_pair(left["singles"], right["singles"])
            res_ex = cmh_pair(left["singles"], right["singles"], exclude=STRAY_MODES)
            same_epoch = left["plan_key"] == right["plan_key"]
            tag = f"set{index}:{left['name'][:19]}>{right['name'][:19]}"
            detail = {
                "set": index,
                "left": left["run"],
                "right": right["run"],
                "same_plan_epoch": same_epoch,
                "samples_each": [c.sig(res["samples_a"]), c.sig(res["samples_b"])],
            }
            for label, r_ in (("all_modes", res), ("stray_modes_0_1_5_excluded", res_ex)):
                log10_cmh = c.chi2_log10_sf(r_["q_cmh"], r_["cmh_dof"]) if r_["cmh_dof"] else 0.0
                resid_q = r_["q_total"] - r_["q_cmh"]
                resid_dof = r_["total_dof"] - r_["cmh_dof"]
                log10_res = c.chi2_log10_sf(resid_q, resid_dof) if resid_dof > 0 else 0.0
                detail[label] = {
                    "strata": r_["strata"],
                    "q_cmh": c.sig(r_["q_cmh"]),
                    "cmh_dof": r_["cmh_dof"],
                    "q_residual": c.sig(resid_q),
                    "residual_dof": resid_dof,
                    "q_total": c.sig(r_["q_total"]),
                    "total_dof": r_["total_dof"],
                }
                ledger.append(
                    c.ledger_row(
                        f"A3.cmh[{label}]." + tag,
                        3,
                        "common per-mode factor between two runs of identical circuits "
                        f"({'same' if same_epoch else 'different'} plan epoch, {label}): generalized CMH, run against "
                        "mode over settings",
                        log10_cmh,
                        {
                            "q_cmh": c.sig(r_["q_cmh"]),
                            "dof": r_["cmh_dof"],
                            "q_over_dof": c.sig(r_["q_cmh"] / max(r_["cmh_dof"], 1)),
                        },
                        None,
                        "chi-square null; efficiency-type change",
                    )
                )
                ledger.append(
                    c.ledger_row(
                        f"A3.res[{label}]." + tag,
                        3,
                        f"setting-specific change between the same runs ({label}): total homogeneity chi-square minus "
                        "the CMH common-factor part",
                        log10_res,
                        {
                            "q_residual": c.sig(resid_q),
                            "dof": resid_dof,
                            "q_over_dof": c.sig(resid_q / max(resid_dof, 1)),
                        },
                        None,
                        "approximate: difference of Pearson statistics; phase or mixing change",
                    )
                )
            details.append(detail)
            # per-mode reading
            mh = res["mh"]
            lor = {m_: v[0] for m_, v in mh.items()}
            centre = (
                float(np.median([lor[m_] for m_ in lor if mh[m_][1] < 0.1]))
                if any(v[1] < 0.1 for v in mh.values())
                else 0.0
            )
            dt = np.array(right["t_out"]) / np.array(left["t_out"])
            for m_, (val, se) in sorted(mh.items()):
                mode_rows.append(
                    {
                        "pair": tag,
                        "same_plan_epoch": same_epoch,
                        "mode": m_,
                        "ln_odds_ratio_B_over_A": c.sig(val, 4),
                        "se": c.sig(se, 3),
                        "z_raw": c.sig(val / se, 4),
                        "ln_odds_ratio_centered": c.sig(val - centre, 4),
                        "ln_plan_t_out_ratio": c.sig(float(math.log(dt[m_])), 4)
                        if np.isfinite(dt[m_]) and dt[m_] > 0
                        else None,
                    }
                )
    return ledger, details, mode_rows


# ---------- Part 2: model-based session fits ----------


def fisher_log_eta(p: np.ndarray, counts: np.ndarray, eta: np.ndarray) -> np.ndarray:
    """Covariance of ln eta (geometric mean fixed) from the multinomial information sum_s N_s (diag q - q q^T)."""
    info = np.zeros((MODES, MODES))
    for ps, ns in zip(p, counts, strict=True):
        n = ns.sum()
        w = eta * ps
        if w.sum() <= 0 or n <= 0:
            continue
        q = w / w.sum()
        info += n * (np.diag(q) - np.outer(q, q))
    proj = np.eye(MODES) - np.ones((MODES, MODES)) / MODES
    return proj @ np.linalg.pinv(info, rcond=1e-9) @ proj


def session_fit(rows: list[dict[str, Any]]) -> dict[str, Any]:
    p = np.vstack([r["probs"] for r in rows])
    n = np.vstack([r["singles"] for r in rows])
    eta = mesh.fit_efficiency(p, n)
    cov = fisher_log_eta(p, n, eta)
    q = (eta * p) / (eta * p).sum(axis=1, keepdims=True)
    expected = n.sum(axis=1, keepdims=True) * q
    ok = expected >= 5
    pearson = float((((n - expected) ** 2 / np.maximum(expected, 1e-300))[ok]).sum())
    dof = int(ok.sum() - len(rows) - (MODES - 1))
    jack = None
    if len(rows) >= 3:
        # jackknife over runs: refit leaving one run out, in log scale
        log_list = []
        for leave in range(len(rows)):
            keep = [r for k, r in enumerate(rows) if k != leave]
            e = mesh.fit_efficiency(np.vstack([r["probs"] for r in keep]), np.vstack([r["singles"] for r in keep]))
            log_list.append(np.log(e))
        logs = np.array(log_list)
        m = len(rows)
        jack = np.sqrt((m - 1) / m * ((logs - logs.mean(axis=0)) ** 2).sum(axis=0))
    light = (p * (n.sum(axis=1, keepdims=True) > 0)).sum(axis=0)
    return {
        "eta": eta,
        "log_eta": np.log(eta),
        "se_fisher": np.sqrt(np.maximum(np.diag(cov), 0)),
        "cov": cov,
        "pearson": pearson,
        "dof": dof,
        "overdispersion": pearson / max(dof, 1),
        "jackknife_se": jack,
        "model_light": light,
        "runs": [r["name"] for r in rows],
        "settings": len(p),
    }


def part2(runs: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    ledger: list[dict[str, Any]] = []
    out: dict[str, Any] = {}
    # consecutive runs with equal plan-time vectors form one session; families kept separate
    sessions: list[list[dict[str, Any]]] = []
    for r in runs:
        if (
            sessions
            and sessions[-1][-1]["plan_key"] == r["plan_key"]
            and sessions[-1][-1]["family"] == r["family"]
            and sessions[-1][-1]["mitigation"] == r["mitigation"]
        ):
            sessions[-1].append(r)
        else:
            sessions.append([r])
    fits = []
    for s in sessions:
        f = session_fit(s)
        f["family"] = s[0]["family"]
        f["plan_key"] = s[0]["plan_key"]
        f["mitigation"] = s[0]["mitigation"]
        f["first_submitted"] = s[0]["submitted"]
        f["t_out"] = s[0]["t_out"]
        fits.append(f)
    out["sessions"] = [
        {
            "family": f["family"],
            "plan_key": f["plan_key"],
            "mitigation": f["mitigation"],
            "first_submitted": f["first_submitted"],
            "runs": f["runs"],
            "settings": f["settings"],
            "overdispersion_pearson_over_dof": c.sig(f["overdispersion"], 4),
            "ln_eta": [c.sig(float(v), 4) for v in f["log_eta"]],
            "se_fisher": [c.sig(float(v), 3) for v in f["se_fisher"]],
            "jackknife_se": [c.sig(float(v), 3) for v in f["jackknife_se"]] if f["jackknife_se"] is not None else None,
        }
        for f in fits
    ]
    # replay check against the retained C1 record
    c1 = c.ROOT / "results/quandela/sessions/2026-10-18T030133Z-qpu_belenos-belenos_mesh/efficiency.json"
    record = json.loads(c1.read_text())
    ref_runs = set(record["runs"])
    sel = [r for r in runs if r["name"] in ref_runs]
    if len(sel) == len(ref_runs):
        eta_mine = mesh.fit_efficiency(np.vstack([r["probs"] for r in sel]), np.vstack([r["singles"] for r in sel]))
        theirs = np.array(record["efficiency_under_ideal"])
        out["replay_of_retained_session_record"] = {
            "runs": sorted(ref_runs),
            "max_abs_difference_eta": c.sig(float(np.max(np.abs(eta_mine - theirs))), 4),
            "max_relative_difference": c.sig(float(np.max(np.abs(eta_mine / theirs - 1))), 4),
            "note": (
                "record = qd_belenos_mesh.efficiency_record under dark-free ideal fit; the record's own singles come "
                "from analysis.json (dark-subtracted sources differ from raw counts only through dark_expected)"
            ),
        }
    # per-family heterogeneity of ln eta across sessions, per mode
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for f in fits:
        by_family[f"{f['family']}|{f['mitigation']}"].append(f)
    hetero = {}
    for fam, group in by_family.items():
        if len(group) < 2:
            continue
        # intervals: Fisher se inflated by sqrt(overdispersion) of the session's fit; per-mode precision-weighted mean
        info_ok = [
            set(
                np.flatnonzero(
                    np.diag(np.linalg.pinv(g["cov"], rcond=1e-9))
                    > 1e-3 * np.diag(np.linalg.pinv(g["cov"], rcond=1e-9)).max()
                )
            )
            for g in group
        ]
        common = sorted(set.intersection(*info_ok))
        if len(common) < 4:
            continue
        # common gauge: centre ln eta over the modes every session identifies; covariance projected the same way
        proj = np.zeros((MODES, MODES))
        for m_ in common:
            proj[m_, common] = -1.0 / len(common)
            proj[m_, m_] += 1.0
        L = np.array([proj @ g["log_eta"] for g in group])
        S = np.array(
            [
                np.sqrt(np.maximum(np.diag(proj @ g["cov"] @ proj.T), 0)) * math.sqrt(max(1.0, g["overdispersion"]))
                for g in group
            ]
        )
        S_binom = np.array([np.sqrt(np.maximum(np.diag(proj @ g["cov"] @ proj.T), 0)) for g in group])
        S = np.maximum(S, 1e-6)
        S_binom = np.maximum(S_binom, 1e-6)
        rows: list[dict[str, Any]] = []
        for m_ in common:
            w = 1 / S[:, m_] ** 2
            wb = 1 / S_binom[:, m_] ** 2
            mean = float((w * L[:, m_]).sum() / w.sum())
            q_infl = float((w * (L[:, m_] - mean) ** 2).sum())
            meanb = float((wb * L[:, m_]).sum() / wb.sum())
            q_binom = float((wb * (L[:, m_] - meanb) ** 2).sum())
            rows.append(
                {
                    "mode": int(m_),
                    "q_binomial_fisher": c.sig(q_binom, 4),
                    "q_overdispersion_inflated": c.sig(q_infl, 4),
                    "dof": len(group) - 1,
                    "log10_p_binomial": c.sig(c.chi2_log10_sf(q_binom, len(group) - 1), 4),
                    "log10_p_inflated": c.sig(c.chi2_log10_sf(q_infl, len(group) - 1), 4),
                    "ln_eta_range": [c.sig(float(L[:, m_].min()), 4), c.sig(float(L[:, m_].max()), 4)],
                }
            )
        hetero[fam] = {"sessions": len(group), "common_identified_modes": [int(m_) for m_ in common], "modes": rows}
        ledger_ps = [r["log10_p_inflated"] for r in rows]
        # family-level test: Bonferroni over modes, reported as the smallest inflated p
        ledger.append(
            c.ledger_row(
                f"A3.model.{fam}",
                3,
                f"smallest per-mode p of the across-session heterogeneity of ln efficiency, {len(group)} plan-time "
                f"sessions of {fam}, Bonferroni over the modes every session identifies",
                min(0.0, min(ledger_ps) + math.log10(len(common))),
                {
                    "sessions": len(group),
                    "modes_below_bonferroni_0.05": int(sum(p <= math.log10(0.05 / len(common)) for p in ledger_ps)),
                    "mean_overdispersion": c.sig(float(np.mean([g["overdispersion"] for g in group])), 4),
                },
                None,
                "intervals inflated by the session's Pearson/dof because the ideal-mesh model is rejected by the "
                "retained held-out fits",
            )
        )
    out["family_heterogeneity"] = hetero
    # mitigation contrast: same plan key, default against none (single runs of the bdsc_qualification family)
    contrast = []
    for a in fits:
        for b in fits:
            if (
                a is b
                or a["mitigation"] != "default"
                or b["mitigation"] != "none"
                or a["plan_key"] != b["plan_key"]
                or a["family"] != b["family"]
            ):
                continue
            d = a["log_eta"] - b["log_eta"]
            se = np.sqrt(a["se_fisher"] ** 2 + b["se_fisher"] ** 2)
            z = d / np.maximum(se, 1e-9)
            contrast.append(
                {
                    "default": a["runs"],
                    "none": b["runs"],
                    "ln_eta_default_minus_none": [c.sig(float(v), 4) for v in d],
                    "se": [c.sig(float(v), 3) for v in se],
                    "chi2_binomial": c.sig(float((z**2).sum()), 4),
                    "dof": MODES - 1,
                    "max_abs_z": c.sig(float(np.max(np.abs(z))), 4),
                }
            )
            q_stat = float((z**2).sum())
            ledger.append(
                c.ledger_row(
                    "A3.mitigation." + a["runs"][0][:19],
                    3,
                    "DetectorBalancing contrast: fitted ln efficiency of the default-mitigation run against the none "
                    "run on one plan-time record (different compiled circuits)",
                    c.chi2_log10_sf(q_stat, MODES - 1),
                    {"chi2": c.sig(q_stat), "dof": MODES - 1},
                    None,
                    "model-based; the two runs carry different returned meshes, so mesh-model misfit also enters",
                )
            )
    out["mitigation_contrast"] = contrast
    return ledger, out


def main() -> None:
    runs = read_runs()
    ledger1, details1, mode_rows = part1(runs)
    ledger2, part2_out = part2(runs)
    # mode-level family for the identical-circuit pairs
    z_rows = [r for r in mode_rows if r["z_raw"] is not None]
    bonf = 0.05 / max(len(z_rows), 1)
    flagged = [r for r in z_rows if c.normal_two_sided_log10(r["z_raw"]) <= math.log10(bonf)]
    modes_hit: dict[int, int] = defaultdict(int)
    for r in flagged:
        modes_hit[r["mode"]] += 1

    # within-epoch spread of the centered per-mode shift (empirical within-session interval) against between-epoch pairs
    def centered(rows_: list[dict[str, Any]]) -> list[float]:
        return [r["ln_odds_ratio_centered"] for r in rows_ if r["se"] < 0.2 and r["mode"] not in STRAY_MODES]

    within = centered([r for r in z_rows if r["same_plan_epoch"]])
    between_rows = [r for r in z_rows if not r["same_plan_epoch"]]
    between = centered(between_rows)
    spread: dict[str, Any] = {
        "within_epoch_rms_ln_odds_ratio": c.sig(float(np.sqrt(np.mean(np.square(within)))), 4) if within else None,
        "between_epoch_rms_ln_odds_ratio": c.sig(float(np.sqrt(np.mean(np.square(between)))), 4) if between else None,
        "within_epoch_pairs": len({r["pair"] for r in z_rows if r["same_plan_epoch"]}),
        "between_epoch_pairs": len({r["pair"] for r in between_rows}),
        "binomial_rms_expected": c.sig(
            float(np.sqrt(np.mean([r["se"] ** 2 for r in z_rows if r["se"] < 0.2 and r["mode"] not in STRAY_MODES]))), 4
        ),
    }
    moved: dict[int, int] = defaultdict(int)
    if within:
        threshold = 3 * float(np.sqrt(np.mean(np.square(within))))
        for r in between_rows:
            if r["se"] < 0.2 and r["mode"] not in STRAY_MODES and abs(r["ln_odds_ratio_centered"]) > threshold:
                moved[r["mode"]] += 1
        spread["modes_beyond_3x_within_epoch_rms_count_by_mode_over_between_epoch_pairs"] = dict(sorted(moved.items()))
        spread["threshold_ln_odds_ratio"] = c.sig(threshold, 4)
    # relation of the centered mode shift to the plan-time t_out ratio, between-epoch pairs
    rel = []
    for pair in sorted({r["pair"] for r in z_rows}):
        rows = [
            r
            for r in z_rows
            if r["pair"] == pair
            and r["ln_plan_t_out_ratio"] is not None
            and r["se"] < 0.2
            and r["mode"] not in STRAY_MODES
        ]
        if len(rows) >= 8 and not rows[0]["same_plan_epoch"]:
            x = [r["ln_plan_t_out_ratio"] for r in rows]
            y = [r["ln_odds_ratio_centered"] for r in rows]
            rho = stats.spearmanr(x, y)
            rel.append(
                {
                    "pair": pair,
                    "modes": len(rows),
                    "spearman": c.sig(float(rho.statistic), 4),
                    "p": c.sig(float(rho.pvalue), 4),
                }
            )
    zs = [stats.norm.isf(r["p"] / 2) * np.sign(r["spearman"]) for r in rel if r["p"] > 0]
    ledger3 = []
    if zs:
        zc = float(np.sum(zs) / math.sqrt(len(zs)))
        ledger3.append(
            c.ledger_row(
                "A3.plan_t_out",
                3,
                "centered fitted per-mode shift against the change of the plan-time t_out, Stouffer over "
                "between-epoch identical-circuit pairs",
                c.normal_two_sided_log10(zc),
                {"pairs": len(zs), "stouffer_z": c.sig(zc)},
                None,
                "consecutive pairs share runs, so the pairs are dependent; the Stouffer z is optimistic",
            )
        )
    all_rows = ledger1 + ledger3
    out = {
        "analysis": 3,
        "falsifier": __doc__,
        "data": {
            "single_photon_completed_qpu_belenos_runs": len(runs),
            "runs": [r["run"] for r in runs],
            "plan_epochs": len({r["plan_key"] for r in runs}),
            "identical_circuit_sets": {
                str(i): [r["name"] for r in members] for i, members in enumerate(s for s in _sets(runs) if len(s) >= 2)
            },
            "not_examined": (
                "multiphoton Belenos runs (2, 3 and 6 photon inputs): their single-click marginals depend on "
                "permanents, outside the single-photon ideal model used here"
            ),
        },
        "part1_identical_circuits": {
            "pairs": details1,
            "modes_flagged_bonferroni": dict(sorted(modes_hit.items())),
            "mode_tests": len(z_rows),
            "bonferroni_alpha": c.sig(bonf),
            "t_out_relation": rel,
            "within_vs_between_epoch_spread": spread,
        },
        "part1_mode_rows": mode_rows,
        "part2_model_based": part2_out,
        "part2_secondary_tests_not_in_ledger": c.summarize_ledger(ledger2)
        | {
            "reason": (
                "model-based comparisons inherit the ideal-mesh misfit (Pearson/dof 19 to 1e5, strategy.md section 2 "
                "held-out rejection) and the mitigation contrast compares different compiled circuits; the "
                "quasi-likelihood intervals are not a well-posed null, so these rows stay out of the corrected ledger"
            )
        },
        "ledger": c.summarize_ledger(all_rows),
    }
    path = c.write_json("a3_belenos_mode_efficiency.json", out)
    print(
        f"wrote {c.rel(path)}: {len(runs)} runs, {len(details1)} identical-circuit pairs, {len(all_rows)} ledger tests"
    )


def _sets(runs: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    d: dict[tuple[str, ...], list[dict[str, Any]]] = defaultdict(list)
    for r in runs:
        d[tuple(r["circuit_hashes"])].append(r)
    return list(d.values())


if __name__ == "__main__":
    main()
