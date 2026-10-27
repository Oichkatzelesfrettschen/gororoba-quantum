"""Shot-order diagnostics of a collected measurement-sequence envelope run, read from its raw shot-ordered bits.

The envelope job holds one fused dynamic PUB per member row, every row the same member on every layout qubit. The
service executes a job's circuits column-wise, every circuit once per shot index in submission order
(docs/notes/ibm_quantum/repetition-rate-execution.md), and gives no guarantee of that order; the run's executor
reports one chunk holding every PUB. If the order holds, shot j of PUB k follows shot j of PUB k - 1 by one circuit,
and shot j - 1 or j + 1 of PUB k - 1 lies a full column away. The adjacency section tests that: the conditional
difference P(final_k = 1 | final_prev = 1) - P(final_k = 1 | final_prev = 0) per row and qubit, at the same shot and at
the misaligned shots, which share the drift but not the predecessor.

Carryover. The ro0 row (measure only) follows a row ending near |1> in most shots, so its conditional difference reads
the excitation one previous end state leaves through the terminal reset, the repetition delay and the service's
initialization, scaled by the readout contrast. The pattern rows read the same quantity per qubit with far more shots:
each prepares a fixed bit on each qubit (x or nothing, then read), so among consecutive pattern rows a qubit's P1 on
rows that read ground after a row that prepared 1, minus after one that prepared 0, is D; on rows that prepare 1 the
carried excitation is flipped by the x and enters with the opposite sign. The two estimates combine by inverse
variance. Both rest on column-wise order; under any other order they read about zero. A neighbor's current bit is
not balanced across the conditioning classes of the 35 consecutive pairs, so readout crosstalk enters D on qubits the
pattern screen flags: the section reports each qubit's retained pattern-screen outcome, a between-row standard error
beside the binomial one, the pooled D over qubits that pass, and the carryover screen sized with the larger error.

T1 series. The analysis corrects the t1 rows through the ro0 and t1-0 brackets and fits y_k = q (1 - e_k) - e_k with
e_k = exp(-t_k / T1). This section fits four nuisance models per informative qubit with inverse binomial-variance
weights on the delays after the bracket: T1 and q free; calibrated T1 with q free; T1 free with q = 1 (decay to the
ground state); calibrated T1 with q = 1. It reports chi-square, degrees of freedom and p-value for each, and the free
fits on each quarter of the shot index, which execution order maps onto quarters of the job's time.

Gamma-rate model. A decay rate that fluctuates faster than the job resolves, drawn from a gamma distribution of mean mu
and shape k, gives the survival (1 + mu t / k)^(-k) and decays to the ground state (q = 1) with two parameters, the
count the (T1, q) fit spends. The fit profiles mu by bounded Brent search at each shape of a fixed geometric grid and
keeps the grid's best shape. The section reports its lack of fit and the N = 16 residual of the measure, unitary and
delay arms (measured P0 from the exploratory analysis minus the model chain averaged over the rate distribution at its
GAMMA_NODES equal-probability midpoint quantiles), beside the analysis's own residuals. It also reports the residuals of
the plain exponential chain at the gamma fit's mean lifetime and q = 1, which the N = 16 arms cannot tell from the
rate-averaged chain over their microseconds, and the settle gap at q = 1: the settle arm's P0 minus the settle chain
at the loss that matches the measure arm, as `quantities` computes it with the fitted (T1, q).

``--out FILE`` writes the result; ``--check FILE`` recomputes it and requires the retained bytes. No result here is a
preregistered verdict of the envelope case.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import minimize_scalar
from scipy.stats import chi2, norm
from scipy.stats import gamma as gamma_distribution

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import measurement_sequence_analysis as msa  # noqa: E402
from diagnostic_experiments import msqe_pattern_bits  # noqa: E402
from parallel import ordered_map  # noqa: E402

SCHEMA = "msq-envelope-raw-diagnostics-v1"
RESULT_METADATA = "result_metadata.json"
EXPLORATORY = ROOT / "docs/evidence/measurement_sequence/envelope-run-exploratory.json"
# Lags of the adjacency section: (rows back, shot offset). (1, 0) is the predecessor under column-wise order.
LAGS = ((1, 0), (2, 0), (5, 0), (1, -1), (1, 1))
QUARTERS = 4
# The gamma-rate shape grid; the exponential limit (k -> infinity) is the t1_free_q_1 model.
GAMMA_SHAPES = tuple(float(k) for k in np.geomspace(0.25, 1000.0, 97))
GAMMA_NODES = 64
RESIDUAL_ARMS = ("measure", "unitary", "delay")
SENSITIVITY = ROOT / "docs/evidence/measurement_sequence/carryover-sensitivity.json"
# The successor's carryover screen: a quarter of the bound floor, one-sided bounds Bonferroni over the layout width.
CARRYOVER_MARGIN = 0.25 * 0.0188
FAMILY_ALPHA = 0.05
# A conditional difference needs this many shots on each side of the conditioning bit to enter a summary.
MIN_SIDE = 50
LARGE_Z = 3.0


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def final_bits(item: tuple[Path, str, str, list[str]]) -> list[bytes]:
    """The shot-ordered final bits of one PUB, one bytes string per layout qubit, after the file's digest check."""
    path, digest, name, registers = item
    data = path.read_bytes()
    require(hashlib.sha256(data).hexdigest() == digest, f"{path}: sha256 differs from index.json")
    pub = json.loads(data)
    require(pub["pub_name"] == name, f"{path}: PUB {pub['pub_name']} where the record names {name}")
    out = []
    for register in registers:
        entry = pub["registers"][register]
        require(entry["num_bits"] == 1, f"{path}: {register} holds {entry['num_bits']} bits")
        out.append("".join(entry["bitstrings"]).encode())
    return out


def load(run: Path) -> dict[str, Any]:
    record = json.loads((run / "record.json").read_text())
    (raw,) = sorted((run / "raw").iterdir())
    index = json.loads((raw / "index.json").read_text())
    metadata = (raw / RESULT_METADATA).read_bytes()
    require(hashlib.sha256(metadata).hexdigest() == index["files"][RESULT_METADATA], f"{raw}: metadata sha256 differs")
    chunks = json.loads(metadata)["executor"]["chunk_timing"]
    pubs = record["execution_pubs"]
    items = []
    for k, pub in enumerate(pubs):
        registers = []
        for component in pub["components"]:
            (replica,) = component["registers_by_replica"]
            finals = [r for r in replica if r.endswith("_final")]
            require(len(finals) == 1, f"{pub['name']}: {component['member']} has no single final register")
            registers.append(finals[0])
        name = f"pub_{k:02d}.json"
        items.append((raw / name, index["files"][name], pub["name"], registers))
    columns = ordered_map(final_bits, items, min_items=2)
    bits = np.array([[np.frombuffer(b, dtype=np.uint8) - ord("0") for b in row] for row in columns], dtype=np.int8)
    require(bool(np.all((bits == 0) | (bits == 1))), f"{raw}: a final bit is neither 0 nor 1")
    qubits = [int(component["physical_qubits"][0]) for component in pubs[0]["components"]]
    for pub in pubs:
        require(
            [int(c["physical_qubits"][0]) for c in pub["components"]] == qubits, f"{pub['name']}: layout order differs"
        )
    return {
        "record": record,
        "bits": bits,
        "members": [msa_class(pub["components"][0]["member"]) for pub in pubs],
        "qubits": qubits,
        "chunks": [[part["idx_item"] for part in chunk["parts"]] for chunk in chunks],
        "job_id": index["job_id"],
    }


def msa_class(member: str) -> str:
    """The member name without its qubit suffix, which names the row on every qubit."""
    head, _, tail = member.rpartition("_q")
    require(tail.isdigit(), f"{member}: no qubit suffix")
    return head


def conditional(current: np.ndarray, previous: np.ndarray) -> tuple[float, float] | None:
    """P(current = 1 | previous = 1) - P(current = 1 | previous = 0) and its binomial standard error.

    Each side's variance is at least that of one count in its shots, so a side that reads all zeros or all ones on a
    row near P1 = 0 or 1 cannot drive the standard error to zero.
    """
    ones, zeros = current[previous == 1], current[previous == 0]
    if ones.size < MIN_SIDE or zeros.size < MIN_SIDE:
        return None
    p1, p0 = float(ones.mean()), float(zeros.mean())
    se = math.sqrt(max(p1 * (1 - p1), 1.0 / ones.size) / ones.size + max(p0 * (1 - p0), 1.0 / zeros.size) / zeros.size)
    return p1 - p0, se


def lagged(bits: np.ndarray, k: int, g: int, back: int, offset: int) -> tuple[float, float] | None:
    current, previous = bits[k, g], bits[k - back, g]
    if offset > 0:
        current, previous = current[:-offset], previous[offset:]
    elif offset < 0:
        current, previous = current[-offset:], previous[:offset]
    return conditional(current, previous)


def adjacency(bits: np.ndarray, members: list[str]) -> dict[str, Any]:
    rows, groups = bits.shape[0], bits.shape[1]
    summaries = {}
    tables: dict[tuple[int, int], dict[int, list[float]]] = {}
    for back, offset in LAGS:
        cells = {}
        for k in range(back, rows):
            for g in range(groups):
                value = lagged(bits, k, g, back, offset)
                if value is not None:
                    cells[(k, g)] = value
        z = np.array([d / se for d, se in cells.values()])
        summaries[f"rows_back_{back}_shot_offset_{offset:+d}"] = {
            "cells": len(cells),
            "mean_z": float(z.mean()),
            "rms_z": float(math.sqrt(float((z * z).mean()))),
            "fraction_abs_z_above_3": float((np.abs(z) > LARGE_Z).mean()),
            "median_difference": float(np.median([d for d, _ in cells.values()])),
        }
        tables[(back, offset)] = {
            k: [cells[(k, g)][0] for g in range(groups) if (k, g) in cells] for k in range(back, rows)
        }
    per_row = []
    for k in range(1, rows):
        same, shifted = tables[(1, 0)][k], tables[(1, -1)][k]
        per_row.append(
            {
                "row": k,
                "member": members[k],
                "previous": members[k - 1],
                "p1": float(bits[k].mean()),
                "median_difference_same_shot": float(np.median(same)) if same else None,
                "median_difference_shot_minus_1": float(np.median(shifted)) if shifted else None,
            }
        )
    return {"lags": summaries, "per_row": per_row}


def carryover(bits: np.ndarray, members: list[str], qubits: list[int]) -> dict[str, Any]:
    (row,) = [k for k, m in enumerate(members) if m == "msq_ro0"]
    per_qubit = {}
    for g, qubit in enumerate(qubits):
        value = conditional(bits[row, g], bits[row - 1, g])
        if value is not None:
            per_qubit[str(qubit)] = {"difference": value[0], "se": value[1]}
    differences = [v["difference"] for v in per_qubit.values()]
    mean = float(np.mean(differences))
    se = math.sqrt(sum(v["se"] ** 2 for v in per_qubit.values())) / len(per_qubit)
    return {
        "row": row,
        "previous_member": members[row - 1],
        "previous_p1": float(bits[row - 1].mean()),
        "per_qubit": per_qubit,
        "median_difference": float(np.median(differences)),
        "mean_difference": mean,
        "mean_se": se,
    }


def pattern_carryover(
    bits: np.ndarray, members: list[str], qubits: list[int], screens: dict[str, Any]
) -> dict[str, Any]:
    """Per-qubit carryover D from consecutive pattern rows, conditioned on the predecessor row's prepared bit."""
    pattern = msqe_pattern_bits(len(qubits))
    prefix = "msqe_pat"
    per_qubit: dict[str, dict[str, Any]] = {}
    pairs = [
        (int(members[k - 1][len(prefix) :]), int(member[len(prefix) :]), k)
        for k, member in enumerate(members)
        if k and member.startswith(prefix) and members[k - 1].startswith(prefix)
    ]
    for g, qubit in enumerate(qubits):
        cells: dict[tuple[int, int], list[float]] = {(a, b): [] for a in (0, 1) for b in (0, 1)}
        for previous, current, row in pairs:
            cells[(pattern[previous][g], pattern[current][g])].append(float(bits[row, g].mean()))
        shots = int(bits.shape[2])
        estimates = []
        # Ground rows: P1 after a 1 minus after a 0. Excited rows: the x flips carried excitation to 0, so P1 after a 0
        # minus after a 1. Keys are (previous prepared bit, current prepared bit). Every row holds the same shots, so
        # the mean of row P1 is the pooled P1.
        for larger, smaller in (((1, 0), (0, 0)), ((0, 1), (1, 1))):
            a, b = np.array(cells[larger]), np.array(cells[smaller])
            pa, pb = float(a.mean()), float(b.mean())
            na, nb = a.size * shots, b.size * shots
            binomial = math.sqrt(max(pa * (1 - pa), 1.0 / na) / na + max(pb * (1 - pb), 1.0 / nb) / nb)
            between = math.sqrt(float(a.var(ddof=1)) / a.size + float(b.var(ddof=1)) / b.size)
            estimates.append((pa - pb, binomial, between))
        value = {}
        for label, column in (("binomial", 1), ("larger", None)):
            ses = [e[1] if column else max(e[1], e[2]) for e in estimates]
            weights = [1 / se**2 for se in ses]
            value[label] = (
                sum(w * e[0] for w, e in zip(weights, estimates, strict=True)) / sum(weights),
                1 / math.sqrt(sum(weights)),
            )
        per_qubit[str(qubit)] = {
            "difference": value["binomial"][0],
            "se": value["binomial"][1],
            "difference_larger_se": value["larger"][0],
            "se_larger": value["larger"][1],
            "pattern_screen_passes": bool(screens[str(qubit)]["patterns"]["passes"]),
            "ground_rows": dict(zip(("difference", "se", "se_between_rows"), estimates[0], strict=True)),
            "excited_rows": dict(zip(("difference", "se", "se_between_rows"), estimates[1], strict=True)),
            "rows": {f"previous_{a}_current_{b}": len(cells[(a, b)]) for a, b in sorted(cells)},
        }
    values = [v["difference"] for v in per_qubit.values()]
    clean = {q: v for q, v in per_qubit.items() if v["pattern_screen_passes"]}
    allocation = json.loads(SENSITIVITY.read_text())["run"]["allocation_coefficient"]["per_qubit"]
    z = float(norm.ppf(1 - FAMILY_ALPHA / len(qubits)))
    bias = {
        q: allocation[q] * (abs(v["difference_larger_se"]) + z * v["se_larger"])
        for q, v in per_qubit.items()
        if q in allocation
    }
    return {
        "row_pairs": len(pairs),
        "per_qubit": per_qubit,
        "median_difference": float(np.median(values)),
        "median_se": float(np.median([v["se"] for v in per_qubit.values()])),
        "mean_difference": float(np.mean(values)),
        "mean_se": math.sqrt(sum(v["se"] ** 2 for v in per_qubit.values())) / len(per_qubit),
        "pattern_screen_passing": {
            "qubits": len(clean),
            "mean_difference": float(np.mean([v["difference_larger_se"] for v in clean.values()])),
            "mean_se": math.sqrt(sum(v["se_larger"] ** 2 for v in clean.values())) / len(clean),
        },
        "screen": {
            "margin": CARRYOVER_MARGIN,
            "bonferroni_z": z,
            "allocation_model": "t1_q (carryover-sensitivity.json run section)",
            "bias_bound": bias,
            "passing": sum(1 for b in bias.values() if b < CARRYOVER_MARGIN),
            "passing_with_pattern_screen": sum(
                1 for q, b in bias.items() if b < CARRYOVER_MARGIN and per_qubit[q]["pattern_screen_passes"]
            ),
            "evaluated": len(bias),
        },
    }


def series(ones: np.ndarray, shots: int) -> tuple[list[float], list[float]]:
    """The bracket-corrected t1 series and its standard errors from the ro0 and t1 rows' ones counts."""
    p = ones / shots
    z0, z1 = 1 - 2 * p[0], 1 - 2 * p[1]
    scale, offset = (z0 - z1) / 2, (z0 + z1) / 2
    y = [((1 - 2 * pk) - offset) / scale for pk in p[1:]]
    se = [2 * math.sqrt(max(pk * (1 - pk), 1.0 / shots) / shots) / abs(scale) for pk in p[1:]]
    return y, se


def fit(delays: list[float], y: list[float], se: list[float], t1: float | None, q: float | None) -> dict[str, Any]:
    """Weighted least squares of y_k = q (1 - e_k) - e_k over the delays after the bracket, T1 and q free or fixed."""
    t = np.array(delays[1:])
    ys = np.array(y[1:])
    w = 1 / np.array(se[1:]) ** 2

    def at(lifetime: float) -> tuple[float, float]:
        e = np.exp(-t / lifetime)
        plateau = q if q is not None else float(np.sum(w * (1 - e) * (ys + e)) / np.sum(w * (1 - e) ** 2))
        return plateau, float(np.sum(w * (ys + e - plateau * (1 - e)) ** 2))

    if t1 is None:
        best = minimize_scalar(
            lambda u: at(math.exp(u))[1],
            bounds=(math.log(msa.T1_BOUNDS[0]), math.log(msa.T1_BOUNDS[1])),
            method="bounded",
            options={"xatol": 1e-10},
        )
        t1 = math.exp(float(best.x))
    plateau, statistic = at(t1)
    return {"t1_us": t1 * 1e6, "q": plateau, "chi2": statistic}


def gamma_fit(delays: list[float], y: list[float], se: list[float]) -> dict[str, Any]:
    """Weighted least squares of y_k = 1 - 2 (1 + t_k / (k T))^(-k), the mean lifetime T = 1 / mu profiled per shape."""
    t = np.array(delays[1:])
    ys = np.array(y[1:])
    w = 1 / np.array(se[1:]) ** 2
    best: dict[str, Any] | None = None
    for shape in GAMMA_SHAPES:

        def residual(u: float, shape: float = shape) -> float:
            survival = (1 + t / (shape * math.exp(u))) ** (-shape)
            return float(np.sum(w * (ys - (1 - 2 * survival)) ** 2))

        found = minimize_scalar(
            residual,
            bounds=(math.log(msa.T1_BOUNDS[0]), math.log(msa.T1_BOUNDS[1])),
            method="bounded",
            options={"xatol": 1e-10},
        )
        if best is None or float(found.fun) < best["chi2"]:
            best = {"mean_lifetime_us": math.exp(float(found.x)) * 1e6, "shape": shape, "chi2": float(found.fun)}
    if best is None:
        raise ValueError("empty gamma shape grid")
    dof = len(t) - 2
    return {**best, "dof": dof, "p_value": float(chi2.sf(best["chi2"], dof))}


def gamma_p0(arm: str, ctx: dict[str, Any], mean_lifetime_s: float, shape: float) -> float:
    """The arm's N = 16 P0 on the analysis's chain at q = 1, averaged over a gamma-distributed decay rate."""
    quantiles = (np.arange(GAMMA_NODES) + 0.5) / GAMMA_NODES
    rates = gamma_distribution.ppf(quantiles, shape, scale=1 / (shape * mean_lifetime_s))
    gate = msa.sx_gate(ctx, 0.0)
    tau = msa.tau_of(arm, ctx, msa.WINDOW_RELAX_FRACTION)
    total = 0.0
    for rate in rates.tolist():
        t1 = 1 / rate
        total += (1 + msa.corrected_z(arm, msa.TOP_STEPS, t1, min(ctx["t2_s"], 2 * t1), tau, 0.0, gate, 1.0)) / 2
    return total / GAMMA_NODES


def t1_models(item: tuple[int, list[float], float, np.ndarray, dict[str, Any], dict[str, Any]]) -> dict[str, Any]:
    qubit, delays, t1_cal, ones, ctx, p0 = item
    shots = ones.shape[1]
    y, se = series(ones.sum(axis=1), shots)
    models = {}
    for label, t1, q, free in (
        ("t1_free_q_free", None, None, 2),
        ("t1_calibrated_q_free", t1_cal, None, 1),
        ("t1_free_q_1", None, 1.0, 1),
        ("t1_calibrated_q_1", t1_cal, 1.0, 0),
    ):
        result = fit(delays, y, se, t1, q)
        dof = len(delays) - 1 - free
        models[label] = {**result, "dof": dof, "p_value": float(chi2.sf(result["chi2"], dof))}
    quarters = []
    for part in range(QUARTERS):
        window = ones[:, part * shots // QUARTERS : (part + 1) * shots // QUARTERS]
        qy, qse = series(window.sum(axis=1), window.shape[1])
        quarters.append(
            {"t1_free_q_free": fit(delays, qy, qse, None, None), "t1_free_q_1": fit(delays, qy, qse, None, 1.0)}
        )
    gamma = gamma_fit(delays, y, se)
    top = str(msa.TOP_STEPS)
    lifetime = gamma["mean_lifetime_us"] * 1e-6
    exponential = msa.model_tables(lifetime, 1.0, ctx, 0.0, msa.WINDOW_RELAX_FRACTION)
    residuals = {
        arm: {
            "analysis": p0[arm][top]["measured_minus_modeled"],
            "gamma_rate": p0[arm][top]["p0"] - gamma_p0(arm, ctx, lifetime, gamma["shape"]),
            "exponential_at_gamma_lifetime": p0[arm][top]["p0"] - exponential[arm][top],
        }
        for arm in RESIDUAL_ARMS
    }
    t2 = min(ctx["t2_s"], 2 * lifetime)
    gate = msa.sx_gate(ctx, 0.0)
    loss = msa.implied_loss(2 * p0["measure"][top]["p0"] - 1, lifetime, t2, ctx, 1.0, gate, msa.WINDOW_RELAX_FRACTION)
    settle_tau = msa.tau_of("settle", ctx, msa.WINDOW_RELAX_FRACTION)
    settle = msa.corrected_z("settle", msa.TOP_STEPS, lifetime, t2, settle_tau, loss, gate, 1.0)
    settle_gap = {
        "gap_q_1": p0["settle"][top]["p0"] - (1 + settle) / 2,
        "implied_loss_q_1": loss,
        "statistical_se": math.hypot(p0["settle"][top]["se"], p0["measure"][top]["se"]),
    }
    return {
        "qubit": qubit,
        "t1_calibrated_us": t1_cal * 1e6,
        "models": models,
        "quarters": quarters,
        "gamma_rate": gamma,
        "n16_residuals": residuals,
        "settle": settle_gap,
    }


def t1_section(loaded: dict[str, Any], collected: list[Any]) -> dict[str, Any]:
    record, bits, members, qubits = loaded["record"], loaded["bits"], loaded["members"], loaded["qubits"]
    executed: dict[str, Any] = {}
    for entry in collected[1:]:
        executed.update(entry["executed"])
    contexts = msa.contexts_from_record(record, executed)
    exploratory = json.loads(EXPLORATORY.read_text())["analysis"]
    uninformative = {int(q) for q in exploratory["device"]["uninformative_qubits"]}
    (ro0,) = [k for k, m in enumerate(members) if m == "msq_ro0"]
    rows = [ro0]
    for k in range(msa.T1_COUNT):
        (row,) = [i for i, m in enumerate(members) if m == msa_class(msa.t1_names(0)[k])]
        rows.append(row)
    items = [
        (
            q,
            list(contexts[q]["t1_delays_s"]),
            float(contexts[q]["t1_cal_s"]),
            bits[rows, g],
            contexts[q],
            exploratory["qubits"][str(q)]["p0"],
        )
        for g, q in enumerate(qubits)
        if q not in uninformative
    ]
    fits = ordered_map(t1_models, items, min_items=2)
    admitted = {label: sum(1 for f in fits if f["models"][label]["p_value"] >= 0.01) for label in fits[0]["models"]}
    admitted["gamma_rate"] = sum(1 for f in fits if f["gamma_rate"]["p_value"] >= 0.01)
    residuals = {
        arm: {
            model: {
                "median": float(np.median([f["n16_residuals"][arm][model] for f in fits])),
                "positive": sum(1 for f in fits if f["n16_residuals"][arm][model] > 0),
            }
            for model in ("analysis", "gamma_rate", "exponential_at_gamma_lifetime")
        }
        for arm in RESIDUAL_ARMS
    }
    return {
        "delays_us": [d * 1e6 for d in items[0][1]],
        "uninformative": sorted(uninformative),
        "per_qubit": {str(f["qubit"]): f for f in fits},
        "admitted_at_p_0_01": admitted,
        "n16_residuals": residuals,
        "rate_average_effect": {
            arm: max(
                abs(f["n16_residuals"][arm]["gamma_rate"] - f["n16_residuals"][arm]["exponential_at_gamma_lifetime"])
                for f in fits
            )
            for arm in RESIDUAL_ARMS
        },
        "settle_gap_q_1": {
            "median": float(np.median([f["settle"]["gap_q_1"] for f in fits])),
            "abs_z_at_least_3": sum(
                1 for f in fits if abs(f["settle"]["gap_q_1"]) >= 3 * f["settle"]["statistical_se"]
            ),
        },
        "informative": len(fits),
    }


def run(path: Path) -> dict[str, Any]:
    loaded = load(path)
    bits, members, qubits = loaded["bits"], loaded["members"], loaded["qubits"]
    collected = json.loads((path / "collect.json").read_text())
    screens = collected[0]["family_analysis"]["envelope"]["screens"]
    return {
        "schema": SCHEMA,
        "run": path.relative_to(ROOT).as_posix(),
        "job_id": loaded["job_id"],
        "rows": int(bits.shape[0]),
        "qubits": qubits,
        "shots": int(bits.shape[2]),
        "executor_chunks": loaded["chunks"],
        "adjacency": adjacency(bits, members),
        "carryover": carryover(bits, members, qubits),
        "pattern_carryover": pattern_carryover(bits, members, qubits, screens),
        "t1_series": t1_section(loaded, collected),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run", type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    args = parser.parse_args(argv)
    text = json.dumps(run(args.run.resolve()), indent=1, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text)
        return 0
    if args.check.read_text() != text:
        raise SystemExit(f"{args.check} differs from the recomputed diagnostics")
    print(f"{args.check}: reproduced")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
