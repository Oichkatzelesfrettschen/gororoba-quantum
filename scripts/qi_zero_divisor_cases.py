"""Exact Clifford+T zero-divisor witness for Tuna-17: Design B's dark, bright and fixture cases in a balanced rotation.

The fixed-operand LCU of Design B (gororoba_quantum/AGENTS.md, "Zero-product
witnesses") applies (L_{e1} + L_{e10})/2 to b = (e_k + e^{i phase} e_l)/sqrt2
and reads the selector: P(s = 0) = ||(e1 + e10)(e_k +- e_l)||^2 / 8, which is
||x y||^2 / 2 for the normalized operands x and y. The cases are the
dark witness (e1 + e10)(e4 - e15) = 0 (P = 0), its bright control
(e1 + e10)(e4 + e15) (P = 1) and the negative fixture (e1 + e10)(e2 - e13),
whose four product terms land on four labels (P = 1/2).

The SELECT sign function of (1, 10), built from cd_core.cd_sign by
select_lcu.joint_select_signs, has algebraic degree 4: the selector times
degree-3 terms of the left-multiplication signs. A degree-4 phase monomial
needs pi/8 rotations, which Tuna quantizes to the nearest pi/36 (20 or 25
degrees). The sign ANF factors through majorities (select_exact), so the
whole SELECT is Z, CZ, CX, two Toffolis and two CCZ on the five qubits
(data 0-3, selector 4): every gate decomposes into H, S, T, Tdag and CZ, on
Tuna's angle grid, and the replica is exact with no workspace. Every corpus
pair (cd_core.sedenion_zero_divisors) has a degree-4 SELECT of similar
size, so (1, 10) keeps the comparison with the Kingston run.

Before any circuit is written, certify() computes each case's product with
cd_core.cd_multiply and with the retained D = 16 tables of the packages
identical to cd_core (docs/evidence/algebra_packages/tables.json), requires
the dark pair in cd_core.sedenion_zero_divisor_corpus, and requires SELECT to
equal cd_sign(16, m, q)|m XOR q> on all 32 basis inputs.
Generation first validates backend identities, widths, directed topologies,
gate support and capacity against the retained QI catalogue. A changed
catalogue requires review of this fixed routing contract before generation.

Two disjoint 5-qubit regions of Tuna-17 (REGIONS) run a replica each. The
qubits of EXCLUDED_QUBITS appear in no region, so 12 qubits remain and fit two
connected 5-qubit regions at most. Of the disjoint region pairs, REGIONS has
the fewest routed CZ summed over the three cases (`--select-regions` recomputes
the choice), then the fewest couplers joining the two regions (spectator
adjacency), then the lexicographically least pair. Circuits 1-3 (files
latin-1..3.cq) rotate the cases through the regions cyclically, dark and
bright, bright and fixture, fixture and dark, so every case runs once in each
region, every pair of cases shares one circuit, and case and region separate.
Circuit 4 measures every qubit prepared in |0> and circuit 5 every qubit
prepared in |1>, giving each selector's readout assignment. A batch holds at
most HARDWARE_BATCH_CIRCUITS circuits and a batch boundary is a calibration
boundary, so the series runs as batch-00..02, each holding one witness circuit
followed by readout-0 and readout-1. Each witness circuit carries two cases,
so its contrast shares one calibration, and its readout correction uses the
assignment measured in the same batch. Routing
seeds are searched over SEEDS and the fewest-CZ result kept, so the circuits
regenerate byte for byte under the pinned Qiskit.

Preregistered analysis (fixed in cases.json before submission):
- P(s = 0) per case and region, raw with a Wilson 95% interval, and corrected
  for the selector's readout assignment from the readout pair of its own batch.
- Contraction law: a visibility contraction V gives dark (1 - V)/2, bright
  (1 + V)/2 and fixture 1/2, so dark + bright - 1 and fixture - 1/2 are each
  consistent with zero at |z| < 3; a violation names a coherent or biased
  error outside the contraction.
- The Kingston Design B dark value 0.182 [0.146, 0.217] at bright 0.828
  (hw-zero-divisor-floor) is the comparison; Kingston ran the same witness
  with continuous rotations in about 45 CZ, so the routed depths differ.

The QX twin packs the same six routed replicas two per 10-qubit circuit and
runs them on the ideal emulator, which checks the platform's handling of the
emitted cQASM.

--select-regions prints the REGIONS choice rule's ranking without writing.
--write DIR writes DIR/zero_divisor_tuna_17/ and DIR/zero_divisor_qx/, each a
series of batch-NN/ cases (circuits and cases.json) under a series cases.json;
--check DIR regenerates both and compares bytes and file sets; --analyze
RUN_DIR... [--out FILE] writes the analysis from the raw shots of every batch
of one series, keyed by (batch, file); --replay RUN_DIR... recomputes retained single-batch analyses and
--replay-series FILE RUN_DIR... the analysis FILE of one batched series. Bit strings put qubit 0 at
the rightmost character (Tuna).

Usage: "$PYTHON" scripts/qi_zero_divisor_cases.py
       (--write DIR | --check DIR | --select-regions | --analyze RUN_DIR... [--out FILE] | --replay RUN_DIR...
        | --replay-series FILE RUN_DIR... | --self-test)
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import sys
from functools import cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from qi_platform import HARDWARE_BATCH_CIRCUITS  # noqa: E402

import parallel  # noqa: E402
from cd_core import _lmat, cd_multiply, cd_sign, sedenion_zero_divisor_corpus  # noqa: E402
from select_lcu import anf_coefficients, joint_select_signs, sparse_pair_prep  # noqa: E402

PACKAGE_TABLES = ROOT / "docs/evidence/algebra_packages/tables.json"
CATALOGUE = ROOT / "docs/evidence/quantum_inspire/catalogue.json"
# Packages whose retained D = 16 table is identical to cd_core
# (gororoba_quantum/AGENTS.md, "Cayley-Dickson packages on the build host").
IDENTICAL_PACKAGES = ("hypercomplex", "hypercomplex-engine", "Cayley-Calculator", "cayley-dickson")

BACKEND = "tuna_17"
BACKEND_TYPE_ID = 7
QX_BACKEND_TYPE_ID = 1
QX_QUBITS = 10
QX_SHOTS = 2048
NQUBITS = 17
SHOTS = 16384
# Frozen routing contract for the acquired witness. Fresh generation must
# validate this contract against the retained catalogue before routing.
TUNA17 = (
    (0, 1), (0, 2), (1, 4), (2, 4), (2, 5), (3, 5), (3, 6), (4, 7), (4, 8), (5, 8), (5, 9), (6, 9),
    (7, 10), (7, 11), (8, 11), (8, 12), (9, 12), (10, 13), (11, 13), (11, 14), (12, 14), (12, 15),
    (14, 16), (15, 16),
)  # fmt: skip
# Qubits no replica uses as a data or selector qubit, with every coupler on
# them; REGIONS avoids all of them. The set is the union of two declared
# parts. READOUT_EXCLUDED holds q9, whose gate-free circuit reads P1 0.27-0.28
# on the idle qubit, and q0 and q6, which read P1 0.39 and 0.14 when prepared
# in |1> after a platform recalibration (pi-pulse and T1 collapse).
# visibility_excluded() holds the qubits whose Ramsey visibility, minimum over
# neighbor sectors and the 0.5 us and 2 us delays, falls below VISIBILITY_FLOOR
# in the coupler-ZZ map analysis; its targets split into a cluster at 0.755 and above
# and a cluster at 0.30 and below with no value between.
READOUT_EXCLUDED = (0, 6, 9)
VISIBILITY_FLOOR = 0.5
COUPLER_ZZ_ANALYSIS = ROOT / "results/quantum_inspire/coupler_zz_tuna_17_analysis.json"
EXPECTED_VISIBILITY_EXCLUDED = (5, 6, 7)


def visibility_excluded(path: Path = COUPLER_ZZ_ANALYSIS, floor: float = VISIBILITY_FLOOR) -> tuple[int, ...]:
    """Targets of the retained coupler-ZZ analysis whose min_visibility is below `floor`, ascending.

    min_visibility is the smallest Ramsey visibility over the sectors of a
    target at both delays of qi_coupler_zz_map (DELAYS, 0.5 us and 2 us).
    """
    targets = json.loads(path.read_text(encoding="utf-8"))["targets"]
    if sorted(row["target"] for row in targets) != list(range(NQUBITS)):
        raise SystemExit(f"{path} does not hold one row per Tuna-17 qubit")
    return tuple(sorted(row["target"] for row in targets if row["min_visibility"] < floor))


@cache
def excluded_qubits() -> tuple[int, ...]:
    """Read the hardware visibility exclusions on first use, keeping pure emitters independent of run archives."""
    return tuple(sorted(set(READOUT_EXCLUDED) | set(visibility_excluded())))


def __getattr__(name: str) -> tuple[int, ...]:
    """Keep the public EXCLUDED_QUBITS tuple available through the lazy hardware read."""
    if name == "EXCLUDED_QUBITS":
        return excluded_qubits()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    return sorted({*globals(), "EXCLUDED_QUBITS"})


REGIONS = ((1, 2, 4, 8, 12), (10, 11, 13, 14, 16))
SEEDS = range(16)
A_PAIR = (1, 10)
CASES = {
    "dark": ((4, 15), math.pi, 0.0),
    "bright": ((4, 15), 0.0, 1.0),
    "fixture": ((2, 13), math.pi, 0.5),
}
# Cyclic rotation of the cases through REGIONS: circuit i holds ROTATION[i] in
# REGIONS order, so each case meets each region once and each pair of cases
# shares one circuit.
ROTATION = (("dark", "bright"), ("bright", "fixture"), ("fixture", "dark"))
DATA, SELECTOR = (0, 1, 2, 3), 4
ANF_MONOMIALS = {0b1, 0b110, 0b1010, 0b1100, 0b1110, 0b10001, 0b10100, 0b11000}
ANF_MONOMIALS |= {0b10011, 0b11001, 0b11010, 0b10111, 0b11101, 0b11110}
BASIS = ["cz", "h", "s", "sdg", "t", "tdg", "x", "y", "z", "sx", "sxdg"]
CQASM = {"h": "H", "s": "S", "sdg": "Sdag", "t": "T", "tdg": "Tdag", "x": "X", "y": "Y", "z": "Z", "sx": "X90"}
CQASM["sxdg"] = "mX90"
KINGSTON = {"dark": 0.182, "dark_ci95": [0.146, 0.217], "bright": 0.828, "claim": "hw-zero-divisor-floor"}


def catalogue_backends(catalogue: Any) -> tuple[dict[str, Any], dict[str, Any]]:
    """Admit only the retained hardware/emulator contract used by this witness.

    A changed backend identity, width or topology needs a reviewed new design;
    it must not silently reuse this acquisition's routing or provenance.
    """
    if not isinstance(catalogue, dict) or not isinstance(catalogue.get("backend_types"), list):
        raise SystemExit("witness catalogue must contain a backend_types list")
    admitted = []
    for identifier, backend_id, width, hardware, shots in (
        (BACKEND, BACKEND_TYPE_ID, NQUBITS, True, SHOTS),
        ("QXsinglenodesimulator", QX_BACKEND_TYPE_ID, QX_QUBITS, False, QX_SHOTS),
    ):
        matches = [b for b in catalogue["backend_types"] if isinstance(b, dict) and b.get("identifier") == identifier]
        if len(matches) != 1:
            raise SystemExit(f"witness catalogue needs exactly one {identifier} backend type")
        backend = matches[0]
        if (
            type(backend.get("id")) is not int
            or backend["id"] != backend_id
            or type(backend.get("nqubits")) is not int
            or backend["nqubits"] != width
            or backend.get("is_hardware") is not hardware
        ):
            raise SystemExit(f"{identifier}: backend identity, width or hardware class changed; review the witness")
        topology = backend.get("topology")
        if not isinstance(topology, list) or not all(
            isinstance(edge, list)
            and len(edge) == 2
            and all(type(q) is int and 0 <= q < width for q in edge)
            and edge[0] != edge[1]
            for edge in topology
        ):
            raise SystemExit(f"{identifier}: malformed catalogue topology")
        actual = {tuple(edge) for edge in topology}
        expected = (
            {edge for a, b in TUNA17 for edge in ((a, b), (b, a))}
            if hardware
            else {(a, b) for a in range(width) for b in range(width) if a != b}
        )
        if actual != expected or len(actual) != len(topology):
            raise SystemExit(f"{identifier}: catalogue topology changed; review the witness routing")
        gates = backend.get("gateset")
        needed = set(CQASM.values()) | {"CZ", "barrier", "measure"}
        if not isinstance(gates, list) or not all(isinstance(gate, str) for gate in gates) or not needed <= set(gates):
            raise SystemExit(f"{identifier}: catalogue lacks a required witness gate")
        if (
            type(backend.get("max_number_of_shots")) is not int
            or backend["max_number_of_shots"] < shots
            or type(backend.get("max_jobs_per_batch_job")) is not int
            or backend["max_jobs_per_batch_job"] < HARDWARE_BATCH_CIRCUITS
        ):
            raise SystemExit(f"{identifier}: witness exceeds the retained backend capacity")
        admitted.append(backend)
    return admitted[0], admitted[1]


def analysis_claim_kind(cases: dict[str, Any]) -> str:
    """Classify retained evidence by its recorded backend; do not relabel old runs from a current catalogue."""
    if type(cases.get("backend_type_id")) is not int:
        raise SystemExit("witness analysis needs an integer recorded backend type id")
    backend = cases.get("backend")
    if backend == BACKEND and cases.get("backend_type_id") == BACKEND_TYPE_ID and "twin_of" not in cases:
        return "preregistered hardware inference"
    if (
        backend == "QXsinglenodesimulator"
        and cases.get("backend_type_id") == QX_BACKEND_TYPE_ID
        and cases.get("twin_of") == BACKEND
    ):
        return "preregistered emulator control"
    raise SystemExit("witness analysis has an unknown or inconsistent recorded backend/twin identity")


def vector(terms: dict[int, int]) -> list[float]:
    out = [0.0] * 16
    for index, coefficient in terms.items():
        out[index] = float(coefficient)
    return out


def table_product(table: dict[str, list[list[int]]], x: dict[int, int], y: dict[int, int]) -> dict[int, int]:
    out: dict[int, int] = {}
    for p, a in x.items():
        for q, b in y.items():
            r = table["index"][p][q]
            out[r] = out.get(r, 0) + table["signs"][p][q] * a * b
    return {r: c for r, c in sorted(out.items()) if c}


def certify() -> dict[str, Any]:
    """Every case's product from cd_core, the retained package tables, and the SELECT action.

    The products (e1 + e10) b come from cd_core.cd_multiply and from each
    retained D = 16 table of the packages identical to cd_core; all must
    agree term for term. The dark pair must be a row of
    cd_core.sedenion_zero_divisor_corpus. The routed circuits implement
    select_exact, whose action on |q>|a>|w=0> must equal
    cd_sign(16, m_a, q)|m_a XOR q>|a>|0> with m_0 = 1 and m_1 = 10, the
    left-multiplication matrices cd_core._lmat builds.
    """
    from qiskit.quantum_info import Statevector

    packages = json.loads(PACKAGE_TABLES.read_text(encoding="utf-8"))["packages"]
    a = {A_PAIR[0]: 1, A_PAIR[1]: 1}
    rows: dict[str, Any] = {}
    for name, ((k, el), phase, ideal) in CASES.items():
        b = {k: 1, el: 1 if phase == 0.0 else -1}
        reference = {r: round(c) for r, c in enumerate(cd_multiply(16, vector(a), vector(b))) if c}
        for package in IDENTICAL_PACKAGES:
            if table_product(packages[package]["tables"]["16"], a, b) != reference:
                raise SystemExit(f"{package} disagrees with cd_core on {name}")
        norm = sum(c * c for c in reference.values())
        if abs(norm / 8 - ideal) > 1e-12:
            raise SystemExit(f"{name}: ||ab||^2/8 = {norm / 8} against the ideal {ideal}")
        rows[name] = {"b": {str(i): c for i, c in b.items()}, "product": {str(i): c for i, c in reference.items()}}
    dark_b = CASES["dark"][0]
    if (A_PAIR[0], A_PAIR[1], 1, dark_b[0], dark_b[1], -1) not in sedenion_zero_divisor_corpus():
        raise SystemExit("the dark pair is not a row of the sedenion zero-divisor corpus")
    select = select_exact(*A_PAIR)
    for selector in (0, 1):
        m = A_PAIR[selector]
        matrix = _lmat(16, m)
        for q in range(16):
            state = Statevector.from_int(q + 16 * selector, 32).evolve(select)
            target = (m ^ q) + 16 * selector
            if abs(state.data[target] - matrix[m ^ q][q]) > 1e-9 or abs(abs(state.data[target]) - 1) > 1e-9:
                raise SystemExit(f"SELECT on |{q}>|{selector}> differs from cd_sign(16, {m}, {q})")
            if matrix[m ^ q][q] != cd_sign(16, m, q):
                raise SystemExit("cd_core._lmat disagrees with cd_sign")
    return {
        "products": rows,
        "package_tables": list(IDENTICAL_PACKAGES),
        "dark_in_cd_core_corpus": True,
        "select_equals_left_multiplication": True,
    }


def select_exact(i: int, j: int) -> Any:
    """SELECT of (L_e1, L_e10) on data 0-3 and selector 4 from the factored sign function.

    The ANF of the joint sign (-1)^f(q, a), a the selector, is
    f = q0 + Maj(q1, q2, q3) + q1 q2 q3 + a (q0 + q2 + q3) + a (1 + q2) Maj(q0, q1, q3),
    since q0 q1 + q0 q3 + q1 q3 = Maj(q0, q1, q3) and likewise for (q1, q2, q3).
    The in-place Cuccaro MAJ (CX q3->q1, CX q3->q0, CCX q0 q1 -> q3) leaves
    Maj(q0, q1, q3) on q3, the phase a (1 + q2) Maj becomes a CCZ between X
    layers on q2, and the MAJ is undone: four three-qubit gates, no workspace.
    ANF_MONOMIALS is the monomial set this construction implements; the sign
    table from cd_core must have exactly that ANF.
    """
    from qiskit import QuantumCircuit

    truth = [0 if sign > 0 else 1 for sign in joint_select_signs(16, i, j)]
    if (i, j) != A_PAIR or set(anf_coefficients(truth)) != ANF_MONOMIALS:
        raise ValueError(f"the factored SELECT implements (1, 10) only; ({i}, {j}) has another sign ANF")
    q0, q1, q2, q3 = DATA
    qc = QuantumCircuit(5)
    qc.z(q0)
    qc.cz(q1, q2)
    qc.cz(q1, q3)
    qc.cz(q2, q3)
    qc.ccz(q1, q2, q3)
    for q in (q0, q2, q3):
        qc.cz(SELECTOR, q)
    qc.cx(q3, q1)
    qc.cx(q3, q0)
    qc.ccx(q0, q1, q3)
    qc.x(q2)
    qc.ccz(SELECTOR, q2, q3)
    qc.x(q2)
    qc.ccx(q0, q1, q3)
    qc.cx(q3, q0)
    qc.cx(q3, q1)
    for b in DATA:
        if i >> b & 1:
            qc.x(b)
    for b in DATA:
        if (i ^ j) >> b & 1:
            qc.cx(SELECTOR, b)
    return qc


def logical(case: str) -> Any:
    from qiskit import QuantumCircuit

    (k, el), phase, _ = CASES[case]
    qc = QuantumCircuit(5)
    qc.compose(sparse_pair_prep(4, k, el, phase), list(DATA), inplace=True)
    qc.h(SELECTOR)
    qc.compose(select_exact(*A_PAIR), range(5), inplace=True)
    qc.h(SELECTOR)
    return qc


class Route:
    """One seeded routing of a case onto a region; a module-level callable the process pool can pickle."""

    def __init__(self, case: str, region: tuple[int, ...], topology: tuple[tuple[int, int], ...]) -> None:
        self.case = case
        self.region = region
        self.topology = topology

    def __call__(self, seed: int) -> tuple[int, int, Any]:
        from qiskit import transpile
        from qiskit.transpiler import CouplingMap

        local = {q: n for n, q in enumerate(self.region)}
        edges = [[local[a], local[b]] for a, b in self.topology if a in local and b in local]
        coupling = CouplingMap(edges + [[b, a] for a, b in edges])
        circuit = transpile(
            logical(self.case), coupling_map=coupling, basis_gates=BASIS, optimization_level=2, seed_transpiler=seed
        )
        return circuit.count_ops().get("cz", 0), seed, circuit


class RouteCount:
    """Routed CZ count of one (case, region, seed) item; a module-level callable the process pool can pickle."""

    def __init__(self, topology: tuple[tuple[int, int], ...]) -> None:
        self.topology = topology

    def __call__(self, item: tuple[str, tuple[int, ...], int]) -> int:
        case, region, seed = item
        return Route(case, region, self.topology)(seed)[0]


def routed(
    case: str, region: tuple[int, ...], topology: tuple[tuple[int, int], ...]
) -> tuple[Any, dict[str, int], int]:
    """Fewest-CZ routing of a case onto a region; returns the circuit on region-local indices, roles, seed.

    The seeds route independently through parallel.ordered_map; the first
    seed in SEEDS order among the fewest-CZ routings wins, as in a serial scan.
    """
    candidates = parallel.ordered_map(Route(case, region, topology), list(SEEDS))
    _, seed, circuit = min(candidates, key=lambda candidate: (candidate[0], candidate[1]))
    final = circuit.layout.final_index_layout()
    roles = {f"d{b}": region[final[b]] for b in DATA}
    roles["selector"] = region[final[SELECTOR]]
    return circuit, roles, seed


def ideal_selector_zero(circuit: Any, roles: dict[str, int], region: tuple[int, ...]) -> float:
    from qiskit.quantum_info import Statevector

    probabilities = Statevector(circuit).probabilities_dict()
    sel = region.index(roles["selector"])
    return sum(p for bits, p in probabilities.items() if bits[len(bits) - 1 - sel] == "0")


def emit(circuit: Any, place: dict[int, int]) -> list[str]:
    """cQASM lines of a routed replica; place maps region-local qubit indices to register indices."""
    lines = []
    for instruction in circuit.data:
        name = instruction.operation.name
        qubits = [place[circuit.find_bit(q).index] for q in instruction.qubits]
        if name == "cz":
            lines.append(f"CZ q[{qubits[0]}], q[{qubits[1]}]")
        elif name in CQASM:
            lines.append(f"{CQASM[name]} q[{qubits[0]}]")
        elif name != "barrier":
            raise ValueError(f"{name} is outside the Tuna gate map")
    return lines


def header(nqubits: int) -> list[str]:
    return ["version 3.0", "", f"qubit[{nqubits}] q", f"bit[{nqubits}] b", ""]


def readout_circuits(nqubits: int) -> dict[str, str]:
    """readout-0 measures every qubit prepared in |0>, readout-1 every qubit after an X: the batch's assignment."""
    measure = ["barrier q", "b = measure q", ""]
    return {
        "readout-0.cq": "\n".join(header(nqubits) + measure),
        "readout-1.cq": "\n".join(header(nqubits) + [f"X q[{q}]" for q in range(nqubits)] + [""] + measure),
    }


def finish(cases: dict[str, Any], texts: dict[str, str]) -> dict[str, str]:
    """batch-NN/ directories of at most HARDWARE_BATCH_CIRCUITS circuits, and the series cases.json.

    Witness circuits fill each batch in manifest order and every batch ends
    with the series' readout circuits, so a witness's readout correction uses
    the assignment measured under its own batch's calibration. Each batch is a
    submittable case whose manifest carries every shared field, so one batch's
    run directory names the full design.
    """
    files: dict[str, str] = {}
    batches = []
    rows = cases.pop("circuits")
    readout = [row for row in rows if row["kind"] == "readout"]
    witness = [row for row in rows if row["kind"] != "readout"]
    per_batch = HARDWARE_BATCH_CIRCUITS - len(readout)
    if per_batch < 1:
        raise SystemExit(f"{len(readout)} readout circuits leave no witness slot in a batch")
    for index, start in enumerate(range(0, len(witness), per_batch)):
        name = f"batch-{index:02d}"
        chunk = [dict(row) for row in witness[start : start + per_batch] + readout]
        for row in chunk:
            row["sha256"] = hashlib.sha256(texts[row["file"]].encode()).hexdigest()
            files[f"{name}/{row['file']}"] = texts[row["file"]]
        manifest = {**cases, "schema": "qi-zero-divisor-cases-v2", "batch": name, "circuits": chunk}
        files[f"{name}/cases.json"] = json.dumps(manifest, indent=1) + "\n"
        batches.append({"batch": name, "files": [row["file"] for row in chunk]})
    series = {"schema": "qi-zero-divisor-series-v1", "backend": cases["backend"], "batches": batches}
    files["cases.json"] = json.dumps(series, indent=1) + "\n"
    return files


def catalogue_check() -> tuple[dict[str, Any], dict[str, Any]]:
    """Validate the public routing contract and return the admitted Tuna-17/QX backend records."""
    return catalogue_backends(json.loads(CATALOGUE.read_text(encoding="utf-8")))


def build() -> dict[str, dict[str, str]]:
    """Case directory name -> files: the Tuna-17 case rotation and its QX twin."""
    tuna_backend, qx_backend = catalogue_check()
    topology = tuple(sorted({tuple(sorted(edge)) for edge in tuna_backend["topology"]}))
    common = {
        "a_pair": list(A_PAIR),
        "cases": {
            name: {"b_pair": list(b), "phase": ph, "ideal_p_selector_zero": p} for name, (b, ph, p) in CASES.items()
        },
        "certificate": certify(),
        "preregistered": {
            "estimators": "P(s=0) raw with Wilson 95%; readout-corrected with the selector's assignment from "
            "the readout-0 and readout-1 circuits of the same batch; contraction residuals dark+bright-1 and "
            "fixture-1/2 with |z| < 3 as consistency",
            "comparison": KINGSTON,
        },
    }
    excluded = excluded_qubits()
    for region in REGIONS:
        if set(region) & set(excluded):
            raise SystemExit(f"region {region} uses an excluded qubit of {excluded}")
    replicas = []
    for index, assignment in enumerate(ROTATION, start=1):
        for region, case in zip(REGIONS, assignment, strict=True):
            circuit, roles, seed = routed(case, region, topology)
            p0 = ideal_selector_zero(circuit, roles, region)
            if abs(p0 - CASES[case][2]) > 1e-9:
                raise SystemExit(f"{case} on {region}: ideal P(s=0) {p0}")
            replicas.append((index, region, case, circuit, roles, seed, p0))

    def row(file: str, case: str, region: tuple[int, ...], roles: dict[str, int], seed: int, circuit: Any, p0: float):
        ops = circuit.count_ops()
        return {
            "file": file,
            "case": case,
            "region": list(region),
            "roles": roles,
            "seed": seed,
            "cz": ops.get("cz", 0),
            "t_count": ops.get("t", 0) + ops.get("tdg", 0),
            "ideal_p_selector_zero": round(p0, 12),
        }

    tuna: dict[str, str] = {}
    cases: dict[str, Any] = {
        "schema": "qi-zero-divisor-cases-v1",
        "backend": BACKEND,
        "backend_type_id": tuna_backend["id"],
        "nqubits": tuna_backend["nqubits"],
        "shots": SHOTS,
        **common,
        "regions": [list(r) for r in REGIONS],
        "circuits": [],
        "replicas": [],
    }
    for index in range(1, len(ROTATION) + 1):
        name = f"latin-{index}.cq"
        lines = header(NQUBITS)
        for _, region, case, circuit, roles, seed, p0 in (r for r in replicas if r[0] == index):
            lines.append(f"// region {list(region)} case {case} seed {seed} roles {roles}")
            lines += emit(circuit, dict(enumerate(region)))
            cases["replicas"].append(row(name, case, region, roles, seed, circuit, p0))
        tuna[name] = "\n".join(lines + ["", "barrier q", "b = measure q", ""])
        cases["circuits"].append({"file": name, "kind": "witness"})
    tuna.update(readout_circuits(NQUBITS))
    cases["circuits"] += [{"file": "readout-0.cq", "kind": "readout"}, {"file": "readout-1.cq", "kind": "readout"}]

    # QX serves 10 qubits, so its twin packs the six routed replicas two per
    # circuit (register slots 0-4 and 5-9) into three circuits, batched as the
    # Tuna series is.
    qx: dict[str, str] = {}
    twin: dict[str, Any] = {
        "schema": "qi-zero-divisor-cases-v1",
        "backend": "QXsinglenodesimulator",
        "backend_type_id": qx_backend["id"],
        "nqubits": qx_backend["nqubits"],
        "shots": QX_SHOTS,
        **common,
        "twin_of": BACKEND,
        "circuits": [],
        "replicas": [],
    }
    for start in range(0, len(replicas), 2):
        name = f"twin-{start // 2 + 1}.cq"
        lines = header(QX_QUBITS)
        for slot, (_, region, case, circuit, roles, seed, p0) in enumerate(replicas[start : start + 2]):
            place = {local: 5 * slot + local for local in range(5)}
            slot_roles = {role: place[region.index(q)] for role, q in roles.items()}
            lines.append(f"// tuna region {list(region)} case {case} seed {seed} slot {slot} roles {slot_roles}")
            lines += emit(circuit, place)
            twin["replicas"].append(row(name, case, region, slot_roles, seed, circuit, p0))
        qx[name] = "\n".join(lines + ["", "b = measure q", ""])
        twin["circuits"].append({"file": name, "kind": "witness"})
    return {"zero_divisor_tuna_17": finish(cases, tuna), "zero_divisor_qx": finish(twin, qx)}


def connected_regions(topology: tuple[tuple[int, int], ...], size: int = 5) -> list[tuple[int, ...]]:
    """Every connected `size`-qubit set of the topology that avoids EXCLUDED_QUBITS, in lexicographic order."""
    from itertools import combinations

    excluded = excluded_qubits()
    qubits = [q for q in range(NQUBITS) if q not in excluded]
    adjacent: dict[int, set[int]] = {q: set() for q in qubits}
    for a, b in topology:
        if a in adjacent and b in adjacent:
            adjacent[a].add(b)
            adjacent[b].add(a)
    found = []
    for members in combinations(qubits, size):
        inside = set(members)
        reached, frontier = {members[0]}, [members[0]]
        while frontier:
            for q in adjacent[frontier.pop()] & inside - reached:
                reached.add(q)
                frontier.append(q)
        if reached == inside:
            found.append(members)
    return found


def select_regions(topology: tuple[tuple[int, int], ...]) -> list[tuple[int, tuple[tuple[int, ...], ...], int]]:
    """Disjoint region pairs ranked by (routed CZ over all cases and both regions, joining couplers, regions).

    Each region runs every case once (ROTATION), so a pair costs the sum of the
    fewest-CZ routings of the three cases on each of its two regions. Joining
    couplers are the topology edges with one end in each region. REGIONS is
    the first entry. Every (region, case, seed) routing is independent and
    runs in one parallel.ordered_map; the fewest-CZ count per (region, case)
    equals routed()'s. Three disjoint regions need 15 qubits and the topology
    leaves 17 - len(EXCLUDED_QUBITS), so no triple exists here.
    """
    from itertools import combinations

    regions = connected_regions(topology)
    pairs = [pair for pair in combinations(regions, 2) if not set(pair[0]) & set(pair[1])]
    placed = sorted({region for pair in pairs for region in pair})
    items = [(case, region, seed) for region in placed for case in CASES for seed in SEEDS]
    counts = iter(parallel.ordered_map(RouteCount(topology), items))
    cost = {}
    for region in placed:
        total = 0
        for _ in CASES:
            total += min(next(counts) for _ in SEEDS)
        cost[region] = total
    ranking = []
    for first, second in pairs:
        joining = sum(1 for a, b in topology if (a in first and b in second) or (a in second and b in first))
        ranking.append((cost[first] + cost[second], (first, second), joining))
    return sorted(ranking, key=lambda row: (row[0], row[2], row[1]))


def bit(shot: str, qubit: int) -> int:
    return int(shot[len(shot) - 1 - qubit])


def wilson(k: int, n: int, z: float = 1.959963984540054) -> list[float]:
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [centre - half, centre + half]


BOOTSTRAP_DRAWS = 4000
BOOTSTRAP_SEED = 20261016


def linear(weights: dict[str, float], mean: dict[str, float], cov: dict[tuple[str, str], float]) -> dict[str, float]:
    """Value and standard error of sum_k w_k X_k from the means and covariances of the X_k."""
    value = sum(w * mean[k] for k, w in weights.items())
    variance = sum(wi * wj * cov[(i, j)] for i, wi in weights.items() for j, wj in weights.items())
    return {"value": value, "se": math.sqrt(max(variance, 0.0))}


Shots = dict[tuple[str, str], list[str]]
# Linear tests on the pooled dark, bright and fixture means, with constant offsets.
SECONDARY_TESTS = {
    "contrast_B_minus_D": {"bright": 1.0, "dark": -1.0},
    "sum_residual_D_plus_B_minus_1": {"dark": 1.0, "bright": 1.0},
    "fixture_minus_endpoint_midpoint_H": {"fixture": 1.0, "dark": -0.5, "bright": -0.5},
    "fixture_minus_half": {"fixture": 1.0},
}
SECONDARY_OFFSETS = {"sum_residual_D_plus_B_minus_1": -1.0, "fixture_minus_half": -0.5}


def secondary(replicas: list[dict[str, Any]], raw: Shots, batch_of: dict[str, str]) -> dict[str, Any]:
    """Secondary analysis, fixed after the data: same-shot covariance and the common-affine fixture test.

    The replicas of a witness circuit share every shot, so their selector
    outcomes can correlate; the pooled dark (D), bright (B) and fixture (F)
    means each average the replicas of their case across circuits, and
    Cov(D, B) collects the same-shot covariances of the dark and bright
    replicas that share a circuit. The contrast B - D and the sum residual D + B - 1 take
    that covariance with opposite signs. H = F - (D + B)/2 tests one affine
    response p_obs = u + v p_ideal for all three preparations, which places an
    ideal-1/2 fixture at the endpoint midpoint; F = 1/2 tests the fixture
    against its ideal instead. Raw quantities use the exact delta-method
    covariance from the per-circuit joint selector distribution. The
    readout-corrected quantities resample, per batch, the joint selector
    readout of that batch's two calibration circuits and then each of its
    witness circuits' joint selector outcomes (multinomial, BOOTSTRAP_DRAWS
    draws, BOOTSTRAP_SEED), and correct every circuit with its own batch's
    resampled assignment, so each calibration's sampling error propagates
    into exactly the circuits it calibrates. raw and batch_of key shots by
    (batch, file) and each witness file by its batch.
    """
    import numpy as np

    names = list(CASES)
    batches = sorted({batch_of[r["file"]] for r in replicas})
    files = {batch: sorted({r["file"] for r in replicas if batch_of[r["file"]] == batch}) for batch in batches}

    def indicator(shots: list[str], qubits: list[int]) -> Any:
        return np.array([[1 - bit(s, q) for q in qubits] for s in shots], dtype=float)

    # Raw: per-circuit covariance of the three selector-zero indicators.
    mean: dict[str, float] = {}
    cov: dict[tuple[str, str], float] = {(a, b): 0.0 for a in names for b in names}
    per_replica: dict[tuple[str, str], tuple[float, float]] = {}
    counts = {name: sum(1 for r in replicas if r["case"] == name) for name in names}
    for name in names:
        rows = [r for r in replicas if r["case"] == name]
        mean[name] = sum(r["p_selector_zero"] for r in rows) / len(rows)
    for batch, file in [(b, f) for b in batches for f in files[b]]:
        rows = [r for r in replicas if r["file"] == file]
        z = indicator(raw[(batch, file)], [r["roles"]["selector"] for r in rows])
        c = np.atleast_2d(np.cov(z, rowvar=False, bias=True)) / len(z)
        for i, ri in enumerate(rows):
            for j, rj in enumerate(rows):
                cov[(ri["case"], rj["case"])] += float(c[i, j]) / (counts[ri["case"]] * counts[rj["case"]])
            per_replica[(ri["case"], str(ri["region"]))] = (float(z[:, i].mean()), float(c[i, i]))
    tests, offsets = SECONDARY_TESTS, SECONDARY_OFFSETS
    raw_tests = {}
    for key, weights in tests.items():
        result: dict[str, Any] = linear(weights, mean, cov)
        result["value"] += offsets.get(key, 0.0)
        result["z"] = result["value"] / result["se"] if result["se"] else None
        raw_tests[key] = result
    by_region = {}
    # The regions come from the recorded replicas, in order of first appearance:
    # a retained run keeps the placement it executed.
    recorded = list(dict.fromkeys(str(r["region"]) for r in replicas))
    for region in recorded:
        d, b, f = (per_replica[(n, region)] for n in ("dark", "bright", "fixture"))
        h = f[0] - (d[0] + b[0]) / 2
        se = math.sqrt(f[1] + (d[1] + b[1]) / 4)
        contrast = b[0] - d[0]
        cse = math.sqrt(b[1] + d[1])
        by_region[region] = {
            "contrast": contrast,
            "contrast_ci95": [contrast - 1.959963984540054 * cse, contrast + 1.959963984540054 * cse],
            "H": h,
            "H_se": se,
            "H_z": h / se if se else None,
        }

    # Readout-corrected: parametric bootstrap of circuits and calibrations together.
    rng = np.random.default_rng(BOOTSTRAP_SEED)

    def joint_counts(shots: list[str], qubits: list[int]) -> tuple[Any, int]:
        codes = np.zeros(len(shots), dtype=int)
        for position, q in enumerate(qubits):
            codes += np.array([bit(s, q) for s in shots]) << position
        return np.bincount(codes, minlength=1 << len(qubits)), len(shots)

    selectors: dict[str, list[int]] = {}
    circuit_counts: dict[str, list[tuple[list[dict[str, Any]], Any, int]]] = {}
    calibration: dict[str, dict[str, tuple[Any, int]]] = {}
    for batch in batches:
        selectors[batch] = sorted({r["roles"]["selector"] for r in replicas if batch_of[r["file"]] == batch})
        circuit_counts[batch] = []
        for file in files[batch]:
            rows = [r for r in replicas if r["file"] == file]
            circuit_counts[batch].append(
                (rows, *joint_counts(raw[(batch, file)], [r["roles"]["selector"] for r in rows]))
            )
        # The ideal QX twin carries no readout circuits; its assignment is exact.
        calibration[batch] = {
            name: joint_counts(raw[(batch, name)], selectors[batch])
            for name in ("readout-0.cq", "readout-1.cq")
            if (batch, "readout-0.cq") in raw
        }
    draws: dict[str, list[float]] = {k: [] for k in tests}
    for _ in range(BOOTSTRAP_DRAWS):
        corrected: dict[str, list[float]] = {n: [] for n in names}
        for batch in batches:
            e01: dict[int, float] = {q: 0.0 for q in selectors[batch]}
            e10: dict[int, float] = {q: 0.0 for q in selectors[batch]}
            for name, (counts, n) in calibration[batch].items():
                sample = rng.multinomial(n, counts / n)
                for position, q in enumerate(selectors[batch]):
                    ones = sum(int(sample[code]) for code in range(len(sample)) if code >> position & 1) / n
                    if name == "readout-0.cq":
                        e01[q] = ones
                    else:
                        e10[q] = 1 - ones
            for members, counts, total in circuit_counts[batch]:
                sample = rng.multinomial(total, counts / total)
                for position, member in enumerate(members):
                    p_zero = sum(int(sample[code]) for code in range(len(sample)) if not code >> position & 1) / total
                    q = member["roles"]["selector"]
                    corrected[member["case"]].append((p_zero - e10[q]) / (1 - e01[q] - e10[q]))
        m = {n: sum(v) / len(v) for n, v in corrected.items()}
        for key, weights in tests.items():
            draws[key].append(sum(w * m[k] for k, w in weights.items()) + offsets.get(key, 0.0))
    corrected_tests = {}
    for key, values in draws.items():
        array = np.array(values)
        corrected_tests[key] = {
            "mean": float(array.mean()),
            "se": float(array.std(ddof=1)),
            "ci95": [float(np.quantile(array, 0.025)), float(np.quantile(array, 0.975))],
        }
    return {
        "claim_kind": "secondary analysis, fixed after the data",
        "endpoint_midpoint": (mean["dark"] + mean["bright"]) / 2,
        "raw": raw_tests,
        "raw_covariance": {f"{a},{b}": v for (a, b), v in cov.items()},
        "readout_corrected_bootstrap": corrected_tests,
        "by_region_raw": by_region,
        "bootstrap": {"draws": BOOTSTRAP_DRAWS, "seed": BOOTSTRAP_SEED},
    }


def load_series(run_dirs: list[Path]) -> tuple[dict[str, Any], Shots, dict[str, str]]:
    """The shared manifest fields, the raw shots keyed by (batch, file), and each witness file's batch.

    A run directory holds one submitted batch, named by its manifest's batch
    field; a retained run that predates batching has none and forms the single
    batch "". Every batch manifest of a series carries the same shared fields.
    The readout circuits repeat in every batch under the same file names, so a
    shot list is identified by its batch and file; a witness file belongs to
    exactly one batch of the series.
    """
    shared: dict[str, Any] | None = None
    raw: Shots = {}
    batch_of: dict[str, str] = {}
    for run_dir in run_dirs:
        cases = json.loads((run_dir / "cases.json").read_text(encoding="utf-8"))
        fields = {k: v for k, v in cases.items() if k not in {"batch", "circuits", "schema"}}
        if shared is None:
            shared = fields
        elif fields != shared:
            raise SystemExit(f"{run_dir}/cases.json describes a different series")
        batch = cases.get("batch", "")
        if not isinstance(batch, str):
            raise SystemExit(f"{run_dir}/cases.json names a non-string batch")
        for row in cases["circuits"]:
            key = (batch, row["file"])
            if key in raw:
                raise SystemExit(f"{run_dir}: {row['file']} appears twice in batch {batch!r} of the series")
            if row["kind"] != "readout":
                if row["file"] in batch_of:
                    raise SystemExit(f"{run_dir}: witness {row['file']} appears in two batches of the series")
                batch_of[row["file"]] = batch
            raw[key] = json.loads((run_dir / "raw" / f"{row['file']}.json").read_text(encoding="utf-8"))
    if shared is None:
        raise SystemExit("a series needs at least one run directory")
    return shared, raw, batch_of


def analyze(run_dirs: list[Path]) -> dict[str, Any]:
    return analyze_series(*load_series(run_dirs))


def analyze_series(cases: dict[str, Any], raw: Shots, batch_of: dict[str, str]) -> dict[str, Any]:
    """Preregistered and secondary analysis; each replica is corrected with its own batch's readout pair."""
    claim_kind = analysis_claim_kind(cases)
    for file in sorted({replica["file"] for replica in cases["replicas"]}):
        if file not in batch_of:
            raise SystemExit(f"the series lacks the batch holding {file}; analyze every batch together")
        # The ideal QX twin carries no readout circuits and takes the assignment
        # as exact; every hardware batch carries its own readout pair.
        batch = batch_of[file]
        if "twin_of" not in cases and not {(batch, "readout-0.cq"), (batch, "readout-1.cq")} <= raw.keys():
            raise SystemExit(f"batch {batch!r} holding {file} lacks its readout-0/readout-1 pair")
    replicas = []
    for replica in cases["replicas"]:
        sel = replica["roles"]["selector"]
        batch = batch_of[replica["file"]]
        shots = raw[(batch, replica["file"])]
        if "twin_of" in cases:
            zero, one = ["0" * cases["nqubits"]], ["1" * cases["nqubits"]]
        else:
            zero, one = raw[(batch, "readout-0.cq")], raw[(batch, "readout-1.cq")]
        n = len(shots)
        k = sum(1 - bit(s, sel) for s in shots)
        # Assignment: e01 = P(read 1 | prepared 0), e10 = P(read 0 | prepared 1).
        e01 = sum(bit(s, sel) for s in zero) / len(zero)
        e10 = sum(1 - bit(s, sel) for s in one) / len(one)
        p_raw = k / n
        p_corrected = (p_raw - e10) / (1 - e01 - e10)
        replicas.append(
            {
                **replica,
                "shots": n,
                "selector_zero_count": k,
                "p_selector_zero": p_raw,
                "p_selector_zero_ci95": wilson(k, n),
                "selector_e01": e01,
                "selector_e10": e10,
                "p_selector_zero_readout_corrected": p_corrected,
            }
        )
    by_case: dict[str, dict[str, Any]] = {}
    for name in CASES:
        rows = [r for r in replicas if r["case"] == name]
        k = sum(r["selector_zero_count"] for r in rows)
        n = sum(r["shots"] for r in rows)
        by_case[name] = {
            "p_selector_zero": k / n,
            "ci95": wilson(k, n),
            "readout_corrected": sum(r["p_selector_zero_readout_corrected"] for r in rows) / len(rows),
            "variance": (k / n) * (1 - k / n) / n,
        }
    dark, bright, fixture = by_case["dark"], by_case["bright"], by_case["fixture"]
    sum_residual = dark["p_selector_zero"] + bright["p_selector_zero"] - 1
    fixture_residual = fixture["p_selector_zero"] - 0.5

    def z(residual: float, variance: float) -> float | None:
        # An ideal or saturated case has zero binomial variance; its residual is then exact.
        return residual / math.sqrt(variance) if variance > 0 else (0.0 if residual == 0 else None)

    return {
        "schema": "qi-zero-divisor-analysis-v1",
        "claim_kind": claim_kind,
        "replicas": replicas,
        "by_case": by_case,
        "visibility": bright["p_selector_zero"] - dark["p_selector_zero"],
        "contraction": {
            "dark_plus_bright_minus_one": sum_residual,
            "z": z(sum_residual, dark["variance"] + bright["variance"]),
            "fixture_minus_half": fixture_residual,
            "fixture_z": z(fixture_residual, fixture["variance"]),
        },
        "kingston_comparison": KINGSTON,
        # The preregistered z-scores above use raw counts and treat replicas as
        # independent; the secondary block carries the same-shot covariance and
        # the readout-corrected uncertainty.
        "secondary": secondary(replicas, raw, batch_of),
    }


def self_test() -> None:
    catalogue = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    tuna, qx = catalogue_backends(catalogue)
    if (tuna["id"], qx["id"]) != (BACKEND_TYPE_ID, QX_BACKEND_TYPE_ID):
        raise AssertionError("retained witness backend identities were not admitted")
    rejected = 0
    for identifier, field, value in (
        (BACKEND, "topology", tuna["topology"][2:]),
        (BACKEND, "topology", [[0, 17]]),
        (BACKEND, "topology", [[0, True]]),
        (BACKEND, "nqubits", 18),
        (BACKEND, "id", 8),
        (BACKEND, "is_hardware", False),
        ("QXsinglenodesimulator", "topology", qx["topology"][1:]),
        ("QXsinglenodesimulator", "nqubits", 9),
        ("QXsinglenodesimulator", "id", 2),
    ):
        altered = copy.deepcopy(catalogue)
        next(b for b in altered["backend_types"] if b["identifier"] == identifier)[field] = value
        try:
            catalogue_backends(altered)
        except SystemExit:
            rejected += 1
        else:
            raise AssertionError(f"witness admitted a changed {identifier} {field}")
    for malformed in ({}, {"backend_types": None}, {"backend_types": [tuna, tuna, qx]}):
        try:
            catalogue_backends(malformed)
        except SystemExit:
            rejected += 1
        else:
            raise AssertionError("witness admitted a malformed or duplicate backend catalogue")
    hardware = {"backend": BACKEND, "backend_type_id": BACKEND_TYPE_ID}
    simulation = {"backend": "QXsinglenodesimulator", "backend_type_id": QX_BACKEND_TYPE_ID, "twin_of": BACKEND}
    if analysis_claim_kind(hardware) != "preregistered hardware inference":
        raise AssertionError("hardware evidence lost its classification")
    if analysis_claim_kind(simulation) != "preregistered emulator control":
        raise AssertionError("QX evidence was classified as hardware")
    for inconsistent in (
        {},
        {**hardware, "twin_of": BACKEND},
        {**simulation, "backend_type_id": 7},
        {**simulation, "backend_type_id": True},
        {k: v for k, v in simulation.items() if k != "twin_of"},
    ):
        try:
            analysis_claim_kind(inconsistent)
        except SystemExit:
            rejected += 1
        else:
            raise AssertionError("inconsistent witness backend metadata was accepted")
    excluded = excluded_qubits()
    if visibility_excluded() != EXPECTED_VISIBILITY_EXCLUDED or excluded != (0, 5, 6, 7, 9):
        raise AssertionError("the retained Ramsey visibilities no longer exclude exactly q5, q6 and q7 at the floor")
    rows = json.loads(COUPLER_ZZ_ANALYSIS.read_text(encoding="utf-8"))["targets"]
    if any(0.30 < row["min_visibility"] < 0.755 for row in rows):
        raise AssertionError("a visibility lies inside the gap between the two clusters")
    placed = [set(region) for region in REGIONS]
    if any(a & b for i, a in enumerate(placed) for b in placed[:i]) or any(set(excluded) & a for a in placed):
        raise AssertionError("REGIONS overlap or use an excluded qubit")
    if not all(region in connected_regions(TUNA17) for region in REGIONS):
        raise AssertionError("a region is disconnected in the Tuna-17 topology")
    batch_calibration_contract()
    print(
        "qi zero-divisor contracts: catalogue admission, evidence classes and per-batch readout calibration pass; "
        f"{rejected} mutations rejected"
    )


CALIBRATION_SHOTS = 512


def synthetic_series(readout_flips: dict[str, tuple[float, float]]) -> tuple[dict[str, Any], Shots, dict[str, str]]:
    """The retained Tuna-17 series manifests with seeded synthetic shots.

    Every witness circuit receives the same witness shot list, and batch B's
    readout-0 and readout-1 flip each bit with the probabilities
    readout_flips[B], drawn from one seeded generator in batch order.
    """
    import random

    root = ROOT / "results/quantum_inspire/cases/zero_divisor_tuna_17"
    manifests = [json.loads(path.read_text(encoding="utf-8")) for path in sorted(root.glob("batch-*/cases.json"))]
    cases = {k: v for k, v in manifests[0].items() if k not in {"batch", "circuits", "schema"}}
    rng = random.Random(BOOTSTRAP_SEED)
    witness = ["".join(rng.choice("01") for _ in range(NQUBITS)) for _ in range(CALIBRATION_SHOTS)]
    raw: Shots = {}
    batch_of: dict[str, str] = {}
    for manifest in manifests:
        batch = manifest["batch"]
        for row in manifest["circuits"]:
            if row["kind"] != "readout":
                raw[(batch, row["file"])] = list(witness)
                batch_of[row["file"]] = batch
                continue
            prepared = "0" if row["file"] == "readout-0.cq" else "1"
            flip = readout_flips[batch][int(prepared)]
            other = "1" if prepared == "0" else "0"
            raw[(batch, row["file"])] = [
                "".join(other if rng.random() < flip else prepared for _ in range(NQUBITS))
                for _ in range(CALIBRATION_SHOTS)
            ]
    return cases, raw, batch_of


def batch_calibration_contract() -> None:
    """A readout change in one batch moves only that batch's corrected estimates and no raw estimate.

    Two synthetic series share every witness shot and every calibration but
    batch-01's readout-1. The raw estimates of both series are equal; the
    corrected estimates of the latin-2 replicas differ between the series,
    each equal to (p - e10_B)/(1 - e01_B - e10_B) from its own batch B, while
    the latin-1 and latin-3 replicas keep their corrected values. Within one
    series, a selector qubit shared by batch-00 and batch-01 reads the same
    raw P(s = 0) from identical shots and two different corrected values. A
    batch missing its readout pair is refused.
    """
    base = {"batch-00": (0.02, 0.05), "batch-01": (0.02, 0.05), "batch-02": (0.03, 0.04)}
    first = analyze_series(*synthetic_series(base))
    series = synthetic_series({**base, "batch-01": (0.02, 0.20)})
    cases, raw, batch_of = series
    second = analyze_series(*series)
    raw_fields = ("shots", "selector_zero_count", "p_selector_zero", "p_selector_zero_ci95")
    for one, two in zip(first["replicas"], second["replicas"], strict=True):
        label = f"{two['file']} {two['case']}"
        if any(one[k] != two[k] for k in raw_fields):
            raise AssertionError(f"{label}: a batch-01 readout change moved a raw estimate")
        batch, sel = batch_of[two["file"]], two["roles"]["selector"]
        e01 = sum(bit(s, sel) for s in raw[(batch, "readout-0.cq")]) / CALIBRATION_SHOTS
        e10 = sum(1 - bit(s, sel) for s in raw[(batch, "readout-1.cq")]) / CALIBRATION_SHOTS
        expected = (two["p_selector_zero"] - e10) / (1 - e01 - e10)
        if (two["selector_e01"], two["selector_e10"], two["p_selector_zero_readout_corrected"]) != (e01, e10, expected):
            raise AssertionError(f"{label}: corrected with another batch's assignment")
        moved = one["p_selector_zero_readout_corrected"] != two["p_selector_zero_readout_corrected"]
        if moved != (batch == "batch-01"):
            raise AssertionError(f"{label}: corrected estimate moved={moved} in {batch}")

    def raw_view(analysis: dict[str, Any]) -> Any:
        by_case = {
            n: {k: v for k, v in row.items() if k != "readout_corrected"} for n, row in analysis["by_case"].items()
        }
        kept = ("raw", "raw_covariance", "by_region_raw", "endpoint_midpoint")
        return by_case, analysis["contraction"], analysis["visibility"], [analysis["secondary"][k] for k in kept]

    if raw_view(first) != raw_view(second):
        raise AssertionError("a batch-01 readout change moved a pooled raw estimate")
    if first["secondary"]["readout_corrected_bootstrap"] == second["secondary"]["readout_corrected_bootstrap"]:
        raise AssertionError("the corrected bootstrap ignored batch-01's own calibration")
    # The bootstrap centers on the point estimate from per-batch corrected
    # replicas; resampling any circuit against another batch's assignment
    # shifts the pooled tests by several bootstrap standard errors.
    for analysis in (first, second):
        corrected = {}
        for n in CASES:
            rows = [r["p_selector_zero_readout_corrected"] for r in analysis["replicas"] if r["case"] == n]
            corrected[n] = sum(rows) / len(rows)
        for key, weights in SECONDARY_TESTS.items():
            point = sum(w * corrected[n] for n, w in weights.items()) + SECONDARY_OFFSETS.get(key, 0.0)
            boot = analysis["secondary"]["readout_corrected_bootstrap"][key]
            if abs(boot["mean"] - point) > 4 * boot["se"]:
                raise AssertionError(f"{key}: bootstrap mean {boot['mean']} departs from the point estimate {point}")
    by_batch = {(batch_of[r["file"]], r["roles"]["selector"]): r for r in second["replicas"]}
    shared = {q for b, q in by_batch if b == "batch-00"} & {q for b, q in by_batch if b == "batch-01"}
    if not shared:
        raise AssertionError("batch-00 and batch-01 share no selector qubit")
    for q in sorted(shared):
        zero, one_ = by_batch[("batch-00", q)], by_batch[("batch-01", q)]
        if zero["p_selector_zero"] != one_["p_selector_zero"]:
            raise AssertionError(f"selector {q}: identical shots gave different raw estimates")
        if zero["p_selector_zero_readout_corrected"] == one_["p_selector_zero_readout_corrected"]:
            raise AssertionError(f"selector {q}: two batch calibrations gave one corrected estimate")
    partial = {key: shots for key, shots in raw.items() if key != ("batch-01", "readout-1.cq")}
    try:
        analyze_series(cases, partial, batch_of)
    except SystemExit as error:
        if "readout" not in str(error):
            raise AssertionError(f"a batch without its readout pair failed for another reason: {error}") from error
    else:
        raise AssertionError("a batch without its readout pair borrowed another batch's calibration")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--select-regions", action="store_true", help="rank the region pairs REGIONS is chosen from")
    mode.add_argument("--analyze", type=Path, nargs="+", metavar="RUN_DIR", help="the batches of one series")
    mode.add_argument(
        "--replay-series",
        type=Path,
        nargs="+",
        metavar="FILE RUN_DIR",
        help="recompute the analysis FILE over the run directories of one series and compare bytes",
    )
    mode.add_argument("--replay", type=Path, nargs="+")
    parser.add_argument("--out", type=Path, help="with --analyze: the analysis file (default RUN_DIR/analysis.json)")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.select_regions:
        ranking = select_regions(TUNA17)
        for cz, pair, joining in ranking[:10]:
            print(f"cz {cz} joining {joining} regions {[list(r) for r in pair]}")
        print(f"{len(ranking)} disjoint pairs; REGIONS {'is' if ranking[0][1] == REGIONS else 'is not'} the first")
        return 0 if ranking[0][1] == REGIONS else 1
    if args.analyze:
        if len(args.analyze) > 1 and args.out is None:
            parser.error("--analyze over several batches needs --out")
        text = json.dumps(analyze(args.analyze), indent=1) + "\n"
        (args.out or args.analyze[0] / "analysis.json").write_text(text, encoding="utf-8")
        print(text, end="")
        return 0
    if args.replay_series:
        out, *runs = args.replay_series
        if not runs:
            parser.error("--replay-series needs FILE and at least one RUN_DIR")
        if out.read_text(encoding="utf-8") != json.dumps(analyze(runs), indent=1) + "\n":
            raise SystemExit(f"{out} differs from the recomputation over its {len(runs)} batches")
        print(f"{out}: {len(runs)} batches reproduce their series analysis")
        return 0
    if args.replay:
        for run in args.replay:
            if (run / "analysis.json").read_text(encoding="utf-8") != json.dumps(analyze([run]), indent=1) + "\n":
                raise SystemExit(f"{run}/analysis.json differs from its recomputation")
        print(f"qi zero-divisor analyses: {len(args.replay)} runs reproduce their analysis.json")
        return 0
    directories = build()
    count = 0
    for directory, files in directories.items():
        if args.check:
            root = args.check / directory
            retained = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
            if retained != set(files):
                raise SystemExit(f"{root}: files {sorted(retained ^ set(files))} differ from the regeneration")
        for name, text in files.items():
            path = (args.write or args.check) / directory / name
            if args.write:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            elif path.read_text(encoding="utf-8") != text:
                raise SystemExit(f"{path} differs from its regeneration")
            count += 1
    print(f"qi zero-divisor cases: {count} files {'written' if args.write else 'match their regeneration'}")
    return 0


# A star import resolves the lazy tuple just as an explicit hardware import does.
__all__ = sorted({name for name in globals() if not name.startswith("_")} | {"EXCLUDED_QUBITS"})


if __name__ == "__main__":
    sys.exit(main())
