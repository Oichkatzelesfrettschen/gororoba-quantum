"""Preregistered analysis of the Tuna-17 Walsh exemplar series and its q13 readout-context circuits.

The series (scripts/qi_walsh_exemplar_cases.py, results/quantum_inspire/cases/
walsh_exemplar_tuna_17/) runs walsh-c1 (high class on block X, low on Y) and
walsh-c2 (swapped) twice, in batch-01 and batch-02, between readout brackets
in batch-00 and batch-03, and four context readouts of q13. Every rule and
threshold comes from the manifest's `preregistered` block.

- Readout. Each qubit's e01 and e10 are the mean of the two brackets. q13's
  e10 enters three ways: the bracket value, the isolated value of
  readout-q13, and the context value chosen by the true state of q10 and q11
  (readout-q13, -q13-q10, -q13-q11, readout-1). The block response R is the
  16 x 16 channel from true to measured z with that conditional channel on
  q13, and the corrected distribution is R^-1 applied to the measured one.
- Attribution. readout-q13-xx drives q10 and q11 twice and leaves them in
  |0>; its e10 against readout-q13 measures drive crosstalk, and the
  one-neighbor readouts measure the neighbor's state.
- Walsh observables. Per job and block: K = sum p^2 of the corrected
  distribution, the corrected weight outside the ideal support, the
  visibility V = (K - 1/16) / (K_ideal - 1/16), the depolarizing-shape G test
  through R, and across jobs the class-by-block interaction I and the
  replicate TVD.

Errors come from a parametric bootstrap that redraws every job's block
histogram and every readout circuit's per-qubit counts on one seeded stream,
batched over draws with numpy.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, NoReturn

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
from box_kite_analysis import bit_matrix, check_receipt  # noqa: E402
from qi_shot_record_line import chi2_log10_tail  # noqa: E402
from qi_walsh_exemplar_cases import (  # noqa: E402
    BLOCKS,
    CASES,
    CIRCUITS,
    CONTEXT_NEIGHBORS,
    CONTEXT_QUBIT,
    CONTEXTS,
    FAMILY,
    SERIES_PLAN,
    WIDTH,
)

SCHEMA = "qi-walsh-exemplar-analysis-v1"
DECIMALS = 6
OUTCOMES = 1 << WIDTH
UNIFORM = 1 / OUTCOMES


def fail(message: str) -> NoReturn:
    raise SystemExit(message)


def sig(value: float) -> float:
    return float(f"{value:.{DECIMALS}g}") if math.isfinite(value) else value


# ---------------------------------------------------------------- inputs


def load_run(run: Path) -> tuple[dict[str, Any], dict[str, np.ndarray], dict[str, str]]:
    """Manifest, bit matrices and raw digests of one run directory bound to its retained case and receipt."""
    cases_bytes = (run / "cases.json").read_bytes()
    manifest = json.loads(cases_bytes)
    if manifest.get("family") != FAMILY:
        fail(f"{run}: family {manifest.get('family')!r} is not {FAMILY}")
    retained = CASES / FAMILY / manifest["batch"] / "cases.json"
    if not retained.exists() or retained.read_bytes() != cases_bytes:
        fail(f"{run}: cases.json differs from the retained case")
    collected = json.loads((run / "results.json").read_text(encoding="utf-8"))
    jobs = check_receipt(run, manifest, cases_bytes, collected)
    bits: dict[str, np.ndarray] = {}
    digests: dict[str, str] = {}
    for row in manifest["circuits"]:
        file = row["file"]
        if hashlib.sha256((run / file).read_bytes()).hexdigest() != row["sha256"]:
            fail(f"{run}/{file}: bytes differ from the cases.json sha256")
        if jobs[file]["job"]["status"] != "completed":
            fail(f"{run}/{file}: job {jobs[file]['job']['status']}")
        raw_bytes = (run / "raw" / f"{file}.json").read_bytes()
        raw = json.loads(raw_bytes)
        if len(raw) != manifest["shots"]:
            fail(f"{run}/{file}: {len(raw)} raw shots against the manifest's {manifest['shots']}")
        matrix = bit_matrix(raw, manifest["nqubits"], "rightmost")
        if matrix is None:
            fail(f"{run}/{file}: a shot string holds a character other than 0 and 1")
        bits[file] = matrix
        digests[file] = hashlib.sha256(raw_bytes).hexdigest()
    return manifest, bits, digests


# ---------------------------------------------------------------- readout


def rates(bits: dict[str, dict[str, np.ndarray]]) -> dict[str, Any]:
    """Counts of the readout circuits: per bracket and qubit, ones of readout-0 and zeros of readout-1, and q13's."""
    brackets = []
    for batch in ("batch-00", "batch-03"):
        zero, one = bits[batch]["readout-0.cq"], bits[batch]["readout-1.cq"]
        brackets.append(
            {"n0": zero.shape[0], "ones0": zero.sum(axis=0), "n1": one.shape[0], "zeros1": (1 - one).sum(axis=0)}
        )
    context = {}
    for name in CONTEXTS:
        batch = next(f"batch-{n:02d}" for n, plan in enumerate(SERIES_PLAN) if name in plan)
        column = bits[batch][f"{name}.cq"][:, CONTEXT_QUBIT]
        context[name] = {"n": int(column.shape[0]), "zeros": int(column.shape[0] - column.sum())}
    return {"brackets": brackets, "context": context}


def channel_values(counts: dict[str, Any], rng: np.random.Generator | None, draws: int) -> dict[str, np.ndarray]:
    """e01 and e10 per qubit and q13's context e10s, shape (draws, ...) under the bootstrap or (1, ...) as measured."""

    def draw(k: Any, n: int) -> np.ndarray:
        k = np.asarray(k, dtype=np.float64)
        if rng is None:
            return (k / n)[np.newaxis, ...]
        return rng.binomial(n, k / n, size=(draws, *k.shape)) / n

    e01 = np.mean([draw(b["ones0"], b["n0"]) for b in counts["brackets"]], axis=0)
    e10 = np.mean([draw(b["zeros1"], b["n1"]) for b in counts["brackets"]], axis=0)
    out = {"e01": e01, "e10": e10}
    for name, row in counts["context"].items():
        out[name] = draw(row["zeros"], row["n"])
    return out


def response(values: dict[str, np.ndarray], block: tuple[int, ...], variant: str) -> np.ndarray:
    """R[d, m, t]: probability of measured z m given true z t for each draw d, q13 by the named variant."""
    draws = values["e01"].shape[0]
    r = np.ones((draws, OUTCOMES, OUTCOMES))
    m = np.arange(OUTCOMES)[:, None]
    t = np.arange(OUTCOMES)[None, :]
    for k, q in enumerate(block):
        mk, tk = (m >> k) & 1, (t >> k) & 1
        e01 = values["e01"][:, q][:, None, None]
        e10 = values["e10"][:, q][:, None, None]
        if q == CONTEXT_QUBIT and variant != "bracket":
            if variant == "isolated":
                e10 = values["readout-q13"][:, None, None] * np.ones((1, 1, OUTCOMES))
            else:
                n10, n11 = (block.index(CONTEXT_NEIGHBORS[0]), block.index(CONTEXT_NEIGHBORS[1]))
                state = ((t >> n10) & 1) + 2 * ((t >> n11) & 1)
                table = np.stack(
                    [values["readout-q13"], values["readout-q13-q10"], values["readout-q13-q11"], values["e10"][:, q]],
                    axis=1,
                )
                e10 = table[:, state.reshape(-1)][:, None, :]
        flip = np.where(tk == 0, e01, e10)
        r = r * np.where(mk == tk, 1 - flip, flip)
    return r


# ---------------------------------------------------------------- Walsh observables


def histogram(matrix: np.ndarray, block: tuple[int, ...], outcomes: int = OUTCOMES) -> np.ndarray:
    z = sum(matrix[:, q].astype(np.int64) << k for k, q in enumerate(block))
    return np.bincount(z, minlength=outcomes)


def shape_test(raw: np.ndarray, r: np.ndarray, ideal: np.ndarray) -> dict[str, float]:
    """Maximum-likelihood lambda of N R (lambda P + (1 - lambda) u) on [0, 1] and its G statistic on 14 dof."""
    n = raw.sum()
    a, b = r @ ideal, r @ np.full(OUTCOMES, UNIFORM)

    def loglik(lam: float) -> float:
        q = np.clip(lam * a + (1 - lam) * b, 1e-300, None)
        return float(np.sum(raw * np.log(q)))

    lo, hi = 0.0, 1.0
    for _ in range(80):
        m1, m2 = lo + (hi - lo) / 3, hi - (hi - lo) / 3
        if loglik(m1) < loglik(m2):
            lo = m1
        else:
            hi = m2
    lam = (lo + hi) / 2
    expected = n * (lam * a + (1 - lam) * b)
    seen = raw > 0
    g = 2 * float(np.sum(raw[seen] * np.log(raw[seen] / expected[seen])))
    return {
        "lambda": lam,
        "g": g,
        "dof": OUTCOMES - 2,
        "log10_p": float(chi2_log10_tail(np.array([g]), OUTCOMES - 2)[0]),
    }


def observables(raw: np.ndarray, r: np.ndarray, ideal: np.ndarray, k_ideal: float) -> dict[str, np.ndarray]:
    """K, forbidden weight and visibility of the corrected distribution for every draw of raw (d, 16) and r."""
    measured = raw / raw.sum(axis=-1, keepdims=True)
    corrected = np.linalg.solve(r, measured[..., None])[..., 0]
    k = np.sum(corrected**2, axis=-1)
    forbidden = np.sum(corrected[..., ideal == 0], axis=-1)
    return {"k": k, "forbidden": forbidden, "visibility": (k - UNIFORM) / (k_ideal - UNIFORM), "p": corrected}


def analyze_bits(manifests: dict[str, dict[str, Any]], bits: dict[str, dict[str, np.ndarray]]) -> dict[str, Any]:
    """The preregistered record from every batch's bit matrices (batch name -> file -> (shots, 17))."""
    if set(bits) != {f"batch-{n:02d}" for n in range(len(SERIES_PLAN))}:
        fail(f"the analysis needs every batch of the series; it has {sorted(bits)}")
    pre = manifests["batch-00"]["preregistered"]
    classes = manifests["batch-00"]["classes"]
    zdec, draws = pre["z_decision"], pre["bootstrap"]["draws"]
    rng = np.random.default_rng(pre["bootstrap"]["seed"])
    counts = rates(bits)
    point = channel_values(counts, None, 1)
    boot = channel_values(counts, rng, draws)

    def dist(values: np.ndarray) -> dict[str, float]:
        return {"value": sig(float(values[0])), "se": sig(float(np.std(values[1:], ddof=1)))}

    readout = {}
    for k, b in enumerate(counts["brackets"]):
        e01, e10 = b["ones0"] / b["n0"], b["zeros1"] / b["n1"]
        readout[("batch-00", "batch-03")[k]] = {
            str(q): [sig(float(e01[q])), sig(float(e10[q]))] for q in sorted(q for blk in BLOCKS.values() for q in blk)
        }
    drift = {
        str(q): sig(float(max(abs(np.diff([rows[str(q)][i] for rows in readout.values()]))[0] for i in (0, 1))))
        for q in sorted(q for blk in BLOCKS.values() for q in blk)
    }
    joined = {name: np.concatenate([point[name], boot[name]]) for name in CONTEXTS}
    joined["readout-1"] = np.concatenate([point["e10"][:, CONTEXT_QUBIT], boot["e10"][:, CONTEXT_QUBIT]])
    # readout-q13 runs in batch-00 and each context readout in a later batch, so q13's bracket drift
    # between batch-00 and batch-03 bounds the baseline shift a delta carries and joins its SE in quadrature.
    q13_drift = drift[str(CONTEXT_QUBIT)]
    attribution: dict[str, dict[str, Any]] = {}
    for label, name in (("drive", "readout-q13-xx"), ("q10", "readout-q13-q10"), ("q11", "readout-q13-q11")):
        delta = joined[name] - joined["readout-q13"]
        se = float(np.std(delta[1:], ddof=1))
        total = math.hypot(se, q13_drift)
        established = abs(delta[0]) >= pre["delta_min"] and abs(delta[0]) >= zdec * total
        attribution[label] = {
            "delta": sig(float(delta[0])),
            "se": sig(se),
            "se_with_drift": sig(total),
            "established": bool(established),
        }
    drive = bool(attribution["drive"]["established"])
    state = bool(attribution["q10"]["established"] or attribution["q11"]["established"])
    verdict = {(False, False): "neither", (True, False): "drive", (False, True): "state", (True, True): "both"}
    context = {
        "e10": {name: dist(values) for name, values in joined.items()},
        "attribution": attribution,
        "verdict": verdict[(drive, state)],
    }

    jobs: list[dict[str, Any]] = []
    pooled: dict[tuple[str, str], list[np.ndarray]] = {}
    for batch in ("batch-01", "batch-02"):
        for name, assignment in CIRCUITS.items():
            matrix = bits[batch][f"{name}.cq"]
            outside = [q for q in range(matrix.shape[1]) if all(q not in blk for blk in BLOCKS.values())]
            row: dict[str, Any] = {"batch": batch, "circuit": name, "stray": int(matrix[:, outside].any(axis=1).sum())}
            # Both blocks read the same shots, so each draw resamples the joint (X, Y) histogram once and
            # takes both block histograms from it: index x + 16 y, rows y and columns x after the reshape.
            joint = histogram(matrix, BLOCKS["X"] + BLOCKS["Y"], OUTCOMES * OUTCOMES).astype(np.float64)
            n = joint.sum()
            joint_draws = np.concatenate(
                [joint[None, :], rng.multinomial(int(n), joint / n, size=draws).astype(np.float64)]
            ).reshape(-1, OUTCOMES, OUTCOMES)
            block_draws = {"X": joint_draws.sum(axis=1), "Y": joint_draws.sum(axis=2)}
            for block, cls in assignment.items():
                qubits = BLOCKS[block]
                raw = histogram(matrix, qubits).astype(np.float64)
                ideal = np.array([float(Fraction(p)) for p in classes[cls]["ideal_p"]])
                k_ideal = float(Fraction(classes[cls]["k"]))
                raw_draws = block_draws[block]
                if not np.array_equal(raw_draws[0], raw):
                    fail(f"{batch}/{name}: the joint histogram's {block} marginal differs from the block histogram")
                variants: dict[str, dict[str, Any]] = {}
                for variant in pre["q13"]["variants"] if CONTEXT_QUBIT in qubits else ["bracket"]:
                    r = np.concatenate([response(point, qubits, variant), response(boot, qubits, variant)])
                    obs = observables(raw_draws, r, ideal, k_ideal)
                    variants[variant] = {
                        "k": dist(obs["k"]),
                        "forbidden": dist(obs["forbidden"]),
                        "visibility": dist(obs["visibility"]),
                        "shape": {key: sig(v) for key, v in shape_test(raw, r[0], ideal).items()},
                    }
                    if variant == ("context" if CONTEXT_QUBIT in qubits else "bracket"):
                        pooled.setdefault((cls, block), []).append(obs["visibility"])
                        variants[variant]["p"] = [sig(float(v)) for v in obs["p"][0]]
                        variants[variant]["_p_draws"] = obs["p"]
                row[block] = {"class": cls, "raw": [int(v) for v in raw], "variants": variants}
            jobs.append(row)

    primary = {b: "context" if CONTEXT_QUBIT in BLOCKS[b] else "bracket" for b in BLOCKS}
    # Each block compares its high-class job with its low-class job of the same batch, so the block's
    # own fidelity cancels; the two jobs are separate acquisitions and their SEs combine in quadrature.
    order = []
    for batch in ("batch-01", "batch-02"):
        for block in BLOCKS:
            by_class = {
                row[block]["class"]: row[block]["variants"][primary[block]]["k"]
                for row in jobs
                if row["batch"] == batch
            }
            diff = by_class["high"]["value"] - by_class["low"]["value"]
            se = math.hypot(by_class["high"]["se"], by_class["low"]["se"])
            order.append({"batch": batch, "block": block, "z": sig(diff / se), "holds": bool(diff >= zdec * se)})
    v = {key: np.mean(values, axis=0) for key, values in pooled.items()}
    if min(float(np.min(x)) for x in v.values()) <= 0:
        interaction: dict[str, Any] = {
            "value": None,
            "se": None,
            "established": None,
            "reason": "a pooled visibility is not positive",
        }
    else:
        stat = np.log(v[("high", "X")]) - np.log(v[("high", "Y")]) - np.log(v[("low", "X")]) + np.log(v[("low", "Y")])
        se = float(np.std(stat[1:], ddof=1))
        interaction = {"value": sig(float(stat[0])), "se": sig(se), "established": bool(abs(stat[0]) >= zdec * se)}
    scatter = []
    for name, assignment in CIRCUITS.items():
        a, b = (row for row in jobs if row["circuit"] == name)
        for block in assignment:
            pa = a[block]["variants"][primary[block]].pop("_p_draws")
            pb = b[block]["variants"][primary[block]].pop("_p_draws")
            tvd = 0.5 * np.sum(np.abs(pa - pb), axis=-1)
            se = float(np.std(tvd[1:], ddof=1))
            flagged = tvd[0] > pre["scatter_allowance"] + zdec * se
            scatter.append(
                {"circuit": name, "block": block, "tvd": sig(float(tvd[0])), "se": sig(se), "flagged": bool(flagged)}
            )
    for row in jobs:
        for block in BLOCKS:
            row[block]["variants"][primary[block]].pop("_p_draws", None)
    shape_rejected = [
        f"{row['batch']}/{row['circuit']}/{block}"
        for row in jobs
        for block in BLOCKS
        if row[block]["variants"][primary[block]]["shape"]["log10_p"] <= pre["shape_log10_p"]
    ]
    return {
        "schema": SCHEMA,
        "family": FAMILY,
        "primary_variant": primary,
        "readout": {
            "brackets": readout,
            "drift": drift,
            "drift_flagged": [q for q, d in drift.items() if d > pre["bracket_drift_max"]],
        },
        "context": context,
        "jobs": jobs,
        "decisions": {
            "class_order": order,
            "class_order_holds": all(row["holds"] for row in order),
            "interaction": interaction,
            "shape_rejected": shape_rejected,
            "replicate_scatter": scatter,
        },
        "bootstrap": pre["bootstrap"],
    }


def analyze(runs: list[Path]) -> dict[str, Any]:
    manifests, bits, digests = {}, {}, {}
    for run in runs:
        manifest, matrices, raw = load_run(run)
        if manifest["batch"] in bits:
            fail(f"{run}: a second run of {manifest['batch']}")
        manifests[manifest["batch"]], bits[manifest["batch"]] = manifest, matrices
        digests[manifest["batch"]] = {"run": run.resolve().relative_to(ROOT).as_posix(), "raw_sha256": raw}
    record = analyze_bits(manifests, bits)
    record["inputs"] = dict(sorted(digests.items()))
    return record


# ---------------------------------------------------------------- self-test


def synthetic(
    seed: int,
    truth: dict[str, dict[str, np.ndarray]],
    e01: float = 0.02,
    e10: float = 0.05,
    q13: tuple[float, float, float, float] = (0.04, 0.06, 0.06, 0.09),
    drive: float = 0.0,
    shots: int = 131072,
    q13_shift: float = 0.0,
) -> dict[str, dict[str, np.ndarray]]:
    """Bit matrices of the whole series from true block distributions and a readout model.

    q13's e10 follows the true state of (q10, q11) through q13 = (00, 10, 01, 11); the X X readout adds
    `drive` to its isolated value, and every batch after batch-00 adds `q13_shift` to q13's e10.
    """
    rng = np.random.default_rng(seed)
    bits: dict[str, dict[str, np.ndarray]] = {}
    for n, plan in enumerate(SERIES_PLAN):
        batch = f"batch-{n:02d}"
        bits[batch] = {}
        for name in plan:
            true = np.zeros((shots, 17), dtype=np.uint8)
            if name in CIRCUITS:
                for block in CIRCUITS[name]:
                    z = rng.choice(OUTCOMES, size=shots, p=truth[batch][f"{name}:{block}"])
                    for k, q in enumerate(BLOCKS[block]):
                        true[:, q] = (z >> k) & 1
            elif name == "readout-1":
                true[:] = 1
            elif name in CONTEXTS:
                for q, pulses in CONTEXTS[name].items():
                    true[:, q] = pulses % 2
            flip_p = np.where(true == 0, e01, e10)
            neighbors = true[:, CONTEXT_NEIGHBORS[0]] + 2 * true[:, CONTEXT_NEIGHBORS[1]]
            q13_e10 = np.asarray(q13)[neighbors] + (drive if name == "readout-q13-xx" else 0.0)
            q13_e10 = q13_e10 + (q13_shift if n > 0 else 0.0)
            flip_p[:, CONTEXT_QUBIT] = np.where(true[:, CONTEXT_QUBIT] == 0, e01, q13_e10)
            bits[batch][f"{name}.cq"] = true ^ (rng.random(true.shape) < flip_p)
    return bits


def ideal_of(classes: dict[str, Any], cls: str) -> np.ndarray:
    return np.array([float(Fraction(p)) for p in classes[cls]["ideal_p"]])


def truth_of(classes: dict[str, Any], lam: dict[str, float], override: dict[str, np.ndarray] | None = None) -> dict:
    truth: dict[str, dict[str, np.ndarray]] = {}
    for batch in ("batch-01", "batch-02"):
        truth[batch] = {}
        for name, assignment in CIRCUITS.items():
            for block, cls in assignment.items():
                p = lam[block] * ideal_of(classes, cls) + (1 - lam[block]) * UNIFORM
                truth[batch][f"{name}:{block}"] = (override or {}).get(f"{name}:{block}", p)
    return truth


def self_test() -> str:
    manifests = {
        f"batch-{n:02d}": json.loads((CASES / FAMILY / f"batch-{n:02d}" / "cases.json").read_text(encoding="utf-8"))
        for n in range(len(SERIES_PLAN))
    }
    classes = manifests["batch-00"]["classes"]
    lam = {"X": 0.85, "Y": 0.8}

    def k_true(cls: str, block: str) -> float:
        return lam[block] ** 2 * (float(Fraction(classes[cls]["k"])) - UNIFORM) + UNIFORM

    # Per-block depolarizing with state-dependent q13 readout: context correction recovers K, no
    # interaction, no shape rejection, the class order holds and the state attribution is established.
    record = analyze_bits(manifests, synthetic(1, truth_of(classes, lam)))
    if not record["decisions"]["class_order_holds"]:
        raise AssertionError("self-test: the class order fails on a depolarizing truth")
    if record["decisions"]["interaction"]["established"]:
        raise AssertionError(
            f"self-test: interaction established on a multiplicative truth {record['decisions']['interaction']}"
        )
    if record["decisions"]["shape_rejected"]:
        raise AssertionError(
            f"self-test: depolarizing shape rejected on a depolarizing truth: {record['decisions']['shape_rejected']}"
        )
    if record["context"]["verdict"] != "state":
        raise AssertionError(f"self-test: q13 attribution {record['context']['verdict']} on a state-dependent truth")
    bias: dict[str, list[float]] = {}
    for row in record["jobs"]:
        for block in BLOCKS:
            for variant, values in row[block]["variants"].items():
                bias.setdefault(variant, []).append(
                    (values["k"]["value"] - k_true(row[block]["class"], block)) / values["k"]["se"]
                )
    if max(abs(z) for z in bias["context"]) > 4 or max(abs(z) for z in bias["bracket"]) < 4:
        raise AssertionError(f"self-test: context correction bias {bias['context']} against bracket {bias['bracket']}")
    if any(row["flagged"] for row in record["decisions"]["replicate_scatter"]):
        raise AssertionError("self-test: replicate scatter flagged on identical truths")

    # A coherent error on the high class of block X alone: the shape test rejects it and the interaction appears.
    import qi_walsh_exemplar_cases as cases

    solutions = cases.path_search(False)
    ops = cases.block_ops(solutions["high"])
    first_t = next(k for k, (g, _) in enumerate(ops) if g == "T")
    saved = dict(cases.ONE_QUBIT)
    cases.ONE_QUBIT["Tbad"] = np.diag([1, np.exp(1j * (np.pi / 4 + 0.35))])
    try:
        bad = cases.probabilities(
            [("Tbad", on) if k == first_t else (g, on) for k, (g, on) in enumerate(ops)], tuple(range(WIDTH))
        )
    finally:
        cases.ONE_QUBIT.clear()
        cases.ONE_QUBIT.update(saved)
    coherent = lam["X"] * bad + (1 - lam["X"]) * UNIFORM
    record = analyze_bits(
        manifests, synthetic(2, truth_of(classes, lam, {"walsh-c1:X": coherent}), q13=(0.04,) * 4, drive=0.03)
    )
    if not any(item.endswith("walsh-c1/X") for item in record["decisions"]["shape_rejected"]):
        raise AssertionError("self-test: a coherent T error escapes the shape test")
    if not record["decisions"]["interaction"]["established"]:
        raise AssertionError("self-test: a class-specific error on one block leaves no interaction")
    if record["context"]["verdict"] != "drive":
        raise AssertionError(f"self-test: q13 attribution {record['context']['verdict']} on a drive-only truth")

    # Block X far below block Y: a within-job comparison of high on X against low on Y reverses, while each
    # block's own high-against-low comparison holds.
    record = analyze_bits(manifests, synthetic(4, truth_of(classes, {"X": 0.5, "Y": 0.95}), shots=32768))
    if not record["decisions"]["class_order_holds"]:
        raise AssertionError(f"self-test: the class order fails at fixed block {record['decisions']['class_order']}")

    # A q13 baseline that shifts after batch-00 by more than the context deltas attributes nothing.
    record = analyze_bits(manifests, synthetic(5, truth_of(classes, lam), q13_shift=0.06))
    if record["context"]["verdict"] != "neither":
        raise AssertionError(f"self-test: q13 attribution {record['context']['verdict']} on a drifting baseline")

    # Missing batches fail.
    bits = synthetic(3, truth_of(classes, lam), shots=4096)
    del bits["batch-03"]
    try:
        analyze_bits(manifests, bits)
    except SystemExit:
        pass
    else:
        raise AssertionError("self-test: a series without its closing bracket was analyzed")
    return "walsh exemplar analysis self-test: depolarizing, coherent and context truths decided as built"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    parser.add_argument("runs", nargs="*", type=Path)
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
        return 0
    text = json.dumps(analyze(args.runs), indent=1) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
        print(f"walsh exemplar analysis: {args.out} written")
    elif args.check.read_text(encoding="utf-8") != text:
        fail(f"{args.check} differs from its recomputation")
    else:
        print(f"walsh exemplar analysis: {args.check} matches its recomputation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
