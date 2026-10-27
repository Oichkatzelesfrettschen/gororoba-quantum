"""Sizing replay of the measurement-sequence successor's analysis over the retained envelope run.

The run holds no carryover reader members and no equilibrium row, so those two gates are reported as not evaluable.
Everything else the successor's analysis (gororoba_quantum/msq_successor_analysis.py) evaluates on the retained
counts: the gamma-rate fit at q = 1 and the admission gate at 0.01 / W, the per-qubit residuals and settle gaps, the
settle veto over the qubits that pass the retained execution-time eligibility and pattern screens, the shape
systematic over the layout, the departure and count rule, and the order sentinel on the N = 4 and N = 8 delay rows of
the run's raw shot-ordered bits (rows of consecutive delay-arm members).

``--out FILE`` writes the result; ``--check FILE`` recomputes it and requires the retained bytes. No result here is a
preregistered verdict.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from msq_envelope_raw_diagnostics import load  # noqa: E402

import measurement_sequence_analysis as msa  # noqa: E402
import msq_envelope_analysis as ea  # noqa: E402
import msq_successor_analysis as su  # noqa: E402

SCHEMA = "msq-successor-replay-v1"
# Consecutive delay-arm member rows whose order the sentinel reads, by step count N.
SENTINEL_ROWS = {"n4": (8, 9, 10, 11), "n8": (12, 13, 14, 15)}
# The replay's shape domain: the bound is largest at the smallest shape, and three shapes keep the replay within the
# pull-request gate budget.
SHAPE_SHAPES = (0.25, 1.0, 4.0)
NOT_EVALUABLE = {
    "carryover_readers": "the retained run holds no reader members",
    "equilibrium_row": "the retained run holds no ground-start 400 us row",
}


def median(values: list[float]) -> float:
    return float(np.median(values))


def member_counts(loaded: dict[str, Any]) -> dict[int, dict[str, Any]]:
    """Whole-shot final-bit counts per msq_ member and layout qubit, from the raw shot-ordered bits."""
    bits, members, qubits = loaded["bits"], loaded["members"], loaded["qubits"]
    shots = int(bits.shape[2])
    out: dict[int, dict[str, Any]] = {q: {"final": {}} for q in qubits}
    for row, member in enumerate(members):
        if not member.startswith("msq_"):
            continue
        for g, qubit in enumerate(qubits):
            out[qubit]["final"][f"{member}_q{qubit}"] = (int(bits[row, g].sum()), shots)
    return out


def qubit_summary(row: dict[str, Any], selected: set[int]) -> dict[str, Any]:
    if not row["usable"]:
        return {"usable": False, "reason": row["reason"]}
    top = str(msa.TOP_STEPS)
    fitted = row["fitted"]
    return {
        "usable": True,
        "informative": row["informative"],
        "informative_before_admission": row["informative_before_admission"],
        "uninformative_reason": row["uninformative_reason"],
        "t1_us": fitted["t1_s"] * 1e6,
        "shape": fitted["shape"],
        "chi2": fitted["chi2"],
        "p_value": fitted["p_value"],
        "admitted": row["admission"]["passes"],
        "measure_residual_n16": row["p0"]["measure"][top]["measured_minus_modeled"],
        "unitary_residual_n16": row["p0"]["unitary"][top]["measured_minus_modeled"],
        "delay_residual_n16": row["p0"]["delay"][top]["measured_minus_modeled"],
        "departure_z": row["decisions"]["departure"]["z"],
        "departure_outcome": row["decisions"]["departure"]["outcome"],
        "settle_gap": row["settle_n16"]["gap_difference"],
        "settle_gap_se": row["settle_n16"]["se"],
        "selected": row["qubit"] in selected,
    }


def sentinel(loaded: dict[str, Any]) -> dict[str, Any]:
    bits = loaded["bits"]
    result: dict[str, Any] = {"pairs": {}, "pooled": {}}
    every = []
    for label, rows in SENTINEL_ROWS.items():
        pairs = [(bits[k - 1], bits[k]) for k in rows[1:]]
        every.extend(pairs)
        for k, pair in zip(rows[1:], pairs, strict=True):
            result["pairs"][f"{loaded['members'][k - 1]}->{loaded['members'][k]}"] = su.order_sentinel([pair])
        result["pooled"][label] = su.order_sentinel(pairs)
    result["pooled"]["all"] = su.order_sentinel(every)
    return result


def run(path: Path) -> dict[str, Any]:
    loaded = load(path)
    record, qubits = loaded["record"], loaded["qubits"]
    collected = json.loads((path / "collect.json").read_text())
    executed: dict[str, Any] = {}
    for entry in collected[1:]:
        executed.update(entry["executed"])
    screens = collected[0]["family_analysis"]["envelope"]["screens"]
    floor, reason = msa.bound_floor(msa.record_backends(record))
    if floor is None:
        raise SystemExit(f"no scatter floor: {reason}")
    width = int(record["family_configuration"]["layout_width"])
    contexts = msa.contexts_from_record(record, executed)
    rows = su.analyze_members(member_counts(loaded), contexts, floor, width)
    eligible = [
        q for q in qubits if screens[str(q)]["execution_eligibility"] is None and screens[str(q)]["patterns"]["passes"]
    ]
    count = ea.count_rule(width)
    live = [q for q in qubits if rows[q]["usable"]]
    pool = [q for q in eligible if rows[q]["informative"]]
    domain = su.shape_systematic({"contexts": {q: contexts[q] for q in pool}, "shapes": SHAPE_SHAPES})
    at_calibrated = su.shape_systematic(
        {
            "contexts": {q: contexts[q] for q in pool},
            "shapes": SHAPE_SHAPES[:1],
            "t_factor": 1.0,
            "t_points": 1,
            "t_scope": "qubit",
        }
    )
    decision = su.device_decision(rows, eligible, count, domain["bound"])
    selected = set(decision["selected"])
    informative = [q for q in live if rows[q]["informative_before_admission"]]
    admitted = [q for q in informative if rows[q]["admission"]["passes"]]
    top = str(msa.TOP_STEPS)

    def medians(arm: str, among: list[int]) -> float:
        return median([rows[q]["p0"][arm][top]["measured_minus_modeled"] for q in among])

    summary = {
        "layout_width": width,
        "informative_before_admission": len(informative),
        "admitted": len(admitted),
        "admission_threshold": su.ADMISSION_ALPHA / width,
        "exponential_edge": sum(1 for q in admitted if rows[q]["fitted"]["exponential_edge"]),
        "median_shape_admitted": median(
            [rows[q]["fitted"]["shape"] for q in admitted if rows[q]["fitted"]["shape"] is not None]
        ),
        "median_measure_residual_n16": medians("measure", admitted),
        "median_unitary_residual_n16": medians("unitary", admitted),
        "median_delay_residual_n16": medians("delay", admitted),
        "median_settle_gap": median([rows[q]["settle_n16"]["gap_difference"] for q in admitted]),
        "eligible": len(eligible),
        "selected": len(selected),
    }
    return {
        "schema": SCHEMA,
        "run": path.relative_to(ROOT).as_posix(),
        "job_id": loaded["job_id"],
        "scatter_floor": floor,
        "summary": summary,
        "shape_systematic": domain,
        "shape_systematic_at_calibrated_t1": at_calibrated,
        "decision": decision,
        "not_evaluable": NOT_EVALUABLE,
        "order_sentinel": sentinel(loaded),
        "per_qubit": {str(q): qubit_summary(rows[q], selected) for q in qubits},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run", type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    args = parser.parse_args(argv)
    text = json.dumps(run(args.run.resolve()), indent=1, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text)
        return 0
    if args.check.read_text() != text:
        raise SystemExit(f"{args.check} differs from the recomputed replay")
    print(f"{args.check}: reproduced")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
