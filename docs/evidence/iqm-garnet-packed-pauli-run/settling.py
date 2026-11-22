"""Settling of the packed Pauli science response after the all-ones reference, read from the retained Garnet run.

The packed Pauli result (docs/design/iqm-garnet-packed-pauli-response.md, "Open hypotheses") holds that the low
response of the first science circuit after the all-ones reference (circuit-002, pair 0's -229) may be the all-ones
carryover settling over several circuits. Within one shot every circuit of the job runs in order, so a carryover
that settles over circuits is a function of a circuit's place after the reference, the same in early and late shots;
a transient of the device is a function of the shot index. This script reads each science circuit's response (the
bright minus kernel Y-cell score of the analysis, over its shots), subtracts the mean of its dense or sparse arm, and
reports the residual by the number of science circuits since the last all-ones reference, in the first and the second
half of the shots. It decides nothing: it is written after the analysis of the run.

Usage: "$PYTHON" docs/evidence/iqm-garnet-packed-pauli-run/settling.py OUT.json
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import iqm_packed_pauli_case as case  # noqa: E402

import iqm_records  # noqa: E402
from parallel import ordered_map  # noqa: E402

RUN = ROOT / "results/iqm/runs/2026-11-21T220346Z-garnet-packed-pauli-response-garnet-packed"
ROUND = 5


def responses(labels: list[np.ndarray]) -> np.ndarray:
    """Per-shot bright minus kernel Y-cell score, halved as in the analysis's response."""
    return (case.SCORE2[labels[case.BRIGHT_Y]] - case.SCORE2[labels[case.KERNEL_Y]]) / 2


def summary(values: np.ndarray) -> dict[str, float]:
    return {"mean": float(values.mean()), "se": float(values.std(ddof=1) / math.sqrt(len(values)))}


def circuit_summaries(item: tuple[dict[str, Any], dict[str, Any]]) -> dict[str, dict[str, float]]:
    """One science circuit's per-shot response summarized over all shots and over each half."""
    role, result = item
    per_shot = responses([case.shot_labels(result["c"], cell) for cell in range(len(role["cells"]))])
    half = len(per_shot) // 2
    return {"all": summary(per_shot), "first_half": summary(per_shot[:half]), "second_half": summary(per_shot[half:])}


def main(out: Path) -> None:
    run = iqm_records.read_run(RUN)
    prediction = json.loads((RUN / "prediction.json").read_text(encoding="utf-8"))
    roles = prediction["circuits"]
    measurements = run.completed_measurements()
    if len(measurements) != len(roles):
        raise SystemExit("the retained measurements do not match the circuits of the prediction")
    science: list[tuple[int, int | None]] = []
    since: int | None = None
    # A shot runs the playlist in order and the next shot starts over, so the count carries across the wrap.
    for _ in range(2):
        science = []
        for position, role in enumerate(roles):
            if role["kind"] == "reference" and role["reference"] == 1:
                since = 0
                continue
            if role["kind"] != "science":
                continue
            since = None if since is None else since + 1
            science.append((position, since))
    stats = ordered_map(circuit_summaries, [(roles[p], measurements[p]) for p, _ in science])
    rows: list[dict[str, Any]] = [
        {
            "name": roles[position]["name"],
            "position": position,
            "pair": roles[position]["pair"],
            "dense": bool(roles[position]["dense"]),
            "science_since_all_ones": count,
            **summaries,
        }
        for (position, count), summaries in zip(science, stats, strict=True)
    ]
    arm_mean = {d: float(np.mean([r["all"]["mean"] for r in rows if r["dense"] == d])) for d in (True, False)}
    for row in rows:
        for part in ("all", "first_half", "second_half"):
            # The reference is the mean of the same arm's other circuits over the same shots, so the residual is not
            # shrunk by the circuit's own weight in its arm mean.
            others = [r[part]["mean"] for r in rows if r["dense"] == row["dense"] and r is not row]
            reference = float(np.mean(others))
            se = math.sqrt(row[part]["se"] ** 2 + float(np.var(others, ddof=1)) / len(others))
            row[part]["residual"] = row[part]["mean"] - reference
            row[part]["residual_se"] = se
            row[part]["z"] = row[part]["residual"] / se
    by_since: dict[str, Any] = {}
    for since_value in sorted({r["science_since_all_ones"] for r in rows}):
        group = [r for r in rows if r["science_since_all_ones"] == since_value]
        for part in ("all", "first_half", "second_half"):
            residual = float(np.mean([r[part]["residual"] for r in group]))
            se = math.sqrt(sum(r[part]["residual_se"] ** 2 for r in group)) / len(group)
            by_since.setdefault(str(since_value), {})[part] = {
                "circuits": len(group),
                "mean_residual": round(residual, ROUND),
                "se": round(se, ROUND),
                "z": round(residual / se, 2),
            }

    def rounded(value: Any) -> Any:
        if isinstance(value, float):
            return round(value, ROUND)
        if isinstance(value, dict):
            return {k: rounded(v) for k, v in value.items()}
        return value

    record = {
        "run": str(RUN.relative_to(ROOT)),
        "definition": (
            "response = mean over shots of (score(bright Y cell) - score(kernel Y cell)) / 2; residual = response "
            "minus the mean response of the other circuits of its arm over the same shots, z against the combined "
            "error; science_since_all_ones = 1 for the first science circuit after the all-ones reference, counted "
            "across the wrap from one shot to the next"
        ),
        "arm_mean_response": {"dense": round(arm_mean[True], ROUND), "sparse": round(arm_mean[False], ROUND)},
        "by_science_since_all_ones": by_since,
        "circuits": [rounded(r) for r in rows],
        "note": "descriptive reading written after the analysis of the run; it decides nothing",
    }
    out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(Path(sys.argv[1]))
