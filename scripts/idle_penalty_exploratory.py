"""Exploratory reanalysis of a collected idle_penalty run, outside the preregistered decisions.

Reads the run through scripts/idle_penalty_report.py (`load`, so the collector and exposure refusals apply) and its
retained report (`idle-penalty-report.json` beside the record), and writes quantities chosen after the data:

- pure-dephasing multipliers per qubit, (1/T2_measured - kappa_1 / 2 T1_reported) / (1/T2_reported - 1/2
  T1_reported) for the Ramsey (free) and echo ladders. The numerator subtracts the measured relaxation half-rate,
  the denominator the reported one. Each carries a first-order error from the multiplier errors alone, treated as
  independent; the shared assignment references and the reported-value uncertainty are not propagated, so the
  cohort band is a fixed-cohort order statistic over point estimates, not a parameter interval;
- the reader's excitation after its train: P1 of the reader in the during arm (mean of the x and y quadratures)
  less its P1 in the ground reference, per probe. It bounds the final population only; a transient population
  during the train is not observable here;
- the shift static ZZ would cause through that final excitation, zz_khz x excitation, for target probes, and its
  correlation with the measured target-probe shift;
- the correlation of pair visibility change with pair shift;
- for each historical run named on the command line, the placed qubits it shares with this run and their values.

Usage:
    "$PYTHON" scripts/idle_penalty_exploratory.py RUN [--historical RUN ...] --out RUN/idle-penalty-exploratory.json
    (add --check to require the retained file to agree with a fresh reanalysis)
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import idle_penalty_report as report  # noqa: E402
import numpy as np  # noqa: E402

import idle_penalty as ip  # noqa: E402

REGION_KEYS = ("kappa_1", "kappa_2star", "kappa_2echo")


def pure_dephasing(entry: dict[str, Any], label: str) -> dict[str, float] | None:
    """Measured over reported pure-dephasing rate for one ladder, or None when the reported rate is not positive."""
    t1, t2 = entry["t1_reported_us"], entry["t2_reported_us"]
    reported = 1.0 / t2 - 1.0 / (2.0 * t1)
    if label not in entry or reported <= 0:
        return None
    measured = entry[label] / t2 - entry["kappa_1"] / (2.0 * t1)
    error = math.hypot(entry[f"{label}_se"] / t2, entry["kappa_1_se"] / (2.0 * t1)) / reported
    return {"value": measured / reported, "se": error}


def layout_qubits(run: Path) -> list[int]:
    record = json.loads((run / "record.json").read_text())
    placed: set[int] = set()
    for group in record["groups"]:
        for replica in group.get("replicas", []):
            placed |= set(replica.get("initial_layout", []))
    return sorted(placed)


def exploratory(run: Path, historical: list[Path]) -> dict[str, Any]:
    retained = json.loads((run / "idle-penalty-report.json").read_text())
    data = report.load(run, predicted=False)
    if retained["identity"]["collect_sha256"] != data["identity"]["collect_sha256"]:
        raise report.RefusedAnalysis("the retained report was made from another collect.json")
    laws, qubits = data["laws"], retained["qubits"]
    dephasing: dict[str, Any] = {}
    for label, key in (("kappa_2star", "free"), ("kappa_2echo", "echo")):
        per_qubit = {q: pure_dephasing(entry, label) for q, entry in qubits.items()}
        values = [v["value"] for v in per_qubit.values() if v is not None]
        dephasing[key] = {
            "per_qubit": per_qubit,
            "cohort_order_statistic": report.median_interval(values),
            "range": [min(values), max(values)],
        }
    excitation: dict[str, float] = {}
    induced, measured_shift = [], []
    for k, pair in enumerate(data["roles"]):
        for probe, qubit in enumerate(pair):
            reader = 1 - probe
            head = ip.probe_prefix(probe)
            during = np.mean([report._p1(laws[f"{head}meas_during_{q}"][k], reader) for q in ip.QUADRATURES])
            excitation[str(qubit)] = float(during) - report._p1(laws["idle_ground"][k], reader)
        target = qubits[str(pair[ip.TARGET])]
        induced.append(target["zz_khz"] * excitation[str(pair[ip.TARGET])])
        measured_shift.append(target["readout"]["shift_khz"])
    pairs = retained["pairs"]
    overlaps = {}
    for past in historical:
        shared = [q for q in layout_qubits(past) if str(q) in qubits]
        overlaps[past.name] = {
            "layout_qubits": layout_qubits(past),
            "shared": {
                str(q): {key: qubits[str(q)].get(key) for key in REGION_KEYS}
                | {
                    "shift_khz": qubits[str(q)]["readout"]["shift_khz"],
                    "dV": qubits[str(q)]["readout"]["dV"],
                    "free_pure_dephasing": dephasing["free"]["per_qubit"][str(q)],
                }
                for q in shared
            },
        }
    return {
        "schema": "idle-penalty-exploratory-v1",
        "identity": retained["identity"],
        "pure_dephasing_multiplier": dephasing,
        "reader_final_excitation": {
            "per_probe": excitation,
            "median": float(np.median(list(excitation.values()))),
            "max": max(excitation.values()),
        },
        "zz_through_final_excitation": {
            "max_abs_khz": float(np.max(np.abs(induced))),
            "correlation_with_measured_shift": float(np.corrcoef(induced, measured_shift)[0, 1]),
        },
        "pair_dV_shift_correlation": float(
            np.corrcoef([p["dV"] for p in pairs], [p["shift_khz"] for p in pairs])[0, 1]
        ),
        "historical_overlap": overlaps,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("run", type=Path)
    parser.add_argument("--historical", type=Path, nargs="*", default=[])
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument(
        "--check",
        action="store_true",
        help="require --out to agree with a fresh reanalysis (idle_penalty_report.replay_differences)",
    )
    args = parser.parse_args(argv)
    try:
        result = exploratory(args.run, args.historical)
    except report.RefusedAnalysis as refusal:
        print(f"refused: {refusal}")
        return 2
    text = json.dumps(result, indent=1, sort_keys=True) + "\n"
    if args.check:
        return report.check_replay(args.out, result)
    args.out.write_text(text)
    for key in ("free", "echo"):
        band = result["pure_dephasing_multiplier"][key]["cohort_order_statistic"]
        print(f"pure dephasing {key}: median {band['median']:.3f} cohort band [{band['low']:.3f}, {band['high']:.3f}]")
    print(f"reader final excitation: {result['reader_final_excitation']}"[:200])
    print(f"zz through final excitation: {result['zz_through_final_excitation']}")
    print(f"pair dV-shift correlation: {result['pair_dV_shift_correlation']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
