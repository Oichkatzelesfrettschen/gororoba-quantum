"""Global Bonferroni and Benjamini-Hochberg over every test of the six analyses (and the stacked-line follow-up).

Reads the a*_pvalues.json.gz side files (id, family, log10 p). The follow-up job stack (a1b) re-uses the
data of the column scan (a1), so counting both is conservative. The 60 Hz and 29.7 Hz category table reads
a1b_job_stack.json.

Law of each family. a1 white-line, narrow-line and drift: asymptotic laws of independent stationary shots.
a1b stacks: Gamma and F laws of independent columns, anti-conservative under positive column correlation, so
the tally is also given without them. a2 dispersion: the circular-shift distribution over the full group of
shifts; a2 tails, adjacency and window: Poisson approximations. a3 bins, trend and contrast:
t tests over PUBs (the units of one calibration epoch share a device state; the epoch-level tests sit in
a3_coupler_distance.json and enter no count); a3 pairs: exact hypergeometric laws. a4 diagonal: exact adjacency
law; a4 cross: Poisson approximation; the exact variance is below the mean, which does not prove a tail bound.
a5 columns: exact run-count law; a5 groups: exact for independently arranged columns where the cost allows,
otherwise a Chernoff upper bound of the exact law; a5 continuation: normal approximation.
"""

from __future__ import annotations

import gzip
import json
import math
import re
from typing import Any

import common

FILES = ["a1", "a1b", "a2", "a3", "a4", "a5", "a6"]
ALPHA = 0.05


def main() -> None:
    tests: list[tuple[str, str, float]] = []
    per: dict[str, int] = {}
    for tag in FILES:
        with gzip.open(common.OUT / f"{tag}_pvalues.json.gz", "rt") as handle:
            rows = json.load(handle)["tests"]
        per[tag] = len(rows)
        tests += [(f"{tag}:{r[0]}", f"{tag}:{r[1]}", float(r[2])) for r in rows]
    n = len(tests)
    order = sorted(range(n), key=lambda i: tests[i][2])
    log_alpha = math.log10(ALPHA)
    bonf = log_alpha - math.log10(n)
    bh_cut = 0
    for rank, i in enumerate(order, start=1):
        if tests[i][2] <= log_alpha + math.log10(rank) - math.log10(n):
            bh_cut = rank
    bh_set = {order[k] for k in range(bh_cut)}
    summary: dict[str, dict[str, Any]] = {}
    for i, (_tid, fam, lp) in enumerate(tests):
        e = summary.setdefault(fam, {"tests": 0, "bonferroni": 0, "bh": 0, "min_log10_p": 0.0})
        e["tests"] += 1
        e["bonferroni"] += lp <= bonf
        e["bh"] += i in bh_set
        e["min_log10_p"] = min(e["min_log10_p"], lp)
    # category table at the stacked 60 Hz bin and at the 29.7 Hz peak bin
    stack = json.loads((common.OUT / "a1b_job_stack.json").read_text())
    population = re.compile(r"ground|excited|relax|cz_kick")
    cat_tables: dict[str, Any] = {}
    for label, sel in (
        ("60hz_window", lambda r: r["bin_label"] == "60hz_window_peak"),
        ("29.7hz_peak", lambda r: r["bin_label"] == "narrow_peak" and 29.0 < r["hz"] < 30.5),
    ):
        pop = [0, 0]
        phase = [0, 0]
        for r in stack["pub_rows_at_flagged_bins"]:
            if not sel(r):
                continue
            member = (r["members"] or ["?"])[0]
            bucket = pop if population.search(member) else phase
            bucket[0] += 1
            bucket[1] += r["log10_p_bin"] < -3
        cat_tables[label] = {
            "population_only_pubs": pop,
            "phase_or_other_pubs": phase,
            "format": "[n PUB rows, n with log10 p < -3 at the bin]",
        }

    def group(fam: str) -> str:
        tag, rest = fam.split(":", 1)
        if tag in ("a3", "a4"):
            dataset = "pilot" if rest.startswith("pilot") else "state_prep"
            kind = rest.rsplit("_", 1)[-1]
            trimmed = "_trimmed" if "_trimmed_" in rest else ""
            return f"{tag}:{dataset}_{kind}{trimmed}"
        return fam

    rollup: dict[str, dict[str, Any]] = {}
    for i, (_tid, fam, lp) in enumerate(tests):
        g = rollup.setdefault(group(fam), {"tests": 0, "global_bonferroni": 0, "global_bh": 0})
        g["tests"] += 1
        g["global_bonferroni"] += lp <= bonf
        g["global_bh"] += i in bh_set
    own = {}
    for tag, fname in (
        ("a1", "a1_line_scan"),
        ("a1b", "a1b_job_stack"),
        ("a2", "a2_burst"),
        ("a3", "a3_coupler_distance"),
        ("a4", "a4_lag1_memory"),
        ("a5", "a5_run_length"),
        ("a6", "a6_calibration_age"),
    ):
        c = json.loads((common.OUT / f"{fname}.json").read_text())["corrections"]
        own[tag] = {
            "tests": c["n_tests"],
            "log10_line": c.get("bonferroni_log10_threshold"),
            "n_bonferroni": c["n_bonferroni"],
            "n_bh": c["n_bh"],
        }
    per_tag: dict[str, Any] = {}
    for tag in FILES:
        rows = [(f, g) for f, g in rollup.items() if f.startswith(tag + ":")]
        per_tag[tag] = {
            "tests": sum(g["tests"] for _, g in rows),
            "global_bonferroni": sum(g["global_bonferroni"] for _, g in rows),
            "global_bh": sum(g["global_bh"] for _, g in rows),
        }
    from scipy.stats import t as tdist

    slope = json.loads((common.OUT / "a6_calibration_age.json").read_text())["age_slope"]
    tcrit = float(tdist.ppf(1 - ALPHA / n / 2, slope["dof"]))
    a6_global = {
        "slope_per_hour": slope["slope_excess_per_hour"],
        "se": slope["se"],
        "dof": slope["dof"],
        "t_critical_at_global_alpha": tcrit,
        "interval_at_global_alpha": [
            slope["slope_excess_per_hour"] - tcrit * slope["se"],
            slope["slope_excess_per_hour"] + tcrit * slope["se"],
        ],
    }
    without_stack = {
        "n_global_bonferroni_without_a1b_stacks": sum(v["global_bonferroni"] for t, v in per_tag.items() if t != "a1b"),
        "n_global_bh_without_a1b_stacks": sum(v["global_bh"] for t, v in per_tag.items() if t != "a1b"),
        "note": "same global lines as above; the a1b stack tests keep their counts in the line but drop from the tally",
    }
    out = {
        "a6_globally_corrected_slope_interval": a6_global,
        "tally_without_anti_conservative_stacks": without_stack,
        "analysis_own_correction": own,
        "global_by_analysis": per_tag,
        "global_by_group": rollup,
        "n_tests_total": n,
        "tests_per_analysis_file": per,
        "alpha": ALPHA,
        "global_bonferroni_log10_threshold": bonf,
        "n_global_bonferroni": sum(1 for t in tests if t[2] <= bonf),
        "n_global_bh": bh_cut,
        "by_family": summary,
        "category_table": cat_tables,
    }
    common.write_json(common.OUT / "aggregate.json", out)
    print(json.dumps({k: v for k, v in out.items() if k != "by_family"}, indent=1))
    print("own correction", json.dumps(own))
    print("global by analysis", json.dumps(per_tag))
    for group_name, group_row in sorted(rollup.items()):
        print(group_name, group_row)


if __name__ == "__main__":
    main()
