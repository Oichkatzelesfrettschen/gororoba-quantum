"""Members whose bound law needs no entangling gate must compile to zero CZ, or declare why they execute one.

live_run.select compiles each member's circuit object as it stands
(live_run._compile at OPT_LEVEL on the admission Target) and binds the
member's angles afterwards (live_run._bind). A member that shares a symbolic
template therefore executes every CZ the template lowers to, whatever its
bound angles: the ripple walk readout controls are logically the identity
before measurement and execute the 252-CZ walk scaffold
(docs/evidence/walk-control-scaffolding/README.md).

The contract enumerates every member live_run can plan: the default and
standalone groups (experiments.all_experiment_groups) and the family groups
diagnostic_experiments.record_groups rebuilds from each distinct
family_configuration among the retained records under results/live/. Members
are deduplicated by name and a digest of their circuit structure and binding.
For each member it binds the circuit, removes final measurements, and calls
the bound unitary local when, for every qubit q, its operator Schmidt rank
across q and the rest is 1 (singular-value ratio below TOLERANCE); a local
unitary maps every basis input to a product state, so its law needs no
two-qubit gate. Each local member's circuit object is then lowered with
transpile(basis_gates=BASIS, optimization_level=OPT_LEVEL,
seed_transpiler=SEED) and no coupling map, exactly as live_run compiles it
apart from routing; routing only inserts SWAPs around existing two-qubit
gates, so the unrouted CZ count is zero exactly when the routed count is.

A barrier or a delay states a cancellation the design asks the device to
perform: designs.design_a_associator and design_c_associator_spectrum
separate their multiplication blocks with barriers so the device composes W,
and a conditional-Ramsey Bell arm brackets its measured idle with CX. The
bound ISA's DAG is therefore cut at every barrier, delay and measurement on
the wires each one touches, and split into connected components; only the CZ
inside a component whose own bound unitary is local counts as scaffold. A
member with scaffold CZ fails unless SCAFFOLD_CONTROLS names it with the
measurement that requires the scaffold.

A member whose unitary entangles can still map its prepared input to a
product state, so its observed law needs no two-qubit gate either. Such a
member that executes CZ fails unless PRODUCT_OUTPUT_PROBES names it with
what its circuit tests.

A member with mid-circuit measurement, reset or control flow has no unitary;
its ideal measured law is the joint distribution of its classical bits,
which qpe_diagnostics.ideal_branch_probabilities enumerates exactly, one
statevector per measurement and reset branch, with if_else selecting its
block from the stored bit. The law is a point mass, a product of its
single-bit marginals, or correlated across bits. A point-mass or product law
carries no correlation between classical bits, the condition under which a
product output already requires a declaration. A correlated law that is
unchanged once every multi-qubit unitary is removed from the bound circuit,
control-flow blocks included, comes from measurement and classical
feed-forward alone. A member with either law that executes CZ anywhere in
its ISA fails unless DYNAMIC_LAW_PROBES names it with the measurement its CZ
serves; a correlation its multi-qubit gates produce passes. The audit
records the label, the point-mass outcome, the removal comparison and the
CZ count, never a float. The member digest includes each control-flow
operation's condition or target, case labels and block structure, so
members that differ only inside a branch stay distinct.
A member with more than MAX_BRANCH_OPS measurements and resets on one
branch, or more classical bits, or with control flow other than a
single-bit if_else, is listed as unchecked with that reason, as is a member
wider than MAX_WIDTH qubits.

Every declared pattern must match at least one member that executes CZ.
The per-member classification, static and dynamic, runs through
parallel.ordered_map, so GOROROBA_WORKERS caps it and the order is the
serial one.

``--write`` stores the census in
docs/evidence/walk-control-scaffolding/local_member_conformance.json;
``--check`` recomputes it, requires equality and enforces the declarations.
``--check-dynamic`` rebuilds the planned groups, recomputes only the
dynamic rows and unchecked reasons, compares them with the stored census
and enforces DYNAMIC_LAW_PROBES. ``--self-test`` classifies synthetic
dynamic circuits of every law and unchecked reason and requires members
that differ only inside an if_else block to differ in digest. ``--self-test-undeclared`` reruns the declaration check on
the stored census with folded_qpe_null's declaration removed, and with a
pattern that matches only a CZ-free member added, and requires each to fail
naming that member or pattern. ``--cross-check-n21`` rebuilds the N=21
members the census classifies as correlated and requires the enumerated law
to equal qpe_diagnostics.n21_labeled_law, whose Fraction values do not
factor over the two bits.
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import re
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import numpy as np  # noqa: E402
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister, transpile  # noqa: E402
from qiskit.circuit import Clbit, ControlFlowOp, Parameter  # noqa: E402
from qiskit.circuit.library import get_standard_gate_name_mapping  # noqa: E402
from qiskit.converters import circuit_to_dag  # noqa: E402
from qiskit.quantum_info import Operator, Statevector, partial_trace  # noqa: E402

import parallel  # noqa: E402
from diagnostic_experiments import record_groups  # noqa: E402
from experiments import Group, Member, all_experiment_groups  # noqa: E402
from live_run import OPT_LEVEL  # noqa: E402
from qpe_diagnostics import ideal_branch_probabilities, lift_phase_law, n21_labeled_law  # noqa: E402

OUTPUT = ROOT / "docs/evidence/walk-control-scaffolding/local_member_conformance.json"
BASIS = ["cz", "id", "rz", "sx", "x"]
SEED = 11
MAX_WIDTH = 10
# 2**12 branches of at most 2**MAX_WIDTH amplitudes bound the enumeration's
# live statevectors at 64 MiB.
MAX_BRANCH_OPS = 12
DYNAMIC = "mid-circuit measurement, reset or control flow"
TOLERANCE = 1e-9
STANDARD = set(get_standard_gate_name_mapping()) | {"barrier", "delay", "measure", "reset"}
CUTS = ("barrier", "delay", "measure")
# Members that execute a CZ scaffold their bound law does not need, each with
# the measurement that requires the scaffold.
SCAFFOLD_CONTROLS: dict[str, str] = {
    r"ripple_walk_lane\d+_readout[01]": (
        "walk readout controls bind the shared walk template, so they measure the scaffold's loss "
        "under the walk members' exact CZ load (README.md, 'Walk readout controls')"
    ),
    r"ripple_walk_lane\d+_pair\d+_\d+_depth0_packed": (
        "depth-0 origin of the walk depth axis binds the shared walk template, so every depth "
        "runs under the same CZ load and depth differences are not load differences "
        "(README.md, hypothesis 1)"
    ),
    r"scaffold_template_readout[01]": (
        "scaffold A/B arm: the template-bound readout against scaffold_measure_only and "
        "scaffold_x_measure isolates the scaffold's loss (diagnostic_controls.scaffold_ab_group)"
    ),
    r"null(rep)?_\d_\d_[XY]": (
        "gap-88 null arms bind primorial_campaigns.parametrized_arm at every network angle zero, so the "
        "eight-CNOT parity network is the identity under the gap-88 arms' CZ count and schedule, and "
        "primorial_tomography.null_subtracted removes the network's gate error from the fitted coefficients"
    ),
}
# Members whose entangling circuit maps the prepared input to a product state,
# each with what the circuit tests at that point.
PRODUCT_OUTPUT_PROBES: dict[str, str] = {
    r"rank_sector_\d+_(bright|kernel)_at_one_t\d+d\d+(_reference)?": (
        "rank-sector endpoint probes at parameter one: each prepared probe and the sector circuit at its "
        "endpoint compose to a product output, and the probe reads the compiled sector circuit there "
        "(rank_sector_experiments.sector_probes)"
    ),
    r"ripple_walk_lane\d+_pair\d+_\d+_depth1_packed": (
        "depth-1 point of the walk depth axis, where the walk sends its input to a product state; like "
        "every depth it executes the shared walk template"
    ),
    r"g88(rep)?_\d_\d_[XY]": (
        "gap-88 tomography arms: the diagonal network exp(-i gamma H) (primorial_tomography.parity_network) "
        "keeps the prepared (|x> + |x ^ 2^j>)/sqrt2 a product with qubit j carrying the relative phase "
        "2 gamma (H(x ^ 2^j) - H(x)), and the X and Y readouts of qubit j measure the cost coefficients c_S "
        "the CZ write into that phase (primorial_campaigns)"
    ),
}
# Dynamic members whose ideal law is a point mass or a product over classical
# bits and that execute CZ, each with the measurement the CZ serves.
DYNAMIC_LAW_PROBES: dict[str, str] = {
    r"(folded_qpe|qpe_archived)_s\d": (
        "one-hot two-bit eigenphase readout of |u_s>: the controlled rotations "
        "(order_finding.controlled_rotate) kick the eigenphase onto the control, so the CZ is the measured "
        "phase transfer (order_finding.folded_qpe)"
    ),
    "folded_qpe_null": (
        "identity-multiplier null of folded_qpe_mod15: it omits the controlled rotations and keeps "
        "eigenstate_prep's CRY and CX, so every folded member carries the same preparation CZ and the "
        "contrast with folded_qpe_s* isolates the controlled rotation; the control returns to |0> through "
        "H-H and reads 00 (experiments._folded_qpe_mod15)"
    ),
    r"qpe_delay_s\d": (
        "delay rung of the folded ladder: a calibration-bound delay replaces the first measurement and the "
        "prepared label supplies the correction, so the terminal bit reads the second controlled rotation's "
        "kickback (qpe_diagnostics.folded_diagnostic)"
    ),
    r"qpe_no_feed_forward_s\d": (
        "feed-forward-off control of the archived circuit: even labels stay one-hot and odd labels spread "
        "the terminal bit to a fair coin independent of b0; it executes the same controlled rotations, so "
        "the contrast with qpe_archived_s* isolates the conditional phase (qpe_diagnostics.folded_diagnostic)"
    ),
    r"correction_(known|measured)_s[13]": (
        "odd-label correction pair on one template (correction_circuits.correction_template): the measured "
        "arm conditions the -pi/2 correction on the recorded first bit and the known arm applies it from the "
        "label; both read the one-hot eigenphase the controlled rotations kick onto the control"
    ),
    "hybrid_shor_N15_a2": (
        "eight-bit order finding for N=15, a=2: the pruned law is uniform over y in {0, 64, 128, 192}, a "
        "product of the two top phase bits, which read the order-4 eigenphases the controlled "
        "multiplications by 2 and 4 modulo 15 (order_finding.append_controlled_modular_multiply) kick onto "
        "the control; hybrid_shor_N15_a2_null runs the schedule without them (experiments._hybrid_shor_mod15)"
    ),
    r"lr_(ff_0|ff_w|frame_0|frame_l|frame_lw)_err_(XY|YX)": (
        "quadrature arms of the latency-recovery family (latency_recovery.latency_recovery_circuit): the "
        "recovered Bell pair gives <XY> = <YX> = 0 and a product law, and a coherent phase over the idle "
        "window rotates the pair into these arms, which latency_recovery.coherence_and_phase reads"
    ),
    r"lr_ff_0_unencoded_err_(XX|YY)": (
        "unencoded control of the latency-recovery family: with d1 and d2 unencoded the syndrome ancilla a0 "
        "records Z on d0, which collapses the r-d0 Bell pair to <XX> = <YY> = 0 and a product law; the "
        "lr_code_property contrast against lr_ff_0 measures the coherence the code preserves, and the CZ "
        "prepare the pair and write that Z record"
    ),
    r"coherence_measure_reset_(xy|yx)": (
        "imaginary-part arms of the branch-signed coherence C = (S_XX + S_YY + i (S_XY - S_YX)) / 4: the "
        "round-1 orbit prefix's controlled swaps correlate b0 with the work pair, the ideal Im C = 0 leaves "
        "S_XY = S_YX = 0 and a product law, and a coherent window phase rotates C into these arms "
        "(coherence_window.coherence_circuit)"
    ),
}
DECLARATIONS: dict[str, dict[str, str]] = {
    "local_unitary": SCAFFOLD_CONTROLS,
    "product_output": PRODUCT_OUTPUT_PROBES,
    "dynamic_law": DYNAMIC_LAW_PROBES,
}


# A family configuration recorded before record_groups required a field
# predates its builder; only these (family, field) pairs mark one superseded,
# and every other missing field fails the census.
SUPERSEDED_FIELDS = {("patch-window", "measure_dt")}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def planned_groups(
    families: frozenset[str] | None = None,
) -> tuple[list[tuple[str, Group]], list[dict[str, str]]]:
    """Every registered group, plus each distinct retained family configuration's groups.

    families restricts the result to the retained configurations of those
    families, without the registered groups.
    """
    groups = [("registered", group) for group in all_experiment_groups()] if families is None else []
    seen: set[str] = set()
    superseded = []
    for path in sorted(glob.glob(str(ROOT / "results/live/*/record.json"))):
        record = json.loads(Path(path).read_text(encoding="utf-8"))
        family = record.get("family_configuration")
        if not isinstance(family, dict) or "name" not in family:
            continue
        if families is not None and family["name"] not in families:
            continue
        key = json.dumps(family, sort_keys=True)
        if key in seen:
            continue
        seen.add(key)
        run = Path(path).parent.relative_to(ROOT).as_posix()
        try:
            built = record_groups(record)
        except KeyError as missing:
            field = str(missing.args[0]) if missing.args else ""
            if (family["name"], field) not in SUPERSEDED_FIELDS:
                raise
            superseded.append({"run": run, "family": family["name"], "missing_field": field})
            continue
        groups += [(f"{family['name']}:{run}", group) for group in built]
    return groups, superseded


def structure(circuit: QuantumCircuit) -> list[Any]:
    """Canonical instruction list with every custom gate expanded into its definition.

    QPY serializes custom gates under names derived from object identity, and
    lazily built definitions carry counter-numbered circuit names, so both
    vary between processes; this form depends on the circuit alone.
    """
    out: list[Any] = [circuit.num_qubits, circuit.num_clbits, str(circuit.global_phase)]
    for instruction in circuit.data:
        operation = instruction.operation
        qubits = [circuit.find_bit(q).index for q in instruction.qubits]
        clbits = [circuit.find_bit(c).index for c in instruction.clbits]
        params = [str(param) for param in operation.params if not isinstance(param, (QuantumCircuit, np.ndarray))]
        params += [
            np.asarray(param).round(12).tobytes().hex() for param in operation.params if isinstance(param, np.ndarray)
        ]
        # Qiskit names an unnamed circuit-to-gate conversion circuit-N from a
        # process-wide counter; the expanded definition below carries its content.
        name = re.sub(r"^circuit-\d+$", "circuit", operation.name)
        row: list[Any] = [name, qubits, clbits, params]
        definition = getattr(operation, "definition", None)
        if isinstance(operation, ControlFlowOp):
            row.append(control_structure(circuit, operation))
        elif operation.name not in STANDARD and definition is not None:
            row.append(structure(definition))
        out.append(row)
    return out


def classical_operand(circuit: QuantumCircuit, value: Any) -> Any:
    """A condition or switch target by bit index: a Clbit, a register's bits, a (target, value) pair."""
    if isinstance(value, Clbit):
        return ["clbit", circuit.find_bit(value).index]
    if isinstance(value, ClassicalRegister):
        return ["register", [circuit.find_bit(bit).index for bit in value]]
    if isinstance(value, tuple):
        return [classical_operand(circuit, item) for item in value]
    if isinstance(value, (bool, int)) or value is None:
        return value
    return ["expr", str(value)]


def control_structure(circuit: QuantumCircuit, operation: ControlFlowOp) -> list[Any]:
    """The condition or switch target, the case labels, and the structure of every block."""
    cases = (
        [[str(label) for label in labels] for labels, _block in operation.cases_specifier()]
        if hasattr(operation, "cases_specifier")
        else []
    )
    return [
        classical_operand(circuit, getattr(operation, "condition", None)),
        classical_operand(circuit, getattr(operation, "target", None)),
        cases,
        [structure(block) for block in operation.blocks],
    ]


def digest(member: Member) -> str:
    binding = sorted((parameter.name, float(value)) for parameter, value in (member.binding or {}).items())
    text = json.dumps([structure(member.circuit), binding])
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def unitary_part(member: Member) -> QuantumCircuit | str:
    """The bound circuit without final measurements, or the reason it has no unitary."""
    bound = member.circuit.assign_parameters(member.binding) if member.binding else member.circuit
    bound = bound.remove_final_measurements(inplace=False)
    for instruction in bound.data:
        operation = instruction.operation
        if operation.name in ("measure", "reset") or getattr(operation, "blocks", None):
            return DYNAMIC
    return bound


def components(circuit: QuantumCircuit) -> list[QuantumCircuit]:
    """Connected pieces of the circuit's DAG once every barrier, delay and measurement is removed.

    Removing a barrier or delay cuts only the wires it touches, so operations on
    other qubits stay joined; each piece acts on its own qubits.
    """
    dag = circuit_to_dag(circuit)
    nodes = [node for node in dag.topological_op_nodes() if node.op.name not in CUTS]
    parent = {node._node_id: node._node_id for node in nodes}

    def root(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    for node in nodes:
        for successor in dag.op_successors(node):
            if successor._node_id in parent:
                parent[root(successor._node_id)] = root(node._node_id)
    grouped: dict[int, list[Any]] = {}
    for node in nodes:
        grouped.setdefault(root(node._node_id), []).append(node)
    pieces = []
    for group in grouped.values():
        qubits = sorted({circuit.find_bit(q).index for node in group for q in node.qargs})
        position = {q: k for k, q in enumerate(qubits)}
        piece = QuantumCircuit(len(qubits))
        for node in group:
            piece.append(node.op, [position[circuit.find_bit(q).index] for q in node.qargs])
        pieces.append(piece)
    return pieces


def product_output(circuit: QuantumCircuit) -> bool:
    """Every single-qubit reduced state of circuit|0...0> is pure."""
    bare = circuit.copy_empty_like()
    for instruction in circuit.data:
        if instruction.operation.name not in CUTS:
            bare.append(instruction)
    state = Statevector(bare)
    n = bare.num_qubits
    return all(abs(partial_trace(state, [k for k in range(n) if k != q]).purity() - 1) < TOLERANCE for q in range(n))


def classify(member: Member) -> str:
    """local, product, entangling, or the reason the member has no unitary to classify."""
    if member.circuit.num_qubits > MAX_WIDTH:
        return f"wider than {MAX_WIDTH} qubits"
    part = unitary_part(member)
    if isinstance(part, str):
        return part
    bare = part.copy_empty_like()
    for instruction in part.data:
        if instruction.operation.name not in CUTS:
            bare.append(instruction)
    if is_local(bare):
        return "local"
    return "product" if product_output(part) else "entangling"


def is_local(circuit: QuantumCircuit) -> bool:
    """Operator Schmidt rank 1 across every single-qubit cut."""
    n = circuit.num_qubits
    if n == 1:
        return True
    tensor = Operator(circuit).data.reshape((2,) * (2 * n))
    for q in range(n):
        out_axis, in_axis = n - 1 - q, 2 * n - 1 - q
        rest = [a for a in range(2 * n) if a not in (out_axis, in_axis)]
        matrix = np.transpose(tensor, [out_axis, in_axis, *rest]).reshape(4, -1)
        singular = np.linalg.svd(matrix, compute_uv=False)
        if singular[1] > TOLERANCE * singular[0]:
            return False
    return True


def scaffold_cz(member: Member, isa: QuantumCircuit) -> tuple[int, int]:
    """Total CZ of the bound ISA and the CZ inside components whose bound unitary is local."""
    binding = {p: v for p, v in (member.binding or {}).items() if isa.has_parameter(p)}
    bound = isa.assign_parameters(binding) if binding else isa
    total = int(bound.count_ops().get("cz", 0))
    local = 0
    for piece in components(bound):
        cz = int(piece.count_ops().get("cz", 0))
        if cz and is_local(piece):
            local += cz
    return total, local


def branch_ops(circuit: QuantumCircuit) -> int:
    """Measurements and resets on the longest classical path; an if_else runs one block per branch."""
    count = 0
    for instruction in circuit.data:
        operation = instruction.operation
        if operation.name in ("measure", "reset"):
            count += 1
        elif getattr(operation, "blocks", None):
            count += max(branch_ops(block) for block in operation.blocks)
    return count


def cz_count(circuit: QuantumCircuit) -> int:
    """CZ in the circuit and in every control-flow block, each of which executes on some branch."""
    count = 0
    for instruction in circuit.data:
        operation = instruction.operation
        if operation.name == "cz":
            count += 1
        for block in getattr(operation, "blocks", None) or ():
            count += cz_count(block)
    return count


def branch_law(member: Member) -> tuple[float, ...] | str:
    """The bound circuit's ideal law over its classical bits, or the reason it is not enumerated."""
    bound = member.circuit.assign_parameters(member.binding) if member.binding else member.circuit
    if max(branch_ops(bound), bound.num_clbits) > MAX_BRANCH_OPS:
        return f"more than {MAX_BRANCH_OPS} mid-circuit measurements, resets or classical bits"
    try:
        return ideal_branch_probabilities(bound)
    except ValueError as error:
        return f"unsupported control flow: {error}"


def law_kind(probabilities: tuple[float, ...], clbits: int) -> tuple[str, str | None]:
    """point_mass with its outcome (clbit 0 rightmost), bit_product, or correlated.

    The product test compares every joint entry with the product of the
    single-bit marginals at TOLERANCE.
    """
    law = np.asarray(probabilities, dtype=float)
    peak = int(np.argmax(law))
    if law[peak] > 1 - TOLERANCE:
        return "point_mass", format(peak, f"0{clbits}b") if clbits else ""
    tensor = law.reshape((2,) * clbits)
    product = np.ones(())
    for axis in range(clbits):
        product = np.multiply.outer(product, tensor.sum(axis=tuple(a for a in range(clbits) if a != axis)))
    return ("bit_product" if np.allclose(product, tensor, atol=TOLERANCE, rtol=0) else "correlated"), None


def without_multi_qubit_gates(circuit: QuantumCircuit) -> QuantumCircuit:
    """The circuit with every multi-qubit unitary removed, custom gates and control-flow blocks included.

    A custom gate is expanded into its definition first, so its single-qubit
    content stays; measurement, reset, barrier, delay and every condition stay.
    """
    out = circuit.copy_empty_like()
    for instruction in circuit.data:
        operation = instruction.operation
        definition = getattr(operation, "definition", None)
        if isinstance(operation, ControlFlowOp):
            blocks = [without_multi_qubit_gates(block) for block in operation.blocks]
            out.append(operation.replace_blocks(blocks), instruction.qubits, instruction.clbits)
        elif operation.name in ("measure", "reset", "barrier", "delay"):
            out.append(instruction)
        elif operation.name not in STANDARD and definition is not None:
            out.compose(without_multi_qubit_gates(definition), instruction.qubits, instruction.clbits, inplace=True)
        elif operation.num_qubits == 1:
            out.append(instruction)
    return out


def classify_dynamic(member: Member) -> tuple[str, str | None, int, bool | None] | str:
    """Law label, point-mass outcome, ISA CZ count and, for a correlated law, whether removing every
    multi-qubit gate leaves the law unchanged; or the reason the member stays unchecked.

    The circuit object is lowered as live_run compiles it, unbound for a
    shared template; a dynamic circuit has no unitary to split into local
    components, so every CZ counts. A correlated law that survives the
    removal comes from measurement and classical feed-forward alone.
    """
    law = branch_law(member)
    if isinstance(law, str):
        return law
    kind, outcome = law_kind(law, member.circuit.num_clbits)
    classical: bool | None = None
    if kind == "correlated":
        bound = member.circuit.assign_parameters(member.binding) if member.binding else member.circuit
        stripped = ideal_branch_probabilities(without_multi_qubit_gates(bound))
        classical = bool(np.allclose(stripped, law, atol=TOLERANCE, rtol=0))
    isa = transpile(member.circuit, basis_gates=BASIS, optimization_level=OPT_LEVEL, seed_transpiler=SEED)
    return kind, outcome, cz_count(isa), classical


def declaration(row: dict[str, Any], declarations: dict[str, dict[str, str]]) -> str | None:
    return next((pattern for pattern in declarations[row["kind"]] if re.fullmatch(pattern, row["member"])), None)


def unchecked_entry(name: str, key: str) -> dict[str, str]:
    """An unchecked member by name and digest, so a changed circuit under one name changes the census."""
    return {"member": name, "digest": key}


def unchecked_table(unchecked: dict[str, list[dict[str, str]]]) -> dict[str, list[dict[str, str]]]:
    return {
        reason: sorted(entries, key=lambda entry: (entry["member"], entry["digest"]))
        for reason, entries in sorted(unchecked.items())
    }


def dynamic_rows(
    dynamic: list[tuple[str, str, Member]],
) -> tuple[list[dict[str, Any]], dict[str, list[dict[str, str]]]]:
    """Record rows of the dynamic members, in their given order, and the unchecked ones by reason."""
    laws = parallel.ordered_map(classify_dynamic, [member for _name, _key, member in dynamic], min_items=2)
    rows: list[dict[str, Any]] = []
    unchecked: dict[str, list[dict[str, str]]] = {}
    for (name, key, member), law in zip(dynamic, laws, strict=True):
        if isinstance(law, str):
            unchecked.setdefault(law, []).append(unchecked_entry(name, key))
            continue
        row = {
            "member": name,
            "digest": key,
            "kind": "dynamic_law",
            "templated": bool(member.binding),
            "law": law[0],
            "outcome": law[1],
            "same_law_without_multi_qubit_gates": law[3],
            "cz": law[2],
        }
        rows.append(row | {"declared": declaration(row, DECLARATIONS)})
    return rows, unchecked


def census() -> dict[str, Any]:
    groups, superseded = planned_groups()
    members: dict[tuple[str, str], tuple[str, Member]] = {}
    for source, group in groups:
        for member in group.members:
            members.setdefault((member.name, digest(member)), (f"{source}/{group.name}", member))
    ordered = sorted(members.items())
    kinds = parallel.ordered_map(classify, [member for _, (_source, member) in ordered], min_items=2)
    unchecked: dict[str, list[dict[str, str]]] = {}
    checked: list[tuple[str, str, str, Member]] = []
    dynamic: list[tuple[str, str, Member]] = []
    entangling = 0
    for ((name, key), (_source, member)), kind in zip(ordered, kinds, strict=True):
        if kind in ("local", "product"):
            checked.append((kind, name, key, member))
        elif kind == "entangling":
            entangling += 1
        elif kind == DYNAMIC:
            dynamic.append((name, key, member))
        else:
            unchecked.setdefault(kind, []).append(unchecked_entry(name, key))
    compiled: dict[int, QuantumCircuit] = {}
    rows = []
    for kind, name, key, member in checked:
        if id(member.circuit) not in compiled:
            compiled[id(member.circuit)] = transpile(
                member.circuit, basis_gates=BASIS, optimization_level=OPT_LEVEL, seed_transpiler=SEED
            )
        total, scaffold = scaffold_cz(member, compiled[id(member.circuit)])
        row: dict[str, Any] = {
            "member": name,
            "digest": key,
            "kind": "local_unitary" if kind == "local" else "product_output",
            "templated": bool(member.binding),
            "cz": total,
            "cz_in_local_components": scaffold,
        }
        rows.append(row | {"declared": declaration(row, DECLARATIONS)})
    dynamic_law_rows, dynamic_unchecked = dynamic_rows(dynamic)
    rows += dynamic_law_rows
    for reason, names in dynamic_unchecked.items():
        unchecked.setdefault(reason, []).extend(names)
    rows.sort(key=lambda row: (row["member"], row["digest"]))
    return {
        "schema": "local-member-cz-conformance-v3",
        "basis": BASIS,
        "optimization_level": OPT_LEVEL,
        "seed_transpiler": SEED,
        "groups": len(groups),
        "superseded_configurations": superseded,
        "distinct_members": len(members),
        "entangling_members": entangling,
        "unchecked": unchecked_table(unchecked),
        "members": rows,
    }


def routes_dynamic(member: Member) -> bool:
    """classify sends the member to the branch-law audit."""
    return member.circuit.num_qubits <= MAX_WIDTH and isinstance(part := unitary_part(member), str) and part == DYNAMIC


def check_dynamic() -> None:
    """Recompute every dynamic member's row and unchecked reason, compare them with the stored census
    and enforce the dynamic declarations, without the static classification."""
    groups, _superseded = planned_groups()
    members: dict[tuple[str, str], Member] = {}
    for _source, group in groups:
        for member in group.members:
            members.setdefault((member.name, digest(member)), member)
    ordered = sorted(members.items())
    routed = parallel.ordered_map(routes_dynamic, [member for _key, member in ordered], min_items=2)
    dynamic = [(name, key, member) for ((name, key), member), flag in zip(ordered, routed, strict=True) if flag]
    rows, unchecked = dynamic_rows(dynamic)
    # Width is read from the circuit alone, so the over-width members of every
    # kind join the comparison without the static classification.
    for (name, key), member in ordered:
        if member.circuit.num_qubits > MAX_WIDTH:
            unchecked.setdefault(f"wider than {MAX_WIDTH} qubits", []).append(unchecked_entry(name, key))
    stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
    require(
        rows == [row for row in stored["members"] if row["kind"] == "dynamic_law"],
        f"{OUTPUT.relative_to(ROOT)} dynamic rows differ from the recomputed branch laws",
    )
    require(
        unchecked_table(unchecked) == stored["unchecked"],
        f"{OUTPUT.relative_to(ROOT)} unchecked members differ from the recomputed dynamic and width ones",
    )
    enforce(rows, {"dynamic_law": DYNAMIC_LAW_PROBES})
    declared = sum(needs_declaration(row) for row in rows)
    print(f"local-member conformance: {len(rows)} dynamic laws match the census, {declared} declared CZ executions")


def needs_declaration(row: dict[str, Any]) -> bool:
    """A local unitary needs one for scaffold CZ, a product output for any CZ, a dynamic member for
    any CZ under an uncorrelated law or a correlation its multi-qubit gates do not produce."""
    if row["kind"] == "dynamic_law":
        return bool(row["cz"]) and (row["law"] != "correlated" or bool(row["same_law_without_multi_qubit_gates"]))
    return bool(row["cz_in_local_components"] if row["kind"] == "local_unitary" else row["cz"])


def enforce(rows: list[dict[str, Any]], declarations: dict[str, dict[str, str]] = DECLARATIONS) -> None:
    violations = [r["member"] for r in rows if needs_declaration(r) and not r["declared"]]
    require(not violations, f"members executing CZ their law does not need, undeclared: {violations}")
    for patterns in declarations.values():
        for pattern in patterns:
            require(
                any(r["declared"] == pattern and needs_declaration(r) for r in rows),
                f"declaration {pattern} matches no member that executes CZ",
            )


def _dynamic_member(name: str, circuit: QuantumCircuit, binding: dict[Parameter, float] | None = None) -> Member:
    return Member(name, circuit, np.zeros(1 << circuit.num_clbits), binding)


Expected = tuple[str, str | None, bool, bool | None, bool]


def _synthetic_members() -> list[tuple[Member, Expected | str]]:
    """Dynamic circuits with their expected (law, outcome, executes CZ, same law without multi-qubit
    gates, needs a declaration) or unchecked reason."""
    cases: list[tuple[Member, Expected | str]] = []

    bell = QuantumCircuit(2, 2)
    bell.h(0)
    bell.cx(0, 1)
    bell.measure(0, 0)
    bell.reset(0)
    bell.measure(1, 1)
    cases.append((_dynamic_member("bell_measured_together", bell), ("correlated", None, True, False, False)))

    independent = QuantumCircuit(2, 2)
    independent.h([0, 1])
    independent.measure(0, 0)
    independent.reset(0)
    independent.measure(1, 1)
    cases.append((_dynamic_member("independent_coins", independent), ("bit_product", None, False, None, False)))

    # The unmeasured Bell pair keeps its CZ through the H that follows it.
    spectator = QuantumCircuit(3, 1)
    spectator.x(0)
    spectator.measure(0, 0)
    spectator.reset(0)
    spectator.h(1)
    spectator.cx(1, 2)
    cases.append((_dynamic_member("point_mass_spectator_cz", spectator), ("point_mass", "1", True, None, True)))

    remeasured = QuantumCircuit(1, 2)
    remeasured.x(0)
    remeasured.measure(0, 0)
    remeasured.reset(0)
    remeasured.measure(0, 1)
    cases.append((_dynamic_member("reset_after_measure", remeasured), ("point_mass", "01", False, None, False)))

    angle = Parameter("theta")
    templated = QuantumCircuit(1, 2)
    templated.rx(angle, 0)
    templated.measure(0, 0)
    templated.reset(0)
    templated.measure(0, 1)
    cases.append(
        (_dynamic_member("bound_template", templated, {angle: np.pi}), ("point_mass", "01", False, None, False))
    )

    forward = QuantumCircuit(2, 2)
    forward.x(0)
    forward.measure(0, 0)
    with forward.if_test((forward.clbits[0], 1)):
        forward.x(1)
    forward.measure(1, 1)
    cases.append((_dynamic_member("feed_forward_point_mass", forward), ("point_mass", "11", False, None, False)))

    copy = QuantumCircuit(2, 2)
    copy.h(0)
    copy.measure(0, 0)
    with copy.if_test((copy.clbits[0], 1)):
        copy.x(1)
    copy.measure(1, 1)
    cases.append((_dynamic_member("feed_forward_classical_copy", copy), ("correlated", None, False, True, False)))

    # Feed-forward copies the measured bit, so the correlation survives without
    # the spectator Bell pair and its CZ needs a declaration.
    scaffold = QuantumCircuit(4, 2)
    scaffold.h(0)
    scaffold.measure(0, 0)
    with scaffold.if_test((scaffold.clbits[0], 1)):
        scaffold.x(1)
    scaffold.h(2)
    scaffold.cx(2, 3)
    scaffold.measure(1, 1)
    cases.append((_dynamic_member("feed_forward_copy_spectator_cz", scaffold), ("correlated", None, True, True, True)))

    switch = QuantumCircuit(QuantumRegister(2), ClassicalRegister(2))
    switch.h(0)
    switch.measure(0, 0)
    with switch.switch(switch.clbits[0]) as case:
        with case(0):
            switch.x(1)
        with case(1):
            switch.h(1)
    switch.measure(1, 1)
    cases.append(
        (
            _dynamic_member("switch_case", switch),
            "unsupported control flow: unsupported exact-branch control flow switch_case",
        )
    )

    budget = QuantumCircuit(1, 1)
    for _ in range(MAX_BRANCH_OPS):
        budget.reset(0)
    budget.measure(0, 0)
    cases.append(
        (
            _dynamic_member("branch_budget", budget),
            f"more than {MAX_BRANCH_OPS} mid-circuit measurements, resets or classical bits",
        )
    )
    return cases


def self_test() -> None:
    cases = _synthetic_members()
    members = [member for member, _expected in cases]
    require(all(classify(member) == DYNAMIC for member in members), "a synthetic dynamic member left the dynamic path")
    results = parallel.ordered_map(classify_dynamic, members, min_items=2)
    for (member, expected), result in zip(cases, results, strict=True):
        if isinstance(expected, str):
            require(result == expected, f"{member.name}: {result!r}, expected {expected!r}")
            continue
        if isinstance(result, str):
            raise SystemExit(f"{member.name}: unchecked as {result!r}")
        law, outcome, cz, classical = result
        row = {"kind": "dynamic_law", "law": law, "cz": cz, "same_law_without_multi_qubit_gates": classical}
        observed = (law, outcome, cz > 0, classical, needs_declaration(row))
        require(observed == expected, f"{member.name}: {observed}, {cz} CZ; expected {expected}")
    flipped = []
    for gate in ("x", "h"):
        branch = QuantumCircuit(2, 2)
        branch.h(0)
        branch.measure(0, 0)
        with branch.if_test((branch.clbits[0], 1)):
            getattr(branch, gate)(1)
        branch.measure(1, 1)
        flipped.append(digest(_dynamic_member("same_name", branch)))
    require(flipped[0] != flipped[1], "members differing only in an if_else block share a digest")
    wide = QuantumCircuit(MAX_WIDTH + 1, 1)
    wide.measure(0, 0)
    wide.reset(0)
    wide.measure(0, 0)
    require(
        classify(_dynamic_member("wide", wide)) == f"wider than {MAX_WIDTH} qubits",
        "a member wider than MAX_WIDTH reached the branch enumeration",
    )
    print(f"local-member conformance self-test: {len(cases) + 1} synthetic dynamic members classified")


def _failure(check: Callable[[], None]) -> str:
    try:
        check()
    except SystemExit as failure:
        return str(failure)
    raise SystemExit("the declaration check passed where it must fail")


def self_test_undeclared() -> None:
    """The stored census fails without folded_qpe_null's declaration and with a stale pattern."""
    rows = json.loads(OUTPUT.read_text(encoding="utf-8"))["members"]
    require(
        all(row["declared"] == declaration(row, DECLARATIONS) for row in rows),
        f"{OUTPUT.relative_to(ROOT)} declarations differ from the declared patterns",
    )
    enforce(rows)

    def redeclared(declarations: dict[str, dict[str, str]]) -> list[dict[str, Any]]:
        return [row | {"declared": declaration(row, declarations)} for row in rows]

    dropped = DECLARATIONS | {
        "dynamic_law": {p: text for p, text in DYNAMIC_LAW_PROBES.items() if p != "folded_qpe_null"}
    }
    message = _failure(lambda: enforce(redeclared(dropped), dropped))
    expected = "members executing CZ their law does not need, undeclared: ['folded_qpe_null']"
    require(message == expected, f"undeclared folded_qpe_null failed with {message!r}")
    stale = DECLARATIONS | {"dynamic_law": DYNAMIC_LAW_PROBES | {"hybrid_shor_N15_a2_null": "CZ-free null"}}
    message = _failure(lambda: enforce(redeclared(stale), stale))
    expected = "declaration hybrid_shor_N15_a2_null matches no member that executes CZ"
    require(message == expected, f"stale declaration failed with {message!r}")
    print("local-member conformance: undeclared folded_qpe_null and a stale pattern both fail")


# Retained families whose groups hold every N=21 orbit or feedback member.
N21_FAMILIES = frozenset(
    {"n21-feedback", "n21-feedback-encoded", "n21-orbit-feedback", "n21-orbit-rca", "patch-window"}
)
N21_MEMBER = re.compile(r"(n21|orbit)_\w*feedback")


def _branch_law_and_kind(member: Member) -> tuple[tuple[float, ...] | str, str | None]:
    law = branch_law(member)
    return law, None if isinstance(law, str) else law_kind(law, member.circuit.num_clbits)[0]


def cross_check_n21() -> None:
    """The census's correlated N=21 members enumerate to n21_labeled_law, which does not factor."""
    for feed_forward in (True, False):
        exact = n21_labeled_law(feed_forward)
        bit0 = exact[1] + exact[3]
        bit1 = exact[2] + exact[3]
        product = [(bit0 if k & 1 else 1 - bit0) * (bit1 if k & 2 else 1 - bit1) for k in range(4)]
        require(
            sum(exact) == 1 and max(exact) < 1 and list(exact) != product,
            f"n21_labeled_law({feed_forward}) {exact} factors over its bits or is a point mass",
        )
    rows = json.loads(OUTPUT.read_text(encoding="utf-8"))["members"]
    expected = {
        (row["member"], row["digest"])
        for row in rows
        if row["kind"] == "dynamic_law" and row["law"] == "correlated" and N21_MEMBER.fullmatch(row["member"])
    }
    groups, _superseded = planned_groups(N21_FAMILIES)
    members: dict[tuple[str, str], Member] = {}
    for _source, group in groups:
        for member in group.members:
            if N21_MEMBER.fullmatch(member.name):
                members.setdefault((member.name, digest(member)), member)
    require(
        set(members) == expected,
        f"rebuilt N=21 members {sorted(set(members) - expected)} and census rows "
        f"{sorted(expected - set(members))} differ",
    )
    ordered = sorted(members.items())
    results = parallel.ordered_map(_branch_law_and_kind, [member for _key, member in ordered], min_items=2)
    for ((name, _key), member), (law, kind) in zip(ordered, results, strict=True):
        if isinstance(law, str):
            raise SystemExit(f"{name}: unchecked as {law!r}")
        exact = n21_labeled_law(not name.endswith("no_feedback"))
        # A heralded member measures every qubit first, so its ideal law is
        # the phase law lifted onto the herald bits, each reading 0.
        clbits = member.circuit.num_clbits
        ideal = lift_phase_law([float(value) for value in exact], clbits)
        require(
            np.allclose(law, ideal, atol=1e-11, rtol=0),
            f"{name}: enumerated law {law} differs from n21_labeled_law {exact} lifted onto {clbits} clbits {ideal}",
        )
        require(kind == "correlated", f"{name}: classified {kind}")
    heralded = sum(member.circuit.num_clbits > 2 for _key, member in ordered)
    print(
        f"local-member conformance: {len(ordered)} correlated N=21 members ({heralded} heralded) enumerate to "
        "n21_labeled_law"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--check-dynamic", action="store_true")
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--self-test-undeclared", action="store_true")
    mode.add_argument("--cross-check-n21", action="store_true")
    args = parser.parse_args()
    if args.check_dynamic:
        check_dynamic()
        return 0
    if args.self_test:
        self_test()
        return 0
    if args.self_test_undeclared:
        self_test_undeclared()
        return 0
    if args.cross_check_n21:
        cross_check_n21()
        return 0
    if args.write:
        # The census gates run under the qiskit-2.5 replay runtime
        # (ci/gates.json "runtime"), and a compiled member's digest follows
        # the transpiler release, so the census is written under that runtime.
        import qiskit

        requirements = (ROOT / "ci/requirements-replay.txt").read_text(encoding="utf-8").splitlines()
        pins = [line.split("==", 1)[1].strip() for line in requirements if line.startswith("qiskit==")]
        require(
            len(pins) == 1, f"ci/requirements-replay.txt pins qiskit {len(pins)} times; --write needs one qiskit== pin"
        )
        (pinned,) = pins
        require(
            qiskit.__version__ == pinned,
            f"--write runs under the replay runtime's qiskit {pinned} (REPLAY_PYTHON), not {qiskit.__version__}",
        )
    result = census()
    enforce(result["members"])
    text = json.dumps(result, indent=1) + "\n"
    if args.write:
        OUTPUT.write_text(text, encoding="utf-8")
    else:
        require(OUTPUT.read_text(encoding="utf-8") == text, f"{OUTPUT.relative_to(ROOT)} differs from the census")
    rows = result["members"]
    count = {kind: sum(r["kind"] == kind for r in rows) for kind in DECLARATIONS}
    declared = sum(needs_declaration(r) for r in rows)
    print(
        f"local-member conformance: {count['local_unitary']} local unitaries, {count['product_output']} product "
        f"outputs, {count['dynamic_law']} dynamic laws, {declared} declared CZ executions, "
        f"{result['entangling_members']} entangling"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
