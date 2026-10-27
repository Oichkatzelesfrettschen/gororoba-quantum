"""Preregistered screens of the measurement-sequence envelope run and the pinching analysis over the qubits they keep.

Three screens withhold a qubit before the device test reads any measure-member outcome
(docs/design/measurement-sequence-adaptive-envelope.md):
- execution-time eligibility: every PUB holding one of the qubit's members ran under properties on which the qubit
  passes msq_envelope.qubit_eligibility, all PUBs under the same values; a missing value fails closed;
- reset equivalence: the upper end of the two-sided Bonferroni confidence interval on the readout-corrected
  difference between the reset controls' residual P1 (rc1 from |1>, rc0 from |0>) lies below RESET_MARGIN;
- pattern dispersion: within the patterns of each own state, the qubit's readout errors show no excess binomial
  dispersion across the other qubits' configurations (chi-square, Bonferroni over the 2W (qubit, own state) tests).
The kept qubits then run measurement_sequence_analysis.collected with the count rule max(2, ceil(0.1 W)).
"""

from __future__ import annotations

import math
from statistics import NormalDist
from typing import Any

import numpy as np
from scipy.stats import chi2

import measurement_sequence_analysis as msa
import msq_envelope
from diagnostic_experiments import MSQE_RESET_CONTROLS, msqe_pattern_member, msqe_reset_member

SCHEMA = "msq-envelope-analysis-v1"
SCREEN_ALPHA = 0.05
# Half the bound floor (measurement_sequence_analysis's registered 0.0188): fixed, so the reset screen does not move
# with the in-job residuals the departure floor reads.
RESET_MARGIN = 0.0094
# Below this many kept qubits the run reports per-qubit results and no device verdict.
MIN_KEPT = 8


def count_rule(width: int) -> int:
    """Informative qubits departing in one direction that fire the count rule at layout width W."""
    return max(2, math.ceil(0.1 * width))


def two_sided_z(alpha: float, tests: int) -> float:
    return NormalDist().inv_cdf(1.0 - alpha / (2.0 * tests))


def final_ones(law: np.ndarray, shots: int) -> int:
    """Shots whose final bit (clbit 0) reads 1, from a member's joint law over its clbits."""
    ones = shots * float(np.asarray(law, dtype=float)[1::2].sum())
    if abs(ones - round(ones)) > 1e-2 * max(1.0, shots / 1e4):
        raise msa.AnalysisError(f"P(final = 1) is not a whole-shot count: {ones}")
    return round(ones)


def member_ones(distributions: dict[str, list[np.ndarray]], executed: dict[str, Any], name: str) -> tuple[int, int]:
    if name not in distributions or len(distributions[name]) != 1:
        raise msa.AnalysisError(f"{name}: the envelope analysis reads exactly one replica")
    shots = int(executed[name]["shots"])
    return final_ones(distributions[name][0], shots), shots


def reset_screen(
    rc1: tuple[int, int], rc0: tuple[int, int], ro0: tuple[int, int], ro1: tuple[int, int], width: int
) -> dict[str, Any]:
    """The reset controls' readout-corrected residual difference and its Bonferroni upper confidence bound.

    The difference of two final P1 values divided by the in-job readout contrast P1(ro1) - P1(ro0) is the corrected
    difference: the shared P(1|0) offset cancels. A contrast at or below zero fails the screen.
    """
    p1, p0 = rc1[0] / rc1[1], rc0[0] / rc0[1]
    contrast = ro1[0] / ro1[1] - ro0[0] / ro0[1]
    z = two_sided_z(SCREEN_ALPHA, width)
    if contrast <= 0.0:
        return {"passes": False, "reason": f"readout contrast {contrast:.6g} is not positive", "z": z}
    difference = (p1 - p0) / contrast
    se = math.sqrt(p1 * (1.0 - p1) / rc1[1] + p0 * (1.0 - p0) / rc0[1]) / contrast
    upper = abs(difference) + z * se
    return {
        "difference": difference,
        "se": se,
        "z": z,
        "upper_bound": upper,
        "margin": RESET_MARGIN,
        "passes": upper < RESET_MARGIN,
    }


def pattern_screen(bits: list[int], ones: list[tuple[int, int]], width: int) -> dict[str, Any]:
    """Per own state, the chi-square dispersion of the qubit's readout errors across its patterns of that state.

    bits[k] is the qubit's own bit in pattern k and ones[k] its (final ones, shots). An error reads 1 from |0> or 0
    from |1>. A pooled error rate of 0 or 1 leaves no dispersion to test and reports a statistic of 0.
    """
    if len(bits) != len(ones):
        raise msa.AnalysisError("pattern bits and counts differ in length")
    tests = 2 * width
    states: dict[str, Any] = {}
    passes = True
    for state in (0, 1):
        rows = [(k if state == 0 else n - k, n) for bit, (k, n) in zip(bits, ones, strict=True) if bit == state]
        if len(rows) < 2:
            raise msa.AnalysisError(f"own state {state} has {len(rows)} patterns")
        errors, shots = sum(e for e, _ in rows), sum(n for _, n in rows)
        rate = errors / shots
        statistic = (
            0.0 if rate in (0.0, 1.0) else math.fsum((e - n * rate) ** 2 / (n * rate * (1.0 - rate)) for e, n in rows)
        )
        dof = len(rows) - 1
        p_value = float(chi2.sf(statistic, dof))
        kept = p_value > SCREEN_ALPHA / tests
        passes = passes and kept
        states[str(state)] = {
            "patterns": len(rows),
            "error_rate": rate,
            "statistic": statistic,
            "dof": dof,
            "p_value": p_value,
            "passes": kept,
        }
    return {"alpha_per_test": SCREEN_ALPHA / tests, "states": states, "passes": passes}


def execution_eligibility(executed: dict[str, Any], qubit: int, names: list[str]) -> str | None:
    """Why the qubit fails the layout rule's eligibility at its PUBs' execution starts, or None when it passes."""
    seen: dict[str, Any] | None = None
    for name in names:
        evidence = executed.get(name, {})
        coherence = evidence.get("placed_qubit_calibration", {}).get(str(qubit))
        gate = evidence.get("placed_gate_calibration", {}).get(str(qubit))
        if coherence is None or gate is None:
            return f"{name}: no execution-time calibration"
        values = {"coherence": coherence, "gate": gate}
        if seen is None:
            seen = values
        elif values != seen:
            return f"{name}: the calibration changed between the qubit's PUBs"
    if seen is None:
        return "no executed member"
    coherence, gate = seen["coherence"], seen["gate"]
    row = {
        "readout_error": coherence.get("readout_error"),
        "sx_error": gate.get("sx_error"),
        "t1_s": None if coherence.get("T1") is None else float(coherence["T1"]) * 1e-6,
        "t2_s": None if coherence.get("T2") is None else float(coherence["T2"]) * 1e-6,
        "prob_meas1_prep0": coherence.get("prob_meas1_prep0"),
    }
    return msq_envelope.qubit_eligibility(row)


def screens(
    record: dict[str, Any], distributions: dict[str, list[np.ndarray]], executed: dict[str, Any]
) -> dict[str, dict[str, Any]]:
    """Every qubit's three screens and whether it is kept."""
    configuration = record["family_configuration"]
    qubits = [int(q) for q in configuration["qubits"]]
    width = int(configuration["layout_width"])
    pattern_bits = [[int(b) for b in row] for row in configuration["pattern_bits"]]
    out: dict[str, dict[str, Any]] = {}
    for rank, qubit in enumerate(qubits):
        names = sorted(name for name in executed if name.endswith(f"_q{qubit}") and name.startswith("msq"))
        eligibility = execution_eligibility(executed, qubit, names)
        ro0 = member_ones(distributions, executed, msa.ro0_name(qubit))
        ro1 = member_ones(distributions, executed, msa.t1_names(qubit)[0])
        controls = {c: member_ones(distributions, executed, msqe_reset_member(c, qubit)) for c in MSQE_RESET_CONTROLS}
        reset = reset_screen(controls["rc1"], controls["rc0"], ro0, ro1, width)
        patterns = pattern_screen(
            [row[rank] for row in pattern_bits],
            [member_ones(distributions, executed, msqe_pattern_member(k, qubit)) for k in range(len(pattern_bits))],
            width,
        )
        kept = eligibility is None and reset["passes"] and patterns["passes"]
        out[str(qubit)] = {
            "execution_eligibility": eligibility,
            "reset": reset,
            "patterns": patterns,
            "kept": kept,
        }
    return out


def collected(
    record: dict[str, Any],
    distributions: dict[str, list[np.ndarray]],
    executed: dict[str, Any],
    floor: float | None = None,
) -> dict[str, Any]:
    """The screens, then the pinching analysis over the kept qubits, or the reason the device verdict is withheld."""
    try:
        screened = screens(record, distributions, executed)
    except (msa.AnalysisError, KeyError, ValueError) as error:
        return {"schema": SCHEMA, "withheld": str(error)}
    kept = [q for q in record["family_configuration"]["qubits"] if screened[str(q)]["kept"]]
    width = int(record["family_configuration"]["layout_width"])
    result: dict[str, Any] = {
        "schema": SCHEMA,
        "screens": screened,
        "kept_qubits": kept,
        "count_rule": count_rule(width),
    }
    if len(kept) < MIN_KEPT:
        result["pinching"] = {"schema": msa.SCHEMA, "withheld": f"{len(kept)} kept qubits, fewer than {MIN_KEPT}"}
        return result
    kept_record = {**record, "family_configuration": {**record["family_configuration"], "qubits": kept}}
    result["pinching"] = msa.collected(kept_record, distributions, executed, floor, count_rule(width))
    return result
