"""Estimators and the preregistered decision of the A_5 complex kernel case on Garnet.

Each kind of circuit (operand, real | complex | plain) runs in two orientations, + and -; its arm difference is
D = P_plus(s = 0) - P_minus(s = 0) of the selector bit, estimated from the kept shots (heralded) of the copies of each
orientation. An operand holds the real kind r (the block of e_i + e_j) and the complex kind c (e_i + i e_j). By the
complement law of ledger row A5-629 the ideal differences satisfy D_c + D_r = 1, so the pair measures the visibility
V = D_c + D_r and the ideal readings of N / 16 are D_c / V and D_r / V. The estimators:

- the raw double difference DD = D_c - D_r, ideal value (2 D_c - 1) V, which needs no division;
- the visibility-normalized double difference r = DD / V, ideal 2 D_c / V - 1 = (N_c - 8) / 8, and the nullity
  N_c = 8 + 8 r = 16 D_c / V, undefined when V lies within Z_RESOLVE standard errors of zero;
- the null-subtracted nullity N_c' = 8 + 8 (r - r_null), where r_null is r of the null operand: its real and complex
  readings coincide at the stratum 8 / 8, so its ideal r vanishes and r_null measures the offset the S gates add to
  every operand on the same qubits (odd(t) - odd(0) of the hardware-probe rule);
- the mutation reading D_p / V of the plain-phase kind, the same circuit with the pair sign s_k dropped.

The estimators never read the ideal sign table of the complex circuit. A device that returns the real-map law for the
complex circuit gives D_c = D_r and reads N_c = 8; one that returns the plain law gives a negative D_c at the
mutation operands.
"""

from __future__ import annotations

import math
from typing import Any

PHI = 1.54  # 95 percent upper bound of the retained Garnet copy-to-copy Pearson dispersion (grover-plane case)
Z_RESOLVE = 5.0
MIDPOINT = 8.0  # N_r + N_c = 16 on every pair, so the complex and real readings split at 8
# Discriminating operands and the side of 8 on which the complex reading lies; s808 is the null operand.
DISCRIMINATING: dict[str, int] = {"s016": 1, "s412": 1, "s124": -1}
NULL_OPERAND = "s808"
MUTATION_OPERANDS = ("s016", "s412")

Counts = tuple[int, int, int, int]  # (selector-zero kept shots +, kept shots +, selector-zero -, kept shots -)


def difference(counts: Counts, phi: float = PHI) -> tuple[float, float]:
    """(D, variance of D) from the selector-zero counts of the + and - orientations, binomial variance times phi."""
    k_plus, n_plus, k_minus, n_minus = counts
    if min(n_plus, n_minus) <= 0:
        raise ValueError("an orientation kept no shots")
    p_plus, p_minus = k_plus / n_plus, k_minus / n_minus
    variance = phi * (p_plus * (1 - p_plus) / n_plus + p_minus * (1 - p_minus) / n_minus)
    return p_plus - p_minus, variance


def operand_estimates(real: Counts, cplx: Counts, phi: float = PHI) -> dict[str, float | None]:
    """DD, V and N_c of one operand with delta-method standard errors; N_c is None when V is not resolved."""
    d_r, var_r = difference(real, phi)
    d_c, var_c = difference(cplx, phi)
    visibility, var_v = d_c + d_r, var_c + var_r
    out: dict[str, float | None] = {
        "d_real": d_r,
        "d_complex": d_c,
        "dd": d_c - d_r,
        "se_dd": math.sqrt(var_v),
        "visibility": visibility,
        "se_visibility": math.sqrt(var_v),
        "ratio": None,
        "se_ratio": None,
        "n_c": None,
        "se_n_c": None,
    }
    if visibility > Z_RESOLVE * math.sqrt(var_v):
        # N_c = 16 D_c / (D_c + D_r): dN/dD_c = 16 D_r / V^2 and dN/dD_r = -16 D_c / V^2.
        out["n_c"] = 16 * d_c / visibility
        se_n = 16 / visibility**2 * math.sqrt(d_r**2 * var_c + d_c**2 * var_r)
        out["se_n_c"] = se_n
        out["ratio"] = (d_c - d_r) / visibility
        out["se_ratio"] = se_n / 8
    return out


def mutation_reading(plain: Counts, estimates: dict[str, float | None], phi: float = PHI) -> tuple[float, float] | None:
    """(D_p / V, standard error) of the plain-phase kind against the visibility of its operand; None when the
    visibility is not resolved above zero."""
    d_p, var_p = difference(plain, phi)
    visibility, se_v = estimates["visibility"], estimates["se_visibility"]
    if visibility is None or se_v is None or visibility <= Z_RESOLVE * se_v:
        return None
    return d_p / visibility, math.sqrt(var_p / visibility**2 + d_p**2 * se_v**2 / visibility**4)


def side(n_c: float | None, se: float | None, expected_sign: int) -> str:
    """complex-side, real-side or unresolved from a nullity reading against the midpoint 8, for an operand whose
    complex reading lies on the side expected_sign (+1 above 8, -1 below)."""
    if n_c is None or se is None or se <= 0:
        return "unresolved"
    z = expected_sign * (n_c - MIDPOINT) / se
    if z >= Z_RESOLVE:
        return "complex-side"
    if z <= -Z_RESOLVE:
        return "real-side"
    return "unresolved"


def subtracted(estimates: dict[str, float | None], null: dict[str, float | None]) -> tuple[float | None, float | None]:
    """(N_c', standard error) with the null operand's r subtracted; None when either visibility is unresolved."""
    r, se_r, r0, se_r0 = estimates["ratio"], estimates["se_ratio"], null["ratio"], null["se_ratio"]
    if r is None or se_r is None or r0 is None or se_r0 is None:
        return None, None
    return MIDPOINT + 8 * (r - r0), 8 * math.hypot(se_r, se_r0)


def analyze(counts: dict[str, dict[str, Counts]], phi: float = PHI) -> dict[str, Any]:
    """Operand -> kind -> counts, to the per-operand estimates, the null-subtracted readings, the mutation readings
    and the verdict.

    complex strata: the null operand's visibility is resolved, the three discriminating operands read on the complex
    side of 8 after the null subtraction, and the plain kind reads below zero at both mutation operands beyond
    Z_RESOLVE standard errors. real strata: the three discriminating operands read on the real side. Anything else is
    no reading."""
    estimates = {name: operand_estimates(kinds["real"], kinds["cplx"], phi) for name, kinds in counts.items()}
    null = estimates[NULL_OPERAND]
    readings = {name: subtracted(estimates[name], null) for name in DISCRIMINATING}
    sides = {name: side(*readings[name], sign) for name, sign in DISCRIMINATING.items()}
    mutations: dict[str, dict[str, float] | None] = {}
    for name in MUTATION_OPERANDS:
        reading = mutation_reading(counts[name]["plain"], estimates[name], phi)
        mutations[name] = (
            None
            if reading is None
            else {
                "reading": reading[0],
                "se": reading[1],
                "z_below_zero": -reading[0] / reading[1] if reading[1] > 0 else math.inf,
            }
        )
    null_resolved = null["ratio"] is not None
    if all(s == "complex-side" for s in sides.values()):
        mutated = all(m is not None and m["z_below_zero"] >= Z_RESOLVE for m in mutations.values())
        verdict = "complex strata" if mutated and null_resolved else "complex side, a control fails"
    elif all(s == "real-side" for s in sides.values()):
        verdict = "real strata"
    else:
        verdict = "no reading"
    return {
        "estimates": estimates,
        "null_ratio": null["ratio"],
        "subtracted": {name: {"n_c": r[0], "se": r[1]} for name, r in readings.items()},
        "sides": sides,
        "mutations": mutations,
        "null_resolved": null_resolved,
        "verdict": verdict,
    }


def z_values(result: dict[str, Any]) -> list[float]:
    """The z of every condition of the complex verdict: each discriminating operand's distance from 8 on its complex
    side in standard errors of the null-subtracted reading, each mutation reading below zero, and the null
    visibility."""
    out: list[float] = []
    for name, sign in DISCRIMINATING.items():
        row = result["subtracted"][name]
        out.append(sign * (row["n_c"] - MIDPOINT) / row["se"] if row["n_c"] is not None else -math.inf)
    for name in MUTATION_OPERANDS:
        m = result["mutations"][name]
        out.append(m["z_below_zero"] if m is not None else -math.inf)
    null = result["estimates"][NULL_OPERAND]
    out.append(null["visibility"] / null["se_visibility"])
    return out


def power(z_predicted: list[float]) -> float:
    """Probability that every z of the list reaches Z_RESOLVE when each is normal with unit variance about its
    predicted value (independent circuits)."""
    result = 1.0
    for z in z_predicted:
        result *= 0.5 * math.erfc((Z_RESOLVE - z) / math.sqrt(2.0))
    return result
