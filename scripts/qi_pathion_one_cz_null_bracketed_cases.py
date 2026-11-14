"""Bracketed-twin successor case of the Tuna-17 one-CZ null series: every coin twin runs between its own readouts.

The predecessor case (scripts/qi_pathion_one_cz_null_cases.py, module `oc`) runs both coin twins of a template in one
batch beside one readout circuit, so a twin batch carries no bracket. This case runs each twin as [readout-0, twin,
readout-1], within the platform's three circuits per batch (qi_platform.HARDWARE_BATCH_CIRCUITS; a pair plus a bracket
is four), and the two twins of a pair sit in adjacent batches. It keeps the predecessor's circuit texts, base batches,
calibration batches and routing by import, and it preregisters twin-control rule v2 (qi_pathion_one_cz_null_rule_v2.py)
and the zero-error finite-count pooling of qi_pathion_one_cz_null_analysis.py (`ana`) from the start.

Estimator. The selector qubit's assignment errors e01 = P(read 1 | prepared 0) and e10 = P(read 0 | prepared 1) come
from the batch's own readout-0 and readout-1. A raw reading P of P(s = 0) is e10 + lambda p with lambda = 1 - e01 - e10
and p the ideal probability, so P - 1/2 = lambda (p - 1/2) + c with the bracket offset c = (e10 - e01) / 2. The twin
reading of a batch is P - c and the twin contrast of a replicate is t = (P1 - c1) - (P0 - c0) over the coin-1 and coin-0
batches. Equal brackets reduce t to the raw P1 - P0 of the predecessor; its expectation is lambda1 (p1 - 1/2) -
lambda0 (p0 - 1/2), the raw scale of `oc.PREDICTED`; it is linear in the measured rates, so its variance is the sum of
the arm variances of P, e10 and e01 with weights 1, 1/4 and 1/4 per batch (`ana.arm_variance`).

Order. A forward round of twelve batches (batch_order) and its mirror reversed, then the three X-only calibration
batches of `oc`: 27 batches. The mirror runs the coin-1 twin before the coin-0 twin, so a linear drift per batch enters
the two replicates of t with opposite signs and cancels in the pooled contrast.

Usage: "$PYTHON" scripts/qi_pathion_one_cz_null_bracketed_cases.py
       (--write DIR | --check DIR | --operating-characteristics | --sanity RUN_DIR... | --analyze RUN_DIR... --out FILE
        | --qx-check COUNTS_JSON)
Bit strings put qubit 0 at the rightmost character."""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections.abc import Callable
from functools import partial
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import qi_pathion_coset_block_series as pcs  # noqa: E402
import qi_pathion_coset_coin_cases as cc  # noqa: E402
import qi_pathion_one_cz_null_analysis as ana  # noqa: E402
import qi_pathion_one_cz_null_cases as oc  # noqa: E402
import qi_pathion_one_cz_null_rule_v2 as rule  # noqa: E402
import qi_platform  # noqa: E402

import parallel  # noqa: E402
import pathion_coset_analysis as pca  # noqa: E402
from qrng_seeds import read_record  # noqa: E402

TUNA_SERIES = "pathion_one_cz_null_bracketed_tuna_17"
QX_SERIES = "pathion_one_cz_null_bracketed_qx"
CASE_DIR = "results/quantum_inspire/cases"
SCHEMA = "qi-pathion-one-cz-null-bracketed-cases-v1"
SERIES_SCHEMA = "qi-pathion-one-cz-null-bracketed-series-v1"
ANALYSIS_SCHEMA = "qi-pathion-one-cz-null-bracketed-analysis-v1"
HARDWARE_BATCH_CIRCUITS = qi_platform.HARDWARE_BATCH_CIRCUITS
# The bracketed twin batch: [readout-0, twin, readout-1].
TWIN_BATCH_CIRCUITS = 3
REPLICATES = oc.REPLICATES
# Twelve batches of the forward round as (template, kind, coin): each template's base batch and its two twin batches
# (coin 0 then coin 1), in the order of the predecessor's forward round.
FORWARD = (
    ("b0", "base", None),
    ("b0", "twin", 0),
    ("b0", "twin", 1),
    ("k4", "twin", 0),
    ("k4", "twin", 1),
    ("k4", "base", None),
    ("k8", "base", None),
    ("k8", "twin", 0),
    ("k8", "twin", 1),
    ("k12", "twin", 0),
    ("k12", "twin", 1),
    ("k12", "base", None),
)
# The retained one-CZ series' selector (physical q8) readout errors: the unweighted mean of the twelve readout-0 and
# twelve readout-1 references of the v3 analysis record. They size the design standard errors and the simulation.
RATES_RECORD = ana.SUCCESSOR_RECORD
SELECTOR_QUBIT = oc.JOINT_QUBITS["selector"]
# Operating characteristics: a new ANU QRNG draw, registered by the manifest-owned prediction record of this case.
OC_DRAW = "docs/evidence/anu_qrng/draw-2026-11-14T183922Z.json"
OC_SEED_INDEX = 0
OC_SEED = int(read_record(OC_DRAW)["values"][OC_SEED_INDEX])
OC_DRAWS = oc.OC_DRAWS
OC_DRIFT_SD = oc.OC_DRIFT_SD


def batch_order() -> list[tuple[str, str, int | None, int]]:
    """(template, kind, coin, replicate) of the twenty-four template batches: the forward round and its mirror."""
    return [(t, k, c, 0) for t, k, c in FORWARD] + [(t, k, c, 1) for t, k, c in reversed(FORWARD)]


def _twin_spec(name: str, coin: int) -> dict[str, Any]:
    return {"file": oc.twin_file(name, coin), "kind": "data", "template": name, "coin": coin}


def batch_rows(series_name: str) -> list[dict[str, Any]]:
    """The batches of a series. Tuna-17: the twenty-four template batches of batch_order (a base batch is [readout-0,
    template, readout-1]; a twin batch is [readout-0, twin, readout-1]), then the predecessor's three X-only calibration
    batches. QX: per template a batch [readout-0, coin-0 twin, readout-1, base] and a batch [readout-0, coin-1 twin,
    readout-1], so every bracket stays inside its batch (a batch keys its circuits by file name)."""
    rows: list[dict[str, Any]] = []
    readout = ({"file": "readout-0.cq", "kind": "readout"}, {"file": "readout-1.cq", "kind": "readout"})
    if series_name == QX_SERIES:
        for name in oc.TEMPLATES:
            base = {"file": f"{name}.cq", "kind": "data", "template": name, "coin": None}
            for value, extra in ((0, [base]), (1, [])):
                rows.append(
                    {
                        "batch": f"batch-{len(rows):02d}",
                        "kind": "control",
                        "template": name,
                        "replicate": None,
                        "coin": value,
                        "circuits": [readout[0], _twin_spec(name, value), readout[1], *extra],
                    }
                )
        return rows
    for name, kind, coin, replicate in batch_order():
        data = {"file": f"{name}.cq", "kind": "data", "template": name, "coin": None} if coin is None else None
        rows.append(
            {
                "batch": f"batch-{len(rows):02d}",
                "kind": kind,
                "template": name,
                "replicate": replicate,
                "coin": coin,
                "circuits": [readout[0], data if coin is None else _twin_spec(name, coin), readout[1]],
            }
        )
    for joint in (r for r in oc.batch_rows(oc.TUNA_SERIES) if r["kind"] == "joint"):
        rows.append({**joint, "batch": f"batch-{len(rows):02d}", "coin": None})
    return rows


def preregistered() -> dict[str, str]:
    """The predecessor's preregistered rule with the estimates restated for the bracketed twin and twin rule v2."""
    text = oc.preregistered()
    text["estimates"] = (
        "per template and batch kind, the contrast of each batch, pooled over the replicate batches by inverse "
        "variance: base, the raw arm contrast P(s=0 | coin read 1) - P(s=0 | coin read 0); twin, t = (P1 - c1) - "
        "(P0 - c0) over the coin-1 and coin-0 twin batches of one replicate, P the raw P(s=0) of the twin and "
        "c = (e10 - e01) / 2 the bracket offset of its own batch from the selector's assignment errors e01 (readout-0) "
        "and e10 (readout-1); the variance of t sums, per batch, the arm variance of P and a quarter of each arm "
        "variance of e01 and e10, a deterministic arm taking the Agresti-Coull interval variance"
    )
    text["twin_control"] = rule.TWIN_CONTROL
    return text


series = ana.rebound(oc.series, batch_rows=batch_rows, preregistered=preregistered, SCHEMA=SCHEMA, QX_SERIES=QX_SERIES)


def series_files(
    plan: dict[str, Any], backend: dict[str, Any], series_name: str, nqubits: int, place: dict[int, int]
) -> dict[str, str]:
    """The files of one series: the predecessor's builder over this module's batches, with the series index renamed."""
    files: dict[str, str] = series(plan, backend, series_name, nqubits, place)
    index = json.loads(files["cases.json"])
    index["schema"] = SERIES_SCHEMA
    files["cases.json"] = json.dumps(index, indent=1) + "\n"
    return files


build = ana.rebound(oc.build, series=series_files, TUNA_SERIES=TUNA_SERIES, QX_SERIES=QX_SERIES)
write = ana.rebound(
    oc.write, build=build, predictions=lambda: predictions(), TUNA_SERIES=TUNA_SERIES, QX_SERIES=QX_SERIES
)
check = ana.rebound(
    oc.check,
    build=build,
    predictions=lambda operating=True: predictions(operating),
    TUNA_SERIES=TUNA_SERIES,
    QX_SERIES=QX_SERIES,
)
series_of = ana.rebound(oc.series_of, TUNA_SERIES=TUNA_SERIES, QX_SERIES=QX_SERIES)
sanity = ana.rebound(oc.sanity, series_of=series_of)


# Estimator ------------------------------------------------------------------------------------------------------


def retained_selector_rates() -> tuple[float, float]:
    """(e01, e10) of the selector: the means of the retained references of the one-CZ series (RATES_RECORD)."""
    references = json.loads((ROOT / RATES_RECORD).read_text(encoding="utf-8"))["drift_covariate"]["references"][
        "references"
    ]
    rates = {
        kind: [float(r["rates"][str(SELECTOR_QUBIT)]) for r in references if r["kind"] == kind]
        for kind in ("e01", "e10")
    }
    if not rates["e01"] or len(rates["e01"]) != len(rates["e10"]):
        raise ValueError(f"{RATES_RECORD} holds no complete selector reference set")
    return sum(rates["e01"]) / len(rates["e01"]), sum(rates["e10"]) / len(rates["e10"])


def twin_reading(
    zeros: int, shots: int, readout0_ones: int, shots0: int, readout1_zeros: int, shots1: int
) -> tuple[float, float]:
    """(P - c, variance) of one twin batch from integer counts of the selector qubit: `zeros` of `shots` twin shots
    read 0, `readout0_ones` of `shots0` readout-0 shots read 1 (e01) and `readout1_zeros` of `shots1` readout-1 shots
    read 0 (e10); c = (e10 - e01) / 2."""
    p = zeros / shots
    e01 = readout0_ones / shots0
    e10 = readout1_zeros / shots1
    variance = ana.arm_variance(p, shots) + (ana.arm_variance(e10, shots1) + ana.arm_variance(e01, shots0)) / 4
    return p - (e10 - e01) / 2, variance


def twin_contrast(coin1: tuple[float, float], coin0: tuple[float, float]) -> tuple[float, float]:
    """(t, se) of one replicate from the readings (value, variance) of its coin-1 and coin-0 batches."""
    return coin1[0] - coin0[0], math.sqrt(coin1[1] + coin0[1])


def batch_reading(shots: dict[str, list[str]], batch: str, file: str, qubit: int) -> tuple[float, float]:
    """The twin reading of `batch`: the selector `qubit` of its twin circuit `file` against its own readout pair."""
    twin, zero, one = shots[f"{batch}/{file}"], shots[f"{batch}/readout-0.cq"], shots[f"{batch}/readout-1.cq"]
    return twin_reading(
        sum(1 for s in twin if pca.bit(s, qubit) == 0),
        len(twin),
        sum(pca.bit(s, qubit) for s in zero),
        len(zero),
        sum(1 for s in one if pca.bit(s, qubit) == 0),
        len(one),
    )


def batch_estimates(
    shots: dict[str, list[str]], manifest: dict[str, Any]
) -> tuple[dict[str, dict[str, list[tuple[float, float]]]], dict[str, dict[str, dict[str, Any]]]]:
    """Per template and kind, the (value, se) of every batch: base contrasts as the exact v3 analyzer reads them (the
    twin keys left out of its call, since it pairs twins inside one batch), twin contrasts from the bracketed
    readings of the coin-1 and coin-0 batches of each replicate (paired by this series' batch layout)."""
    layout = {row["batch"]: row for row in batch_rows(TUNA_SERIES)}
    rows, detail = ana.batch_estimates(
        {k: v for k, v in shots.items() if oc.parse_file(k.split("/")[1])[0] != "twin"}, manifest
    )
    readings: dict[tuple[str, int, int], tuple[float, float]] = {}
    for key in sorted(shots):
        batch, name = key.split("/")
        kind, template, coin = oc.parse_file(name)
        if kind != "twin" or template is None or coin is None:
            continue
        row = layout[batch]
        if (row["template"], row["coin"]) != (template, coin):
            raise ValueError(f"{key} is not the twin that {batch} of the series layout holds")
        readings[(template, row["replicate"], coin)] = batch_reading(
            shots, batch, name, manifest["templates"][template]["roles"]["selector"]
        )
    for template in rows:
        for replicate in range(REPLICATES):
            pair = [readings.get((template, replicate, coin)) for coin in (1, 0)]
            if pair[0] is None or pair[1] is None:
                raise ValueError(f"{template} replicate {replicate} lacks a coin twin batch")
            rows[template]["twin"].append(twin_contrast(pair[0], pair[1]))
    return rows, detail


evaluate = ana.rebound(
    oc.evaluate,
    batch_estimates=batch_estimates,
    decide_estimates=rule.decide_estimates,
    joint_statistics=ana.joint_statistics,
)
analyze_series = ana.rebound(
    oc.analyze,
    evaluate=evaluate,
    ANALYSIS_SCHEMA=ANALYSIS_SCHEMA,
    batch_rows=batch_rows,
    series_of=series_of,
    TUNA_SERIES=TUNA_SERIES,
    QX_SERIES=QX_SERIES,
)


def qx_brackets(shots: dict[str, list[str]], manifest: dict[str, Any]) -> dict[str, Any]:
    """The bracket arithmetic on the noiseless emulator: every readout arm of the selector misassigns no shot, every
    bracket offset is 0 and each template's bracketed twin contrast equals its raw contrast P1 - P0."""
    rows = {row["batch"]: row for row in batch_rows(QX_SERIES)}
    readings: dict[tuple[str, int], tuple[float, float]] = {}
    raw: dict[tuple[str, int], float] = {}
    arms: dict[str, dict[str, int]] = {}
    for batch, row in rows.items():
        qubit = manifest["templates"][row["template"]]["roles"]["selector"]
        file = oc.twin_file(row["template"], row["coin"])
        zero, one = shots[f"{batch}/readout-0.cq"], shots[f"{batch}/readout-1.cq"]
        arms[batch] = {
            "readout_0_selector_ones": sum(pca.bit(s, qubit) for s in zero),
            "readout_1_selector_zeros": sum(1 for s in one if pca.bit(s, qubit) == 0),
        }
        readings[(row["template"], row["coin"])] = batch_reading(shots, batch, file, qubit)
        twin = shots[f"{batch}/{file}"]
        raw[(row["template"], row["coin"])] = sum(1 for s in twin if pca.bit(s, qubit) == 0) / len(twin)
    contrasts = {
        t: {
            "bracketed": twin_contrast(readings[(t, 1)], readings[(t, 0)])[0],
            "raw": raw[(t, 1)] - raw[(t, 0)],
        }
        for t in oc.TEMPLATES
    }
    deterministic = all(v == 0 for arm in arms.values() for v in arm.values())
    equal = all(math.isclose(c["bracketed"], c["raw"], rel_tol=0.0, abs_tol=1e-12) for c in contrasts.values())
    return {"readout_misassigned_shots": arms, "twin_contrasts": contrasts, "pass": deterministic and equal}


def analyze(run_dirs: list[Path], case_root: Path | None = pcs.CASES_ROOT) -> dict[str, Any]:
    """Score collected batches of one series: a Tuna-17 series reports its batch list while incomplete and the rule-v2
    decision once complete; a QX series reports the control verdict and the bracket arithmetic a Tuna-17 submission
    needs."""
    record: dict[str, Any] = analyze_series(run_dirs, case_root)
    if record["claim_kind"] == oc.CONTROL_KIND and record["complete"]:
        data = pca.read_series(run_dirs, case_root, series_of, "data", oc.BATCH_FIELDS, pcs.load_run)
        record["qx_brackets"] = qx_brackets(data["shots"], data["shared"])
    return record


def qx_check(counts: dict[str, dict[str, int]]) -> dict[str, Any]:
    """The QX control of a local qxelarator run: `counts` maps "batch/file" to the result histogram of each circuit of
    the QX series; every data circuit is read against its ideal law of record and the bracket arithmetic is checked."""
    files = build()[QX_SERIES]
    manifests = {row["batch"]: json.loads(files[f"{row['batch']}/cases.json"]) for row in batch_rows(QX_SERIES)}
    shots = {key: [s for s, n in sorted(hist.items()) for _ in range(n)] for key, hist in counts.items()}
    arms = {
        f"{batch}/{row['file']}": (
            shots[f"{batch}/{row['file']}"],
            cases["templates"][row["template"]]["roles"],
            row["ideal"],
        )
        for batch, cases in manifests.items()
        for row in cases["circuits"]
        if row["kind"] == "data"
    }
    shared = manifests["batch-00"]
    return {
        "qx_control": pca.control_report(arms, cc.coin_counts),
        "qx_brackets": qx_brackets(shots, shared),
    }


# Design ---------------------------------------------------------------------------------------------------------


def micro(value: float) -> int:
    """10^6 x a value, as an integer: the unit of the standard errors of the float-free prediction record."""
    return round(value * 1e6)


def design() -> dict[str, Any]:
    """Standard errors, jobs, shots and seconds of the series as integers (no float enters the record): standard errors
    in micro-units, seconds in tenths. A twin batch reads P = 1/2 against the retained selector errors e01 and e10."""
    e01, e10 = retained_selector_rates()
    timing = oc.coin_timing()
    rows = batch_rows(TUNA_SERIES)
    jobs = sum(len(r["circuits"]) for r in rows)
    shots_total = sum(oc.row_shots(r) * len(r["circuits"]) for r in rows)
    n = oc.BATCH_SHOTS
    reading_variance = ana.arm_variance(0.5, n) + (ana.arm_variance(e10, n) + ana.arm_variance(e01, n)) / 4
    twin_se = math.sqrt(2 * reading_variance)
    raw_twin_se = math.sqrt(2 * ana.arm_variance(0.5, n))
    reused = oc.design()
    return {
        "unit": "standard errors in micro-units (10^-6), seconds in tenths, rates in ten-thousandths",
        "base_batch_se_micro": micro(reused["base_batch_se"]),
        "b0_base_batch_se_micro": micro(reused["b0_base_batch_se"]),
        "twin_batch_se_micro": micro(twin_se),
        "raw_twin_batch_se_micro": micro(raw_twin_se),
        "pooled_se_micro": {
            "base": micro(reused["pooled_se"]["base"]),
            "b0_base": micro(reused["pooled_se"]["b0_base"]),
            "twin": micro(twin_se / math.sqrt(REPLICATES)),
            "raw_twin": micro(raw_twin_se / math.sqrt(REPLICATES)),
        },
        "calibration_se_micro": {k: micro(v) for k, v in reused["calibration_se"].items()},
        "calibration_se_limit_micro": micro(reused["calibration_se_limit"]),
        "design_selector_readout_e01_e10_ten_thousandths": [round(e01 * 1e4), round(e10 * 1e4)],
        "jobs": jobs,
        "batches": len(rows),
        "circuits_per_batch_max": max(len(r["circuits"]) for r in rows),
        "shots_total": shots_total,
        "execution_seconds_range_tenths": [
            round(10 * (jobs * 2.6 + shots_total * 0.53e-3)),
            round(10 * (jobs * 2.6 + shots_total * timing["seconds_per_shot_max"])),
        ],
        "longest_job_seconds_tenths": round(
            10 * (2.6 + max(oc.row_shots(r) for r in rows) * timing["seconds_per_shot_max"])
        ),
        "job_seconds_limit": 300,
        "pause_seconds_per_batch": 30,
        "pause_seconds_total": 30 * (len(rows) - 1),
        "coin_series_seconds_per_shot_nanoseconds": [
            round(timing["seconds_per_shot_min"] * 1e9),
            round(timing["seconds_per_shot_max"] * 1e9),
        ],
    }


# Operating characteristics --------------------------------------------------------------------------------------


def _series_label(
    draw: tuple[np.ndarray, ...],
    *,
    mean: dict[str, float],
    se_base: dict[str, float],
    shots: int,
    band: float,
    decide: Callable[..., dict[str, Any]],
) -> str:
    """The decision label of one simulated series. `draw` holds, over (template, replicate[, coin]), the standard
    normal base noise, the base drift, and for each twin batch the selector's zero count in the twin, the one count in
    readout-0, the zero count in readout-1 and the drift of the reading; the twin contrast is the estimator
    (`twin_reading`, `twin_contrast`) of those integer counts."""
    base_noise, base_drift, zeros, ones0, zeros1, twin_drift = draw
    rows: dict[str, dict[str, list[tuple[float, float]]]] = {}
    for j, name in enumerate(oc.TEMPLATES):
        key = "b0" if name == "b0" else "k"
        twin = []
        for r in range(REPLICATES):
            readings = [
                twin_reading(int(zeros[j, r, c]), shots, int(ones0[j, r, c]), shots, int(zeros1[j, r, c]), shots)
                for c in (0, 1)
            ]
            readings = [(value + float(twin_drift[j, r, c]), var) for c, (value, var) in enumerate(readings)]
            twin.append(twin_contrast(readings[1], readings[0]))
        rows[name] = {
            "base": [
                (mean[f"s_{key}"] + se_base[name] * float(base_noise[j, r]) + float(base_drift[j, r]), se_base[name])
                for r in range(REPLICATES)
            ],
            "twin": twin,
        }
    return str(decide(rows, band)["label"])


def operating_characteristics(
    draws: int = OC_DRAWS,
    drift_sd: float = 0.0,
    b0_like_z: float | None = None,
    worlds: dict[str, dict[str, float]] | None = None,
) -> dict[str, dict[str, float]]:
    """Frequency of each rule-v2 label per world, from `draws` simulated series, seeded from QRNG value OC_SEED_INDEX of
    OC_DRAW. A base contrast is a Gaussian draw at the design standard error; a twin batch draws binomial counts of its
    twin circuit and of its two readouts at the design rates, so the bracket noise enters through the real estimator,
    and an independent per-batch drift of standard deviation `drift_sd` is added to every base contrast and to every
    twin reading (a twin contrast carries sqrt(2) times it). Every series' counts and drift are drawn, world by world,
    before any series is decided; the decisions run through parallel.ordered_map in series order."""
    band = oc.B0_LIKE_Z if b0_like_z is None else b0_like_z
    worlds = rule.WORLDS if worlds is None else worlds
    e01, e10 = retained_selector_rates()
    shots = oc.BATCH_SHOTS
    se_base = {t: 1.0 / math.sqrt(oc.CONTROL_SHOTS if t == "b0" else oc.BATCH_SHOTS) for t in oc.TEMPLATES}
    rng = np.random.default_rng(OC_SEED)
    shape = (draws, len(oc.TEMPLATES), REPLICATES)
    drawn: dict[str, list[tuple[np.ndarray, ...]]] = {}
    for world, mean in worlds.items():
        t_mean = np.array([mean["t_b0" if t == "b0" else "t_k"] for t in oc.TEMPLATES])
        # P(s = 0) of a twin batch: 1/2 + (2 coin - 1) t / 2 on the corrected scale, plus its bracket offset.
        p_read = 0.5 + (e10 - e01) / 2 + np.array([-0.5, 0.5]) * t_mean[:, None]
        base_noise = rng.normal(size=shape)
        base_drift = rng.normal(scale=drift_sd, size=shape)
        zeros = rng.binomial(shots, p_read[:, None, :], size=(*shape, 2))
        ones0 = rng.binomial(shots, e01, size=(*shape, 2))
        zeros1 = rng.binomial(shots, e10, size=(*shape, 2))
        twin_drift = rng.normal(scale=drift_sd, size=(*shape, 2))
        drawn[world] = list(zip(base_noise, base_drift, zeros, ones0, zeros1, twin_drift, strict=True))
    out: dict[str, dict[str, float]] = {}
    for world, items in drawn.items():
        labels = parallel.ordered_map(
            partial(
                _series_label,
                mean=worlds[world],
                se_base=se_base,
                shots=shots,
                band=band,
                decide=rule.decide_estimates,
            ),
            items,
        )
        counts: dict[str, int] = {}
        for label in labels:
            counts[label] = counts.get(label, 0) + 1
        out[world] = {label: round(n / draws, 4) for label, n in sorted(counts.items())}
    return out


# Predictions ----------------------------------------------------------------------------------------------------


def predictions(operating: bool = True) -> dict[str, Any]:
    """The prediction record, float-free (contrasts and shares in ten-thousandths, standard errors in micro-units);
    `operating` adds the operating characteristics, OC_DRAWS simulated series per world."""
    record: dict[str, Any] = {
        "model": "raw selector contrast of the base circuit (s) and of the bracketed coin-twin pair (t) of b0 and of a "
        "6-CZ block under each hypothesis, as in the predecessor case (docs/evidence/pathion-kernel-map/conjectures/"
        "c2_one_cz_mech.txt and c2_one_cz_twins.txt), plus the negative-twin world of rule v2",
        "unit": "contrasts and shares in ten-thousandths: 164 is 0.0164, 9706 is a share of 0.9706",
        "predicted_contrast": {
            w: {k: rule.ten_thousandths(v) for k, v in mean.items()} for w, mean in rule.WORLDS.items()
        },
        "outside_admitted_set": list(oc.OUTSIDE_ADMITTED),
        "design": design(),
        "preregistered": preregistered(),
        "outcomes": {label: {"outcome": v[0], "a5_186": v[1]} for label, v in rule.OUTCOMES.items()},
    }
    if operating:
        tables = {
            "stationary": operating_characteristics(),
            f"batch_drift_sd_{OC_DRIFT_SD}": operating_characteristics(drift_sd=OC_DRIFT_SD),
        }
        record["operating_characteristics"] = {
            "qrng_draw": OC_DRAW,
            "seed_index": OC_SEED_INDEX,
            "draws_per_world": OC_DRAWS,
            **{
                key: {
                    w: {label: rule.ten_thousandths(share) for label, share in row.items()} for w, row in table.items()
                }
                for key, table in tables.items()
            },
        }
    return record


def expand(counts: dict[str, Any]) -> dict[str, dict[str, int]]:
    """The result histograms of a local-run file: circuit key -> {bit string: count}."""
    return {key: {str(s): int(n) for s, n in hist.items()} for key, hist in counts["results"].items()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--operating-characteristics", action="store_true")
    mode.add_argument("--sanity", type=Path, nargs="+", metavar="RUN_DIR")
    mode.add_argument("--analyze", type=Path, nargs="+", metavar="RUN_DIR")
    mode.add_argument("--qx-check", type=Path, metavar="COUNTS_JSON")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.write:
        write(args.write)
    elif args.check:
        check(args.check)
    elif args.operating_characteristics:
        print(json.dumps(predictions()["operating_characteristics"], indent=1, sort_keys=True))
    elif args.sanity:
        print(json.dumps(sanity(args.sanity), indent=1, sort_keys=True))
    elif args.qx_check:
        report = qx_check(expand(json.loads(args.qx_check.read_text(encoding="utf-8"))))
        print(json.dumps(report, indent=1, sort_keys=True, allow_nan=False))
        return 0 if report["qx_control"]["pass"] and report["qx_brackets"]["pass"] else 1
    else:
        if args.out is None:
            parser.error("--analyze needs --out")
        with args.out.open("x", encoding="utf-8") as handle:
            handle.write(ana.record_text(analyze(args.analyze)))
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
