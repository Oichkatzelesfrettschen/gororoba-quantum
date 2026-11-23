"""Analysis of a run of results/iqm/cases/grover-plane-mirrored, built by scripts/iqm_grover_plane_case.py.

The run enters through garnet_followup_analysis.read_job (the shared record checks, the case and prediction digests, the
calibration set and the measurement order; a garnet:mock run is refused). The record binds every circuit's file digest
and position to its counts and applies the preregistered rule of grover_plane_decision to the mirror pairs.

Admission. Beyond read_job: the depth arms and the readout preparations are images of one another about the job's
center; every copy of a depth carries one circuit (14 CZ per iteration) and the four depths carry four circuits. The
response tables are not read from a file: the analysis rebuilds the noisy plane response from the circuit files the run
carries and the calibration copy beside them (grover_plane_sim.Response) and refuses a run whose response digest or
model
probabilities differ from prediction.json, so a later change of the builder cannot change what a retained run reads.

Readout. Each preparation runs on both sides of the center; its marked fraction is the mean of the two sides with equal
weights, so a drift linear in position cancels from the row whatever the kept shots of each side. The eight rows and the
model's depth distributions (decisions.readout.q) correct the four depth frequencies to the model's readout and supply
the common-mode covariance. Three gates read "not evaluated": a preparation keeps under half its planned shots, the
two sides of the readout block differ over all eight outcomes of each preparation by more than the 0.99 chi-square
quantile, or a corrected frequency moves by more than the tolerance.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

import numpy as np

import garnet_followup_analysis as followup
import grover_plane_decision as decision
import grover_plane_sim as sim
import iqm_records
from garnet_followup_analysis import AnalysisError

CASE = "grover-plane-mirrored"
JOBS = ("grover",)
SCHEMA = "iqm-grover-plane-analysis-v1"
CASE_DIR = iqm_records.ROOT / "results" / "iqm" / "cases" / CASE
CZ_PER_ITERATION = 14
MARKS = ("101", "011")
ARM = re.compile(r"m(101|011)-k([1-4])-c(\d+)")
READOUT = re.compile(r"ro-[01]{3}(-m)?")


def normalized_sha256(circuit: dict[str, Any]) -> str:
    return iqm_records.sha256(json.dumps({**circuit, "name": ""}, sort_keys=True).encode())


def cz_count(circuit: dict[str, Any]) -> int:
    return sum(op["name"] == "cz" for op in circuit["instructions"])


def rounded(x: Any) -> Any:
    if isinstance(x, dict):
        return {k: rounded(v) for k, v in x.items()}
    if isinstance(x, np.ndarray):
        return rounded(x.tolist())
    if isinstance(x, (list, tuple)):
        return [rounded(v) for v in x]
    if isinstance(x, (bool, np.bool_)):
        return bool(x)
    if isinstance(x, (int, np.integer)):
        return int(x)
    if isinstance(x, (float, np.floating)):
        return None if math.isnan(float(x)) else round(float(x), 9)
    return x


def response_digest(response: sim.Response, plan: dict[str, Any]) -> str:
    table = [[list(response.centered(s, e)) for e in plan["eps"]] for s in plan["s"]]
    return hashlib.sha256(json.dumps(rounded(table)).encode()).hexdigest()


def sides_chi2(a: np.ndarray, b: np.ndarray) -> tuple[float, int]:
    """Two-sample chi-square of the outcome counts of the two sides of one preparation."""
    na, nb = float(a.sum()), float(b.sum())
    cells = (a + b) > 0
    stat = np.sum((a[cells] * np.sqrt(nb / na) - b[cells] * np.sqrt(na / nb)) ** 2 / (a[cells] + b[cells]))
    return float(stat), int(cells.sum()) - 1


def analyze(run_dir: Path, case_dir: Path = CASE_DIR) -> dict[str, Any]:
    job = followup.read_job(run_dir, case_dir, case=CASE, jobs=JOBS)
    arms = job.prediction["arms"]
    plan_all = job.prediction["decisions"]
    total = len(job.names)
    files = {Path(c["file"]).stem: c for c in job.run.row["circuits"]}
    pairs_at: dict[str, dict[int, dict[int, tuple[int, int]]]] = {m: {} for m in MARKS}
    circuits: dict[str, dict[int, dict[str, Any]]] = {m: {} for m in MARKS}
    digests: dict[tuple[str, int], set[str]] = {}
    readouts: dict[int, list[tuple[int, np.ndarray]]] = {}
    table: list[dict[str, Any]] = []
    kinds: list[str] = []
    for position, name in enumerate(job.names):
        if arms[name]["position"] != position:
            raise AnalysisError(f"{run_dir}: {name} runs at position {position}, not {arms[name]['position']}")
        circuit = json.loads((run_dir / files[name]["file"]).read_text(encoding="utf-8"))
        row: dict[str, Any] = {"position": position, "name": name, "sha256": files[name]["sha256"]}
        arm = ARM.fullmatch(name)
        if arm is None:
            if READOUT.fullmatch(name) is None:
                raise AnalysisError(f"{run_dir}: circuit {name} is neither a depth copy nor a readout preparation")
            kinds.append("readout")
            prepared = followup.outcome_index(name.removeprefix("ro-").removesuffix("-m"))
            readouts.setdefault(prepared, []).append((position, job.counts[name]))
            table.append(row)
            continue
        mark, k = arm[1], int(arm[2])
        if arms[name]["iterations"] != k or arms[name]["marked"] != mark or cz_count(circuit) != CZ_PER_ITERATION * k:
            raise AnalysisError(f"{run_dir}: {name} is not the line-native Grover of mark {mark} at depth {k}")
        digest = normalized_sha256(circuit)
        digests.setdefault((mark, k), set()).add(digest)
        circuits[mark].setdefault(k, circuit)
        counts = job.counts[name]
        pairs_at[mark].setdefault(k, {})[position] = (int(counts[followup.outcome_index(mark)]), int(counts.sum()))
        kinds.append(f"{mark} depth {k}")
        table.append(
            row
            | {
                "mark": mark,
                "depth": k,
                "circuit_sha256": digest,
                "marked": pairs_at[mark][k][position][0],
                "kept_shots": int(counts.sum()),
            }
        )
    if any(len(d) != 1 for d in digests.values()) or len({next(iter(d)) for d in digests.values()}) != len(digests):
        raise AnalysisError(f"{run_dir}: the copies of a depth do not share one circuit, or two depths share one")
    if kinds != kinds[::-1]:
        raise AnalysisError(f"{run_dir}: the job's arms are not images of one another about its center")
    gate = plan_all["gate"]
    if sorted(readouts) != list(range(8)) or any(
        len(v) != 2 or v[0][0] + v[1][0] != total - 1 for v in readouts.values()
    ):
        raise AnalysisError(f"{run_dir}: the readout preparations are not all eight, each at mirrored positions")
    floor = decision.COPY_FLOOR * float(gate["planned_kept_per_copy"])
    sides = [(min(readouts[j])[1], max(readouts[j])[1]) for j in range(8)]
    lost = any(a.sum() < floor or b.sum() < floor for a, b in sides)
    stat, dof = 0.0, 0
    for a, b in sides:
        s, d = sides_chi2(a, b)
        stat, dof = stat + s, dof + d
    calibration_dir = (
        run_dir / "calibration" if (run_dir / "calibration" / "metrics.json").exists() else case_dir / "calibration"
    )
    import iqm_sim

    cal = iqm_sim.Calibration.from_directory(calibration_dir)
    if cal.set_id != job.prediction["calibration_set"]:
        raise AnalysisError(f"{run_dir}: the calibration copy is set {cal.set_id}, not the prediction's")
    path = followup_path(job)
    delta = float(plan_all["rule"]["delta_resolve"])
    decisions: dict[str, Any] = {}
    readout_record: dict[str, Any] = {}
    fits: dict[str, dict[str, Any]] = {}
    for mark in MARKS:
        block = plan_all if mark == "101" else plan_all["mark_011"]
        plan = block["readout"]
        r_model = np.asarray(plan["r_model"], dtype=float)
        marked_at = int(plan["marked_index"])
        r_hat, r_var = np.zeros(8), np.zeros(8)
        for j, (a, b) in enumerate(sides):
            r_hat[j], r_var[j] = decision.pair_mean(
                ((int(a[marked_at]), int(a.sum())), (int(b[marked_at]), int(b.sum())))
            )
        q = np.asarray(plan["q"], dtype=float)
        shift = q @ (r_hat - r_model)
        readout_cov = (q * r_var) @ q.T
        reason = ""
        if lost:
            reason = "not evaluated: a readout preparation kept fewer than half its planned shots"
        elif stat > float(decision.stats.chi2.isf(decision.ALPHA, dof)):
            reason = "not evaluated: the two sides of the readout block differ by more than their scatter"
        elif float(np.max(np.abs(shift))) > float(plan["tolerance"]):
            reason = "not evaluated: the job's readout departs from the model's by more than the tolerance"
        response = sim.Response(circuits[mark], cal, path, mark)
        if response_digest(response, block["response"]) != block["response"]["sha256"]:
            raise AnalysisError(
                f"{run_dir}: the mark {mark} response rebuilt from the run's circuits differs from prediction.json"
            )
        model = response.probabilities(1.0, 1.0, 0.0)
        if float(np.max(np.abs(model - np.asarray(block["model_probabilities"])))) > 2e-9:
            raise AnalysisError(f"{run_dir}: the rebuilt mark {mark} model probabilities differ from prediction.json")
        pairs: dict[int, list[Any]] = {}
        for k in sorted(pairs_at[mark]):
            pairs[k] = []
            for position in sorted(pairs_at[mark][k]):
                mirror = total - 1 - position
                if position < mirror:
                    if mirror not in pairs_at[mark][k]:
                        raise AnalysisError(
                            f"{run_dir}: the mark {mark} depth {k} copy at {position} has no image at {mirror}"
                        )
                    pairs[k].append((pairs_at[mark][k][position], pairs_at[mark][k][mirror]))
        fitter = decision.Fitter(response)
        out = decision.read_pairs(fitter, pairs, shift, readout_cov, float(gate["planned_kept_per_copy"]), delta)
        if reason:
            out["departure_before"] = out.get("departure")
            out["departure"] = reason
        decisions[mark] = out
        fits[mark] = out
        readout_record[mark] = {
            "marked_row": rounded(r_hat),
            "model_marked_row": rounded(r_model),
            "frequency_shift": rounded(shift),
            "passed": not reason,
        }
    contrast_block: dict[str, Any] = {"reading": "not evaluated: a mark's rotation fit is missing"}
    a_fit, b_fit = fits["101"], fits["011"]
    if "rotation" in a_fit and "rotation" in b_fit:
        contrast_block = decision.contrast(
            a_fit["rotation"]["eps"],
            a_fit["rotation_se"].get("eps", float("nan")),
            b_fit["rotation"]["eps"],
            b_fit["rotation_se"].get("eps", float("nan")),
            float(plan_all["contrast"]["ratio_prx"]),
        )
    return {
        "schema": SCHEMA,
        "case": CASE,
        "run": {
            "job_id": job.run.submission["job_id"],
            "qc": job.run.submission["qc"],
            "cases_sha256": job.run.cases_sha256,
            "prediction_sha256": job.run.case["prediction_sha256"],
            "calibration_set": job.prediction["calibration_set"],
        },
        "readout": {**readout_record, "sides_chi2": round(stat, 4), "sides_dof": dof},
        "circuits": table,
        "decisions": rounded(decisions),
        "contrast": rounded(contrast_block),
        "mechanism_attribution": {
            "note": "a reading beside the departure; it decides nothing",
            "eps_per_unit": plan_all["mechanism_slopes"],
        },
    }


def followup_path(job: followup.Job) -> list[str]:
    return list(job.prediction["forward_path"])


def write_record(record: dict[str, Any], out: Path) -> None:
    out.write_text(json.dumps(record, indent=1, sort_keys=True, default=float) + "\n", encoding="utf-8")
