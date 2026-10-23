"""What the signed kernel probe on Garnet measures: algebra dependence, coherent-error response, sign cocycle.

Three exact computations bound the reading of results/iqm/signed_kernel_probe_analysis.json.

kernel independence. The probe reads Re<v|B(t)|u> with v = L_e2 u. L_e2^T L_e1 and L_e2^T L_e10 are
antisymmetric on the sedenions (cd_core), so <L_e2 u, L_e1 u> = <L_e2 u, L_e10 u> = 0 for every real u
and the overlap equals t/(2 + |t|) whether or not u lies in the kernel of L(e1 + e10); on the support
{e4, e15} of the certified u it also holds for every replacement sign table. The zero-divisor property
is instead the eigenvalue -1 of K = L_e1^T L_e10 on u, equivalently <L_e1 u, L_e10 u> = -1: the
cancellation observable cos^2(theta) <w|L_e1 u> + sin^2(theta) <w|L_e10 u> with w = L_e1 u reads
cos(2 theta) for the kernel vector, a constant 1 for the bright vector (e4 + e15)/sqrt2, and a
different law under any flip of the L_e10 signs at e4 or e15.

coherent response. A coherent error moves <Z> of the measured qubit at first order, while randomized
benchmarking sees it at second order, so the calibration's depolarizing fidelities bound neither the
even offset nor the odd part. The response is the derivative of <Z> with respect to an over-rotation
(angle times 1 + eps) or axis error of every prx on a qubit, a residual Z rotation after every CZ on a
qubit, and a conditional-phase error of every CZ on a coupler, by central differences on the retained
compile restricted to its seven qubits. Every odd-part derivative vanishes at t = 0, where the signed
amplitude sqrt(|t|/(2 + |t|)) is zero, and grows with that amplitude rather than with t.

sign cocycle. e_p e_q = (-1)^f(p, q) e_(p xor q) in dimension 2^n, enumerated for n = 1 to 6; the
algebraic normal form of f over the 2n index bits has degree max(2, n), and its degree in q, maximized
over the left factor p, is max(1, n - 1): octonion left multiplication is at most a degree-2 phase (CZ
and Z), sedenion left multiplication reaches degree 3. The closed form beyond n = 6 is unproved.

Usage: "$PYTHON" scripts/iqm_probe_audit.py (--out FILE | --check FILE | --self-test)
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from math import comb
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
from cd_core import cd_sign  # noqa: E402
from parallel import ordered_map  # noqa: E402

CASE = ROOT / "results/iqm/cases/signed-kernel-probe"
DIM = 16
KERNEL = {4: 1.0, 15: -1.0}
BRIGHT = {4: 1.0, 15: 1.0}
T_GRID = (0.0, 0.01, 0.05, 0.125, 0.25, 0.5, 1.0)
RETAINED = {
    (0.25, False): "t+0.25-00",
    (0.25, True): "t-0.25-00",
    (0.05, False): "t+0.05-00",
    (0.05, True): "t-0.05-00",
}
STEP = 1e-4
COCYCLE_LEVELS = range(1, 7)
DIGITS = 9


def left(m: int, signs: np.ndarray | None = None) -> np.ndarray:
    matrix = np.zeros((DIM, DIM))
    for q in range(DIM):
        matrix[m ^ q, q] = cd_sign(DIM, m, q) * (1.0 if signs is None else signs[q])
    return matrix


def unit(support: dict[int, float]) -> np.ndarray:
    vector = np.zeros(DIM)
    for index, value in support.items():
        vector[index] = value
    return vector / np.linalg.norm(vector)


def signed_overlap(u: np.ndarray, t: float, l1: np.ndarray, l10: np.ndarray, l2: np.ndarray) -> float:
    return float((l2 @ u) @ ((l1 + l10 + t * l2) @ u) / (2 + abs(t)))


def cancellation(u: np.ndarray, theta: float, l1: np.ndarray, l10: np.ndarray) -> float:
    w = l1 @ u
    return float(math.cos(theta) ** 2 * (w @ l1 @ u) + math.sin(theta) ** 2 * (w @ l10 @ u))


def kernel_independence() -> dict[str, Any]:
    rng = np.random.default_rng(20261023)
    l1, l10, l2 = left(1), left(10), left(2)
    random_u = rng.normal(size=DIM)
    vectors = {
        "kernel (e4 - e15)/sqrt2": unit(KERNEL),
        "bright (e4 + e15)/sqrt2": unit(BRIGHT),
        "e4": unit({4: 1.0}),
        "seeded random unit vector": random_u / np.linalg.norm(random_u),
    }
    signed = []
    for name, u in vectors.items():
        signed.append(
            {
                "u": name,
                "kernel_residual": round(float(np.linalg.norm((l1 + l10) @ u)), DIGITS),
                "overlap": {f"{t:+.2f}": round(signed_overlap(u, t, l1, l10, l2), DIGITS) for t in (-0.05, 0.05)},
            }
        )
    tables = [tuple(rng.choice([-1.0, 1.0], size=DIM) for _ in range(3)) for _ in range(1000)]
    kernel = unit(KERNEL)
    law = 0.05 / 2.05
    signed_invariant = sum(
        abs(signed_overlap(kernel, 0.05, left(1, a), left(10, b), left(2, c)) - law) < 1e-12 for a, b, c in tables
    )
    crossing_broken = sum(abs(cancellation(kernel, math.pi / 4, left(1, a), left(10, b))) > 1e-12 for a, b, _ in tables)
    single_flips = [
        q
        for q in range(DIM)
        if abs(cancellation(kernel, math.pi / 4, l1, left(10, np.where(np.arange(DIM) == q, -1.0, 1.0)))) > 1e-12
    ]
    k = l1.T @ l10
    symmetric = np.linalg.eigvalsh((k + k.T) / 2)
    phis = (-0.25, -0.05, 0.0, 0.05, 0.25)
    return {
        "signed_overlap": signed,
        "random_sign_tables": len(tables),
        "signed_overlap_unchanged_by_sign_table": signed_invariant,
        "cancellation_crossing_broken_by_sign_table": crossing_broken,
        "cancellation_single_e10_flips_breaking_crossing": single_flips,
        "cancellation": {
            name: {f"{phi:+.2f}": round(cancellation(unit(s), math.pi / 4 + phi, l1, l10), DIGITS) for phi in phis}
            for name, s in (("kernel", KERNEL), ("bright", BRIGHT))
        },
        "k_eigenvalue_on_kernel": round(float(kernel @ k @ kernel), DIGITS),
        "k_eigenvalue_on_bright": round(float(unit(BRIGHT) @ k @ unit(BRIGHT)), DIGITS),
        "k_minus_one_multiplicity": int(np.sum(np.isclose(symmetric, -1.0))),
    }


def anf(values: np.ndarray, bits: int) -> np.ndarray:
    out = values.copy()
    for i in range(bits):
        step = 1 << i
        for j in range(len(out)):
            if j & step:
                out[j] ^= out[j ^ step]
    return out


def cocycle_level(n: int) -> dict[str, Any]:
    dim = 1 << n
    table = np.array([[1 if cd_sign(dim, p, q) < 0 else 0 for q in range(dim)] for p in range(dim)], dtype=np.uint8)
    # Index p + dim q over the 2n bits of (p, q).
    monomials = [m for m, bit in enumerate(anf(table.T.reshape(-1), 2 * n)) if bit]
    by_degree: dict[int, int] = {}
    for m in monomials:
        by_degree[m.bit_count()] = by_degree.get(m.bit_count(), 0) + 1
    fixed = 0
    for p in range(dim):
        row = [m.bit_count() for m, bit in enumerate(anf(table[p].copy(), n)) if bit]
        fixed = max([fixed, *row])
    closed = {k: comb(n, 2) + n if k == 2 else (2 ** (k - 1) - 1) * comb(n, k) for k in range(2, max(n, 2) + 1)}
    closed = {k: c for k, c in closed.items() if c}
    return {
        "dimension": dim,
        "degree": max(m.bit_count() for m in monomials),
        "monomials_by_degree": {str(k): v for k, v in sorted(by_degree.items())},
        "closed_form_holds": by_degree == closed,
        "degree_in_q_at_fixed_p": fixed,
    }


def cocycle() -> list[dict[str, Any]]:
    return ordered_map(cocycle_level, list(COCYCLE_LEVELS), min_items=2)


class Register:
    """Statevector of a Garnet circuit on the qubits it touches, with coherent errors per qubit and coupler."""

    def __init__(self, instructions: list[dict[str, Any]]) -> None:
        self.qubits = sorted({q for op in instructions for q in op["locus"]}, key=lambda q: int(q[2:]))
        self.index = {q: n for n, q in enumerate(self.qubits)}
        self.size = len(self.qubits)
        self.measured = next(op["locus"][0] for op in instructions if op["name"] == "measure")
        self.basis = np.arange(2**self.size)
        self.couplers = sorted(
            {tuple(sorted(self.index[q] for q in op["locus"])) for op in instructions if op["name"] == "cz"}
        )

    def bit(self, qubit: int) -> np.ndarray:
        return (self.basis >> qubit) & 1

    def z(self, instructions: list[dict[str, Any]], errors: dict[tuple[str, Any], float]) -> float:
        psi = np.zeros(2**self.size, complex)
        psi[0] = 1.0
        for op in instructions:
            if op["name"] == "prx":
                q = self.index[op["locus"][0]]
                angle = op["args"]["angle"] * (1 + errors.get(("over", q), 0.0))
                phase = op["args"]["phase"] + errors.get(("axis", q), 0.0)
                c, s = math.cos(angle / 2), math.sin(angle / 2)
                gate = np.array([[c, -1j * s * np.exp(-1j * phase)], [-1j * s * np.exp(1j * phase), c]])
                axis = self.size - 1 - q
                psi = np.moveaxis(np.tensordot(gate, psi.reshape([2] * self.size), axes=([1], [axis])), 0, axis)
                psi = psi.reshape(-1)
            elif op["name"] == "cz":
                a, b = (self.index[x] for x in op["locus"])
                both = self.bit(a) & self.bit(b)
                psi = psi * np.exp(1j * (math.pi + errors.get(("cphase", tuple(sorted((a, b)))), 0.0)) * both)
                for q in (a, b):
                    residual = errors.get(("zres", q), 0.0)
                    if residual:
                        psi = psi * np.exp(-1j * residual / 2 * (1 - 2 * self.bit(q)))
        probabilities = np.abs(psi) ** 2
        down = self.bit(self.index[self.measured]) == 0
        return float(probabilities[down].sum() - probabilities[~down].sum())

    def errors(self) -> list[tuple[str, Any]]:
        singles = [(kind, q) for kind in ("over", "axis", "zres") for q in range(self.size)]
        return singles + [("cphase", c) for c in self.couplers]

    def label(self, error: tuple[str, Any]) -> str:
        kind, where = error
        names = self.qubits[where] if isinstance(where, int) else "-".join(self.qubits[i] for i in where)
        return f"{kind}:{names}"


def compiled_arms() -> dict[tuple[float, bool], list[dict[str, Any]]]:
    """The retained seed of the case's compile, bound at every grid point; the retained arms must match."""
    import iqm_signed_probe as probe
    import iqm_sim
    from qiskit import transpile

    import signed_kernel_probe as skp

    prediction = json.loads((CASE / "prediction.json").read_text(encoding="utf-8"))
    calibration = iqm_sim.Calibration.from_directory(CASE / "calibration")
    _, coupling = probe.target_of(calibration)
    compiled = transpile(
        skp.matched_signed_probe(),
        basis_gates=["r", "cz"],
        coupling_map=coupling,
        optimization_level=3,
        seed_transpiler=prediction["chosen_seed"],
    )
    arms = {}
    for t in T_GRID:
        for negative in (False, True):
            values = skp.matched_values(t)
            values[skp.SIGN_PHASE] = math.pi if negative else 0.0
            arms[(t, negative)] = probe.to_iqm(compiled.assign_parameters(values), "arm", calibration.qubits)[
                "instructions"
            ]
    for key, name in RETAINED.items():
        retained = json.loads((CASE / f"circuits/{name}.json").read_text(encoding="utf-8"))["instructions"]
        if arms[key] != retained:
            raise ValueError(f"the recompiled arm {key} differs from the retained {name}")
    return arms


def derivative(item: tuple[list[dict[str, Any]], tuple[str, Any]]) -> float:
    instructions, error = item
    register = Register(instructions)
    return (register.z(instructions, {error: STEP}) - register.z(instructions, {error: -STEP})) / (2 * STEP)


def coherent_response() -> dict[str, Any]:
    arms = compiled_arms()
    register = Register(arms[(0.25, False)])
    errors = register.errors()
    keys = list(arms)
    grads = ordered_map(derivative, [(arms[key], error) for error in errors for key in keys])
    rows: list[dict[str, Any]] = []
    for n, error in enumerate(errors):
        g = dict(zip(keys, grads[n * len(keys) : (n + 1) * len(keys)], strict=True))
        odd = {f"{t}": round((g[(t, False)] - g[(t, True)]) / 2, 6) for t in T_GRID}
        even = {f"{t}": round((g[(t, False)] + g[(t, True)]) / 2, 6) for t in T_GRID}
        if max(abs(v) for v in (*odd.values(), *even.values())) > 1e-6:
            rows.append({"error": register.label(error), "odd": odd, "even": even})
    rows.sort(key=lambda r: -abs(r["even"]["0.05"]))
    ideal = {
        f"{t}": round((register.z(arms[(t, False)], {}) - register.z(arms[(t, True)], {})) / 2, DIGITS) for t in T_GRID
    }
    amplitude = {f"{t}": round(math.sqrt(t / (2 + t)), DIGITS) for t in T_GRID}
    return {
        "qubits": register.qubits,
        "measured": register.measured,
        "step": STEP,
        "ideal_odd": ideal,
        "signed_amplitude": amplitude,
        "max_abs_odd_derivative_at_t0": max(abs(r["odd"]["0.0"]) for r in rows),
        "derivatives": rows,
    }


def audit() -> dict[str, Any]:
    return {
        "schema": "iqm-signed-probe-audit-v1",
        "kernel_independence": kernel_independence(),
        "sign_cocycle": cocycle(),
        "coherent_response": coherent_response(),
    }


def self_test() -> str:
    independence = kernel_independence()
    if any(abs(r["overlap"]["+0.05"] - 0.05 / 2.05) > 1e-9 for r in independence["signed_overlap"]):
        raise RuntimeError("the signed overlap departs from t/(2 + |t|) for some u")
    if independence["signed_overlap_unchanged_by_sign_table"] != independence["random_sign_tables"]:
        raise RuntimeError("a sign table changed the signed overlap on the kernel support")
    if independence["cancellation"]["kernel"]["+0.00"] != 0.0 or independence["cancellation"]["bright"]["+0.00"] != 1.0:
        raise RuntimeError("the cancellation observable does not separate kernel from bright")
    if independence["cancellation_single_e10_flips_breaking_crossing"] != [4, 15]:
        raise RuntimeError("the crossing does not depend on the e10 signs at the kernel support")
    if independence["k_minus_one_multiplicity"] != 4:
        raise RuntimeError("the -1 eigenspace of L_e1^T L_e10 is not four-dimensional")
    levels = [cocycle_level(n) for n in range(1, 5)]
    if [level["degree"] for level in levels] != [2, 2, 3, 4] or not all(level["closed_form_holds"] for level in levels):
        raise RuntimeError(f"sign cocycle degrees {[level['degree'] for level in levels]}")
    flipped = left(10, np.where(np.arange(DIM) == 4, -1.0, 1.0))
    if abs(cancellation(unit(KERNEL), math.pi / 4, left(1), flipped)) < 0.5:
        raise RuntimeError("a flipped e10 sign left the kernel crossing in place")
    return "probe audit: signed overlap kernel-independent; cancellation kernel-specific; cocycle degree max(2, n)"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
        return 0
    text = json.dumps(audit(), indent=1, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    elif args.check.read_text(encoding="utf-8") != text:
        raise SystemExit(f"{args.check} differs from the re-derived audit")
    else:
        print(f"{args.check}: matches the re-derived audit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
