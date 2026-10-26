"""Contracts of the QET passivity controls: no information, no energy below the vacuum value."""

from __future__ import annotations

import math

import numpy as np
import qet_passivity_controls as controls


def test_reference_checks_pass_and_report_e_b() -> None:
    e_b = controls.reference()["E_B"]
    if not isinstance(e_b, float) or not math.isclose(e_b, math.sqrt(5) - 3 / math.sqrt(2), rel_tol=1e-12):
        raise AssertionError("E_B at h = k = 1 departs from sqrt(5) - 3/sqrt(2)")


def test_kabsch_minimum_matches_search_on_a_mixed_state() -> None:
    rho = controls.averaged(controls.prepare(1.0, 0.7, delta=0.08, gamma=0.03, phase=0.3))
    fast, slow = controls.kabsch_min_local(rho, 1.0, 0.7), controls.search_min_local(rho, 1.0, 0.7)
    if abs(fast - slow) > 1e-8:
        raise AssertionError(f"Kabsch {fast} and search {slow} differ")


def test_uninformed_record_never_shows_an_information_excess() -> None:
    for case in ({}, {"delta": 0.1}, {"gamma": 0.1}, {"phase": 0.4}, {"delta": -0.07, "gamma": 0.02, "phase": 0.9}):
        excess = controls.summary(1.0, 1.0, flip=0.5, **case)["information_excess"]
        if excess > 1e-10:
            raise AssertionError(f"{case}: q = 1/2 gives information excess {excess}")


def test_angle_error_fakes_the_absolute_endpoint_and_the_excess_rejects_it() -> None:
    row = controls.summary(1.0, 1.0, delta=0.15)
    if row["uninformed_below_ground"] < 0.1 or row["information_excess"] > 0:
        raise AssertionError("the angle-error false positive or its rejection changed")


def test_planted_mutant_without_feedback_sign_is_caught() -> None:
    rho = controls.prepare(1.0, 1.0)
    unsigned = controls.final_local(rho, 1.0, 1.0, "plus")
    if -unsigned > 1e-10 or not np.isfinite(unsigned):
        raise AssertionError("a fixed-sign rotation went below the vacuum value")


def test_reported_bit_estimator_fakes_an_excess_that_remeasurement_rejects() -> None:
    ground = controls.ground_state(1.0, 1.0)
    reported = controls.hardware_excess(ground, 1.0, 1.0, 0.5, 0.0, "reported")
    remeasured = controls.hardware_excess(ground, 1.0, 1.0, 0.5, 0.0, "remeasured")
    if reported < 0.1 or remeasured > 1e-10:
        raise AssertionError(f"q = 1/2: reported {reported}, remeasured {remeasured}")


def test_product_state_keeps_the_record_excess_and_loses_the_floor_margin() -> None:
    row = controls.summary(1.0, 1.0, delta=-math.pi / 8)
    if row["information_excess"] <= 0 or row["channel_floor_margin"] >= 0:
        raise AssertionError("the product-state mutation no longer separates the two endpoints")
