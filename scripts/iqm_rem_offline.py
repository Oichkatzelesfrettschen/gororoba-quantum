"""Offline readout mitigation of a retained IQM complex-kernel run, as an exploratory comparison.

The preregistered analysis (iqm_complex_kernel_analyze.py) reads the selector bit's zero count of every circuit
group. This tool applies the single-qubit readout inversion that IQM's REM facility builds on (iqm-error-reduction
is not installed here, so the inversion is written out): with e01 = P(read 1 | prepared 0) and e10 = P(read 0 |
prepared 1) of the selector's physical qubit, the zero fraction p0 of the true state follows from the observed
fraction q0 as p0 = (q0 - e10) / (1 - e01 - e10). The error rates come from the calibration set the run compiled
against (calibration/metrics.json of the run, the heralded variants because the kept shots passed the herald).

The comparison never replaces the preregistered analysis. It reports N_c per operand without and with the inversion,
and the delta, so a note can state how far readout error moves each estimate.

Usage:
    "$PYTHON" scripts/iqm_rem_offline.py RUN_DIR --analysis-root CHECKOUT [--out FILE]
CHECKOUT holds scripts/iqm_complex_kernel_analyze.py and the case (the branch that retains the run).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def invert_zero_fraction(q0: float, e01: float, e10: float) -> float:
    """True zero fraction from the observed one; e01 + e10 must stay below 1."""
    gap = 1.0 - e01 - e10
    if gap <= 0:
        raise ValueError("readout error rates leave no contrast")
    return (q0 - e10) / gap


def readout_rates(metrics: dict[str, Any], qubit: str) -> tuple[float, float]:
    """(e01, e10) of qubit from a calibration quality-metric set, the heralded variant first."""
    values = {o["dut_field"]: float(o["value"]) for o in metrics["observations"]}
    for suffix in (":herald=measure.constant", ""):
        base = f"metrics.ssro.measure.constant.{qubit}"
        e01, e10 = values.get(f"{base}.error_0_to_1{suffix}"), values.get(f"{base}.error_1_to_0{suffix}")
        if e01 is not None and e10 is not None:
            return e01, e10
    raise KeyError(f"no readout error metrics for {qubit}")


def selector_qubits(case_dir: Path, prediction: dict[str, Any]) -> dict[str, str]:
    """Physical qubit of each operand's selector bit: the selector-th qubit of the measure locus of its circuits."""
    cases = json.loads((case_dir / "cases.json").read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    for entry in cases["jobs"][0]["circuits"]:
        operand = Path(entry["file"]).stem.split("-")[0]
        if operand in out:
            continue
        circuit = json.loads((case_dir / entry["file"]).read_text(encoding="utf-8"))
        locus = next(i["locus"] for i in circuit["instructions"] if i["name"] == "measure")
        out[operand] = locus[prediction["operands"][operand]["block"]["data_qubits"]]
    return out


def mitigated(
    pooled: dict[tuple[str, str, str], list[int]], rates: dict[str, tuple[float, float]]
) -> dict[Any, list[float]]:
    out: dict[Any, list[float]] = {}
    for (operand, kind, orientation), (zeros, total) in pooled.items():
        e01, e10 = rates[operand]
        out[(operand, kind, orientation)] = [total * invert_zero_fraction(zeros / total, e01, e10), total]
    return out


def compare(run_dir: Path, root: Path) -> dict[str, Any]:
    sys.path[:0] = [str(root / "scripts"), str(root / "gororoba_quantum")]
    import a5_complex_kernel_decision as decision
    import iqm_complex_kernel_analyze as analyzer

    import iqm_records

    case_dir = root / "results/iqm/cases/a5-complex-kernel-garnet"
    prediction = json.loads((case_dir / "prediction.json").read_text(encoding="utf-8"))
    run = iqm_records.read_run(run_dir)
    pooled = analyzer.tally(run, prediction)["pooled"]
    metrics = json.loads((run_dir / "calibration/metrics.json").read_text(encoding="utf-8"))
    qubits = selector_qubits(case_dir, prediction)
    rates = {operand: readout_rates(metrics, qubit) for operand, qubit in qubits.items()}
    raw = decision.analyze(analyzer.counts_of(pooled))
    corrected = decision.analyze(analyzer.counts_of(mitigated(pooled, rates)))
    rows = {}
    for operand in sorted(raw["estimates"]):
        before, after = raw["estimates"][operand], corrected["estimates"][operand]
        rows[operand] = {
            "selector_qubit": qubits[operand],
            "e01_e10": list(rates[operand]),
            "n_c_raw": before["n_c"],
            "n_c_rem": after["n_c"],
            "n_c_delta": after["n_c"] - before["n_c"],
            "se_n_c_raw": before["se_n_c"],
            "se_n_c_rem": after["se_n_c"],
        }
    return {"run": run_dir.name, "operands": rows, "note": "exploratory; the preregistered analysis keeps its verdict"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("run", type=Path)
    parser.add_argument("--analysis-root", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    report = compare(args.run, args.analysis_root)
    text = json.dumps(report, indent=2, sort_keys=True)
    print(text)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
