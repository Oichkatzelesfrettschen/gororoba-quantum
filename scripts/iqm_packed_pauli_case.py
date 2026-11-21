"""Packed Pauli response case for IQM Garnet: the 36 logical programs compiled natively, bound to a prediction.

The logical programs of results/iqm/proposals/packed-pauli-response-garnet/ (docs/design/packed-pauli-response-current-balance.md)
run twenty qubits as five disjoint four-qubit cells, four sentinel cells and one load cell, in a sparse arm that
prepares the sentinels and a dense arm that prepares every cell. This script compiles each program onto Garnet's
native basis (r, cz) with the proposal's physical map as a fixed initial layout and no routing, refuses a SWAP, a CZ
off the calibration's loci and any layout drift, keeps the preparation/readout barrier over all twenty qubits, reads
all twenty qubits in one joint measure in logical bit order, and writes one 36-circuit job in the iqm_jobs case
format. The prediction holds, per circuit and cell, the ideal outcome distribution of the logical cell and a noisy one
from an exact four-qubit density matrix of the native cell under iqm_sim's calibration noise model (PRX and CZ
depolarizing error, unheralded readout assignment; idle relaxation and crosstalk are outside the model, so the
modeled dense-minus-sparse response is exactly zero). The analysis scores each shot's sentinel cells with
packed_pauli_probe.score, forms the primary response B_Y - K_Y from the two Y-quadrature sentinel cells (2 and 3),
takes each pair's integer numerator difference dense minus sparse in units of 2g, and applies the exact
paired assignment test of packed_pauli_analysis. Mock outcomes never enter the analysis.

Usage: "$PYTHON" scripts/iqm_packed_pauli_case.py (build DIR --calibration SRC | check DIR | analyze RUN_DIR --out FILE
       [--replay] | --self-test)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit, qasm2, transpile
from qiskit.circuit.library import RGate
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import iqm_sim  # noqa: E402
import packed_pauli_analysis  # noqa: E402
import packed_pauli_probe  # noqa: E402
from iqm_jobs import CASE_SCHEMA, JOB_SECONDS, ceiling_credits, dump  # noqa: E402
from iqm_signed_probe import ACTIVE_SHOT_SECONDS, DURATIONS, target_of  # noqa: E402

import iqm_records  # noqa: E402
from parallel import ordered_map  # noqa: E402

CASE = "packed-pauli-response-garnet"
QC = "garnet"
QCS = ["garnet:mock", "garnet"]
PRICE = {"garnet": 0.5, "garnet:mock": 0.0}
PROPOSAL = ROOT / "results/iqm/proposals/packed-pauli-response-garnet"
PROPOSAL_SCHEMA = "packed-pauli-reference-proposal-v1"
CASE_DIR = ROOT / "results/iqm/cases" / CASE
OPTIONS: dict[str, Any] = {"heralding_mode": "none", "active_reset_cycles": 1}
CALIBRATION_FILES = ("metrics.json", "dynamic-quantum-architecture.json")
WIDTH = 20
CELL = 4
KERNEL_Y, BRIGHT_Y, KERNEL_X, BRIGHT_X = 2, 3, 0, 1
NATIVE_OPS = frozenset({"r", "cz", "barrier", "measure"})
DISTRIBUTION_DIGITS = 9
ANALYSIS_SCHEMA = "iqm-packed-pauli-garnet-analysis-v1"
# Twice the bounded score g in {0, 1/2, 1}: the integer numerators the exact assignment test enumerates.
SCORE2 = np.array([round(2 * packed_pauli_probe.score(label)) for label in range(16)], dtype=np.int64)
SECTOR_BIT = np.array([(label >> 2) & 1 for label in range(16)], dtype=np.int64)
PARITY = np.array([((label >> 3) ^ (label >> 1) ^ label) & 1 for label in range(16)], dtype=np.int64)
KERNEL_EVENT = SECTOR_BIT * (1 - PARITY)


class CaseError(ValueError):
    """A proposal, compile or run that this case refuses."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def ordered(names: Any) -> list[str]:
    return sorted(names, key=lambda q: int(q[2:]))


def load_proposal(directory: Path = PROPOSAL) -> tuple[dict[str, Any], list[str]]:
    """The proposal record and the QASM text of each circuit, every sha256 verified against proposal.json."""
    proposal = json.loads((directory / "proposal.json").read_text(encoding="utf-8"))
    if proposal.get("schema") != PROPOSAL_SCHEMA or proposal.get("backend") != "iqm:garnet":
        raise CaseError(f"{directory}: not a Garnet {PROPOSAL_SCHEMA} proposal")
    texts = []
    for row in proposal["circuits"]:
        data = (directory / row["file"]).read_bytes()
        if sha256(data) != row["sha256"]:
            raise CaseError(f"{directory}/{row['file']} differs from the sha256 proposal.json records")
        texts.append(data.decode("utf-8"))
    if proposal["cells"] * CELL != WIDTH or len(proposal["circuits"]) != 36:
        raise CaseError(f"{directory}: the case runs 36 circuits of {WIDTH} qubits")
    return proposal, texts


def layout_of(physical_map: dict[str, str], calibration: iqm_sim.Calibration) -> list[int]:
    """Calibration qubit index of each logical qubit; the map must be a bijection onto the calibration's qubits."""
    names = [physical_map[str(i)] for i in range(WIDTH)]
    if sorted(names) != sorted(calibration.qubits) or len(set(names)) != WIDTH:
        raise CaseError("the physical map is not a bijection onto the calibration's twenty qubits")
    return [calibration.qubits.index(name) for name in names]


def verify_native(
    compiled: QuantumCircuit, source: QuantumCircuit, physical_map: dict[str, str], calibration: iqm_sim.Calibration
) -> None:
    """Refuse a compile that routed, left the native basis, used an uncalibrated pair or moved a qubit."""
    layout = layout_of(physical_map, calibration)
    index = {q: n for n, q in enumerate(calibration.qubits)}
    for item in compiled.data:
        op = item.operation
        if op.name not in NATIVE_OPS:
            raise CaseError(f"{compiled.name}: {op.name} is not native (a SWAP or a non-native gate)")
        qubits = [compiled.find_bit(q).index for q in item.qubits]
        if op.name == "cz" and frozenset(calibration.qubits[i] for i in qubits) not in calibration.cz:
            raise CaseError(f"{compiled.name}: cz on {[calibration.qubits[i] for i in qubits]} is off the CZ loci")
        if op.name == "barrier" and sorted(qubits) != list(range(len(calibration.qubits))):
            raise CaseError(f"{compiled.name}: a barrier spans {len(qubits)} qubits, not every qubit")
    layout_object = compiled.layout
    if layout_object is None or layout_object.initial_index_layout(filter_ancillas=True) != layout:
        raise CaseError(f"{compiled.name}: the initial layout differs from the physical map")
    final = layout_object.final_index_layout(filter_ancillas=True)
    if final != list(range(len(final))) and layout_object.final_layout is not None:
        raise CaseError(f"{compiled.name}: the final layout differs from the initial one (routing)")
    wanted = {i: index[physical_map[str(i)]] for i in range(WIDTH)}
    got = {
        compiled.find_bit(item.clbits[0]).index: compiled.find_bit(item.qubits[0]).index
        for item in compiled.data
        if item.operation.name == "measure"
    }
    if got != wanted:
        raise CaseError(f"{compiled.name}: a measured bit reads another physical qubit than the map's")
    barriers = sum(item.operation.name == "barrier" for item in compiled.data)
    if barriers != sum(item.operation.name == "barrier" for item in source.data):
        raise CaseError(f"{compiled.name}: the compile changed the number of barriers")


def compile_native(
    source: QuantumCircuit, name: str, physical_map: dict[str, str], calibration: iqm_sim.Calibration
) -> QuantumCircuit:
    """Transpile onto Garnet's target (r, cz) with the map as the fixed layout and no routing; a program that needs
    routing fails here."""
    target, _ = target_of(calibration)
    try:
        compiled = transpile(
            source,
            target=target,
            initial_layout=layout_of(physical_map, calibration),
            routing_method="none",
            optimization_level=1,
        )
    except Exception as error:
        raise CaseError(f"{name}: compilation onto the mapped qubits without routing failed: {error}") from error
    compiled.name = name
    verify_native(compiled, source, physical_map, calibration)
    return compiled


def to_iqm_joint(compiled: QuantumCircuit, name: str, calibration: iqm_sim.Calibration) -> dict[str, Any]:
    """A compiled circuit as an IQM circuit: prx and cz as iqm_signed_probe.to_iqm writes them, the preparation/readout
    barrier kept as one barrier instruction over every qubit, and one joint measure in logical bit order."""
    names = calibration.qubits
    instructions: list[dict[str, Any]] = []
    measured: dict[int, str] = {}
    for item in compiled.data:
        op = item.operation
        locus = [names[compiled.find_bit(q).index] for q in item.qubits]
        if op.name == "r":
            angle, phase = (float(p) for p in op.params)
            instructions.append({"name": "prx", "locus": locus, "args": {"angle": angle, "phase": phase}})
        elif op.name == "cz":
            instructions.append({"name": "cz", "locus": locus, "args": {}})
        elif op.name == "barrier":
            instructions.append({"name": "barrier", "locus": ordered(locus), "args": {}})
        elif op.name == "measure":
            measured[compiled.find_bit(item.clbits[0]).index] = locus[0]
        else:
            raise CaseError(f"{name}: {op.name} is not a Garnet native operation")
    instructions.append(
        {"name": "measure", "locus": [measured[bit] for bit in range(len(measured))], "args": {"key": "c"}}
    )
    return {"name": name, "instructions": instructions}


def shot_path_seconds(circuit: dict[str, Any]) -> float:
    """The gate critical path of one shot: PRX and CZ durations, a barrier aligning its qubits."""
    clock: dict[str, float] = {}
    for op in circuit["instructions"]:
        if op["name"] == "measure":
            continue
        start = max((clock.get(q, 0.0) for q in op["locus"]), default=0.0)
        end = start + (DURATIONS["r"] if op["name"] == "prx" else DURATIONS["cz"] if op["name"] == "cz" else 0.0)
        for q in op["locus"]:
            clock[q] = end
    return max(clock.values(), default=0.0)


def cell_qubits(physical_map: dict[str, str], cell: int) -> list[str]:
    return [physical_map[str(CELL * cell + bit)] for bit in range(CELL)]


def logical_cell_distribution(source: QuantumCircuit, cell: int) -> np.ndarray:
    """The ideal outcome distribution of one cell of the logical program (label bit b is the cell's qubit b)."""
    part = QuantumCircuit(CELL)
    low = CELL * cell
    for item in source.data:
        indices = [source.find_bit(q).index for q in item.qubits]
        if item.operation.name in ("barrier", "measure"):
            continue
        if all(low <= i < low + CELL for i in indices):
            part.append(item.operation, [i - low for i in indices])
        elif any(low <= i < low + CELL for i in indices):
            raise CaseError(f"{source.name}: a gate couples cell {cell} to another cell")
    return np.asarray(Statevector(part).probabilities(), dtype=float)


def native_cell_circuit(circuit: dict[str, Any], qubits: list[str]) -> QuantumCircuit:
    part = QuantumCircuit(CELL)
    index = {q: b for b, q in enumerate(qubits)}
    for op in circuit["instructions"]:
        if op["name"] in ("barrier", "measure"):
            continue
        if all(q in index for q in op["locus"]):
            locus = [index[q] for q in op["locus"]]
            if op["name"] == "prx":
                part.append(RGate(op["args"]["angle"], op["args"]["phase"]), locus)
            else:
                part.cz(*locus)
        elif any(q in index for q in op["locus"]):
            raise CaseError(f"{circuit['name']}: an operation on {op['locus']} couples this cell to another")
    return part


def cell_noise_model(calibration: iqm_sim.Calibration, qubits: list[str]) -> NoiseModel:
    """The calibration's PRX and CZ depolarizing errors for one cell's qubits; readout is applied analytically."""
    model = NoiseModel(basis_gates=["r", "cz"])
    for b, qubit in enumerate(qubits):
        model.add_quantum_error(depolarizing_error(calibration.prx_p(qubit), 1), "r", [b])
    for a in range(CELL):
        for b in range(CELL):
            pair = frozenset((qubits[a], qubits[b]))
            if a != b and pair in calibration.cz:
                model.add_quantum_error(depolarizing_error(4 * (1 - calibration.cz[pair]) / 3, 2), "cz", [a, b])
    return model


def read_out(distribution: np.ndarray, calibration: iqm_sim.Calibration, qubits: list[str]) -> np.ndarray:
    """The distribution after each qubit's unheralded assignment error: P(1|0) = e01, P(0|1) = e10."""
    out = distribution.copy()
    for b, qubit in enumerate(qubits):
        e01, e10 = calibration.readout(qubit)
        nxt = np.zeros_like(out)
        for label in range(16):
            bit = (label >> b) & 1
            flipped = label ^ (1 << b)
            nxt[label] += out[label] * (1 - (e10 if bit else e01))
            nxt[flipped] += out[label] * (e10 if bit else e01)
        out = nxt
    return out


def noisy_cell_distribution(part: QuantumCircuit, calibration: iqm_sim.Calibration, qubits: list[str]) -> np.ndarray:
    """Exact four-qubit density matrix of the native cell under the calibration noise, then readout error."""
    measured = part.copy()
    measured.save_density_matrix()
    simulator = AerSimulator(method="density_matrix", noise_model=cell_noise_model(calibration, qubits))
    matrix = simulator.run(measured).result().data(0)["density_matrix"]
    diagonal = np.real(np.diag(np.asarray(matrix)))
    return read_out(diagonal / diagonal.sum(), calibration, qubits)


def means(distribution: np.ndarray) -> dict[str, float]:
    return {
        "g": round(float(distribution @ SCORE2) / 2, DISTRIBUTION_DIGITS),
        "sector": round(float(distribution @ SECTOR_BIT), DISTRIBUTION_DIGITS),
        "kernel_event": round(float(distribution @ KERNEL_EVENT), DISTRIBUTION_DIGITS),
    }


def circuit_task(item: tuple[int, dict[str, Any], str, dict[str, str], str]) -> dict[str, Any]:
    """Compile one logical program and predict each of its five cells."""
    number, row, text, physical_map, calibration_dir = item
    calibration = iqm_sim.Calibration.from_directory(Path(calibration_dir))
    name = Path(row["file"]).stem
    source = qasm2.loads(text, custom_instructions=qasm2.LEGACY_CUSTOM_INSTRUCTIONS)
    source.name = name
    compiled = compile_native(source, name, physical_map, calibration)
    native = to_iqm_joint(compiled, name, calibration)
    cells = []
    for cell in range(len(physical_map) // CELL):
        qubits = cell_qubits(physical_map, cell)
        ideal = logical_cell_distribution(source, cell)
        part = native_cell_circuit(native, qubits)
        noiseless = np.asarray(Statevector(part).probabilities(), dtype=float)
        if float(np.abs(noiseless - ideal).max()) > 1e-9:
            raise CaseError(f"{name}: cell {cell} compiled to another distribution than the logical program's")
        noisy = noisy_cell_distribution(part, calibration, qubits)
        cells.append(
            {
                "cell": cell,
                "qubits": qubits,
                "ideal": means(ideal),
                "noisy": means(noisy),
                "ideal_distribution": [round(float(v), DISTRIBUTION_DIGITS) for v in ideal],
                "noisy_distribution": [round(float(v), DISTRIBUTION_DIGITS) for v in noisy],
            }
        )
    role = {k: row[k] for k in ("kind", "pair", "dense", "reference") if k in row}
    return {
        "number": number,
        "circuit": native,
        "record": {"name": name, "file": f"circuits/{name}.json", **role, "cells": cells},
        "shot_path_seconds": shot_path_seconds(native),
    }


def primary_of(cells: list[dict[str, Any]], key: str) -> float:
    return round(cells[BRIGHT_Y][key]["g"] - cells[KERNEL_Y][key]["g"], DISTRIBUTION_DIGITS)


def build_from(calibration_dir: Path) -> tuple[dict[str, str], dict[str, Any]]:
    calibration = iqm_sim.Calibration.from_directory(calibration_dir)
    proposal, texts = load_proposal()
    physical_map = proposal["physical_map_to_be_applied_by_native_compiler"]
    layout_of(physical_map, calibration)
    results = ordered_map(
        circuit_task,
        [(i, row, texts[i], physical_map, str(calibration_dir)) for i, row in enumerate(proposal["circuits"])],
    )
    shots = proposal["shots_per_circuit"]
    files = {r["record"]["file"]: dump(r["circuit"]) for r in results}
    for r in results:
        if len(r["circuit"]["instructions"]) > 10000:
            raise CaseError(f"{r['record']['name']}: more than Garnet's 10000 instructions")
    expected = round(shots * sum(ACTIVE_SHOT_SECONDS + r["shot_path_seconds"] for r in results), 3)
    ceilings = {qc: ceiling_credits(expected, PRICE[qc], JOB_SECONDS) for qc in QCS}
    if ceilings[QC] > proposal["budget"]["maximum_planned_credits"]:
        raise CaseError(f"{ceilings[QC]} credits exceed the proposal's {proposal['budget']['maximum_planned_credits']}")
    records = [r["record"] for r in results]
    science = [r for r in records if r["kind"] == "science"]
    prediction = {
        "calibration_set": calibration.set_id,
        "proposal_sha256": sha256((PROPOSAL / "proposal.json").read_bytes()),
        "physical_map": physical_map,
        "primary": "B_Y - K_Y of sentinel cells 3 and 2, mean g per shot; pair statistic: dense minus sparse in units of 2g",
        "circuits": records,
        "predicted_primary": {
            r["name"]: {"ideal": primary_of(r["cells"], "ideal"), "noisy": primary_of(r["cells"], "noisy")}
            for r in science
        },
        "predicted_pair_difference": 0,
        "model": (
            "exact four-qubit density matrix per cell: iqm_sim depolarizing PRX and CZ, unheralded readout "
            "assignment; cells independent, no idle relaxation, crosstalk, leakage or coherent error"
        ),
    }
    files["prediction.json"] = dump(prediction)
    job = {
        "job": "packed",
        "circuits": [
            {"file": r["file"], "sha256": sha256(files[r["file"]].encode())} for r in records
        ],
        "shots": shots,
        # The job compiles against the calibration set the prediction was made from, or fails if it is gone.
        "options": {**OPTIONS, "calibration_set_id": {QC: calibration.set_id}},
        "expected_seconds": expected,
        "max_credits": ceilings,
    }
    files["cases.json"] = dump(
        {
            "schema": CASE_SCHEMA,
            "case": CASE,
            "question": (
                "Does preparing every cell of Garnet's five four-qubit cells, against only the four sentinel cells, "
                "change the sentinel Y-quadrature response B_Y - K_Y of 16 randomized dense/sparse pairs?"
            ),
            "qcs": QCS,
            "jobs": [job],
            # The approval digest of cases.json covers the prediction the analysis decides against.
            "prediction_sha256": sha256(files["prediction.json"].encode()),
        }
    )
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
    job = json.loads(files["cases.json"])["jobs"][0]
    print(
        json.dumps(
            {
                "circuits": len(job["circuits"]),
                "expected_seconds": job["expected_seconds"],
                "max_credits": job["max_credits"],
                "calibration_set": prediction["calibration_set"],
            }
        )
    )


def check(directory: Path) -> None:
    files, _ = build_from(directory / "calibration")
    present = {p.relative_to(directory).as_posix() for p in directory.rglob("*") if p.is_file()}
    expected = set(files) | {f"calibration/{name}" for name in CALIBRATION_FILES}
    if present != expected:
        raise CaseError(f"{directory}: files differ from the build: {sorted(present ^ expected)}")
    for rel, text in files.items():
        if (directory / rel).read_text(encoding="utf-8") != text:
            raise CaseError(f"{directory}/{rel} differs from the build")
    print(f"{directory}: matches the build from its retained calibration")


def shot_labels(shots: list[list[int]], cell: int) -> np.ndarray:
    bits = np.asarray(shots, dtype=np.int64)
    if bits.ndim != 2 or bits.shape[1] != WIDTH:
        raise CaseError("a shot does not hold one bit for each of the twenty qubits")
    block = bits[:, CELL * cell : CELL * cell + CELL]
    return block @ np.array([1, 2, 4, 8], dtype=np.int64)


def cell_summary(labels: np.ndarray) -> dict[str, float]:
    return {
        "g": float(SCORE2[labels].mean()) / 2,
        "sector": float(SECTOR_BIT[labels].mean()),
        "kernel_event": float(KERNEL_EVENT[labels].mean()),
    }


def analyze(run_dir: Path) -> dict[str, Any]:
    run = iqm_records.read_run(run_dir)
    # Mock outcomes are random bits and never enter the analysis.
    if run.submission["qc"] != QC or run.case.get("case") != CASE:
        raise CaseError(f"{run_dir}: a {run.case.get('case')} run on {run.submission['qc']}, not a {CASE} run on {QC}")
    prediction = json.loads((run_dir / "prediction.json").read_text(encoding="utf-8"))
    compilation = run.job.get("compilation") or {}
    if compilation.get("calibration_set_id") != prediction["calibration_set"]:
        raise CaseError(f"{run_dir}: compiled against another calibration set than the prediction's")
    measurements = run.completed_measurements()
    roles = prediction["circuits"]
    if len(measurements) != len(roles) or [c["file"] for c in run.row["circuits"]] != [r["file"] for r in roles]:
        raise CaseError(f"{run_dir}: the job's circuits are not the prediction's")
    cells_of: list[list[np.ndarray]] = []
    for role, result in zip(roles, measurements, strict=True):
        cells_of.append([shot_labels(result["c"], cell) for cell in range(len(role["cells"]))])
    pairs: dict[int, dict[bool, int]] = {}
    arms: dict[int, dict[bool, list[np.ndarray]]] = {}
    per_circuit = []
    for role, labels in zip(roles, cells_of, strict=True):
        summary = [cell_summary(x) for x in labels]
        row = {"name": role["name"], "kind": role["kind"], "cells": summary}
        if role["kind"] == "science":
            numerator = int(SCORE2[labels[BRIGHT_Y]].sum() - SCORE2[labels[KERNEL_Y]].sum())
            pairs.setdefault(role["pair"], {})[bool(role["dense"])] = numerator
            arms.setdefault(role["pair"], {})[bool(role["dense"])] = labels
            row["numerator_2g"] = numerator
        per_circuit.append(row)
    if any(set(arm) != {True, False} for arm in pairs.values()):
        raise CaseError(f"{run_dir}: a pair lacks its dense or its sparse circuit")
    order = sorted(pairs)
    differences = [pairs[p][True] - pairs[p][False] for p in order]
    p_value = packed_pauli_analysis.paired_pvalue(differences)
    shots = run.row["shots"]
    scale = 2 * shots
    predicted = prediction["predicted_primary"]
    by_name = {r["name"]: r for r in per_circuit}
    primary = {
        "pairs": len(order),
        "numerator_2g_dense_minus_sparse": differences,
        "p_value": str(p_value),
        "p_value_float": float(p_value),
        "minimum_p_value": str(Fraction(2, 2 ** len(order))),
        "reject_at_0.05": bool(p_value <= Fraction(1, 20)),
        "mean_difference": sum(differences) / (len(order) * scale),
        "dense_response": sum(pairs[p][True] for p in order) / (len(order) * scale),
        "sparse_response": sum(pairs[p][False] for p in order) / (len(order) * scale),
        "predicted_noisy_response": float(
            np.mean([predicted[r["name"]]["noisy"] for r in roles if r["kind"] == "science"])
        ),
        "predicted_ideal_response": float(
            np.mean([predicted[r["name"]]["ideal"] for r in roles if r["kind"] == "science"])
        ),
    }
    exploratory: dict[str, Any] = {"note": "exploratory: no decision rests on these"}
    dense_x = []
    sparse_x = []
    cell_gap: dict[int, list[float]] = {}
    for p in order:
        for dense, bucket in ((True, dense_x), (False, sparse_x)):
            labels = arms[p][dense]
            bucket.append(float(SCORE2[labels[BRIGHT_X]].mean() - SCORE2[labels[KERNEL_X]].mean()) / 2)
        for cell in range(len(arms[p][True])):
            gap = float(SCORE2[arms[p][True][cell]].mean() - SCORE2[arms[p][False][cell]].mean()) / 2
            cell_gap.setdefault(cell, []).append(gap)
    exploratory["x_quadrature_response"] = {
        "dense_mean": float(np.mean(dense_x)),
        "sparse_mean": float(np.mean(sparse_x)),
    }
    exploratory["per_cell_dense_minus_sparse_g"] = {
        str(cell): float(np.mean(gaps)) for cell, gaps in sorted(cell_gap.items())
    }
    exploratory["kernel_event_fraction"] = {
        str(cell): {
            "dense": float(np.mean([KERNEL_EVENT[arms[p][True][cell]].mean() for p in order])),
            "sparse": float(np.mean([KERNEL_EVENT[arms[p][False][cell]].mean() for p in order])),
        }
        for cell in range(len(arms[order[0]][True]))
    }
    references: dict[str, Any] = {}
    for role, labels in zip(roles, cells_of, strict=True):
        if role["kind"] == "reference":
            bits = np.concatenate([[(labels[c] >> b) & 1 for b in range(CELL)] for c in range(len(labels))])
            references[role["name"]] = {
                "reference": role["reference"],
                "assignment_error": float(np.mean(bits != role["reference"])),
            }
    exploratory["product_reference_assignment_error"] = references
    exploratory["drift_first_vs_last_reference_error"] = {
        str(value): [references[r["name"]]["assignment_error"] for r in roles if r["kind"] == "reference" and r["reference"] == value]
        for value in (0, 1)
    }
    return {
        "schema": ANALYSIS_SCHEMA,
        "run": run_dir.name,
        "calibration_set": compilation["calibration_set_id"],
        "estimate_seconds": compilation.get("execution_runtime_estimate_seconds"),
        "runtime_seconds": (run.job.get("metrics") or {}).get("runtime_seconds"),
        "billed_seconds": run.billed_seconds,
        "charge": round(run.billed_seconds * float(run.submission["price_per_second"]), 6),
        "primary": primary,
        "exploratory": exploratory,
        "circuits": by_name,
    }


def largest_remainder(distribution: list[float], total: int) -> list[int]:
    raw = [v * total for v in distribution]
    counts = [math.floor(v) for v in raw]
    for index in sorted(range(len(raw)), key=lambda i: (counts[i] - raw[i], i))[: total - sum(counts)]:
        counts[index] += 1
    return counts


def synthetic_shots(prediction: dict[str, Any], shots: int, mode: str) -> list[dict[str, Any]]:
    """Measurements of a model device without a random generator: every cell's noisy distribution rounded to whole
    shots and laid out by a fixed stride. null: the arms agree; alternating: one sentinel shot of the bright cell
    reads high in the dense arm of even pairs and in the sparse arm of odd pairs, so the pair differences cancel;
    planted: the dense arm's bright Y cell repeats the kernel Y cell of the same shot in 30 % of shots."""
    high = int(np.flatnonzero(SCORE2 == 2)[0])
    out = []
    for role in prediction["circuits"]:
        labels = []
        for cell in role["cells"]:
            counts = largest_remainder(cell["noisy_distribution"], shots)
            flat = np.repeat(np.arange(16), counts)
            labels.append(np.roll(flat, 37 * cell["cell"]))
        if role["kind"] == "science":
            dense = bool(role["dense"])
            if mode == "planted" and dense:
                cut = (3 * shots) // 10
                labels[BRIGHT_Y][:cut] = labels[KERNEL_Y][:cut]
            if mode == "alternating" and dense == (role["pair"] % 2 == 0):
                labels[BRIGHT_Y][0] = high
        bits = np.zeros((shots, WIDTH), dtype=np.int64)
        for cell, label in enumerate(labels):
            for bit in range(CELL):
                bits[:, CELL * cell + bit] = (label >> bit) & 1
        out.append({"c": bits.tolist()})
    return out


def synthetic_run(case_dir: Path, run_dir: Path, mode: str, qc: str = QC) -> Path:
    """A run directory of a model device over a built case, in the layout iqm_records reads."""
    shutil.copytree(case_dir, run_dir, ignore=shutil.ignore_patterns("calibration"))
    case = json.loads((run_dir / "cases.json").read_text(encoding="utf-8"))
    prediction = json.loads((run_dir / "prediction.json").read_text(encoding="utf-8"))
    row = case["jobs"][0]
    measurements = synthetic_shots(prediction, row["shots"], mode)
    raw = run_dir / "raw"
    raw.mkdir()
    job = {
        "id": "job-1",
        "status": "completed",
        "metrics": {"billed_seconds": 3.0, "runtime_seconds": 2.5},
        "compilation": {"calibration_set_id": prediction["calibration_set"], "execution_runtime_estimate_seconds": 2.0},
    }
    files = {
        "job.json": dump(job).encode(),
        "measurements.json": json.dumps(measurements).encode(),
        "measurement_counts.json": b"[]",
    }
    for name, data in files.items():
        (raw / name).write_bytes(data)
    (run_dir / "submission.json").write_text(
        dump(
            {
                "schema": iqm_records.SUBMISSION_SCHEMA,
                "job_id": "job-1",
                "qc": qc,
                "job": row["job"],
                "cases_sha256": sha256((run_dir / "cases.json").read_bytes()),
                "approval": "synthetic fixture",
                "price_per_second": PRICE[qc],
                "submitted_at": "2026-01-01T00:00:00Z",
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "results.json").write_text(
        dump(
            {
                "schema": iqm_records.RESULTS_SCHEMA,
                "job_id": "job-1",
                "status": "completed",
                "raw_sha256": {n: sha256(d) for n, d in files.items()},
                "shots_per_circuit": [row["shots"]] * len(row["circuits"]),
            }
        ),
        encoding="utf-8",
    )
    return run_dir


def expect_refusal(action: Any, fragment: str) -> None:
    try:
        action()
    except CaseError as error:
        if fragment not in str(error):
            raise RuntimeError(f"refused for another reason than {fragment!r}: {error}") from error
        return
    raise RuntimeError(f"no refusal containing {fragment!r}")


def refusal_checks(calibration: iqm_sim.Calibration, physical_map: dict[str, str]) -> None:
    """A SWAP, a CZ off the loci and an off-map layout are refused by the verifier and the compiler."""
    source = QuantumCircuit(WIDTH, WIDTH)
    source.h(0)
    source.measure(range(WIDTH), range(WIDTH))
    layout = layout_of(physical_map, calibration)
    qiskit_names = calibration.qubits
    swapped = QuantumCircuit(len(qiskit_names), WIDTH, name="swap")
    swapped.swap(0, 1)
    swapped.measure(range(WIDTH), range(WIDTH))
    expect_refusal(lambda: verify_native(swapped, source, physical_map, calibration), "not native")
    uncoupled = next(
        (a, b)
        for a in range(len(qiskit_names))
        for b in range(a + 1, len(qiskit_names))
        if frozenset((qiskit_names[a], qiskit_names[b])) not in calibration.cz
    )
    off = QuantumCircuit(len(qiskit_names), WIDTH, name="off-locus")
    off.cz(*uncoupled)
    expect_refusal(lambda: verify_native(off, source, physical_map, calibration), "off the CZ loci")
    # A program that needs a CZ between qubits the map places on uncoupled sites cannot compile without routing.
    far = QuantumCircuit(WIDTH, WIDTH, name="far")
    inverse = {name: i for i, name in enumerate(physical_map[str(i)] for i in range(WIDTH))}
    a_name, b_name = (qiskit_names[uncoupled[0]], qiskit_names[uncoupled[1]])
    far.cx(inverse[a_name], inverse[b_name])
    far.measure(range(WIDTH), range(WIDTH))
    expect_refusal(lambda: compile_native(far, "far", physical_map, calibration), "without routing failed")
    # An off-map layout: the compile of a circuit under one map checked against another.
    rotated = {str(i): physical_map[str((i + 1) % WIDTH)] for i in range(WIDTH)}
    plain = QuantumCircuit(WIDTH, WIDTH, name="plain")
    plain.measure(range(WIDTH), range(WIDTH))
    compiled = compile_native(plain, "plain", physical_map, calibration)
    expect_refusal(lambda: verify_native(compiled, plain, rotated, calibration), "differs from the physical map")
    if layout_of(physical_map, calibration) != layout:
        raise RuntimeError("layout_of is not deterministic")


def self_test() -> str:
    calibration_dir = iqm_sim.EVIDENCE / QC / "calibration"
    calibration = iqm_sim.Calibration.from_directory(calibration_dir)
    proposal, _ = load_proposal()
    refusal_checks(calibration, proposal["physical_map_to_be_applied_by_native_compiler"])
    with tempfile.TemporaryDirectory(prefix="packed-pauli-case-") as scratch:
        case_dir = Path(scratch) / "case"
        write(case_dir, calibration_dir)
        check(case_dir)
        case = json.loads((case_dir / "cases.json").read_text(encoding="utf-8"))
        prediction = json.loads((case_dir / "prediction.json").read_text(encoding="utf-8"))
        if case["prediction_sha256"] != sha256((case_dir / "prediction.json").read_bytes()):
            raise RuntimeError("cases.json does not bind the prediction it was built with")
        circuits = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((case_dir / "circuits").glob("*.json"))]
        if len(circuits) != 36 or any(not c["instructions"][-1]["name"] == "measure" for c in circuits):
            raise RuntimeError("the job is not 36 circuits ending in one joint measure")
        results = {}
        for mode in ("null", "alternating", "planted"):
            run = synthetic_run(case_dir, Path(scratch) / mode, mode)
            results[mode] = analyze(run)["primary"]
        if Fraction(results["null"]["p_value"]) != 1 or results["null"]["reject_at_0.05"]:
            raise RuntimeError(f"a null device reads {results['null']}")
        if results["alternating"]["reject_at_0.05"]:
            raise RuntimeError(f"balanced pair differences reject: {results['alternating']}")
        if Fraction(results["planted"]["p_value"]) > Fraction(1, 128):
            raise RuntimeError(f"a planted response reads {results['planted']}")
        mock = synthetic_run(case_dir, Path(scratch) / "mock", "null", qc="garnet:mock")
        expect_refusal(lambda: analyze(mock), "not a")
    return (
        f"packed Pauli Garnet case: 36 circuits, sparse arm cells {prediction['circuits'][2]['cells'][0]['qubits']}; "
        f"null p = {results['null']['p_value']}, planted p = {results['planted']['p_value']}; "
        "a SWAP, an off-locus CZ, a routed program, an off-map layout and a mock run are refused"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    sub = parser.add_subparsers(dest="command")
    bd = sub.add_parser("build")
    bd.add_argument("directory", type=Path)
    bd.add_argument("--calibration", type=Path, required=True)
    sub.add_parser("check").add_argument("directory", type=Path)
    an = sub.add_parser("analyze")
    an.add_argument("run_dir", type=Path)
    an.add_argument("--out", type=Path, required=True)
    an.add_argument("--replay", action="store_true")
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
                raise CaseError(f"{args.out} differs from the recomputation")
            print(f"{args.out}: replays byte for byte")
        else:
            args.out.write_text(text, encoding="utf-8")
    else:
        parser.error("choose a subcommand or --self-test")
    return 0


if __name__ == "__main__":
    sys.exit(main())
