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
what its circuit tests. Every declared pattern must match at least one
member that executes CZ. Members with mid-circuit measurement, reset or
control flow, and members wider than MAX_WIDTH qubits, are listed as
unchecked with that reason. The per-member classification runs through
parallel.ordered_map, so GOROROBA_WORKERS caps it and the order is the
serial one.

``--write`` stores the census in
docs/evidence/walk-control-scaffolding/local_member_conformance.json;
``--check`` recomputes it, requires equality and enforces the declarations.
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import numpy as np  # noqa: E402
from qiskit import QuantumCircuit, transpile  # noqa: E402
from qiskit.circuit.library import get_standard_gate_name_mapping  # noqa: E402
from qiskit.converters import circuit_to_dag  # noqa: E402
from qiskit.quantum_info import Operator, Statevector, partial_trace  # noqa: E402

import parallel  # noqa: E402
from diagnostic_experiments import record_groups  # noqa: E402
from experiments import Group, Member, all_experiment_groups  # noqa: E402
from live_run import OPT_LEVEL  # noqa: E402

OUTPUT = ROOT / "docs/evidence/walk-control-scaffolding/local_member_conformance.json"
BASIS = ["cz", "id", "rz", "sx", "x"]
SEED = 11
MAX_WIDTH = 10
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
}


# A family configuration recorded before record_groups required a field
# predates its builder; only these (family, field) pairs mark one superseded,
# and every other missing field fails the census.
SUPERSEDED_FIELDS = {("patch-window", "measure_dt")}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def planned_groups() -> tuple[list[tuple[str, Group]], list[dict[str, str]]]:
    """Every registered group, plus each distinct retained family configuration's groups."""
    groups = [("registered", group) for group in all_experiment_groups()]
    seen: set[str] = set()
    superseded = []
    for path in sorted(glob.glob(str(ROOT / "results/live/*/record.json"))):
        record = json.loads(Path(path).read_text(encoding="utf-8"))
        family = record.get("family_configuration")
        if not isinstance(family, dict) or "name" not in family:
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
        if operation.name not in STANDARD and definition is not None:
            row.append(structure(definition))
        out.append(row)
    return out


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
            return "mid-circuit measurement, reset or control flow"
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


def census() -> dict[str, Any]:
    groups, superseded = planned_groups()
    members: dict[tuple[str, str], tuple[str, Member]] = {}
    for source, group in groups:
        for member in group.members:
            members.setdefault((member.name, digest(member)), (f"{source}/{group.name}", member))
    ordered = sorted(members.items())
    kinds = parallel.ordered_map(classify, [member for _, (_source, member) in ordered], min_items=2)
    unchecked: dict[str, list[str]] = {}
    checked: list[tuple[str, str, str, Member]] = []
    entangling = 0
    for ((name, key), (_source, member)), kind in zip(ordered, kinds, strict=True):
        if kind in ("local", "product"):
            checked.append((kind, name, key, member))
        elif kind == "entangling":
            entangling += 1
        else:
            unchecked.setdefault(kind, []).append(name)
    compiled: dict[int, QuantumCircuit] = {}
    rows = []
    for kind, name, key, member in checked:
        if id(member.circuit) not in compiled:
            compiled[id(member.circuit)] = transpile(
                member.circuit, basis_gates=BASIS, optimization_level=OPT_LEVEL, seed_transpiler=SEED
            )
        total, scaffold = scaffold_cz(member, compiled[id(member.circuit)])
        patterns = SCAFFOLD_CONTROLS if kind == "local" else PRODUCT_OUTPUT_PROBES
        rows.append(
            {
                "member": name,
                "digest": key,
                "kind": "local_unitary" if kind == "local" else "product_output",
                "templated": bool(member.binding),
                "cz": total,
                "cz_in_local_components": scaffold,
                "declared": next((pattern for pattern in patterns if re.fullmatch(pattern, name)), None),
            }
        )
    return {
        "schema": "local-member-cz-conformance-v2",
        "basis": BASIS,
        "optimization_level": OPT_LEVEL,
        "seed_transpiler": SEED,
        "groups": len(groups),
        "superseded_configurations": superseded,
        "distinct_members": len(members),
        "entangling_members": entangling,
        "unchecked": {reason: sorted(set(names)) for reason, names in sorted(unchecked.items())},
        "members": rows,
    }


def needs_declaration(row: dict[str, Any]) -> bool:
    """A local unitary needs one for scaffold CZ, a product output for any CZ."""
    return bool(row["cz_in_local_components"] if row["kind"] == "local_unitary" else row["cz"])


def enforce(result: dict[str, Any]) -> None:
    rows = result["members"]
    violations = [r["member"] for r in rows if needs_declaration(r) and not r["declared"]]
    require(not violations, f"members executing CZ their law does not need, undeclared: {violations}")
    for pattern in (*SCAFFOLD_CONTROLS, *PRODUCT_OUTPUT_PROBES):
        require(
            any(r["declared"] == pattern and needs_declaration(r) for r in rows),
            f"declaration {pattern} matches no member that executes CZ",
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = census()
    enforce(result)
    text = json.dumps(result, indent=1) + "\n"
    if args.write:
        OUTPUT.write_text(text, encoding="utf-8")
    else:
        require(OUTPUT.read_text(encoding="utf-8") == text, f"{OUTPUT.relative_to(ROOT)} differs from the census")
    rows = result["members"]
    local = sum(r["kind"] == "local_unitary" for r in rows)
    declared = sum(needs_declaration(r) for r in rows)
    print(
        f"local-member conformance: {local} local unitaries, {len(rows) - local} product outputs, "
        f"{declared} declared CZ executions, {result['entangling_members']} entangling"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
