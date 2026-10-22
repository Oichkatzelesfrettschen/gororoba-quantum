"""Tuna-17 case builder for the BDSC target effect read as a four-qubit local Pauli sum.

The target effect E0 = I/2 - YIXY/4 + YZXY/4 of docs/notes/topics/bdsc-pauli-readout.md is
diagonal in one product basis (Y on q3, Z on q2, X on q1, Y on q0). With signs z2 and
t = y3 x1 y0 of the measured eigenvalues, the score g is 1/2 for z2 = +1 and (1 - t)/2 for
z2 = -1; its mean is Tr(E0 rho) and the table of scores is the `target.readout.scores` list of
docs/evidence/bdsc/pauli/pauli_form.json. docs/design/bdsc-tuna17-pauli-pilot.md fixes the
design this script builds: a twelve-state bank whose ideal scores are 0, 1/2 and 1, three disjoint
patches of Tuna-17, and a Latin rotation of the bank through the patches.

Patch. Logical qubits (q3, q2, q1, q0) sit on four physical qubits. (q3, q1, q0) is a connected
path with q1 in the middle, carrying a GHZ-type pair (|a> + s|~a>)/sqrt2 prepared by H on q3,
CNOT q3 -> q1 and CNOT q1 -> q0 (each CNOT is H CZ H on the target), then X and Z corrections;
q2 holds a definite Z state and needs no coupler. Every gate is Clifford and lies on Tuna's
5 degree grid. The readout rotates q3 and q0 by Sdag then H, q1 by H, and leaves q2.

Placement. PLACEMENT is the first entry of select_placement(): the disjoint triples of patches
over the qubits outside excluded_qubits() of scripts/qi_zero_divisor_cases.py, ranked by the
number of paths holding both q11 and q13 (their readout context is established), then the
couplers joining one patch's path to another patch's path, then the couplers from a q2 qubit to
another patch's path, then the lexicographically least placement.

Series. Twelve witness circuits put state (c + 4p) mod 12 of BANK on patch p of circuit c, so
each state meets each patch once. Six batches hold two witness circuits and one readout
reference, readout-0 in even batches and readout-1 in odd ones. A witness is corrected with
the reference of its own batch for one preparation and the nearest other batch for the other
(the earlier batch on a tie; batch-00 uses batch-01); cases.json records the pairing.
Every circuit measures all 17 qubits, and bit strings put qubit 0 at the rightmost character.

Before emitting, build() checks each state's preparation circuit with a Qiskit Statevector
against its target vector, and the emitted cQASM text of every witness against the ideal score
of each state it holds.

--select-placement prints the ranking without writing. --write DIR writes
DIR/bdsc_pauli_tuna_17/ (batch-NN/ cases and a series cases.json); --check DIR regenerates it and
compares bytes and file sets. --analyze RUN_DIR... [--out FILE] writes the preregistered analysis
of the raw shots of every batch of one series. --self-test runs ideal, depolarized, readout-biased
and coherent-error synthetic series through the analysis.

Usage: "$PYTHON" scripts/qi_bdsc_pauli_cases.py
       (--select-placement | --write DIR | --check DIR | --analyze RUN_DIR... [--out FILE] | --self-test)
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from functools import cache
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import bdsc_pauli  # noqa: E402
from qi_platform import HARDWARE_BATCH_CIRCUITS  # noqa: E402
from qi_zero_divisor_cases import (  # noqa: E402
    BACKEND,
    BACKEND_TYPE_ID,
    NQUBITS,
    TUNA17,
    bit,
    catalogue_check,
    excluded_qubits,
    header,
    load_series,
    readout_circuits,
    wilson,
)

import bdsc  # noqa: E402
import parallel  # noqa: E402

PAULI_FORM = ROOT / "docs/evidence/bdsc/pauli/pauli_form.json"
SERIES = "bdsc_pauli_tuna_17"
SHOTS = 32768
PATCHES = 3
BATCHES = 6
WITNESS_PER_BATCH = HARDWARE_BATCH_CIRCUITS - 1
READOUT_STOP = 0.15
Z_FLAG = 3.0
ALPHA = 0.05
Z_95 = 1.959963984540054
# Patch (q3, q1, q0, q2) of physical qubits; the three patches use all twelve qubits outside
# excluded_qubits(), with q3 (isolated once q5 and q6 are excluded) as a q2 qubit.
PLACEMENT = ((1, 4, 2, 3), (8, 11, 14, 13), (12, 15, 16, 10))
GROUP_IDEAL = {"kernel": 0.0, "bright": 1.0, "middle": 0.5, "sector": 0.5}
CQASM = {"h": "H", "x": "X", "z": "Z", "sdg": "Sdag"}
PREREGISTERED = {
    "estimators": "Per state and patch: the raw score mean with an empirical-Bernstein 95% interval "
    "(Maurer-Pontil Theorem 4, range 1, unbiased sample variance, two-sided) and the kernel-outcome "
    "fraction (z2 = -1 and t = +1) with a Wilson 95% interval; a readout-corrected score from the "
    "tensor product of single-qubit assignment matrices built from the readout pairing of the "
    "witness's batch, reported beside the raw value without an interval.",
    "contraction": "Under a depolarizing contraction V of the (q3, q1, q0) parity, kernel and bright "
    "states read (1 - V)/2 and (1 + V)/2, so kernel + bright - 1 is consistent with zero for each "
    "partner pair (k_i, b_i) and pooled over the four pairs, and middle and sector states read 1/2. "
    "A violation at |z| >= 3 on any such statistic of a patch names an error outside the contraction "
    "(readout bias, leakage or a coherent preparation error). Each z divides the raw residual by the "
    "square root of the summed sample variances over shots.",
    "pooling": "Patches are analyzed separately; the pooled value is the equal-weight mean over the "
    "three patches of the per-patch pooled kernel + bright - 1.",
    "stop_conditions": "Batch 0's readout reference shows a patch qubit with P(1|0) or P(0|1) above "
    f"{READOUT_STOP}: stop and redraw the placement. A job fails or returns fewer shots than requested. "
    "The account-wide pause or the three-circuit limit would be broken.",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


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


READOUT_OPS: list[tuple[str, tuple[int, ...]]] = [
    ("sdg", (3,)),
    ("h", (3,)),
    ("h", (1,)),
    ("sdg", (0,)),
    ("h", (0,)),
]


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


def readout_unitary() -> np.ndarray:
    """Readout rotation of logical qubits (q3, q2, q1, q0) in the kron order of bdsc_pauli.word_matrix."""
    one = np.eye(2, dtype=complex)

    def rot(letter: str) -> np.ndarray:
        u = one
        for gate in bdsc_pauli.ROTATIONS[letter]:
            u = bdsc_pauli.GATES[gate] @ u
        return u

    return np.kron(np.kron(np.kron(rot("Y"), one), rot("X")), rot("Y"))


def outcome_distribution(psi: np.ndarray) -> np.ndarray:
    """P(code) of the readout of the logical state psi (index j = 8 j3 + 4 j2 + 2 j1 + j0)."""
    return np.abs(readout_unitary() @ psi) ** 2


def ideal_scores() -> dict[str, float]:
    """Ideal score of each bank state, checked against <psi|E0|psi> and the group value; raises on mismatch."""
    g, effect = score_vector(), bdsc.ideal_effect()
    out = {}
    for entry in BANK:
        psi = state_vector(entry)
        require(abs(np.linalg.norm(psi) - 1) < 1e-12, f"{entry['name']}: state is not normalized")
        expectation = float((psi.conj() @ effect @ psi).real)
        by_outcome = float(g @ outcome_distribution(psi))
        want = GROUP_IDEAL[entry["group"]]
        require(
            abs(expectation - want) < 1e-12 and abs(by_outcome - want) < 1e-12,
            f"{entry['name']}: <E0> {expectation}, readout score {by_outcome}, group value {want}",
        )
        out[entry["name"]] = want
    return out


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


def witness_text(circuit: int) -> str:
    lines = header(NQUBITS)
    prep, rot = [], []
    for p, patch in enumerate(PLACEMENT):
        entry = BANK[state_index(circuit, p)]
        where = logical_map(patch)
        prep.append(f"// patch {p} (q3 q1 q0 q2 = {list(patch)}) state {entry['name']}")
        prep += cqasm_ops(prep_ops(entry), where)
        rot += cqasm_ops(READOUT_OPS, where)
    return "\n".join(lines + prep + ["", "barrier q", ""] + rot + ["", "barrier q", "b = measure q", ""])


def state_index(circuit: int, patch: int) -> int:
    return (circuit + (len(BANK) // PATCHES) * patch) % len(BANK)


def qiskit_circuit(ops: list[tuple[str, tuple[int, ...]]], width: int) -> Any:
    from qiskit import QuantumCircuit

    qc = QuantumCircuit(width)
    for name, qubits in ops:
        getattr(qc, name)(*qubits)
    return qc


def parse_cqasm(text: str) -> list[tuple[str, tuple[int, ...]]]:
    """Gate list of an emitted witness; any line outside the emitted vocabulary raises."""
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


class CheckWitness:
    """Exact check of one witness circuit; a module-level callable for parallel.ordered_map."""

    def __call__(self, circuit: int) -> dict[str, Any]:
        from qiskit.quantum_info import Statevector

        g, ideal = score_vector(), ideal_scores()
        for p in range(PATCHES):
            entry = BANK[state_index(circuit, p)]
            target = state_vector(entry)
            prepared = Statevector(qiskit_circuit(prep_ops(entry), 4)).data
            if abs(abs(np.vdot(target, prepared)) - 1) > 1e-12:
                raise ValueError(f"{entry['name']}: preparation circuit differs from its target vector")
        emitted = Statevector(qiskit_circuit(parse_cqasm(witness_text(circuit)), NQUBITS))
        rows = []
        for p, patch in enumerate(PLACEMENT):
            entry = BANK[state_index(circuit, p)]
            q3, q1, q0, q2 = patch
            probs = emitted.probabilities([q0, q1, q2, q3])
            score = float(g @ probs)
            if abs(score - ideal[entry["name"]]) > 1e-9:
                raise ValueError(f"circuit {circuit} patch {p} {entry['name']}: emitted ideal score {score}")
            rows.append({"patch": p, "state": entry["name"], "ideal_score": round(score, 12)})
        return {"circuit": circuit, "patches": rows}


def witness_file(circuit: int) -> str:
    return f"witness-{circuit + 1:02d}.cq"


def readout_pairing() -> dict[str, dict[str, str]]:
    """Batch holding the readout-0 and readout-1 reference of each batch's witnesses."""
    out = {}
    for b in range(BATCHES):
        own = f"readout-{b % 2}.cq"
        other = f"readout-{1 - b % 2}.cq"
        neighbor = b - 1 if b > 0 else b + 1
        out[f"batch-{b:02d}"] = {own: f"batch-{b:02d}", other: f"batch-{neighbor:02d}"}
    return out


def logical_to_physical() -> list[dict[str, Any]]:
    return [
        {"patch": p, **{f"q{bit_}": phys for bit_, phys in sorted(logical_map(patch).items(), reverse=True)}}
        for p, patch in enumerate(PLACEMENT)
    ]


@cache
def build() -> dict[str, str]:
    """The series directory: file name -> text, after the exact circuit checks."""
    backend, _ = catalogue_check()
    if backend["max_number_of_shots"] < SHOTS:
        raise SystemExit(f"{BACKEND} admits {backend['max_number_of_shots']} shots, below {SHOTS}")
    excluded = set(excluded_qubits())
    used = {q for patch in PLACEMENT for q in patch}
    if len(used) != 4 * PATCHES or used & excluded:
        raise SystemExit(f"PLACEMENT {PLACEMENT} overlaps or uses an excluded qubit of {sorted(excluded)}")
    ideal = ideal_scores()
    checks = parallel.ordered_map(CheckWitness(), list(range(len(BANK))))
    texts = {witness_file(c): witness_text(c) for c in range(len(BANK))}
    texts.update(readout_circuits(NQUBITS))
    shared: dict[str, Any] = {
        "backend": BACKEND,
        "backend_type_id": backend["id"],
        "nqubits": backend["nqubits"],
        "shots": SHOTS,
        "placement": [list(p) for p in PLACEMENT],
        "placement_fields": ["q3", "q1", "q0", "q2"],
        "excluded_qubits": sorted(excluded),
        "logical_to_physical": logical_to_physical(),
        "bit_order": "a shot string puts qubit 0 at the rightmost character: qubit q is character -(1 + q)",
        "readout_basis": {"q3": "Y", "q2": "Z", "q1": "X", "q0": "Y"},
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
        "readout_rotation": [[name, list(qs)] for name, qs in READOUT_OPS],
        "witnesses": [{"file": witness_file(c), "patches": check["patches"]} for c, check in enumerate(checks)],
        "readout_pairing": readout_pairing(),
        "preregistered": PREREGISTERED,
    }
    files: dict[str, str] = {}
    batches = []
    for b in range(BATCHES):
        name = f"batch-{b:02d}"
        rows = [{"file": witness_file(WITNESS_PER_BATCH * b + n), "kind": "witness"} for n in range(WITNESS_PER_BATCH)]
        rows.append({"file": f"readout-{b % 2}.cq", "kind": "readout"})
        for row in rows:
            row["sha256"] = hashlib.sha256(texts[row["file"]].encode()).hexdigest()
            files[f"{name}/{row['file']}"] = texts[row["file"]]
        manifest = {"schema": "qi-bdsc-pauli-cases-v1", **shared, "batch": name, "circuits": rows}
        files[f"{name}/cases.json"] = json.dumps(manifest, indent=1) + "\n"
        batches.append({"batch": name, "files": [row["file"] for row in rows]})
    series = {"schema": "qi-bdsc-pauli-series-v1", "backend": BACKEND, "batches": batches}
    files["cases.json"] = json.dumps(series, indent=1) + "\n"
    if len(files) != 6 * (WITNESS_PER_BATCH + 2) + 1:
        raise SystemExit(f"series holds {len(files)} files")
    return files


# --- analysis -----------------------------------------------------------------------------------


def shot_bits(shots: list[str], width: int) -> np.ndarray:
    """(n, width) uint8 matrix of the shot strings, column c holding character c."""
    if any(len(s) != width for s in shots):
        raise SystemExit(f"a shot string differs from the declared width {width}")
    return np.frombuffer("".join(shots).encode("ascii"), dtype=np.uint8).reshape(len(shots), width) - 48


def assignment(shots0: list[str], shots1: list[str], qubit: int) -> tuple[float, float]:
    """(e01, e10) = (P(read 1 | prepared 0), P(read 0 | prepared 1)) of one physical qubit."""
    return (
        sum(bit(s, qubit) for s in shots0) / len(shots0),
        sum(1 - bit(s, qubit) for s in shots1) / len(shots1),
    )


def corrected_score(codes: np.ndarray, rates: list[tuple[float, float]], g: np.ndarray) -> float:
    """Mean score after applying the inverse tensor product of single-qubit assignment matrices to P(code)."""
    observed = np.bincount(codes, minlength=16) / len(codes)
    full = np.ones((1, 1))
    for e01, e10 in rates:
        full = np.kron(full, np.array([[1 - e01, e10], [e01, 1 - e10]]))
    return float(g @ np.linalg.solve(full, observed))


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


def analyze(run_dirs: list[Path]) -> dict[str, Any]:
    return analyze_series(*load_series(run_dirs))


def analyze_series(cases: dict[str, Any], raw: dict[tuple[str, str], list[str]], batch_of: dict[str, str]) -> dict:
    require(cases.get("backend") == BACKEND and cases.get("backend_type_id") == BACKEND_TYPE_ID, "not a Tuna-17 series")
    width = cases["nqubits"]
    g = score_vector()
    bank_ideal = {row["name"]: row["ideal_score"] for row in cases["bank"]}
    group = {row["name"]: row["group"] for row in cases["bank"]}
    placement = [tuple(p) for p in cases["placement"]]
    cells = []
    readout: dict[str, dict[str, Any]] = {}
    for witness in cases["witnesses"]:
        file = witness["file"]
        if file not in batch_of:
            raise SystemExit(f"the series lacks the batch holding {file}; analyze every batch together")
        batch = batch_of[file]
        pairing = cases["readout_pairing"][batch]
        refs = {name: raw[(owner, name)] for name, owner in pairing.items() if (owner, name) in raw}
        if len(refs) != len(pairing):
            raise SystemExit(f"batch {batch!r} holding {file} lacks the readout references {pairing}")
        bits = shot_bits(raw[(batch, file)], width)
        for row in witness["patches"]:
            q3, q1, q0, q2 = placement[row["patch"]]
            columns = [width - 1 - q for q in (q3, q2, q1, q0)]
            y3, z2, x1, y0 = (bits[:, c].astype(int) for c in columns)
            codes = y3 << 3 | z2 << 2 | x1 << 1 | y0
            scores = g[codes]
            t = (1 - 2 * y3) * (1 - 2 * x1) * (1 - 2 * y0)
            kernel = int(np.count_nonzero((z2 == 1) & (t == 1)))
            rates = [assignment(refs["readout-0.cq"], refs["readout-1.cq"], q) for q in (q3, q2, q1, q0)]
            for q, (e01, e10) in zip((q3, q2, q1, q0), rates, strict=True):
                readout.setdefault(batch, {})[str(q)] = {"e01": e01, "e10": e10}
            n = len(scores)
            cells.append(
                {
                    "state": row["state"],
                    "group": group[row["state"]],
                    "patch": row["patch"],
                    "batch": batch,
                    "file": file,
                    "shots": n,
                    "shots_requested": cases["shots"],
                    "ideal_score": bank_ideal[row["state"]],
                    "score_mean": float(scores.mean()),
                    "score_variance": float(scores.var(ddof=1)),
                    "score_ci95_empirical_bernstein": eb_interval(scores),
                    "kernel_count": kernel,
                    "kernel_fraction": kernel / n,
                    "kernel_ci95_wilson": wilson(kernel, n),
                    "score_readout_corrected": corrected_score(codes, rates, g),
                }
            )
    return {
        "schema": "qi-bdsc-pauli-analysis-v1",
        "claim_kind": "preregistered hardware inference" if "twin_of" not in cases else "emulator control",
        "cells": cells,
        "readout_references": readout,
        "stop_condition_readout": stop_condition(readout, cases),
        "contraction": contraction(cells, len(placement)),
    }


def stop_condition(readout: dict[str, dict[str, Any]], cases: dict[str, Any]) -> list[dict[str, Any]]:
    """Patch qubits whose assignment error exceeds READOUT_STOP in any batch's references."""
    return [
        {"batch": batch, "qubit": int(q), **rates}
        for batch, qubits in sorted(readout.items())
        for q, rates in sorted(qubits.items(), key=lambda kv: int(kv[0]))
        if rates["e01"] > READOUT_STOP or rates["e10"] > READOUT_STOP
    ]


def contraction(cells: list[dict[str, Any]], patches: int) -> dict[str, Any]:
    by = {(c["state"], c["patch"]): c for c in cells}
    out: dict[str, Any] = {}
    pooled_patch = []
    for p in range(patches):
        pairs = []
        for n in range(1, len(bdsc.KERNEL_PAIRS) + 1):
            k, b = by.get((f"k{n}", p)), by.get((f"b{n}", p))
            if k is None or b is None:
                continue
            variance = k["score_variance"] / k["shots"] + b["score_variance"] / b["shots"]
            pairs.append({"pair": n, **statistic(k["score_mean"] + b["score_mean"] - 1, variance)})
        singles = [
            {
                "state": name,
                **statistic(
                    by[(name, p)]["score_mean"] - 0.5, by[(name, p)]["score_variance"] / by[(name, p)]["shots"]
                ),
            }
            for name in ("e0", "e10", "e7", "e12")
            if (name, p) in by
        ]
        pooled = None
        if pairs:
            variance = sum(r["se"] ** 2 for r in pairs) / len(pairs) ** 2
            pooled = statistic(sum(r["residual"] for r in pairs) / len(pairs), variance)
            pooled_patch.append(pooled)
        out[f"patch-{p}"] = {
            "pairs_kernel_plus_bright_minus_one": pairs,
            "pooled_kernel_plus_bright_minus_one": pooled,
            "middle_sector_minus_half": singles,
            "violation": any(r["flag"] for r in [*pairs, *singles, *([pooled] if pooled else [])]),
        }
    if len(pooled_patch) == patches:
        residual = sum(r["residual"] for r in pooled_patch) / patches
        variance = sum(r["se"] ** 2 for r in pooled_patch) / patches**2
        out["pooled_equal_patch_weights"] = {
            "estimand": "equal-weight mean over the patches of the per-patch pooled kernel + bright - 1",
            **statistic(residual, variance),
        }
    return out


# --- self-test ------------------------------------------------------------------------------------


def synthetic_series(
    files: dict[str, str],
    distribution: Any,
    flips: tuple[float, float],
    seed: int,
    shots: int = SHOTS,
) -> tuple[dict[str, Any], dict[tuple[str, str], list[str]], dict[str, str]]:
    """Shots of the written series for per-state outcome distributions and a readout flip pair (e01, e10).

    distribution(name) gives P(code) over the 16 outcomes of one patch; patches are independent,
    qubits outside the patches read the readout flips of an idle qubit, and the readout circuits
    flip every qubit with (e01, e10).
    """
    rng = np.random.default_rng(seed)
    manifests = [json.loads(files[f"batch-{b:02d}/cases.json"]) for b in range(BATCHES)]
    cases = {k: v for k, v in manifests[0].items() if k not in {"batch", "circuits", "schema"}}
    placement = [tuple(p) for p in cases["placement"]]

    def strings(matrix: np.ndarray) -> list[str]:
        return [row.tobytes().decode("ascii") for row in np.ascontiguousarray(matrix + 48).view(f"S{NQUBITS}")]

    raw: dict[tuple[str, str], list[str]] = {}
    batch_of: dict[str, str] = {}
    for manifest in manifests:
        batch = manifest["batch"]
        for row in manifest["circuits"]:
            if row["kind"] == "readout":
                prepared = int(row["file"][8])
                raw[(batch, row["file"])] = strings(
                    flip_bits(np.full((shots, NQUBITS), prepared, dtype=np.uint8), flips, rng)
                )
                continue
            batch_of[row["file"]] = batch
            matrix = np.zeros((shots, NQUBITS), dtype=np.uint8)
            witness = next(w for w in cases["witnesses"] if w["file"] == row["file"])
            for entry in witness["patches"]:
                q3, q1, q0, q2 = placement[entry["patch"]]
                counts = rng.multinomial(shots, distribution(entry["state"]))
                codes = rng.permutation(np.repeat(np.arange(16), counts))
                for position, q in zip((3, 2, 1, 0), (q3, q2, q1, q0), strict=True):
                    matrix[:, NQUBITS - 1 - q] = codes >> position & 1
            matrix = flip_bits(matrix, flips, rng)
            raw[(batch, row["file"])] = strings(matrix)
    return cases, raw, batch_of


def flip_bits(columns: np.ndarray, flips: tuple[float, float], rng: np.random.Generator) -> np.ndarray:
    """Apply the assignment errors: 0 reads 1 with flips[0], 1 reads 0 with flips[1]."""
    u = rng.random(columns.shape)
    return np.where(columns == 0, (u < flips[0]).astype(np.uint8), (u >= flips[1]).astype(np.uint8))


def self_test() -> None:
    files = build()
    ranking = select_placement(TUNA17)
    if ranking[0][3] != PLACEMENT:
        raise AssertionError(f"PLACEMENT is not the first of {len(ranking)} ranked placements")
    if ranking[0][0] != 0:
        raise AssertionError("the first placement holds a path with both q11 and q13")
    ideal = ideal_scores()
    entries = {e["name"]: e for e in BANK}
    # Negative controls: a wrong sign or a wrong group value must be refused by the exact checks.
    from qiskit.quantum_info import Statevector

    wrong = Statevector(qiskit_circuit([op for op in prep_ops(entries["k2"]) if op[0] != "z"], 4)).data
    if abs(abs(np.vdot(state_vector(entries["k2"]), wrong)) - 1) < 1e-6:
        raise AssertionError("the preparation check cannot see a dropped Z correction")
    if abs(abs(np.vdot(state_vector(entries["b2"]), wrong)) - 1) > 1e-9:
        raise AssertionError("k2 without its Z correction should be b2")

    def ideal_distribution(name: str) -> np.ndarray:
        return outcome_distribution(state_vector(entries[name]))

    def run(distribution: Any, flips: tuple[float, float], seed: int) -> dict[str, Any]:
        return analyze_series(*synthetic_series(files, distribution, flips, seed, 8192))

    def cell_map(analysis: dict[str, Any]) -> dict[tuple[str, int], dict[str, Any]]:
        return {(c["state"], c["patch"]): c for c in analysis["cells"]}

    clean = run(ideal_distribution, (0.0, 0.0), 1)
    for key, cell in cell_map(clean).items():
        low, high = cell["score_ci95_empirical_bernstein"]
        if not low - 1e-12 <= ideal[key[0]] <= high + 1e-12:
            raise AssertionError(f"{key}: ideal shots read {cell['score_mean']}, ideal {ideal[key[0]]}")
        if (
            abs(cell["score_mean"] - ideal[key[0]]) > 0.02
            or abs(cell["score_readout_corrected"] - ideal[key[0]]) > 0.02
        ):
            raise AssertionError(f"{key}: ideal shots read {cell['score_mean']}")
    if any(patch["violation"] for name, patch in clean["contraction"].items() if name.startswith("patch")):
        raise AssertionError("ideal shots violate the contraction law")

    lam = 0.3
    uniform = np.full(16, 1 / 16)

    def depolarized(name: str) -> np.ndarray:
        return (1 - lam) * ideal_distribution(name) + lam * uniform

    contracted = run(depolarized, (0.0, 0.0), 2)
    for key, cell in cell_map(contracted).items():
        want = (1 - lam) * ideal[key[0]] + lam * 0.5
        if abs(cell["score_mean"] - want) > 0.02:
            raise AssertionError(f"{key}: depolarized score {cell['score_mean']}, expected {want}")
    if any(patch["violation"] for name, patch in contracted["contraction"].items() if name.startswith("patch")):
        raise AssertionError("a depolarizing contraction violates the contraction law")

    # An asymmetric assignment error moves single-bit reads (the raw z2 of every state) while the
    # parity residual stays within noise; the assignment correction restores the depolarized values.
    biased = run(depolarized, (0.03, 0.08), 3)
    shifts = []
    for key, cell in cell_map(biased).items():
        want = (1 - lam) * ideal[key[0]] + lam * 0.5
        shifts.append(abs(cell["score_mean"] - want))
        if abs(cell["score_readout_corrected"] - want) > 0.02:
            raise AssertionError(f"{key}: corrected score {cell['score_readout_corrected']}, expected {want}")
    if max(shifts) < 0.02:
        raise AssertionError("the assignment error did not move any raw score")

    # Coherent error: Rx(0.4) on q0 and q3 q1 jointly (exp(-i 0.2 X0) exp(-i 0.2 X3 X1)) after preparation.
    from scipy.linalg import expm

    unitary = expm(-0.2j * bdsc_pauli.word_matrix("IIIX")) @ expm(-0.2j * bdsc_pauli.word_matrix("XIXI"))

    def coherent(name: str) -> np.ndarray:
        return outcome_distribution(unitary @ state_vector(entries[name]))

    rotated = run(coherent, (0.0, 0.0), 4)
    if not all(patch["violation"] for name, patch in rotated["contraction"].items() if name.startswith("patch")):
        raise AssertionError("a coherent error escaped the contraction law on some patch")
    first = rotated["contraction"]["patch-0"]["pairs_kernel_plus_bright_minus_one"]
    if max(abs(row["residual"]) for row in first) < 0.1:
        raise AssertionError("the coherent error did not move kernel + bright - 1")
    cases, raw, batch_of = synthetic_series(files, depolarized, (0.0, 0.0), 5, 64)
    del raw[("batch-01", "readout-1.cq")]
    try:
        analyze_series(cases, raw, batch_of)
    except SystemExit as exc:
        if "readout" not in str(exc):
            raise AssertionError(f"a missing readout reference failed for another reason: {exc}") from exc
    else:
        raise AssertionError("a witness was analyzed without its readout reference")
    print(
        f"qi bdsc pauli: {len(files)} files, ideal scores and 36 cells of ideal, depolarized, "
        "readout-biased and coherent series pass the contraction law as predicted"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--select-placement", action="store_true", help="rank the placements PLACEMENT is chosen from")
    mode.add_argument("--analyze", type=Path, nargs="+", metavar="RUN_DIR", help="the batches of one series")
    parser.add_argument("--out", type=Path, help="with --analyze: the analysis file (default RUN_DIR/analysis.json)")
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
    if args.analyze:
        if len(args.analyze) > 1 and args.out is None:
            parser.error("--analyze over several batches needs --out")
        text = json.dumps(analyze(args.analyze), indent=1) + "\n"
        (args.out or args.analyze[0] / "analysis.json").write_text(text, encoding="utf-8")
        print(text, end="")
        return 0
    files = build()
    root = (args.write or args.check) / SERIES
    if args.check:
        retained = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
        if retained != set(files):
            raise SystemExit(f"{root}: files {sorted(retained ^ set(files))} differ from the regeneration")
    for name, text in files.items():
        path = root / name
        if args.write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        elif path.read_text(encoding="utf-8") != text:
            raise SystemExit(f"{path} differs from its regeneration")
    print(f"qi bdsc pauli cases: {len(files)} files {'written' if args.write else 'match their regeneration'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
