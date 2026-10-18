"""Paired bounded-score ET inference; physical context and controls gate scientific admission.

Hoeffding bounds apply to conditionally independent shots within each block,
including its PUBs. A union bound permits arbitrary dependence between blocks.
Calibration fits use designated samples; held-out observations remain separate.
"""

import math
from typing import Any

import numpy as np
from scipy.stats import beta

from et_campaign import ROWS, endpoint_terms, row_name, validate_configuration
from et_reference import ETSpec


def bounded_pvalue(effect: float, variance_proxy: float) -> float:
    if not math.isfinite(effect) or not math.isfinite(variance_proxy) or variance_proxy <= 0:
        raise ValueError("bounded-score effect and variance proxy must be finite, with a positive proxy")
    return math.exp(-2 * max(0.0, effect) ** 2 / variance_proxy)


def holm(probabilities: list[float], alpha: float) -> list[bool]:
    if not 0 < alpha < 1 or any(not math.isfinite(value) or not 0 <= value <= 1 for value in probabilities):
        raise ValueError("invalid Holm probabilities or alpha")
    accepted = [False] * len(probabilities)
    for rank, index in enumerate(sorted(range(len(probabilities)), key=lambda index: probabilities[index])):
        if probabilities[index] > alpha / (len(probabilities) - rank):
            break
        accepted[index] = True
    return accepted


def histogram(observation: dict[str, Any], size: int) -> tuple[np.ndarray, int]:
    values, shots = observation["counts"], observation["shots"]
    if (
        not isinstance(values, list)
        or len(values) != size
        or any(type(value) is not int or value < 0 for value in values)
        or type(shots) is not int
        or shots <= 0
        or sum(values) != shots
    ):
        raise ValueError("ET histogram requires integer counts and its own exact denominator")
    return np.array(values, dtype=float) / shots, shots


def _blocked_proxy(ranges: list[float], shots: list[int], blocks: list[int]) -> float:
    proxies: dict[int, float] = {}
    for width, count, block in zip(ranges, shots, blocks, strict=True):
        proxies[block] = proxies.get(block, 0.0) + width * width / count
    return sum(math.sqrt(value) for value in proxies.values()) ** 2


def _union_pvalue(effect: float, ranges: list[float], shots: list[int], blocks: list[int]) -> float:
    """Condition on shared fitted responses, combine independent shots, then union-bound blocks."""
    denominator = _blocked_proxy(ranges, shots, blocks)
    if denominator == 0:
        return 1.0 if effect <= 0 else 0.0
    return min(1.0, len(set(blocks)) * bounded_pvalue(effect, denominator))


def analyze(
    config: dict[str, Any], observations: dict[str, dict[str, Any]], contexts: dict[str, Any] | None = None
) -> dict[str, Any]:
    validate_configuration(config)
    metadata = config["members"]
    if set(observations) != set(metadata):
        return {"admitted": False, "withheld": "incomplete physical-control or signal observations", "endpoints": []}
    histograms = {name: histogram(observations[name], 64) for name in metadata}
    endpoints: list[dict[str, Any]] = []
    # Calibration confidence is spent once across the six endpoints and every
    # measured response column. A shared fitted matrix therefore stays shared.
    calibration_tail = config["alpha"] / 2
    response: dict[tuple, tuple[np.ndarray, float, float]] = {}
    inverse_scores = {}
    for dimensions in ROWS:
        for block in range(config["blocks"]):
            for basis in ("Z", "X"):
                key = (dimensions, block, basis)
                columns = sorted(
                    (item["value"], name)
                    for name, item in metadata.items()
                    if tuple(item["spec"]) == dimensions
                    and item["block"] == block
                    and item["basis"] == basis
                    and item["kind"] == "readout"
                    and not item["held_out"]
                )
                matrix = np.column_stack([histograms[name][0] for _, name in columns])
                # A lower bound L on the true diagonal gives
                # ||R_column - Rhat_column||_1 <= 2(1-L): both columns
                # place at least L on that outcome. Union-bound all 1536
                # diagonal events, including every block and context.
                lower = []
                for value, name in columns:
                    probabilities, count = histograms[name]
                    successes = int(round(probabilities[value] * count))
                    lower.append(
                        float(beta.ppf(calibration_tail / 1536, successes, count - successes + 1)) if successes else 0.0
                    )
                epsilon = 2 * (1 - min(lower))
                condition = float(np.linalg.cond(matrix))
                response[key] = (matrix, epsilon, condition)
    for dimensions in ROWS:
        spec = ETSpec(*dimensions)
        for kind in ("signed", "coherence"):
            estimate = raw_estimate = calibration_allowance = 0.0
            ranges, counts, blocks = [], [], []
            charged = set()
            invalid = False
            for name, weights, coefficient in endpoint_terms(config, spec, kind):
                item = metadata[name]
                matrix, epsilon, condition = response[(dimensions, item["block"], item["basis"])]
                probabilities, count = histograms[name]
                raw_estimate += coefficient * float(probabilities @ weights)
                if not math.isfinite(condition) or condition > 1e8:
                    invalid = True
                    corrected = weights
                else:
                    cache_key = (dimensions, item["block"], item["basis"], kind)
                    if cache_key not in inverse_scores:
                        inverse_scores[cache_key] = np.linalg.solve(matrix.T, weights)
                    corrected = inverse_scores[cache_key]
                estimate += coefficient * float(probabilities @ corrected)
                width = float(np.ptp(corrected))
                # The two signal distributions have difference L1 <= 2.
                # Complete dephasing ensembles contain the same native
                # programs with balanced masks, so their expected marker
                # difference is zero under the fixed block channel. Charge
                # shared response uncertainty once per block, not per mask.
                if item["block"] not in charged:
                    calibration_allowance += width * epsilon / config["blocks"]
                    charged.add(item["block"])
                ranges.append(abs(coefficient) * width)
                counts.append(count)
                blocks.append(item["block"])
            # Conditional on the simultaneous response event, the fitted
            # inverse scores are fixed and the signals are independent of fit data.
            p_value = 1.0 if invalid else _union_pvalue(estimate - calibration_allowance, ranges, counts, blocks)
            tail = config["alpha"] / 12
            radius = (
                math.sqrt(_blocked_proxy(ranges, counts, blocks) * math.log(2 * len(set(blocks)) / tail) / 2)
                + calibration_allowance
            )
            endpoints.append(
                {
                    "name": f"et_{row_name(spec)}_{kind}",
                    "kind": kind,
                    "estimate": estimate,
                    "raw_estimate": raw_estimate,
                    "calibration_allowance": calibration_allowance,
                    "confidence_interval": [estimate - radius, estimate + radius],
                    "p_value": p_value,
                    "response_informative": not invalid,
                }
            )
    decisions = holm([row["p_value"] for row in endpoints], config["alpha"] / 2)
    for row, rejected in zip(endpoints, decisions, strict=True):
        row["detected"] = rejected
    # Two-sided simultaneous component intervals test held-out response and
    # decoder predictions. Their uncertainty is reported, never read as fidelity.
    controls = []
    from et_campaign import et_group

    ideals = {member.name: member.ideal for member in et_group(config).members}
    comparisons = sum(item["kind"] == "decoder" or item.get("held_out", False) for item in metadata.values())
    per_bin_tail = 0.01 / (max(1, comparisons) * 64)
    for name, item in metadata.items():
        if item["kind"] != "decoder" and not item.get("held_out", False):
            continue
        matrix, epsilon, _ = response[(tuple(item["spec"]), item["block"], item["basis"])]
        ideal = ideals[name]
        expected = matrix @ ideal
        probabilities, count = histograms[name]
        radius = math.sqrt(math.log(2 / per_bin_tail) / (2 * count)) + epsilon / 2
        residual = float(np.max(abs(probabilities - expected)))
        controls.append(
            {
                "member": name,
                "max_residual": residual,
                "simultaneous_allowance": radius,
                "compatible": residual <= radius,
            }
        )
    reasons = []
    if contexts is None:
        reasons.append("physical-control maps and compatible execution epochs are required")
    elif set(contexts) != set(metadata) or any(not context.get("validated") for context in contexts.values()):
        reasons.append("physical-control context validation failed")
    if any(not row["compatible"] for row in controls):
        reasons.append("held-out readout or decoder control discrepancy")
    if any(not row["response_informative"] for row in endpoints):
        reasons.append("singular or ill-conditioned response calibration")
    return {
        "admitted": not reasons and all(decisions),
        "withheld": "; ".join(reasons) if reasons else None,
        "endpoints": endpoints,
        "controls": controls,
        "calibration_tail": calibration_tail,
        "endpoint_family_tail": config["alpha"] / 2,
        "control_diagnostic_tail": 0.01,
        "assumption": config["sampling_assumption"],
        "interpretation": config["interpretation"],
    }
