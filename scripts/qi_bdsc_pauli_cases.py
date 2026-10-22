"""Tuna-17 case builder for the BDSC target effect read as a four-qubit local Pauli sum.

The target effect E0 = I/2 - YIXY/4 + YZXY/4 of docs/notes/topics/bdsc-pauli-readout.md is
diagonal in one product basis (Y on q3, Z on q2, X on q1, Y on q0). With signs z2 and
t = y3 x1 y0 of the measured eigenvalues, the score g is 1/2 for z2 = +1 and (1 - t)/2 for
z2 = -1; its mean is Tr(E0 rho) and the table of scores is the `target.readout.scores` list of
docs/evidence/bdsc/pauli/pauli_form.json. docs/design/bdsc-tuna17-pauli-pilot.md fixes the
design this script builds: a twelve-state bank whose ideal scores are 0, 1/2 and 1, three disjoint
patches of Tuna-17, a group-balanced layout, bracketing readout references and a quadrature batch.

Patch. Logical qubits (q3, q2, q1, q0) sit on four physical qubits. (q3, q1, q0) is a connected
path with q1 in the middle, carrying a GHZ-type pair (|a> + s|~a>)/sqrt2 prepared by H on q3,
CNOT q3 -> q1 and CNOT q1 -> q0 (each CNOT is H CZ H on the target), then X and Z corrections;
q2 holds a definite Z state and needs no coupler. Every gate is Clifford and lies on Tuna's
5 degree grid. The readout uses the native pulses of the cQASM v3 standard gate set: X90 puts the
Y eigenbasis of q3 and q0 on Z and mY90 does the same for the X eigenbasis of q1 (the quadrature
circuits read q3 with mY90). q2 is left in Z.

Placement. PLACEMENT is the first entry of select_placement(): the disjoint triples of patches
over the qubits outside excluded_qubits() of scripts/qi_zero_divisor_cases.py, ranked by the
number of paths holding both q11 and q13 (their readout context is established), then the
couplers joining one patch's path to another patch's path, then the couplers from a q2 qubit to
another patch's path, then the lexicographically least placement.

Witness layout. Let H be the middle or sector slot. The six assignments of (kernel, bright, H) to
the three patches form three swap pairs that differ by exchanging kernel and bright. One batch
holds one swap pair on two patches (a, b) and H on the third (m): circuit 1 puts k_na on a, b_nb on
b and an H state on m; circuit 2 puts b_na on a, k_nb on b and the other H state. Kernel and bright
partners of one index therefore share a batch, its readout references and its neighbor activity.
WITNESS_PLAN uses each swap pair twice, so all six assignments occur twice, every kernel and bright
state meets every patch once and every middle and sector state meets every patch once. balance_tables()
counts group x patch x ordered neighbor groups and raises on any unequal count; build() writes the
counts to cases.json.

Series. Nine batches of at most three circuits: batch-00 holds readout-0, readout-1 and the first
checkerboard reference before any witness; six witness batches follow, each with one reference, and
two quadrature batches sit between them. Each quadrature batch holds one of k1 and b1 read with q3 in X
(quadrature) and in Y (cosine), the same state on every patch, so the sine and cosine amplitudes of the
branch phase share their visibility, neighbor activity and calibration window; the e7 null and a
reference fill the third slots. Readout-1 flips only the patch qubits, so idle
spectators stay in |0> as in the witnesses. The coupling graph of the patch qubits is bipartite and
the two checkerboard references flip one part each, so with readout-0 and readout-1 every coupled
pair meets all four joint preparations. A witness is corrected with the nearest readout-0 and
readout-1 (the earlier batch on a tie); cases.json records the pairing. Every circuit measures all
qubits of its device, and bit strings put qubit 0 at the rightmost character.

QX twin. The remote emulator takes 10 qubits, so bdsc_pauli_qx packs two patches per circuit on
qubits 0-3 and 4-7 with the gate sequence of the Tuna patch, relabeled; build() requires that
equality. The twin is a noiseless control of the plumbing and the analysis.

Before emitting, build() checks each state's preparation circuit with a Qiskit Statevector against
its target vector, the emitted cQASM text of every circuit against the ideal score or parity of each
state it holds, the native readout pulses against their spec matrices, and the reference sets
against the coupling graph.

--select-placement prints the ranking without writing. --write DIR writes DIR/bdsc_pauli_tuna_17/
and DIR/bdsc_pauli_qx/ (batch-NN/ cases and a series cases.json); --check DIR regenerates both and
compares bytes and file sets. --analyze RUN_DIR... [--out FILE] writes the preregistered analysis
of the raw shots of every batch of one series; --replay compares FILE with the recomputation
instead of writing it. --references RUN_DIR... reports the assignment
references, the batch-00 stop test, the bracket drift and the neighbor-conditioned assignment of the
batches loaded so far, and exits 1 when a stop fired. --submit-next SERIES_DIR copies the next batch
of a case series into its run directory and submits it through qi_platform.submit only after every
preregistered stop of the batches before it is clear, every one is collected with full shot lists,
the QX twin's control verdict passes (Tuna-17), and the live backend's topology, gate set and compiler
configuration match the digests in the cases; --dry prints the receipt and sends nothing.
--self-test runs ideal, depolarized, readout-biased, coherent-error, branch-phase, matched-visibility,
unresolved-phase, drift, breach and context synthetic series through the analysis and the gate's
refusals offline.

Usage: "$PYTHON" scripts/qi_bdsc_pauli_cases.py
       (--select-placement | --write DIR | --check DIR | --analyze RUN_DIR... [--out FILE] [--replay]
        | --references RUN_DIR... | --submit-next SERIES_DIR [--approval QUOTE] [--control FILE]
          [--runs DIR] [--dry] | --self-test)
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from collections import Counter
from collections.abc import Callable
from functools import cache
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import bdsc_pauli  # noqa: E402
from qi_platform import HARDWARE_BATCH_CIRCUITS, HARDWARE_PAUSE_LADDER  # noqa: E402
from qi_zero_divisor_cases import (  # noqa: E402
    BACKEND,
    NQUBITS,
    QX_QUBITS,
    QX_SHOTS,
    TUNA17,
    analysis_claim_kind,
    catalogue_check,
    excluded_qubits,
    header,
    load_series,
    wilson,
)

import bdsc  # noqa: E402
import parallel  # noqa: E402

PAULI_FORM = ROOT / "docs/evidence/bdsc/pauli/pauli_form.json"
SERIES = "bdsc_pauli_tuna_17"
TWIN_SERIES = "bdsc_pauli_qx"
QX_BACKEND = "QXsinglenodesimulator"
SHOTS = 32768
PATCHES = 3
READOUT_STOP = 0.15
DRIFT_STOP = 0.02
Z_FLAG = 3.0
ALPHA = 0.05
Z_95 = 1.959963984540054
JOB_FIXED_SECONDS = 2.6
JOB_SECONDS_PER_SHOT = 0.00053
BOOTSTRAP_DRAWS = 4000
BOOTSTRAP_SEED = 20261022
# Jeffreys prior weight per outcome: a Dirichlet(counts + 1/2) draw keeps an unobserved outcome's
# probability positive, so a cell or reference with every shot in one outcome still has an interval.
JEFFREYS = 0.5
SINGULAR_DET = 1e-6
# Chi-square with 2 degrees of freedom at the two-sided 3-sigma tail (p = 0.0027): the (S, C) amplitude
# must reject zero at this level before the branch phase is defined.
VISIBILITY_CHI2 = -2 * math.log(0.0027)
# Primary endpoints: the chi-square of each patch's kernel + bright - 1 pair residuals and the branch phase
# of each patch, six tests at the two-sided 3-sigma tail p = 0.0027, family-wise error at most
# 6 x 0.0027 = 0.016 by Bonferroni; every other statistic is exploratory. The chi-square sums the pairs'
# squared z values, so residuals of opposite sign, which a coherent error produces and the pooled mean
# cancels, still add.
PRIMARY_TESTS = 6
PRIMARY_P = 0.0027
CONTRACT_FIELDS = ("topology", "gateset", "default_compiler_config")
# Patch (q3, q1, q0, q2) of physical qubits; the three patches use all twelve qubits outside
# excluded_qubits(), with q3 (isolated once q5 and q6 are excluded) as a q2 qubit.
PLACEMENT = ((1, 4, 2, 3), (8, 11, 14, 13), (12, 15, 16, 10))
GROUP_IDEAL = {"kernel": 0.0, "bright": 1.0, "middle": 0.5, "sector": 0.5}
CQASM = {"h": "H", "x": "X", "z": "Z", "x90": "X90", "my90": "mY90"}
# (patch holding the middle or sector slot, kernel index on the lower and on the higher other patch,
# state of that slot in circuit 1, state in circuit 2). Circuit 1 puts kernel on the lower other patch
# and bright on the higher one; circuit 2 exchanges them.
WITNESS_PLAN = (
    (2, 1, 3, "e0", "e7"),
    (1, 3, 1, "e0", "e7"),
    (0, 1, 3, "e0", "e7"),
    (2, 2, 4, "e12", "e10"),
    (1, 4, 2, "e12", "e10"),
    (0, 2, 4, "e12", "e10"),
)
QUADRATURE_STATES = ("k1", "b1", "e7")
READOUT_ZERO = "readout-0.cq"
READOUT_ONE = "readout-1.cq"
CHECKER_P = "checkerboard-p.cq"
CHECKER_Q = "checkerboard-q.cq"
PREREGISTERED = {
    "estimators": "Per state and patch the primary estimand is the raw score: its mean with an "
    "empirical-Bernstein 95% interval (Maurer-Pontil Theorem 4, range 1, unbiased sample variance, two-sided) "
    "and the kernel-outcome fraction (z2 = -1 and t = +1) with a Wilson 95% interval. The tensor-model "
    "mitigated score applies the inverse tensor product of the four single-qubit assignment matrices of the "
    "witness batch's nearest readout-0 and readout-1 (the earlier batch on a tie, the pairing in "
    "readout_pairing); it is an estimate under the model that each qubit's assignment is independent of the "
    "other qubits' states, and its 95% interval is conditional on that model. The interval is the percentile "
    f"interval of {BOOTSTRAP_DRAWS} seeded draws from the Jeffreys posterior: Dirichlet(counts + 1/2) over the "
    "16 witness outcomes and over the 16 joint outcomes of the patch qubits in each reference, so every rate "
    "keeps the covariance of the calibration shots and an outcome never observed keeps a positive weight. A "
    "cell whose patch holds a qubit with a neighbor-context flag in the references rejects that model, and "
    "its mitigated score is withheld.",
    "contraction": "A depolarizing contraction V of the (q3, q1, q0) parity gives kernel and bright states "
    "(1 - V)/2 and (1 + V)/2, so kernel + bright - 1 is consistent with zero for each partner pair "
    "(k_i, b_i) of a batch and pooled over the four pairs of a patch, and middle and sector states read "
    "1/2. A chi-square of a patch's four pair residuals (sum of z^2, 4 dof) beyond its p = 0.0027 quantile "
    "rejects the stationary contraction-plus-readout model on that patch; "
    "an entangling coherent error, leakage, drift within the series and context-dependent readout each "
    "produce one, and the test does not tell them apart. The law is blind to a phase between the two GHZ "
    "branches (kernel and bright scores move by (1 -+ cos phi) V/2 and still sum to one), to single-qubit "
    "coherent errors and to readout bias. Each z divides the raw residual by the square root of the summed "
    "sample variances over shots.",
    "quadrature": "A GHZ pair (|a> + s e^{i phi}|~a>)/sqrt2 with a3 = 0, a0 = 1 gives <X3 X1 Y0> = -s sin(phi) V "
    "with q3 read in X and <Y3 X1 Y0> = s cos(phi) V with q3 read in Y. The quadrature batches hold, for k1 and "
    "for b1, one X-basis and one Y-basis circuit in the same batch with the same state on every patch, so the "
    "sine and cosine amplitudes S = (m_b1x - m_k1x)/2 and C = (m_k1y - m_b1y)/2 carry the same visibility, "
    "neighbor activity and calibration window. phi = atan2(S, C) and V = hypot(S, C); the phase is reported "
    f"only when S^2/var(S) + C^2/var(C) >= {VISIBILITY_CHI2:.2f} (2-dof chi-square at p = 0.0027), and is "
    "otherwise withheld as unidentified. This is a repository-derived fixed-quadrature estimator from two "
    "fixed bases, not the phase scan of GHZ parity-oscillation or multiple-quantum-coherence practice. "
    "(m_k1 + m_b1)/2 of both bases and the e7 parity are null statistics, and the cosine amplitude of the "
    "witness circuits minus the matched C measures how far neighbor context moves the visibility.",
    "pooling": "Patches are analyzed separately; the pooled value is the equal-weight mean over the "
    "three patches of the per-patch pooled kernel + bright - 1.",
    "multiplicity": f"The primary family is the pair chi-square of each patch and the branch phase of each "
    f"patch: {PRIMARY_TESTS} tests at p = {PRIMARY_P} (|z| >= {Z_FLAG} for the phase), family-wise error at "
    "most 0.016 by Bonferroni. Single pair residuals, the per-patch and equal-weight pooled means, middle "
    "and sector residuals, the nulls and the neighbor-context shifts are exploratory and carry no claim.",
    "stop_conditions": f"Batch 0's readout-0 or readout-1 shows a patch qubit with P(1|0) or P(0|1) above "
    f"{READOUT_STOP}: stop and redraw the placement. Two successive readout-0 circuits move a patch qubit's "
    f"P(1|0), or two successive readout-1 circuits move its P(0|1), by more than {DRIFT_STOP}: stop. "
    "A job fails or returns fewer shots than requested. The QX control misses its ideal. The account-wide "
    "pause or the three-circuit limit would be broken. --submit-next enforces every stop before it sends "
    "a batch, and a stopped analysis emits operational diagnostics only.",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


# --- native pulses ------------------------------------------------------------------------------

PAULI_MATRIX = bdsc_pauli.PAULI
# cQASM v3 standard gate set, docs/notes/quantum_inspire/cqasm-spec/standard_gate_set/single_qubit/:
# sq_X90.md and sq_mY90.md state the operator matrices; the same pages give the R_n forms below.
X90 = np.array([[1 + 1j, 1 - 1j], [1 - 1j, 1 + 1j]]) / 2
MY90 = np.array([[1 - 1j, 1 - 1j], [-1 + 1j, 1 - 1j]]) / 2
GATE_MATRIX = {"x90": X90, "my90": MY90, **{k: v for k, v in bdsc_pauli.GATES.items() if k == "h"}}
# Native pulse that maps the eigenbasis of a Pauli onto Z.
ROTATION_GATE = {"Y": "x90", "X": "my90"}
WITNESS_BASIS = {3: "Y", 2: "Z", 1: "X", 0: "Y"}
QUADRATURE_BASIS = {3: "X", 2: "Z", 1: "X", 0: "Y"}


def rn_form(axis: str, theta: float, phase: float) -> np.ndarray:
    """e^{i phase} e^{-i theta sigma/2}, the R_n canonical form of the cQASM spec."""
    return np.exp(1j * phase) * (np.cos(theta / 2) * np.eye(2) - 1j * np.sin(theta / 2) * PAULI_MATRIX[axis])


def native_rotation_check() -> dict[str, Any]:
    """Spec matrices agree with the spec's R_n forms, and U P U^dagger = Z for each pulse; raises otherwise."""
    forms = {"x90": ("X", math.pi / 2, math.pi / 4), "my90": ("Y", -math.pi / 2, -math.pi / 4)}
    out: dict[str, Any] = {}
    for letter, gate in ROTATION_GATE.items():
        u = GATE_MATRIX[gate]
        axis, theta, phase = forms[gate]
        require(np.allclose(u, rn_form(axis, theta, phase), atol=1e-14), f"{gate} differs from its R_n form")
        require(np.allclose(u @ u.conj().T, np.eye(2), atol=1e-14), f"{gate} is not unitary")
        rotated = u @ PAULI_MATRIX[letter] @ u.conj().T
        require(np.allclose(rotated, PAULI_MATRIX["Z"], atol=1e-14), f"{gate} P {gate}^dagger is not Z for {letter}")
        out[gate] = {"maps_pauli_to_z": letter, "spec_matrix_equals_rn_form": True}
    return out


def readout_ops(basis: dict[int, str]) -> list[tuple[str, tuple[int, ...]]]:
    return [(ROTATION_GATE[basis[q]], (q,)) for q in (3, 1, 0) if basis[q] in ROTATION_GATE]


READOUT_OPS = readout_ops(WITNESS_BASIS)
QUADRATURE_OPS = readout_ops(QUADRATURE_BASIS)


# --- bank -----------------------------------------------------------------------------------


def bank() -> list[dict[str, Any]]:
    """The twelve states: kernel, bright, middle, sector, as {index: coefficient} vectors over e_0..e_15."""
    out = []
    r = 1 / math.sqrt(2)
    for group, sign in (("kernel", 1), ("bright", -1)):
        for n, (a, b, s) in enumerate(bdsc.KERNEL_PAIRS, start=1):
            out.append({"name": f"{group[0]}{n}", "group": group, "terms": {a: r, b: sign * s * r}})
    for name, group, index in (("e0", "middle", 0), ("e10", "middle", 10), ("e7", "sector", 7), ("e12", "sector", 12)):
        out.append({"name": name, "group": group, "terms": {index: 1.0}})
    return out


BANK = bank()
ENTRY = {e["name"]: e for e in BANK}


def state_vector(entry: dict[str, Any]) -> np.ndarray:
    v = np.zeros(bdsc_pauli.DIM, dtype=complex)
    for index, coefficient in entry["terms"].items():
        v[index] = coefficient
    return v


def prep_ops(entry: dict[str, Any]) -> list[tuple[str, tuple[int, ...]]]:
    """Clifford preparation of a bank state on logical qubits 0..3, gates h, x, z, cz.

    A basis state takes X on its set bits. A pair (e_a + s e_b)/sqrt2 has b the complement of a on
    (q3, q1, q0) with q2 shared and bit 3 of a clear: X on q2 when set, the GHZ ladder, X on q1 and q0
    where a is set, and Z on q3 for s = -1.
    """
    terms = entry["terms"]
    if len(terms) == 1:
        (index,) = terms
        return [("x", (b,)) for b in range(4) if index >> b & 1]
    (a, ca), (b, cb) = sorted(terms.items())
    require(a >> 3 == 0 and (a ^ b) == 0b1011 and abs(ca) == abs(cb), f"{entry['name']}: not a complement pair")
    ops: list[tuple[str, tuple[int, ...]]] = []
    if a >> 2 & 1:
        ops.append(("x", (2,)))
    ops += [("h", (3,))]
    for control, target in ((3, 1), (1, 0)):
        ops += [("h", (target,)), ("cz", (control, target)), ("h", (target,))]
    ops += [("x", (q,)) for q in (1, 0) if a >> q & 1]
    if ca * cb < 0:
        ops.append(("z", (3,)))
    return ops


def score_vector() -> np.ndarray:
    """g[code], code = y3 << 3 | z2 << 2 | x1 << 1 | y0 with bit 1 meaning eigenvalue -1, from pauli_form.json."""
    scores = json.loads(PAULI_FORM.read_text(encoding="utf-8"))["target"]["readout"]["scores"]
    require(len(scores) == 16, f"{PAULI_FORM} lists {len(scores)} scores")
    g = np.zeros(16)
    for row in scores:
        code = sum((1 - sign) // 2 << (3 - n) for n, sign in enumerate(row["signs_q3q2q1q0"]))
        num, _, den = row["score"].partition("/")
        g[code] = int(num) / int(den or 1)
    return g


def parity_vector() -> np.ndarray:
    """t[code] = y3 x1 y0 of the outcome code (the z2 bit does not enter)."""
    return np.array(
        [float((1 - 2 * (c >> 3 & 1)) * (1 - 2 * (c >> 1 & 1)) * (1 - 2 * (c & 1))) for c in range(16)], dtype=float
    )


def readout_unitary(basis: dict[int, str] | None = None) -> np.ndarray:
    """Readout rotation of logical qubits (q3, q2, q1, q0) in the kron order of bdsc_pauli.word_matrix."""
    basis = basis or WITNESS_BASIS
    one = np.eye(2, dtype=complex)
    factors = [GATE_MATRIX[ROTATION_GATE[basis[q]]] if basis[q] in ROTATION_GATE else one for q in (3, 2, 1, 0)]
    return np.kron(np.kron(np.kron(factors[0], factors[1]), factors[2]), factors[3])


def outcome_distribution(psi: np.ndarray, basis: dict[int, str] | None = None) -> np.ndarray:
    """P(code) of the readout of the logical state psi (index j = 8 j3 + 4 j2 + 2 j1 + j0)."""
    return np.abs(readout_unitary(basis) @ psi) ** 2


def reference_unitary() -> np.ndarray:
    """The Sdag-then-H and H rotations of pauli_form.json, whose outcome probabilities the native pulses reproduce."""
    one = np.eye(2, dtype=complex)

    def rot(letter: str) -> np.ndarray:
        u = one
        for gate in bdsc_pauli.ROTATIONS[letter]:
            u = bdsc_pauli.GATES[gate] @ u
        return u

    return np.kron(np.kron(np.kron(rot("Y"), one), rot("X")), rot("Y"))


def ideal_scores() -> dict[str, float]:
    """Ideal score of each bank state, checked against <psi|E0|psi>, the group value and the pauli_form readout."""
    g, effect = score_vector(), bdsc.ideal_effect()
    old = reference_unitary()
    out = {}
    for entry in BANK:
        psi = state_vector(entry)
        require(abs(np.linalg.norm(psi) - 1) < 1e-12, f"{entry['name']}: state is not normalized")
        expectation = float((psi.conj() @ effect @ psi).real)
        distribution = outcome_distribution(psi)
        by_outcome = float(g @ distribution)
        want = GROUP_IDEAL[entry["group"]]
        require(
            abs(expectation - want) < 1e-12 and abs(by_outcome - want) < 1e-12,
            f"{entry['name']}: <E0> {expectation}, readout score {by_outcome}, group value {want}",
        )
        require(
            np.allclose(distribution, np.abs(old @ psi) ** 2, atol=1e-12),
            f"{entry['name']}: native readout differs from the pauli_form.json rotations",
        )
        out[entry["name"]] = want
    return out


def quadrature_expectation(name: str) -> dict[str, float]:
    """Exact <Y3 X1 Y0> = cos_coefficient cos(phi) and <X3 X1 Y0> = sin_coefficient sin(phi) of a pair state.

    A pair (|a> + w e^{i phi}|~a>)/sqrt2 with a3 = 0 and the branch phase phi carried by the q3 = 1
    branch has <a|P|~a> = prod_j <a_j|sigma_j|~a_j> for P with no Z factor, and <P> = Re(w e^{i phi}
    <a|P|~a>). <1|Y|0> = i, <0|Y|1> = -i and <a|X|~a> = 1 give the two coefficients below; basis
    states read zero in both bases.
    """
    terms = ENTRY[name]["terms"]
    if len(terms) == 1:
        return {"cos_coefficient": 0.0, "sin_coefficient": 0.0}
    (a, ca), (_, cb) = sorted(terms.items())
    w = cb / ca
    a3, a0 = a >> 3 & 1, a & 1
    return {
        "cos_coefficient": -w * (2 * a3 - 1) * (2 * a0 - 1),
        "sin_coefficient": -w * (2 * a0 - 1),
    }


# --- placement --------------------------------------------------------------------------------


def adjacency(topology: tuple[tuple[int, int], ...]) -> dict[int, set[int]]:
    out: dict[int, set[int]] = {q: set() for q in range(NQUBITS)}
    for a, b in topology:
        out[a].add(b)
        out[b].add(a)
    return out


def patch_candidates(topology: tuple[tuple[int, int], ...]) -> list[tuple[int, int, int, int]]:
    """Every (q3, q1, q0, q2) with q3 < q0 both coupled to q1, over the qubits outside excluded_qubits()."""
    excluded = set(excluded_qubits())
    qubits = [q for q in range(NQUBITS) if q not in excluded]
    adj = adjacency(topology)
    out: list[tuple[int, int, int, int]] = []
    for q1 in qubits:
        for q3, q0 in itertools.combinations(sorted(adj[q1] & set(qubits)), 2):
            out.extend((q3, q1, q0, q2) for q2 in qubits if q2 not in {q3, q1, q0})
    return sorted(out)


def placement_key(placement: tuple[tuple[int, int, int, int], ...], topology: tuple[tuple[int, int], ...]) -> tuple:
    edges = {frozenset(e) for e in topology}
    paths = [set(p[:3]) for p in placement]
    holds_both = sum(1 for p in paths if {11, 13} <= p)
    path_path = sum(
        frozenset((a, b)) in edges
        for i, j in itertools.combinations(range(len(paths)), 2)
        for a in paths[i]
        for b in paths[j]
    )
    q2_path = sum(
        frozenset((p[3], b)) in edges
        for i, p in enumerate(placement)
        for j, path in enumerate(paths)
        if j != i
        for b in path
    )
    return (holds_both, path_path, q2_path, placement)


def select_placement(topology: tuple[tuple[int, int], ...]) -> list[tuple]:
    """Disjoint patch triples ranked by (paths holding q11 and q13, path-path couplers, q2-path couplers, tuple)."""
    patches = patch_candidates(topology)
    masks = [sum(1 << q for q in p) for p in patches]
    ranking = []
    for i, mi in enumerate(masks):
        for j in range(i + 1, len(patches)):
            if mi & masks[j]:
                continue
            both = mi | masks[j]
            for k in range(j + 1, len(patches)):
                if not both & masks[k]:
                    ranking.append(placement_key((patches[i], patches[j], patches[k]), topology))
    return sorted(ranking)


# --- layout and references ---------------------------------------------------------------------


def circuit_states(plan: tuple[tuple[int, int, int, str, str], ...] = WITNESS_PLAN) -> list[tuple[str, str, str]]:
    """State names by patch (0, 1, 2) of each of the 2 x len(plan) witness circuits, in file order."""
    out = []
    for m, n_low, n_high, first, second in plan:
        a, b = (p for p in range(PATCHES) if p != m)
        for k_on_low, h_state in ((True, first), (False, second)):
            row = [""] * PATCHES
            row[a] = f"{'k' if k_on_low else 'b'}{n_low}"
            row[b] = f"{'b' if k_on_low else 'k'}{n_high}"
            row[m] = h_state
            out.append((row[0], row[1], row[2]))
    return out


def state_group(name: str) -> str:
    return ENTRY[name]["group"]


def balance_tables(
    plan: tuple[tuple[int, int, int, str, str], ...] = WITNESS_PLAN,
) -> dict[str, Any]:
    """Counts of the witness layout; raises unless every balance property holds.

    Properties: every state meets every patch once; each group meets each patch equally; each group meets
    each (patch, ordered pair of groups on the other two patches) equally; every swap pair of group
    assignments occurs twice; every kernel index and its bright partner share a batch on every patch.
    """
    rows = circuit_states(plan)
    state_patch = Counter((s, p) for row in rows for p, s in enumerate(row))
    require(
        all(state_patch[(e["name"], p)] == 1 for e in BANK for p in range(PATCHES)) and len(state_patch) == 36,
        "a state does not meet every patch exactly once",
    )
    group_patch = Counter((state_group(s), p) for row in rows for p, s in enumerate(row))
    for group in GROUP_IDEAL:
        counts = {group_patch[(group, p)] for p in range(PATCHES)}
        require(len(counts) == 1, f"{group} meets the patches unequally: {sorted(group_patch.items())}")

    def slot(name: str) -> str:
        return "half" if state_group(name) in {"middle", "sector"} else state_group(name)

    context: Counter[tuple[str, int, tuple[str, ...]]] = Counter()
    for row in rows:
        labels = [slot(s) for s in row]
        for p in range(PATCHES):
            others = tuple(labels[q] for q in range(PATCHES) if q != p)
            context[(labels[p], p, others)] += 1
    # Kernel and bright circuits sit 2 per (patch, order); the half slot holds middle or sector, 1 each.
    half_context: Counter[tuple[str, int, tuple[str, ...]]] = Counter()
    for row in rows:
        labels = [slot(s) for s in row]
        for p in range(PATCHES):
            if labels[p] == "half":
                half_context[(state_group(row[p]), p, tuple(labels[q] for q in range(PATCHES) if q != p))] += 1
    expected_keys = {
        "kernel": {("kernel", p, o) for p in range(PATCHES) for o in _orders("bright")},
        "bright": {("bright", p, o) for p in range(PATCHES) for o in _orders("kernel")},
    }
    for group, keys in expected_keys.items():
        require(
            set(k for k in context if k[0] == group) == keys and {context[k] for k in keys} == {2},
            f"{group} meets its neighbor contexts unequally: {sorted(context.items())}",
        )
    half_keys = {
        (g, p, o)
        for g in ("middle", "sector")
        for p in range(PATCHES)
        for o in (("kernel", "bright"), ("bright", "kernel"))
    }
    require(
        set(half_context) == half_keys and {half_context[k] for k in half_keys} == {1},
        f"middle and sector meet neighbor contexts unequally: {sorted(half_context.items())}",
    )
    assignments = Counter(
        tuple("half" if state_group(s) in {"middle", "sector"} else state_group(s) for s in row) for row in rows
    )
    require(len(assignments) == 6 and set(assignments.values()) == {2}, f"assignment counts {assignments}")
    pairs: dict[str, list[dict[str, Any]]] = {f"patch-{p}": [] for p in range(PATCHES)}
    for batch, (m, n_low, n_high, _, _) in enumerate(plan):
        a, b = (p for p in range(PATCHES) if p != m)
        pairs[f"patch-{a}"].append({"plan_row": batch, "pair": n_low})
        pairs[f"patch-{b}"].append({"plan_row": batch, "pair": n_high})
    for patch, found in pairs.items():
        require(sorted(r["pair"] for r in found) == [1, 2, 3, 4], f"{patch} partner pairs {found}")
    return {
        "state_patch_cells": {f"{s}/patch-{p}": n for (s, p), n in sorted(state_patch.items())},
        "group_patch_cells": {f"{g}/patch-{p}": n for (g, p), n in sorted(group_patch.items())},
        "group_patch_neighbor_groups_cells": {
            f"{g}/patch-{p}/{'+'.join(o)}": n
            for (g, p, o), n in sorted({**context, **half_context}.items())
            if g != "half"
        },
        "group_assignments_circuits": {"+".join(k): n for k, n in sorted(assignments.items())},
        "partner_pairs_per_patch": pairs,
        "properties": [
            "every state meets every patch once (36 witness cells)",
            "each group meets each patch equally",
            "each group meets each patch and ordered pair of neighbor groups equally "
            "(kernel and bright 2, middle and sector 1)",
            "each of the six assignments of (kernel, bright, half) to the patches occurs in two circuits",
            "kernel and bright states of one index share a batch on each patch that carries them",
        ],
    }


def _orders(other: str) -> list[tuple[str, str]]:
    """Ordered neighbor labels of a kernel or bright state: its partner group and the half slot in either order."""
    return [(other, "half"), ("half", other)]


def patch_qubits() -> list[int]:
    return sorted(q for patch in PLACEMENT for q in patch)


def bipartition(qubits: list[int], edges: tuple[tuple[int, int], ...]) -> tuple[list[int], list[int]]:
    """Two-coloring of the coupling graph induced on qubits; the lowest qubit of a component is in part P."""
    chosen = set(qubits)
    adj = {q: sorted(n for n in adjacency(edges)[q] if n in chosen) for q in qubits}
    color: dict[int, int] = {}
    for start in qubits:
        if start in color:
            continue
        color[start] = 0
        queue = [start]
        while queue:
            current = queue.pop(0)
            for neighbor in adj[current]:
                if neighbor not in color:
                    color[neighbor] = 1 - color[current]
                    queue.append(neighbor)
                elif color[neighbor] == color[current]:
                    raise ValueError(f"coupler ({current}, {neighbor}) joins two qubits of one part")
    return [q for q in qubits if color[q] == 0], [q for q in qubits if color[q] == 1]


def patch_couplers(qubits: list[int], edges: tuple[tuple[int, int], ...]) -> list[list[int]]:
    chosen = set(qubits)
    return [sorted(e) for e in sorted(edges) if e[0] in chosen and e[1] in chosen]


def reference_sets() -> dict[str, list[int]]:
    """Physical qubits flipped by X in each Tuna reference circuit."""
    qubits = patch_qubits()
    part_p, part_q = bipartition(qubits, TUNA17)
    return {READOUT_ZERO: [], READOUT_ONE: qubits, CHECKER_P: part_p, CHECKER_Q: part_q}


def check_reference_sets(sets: dict[str, list[int]]) -> None:
    """Every coupler of the patch qubits meets all four joint preparations, and q13 is coupled to q11."""
    couplers = patch_couplers(patch_qubits(), TUNA17)
    require([11, 13] in couplers, "q11 and q13 are not a coupled pair of patch qubits")
    for u, v in couplers:
        seen = {(int(u in x), int(v in x)) for x in sets.values()}
        require(seen == {(0, 0), (0, 1), (1, 0), (1, 1)}, f"coupler ({u}, {v}) sees the preparations {sorted(seen)}")


# --- circuits ---------------------------------------------------------------------------------


def logical_map(patch: tuple[int, int, int, int]) -> dict[int, int]:
    q3, q1, q0, q2 = patch
    return {3: q3, 2: q2, 1: q1, 0: q0}


def cqasm_ops(ops: list[tuple[str, tuple[int, ...]]], where: dict[int, int]) -> list[str]:
    lines = []
    for name, qubits in ops:
        if name == "cz":
            lines.append(f"CZ q[{where[qubits[0]]}], q[{where[qubits[1]]}]")
        else:
            lines.append(f"{CQASM[name]} q[{where[qubits[0]]}]")
    return lines


def circuit_text(
    width: int, instances: list[tuple[int, tuple[int, int, int, int], str]], rotation: list[tuple[str, tuple[int, ...]]]
) -> str:
    """cQASM text of patch instances (patch id, physical (q3, q1, q0, q2), state): prepare, barrier, rotate, measure."""
    prep, rot = [], []
    for patch_id, qubits, state in instances:
        where = logical_map(qubits)
        prep.append(f"// patch {patch_id} (q3 q1 q0 q2 = {list(qubits)}) state {state}")
        prep += cqasm_ops(prep_ops(ENTRY[state]), where)
        rot += cqasm_ops(rotation, where)
    return "\n".join(header(width) + prep + ["", "barrier q", ""] + rot + ["", "barrier q", "b = measure q", ""])


def reference_text(width: int, flipped: list[int]) -> str:
    """Reference circuit: X on the flipped qubits, then measure the whole register."""
    lines = header(width) + [f"X q[{q}]" for q in flipped] + ([""] if flipped else [])
    return "\n".join(lines + ["barrier q", "b = measure q", ""])


def qiskit_circuit(ops: list[tuple[str, tuple[int, ...]]], width: int) -> Any:
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(width)
    for name, qubits in ops:
        if name in {"x90", "my90"}:
            qc.unitary(GATE_MATRIX[name], list(qubits), label=name)
        else:
            getattr(qc, name)(*qubits)
    return qc


def parse_cqasm(text: str) -> list[tuple[str, tuple[int, ...]]]:
    """Gate list of an emitted circuit; any line outside the emitted vocabulary raises."""
    inverse = {v: k for k, v in CQASM.items()}
    ops: list[tuple[str, tuple[int, ...]]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(("//", "version", "qubit[", "bit[", "barrier", "b = measure")):
            continue
        name, _, rest = line.partition(" ")
        qubits = tuple(int(part.strip()[2:-1]) for part in rest.split(","))
        if name == "CZ" and len(qubits) == 2:
            ops.append(("cz", qubits))
        elif name in inverse and len(qubits) == 1:
            ops.append((inverse[name], qubits))
        else:
            raise ValueError(f"unrecognized cQASM line {line!r}")
    return ops


def patch_sequences(text: str, patches: list[tuple[int, int, int, int]]) -> list[list[tuple[str, tuple[int, ...]]]]:
    """Gate sequence of each patch with physical qubits mapped back to logical ones."""
    owner: dict[int, tuple[int, int]] = {}
    for p, patch in enumerate(patches):
        owner.update({phys: (p, logical) for logical, phys in logical_map(patch).items()})
    out: list[list[tuple[str, tuple[int, ...]]]] = [[] for _ in patches]
    for name, qubits in parse_cqasm(text):
        index = {owner[q][0] for q in qubits}
        require(len(index) == 1, f"{name} {qubits} joins two patches")
        out[index.pop()].append((name, tuple(owner[q][1] for q in qubits)))
    return out


class CheckCircuit:
    """Exact check of one witness or quadrature circuit; a module-level callable for parallel.ordered_map."""

    def __call__(self, spec: tuple[str, int, str, list[tuple[int, tuple[int, int, int, int], str]]]) -> dict[str, Any]:
        from qiskit.quantum_info import Statevector

        kind, width, text, instances = spec
        g, parity = score_vector(), parity_vector()
        ideal = ideal_scores()
        for _, _, state in instances:
            prepared = Statevector(qiskit_circuit(prep_ops(ENTRY[state]), 4)).data
            if abs(abs(np.vdot(state_vector(ENTRY[state]), prepared)) - 1) > 1e-12:
                raise ValueError(f"{state}: preparation circuit differs from its target vector")
        emitted = Statevector(qiskit_circuit(parse_cqasm(text), width))
        rows = []
        for patch_id, (q3, q1, q0, q2), state in instances:
            probs = emitted.probabilities([q0, q1, q2, q3])
            if kind == "witness":
                value = float(g @ probs)
                if abs(value - ideal[state]) > 1e-9:
                    raise ValueError(f"{state} on patch {patch_id}: emitted ideal score {value}")
            else:
                value = float(parity @ probs)
                want = quadrature_expectation(state)["cos_coefficient"] if kind == "cosine" else 0.0
                if abs(value - want) > 1e-9:
                    raise ValueError(f"{state} on patch {patch_id}: emitted ideal {kind} parity {value}, not {want}")
            rows.append(round(value, 12))
        return {"values": rows}


# --- schedule -----------------------------------------------------------------------------------


def witness_file(circuit: int) -> str:
    return f"witness-{circuit + 1:02d}.cq"


def quadrature_file(state: str) -> str:
    return f"quadrature-{state}.cq"


def cosine_file(state: str) -> str:
    return f"cosine-{state}.cq"


def tuna_schedule() -> list[list[tuple[str, str]]]:
    """(kind, file) of each circuit of each batch, in submission order.

    The X-basis and Y-basis circuits of one state share a batch, so the sine and cosine amplitudes of the
    branch phase average the same two calibration windows.
    """
    w = [("witness", witness_file(c)) for c in range(2 * len(WITNESS_PLAN))]
    ro0, ro1 = ("readout", READOUT_ZERO), ("readout", READOUT_ONE)
    k1, b1, e7 = QUADRATURE_STATES
    return [
        [ro0, ro1, ("readout", CHECKER_P)],
        [w[0], w[1], ("readout", CHECKER_Q)],
        [w[2], w[3], ro0],
        [w[4], w[5], ro1],
        [("quadrature", quadrature_file(k1)), ("cosine", cosine_file(k1)), ("quadrature", quadrature_file(e7))],
        [("quadrature", quadrature_file(b1)), ("cosine", cosine_file(b1)), ro0],
        [w[6], w[7], ro1],
        [w[8], w[9], ro0],
        [w[10], w[11], ro1],
    ]


def twin_schedule(files: list[tuple[str, str]]) -> list[list[tuple[str, str]]]:
    """Batch-00 holds both references and the first circuit; two circuits and one reference follow in each batch."""
    ro0, ro1 = ("readout", READOUT_ZERO), ("readout", READOUT_ONE)
    batches = [[ro0, ro1, files[0]]]
    rest = files[1:]
    for n, start in enumerate(range(0, len(rest), 2)):
        batches.append([*rest[start : start + 2], ro0 if n % 2 == 0 else ro1])
    return batches


def nearest_references(schedule: list[list[tuple[str, str]]]) -> dict[str, dict[str, str]]:
    """Batch holding the nearest readout-0 and readout-1 of each batch; the earlier batch on a tie."""
    out = {}
    for b in range(len(schedule)):
        row = {}
        for name in (READOUT_ZERO, READOUT_ONE):
            holders = [j for j, batch in enumerate(schedule) if ("readout", name) in batch]
            row[name] = f"batch-{min(holders, key=lambda j: (abs(j - b), j)):02d}"
        out[f"batch-{b:02d}"] = row
    return out


def series_cost(schedule: list[list[tuple[str, str]]], shots: int, hardware: bool) -> dict[str, Any]:
    """Execution by the Tuna-17 timing fit and the wall-time ceiling of the approved budget.

    The ceiling takes the top step of HARDWARE_PAUSE_LADDER between hardware batches, so a series paced at
    any lower step finishes inside it and the manifests stay the same whichever step qi_platform.submit
    applies; the emulator takes no pause.
    """
    jobs = sum(len(batch) for batch in schedule)
    per_job = JOB_FIXED_SECONDS + JOB_SECONDS_PER_SHOT * shots
    execution = jobs * per_job
    pause = HARDWARE_PAUSE_LADDER[-1] if hardware else 0
    return {
        "jobs": jobs,
        "batches": len(schedule),
        "shots": shots,
        "seconds_per_job": round(per_job, 3),
        "execution_seconds": round(execution, 1),
        "pause_seconds": pause,
        "wall_seconds": round(execution + pause * (len(schedule) - 1), 1),
        "fit": f"{JOB_FIXED_SECONDS} s + {JOB_SECONDS_PER_SHOT * 1000} ms per shot per job",
        "queue": "excluded: each batch also waits behind other users' batches",
    }


# --- build --------------------------------------------------------------------------------------


def backend_contract(backend: dict[str, Any]) -> dict[str, str]:
    """sha256 of the canonical JSON of each CONTRACT_FIELDS value of a backend type record.

    The placement, the emitted gate names and compile_stage "none" assume the topology, gate set and
    default compiler configuration of the record the cases were built from; --submit-next compares these
    digests with the live record before it sends a batch.
    """
    return {
        field: hashlib.sha256(json.dumps(backend[field], sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        for field in CONTRACT_FIELDS
    }


def witness_specs() -> list[dict[str, Any]]:
    """Tuna circuits that read the Y/X/Y/Z basis, then the quadrature circuits, as patch instances."""
    out: list[dict[str, Any]] = []
    for c, states in enumerate(circuit_states()):
        out.append(
            {
                "file": witness_file(c),
                "kind": "witness",
                "instances": [(p, PLACEMENT[p], states[p]) for p in range(PATCHES)],
            }
        )
    for state in QUADRATURE_STATES:
        out.append(
            {
                "file": quadrature_file(state),
                "kind": "quadrature",
                "instances": [(p, PLACEMENT[p], state) for p in range(PATCHES)],
            }
        )
    for state in QUADRATURE_STATES[:2]:
        out.append(
            {
                "file": cosine_file(state),
                "kind": "cosine",
                "instances": [(p, PLACEMENT[p], state) for p in range(PATCHES)],
            }
        )
    return out


def rotation_of(kind: str) -> list[tuple[str, tuple[int, ...]]]:
    """The cosine circuits read the witness basis; only the quadrature circuits read q3 in X."""
    return QUADRATURE_OPS if kind == "quadrature" else READOUT_OPS


def batch_of_file(schedule: list[list[tuple[str, str]]]) -> dict[str, str]:
    return {f: f"batch-{b:02d}" for b, batch in enumerate(schedule) for _, f in batch}


def twin_slot_qubits(slot: int) -> tuple[int, int, int, int]:
    return (4 * slot + 3, 4 * slot + 1, 4 * slot, 4 * slot + 2)


def twin_specs(tuna: list[dict[str, Any]], source_batch: dict[str, str]) -> list[dict[str, Any]]:
    """Two patch instances per circuit, in the order of the Tuna circuits, with kinds kept apart."""
    out: list[dict[str, Any]] = []
    for kind in ("witness", "quadrature", "cosine"):
        flat = [(p, state, spec["file"]) for spec in tuna if spec["kind"] == kind for p, _, state in spec["instances"]]
        for n, start in enumerate(range(0, len(flat), 2), start=1):
            chunk = flat[start : start + 2]
            out.append(
                {
                    "file": f"twin-{kind}-{n:02d}.cq",
                    "kind": kind,
                    "instances": [(p, twin_slot_qubits(s), state) for s, (p, state, _) in enumerate(chunk)],
                    "sources": [{"file": f, "batch": source_batch[f]} for _, _, f in chunk],
                }
            )
    return out


def patch_rows(
    spec: dict[str, Any], values: list[float], sources: list[dict[str, str]], ideal: dict[str, float]
) -> list[dict[str, Any]]:
    rows = []
    for (patch_id, qubits, state), value, source in zip(spec["instances"], values, sources, strict=True):
        row: dict[str, Any] = {
            "patch": patch_id,
            "state": state,
            "qubits": list(qubits),
            "source_file": source["file"],
            "source_batch": source["batch"],
        }
        if spec["kind"] == "witness":
            row["ideal_score"] = ideal[state]
        else:
            row["ideal_parity"] = value
            row["quadrature"] = quadrature_expectation(state)
        rows.append(row)
    return rows


@cache
def build() -> dict[str, dict[str, str]]:
    """Series directory name -> {file name: text}, after the exact circuit checks."""
    backend, qx_backend = catalogue_check()
    for device in (backend, qx_backend):
        needed = {CQASM[g] for g in CQASM} | {"CZ", "barrier", "measure"}
        if not needed <= set(device["gateset"]):
            raise SystemExit(f"{device['identifier']}: gate set lacks {sorted(needed - set(device['gateset']))}")
    if backend["max_number_of_shots"] < SHOTS:
        raise SystemExit(f"{BACKEND} admits {backend['max_number_of_shots']} shots, below {SHOTS}")
    excluded = set(excluded_qubits())
    used = {q for patch in PLACEMENT for q in patch}
    if len(used) != 4 * PATCHES or used & excluded:
        raise SystemExit(f"PLACEMENT {PLACEMENT} overlaps or uses an excluded qubit of {sorted(excluded)}")
    ideal = ideal_scores()
    rotations = native_rotation_check()
    balance = balance_tables()
    references = reference_sets()
    check_reference_sets(references)
    schedule = tuna_schedule()
    if any(len(batch) > HARDWARE_BATCH_CIRCUITS for batch in schedule):
        raise SystemExit(f"a batch exceeds the {HARDWARE_BATCH_CIRCUITS}-circuit limit")
    specs = witness_specs()
    texts: dict[str, str] = {}
    for spec in specs:
        texts[spec["file"]] = circuit_text(NQUBITS, spec["instances"], rotation_of(spec["kind"]))
    for name, flipped in references.items():
        texts[name] = reference_text(NQUBITS, flipped)
    checks = parallel.ordered_map(
        CheckCircuit(), [(s["kind"], NQUBITS, texts[s["file"]], s["instances"]) for s in specs]
    )
    tuna_batch = batch_of_file(schedule)
    couplers = patch_couplers(patch_qubits(), TUNA17)

    shared = {
        "backend": BACKEND,
        "backend_type_id": backend["id"],
        "nqubits": backend["nqubits"],
        "shots": SHOTS,
        "placement": [list(p) for p in PLACEMENT],
        "placement_fields": ["q3", "q1", "q0", "q2"],
        "patch_qubits": patch_qubits(),
        "patch_couplers": couplers,
        "excluded_qubits": sorted(excluded),
        "logical_to_physical": [
            {"patch": p, **{f"q{b}": q for b, q in sorted(logical_map(patch).items(), reverse=True)}}
            for p, patch in enumerate(PLACEMENT)
        ],
        "bit_order": "a shot string puts qubit 0 at the rightmost character: qubit q is character -(1 + q)",
        "readout_basis": {"witness": WITNESS_BASIS, "quadrature": QUADRATURE_BASIS},
        "readout_rotation": {
            "witness": [[n, list(qs)] for n, qs in READOUT_OPS],
            "quadrature": [[n, list(qs)] for n, qs in QUADRATURE_OPS],
            "pulses": "X90 maps the Y eigenbasis and mY90 the X eigenbasis onto Z (cQASM v3 standard gate set)",
            "verified": rotations,
        },
        "score": "g = 1/2 for z2 = +1 and (1 - t)/2 for z2 = -1, t = y3 x1 y0, as in "
        + PAULI_FORM.relative_to(ROOT).as_posix(),
        "bank": [
            {
                "name": e["name"],
                "group": e["group"],
                "ideal_score": ideal[e["name"]],
                "terms": {str(i): c for i, c in sorted(e["terms"].items())},
                "preparation": [[name, list(qs)] for name, qs in prep_ops(e)],
            }
            for e in BANK
        ],
        "witness_layout": {
            "plan_fields": [
                "h_patch",
                "kernel_index_low_patch",
                "kernel_index_high_patch",
                "h_circuit_1",
                "h_circuit_2",
            ],
            "plan": [list(row) for row in WITNESS_PLAN],
            "balance": balance,
        },
        "references": references,
        "readout_pairing": nearest_references(schedule),
        "schedule": [[f for _, f in batch] for batch in schedule],
        "cost": series_cost(schedule, SHOTS, True),
        "backend_contract": backend_contract(backend),
        "preregistered": PREREGISTERED,
    }
    files = write_series(
        shared,
        schedule,
        specs,
        [c["values"] for c in checks],
        texts,
        {s["file"]: [{"file": s["file"], "batch": tuna_batch[s["file"]]}] * len(s["instances"]) for s in specs},
        ideal,
        references,
    )

    # Twin: two patches per circuit on qubits 0-7 of the 10-qubit emulator.
    twin_source = twin_specs(specs, tuna_batch)
    twin_texts: dict[str, str] = {}
    for spec in twin_source:
        twin_texts[spec["file"]] = circuit_text(QX_QUBITS, spec["instances"], rotation_of(spec["kind"]))
    flipped = list(range(8))
    twin_refs = {READOUT_ZERO: [], READOUT_ONE: flipped}
    twin_texts.update({name: reference_text(QX_QUBITS, qs) for name, qs in twin_refs.items()})
    twin_checks = parallel.ordered_map(
        CheckCircuit(), [(s["kind"], QX_QUBITS, twin_texts[s["file"]], s["instances"]) for s in twin_source]
    )
    for spec in twin_source:
        # Identical gate sequence per patch: each twin slot repeats the Tuna patch's gates on relabeled qubits.
        slot_patches = [qs for _, qs, _ in spec["instances"]]
        twin_seq = patch_sequences(twin_texts[spec["file"]], slot_patches)
        for (patch_id, _, _), source, sequence in zip(spec["instances"], spec["sources"], twin_seq, strict=True):
            tuna_seq = patch_sequences(texts[source["file"]], list(PLACEMENT))[patch_id]
            if sequence != tuna_seq:
                raise SystemExit(f"{spec['file']}: patch {patch_id} differs from {source['file']}")
    twin_schedule_rows = twin_schedule([(s["kind"], s["file"]) for s in twin_source])
    twin_shared = {
        **{k: v for k, v in shared.items() if k not in {"placement", "logical_to_physical", "excluded_qubits"}},
        "backend": QX_BACKEND,
        "backend_type_id": qx_backend["id"],
        "nqubits": qx_backend["nqubits"],
        "shots": QX_SHOTS,
        "twin_of": BACKEND,
        "placement": [list(twin_slot_qubits(s)) for s in range(2)],
        "logical_to_physical": [
            {"patch": s, **{f"q{b}": q for b, q in sorted(logical_map(twin_slot_qubits(s)).items(), reverse=True)}}
            for s in range(2)
        ],
        "twin_note": "slot s carries a Tuna patch on qubits 4s to 4s+3; each patch row names its Tuna patch, "
        "source circuit and source batch",
        "patch_qubits": flipped,
        "patch_couplers": [],
        "references": twin_refs,
        "readout_pairing": nearest_references(twin_schedule_rows),
        "schedule": [[f for _, f in batch] for batch in twin_schedule_rows],
        "cost": series_cost(twin_schedule_rows, QX_SHOTS, False),
        "backend_contract": backend_contract(qx_backend),
    }
    twin_files = write_series(
        twin_shared,
        twin_schedule_rows,
        twin_source,
        [c["values"] for c in twin_checks],
        twin_texts,
        {s["file"]: s["sources"] for s in twin_source},
        ideal,
        twin_refs,
        series_name="qi-bdsc-pauli-twin-series-v1",
    )
    return {SERIES: files, TWIN_SERIES: twin_files}


def write_series(
    shared: dict[str, Any],
    schedule: list[list[tuple[str, str]]],
    specs: list[dict[str, Any]],
    values: list[list[float]],
    texts: dict[str, str],
    sources: dict[str, list[dict[str, str]]],
    ideal: dict[str, float],
    references: dict[str, list[int]],
    series_name: str = "qi-bdsc-pauli-series-v1",
) -> dict[str, str]:
    by_file = {s["file"]: s for s in specs}
    witnesses = []
    for spec, row_values in zip(specs, values, strict=True):
        witnesses.append(
            {
                "file": spec["file"],
                "kind": spec["kind"],
                "patches": patch_rows(spec, row_values, sources[spec["file"]], ideal),
            }
        )
    shared = {**shared, "witnesses": witnesses}
    files: dict[str, str] = {}
    batches = []
    for b, batch in enumerate(schedule):
        name = f"batch-{b:02d}"
        rows = []
        for kind, file in batch:
            row: dict[str, Any] = {"file": file, "kind": "readout" if kind == "readout" else kind}
            if kind == "readout":
                row["x_qubits"] = references[file]
            row["sha256"] = hashlib.sha256(texts[file].encode()).hexdigest()
            files[f"{name}/{file}"] = texts[file]
            rows.append(row)
            if kind != "readout" and file not in by_file:
                raise SystemExit(f"{file} is scheduled but has no specification")
        manifest = {"schema": "qi-bdsc-pauli-cases-v2", **shared, "batch": name, "circuits": rows}
        files[f"{name}/cases.json"] = json.dumps(manifest, indent=1) + "\n"
        batches.append({"batch": name, "files": [row["file"] for row in rows]})
    series = {"schema": series_name, "backend": shared["backend"], "batches": batches}
    files["cases.json"] = json.dumps(series, indent=1) + "\n"
    scheduled = {f for batch in schedule for _, f in batch}
    if scheduled != set(by_file) | set(references):
        raise SystemExit("the schedule and the circuit set differ")
    return files


# --- analysis -----------------------------------------------------------------------------------


def shot_bits(shots: list[str], width: int, source: str = "") -> np.ndarray:
    """(n, width) uint8 matrix of the shot strings, column c holding character c.

    Each character is one qubit's measured bit; the conversion subtracts ord("0"), so a character other
    than the binary digits 0 and 1 is refused rather than read as a large integer.
    """
    if any(len(s) != width for s in shots):
        raise SystemExit(f"{source}: a shot string differs from the declared width {width}")
    try:
        data = "".join(shots).encode("ascii")
    except UnicodeEncodeError:
        raise SystemExit(f"{source}: a shot string holds a character other than the binary digits 0 and 1") from None
    bits = np.frombuffer(data, dtype=np.uint8).reshape(len(shots), width) - 48
    if bits.size and int(bits.max()) > 1:
        raise SystemExit(f"{source}: a shot string holds a character other than the binary digits 0 and 1")
    return bits


def unassign(freq: list[float], rates: list[tuple[float, float]]) -> list[float]:
    """Inverse tensor product of the assignment matrices applied to P(code); rates[i] is (e01, e10) of bit 3 - i.

    Each axis applies the closed-form inverse of [[1 - e01, e10], [e01, 1 - e10]]; unassign_batch repeats the
    same operations in the same order on arrays, so a replicate has the same bits in both paths.
    """
    p = list(freq)
    for i, (e01, e10) in enumerate(rates):
        k = 3 - i
        det = (1.0 - e01) * (1.0 - e10) - e10 * e01
        if not det > SINGULAR_DET:
            raise ValueError(f"assignment matrix of bit {k} is singular (e01 {e01}, e10 {e10})")
        for c in range(16):
            if not c >> k & 1:
                v0, v1 = p[c], p[c | 1 << k]
                p[c] = ((1.0 - e10) * v0 - e10 * v1) / det
                p[c | 1 << k] = ((1.0 - e01) * v1 - e01 * v0) / det
    return p


def expectation(weights: list[float], p: list[float]) -> float:
    acc = 0.0
    for c in range(16):
        acc += weights[c] * p[c]
    return acc


def corrected_expectation(freq: list[float], rates: list[tuple[float, float]], weights: np.ndarray) -> float:
    return expectation(weights.tolist(), unassign(freq, rates))


def unassign_batch(freq: np.ndarray, e01: np.ndarray, e10: np.ndarray) -> np.ndarray:
    """unassign over B replicates: freq (B, 16), e01 and e10 (B, 4) with column i the rate of bit 3 - i."""
    p = freq.copy()
    b = len(p)
    for i in range(4):
        k = 3 - i
        a_, c_ = e01[:, i], e10[:, i]
        det = (1.0 - a_) * (1.0 - c_) - c_ * a_
        if not np.all(det > SINGULAR_DET):
            raise ValueError(f"an assignment matrix of bit {k} is singular in a bootstrap draw")
        view = p.reshape(b, 2 ** (3 - k), 2, 2**k)
        v0, v1 = view[:, :, 0, :].copy(), view[:, :, 1, :].copy()
        a3, c3, d3 = a_[:, None, None], c_[:, None, None], det[:, None, None]
        view[:, :, 0, :] = ((1.0 - c3) * v0 - c3 * v1) / d3
        view[:, :, 1, :] = ((1.0 - a3) * v1 - a3 * v0) / d3
    return p


def expectation_batch(weights: np.ndarray, p: np.ndarray) -> np.ndarray:
    acc = np.zeros(len(p))
    for c in range(16):
        acc += float(weights[c]) * p[:, c]
    return acc


CODE_BIT = np.array([[c >> (3 - i) & 1 for i in range(4)] for c in range(16)], dtype=float)


def joint_rates(p0: np.ndarray, p1: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(e01, e10) with column i the rate of bit 3 - i, from joint outcome probabilities (..., 16) of the
    patch qubits in readout-0 and readout-1: e01 is P(read 1 | 0) and e10 is P(read 0 | 1) of each bit."""
    return p0 @ CODE_BIT, p1 @ (1.0 - CODE_BIT)


class BootstrapCell:
    """Jeffreys-posterior percentile interval of one cell's tensor-model mitigated score.

    Each draw takes Dirichlet(counts + JEFFREYS) over the 16 witness outcomes and over the 16 joint
    outcomes of the patch qubits in readout-0 and in readout-1, so the four assignment rates of one draw
    keep the covariance of the calibration shots they share. A module-level callable for
    parallel.ordered_map.
    """

    def __init__(self, weights: np.ndarray, draws: int, vary_reference: bool = True) -> None:
        self.weights = weights
        self.draws = draws
        self.vary_reference = vary_reference

    def replicates(self, task: tuple[Any, ...]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        counts, ref0, ref1, index = task
        rng = np.random.default_rng(np.random.SeedSequence([BOOTSTRAP_SEED, index]))
        freq = rng.dirichlet(np.asarray(counts, dtype=float) + JEFFREYS, size=self.draws)
        r0, r1 = np.asarray(ref0, dtype=float), np.asarray(ref1, dtype=float)
        if self.vary_reference:
            p0 = rng.dirichlet(r0 + JEFFREYS, size=self.draws)
            p1 = rng.dirichlet(r1 + JEFFREYS, size=self.draws)
        else:
            p0 = np.tile(r0 / r0.sum(), (self.draws, 1))
            p1 = np.tile(r1 / r1.sum(), (self.draws, 1))
        e01, e10 = joint_rates(p0, p1)
        return freq, e01, e10

    def __call__(self, task: tuple[Any, ...]) -> list[float]:
        """The equal-tailed posterior interval widened to hold the plug-in estimate.

        A cell or reference with every shot in one outcome has its plug-in value on the boundary, where the
        equal-tailed Jeffreys interval excludes it; the hull follows the boundary rule of Brown, Cai and
        DasGupta (2001, Stat. Sci. 16, 101), which sets the Jeffreys bound to the observed value there.
        """
        counts, ref0, ref1, _ = task
        freq, e01, e10 = self.replicates(task)
        scores = expectation_batch(self.weights, unassign_batch(freq, e01, e10))
        low, high = np.percentile(scores, [100 * ALPHA / 2, 100 * (1 - ALPHA / 2)])
        r0, r1 = np.asarray(ref0, dtype=float), np.asarray(ref1, dtype=float)
        a, c = joint_rates(r0 / r0.sum(), r1 / r1.sum())
        n = sum(counts)
        point = corrected_expectation(
            [x / n for x in counts], list(zip(a.tolist(), c.tolist(), strict=True)), self.weights
        )
        return [min(float(low), point), max(float(high), point)]


def eb_interval(scores: np.ndarray) -> list[float]:
    from experiment_optimizer import empirical_bernstein_radius

    n = len(scores)
    radius = empirical_bernstein_radius(float(scores.var(ddof=1)), 1.0, n, ALPHA, True)
    mean = float(scores.mean())
    return [max(mean - radius, 0.0), min(mean + radius, 1.0)]


def z_of(residual: float, variance: float) -> float | None:
    if variance > 0:
        return residual / math.sqrt(variance)
    return 0.0 if residual == 0 else None


def statistic(residual: float, variance: float) -> dict[str, Any]:
    z = z_of(residual, variance)
    return {"residual": residual, "se": math.sqrt(variance), "z": z, "flag": z is None or abs(z) >= Z_FLAG}


def reference_counts(bits0: np.ndarray, bits1: np.ndarray, qubit: int, width: int) -> tuple[int, int, int, int]:
    """(ones in readout-0, shots, zeros in readout-1, shots) of one physical qubit."""
    column = width - 1 - qubit
    return int(bits0[:, column].sum()), len(bits0), int(len(bits1) - bits1[:, column].sum()), len(bits1)


STOPPED_CLAIM = "stopped series: a preregistered stop fired, no inference"


def claim_kind(cases: dict[str, Any]) -> str:
    """Hardware inference, or an emulator control for the QX twin and for a local qxelarator run of either series."""
    if "control" in cases or "simulator" in cases:
        require(
            cases.get("control") == "local_qxelarator" and isinstance(cases.get("simulator"), dict),
            "a manifest with a control marker must name the local qxelarator simulator",
        )
        return "emulator control"
    return analysis_claim_kind(cases)


def require_full_shots(cases: dict[str, Any], raw: dict[tuple[str, str], list[str]]) -> None:
    """Refuse a series whose shot list is shorter than cases["shots"]; the preregistered stop names the file.

    qi_platform.collect retains a short list as returned, so the analysis applies the stop before any cell.
    """
    wanted = {file: cases["shots"] for (_, file) in raw}
    for file in cases.get("references", {}):
        wanted[file] = cases.get("reference_shots", cases["shots"])
    short = sorted((batch, file, len(shots)) for (batch, file), shots in raw.items() if len(shots) != wanted[file])
    if short:
        batch, file, count = short[0]
        raise SystemExit(
            f"{batch}/{file} holds {count} shots of the {wanted[file]} requested ({len(short)} lists short); "
            "the preregistered stop applies and no cell is computed"
        )


def analyze(run_dirs: list[Path]) -> dict[str, Any]:
    return analyze_series(*load_series(run_dirs))


# A retained analysis keeps the bytes its writer's interpreter produced, because series-gate.json binds
# the control analysis by sha256; numpy builds of one version differ across interpreters in the last
# bits of a float, so a replay accepts equal structure, equal non-float values and floats within REPLAY_RTOL.
REPLAY_RTOL = 1e-12


def replay_mismatch(retained: Any, recomputed: Any, where: str) -> str | None:
    """The first path at which recomputed departs from retained beyond float rounding, or None."""
    if isinstance(retained, float) and isinstance(recomputed, float):
        return None if math.isclose(retained, recomputed, rel_tol=REPLAY_RTOL, abs_tol=REPLAY_RTOL) else where
    if type(retained) is not type(recomputed):
        return where
    if isinstance(retained, dict):
        if list(retained) != list(recomputed):
            return where
        for key in retained:
            found = replay_mismatch(retained[key], recomputed[key], f"{where}.{key}")
            if found:
                return found
        return None
    if isinstance(retained, list):
        if len(retained) != len(recomputed):
            return where
        for index, (left, right) in enumerate(zip(retained, recomputed, strict=True)):
            found = replay_mismatch(left, right, f"{where}[{index}]")
            if found:
                return found
        return None
    return None if retained == recomputed else where


def analyze_series(cases: dict[str, Any], raw: dict[tuple[str, str], list[str]], batch_of: dict[str, str]) -> dict:
    claim = claim_kind(cases)
    width = cases["nqubits"]
    require_full_shots(cases, raw)
    # The stops come first: a fired stop invalidates every inference, so the record then holds the references
    # and the shot counts only, and no inversion of a possibly singular assignment matrix is attempted.
    references = reference_report(cases, raw)
    stopped = bool(references["stop_condition_batch_00"]) or bool(references["bracket_drift"]["flagged"])
    if stopped:
        return {
            "schema": "qi-bdsc-pauli-analysis-v3",
            "claim_kind": STOPPED_CLAIM,
            "manifest_sha256": manifest_digest(cases),
            "references": references,
            "stop_condition_readout": references["stop_condition_batch_00"],
            "operational": [
                {"batch": batch, "file": file, "shots": len(shots)} for (batch, file), shots in sorted(raw.items())
            ],
            "cells": None,
            "contraction": None,
            "quadrature": None,
        }
    context_qubits = sorted({e["qubit"] for e in references["neighbor_context"] if e["e01_flag"] or e["e10_flag"]})
    g, parity = score_vector(), parity_vector()
    bank_ideal = {row["name"]: row["ideal_score"] for row in cases["bank"]}
    group = {row["name"]: row["group"] for row in cases["bank"]}
    bits_cache: dict[tuple[str, str], np.ndarray] = {}

    def bits_of(key: tuple[str, str]) -> np.ndarray:
        if key not in bits_cache:
            bits_cache[key] = shot_bits(raw[key], width, "/".join(key))
        return bits_cache[key]

    def joint_counts(bits: np.ndarray, qubits: tuple[int, ...]) -> np.ndarray:
        codes = np.zeros(len(bits), dtype=np.int64)
        for q in qubits:
            codes = codes << 1 | bits[:, width - 1 - q].astype(np.int64)
        return np.bincount(codes, minlength=16)

    cells: list[dict[str, Any]] = []
    shot_scores: dict[tuple[str, int], np.ndarray] = {}
    tasks: list[tuple[Any, ...]] = []
    task_cell: list[int] = []
    for witness in cases["witnesses"]:
        file = witness["file"]
        if file not in batch_of:
            raise SystemExit(f"the series lacks the batch holding {file}; analyze every batch together")
        batch = batch_of[file]
        pairing = cases["readout_pairing"][batch]
        keys = {name: (owner, name) for name, owner in pairing.items()}
        if any(key not in raw for key in keys.values()):
            raise SystemExit(f"batch {batch!r} holding {file} lacks the readout references {pairing}")
        ref0, ref1 = bits_of(keys[READOUT_ZERO]), bits_of(keys[READOUT_ONE])
        bits = bits_of((batch, file))
        for row in witness["patches"]:
            q3, q1, q0, q2 = row["qubits"]
            order = (q3, q2, q1, q0)
            counts = joint_counts(bits, order)
            b3, bz, b1, b0 = (bits[:, width - 1 - q].astype(int) for q in order)
            n = len(bits)
            freq = (counts / n).tolist()
            ref0_counts, ref1_counts = joint_counts(ref0, order), joint_counts(ref1, order)
            e01, e10 = joint_rates(ref0_counts / ref0_counts.sum(), ref1_counts / ref1_counts.sum())
            rates = [(float(a), float(b)) for a, b in zip(e01, e10, strict=True)]
            t = (1 - 2 * b3) * (1 - 2 * b1) * (1 - 2 * b0)
            flagged = sorted(set(order) & set(context_qubits))
            cell: dict[str, Any] = {
                "kind": witness["kind"],
                "state": row["state"],
                "group": group[row["state"]],
                "patch": row["patch"],
                "batch": batch,
                "source_batch": row["source_batch"],
                "file": file,
                "shots": n,
                "shots_requested": cases["shots"],
                "parity_mean": float(t.mean()),
                "parity_variance": float(t.var(ddof=1)),
                "tensor_model_rejected_by_context": flagged,
                "parity_tensor_model_mitigated": None if flagged else corrected_expectation(freq, rates, parity),
            }
            if witness["kind"] == "witness":
                scores = g[b3 << 3 | bz << 2 | b1 << 1 | b0]
                shot_scores[(file, row["patch"])] = scores
                kernel = int(np.count_nonzero((bz == 1) & (t == 1)))
                cell |= {
                    "ideal_score": bank_ideal[row["state"]],
                    "score_mean": float(scores.mean()),
                    "score_variance": float(scores.var(ddof=1)),
                    "score_ci95_empirical_bernstein": eb_interval(scores),
                    "kernel_count": kernel,
                    "kernel_fraction": kernel / n,
                    "kernel_ci95_wilson": wilson(kernel, n),
                    "score_tensor_model_mitigated": None if flagged else corrected_expectation(freq, rates, g),
                    "score_tensor_model_ci95_jeffreys": None,
                }
                if not flagged:
                    tasks.append(
                        (
                            tuple(int(c) for c in counts),
                            tuple(int(c) for c in ref0_counts),
                            tuple(int(c) for c in ref1_counts),
                            len(tasks),
                        )
                    )
                    task_cell.append(len(cells))
            else:
                cell |= {"ideal_parity": row["ideal_parity"], "quadrature": row["quadrature"]}
            cells.append(cell)
    intervals = parallel.ordered_map(BootstrapCell(g, BOOTSTRAP_DRAWS), tasks, min_items=8)
    for index, interval in zip(task_cell, intervals, strict=True):
        cells[index]["score_tensor_model_ci95_jeffreys"] = interval
    patches = sorted({c["patch"] for c in cells})
    contraction_out = contraction(cells, patches, shot_scores)
    quadrature_out = quadrature(cells, patches)
    primary = [
        {"test": f"pair chi-square, {name}", **row["pairs_chi2"]}
        for name, row in contraction_out.items()
        if name.startswith("patch") and row["pairs_chi2"] is not None
    ] + [
        {"test": f"branch phase, {name}", "z": row["phi_z_against_zero"], "flag": row["phase_flag"]}
        for name, row in quadrature_out.items()
    ]
    out: dict[str, Any] = {
        "schema": "qi-bdsc-pauli-analysis-v3",
        "claim_kind": claim,
        "manifest_sha256": manifest_digest(cases),
        "bootstrap": {"draws": BOOTSTRAP_DRAWS, "seed": BOOTSTRAP_SEED, "alpha": ALPHA, "prior": "Jeffreys"},
        "tensor_model_rejected_on_qubits": context_qubits,
        "cells": cells,
        "references": references,
        "stop_condition_readout": references["stop_condition_batch_00"],
        "contraction": contraction_out,
        "quadrature": quadrature_out,
        "primary_endpoints": {
            "family": PREREGISTERED["multiplicity"],
            "tests": primary,
            "rejects_model": any(t["flag"] for t in primary),
        },
    }
    if claim == "emulator control" or cases.get("twin_of"):
        out["control_verdict"] = control_verdict(cells, quadrature_out)
    return out


def control_verdict(cells: list[dict[str, Any]], quadrature_out: dict[str, Any]) -> dict[str, Any]:
    """Pass when every witness cell's empirical-Bernstein interval holds its ideal score, every quadrature
    and cosine cell's parity lies within Z_FLAG standard errors of its ideal (exactly on it at zero
    variance), and every patch reads its branch phase within Z_FLAG standard errors of zero."""
    misses = []
    for c in cells:
        if c["kind"] == "witness":
            low, high = c["score_ci95_empirical_bernstein"]
            if not low - 1e-12 <= c["ideal_score"] <= high + 1e-12:
                misses.append(f"{c['file']} patch {c['patch']} {c['state']} score {c['score_mean']}")
        else:
            se = math.sqrt(c["parity_variance"] / c["shots"])
            if abs(c["parity_mean"] - c["ideal_parity"]) > Z_FLAG * se + 1e-12:
                misses.append(f"{c['file']} patch {c['patch']} {c['state']} parity {c['parity_mean']}")
    for name, row in quadrature_out.items():
        if row["phase_flag"] or row["phi_rad"] is None:
            misses.append(f"{name} phase {row['phi_rad']}")
    return {"pass": not misses, "misses": misses}


def reference_report(cases: dict[str, Any], raw: dict[tuple[str, str], list[str]]) -> dict[str, Any]:
    """Assignment rates of every loaded reference, the batch-00 stop test, bracket drift and neighbor context."""
    width = cases["nqubits"]
    qubits = cases["patch_qubits"]
    x_sets = cases["references"]
    instances = sorted((batch, file) for (batch, file) in raw if file in x_sets)
    bits = {key: shot_bits(raw[key], width, "/".join(key)) for key in instances}
    rows: list[dict[str, Any]] = []
    for batch, file in instances:
        flipped = set(x_sets[file])
        ones = {q: float(bits[(batch, file)][:, width - 1 - q].mean()) for q in qubits}  # P(read 1) of each patch qubit
        rows.append(
            {
                "batch": batch,
                "reference": file,
                "shots": len(bits[(batch, file)]),
                "p_read_1": ones,
                "prepared": {q: int(q in flipped) for q in qubits},
                "e01": {q: ones[q] for q in qubits if q not in flipped},
                "e10": {q: 1 - ones[q] for q in qubits if q in flipped},
            }
        )
    stop = []
    for q in qubits:
        for file, key in ((READOUT_ZERO, "e01"), (READOUT_ONE, "e10")):
            if any(r["reference"] == file and r["batch"] == "batch-00" for r in rows):
                value = next(r[key][q] for r in rows if r["reference"] == file and r["batch"] == "batch-00")
                if value > READOUT_STOP:
                    stop.append(
                        {"batch": "batch-00", "qubit": q, "reference": file, "rate": value, "threshold": READOUT_STOP}
                    )
    drift = []
    for file, key in ((READOUT_ZERO, "e01"), (READOUT_ONE, "e10")):
        series = [r for r in rows if r["reference"] == file]
        for before, after in zip(series, series[1:], strict=False):
            for q in qubits:
                delta = after[key][q] - before[key][q]
                drift.append(
                    {
                        "reference": file,
                        "from": before["batch"],
                        "to": after["batch"],
                        "qubit": q,
                        "rate_from": before[key][q],
                        "rate_to": after[key][q],
                        "delta": delta,
                        "flag": abs(delta) > DRIFT_STOP,
                    }
                )
    context = neighbor_context(cases, rows)
    return {
        "instances": rows,
        "stop_condition_batch_00": stop,
        "bracket_drift": {
            "threshold": DRIFT_STOP,
            "max_abs_delta": max((abs(d["delta"]) for d in drift), default=0.0),
            "flagged": [d for d in drift if d["flag"]],
            "pairs": drift,
        },
        "neighbor_context": context,
    }


def neighbor_context(cases: dict[str, Any], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Assignment of each coupled patch qubit given the neighbor's prepared bit, from the first loaded reference."""
    out = []
    x_sets = cases["references"]
    first: dict[str, dict[str, Any]] = {}
    for row in rows:
        first.setdefault(row["reference"], row)
    for u, v in cases["patch_couplers"]:
        for qubit, neighbor in ((u, v), (v, u)):
            found = {}
            for file, row in first.items():
                key = (int(qubit in x_sets[file]), int(neighbor in x_sets[file]))
                found[key] = row
            if len(found) < 4:
                continue

            def p(
                prepared: int, nb: int, qubit: int = qubit, found: dict[tuple[int, int], dict[str, Any]] = found
            ) -> tuple[float, int]:
                return found[(prepared, nb)]["p_read_1"][qubit], found[(prepared, nb)]["shots"]

            twins = sorted(
                w
                for a, b in cases["patch_couplers"]
                for w in ((b,) if a == qubit else (a,) if b == qubit else ())
                if w != neighbor and all((w in x) == (neighbor in x) for x in x_sets.values())
            )
            entry: dict[str, Any] = {"qubit": qubit, "neighbor": neighbor, "indistinguishable_neighbors": twins}
            for label, prepared in (("e01", 0), ("e10", 1)):
                values = []
                for nb in (0, 1):
                    p1, n = p(prepared, nb)
                    values.append((p1 if prepared == 0 else 1 - p1, n))
                (r0, n0), (r1, n1) = values
                variance = r0 * (1 - r0) / n0 + r1 * (1 - r1) / n1
                stat = statistic(r1 - r0, variance)
                entry |= {
                    f"{label}_neighbor_0": r0,
                    f"{label}_neighbor_1": r1,
                    f"{label}_shift": r1 - r0,
                    f"{label}_z": stat["z"],
                    f"{label}_flag": stat["flag"],
                }
            out.append(entry)
    return out


def pooled_variance(weights: dict[tuple[str, int], float], shot_scores: dict[tuple[str, int], np.ndarray]) -> float:
    """Variance of sum_c w_c mean(score_c) with the covariance of cells measured in the same shots.

    Cells of one circuit share its shots, so their means covary through the joint per-shot scores; cells
    of different circuits are independent runs. Each circuit contributes Var(sum_c w_c score_c) / n.
    """
    total = 0.0
    for file in sorted({f for f, _ in weights}):
        cols = [(p, w) for (f, p), w in sorted(weights.items()) if f == file]
        stack = np.array([shot_scores[(file, p)] for p, _ in cols])
        cov = np.atleast_2d(np.cov(stack, ddof=1))
        w = np.array([w for _, w in cols])
        total += float(w @ cov @ w) / stack.shape[1]
    return total


def contraction(
    cells: list[dict[str, Any]], patches: list[int], shot_scores: dict[tuple[str, int], np.ndarray]
) -> dict[str, Any]:
    witness = [c for c in cells if c["kind"] == "witness"]
    out: dict[str, Any] = {}
    pooled_patch = []
    patch_weights: dict[tuple[str, int], float] = {}
    for p in patches:
        mine = [c for c in witness if c["patch"] == p]
        by = {(c["source_batch"], c["state"]): c for c in mine}
        pairs = []
        for batch in sorted({c["source_batch"] for c in mine}):
            for n in range(1, len(bdsc.KERNEL_PAIRS) + 1):
                k, b = by.get((batch, f"k{n}")), by.get((batch, f"b{n}"))
                if k is None or b is None:
                    continue
                variance = k["score_variance"] / k["shots"] + b["score_variance"] / b["shots"]
                pairs.append({"pair": n, "batch": batch, **statistic(k["score_mean"] + b["score_mean"] - 1, variance)})
        singles = [
            {"state": c["state"], **statistic(c["score_mean"] - 0.5, c["score_variance"] / c["shots"])}
            for c in sorted(mine, key=lambda c: c["state"])
            if c["state"] in {"e0", "e10", "e7", "e12"}
        ]
        pooled = None
        if pairs:
            variance = sum(r["se"] ** 2 for r in pairs) / len(pairs) ** 2
            pooled = statistic(sum(r["residual"] for r in pairs) / len(pairs), variance)
            pooled_patch.append(pooled)
            for pair in pairs:
                for state in (f"k{pair['pair']}", f"b{pair['pair']}"):
                    cell = by[(pair["batch"], state)]
                    key = (cell["file"], p)
                    patch_weights[key] = patch_weights.get(key, 0.0) + 1 / len(pairs) / len(patches)
        pairs_chi2 = None
        if pairs:
            from scipy.stats import chi2 as chi2_law

            total = sum(r["z"] ** 2 if r["z"] is not None else (math.inf if r["residual"] else 0.0) for r in pairs)
            threshold = float(chi2_law.isf(PRIMARY_P, len(pairs)))
            pairs_chi2 = {"chi2": total, "dof": len(pairs), "threshold": threshold, "flag": total >= threshold}
        out[f"patch-{p}"] = {
            "pairs_kernel_plus_bright_minus_one": pairs,
            "pairs_chi2": pairs_chi2,
            "pooled_kernel_plus_bright_minus_one": pooled,
            "middle_sector_minus_half": singles,
            "rejects_model": bool(pairs_chi2 and pairs_chi2["flag"]),
            "exploratory_flags": sum(bool(r["flag"]) for r in [*pairs, *singles, *([pooled] if pooled else [])]),
        }
    if len(pooled_patch) == len(patches):
        residual = sum(r["residual"] for r in pooled_patch) / len(patches)
        marginal = sum(r["se"] ** 2 for r in pooled_patch) / len(patches) ** 2
        variance = pooled_variance(patch_weights, shot_scores)
        out["pooled_equal_patch_weights"] = {
            "estimand": "equal-weight mean over the patches of the per-patch pooled kernel + bright - 1",
            "variance_includes": "covariance of the patches' per-shot scores within each circuit",
            "se_marginal_only": math.sqrt(marginal),
            **statistic(residual, variance),
        }
    return out


def quadrature(cells: list[dict[str, Any]], patches: list[int]) -> dict[str, Any]:
    """Branch phase of each patch from the matched X-basis (quadrature) and Y-basis (cosine) circuits of k1 and b1.

    S and C come from circuits that prepare the same state on every patch in the same batch, so they share
    one visibility. The phase is defined only when the (S, C) amplitude rejects zero (VISIBILITY_CHI2); its
    standard error is the delta-method value, accurate once the amplitude is many standard errors from zero.
    The witnesses' own cosine amplitude, measured with other states on the neighboring patches, is compared
    with C as an exploratory check of how far neighbor context moves the visibility.
    """
    out: dict[str, Any] = {}
    for p in patches:

        def find(kind: str, state: str, p: int = p) -> dict[str, Any] | None:
            hits = [c for c in cells if c["kind"] == kind and c["patch"] == p and c["state"] == state]
            return hits[0] if len(hits) == 1 else None

        kx, bx, ex = find("quadrature", "k1"), find("quadrature", "b1"), find("quadrature", "e7")
        ky, by = find("cosine", "k1"), find("cosine", "b1")
        kw, bw = find("witness", "k1"), find("witness", "b1")
        if kx is None or bx is None or ex is None or ky is None or by is None:
            continue

        def var(c: dict[str, Any]) -> float:
            return c["parity_variance"] / c["shots"]

        sin_sign = (kx["quadrature"]["sin_coefficient"], bx["quadrature"]["sin_coefficient"])
        cos_sign = (ky["quadrature"]["cos_coefficient"], by["quadrature"]["cos_coefficient"])
        require(sin_sign == (-1.0, 1.0), f"quadrature coefficients of k1, b1 are {sin_sign}")
        require(cos_sign == (1.0, -1.0), f"cosine coefficients of k1, b1 are {cos_sign}")
        s_amp = (bx["parity_mean"] - kx["parity_mean"]) / 2
        c_amp = (ky["parity_mean"] - by["parity_mean"]) / 2
        var_s = (var(kx) + var(bx)) / 4
        var_c = (var(ky) + var(by)) / 4
        chi2 = (s_amp * s_amp / var_s if var_s > 0 else (math.inf if s_amp else 0.0)) + (
            c_amp * c_amp / var_c if var_c > 0 else (math.inf if c_amp else 0.0)
        )
        supported = chi2 >= VISIBILITY_CHI2
        norm = s_amp * s_amp + c_amp * c_amp
        phi: float | None = None
        phase: dict[str, Any] = {"se": None, "z": None, "flag": False}
        mitigated: float | None = None
        if supported:
            phi = math.atan2(s_amp, c_amp)
            phase = statistic(phi, (c_amp * c_amp * var_s + s_amp * s_amp * var_c) / (norm * norm))
            parts = [c["parity_tensor_model_mitigated"] for c in (kx, bx, ky, by)]
            if all(v is not None for v in parts):
                mitigated = math.atan2((parts[1] - parts[0]) / 2, (parts[2] - parts[3]) / 2)
        nulls = {
            "x_basis_half_sum": statistic((kx["parity_mean"] + bx["parity_mean"]) / 2, (var(kx) + var(bx)) / 4),
            "y_basis_half_sum": statistic((ky["parity_mean"] + by["parity_mean"]) / 2, (var(ky) + var(by)) / 4),
            "e7_parity": statistic(ex["parity_mean"], var(ex)),
        }
        context = None
        if kw is not None and bw is not None:
            c_wit = (kw["parity_mean"] - bw["parity_mean"]) / 2
            context = statistic(c_wit - c_amp, (var(kw) + var(bw)) / 4 + var_c)
        out[f"patch-{p}"] = {
            "sin_phi_times_v": s_amp,
            "cos_phi_times_v": c_amp,
            "v": math.hypot(s_amp, c_amp),
            "amplitude_chi2": chi2,
            "visibility_supported": supported,
            "phi_rad": phi,
            "phi_se": phase["se"],
            "phi_z_against_zero": phase["z"],
            "phase_flag": bool(phase["flag"]),
            "phi_tensor_model_mitigated_rad": mitigated,
            "nulls": nulls,
            "witness_cos_minus_matched_cos": context,
            "exploratory_flags": sum(bool(n["flag"]) for n in nulls.values()) + int(bool(context and context["flag"])),
        }
    return out


# --- series gate ----------------------------------------------------------------------------------


def manifest_digest(cases: dict[str, Any]) -> str:
    """sha256 of the canonical JSON of a manifest's shared fields: the identity of one series design."""
    shared = {k: v for k, v in cases.items() if k not in {"batch", "circuits", "schema", "control", "simulator"}}
    return hashlib.sha256(json.dumps(shared, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def series_runs(series_dir: Path, runs: Path) -> tuple[str | None, dict[str, Path]]:
    """The UTC stamp every run directory of the series shares, and the run directory of each submitted batch."""
    found: dict[str, Path] = {}
    stamps = set()
    for path in sorted(runs.glob(f"*-{series_dir.name}-batch-*")):
        stamp, _, batch = path.name.partition(f"-{series_dir.name}-")
        if batch in found:
            raise SystemExit(f"{batch} of {series_dir.name} has two run directories")
        found[batch] = path
        stamps.add(stamp)
    if len(stamps) > 1:
        raise SystemExit(f"run directories of {series_dir.name} carry several stamps {sorted(stamps)}")
    return (stamps.pop() if stamps else None), found


def gate_predecessor(case_batch: Path, run_dir: Path) -> dict[str, Any]:
    """A submitted batch passes when its retained case bytes equal the series' and every job completed
    with its raw shot list; returns the digests the receipt binds."""
    for row in json.loads((case_batch / "cases.json").read_text(encoding="utf-8"))["circuits"]:
        if file_sha256(run_dir / row["file"]) != row["sha256"]:
            raise SystemExit(f"{run_dir}/{row['file']} differs from the series case")
    if file_sha256(run_dir / "cases.json") != file_sha256(case_batch / "cases.json"):
        raise SystemExit(f"{run_dir}/cases.json differs from {case_batch}/cases.json")
    results_path = run_dir / "results.json"
    if not results_path.exists():
        raise SystemExit(f"{run_dir} is not collected; run qi_platform.py collect first")
    results = json.loads(results_path.read_text(encoding="utf-8"))
    raw = {}
    for row in results["jobs"]:
        if row["job"]["status"] != "completed":
            raise SystemExit(
                f"{run_dir}/{row['file']} job {row['job']['id']} is {row['job']['status']}: the series stops"
            )
        raw[row["file"]] = file_sha256(run_dir / "raw" / f"{row['file']}.json")
    return {"run_dir": run_dir.name, "results_sha256": file_sha256(results_path), "raw_sha256": raw}


def submit_next(
    series_dir: Path, runs: Path, approval: str, control: Path | None, dry: bool = False
) -> tuple[Path, dict[str, Any]]:
    """Copy the next batch of a series into its run directory and submit it, after every preregistered stop.

    Every earlier batch must be submitted, collected with all jobs completed and full shot lists, and
    byte-equal to the series case; the batch-00 assignment stop and the bracket-drift stop are evaluated
    over the collected references; a Tuna-17 series needs the QX control analysis of its twin with a
    passing verdict before its first batch; and the live backend's topology, gate set and default compiler
    configuration must match the digests the cases were built against. The run directory's
    series-gate.json binds the predecessors' result and raw digests.
    """
    import datetime

    import qi_platform

    names = [row["batch"] for row in json.loads((series_dir / "cases.json").read_text(encoding="utf-8"))["batches"]]
    first = json.loads((series_dir / names[0] / "cases.json").read_text(encoding="utf-8"))
    stamp, done = series_runs(series_dir, runs)
    pending = [name for name in names if name not in done]
    if not pending:
        raise SystemExit(f"every batch of {series_dir.name} is submitted")
    following = names[names.index(pending[0]) :]
    if any(name in done for name in following):
        raise SystemExit(f"{series_dir.name}: a later batch was submitted before {pending[0]}")
    batch = pending[0]
    predecessors = [
        {"batch": name, **gate_predecessor(series_dir / name, done[name])} for name in names if name in done
    ]
    stops: dict[str, Any] = {"batches_checked": [p["batch"] for p in predecessors]}
    if predecessors:
        cases, raw, _ = load_series([done[p["batch"]] for p in predecessors])
        require_full_shots(cases, raw)
        report = reference_report(cases, raw)
        if report["stop_condition_batch_00"] or report["bracket_drift"]["flagged"]:
            raise SystemExit(
                f"a preregistered stop fired: batch-00 {report['stop_condition_batch_00']}, "
                f"drift {report['bracket_drift']['flagged']}; the series stops"
            )
        stops |= {
            "stop_condition_batch_00": [],
            "bracket_drift_flagged": [],
            "max_drift": report["bracket_drift"]["max_abs_delta"],
        }
    control_record = None
    if "twin_of" not in first:
        twin_first = series_dir.parent / TWIN_SERIES / "batch-00" / "cases.json"
        want = manifest_digest(json.loads(twin_first.read_text(encoding="utf-8")))
        if control is None:
            raise SystemExit("a Tuna-17 batch needs --control, the analysis of the collected QX twin")
        analysis = json.loads(control.read_text(encoding="utf-8"))
        # The remote twin exercises the platform's upload, raw-data and bit-order path; a local qxelarator run
        # (claim kind "emulator control") does not.
        if analysis.get("manifest_sha256") != want or analysis.get("claim_kind") != "preregistered emulator control":
            raise SystemExit(f"{control} is not the analysis of the remote {TWIN_SERIES} run")
        try:
            control_name = control.resolve().relative_to(ROOT).as_posix()
        except ValueError:
            raise SystemExit(f"{control} lies outside the repository; retain the twin's analysis first") from None
        if not analysis.get("control_verdict", {}).get("pass"):
            raise SystemExit(f"the QX control missed its ideal: {analysis.get('control_verdict')}")
        control_record = {"file": control_name, "sha256": file_sha256(control), "manifest_sha256": want}
    client = qi_platform.Client()
    live = client.get(f"/backend_types/{first['backend_type_id']}")
    if backend_contract(live) != first["backend_contract"]:
        raise SystemExit(
            f"{live['name']}: the live topology, gate set or compiler configuration differs from the cases"
        )
    stamp = stamp or datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H%M%SZ")
    run_dir = runs / f"{stamp}-{series_dir.name}-{batch}"
    receipt = {
        "schema": "qi-bdsc-pauli-gate-v1",
        "series": series_dir.name,
        "batch": batch,
        "cases_sha256": file_sha256(series_dir / batch / "cases.json"),
        "predecessors": predecessors,
        "stops": stops,
        "control": control_record,
        "backend_contract": "live record matches",
        "pause_seconds": qi_platform.HARDWARE_PAUSE_SECONDS if live["is_hardware"] else 0,
    }
    if dry:
        return run_dir, receipt
    import shutil
    import time

    if live["is_hardware"]:
        # hardware_pause_left refuses while any hardware job of the account is unfinished.
        while (left := qi_platform.hardware_pause_left(client)) > 0:
            time.sleep(left + 1)
    shutil.copytree(series_dir / batch, run_dir)
    (run_dir / "series-gate.json").write_text(json.dumps(receipt, indent=1) + "\n", encoding="utf-8")
    try:
        record = qi_platform.submit(run_dir, first["backend_type_id"], approval)
    except BaseException:
        # A refusal or a transport failure before the checkpoint leaves nothing on the service; the copy
        # goes so the next call does not read an unsent batch as submitted.
        if not (run_dir / "submission-state.json").exists():
            shutil.rmtree(run_dir)
        raise
    print(f"{run_dir.name}: batch {record['batch_job']}, jobs {[row['job'] for row in record['jobs']]}")
    return run_dir, receipt


# --- self-test ------------------------------------------------------------------------------------


def flip_bits(columns: np.ndarray, flips: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Apply the assignment errors: a 0 reads 1 with flips[q, 0] and a 1 reads 0 with flips[q, 1] per column q."""
    u = rng.random(columns.shape)
    return np.where(columns == 0, (u < flips[:, 0]).astype(np.uint8), (u >= flips[:, 1]).astype(np.uint8))


def synthetic_series(
    files: dict[str, str],
    distribution: Callable[[str, str], np.ndarray],
    flips: tuple[float, float],
    seed: int,
    shots: int = SHOTS,
    ref_shots: int | None = None,
    ref_flips: dict[tuple[str, str], dict[int, tuple[float, float]]] | None = None,
    neighbor_bias: tuple[int, int, float] | None = None,
    common_flip: float = 0.0,
) -> tuple[dict[str, Any], dict[tuple[str, str], list[str]], dict[str, str]]:
    """Shots of a written series for per-state outcome distributions and a readout flip pair (e01, e10).

    distribution(state, kind) gives P(code) over the 16 outcomes of one patch in a witness or quadrature
    circuit; patches are independent, qubits outside the patches read the flips of an idle qubit, and each
    reference flips its x_qubits before the readout flips. ref_flips overrides the flips of single qubits in
    one reference (batch, file); neighbor_bias (u, v, delta) adds delta to P(read 1) of a qubit u prepared 0
    while the coupled qubit v is prepared 1, in references only; common_flip flips the z2 outcome of every
    patch of a circuit together in that fraction of shots, a noise shared by the patches of one circuit.
    """
    rng = np.random.default_rng(seed)
    batches = json.loads(files["cases.json"])["batches"]
    manifests = [json.loads(files[f"{b['batch']}/cases.json"]) for b in batches]
    cases = {k: v for k, v in manifests[0].items() if k not in {"batch", "circuits", "schema"}}
    width = cases["nqubits"]
    cases["shots"] = shots
    if ref_shots:
        cases["reference_shots"] = ref_shots

    def strings(matrix: np.ndarray) -> list[str]:
        return [row.tobytes().decode("ascii") for row in np.ascontiguousarray(matrix + 48).view(f"S{width}")]

    raw: dict[tuple[str, str], list[str]] = {}
    batch_of: dict[str, str] = {}
    witnesses = {w["file"]: w for w in cases["witnesses"]}
    for manifest in manifests:
        batch = manifest["batch"]
        for row in manifest["circuits"]:
            table = np.tile(np.array(flips, dtype=float), (width, 1))
            for q, pair in (ref_flips or {}).get((batch, row["file"]), {}).items():
                table[width - 1 - q] = pair
            if row["kind"] == "readout":
                count = ref_shots or shots
                prepared = np.zeros(width, dtype=np.uint8)
                prepared[row["x_qubits"]] = 1
                matrix = flip_bits(np.tile(prepared[::-1], (count, 1)), table, rng)
                if neighbor_bias is not None:
                    u, v, delta = neighbor_bias
                    if prepared[u] == 0 and prepared[v] == 1:
                        extra = rng.random(count) < delta
                        matrix[:, width - 1 - u] |= extra.astype(np.uint8)
                raw[(batch, row["file"])] = strings(matrix)
                continue
            batch_of[row["file"]] = batch
            matrix = np.zeros((shots, width), dtype=np.uint8)
            shared_flip = (rng.random(shots) < common_flip).astype(np.int64) << 2
            for entry in witnesses[row["file"]]["patches"]:
                q3, q1, q0, q2 = entry["qubits"]
                counts = rng.multinomial(shots, distribution(entry["state"], row["kind"]))
                codes = rng.permutation(np.repeat(np.arange(16), counts)) ^ shared_flip
                for position, q in zip((3, 2, 1, 0), (q3, q2, q1, q0), strict=True):
                    matrix[:, width - 1 - q] = codes >> position & 1
            raw[(batch, row["file"])] = strings(flip_bits(matrix, table, rng))
    return cases, raw, batch_of


def branch_phase_state(name: str, theta: float) -> np.ndarray:
    """Bank state with a phase e^{i theta} on the q3 = 1 branch, which is the ~a branch of every pair."""
    phase = np.exp(1j * theta * np.array([j >> 3 & 1 for j in range(16)]))
    return phase * state_vector(ENTRY[name])


def verify_quadrature_derivation() -> str:
    """Statevector check of the closed forms for <Y3 X1 Y0> and <X3 X1 Y0> with a branch phase on q3."""
    from qiskit.quantum_info import Statevector

    weights = parity_vector()
    worst = 0.0
    for name in ("k1", "b1", "k2", "b2", "k3", "b3", "k4", "b4", "e7", "e12", "e0", "e10"):
        coefficients = quadrature_expectation(name)
        for theta in (-1.2, -0.35, 0.0, 0.1, 0.5, 2.0):
            for ops, expected in (
                (READOUT_OPS, coefficients["cos_coefficient"] * math.cos(theta)),
                (QUADRATURE_OPS, coefficients["sin_coefficient"] * math.sin(theta)),
            ):
                from qiskit import QuantumCircuit

                qc = QuantumCircuit(4)
                for gate, qs in prep_ops(ENTRY[name]):
                    getattr(qc, gate)(*qs)
                qc.p(theta, 3)
                qc.compose(qiskit_circuit(ops, 4), inplace=True)
                probs = Statevector(qc).probabilities([0, 1, 2, 3])
                value = float(weights @ probs)
                worst = max(worst, abs(value - expected))
                if abs(value - expected) > 1e-12:
                    raise AssertionError(f"{name} phi={theta}: parity {value}, closed form {expected}")
    return f"max |Statevector - closed form| {worst:.1e}"


def series_gate_self_test(
    files: dict[str, str], twin: dict[str, str], synthetic: Callable[..., Any], ideal: Callable[[str, str], np.ndarray]
) -> None:
    """--submit-next refuses each preregistered stop and an out-of-order or uncollected series, offline.

    qi_platform.Client is replaced by the retained catalogue record, and every call uses dry=True, so the
    test sends nothing and writes only under a temporary directory.
    """
    import shutil
    import tempfile

    import qi_platform

    backend = catalogue_check()[0]

    class Catalogue:
        def get(self, path: str, **_: Any) -> dict[str, Any]:
            return backend

    def write(root: Path, tree: dict[str, str]) -> None:
        for relative, text in tree.items():
            (root / relative).parent.mkdir(parents=True, exist_ok=True)
            (root / relative).write_text(text, encoding="utf-8")

    def refused(call: Callable[[], Any], words: str) -> None:
        try:
            call()
        except SystemExit as exc:
            if words not in str(exc):
                raise AssertionError(f"the gate refused for another reason: {exc}") from exc
        else:
            raise AssertionError(f"the gate passed where it must refuse ({words})")

    saved, saved_root = qi_platform.Client, ROOT
    qi_platform.Client = Catalogue  # type: ignore[misc,assignment]
    try:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            # The receipt names the control relative to the repository root; the test's root is the temporary one.
            globals()["ROOT"] = root
            series, twin_dir, runs = root / "cases" / SERIES, root / "cases" / TWIN_SERIES, root / "runs"
            write(series, files)
            write(twin_dir, twin)
            runs.mkdir()
            twin_shots = json.loads(twin["batch-00/cases.json"])["shots"]
            control = root / "control.json"
            control.write_text(json.dumps(analyze_series(*synthetic(twin, ideal, (0.0, 0.0), 21, twin_shots))))
            refused(lambda: submit_next(series, runs, "", None, True), "needs --control")
            local = root / "local.json"
            local.write_text(json.dumps({**json.loads(control.read_text()), "claim_kind": "emulator control"}))
            refused(lambda: submit_next(series, runs, "", local, True), "remote")
            submit_next(series, runs, "", control, True)

            def collect(batch: str, flips: dict[tuple[str, str], dict[int, tuple[float, float]]], status: str) -> Path:
                run_dir = runs / f"2026-10-22T000000Z-{SERIES}-{batch}"
                shutil.copytree(series / batch, run_dir)
                _, raw, _ = synthetic(files, ideal, (0.02, 0.04), 22, SHOTS, ref_flips=flips)
                (run_dir / "raw").mkdir()
                jobs = []
                for n, row in enumerate(json.loads((run_dir / "cases.json").read_text())["circuits"]):
                    (run_dir / "raw" / f"{row['file']}.json").write_text(json.dumps(raw[(batch, row["file"])]))
                    jobs.append({"file": row["file"], "job": {"id": n, "status": status if n == 0 else "completed"}})
                (run_dir / "results.json").write_text(json.dumps({"jobs": jobs}))
                return run_dir

            done = collect("batch-00", {}, "completed")
            receipt_dir, _ = submit_next(series, runs, "", control, True)
            if receipt_dir.name != f"2026-10-22T000000Z-{SERIES}-batch-01":
                raise AssertionError(f"the gate chose {receipt_dir.name}")
            # A transport failure before the checkpoint removes the copied batch; one after it keeps the copy.
            for checkpoint in (False, True):

                def failing_submit(run_dir: Path, *_: Any, checkpoint: bool = checkpoint) -> dict[str, Any]:
                    if checkpoint:
                        (run_dir / "submission-state.json").write_text("{}", encoding="utf-8")
                    raise OSError("synthetic transport failure")

                saved_submit, saved_pause = qi_platform.submit, qi_platform.hardware_pause_left
                qi_platform.submit, qi_platform.hardware_pause_left = failing_submit, lambda _: 0  # type: ignore[assignment]
                try:
                    submit_next(series, runs, "synthetic", control, False)
                except OSError:
                    pass
                else:
                    raise AssertionError("a failing submit returned")
                finally:
                    qi_platform.submit, qi_platform.hardware_pause_left = saved_submit, saved_pause
                if receipt_dir.exists() != checkpoint:
                    raise AssertionError(
                        f"a submit failing with checkpoint {checkpoint} left exists={receipt_dir.exists()}"
                    )
            shutil.rmtree(receipt_dir)
            shutil.rmtree(done)
            collect("batch-00", {("batch-00", READOUT_ONE): {13: (0.02, 0.2)}}, "completed")
            refused(lambda: submit_next(series, runs, "", control, True), "preregistered stop fired")
            shutil.rmtree(done)
            collect("batch-00", {}, "failed")
            refused(lambda: submit_next(series, runs, "", control, True), "the series stops")
            shutil.rmtree(done)
            collect("batch-01", {}, "completed")
            refused(lambda: submit_next(series, runs, "", control, True), "later batch was submitted")
            shutil.rmtree(runs / f"2026-10-22T000000Z-{SERIES}-batch-01")
            failing = json.loads(control.read_text())
            failing["control_verdict"] = {"pass": False, "misses": ["synthetic"]}
            control.write_text(json.dumps(failing))
            refused(lambda: submit_next(series, runs, "", control, True), "missed its ideal")
            backend = {**backend, "gateset": [*backend["gateset"], "extra"]}
            control.write_text(json.dumps({**failing, "control_verdict": {"pass": True}}))
            refused(lambda: submit_next(series, runs, "", control, True), "compiler configuration differs")
    finally:
        qi_platform.Client = saved  # type: ignore[misc]
        globals()["ROOT"] = saved_root


def self_test() -> None:
    all_files = build()
    files = all_files[SERIES]
    twin = all_files[TWIN_SERIES]
    ranking = select_placement(TUNA17)
    if ranking[0][3] != PLACEMENT:
        raise AssertionError(f"PLACEMENT is not the first of {len(ranking)} ranked placements")
    if ranking[0][0] != 0:
        raise AssertionError("the first placement holds a path with both q11 and q13")
    ideal = ideal_scores()
    entries = ENTRY

    # Native readout: spec matrices, R_n forms, U P U^dagger = Z, and the pauli_form.json outcome probabilities.
    rotations = native_rotation_check()
    if set(rotations) != {"x90", "my90"}:
        raise AssertionError("a native readout pulse was not verified")
    if np.allclose(X90 @ PAULI_MATRIX["X"] @ X90.conj().T, PAULI_MATRIX["Z"]):
        raise AssertionError("X90 should not map X to Z; the check cannot discriminate")
    if np.allclose(MY90 @ PAULI_MATRIX["Y"] @ MY90.conj().T, PAULI_MATRIX["Z"]):
        raise AssertionError("mY90 should not map Y to Z; the check cannot discriminate")

    # Group-patch balance: the plan passes, and a plan that repeats an index on a patch fails.
    tables = balance_tables()
    broken = list(WITNESS_PLAN)
    broken[3] = (2, 1, 4, "e12", "e10")
    try:
        balance_tables(tuple(broken))
    except ValueError:
        pass
    else:
        raise AssertionError("an unbalanced plan passed balance_tables")
    check_reference_sets(reference_sets())
    sets = reference_sets()
    bad = {**sets, CHECKER_Q: sets[CHECKER_P]}
    try:
        check_reference_sets(bad)
    except ValueError:
        pass
    else:
        raise AssertionError("duplicated checkerboards passed the coupler check")

    # Negative controls: a wrong sign or a wrong group value must be refused by the exact checks.
    from qiskit.quantum_info import Statevector

    wrong = Statevector(qiskit_circuit([op for op in prep_ops(entries["k2"]) if op[0] != "z"], 4)).data
    if abs(abs(np.vdot(state_vector(entries["k2"]), wrong)) - 1) < 1e-6:
        raise AssertionError("the preparation check cannot see a dropped Z correction")
    if abs(abs(np.vdot(state_vector(entries["b2"]), wrong)) - 1) > 1e-9:
        raise AssertionError("k2 without its Z correction should be b2")

    derivation = verify_quadrature_derivation()
    # With the Y-basis q3 readout a branch phase enters only at second order.
    theta = 0.05
    y_value = float(parity_vector() @ outcome_distribution(branch_phase_state("k1", theta)))
    x_value = float(parity_vector() @ outcome_distribution(branch_phase_state("k1", theta), QUADRATURE_BASIS))
    if not (abs(y_value - math.cos(theta)) < 1e-12 and abs(x_value + math.sin(theta)) < 1e-12):
        raise AssertionError("closed forms differ from the exact parities at phi = 0.05")
    if abs(1 - y_value) > 2 * theta**2 or abs(x_value) < 0.9 * theta:
        raise AssertionError("the quadrature circuit is not first order in the branch phase")

    def ideal_distribution(name: str, kind: str = "witness") -> np.ndarray:
        basis = QUADRATURE_BASIS if kind == "quadrature" else WITNESS_BASIS
        return outcome_distribution(state_vector(entries[name]), basis)

    def run(
        distribution: Callable[[str, str], np.ndarray],
        flips: tuple[float, float],
        seed: int,
        series: dict[str, str] = files,
        **kwargs: Any,
    ) -> dict[str, Any]:
        return analyze_series(*synthetic_series(series, distribution, flips, seed, kwargs.pop("shots", 8192), **kwargs))

    def cell_map(analysis: dict[str, Any], kind: str = "witness") -> dict[tuple[str, int, str], dict[str, Any]]:
        return {(c["state"], c["patch"], c["source_batch"]): c for c in analysis["cells"] if c["kind"] == kind}

    def coverage(analysis: dict[str, Any], want: Callable[[str], float]) -> float:
        hits = [
            c["score_tensor_model_ci95_jeffreys"][0] <= want(c["state"]) <= c["score_tensor_model_ci95_jeffreys"][1]
            for c in analysis["cells"]
            if c["kind"] == "witness"
        ]
        return sum(hits) / len(hits)

    def quiet(analysis: dict[str, Any]) -> bool:
        return not any(p["rejects_model"] for name, p in analysis["contraction"].items() if name.startswith("patch"))

    def phase_quiet(analysis: dict[str, Any]) -> bool:
        return not any(p["phase_flag"] or p["exploratory_flags"] for p in analysis["quadrature"].values())

    clean = run(ideal_distribution, (0.0, 0.0), 1)
    witness_cells = [c for c in clean["cells"] if c["kind"] == "witness"]
    if len(witness_cells) != 36 or len(clean["cells"]) != 51:
        raise AssertionError(f"{len(witness_cells)} witness cells and {len(clean['cells'])} cells")
    for cell in witness_cells:
        low, high = cell["score_ci95_empirical_bernstein"]
        if not low - 1e-12 <= ideal[cell["state"]] <= high + 1e-12:
            raise AssertionError(f"{cell['state']}: ideal shots read {cell['score_mean']}")
        if (
            abs(cell["score_mean"] - ideal[cell["state"]]) > 0.02
            or abs(cell["score_tensor_model_mitigated"] - ideal[cell["state"]]) > 0.02
        ):
            raise AssertionError(f"{cell['state']}: ideal shots read {cell['score_mean']}")
    if not quiet(clean) or not phase_quiet(clean) or clean["primary_endpoints"]["rejects_model"]:
        raise AssertionError("ideal shots violate the contraction law or the quadrature nulls")
    if any(abs(p["phi_rad"]) > 4 * p["phi_se"] for p in clean["quadrature"].values()) or len(clean["quadrature"]) != 3:
        raise AssertionError("ideal shots do not read phi = 0")
    refs = clean["references"]
    if (
        refs["stop_condition_batch_00"]
        or refs["bracket_drift"]["flagged"]
        or refs["bracket_drift"]["max_abs_delta"] != 0
    ):
        raise AssertionError("ideal references trip a stop condition")
    if coverage(clean, lambda s: ideal[s]) < 0.8:
        raise AssertionError("the corrected-score interval misses too many ideal cells")

    lam = 0.3
    uniform = np.full(16, 1 / 16)

    def depolarized(name: str, kind: str = "witness") -> np.ndarray:
        return (1 - lam) * ideal_distribution(name, kind) + lam * uniform

    contracted = run(depolarized, (0.0, 0.0), 2)
    for cell in cell_map(contracted).values():
        want = (1 - lam) * ideal[cell["state"]] + lam * 0.5
        if abs(cell["score_mean"] - want) > 0.02:
            raise AssertionError(f"{cell['state']}: depolarized score {cell['score_mean']}, expected {want}")
    if not quiet(contracted):
        raise AssertionError("a depolarizing contraction violates the contraction law")
    if any(abs(p["phi_rad"]) > 4 * p["phi_se"] for p in contracted["quadrature"].values()):
        raise AssertionError("a depolarizing contraction moves the branch phase")
    if any(abs(p["v"] - (1 - lam)) > 0.03 for p in contracted["quadrature"].values()):
        raise AssertionError("the quadrature visibility does not read the contraction")

    # An asymmetric assignment error moves single-bit reads while the parity residual stays within noise;
    # the assignment correction restores the depolarized values.
    biased = run(depolarized, (0.03, 0.08), 3)
    shifts = []
    for cell in cell_map(biased).values():
        want = (1 - lam) * ideal[cell["state"]] + lam * 0.5
        shifts.append(abs(cell["score_mean"] - want))
        if abs(cell["score_tensor_model_mitigated"] - want) > 0.02:
            raise AssertionError(
                f"{cell['state']}: mitigated score {cell['score_tensor_model_mitigated']}, expected {want}"
            )
    if max(shifts) < 0.02:
        raise AssertionError("the assignment error did not move any raw score")
    if coverage(biased, lambda s: (1 - lam) * ideal[s] + lam * 0.5) < 0.8:
        raise AssertionError("the corrected-score interval misses too many cells under an assignment error")

    # Coherent error: Rx(0.4) on q0 and q3 q1 jointly (exp(-i 0.2 X0) exp(-i 0.2 X3 X1)) after preparation.
    from scipy.linalg import expm

    unitary = expm(-0.2j * bdsc_pauli.word_matrix("IIIX")) @ expm(-0.2j * bdsc_pauli.word_matrix("XIXI"))

    def coherent(name: str, kind: str = "witness") -> np.ndarray:
        basis = QUADRATURE_BASIS if kind == "quadrature" else WITNESS_BASIS
        return outcome_distribution(unitary @ state_vector(entries[name]), basis)

    rotated = run(coherent, (0.0, 0.0), 4)
    if not all(p["rejects_model"] for name, p in rotated["contraction"].items() if name.startswith("patch")):
        raise AssertionError("a coherent error escaped the contraction law on some patch")
    first = rotated["contraction"]["patch-0"]["pairs_kernel_plus_bright_minus_one"]
    if max(abs(row["residual"]) for row in first) < 0.1:
        raise AssertionError("the coherent error did not move kernel + bright - 1")

    # Branch phase: a Z rotation of q3 alone. The contraction law stays silent (kernel and bright still sum to
    # one), the raw kernel score moves, and the quadrature batch recovers the phase on every patch.
    phase_theta = 0.35

    def dephased(name: str, kind: str = "witness") -> np.ndarray:
        basis = QUADRATURE_BASIS if kind == "quadrature" else WITNESS_BASIS
        return outcome_distribution(branch_phase_state(name, phase_theta), basis)

    phased = run(dephased, (0.0, 0.0), 6)
    if not quiet(phased):
        raise AssertionError("a pure branch phase violates the contraction law")
    kernel_shift = [
        c["score_mean"] - ideal[c["state"]]
        for c in phased["cells"]
        if c["kind"] == "witness" and c["state"].startswith("k")
    ]
    if min(kernel_shift) < 0.02:
        raise AssertionError("the branch phase did not move the kernel scores")
    for name, row in phased["quadrature"].items():
        if abs(row["phi_rad"] - phase_theta) > 4 * row["phi_se"] or row["phi_z_against_zero"] < Z_FLAG:
            raise AssertionError(f"{name}: phase {row['phi_rad']} against {phase_theta}")

    # Corrected-score interval: scalar closed form against a linear solve, batched path against scalar bits,
    # and reference noise widening the interval.
    rng = np.random.default_rng(11)
    freq = rng.dirichlet(np.ones(16)).tolist()
    rates = [(float(a), float(b)) for a, b in rng.uniform(0.0, 0.12, size=(4, 2))]
    full = np.ones((1, 1))
    for e01, e10 in rates:
        full = np.kron(full, np.array([[1 - e01, e10], [e01, 1 - e10]]))
    solved = np.linalg.solve(full, np.array(freq))
    if np.max(np.abs(np.array(unassign(freq, rates)) - solved)) > 1e-12:
        raise AssertionError("unassign differs from the linear solve")
    boot = BootstrapCell(score_vector(), 64)
    ref0_p: np.ndarray = np.ones(1)
    ref1_p: np.ndarray = np.ones(1)
    for _ in range(4):
        ref0_p = np.kron(ref0_p, [0.94, 0.06])
        ref1_p = np.kron(ref1_p, [0.045, 0.955])
    task = (
        tuple(int(x) for x in rng.multinomial(2000, freq)),
        tuple(int(x) for x in rng.multinomial(2000, ref0_p)),
        tuple(int(x) for x in rng.multinomial(2000, ref1_p)),
        5,
    )
    f_b, a_b, c_b = boot.replicates(task)
    batched = expectation_batch(score_vector(), unassign_batch(f_b, a_b, c_b))
    scalar = [
        corrected_expectation(f_b[i].tolist(), [(a_b[i, j], c_b[i, j]) for j in range(4)], score_vector())
        for i in range(len(f_b))
    ]
    if [float(x).hex() for x in batched] != [float(x).hex() for x in scalar]:
        raise AssertionError("the batched bootstrap differs from the scalar reference in its bits")
    # Short references widen the interval: one witness cell against references of 256 and of 32768 shots.
    witness_counts = tuple(int(x) for x in rng.multinomial(4096, freq))

    def ref_counts(shots: int, p: np.ndarray) -> tuple[int, ...]:
        return tuple(int(x) for x in np.round(p * shots).astype(int))

    def width(shots: int) -> float:
        low, high = BootstrapCell(score_vector(), 2000)(
            (witness_counts, ref_counts(shots, ref0_p), ref_counts(shots, ref1_p), 3)
        )
        return high - low

    if width(256) < 1.15 * width(32768):
        raise AssertionError("short readout references do not widen the corrected-score interval")

    # References: drift, a batch-00 breach, no-drift control and a neighbor-conditioned shift of q13 given q11.
    drifted = run(
        ideal_distribution,
        (0.02, 0.04),
        8,
        ref_flips={("batch-05", READOUT_ZERO): {8: (0.02 + 0.03, 0.04)}},
    )
    flagged = {(d["qubit"], d["reference"], d["to"]) for d in drifted["references"]["bracket_drift"]["flagged"]}
    if flagged != {(8, READOUT_ZERO, "batch-05"), (8, READOUT_ZERO, "batch-07")}:  # out of and back from the excursion
        raise AssertionError(f"drift flags {sorted(flagged)}")
    if drifted["claim_kind"] != STOPPED_CLAIM or drifted["contraction"] is not None:
        raise AssertionError("a series whose bracket drift stop fired kept its inference")
    steady = run(ideal_distribution, (0.02, 0.04), 8)
    if steady["references"]["bracket_drift"]["flagged"]:
        raise AssertionError("steady references trip the drift stop")
    if steady["claim_kind"] == STOPPED_CLAIM or steady["contraction"] is None:
        raise AssertionError("a series with no fired stop lost its inference")
    breach = run(ideal_distribution, (0.02, 0.04), 9, ref_flips={("batch-00", READOUT_ONE): {13: (0.02, 0.2)}})
    if [(r["qubit"], r["reference"]) for r in breach["stop_condition_readout"]] != [(13, READOUT_ONE)]:
        raise AssertionError(f"batch-00 breach read {breach['stop_condition_readout']}")
    if breach["claim_kind"] != STOPPED_CLAIM or breach["quadrature"] is not None:
        raise AssertionError("a series whose batch-00 stop fired kept its inference")
    later = run(ideal_distribution, (0.02, 0.04), 9, ref_flips={("batch-02", READOUT_ZERO): {13: (0.3, 0.04)}})
    if later["stop_condition_readout"]:
        raise AssertionError("a breach after batch-00 is reported as the batch-00 stop")
    contextual = run(ideal_distribution, (0.02, 0.04), 10, neighbor_bias=(13, 11, 0.04))
    shifts_flagged = [
        (e["qubit"], e["neighbor"])
        for e in contextual["references"]["neighbor_context"]
        if e["e01_flag"] or e["e10_flag"]
    ]
    if shifts_flagged != [(13, 10), (13, 11)]:  # q10 and q11 share one part, so the references cannot tell them apart
        raise AssertionError(f"context shifts {shifts_flagged}")
    if any(e["e01_flag"] or e["e10_flag"] for e in steady["references"]["neighbor_context"]):
        raise AssertionError("steady references show a context shift")

    # The QX twin analyzed noiselessly reads the same cells.
    twin_run = run(ideal_distribution, (0.0, 0.0), 12, series=twin)
    if len(twin_run["cells"]) != 51 or twin_run["claim_kind"] != "preregistered emulator control":
        raise AssertionError("the twin analysis lost cells")
    if not quiet(twin_run) or not phase_quiet(twin_run):
        raise AssertionError("the noiseless twin violates the contraction law or the nulls")
    if not twin_run["control_verdict"]["pass"]:
        raise AssertionError(f"the noiseless twin misses its control verdict: {twin_run['control_verdict']}")
    off = run(depolarized, (0.0, 0.0), 12, series=twin)
    if off["control_verdict"]["pass"]:
        raise AssertionError("a depolarized twin passed the control verdict")

    # The tensor model is withheld on every cell whose patch holds a context-flagged qubit (q13 sits on patch 1).
    withheld = {
        c["patch"] for c in contextual["cells"] if c["kind"] == "witness" and c["score_tensor_model_mitigated"] is None
    }
    if withheld != {1} or contextual["tensor_model_rejected_on_qubits"] != [13]:
        raise AssertionError(f"context withholding on patches {sorted(withheld)}")
    if any(c["score_tensor_model_mitigated"] is None for c in steady["cells"] if c["kind"] == "witness"):
        raise AssertionError("steady references withheld a mitigated score")

    # A stop fired by an assignment matrix too poor to invert returns the stop, not an inversion error.
    ruined = run(ideal_distribution, (0.02, 0.04), 9, ref_flips={("batch-00", READOUT_ONE): {13: (0.02, 0.6)}})
    if ruined["claim_kind"] != STOPPED_CLAIM or ruined["cells"] is not None:
        raise AssertionError("a singular batch-00 reference escaped the stop")

    # Visibility differing between the witnesses and the matched quadrature circuits: the matched phase
    # stays unbiased and the context comparison flags the witnesses' cosine amplitude.
    def unmatched(name: str, kind: str = "witness") -> np.ndarray:
        basis = QUADRATURE_BASIS if kind == "quadrature" else WITNESS_BASIS
        mix = 0.85 if kind == "witness" else 0.7
        return mix * outcome_distribution(branch_phase_state(name, 0.1), basis) + (1 - mix) * uniform

    matched = run(unmatched, (0.0, 0.0), 15, shots=32768)
    for name, row in matched["quadrature"].items():
        if abs(row["phi_rad"] - 0.1) > 4 * row["phi_se"]:
            raise AssertionError(f"{name}: matched phase {row['phi_rad']} biased against 0.1")
        if not row["witness_cos_minus_matched_cos"]["flag"]:
            raise AssertionError(f"{name}: a 0.15 visibility difference escaped the context comparison")

    # An unresolved amplitude withholds the phase: zero visibility on every circuit of the phase pair.
    def flat(name: str, kind: str = "witness") -> np.ndarray:
        return uniform if name in {"k1", "b1"} and kind != "witness" else ideal_distribution(name, kind)

    blind = run(flat, (0.0, 0.0), 16)
    if any(row["visibility_supported"] or row["phi_rad"] is not None for row in blind["quadrature"].values()):
        raise AssertionError("a phase was reported at unresolved visibility")

    # Boundary-aware intervals: every shot in one outcome with perfect references keeps a positive width.
    point = BootstrapCell(score_vector(), 400)(((1000, *[0] * 15), (1000, *[0] * 15), (*[0] * 15, 1000), 0))
    if not point[1] > point[0]:
        raise AssertionError(f"an all-one-outcome cell has the zero-width interval {point}")

    # Shot strings holding anything but the binary outcome digits 0 and 1 are refused with their source.
    for malformed in (["xxxx"], ["01-1"], ["0\u00e91"]):
        try:
            shot_bits(malformed, 4, "batch-09/witness-99.cq")
        except SystemExit as exc:
            if "batch-09/witness-99.cq" not in str(exc):
                raise AssertionError(f"shot parse error lacks its source: {exc}") from exc
        else:
            raise AssertionError(f"shot strings {malformed} parsed")

    series_gate_self_test(files, twin, synthetic_series, ideal_distribution)

    # Pooled variance with the joint per-shot scores: independent reconstruction from the combined series.
    g_vec = score_vector()
    cases_c, raw_c, batch_c = synthetic_series(files, ideal_distribution, (0.0, 0.0), 14, 8192, common_flip=0.25)
    correlated = analyze_series(cases_c, raw_c, batch_c)
    pooled = correlated["contraction"]["pooled_equal_patch_weights"]
    expected = 0.0
    for witness in cases_c["witnesses"]:
        if witness["kind"] != "witness":
            continue
        bits_c = shot_bits(raw_c[(batch_c[witness["file"]], witness["file"])], cases_c["nqubits"])
        combined = np.zeros(len(bits_c))
        for patch_row in witness["patches"]:
            if patch_row["state"][0] in "kb":
                q3, q1, q0, q2 = patch_row["qubits"]
                cols = [cases_c["nqubits"] - 1 - q for q in (q3, q2, q1, q0)]
                code = sum(bits_c[:, c].astype(int) << (3 - i) for i, c in enumerate(cols))
                combined += g_vec[code] / 12
        if combined.any():
            expected += float(combined.var(ddof=1)) / len(combined)
    if abs(pooled["se"] ** 2 - expected) > 1e-12 * max(expected, 1e-30) + 1e-15:
        raise AssertionError(
            f"pooled variance {pooled['se'] ** 2} differs from the combined-series variance {expected}"
        )
    if abs(pooled["se"] / pooled["se_marginal_only"] - 1) < 0.03:
        raise AssertionError("shared noise does not change the pooled standard error")

    # A short shot list is refused by name before any cell; a local qxelarator run is an emulator control.
    cases_s, raw_s, batch_s = synthetic_series(files, depolarized, (0.0, 0.0), 13, 64)
    key = ("batch-01", "witness-01.cq")
    raw_s[key] = raw_s[key][:-1]
    try:
        analyze_series(cases_s, raw_s, batch_s)
    except SystemExit as exc:
        if "witness-01.cq" not in str(exc) or "no cell is computed" not in str(exc):
            raise AssertionError(f"short list refused for another reason: {exc}") from exc
    else:
        raise AssertionError("a short shot list was analyzed")
    local = {**cases_s, "control": "local_qxelarator", "simulator": {"name": "qxelarator", "version": "0.10.0"}}
    if claim_kind(local) != "emulator control" or claim_kind(cases_s) != "preregistered hardware inference":
        raise AssertionError("claim kinds of a local control and a hardware series are wrong")

    cases, raw, batch_of = synthetic_series(files, depolarized, (0.0, 0.0), 5, 64)
    del raw[("batch-03", READOUT_ONE)]
    try:
        analyze_series(cases, raw, batch_of)
    except SystemExit as exc:
        if "readout" not in str(exc):
            raise AssertionError(f"a missing readout reference failed for another reason: {exc}") from exc
    else:
        raise AssertionError("a witness was analyzed without its readout reference")
    cost = json.loads(files["batch-00/cases.json"])["cost"]
    print(
        f"qi bdsc pauli: {len(files)} Tuna files and {len(twin)} QX twin files; native X90 and mY90 verified "
        f"(U P U^dagger = Z, spec R_n forms, pauli_form.json probabilities); balance tables "
        f"{len(tables['state_patch_cells'])} state-patch cells; quadrature {derivation}; "
        f"36 witness and 15 quadrature and cosine cells pass the ideal, depolarized, readout-biased, coherent, "
        f"branch-phase, matched-visibility, unresolved-phase, drift, breach, context and twin series; the series "
        f"gate refuses every stop offline; {cost['jobs']} jobs, {cost['execution_seconds']} s, "
        f"{cost['wall_seconds']} s wall"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--select-placement", action="store_true", help="rank the placements PLACEMENT is chosen from")
    mode.add_argument("--analyze", type=Path, nargs="+", metavar="RUN_DIR", help="the batches of one series")
    mode.add_argument("--references", type=Path, nargs="+", metavar="RUN_DIR", help="the batches loaded so far")
    mode.add_argument(
        "--submit-next", type=Path, metavar="SERIES_DIR", help="gate and submit the next batch of a case series"
    )
    parser.add_argument("--out", type=Path, help="with --analyze: the analysis file (default RUN_DIR/analysis.json)")
    parser.add_argument("--replay", action="store_true", help="with --analyze: compare OUT with the recomputation")
    parser.add_argument("--runs", type=Path, default=ROOT / "results/quantum_inspire/runs", help="with --submit-next")
    parser.add_argument("--approval", help="with --submit-next: the owner's approval, quoted")
    parser.add_argument("--control", type=Path, help="with --submit-next on Tuna-17: the QX twin's analysis")
    parser.add_argument("--dry", action="store_true", help="with --submit-next: print the receipt, send nothing")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.select_placement:
        ranking = select_placement(TUNA17)
        for holds, path_path, q2_path, placement in ranking[:10]:
            print(
                f"paths with q11 and q13 {holds} path-path couplers {path_path} q2-path couplers {q2_path} {placement}"
            )
        first = ranking[0][3] == PLACEMENT
        print(f"{len(ranking)} disjoint placements; PLACEMENT {'is' if first else 'is not'} the first")
        return 0 if first else 1
    if args.references:
        cases, raw, _ = load_series(args.references)
        require_full_shots(cases, raw)
        report = reference_report(cases, raw)
        print(json.dumps(report, indent=1))
        return 1 if report["stop_condition_batch_00"] or report["bracket_drift"]["flagged"] else 0
    if args.submit_next:
        if not args.dry and not (args.approval or "").strip():
            parser.error("--submit-next needs --approval")
        run_dir, receipt = submit_next(args.submit_next, args.runs, args.approval or "", args.control, args.dry)
        if args.dry:
            print(json.dumps({"run_dir": run_dir.name, **receipt}, indent=1))
        return 0
    if args.analyze:
        if len(args.analyze) > 1 and args.out is None:
            parser.error("--analyze over several batches needs --out")
        text = json.dumps(analyze(args.analyze), indent=1) + "\n"
        out = args.out or args.analyze[0] / "analysis.json"
        if args.replay:
            retained = out.read_text(encoding="utf-8")
            if retained == text:
                print(f"{out} replays byte for byte")
                return 0
            mismatch = replay_mismatch(json.loads(retained), json.loads(text), "$")
            if mismatch:
                raise SystemExit(f"{out} differs from the recomputation of {len(args.analyze)} batches at {mismatch}")
            print(f"{out} replays within {REPLAY_RTOL:g} relative float rounding")
            return 0
        out.write_text(text, encoding="utf-8")
        print(text, end="")
        return 0
    series = build()
    base = args.write or args.check
    total = 0
    for name, files in series.items():
        root = base / name
        if args.check:
            retained = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
            if retained != set(files):
                raise SystemExit(f"{root}: files {sorted(retained ^ set(files))} differ from the regeneration")
        for relative, text in files.items():
            path = root / relative
            if args.write:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            elif path.read_text(encoding="utf-8") != text:
                raise SystemExit(f"{path} differs from its regeneration")
        total += len(files)
    print(f"qi bdsc pauli cases: {total} files {'written' if args.write else 'match their regeneration'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
