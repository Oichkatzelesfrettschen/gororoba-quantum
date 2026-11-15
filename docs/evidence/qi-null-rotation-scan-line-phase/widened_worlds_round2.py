"""Exploratory: phases tied to CZ gates, scored with one parameter per batch.

Written before fitting: a z rotation on one qubit after each CZ it takes part in (all its couplers, or one coupler),
beside the exact circuit, the phase before each q12 pulse or every pulse, and the conditional phase on every CZ or
on coupler 8-12. The statistic adds per-batch parameters (16 degrees of freedom, 0.001 point 39.25)."""

import json
from typing import Any

import scan_fits
from scan_forward import HERE, pairs, region

import parallel

KEYS = (
    "cand",
    "mix",
    "theta_fwd",
    "chi_fwd",
    "chi_mirror_at_fwd",
    "theta_all",
    "chi_all",
    "chi_per_batch_param",
    "params",
    "per",
)


def main() -> None:
    cands: list[tuple[Any, Any, Any]] = [scan_fits.NONE, ("pulse", "zb", None), ("pulse", "zb", 12)]
    cands += (
        [("cz", None, None), ("cz", (8, 12), None)]
        + [("czz", q, None) for q in region]
        + [("czz", q, p) for p in pairs for q in p]
    )
    items = [(cand, 0.0) for cand in cands]
    rows = [{k: row[k] for k in KEYS} for row in parallel.ordered_map(scan_fits.single_world, items, min_items=2)]
    rows.sort(key=lambda r: r["chi_per_batch_param"])
    for r in rows[:25]:
        print(r)
    print("exact:", [r for r in rows if "none" in r["cand"]])
    (HERE / "widened_worlds_round2.json").write_text(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
