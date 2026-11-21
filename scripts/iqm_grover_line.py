"""IQM Garnet case of three-qubit Grover search with a seven-CZ line-native CCZ.

Garnet's couplers form a square lattice with no triangle, so a three-qubit diagonal gate runs on a path
a-b-c whose end qubits share no coupler. CCZ is the phase polynomial
pi x0 x1 x2 = (pi/4)(x0 + x1 + x2 - x0^x1 - x0^x2 - x1^x2 + x0^x1^x2), so a CNOT network on the path's two
couplers that carries each of the seven parities onto some wire implements it with one phase gate
diag(1, exp(+-i pi/4)) per parity. line_networks() searches every reachable pair of linear map and covered
parity set breadth first: the shortest network that returns each wire to its input has 8 CNOTs, and the
shortest one that may end in a wire permutation has 7 and exchanges the middle wire with one end. Grover's
later layers act qubit by qubit, so the compiler tracks that exchange as a relabeling. A CNOT is a CZ between
Hadamards on its target; every Z rotation travels as a frame into the phase of the qubit's next prx, which
CZ commutes with, and the frame left before the measurement is dropped. A k-iteration search therefore costs
14k CZ, and the case carries the generic qiskit compile of one iteration on the same path for comparison.

Arms, one job under active reset with all-zeros heralding:
  k0                 Hadamards and measurement, the uniform reference
  m101-k1, m101-k2   marked 101 (bit q of the string is qubit q), line-native, one and two iterations
  m011-k1, m011-k2   marked 011, which is not a palindrome, so a reversed bit order shows as 110
  m101-k1-generic    marked 101, one iteration through qiskit transpile at optimization level 3 on the path;
                     it and m101-k1 run in DECISION_COPIES copies (-c1, -c2, ...) in ABBA order, so a
                     drift linear in circuit position cancels from their pooled difference
  ro-xyz             the eight basis preparations of the readout assignment matrix

The builder scores every oriented calibrated path by the mean predicted marked probability of the four
line-native arms and predicts every arm on the best one. A prediction is exact: the density matrix under
scripts/iqm_sim.py's depolarizing PRX and CZ plus idle T1 and T2 over the ASAP schedule Garnet runs
(docs/notes/iqm/README.md, "Schedule"), then each measured qubit's assignment matrix conditioned on the
all-zeros herald the job's kept shots pass. Probabilities round to 9 digits and angles to 10, which holds the
line-native circuits and the prediction across numpy's CPU dispatch; the generic copies come from qiskit's
seeded transpile, whose gate sequence follows the qiskit release, so the build runs under requirements.txt.

Usage: "$PYTHON" scripts/iqm_grover_line.py (build DIR --calibration SRC | check DIR | analyze RUN --out FILE [--replay]
       | --self-test)
"""

from __future__ import annotations

import argparse
import cmath
import itertools
import json
import math
import shutil
import sys
from collections import deque
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import CouplingMap
from qiskit_aer import AerSimulator

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import iqm_sim  # noqa: E402
from iqm_jobs import CASE_SCHEMA, JOB_SECONDS, ceiling_credits, dump  # noqa: E402
from iqm_platform import sha256  # noqa: E402
from iqm_signed_probe import ACTIVE_SHOT_SECONDS, CALIBRATION_FILES, OPTIONS, relaxed, target_of  # noqa: E402

from boolean_anf import anf_degree  # noqa: E402
from cd_core import cd_sign  # noqa: E402
from parallel import ordered_map  # noqa: E402

CASE = "grover-line-ccz"
QCS = ["garnet:mock", "garnet"]
# Pay-as-you-go price per second of each quantum computer in the 2026-11-20 snapshot (details.json pricing).
PRICE = {"garnet:mock": 0.0, "garnet": 0.5}
SHOTS = 4000
# docs/evidence/anu_qrng/draw-2026-11-16T041214Z.json#3
TRANSPILER_SEED = 53987
MARKS = ("101", "011")
DECISION_COPIES = 4
# Preregistered decision: a difference resolves when it lies Z_RESOLVE binomial standard errors from zero.
Z_RESOLVE = 3.0
EPS = 1e-12

NEEDED = (0b011, 0b101, 0b110, 0b111)
LINE_MOVES = ((0, 1), (1, 0), (1, 2), (2, 1))
IDENTITY_WIRES = (1, 2, 4)

H = np.array([[1, 1], [1, -1]], dtype=complex) / math.sqrt(2)
X = np.array([[0, 1], [1, 0]], dtype=complex)


def covered(wires: tuple[int, ...], mask: int) -> int:
    for n, parity in enumerate(NEEDED):
        if parity in wires:
            mask |= 1 << n
    return mask


def line_networks() -> dict[str, tuple[tuple[int, int], ...]]:
    """Shortest CNOT networks (control, target) on the path 0-1-2 that carry every parity of two or three
    inputs onto a wire: "fixed" ends with each wire holding its input, "exchanged" in any wire permutation."""
    full = (1 << len(NEEDED)) - 1
    start = (IDENTITY_WIRES, covered(IDENTITY_WIRES, 0))
    queue: deque[tuple[tuple[int, ...], int, tuple[tuple[int, int], ...]]] = deque([(*start, ())])
    seen: set[tuple[tuple[int, ...], int]] = {start}
    found: dict[str, tuple[tuple[int, int], ...]] = {}
    while queue and len(found) < 2:
        wires, mask, network = queue.popleft()
        if mask == full:
            if wires == IDENTITY_WIRES:
                found.setdefault("fixed", network)
            if tuple(sorted(wires)) == IDENTITY_WIRES:
                found.setdefault("exchanged", network)
        for control, target in LINE_MOVES:
            nxt = list(wires)
            nxt[target] ^= nxt[control]
            state = (tuple(nxt), covered(tuple(nxt), mask))
            if state not in seen:
                seen.add(state)
                queue.append((*state, (*network, (control, target))))
    return found


def ccz_block(network: tuple[tuple[int, int], ...]) -> tuple[list[tuple[Any, ...]], tuple[int, ...]]:
    """The network with one phase gate diag(1, exp(i theta)) on each parity's first appearance, theta = +pi/4
    for odd and -pi/4 for even weight, and the final wire contents (wire p holds input log2(wires[p]))."""
    wires = list(IDENTITY_WIRES)
    phased: set[int] = set()
    ops: list[tuple[Any, ...]] = []

    def mark() -> None:
        for position, parity in enumerate(wires):
            if parity not in phased:
                phased.add(parity)
                ops.append(("phase", position, (1 if bin(parity).count("1") % 2 else -1) * math.pi / 4))

    mark()
    for control, target in network:
        wires[target] ^= wires[control]
        ops.append(("cnot", control, target))
        mark()
    if len(phased) != 7:
        raise ValueError(f"network {network} carries {len(phased)} of the 7 parities")
    return ops, tuple(wires)


def grover_ops(marked: str, k: int) -> list[tuple[Any, ...]]:
    """Logical gates of k Grover iterations for the basis state whose bit q is marked[q]."""
    ops: list[tuple[Any, ...]] = [("h", q) for q in range(3)]
    zeros = [q for q in range(3) if marked[q] == "0"]
    for _ in range(k):
        ops += [("x", q) for q in zeros] + [("ccz",)] + [("x", q) for q in zeros]
        ops += [("h", q) for q in range(3)] + [("x", q) for q in range(3)] + [("ccz",)]
        ops += [("x", q) for q in range(3)] + [("h", q) for q in range(3)]
    return ops


def ideal_probability(k: int) -> float:
    return math.sin((2 * k + 1) * math.asin(1 / math.sqrt(8))) ** 2


def rz(gamma: float) -> np.ndarray:
    return np.diag([cmath.exp(-0.5j * gamma), cmath.exp(0.5j * gamma)])


def prx_matrix(theta: float, phi: float) -> np.ndarray:
    c, s = math.cos(theta / 2), math.sin(theta / 2)
    return np.array([[c, -1j * cmath.exp(-1j * phi) * s], [-1j * cmath.exp(1j * phi) * s, c]])


def euler(u: np.ndarray) -> tuple[float, float, float]:
    """(theta, phi, gamma) with u = exp(i delta) rz(gamma) prx(theta, phi): the prx runs first."""
    c, s = abs(u[0, 0]), abs(u[1, 0])
    theta = 2 * math.atan2(s, c)
    if s < 1e-9:
        return 0.0, 0.0, cmath.phase(u[1, 1] / u[0, 0])
    if c < 1e-9:
        return theta, 0.0, cmath.phase(u[1, 0] / u[0, 1])
    return theta, cmath.phase(1j * u[1, 0] / u[1, 1]), cmath.phase(u[1, 1] / u[0, 0])


def angle(x: float) -> float:
    return round(math.remainder(x, 2 * math.pi), 10) + 0.0


def compile_line(
    ops: list[tuple[Any, ...]], network: tuple[tuple[int, int], ...], path: list[str], name: str
) -> tuple[dict[str, Any], list[int]]:
    """Native circuit of the logical gates on path positions 0-1-2, and the final position of each logical qubit."""
    block, final = ccz_block(network)
    source = [wire.bit_length() - 1 for wire in final]
    position = [0, 1, 2]
    pending = [np.eye(2, dtype=complex) for _ in range(3)]
    out: list[dict[str, Any]] = []

    def flush(p: int) -> None:
        theta, phi, gamma = euler(pending[p])
        if theta > 1e-9:
            out.append({"name": "prx", "locus": [path[p]], "args": {"angle": angle(theta), "phase": angle(phi)}})
        pending[p] = rz(gamma)

    for op in ops:
        if op[0] in ("h", "x"):
            p = position[op[1]]
            pending[p] = (H if op[0] == "h" else X) @ pending[p]
            continue
        for item in block:
            if item[0] == "phase":
                pending[item[1]] = np.diag([1, cmath.exp(1j * item[2])]) @ pending[item[1]]
                continue
            control, target = item[1], item[2]
            pending[target] = H @ pending[target]
            flush(control)
            flush(target)
            out.append({"name": "cz", "locus": [path[control], path[target]], "args": {}})
            pending[target] = H @ pending[target]
        position = [source.index(position[q]) for q in range(3)]
    for p in range(3):
        flush(p)
    out.append({"name": "measure", "locus": [path[position[q]] for q in range(3)], "args": {"key": "m"}})
    return {"name": name, "instructions": out}, position


def generic(marked: str, path: list[str], name: str) -> dict[str, Any]:
    """One iteration through qiskit's optimization level 3 on the path's two couplers."""
    logical = QuantumCircuit(3, 3)
    for op in grover_ops(marked, 1):
        if op[0] == "h":
            logical.h(op[1])
        elif op[0] == "x":
            logical.x(op[1])
        else:
            logical.ccz(0, 1, 2)
    logical.measure(range(3), range(3))
    compiled = transpile(
        logical,
        basis_gates=["r", "cz"],
        coupling_map=CouplingMap([[0, 1], [1, 0], [1, 2], [2, 1]]),
        initial_layout=[0, 1, 2],
        optimization_level=3,
        seed_transpiler=TRANSPILER_SEED,
    )
    out: list[dict[str, Any]] = []
    readout: dict[int, str] = {}
    for item in compiled.data:
        op = item.operation
        locus = [path[compiled.find_bit(q).index] for q in item.qubits]
        if op.name == "r":
            theta, phi = (float(p) for p in op.params)
            out.append({"name": "prx", "locus": locus, "args": {"angle": angle(theta), "phase": angle(phi)}})
        elif op.name == "cz":
            out.append({"name": "cz", "locus": locus, "args": {}})
        elif op.name == "measure":
            readout[compiled.find_bit(item.clbits[0]).index] = locus[0]
        elif op.name != "barrier":
            raise ValueError(f"{name}: {op.name} is not a Garnet native operation")
    out.append({"name": "measure", "locus": [readout[q] for q in range(3)], "args": {"key": "m"}})
    return {"name": name, "instructions": out}


def readout_circuit(bits: str, path: list[str]) -> dict[str, Any]:
    out: list[dict[str, Any]] = [
        {"name": "prx", "locus": [path[q]], "args": {"angle": angle(math.pi), "phase": 0.0}}
        for q in range(3)
        if bits[q] == "1"
    ]
    out.append({"name": "measure", "locus": list(path), "args": {"key": "m"}})
    return {"name": f"ro-{bits}", "instructions": out}


Arm = tuple[str, dict[str, Any], str | None, int | None]
LINE_ARMS = (("101", 1), ("101", 2), ("011", 1), ("011", 2))


def line_arm(marked: str, k: int, path: list[str], name: str) -> Arm:
    return (name, compile_line(grover_ops(marked, k), line_networks()["exchanged"], path, name)[0], marked, k)


def arms(path: list[str]) -> list[Arm]:
    """(name, circuit, marked string, iterations) of every circuit in the job's order. The two arms of the
    line-against-generic decision run in DECISION_COPIES copies spread through the job in ABBA order (line
    first, generic first, generic first, line first), so the summed positions of the two arms are equal and a
    drift linear in circuit position cancels from their pooled difference."""

    def pair(copy: int) -> list[Arm]:
        suffix = f"-c{copy}" if copy else ""
        name = f"m101-k1-generic{suffix}"
        line = line_arm("101", 1, path, f"m101-k1{suffix}")
        other: Arm = (name, generic("101", path, name), "101", 1)
        return [line, other] if copy % 4 in (0, 3) else [other, line]

    readout: list[Arm] = [
        (f"ro-{bits}", readout_circuit(bits, path), None, None)
        for bits in ("".join(b) for b in itertools.product("01", repeat=3))
    ]
    others: list[list[Arm]] = [
        [
            line_arm("000", 0, path, "k0"),
            *(line_arm(m, k, path, f"m{m}-k{k}") for m, k in LINE_ARMS if (m, k) != ("101", 1)),
        ],
        readout[:4],
        readout[4:],
        [],
    ]
    out: list[Arm] = []
    for copy, block in zip(range(DECISION_COPIES), others, strict=True):
        out += pair(copy) + block
    return out


def logical_unitary(ops: list[tuple[Any, ...]]) -> np.ndarray:
    """8x8 unitary on basis index sum(x_q << q)."""
    u = np.eye(8, dtype=complex)
    for op in ops:
        if op[0] == "ccz":
            u = np.diag([-1 if i == 7 else 1 for i in range(8)]) @ u
        else:
            u = embed(H if op[0] == "h" else X, op[1]) @ u
    return u


def embed(gate: np.ndarray, q: int) -> np.ndarray:
    full = np.zeros((8, 8), dtype=complex)
    for i in range(8):
        for j in range(8):
            if (i ^ j) & ~(1 << q) == 0:
                full[i, j] = gate[(i >> q) & 1, (j >> q) & 1]
    return full


def native_unitary(circuit: dict[str, Any], path: list[str]) -> tuple[np.ndarray, list[int]]:
    """8x8 unitary of the prx and cz gates on basis index sum(x_p << p) over path positions, and the
    path position each measured bit reads."""
    u = np.eye(8, dtype=complex)
    measured: list[int] = []
    for op in circuit["instructions"]:
        where = [path.index(q) for q in op["locus"]]
        if op["name"] == "prx":
            u = embed(prx_matrix(op["args"]["angle"], op["args"]["phase"]), where[0]) @ u
        elif op["name"] == "cz":
            a, b = where
            u = np.diag([-1 if (i >> a) & (i >> b) & 1 else 1 for i in range(8)]) @ u
        elif op["name"] == "measure":
            measured = where
    return u, measured


def ideal_distribution(circuit: dict[str, Any], path: list[str]) -> np.ndarray:
    """Noiseless probability of each logical outcome index sum(bit_q << q), bit q from the q-th measured qubit."""
    u, measured = native_unitary(circuit, path)
    amplitudes = u[:, 0]
    out = np.zeros(8)
    for i in range(8):
        out[sum(((i >> p) & 1) << q for q, p in enumerate(measured))] += abs(amplitudes[i]) ** 2
    return out


def verify_line(ops: list[tuple[Any, ...]], circuit: dict[str, Any], position: list[int], path: list[str]) -> float:
    """Largest off-diagonal of U_native (P U_ideal)^dagger: zero when the native circuit equals the logical one
    up to the final per-qubit Z frame and the tracked relabeling P."""
    native, _ = native_unitary(circuit, path)
    permute = np.zeros((8, 8))
    for x in range(8):
        permute[sum(((x >> q) & 1) << position[q] for q in range(3)), x] = 1
    product = native @ (permute @ logical_unitary(ops)).conj().T
    return float(np.max(np.abs(product - np.diag(np.diag(product)))))


def key_of(index: int) -> str:
    return "".join(str((index >> q) & 1) for q in range(3))


def predicted(item: tuple[str, str]) -> dict[str, float]:
    """Exact predicted outcome distribution of one circuit, keyed by the marked-string convention."""
    circuit_text, calibration_dir = item
    circuit = json.loads(circuit_text)
    calibration = iqm_sim.Calibration.from_directory(Path(calibration_dir))
    target, _ = target_of(calibration)
    qiskit_circuit, bits = iqm_sim.to_qiskit(circuit, calibration)
    measured = [calibration.qubits.index(qubit) for _, qubit in bits]
    # Scheduling runs on the circuit without its measurement, so a qubit whose gates end early idles until the
    # joint measure; a measure that stays mid-circuit collapses the density matrix per shot and turns the exact
    # probabilities into a sampled average.
    unmeasured = qiskit_circuit.remove_final_measurements(inplace=False)
    scheduled = transpile(unmeasured, target=target, optimization_level=0, scheduling_method="asap")
    body = relaxed(calibration, scheduled)
    if any(item.operation.name in ("measure", "reset") for item in body.data):
        raise ValueError(f"{circuit['name']}: a measure or reset precedes the joint final measure")
    body.save_probabilities(measured)
    simulator = AerSimulator(method="density_matrix", noise_model=calibration.noise_model())
    true = np.asarray(simulator.run(body).result().data(0)["probabilities"], dtype=float)
    read = true
    for q, (_, qubit) in enumerate(bits):
        e01, e10 = calibration.readout(qubit, heralded=True)
        confusion = np.array([[1 - e01, e10], [e01, 1 - e10]])
        shaped = read.reshape(2 ** (2 - q), 2, 2**q)
        read = np.einsum("rt,atb->arb", confusion, shaped).reshape(8)
    return {key_of(i): round(float(read[i]), 9) for i in range(8)}


def oriented_paths(calibration: iqm_sim.Calibration) -> list[list[str]]:
    neighbors: dict[str, list[str]] = {q: [] for q in calibration.qubits}
    for pair in calibration.cz:
        a, b = sorted(pair, key=calibration.qubits.index)
        neighbors[a].append(b)
        neighbors[b].append(a)
    return [
        [a, b, c]
        for b in calibration.qubits
        for a, c in itertools.permutations(sorted(neighbors[b], key=calibration.qubits.index), 2)
    ]


def path_score(item: tuple[list[str], str]) -> tuple[list[str], float | None, str | None]:
    path, calibration_dir = item
    try:
        scores = []
        for marked, k in LINE_ARMS:
            _, circuit, _, _ = line_arm(marked, k, path, f"m{marked}-k{k}")
            scores.append(predicted((dump(circuit), calibration_dir))[marked])
        return path, round(sum(scores) / len(scores), 9), None
    except (KeyError, ValueError) as error:
        return path, None, f"{type(error).__name__}: {error}"


def build_from(calibration_dir: Path) -> tuple[dict[str, str], dict[str, Any]]:
    calibration = iqm_sim.Calibration.from_directory(calibration_dir)
    scored = ordered_map(path_score, [(path, str(calibration_dir)) for path in oriented_paths(calibration)])
    usable = [(score, path) for path, score, _ in scored if score is not None]
    if not usable:
        raise ValueError("no oriented path has a complete calibration")
    best = max(usable, key=lambda item: item[0])
    path = best[1]
    chosen = arms(path)
    files: dict[str, str] = {}
    for name, circuit, _, _ in chosen:
        files[f"circuits/{name}.json"] = dump(circuit)
    distributions = ordered_map(
        predicted, [(files[f"circuits/{name}.json"], str(calibration_dir)) for name, *_ in chosen]
    )
    arm_records: dict[str, Any] = {}
    for (name, circuit, marked, k), distribution in zip(chosen, distributions, strict=True):
        arm_records[name] = {
            "cz": sum(op["name"] == "cz" for op in circuit["instructions"]),
            "prx": sum(op["name"] == "prx" for op in circuit["instructions"]),
            "marked": marked,
            "iterations": k,
            "ideal_marked": None if marked is None or k is None else ideal_probability(k),
            "predicted_marked": None if marked is None else distribution[marked],
            "predicted": distribution,
        }
    expected = round(len(chosen) * SHOTS * ACTIVE_SHOT_SECONDS, 3)
    job = {
        "job": "grover",
        "circuits": [
            {"file": f"circuits/{name}.json", "sha256": sha256(files[f"circuits/{name}.json"].encode())}
            for name, *_ in chosen
        ],
        "shots": SHOTS,
        # The QPU compiles against the calibration set of the prediction, or fails if it is gone; the mock
        # twin's sets differ, so it compiles against its own default.
        "options": {**OPTIONS, "calibration_set_id": {"garnet": calibration.set_id}},
        "expected_seconds": expected,
        "max_credits": {qc: ceiling_credits(expected, PRICE[qc], JOB_SECONDS) for qc in QCS},
    }
    networks = line_networks()

    def sign(first: str, second: str) -> str:
        return "+" if arm_records[first]["predicted_marked"] > arm_records[second]["predicted_marked"] else "-"

    prediction = {
        "calibration_set": calibration.set_id,
        "networks": {kind: [list(step) for step in network] for kind, network in networks.items()},
        "path": path,
        "paths_scored": len(usable),
        "paths_skipped": [{"path": p, "reason": reason} for p, score, reason in scored if score is None],
        "best_paths": [{"path": p, "score": round(s, 4)} for s, p in sorted(usable, key=lambda item: -item[0])[:10]],
        "arms": arm_records,
        "decisions": {
            "z_resolve": Z_RESOLVE,
            "line_vs_generic": (
                f"P(m101-k1) - P(m101-k1-generic), each pooled over its {DECISION_COPIES} copies in ABBA order; "
                f"predicted sign {sign('m101-k1', 'm101-k1-generic')}"
            ),
            "pooling": (
                "every difference pools all copies of each arm: a binomial standard error from the arm's summed "
                "heralded kept shots"
            ),
            "readout_correction": (
                "reported beside the raw decisions: the 8 x 8 assignment matrix of the ro circuits, read in the "
                "physical order of their measurement locus, is permuted into each circuit's own measurement locus "
                "order before it is inverted"
            ),
            "second_iteration": {
                m: f"P(m{m}-k2) - P(m{m}-k1); predicted sign {sign(f'm{m}-k2', f'm{m}-k1')}" for m in MARKS
            },
            "bit_order": "the most frequent outcome of m011-k1 and m011-k2 is 011, not 110",
        },
        "model": (
            "exact density matrix: iqm_sim depolarizing PRX and CZ, ASAP idle T1/T2, herald-conditioned readout "
            "assignment; "
            "no coherent error, leakage or crosstalk"
        ),
    }
    files["cases.json"] = dump(
        {
            "schema": CASE_SCHEMA,
            "case": CASE,
            "question": (
                "Does three-qubit Grover search compiled with a seven-CZ line-native CCZ reach a higher marked-state "
                "probability on a Garnet path than the generic compile of the same search, and does a second "
                "iteration move it in the direction the calibration model predicts?"
            ),
            "ideal": {name: record["ideal_marked"] for name, record in arm_records.items() if record["marked"]},
            "qcs": QCS,
            "jobs": [job],
        }
    )
    files["prediction.json"] = dump(prediction)
    return files, prediction


def write(directory: Path, source: Path) -> None:
    calibration_dir = directory / "calibration"
    calibration_dir.mkdir(parents=True, exist_ok=True)
    for name in CALIBRATION_FILES:
        shutil.copyfile(source / name, calibration_dir / name)
    files, prediction = build_from(calibration_dir)
    for rel, text in files.items():
        path = directory / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    summary = {name: (a["cz"], a["predicted_marked"]) for name, a in prediction["arms"].items() if a["marked"]}
    print(json.dumps({"path": prediction["path"], "arms": summary}, indent=1))


def check(directory: Path) -> None:
    files, _ = build_from(directory / "calibration")
    present = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}
    expected = set(files) | {f"calibration/{name}" for name in CALIBRATION_FILES}
    if present != expected:
        raise ValueError(f"{directory}: files differ from the build: {sorted(present ^ expected)}")
    for rel, text in files.items():
        if (directory / rel).read_text(encoding="utf-8") != text:
            raise ValueError(f"{directory}/{rel} differs from the build")
    print(f"{directory}: matches the build from its retained calibration")


WALSH = np.array([[(-1) ** bin(s & x).count("1") for x in range(8)] for s in range(8)], dtype=float)
DECISION_ARMS = (("m101-k1", "101", 1), ("m101-k1-generic", "101", 1), ("m101-k2", "101", 2))
GROVER_ARMS = (*DECISION_ARMS, ("m011-k1", "011", 1), ("m011-k2", "011", 2))


def index_of(key: str) -> int:
    """Basis index sum(b_q << q) of an outcome key whose character q is logical qubit q."""
    return sum(int(key[q]) << q for q in range(3))


def counts_vector(counts: dict[str, int]) -> np.ndarray:
    out = np.zeros(8)
    for key, n in counts.items():
        out[index_of(key)] += n
    return out


def move_matrix(order: list[str], target: list[str]) -> np.ndarray:
    """Permutation taking an outcome index read in measurement order `target` to the index of the same physical
    outcome read in measurement order `order`."""
    move = np.zeros((8, 8))
    for x in range(8):
        move[sum(((x >> j) & 1) << order.index(target[j]) for j in range(3)), x] = 1
    return move


def relabel(matrix: np.ndarray, order: list[str], target: list[str]) -> np.ndarray:
    """An 8 x 8 matrix on outcomes read in measurement order `order`, re-expressed on outcomes read in `target`."""
    move = move_matrix(order, target)
    return move.T @ matrix @ move


def walsh_ratios(q: np.ndarray, marked: str, k: int) -> list[float]:
    """<Z_S> of q over its ideal value chi_S(marked) (8 P_k - 1) / 7, for S = 1 to 7: one global depolarizing
    factor scales every parity alike, while independent bit flips damp a weight-w parity as f^w."""
    scale = (8 * ideal_probability(k) - 1) / 7
    m = index_of(marked)
    spectrum = WALSH @ q
    return [float(spectrum[s] / ((-1) ** bin(s & m).count("1") * scale)) for s in range(1, 8)]


def hamming_profile(q: np.ndarray, marked: str) -> list[float]:
    """Share of the unmarked mass at Hamming distance 1, 2, 3 from the marked string; uniform error gives
    3/7, 3/7, 1/7."""
    m = index_of(marked)
    wrong = 1 - q[m]
    return [float(sum(q[x] for x in range(8) if bin(x ^ m).count("1") == h) / wrong) for h in (1, 2, 3)]


class Run:
    """One retained run of the case: counts per circuit, the readout assignment matrix of its ro circuits, and
    every circuit's measurement order."""

    def __init__(self, run_dir: Path) -> None:
        cases = json.loads((run_dir / "cases.json").read_text(encoding="utf-8"))
        self.prediction = json.loads((run_dir / "prediction.json").read_text(encoding="utf-8"))
        files = [c["file"] for c in cases["jobs"][0]["circuits"]]
        self.names = [Path(f).stem for f in files]
        raw = json.loads((run_dir / "raw/measurement_counts.json").read_text(encoding="utf-8"))
        if len(raw) != len(files):
            raise ValueError(f"{run_dir}: {len(raw)} count records for {len(files)} circuits")
        self.counts = {n: counts_vector(r["counts"]) for n, r in zip(self.names, raw, strict=True)}
        self.order = {}
        for name, rel in zip(self.names, files, strict=True):
            circuit = json.loads((run_dir / rel).read_text(encoding="utf-8"))
            self.order[name] = next(op["locus"] for op in circuit["instructions"] if op["name"] == "measure")
        self.ro_order = self.order["ro-000"]
        self.ro_shots = np.array([self.counts["ro-" + key_of(c)].sum() for c in range(8)])
        self.assignment = np.column_stack([self.counts["ro-" + key_of(c)] / self.ro_shots[c] for c in range(8)])

    def copies(self, base: str) -> list[str]:
        return [n for n in self.names if n == base or n.startswith(base + "-c")]

    def marked_terms(self, base: str, marked: str) -> tuple[float, float, dict[str, np.ndarray], np.ndarray]:
        """Raw and readout-corrected pooled marked frequency of an arm, with the gradient of the corrected value
        in every circuit's frequencies and in every column of the assignment matrix (delta method)."""
        names = self.copies(base)
        total = sum(self.counts[n].sum() for n in names)
        m = index_of(marked)
        raw = sum(self.counts[n][m] for n in names) / total
        corrected = 0.0
        grad_p: dict[str, np.ndarray] = {}
        grad_a = np.zeros((8, 8))
        for n in names:
            weight = self.counts[n].sum() / total
            move = move_matrix(self.ro_order, self.order[n])
            local = move.T @ self.assignment @ move
            p = self.counts[n] / self.counts[n].sum()
            q = np.linalg.solve(local, p)
            u = np.linalg.solve(local.T, np.eye(8)[m])
            corrected += weight * q[m]
            grad_p[n] = weight * u
            grad_a -= weight * np.outer(move @ u, move @ q)
        return float(raw), float(corrected), grad_p, grad_a

    def variance(self, grad_p: dict[str, np.ndarray], grad_a: np.ndarray) -> float:
        out = 0.0
        for n, g in grad_p.items():
            p = self.counts[n] / self.counts[n].sum()
            out += float(g @ ((np.diag(p) - np.outer(p, p)) / self.counts[n].sum()) @ g)
        for c in range(8):
            a = self.assignment[:, c]
            out += float(grad_a[:, c] @ ((np.diag(a) - np.outer(a, a)) / self.ro_shots[c]) @ grad_a[:, c])
        return out

    def corrected_distribution(self, base: str) -> np.ndarray:
        names = self.copies(base)
        total = sum(self.counts[n].sum() for n in names)
        out = np.zeros(8)
        for n in names:
            local = relabel(self.assignment, self.ro_order, self.order[n])
            out += np.linalg.solve(local, self.counts[n] / self.counts[n].sum()) * self.counts[n].sum() / total
        return out

    def model_distribution(self, base: str) -> np.ndarray:
        predicted = self.prediction["arms"][base]["predicted"]
        return np.array([predicted[key_of(x)] for x in range(8)])


def r6(x: float) -> float:
    return round(float(x), 6)


def analyze(run_dir: Path) -> dict[str, Any]:
    run = Run(run_dir)
    arms: dict[str, Any] = {}
    terms = {}
    for base, marked, k in GROVER_ARMS:
        raw, corrected, grad_p, grad_a = run.marked_terms(base, marked)
        terms[base] = (raw, corrected, grad_p, grad_a)
        names = run.copies(base)
        kept = int(sum(run.counts[n].sum() for n in names))
        pooled = sum(run.counts[n] for n in names) / kept
        q = run.corrected_distribution(base)
        model = run.model_distribution(base)
        predicted = run.prediction["arms"][base]["predicted_marked"]
        ratios = walsh_ratios(q, marked, k)
        model_ratios = walsh_ratios(model, marked, k)
        arms[base] = {
            "copies": names,
            "kept_shots": kept,
            "raw_marked": r6(raw),
            "corrected_marked": r6(corrected),
            "corrected_marked_se": r6(math.sqrt(run.variance(grad_p, grad_a))),
            "predicted_marked": predicted,
            "ideal_marked": r6(ideal_probability(k)),
            "raw_excess_over_predicted": r6((raw - 0.125) / (predicted - 0.125)),
            "corrected_retention": r6((corrected - 0.125) / (ideal_probability(k) - 0.125)),
            "tvd_raw_to_model": r6(0.5 * float(np.abs(pooled - model).sum())),
            "hellinger_fidelity_raw_to_model": r6(float(np.sqrt(pooled * model).sum()) ** 2),
            "most_frequent": key_of(int(np.argmax(pooled))),
            "walsh_ratio": {key_of(s): r6(ratios[s - 1]) for s in range(1, 8)},
            "walsh_ratio_by_weight": {
                str(w): r6(np.mean([ratios[s - 1] for s in range(1, 8) if bin(s).count("1") == w])) for w in (1, 2, 3)
            },
            "model_walsh_ratio_by_weight": {
                str(w): r6(np.mean([model_ratios[s - 1] for s in range(1, 8) if bin(s).count("1") == w]))
                for w in (1, 2, 3)
            },
            "hamming_profile": [r6(x) for x in hamming_profile(q, marked)],
            "logical_bit_error": [r6(sum(q[x] for x in range(8) if (x ^ index_of(marked)) >> b & 1)) for b in range(3)],
            "measured_on": run.order[names[0]],
        }
        if len(names) > 1:
            freqs = [run.counts[n][index_of(marked)] / run.counts[n].sum() for n in names]
            chi2 = sum(
                (f - raw) ** 2 / (raw * (1 - raw) / run.counts[n].sum()) for f, n in zip(freqs, names, strict=True)
            )
            positions = [run.names.index(n) for n in names]
            arms[base]["copy_frequencies"] = [r6(f) for f in freqs]
            arms[base]["copy_positions"] = positions
            arms[base]["copy_chi2"] = r6(chi2)
            arms[base]["copy_slope_per_position"] = r6(np.polyfit(positions, freqs, 1)[0])

    def difference(first: str, second: str) -> dict[str, Any]:
        a, b = arms[first], arms[second]
        raw = a["raw_marked"] - b["raw_marked"]
        se = math.sqrt(sum(x["raw_marked"] * (1 - x["raw_marked"]) / x["kept_shots"] for x in (a, b)))
        _, ca, pa, ga = terms[first]
        _, cb, pb, gb = terms[second]
        grads = dict(pa)
        for n, g in pb.items():
            grads[n] = grads.get(n, np.zeros(8)) - g
        corrected_se = math.sqrt(run.variance(grads, ga - gb))
        z = raw / se
        verdict = "positive" if z >= Z_RESOLVE else "negative" if z <= -Z_RESOLVE else "unresolved"
        return {
            "raw": r6(raw),
            "se": r6(se),
            "z": r6(z),
            "verdict": verdict,
            "corrected": r6(ca - cb),
            "corrected_se": r6(corrected_se),
        }

    retention = {}
    for m in MARKS:
        one = arms[f"m{m}-k1"]["corrected_retention"]
        two = arms[f"m{m}-k2"]["corrected_retention"]
        retention[m] = {"k1": one, "k2": two, "per_iteration": r6(two / one)}
    k0 = run.counts["k0"] / run.counts["k0"].sum()
    k0_corrected = np.linalg.solve(relabel(run.assignment, run.ro_order, run.order["k0"]), k0)
    return {
        "run": run_dir.resolve().relative_to(ROOT).as_posix(),
        "readout_assignment_diagonal": {key_of(c): r6(run.assignment[c, c]) for c in range(8)},
        "arms": arms,
        "decisions": {
            "line_vs_generic": difference("m101-k1", "m101-k1-generic"),
            "second_iteration": {m: difference(f"m{m}-k2", f"m{m}-k1") for m in MARKS},
            "bit_order": {n: arms[n]["most_frequent"] for n in ("m011-k1", "m011-k2")},
        },
        "retention": retention,
        "generic_retention_over_line": r6(
            arms["m101-k1-generic"]["corrected_retention"] / arms["m101-k1"]["corrected_retention"]
        ),
        "k0": {
            "raw": {key_of(x): r6(k0[x]) for x in range(8)},
            "corrected": {key_of(x): r6(k0_corrected[x]) for x in range(8)},
            "chi2_uniform_raw": r6(float(((k0 - 0.125) ** 2 / (0.125 * 0.875 / run.counts["k0"].sum())).sum())),
        },
    }


def analysis_selftest() -> None:
    for marked, k in (("101", 1), ("011", 2)):
        ideal = np.full(8, (1 - ideal_probability(k)) / 7)
        ideal[index_of(marked)] = ideal_probability(k)
        if max(abs(r - 1) for r in walsh_ratios(ideal, marked, k)) > 1e-12:
            raise AssertionError("the ideal Grover distribution has a Walsh ratio other than 1")
        noisy = 0.8 * ideal + 0.2 / 8
        if max(abs(r - 0.8) for r in walsh_ratios(noisy, marked, k)) > 1e-12:
            raise AssertionError("global depolarizing noise does not scale every parity alike")
        if max(abs(a - b) for a, b in zip(hamming_profile(noisy, marked), (3 / 7, 3 / 7, 1 / 7), strict=True)) > 1e-12:
            raise AssertionError("uniform error does not spread 3/7, 3/7, 1/7 over the Hamming shells")
    for n in (3, 4, 5):
        degrees = {anf_degree([(1 - cd_sign(2**n, m, q)) // 2 for q in range(2**n)]) for m in range(1, 2**n)}
        if degrees != {n - 1}:
            raise AssertionError(f"left-multiplication signs of dimension {2**n} have degrees {degrees}, not {n - 1}")
    flip = np.array([[0.9, 0.2], [0.1, 0.8]])
    product = np.kron(np.kron(np.eye(2), flip), np.eye(2))
    moved = relabel(product, ["A", "B", "C"], ["B", "C", "A"])
    if not np.allclose(moved, np.kron(np.kron(np.eye(2), np.eye(2)), flip)):
        raise AssertionError("relabel does not carry qubit B's readout to its new measurement position")


def self_test() -> str:
    analysis_selftest()
    networks = line_networks()
    if [len(networks["fixed"]), len(networks["exchanged"])] != [8, 7]:
        raise AssertionError(f"network lengths {[len(n) for n in networks.values()]}, expected fixed 8, exchanged 7")
    for kind, network in networks.items():
        _, final = ccz_block(network)
        if kind == "fixed" and final != IDENTITY_WIRES:
            raise AssertionError("the fixed network moves a wire")
        if tuple(sorted(final)) != IDENTITY_WIRES:
            raise AssertionError(f"the {kind} network ends in a non-permutation {final}")
    edges = (0.0, 1e-7, 0.3, math.pi / 2, 2.0, math.pi - 1e-7, math.pi)
    for theta, phi, gamma, delta in itertools.product(
        edges, (-3.0, -0.7, 0.0, 1.1, math.pi), (-2.5, 0.0, 0.9), (0.0, 1.3)
    ):
        u = cmath.exp(1j * delta) * rz(gamma) @ prx_matrix(theta, phi)
        a, b, c = euler(u)
        overlap = abs(np.trace((rz(c) @ prx_matrix(a, b)).conj().T @ u)) / 2
        if abs(overlap - 1) > 1e-10:
            raise AssertionError(f"euler round trip of theta {theta}, phi {phi}, gamma {gamma}: overlap {overlap}")
    path = ["QA", "QB", "QC"]
    worst = 0.0
    for kind, network in networks.items():
        for marked in ("000", "101", "011", "110", "111"):
            for k in (0, 1, 2, 3):
                ops = grover_ops(marked, k)
                circuit, position = compile_line(ops, network, path, "t")
                worst = max(worst, verify_line(ops, circuit, position, path))
                cz = sum(op["name"] == "cz" for op in circuit["instructions"])
                if cz != 2 * k * len(network):
                    raise AssertionError(f"{kind} {marked} k={k}: {cz} CZ")
                p = ideal_distribution(circuit, path)[int(marked[::-1], 2)]
                if abs(p - ideal_probability(k)) > 1e-9:
                    raise AssertionError(f"{kind} {marked} k={k}: P(marked) {p}, law {ideal_probability(k)}")
    if worst > 1e-8:
        raise AssertionError(f"a line-native circuit differs from its logical circuit by {worst}")
    gen = generic("101", path, "g")
    p_generic = ideal_distribution(gen, path)
    p_line = ideal_distribution(compile_line(grover_ops("101", 1), networks["exchanged"], path, "l")[0], path)
    if float(np.max(np.abs(p_generic - p_line))) > 1e-9:
        raise AssertionError("the generic compile's distribution differs from the line-native one")
    if any(op["name"] == "cz" and set(op["locus"]) == {"QA", "QC"} for op in gen["instructions"]):
        raise AssertionError("the generic compile uses the absent end-to-end coupler")
    for bits in ("".join(b) for b in itertools.product("01", repeat=3)):
        if ideal_distribution(readout_circuit(bits, path), path)[int(bits[::-1], 2)] < 1 - 1e-12:
            raise AssertionError(f"readout preparation {bits} misses its state")
    generic_cz = sum(op["name"] == "cz" for op in gen["instructions"])
    return (
        f"iqm_grover_line self-test passed: networks 8 and 7 CNOTs, unitary residual {worst:.1e}, "
        f"generic one-iteration CZ {generic_cz}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")
    b = sub.add_parser("build")
    b.add_argument("directory", type=Path)
    b.add_argument(
        "--calibration", type=Path, required=True, help="folder of metrics.json and dynamic-quantum-architecture.json"
    )
    sub.add_parser("check").add_argument("directory", type=Path)
    an = sub.add_parser("analyze")
    an.add_argument("run_dir", type=Path)
    an.add_argument("--out", type=Path, required=True)
    an.add_argument("--replay", action="store_true", help="compare with the retained file instead of writing it")
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
    elif args.command == "build":
        write(args.directory, args.calibration)
    elif args.command == "check":
        check(args.directory)
    elif args.command == "analyze":
        text = dump(analyze(args.run_dir))
        if args.replay:
            if args.out.read_text(encoding="utf-8") != text:
                raise ValueError(f"{args.out} differs from the analysis of {args.run_dir}")
            print(f"{args.out}: matches the analysis of {args.run_dir}")
        else:
            args.out.write_text(text, encoding="utf-8")
    else:
        parser.error("a subcommand or --self-test is required")
    return 0


if __name__ == "__main__":
    sys.exit(main())
