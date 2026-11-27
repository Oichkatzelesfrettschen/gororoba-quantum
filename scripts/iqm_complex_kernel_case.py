"""IQM Garnet case of the complex kernel map of A_5: the S phases that turn the real nullity into the complex one.

The pathion kernel map reads the nullity N of L_(e_i + t e_j) over C from the selector bit of a 6-qubit circuit
(docs/evidence/a5-complex-kernel-map). This case reads the same strata on coset blocks of 2 to 4 qubits
(gororoba_quantum/pathion_complex_block.py): the selector-zero difference of the two orientations is N / 16 on every
coset of a subspace whose dimension d is 1 (N = 0 or 16), 3 (N = 4 or 12) or 2 (N = 8), so one block per operand
reads N. Each operand runs the real kind (t = 1), the complex kind (t = i) and, at two operands, the plain-phase
mutation, all in the orientations + and - in the order +, -, -, + and mirrored about the center of the job. The
real and complex kinds share one compiled gate skeleton; only the rotation angles of two phase gates differ.

Usage: "$PYTHON" scripts/iqm_complex_kernel_case.py build DIR [--calibration SRC | --live]
       "$PYTHON" scripts/iqm_complex_kernel_case.py check DIR
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import CouplingMap
from qiskit_aer import AerSimulator

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import iqm_sim  # noqa: E402
from iqm_jobs import CASE_SCHEMA, dump  # noqa: E402
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
CEILING_CREDITS = 11.0
MAX_CIRCUITS = 100
MAX_EXECUTIONS = 2_000_000
# Transpiler seeds of the layout search: ANU QRNG draw docs/evidence/anu_qrng/draw-2026-11-27T222523Z.json,
# indices 10 to 17 (record docs/evidence/qrng_seeds/allocations.json).
TRANSPILER_SEEDS = (37071, 270, 57975, 32200, 15385, 32776, 46268, 18502)
GATE_DURATIONS = {"prx": 16, "cz": 40, "measure": 480}
# Planning floor of the herald-kept fraction of the shots (the analysis reads the kept counts of the run).
PLANNING_RETENTION = 0.5
ORIENTATIONS = ("plus", "minus", "minus", "plus")


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


def block_of(operand: Operand) -> pcb.Block:
    """The block of the operand: the coset of its subspace on which the plain mutation reads lowest (the first coset
    where the operand has no plain kind)."""
    i, j = operand.pair
    basis = pcx.normalized_basis((i, j, 1), operand.basis)
    cosets = pcb.cosets(basis)
    if "plain" not in operand.kinds:
        return pcb.Block(operand.name, (i, j, 1), basis, cosets[0])
    best = min(
        cosets, key=lambda k0: pcx.selector_marginal(pcb.Block(operand.name, (i, j, 1), basis, k0), 1j, plain=True)
    )
    return pcb.Block(operand.name, (i, j, 1), basis, best)


def ideal_difference(block: pcb.Block, kind: str) -> float:
    """The selector-zero difference D of the kind on the block (exact)."""
    if kind == "plain":
        return pcx.selector_marginal(block, 1j, plain=True)
    return pcx.selector_marginal(block, 1 if kind == "real" else 1j)


def to_iqm(bound: QuantumCircuit, name: str, qubits: list[str]) -> dict[str, Any]:
    """The native circuit: prx, cz and one joint measure under the key m in classical-bit order."""
    instructions: list[dict[str, Any]] = []
    measured: dict[int, str] = {}
    for item in bound.data:
        op, locus = item.operation, [qubits[bound.find_bit(q).index] for q in item.qubits]
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


def modeled(calibration: iqm_sim.Calibration) -> iqm_sim.Calibration:
    """The calibration with the unheralded readout copied into any missing herald-conditioned field, so that the noise
    model builds for the whole register; usable_coupling keeps those qubits out of every layout."""
    clone = copy.copy(calibration)
    clone.values = dict(calibration.values)
    for q in calibration.qubits:
        for kind in ("error_0_to_1", "error_1_to_0"):
            field = iqm_sim.READOUT_FIELD.format(q=q, kind=kind)
            clone.values.setdefault(field + iqm_sim.HERALD_SUFFIX, calibration.values[field])
    return clone


def exact_law(bound: QuantumCircuit, calibration: iqm_sim.Calibration) -> np.ndarray:
    """The outcome law over the measured bits (index = sum of bit c times 2^c) of the compiled circuit under the
    calibration: depolarizing PRX and CZ, ASAP idle T1 and T2 relaxation, herald-conditioned readout. Exact density
    matrix of the touched qubits; no sampling."""
    target, _ = target_of(calibration)
    scheduled = transpile(bound, target=target, optimization_level=0, scheduling_method="alap")
    noisy = relaxed(calibration, scheduled)
    measures = sorted(
        (noisy.find_bit(i.clbits[0]).index, noisy.find_bit(i.qubits[0]).index)
        for i in noisy.data
        if i.operation.name == "measure"
    )
    body = QuantumCircuit(*noisy.qregs)
    for item in noisy.data:
        if item.operation.name != "measure":
            body.append(item.operation, item.qubits, item.clbits)
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
    half = 1 << d
    return float(law[:half].sum())


def usable_coupling(calibration: iqm_sim.Calibration) -> CouplingMap:
    """Couplers of the calibration whose two qubits carry herald-conditioned readout, relaxation times and a PRX
    fidelity and whose CZ carries an interleaved fidelity; a qubit or coupler outside the set stays out of every
    layout."""
    ok = {
        q
        for q in calibration.qubits
        if all(
            iqm_sim.READOUT_FIELD.format(q=q, kind=kind) + iqm_sim.HERALD_SUFFIX in calibration.values
            for kind in ("error_0_to_1", "error_1_to_0")
        )
        and all(f"characterization.model.{q}.{kind}" in calibration.values for kind in ("t1_time", "t2_time"))
        and (q in calibration.prx or iqm_sim.PRX_FIELD.format(q=q) in calibration.values)
    }
    index = {q: n for n, q in enumerate(calibration.qubits)}
    edges = [
        (index[a], index[b])
        for pair in calibration.cz
        for a, b in [sorted(pair, key=calibration.qubits.index)]
        if a in ok and b in ok
    ]
    return CouplingMap([e for a, b in edges for e in ((a, b), (b, a))])


def compile_template(
    block: pcb.Block, plain: bool, seed: int, calibration_dir: str, layout: list[int] | None
) -> QuantumCircuit:
    calibration = iqm_sim.Calibration.from_directory(Path(calibration_dir))
    coupling = usable_coupling(calibration)
    return transpile(
        pcx.block_template(block, plain=plain),
        basis_gates=["r", "cz"],
        coupling_map=coupling,
        optimization_level=3,
        seed_transpiler=seed,
        initial_layout=layout,
    )


def bind(compiled: QuantumCircuit, label: str, plus: bool) -> QuantumCircuit:
    return compiled.assign_parameters({pcx.ORIENTATION: float(np.pi) if plus else 0.0, pcx.PHASE: pcx.ANGLES[label]})


def seed_trial(item: tuple[str, int, str]) -> dict[str, Any]:
    """One transpiler seed on one operand: the real and complex kinds' predicted visibility V = D_c + D_r."""
    name, seed, calibration_dir = item
    operand = next(op for op in OPERANDS if op.name == name)
    block = block_of(operand)
    calibration = iqm_sim.Calibration.from_directory(Path(calibration_dir))
    compiled = compile_template(block, False, seed, calibration_dir, None)
    d = block.d
    diffs = {}
    for kind, label in (("real", "1"), ("cplx", "i")):
        zero = {plus: selector_zero(exact_law(bind(compiled, label, plus), calibration), d) for plus in (True, False)}
        diffs[kind] = zero[True] - zero[False]
    return {
        "seed": seed,
        "cz": int(compiled.count_ops().get("cz", 0)),
        "visibility": round(diffs["cplx"] + diffs["real"], 6),
    }


def kind_label(kind: str) -> str:
    return "1" if kind == "real" else "i"


def build_operand(operand: Operand, calibration_dir: Path) -> dict[str, Any]:
    calibration = iqm_sim.Calibration.from_directory(calibration_dir)
    block = block_of(operand)
    trials = ordered_map(
        seed_trial, [(operand.name, seed, str(calibration_dir)) for seed in TRANSPILER_SEEDS], min_items=1
    )
    chosen = max(trials, key=lambda row: row["visibility"])  # the first seed of the largest visibility
    compiled = compile_template(block, False, chosen["seed"], str(calibration_dir), None)
    layout = compiled.layout.initial_index_layout(filter_ancillas=True)
    templates = {"real": compiled, "cplx": compiled}
    if "plain" in operand.kinds:
        templates["plain"] = compile_template(block, True, chosen["seed"], str(calibration_dir), layout)
    circuits: dict[tuple[str, bool], dict[str, Any]] = {}
    laws: dict[tuple[str, bool], np.ndarray] = {}
    for kind in operand.kinds:
        for plus in (True, False):
            bound = bind(templates[kind], "1" if kind == "real" else "i", plus)
            circuits[(kind, plus)] = to_iqm(bound, f"{operand.name}-{kind}", calibration.qubits)
            laws[(kind, plus)] = exact_law(bound, calibration)
    return {
        "operand": operand,
        "block": block,
        "trials": trials,
        "chosen": chosen,
        "circuits": circuits,
        "laws": laws,
        "cz": {kind: int(templates[kind].count_ops().get("cz", 0)) for kind in operand.kinds},
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
    """The largest shot count in steps of 500 whose billing v4 ceiling stays within CEILING_CREDITS; the overrun margins
    of the adopted sizing (1.5 and 2.2 times the expected runtime) are recorded, not enforced."""
    inputs = sizing.load_inputs()
    seconds = [schedule_nanoseconds(c) * 1e-9 for c in circuits]
    mid = [0 for _ in circuits]
    best: dict[str, Any] | None = None
    for shots in range(500, MAX_EXECUTIONS // len(circuits) + 1, 500):
        priced = sizing.price(inputs, seconds, mid, shots)
        chosen = sizing.adopted(inputs, priced)
        if chosen["max_credits"] > CEILING_CREDITS:
            break
        best = {"shots": shots, "priced": priced, "adopted": chosen}
    if best is None:
        raise ValueError("no shot count fits the ceiling")
    best["inputs_sha256"] = hashlib.sha256(sizing.INPUTS.read_bytes()).hexdigest()
    return best


def build_from(calibration_dir: Path) -> tuple[dict[str, str], dict[str, Any]]:
    calibration = iqm_sim.Calibration.from_directory(calibration_dir)
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
    operands: dict[str, Any] = {}
    for name, info in built.items():
        block = info["block"]
        d = block.d
        kinds: dict[str, Any] = {}
        for kind in info["operand"].kinds:
            zero = {o: selector_zero(info["laws"][(kind, o == "plus")], d) for o in ("plus", "minus")}
            delta = zero["plus"] - zero["minus"]
            var = decision.PHI * sum(p * (1 - p) / kept for p in zero.values())
            kinds[kind] = {
                "ideal_difference": ideal_difference(block, kind),
                "predicted_zero": {o: round(z, 9) for o, z in zero.items()},
                "predicted_difference": round(delta, 9),
                "planned_se": round(math.sqrt(var), 9),
                "cz": info["cz"][kind],
                "law": {o: [round(float(x), 9) for x in info["laws"][(kind, o == "plus")]] for o in ("plus", "minus")},
            }
        real, cplx = kinds["real"], kinds["cplx"]
        v_pred = real["predicted_difference"] + cplx["predicted_difference"]
        se_v = math.sqrt(real["planned_se"] ** 2 + cplx["planned_se"] ** 2)
        dd_pred = cplx["predicted_difference"] - real["predicted_difference"]
        n_pred = 16 * cplx["predicted_difference"] / v_pred
        se_n = (
            16
            / v_pred**2
            * math.sqrt(
                real["predicted_difference"] ** 2 * cplx["planned_se"] ** 2
                + cplx["predicted_difference"] ** 2 * real["planned_se"] ** 2
            )
        )
        operands[name] = {
            "pair": list(info["operand"].pair),
            "stratum_real_complex": info["operand"].stratum,
            "block": {"basis": list(block.basis), "coset": block.coset, "data_qubits": d},
            "transpiler_trials": info["trials"],
            "chosen_seed": info["chosen"]["seed"],
            "physical_qubits": sorted(
                {q for op in info["circuits"][("cplx", True)]["instructions"] for q in op["locus"]}
            ),
            "kinds": kinds,
            "predicted": {
                "visibility": round(v_pred, 9),
                "double_difference": round(dd_pred, 9),
                "nullity_complex": round(n_pred, 6),
                "se_nullity_complex": round(se_n, 6),
                "z_nullity_from_midpoint": round(abs(n_pred - decision.MIDPOINT) / se_n, 3),
                "visibility_for_z_resolve": (
                    round(v_pred * decision.Z_RESOLVE / (abs(n_pred - decision.MIDPOINT) / se_n), 6)
                    if name in decision.DISCRIMINATING
                    else None
                ),
                "visibility_over_se": round(v_pred / se_v, 3),
            },
        }
    z = [operands[n]["predicted"]["z_nullity_from_midpoint"] for n in decision.DISCRIMINATING]
    prediction = {
        "calibration_set": calibration.set_id,
        "model": (
            "exact density matrix of the touched qubits of each compiled circuit: depolarizing PRX and CZ, ASAP idle "
            "T1/T2, herald-conditioned readout; no coherent error, leakage or crosstalk"
        ),
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
            "null_fraction": decision.NULL_FRACTION,
            "mutation_operands": list(decision.MUTATION_OPERANDS),
            "midpoint": decision.MIDPOINT,
            "power_complex_truth": round(decision.power(z), 6),
        },
        "cost": {
            "inputs_sha256": sized["inputs_sha256"],
            "billing_v4": {k: {kk: round(vv, 6) for kk, vv in row.items()} for k, row in sized["priced"].items()},
            "adopted": {
                k: (round(v, 6) if isinstance(v, float) else v)
                for k, v in sized["adopted"].items()
                if k != "overrun_margins"
            },
            "overrun_margins": sized["adopted"]["overrun_margins"],
        },
    }
    files["prediction.json"] = dump(prediction)
    adopted = sized["adopted"]
    job = {
        "job": "kernel",
        "circuits": [
            {"file": f"circuits/{c['name']}.json", "sha256": sha256(files[f"circuits/{c['name']}.json"].encode())}
            for c in circuits_in_order
        ],
        "shots": shots,
        "options": {**OPTIONS, "calibration_set_id": {"garnet": calibration.set_id}},
        "expected_seconds": round(adopted["expected_execution_seconds"], 3),
        "max_credits": {qc: (adopted["max_credits"] if PRICED[qc] else 0.0) for qc in QCS},
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
