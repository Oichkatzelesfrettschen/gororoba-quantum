"""Analysis 1: the Tuna-17 shot-order 50 Hz line scan extended past the 2026-10-18 corpus cutoff.

Falsifier, fixed before computing. "No structure" is any of: (a) no later Tuna-17 job crosses the corpus
threshold (band-corrected p < 1e-6 in the whitened zoom-FFT of scripts/qi_shot_record_line.py over the band
0.019 to 0.021 cycles per shot), (b) the later detected fraction is statistically indistinguishable from the
earlier 72 of 159 jobs, (c) the later detected jobs' first-harmonic amplitudes and peak frequencies are
indistinguishable from the earlier detected jobs. A miscalibrated scanner would also detect lines in the QX
twins (independent draws) or in the readout circuits (which carried no line in the earlier corpus); either
detection invalidates every Tuna reading below.

Method. The statistic, band, threshold and lock-in are the repository's own (qi_shot_record_line.scan, reached
through job_row). Added: a declared wider secondary band 0.010 to 0.040 cycles per shot, because the shot
period grows with circuit length and a longer circuit moves a 50 Hz line out of the primary band. Nulls are the
analytic Gamma(rank, 1) law of the whitened periodogram (already in the statistic), binomial tail for counts,
Fisher exact for two fractions, Mann-Whitney (asymptotic, deterministic) for amplitude and frequency.
No random draw anywhere.
"""

from __future__ import annotations

import json
import math
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import common as c
import numpy as np
import qi_shot_record_line as line
from scipy import stats
from worker1 import SECONDARY_BAND, scan_file, scan_secondary

import parallel
import qi_records

CUTOFF_ISO = "2026-10-18T16:59:57+00:00"


def leaf_dirs() -> list[Path]:
    return sorted(p.parent for p in line.RUNS.rglob("raw") if p.is_dir())


def classify(directory: Path) -> tuple[str, str, bool]:
    """(run path relative to RUNS, backend name, later-than-cutoff)."""
    relative = directory.relative_to(line.RUNS)
    top = relative.parts[0]
    sub = json.loads((directory / "submission.json").read_text()) if (directory / "submission.json").exists() else {}
    backend = line.BACKENDS.get(sub.get("backend_type_id"), f"unknown-{sub.get('backend_type_id')}")
    if re.match(r"^2026-\d\d-\d\dT\d{6}Z", top) and len(relative.parts) == 1:
        later = top[: len(line.CORPUS_THROUGH)] > line.CORPUS_THROUGH
    else:
        created = sub.get("created_utc") or sub.get("submitted_utc") or ""
        later = created > CUTOFF_ISO
    return str(relative), backend, later


def family_of(run: str) -> str:
    name = run.split("/")[-1]
    name = re.sub(r"^\d{4}-\d\d-\d\dT\d{6}Z-", "", name)
    name = re.sub(r"^\d{8}T\d{6}Z-", "", name)
    name = re.sub(r"-(batch|recal|rerun|order-batch)-?\d*.*$", "", name)
    return run.split("/")[0] if run.startswith("tuna17-") else name


def max_first(primary: dict[str, Any]) -> float | None:
    values = [v["first"] for v in primary.get("bits", {}).values() if v["first_significant"]]
    return max(values) if values else None


def main() -> None:
    dirs = leaf_dirs()
    items: list[tuple[str, str, int]] = []
    validation: list[dict[str, Any]] = []
    later_dirs: list[tuple[str, str]] = []
    for directory in dirs:
        run, backend, later = classify(directory)
        if not later or backend not in ("Tuna-17", "QX"):
            continue
        later_dirs.append((run, backend))
        backend_id = 7 if backend == "Tuna-17" else 1
        status = "not validated"
        if (
            (directory / "cases.json").exists()
            and (directory / "submission.json").exists()
            and (directory / "results.json").exists()
        ):
            try:
                qi_records.read_run(directory)
                status = "read_run ok"
            except Exception as error:  # reported, never dropped
                status = f"read_run failed: {str(error)[:160]}"
        else:
            status = "no cases/submission/results at this level (nested prepared-run directory or incomplete record)"
        validation.append({"run": run, "backend": backend, "validation": status})
        for raw in sorted((directory / "raw").glob("*.json")):
            items.append((run, raw.name[: -len(".json")], backend_id))
    rows = parallel.ordered_map(scan_file, items, min_items=2)

    earlier_items = line.inventory()
    earlier_rows = parallel.ordered_map(scan_secondary, earlier_items, min_items=2)
    early = json.loads((c.ROOT / "results/quantum_inspire/tuna_17_shot_record_line.json").read_text())
    early_tuna = [r for r in early["jobs"] if r["backend"] == "Tuna-17"]
    early_det = [r for r in early_tuna if r["detected"]]
    early_nonro = [r for r in early_tuna if not r["file"].startswith("readout")]
    early_amp = [m for r in early_det if (m := max_first(r)) is not None]
    early_freq = [r["cycles_per_shot"] for r in early_det]

    tuna = [r for r in rows if r["backend"] == "Tuna-17"]
    qx = [r for r in rows if r["backend"] == "QX"]
    tuna_det = [r for r in tuna if r["primary"]["detected"]]
    tuna_nonro = [r for r in tuna if not r["file"].startswith("readout")]
    tuna_nonro_det = [r for r in tuna_nonro if r["primary"]["detected"]]
    tuna_ro = [r for r in tuna if r["file"].startswith("readout")]
    qx_det = [r for r in qx if r["primary"]["detected"]]
    qx_sec_det = [r for r in qx if r["secondary"]["detected"]]
    ro_sec_det = [r for r in tuna_ro if r["secondary"]["detected"]]
    tuna_sec_only = [r for r in tuna if r["secondary"]["detected"] and not r["primary"]["detected"]]

    later_amp = [m for r in tuna_det if (m := max_first(r["primary"])) is not None]
    later_freq = [r["primary"]["cycles_per_shot"] for r in tuna_det]

    n, k = len(tuna), len(tuna_det)
    ledger = []
    # null: each job detects with probability at most DETECTION_P when no line exists
    log10_binom = float(stats.binom.logsf(k - 1, n, line.DETECTION_P)) / math.log(10) if k else 0.0
    ledger.append(
        c.ledger_row(
            "A1.1",
            1,
            "later Tuna-17 jobs with a band-corrected line p < 1e-6, against detection probability 1e-6 per job",
            log10_binom,
            {"detected": k, "jobs": n, "fraction": c.sig(k / n)},
            c.wilson(k, n),
        )
    )
    odds = stats.fisher_exact([[k, n - k], [72, 159 - 72]])
    ledger.append(
        c.ledger_row(
            "A1.2",
            1,
            "fraction of later Tuna-17 jobs with the line against the earlier 72 of 159 (Fisher exact, all jobs)",
            math.log10(max(odds.pvalue, 1e-300)),
            {"later": c.sig(k / n), "earlier": c.sig(72 / 159), "odds_ratio": c.sig(float(odds.statistic))},
            None,
            "circuit mix differs between corpora; readout circuits (no line) are 51 earlier and "
            f"{len(tuna_ro)} later jobs",
        )
    )
    kn, nn = len(tuna_nonro_det), len(tuna_nonro)
    odds2 = stats.fisher_exact([[kn, nn - kn], [len(early_det), len(early_nonro) - len(early_det)]])
    ledger.append(
        c.ledger_row(
            "A1.3",
            1,
            "fraction of later non-readout Tuna-17 jobs with the line against the earlier non-readout jobs (Fisher "
            "exact)",
            math.log10(max(odds2.pvalue, 1e-300)),
            {"later": c.sig(kn / max(nn, 1)), "earlier": c.sig(len(early_det) / len(early_nonro))},
            None,
        )
    )
    if len(later_amp) >= 3 and len(early_amp) >= 3:
        mw = stats.mannwhitneyu(later_amp, early_amp, alternative="two-sided")
        ledger.append(
            c.ledger_row(
                "A1.4",
                1,
                "per-job maximum first-harmonic amplitude of detected jobs, later against earlier (Mann-Whitney)",
                math.log10(max(float(mw.pvalue), 1e-300)),
                {
                    "later_median": c.sig(float(np.median(later_amp))),
                    "earlier_median": c.sig(float(np.median(early_amp))),
                },
                None,
                "class-level comparison: later and earlier jobs run different circuits",
            )
        )
    if len(later_freq) >= 3:
        mw = stats.mannwhitneyu(later_freq, early_freq, alternative="two-sided")
        ledger.append(
            c.ledger_row(
                "A1.5",
                1,
                "peak frequency in cycles per shot of detected jobs, later against earlier (Mann-Whitney)",
                math.log10(max(float(mw.pvalue), 1e-300)),
                {
                    "later_median": c.sig(float(np.median(later_freq)), 7),
                    "earlier_median": c.sig(float(np.median(early_freq)), 7),
                },
                None,
                "a different shot period at fixed wall-clock frequency moves the cycles-per-shot value",
            )
        )
    pay_sec = [r for r in tuna_sec_only if not r["file"].startswith("readout")]
    ro1 = [r for r in tuna_ro if r["file"].startswith("readout-1")]
    ro1_sec = [r for r in ro1 if r["secondary"]["detected"]]
    ro0 = [r for r in tuna_ro if r["file"].startswith("readout-0")]
    ro0_sec = [r for r in ro0 if r["secondary"]["detected"]]
    sec_k = len(pay_sec)

    def tail(k: int, m: int) -> float:
        return float(stats.binom.logsf(k - 1, m, line.DETECTION_P)) / math.log(10) if k else 0.0

    ledger.append(
        c.ledger_row(
            "A1.6",
            1,
            "later non-readout Tuna-17 jobs detected only in the wider secondary band 0.010-0.040 (band-corrected p "
            "< 1e-6)",
            tail(sec_k, n),
            {"jobs": sec_k, "of": len(tuna_nonro)},
            c.wilson(sec_k, len(tuna_nonro)),
            "exploratory band declared after the primary scan; the later QX twins give 0 detections in the same band",
        )
    )
    ledger.append(
        c.ledger_row(
            "A1.7",
            1,
            "later readout-1 circuits (X-prepared qubits) with a secondary-band line, outside the primary band",
            tail(len(ro1_sec), len(ro1)),
            {
                "detected": len(ro1_sec),
                "readout_1_jobs": len(ro1),
                "readout_0_detected": len(ro0_sec),
                "readout_0_jobs": len(ro0),
            },
            c.wilson(len(ro1_sec), len(ro1)),
            "the earlier corpus scanned readouts in the primary band only",
        )
    )
    e_tuna = [r for r in earlier_rows if r["backend"] == "Tuna-17"]
    e_ro1 = [r for r in e_tuna if r["file"].startswith("readout") and "-1" in r["file"]]
    e_ro1_det = [r for r in e_ro1 if r["detected"]]
    e_qx_det = [r for r in earlier_rows if r["backend"] == "QX" and r["detected"]]
    ledger.append(
        c.ledger_row(
            "A1.8",
            1,
            "earlier-corpus Tuna-17 readout-1 circuits with a secondary-band line (rescan of the 2026-10-18 corpus)",
            tail(len(e_ro1_det), len(e_ro1)),
            {"detected": len(e_ro1_det), "jobs": len(e_ro1)},
            c.wilson(len(e_ro1_det), len(e_ro1)),
        )
    )
    fam_groups: defaultdict[str, list[int]] = defaultdict(lambda: [0, 0])
    for r in tuna_nonro:
        f = family_of(r["run"])
        if f.startswith("prepared") or f.startswith("projector"):
            continue
        fam_groups[f][0] += int(r["primary"]["detected"])
        fam_groups[f][1] += 1
    table = [[a, b - a] for a, b in fam_groups.values()]
    chi2_het = stats.chi2_contingency(table)
    ledger.append(
        c.ledger_row(
            "A1.9",
            1,
            "heterogeneity of the primary-band detected fraction across later payload families (chi-square "
            "contingency)",
            float(stats.chi2.logsf(chi2_het.statistic, chi2_het.dof)) / math.log(10),
            {f: f"{a}/{b}" for f, (a, b) in fam_groups.items()},
            None,
            "families differ in circuit and phase sensitivity",
        )
    )

    # per-job family table
    by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in tuna:
        by_family[family_of(r["run"])].append(r)
    family_table = {}
    for name, group in sorted(by_family.items()):
        det = [r for r in group if r["primary"]["detected"]]
        amps = [m for r in det if (m := max_first(r["primary"])) is not None]
        freqs = [r["primary"]["cycles_per_shot"] for r in det]
        eps = [r["exec_seconds_per_shot"] for r in group if r["exec_seconds_per_shot"]]
        family_table[name] = {
            "jobs": len(group),
            "detected_primary": len(det),
            "detected_secondary_only": sum(
                1 for r in group if r["secondary"]["detected"] and not r["primary"]["detected"]
            ),
            "median_max_first_amplitude": c.sig(float(np.median(amps))) if amps else None,
            "cycles_per_shot_range": [c.sig(min(freqs), 7), c.sig(max(freqs), 7)] if freqs else None,
            "implied_shot_period_us_at_50Hz": [c.sig(min(freqs) / 50 * 1e6, 5), c.sig(max(freqs) / 50 * 1e6, 5)]
            if freqs
            else None,
            "exec_us_per_shot_range": [c.sig(min(eps) * 1e6, 4), c.sig(max(eps) * 1e6, 4)] if eps else None,
            "shots_range": [min(r["shots"] for r in group), max(r["shots"] for r in group)],
        }

    # per-job BH inside the analysis: primary band
    primary_logp = [r["primary"].get("log10_p", 0.0) if r["primary"].get("detected") is not None else 0.0 for r in tuna]
    primary_logp = [r["primary"].get("log10_p", 0.0) for r in tuna]
    bh = c.benjamini_hochberg(primary_logp)
    bf = c.bonferroni(primary_logp)

    # amplitude against date among later detected jobs (class-confounded)
    dates = []
    for r in tuna_det:
        stamp = r["run"].split("/")[0][:10]
        m = max_first(r["primary"])
        if m is not None and re.match(r"\d{4}-\d\d-\d\d", stamp):
            dates.append((stamp, m))
    date_rho = None
    if len(dates) >= 5:
        days = [(np.datetime64(d) - np.datetime64("2026-10-18")).astype(int) for d, _ in dates]
        rho = stats.spearmanr(days, [m for _, m in dates])
        date_rho = {
            "n": len(dates),
            "rho": c.sig(float(rho.statistic)),
            "p": c.sig(float(rho.pvalue)),
            "note": "class-confounded: families are dated in blocks",
        }

    out: dict[str, Any] = {
        "analysis": 1,
        "falsifier": __doc__,
        "threshold": {"band": list(line.BAND), "detection_p": line.DETECTION_P, "secondary_band": list(SECONDARY_BAND)},
        "data": {
            "later_directories": len(later_dirs),
            "later_tuna_directories": sum(1 for _, b in later_dirs if b == "Tuna-17"),
            "later_qx_directories": sum(1 for _, b in later_dirs if b == "QX"),
            "tuna_raw_files": len(tuna),
            "qx_raw_files": len(qx),
            "directory_list": validation,
            "earlier_corpus_record": "results/quantum_inspire/tuna_17_shot_record_line.json",
        },
        "counts": {
            "tuna_jobs": n,
            "tuna_detected_primary": k,
            "tuna_fraction_wilson95": c.wilson(k, n),
            "tuna_nonreadout_jobs": nn,
            "tuna_nonreadout_detected": kn,
            "tuna_readout_jobs": len(tuna_ro),
            "tuna_readout_detected_primary": sum(1 for r in tuna_ro if r["primary"]["detected"]),
            "tuna_readout_detected_secondary": len(ro_sec_det),
            "qx_jobs": len(qx),
            "qx_detected_primary": len(qx_det),
            "qx_detected_secondary": len(qx_sec_det),
            "tuna_detected_secondary_only": len(tuna_sec_only),
            "payload_secondary_only": sec_k,
            "readout_1_secondary_only": len(ro1_sec),
            "readout_0_secondary_only": len(ro0_sec),
            "earlier_rescan_secondary": {
                "tuna_jobs": len(e_tuna),
                "tuna_detected": sum(r["detected"] for r in e_tuna),
                "tuna_readout_1_detected": len(e_ro1_det),
                "qx_jobs": len(earlier_rows) - len(e_tuna),
                "qx_detected": len(e_qx_det),
            },
            "earlier_tuna_detected": len(early_det),
            "earlier_tuna_jobs": len(early_tuna),
            "per_job_bh_survivors_primary": int(sum(bh)),
            "per_job_bonferroni_survivors_primary": int(sum(bf)),
        },
        "amplitude": {
            "later_detected_max_first": {
                "n": len(later_amp),
                "median": c.sig(float(np.median(later_amp))) if later_amp else None,
                "range": [c.sig(min(later_amp)), c.sig(max(later_amp))] if later_amp else None,
            },
            "earlier_detected_max_first": {
                "n": len(early_amp),
                "median": c.sig(float(np.median(early_amp))),
                "range": [c.sig(min(early_amp)), c.sig(max(early_amp))],
            },
            "later_vs_date_spearman": date_rho,
        },
        "frequency": {
            "later_cycles_per_shot_range": [c.sig(min(later_freq), 7), c.sig(max(later_freq), 7)]
            if later_freq
            else None,
            "earlier_cycles_per_shot_range": [c.sig(min(early_freq), 7), c.sig(max(early_freq), 7)],
            "earlier_shot_period_us_at_50Hz": (
                "402.9 to 404.6 in the ring-down circuits and 400.7 in the follow series "
                "(docs/notes/quantum_inspire/tuna-17.md)"
            ),
        },
        "families": family_table,
        "ledger": c.summarize_ledger(ledger),
        "secondary_only_jobs": [
            {k: r[k] for k in ("run", "file", "shots")}
            | {"cycles_per_shot": r["secondary"]["cycles_per_shot"], "log10_p": r["secondary"]["log10_p"]}
            for r in tuna_sec_only
        ],
        "earlier_secondary_detections": [r for r in earlier_rows if r["detected"]],
        "jobs": rows,
    }
    path = c.write_json("a1_shot_line_extension.json", out)
    print(
        f"wrote {c.rel(path)}: {k}/{n} later Tuna jobs with the line; QX control {len(qx_det)}/{len(qx)}; readout "
        f"{out['counts']['tuna_readout_detected_primary']}/{len(tuna_ro)}"
    )


if __name__ == "__main__":
    main()
