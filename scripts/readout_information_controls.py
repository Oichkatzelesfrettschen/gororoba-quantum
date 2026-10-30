"""Exact two-bit noise controls for a prospective readout-information experiment.

The calculation concerns classical channels and does not authenticate or submit
provider jobs. The commanded-input experiment includes preparation and readout.
"""

from __future__ import annotations

import argparse
import json
import math
from fractions import Fraction
from typing import TypedDict

import numpy as np
from scipy.stats import entropy

MIN_NONZERO_PROBABILITY = Fraction(1, 10**12)


class ParityErrorSummary(TypedDict):
    """Exact descriptive values retain their scalar and paired types for callers."""

    counts: tuple[int, ...]
    marginal_errors: tuple[Fraction, Fraction]
    parity_error: Fraction
    improvement: Fraction
    maximum_improvement: Fraction
    boundary: str


def noise_distribution(flip_probability: Fraction, shared: bool) -> tuple[Fraction, ...]:
    """Return probabilities of flip masks 00, 01, 10 and 11."""
    if type(flip_probability) is not Fraction or not 0 <= flip_probability <= 1 or type(shared) is not bool:
        raise ValueError("noise model requires a rational probability and a Boolean shared flag")
    complement = 1 - flip_probability
    if shared:
        return complement, Fraction(0), Fraction(0), flip_probability
    return complement**2, flip_probability * complement, flip_probability * complement, flip_probability**2


def _validate_channel(noise: tuple[Fraction, ...], summary_mask: int) -> None:
    if (
        type(noise) is not tuple
        or len(noise) != 4
        or any(type(weight) is not Fraction or weight < 0 or 0 < weight < MIN_NONZERO_PROBABILITY for weight in noise)
        or sum(noise) != 1
        or type(summary_mask) is not int
        or summary_mask not in (1, 2, 3)
    ):
        raise ValueError("expected a normalized four-mask channel and a nonzero two-bit summary")


def information(noise: tuple[Fraction, ...], summary_mask: int) -> float:
    """Compute information for channel weights zero or at least 1e-12."""
    _validate_channel(noise, summary_mask)
    joint = [[Fraction(0) for _ in range(4)] for _ in range(2)]
    for input_bits in range(4):
        summary = (input_bits & summary_mask).bit_count() % 2
        for flip_mask, probability in enumerate(noise):
            joint[summary][input_bits ^ flip_mask] += probability / 4
    summary_marginal = [sum(row) for row in joint]
    output_marginal = [joint[0][output] + joint[1][output] for output in range(4)]
    terms = []
    for summary in range(2):
        for output in range(4):
            probability = joint[summary][output]
            if probability:
                ratio = probability / (summary_marginal[summary] * output_marginal[output])
                terms.append(float(probability) * math.log2(float(ratio)))
    return math.fsum(terms)


def binary_entropy(probability: Fraction) -> float:
    """Calculate binary entropy for endpoints or probabilities within [1e-12, 1-1e-12]."""
    if type(probability) is not Fraction or not 0 <= probability <= 1:
        raise ValueError("entropy requires a rational probability between zero and one")
    if probability in (0, 1):
        return 0.0
    if min(probability, 1 - probability) < MIN_NONZERO_PROBABILITY:
        raise ValueError("entropy probability is outside the supported numerical range")
    value = float(probability)
    return -value * math.log2(value) - (1 - value) * math.log2(1 - value)


def scipy_information(
    noise: tuple[Fraction, ...], summary_mask: int, output_relabel: tuple[int, ...] = (0, 1, 2, 3)
) -> float:
    """Cross-check the finite channel with NumPy and SciPy entropy."""
    _validate_channel(noise, summary_mask)
    if (
        type(output_relabel) is not tuple
        or len(output_relabel) != 4
        or any(type(value) is not int for value in output_relabel)
        or set(output_relabel) != {0, 1, 2, 3}
    ):
        raise ValueError("output relabeling must be a bijection on four outcomes")
    inputs = np.arange(4, dtype=np.int64)
    flips = np.arange(4, dtype=np.int64)
    outputs = np.asarray(output_relabel)[np.bitwise_xor(inputs[:, None], flips[None, :])]
    selected = np.bitwise_and(inputs, summary_mask)
    summaries = np.bitwise_xor(selected & 1, (selected >> 1) & 1)
    probabilities = np.broadcast_to(np.array([float(weight) / 4 for weight in noise]), outputs.shape)
    joint = np.zeros((2, 4), dtype=np.float64)
    np.add.at(joint, (np.broadcast_to(summaries[:, None], outputs.shape), outputs), probabilities)
    return float(
        entropy(joint.sum(axis=1), base=2) + entropy(joint.sum(axis=0), base=2) - entropy(joint.ravel(), base=2)
    )


def observed_information(counts: list[list[int]]) -> dict[str, object]:
    """Describe a four-input empirical channel under an explicit uniform mixture.

    Counts require separate authenticated source, ordering and uncertainty
    checks; the function makes no scientific or hardware admission decision.
    """
    if (
        type(counts) is not list
        or len(counts) != 4
        or any(
            type(row) is not list
            or len(row) != 4
            or any(type(value) is not int or not 0 <= value <= 10**9 for value in row)
            or sum(row) == 0
            for row in counts
        )
    ):
        raise ValueError("counts must contain four nonempty rows of four bounded nonnegative integers")
    array = np.asarray(counts, dtype=np.float64)
    joint_input_output = array / array.sum(axis=1, keepdims=True) / 4
    results: dict[str, float] = {}
    input_values = np.arange(4, dtype=np.int64)
    for name, summary_mask in (("coordinate_0_bits", 1), ("coordinate_1_bits", 2), ("parity_bits", 3)):
        selected = input_values & summary_mask
        summaries = (selected & 1) ^ ((selected >> 1) & 1)
        joint = np.zeros((2, 4), dtype=np.float64)
        np.add.at(joint, summaries, joint_input_output)
        results[name] = float(
            entropy(joint.sum(axis=1), base=2) + entropy(joint.sum(axis=0), base=2) - entropy(joint.ravel(), base=2)
        )
    return {
        "row_shots": [sum(row) for row in counts],
        "input_weighting": "uniform mixture of the four empirically normalized input rows",
        "information_bits": results,
        "boundary": "Descriptive plug-in estimates; no ordering, uncertainty, source authentication or device claim.",
    }


def parity_error_summary(preparation: tuple[int, int], outputs: list[tuple[int, int]]) -> ParityErrorSummary:
    """Describe paired errors exactly; the result is not a confidence bound.

    The caller must authenticate preparation, mapping, ordering and the source
    of every shot before interpreting the descriptive result.
    """
    if (
        type(preparation) is not tuple
        or len(preparation) != 2
        or any(type(bit) is not int or bit not in (0, 1) for bit in preparation)
        or type(outputs) is not list
        or not outputs
        or any(
            type(output) is not tuple
            or len(output) != 2
            or any(type(bit) is not int or bit not in (0, 1) for bit in output)
            for output in outputs
        )
    ):
        raise ValueError("preparation and each output must contain two integer bits, with at least one shot")
    errors = np.bitwise_xor(np.asarray(outputs, dtype=np.uint8), np.asarray(preparation, dtype=np.uint8))
    cells = np.bincount(2 * errors[:, 0] + errors[:, 1], minlength=4)
    counts = tuple(int(count) for count in cells)
    total = len(outputs)
    first_error = Fraction(counts[2] + counts[3], total)
    second_error = Fraction(counts[1] + counts[3], total)
    parity_error = Fraction(counts[1] + counts[2], total)
    return {
        "counts": counts,
        "marginal_errors": (first_error, second_error),
        "parity_error": parity_error,
        "improvement": min(first_error, second_error) - parity_error,
        "maximum_improvement": 2 * min(first_error, second_error) - max(first_error, second_error),
        "boundary": "Descriptive empirical values; neither feasibility nor statistical significance is established.",
    }


def project_reporter_shots(shots: list[str], width: int, reporter_bits: tuple[int, int]) -> list[tuple[int, int]]:
    """Project ordered, single-register Qiskit bitstrings onto two classical bits.

    The caller must authenticate the register identity and physical mapping.
    This projection does not infer physical predecessor order or independence.
    """
    if (
        type(shots) is not list
        or not shots
        or len(shots) > 1_000_000
        or type(width) is not int
        or not 2 <= width <= 4096
        or len(shots) * width > 100_000_000
        or type(reporter_bits) is not tuple
        or len(reporter_bits) != 2
        or any(type(bit) is not int or not 0 <= bit < width for bit in reporter_bits)
        or reporter_bits[0] == reporter_bits[1]
        or any(type(shot) is not str or len(shot) != width for shot in shots)
    ):
        raise ValueError("a nonempty ordered single-register bitstring list and two distinct bit indices are required")
    try:
        encoded = "".join(shots).encode("ascii")
    except UnicodeEncodeError as error:
        raise ValueError("shot strings must contain only binary characters") from error
    bits = np.frombuffer(encoded, dtype=np.uint8).reshape(len(shots), width)
    if not np.all((bits == ord("0")) | (bits == ord("1"))):
        raise ValueError("shot strings must contain only binary characters")
    projected = bits[:, [width - 1 - bit for bit in reporter_bits]] - ord("0")
    return list(zip(projected[:, 0].tolist(), projected[:, 1].tolist(), strict=True))


def paired_component_moments(counts: tuple[int, int, int, int]) -> dict[str, object]:
    """Return exact descriptive moments for two paired error scores.

    The input cells are error bits 00, 01, 10 and 11. The moments do not
    authenticate a source or establish independence, coverage or admission.
    """
    if (
        type(counts) is not tuple
        or len(counts) != 4
        or any(type(count) is not int or not 0 <= count <= 10**9 for count in counts)
        or sum(counts) < 2
    ):
        raise ValueError("four bounded nonnegative integer cells with at least two shots are required")
    shots = sum(counts)
    means = (Fraction(counts[3] - counts[1], shots), Fraction(counts[3] - counts[2], shots))
    second_moments = (Fraction(counts[3] + counts[1], shots), Fraction(counts[3] + counts[2], shots))
    variances = tuple(
        Fraction(shots, shots - 1) * (second - mean * mean) for mean, second in zip(means, second_moments, strict=True)
    )
    covariance = Fraction(shots, shots - 1) * (Fraction(counts[3], shots) - means[0] * means[1])
    return {
        "means": means,
        "sample_variances": variances,
        "sample_covariance": covariance,
        "boundary": "Descriptive paired moments; no confidence interval or hardware decision.",
    }


def controls() -> dict[str, object]:
    """Compute and independently check the quarter-flip counterexample."""
    flip_probability = Fraction(1, 4)
    independent = noise_distribution(flip_probability, shared=False)
    common = noise_distribution(flip_probability, shared=True)
    coordinate = 1 - binary_entropy(flip_probability)
    independent_parity = 1 - binary_entropy(2 * flip_probability * (1 - flip_probability))
    results = {}
    for name, noise in (("independent", independent), ("common_flip", common)):
        first = information(noise, 1)
        second = information(noise, 2)
        parity = information(noise, 3)
        expected_parity = independent_parity if name == "independent" else 1.0
        if not all(
            math.isclose(value, coordinate, rel_tol=0.0, abs_tol=1e-14) for value in (first, second)
        ) or not math.isclose(parity, expected_parity, rel_tol=0.0, abs_tol=1e-14):
            raise ValueError("enumerated information differs from the binary-entropy identity")
        for mask, expected in ((1, first), (2, second), (3, parity)):
            if not math.isclose(scipy_information(noise, mask), expected, rel_tol=0.0, abs_tol=1e-14):
                raise ValueError("SciPy entropy differs from the exact-channel calculation")
        results[name] = {"coordinate_0_bits": first, "coordinate_1_bits": second, "parity_bits": parity}
    if not (results["independent"]["parity_bits"] < coordinate < results["common_flip"]["parity_bits"]):
        raise ValueError("control does not reverse the parity-versus-coordinate information ordering")
    return {
        "schema": "readout-information-classical-controls-v1",
        "flip_probability": "1/4",
        "input": "uniform independent two-bit commanded input",
        "output": "complete two-bit output",
        "models": results,
        "boundary": "Exact classical channel construction; no provider or physical measurement.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="check exact channel identities and ordering")
    arguments = parser.parse_args()
    result = controls()
    if arguments.check:
        print("Independent and common-flip controls satisfy the information identities.")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
