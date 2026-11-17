"""The physical-noise simulation of the injected-rotation scan: its density matrix, sizing and wrong-class rule."""

from __future__ import annotations

import numpy as np
import pytest
import qi_pathion_null_rotation_scan_cases as rs
import qi_pathion_null_rotation_scan_noise as noise

NONE = (0.0, 0.0, 0.0, 0.0, 0.0)


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


@pytest.mark.parametrize(
    ("arm", "world", "theta"), [(rs.CENTER, None, 0.0), ("b0-rx-q8-m10", "pulse_y_before_all", -0.07)]
)
def test_the_noiseless_density_matrix_equals_the_state_vector_law(arm: str, world: str | None, theta: float) -> None:
    law = noise.noisy_law(arm, NONE, world, theta)
    _expect(float(np.abs(law - rs.forward_law(arm, world, theta)).max()) < 1e-12, "the two laws differ")


def test_an_amplitude_scale_is_an_x_rotation_of_the_center_arm() -> None:
    scaled = noise.noisy_law(rs.CENTER, NONE, None, 0.0, 0.0, 0.02)
    rotated = rs.forward_law(rs.CENTER, "pulse_x_before_all", 0.02 * np.pi / 2)
    _expect(float(np.abs(scaled - rotated).max()) < 1e-12, "a scale of the center arm is not its x rotation")


def test_the_retained_brackets_hold_the_q11_jump() -> None:
    rates = [bracket[11][1] for bracket in noise.retained_brackets()]
    _expect(min(rates) < 0.05 < 0.3 < max(rates), f"q11 e10 spans {min(rates)} to {max(rates)}")


@pytest.mark.parametrize(
    ("label", "rx_label", "truth", "expected"),
    [
        ("pulse_x", None, "pulse_other", True),
        ("pulse_x", None, "pulse_x", False),
        ("x_excluded", None, "readout", False),
        ("x_excluded", None, "pulse_x", True),
        ("unresolved_both", None, "pulse_x", False),
        ("unresolved_bridge", "readout", "pulse_x", True),
        ("readout", None, None, True),
    ],
)
def test_the_wrong_class_rule(label: str, rx_label: str | None, truth: str | None, expected: bool) -> None:
    _expect(noise.wrong(label, rx_label, truth) is expected, f"{label} against {truth}")


@pytest.mark.audit
def test_self_test_passes() -> None:
    _expect(noise.self_test().endswith("OK"), "the self-test fails")
