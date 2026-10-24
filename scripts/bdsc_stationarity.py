"""Belenos stationarity case under a frozen stray-detector veto: request builder, checkpoints and readout.

The case repeats the four frozen requests of the crossed diagnostic
(scripts/bdsc_diagnostic.py, results/quandela/cases/bdsc_diagnostic/) in two
new acquisition windows: block S1 runs the b1-j1 and b1-j2 requests, block S2
the b2-j1 and b2-j2 requests, starting at least one hour after S1 ends. Each
request keeps its source manifest's compilation seeds, circuit parameters,
groups, drawn order, circuit and empty mitigation list; only the family name
and the per-iteration sample and shot budgets change (TRIALS samples and
MAX_SHOTS shots per iteration), so no QRNG read is made. --check proves that
every request equals its source in every other field.

Output mode bdsc_diagnostic.STRAY_MODE lies outside every selection and target
support and carries the largest plan-time dark-count rate of qpu:belenos. The
readout reads every test of bdsc_diagnostic.analyse() on two vetoed eligible
sets (bdsc_stray_mode_veto): the primary removes the stray detector from every
pattern before the one-click rule (detector_absent), the secondary subtracts
stray one-click samples from the eligible count. Beside the preregistered
falsifiers of docs/design/bdsc-qualification.md (heterogeneity of the S1-to-S2
matched changes, the coincidence test), it reports the non-counting variance
tau^2 of the matched changes with and without the veto, which does not shrink
with the sample count as the heterogeneity statistic's power grows, the common
superposition shift, the confounded group-by-block contrast, the stray share
against the plan-time and post-collection dark-count rates, and whether every
returned circuit equals its retained diagnostic counterpart.

Usage:
  "$PYTHON" scripts/bdsc_stationarity.py --write
  "$PYTHON" scripts/bdsc_stationarity.py --check
  "$PYTHON" scripts/bdsc_stationarity.py --plan-check PLAN_JSON
  "$PYTHON" scripts/bdsc_stationarity.py --matched-check RUN_DIR
  "$PYTHON" scripts/bdsc_stationarity.py --readout RUN_DIR...
  "$PYTHON" scripts/bdsc_stationarity.py --calibration-contrast BEFORE_RUN AFTER_RUN

--write and --check also build RETAINED, the same analysis of the retained
diagnostic runs (which chose the veto, so it tests nothing) with the primary's
projected readings at 40000 and TRIALS samples. --check also replays READOUT
and CONTRAST from their retained runs and requires each to equal its file.
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
from scipy.optimize import brentq
from scipy.stats import chi2, norm

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import bdsc_diagnostic as diag  # noqa: E402
import bdsc_stray_mode_veto as veto  # noqa: E402
from qi_readout_ringdown_cases import fsum_rows, libm_map  # noqa: E402

import parallel  # noqa: E402

CASE = ROOT / "docs/evidence/bdsc/stationarity/case.json"
CASES_DIR = ROOT / "results/quandela/cases/bdsc_stationarity"
SOURCE_DIR = diag.CASES_DIR
FAMILY = "bdsc_stationarity"
JOBS = ("b1-j1", "b1-j2", "b2-j1", "b2-j2")
# Every retained diagnostic iteration used exactly as many shots as samples (nb_shots_used equals samples on all 96),
# so a shot budget 1.2 times the sample budget stops on samples; a job bills its largest iteration's max_shots.
TRIALS = 100000
MAX_SHOTS = 120000
# The only manifest fields a request changes from its source; settings, circuit, policy and order stay equal.
CHANGED = ("family", "max_samples", "max_shots")
ADDED = ("source", "stationarity_case_sha256")
# Post-collection platform reads: scripts/qd_platform.py snapshot --out DARK_DIR/after-JOB after each collection.
DARK_DIR = ROOT / "results/quandela/bdsc_stationarity_dark"
DARK = veto.DARK
STRAY = veto.STRAY
PLATFORM = diag.bdsc_cases.QUALIFYING_PLATFORM
# The stationarity analysis of the retained diagnostic runs that chose the veto, with the primary's projected
# readings at the diagnostic's and this case's sample counts.
RETAINED = ROOT / "results/quandela/bdsc_stationarity_retained.json"
PROJECTION_SEED = 20261023
PROJECTION_REPLICATES = 10000
# The retained readout of the four post-calibration runs, in job order, and the calibration contrast of the b1-j1
# requests read before and after the Belenos calibration (docs/runbooks/bdsc-qualification-case.md).
# Both are the pinned interpreter's bytes; the unsuffixed predecessors keep the registered bytes of a system-numpy
# build that differs in the last ulps.
RUNS_DIR = ROOT / "results/quandela/runs"
READOUT = ROOT / "results/quandela/bdsc_stationarity_readout_pinned.json"
READOUT_RUNS = (
    "2026-10-23T201808Z-qpu_belenos-bdsc_stationarity-b1-j1-repeat",
    "2026-10-23T202212Z-qpu_belenos-bdsc_stationarity-b1-j2",
    "2026-10-23T213050Z-qpu_belenos-bdsc_stationarity-b2-j1",
    "2026-10-23T213450Z-qpu_belenos-bdsc_stationarity-b2-j2",
)
CONTRAST = ROOT / "results/quandela/bdsc_stationarity_calibration_contrast_pinned.json"
CONTRAST_RUNS = (
    "2026-10-23T195000Z-qpu_belenos-bdsc_stationarity-b1-j1",
    "2026-10-23T201808Z-qpu_belenos-bdsc_stationarity-b1-j1-repeat",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def seconds_per_job(iterations: int) -> float:
    return iterations * (diag.SECONDS_PER_ITERATION + diag.SECONDS_PER_SAMPLE * TRIALS)


def sources() -> dict[str, dict[str, Any]]:
    """Each job's source manifest and circuit bytes from the committed diagnostic case directories."""
    out = {}
    for job in JOBS:
        manifest_bytes = (SOURCE_DIR / job / "cases.json").read_bytes()
        circuit_bytes = (SOURCE_DIR / job / "circuit.json").read_bytes()
        manifest = json.loads(manifest_bytes)
        require(manifest.get("job") == job and manifest.get("family") == diag.FAMILY, f"{job}: not a diagnostic job")
        require(not manifest.get("draft", True) and isinstance(manifest.get("draw"), dict), f"{job}: no bound draw")
        require(manifest.get("mitigations") == diag.POLICY, f"{job}: the source policy is not the empty list")
        out[job] = {"manifest": manifest, "manifest_bytes": manifest_bytes, "circuit_bytes": circuit_bytes}
    return out


def case_record(found: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """The frozen layout, resources, analysis and stop conditions of the stationarity case."""
    per_job = {job: len(found[job]["manifest"]["settings"]) for job in JOBS}
    draws = {json.dumps(found[job]["manifest"]["draw"], sort_keys=True) for job in JOBS}
    require(len(draws) == 1, "the source manifests bind more than one QRNG draw")
    job_seconds = {job: round(seconds_per_job(n), 3) for job, n in per_job.items()}
    return {
        "schema": "bdsc-stationarity-case-v1",
        "record": "stationarity_case",
        "question": "does removing output detector 5 from every pattern remove the instance-specific change of "
        "matched requests between two acquisition windows, and are mode-5 clicks independent of the prepared state",
        "authorization": "none: the case waits for its written-case approval; it makes no QRNG read",
        "source": {
            "diagnostic_case_sha256": sha256_bytes(diag.CASE.read_bytes()),
            "draw": found[JOBS[0]]["manifest"]["draw"],
            "manifests": {
                job: {
                    "cases": rel(SOURCE_DIR / job / "cases.json"),
                    "cases_sha256": sha256_bytes(found[job]["manifest_bytes"]),
                    "circuit_sha256": sha256_bytes(found[job]["circuit_bytes"]),
                }
                for job in JOBS
            },
            "retained_runs": {job: run for job, run in zip(JOBS, veto.RUNS, strict=True)},
        },
        "design": {
            "blocks": {"S1": ["b1-j1", "b1-j2"], "S2": ["b2-j1", "b2-j2"]},
            "block_gap_hours": diag.BLOCK_GAP_HOURS,
            "instances": sum(per_job.values()),
            "eligible_trials_per_instance": TRIALS,
            "max_shots_per_iteration": MAX_SHOTS,
            "changed_fields": list(CHANGED),
            "unchanged": "settings (seeds, parameters, columns, groups, drawn order), circuit.json, the empty "
            "mitigation list, command, gate form, selected modes and eligibility of each source manifest",
            "stray_mode": STRAY,
            "veto": {
                "primary": "detector_absent: detector 5 is removed from every pattern before the one-click rule",
                "secondary": "subtract: mode-5 one-click samples leave the eligible count",
            },
            "slots": "each (template, seed) group runs in one job per block; the groups of S1's job 1 run as S2's "
            "job 2 at matched positions and the reverse",
        },
        "jobs": [
            {"job": job, "block": "S1" if job.startswith("b1") else "S2", "iterations": per_job[job]} for job in JOBS
        ],
        "resources": {
            "billing_rule": "1 credit per job plus 1e-6 per shot of the job's largest iteration max_shots",
            "credits_per_job": round(diag.CREDIT_PER_JOB + diag.CREDIT_PER_SHOT * MAX_SHOTS, 6),
            "credits": round(len(JOBS) * (diag.CREDIT_PER_JOB + diag.CREDIT_PER_SHOT * MAX_SHOTS), 6),
            "seconds_per_job_estimate": job_seconds,
            "seconds_estimate": round(sum(job_seconds.values()), 3),
            "timing_rule": "6.3 s plus 2.6e-05 s per sample for each iteration against the 300 s per-job limit; "
            "measured at up to 40000 samples per iteration, where the four diagnostic jobs ran 164 to 171 s "
            "against 176.16 s predicted; the written case restates the live qd_platform.py plan output",
        },
        "analysis": {
            "observation": "one-click selected fraction under each eligible set; every standard error is a "
            "reference value under independent Bernoulli trials",
            "primary": "heterogeneity of the S1-to-S2 matched changes about their class means under detector_absent "
            "(bdsc_diagnostic.analyse block_change); resolved at p < 0.01 falsifies the claim that mode 5 carried "
            "the instance-specific change",
            "coincidence_test": "bdsc_stray_mode_veto.coincidence_test on all 96 instances, calibrated on its "
            "conditional hypergeometric null (100000 draws, seed 20261023); resolved at p < 0.01 rejects the "
            "dark-click reading",
            "excess_variance": "reported, decides nothing: the variance tau^2 of the matched changes beyond their "
            "reference counting errors per class (superposition, f, g), by the Paule-Mandel estimate with "
            "its Q-profile 95 % interval, raw and under each veto, and the share 1 - tau^2(veto) / "
            "tau^2(raw) with its lower bound from the veto's upper limit; it reads the size of a residual change "
            "that the heterogeneity test at 100000 trials can resolve",
            "common_shift": "the superposition class-mean change S1 to S2 with its z under detector_absent, read as a "
            "window effect under an additive, group-independent slot effect; its sign against the retained -0.0044 "
            "is reported and decides nothing",
            "group_by_block": "the superposition mean change of the groups that moved from job 1 to job 2 minus that "
            "of the groups that moved from job 2 to job 1, with its z; a slot effect and a group-specific window "
            "change are confounded in it, so it decides nothing",
            "reported": [
                "the mode-5 share per job and block against the plan-time and post-collection dark-count rates",
                "the mode-5 share against each job's recorded duration per sample",
                "the position trend of the mode-5 share in each job",
                "the seed-by-state interaction at fixed seeds under each eligible set",
                "how many returned circuits equal their retained diagnostic counterparts",
                "every analysis on the raw one-click fractions",
            ],
            "tests": f"resolved at p < {diag.ALPHA}, consistent at p >= {diag.CONSISTENT_P}, inconclusive between",
            "scope": "a consistent primary reading supports designing a veto-based confirmation and certifies nothing",
        },
        "stop_conditions": [
            "scripts/qd_platform.py plan refuses the platform",
            "--plan-check on the plan output finds a mode other than 5 at or above mode 5's dark-count rate",
            "a retained job body differs from the empty mitigation list, or a result is not an integer BSCount",
            f"a job fails, an iteration returns fewer than {TRIALS} samples, or the one-click rule (before the veto) "
            "excludes more than 0.01 of an iteration's samples",
            "an iteration returns no compiled circuit or no positive result_fields.physical_perf",
            "--matched-check finds a returned-circuit hash that differs from its retained diagnostic counterpart",
            "a job is submitted before the previous job is collected and checked",
            "S2 would start within one hour of S1's last execution end",
            "a scheduled maintenance window overlaps the span from S1's first execution to S2's last",
            "spent credits or seconds reach the approved ceiling",
        ],
        "resubmission": "a job that ends canceled before its start time with 0 samples is resubmitted once, "
        "unchanged, and its run directory records the canceled attempt; a second cancellation of the same job, a "
        "started job that failed or a cancellation the case did not order stops the case",
    }


def documents() -> dict[str, bytes | dict[str, bytes]]:
    """{"case.json": bytes, job: {"cases.json": bytes, "circuit.json": bytes}} built from the source manifests."""
    found = sources()
    record_bytes = (json.dumps(case_record(found), indent=1) + "\n").encode()
    out: dict[str, bytes | dict[str, bytes]] = {"case.json": record_bytes}
    for job in JOBS:
        source = found[job]["manifest"]
        manifest = dict(source)
        iterations = len(source["settings"])
        manifest["family"] = FAMILY
        manifest["max_samples"] = TRIALS * iterations
        manifest["max_shots"] = MAX_SHOTS * iterations
        manifest["source"] = {
            "cases": rel(SOURCE_DIR / job / "cases.json"),
            "cases_sha256": sha256_bytes(found[job]["manifest_bytes"]),
        }
        manifest["stationarity_case_sha256"] = sha256_bytes(record_bytes)
        out[job] = {
            "cases.json": (json.dumps(manifest, indent=1) + "\n").encode(),
            "circuit.json": found[job]["circuit_bytes"],
        }
    return out


def request_differences(manifest: dict[str, Any], source: dict[str, Any]) -> list[str]:
    """Fields in which a stationarity manifest differs from its source manifest, apart from CHANGED and ADDED."""
    keys = (set(manifest) | set(source)) - set(CHANGED) - set(ADDED)
    return sorted(k for k in keys if manifest.get(k) != source.get(k))


def write() -> None:
    for name, content in documents().items():
        if isinstance(content, bytes):
            CASE.parent.mkdir(parents=True, exist_ok=True)
            CASE.write_bytes(content)
            continue
        (CASES_DIR / name).mkdir(parents=True, exist_ok=True)
        for file, data in content.items():
            (CASES_DIR / name / file).write_bytes(data)
    print(f"bdsc stationarity: wrote {rel(CASE)} and the job directories under {rel(CASES_DIR)}")


def check() -> None:
    """The committed record and job directories equal a fresh build, and each request equals its source."""
    fresh = documents()
    require(CASE.read_bytes() == fresh["case.json"], f"{rel(CASE)} differs from a fresh build")
    present = sorted(p.name for p in CASES_DIR.iterdir() if p.is_dir())
    require(present == list(JOBS), f"job directories differ: {sorted(set(present) ^ set(JOBS))}")
    found = sources()
    for job in JOBS:
        files = fresh[job]
        require(isinstance(files, dict), f"{job}: not a job")
        if not isinstance(files, dict):
            continue
        for name, data in files.items():
            require((CASES_DIR / job / name).read_bytes() == data, f"{job}/{name} differs from a fresh build")
        manifest = json.loads(files["cases.json"])
        source = found[job]["manifest"]
        differing = request_differences(manifest, source)
        require(not differing, f"{job}: the request differs from its source in {differing}")
        require(manifest["settings"] == source["settings"], f"{job}: settings differ from the source")
        require(manifest["max_samples"] // len(manifest["settings"]) == TRIALS, f"{job}: sample budget")
        require(manifest["max_shots"] // len(manifest["settings"]) == MAX_SHOTS, f"{job}: shot budget")
    print(f"bdsc stationarity: the case record and {len(JOBS)} job directories match a fresh build and their sources")


def mode_rates(value: Any, owner: str) -> list[float]:
    """A dark-count reading as one float per mode of the chip."""
    if not (isinstance(value, list) and len(value) == diag.cert.MODES):
        raise ValueError(f"{owner}: dark counts do not cover every mode")
    return [float(r) for r in value]


def dark_rates(perfs: dict[str, Any], owner: str) -> list[float]:
    """The per-mode dark-count rates of one platform reading, with mode 5 above every other mode."""
    rates = mode_rates(perfs.get(DARK), owner)
    others = max(r for m, r in enumerate(rates) if m != STRAY)
    require(rates[STRAY] > others, f"{owner}: mode {STRAY} reads {rates[STRAY]}, not above every other mode ({others})")
    return rates


def plan_check(path: Path) -> int:
    """Apply the plan-time stop condition to the JSON that qd_platform.py plan printed."""
    plan = json.loads(path.read_text(encoding="utf-8"))
    rates = dark_rates(plan.get("perfs_at_plan") or {}, str(path))
    others = max(r for m, r in enumerate(rates) if m != STRAY)
    print(
        f"bdsc stationarity plan check: mode {STRAY} reads {rates[STRAY]} dark counts/s, every other mode <= {others}"
    )
    return 0


def admit(run: Path, validate: bool, frozen: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """(manifest, result, submission) of one stationarity run after every integrity check of the readout."""
    import qd_platform

    if validate:
        qd_platform.run_facts(run)
    manifest_bytes = (run / "cases.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    result = json.loads((run / "results.json").read_text(encoding="utf-8"))
    submission = json.loads((run / "submission.json").read_text(encoding="utf-8"))
    body_bytes = (run / "job-body.json").read_bytes()
    job = manifest.get("job")
    require(job in JOBS and isinstance(frozen.get(job), dict), f"{run}: job {job!r} is not a job of the case")
    require(manifest_bytes == frozen[job]["cases.json"], f"{run}: cases.json differs from the frozen build")
    require(submission.get("platform") == PLATFORM, f"{run}: submitted to {submission.get('platform')!r}")
    served = result.get("data", {}).get("platform_name")
    require(served == PLATFORM, f"{run}: the service reports {served!r}")
    require(submission.get("cases_sha256") == sha256_bytes(manifest_bytes), f"{run}: cases.json changed")
    require(submission.get("body_sha256") == diag.bdsc_cases.body_digest(body_bytes), f"{run}: job-body.json differs")
    require(result.get("job_id") == submission.get("job_id"), f"{run}: the result answers another job")
    require(qd_platform.body_mitigations(json.loads(body_bytes)) == diag.POLICY, f"{run}: the body's policy differs")
    require(result.get("status", {}).get("status") == "completed", f"{run}: the job did not complete")
    require(result.get("partial") is False, f"{run}: a partial result")
    return manifest, result, submission


def retained_circuits(job: str) -> dict[int, str]:
    """Returned-circuit sha256 per instance of the retained diagnostic run of the same requests."""
    context: dict[str, Any] = {}
    manifest, result, _ = diag.admit_run(ROOT / dict(zip(JOBS, veto.RUNS, strict=True))[job], True, context)
    return {index: item["circuit_sha256"] for index, item in diag.observations(manifest, result).items()}


def matched_check(run: Path, validate: bool = True) -> list[str]:
    """Instances of one collected run whose returned circuit differs from its retained diagnostic counterpart."""
    frozen = documents()
    manifest, result, _ = admit(run, validate, frozen)
    items = diag.observations(manifest, result, TRIALS)
    retained = retained_circuits(manifest["job"])
    names = {s["instance_index"]: s["name"] for s in manifest["settings"]}
    return [
        f"{names[index]}: returned another circuit than the retained diagnostic run"
        for index, item in sorted(items.items())
        if item["circuit_sha256"] != retained[index]
    ]


def run_matched_check(run: Path) -> int:
    mismatches = matched_check(run)
    if mismatches:
        print(
            f"bdsc stationarity matched check: {len(mismatches)} instances recompiled; stop the case", file=sys.stderr
        )
        for line in mismatches:
            print(f"  {line}", file=sys.stderr)
        return 1
    print(f"bdsc stationarity matched check: {run.name} returned every retained diagnostic circuit")
    return 0


def class_excess_variance(group: list[tuple[float, float]]) -> dict[str, Any]:
    """Between-instance variance tau^2 of one class's (change, reference error) pairs beyond their reference errors.

    The generalized heterogeneity Q(tau^2) sums w (change - mean)^2 with w = 1 / (se^2 + tau^2) and the
    inverse-variance mean; it falls monotonically in tau^2. The Paule-Mandel estimate solves Q(tau^2) = df (0 when
    Q(0) <= df), and the 95 % interval solves Q(tau^2) at the chi-square quantiles on df (Q-profile), so the estimate
    and its interval invert one statistic.
    """
    df = len(group) - 1

    def q(tau2: float) -> float:
        weights = [1 / (s * s + tau2) for _, s in group]
        mean = sum(w * v for w, (v, _) in zip(weights, group, strict=True)) / sum(weights)
        return sum(w * (v - mean) ** 2 for w, (v, _) in zip(weights, group, strict=True))

    statistic = q(0.0)

    def solve(target: float) -> float:
        # A selected fraction lies in [0, 1], so a change has variance below 1 and Q(1) lies below every target.
        if statistic <= target:
            return 0.0
        return float(brentq(lambda t: q(t) - target, 0.0, 1.0, xtol=1e-15))

    estimate = solve(float(df))
    return {
        "n": len(group),
        "q": statistic,
        "df": df,
        "p_value": float(chi2.sf(statistic, df)),
        "tau2": estimate,
        "tau": math.sqrt(estimate),
        "tau2_interval_95": [solve(float(chi2.ppf(0.975, df))), solve(float(chi2.ppf(0.025, df)))],
        "median_se": float(sorted(s for _, s in group)[len(group) // 2]),
    }


def excess_variance(changes: list[dict[str, Any]]) -> dict[str, Any]:
    """Paule-Mandel tau^2 with its Q-profile interval per block-change class (bdsc_diagnostic.CLASSES).

    Each class gets its own tau^2: the reference errors of f and g lie near 0.0005 and those of the superpositions
    near 0.0035, so one tau^2 common to the classes cannot fit both (a common estimate implies an expected Q well
    above the observed one on the retained diagnostic).
    """
    return {
        name: class_excess_variance(
            [
                (c["change"], c["se"])
                for c in changes
                if c["same_returned_circuit"] and diag.class_of(c["label"]) == name
            ]
        )
        for name in diag.CLASSES
    }


def group_by_block(changes: list[dict[str, Any]]) -> dict[str, Any]:
    """Superposition mean change of the groups that moved from job 1 to job 2, minus that of the reverse groups."""
    first_job = {(i["template"], i["slot"]): i["job"] for i in diag.instances() if i["block"] == 1}
    means = {}
    for job in ("b1-j1", "b1-j2"):
        members = [
            c
            for c in changes
            if c["same_returned_circuit"]
            and diag.class_of(c["label"]) == "superposition"
            and first_job[(c["template"], c["slot"])] == job
        ]
        weights = [1 / c["se"] ** 2 for c in members]
        means[job] = (
            sum(w * c["change"] for w, c in zip(weights, members, strict=True)) / sum(weights),
            1 / math.sqrt(sum(weights)),
            len(members),
        )
    contrast = means["b1-j1"][0] - means["b1-j2"][0]
    se = math.hypot(means["b1-j1"][1], means["b1-j2"][1])
    p_value = float(2 * norm.sf(abs(contrast / se)))
    return {
        "job1_to_job2": {"mean": means["b1-j1"][0], "se": means["b1-j1"][1], "n": means["b1-j1"][2]},
        "job2_to_job1": {"mean": means["b1-j2"][0], "se": means["b1-j2"][1], "n": means["b1-j2"][2]},
        "contrast": contrast,
        "se": se,
        "z": contrast / se,
        "p_value": p_value,
        "reading": "confounded: a slot effect and a group-specific window change; decides nothing",
    }


def summary(read: dict[str, Any]) -> dict[str, Any]:
    return {
        **veto.summary(read),
        "seed_interaction": read["tests"]["seed_interaction"],
        "excess_variance": excess_variance(read["block_changes"]),
        "group_by_block": group_by_block(read["block_changes"]),
    }


def analysis(
    observed: dict[int, dict[str, Any]],
    subtract: dict[int, dict[str, Any]],
    absent: dict[int, dict[str, Any]],
) -> dict[str, Any]:
    """The preregistered and reported readings of the raw and vetoed eligible sets."""
    raw = summary(diag.analyse(observed))
    primary = summary(diag.analyse(absent))
    secondary = summary(diag.analyse(subtract))

    def removed(read: dict[str, Any]) -> dict[str, Any]:
        out = {}
        for name, before in raw["excess_variance"].items():
            after = read["excess_variance"][name]
            if before["tau2"] == 0.0:
                out[name] = {"share": None, "lower_bound": None, "reason": "the raw changes carry no excess variance"}
            else:
                out[name] = {
                    "share": 1 - after["tau2"] / before["tau2"],
                    "lower_bound": 1 - after["tau2_interval_95"][1] / before["tau2"],
                }
        return out

    coincidence = veto.coincidence_test(subtract, absent)
    block_change = primary["block_change"]
    return {
        "primary": {
            "test": "heterogeneity of matched changes under detector_absent",
            "statistic": block_change["statistic"],
            "df": block_change["df"],
            "p_value": block_change["p_value"],
            "reading": block_change["reading"],
        },
        "dark_click_falsifier": coincidence,
        "common_shift": primary["calibration_shift"].get("superposition"),
        "share_of_excess_variance_removed": {"detector_absent": removed(primary), "subtract": removed(secondary)},
        "raw": raw,
        "detector_absent": primary,
        "subtract": secondary,
    }


def post_collection_rates(job: str) -> list[float] | None:
    path = DARK_DIR / f"after-{job}" / "catalogue.json"
    if not path.is_file():
        return None
    catalogue = json.loads(path.read_text(encoding="utf-8"))
    return mode_rates((catalogue.get("processors", {}).get(PLATFORM, {}).get("perfs") or {}).get(DARK), rel(path))


def readout(runs: list[Path], validate: bool = True) -> dict[str, Any]:
    """The analysis of the four collected runs after every integrity, schedule and plan-time check."""
    frozen = documents()
    observed: dict[int, dict[str, Any]] = {}
    subtract: dict[int, dict[str, Any]] = {}
    absent: dict[int, dict[str, Any]] = {}
    stray: dict[int, dict[str, Any]] = {}
    dark: dict[str, Any] = {}
    after: dict[str, Any] = {}
    windows: dict[str, tuple[float, float]] = {}
    collected: dict[str, float] = {}
    submitted: dict[str, float] = {}
    maintenance: set[tuple[float, float]] = set()
    recompiled = 0
    for run in runs:
        manifest, result, submission = admit(run, validate, frozen)
        job = manifest["job"]
        require(job not in windows, f"{run}: job {job} collected twice")
        rates = dark_rates(submission.get("perfs_at_plan") or {}, f"{run}: plan")
        dark[job] = veto.job_dark(rates, result)
        post = post_collection_rates(job)
        after[job] = (
            None
            if post is None
            else {"stray": post[STRAY], "largest_other": max(r for m, r in enumerate(post) if m != STRAY)}
        )
        start = diag.utc(result["data"]["start_time"])
        windows[job] = (start, start + float(result["data"]["duration"]))
        collected[job] = diag.utc(result["collected_utc"])
        submitted[job] = diag.utc(submission["submitted_utc"])
        window = submission.get("platform_at_plan", {}).get("maintenance")
        if isinstance(window, dict):
            maintenance.add((diag.utc(window["start_time"]), diag.utc(window["end_time"])))
        items = diag.observations(manifest, result, TRIALS)
        retained = retained_circuits(job) if validate else {}
        recompiled += sum(1 for index, item in items.items() if retained and item["circuit_sha256"] != retained[index])
        run_subtract, run_absent, run_stray = veto.tallies(manifest, result, items)
        for target, part in ((observed, items), (subtract, run_subtract), (absent, run_absent), (stray, run_stray)):
            target.update(part)
    require(sorted(windows) == sorted(JOBS), f"the readout needs every job; it holds {sorted(windows)}")
    for earlier, later in zip(JOBS, JOBS[1:], strict=False):
        require(collected[earlier] < submitted[later], f"{later} was submitted before {earlier} was collected")
    diag.require_schedule(windows, collected, maintenance)
    report = veto.stray_report(stray, dark, TRIALS)
    report["dark_counts_after_collection"] = after
    report["duration_per_sample"] = {job: d["duration_seconds"] / d["samples"] for job, d in sorted(dark.items())}
    return {
        "schema": "bdsc-stationarity-readout-v1",
        "case_sha256": sha256_bytes(frozen["case.json"]) if isinstance(frozen["case.json"], bytes) else None,
        "runs": [
            {"run": rel(run), "results_sha256": sha256_bytes((run / "results.json").read_bytes())} for run in runs
        ],
        "returned_circuits_differing_from_retained": recompiled if validate else None,
        **analysis(observed, subtract, absent),
        "stray": report,
    }


def instance_changes(before: dict[int, dict[str, Any]], after: dict[int, dict[str, Any]]) -> list[dict[str, Any]]:
    """Per-instance change of the selected fraction from one run of a request set to another run of the same set."""
    require(before.keys() == after.keys(), "the two runs hold different instances")
    labels = {i["index"]: i["label"] for i in diag.instances()}
    out = []
    for index in sorted(before):
        first, second = before[index], after[index]
        p1, p2 = first["selected"] / first["eligible"], second["selected"] / second["eligible"]
        out.append(
            {
                "index": index,
                "label": labels[index],
                "change": p2 - p1,
                "se": math.hypot(diag.reference_se(p1, first["eligible"]), diag.reference_se(p2, second["eligible"])),
                "same_returned_circuit": first["circuit_sha256"] == second["circuit_sha256"],
            }
        )
    return out


def class_shifts(changes: list[dict[str, Any]]) -> dict[str, Any]:
    """Inverse-variance mean change per class with its standard error and z."""
    out = {}
    for name in diag.CLASSES:
        members = [c for c in changes if c["same_returned_circuit"] and diag.class_of(c["label"]) == name]
        weights = [1 / c["se"] ** 2 for c in members]
        mean = sum(w * c["change"] for w, c in zip(weights, members, strict=True)) / sum(weights)
        se = 1 / math.sqrt(sum(weights))
        out[name] = {"mean": mean, "se": se, "z": mean / se, "n": len(members)}
    return out


def calibration_contrast(before: Path, after: Path, validate: bool = True) -> dict[str, Any]:
    """The b1-j1 requests read before and after the Belenos calibration, under the primary veto (reported only).

    Both runs pass every integrity check of the readout. The contrast enters no frozen test: it reports the class
    shifts and the per-class excess variance of the 24 matched changes, and the mode-5 share and plan-time dark-count
    rates of both runs.
    """
    frozen = documents()
    loaded = []
    for run in (before, after):
        manifest, result, submission = admit(run, validate, frozen)
        require(manifest["job"] == "b1-j1", f"{run}: job {manifest['job']!r}, the contrast reads b1-j1 runs")
        items = diag.observations(manifest, result, TRIALS)
        _, absent, stray = veto.tallies(manifest, result, items)
        rates = dark_rates(submission.get("perfs_at_plan") or {}, f"{run}: plan")
        loaded.append((run, result, absent, stray, rates))
    (run1, result1, absent1, stray1, rates1), (run2, result2, absent2, stray2, rates2) = loaded
    require(
        diag.utc(result1["data"]["start_time"]) < diag.utc(result2["data"]["start_time"]),
        "the contrast reads the earlier run first",
    )
    changes = instance_changes(absent1, absent2)

    def share(stray: dict[int, dict[str, Any]]) -> dict[str, float]:
        values = [v["share"] for v in stray.values()]
        return {"mean": float(np.mean(values)), "min": min(values), "max": max(values)}

    return {
        "schema": "bdsc-stationarity-calibration-contrast-v1",
        "reading": "reported only: the same requests across one calibration; enters no frozen test",
        "runs": [
            {"run": rel(run), "results_sha256": sha256_bytes((run / "results.json").read_bytes())}
            for run in (run1, run2)
        ],
        "returned_circuits_differing": sum(1 for c in changes if not c["same_returned_circuit"]),
        "class_shifts": class_shifts(changes),
        "excess_variance": excess_variance(changes),
        "stray_share": {"before": share(stray1), "after": share(stray2)},
        "plan_dark_counts": {
            "before": {"stray": rates1[STRAY], "largest_other": max(r for m, r in enumerate(rates1) if m != STRAY)},
            "after": {"stray": rates2[STRAY], "largest_other": max(r for m, r in enumerate(rates2) if m != STRAY)},
        },
        "changes": changes,
    }


def _projected_q(item: tuple[list[float], list[int], list[float], np.ndarray]) -> list[float]:
    """Heterogeneity Q of each replicate about its class means at fixed weights 1 / se^2 (scalar arithmetic).

    item is (reference errors, class index per change, tau^2 per change, standard normal draws of shape
    replicates x changes); replicate change i is draw_i * sqrt(se_i^2 + tau2_i).
    """
    se, classes, tau2, draws = item
    spread = [math.sqrt(s * s + t) for s, t in zip(se, tau2, strict=True)]
    weights = [1 / (s * s) for s in se]
    members = [[i for i, c in enumerate(classes) if c == k] for k in sorted(set(classes))]
    out = []
    for row in draws.tolist():
        values = [z * sd for z, sd in zip(row, spread, strict=True)]
        total = 0.0
        for group in members:
            weight = sum(weights[i] for i in group)
            mean = sum(weights[i] * values[i] for i in group) / weight
            total += sum(weights[i] * (values[i] - mean) ** 2 for i in group)
        out.append(total)
    return out


def _projected_q_batch(item: tuple[list[float], list[int], list[float], np.ndarray]) -> list[float]:
    """_projected_q(item) for every replicate at once, with the scalar path's bits.

    The products keep the scalar association, fsum_rows repeats builtin sum()'s Neumaier update over each class in
    index order, and every square goes through libm pow as Python's ** does (docs/runbooks/vectorized-fits.md).
    """
    se, classes, tau2, draws = item
    spread = [math.sqrt(s * s + t) for s, t in zip(se, tau2, strict=True)]
    weights = [1 / (s * s) for s in se]
    members = [[i for i, c in enumerate(classes) if c == k] for k in sorted(set(classes))]
    values = [draws[:, i] * spread[i] for i in range(len(se))]
    total = np.zeros(draws.shape[0])
    for group in members:
        weight = sum(weights[i] for i in group)
        mean = fsum_rows([weights[i] * values[i] for i in group]) / weight
        total = total + fsum_rows([weights[i] * libm_map(math.pow, values[i] - mean, 2.0) for i in group])
    return [float(q) for q in total.tolist()]


def projection(changes: list[dict[str, Any]], excess: dict[str, Any]) -> list[dict[str, Any]]:
    """The primary's expected Q and reading probabilities at 40000 and TRIALS samples under three residuals.

    The retained reference errors scale as sqrt(40000 / n), and the residual per class is none, the Paule-Mandel
    estimate, or its Q-profile upper limit. Every scenario's normal draws come from one generator seeded with
    PROJECTION_SEED, drawn in scenario order before the pool maps them.
    """
    kept = [c for c in changes if c["same_returned_circuit"]]
    names = list(diag.CLASSES)
    classes = [names.index(diag.class_of(c["label"])) for c in kept]
    residuals = {
        "none": [0.0] * len(names),
        "point": [excess[name]["tau2"] for name in names],
        "upper_95": [excess[name]["tau2_interval_95"][1] for name in names],
    }
    rng = np.random.default_rng(PROJECTION_SEED)
    scenarios, items = [], []
    for trials in (diag.TRIALS, TRIALS):
        se = [c["se"] * math.sqrt(diag.TRIALS / trials) for c in kept]
        for residual, per_class in residuals.items():
            draws = rng.standard_normal((PROJECTION_REPLICATES, len(kept)))
            scenarios.append({"trials": trials, "residual": residual, "tau2": dict(zip(names, per_class, strict=True))})
            items.append((se, classes, [per_class[k] for k in classes], draws))
    df = len(kept) - len({*classes})
    out = []
    for scenario, qs in zip(scenarios, parallel.ordered_map(_projected_q_batch, items, min_items=1), strict=True):
        p_values = [float(chi2.sf(q, df)) for q in qs]
        out.append(
            {
                **scenario,
                "replicates": PROJECTION_REPLICATES,
                "expected_q": sum(qs) / len(qs),
                "p_resolved": sum(p < diag.ALPHA for p in p_values) / len(qs),
                "p_consistent": sum(p >= diag.CONSISTENT_P for p in p_values) / len(qs),
            }
        )
    return out


def retained() -> dict[str, Any]:
    """The stationarity analysis of the retained diagnostic runs and the primary's projected readings."""
    observed, vetoed, _, _ = veto.collect()
    read = analysis(observed, vetoed["subtract"], vetoed["detector_absent"])
    primary_changes = diag.analyse(vetoed["detector_absent"])["block_changes"]
    return {
        "schema": "bdsc-stationarity-retained-v1",
        "status": "exploratory: these are the runs whose outcomes chose the veto, so nothing here tests it",
        "runs": [
            {"run": run, "results_sha256": sha256_bytes((ROOT / run / "results.json").read_bytes())}
            for run in veto.RUNS
        ],
        "primary": read["primary"],
        "dark_click_falsifier": read["dark_click_falsifier"],
        "common_shift": read["common_shift"],
        "share_of_excess_variance_removed": read["share_of_excess_variance_removed"],
        "excess_variance": {name: read[name]["excess_variance"] for name in ("raw", "detector_absent", "subtract")},
        "group_by_block": {name: read[name]["group_by_block"] for name in ("raw", "detector_absent", "subtract")},
        "projection": projection(primary_changes, read["detector_absent"]["excess_variance"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    group.add_argument("--plan-check", type=Path, metavar="PLAN_JSON")
    group.add_argument("--matched-check", type=Path, metavar="RUN_DIR")
    group.add_argument("--readout", type=Path, nargs="+")
    group.add_argument("--calibration-contrast", type=Path, nargs=2, metavar=("BEFORE_RUN", "AFTER_RUN"))
    args = parser.parse_args()
    if args.write:
        write()
        RETAINED.write_text(json.dumps(retained(), indent=1, sort_keys=True) + "\n")
        print(f"bdsc stationarity: wrote {rel(RETAINED)}")
    elif args.check:
        check()
        text = json.dumps(retained(), indent=1, sort_keys=True) + "\n"
        require(RETAINED.is_file() and RETAINED.read_text() == text, f"{rel(RETAINED)} differs from a fresh build")
        print(f"bdsc stationarity: {rel(RETAINED)} matches a fresh build")
        replays = (
            (READOUT, lambda: readout([RUNS_DIR / run for run in READOUT_RUNS])),
            (CONTRAST, lambda: calibration_contrast(RUNS_DIR / CONTRAST_RUNS[0], RUNS_DIR / CONTRAST_RUNS[1])),
        )
        for path, build in replays:
            text = json.dumps(build(), indent=1, sort_keys=True) + "\n"
            require(path.read_text() == text, f"{rel(path)} differs from a fresh analysis of its retained runs")
            print(f"bdsc stationarity: {rel(path)} matches a fresh analysis of its retained runs")
    elif args.plan_check:
        return plan_check(args.plan_check)
    elif args.matched_check:
        return run_matched_check(args.matched_check)
    elif args.calibration_contrast:
        before, after = (run.resolve() for run in args.calibration_contrast)
        print(json.dumps(calibration_contrast(before, after), indent=1, sort_keys=True))
    else:
        print(json.dumps(readout([run.resolve() for run in args.readout]), indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
