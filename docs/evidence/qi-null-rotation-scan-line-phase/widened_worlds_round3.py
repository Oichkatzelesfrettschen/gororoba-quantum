"""Exploratory: two-parameter composites of the two leading worlds, forward fit and mirror score.

Written before fitting: pairs A x B with A in {conditional phase on coupler 8-12, phase before each q12 pulse} and
B in the list below; two shared parameters on 24 arms (22 degrees of freedom, 0.001 point 48.27), fitted on the
forward round and scored on the mirror round (12 arms, 32.91)."""

import json

import scan_fits
from scan_forward import HERE

import parallel

FIRST = [("cz", (8, 12), None), ("pulse", "zb", 12)]
SECOND = [
    ("pulse", "zb", 4),
    ("pulse", "yb", 4),
    ("pulse", "xb", 4),
    ("pulse", "xb", 8),
    ("pulse", "zb", 8),
    ("pulse", "yb", 8),
    ("cz", None, None),
    ("cz", (4, 8), None),
    ("pulse", "zb", 2),
    ("pulse", "zb", 11),
    ("czz", 8, (8, 12)),
    ("pulse", "xb", None),
    ("pulse", "xb", 12),
    ("pulse", "yb", 12),
    ("cz", (8, 11), None),
    ("cz", (2, 4), None),
]


def main() -> None:
    items = [(ca, cb) for ca in FIRST for cb in SECOND if ca != cb]
    rows = parallel.ordered_map(scan_fits.pair_world, items, min_items=2)
    rows.sort(key=lambda r: r["chi_all"])
    print("RANK")
    for r in rows[:12]:
        print(
            r["A"],
            r["B"],
            r["chi_all"],
            r["all"],
            "mirror@fwd",
            r["chi_mirror_at_fwd"],
            "vis miss",
            r["max_abs_visibility_miss"],
        )
    (HERE / "widened_worlds_round3.json").write_text(json.dumps(rows, indent=1))


if __name__ == "__main__":
    main()
