"""Per-placement readout-corrected whole-operand nullity of a retained pathion_wide_coset run, and the case's rules.

live_run's ``measured_summary_readout_corrected`` keeps only the mean over placements. The decision rules of the case
need that mean's interval, so this script recomputes the corrected value on every placement: each placement's own
confusion matrices (the execution-start ``placed_qubit_calibration`` of the member's PUB, at the physical qubit that the
archived routed circuit measures into each clbit) invert that placement's laws, the group's summary runs on the
inverted laws, and ``variance.interval`` gives the Student t interval over the placements. The corrected mean agrees
with live_run's pooled value to the 6-decimal rounding of the stored laws, and the script reports the difference.

Usage: "$PYTHON" scripts/pathion_wide_coset_analysis.py RUN_DIR [OTHER_RUN_DIR]   (a directory holding collect.json,
record.json and its archive; a second directory adds the device-agreement rule). Exit 0 when every rule passes.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import qpy
from qiskit.circuit import QuantumCircuit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gororoba_quantum"))

import law_encoding  # noqa: E402
import pathion_parallel_coset as ppc  # noqa: E402
import pathion_wide_coset as pw  # noqa: E402
import run_archive  # noqa: E402
import variance  # noqa: E402

GROUP = "pathion_wide_coset"
OFFSET_PER_BLOCK = 0.05
BLOCKS = {op.key: len(op.blocks()) for op in pw.WIDE_OPERANDS}
TARGET_BAND = {"o64": 0.6, "o128": 1.0}
DIFFERENCE_BAND = {64: 0.5, 128: 0.8}
SEPARATION_FLOOR = {64: 27.0, 128: 55.0}
SELECTOR_BAND = {"n64": 0.05, "n128": 0.10}
PER_BLOCK_BAND = 0.25
VISIBILITY_FLOOR = 0.5


def replica_writers(circuit: QuantumCircuit) -> dict[int, list[int]]:
    """For each placement, the physical qubit that writes clbit 0, 1, 2, 3 of its register ``..._r<k>_c``."""
    writers: dict[int, dict[int, int]] = {}
    for inst in circuit.data:
        if inst.operation.name != "measure":
            continue
        register, index = circuit.find_bit(inst.clbits[0]).registers[0]
        match = re.search(r"_r(\d+)_c$", register.name)
        if match is not None:
            writers.setdefault(int(match.group(1)), {})[index] = circuit.find_bit(inst.qubits[0]).index
    return {replica: [bits[c] for c in sorted(bits)] for replica, bits in sorted(writers.items())}


def confusion(calibration: dict[str, dict[str, float]], qubit: int) -> tuple[float, float]:
    """(P(read 1 | prepared 0), P(read 0 | prepared 1)) of a physical qubit, readout_error for both when absent."""
    values = calibration[str(qubit)]
    if "prob_meas1_prep0" in values and "prob_meas0_prep1" in values:
        return float(values["prob_meas1_prep0"]), float(values["prob_meas0_prep1"])
    return float(values["readout_error"]), float(values["readout_error"])


def placement_summaries(
    entry: dict[str, Any], writers: dict[str, dict[int, list[int]]], *, corrected: bool
) -> list[dict[str, float]]:
    """The group summary on every placement, on the raw laws or on each placement's inverted laws.

    ``writers`` maps a member's PUB name to replica -> physical qubit of each clbit."""
    group = pw.pathion_wide_coset_group()
    measured = {
        name: [np.asarray(law_encoding.dense(d), dtype=float) for d in laws] for name, laws in entry["measured"].items()
    }
    count = len(next(iter(measured.values())))
    summaries = []
    for replica in range(count):
        dist = {}
        for name, laws in measured.items():
            law = laws[replica]
            if corrected:
                executed = entry["executed"][name]
                pairs = [confusion(executed["placed_qubit_calibration"], q) for q in writers[executed["pub"]][replica]]
                law = ppc.invert_readout(law, [p[0] for p in pairs], [p[1] for p in pairs])
            dist[name] = law
        summaries.append(group.summarize(dist))
    return summaries


def intervals(summaries: list[dict[str, float]]) -> dict[str, dict[str, Any]]:
    return {key: variance.interval([s[key] for s in summaries], 0, False) for key in summaries[0]}


def within(stat: dict[str, Any], centre: float, band: float) -> bool:
    return bool(stat["lo"] >= centre - band and stat["hi"] <= centre + band)


def rules(raw: dict[str, dict[str, Any]], corr: dict[str, dict[str, Any]]) -> list[tuple[str, bool, str]]:
    """(rule title, verdict, reading) of every single-run rule of the case."""
    out: list[tuple[str, bool, str]] = []
    for key in BLOCKS:
        bins = raw[f"wide_{key}_bins"]["mean"]
        agree = raw[f"wide_{key}_sign_agreement"]["mean"]
        out.append((f"sign resolution {key}", agree >= bins - 0.5, f"{agree:.2f} of {bins:.0f}"))
    for key, band in TARGET_BAND.items():
        stat, ideal = corr[f"wide_{key}_nullity_estimate"], corr[f"wide_{key}_certified_nullity"]["mean"]
        out.append(
            (f"whole-operand nullity {key}", within(stat, ideal, band), f"{stat['mean']:.3f} of {ideal:.0f} +- {band}")
        )
    for key in ("n64", "n128"):
        stat = corr[f"wide_{key}_nullity_estimate"]
        band = OFFSET_PER_BLOCK * BLOCKS[key]
        out.append((f"null control {key}", within(stat, 0.0, band), f"{stat['mean']:.3f} +- {band:.1f}"))
    for dim in (64, 128):
        stat, ideal = corr[f"wide_d{dim}_target_minus_null"], float(corr[f"wide_o{dim}_certified_nullity"]["mean"])
        out.append(
            (
                f"null-referenced difference d{dim}",
                within(stat, ideal, DIFFERENCE_BAND[dim]),
                f"{stat['mean']:.3f} of {ideal:.0f}",
            )
        )
        mutated = corr[f"wide_m{dim}_nullity_estimate"]
        separation = corr[f"wide_d{dim}_target_minus_mutation"]
        ok = within(mutated, -2.0, TARGET_BAND[f"o{dim}"]) and separation["lo"] >= SEPARATION_FLOOR[dim]
        out.append((f"mutation d{dim}", ok, f"{mutated['mean']:.3f} of -2, separation {separation['mean']:.2f}"))
    for key in BLOCKS:
        worst = max(
            abs(stat["mean"] - corr[name.replace("estimate", "ideal")]["mean"])
            for name, stat in corr.items()
            if name.startswith(f"wide_{key}_k") and name.endswith("_nullity_estimate")
        )
        out.append((f"per-block localization {key}", worst <= PER_BLOCK_BAND, f"worst deviation {worst:.3f}"))
    for key, band in SELECTOR_BAND.items():
        total = sum(
            stat["mean"]
            for name, stat in raw.items()
            if name.startswith(f"wide_{key}_k") and name.endswith("_selector_contrast")
        )
        out.append((f"null selector contrast {key}", abs(total) <= band, f"{total:+.4f} +- {band}"))
    floor = min(
        stat["lo"]
        for name, stat in raw.items()
        if name.startswith("wide_") and name.endswith("_visibility") and "_k" in name
    )
    out.append(("visibility floor", floor > VISIBILITY_FLOOR, f"lowest interval bound {floor:.3f}"))
    return out


def device_agreement(
    first: dict[str, dict[str, Any]], second: dict[str, dict[str, Any]], model_gap: dict[str, float]
) -> list[tuple[str, bool, str]]:
    out = []
    for op in pw.WIDE_OPERANDS:
        key = f"wide_{op.key}_nullity_estimate"
        gap = first[key]["mean"] - second[key]["mean"] - model_gap[key]
        half_widths = (first[key]["hi"] - first[key]["lo"]) / 2 + (second[key]["hi"] - second[key]["lo"]) / 2
        allowed = half_widths + OFFSET_PER_BLOCK * BLOCKS[op.key]
        out.append((f"device agreement {op.key}", abs(gap) <= allowed, f"{gap:+.3f} against {allowed:.3f}"))
    return out


def analyze_run(run: Path) -> dict[str, Any]:
    collect = json.loads((run / "collect.json").read_text())
    entry = next(e for e in collect[1:] if isinstance(e, dict) and e.get("group") == GROUP)
    circuits = {c.name: c for c in qpy.load(run_archive.open_archive(run))}
    writers = {name: replica_writers(c) for name, c in circuits.items()}
    raw = intervals(placement_summaries(entry, writers, corrected=False))
    corr = intervals(placement_summaries(entry, writers, corrected=True))
    pooled = entry["measured_summary_readout_corrected"]
    drift = max(abs(corr[k]["mean"] - pooled[k]) for k in pooled if k in corr and k.endswith("_nullity_estimate"))
    record = json.loads((run / "record.json").read_text())
    model = next(g for g in record["groups"] if g["group"] == GROUP)["summary_readout_corrected"]
    return {"raw": raw, "corrected": corr, "pooled_difference": drift, "model": model, "backend": entry["backend"]}


def main() -> int:
    runs = [analyze_run(Path(arg)) for arg in sys.argv[1:3]]
    failed = False
    for result in runs:
        drift = result["pooled_difference"]
        print(f"{result['backend']}: corrected mean differs from live_run's pooled value by {drift:.2e}")
        for title, ok, reading in rules(result["raw"], result["corrected"]):
            print(f"  {'pass' if ok else 'FAIL'}  {title}: {reading}")
            failed |= not ok
    if len(runs) == 2:
        gap = {
            k: runs[0]["model"][k] - runs[1]["model"][k] for k in runs[0]["model"] if k.endswith("_nullity_estimate")
        }
        for title, ok, reading in device_agreement(runs[0]["corrected"], runs[1]["corrected"], gap):
            print(f"  {'pass' if ok else 'FAIL'}  {title}: {reading}")
            failed |= not ok
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
