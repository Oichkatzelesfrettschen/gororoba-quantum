import bdsc_certificate as cert
import numpy as np
import pytest

# Both ladder templates, from the interior source the frozen target uses and from either end of the array, where one
# side of the ladder is empty.
CASES = [(name, source) for name in cert.PREPARATION_DESCRIPTIONS for source in (0, 12, cert.MODES - 1)]


def _check(condition: object, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _column(source: int, residue: complex) -> np.ndarray:
    """A photon left on the source mode, with `residue` as the amplitude of the mode farthest from it."""
    column = np.zeros(cert.MODES, dtype=complex)
    column[source] = 1.0
    column[0 if source == cert.MODES - 1 else cert.MODES - 1] = residue
    return column / np.linalg.norm(column)


def _angles(name: str, source: int, column: np.ndarray) -> np.ndarray:
    return cert.template_params(name, column, source, modes=cert.MODES)


@pytest.mark.parametrize(("name", "source"), CASES)
def test_rounding_residue_takes_the_exact_zero_angles(name: str, source: int) -> None:
    exact = _angles(name, source, _column(source, 0.0))
    residue = _angles(name, source, _column(source, 9e-18))
    _check(np.array_equal(exact, residue), f"residue moved {np.flatnonzero(exact != residue).tolist()}")


@pytest.mark.parametrize(("name", "source"), CASES)
def test_weight_above_the_floor_turns_its_splitter(name: str, source: int) -> None:
    amplitude = 1e-11
    _check(amplitude**2 > cert.LADDER_WEIGHT_FLOOR, "the probe weight sits above the floor")
    exact, resolved = _angles(name, source, _column(source, 0.0)), _angles(name, source, _column(source, amplitude))
    _check(not np.array_equal(exact, resolved), "a resolvable weight left every angle unchanged")


@pytest.mark.parametrize(("name", "source"), CASES)
def test_ladder_reaches_the_column_through_a_residue(name: str, source: int) -> None:
    column = _column(source, 9e-18)
    ops = cert.template_ops(name, source, modes=cert.MODES)
    reached = cert.template_unitary(ops, _angles(name, source, column), modes=cert.MODES)[:, source]
    _check(np.allclose(reached, column, rtol=0, atol=1e-12), "the ladder misses the column")
