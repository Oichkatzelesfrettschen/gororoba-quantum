"""Tuna-17 T1 shape: test a level step between the two T1 batches against anchor circuits repeated across batches.

The six T1 delays split over two batches (0, 250, 500 cycles in the first, 1000, 2000, 4000 in the second), so a level
step between the batches acts on the three longest delays only. This script reads the retained counts (no provider
read) and writes one record:

- per qubit, the single exponential, the plateau, the exponential with an additive step on the later batch (2
  parameters), the free-amplitude exponential and the free-amplitude exponential with a step (3 parameters), each a
  binomial-likelihood fit on the mean readout pair with profile intervals (gororoba_quantum/qi_decay_models.py);
- the circuits that repeat byte for byte across batches (found by the sha256 of the circuit text, in at least three
  jobs), with each qubit's count in every job ordered by finish time, the homogeneity of the levels, and the shift of
  the middle level against the time interpolation of the first and last (gororoba_quantum/qi_batch_anchors.py);
- the fitted steps against the anchor shift of the prepared-0 circuit, and the tallies registered in the note
  (docs/notes/quantum_inspire/tuna17-characterization-2026-11-16.md, "Batch-offset test registered before its last
  two pieces ran").

Usage: "$PYTHON" scripts/qi_tuna17_batch_step.py OUT RUN_DIR... [--catalogue PATH]
OUT is the analysis record; RUN_DIR are the run directories of the series in submission order. The interpreter is the
analysis one (numpy and scipy), not QI_PYTHON.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any

from scipy import stats

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "gororoba_quantum"))
import qi_tuna17_characterization_cases as cases  # noqa: E402
import qi_tuna17_t1_shape as shape  # noqa: E402

import parallel  # noqa: E402
import qi_batch_anchors  # noqa: E402
import qi_decay_models  # noqa: E402

SCHEMA = "qi-tuna17-batch-step-analysis-v1"
LIMIT = shape.CHI_SQUARE_PER_DOF_LIMIT
LARGE_STEP = 0.02
DRIFT_BOUND = 0.015


def anchor_groups(runs: list[Path]) -> list[dict[str, Any]]:
    """Circuits that appear in at least three jobs with one sha256, with each job's counts per qubit and finish time."""
    groups: dict[str, list[dict[str, Any]]] = {}
    for run in runs:
        _, manifest, raw = cases.read_run(run)
        record = json.loads((run / "results.json").read_text(encoding="utf-8"))
        jobs = {entry["file"]: entry for entry in record["jobs"]}
        for name in sorted(raw):
            digest = hashlib.sha256((run / name).read_bytes()).hexdigest()
            shots = len(raw[name])
            fractions = cases.p1(raw[name], manifest["nqubits"])
            groups.setdefault(digest, []).append(
                {
                    "run": run.name,
                    "file": name,
                    "time_s": shape.seconds(jobs[name]["job"]["finished_at"]),
                    "queued_s": shape.seconds(jobs[name]["job"]["queued_at"]),
                    "shots": shots,
                    "ones": [round(value * shots) for value in fractions],
                }
            )
    return [
        {"sha256": digest, "jobs": sorted(members, key=lambda member: member["time_s"])}
        for digest, members in sorted(groups.items())
        if len(members) >= 3
    ]


def prepared_state(group: dict[str, Any]) -> str:
    """The prepared state of an anchor group: 1 when its circuit text holds an X line, else 0."""
    return "one" if any(member["file"].startswith(("readout-1", "t1-0")) for member in group["jobs"]) else "zero"


def qubit_anchor(group: dict[str, Any], qubit: int) -> dict[str, Any]:
    levels = [
        qi_batch_anchors.Level(member["time_s"], member["ones"][qubit], member["shots"]) for member in group["jobs"]
    ]
    return {
        "levels": [
            {"run": member["run"], "file": member["file"], "ones": member["ones"][qubit], "shots": member["shots"]}
            for member in group["jobs"]
        ],
        "homogeneity": qi_batch_anchors.homogeneity(levels),
        "shift": qi_batch_anchors.probe_shift(levels),
    }


def half_width(interval: list[float | None]) -> float | None:
    low, high = interval
    return None if low is None or high is None else (high - low) / 2.0


def compare(step: dict[str, Any], anchor: dict[str, Any], scaled: bool) -> dict[str, float | None]:
    """Fitted step against an anchor shift: difference, combined standard error and z (None when an end is open)."""
    key = "interval_scaled" if scaled else "interval"
    width = half_width(step[key]["batch_step"])
    difference = step["params"]["batch_step"] - anchor["shift"]["shift"]
    if width is None:
        return {"difference": difference, "se": None, "z": None}
    se = math.hypot(width, anchor["shift"]["se"])
    return {"difference": difference, "se": se, "z": difference / se}


def exceeds(row: dict[str, float | None], limit: float) -> bool:
    z = row["z"]
    return z is not None and z > limit


def within(row: dict[str, float | None], limit: float) -> bool:
    z = row["z"]
    return z is not None and abs(z) <= limit


def tally_step(
    reports: list[dict[str, Any]], anchors0: list[dict[str, Any]], anchors1: list[dict[str, Any]]
) -> dict[str, Any]:
    two = [report["models"]["single_step"] for report in reports]
    three = [report["models"]["single_amplitude_step"] for report in reports]
    comparison: dict[str, Any] = {}
    for name, rows in (("two_parameter", two), ("three_parameter", three)):
        nominal = [compare(row, anchor, False) for row, anchor in zip(rows, anchors0, strict=True)]
        widened = [compare(row, anchor, True) for row, anchor in zip(rows, anchors0, strict=True)]
        large = [i for i, row in enumerate(two) if row["params"]["batch_step"] >= LARGE_STEP]
        comparison[name] = {
            "within_2_se": sum(within(c, 2.0) for c in nominal),
            "step_exceeds_by_3_se": sum(exceeds(c, 3.0) for c in nominal),
            "open_interval": sum(c["z"] is None for c in nominal),
            "within_2_se_widened": sum(within(c, 2.0) for c in widened),
            "step_exceeds_by_3_se_widened": sum(exceeds(c, 3.0) for c in widened),
            "large_step_qubits": large,
            "large_step_exceeds_by_3_se": sum(exceeds(nominal[i], 3.0) for i in large),
            "rows": nominal,
        }
    models = [report["models"] for report in reports]
    d_aicc_step_plateau = [
        m["single_step"]["aicc"] - m["plateau"]["aicc"]
        for m in models
        if m["single_step"]["aicc"] is not None and m["plateau"]["aicc"] is not None
    ]
    freedom = {name: models[0][name]["freedom"] for name in qi_decay_models.STEP_BATTERY}
    return {
        "freedom": freedom,
        "two_parameter_step": {
            **shape.tally([shape.per_dof(row) for row in two]),
            "step": shape.span([row["params"]["batch_step"] for row in two]),
            "step_positive": sum(row["params"]["batch_step"] > 0 for row in two),
            "large_step_qubits": [i for i, row in enumerate(two) if row["params"]["batch_step"] >= LARGE_STEP],
        },
        "three_parameter_step": {
            **shape.tally([shape.per_dof(row) for row in three]),
            "step": shape.span([row["params"]["batch_step"] for row in three]),
            "amplitude": shape.span([row["params"]["amplitude"] for row in three]),
            "step_positive": sum(row["params"]["batch_step"] > 0 for row in three),
            "aicc_gain_over_4": sum(
                row["aicc"] is not None and row["aicc"] - m["single"]["aicc"] < -4
                for row, m in zip(three, models, strict=True)
            ),
        },
        "amplitude_only": shape.tally([shape.per_dof(m["single_amplitude"]) for m in models]),
        "step_against_plateau": {
            "step_lower_aicc": sum(value < 0 for value in d_aicc_step_plateau),
            "plateau_lower_aicc": sum(value > 0 for value in d_aicc_step_plateau),
            "delta_aicc_median": statistics.median(d_aicc_step_plateau),
        },
        "anchor_comparison": comparison,
        "anchor_prepared0": anchor_tally(anchors0),
        "anchor_prepared1": anchor_tally(anchors1),
    }


def anchor_tally(anchors: list[dict[str, Any]]) -> dict[str, Any]:
    z = [anchor["shift"]["z"] for anchor in anchors]
    chi = [anchor["homogeneity"]["chi_square"] for anchor in anchors]
    freedom = anchors[0]["homogeneity"]["freedom"]
    positive = sum(anchor["shift"]["shift"] > 0 for anchor in anchors)
    pooled_z2 = sum(value * value for value in z)
    pooled_chi = sum(chi)
    return {
        "qubits": len(anchors),
        "shift": shape.span([anchor["shift"]["shift"] for anchor in anchors]),
        "abs_shift_over_bound": sum(abs(anchor["shift"]["shift"]) > DRIFT_BOUND for anchor in anchors),
        "abs_z_over_2": sum(abs(value) > 2.0 for value in z),
        "abs_z_over_3": sum(abs(value) > 3.0 for value in z),
        "shift_positive": positive,
        "sign_test_p": float(stats.binomtest(positive, len(z), 0.5).pvalue),
        "z_mean": statistics.fmean(z),
        "z_squared_sum": pooled_z2,
        "z_squared_p": float(stats.chi2.sf(pooled_z2, len(z))),
        "homogeneity_chi_square_sum": pooled_chi,
        "homogeneity_freedom": freedom * len(chi),
        "homogeneity_p": float(stats.chi2.sf(pooled_chi, freedom * len(chi))),
        "se": shape.span([anchor["shift"]["se"] for anchor in anchors]),
    }


def analyze(runs: list[Path], qubits: list[int] | None = None) -> dict[str, Any]:
    series = shape.load(runs)
    chosen = qubits if qubits is not None else list(range(series["nqubits"]))
    work = shape.tasks(series, chosen)
    reports = parallel.ordered_map(qi_decay_models.analyze_step, work, min_items=2)
    groups = anchor_groups(runs)
    by_state = {prepared_state(group): group for group in groups}
    if set(by_state) != {"zero", "one"}:
        raise SystemExit("qi_tuna17_batch_step: the runs hold no prepared-0 and prepared-1 circuit repeated in 3 jobs")
    anchors0 = [qubit_anchor(by_state["zero"], q) for q in chosen]
    anchors1 = [qubit_anchor(by_state["one"], q) for q in chosen]
    return {
        "schema": SCHEMA,
        "runs": [run.name for run in runs],
        "nqubits": series["nqubits"],
        "delays_cycles": [row["cycles"] for row in series["t1"]],
        "decision_limit_chi_square_per_dof": LIMIT,
        "anchor_groups": [
            {
                "prepared": prepared_state(group),
                "sha256": group["sha256"],
                "jobs": [
                    {key: member[key] for key in ("run", "file", "queued_s", "time_s", "shots")}
                    for member in group["jobs"]
                ],
            }
            for group in groups
        ],
        "summary": tally_step(reports, anchors0, anchors1),
        "qubits": [
            {"qubit": q, "models": report["models"], "anchor_prepared0": a0, "anchor_prepared1": a1}
            for q, report, a0, a1 in zip(chosen, reports, anchors0, anchors1, strict=True)
        ],
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("out", type=Path)
    parser.add_argument("runs", nargs="+", type=Path)
    args = parser.parse_args(argv)
    found = analyze(args.runs)
    args.out.write_text(json.dumps(found, indent=1, allow_nan=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
