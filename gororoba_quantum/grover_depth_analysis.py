"""Analysis of a run of results/iqm/cases/grover-fourth-depth-mirrored, the Garnet fourth-depth Grover case built by
scripts/iqm_grover_fourth_depth.py (the case's CASE.md, "Preregistered decision rule").

analyze reads the run of job "grover" through garnet_followup_analysis.read_job (the shared record checks of
iqm_records.read_run, the case, the prediction digest, the calibration set and the measurement order) and writes one
record, schema SCHEMA, whose "decisions" apply grover_depth_families.read_copies with the gate that the case's
prediction.json fixes (decisions.heterogeneity).

Admission. Beyond read_job: the circuits of the run sit at the positions the prediction names, in a layout whose
depth arms are images of one another about the job's center; every copy of a depth carries one circuit (its file
without the name field has one sha256) with 14 CZ per iteration, and the four depths carry four circuits; the
readout block fills the center. A run on garnet:mock, a run of another case or digest, or a run that breaks one of
these raises AnalysisError (or iqm_records.RecordError for a run directory whose files contradict each other), and
a mock outcome never enters the analysis.

Decisions. The copies of each depth enter as (position, marked count, kept shots) with the marked count read at the
outcome of the case's mark in the prediction's measurement order. Mirror pairs, the heterogeneity gate and the
verdict follow grover_depth_families.read_copies.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import garnet_followup_analysis as followup
import grover_depth_families as families
import iqm_records
from garnet_followup_analysis import AnalysisError

CASE = "grover-fourth-depth-mirrored"
JOBS = ("grover",)
SCHEMA = "iqm-grover-fourth-depth-analysis-v1"
CASE_DIR = iqm_records.ROOT / "results" / "iqm" / "cases" / CASE
MARKED = "101"
CZ_PER_ITERATION = 14
ARM = re.compile(r"m101-k([1-4])-c(\d+)")
READOUT = re.compile(r"ro-[01]{3}")


def normalized_sha256(circuit: dict[str, Any]) -> str:
    """The digest of a circuit file's content without its name: copies of one depth share it."""
    return iqm_records.sha256(json.dumps({**circuit, "name": ""}, sort_keys=True).encode())


def cz_count(circuit: dict[str, Any]) -> int:
    return sum(op["name"] == "cz" for op in circuit["instructions"])


def analyze(run_dir: Path, case_dir: Path = CASE_DIR) -> dict[str, Any]:
    job = followup.read_job(run_dir, case_dir, case=CASE, jobs=JOBS)
    arms = job.prediction["arms"]
    total = len(job.names)
    files = {Path(c["file"]).stem: c for c in job.run.row["circuits"]}
    copies: dict[int, list[families.Copy]] = {k: [] for k in families.DEPTHS}
    table: list[dict[str, Any]] = []
    digests: dict[int, set[str]] = {k: set() for k in families.DEPTHS}
    kinds: list[str] = []
    for position, name in enumerate(job.names):
        if arms[name]["position"] != position:
            raise AnalysisError(
                f"{run_dir}: {name} runs at position {position}, not the prediction's {arms[name]['position']}"
            )
        circuit = json.loads((run_dir / files[name]["file"]).read_text(encoding="utf-8"))
        row: dict[str, Any] = {"position": position, "name": name, "sha256": files[name]["sha256"]}
        arm = ARM.fullmatch(name)
        if arm is None:
            if READOUT.fullmatch(name) is None:
                raise AnalysisError(f"{run_dir}: circuit {name} is neither a depth copy nor a readout preparation")
            kinds.append("readout")
            table.append(row)
            continue
        k = int(arm[1])
        if arms[name]["iterations"] != k or arms[name]["marked"] != MARKED or cz_count(circuit) != CZ_PER_ITERATION * k:
            raise AnalysisError(f"{run_dir}: {name} is not the line-native Grover of mark {MARKED} at depth {k}")
        digest = normalized_sha256(circuit)
        digests[k].add(digest)
        counts = job.counts[name]
        marked, kept = int(counts[followup.outcome_index(MARKED)]), int(counts.sum())
        copies[k].append((position, marked, kept))
        kinds.append(f"depth {k}")
        table.append(row | {"depth": k, "circuit_sha256": digest, "marked": marked, "kept_shots": kept})
    if any(len(d) != 1 for d in digests.values()) or len({next(iter(d)) for d in digests.values()}) != len(
        families.DEPTHS
    ):
        raise AnalysisError(f"{run_dir}: the copies of a depth do not share one circuit, or two depths share one")
    if kinds != kinds[::-1]:
        raise AnalysisError(f"{run_dir}: the job's depth arms are not images of one another about its center")
    gate = job.prediction["decisions"]["heterogeneity"]
    retained = job.prediction["decisions"]["retained"]
    model = families.model_retention(arms)
    decisions = families.read_copies(
        copies,
        total,
        float(gate["planned_kept_per_copy"]),
        model,
        {"geometric_next": retained["geometric_rho_4"], "coherent_next": retained["coherent_rho_4"]},
        gate,
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
        "model_lambda": {str(k): round(x, 6) for k, x in zip(families.DEPTHS, model, strict=True)},
        "circuits": table,
        "decisions": decisions,
    }


def write_record(record: dict[str, Any], out: Path) -> None:
    out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
