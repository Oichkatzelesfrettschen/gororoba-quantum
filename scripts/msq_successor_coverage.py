"""Calibration coverage of a measurement-sequence successor binding run against its null's rehearsal record.

``REHEARSAL_DIR RUN_DIR --factor F`` exits 0 when RUN_DIR plans the rehearsal's family at the rehearsal's layout width
and shot count and its layout's calibration lies inside the domain the null sampled; it prints every violation and
exits 1 otherwise, and 2 on a record it cannot read. A replicate of the null gives each slot a calibration drawn with
replacement from the rehearsal layout's qubits (msq_successor_null_batch.draw_replicate), so the domain is that pool,
not any one qubit's own earlier value, and the shot count is the rehearsal's (every member count is binomial out of it):

- Each live T1, T2 and sx error lies within the rehearsal layout's range widened by F, and the live layout's median
  of each lies within a factor F of the pool's, so a device-wide shift the pool never held refuses. The sx error
  bounds both ways: the analysis's gate-model systematic scales with the reported value
  (measurement_sequence_analysis.SX_SYSTEMATIC), so a lower report narrows the allowance the null calibrated.
- Each readout assignment error (prob_meas1_prep0, prob_meas0_prep1), and the layout's median of each, stays at or
  below F times the pool's. A smaller error lowers the binomial variance every screen reads in-job.

- Each live sx gate length and readout length lies within the pool's range: the null draws them with each slot's
  calibration (msq_successor_null_batch.snapshot_executed), and the analysis reads them as executed durations.
- The run's experiment digest equals the rehearsal's, so the binding run executes the code the null calibrated.

``--null SUMMARY`` (a `scripts/msq_successor_null.py --summarize` file) also refuses unless the summary holds a record
of every null arm on the rehearsal's snapshot, layout width and shots, each with no fire and every target met.

A per-quantity range leaves a joint (T1, T2, readout, sx) combination the pool never held uncovered. The design
states the rule (docs/design/measurement-sequence-envelope-successor.md, "Null calibration", Coverage).
``scripts/approved_run.sh --check`` runs it from gororoba_quantum/ with RUN set to the binding dry run's directory, so
a refusal sends nothing.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import msq_successor_null_batch as nl  # noqa: E402

DRIFTING = ("T1", "T2", "sx_error")
READOUT = ("prob_meas1_prep0", "prob_meas0_prep1")
QUANTITIES = (*DRIFTING, *READOUT)


def calibration(properties: dict[str, object], qubit: int) -> dict[str, float]:
    """The null's drawn quantities of one qubit from a snapshot's backend properties."""
    qubits = properties["qubits"]
    gates = properties["gates"]
    if not isinstance(qubits, list) or not isinstance(gates, list):
        raise ValueError("snapshot properties carry no qubit or gate list")
    values = {item["name"]: float(item["value"]) for item in qubits[qubit]}
    out = {name: values[name] for name in ("T1", "T2", *READOUT)}
    for gate in gates:
        if gate["gate"] == "sx" and gate["qubits"] == [qubit]:
            out["sx_error"] = next(float(p["value"]) for p in gate["parameters"] if p["name"] == "gate_error")
    if "sx_error" not in out:
        raise ValueError(f"the snapshot holds no sx calibration for qubit {qubit}")
    return out


def durations(properties: dict[str, object], qubit: int) -> dict[str, float]:
    """The sx gate length and readout length of one qubit, in the snapshot's ns, which the null draws per slot."""
    qubits = properties["qubits"]
    gates = properties["gates"]
    if not isinstance(qubits, list) or not isinstance(gates, list):
        raise ValueError("snapshot properties carry no qubit or gate list")
    readout = next(float(item["value"]) for item in qubits[qubit] if item["name"] == "readout_length")
    sx = next(
        float(p["value"])
        for gate in gates
        if gate["gate"] == "sx" and gate["qubits"] == [qubit]
        for p in gate["parameters"]
        if p["name"] == "gate_length"
    )
    return {"sx_gate_length": sx, "readout_length": readout}


def null_violations(summary: dict[str, Any], snapshot: str, width: int, shots: int) -> list[str]:
    """Every null arm the summary lacks on this snapshot, width and shots, or holds with a fire or a missed target."""
    found: list[str] = []
    for arm in nl.ARMS:
        records = [
            r
            for r in summary["records"]
            if r["arm"] == arm
            and r["snapshot_sha256"] == snapshot
            and int(r["layout_width"]) == width
            and int(r["shots"]) == shots
        ]
        if not records:
            found.append(f"null arm {arm} has no record on snapshot {snapshot[:16]} at width {width} and {shots} shots")
        for record in records:
            for case, stats in record["cases"].items():
                if stats["fires"] or stats["exposed_fires"]:
                    found.append(f"null arm {arm} case {case} fired")
                missed = sorted(name for name, met in stats["targets"].items() if met is not True)
                if missed:
                    found.append(f"null arm {arm} case {case} missed {', '.join(missed)}")
    return found


def violations(rehearsal_dir: Path, run_dir: Path, factor: float, summary: dict[str, Any] | None = None) -> list[str]:
    """Every coverage violation of the run against the rehearsal, empty when the run lies inside."""
    if not factor > 1.0:
        raise ValueError(f"the factor must exceed 1, got {factor}")
    rehearsal, rehearsal_properties, rehearsal_snapshot = nl.load_snapshot(rehearsal_dir)
    run, run_properties, _ = nl.load_snapshot(run_dir)
    family, width = (
        rehearsal["family_configuration"]["name"],
        int(rehearsal["family_configuration"]["layout_width"]),
    )
    found: list[str] = []
    if run["family_configuration"]["name"] != family:
        found.append(f"family {run['family_configuration']['name']} differs from the rehearsal's {family}")
    run_qubits = [int(q) for q in run["family_configuration"]["qubits"]]
    if len(run_qubits) != width or int(run["family_configuration"]["layout_width"]) != width:
        found.append(f"layout width {len(run_qubits)} differs from the rehearsal's {width}")
    if int(run["shots"]) != int(rehearsal["shots"]):
        found.append(f"shots {int(run['shots'])} differ from the rehearsal's {int(rehearsal['shots'])}")
    if run.get("experiment_digest") != rehearsal.get("experiment_digest"):
        found.append(
            f"experiment digest {run.get('experiment_digest')} differs from the rehearsal's"
            f" {rehearsal.get('experiment_digest')}"
        )
    if summary is not None:
        found.extend(null_violations(summary, rehearsal_snapshot, width, int(rehearsal["shots"])))
    pool = [calibration(rehearsal_properties, int(q)) for q in rehearsal["family_configuration"]["qubits"]]
    live = {qubit: calibration(run_properties, qubit) for qubit in run_qubits}
    for name in QUANTITIES:
        low, high = min(c[name] for c in pool) / factor, max(c[name] for c in pool) * factor
        for qubit, values in live.items():
            if name in DRIFTING and not low <= values[name] <= high:
                found.append(
                    f"q{qubit} {name} {values[name]:.6g} lies outside the widened rehearsal range"
                    f" [{low:.6g}, {high:.6g}]"
                )
            if name in READOUT and values[name] > high:
                found.append(f"q{qubit} {name} {values[name]:.6g} exceeds the widened rehearsal maximum {high:.6g}")
        center = statistics.median(c[name] for c in pool)
        median = statistics.median(values[name] for values in live.values())
        if median > factor * center or (name in DRIFTING and median * factor < center):
            found.append(f"layout median {name} {median:.6g} lies beyond a factor {factor} of the pool's {center:.6g}")
    pool_durations = [durations(rehearsal_properties, int(q)) for q in rehearsal["family_configuration"]["qubits"]]
    for qubit in run_qubits:
        for name, value in durations(run_properties, qubit).items():
            low, high = min(d[name] for d in pool_durations), max(d[name] for d in pool_durations)
            if not low <= value <= high:
                found.append(f"q{qubit} {name} {value:.6g} lies outside the rehearsal range [{low:.6g}, {high:.6g}]")
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("rehearsal_dir", type=Path, help="the dry-run record the null ran on")
    parser.add_argument("run_dir", type=Path, help="the binding dry run's record directory")
    parser.add_argument("--factor", type=float, required=True, help="the largest allowed ratio, above 1")
    parser.add_argument("--null", type=Path, metavar="SUMMARY", help="the null summary that must cover the rehearsal")
    args = parser.parse_args(argv)
    try:
        summary = json.loads(args.null.read_text()) if args.null is not None else None
        found = violations(args.rehearsal_dir, args.run_dir, args.factor, summary)
    except (OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
        print(f"coverage: cannot read the records: {exc}", file=sys.stderr)
        return 2
    for line in found:
        print(f"coverage: {line}")
    if found:
        return 1
    print(f"coverage: {args.run_dir.name} lies inside {args.rehearsal_dir.name} at factor {args.factor}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
