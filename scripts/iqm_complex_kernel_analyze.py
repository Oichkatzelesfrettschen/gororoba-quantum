"""Analysis of a retained Garnet run of the A_5 complex kernel case: run records to the preregistered verdict.

Reads one completed run of results/iqm/cases/a5-complex-kernel-garnet with iqm_records.read_run (the receipt, the digest
of every circuit file, the retained raw files and their shot counts), refuses a run that is not on Garnet (by the
receipt and by the quantum computer id of the job record), whose cases.json or prediction.json differs from the
retained case, or whose compilation
names another calibration set or is missing, rejects a shot that is not a bit or a circuit without the measure key,
tallies the kept shots of each (operand, kind, orientation) at the selector bit of its measure locus and passes the
counts to a5_complex_kernel_decision.analyze. Mock outcomes never enter it.

Usage: "$PYTHON" scripts/iqm_complex_kernel_analyze.py RUN_DIR [--case-dir DIR] [--out FILE]
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import a5_complex_kernel_decision as decision  # noqa: E402
import iqm_records  # noqa: E402

CASE_DIR = ROOT / "results/iqm/cases/a5-complex-kernel-garnet"
QC = "garnet"
JOB = "kernel"
GARNET_ID_FILE = ROOT / "docs/evidence/iqm/qc/garnet/details.json"


def tally(run: iqm_records.Run, prediction: dict[str, Any]) -> dict[str, Any]:
    """Selector-zero and kept counts per circuit file, pooled per (operand, kind, orientation) and per half of the job
    (copies 0 and 1 against 2 and 3)."""
    pooled: dict[tuple[str, str, str], list[int]] = {}
    halves: dict[tuple[str, str, str, int], list[int]] = {}
    kept_total = 0
    for entry, circuit in zip(run.row["circuits"], run.completed_measurements(), strict=True):
        name = Path(entry["file"]).stem
        operand, kind, orientation, copy = name.split("-")
        selector = prediction["operands"][operand]["block"]["data_qubits"]
        shots = circuit.get("m") if isinstance(circuit, dict) else None
        if not isinstance(shots, list):
            raise iqm_records.RecordError(f"{name}: the circuit has no measurement key m")
        if any(
            not isinstance(shot, list) or len(shot) != selector + 1 or any(bit not in (0, 1) for bit in shot)
            for shot in shots
        ):
            raise iqm_records.RecordError(f"{name}: a shot is not {selector + 1} bits of 0 or 1")
        zeros = sum(1 for shot in shots if shot[selector] == 0)
        for table, key in (
            (pooled, (operand, kind, orientation)),
            (halves, (operand, kind, orientation, int(copy) // 2)),
        ):
            row = table.setdefault(key, [0, 0])  # type: ignore[arg-type]
            row[0] += zeros
            row[1] += len(shots)
        kept_total += len(shots)
    return {"pooled": pooled, "halves": halves, "kept": kept_total}


def counts_of(pooled: dict[tuple[str, str, str], list[int]]) -> dict[str, dict[str, decision.Counts]]:
    out: dict[str, dict[str, decision.Counts]] = {}
    for (operand, kind, orientation), _ in sorted(pooled.items()):
        if orientation != "plus":
            continue
        plus, minus = pooled[(operand, kind, "plus")], pooled[(operand, kind, "minus")]
        out.setdefault(operand, {})[kind] = (plus[0], plus[1], minus[0], minus[1])
    return out


def heterogeneity(halves: dict[tuple[str, str, str, int], list[int]]) -> dict[str, float | None]:
    """z of the difference between the arm difference D of the first and the second half of the job, per kind; None
    for a kind whose halves have no spread. The halves are mirror images about the center of the job, so a drift that
    is symmetric about the center leaves this z at zero: the sentinel's inner_outer_z (decision.drift_z) carries it."""
    out: dict[str, float | None] = {}
    kinds = sorted({(o, k) for o, k, _, _ in halves})
    for operand, kind in kinds:
        d = []
        for half in (0, 1):
            plus, minus = halves[(operand, kind, "plus", half)], halves[(operand, kind, "minus", half)]
            d.append(decision.difference((plus[0], plus[1], minus[0], minus[1])))
        spread = d[0][1] + d[1][1]
        out[f"{operand}-{kind}"] = round((d[0][0] - d[1][0]) / math.sqrt(spread), 4) if spread > 0 else None
    return out


def analyze_run(run_dir: Path, case_dir: Path = CASE_DIR) -> dict[str, Any]:
    run = iqm_records.read_run(run_dir)
    if run.submission["qc"] != QC or run.submission["job"] != JOB:
        raise iqm_records.RecordError(
            f"{run_dir}: ran {run.submission['job']} on {run.submission['qc']}, not {JOB} on {QC}"
        )
    if run.results["status"] != "completed":
        raise iqm_records.RecordError(f"{run_dir}: job status {run.results['status']}")
    garnet = json.loads(GARNET_ID_FILE.read_text(encoding="utf-8"))["id"]
    ran_on = (run.job.get("qc") or {}).get("id") if isinstance(run.job.get("qc"), dict) else None
    if ran_on != garnet:
        raise iqm_records.RecordError(f"{run_dir}: the job record names quantum computer {ran_on}, not Garnet {garnet}")
    for name in ("cases.json", "prediction.json"):
        if (run_dir / name).read_bytes() != (case_dir / name).read_bytes():
            raise iqm_records.RecordError(f"{run_dir}/{name} differs from {case_dir.name}/{name}")
    prediction = json.loads((case_dir / "prediction.json").read_text(encoding="utf-8"))
    compilation = run.job.get("compilation")
    if not isinstance(compilation, dict) or "calibration_set_id" not in compilation:
        raise iqm_records.RecordError(f"{run_dir}: the job record holds no compilation calibration set")
    compiled = compilation["calibration_set_id"]
    if compiled != prediction["calibration_set"]:
        raise iqm_records.RecordError(f"{run_dir}: compiled against {compiled}, not {prediction['calibration_set']}")
    counted = tally(run, prediction)
    result = decision.analyze(counts_of(counted["pooled"]))
    predicted_subtracted = {
        name: prediction["operands"][name]["predicted"]["nullity_subtracted"] for name in decision.DISCRIMINATING
    }
    return {
        "schema": "iqm-complex-kernel-analysis-v1",
        "run": run_dir.name,
        "job_id": run.submission["job_id"],
        "calibration_set": compiled,
        "billed_seconds": run.billed_seconds,
        "kept_fraction": counted["kept"] / (run.row["shots"] * len(run.row["circuits"])),
        "analysis": result,
        "predicted_nullity_subtracted": predicted_subtracted,
        "half_to_half_z": heterogeneity(counted["halves"]),
        "inner_outer_z": result["drift_z"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--case-dir", type=Path, default=CASE_DIR)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    text = json.dumps(analyze_run(args.run_dir, args.case_dir), indent=1, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
