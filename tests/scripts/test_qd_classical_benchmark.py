"""Contract for qd_classical_benchmark: the certified separable-Choi bounds equal the known classical optima,
upper-bound every explicit measure-and-prepare instrument, reach their value with a PPT Choi operator, and refuse
inputs outside the program's domain.
"""

from __future__ import annotations

import io
import itertools
import json
from collections.abc import Callable, Mapping, Sequence
from contextlib import redirect_stdout

import numpy as np
import pytest
import qd_classical_benchmark as benchmark
import qd_network_protocol as protocol

UNIFORM = {label: 1.0 / 6.0 for label in benchmark.SIX_LABELS}
Z_WEIGHTED = {"+Z": 0.25, "-Z": 0.25, "+X": 0.125, "-X": 0.125, "+Y": 0.125, "-Y": 0.125}
PLUS_Z_WEIGHTED = {"+Z": 0.5, "-Z": 0.1, "+X": 0.1, "-X": 0.1, "+Y": 0.1, "-Y": 0.1}
BLOCH = {"+Z": (0, 0, 1), "-Z": (0, 0, -1), "+X": (1, 0, 0), "-X": (-1, 0, 0), "+Y": (0, 1, 0), "-Y": (0, -1, 0)}
TOLERANCE = 1e-7


def projector(label: str) -> np.ndarray:
    vector = np.array(benchmark.SIX_AMPLITUDES[label], dtype=complex)
    return np.outer(vector, vector.conj())


def pooled_fidelity(instrument: Sequence[tuple[np.ndarray, np.ndarray]], priors: Mapping[str, float]) -> float:
    """``sum p f / sum p s`` of ``rho -> sum_k tr(M_k rho) sigma_k``, computed without the Choi operator."""
    numerator = 0.0
    accepted = 0.0
    for label, weight in priors.items():
        rho = projector(label)
        for effect, prepared in instrument:
            success = float(np.trace(effect @ rho).real)
            accepted += weight * success
            numerator += weight * success * float(np.trace(rho @ prepared).real)
    return numerator / accepted


def profile_from_operator(offset: float, tilt: Sequence[float]) -> dict[str, float]:
    """Six-state success ``tr[K psi^T]`` of ``K = offset I + tilt . sigma``; the transpose reverses the Y tilt."""
    return {label: offset + tilt[0] * axis[0] - tilt[1] * axis[1] + tilt[2] * axis[2] for label, axis in BLOCH.items()}


def test_uniform_six_state_bound_is_two_thirds_and_reached_by_measure_and_prepare() -> None:
    result = benchmark.six_state_benchmark(UNIFORM)
    if abs(result.certified - 2.0 / 3.0) > TOLERANCE or result.gap > benchmark.GAP_LIMIT:
        raise AssertionError(f"uniform six-state bound {result.certified}")
    grid = [fidelity for fidelity, _ in protocol.measure_and_prepare_grid()]
    if max(grid) > result.certified + 1e-12 or max(grid) < result.certified - TOLERANCE:
        raise AssertionError("the measure-and-prepare grid and the certified bound disagree")


def test_known_optima() -> None:
    bb84 = benchmark.classical_benchmark(
        [benchmark.SIX_AMPLITUDES[label] for label in ("+Z", "-Z", "+X", "-X")], [0.25] * 4
    )
    # Breidbart measurement: (1 + cos^2(pi/4))/2.
    if abs(bb84.certified - 0.75) > TOLERANCE:
        raise AssertionError(f"BB84 bound {bb84.certified}")
    # Measure Z and prepare the outcome: 2 * (1/4) * 1 + 4 * (1/8) * (1/2).
    if abs(benchmark.six_state_benchmark(Z_WEIGHTED).certified - 0.75) > TOLERANCE:
        raise AssertionError("Z-weighted bound")


def test_post_selection_raises_the_unequal_prior_bound() -> None:
    """Keep only the +Z outcome of a Z measurement: (0.5 + 0.4 * 0.25) / (0.5 + 0.4 * 0.5) = 6/7."""
    keep_plus = [(projector("+Z"), projector("+Z"))]
    always = [(projector("+Z"), projector("+Z")), (projector("-Z"), projector("-Z"))]
    if abs(pooled_fidelity(keep_plus, PLUS_Z_WEIGHTED) - 6.0 / 7.0) > 1e-12:
        raise AssertionError("post-selected instrument value")
    if abs(pooled_fidelity(always, PLUS_Z_WEIGHTED) - 0.8) > 1e-12:
        raise AssertionError("trace-preserving instrument value")
    if abs(benchmark.six_state_benchmark(PLUS_Z_WEIGHTED).certified - 6.0 / 7.0) > TOLERANCE:
        raise AssertionError("certified bound misses the post-selected optimum")


def test_certified_bound_dominates_every_grid_instrument() -> None:
    bound = benchmark.six_state_benchmark(PLUS_Z_WEIGHTED).certified
    directions = protocol.BLOCH_GRID
    for measured, prepared, keep_minus in itertools.product(directions, directions, protocol.KEEP_MINUS_WEIGHTS):
        instrument = [
            (protocol.bloch_projector(measured), protocol.bloch_projector(prepared)),
            (
                keep_minus * protocol.bloch_projector([-v for v in measured]),
                protocol.bloch_projector([-v for v in prepared]),
            ),
        ]
        if pooled_fidelity(instrument, PLUS_Z_WEIGHTED) > bound + 1e-12:
            raise AssertionError(f"grid instrument {measured}, {prepared}, {keep_minus} exceeds the bound")


def test_achieving_choi_operator_is_separable_and_trace_bounded() -> None:
    profile = profile_from_operator(0.6, (0.1, -0.05, 0.2))
    for result in (
        benchmark.six_state_benchmark(PLUS_Z_WEIGHTED),
        benchmark.six_state_benchmark(UNIFORM, profile, "average"),
    ):
        choi = result.choi
        for operator in (choi, benchmark.partial_transpose_input(choi)):
            if np.linalg.eigvalsh(operator).min() < -benchmark.FEASIBILITY_TOLERANCE:
                raise AssertionError("the achieving Choi operator leaves the PPT cone")
    acceptance = benchmark.partial_trace_output(result.choi)
    for label, target in profile.items():
        if abs(float(np.trace(acceptance @ projector(label).T).real) - target) > benchmark.FEASIBILITY_TOLERANCE:
            raise AssertionError(f"the achieving map misses the success of {label}")


@pytest.mark.parametrize(
    "offset, tilt",
    [(0.5, (0.0, 0.0, 0.0)), (0.7, (0.0, 0.0, 0.2)), (0.5, (0.1, -0.1, 0.1)), (0.3, (0.1, 0.15, -0.1))],
)
def test_realizable_profiles_keep_the_uniform_bound(offset: float, tilt: tuple[float, float, float]) -> None:
    profile = profile_from_operator(offset, tilt)
    for figure in benchmark.FIGURES:
        result = benchmark.six_state_benchmark(UNIFORM, profile, figure)
        if result.certified > 2.0 / 3.0 + TOLERANCE or result.gap > benchmark.GAP_LIMIT:
            raise AssertionError(f"{figure} bound {result.certified} under profile {profile}")


def test_attempts_set_the_priors() -> None:
    equal = benchmark.attempts_benchmark(dict.fromkeys(benchmark.SIX_LABELS, 400))
    if abs(equal.certified - 2.0 / 3.0) > TOLERANCE:
        raise AssertionError("equal attempts")
    unequal = benchmark.attempts_benchmark({"+Z": 800, "-Z": 800, "+X": 400, "-X": 400, "+Y": 400, "-Y": 400})
    if abs(unequal.certified - 0.75) > TOLERANCE:
        raise AssertionError("attempts proportional to Z_WEIGHTED")


def test_realizable_profile_fit() -> None:
    affine = profile_from_operator(0.6, (0.1, 0.2, -0.1))
    fitted, residual = benchmark.realizable_profile(affine)
    if residual > 1e-12 or any(abs(fitted[label] - affine[label]) > 1e-12 for label in affine):
        raise AssertionError("an affine profile refits exactly")
    measured = {"+Z": 0.9, "-Z": 0.5, "+X": 0.72, "-X": 0.70, "+Y": 0.69, "-Y": 0.71}
    fitted, residual = benchmark.realizable_profile(measured)
    pair_sums = {round(fitted[f"+{axis}"] + fitted[f"-{axis}"], 12) for axis in "XYZ"}
    if len(pair_sums) != 1 or abs(residual - 0.02 / 3.0) > 1e-12:
        raise AssertionError(f"fit {fitted} residual {residual}")
    benchmark.six_state_benchmark(UNIFORM, fitted, "average")


def test_tables_cli() -> None:
    stream = io.StringIO()
    with redirect_stdout(stream):
        status = benchmark.main(["--tables"])
    rows = json.loads(stream.getvalue())
    if status != 0 or rows["six_uniform_free"] != 0.666666667 or rows["bb84_uniform"] != 0.75:
        raise AssertionError(f"tables {rows}")


@pytest.mark.parametrize(
    "call",
    [
        lambda: benchmark.six_state_benchmark(UNIFORM, figure="median"),
        lambda: benchmark.six_state_benchmark(UNIFORM, figure="average"),
        lambda: benchmark.six_state_benchmark({**UNIFORM, "+Z": 0.5}),
        lambda: benchmark.six_state_benchmark({**UNIFORM, "+Z": -1.0 / 6.0, "-Z": 0.5}),
        lambda: benchmark.six_state_benchmark({"+Z": 1.0}),
        lambda: benchmark.classical_benchmark([(1.0, 0.0)], [1.0]),
        lambda: benchmark.classical_benchmark([(1.0, 1.0)], [1.0]),
        lambda: benchmark.classical_benchmark([(1.0, 0.0), (0.0, 1.0)], [1.0]),
        lambda: benchmark.six_state_benchmark(UNIFORM, dict.fromkeys(benchmark.SIX_LABELS, 0.0)),
        lambda: benchmark.six_state_benchmark(UNIFORM, dict.fromkeys(benchmark.SIX_LABELS, 1.2)),
        lambda: benchmark.six_state_benchmark(UNIFORM, {**dict.fromkeys(benchmark.SIX_LABELS, 0.5), "+Z": 0.9}),
        lambda: benchmark.six_state_benchmark(UNIFORM, profile_from_operator(0.5, (0.3, 0.3, 0.3))),
        lambda: benchmark.attempts_benchmark({**dict.fromkeys(benchmark.SIX_LABELS, 10), "+Z": 0}),
        lambda: benchmark.attempts_benchmark({"+Z": 10}),
        lambda: benchmark.realizable_profile({"+Z": 0.5}),
    ],
)
def test_domain_refusals(call: Callable[[], object]) -> None:
    with pytest.raises(protocol.ProtocolError):
        call()
