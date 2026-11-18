"""Operating characteristics of replicate and shot options of the bracketed twin layout, one option per run.

The CASE.md of the bracketed Tuna-17 successor ("Designs rejected") prices a third replicate, replicates of only the
twin or of only the base batches, and a change of shots by simulating series of the preregistered rule under an
independent drift of OC_DRIFT_SD in every batch contrast. One run prices one option: `--base-replicates` and
`--twin-replicates` per template, `--shot-factor` times the layout's shots per circuit, `--draws` series per world,
`--seed qrng:DRAW#INDEX` for the generator (a value of the retained draw drives one option; the worlds draw in
WORLD_NAMES order from it). The result line carries the option's layout (batches, waves, jobs, shots and execution
seconds), the label counts per world and per (drift model, batch gate) and the seed's spelling. `--reference` adds the
labels of the shared rule `qi_pathion_one_cz_null_rule_v2.decide_estimates` beside those of `decide`, which agree with
it at the previous layout (2 / 2 replicates at 32,768 shots).

Drift models: `contrast` adds the drift to the twin contrast of each batch (the twins' batch-level drift) and `pair`
leaves the twin contrast free of it, as a drift common to the two twins of a batch. Batch gates: `fixed` keeps the
BATCH_CHI2 of 1 degree of freedom, `dof` takes the alpha = 0.001 quantile at the replicates' degrees of freedom.

`--check CELLS` regenerates every row of a retained cells file from the value of the draw its `seed_source` names and
compares layout and counts exactly; it exits 1 on any difference. The draw of the retained cells is owned whole by
the bracketed case's `prediction.json` (the seed ledger takes no row for it): the nine cells take values 911 to 919
in index order, and the case's operating-characteristic tables take 920 to 922.

Usage: "$PYTHON" scripts/qi_pathion_one_cz_null_bracketed_pricing.py
       --seed qrng:docs/evidence/anu_qrng/draw-<UTC>.json#I --base-replicates 4 --twin-replicates 4
       --shot-factor 0.5 --draws 20000 [--reference]
       "$PYTHON" scripts/qi_pathion_one_cz_null_bracketed_pricing.py
       --check docs/evidence/qi-bracketed-pricing/cells.jsonl
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections.abc import Sequence
from functools import partial
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import chi2

sys.path[:0] = [str(Path(__file__).resolve().parents[1] / "gororoba_quantum"), str(Path(__file__).resolve().parent)]
import qi_pathion_one_cz_null_analysis as ana  # noqa: E402
import qi_pathion_one_cz_null_bracketed_cases as bracketed  # noqa: E402
import qi_pathion_one_cz_null_cases as oc  # noqa: E402
import qi_pathion_one_cz_null_rule_v2 as rule  # noqa: E402

import parallel  # noqa: E402
import qrng_seeds  # noqa: E402

WORLD_NAMES = ("coin_dropout", "superposition_only")
TEMPLATES = oc.TEMPLATES
DRIFT_MODELS = ("contrast", "pair")
GATE_MODES = ("fixed", "dof")
SCRIPT = "scripts/qi_pathion_one_cz_null_bracketed_pricing.py"
# Per circuit: the fixed overhead of a job and the slowest and fastest measured seconds per shot (Tuna-17), and the
# 300 s job limit; the CASE.md table prices execution seconds with these.
JOB_OVERHEAD_SECONDS = 2.6
SECONDS_PER_SHOT_FASTEST = 0.53e-3
JOB_LIMIT_SECONDS = 300


def gate_threshold(dof: int, mode: str) -> float:
    """The batch-gate threshold: BATCH_CHI2 (1 degree of freedom, alpha 0.001) for `fixed`, and for `dof` the
    alpha = 0.001 quantile at `dof` degrees of freedom."""
    return float(oc.BATCH_CHI2) if mode == "fixed" else float(chi2.ppf(0.999, dof))


def decide(
    rows: dict[str, dict[str, list[tuple[float, float]]]], base_gate: float, twin_gate: float
) -> tuple[str, list[str]]:
    """The preregistered decision of per-batch estimates with the batch gates set per kind, and the gates it tripped.

    The pooling is `qi_pathion_one_cz_null_analysis`'s; a base or twin heterogeneity above its gate reads
    `unresolved_batch`, as `decide_estimates` does, and a superposition-only reading with a significantly negative twin
    b0 offset reads `unresolved_negative_twin`."""
    base = {t: ana.pooled(rows[t]["base"]) for t in TEMPLATES}
    twin = {t: ana.pooled(rows[t]["twin"]) for t in TEMPLATES}
    z = oc.Z_RESOLVE
    batch_q = {(t, kind): ana.heterogeneity(rows[t][kind]) for t in TEMPLATES for kind in ("base", "twin")}
    block_q = {
        "base": ana.heterogeneity([base[t] for t in oc.LOW_NAMES]),
        "twin": ana.heterogeneity([twin[t] for t in oc.LOW_NAMES]),
    }
    s0, t0 = base["b0"], twin["b0"]
    c, d = ana.pooled([base[t] for t in oc.LOW_NAMES]), ana.pooled([twin[t] for t in oc.LOW_NAMES])
    m, r = ana.pooled([c, d]), ana.pooled([s0, t0])
    diff, diff_se = r[0] - m[0], math.hypot(r[1], m[1])
    tripped = [f"{t}/{kind}" for (t, kind), q in batch_q.items() if q > (base_gate if kind == "base" else twin_gate)]
    if tripped:
        return "unresolved_batch", tripped
    if any(q > oc.BLOCK_CHI2 for q in block_q.values()):
        return "unresolved_block", [kind for kind, q in block_q.items() if q > oc.BLOCK_CHI2]
    if s0[0] < z * s0[1]:
        return "offset_absent", []
    if t0[0] < z * t0[1]:
        gap = (s0[0] - t0[0]) / math.hypot(s0[1], t0[1])
        label = "superposition_only" if gap >= z else "unresolved"
        if label == "superposition_only" and t0[0] < -z * t0[1]:
            label = "unresolved_negative_twin"
        return label, []
    if abs(c[0] - d[0]) > z * math.hypot(c[1], d[1]):
        return "unresolved_context", []
    if abs(m[0]) <= z * m[1] and diff >= z * diff_se:
        return "zero", []
    if m[0] >= z * m[1] and abs(diff) <= oc.B0_LIKE_Z * diff_se:
        return "b0_like", []
    if m[0] >= z * m[1]:
        return "intermediate", []
    return "unresolved", []


def build_rows(
    item: tuple[Any, Any, Any, Any], mean: dict[str, float], se_base: dict[str, float], n_twin: int, drift_in_twin: bool
) -> dict[str, dict[str, list[tuple[float, float]]]]:
    """Per-batch (value, se) of one simulated series: base batches from a noise and a drift draw, twin batches from
    the binomial coin-zero counts of the two twins plus, under the `contrast` drift model, the twin-contrast drift."""
    base_noise, base_drift, zeros, twin_drift = item
    rows: dict[str, dict[str, list[tuple[float, float]]]] = {}
    for j, name in enumerate(TEMPLATES):
        key = "b0" if name == "b0" else "k"
        twins = []
        for replicate in range(zeros.shape[1]):
            value, se = bracketed.twin_contrast(
                int(zeros[j, replicate, 1]), n_twin, int(zeros[j, replicate, 0]), n_twin
            )
            twins.append((value + (float(twin_drift[j, replicate]) if drift_in_twin else 0.0), se))
        rows[name] = {
            "base": [
                (mean[f"s_{key}"] + se_base[name] * float(base_noise[j, r]) + float(base_drift[j, r]), se_base[name])
                for r in range(base_noise.shape[1])
            ],
            "twin": twins,
        }
    return rows


def one_series(
    item: tuple[Any, Any, Any, Any],
    *,
    mean: dict[str, float],
    se_base: dict[str, float],
    n_twin: int,
    reference: bool,
) -> dict[str, tuple[str, tuple[str, ...]]]:
    """The labels of one series under every (drift model, gate mode), and the shared rule's label under `reference`."""
    out: dict[str, tuple[str, tuple[str, ...]]] = {}
    for model in DRIFT_MODELS:
        rows = build_rows(item, mean, se_base, n_twin, model == "contrast")
        replicates_base, replicates_twin = len(rows["b0"]["base"]), len(rows["b0"]["twin"])
        for mode in GATE_MODES:
            # A kind with one replicate has no heterogeneity to test, so its threshold is infinite; the other kind keeps
            # its own degrees of freedom.
            base_threshold = gate_threshold(replicates_base - 1, mode) if replicates_base > 1 else 1e300
            twin_threshold = gate_threshold(replicates_twin - 1, mode) if replicates_twin > 1 else 1e300
            label, tripped = decide(rows, base_threshold, twin_threshold)
            out[f"{model}/{mode}"] = (label, tuple(tripped))
        if reference:
            out[f"{model}/ref"] = (str(rule.decide_estimates(rows, oc.B0_LIKE_Z)["label"]), ())
    return out


def layout(base_replicates: int, twin_replicates: int, shot_factor: float) -> dict[str, Any]:
    """The batches, waves, jobs, shots and execution seconds of an option, and its per-circuit shots."""
    timing = oc.coin_timing()
    slowest = timing["seconds_per_shot_max"]
    n_batch = int(round(oc.BATCH_SHOTS * shot_factor))
    n_control = min(
        int(round(oc.CONTROL_SHOTS * shot_factor)), int((JOB_LIMIT_SECONDS - JOB_OVERHEAD_SECONDS) / slowest)
    )
    calibration = [row for row in oc.batch_rows(oc.TUNA_SERIES) if row["kind"] == "joint"]
    calibration_circuits = sum(len(row["circuits"]) for row in calibration)
    batches = len(TEMPLATES) * (base_replicates + twin_replicates) + len(calibration)
    jobs = 3 * len(TEMPLATES) * base_replicates + 4 * len(TEMPLATES) * twin_replicates + calibration_circuits
    shots = (
        3 * (len(TEMPLATES) - 1) * base_replicates * n_batch
        + 3 * base_replicates * n_control
        + 4 * len(TEMPLATES) * twin_replicates * n_batch
        + calibration_circuits * oc.JOINT_SHOTS
    )
    return {
        "batches": batches,
        "waves": -(-batches // 3),
        "jobs": jobs,
        "shots": shots,
        "sec_low": jobs * JOB_OVERHEAD_SECONDS + shots * SECONDS_PER_SHOT_FASTEST,
        "sec_high": jobs * JOB_OVERHEAD_SECONDS + shots * slowest,
        "longest_job_s": JOB_OVERHEAD_SECONDS + max(n_batch, n_control) * slowest,
        "n_b": n_batch,
        "n_c": n_control,
        "cap": int((JOB_LIMIT_SECONDS - JOB_OVERHEAD_SECONDS) / slowest),
    }


def simulate(
    seed: int,
    base_replicates: int,
    twin_replicates: int,
    shot_factor: float,
    draws: int,
    reference: bool = False,
) -> tuple[dict[str, Any], dict[str, dict[str, dict[str, int]]]]:
    """The layout of an option and its label counts per world and (drift model / gate mode); the worlds draw in
    WORLD_NAMES order from one generator seeded by `seed`."""
    option = layout(base_replicates, twin_replicates, shot_factor)
    e01, e10 = bracketed.retained_selector_rates()
    n_batch, n_control = option["n_b"], option["n_c"]
    se_base = {t: 1.0 / math.sqrt(n_control if t == "b0" else n_batch) for t in TEMPLATES}
    rng = np.random.default_rng(seed)
    result: dict[str, dict[str, dict[str, int]]] = {}
    for world in WORLD_NAMES:
        mean = rule.WORLDS[world]
        twin_mean = np.array([mean["t_b0" if t == "b0" else "t_k"] for t in TEMPLATES])
        p_read = 0.5 + (e10 - e01) / 2 + np.array([-0.5, 0.5]) * twin_mean[:, None]
        base_shape, twin_shape = (draws, len(TEMPLATES), base_replicates), (draws, len(TEMPLATES), twin_replicates)
        base_noise = rng.normal(size=base_shape)
        base_drift = rng.normal(scale=oc.OC_DRIFT_SD, size=base_shape)
        zeros = rng.binomial(n_batch, p_read[:, None, :], size=(*twin_shape, 2))
        twin_drift = rng.normal(scale=oc.OC_DRIFT_SD, size=twin_shape)
        items = list(zip(base_noise, base_drift, zeros, twin_drift, strict=True))
        outputs = parallel.ordered_map(
            partial(one_series, mean=mean, se_base=se_base, n_twin=n_batch, reference=reference), items
        )
        counts: dict[str, dict[str, int]] = {}
        for output in outputs:
            for key, (label, tripped) in output.items():
                tally = counts.setdefault(key, {})
                tally[label] = tally.get(label, 0) + 1
                for gate in tripped:
                    tally[f"trip:{gate}"] = tally.get(f"trip:{gate}", 0) + 1
        result[world] = counts
    return option, result


def result_line(args: argparse.Namespace) -> dict[str, Any]:
    """The JSON object of one priced option: its arguments, layout, counts and the seed's spelling."""
    option, counts = simulate(
        args.seed, args.base_replicates, args.twin_replicates, args.shot_factor, args.draws, args.reference
    )
    experiment = f"pricing-{args.base_replicates}-{args.twin_replicates}-{args.shot_factor}"
    return {
        "seed_source": qrng_seeds.seed_record(SCRIPT, "--seed", experiment, args.seed_source),
        "rb": args.base_replicates,
        "rt": args.twin_replicates,
        "f": args.shot_factor,
        "draws": args.draws,
        "layout": option,
        "counts": counts,
    }


# The nine retained options in index order: each takes value 911 + position of DRAW; the first carries the shared rule
# beside the options' own decision (`--reference`).
CELL_DRAW = "docs/evidence/anu_qrng/draw-2026-11-14T183922Z.json"
CELL_FIRST_INDEX = 911
CELL_PLAN = (
    (2, 2, 1.0, True),
    (2, 3, 1.0, False),
    (3, 2, 1.0, False),
    (3, 3, 1.0, False),
    (2, 2, 2.0, False),
    (2, 4, 1.0, False),
    (2, 2, 0.5, False),
    (4, 4, 0.5, False),
    (3, 3, 0.5, False),
)


def cell_lines() -> list[str]:
    """The text of every retained cell, one JSON line per option of CELL_PLAN, regenerated from its draw value."""
    lines = []
    for position, (base, twin, factor, reference) in enumerate(CELL_PLAN):
        spelling = f"qrng:{CELL_DRAW}#{CELL_FIRST_INDEX + position}"
        seed, _ = qrng_seeds.parse_value(spelling, [])
        args = argparse.Namespace(
            seed=seed,
            seed_source=spelling,
            base_replicates=base,
            twin_replicates=twin,
            shot_factor=factor,
            draws=20000,
            reference=reference,
        )
        lines.append(json.dumps(result_line(args), sort_keys=True))
    return lines


def replay(cells: Path) -> list[str]:
    """The rows of a retained cells file whose regenerated layout or counts differ from the stored ones."""
    problems = []
    for number, line in enumerate(cells.read_text(encoding="utf-8").splitlines(), 1):
        cell = json.loads(line)
        seed = qrng_seeds.resolve(cell["seed_source"]["sources"][0])[0]
        reference = "contrast/ref" in cell["counts"][WORLD_NAMES[0]]
        option, counts = simulate(seed, cell["rb"], cell["rt"], cell["f"], cell["draws"], reference)
        if option != cell["layout"] or counts != cell["counts"]:
            problems.append(
                f"row {number} ({cell['rb']}/{cell['rt']} at factor {cell['f']}) differs from its regeneration"
            )
    return problems


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Price one replicate and shot option of the bracketed twin layout.")
    qrng_seeds.add_seed_argument(parser, "--seed", help="qrng:<draw>#<index> or repro:<integer>")
    parser.add_argument("--base-replicates", type=int)
    parser.add_argument("--twin-replicates", type=int)
    parser.add_argument("--shot-factor", type=float)
    parser.add_argument("--draws", type=int, default=20000)
    parser.add_argument("--reference", action="store_true")
    parser.add_argument("--check", type=Path, help="regenerate every row of a retained cells file")
    parser.add_argument("--write", type=Path, help="write the nine retained cells of CELL_PLAN to a new file")
    args = parser.parse_args(argv)
    if args.write is not None:
        with args.write.open("x", encoding="utf-8") as handle:
            handle.write("\n".join(cell_lines()) + "\n")
        return 0
    if args.check is not None:
        problems = replay(args.check)
        for problem in problems:
            print(problem, file=sys.stderr)
        if not problems:
            print(f"{args.check}: every row regenerates count for count")
        return 1 if problems else 0
    if args.seed is None or args.base_replicates is None or args.twin_replicates is None or args.shot_factor is None:
        parser.error("--seed, --base-replicates, --twin-replicates and --shot-factor are required without --check")
    if min(args.base_replicates, args.twin_replicates, args.draws) < 1 or args.shot_factor <= 0:
        parser.error("replicates and draws must be positive and the shot factor above zero")
    print(json.dumps(result_line(args), sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
