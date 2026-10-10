"""Exact classical host stages for bounded hybrid Shor experiments.

The module performs cheap factor checks, rational reconstruction, exact order
validation, factor extraction, ideal finite-precision phase laws, and resource
accounting. Circuit builders never receive the reference order or factors.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

MAX_EXACT_PRECHECK_MODULUS = 1 << 64


@dataclass(frozen=True)
class PrecheckResult:
    status: str
    modulus: int
    base: int
    factor: int | None
    reason: str


@dataclass(frozen=True)
class OrderCandidate:
    numerator: int
    denominator: int
    order: int | None


@dataclass(frozen=True)
class PhaseRecovery:
    measurement: int
    phase_bits: int
    candidates: tuple[OrderCandidate, ...]
    orders: tuple[int, ...]
    factors: tuple[int, ...]


@dataclass(frozen=True)
class MultiplierResource:
    round_index: int
    exponent: int
    multiplier: int
    strategy: str
    scratch_qubits: int
    forward_anf_terms: int
    inverse_anf_terms: int
    maximum_anf_degree: int
    degree_histogram: tuple[tuple[int, int], ...]
    controlled_swaps: int


@dataclass(frozen=True)
class OrderFindingPlan:
    modulus: int
    base: int
    work_qubits: int
    phase_bits: int
    quantum_qubits: int
    scratch_qubits: int
    active_rounds: int
    unique_multipliers: tuple[int, ...]
    forward_anf_terms: int
    inverse_anf_terms: int
    maximum_anf_degree: int
    degree_histogram: tuple[tuple[int, int], ...]
    controlled_swaps: int
    measurements: int
    resets: int
    conditional_phases: int
    rounds: tuple[MultiplierResource, ...]


def _require_exact_precheck_range(modulus: int) -> None:
    if modulus >= MAX_EXACT_PRECHECK_MODULUS:
        raise ValueError(
            f"exact primality preprocessing supports modulus < {MAX_EXACT_PRECHECK_MODULUS}, got {modulus}"
        )


def is_prime(modulus: int) -> bool:
    """Return exact primality for unsigned 64-bit integers."""
    if modulus < 2:
        return False
    _require_exact_precheck_range(modulus)
    small_primes = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    if modulus in small_primes:
        return True
    if any(modulus % prime == 0 for prime in small_primes):
        return False
    odd_part = modulus - 1
    power_of_two = 0
    while odd_part % 2 == 0:
        power_of_two += 1
        odd_part //= 2
    for witness in (2, 325, 9375, 28178, 450775, 9780504, 1795265022):
        normalized = witness % modulus
        if normalized == 0:
            continue
        value = pow(normalized, odd_part, modulus)
        if value in (1, modulus - 1):
            continue
        for _ in range(power_of_two - 1):
            value = value * value % modulus
            if value == modulus - 1:
                break
        else:
            return False
    return True


def _integer_nth_root(value: int, exponent: int) -> int:
    if value < 0 or exponent < 2:
        raise ValueError("integer root needs a nonnegative value and exponent >= 2")
    if value < 2:
        return value
    lower = 1
    upper = 1 << ((value.bit_length() + exponent - 1) // exponent)
    while lower <= upper:
        midpoint = (lower + upper) // 2
        powered = midpoint**exponent
        if powered == value:
            return midpoint
        if powered < value:
            lower = midpoint + 1
        else:
            upper = midpoint - 1
    return upper


def perfect_power(modulus: int) -> tuple[int, int] | None:
    """Return an exact nontrivial base and exponent when modulus is a power."""
    if modulus < 4:
        return None
    for exponent in range(2, modulus.bit_length() + 1):
        root = _integer_nth_root(modulus, exponent)
        if root > 1 and root**exponent == modulus:
            return root, exponent
    return None


def classical_precheck(modulus: int, base: int) -> PrecheckResult:
    """Fail closed before allocating a circuit or accepting a measured order."""
    if modulus < 2:
        return PrecheckResult("invalid", modulus, base, None, "modulus must be at least 2")
    _require_exact_precheck_range(modulus)
    if modulus == 2 or is_prime(modulus):
        return PrecheckResult("prime", modulus, base % modulus, None, "modulus is prime")
    if modulus % 2 == 0:
        return PrecheckResult("factor", modulus, base % modulus, 2, "modulus is even")
    power = perfect_power(modulus)
    if power is not None:
        factor, exponent = power
        return PrecheckResult("factor", modulus, base % modulus, factor, f"modulus is {factor}^{exponent}")
    normalized = base % modulus
    if normalized in (0, 1):
        return PrecheckResult("invalid", modulus, normalized, None, "base must lie between 2 and modulus - 1")
    common = math.gcd(normalized, modulus)
    if 1 < common < modulus:
        return PrecheckResult("factor", modulus, normalized, common, "gcd(base, modulus) is nontrivial")
    if common != 1:
        return PrecheckResult("invalid", modulus, normalized, None, "base is not an invertible residue")
    return PrecheckResult("proceed", modulus, normalized, None, "quantum order finding is required")


def continued_fraction_convergents(
    numerator: int, denominator: int, maximum_denominator: int
) -> tuple[tuple[int, int], ...]:
    """Return exact convergents of numerator/denominator within a bound."""
    if denominator <= 0:
        raise ValueError("denominator must be positive")
    if numerator < 0 or numerator >= denominator:
        raise ValueError("phase numerator must satisfy 0 <= numerator < denominator")
    if maximum_denominator < 1:
        raise ValueError("maximum denominator must be positive")
    terms: list[int] = []
    remainder_numerator, remainder_denominator = numerator, denominator
    while remainder_denominator:
        quotient, remainder = divmod(remainder_numerator, remainder_denominator)
        terms.append(quotient)
        remainder_numerator, remainder_denominator = remainder_denominator, remainder
    convergents: list[tuple[int, int]] = []
    numerator_older, numerator_previous = 0, 1
    denominator_older, denominator_previous = 1, 0
    for term in terms:
        convergent_numerator = term * numerator_previous + numerator_older
        convergent_denominator = term * denominator_previous + denominator_older
        if convergent_denominator > maximum_denominator:
            break
        convergents.append((convergent_numerator, convergent_denominator))
        numerator_older, numerator_previous = numerator_previous, convergent_numerator
        denominator_older, denominator_previous = denominator_previous, convergent_denominator
    return tuple(convergents)


def _prime_divisors(value: int) -> tuple[int, ...]:
    divisors: list[int] = []
    candidate = 2
    remainder = value
    while candidate * candidate <= remainder:
        if remainder % candidate == 0:
            divisors.append(candidate)
            while remainder % candidate == 0:
                remainder //= candidate
        candidate = 3 if candidate == 2 else candidate + 2
    if remainder > 1:
        divisors.append(remainder)
    return tuple(divisors)


def validate_order_multiple(base: int, modulus: int, candidate: int) -> int | None:
    """Validate a measured multiple and reduce it to the exact order."""
    if candidate < 1 or candidate >= modulus or math.gcd(base, modulus) != 1:
        return None
    if pow(base, candidate, modulus) != 1:
        return None
    order = candidate
    for prime in _prime_divisors(candidate):
        while order % prime == 0 and pow(base, order // prime, modulus) == 1:
            order //= prime
    return order


def extract_factors(base: int, modulus: int, order: int) -> tuple[int, ...]:
    """Return only divisibility-checked nontrivial factors from an exact order."""
    if validate_order_multiple(base, modulus, order) != order or order % 2:
        return ()
    half_power = pow(base, order // 2, modulus)
    if half_power in (1, modulus - 1):
        return ()
    factors = {
        factor
        for factor in (math.gcd(half_power - 1, modulus), math.gcd(half_power + 1, modulus))
        if 1 < factor < modulus and modulus % factor == 0
    }
    return tuple(sorted(factors))


def recover_from_measurement(measurement: int, phase_bits: int, modulus: int, base: int) -> PhaseRecovery:
    """Interpret one phase sample without assuming the order or expected factors."""
    if phase_bits < 1:
        raise ValueError("phase_bits must be positive")
    phase_denominator = 1 << phase_bits
    if measurement < 0 or measurement >= phase_denominator:
        raise ValueError(f"measurement must lie in [0, {phase_denominator}), got {measurement}")
    candidates: list[OrderCandidate] = []
    orders: set[int] = set()
    factors: set[int] = set()
    for numerator, denominator in continued_fraction_convergents(measurement, phase_denominator, modulus - 1):
        order = validate_order_multiple(base, modulus, denominator)
        candidates.append(OrderCandidate(numerator, denominator, order))
        if order is not None:
            orders.add(order)
            factors.update(extract_factors(base, modulus, order))
    return PhaseRecovery(
        measurement,
        phase_bits,
        tuple(candidates),
        tuple(sorted(orders)),
        tuple(sorted(factors)),
    )


def parse_count_key(key: str | int, phase_bits: int) -> int:
    """Convert an integer or Qiskit bitstring count key into a phase integer."""
    if isinstance(key, int):
        measurement = key
    else:
        compact = key.replace(" ", "").replace("_", "")
        if not compact or any(bit not in "01" for bit in compact):
            raise ValueError(f"count key must contain binary digits, got {key!r}")
        measurement = int(compact, 2)
    if measurement < 0 or measurement >= 1 << phase_bits:
        raise ValueError(f"count key {key!r} exceeds {phase_bits} phase bits")
    return measurement


def decode_counts(
    counts: Mapping[str | int, int], phase_bits: int, modulus: int, base: int
) -> tuple[tuple[PhaseRecovery, int], ...]:
    """Aggregate count keys and attach exact host recovery to each outcome."""
    aggregated: dict[int, int] = {}
    for key, count in counts.items():
        if count < 0:
            raise ValueError(f"count for {key!r} must be nonnegative")
        measurement = parse_count_key(key, phase_bits)
        aggregated[measurement] = aggregated.get(measurement, 0) + count
    return tuple(
        (recover_from_measurement(measurement, phase_bits, modulus, base), count)
        for measurement, count in sorted(aggregated.items())
    )


def reference_multiplicative_order(base: int, modulus: int) -> int:
    """Compute a bounded test oracle; circuit construction never calls this function."""
    if math.gcd(base, modulus) != 1:
        raise ValueError(f"base {base} is not invertible modulo {modulus}")
    value = 1
    for order in range(1, modulus):
        value = value * base % modulus
        if value == 1:
            return order
    raise RuntimeError(f"failed to find the multiplicative order of {base} modulo {modulus}")


def ideal_phase_distribution(order: int, phase_bits: int) -> tuple[float, ...]:
    """Return the exact-QPE finite-precision law averaged over all eigenphases."""
    if order < 1 or phase_bits < 1:
        raise ValueError("order and phase_bits must be positive")
    phase_denominator = 1 << phase_bits
    probabilities: list[float] = []
    for measurement in range(phase_denominator):
        probability = 0.0
        for phase_numerator in range(order):
            delta = phase_numerator / order - measurement / phase_denominator
            if math.isclose(delta, round(delta), rel_tol=0.0, abs_tol=1e-15):
                component = 1.0
            else:
                component = (
                    math.sin(math.pi * phase_denominator * delta) / (phase_denominator * math.sin(math.pi * delta))
                ) ** 2
            probability += component / order
        probabilities.append(probability)
    normalization = math.fsum(probabilities)
    return tuple(probability / normalization for probability in probabilities)


def distribution_success(distribution: Sequence[float], phase_bits: int, modulus: int, base: int) -> dict[str, float]:
    """Measure exact-order and verified-factor yield in a phase distribution."""
    if len(distribution) != 1 << phase_bits:
        raise ValueError(f"distribution has {len(distribution)} outcomes, expected {1 << phase_bits}")
    reference_order = reference_multiplicative_order(base, modulus)
    order_probability = 0.0
    factor_probability = 0.0
    for measurement, probability in enumerate(distribution):
        recovery = recover_from_measurement(measurement, phase_bits, modulus, base)
        if reference_order in recovery.orders:
            order_probability += float(probability)
        if recovery.factors:
            factor_probability += float(probability)
    return {"order_recovery_probability": order_probability, "factorable_probability": factor_probability}


def shots_for_success(per_shot_probability: float, failure_probability: float = 0.01) -> int:
    if not 0.0 < failure_probability < 1.0:
        raise ValueError("failure_probability must lie strictly between zero and one")
    if per_shot_probability <= 0.0:
        raise ValueError("per_shot_probability must be positive")
    if per_shot_probability >= 1.0:
        return 1
    return math.ceil(math.log(failure_probability) / math.log1p(-per_shot_probability))


def make_order_finding_plan(
    modulus: int, base: int, phase_bits: int, rounds: Sequence[MultiplierResource]
) -> OrderFindingPlan:
    """Aggregate independently extracted multiplier coefficients into one plan."""
    work_qubits = modulus.bit_length()
    if phase_bits < 1 or len(rounds) != phase_bits:
        raise ValueError(f"expected one multiplier resource for each of {phase_bits} phase bits")
    if tuple(resource.round_index for resource in rounds) != tuple(range(phase_bits)):
        raise ValueError("multiplier resources must appear in round order")
    scratch_qubits = max((resource.scratch_qubits for resource in rounds), default=0)
    histogram: dict[int, int] = {}
    for resource in rounds:
        for degree, count in resource.degree_histogram:
            histogram[degree] = histogram.get(degree, 0) + count
    active = tuple(resource for resource in rounds if resource.strategy != "identity")
    return OrderFindingPlan(
        modulus=modulus,
        base=base % modulus,
        work_qubits=work_qubits,
        phase_bits=phase_bits,
        quantum_qubits=1 + work_qubits + scratch_qubits,
        scratch_qubits=scratch_qubits,
        active_rounds=len(active),
        unique_multipliers=tuple(sorted({resource.multiplier for resource in active})),
        forward_anf_terms=sum(resource.forward_anf_terms for resource in rounds),
        inverse_anf_terms=sum(resource.inverse_anf_terms for resource in rounds),
        maximum_anf_degree=max((resource.maximum_anf_degree for resource in rounds), default=0),
        degree_histogram=tuple(sorted(histogram.items())),
        controlled_swaps=sum(resource.controlled_swaps for resource in rounds),
        measurements=phase_bits,
        resets=phase_bits - 1,
        conditional_phases=phase_bits * (phase_bits - 1) // 2,
        rounds=tuple(rounds),
    )


def _verify() -> None:
    expected_prechecks = {
        (2, 1): ("prime", None),
        (14, 3): ("factor", 2),
        (9, 2): ("factor", 3),
        (15, 3): ("factor", 3),
        (15, 2): ("proceed", None),
        (13, 2): ("prime", None),
    }
    for (modulus, base), expected in expected_prechecks.items():
        observed = classical_precheck(modulus, base)
        if (observed.status, observed.factor) != expected:
            raise RuntimeError(f"precheck ({modulus}, {base}) returned {observed}, expected {expected}")
    recovered = recover_from_measurement(64, 8, 15, 2)
    if recovered.orders != (4,) or recovered.factors != (3, 5):
        raise RuntimeError(f"phase 64/256 returned {recovered}")
    if recover_from_measurement(128, 8, 15, 2).orders:
        raise RuntimeError("reduced phase 128/256 incorrectly validates denominator two as the order")
    ideal = ideal_phase_distribution(4, 8)
    support = {index for index, probability in enumerate(ideal) if probability > 1e-12}
    if support != {0, 64, 128, 192}:
        raise RuntimeError(f"N=15 ideal support is {sorted(support)}")
    success = distribution_success(ideal, 8, 15, 2)
    if any(not math.isclose(value, 0.5, abs_tol=1e-12) for value in success.values()):
        raise RuntimeError(f"N=15 ideal success is {success}, expected 0.5")
    if shots_for_success(0.5) != 7:
        raise RuntimeError("seven independent 50-percent shots must bound failure below one percent")
    print("factoring host: exact prechecks, continued fractions, order validation, factors, and ideal laws pass")


if __name__ == "__main__":
    _verify()
