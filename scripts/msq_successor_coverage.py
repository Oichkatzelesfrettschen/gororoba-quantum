"""Calibration coverage of a measurement-sequence successor binding run against its null's rehearsal record.

``REHEARSAL_DIR RUN_DIR --factor F`` exits 0 when RUN_DIR plans the rehearsal's family at the rehearsal's layout width
and every layout qubit of RUN_DIR lies inside the calibration domain the null sampled; it prints every violation and
exits 1 otherwise, and 2 on a record it cannot read. A replicate of the null draws each qubit's calibration from the
rehearsal layout's (msq_successor_null_batch.draw_replicate), so the domain is that layout's range of each quantity:

- T1, T2 and the sx error stay within a factor F of the same qubit's value in the rehearsal snapshot (a drifted qubit
  leaves the domain) and within the rehearsal layout's range widened by F (a qubit the layout rule newly places
  stays inside it).
- Each readout assignment error (prob_meas1_prep0, prob_meas0_prep1) stays at or below F times the rehearsal
  layout's largest. The backend re-estimates these at every calibration from a few thousand shots, in steps of
  1/4096, and the layout rule ranks qubits by them, so a per-qubit ratio reads shot noise (0 to a step and back); a
  smaller error lowers the binomial variance every screen reads in-job.

The design states the rule (docs/design/measurement-sequence-envelope-successor.md, "Null calibration", Coverage).
``scripts/approved_run.sh --check`` runs it from gororoba_quantum/ with RUN set to the binding dry run's directory, so
a refusal sends nothing.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

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


def violations(rehearsal_dir: Path, run_dir: Path, factor: float) -> list[str]:
    """Every coverage violation of the run against the rehearsal, empty when the run lies inside."""
    if not factor > 1.0:
        raise ValueError(f"the factor must exceed 1, got {factor}")
    rehearsal, rehearsal_properties, _ = nl.load_snapshot(rehearsal_dir)
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
    pool = [calibration(rehearsal_properties, int(q)) for q in rehearsal["family_configuration"]["qubits"]]
    span = {name: (min(c[name] for c in pool) / factor, max(c[name] for c in pool) * factor) for name in QUANTITIES}
    for qubit in run_qubits:
        live, before = calibration(run_properties, qubit), calibration(rehearsal_properties, qubit)
        for name in DRIFTING:
            ratio = live[name] / before[name] if before[name] > 0 else float("inf")
            if not 1.0 / factor <= ratio <= factor:
                found.append(
                    f"q{qubit} {name} {live[name]:.6g} is {ratio:.3g} x its rehearsal value {before[name]:.6g}"
                )
            low, high = span[name]
            if not low <= live[name] <= high:
                found.append(
                    f"q{qubit} {name} {live[name]:.6g} lies outside the widened rehearsal range [{low:.6g}, {high:.6g}]"
                )
        for name in READOUT:
            if live[name] > span[name][1]:
                found.append(
                    f"q{qubit} {name} {live[name]:.6g} exceeds the widened rehearsal maximum {span[name][1]:.6g}"
                )
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("rehearsal_dir", type=Path, help="the dry-run record the null ran on")
    parser.add_argument("run_dir", type=Path, help="the binding dry run's record directory")
    parser.add_argument("--factor", type=float, required=True, help="the largest allowed ratio, above 1")
    args = parser.parse_args(argv)
    try:
        found = violations(args.rehearsal_dir, args.run_dir, args.factor)
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
