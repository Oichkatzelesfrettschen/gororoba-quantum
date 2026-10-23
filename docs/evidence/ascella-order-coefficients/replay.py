"""Check order-coherence coefficients and render an explicitly theoretical atlas."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import matplotlib
import numpy as np
import sympy as sp

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from hypercomplex_operators import order_interferometer  # noqa: E402
from parallel import ordered_map  # noqa: E402

FAMILY_ALPHA = 0.01
PRIMARY_ENDPOINTS = 27
SUPERSEDED_ENDPOINTS = 17
EVENTS_PER_ITERATION = 8192
COEFFICIENT_TOLERANCE = 0.05
MUTATION_DARK_TOLERANCE = 0.05
SIGN_EVEN_TWIST = 0.2


def check_point(angles: tuple[float, float]) -> dict[str, float]:
    """Compare the repository matrix with its coefficient and coherence formulas."""
    theta, phi = angles
    state = order_interferometer(theta, phi)[:, 0]
    expected = np.array(
        [np.exp(1j * theta) * math.cos(phi), -math.cos(theta) * math.sin(phi), 0, 1j * math.sin(theta) * math.sin(phi)]
    )
    probabilities = np.abs(state) ** 2
    coherence = 2 * state[0].conjugate() * state[3]
    predicted = complex(math.sin(theta) ** 2 * math.sin(2 * phi), 0.5 * math.sin(2 * theta) * math.sin(2 * phi))
    dark = float(probabilities[2] + probabilities[3])
    return {
        "state_residual": float(np.max(np.abs(state - expected))),
        "coherence_residual": float(abs(coherence - predicted)),
        "dark_residual": abs(dark - math.sin(theta) ** 2 * math.sin(phi) ** 2),
        "purity_minor_residual": float(abs(abs(coherence) ** 2 - 4 * probabilities[0] * probabilities[3])),
    }


def report() -> dict[str, Any]:
    """Produce exact identities, a finite source cross-check and pilot observations."""
    theta = sp.symbols("theta", real=True)
    horizontal = sp.sin(theta) ** 2
    vertical = sp.sin(2 * theta) / 2
    dark = horizontal / 2
    identities = {
        "coherence_circle": sp.trigsimp((horizontal - sp.Rational(1, 2)) ** 2 + vertical**2 - sp.Rational(1, 4)),
        "dark_coherence_link": sp.simplify(horizontal - 2 * dark),
        "quadrature_dark_link": sp.trigsimp(vertical**2 - 2 * dark * (1 - 2 * dark)),
    }
    attenuation, rotation = sp.symbols("attenuation rotation", real=True)
    constant_vector = attenuation * sp.Matrix([sp.cos(rotation), sp.sin(rotation)]) / 2
    sine_vector = attenuation * sp.Matrix([-sp.sin(rotation), sp.cos(rotation)]) / 2
    identities.update(
        {
            "rotated_coefficient_orthogonality": sp.simplify(constant_vector.dot(sine_vector)),
            "rotated_coefficient_equal_norm": sp.simplify(
                constant_vector.dot(constant_vector) - sine_vector.dot(sine_vector)
            ),
            "rotated_coefficient_orientation": sp.trigsimp(
                sp.Matrix.hstack(constant_vector, sine_vector).det() - attenuation**2 / 4
            ),
        }
    )
    gain_real, gain_imag, common_phase = sp.symbols("gain_real gain_imag common_phase", real=True)
    gain = gain_real + sp.I * gain_imag
    complex_coherence = horizontal + sp.I * vertical
    identities.update(
        {
            "complex_coherence_form": sp.simplify(
                sp.expand_complex(complex_coherence - (1 - sp.exp(-2 * sp.I * theta)) / 2)
            ),
            "gain_model_coefficients": sp.simplify(
                sp.expand_complex(
                    gain * complex_coherence
                    - (gain / 2 - gain / 2 * sp.cos(2 * theta) + sp.I * gain / 2 * sp.sin(2 * theta))
                )
            ),
            "common_phase_cancels": sp.simplify(
                sp.expand_complex(
                    2
                    * sp.conjugate(sp.exp(sp.I * common_phase) * sp.cos(theta))
                    * (sp.exp(sp.I * common_phase) * sp.I * sp.sin(theta))
                    - 2 * sp.cos(theta) * sp.I * sp.sin(theta)
                )
            ),
        }
    )
    if any(value != 0 for value in identities.values()):
        raise ValueError("an exact coefficient identity fails")
    angles = [(index * math.pi / 5, sign * math.pi / 4) for index in range(5) for sign in (-1, 1)]
    angles += [(index * math.pi / 13, index * math.pi / 17) for index in range(-20, 21)]
    checks = ordered_map(check_point, angles)
    maxima = {key: max(row[key] for row in checks) for key in checks[0]}
    if max(maxima.values()) > 1e-12:
        raise ValueError("repository matrix disagrees with coefficient formulas")
    samples = np.arange(5) * np.pi / 5
    basis = np.column_stack(
        (np.ones(5), np.cos(2 * samples), np.sin(2 * samples), np.cos(4 * samples), np.sin(4 * samples))
    )
    values = np.column_stack((np.sin(samples) ** 2, np.sin(2 * samples) / 2, np.sin(samples) ** 2 / 2))
    coefficients = np.linalg.lstsq(basis, values, rcond=None)[0].T
    expected_coefficients = np.array([[0.5, -0.5, 0, 0, 0], [0, 0, 0.5, 0, 0], [0.25, -0.25, 0, 0, 0]])
    if np.max(np.abs(coefficients - expected_coefficients)) > 1e-12:
        raise ValueError("harmonic coefficient decomposition fails")
    pilot_path = ROOT / "results/quandela/runs/ascella-mosaiq-update-order-retry/analysis.json"
    pilot = json.loads(pilot_path.read_text())
    transform = np.linalg.inv(basis)
    # Arms run phi = +pi/4, -pi/4, -pi/4, +pi/4: the sign-odd estimator is (z_+ - z_-)/2, the sign-even (z_+ + z_-)/2.
    analyzer_weights = np.kron(transform, np.array([[1, -1, -1, 1]]) / 4)
    sign_even_weights = np.kron(transform, np.ones((1, 4)) / 4)
    direct_weights = np.kron(transform, np.ones((1, 4)) / 4)
    log_factor = 0.5 * math.log(2 / (FAMILY_ALPHA / PRIMARY_ENDPOINTS))
    analyzer_radii = np.sqrt(log_factor * np.sum(analyzer_weights**2, axis=1) * 4 / EVENTS_PER_ITERATION)
    sign_even_radii = np.sqrt(log_factor * np.sum(sign_even_weights**2, axis=1) * 4 / EVENTS_PER_ITERATION)
    radius_scale = math.sqrt(
        math.log(2 * PRIMARY_ENDPOINTS / FAMILY_ALPHA) / math.log(2 * SUPERSEDED_ENDPOINTS / FAMILY_ALPHA)
    )
    direct_radii = np.sqrt(log_factor * np.sum(direct_weights**2, axis=1) / EVENTS_PER_ITERATION)
    # Each sampled value is the basis row dotted with the coefficient vector, so a coefficient box of half-widths r
    # bounds the value at theta_k by sum_j |basis[k, j]| r_j.
    envelope = np.abs(basis)
    ideal_contrast = math.sin(math.pi / 5) ** 2 / 2
    complex_ideal = np.sin(samples) ** 2 + 1j * np.sin(2 * samples) / 2
    dark_ideal = np.sin(samples) ** 2 / 2
    plus = complex_ideal * (1 + 1j * SIGN_EVEN_TWIST)
    minus = -complex_ideal * (1 - 1j * SIGN_EVEN_TWIST)
    # |C_+-|^2 = (1 + t^2) |C|^2 = 4 (1 + t^2) p0 p3 with ideal p0 = cos(pi/4)^2, so bright mode population
    # (1 + t^2)/2 saturates the 0,3 positivity minor X^2 + Y^2 <= 4 p0 p3 and mode 1 takes the remainder.
    bright = 0.5 * (1 + SIGN_EVEN_TWIST**2)
    remainder = 1 - bright - dark_ideal
    if np.max(np.abs((plus - minus) / 2 - complex_ideal)) > 1e-12:
        raise ValueError("the sign-even counterexample changes the sign-odd projection")
    if np.min(remainder) < 0 or np.max(np.abs(np.abs(plus) ** 2 - 4 * bright * dark_ideal)) > 1e-12:
        raise ValueError("the sign-even counterexample is not a positive state")
    sign_even = (plus + minus) / 2
    even_coefficients = transform @ np.column_stack((sign_even.real, sign_even.imag))
    # At expected counts an endpoint's interval is its value +- radius; the counterexample is a required negative
    # control, so some sign-even interval must lie wholly outside the coefficient tolerance.
    rejected = [
        {"row": row, "basis": basis_name, "value": float(even_coefficients[index, column])}
        for column, row in enumerate(("X", "Y"))
        for index, basis_name in enumerate(("constant", "cos(2 theta)", "sin(2 theta)", "cos(4 theta)", "sin(4 theta)"))
        if abs(even_coefficients[index, column]) - sign_even_radii[index] > COEFFICIENT_TOLERANCE
    ]
    if not rejected:
        raise ValueError("the expanded endpoint family does not reject the sign-even counterexample")
    return {
        "evidence_class": "exact identities and local matrix computation; artwork is theoretical",
        "operator_sha256": hashlib.sha256(
            (ROOT / "gororoba_quantum/hypercomplex_operators.py").read_bytes()
        ).hexdigest(),
        "pilot_analysis_sha256": hashlib.sha256(pilot_path.read_bytes()).hexdigest(),
        "exact_zero_residuals": {key: str(value) for key, value in identities.items()},
        "numerical_points": len(angles),
        "maximum_residuals": maxima,
        "coefficient_basis": ["constant", "cos(2 theta)", "sin(2 theta)", "cos(4 theta)", "sin(4 theta)"],
        "coefficient_rows": ["X", "Y", "dark"],
        "coefficients": coefficients.tolist(),
        "primary_endpoints": PRIMARY_ENDPOINTS,
        "hoeffding_radii_at_8192": {
            "analyzer_coefficients": analyzer_radii.tolist(),
            "sign_even_analyzer_coefficients": sign_even_radii.tolist(),
            "dark_coefficients": direct_radii.tolist(),
            "mutation_difference": math.sqrt(log_factor / EVENTS_PER_ITERATION),
            "mutation_dark": math.sqrt(log_factor * 0.5 / EVENTS_PER_ITERATION),
        },
        "superseded_endpoints": SUPERSEDED_ENDPOINTS,
        "radius_scale_from_superseded_endpoints": radius_scale,
        "events_per_iteration_for_superseded_radii": EVENTS_PER_ITERATION * radius_scale**2,
        "sign_specific_coefficient_radii": (analyzer_radii + sign_even_radii).tolist(),
        "sign_specific_coefficient_tolerance": 2 * COEFFICIENT_TOLERANCE,
        "pointwise_envelope_of_coefficient_tolerance": (COEFFICIENT_TOLERANCE * envelope.sum(axis=1)).tolist(),
        "simultaneous_xy_pointwise_radii": (envelope @ analyzer_radii).tolist(),
        "mutation": {
            "ideal_contrast": ideal_contrast,
            "dark_tolerance": MUTATION_DARK_TOLERANCE,
            "equal_contrast_counterexample": {"target_dark": ideal_contrast + 0.08, "mutation_dark": 0.08},
        },
        "sign_even_counterexample": {
            "twist": SIGN_EVEN_TWIST,
            "bright_population": bright,
            "minimum_remaining_population": float(np.min(remainder)),
            "maximum_sign_even_magnitude": float(np.max(np.abs(sign_even))),
            "sign_even_coefficients": even_coefficients.T.tolist(),
            "rejected_at_expected_counts": rejected,
        },
        "pilot_dark_counts": [
            {
                "name": row["name"],
                "dark": sum(row["counts"][2:]),
                "eligible": row["accepted_samples"],
            }
            for row in pilot["observations"]
        ],
        "versions": {"numpy": np.__version__, "sympy": sp.__version__, "matplotlib": matplotlib.__version__},
    }


def render(destination: Path, radii: list[float]) -> None:
    """Draw predicted curves; hardware points require a separate retained rendering."""
    matplotlib.rcParams["svg.hashsalt"] = "ascella-order-coefficients"
    theta = np.linspace(0, np.pi, 513)
    horizontal = np.sin(theta) ** 2
    vertical = np.sin(2 * theta) / 2
    dark = horizontal / 2
    sample_theta = np.arange(5) * np.pi / 5
    sample_x = np.sin(sample_theta) ** 2
    sample_y = np.sin(2 * sample_theta) / 2
    figure, panels = plt.subplots(1, 4, figsize=(18, 4.9), layout="constrained")
    figure.suptitle("Order interference: coefficient atlas | THEORY ONLY", fontsize=16)
    traced = panels[0].scatter(horizontal, vertical, c=theta / np.pi, cmap="twilight", s=10)
    figure.colorbar(traced, ax=panels[0], label="theta / pi", shrink=0.8)
    for start_index in (64, 192, 320, 448):
        panels[0].annotate(
            "",
            xy=(horizontal[start_index + 8], vertical[start_index + 8]),
            xytext=(horizontal[start_index], vertical[start_index]),
            arrowprops={"arrowstyle": "->", "color": "black"},
        )
        panels[0].annotate(
            "",
            xy=(horizontal[start_index + 8] - 0.06, -vertical[start_index + 8]),
            xytext=(horizontal[start_index] - 0.06, -vertical[start_index]),
            arrowprops={"arrowstyle": "->", "color": "slateblue"},
        )
    panels[0].plot(horizontal, -vertical, color="slateblue", alpha=0.6, label="conjugate: reversed traversal")
    panels[0].errorbar(
        sample_x,
        sample_y,
        xerr=radii,
        yerr=radii,
        fmt="o",
        color="black",
        markersize=4,
        capsize=2,
        label="planned angles, simultaneous X/Y radius",
    )
    for index, (x, y) in enumerate(zip(sample_x, sample_y, strict=True)):
        panels[0].annotate(f"{index}pi/5", (x, y), textcoords="offset points", xytext=(6, 4), fontsize=7)
    panels[0].scatter([0], [0], marker="x", color="red", s=65, label="diagonal mixture; also ideal at theta = 0")
    panels[0].set(xlabel="X coherence", ylabel="Y coherence", title="Sign-odd coherence circle", aspect="equal")
    panels[0].legend(fontsize=6, loc="center")
    panels[1].plot(theta / np.pi, np.zeros_like(theta), color="gray", label="ideal sign-even X and Y")
    panels[1].plot(
        theta / np.pi, -0.2 * vertical, linestyle="--", color="darkorange", label="counterexample sign-even X"
    )
    panels[1].plot(
        theta / np.pi, 0.2 * horizontal, linestyle=":", color="darkorange", label="counterexample sign-even Y"
    )
    panels[1].set(
        xlabel="theta / pi",
        ylabel="sign-even response",
        title="Sign-even response: primary endpoints, ideal zero",
    )
    panels[1].legend(fontsize=7)
    panels[2].plot(theta / np.pi, horizontal, label="X: even in theta")
    panels[2].plot(theta / np.pi, vertical, label="Y: odd in theta")
    panels[2].plot(theta / np.pi, dark, label="dark probability")
    panels[2].set(xlabel="theta / pi", ylabel="predicted response", title="Coefficient harmonics")
    panels[2].legend(fontsize=7)
    panels[3].plot(dark, vertical, color="teal")
    panels[3].set(xlabel="dark probability", ylabel="Y coherence", title="Intensity hides the two branches")
    for panel in panels:
        panel.grid(alpha=0.2)
    figure.savefig(destination, metadata={"Date": None})
    plt.close(figure)
    if destination.suffix == ".svg":
        destination.write_text("\n".join(line.rstrip() for line in destination.read_text().splitlines()) + "\n")


def matches(retained: Any, fresh: Any) -> bool:
    """Equal structure and values; floats agree within the replay's 1e-12 residual bound."""
    if isinstance(retained, dict) and isinstance(fresh, dict):
        return retained.keys() == fresh.keys() and all(matches(retained[k], fresh[k]) for k in retained)
    if isinstance(retained, list) and isinstance(fresh, list):
        return len(retained) == len(fresh) and all(matches(a, b) for a, b in zip(retained, fresh, strict=True))
    if isinstance(retained, float) or isinstance(fresh, float):
        return abs(retained - fresh) <= 1e-12
    return bool(retained == fresh)


if __name__ == "__main__":
    evidence = report()
    target = Path(__file__).resolve().parent
    if "--check" in sys.argv:
        retained = json.loads((target / "derivation.json").read_text())
        # Tool versions describe the writing host; residuals are bounded by report() itself.
        ignored = ("versions", "maximum_residuals")
        if not matches(
            {k: v for k, v in retained.items() if k not in ignored},
            {k: v for k, v in evidence.items() if k not in ignored},
        ):
            raise SystemExit("derivation.json differs from the recomputed derivation")
        print("derivation.json reproduces")
        raise SystemExit(0)
    if "--write" in sys.argv:
        (target / "derivation.json").write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
        render(target / "coefficient-atlas.svg", evidence["simultaneous_xy_pointwise_radii"])
    print(json.dumps(evidence, indent=2, sort_keys=True))
