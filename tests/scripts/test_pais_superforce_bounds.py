"""Contracts of the decomposition of the Pais Superforce claims."""

from __future__ import annotations

import math

import pais_superforce_bounds as bounds


def test_the_unification_equalities_are_planck_unit_identities() -> None:
    result = bounds.bounds()
    residuals = result["planck_identity_residuals"]
    if not isinstance(residuals, dict) or max(residuals.values()) > 1e-12:
        raise AssertionError(f"a Planck-unit identity fails: {residuals}")
    for multiple in (1, 3, 50):
        value = bounds.fine_structure_step(multiple * bounds.E_CHARGE)
        if not math.isclose(value, bounds.planck_force(), rel_tol=1e-12):
            raise AssertionError(f"(1/alpha) F_EM at L_P depends on the charge multiple {multiple}")


def test_measured_strong_coupling_falls_short_of_the_planck_force() -> None:
    strong = bounds.strong_at_planck()
    if not 50 < strong["planck_force_over_strong_force_at_LP"] < 56:
        raise AssertionError(f"c^4/G over the Planck-length strong force moved: {strong}")
    if not math.isclose(strong["alpha_s_planck_one_loop"], strong["alpha_s_planck_three_loop"], rel_tol=0.02):
        raise AssertionError("one-loop running departs from the three-loop Planck-scale coupling by over 2 percent")


def test_one_loop_running_returns_the_input_at_the_z_mass() -> None:
    if not math.isclose(bounds.alpha_s_one_loop(bounds.M_Z_GEV), bounds.ALPHA_S_MZ, rel_tol=1e-14):
        raise AssertionError("alpha_s(m_Z) does not reproduce its input")


def test_friedmann_identity_holds_for_any_hubble_rate() -> None:
    for h0 in (50.0, 67.4, 73.0):
        if not math.isclose(bounds.cosmic_identity(h0)["gradient_over_planck_force"], 0.5, rel_tol=1e-12):
            raise AssertionError(f"M_H c^2 / R_H differs from c^4/(2G) at H0 = {h0}")


def test_proton_pressure_is_the_proton_energy_scale() -> None:
    pressure = bounds.proton_pressure()
    if not 1 < pressure["pais_pressure_over_proton_energy_density"] < 2:
        raise AssertionError(f"1e35 Pa against m_p c^2 / V_p moved: {pressure}")
    if pressure["pais_pressure_over_planck_pressure"] > 1e-78:
        raise AssertionError("the proton pressure comes within 78 decades of the Planck pressure")


def test_water_cherenkov_threshold() -> None:
    medium = bounds.medium_substitution()
    if not 1.33 < medium["water_index"] < 1.35:
        raise AssertionError(f"water index at 400 nm {medium['water_index']}")
    if not 0.24 < medium["electron_cherenkov_threshold_kinetic_MeV"] < 0.27:
        raise AssertionError("the electron Cherenkov threshold in water left 0.24-0.27 MeV")
