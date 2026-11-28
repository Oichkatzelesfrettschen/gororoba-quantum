"""Estimators and the preregistered decision of the A_5 complex kernel case on Garnet.

Each kind of circuit (operand, real | complex | plain | sentinel) runs in two orientations, + and -; its arm difference
is D = P_plus(s = 0) - P_minus(s = 0) of the selector bit, estimated from the kept shots (heralded) of the copies of
each orientation. An operand holds the real kind r (the block of e_i + e_j) and the complex kind c (e_i + i e_j). By
the complement law of ledger row A5-629 the ideal differences satisfy D_c + D_r = 1, so the pair measures the
visibility V = D_c + D_r and the ideal readings of N / 16 are D_c / V and D_r / V. The estimators:

- the raw double difference DD = D_c - D_r, ideal value (2 D_c - 1) V, which needs no division;
- the visibility-normalized double difference r = DD / V, ideal 2 D_c / V - 1 = (N_c - 8) / 8, and the nullity
  N_c = 8 + 8 r = 16 D_c / V, undefined when V lies within Z_RESOLVE standard errors of zero;
- the null-subtracted nullity N_c' = 8 + 8 (r - r_null), where r_null is r of the null operand: its real and complex
  readings coincide at the stratum 8 / 8, so its ideal r vanishes and r_null measures the offset the S gates add to
  every operand on the same qubits (odd(t) - odd(0) of the hardware-probe rule);
- the mutation reading D_p / V of the plain-phase kind, the same circuit with the pair sign s_k dropped, at the one
  operand whose coset carries a non-constant pair sign;
- the drift reading z of the sentinel: the real kind of the null operand runs at the outer end of the job and again
  at its center, and the two arm differences agree under a stationary device.

The estimators never read the ideal sign table of the complex circuit. A device that returns the real-map law for the
complex circuit gives D_c = D_r and reads N_c = 8; one that returns the plain law gives a negative D_c at the
mutation operand.

The rule below is frozen before the live calibration read and carries fixed numbers: no constant derives from the
predictions of the calibration set the case loads. The tolerance on N_c' is half the distance (4) between the
complex reading and the nearest wrong stratum of s412 and s124, so a reading accepted as complex lies closer to the
complex stratum than to the real one by a margin of the same size; the coherent audit of the case reports where it
stops holding.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
from scipy.special import ndtri
from scipy.stats import qmc

PHI = 1.54  # 95 percent upper bound of the retained Garnet copy-to-copy Pearson dispersion (grover-plane case)
Z_RESOLVE = 5.0
MIDPOINT = 8.0  # N_r + N_c = 16 on every pair, so the complex and real readings split at 8
# Discriminating operands and the side of 8 on which the complex reading lies; s808 is the null operand.
DISCRIMINATING: dict[str, int] = {"s016": 1, "s412": 1, "s124": -1}
IDEAL_COMPLEX: dict[str, float] = {"s016": 16.0, "s412": 12.0, "s124": 4.0}
NULL_OPERAND = "s808"
MUTATION_OPERANDS = ("s412",)
# The preregistered tolerances.
N_TOLERANCE = 2.0  # a stratum reading N_c' lies within this of its ideal value
V_S016_MIN = 0.5  # s016 reads its visibility alone (D_r = 0 makes N_c = 16 for any D_c > 0)
R_NULL_MAX = 0.08  # |r_null|: the offset of the null operand, at most 0.64 in N_c'
DRIFT_Z_MAX = Z_RESOLVE  # |z| between the outer and the center arm difference of the sentinel

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


def z_below_zero(reading: float, se: float) -> float:
    """How many standard errors the mutation reading lies below zero; a reading without spread is infinitely far on
    its own side of zero, so a dead control (reading 0, no spread) reads minus infinity and fails."""
    if se > 0:
        return -reading / se
    return math.inf if reading < 0 else -math.inf


def drift_z(outer: Counts, inner: Counts, phi: float = PHI) -> float | None:
    """z of the difference between the arm difference of the sentinel at the outer end of the job and at its center;
    None when neither orientation has spread."""
    d_o, var_o = difference(outer, phi)
    d_i, var_i = difference(inner, phi)
    if var_o + var_i <= 0:
        return None
    return (d_o - d_i) / math.sqrt(var_o + var_i)


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


def within(n_c: float | None, ideal: float) -> bool:
    return n_c is not None and abs(n_c - ideal) <= N_TOLERANCE


def analyze(counts: dict[str, dict[str, Counts]], phi: float = PHI) -> dict[str, Any]:
    """Operand -> kind -> counts, to the per-operand estimates, the null-subtracted readings, the controls and the
    verdict.

    complex strata within tolerance: the three discriminating operands read on the complex side of 8 after the null
    subtraction, each within N_TOLERANCE of its complex stratum (16, 12, 4), and every control holds: the plain kind
    reads below zero beyond Z_RESOLVE standard errors at the mutation operand, the null visibility resolves with
    |r_null| at most R_NULL_MAX, the s016 visibility reaches V_S016_MIN, and the sentinel's arm differences at the
    outer end and the center of the job agree within DRIFT_Z_MAX standard errors. real strata within tolerance: the
    three read on the real side within N_TOLERANCE of the real strata (0, 4, 12) with the null and drift controls
    holding. complex side, off tolerance and real side, off tolerance: the side holds and a reading lies beyond the
    tolerance. complex side, a control fails: the side and tolerance hold and a control fails. Anything else is no
    reading."""
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
            else {"reading": reading[0], "se": reading[1], "z_below_zero": z_below_zero(*reading)}
        )
    null_resolved = null["ratio"] is not None
    null_bounded = null_resolved and abs(float(null["ratio"] or 0.0)) <= R_NULL_MAX
    drift = drift_z(counts[NULL_OPERAND]["real"], counts[NULL_OPERAND]["sent"], phi)
    drift_ok = drift is not None and abs(drift) <= DRIFT_Z_MAX
    v016 = estimates["s016"]["visibility"]
    visibility_ok = v016 is not None and v016 >= V_S016_MIN
    mutated = all(m is not None and m["z_below_zero"] >= Z_RESOLVE for m in mutations.values())
    controls = {
        "mutation": mutated,
        "null_resolved_and_bounded": null_bounded,
        "s016_visibility": visibility_ok,
        "drift": drift_ok,
    }
    complex_within = all(within(readings[n][0], IDEAL_COMPLEX[n]) for n in DISCRIMINATING)
    real_within = all(within(readings[n][0], 16.0 - IDEAL_COMPLEX[n]) for n in DISCRIMINATING)
    if all(s == "complex-side" for s in sides.values()):
        if not complex_within:
            verdict = "complex side, off tolerance"
        elif all(controls.values()):
            verdict = "complex strata within tolerance"
        else:
            verdict = "complex side, a control fails"
    elif all(s == "real-side" for s in sides.values()):
        verdict = (
            "real strata within tolerance" if real_within and null_bounded and drift_ok else "real side, off tolerance"
        )
    else:
        verdict = "no reading"
    return {
        "estimates": estimates,
        "null_ratio": null["ratio"],
        "subtracted": {name: {"n_c": r[0], "se": r[1]} for name, r in readings.items()},
        "sides": sides,
        "mutations": mutations,
        "null_resolved": null_resolved,
        "drift_z": drift,
        "controls": controls,
        "verdict": verdict,
    }


def z_values(result: dict[str, Any]) -> list[float]:
    """The z of every conditional margin of the complex verdict: each discriminating operand's distance from 8 on
    its complex side in standard errors of the null-subtracted reading, each mutation reading below zero, the null
    visibility, and the margin of the s016 visibility over its floor."""
    out: list[float] = []
    for name, sign in DISCRIMINATING.items():
        row = result["subtracted"][name]
        out.append(sign * (row["n_c"] - MIDPOINT) / row["se"] if row["n_c"] is not None else -math.inf)
    for name in MUTATION_OPERANDS:
        m = result["mutations"][name]
        out.append(m["z_below_zero"] if m is not None else -math.inf)
    null = result["estimates"][NULL_OPERAND]
    out.append(null["visibility"] / null["se_visibility"])
    s016 = result["estimates"]["s016"]
    out.append((s016["visibility"] - V_S016_MIN) / s016["se_visibility"])
    return out


POWER_LOG2_POINTS = 12


def simulated_power(counts: dict[str, dict[str, Counts]], phi: float = PHI) -> float:
    """Probability that the complete rule returns complex strata within tolerance when the counts of every kind and
    orientation scatter about the given counts as independent normals of variance phi n p (1 - p), the same variance
    the estimators use. The joint rule runs on every draw, so the shared null operand and the shared visibilities
    enter as they do in the analysis. The draws are the unscrambled Sobol' sequence mapped through the normal
    quantile: a deterministic quadrature that takes no seed."""
    cells = [
        (name, kind, orient) for name, kinds in sorted(counts.items()) for kind in sorted(kinds) for orient in (0, 1)
    ]
    sobol = qmc.Sobol(d=len(cells), scramble=False)
    points = np.clip(sobol.random_base2(POWER_LOG2_POINTS), 1e-9, 1 - 1e-9)
    normals = ndtri(points)
    passed = 0
    for row in normals:
        drawn: dict[str, dict[str, list[int]]] = {
            name: {kind: [0, 0, 0, 0] for kind in kinds} for name, kinds in counts.items()
        }
        for z, (name, kind, orient) in zip(row, cells, strict=True):
            k, n = counts[name][kind][2 * orient], counts[name][kind][2 * orient + 1]
            p = k / n
            value = k + float(z) * math.sqrt(phi * n * p * (1 - p))
            drawn[name][kind][2 * orient] = int(round(min(max(value, 0.0), float(n))))
            drawn[name][kind][2 * orient + 1] = n
        cast = {name: {kind: (c[0], c[1], c[2], c[3]) for kind, c in kinds.items()} for name, kinds in drawn.items()}
        if analyze(cast, phi)["verdict"] == "complex strata within tolerance":
            passed += 1
    return passed / len(normals)
