"""Ascella postselected CZ compilation ensemble: two qpu:ascella jobs of 60 template iterations with anchors.

docs/design/ascella-cz-compilation-ensemble-case.md fixes the request and the preregistered analysis. The gate, the
window, the photon inputs and the eligibility rule are those of scripts/ascella_cz_tomography_case.py (imported as
tomo): the Ralph CZ of Perceval's "postprocessed cz" on chip modes 0..5, photons in chip modes 0 and 2, an eligible
event carrying exactly two threshold clicks, one on each rail pair. The observable is two complementary truth tables
(Hofmann, PRL 94, 160504 (2005)): ZX reads the control in Z and the target in X for the inputs |0,+>, |0,->, |1,+>,
|1,->, and XZ exchanges the roles. Each of the eight settings folds its preparations and readout rotations into one
6 x 6 unitary around the CZ block, as in the tomography.

Each job holds 40 ensemble iterations (every setting under five compilation seeds; job-01 takes five further seeds, so
each setting meets ten compiled meshes) and 20 anchor iterations (four settings under one fixed seed each, repeated at
iterations 0-3, 14-17, 28-31, 42-45 and 56-59 of both jobs). The service returns the same computed_circuit for the same
parameters under the same seed (docs/notes/quandela/strategy.md section 7), so the ten repeats of an anchor request
one mesh. Every compilation seed, the order of every ensemble segment, the Monte Carlo stream of the analysis and the
false-alarm simulation come from one ANU QRNG draw that the manifests own whole.

--check rebuilds both jobs and the forecast inputs and compares them with the retained files, binds every iteration
through qd_platform.template_experiment, and holds the schedule to the design. --forecast recomputes forecast.json.
--read and --estimate retain the live platform read and Perceval's shot estimate (read-only platform calls; nothing is
sent). --analyze OUT.json RUN RUN reduces the two collected runs to the preregistered estimates. Submission uses the
generic runner, scripts/qd_platform.py plan/submit/collect, under the written case's approval.

Usage:
  "$PYTHON" scripts/ascella_cz_ensemble_case.py [--check | --build | --forecast | --read | --estimate]
  "$PYTHON" scripts/ascella_cz_ensemble_case.py --analyze OUT.json RUN [RUN]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from fractions import Fraction
from functools import cache
from pathlib import Path
from typing import Any

import numpy as np
from flint import arb, arb_mat, arf, ctx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import ascella_cz_tomography_case as tomo  # noqa: E402
import billing_rule_v2  # noqa: E402
import qd_platform  # noqa: E402
from hypercomplex_cases import encoded, photonic_template  # noqa: E402

import qd_records  # noqa: E402
from parallel import ordered_map, workers  # noqa: E402

PLATFORM = "qpu:ascella"
FAMILY = "ascella_cz_ensemble"
FAMILY_DIR = ROOT / "results/quandela/cases" / FAMILY
DESIGN = "docs/design/ascella-cz-compilation-ensemble-case.md"
READ = "platform-read/ascella-perfs.json"
FORECAST = "forecast.json"
ESTIMATE = "shot-estimate.json"
JOBS = ("job-00", "job-01")
ITERATIONS = 60
MAX_DURATION = 300
SAMPLES_PER_ITERATION = 4000
# max_shots per iteration of each job: Perceval's largest estimate over the job's settings (shot-estimate.json) times
# SHOT_MARGIN, rounded up to SHOT_QUANTUM. qd_platform.job_billing bills an iterated job 1 credit plus 1e-6 per shot of
# the smaller of its shots used and that cap, so the cap fixes each job's credit ceiling.
JOB_SHOTS = {"job-00": 400000, "job-01": 400000}
SHOT_MARGIN = 1.25
SHOT_QUANTUM = 100000
PER_JOB_CREDITS = 1.0
PRICE_PER_SHOT = 1e-6
CASE_CREDIT_CEILING = 6.0
# Seconds one template iteration takes on qpu:ascella (tomo.ITERATION_SECONDS); both 72-iteration tomography jobs took
# 221 s, 3.07 s per iteration, which gives 184 s for 60.
EXPECTED_SECONDS = 220
TOLERANCE = tomo.TOLERANCE
# The ANU QRNG draw whose values seed every compilation, order every segment and seed the analysis and the forecast's
# false-alarm study. The manifests name it without an index, so the case owns it whole (ci/seed_provenance.py).
DRAW = "docs/evidence/anu_qrng/draw-2026-11-07T164259Z.json"
SEED_RULE = (
    "nonzero draw values in index order, repeats skipped: 4 anchor seeds in anchor order, then 10 seeds per ensemble "
    "setting in setting order (seed index s = 1..10, s <= 5 in job-00), then the analysis Monte Carlo seed, then the "
    "false-alarm study seed; the order keys are the raw values of the next 176 indices; the three indices after them "
    "seed the bootstrap of the tomography prediction, the random-map check of the bound and the test fixtures"
)
TABLES = {
    "ZX": (("0", "+"), ("0", "-"), ("1", "+"), ("1", "-")),
    "XZ": (("+", "0"), ("-", "0"), ("+", "1"), ("-", "1")),
}
INPUT_STATES = {**tomo.INPUT_STATES, "-": (math.pi / 2, math.pi)}
ANCHORS = ("in-0+-ZX", "in-1--ZX", "in-+0-XZ", "in--1-XZ")
ANCHOR_STARTS = (0, 14, 28, 42, 56)
SEEDS_PER_JOB = 5
SEGMENTS = len(ANCHOR_STARTS) - 1
SEGMENT_SIZE = 10
# Per job: 8 keys choose the two settings whose fifth replicate joins each segment, 40 place each setting's five
# replicates on its five segment slots, 40 order the ten iterations of each segment.
ORDER_KEYS_PER_JOB = 88
MIN_ELIGIBLE = 200
ALPHA = 0.01
DRIFT_TESTS = 16
MESH_TESTS = 8
MC_TABLES = 100000
SCORE_LEVEL = 0.95
BOUND_LOWER_LEVEL = 0.975
BOUND_UPPER_LEVEL = 0.9875
# 1000 null datasets put the 95 % Clopper-Pearson upper limit of a family rate near 0.01 below 0.02.
FALSE_ALARM_DATASETS = 1000
FALSE_ALARM_VARIANT = "source, loss and dark counts"
# The retained tomography: its two runs and the analysis whose unprojected fit predicts the ensemble's tables.
TOMOGRAPHY_RUNS = (
    "results/quandela/runs/2026-10-31T050944Z-qpu_ascella-ascella_cz_tomography-job-00",
    "results/quandela/runs/2026-10-31T050944Z-qpu_ascella-ascella_cz_tomography-job-01",
)
TOMOGRAPHY_ANALYSIS = "results/quandela/ascella-cz-tomography-analysis.json"
HOM_READING_POINTS = 1.0
TOMOGRAPHY_HOM_LABEL = "HOM at which the tomography's job-00 was submitted (its submission.json perfs_at_plan)"
PREDICTION_REPLICATES = tomo.BOOTSTRAP_REPLICATES
# arb working precisions tried in order until every float64 of the prediction certifies
CERTIFIED_PRECISIONS = (128, 256, 512)
# each worker batch re-solves the normal equations, so a batch takes at least this many columns
MIN_BATCH_COLUMNS = 32
BOUND_CHECK_MAPS = 20000


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


# ---------------------------------------------------------------- settings


def base_settings() -> list[dict[str, Any]]:
    """The eight ensemble settings in table order: ZX then XZ, each in its input order."""
    rows = []
    for table, inputs in TABLES.items():
        for control, target in inputs:
            rows.append({"name": f"in-{control}{target}-{table}", "input": control + target, "basis": table})
    return rows


def setting_unitary(row: Mapping[str, Any]) -> np.ndarray:
    """Readout rotations after the CZ after the input preparations, as tomo.setting_unitary with |-> admitted."""
    prepare = tomo.pair_block(*(tomo.preparation(*INPUT_STATES[label]) for label in row["input"]))
    read = tomo.pair_block(tomo.readout(row["basis"][0]), tomo.readout(row["basis"][1]))
    return np.asarray(read @ tomo.cz_unitary() @ prepare, dtype=complex)


def input_density(label: str) -> np.ndarray:
    first, second = (tomo.preparation(*INPUT_STATES[part])[:, 0] for part in label)
    vector = np.kron(first, second).astype(complex)
    return np.asarray(np.outer(vector, vector.conj()), dtype=complex)


def ideal_outcomes(row: Mapping[str, Any]) -> list[float]:
    """Conditional probability of each readout outcome (2 * control rail + target rail) under the ideal CZ."""
    first, second = (tomo.preparation(*INPUT_STATES[label])[:, 0] for label in row["input"])
    state = tomo.ideal_cz() @ np.kron(first, second)
    return [float(np.real(state.conj() @ tomo.outcome_projector(row["basis"], o) @ state)) for o in range(4)]


def correct_outcome(row: Mapping[str, Any]) -> int:
    """The one outcome the ideal CZ returns with probability 1; a truth-table input admits exactly one."""
    probabilities = ideal_outcomes(row)
    certain = [o for o, p in enumerate(probabilities) if abs(p - 1.0) <= TOLERANCE]
    require(len(certain) == 1, f"{row['name']}: ideal outcomes {probabilities} name no single correct outcome")
    require(all(abs(p) <= TOLERANCE for o, p in enumerate(probabilities) if o != certain[0]), f"{row['name']}")
    return certain[0]


def exact_outcomes(row: Mapping[str, Any]) -> tuple[list[float], float]:
    """(conditional probabilities, accepted probability per attempt) by permanents, indistinguishable and lossless."""
    amplitudes = tomo.coincidence_block(setting_unitary(row))[:, 0]
    probabilities = np.abs(amplitudes) ** 2
    total = float(probabilities.sum())
    return [float(p / total) for p in probabilities], total


# ---------------------------------------------------------------- seeds and order


@cache
def draw_values() -> tuple[int, ...]:
    record = json.loads((ROOT / DRAW).read_text(encoding="utf-8"))
    values = record["values"]
    require(isinstance(values, list) and all(type(v) is int for v in values), f"{DRAW} holds no integer values")
    return tuple(values)


@cache
def seed_plan() -> dict[str, Any]:
    """Draw index and value of every seed and order key, by the rule SEED_RULE states."""
    taken: set[int] = set()
    usable: list[tuple[int, int]] = []
    for index, value in enumerate(draw_values()):
        if value == 0 or value in taken:
            continue
        taken.add(value)
        usable.append((index, value))
    bases = base_settings()
    needed = len(ANCHORS) + len(bases) * 2 * SEEDS_PER_JOB + 2
    require(len(usable) >= needed, f"{DRAW} holds {len(usable)} usable values, not {needed}")
    anchors = dict(zip(ANCHORS, usable[: len(ANCHORS)], strict=True))
    start = len(ANCHORS)
    ensemble = {
        row["name"]: usable[start + k * 2 * SEEDS_PER_JOB : start + (k + 1) * 2 * SEEDS_PER_JOB]
        for k, row in enumerate(bases)
    }
    after = start + len(bases) * 2 * SEEDS_PER_JOB
    analysis, false_alarm = usable[after], usable[after + 1]
    first_key = false_alarm[0] + 1
    count = ORDER_KEYS_PER_JOB * len(JOBS)
    values = draw_values()
    require(first_key + count <= len(values), f"{DRAW} ends before the {count} order keys")
    keys = {
        job: [
            (first_key + j * ORDER_KEYS_PER_JOB + i, values[first_key + j * ORDER_KEYS_PER_JOB + i])
            for i in range(ORDER_KEYS_PER_JOB)
        ]
        for j, job in enumerate(JOBS)
    }
    tail = first_key + count
    used = {value for _, value in usable[: after + 2]}
    extra = []
    for index in range(tail, tail + 3):
        require(index < len(values) and values[index] != 0, f"{DRAW} has no nonzero value at index {index}")
        require(values[index] not in used, f"{DRAW} index {index} repeats a seed already taken")
        used.add(values[index])
        extra.append((index, values[index]))
    return {
        "anchors": anchors,
        "ensemble": ensemble,
        "analysis": analysis,
        "false_alarm": false_alarm,
        "keys": keys,
        "prediction": extra[0],
        "bound_check": extra[1],
        "fixture": extra[2],
    }


def ranked(items: Sequence[Any], keys: Sequence[tuple[int, int]]) -> list[Any]:
    """`items` sorted by their order keys (value, then draw index)."""
    order = sorted(range(len(items)), key=lambda i: (keys[i][1], keys[i][0]))
    return [items[i] for i in order]


@cache
def job_schedule(job: str) -> tuple[dict[str, Any], ...]:
    """The 60 iterations of a job in request order: anchors at ANCHOR_STARTS, ensemble segments between them.

    Every setting appears once in every segment, and one replicate of each setting joins a second segment, two per
    segment, so every setting appears in every pair of adjacent segments."""
    plan = seed_plan()
    keys = plan["keys"][job]
    bases = base_settings()
    offset = JOBS.index(job) * SEEDS_PER_JOB
    extras = ranked(list(range(len(bases))), keys[: len(bases)])
    extra_segment = {setting: rank // 2 for rank, setting in enumerate(extras)}
    segments: list[list[tuple[int, int]]] = [[] for _ in range(SEGMENTS)]
    for k in range(len(bases)):
        replicates = ranked(list(range(SEEDS_PER_JOB)), keys[len(bases) + SEEDS_PER_JOB * k :][:SEEDS_PER_JOB])
        slots = [*range(SEGMENTS), extra_segment[k]]
        for replicate, segment in zip(replicates, slots, strict=True):
            segments[segment].append((k, replicate))
    base = len(bases) + SEEDS_PER_JOB * len(bases)
    rows: list[dict[str, Any]] = []
    for position in range(ITERATIONS):
        if any(start <= position < start + len(ANCHORS) for start in ANCHOR_STARTS):
            start = max(s for s in ANCHOR_STARTS if s <= position)
            name = ANCHORS[position - start]
            index, seed = plan["anchors"][name]
            row = next(r for r in bases if r["name"] == name)
            rows.append(
                {
                    **row,
                    "name": f"{name}-a{ANCHOR_STARTS.index(start)}",
                    "setting": name,
                    "role": "anchor",
                    "anchor_position": ANCHOR_STARTS.index(start),
                    "compilation_seed": seed,
                    "draw_index": index,
                }
            )
            continue
        segment = max(i for i, s in enumerate(ANCHOR_STARTS) if s <= position)
        members = sorted(segments[segment])
        order = ranked(members, keys[base + SEGMENT_SIZE * segment :][:SEGMENT_SIZE])
        k, replicate = order[position - ANCHOR_STARTS[segment] - len(ANCHORS)]
        seed_index = offset + replicate
        index, seed = plan["ensemble"][bases[k]["name"]][seed_index]
        rows.append(
            {
                **bases[k],
                "name": f"{bases[k]['name']}-s{seed_index + 1}",
                "setting": bases[k]["name"],
                "role": "ensemble",
                "seed_index": seed_index + 1,
                "segment": segment,
                "compilation_seed": seed,
                "draw_index": index,
            }
        )
    return tuple(rows)


def order_key_indices(job: str) -> list[int]:
    return [index for index, _ in seed_plan()["keys"][job]]


# ---------------------------------------------------------------- the retained request


def read_perfs() -> dict[str, Any]:
    perfs: dict[str, Any] = json.loads((FAMILY_DIR / READ).read_text(encoding="utf-8"))["perfs"]
    return perfs


def build_setting(item: tuple[int, dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    """The template mesh and the manifest setting of one iteration."""
    position, row = item
    unitary = setting_unitary(row)
    mesh, parameters = photonic_template(unitary)
    full = tomo.embed(unitary)
    conditional, accepted = exact_outcomes(row)
    setting = {
        **row,
        "table": row["basis"],
        "correct_outcome": correct_outcome(row),
        "observation_index": position,
        "ideal": {
            "outcome_probabilities": [round(p, 12) for p in conditional],
            "accepted_probability": round(accepted, 12),
        },
        "circuit_params": parameters,
        "column": [[float(value.real), float(value.imag)] for value in full[:, tomo.SOURCES[0]]],
        "operator": encoded(full),
    }
    return mesh, setting


def request_parts(job: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    built = ordered_map(build_setting, list(enumerate(job_schedule(job))), min_items=1)
    template = built[0][0]
    for position, (mesh, _) in enumerate(built):
        require(mesh == template, f"{job}: iteration {position} needs another mesh than iteration 0")
    circuit = {**template, "modes": tomo.MODES, "input_state": tomo.source_state()}
    return [setting for _, setting in built], circuit


def preregistered() -> dict[str, Any]:
    plan = seed_plan()
    return {
        "observable": "two complementary truth tables (Hofmann, PRL 94, 160504 (2005)): ZX reads control Z and target "
        "X for |0,+>, |0,->, |1,+>, |1,->; XZ reads control X and target Z for |+,0>, |-,0>, |+,1>, |-,1>; each "
        "setting's correct outcome is the one its ideal CZ output returns with probability 1",
        "rates": "eligible rate = eligible events over the iteration's nb_shots_used; correct rate = the events on "
        "the correct outcome over the same shots",
        "primary": "rate-weighted score F_T(s) = sum over the four inputs of table T of the correct rates at seed "
        "index s over the sum of their eligible rates",
        "descriptive": "per-input score F'_T(s) = mean over the four inputs of correct over eligible events",
        "binding": "each run's cases.json equals the retained case byte for byte and the two runs are distinct jobs; "
        "an ensemble iteration binds one to one to the setting whose compilation_seed it echoes, an anchor iteration "
        "to its anchor's seed group, which must hold exactly five per job; every iteration echoes its setting's "
        "circuit_params. The five members of an anchor group are labeled in returned order, which proves no "
        "physical chronology; no statistic below depends on that label, since a homogeneity table is invariant "
        "under permuting its rows",
        "preconditions": "both runs complete, and every one of the 120 iterations returns counts and carries at "
        f"least {MIN_ELIGIBLE} eligible events; otherwise the case is undecided",
        "homogeneity_test": "Pearson chi-square of an R x 4 table of eligible outcome counts against the pooled "
        f"row proportions (columns with no events dropped); Monte Carlo p = (1 + b) / (1 + {MC_TABLES}), b the "
        f"number of {MC_TABLES} tables drawn uniformly over the arrangements with the observed row and column totals "
        "(sequential hypergeometric draws, the exact conditional null) whose statistic reaches the observed one",
        "rate_test": "conditional binomial comparison of an anchor's per-shot eligible rate between the jobs: given "
        "k0 + k1, k0 ~ Binomial(k0 + k1, n0 / (n0 + n1)) with n the summed nb_shots_used, two-sided; this is the "
        "Poisson-rate form, and under the stopping rule (fixed samples, random shots) its variance ratio is "
        "1 - p_eligible / p_any_click, about 0.996 at the forecast, so it is slightly conservative",
        "estimate_1_drift": f"per anchor: positions in job-00, positions in job-01, job-00 against job-01 "
        f"(homogeneity) and the rate test; the jobs pool only when all {DRIFT_TESTS} p-values exceed "
        f"{ALPHA} / {DRIFT_TESTS} and every anchor iteration returns a computed_circuit, one digest per anchor across "
        "both jobs; a missing or empty computed_circuit unpools the jobs",
        "estimate_2_mesh_variance": f"per ensemble setting, homogeneity of its ten seed tables at {ALPHA} / "
        f"{MESH_TESTS} when the jobs pool, else of each job's five seed tables at {ALPHA} / {2 * MESH_TESTS}, so a "
        "shift between jobs never reads as mesh variance; the between-seed variance of its correct fraction minus the "
        "mean binomial variance is reported as the excess, and seeds that return one computed_circuit are reported as "
        "one mesh",
        "estimate_3_scores": f"mean over s of F_T(s) with a two-sided {SCORE_LEVEL} Student-t interval on 9 degrees "
        "of freedom when the jobs pool, else per job on 4; the same for F'_T. The seed index s pairs the four "
        "settings of a table arbitrarily, each setting's replicates being placed by independent order keys; time "
        "drift between s adds variance the interval carries. The interval's coverage under a non-normal mesh "
        "distribution is not established",
        "estimate_4_bound": f"L = one-sided {BOUND_LOWER_LEVEL} lower limit of the mean of F_ZX(s) + F_XZ(s) - 1, "
        f"U = the smaller one-sided {BOUND_UPPER_LEVEL} upper limit of F_ZX and F_XZ; reported only when the jobs "
        "pool, as a statement conditional on one process for every setting and one chance of a shot per attempt",
        "estimate_5_tomography": "each ensemble score minus the score that the retained unprojected tomography fit "
        "predicts for the same settings (forecast.json tomography_prediction); the interval combines estimate 3's "
        "standard error with the standard deviation of the prediction over a parametric bootstrap of the tomography "
        f"runs ({PREDICTION_REPLICATES} replicates, tomo.resampled_rates), at the Student-t quantile of estimate 3; "
        "the predicted rates are linear images of an unprojected fit and can be negative",
        "hom": f"each plan's HOM minus the {TOMOGRAPHY_HOM_LABEL}; hom_moved is true beyond {HOM_READING_POINTS} point",
        "monte_carlo_seed": {"draw": DRAW, "index": plan["analysis"][0]},
        "readings": READINGS,
    }


READINGS = {
    "both_differences_contain_zero": "the single-compilation tomography fit predicts the ensemble's truth tables",
    "difference_above_zero": "the ensemble reads that table better than the tomography fit predicts",
    "difference_below_zero": "the tomography fit overstated that table, by mesh selection or by its estimator",
    "mesh_variance_rejects": "the tomography interval, which covers shot noise only, is too narrow for the mesh "
    "ensemble",
    "drift_or_recalibration": "the jobs are reported separately and no pooled bound is claimed",
    "hom_moved": f"the plan's HOM differs from the tomography's by more than {HOM_READING_POINTS} point: estimate 5 "
    "states the HOM difference beside each comparison",
}


def documents(job: str) -> dict[str, bytes]:
    settings, circuit = request_parts(job)
    circuit_bytes = (json.dumps(circuit, indent=1) + "\n").encode()
    count = len(settings)
    manifest = {
        "schema": "qd-hypercomplex-cases-v1",
        "family": FAMILY,
        "job": job,
        "platforms": [PLATFORM],
        "command": "sample_count",
        "gate_form": "template",
        "iterations": count,
        "min_detected_photons": tomo.MIN_CLICKS,
        "max_samples": SAMPLES_PER_ITERATION * count,
        "max_shots": JOB_SHOTS[job] * count,
        "max_duration": MAX_DURATION,
        "max_credits": round(PER_JOB_CREDITS + PRICE_PER_SHOT * JOB_SHOTS[job], 6),
        "mitigations": [],
        "output_modes": tomo.MODES,
        "logical_modes": list(range(tomo.WINDOW)),
        "layout": {"logical": ["c0", "c1", "t0", "t1", "h0", "h1"], "chip_modes": list(range(tomo.WINDOW))},
        "eligibility": "exactly two threshold clicks across all twelve returned modes, one on a control rail "
        "(modes 0, 1) and one on a target rail (modes 2, 3)",
        "outcomes": {"order": ["00", "01", "10", "11"], "meaning": "control rail then target rail of the click"},
        "design": DESIGN,
        "settings": settings,
        "circuit": {"file": "circuit.json", "sha256": qd_platform.sha256_bytes(circuit_bytes)},
        "compilation_seeds": {
            "draw": DRAW,
            "indices": [setting["draw_index"] for setting in settings],
            "order_key_indices": order_key_indices(job),
            "rule": SEED_RULE,
        },
        "billing": billing_rule_v2.RULE,
        "preregistered": preregistered(),
    }
    return {"cases.json": (json.dumps(manifest, indent=1) + "\n").encode(), "circuit.json": circuit_bytes}


# ---------------------------------------------------------------- scores and tests


def table_scores(correct: np.ndarray, eligible: np.ndarray, shots: np.ndarray) -> tuple[float, float]:
    """(rate-weighted F, per-input F') of one table from its four inputs' correct and eligible events and shots."""
    rate_correct = correct / shots
    rate_eligible = eligible / shots
    return float(rate_correct.sum() / rate_eligible.sum()), float(np.mean(correct / eligible))


def map_scores(kraus: np.ndarray | Sequence[np.ndarray]) -> dict[str, float]:
    """Exact rate-weighted and per-input scores of each table, and the trace-normalized process fidelity, of the
    trace-non-increasing map rho -> sum_k K_k rho K_k^dagger, the design's check of the Hofmann bound."""
    operators = [kraus] if isinstance(kraus, np.ndarray) else list(kraus)

    def apply(rho: np.ndarray) -> np.ndarray:
        return np.asarray(sum(k @ rho @ k.conj().T for k in operators))

    out: dict[str, float] = {}
    for table, inputs in TABLES.items():
        correct, eligible = [], []
        for control, target in inputs:
            row = {"input": control + target, "basis": table}
            output = apply(input_density(row["input"]))
            probabilities = [float(np.real(np.trace(tomo.outcome_projector(table, o) @ output))) for o in range(4)]
            correct.append(probabilities[correct_outcome({**row, "name": table})])
            eligible.append(sum(probabilities))
        ones = np.ones(4)
        out[f"F_{table}"], out[f"F_prime_{table}"] = table_scores(np.asarray(correct), np.asarray(eligible), ones)
    choi_vector = tomo.ideal_choi_vector()
    choi = np.zeros((16, 16), dtype=complex)
    for i in range(4):
        for j in range(4):
            unit = np.zeros((4, 4), dtype=complex)
            unit[i, j] = 1.0
            choi += np.kron(unit, apply(unit))
    out["process_fidelity"] = float(np.real(choi_vector.conj() @ choi @ choi_vector) / (4 * np.real(np.trace(choi))))
    return out


def pearson(table: np.ndarray) -> np.ndarray:
    """Pearson statistic of each (..., R, K) table against its own pooled row proportions."""
    totals = table.sum(axis=-1, keepdims=True)
    pooled = table.sum(axis=-2, keepdims=True) / table.sum(axis=(-2, -1), keepdims=True)
    expected = totals * pooled
    with np.errstate(divide="ignore", invalid="ignore"):
        terms = np.where(expected > 0, (table - expected) ** 2 / expected, 0.0)
    return np.asarray(terms.sum(axis=(-2, -1)))


def conditional_tables(table: np.ndarray, generator: np.random.Generator, size: int) -> np.ndarray:
    """`size` random tables with the row and column totals of `table`, uniform over the arrangements of its events
    (the exact conditional null of homogeneity): each cell is a hypergeometric draw of its row's remaining events from
    the remaining column totals, vectorized over the tables."""
    rows, columns = table.sum(axis=1), table.sum(axis=0)
    remaining = np.tile(columns, (size, 1)).astype(np.int64)
    out = np.zeros((size, *table.shape), dtype=np.int64)
    for i in range(table.shape[0] - 1):
        need = np.full(size, rows[i], dtype=np.int64)
        for j in range(table.shape[1] - 1):
            good, bad = remaining[:, j], remaining[:, j + 1 :].sum(axis=1)
            drawn = np.zeros(size, dtype=np.int64)
            active = need > 0
            if active.any():
                drawn[active] = generator.hypergeometric(good[active], bad[active], need[active])
            out[:, i, j] = drawn
            remaining[:, j] -= drawn
            need -= drawn
        out[:, i, -1] = need
        remaining[:, -1] -= need
    out[:, -1, :] = remaining
    return out


def homogeneity(table: np.ndarray, generator: np.random.Generator, tables: int | None = None) -> dict[str, Any]:
    """Monte Carlo homogeneity test of an R x 4 table of eligible outcome counts (homogeneity_test of cases.json), at
    MC_TABLES tables unless `tables` names another count."""
    tables = MC_TABLES if tables is None else tables
    table = np.asarray(table, dtype=np.int64)
    kept = table[:, table.sum(axis=0) > 0]
    statistic = float(pearson(kept.astype(float)))
    exceed = 0
    for start in range(0, tables, 10000):
        size = min(10000, tables - start)
        drawn = conditional_tables(kept, generator, size)
        exceed += int(np.count_nonzero(pearson(drawn.astype(float)) >= statistic * (1.0 - 1e-12)))
    return {"statistic": statistic, "rows": int(kept.shape[0]), "p": (1 + exceed) / (1 + tables)}


def rate_test(k0: int, n0: int, k1: int, n1: int) -> float:
    from scipy.stats import binomtest

    return float(binomtest(k0, k0 + k1, n0 / (n0 + n1)).pvalue)


def t_quantile(level: float, df: int) -> float:
    from scipy.stats import t

    return float(t.ppf(level, df))


def mean_interval(values: Sequence[float], level: float = SCORE_LEVEL) -> dict[str, Any]:
    data = np.asarray(values, dtype=float)
    mean, se = float(data.mean()), float(data.std(ddof=1) / math.sqrt(len(data)))
    half = t_quantile(0.5 + level / 2, len(data) - 1) * se
    return {"mean": mean, "se": se, "df": len(data) - 1, "interval": [mean - half, mean + half], "values": list(values)}


# ---------------------------------------------------------------- estimates


def tally_arrays(tallies: Sequence[Mapping[str, Any]]) -> dict[str, np.ndarray]:
    return {
        "eligible": np.asarray([t["eligible"] for t in tallies], dtype=np.int64),
        "shots": np.asarray([t["shots"] for t in tallies], dtype=np.int64),
    }


def homogeneity_item(item: tuple[np.ndarray, np.random.Generator]) -> dict[str, Any]:
    """homogeneity of one (table, its own generator) pair, the unit parallel.py maps; each generator serves one test."""
    table, generator = item
    return homogeneity(table, generator)


def drift(runs: Mapping[str, Sequence[Mapping[str, Any]]], streams: Sequence[np.random.Generator]) -> dict[str, Any]:
    """Estimate 1 from per-job iteration tallies in request order."""
    tests: list[dict[str, Any]] = []
    digests: dict[str, dict[str, list[str]]] = {}
    missing: list[str] = []
    stream = iter(streams)
    pending: list[tuple[int, np.ndarray, np.random.Generator]] = []
    for anchor in ANCHORS:
        groups = {job: [t for t in runs[job] if t["setting"] == anchor and t["role"] == "anchor"] for job in JOBS}
        for job in JOBS:
            pending.append((len(tests), tally_arrays(groups[job])["eligible"], next(stream)))
            tests.append({"anchor": anchor, "test": f"positions in {job}"})
        between = np.asarray([tally_arrays(groups[job])["eligible"].sum(axis=0) for job in JOBS])
        pending.append((len(tests), between, next(stream)))
        tests.append({"anchor": anchor, "test": "job-00 against job-01"})
        k = [int(tally_arrays(groups[job])["eligible"].sum()) for job in JOBS]
        n = [int(tally_arrays(groups[job])["shots"].sum()) for job in JOBS]
        tests.append({"anchor": anchor, "test": "eligible rate between jobs", "p": rate_test(k[0], n[0], k[1], n[1])})
        digests[anchor] = {job: sorted({t["digest"] for t in groups[job] if t.get("digest")}) for job in JOBS}
        if any(not t.get("digest") for job in JOBS for t in groups[job]):
            missing.append(anchor)
    results = ordered_map(homogeneity_item, [(table, generator) for _, table, generator in pending], min_items=1)
    for (position, _, _), result in zip(pending, results, strict=True):
        tests[position].update(result)
    threshold = ALPHA / DRIFT_TESTS
    passed = all(test["p"] > threshold for test in tests)
    one_mesh_within = {a: a not in missing and all(len(d[job]) == 1 for job in JOBS) for a, d in digests.items()}
    same_mesh_across = {a: one_mesh_within[a] and d[JOBS[0]] == d[JOBS[1]] for a, d in digests.items()}
    return {
        "tests": tests,
        "threshold": threshold,
        "all_pass": passed,
        "computed_circuit_digests": digests,
        "anchors_missing_computed_circuit": missing,
        "one_mesh_within_each_job": one_mesh_within,
        "same_mesh_across_jobs": same_mesh_across,
        "pooled": passed and all(same_mesh_across.values()),
    }


def ensemble_groups(runs: Mapping[str, Sequence[Mapping[str, Any]]]) -> dict[str, list[Mapping[str, Any]]]:
    """Each ensemble setting's ten tallies in seed-index order."""
    out: dict[str, list[Mapping[str, Any]]] = {}
    for row in base_settings():
        members = [t for job in JOBS for t in runs[job] if t["setting"] == row["name"] and t["role"] == "ensemble"]
        out[row["name"]] = sorted(members, key=lambda t: t["seed_index"])
    return out


def mesh_variance(
    groups: Mapping[str, Sequence[Mapping[str, Any]]], streams: Sequence[np.random.Generator], pooled: bool
) -> dict:
    """Estimate 2: each setting's ten seeds when the jobs pool, else each job's five, so a shift between the jobs never
    reads as mesh variance. streams holds 2 * MESH_TESTS generators; the pooled test takes the first MESH_TESTS."""
    blocks: list[tuple[str, str, list[Mapping[str, Any]]]] = []
    for name, members in groups.items():
        if pooled:
            blocks.append((name, name, list(members)))
        else:
            for j, job in enumerate(JOBS):
                low, high = j * SEEDS_PER_JOB + 1, (j + 1) * SEEDS_PER_JOB
                blocks.append((name, f"{name} {job}", [t for t in members if low <= t["seed_index"] <= high]))
    assigned = list(zip(blocks, streams, strict=False))
    tests = ordered_map(
        homogeneity_item,
        [(tally_arrays(members)["eligible"], generator) for (_, _, members), generator in assigned],
        min_items=1,
    )
    rows: dict[str, Any] = {}
    for ((setting, label, members), _), test in zip(assigned, tests, strict=True):
        table = tally_arrays(members)["eligible"]
        correct = np.asarray([t["eligible"][t["correct_outcome"]] for t in members], dtype=float)
        events = table.sum(axis=1).astype(float)
        fraction = correct / events
        binomial = float(np.mean(fraction * (1 - fraction) / events))
        between = float(np.var(fraction, ddof=1))
        rows[label] = {
            "setting": setting,
            **test,
            "correct_fraction_variance": between,
            "mean_binomial_variance": binomial,
            "excess_variance": between - binomial,
            "distinct_meshes": len({t.get("digest") for t in members if t.get("digest")}),
            "seeds": len(members),
        }
    threshold = ALPHA / len(rows)
    return {
        "pooled": pooled,
        "settings": rows,
        "threshold": threshold,
        "rejects": sorted(n for n, r in rows.items() if r["p"] <= threshold),
    }


def scores_by_seed(groups: Mapping[str, Sequence[Mapping[str, Any]]], indices: Sequence[int]) -> dict[str, Any]:
    """F_T(s) and F'_T(s) for each table T and seed index s in `indices`."""
    out: dict[str, Any] = {}
    for table, inputs in TABLES.items():
        names = [f"in-{c}{t}-{table}" for c, t in inputs]
        primary, per_input = [], []
        for s in indices:
            picked = [next(t for t in groups[name] if t["seed_index"] == s) for name in names]
            correct = np.asarray([t["eligible"][t["correct_outcome"]] for t in picked], dtype=float)
            eligible = np.asarray([sum(t["eligible"]) for t in picked], dtype=float)
            shots = np.asarray([t["shots"] for t in picked], dtype=float)
            f, f_prime = table_scores(correct, eligible, shots)
            primary.append(f)
            per_input.append(f_prime)
        out[table] = {"F": primary, "F_prime": per_input}
    return out


def score_estimates(groups: Mapping[str, Sequence[Mapping[str, Any]]], pooled: bool, prediction: Mapping) -> dict:
    """Estimates 3, 4 and 5."""
    blocks = (
        {"pooled": list(range(1, 11))}
        if pooled
        else {
            JOBS[0]: list(range(1, SEEDS_PER_JOB + 1)),
            JOBS[1]: list(range(SEEDS_PER_JOB + 1, 2 * SEEDS_PER_JOB + 1)),
        }
    )
    out: dict[str, Any] = {}
    for label, indices in blocks.items():
        by_seed = scores_by_seed(groups, indices)
        tables = {
            table: {
                "F": mean_interval(values["F"]),
                "F_prime": mean_interval(values["F_prime"]),
                "difference_from_tomography": difference(
                    mean_interval(values["F"]), prediction[table]["F"], prediction[table]["F_sd"]
                ),
            }
            for table, values in by_seed.items()
        }
        block: dict[str, Any] = {"seed_indices": indices, "tables": tables}
        if pooled:
            lower_terms = [a + b - 1 for a, b in zip(by_seed["ZX"]["F"], by_seed["XZ"]["F"], strict=True)]
            lower = mean_interval(lower_terms)
            df = len(indices) - 1
            low = lower["mean"] - t_quantile(BOUND_LOWER_LEVEL, df) * lower["se"]
            uppers = [tables[t]["F"]["mean"] + t_quantile(BOUND_UPPER_LEVEL, df) * tables[t]["F"]["se"] for t in TABLES]
            block["hofmann_interval"] = {
                "L": low,
                "U": min(uppers),
                "conditional_on": "one process for every setting and one chance of a shot per attempt",
            }
        out[label] = block
    return out


def difference(estimate: Mapping[str, Any], predicted: float, predicted_sd: float) -> dict[str, Any]:
    """Estimate 5: the ensemble mean minus the prediction, its interval at estimate 3's t quantile on the combined
    standard error of the two independent estimates."""
    se = math.sqrt(estimate["se"] ** 2 + predicted_sd**2)
    half = t_quantile(0.5 + SCORE_LEVEL / 2, estimate["df"]) * se
    centre = estimate["mean"] - predicted
    shifted = [centre - half, centre + half]
    sign = "contains_zero" if shifted[0] <= 0 <= shifted[1] else ("above_zero" if shifted[0] > 0 else "below_zero")
    return {
        "predicted": predicted,
        "predicted_sd": predicted_sd,
        "difference": centre,
        "se": se,
        "interval": shifted,
        "reading": sign,
    }


def analysis_streams(seed: int) -> tuple[list[np.random.Generator], list[np.random.Generator]]:
    """One SeedSequence per test, drift tests first, then one per per-job mesh test, so a result does not depend on
    evaluation order or on whether the jobs pool."""
    children = np.random.SeedSequence(seed).spawn(DRIFT_TESTS + 2 * MESH_TESTS)
    generators = [np.random.default_rng(child) for child in children]
    return generators[:DRIFT_TESTS], generators[DRIFT_TESTS:]


def estimates(runs: Mapping[str, Sequence[Mapping[str, Any]]], seed: int, prediction: Mapping) -> dict[str, Any]:
    drift_streams, mesh_streams = analysis_streams(seed)
    first = drift(runs, drift_streams)
    groups = ensemble_groups(runs)
    return {
        "estimate_1_drift": first,
        "estimate_2_mesh_variance": mesh_variance(groups, mesh_streams, first["pooled"]),
        "scores": score_estimates(groups, first["pooled"], prediction),
    }


# ---------------------------------------------------------------- the retained tomography's prediction


@cache
def tomography_arrays() -> dict[str, np.ndarray]:
    """Eligible events, samples, shots and job scale of the 144 retained tomography settings in schedule order."""
    loaded = [tomo.load_run(ROOT / run) for run in TOMOGRAPHY_RUNS]
    pool = tomo.pooling(loaded)
    tallies: dict[str, Any] = {}
    for entry in loaded:
        tallies.update(entry["tallies"])
    rows = tomo.schedule()
    return {
        "eligible": np.asarray([tallies[row["name"]]["eligible"] for row in rows], dtype=float),
        "samples": np.asarray([tallies[row["name"]]["samples"] for row in rows], dtype=float),
        "shots": np.asarray([tallies[row["name"]]["shots"] for row in rows], dtype=float),
        "scale": np.asarray([pool["scales"][row["job"]] for row in rows]),
    }


@cache
def tomography_choi() -> tuple[np.ndarray, float]:
    """The unprojected tomography fit from the two retained runs, and its process fidelity."""
    a = tomography_arrays()
    choi = tomo.linear_inversion(tomo.absolute_rates(a["eligible"], a["shots"], a["scale"]))
    return choi, tomo.trace_normalized_fidelity(choi)


def exact_fraction(endpoint: arb) -> Fraction:
    """The exact rational value of an exact arb (a ball endpoint), from its dyadic mantissa and exponent."""
    mantissa, exponent = (int(v) for v in endpoint.man_exp())
    return Fraction(mantissa) * 2**exponent if exponent >= 0 else Fraction(mantissa, 2**-exponent)


def exact_float(endpoint: arb) -> float:
    """The float64 nearest an exact arb value: Fraction division rounds to nearest, ties to even."""
    return float(exact_fraction(endpoint))


def certified_float(value: arb) -> float | None:
    """The float64 every point of the ball rounds to, or None when the ball straddles a rounding boundary."""
    low, high = exact_float(value.lower()), exact_float(value.upper())
    return low if low == high else None


def to_arb_mat(rows: np.ndarray) -> arb_mat:
    return arb_mat([[arb(float(v)) for v in row] for row in np.asarray(rows, dtype=np.float64)])


def nonnegative_sqrt(value: arb) -> arb:
    """The root of a ball whose exact value is a variance: its part below zero holds no admissible value."""
    return value.nonnegative_part().sqrt()


def order_statistic(values: Sequence[arb], k: int) -> arb:
    """A ball holding the k-th smallest exact value: it lies between the k-th smallest lower and upper endpoints."""
    return sorted((v.lower() for v in values), key=exact_fraction)[k].union(
        sorted((v.upper() for v in values), key=exact_fraction)[k]
    )


def percentile_ball(values: Sequence[arb], q: float) -> arb:
    """numpy.percentile's default linear interpolation of the q-th percentile, enclosed."""
    h = q / 100 * (len(values) - 1)  # numpy's float64 virtual index, taken exactly
    low = math.floor(h)
    weight = arb(h) - low
    below, above = order_statistic(values, low), order_statistic(values, min(low + 1, len(values) - 1))
    return below + (above - below) * weight


@cache
def prediction_inputs() -> dict[str, Any]:
    """The float64 inputs of the certified prediction: the tomography design, the rate observables of the eight
    settings with their names, and the real and imaginary parts of the Hermitian basis."""
    rows: list[np.ndarray] = []
    names: list[tuple[str, str, int]] = []
    for table, inputs in TABLES.items():
        for control, target in inputs:
            row = {"name": f"in-{control}{target}-{table}", "input": control + target, "basis": table}
            names.append((table, row["name"], correct_outcome(row)))
            density = input_density(row["input"]).T
            rows.extend(np.kron(density, tomo.outcome_projector(table, o)) for o in range(4))
    basis = np.transpose(tomo.hermitian_stack(), (0, 2, 1)).reshape(256, -1)
    return {"design": tomo.design_matrix(), "observables": np.asarray(rows), "basis": basis, "names": names}


def ball_parts(value: arb) -> tuple[int, int, int, int]:
    """The exact dyadic midpoint and radius of a ball as (mantissa, exponent) pairs, which pickle."""
    mid, rad = value.mid().man_exp(), value.rad().man_exp()
    return int(mid[0]), int(mid[1]), int(rad[0]), int(rad[1])


def from_parts(parts: Sequence[int]) -> arb:
    """The ball of ball_parts: the midpoint exact, the radius rounded up to arb's radius type, so it still encloses."""
    return arb(arf((parts[0], parts[1])), arf((parts[2], parts[3])))


def solve_columns(columns: np.ndarray) -> arb_mat:
    """The least-squares coefficients of each column at ctx.prec: pinv(A) b of the full-column-rank design A equals the
    solution of the normal equations (A^T A) x = A^T b, which arb_mat solves with a rigorous radius on the float64
    inputs."""
    a = to_arb_mat(prediction_inputs()["design"])
    at = a.transpose()
    return (at * a).solve(at * to_arb_mat(columns))


def column_balls(item: tuple[np.ndarray, int]) -> dict[str, Any]:
    """Rates, F and F' of each column of one batch of observed rates (576 x k) at one working precision, as
    ball_parts. A rate is Tr[(rho^T x E) J] = sum_k x_k Tr[(rho^T x E) H_k], formed exactly on the doubles."""
    columns, precision = item
    ctx.prec = precision
    inputs = prediction_inputs()
    observables = inputs["observables"].reshape(len(inputs["observables"]), -1)
    basis = inputs["basis"]
    rate_matrix = to_arb_mat(observables.real) * to_arb_mat(basis.real).transpose()
    rate_matrix -= to_arb_mat(observables.imag) * to_arb_mat(basis.imag).transpose()
    rates = rate_matrix * solve_columns(columns)
    out: dict[str, Any] = {"rates": [], "F": {t: [] for t in TABLES}, "F_prime": {t: [] for t in TABLES}}
    for k in range(rates.ncols()):
        sums: dict[str, list[arb]] = {t: [arb(0), arb(0), arb(0)] for t in TABLES}
        column = []
        for i, (table, _, correct_index) in enumerate(inputs["names"]):
            values = [rates[4 * i + o, k] for o in range(4)]
            column.append([ball_parts(v) for v in values])
            eligible = values[0] + values[1] + values[2] + values[3]
            correct = values[correct_index]
            sums[table][0] += correct
            sums[table][1] += eligible
            sums[table][2] += correct / eligible
        out["rates"].append(column)
        for table, (correct, eligible, ratio) in sums.items():
            out["F"][table].append(ball_parts(correct / eligible))
            out["F_prime"][table].append(ball_parts(ratio / 4))
    return out


def prediction_balls(columns: np.ndarray, precision: int) -> dict[str, Any]:
    """Rates of the point column, F and F' of each column of observed rates (576 x K), and the point column's process
    fidelity, as arb balls. The columns are scored in batches through parallel.ordered_map, each worker solving its
    batch at the same precision; the certified values do not depend on the batching, since each is the correct
    rounding of an exact value its ball encloses."""
    ctx.prec, ctx.threads = precision, 1
    inputs = prediction_inputs()
    count = max(1, min(4 * workers(), columns.shape[1] // MIN_BATCH_COLUMNS))
    batches = [columns[:, idx] for idx in np.array_split(np.arange(columns.shape[1]), count)]
    scored = ordered_map(column_balls, [(batch, precision) for batch in batches], min_items=2)
    out: dict[str, Any] = {"rates": {}, "F": {t: [] for t in TABLES}, "F_prime": {t: [] for t in TABLES}}
    for part in scored:
        for table in TABLES:
            out["F"][table].extend(from_parts(v) for v in part["F"][table])
            out["F_prime"][table].extend(from_parts(v) for v in part["F_prime"][table])
    for (_, name, _), values in zip(inputs["names"], scored[0]["rates"][0], strict=True):
        out["rates"][name] = [from_parts(v) for v in values]
    vector = tomo.ideal_choi_vector()
    require(not np.any(vector.imag), "the ideal CZ Choi vector is not real")
    weights = np.vstack([np.outer(vector.real, vector.real).reshape(-1), np.eye(16).reshape(-1)])
    x = solve_columns(columns[:, :1])
    functional = to_arb_mat(weights) * to_arb_mat(tomo.hermitian_stack().real.reshape(256, -1)).transpose() * x
    out["process_fidelity"] = functional[0, 0] / (4 * functional[1, 0])
    # the certificate covers these float64 bits, which float64 libm and BLAS calls produce; their digests let a replay
    # tell an input that moved from an output that did
    out["inputs_sha256"] = {
        name: hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()
        for name, array in (
            ("design_matrix", inputs["design"]),
            ("rate_observables", inputs["observables"]),
            ("hermitian_basis", tomo.hermitian_stack()),
            ("ideal_choi_vector", vector),
            ("observed_rate_columns", columns),
        )
    }
    return out


def certified_prediction(columns: np.ndarray) -> tuple[dict[str, Any], int]:
    """The prediction record with every float64 certified as the correctly rounded value of its ball, at the first
    precision of CERTIFIED_PRECISIONS where every value certifies."""
    for precision in CERTIFIED_PRECISIONS:
        balls = prediction_balls(columns, precision)
        record: dict[str, Any] = {"rates": {}, "inputs_sha256": balls["inputs_sha256"]}
        floats: list[float | None] = []
        for name, values in balls["rates"].items():
            record["rates"][name] = [certified_float(v) for v in values]
            floats.extend(record["rates"][name])
        record["process_fidelity"] = certified_float(balls["process_fidelity"])
        floats.append(record["process_fidelity"])
        for table in TABLES:
            replicates = balls["F"][table][1:]
            n = len(replicates)
            mean = sum(replicates, arb(0)) / n
            sd = nonnegative_sqrt(sum(((v - mean) ** 2 for v in replicates), arb(0)) / (n - 1))
            scores = [certified_float(balls["F"][table][0]), certified_float(balls["F_prime"][table][0])]
            spread = certified_float(sd)
            percentiles = [certified_float(percentile_ball(replicates, q)) for q in (2.5, 97.5)]
            floats.extend([*scores, spread, *percentiles])
            record[table] = {"F": scores[0], "F_prime": scores[1], "F_sd": spread, "F_percentile_95": percentiles}
        if all(v is not None for v in floats):
            return record, precision
    raise RuntimeError(f"a prediction value straddles a float64 rounding boundary at {CERTIFIED_PRECISIONS[-1]} bits")


def tomography_prediction() -> dict[str, Any]:
    """Estimate 5's reference: the rates the retained fit predicts for the eight settings, its table scores, and the
    bootstrap spread of F, each float64 the certified correct rounding of an arb enclosure computed from the float64
    inputs whose digests the record carries. The solve and every step after it are independent of the BLAS and its
    thread count; the inputs come from float64 libm and BLAS calls, so the bytes match across hosts whose input
    digests match."""
    _, fidelity = tomography_choi()
    retained = json.loads((ROOT / TOMOGRAPHY_ANALYSIS).read_text(encoding="utf-8"))["process"]["process_fidelity"]
    require(abs(fidelity - retained) <= TOLERANCE, f"the recomputed fit reads {fidelity}, the retained {retained}")
    index, value = seed_plan()["prediction"]
    a = tomography_arrays()
    generator = np.random.default_rng(value)
    batch = tomo.resampled_rates(a["eligible"], a["samples"], a["shots"], a["scale"], generator, PREDICTION_REPLICATES)
    point = tomo.absolute_rates(a["eligible"], a["shots"], a["scale"])
    record, precision = certified_prediction(np.column_stack([point, batch.T]))
    return {
        "process_fidelity": record["process_fidelity"],
        "retained_analysis": TOMOGRAPHY_ANALYSIS,
        "rates": record["rates"],
        "bootstrap": {"replicates": PREDICTION_REPLICATES, "seed": {"draw": DRAW, "index": index}},
        "arithmetic": {
            "method": "arb normal equations (python-flint arb_mat)",
            "precision_bits": precision,
            "rounding": "each float64 is the correctly rounded value of every point of its arb enclosure",
            "inputs_sha256": record["inputs_sha256"],
        },
        **{table: record[table] for table in TABLES},
    }


def random_trace_non_increasing_map(generator: np.random.Generator) -> list[np.ndarray]:
    """Kraus operators of a random CP map on two qubits, scaled so sum K^dagger K <= 1 with a random top eigenvalue in
    (0, 1]. Half the maps are Ginibre maps of rank 1 to 4; the other half are CZ times a random input filter diag(d)
    plus a weak random Kraus term, the input-dependent-success regime near the bound."""
    rank = int(generator.integers(1, 5))
    kraus = [generator.normal(size=(4, 4)) + 1j * generator.normal(size=(4, 4)) for _ in range(rank)]
    if generator.uniform() < 0.5:
        weak = float(generator.uniform(0.0, 0.3))
        kraus = [tomo.ideal_cz() @ np.diag(generator.uniform(0.0, 1.0, size=4))] + [weak * k for k in kraus]
    top = float(np.linalg.eigvalsh(sum(k.conj().T @ k for k in kraus)).max())
    scale = math.sqrt(float(generator.uniform(0.0, 1.0)) / top)
    return [k * scale for k in kraus]


def bound_margins(item: int) -> tuple[float, float]:
    """(F - (F_ZX + F_XZ - 1), min(F_ZX, F_XZ) - F) of one random map, seeded by its SeedSequence child index."""
    _, value = seed_plan()["bound_check"]
    # SeedSequence(value, spawn_key=(item,)) is child `item` of SeedSequence(value).spawn(...).
    generator = np.random.default_rng(np.random.SeedSequence(value, spawn_key=(item,)))
    scores = map_scores(random_trace_non_increasing_map(generator))
    f = scores["process_fidelity"]
    return f - (scores["F_ZX"] + scores["F_XZ"] - 1), min(scores["F_ZX"], scores["F_XZ"]) - f


def bound_check(maps: int = BOUND_CHECK_MAPS) -> dict[str, Any]:
    """The normalized Hofmann bound on random trace-non-increasing CP maps: the smallest margin of each side."""
    margins = ordered_map(bound_margins, list(range(maps)), min_items=1)
    index, _ = seed_plan()["bound_check"]
    return {
        "maps": maps,
        "seed": {"draw": DRAW, "index": index},
        "least_lower_margin": float(min(m[0] for m in margins)),
        "least_upper_margin": float(min(m[1] for m in margins)),
        "violations": sum(1 for m in margins if min(m) < -1e-12),
    }


# ---------------------------------------------------------------- noise forecast


def forecast_setting(item: tuple[dict[str, Any], dict[str, float], list[float]]) -> dict[str, Any]:
    """Per variant of tomo.FORECAST_VARIANTS: the chance per attempt of any click and of two or more, and of each
    eligible outcome, from Perceval's NoiseModel through tomo.detected_clicks."""
    row, figures, dark_rates = item
    unitary = setting_unitary(row)
    photons = tomo.photon_distribution(unitary, figures["hom"], figures["g2"])
    pure = tomo.photon_distribution(unitary, figures["hom"], 0.0)
    corrected = tomo.photon_distribution(unitary, tomo.corrected_overlap(figures["hom"], figures["g2"]), figures["g2"])
    dark = [rate / (figures["clock_mhz"] * 1e6) for rate in dark_rates]
    quiet = [0.0] * tomo.MODES
    configurations = {
        "indistinguishability only": (pure, 1.0, quiet),
        "source only": (photons, 1.0, quiet),
        "source and loss": (photons, figures["transmittance"], quiet),
        "source, loss and dark counts": (photons, figures["transmittance"], dark),
        "g2-corrected overlap, loss and dark counts": (corrected, figures["transmittance"], dark),
    }
    out: dict[str, Any] = {}
    for name, (distribution, efficiency, dark_chance) in configurations.items():
        clicks = tomo.detected_clicks(distribution, efficiency, dark_chance)
        eligible = [0.0] * 4
        for vector, p in clicks.items():
            outcome = tomo.outcome_of(vector)
            if outcome is not None:
                eligible[outcome] += p
        out[name] = {
            "any_click_probability": sum(p for vector, p in clicks.items() if sum(vector) >= 1),
            "sample_probability": sum(p for vector, p in clicks.items() if sum(vector) >= tomo.MIN_CLICKS),
            "eligible_probabilities": eligible,
        }
    return out


def variant_scores(per_setting: Mapping[str, Mapping[str, Any]], variant: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for table, inputs in TABLES.items():
        correct, eligible, shots = [], [], []
        for control, target in inputs:
            row = {"name": f"in-{control}{target}-{table}", "input": control + target, "basis": table}
            entry = per_setting[row["name"]][variant]
            correct.append(entry["eligible_probabilities"][correct_outcome(row)])
            eligible.append(sum(entry["eligible_probabilities"]))
            shots.append(entry["any_click_probability"])
        f, f_prime = table_scores(np.asarray(correct), np.asarray(eligible), np.asarray(shots))
        out[table] = {"F": f, "F_prime": f_prime}
    out["hofmann_interval"] = [out["ZX"]["F"] + out["XZ"]["F"] - 1, min(out["ZX"]["F"], out["XZ"]["F"])]
    return out


def synthetic_tallies(
    per_setting: Mapping[str, Mapping[str, Any]], generator: np.random.Generator
) -> dict[str, list[dict[str, Any]]]:
    """One dataset under the null of no drift and no mesh variance: each iteration stops at its samples, which fall
    multinomially over the four eligible outcomes and the rest, and its shots are the samples plus a negative binomial
    count of failures at the sample share of a shot."""
    runs: dict[str, list[dict[str, Any]]] = {}
    for job in JOBS:
        rows = []
        for row in job_schedule(job):
            entry = per_setting[row["setting"]][FALSE_ALARM_VARIANT]
            sample = entry["sample_probability"]
            p = [e / sample for e in entry["eligible_probabilities"]]
            drawn = generator.multinomial(SAMPLES_PER_ITERATION, [*p, max(0.0, 1.0 - sum(p))])
            shots = SAMPLES_PER_ITERATION + int(
                generator.negative_binomial(SAMPLES_PER_ITERATION, sample / entry["any_click_probability"])
            )
            rows.append(
                {
                    **{key: row[key] for key in ("setting", "role")},
                    "seed_index": row.get("seed_index"),
                    "correct_outcome": correct_outcome(row),
                    "eligible": [int(v) for v in drawn[:4]],
                    "shots": shots,
                    "digest": "one-mesh",
                }
            )
        runs[job] = rows
    return runs


def false_alarm_dataset(item: tuple[Mapping[str, Mapping[str, Any]], np.random.SeedSequence]) -> dict[str, Any]:
    per_setting, sequence = item
    data_sequence, test_sequence = sequence.spawn(2)
    runs = synthetic_tallies(per_setting, np.random.default_rng(data_sequence))
    children = test_sequence.spawn(DRIFT_TESTS + 2 * MESH_TESTS)
    generators = [np.random.default_rng(child) for child in children]
    first = drift(runs, generators[:DRIFT_TESTS])
    second = mesh_variance(ensemble_groups(runs), generators[DRIFT_TESTS:], first["pooled"])
    return {
        "drift_p": [test["p"] for test in first["tests"]],
        "mesh_p": [row["p"] for row in second["settings"].values()],
        "drift_family_rejects": not first["all_pass"],
        "mesh_family_rejects": bool(second["rejects"]),
        "pooled": first["pooled"],
    }


def false_alarm_study(per_setting: Mapping[str, Mapping[str, Any]], datasets: int = FALSE_ALARM_DATASETS) -> dict:
    """The family-wise rejection rates of estimates 1 and 2 when the forecast law holds at every seed and position."""
    index, value = seed_plan()["false_alarm"]
    sequences = np.random.SeedSequence(value).spawn(datasets)
    results = ordered_map(false_alarm_dataset, [(per_setting, s) for s in sequences], min_items=1)
    from scipy.stats import binomtest

    drift_p = np.asarray([r["drift_p"] for r in results])
    mesh_p = np.asarray([p for r in results for p in r["mesh_p"]])
    out: dict[str, Any] = {
        "variant": FALSE_ALARM_VARIANT,
        "datasets": datasets,
        "monte_carlo_tables": MC_TABLES,
        "seed": {"draw": DRAW, "index": index},
        "drift_test_rate_at_unadjusted_alpha": [float(v) for v in np.mean(drift_p <= ALPHA, axis=0)],
        "mesh_test_rate_at_unadjusted_alpha": float(np.mean(mesh_p <= ALPHA)),
        "unpooled_datasets": sum(1 for r in results if not r["pooled"]),
    }
    for family in ("drift", "mesh"):
        rejects = sum(1 for r in results if r[f"{family}_family_rejects"])
        interval = binomtest(rejects, datasets).proportion_ci(confidence_level=0.95, method="exact")
        out[f"{family}_family_rate"] = rejects / datasets
        out[f"{family}_family_rate_interval"] = [float(interval.low), float(interval.high)]
    return out


def forecast() -> dict[str, Any]:
    perfs = read_perfs()
    figures = tomo.perf_figures(perfs)
    dark = list(perfs["Dark counts (detection/s)"])
    bases = base_settings()
    computed = ordered_map(forecast_setting, [(row, figures, dark) for row in bases], min_items=1)
    per_setting = {row["name"]: entry for row, entry in zip(bases, computed, strict=True)}
    variants = {name: variant_scores(per_setting, name) for name in tomo.FORECAST_VARIANTS}
    expected = {
        name: {
            "eligible_events_per_iteration": SAMPLES_PER_ITERATION
            * sum(entry[FALSE_ALARM_VARIANT]["eligible_probabilities"])
            / entry[FALSE_ALARM_VARIANT]["sample_probability"],
            "shots_per_iteration": SAMPLES_PER_ITERATION
            * entry[FALSE_ALARM_VARIANT]["any_click_probability"]
            / entry[FALSE_ALARM_VARIANT]["sample_probability"],
        }
        for name, entry in per_setting.items()
    }
    return {
        "schema": "qd-cz-ensemble-forecast-v1",
        "read": {"path": READ, "sha256": qd_platform.sha256_bytes((FAMILY_DIR / READ).read_bytes()), **figures},
        "samples_per_iteration": SAMPLES_PER_ITERATION,
        "variants": variants,
        "expected_by_setting": expected,
        "tomography_prediction": tomography_prediction(),
        "bound_check": bound_check(),
        "false_alarm": false_alarm_study(per_setting),
        "settings": per_setting,
    }


def forecast_bytes() -> bytes:
    return (json.dumps(forecast(), indent=1, sort_keys=True) + "\n").encode()


# ---------------------------------------------------------------- checks


def worst_case_seconds(job: str) -> float:
    figures = tomo.perf_figures(read_perfs())
    rate = figures["clock_mhz"] * 1e6 * (1.0 - (1.0 - figures["transmittance"]) ** 2)
    return tomo.ITERATION_SECONDS * ITERATIONS + JOB_SHOTS[job] * ITERATIONS / rate


def expected_seconds_model(job: str) -> float:
    figures = tomo.perf_figures(read_perfs())
    rate = figures["clock_mhz"] * 1e6 * (1.0 - (1.0 - figures["transmittance"]) ** 2)
    plan = json.loads((FAMILY_DIR / job / "plan-read.json").read_text(encoding="utf-8"))
    return tomo.ITERATION_SECONDS * ITERATIONS + plan["estimated_shots"] / rate


def check_schedule(job: str) -> None:
    rows = job_schedule(job)
    require(len(rows) == ITERATIONS, f"{job}: {len(rows)} iterations")
    for start in ANCHOR_STARTS:
        names = [rows[start + i]["setting"] for i in range(len(ANCHORS))]
        require(names == list(ANCHORS) and all(rows[start + i]["role"] == "anchor" for i in range(4)), f"{job}")
    ensemble = [row for row in rows if row["role"] == "ensemble"]
    require(len(ensemble) == len(base_settings()) * SEEDS_PER_JOB, f"{job}: {len(ensemble)} ensemble iterations")
    for row in base_settings():
        mine = [r for r in ensemble if r["setting"] == row["name"]]
        offset = JOBS.index(job) * SEEDS_PER_JOB
        require(sorted(r["seed_index"] for r in mine) == list(range(offset + 1, offset + 6)), f"{job}: {row['name']}")
        require({r["segment"] for r in mine} == set(range(SEGMENTS)), f"{job}: {row['name']} misses a segment")
    for segment in range(SEGMENTS):
        require(sum(1 for r in ensemble if r["segment"] == segment) == SEGMENT_SIZE, f"{job}: segment {segment}")
    seeds = [row["compilation_seed"] for row in ensemble]
    require(len(set(seeds)) == len(seeds) and 0 not in seeds, f"{job}: an ensemble seed repeats or is zero")
    anchor_seeds = {row["setting"]: row["compilation_seed"] for row in rows if row["role"] == "anchor"}
    require(set(anchor_seeds.values()).isdisjoint(seeds), f"{job}: an anchor seed is also an ensemble seed")


def check_job(job: str) -> str:
    out = FAMILY_DIR / job
    check_schedule(job)
    rebuilt = documents(job)
    for name, data in rebuilt.items():
        require((out / name).read_bytes() == data, f"{out}/{name} differs from the builder's bytes")
    manifest, circuit, _ = qd_platform.load_case(out)
    experiment, settings = qd_platform.template_experiment(manifest, circuit)
    require(experiment is not None and len(settings) == ITERATIONS, f"{job}: the template did not bind")
    require(manifest["max_samples"] == SAMPLES_PER_ITERATION * ITERATIONS, f"{job}: max_samples")
    require(manifest["max_shots"] == JOB_SHOTS[job] * ITERATIONS, f"{job}: max_shots")
    plan = json.loads((out / "plan-read.json").read_text(encoding="utf-8"))
    require(plan["cases_sha256"] == qd_platform.sha256_bytes((out / "cases.json").read_bytes()), f"{job}: stale plan")
    ceiling = PER_JOB_CREDITS + JOB_SHOTS[job] * PRICE_PER_SHOT
    require(abs(plan["credit_ceiling"] - ceiling) < TOLERANCE, f"{job}: the plan's credit ceiling is not {ceiling}")
    # plan-read.json is a read of the live platform, not a reproducible build; its request-derived fields must name
    # this request.
    for key, want in (
        ("case", job),
        ("platform", PLATFORM),
        ("per_job_credits", PER_JOB_CREDITS),
        ("max_samples", manifest["max_samples"]),
        ("max_shots", manifest["max_shots"]),
        ("max_credits", round(ceiling, 6)),
        ("expected_seconds", float(EXPECTED_SECONDS)),
    ):
        require(plan.get(key) == want, f"{job}: plan-read.json {key} reads {plan.get(key)!r}, not {want!r}")
    require(set(plan["admitted_statuses"]) <= {"available", "running"}, f"{job}: the plan admits other statuses")
    estimate = json.loads((FAMILY_DIR / ESTIMATE).read_text(encoding="utf-8"))["jobs"][job]
    inputs = estimate["inputs"]
    require(sorted(inputs) == sorted(s["name"] for s in settings), f"{job}: {ESTIMATE} names other iterations")
    values = list(inputs.values())
    require(
        (estimate["smallest"], estimate["largest"]) == (min(values), max(values))
        and abs(estimate["mean"] - sum(values) / len(values)) <= TOLERANCE * max(values),
        f"{job}: {ESTIMATE} summary disagrees with its inputs",
    )
    cap = math.ceil(estimate["largest"] * SHOT_MARGIN / SHOT_QUANTUM) * SHOT_QUANTUM
    require(estimate["shots_per_iteration"] == cap == JOB_SHOTS[job], f"{job}: the shot cap is not {cap}")
    worst, expected = worst_case_seconds(job), expected_seconds_model(job)
    require(worst <= MAX_DURATION, f"{job}: every iteration at its cap takes {worst:.0f} s, past {MAX_DURATION} s")
    require(expected <= EXPECTED_SECONDS, f"{job}: the modeled {expected:.0f} s pass the {EXPECTED_SECONDS} s bound")
    return (
        f"{FAMILY}/{job}: {ITERATIONS} iterations bound, credit ceiling {ceiling:g}, "
        f"modeled {expected:.0f} s expected and {worst:.0f} s with every iteration at its cap"
    )


def check() -> int:
    for row in base_settings():
        conditional, _ = exact_outcomes(row)
        require(
            all(abs(a - b) <= 1e-9 for a, b in zip(conditional, ideal_outcomes(row), strict=True)),
            f"{row['name']}: the permanents of its unitary miss the ideal CZ outcomes",
        )
    connected = json.loads((FAMILY_DIR / READ).read_text(encoding="utf-8"))["connected_input_modes"]
    require(all(mode in connected for mode in tomo.SOURCES), f"chip modes {tomo.SOURCES} are not connected sources")
    total = sum(PER_JOB_CREDITS + JOB_SHOTS[job] * PRICE_PER_SHOT for job in JOBS)
    require(total <= CASE_CREDIT_CEILING, f"the two jobs' ceilings sum to {total}, past {CASE_CREDIT_CEILING}")
    anchors = [seed_plan()["anchors"][name][1] for name in ANCHORS]
    ensemble = [value for seeds in seed_plan()["ensemble"].values() for _, value in seeds]
    values = anchors + ensemble + [seed_plan()[key][1] for key in ("analysis", "false_alarm", "prediction")]
    values += [seed_plan()[key][1] for key in ("bound_check", "fixture")]
    require(len(set(values)) == len(values) and 0 not in values, "a seed repeats or is zero")
    for line in [check_job(job) for job in JOBS]:
        print(line)
    estimates_record = json.loads((FAMILY_DIR / ESTIMATE).read_text(encoding="utf-8"))["jobs"]
    for job in JOBS:
        require(estimates_record[job]["samples"] == SAMPLES_PER_ITERATION, f"{ESTIMATE} predates the sample budget")
        require(
            estimates_record[job]["shots_per_iteration"] == JOB_SHOTS[job],
            f"{job}: max_shots per iteration is {JOB_SHOTS[job]}, the estimate gives "
            f"{estimates_record[job]['shots_per_iteration']}",
        )
    retained = json.loads((FAMILY_DIR / FORECAST).read_text(encoding="utf-8"))
    require(
        retained["read"]["sha256"] == qd_platform.sha256_bytes((FAMILY_DIR / READ).read_bytes()),
        "forecast.json predates the retained platform read",
    )
    expected = retained["expected_by_setting"]
    least = min(row["eligible_events_per_iteration"] for row in expected.values())
    require(
        least >= MIN_ELIGIBLE, f"the forecast expects {least:.0f} eligible events in a setting, below {MIN_ELIGIBLE}"
    )
    study = retained["false_alarm"]
    for family in ("drift", "mesh"):
        low, high = study[f"{family}_family_rate_interval"]
        require(
            low <= ALPHA and high <= 2 * ALPHA,
            f"the {family} family's false-alarm rate interval [{low}, {high}] excludes the level {ALPHA} or passes "
            f"{2 * ALPHA}",
        )
    bound = retained["bound_check"]
    require(bound["violations"] == 0, f"{bound['violations']} random maps violate the normalized Hofmann bound")
    prediction = retained["tomography_prediction"]
    print(
        f"{FAMILY}: tomography fit {prediction['process_fidelity']:.6f} predicts F_ZX {prediction['ZX']['F']:.4f}, "
        f"F_XZ {prediction['XZ']['F']:.4f}; false alarms drift {study['drift_family_rate']}, "
        f"mesh {study['mesh_family_rate']}"
    )
    return 0


def moved_inputs(retained: dict[str, Any], recomputed: dict[str, Any]) -> list[str]:
    """Remove the prediction's input digests from both records and name the inputs whose float64 bits differ.

    The digests are exact strings over float64 bits that libm and BLAS produce, so another numeric identity may move
    them by an ulp; the floats they feed stay inside the tolerance first_difference applies, and the digests report
    which input moved instead of failing the comparison."""
    digests = [r["tomography_prediction"]["arithmetic"].pop("inputs_sha256") for r in (retained, recomputed)]
    return sorted(name for name in digests[0] if digests[0][name] != digests[1].get(name))


def check_forecast() -> int:
    retained = json.loads((FAMILY_DIR / FORECAST).read_text(encoding="utf-8"))
    recomputed = json.loads(forecast_bytes())
    moved = moved_inputs(retained, recomputed)
    found = tomo.first_difference(retained, recomputed)
    require(found is None, f"{FORECAST} differs from the recomputed forecast at {found}")
    if moved:
        print(f"tomography prediction inputs moved on this numeric identity: {', '.join(moved)}")
    for name, row in retained["variants"].items():
        print(f"{name}: F_ZX {row['ZX']['F']:.4f} F_XZ {row['XZ']['F']:.4f} Hofmann {row['hofmann_interval']}")
    return 0


# ---------------------------------------------------------------- platform reads


def platform_read() -> int:
    """Retain the live processor record's perfs and limits (a read-only platform call)."""
    processor = qd_platform.get(qd_platform.platform_route(PLATFORM))
    specs = processor.get("specs") or {}
    record = {
        "schema": "qd-cz-ensemble-platform-read-v1",
        "retrieved_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "status": processor.get("status"),
        "perfs": qd_platform.scrub(processor.get("perfs") or {}),
        "connected_input_modes": specs.get("connected_input_modes"),
        "constraints": specs.get("constraints"),
    }
    path = FAMILY_DIR / READ
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{PLATFORM}: {record['status']}, perfs {record['perfs']}")
    return 0


def shot_estimate(job: str) -> dict[str, Any]:
    """Perceval's estimate_required_shots of each iteration at the live performance figures, recorded while
    qd_platform.payload builds the job (a read-only platform call: nothing is sent)."""
    from perceval import RemoteComputer

    recorded: list[tuple[int, int | None]] = []
    original = RemoteComputer.estimate_required_shots

    def record(self: Any, computation: Any, nsamples: int, param_values: dict[str, float] | None = None) -> Any:
        value = original(self, computation, nsamples, param_values)
        recorded.append((nsamples, value))
        return value

    RemoteComputer.estimate_required_shots = record
    manifest, circuit, _ = qd_platform.load_case(FAMILY_DIR / job)
    try:
        qd_platform.payload(FAMILY_DIR / job, manifest, circuit, PLATFORM)
    except qd_platform.PlatformError:
        pass  # an estimate above max_shots stops payload only after the recorder holds it
    finally:
        RemoteComputer.estimate_required_shots = original
    require(len(recorded) == len(manifest["settings"]), f"{len(recorded)} estimates were recorded")
    require(all(value is not None for _, value in recorded), "Perceval estimates no sample of interest")
    values = [int(value) for _, value in recorded if value is not None]
    return {
        "samples": recorded[0][0],
        "smallest": min(values),
        "largest": max(values),
        "mean": sum(values) / len(values),
        "shots_per_iteration": math.ceil(max(values) * SHOT_MARGIN / SHOT_QUANTUM) * SHOT_QUANTUM,
        "inputs": {s["name"]: v for s, v in zip(manifest["settings"], values, strict=True)},
    }


def estimate_command() -> int:
    jobs = {job: shot_estimate(job) for job in JOBS}
    record = {
        "schema": "qd-cz-ensemble-shot-estimate-v1",
        "basis": "RemoteComputer.estimate_required_shots under the live perfs of qpu:ascella, per iteration",
        "jobs": jobs,
    }
    (FAMILY_DIR / ESTIMATE).write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    for job, row in jobs.items():
        print(f"{job}: {row['samples']} samples need up to {row['largest']} shots (cap {JOB_SHOTS[job]})")
    return 0


# ---------------------------------------------------------------- analysis


def load_run(run: Path) -> dict[str, Any]:
    """One collected run bound to its retained case (the binding rule of cases.json).

    qd_records.read_run binds the receipt, circuit, body, collection and raw result first. Returns the run's tallies in
    request order, each with its eligible outcome counts, samples, nb_shots_used and computed_circuit digest."""
    record = qd_records.read_run(run)
    manifest, submission, results = record.manifest, record.submission, record.collected
    job = manifest.get("job")
    require(manifest.get("family") == FAMILY and job in JOBS, f"{run}: not a run of {FAMILY}")
    retained = (FAMILY_DIR / str(job) / "cases.json").read_bytes()
    require(record.cases_sha256 == qd_platform.sha256_bytes(retained), f"{run}: cases.json differs from {job}")
    tallies, missing = bind_entries(str(run), manifest["settings"], results.get("iterations") or [])
    return {
        "job": job,
        "status": run_status(results),
        "cases_sha256": record.cases_sha256,
        "tallies": tallies,
        "uncounted": missing,
        "perfs": submission.get("perfs_at_plan"),
        "submitted_utc": submission.get("submitted_utc"),
    }


def run_status(results: Mapping[str, Any]) -> str | None:
    """The terminal status a collected results.json records under status.status, or None."""
    status = results.get("status")
    value = status.get("status") if isinstance(status, dict) else None
    return value if isinstance(value, str) else None


def bind_entries(
    run: str, settings: Sequence[Mapping[str, Any]], entries: Sequence[Any]
) -> tuple[list[dict[str, Any]], int]:
    """(tallies in request order, iterations without counts) of one run's returned entries.

    An ensemble entry binds to the setting whose unique compilation_seed it echoes; an anchor entry takes the next
    unbound member of its seed's group of five, in returned order. Every entry echoes its setting's circuit_params."""
    require(len(entries) <= len(settings), f"{run}: {len(entries)} iterations returned for {len(settings)}")
    ensemble = {s["compilation_seed"]: s for s in settings if s["role"] == "ensemble"}
    anchors: dict[int, list[Mapping[str, Any]]] = {}
    for s in settings:
        if s["role"] == "anchor":
            anchors.setdefault(s["compilation_seed"], []).append(s)
    bound: dict[str, dict[str, Any]] = {}
    missing = 0
    for entry in entries:
        counts = entry.get("counts") if isinstance(entry, dict) else None
        echo = (entry.get("iteration") or {}) if isinstance(entry, dict) else {}
        if not counts:
            missing += 1
            continue
        seed = echo.get("compilation_seed")
        if seed in ensemble:
            setting = ensemble[seed]
        else:
            group = anchors.get(seed) if isinstance(seed, int) else None
            require(bool(group), f"{run}: an iteration echoes seed {seed!r}, unbound or spent")
            setting = (group or []).pop(0)
        require(setting["name"] not in bound, f"{run}: two iterations bind to {setting['name']}")
        require(
            echo.get("circuit_params") == setting["circuit_params"], f"{run}: {setting['name']} echoes other params"
        )
        eligible = [0, 0, 0, 0]
        for key, count in counts.items():
            outcome = tomo.outcome_of([1 if n else 0 for n in tomo.parse_state(key)])
            if outcome is not None:
                eligible[outcome] += count
        samples = sum(counts.values())
        shots = (entry.get("result_fields") or {}).get("nb_shots_used")
        require(isinstance(shots, int) and not isinstance(shots, bool) and shots >= samples, f"{run}: shots {shots!r}")
        computed = (entry.get("result_fields") or {}).get("computed_circuit")
        bound[setting["name"]] = {
            "setting": setting["setting"],
            "role": setting["role"],
            "seed_index": setting.get("seed_index"),
            "correct_outcome": setting["correct_outcome"],
            "eligible": eligible,
            "samples": samples,
            "shots": shots,
            "digest": (
                qd_platform.sha256_bytes(computed.encode()) if isinstance(computed, str) and computed.strip() else None
            ),
        }
    return [bound[s["name"]] for s in settings if s["name"] in bound], missing


def analyze(runs: Sequence[Path]) -> dict[str, Any]:
    return summarize([load_run(run) for run in runs])


def summarize(loaded: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """The preregistered record of two loaded runs: undecided unless both completed and every iteration counts its
    eligible events."""
    jobs = [entry["job"] for entry in loaded]
    require(sorted(jobs) == sorted(JOBS) and len(set(jobs)) == len(jobs), f"the runs are not both jobs: {jobs}")
    by_job = {entry["job"]: entry["tallies"] for entry in loaded}
    short = {job: [t for t in tallies if sum(t["eligible"]) < MIN_ELIGIBLE] for job, tallies in by_job.items()}
    record: dict[str, Any] = {
        "schema": "qd-cz-ensemble-analysis-v1",
        "runs": [{"job": e["job"], "cases_sha256": e["cases_sha256"], "counted": len(e["tallies"])} for e in loaded],
        "uncounted": {e["job"]: e["uncounted"] for e in loaded},
        "job_status": {e["job"]: e.get("status") for e in loaded},
        "eligible_events": {job: [sum(t["eligible"]) for t in tallies] for job, tallies in by_job.items()},
    }
    completed = all(e.get("status") == "completed" for e in loaded)
    complete = completed and all(len(by_job[job]) == ITERATIONS and not short[job] for job in JOBS)
    if not complete:
        record["status"] = "undecided"
        record["reason"] = (
            "a job did not complete, or an iteration returned no counts or fewer than the preregistered eligible events"
        )
        return record
    retained = json.loads((FAMILY_DIR / FORECAST).read_text(encoding="utf-8"))
    prediction = retained["tomography_prediction"]
    record["status"] = "decided"
    record.update(estimates(by_job, seed_plan()["analysis"][1], prediction))
    tomography_hom = json.loads((ROOT / TOMOGRAPHY_RUNS[0] / "submission.json").read_text(encoding="utf-8"))[
        "perfs_at_plan"
    ]["HOM (%)"]
    homs = {e["job"]: (e["perfs"] or {}).get("HOM (%)") for e in loaded}
    differences = {job: None if hom is None else hom - tomography_hom for job, hom in homs.items()}
    record["hom"] = {
        "tomography_hom": tomography_hom,
        "difference_points": differences,
        "hom_moved": any(d is None or abs(d) > HOM_READING_POINTS for d in differences.values()),
    }
    return record


def build() -> int:
    for job in JOBS:
        out = FAMILY_DIR / job
        out.mkdir(parents=True, exist_ok=True)
        for name, data in documents(job).items():
            (out / name).write_bytes(data)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--build", action="store_true", help="write both jobs' cases.json and circuit.json")
    group.add_argument("--forecast", action="store_true", help="recompute and compare forecast.json")
    group.add_argument("--write-forecast", action="store_true", help="write forecast.json")
    group.add_argument("--read", action="store_true", help="retain the live platform read")
    group.add_argument("--estimate", action="store_true", help="retain Perceval's shot estimate")
    group.add_argument("--analyze", nargs="+", metavar=("OUT.json", "RUN"))
    args = parser.parse_args()
    if args.build:
        return build()
    if args.forecast:
        return check_forecast()
    if args.write_forecast:
        (FAMILY_DIR / FORECAST).write_bytes(forecast_bytes())
        return 0
    if args.read:
        return platform_read()
    if args.estimate:
        return estimate_command()
    if args.analyze:
        out, *runs = args.analyze
        require(len(runs) == len(JOBS), "--analyze takes OUT.json and the two runs")
        result = analyze([Path(run) for run in runs])
        Path(out).write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print(f"{FAMILY}: {result['status']}")
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
