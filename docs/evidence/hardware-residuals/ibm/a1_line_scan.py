"""Shot-order line scan of every retained IBM shot-ordered column (64 acquisitions, 2232 PUB files).

Falsifier, fixed before the run. Each channel is one classical bit column (a register bit), the parity of a
multi-bit register, or the sum of all bits of a PUB with at least 16 columns, taken in the returned shot
order. The null is that shots are independent given the channel marginal. Under it the normalized
periodogram ordinates c_k = |sum_n (x_n - p) exp(-2 pi i k n / N)|^2 / (N p (1 - p)), k = 9 ... (N-1)/2,
are standard exponential (Schuster; the sum-of-bits channel normalizes by its sample variance), and Fisher's
max-ordinate law gives one p-value per channel: P(max c_k >= c) = 1 - (1 - exp(-c))^m. The lowest eight
bins (k = 1 ... 8, cycles per N shots) are the drift band: the sum of their ordinates is Gamma(8, 1) under
the null, one further p-value per channel. A slow drift leaks power into bins above k = 8, so a third
statistic normalizes each ordinate by the mean of its 64 neighbors (32 per side, one guard bin each side):
the ratio R_k = c_k / mean(neighbors) has P(R >= r) = (1 + r / 64)^-64 under a locally flat spectrum, and
the maximum over the bins with a full window gives one narrow-line p-value per channel (union bound over those
bins). "No structure" means every channel's white-line, narrow-line and drift p-value stays above the
family-wise threshold alpha / (number of tests) with alpha = 0.05 over all channels and all three families,
and the bulk of ordinates follows the exponential law. A columns with fewer than 30 minority-valued
shots is not tested (the exponential law needs events to sum); the number skipped is reported.

Conservative check for survivors. Conditional on the minority count K, the periodogram sum is a sum of K draws
without replacement of unit phasors, so Hoeffding's lemma bounds each projection's tail; with eight
directions p_cons(k) <= 8 exp(-0.427 |X_k|^2 / K) per frequency. A survivor must also pass the same
threshold under that bound to count as structure found.

Calibration limit. The exponential, Fisher, Gamma and neighbor-ratio laws hold for independent shots with a
locally flat spectrum. Slow drift and short-lag dependence of the same records (analyses 4 and 5) color the
spectrum, so the tails of the maximum and of the local ratio are asymptotic under independence; the bulk
fractions above validate the marginal exponential law only. The calibrated tails of the windows near 60 Hz
and 29.70 Hz (bin enumeration over the same spectrum) sit in a1b_job_stack.py.

Caveats carried into the result: IBM documents shot order as unguaranteed and the raw records carry chunk
start and stop times only, so a null bounds structure that survives the service's ordering; a frequency
in Hz converts a list-position frequency with the documented column-wise period (see common.py).

Deterministic controls (no random draw): a reordering of the 149-qubit prep0 PUB by the argsort of the
splitmix64 hash of the shot index must read uniform p-values (a multiplicative index scramble is no
control, because a dilation of the index only permutes the periodogram bins); a pulse comb added to a
scrambled column must be recovered at a multiple of its fundamental bin.
"""

from __future__ import annotations

import math
from typing import Any

import common
import numpy as np

KMIN = 30
LOW = 8
HALF = 32
GUARD = 1
THRESH = (3.0, math.log(100), math.log(1000))
ALPHA = 0.05


def scan_matrix(chan: np.ndarray, binary: bool) -> dict[str, np.ndarray]:
    """Line and drift statistics of every column of chan (N, C), float64."""
    n = chan.shape[0]
    p = chan.mean(axis=0)
    spectrum = np.fft.rfft(chan - p, axis=0)
    m = (n - 1) // 2
    power = spectrum[1 : m + 1].real ** 2 + spectrum[1 : m + 1].imag ** 2
    var = n * p * (1 - p) if binary else n * chan.var(axis=0)
    ok = var > 0
    c = np.where(ok, power / np.where(ok, var, 1.0), 0.0)
    low = c[:LOW].sum(axis=0)
    line = c[LOW:]
    k_rel = line.argmax(axis=0)
    cmax = line.max(axis=0)
    # narrow-line statistic: ordinate over the mean of its 2 * HALF neighbors outside a one-bin guard
    h = HALF + GUARD
    csum = np.vstack([np.zeros((1, c.shape[1])), np.cumsum(c, axis=0)])
    idx = np.arange(h, m - h)
    left = csum[idx - GUARD] - csum[idx - h]
    right = csum[idx + h + 1] - csum[idx + GUARD + 1]
    local = c[idx] / np.maximum((left + right) / (2 * HALF), 1e-300)
    loc_arg = local.argmax(axis=0)
    loc_max = local.max(axis=0)
    kmin = np.minimum(chan.sum(axis=0), n - chan.sum(axis=0)) if binary else np.full(chan.shape[1], np.nan)
    cons = power[LOW:].max(axis=0) / np.maximum(kmin, 1) if binary else np.full(chan.shape[1], np.nan)
    qq = np.array([(line >= t).sum(axis=0) for t in THRESH])  # (3, C)
    return {
        "p": p,
        "kmin": kmin,
        "cmax": cmax,
        "kmax": k_rel + LOW + 1,
        "loc_max": loc_max,
        "loc_k": idx[loc_arg] + 1,
        "m_loc": np.full(chan.shape[1], idx.size),
        "low": low,
        "cons": cons,
        "m_line": np.full(chan.shape[1], m - LOW),
        "qq": qq,
        "n_ord": np.full(chan.shape[1], m - LOW),
    }


def channel_list(regs: dict[str, np.ndarray]) -> list[tuple[str, str, np.ndarray, bool]]:
    """(register, label, series, binary) for each bit, each multi-bit parity, and the sum of all bits."""
    out: list[tuple[str, str, np.ndarray, bool]] = []
    total = 0
    for name, matrix in sorted(regs.items()):
        total += matrix.shape[1]
        for b in range(matrix.shape[1]):
            out.append((name, f"bit{b}", matrix[:, b].astype(np.float64), True))
        if matrix.shape[1] >= 2:
            out.append((name, "parity", (matrix.sum(axis=1) % 2).astype(np.float64), True))
    if total >= 16:
        out.append(("*", "sum", np.hstack([m for _, m in sorted(regs.items())]).sum(axis=1).astype(np.float64), False))
    return out


def scan_pub(task: dict[str, Any]) -> dict[str, Any]:
    pub = common.load_pub(task["file"])
    channels = channel_list(pub["regs"])
    n = next(iter(pub["regs"].values())).shape[0]
    tested: list[list[Any]] = []
    skipped = 0
    qq = np.zeros(3, dtype=np.int64)
    n_ord = 0
    for binary in (True, False):
        group = [ch for ch in channels if ch[3] == binary]
        if not group:
            continue
        data = np.stack([ch[2] for ch in group], axis=1)
        stats = scan_matrix(data, binary)
        for j, (reg, label, series, _) in enumerate(group):
            k_events = int(stats["kmin"][j]) if binary else -1
            if binary and k_events < KMIN:
                skipped += 1
                continue
            if not binary and not (series.std() > 0):
                skipped += 1
                continue
            m_line = int(stats["m_line"][j])
            lp_line = float(common.log10_fisher_p(stats["cmax"][j], m_line))
            lp_low = common.log10_gamma_sf(float(stats["low"][j]), LOW)
            m_loc = int(stats["m_loc"][j])
            lp_loc = float(
                min(0.0, math.log10(m_loc) - 2 * HALF * math.log10(1 + float(stats["loc_max"][j]) / (2 * HALF)))
            )
            if binary:
                cons_c = float(stats["cons"][j])
                lp_cons = float(min(0.0, math.log10(m_line * 8) - 0.427 * cons_c / math.log(10)))
            else:
                lp_cons = None
            qq += stats["qq"][:, j]
            n_ord += m_line
            tested.append(
                [
                    reg,
                    label,
                    k_events,
                    float(stats["p"][j]),
                    float(stats["cmax"][j]),
                    int(stats["kmax"][j]),
                    lp_line,
                    lp_low,
                    lp_cons,
                    m_line,
                    lp_loc,
                    float(stats["loc_max"][j]),
                    int(stats["loc_k"][j]),
                    float(stats["low"][j]),
                ]
            )
    return {
        "file": task["file"],
        "name": pub["name"],
        "n": n,
        "n_channels": len(channels),
        "n_tested": len(tested),
        "n_skipped": skipped,
        "qq": qq.tolist(),
        "n_ord": n_ord,
        "channels": tested,
    }


def hash_order(n: int) -> np.ndarray:
    """Fixed pseudo-random reordering: argsort of the splitmix64 hash of the index (no draw, no seed)."""
    with np.errstate(over="ignore"):
        z = np.arange(n, dtype=np.uint64) + np.uint64(0x9E3779B97F4A7C15)
        z = (z ^ (z >> np.uint64(30))) * np.uint64(0xBF58476D1CE4E5B9)
        z = (z ^ (z >> np.uint64(27))) * np.uint64(0x94D049BB133111EB)
        z = z ^ (z >> np.uint64(31))
    return np.argsort(z, kind="stable")


def self_controls(cat: dict[str, Any]) -> dict[str, Any]:
    """Scramble calibration and pulse-comb recovery on the 149-qubit prep0 PUB."""
    target = next(p for j in cat["jobs"] if j["run"].endswith("2026-10-18T083402.386701Z") for p in j["pubs"])
    pub = common.load_pub(target["file"])
    matrix = np.hstack([m for _, m in sorted(pub["regs"].items())]).astype(np.float64)
    n = matrix.shape[0]
    perm = hash_order(n)
    out: dict[str, Any] = {"file": target["file"], "n": n, "columns": matrix.shape[1]}
    for label, data in (("raw", matrix), ("scrambled", matrix[perm])):
        stats = scan_matrix(data, True)
        good = stats["kmin"] >= KMIN
        lp = common.log10_fisher_p(stats["cmax"][good], int(stats["m_line"][0]))
        lpl = np.array([common.log10_gamma_sf(float(v), LOW) for v in stats["low"][good]])
        out[label] = {
            "tested": int(good.sum()),
            "frac_line_p_below_0.05": float(np.mean(lp < math.log10(0.05))),
            "frac_drift_p_below_0.05": float(np.mean(lpl < math.log10(0.05))),
            "min_log10_line_p": float(np.min(lp)),
            "min_log10_drift_p": float(lpl.min()),
        }
    scr = matrix[perm]
    for period in (64, 256):
        col = scr[:, 0].copy()
        comb = (np.arange(n) % period) == 0
        injected = np.maximum(col, comb.astype(np.float64))
        stats = scan_matrix(injected[:, None], True)
        out[f"comb_period_{period}"] = {
            "fundamental_bin": n // period,
            "recovered_bin": int(stats["kmax"][0]),
            "recovered_is_harmonic": bool(int(stats["kmax"][0]) % (n // period) == 0),
            "log10_line_p": float(common.log10_fisher_p(stats["cmax"][0], int(stats["m_line"][0]))),
            "added_probability": float(1.0 / period),
        }
        base = scan_matrix(col[:, None], True)
        out[f"comb_period_{period}"]["unmodified_log10_line_p"] = float(
            common.log10_fisher_p(base["cmax"][0], int(base["m_line"][0]))
        )
    return out


def main() -> None:
    cat = common.catalog()
    jobs = {p["file"]: j for j in cat["jobs"] for p in j["pubs"]}
    tasks = [{"file": p["file"]} for j in cat["jobs"] for p in j["pubs"]]
    results = common.ordered_map(scan_pub, tasks, min_items=1)

    channels = []
    for r in results:
        job = jobs[r["file"]]
        pub = next(p for p in job["pubs"] if p["file"] == r["file"])
        pub_period = job["rep_delay_s"] + pub["dur_dt"] * common.DT
        for ch in r["channels"]:
            channels.append(
                {
                    "file": r["file"],
                    "run": job["run"],
                    "backend": job["backend"],
                    "pub": r["name"],
                    "n": r["n"],
                    "reg": ch[0],
                    "chan": ch[1],
                    "minority": ch[2],
                    "p_hat": ch[3],
                    "cmax": ch[4],
                    "kmax": ch[5],
                    "lp_white": ch[6],
                    "lp_low": ch[7],
                    "lp_cons": ch[8],
                    "m_line": ch[9],
                    "lp_local": ch[10],
                    "ratio_local": ch[11],
                    "k_local": ch[12],
                    "s_low": ch[13],
                    "slot_s": job["slot_s"],
                    "pub_period_s": pub_period,
                }
            )
    n_chan = len(channels)
    families = (("white_line", "lp_white"), ("narrow_line", "lp_local"), ("drift", "lp_low"))
    n_tests = len(families) * n_chan
    tests = [(f"{c['file']}|{c['reg']}|{c['chan']}|{fam}", fam, c[key]) for fam, key in families for c in channels]
    corr = common.global_corrections(tests, ALPHA)
    thr = corr["bonferroni_log10_threshold"]
    bh_ids = set(corr.pop("_bh_member_ids", []))

    def hit_row(c: dict[str, Any], family: str) -> dict[str, Any]:
        row = {
            k: c[k]
            for k in (
                "run",
                "backend",
                "pub",
                "reg",
                "chan",
                "n",
                "minority",
                "p_hat",
                "lp_white",
                "lp_local",
                "lp_low",
                "lp_cons",
            )
        }
        k = c["k_local"] if family == "narrow_line" else c["kmax"]
        stat = c["ratio_local"] if family == "narrow_line" else c["cmax"]
        f_cyc = k / c["n"]
        row.update(
            {
                "family": family,
                "bin_k": k,
                "statistic": stat,
                "f_cycles_per_shot": f_cyc,
                "f_hz_column_wise_slot": f_cyc / c["slot_s"],
                "f_hz_single_circuit_period": f_cyc / c["pub_period_s"],
                "slot_s": c["slot_s"],
            }
        )
        if c["chan"] != "sum" and family != "drift":
            p = c["p_hat"]
            row["amplitude_effect_size_prob"] = 2 * math.sqrt(max(stat - 1, 0) * p * (1 - p) / c["n"])
        if c["chan"] != "sum":
            p = c["p_hat"]
            row["drift_band_rms_modulation_prob"] = math.sqrt(max(c["s_low"] - LOW, 0) * 2 * p * (1 - p) / c["n"])
        return row

    summary: dict[str, Any] = {}
    for fam, key in families:
        ranked = sorted(channels, key=lambda c: c[key])
        hits = [c for c in ranked if c[key] <= thr]
        summary[fam] = {
            "n_bonferroni_hits": len(hits),
            "n_bh_hits": sum(1 for c in ranked if f"{c['file']}|{c['reg']}|{c['chan']}|{fam}" in bh_ids),
            "hits_bonferroni_first_500": [hit_row(c, fam) for c in hits[:500]],
            "top10": [hit_row(c, fam) for c in ranked[:10]],
            "fraction_p_below_0.05": float(np.mean([c[key] < math.log10(0.05) for c in channels])),
            "fraction_p_below_0.001": float(np.mean([c[key] < -3 for c in channels])),
        }
    # conservative bound on the white-line survivors
    cons_pass = [c for c in channels if c["lp_white"] <= thr and c["lp_cons"] is not None and c["lp_cons"] <= thr]
    summary["white_line"]["n_pass_hoeffding_conservative_bound"] = len(cons_pass)

    qq_total = np.sum([r["qq"] for r in results], axis=0)
    n_ord = int(sum(r["n_ord"] for r in results))
    by_run: dict[str, Any] = {}
    for c in channels:
        e = by_run.setdefault(
            c["run"],
            {
                "backend": c["backend"],
                "channels": 0,
                "min_lp_white": 0.0,
                "min_lp_local": 0.0,
                "min_lp_low": 0.0,
                "n_white_below_0.01": 0,
                "n_local_below_0.01": 0,
            },
        )
        e["channels"] += 1
        e["min_lp_white"] = min(e["min_lp_white"], c["lp_white"])
        e["min_lp_local"] = min(e["min_lp_local"], c["lp_local"])
        e["min_lp_low"] = min(e["min_lp_low"], c["lp_low"])
        e["n_white_below_0.01"] += c["lp_white"] < -2
        e["n_local_below_0.01"] += c["lp_local"] < -2

    amin = []
    for c in channels:
        if c["chan"] == "sum":
            continue
        p = c["p_hat"]
        c_star = math.log(c["m_line"]) - math.log(ALPHA / n_tests)
        amin.append(2 * math.sqrt(max(c_star - 1, 0) * p * (1 - p) / c["n"]))
    amin_arr = np.array(amin)

    controls = self_controls(cat)
    out = {
        "analysis": "a1_line_scan",
        "inputs": {
            "n_acquisitions_with_tested_channels": len({c["run"] for c in channels}),
            "n_acquisitions_with_shot_records": cat["n_runs"],
            "n_pub_files": len(results),
            "n_jobs": cat["n_jobs"],
            "n_channels_tested": n_chan,
            "n_channels_skipped_below_30_minority_shots": int(sum(r["n_skipped"] for r in results)),
            "n_tests": n_tests,
            "families": [f for f, _ in families],
            "alpha": ALPHA,
        },
        "corrections": corr,
        "families": summary,
        "bulk_calibration": {
            "thresholds_c": list(THRESH),
            "expected_fraction_exp1": [math.exp(-t) for t in THRESH],
            "observed_fraction": (qq_total / n_ord).tolist(),
            "n_ordinates": n_ord,
        },
        "detectable_amplitude_at_bonferroni_threshold": {
            "meaning": (
                "probability-modulation amplitude a with E c = 1 + N a^2 / (4 p q) = Bonferroni c* (white statistic)"
            ),
            "median": float(np.median(amin_arr)),
            "p10": float(np.percentile(amin_arr, 10)),
            "p90": float(np.percentile(amin_arr, 90)),
        },
        "by_run": by_run,
        "controls": controls,
        "caveat": (
            "shot order is unguaranteed by IBM and records carry chunk start/stop only; a null bounds structure that "
            "survives the service ordering"
        ),
    }
    common.write_json(common.OUT / "a1_line_scan.json", out)
    common.write_json_gz(common.OUT / "a1_pvalues.json.gz", {"tests": [[t[0], t[1], round(t[2], 4)] for t in tests]})
    print(out["inputs"], out["corrections"])
    for fam in summary:
        print(fam, {k: v for k, v in summary[fam].items() if k.startswith(("n_", "fraction"))})
    print(out["bulk_calibration"])
    print(controls)


if __name__ == "__main__":
    main()
