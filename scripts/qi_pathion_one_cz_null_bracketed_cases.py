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
contrast to first order. The platform sets the execution order, so the decision does not assume the requested order: it
fits the drift on the position offsets that the per-job start stamps give (`evaluate`, `twin_offsets`,
qi_pathion_one_cz_null_executed_order.py), `order_gate` records which batches kept their order, the base levels are
read at their executed times (`base_level_rows`) and a line in executed time must describe the bracket offsets
(`bracket_series`).

Usage: "$PYTHON" scripts/qi_pathion_one_cz_null_bracketed_cases.py
       (--write DIR | --check DIR | --operating-characteristics | --sanity RUN_DIR... | --analyze RUN_DIR... --out FILE
        | --qx-check COUNTS_JSON)
Bit strings put qubit 0 at the rightmost character."""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections.abc import Callable, Mapping
from datetime import UTC, datetime, timedelta
from functools import cache, partial
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import qi_pathion_coset_block_series as pcs  # noqa: E402
import qi_pathion_coset_coin_cases as cc  # noqa: E402
import qi_pathion_one_cz_null_analysis as ana  # noqa: E402
import qi_pathion_one_cz_null_cases as oc  # noqa: E402
import qi_pathion_one_cz_null_executed_order as eo  # noqa: E402
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


def control_preregistered() -> dict[str, str]:
    """The rule text of the QX control manifests: the predecessor's preregistered rule with the estimates restated for
    the bracketed twin and twin rule v2, and the plain pool of the batch contrasts. The hosted QX run's receipts bind
    the sha256 of these manifests, so the text keeps its bytes; the control decides no twin series and reads no
    stamp."""
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


def preregistered() -> dict[str, str]:
    """The preregistered rule of the Tuna-17 series: the control text with the estimates restated on the executed
    order, and the executed-order, base-level, drift-monitor and withheld-label rules (owner ruling 2026-11-16, issue
    791). Every label `evaluate` can read is one of rule.OUTCOMES and WITHHELD_LABELS."""
    text = control_preregistered()
    text["estimates"] = (
        "per template and batch kind, the contrast of each batch, read on the order and the times the provider "
        "executed it (the instant of each job's queued_at, in integer microseconds) and pooled by inverse variance: "
        "base, the raw arm contrast P(s=0 | coin read 1) - P(s=0 | coin read 0); twin, t = (P1 - c) - (P0 - c) = "
        "P1 - P0 over the two coin twins of one batch, P the raw P(s=0) of a twin and c = (e10 - e01) / 2 the offset "
        "of the batch's own readout-0 and readout-1, which cancels in t; the variance of t sums the arm variances of "
        "P1 and P0, a deterministic arm taking the Agresti-Coull interval variance; the twin and base rows enter the "
        "pool as the executed_order and base_level rules correct them"
    )
    text["executed_order"] = (
        "v_b = t_T + g x_b + e_b over the twin batches b by weighted least squares, one drift g shared by every twin "
        "batch, one contrast t_T per template and x_b the executed place of the coin-1 twin minus that of the coin-0 "
        "twin among the circuits of batch b; each twin row is reduced by g x_b and its error multiplied by "
        "sqrt(1 + x_T^2 var(g) W_T); the template contrasts pool with the covariance x_T x_U var(g) that the shared "
        "drift gives them"
    )
    text["base_level"] = (
        "the base level of a template is read at the mean executed time of its twin circuits through a weighted line "
        "over its four base replicates at their executed times; each base row is reduced by the slope times its time "
        "offset and its error multiplied by sqrt(1 + (t_w - tau)^2 / S_tt)"
    )
    text["drift_monitor"] = (
        "the bracket offset c of each of the 32 base and twin batches, placed at the mean executed time of its two "
        "readouts, fits a line in time within the alpha 0.001 chi-square quantile of n - 2 degrees of freedom; the "
        "slope bound g_up |t - tau| of each X-only calibration batch is reported beside the decision"
    )
    text["withheld"] = (
        "the decision is withheld, the first of these in order, as unresolved_order (a start stamp is missing, null, "
        "not an ISO 8601 instant with an offset, or two circuits of a twin batch start at one instant), "
        "unresolved_order_confounded (every template keeps one position offset), unresolved_base_drift_confounded (a "
        "template's base replicates share one start time), unresolved_drift_model (the monitor refuses the line) and "
        "unresolved_drift_heterogeneity (a template's own drift departs from the shared drift by more than 3 errors of "
        "the difference); the label of the pool that ignores the order stays beside the reading"
    )
    return text


series = ana.rebound(
    oc.series,
    batch_rows=batch_rows,
    preregistered=preregistered,
    row_shots=row_shots,
    SCHEMA=SCHEMA,
    QX_SERIES=QX_SERIES,
)
control_series = ana.rebound(
    oc.series,
    batch_rows=batch_rows,
    preregistered=control_preregistered,
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
    files: dict[str, str] = (series if series_name == TUNA_SERIES else control_series)(
        plan, backend, series_name, nqubits, place
    )
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


@cache
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


def order_gate(executed: Mapping[str, object] | None) -> dict[str, Any] | None:
    """Whether every batch ran its circuits in the requested order, read from the provider's per-job start stamps.

    The record is a reading beside the decision: the decision reads the executed order through `executed_twin_fit`
    and no reordered batch withholds it. `executed` maps "batch/file" to the job's `queued_at`, which in the retained
    Tuna-17 series follows the previous job's `finished_at` by 0.03 to 0.19 s and so orders the executions (measured on
    the 19 retained batches of the predecessor series; provider behavior, not a documented guarantee). The queue fixes
    the order requested, not the order executed (the provider's terms allow priority without regard to the queue): 7 of
    those 19 batches ran out of the requested order. A batch whose stamps order its circuits otherwise, tie two of them
    at one instant, or lack, null or malform one is not intact (issue 894). None when no stamps are read.
    """
    if not executed:
        return None
    batches: dict[str, dict[str, Any]] = {}
    rows = list(batch_rows(TUNA_SERIES))
    for row in rows:
        requested = [circuit["file"] for circuit in row["circuits"]]
        instants: dict[str, int] = {}
        missing: list[str] = []
        for name in requested:
            try:
                instants[name] = stamp_instant(executed.get(f"{row['batch']}/{name}"))
            except UnusableOrder:
                missing.append(name)
        if missing:
            batches[row["batch"]] = {"requested": requested, "executed": [], "intact": False, "missing_stamps": missing}
            continue
        ran = sorted(requested, key=lambda name: instants[name])
        tied = len(set(instants.values())) < len(requested)
        batches[row["batch"]] = {"requested": requested, "executed": ran, "intact": ran == requested and not tied}
    return {
        "batches": batches,
        "intact": len(batches) == len(rows) and all(entry["intact"] for entry in batches.values()),
    }


class UnusableOrder(ValueError):
    """The start stamps of a series cannot order its circuits: none were read, one is missing, null or not an ISO 8601
    instant with an offset, or two circuits of a twin batch start at one instant. The executed-order rule decides
    nothing then (`unresolved_order`)."""


EPOCH = datetime(1970, 1, 1, tzinfo=UTC)


def stamp_instant(stamp: object) -> int:
    """Integer microseconds since the epoch of a start stamp: ISO 8601 text with an explicit UTC offset (the provider's
    stamps read `2026-11-08T01:23:38.076340Z`). A stamp ranks by its instant, so `...:38Z` and `...:38.000000Z` are
    one instant and an offset other than Z orders correctly; digits of a fraction beyond six truncate, which can only
    tie two stamps. A missing, null, non-text, malformed or offset-free stamp is UnusableOrder."""
    if not isinstance(stamp, str):
        raise UnusableOrder(f"a start stamp is {stamp!r}, not ISO 8601 text")
    try:
        when = datetime.fromisoformat(stamp)
    except ValueError as error:
        raise UnusableOrder(f"start stamp {stamp!r} is not ISO 8601") from error
    if when.utcoffset() is None:
        raise UnusableOrder(f"start stamp {stamp!r} carries no UTC offset")
    return (when - EPOCH) // timedelta(microseconds=1)


def series_instants(executed: Mapping[str, object] | None) -> dict[str, int]:
    """The instant of every circuit of the Tuna-17 series layout ("batch/file" keys). Every circuit needs a usable
    stamp (UnusableOrder otherwise); a key outside the layout is ignored, since nothing reads it."""
    if not executed:
        raise UnusableOrder("no start stamps were read")
    instants: dict[str, int] = {}
    absent: list[str] = []
    for row in batch_rows(TUNA_SERIES):
        for circuit in row["circuits"]:
            key = f"{row['batch']}/{circuit['file']}"
            try:
                instants[key] = stamp_instant(executed.get(key))
            except UnusableOrder as error:
                absent.append(f"{key}: {error}")
    if absent:
        raise UnusableOrder(f"{len(absent)} circuits lack a usable start stamp, first {absent[0]}")
    return instants


# A template whose own drift departs from the shared drift by more than this many errors of the difference reads
# `unresolved_drift_heterogeneity` (rule 3 of docs/design/bracketed-executed-order-analysis.md).
DRIFT_HETEROGENEITY_SE = 3.0
# Floor of the own-drift departure, per executed position. When one template alone varies its offset, its own drift and
# the shared drift are one quantity, the error of their difference is zero and the two sums differ by rounding (about
# 2e-18 measured at drifts of 1e-2): a departure below the floor is that rounding.
DRIFT_DEPARTURE_FLOOR = 1e-12


def twin_layout() -> dict[str, tuple[str, str, str]]:
    """Per twin batch of the Tuna-17 series, (template, coin-0 twin file, coin-1 twin file)."""
    return {
        row["batch"]: (row["template"], oc.twin_file(row["template"], 0), oc.twin_file(row["template"], 1))
        for row in batch_rows(TUNA_SERIES)
        if row["kind"] == "twin"
    }


def twin_offsets(executed: Mapping[str, object] | None) -> dict[str, int]:
    """Executed position offset x of every twin batch: the executed place of its coin-1 twin minus that of its coin-0
    twin among the circuits of the batch, ordered by start instant.

    Every circuit of every batch of the series needs a usable stamp (`series_instants`), and no two circuits of a twin
    batch may start at one instant; otherwise UnusableOrder."""
    instants = series_instants(executed)
    rows = {row["batch"]: row for row in batch_rows(TUNA_SERIES)}
    offsets: dict[str, int] = {}
    for batch, (_, coin0, coin1) in twin_layout().items():
        stamps = {c["file"]: instants[f"{batch}/{c['file']}"] for c in rows[batch]["circuits"]}
        try:
            offsets[batch] = eo.executed_offset(stamps, coin0, coin1)
        except eo.ConfoundedOrder as error:
            raise UnusableOrder(f"{batch}: {error}") from error
    return offsets


def twin_batch_ids(contrasts: dict[str, dict[str, list[Any]]]) -> dict[str, list[str]]:
    """The twin batches of each template in the order `batch_estimates` lists their contrasts (sorted by batch)."""
    ids: dict[str, list[str]] = {template: [] for template in contrasts}
    for batch, (template, _, _) in sorted(twin_layout().items()):
        ids[template].append(batch)
    for template, listed in ids.items():
        if len(listed) != len(contrasts[template]["twin"]):
            raise ValueError(f"{template} holds {len(contrasts[template]['twin'])} twin contrasts, not {len(listed)}")
    return ids


def executed_twin_fit(
    contrasts: dict[str, dict[str, list[Any]]], offsets: dict[str, int]
) -> tuple[dict[str, dict[str, list[tuple[float, float]]]], dict[str, Any]]:
    """The rows rule v2 pools under the executed-order rule, and the fit beside them.

    `contrasts` is the record's `batch_contrasts` (per template the (value, se) of every base and twin batch).
    Each twin value is reduced by the shared drift times its batch's executed offset and its error is inflated by the
    drift's uncertainty (`qi_pathion_one_cz_null_executed_order.adjusted_rows`); a batch run in the requested order has
    the offset the layout requests, so a series that kept its order is pooled to the same value as the plain pool.
    ConfoundedOrder when no template varies its offset (no separable drift)."""
    ids = twin_batch_ids(contrasts)
    fit_rows = {
        template: [
            (float(v), float(se), float(offsets[batch]))
            for (v, se), batch in zip(c["twin"], ids[template], strict=True)
        ]
        for template, c in contrasts.items()
    }
    adjusted = eo.adjusted_rows(fit_rows)
    rows = {
        template: {"base": [(float(v), float(se)) for v, se in c["base"]], "twin": adjusted[template]}
        for template, c in contrasts.items()
    }
    fitted = eo.fit(fit_rows)
    fitted["offsets"] = {batch: offsets[batch] for template in ids for batch in ids[template]}
    return rows, fitted


# The labels the executed-order rule withholds a decision under, in the order they are read, and the text of each.
WITHHELD_LABELS = (
    "unresolved_order",
    "unresolved_order_confounded",
    "unresolved_base_drift_confounded",
    "unresolved_drift_model",
    "unresolved_drift_heterogeneity",
)
OUTCOMES: dict[str, tuple[str, str]] = {
    **rule.OUTCOMES,
    "unresolved_order": (
        "unresolved: the start stamps cannot order the circuits (one is missing, null, not an ISO 8601 instant with an "
        "offset, or two circuits of a twin batch start at one instant)",
        "unchanged; the numbers are reported",
    ),
    "unresolved_order_confounded": (
        "unresolved: every template keeps one executed position offset in all its twin batches, so the drift and the "
        "contrasts are not separable",
        "unchanged; the numbers are reported",
    ),
    "unresolved_base_drift_confounded": (
        "unresolved: the base replicates of a template share one start time, so the drift and the base level are not "
        "separable",
        "unchanged; the numbers are reported",
    ),
    "unresolved_drift_model": (
        "unresolved: the bracket offsets are not a line in executed time",
        "unchanged; the numbers are reported",
    ),
    "unresolved_drift_heterogeneity": (
        "unresolved: a template's own drift departs from the drift shared by the twin batches",
        "unchanged; the numbers are reported",
    ),
}


def unresolved(record: dict[str, Any], label: str, why: str) -> None:
    """Replace the decision by an undecided `label`; the label of the plain pool and of the fit stay beside it."""
    outcome, effect = OUTCOMES[label]
    decision = record["decision"]
    record["decision"] = {
        **decision,
        "label": label,
        "outcome": outcome,
        "a5_186": effect,
        "decided": False,
        "label_if_order_ignored": record["order_ignored_label"],
        "why": why,
    }


# One-sided 95 percent normal quantile: the upper bound of the monitor slope that sizes the calibration systematic.
SLOPE_BOUND_Z = statistics.NormalDist().inv_cdf(0.95)


def circuit_seconds(executed: Mapping[str, object]) -> dict[str, float]:
    """Executed start of every circuit of the series layout, in seconds after the series' first start ("batch/file"
    keys); UnusableOrder when a stamp is missing or unusable (`series_instants`)."""
    instants = series_instants(executed)
    origin = min(instants.values())
    return {key: (value - origin) / 1e6 for key, value in instants.items()}


def twin_reference_times(seconds: dict[str, float]) -> dict[str, float]:
    """Per template, the mean executed time of its twin circuits: the time at which the base level is estimated."""
    listed: dict[str, list[float]] = {template: [] for template in oc.TEMPLATES}
    for batch, (template, coin0, coin1) in twin_layout().items():
        listed[template] += [seconds[f"{batch}/{coin0}"], seconds[f"{batch}/{coin1}"]]
    return {template: sum(times) / len(times) for template, times in listed.items()}


def base_batch_ids() -> dict[str, list[str]]:
    """The base batches of each template in the order `batch_estimates` lists their contrasts (sorted by batch)."""
    ids: dict[str, list[str]] = {template: [] for template in oc.TEMPLATES}
    for row in sorted(batch_rows(TUNA_SERIES), key=lambda r: r["batch"]):
        if row["kind"] == "base":
            ids[row["template"]].append(row["batch"])
    return ids


def bracket_series(
    shots: dict[str, list[str]], manifest: dict[str, Any], seconds: dict[str, float]
) -> tuple[list[float], ...]:
    """(times, offsets, errors) of the bracket offset c of every base and twin batch: each batch's own readouts give
    one reading of the selector offset, placed at the mean executed start of its two readout circuits."""
    times: list[float] = []
    values: list[float] = []
    ses: list[float] = []
    for row in sorted(batch_rows(TUNA_SERIES), key=lambda r: r["batch"]):
        if row["kind"] not in ("base", "twin"):
            continue
        batch = row["batch"]
        qubit = manifest["templates"][row["template"]]["roles"]["selector"]
        zero, one = shots[f"{batch}/readout-0.cq"], shots[f"{batch}/readout-1.cq"]
        c, variance = bracket_offset(
            sum(pca.bit(s, qubit) for s in zero), len(zero), sum(1 for s in one if pca.bit(s, qubit) == 0), len(one)
        )
        times.append((seconds[f"{batch}/readout-0.cq"] + seconds[f"{batch}/readout-1.cq"]) / 2)
        values.append(c)
        ses.append(math.sqrt(variance))
    return times, values, ses


def calibration_readings(
    shots: dict[str, list[str]], manifest: dict[str, Any], seconds: dict[str, float]
) -> list[dict[str, Any]]:
    """Per X-only calibration batch, its mean executed start and the largest finite-count standard error of the
    selector's misassignment rate over its circuits."""
    qubit = manifest["joint_qubits"]["selector"]
    out: list[dict[str, Any]] = []
    for row in batch_rows(TUNA_SERIES):
        if row["kind"] != "joint":
            continue
        errors = []
        for circuit in row["circuits"]:
            prepared = int(circuit["file"].removeprefix("joint-").removesuffix(".cq")[1])
            listed = shots[f"{row['batch']}/{circuit['file']}"]
            rate = sum(1 for s in listed if pca.bit(s, qubit) != prepared) / len(listed)
            errors.append(math.sqrt(ana.arm_variance(rate, len(listed))))
        started = [seconds[f"{row['batch']}/{c['file']}"] for c in row["circuits"]]
        out.append({"batch": row["batch"], "time": sum(started) / len(started), "se": max(errors)})
    return out


def base_level_rows(
    contrasts: dict[str, dict[str, list[Any]]], seconds: dict[str, float]
) -> tuple[dict[str, list[tuple[float, float]]], dict[str, Any]]:
    """Per template, the base rows rule v2 pools under the executed-time weights and the level fit beside them: the
    base level at the mean executed time of the template's twin circuits, from a weighted line through the replicates
    at their executed times (`qi_pathion_one_cz_null_executed_order.level_rows`). ConfoundedOrder when the replicates
    of a template share one start time."""
    ids = base_batch_ids()
    reference = twin_reference_times(seconds)
    rows: dict[str, list[tuple[float, float]]] = {}
    fits: dict[str, Any] = {}
    for template, c in contrasts.items():
        if len(ids[template]) != len(c["base"]):
            raise ValueError(f"{template} holds {len(c['base'])} base contrasts, not {len(ids[template])}")
        times = [seconds[f"{batch}/{template}.cq"] for batch in ids[template]]
        adjusted, fit = eo.level_rows(
            [v for v, _ in c["base"]], [se for _, se in c["base"]], times, reference[template]
        )
        rows[template] = adjusted
        fits[template] = {**fit, "reference_time": reference[template], "times": times}
    return rows, fits


def decide_correlated(
    rows: dict[str, dict[str, list[tuple[float, float]]]],
    covariance: dict[str, dict[str, float]],
    b0_like_z: float | None = None,
) -> dict[str, Any]:
    """The rule-v2 decision of corrected per-batch rows when the twin contrasts of different templates are correlated.

    `covariance` is the matrix of the template twin contrasts that `qi_pathion_one_cz_null_executed_order.fit`
    returns. The ladder is that of `rule.decide_estimates` with three statistics read through the covariance: the
    pooled 6-CZ twin contrast d and its chi-square over the three blocks (generalized least squares,
    `eo.pool_correlated`), and the error of r - m, where t0 and d share the drift g. A diagonal covariance gives the
    decision of `rule.decide_estimates` (a test pins it)."""
    band = oc.B0_LIKE_Z if b0_like_z is None else b0_like_z
    z = oc.Z_RESOLVE
    low = list(oc.LOW_NAMES)
    base = {t: ana.pooled(rows[t]["base"]) for t in oc.TEMPLATES}
    twin = {t: ana.pooled(rows[t]["twin"]) for t in oc.TEMPLATES}
    batch_q = {f"{t}/{kind}": ana.heterogeneity(rows[t][kind]) for t in oc.TEMPLATES for kind in ("base", "twin")}
    mean, error, twin_q, weights = eo.pool_correlated(
        [twin[t][0] for t in low], [[covariance[t][u] for u in low] for t in low]
    )
    d = (mean, error)
    block_q = {"base": ana.heterogeneity([base[t] for t in low]), "twin": twin_q}
    s0, t0 = base["b0"], twin["b0"]
    c = ana.pooled([base[t] for t in low])
    m, r = ana.pooled([c, d]), ana.pooled([s0, t0])
    share_t0 = (1.0 / t0[1] ** 2) / (1.0 / s0[1] ** 2 + 1.0 / t0[1] ** 2)
    share_d = (1.0 / d[1] ** 2) / (1.0 / c[1] ** 2 + 1.0 / d[1] ** 2)
    shared = sum(w * covariance["b0"][t] for w, t in zip(weights, low, strict=True))
    diff = r[0] - m[0]
    diff_se = math.sqrt(r[1] ** 2 + m[1] ** 2 - 2.0 * share_t0 * share_d * shared)
    numbers = {
        "s_b0": s0,
        "t_b0": t0,
        "c_six_cz_base": c,
        "d_six_cz_twin": d,
        "m_six_cz": m,
        "r_b0": r,
        "r_minus_m": (diff, diff_se),
        "batch_chi2": batch_q,
        "block_chi2": block_q,
    }
    if any(q > BATCH_CHI2 for q in batch_q.values()):
        label = "unresolved_batch"
    elif any(q > oc.BLOCK_CHI2 for q in block_q.values()):
        label = "unresolved_block"
    elif s0[0] < z * s0[1]:
        label = "offset_absent"
    elif t0[0] < z * t0[1]:
        gap = (s0[0] - t0[0]) / math.hypot(s0[1], t0[1])
        label = "superposition_only" if gap >= z else "unresolved"
        if label == "superposition_only" and t0[0] < -z * t0[1]:
            label = rule.NEGATIVE_TWIN
    elif abs(c[0] - d[0]) > z * math.hypot(c[1], d[1]):
        label = "unresolved_context"
    elif abs(m[0]) <= z * m[1] and diff >= z * diff_se:
        label = "zero"
    elif m[0] >= z * m[1] and abs(diff) <= band * diff_se:
        label = "b0_like"
    elif m[0] >= z * m[1]:
        label = "intermediate"
    else:
        label = "unresolved"
    outcome, effect = OUTCOMES[label]
    return {"label": label, "outcome": outcome, "a5_186": effect, "decided": label in oc.DECIDING, "numbers": numbers}


def stray_templates(fitted: dict[str, Any]) -> list[str]:
    """The templates whose own twin drift departs from the shared drift by more than DRIFT_HETEROGENEITY_SE errors of
    the difference."""
    return [
        template
        for template in oc.TEMPLATES
        if fitted["template_drift"][template] is not None
        and abs(fitted["template_drift"][template] - fitted["drift"])
        > DRIFT_HETEROGENEITY_SE * fitted["template_drift_difference_se"][template] + DRIFT_DEPARTURE_FLOOR
    ]


def decide_executed(
    record: dict[str, Any],
    contrasts: dict[str, dict[str, list[Any]]],
    offsets: dict[str, int],
    seconds: dict[str, float],
    reference: tuple[list[float], ...],
    calibration: Callable[[], list[dict[str, Any]]],
) -> None:
    """The executed-order decision of the batch contrasts, written into `record` (which already holds the plain
    pool's `decision` and `order_ignored_label`): the twin fit, the base levels, the drift monitor, the calibration
    systematics and the decision of `decide_correlated` on the corrected rows, withheld under the first of
    WITHHELD_LABELS that applies. `seconds` holds the executed start of every circuit, `reference` the bracket offset
    series (times, values, errors) and `calibration` reads the X-only calibration batches once the monitor fits."""
    try:
        rows, fitted = executed_twin_fit(contrasts, offsets)
    except eo.ConfoundedOrder as error:
        record["executed_order_fit"] = {"status": "confounded", "reason": str(error)}
        unresolved(record, "unresolved_order_confounded", str(error))
        return
    stray = stray_templates(fitted)
    record["executed_order_fit"] = {"status": "fitted", **fitted, "stray_templates": stray}
    withheld: list[tuple[str, str]] = []
    try:
        base_rows, levels = base_level_rows(contrasts, seconds)
        for template in oc.TEMPLATES:
            rows[template]["base"] = base_rows[template]
        record["base_level_fit"] = {"status": "fitted", "templates": levels}
    except eo.ConfoundedOrder as error:
        record["base_level_fit"] = {"status": "confounded", "reason": str(error)}
        withheld.append(("unresolved_base_drift_confounded", str(error)))
    try:
        monitor = eo.drift_monitor(*reference)
    except eo.ConfoundedOrder as error:
        record["drift_monitor"] = {"status": "unusable", "reason": str(error)}
        withheld.append(("unresolved_drift_model", str(error)))
    else:
        record["drift_monitor"] = {"status": "fitted", **monitor}
        if not monitor["adequate"]:
            withheld.append(("unresolved_drift_model", "the bracket offsets are not a line in executed time"))
        bound = abs(float(monitor["slope"])) + SLOPE_BOUND_Z * float(monitor["slope_se"])
        tau = sum(twin_reference_times(seconds).values()) / len(oc.TEMPLATES)
        record["calibration_drift"] = [
            {
                **reading,
                "sigma_sys": bound * abs(reading["time"] - tau),
                "unresolved_calibration_drift": bound * abs(reading["time"] - tau) > reading["se"],
            }
            for reading in calibration()
        ]
    record["decision"] = decide_correlated(rows, fitted["covariance"])
    if stray:
        withheld.append(("unresolved_drift_heterogeneity", f"own drift departs from the shared drift: {stray}"))
    if withheld:
        common = record["decision"]["label"]
        unresolved(record, *withheld[0])
        record["decision"]["label_if_nothing_withheld"] = common
        record["decision"]["also_withheld"] = [label for label, _ in withheld[1:]]


def evaluate(
    shots: dict[str, list[str]], manifest: dict[str, Any], executed: dict[str, str] | None = None
) -> dict[str, Any]:
    """The rule-v2 decision of a complete Tuna-17 series on its executed order, with the per-batch bracket offsets
    beside it.

    Registered rule (owner ruling 2026-11-16, issue 791): the series is read on the order and the times the provider
    executed, recorded per job as `queued_at` and ranked by instant (`stamp_instant`).
    - Twin contrasts: each is corrected for one drift shared by the twin batches (their executed position offsets), and
      the templates pool with the covariance that the shared drift gives them (`decide_correlated`).
    - Base contrasts: each template's replicates are read at their executed times through a weighted line, and the
      level is taken at the mean executed time of the template's twin circuits.
    - Rule v2 pools the corrected rows. A reference series (the bracket offset of every base and twin batch) must
      keep its residual under the alpha 0.001 chi-square of the line.
    - Calibration batches carry the systematic g_up |t - tau| of that line's slope bound, reported beside the decision.
    Labels, in the order they are withheld (WITHHELD_LABELS): `unresolved_order` (a stamp is missing, null or not an ISO
    8601 instant with an offset, or two circuits of a twin batch start at one instant), `unresolved_order_confounded`
    (every template keeps one position offset), `unresolved_base_drift_confounded` (a template's base replicates share
    one start time), `unresolved_drift_model` (the reference series is not a line), `unresolved_drift_heterogeneity`
    (a template's own drift departs from the shared one). The label of the pool that ignores the order stays beside
    every withheld reading as `label_if_order_ignored`, and the strict reading of `order_gate` stays as a record that
    decides nothing."""
    try:
        instants: dict[str, int] | None = series_instants(executed)
        reason = ""
    except UnusableOrder as error:
        instants, reason = None, str(error)
    # The plain pool reads a canonical, fixed-width rendering of the instants, or no stamps when one is unusable.
    plain_stamps = (
        None
        if instants is None
        else {
            key: (EPOCH + timedelta(microseconds=us)).strftime("%Y-%m-%dT%H:%M:%S.%fZ") for key, us in instants.items()
        }
    )
    record: dict[str, Any] = evaluate_decision(shots, manifest, plain_stamps)
    record["twin_brackets"] = batch_brackets(shots, manifest)
    record["order_gate"] = order_gate(executed)
    record["order_ignored_label"] = record["decision"]["label"]
    try:
        if instants is None:
            raise UnusableOrder(reason)
        offsets = twin_offsets(executed)
    except UnusableOrder as error:
        record["executed_order_fit"] = {"status": "unusable", "reason": str(error)}
        unresolved(record, "unresolved_order", str(error))
        return record
    contrasts = {t: {k: [tuple(x) for x in v] for k, v in c.items()} for t, c in record["batch_contrasts"].items()}
    seconds = circuit_seconds(executed or {})
    decide_executed(
        record,
        contrasts,
        offsets,
        seconds,
        bracket_series(shots, manifest, seconds),
        lambda: calibration_readings(shots, manifest, seconds),
    )
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


# Operating characteristics of the executed-order rule -----------------------------------------------------------------

# The model of the executed-order tables (hypotheses: each is a stated assumption of the simulation, not a measurement
# of Tuna-17 except where marked). A batch runs its circuits in a uniformly random permutation with probability
# REORDER_RATE and in its requested order otherwise, so a twin batch reverses its twins with probability REORDER_RATE
# / 2 (measured: 3 of 12 twin batches of the predecessor series and the hosted QX run reversed theirs, 2 of 8 and 1 of
# 4, which is 0.25; the strict gate counted 7 of the predecessor's 19 batches out of order, 0.37, so 0.5 is the
# cautious side of both). Circuits start JOB_SECONDS apart (the design's execution seconds per job) and a wave waits
# POLICY.pause_seconds + 1 s before the next. The shared twin drift is LINEAR_TWIN_DRIFT per executed position, the
# base level and the bracket offset drift linearly in time at LINEAR_BASE_SLOPE per second (the largest plausible 0.01
# per hour of docs/design/bracketed-base-contrast-weights.md), and a planted departure adds to the k4 twin drift per
# position.
REORDER_RATE = 0.5
LINEAR_TWIN_DRIFT = 0.003
LINEAR_BASE_SLOPE = 0.01 / 3600.0
PLANTED_DEPARTURES = (0.0075, 0.015)
PLANTED_TEMPLATE = "k4"
# World subset of the heterogeneity-gate tables: the gate reads the twin drifts, which a world's contrasts do not move.
GATE_WORLDS = ("absent", "coin_dropout", "superposition_only")
EXECUTED_TABLES: dict[str, dict[str, float]] = {
    "executed_in_order": {"rate": 0.0, "twin_drift": 0.0, "base_slope": 0.0, "departure": 0.0},
    "executed_reordered_stationary": {"rate": REORDER_RATE, "twin_drift": 0.0, "base_slope": 0.0, "departure": 0.0},
    "executed_reordered_linear_drift": {
        "rate": REORDER_RATE,
        "twin_drift": LINEAR_TWIN_DRIFT,
        "base_slope": LINEAR_BASE_SLOPE,
        "departure": 0.0,
    },
    **{
        f"executed_planted_departure_{departure}": {
            "rate": REORDER_RATE,
            "twin_drift": LINEAR_TWIN_DRIFT,
            "base_slope": LINEAR_BASE_SLOPE,
            "departure": departure,
        }
        for departure in PLANTED_DEPARTURES
    },
}
OC_SEED_INDICES.update({name: 923 + n for n, name in enumerate(EXECUTED_TABLES)})
# The design's 1,667 to 1,821 s of execution over 120 jobs is 13.9 to 15.2 s per job.
JOB_SECONDS = 14.0
WAVE_GAP_SECONDS = float(POLICY.pause_seconds or 0) + 1.0


@cache
def _simulation_layout() -> dict[str, Any]:
    """The series layout the simulation reads: per batch its circuits, its first start under the requested order, and
    the base and twin batch ids of each template."""
    rows = batch_rows(TUNA_SERIES)
    starts: list[float] = []
    clock = 0.0
    for n, row in enumerate(rows):
        if n and n % POLICY.queued_batches == 0:
            clock += WAVE_GAP_SECONDS
        starts.append(clock)
        clock += JOB_SECONDS * len(row["circuits"])
    twin_ids = twin_layout()
    return {
        "rows": rows,
        "starts": starts,
        "twin": {
            template: [b for b, (t, _, _) in sorted(twin_ids.items()) if t == template] for template in oc.TEMPLATES
        },
        "base": base_batch_ids(),
    }


def _executed_series(
    seed: np.random.SeedSequence, *, mean: dict[str, float], params: dict[str, float]
) -> tuple[str, bool]:
    """(decision label, whether the drift-heterogeneity gate fired) of one simulated series read on its executed order.

    The series is drawn from `seed`: the permutation of each batch, the binomial selector zero counts of every twin
    circuit, the Gaussian base noise and the bracket offsets, with the drifts of `params` added to the twin contrasts
    (per executed position), the base levels and the bracket offsets (per second about the template's twin reference
    time and the series' first start); the decision is `decide_executed` on those contrasts."""
    rng = np.random.default_rng(seed)
    layout = _simulation_layout()
    e01, e10 = retained_selector_rates()
    seconds: dict[str, float] = {}
    offsets: dict[str, int] = {}
    for row, start in zip(layout["rows"], layout["starts"], strict=True):
        circuits = [c["file"] for c in row["circuits"]]
        place = rng.permutation(len(circuits)) if rng.random() < params["rate"] else np.arange(len(circuits))
        for name, position in zip(circuits, place, strict=True):
            seconds[f"{row['batch']}/{name}"] = start + JOB_SECONDS * float(position)
        if row["kind"] == "twin":
            offsets[row["batch"]] = int(place[circuits.index(oc.twin_file(row["template"], 1))]) - int(
                place[circuits.index(oc.twin_file(row["template"], 0))]
            )
    reference_time = twin_reference_times(seconds)
    contrasts: dict[str, dict[str, list[tuple[float, float]]]] = {}
    for template in oc.TEMPLATES:
        key = "b0" if template == "b0" else "k"
        shots = BATCH_SHOTS
        p_read = 0.5 + (e10 - e01) / 2 + np.array([-0.5, 0.5]) * mean[f"t_{key}"]
        drift = params["twin_drift"] + (params["departure"] if template == PLANTED_TEMPLATE else 0.0)
        twin = []
        for batch in layout["twin"][template]:
            zeros = rng.binomial(shots, p_read)
            value, se = twin_contrast(int(zeros[1]), shots, int(zeros[0]), shots)
            twin.append((value + drift * offsets[batch], se))
        se_base = 1.0 / math.sqrt(CONTROL_SHOTS if template == "b0" else BATCH_SHOTS)
        base = [
            (
                mean[f"s_{key}"]
                + se_base * float(rng.normal())
                + params["base_slope"] * (seconds[f"{batch}/{template}.cq"] - reference_time[template]),
                se_base,
            )
            for batch in layout["base"][template]
        ]
        contrasts[template] = {"base": base, "twin": twin}
    offset_se = math.sqrt((ana.arm_variance(e10, BATCH_SHOTS) + ana.arm_variance(e01, BATCH_SHOTS)) / 4)
    times, values = [], []
    for row in layout["rows"]:
        if row["kind"] in ("base", "twin"):
            mid = (seconds[f"{row['batch']}/readout-0.cq"] + seconds[f"{row['batch']}/readout-1.cq"]) / 2
            times.append(mid)
            values.append((e10 - e01) / 2 + params["base_slope"] * mid + offset_se * float(rng.normal()))
    record: dict[str, Any] = {"decision": {}, "order_ignored_label": ""}
    decide_executed(record, contrasts, offsets, seconds, (times, values, [offset_se] * len(times)), list)
    fit = record["executed_order_fit"]
    return str(record["decision"]["label"]), bool(fit.get("stray_templates"))


def executed_operating_characteristics(
    seed_index: int,
    params: dict[str, float],
    draws: int = OC_DRAWS,
    worlds: dict[str, dict[str, float]] | None = None,
) -> dict[str, dict[str, Any]]:
    """Share of each decision label per world and of series whose drift-heterogeneity gate fired, from `draws`
    simulated series of the executed-order rule per world (`_executed_series`), seeded from QRNG value `seed_index` of
    OC_DRAW. Each series owns a child of one SeedSequence, in world order and series order, so the table does not depend
    on the worker count."""
    worlds = rule.WORLDS if worlds is None else worlds
    children = np.random.SeedSequence(int(read_record(OC_DRAW)["values"][seed_index])).spawn(draws * len(worlds))
    labels: dict[str, dict[str, float]] = {}
    fired: dict[str, float] = {}
    for k, (world, mean) in enumerate(worlds.items()):
        results = parallel.ordered_map(
            partial(_executed_series, mean=mean, params=params), children[k * draws : (k + 1) * draws]
        )
        counts: dict[str, int] = {}
        for label, _ in results:
            counts[label] = counts.get(label, 0) + 1
        labels[world] = {label: round(n / draws, 4) for label, n in sorted(counts.items())}
        fired[world] = round(sum(1 for _, gate in results if gate) / draws, 4)
    return {"labels": labels, "heterogeneity_gate_fired": fired}


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
        "outcomes": {label: {"outcome": v[0], "a5_186": v[1]} for label, v in OUTCOMES.items()},
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
        executed = {}
        for name, params in EXECUTED_TABLES.items():
            gate_only = name.startswith("executed_planted")
            table = executed_operating_characteristics(
                OC_SEED_INDICES[name], params, worlds={w: rule.WORLDS[w] for w in GATE_WORLDS} if gate_only else None
            )
            executed[name] = {
                "labels": {
                    w: {label: rule.ten_thousandths(share) for label, share in row.items()}
                    for w, row in table["labels"].items()
                },
                "heterogeneity_gate_fired": {
                    w: rule.ten_thousandths(share) for w, share in table["heterogeneity_gate_fired"].items()
                },
            }
        record["operating_characteristics"] = {
            "qrng_draw": OC_DRAW,
            "seed_indices": dict(OC_SEED_INDICES),
            "draws_per_world": OC_DRAWS,
            "executed_order_model": {
                "unit": "rates and drifts in ten-thousandths: 5000 is 0.5; a drift per executed position or per hour",
                "reorder_rate_per_batch": rule.ten_thousandths(REORDER_RATE),
                "twin_drift_per_position": rule.ten_thousandths(LINEAR_TWIN_DRIFT),
                "base_drift_per_hour": rule.ten_thousandths(LINEAR_BASE_SLOPE * 3600.0),
                "planted_departures_per_position": [rule.ten_thousandths(d) for d in PLANTED_DEPARTURES],
                "planted_template": PLANTED_TEMPLATE,
                "gate_worlds": list(GATE_WORLDS),
                "job_seconds": round(JOB_SECONDS),
                "wave_gap_seconds": round(WAVE_GAP_SECONDS),
            },
            **{
                key: {
                    w: {label: rule.ten_thousandths(share) for label, share in row.items()} for w, row in table.items()
                }
                for key, table in tables.items()
            },
            **executed,
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
