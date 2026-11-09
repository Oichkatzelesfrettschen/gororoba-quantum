"""Ascella CZ process tomography reference above 90 % HOM: two qpu:ascella jobs of 72 template iterations.

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
- Gate. A submit_wrapper gate admits a plan only at HOM strictly above qd_platform.HOM_FLOOR, at status available or
  running with the token idle, with the shot estimate and an in-lock processor re-read on the plan's perfs, the
  transmittance at or above the floor, and, for job-01, a completed job-00 run with every iteration counted. The
  request is frozen at build: a gate refuses, it never adapts the body to the live read.
- Forecast. The noise forecast is a curve over HOM at the retained read's g2, transmittance and dark counts, since
  no read above 90 % exists to forecast at; the plan read at submission picks the point.

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
from collections.abc import Mapping, Sequence
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
# HOM points of the forecast curve, in percent: the admitted region above qd_platform.HOM_FLOOR.
FORECAST_HOMS = (90.5, 91.0, 91.5, 92.0, 92.5, 93.0, 94.0)
FORECAST_RECORD_VARIANT = "source, loss and dark counts"
FORECAST_CURVE_VARIANTS = ("indistinguishability only", FORECAST_RECORD_VARIANT)
TOLERANCE = tomo.TOLERANCE


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
    need = count + 1 + len(FORECAST_HOMS)
    require(len(usable) >= need, f"{DRAW} holds {len(usable)} usable values, not {need}")
    return {
        "compilation": usable[:count],
        "bootstrap": usable[count],
        "forecast": usable[count + 1 : need],
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
        "hom_percent": {"above": qd_platform.HOM_FLOOR},
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


def forecast_point(item: tuple[float, dict[str, Any], list[float], int]) -> dict[str, Any]:
    """The forecast at one HOM: per curve variant the estimand, and for the record variant the delta-method spread of
    this design and of the retained uniform 4000-sample design, and one synthetic dataset of this design analyzed as
    a run would be."""
    hom, figures, dark, seed = item
    rows = tomo.schedule()
    at = {**figures, "hom": hom / 100.0}
    per_setting = [tomo.forecast_setting((row, at, dark)) for row in rows]
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
    items = [(hom, figures, dark, value) for hom, (_, value) in zip(FORECAST_HOMS, seeds, strict=True)]
    points = ordered_map(forecast_point, items, min_items=1)
    for point, (index, _) in zip(points, seeds, strict=True):
        point["seed_index"] = index
        del point["seed"]
    return {
        "schema": "qd-cz-tomography-reference-forecast-v1",
        "read": {"path": READ, "sha256": qd_platform.sha256_bytes((FAMILY_DIR / READ).read_bytes()), **figures},
        "basis": "the retained read's g2, transmittance, clock and dark counts at each HOM of the curve; no read "
        "above the HOM floor exists, so the plan read at submission picks the point",
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


def check_job(job: str) -> None:
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
    values = [value for _, value in [*plan["compilation"], plan["bootstrap"], *plan["forecast"]]]
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
        require(planned["case"] == job and planned["platform"] == PLATFORM, f"the plan names {planned['case']}")
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
        require(hom > qd_platform.HOM_FLOOR, f"{job}: HOM {hom:g} % is not above {qd_platform.HOM_FLOOR:g} %")
        floor = float(policy["transmittance_percent"]["at_least"])
        t = float(figures["Transmittance (%)"])
        require(t >= floor, f"{job}: transmittance {t:g} % is below the {floor:g} % the caps need")
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
    """Refuse a further attempt of job under the stopping rule: a posted attempt that is not collected, or that
    returned a counted iteration, ends the job's attempts, and so do MAX_ATTEMPTS posted attempts. A directory with no
    posting checkpoint (submission.json, submission-state.json or job-body.json) is no attempt."""
    posted = []
    for run in sorted(runs_dir.glob(f"*-{PLATFORM.replace(':', '_')}-{FAMILY}-{job}")):
        if not any((run / name).exists() for name in ("submission.json", "submission-state.json", "job-body.json")):
            continue
        posted.append(run)
        name = run.relative_to(runs_dir)
        require((run / "results.json").exists(), f"{job}: the earlier attempt {name} is not collected")
        results = json.loads((run / "results.json").read_text(encoding="utf-8"))
        counted = [e for e in results.get("iterations") or [] if isinstance(e, dict) and e.get("counts")]
        require(not counted, f"{job}: the earlier attempt {name} returned counts, so the job is never resubmitted")
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
    except (RuntimeError, qd_platform.PlatformError):
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


def analyze(runs: Sequence[Path]) -> dict[str, Any]:
    """Pool the two collected runs under the retained case's estimator, with this case's bootstrap seed."""
    loaded = [load_run(run) for run in runs]
    jobs = [entry["job"] for entry in loaded]
    require(sorted(jobs) == sorted(JOBS), f"the runs are not both jobs: {jobs}")
    tallies: dict[str, dict[str, Any]] = {}
    for entry in loaded:
        tallies.update(entry["tallies"])
    rows = tomo.schedule()
    record: dict[str, Any] = {
        "schema": "qd-cz-tomography-reference-analysis-v1",
        "runs": [{"job": e["job"], "cases_sha256": e["cases_sha256"], "counted": len(e["tallies"])} for e in loaded],
        "settings_with_counts": len(tallies),
        "eligible_events_by_setting": {name: sum(t["eligible"]) for name, t in tallies.items()},
        "uncounted_by_kind": {k: sum(e["uncounted"].get(k, 0) for e in loaded) for k in (*tomo.UNCOUNTED, "uncounted")},
    }
    if not all(row["name"] in tallies and sum(tallies[row["name"]]["eligible"]) > 0 for row in rows):
        record["process"] = "undecided"
        return record
    pool = tomo.pooling(loaded, JOBS)
    eligible = np.asarray([tallies[row["name"]]["eligible"] for row in rows], dtype=float)
    samples = np.asarray([tallies[row["name"]]["samples"] for row in rows], dtype=float)
    shots = np.asarray([tallies[row["name"]]["shots"] for row in rows], dtype=float)
    scale = np.asarray([pool["scales"][row["job"]] for row in rows])
    seed = seed_plan()["bootstrap"][1]
    process = tomo.tomography(eligible, samples, shots, scale, np.random.default_rng(seed))
    process["pooling"] = pool
    process["status"] = pool["status"]
    short = sorted(name for entry in loaded for name in entry.get("short", []))
    if short:
        process["status"] = "descriptive"
        process["short_settings"] = short
        pool["reason"] = f"{len(short)} settings stopped at max_shots short of their max_samples"
    record["process"] = process
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
    if args.analyze:
        out, *runs = args.analyze
        require(len(runs) == len(JOBS), "--analyze takes OUT.json and the two runs")
        result = analyze([Path(run) for run in runs])
        Path(out).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
