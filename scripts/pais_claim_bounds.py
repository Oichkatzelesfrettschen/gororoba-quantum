"""Bounds of standard electrodynamics, QED and general relativity on the Pais patent claims.

Every input number is the patent's own (US 10,135,366 B2, US 10,144,532 B2 and
US 10,322,827 B2, read 2026-10-25; docs/notes/papers/pais-patent-web-sources.md),
and every constant is CODATA through scipy.constants. Each check computes the
quantity the patent asserts, the bound physics places on it, and their ratio;
the script raises when a stated inequality fails, so a passing run certifies
every number the topic note docs/notes/topics/pais-claims-falsification.md
quotes. It submits no job and reads no network.

The patents write the Poynting magnitude of a charged spinning surface as
S_max = f_G (sigma^2/eps0) [R_r omega + R_v nu + v_R] (Eq. 1) and the
vibrating case as S_max = f_G (sigma^2/eps0) R_v nu^2 t_op (Eq. 2). Eq. 1 is
the magnitude of the circulating E x B / mu0 of a steady charge current; a
time-independent charge and current density radiates nothing, so Eq. 1 is a
stored-momentum density times c^2, not a radiated power. Eq. 2 replaces the
velocity by acceleration times operating time, a velocity that grows without
bound, while a harmonic vibration of amplitude R_v keeps |v| <= 2 pi nu R_v.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from scipy import constants as sc

EPS0 = sc.epsilon_0
MU0 = sc.mu_0
C = sc.c
HBAR = sc.hbar
G = sc.G
E_CHARGE = sc.e
M_E = sc.m_e
ALPHA = sc.fine_structure

# Patent inputs (US 10,135,366 B2 and US 10,144,532 B2 worked example; US 10,322,827 B2 Eq. 4 inputs).
SIGMA_EXAMPLE = 5.0e4  # C/m^2
RADIUS_EXAMPLE = 2.0  # m
RPM_EXAMPLE = 3.0e4
CLAIMED_FLUX_EXAMPLE = 1.0e24  # W/m^2
PATENT_VACUUM_FIELD_LIMIT = 1.0e9  # V/m, the patent's own vacuum breakdown figure
HFGW_FIELD = 1.0e10  # T, US 10,322,827 B2 "B0 on the order of 10^10 Tesla"
HFGW_INPUT_FLUX = 1.0e33  # W/m^2
HFGW_CLAIMED_POWER = 1.0e10  # W
GHZ_DRIVE = 1.0e9  # Hz, low end of the 10^9..10^18 Hz vibration range the patents name
ONE_COULOMB = 1.0  # C, the dynamic-fusor charge of US 2019/0295733 A1


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def schwinger_field() -> float:
    """E_S = m_e^2 c^3 / (e hbar), the field that does work m_e c^2 over one reduced Compton length."""
    return M_E**2 * C**3 / (E_CHARGE * HBAR)


def critical_magnetic_field() -> float:
    """B_c = m_e^2 c^2 / (e hbar) = E_S / c, where the electron cyclotron energy reaches m_e c^2."""
    return M_E**2 * C**2 / (E_CHARGE * HBAR)


def log10_schwinger_rate(field: float) -> float:
    """log10 of the leading constant-field pair-production rate per volume and time.

    Gamma = (e E)^2 / (4 pi^3 c hbar^2) exp(-pi E_S / E) for the leading n = 1
    term; the logarithm avoids underflow far below E_S.
    """
    prefactor = (E_CHARGE * field) ** 2 / (4 * math.pi**3 * C * HBAR**2)
    return math.log10(prefactor) - math.pi * schwinger_field() / field / math.log(10)


def euler_heisenberg_fraction(field: float) -> float:
    """Leading Euler-Heisenberg energy correction over eps0 E^2 / 2 for a pure electric field.

    The Lagrangian term is a E^4 with a E^4 / (eps0 E^2 / 2) = (alpha / 45 pi)(E/E_S)^2;
    the energy density E dL/dE - L carries 3 a E^4, so the energy fraction is
    three times the Lagrangian fraction.
    """
    return 3 * ALPHA / (45 * math.pi) * (field / schwinger_field()) ** 2


def invariant_identity(samples: int = 64) -> float:
    """Largest relative residual of u^2 - |S/c|^2 = (eps0/2)^2 [(E^2 - c^2 B^2)^2 + 4 c^2 (E.B)^2].

    The right side is a sum of squares of the two Lorentz invariants, so the
    energy density of every Maxwell field bounds its momentum flux, u >= |S|/c,
    with equality only for null fields (plane waves). Fields are drawn on a
    fixed lattice of directions so the check is deterministic.
    """
    worst = 0.0
    for index in range(samples):
        a, b = 0.37 * index + 0.1, 0.61 * index + 0.2
        e_field = np.array([math.cos(a), math.sin(a) * math.cos(b), math.sin(a) * math.sin(b)]) * (1 + index)
        b_field = np.array([math.sin(b), math.cos(a + b), math.sin(2 * a - b)]) * (0.5 + index % 7) / C
        u = EPS0 * (e_field @ e_field + C**2 * (b_field @ b_field)) / 2
        s_over_c = np.linalg.norm(np.cross(e_field, b_field)) / (MU0 * C)
        first = e_field @ e_field - C**2 * (b_field @ b_field)
        second = C * (e_field @ b_field)
        right = (EPS0 / 2) ** 2 * (first**2 + 4 * second**2)
        worst = max(worst, abs((u**2 - s_over_c**2) - right) / u**2)
        require(u >= s_over_c * (1 - 1e-12), f"sample {index}: u < |S|/c")
    return worst


def worked_example() -> dict[str, float]:
    """The 2 m, 30000 RPM, 5e4 C/m^2 disc and shell of US 10,135,366 B2 and US 10,144,532 B2."""
    omega = RPM_EXAMPLE * 2 * math.pi / 60
    rim_speed = RADIUS_EXAMPLE * omega
    eq1_flux = SIGMA_EXAMPLE**2 / EPS0 * rim_speed
    surface_field = SIGMA_EXAMPLE / EPS0
    pressure = SIGMA_EXAMPLE**2 / (2 * EPS0)
    # Steady rotating sheet: E = sigma / (2 eps0) per face, B = mu0 sigma v / 2 at the sheet.
    sheet_e, sheet_b = SIGMA_EXAMPLE / (2 * EPS0), MU0 * SIGMA_EXAMPLE * rim_speed / 2
    circulating_flux = sheet_e * sheet_b / MU0
    shell_charge = SIGMA_EXAMPLE * 4 * math.pi * RADIUS_EXAMPLE**2
    shell_field_energy = shell_charge**2 / (8 * math.pi * EPS0 * RADIUS_EXAMPLE)
    require(0.5 < eq1_flux / CLAIMED_FLUX_EXAMPLE < 5, "Eq. 1 does not reproduce the patent's 1e24 W/m^2")
    require(abs(circulating_flux / eq1_flux - 0.25) < 1e-12, "steady-sheet E x B / mu0 differs from Eq. 1 / 4")
    require(surface_field > 1e6 * PATENT_VACUUM_FIELD_LIMIT, "the example field sits within the patent's limit")
    require(surface_field < schwinger_field(), "the example field reaches E_S")
    return {
        "rim_speed_m_per_s": rim_speed,
        "rim_speed_over_c": rim_speed / C,
        "eq1_flux_W_per_m2": eq1_flux,
        "steady_sheet_circulating_flux_W_per_m2": circulating_flux,
        "steady_rotation_radiated_power_W": 0.0,
        "surface_field_V_per_m": surface_field,
        "surface_field_over_patent_vacuum_limit": surface_field / PATENT_VACUUM_FIELD_LIMIT,
        "surface_field_over_schwinger": surface_field / schwinger_field(),
        "electrostatic_pressure_Pa": pressure,
        "shell_charge_C": shell_charge,
        "shell_exterior_field_energy_J": shell_field_energy,
        "shell_field_mass_kg": shell_field_energy / C**2,
        "log10_schwinger_rate_per_m3_s": log10_schwinger_rate(surface_field),
        "euler_heisenberg_fraction": euler_heisenberg_fraction(surface_field),
    }


def patent_limit_case() -> dict[str, float]:
    """The largest surface charge the patent's own 1e9 V/m vacuum limit admits, and the fusor's 1 C."""
    sigma = EPS0 * PATENT_VACUUM_FIELD_LIMIT
    omega = RPM_EXAMPLE * 2 * math.pi / 60
    one_coulomb_radius = math.sqrt(ONE_COULOMB / (4 * math.pi * EPS0 * PATENT_VACUUM_FIELD_LIMIT))
    return {
        "sigma_at_limit_C_per_m2": sigma,
        "eq1_flux_at_limit_W_per_m2": sigma**2 / EPS0 * RADIUS_EXAMPLE * omega,
        "field_energy_density_at_limit_J_per_m3": sigma**2 / (2 * EPS0),
        "one_coulomb_sphere_field_at_2m_V_per_m": ONE_COULOMB / (4 * math.pi * EPS0 * RADIUS_EXAMPLE**2),
        "one_coulomb_min_radius_m": one_coulomb_radius,
        "euler_heisenberg_fraction": euler_heisenberg_fraction(PATENT_VACUUM_FIELD_LIMIT),
        "log10_schwinger_rate_per_m3_s": log10_schwinger_rate(PATENT_VACUUM_FIELD_LIMIT),
    }


def vibration_case(amplitude: float = 1.0e-6, frequency: float = GHZ_DRIVE, t_op: float = 1.0) -> dict[str, float]:
    """Eq. 2 against the bounded velocity and the radiated flux of a vibrating charged sheet.

    A sheet carrying sigma and moving in its own plane with v(t) (a tangential
    surface current sigma v) radiates a plane wave of field sigma v / (2 eps0 c)
    from each face, flux sigma^2 v^2 / (4 eps0 c): the radiated flux is the
    circulating flux times v/c. A spherically symmetric
    breathing shell radiates nothing, because Gauss's law fixes its exterior field.
    """
    sigma = EPS0 * PATENT_VACUUM_FIELD_LIMIT
    v_max = 2 * math.pi * frequency * amplitude
    eq2_flux = sigma**2 / EPS0 * amplitude * frequency**2 * t_op
    radiated_peak = sigma**2 * v_max**2 / (4 * EPS0 * C)
    require(v_max < C, "the vibration amplitude and frequency exceed c")
    return {
        "amplitude_m": amplitude,
        "frequency_Hz": frequency,
        "t_op_s": t_op,
        "eq2_implied_speed_over_bounded_speed": amplitude * frequency**2 * t_op / v_max,
        "eq2_flux_W_per_m2": eq2_flux,
        "sheet_radiated_peak_flux_W_per_m2": radiated_peak,
        "eq2_over_radiated": eq2_flux / radiated_peak,
        "breathing_shell_radiated_W": 0.0,
    }


def zero_point_cutoff(flux: float = CLAIMED_FLUX_EXAMPLE) -> dict[str, float]:
    """Eq. 4 of US 10,144,532 B2, S/c = hbar nu^4 / (8 pi^2 c^3): the cutoff it implies.

    hbar w_c^4 / (8 pi^2 c^3) is the zero-point energy density integrated to an
    angular cutoff w_c; it is regulator-dependent and Lorentz-noninvariant, and
    only renormalized differences such as Casimir energies are observable.
    """
    cutoff = (flux / C * 8 * math.pi**2 * C**3 / HBAR) ** 0.25
    return {"angular_cutoff_per_s": cutoff, "cutoff_photon_energy_eV": HBAR * cutoff / E_CHARGE}


def quantum_inequality(mass_kg: float = 10.0, volume_m3: float = 10.0) -> dict[str, object]:
    """Ford-Roman free-massless-scalar bound -3 hbar / (32 pi^2 c^3 t0^4) against a mass reduction.

    The bound limits the Lorentzian-sampled negative energy density an inertial
    observer sees over sampling time t0 (Ford and Roman 1997); the electromagnetic
    bound carries the same t0^-4 scaling. A craft shedding mass_kg from volume_m3
    needs mean negative energy density mass_kg c^2 / volume_m3.
    """
    needed = mass_kg * C**2 / volume_m3
    rows: dict[str, dict[str, float]] = {}
    for label, t0 in (("1ns", 1.0 / GHZ_DRIVE), ("1s", 1.0)):
        bound = 3 * HBAR / (32 * math.pi**2 * C**3 * t0**4)
        rows[label] = {"bound_J_per_m3": bound, "log10_needed_over_bound": math.log10(needed / bound)}
    gap = min(row["log10_needed_over_bound"] for row in rows.values())
    return {"needed_J_per_m3": needed, "sampling": rows, "min_log10_needed_over_bound": gap}


def casimir_separation(mass_kg: float = 10.0, volume_m3: float = 10.0) -> dict[str, float]:
    """Parallel-plate separation whose Casimir energy density -pi^2 hbar c / (720 a^4) reaches the mass reduction.

    A cavity evades the free-field Ford-Roman bound, so the boundary case asks
    which ideal-conductor gap stores the needed negative density; the Bohr
    radius sets the scale where the continuum-conductor model ends.
    """
    needed = mass_kg * C**2 / volume_m3
    gap = (math.pi**2 * HBAR * C / (720 * needed)) ** 0.25
    bohr = sc.physical_constants["Bohr radius"][0]
    require(gap < bohr, "the required Casimir gap reaches the Bohr radius")
    return {"needed_J_per_m3": needed, "plate_gap_m": gap, "plate_gap_over_bohr_radius": gap / bohr}


def spin_up_radiation(spin_up_seconds: float = 1.0) -> dict[str, float]:
    """Magnetic-dipole power mu0 |m''|^2 / (6 pi c^3) of the worked-example shell spun up in spin_up_seconds.

    A uniformly charged spherical shell spinning at omega carries
    m = Q R^2 omega / 3 and no electric dipole, so an accelerating spin
    radiates only through omega''; the estimate takes omega'' ~ omega / t^2.
    """
    omega = RPM_EXAMPLE * 2 * math.pi / 60
    charge = SIGMA_EXAMPLE * 4 * math.pi * RADIUS_EXAMPLE**2
    moment_second_derivative = charge * RADIUS_EXAMPLE**2 * omega / spin_up_seconds**2 / 3
    power = MU0 * moment_second_derivative**2 / (6 * math.pi * C**3)
    require(power < 1e-6, "spin-up radiation reaches a microwatt")
    return {"spin_up_seconds": spin_up_seconds, "magnetic_dipole_power_W": power}


def gertsenshtein(field: float, length: float) -> float:
    """Graviton-photon conversion probability 4 pi G B^2 L^2 / (mu0 c^4) in SI.

    Ejlli et al. (EPJC 79, 1032, arXiv:1908.00232v2, Appendix A) write the
    mixing term kappa B / 2 with kappa^2 = 16 pi G in rationalized
    Lorentz-Heaviside units, so P = (kappa B L / 2)^2 = 4 pi G B^2 L^2; the
    SI field enters as B^2 / mu0 because both systems give energy density B^2 / 2.
    """
    return 4 * math.pi * G * field**2 * length**2 / (MU0 * C**4)


def hfgw_case() -> dict[str, float]:
    magnetic_energy = HFGW_FIELD**2 / (2 * MU0)
    length_for_claim = math.sqrt(HFGW_CLAIMED_POWER / HFGW_INPUT_FLUX / gertsenshtein(HFGW_FIELD, 1.0))
    require(HFGW_FIELD > critical_magnetic_field(), "the patent field sits below B_c")
    return {
        "conversion_10T_1m": gertsenshtein(10.0, 1.0),
        "conversion_patent_field_1m": gertsenshtein(HFGW_FIELD, 1.0),
        "path_length_for_claimed_power_with_1m2_input_m": length_for_claim,
        "patent_field_over_critical_field": HFGW_FIELD / critical_magnetic_field(),
        "patent_field_energy_density_J_per_m3": magnetic_energy,
        "patent_field_mass_density_kg_per_m3": magnetic_energy / C**2,
        "input_flux_over_schwinger_intensity": HFGW_INPUT_FLUX / (C * EPS0 * schwinger_field() ** 2 / 2),
    }


def bounds() -> dict[str, object]:
    residual = invariant_identity()
    require(residual < 1e-10, f"Lorentz-invariant identity residual {residual}")
    example = worked_example()
    limit = patent_limit_case()
    require(limit["one_coulomb_sphere_field_at_2m_V_per_m"] > PATENT_VACUUM_FIELD_LIMIT, "1 C on 2 m sits within 1e9")
    vibration = vibration_case()
    require(vibration["eq2_implied_speed_over_bounded_speed"] > 1e8, "Eq. 2 stays within the bounded speed")
    qi = quantum_inequality()
    gap = qi["min_log10_needed_over_bound"]
    require(isinstance(gap, float) and gap > 40, "QI gap below 1e40")
    return {
        "constants": {
            "schwinger_field_V_per_m": schwinger_field(),
            "critical_magnetic_field_T": critical_magnetic_field(),
            "scipy_constants_codata": sc.physical_constants["speed of light in vacuum"][0] == C,
        },
        "invariant_identity_max_relative_residual": residual,
        "worked_example": example,
        "patent_limit_case": limit,
        "vibration_case": vibration,
        "zero_point_cutoff": zero_point_cutoff(),
        "quantum_inequality": qi,
        "casimir_boundary_case": casimir_separation(),
        "spin_up_radiation": spin_up_radiation(),
        "hfgw": hfgw_case(),
        # Maxwell stress-energy is traceless, so rho c^2 + sum of principal pressures = 2u >= 0:
        # every electromagnetic field has positive active gravitational mass density.
        "em_active_mass_density_over_energy_density": 2.0,
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
