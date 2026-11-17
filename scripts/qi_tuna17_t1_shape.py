"""Tuna-17 T1 shape: refit the retained counts of the characterization series and test five explanations.

The single-exponential verdict of qi_tuna17_characterization_cases.py fails on most qubits. This script refits the
retained counts only (no provider read) and writes one analysis record:

- per qubit, five decay models (single, single with a free amplitude, plateau, stretched, biexponential) and the single
  exponential with a batch step, each a binomial-likelihood fit on the mean readout pair, with profile-likelihood
  intervals (gororoba_quantum/qi_decay_models.py);
- the single exponential under the opening, the closing, the mean and the time-interpolated readout pair, and jointly
  with the pooled readout counts (readout floor and drift);
- the waits of the circuit texts, the execution time of the six jobs against the delay, and a common stretched exponent
  (delay unit);
- the residual of the last delay against the fit of the earlier ones, its rank correlation with the degree and the
  neighbor residuals on the catalogue's coupling map, and the connected correlation of coupled against uncoupled
  pairs from the 17-bit shot records (crosstalk);
- the retained analyzer's T1 and standard error beside the refits (standard-error mechanism).

Usage: "$PYTHON" scripts/qi_tuna17_t1_shape.py OUT RUN_DIR... [--retained-analysis PATH] [--catalogue PATH]
OUT is the analysis record; RUN_DIR are the run directories of the series in submission order. The interpreter is the
analysis one (numpy and scipy), not QI_PYTHON.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import statistics
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "gororoba_quantum"))
import qi_tuna17_characterization_cases as cases  # noqa: E402

import parallel  # noqa: E402
import qi_bit_correlations  # noqa: E402
import qi_decay_models  # noqa: E402

SCHEMA = "qi-tuna17-t1-shape-analysis-v1"
CATALOGUE = HERE.parent / "docs/evidence/quantum_inspire/catalogue.json"
RETAINED_ANALYSIS = HERE.parent / "results/quantum_inspire/characterization_tuna_17_analysis.json"
TUNA17_TYPE_ID = 7
NOMINAL_CYCLE_NS = cases.CYCLE_SECONDS * 1e9
CHI_SQUARE_PER_DOF_LIMIT = 3.0
WAIT_LINE = re.compile(r"^wait\((\d+)\) q\[(\d+)\]$")


def coupling_edges(path: Path) -> list[tuple[int, int]]:
    """Undirected coupling edges of backend type 7 in the retained catalogue."""
    catalogue = json.loads(path.read_text(encoding="utf-8"))
    topology = next(kind["topology"] for kind in catalogue["backend_types"] if kind["id"] == TUNA17_TYPE_ID)
    return sorted({(min(a, b), max(a, b)) for a, b in topology})


def seconds(stamp: str) -> float:
    return datetime.fromisoformat(stamp).timestamp()


def load(runs: list[Path]) -> dict[str, Any]:
    """Counts, finish times and execution times of the series in submission order, from the retained run directories."""
    readouts: list[dict[str, Any]] = []
    t1: list[dict[str, Any]] = []
    shots_by_circuit: dict[tuple[str, str], list[str]] = {}
    waits: dict[int, bool] = {}
    nqubits = 0
    t1_runs: list[str] = []
    for run in runs:
        _, manifest, raw = cases.read_run(run)
        nqubits = manifest["nqubits"]
        record = json.loads((run / "results.json").read_text(encoding="utf-8"))
        jobs = {entry["file"]: entry for entry in record["jobs"]}
        rows = {row["file"]: row for row in manifest["circuits"]}
        for name, shots in raw.items():
            shots_by_circuit[(run.name, name)] = shots
        if {"readout-0.cq", "readout-1.cq"} <= set(raw):
            readouts.append(
                {
                    "run": run.name,
                    "zero": cases.p1(raw["readout-0.cq"], nqubits),
                    "one": cases.p1(raw["readout-1.cq"], nqubits),
                    "zero_shots": len(raw["readout-0.cq"]),
                    "one_shots": len(raw["readout-1.cq"]),
                    "time_s": statistics.fmean(
                        seconds(jobs[name]["job"]["finished_at"]) for name in ("readout-0.cq", "readout-1.cq")
                    ),
                }
            )
        for name in sorted(raw):
            if rows[name]["kind"] != "t1":
                continue
            cycles = rows[name]["wait_cycles"]
            lines = [WAIT_LINE.match(line) for line in (run / name).read_text(encoding="utf-8").splitlines()]
            found = {int(match.group(2)): int(match.group(1)) for match in lines if match}
            waits[cycles] = (
                set(found) == set(range(nqubits)) and set(found.values()) == {cycles} if cycles else not any(lines)
            )
            if run.name not in t1_runs:
                t1_runs.append(run.name)
            t1.append(
                {
                    "cycles": cycles,
                    "run": run.name,
                    "file": name,
                    "p1": cases.p1(raw[name], nqubits),
                    "shots": len(raw[name]),
                    "time_s": seconds(jobs[name]["job"]["finished_at"]),
                    "execution_s": jobs[name]["results"][0]["execution_time_in_seconds"],
                    "batch": t1_runs.index(run.name),
                }
            )
    return {
        "nqubits": nqubits,
        "readouts": readouts,
        "t1": sorted(t1, key=lambda row: row["cycles"]),
        "shots": shots_by_circuit,
        "waits_consistent": waits,
    }


def readout_pair(opening: dict[str, Any], qubit: int, key: str) -> list[int]:
    shots = opening[f"{key}_shots"]
    return [round(opening[key][qubit] * shots), shots]


def tasks(series: dict[str, Any], qubits: list[int]) -> list[dict[str, Any]]:
    opening, closing = series["readouts"][0], series["readouts"][-1]
    first_batch = min(row["batch"] for row in series["t1"])
    found = []
    for qubit in qubits:
        found.append(
            {
                "qubit": qubit,
                "delays_us": [row["cycles"] * cases.CYCLE_SECONDS * 1e6 for row in series["t1"]],
                "ones": [round(row["p1"][qubit] * row["shots"]) for row in series["t1"]],
                "shots": [row["shots"] for row in series["t1"]],
                "step": [int(row["batch"] > first_batch) for row in series["t1"]],
                "time_s": [row["time_s"] for row in series["t1"]],
                "opening": {
                    "zero": readout_pair(opening, qubit, "zero"),
                    "one": readout_pair(opening, qubit, "one"),
                    "time_s": opening["time_s"],
                },
                "closing": {
                    "zero": readout_pair(closing, qubit, "zero"),
                    "one": readout_pair(closing, qubit, "one"),
                    "time_s": closing["time_s"],
                },
            }
        )
    return found


def count_data(task: dict[str, Any]) -> qi_decay_models.CountData:
    variants = qi_decay_models.readout_variants(task)
    return qi_decay_models.build_data(task, *variants["mean"])


def per_dof(row: dict[str, Any]) -> float | None:
    value: float | None = row["chi_square_per_dof"]
    return value


def tally(values: list[float | None], limit: float = CHI_SQUARE_PER_DOF_LIMIT) -> dict[str, Any]:
    found = [value for value in values if value is not None]
    return {
        "qubits": len(found),
        "at_most_limit": sum(value <= limit for value in found),
        "median": statistics.median(found),
        "minimum": min(found),
        "maximum": max(found),
    }


def span(values: list[float]) -> dict[str, float]:
    return {"minimum": min(values), "median": statistics.median(values), "maximum": max(values)}


def execution_slope(t1: list[dict[str, Any]]) -> dict[str, Any]:
    """Least-squares slope of the job execution time against the delay, in ns of execution per cycle per shot."""
    cycles = np.array([row["cycles"] for row in t1], dtype=float)
    seconds_run = np.array([row["execution_s"] for row in t1])
    shots = float(t1[0]["shots"])
    fit, covariance = np.polyfit(cycles, seconds_run, 1, cov=True)
    return {
        "execution_s": [row["execution_s"] for row in t1],
        "slope_ns_per_cycle_per_shot": float(fit[0] / shots * 1e9),
        "slope_se_ns": float(math.sqrt(covariance[0, 0]) / shots * 1e9),
        "nominal_ns_per_cycle": NOMINAL_CYCLE_NS,
    }


def shot_records(series: dict[str, Any], edges: list[tuple[int, int]]) -> list[dict[str, Any]]:
    """Connected correlation contrast and overdispersion of every circuit that holds a single prepared state."""
    chosen = [(key, shots) for key, shots in sorted(series["shots"].items()) if key[1].startswith(("t1-", "readout-"))]
    contrasts = parallel.ordered_map(
        qi_bit_correlations.ShotContrast(edges), [shots for _, shots in chosen], min_items=2
    )
    return [
        {"run": run, "file": name, **contrast} for ((run, name), _), contrast in zip(chosen, contrasts, strict=True)
    ]


def analyze(
    runs: list[Path], retained: dict[str, Any] | None, edges: list[tuple[int, int]], qubits: list[int] | None = None
) -> dict[str, Any]:
    series = load(runs)
    if len(series["readouts"]) < 2 or len(series["t1"]) < 5:
        raise SystemExit("qi_tuna17_t1_shape: the runs hold no opening and closing readout pair and five delays")
    chosen = qubits if qubits is not None else list(range(series["nqubits"]))
    work = tasks(series, chosen)
    reports = parallel.ordered_map(qi_decay_models.analyze_decay, work, min_items=2)
    datas = [count_data(task) for task in work]
    exponent = qi_decay_models.common_parameter(datas, "stretched", "exponent")
    offset = qi_decay_models.common_parameter(datas, "delay_offset", "t0_us")
    models = [report["models"] for report in reports]

    def column(name: str, key: str) -> list[float | None]:
        return [model[name][key] for model in models]

    summary: dict[str, Any] = {}
    # H1: readout floor under each readout choice and jointly.
    summary["h1_readout"] = {
        variant: {
            **tally([per_dof(report["single_by_readout"][variant]) for report in reports]),
            "T_us": span([report["single_by_readout"][variant]["params"]["T_us"] for report in reports]),
        }
        for variant in ("opening", "closing", "mean", "interpolated")
    }
    summary["h1_readout"]["joint"] = {
        **tally([per_dof(report["single_joint"]) for report in reports]),
        "T_us": span([report["single_joint"]["params"]["T_us"] for report in reports]),
    }
    # H2: units, execution time and a common stretched exponent.
    summary["h2_delay"] = {
        "waits_consistent": {str(k): v for k, v in sorted(series["waits_consistent"].items())},
        "execution": execution_slope(series["t1"]),
        "amplitude_model": tally(column("single_amplitude", "chi_square_per_dof")),
        "stretched_model": tally(column("stretched", "chi_square_per_dof")),
        "common_exponent": exponent,
        "exponent_spread": span([m["stretched"]["params"]["exponent"] for m in models]),
        "offset_model": tally(column("delay_offset", "chi_square_per_dof")),
        "common_offset": offset,
        "offset_us": span([m["delay_offset"]["params"]["t0_us"] for m in models]),
        "offset_T_us": span([m["delay_offset"]["params"]["T_us"] for m in models]),
        "offset_aicc_gain_over_4": sum(
            m["delay_offset"]["aicc"] is not None and m["delay_offset"]["aicc"] - m["single"]["aicc"] < -4
            for m in models
        ),
    }
    # H3: two-scale models against the single exponential on the mean pair.
    h3: dict[str, Any] = {}
    for name in ("plateau", "stretched", "biexponential"):
        d_aicc = [(m[name]["aicc"] - m["single"]["aicc"]) if m[name]["aicc"] is not None else None for m in models]
        d_bic = [m[name]["bic"] - m["single"]["bic"] for m in models]
        h3[name] = {
            **tally(column(name, "chi_square_per_dof")),
            "aicc_gain_over_4": sum(value is not None and value < -4 for value in d_aicc),
            "aicc_gain_under_2": sum(value is None or value > -2 for value in d_aicc),
            "bic_better": sum(value < 0 for value in d_bic),
            "delta_aicc_median": statistics.median([v for v in d_aicc if v is not None])
            if any(v is not None for v in d_aicc)
            else None,
            "delta_bic_median": statistics.median(d_bic),
        }
    h3["plateau"]["plateau_fraction"] = span([m["plateau"]["params"]["plateau"] for m in models])
    h3["plateau"]["T_us"] = span([m["plateau"]["params"]["T_us"] for m in models])
    h3["biexponential"]["slow_weight"] = span([m["biexponential"]["params"]["slow_weight"] for m in models])
    h3["biexponential"]["T_fast_us"] = span([m["biexponential"]["params"]["T_fast_us"] for m in models])
    h3["biexponential"]["slow_over_fast"] = span([m["biexponential"]["params"]["slow_over_fast"] for m in models])
    h3["biexponential"]["slow_scale_open_above"] = sum(
        m["biexponential"]["interval"]["slow_over_fast"][1] is None for m in models
    )
    h3["biexponential"]["slow_scale_lower_bound_above_one"] = sum(
        (m["biexponential"]["interval"]["slow_over_fast"][0] or 0.0) > 1.0 for m in models
    )
    h3["single"] = {
        **tally(column("single", "chi_square_per_dof")),
        "T_us": span([m["single"]["params"]["T_us"] for m in models]),
    }
    best = [
        min((name for name in qi_decay_models.MODELS if m[name]["aicc"] is not None), key=lambda n: m[n]["aicc"])
        for m in models
    ]
    h3["best_by_aicc"] = {name: best.count(name) for name in sorted(set(best))}
    summary["h3_two_rate"] = h3
    # H6 (exploratory): a lognormal distribution of T1 inside one job.
    h6_aicc = [m["lognormal"]["aicc"] - m["single"]["aicc"] for m in models]
    summary["h6_t1_distribution"] = {
        **tally(column("lognormal", "chi_square_per_dof")),
        "aicc_gain_over_4": sum(value < -4 for value in h6_aicc),
        "delta_aicc_median": statistics.median(h6_aicc),
        "sigma": span([m["lognormal"]["params"]["sigma"] for m in models]),
        "T_us": span([m["lognormal"]["params"]["T_us"] for m in models]),
    }
    # Descriptive residual signs of the single exponential at each delay (not a registered test).
    residuals = [report["single_residual_z"] for report in reports]
    signs = []
    for index, cycles in enumerate(w["cycles"] for w in series["t1"]):
        column_z = [row[index] for row in residuals]
        positive = sum(value > 0 for value in column_z)
        signs.append(
            {
                "cycles": cycles,
                "positive": positive,
                "qubits": len(column_z),
                "median_z": statistics.median(column_z),
                "sign_test_p": float(stats.binomtest(positive, len(column_z), 0.5).pvalue),
            }
        )
    summary["residual_signs"] = signs
    # H4: drift, interpolation and the batch step.
    steps = [m["single_step"]["params"]["batch_step"] for m in models]
    lr = [m["single"]["deviance"] - m["single_step"]["deviance"] for m in models]
    drifts = [
        max(
            abs(series["readouts"][-1]["zero"][q] - series["readouts"][0]["zero"][q]),
            abs(series["readouts"][-1]["one"][q] - series["readouts"][0]["one"][q]),
        )
        for q in chosen
    ]
    summary["h4_drift"] = {
        "interpolated": summary["h1_readout"]["interpolated"],
        "readout_drift": span(drifts),
        "batch_step": span(steps),
        "step_lr_over_4": sum(value > 4.0 for value in lr),
        "step_positive": sum(value > 0 for value in steps),
        "step_model": tally(column("single_step", "chi_square_per_dof")),
        "job_gap_s": {
            "opening_to_last_t1": series["t1"][-1]["time_s"] - series["readouts"][0]["time_s"],
            "last_t1_to_closing": series["readouts"][-1]["time_s"] - series["t1"][-1]["time_s"],
        },
    }
    # H5: tail residual against the coupling map, and the joint shot records.
    degree = [sum(q in edge for edge in edges) for q in chosen]
    z = [report["tail_residual"]["z"] for report in reports]
    neighbor = []
    for q in chosen:
        near = [b if a == q else a for a, b in edges if q in (a, b) and (b if a == q else a) in chosen]
        neighbor.append(statistics.fmean(z[chosen.index(n)] for n in near) if near else float("nan"))
    valid = [i for i, value in enumerate(neighbor) if not math.isnan(value)]
    rho_degree = stats.spearmanr(degree, z)
    rho_neighbor = stats.spearmanr([z[i] for i in valid], [neighbor[i] for i in valid])
    records = shot_records(series, edges)
    summary["h5_crosstalk"] = {
        "tail_z": span(z),
        "spearman_degree": {"rho": float(rho_degree.statistic), "p": float(rho_degree.pvalue)},
        "spearman_neighbor_mean": {"rho": float(rho_neighbor.statistic), "p": float(rho_neighbor.pvalue)},
        "shot_records": records,
    }
    # Standard-error mechanism.
    mechanism: list[dict[str, Any]] = []
    if retained is not None:
        by_qubit = {row["qubit"]: row for row in retained["qubits"] if "t1" in row}
        for report in reports:
            row = by_qubit.get(report["qubit"])
            if row is None:
                continue
            t1 = row["t1"]
            scale = math.sqrt(max(1.0, t1["chi_square"] / t1["freedom"]))
            se = t1["us_se"]
            scaled_se = None if se is None else se * scale
            alternatives = {
                variant: report["single_by_readout"][variant]["params"]["T_us"]
                for variant in report["single_by_readout"]
            }
            alternatives["joint"] = report["single_joint"]["params"]["T_us"]
            alternatives["retained_log_fit"] = t1["us"]
            values = list(alternatives.values())
            mechanism.append(
                {
                    "qubit": report["qubit"],
                    "retained_T1_us": t1["us"],
                    "retained_se_us": t1["us_se"],
                    "retained_chi_square_per_dof": t1["chi_square"] / t1["freedom"],
                    "se_scale": scale,
                    "scaled_se_us": scaled_se,
                    "refit_T1_us": alternatives,
                    "spread_us": max(values) - min(values),
                    "spread_over_scaled_se": None if scaled_se is None else (max(values) - min(values)) / scaled_se,
                    "refit_over_retained": alternatives["mean"] / t1["us"],
                }
            )
        scaled = [row["scaled_se_us"] for row in mechanism if row["scaled_se_us"] is not None]
        ratios = [row["spread_over_scaled_se"] for row in mechanism if row["spread_over_scaled_se"] is not None]
        summary["standard_error"] = {
            "qubits": len(mechanism),
            "spread_exceeds_scaled_se": sum(ratio > 1.0 for ratio in ratios),
            "se_scale": span([row["se_scale"] for row in mechanism]),
            "scaled_se_us": span(scaled) if scaled else None,
        }
    return {
        "schema": SCHEMA,
        "runs": [run.name for run in runs],
        "nqubits": series["nqubits"],
        "delays_cycles": [row["cycles"] for row in series["t1"]],
        "decision_limit_chi_square_per_dof": CHI_SQUARE_PER_DOF_LIMIT,
        "coupling_edges": [list(edge) for edge in edges],
        "summary": summary,
        "standard_error_rows": mechanism,
        "qubits": reports,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("out", type=Path)
    parser.add_argument("runs", nargs="+", type=Path)
    parser.add_argument("--retained-analysis", type=Path, default=RETAINED_ANALYSIS)
    parser.add_argument("--catalogue", type=Path, default=CATALOGUE)
    args = parser.parse_args(argv)
    retained = (
        json.loads(args.retained_analysis.read_text(encoding="utf-8")) if args.retained_analysis.is_file() else None
    )
    found = analyze(args.runs, retained, coupling_edges(args.catalogue))
    args.out.write_text(json.dumps(found, indent=1, allow_nan=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
