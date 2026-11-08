"""D2: the ibm_marrakesh +0.045 N_hat offset of the 1-CZ null blocks on ibm_fez and ibm_kingston, and the cause it selects.

Falsifier, fixed before the numbers: the offset recurs when the readout-corrected N_hat of any 1-CZ null block (k4, k8,
k12) has a mean above +0.02 over the placements; it is absent where every mean lies within +-0.02 with a 95 percent
half-width at most 0.02. The cause follows the written case's signature table through select_rows below: the odd part O
of the null operand's N_hat tests the readout channel after the X (the model's O is the calibrated asymmetry), the even
part E tests acts before the X (relaxation, residual excitation, coherent error, crosstalk), a nonzero within-arm
repeat marks position or drift, and a positive k0 selector contrast with 1-CZ blocks at zero marks an sx over-rotation.
The sensitivity block drops placements whose paired O difference or paired E difference lies beyond 3.5 robust sigma
(median and 1.4826 MAD, Iglewicz-Hoaglin) and is exploratory. The drift block separates a calibration change between
the dry run and the run from a real shortfall: the odd part of the ideal laws pushed through the executed confusion
matrices alone is the calibrated asymmetry at the executed calibration; if it matches the dry-run model's O, the
dry-run calibration did not drift, and a measured shortfall against it is not drift.
"""

import math

import numpy as np
from d_data import analysis
from scipy import stats

OFFSET_MARRAKESH = 0.045
BAND = 0.02
ODD_BAND = 0.04
EVEN_BAND = 0.03
OUTLIER_Z = 3.5


def select_rows(rules: dict) -> list[str]:
    """Signature-table rows the readings support, from the rule verdicts of one backend."""
    rows: list[str] = []
    odd, even = rules["offset_odd"], rules["offset_even"]
    if odd["literal_pass"]:
        rows.append(
            "readout asymmetry after the X at the calibrated size (O within the model's band"
            + ("" if odd["resolves_band"] else "; the interval half-width exceeds the band, so unresolved")
            + ")"
        )
    elif odd["paired_mean"] < 0:
        rows.append("readout asymmetry after the X below the calibrated size (O under the model's band)")
    else:
        rows.append("readout asymmetry after the X above the calibrated size (O over the model's band)")
    if even["literal_pass"]:
        rows.append(
            "relaxation and residual excitation at the model's size (E within the model's band"
            + ("" if even["resolves_band"] else "; the interval half-width exceeds the band, so unresolved")
            + ")"
        )
    elif even["paired_mean"] > 0:
        rows.append("even excess before the X: relaxation, residual excitation, coherent CZ error or crosstalk")
    else:
        rows.append("even deficit before the X: the model overpredicts relaxation")
    if any(not q["literal_pass"] for q in rules["within_arm_repeats"]["quantities"].values()):
        rows.append("position or drift between PUBs (a within-arm repeat departs from zero)")
    if rules["null_selector_contrast"]["sx_overrotation_signature"]:
        rows.append("coherent sx over-rotation (k0 selector contrast above 0.006, 1-CZ blocks at zero)")
    return rows


def robust_keep(values: np.ndarray) -> np.ndarray:
    scale = 1.4826 * np.median(np.abs(values - np.median(values)))
    return np.abs(values - np.median(values)) <= OUTLIER_Z * scale


def interval(values: np.ndarray) -> str:
    n = values.size
    se = values.std(ddof=1) / math.sqrt(n)
    half = stats.t.ppf(0.975, n - 1) * se
    return f"{values.mean():+.4f} +- {se:.4f} (95 percent [{values.mean() - half:+.4f}, {values.mean() + half:+.4f}])"


print(
    f"falsifier: a 1-CZ null block with a readout-corrected N_hat mean above +{BAND} reproduces the +{OFFSET_MARRAKESH} offset"
)
for backend, body in analysis()["backends"].items():
    rules = body["rules"]
    print(f"== {backend}: {body['placements']} placements, {body['shots_per_member']} shots per member")
    blocks = rules["null_nhat_per_placement"]["blocks"]
    for k in ("k0", "k4", "k8", "k12"):
        b = blocks[k]
        extra = (
            f"; rule {b['verdict']} (band {b['band']}, half-width resolves band {b['resolves_band']})"
            if "verdict" in b
            else ""
        )
        print(
            f"  {k:3s} raw {b['raw_mean']:+.4f}  corrected {b['corrected_mean']:+.4f} +- {b['corrected_se']:.4f}  "
            f"flip twin corrected {b['flip_corrected_mean']:+.4f} +- {b['flip_corrected_se']:.4f}{extra}"
        )
    ones = [blocks[k] for k in ("k4", "k8", "k12")]
    above = [k for k in ("k4", "k8", "k12") if blocks[k]["corrected_mean"] > BAND]
    print(
        f"  1-CZ corrected mean {np.mean([b['corrected_mean'] for b in ones]):+.4f}; blocks above +{BAND}: {above or 'none'}; "
        f"the 95 percent interval of k4 holds +{OFFSET_MARRAKESH}: "
        f"{blocks['k4']['corrected_interval'][0] <= OFFSET_MARRAKESH <= blocks['k4']['corrected_interval'][1]}"
    )
    z = [(OFFSET_MARRAKESH - blocks[k]["corrected_mean"]) / blocks[k]["corrected_se"] for k in ("k4", "k8", "k12")]
    print(
        f"  1-CZ mean minus k0 corrected {np.mean([b['corrected_mean'] for b in ones]) - blocks['k0']['corrected_mean']:+.4f}; "
        f"distance of k4, k8, k12 from +{OFFSET_MARRAKESH} in standard errors: {z[0]:.1f}, {z[1]:.1f}, {z[2]:.1f}"
    )
    for name in ("offset_odd", "offset_even"):
        r = rules[name]
        print(
            f"  {name}: measured {r['measured_mean']:+.4f}, model {r['model_mean']:+.4f}, paired {r['paired_mean']:+.4f} +- "
            f"{r['paired_se']:.4f}, band {r['band']}, {r['verdict']}"
        )
    spread = rules["offset_spread"]
    print(
        f"  O spread: slope {spread['slope']:+.3f} (95 percent [{spread['slope_interval_95'][0]:+.2f}, "
        f"{spread['slope_interval_95'][1]:+.2f}]), R squared {spread['r_squared']:.3f}, {spread['verdict']}"
    )
    for name, r in rules["within_arm_repeats"]["quantities"].items():
        print(f"  within-arm {name}: {r['mean']:+.4f} +- {r['se']:.4f}, {r['verdict']}")
    drift = body["calibration_drift_check"]
    per_o = body["per_placement"]
    for label, key in (
        ("measured", "measured_minus_readout_only_odd"),
        ("dry-run model", "model_minus_readout_only_odd"),
    ):
        v = drift[key]
        print(f"  odd part, {label} minus readout-only at the executed calibration: {v['mean']:+.4f} +- {v['se']:.4f}")
    print(
        f"  readout-only O at the executed calibration {np.mean(per_o['o_readout_only']):+.4f}, "
        f"dry-run model O {np.mean(per_o['o_model']):+.4f}, measured O {np.mean(per_o['o_measured']):+.4f}"
    )
    print("  signature rows selected:")
    for row in select_rows(rules):
        print(f"    - {row}")
    per = body["per_placement"]
    o_diff = np.array(per["o_measured"]) - np.array(per["o_model"])
    e_diff = np.array(per["e_measured"]) - np.array(per["e_model"])
    keep = robust_keep(o_diff) & robust_keep(e_diff)
    dropped = [int(i) for i in np.flatnonzero(~keep)]
    print(f"  sensitivity (exploratory): placements dropped {dropped or 'none'}")
    print(f"    paired O all {interval(o_diff)}; kept {interval(o_diff[keep])}")
    print(f"    paired E all {interval(e_diff)}; kept {interval(e_diff[keep])}")
    shortfall = np.array(per["o_measured"]) - np.array(per["o_readout_only"])
    print(f"    paired O against the executed-calibration readout-only O, kept: {interval(shortfall[keep])}")
    slope = stats.linregress(np.array(per["o_model"])[keep], np.array(per["o_measured"])[keep])
    print(f"    O on model O, kept: slope {slope.slope:+.3f} +- {slope.stderr:.3f}, R squared {slope.rvalue**2:.3f}")
verdicts = {
    backend: all(
        body["rules"]["null_nhat_per_placement"]["blocks"][k]["corrected_interval"][1] < OFFSET_MARRAKESH
        for k in ("k4", "k8", "k12")
    )
    for backend, body in analysis()["backends"].items()
}
print(f"interval of every 1-CZ block excludes +{OFFSET_MARRAKESH}: {verdicts}")
print(
    "hypothesis: the corrected 1-CZ offset is device-specific; a backend whose three intervals exclude +0.045 does not carry it, "
    "and a backend whose intervals span it is unresolved at this precision"
)
