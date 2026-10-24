"""Registered estimators of the Ascella signed-coherence request: 27 primary endpoints and their decisions.

docs/design/ascella-signed-coherence-conformance.md registers the analysis.
Each of the 64 iterations of results/quandela/cases/ascella_signed_coherence
contributes one statistic over its eligible events, N_i occupation-sum-one
events across all twelve returned modes: z_i = (n_i0 - n_i3) / N_i on an X or
Y readout (range [-1, 1]) and p_i = (n_i2 + n_i3) / N_i on a direct readout
(range [0, 1]). At angle theta_k the sign-odd value is sum(phi_sign * z) / 4,
the sign-even value sum(z) / 4 and the dark value sum(p) / 4 over the four arms
of the block; the five-point transform inv(B), B[k] = (1, cos 2theta_k,
sin 2theta_k, cos 4theta_k, sin 4theta_k), maps each sequence to its five
coefficients. The mutation difference is (p1 - p2 - p3 + p4) / 2 over the
mutation block and the mutation dark probability (p2 + p3) / 2 over its
commuting arms.

Every endpoint is a linear form sum_i c_i s_i, so the Hoeffding radius at
family error alpha split equally over the endpoints is
sqrt(log(2 / alpha_j) / 2 * sum_i c_i^2 (b_i - a_i)^2 / N_i). An endpoint
qualifies when its interval lies inside its tolerance region, is falsified when
the two are disjoint and is inconclusive otherwise; whether the interval
excludes the registered ideal is reported separately. The mutation dark
interval is clipped to [0, 1] and its region is [0, tolerance]. Inference needs
all 64 attributable iterations with positive N_i; any other input returns a
record whose complete flag is false and carries no decisions.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

import numpy as np

ENTRIES = 64
MODES = 12
ANGLES = 5
BASIS_NAMES = ("constant", "cos(2 theta)", "sin(2 theta)", "cos(4 theta)", "sin(4 theta)")
COEFFICIENT_ROWS = (
    ("X", "x", "odd"),
    ("Y", "y", "odd"),
    ("dark", "direct", "dark"),
    ("X", "x", "even"),
    ("Y", "y", "even"),
)


def transform() -> np.ndarray:
    """inv(B) for the planned grid theta_k = k pi/5: row j gives coefficient j from the five sampled values."""
    samples = np.arange(ANGLES) * np.pi / ANGLES
    basis = np.column_stack(
        (np.ones(ANGLES), np.cos(2 * samples), np.sin(2 * samples), np.cos(4 * samples), np.sin(4 * samples))
    )
    return np.asarray(np.linalg.inv(basis))


def endpoint_weights(settings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The 27 endpoints as weight vectors over the 64 iterations, in registered order."""
    if len(settings) != ENTRIES:
        raise ValueError(f"the request holds {len(settings)} settings, not {ENTRIES}")
    inverse = transform()
    endpoints: list[dict[str, Any]] = []
    for row, readout, parity in COEFFICIENT_ROWS:
        for index, basis in enumerate(BASIS_NAMES):
            weights = np.zeros(ENTRIES)
            for position, setting in enumerate(settings):
                if setting["block"] == "mutation" or setting["readout"] != readout:
                    continue
                arm = setting["phi_sign"] if parity == "odd" else 1
                weights[position] = inverse[index, setting["theta_index"]] * arm / 4
            name = f"{'dark' if parity == 'dark' else f'{row}_{parity}'} {basis}"
            endpoints.append({"name": name, "row": row, "parity": parity, "basis": basis, "weights": weights})
    difference = np.zeros(ENTRIES)
    closure = np.zeros(ENTRIES)
    for position, setting in enumerate(settings):
        if setting["block"] == "mutation":
            difference[position] = 0.5 if setting["generator"] == "j" else -0.5
            closure[position] = 0.5 if setting["generator"] == "i" else 0.0
    endpoints.append({"name": "mutation difference", "row": "mutation", "parity": "contrast", "weights": difference})
    endpoints.append({"name": "mutation dark", "row": "mutation", "parity": "closure", "weights": closure})
    return endpoints


def statistics(
    settings: list[dict[str, Any]], mode_counts: Sequence[Sequence[float] | None]
) -> tuple[np.ndarray, np.ndarray]:
    """Per-iteration statistics and eligible totals from twelve-mode single-photon counts."""
    counts = np.asarray(mode_counts, dtype=float)
    if counts.shape != (ENTRIES, MODES) or not np.isfinite(counts).all() or (counts < 0).any():
        raise ValueError(f"counts must be {ENTRIES} finite non-negative twelve-mode rows, not {counts.shape}")
    eligible = counts.sum(axis=1)
    if (eligible <= 0).any():
        raise ValueError("every iteration needs a positive eligible count")
    analyzer = np.array([setting["readout"] != "direct" for setting in settings])
    values = np.where(analyzer, (counts[:, 0] - counts[:, 3]) / eligible, (counts[:, 2] + counts[:, 3]) / eligible)
    return values, eligible


def registered_ideals(settings: list[dict[str, Any]]) -> np.ndarray:
    """The ideal statistic of every iteration from its registered manifest ideal."""
    return np.array([setting["ideal"]["dark" if setting["readout"] == "direct" else "z"] for setting in settings])


def decide(interval: tuple[float, float], region: tuple[float, float]) -> str:
    if region[0] <= interval[0] and interval[1] <= region[1]:
        return "qualifies"
    if interval[1] < region[0] or region[1] < interval[0]:
        return "falsified"
    return "inconclusive"


def analyze(manifest: dict[str, Any], mode_counts: Sequence[Sequence[float] | None] | None) -> dict[str, Any]:
    """The 27 endpoints of one acquisition or synthetic response, or an incomplete record without decisions."""
    settings = manifest["settings"]
    registered = manifest["preregistered"]
    if mode_counts is None or len(mode_counts) != ENTRIES or any(row is None for row in mode_counts):
        present = 0 if mode_counts is None else sum(row is not None for row in mode_counts)
        return {"complete": False, "reason": f"{present} of {ENTRIES} iterations attributable", "endpoints": []}
    empty = [index for index, row in enumerate(mode_counts) if row is not None and sum(row) <= 0]
    if empty:
        return {"complete": False, "reason": f"iterations {empty} have no eligible events", "endpoints": []}
    values, eligible = statistics(settings, mode_counts)
    ideals = registered_ideals(settings)
    ranges = np.array([2.0 if setting["readout"] != "direct" else 1.0 for setting in settings])
    endpoints = endpoint_weights(settings)
    if len(endpoints) != registered["primary_endpoints"]:
        raise ValueError(f"{len(endpoints)} endpoints, not the registered {registered['primary_endpoints']}")
    log_factor = 0.5 * math.log(2 / (registered["family_alpha"] / len(endpoints)))
    # One weight row per endpoint: values, ideals and radii come from the same matrix products.
    matrix = np.vstack([endpoint["weights"] for endpoint in endpoints])
    estimates = matrix @ values
    ideal_values = matrix @ ideals + 0.0
    radii = np.sqrt(log_factor * (matrix**2 @ (ranges**2 / eligible)))
    rows = []
    for endpoint, value, ideal, radius in zip(endpoints, estimates, ideal_values, radii, strict=True):
        low, high = float(value - radius), float(value + radius)
        if endpoint["parity"] == "closure":
            low, high = max(0.0, low), min(1.0, high)
            region = (0.0, registered["mutation_dark_tolerance"])
        else:
            tolerance = (
                registered["mutation_difference_tolerance"]
                if endpoint["parity"] == "contrast"
                else registered["coefficient_tolerance"]
            )
            region = (float(ideal) - tolerance, float(ideal) + tolerance)
        labels: dict[str, str] = {key: endpoint[key] for key in ("name", "row", "parity", "basis") if key in endpoint}
        rows.append(
            {
                **labels,
                "value": float(value),
                "ideal": float(ideal),
                "radius": float(radius),
                "interval": [low, high],
                "tolerance_region": list(region),
                "verdict": decide((low, high), region),
                "ideal_excluded": not low <= float(ideal) <= high,
            }
        )
    return {
        "complete": True,
        "eligible_total": float(eligible.sum()),
        "endpoints": rows,
        "verdicts": {
            verdict: sum(row["verdict"] == verdict for row in rows)
            for verdict in ("qualifies", "falsified", "inconclusive")
        },
        "ideal_excluded": [row["name"] for row in rows if row["ideal_excluded"]],
    }
