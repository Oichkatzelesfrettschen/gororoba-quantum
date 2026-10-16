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
bound ISA is therefore cut at every barrier and delay, and only the CZ inside
a segment whose own bound unitary is local counts as scaffold. A member with
scaffold CZ fails unless SCAFFOLD_CONTROLS names it with the measurement that
requires the scaffold, and every declared pattern must match at least one
such member. Members with mid-circuit measurement, reset or control flow,
and members wider than MAX_WIDTH qubits, are listed as unchecked with that
reason.

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
from qiskit.quantum_info import Operator  # noqa: E402

from diagnostic_experiments import record_groups  # noqa: E402
from experiments import Group, Member, all_experiment_groups  # noqa: E402
from live_run import OPT_LEVEL  # noqa: E402

OUTPUT = ROOT / "docs/evidence/walk-control-scaffolding/local_member_conformance.json"
BASIS = ["cz", "id", "rz", "sx", "x"]
SEED = 11
MAX_WIDTH = 10
TOLERANCE = 1e-9
STANDARD = set(get_standard_gate_name_mapping()) | {"barrier", "delay", "measure", "reset"}
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
            superseded.append({"run": run, "family": family["name"], "missing_field": str(missing).strip("'")})
            continue
        groups += [(f"{family['name']}:{run}", group) for group in built]
    return groups, superseded


def structure(circuit: QuantumCircuit) -> list[Any]:
    """Canonical instruction list with every custom gate expanded into its definition.

    QPY serializes custom gates under names derived from object identity, so
    its bytes differ between processes; this form depends on the circuit alone.
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
        row: list[Any] = [operation.name, qubits, clbits, params]
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


def segments(circuit: QuantumCircuit) -> list[QuantumCircuit]:
    """The circuit cut at every barrier and delay, each piece on the full register."""
    pieces = [circuit.copy_empty_like()]
    for instruction in circuit.data:
        if instruction.operation.name in ("barrier", "delay"):
            pieces.append(circuit.copy_empty_like())
        elif instruction.operation.name != "measure":
            pieces[-1].append(instruction)
    return [piece for piece in pieces if piece.data]


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
    """Total CZ of the bound ISA and the CZ inside segments whose bound unitary is local."""
    binding = {p: v for p, v in (member.binding or {}).items() if isa.has_parameter(p)}
    bound = isa.assign_parameters(binding) if binding else isa
    total = int(bound.count_ops().get("cz", 0))
    local = 0
    for piece in segments(bound):
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
    unchecked: dict[str, list[str]] = {}
    local: list[tuple[str, str, Member]] = []
    entangling = 0
    for (name, key), (_source, member) in sorted(members.items()):
        if member.circuit.num_qubits > MAX_WIDTH:
            unchecked.setdefault(f"wider than {MAX_WIDTH} qubits", []).append(name)
            continue
        part = unitary_part(member)
        if isinstance(part, str):
            unchecked.setdefault(part, []).append(name)
            continue
        if is_local(part.remove_final_measurements(inplace=False)):
            local.append((name, key, member))
        else:
            entangling += 1
    compiled: dict[int, QuantumCircuit] = {}
    rows = []
    for name, key, member in local:
        if id(member.circuit) not in compiled:
            compiled[id(member.circuit)] = transpile(
                member.circuit, basis_gates=BASIS, optimization_level=OPT_LEVEL, seed_transpiler=SEED
            )
        total, scaffold = scaffold_cz(member, compiled[id(member.circuit)])
        declared = next((pattern for pattern in SCAFFOLD_CONTROLS if re.fullmatch(pattern, name)), None)
        rows.append(
            {
                "member": name,
                "digest": key,
                "templated": bool(member.binding),
                "cz": total,
                "cz_in_local_segments": scaffold,
                "declared_scaffold": declared,
            }
        )
    return {
        "schema": "local-member-cz-conformance-v1",
        "basis": BASIS,
        "optimization_level": OPT_LEVEL,
        "seed_transpiler": SEED,
        "groups": len(groups),
        "superseded_configurations": superseded,
        "distinct_members": len(members),
        "entangling_members": entangling,
        "unchecked": {reason: sorted(set(names)) for reason, names in sorted(unchecked.items())},
        "local_members": rows,
    }


def enforce(result: dict[str, Any]) -> None:
    rows = result["local_members"]
    violations = [r["member"] for r in rows if r["cz_in_local_segments"] and not r["declared_scaffold"]]
    require(not violations, f"local members executing CZ without a declaration: {violations}")
    for pattern in SCAFFOLD_CONTROLS:
        require(
            any(r["declared_scaffold"] == pattern and r["cz_in_local_segments"] for r in rows),
            f"declared scaffold {pattern} matches no local member that executes CZ",
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
    scaffolds = sum(1 for r in result["local_members"] if r["cz_in_local_segments"])
    print(
        f"local-member conformance: {len(result['local_members'])} local members, "
        f"{scaffolds} declared scaffold controls, {result['entangling_members']} entangling"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
