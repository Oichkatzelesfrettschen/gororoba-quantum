"""Model contrasts of the draft follow-up arms under exact pulses, a q12 phase and a coupler 8-12 phase.

Mean selector contrast and d2 split at the retention where the exact center reads visibility 0.42 through the mean
bracket matrix of the retained series. Worlds: exact pulses; a phase of -0.18 rad before each q12 pulse; a
conditional phase of -0.25 rad on coupler 8-12. Arms: q4's pulses at k steps of 5 degrees; Rz(phi) before each q12
pulse; Rz(phi) on q8 after each CZ of coupler 8-12."""

import json

import scan_fits
from scan_forward import HERE

import parallel

LABELS = {"exact": "exact", "q12_phase": "z12 -0.18", "coupler_8_12_phase": "cz(8,12) -0.25"}


def main() -> None:
    names = list(scan_fits.FIXED_WORLDS)
    rows = parallel.ordered_map(scan_fits.followup_world, names, min_items=2)
    out = {LABELS[name]: row for name, row in zip(names, rows, strict=True)}
    for label, row in out.items():
        print(label)
        for key, arms in row.items():
            print(f"  {key} degrees -> (contrast, d2_split):", arms)
    retention = scan_fits.mean_setup()[2]
    (HERE / "followup_predictions.json").write_text(
        json.dumps({"retention": retention, "worlds": out}, indent=1) + "\n"
    )


if __name__ == "__main__":
    main()
