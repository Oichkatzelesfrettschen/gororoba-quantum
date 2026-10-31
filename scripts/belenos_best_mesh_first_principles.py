#!/usr/bin/env python3
"""First-principles checks behind the Belenos best-mesh teleportation replay.

The script reads the retained teleportation rehearsal runs (job-02, its exact replay and job-03) and computes, per
served mesh, the quantities that decide how a winner-and-loser replay of the job-02 and job-03 compilation seeds
reads:

- compiled: the noiseless three-photon propagation through each returned ``computed_circuit`` unitary, scored by the
  rehearsal classifier, against the target operator of its setting. A compiled-mesh shortfall that differs by seed
  places the per-seed error in the compiler; equal unit scores place it on the chip.
- shrinkage: the normal-normal hierarchical estimate of each input's true block A minus block B difference and the
  expected winner-minus-loser gap, with the directional Benjamini-Hochberg sign decisions.
- replay_power: the posterior-predictive power of a winner-and-loser replay at two and four jobs, with inputs dropped
  when a seed returns a new mesh, and its size when no mesh error persists.
- replay_budget: the shot cap and credits per replay job from the lossiest retained mesh.

Usage: belenos_best_mesh_first_principles.py --out PATH --seed qrng:<draw>#<index>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import qd_belenos_mesh as mesh  # noqa: E402
import qd_teleportation_rehearsal as tr  # noqa: E402
from qd_network_protocol import propagate  # noqa: E402

import qrng_seeds  # noqa: E402
from parallel import ordered_map  # noqa: E402

RUNS = ROOT / "results/quandela/runs"
RUN_NAMES = {
    "job-02": "2026-10-31T035736Z-qpu_belenos-teleportation_rehearsal-job-02",
    "job-02-replay": "2026-10-31T042633Z-qpu_belenos-teleportation_rehearsal-job-02-replay",
    "job-03": "2026-10-31T040337Z-qpu_belenos-teleportation_rehearsal-job-03",
}


def clicks_of(unitary: np.ndarray, source: Sequence[int]) -> dict[tuple[int, ...], float]:
    """Threshold-click distribution of the noiseless three-photon propagation through ``unitary``."""
    output = propagate(unitary, {tuple(source): 1.0 + 0.0j})
    clicks: dict[tuple[int, ...], float] = {}
    for occupation, amplitude in output.items():
        key = tuple(1 if count else 0 for count in occupation)
        clicks[key] = clicks.get(key, 0.0) + abs(amplitude) ** 2
    return clicks


def total_variation(left: Mapping[tuple[int, ...], float], right: Mapping[tuple[int, ...], float]) -> float:
    """Total variation distance of two click distributions: the complete observable of threshold detection, blind to
    the input-photon and output-mode phases that a column comparison would count."""
    return 0.5 * sum(abs(left.get(key, 0.0) - right.get(key, 0.0)) for key in set(left) | set(right))


def compiled_row(item: tuple[str, int, Mapping[str, Any], str, Sequence[int]]) -> dict[str, Any]:
    run, index, setting, circuit_text, layout = item
    elements = mesh.decode(circuit_text)
    arch = mesh.run_architecture(elements)
    phases = mesh.mesh_phases(arch, elements)
    compiled = mesh.unitary(arch, phases)
    target = tr.operator_of(dict(setting))
    source = tr.source_state(layout)
    occupied = [mode for mode, count in enumerate(source) if count]
    label = setting["label"]
    target_clicks, compiled_clicks = clicks_of(target, source), clicks_of(compiled, source)
    ideal_acc, ideal_cor = tr.scored(label, target_clicks, layout)
    comp_acc, comp_cor = tr.scored(label, compiled_clicks, layout)
    power = np.abs(compiled[:, occupied]) ** 2 - np.abs(target[:, occupied]) ** 2
    return {
        "run": run,
        "index": index,
        "label": label,
        "compilation_seed": setting["compilation_seed"],
        "mesh_sha": hashlib.sha256(mesh.unzip(circuit_text).encode()).hexdigest()[:8],
        "heater_phase_rad": float(sum(phases)),
        "click_total_variation": total_variation(compiled_clicks, target_clicks),
        "max_column_power_difference": float(np.max(np.abs(power))),
        "target_accepted_probability": ideal_acc,
        "target_conditional_fidelity": ideal_cor / ideal_acc,
        "compiled_accepted_probability": comp_acc,
        "compiled_conditional_fidelity": comp_cor / comp_acc,
    }


def compiled_section() -> list[dict[str, Any]]:
    items = []
    for run, name in RUN_NAMES.items():
        cases = json.loads((RUNS / name / "cases.json").read_text(encoding="utf-8"))
        layout = tuple(cases["layout"]["chip_modes"])
        circuits = mesh.computed_circuits(RUNS / name)
        if len(circuits) != len(cases["settings"]):
            raise ValueError(f"{run}: {len(circuits)} computed circuits for {len(cases['settings'])} settings")
        for index, (setting, text) in enumerate(zip(cases["settings"], circuits, strict=True)):
            items.append((run, index, setting, text, layout))
    return ordered_map(compiled_row, items, min_items=1)


LABELS = ("+Z", "-Z", "+X", "-X", "+Y", "-Y")
BLOCKS = {"job-02": "A", "job-02-replay": "A", "job-03": "B"}
TAU_GRID = np.linspace(0.0, 0.25, 1001)
FDR_Q = 0.10
ALPHA_ONE_SIDED = 0.05
Z_ONE_SIDED = 1.6448536269514722
REPLAY_SAMPLES = 1200
TRIALS = 200_000
DROPOUTS = (0, 1, 2, 3)
JOB_COUNTS = (2, 4)


def iterations() -> list[dict[str, Any]]:
    """Every retained iteration with its run and block."""
    rows: list[dict[str, Any]] = []
    for run, name in RUN_NAMES.items():
        analysis = json.loads((RUNS / name / "analysis.json").read_text(encoding="utf-8"))
        rows.extend({**row, "run": run, "block_of_seed": BLOCKS[run]} for row in analysis["iterations"])
    return rows


def block_counts(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, dict[str, float]]]:
    """Per input and block: correct, accepted, samples and shots summed over the block's runs (job-02 pools with its
    exact replay, which returned the same six meshes)."""
    out: dict[str, dict[str, dict[str, float]]] = {label: {} for label in LABELS}
    for row in rows:
        cell = out[row["label"]].setdefault(
            row["block_of_seed"],
            {"correct": 0, "accepted": 0, "samples": 0, "shots": 0, "seed": row["compilation_seed"]},
        )
        if cell["seed"] != row["compilation_seed"]:
            raise ValueError(f"{row['label']} block {row['block_of_seed']} mixes compilation seeds")
        for key, field in (("correct", "correct"), ("accepted", "accepted"), ("samples", "samples")):
            cell[key] += row[field]
        cell["shots"] += row["nb_shots_used"]
    return out


def normal_cdf(x: Any) -> Any:
    from scipy.special import ndtr

    return ndtr(x)


def shrinkage(counts: Mapping[str, Mapping[str, Mapping[str, float]]]) -> dict[str, Any]:
    """Normal-normal hierarchical shrinkage of the six block A minus block B correctness differences.

    The A and B seeds of an input are exchangeable draws of the transpiler, so the prior on the true difference is
    centered at zero: mu_i ~ N(0, tau^2), d_i | mu_i ~ N(mu_i, s_i^2) with s_i the binomial standard error. Tweedie's
    formula for this prior gives E[mu_i | d_i, tau] = C_i d_i with C_i = tau^2 / (tau^2 + s_i^2) (Efron 2011, Eqs. 3.7
    and 3.8). tau carries a uniform prior on TAU_GRID, so its estimation error enters every posterior moment, the
    hierarchical counterpart of Efron's Eq. 7.26 regret term. The expected winner-minus-loser gap of input i is
    E[sign(d_i) mu_i | data] = |d_i| E[C_i | data]."""
    d = np.empty(len(LABELS))
    s = np.empty(len(LABELS))
    for i, label in enumerate(LABELS):
        a, b = counts[label]["A"], counts[label]["B"]
        pa, pb = a["correct"] / a["accepted"], b["correct"] / b["accepted"]
        d[i] = pa - pb
        s[i] = np.sqrt(pa * (1 - pa) / a["accepted"] + pb * (1 - pb) / b["accepted"])
    z = d / s
    n = len(LABELS)
    variance = TAU_GRID[:, None] ** 2 + s[None, :] ** 2
    log_post = np.sum(-0.5 * np.log(variance) - d[None, :] ** 2 / (2 * variance), axis=1)
    weights = np.exp(log_post - log_post.max())
    weights /= weights.sum()
    factor = TAU_GRID[:, None] ** 2 / variance
    mean_factor = weights @ factor
    gap = np.abs(d) * mean_factor
    gap_second = weights @ (factor * s**2 + factor**2 * d**2)
    sign_right = weights @ normal_cdf(np.sqrt(factor) * np.abs(d) / s)
    cdf = np.cumsum(weights)
    p_values = 2 * (1 - normal_cdf(np.abs(z)))
    order = np.argsort(p_values)
    passed = [p_values[k] <= FDR_Q * (rank + 1) / n for rank, k in enumerate(order)]
    determined = max((rank + 1 for rank, ok in enumerate(passed) if ok), default=0)
    return {
        "prior": "mu_i ~ N(0, tau^2), tau uniform on [0, 0.25]",
        "inputs": {
            label: {
                "block_a": dict(counts[label]["A"]),
                "block_b": dict(counts[label]["B"]),
                "difference": float(d[i]),
                "standard_error": float(s[i]),
                "z": float(z[i]),
                "two_sided_p": float(p_values[i]),
                "winner_block": "A" if d[i] > 0 else "B",
                "shrinkage_factor": float(mean_factor[i]),
                "expected_gap": float(gap[i]),
                "gap_posterior_sd": float(np.sqrt(gap_second[i] - gap[i] ** 2)),
                "probability_winner_is_better": float(sign_right[i]),
                "sign_determined_directional_bh": bool(i in {int(k) for k in order[:determined]}),
            }
            for i, label in enumerate(LABELS)
        },
        "chi_square_on_6": float(np.sum(z**2)),
        "james_stein_factor": float(max(0.0, 1 - (n - 2) / np.sum(z**2))),
        "tau_mle": float(TAU_GRID[np.argmax(log_post)]),
        "tau_posterior_mean": float(weights @ TAU_GRID),
        "tau_90_interval": [float(TAU_GRID[np.searchsorted(cdf, 0.05)]), float(TAU_GRID[np.searchsorted(cdf, 0.95)])],
        "mean_expected_gap": float(gap.mean()),
        "directional_bh_q": FDR_Q,
        "signs_determined": determined,
        "_draw": {"d": d, "s": s, "weights": weights},
    }


def replay_power(counts: Mapping[str, Any], shrink: Mapping[str, Any], seed: int) -> dict[str, Any]:
    """Posterior-predictive power of the winner-and-loser replay.

    Each trial draws tau from its posterior, each input's true A-minus-B difference from its conditional posterior
    N(C d, C s^2), and sets the winner and loser correctness at the input's observed two-block mean plus and minus
    half the signed gap. Each mesh runs REPLAY_SAMPLES samples per job pair at its observed acceptance per sample, so
    accepted counts and correct counts are binomial. The primary statistic is the summed contrast over the kept
    inputs divided by its binomial standard error, one-sided at ALPHA_ONE_SIDED. A dropout removes inputs whose seed
    returns a different mesh after the recalibration, as the preregistered mismatch branch does. Trials draw every
    input first and evaluate as numpy arrays, so the record depends only on the seed."""
    rng = np.random.default_rng(seed)
    draw = shrink["_draw"]
    d, s, weights = draw["d"], draw["s"], draw["weights"]
    sign = np.sign(d)
    mean_level = np.empty(len(LABELS))
    accept = np.empty((2, len(LABELS)))
    for i, label in enumerate(LABELS):
        a, b = counts[label]["A"], counts[label]["B"]
        mean_level[i] = 0.5 * (a["correct"] / a["accepted"] + b["correct"] / b["accepted"])
        winner, loser = (a, b) if d[i] > 0 else (b, a)
        accept[0, i] = winner["accepted"] / winner["samples"]
        accept[1, i] = loser["accepted"] / loser["samples"]
    tau = TAU_GRID[rng.choice(len(TAU_GRID), size=TRIALS, p=weights)]
    factor = tau[:, None] ** 2 / (tau[:, None] ** 2 + s[None, :] ** 2)
    true_difference = factor * d + np.sqrt(factor) * s * rng.standard_normal((TRIALS, len(LABELS)))
    gap = sign * true_difference
    tau_mle = TAU_GRID[int(np.argmax(weights))]
    factor_mle = tau_mle**2 / (tau_mle**2 + s**2)
    gap_mle = sign * (factor_mle * d + np.sqrt(factor_mle) * s * rng.standard_normal((TRIALS, len(LABELS))))
    order = rng.random((TRIALS, len(LABELS))).argsort(axis=1)
    uniforms = [rng.random((TRIALS, len(LABELS))) for _ in range(4 * len(JOB_COUNTS))]
    out: dict[str, Any] = {"seed": seed, "trials": TRIALS, "samples_per_iteration": REPLAY_SAMPLES, "designs": []}
    for j, jobs in enumerate(JOB_COUNTS):
        samples = REPLAY_SAMPLES * jobs // 2
        u = uniforms[4 * j : 4 * j + 4]
        from scipy.stats import binom

        scenarios = (
            ("persistent mesh error", gap),
            ("persistent mesh error, tau fixed at its maximum", gap_mle),
            ("no persistent mesh error", 0.0 * gap),
        )
        for scenario, effect in scenarios:
            p_win = np.clip(mean_level + effect / 2, 0.0, 1.0)
            p_lose = np.clip(mean_level - effect / 2, 0.0, 1.0)
            n_win = np.maximum(binom.ppf(u[0], samples, accept[0]), 1)
            n_lose = np.maximum(binom.ppf(u[1], samples, accept[1]), 1)
            c_win = binom.ppf(u[2], n_win, p_win)
            c_lose = binom.ppf(u[3], n_lose, p_lose)
            f_win, f_lose = c_win / n_win, c_lose / n_lose
            contrast = f_win - f_lose
            variance = f_win * (1 - f_win) / n_win + f_lose * (1 - f_lose) / n_lose
            for dropped in DROPOUTS:
                keep = order >= dropped
                total = np.where(keep, contrast, 0.0).sum(axis=1)
                spread = np.sqrt(np.where(keep, variance, 0.0).sum(axis=1))
                statistic = np.divide(total, spread, out=np.zeros_like(total), where=spread > 0)
                kept = len(LABELS) - dropped
                out["designs"].append(
                    {
                        "jobs": jobs,
                        "scenario": scenario,
                        "pairs_dropped": dropped,
                        "power": float(np.mean(statistic > Z_ONE_SIDED)),
                        "mean_true_gap_kept": float(np.mean(np.where(keep, effect, 0.0).sum(axis=1) / kept)),
                    }
                )
    return out


def replay_budget(counts: Mapping[str, Any]) -> dict[str, Any]:
    """Shot cap and credits per replay job: the lossiest retained mesh's shots per sample sets max_shots."""
    shots_per_sample = max(cell["shots"] / cell["samples"] for row in counts.values() for cell in row.values())
    raw = REPLAY_SAMPLES * shots_per_sample * tr.SHOT_MARGIN
    max_shots = int(-(-raw // tr.SHOT_QUANTUM) * tr.SHOT_QUANTUM)
    return {
        "max_shots_per_sample_retained": shots_per_sample,
        "max_shots_per_iteration": max_shots,
        "credits_per_job": tr.PER_JOB_CREDITS + max_shots * tr.PRICE_PER_SHOT,
        "credits": {str(jobs): jobs * (tr.PER_JOB_CREDITS + max_shots * tr.PRICE_PER_SHOT) for jobs in JOB_COUNTS},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--out", type=Path, required=True)
    qrng_seeds.add_seed_argument(parser, "--seed", help="power-simulation seed, qrng:<draw>#<index>")
    args = parser.parse_args()
    if args.seed is None:
        parser.error("--seed is required")
    counts = block_counts(iterations())
    shrink = shrinkage(counts)
    power = replay_power(counts, shrink, args.seed)
    shrink.pop("_draw")
    record = {
        "schema": "belenos-best-mesh-first-principles-v1",
        "seed_source": qrng_seeds.seed_record(
            "scripts/belenos_best_mesh_first_principles.py",
            "--seed",
            "belenos-best-mesh-replay-power",
            args.seed_source,
        ),
        "compiled": compiled_section(),
        "shrinkage": shrink,
        "replay_power": power,
        "replay_budget": replay_budget(counts),
    }
    args.out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
