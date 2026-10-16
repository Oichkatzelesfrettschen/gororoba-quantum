"""Signed perturbation of a certified sedenion kernel: a dark count against a dilation reference.

In the sedenions (D = 16, cd_core convention), L_(e1+e10) annihilates
u = (e4 - e15)/sqrt2. Perturb along L_e2:

    L(t) = L_e1 + L_e10 + t L_e2,   alpha(t) = 2 + |t|,   B(t) = L(t) / alpha(t).

alpha is the 1-norm of the three signed-permutation coefficients, so B(t) is a
contraction that a three-term LCU block-encodes. With v = L_e2 u, a unit
vector because L_e2 is orthogonal, the kernel identity L(0) u = 0 gives
B(t) u = t v / alpha(t) and two observables:

    dark success      p(t) = ||B(t) u||^2 = t^2 / (2 + |t|)^2,
    dilation overlap  Re<v|B(t)|u> = <Psi|D(t)|Psi> = t / (2 + |t|),

with D(t) = [[0, B^dagger], [B, 0]] and Psi = (|0>u + |1>v)/sqrt2. p is even
in t; the overlap keeps the sign and is first order. At t = +-1/20 they are
1/1681 and +-1/41.

Circuits, data on qubits 0-3 (algebra bit b on qubit b), selector on 4-5:

- dark: load u, PREP the selector with amplitudes sqrt(|t|/alpha),
  sqrt(1/alpha), sqrt(1/alpha) on s = 0, 1, 2, SELECT sign(t) L_e2, L_e1 and
  L_e10, PREP^dagger, read the selector: P(00) = p(t). The selector-00 block
  of that unitary equals B(t) entry by entry.
- signed: the same PREP, then a control qubit 6 in |+> that selects SELECT
  (control 0) or L_e2 on the data (control 1). Both branches share the
  prepared selector |s> = sum_k a_k |k>, so <X_c> before the final H, read as
  <Z_c> after it, is <s,v|SELECT|s,u> = sum_k a_k^2 <v|L_k|u> = Re<v|B(t)|u>
  with no PREP^dagger. The sign of t sits on the e2 entries of the diagonal
  inside branch 0, so it is a relative phase between the branches.

The module certifies the kernel and both laws in exact rationals, checks the
circuits by statevector, applies the mutations that must break the signed
law, compiles both probes on FakeFez and prices shots against direct
counting. Run with --out to write the evidence, --check to re-derive it.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Parameter
from qiskit.circuit.library import DiagonalGate, MCPhaseGate, StatePreparation
from qiskit.quantum_info import Operator, Statevector

from cd_core import cd_multiply, cd_sign
from select_lcu import sparse_pair_prep

DIM = 16
LEFT = (1, 10)
DIRECTION = 2
KERNEL = {4: 1, 15: -1}
CHECK_T = (Fraction(-1, 5), Fraction(-1, 20), Fraction(0), Fraction(1, 20), Fraction(1, 5))
SEED = 20261015
# The ibm_kingston zero-divisor fringe run anchors the hardware scenario: its
# collection carries the measured Design B dark floor and fringe visibility,
# its record the compiled CZ count of the dark member, and both files are
# pinned by digest.
ANCHOR_RUN = "results/live/2026-10-15T070853.550532Z"
ANCHOR_SHA256 = {
    "collect.json": "2d6b3b2eeb9dd3aadc29f524f51e233c2d259ce508690bf28f63d83aea410696",
    "record.json": "22c078143a9e266123ad0f9acba9f3c234ac1c6522aa3e669eb4a579aee32c65",
}
ANCHOR_MEMBER = "design_b_dark_1_10_4_15"
ROOT = Path(__file__).resolve().parent.parent
Z_SCORE = 3.0


def _vector(support: dict[int, int]) -> list[int]:
    vector = [0] * DIM
    for index, value in support.items():
        vector[index] = value
    return vector


def _left(m: int, vector: list[int]) -> list[int]:
    """L_e_m applied to an integer vector; cd_multiply sums +-1 multiples of integers exactly."""
    product = cd_multiply(DIM, [float(i == m) for i in range(DIM)], [float(value) for value in vector])
    if not all(value.is_integer() for value in product):
        raise ValueError("a signed permutation of an integer vector left the integers")
    return [int(value) for value in product]


def certificate() -> dict[str, Any]:
    """Exact integer certificate of the kernel, the perturbation and both laws."""
    u = _vector(KERNEL)
    product = [a + b for a, b in zip(_left(LEFT[0], u), _left(LEFT[1], u), strict=True)]
    if any(product):
        raise ValueError("L_(e1+e10) does not annihilate e4 - e15")
    v = _left(DIRECTION, u)
    norm_u = sum(value * value for value in u)
    if sum(value * value for value in v) != norm_u:
        raise ValueError("L_e2 does not preserve the norm of the kernel vector")
    if sum(a * b for a, b in zip(u, v, strict=True)) != 0:
        raise ValueError("v is not orthogonal to u")
    laws = []
    for t in CHECK_T:
        alpha = 2 + abs(t)
        image = [t * value for value in v]
        dark = sum(value * value for value in image) / (norm_u * alpha * alpha)
        overlap = sum(a * b for a, b in zip(v, image, strict=True)) / (norm_u * alpha)
        if dark != t * t / (alpha * alpha) or overlap != t / alpha:
            raise ValueError(f"exact laws fail at t = {t}")
        laws.append({"t": str(t), "dark_success": str(dark), "dilation_overlap": str(overlap)})
    return {
        "u_unnormalized": {str(index): value for index, value in KERNEL.items()},
        "v_unnormalized": {str(index): value for index, value in enumerate(v) if value},
        "laws": laws,
    }


# Selector value s carries the unit m(s) = 2 ^ s0*3 ^ s1*8: e2, e1, e10 for
# s = 0, 1, 2, and the unused s = 3 (amplitude zero) completes the affine map,
# so the basis permutation of every term is X on bit 1 plus CX from s0 onto
# bits 0 and 1 and from s1 onto bit 3.
SELECTOR_UNITS = (DIRECTION, LEFT[0], LEFT[1])
COMMON_FLIP, S0_FLIP, S1_FLIP = 2, 3, 8


def selector_unit(value: int) -> int:
    return COMMON_FLIP ^ (S0_FLIP if value & 1 else 0) ^ (S1_FLIP if value & 2 else 0)


def _prep(t: float) -> StatePreparation:
    alpha = 2.0 + abs(t)
    return StatePreparation([math.sqrt(abs(t) / alpha), math.sqrt(1.0 / alpha), math.sqrt(1.0 / alpha), 0.0])


def _sign_diagonal(t: float, controlled: bool, drop_sign: bool) -> DiagonalGate:
    """Every term's cd_sign diagonal in one gate, with sign(t) on the e2 term.

    Index z = q + 16 s (+ 64 c): branch c = 1 of the signed probe carries the
    diagonal of L_e2 alone; s = 3 has zero amplitude and keeps sign +1.
    """
    term_sign = -1.0 if t < 0 and not drop_sign else 1.0
    entries = []
    for c in (0, 1) if controlled else (0,):
        for value in range(4):
            for q in range(DIM):
                if c:
                    entries.append(float(cd_sign(DIM, DIRECTION, q)))
                elif value == 3:
                    entries.append(1.0)
                else:
                    sign = float(cd_sign(DIM, selector_unit(value), q))
                    entries.append(sign * (term_sign if value == 0 else 1.0))
    return DiagonalGate(entries)


def _load_u(circuit: QuantumCircuit) -> None:
    circuit.compose(sparse_pair_prep(4, 4, 15, math.pi), [0, 1, 2, 3], inplace=True)


def _bits(mask: int) -> list[int]:
    return [bit for bit in range(4) if mask >> bit & 1]


def block_encoding(t: float) -> QuantumCircuit:
    """PREP, SELECT, PREP^dagger on data 0-3 and selector 4-5; its selector-00 block is B(t)."""
    circuit = QuantumCircuit(6, name="kernel_block")
    circuit.append(_prep(t), [4, 5])
    circuit.append(_sign_diagonal(t, controlled=False, drop_sign=False), range(6))
    for bit in _bits(COMMON_FLIP):
        circuit.x(bit)
    for bit in _bits(S0_FLIP):
        circuit.cx(4, bit)
    for bit in _bits(S1_FLIP):
        circuit.cx(5, bit)
    circuit.append(_prep(t).inverse(), [4, 5])
    return circuit


def dark_probe(t: float) -> QuantumCircuit:
    circuit = QuantumCircuit(6, 2, name="kernel_dark")
    _load_u(circuit)
    circuit.compose(block_encoding(t), range(6), inplace=True)
    circuit.measure([4, 5], [0, 1])
    return circuit


def signed_probe(t: float, *, drop_sign: bool = False, branch_prep: bool = False) -> QuantumCircuit:
    """Hadamard test of Re<v|B(t)|u> on control qubit 6.

    Branch c = 0 applies SELECT and branch c = 1 applies L_e2; both share the X
    on bit 1, so only the diagonal and the selector CX layer are controlled.
    drop_sign applies |t| L_e2 instead of t L_e2; branch_prep prepares the
    selector in branch 0 only, so the branches recombine with different
    selector states. Both are the mutations that must break the signed law.
    """
    circuit = QuantumCircuit(7, 1, name="kernel_signed")
    _load_u(circuit)
    circuit.h(6)
    if branch_prep:
        circuit.append(_prep(t).control(1, ctrl_state="0"), [6, 4, 5])
    else:
        circuit.append(_prep(t), [4, 5])
    circuit.append(_sign_diagonal(t, controlled=True, drop_sign=drop_sign), range(7))
    for bit in _bits(COMMON_FLIP):
        circuit.x(bit)
    # ctrl_state reads the last-listed control first: "01" is control 6 at 0
    # and the selector bit at 1.
    for bit in _bits(S0_FLIP):
        circuit.ccx(4, 6, bit, ctrl_state="01")
    for bit in _bits(S1_FLIP):
        circuit.ccx(5, 6, bit, ctrl_state="01")
    circuit.h(6)
    circuit.measure(6, 0)
    return circuit


# Structure-matched probes: one parametrized circuit for every t. The selector
# amplitudes (sqrt(|t|/alpha), sqrt(1/alpha), sqrt(1/alpha), 0) come from two
# RY angles, and sign(t) is a phase SIGN_PHASE = pi on selector 00 (and control
# 0 in the signed probe) instead of an entry of the synthesized diagonal, so a
# compile at bound parameters differs between t only in rotation angles.
PREP_HIGH = Parameter("prep_high")
PREP_LOW = Parameter("prep_low")
SIGN_PHASE = Parameter("sign_phase")


def matched_values(t: float) -> dict[Parameter, float]:
    alpha = 2.0 + abs(t)
    a0, a1, a2 = math.sqrt(abs(t) / alpha), math.sqrt(1.0 / alpha), math.sqrt(1.0 / alpha)
    return {
        PREP_HIGH: 2.0 * math.atan2(a2, math.hypot(a0, a1)),
        PREP_LOW: 2.0 * math.atan2(a1, a0),
        SIGN_PHASE: math.pi if t < 0 else 0.0,
    }


def _matched_prep() -> QuantumCircuit:
    """Selector 4-5 (s0, s1) from |00>: RY on s1, then RY on s0 controlled on s1 = 0."""
    prep = QuantumCircuit(2, name="prep")
    prep.ry(PREP_HIGH, 1)
    prep.x(1)
    prep.cry(PREP_LOW, 1, 0)
    prep.x(1)
    return prep


def _phase_on_zero(circuit: QuantumCircuit, qubits: list[int]) -> None:
    """Phase exp(i SIGN_PHASE) on the all-zero state of ``qubits``."""
    circuit.x(qubits)
    circuit.append(MCPhaseGate(SIGN_PHASE, len(qubits) - 1), qubits)
    circuit.x(qubits)


def matched_dark_probe() -> QuantumCircuit:
    circuit = QuantumCircuit(6, 2, name="kernel_dark_matched")
    _load_u(circuit)
    circuit.compose(_matched_prep(), [4, 5], inplace=True)
    circuit.append(_sign_diagonal(1.0, controlled=False, drop_sign=True), range(6))
    _phase_on_zero(circuit, [4, 5])
    for bit in _bits(COMMON_FLIP):
        circuit.x(bit)
    for bit in _bits(S0_FLIP):
        circuit.cx(4, bit)
    for bit in _bits(S1_FLIP):
        circuit.cx(5, bit)
    circuit.compose(_matched_prep().inverse(), [4, 5], inplace=True)
    circuit.measure([4, 5], [0, 1])
    return circuit


def matched_signed_probe() -> QuantumCircuit:
    circuit = QuantumCircuit(7, 1, name="kernel_signed_matched")
    _load_u(circuit)
    circuit.h(6)
    circuit.compose(_matched_prep(), [4, 5], inplace=True)
    circuit.append(_sign_diagonal(1.0, controlled=True, drop_sign=True), range(7))
    _phase_on_zero(circuit, [4, 5, 6])
    for bit in _bits(COMMON_FLIP):
        circuit.x(bit)
    for bit in _bits(S0_FLIP):
        circuit.ccx(4, 6, bit, ctrl_state="01")
    for bit in _bits(S1_FLIP):
        circuit.ccx(5, 6, bit, ctrl_state="01")
    circuit.h(6)
    circuit.measure(6, 0)
    return circuit


def block_encoding_error(t: float) -> float:
    """Largest entry error between the selector-00 block of block_encoding(t) and B(t)."""
    matrix = Operator(block_encoding(t)).data[:DIM, :DIM]
    expected = np.zeros((DIM, DIM))
    for m, weight in ((LEFT[0], 1.0), (LEFT[1], 1.0), (DIRECTION, t)):
        for q in range(DIM):
            expected[m ^ q, q] += weight * cd_sign(DIM, m, q)
    return float(np.max(np.abs(matrix - expected / (2.0 + abs(t)))))


def _probability(circuit: QuantumCircuit, qubits: list[int], outcome: int) -> float:
    state = Statevector(circuit.remove_final_measurements(inplace=False))
    return float(state.probabilities(qubits)[outcome])


def statevector_checks() -> dict[str, Any]:
    rows = []
    for exact_t in CHECK_T:
        t = float(exact_t)
        alpha = 2.0 + abs(t)
        dark = _probability(dark_probe(t), [4, 5], 0)
        x_c = 2.0 * _probability(signed_probe(t), [6], 0) - 1.0
        if abs(dark - t * t / alpha**2) > 1e-12 or abs(x_c - t / alpha) > 1e-12:
            raise ValueError(f"circuit laws fail at t = {t}: dark {dark}, <X_c> {x_c}")
        rows.append({"t": str(exact_t), "dark_success": dark, "x_control": x_c})
    if [selector_unit(value) for value in range(3)] != list(SELECTOR_UNITS):
        raise ValueError("the affine selector map does not carry e2, e1, e10")
    block_error = max(block_encoding_error(float(exact_t)) for exact_t in CHECK_T)
    if block_error > 1e-12:
        raise ValueError(f"the selector-00 block differs from B(t) by {block_error}")
    t = float(CHECK_T[1])
    unsigned = 2.0 * _probability(signed_probe(t, drop_sign=True), [6], 0) - 1.0
    split = 2.0 * _probability(signed_probe(t, branch_prep=True), [6], 0) - 1.0
    if abs(unsigned + t / (2.0 + abs(t))) > 1e-12:
        raise ValueError("dropping the sign must read +|t|/alpha at negative t")
    if abs(split - t / (2.0 + abs(t))) < 1e-3:
        raise ValueError("a selector prepared in one branch only must change the overlap")
    return {
        "rows": rows,
        "block_encoding_max_error_below_1e-12": True,
        "mutations": {
            "drop_sign_at_t_minus_1_20": unsigned,
            "branch_prep_at_t_minus_1_20": split,
        },
    }


def native_cost() -> dict[str, Any]:
    from qiskit_ibm_runtime.fake_provider import FakeFez

    backend = FakeFez()
    errors = sorted(
        value[0]
        for gate in backend.properties().gates
        if gate.gate == "cz"
        for value in [[param.value for param in gate.parameters if param.name == "gate_error"]]
        if value and value[0] < 1.0
    )
    median_cz_error = float(np.median(errors))
    out: dict[str, Any] = {"backend": "FakeFez", "median_cz_error": median_cz_error, "seed_transpiler": SEED}
    for name, circuit in (("dark", dark_probe(-0.05)), ("signed", signed_probe(-0.05))):
        compiled = transpile(circuit, backend, optimization_level=3, seed_transpiler=SEED)
        counts = compiled.count_ops()
        cz = int(counts.get("cz", 0))
        out[name] = {
            "cz": cz,
            "depth": compiled.depth(),
            "gate_visibility_factor": (1.0 - median_cz_error) ** cz,
        }
    return out


def hardware_anchor() -> dict[str, Any]:
    """Dark floor, visibility and dark-member CZ count of the pinned Kingston fringe run."""
    import hashlib

    run = ROOT / ANCHOR_RUN
    for name, expected in ANCHOR_SHA256.items():
        if hashlib.sha256((run / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"{ANCHOR_RUN}/{name} differs from its pinned digest")
    collect = json.loads((run / "collect.json").read_text())
    summary = next(
        group["measured_statistics"]["summary"]
        for group in collect
        if isinstance(group, dict) and "visibility" in group.get("measured_statistics", {}).get("summary", {})
    )

    def members(node: Any) -> Any:
        if isinstance(node, dict):
            if node.get("name") == ANCHOR_MEMBER and isinstance(node.get("cz"), int):
                yield node["cz"]
            for value in node.values():
                yield from members(value)
        elif isinstance(node, list):
            for value in node:
                yield from members(value)

    counts = set(members(json.loads((run / "record.json").read_text())))
    if len(counts) != 1:
        raise ValueError(f"{ANCHOR_MEMBER} carries CZ counts {sorted(counts)} in the anchor record")
    return {
        "run": ANCHOR_RUN,
        "dark_floor": float(summary["p0_dark"]),
        "visibility": float(summary["visibility"]),
        "dark_member_cz": counts.pop(),
    }


def shot_scenarios(cost: dict[str, Any], anchor: dict[str, Any]) -> list[dict[str, Any]]:
    """Shots for a z = Z_SCORE resolution in each readout, under one criterion.

    Dark counting estimates the rate b + p above a background b, so it needs
    z^2 (b + p)(1 - b - p) / p^2 shots; the signed readout sees V s with
    s = t/(2+|t|) and needs z^2 (1 - V^2 s^2)/(V s)^2. Since p = s^2, the two
    agree at b = 0 and V = 1. dark_one_count_shots is a different quantity,
    ln(20)/p shots for a 95 percent chance of at least one dark count at b = 0.
    The hardware scenario takes the anchor run's floor b and visibility V; the
    signed visibility multiplies V by (1 - e)^(CZ - CZ_anchor) at the median
    FakeFez CZ error e, while the dark count keeps b, a lower bound for a
    probe with more CZ than the anchor, so the comparison favors dark
    counting. These price the readouts and predict no hardware result.
    """
    scenarios = (
        (0.0, 1.0, "ideal"),
        (anchor["dark_floor"], anchor["visibility"], "kingston_design_b_fringe"),
    )
    rows = []
    for t in (0.05, 0.1, 0.2):
        alpha = 2.0 + t
        p = t * t / alpha**2
        s = t / alpha
        for background, visibility, label in scenarios:
            extra = cost["signed"]["cz"] - anchor["dark_member_cz"]
            gate = (1.0 - cost["median_cz_error"]) ** extra if label != "ideal" else 1.0
            effective = visibility * gate
            rate = background + p
            dark = Z_SCORE**2 * rate * (1.0 - rate) / p**2
            signed = Z_SCORE**2 * (1.0 - (effective * s) ** 2) / (effective * s) ** 2
            rows.append(
                {
                    "t": t,
                    "scenario": label,
                    "dark_success": p,
                    "dark_shots": math.ceil(dark),
                    "dark_one_count_shots": math.ceil(math.log(20.0) / p) if background == 0.0 else None,
                    "signed_effective_visibility": effective,
                    "signed_shots": math.ceil(signed),
                    "dark_resolves_sign": False,
                }
            )
    return rows


def evidence() -> dict[str, Any]:
    cost = native_cost()
    anchor = hardware_anchor()
    return {
        "schema": "signed-kernel-probe-v1",
        "convention": "cd_core.cd_sign, D = 16, algebra bit b on qubit b",
        "certificate": certificate(),
        "statevector": statevector_checks(),
        "native_cost": cost,
        "hardware_anchor": anchor,
        "shot_scenarios": shot_scenarios(cost, anchor),
    }


def _matches(retained: Any, derived: Any, where: str = "$") -> list[str]:
    """Structural comparison: keys, lengths, strings and integers exact; floats to 1e-9 relative.

    Statevector and fit floats differ in their last digits between BLAS builds,
    while exact rationals stay strings and compiled CZ counts stay integers.
    """
    if isinstance(retained, dict) and isinstance(derived, dict):
        if retained.keys() != derived.keys():
            return [f"{where}: keys {sorted(retained)} != {sorted(derived)}"]
        return [problem for key in retained for problem in _matches(retained[key], derived[key], f"{where}.{key}")]
    if isinstance(retained, list) and isinstance(derived, list):
        if len(retained) != len(derived):
            return [f"{where}: length {len(retained)} != {len(derived)}"]
        return [
            problem
            for index, pair in enumerate(zip(retained, derived, strict=True))
            for problem in _matches(*pair, f"{where}[{index}]")
        ]
    if isinstance(retained, float) or isinstance(derived, float):
        if isinstance(retained, bool) or isinstance(derived, bool):
            return [] if retained == derived else [f"{where}: {retained} != {derived}"]
        if math.isclose(float(retained), float(derived), rel_tol=1e-9, abs_tol=1e-12):
            return []
        return [f"{where}: {retained} != {derived}"]
    return [] if retained == derived else [f"{where}: {retained!r} != {derived!r}"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    arguments = parser.parse_args()
    data = evidence()
    text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    if arguments.out is not None:
        arguments.out.write_text(text)
        return 0
    problems = _matches(json.loads(arguments.check.read_text()), json.loads(text))
    if problems:
        print(f"signed kernel probe: {arguments.check} differs from the re-derived evidence:", file=sys.stderr)
        for problem in problems[:20]:
            print(f"  {problem}", file=sys.stderr)
        return 1
    signed = data["native_cost"]["signed"]["cz"]
    print(f"signed kernel probe: exact laws at {len(CHECK_T)} points, 2 mutations rejected, signed probe {signed} CZ")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
