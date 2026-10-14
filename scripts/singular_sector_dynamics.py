"""Singular sectors of two-term Cayley-Dickson elements and the dynamics they fix.

For distinct imaginary basis units e_i, e_j of the 2^n-dimensional algebra
(cd_core.cd_sign, D = 2^n >= 8), t = +-1 and a = e_i + t e_j, put
P = L_i L_j. Every claim below is recomputed here; integer matrices keep the
algebra exact, and the dynamics checks use Hermitian eigendecompositions at
tolerance TOL:

1. Sector split, every D. L_i and L_j are signed permutations with
   L^T = -L and L^2 = -I, so P^2 is a diagonal sign and R^D = S+ (+) S-
   splits into coordinate subspaces. L_i and L_j commute with P^2, commute
   with each other on S+ and anticommute on S-. On S+ the involution tP
   splits dark (tP = 1, L_a = 0) from bright (tP = -1, L_a^T L_a = 4I), each
   of dimension |S+|/2; on S-, L_a^T L_a = 2I. So L_a^T L_a has spectrum in
   {0, 2, 4} and nullity |S+|/2 for every two-term element of every algebra.
2. Census link. {L_i, L_j} e_k = -[(e_i, e_j, e_k) + (e_j, e_i, e_k)], so k
   lies in S+ exactly when omega(i, j, k) != omega(j, i, k). With census
   Theorem 3 (omega = -(-1)^l_W(a xor c) on a quasi-octonion plane W, -1 on
   an octonion plane) this is l_W(i xor j) = 1 for W = span(i, j, k): twelve
   of a quasi-octonion plane's 21 pairs, four k each. Hence
   sum over pairs of |S+| = 48 Q(D) = (D-2)(D-4)(D-8)/4. The doubling
   (a, b)(c, d) = (ac - conj(d) b, da + b conj(c)) makes |S+| double on low
   and high pairs and gives 2 (h - 4 - |S+_m(a, x)|) on a mixed pair
   (e_a, e_(h+x)), x outside {0, a}; so |S+| <= D - 8 with equality, the
   anticommuting pairs (S+ empty) satisfy c(D) = 2 c(D/2) + 3D/2 - 3 and
   number (3/2) D log2(D) - (9/4) D + 3, and the largest two-term nullity is
   D/2 - 4. All of this is checked through SECTOR_MAX_DIM. Nullity |S+|/2
   per pair, doubled for the two signs, reproduces every rank-nullity
   histogram in annihilator_strata.json.
3. Dilation. Imaginary a has L_a^T = -L_a, so the Hermitian dilation
   H_a = |0><1| (x) L_a + |1><0| (x) L_a^T equals (iY) (x) L_a and
   H_a^2 = I (x) L_a^T L_a. From |1>|v>, evolution under H_a / alpha for time s
   flips the block with probability
   sum_sigma ||Pi_sigma v||^2 sin^2(sigma s / alpha), sigma in {0, sqrt2, 2}.
   Its long-time mean from the maximally mixed algebra register is
   rank(L_a) / (2D): 3/8 at D = 16.
4. Product formula. With H_a = H_i + t H_j, one step
   exp(-i theta H_i) exp(-i theta t H_j) equals exp(-i theta H_a) on
   S+ (dark (+) bright) for every theta. On S- one step flips the block with
   probability sin^2(2 theta) / 2, so a single step flips
   sin^2(2 theta) <v| B^T B |v> / |v|^2 with B = L_a / 2, Design B's success
   probability. Repeated steps on S- follow
   sin^2(n phi) 2 cos^2(theta) / (1 + cos^2(theta)) with cos(phi) = cos^2(theta).
5. Amplitude amplification of Design B. The LCU block encoding U of
   B = L_a / 2 has singular values sigma / alpha in {0, 1/sqrt2, 1}, so the
   rounds U (Z_anc U^dagger Z_anc U)^k leave P(anc = 0) at 0, 1/2 and 1 for
   every k on the dark, S- and bright sectors of all 84 sedenion corpus
   elements. A PREP rotation off by eps from pi/4 encodes
   cos^2(beta) L_i + t sin^2(beta) L_j: dark leakage becomes
   sin^2(2 (2k+1) eps), bright stays 1, and S- follows
   sin^2((2k+1) arcsin(sqrt(cos^4 beta + sin^4 beta))).
6. Population flow. For Hermitian H and rho, the populations obey
   dp_x/dt = 2 sum_y Im(H_xy rho_yx); one unitary step gives
   p'_x = sum_{y,z} U_xy rho_yz conj(U_xz). The ripple walk has
   |U_xy|^2 = 1/16, so its depth-two distribution away from uniform is
   entirely the y != z interference term.
7. Operator boundary. (L_a L_b - L_ab) c = -(a, b, c) with
   (a, b, c) = (ab)c - a(bc), exact on integer elements of the sedenions.

   The echo arm U U^dagger U, with the same barriers and no Z, returns the
   round-0 probability whenever the compiled inverse undoes the error in U,
   as for a PREP angle; the two arms differ by virtual Z gates only. A
   conditional phase after every self-inverse CZ survives the inverse and
   moves amplified minus echo the other way.

--fake-backend writes the FakeFez transpilation cost and seeded Aer response
of the amplified dark probe and of the echo-matched contrast under injected
PREP and CZ-phase errors; --check-fake-backend FILE replays that record.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))
from cd_associator_defect_census import sign_array  # noqa: E402

from cd_core import cd_sign, sedenion_zero_divisor_corpus  # noqa: E402

TOL = 1e-10
STRATA = ROOT / "results" / "hw_estimate" / "annihilator_strata.json"
SECTOR_MAX_DIM = 512
MATRIX_MAX_DIM = 32
FAKE_SEEDS = {"transpiler": 7, "simulator": 11}
FAKE_SHOTS = 20000
FAKE_ROUNDS = (0, 1, 2)
FAKE_EPS = (0.0, 0.03, 0.06, 0.1)
FAKE_ECHO_SHOTS = 40000
FAKE_CZ_PHASES = (0.02, 0.05, 0.1)
Y = np.array([[0, -1j], [1j, 0]])


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def basis_matrix(dim: int, m: int) -> np.ndarray:
    """L_{e_m} as an integer signed permutation: L e_k = cd_sign(dim, m, k) e_{m xor k}."""
    matrix = np.zeros((dim, dim), dtype=np.int64)
    for k in range(dim):
        matrix[m ^ k, k] = cd_sign(dim, m, k)
    return matrix


def element_matrix(dim: int, coefficients: dict[int, int]) -> np.ndarray:
    return sum((c * basis_matrix(dim, m) for m, c in coefficients.items()), np.zeros((dim, dim), dtype=np.int64))


def vector_matrix(dim: int, x: np.ndarray) -> np.ndarray:
    return element_matrix(dim, {m: int(c) for m, c in enumerate(x) if c})


def multiply(dim: int, x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Exact product of integer coefficient vectors from the basis sign table."""
    out = np.zeros(dim, dtype=np.int64)
    for p in np.flatnonzero(x):
        for q in np.flatnonzero(y):
            out[p ^ q] += cd_sign(dim, int(p), int(q)) * x[p] * y[q]
    return out


def sectors(dim: int, i: int, j: int, t: int) -> dict[str, np.ndarray]:
    """Scaled integer projectors 2 Pi_S+, 2 Pi_S-, 4 Pi_dark, 4 Pi_bright of a = e_i + t e_j."""
    eye = np.eye(dim, dtype=np.int64)
    p = basis_matrix(dim, i) @ basis_matrix(dim, j)
    square = p @ p
    require(np.array_equal(square, np.diag(np.diag(square))) and set(np.diag(square)) <= {-1, 1}, "P^2 is a sign")
    plus, minus = eye + square, eye - square
    return {"plus": plus, "minus": minus, "dark": plus @ (eye + t * p), "bright": plus @ (eye - t * p)}


def sector_split(max_dim: int) -> dict[str, int]:
    """Statement 1 on integer matrices for every pair and sign through max_dim."""
    checked = 0
    dim = 8
    while dim <= max_dim:
        eye = np.eye(dim, dtype=np.int64)
        units = [basis_matrix(dim, m) for m in range(dim)]
        for m in range(1, dim):
            u = units[m]
            require(np.array_equal(u.T, -u) and np.array_equal(u @ u, -eye), f"D={dim}: L_{m} skew involution")
        for i in range(1, dim):
            for j in range(i + 1, dim):
                li, lj = units[i], units[j]
                for t in (1, -1):
                    s = sectors(dim, i, j, t)
                    la = li + t * lj
                    gram = la.T @ la
                    plus_dim = int(np.trace(s["plus"])) // 2
                    for name, scale in (("plus", 2), ("minus", 2), ("dark", 4), ("bright", 4)):
                        q = s[name]
                        require(np.array_equal(q @ q, scale * q), f"D={dim} ({i},{j},{t}): {name} idempotent")
                        for op in (li, lj):
                            require(np.array_equal(op @ q, q @ op), f"D={dim} ({i},{j},{t}): {name} invariant")
                    require(np.array_equal((li @ lj - lj @ li) @ s["plus"], 0 * eye), f"D={dim}: commute on S+")
                    require(np.array_equal((li @ lj + lj @ li) @ s["minus"], 0 * eye), f"D={dim}: anticommute on S-")
                    require(np.array_equal(la @ s["dark"], 0 * eye), f"D={dim} ({i},{j},{t}): dark kernel")
                    require(np.array_equal(gram @ s["bright"], 4 * s["bright"]), f"D={dim}: bright Gram 4")
                    require(np.array_equal(gram @ s["minus"], 2 * s["minus"]), f"D={dim}: S- Gram 2")
                    require(int(np.trace(s["dark"])) == int(np.trace(s["bright"])) == 2 * plus_dim, "dark = bright")
                    require(np.linalg.matrix_rank(la) == dim - plus_dim // 2, f"D={dim}: nullity |S+|/2")
                    checked += 1
        dim *= 2
    return {"signed_pairs": checked}


def pair_sizes(dim: int, table: np.ndarray) -> dict[tuple[int, int], int]:
    """|S+| for every imaginary basis pair i < j, from a sign table."""
    k = np.arange(dim)
    sizes: dict[tuple[int, int], int] = {}
    for i in range(1, dim):
        js = np.arange(i + 1, dim)
        step = table[js][:, k] * table[i][js[:, None] ^ k[None, :]]
        shifted = np.take_along_axis(step, k[None, :] ^ (i ^ js)[:, None], axis=1)
        for j, n in zip(js, (step * shifted == 1).sum(axis=1), strict=True):
            sizes[(i, int(j))] = int(n)
    return sizes


def sector_sizes(dim: int, table: np.ndarray) -> Counter[int]:
    """Imaginary basis pairs counted by |S+|."""
    return Counter(pair_sizes(dim, table).values())


def size_recursion(max_dim: int) -> int:
    """Doubling recursion of |S+| from A_m (dimension h) to A_(m+1), and the bound |S+| <= D - 8.

    Low and high pairs double their sector because the anticommutator is
    block diagonal with {R_a, R_b} = C {L_a, L_b} C; the high pair through
    e_h anticommutes. A mixed pair (e_a, e_(h+x)) has an off-diagonal
    anticommutator built from [L_a, R_x] and [R_a, L_x], whose nonzero columns
    are the c with omega(a, c, x) = -1, so |S+| = 2 (h - 4 - |S+_m(a, x)|) for
    x outside {0, a} and 0 for x in {0, a}.
    """
    previous = pair_sizes(8, sign_table(8))
    require(max(previous.values()) == 0, "every octonion pair anticommutes")
    dim = 16
    while dim <= max_dim:
        half = dim // 2
        current = pair_sizes(dim, sign_table(dim))
        for (i, j), n in current.items():
            if j < half:
                expected = 2 * previous[(i, j)]
            elif i >= half:
                expected = 0 if i == half else 2 * previous[(i - half, j - half)]
            else:
                x = j - half
                expected = 0 if x in (0, i) else 2 * (half - 4 - previous[(min(i, x), max(i, x))])
            require(n == expected, f"D={dim} ({i},{j}): |S+| doubling recursion")
        require(max(current.values()) == dim - 8, f"D={dim}: largest |S+| is D - 8")
        previous = current
        dim *= 2
    return max_dim


def sign_table(dim: int) -> np.ndarray:
    grid = np.meshgrid(np.arange(dim), np.arange(dim), indexing="ij")
    return sign_array(dim, grid[0], grid[1]).astype(np.int64)


def census_link(max_dim: int) -> dict[int, dict[str, int]]:
    """Statement 2 from the vectorized sign table, with the omega criterion through MATRIX_MAX_DIM."""
    rows: dict[int, dict[str, int]] = {}
    damaged = sign_table(16)
    damaged[3, 12] *= -1
    require(sum(n * c for n, c in sector_sizes(16, damaged).items()) != 336, "one flipped sign moves the D=16 total")
    census = json.loads(STRATA.read_text(encoding="utf-8"))
    retained = {
        int(row["dimension"]): {
            int(h["nullity"]): int(h["signed_element_count"]) for h in row["rank_nullity_histogram"]
        }
        for row in census["dimensions"]
    }
    dim = 8
    while dim <= max_dim:
        n = dim.bit_length() - 1
        table = sign_table(dim)
        k = np.arange(dim)
        if dim <= MATRIX_MAX_DIM:
            for i in range(1, dim):
                for j in range(i + 1, dim):
                    p = basis_matrix(dim, i) @ basis_matrix(dim, j)
                    plus = np.diag(p @ p) == 1
                    omega_ij = table[i, j] * table[i ^ j][k] * table[j][k] * table[i][j ^ k]
                    omega_ji = table[j, i] * table[i ^ j][k] * table[i][k] * table[j][i ^ k]
                    require(np.array_equal(plus, omega_ij != omega_ji), f"D={dim} ({i},{j}): omega criterion")
        sizes = sector_sizes(dim, table)
        anticommuting, total = sizes.get(0, 0), sum(n * c for n, c in sizes.items())
        if dim in retained:
            predicted = {n // 2: 2 * c for n, c in sizes.items()}
            require(predicted == retained[dim], f"D={dim}: nullity |S+|/2 reproduces annihilator_strata.json")
        require(total == (dim - 2) * (dim - 4) * (dim - 8) // 4, f"D={dim}: sum |S+| = 48 Q(D)")
        require(anticommuting == (3 * dim * n) // 2 - (9 * dim) // 4 + 3, f"D={dim}: anticommuting pair count")
        rows[dim] = {"anticommuting_pairs": anticommuting, "sector_incidences": total}
        dim *= 2
    require(set(retained) <= set(rows), "every retained census dimension is compared")
    return rows


def evolve(hamiltonian: np.ndarray, time: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hamiltonian)
    out: np.ndarray = (vectors * np.exp(-1j * time * values)) @ vectors.conj().T
    return out


def flip(unitary: np.ndarray, v: np.ndarray) -> float:
    """Block-0 probability after unitary from |1>|v>, block qubit most significant."""
    dim = v.size
    state = unitary @ np.concatenate([np.zeros(dim), v / np.linalg.norm(v)])
    return float(np.sum(np.abs(state[:dim]) ** 2))


def dilation_and_steps() -> dict[str, object]:
    """Statements 3 and 4 on every sedenion corpus element."""
    dim, alpha = 16, 2
    rng = np.random.default_rng(20261013)
    up = np.array([[0, 1], [0, 0]])
    elements = sorted({(r[0], r[1], r[2]) for r in sedenion_zero_divisor_corpus()})
    require(len(elements) == 84, "84 corpus elements")
    times = (0.3, 0.7, math.pi / 4, 1.9)
    for i, j, t in elements:
        li, lj = basis_matrix(dim, i), basis_matrix(dim, j)
        la = li + t * lj
        h = np.kron(up, la) + np.kron(up.T, la.T)
        require(np.array_equal(h, np.kron(1j * Y, la).real) and np.allclose(np.kron(1j * Y, la).imag, 0), "(iY) x L")
        require(np.array_equal(h @ h, np.kron(np.eye(2, dtype=np.int64), la.T @ la)), "H^2 = I x L^T L")
        s = sectors(dim, i, j, t)
        pi = {name: s[name] / (2 if name in ("plus", "minus") else 4) for name in s}
        weights = {"dark": 0.0, "minus": math.sqrt(2), "bright": 2.0}
        hi, hj = np.kron(1j * Y, li), np.kron(1j * Y, t * lj)
        for time in times:
            exact = evolve(h / alpha, time)
            v = rng.normal(size=dim)
            predicted = sum(float(v @ pi[n] @ v) * math.sin(w * time / alpha) ** 2 for n, w in weights.items())
            require(abs(flip(exact, v) - predicted / float(v @ v)) < TOL, f"({i},{j},{t}): flip law at {time}")
            theta = time
            step = evolve(hi, theta) @ evolve(hj, theta)
            full = evolve(hi + hj, theta)
            outside = np.kron(np.eye(2), pi["plus"])
            require(np.allclose(step @ outside, full @ outside, atol=TOL), f"({i},{j},{t}): product exact on S+")
            inside = np.kron(np.eye(2), pi["minus"])
            require(not np.allclose(step @ inside, full @ inside, atol=1e-3), f"({i},{j},{t}): product inexact on S-")
            gram = (la.T @ la) / 4
            one_step = math.sin(2 * theta) ** 2 * float(v @ gram @ v) / float(v @ v)
            require(abs(flip(step, v) - one_step) < TOL, f"({i},{j},{t}): one step is Design B times sin^2(2 theta)")
            c2 = math.cos(theta) ** 2
            phi = math.acos(c2)
            w = pi["minus"] @ v
            power = np.eye(2 * dim, dtype=complex)
            for n in range(1, 7):
                power = step @ power
                law = math.sin(n * phi) ** 2 * 2 * c2 / (1 + c2)
                require(abs(flip(power, w) - law) < TOL, f"({i},{j},{t}): S- Floquet law n={n}")
        # Each oscillating sector averages sin^2 to 1/2, so the long-time mean of the
        # flip law from I/D is (dim S- + dim bright) / (2D), and that dimension is rank L_a.
        oscillating = int(np.trace(s["minus"])) // 2 + int(np.trace(s["bright"])) // 4
        require(oscillating == int(np.linalg.matrix_rank(la)), f"({i},{j},{t}): oscillating dimension = rank")
        require(Fraction(oscillating, 2 * dim) == Fraction(3, 8), f"({i},{j},{t}): long-time mean rank/(2D) = 3/8")
    return {"elements": len(elements), "times": len(times), "rank_meter_D16": "3/8"}


def lcu_circuit(i: int, j: int, t: int, beta: float) -> Any:
    """Design B's block encoding with PREP angle beta: <0|U|0> = cos^2(beta) L_i + t sin^2(beta) L_j."""
    from qiskit import QuantumCircuit

    from select_lcu import select_circuit

    circuit = QuantumCircuit(5)
    circuit.ry(2 * beta, 4)
    if t < 0:
        circuit.z(4)
    circuit.compose(select_circuit(16, i, j), range(5), inplace=True)
    circuit.ry(-2 * beta, 4)
    return circuit


def amplification_unitary(i: int, j: int, t: int, beta: float) -> np.ndarray:
    from qiskit.quantum_info import Operator

    return np.asarray(Operator(lcu_circuit(i, j, t, beta)).data)


def amplification() -> dict[str, int]:
    """Statement 5 on all 84 corpus elements, rounds 0 through 3."""
    dim = 16
    z_anc = np.kron(np.diag([1.0, -1.0]), np.eye(dim))
    elements = sorted({(r[0], r[1], r[2]) for r in sedenion_zero_divisor_corpus()})
    rng = np.random.default_rng(20261014)
    eps = 0.02
    checked = 0
    for i, j, t in elements:
        s = sectors(dim, i, j, t)
        for beta, kind in ((math.pi / 4, "ideal"), (math.pi / 4 + eps, "prep")):
            u = amplification_unitary(i, j, t, beta)
            block = u[:dim, :dim]
            target = math.cos(beta) ** 2 * basis_matrix(dim, i) + t * math.sin(beta) ** 2 * basis_matrix(dim, j)
            require(np.allclose(block, target, atol=TOL), f"({i},{j},{t}): block encoding at beta={beta}")
            c4s4 = math.cos(beta) ** 4 + math.sin(beta) ** 4
            angles = {
                "dark": abs(2 * (beta - math.pi / 4)),
                "minus": math.asin(math.sqrt(c4s4)),
                "bright": math.pi / 2,
            }
            for name, angle in angles.items():
                v = s[name] @ rng.normal(size=dim)
                initial = np.concatenate([v / np.linalg.norm(v), np.zeros(dim)]).astype(complex)
                echo = u @ (u.conj().T @ (u @ initial))
                require(abs(float(np.sum(np.abs(echo[:dim]) ** 2)) - math.sin(angle) ** 2) < 1e-9, "echo arm = round 0")
                state = u @ initial
                for k in range(4):
                    expected = math.sin((2 * k + 1) * angle) ** 2
                    got = float(np.sum(np.abs(state[:dim]) ** 2))
                    require(abs(got - expected) < 1e-9, f"({i},{j},{t}) {kind} {name}: P_{k}")
                    if kind == "ideal":
                        require(abs(got - {"dark": 0.0, "minus": 0.5, "bright": 1.0}[name]) < 1e-9, "frozen")
                    state = u @ (z_anc @ (u.conj().T @ (z_anc @ state)))
                    checked += 1
    return {"probabilities": checked}


def population_flow() -> dict[str, float]:
    """Statement 6: continuous identity on random Hermitian pairs, discrete split on the ripple walk."""
    from qiskit.quantum_info import Operator

    from ripple_dynamics import PAIRS, walk_circuit

    rng = np.random.default_rng(7)
    for _ in range(8):
        a = rng.normal(size=(8, 8)) + 1j * rng.normal(size=(8, 8))
        h = a + a.conj().T
        b = rng.normal(size=(8, 8)) + 1j * rng.normal(size=(8, 8))
        rho = b @ b.conj().T
        rho /= np.trace(rho)
        commutator = np.real(np.diag(-1j * (h @ rho - rho @ h)))
        flow = 2 * np.array([sum(np.imag(h[x, y] * rho[y, x]) for y in range(8)) for x in range(8)])
        require(np.allclose(commutator, flow, atol=TOL), "dp/dt = 2 sum Im(H_xy rho_yx)")
    largest = 0.0
    for pair in PAIRS:
        u = np.asarray(Operator(walk_circuit(pair, 1)).data)
        require(np.allclose(np.abs(u) ** 2, 1 / 16, atol=TOL), f"{pair}: |U_xy|^2 = 1/16")
        psi = u[:, 0]
        rho = np.outer(psi, psi.conj())
        total = np.real(np.diag(u @ rho @ u.conj().T))
        classical = (np.abs(u) ** 2) @ np.real(np.diag(rho))
        require(np.allclose(classical, 1 / 16, atol=TOL), f"{pair}: incoherent part uniform")
        largest = max(largest, float(np.max(np.abs(total - classical))))
        require(np.allclose(total, np.abs((u @ u)[:, 0]) ** 2, atol=TOL), f"{pair}: depth-two distribution")
    require(largest > 0.1, "the walk distribution departs from uniform through interference")
    return {"largest_interference_shift": largest}


def operator_boundary() -> dict[str, int]:
    """Statement 7 on seeded integer sedenions."""
    dim = 16
    rng = np.random.default_rng(3)
    for _ in range(40):
        a, b, c = (rng.integers(-3, 4, size=dim) for _ in range(3))
        lhs = vector_matrix(dim, a) @ (vector_matrix(dim, b) @ c) - vector_matrix(dim, multiply(dim, a, b)) @ c
        associator = multiply(dim, multiply(dim, a, b), c) - multiply(dim, a, multiply(dim, b, c))
        require(np.array_equal(lhs, -associator), "(L_a L_b - L_ab) c = -(a, b, c)")
    return {"triples": 40}


def gpt_example() -> None:
    """The review's sedenion example in this repository's convention."""
    la = element_matrix(16, {1: 1, 10: 1})
    minus = np.zeros(16, dtype=np.int64)
    minus[[4, 15]] = (1, -1)
    plus = np.abs(minus)
    require(not (la @ minus).any(), "L_a (e4 - e15) = 0")
    require(np.array_equal(la.T @ la @ plus, 4 * plus), "L_a^T L_a (e4 + e15) = 4 (e4 + e15)")


def fake_backend_record() -> dict[str, Any]:
    """Transpiled cost and seeded noisy response of the amplified dark probe on FakeFez."""
    import qiskit
    import qiskit_aer
    import qiskit_ibm_runtime
    from qiskit import QuantumCircuit, transpile
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel, coherent_unitary_error
    from qiskit_ibm_runtime.fake_provider import FakeFez

    from select_lcu import select_circuit, sparse_pair_prep

    u = QuantumCircuit(5)
    u.h(4)
    u.compose(select_circuit(16, 1, 10), range(5), inplace=True)
    u.h(4)
    backend = FakeFez()
    # One thread fixes Aer's shot partition, so the seeded counts replay on any runner.
    simulator = AerSimulator.from_backend(
        backend, max_parallel_threads=1, max_parallel_experiments=1, max_parallel_shots=1
    )
    rows = []
    for rounds in FAKE_ROUNDS:
        circuit = QuantumCircuit(5, 1)
        circuit.compose(sparse_pair_prep(4, 4, 15, math.pi), range(4), inplace=True)
        circuit.compose(u, inplace=True)
        for _ in range(rounds):
            circuit.z(4)
            circuit.compose(u.inverse(), inplace=True)
            circuit.z(4)
            circuit.compose(u, inplace=True)
        circuit.measure(4, 0)
        compiled = transpile(circuit, backend, optimization_level=3, seed_transpiler=FAKE_SEEDS["transpiler"])
        counts = simulator.run(compiled, shots=FAKE_SHOTS, seed_simulator=FAKE_SEEDS["simulator"]).result().get_counts()
        rows.append(
            {
                "rounds": rounds,
                "two_qubit_gates": int(compiled.count_ops().get("cz", 0)),
                "depth": int(compiled.depth()),
                "ideal_p_anc0": 0.0,
                "noisy_p_anc0": counts.get("0", 0) / FAKE_SHOTS,
            }
        )

    def echo_pair(lcu: Any) -> dict[str, Any]:
        """Amplified U Z U^dagger Z U and echo U U^dagger U, compiled, with matched physical content."""
        compiled = {}
        for arm in ("amplified", "echo"):
            circuit = QuantumCircuit(5, 1)
            circuit.compose(sparse_pair_prep(4, 4, 15, math.pi), range(4), inplace=True)
            circuit.compose(lcu, inplace=True)
            circuit.barrier()
            if arm == "amplified":
                circuit.z(4)
            circuit.compose(lcu.inverse(), inplace=True)
            circuit.barrier()
            if arm == "amplified":
                circuit.z(4)
            circuit.compose(lcu, inplace=True)
            circuit.measure(4, 0)
            compiled[arm] = transpile(circuit, backend, optimization_level=3, seed_transpiler=FAKE_SEEDS["transpiler"])
        ops = {arm: {k: v for k, v in c.count_ops().items() if k != "rz"} for arm, c in compiled.items()}
        require(ops["amplified"] == ops["echo"], "the arms share every non-virtual gate")
        durations = {arm: c.estimate_duration(backend.target) for arm, c in compiled.items()}
        require(durations["amplified"] == durations["echo"], "the arms share their scheduled duration")
        return compiled

    def p_anc0(sim: Any, circuit: Any) -> float:
        counts = sim.run(circuit, shots=FAKE_ECHO_SHOTS, seed_simulator=FAKE_SEEDS["simulator"]).result().get_counts()
        return float(counts.get("0", 0) / FAKE_ECHO_SHOTS)

    echo_rows = []
    for eps in FAKE_EPS:
        compiled = echo_pair(lcu_circuit(1, 10, 1, math.pi / 4 + eps))
        amplified, echo = (p_anc0(simulator, compiled[arm]) for arm in ("amplified", "echo"))
        echo_rows.append(
            {
                "prep_error_rad": eps,
                "two_qubit_gates": int(compiled["echo"].count_ops().get("cz", 0)),
                "duration_dt": int(compiled["echo"].estimate_duration(backend.target, unit="dt")),
                "amplified_p_anc0": amplified,
                "echo_p_anc0": echo,
                "difference": round(amplified - echo, 6),
                "ideal_difference": round(math.sin(6 * eps) ** 2 - math.sin(2 * eps) ** 2, 6),
                "echo_normalized_difference": round((amplified - echo) / (1 - 2 * echo), 6),
            }
        )
    # CZ is self-inverse, so a conditional phase after every CZ enters U and U^dagger with
    # the same sign and survives the echo; the composed noise model keeps FakeFez's errors.
    compiled = echo_pair(lcu_circuit(1, 10, 1, math.pi / 4))
    pairs = sorted(
        {
            tuple(c.find_bit(q).index for q in inst.qubits)
            for c in compiled.values()
            for inst in c.data
            if inst.operation.name == "cz"
        }
    )
    cz_rows = []
    for delta in FAKE_CZ_PHASES:
        error = coherent_unitary_error(np.diag([1, 1, 1, np.exp(1j * delta)]))
        row: dict[str, float] = {"cz_phase_rad": delta}
        for label, model in (
            ("coherent_only", NoiseModel(basis_gates=["cz", "rz", "sx", "x"])),
            ("fakefez", NoiseModel.from_backend(backend)),
        ):
            for pair in pairs:
                model.add_quantum_error(error, "cz", list(pair), warnings=False)
            sim = AerSimulator(
                noise_model=model, max_parallel_threads=1, max_parallel_experiments=1, max_parallel_shots=1
            )
            amplified, echo = (p_anc0(sim, compiled[arm]) for arm in ("amplified", "echo"))
            row.update(
                {
                    f"{label}_amplified": amplified,
                    f"{label}_echo": echo,
                    f"{label}_difference": round(amplified - echo, 6),
                }
            )
        cz_rows.append(row)
    return {
        "cz_phase_rows": cz_rows,
        "echo_shots": FAKE_ECHO_SHOTS,
        "echo_rows": echo_rows,
        "element": "e1 + e10",
        "input": "(e4 - e15)/sqrt2, the dark partner",
        "backend": "FakeFez",
        "optimization_level": 3,
        "seeds": FAKE_SEEDS,
        "shots": FAKE_SHOTS,
        "versions": {
            "qiskit": qiskit.__version__,
            "qiskit_aer": qiskit_aer.__version__,
            "qiskit_ibm_runtime": qiskit_ibm_runtime.__version__,
        },
        "rows": rows,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--fake-backend", type=Path, help="write the FakeFez cost and response record")
    parser.add_argument("--check-fake-backend", type=Path, help="replay a retained FakeFez record")
    args = parser.parse_args(argv)
    if args.fake_backend or args.check_fake_backend:
        record = fake_backend_record()
        if args.fake_backend:
            args.fake_backend.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        if args.check_fake_backend:
            retained = json.loads(args.check_fake_backend.read_text(encoding="utf-8"))
            require(retained == record, "FakeFez record differs from the replay")
        print(json.dumps(record["rows"]))
        print(json.dumps(record["echo_rows"]))
        print(json.dumps(record["cz_phase_rows"]))
        return 0
    gpt_example()
    split = sector_split(MATRIX_MAX_DIM)
    link = census_link(SECTOR_MAX_DIM)
    size_recursion(SECTOR_MAX_DIM)
    dynamics = dilation_and_steps()
    rounds = amplification()
    flow = population_flow()
    boundary = operator_boundary()
    print(
        f"singular sectors: {split['signed_pairs']} signed pairs through D={MATRIX_MAX_DIM}; "
        f"census link through D={SECTOR_MAX_DIM} {json.dumps(link)}; dilation on {dynamics['elements']} elements; "
        f"{rounds['probabilities']} amplification probabilities; interference shift "
        f"{flow['largest_interference_shift']:.4f}; {boundary['triples']} associator triples"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
