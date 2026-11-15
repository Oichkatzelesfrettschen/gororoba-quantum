"""Exploratory: two error parameters driven by one line phase, fitted to the phase-bin contrasts.

Written before fitting: one line drives two error parameters with a common phase, a = a0 + s Aa cos(theta) and
b = b0 + s Ab cos(theta) (Ab of either sign), s per arm chosen so that the model's q4 P(1) is largest at theta = 0,
and by the lower contrast score where the two alignments give the same q4 harmonic (`free_alignment_arms`).
Pairs: (z on q4 pulses, z on q12 pulses), (cz phase 4-8, z on q12), (z on q4, cz phase 8-12), (cz phase 4-8, cz
phase 8-12), (z on q4, z on q8), (z on q8, z on q12). Four shared parameters; falsifier: chi-square of the 72
contrast points (9 `Rx` arm types) above 109.8 (upper tail 0.001, 68 degrees of freedom)."""

import json

import scan_fits
from scan_forward import HERE

import parallel

PAIRS = [
    (("pulse", "zb", 4), ("pulse", "zb", 12)),
    (("cz", (4, 8), None), ("pulse", "zb", 12)),
    (("pulse", "zb", 4), ("cz", (8, 12), None)),
    (("cz", (4, 8), None), ("cz", (8, 12), None)),
    (("pulse", "zb", 4), ("pulse", "zb", 8)),
    (("pulse", "zb", 8), ("pulse", "zb", 12)),
]


def main() -> None:
    out = parallel.ordered_map(scan_fits.phase_pair, PAIRS, min_items=2)
    for row in out:
        print({k: v for k, v in row.items() if k != "pred"})
    out.sort(key=lambda r: r["total"])
    print("BEST", out[0]["A"], out[0]["B"])
    (HERE / "phase_resolved_two_source.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
