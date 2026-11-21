"""IQM Garnet follow-up case: Grover depth, single-qubit load, qubit-versus-position, and sedenion sign-row
Walsh spectroscopy, built on the line-native CCZ compile of scripts/iqm_grover_line.py.

The retained grover-line-ccz run (docs/design/iqm-garnet-grover-line-ccz.md) leaves four questions this case
answers in two jobs on one calibration set:

Job "grover" (three qubits, the retained path FORWARD_PATH and its reversal):
  m101-k1, m101-k1-fused, m101-k1-generic   one iteration three ways: line-native (14 CZ), the
                     generic qiskit compile of the retained case (18 CZ, grover.generic at the retained
                     seed grover.TRANSPILER_SEED) with its single-qubit runs fused into one prx per qubit
                     between CZs ("fused"), and that compile as emitted ("generic"); fused against generic
                     changes only the prx count at a fixed CZ sequence, line against fused changes the CZ
                     sequence. Four copies each, in blocks L F G and G F L mirrored about the job's center,
                     so a drift linear in position cancels from every pairwise contrast.
  m101-k2, m101-k3, m011-k1, m011-k2, m011-k3, k0   the depth series on FORWARD_PATH: three depths test the
                     geometric retention law lambda_k = A r^k that two depths fit exactly.
  r-m101-k1, r-m011-k1, r-k0   the same circuits on the reversed path: each physical qubit takes another
                     logical role, so a per-qubit error profile that follows the qubit stays and one that
                     follows the role moves.
  ro-xyz             the eight readout preparations on FORWARD_PATH (the reversed arms measure the same qubits).

Job "sedenion" (four qubits on a square):
  s5-row, s5-trunc, s10-row, s10-trunc, s-id   H on every wire, a phase oracle, H on every wire. The row is
                     the left sign row diag(cd_sign(16, m, x)) of the sedenion basis element e_m
                     (gororoba_quantum/sedenion_sign_oracle.py): 8 CNOTs on the square for m = 5 and m = 10,
                     whose two bits sit on opposite corners. Its ideal output is 9/16 on one string, 1/16 on
                     seven, 0 on eight. trunc is the mutation: the degree-two truncation of the row's sign
                     polynomial, realized by the same CNOT network with four of the eight phases set to zero, so
                     the physical CZ sequence is identical and only virtual frames differ; its ideal output puts
                     1/4 on four strings. id sets every phase to zero, the null arm, ideal output all zeros. Row
                     and truncation run row, trunc, trunc, row per m; id opens and closes the job.
  ro4-wxyz           the sixteen readout preparations on the square.

Path and square selection are fixed before any prediction: the Grover arms run on the retained case's path
(no re-selection on this calibration) and its reversal; the square is the one of the calibration's squares
whose predicted mean peak probability of the two rows is highest, labeled from its lowest-index qubit toward
that qubit's lower-index square neighbor. Every prediction is the exact density matrix of
iqm_grover_line.predicted's model (depolarizing PRX and CZ, idle T1 and T2 over the ASAP schedule,
herald-conditioned readout), generalized here to four qubits.

Usage: "$PYTHON" scripts/iqm_garnet_followup.py (build DIR --calibration SRC | check DIR | --self-test)
"""

from __future__ import annotations

import argparse
import cmath
import itertools
import json
import math
import shutil
import sys
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import transpile
from qiskit_aer import AerSimulator

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import iqm_grover_line as grover  # noqa: E402
import iqm_sim  # noqa: E402
from iqm_jobs import CASE_SCHEMA, JOB_SECONDS, ceiling_credits, dump  # noqa: E402
from iqm_platform import sha256  # noqa: E402
from iqm_signed_probe import ACTIVE_SHOT_SECONDS, CALIBRATION_FILES, OPTIONS, relaxed, target_of  # noqa: E402

import sedenion_sign_oracle as sed  # noqa: E402
from grover_line_analysis import ideal_probability  # noqa: E402
from parallel import ordered_map  # noqa: E402

CASE = "grover-depth-sedenion-walsh"
QCS = ["garnet:mock", "garnet"]
PRICE = grover.PRICE
SHOTS = {"grover": 4000, "sedenion": 1000}
RETAINED_CASE = ROOT / "results" / "iqm" / "cases" / grover.CASE
FORWARD_PATH = ["QB20", "QB16", "QB17"]
REVERSED_PATH = FORWARD_PATH[::-1]
ROWS = (5, 10)
COPIES = 4
KINDS = ("fused", "generic")
DEPTHS = (("101", 2), ("101", 3), ("011", 1), ("011", 2), ("011", 3))
H = grover.H
X = grover.X

Arm = dict[str, Any]


def count(circuit: dict[str, Any], name: str) -> int:
    return sum(op["name"] == name for op in circuit["instructions"])


def fused(circuit: dict[str, Any], path: list[str], name: str) -> dict[str, Any]:
    """The circuit with every run of prx between two CZ on one qubit fused into one prx, the residual Z rotation
    carried as a frame through the CZ (which commutes with it) into the next prx and dropped before the measure;
    the CZ sequence and its loci are unchanged."""
    pending = [np.eye(2, dtype=complex) for _ in path]
    out: list[dict[str, Any]] = []
    measure: dict[str, Any] | None = None

    def flush(p: int) -> None:
        theta, phi, gamma = grover.euler(pending[p])
        if theta > 1e-9:
            out.append(
                {"name": "prx", "locus": [path[p]], "args": {"angle": grover.angle(theta), "phase": grover.angle(phi)}}
            )
        pending[p] = grover.rz(gamma)

    for op in circuit["instructions"]:
        if op["name"] == "prx":
            p = path.index(op["locus"][0])
            pending[p] = grover.prx_matrix(op["args"]["angle"], op["args"]["phase"]) @ pending[p]
        elif op["name"] == "cz":
            for q in op["locus"]:
                flush(path.index(q))
            out.append(op)
        elif op["name"] == "measure":
            measure = op
        else:
            raise ValueError(f"{name}: unexpected {op['name']}")
    if measure is None:
        raise ValueError(f"{name}: no measurement")
    for p in range(len(path)):
        flush(p)
    out.append(measure)
    return {"name": name, "instructions": out}


def compile_native(ops: list[tuple[Any, ...]], path: list[str], name: str) -> dict[str, Any]:
    """Native prx and cz of logical gates on path positions ("h", p), ("x", p), ("phase", p, angle) and
    ("cnot", c, t), a CNOT as H CZ H on its target, Z rotations carried as frames; measures every position in
    path order."""
    pending = [np.eye(2, dtype=complex) for _ in path]
    out: list[dict[str, Any]] = []

    def flush(p: int) -> None:
        theta, phi, gamma = grover.euler(pending[p])
        if theta > 1e-9:
            out.append(
                {"name": "prx", "locus": [path[p]], "args": {"angle": grover.angle(theta), "phase": grover.angle(phi)}}
            )
        pending[p] = grover.rz(gamma)

    for op in ops:
        if op[0] in ("h", "x"):
            pending[op[1]] = (H if op[0] == "h" else X) @ pending[op[1]]
        elif op[0] == "phase":
            pending[op[1]] = np.diag([1, cmath.exp(1j * op[2])]) @ pending[op[1]]
        elif op[0] == "cnot":
            control, target = op[1], op[2]
            pending[target] = H @ pending[target]
            flush(control)
            flush(target)
            out.append({"name": "cz", "locus": [path[control], path[target]], "args": {}})
            pending[target] = H @ pending[target]
        else:
            raise ValueError(f"{name}: unknown logical gate {op[0]}")
    for p in range(len(path)):
        flush(p)
    out.append({"name": "measure", "locus": list(path), "args": {"key": "m"}})
    return {"name": name, "instructions": out}


def embed(gate: np.ndarray, q: int, n: int) -> np.ndarray:
    full = np.zeros((2**n, 2**n), dtype=complex)
    for i in range(2**n):
        for j in range(2**n):
            if (i ^ j) & ~(1 << q) == 0:
                full[i, j] = gate[(i >> q) & 1, (j >> q) & 1]
    return full


def ideal(circuit: dict[str, Any], path: list[str]) -> np.ndarray:
    """Noiseless probability of each outcome index sum(bit_q << q), bit q read from the q-th measured qubit."""
    n = len(path)
    state = np.zeros(2**n, dtype=complex)
    state[0] = 1
    measured: list[int] = []
    for op in circuit["instructions"]:
        where = [path.index(q) for q in op["locus"]]
        if op["name"] == "prx":
            state = embed(grover.prx_matrix(op["args"]["angle"], op["args"]["phase"]), where[0], n) @ state
        elif op["name"] == "cz":
            a, b = where
            state = np.array([-v if (i >> a) & (i >> b) & 1 else v for i, v in enumerate(state)])
        elif op["name"] == "measure":
            measured = where
    out = np.zeros(2**n)
    for i in range(2**n):
        out[sum(((i >> p) & 1) << q for q, p in enumerate(measured))] += abs(state[i]) ** 2
    return out


def key(index: int, n: int) -> str:
    return "".join(str((index >> q) & 1) for q in range(n))


def predicted(item: tuple[str, str]) -> dict[str, float]:
    """iqm_grover_line.predicted's exact model for a circuit on any number of measured qubits."""
    circuit_text, calibration_dir = item
    circuit = json.loads(circuit_text)
    calibration = iqm_sim.Calibration.from_directory(Path(calibration_dir))
    target, _ = target_of(calibration)
    qiskit_circuit, bits = iqm_sim.to_qiskit(circuit, calibration)
    measured = [calibration.qubits.index(qubit) for _, qubit in bits]
    unmeasured = qiskit_circuit.remove_final_measurements(inplace=False)
    scheduled = transpile(unmeasured, target=target, optimization_level=0, scheduling_method="asap")
    body = relaxed(calibration, scheduled)
    if any(item.operation.name in ("measure", "reset") for item in body.data):
        raise ValueError(f"{circuit['name']}: a measure or reset precedes the joint final measure")
    body.save_probabilities(measured)
    simulator = AerSimulator(method="density_matrix", noise_model=calibration.noise_model())
    read = np.asarray(simulator.run(body).result().data(0)["probabilities"], dtype=float)
    n = len(bits)
    for q, (_, qubit) in enumerate(bits):
        e01, e10 = calibration.readout(qubit, heralded=True)
        confusion = np.array([[1 - e01, e10], [e01, 1 - e10]])
        read = np.einsum("rt,atb->arb", confusion, read.reshape(2 ** (n - 1 - q), 2, 2**q)).reshape(2**n)
    return {key(i, n): round(float(read[i]), 9) for i in range(2**n)}


def readout_circuit(bits: str, path: list[str], prefix: str) -> dict[str, Any]:
    out: list[dict[str, Any]] = [
        {"name": "prx", "locus": [path[q]], "args": {"angle": grover.angle(math.pi), "phase": 0.0}}
        for q in range(len(path))
        if bits[q] == "1"
    ]
    out.append({"name": "measure", "locus": list(path), "args": {"key": "m"}})
    return {"name": f"{prefix}-{bits}", "instructions": out}


def oracle_angles(m: int, kind: str) -> dict[int, int]:
    """Parity angles in eighths of pi: the row, its degree-two truncation, or none (the identity)."""
    bits = sed.row_bits(m)
    if kind == "row":
        return sed.phase_eighths(bits)
    if kind == "trunc":
        return sed.phase_eighths(sed.truncated_bits(bits))
    if kind == "id":
        return {}
    raise ValueError(kind)


def sedenion_circuit(m: int, kind: str, square: list[str], name: str) -> tuple[dict[str, Any], np.ndarray]:
    """The native circuit H, oracle, H on the square, and its ideal distribution from the 16 x 16 algebra
    (H P D H on |0000>, P the network's final relabeling and D the oracle's diagonal)."""
    row = sed.phase_eighths(sed.row_bits(m))
    net, final = sed.network("square", frozenset(row), False)
    angles = oracle_angles(m, kind)
    oracle, _ = sed.oracle_ops(net, angles)
    ops: list[tuple[Any, ...]] = [("h", p) for p in range(4)] + oracle + [("h", p) for p in range(4)]
    h4: np.ndarray = np.ones((1, 1))
    for _ in range(4):
        h4 = np.kron(H, h4)
    state = h4 @ sed.relabeling(final) @ np.diag(sed.diagonal_of(angles)) @ h4[:, 0]
    return compile_native(ops, square, name), np.abs(state) ** 2


def squares(calibration: iqm_sim.Calibration) -> list[list[str]]:
    """Every four-cycle of the coupler graph, labeled from its lowest-index qubit toward that qubit's
    lower-index neighbor on the cycle."""
    order = calibration.qubits.index
    adjacent: dict[str, set[str]] = {q: set() for q in calibration.qubits}
    for pair in calibration.cz:
        a, b = tuple(pair)
        adjacent[a].add(b)
        adjacent[b].add(a)
    found: set[frozenset[str]] = set()
    out: list[list[str]] = []
    for a in calibration.qubits:
        for b, d in itertools.combinations(sorted(adjacent[a], key=order), 2):
            for c in sorted((adjacent[b] & adjacent[d]) - {a}, key=order):
                cycle = frozenset((a, b, c, d))
                if cycle in found:
                    continue
                found.add(cycle)
                start = min(cycle, key=order)
                ring = [a, b, c, d]
                i = ring.index(start)
                ring = ring[i:] + ring[:i]
                if order(ring[3]) < order(ring[1]):
                    ring = [ring[0], ring[3], ring[2], ring[1]]
                out.append(ring)
    return out


def square_score(item: tuple[list[str], str]) -> tuple[list[str], float | None, str | None]:
    square, calibration_dir = item
    try:
        peaks = []
        for m in ROWS:
            circuit, p = sedenion_circuit(m, "row", square, f"s{m}-row")
            peaks.append(predicted((dump(circuit), calibration_dir))[key(int(np.argmax(p)), 4)])
        return square, round(sum(peaks) / len(peaks), 9), None
    except (KeyError, ValueError) as error:
        return square, None, f"{type(error).__name__}: {error}"


def grover_arms() -> list[Arm]:
    path, rev = FORWARD_PATH, REVERSED_PATH

    def line(marked: str, k: int, p: list[str], name: str) -> Arm:
        circuit = grover.line_arm(marked, k, p, name)[1]
        return {"name": name, "circuit": circuit, "path": p, "marked": marked, "k": k}

    def one_iteration(kind: str, copy: int) -> Arm:
        name = "m101-k1" + ("" if kind == "line" else f"-{kind}") + f"-c{copy}"
        if kind == "line":
            return line("101", 1, path, name)
        generic = grover.generic("101", path, name)
        circuit = generic if kind == "generic" else fused(generic, path, name)
        return {"name": name, "circuit": circuit, "path": path, "marked": "101", "k": 1}

    # Copy blocks sit at positions mirrored about the job's center, each block the reverse of its mirror, so
    # every arm's summed position is equal and a drift linear in position cancels from each pairwise contrast.
    blocks = [
        [one_iteration(kind, copy) for kind in (order if copy in (0, 2) else order[::-1])]
        for copy, order in zip(range(COPIES), [("line", "fused", "generic")] * COPIES, strict=True)
    ]
    depth = [line("000", 0, path, "k0"), *(line(m, k, path, f"m{m}-k{k}") for m, k in DEPTHS)]
    reversed_arms = [line("101", 1, rev, "r-m101-k1"), line("011", 1, rev, "r-m011-k1"), line("000", 0, rev, "r-k0")]
    readout = [
        {"name": c["name"], "circuit": c, "path": path, "marked": None, "k": None}
        for c in (readout_circuit("".join(b), path, "ro") for b in itertools.product("01", repeat=3))
    ]
    out = blocks[0] + readout[:4] + blocks[1] + depth + reversed_arms + blocks[2] + readout[4:] + blocks[3]
    total = len(out)
    sums = {kind: sum(n for n, a in enumerate(out) if a["name"].startswith(f"m101-k1-{kind}-c")) for kind in KINDS}
    sums["line"] = sum(n for n, a in enumerate(out) if a["name"].startswith("m101-k1-c"))
    if len(set(sums.values())) != 1 or any(
        out[n]["name"].rsplit("-c", 1)[0] != out[total - 1 - n]["name"].rsplit("-c", 1)[0]
        for n in range(total)
        if out[n]["name"].startswith("m101-k1")
    ):
        raise AssertionError(f"one-iteration copies are not mirrored: summed positions {sums}")
    return out


def sedenion_arms(square: list[str]) -> list[Arm]:
    def arm(m: int, kind: str, name: str) -> Arm:
        circuit, p = sedenion_circuit(m, kind, square, name)
        return {"name": name, "circuit": circuit, "path": square, "m": m, "kind": kind, "ideal": p}

    first = [arm(ROWS[0], "id", "s-id-c0")]
    for m in ROWS:
        first += [arm(m, "row", f"s{m}-row-c0"), arm(m, "trunc", f"s{m}-trunc-c0")]
    last = []
    for m in reversed(ROWS):
        last += [arm(m, "trunc", f"s{m}-trunc-c1"), arm(m, "row", f"s{m}-row-c1")]
    last.append(arm(ROWS[0], "id", "s-id-c1"))
    readout = [
        {"name": c["name"], "circuit": c, "path": square, "m": None, "kind": None, "ideal": None}
        for c in (readout_circuit("".join(b), square, "ro4") for b in itertools.product("01", repeat=4))
    ]
    return first + readout + last


# Heralded kept fraction of the retained run (13,700 kept of 16,000 requested in the line arm, 85.6 %).
KEPT = 0.856


def se_difference(p1: float, n1: float, p2: float, n2: float) -> float:
    return math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)


def retention(p: float, k: int) -> float:
    return (p - 1 / 8) / (ideal_probability(k) - 1 / 8)


def build_from(calibration_dir: Path) -> tuple[dict[str, str], dict[str, Any]]:
    calibration = iqm_sim.Calibration.from_directory(calibration_dir)
    retained = json.loads((RETAINED_CASE / "prediction.json").read_text(encoding="utf-8"))
    if retained["path"] != FORWARD_PATH:
        raise ValueError(f"the retained case ran on {retained['path']}, not {FORWARD_PATH}")
    scored = ordered_map(square_score, [(s, str(calibration_dir)) for s in squares(calibration)], min_items=1)
    usable = [(score, s) for s, score, _ in scored if score is not None]
    if not usable:
        raise ValueError("no square has a complete calibration")
    square = max(usable, key=lambda item: item[0])[1]
    jobs = {"grover": grover_arms(), "sedenion": sedenion_arms(square)}
    files: dict[str, str] = {}
    for arms in jobs.values():
        for arm in arms:
            files[f"circuits/{arm['name']}.json"] = dump(arm["circuit"])
    names = [arm["name"] for arms in jobs.values() for arm in arms]
    distributions = ordered_map(
        predicted, [(files[f"circuits/{name}.json"], str(calibration_dir)) for name in names], min_items=1
    )
    predictions = dict(zip(names, distributions, strict=True))
    arm_records: dict[str, Any] = {}
    for job, arms in jobs.items():
        for arm in arms:
            c = arm["circuit"]
            record: dict[str, Any] = {
                "job": job,
                "locus": c["instructions"][-1]["locus"],
                "cz": count(c, "cz"),
                "prx": count(c, "prx"),
                "predicted": predictions[arm["name"]],
            }
            if job == "grover" and arm["marked"] is not None:
                record |= {
                    "marked": arm["marked"],
                    "iterations": arm["k"],
                    "ideal_marked": ideal_probability(arm["k"]),
                    "predicted_marked": predictions[arm["name"]][arm["marked"]],
                }
            if job == "sedenion" and arm["kind"] is not None:
                row_ideal = sedenion_circuit(arm["m"], "row", square, "x")[1]
                peak = key(int(np.argmax(row_ideal)), 4)
                record |= {
                    "m": arm["m"],
                    "kind": arm["kind"],
                    "row_peak": peak,
                    "ideal": {key(i, 4): round(float(v), 9) for i, v in enumerate(arm["ideal"]) if v > 1e-12},
                    "predicted_row_peak": predictions[arm["name"]][peak],
                }
            arm_records[arm["name"]] = record
    job_records = []
    for job, arms in jobs.items():
        expected = round(len(arms) * SHOTS[job] * ACTIVE_SHOT_SECONDS, 3)
        job_records.append(
            {
                "job": job,
                "circuits": [
                    {
                        "file": f"circuits/{a['name']}.json",
                        "sha256": sha256(files[f"circuits/{a['name']}.json"].encode()),
                    }
                    for a in arms
                ],
                "shots": SHOTS[job],
                "options": {**OPTIONS, "calibration_set_id": {"garnet": calibration.set_id}},
                "expected_seconds": expected,
                "max_credits": {qc: ceiling_credits(expected, PRICE[qc], JOB_SECONDS) for qc in QCS},
            }
        )
    prediction = {
        "calibration_set": calibration.set_id,
        "forward_path": FORWARD_PATH,
        "reversed_path": REVERSED_PATH,
        "square": square,
        "squares_scored": [{"square": s, "score": round(v, 4)} for v, s in sorted(usable, key=lambda i: -i[0])],
        "squares_skipped": [{"square": s, "reason": r} for s, v, r in scored if v is None],
        "arms": arm_records,
        "decisions": decisions(arm_records),
        "model": (
            "exact density matrix: iqm_sim depolarizing PRX and CZ, ASAP idle T1/T2, herald-conditioned readout "
            "assignment; no coherent error, leakage or crosstalk"
        ),
    }
    files["cases.json"] = dump(
        {
            "schema": CASE_SCHEMA,
            "case": CASE,
            "question": (
                "On one Garnet calibration: does the line-native Grover retention stay geometric at a third depth, "
                "does fusing the generic compile's single-qubit gates recover its loss, does the per-qubit error "
                "profile follow the qubit or the logical role, and does a sedenion left sign row imprint its exact "
                "Walsh peak, against its degree-two truncation on the same CZ sequence?"
            ),
            "qcs": QCS,
            "jobs": job_records,
        }
    )
    files["prediction.json"] = dump(prediction)
    return files, prediction


def pooled(arms: dict[str, Any], stem: str, outcome: str) -> tuple[float, float]:
    """Mean predicted probability of one outcome over the copies of an arm, and the kept shots they pool."""
    copies = [a for name, a in arms.items() if name == stem or name.startswith(stem + "-c")]
    shots = SHOTS[copies[0]["job"]] * KEPT * len(copies)
    return sum(a["predicted"][outcome] for a in copies) / len(copies), shots


def decision(arms: dict[str, Any], first: str, second: str, outcome: str, rule: str) -> dict[str, Any]:
    p1, n1 = pooled(arms, first, outcome)
    p2, n2 = pooled(arms, second, outcome)
    se = se_difference(p1, n1, p2, n2)
    return {
        "rule": rule,
        "predicted": round(p1 - p2, 4),
        "se_at_planned_shots": round(se, 4),
        "predicted_z": round((p1 - p2) / se, 1),
    }


def decisions(arms: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {
        "z_resolve": grover.Z_RESOLVE,
        "prx_load": decision(
            arms,
            "m101-k1-fused",
            "m101-k1-generic",
            "101",
            "P(101) of fused minus generic, four copies each: the effect of 30 prx at a fixed 18-CZ sequence",
        ),
        "cz_sequence": decision(
            arms,
            "m101-k1",
            "m101-k1-fused",
            "101",
            "P(101) of line minus fused: 14 CZ and 22 prx against 18 CZ and 38 prx",
        ),
    }
    for marked in grover.MARKS:
        p = {k: pooled(arms, f"m{marked}-k{k}", marked)[0] for k in (1, 2, 3)}
        lam = {k: retention(p[k], k) for k in p}
        extrapolated = lam[2] ** 2 / lam[1]
        n = SHOTS["grover"] * KEPT
        se3 = math.sqrt(p[3] * (1 - p[3]) / n) / (ideal_probability(3) - 1 / 8)
        out[f"depth_law_{marked}"] = {
            "rule": (
                "lambda_3 minus lambda_2^2 / lambda_1 (raw marked probabilities; the corrected values are "
                "reported beside): zero under lambda_k = A r^k"
            ),
            "predicted_lambda": {str(k): round(v, 4) for k, v in lam.items()},
            "predicted": round(lam[3] - extrapolated, 4),
            "se_lambda3_at_planned_shots": round(se3, 4),
        }
    out["role_or_qubit"] = {
        "rule": (
            "per physical qubit, the probability that its measured bit differs from the marked bit, pooled over "
            "m101-k1 and m011-k1 on each path; the qubit hypothesis keeps QB20 lowest on both paths, the role "
            "hypothesis moves the lowest wrong-bit probability with the logical position"
        ),
        "retained": {"QB20": 0.154, "QB16": 0.180, "QB17": 0.178},
    }
    for m in ROWS:
        out[f"sedenion_{m}"] = decision(
            arms,
            f"s{m}-row",
            f"s{m}-trunc",
            arms[f"s{m}-row-c0"]["row_peak"],
            f"P(row peak) of row minus truncation for e_{m}, two copies each on one CZ sequence",
        )
        out[f"sedenion_{m}"]["null_floor"] = round(pooled(arms, "s-id", arms[f"s{m}-row-c0"]["row_peak"])[0], 4)
    return out


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
    print(json.dumps({"square": prediction["square"], "decisions": prediction["decisions"]}, indent=1))


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


def self_test() -> str:
    """Every circuit of both jobs against its exact ideal on placeholder qubits."""
    path = ["QA", "QB", "QC"]
    generic = grover.generic("101", path, "g")
    merged = fused(generic, path, "f")
    if count(merged, "cz") != count(generic, "cz") or count(merged, "prx") >= count(generic, "prx"):
        raise AssertionError(f"fusion gives {count(merged, 'cz')} CZ and {count(merged, 'prx')} prx")
    if [op["locus"] for op in merged["instructions"] if op["name"] == "cz"] != [
        op["locus"] for op in generic["instructions"] if op["name"] == "cz"
    ]:
        raise AssertionError("fusion moved a CZ")
    if float(np.max(np.abs(ideal(merged, path) - ideal(generic, path)))) > 1e-9:
        raise AssertionError("the fused compile's distribution differs from the generic one")
    for marked, k in DEPTHS:
        p = ideal(grover.line_arm(marked, k, path, "t")[1], path)[int(marked[::-1], 2)]
        if abs(p - ideal_probability(k)) > 1e-9:
            raise AssertionError(f"line m{marked}-k{k}: P(marked) {p}")
    reversed_line = grover.line_arm("101", 1, path[::-1], "r")[1]
    forward_line = grover.line_arm("101", 1, path, "f")[1]
    if reversed_line["instructions"][-1]["locus"] == forward_line["instructions"][-1]["locus"]:
        raise AssertionError("the reversed path leaves every logical role on the same qubit")
    square = ["QA", "QB", "QC", "QD"]
    for m in ROWS:
        peaks = {}
        for kind in ("row", "trunc", "id"):
            circuit, want = sedenion_circuit(m, kind, square, "s")
            got = ideal(circuit, square)
            if float(np.max(np.abs(got - want))) > 1e-9:
                raise AssertionError(
                    f"e_{m} {kind}: native distribution differs from the algebra by {np.abs(got - want).max()}"
                )
            if count(circuit, "cz") != 8:
                raise AssertionError(f"e_{m} {kind}: {count(circuit, 'cz')} CZ")
            peaks[kind] = got
        top = int(np.argmax(peaks["row"]))
        if abs(peaks["row"][top] - 9 / 16) > 1e-9 or peaks["trunc"][top] > 0.25 + 1e-9 or peaks["id"][0] < 1 - 1e-9:
            raise AssertionError(f"e_{m}: peak {peaks['row'][top]}, truncation {peaks['trunc'][top]}")
        loci = [
            [op["locus"] for op in sedenion_circuit(m, kind, square, "s")[0]["instructions"] if op["name"] == "cz"]
            for kind in ("row", "trunc", "id")
        ]
        if not loci[0] == loci[1] == loci[2]:
            raise AssertionError(f"e_{m}: the row, truncation and identity differ in their CZ sequence")
    return (
        f"iqm_garnet_followup self-test passed: fused generic {count(merged, 'cz')} CZ {count(merged, 'prx')} prx "
        f"(emitted {count(generic, 'prx')}), sedenion rows {ROWS} at 8 CZ"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")
    b = sub.add_parser("build")
    b.add_argument("directory", type=Path)
    b.add_argument("--calibration", type=Path, required=True)
    sub.add_parser("check").add_argument("directory", type=Path)
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
    elif args.command == "build":
        write(args.directory, args.calibration)
    elif args.command == "check":
        check(args.directory)
    else:
        parser.error("choose build, check or --self-test")
    return 0


if __name__ == "__main__":
    sys.exit(main())
