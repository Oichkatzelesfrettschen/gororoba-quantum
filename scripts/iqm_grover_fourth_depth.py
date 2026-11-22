"""IQM Garnet fourth Grover depth with every depth arm at positions mirrored about the job's center.

The retained run grover-depth-sedenion-walsh (docs/design/iqm-garnet-grover-depth-sedenion-walsh.md) measured the
marked-state retention of the line-native Grover of mark 101 at depths 1, 2 and 3 as lambda = 0.831, 0.730, 0.519
and read f = lambda_3 - lambda_2^2 / lambda_1 = -0.122 against a geometric law's 0 (the model reads +0.010). Its
open hypothesis names two causes of the bend, a coherent error that accumulates with iterations and positional drift
across the job; the retained bytes exclude linear and symmetric positional drift
(docs/evidence/iqm-garnet-grover-positions on branch iqm-qb12-fault-models).

This case puts the arms of depth 1, 2, 3 and 4 at positions mirrored about the center of one job, so a drift linear
in position leaves every depth's pooled frequency unchanged, and adds the fourth depth. The ideal marked
probability is 0.781, 0.945, 0.330 and 0.012 at depths 1 to 4; the retained fits continue to depth 4 as lambda_4 =
A r^4 (geometric) or r^4 (Q_4(eps) - 1/8) / (P_4 - 1/8) (an oracle-phase error eps per iteration, gororoba_quantum/
grover_depth_families.py). The case's decisions are the bend at mirrored positions and the chi-square comparison of
the two families over four depths.

Job "grover" (three qubits, path QB20-QB16-QB17 of the retained case, as scripts/iqm_garnet_followup.py):
  m101-k{1,2,3,4}-c{n}  the line-native Grover of mark 101, COPIES[k] copies of each depth. The first half of the
                        job holds half the copies in an order chosen by arrangement(), the eight readout
                        preparations ro-xyz hold the center, and the second half repeats the first half reversed,
                        so each depth's summed position equals its copies times the job's center and the spread of
                        its squared offsets is the smallest the multiset allows.

Every prediction is the exact density matrix of iqm_grover_line.predicted's model through
iqm_garnet_followup.predicted: depolarizing PRX and CZ, idle T1 and T2 over the ASAP schedule, herald-conditioned
readout; no coherent error. The case draws no random number, so it takes no seed.

analyze RUN_DIR --out OUT.json reads one collected run of the case (gororoba_quantum/grover_depth_analysis.py): the
circuit digests and positions bound to the counts, copies dropped in mirror pairs, the copy-heterogeneity gate and
the preregistered verdict. A run on garnet:mock is refused.

Usage: "$PYTHON" scripts/iqm_grover_fourth_depth.py (build DIR (--calibration SRC | --live) | check DIR |
       analyze RUN_DIR --out OUT.json | --self-test)

build --live reads Garnet's current default calibration set into DIR/calibration (a free read) and rebuilds
the circuits, the prediction and the digest cases.json binds; a submission follows such a build, so the approved
digest names the calibration the job runs on.
"""

from __future__ import annotations

import argparse
import itertools
import json
import re
import shutil
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import iqm_garnet_followup as followup  # noqa: E402
import iqm_grover_line as grover  # noqa: E402
import iqm_sim  # noqa: E402
from iqm_jobs import CASE_SCHEMA, JOB_SECONDS, ceiling_credits, ceiling_seconds, dump  # noqa: E402
from iqm_platform import sha256  # noqa: E402
from iqm_signed_probe import CALIBRATION_FILES, OPTIONS  # noqa: E402

import grover_depth_analysis as run_analysis  # noqa: E402
import grover_depth_families as families  # noqa: E402
from parallel import ordered_map  # noqa: E402

CASE = "grover-fourth-depth-mirrored"
QCS = ["garnet:mock", "garnet"]
PRICE = grover.PRICE
PATH = followup.FORWARD_PATH
MARKED = "101"
SHOTS = 20000
# Copies per depth; each is even so that every copy has a mirror image.
COPIES = {1: 4, 2: 4, 3: 4, 4: 18}
# Depths of the first half of the job's circuits: of the 450,450 orderings of half the copies of every depth, the one
# whose depths have the most nearly equal mean squared offset from the job's center (best_first_half() recomputes it).
FIRST_HALF = (4, 4, 1, 2, 3, 4, 4, 4, 4, 3, 4, 2, 4, 1, 4)
READOUTS = 8
# Kept fraction of the retained depth arms: 13,450 of 16,000, 3,377 and 3,383 of 4,000 (0.841, 0.844, 0.846).
KEPT_PLAN = 0.84
PLANNED_KEPT_PER_COPY = SHOTS * KEPT_PLAN
# Seconds per circuit-shot of the retained Grover depth job: 1.99852 s of execution over 144,000 circuit-shots is
# 13.9 us, which carries the job's fixed 0.13 s; the depth-4 circuits add about 14 CZ (40 ns each) to the retained
# depth-3 schedule, and 14.5 us bounds the job's mean.
CIRCUIT_SHOT_SECONDS = 14.5e-6
# Billed seconds the credit ceiling carries above the expected ones (iqm_jobs.ceiling_credits adds JOB_SECONDS).
CEILING_MARGIN_SECONDS = 3
RETAINED_ANALYSIS = ROOT / "results" / "iqm" / "garnet_grover_depth_sedenion_walsh_analysis.json"


def distinct_orders(remaining: dict[int, int], prefix: tuple[int, ...] = ()) -> Iterator[tuple[int, ...]]:
    """Every distinct ordering of the multiset remaining (depth -> count), in sorted order."""
    if not any(remaining.values()):
        yield prefix
        return
    for k in sorted(remaining):
        if remaining[k]:
            yield from distinct_orders({**remaining, k: remaining[k] - 1}, (*prefix, k))


def distinct_prefixes(
    remaining: dict[int, int], length: int, prefix: tuple[int, ...] = ()
) -> Iterator[tuple[tuple[int, ...], dict[int, int]]]:
    """Every distinct first length depths of an ordering of the multiset, with the depths left, in sorted order."""
    if len(prefix) == length:
        yield prefix, remaining
        return
    for k in sorted(remaining):
        if remaining[k]:
            yield from distinct_prefixes({**remaining, k: remaining[k] - 1}, length, (*prefix, k))


def half_counts() -> dict[int, int]:
    return {k: n // 2 for k, n in COPIES.items()}


def offset_spread(order: tuple[int, ...]) -> float:
    """Largest minus smallest over the depths of the mean squared offset of their positions in order from the job's
    center, the spread of the squared offsets that mirroring leaves."""
    half = half_counts()
    center = (2 * len(order) + READOUTS - 1) / 2
    sums = dict.fromkeys(half, 0.0)
    for p, k in enumerate(order):
        sums[k] += (p - center) ** 2
    means = [sums[k] / half[k] for k in half]
    return max(means) - min(means)


def shard_best(item: tuple[tuple[int, ...], dict[int, int]]) -> tuple[float, tuple[int, ...]] | None:
    """The first ordering in sorted order of the least offset spread among the completions of one prefix."""
    prefix, remaining = item
    best: tuple[float, tuple[int, ...]] | None = None
    for order in distinct_orders(remaining, prefix):
        score = offset_spread(order)
        if best is None or score < best[0] - 1e-9:
            best = (score, order)
    return best


def best_first_half() -> tuple[int, ...]:
    """The exhaustive search that fixed FIRST_HALF: the orderings of half the copies of every depth, sharded by
    their first three depths over parallel.ordered_map; among equal spreads the first in sorted order. The case does
    not run it on a build (tests/test_iqm_grover_fourth_depth.py does)."""
    shards = ordered_map(shard_best, list(distinct_prefixes(half_counts(), 3)), min_items=1)
    best: tuple[float, tuple[int, ...]] | None = None
    for found in shards:
        if found is not None and (best is None or found[0] < best[0] - 1e-9):
            best = found
    if best is None:
        raise ValueError("no arrangement")
    return best[1]


def verify_first_half(order: tuple[int, ...]) -> None:
    """The invariants the search established for FIRST_HALF: it holds half the copies of every depth, and the
    depths' mean squared offsets from the center differ by under a quarter of the smallest."""
    if sorted(order) != sorted(k for k, n in half_counts().items() for _ in range(n)):
        raise AssertionError(f"first half {order} is not half the copies of every depth")
    center = (2 * len(order) + READOUTS - 1) / 2
    means = {k: float(np.mean([(p - center) ** 2 for p, d in enumerate(order) if d == k])) for k in COPIES}
    if offset_spread(order) >= 0.25 * min(means.values()):
        raise AssertionError(f"first half {order} leaves squared offsets {means}")


def arrangement() -> list[int]:
    """Depths of the job's circuits in order: FIRST_HALF, the readout block (depth 0), FIRST_HALF reversed, so the
    positions of every depth are mirror images about the job's center."""
    verify_first_half(FIRST_HALF)
    return [*FIRST_HALF, *([0] * READOUTS), *FIRST_HALF[::-1]]


def depth_arms() -> list[dict[str, Any]]:
    order = arrangement()
    seen = {k: 0 for k in COPIES}
    out: list[dict[str, Any]] = []
    bits = ["".join(b) for b in itertools.product("01", repeat=3)]
    readout = 0
    for k in order:
        if k == 0:
            circuit = followup.readout_circuit(bits[readout], PATH, "ro")
            out.append({"name": circuit["name"], "circuit": circuit, "marked": None, "k": None})
            readout += 1
            continue
        name = f"m{MARKED}-k{k}-c{seen[k]}"
        seen[k] += 1
        out.append({"name": name, "circuit": grover.line_arm(MARKED, k, PATH, name)[1], "marked": MARKED, "k": k})
    if seen != COPIES or readout != READOUTS:
        raise AssertionError(f"arrangement holds {seen} and {readout} readouts")
    total = len(out)
    for k in COPIES:
        at = [n for n, a in enumerate(out) if a["k"] == k]
        if sum(at) != len(at) * (total - 1) / 2 or any(out[total - 1 - n]["k"] != k for n in at):
            raise AssertionError(f"depth {k} copies are not mirrored: positions {at}")
    return out


def retained_inputs() -> dict[str, Any]:
    """The retained job's raw retention at depths 1 to 3, its kept shots and the model's retention at the retained
    calibration, read from the retained analysis and the retained case's prediction."""
    record = json.loads(RETAINED_ANALYSIS.read_text(encoding="utf-8"))
    lam = record["decisions"]["depth_law_101"]["lambda_raw"]
    arms = record["exploratory"]["grover"]["arms"]
    prediction = json.loads(
        (followup.RETAINED_CASE.parent / followup.CASE / "prediction.json").read_text(encoding="utf-8")
    )
    model = []
    for k in (1, 2, 3):
        pattern = re.compile(rf"m101-k{k}(-c\d+)?")
        marked = [a["predicted_marked"] for name, a in prediction["arms"].items() if pattern.fullmatch(name)]
        model.append(families.retention(float(np.mean(marked)), k))
    return {
        "lambda": [float(lam[str(k)]) for k in (1, 2, 3)],
        "kept": [int(arms[f"m101-k{k}"]["kept_shots"]) for k in (1, 2, 3)],
        "model": model,
        "f_raw": record["decisions"]["depth_law_101"]["f_raw"],
    }


def planned_kept() -> list[float]:
    return [COPIES[k] * PLANNED_KEPT_PER_COPY for k in families.DEPTHS]


def rounded(x: Any) -> Any:
    if isinstance(x, dict):
        return {k: rounded(v) for k, v in x.items()}
    if isinstance(x, list):
        return [rounded(v) for v in x]
    return round(x, 6) if isinstance(x, float) else x


def depth_positions(arm_records: dict[str, Any]) -> dict[int, list[int]]:
    return {
        k: sorted(a["position"] for n, a in arm_records.items() if n.startswith(f"m101-k{k}-c"))
        for k in families.DEPTHS
    }


def drift_noncentrality(
    model: list[float], positions: dict[int, list[int]], slope: float, in_retention: bool = True
) -> float:
    """Noncentrality of the heterogeneity statistic when every copy drifts linearly in position by slope per position,
    in retention (a depth's marked frequency then moves by slope times its retention scale P_k - 1/8) or, with
    in_retention false, in marked frequency at the same rate at every depth: the copies' frequencies scatter about
    their mean by that amount times their offset from the depth's mean position, and each depth adds kept shots per
    copy times the squared scatter over p (1 - p)."""
    total = 0.0
    for k, m in zip(families.DEPTHS, model, strict=True):
        p = families.probability_of(m, k)
        x = np.asarray(positions[k], dtype=float)
        shift = slope * (families.retention_scale(k) if in_retention else 1.0) * (x - x.mean())
        total += float(np.sum(shift**2)) * PLANNED_KEPT_PER_COPY / (p * (1 - p))
    return total


def heterogeneity_gate(arm_records: dict[str, Any], model: list[float]) -> dict[str, Any]:
    """The copy-heterogeneity gate fixed in prediction.json: the mirror-pair floor, the chi-square quantile for every
    degree of freedom the surviving copies can leave, and what the gate costs the design (its false-alarm
    probability, the linear retention drift that trips it half and nine tenths of the time, its probability at the
    retained drift, and the sizing after pairs leave)."""
    from scipy import stats

    positions = depth_positions(arm_records)
    dof = sum(len(x) - 1 for x in positions.values())
    threshold = families.heterogeneity_threshold(dof)

    def fires(slope: float, in_retention: bool = True) -> float:
        noncentrality = drift_noncentrality(model, positions, slope, in_retention)
        return float(stats.ncx2.sf(threshold, dof, noncentrality))

    def slope_at(power: float, in_retention: bool = True) -> float:
        low, high = 0.0, 0.05
        for _ in range(100):
            mid = (low + high) / 2
            low, high = (mid, high) if fires(mid, in_retention) < power else (low, mid)
        return high

    # The retained job's k = 1 copies, positions 0, 13, 22 and 35, gave a raw marked-frequency slope of -0.000303
    # +- 0.000317 per position (docs/evidence/iqm-garnet-grover-positions on branch iqm-qb12-fault-models), which is
    # slope / (P_1 - 1/8) in retention.
    retained_frequency_slope = 0.000303
    retained_slope = retained_frequency_slope / families.retention_scale(1)
    return {
        "statistic": (
            "sum over depths of the chi-square of the surviving copies' marked counts about the depth's pooled "
            "marked frequency, sum (m - n p)^2 / (n p (1 - p)), with copies - 1 degrees of freedom per depth"
        ),
        "alpha": families.HETEROGENEITY_ALPHA,
        "copy_floor": families.COPY_FLOOR,
        "planned_kept_per_copy": PLANNED_KEPT_PER_COPY,
        "planned_dof": dof,
        "planned_threshold": threshold,
        "threshold_by_dof": {str(d): families.heterogeneity_threshold(d) for d in range(1, dof + 1)},
        "power": {
            "false_not_evaluated_probability": families.HETEROGENEITY_ALPHA,
            "linear_drift_of_retention_per_position_at_half_power": slope_at(0.5),
            "linear_drift_of_retention_per_position_at_nine_tenths_power": slope_at(0.9),
            "retained_slope_of_retention_per_position": retained_slope,
            "probability_at_the_retained_slope": fires(retained_slope),
            "probability_at_half_the_retained_slope": fires(retained_slope / 2),
            # The retained evidence is one raw marked-frequency slope on depth-1 copies, so it does not choose
            # between a drift that follows each depth's retention span (above) and one of equal marked-frequency
            # size at every depth (below), which the depth-4 copies, at frequency 0.06, feel most.
            "equal_frequency_drift_of_marked_frequency_per_position_at_half_power": slope_at(0.5, False),
            "equal_frequency_drift_of_marked_frequency_per_position_at_nine_tenths_power": slope_at(0.9, False),
            "retained_slope_of_marked_frequency_per_position": retained_frequency_slope,
            "probability_at_the_retained_slope_in_marked_frequency": fires(retained_frequency_slope, False),
            "probability_at_half_the_retained_slope_in_marked_frequency": fires(retained_frequency_slope / 2, False),
        },
    }


def pair_loss_sizing(cont: dict[str, Any], model: list[float]) -> dict[str, Any]:
    """The sizing numbers when mirror pairs leave: the depth-4 separation z with 0 to 3 of its 9 pairs gone, and
    the bend's standard error with one pair gone from each of depths 1 to 3."""
    pair = 2 * PLANNED_KEPT_PER_COPY
    out: dict[str, Any] = {}
    for lost in range(4):
        kept = planned_kept()
        kept[3] -= lost * pair
        out[f"depth_4_pairs_lost_{lost}"] = families.separation(cont["geometric"], cont["coherent"], kept, model)[
            "last_depth_z"
        ]
    full = planned_kept()
    out["bend_se_all_copies"] = families.bend(model, full)[1]
    out["bend_se_one_pair_lost_from_each_of_depths_1_to_3"] = families.bend(
        model, [full[0] - pair, full[1] - pair, full[2] - pair, full[3]]
    )[1]
    return out


def decisions(arm_records: dict[str, Any]) -> dict[str, Any]:
    retained = retained_inputs()
    cont = families.continuations(retained["lambda"], retained["kept"], retained["model"])
    kept = planned_kept()
    model = families.model_retention(arm_records)
    # The retained ratios continued to depth 4 and scaled by this calibration's model retention are the two
    # continuations of lambda_4; the data the rule would see if one family held exactly sit at those values.
    sep = families.separation(cont["geometric"], cont["coherent"], kept, model)
    model_f, model_f_se = families.bend(model, kept)
    model_counts = [
        round(families.probability_of(m, k) * n) for m, k, n in zip(model, families.DEPTHS, kept, strict=True)
    ]
    model_reading = families.verdict(model_counts, [round(n) for n in kept], model, cont)
    gate = heterogeneity_gate(arm_records, model)
    return rounded(
        {
            "z_resolve": families.Z_RESOLVE,
            "planned_kept_shots": {str(k): n for k, n in zip(families.DEPTHS, kept, strict=True)},
            "retained": {
                "source": RETAINED_ANALYSIS.relative_to(ROOT).as_posix(),
                "lambda_raw": dict(zip(("1", "2", "3"), retained["lambda"], strict=True)),
                "kept_shots": dict(zip(("1", "2", "3"), retained["kept"], strict=True)),
                "model_lambda": dict(zip(("1", "2", "3"), retained["model"], strict=True)),
                "rho": dict(zip(("1", "2", "3"), cont["rho"], strict=True)),
                "f_raw": retained["f_raw"],
                "geometric_fit": cont["geometric"],
                "coherent_fit": cont["coherent"],
                "geometric_rho_4": cont["geometric_next"],
                "coherent_rho_4": cont["coherent_next"],
            },
            "continuation": {
                "model_lambda_4": model[3],
                "geometric_lambda_4": cont["geometric_next"] * model[3],
                "coherent_lambda_4": cont["coherent_next"] * model[3],
                "lambda_4_difference": sep["last_depth_difference"] * model[3],
                "se_rho_4_at_planned_shots": sep["last_depth_difference"] / sep["last_depth_z"],
                "z": sep["last_depth_z"],
                "chi2_geometric_fit_to_coherent_values": sep["chi2_geometric_on_coherent_data"],
                "chi2_coherent_fit_to_geometric_values": sep["chi2_coherent_on_geometric_data"],
                "delta_resolve": families.DELTA_RESOLVE,
                "rule": (
                    "the retained ratios rho = lambda / model lambda at depths 1 to 3 fitted by each family and "
                    "continued to depth 4, scaled by this calibration's model lambda_4; z is their difference over "
                    "the binomial standard error of rho_4 from the planned kept shots, the larger of the two; each "
                    "chi-square is what the other family leaves when the four depths equal one family's values at "
                    "the planned shots, to be compared with delta_resolve"
                ),
            },
            "heterogeneity": gate,
            "mirror_pair_loss": pair_loss_sizing(cont, model),
            "model": {
                "lambda": dict(zip(("1", "2", "3", "4"), model, strict=True)),
                "f": model_f,
                "f_se_at_planned_shots": model_f_se,
                "verdict_on_the_model_at_planned_shots": model_reading,
            },
            "rule": {
                "bend": (
                    "f = lambda_3 - lambda_2^2 / lambda_1 from raw pooled marked frequencies of the depth arms "
                    "(copies pooled after the mirror-pair and heterogeneity gates below, binomial variances at the "
                    "observed frequencies, delta method over the three arms), z = (f - model.f) / SE; z <= -3 "
                    "reads 'the retention law bends beyond the model at mirrored positions', which excludes positional "
                    "drift linear in position as the cause of the retained bend; z >= 3 reads 'bends upward of the "
                    "model'; otherwise 'no bend beyond the model resolved at mirrored positions'"
                ),
                "family": (
                    "weighted least squares of the geometric family a s^k and the coherent family s^k (Q_k(eps) - "
                    "1/8) / (P_k - 1/8) to rho_k = lambda_k / model.lambda_k at k = 1 to 4 "
                    "(gororoba_quantum/grover_depth_families.py), binomial standard errors at the observed "
                    "frequencies, over the rate domains geometric s in [0.30, 1.20] and coherent s in [0.50, 1.10] "
                    "(eps ranges over a full period, the amplitude a is free); with chi2 of each fit (two degrees of "
                    "freedom): 'out of domain' when either fit's rate sits on its bound, the bound rather than the "
                    "data having ended its search; else 'neither family fits' when both "
                    "exceed their 0.99 chi2 quantile (9.21 at four usable depths, 6.63 at three); else 'coherent' when "
                    "chi2_geometric - chi2_coherent >= 9, 'geometric' when it is <= -9, else 'unresolved'; gating: "
                    "a copy below half its planned kept shots leaves its depth together with the copy at its mirrored "
                    "position, a depth without kept shots is unusable, the bend needs depths 1 to 3, the family "
                    "comparison any three depths, and a decision whose depths are unusable reads 'not evaluated' "
                    "without blocking the other"
                ),
                "heterogeneity": (
                    "after the mirror-pair gate, the chi-square of the surviving copies of each depth about that "
                    "depth's pooled marked frequency, summed over depths, is compared with the 1 - alpha chi-square "
                    "quantile at its degrees of freedom (decisions.heterogeneity.threshold_by_dof); above it the "
                    "bend and family decisions both read 'not evaluated', since a depth's pooled frequency no longer "
                    "describes copies that differ beyond binomial scatter"
                ),
                "beside": (
                    "rho_4 against the retained fits' continuations in standard errors, and whether the "
                    "retention decreases with depth; neither decides"
                ),
                "function": "grover_depth_families.read_copies",
                "analyzer": "grover_depth_analysis.analyze",
            },
        }
    )


def build_from(calibration_dir: Path) -> tuple[dict[str, str], dict[str, Any]]:
    calibration = iqm_sim.Calibration.from_directory(calibration_dir)
    retained_case = json.loads((followup.RETAINED_CASE / "prediction.json").read_text(encoding="utf-8"))
    if retained_case["path"] != PATH:
        raise ValueError(f"the retained case ran on {retained_case['path']}, not {PATH}")
    arms = depth_arms()
    files = {f"circuits/{a['name']}.json": dump(a["circuit"]) for a in arms}
    names = [a["name"] for a in arms]
    distributions = ordered_map(
        followup.predicted, [(files[f"circuits/{n}.json"], str(calibration_dir)) for n in names], min_items=1
    )
    predictions = dict(zip(names, distributions, strict=True))
    arm_records: dict[str, Any] = {}
    for position, arm in enumerate(arms):
        c = arm["circuit"]
        record: dict[str, Any] = {
            "job": "grover",
            "position": position,
            "locus": c["instructions"][-1]["locus"],
            "cz": followup.count(c, "cz"),
            "prx": followup.count(c, "prx"),
            "predicted": predictions[arm["name"]],
        }
        if arm["marked"] is not None:
            record |= {
                "marked": arm["marked"],
                "iterations": arm["k"],
                "ideal_marked": families.ideal_marked(arm["k"]),
                "predicted_marked": predictions[arm["name"]][arm["marked"]],
            }
        arm_records[arm["name"]] = record
    expected = round(len(arms) * SHOTS * CIRCUIT_SHOT_SECONDS, 3)
    ceiling = {qc: ceiling_credits(expected, PRICE[qc], JOB_SECONDS) for qc in QCS}
    max_credits = {
        qc: (ceiling_seconds(ceiling[qc], PRICE[qc]) + CEILING_MARGIN_SECONDS) * PRICE[qc] if PRICE[qc] else 0.0
        for qc in QCS
    }
    job = {
        "job": "grover",
        "circuits": [
            {"file": f"circuits/{a['name']}.json", "sha256": sha256(files[f"circuits/{a['name']}.json"].encode())}
            for a in arms
        ],
        "shots": SHOTS,
        "options": {**OPTIONS, "calibration_set_id": {"garnet": calibration.set_id}},
        "expected_seconds": expected,
        "max_credits": max_credits,
    }
    prediction = {
        "calibration_set": calibration.set_id,
        "forward_path": PATH,
        "copies": {str(k): n for k, n in COPIES.items()},
        "arms": arm_records,
        "decisions": decisions(arm_records),
        "model": (
            "exact density matrix: iqm_sim depolarizing PRX and CZ, ASAP idle T1/T2, herald-conditioned readout "
            "assignment; no coherent error, leakage or crosstalk"
        ),
    }
    files["prediction.json"] = dump(prediction)
    files["cases.json"] = dump(
        {
            "schema": CASE_SCHEMA,
            "case": CASE,
            # The approval quotes this file's digest, so the prediction the verdict decides against is bound.
            "prediction_sha256": sha256(files["prediction.json"].encode()),
            "question": (
                "With the line-native Grover of mark 101 at depths 1 to 4 placed at positions mirrored about the "
                "job's center on one Garnet calibration, does the retention law still bend at depth 3, and do the "
                "four retentions follow a geometric law or an oracle-phase coherent error that accumulates with "
                "iterations?"
            ),
            "qcs": QCS,
            "jobs": [job],
        }
    )
    return files, prediction


def fetch_live(calibration_dir: Path) -> None:
    """Garnet's current default calibration set, a free read-only call (IQM_TOKENS_FILE), into calibration_dir."""
    from iqm_cancellation_probe import fetch_calibration

    fetch_calibration(calibration_dir)


def write(directory: Path, source: Path | None, live: bool = False) -> None:
    """Build the case from a calibration directory, or with live from the set Garnet serves now; a rebuild drops
    the circuits the new build does not emit."""
    if live == (source is not None):
        raise ValueError("build takes exactly one of --calibration and --live")
    calibration_dir = directory / "calibration"
    calibration_dir.mkdir(parents=True, exist_ok=True)
    if live:
        fetch_live(calibration_dir)
    elif source is not None:
        for name in CALIBRATION_FILES:
            shutil.copyfile(source / name, calibration_dir / name)
    files, prediction = build_from(calibration_dir)
    for stale in (directory / "circuits").glob("*.json"):
        if stale.relative_to(directory).as_posix() not in files:
            stale.unlink()
    for rel, text in files.items():
        path = directory / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    print(json.dumps(prediction["decisions"], indent=1))


def check(directory: Path) -> None:
    files, _ = build_from(directory / "calibration")
    present = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}
    expected = set(files) | {f"calibration/{name}" for name in CALIBRATION_FILES}
    if present != expected:
        raise ValueError(f"{directory}: files differ from the build: {sorted(present ^ expected)}")
    for rel, text in files.items():
        if (directory / rel).read_text(encoding="utf-8") != text:
            raise ValueError(f"{directory}/{rel} differs from the build")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def counts_of(lam: list[float], kept: list[int]) -> list[int]:
    return [round(families.probability_of(x, k) * n) for x, k, n in zip(lam, families.DEPTHS, kept, strict=True)]


def analyze(run_dir: Path, case_dir: Path | None = None) -> dict[str, Any]:
    """The record of one collected run: circuit digests and positions bound to the counts, mirror-pair gating, the
    copy-heterogeneity gate and the verdict (gororoba_quantum/grover_depth_analysis.py)."""
    return run_analysis.analyze(run_dir, run_analysis.CASE_DIR if case_dir is None else case_dir)


def layout_copies(
    lam: list[float], kept: int = int(PLANNED_KEPT_PER_COPY), tweak: Any = None
) -> dict[int, list[families.Copy]]:
    """The copies of the arrangement at the planned kept shots, each marked count the model value of lam at its depth;
    tweak(depth, position, marked, kept) may return another (marked, kept)."""
    order = arrangement()
    out: dict[int, list[families.Copy]] = {k: [] for k in COPIES}
    for position, k in enumerate(order):
        if k:
            marked = round(families.probability_of(lam[k - 1], k) * kept)
            m, n = tweak(k, position, marked, kept) if tweak else (marked, kept)
            out[k].append((position, m, n))
    return out


def self_test() -> str:
    """Circuits against their exact ideal, the arrangement's mirror invariants, the families, and the verdict on
    planted data."""
    arms = depth_arms()
    path = ["QA", "QB", "QC"]
    for arm in arms:
        if arm["k"] is None:
            continue
        circuit = grover.line_arm(MARKED, arm["k"], path, "t")[1]
        p = followup.ideal(circuit, path)[int(MARKED[::-1], 2)]
        require(abs(p - families.ideal_marked(arm["k"])) < 1e-9, f"depth {arm['k']}: P(marked) {p}")
        require(followup.count(circuit, "cz") == 14 * arm["k"], f"depth {arm['k']}: CZ count")
    require(len(arms) == sum(COPIES.values()) + READOUTS and len(arms) <= 100, "circuits per job")
    require(len(arms) * SHOTS <= 2_000_000 and SHOTS <= 20_000, "Garnet job limits")
    total = len(arms)
    center = (total - 1) / 2
    means = {k: float(np.mean([(n - center) ** 2 for n, a in enumerate(arms) if a["k"] == k])) for k in COPIES}
    require(max(means.values()) - min(means.values()) < 0.25 * min(means.values()), f"squared offsets {means}")
    require(
        all(arms[n]["name"][:7] == arms[total - 1 - n]["name"][:7] for n in range(total) if arms[n]["k"]),
        "mirror images carry the same depth",
    )
    # eps = 0 is the ideal rotation; the families agree with the exact two-dimensional recursion.
    zero = np.zeros(1)
    for k in families.DEPTHS:
        require(abs(float(families.oracle_phase_probability(k, zero)[0]) - families.ideal_marked(k)) < 1e-12, "eps 0")
    # Planted recovery: noise-free values of each family return their own parameters with chi2 near zero.
    kept = [int(n) for n in planned_kept()]
    model = [0.85, 0.77, 0.70, 0.58]
    # The retained ratios' two fits (decisions.retained of the case's prediction).
    geo_truth = {"A": 1.025983, "r": 0.963383}
    coh_truth = {"eps": 0.304302, "r": 1.013413}
    geo_rho = families.geometric_values(geo_truth, families.DEPTHS)
    coh_rho = families.coherent_values(coh_truth, families.DEPTHS)
    cont = {"geometric_next": geo_rho[3], "coherent_next": coh_rho[3]}
    for rho, want in ((geo_rho, "geometric"), (coh_rho, "coherent")):
        lam = [r * m for r, m in zip(rho, model, strict=True)]
        read = families.verdict(counts_of(lam, kept), kept, model, cont)
        require(read["family"] == want, f"planted {want}: {read['family']} (delta {read['delta_chi2']})")
    flat = families.verdict(counts_of(model, kept), kept, model, cont)
    require(flat["family"] == "unresolved", f"the model's own retention reads {flat['family']}")
    require(
        flat["bend"]["reading"] == "no bend beyond the model resolved at mirrored positions", f"flat {flat['bend']}"
    )
    # Planted bend: lambda_3 well below the model's reads as a bend beyond the model, and no family fits it.
    bent = [0.85, 0.77, 0.55, 0.58]
    read = families.verdict(counts_of(bent, kept), kept, model, cont)
    require(
        read["bend"]["reading"] == "the retention law bends beyond the model at mirrored positions",
        f"bend {read['bend']}",
    )
    require(read["family"] == "neither family fits", f"bent data: {read['family']}")
    gated = families.verdict([*counts_of(model, kept)[:3], 0], [*kept[:3], 0], model, cont)
    require(gated["usable_depths"] == [1, 2, 3] and gated["family"] == "unresolved", f"one unusable depth: {gated}")
    require("z_against_model" in gated["bend"], "the bend needs depths 1 to 3 only")
    for bad in ([1, 2, 3], [-1, 0, 0, 0]):
        try:
            families.verdict(bad, [10, 10, 10, 10][: len(bad)], [0.5] * 4, {})
        except ValueError:
            continue
        raise AssertionError(f"verdict accepted counts {bad}")
    # Parameter domains: data of each family one step outside its rate bound read "out of domain", one inside read the
    # family; the retained geometric amplitude would push the outside values past probability 1.
    planted = (
        ("geometric", families.geometric_values, {"A": 0.5, "r": 1.19}, "geometric"),
        ("geometric", families.geometric_values, {"A": 0.5, "r": 1.25}, "out of domain"),
        ("coherent", families.coherent_values, {"eps": 0.3, "r": 1.09}, "coherent"),
        ("coherent", families.coherent_values, {"eps": 0.3, "r": 1.11}, "out of domain"),
    )
    for family, values, parameters, want in planted:
        domain_lam = [r * m for r, m in zip(values(parameters, families.DEPTHS), model, strict=True)]
        domain_read = families.verdict(counts_of(domain_lam, kept), kept, model, cont)
        require(domain_read["family"].startswith(want), f"planted {family} {parameters}: {domain_read['family']}")
    # Mirror pairs and the heterogeneity gate on the arrangement's copies.
    gate = {
        "copy_floor": families.COPY_FLOOR,
        "threshold_by_dof": {str(d): families.heterogeneity_threshold(d) for d in range(1, 27)},
    }
    per_copy = PLANNED_KEPT_PER_COPY
    clean = families.read_copies(layout_copies(model), total, per_copy, model, cont, gate)
    require(clean["heterogeneity"]["passed"] and clean["family"] == "unresolved", f"clean copies read {clean}")
    raised = layout_copies(model, tweak=lambda k, p, m, n: (m + round(0.04 * n), n) if (k, p) == (1, 2) else (m, n))
    raised_read = families.read_copies(raised, total, per_copy, model, cont, gate)
    require(
        raised_read["bend"]["reading"].startswith("not evaluated")
        and raised_read["family"].startswith("not evaluated"),
        f"one copy of depth 1 raised by 0.04 reads {raised_read['bend']} and {raised_read['family']}",
    )
    short = layout_copies(model, tweak=lambda k, p, m, n: (m // 20, n // 20) if (k, p) == (1, 2) else (m, n))
    kept_pairs = families.read_copies(short, total, per_copy, model, cont, gate)
    require(kept_pairs["dropped_pairs"] == {"1": [[2, 35]]}, f"a short copy leaves with its image: {kept_pairs}")
    require(kept_pairs["usable_depths"] == [1, 2, 3, 4], "the other pair of depth 1 stays")
    try:
        families.read_copies({**layout_copies(model), 1: [(2, 100, 200)]}, total, per_copy, model, cont, gate)
    except ValueError:
        pass
    else:
        raise AssertionError("an unpaired copy was accepted")
    # Billing arithmetic: the job's ceiling lies below max_credits, whose cancel threshold exceeds the expected run.
    expected = round(total * SHOTS * CIRCUIT_SHOT_SECONDS, 3)
    garnet_max = (
        ceiling_seconds(ceiling_credits(expected, PRICE["garnet"], JOB_SECONDS), PRICE["garnet"])
        + CEILING_MARGIN_SECONDS
    ) * PRICE["garnet"]
    require(ceiling_credits(expected, PRICE["garnet"], JOB_SECONDS) < garnet_max, "ceiling below max_credits")
    return (
        "self-test passed: 3 depth circuits against ideal, mirror invariants, families, 5 planted verdicts, "
        "2 refusals, 4 domain plants, 3 copy gates"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")
    b = sub.add_parser("build")
    b.add_argument("directory", type=Path)
    b.add_argument("--calibration", type=Path)
    b.add_argument("--live", action="store_true", help="read Garnet's current calibration (network, read-only)")
    sub.add_parser("check").add_argument("directory", type=Path)
    a = sub.add_parser("analyze")
    a.add_argument("run_dir", type=Path)
    a.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
    elif args.command == "build":
        write(args.directory, args.calibration, args.live)
    elif args.command == "check":
        check(args.directory)
    elif args.command == "analyze":
        run_analysis.write_record(analyze(args.run_dir), args.out)
    else:
        parser.error("choose build, check, analyze or --self-test")
    return 0


if __name__ == "__main__":
    sys.exit(main())
