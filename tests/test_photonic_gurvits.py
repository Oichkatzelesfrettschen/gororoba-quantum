"""Deterministic algebra/oracle tests; no QRNG draw or statistical coverage claim."""

from __future__ import annotations

import itertools
import math
from collections.abc import Iterator
from typing import Any, cast

import numpy as np
import pytest

import parallel
from photonic_gaussian import (
    FockHusimiKernel,
    estimate_fock_husimi,
    hafnian,
    median_of_means_plan,
    pure_gaussian_probability,
)
from photonic_marginals import collision_free_marginal, low_rank_coefficients
from photonic_permanents import (
    AdditiveEstimate,
    estimate_fock_amplitude,
    estimate_permanent,
    estimate_repeated_permanent,
    evaluate_roots,
    fock_amplitude,
    hoeffding_radius,
    permanent_ryser,
    repeated_kernel,
    sample_budget,
)


def close(actual: Any, expected: Any, atol: float = 1e-10) -> None:
    np.testing.assert_allclose(actual, expected, atol=atol, rtol=atol)


def require(condition: bool, message: str = "invariant failed") -> None:
    if not condition:
        raise AssertionError(message)


def direct_permanent(a: np.ndarray) -> complex:
    """Permutation definition independent of Gray-code inclusion/exclusion."""
    terms = (math.prod(a[i, j] for i, j in enumerate(perm)) for perm in itertools.permutations(range(len(a))))
    return complex(sum(terms))


def occupations(n: int, m: int) -> Iterator[tuple[int, ...]]:
    if m == 0:
        if n == 0:
            yield ()
    elif m == 1:
        yield (n,)
    else:
        for first in range(n + 1):
            for rest in occupations(n - first, m - 1):
                yield (first, *rest)


def creation_oracle(u: np.ndarray, inputs: tuple[int, ...]) -> dict[tuple[int, ...], complex]:
    """Apply creation operators to normalised Fock states, not permanents."""
    states = {(0,) * len(u): 1 + 0j}
    for source, photons in enumerate(inputs):
        for number in range(photons):
            following: dict[tuple[int, ...], complex] = {}
            for state, amplitude in states.items():
                for output in range(len(u)):
                    target = tuple(count + int(i == output) for i, count in enumerate(state))
                    contribution = amplitude * u[output, source] * math.sqrt((state[output] + 1) / (number + 1))
                    following[target] = following.get(target, 0j) + contribution
            states = following
    return states


def optical_matrix(m: int) -> np.ndarray:
    """Deterministic Fourier matrix with unequal input and output phases."""
    x = np.arange(m)
    q = np.exp(2j * math.pi * np.outer(x, x) / m) / math.sqrt(m)
    return np.exp(0.17j * x)[:, None] * q * np.exp(-0.31j * x)[None, :]


class DeterministicDraws:
    """Controlled test inputs, NOT independent random draws or evidence of coverage."""

    calls = 0

    def integers(self, low: int, high: np.ndarray, *, size: tuple[int, int]) -> np.ndarray:
        self.calls += 1
        points = list(itertools.product(*(range(int(order)) for order in high)))
        return np.asarray([points[i % len(points)] for i in range(size[0])], dtype=np.int64).reshape(size)

    def gamma(self, shape: np.ndarray, scale: float, *, size: tuple[int, int]) -> np.ndarray:
        self.calls += 1
        return np.broadcast_to(shape * scale, size).copy()

    def uniform(self, low: float, high: float, *, size: tuple[int, int]) -> np.ndarray:
        self.calls += 1
        return np.full(size, (low + high) / 3)


class RecordingDraws:
    """Records the arguments of each draw and returns fixed values that expose the sampling law.

    gamma returns its mean, shape * scale. uniform returns low + (high - low) * f_j in column j, so a change of
    either bound moves the relative phase of the modes. These are controlled inputs, not random draws.
    """

    fractions = (0.25, 0.5, 0.75)

    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[Any, ...], dict[str, Any]]] = []

    def gamma(self, *args: Any, **kwargs: Any) -> np.ndarray:
        self.calls.append(("gamma", args, kwargs))
        shape, scale = args
        return np.broadcast_to(shape * scale, kwargs["size"]).copy()

    def uniform(self, *args: Any, **kwargs: Any) -> np.ndarray:
        self.calls.append(("uniform", args, kwargs))
        low, high = args
        columns = np.asarray(self.fractions[: kwargs["size"][1]])
        return np.broadcast_to(low + (high - low) * columns, kwargs["size"]).copy()


def husimi_closed_form(u: np.ndarray, t: tuple[int, ...], s: tuple[int, ...], phases: np.ndarray) -> complex:
    """<s|U alpha> / <t|alpha> for alpha_i = sqrt(t_i + 1) exp(i phase_i), from the coherent-state overlaps.

    The overlap <n|alpha> carries alpha^n / sqrt(n!) and a factor exp(-|alpha|^2 / 2); the factors of the numerator
    and denominator cancel because U is unitary, so |U alpha| = |alpha|.
    """
    alpha = np.sqrt(np.asarray(t, dtype=float) + 1) * np.exp(1j * phases)
    beta = u @ alpha
    numerator = np.prod([beta[i] ** s[i] / math.sqrt(math.factorial(s[i])) for i in range(len(s))])
    denominator = np.prod([alpha[i] ** t[i] / math.sqrt(math.factorial(t[i])) for i in range(len(t))])
    return complex(numerator / denominator)


def fake_rng() -> tuple[DeterministicDraws, np.random.Generator]:
    draws = DeterministicDraws()
    return draws, cast(np.random.Generator, draws)


@pytest.mark.parametrize("n", range(6))
def test_ryser_against_permutation(n: int) -> None:
    a = np.asarray(
        [complex(((i + 2) * (j + 3)) % 7 - 3, (i - j) % 4 - 2) / 5 for i in range(n) for j in range(n)]
    ).reshape(n, n)
    close(permanent_ryser(a), direct_permanent(a))


@pytest.mark.parametrize("n", range(1, 7))
def test_diagonal_and_triangular(n: int) -> None:
    a = np.triu(np.ones((n, n), dtype=complex))
    np.fill_diagonal(a, [complex(i + 1, 1) / 3 for i in range(n)])
    close(permanent_ryser(a), np.prod(np.diag(a)))


@pytest.mark.parametrize("inputs", [(1, 0, 0), (1, 1, 0), (2, 0, 0), (2, 1, 0), (1, 1, 1)])
def test_general_fock_creation_oracle(inputs: tuple[int, ...]) -> None:
    u = optical_matrix(3)
    expected = creation_oracle(u, inputs)
    computed = {s: fock_amplitude(u, inputs, s) for s in occupations(sum(inputs), 3)}
    for s, amplitude in expected.items():
        close(computed[s], amplitude)
    close(sum(abs(z) ** 2 for z in computed.values()), 1)


@pytest.mark.parametrize("reflectivity", [0.0, 0.2, 0.5, 0.8, 1.0])
def test_hom_and_distinguishable_control(reflectivity: float) -> None:
    r, t = math.sqrt(reflectivity), math.sqrt(1 - reflectivity)
    u = np.asarray([[r, t], [t, -r]])
    close(abs(fock_amplitude(u, [1, 1], [1, 1])) ** 2, (2 * reflectivity - 1) ** 2)
    distinguishable = reflectivity**2 + (1 - reflectivity) ** 2
    close(distinguishable - (2 * reflectivity - 1) ** 2, 2 * reflectivity * (1 - reflectivity))
    close(sum(abs(fock_amplitude(u, [1, 1], s)) ** 2 for s in occupations(2, 2)), 1)


def test_vacuum_and_number_selection() -> None:
    close(fock_amplitude(np.empty((0, 0)), [], []), 1)
    close(fock_amplitude(np.eye(2), [0, 0], [0, 0]), 1)
    close(fock_amplitude(np.eye(2), [1, 0], [0, 0]), 0)


@pytest.mark.parametrize("counts", [(1, 1, 1), (2, 1), (3,), (0, 2, 1)])
@pytest.mark.parametrize("axis", [0, 1])
def test_repeated_root_average_is_permanent(counts: tuple[int, ...], axis: int) -> None:
    n, k = sum(counts), len(counts)
    b = np.asarray([complex(i + j + 1, i - j) / 5 for i in range(n) for j in range(k)]).reshape(n, k)
    source = b if axis == 1 else b.T
    kernel, scale = repeated_kernel(source, counts, axis=axis)
    points = np.asarray(list(itertools.product(*(range(c + 1) for c in kernel.counts))), dtype=np.int64)
    values = evaluate_roots(kernel, points)
    expected = direct_permanent(np.repeat(b, counts, axis=1))
    close(scale * sum(values) / len(values), expected)
    require(max(abs(z) for z in values) <= 1 + 1e-12)


def test_ordinary_samples_and_input_immutability() -> None:
    a = np.asarray([[0.2 + 0.1j, 0.3], [0.4j, -0.1]])
    before = a.copy()
    _, rng = fake_rng()
    result = estimate_permanent(a, rng=rng, samples=4)
    close(result.value, direct_permanent(a))
    close(a, before, atol=0)
    close(result.radius, hoeffding_radius(np.linalg.norm(a, 2) ** 2, 4, 0.01))


def test_repeated_estimator_and_bunched_fock() -> None:
    _, rng = fake_rng()
    result = estimate_repeated_permanent(np.asarray([[1], [2]]), [2], rng=rng, samples=3)
    close(result.value, 4)
    u = np.array([[1, 1], [1, -1]]) / math.sqrt(2)
    estimate = estimate_fock_amplitude(u, [2, 0], [1, 1], rng=rng, samples=12)
    close(estimate.value, fock_amplitude(u, [2, 0], [1, 1]))
    lower, upper = estimate.probability_interval()
    require(lower <= 0.5 <= upper)


def test_structural_estimates_do_not_consume_rng() -> None:
    draws, rng = fake_rng()
    close(estimate_permanent(np.zeros((2, 2)), rng=rng, samples=4).value, 0)
    close(estimate_permanent(np.empty((0, 0)), rng=rng, samples=4).value, 1)
    close(estimate_fock_amplitude(np.eye(2), [1, 0], [0, 0], rng=rng, samples=4).value, 0)
    require(draws.calls == 0)


@pytest.mark.parametrize("epsilon,delta", [(0.5, 0.1), (0.2, 0.01), (0.1, 0.001)])
def test_complex_sample_budget(epsilon: float, delta: float) -> None:
    n = sample_budget(epsilon, delta)
    require(hoeffding_radius(1, n, delta) <= epsilon)
    require(4 * math.exp(-n * epsilon**2 / 4) <= delta * (1 + 1e-14))


def test_probability_disk_geometry() -> None:
    interval = AdditiveEstimate(3 + 4j, 0.2, 0.01, 100, "test", 1).probability_interval()
    close(interval, (4.8**2, 5.2**2))
    close(AdditiveEstimate(0j, 0.2, 0.01, 1, "test", 1).probability_interval(), (0, 0.04))


@pytest.mark.parametrize("n,k", [(0, 1), (1, 1), (3, 1), (4, 2)])
def test_low_rank_identity(n: int, k: int) -> None:
    x = np.asarray([complex(i + j + 1, i - j) / 10 for i in range(n) for j in range(k)]).reshape(n, k)
    y = np.asarray([complex(i - j, i + j + 2) / 9 for i in range(n) for j in range(k)]).reshape(n, k)
    coefficients = low_rank_coefficients(x, y)
    computed = sum(math.prod(math.factorial(a) for a in index) * v for index, v in coefficients.items())
    close(computed, direct_permanent(np.eye(n) + x @ y.T))


@pytest.mark.parametrize("selected", [(), (0,), (2,), (0, 3), (3, 1)])
def test_marginal_against_complete_fock_oracle(selected: tuple[int, ...]) -> None:
    u = optical_matrix(4)
    inputs = (1, 0, 1, 0)
    result = collision_free_marginal(u, inputs, selected)
    reference: dict[tuple[int, ...], float] = {}
    for state, amplitude in creation_oracle(u, inputs).items():
        key = tuple(state[i] for i in selected)
        reference[key] = reference.get(key, 0.0) + abs(amplitude) ** 2
    for key in set(reference) | set(result.probabilities):
        close(result.probabilities.get(key, 0.0), reference.get(key, 0.0))
    close(sum(result.probabilities.values()), 1)


def test_marginal_hom_and_vacuum() -> None:
    h = np.array([[1, 1], [1, -1]]) / math.sqrt(2)
    result = collision_free_marginal(h, [1, 1], [0])
    close([result.probabilities[(i,)] for i in range(3)], [0.5, 0, 0.5])
    close(collision_free_marginal(h, [0, 0], [0]).probabilities[(0,)], 1)


@pytest.mark.parametrize("n", range(5))
def test_hafnian_embeds_permanent(n: int) -> None:
    a = np.asarray([complex(i + j, i - j + 1) / 4 for i in range(n) for j in range(n)]).reshape(n, n)
    b = np.block([[np.zeros_like(a), a], [a.T, np.zeros_like(a)]])
    close(hafnian(b), direct_permanent(a))


@pytest.mark.parametrize("n", [2, 4, 6, 8])
def test_pairing_counts(n: int) -> None:
    close(hafnian(np.ones((n, n))), math.prod(range(1, n, 2)))


def test_loop_and_odd_hafnian() -> None:
    close(hafnian(np.empty((0, 0))), 1)
    close(hafnian([[123]]), 0)
    close(hafnian([[123]], loops=[2j]), 2j)
    close(hafnian([[100, 3j], [3j, -100]], loops=[2, 5]), 10 + 3j)


@pytest.mark.parametrize("k", range(5))
def test_two_mode_squeezed_normalisation(k: int) -> None:
    q = 0.4
    b = np.asarray([[0, q], [q, 0]])
    close(pure_gaussian_probability(b, [k, k]), (1 - q * q) * q ** (2 * k))
    close(pure_gaussian_probability(b, [k, k + 1]), 0)


@pytest.mark.parametrize("k", range(5))
def test_single_mode_squeezed_normalisation(k: int) -> None:
    q = 0.3
    expected = math.sqrt(1 - q * q) * math.comb(2 * k, k) * (q * q / 4) ** k
    close(pure_gaussian_probability([[q]], [2 * k]), expected)


@pytest.mark.parametrize("inputs,outputs", [((1, 1), (2, 0)), ((2, 0), (1, 1)), ((2, 1), (1, 2)), ((1, 2), (1, 2))])
def test_husimi_phase_quadrature(inputs: tuple[int, ...], outputs: tuple[int, ...]) -> None:
    u = optical_matrix(2)
    kernel = FockHusimiKernel(u, inputs, outputs)
    order = sum(inputs) + 1
    points = [
        np.array([1.2, 0.7]) * np.exp(2j * math.pi * np.asarray(indices) / order)
        for indices in itertools.product(range(order), repeat=2)
    ]
    values = parallel.ordered_map(kernel, points)
    close(sum(values) / len(values), fock_amplitude(u, inputs, outputs))


def test_husimi_identity_and_selection() -> None:
    draws, rng = fake_rng()
    result = estimate_fock_husimi(np.eye(2), [2, 1], [2, 1], rng=rng, epsilon=0.5)
    close(result.value, 1)
    close(result.radius, 0.5)
    require(draws.calls == 2)
    close(estimate_fock_husimi(np.eye(2), [1, 0], [0, 0], rng=rng, epsilon=0.5).value, 0)
    close(estimate_fock_husimi(np.eye(2), [0, 0], [0, 0], rng=rng, epsilon=0.5).value, 1)
    require(draws.calls == 2)


@pytest.mark.parametrize(
    "inputs,outputs",
    [((1, 1), (2, 0)), ((2, 1), (1, 2)), ((1, 0), (0, 1))],
)
def test_husimi_sampling_law_and_value(inputs: tuple[int, ...], outputs: tuple[int, ...]) -> None:
    """Gamma(t + 1, 1) radii and Uniform[0, 2 pi) phases, with the value known from the fixed draws."""
    epsilon, delta = 0.5, 0.01
    block_size, groups = median_of_means_plan(epsilon, delta)
    count = block_size * groups
    u = optical_matrix(2)
    draws = RecordingDraws()
    result = estimate_fock_husimi(
        u, inputs, outputs, rng=cast(np.random.Generator, draws), epsilon=epsilon, delta=delta
    )
    require([name for name, _, _ in draws.calls] == ["gamma", "uniform"], "draw order or count differs")
    (_, gamma_args, gamma_kwargs), (_, uniform_args, uniform_kwargs) = draws.calls
    require(len(gamma_args) == 2 and gamma_args[1] == 1, "gamma scale must be 1")
    np.testing.assert_array_equal(gamma_args[0], np.asarray(inputs) + 1)
    require(set(gamma_kwargs) == {"size"} and gamma_kwargs["size"] == (count, 2), "gamma size differs")
    require(uniform_args == (0, 2 * math.pi), "phase range must be [0, 2 pi)")
    require(set(uniform_kwargs) == {"size"} and uniform_kwargs["size"] == (count, 2), "uniform size differs")
    phases = 2 * math.pi * np.asarray(RecordingDraws.fractions[:2])
    close(result.value, husimi_closed_form(u, inputs, outputs, phases))
    require(result.samples == count, "sample count differs from the plan")


@pytest.mark.parametrize("epsilon,delta", [(0.5, 0.1), (0.2, 0.01), (0.1, 0.001)])
def test_median_of_means_plan(epsilon: float, delta: float) -> None:
    block, groups = median_of_means_plan(epsilon, delta)
    require(block * epsilon * epsilon >= 8 - 1e-12)
    require(groups % 2 == 1)
    require(2 * math.exp(-groups / 8) <= delta)


@pytest.mark.parametrize("bad", [np.nan, np.inf, -np.inf])
def test_nonfinite_matrix_rejected(bad: float) -> None:
    with pytest.raises(ValueError, match="finite"):
        permanent_ryser([[bad]])


@pytest.mark.parametrize("bad", [True, -1, 0.5, 1.0])
def test_invalid_occupation_rejected(bad: int) -> None:
    with pytest.raises(ValueError):
        fock_amplitude(np.eye(1), [bad], [1])


@pytest.mark.parametrize("delta", [0.0, -0.1, 1.0, 2.0, np.nan])
def test_invalid_failure_probability(delta: float) -> None:
    with pytest.raises(ValueError):
        hoeffding_radius(1, 10, delta)


def test_loss_and_shape_rejected() -> None:
    with pytest.raises(ValueError, match="unitary"):
        fock_amplitude(0.9 * np.eye(2), [1, 0], [1, 0])
    with pytest.raises(ValueError, match="square"):
        permanent_ryser([[1, 2]])
    with pytest.raises(ValueError, match="entries"):
        fock_amplitude(np.eye(2), [1], [1, 0])


def test_root_contract_rejected() -> None:
    with pytest.raises(ValueError, match="sum"):
        repeated_kernel(np.eye(2), [1, 2])
    with pytest.raises(ValueError, match="axis"):
        repeated_kernel(np.eye(2), [1, 1], axis=True)
    kernel, _ = repeated_kernel(np.eye(2), [1, 1])
    with pytest.raises(ValueError, match="outside"):
        evaluate_roots(kernel, [[0, 2]])
    with pytest.raises(ValueError, match="integer"):
        evaluate_roots(kernel, [[0.0, 1.0]])


def test_marginal_contract_rejected() -> None:
    with pytest.raises(ValueError, match="collision-free"):
        collision_free_marginal(np.eye(2), [2, 0], [0])
    for modes in ([0, 0], [2], [True]):
        with pytest.raises(ValueError):
            collision_free_marginal(np.eye(2), [1, 0], modes)
    with pytest.raises(ValueError, match="shape"):
        low_rank_coefficients(np.zeros((2, 1)), np.zeros((2, 2)))


def test_gaussian_contract_rejected() -> None:
    with pytest.raises(ValueError, match="symmetric"):
        hafnian([[0, 1j], [-1j, 0]])
    with pytest.raises(ValueError, match="loops"):
        hafnian(np.eye(2), loops=[1])
    with pytest.raises(ValueError, match="contraction"):
        pure_gaussian_probability(np.eye(2), [0, 0])
    with pytest.raises(ValueError, match="sampling density"):
        FockHusimiKernel(np.eye(1, dtype=np.complex128), (1,), (1,))(np.array([0]))


def test_resource_budgets_fail_before_draws() -> None:
    draws, rng = fake_rng()
    with pytest.raises(ValueError, match="max_photons"):
        permanent_ryser(np.eye(3), max_photons=2)
    with pytest.raises(ValueError, match="max_photons"):
        fock_amplitude(np.eye(2), [3, 0], [3, 0], max_photons=2)
    with pytest.raises(ValueError, match="max_elements"):
        estimate_permanent(np.eye(2), rng=rng, samples=100, max_elements=10)
    with pytest.raises(ValueError, match="max_samples"):
        sample_budget(1e-100, 0.01)
    with pytest.raises(ValueError, match="max_samples"):
        median_of_means_plan(1e-100, 0.01)
    with pytest.raises(ValueError, match="max_elements"):
        estimate_fock_husimi(np.eye(2), [1, 1], [1, 1], rng=rng, epsilon=0.5, max_elements=10)
    with pytest.raises(ValueError, match="max_work"):
        collision_free_marginal(np.eye(4), [1] * 4, [0, 1, 2], max_work=10)
    require(draws.calls == 0)


def test_scale_overflow_and_underflow_are_not_silent() -> None:
    for scale in (1e200, 1e-200):
        with pytest.raises(ArithmeticError):
            repeated_kernel(np.eye(2) * scale, [1, 1])


@pytest.mark.parametrize("inputs,outputs", [((2, 1), (1, 2)), ((1, 2), (3, 0)), ((2, 2), (2, 2))])
def test_both_sides_repeated_against_oracle(inputs: tuple[int, ...], outputs: tuple[int, ...]) -> None:
    _, rng = fake_rng()
    u = optical_matrix(2)
    result = estimate_fock_amplitude(u, inputs, outputs, rng=rng, samples=360)
    close(result.value, creation_oracle(u, inputs)[outputs])


@pytest.mark.parametrize("inputs,outputs", [((1, 1), (2, 0)), ((2, 1), (1, 2))])
def test_husimi_second_moment_quadrature(inputs: tuple[int, ...], outputs: tuple[int, ...]) -> None:
    # Gauss-Laguerre radial integration and exhaustive phases integrate these
    # finite-degree moments. This is not an empirical iid coverage test.
    radii, weights = np.polynomial.laguerre.laggauss(5)
    order = 2 * sum(inputs) + 1
    points, probabilities = [], []
    for i, j in itertools.product(range(len(radii)), repeat=2):
        weight = (
            weights[i]
            * weights[j]
            * radii[i] ** inputs[0]
            * radii[j] ** inputs[1]
            / math.prod(math.factorial(v) for v in inputs)
            / order**2
        )
        for phases in itertools.product(range(order), repeat=2):
            points.append(np.sqrt([radii[i], radii[j]]) * np.exp(2j * math.pi * np.asarray(phases) / order))
            probabilities.append(weight)
    values = parallel.ordered_map(FockHusimiKernel(optical_matrix(2), inputs, outputs), points)
    close(math.fsum(weight * abs(value) ** 2 for weight, value in zip(probabilities, values, strict=True)), 1)


def test_marginal_empty_set_still_validates_budget() -> None:
    with pytest.raises(ValueError, match="max_work"):
        collision_free_marginal(np.eye(1), [1], [], max_work=0)


def test_low_rank_overflow_is_rejected() -> None:
    with pytest.raises(ArithmeticError):
        low_rank_coefficients([[1e200]], [[1e200]])


def test_empty_block_mean_rejected() -> None:
    from photonic_gaussian import block_mean

    with pytest.raises(ValueError, match="nonempty"):
        block_mean([])


@pytest.mark.parametrize(
    "field,value",
    [
        ("value", complex(float("nan"), 0)),
        ("radius", -1.0),
        ("radius", float("inf")),
        ("delta", 0.0),
        ("samples", True),
        ("scale", -1.0),
        ("method", ""),
    ],
)
def test_estimate_record_rejects_invalid_fields(field: str, value: object) -> None:

    fields: dict[str, Any] = dict(value=0j, radius=0.1, delta=0.01, samples=10, method="test", scale=1.0)
    fields[field] = value
    with pytest.raises((ValueError, ArithmeticError)):
        AdditiveEstimate(**fields)


def test_complex_hoeffding_constant_against_union_bound() -> None:
    bound, count, delta = 1.7, 123, 0.03
    expected = 2 * bound * math.sqrt(math.log(4 / delta) / count)
    close(hoeffding_radius(bound, count, delta), expected, atol=1e-14)
    radius = hoeffding_radius(bound, count, delta)
    close(4 * math.exp(-count * radius**2 / (4 * bound**2)), delta, atol=1e-14)


def test_subnormal_one_by_one_kernel_normalises_without_reciprocal_overflow() -> None:
    kernel, scale = repeated_kernel([[1e-310]], [1])
    require(bool(np.isfinite(kernel.normalised).all()))
    close(kernel.normalised, [[1]])
    require(scale > 0)
    close(scale / 1e-310, 1)


def test_confidence_geometry_rejects_underflow() -> None:
    with pytest.raises(ArithmeticError, match="underflows"):
        AdditiveEstimate(1e-200 + 0j, 0.0, 0.01, 1, "test", 1e-200).probability_interval()
    with pytest.raises(ArithmeticError, match="outside"):
        hoeffding_radius(float(np.nextafter(0.0, 1.0)), 1000000, 0.01)


def test_odd_hafnian_uses_selection_rule() -> None:
    close(hafnian(np.ones((19, 19))), 0)
