"""Analysis of the two runs of results/iqm/cases/grover-depth-sedenion-walsh, the Garnet follow-up case built by
scripts/iqm_garnet_followup.py (design: docs/design/iqm-garnet-grover-depth-sedenion-walsh.md, "Preregistered
decisions").

analyze reads the run of job "grover" and the run of job "sedenion" through iqm_records.read_run and writes one
record, schema SCHEMA. Its "decisions" apply the rules of the case's prediction.json (decisions) and the bit-order
check of the design document's "Preregistered decisions"; each verdict follows one of those rules. Beside a verdict
sit fields that decide nothing (readout-corrected values, per-qubit marginals, the uniformity statistics against k0),
and every other statistic sits under "exploratory".

Admission. A run enters the analysis only when it ran on the quantum computer QC (a mock run returns random bits),
belongs to the case CASE, carries the prediction digest and the cases.json bytes of the retained case directory,
completed, compiled against the calibration set of the prediction, and measured every circuit of its job in
the prediction's measurement order. One run per job. Anything else raises AnalysisError, and iqm_records.RecordError
reports a run directory whose records contradict each other.

Variances (the design document names the binomial and the paired per-shot variances; the rest follow from them):
- Contrasts between arms (prx load generic, prx load line, CZ sequence, sedenion row against truncation and against
  null): independent binomial variances p (1 - p) / n of each arm's pooled kept shots at the observed frequency,
  as in grover_line_analysis.analyze. The readout-corrected contrast and its delta-method standard error through
  grover_line_analysis.Readout are reported beside.
- Depth law: lambda_k = (P_k - 1/8) / (P_k^ideal - 1/8) from raw pooled marked frequencies; f = lambda_3 -
  lambda_2^2 / lambda_1 carries the delta-method variance over the three independent arms at the observed
  frequencies, and z = (f - f_model) / SE against the model's f in prediction.json. The corrected f, zero under
  lambda_k = A r^k, is reported with its Readout delta-method SE and its z against zero.
- Qubit or role: D = w(QB17) - w(QB20) is the mean of x = I(QB17 wrong) - I(QB20 wrong) over every kept shot of
  the pooled copies; its variance is the sample variance of x divided by the shots, which carries the covariance of
  two bits read in one shot.

Resolution. A contrast resolves at z >= Z_RESOLVE in the direction named; a negative resolved contrast falsifies
its hypothesis. The role rule reads |z| > Z_RESOLVE on the unrounded z, the strict form of prediction.json
(decisions.role_or_qubit). A sedenion row resolves when
row minus truncation and row minus null each reach Z_RESOLVE and the row arms' pooled counts have the row peak as
their single most frequent string.

Every value is rounded to 6 digits. The CPU-bound per-arm readout solves and the per-row sedenion decisions run
through parallel.ordered_map.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

import iqm_records
from grover_line_analysis import Acquisition, Readout, ideal_probability, r6, uniformity_wald
from parallel import ordered_map

CASE = "grover-depth-sedenion-walsh"
QC = "garnet"
SCHEMA = "iqm-garnet-followup-analysis-v1"
JOBS = ("grover", "sedenion")
CASE_DIR = iqm_records.ROOT / "results" / "iqm" / "cases" / CASE
Z_RESOLVE = 3.0
MARKS = ("101", "011")
ROWS = (5, 10)
EXPLORATORY_NOTE = "exploratory: no decision rests on these"


class AnalysisError(ValueError):
    pass


def outcome_index(key: str) -> int:
    """Basis index of an outcome string: character q is bit q, as in the case's prediction keys."""
    if not key or set(key) - {"0", "1"}:
        raise AnalysisError(f"outcome {key!r} is not a bit string")
    return sum(int(c) << q for q, c in enumerate(key))


def outcome_key(index: int, width: int) -> str:
    return "".join(str((index >> q) & 1) for q in range(width))


@dataclass(frozen=True)
class Job:
    """One admitted run: the counts of every circuit in job order, each circuit's measurement order and the
    prediction its directory carries."""

    job: str
    directory: Path
    names: list[str]
    counts: dict[str, np.ndarray]
    orders: dict[str, list[str]]
    prediction: dict[str, Any]
    run: iqm_records.Run

    def copies(self, stem: str) -> list[str]:
        found = [n for n in self.names if re.fullmatch(re.escape(stem) + r"(-c\d+)?", n)]
        if not found:
            raise AnalysisError(f"{self.directory}: no circuit of arm {stem}")
        return found

    def pooled(self, stem: str) -> tuple[np.ndarray, list[str]]:
        names = self.copies(stem)
        order = self.orders[names[0]]
        if any(self.orders[n] != order for n in names):
            raise AnalysisError(f"{self.directory}: the copies of {stem} measure in different orders")
        return np.sum([self.counts[n] for n in names], axis=0), order


def read_job(run_dir: Path, case_dir: Path = CASE_DIR) -> Job:
    """Admit one run of the case: the shared record checks, then the case-bound ones."""
    run = iqm_records.read_run(run_dir)
    submission = run.submission
    if submission["qc"] != QC or run.case.get("case") != CASE:
        raise AnalysisError(f"{run_dir}: a {run.case.get('case')} run on {submission['qc']}, not a {CASE} run on {QC}")
    bound = json.loads((case_dir / "cases.json").read_text(encoding="utf-8"))
    if run.case.get("prediction_sha256") != bound["prediction_sha256"]:
        raise AnalysisError(f"{run_dir}: the case binds another prediction digest than the retained case")
    if run.cases_sha256 != iqm_records.sha256((case_dir / "cases.json").read_bytes()):
        raise AnalysisError(f"{run_dir}: cases.json differs from the retained case")
    job = run.row["job"]
    if job not in JOBS:
        raise AnalysisError(f"{run_dir}: job {job} is not a job of {CASE}")
    prediction = json.loads((run_dir / "prediction.json").read_text(encoding="utf-8"))
    compilation = run.job.get("compilation") or {}
    if compilation.get("calibration_set_id") != prediction["calibration_set"]:
        raise AnalysisError(f"{run_dir}: compiled against another calibration set than the prediction's")
    measurements = run.completed_measurements()
    files = [c["file"] for c in run.row["circuits"]]
    names = [Path(f).stem for f in files]
    arms = {n: a for n, a in prediction["arms"].items() if a["job"] == job}
    if set(names) != set(arms) or len(set(names)) != len(names):
        raise AnalysisError(f"{run_dir}: the job's circuits are not the prediction's arms of job {job}")
    raw = json.loads(run.raw["measurement_counts.json"])
    if len(raw) != len(files) or len(measurements) != len(files):
        raise AnalysisError(f"{run_dir}: {len(raw)} count records for {len(files)} circuits")
    counts: dict[str, np.ndarray] = {}
    orders: dict[str, list[str]] = {}
    for name, rel, record, measured in zip(names, files, raw, measurements, strict=True):
        width = len(arms[name]["locus"])
        vector = np.zeros(2**width, dtype=np.int64)
        for key, n in record["counts"].items():
            if len(key) != width:
                raise AnalysisError(f"{run_dir}: {name} outcome {key!r} is not {width} bits")
            vector[outcome_index(key)] += n
        if int(vector.sum()) != len(next(iter(measured.values()))):
            raise AnalysisError(f"{run_dir}: {name} counts and measurements disagree on the shots")
        counts[name] = vector
        circuit = json.loads((run_dir / rel).read_text(encoding="utf-8"))
        order = next(op["locus"] for op in circuit["instructions"] if op["name"] == "measure")
        if order != arms[name]["locus"]:
            raise AnalysisError(f"{run_dir}: {name} measures {order}, not the prediction's {arms[name]['locus']}")
        orders[name] = order
    return Job(job, run_dir, names, counts, orders, prediction, run)


def binomial_se(parts: list[tuple[float, float]]) -> float:
    """Standard error of a sum of independent frequencies, each (p, n)."""
    return math.sqrt(sum(p * (1 - p) / n for p, n in parts))


def z_of(value: float, se: float) -> float:
    if se <= 0.0:
        raise AnalysisError("a statistic with zero variance has no z-score")
    return value / se


def verdict_of(z: float, strict: bool = False) -> str:
    high = z > Z_RESOLVE if strict else z >= Z_RESOLVE
    low = z < -Z_RESOLVE if strict else z <= -Z_RESOLVE
    return "positive" if high else "negative" if low else "unresolved"


def stems_of(job: Job) -> list[str]:
    seen: list[str] = []
    for name in job.names:
        stem = re.sub(r"-c\d+$", "", name)
        if stem not in seen:
            seen.append(stem)
    return seen


def fit_arm(item: tuple[Acquisition, str, str]) -> dict[str, Any]:
    """The corrected marked probability of one Grover arm, its gradients through the readout system and its
    corrected uniformity statistic over the unmarked cells (all cells for k0, whose mark is 000)."""
    acquisition, stem, marked = item
    readout = Readout(acquisition)
    value, grad_p, grad_a = readout.marked(stem, marked)
    cells = list(range(8)) if stem == "k0" else [x for x in range(8) if x != outcome_index(marked)]
    wald = uniformity_wald(*readout.corrected_covariance(stem), cells)
    return {
        "stem": stem,
        "corrected": float(value),
        "corrected_se": math.sqrt(readout.variance(grad_p, grad_a)),
        "wald": wald,
        "dof": len(cells) - 1,
        "grad_p": grad_p,
        "grad_a": grad_a,
    }


def combined(readout: Readout, parts: list[tuple[float, dict[str, Any]]]) -> tuple[float, float]:
    """A linear combination of corrected marked probabilities with its delta-method standard error."""
    grad_p: dict[str, np.ndarray] = {}
    grad_a = np.zeros((8, 8))
    value = 0.0
    for scale, fit in parts:
        value += scale * fit["corrected"]
        for name, g in fit["grad_p"].items():
            grad_p[name] = grad_p.get(name, np.zeros(8)) + scale * g
        grad_a = grad_a + scale * fit["grad_a"]
    return value, math.sqrt(readout.variance(grad_p, grad_a))


def predicted_of(prediction: dict[str, Any], key: str) -> dict[str, Any]:
    keep = ("predicted", "predicted_z", "se_at_planned_shots")
    return {k: v for k, v in prediction["decisions"][key].items() if k in keep}


def end_difference(job: Job, stem: str, marked: str) -> dict[str, Any]:
    """D = w(QB17) - w(QB20) over the pooled copies of an arm, with the paired per-shot variance; w is the
    probability that the qubit reads other than the mark's bit at its measurement position."""
    pooled, order = job.pooled(stem)
    shots = int(pooled.sum())
    p = pooled / shots
    i17, i20, i16 = order.index("QB17"), order.index("QB20"), order.index("QB16")
    x = np.zeros(len(p))
    wrong = {q: np.zeros(len(p)) for q in ("QB17", "QB20", "QB16")}
    for index in range(len(p)):
        key = outcome_key(index, len(order))
        for q, i in (("QB17", i17), ("QB20", i20), ("QB16", i16)):
            wrong[q][index] = float(key[i] != marked[i])
        x[index] = wrong["QB17"][index] - wrong["QB20"][index]
    d = float(x @ p)
    se = math.sqrt(max(float((x * x) @ p) - d * d, 0.0) / shots)
    return {
        "arm": stem,
        "copies": job.copies(stem),
        "kept_shots": shots,
        "D": r6(d),
        "se_paired": r6(se),
        "z": r6(z_of(d, se)),
        "resolved": abs(z_of(d, se)) > Z_RESOLVE,
        "wrong_bit": {q: r6(float(w @ p)) for q, w in sorted(wrong.items())},
    }


def role_decision(job: Job) -> tuple[dict[str, Any], dict[str, Any]]:
    forward = end_difference(job, "m101-k1", "101")
    reverse = end_difference(job, "r-m101-k1", "101")
    resolved = bool(forward["resolved"])
    reverse_resolved = bool(reverse["resolved"])
    if not resolved:
        reading = "open: the forward D does not resolve"
    elif not reverse_resolved:
        reading = "open: the reversed D does not resolve"
    elif (forward["D"] > 0) == (reverse["D"] > 0):
        reading = "with the qubits: a resolved reversed D of the forward sign"
    else:
        reading = "moves with the roles: a resolved reversed D of the opposite sign"
    decision = {
        "forward": forward,
        "reversed": reverse,
        "forward_resolved": resolved,
        "reversed_resolved": reverse_resolved,
        "reading": reading,
        "predicted": job.prediction["decisions"]["role_or_qubit"]["model"],
    }
    beside = {
        "m011_forward": end_difference(job, "m011-k1", "011"),
        "m011_reversed": end_difference(job, "r-m011-k1", "011"),
    }
    return decision, beside


def grover_analysis(job: Job) -> tuple[dict[str, Any], dict[str, Any]]:
    prediction = job.prediction
    acquisition = Acquisition(job.directory.name, job.names, job.counts, job.orders, prediction)
    readout = Readout(acquisition)
    stems = [s for s in stems_of(job) if not s.startswith("ro-")]
    marks = {s: prediction["arms"][job.copies(s)[0]]["marked"] for s in stems}
    fits_list = ordered_map(fit_arm, [(acquisition, s, marks[s]) for s in stems])
    fits = {f["stem"]: f for f in fits_list}
    pooled = {}
    for stem in stems:
        counts, _ = job.pooled(stem)
        shots = int(counts.sum())
        pooled[stem] = (float(counts[outcome_index(marks[stem])]) / shots, shots)

    def contrast(first: str, second: str, key: str) -> dict[str, Any]:
        (p1, n1), (p2, n2) = pooled[first], pooled[second]
        raw = p1 - p2
        se = binomial_se([(p1, n1), (p2, n2)])
        z = z_of(raw, se)
        corrected, corrected_se = combined(readout, [(1.0, fits[first]), (-1.0, fits[second])])
        verdict = verdict_of(z)
        return {
            "first": first,
            "second": second,
            "raw": r6(raw),
            "se": r6(se),
            "z": r6(z),
            "verdict": verdict,
            "reading": {
                "positive": "resolved positive: the hypothesis stands",
                "negative": "resolved negative: the hypothesis is falsified",
                "unresolved": "unresolved: no effect and a small effect are not separated",
            }[verdict],
            "corrected": r6(corrected),
            "corrected_se": r6(corrected_se),
            "predicted": predicted_of(prediction, key),
        }

    decisions: dict[str, Any] = {
        "prx_load_generic": contrast("m101-k1-fused", "m101-k1-generic", "prx_load_generic"),
        "prx_load_line": contrast("m101-k1", "m101-k1-padded", "prx_load_line"),
        "cz_sequence": contrast("m101-k1-padded", "m101-k1-fused", "cz_sequence"),
    }
    for marked in MARKS:
        arm_of = {k: f"m{marked}-k{k}" for k in (1, 2, 3)}
        scale = {k: ideal_probability(k) - 1 / 8 for k in arm_of}
        lam = {k: (pooled[arm_of[k]][0] - 1 / 8) / scale[k] for k in arm_of}
        if lam[1] <= 0.0:
            raise AnalysisError(f"m{marked}-k1 retains nothing above uniform: lambda_1 = {lam[1]}")
        f = lam[3] - lam[2] ** 2 / lam[1]
        gradient = {3: 1.0, 2: -2 * lam[2] / lam[1], 1: lam[2] ** 2 / lam[1] ** 2}
        se = math.sqrt(
            sum(
                (gradient[k] / scale[k]) ** 2 * pooled[arm_of[k]][0] * (1 - pooled[arm_of[k]][0]) / pooled[arm_of[k]][1]
                for k in arm_of
            )
        )
        model = prediction["decisions"][f"depth_law_{marked}"]
        z = z_of(f - model["predicted"], se)
        corrected_lam = {k: (fits[arm_of[k]]["corrected"] - 1 / 8) / scale[k] for k in arm_of}
        corrected_f = corrected_lam[3] - corrected_lam[2] ** 2 / corrected_lam[1]
        corrected_gradient = {
            3: 1.0,
            2: -2 * corrected_lam[2] / corrected_lam[1],
            1: corrected_lam[2] ** 2 / corrected_lam[1] ** 2,
        }
        corrected_weights = [(corrected_gradient[k] / scale[k], fits[arm_of[k]]) for k in (1, 2, 3)]
        _, corrected_se = combined(readout, corrected_weights)
        decisions[f"depth_law_{marked}"] = {
            "lambda_raw": {str(k): r6(v) for k, v in lam.items()},
            "f_raw": r6(f),
            "se": r6(se),
            "model_f": model["predicted"],
            "z_against_model": r6(z),
            "verdict": "outside the model: the retention law bends with depth" if abs(z) >= Z_RESOLVE else "inside",
            "corrected_lambda": {str(k): r6(v) for k, v in corrected_lam.items()},
            "corrected_f": r6(corrected_f),
            "corrected_f_se": r6(corrected_se),
            "corrected_f_z_against_zero": r6(z_of(corrected_f, corrected_se)),
            "predicted": {
                k: v
                for k, v in model.items()
                if k in ("predicted_lambda", "resolvable_deviation", "se_at_planned_shots")
            },
        }
    role, beside = role_decision(job)
    decisions["role_or_qubit"] = role
    decisions["unmarked_uniformity"] = {
        "k0_reference": {"wald": r6(fits["k0"]["wald"]), "dof": fits["k0"]["dof"]},
        "arms": {
            s: {"wald": r6(fits[s]["wald"]), "dof": fits[s]["dof"], "over_k0": r6(fits[s]["wald"] / fits["k0"]["wald"])}
            for s in stems
            if s != "k0"
        },
        "reading": "reported against the k0 statistic as in the retained analysis; no threshold decides",
        "rule": prediction["decisions"]["k0_reference"],
    }
    arms: dict[str, Any] = {}
    for stem in stems:
        names = job.copies(stem)
        counts, order = job.pooled(stem)
        shots = int(counts.sum())
        entry: dict[str, Any] = {
            "copies": names,
            "kept_shots": shots,
            "measured_on": order,
            "marked": marks[stem],
            "raw_marked": r6(pooled[stem][0]),
            "corrected_marked": r6(fits[stem]["corrected"]),
            "corrected_marked_se": r6(fits[stem]["corrected_se"]),
            "predicted_marked": prediction["arms"][names[0]].get("predicted_marked"),
            "most_frequent": outcome_key(int(np.argmax(counts)), 3),
        }
        if len(names) > 1:
            freqs = [float(job.counts[n][outcome_index(marks[stem])]) / float(job.counts[n].sum()) for n in names]
            positions = [job.names.index(n) for n in names]
            entry["copy_frequencies"] = [r6(v) for v in freqs]
            entry["copy_positions"] = positions
            entry["copy_slope_per_position"] = r6(float(np.polyfit(positions, freqs, 1)[0]))
        arms[stem] = entry
    m011 = {stem: arms[stem]["most_frequent"] for stem in stems if marks[stem] == "011"}
    decisions["bit_order"] = {
        "rule": "the Grover arms keep the retained run's bit order: the most frequent outcome of m011 arms is 011",
        "m011_most_frequent": m011,
        "holds": all(value == "011" for value in m011.values()),
    }
    exploratory = {
        "arms": arms,
        "role_m011_beside": beside,
        "readout_assignment_diagonal": {outcome_key(c, 3): r6(float(readout.matrix[c, c])) for c in range(8)},
    }
    return decisions, exploratory


def sedenion_row(item: tuple[Job, int, np.ndarray]) -> tuple[dict[str, Any], dict[str, Any]]:
    """The decision of sedenion row m and its exploratory statistics; matrix is the 4-qubit assignment matrix."""
    job, m, matrix = item
    prediction = job.prediction
    width = 4
    order = job.orders[f"ro4-{outcome_key(0, width)}"]
    peak = prediction["arms"][f"s{m}-row-c0"]["row_peak"]
    index = outcome_index(peak)
    arms = {}
    for kind in ("row", "trunc", "id"):
        counts, arm_order = job.pooled(f"s{m}-{kind}")
        if arm_order != order:
            raise AnalysisError(f"{job.directory}: s{m}-{kind} measures in another order than the readout circuits")
        shots = int(counts.sum())
        arms[kind] = (float(counts[index]) / shots, shots, counts)
    (pr, nr, row_counts), (pt, nt, _), (pn, nn, _) = arms["row"], arms["trunc"], arms["id"]
    se_trunc = binomial_se([(pr, nr), (pt, nt)])
    se_null = binomial_se([(pr, nr), (pn, nn)])
    z_trunc, z_null = z_of(pr - pt, se_trunc), z_of(pr - pn, se_null)
    others = np.delete(row_counts, index)
    unique_mode = bool(row_counts[index] > others.max())
    resolved = z_trunc >= Z_RESOLVE and z_null >= Z_RESOLVE and unique_mode
    decision = {
        "row_peak": peak,
        "p_row": r6(pr),
        "p_truncation": r6(pt),
        "p_null": r6(pn),
        "kept_shots": {"row": nr, "truncation": nt, "null": nn},
        "row_minus_truncation": r6(pr - pt),
        "row_minus_truncation_se": r6(se_trunc),
        "row_minus_truncation_z": r6(z_trunc),
        "row_minus_null": r6(pr - pn),
        "row_minus_null_se": r6(se_null),
        "row_minus_null_z": r6(z_null),
        "most_frequent_row_string": outcome_key(int(np.argmax(row_counts)), width),
        "row_peak_is_unique_mode": unique_mode,
        "verdict": "resolved" if resolved else "unresolved",
        "reading": (
            "resolved: the eight-CZ sign oracle keeps its Walsh peak against truncation and null"
            if resolved
            else "unresolved: a row peak within 3 SE of its truncation or null, or not the most frequent string"
        ),
        "predicted": predicted_of(prediction, f"sedenion_{m}")
        | {"row_minus_null_z": prediction["decisions"][f"sedenion_{m}"]["row_minus_null_z"]},
    }
    ideal = prediction["arms"][f"s{m}-row-c0"]["ideal"]
    distribution = row_counts / row_counts.sum()
    model = np.array([prediction["arms"][f"s{m}-row-c0"]["predicted"][outcome_key(c, width)] for c in range(2**width)])
    ideal_vector = np.array([ideal.get(outcome_key(c, width), 0.0) for c in range(2**width)])
    corrected = np.linalg.solve(matrix, distribution)
    detail = {
        "row_distribution": {outcome_key(c, width): r6(float(distribution[c])) for c in range(2**width)},
        "tvd_to_model": r6(0.5 * float(np.abs(distribution - model).sum())),
        "tvd_to_ideal": r6(0.5 * float(np.abs(distribution - ideal_vector).sum())),
        "readout_corrected_row_peak": r6(float(corrected[index])),
        "copy_peak_frequencies": {
            kind: [r6(float(job.counts[n][index]) / float(job.counts[n].sum())) for n in job.copies(f"s{m}-{kind}")]
            for kind in ("row", "trunc", "id")
        },
    }
    return decision, detail


def sedenion_analysis(job: Job) -> tuple[dict[str, Any], dict[str, Any]]:
    width = 4
    ro_names = [f"ro4-{outcome_key(c, width)}" for c in range(2**width)]
    matrix = np.column_stack([job.counts[n] / job.counts[n].sum() for n in ro_names])
    rows = ordered_map(sedenion_row, [(job, m, matrix) for m in ROWS])
    decisions = {f"sedenion_{m}": decision for m, (decision, _) in zip(ROWS, rows, strict=True)}
    exploratory: dict[str, Any] = {f"sedenion_{m}": detail for m, (_, detail) in zip(ROWS, rows, strict=True)}
    exploratory["readout_assignment_diagonal"] = {
        outcome_key(c, width): r6(float(matrix[c, c])) for c in range(2**width)
    }
    return decisions, exploratory


def analyze(run_dirs: list[Path], case_dir: Path = CASE_DIR) -> dict[str, Any]:
    """The analysis record of one or two runs of the case, one per job."""
    jobs: dict[str, Job] = {}
    for run_dir in run_dirs:
        job = read_job(run_dir, case_dir)
        if job.job in jobs:
            raise AnalysisError(f"{run_dir}: a second run of job {job.job}")
        jobs[job.job] = job
    if not jobs:
        raise AnalysisError("no run to analyze")
    decisions: dict[str, Any] = {}
    exploratory: dict[str, Any] = {"note": EXPLORATORY_NOTE}
    if "grover" in jobs:
        d, e = grover_analysis(jobs["grover"])
        decisions.update(d)
        exploratory["grover"] = e
    if "sedenion" in jobs:
        d, e = sedenion_analysis(jobs["sedenion"])
        decisions.update(d)
        exploratory["sedenion"] = e
    sample = next(iter(jobs.values()))
    return {
        "schema": SCHEMA,
        "case": CASE,
        "cases_sha256": sample.run.cases_sha256,
        "prediction_sha256": sample.run.case["prediction_sha256"],
        "calibration_set": sample.prediction["calibration_set"],
        "z_resolve": Z_RESOLVE,
        "runs": {
            name: {
                "run": job.directory.name,
                "job_id": job.run.submission["job_id"],
                "billed_seconds": job.run.billed_seconds,
                "runtime_seconds": (job.run.job.get("metrics") or {}).get("runtime_seconds"),
                "charge": round(job.run.billed_seconds * float(job.run.submission["price_per_second"]), 6),
            }
            for name, job in sorted(jobs.items())
        },
        "not_run": [j for j in JOBS if j not in jobs],
        "decisions": decisions,
        "exploratory": exploratory,
    }


def write_record(record: dict[str, Any], out: Path) -> None:
    out.write_text(json.dumps(record, indent=1, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
