"""Per-placement readout-corrected whole-operand nullity of a retained pathion_wide_coset run, and the case's rules.

Each fused PUB carries one arm of one operand and every placement runs a different block of it, so the whole-operand
nullity is the sum over blocks of the block estimates read in one shot. live_run keeps only the pooled mean of the
placement summaries; this script recomputes every placement's block estimate from the stored laws. Each placement's own
confusion matrices (the execution-start ``placed_qubit_calibration`` of the member's PUB, at the physical qubit that the
archived routed circuit measures into each clbit) invert that placement's laws, and the block's own ideal laws (the
group's bodies) score them. A 64-dimensional operand's eight blocks run on two placements each, and a block's estimate
is the mean over its copies.

Interval. A block estimate N_hat is a smooth function of the plus and minus laws, each a multinomial sample of the
PUB's shots; the delta method with the multinomial covariance (M (diag p - p p^T) M^T / shots for the readout inverse
M, the identity for raw laws) gives its variance, the placements are disjoint and the arms are separate PUBs, so
variances add over blocks, and the 95 percent interval is the estimate +- 1.96 standard errors. The decision bands add
the offset allowance for the unmodeled placement-to-placement error. The copy agreement of the 64-dimensional operands
compares the two copies of every block and reports the standardized sum of their differences.

Usage: "$PYTHON" scripts/pathion_wide_coset_analysis.py RUN_DIR [OTHER_RUN_DIR]   (a directory holding collect.json,
record.json and its archive; a second directory adds the device-agreement rule). Exit 0 when every rule passes.
"""

from __future__ import annotations

import json
import math
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

GROUPS = ("pathion_wide_coset", "pathion_wide_coset_d32")
Z95 = 1.959964
OFFSET_PER_BLOCK = 0.05
BLOCKS = {op.key: len(op.blocks()) for op in pw.WIDE_OPERANDS}
TARGET_BAND = {"o64": 0.6, "o128": 1.0}
DIFFERENCE_BAND = {64: 0.5, 128: 0.8}
SEPARATION_FLOOR = {64: 27.0, 128: 55.0}
SELECTOR_BAND = {"n64": 0.05, "n128": 0.10}
PER_BLOCK_BAND = 0.25
VISIBILITY_FLOOR = 0.5
COPY_Z_LIMIT = 3.0
STEP = 1e-7


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


def readout_matrix(e01: list[float], e10: list[float]) -> np.ndarray:
    """The 16 x 16 inverse of the placement's confusion channels, column j the inverse applied to outcome j."""
    return np.column_stack([ppc.invert_readout(np.eye(16)[j], e01, e10) for j in range(16)])


def _law_values(plus: np.ndarray, minus: np.ndarray, ideal_plus: np.ndarray, ideal_minus: np.ndarray) -> np.ndarray:
    values = pw.block_values(plus, minus, ideal_plus, ideal_minus)
    return np.array([values["nullity_estimate"], values["visibility"], values["selector_contrast"]])


def block_reading(
    laws: tuple[np.ndarray, np.ndarray],
    ideals: tuple[np.ndarray, np.ndarray],
    shots: tuple[int, int],
    inverse: tuple[np.ndarray, np.ndarray] | None,
) -> dict[str, Any]:
    """One placement's block: N_hat, visibility and selector contrast with delta-method variances, and its signs.

    laws are the observed laws (the multinomial samples); with inverse they are inverted first and carry the
    covariance of the inverted law."""
    raw = [np.asarray(law, dtype=float) for law in laws]
    matrices = inverse if inverse is not None else (np.eye(16), np.eye(16))
    used = [m @ law for m, law in zip(matrices, raw, strict=True)]
    values = _law_values(used[0], used[1], ideals[0], ideals[1])
    jacobian = np.zeros((3, 32))
    for index in range(32):
        step = np.zeros(32)
        step[index] = STEP
        up = _law_values(used[0] + step[:16], used[1] + step[16:], ideals[0], ideals[1])
        down = _law_values(used[0] - step[:16], used[1] - step[16:], ideals[0], ideals[1])
        jacobian[:, index] = (up - down) / (2.0 * STEP)
    covariance = np.zeros((32, 32))
    for arm, (law, matrix, count) in enumerate(zip(raw, matrices, shots, strict=True)):
        block = matrix @ (np.diag(law) - np.outer(law, law)) @ matrix.T / count
        covariance[16 * arm : 16 * arm + 16, 16 * arm : 16 * arm + 16] = block
    variance = np.einsum("ij,jk,ik->i", jacobian, covariance, jacobian)
    full = pw.block_values(used[0], used[1], ideals[0], ideals[1])
    return {
        "nullity": float(values[0]),
        "nullity_variance": float(variance[0]),
        "visibility": float(values[1]),
        "visibility_variance": float(variance[1]),
        "selector": float(values[2]),
        "selector_variance": float(variance[2]),
        "sign_agreement": full["sign_agreement"],
        "ideal": full["nullity_ideal"],
        "bins": float(1 << 3),
    }


def placement_readings(
    entry: dict[str, Any], writers: dict[str, dict[int, list[int]]], group: Any, *, corrected: bool
) -> dict[str, list[dict[str, Any]]]:
    """Every placement's block reading of every operand, by operand key, in placement order; the 32-dimensional
    reference block of the d32 group is under the key ``ref32_<operand>``, one reading per operand's PUB pair."""
    measured = {
        name: [np.asarray(law_encoding.dense(d), dtype=float) for d in laws] for name, laws in entry["measured"].items()
    }
    bodies = {member.name: member.replica_bodies or () for member in group.members}
    ideal = {name: law for name, _, law in group.body_templates}
    out: dict[str, list[dict[str, Any]]] = {}
    for op in pw.WIDE_OPERANDS:
        plus, minus = pw.member_name(op, "plus"), pw.member_name(op, "minus")
        count = len(measured[plus])
        if count != len(bodies[plus]) or len(measured[minus]) != count:
            raise ValueError(f"{op.key}: {count} measured placements for {len(bodies[plus])} bodies")
        for placement in range(count):
            laws, shots, inverse = [], [], []
            for name in (plus, minus):
                executed = entry["executed"][name]
                laws.append(measured[name][placement])
                shots.append(int(executed["shots"]))
                if corrected:
                    pairs = [
                        confusion(executed["placed_qubit_calibration"], q) for q in writers[executed["pub"]][placement]
                    ]
                    inverse.append(readout_matrix([p[0] for p in pairs], [p[1] for p in pairs]))
            reading = block_reading(
                (laws[0], laws[1]),
                (ideal[bodies[plus][placement]], ideal[bodies[minus][placement]]),
                (shots[0], shots[1]),
                (inverse[0], inverse[1]) if corrected else None,
            )
            if placement < pw.PLACEMENTS:
                block = op.block_at(placement)
                reading |= {"placement": placement, "block": pw.block_prefix(op, block)}
                out.setdefault(op.key, []).append(reading)
            else:
                out.setdefault(f"ref32_{op.key}", []).append(reading | {"placement": placement, "block": "ref32"})
    return out


def reading_stat(mean: float, variance: float) -> dict[str, Any]:
    """A reading with its standard error and the 95 percent normal interval of the delta method."""
    se = math.sqrt(max(variance, 0.0))
    return {"mean": mean, "se": se, "lo": mean - Z95 * se, "hi": mean + Z95 * se}


def block_means(readings: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Per block: the mean over its copies of every reading and the variance of that mean."""
    by_block: dict[str, list[dict[str, Any]]] = {}
    for reading in readings:
        by_block.setdefault(reading["block"], []).append(reading)
    out: dict[str, dict[str, Any]] = {}
    for block, rows in by_block.items():
        copies = len(rows)
        out[block] = {
            "copies": copies,
            **{
                key: float(np.mean([r[key] for r in rows]))
                for key in ("nullity", "visibility", "selector", "sign_agreement", "ideal", "bins")
            },
            **{
                f"{key}_variance": float(sum(r[f"{key}_variance"] for r in rows) / copies**2)
                for key in ("nullity", "visibility", "selector")
            },
        }
    return out


def operand_stats(readings: dict[str, list[dict[str, Any]]]) -> dict[str, dict[str, Any]]:
    """The summary keys of the case's rules, each a stat: per-block and whole-operand values and the differences."""
    out: dict[str, dict[str, Any]] = {}
    blocks = {key: block_means(rows) for key, rows in readings.items() if not key.startswith("ref32_")}
    for op in pw.WIDE_OPERANDS:
        parts = blocks[op.key]
        tag = f"wide_{op.key}"
        for block, row in parts.items():
            out[f"{block}_nullity_estimate"] = reading_stat(row["nullity"], row["nullity_variance"])
            out[f"{block}_nullity_ideal"] = reading_stat(row["ideal"], 0.0)
            out[f"{block}_visibility"] = reading_stat(row["visibility"], row["visibility_variance"])
            out[f"{block}_selector_contrast"] = reading_stat(row["selector"], row["selector_variance"])
            out[f"{block}_sign_agreement"] = reading_stat(row["sign_agreement"], 0.0)
        out[f"{tag}_nullity_estimate"] = reading_stat(
            sum(r["nullity"] for r in parts.values()), sum(r["nullity_variance"] for r in parts.values())
        )
        out[f"{tag}_nullity_ideal"] = reading_stat(sum(r["ideal"] for r in parts.values()), 0.0)
        out[f"{tag}_certified_nullity"] = reading_stat(float(op.nullity), 0.0)
        out[f"{tag}_selector_contrast_sum"] = reading_stat(
            sum(r["selector"] for r in parts.values()), sum(r["selector_variance"] for r in parts.values())
        )
        out[f"{tag}_sign_agreement"] = reading_stat(sum(r["sign_agreement"] for r in parts.values()), 0.0)
        out[f"{tag}_bins"] = reading_stat(sum(r["bins"] for r in parts.values()), 0.0)
        out[f"{tag}_visibility_mean"] = reading_stat(
            float(np.mean([r["visibility"] for r in parts.values()])),
            sum(r["visibility_variance"] for r in parts.values()) / len(parts) ** 2,
        )
    for dim in (64, 128):
        for other, name in (("n", "null"), ("m", "mutation")):
            target, control = blocks[f"o{dim}"], blocks[f"{other}{dim}"]
            variance = sum(
                target[b]["nullity_variance"] + control[c]["nullity_variance"]
                for b, c in zip(target, control, strict=True)
            )
            mean = sum(target[b]["nullity"] - control[c]["nullity"] for b, c in zip(target, control, strict=True))
            out[f"wide_d{dim}_target_minus_{name}"] = reading_stat(mean, variance)
    return out


def copy_agreement(readings: dict[str, list[dict[str, Any]]]) -> list[tuple[str, bool, str]]:
    """Report-only reading of the 64-dimensional operands: the sum over blocks of copy A minus copy B of N_hat,
    over its standard error, which the shot-noise interval must cover for its bands to hold."""
    out = []
    for op in pw.WIDE_OPERANDS:
        count = len(op.blocks())
        if count == pw.PLACEMENTS:
            continue
        rows = readings[op.key]
        first, second = rows[:count], rows[count : 2 * count]
        difference = sum(a["nullity"] - b["nullity"] for a, b in zip(first, second, strict=True))
        variance = sum(a["nullity_variance"] + b["nullity_variance"] for a, b in zip(first, second, strict=True))
        z = difference / math.sqrt(variance) if variance > 0 else 0.0
        out.append(
            (f"copy agreement {op.key}", abs(z) <= COPY_Z_LIMIT, f"copy A - copy B {difference:+.3f}, z {z:+.2f}")
        )
    return out


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
    entry = next(e for e in collect[1:] if isinstance(e, dict) and e.get("group") in GROUPS)
    group = pw.pathion_wide_coset_group(reference=entry["group"] == GROUPS[1])
    circuits = {c.name: c for c in qpy.load(run_archive.open_archive(run))}
    writers = {name: replica_writers(c) for name, c in circuits.items()}
    raw_readings = placement_readings(entry, writers, group, corrected=False)
    corr_readings = placement_readings(entry, writers, group, corrected=True)
    raw, corr = operand_stats(raw_readings), operand_stats(corr_readings)
    pooled = entry["measured_summary_readout_corrected"]
    drift = max(abs(corr[k]["mean"] - pooled[k]) for k in pooled if k in corr and k.endswith("_nullity_estimate"))
    record = json.loads((run / "record.json").read_text())
    model = next(g for g in record["groups"] if g["group"] == entry["group"])["summary_readout_corrected"]
    return {
        "raw": raw,
        "corrected": corr,
        "readings": corr_readings,
        "pooled_difference": drift,
        "model": model,
        "backend": entry["backend"],
        "group": entry["group"],
    }


def report_readings(result: dict[str, Any]) -> list[str]:
    """Per-placement lines (block, corrected N_hat with its standard error, visibility) and the report-only ratio."""
    lines = []
    for key, rows in result["readings"].items():
        for row in rows:
            lines.append(
                f"  placement {row['placement']:2d} {key:>9} {row['block']:>14}: N_hat {row['nullity']:+.3f}"
                f" +- {math.sqrt(max(row['nullity_variance'], 0.0)):.3f}, visibility {row['visibility']:.3f}"
            )
    corr = result["corrected"]
    ratio = corr["wide_o128_nullity_estimate"]["mean"] / corr["wide_o64_nullity_estimate"]["mean"]
    lines.append(f"  report-only: o128 / o64 nullity ratio {ratio:.3f} (ideal {60 / 28:.3f})")
    return lines


def model_gap(first: dict[str, Any], second: dict[str, Any]) -> tuple[dict[str, float], list[str]]:
    """Model nullity-estimate gap between two devices over the estimates both carry, and the estimates only one carries
    (a reference PUB planned on one device and dropped from the other's plan)."""
    keys = {k for k in first if k.endswith("_nullity_estimate")}
    other = {k for k in second if k.endswith("_nullity_estimate")}
    return {k: first[k] - second[k] for k in sorted(keys & other)}, sorted(keys ^ other)


def main() -> int:
    runs = [analyze_run(Path(arg)) for arg in sys.argv[1:3]]
    failed = False
    for result in runs:
        drift = result["pooled_difference"]
        print(f"{result['backend']}: corrected mean differs from live_run's pooled value by {drift:.2e}")
        for title, ok, reading in rules(result["raw"], result["corrected"]):
            print(f"  {'pass' if ok else 'FAIL'}  {title}: {reading}")
            failed |= not ok
        for title, ok, reading in copy_agreement(result["readings"]):
            print(f"  report {'ok  ' if ok else 'WIDE'}  {title}: {reading}")
        for line in report_readings(result):
            print(line)
    if len(runs) == 2:
        gap, unmatched = model_gap(runs[0]["model"], runs[1]["model"])
        for key in unmatched:
            print(f"  report  device agreement: {key} is planned on one device only and left out")
        for title, ok, reading in device_agreement(runs[0]["corrected"], runs[1]["corrected"], gap):
            print(f"  {'pass' if ok else 'FAIL'}  {title}: {reading}")
            failed |= not ok
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
