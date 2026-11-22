"""Positional and shot-block reading of the Grover depth arms of the retained Garnet follow-up run.

The readout-corrected 101 depth statistic f = lambda_3 - lambda_2^2 / lambda_1 read -0.121 +- 0.041 against zero
(docs/design/iqm-garnet-grover-depth-sedenion-walsh.md, "Result"). The depth arms k = 2 and 3 are single circuits at
positions 15 and 16 of the 36, and k = 1 pools four copies at 0, 13, 22 and 35, so a response that changes with
position or with time in the job enters f. This script reads, for each Grover arm of both marked states, the raw
marked frequency over its kept shots and over four shot blocks; fits a line in position to the k = 1 copies; recomputes
the raw f with every arm moved to the k = 1 copies' mean position along that line and along the line at three
standard errors of its slope; and tests each depth arm's four shot blocks for equality. It decides nothing: it is
written after the analysis of the run.

Usage: "$PYTHON" docs/evidence/iqm-garnet-grover-positions/positions.py OUT.json
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

from grover_line_analysis import ideal_probability  # noqa: E402

RUN = ROOT / "results/iqm/runs/2026-11-21T220358Z-garnet-grover-depth-sedenion-walsh-grover"
MARKS = ("101", "011")
BLOCKS = 4
ROUND = 5


def read() -> dict[str, dict[str, Any]]:
    cases = json.loads((RUN / "cases.json").read_text(encoding="utf-8"))
    job = next(j for j in cases["jobs"] if j["job"] == "grover")
    shots = json.loads((RUN / "raw/measurements.json").read_text(encoding="utf-8"))
    if len(shots) != len(job["circuits"]):
        raise SystemExit("the retained shots do not match the circuits of the grover job")
    out = {}
    for position, (entry, record) in enumerate(zip(job["circuits"], shots, strict=True)):
        name = Path(entry["file"]).stem
        bits = np.array([[b[0] if isinstance(b, list) else b for b in shot] for shot in record["m"]], dtype=np.int64)
        out[name] = {"position": position, "index": bits @ (1 << np.arange(bits.shape[1]))}
    return out


def marked_index(marked: str) -> int:
    return sum(int(c) << q for q, c in enumerate(marked))


def retention(p: float, k: int) -> float:
    return (p - 1 / 8) / (ideal_probability(k) - 1 / 8)


def f_of(p: dict[int, float]) -> float:
    lam = {k: retention(v, k) for k, v in p.items()}
    return lam[3] - lam[2] ** 2 / lam[1]


def moved(p_raw: dict[int, float], positions: dict[int, int], mean_position: float, slope: float) -> dict[int, float]:
    """The depth arms' frequencies moved along a line in position to the k = 1 copies' mean position."""
    return {k: p - (slope * (positions[k] - mean_position) if k > 1 else 0.0) for k, p in p_raw.items()}


def main(out: Path) -> None:
    circuits = read()
    report: dict[str, Any] = {}
    for marked in MARKS:
        target = marked_index(marked)
        arms = {
            name: c
            for name, c in circuits.items()
            if name == f"m{marked}-k1"
            or name.startswith(f"m{marked}-k1-c")
            or name in (f"m{marked}-k2", f"m{marked}-k3")
        }
        rows = {}
        for name, c in sorted(arms.items(), key=lambda item: item[1]["position"]):
            hits = (c["index"] == target).astype(float)
            blocks = np.array_split(hits, BLOCKS)
            block_p = [float(b.mean()) for b in blocks]
            pooled = float(hits.mean())
            chi2 = sum(len(b) * (bp - pooled) ** 2 for b, bp in zip(blocks, block_p, strict=True)) / max(
                pooled * (1 - pooled), 1e-12
            )
            rows[name] = {
                "position": c["position"],
                "shots": len(hits),
                "p": pooled,
                "block_p": block_p,
                "block_chi2_df3": chi2,
            }
        copies = [r for name, r in rows.items() if "-k1" in name]
        k1_shots = sum(r["shots"] for r in copies)
        p_raw = {
            1: sum(r["p"] * r["shots"] for r in copies) / k1_shots,
            2: rows[f"m{marked}-k2"]["p"],
            3: rows[f"m{marked}-k3"]["p"],
        }
        f_raw = f_of(p_raw)
        report[marked] = {
            "arms": {
                name: {k: (round(v, ROUND) if isinstance(v, float) else v) for k, v in r.items()}
                for name, r in rows.items()
            },
            "raw_f": round(f_raw, ROUND),
        }
        if len(copies) < 2:
            continue
        x = np.array([r["position"] for r in copies], dtype=float)
        y = np.array([r["p"] for r in copies])
        w = np.array([r["shots"] / max(r["p"] * (1 - r["p"]), 1e-12) for r in copies])
        xm = float(np.sum(w * x) / np.sum(w))
        slope = float(np.sum(w * (x - xm) * (y - np.sum(w * y) / np.sum(w))) / np.sum(w * (x - xm) ** 2))
        slope_se = float(1 / math.sqrt(np.sum(w * (x - xm) ** 2)))
        positions = {2: rows[f"m{marked}-k2"]["position"], 3: rows[f"m{marked}-k3"]["position"]}

        report[marked] |= {
            "k1_slope_per_position": round(slope, 6),
            "k1_slope_se": round(slope_se, 6),
            "k1_mean_position": round(xm, 3),
            "raw_f_moved_along_fitted_line": round(f_of(moved(p_raw, positions, xm, slope)), ROUND),
            "raw_f_moved_at_slope_plus_3se": round(f_of(moved(p_raw, positions, xm, slope + 3 * slope_se)), ROUND),
            "raw_f_moved_at_slope_minus_3se": round(f_of(moved(p_raw, positions, xm, slope - 3 * slope_se)), ROUND),
        }
    record = {
        "run": str(RUN.relative_to(ROOT)),
        "definition": (
            "p = raw marked frequency over kept shots; f = lambda_3 - lambda_2^2 / lambda_1 with "
            "lambda_k = (p - 1/8) / (ideal_k - 1/8), raw, without the readout correction; moved: the k = 2 and 3 arms "
            "shifted along a line in "
            "position to the k = 1 copies' mean position; block_chi2_df3: Pearson statistic of the four shot blocks "
            "against their pooled frequency"
        ),
        "marks": report,
        "note": "descriptive reading written after the analysis of the run; it decides nothing",
    }
    out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(Path(sys.argv[1]))
