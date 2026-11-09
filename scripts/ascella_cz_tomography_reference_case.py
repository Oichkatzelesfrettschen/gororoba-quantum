"""Ascella CZ process tomography reference across the HOM band 90 +- 6.8420696 points: two qpu:ascella jobs of 72
template iterations.

docs/design/ascella-cz-tomography-reference-case.md fixes the request. The estimand, the 144 settings, the six-mode
window at chip modes 0..5, the parity split into two jobs, the eligibility rule, the estimator, the bootstrap and the
pooling rule are those of scripts/ascella_cz_tomography_case.py, imported by name. Four things differ:

- Seeds. Every compilation seed, the bootstrap seed and every forecast dataset seed comes from one fresh ANU QRNG
  draw (DRAW), under the retained case's rule: nonzero values in index order, repeats skipped.
- Budgets. Every iteration shares one shot cap, SHOT_CAP, and takes its own max_samples: the largest multiple of
  SAMPLE_QUANTUM whose Perceval shot estimate, times tomo.SHOT_MARGIN, stays within the cap. An iterated job bills
  1 credit plus 1e-6 per shot up to its largest iteration's max_shots, so with equal caps every iteration spends
  the shots the bill already pays for, and the worst-case seconds, every iteration at its cap, stay within
  max_duration down to the transmittance floor that submission_policy names.
- Gate. A submit_wrapper gate admits a plan at any HOM inside HOM_BAND, at status available or running with the
  token idle, with the shot estimate and an in-lock processor re-read on the plan's perfs, the transmittance at or
  above the floor, and, for job-01, a completed job-00 run with every iteration counted. The request is frozen at
  build: a gate refuses, it never adapts the body to the live read.
- Forecast. The noise forecast is a curve over the HOM band at the retained read's g2, transmittance and dark counts,
  anchored at HOM_PREFERRED; the plan read at submission picks the point and its offset from HOM_PREFERRED is a
  reported covariate.

--check rebuilds both jobs in memory and compares them with the retained files and checks the budgets, the seed
plan, the time and credit bounds and the design comparison. --read retains the live processor record, --estimate
Perceval's shot estimate at a probe budget (both read-only platform calls), --build writes both jobs, --forecast
recomputes forecast.json, --preflight JOB plans read-only and retains the admission, --submit JOB submits once under
--approval, and --analyze OUT.json RUN RUN pools the collected runs.

Usage:
  "$PYTHON" scripts/ascella_cz_tomography_reference_case.py [--check | --read | --estimate | --build | --forecast]
  "$PYTHON" scripts/ascella_cz_tomography_reference_case.py --preflight JOB [--after RUN]
  "$PYTHON" scripts/ascella_cz_tomography_reference_case.py --submit JOB --approval TEXT [--after RUN]
  "$PYTHON" scripts/ascella_cz_tomography_reference_case.py --analyze OUT.json RUN RUN
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import tempfile
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ascella_cz_tomography_case as tomo  # noqa: E402
import billing_rule_v2  # noqa: E402
import qd_platform  # noqa: E402
from qd_schedule import body_digest  # noqa: E402

from parallel import ordered_map  # noqa: E402

PLATFORM = tomo.PLATFORM
FAMILY = "ascella_cz_tomography_reference"
FAMILY_DIR = ROOT / "results/quandela/cases" / FAMILY
DESIGN = "docs/design/ascella-cz-tomography-reference-case.md"
READ = "platform-read/ascella-perfs.json"
ESTIMATE = "shot-estimate.json"
FORECAST = "forecast.json"
JOBS = tomo.JOBS
# The ANU QRNG draw whose values seed every compilation, the bootstrap and every forecast dataset; the manifests name
# it without an index and so own it whole (ci/seed_provenance.py).
DRAW = "docs/evidence/anu_qrng/draw-2026-11-09T020604Z.json"
SEED_RULE = (
    "nonzero draw values in index order, repeats skipped; 144 compilation seeds in schedule order, then the "
    "bootstrap seed, then one seed per forecast HOM point"
)
# One shot cap for every iteration: the bill of an iterated job is 1 credit plus 1e-6 per shot up to the largest
# iteration's max_shots (docs/runbooks/quandela-credit-optimization.md). The owner chose (2026-11-09) the largest cap
# whose every-iteration-at-cap worst case fits max_duration at the retained read's transmittance, 2.567 credits per job.
SHOT_CAP = 1_567_000
PROBE_SAMPLES = 4000
PROBE_SHOTS = 2_000_000
SAMPLE_QUANTUM = 100
PER_JOB_CREDITS = tomo.PER_JOB_CREDITS
PRICE_PER_SHOT = tomo.PRICE_PER_SHOT
MAX_DURATION = tomo.MAX_DURATION
# The submitted retained tomography jobs: their recorded duration over their iterations is the seconds one template
# iteration takes, compilation and its 4000-sample acquisition together.
TOMOGRAPHY_RUNS = (
    "results/quandela/runs/2026-10-31T050944Z-qpu_ascella-ascella_cz_tomography-job-00",
    "results/quandela/runs/2026-10-31T050944Z-qpu_ascella-ascella_cz_tomography-job-01",
)
SUBMIT_STATUSES = ("available", "running")
SUBMIT_WRAPPER = "scripts/ascella_cz_tomography_reference_case.py --submit"
IDLE_COUNTERS = ("num_concurrent_jobs", "num_jobs_in_queue", "num_running_qt_jobs")
RUNS_DIR = ROOT / "results/quandela/runs"
# Attempts of one job the stopping rule admits: the first, and one resubmission after a terminal error that returned
# no counted iteration.
MAX_ATTEMPTS = 2
# The admitted HOM band in percent (owner ruling of 2026-11-09): preferred HOM_PREFERRED, admitted within
# HOM_BAND_POINTS percentage points of it, both ends inclusive. Perceval's estimate_required_shots simulates at
# indistinguishability 1 and g2 0 (perceval.runtime.remote_computer._estimate_sample_probability); two photons bunch
# into mode k with probability (1 + M) |U_k1|^2 |U_k2|^2 at photon overlap M, so the two-click probability falls as M
# rises and the estimate at M = 1 bounds the shots per sample at every HOM in the band.
HOM_PREFERRED = qd_platform.HOM_FLOOR
HOM_BAND_POINTS = 6.8420696
HOM_BAND = (round(HOM_PREFERRED - HOM_BAND_POINTS, 7), round(HOM_PREFERRED + HOM_BAND_POINTS, 7))
# HOM points of the forecast curve, in percent: the band's ends, the retained tomography's 87.56 and HOM_PREFERRED.
FORECAST_HOMS = (83.1579304, 84.5, 86.0, 87.56, 88.5, 89.25, 90.0, 91.0, 92.5, 94.0, 95.5, 96.8420696)
FORECAST_RECORD_VARIANT = "source, loss and dark counts"
FORECAST_CURVE_VARIANTS = ("indistinguishability only", FORECAST_RECORD_VARIANT)
TOLERANCE = tomo.TOLERANCE
# Preregistered conjectures the pooled pair tests, each against the analysis' 95 % bootstrap interval
# (tomo.INTERVAL_KIND). M is the photon overlap; V and g2 are the plan reads of job-00 and job-01, averaged, in units.
CONJECTURES = (
    {
        "id": "overlap-only-law",
        "statement": "overlap is the only error: F_pro = (1 + M) / (2 (2 - M)) with M = V",
        "falsified_when": "the process-fidelity interval excludes the law at M = V",
    },
    {
        "id": "g2-corrected-overlap-law",
        "statement": "the same law with the multiphoton-corrected overlap M = min(1, (V + g2) / (1 - g2))",
        "falsified_when": "the process-fidelity interval excludes the law at the corrected M",
    },
    {
        "id": "noise-model-record-variant",
        "statement": "the retained noise pipeline's record variant (source, loss and dark counts) at the plan reads",
        "falsified_when": "the process-fidelity interval excludes the variant's estimand",
    },
    {
        "id": "noise-model-g2-corrected-variant",
        "statement": "the retained noise pipeline's g2-corrected overlap variant at the plan reads",
        "falsified_when": "the process-fidelity interval excludes the variant's estimand",
    },
    {
        "id": "rail-ratio-reads-hom",
        "statement": "the rail overlap inverted through the record noise model at the plan reads equals the "
        "platform's HOM V",
        "falsified_when": "the interval of the record-model M_R excludes V",
    },
    {
        "id": "two-overlaps-agree",
        "statement": "overlap-only closure: M_F = (4 F - 1) / (2 F + 1) equals M_R = (5 - D) / 4",
        "falsified_when": "the interval of M_F - M_R on the joint replicates excludes 0",
    },
    {
        "id": "record-overlaps-agree",
        "statement": "record-model closure: the overlaps that the record noise model at the plan reads assigns to the "
        "measured F and to the measured D agree, so one overlap explains both once g2, loss and dark counts enter",
        "falsified_when": "the interval of the record-model M_F - M_R on the joint replicates excludes 0",
    },
    {
        "id": "noise-model-ceiling",
        "statement": "no overlap beats M = 1: F stays at or below the record variant at HOM 100 % with the plan's g2, "
        "transmittance and dark counts",
        "falsified_when": "the lower end of the process-fidelity interval exceeds the ceiling",
    },
    {
        "id": "control-ratio-lossless",
        "statement": "r(11) / r(01) = 1: the two inputs whose photons never meet succeed equally on balanced rails",
        "falsified_when": "the interval of r(11) / r(01) excludes 1",
    },
    {
        "id": "control-ratio-noise-model",
        "statement": "r(11) / r(01) takes the record variant's value at the plan reads (multiphoton lost-twin events)",
        "falsified_when": "the interval of r(11) / r(01) excludes the record variant's ratio",
    },
    {
        "id": "scatter-matches-acquisition-law",
        "statement": "model check: the counts scatter about one Choi matrix as the acquisition law draws them",
        "falsified_when": "the Pearson statistic exceeds the 97.5th percentile of its acquisition reference",
    },
    {
        "id": "overdispersion-constant-factor",
        "statement": "the scatter beyond Poisson is a constant variance factor: the overdispersion ratio equals the "
        "retained pair's",
        "falsified_when": "the observed ratio lies more than 25 % from the retained pair's ratio",
    },
    {
        "id": "overdispersion-relative-systematic",
        "statement": "the scatter beyond Poisson is a relative systematic per rate fixed by the retained pair, so the "
        "ratio minus one grows with the mean eligible events per rate",
        "falsified_when": "the observed ratio lies more than 25 % from 1 + (retained ratio - 1) e / e_retained, e the "
        "mean eligible events per rate",
    },
)


def require(condition: bool, message: str) -> None:
    """Raise RuntimeError(message) unless condition holds; python -O keeps the check."""
    if not condition:
        raise RuntimeError(message)


# ---------------------------------------------------------------- seeds


def draw_values() -> list[int]:
    record = json.loads((ROOT / DRAW).read_text(encoding="utf-8"))
    values = record["values"]
    require(isinstance(values, list) and all(type(v) is int for v in values), f"{DRAW} holds no integer values")
    return list(values)


def usable_draw() -> list[tuple[int, int]]:
    """(index, value) of the draw's usable values in index order: nonzero, not yet taken."""
    taken: set[int] = set()
    usable = []
    for index, value in enumerate(draw_values()):
        if value == 0 or value in taken:
            continue
        taken.add(value)
        usable.append((index, value))
    return usable


def seed_plan() -> dict[str, Any]:
    """(index, value) of the 144 compilation seeds in schedule order, the bootstrap seed and the forecast seeds."""
    usable = usable_draw()
    count = len(tomo.schedule())
    need = count + 1 + len(FORECAST_HOMS) + 1
    require(len(usable) >= need, f"{DRAW} holds {len(usable)} usable values, not {need}")
    return {
        "compilation": usable[:count],
        "bootstrap": usable[count],
        "forecast": usable[count + 1 : need - 1],
        "overdispersion": usable[need - 1],
    }


# ---------------------------------------------------------------- platform reads


def read_perfs() -> dict[str, Any]:
    perfs: dict[str, Any] = json.loads((FAMILY_DIR / READ).read_text(encoding="utf-8"))["perfs"]
    return perfs


def platform_read() -> int:
    """Retain the live processor record's status, perfs and limits (a read-only platform call)."""
    processor = qd_platform.get(qd_platform.platform_route(PLATFORM))
    specs = processor.get("specs") or {}
    record = {
        "schema": "qd-cz-tomography-reference-platform-read-v1",
        "retrieved_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "status": processor.get("status"),
        "perfs": qd_platform.scrub(processor.get("perfs") or {}),
        "connected_input_modes": specs.get("connected_input_modes"),
        "constraints": specs.get("constraints"),
    }
    path = FAMILY_DIR / READ
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{PLATFORM}: {record['status']}, perfs {record['perfs']}")
    return 0


def iteration_seconds() -> float:
    """The largest recorded duration per iteration of the retained tomography runs (results.json status.duration)."""
    per = []
    for run in TOMOGRAPHY_RUNS:
        results = json.loads((ROOT / run / "results.json").read_text(encoding="utf-8"))
        duration, iterations = results["status"]["duration"], len(results["iterations"])
        require(isinstance(duration, int | float) and iterations > 0, f"{run}: no duration over iterations")
        per.append(duration / iterations)
    return max(per)


def shot_rate(perfs: Mapping[str, Any]) -> float:
    """Shots per second: the clock times the chance of at least one click from two photons, 1 - (1 - T)^2 (a shot is a
    detection event of at least one photon, docs/runbooks/quandela-credit-optimization.md)."""
    t = perfs["Transmittance (%)"] / 100.0
    return float(perfs["Clock (MHz)"]) * 1e6 * (1.0 - (1.0 - t) ** 2)


# ---------------------------------------------------------------- budgets


def probe_documents(job: str) -> dict[str, bytes]:
    """The job at PROBE_SAMPLES samples and PROBE_SHOTS shots per iteration, the budget the shot estimate reads."""
    return documents(job, {row["name"]: (PROBE_SAMPLES, PROBE_SHOTS) for row in tomo.job_rows(job)}, probe=True)


def shot_estimate(job: str) -> dict[str, Any]:
    """Perceval's estimate_required_shots for every setting of job at PROBE_SAMPLES under the live perfs, recorded
    while qd_platform.payload builds the probe body in a scratch directory (read-only: nothing is sent)."""
    from perceval import RemoteComputer

    recorded: list[int | None] = []
    original = RemoteComputer.estimate_required_shots

    def record(self: Any, computation: Any, nsamples: int, param_values: dict[str, float] | None = None) -> Any:
        value = original(self, computation, nsamples, param_values)
        require(nsamples == PROBE_SAMPLES, f"an estimate read {nsamples} samples, not {PROBE_SAMPLES}")
        recorded.append(value)
        return value

    with tempfile.TemporaryDirectory() as scratch:
        case = Path(scratch) / job
        case.mkdir()
        for name, data in probe_documents(job).items():
            (case / name).write_bytes(data)
        manifest, circuit, _ = qd_platform.load_case(case)
        RemoteComputer.estimate_required_shots = record
        try:
            built = qd_platform.payload(case, manifest, circuit, PLATFORM)
        finally:
            RemoteComputer.estimate_required_shots = original
    require(len(recorded) == len(manifest["settings"]), f"{len(recorded)} estimates were recorded")
    require(all(value is not None for value in recorded), "Perceval estimates no sample of interest")
    return {
        "samples": PROBE_SAMPLES,
        "perfs": built.get("estimate_perfs"),
        "inputs": {s["name"]: int(v) for s, v in zip(manifest["settings"], recorded, strict=True) if v is not None},
    }


def estimate_command() -> int:
    jobs = {job: shot_estimate(job) for job in JOBS}
    record = {
        "schema": "qd-cz-tomography-reference-shot-estimate-v1",
        "basis": "RemoteComputer.estimate_required_shots under the live perfs of qpu:ascella, per iteration, at the "
        "probe budget",
        "jobs": jobs,
    }
    (FAMILY_DIR / ESTIMATE).write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    for job, row in jobs.items():
        print(f"{job}: {PROBE_SAMPLES} samples need {min(row['inputs'].values())} to {max(row['inputs'].values())}")
    return 0


def retained_estimate() -> dict[str, Any]:
    estimate: dict[str, Any] = json.loads((FAMILY_DIR / ESTIMATE).read_text(encoding="utf-8"))
    return estimate


def samples_for(estimated_shots: int) -> int:
    """The largest multiple of SAMPLE_QUANTUM whose shots, scaled from the probe estimate and times tomo.SHOT_MARGIN,
    stay within SHOT_CAP."""
    per_sample = estimated_shots / PROBE_SAMPLES
    samples = int(SHOT_CAP / (tomo.SHOT_MARGIN * per_sample) // SAMPLE_QUANTUM) * SAMPLE_QUANTUM
    require(samples >= SAMPLE_QUANTUM, f"{estimated_shots} probe shots leave no sample within {SHOT_CAP}")
    return samples


def budgets(job: str) -> dict[str, tuple[int, int]]:
    """(max_samples, max_shots) of every setting of job: its own samples under the shared SHOT_CAP."""
    inputs = retained_estimate()["jobs"][job]["inputs"]
    return {row["name"]: (samples_for(inputs[row["name"]]), SHOT_CAP) for row in tomo.job_rows(job)}


def worst_case_seconds(job: str, perfs: Mapping[str, Any]) -> float:
    """Every iteration at its max_shots: the iterations' recorded seconds plus the summed caps at the shot rate."""
    caps = sum(shots for _, shots in budgets(job).values())
    return len(tomo.job_rows(job)) * iteration_seconds() + caps / shot_rate(perfs)


def transmittance_floor(job: str, clock_mhz: float) -> float:
    """The transmittance in percent below which every iteration at its cap would pass MAX_DURATION:
    1 - sqrt(1 - R / clock), with R the summed caps over the seconds the iterations leave."""
    caps = sum(shots for _, shots in budgets(job).values())
    spare = MAX_DURATION - len(tomo.job_rows(job)) * iteration_seconds()
    require(spare > 0, f"{job}: {len(tomo.job_rows(job))} iterations leave no seconds for shots")
    needed = caps / spare / (clock_mhz * 1e6)
    require(needed < 1, f"{job}: the caps need more than one click per clock cycle")
    return 100.0 * (1.0 - math.sqrt(1.0 - needed))


def expected_seconds(job: str) -> int:
    """The seconds a job is expected to take at the retained read: the recorded iteration seconds plus the shots the
    samples need (the cap over tomo.SHOT_MARGIN), rounded up."""
    caps = sum(shots for _, shots in budgets(job).values())
    perfs = read_perfs()
    return math.ceil(len(tomo.job_rows(job)) * iteration_seconds() + caps / tomo.SHOT_MARGIN / shot_rate(perfs))


def credit_ceiling() -> float:
    return round(PER_JOB_CREDITS + PRICE_PER_SHOT * SHOT_CAP, 6)


# ---------------------------------------------------------------- request


def request_parts(
    job: str, budget: Mapping[str, tuple[int, int]]
) -> tuple[list[dict[str, Any]], dict[str, Any], list[int]]:
    """The manifest settings of a job with their budgets, the one template circuit they share and the draw index of
    each compilation seed. The window is chip modes 0..5 with the photons on modes 0 and 2 (tomo.SOURCES), the
    retained case's window: the compared estimand keeps it whatever the live dark counts select."""
    seeds = seed_plan()["compilation"]
    rows = tomo.job_rows(job)
    items = [(position, row, seeds[row["schedule_index"]][1]) for position, row in enumerate(rows)]
    built = ordered_map(tomo.build_setting, items, min_items=1)
    template = built[0][0]
    for position, (mesh, _) in enumerate(built):
        require(mesh == template, f"setting {position} needs another mesh than setting 0")
    circuit = {**template, "modes": tomo.MODES, "input_state": tomo.source_state()}
    settings = []
    for _, setting in built:
        samples, shots = budget[setting["name"]]
        settings.append({**setting, "max_samples": samples, "max_shots": shots})
    return settings, circuit, [seeds[row["schedule_index"]][0] for row in rows]


def submission_policy(job: str) -> dict[str, Any]:
    clock = float(read_perfs()["Clock (MHz)"])
    return {
        "platform": PLATFORM,
        "credit_ceiling": credit_ceiling(),
        "per_job_credits": PER_JOB_CREDITS,
        "expected_seconds": expected_seconds(job),
        "hom_percent": {
            "preferred": HOM_PREFERRED,
            "band_points": HOM_BAND_POINTS,
            "at_least": HOM_BAND[0],
            "at_most": HOM_BAND[1],
            "applies_to": f"both jobs; {JOBS[1]} also stays within the pooling tolerances of {JOBS[0]}'s read",
        },
        "transmittance_percent": {
            "at_least": math.ceil(transmittance_floor(job, clock) * 1e4) / 1e4,
            "rule": f"every iteration at its max_shots stays within max_duration {MAX_DURATION} s at clock "
            f"{clock:g} MHz, iterations taking the retained tomography's recorded seconds",
        },
        "statuses": "Explorer row and processor read available or running, while the token counts no running, no "
        "queued and no running quantum-task job",
        "live_read": "the shot estimate and a processor read inside the submit lock, after the plan, carry the "
        f"plan's perfs and connect source modes {list(tomo.SOURCES)}",
        "after": None
        if job == JOBS[0]
        else {
            "job": JOBS[0],
            "requires": f"a collected run of {JOBS[0]} that completed with every one of its "
            f"{len(tomo.job_rows(JOBS[0]))} iterations counted, and a plan inside the pooling tolerances against it: "
            f"HOM within {tomo.POOL_HOM_TOLERANCE:g} point, transmittance within {tomo.POOL_T_TOLERANCE:g} point, "
            f"at most {tomo.POOL_MAX_GAP_HOURS:g} h after its submission",
        },
    }


def preregistered() -> dict[str, Any]:
    plan = seed_plan()
    return {
        "estimator": "scripts/ascella_cz_tomography_case.py: linear inversion of the 144 x 4 absolute outcome rates "
        "(eligible events over the iteration's nb_shots_used) onto the 16 x 16 Choi matrix, F_pro = <Phi_CZ| J "
        "|Phi_CZ> / (4 Tr J) of the unprojected fit, F_avg = (4 F_pro + 1) / 5",
        "bootstrap": {
            "replicates": tomo.BOOTSTRAP_REPLICATES,
            "level": tomo.BOOTSTRAP_LEVEL,
            "kind": "the parametric resample of tomo.resampled_rates; the " + tomo.INTERVAL_KIND + " interval, the "
            "type the retained case's coverage study chose",
            "seed_draw": DRAW,
            "seed_index": plan["bootstrap"][0],
        },
        "binding": "each returned iteration binds to the setting that has its echoed compilation_seed, one to one; "
        "each run's cases.json must equal the retained case byte for byte and the two runs must be distinct jobs; "
        "an entry that is missing, malformed or an error is counted and skipped",
        "pooling": {
            "rule": "tomo.pooling: the rates of job-01 are multiplied by g(T_job-00) / g(T_job-01) with g(T) = "
            "T / (2 - T), T read from each run's perfs_at_plan",
            "decided_when": {
                "hom_percentage_points": tomo.POOL_HOM_TOLERANCE,
                "transmittance_percentage_points": tomo.POOL_T_TOLERANCE,
                "max_gap_hours_between_submissions": tomo.POOL_MAX_GAP_HOURS,
            },
            "otherwise": "the pooled estimate is reported as descriptive",
            "incomplete": "a missing setting, or a run that is not both jobs, leaves the estimate undecided",
        },
        "reference_role": "the process tomography that the CZ compilation ensemble compares with "
        "(scripts/ascella_cz_ensemble_case.py TOMOGRAPHY_RUNS) once its pool is decided",
        "hom_comparison": "the change in process fidelity against the retained 2026-10-31 tomography at HOM 87.56 %, "
        "descriptive: two calibrations with other figures moving",
        "interpretation": "service-compiled average postselected CZ; preparation, readout and gate errors are not "
        "separable because every setting compiles to its own mesh",
        "hom_band": {
            "preferred": HOM_PREFERRED,
            "band_points": HOM_BAND_POINTS,
            "covariate": "each job's plan HOM minus the preferred HOM, reported beside every estimate",
        },
        "overlap_estimators": {
            "from_fidelity": "M_F = (4 F - 1) / (2 F + 1), the inverse of F_pro = (1 + M) / (2 (2 - M))",
            "from_rail_rates": "M_R = (5 - D) / 4, D = r(10) r(01) / (r(00) r(11)), r(xy) the absolute eligible rate "
            "of input xy summed over its four outcomes and averaged over all nine readout bases, after pooling",
            "record_model": "the same two quantities inverted through the record noise variant at the plan reads: "
            "F(M) and D(M) evaluated at overlaps 0.70 to 1.00 in steps of 0.0375, F fitted linear-fractional and D "
            "quadratic, each inverted by monotone interpolation on 3001 points",
            "bootstrap": "all on the replicates of the primary bootstrap, so each difference has a joint interval",
        },
        "plan_reads": "V, g2 and transmittance are the means of the two jobs' perfs_at_plan; dark counts and clock "
        "come from job-00's perfs_at_plan; the noise pipeline runs at those reads",
        "conjectures": [dict(row) for row in CONJECTURES],
        "verdict_rule": "every interval is the primary bootstrap's 95 % interval; a conjecture is falsified when its "
        "band excludes its prediction (or, for the two overdispersion conjectures, the observed ratio), and survives "
        "otherwise; the model check scatter-matches-acquisition-law decides first, and when it is falsified every "
        "other verdict is reported as conditional on that failure; a descriptive pool reports each verdict as "
        "descriptive",
        "overdispersion": {
            "statistic": "Pearson chi-squared of the 576 eligible counts about the counts of the unweighted "
            "linear-inversion fit, each over its expected count, one event at least",
            "reference": f"{OVERDISPERSION_DRAWS} synthetic pairs drawn under the fit as the service acquires them: "
            "each setting stops at its observed sample count, its eligible outcomes are one multinomial over that "
            "quota at the fit's rates per shot over the observed samples per shot (negative predictions set to 0), "
            "its shots are the quota plus a negative-binomial count, and each pair is refit and scored like the data",
            "ratio": "the observed statistic over the reference mean",
            "seed_draw": DRAW,
            "seed_index": plan["overdispersion"][0],
        },
    }


def documents(job: str, budget: Mapping[str, tuple[int, int]] | None = None, probe: bool = False) -> dict[str, bytes]:
    """The job's cases.json and circuit.json; a probe carries the given budgets and no submission policy, which the
    shot estimate it serves determines."""
    budget = budgets(job) if budget is None else budget
    settings, circuit, indices = request_parts(job, budget)
    circuit_bytes = (json.dumps(circuit, indent=1) + "\n").encode()
    manifest = {
        "schema": "qd-hypercomplex-cases-v1",
        "family": FAMILY,
        "job": job,
        "platforms": [PLATFORM],
        "command": "sample_count",
        "gate_form": "template",
        "iterations": len(settings),
        "min_detected_photons": tomo.MIN_CLICKS,
        "max_samples": sum(s["max_samples"] for s in settings),
        "max_shots": sum(s["max_shots"] for s in settings),
        "max_duration": MAX_DURATION,
        "max_credits": round(PER_JOB_CREDITS + PRICE_PER_SHOT * max(s["max_shots"] for s in settings), 6),
        "mitigations": [],
        "output_modes": tomo.MODES,
        "logical_modes": list(range(tomo.WINDOW)),
        "layout": {"logical": ["c0", "c1", "t0", "t1", "h0", "h1"], "chip_modes": list(range(tomo.WINDOW))},
        "eligibility": "exactly two threshold clicks across all twelve returned modes, one on a control rail "
        "(modes 0, 1) and one on a target rail (modes 2, 3)",
        "outcomes": {"order": ["00", "01", "10", "11"], "meaning": "control rail then target rail of the click"},
        "design": DESIGN,
        "settings": settings,
        "circuit": {"file": "circuit.json", "sha256": qd_platform.sha256_bytes(circuit_bytes)},
        "compilation_seeds": {"draw": DRAW, "indices": indices, "rule": SEED_RULE},
        "budgets": {
            "shot_cap": SHOT_CAP,
            "rule": f"every iteration's max_shots is {SHOT_CAP}; its max_samples is the largest multiple of "
            f"{SAMPLE_QUANTUM} whose shots, scaled from Perceval's estimate at {PROBE_SAMPLES} samples "
            f"({ESTIMATE}) and times {tomo.SHOT_MARGIN}, stay within it",
        },
        "billing": billing_rule_v2.RULE,
        "preregistered": preregistered(),
    }
    if not probe:
        manifest["submit_wrapper"] = SUBMIT_WRAPPER
        manifest["submission_policy"] = submission_policy(job)
    return {"cases.json": (json.dumps(manifest, indent=1) + "\n").encode(), "circuit.json": circuit_bytes}


def build() -> int:
    for job in JOBS:
        out = FAMILY_DIR / job
        out.mkdir(parents=True, exist_ok=True)
        for name, data in documents(job).items():
            (out / name).write_bytes(data)
    return 0


# ---------------------------------------------------------------- forecast and design comparison


def fidelity_sd(arrays: Mapping[str, np.ndarray], shots: np.ndarray) -> float:
    """The delta-method standard deviation of the unprojected process fidelity when setting s spends shots[s] shots.

    Each shot of setting s falls into one of its four eligible outcomes with probability r_s (eligible events per
    shot) or into the rest, so the rate estimate has covariance (diag(r_s) - r_s r_s^T) / shots[s]; F = (r . a) /
    (r . b) has gradient (a - F b) / (r . b) (tomo.fidelity_functionals)."""
    numerator, denominator = tomo.fidelity_functionals()
    rates = tomo.exact_rates(arrays).reshape(-1, 4)
    flat = rates.reshape(-1)
    fidelity = float(flat @ numerator / (flat @ denominator))
    gradient = ((numerator - fidelity * denominator) / (flat @ denominator)).reshape(-1, 4)
    variance = 0.0
    for s in range(rates.shape[0]):
        covariance = (np.diag(rates[s]) - np.outer(rates[s], rates[s])) / shots[s]
        variance += float(gradient[s] @ covariance @ gradient[s])
    return math.sqrt(variance)


def design_shots(arrays: Mapping[str, np.ndarray], samples: np.ndarray) -> np.ndarray:
    """The expected shots each setting spends to collect its samples: samples times any-click over sample
    probability."""
    return np.asarray(samples * arrays["any"] / arrays["samples"])


def design_samples() -> np.ndarray:
    """This case's max_samples of every setting in schedule order."""
    by_name = {name: samples for job in JOBS for name, (samples, _) in budgets(job).items()}
    return np.asarray([by_name[row["name"]] for row in tomo.schedule()], dtype=float)


def sampled_dataset(
    arrays: Mapping[str, np.ndarray], quotas: np.ndarray, generator: np.random.Generator
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """One synthetic run as tomo.sampled_dataset draws it, with setting s stopping at quotas[s] samples."""
    eligible = np.empty((len(quotas), 4), dtype=int)
    shots = np.empty(len(quotas), dtype=int)
    for s, quota in enumerate(int(q) for q in quotas):
        within = arrays["eligible"][s] / arrays["samples"][s]
        draw = generator.multinomial(quota, np.append(within, 1.0 - within.sum()))
        eligible[s] = draw[:4]
        shots[s] = quota + generator.negative_binomial(quota, arrays["samples"][s] / arrays["any"][s])
    return eligible, quotas.astype(int), shots


def forecast_point(item: tuple[float, list[dict[str, Any]], int]) -> dict[str, Any]:
    """The forecast at one HOM from its 144 setting forecasts in schedule order: per curve variant the estimand, and
    for the record variant the delta-method spread of this design and of the retained uniform 4000-sample design, and
    one synthetic dataset of this design analyzed as a run would be."""
    hom, per_setting, seed = item
    rows = tomo.schedule()
    out: dict[str, Any] = {"hom_percent": hom, "seed": seed}
    for name in FORECAST_CURVE_VARIANTS:
        arrays = tomo.variant_arrays(per_setting, name)
        estimand = tomo.estimate_rates(tomo.exact_rates(arrays))
        out[name] = {
            "estimand_process_fidelity": estimand["process_fidelity"],
            "estimand_average_gate_fidelity": estimand["average_gate_fidelity"],
        }
    arrays = tomo.variant_arrays(per_setting, FORECAST_RECORD_VARIANT)
    samples = design_samples()
    uniform = np.full(len(rows), float(tomo.SAMPLES_PER_ITERATION))
    shots = design_shots(arrays, samples)
    out["design"] = {
        "process_fidelity_sd": fidelity_sd(arrays, shots),
        "retained_uniform_design_process_fidelity_sd": fidelity_sd(arrays, design_shots(arrays, uniform)),
        "expected_shots_by_job": {
            job: float(sum(shots[row["schedule_index"]] for row in tomo.job_rows(job))) for job in JOBS
        },
        "largest_expected_shots": float(shots.max()),
        "expected_eligible_events": float((samples[:, None] * arrays["eligible"] / arrays["samples"][:, None]).sum()),
    }
    sampling, resampling = tomo.dataset_streams(seed)
    eligible, quotas, drawn = sampled_dataset(arrays, samples, sampling)
    sampled = tomo.tomography(eligible, quotas.astype(float), drawn.astype(float), np.ones(len(rows)), resampling)
    out["sampled_dataset"] = {key: sampled[key] for key in tomo.SAMPLED_KEYS}
    return out


def forecast() -> dict[str, Any]:
    perfs = read_perfs()
    figures = tomo.perf_figures(perfs)
    dark = [float(rate) for rate in perfs["Dark counts (detection/s)"]]
    seeds = seed_plan()["forecast"]
    rows = tomo.schedule()
    # Every (HOM, setting) forecast is independent, so one flat map carries all of them before the per-point summaries.
    tasks = [(row, {**figures, "hom": hom / 100.0}, dark) for hom in FORECAST_HOMS for row in rows]
    flat = ordered_map(tomo.forecast_setting, tasks, min_items=1)
    chunks = [flat[k * len(rows) : (k + 1) * len(rows)] for k in range(len(FORECAST_HOMS))]
    items = [(hom, chunk, value) for hom, chunk, (_, value) in zip(FORECAST_HOMS, chunks, seeds, strict=True)]
    points = ordered_map(forecast_point, items, min_items=1)
    for point, (index, _) in zip(points, seeds, strict=True):
        point["seed_index"] = index
        del point["seed"]
    return {
        "schema": "qd-cz-tomography-reference-forecast-v1",
        "read": {"path": READ, "sha256": qd_platform.sha256_bytes((FAMILY_DIR / READ).read_bytes()), **figures},
        "basis": "the retained read's g2, transmittance, clock and dark counts at each HOM of the curve across the "
        "admitted band; the plan read at submission picks the point",
        "record_variant": FORECAST_RECORD_VARIANT,
        "seed_draw": DRAW,
        "interval": tomo.INTERVAL_KIND,
        "points": points,
    }


def forecast_bytes() -> bytes:
    return (json.dumps(forecast(), indent=1, sort_keys=True) + "\n").encode()


def check_forecast() -> int:
    retained = json.loads((FAMILY_DIR / FORECAST).read_text(encoding="utf-8"))
    difference = tomo.first_difference(retained, json.loads(forecast_bytes()))
    require(difference is None, f"forecast.json differs from the recomputation at {difference}")
    print(f"{FAMILY}: forecast.json recomputes")
    return 0


# ---------------------------------------------------------------- checks


def check_job(job: str, rebuild: bool = True) -> None:
    """The retained request's budgets, bounds and identity; with rebuild, also its byte-for-byte rebuild, whose
    decomposed mesh floats follow the CPU's numeric path, so the on-demand gate core-record-check-07 runs it on the
    build host (ci/gates.json)."""
    if rebuild:
        retained = {name: (FAMILY_DIR / job / name).read_bytes() for name in ("cases.json", "circuit.json")}
        require(documents(job) == retained, f"{job}: the retained request differs from the rebuild")
    manifest, circuit, _ = qd_platform.load_case(FAMILY_DIR / job)
    require(qd_platform.iteration_form(manifest) == "template", f"{job}: not a template case")
    steps = qd_platform.iteration_budgets(manifest)
    require({shots for _, shots in steps} == {SHOT_CAP}, f"{job}: an iteration's max_shots is not {SHOT_CAP}")
    inputs = retained_estimate()["jobs"][job]["inputs"]
    for setting, (samples, shots) in zip(manifest["settings"], steps, strict=True):
        scaled = inputs[setting["name"]] * samples / PROBE_SAMPLES
        require(scaled * tomo.SHOT_MARGIN <= shots, f"{job}/{setting['name']}: {scaled:.0f} shots over the margin")
        require(samples % SAMPLE_QUANTUM == 0, f"{job}/{setting['name']}: {samples} samples off the quantum")
        bigger = (samples + SAMPLE_QUANTUM) * inputs[setting["name"]] / PROBE_SAMPLES * tomo.SHOT_MARGIN
        require(bigger > shots, f"{job}/{setting['name']}: {samples} samples leave a quantum unspent")
    worst = worst_case_seconds(job, read_perfs())
    require(worst <= MAX_DURATION, f"{job}: every iteration at its cap takes {worst:.0f} s")
    require(manifest["max_credits"] == credit_ceiling(), f"{job}: max_credits {manifest['max_credits']}")
    names = {row["name"] for row in tomo.job_rows(job)}
    require({s["name"] for s in manifest["settings"]} == names, f"{job}: the settings are not its parity half")
    require(circuit["input_state"] == tomo.source_state(), f"{job}: the photons do not enter modes {tomo.SOURCES}")


def check() -> int:
    plan = seed_plan()
    values = [
        value for _, value in [*plan["compilation"], plan["bootstrap"], *plan["forecast"], plan["overdispersion"]]
    ]
    require(len(set(values)) == len(values), "a seed value repeats")
    retained_seeds = {value for _, value in tomo.seed_plan()[0]}
    require(not retained_seeds & set(values), "a compilation seed repeats one of the retained case's")
    estimate = retained_estimate()
    for job in JOBS:
        require(estimate["jobs"][job]["perfs"] == read_perfs(), f"{job}: the shot estimate read other perfs")
        check_job(job)
    require(
        json.loads((FAMILY_DIR / FORECAST).read_text(encoding="utf-8"))["read"]["sha256"]
        == qd_platform.sha256_bytes((FAMILY_DIR / READ).read_bytes()),
        "forecast.json was computed from another read",
    )
    for point in json.loads((FAMILY_DIR / FORECAST).read_text(encoding="utf-8"))["points"]:
        design = point["design"]
        require(
            design["process_fidelity_sd"] < design["retained_uniform_design_process_fidelity_sd"],
            f"HOM {point['hom_percent']}: the design does not narrow the retained design's spread",
        )
    retained = json.loads((FAMILY_DIR / RETAINED_VERDICTS).read_text(encoding="utf-8"))
    difference = tomo.first_difference(retained, json.loads(json.dumps(retained_verdicts())))
    require(difference is None, f"{RETAINED_VERDICTS} differs from the recomputation at {difference}")
    for job in JOBS:
        print(
            f"{job}: worst case {worst_case_seconds(job, read_perfs()):.1f} s, expected {expected_seconds(job)} s, "
            f"transmittance floor {transmittance_floor(job, float(read_perfs()['Clock (MHz)'])):.3f} %, "
            f"ceiling {credit_ceiling()} credits"
        )
    return 0


# ---------------------------------------------------------------- submission gate


def admit(
    job: str, planned: Mapping[str, Any], predecessor: Mapping[str, Any] | None, at: datetime | None = None
) -> None:
    """Refuse a fresh plan that leaves the job's submission policy, at time at (now when None); raises
    qd_platform.PlatformError."""
    try:
        policy = submission_policy(job)
        # qd_platform.plan names the case after its directory, a run directory at submission, so the request's
        # identity is its cases.json digest.
        retained = qd_platform.sha256_bytes((FAMILY_DIR / job / "cases.json").read_bytes())
        require(planned["platform"] == PLATFORM, f"{job}: the plan names platform {planned['platform']}")
        require(planned["cases_sha256"] == retained, f"{job}: the plan's cases.json is not the retained {job}")
        for key in ("credit_ceiling", "per_job_credits", "expected_seconds"):
            require(
                abs(float(planned[key]) - float(policy[key])) <= TOLERANCE,
                f"{job}: the plan's {key} {planned[key]!r} is not {policy[key]!r}",
            )
        perfs = planned.get("perfs_at_plan") or {}
        figures: dict[str, float] = {}
        for key in ("HOM (%)", "Transmittance (%)"):
            read = perfs.get(key)
            if isinstance(read, bool) or not isinstance(read, int | float) or not math.isfinite(read):
                raise RuntimeError(f"{job}: the plan reads {key} {read!r}")
            figures[key] = float(read)
        require(
            planned.get("perfs_at_estimate") == planned["perfs_at_plan"],
            f"{job}: the shot estimate read other processor perfs than the plan's",
        )
        hom = float(figures["HOM (%)"])
        low, high = HOM_BAND
        require(low <= hom <= high, f"{job}: HOM {hom:g} % is outside the admitted band {low:g} to {high:g} %")
        floor = float(policy["transmittance_percent"]["at_least"])
        t = float(figures["Transmittance (%)"])
        require(t >= floor, f"{job}: transmittance {t:g} % is below the {floor:g} % the caps need")
        clock = perfs.get("Clock (MHz)")
        if isinstance(clock, bool) or not isinstance(clock, int | float) or not math.isfinite(clock) or clock <= 0:
            raise RuntimeError(f"{job}: the plan reads Clock (MHz) {clock!r}")
        # The floor assumes the read's clock; the plan's own clock and transmittance bound the time.
        worst = worst_case_seconds(job, {"Clock (MHz)": float(clock), "Transmittance (%)": t})
        require(worst <= MAX_DURATION, f"{job}: every iteration at its cap takes {worst:.2f} s at the plan's figures")
        statuses = planned["status_at_plan"]
        require(all(statuses.get(k) in SUBMIT_STATUSES for k in ("explorer", "processor")), f"{job}: status {statuses}")
        counters = planned["availability_at_plan"]
        require(
            all(type(counters.get(key)) is int and counters[key] == 0 for key in IDLE_COUNTERS),
            f"{job}: this token holds jobs: {counters}",
        )
        if job != JOBS[0]:
            require(predecessor is not None, f"{job} requires the collected {JOBS[0]} run (--after RUN)")
            predecessor_complete(predecessor or {})
            poolable(job, figures, predecessor or {}, datetime.now(UTC) if at is None else at)
    except (RuntimeError, ValueError, KeyError, TypeError) as error:
        raise qd_platform.PlatformError(str(error)) from None


def poolable(job: str, figures: Mapping[str, float], predecessor: Mapping[str, Any], at: datetime) -> None:
    """Refuse a job-01 plan whose pool with the job-00 run would be undecided under tomo.pooling: HOM within
    tomo.POOL_HOM_TOLERANCE points, transmittance within tomo.POOL_T_TOLERANCE points, and at most
    tomo.POOL_MAX_GAP_HOURS since job-00's submission."""
    first = predecessor.get("perfs") or {}
    for key, tolerance in (("HOM (%)", tomo.POOL_HOM_TOLERANCE), ("Transmittance (%)", tomo.POOL_T_TOLERANCE)):
        difference = abs(figures[key] - float(first[key]))
        require(difference <= tolerance, f"{job}: {key} differs from {JOBS[0]}'s by {difference:g}, over {tolerance:g}")
    gap = (at - datetime.fromisoformat(predecessor["submitted_utc"])).total_seconds() / 3600.0
    require(
        0 <= gap <= tomo.POOL_MAX_GAP_HOURS, f"{job}: {gap:.2f} h after {JOBS[0]}, over {tomo.POOL_MAX_GAP_HOURS:g}"
    )


def load_run(run: Path) -> dict[str, Any]:
    """One collected run through tomo.load_run, with its terminal status and the settings that stopped short of their
    max_samples (an iteration ends at max_samples or max_shots, whichever comes first)."""
    loaded = tomo.load_run(run, FAMILY, FAMILY_DIR, JOBS)
    results = json.loads((run / "results.json").read_text(encoding="utf-8"))
    status = results.get("status")
    loaded["status"] = status.get("status") if isinstance(status, dict) else None
    quotas = {s["name"]: s["max_samples"] for s in json.loads((run / "cases.json").read_text())["settings"]}
    loaded["short"] = sorted(name for name, t in loaded["tallies"].items() if t["samples"] < quotas[name])
    return loaded


def prior_attempts(job: str, runs_dir: Path = RUNS_DIR) -> None:
    """Refuse a further attempt of job under the stopping rule: a posted attempt that is not collected, that returned a
    counted iteration or that ended other than in error ends the job's attempts, and so do MAX_ATTEMPTS posted
    attempts. A directory with no
    posting checkpoint (submission.json, submission-state.json or job-body.json) is no attempt."""
    posted = []
    for run in sorted(runs_dir.glob(f"*-{PLATFORM.replace(':', '_')}-{FAMILY}-{job}")):
        if not any((run / name).exists() for name in ("submission.json", "submission-state.json", "job-body.json")):
            continue
        state_path = run / "submission-state.json"
        if not (run / "submission.json").exists() and state_path.exists():
            # qd_platform.submit records phase "refused" when the service definitively rejected the POST: no job
            # exists, so the directory is an audit record and no attempt.
            if json.loads(state_path.read_text(encoding="utf-8")).get("phase") == "refused":
                continue
        posted.append(run)
        name = run.relative_to(runs_dir)
        require((run / "results.json").exists(), f"{job}: the earlier attempt {name} is not collected")
        results = json.loads((run / "results.json").read_text(encoding="utf-8"))
        counted = [e for e in results.get("iterations") or [] if isinstance(e, dict) and e.get("counts")]
        require(not counted, f"{job}: the earlier attempt {name} returned counts, so the job is never resubmitted")
        status = results.get("status")
        state = status.get("status") if isinstance(status, dict) else None
        require(state == "error", f"{job}: the earlier attempt {name} ended {state!r}; only an error admits a retry")
    require(len(posted) < MAX_ATTEMPTS, f"{job}: {len(posted)} attempts were posted, the most the stopping rule admits")


def predecessor_complete(loaded: Mapping[str, Any]) -> None:
    """Refuse unless a loaded job-00 run completed with every iteration counted."""
    count = len(tomo.job_rows(JOBS[0]))
    require(loaded["job"] == JOBS[0], f"the predecessor run is {loaded['job']}, not {JOBS[0]}")
    require(loaded["status"] == "completed", f"{JOBS[0]} reads {loaded['status']!r}, not completed")
    uncounted = sum(loaded["uncounted"].values())
    require(
        len(loaded["tallies"]) == count and uncounted == 0,
        f"{JOBS[0]} counted {len(loaded['tallies'])} of {count} iterations with {uncounted} uncounted",
    )
    short = loaded.get("short", [])
    require(not short, f"{JOBS[0]} stopped {len(short)} settings short of their max_samples: {short[:4]}")


def live_read(job: str, planned: Mapping[str, Any], processor: Mapping[str, Any]) -> None:
    """Refuse unless a processor read taken after the plan carries the plan's perfs and connects tomo.SOURCES."""
    perfs = qd_platform.scrub(processor.get("perfs") or {})
    require(perfs == planned["perfs_at_plan"], f"{job}: the processor perfs moved after the plan read")
    connected = (processor.get("specs") or {}).get("connected_input_modes") or []
    require(all(mode in connected for mode in tomo.SOURCES), f"{job}: modes {tomo.SOURCES} are not all in {connected}")


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def predecessor_record(loaded: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if loaded is None:
        return None
    return {"submitted_utc": loaded["submitted_utc"], "sha256": qd_platform.sha256_bytes(canonical(loaded))}


def bind_reviewed(job: str, planned: Mapping[str, Any], reviewed: Mapping[str, Any], predecessor: Any) -> None:
    """Refuse a fresh plan that differs from the admitted preflight the owner reviewed: its case digest, its body
    beyond the process_id Perceval draws afresh for every job, its processor perfs and the predecessor run."""
    require(
        (reviewed.get("admission") or {}).get("admitted") is True, f"{job}: the retained preflight was not admitted"
    )
    require(reviewed.get("cases_sha256") == planned["cases_sha256"], f"{job}: the case changed since the preflight")
    fresh, frozen = body_digest(planned["body"]), reviewed.get("body_sha256_without_process_id")
    require(fresh == frozen, f"{job}: the planned body {fresh} differs from the preflight's {frozen}")
    require(reviewed.get("perfs_at_plan") == planned["perfs_at_plan"], f"{job}: the perfs moved since the preflight")
    require(reviewed.get("predecessor") == predecessor, f"{job}: the predecessor differs from the preflight's")


def require_manifest_policy(job: str) -> None:
    """Refuse unless the retained manifest declares the policy the gate enforces."""
    manifest = json.loads((FAMILY_DIR / job / "cases.json").read_text(encoding="utf-8"))
    generated = json.loads(json.dumps(submission_policy(job)))
    require(manifest.get("submission_policy") == generated, f"{job}: cases.json declares another submission policy")


class PolicyGate:
    """The policy checks of a plan: admit, then live_read on a fresh processor read. It carries no submission
    capability, so --preflight uses it and qd_platform.submit refuses it for a submit_wrapper case."""

    def __init__(self, job: str, after: Path | None) -> None:
        require_manifest_policy(job)
        self.job = job
        self.predecessor = None if after is None else load_run(after)
        self.predecessor_record = predecessor_record(self.predecessor)

    def check(self, planned: dict[str, Any]) -> None:
        admit(self.job, planned, self.predecessor)
        try:
            prior_attempts(self.job)
        except RuntimeError as error:
            raise qd_platform.PlatformError(str(error)) from None
        try:
            live_read(self.job, planned, qd_platform.get(qd_platform.platform_route(PLATFORM)))
        except (RuntimeError, KeyError, TypeError, ValueError) as error:
            raise qd_platform.PlatformError(str(error)) from None

    def __call__(self, planned: dict[str, Any]) -> None:
        self.check(planned)


class SubmissionGate(PolicyGate):
    """The verify step qd_platform.submit runs inside the submit lock on the plan whose body it posts: the policy
    checks and the binding to the admitted preflight. Its submit_wrapper attribute is the capability
    qd_platform.submit requires of a case that names this wrapper."""

    submit_wrapper = SUBMIT_WRAPPER

    def __init__(self, job: str, after: Path | None, reviewed: Mapping[str, Any]) -> None:
        super().__init__(job, after)
        self.reviewed = reviewed

    def __call__(self, planned: dict[str, Any]) -> None:
        self.check(planned)
        try:
            bind_reviewed(self.job, planned, self.reviewed, self.predecessor_record)
        except (RuntimeError, KeyError, TypeError, ValueError) as error:
            raise qd_platform.PlatformError(str(error)) from None


def submit_job(job: str, approval: str, after: Path | None, send: bool) -> int:
    """Without send, plan the job read-only, hold the plan to its policy and retain both as plan-read.json; with send,
    submit it through qd_platform.submit with the policy and the binding to that preflight as its verify step."""
    require(job in JOBS, f"{job} is not one of {JOBS}")
    out = FAMILY_DIR / job
    policy = submission_policy(job)
    ceiling, seconds, statuses = float(policy["credit_ceiling"]), float(policy["expected_seconds"]), ("running",)
    if not send:
        verify = PolicyGate(job, after)
        planned = qd_platform.plan(out, PLATFORM, ceiling, seconds, PER_JOB_CREDITS, statuses)
        try:
            verify(planned)
            admission: dict[str, Any] = {"admitted": True}
        except qd_platform.PlatformError as error:
            admission = {"admitted": False, "refusal": str(error)}
        record = {
            **qd_platform.plan_summary(planned),
            "body_sha256_without_process_id": body_digest(planned["body"]),
            "admission": admission,
            "predecessor": verify.predecessor_record,
            "planned_utc": qd_platform.now(),
        }
        qd_platform.write_json(out / "plan-read.json", record)
        print(f"{job}: " + ("admitted" if admission["admitted"] else f"refused: {admission['refusal']}"))
        return 0 if admission["admitted"] else 1
    require(bool(approval.strip()), "--submit requires the owner's --approval text")
    reviewed = json.loads((out / "plan-read.json").read_text(encoding="utf-8"))
    verify = SubmissionGate(job, after, reviewed)
    run = run_directory(job)
    try:
        receipt = qd_platform.submit(
            run, PLATFORM, approval, ceiling, seconds, PER_JOB_CREDITS, statuses, verify=verify
        )
    except RuntimeError, qd_platform.PlatformError:
        discard_unposted(run)
        raise
    print(f"submitted {job}: {receipt['job_id']} in {run.relative_to(ROOT)}")
    return 0


def discard_unposted(run: Path) -> None:
    """Remove a run directory that holds only the two request copies run_directory wrote: a refused submit posted
    nothing and wrote no checkpoint, and a directory without submission.json fails qd_records.read_run."""
    copies = {"cases.json", "circuit.json"}
    if {entry.name for entry in run.iterdir()} <= copies:
        for name in copies & {entry.name for entry in run.iterdir()}:
            (run / name).unlink()
        run.rmdir()


def run_directory(job: str) -> Path:
    """A fresh run directory, results/quandela/runs/<UTC stamp>-qpu_ascella-<FAMILY>-<job>, holding copies of the
    job's cases.json and circuit.json: qd_platform.submit writes its receipt beside them, and the case directory
    keeps only the request and its preflight."""
    stamp = datetime.now(UTC).strftime("%Y-%m-%dT%H%M%SZ")
    run = ROOT / "results/quandela/runs" / f"{stamp}-{PLATFORM.replace(':', '_')}-{FAMILY}-{job}"
    run.mkdir(parents=True, exist_ok=False)
    for name in ("cases.json", "circuit.json"):
        (run / name).write_bytes((FAMILY_DIR / job / name).read_bytes())
    return run


# ---------------------------------------------------------------- analysis


def overlap_from_fidelity(fidelity: float) -> float:
    """The photon overlap M that the overlap-only law F = (1 + M) / (2 (2 - M)) gives for process fidelity F."""
    return (4.0 * fidelity - 1.0) / (2.0 * fidelity + 1.0)


RAIL_INPUTS = ("00", "01", "10", "11")


def rail_rate_ratio(rates: np.ndarray) -> float:
    """D = r(10) r(01) / (r(00) r(11)), r(xy) the absolute eligible rate of input xy summed over its outcomes and
    averaged over its nine readouts.

    Two photons on the postselected CZ succeed with probability 1/9 for inputs 00, 01 and 11 and (5 - 4M)/9 for 10,
    the only input whose photons meet at the 1/3 coupler (permanent 1/3, determinant -1, P = (1+M)/2 per^2 +
    (1-M)/2 det^2), so D = 5 - 4M when overlap is the only error. A local readout keeps one photon per qubit, so
    every readout of an input carries the same success probability, and the average over nine readouts dilutes the
    per-setting systematic that the overdispersion statistic measures. Each rail's detection efficiency appears
    once above and once below, and the two job-01 inputs (10, 01) over the two job-00 inputs (00, 11) leave the
    square of the job-01 pooling scale, which tomo.pooling sets."""
    total = dict.fromkeys(RAIL_INPUTS, 0.0)
    for row in tomo.schedule():
        if row["input"] in total:
            index = row["schedule_index"]
            total[row["input"]] += float(rates[4 * index : 4 * index + 4].sum()) / len(tomo.BASES) ** 2
    require(all(value > 0.0 for value in total.values()), f"a rail-basis input has no eligible rate: {total}")
    return total["10"] * total["01"] / (total["00"] * total["11"])


def control_rate_ratio(rates: np.ndarray) -> float:
    """r(11) / r(01) over the readout sums: 1 at every overlap when the CZ is lossless and the rails balance."""
    total = dict.fromkeys(("01", "11"), 0.0)
    for row in tomo.schedule():
        if row["input"] in total:
            index = row["schedule_index"]
            total[row["input"]] += float(rates[4 * index : 4 * index + 4].sum())
    return total["11"] / total["01"]


OVERDISPERSION_DRAWS = 200


def pearson(eligible: np.ndarray, shots: np.ndarray, scale: np.ndarray) -> float:
    """Pearson chi-squared of the 576 eligible counts about the counts the linear-inversion fit predicts (predicted
    rate times shots over the pooling scale), each weighted by its expected count, one event at least."""
    rates = tomo.absolute_rates(eligible, shots, scale)
    predicted = (tomo.design_matrix() @ (tomo.design_pseudoinverse() @ rates)).reshape(eligible.shape)
    expected = predicted * shots[:, None] / scale[:, None]
    return float((((eligible - expected) ** 2) / np.maximum(expected, 1.0)).sum())


def pearson_of(item: tuple[np.ndarray, np.ndarray, np.ndarray]) -> float:
    """pearson over one (eligible, shots, scale) triple, the unit parallel.ordered_map maps."""
    return pearson(*item)


def overdispersion(
    eligible: np.ndarray, samples: np.ndarray, shots: np.ndarray, scale: np.ndarray, seed: int
) -> dict[str, Any]:
    """The Pearson statistic over its acquisition reference: OVERDISPERSION_DRAWS synthetic pairs drawn as the service
    acquires them under the fit. Each setting stops at its observed sample count; its four eligible outcomes and the
    remaining samples are one multinomial over that quota, with per-sample probabilities the fit's eligible rate per
    shot (negative predictions clipped to 0, the four scaled down together if they pass 1) over the observed samples
    per shot; its shots are the quota plus a negative-binomial count at the observed samples per shot
    (sampled_dataset). Each synthetic pair is refit and scored like the data, so the reference carries the bias of
    the unweighted fit on near-zero cells and the ratio measures scatter beyond the acquisition law."""
    rates = tomo.absolute_rates(eligible, shots, scale)
    predicted = (tomo.design_matrix() @ (tomo.design_pseudoinverse() @ rates)).reshape(eligible.shape)
    per_shot = np.clip(predicted, 0.0, None) / scale[:, None]
    sample_rate = samples / shots
    within = per_shot / sample_rate[:, None]
    within = within / np.maximum(within.sum(axis=1), 1.0)[:, None]
    arrays = {"eligible": within, "samples": np.ones(len(samples)), "any": 1.0 / sample_rate}
    generator = np.random.default_rng(seed)
    # Every synthetic pair is drawn first, in the generator's order, so the statistics do not depend on worker count.
    draws = []
    for _ in range(OVERDISPERSION_DRAWS):
        drawn, _, drawn_shots = sampled_dataset(arrays, samples, generator)
        draws.append((drawn.astype(float), drawn_shots.astype(float), scale))
    reference = ordered_map(pearson_of, draws, min_items=1)
    observed = pearson(eligible, shots, scale)
    centre = float(np.mean(reference))
    return {
        "pearson": observed,
        "reference_mean": centre,
        "reference_95": [float(v) for v in np.percentile(reference, [2.5, 97.5])],
        "ratio": observed / centre,
        "mean_events_per_rate": float(eligible.mean()),
        "draws": OVERDISPERSION_DRAWS,
        "seed": seed,
    }


RECORD_GRID = tuple(round(0.70 + 0.0375 * k, 4) for k in range(9))


def record_inversion(perfs: Mapping[str, Any]) -> dict[str, Any]:
    """The record noise variant's process fidelity F(M) and rail ratio D(M) on RECORD_GRID overlaps at the pair's g2,
    transmittance, clock and dark counts, fitted (F linear-fractional, D quadratic) and inverted on a fine grid by
    monotone interpolation. An observed value outside the fitted range maps to the nearer end, flagged by the fit's
    range. The fit residuals and ranges are recorded so a reader can see where the inversion is trusted."""
    points = [noise_model_at({**perfs, "HOM (%)": 100.0 * m})[FORECAST_RECORD_VARIANT] for m in RECORD_GRID]
    grid = np.asarray(RECORD_GRID)
    fidelity = np.asarray([p["process_fidelity"] for p in points])
    ratio = np.asarray([p["rail_rate_ratio"] for p in points])
    design = np.column_stack([np.ones_like(grid), grid, -grid * fidelity])
    p0, q, r = np.linalg.lstsq(design, fidelity, rcond=None)[0]
    quadratic = np.polyfit(grid, ratio, 2)
    fine = np.linspace(grid[0], grid[-1], 3001)
    f_fine = (p0 + q * fine) / (1.0 + r * fine)
    d_fine = np.polyval(quadratic, fine)
    require(bool(np.all(np.diff(f_fine) > 0)), "the record F(M) is not increasing over the inversion grid")
    require(bool(np.all(np.diff(d_fine) < 0)), "the record D(M) is not decreasing over the inversion grid")
    return {
        "from_fidelity": lambda value: float(np.interp(value, f_fine, fine)),
        "from_rail_ratio": lambda value: float(np.interp(value, d_fine[::-1], fine[::-1])),
        "fit": {
            "grid": list(RECORD_GRID),
            "fidelity_max_residual": float(np.abs((p0 + q * grid) / (1.0 + r * grid) - fidelity).max()),
            "rail_ratio_max_residual": float(np.abs(np.polyval(quadratic, grid) - ratio).max()),
            "fidelity_range": [float(f_fine[0]), float(f_fine[-1])],
            "rail_ratio_range": [float(d_fine[-1]), float(d_fine[0])],
        },
    }


def overlap_estimates(
    runs: Sequence[Path],
    seed: int,
    perfs: Mapping[str, Any],
    loader: Callable[[Path], dict[str, Any]] | None = None,
    jobs: Sequence[str] = JOBS,
) -> dict[str, Any]:
    """The preregistered overlap estimates of a complete pool with joint bootstrap intervals, on the replicates
    tomo.tomography draws from seed: M_F and M_R through the overlap-only laws, and the same two through the record
    noise model at the pair's plan reads (record_inversion)."""
    loaded = [(loader or load_run)(run) for run in runs]
    tallies: dict[str, dict[str, Any]] = {}
    for entry in loaded:
        tallies.update(entry["tallies"])
    rows = tomo.schedule()
    pool = tomo.pooling(loaded, jobs)
    eligible = np.asarray([tallies[row["name"]]["eligible"] for row in rows], dtype=float)
    samples = np.asarray([tallies[row["name"]]["samples"] for row in rows], dtype=float)
    shots = np.asarray([tallies[row["name"]]["shots"] for row in rows], dtype=float)
    scale = np.asarray([pool["scales"][jobs[tomo.JOBS.index(row["job"])]] for row in rows])
    point = tomo.absolute_rates(eligible, shots, scale)
    batch = tomo.resampled_rates(
        eligible, samples, shots, scale, np.random.default_rng(seed), tomo.BOOTSTRAP_REPLICATES
    )
    fidelities = tomo.batch_fidelity(batch)
    m_f = [overlap_from_fidelity(float(f)) for f in fidelities]
    m_r = [(5.0 - rail_rate_ratio(replicate)) / 4.0 for replicate in batch]
    m_f_point = overlap_from_fidelity(tomo.estimate_rates(point)["process_fidelity"])
    m_r_point = (5.0 - rail_rate_ratio(point)) / 4.0
    level = tomo.BOOTSTRAP_LEVEL
    inverse = record_inversion(perfs)
    f_point, d_point = tomo.estimate_rates(point)["process_fidelity"], rail_rate_ratio(point)
    rf = [inverse["from_fidelity"](float(f)) for f in fidelities]
    rr = [inverse["from_rail_ratio"](rail_rate_ratio(replicate)) for replicate in batch]
    rf_point, rr_point = inverse["from_fidelity"](f_point), inverse["from_rail_ratio"](d_point)

    def summary(point_value: float, replicates: Sequence[float]) -> dict[str, Any]:
        return {"point": point_value, "interval": tomo.intervals(point_value, replicates, level)[tomo.INTERVAL_KIND]}

    record_model = {
        "fit": inverse["fit"],
        "overlap_from_fidelity": summary(rf_point, rf),
        "overlap_from_rail_rates": summary(rr_point, rr),
        "difference": summary(rf_point - rr_point, [a - b for a, b in zip(rf, rr, strict=True)]),
    }
    return {
        "record_model": record_model,
        "overlap_from_fidelity": {
            "point": m_f_point,
            "interval": tomo.intervals(m_f_point, m_f, level)[tomo.INTERVAL_KIND],
        },
        "overlap_from_rail_rates": {
            "point": m_r_point,
            "interval": tomo.intervals(m_r_point, m_r, level)[tomo.INTERVAL_KIND],
        },
        "difference": {
            "point": m_f_point - m_r_point,
            "interval": tomo.intervals(m_f_point - m_r_point, [a - b for a, b in zip(m_f, m_r, strict=True)], level)[
                tomo.INTERVAL_KIND
            ],
        },
        "rail_rate_ratio": rail_rate_ratio(point),
        "control_rate_ratio": {
            "point": control_rate_ratio(point),
            "interval": tomo.intervals(
                control_rate_ratio(point), [control_rate_ratio(replicate) for replicate in batch], level
            )[tomo.INTERVAL_KIND],
        },
        "overdispersion": overdispersion(eligible, samples, shots, scale, seed_plan()["overdispersion"][1]),
    }


def overlap_law(overlap: float) -> float:
    """F_pro of the postselected CZ when photon overlap is the only error (see rail_rate_ratio for the rates)."""
    return (1.0 + overlap) / (2.0 * (2.0 - overlap))


def plan_reads(loaded: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """The pooled pair's plan reads: V, g2 and transmittance averaged over the jobs, and the rest of the perfs (dark
    counts, clock) from the job-00 run, chosen by job name whatever order the runs arrive in."""
    first = min(loaded, key=lambda entry: str(entry["job"]))
    perfs = [entry["perfs"] for entry in loaded]
    mean = {key: sum(float(p[key]) for p in perfs) / len(perfs) for key in ("HOM (%)", "g2 (%)", "Transmittance (%)")}
    return {**first["perfs"], **mean}


def noise_model_at(perfs: Mapping[str, Any]) -> dict[str, dict[str, float]]:
    """The retained noise pipeline per variant at one read: the process-fidelity estimand and r(11) / r(01)."""
    figures = tomo.perf_figures(perfs)
    dark = [float(rate) for rate in perfs["Dark counts (detection/s)"]]
    per_setting = ordered_map(tomo.forecast_setting, [(row, figures, dark) for row in tomo.schedule()], min_items=1)
    out = {}
    for name in (FORECAST_RECORD_VARIANT, "g2-corrected overlap, loss and dark counts"):
        rates = tomo.exact_rates(tomo.variant_arrays(per_setting, name))
        out[name] = {
            "process_fidelity": tomo.estimate_rates(rates)["process_fidelity"],
            "control_rate_ratio": control_rate_ratio(rates),
            "rail_rate_ratio": rail_rate_ratio(rates),
        }
    return out


def retained_overdispersion() -> dict[str, float]:
    """The overdispersion of the retained 2026-10-31 pair, the anchor of both overdispersion conjectures."""
    loaded = [tomo.load_run(ROOT / run) for run in TOMOGRAPHY_RUNS]
    tallies: dict[str, dict[str, Any]] = {}
    for entry in loaded:
        tallies.update(entry["tallies"])
    rows = tomo.schedule()
    pool = tomo.pooling(loaded, tomo.JOBS)
    eligible = np.asarray([tallies[row["name"]]["eligible"] for row in rows], dtype=float)
    samples = np.asarray([tallies[row["name"]]["samples"] for row in rows], dtype=float)
    shots = np.asarray([tallies[row["name"]]["shots"] for row in rows], dtype=float)
    scale = np.asarray([pool["scales"][row["job"]] for row in rows])
    return overdispersion(eligible, samples, shots, scale, seed_plan()["overdispersion"][1])


MODEL_CHECK = "scatter-matches-acquisition-law"


def conjecture_verdicts(process: Mapping[str, Any], overlaps: Mapping[str, Any], perfs: Mapping[str, Any]) -> list:
    """Each preregistered conjecture's prediction, the band it is held against and its verdict. A band is
    {"lower", "upper"}, either of which may be None for a one-sided test. The model check MODEL_CHECK decides
    whether the acquisition bootstrap describes the data; when it is falsified, every other verdict is reported as
    conditional on that failure rather than as decided."""
    v, g2 = float(perfs["HOM (%)"]) / 100.0, float(perfs["g2 (%)"]) / 100.0
    corrected = min(1.0, (v + g2) / (1.0 - g2))
    model = noise_model_at(perfs)
    ceiling = noise_model_at({**perfs, "HOM (%)": 100.0})[FORECAST_RECORD_VARIANT]["process_fidelity"]
    record, g2_variant = model[FORECAST_RECORD_VARIANT], model["g2-corrected overlap, loss and dark counts"]
    spread = overlaps["overdispersion"]
    fidelity = process["process_fidelity_interval"]
    anchor = retained_overdispersion()
    growth = 1.0 + (anchor["ratio"] - 1.0) * spread["mean_events_per_rate"] / anchor["mean_events_per_rate"]

    def band(lower: float | None, upper: float | None) -> dict[str, float | None]:
        return {"lower": lower, "upper": upper}

    def interval(key: str) -> dict[str, float | None]:
        low, high = overlaps[key]["interval"]
        return band(low, high)

    def record_interval(key: str) -> dict[str, float | None]:
        low, high = overlaps["record_model"][key]["interval"]
        return band(low, high)

    # (prediction, band, observed): a two-sided interval test asks whether the band holds the prediction; a band test
    # with an observed value asks whether the band holds the observation.
    tests: dict[str, tuple[float, dict[str, float | None], float | None]] = {
        "overlap-only-law": (overlap_law(v), band(*fidelity), None),
        "g2-corrected-overlap-law": (overlap_law(corrected), band(*fidelity), None),
        "noise-model-record-variant": (record["process_fidelity"], band(*fidelity), None),
        "noise-model-g2-corrected-variant": (g2_variant["process_fidelity"], band(*fidelity), None),
        "rail-ratio-reads-hom": (v, record_interval("overlap_from_rail_rates"), None),
        "two-overlaps-agree": (0.0, interval("difference"), None),
        "record-overlaps-agree": (0.0, record_interval("difference"), None),
        "noise-model-ceiling": (ceiling, band(fidelity[0], None), None),
        "control-ratio-lossless": (1.0, interval("control_rate_ratio"), None),
        "control-ratio-noise-model": (record["control_rate_ratio"], interval("control_rate_ratio"), None),
        MODEL_CHECK: (spread["pearson"], band(None, spread["reference_95"][1]), None),
        "overdispersion-constant-factor": (
            anchor["ratio"],
            band(0.75 * anchor["ratio"], 1.25 * anchor["ratio"]),
            spread["ratio"],
        ),
        "overdispersion-relative-systematic": (growth, band(0.75 * growth, 1.25 * growth), spread["ratio"]),
    }
    decided = {}
    for row in CONJECTURES:
        prediction, limits, observed = tests[row["id"]]
        value = prediction if observed is None else observed
        lower, upper = limits["lower"], limits["upper"]
        holds = (lower is None or lower <= value) and (upper is None or value <= upper)
        decided[row["id"]] = {
            "id": row["id"],
            "prediction": prediction,
            "observed": observed,
            "band": limits,
            "verdict": "survives" if holds else "falsified",
        }
    check_failed = decided[MODEL_CHECK]["verdict"] == "falsified"
    out = []
    for row in CONJECTURES:
        entry = decided[row["id"]]
        if check_failed and row["id"] != MODEL_CHECK:
            entry["verdict"] = f"conditional on a failed model check: {entry['verdict']}"
        if process.get("status") != "decided":
            entry["verdict"] = f"descriptive: {entry['verdict']}"
        out.append(entry)
    return out


RETAINED_VERDICTS = "retained-conjecture-verdicts.json"


def retained_verdicts() -> dict[str, Any]:
    """The preregistered conjectures held against the retained 2026-10-31 pair through this case's own estimators,
    with the retained case's loader, pooling and bootstrap seed: the baseline each new verdict is read against."""
    runs = [ROOT / run for run in TOMOGRAPHY_RUNS]
    record = tomo.analyze(runs, forecast_path=None)
    loaded = [tomo.load_run(run) for run in runs]
    _, bootstrap = tomo.seed_plan()
    perfs = plan_reads(loaded)
    overlaps = overlap_estimates(runs, bootstrap[1], perfs, loader=tomo.load_run, jobs=tomo.JOBS)
    return {
        "schema": "qd-cz-tomography-reference-retained-verdicts-v1",
        "runs": list(TOMOGRAPHY_RUNS),
        "plan_reads": {key: perfs[key] for key in ("HOM (%)", "g2 (%)", "Transmittance (%)")},
        "process_fidelity": record["process"]["process_fidelity"],
        "process_fidelity_interval": record["process"]["process_fidelity_interval"],
        "overlap_estimates": overlaps,
        "conjectures": conjecture_verdicts(record["process"], overlaps, perfs),
    }


def analyze(runs: Sequence[Path]) -> dict[str, Any]:
    """Pool the two collected runs through tomo.analyze with this case's loader, jobs and bootstrap seed; a setting
    that stopped at max_shots short of its max_samples leaves the pool descriptive."""
    record = tomo.analyze(runs, loader=load_run, jobs=JOBS, seed=seed_plan()["bootstrap"][1], forecast_path=None)
    record["schema"] = "qd-cz-tomography-reference-analysis-v1"
    short = sorted(name for run in runs for name in load_run(run)["short"])
    process = record.get("process")
    if short and isinstance(process, dict):
        process["status"] = "descriptive"
        process["short_settings"] = short
        process["pooling"]["status"] = "descriptive"
        process["pooling"]["reason"] = f"{len(short)} settings stopped at max_shots short of their max_samples"
    if isinstance(process, dict):
        loaded = [load_run(run) for run in runs]
        perfs = plan_reads(loaded)
        overlaps = overlap_estimates(runs, seed_plan()["bootstrap"][1], perfs)
        record["overlap_estimates"] = overlaps
        record["hom_offset_from_preferred"] = {
            entry["job"]: float(entry["perfs"]["HOM (%)"]) - HOM_PREFERRED for entry in loaded
        }
        record["conjectures"] = conjecture_verdicts(process, overlaps, perfs)
    return record


def main() -> int:
    # perceval.utils.persistent_data creates its job_group directory at first import without exist_ok; workers of
    # parallel.ordered_map that import it concurrently in a fresh home race on that mkdir, which -W error raises.
    import perceval  # noqa: F401

    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--read", action="store_true", help="retain the live platform read")
    group.add_argument("--estimate", action="store_true", help="retain Perceval's shot estimate at the probe budget")
    group.add_argument("--build", action="store_true", help="write both jobs' cases.json and circuit.json")
    group.add_argument("--forecast", action="store_true", help="recompute and compare forecast.json")
    group.add_argument("--write-forecast", action="store_true", help="write forecast.json")
    group.add_argument(
        "--retained-verdicts",
        action="store_true",
        help=f"write {RETAINED_VERDICTS}: the conjectures on the retained pair",
    )
    group.add_argument("--analyze", nargs="+", metavar=("OUT.json", "RUN"))
    group.add_argument("--preflight", choices=JOBS, help="plan the job read-only and hold it to its policy")
    group.add_argument("--submit", choices=JOBS, help="submit the job once under --approval")
    parser.add_argument("--approval", default="", help="the owner's approval text for --submit")
    parser.add_argument("--after", type=Path, help="the collected job-00 run that job-01 requires")
    args = parser.parse_args()
    if args.preflight or args.submit:
        try:
            return submit_job(args.preflight or args.submit, args.approval, args.after, send=bool(args.submit))
        except (RuntimeError, qd_platform.PlatformError) as error:
            raise SystemExit(f"refused: {error}") from None
    if args.read:
        return platform_read()
    if args.estimate:
        return estimate_command()
    if args.build:
        return build()
    if args.forecast:
        return check_forecast()
    if args.write_forecast:
        (FAMILY_DIR / FORECAST).write_bytes(forecast_bytes())
        return 0
    if args.retained_verdicts:
        (FAMILY_DIR / RETAINED_VERDICTS).write_text(
            json.dumps(retained_verdicts(), indent=1, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8"
        )
        return 0
    if args.analyze:
        out, *runs = args.analyze
        require(len(runs) == len(JOBS), "--analyze takes OUT.json and the two runs")
        result = analyze([Path(run) for run in runs])
        Path(out).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
