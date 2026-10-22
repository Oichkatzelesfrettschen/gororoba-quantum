"""Density evolution and measured rendering retain physical and provenance boundaries."""

import numpy as np
import pytest

from hypercomplex_dynamics import dephase_evolve, shot_diagnostics
from hypercomplex_operators import periodic_generator


def test_dephasing_preserves_density_and_rejects_negative_rate() -> None:
    state = np.zeros(8, dtype=complex)
    state[0] = 1
    density = np.outer(state, state.conj())
    evolved = dephase_evolve(density, periodic_generator(4, 1), 0.25, 0.3)
    np.testing.assert_allclose(np.trace(evolved), 1, atol=1e-12)
    np.testing.assert_allclose(evolved, evolved.conj().T, atol=1e-12)
    if np.linalg.eigvalsh(evolved).min() < -1e-12:
        raise RuntimeError("a completely positive channel must preserve density positivity")
    with pytest.raises(ValueError):
        dephase_evolve(density, periodic_generator(4, 1), 0.25, -0.1)


def test_ordered_shots_expose_non_iid_structure() -> None:
    diagnostic = shot_diagnostics([0] * 128 + [1] * 128)
    if diagnostic["lag_one_correlation"] < 0.9 or diagnostic["block_mean_range"] != 1:
        raise RuntimeError("a contiguous drift step must remain visible")
