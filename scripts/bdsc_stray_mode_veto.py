"""Exploratory reanalysis of the Belenos crossed diagnostic with the stray output mode vetoed.

The crossed diagnostic (scripts/bdsc_diagnostic.py) reads every one-click
sample as eligible. Output mode bdsc_diagnostic.STRAY_MODE lies outside every
selection and every target support of the case, and the platform record lists
its dark-count rate one to three orders above every other detector of
qpu:belenos. This script reruns the diagnostic's analyse() on the four retained
runs under two definitions of a veto on that mode and reports, beside them, the
stray mode's share of each iteration's one-click samples, its block change on
matched instances and its rank correlation with position in the job.

- subtract: a one-click sample in the stray mode leaves the eligible count;
  every other tally is the diagnostic's.
- detector_absent: the stray detector is removed from every detection pattern
  before the eligibility rule runs, so a pattern of one stray click and one
  other click becomes a one-click sample of the other mode.

The veto was chosen after the diagnostic's outcomes were seen, so neither
reading confirms anything; the stationarity amendment of
docs/runbooks/bdsc-qualification-case.md freezes one definition before new data.
Standard errors are the diagnostic's reference values under independent
Bernoulli trials.

Usage:
  "$PYTHON" scripts/bdsc_stray_mode_veto.py --write
  "$PYTHON" scripts/bdsc_stray_mode_veto.py --check
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
from scipy.stats import chi2, spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import bdsc_diagnostic as diag  # noqa: E402

RUNS = (
    "results/quandela/runs/2026-10-22T160023Z-qpu_belenos-bdsc_diagnostic-b1-j1",
    "results/quandela/runs/2026-10-22T160340Z-qpu_belenos-bdsc_diagnostic-b1-j2",
    "results/quandela/runs/2026-10-23T073329Z-qpu_belenos-bdsc_diagnostic-b2-j1",
    "results/quandela/runs/2026-10-23T081314Z-qpu_belenos-bdsc_diagnostic-b2-j2",
)
OUT = ROOT / "results/quandela/bdsc_stray_mode_veto.json"
STRAY = diag.STRAY_MODE


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def detector_absent(counts: dict[str, int], selected: set[int], support: list[int]) -> dict[str, int]:
    """Selected, eligible and on-support one-click tallies with the stray detector removed from every pattern."""
    out = {"selected": 0, "eligible": 0, "selected_on_support": 0, "on_support": 0}
    for pattern, count in counts.items():
        clicks = [m for m, c in enumerate(pattern.split(",")) if int(c) > 0 and m != STRAY]
        if len(clicks) != 1:
            continue
        mode = clicks[0]
        out["eligible"] += count
        out["selected"] += count if mode in selected else 0
        if mode in support:
            out["on_support"] += count
            out["selected_on_support"] += count if mode in selected else 0
    return out


DARK = "Dark counts (detection/s)"


def collect() -> tuple[
    dict[int, dict[str, Any]], dict[str, dict[int, dict[str, Any]]], dict[int, dict[str, Any]], dict[str, Any]
]:
    """The diagnostic's observations, the two vetoed variants, the stray-mode tallies and each job's dark counts."""
    observed: dict[int, dict[str, Any]] = {}
    subtract: dict[int, dict[str, Any]] = {}
    absent: dict[int, dict[str, Any]] = {}
    stray: dict[int, dict[str, Any]] = {}
    dark: dict[str, Any] = {}
    context: dict[str, Any] = {}
    for run in RUNS:
        manifest, result, submission = diag.admit_run(ROOT / run, True, context)
        rates = submission["perfs_at_plan"][DARK]
        require(len(rates) == diag.cert.MODES, f"{run}: dark counts do not cover every mode")
        dark[manifest["job"]] = {
            "stray": rates[STRAY],
            "largest_other": max(r for m, r in enumerate(rates) if m != STRAY),
        }
        selected = set(manifest["selected_modes"])
        require(STRAY not in selected, f"{run}: the stray mode is selected")
        items = diag.observations(manifest, result)
        for setting, iteration in zip(manifest["settings"], result["iterations"], strict=True):
            index = setting["instance_index"]
            weight = np.abs(diag.forensics.column(setting)) ** 2
            support = [m for m in range(diag.cert.MODES) if weight[m] > diag.forensics.SUPPORT_FLOOR]
            require(STRAY not in support, f"{run}/{setting['name']}: the stray mode is on the target support")
            per_mode, _, _ = diag.forensics.one_click(iteration["counts"], diag.cert.MODES)
            item = items[index]
            observed[index] = item
            subtract[index] = {
                **item,
                "eligible": item["eligible"] - per_mode[STRAY],
                "outside_share": 1 - item["on_support"] / (item["eligible"] - per_mode[STRAY]),
            }
            tally = detector_absent(iteration["counts"], selected, support)
            absent[index] = {**item, **tally, "outside_share": 1 - tally["on_support"] / tally["eligible"]}
            stray[index] = {
                "job": manifest["job"],
                "position": item["position"],
                "share": per_mode[STRAY] / item["eligible"],
                "perf": item["perf"],
                "other_outside_share": (item["eligible"] - item["on_support"] - per_mode[STRAY]) / item["eligible"],
            }
    return observed, {"subtract": subtract, "detector_absent": absent}, stray, dark


def coincidence_test(subtract: dict[int, dict[str, Any]], absent: dict[int, dict[str, Any]]) -> dict[str, Any]:
    """The paired falsifier of the dark-click reading: coincident trials against the subtract-eligible trials.

    The detector-absent eligible set is the subtract set plus the coincident trials (one stray click beside exactly
    one other click), two disjoint trial sets of one iteration. A state-independent dark click leaves the selected
    fraction of the coincident trials equal to that of the subtract set, so per instance
    z = (p_c - p_s) / sqrt(p (1 - p) (1 / c + 1 / n)) with the pooled p, and the sum of z^2 over the instances with
    c > 0 and 0 < p < 1 is chi-square on their count; a resolved reading (p < 0.01) rejects the dark-click reading.
    """
    statistic, terms = 0.0, 0
    for index, item in subtract.items():
        n, s = item["eligible"], item["selected"]
        c = absent[index]["eligible"] - n
        k = absent[index]["selected"] - s
        pooled = (s + k) / (n + c)
        if c == 0 or pooled in (0.0, 1.0):
            continue
        statistic += (k / c - s / n) ** 2 / (pooled * (1 - pooled) * (1 / c + 1 / n))
        terms += 1
    p_value = float(chi2.sf(statistic, terms))
    return {"statistic": statistic, "df": terms, "p_value": p_value, "reading": diag.reading(p_value)}


def summary(read: dict[str, Any]) -> dict[str, Any]:
    return {
        "branch": read["branch"],
        "block_change": read["tests"]["block_change"],
        "calibration_shift": read["calibration_shift"],
        "readings": read["readings"],
        "residuals_beyond_margin": read["residuals_beyond_margin"],
    }


def stray_report(stray: dict[int, dict[str, Any]], dark: dict[str, Any]) -> dict[str, Any]:
    """The stray mode's share per job and block against its plan-time dark-count rate, its matched block change
    against the other off-support share, and its trends with position and with 1 / physical_perf."""
    items = diag.instances()
    key = {(i["block"], i["template"], i["slot"], i["label"]): i["index"] for i in items}
    changes, others = [], []
    for (block, template, slot, label), index in key.items():
        if block == 1:
            match = key[(2, template, slot, label)]
            changes.append(stray[match]["share"] - stray[index]["share"])
            others.append(stray[match]["other_outside_share"] - stray[index]["other_outside_share"])
    per_block = {
        str(block): float(np.mean([stray[i["index"]]["share"] for i in items if i["block"] == block]))
        for block in diag.BLOCKS
    }
    position = {}
    for job in sorted({s["job"] for s in stray.values()}):
        members = sorted((s["position"], s["share"]) for s in stray.values() if s["job"] == job)
        rho, p_value = spearmanr([m[0] for m in members], [m[1] for m in members])
        position[job] = {"n": len(members), "rho": float(rho), "p_value": float(p_value)}
    per_job = {
        job: {
            "share_mean": float(np.mean([s["share"] for s in stray.values() if s["job"] == job])),
            "dark_counts_at_plan": rates,
        }
        for job, rates in sorted(dark.items())
    }
    # A dark-count rate that dominates the stray clicks scales the stray share with that rate between blocks.
    dark_per_block = {str(b): float(np.mean([dark[f"b{b}-j{j}"]["stray"] for j in (1, 2)])) for b in diag.BLOCKS}
    shares = [s["share"] for s in stray.values()]

    # A fixed dark-count rate D over an iteration whose acquisition time scales as 1 / physical_perf makes the stray
    # share rise with D / physical_perf; the plan-time D differs between the blocks, so the law is read on that
    # predictor pooled and on 1 / physical_perf within each block, where one plan-time D holds.
    def rank(pairs: list[tuple[float, float]]) -> dict[str, Any]:
        rho, p_value = spearmanr([x for x, _ in pairs], [y for _, y in pairs])
        return {"n": len(pairs), "rho": float(rho), "p_value": float(p_value)}

    fixed_rate = {
        "dark_over_perf_pooled": rank([(dark[s["job"]]["stray"] / s["perf"], s["share"]) for s in stray.values()]),
        "inverse_perf_by_block": {
            str(b): rank([(1 / s["perf"], s["share"]) for s in stray.values() if s["job"].startswith(f"b{b}")])
            for b in diag.BLOCKS
        },
    }
    return {
        "share_range": [min(shares), max(shares)],
        "share_mean_per_block": per_block,
        "per_job": per_job,
        "block_ratio": {
            "share": per_block["2"] / per_block["1"],
            "dark_counts_at_plan": dark_per_block["2"] / dark_per_block["1"],
        },
        "matched_change": {
            "n": len(changes),
            "stray_mean": float(np.mean(changes)),
            "stray_sd": float(np.std(changes)),
            "other_outside_mean": float(np.mean(others)),
            "other_outside_sd": float(np.std(others)),
        },
        "position": position,
        "fixed_rate_law": fixed_rate,
        "reference_se_of_share": math.sqrt(float(np.mean(shares)) * (1 - float(np.mean(shares))) / diag.TRIALS),
    }


def build() -> dict[str, Any]:
    observed, vetoed, stray, dark = collect()
    return {
        "schema": "bdsc-stray-mode-veto-v1",
        "status": "exploratory: the veto was chosen after the diagnostic's outcomes were seen",
        "stray_mode": STRAY,
        "runs": [
            {"run": run, "results_sha256": hashlib.sha256((ROOT / run / "results.json").read_bytes()).hexdigest()}
            for run in RUNS
        ],
        "definitions": {
            "subtract": "one-click samples in the stray mode leave the eligible count",
            "detector_absent": "the stray detector is removed from every pattern before the one-click rule",
        },
        "raw": summary(diag.analyse(observed)),
        "vetoed": {name: summary(diag.analyse(items)) for name, items in vetoed.items()},
        "coincidence_test": coincidence_test(vetoed["subtract"], vetoed["detector_absent"]),
        "stray": stray_report(stray, dark),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--write", action="store_true")
    action.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = json.dumps(build(), indent=1, sort_keys=True) + "\n"
    if args.write:
        OUT.write_text(text)
    else:
        require(OUT.is_file() and OUT.read_text() == text, f"{OUT.relative_to(ROOT)} differs; regenerate explicitly")
    print(f"stray-mode veto: {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
