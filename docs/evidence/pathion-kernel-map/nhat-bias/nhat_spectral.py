"""Walsh-spectral reading of the kernel-map nullity estimator N_hat on the retained IBM runs.

For a contrast vector c over n = 2^d output bins write its Walsh coefficients c^_a = (1/n) sum_y c(y) (-1)^(a.y). With
w_a = c^_ideal,a^2 (sum w_a = 1, because every ideal bin is +-1) and lambda_a = c^_obs,a / c^_ideal,a on the support
of the ideal, Parseval turns the estimator of ``nhat_bias.estimate`` into

    N_hat = N * lambda_0 / lambda_bar,    lambda_bar = sum_a w_a lambda_a,    whenever N != 0,

and N_hat = n c^_obs,0 / (2 V_hat) when N = 0. Three consequences follow for any channel that acts diagonally on the
characters (a stochastic bit-flip channel on the output register, Pauli noise after the last gate): a block whose
ideal is one character (N_b = 0 blocks) reads exactly 0, an all-aligned block (only the zero character) reads N, and
the bias of every other unit is fixed by how its ideal power spreads over characters of unequal contraction. A
nonzero reading of a one-character block therefore measures leakage into the zero character, which needs a channel
that is not character-diagonal (asymmetric readout, relaxation).

Modes:
    "$PYTHON" nhat_spectral.py --self-test     identity, channel corollaries, orbit-geometry mutation control
    "$PYTHON" nhat_spectral.py --out DIR       write DIR/result_spectral.json
    "$PYTHON" nhat_spectral.py --check DIR     recompute and compare with DIR/result_spectral.json
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

import nhat_bias as nb  # noqa: E402

SCHEMA = "nhat-spectral-v1"
HERE = Path(__file__).resolve().parent
pkm = nb.pkm
pcb = nb.pcb
expect = nb.expect
r12 = nb.r12
SUPPORT = 1e-12


def walsh_matrix(n: int) -> np.ndarray:
    """H[a, y] = (-1)^(popcount(a & y)), a Sylvester-ordered Hadamard matrix on n = 2^d bins."""
    expect(n > 0 and n & (n - 1) == 0, f"{n} bins is not a power of two")
    idx = np.arange(n)
    parity = np.array([[bin(a & y).count("1") & 1 for y in idx] for a in idx])
    return np.asarray(1.0 - 2.0 * parity)


def coefficients(c: np.ndarray) -> np.ndarray:
    """Walsh coefficients c^_a = (1/n) sum_y c(y) (-1)^(a.y), along the last axis."""
    n = c.shape[-1]
    return np.asarray(c @ walsh_matrix(n).T / n)


def spectral_n_hat(c_obs: np.ndarray, sign: np.ndarray) -> float:
    """N_hat from Walsh coefficients alone: n c^_obs,0 / (2 sum_a c^_obs,a c^_ideal,a)."""
    co, ci = coefficients(c_obs), coefficients(sign)
    return float(len(sign) * co[0] / (2.0 * float(co @ ci)))


def weight(a: int) -> int:
    return bin(a).count("1")


# ----------------------------------------------------------------------------------------------- per unit


def unit_spectrum(unit: nb.Unit) -> dict[str, Any]:
    """Characters of the ideal, their contractions per replica, the bias decomposition and the leakage."""
    ci = coefficients(unit.sign)
    co = coefficients(unit.contrast)
    support = [int(a) for a in np.nonzero(np.abs(ci) > SUPPORT)[0]]
    w = {a: float(ci[a] ** 2) for a in support}
    lam = {a: co[:, a] / ci[a] for a in support}
    mean = nb.estimate(unit.contrast.mean(axis=0), unit.sign)
    reps = len(unit.contrast)
    chars = [
        {
            "character": a,
            "weight": weight(a),
            "power": r12(w[a]),
            "lambda": r12(float(lam[a].mean())),
            "lambda_se": r12(float(lam[a].std(ddof=1) / math.sqrt(reps))),
        }
        for a in support
    ]
    row: dict[str, Any] = {
        "key": unit.key,
        "control": unit.control,
        "operand": unit.operand,
        "block": unit.block,
        "bins": len(unit.sign),
        "n_ideal": mean.n_ideal,
        "n_hat": r12(mean.n_hat),
        "n_hat_spectral": r12(spectral_n_hat(unit.contrast.mean(axis=0), unit.sign)),
        "characters": chars,
    }
    if mean.n_ideal != 0:
        lam_mean = {a: float(lam[a].mean()) for a in support}
        bar = sum(w[a] * lam_mean[a] for a in support)
        # N_hat - N = N (lambda_0 - lambda_bar) / lambda_bar, split over characters by w_a (lambda_0 - lambda_a).
        share = {a: mean.n_ideal * w[a] * (lam_mean[0] - lam_mean[a]) / bar for a in support if a != 0}
        top = max(share, key=lambda a: abs(share[a])) if share else None
        row["ratio_identity"] = r12(mean.n_ideal * lam_mean[0] / bar)
        row["bias_by_character"] = {str(a): r12(v) for a, v in sorted(share.items())}
        row["dominant_character"] = top
        total = float(sum(share.values()))
        row["dominant_share"] = r12(share[top] / total) if top is not None and total else None
    else:
        leak = co[:, 0] / np.array([float(np.dot(co[r], ci)) for r in range(reps)])
        row["leakage_ratio"] = r12(float(leak.mean()))
        row["leakage_t"] = r12(float(leak.mean() / (leak.std(ddof=1) / math.sqrt(reps))))
    if mean.forced:
        dev = unit.contrast * unit.sign
        dev = dev - dev.mean(axis=1, keepdims=True)
        se = dev.std(axis=0, ddof=1) / math.sqrt(reps)
        chi2 = float(np.sum((dev.mean(axis=0) / se) ** 2))
        row["flatness_chi2"] = r12(chi2)
        row["flatness_spread"] = r12(float(dev.mean(axis=0).std(ddof=1)))
        row["flatness_dof"] = len(unit.sign) - 1
    return row


def tensor_fit(row: dict[str, Any]) -> dict[str, Any] | None:
    """For a block whose ideal spans {0, a, b, a ^ b}: per-character flip rates and the multiplicativity residual."""
    chars = {c["character"]: c for c in row["characters"]}
    if row["bins"] != 8 or len(chars) != 4 or 0 not in chars:
        return None
    singles = sorted(c for c in chars if weight(c) == 1)
    if len(singles) != 2 or (singles[0] ^ singles[1]) not in chars:
        return None
    a, b = singles
    lam0, la, lb, lab = (chars[x]["lambda"] for x in (0, a, b, a ^ b))
    se = math.hypot(chars[a ^ b]["lambda_se"] * lam0, chars[a]["lambda_se"] * lb)
    return {
        "flip_rate": {str(a): r12((1.0 - la / lam0) / 2.0), str(b): r12((1.0 - lb / lam0) / 2.0)},
        "multiplicativity_residual": r12(lab * lam0 - la * lb),
        "multiplicativity_z": r12((lab * lam0 - la * lb) / se) if se > 0 else None,
    }


def calibration_flip_rates(collect: Any) -> dict[str, float | int | None]:
    """Median and range of (e10 + e01) / 2 over every placed qubit the run's PUBs record."""
    items = collect if isinstance(collect, list) else [collect]
    top = next(x for x in items if isinstance(x, dict) and "pub_calibration" in x)
    rates = [
        (q["prob_meas1_prep0"] + q["prob_meas0_prep1"]) / 2.0
        for pub in top["pub_calibration"].values()
        for q in pub["placed_qubit_calibration"].values()
    ]
    return {
        "median": r12(float(np.median(rates))),
        "p10": r12(float(np.quantile(rates, 0.1))),
        "p90": r12(float(np.quantile(rates, 0.9))),
        "qubit_readings": len(rates),
    }


def readout_comparison(units: list[nb.Unit], entry: dict[str, Any]) -> list[dict[str, Any]]:
    """Raw replica-mean N_hat against the collector's readout-corrected value of the same unit."""
    corrected = entry.get("measured_summary_readout_corrected", {})
    rows = []
    for unit in units:
        value = corrected.get(f"{unit.key}_nullity_estimate")
        if value is None:
            continue
        est = nb.estimate(unit.contrast.mean(axis=0), unit.sign)
        rows.append(
            {
                "key": unit.key,
                "control": unit.control,
                "n_ideal": est.n_ideal,
                "raw": r12(est.n_hat),
                "corrected": r12(float(value)),
                "raw_bias": r12(est.n_hat - est.n_ideal),
                "corrected_bias": r12(float(value) - est.n_ideal),
            }
        )
    return rows


def summarize_readout(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Mean raw and corrected bias by ideal block value and control."""
    groups: dict[tuple[float, str], list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault((row["n_ideal"], row["control"]), []).append(row)
    out = []
    for (n_ideal, control), items in sorted(groups.items()):
        raw = [x["raw_bias"] for x in items]
        cor = [x["corrected_bias"] for x in items]
        out.append(
            {
                "n_ideal": n_ideal,
                "control": control,
                "units": len(items),
                "raw_bias_mean": r12(float(np.mean(raw))),
                "corrected_bias_mean": r12(float(np.mean(cor))),
                "corrected_bias_range": [r12(min(cor)), r12(max(cor))],
            }
        )
    return out


def output_bit_flips(rel: str, entry: dict[str, Any]) -> dict[str, list[float]]:
    """Per member circuit, the recorded readout flip (e10 + e01)/2 of each output bit, averaged over its replicas.

    A coset-map PUB holds one member circuit; each replica writes one 4-bit register whose clbits 0 to 2 carry the
    output bits and clbit 3 the selector (law index y + 8 s), and the measure instruction names the physical qubit.
    PUBs that hold more than one member are skipped, since their registers do not name the member."""
    from qiskit import qpy  # noqa: PLC0415

    with (nb.ROOT / rel / "isa.qpy").open("rb") as handle:
        circuits = {c.name: c for c in qpy.load(handle)}
    executed = entry["executed"]
    per_pub: Counter[str] = Counter(str(v["pub"]) for v in executed.values())
    out: dict[str, list[float]] = {}
    for member, info in executed.items():
        pub = str(info["pub"])
        if per_pub[pub] != 1 or pub not in circuits:
            continue
        circuit = circuits[pub]
        calibration = info["placed_qubit_calibration"]
        sums, counts = [0.0, 0.0, 0.0], [0, 0, 0]
        for inst in circuit.data:
            if inst.operation.name != "measure":
                continue
            clbit = inst.clbits[0]
            register = next(r for r in circuit.cregs if clbit in r)
            index = list(register).index(clbit)
            if register.size != 4 or index > 2:
                continue
            q = calibration[str(circuit.find_bit(inst.qubits[0]).index)]
            sums[index] += (q["prob_meas1_prep0"] + q["prob_meas0_prep1"]) / 2.0
            counts[index] += 1
        if all(counts):
            out[member] = [s / c for s, c in zip(sums, counts, strict=True)]
    return out


def layout_comparison(fits: dict[str, Any], flips: dict[str, list[float]]) -> dict[str, Any] | None:
    """Fitted per-bit flip rate of each N_b = 2 block against the recorded readout flip of the same output bit."""
    pairs = []
    for key, fit in fits.items():
        arms = [flips.get(f"{key}_{arm}") for arm in ("plus", "minus")]
        if any(a is None for a in arms):
            continue
        for char, rate in fit["flip_rate"].items():
            bit = int(char).bit_length() - 1
            recorded = float(np.mean([a[bit] for a in arms if a is not None]))
            pairs.append((key, bit, float(rate), recorded))
    if not pairs:
        return None
    fitted = np.array([p[2] for p in pairs])
    readout = np.array([p[3] for p in pairs])
    return {
        "pairs": [{"key": k, "bit": b, "fitted": r12(f), "readout": r12(r)} for k, b, f, r in pairs],
        "fitted_mean": r12(float(fitted.mean())),
        "readout_mean": r12(float(readout.mean())),
        "excess_mean": r12(float((fitted - readout).mean())),
        "excess_se": r12(float((fitted - readout).std(ddof=1) / math.sqrt(len(pairs)))),
        "correlation": r12(float(np.corrcoef(fitted, readout)[0, 1])) if len(pairs) > 2 else None,
    }


def analyze_run(name: str) -> dict[str, Any]:
    rel, kind = nb.RUNS[name]
    path = nb.ROOT / rel / "collect.json"
    collect = json.loads(path.read_text())
    units, entry, _ideal, _ = nb.run_units(kind, collect)
    spectra = nb.parallel.ordered_map(unit_spectrum, units)
    fits = {row["key"]: fit for row in spectra if (fit := tensor_fit(row)) is not None}
    layout = layout_comparison(fits, output_bit_flips(rel, entry)) if fits else None
    readout = readout_comparison(units, entry)
    flip = [float(v) for f in fits.values() for v in f["flip_rate"].values()]
    return {
        "name": name,
        "run": rel,
        "collect_sha256": nb.sha256(path),
        "units": spectra,
        "tensor_fits": fits,
        "fitted_flip_rate": {"median": r12(float(np.median(flip))), "min": r12(min(flip)), "max": r12(max(flip))}
        if flip
        else None,
        "calibration_flip_rate": calibration_flip_rates(collect),
        "layout_flip_rate": layout,
        "readout": readout,
        "readout_summary": summarize_readout(readout),
    }


# ----------------------------------------------------------------------------------------------- predictions


def block_spectrum_prediction(n_b: int, flip: float) -> float:
    """N_hat of an 8-bin block with N_b = 2 or 3 aligned pairs under a symmetric flip of rate ``flip`` on each bit.

    The block's minus bins are 4 - N_b lower members. For N_b = 3 one bin carries -1, and for N_b = 2 the two minus
    bins differ in one bit (the measured N_b = 2 blocks have the ideal characters {0, a, b, a ^ b} with a and b of
    weight 1). A uniform rate makes the reading depend only on N_b and the rate."""
    sign = np.ones(8)
    for k in range(4 - n_b):
        sign[k ^ 4] = -1.0
    est = nb.estimate(nb.bit_flip_matrix(flip) @ sign, sign)
    return float(est.n_hat)


def predictions(flips: list[float]) -> list[dict[str, Any]]:
    return [
        {"n_b": n_b, "flip_rate": f, "n_hat": r12(block_spectrum_prediction(n_b, f))} for f in flips for n_b in (2, 3)
    ]


# ----------------------------------------------------------------------------------------------- orbit geometry


def aligned_reps(op: tuple[int, int, int]) -> tuple[int, list[int]]:
    i, j, t = op
    k_matrix = pkm._left(i).T @ (t * pkm._left(j))
    m = i ^ j
    return m, [k for k in range(pkm.DIM) if k < k ^ m and k_matrix[k ^ m, k] == k_matrix[k, k ^ m]]


def admissible_tilings(m: int) -> list[tuple[int, int, int]]:
    """Every 3-dimensional subspace of F_2^5 that contains m, as a basis (m, u, v); 35 of them."""
    seen: set[frozenset[int]] = set()
    out = []
    for u in range(1, pkm.DIM):
        for v in range(u + 1, pkm.DIM):
            span = frozenset(pcb.span((m, u, v)))
            if len(span) == 8 and span not in seen:
                seen.add(span)
                out.append((m, u, v))
    return out


def orbit_geometry(op: tuple[int, int, int]) -> dict[str, Any]:
    """Misaligned pairs in F_2^5 / <m>, their linear structure, and the profile under every admissible tiling."""
    m, aligned = aligned_reps(op)
    reps = [k for k in range(pkm.DIM) if k < k ^ m]
    mis = [k for k in reps if k not in aligned]
    tilings = admissible_tilings(m)
    signature = Counter(tuple(sorted(nb.block_profile(op, b))) for b in tilings)
    quotient = {min(k, k ^ m) for k in pcb.span(tuple(mis))} if mis else {0}
    # The ideal contrast reads -1 on the lower member of each misaligned pair, which is the pair's representative.
    linear = len(mis) == 4 and set(pcb.span(tuple(mis))) == set(mis)
    return {
        "operand": pkm.operand_tag(op),
        "nullity": len(aligned),
        "tilings": len(tilings),
        "signature": sorted([list(p), c] for p, c in signature.items()),
        "misaligned_is_subspace": len(mis) == 4 and len(quotient) == 4 and set(mis) == quotient,
        "contains_operand_pair": min(op[0], op[0] ^ m) in mis,
        "minus_bins_linear_plane": linear,
    }


def orbit_blindness() -> dict[str, Any]:
    ops = [(i, j, t) for i in range(1, pkm.DIM) for j in range(i + 1, pkm.DIM) for t in (1, -1)]
    every = nb.parallel.ordered_map(orbit_geometry, ops)
    rows = [g for g in every if g["nullity"] == 12]
    ops12 = [op for op, g in zip(ops, every, strict=True) if g["nullity"] == 12]
    orbits = nb.parallel.ordered_map(nb.operand_orbit, ops12, min_items=2)
    by_orbit: dict[str, Counter[str]] = {}
    for row, orbit in zip(rows, orbits, strict=True):
        by_orbit.setdefault(orbit, Counter())[json.dumps(row["signature"])] += 1
    return {
        "operands": len(rows),
        "signatures": len({json.dumps(r["signature"]) for r in rows}),
        "signature": rows[0]["signature"],
        "by_orbit": {o: dict(c) for o, c in sorted(by_orbit.items())},
        "misaligned_is_subspace": sum(r["misaligned_is_subspace"] for r in rows),
        "contains_operand_pair": sum(r["contains_operand_pair"] for r in rows),
        "minus_bins_linear_plane": sum(r["minus_bins_linear_plane"] for r in rows),
    }


# ----------------------------------------------------------------------------------------------- wide runs


def wide_predictions_check(path: Path, flip: float) -> list[dict[str, Any]]:
    """Measured informative wide blocks against the character-diagonal prediction at the coset runs' flip rate."""
    record = json.loads(path.read_text())
    out = []
    for run in record["runs"]:
        for unit in run["units"]:
            n_b = unit["n_ideal"]
            if unit["forced"] or n_b not in (2.0, 3.0):
                continue
            out.append(
                {
                    "backend": run["backend"],
                    "block": unit["block"],
                    "placement": unit["placement"],
                    "n_ideal": n_b,
                    "n_hat": unit["n_hat"],
                    "v_minus": unit["v_minus"],
                    "predicted": r12(block_spectrum_prediction(int(n_b), flip)),
                }
            )
    return out


# ----------------------------------------------------------------------------------------------- self-test


def self_test() -> list[str]:
    done = []
    for n_plus, n_minus, phase in ((24, 8, 0.3), (6, 2, 1.1), (7, 1, 0.7), (16, 16, 0.2)):
        c_obs, sign = nb.synthetic(n_plus, n_minus, phase)
        expect(abs(spectral_n_hat(c_obs, sign) - nb.estimate(c_obs, sign).n_hat) < 1e-12, "spectral N_hat differs")
    done.append("Walsh form of N_hat equals the estimator on synthetic contrasts")
    for n_b in (0, 1, 2, 3, 4):
        sign = np.ones(8)
        for k in range(4 - n_b):
            sign[k ^ 4] = -1.0
        for flip in (0.0, 0.02, 0.05):
            est = nb.estimate(0.9 * nb.bit_flip_matrix(flip) @ sign, sign)
            co, ci = coefficients(0.9 * nb.bit_flip_matrix(flip) @ sign), coefficients(sign)
            if n_b == 0:
                expect(abs(est.n_hat) < 1e-12, "a symmetric flip channel moved an N_b = 0 block")
            elif n_b == 4:
                expect(abs(est.n_hat - 4) < 1e-12, "a symmetric flip channel moved a forced block")
            else:
                sup = np.abs(ci) > SUPPORT
                lam = co[sup] / ci[sup]
                ratio = n_b * lam[0] / float(np.sum(ci[sup] ** 2 * lam))
                expect(abs(ratio - est.n_hat) < 1e-12, "N lambda_0 / lambda_bar differs from N_hat")
    done.append("symmetric flips: N_b = 0 reads 0, N_b = 4 reads 4, others equal N lambda_0 / lambda_bar")
    sign = np.ones(8)
    for k in range(4):
        sign[k ^ 4] = -1.0
    asym = np.ones((1, 1))
    for _ in range(3):
        asym = np.kron(asym, np.array([[0.99, 0.06], [0.01, 0.94]]))
    # The contrast is conditional on the observed output, c_obs(y') = sum_y T(y'|y) c(y) / sum_y T(y'|y) for a
    # uniform output law: a column-stochastic T alone keeps sum c, the row normalization of an asymmetric T does not.
    conditional = asym / asym.sum(axis=1, keepdims=True)
    leak = nb.estimate(conditional @ sign, sign).n_hat
    expect(abs(leak) > 1e-3, "an asymmetric channel left a one-character block at 0: the leakage test has no power")
    done.append(f"asymmetric flips leak into the zero character (N_b = 0 block reads {leak:.4f})")
    geo = orbit_geometry((1, 24, 1))
    expect(geo["misaligned_is_subspace"] and geo["minus_bins_linear_plane"], "e1 + e24 geometry")
    m, aligned = aligned_reps((1, 24, 1))
    reps = [k for k in range(pkm.DIM) if k < k ^ m]
    mis = [k for k in reps if k not in aligned]
    mutated = [*mis[:3], next(k for k in aligned if k not in pcb.span(tuple(mis)))]
    expect(len({min(k, k ^ m) for k in pcb.span(tuple(mutated))}) != 4, "a swapped pair kept the subspace")
    done.append("orbit geometry: e1 + e24 misaligned pairs form a subspace; swapping one pair breaks it")
    for op in ((1, 24, 1), (1, 18, 1)):
        ideal = np.sign(
            pkm.output_contrast(
                pkm.ideal_law(pkm.kernel_map_circuit(op, True)), pkm.ideal_law(pkm.kernel_map_circuit(op, False))
            )
        )
        m, aligned = aligned_reps(op)
        rule = np.ones(pkm.DIM)
        for k in range(pkm.DIM):
            if k < k ^ m and k not in aligned:
                rule[k] = -1.0
        expect(bool(np.array_equal(ideal, rule)), f"minus-bin rule differs from the ideal contrast of {op}")
    done.append("minus bins are the lower members of misaligned pairs (ideal contrast of e1 + e24 and e1 + e18)")
    expect(abs(block_spectrum_prediction(2, 0.02) - 2.0825) < 1e-3, "N_b = 2 prediction at rate 0.02")
    done.append("N_b = 2 block at flip rate 0.02 predicts 2.0825")
    return done


# ----------------------------------------------------------------------------------------------- driver


def build() -> dict[str, Any]:
    runs = [analyze_run(name) for name in nb.RUNS]
    coset_rates = [
        float(v)
        for run in runs
        if run["fitted_flip_rate"]
        for f in run["tensor_fits"].values()
        for v in f["flip_rate"].values()
    ]
    rate = float(np.median(coset_rates))
    return {
        "schema": SCHEMA,
        "identity": "N_hat = N lambda_0 / sum_a w_a lambda_a (N != 0); N_hat = n c_obs,0 / (2 V_hat) (N = 0)",
        "runs": runs,
        "coset_flip_rate_median": r12(rate),
        "predictions": predictions([0.015, 0.02, r12(rate) or 0.0]),
        "wide_check": wide_predictions_check(HERE / "result_wide.json", rate),
        "orbit_blindness": orbit_blindness(),
    }


def encode(record: dict[str, Any]) -> str:
    return json.dumps(record, indent=1, sort_keys=True, allow_nan=False) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    args = ap.parse_args()
    if args.self_test:
        for line in self_test():
            print(f"ok: {line}")
        return 0
    text = encode(build())
    if args.out:
        (args.out / "result_spectral.json").write_text(text)
        return 0
    stored = (args.check / "result_spectral.json").read_text()
    if stored != text:
        raise SystemExit("result_spectral.json differs from a fresh computation")
    print("ok: result_spectral.json reproduces")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
