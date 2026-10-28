"""Verify the control channel and its parity-versus-coordinate distinction."""

import math
from fractions import Fraction
from itertools import permutations, product

import numpy as np
import pytest
import readout_information_controls as controls_module
from readout_information_controls import (
    binary_entropy,
    information,
    noise_distribution,
    observed_information,
    scipy_information,
)
from scipy.stats import entropy


def test_illustrative_paired_bound_is_not_exported_by_control_module() -> None:
    for name in ("illustrative_paired_lower_bound", "illustrative_contrast_bound"):
        if hasattr(controls_module, name):
            raise AssertionError("the control module must not expose an illustrative decision bound")


def test_default_control_output_carries_no_hardware_verdict() -> None:
    result = controls_module.controls()
    if set(result) != {"schema", "flip_probability", "input", "output", "models", "boundary"}:
        raise AssertionError("the classical control output must not add a hardware verdict or confidence field")
    if "no provider or physical measurement" not in str(result["boundary"]):
        raise AssertionError("the default output must identify its classical-only boundary")


def _paired_illustration(counts: tuple[int, int, int, int], alpha: float) -> float:
    count = sum(counts)
    return (counts[3] - max(counts[1], counts[2])) / count - math.sqrt(2 * math.log(1 / alpha) / count)


def test_shared_and_independent_flips_have_equal_marginals_but_distinct_parity() -> None:
    independent = noise_distribution(Fraction(1, 4), shared=False)
    shared = noise_distribution(Fraction(1, 4), shared=True)
    for noise in (independent, shared):
        if noise[1] + noise[3] != Fraction(1, 4) or noise[2] + noise[3] != Fraction(1, 4):
            raise AssertionError("the two noise models must have the same one-bit flip marginals")
        if not math.isclose(information(noise, 1), 1 - binary_entropy(Fraction(1, 4)), rel_tol=0.0, abs_tol=1e-14):
            raise AssertionError("coordinate information differs from the binary-symmetric value")
    if independent[1] + independent[2] != Fraction(3, 8) or shared[1] + shared[2] != 0:
        raise AssertionError("the models must differ in the probability of changing parity")
    if not information(independent, 3) < information(independent, 1) < information(shared, 3):
        raise AssertionError("the common-flip mutation must reverse the information ordering")


@pytest.mark.parametrize("shared", [False, True])
def test_no_flip_preserves_all_summaries(shared: bool) -> None:
    noise = noise_distribution(Fraction(0), shared)
    for mask in (1, 2, 3):
        if information(noise, mask) != 1.0:
            raise AssertionError("a noiseless full output must preserve every nonzero binary summary")


def test_channel_validation_rejects_boolean_and_bad_probabilities() -> None:
    for invalid in (True, -1, 4):
        with pytest.raises(ValueError):
            information((Fraction(1), Fraction(0), Fraction(0), Fraction(0)), invalid)
    with pytest.raises(ValueError):
        noise_distribution(Fraction(5, 4), False)
    with pytest.raises(ValueError):
        information((Fraction(1), Fraction(1), Fraction(0), Fraction(0)), 1)
    with pytest.raises(ValueError):
        binary_entropy(Fraction(1, 10**400))
    with pytest.raises(ValueError):
        information((Fraction(1) - Fraction(1, 10**400), Fraction(1, 10**400), Fraction(0), Fraction(0)), 1)


def test_every_output_bijection_preserves_information() -> None:
    for shared in (False, True):
        noise = noise_distribution(Fraction(1, 4), shared)
        for summary_mask in (1, 2, 3):
            expected = information(noise, summary_mask)
            for relabel in permutations(range(4)):
                if not math.isclose(
                    scipy_information(noise, summary_mask, relabel), expected, rel_tol=0, abs_tol=1e-14
                ):
                    raise AssertionError("a bijective output relabeling changed mutual information")


def test_fixed_input_order_can_turn_position_drift_into_false_parity() -> None:
    position_outputs = (0, 1, 1, 0)
    values = []
    for summary_mask in (1, 2, 3):
        joint = np.zeros((2, 4), dtype=float)
        for input_bits, output in enumerate(position_outputs):
            summary = (input_bits & summary_mask).bit_count() % 2
            joint[summary, output] += 0.25
        value = entropy(joint.sum(axis=1), base=2) + entropy(joint.sum(axis=0), base=2) - entropy(joint.ravel(), base=2)
        values.append(float(value))
    if values != [0.0, 0.0, 1.0]:
        raise AssertionError("position-only output did not create the expected false parity reversal")


@pytest.mark.parametrize("shared", [False, True])
def test_empirical_channel_reconstructs_exact_control(shared: bool) -> None:
    noise = noise_distribution(Fraction(1, 4), shared)
    counts = [[int(16 * noise[input_bits ^ output]) for output in range(4)] for input_bits in range(4)]
    result = observed_information(counts)
    values = result["information_bits"]
    if not isinstance(values, dict):
        raise AssertionError("descriptive information values are missing")
    for name, mask in (("coordinate_0_bits", 1), ("coordinate_1_bits", 2), ("parity_bits", 3)):
        if not math.isclose(values[name], information(noise, mask), rel_tol=0.0, abs_tol=1e-14):
            raise AssertionError("empirical channel failed to reconstruct the finite control")


def test_empirical_channel_refuses_incomplete_and_aliased_counts() -> None:
    for counts in (
        [[1, 0, 0, 0]] * 3,
        [[1, 0, 0, 0]] * 3 + [[0, 0, 0, 0]],
        [[1, 0, 0, 0]] * 3 + [[True, 0, 0, 0]],
        [[1, 0, 0, 0]] * 3 + [[-1, 1, 0, 0]],
    ):
        with pytest.raises(ValueError):
            observed_information(counts)


def test_fixed_size_99_percent_bound_can_preclude_reversal_at_20000_shots() -> None:
    variation = 2 * math.sqrt(math.log(6400) / (2 * 20000))
    entropy_value = binary_entropy(Fraction.from_float(variation))
    bound = 2 * (variation * (math.log2(3) + math.log2(7)) + 2 * entropy_value)
    if not 1.0296 < bound < 1.0298:
        raise AssertionError("illustrative two-context confidence radius differs")


def test_error_table_decodes_excited_preparation_before_parity() -> None:
    result = controls_module.parity_error_summary((1, 1), [(1, 1)] * 8 + [(0, 0)] * 2)
    if result["counts"] != (8, 0, 0, 2) or result["improvement"] != Fraction(1, 5):
        raise AssertionError("the error table must compare each output against its commanded input")


def test_error_table_exposes_asymmetric_feasibility_limit() -> None:
    result = controls_module.parity_error_summary((0, 0), [(0, 0)] * 7 + [(1, 0)] * 2 + [(1, 1)])
    if result["improvement"] != Fraction(-1, 10) or result["maximum_improvement"] != Fraction(-1, 10):
        raise AssertionError("unequal marginals must bound even the strongest shared-flip improvement")


def test_shared_and_isolated_error_decomposition() -> None:
    for counts in product(range(4), repeat=4):
        total = sum(counts)
        if total == 0:
            continue
        shared = Fraction(counts[3], total)
        isolated = Fraction(counts[1] + counts[2], total)
        imbalance = Fraction(counts[1] - counts[2], total)
        first = Fraction(counts[2] + counts[3], total)
        second = Fraction(counts[1] + counts[3], total)
        if min(first, second) - isolated != shared - isolated / 2 - abs(imbalance) / 2:
            raise AssertionError("paired improvement must decompose into shared, isolated and asymmetric errors")


def test_shared_errors_can_increase_improvement_without_reducing_parity_error() -> None:
    idle = controls_module.parity_error_summary((0, 0), [(0, 0)] * 8 + [(0, 1), (1, 0)])
    active = controls_module.parity_error_summary((0, 0), [(0, 0)] * 6 + [(0, 1), (1, 0)] + [(1, 1)] * 2)
    if not active["improvement"] > idle["improvement"] or active["parity_error"] != idle["parity_error"]:
        raise AssertionError("shared errors can improve G without reducing parity error")
    if not all(
        active_error > idle_error
        for active_error, idle_error in zip(active["marginal_errors"], idle["marginal_errors"], strict=True)
    ):
        raise AssertionError("both marginal errors must increase in the shared-error control")


def test_counterbalanced_drift_contrasts_require_a_schedule_model() -> None:
    values = [Fraction(count, 32768) for count in (3277, 8192, 13107, 18022)]
    first_distance = abs(values[0] - values[1])
    second_distance = abs(values[3] - values[2])
    if first_distance != second_distance or first_distance != Fraction(4915, 32768):
        raise AssertionError("the deterministic drift control must reproduce both pairwise distances")
    if values[0] - values[1] - values[2] + values[3] != 0:
        raise AssertionError("the signed four-target contrast must cancel equally spaced linear drift")
    positions = (-3, -1, 1, 3)
    assignment = (1, 0, 0, 1)
    if any(position**2 != 1 + 8 * actor for position, actor in zip(positions, assignment, strict=True)):
        raise AssertionError("quadratic drift must coincide with predecessor assignment in the four-target schedule")
    weights = (1, -1, -1, 1, -1, 1, 1, -1)
    if any(sum(weight * position**degree for position, weight in enumerate(weights)) for degree in range(3)):
        raise AssertionError("the prospective eight-target contrast must cancel polynomial trends through degree two")


def test_error_table_rejects_missing_or_nonbinary_data() -> None:
    for preparation, outputs in (((0, 0), []), ((True, 0), [(0, 0)]), ((0, 0), [(0, 2)])):
        with pytest.raises(ValueError):
            controls_module.parity_error_summary(preparation, outputs)


def test_error_table_matches_paired_identity_for_all_short_binary_streams() -> None:
    for outputs in product(((0, 0), (0, 1), (1, 0), (1, 1)), repeat=3):
        result = controls_module.parity_error_summary((0, 0), list(outputs))
        counts = [outputs.count(cell) for cell in ((0, 0), (0, 1), (1, 0), (1, 1))]
        expected = Fraction(counts[3] - max(counts[1], counts[2]), 3)
        if result["improvement"] != expected:
            raise AssertionError("paired error improvement differs from the exact four-cell identity")


def test_paired_component_moments_keep_unequal_variances() -> None:
    result = controls_module.paired_component_moments((7, 1, 0, 2))
    if result["means"] != (Fraction(1, 10), Fraction(1, 5)):
        raise AssertionError("component means must use the paired 00, 01, 10 and 11 cells")
    if result["sample_variances"] != (Fraction(29, 90), Fraction(8, 45)):
        raise AssertionError("each component must retain its own unbiased sample variance")
    if result["sample_covariance"] != Fraction(1, 5):
        raise AssertionError("joint score covariance must use the same paired shots")


def test_paired_component_moments_reject_too_few_or_aliased_counts() -> None:
    for counts in ((1, 0, 0, 0), (1, True, 0, 0), (1, -1, 0, 2)):
        with pytest.raises(ValueError):
            controls_module.paired_component_moments(counts)


def test_paired_component_moments_match_direct_scores_for_small_tables() -> None:
    for shots in range(2, 9):
        for first in range(shots + 1):
            for second in range(shots - first + 1):
                for third in range(shots - first - second + 1):
                    counts = (first, second, third, shots - first - second - third)
                    result = controls_module.paired_component_moments(counts)
                    direct_means = []
                    direct_variances = []
                    expanded_scores = []
                    for scores in ((0, -1, 0, 1), (0, 0, -1, 1)):
                        values = [score for score, count in zip(scores, counts, strict=True) for _ in range(count)]
                        expanded_scores.append(values)
                        mean = Fraction(sum(values), shots)
                        variance = sum((Fraction(value) - mean) ** 2 for value in values) / (shots - 1)
                        direct_means.append(mean)
                        direct_variances.append(variance)
                    if result["means"] != tuple(direct_means) or result["sample_variances"] != tuple(direct_variances):
                        raise AssertionError("paired moments must agree with the expanded shot-score reference")
                    covariance = sum(
                        (Fraction(first_score) - direct_means[0]) * (Fraction(second_score) - direct_means[1])
                        for first_score, second_score in zip(*expanded_scores, strict=True)
                    ) / (shots - 1)
                    if result["sample_covariance"] != covariance:
                        raise AssertionError("paired covariance must agree with same-shot expanded scores")
                    common_error = covariance * Fraction(shots - 1, shots) + direct_means[0] * direct_means[1]
                    recovered = (
                        1 - 3 * common_error + direct_means[0] + direct_means[1],
                        common_error - direct_means[0],
                        common_error - direct_means[1],
                        common_error,
                    )
                    if recovered != tuple(Fraction(count, shots) for count in counts):
                        raise AssertionError("paired means and covariance must recover the empirical four-cell law")


def test_reporter_projection_preserves_shot_order_and_little_endian_indices() -> None:
    result = controls_module.project_reporter_shots(["10001", "00100", "00000"], 5, (0, 2))
    if result != [(1, 0), (0, 1), (0, 0)]:
        raise AssertionError("reporter projection must preserve order and map bit zero to the rightmost character")
    reversed_reporters = controls_module.project_reporter_shots(["10001", "00100"], 5, (2, 0))
    if reversed_reporters != [(0, 1), (1, 0)]:
        raise AssertionError("the output tuple must follow the requested reporter order")


def test_large_register_projection_decodes_commanded_excitation() -> None:
    shots = ["0" * 154 + "11", "0" * 156]
    projected = controls_module.project_reporter_shots(shots, 156, (0, 1))
    result = controls_module.parity_error_summary((1, 1), projected)
    if result["counts"] != (1, 0, 0, 1):
        raise AssertionError("a 156-bit single-register output must decode paired errors against its preparation")


def test_reporter_projection_rejects_ambiguous_or_incomplete_registers() -> None:
    for shots, width, reporter_bits in (
        (["010", "01"], 3, (0, 1)),
        (["0 1"], 3, (0, 1)),
        (["0é1"], 3, (0, 1)),
        (["x01"], 3, (0, 1)),
        (["001"], 3, (0, 0)),
        ([], 3, (0, 1)),
    ):
        with pytest.raises(ValueError):
            controls_module.project_reporter_shots(shots, width, reporter_bits)


def test_reporter_projection_rejects_excessive_output_size() -> None:
    with pytest.raises(ValueError):
        controls_module.project_reporter_shots(["00"] * 1_000_001, 2, (0, 1))


def test_paired_illustration_uses_full_pair_level_for_intersection_union() -> None:
    result = _paired_illustration((96000, 500, 500, 3000), 0.05)
    expected = 0.025 - math.sqrt(2 * math.log(20) / 100000)
    if not math.isclose(result, expected, rel_tol=0.0, abs_tol=1e-14):
        raise AssertionError("paired one-sided radius must apply to each component at the per-pair level")


def test_paired_illustration_has_bounded_size_on_exact_boundary_null() -> None:
    sample_size = 12
    probabilities = (Fraction(3, 10), Fraction(3, 10), Fraction(1, 10), Fraction(3, 10))
    rejection_probability = Fraction(0)
    for first in range(sample_size + 1):
        for second in range(sample_size - first + 1):
            for third in range(sample_size - first - second + 1):
                counts = (first, second, third, sample_size - first - second - third)
                if _paired_illustration(counts, 0.1) > 0:
                    coefficient = math.factorial(sample_size)
                    for count in counts:
                        coefficient //= math.factorial(count)
                    probability = Fraction(coefficient)
                    for weight, count in zip(probabilities, counts, strict=True):
                        probability *= weight**count
                    rejection_probability += probability
    if not 0 < rejection_probability <= Fraction(1, 10):
        raise AssertionError("the exact multinomial boundary-null rejection rate exceeds the declared level")
