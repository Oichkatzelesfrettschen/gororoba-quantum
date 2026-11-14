"""Bracketed-twin successor case of the Tuna-17 one-CZ null series: both coin twins of a template run in one batch
between the batch's own readouts.

The predecessor case (scripts/qi_pathion_one_cz_null_cases.py, module `oc`) runs the two coin twins of a template in one
batch beside one readout circuit (readout-0 in the forward round, readout-1 in the mirror). This case runs each pair as
[readout-0, coin-0 twin, coin-1 twin, readout-1] (the mirror round reverses the twins), four circuits per batch, which
the `wave-v1` hardware policy admits (qi_platform_wave.HARDWARE_POLICIES: five circuits per batch, three queued batches,
a wave of up to fifteen circuits, a 60 s pause after a wave). It keeps the predecessor's circuit texts, base batches,
calibration batches and routing by import, and it preregisters twin-control rule v2
(qi_pathion_one_cz_null_rule_v2.py) and the zero-error finite-count pooling of qi_pathion_one_cz_null_analysis.py
(`ana`) from the start. It runs four replicates of every template and kind at half the predecessor's shots per circuit
(REPLICATES, BATCH_SHOTS, CONTROL_SHOTS), and its batch heterogeneity gate is the alpha 0.001 chi-square quantile of the
replicates' degrees of freedom (BATCH_CHI2), where the predecessor's 10.828 is the quantile of one degree of freedom.

Estimator. The selector qubit's assignment errors e01 = P(read 1 | prepared 0) and e10 = P(read 0 | prepared 1) come
from the batch's own readout-0 and readout-1. A raw reading P of P(s = 0) is e10 + lambda p with lambda = 1 - e01 - e10
and p the ideal probability, so P - 1/2 = lambda (p - 1/2) + c with the bracket offset c = (e10 - e01) / 2. Both twins
of a pair carry the one bracket of their batch, so the twin contrast t = (P1 - c) - (P0 - c) = P1 - P0 is the
predecessor's raw contrast with variance v(P1) + v(P0) (`ana.arm_variance`): the offset cancels exactly, and its drift
between batches enters no contrast. The bracket reports c and the offset-corrected reading P - c of each twin
(`batch_brackets`), which the decision does not read.

Order. Four rounds of eight batches (`batch_order`): a forward round (the predecessor's oc.batch_order first round), its
mirror reversed, the forward round again and its mirror, then the three X-only calibration batches of `oc`: 35 batches,
which `waves` groups three to a wave (12 waves). A mirror round runs the coin-1 twin before the coin-0 twin, so a linear
drift per circuit position enters the forward and mirror replicates of t with opposite signs and cancels in the pooled
contrast to first order.

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
import qi_platform_wave  # noqa: E402

import parallel  # noqa: E402
import pathion_coset_analysis as pca  # noqa: E402
from qrng_seeds import read_record  # noqa: E402

TUNA_SERIES = "pathion_one_cz_null_bracketed_tuna_17"
QX_SERIES = "pathion_one_cz_null_bracketed_qx"
CASE_DIR = "results/quantum_inspire/cases"
SCHEMA = "qi-pathion-one-cz-null-bracketed-cases-v1"
SERIES_SCHEMA = "qi-pathion-one-cz-null-bracketed-series-v1"
ANALYSIS_SCHEMA = "qi-pathion-one-cz-null-bracketed-analysis-v1"
# The hardware policy the Tuna-17 case manifests select (qi_platform_wave.hardware_policy).
HARDWARE_POLICY = "wave-v1"
POLICY = qi_platform_wave.HARDWARE_POLICIES[HARDWARE_POLICY]
# Layout: four replicates of every template and kind at half the predecessor's shots per circuit, which keeps the
# series' 2,555,904 shots. The b0 base circuit keeps its fourfold share of a base circuit's shots, and the X-only
# calibration batches keep the predecessor's shots.
REPLICATES = 4
BATCH_SHOTS = oc.BATCH_SHOTS // 2
CONTROL_SHOTS = oc.CONTROL_SHOTS // 2
JOINT_SHOTS = oc.JOINT_SHOTS
# alpha 0.001 upper quantiles of chi-square by degrees of freedom (a table to three decimals, as the predecessor's
# oc.BATCH_CHI2 = 10.828); the batch gate of REPLICATES replicate batches has REPLICATES - 1 degrees of freedom.
CHI2_ALPHA_001 = {1: 10.828, 2: 13.816, 3: 16.266}
BATCH_CHI2 = CHI2_ALPHA_001[REPLICATES - 1]
# The retained one-CZ series' selector (physical q8) readout errors: the unweighted mean of the twelve readout-0 and
# twelve readout-1 references of the v3 analysis record. They size the design standard errors and the simulation.
RATES_RECORD = ana.SUCCESSOR_RECORD
SELECTOR_QUBIT = oc.JOINT_QUBITS["selector"]
# Operating characteristics: a new ANU QRNG draw, owned whole by the manifest-owned prediction record of this case. Each
# of the three tables seeds from its own value of the draw, indices in increasing order, each used once.
OC_DRAW = "docs/evidence/anu_qrng/draw-2026-11-14T183922Z.json"
OC_DRAWS = oc.OC_DRAWS
OC_DRIFT_SD = oc.OC_DRIFT_SD
STATIONARY_TABLE = "stationary"
CONTRAST_DRIFT_TABLE = f"batch_drift_sd_{OC_DRIFT_SD}"
PAIR_DRIFT_TABLE = f"pair_common_drift_sd_{OC_DRIFT_SD}"
OC_SEED_INDICES = {STATIONARY_TABLE: 920, CONTRAST_DRIFT_TABLE: 921, PAIR_DRIFT_TABLE: 922}


def batch_order() -> list[tuple[str, str, int]]:
    """(template, kind, replicate) of the 8 x REPLICATES template batches: the predecessor's forward round (the first
    round of oc.batch_order) at even replicates and its mirror, reversed, at odd ones, so each template's base and twin
    batches sit at mirrored positions and a linear drift cancels between a forward and a mirror replicate."""
    forward = [(t, k) for t, k, replicate in oc.batch_order() if replicate == 0]
    return [(t, k, r) for r in range(REPLICATES) for t, k in (forward if r % 2 == 0 else list(reversed(forward)))]


def row_shots(row: dict[str, Any]) -> int:
    """Shots of every circuit of a batch row: b0's base batches run at CONTROL_SHOTS, the other template batches at
    BATCH_SHOTS and the X-only calibration batches at JOINT_SHOTS."""
    if row["kind"] == "joint":
        return JOINT_SHOTS
    return CONTROL_SHOTS if row["kind"] == "base" and row["template"] == "b0" else BATCH_SHOTS


def batch_rows(series_name: str) -> list[dict[str, Any]]:
    """The batches of a series. Tuna-17: the 8 x REPLICATES template batches of `batch_order` (a base batch is
    [readout-0, template, readout-1]; a twin batch is [readout-0, coin-0 twin, coin-1 twin, readout-1] at an even
    replicate and [readout-0, coin-1 twin, coin-0 twin, readout-1] at an odd one), then the predecessor's three X-only
    calibration batches. QX: per template one batch [readout-0, coin-0 twin, coin-1 twin, readout-1, base circuit]."""
    rows: list[dict[str, Any]] = []
    readout = ({"file": "readout-0.cq", "kind": "readout"}, {"file": "readout-1.cq", "kind": "readout"})

    def twins(name: str, order: tuple[int, int]) -> list[dict[str, Any]]:
        return [{"file": oc.twin_file(name, coin), "kind": "data", "template": name, "coin": coin} for coin in order]

    if series_name == QX_SERIES:
        for name in oc.TEMPLATES:
            base = {"file": f"{name}.cq", "kind": "data", "template": name, "coin": None}
            rows.append(
                {
                    "batch": f"batch-{len(rows):02d}",
                    "kind": "control",
                    "template": name,
                    "replicate": None,
                    "circuits": [readout[0], *twins(name, (0, 1)), readout[1], base],
                }
            )
        return rows
    for name, kind, replicate in batch_order():
        base = {"file": f"{name}.cq", "kind": "data", "template": name, "coin": None}
        pair = twins(name, (0, 1) if replicate % 2 == 0 else (1, 0))
        rows.append(
            {
                "batch": f"batch-{len(rows):02d}",
                "kind": kind,
                "template": name,
                "replicate": replicate,
                "circuits": [readout[0], base, readout[1]] if kind == "base" else [readout[0], *pair, readout[1]],
            }
        )
    for joint in (r for r in oc.batch_rows(oc.TUNA_SERIES) if r["kind"] == "joint"):
        rows.append({**joint, "batch": f"batch-{len(rows):02d}"})
    return rows


def waves(rows: list[dict[str, Any]] | None = None) -> list[list[str]]:
    """The batches of the Tuna-17 series in submission waves: consecutive groups of the policy's queued batches. A
    wave's batches are submitted one after another in this order, which requests the series order from the platform,
    and the next wave waits until every batch of the wave has finished and the policy's pause has passed."""
    names = [r["batch"] for r in (batch_rows(TUNA_SERIES) if rows is None else rows)]
    return [names[i : i + POLICY.queued_batches] for i in range(0, len(names), POLICY.queued_batches)]


def preregistered() -> dict[str, str]:
    """The predecessor's preregistered rule with the estimates restated for the bracketed twin and twin rule v2."""
    text = oc.preregistered()
    text["estimates"] = (
        "per template and batch kind, the contrast of each batch, pooled over the replicate batches by inverse "
        "variance: base, the raw arm contrast P(s=0 | coin read 1) - P(s=0 | coin read 0); twin, t = (P1 - c) - "
        "(P0 - c) = P1 - P0 over the two coin twins of one batch, P the raw P(s=0) of a twin and c = (e10 - e01) / 2 "
        "the offset of the batch's own readout-0 and readout-1, which cancels in t; the variance of t sums the arm "
        "variances of P1 and P0, a deterministic arm taking the Agresti-Coull interval variance"
    )
    text["heterogeneity"] = (
        f"replicate batches of one template and kind agree within chi-square {BATCH_CHI2} ({REPLICATES - 1} degrees of "
        f"freedom, alpha 0.001: the quantile of this case's {REPLICATES} replicates, where the predecessor's "
        f"{oc.BATCH_CHI2} is the 1-degree-of-freedom value of its 2); the three 6-CZ blocks agree within chi-square "
        f"{oc.BLOCK_CHI2} (2 degrees of freedom, alpha 0.01) for the base contrasts and for the twin contrasts; "
        "otherwise the decision is unresolved"
    )
    text["twin_control"] = rule.TWIN_CONTROL
    return text


series = ana.rebound(
    oc.series,
    batch_rows=batch_rows,
    preregistered=preregistered,
    row_shots=row_shots,
    SCHEMA=SCHEMA,
    QX_SERIES=QX_SERIES,
)


def series_files(
    plan: dict[str, Any], backend: dict[str, Any], series_name: str, nqubits: int, place: dict[int, int]
) -> dict[str, str]:
    """The files of one series: the predecessor's builder over this module's batches, with the series index renamed.
    A Tuna-17 batch manifest names the `wave-v1` hardware policy (qi_platform_wave.hardware_policy), and the series
    index
    lists the submission waves."""
    files: dict[str, str] = series(plan, backend, series_name, nqubits, place)
    index = json.loads(files["cases.json"])
    index["schema"] = SERIES_SCHEMA
    if series_name == TUNA_SERIES:
        index["hardware_policy"] = HARDWARE_POLICY
        index["waves"] = waves()
        for name in list(files):
            if name.endswith("/cases.json"):
                manifest = json.loads(files[name])
                files[name] = json.dumps({**manifest, "hardware_policy": HARDWARE_POLICY}, indent=1) + "\n"
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


def bracket_offset(readout0_ones: int, shots0: int, readout1_zeros: int, shots1: int) -> tuple[float, float]:
    """(c, variance) of the batch's bracket offset c = (e10 - e01) / 2 from integer counts of the selector qubit:
    `readout0_ones` of `shots0` readout-0 shots read 1 (e01) and `readout1_zeros` of `shots1` readout-1 shots read 0
    (e10); the variance is a quarter of each arm variance."""
    e01 = readout0_ones / shots0
    e10 = readout1_zeros / shots1
    return (e10 - e01) / 2, (ana.arm_variance(e10, shots1) + ana.arm_variance(e01, shots0)) / 4


def twin_contrast(zeros1: int, shots1: int, zeros0: int, shots0: int) -> tuple[float, float]:
    """(t, se) of one batch from the selector's zero counts of its coin-1 and coin-0 twins. The batch's bracket offset
    c enters both readings, so (P1 - c) - (P0 - c) = P1 - P0 and the variance is v(P1) + v(P0)."""
    p1, p0 = zeros1 / shots1, zeros0 / shots0
    return p1 - p0, math.sqrt(ana.arm_variance(p1, shots1) + ana.arm_variance(p0, shots0))


def selector_counts(shots: dict[str, list[str]], batch: str, file: str, qubit: int) -> tuple[int, int]:
    """(zeros, shots) of the selector `qubit` in circuit `file` of `batch`."""
    listed = shots[f"{batch}/{file}"]
    return sum(1 for s in listed if pca.bit(s, qubit) == 0), len(listed)


def batch_brackets(shots: dict[str, list[str]], manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Per twin batch, the bracket offset c with its standard error and the offset-corrected reading P - c of each coin
    twin, from the batch's own readouts; the decision does not read these."""
    out: dict[str, dict[str, Any]] = {}
    for batch in sorted({key.split("/")[0] for key in shots}):
        twins: dict[int, str] = {}
        template = None
        for key in shots:
            name = key.split("/")[1]
            kind, found, coin = oc.parse_file(name)
            if key.startswith(f"{batch}/") and kind == "twin" and coin is not None:
                twins[coin], template = name, found
        if template is None:
            continue
        qubit = manifest["templates"][template]["roles"]["selector"]
        readout0, readout1 = shots[f"{batch}/readout-0.cq"], shots[f"{batch}/readout-1.cq"]
        c, variance = bracket_offset(
            sum(pca.bit(s, qubit) for s in readout0),
            len(readout0),
            sum(1 for s in readout1 if pca.bit(s, qubit) == 0),
            len(readout1),
        )
        corrected = {}
        for coin, file in sorted(twins.items()):
            zeros, n = selector_counts(shots, batch, file, qubit)
            corrected[str(coin)] = zeros / n - c
        out[batch] = {"template": template, "offset": c, "offset_se": math.sqrt(variance), "corrected_p": corrected}
    return out


def batch_estimates(
    shots: dict[str, list[str]], manifest: dict[str, Any]
) -> tuple[dict[str, dict[str, list[tuple[float, float]]]], dict[str, dict[str, dict[str, Any]]]]:
    """Per template and kind, the (value, se) of every batch, as the v3 analyzer reads them: a base contrast from its
    arms, a twin contrast P1 - P0 from the two twins of one batch (the bracket offset cancels, see `twin_contrast`).
    Each twin batch must hold its template's twins in the series layout."""
    layout = {row["batch"]: row for row in batch_rows(TUNA_SERIES)}
    for key in shots:
        batch, name = key.split("/")
        kind, template, _ = oc.parse_file(name)
        if kind == "twin" and (
            batch not in layout or layout[batch]["template"] != template or layout[batch]["kind"] != "twin"
        ):
            raise ValueError(f"{key} is not a twin that {batch} of the series layout holds")
    rows, detail = ana.batch_estimates(shots, manifest)
    return rows, detail


decide_estimates = partial(rule.decide_estimates, batch_chi2=BATCH_CHI2)
evaluate_decision = ana.rebound(
    oc.evaluate,
    batch_estimates=batch_estimates,
    decide_estimates=decide_estimates,
    joint_statistics=ana.joint_statistics,
    REPLICATES=REPLICATES,
)


def evaluate(
    shots: dict[str, list[str]], manifest: dict[str, Any], executed: dict[str, str] | None = None
) -> dict[str, Any]:
    """The rule-v2 decision of a complete Tuna-17 series, with the per-batch bracket offsets beside it."""
    record: dict[str, Any] = evaluate_decision(shots, manifest, executed)
    record["twin_brackets"] = batch_brackets(shots, manifest)
    return record


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
    bracket offset is 0 and each template's bracketed twin contrast (P1 - c) - (P0 - c) equals its raw contrast."""
    arms: dict[str, dict[str, int]] = {}
    contrasts: dict[str, dict[str, float]] = {}
    for row in batch_rows(QX_SERIES):
        batch, name = row["batch"], row["template"]
        qubit = manifest["templates"][name]["roles"]["selector"]
        zero, one = shots[f"{batch}/readout-0.cq"], shots[f"{batch}/readout-1.cq"]
        arms[batch] = {
            "readout_0_selector_ones": sum(pca.bit(s, qubit) for s in zero),
            "readout_1_selector_zeros": sum(1 for s in one if pca.bit(s, qubit) == 0),
        }
        c, _ = bracket_offset(
            arms[batch]["readout_0_selector_ones"], len(zero), arms[batch]["readout_1_selector_zeros"], len(one)
        )
        p = {coin: selector_counts(shots, batch, oc.twin_file(name, coin), qubit) for coin in (0, 1)}
        contrasts[name] = {
            "bracketed": (p[1][0] / p[1][1] - c) - (p[0][0] / p[0][1] - c),
            "raw": p[1][0] / p[1][1] - p[0][0] / p[0][1],
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
    shots_total = sum(row_shots(r) * len(r["circuits"]) for r in rows)
    n = BATCH_SHOTS
    twin_se = math.sqrt(2 * ana.arm_variance(0.5, n))
    offset_se = math.sqrt((ana.arm_variance(e10, n) + ana.arm_variance(e01, n)) / 4)
    reused = ana.rebound(oc.design, BATCH_SHOTS=BATCH_SHOTS, CONTROL_SHOTS=CONTROL_SHOTS, REPLICATES=REPLICATES)()
    wave_list = waves(rows)
    wave_pause = POLICY.pause_seconds
    if wave_pause is None:
        raise ValueError(f"hardware policy {HARDWARE_POLICY} names no pause between waves")
    return {
        "unit": "standard errors in micro-units (10^-6), seconds in tenths, rates in ten-thousandths, chi-square bound "
        "in thousandths",
        "base_batch_se_micro": micro(reused["base_batch_se"]),
        "b0_base_batch_se_micro": micro(reused["b0_base_batch_se"]),
        "twin_batch_se_micro": micro(twin_se),
        "bracket_offset_se_micro": micro(offset_se),
        "pooled_se_micro": {
            "base": micro(reused["pooled_se"]["base"]),
            "b0_base": micro(reused["pooled_se"]["b0_base"]),
            "twin": micro(twin_se / math.sqrt(REPLICATES)),
        },
        "calibration_se_micro": {k: micro(v) for k, v in reused["calibration_se"].items()},
        "calibration_se_limit_micro": micro(reused["calibration_se_limit"]),
        "design_selector_readout_e01_e10_ten_thousandths": [round(e01 * 1e4), round(e10 * 1e4)],
        "hardware_policy": HARDWARE_POLICY,
        "replicates": REPLICATES,
        "shots_per_circuit": {"b0_base": CONTROL_SHOTS, "template": BATCH_SHOTS, "calibration": JOINT_SHOTS},
        "batch_chi2_thousandths": round(BATCH_CHI2 * 1000),
        "batch_chi2_degrees_of_freedom": REPLICATES - 1,
        "jobs": jobs,
        "batches": len(rows),
        "waves": len(wave_list),
        "circuits_per_batch_max": max(len(r["circuits"]) for r in rows),
        "circuits_per_wave_max": max(sum(len(r["circuits"]) for r in rows if r["batch"] in wave) for wave in wave_list),
        "shots_total": shots_total,
        "execution_seconds_range_tenths": [
            round(10 * (jobs * 2.6 + shots_total * 0.53e-3)),
            round(10 * (jobs * 2.6 + shots_total * timing["seconds_per_shot_max"])),
        ],
        "longest_job_seconds_tenths": round(
            10 * (2.6 + max(row_shots(r) for r in rows) * timing["seconds_per_shot_max"])
        ),
        "job_seconds_limit": 300,
        "pause_seconds_per_wave": wave_pause,
        "pause_seconds_total": wave_pause * (len(wave_list) - 1),
        "coin_series_seconds_per_shot_nanoseconds": [
            round(timing["seconds_per_shot_min"] * 1e9),
            round(timing["seconds_per_shot_max"] * 1e9),
        ],
    }


# Operating characteristics --------------------------------------------------------------------------------------

# Drift models of the stress table. "contrast": an independent drift of standard deviation `drift_sd` on every base
# contrast and every twin contrast, the predecessor's convention (oc.operating_characteristics). "pair": the drift of
# a batch is common to the two twins of its pair, so it cancels in the twin contrast and only the base contrasts
# drift.
DRIFT_MODELS = ("contrast", "pair")


def _series_label(
    draw: tuple[np.ndarray, ...],
    *,
    mean: dict[str, float],
    se_base: dict[str, float],
    shots: int,
    band: float,
    decide: Callable[..., dict[str, Any]],
) -> str:
    """The decision label of one simulated series. `draw` holds, over (template, replicate), the standard normal base
    noise, the base drift, the selector's zero counts of the coin-0 and coin-1 twins of the batch and the twin
    contrast drift; the twin contrast is the estimator `twin_contrast` of those integer counts."""
    base_noise, base_drift, zeros, twin_drift = draw
    rows: dict[str, dict[str, list[tuple[float, float]]]] = {}
    for j, name in enumerate(oc.TEMPLATES):
        key = "b0" if name == "b0" else "k"
        twin = []
        for r in range(REPLICATES):
            value, se = twin_contrast(int(zeros[j, r, 1]), shots, int(zeros[j, r, 0]), shots)
            twin.append((value + float(twin_drift[j, r]), se))
        rows[name] = {
            "base": [
                (mean[f"s_{key}"] + se_base[name] * float(base_noise[j, r]) + float(base_drift[j, r]), se_base[name])
                for r in range(REPLICATES)
            ],
            "twin": twin,
        }
    return str(decide(rows, band)["label"])


def operating_characteristics(
    seed_index: int,
    draws: int = OC_DRAWS,
    drift_sd: float = 0.0,
    b0_like_z: float | None = None,
    worlds: dict[str, dict[str, float]] | None = None,
    drift_model: str = "contrast",
) -> dict[str, dict[str, float]]:
    """Frequency of each rule-v2 label per world, from `draws` simulated series, seeded from QRNG value `seed_index` of
    OC_DRAW (OC_SEED_INDICES names the index of each table). A base contrast is a Gaussian draw at the design standard
    error; the two twins of a batch draw binomial
    selector zero counts at P = 1/2 + c -/+ t / 2 (c the design bracket offset), so the twin contrast carries its real
    estimator noise. The drift of standard deviation `drift_sd` follows `drift_model` (DRIFT_MODELS): added to every
    base contrast and twin contrast independently, or to the base contrasts only, because a drift shared by the two
    twins of a batch cancels in their difference. Every series' counts and drift are drawn, world by world, before any
    series is decided; the decisions run through parallel.ordered_map in series order."""
    if drift_model not in DRIFT_MODELS:
        raise ValueError(f"drift_model {drift_model!r} is not one of {DRIFT_MODELS}")
    band = oc.B0_LIKE_Z if b0_like_z is None else b0_like_z
    worlds = rule.WORLDS if worlds is None else worlds
    e01, e10 = retained_selector_rates()
    shots = BATCH_SHOTS
    se_base = {t: 1.0 / math.sqrt(CONTROL_SHOTS if t == "b0" else BATCH_SHOTS) for t in oc.TEMPLATES}
    rng = np.random.default_rng(int(read_record(OC_DRAW)["values"][seed_index]))
    shape = (draws, len(oc.TEMPLATES), REPLICATES)
    drawn: dict[str, list[tuple[np.ndarray, ...]]] = {}
    for world, mean in worlds.items():
        t_mean = np.array([mean["t_b0" if t == "b0" else "t_k"] for t in oc.TEMPLATES])
        # P(s = 0) of a twin: 1/2 + (2 coin - 1) t / 2 on the corrected scale, plus its batch's bracket offset.
        p_read = 0.5 + (e10 - e01) / 2 + np.array([-0.5, 0.5]) * t_mean[:, None]
        base_noise = rng.normal(size=shape)
        base_drift = rng.normal(scale=drift_sd, size=shape)
        zeros = rng.binomial(shots, p_read[:, None, :], size=(*shape, 2))
        twin_drift = rng.normal(scale=drift_sd, size=shape)
        if drift_model == "pair":
            twin_drift = np.zeros(shape)
        drawn[world] = list(zip(base_noise, base_drift, zeros, twin_drift, strict=True))
    out: dict[str, dict[str, float]] = {}
    for world, items in drawn.items():
        labels = parallel.ordered_map(
            partial(
                _series_label,
                mean=worlds[world],
                se_base=se_base,
                shots=shots,
                band=band,
                decide=decide_estimates,
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
        "model": "raw selector contrast of the base circuit (s) and of the in-batch bracketed coin-twin pair (t) of "
        "b0 and of a 6-CZ block under each hypothesis, as in the predecessor case "
        "(docs/evidence/pathion-kernel-map/conjectures/c2_one_cz_mech.txt and c2_one_cz_twins.txt), plus the "
        "negative-twin world of rule v2",
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
            STATIONARY_TABLE: operating_characteristics(OC_SEED_INDICES[STATIONARY_TABLE]),
            CONTRAST_DRIFT_TABLE: operating_characteristics(
                OC_SEED_INDICES[CONTRAST_DRIFT_TABLE], drift_sd=OC_DRIFT_SD
            ),
            PAIR_DRIFT_TABLE: operating_characteristics(
                OC_SEED_INDICES[PAIR_DRIFT_TABLE], drift_sd=OC_DRIFT_SD, drift_model="pair"
            ),
        }
        record["operating_characteristics"] = {
            "qrng_draw": OC_DRAW,
            "seed_indices": dict(OC_SEED_INDICES),
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
