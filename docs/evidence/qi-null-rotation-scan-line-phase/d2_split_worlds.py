"""Exploratory: the retained d2 splits of the 24 scan arms against three worlds at fixed parameters.

Worlds: exact pulses; a phase of -0.18 rad before each q12 pulse; a conditional phase of -0.25 rad on coupler
8-12 (the shared-parameter values of widened_worlds.py, fitted to the selector contrasts alone). Each batch takes
the contraction (share 0) at which the world's center arm reads the batch's center visibility through its
bracket matrix. Statistic: chi-square of the 24 d2 splits, which no fit here used, with their binomial errors."""

import json

import scan_fits
from scan_forward import HERE

import parallel


def main() -> None:
    names = list(scan_fits.FIXED_WORLDS)
    out = dict(zip(names, parallel.ordered_map(scan_fits.d2_split_world, names, min_items=2), strict=True))
    for name, row in out.items():
        print(name, row["chi2_24"])
    (HERE / "d2_split_worlds.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
