"""Two forward models of the same circuits, compared: the phase-scan generator's laws (elementary_error_laws.py through
forward_law) and the histogram-fit model of gate_noise_histogram_fit.py (law), on the case's arms. The models agree
where both name the same mechanism (a z rotation of q12 after each pulse, CZ and pulse damping, in the order the
generator applies them) and differ in scope where they name different ones (the conditional phase delta and the q8
rotation c8 act on every CZ that touches the qubit; the generator's coupler_phase and q8_phase_at_coupler act on
coupler 8-12 alone). Prints one line per comparison and exits 1 when a same-mechanism pair differs by more than
1e-10.

Usage: analyzer_crosscheck.py"""

import sys

import numpy as np

sys.path[:0] = ["scripts", "gororoba_quantum"]
import qi_pathion_null_phase_scan_cases as ps  # noqa: E402
import qi_pathion_null_rotation_scan_cases as rs  # noqa: E402

import gate_noise_histogram_fit as gnf  # noqa: E402

TOLERANCE = 1e-10
ARMS = (ps.CENTER, "b0-rxz-z12-p30", "b0-rxz-z12-m10", "b0-rxz-z8c-p10", "b0-rxz-q4-p10", "b0-rxz-q4-m5")
CZ_DAMPING = (0.019, 0.031)


def experiment(arm: str) -> gnf.Experiment:
    """The arm's operations as the histogram model's explicit inputs: the q4 pulse angle enters as an injection."""
    ref = rs.retained()
    steps = ps.ARMS[arm][0]
    return gnf.Experiment(
        ops=tuple(ps.arm_operations(arm)),
        region=tuple(ref["region"]),
        roles=ref["roles"],
        keys=tuple(ps.KEYS),
        arms={arm: ("Rx", "q4", steps)},
        scopes={"q4": (ps.Q4,)},
        step=ps.STEP,
        selector="selector",
        flip_bit="d0",
        flip_state=0,
    )


def main() -> int:
    worst_same = 0.0
    scope_gaps = []
    for arm in ARMS:
        e = experiment(arm)
        for label, theta, values, noise in (
            ("exact", 0.0, {}, None),
            ("q12 phase -0.15", -0.15, {"z12": -0.15}, None),
            ("q12 phase +0.18", 0.18, {"z12": 0.18}, None),
            ("CZ damping x1", 0.0, {"ca": CZ_DAMPING[0], "cp": CZ_DAMPING[1]}, (0.0, 0.0, *CZ_DAMPING)),
            (
                "CZ damping x3",
                0.0,
                {"ca": 3 * CZ_DAMPING[0], "cp": 3 * CZ_DAMPING[1]},
                (0.0, 0.0, *(3 * v for v in CZ_DAMPING)),
            ),
            (
                "pulse damping 0.003, CZ x1",
                0.0,
                {"pa": 0.003, "pp": 0.003, "ca": CZ_DAMPING[0], "cp": CZ_DAMPING[1]},
                (0.003, 0.003, *CZ_DAMPING),
            ),
        ):
            world = "q12_phase" if "q12" in label else "exact"
            mine = ps.forward_law(arm, world, theta, noise=noise)
            gap = float(np.abs(mine - gnf.law(e, arm, values)).max())
            worst_same = max(worst_same, gap)
            print(f"{arm:18s} {label:30s} max |difference| {gap:.3e}")
        for label, world, theta, values in (
            ("coupler phase -0.25 vs delta -0.25", "coupler_phase", -0.25, {"delta": -0.25}),
            ("q8 phase -0.25 vs c8 -0.25", "q8_phase_at_coupler", -0.25, {"c8": -0.25}),
        ):
            gap = float(np.abs(ps.forward_law(arm, world, theta) - gnf.law(e, arm, values)).max())
            scope_gaps.append(gap)
            print(f"{arm:18s} {label:30s} max |difference| {gap:.3e} (different scope)")
    print(
        f"worst same-mechanism difference {worst_same:.3e}; "
        f"scope differences {min(scope_gaps):.3e} to {max(scope_gaps):.3e}"
    )
    return 0 if worst_same <= TOLERANCE else 1


if __name__ == "__main__":
    raise SystemExit(main())
