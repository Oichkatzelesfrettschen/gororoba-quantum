"""Exploratory: Pearson chi-square of all 96 outcome counts per batch under a contraction.

Written before fitting: per batch, the 3 x 32 outcome counts against the model law with one error parameter, one
contraction retention and one contraction share (93 - 3 = 90 degrees of freedom per batch, 720 over eight batches).
Candidates: exact; x, y, z before each single qubit's pulses and before all; conditional phase on all CZs and on
each coupler. A crude noise model inflates every chi-square, so the ranking and the gain over exact carry the
reading."""

import json
from typing import Any

import scan_fits
from scan_forward import HERE, pairs, region

import parallel


def main() -> None:
    cands: list[tuple[Any, Any, Any]] = (
        [scan_fits.NONE]
        + [("pulse", a + "b", q) for a in "xyz" for q in (None, *region)]
        + [("cz", None, None)]
        + [("cz", p, None) for p in pairs]
    )
    rows = parallel.ordered_map(scan_fits.histogram_world, cands, min_items=2)
    rows.sort(key=lambda r: r["chi"])
    print("RANK")
    for r in rows[:10]:
        print(r["cand"], r["chi"], r["per"], r["theta"])
    (HERE / "full_histogram_fit.json").write_text(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
