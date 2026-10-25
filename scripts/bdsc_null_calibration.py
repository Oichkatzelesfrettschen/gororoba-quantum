"""Null calibration of the preregistered tests of scripts/bdsc_diagnostic.py, batched across replicates.

A null replicate draws every instance's selected count from Binomial(TRIALS, NULL_FRACTIONS[label]) with
eligible = TRIALS, equal physical_perf for f and g, and one returned circuit per (template, seed slot, state) in both
blocks. Under it no seed, template or block effect exists, and the sum-rule residuals have mean zero because
p(+) + p(-) = p(f) + p(g) for the fractions chosen. Each test of bdsc_diagnostic.analyse reads resolved when its
p-value falls below ALPHA, so a calibrated test resolves in ALPHA of the replicates.

batch_statistics evaluates every statistic of analyse that a branch or the readout reads (the nine tests, the three
class calibration shifts and the count of residuals beyond MARGIN) for a block of replicates with numpy, and returns
the bits of the scalar analyse (docs/runbooks/vectorized-fits.md):

- builtin sum() over floats is Neumaier-compensated, so fsum_rows repeats its update term by term; the running totals
  that analyse builds with += stay plain additions;
- Python's x ** 2 calls libm pow, and math.hypot is CPython's own algorithm, so every replicate-dependent square and
  hypotenuse maps through the math module;
- numpy + - * / sqrt and comparisons are IEEE binary64 operations and keep the scalar association of products;
- np.mean over the four slot differences of a template effect is numpy's reduction, repeated with np.mean along the
  last axis of a C-contiguous array;
- the weighted least-squares terms of seed_split run bdsc_diagnostic.seed_split on each replicate's floats, because
  LAPACK dgelsd, the BLAS matrix product and numpy's pairwise sum fix bits that no reformulation reproduces.

Every replicate's inputs come from one generator, drawn in a single call before blocks are cut and mapped through
parallel.ordered_map, so serial, pooled and differently blocked runs write the same bytes.

Usage:
  "$PYTHON" scripts/bdsc_null_calibration.py --null-calibration REPLICATES [--null-seed SEED] [--out FILE] [--bound]
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import bdsc_certificate as cert  # noqa: E402
import bdsc_diagnostic as diag  # noqa: E402
from qi_readout_ringdown_cases import fsum_rows, libm_map  # noqa: E402

import parallel  # noqa: E402
import qrng_seeds  # noqa: E402

Floats = npt.NDArray[np.float64]

# docs/evidence/anu_qrng/draw-2026-10-25T015224Z.json, index 0.
NULL_SEED = 28807
SCHEMA = "bdsc-diagnostic-null-calibration-v1"
# Selected fraction of each state: f and g sum to the two superpositions of a pair, so every sum-rule residual
# has mean zero.
NULL_FRACTIONS = {"f": 0.003, "g": 0.986, **{label: 0.4945 for label in diag.SUPERPOSITIONS}}
NULL_REPLICATES = 3000
# Replicates per mapped block.
NULL_BLOCK = 250
# The false-resolution rate of a calibrated test lies within BOUND_SIGMAS binomial errors of ALPHA.
BOUND_SIGMAS = 3.0


def pair_map(function: Callable[[float, float], float], first: Floats, second: Floats) -> Floats:
    """function(a, b) for every pair through the math module, the libm and CPython calls of the scalar code."""
    mapped = map(function, first.tolist(), second.tolist(), strict=True)
    return np.fromiter(mapped, np.float64, len(first))


def square(values: Floats) -> Floats:
    """x ** 2 as Python evaluates it for a float."""
    return libm_map(math.pow, values, 2.0)


def probabilities() -> Floats:
    """The selected fraction of every instance in canonical order."""
    return np.array([NULL_FRACTIONS[item["label"]] for item in diag.instances()])


def draw_counts(replicates: int, seed: int) -> npt.NDArray[np.int64]:
    """Selected counts of every replicate and instance (replicates x 96), drawn in one call from one generator."""
    rng = np.random.default_rng(seed)
    return rng.binomial(diag.TRIALS, probabilities(), size=(replicates, len(diag.instances())))


def dispersion_batch(groups: list[list[tuple[Floats, Floats]]]) -> tuple[Floats, int]:
    """diag.dispersion for every replicate: the pooled chi-square of each group about its inverse-variance mean."""
    statistic = np.zeros(len(groups[0][0][0]))
    df = 0
    for group in groups:
        weights = [1 / square(s) for _, s in group]
        mean = fsum_rows([w * v for w, (v, _) in zip(weights, group, strict=True)]) / fsum_rows(weights)
        statistic = statistic + fsum_rows([w * square(v - mean) for w, (v, _) in zip(weights, group, strict=True)])
        df += len(group) - 1
    return statistic, df


def split_batch(
    groups: list[dict[tuple[str, int], tuple[Floats, Floats]]],
) -> tuple[Floats, int, Floats, int]:
    """diag.seed_split for every replicate, through the scalar function on each replicate's floats."""
    replicates = len(next(iter(groups[0].values()))[0])
    cells = [{cell: (v.tolist(), s.tolist()) for cell, (v, s) in group.items()} for group in groups]
    common, interaction = np.zeros(replicates), np.zeros(replicates)
    common_df = interaction_df = 0
    for n in range(replicates):
        one = [{cell: (v[n], s[n]) for cell, (v, s) in group.items()} for group in cells]
        common[n], common_df, interaction[n], interaction_df = diag.seed_split(one)
    return common, common_df, interaction, interaction_df


def batch_statistics(selected: npt.NDArray[np.int64]) -> dict[str, npt.NDArray[Any]]:
    """The statistics of diag.analyse for every row of selected (replicates x 96), with the scalar bits.

    Keys are "tests.NAME.statistic", "tests.NAME.p_value", "calibration_shift.CLASS.mean|se|z|p_value" and
    "residuals_beyond_margin". The degrees of freedom do not vary by replicate and come from batch_degrees.
    """
    from scipy.stats import chi2, norm

    items = diag.instances()
    key = {(i["block"], i["template"], i["slot"], i["label"]): i["index"] for i in items}
    templates = cert.PREPARATION_DESCRIPTIONS
    out: dict[str, npt.NDArray[Any]] = {}
    with np.errstate(all="raise"):
        fraction = selected / float(diag.TRIALS)
        p_cols = {k: np.ascontiguousarray(fraction[:, index]) for k, index in key.items()}
        se_cols = {k: np.sqrt(np.maximum(p * (1 - p), 0.25 / diag.TRIALS) / diag.TRIALS) for k, p in p_cols.items()}
        se_squared = {k: square(se) for k, se in se_cols.items()}

        residuals: list[tuple[int, str, str, Floats, Floats]] = []
        for b in diag.BLOCKS:
            for t in templates:
                for s in range(diag.SLOTS):
                    for family, (plus, minus) in (("delta_R", ("+", "-")), ("delta_I", ("+i", "-i"))):
                        value = p_cols[b, t, s, plus] + p_cols[b, t, s, minus] - p_cols[b, t, s, "f"]
                        value = value - p_cols[b, t, s, "g"]
                        ref = np.sqrt(fsum_rows([se_squared[b, t, s, x] for x in (plus, minus, "f", "g")]))
                        residuals.append((b, t, family, value, ref))

        changes = [
            (
                label,
                p_cols[2, t, s, label] - p_cols[1, t, s, label],
                pair_map(math.hypot, se_cols[1, t, s, label], se_cols[2, t, s, label]),
            )
            for t in templates
            for s in range(diag.SLOTS)
            for label in diag.LABELS
        ]
        heterogeneity = np.zeros(len(selected))
        for name in diag.CLASSES:
            members = [(change, se) for label, change, se in changes if diag.class_of(label) == name]
            weights = [1 / square(se) for _, se in members]
            total = fsum_rows(weights)
            mean = fsum_rows([w * change for w, (change, _) in zip(weights, members, strict=True)]) / total
            mean_se = 1 / np.sqrt(total)
            z = mean / mean_se
            p_shift = 2 * norm.sf(np.abs(z))
            for field, array in (("mean", mean), ("se", mean_se), ("z", z), ("p_value", p_shift)):
                out[f"calibration_shift.{name}.{field}"] = array
            heterogeneity = heterogeneity + fsum_rows(
                [w * square(change - mean) for w, (change, _) in zip(weights, members, strict=True)]
            )
        statistics = {"block_change": heterogeneity}

        for name, labels in (("seed_basis", diag.BASIS), ("seed_superposition", diag.SUPERPOSITIONS)):
            statistics[name] = dispersion_batch(
                [
                    [(p_cols[b, t, s, label], se_cols[b, t, s, label]) for s in range(diag.SLOTS)]
                    for b in diag.BLOCKS
                    for t in templates
                    for label in labels
                ]
            )[0]
        statistics["residual_seed"] = dispersion_batch(
            [
                [(value, ref) for rb, rt, rf, value, ref in residuals if (rb, rt, rf) == (b, t, family)]
                for b in diag.BLOCKS
                for t in templates
                for family in ("delta_R", "delta_I")
            ]
        )[0]
        split_groups = [
            {
                (label, s): (p_cols[b, t, s, label], se_cols[b, t, s, label])
                for label in diag.SUPERPOSITIONS
                for s in range(diag.SLOTS)
            }
            for b in diag.BLOCKS
            for t in templates
        ]
        statistics["seed_common"], _, statistics["seed_interaction"], _ = split_batch(split_groups)
        job_of = {(i["block"], i["template"], i["slot"]): i["job"] for i in items}
        within_groups = [
            {
                (label, s): (p_cols[b, t, s, label], se_cols[b, t, s, label])
                for label in diag.SUPERPOSITIONS
                for s in slots
            }
            for b in diag.BLOCKS
            for t in templates
            for job in sorted({job_of[b, t, s] for s in range(diag.SLOTS)})
            if len(slots := [s for s in range(diag.SLOTS) if job_of[b, t, s] == job]) > 1
        ]
        statistics["seed_common_within_job"], _, statistics["seed_interaction_within_job"], _ = split_batch(
            within_groups
        )

        effect_terms = []
        for b in diag.BLOCKS:
            for label in diag.LABELS:
                differences = np.ascontiguousarray(
                    np.stack(
                        [
                            p_cols[b, templates[0], s, label] - p_cols[b, templates[1], s, label]
                            for s in range(diag.SLOTS)
                        ],
                        axis=1,
                    )
                )
                effect = np.mean(differences, axis=1)
                ref = (
                    np.sqrt(fsum_rows([se_squared[b, t, s, label] for t in templates for s in range(diag.SLOTS)]))
                    / diag.SLOTS
                )
                effect_terms.append(square(effect / ref))
        statistics["template"] = fsum_rows(effect_terms)

        degrees = batch_degrees()
        for name, statistic in statistics.items():
            out[f"tests.{name}.statistic"] = statistic
            out[f"tests.{name}.p_value"] = chi2.sf(statistic, degrees[name])
        z_bound = float(norm.isf(diag.ALPHA / (2 * len(residuals))))
        beyond = [(np.abs(value) - z_bound * ref) > diag.MARGIN for _, _, _, value, ref in residuals]
        out["residuals_beyond_margin"] = np.sum(beyond, axis=0)
    return out


def batch_degrees() -> dict[str, int]:
    """The degrees of freedom of every test, which the design fixes: all 48 block changes repeat their circuit."""
    items = diag.instances()
    templates = cert.PREPARATION_DESCRIPTIONS
    slots = range(diag.SLOTS)
    class_sizes = [len(templates) * diag.SLOTS * len(labels) for labels in diag.CLASSES.values()]
    job_of = {(i["block"], i["template"], i["slot"]): i["job"] for i in items}
    per_job = [
        sum(1 for s in slots if job_of[b, t, s] == job)
        for b in diag.BLOCKS
        for t in templates
        for job in sorted({job_of[b, t, s] for s in slots})
    ]
    shared = [n for n in per_job if n > 1]
    cells = len(diag.SUPERPOSITIONS)
    return {
        "block_change": sum(size - 1 for size in class_sizes),
        "seed_basis": len(diag.BLOCKS) * len(templates) * len(diag.BASIS) * (diag.SLOTS - 1),
        "seed_superposition": len(diag.BLOCKS) * len(templates) * cells * (diag.SLOTS - 1),
        "residual_seed": len(diag.BLOCKS) * len(templates) * 2 * (diag.SLOTS - 1),
        "seed_common": len(diag.BLOCKS) * len(templates) * (diag.SLOTS - 1),
        "seed_interaction": len(diag.BLOCKS) * len(templates) * (cells - 1) * (diag.SLOTS - 1),
        "seed_common_within_job": sum(n - 1 for n in shared),
        "seed_interaction_within_job": sum((cells - 1) * (n - 1) for n in shared),
        "template": len(diag.BLOCKS) * len(diag.LABELS),
    }


def scalar_observed(row: npt.NDArray[np.int64]) -> dict[int, dict[str, Any]]:
    """The observed mapping of diag.analyse for one replicate's selected counts."""
    observed: dict[int, dict[str, Any]] = {}
    positions: dict[str, int] = {}
    for item in diag.instances():
        position = positions.get(item["job"], 0)
        positions[item["job"]] = position + 1
        observed[item["index"]] = {
            "selected": int(row[item["index"]]),
            "eligible": diag.TRIALS,
            "circuit_sha256": f"{item['template']}-{item['slot']}-{item['label']}",
            "perf": 0.078,
            "outside_share": 0.0,
            "position": position,
        }
    return observed


def scalar_statistics(row: npt.NDArray[np.int64]) -> dict[str, float]:
    """The same keys as batch_statistics from the scalar diag.analyse of one replicate."""
    read = diag.analyse(scalar_observed(row))
    out: dict[str, float] = {}
    for name, test in read["tests"].items():
        out[f"tests.{name}.statistic"] = test["statistic"]
        out[f"tests.{name}.p_value"] = test["p_value"]
    for name, shift in read["calibration_shift"].items():
        for field in ("mean", "se", "z", "p_value"):
            out[f"calibration_shift.{name}.{field}"] = shift[field]
    out["residuals_beyond_margin"] = read["residuals_beyond_margin"]
    return out


def evaluate_block(selected: npt.NDArray[np.int64]) -> dict[str, npt.NDArray[Any]]:
    return batch_statistics(selected)


def calibrate(replicates: int, seed: int, block: int = NULL_BLOCK) -> dict[str, npt.NDArray[Any]]:
    """batch_statistics over all replicates, blocks mapped through the process pool in replicate order."""
    counts = draw_counts(replicates, seed)
    blocks = [counts[start : start + block] for start in range(0, replicates, block)]
    results = parallel.ordered_map(evaluate_block, blocks, min_items=1)
    return {name: np.concatenate([r[name] for r in results]) for name in results[0]}


def rate_record(
    statistics: dict[str, npt.NDArray[Any]], replicates: int, seed: int, seed_source: str
) -> dict[str, Any]:
    """False-resolution rate of every test and class shift with its binomial standard error."""
    nominal = math.sqrt(diag.ALPHA * (1 - diag.ALPHA) / replicates)
    rates: dict[str, Any] = {}
    for name in sorted(statistics):
        if name.endswith(".p_value"):
            resolved = int(np.count_nonzero(statistics[name] < diag.ALPHA))
            rate = resolved / replicates
            rates[name.removesuffix(".p_value")] = {
                "resolved": resolved,
                "rate": rate,
                "se": math.sqrt(rate * (1 - rate) / replicates),
                "z_vs_alpha": (rate - diag.ALPHA) / nominal,
            }
    beyond = int(np.count_nonzero(statistics["residuals_beyond_margin"]))
    return {
        "schema": SCHEMA,
        "replicates": replicates,
        "trials": diag.TRIALS,
        "alpha": diag.ALPHA,
        "nominal_se": nominal,
        "null_fractions": NULL_FRACTIONS,
        "seed": seed,
        "seed_source": seed_source,
        "rates": rates,
        "replicates_with_residual_beyond_margin": beyond,
    }


def bound_failures(record: dict[str, Any]) -> list[str]:
    """Tests whose rate lies outside ALPHA +- BOUND_SIGMAS nominal errors, and a beyond-margin rate above the band."""
    nominal = record["nominal_se"]
    failures = [
        f"{name}: rate {row['rate']:.5f} (z {row['z_vs_alpha']:+.2f})"
        for name, row in record["rates"].items()
        if abs(row["rate"] - record["alpha"]) > BOUND_SIGMAS * nominal
    ]
    beyond = record["replicates_with_residual_beyond_margin"] / record["replicates"]
    if beyond > record["alpha"] + BOUND_SIGMAS * nominal:
        failures.append(f"residuals_beyond_margin: rate {beyond:.5f}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--null-calibration", type=int, required=True, metavar="REPLICATES")
    qrng_seeds.add_seed_argument(parser, "--null-seed", default=NULL_SEED)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--bound", action="store_true", help="exit 1 when a rate leaves ALPHA +- 3 nominal errors")
    args = parser.parse_args()
    record = rate_record(
        calibrate(args.null_calibration, args.null_seed), args.null_calibration, args.null_seed, args.null_seed_source
    )
    text = json.dumps(record, indent=1) + "\n"
    if args.out:
        args.out.write_text(text)
    else:
        sys.stdout.write(text)
    failures = bound_failures(record) if args.bound else []
    for line in failures:
        print(f"null calibration: {line}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
