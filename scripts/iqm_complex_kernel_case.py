"""IQM Garnet case of the complex kernel map of A_5: the S phases that turn the real nullity into the complex one.

The pathion kernel map reads the nullity N of L_(e_i + t e_j) over C from the selector bit of a 6-qubit circuit
(docs/evidence/a5-complex-kernel-map). This case reads the same strata on coset blocks of 2 to 4 qubits
(gororoba_quantum/pathion_complex_block.py): the selector-zero difference of the two orientations is N / 16 on every
coset of a subspace whose dimension d is 1 (N = 0 or 16), 3 (N = 4 or 12) or 2 (N = 8), so one block per operand
reads N. Each operand runs the real kind (t = 1) and the complex kind (t = i); s412 also runs the plain-phase
mutation on a coset whose pair sign is not constant, and s808 a sentinel (its real kind again, at the center of the
job). Every kind runs in the orientations + and - in the order +, -, -, + and mirrored about the center of the job.

The four operands sit on one patch of four qubits, the star that a written rule (rank_stars) selects from the
calibration set, so the null operand's offset applies to the others. The phase gates of a block are Z rotations behind
barriers: after the compile every Z rotation moves to the end of the circuit as a shift of the phase of each later
PRX, so the real and complex circuits (and both orientations) carry
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
from qiskit.circuit.library import CPhaseGate, RGate, RZGate, RZZGate
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
SHOTS = 6000
# The cancel threshold of the ceiling must clear the 2.2 times overrun of the expected runtime by this many seconds, the
# latency of the station-control stop that follows a cancel.
OVERRUN_MARGIN_MIN_SECONDS = 1.5
# The plain kind is kept only on a coset where its outcome law differs from the complex kind with the orientations
# swapped by at least this much (the swap is what a constant pair sign leaves).
PLAIN_GAP_MIN = 0.05
# Transpiler seeds: ANU QRNG draw docs/evidence/anu_qrng/draw-2026-11-27T222523Z.json, indices 10 to 17 (record
# docs/evidence/qrng_seeds/allocations.json). The first seed compiles the coset and layout search; the others are
# trials at the chosen layout.
TRANSPILER_SEEDS = (37071, 270, 57975, 32200, 15385, 32776, 46268, 18502)
GATE_DURATIONS = {"prx": 16, "cz": 40, "measure": 480}
# Planning floor of the herald-kept fraction of the shots (the analysis reads the kept counts of the run).
PLANNING_RETENTION = 0.5
ORIENTATIONS = ("plus", "minus", "minus", "plus")
# One star of four qubits holds every operand; local qubit n of a compile is patch[n], with the center at local index 2
# and the leaves (sorted by name) at 0, 1 and 3.
PATCH_EDGES = ((2, 0), (2, 1), (2, 3))
LINEARITY = ROOT / "results/iqm/idle_schedule_probe_analysis.json"
PRIOR_STAR = ("QB11", "QB5", "QB6", "QB7")  # the star of the first draft of the case, ranked for the record
# Coherent errors of the audit (each enters after the scheduling).
PRX_ERRORS = (-0.05, -0.04, -0.03, -0.02, -0.01, 0.01, 0.02, 0.03, 0.04, 0.05)
QUBIT_PRX_ERRORS = (-0.05, -0.03, 0.03, 0.05)
ZZ_ERRORS = (-0.05, 0.05)
CPHASE_ERRORS = (-0.10, -0.05, 0.05, 0.10)
ZRES_ERRORS = (-0.15, -0.05, 0.05, 0.15)
# The combined error scales a base of (PRX amplitude, CZ conditional phase, residual Z rotation after each CZ).
COMBINED_BASE = (-0.02, -0.05, -0.05)
COMBINED_SCALES = (0.25, 0.5, 1.0, 1.5)


@dataclass(frozen=True)
class Operand:
    """One pair of imaginary units, its coset-block subspace and the kinds it runs."""

    name: str
    pair: tuple[int, int]
    basis: tuple[int, ...]
    stratum: str  # real / complex nullity of e_i + e_j and e_i + i e_j
    kinds: tuple[str, ...]  # sent is the real kind again, at the center of the job


OPERANDS = (
    Operand("s016", (1, 3), (2,), "0/16", ("real", "cplx")),
    Operand("s412", (1, 26), (27, 4, 9), "4/12", ("real", "cplx", "plain")),
    Operand("s808", (1, 10), (11, 4), "8/8", ("real", "cplx", "sent")),
    Operand("s124", (1, 18), (19, 4, 8), "12/4", ("real", "cplx")),
)
# The first half of the job; the second half runs the kinds in reverse. The null pair sits at the outer end, the
# sentinel (the null operand's real kind again) at the center, and the weakest kind (s124 cplx) away from both.
KIND_ORDER = (
    ("s808", "real"),
    ("s808", "cplx"),
    ("s124", "real"),
    ("s124", "cplx"),
    ("s016", "real"),
    ("s016", "cplx"),
    ("s412", "real"),
    ("s412", "cplx"),
    ("s412", "plain"),
    ("s808", "sent"),
)


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


def plain_gap(block: pcb.Block) -> float:
    """The largest distance between the outcome law of the plain kind and that of the complex kind with the
    orientations swapped. A pair sign that is constant on the upper members turns the plain kind into that swap (the
    sign multiplies every upper amplitude by -1, which is the orientation phase pi), and the gap vanishes."""
    return max(
        float(np.max(np.abs(pcx.block_law(block, 1j, plus, plain=True) - pcx.block_law(block, 1j, not plus))))
        for plus in (True, False)
    )


def block_of(operand: Operand) -> pcb.Block:
    """The coset of the operand's subspace that carries its readings. Without a plain kind, the first coset. With
    one, among the cosets where the plain reading is negative (the mutation flips the sign) and the plain kind differs
    from the orientation-swapped complex kind by at least PLAIN_GAP_MIN, the coset of the largest gap, then the lowest
    coset index. The choice reads the exact laws alone, never a compile."""
    i, j = operand.pair
    basis = pcx.normalized_basis((i, j, 1), operand.basis)
    cosets = pcb.cosets(basis)
    if "plain" not in operand.kinds:
        return pcb.Block(operand.name, (i, j, 1), basis, cosets[0])
    rows = []
    for coset in cosets:
        block = pcb.Block(operand.name, (i, j, 1), basis, coset)
        gap = plain_gap(block)
        if pcx.selector_marginal(block, 1j, plain=True) < -1e-9 and gap >= PLAIN_GAP_MIN:
            rows.append((-gap, coset))
    if not rows:
        raise ValueError(f"{operand.name}: no coset carries a plain kind distinct from the swapped complex kind")
    return pcb.Block(operand.name, (i, j, 1), basis, min(rows)[1])


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


def check_patch(calibration: iqm_sim.Calibration, patch: tuple[str, ...]) -> None:
    """The patch qubits are usable and the patch edges are calibrated couplers."""
    missing = [q for q in patch if q not in usable_qubits(calibration)]
    edges = [frozenset((patch[a], patch[b])) for a, b in PATCH_EDGES]
    absent = [sorted(e) for e in edges if e not in calibration.cz]
    if missing or absent:
        raise ValueError(f"patch {patch}: qubits {missing} are unusable and couplers {absent} are uncalibrated")


def parallel_train_linearity() -> tuple[dict[str, bool], str]:
    """Per qubit, whether the retained Garnet parallel PRX train (results/iqm/idle_schedule_probe_analysis.json, set
    a18a947f of 2026-10-25) fits the linear over-rotation model, and the sha256 of that file."""
    data = LINEARITY.read_bytes()
    trains = json.loads(data)["parallel_trains"]
    return {q: bool(row["linear"]) for q, row in trains.items()}, hashlib.sha256(data).hexdigest()


def rank_stars(calibration: iqm_sim.Calibration, linearity: dict[str, bool]) -> list[dict[str, Any]]:
    """Every star of four usable qubits (a center and three neighbors on calibrated couplers), best first. The rule,
    written before any live read: fewest qubits whose retained parallel train is not linear, then fewest qubits the
    train did not measure, then the largest product of the three CZ fidelities, then the largest PRX RB fidelity of
    the weakest qubit, then the patch names. A patch lists the leaves in name order around the center at index 2."""
    usable = usable_qubits(calibration)
    rows = []
    for center in sorted(usable):
        leaves = sorted(q for q in usable if q != center and frozenset((center, q)) in calibration.cz)
        for trio in itertools.combinations(leaves, 3):
            patch = (trio[0], trio[1], center, trio[2])
            product = math.prod(calibration.cz[frozenset((center, q))] for q in trio)
            prx = min(calibration.prx.get(q, calibration.values.get(iqm_sim.PRX_FIELD.format(q=q), 0.0)) for q in patch)
            rows.append(
                {
                    "patch": list(patch),
                    "nonlinear_train_qubits": sum(1 for q in patch if linearity.get(q) is False),
                    "unmeasured_train_qubits": sum(1 for q in patch if q not in linearity),
                    "cz_product": round(product, 6),
                    "min_prx_rb_fidelity": round(prx, 6),
                }
            )
    rows.sort(
        key=lambda r: (
            r["nonlinear_train_qubits"],
            r["unmeasured_train_qubits"],
            -r["cz_product"],
            -r["min_prx_rb_fidelity"],
            r["patch"],
        )
    )
    return rows


def modeled(calibration: iqm_sim.Calibration) -> iqm_sim.Calibration:
    """The calibration with the unheralded readout copied into any missing herald-conditioned field, so that the noise
    model builds for the whole register. A qubit whose set holds no unheralded readout stays without a readout error
    (the noise model skips it); check_patch keeps the patch qubits usable."""
    clone = copy.copy(calibration)
    clone.values = dict(calibration.values)
    for q in calibration.qubits:
        fields = [iqm_sim.READOUT_FIELD.format(q=q, kind=kind) for kind in ("error_0_to_1", "error_1_to_0")]
        if all(field in calibration.values for field in fields):
            for field in fields:
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


def embed(circuit: QuantumCircuit, calibration: iqm_sim.Calibration, patch: tuple[str, ...]) -> QuantumCircuit:
    """The patch circuit on the calibration's register (local qubit n on patch[n])."""
    wide = QuantumCircuit(len(calibration.qubits), circuit.num_clbits)
    wide.compose(circuit, qubits=[calibration.qubits.index(patch[n]) for n in range(circuit.num_qubits)], inplace=True)
    return wide


def to_iqm(bound: QuantumCircuit, name: str, patch: tuple[str, ...]) -> dict[str, Any]:
    """The native circuit: prx, cz and one joint measure under the key m in classical-bit order, on the patch."""
    instructions: list[dict[str, Any]] = []
    measured: dict[int, str] = {}
    for item in bound.data:
        op, locus = item.operation, [patch[bound.find_bit(q).index] for q in item.qubits]
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
    patch: tuple[str, ...],
    *,
    schedule: str = "asap",
    errors: dict[str, Any] | None = None,
) -> np.ndarray:
    """The outcome law over the measured bits (index = sum of bit c times 2^c) of the circuit on the calibration's
    register: depolarizing PRX and CZ, idle T1 and T2 relaxation over the schedule (ASAP, as the idle-schedule case
    measured on Garnet), herald-conditioned readout; exact density matrix of the touched qubits, no sampling. A coherent
    error enters after the scheduling (errors): prx_scale, every PRX angle times 1 + e (a number for every qubit, or a
    qubit name to number map); zz, an RZZ rotation after every CZ; cphase, a conditional phase after every CZ; zres, a
    Z rotation on both qubits after every CZ."""
    errors = errors or {}
    prx_scale = errors.get("prx_scale", 0.0)
    zz, cphase, zres = (float(errors.get(key, 0.0)) for key in ("zz", "cphase", "zres"))
    target, _ = target_of(calibration)
    scheduled = transpile(
        embed(bound, calibration, patch), target=target, optimization_level=0, scheduling_method=schedule
    )
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
        qubits = [noisy.find_bit(q).index for q in item.qubits]
        if op.name == "r":
            scale = prx_scale.get(calibration.qubits[qubits[0]], 0.0) if isinstance(prx_scale, dict) else prx_scale
            if scale:
                theta, phi = (float(p) for p in op.params)
                body.append(RGate(theta * (1 + scale), phi), item.qubits)
                continue
        body.append(op, item.qubits, item.clbits)
        if op.name == "cz":
            if zz:
                body.append(RZZGate(zz), item.qubits)
            if cphase:
                body.append(CPhaseGate(cphase), item.qubits)
            if zres:
                for q in item.qubits:
                    body.append(RZGate(zres), [q])
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


def layout_trial(item: tuple[str, tuple[int, ...], int, str, tuple[str, ...]]) -> dict[str, Any]:
    """One layout (virtual qubit n on local qubit layout[n]) and seed of one operand: the predicted visibility
    V = D_c + D_r of the real and complex kinds."""
    name, layout, seed, calibration_dir, patch = item
    block = block_of(operand_named(name))
    calibration = iqm_sim.Calibration.from_directory(Path(calibration_dir))
    compiled = structural_compile(block, False, layout, seed)
    diffs = {}
    for kind, label in (("real", "1"), ("cplx", "i")):
        zero = {
            plus: selector_zero(exact_law(bind(compiled, label, plus), calibration, patch), block.d)
            for plus in (True, False)
        }
        diffs[kind] = zero[True] - zero[False]
    return {
        "layout": list(layout),
        "seed": seed,
        "cz": cz_of(compiled),
        "visibility": round(diffs["cplx"] + diffs["real"], 6),
    }


def build_operand(operand: Operand, calibration_dir: Path, patch: tuple[str, ...]) -> dict[str, Any]:
    block = block_of(operand)
    nq = block.d + 1
    layouts = list(itertools.permutations(range(len(patch)), nq))
    first = ordered_map(
        layout_trial,
        [(operand.name, layout, TRANSPILER_SEEDS[0], str(calibration_dir), patch) for layout in layouts],
        min_items=1,
    )
    best = max(first, key=lambda row: row["visibility"])  # the first layout of the largest visibility
    layout = tuple(best["layout"])
    seeds = ordered_map(
        layout_trial,
        [(operand.name, layout, seed, str(calibration_dir), patch) for seed in TRANSPILER_SEEDS[1:]],
        min_items=1,
    )
    chosen = max([best, *seeds], key=lambda row: row["visibility"])
    compiled = structural_compile(block, False, layout, chosen["seed"])
    templates = {"real": compiled, "cplx": compiled, "sent": compiled}
    if "plain" in operand.kinds:
        templates["plain"] = structural_compile(block, True, layout, chosen["seed"])
    bound: dict[tuple[str, bool], QuantumCircuit] = {}
    circuits: dict[tuple[str, bool], dict[str, Any]] = {}
    for kind in operand.kinds:
        for plus in (True, False):
            bound[(kind, plus)] = bind(templates[kind], "1" if kind in ("real", "sent") else "i", plus)
            circuits[(kind, plus)] = to_iqm(bound[(kind, plus)], f"{operand.name}-{kind}", patch)
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
        "plain_gap": plain_gap(block) if "plain" in operand.kinds else None,
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
    """The job at SHOTS shots: its billing v4 ceiling stays within CEILING_CREDITS, and the cancel threshold at that
    ceiling clears an overrun of 2.2 times the expected runtime (the overrun of the sibling Emerald run) by at least
    OVERRUN_MARGIN_MIN_SECONDS; the job carries CEILING_CREDITS as its ceiling."""
    inputs = sizing.load_inputs()
    seconds = [schedule_nanoseconds(c) * 1e-9 for c in circuits]
    mid = [0 for _ in circuits]
    price = float(inputs["price_garnet"])
    threshold = float(ceiling_seconds(CEILING_CREDITS, price) - CANCEL_MARGIN)
    if SHOTS * len(circuits) > MAX_EXECUTIONS:
        raise ValueError(f"{SHOTS} shots on {len(circuits)} circuits exceed {MAX_EXECUTIONS} executions")
    priced = sizing.price(inputs, seconds, mid, SHOTS)
    chosen = sizing.adopted(inputs, priced)
    if chosen["max_credits"] > CEILING_CREDITS:
        raise ValueError(f"{SHOTS} shots price the ceiling at {chosen['max_credits']} credits, over {CEILING_CREDITS}")
    runtime = chosen["expected_runtime_seconds"]
    margin = threshold - max(OVERRUNS) * runtime
    if margin < OVERRUN_MARGIN_MIN_SECONDS:
        raise ValueError(f"the 2.2 times overrun clears the cancel threshold by {margin:.3f} s at {SHOTS} shots")
    best: dict[str, Any] = {"shots": SHOTS, "priced": priced, "adopted": chosen}
    best["inputs_sha256"] = hashlib.sha256(sizing.INPUTS.read_bytes()).hexdigest()
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
    item: tuple[str, tuple[str, str, bool], QuantumCircuit, dict[str, Any], str, tuple[str, ...]],
) -> tuple[str, str, bool, float]:
    label, (name, kind, plus), bound, error, calibration_dir, patch = item
    calibration = iqm_sim.Calibration.from_directory(Path(calibration_dir))
    law = exact_law(bound, calibration, patch, schedule=str(error.get("schedule", "asap")), errors=error)
    block = block_of(operand_named(name))
    return label, f"{name}:{kind}", plus, selector_zero(law, block.d)


def summarize(result: dict[str, Any]) -> dict[str, Any]:
    """The verdict-level facts of one analysis of predicted counts."""

    def rounded(value: float | None, digits: int) -> float | None:
        return None if value is None else round(value, digits)

    return {
        "verdict": result["verdict"],
        "null_ratio": rounded(result["null_ratio"], 6),
        "n_c_subtracted": {n: rounded(r["n_c"], 4) for n, r in result["subtracted"].items()},
        "n_c_uncorrected": {n: rounded(result["estimates"][n]["n_c"], 4) for n in decision.DISCRIMINATING},
        "visibility": {n: round(e["visibility"], 4) for n, e in result["estimates"].items()},
        "mutation_reading": {n: round(m["reading"], 4) for n, m in result["mutations"].items() if m is not None},
    }


def audit_errors(patch: tuple[str, ...]) -> list[tuple[str, str, float, dict[str, Any]]]:
    """(label, family, magnitude, error) of every audited coherent error; the families are PRX amplitude on every
    qubit, PRX amplitude on one qubit, ZZ rotation after each CZ, CZ conditional phase, residual Z rotation after each
    CZ, the three combined (scaled COMBINED_BASE) and the ALAP schedule."""
    rows: list[tuple[str, str, float, dict[str, Any]]] = [("none", "none", 0.0, {})]
    rows += [(f"prx{e:+.2f}", "prx", abs(e), {"prx_scale": e}) for e in PRX_ERRORS]
    rows += [(f"prx{e:+.2f}@{q}", "qubit_prx", abs(e), {"prx_scale": {q: e}}) for q in patch for e in QUBIT_PRX_ERRORS]
    rows += [(f"zz{e:+.2f}", "zz", abs(e), {"zz": e}) for e in ZZ_ERRORS]
    rows += [(f"cphase{e:+.2f}", "cphase", abs(e), {"cphase": e}) for e in CPHASE_ERRORS]
    rows += [(f"zres{e:+.2f}", "zres", abs(e), {"zres": e}) for e in ZRES_ERRORS]
    prx, cphase, zres = COMBINED_BASE
    for s in COMBINED_SCALES:
        rows.append((f"combined-{s:g}x", "combined", s, {"prx_scale": s * prx, "cphase": s * cphase, "zres": s * zres}))
    rows.append(("combined+1x", "combined_opposite", 1.0, {"prx_scale": -prx, "cphase": -cphase, "zres": -zres}))
    rows.append(("alap", "alap", 0.0, {"schedule": "alap"}))
    return rows


def bound_of(rows: list[tuple[float, bool]]) -> float:
    """The largest magnitude m for which every error of magnitude at most m reads the complex strata."""
    best = 0.0
    for m in sorted({magnitude for magnitude, _ in rows}):
        if all(ok for magnitude, ok in rows if magnitude <= m):
            best = m
        else:
            break
    return best


def coherent_audit(
    built: dict[str, dict[str, Any]], calibration_dir: Path, kept: int, patch: tuple[str, ...]
) -> dict[str, Any]:
    """The verdict of the preregistered rule under coherent errors the depolarizing model omits, each inserted after
    the scheduling (as scripts/iqm_probe_audit.py does). Every kind and orientation runs through the exact density
    matrix at the error (the sentinel is the real kind again), and the predicted counts pass through
    decision.analyze. The bound of a family is the largest magnitude below which every row reads the complex strata;
    the combined family scales one (PRX amplitude, CZ conditional phase, residual Z rotation) triple."""
    specs = audit_errors(patch)
    errors = {label: error for label, _, _, error in specs}
    tasks = [
        (label, (name, kind, plus), info["bound"][(kind, plus)], error, str(calibration_dir), patch)
        for label, error in errors.items()
        for name, info in built.items()
        for kind in info["operand"].kinds
        if kind != "sent"
        for plus in (True, False)
    ]
    rows = ordered_map(audit_item, tasks, min_items=1)
    zero: dict[str, dict[str, dict[str, dict[str, float]]]] = {label: {} for label in errors}
    for label, key, plus, value in rows:
        name, kind = key.split(":")
        zero[label].setdefault(name, {}).setdefault(kind, {})["plus" if plus else "minus"] = value
    for label in errors:
        zero[label]["s808"]["sent"] = dict(zero[label]["s808"]["real"])
    out = {}
    for label, error in errors.items():
        out[label] = {**error, **summarize(decision.analyze(counts_from_zero(zero[label], kept)))}
    families: dict[str, list[tuple[float, bool]]] = {}
    for label, family, magnitude, _ in specs:
        if family not in ("none", "alap"):
            families.setdefault(family, []).append(
                (magnitude, out[label]["verdict"] == "complex strata within tolerance")
            )
    return {
        "errors": out,
        "complex_strata_within": {family: bound_of(rows) for family, rows in families.items()},
        "combined_base": {"prx_scale": COMBINED_BASE[0], "cphase": COMBINED_BASE[1], "zres": COMBINED_BASE[2]},
        "kept_shots_per_orientation": kept,
    }


def build_from(calibration_dir: Path) -> tuple[dict[str, str], dict[str, Any]]:
    calibration = iqm_sim.Calibration.from_directory(calibration_dir)
    linearity, linearity_sha256 = parallel_train_linearity()
    ranking = rank_stars(calibration, linearity)
    if not ranking:
        raise ValueError(f"calibration set {calibration.set_id} holds no usable star of four qubits")
    patch = tuple(ranking[0]["patch"])
    check_patch(calibration, patch)
    built = {op.name: build_operand(op, calibration_dir, patch) for op in OPERANDS}
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
            kind: {o: exact_law(info["bound"][(kind, o == "plus")], calibration, patch) for o in ("plus", "minus")}
            for kind in info["operand"].kinds
            if kind != "sent"
        }
        for name, info in built.items()
    }
    for name, info in built.items():
        if "sent" in info["operand"].kinds:
            laws[name]["sent"] = laws[name]["real"]  # the sentinel is the real circuit again
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
    audit = coherent_audit(built, calibration_dir, kept, patch)
    counts = counts_from_zero(zero, kept)
    rule_source = Path(decision.__file__).read_bytes()
    star_rows = {tuple(row["patch"]): rank for rank, row in enumerate(ranking, start=1)}
    prediction = {
        "calibration_set": calibration.set_id,
        "model": (
            "exact density matrix of the touched qubits of each compiled circuit: depolarizing PRX and CZ, ASAP idle "
            "T1/T2, herald-conditioned readout; no coherent error, leakage or crosstalk"
        ),
        "patch": list(patch),
        "star": {
            "rule": (
                "rank every star of four usable qubits (a center and three neighbors on calibrated couplers) by "
                "fewest qubits with a non-linear retained parallel PRX train, then fewest qubits the train did not "
                "measure, then the largest product of the three CZ fidelities, then the largest PRX RB fidelity of "
                "the weakest qubit, then the names; the first row is the patch"
            ),
            "linearity_source": "results/iqm/idle_schedule_probe_analysis.json",
            "linearity_sha256": linearity_sha256,
            "stars": len(ranking),
            "chosen_rank": 1,
            "prior_star": list(PRIOR_STAR),
            "prior_star_rank": star_rows.get(PRIOR_STAR),
            "ranking": ranking,
        },
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
            "ideal_complex": decision.IDEAL_COMPLEX,
            "null_operand": decision.NULL_OPERAND,
            "mutation_operands": list(decision.MUTATION_OPERANDS),
            "midpoint": decision.MIDPOINT,
            "rule": {
                "n_tolerance": decision.N_TOLERANCE,
                "v_s016_min": decision.V_S016_MIN,
                "r_null_max": decision.R_NULL_MAX,
                "drift_z_max": decision.DRIFT_Z_MAX,
                "z_resolve": decision.Z_RESOLVE,
                "source_sha256": hashlib.sha256(rule_source).hexdigest(),
            },
            "null_ratio_predicted": round(analysis["null_ratio"], 9),
            "drift_z_predicted": analysis["drift_z"],
            "verdict_predicted": analysis["verdict"],
            "z_predicted": [round(v, 3) for v in z],
            "power_complex_truth": round(decision.simulated_power(counts), 3),
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
