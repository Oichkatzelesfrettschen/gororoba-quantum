"""Exploratory: one global parameter per elementary error, fitted to all 24 scan arms at matched center visibility.

Written before fitting. Candidates: a constant rotation about x, y or z before or after every pulse of one region
qubit or of all; a constant conditional-phase error on every CZ or on the CZs of one coupler; none (exact). Statistic:
chi-square of the 24 raw selector contrasts of the eight scan batches with one parameter shared by all batches and a
contraction (share 0 or 1) matched to each batch's center visibility. Split: fit on the forward round (batches 01 to
07), score on the mirror round (13 to 19) with the parameter fixed. Falsifier of a candidate: mirror chi-square above
the 0.001 point of chi-square with 12 degrees of freedom (32.9)."""

import json
from typing import Any

import scan_fits
from scan_forward import HERE, pairs, region

import parallel

KEYS = ("cand", "mix", "theta_fwd", "chi_fwd", "chi_mirror_at_fwd", "theta_all", "chi_all", "per_batch")


def main() -> None:
    cands: list[tuple[Any, Any, Any]] = [scan_fits.NONE]
    for axis in "xyz":
        for order in "ba":
            if axis == "x" and order == "a":
                continue
            for q in (None, *region):
                cands.append(("pulse", axis + order, q))
    cands += [("cz", None, None)] + [("cz", p, None) for p in pairs]
    items = [(cand, mix) for cand in cands for mix in ((0.0,) if cand[0] == "none" else (0.0, 1.0))]
    rows = [{k: row[k] for k in KEYS} for row in parallel.ordered_map(scan_fits.single_world, items, min_items=2)]
    rows.sort(key=lambda r: r["chi_all"])
    for r in rows[:25]:
        print(r)
    print("exact:", [r for r in rows if "none" in r["cand"]])
    (HERE / "widened_worlds.json").write_text(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
