"""Per-placement readout-corrected whole-operand nullity of a retained pathion_wide_coset run, and the case's rules.

Each fused PUB carries one arm of one operand and every placement runs a different block of it, so the whole-operand
nullity is the sum over blocks of the block estimates read in one shot. live_run keeps only the pooled mean of the
placement summaries; this script recomputes every placement's block estimate from the stored laws. Each placement's own
confusion matrices (the execution-start ``placed_qubit_calibration`` of the member's PUB, at the physical qubit that the
archived routed circuit measures into each clbit) invert that placement's laws, and the block's own ideal laws (the
group's bodies) score them. A 64-dimensional operand's eight blocks run on two placements each, and a block's estimate
is the mean over its copies.

Interval. A block estimate N_hat is a smooth function of the plus and minus laws, each the empirical law of one PUB's
shots. The delta method gives each shot an influence value, the gradient of the estimate with respect to the observed
law (through the placement's readout inverse) taken at the shot's outcome, so the estimate is its arm's mean influence
plus a constant. The retained raw record of a PUB keeps the aligned bitstrings of every placement register, so the
covariance of the influence values across placements, taken over the PUB's shots, is the covariance of the placements'
estimates; the standard error of any sum or difference of placements (copy mean, whole operand, copy A minus copy B,
visibility mean) is the quadratic form of its weights in that covariance. The plus and minus arms and the operands
are separate PUBs, so their covariances add. The 95 percent interval is the estimate +- 1.96 standard errors. The
marginal column keeps the earlier model that sums per-placement multinomial variances as if placements were
independent; it is report-only, and its diagonal equals the covariance matrix's. The decision bands add the offset
allowance for the unmodeled placement-to-placement error. The copy agreement of the 64-dimensional operands compares the
two copies of every block and reports the standardized sum of their differences.

Usage: "$PYTHON" scripts/pathion_wide_coset_analysis.py RUN_DIR [OTHER_RUN_DIR] [--out FILE]   (a directory holding
collect.json, record.json, its archive and raw/<job_id>/; a second directory of another backend adds the
device-agreement rule; --out writes the analysis record). Exit 0 when every rule passes.
"""

from __future__ import annotations

import argparse
import hashlib
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
QUANTITIES = ("nullity", "visibility", "selector")
LAW_TOLERANCE = 1e-6
SCHEMA = "pathion-wide-coset-analysis-v2"
DECIMALS = 6


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
    covariance of the inverted law. ``gradient`` is the derivative of (N_hat, visibility, selector) with respect to
    the observed plus and minus laws, shape (3, 2, 16), the factor of every shot's influence value."""
    if min(shots) <= 0:
        raise ValueError(f"shot counts must be positive, got {shots}")
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
    gradient = np.stack([jacobian[:, :16] @ matrices[0], jacobian[:, 16:] @ matrices[1]], axis=1)
    return {
        "gradient": gradient,
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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_outcomes(run: Path, entry: dict[str, Any]) -> dict[str, np.ndarray]:
    """Every member's retained shots as integer outcomes, shape (shots, placements): the 4-bit value of the register
    of each placement, read from the PUB's raw record after its SHA-256 matches the job's index.

    A raw record that is missing, altered, or inconsistent with collect.json's laws raises; no marginal fallback
    stands in for it."""
    root = run / "raw" / entry["job_id"]
    index_path = root / "index.json"
    if not index_path.is_file():
        raise FileNotFoundError(f"{index_path}: the retained raw record of the job is required")
    digests = json.loads(index_path.read_text())["files"]
    registers: dict[str, dict[str, Any]] = {}
    for path in sorted(root.glob("pub_*.json")):
        if digests.get(path.name) != sha256(path):
            raise ValueError(f"{path}: SHA-256 differs from the job index")
        body = json.loads(path.read_text())
        registers[body["pub_name"]] = body["registers"]
    out: dict[str, np.ndarray] = {}
    for name, executed in entry["executed"].items():
        if executed["pub"] not in registers:
            raise ValueError(f"{name}: no raw record for {executed['pub']}")
        columns = []
        for placement, law in enumerate(entry["measured"][name]):
            register = registers[executed["pub"]][f"g0_r{placement}_c"]
            if register["num_bits"] != 4 or len(register["bitstrings"]) != executed["shots"]:
                raise ValueError(f"{name} placement {placement}: raw shots differ from the executed count")
            column = np.array([int(bits, 2) for bits in register["bitstrings"]], dtype=np.int64)
            observed = np.bincount(column, minlength=16) / len(column)
            if float(np.abs(observed - np.asarray(law_encoding.dense(law), dtype=float)).max()) > LAW_TOLERANCE:
                raise ValueError(f"{name} placement {placement}: raw shots differ from collect.json's law")
            columns.append(column)
        out[name] = np.stack(columns, axis=1)
    return out


def shot_covariances(
    readings: dict[str, list[dict[str, Any]]], outcomes: dict[str, np.ndarray]
) -> dict[str, np.ndarray]:
    """Per operand key, the covariance across placements of (N_hat, visibility, selector contrast), shape (3, K, K).

    Within one PUB every shot carries all K placement registers, so the influence value of shot s at placement k is
    the gradient of that placement's reading at the outcome the shot recorded; the covariance matrix of those values
    over the shots, divided by the shot count, is the covariance of the placements' estimates in that arm. The two
    arms of an operand are separate PUBs and add."""
    out: dict[str, np.ndarray] = {}
    for op in pw.WIDE_OPERANDS:
        rows = [*readings[op.key], *readings.get(f"ref32_{op.key}", [])]
        placements = np.arange(len(rows))[None, :]
        total = np.zeros((len(QUANTITIES), len(rows), len(rows)))
        for arm, name in enumerate((pw.member_name(op, "plus"), pw.member_name(op, "minus"))):
            shots = outcomes[name]
            if shots.shape[1] != len(rows):
                raise ValueError(f"{name}: {shots.shape[1]} raw placements for {len(rows)} readings")
            gradient = np.stack([row["gradient"][:, arm, :] for row in rows])
            influence = gradient[placements, :, shots]
            centered = influence - influence.mean(axis=0)
            total += np.einsum("skq,slq->qkl", centered, centered) / shots.shape[0] ** 2
        out[op.key] = total
    return out


def reading_stat(mean: float, variance: float, marginal: float | None = None) -> dict[str, Any]:
    """A reading with its standard error and the 95 percent normal interval of the delta method; the marginal
    columns hold the same interval under independent placements (report-only)."""
    se = math.sqrt(max(variance, 0.0))
    se_marginal = se if marginal is None else math.sqrt(max(marginal, 0.0))
    return {
        "mean": mean,
        "se": se,
        "lo": mean - Z95 * se,
        "hi": mean + Z95 * se,
        "marginal_se": se_marginal,
        "marginal_lo": mean - Z95 * se_marginal,
        "marginal_hi": mean + Z95 * se_marginal,
    }


def marginal_view(stats: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """The same stats with the independent-placement interval in lo, hi and se, to evaluate a rule under that model."""
    return {
        key: {**stat, "se": stat["marginal_se"], "lo": stat["marginal_lo"], "hi": stat["marginal_hi"]}
        for key, stat in stats.items()
    }


def block_weights(rows: list[dict[str, Any]]) -> dict[str, np.ndarray]:
    """Per block, the weights over the operand's placement rows of the mean over that block's copies."""
    out: dict[str, np.ndarray] = {}
    for position, row in enumerate(rows):
        out.setdefault(row["block"], np.zeros(len(rows)))[position] = 1.0
    return {block: weight / weight.sum() for block, weight in out.items()}


def _linear(
    rows: list[dict[str, Any]], covariance: np.ndarray, quantity: str, weights: np.ndarray, other: tuple | None = None
) -> dict[str, Any]:
    """Stat of sum_k w_k reading_k (minus the same sum over another operand's rows and covariance)."""
    q = QUANTITIES.index(quantity)
    values = np.array([row[quantity] for row in rows])
    marginal = np.array([row[f"{quantity}_variance"] for row in rows])
    mean = float(weights @ values)
    variance = float(weights @ covariance[q] @ weights)
    marginal_variance = float(weights**2 @ marginal)
    if other is not None:
        rows2, covariance2 = other
        values2 = np.array([row[quantity] for row in rows2])
        marginal2 = np.array([row[f"{quantity}_variance"] for row in rows2])
        mean -= float(weights @ values2)
        variance += float(weights @ covariance2[q] @ weights)
        marginal_variance += float(weights**2 @ marginal2)
    return reading_stat(mean, variance, marginal_variance)


def operand_stats(
    readings: dict[str, list[dict[str, Any]]], covariances: dict[str, np.ndarray]
) -> dict[str, dict[str, Any]]:
    """The summary keys of the case's rules, each a stat: per-block and whole-operand values and the differences.

    A stat is a weighted sum of placement readings; its variance is the quadratic form of the weights in the
    operand's placement covariance (``shot_covariances``), with the independent-placement variance beside it."""
    out: dict[str, dict[str, Any]] = {}
    ops = {
        op.key: (readings[op.key], covariances[op.key][:, : pw.PLACEMENTS, : pw.PLACEMENTS]) for op in pw.WIDE_OPERANDS
    }
    sums: dict[str, np.ndarray] = {}
    for op in pw.WIDE_OPERANDS:
        rows, cov = ops[op.key]
        tag = f"wide_{op.key}"
        weights = block_weights(rows)
        blocks = len(weights)
        sums[op.key] = np.sum(list(weights.values()), axis=0)
        for block, w in weights.items():
            mine = [r for r, x in zip(rows, w, strict=True) if x > 0]
            for quantity, label in (
                ("nullity", "nullity_estimate"),
                ("visibility", "visibility"),
                ("selector", "selector_contrast"),
            ):
                out[f"{block}_{label}"] = _linear(rows, cov, quantity, w)
            out[f"{block}_nullity_ideal"] = reading_stat(float(np.mean([r["ideal"] for r in mine])), 0.0)
            out[f"{block}_sign_agreement"] = reading_stat(float(np.mean([r["sign_agreement"] for r in mine])), 0.0)
        total = sums[op.key]
        out[f"{tag}_nullity_estimate"] = _linear(rows, cov, "nullity", total)
        out[f"{tag}_nullity_ideal"] = reading_stat(float(total @ np.array([r["ideal"] for r in rows])), 0.0)
        out[f"{tag}_certified_nullity"] = reading_stat(float(op.nullity), 0.0)
        out[f"{tag}_selector_contrast_sum"] = _linear(rows, cov, "selector", total)
        out[f"{tag}_sign_agreement"] = reading_stat(float(total @ np.array([r["sign_agreement"] for r in rows])), 0.0)
        out[f"{tag}_bins"] = reading_stat(float(total @ np.array([r["bins"] for r in rows])), 0.0)
        out[f"{tag}_visibility_mean"] = _linear(rows, cov, "visibility", total / blocks)
    for dim in (64, 128):
        for other, name in (("n", "null"), ("m", "mutation")):
            control = ops[f"{other}{dim}"]
            target = ops[f"o{dim}"]
            out[f"wide_d{dim}_target_minus_{name}"] = _linear(
                target[0], target[1], "nullity", sums[f"o{dim}"], other=control
            )
    return out


def copy_agreement(
    readings: dict[str, list[dict[str, Any]]], covariances: dict[str, np.ndarray]
) -> list[tuple[str, bool, str]]:
    """Report-only reading of the 64-dimensional operands: the sum over blocks of copy A minus copy B of N_hat,
    over its standard error, which the shot-noise interval must cover for its bands to hold. The reading also
    gives the z under independent placements."""
    out = []
    for op in pw.WIDE_OPERANDS:
        count = len(op.blocks())
        if count == pw.PLACEMENTS:
            continue
        rows = readings[op.key][: 2 * count]
        weights = np.concatenate([np.ones(count), -np.ones(count)])
        stat = _linear(rows, covariances[op.key][:, : 2 * count, : 2 * count], "nullity", weights)
        z = stat["mean"] / stat["se"] if stat["se"] > 0 else 0.0
        z_marginal = stat["mean"] / stat["marginal_se"] if stat["marginal_se"] > 0 else 0.0
        out.append(
            (
                f"copy agreement {op.key}",
                abs(z) <= COPY_Z_LIMIT,
                f"copy A - copy B {stat['mean']:+.3f}, z {z:+.2f} (independent placements {z_marginal:+.2f})",
            )
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
    outcomes = load_outcomes(run, entry)
    raw_readings = placement_readings(entry, writers, group, corrected=False)
    corr_readings = placement_readings(entry, writers, group, corrected=True)
    raw = operand_stats(raw_readings, shot_covariances(raw_readings, outcomes))
    corr_covariances = shot_covariances(corr_readings, outcomes)
    corr = operand_stats(corr_readings, corr_covariances)
    pooled = entry["measured_summary_readout_corrected"]
    drift = max(abs(corr[k]["mean"] - pooled[k]) for k in pooled if k in corr and k.endswith("_nullity_estimate"))
    record = json.loads((run / "record.json").read_text())
    model = next(g for g in record["groups"] if g["group"] == entry["group"])["summary_readout_corrected"]
    return {
        "raw": raw,
        "corrected": corr,
        "readings": corr_readings,
        "covariances": corr_covariances,
        "writers": writers,
        "pubs": {name: executed["pub"] for name, executed in entry["executed"].items()},
        "pooled_difference": drift,
        "model": model,
        "backend": entry["backend"],
        "group": entry["group"],
        "job_id": entry["job_id"],
        "input_sha256": {
            name: sha256(run / name) for name in ("collect.json", "record.json", "isa.qpy") if (run / name).is_file()
        }
        | {"raw_index": sha256(run / "raw" / entry["job_id"] / "index.json")},
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


def rule_table(
    runs: list[dict[str, Any]],
) -> tuple[list[list[dict[str, Any]]], list[dict[str, Any]], list[list[tuple[str, bool, str]]]]:
    """Every single-run rule under the covariance and the independent-placement intervals, per run, the
    device-agreement rules of a pair, and the copy-agreement readings of each run."""
    per_run = []
    for result in runs:
        cov = rules(result["raw"], result["corrected"])
        marginal = rules(marginal_view(result["raw"]), marginal_view(result["corrected"]))
        per_run.append(
            [
                {
                    "rule": title,
                    "covariance": ok,
                    "independent_placements": ok_m,
                    "changed": ok != ok_m,
                    "reading": reading,
                    "reading_independent_placements": reading_m,
                }
                for (title, ok, reading), (_, ok_m, reading_m) in zip(cov, marginal, strict=True)
            ]
        )
    pair: list[dict[str, Any]] = []
    if len(runs) == 2:
        gap, _ = model_gap(runs[0]["model"], runs[1]["model"])
        cov = device_agreement(runs[0]["corrected"], runs[1]["corrected"], gap)
        marginal = device_agreement(marginal_view(runs[0]["corrected"]), marginal_view(runs[1]["corrected"]), gap)
        pair = [
            {
                "rule": title,
                "covariance": ok,
                "independent_placements": ok_m,
                "changed": ok != ok_m,
                "reading": reading,
                "reading_independent_placements": reading_m,
            }
            for (title, ok, reading), (_, ok_m, reading_m) in zip(cov, marginal, strict=True)
        ]
    copies = [copy_agreement(result["readings"], result["covariances"]) for result in runs]
    return per_run, pair, copies


def rounded(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): rounded(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [rounded(v) for v in value]
    if isinstance(value, (np.floating, float)):
        return round(float(value), DECIMALS) if math.isfinite(float(value)) else None
    if isinstance(value, np.integer):
        return int(value)
    return value


def placement_map(result: dict[str, Any]) -> dict[str, Any]:
    """The physical qubits each placement measures into clbits 0 to 3, and each block's placements, per operand."""
    pubs = {name: result["writers"][pub] for name, pub in result["pubs"].items()}
    qubits = {str(k): v for k, v in next(iter(pubs.values())).items()}
    blocks: dict[str, dict[str, list[int]]] = {}
    for key, rows in result["readings"].items():
        for row in rows:
            blocks.setdefault(row["block"], {}).setdefault(key, []).append(row["placement"])
    return {"placement_qubits": qubits, "block_placements": blocks}


def analysis_record(runs: list[dict[str, Any]]) -> dict[str, Any]:
    per_run, pair, copies = rule_table(runs)
    backends = {}
    for result, rows, copy in zip(runs, per_run, copies, strict=True):
        stats = {
            key: stat
            for key, stat in result["corrected"].items()
            if key.startswith("wide_")
            and (key.count("_k") == 0)
            and key.endswith(("_nullity_estimate", "_target_minus_null", "_target_minus_mutation", "_visibility_mean"))
        }
        backends[result["backend"]] = {
            "group": result["group"],
            "job_id": result["job_id"],
            "input_sha256": result["input_sha256"],
            "pooled_difference": result["pooled_difference"],
            "rules": rows,
            "copy_agreement": [{"rule": t, "within_limit": ok, "reading": r} for t, ok, r in copy],
            "stats": stats,
            "readings": {
                key: [
                    {k: row[k] for k in ("placement", "block", "nullity", "visibility", "selector")}
                    | {"nullity_se": math.sqrt(max(row["nullity_variance"], 0.0))}
                    for row in value
                ]
                for key, value in result["readings"].items()
            },
            **placement_map(result),
        }
    return rounded(
        {
            "schema": SCHEMA,
            "interval": "delta method, 95 percent, covariance of per-shot influence values across a PUB's placements",
            "independent_placements": "the same rules under per-placement multinomial variances that add (report-only)",
            "backends": backends,
            "cross_device": pair,
            "changed_verdicts": [
                {
                    "backend": backend,
                    "rule": row["rule"],
                    "covariance": row["covariance"],
                    "independent_placements": row["independent_placements"],
                }
                for backend, body in backends.items()
                for row in body["rules"]
                if row["changed"]
            ]
            + [
                {
                    "backend": "cross-device",
                    "rule": row["rule"],
                    "covariance": row["covariance"],
                    "independent_placements": row["independent_placements"],
                }
                for row in pair
                if row["changed"]
            ],
        }
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("runs", nargs="+", type=Path, help="one run directory, or two of different backends")
    parser.add_argument("--out", type=Path, help="write the analysis record here")
    args = parser.parse_args(argv)
    if len(args.runs) > 2:
        parser.error("give one run directory, or two for the device-agreement rule")
    runs = [analyze_run(path.resolve()) for path in args.runs]
    if len(runs) == 2 and runs[0]["backend"] == runs[1]["backend"]:
        parser.error(f"device agreement compares two backends, both runs are {runs[0]['backend']}")
    per_run, pair, copies = rule_table(runs)
    failed = False
    for result, rows, copy in zip(runs, per_run, copies, strict=True):
        print(
            f"{result['backend']}: corrected mean differs from live_run's pooled value"
            f" by {result['pooled_difference']:.2e}"
        )
        for row in rows:
            note = (
                ""
                if not row["changed"]
                else f"  [independent placements: {'pass' if row['independent_placements'] else 'FAIL'}]"
            )
            print(f"  {'pass' if row['covariance'] else 'FAIL'}  {row['rule']}: {row['reading']}{note}")
            failed |= not row["covariance"]
        for title, ok, reading in copy:
            print(f"  report {'ok  ' if ok else 'WIDE'}  {title}: {reading}")
        for line in report_readings(result):
            print(line)
    if len(runs) == 2:
        _, unmatched = model_gap(runs[0]["model"], runs[1]["model"])
        for key in unmatched:
            print(f"  report  device agreement: {key} is planned on one device only and left out")
        for row in pair:
            note = (
                ""
                if not row["changed"]
                else f"  [independent placements: {'pass' if row['independent_placements'] else 'FAIL'}]"
            )
            print(f"  {'pass' if row['covariance'] else 'FAIL'}  {row['rule']}: {row['reading']}{note}")
            failed |= not row["covariance"]
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        record = analysis_record(runs)
        args.out.write_text(json.dumps(record, indent=1, sort_keys=True, allow_nan=False) + "\n")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
