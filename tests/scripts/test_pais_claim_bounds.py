"""Contracts of the analytic bounds on the Pais patent claims."""

from __future__ import annotations

import math

import pais_claim_bounds as bounds


def test_every_stated_inequality_holds() -> None:
    result = bounds.bounds()
    example = result["worked_example"]
    if not isinstance(example, dict):
        raise AssertionError("worked example missing")
    if not 1e24 < example["eq1_flux_W_per_m2"] < 2e24:
        raise AssertionError("Eq. 1 no longer reproduces the patent's 1e24 W/m^2 example")
    if example["steady_rotation_radiated_power_W"] != 0.0 or example["shell_field_mass_kg"] < 1e5:
        raise AssertionError("the steady example radiates or its field adds under 1e5 kg")
    if example["log10_schwinger_rate_per_m3_s"] > -200:
        raise AssertionError("the example field produces pairs at a non-negligible rate")


def test_schwinger_field_matches_its_definition() -> None:
    field = bounds.schwinger_field()
    if not math.isclose(field, 1.3232854777e18, rel_tol=1e-9):
        raise AssertionError(f"E_S {field} departs from m_e^2 c^3 / (e hbar)")
    if not math.isclose(bounds.critical_magnetic_field() * bounds.C, field, rel_tol=1e-14):
        raise AssertionError("B_c c differs from E_S")


def test_euler_heisenberg_fraction_scales_quadratically() -> None:
    low, high = bounds.euler_heisenberg_fraction(1e9), bounds.euler_heisenberg_fraction(1e10)
    if not math.isclose(high / low, 100.0, rel_tol=1e-12):
        raise AssertionError("the vacuum-polarization fraction is not quadratic in the field")


def test_gertsenshtein_conversion_is_dimensionless_and_quadratic() -> None:
    base = bounds.gertsenshtein(10.0, 1.0)
    if not 1e-36 < base < 1e-34:
        raise AssertionError(f"10 T over 1 m converts {base}, outside the SI order 1e-35")
    if not math.isclose(bounds.gertsenshtein(20.0, 3.0) / base, 36.0, rel_tol=1e-12):
        raise AssertionError("conversion is not quadratic in B L")


def test_breathing_and_steady_modes_radiate_nothing() -> None:
    vibration = bounds.vibration_case()
    if vibration["breathing_shell_radiated_W"] != 0.0:
        raise AssertionError("a breathing shell radiates")
    if vibration["eq2_over_radiated"] < 1e12:
        raise AssertionError("Eq. 2 no longer exceeds the radiated sheet flux by twelve orders")
