import bdsc_certificate as cert
import numpy as np

SOURCE = 12


def _check(condition: object, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _column(residue: complex) -> np.ndarray:
    """A photon left on the source mode, with `residue` as the amplitude of mode 0."""
    column = np.zeros(cert.MODES, dtype=complex)
    column[SOURCE] = 1.0
    column[0] = residue
    return column / np.linalg.norm(column)


def _angles(column: np.ndarray) -> np.ndarray:
    return cert.template_params("outward-ladder", column, SOURCE, modes=cert.MODES)


def test_rounding_residue_takes_the_exact_zero_angles() -> None:
    exact = _angles(_column(0.0))
    residue = _angles(_column(9e-18))
    _check(np.array_equal(exact, residue), f"residue moved {np.flatnonzero(exact != residue).tolist()}")
    _check(not np.any(np.isclose(np.abs(residue), np.pi)), "a residue weight produced a pi splitter")


def test_weight_above_the_floor_turns_its_splitter() -> None:
    amplitude = 1e-11
    _check(amplitude**2 > cert.LADDER_WEIGHT_FLOOR, "the probe weight sits above the floor")
    exact, resolved = _angles(_column(0.0)), _angles(_column(amplitude))
    _check(not np.array_equal(exact, resolved), "a resolvable weight left every angle unchanged")


def test_ladder_reaches_the_column_through_a_residue() -> None:
    column = _column(9e-18)
    ops = cert.template_ops("outward-ladder", SOURCE, modes=cert.MODES)
    reached = cert.template_unitary(ops, _angles(column), modes=cert.MODES)[:, SOURCE]
    _check(np.allclose(reached, column, rtol=0, atol=1e-12), "the ladder misses the column")
