"""gororoba_quantum/coherence_probes.py and primorial_campaigns.py: the probes recover injected coherent errors in
primorial_bound_residuals' conventions, a detuned pulse is a tilt, and the gap-88 campaign's arms share one
compiled circuit and read the exact coefficients.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]

import primorial_bound_residuals as br  # noqa: E402
import primorial_probe_case as case  # noqa: E402

import coherence_probes as cp  # noqa: E402
import primorial_campaigns as g88  # noqa: E402

DURATIONS = {"sx": 32e-9, "x": 32e-9, "cz": 68e-9}
# Every family at once, detuning on idles and CZs only (the probe case's mapping).
TRUTH = {
    "tilt": (0.004, -0.007, 0.010),
    "tilt_x": (-0.003, 0.005, 0.002),
    "cz_phase": (0.03, -0.05),
    "detuning": (12.0, -20.0, 7.0),
    "zz": (3.0, -5.0),
    "amplitude": (0.004, -0.003, 0.002),
    "detuning_gates": case.MAPPED_DETUNING,
}


def probe_summary(spec: dict[str, Any]) -> dict[str, float]:
    return cp.summarize({name: np.asarray(br.law(case.logical_ops(c, DURATIONS), spec)) for name, c in cp.circuits()})


def test_probes_recover_every_family_at_once() -> None:
    got = probe_summary(TRUTH)
    truth = case.truth_of(TRUTH)
    # Tolerances: 1e-4 rad on tilt and 2e-4 rad on CZ phase (second-order cross terms), 3 Hz on detuning and ZZ.
    tolerance = {"tilt": 1e-4, "cz_phase": 2e-4, "detuning": 3.0, "zz": 3.0}
    for key, value in truth.items():
        bound = next(t for prefix, t in tolerance.items() if key.startswith(prefix))
        if abs(got[key] - value) > bound:
            raise AssertionError(f"{key}: {got[key]} against {value}")


def test_ideal_probes_read_zero() -> None:
    got = probe_summary({})
    if any(abs(v) > 1e-9 for k, v in got.items() if not k.startswith(("se_", "qse_", "d_", "var_"))):
        raise AssertionError(got)


def test_detuned_pulse_is_a_tilt() -> None:
    if case.detuned_pulse_check()["largest_infidelity_against_tilt"] > 1e-9:
        raise AssertionError("a detuned pulse departs from the tilt Delta / Omega")


def test_tilt_cells_are_identities() -> None:
    for gate in ("x", "sx"):
        law = br.law(case.logical_ops(cp.tilt_circuit(gate, "outer", 3, "z"), DURATIONS), {})
        if abs(law[0] - 1.0) > 1e-12:
            raise AssertionError(f"{gate} cell is not the identity: {law}")


def test_gap88_arms_share_one_circuit_and_read_exact_coefficients() -> None:
    members = g88.members()
    by_setting: dict[str, set[int]] = {}
    for member in members:
        if member.binding is not None:
            setting = member.name.split("_", 1)[1]
            by_setting.setdefault(setting, set()).add(id(member.circuit))
    if len(by_setting) != 24 or any(len(ids) != 1 for ids in by_setting.values()) or len(members) != 104:
        raise AssertionError("the four arms of a setting do not share one circuit")
    summary = g88.summarize({m.name: m.ideal for m in members})
    if summary["max_bias"] > 1e-9 or summary["drift_max"] > 1e-9 or summary["identified"] != 1.0:
        raise AssertionError(summary)


def test_cz_pair_slope_matches_record_convention() -> None:
    phi = 0.02
    got = probe_summary({"cz_phase": (phi, -phi)})
    if abs(got["cz_phase_c0"] - phi) > 1e-9 or abs(got["cz_phase_c1"] + phi) > 1e-9:
        raise AssertionError(got)


def test_covariance_summary_matches_the_multinomial_errors() -> None:
    laws = {name: np.asarray(br.law(case.logical_ops(c, DURATIONS), TRUTH)) for name, c in cp.circuits()}
    # A readout-like mixing keeps every law strictly inside the simplex, as live_run's inverted laws are.
    mixed = {name: 0.9 * law + 0.1 / 8 for name, law in laws.items()}
    covariances = {name: np.diag(law) - np.outer(law, law) for name, law in mixed.items()}
    plain = cp.summarize(mixed)
    propagated = cp.summarize_with_covariance(mixed, covariances)
    for key, value in plain.items():
        if not np.isclose(value, propagated[key], rtol=1e-12, atol=1e-15):
            raise AssertionError(f"{key}: {value} against {propagated[key]}")


def test_readout_calibration_noise_enters_every_error() -> None:
    laws = {
        name: 0.9 * np.asarray(br.law(case.logical_ops(c, DURATIONS), TRUTH)) + 0.1 / 8 for name, c in cp.circuits()
    }
    got = cp.summarize(laws)
    for component in cp.COMPONENTS:
        if got[f"se_{component}"] < got[f"qse_{component}"] - 1e-15:
            raise AssertionError(f"{component}: total error below its quadrature part")
    # The flip derivative of each component equals a direct recomputation at a shifted assignment.
    flips = cp.assignment(laws)
    step = 1e-5
    for wire, flip in cp.FLIPS:
        moved = list(flips)
        e10, e01 = moved[wire]
        moved[wire] = (e10 + step, e01) if flip == "e10" else (e10, e01 + step)
        shifted = cp._components(laws, moved, None)[0]
        for component in cp.COMPONENTS:
            slope = (shifted[component] - got[component]) / step
            scale = max(1.0, abs(slope))
            if abs(slope - got[f"d_{component}__{flip}_q{wire}"]) > 1e-3 * scale:
                raise AssertionError(
                    f"{component} {flip} q{wire}: {slope} against {got[f'd_{component}__{flip}_q{wire}']}"
                )


def test_joint_sample_at_zero_draw_returns_the_estimates() -> None:
    laws = {
        name: 0.9 * np.asarray(br.law(case.logical_ops(c, DURATIONS), TRUTH)) + 0.1 / 8 for name, c in cp.circuits()
    }
    summary = cp.summarize(laws)
    sample = case.joint_sample(summary, 800, [0.0] * len(case.JOINT_INPUTS))
    for key in case.ESTIMATES:
        if abs(sample[key] - summary[key]) > 1e-12 * max(1.0, abs(summary[key])):
            raise AssertionError(f"{key}: {sample[key]} against {summary[key]}")
