"""IQM Garnet case of the complex kernel map of A_5: the S phases that turn the real nullity into the complex one.

The pathion kernel map reads the nullity N of L_(e_i + t e_j) over C from the selector bit of a 6-qubit circuit
(docs/evidence/a5-complex-kernel-map). This case reads the same strata on coset blocks of 2 to 4 qubits
(gororoba_quantum/pathion_complex_block.py): the selector-zero difference of the two orientations is N / 16 on every
coset of a subspace whose dimension d is 1 (N = 0 or 16), 3 (N = 4 or 12) or 2 (N = 8), so one block per operand
reads N. Each operand runs the real kind (t = 1), the complex kind (t = i) and, at two operands, the plain-phase
mutation, all in the orientations + and - in the order +, -, -, + and mirrored about the center of the job.

The four operands sit on one patch of four qubits (a star about QB6), so the null operand's offset applies to the
others. The phase gates of a block are Z rotations behind barriers: after the compile every Z rotation moves to the end
of the circuit as a shift of the phase of each later PRX, so the real and complex circuits (and both orientations) carry
the same PRX amplitudes and CZ gates and differ in PRX phases alone. A PRX amplitude error is then the same
over-rotation in every kind of an operand; the audit in prediction.json measures what remains of its effect.

Usage: "$PYTHON" scripts/iqm_complex_kernel_case.py build DIR [--calibration SRC | --live]
       "$PYTHON" scripts/iqm_complex_kernel_case.py check DIR
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import math
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import RGate, RZZGate
from qiskit.transpiler import CouplingMap
from qiskit_aer import AerSimulator

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import iqm_sim  # noqa: E402
from iqm_jobs import CANCEL_MARGIN, CASE_SCHEMA, ceiling_seconds, dump  # noqa: E402
from iqm_platform import sha256  # noqa: E402
from iqm_signed_probe import CALIBRATION_FILES, OPTIONS, relaxed, target_of  # noqa: E402

import a5_complex_kernel_decision as decision  # noqa: E402
import grover_plane_sizing as sizing  # noqa: E402
import pathion_complex_block as pcx  # noqa: E402
import pathion_coset_block as pcb  # noqa: E402
from parallel import ordered_map  # noqa: E402

CASE = "a5-complex-kernel-garnet"
QCS = ["garnet:mock", "garnet"]
PRICED = {"garnet:mock": False, "garnet": True}
RETAINED_CALIBRATION = ROOT / "results/iqm/cases/grover-plane-mirrored/calibration"
OWNER_BOUND_CREDITS = 11.0
CEILING_CREDITS = 10.5
MAX_CIRCUITS = 100
MAX_EXECUTIONS = 2_000_000
OVERRUNS = (1.0, 1.5, 2.2)
# Transpiler seeds: ANU QRNG draw docs/evidence/anu_qrng/draw-2026-11-27T222523Z.json, indices 10 to 17 (record
# docs/evidence/qrng_seeds/allocations.json). The first seed compiles the coset and layout search; the others are
# trials at the chosen layout.
TRANSPILER_SEEDS = (37071, 270, 57975, 32200, 15385, 32776, 46268, 18502)
GATE_DURATIONS = {"prx": 16, "cz": 40, "measure": 480}
# Planning floor of the herald-kept fraction of the shots (the analysis reads the kept counts of the run).
PLANNING_RETENTION = 0.5
ORIENTATIONS = ("plus", "minus", "minus", "plus")
# One star of four qubits about QB6 holds every operand; local qubit n of a compile is PATCH[n].
PATCH = ("QB11", "QB5", "QB6", "QB7")
PATCH_EDGES = ((2, 0), (2, 1), (2, 3))
PRX_ERRORS = (-0.05, -0.04, -0.03, -0.02, -0.01, 0.01, 0.02, 0.03, 0.04, 0.05)
ZZ_ERRORS = (-0.05, 0.05)


@dataclass(frozen=True)
class Operand:
    """One pair of imaginary units, its coset-block subspace and the kinds it runs."""

    name: str
    pair: tuple[int, int]
    basis: tuple[int, ...]
    stratum: str  # real / complex nullity of e_i + e_j and e_i + i e_j
    kinds: tuple[str, ...]


OPERANDS = (
    Operand("s016", (1, 3), (2,), "0/16", ("real", "cplx", "plain")),
    Operand("s412", (1, 26), (27, 4, 9), "4/12", ("real", "cplx", "plain")),
    Operand("s808", (1, 10), (11, 4), "8/8", ("real", "cplx")),
    Operand("s124", (1, 18), (19, 4, 8), "12/4", ("real", "cplx")),
)
KIND_ORDER = tuple((op.name, kind) for op in OPERANDS for kind in op.kinds)


def patch_coupling() -> CouplingMap:
    return CouplingMap([e for a, b in PATCH_EDGES for e in ((a, b), (b, a))])


def structural_compile(block: pcb.Block, plain: bool, layout: tuple[int, ...], seed: int) -> QuantumCircuit:
    """The symbolic template on the patch star in the basis r, cz and rz (calibration-free)."""
    return transpile(
        pcx.block_template(block, plain=plain),
        basis_gates=["r", "cz", "rz"],
        coupling_map=patch_coupling(),
        optimization_level=3,
        seed_transpiler=seed,
        initial_layout=list(layout),
    )


def cz_of(circuit: QuantumCircuit) -> int:
    return int(circuit.count_ops().get("cz", 0))


def block_of(operand: Operand) -> pcb.Block:
    """The coset of the operand's subspace that carries its readings. Without a plain kind, the first coset. With one,
    among the cosets where the plain reading is negative (the mutation flips the sign), the coset whose plain compile
    has the CZ count closest to the real compile's (identity layout), then the fewest CZ, then the lowest plain
    reading, then the lowest coset index."""
    i, j = operand.pair
    basis = pcx.normalized_basis((i, j, 1), operand.basis)
    cosets = pcb.cosets(basis)
    if "plain" not in operand.kinds:
        return pcb.Block(operand.name, (i, j, 1), basis, cosets[0])
    layout = tuple(range(len(basis) + 1))
    rows = []
    for coset in cosets:
        block = pcb.Block(operand.name, (i, j, 1), basis, coset)
        plain = pcx.selector_marginal(block, 1j, plain=True)
        if plain >= -1e-9:
            continue
        real_cz = cz_of(structural_compile(block, False, layout, TRANSPILER_SEEDS[0]))
        plain_cz = cz_of(structural_compile(block, True, layout, TRANSPILER_SEEDS[0]))
        rows.append((abs(plain_cz - real_cz), real_cz, plain, coset))
    return pcb.Block(operand.name, (i, j, 1), basis, min(rows)[3])


def ideal_difference(block: pcb.Block, kind: str) -> float:
    """The selector-zero difference D of the kind on the block (exact)."""
    if kind == "plain":
        return pcx.selector_marginal(block, 1j, plain=True)
    return pcx.selector_marginal(block, 1 if kind == "real" else 1j)


def usable_qubits(calibration: iqm_sim.Calibration) -> set[str]:
    """Qubits of the calibration with herald-conditioned readout, relaxation times and a PRX fidelity."""
    return {
        q
        for q in calibration.qubits
        if all(
            iqm_sim.READOUT_FIELD.format(q=q, kind=kind) + iqm_sim.HERALD_SUFFIX in calibration.values
            for kind in ("error_0_to_1", "error_1_to_0")
        )
        and all(f"characterization.model.{q}.{kind}" in calibration.values for kind in ("t1_time", "t2_time"))
        and (q in calibration.prx or iqm_sim.PRX_FIELD.format(q=q) in calibration.values)
    }


def check_patch(calibration: iqm_sim.Calibration) -> None:
    """The patch qubits are usable and the patch edges are calibrated couplers."""
    missing = [q for q in PATCH if q not in usable_qubits(calibration)]
    edges = [frozenset((PATCH[a], PATCH[b])) for a, b in PATCH_EDGES]
    absent = [sorted(e) for e in edges if e not in calibration.cz]
    if missing or absent:
        raise ValueError(f"patch {PATCH}: qubits {missing} are unusable and couplers {absent} are uncalibrated")


def modeled(calibration: iqm_sim.Calibration) -> iqm_sim.Calibration:
    """The calibration with the unheralded readout copied into any missing herald-conditioned field, so that the noise
    model builds for the whole register; the patch holds every circuit, and check_patch keeps its qubits usable."""
    clone = copy.copy(calibration)
    clone.values = dict(calibration.values)
    for q in calibration.qubits:
        for kind in ("error_0_to_1", "error_1_to_0"):
            field = iqm_sim.READOUT_FIELD.format(q=q, kind=kind)
            clone.values.setdefault(field + iqm_sim.HERALD_SUFFIX, calibration.values[field])
    return clone


def eliminate_frames(circuit: QuantumCircuit) -> QuantumCircuit:
    """The circuit with every Z rotation moved to the end and dropped: r(theta, phi) after Rz(a) equals Rz(a) after
    r(theta, phi - a), CZ commutes with Z and a Z before a measurement is no change of the outcome. Barriers go."""
    out = QuantumCircuit(*circuit.qregs, *circuit.cregs)
    pending: dict[int, float] = {}
    for item in circuit.data:
        op = item.operation
        qubits = [circuit.find_bit(q).index for q in item.qubits]
        if op.name == "rz":
            pending[qubits[0]] = pending.get(qubits[0], 0.0) + float(op.params[0])
        elif op.name == "r":
            theta, phi = (float(p) for p in op.params)
            shifted = (phi - pending.get(qubits[0], 0.0) + math.pi) % (2 * math.pi) - math.pi
            out.append(RGate(theta, shifted), item.qubits)
        elif op.name != "barrier":
            out.append(op, item.qubits, item.clbits)
    return out


def bind(compiled: QuantumCircuit, label: str, plus: bool) -> QuantumCircuit:
    """The bound circuit on its patch qubits with the frames eliminated: PRX and CZ and measures alone."""
    bound = compiled.assign_parameters({pcx.ORIENTATION: float(np.pi) if plus else 0.0, pcx.PHASE: pcx.ANGLES[label]})
    return eliminate_frames(bound)


def amplitudes(circuit: QuantumCircuit) -> list[tuple[str, tuple[int, ...], float]]:
    """(name, qubits, theta) of every PRX and CZ in order; equal lists mean equal amplitudes."""
    return [
        (i.operation.name, tuple(circuit.find_bit(q).index for q in i.qubits), round(float(i.operation.params[0]), 12))
        if i.operation.name == "r"
        else (i.operation.name, tuple(circuit.find_bit(q).index for q in i.qubits), 0.0)
        for i in circuit.data
        if i.operation.name in ("r", "cz")
    ]


def embed(circuit: QuantumCircuit, calibration: iqm_sim.Calibration) -> QuantumCircuit:
    """The patch circuit on the calibration's register (local qubit n on PATCH[n])."""
    wide = QuantumCircuit(len(calibration.qubits), circuit.num_clbits)
    wide.compose(circuit, qubits=[calibration.qubits.index(PATCH[n]) for n in range(circuit.num_qubits)], inplace=True)
    return wide


def to_iqm(bound: QuantumCircuit, name: str) -> dict[str, Any]:
    """The native circuit: prx, cz and one joint measure under the key m in classical-bit order, on PATCH."""
    instructions: list[dict[str, Any]] = []
    measured: dict[int, str] = {}
    for item in bound.data:
        op, locus = item.operation, [PATCH[bound.find_bit(q).index] for q in item.qubits]
        if op.name == "r":
            angle, phase = (round(float(p), 10) for p in op.params)
            instructions.append({"name": "prx", "locus": locus, "args": {"angle": angle, "phase": phase}})
        elif op.name == "cz":
            instructions.append({"name": "cz", "locus": locus, "args": {}})
        elif op.name == "measure":
            measured[bound.find_bit(item.clbits[0]).index] = locus[0]
        elif op.name != "barrier":
            raise ValueError(f"{name}: {op.name} is not a Garnet native operation")
    instructions.append({"name": "measure", "locus": [measured[c] for c in sorted(measured)], "args": {"key": "m"}})
    return {"name": name, "instructions": instructions}


def schedule_nanoseconds(circuit: dict[str, Any]) -> int:
    """ASAP duration of a circuit on its qubits plus the joint measurement."""
    clock: dict[str, int] = {}
    for op in circuit["instructions"]:
        if op["name"] == "measure":
            continue
        start = max(clock.get(q, 0) for q in op["locus"])
        for q in op["locus"]:
            clock[q] = start + GATE_DURATIONS[op["name"]]
    return max(clock.values(), default=0) + GATE_DURATIONS["measure"]


def exact_law(
    bound: QuantumCircuit,
    calibration: iqm_sim.Calibration,
    *,
    schedule: str = "asap",
    prx_scale: float = 0.0,
    zz: float = 0.0,
) -> np.ndarray:
    """The outcome law over the measured bits (index = sum of bit c times 2^c) of the circuit on the calibration's
    register: depolarizing PRX and CZ, idle T1 and T2 relaxation over the schedule (ASAP, as the idle-schedule case
    measured on Garnet), herald-conditioned readout; exact density matrix of the touched qubits, no sampling. A coherent
    error enters after the scheduling: every PRX angle times 1 + prx_scale, and an RZZ(zz) after every CZ."""
    target, _ = target_of(calibration)
    scheduled = transpile(embed(bound, calibration), target=target, optimization_level=0, scheduling_method=schedule)
    noisy = relaxed(calibration, scheduled)
    measures = sorted(
        (noisy.find_bit(i.clbits[0]).index, noisy.find_bit(i.qubits[0]).index)
        for i in noisy.data
        if i.operation.name == "measure"
    )
    body = QuantumCircuit(*noisy.qregs)
    for item in noisy.data:
        op = item.operation
        if op.name == "measure":
            continue
        if op.name == "r" and prx_scale:
            theta, phi = (float(p) for p in op.params)
            body.append(RGate(theta * (1 + prx_scale), phi), item.qubits)
            continue
        body.append(op, item.qubits, item.clbits)
        if op.name == "cz" and zz:
            body.append(RZZGate(zz), item.qubits)
    body.save_probabilities_dict([q for _, q in measures])
    simulator = AerSimulator(method="density_matrix", noise_model=modeled(calibration).noise_model(heralded=True))
    raw = simulator.run(body, shots=1).result().data()["probabilities"]
    n = len(measures)
    law = np.zeros(1 << n)
    for key, value in raw.items():
        law[int(key, 16) if str(key).startswith("0x") else int(key)] = value
    for c, (_, q) in enumerate(measures):
        e01, e10 = calibration.readout(calibration.qubits[q], heralded=True)
        confusion = np.array([[1 - e01, e10], [e01, 1 - e10]])
        law = np.moveaxis(
            np.tensordot(confusion, np.moveaxis(law.reshape([2] * n), n - 1 - c, 0), axes=(1, 0)), 0, n - 1 - c
        ).reshape(-1)
    return law


def selector_zero(law: np.ndarray, d: int) -> float:
    """P(selector bit d = 0) of a law over d + 1 bits."""
    return float(law[: 1 << d].sum())


def operand_named(name: str) -> Operand:
    return next(op for op in OPERANDS if op.name == name)


def layout_trial(item: tuple[str, tuple[int, ...], int, str]) -> dict[str, Any]:
    """One layout (virtual qubit n on local qubit layout[n]) and seed of one operand: the predicted visibility
    V = D_c + D_r of the real and complex kinds."""
    name, layout, seed, calibration_dir = item
    block = block_of(operand_named(name))
    calibration = iqm_sim.Calibration.from_directory(Path(calibration_dir))
    compiled = structural_compile(block, False, layout, seed)
    diffs = {}
    for kind, label in (("real", "1"), ("cplx", "i")):
        zero = {
            plus: selector_zero(exact_law(bind(compiled, label, plus), calibration), block.d) for plus in (True, False)
        }
        diffs[kind] = zero[True] - zero[False]
    return {
        "layout": list(layout),
        "seed": seed,
        "cz": cz_of(compiled),
        "visibility": round(diffs["cplx"] + diffs["real"], 6),
    }


def build_operand(operand: Operand, calibration_dir: Path) -> dict[str, Any]:
    block = block_of(operand)
    nq = block.d + 1
    layouts = list(itertools.permutations(range(len(PATCH)), nq))
    first = ordered_map(
        layout_trial,
        [(operand.name, layout, TRANSPILER_SEEDS[0], str(calibration_dir)) for layout in layouts],
        min_items=1,
    )
    best = max(first, key=lambda row: row["visibility"])  # the first layout of the largest visibility
    layout = tuple(best["layout"])
    seeds = ordered_map(
        layout_trial, [(operand.name, layout, seed, str(calibration_dir)) for seed in TRANSPILER_SEEDS[1:]], min_items=1
    )
    chosen = max([best, *seeds], key=lambda row: row["visibility"])
    compiled = structural_compile(block, False, layout, chosen["seed"])
    templates = {"real": compiled, "cplx": compiled}
    if "plain" in operand.kinds:
        templates["plain"] = structural_compile(block, True, layout, chosen["seed"])
    bound: dict[tuple[str, bool], QuantumCircuit] = {}
    circuits: dict[tuple[str, bool], dict[str, Any]] = {}
    for kind in operand.kinds:
        for plus in (True, False):
            bound[(kind, plus)] = bind(templates[kind], "1" if kind == "real" else "i", plus)
            circuits[(kind, plus)] = to_iqm(bound[(kind, plus)], f"{operand.name}-{kind}")
    reference = amplitudes(bound[("real", True)])
    for key in (("real", False), ("cplx", True), ("cplx", False)):
        if amplitudes(bound[key]) != reference:
            raise ValueError(f"{operand.name}: kind {key} has PRX amplitudes or CZ gates unlike the real kind")
    return {
        "operand": operand,
        "block": block,
        "layout_trials": first,
        "seed_trials": seeds,
        "chosen": chosen,
        "bound": bound,
        "circuits": circuits,
        "cz": {kind: cz_of(templates[kind]) for kind in operand.kinds},
    }


def order_plan() -> list[tuple[str, str, str, int]]:
    """(operand, kind, orientation, copy) per position: a quad +, -, -, + per kind, the kinds then reversed."""
    seen: dict[tuple[str, str, str], int] = {}
    plan = []
    for name, kind in (*KIND_ORDER, *reversed(KIND_ORDER)):
        for orientation in ORIENTATIONS:
            key = (name, kind, orientation)
            plan.append((name, kind, orientation, seen.get(key, 0)))
            seen[key] = seen.get(key, 0) + 1
    return plan


def circuit_name(name: str, kind: str, orientation: str, copy: int) -> str:
    return f"{name}-{kind}-{orientation}-{copy:02d}"


def size_job(circuits: list[dict[str, Any]]) -> dict[str, Any]:
    """The largest shot count in steps of 500 whose billing v4 ceiling stays within CEILING_CREDITS and whose cancel
    threshold at that ceiling covers an overrun of 2.2 times the longest expected runtime (the overrun of the sibling
    Emerald run); the job carries CEILING_CREDITS as its ceiling."""
    inputs = sizing.load_inputs()
    seconds = [schedule_nanoseconds(c) * 1e-9 for c in circuits]
    mid = [0 for _ in circuits]
    price = float(inputs["price_garnet"])
    threshold = float(ceiling_seconds(CEILING_CREDITS, price) - CANCEL_MARGIN)
    best: dict[str, Any] | None = None
    for shots in range(500, MAX_EXECUTIONS // len(circuits) + 1, 500):
        priced = sizing.price(inputs, seconds, mid, shots)
        chosen = sizing.adopted(inputs, priced)
        if chosen["max_credits"] > CEILING_CREDITS:
            break
        if max(OVERRUNS) * chosen["expected_runtime_seconds"] <= threshold:
            best = {"shots": shots, "priced": priced, "adopted": chosen}
    if best is None:
        raise ValueError("no shot count fits the ceiling and the 2.2 times overrun")
    best["inputs_sha256"] = hashlib.sha256(sizing.INPUTS.read_bytes()).hexdigest()
    runtime = best["adopted"]["expected_runtime_seconds"]
    best["ceiling"] = {
        "max_credits": CEILING_CREDITS,
        "billed_seconds": float(ceiling_seconds(CEILING_CREDITS, price)),
        "cancel_threshold_seconds": threshold,
        "overrun_margins": {
            f"{f:g}x": {
                "runtime_seconds": f * runtime,
                "margin_seconds": threshold - f * runtime,
                "covered": bool(threshold >= f * runtime),
            }
            for f in OVERRUNS
        },
    }
    return best


def counts_from_zero(zero: dict[str, dict[str, dict[str, float]]], kept: int) -> dict[str, dict[str, decision.Counts]]:
    """Kept-shot counts at the predicted selector-zero frequencies: operand -> kind -> (k+, n+, k-, n-)."""
    return {
        name: {k: (round(z["plus"] * kept), kept, round(z["minus"] * kept), kept) for k, z in kinds.items()}
        for name, kinds in zero.items()
    }


def audit_item(
    item: tuple[str, tuple[str, str, bool], QuantumCircuit, dict[str, float | str], str],
) -> tuple[str, str, bool, float]:
    label, (name, kind, plus), bound, error, calibration_dir = item
    calibration = iqm_sim.Calibration.from_directory(Path(calibration_dir))
    law = exact_law(
        bound,
        calibration,
        schedule=str(error.get("schedule", "asap")),
        prx_scale=float(error.get("prx_scale", 0.0)),
        zz=float(error.get("zz", 0.0)),
    )
    block = block_of(operand_named(name))
    return label, f"{name}:{kind}", plus, selector_zero(law, block.d)


def summarize(result: dict[str, Any]) -> dict[str, Any]:
    """The verdict-level facts of one analysis of predicted counts."""
    return {
        "verdict": result["verdict"],
        "null_ratio": round(result["null_ratio"], 6),
        "n_c_subtracted": {n: round(r["n_c"], 4) for n, r in result["subtracted"].items()},
        "n_c_uncorrected": {n: round(result["estimates"][n]["n_c"], 4) for n in decision.DISCRIMINATING},
        "visibility": {n: round(e["visibility"], 4) for n, e in result["estimates"].items()},
        "mutation_reading": {n: round(m["reading"], 4) for n, m in result["mutations"].items() if m is not None},
    }


def coherent_audit(built: dict[str, dict[str, Any]], calibration_dir: Path, kept: int) -> dict[str, Any]:
    """The verdict of the preregistered rule under coherent errors the depolarizing model omits, each inserted after
    the scheduling (as scripts/iqm_probe_audit.py does): PRX amplitude errors, a ZZ rotation after every CZ, and the
    ALAP schedule. Every kind and orientation runs through the exact density matrix at the error, and the
    predicted counts pass through decision.analyze."""
    errors: dict[str, dict[str, float | str]] = {"none": {}}
    errors.update({f"prx{e:+.2f}": {"prx_scale": e} for e in PRX_ERRORS})
    errors.update({f"zz{e:+.2f}": {"zz": e} for e in ZZ_ERRORS})
    errors["alap"] = {"schedule": "alap"}
    tasks = [
        (label, (name, kind, plus), info["bound"][(kind, plus)], error, str(calibration_dir))
        for label, error in errors.items()
        for name, info in built.items()
        for kind in info["operand"].kinds
        for plus in (True, False)
    ]
    rows = ordered_map(audit_item, tasks, min_items=1)
    zero: dict[str, dict[str, dict[str, dict[str, float]]]] = {label: {} for label in errors}
    for label, key, plus, value in rows:
        name, kind = key.split(":")
        zero[label].setdefault(name, {}).setdefault(kind, {})["plus" if plus else "minus"] = value
    out = {}
    for label, error in errors.items():
        out[label] = {**error, **summarize(decision.analyze(counts_from_zero(zero[label], kept)))}
    complex_prx = [e for e in PRX_ERRORS if out[f"prx{e:+.2f}"]["verdict"] == "complex strata"]
    bound = max(
        (m for m in (0.01, 0.02, 0.03, 0.04, 0.05) if all(abs(e) > m or e in complex_prx for e in PRX_ERRORS)),
        default=0.0,
    )
    return {"errors": out, "prx_amplitude_complex_strata_within": bound, "kept_shots_per_orientation": kept}


def build_from(calibration_dir: Path) -> tuple[dict[str, str], dict[str, Any]]:
    calibration = iqm_sim.Calibration.from_directory(calibration_dir)
    check_patch(calibration)
    built = {op.name: build_operand(op, calibration_dir) for op in OPERANDS}
    plan = order_plan()
    files: dict[str, str] = {}
    circuits_in_order: list[dict[str, Any]] = []
    for name, kind, orientation, replicate in plan:
        circuit = dict(built[name]["circuits"][(kind, orientation == "plus")])
        circuit["name"] = circuit_name(name, kind, orientation, replicate)
        circuits_in_order.append(circuit)
        files[f"circuits/{circuit['name']}.json"] = dump(circuit)
    if len(plan) > MAX_CIRCUITS:
        raise ValueError(f"{len(plan)} circuits exceed the job limit {MAX_CIRCUITS}")
    sized = size_job(circuits_in_order)
    shots = sized["shots"]
    copies = len(plan) // (2 * len(KIND_ORDER) * 2)  # copies per orientation: 4 per kind
    kept = int(PLANNING_RETENTION * shots * copies * 2)  # two + circuits (or two -) per quad, two quads
    laws = {
        name: {
            kind: {o: exact_law(info["bound"][(kind, o == "plus")], calibration) for o in ("plus", "minus")}
            for kind in info["operand"].kinds
        }
        for name, info in built.items()
    }
    zero = {
        name: {
            kind: {o: selector_zero(law, built[name]["block"].d) for o, law in by.items()} for kind, by in kinds.items()
        }
        for name, kinds in laws.items()
    }
    analysis = decision.analyze(counts_from_zero(zero, kept))
    z = decision.z_values(analysis)
    operands: dict[str, Any] = {}
    for name, info in built.items():
        block = info["block"]
        kinds: dict[str, Any] = {}
        for kind in info["operand"].kinds:
            z0 = zero[name][kind]
            var = decision.PHI * sum(p * (1 - p) / kept for p in z0.values())
            kinds[kind] = {
                "ideal_difference": ideal_difference(block, kind),
                "predicted_zero": {o: round(v, 9) for o, v in z0.items()},
                "predicted_difference": round(z0["plus"] - z0["minus"], 9),
                "planned_se": round(math.sqrt(var), 9),
                "cz": info["cz"][kind],
                "law": {o: [round(float(x), 9) for x in laws[name][kind][o]] for o in ("plus", "minus")},
            }
        est = analysis["estimates"][name]
        sub = analysis["subtracted"].get(name)
        operands[name] = {
            "pair": list(info["operand"].pair),
            "stratum_real_complex": info["operand"].stratum,
            "block": {"basis": list(block.basis), "coset": block.coset, "data_qubits": block.d},
            "layout": info["chosen"]["layout"],
            "chosen_seed": info["chosen"]["seed"],
            "layout_trials": info["layout_trials"],
            "seed_trials": info["seed_trials"],
            "physical_qubits": sorted(
                {q for op in info["circuits"][("cplx", True)]["instructions"] for q in op["locus"]}
            ),
            "kinds": kinds,
            "predicted": {
                "visibility": round(est["visibility"], 9),
                "double_difference": round(est["dd"], 9),
                "ratio": round(est["ratio"], 9),
                "nullity_complex": round(est["n_c"], 6),
                "se_nullity_complex": round(est["se_n_c"], 6),
                "nullity_subtracted": None if sub is None else round(sub["n_c"], 6),
                "se_nullity_subtracted": None if sub is None else round(sub["se"], 6),
                "visibility_over_se": round(est["visibility"] / est["se_visibility"], 3),
            },
        }
    audit = coherent_audit(built, calibration_dir, kept)
    prediction = {
        "calibration_set": calibration.set_id,
        "model": (
            "exact density matrix of the touched qubits of each compiled circuit: depolarizing PRX and CZ, ASAP idle "
            "T1/T2, herald-conditioned readout; no coherent error, leakage or crosstalk"
        ),
        "patch": list(PATCH),
        "order": [circuit_name(*p) for p in plan],
        "shots": shots,
        "copies_per_orientation": copies * 2,
        "planning": {
            "kept_fraction_floor": PLANNING_RETENTION,
            "kept_shots_per_orientation": kept,
            "phi": decision.PHI,
            "z_resolve": decision.Z_RESOLVE,
        },
        "operands": operands,
        "decision": {
            "discriminating": decision.DISCRIMINATING,
            "null_operand": decision.NULL_OPERAND,
            "mutation_operands": list(decision.MUTATION_OPERANDS),
            "midpoint": decision.MIDPOINT,
            "null_ratio_predicted": round(analysis["null_ratio"], 9),
            "z_predicted": [round(v, 3) for v in z],
            "power_complex_truth": round(decision.power(z), 6),
        },
        "coherent_audit": audit,
        "cost": {
            "inputs_sha256": sized["inputs_sha256"],
            "billing_v4": {k: {kk: round(vv, 6) for kk, vv in row.items()} for k, row in sized["priced"].items()},
            "adopted": {
                k: (round(v, 6) if isinstance(v, float) else v)
                for k, v in sized["adopted"].items()
                if k != "overrun_margins"
            },
            "job_ceiling": {
                k: (round(v, 6) if isinstance(v, float) else v)
                for k, v in sized["ceiling"].items()
                if k != "overrun_margins"
            },
            "overrun_margins": sized["ceiling"]["overrun_margins"],
        },
    }
    files["prediction.json"] = dump(prediction)
    job = {
        "job": "kernel",
        "circuits": [
            {"file": f"circuits/{c['name']}.json", "sha256": sha256(files[f"circuits/{c['name']}.json"].encode())}
            for c in circuits_in_order
        ],
        "shots": shots,
        "options": {**OPTIONS, "calibration_set_id": {"garnet": calibration.set_id}},
        "expected_seconds": round(sized["adopted"]["expected_execution_seconds"], 3),
        "max_credits": {qc: (CEILING_CREDITS if PRICED[qc] else 0.0) for qc in QCS},
    }
    files["cases.json"] = dump(
        {
            "schema": CASE_SCHEMA,
            "case": CASE,
            "prediction_sha256": sha256(files["prediction.json"].encode()),
            "question": QUESTION,
            "qcs": QCS,
            "jobs": [job],
        }
    )
    return files, prediction


QUESTION = (
    "On Garnet, does the selector-zero difference of the coset-block kernel map of A_5 read the complex nullity of "
    "e_i + i e_j (16, 12, 8 and 4 at the strata 0/16, 4/12, 8/8 and 12/4 of the pairs e_1 + e_3, e_1 + e_26, "
    "e_1 + e_10 and e_1 + e_18) rather than the real one (0, 4, 8, 12), and does the plain-phase mutation read the "
    "opposite sign?"
)


def write(directory: Path, source: Path | None, live: bool) -> None:
    if live == (source is not None):
        raise ValueError("build takes exactly one of --calibration and --live")
    calibration_dir = directory / "calibration"
    calibration_dir.mkdir(parents=True, exist_ok=True)
    if live:
        from iqm_cancellation_probe import fetch_calibration

        fetch_calibration(calibration_dir)
    elif source is not None:
        for name in CALIBRATION_FILES:
            shutil.copyfile(source / name, calibration_dir / name)
    files, prediction = build_from(calibration_dir)
    for stale in (directory / "circuits").glob("*.json"):
        if stale.relative_to(directory).as_posix() not in files:
            stale.unlink()
    for rel, text in files.items():
        path = directory / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    print(
        json.dumps(
            {
                "cases_sha256": sha256(files["cases.json"].encode()),
                "decision": prediction["decision"],
                "cost": prediction["cost"]["adopted"],
            },
            indent=1,
        )
    )


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build")
    build.add_argument("directory", type=Path)
    group = build.add_mutually_exclusive_group()
    group.add_argument("--calibration", type=Path, default=None)
    group.add_argument("--live", action="store_true")
    sub.add_parser("check").add_argument("directory", type=Path)
    args = parser.parse_args()
    if args.command == "check":
        check(args.directory)
        return 0
    source = None if args.live else (args.calibration or RETAINED_CALIBRATION)
    write(args.directory, source, args.live)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
