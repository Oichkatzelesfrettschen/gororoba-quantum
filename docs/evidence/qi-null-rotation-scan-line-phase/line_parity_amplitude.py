"""Exploratory: line amplitude of the selector-coin parity bit of every data job, with no phase reference.

The parity bit (selector read value xor coin read value) has mean near 1/2 + contrast/2, so a selector contrast
that oscillates with amplitude h shows as a line of amplitude near h/2 on the bit. Statistic per job: the largest
amplitude 2 |sum x exp(-2 pi i f n)| / N over a grid of 201 frequencies in the line band (0.02008 to 0.02016 cycles
per shot), the same maximum in an off-line band of equal width (0.02350 to 0.02358) as the null of a maximum over
that grid, and the same pair for q4's bit, which the phase folds use as their reference. Written before computing:
an arm whose folded harmonic is small because its q4 reference is lost shows a parity line above the off-line
maximum; an arm without the oscillation shows none."""

import json

import line_fold
import numpy as np
from scan_forward import HERE

import parallel

KEYS = ("parity_line", "parity_off_line", "q4_line", "q4_off_line")


def main() -> None:
    rows = parallel.ordered_map(line_fold.parity_job, line_fold.data_jobs(), min_items=2)
    summary = {}
    for arm in sorted({r["arm"] for r in rows}):
        v = [r for r in rows if r["arm"] == arm]
        summary[arm] = {"jobs": len(v)} | {k: float(np.mean([r[k] for r in v])) for k in KEYS}
        print(arm.ljust(15), {k: round(x, 4) if isinstance(x, float) else x for k, x in summary[arm].items()})
    (HERE / "line_parity_amplitude.json").write_text(json.dumps({"jobs": rows, "per_arm": summary}, indent=1) + "\n")


if __name__ == "__main__":
    main()
