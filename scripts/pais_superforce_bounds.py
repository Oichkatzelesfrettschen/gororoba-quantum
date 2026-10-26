"""Decomposition of the Pais Superforce claims into identities, measured couplings and falsifying bounds.

The Superforce preprints (OSF yh84c_v1, 2023-04-11, and OSF 9kebt_v1, 2023-07-24;
docs/notes/papers/pais-superforce-preprints.md) name the Planck force c^4/G the force of unification and
argue from five steps: the inverse Einstein coupling has units of force; F_SN = F_EM / alpha and the
gravitational force both equal c^4/G at the Planck length; the Schrodinger equation contains c^4/G; the
energy gradient m_U c^2 / R_U of the observable universe equals c^4/G "not by coincidence" (9kebt Eq. 1);
and c^2 = 1/(mu0 mu eps0 eps) in a medium lets a material engineer c^4/G. This script computes each step
with CODATA constants (scipy.constants) and the measured inputs below, states which steps are identities
of the Planck-unit definitions, and raises when an inequality the topic note quotes fails. It submits no
job and reads no network.

Measured inputs and their authorities:
- alpha_s(m_Z) = 0.1180 and the one-loop coefficient b0 = (33 - 2 n_f)/(12 pi) of
  d alpha_s / d ln mu^2 = -b0 alpha_s^2 (PDG 2024 QCD review, Eqs. 9.3 and 9.25);
- g3(M_Pl) = 0.4873 from three-loop Standard Model running (Buttazzo et al., JHEP 12 (2013) 089,
  Eq. 61c), with its reference top mass 173.34 GeV;
- H0 = 67.4 km/s/Mpc and Omega_K = 0.001 +- 0.002 (Planck 2018 VI abstract);
- the Kreuzer bound 5e-5 on the fluorine-bromine active-to-passive mass difference and the lunar laser
  ranging bound 4e-12 on aluminum against iron (Will, Living Rev. Relativ. 17, 4 (2014), Sec. 4.4.3 and
  Eq. 72);
- the refractive index of water at 20.0 C (Daimon and Masumura, Appl. Opt. 46, 3811 (2007), Sellmeier
  coefficients as distributed by the CC0 refractiveindex.info database, file H2O/nk/Daimon-20.0C.yml);
- Pais's own inputs: proton central pressure 1e35 Pa, and m_U ~ 1e53 kg, R_U ~ 1e26 m.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from scipy import constants as sc

C = sc.c
G = sc.G
HBAR = sc.hbar
ALPHA = sc.fine_structure
E_CHARGE = sc.e
M_E = sc.m_e
M_P_PROTON = sc.m_p
EPS0 = sc.epsilon_0
PROTON_RADIUS = sc.physical_constants["proton rms charge radius"][0]
GEV = sc.giga * sc.electron_volt
MEGAPARSEC = sc.parsec * 1e6

ALPHA_S_MZ = 0.1180
M_Z_GEV = 91.1876
M_TOP_GEV = 173.34
G3_PLANCK = 0.4873
H0_KM_S_MPC = 67.4
OMEGA_K = (0.001, 0.002)
KREUZER_BOUND = 5e-5
LUNAR_BOUND = 4e-12
# Daimon and Masumura 2007, 20.0 C: n^2 - 1 = sum B_i lambda^2 / (lambda^2 - C_i), lambda and sqrt(C_i) in um.
WATER_SELLMEIER = (
    (5.684027565e-1, 5.101829712e-3),
    (1.726177391e-1, 1.821153936e-2),
    (2.086189578e-2, 2.620722293e-2),
    (1.130748688e-1, 1.069792721e1),
)
PAIS_PROTON_PRESSURE = 1e35  # Pa, yh84c Sec. VI
PAIS_UNIVERSE_MASS = 1e53  # kg, 9kebt Eq. 1
PAIS_UNIVERSE_RADIUS = 1e26  # m, 9kebt Eq. 1


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def planck_force() -> float:
    return C**4 / G


def planck_length() -> float:
    return math.sqrt(HBAR * G / C**3)


def planck_mass() -> float:
    return math.sqrt(HBAR * C / G)


def coupling_forms() -> dict[str, float]:
    """c^4/G beside the inverse Einstein coupling c^4/(8 pi G) and Gibbons' maximal tension c^4/(4 G)."""
    force = planck_force()
    return {
        "planck_force_N": force,
        "inverse_einstein_coupling_N": force / (8 * math.pi),
        "gibbons_maximal_tension_N": force / 4,
        "planck_force_over_maximal_tension": 4.0,
    }


def planck_identities() -> dict[str, float]:
    """Relative residuals of the equalities the preprints derive; each holds by the definitions of L_P and m_P."""
    force, length, mass = planck_force(), planck_length(), planck_mass()
    planck_energy = mass * C**2
    return {
        "hbar_c_over_LP2": abs(HBAR * C / length**2 / force - 1),
        "G_mP2_over_LP2": abs(G * mass**2 / length**2 / force - 1),
        "EP_over_LP": abs(planck_energy / length / force - 1),
    }


def fine_structure_step(charge: float = E_CHARGE, length: float | None = None) -> float:
    """(1/alpha) F_EM(L) for charge q, with alpha taken as q^2/(4 pi eps0 hbar c) as yh84c Sec. III defines it.

    The charge cancels, leaving hbar c / L^2: the step is Coulomb's law with its coupling set to one, so at
    L = L_P it returns c^4/G by the definition of L_P, for any charge.
    """
    length = planck_length() if length is None else length
    coupling = charge**2 / (4 * math.pi * EPS0 * HBAR * C)
    coulomb = charge**2 / (4 * math.pi * EPS0 * length**2)
    return coulomb / coupling


def alpha_s_one_loop(mu_gev: float) -> float:
    """One-loop alpha_s from m_Z with n_f = 5 below the top mass and 6 above it (PDG 2024 Eq. 9.3)."""

    def run(inverse: float, low: float, high: float, flavors: int) -> float:
        b0 = (33 - 2 * flavors) / (12 * math.pi)
        return inverse + b0 * math.log(high**2 / low**2)

    inverse = run(1 / ALPHA_S_MZ, M_Z_GEV, min(mu_gev, M_TOP_GEV), 5)
    if mu_gev > M_TOP_GEV:
        inverse = run(inverse, M_TOP_GEV, mu_gev, 6)
    return 1 / inverse


def strong_at_planck() -> dict[str, float]:
    """The strong force at the Planck length relative to c^4/G, from measured running couplings."""
    planck_gev = sc.physical_constants["Planck mass energy equivalent in GeV"][0]
    three_loop = G3_PLANCK**2 / (4 * math.pi)
    one_loop = alpha_s_one_loop(planck_gev)
    require(abs(one_loop / three_loop - 1) < 0.15, f"one-loop alpha_s {one_loop} departs from three-loop {three_loop}")
    require(three_loop < 0.03, "alpha_s(M_Pl) reaches 0.03: the factor-of-30 shortfall no longer holds")
    return {
        "planck_mass_GeV": planck_gev,
        "alpha_s_planck_three_loop": three_loop,
        "alpha_s_planck_one_loop": one_loop,
        "strong_force_at_LP_over_planck_force": three_loop,
        "planck_force_over_strong_force_at_LP": 1 / three_loop,
        "pais_ratio_FSN_over_FEM": 1 / ALPHA,
        "pais_ratio_implies_alpha_s": 1.0,
    }


def schrodinger_step() -> dict[str, float]:
    """V/L with V = hbar^2/(2 m L^2), the kinetic-potential balance of yh84c Sec. IV, over c^4/G.

    The value is hbar^2/(2 m L^3); it reaches c^4/(2G) only when the Planck mass and Planck length are
    inserted; an electron at its reduced Compton wavelength gives about 1e-45 of it and a proton at its
    charge radius about 5e-41.
    """

    def gradient(mass: float, length: float) -> float:
        return HBAR**2 / (2 * mass * length**3) / planck_force()

    electron = gradient(M_E, HBAR / (M_E * C))
    proton = gradient(M_P_PROTON, PROTON_RADIUS)
    planck = gradient(planck_mass(), planck_length())
    require(abs(planck - 0.5) < 1e-12, f"Planck insertion gives {planck}, not 1/2")
    require(max(electron, proton) < 1e-40, "an atomic-scale insertion comes within 1e40 of c^4/G")
    return {"electron_compton": electron, "proton_radius": proton, "planck": planck}


def proton_pressure() -> dict[str, float]:
    """Pais's 1e35 Pa proton pressure against the Planck pressure and the proton's own energy scale."""
    planck_pressure = C**7 / (HBAR * G**2)
    volume = 4 * math.pi * PROTON_RADIUS**3 / 3
    self_scale = M_P_PROTON * C**2 / volume
    force_scale = PAIS_PROTON_PRESSURE * math.pi * PROTON_RADIUS**2
    ratio = PAIS_PROTON_PRESSURE / self_scale
    require(0.1 < ratio < 10, f"1e35 Pa is {ratio} of m_p c^2 / V_p, outside one decade")
    require(force_scale / planck_force() < 1e-35, "the proton force scale comes within 1e35 of c^4/G")
    return {
        "planck_pressure_Pa": planck_pressure,
        "pais_pressure_over_planck_pressure": PAIS_PROTON_PRESSURE / planck_pressure,
        "proton_energy_density_Pa": self_scale,
        "pais_pressure_over_proton_energy_density": ratio,
        "pressure_times_area_N": force_scale,
        "pressure_times_area_over_planck_force": force_scale / planck_force(),
    }


def cosmic_identity(h0_km_s_mpc: float = H0_KM_S_MPC) -> dict[str, float]:
    """M_H c^2 / R_H for the critical density inside the Hubble radius, against c^4/G.

    rho_c = 3 H^2 / (8 pi G) and R_H = c / H give M_H = c^3 / (2 G H), so M_H c^2 / R_H = c^4 / (2 G) for every
    H: 9kebt Eq. 1 is the Friedmann equation of a flat universe, and its "coincidence" is the measured
    Omega_K.
    """
    hubble = h0_km_s_mpc * 1e3 / MEGAPARSEC
    radius = C / hubble
    density = 3 * hubble**2 / (8 * math.pi * G)
    mass = 4 * math.pi * density * radius**3 / 3
    gradient = mass * C**2 / radius
    residual = abs(gradient / (planck_force() / 2) - 1)
    require(residual < 1e-12, f"Friedmann identity residual {residual}")
    return {
        "hubble_radius_m": radius,
        "critical_mass_in_hubble_radius_kg": mass,
        "gradient_over_planck_force": gradient / planck_force(),
        "identity_relative_residual": residual,
        "pais_inputs_gradient_over_planck_force": PAIS_UNIVERSE_MASS * C**2 / PAIS_UNIVERSE_RADIUS / planck_force(),
        "omega_k": OMEGA_K[0],
        "omega_k_sigma": OMEGA_K[1],
    }


def water_index(wavelength_um: float) -> float:
    square = wavelength_um**2
    return math.sqrt(1 + sum(b * square / (square - c) for b, c in WATER_SELLMEIER))


def medium_substitution(wavelength_um: float = 0.4) -> dict[str, float]:
    """Pais's c -> c/n in c^4/G (yh84c Sec. V) against active-mass nulls and Cherenkov emission in water.

    Writing the medium's light speed into the Einstein coupling makes it 8 pi G n^4 / c^4, so a body's active
    gravitational mass scales as n^4 and two materials of different index gravitate differently by order one.
    Kreuzer's and the lunar bound then require the compared materials to share n to a quarter of each bound.
    If c/n were the invariant speed in water, no massive particle could exceed it; an electron of kinetic
    energy above m_e c^2 (1/sqrt(1 - 1/n^2) - 1) exceeds c/n and radiates Cherenkov light, which water
    Cherenkov detectors record.
    """
    n = water_index(wavelength_um)
    require(1.3 < n < 1.4, f"water index {n} at {wavelength_um} um")
    threshold_mev = M_E * C**2 * (1 / math.sqrt(1 - 1 / n**2) - 1) / (sc.mega * sc.electron_volt)
    return {
        "superforce_in_water_over_vacuum": n**-4,
        "einstein_coupling_in_water_over_vacuum": n**4,
        "kreuzer_index_match_required": KREUZER_BOUND / 4,
        "lunar_index_match_required": LUNAR_BOUND / 4,
        "water_index": n,
        "wavelength_um": wavelength_um,
        "cherenkov_threshold_beta": 1 / n,
        "electron_cherenkov_threshold_kinetic_MeV": threshold_mev,
    }


def bounds() -> dict[str, object]:
    identities = planck_identities()
    require(max(identities.values()) < 1e-12, f"Planck-unit identities fail: {identities}")
    charge_free = {
        str(multiple): fine_structure_step(multiple * E_CHARGE) / planck_force() - 1 for multiple in (1, 2, 137)
    }
    require(max(abs(v) for v in charge_free.values()) < 1e-12, f"(1/alpha) F_EM depends on charge: {charge_free}")
    return {
        "constants": {
            "scipy_constants_codata": sc.physical_constants["Newtonian constant of gravitation"][0] == G,
            "planck_length_m": planck_length(),
            "planck_mass_kg": planck_mass(),
        },
        "coupling_forms": coupling_forms(),
        "planck_identity_residuals": identities,
        "fine_structure_step_residual_by_charge_multiple": charge_free,
        "strong_at_planck": strong_at_planck(),
        "schrodinger_step_over_planck_force": schrodinger_step(),
        "proton_pressure": proton_pressure(),
        "cosmic_identity": cosmic_identity(),
        "medium_substitution": medium_substitution(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, help="JSON path; default prints the result")
    args = parser.parse_args()
    text = json.dumps(bounds(), indent=1, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
