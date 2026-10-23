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
    analyzer_weights = np.kron(transform, np.array([[1, -1, -1, 1]]) / 4)
    direct_weights = np.kron(transform, np.ones((1, 4)) / 4)
    log_factor = 0.5 * math.log(2 / (0.01 / 16))
    analyzer_radii = np.sqrt(log_factor * np.sum(analyzer_weights**2, axis=1) * 4 / 8192)
    direct_radii = np.sqrt(log_factor * np.sum(direct_weights**2, axis=1) / 8192)
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
        "hoeffding_radii_at_8192": {
            "analyzer_coefficients": analyzer_radii.tolist(),
            "dark_coefficients": direct_radii.tolist(),
            "mutation": math.sqrt(log_factor / 8192),
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


def render(destination: Path) -> None:
    """Draw predicted curves; hardware points require a separate retained rendering."""
    matplotlib.rcParams["svg.hashsalt"] = "ascella-order-coefficients"
    theta = np.linspace(0, np.pi, 513)
    horizontal = np.sin(theta) ** 2
    vertical = np.sin(2 * theta) / 2
    dark = horizontal / 2
    sample_theta = np.arange(5) * np.pi / 5
    figure, panels = plt.subplots(1, 3, figsize=(14, 4.7), layout="constrained")
    figure.suptitle("Order interference: coefficient atlas | THEORY ONLY", fontsize=16)
    panels[0].scatter(horizontal, vertical, c=theta / np.pi, cmap="twilight", s=12)
    panels[0].plot(-horizontal, -vertical, color="slateblue", alpha=0.6, label="negative phi")
    panels[0].scatter(
        np.sin(sample_theta) ** 2, np.sin(2 * sample_theta) / 2, color="black", s=22, label="planned angles"
    )
    panels[0].scatter([0], [0], marker="x", color="red", s=65, label="diagonal mixture")
    panels[0].set(xlabel="X coherence", ylabel="Y coherence", title="Signed coherence circles", aspect="equal")
    panels[0].legend(fontsize=8)
    panels[1].plot(theta / np.pi, horizontal, label="X: even in theta")
    panels[1].plot(theta / np.pi, vertical, label="Y: odd in theta")
    panels[1].plot(theta / np.pi, dark, label="dark probability")
    panels[1].set(xlabel="theta / pi", ylabel="predicted response", title="Coefficient harmonics")
    panels[1].legend(fontsize=8)
    panels[2].plot(dark, vertical, color="teal")
    panels[2].set(xlabel="dark probability", ylabel="Y coherence", title="Intensity hides the two branches")
    for panel in panels:
        panel.grid(alpha=0.2)
    figure.savefig(destination, metadata={"Date": None})
    plt.close(figure)
    if destination.suffix == ".svg":
        destination.write_text("\n".join(line.rstrip() for line in destination.read_text().splitlines()) + "\n")


if __name__ == "__main__":
    evidence = report()
    target = Path(__file__).resolve().parent
    if "--write" in sys.argv:
        (target / "derivation.json").write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
        render(target / "coefficient-atlas.svg")
    print(json.dumps(evidence, indent=2, sort_keys=True))
