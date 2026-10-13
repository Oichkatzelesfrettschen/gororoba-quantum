"""Static Cayley-Dickson circuits with matched patches and a complete phase atlas.

Each edge keeps all eight phases on one lane and one compiled template. A
cyclic block assignment spreads each kite across the seven atlas lanes. Two
walk lanes exchange algebra classes against identical companion workloads.
Explicit sparse rows reserve genuinely isolated controls inside the same job.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter, ParameterExpression

import predict
from boolean_anf import anf_coefficients
from designs import SPECTRUM_EXEMPLARS, design_d_phase_sweep
from experiments import Group, Member, _associator_spectrum, fit_fringe, tvd
from ripple_dynamics import PAIRS, Pair, box_kites

SCHEDULE_SEED = 20261012
HARDWARE_DEPTHS = tuple(range(5))
ATLAS_LANES = 7
WALK_LANES = 2


@dataclass(frozen=True)
class ScheduledMember:
    member: Member
    metadata: dict[str, Any]


def _walk_ideal(pair: Pair, depth: int) -> np.ndarray:
    """Integer Gaussian butterfly prediction, independent of circuit synthesis."""
    signs = predict.associator_phase(32, *pair)[:16]
    numerator = np.zeros(16, dtype=complex)
    numerator[0] = 1
    for _ in range(depth):
        numerator *= signs
        for bit in range(4):
            for lower in range(16):
                if lower & (1 << bit):
                    continue
                upper = lower | (1 << bit)
                left, right = numerator[lower], numerator[upper]
                numerator[lower], numerator[upper] = left - 1j * right, right - 1j * left
    return np.asarray(np.abs(numerator) ** 2 / 16**depth, dtype=float)


def _logical_walk_template() -> tuple[
    QuantumCircuit, dict[tuple[Pair, int], dict[Parameter, float]], dict[int, dict[Parameter, float]]
]:
    """One topology preserves routing and measured sites across every walk arm."""
    coefficients = {
        pair: anf_coefficients([int(sign < 0) for sign in predict.associator_phase(32, *pair)[:16]]) for pair in PAIRS
    }
    masks = sorted({mask for table in coefficients.values() for mask in table})
    if 0 in masks:
        raise ValueError("walk template requires the certified zero-basis phase +1")
    circuit = QuantumCircuit(4, 4, name="ripple_walk_template")
    preparation = Parameter("walk_preparation")
    circuit.rx(preparation, range(4))
    angles: dict[tuple[int, int], Parameter] = {}
    mixers: dict[int, Parameter] = {}
    for layer in range(4):
        for mask in masks:
            angle = Parameter(f"walk_layer{layer}_mask{mask}")
            angles[layer, mask] = angle
            qubits = [bit for bit in range(4) if mask & (1 << bit)]
            if len(qubits) == 1:
                circuit.p(angle, qubits[0])
            else:
                circuit.mcp(angle, qubits[:-1], qubits[-1])
        circuit.barrier()
        mixers[layer] = Parameter(f"walk_mixer{layer}")
        circuit.rx(mixers[layer], range(4))
        circuit.barrier()
    circuit.measure(range(4), range(4))
    bindings = {}
    for pair in PAIRS:
        for depth in HARDWARE_DEPTHS:
            binding = {preparation: 0.0}
            binding.update(
                {
                    angle: math.pi if layer < depth and mask in coefficients[pair] else 0.0
                    for (layer, mask), angle in angles.items()
                }
            )
            binding.update({angle: math.pi / 2 if layer < depth else 0.0 for layer, angle in mixers.items()})
            bindings[pair, depth] = binding
    readout = {value: dict(bindings[PAIRS[0], 0]) | {preparation: value * math.pi} for value in (0, 1)}
    return circuit, bindings, readout


def _native_walk_circuit(source: QuantumCircuit) -> QuantumCircuit:
    """Lower diagonal monomials with parity phases and one symbolic phase sum.

    Basis translation repeatedly accumulates the global phases of controlled
    rotations. Native RZ/SX/CZ synthesis bounds that symbolic work while keeping
    every angle unbound for shared routing. A k-wire phase uses 2**k - 2 CZ
    gates through Gray-code parity cycles. Native topology can change routed
    gate counts, so calibration and statistical admission use a fresh compile.
    """
    circuit = QuantumCircuit(source.num_qubits, source.num_clbits, name=source.name)
    quarter_turns = 0
    phase_terms: list[ParameterExpression] = []

    def hadamard(qubit: int) -> None:
        nonlocal quarter_turns
        circuit.rz(math.pi / 2, qubit)
        circuit.sx(qubit)
        circuit.rz(math.pi / 2, qubit)
        quarter_turns += 1

    def controlled_x(control: int, target: int) -> None:
        hadamard(target)
        circuit.cz(control, target)
        hadamard(target)

    for instruction in source.data:
        qubits = [source.find_bit(qubit).index for qubit in instruction.qubits]
        clbits = [source.find_bit(clbit).index for clbit in instruction.clbits]
        operation = instruction.operation.name
        if operation in ("p", "mcphase"):
            angle = instruction.operation.params[0]
            width = len(qubits)
            # exp(i angle product((I-Z)/2)) factors into commuting parity
            # rotations and the constant term exp(i angle / 2**width).
            phase_terms.append(angle / (1 << width))
            for pivot_index, pivot in enumerate(qubits):
                previous_gray = 0
                for index in range(1 << pivot_index):
                    gray = index ^ (index >> 1)
                    transition = gray ^ previous_gray
                    if transition:
                        controlled_x(qubits[transition.bit_length() - 1], pivot)
                    sign = -1 if gray.bit_count() % 2 else 1
                    circuit.rz(sign * angle / (1 << (width - 1)), pivot)
                    previous_gray = gray
                if previous_gray:
                    controlled_x(qubits[previous_gray.bit_length() - 1], pivot)
        elif operation == "rx":
            angle = instruction.operation.params[0]
            circuit.rz(math.pi / 2, qubits[0])
            circuit.sx(qubits[0])
            circuit.rz(math.pi + angle, qubits[0])
            circuit.sx(qubits[0])
            circuit.rz(math.pi / 2, qubits[0])
            quarter_turns += 2
        elif operation == "barrier":
            circuit.barrier(qubits)
        elif operation == "measure":
            circuit.measure(qubits, clbits)
        else:
            raise ValueError(f"walk native synthesis does not support {operation}")
    circuit.global_phase = sum(phase_terms, source.global_phase + (quarter_turns % 8) * math.pi / 4)
    return circuit


def _walk_template() -> tuple[
    QuantumCircuit, dict[tuple[Pair, int], dict[Parameter, float]], dict[int, dict[Parameter, float]]
]:
    """Retain one native symbolic circuit and its original parameter identities."""
    source, bindings, readout = _logical_walk_template()
    return _native_walk_circuit(source), bindings, readout


def _definitions() -> tuple[list[Group], dict[str, Any]]:
    graphs, _, _ = box_kites()
    generator = random.Random(SCHEDULE_SEED)
    phase = Parameter("atlas_phase")
    templates: dict[tuple[int, int], QuantumCircuit] = {}
    edges: dict[tuple[int, int], dict[str, int]] = {}
    for kite, graph in enumerate(graphs):
        vertices = {vertex["id"]: vertex for vertex in graph["vertices"]}
        for edge_index, edge in enumerate(graph["edges"]):
            left, right = vertices[edge["source"]], vertices[edge["target"]]
            templates[kite, edge_index] = design_d_phase_sweep(
                (left["low"], left["high"]), (right["low"], right["high"]), phase
            )
            edges[kite, edge_index] = edge | {"left_high": left["high"], "right_high": right["high"]}
    walk_template, walk_bindings, walk_readout = _walk_template()
    walk_ideals = {(pair, depth): _walk_ideal(pair, depth) for pair in PAIRS for depth in HARDWARE_DEPTHS}
    groups_by_name: dict[str, list[ScheduledMember]] = {
        **{f"ripple_atlas_lane{lane}": [] for lane in range(ATLAS_LANES)},
        **{f"ripple_walk_lane{lane}": [] for lane in range(WALK_LANES)},
    }
    bundles: list[list[list[ScheduledMember]]] = []
    packed_walk: dict[tuple[int, Pair, int], str] = {}
    atlas_names: dict[tuple[int, int, int], str] = {}

    def atlas_member(kite: int, edge_index: int, phase_index: int, role: str, suffix: str) -> ScheduledMember:
        lane = (kite + edge_index) % ATLAS_LANES
        edge = edges[kite, edge_index]
        angle = phase_index * math.pi / 4
        name = (
            f"ripple_atlas_lane{lane}_kite{kite + 1}_edge{edge['source']}_{edge['target']}_phase{phase_index}_{suffix}"
        )
        expected = predict.phase_sweep_p0(
            (edge["source"], edge["left_high"]), (edge["target"], edge["right_high"]), angle
        )
        metadata = {
            "group": f"ripple_atlas_lane{lane}",
            "lane": lane,
            "kind": "atlas",
            "role": role,
            "kite": kite + 1,
            "edge_index": edge_index,
            "source": edge["source"],
            "target": edge["target"],
            "sign": edge["sign"],
            "phase_index": phase_index,
            "template_key": f"kite{kite + 1}_edge{edge_index}",
        }
        return ScheduledMember(
            Member(
                name,
                templates[kite, edge_index],
                np.array([expected, 1 - expected]),
                {phase: angle},
                weights=np.array([1.0, 0.0]),
            ),
            metadata,
        )

    def walk_member(lane: int, pair: Pair, depth: int, role: str) -> ScheduledMember:
        name = f"ripple_walk_lane{lane}_pair{pair[0]}_{pair[1]}_depth{depth}_{role}"
        metadata = {
            "group": f"ripple_walk_lane{lane}",
            "lane": lane,
            "kind": "walk",
            "role": role,
            "pair": list(pair),
            "depth": depth,
            "template_key": "walk_union_anf",
        }
        if role == "packed":
            packed_walk[lane, pair, depth] = name
        else:
            metadata["packed_member"] = packed_walk[lane, pair, depth]
        weights = np.zeros(16)
        weights[0] = 1
        return ScheduledMember(
            Member(name, walk_template, walk_ideals[pair, depth], walk_bindings[pair, depth], weights=weights), metadata
        )

    slots = [(edge_index, phase_index) for edge_index in range(12) for phase_index in range(8)]
    matched_slots = dict(zip(generator.sample(slots, len(HARDWARE_DEPTHS)), HARDWARE_DEPTHS, strict=True))
    for edge_index, phase_index in slots:
        atlas = [atlas_member(kite, edge_index, phase_index, "atlas", "atlas") for kite in range(ATLAS_LANES)]
        for entry in atlas:
            atlas_names[entry.metadata["kite"] - 1, edge_index, phase_index] = entry.member.name
        if (edge_index, phase_index) not in matched_slots:
            bundles.append([atlas])
            continue
        depth = matched_slots[edge_index, phase_index]
        duplicate = [
            atlas_member(kite, edge_index, phase_index, "companion", f"companion_depth{depth}")
            for kite in range(ATLAS_LANES)
        ]
        first_orientation = generator.randrange(2)
        for assignment, row in enumerate((atlas, duplicate)):
            for lane in range(WALK_LANES):
                pair = PAIRS[(lane + assignment + first_orientation) % 2]
                row.append(walk_member(lane, pair, depth, "packed"))
        bundles.append([atlas, duplicate])
    for lane in range(WALK_LANES):
        for pair in PAIRS:
            bundles.append([[walk_member(lane, pair, 4, "isolated")]])
    for kite in range(ATLAS_LANES):
        sign = edges[kite, 0]["sign"]
        isolated = []
        for phase_index in (0, 4) if sign > 0 else (4, 0):
            entry = atlas_member(kite, 0, phase_index, "isolated", "isolated")
            entry.metadata["packed_member"] = atlas_names[kite, 0, phase_index]
            isolated.append([entry])
        bundles.append(isolated)
    for edge_index in range(12):
        readout_rows = []
        for value in (0, 1):
            row = []
            for kite in range(ATLAS_LANES):
                lane = (kite + edge_index) % ATLAS_LANES
                circuit = QuantumCircuit(5, 1, name=f"ripple_atlas_readout{value}")
                if value:
                    circuit.x(4)
                circuit.measure(4, 0)
                name = f"ripple_atlas_lane{lane}_edge{edge_index}_readout{value}"
                row.append(
                    ScheduledMember(
                        Member(name, circuit, np.array([1 - value, value], dtype=float)),
                        {
                            "group": f"ripple_atlas_lane{lane}",
                            "lane": lane,
                            "kind": "atlas",
                            "role": "readout",
                            "readout_value": value,
                            "readout_target": atlas_names[kite, edge_index, 0],
                            "requires_routed_readout_control": True,
                        },
                    )
                )
            if edge_index == 0:
                for lane in range(WALK_LANES):
                    ideal = np.zeros(16)
                    ideal[15 * value] = 1
                    name = f"ripple_walk_lane{lane}_readout{value}"
                    row.append(
                        ScheduledMember(
                            Member(name, walk_template, ideal, walk_readout[value]),
                            {
                                "group": f"ripple_walk_lane{lane}",
                                "lane": lane,
                                "kind": "walk",
                                "role": "readout",
                                "readout_value": value,
                                "template_key": "walk_union_anf",
                            },
                        )
                    )
            readout_rows.append(row)
        bundles.append(readout_rows)

    ladder_sources: dict[str, Group] = {}
    atlas_bundles = [bundle for bundle in bundles if len(bundle) == 1 and bundle[0][0].metadata["role"] == "atlas"]
    ladder_bundles = generator.sample(atlas_bundles, 3)
    for lane, (dimension, first, second) in enumerate(SPECTRUM_EXEMPLARS):
        original = _associator_spectrum(dimension, first, second)
        group_name = "ripple_" + original.name
        groups_by_name[group_name] = []
        ladder_sources[group_name] = original
        for member_index, source in enumerate(original.members):
            name = "ripple_" + source.name
            member = Member(name, source.circuit, source.ideal, source.binding, weights=source.weights)
            metadata = {
                "group": group_name,
                "lane": lane,
                "kind": "ladder",
                "role": "ladder",
                "dimension": dimension,
                "variant": ("true", "flip", "omit")[member_index],
                "source_member": source.name,
            }
            ladder_bundles[member_index][0].append(ScheduledMember(member, metadata))
            if member_index == 0:
                isolated_member = Member(
                    name + "_isolated", source.circuit, source.ideal, source.binding, weights=source.weights
                )
                bundles.append(
                    [[ScheduledMember(isolated_member, metadata | {"role": "isolated", "packed_member": name})]]
                )
    generator.shuffle(bundles)
    rows: list[dict[str, Any]] = []
    member_metadata = {}
    matched_rows: dict[str, list[int]] = {}
    for bundle in bundles:
        for entries in bundle:
            index = len(rows)
            for entry in entries:
                entry.metadata["execution_row"] = index
                groups_by_name[entry.metadata["group"]].append(entry)
                member_metadata[entry.member.name] = entry.metadata
            walks = [
                entry for entry in entries if entry.metadata["kind"] == "walk" and entry.metadata["role"] == "packed"
            ]
            if walks:
                matched_rows.setdefault(str(walks[0].metadata["depth"]), []).append(index)
            rows.append(
                {
                    "row": index,
                    "members": [entry.member.name for entry in entries],
                    "role": "matched_walk" if walks else entries[0].metadata["role"],
                }
            )

    def group(name: str, entries: list[ScheduledMember]) -> Group:
        # The deepest walk and an entangling edge drive the initial layout,
        # independently of the randomized execution order.
        def priority(entry: ScheduledMember) -> tuple[bool, bool, int]:
            item = entry.metadata
            primary = (
                item["kind"] == "walk"
                and item["role"] == "packed"
                and item["depth"] == 4
                or item["kind"] == "atlas"
                and item["role"] == "atlas"
                and item["edge_index"] == 0
                or item["kind"] == "ladder"
                and item["role"] == "ladder"
                and item["variant"] == "true"
            )
            return not primary, item["role"] == "readout", -item.get("depth", 0)

        entries.sort(key=priority)
        members = tuple(entry.member for entry in entries)

        def summarize(distributions: dict[str, np.ndarray]) -> dict[str, float]:
            distances = [tvd(distributions[member.name], member.ideal) for member in members]
            result = {"mean_tvd_to_ideal": float(np.mean(distances)), "max_tvd_to_ideal": max(distances)}
            if name in ladder_sources:
                source_group = ladder_sources[name]
                result.update(
                    source_group.summarize(
                        {member.name: distributions["ripple_" + member.name] for member in source_group.members}
                    )
                )
            for entry in entries:
                if entry.metadata["kind"] == "walk" or entry.metadata["role"] in ("readout", "isolated"):
                    result[entry.member.name + "_p0"] = float(distributions[entry.member.name][0])
            edge_sets: dict[str, dict[int, str]] = {}
            for entry in entries:
                if entry.metadata["kind"] == "atlas" and entry.metadata["role"] == "atlas":
                    edge_sets.setdefault(entry.metadata["template_key"], {})[entry.metadata["phase_index"]] = (
                        entry.member.name
                    )
            for template_key, phase_members in edge_sets.items():
                fit = fit_fringe(
                    [index * math.pi / 4 for index in range(8)],
                    [float(distributions[phase_members[index]][0]) for index in range(8)],
                )
                result.update({template_key + "_" + quantity: value for quantity, value in fit.items()})
            return result

        return Group(
            name, members, summarize, execution_rows=tuple(entry.metadata["execution_row"] for entry in entries)
        )

    configuration = {
        "name": "ripple",
        "schedule_seed": SCHEDULE_SEED,
        "execution_row_count": len(rows),
        "atlas_lanes": ATLAS_LANES,
        "walk_lanes": WALK_LANES,
        "ladder_lanes": len(SPECTRUM_EXEMPLARS),
        "logical_qubits": 55,
        "rows": rows,
        "members": member_metadata,
        "matched_walk_rows": matched_rows,
        "interpretation_limits": [
            "Every edge's eight phases use one template and one lane; different edges are separate experiments.",
            "Cyclic edge-block assignment spreads each kite over seven patches; each edge stays on one patch.",
            "Matched walk rows repeat seven atlas companions and exchange algebra classes between two fixed patches.",
            "Zero-angle bindings preserve the full compiled walk topology, including its idle entangling cost.",
            "Native parity-phase synthesis keeps exact global phase; changed routing costs require fresh admission.",
            "Each atlas template has zero/one readout controls reconstructed on its own admitted final ancilla writer.",
            "Zero/one preparations probe endpoint bias; they do not identify a correlated readout channel.",
            "Design C true/flip/omit retains its own ideals; distinct routed templates can change readout sites.",
            "Isolated edge controls cover one representative edge per lane; other edges lack isolated comparisons.",
            "Fringe fits and collision summaries need separate uncertainty calculations for inferential use.",
            "Basis distributions constrain short prefixes; long recurrences and computational advantage stay separate.",
        ],
    }
    return [group(name, entries) for name, entries in groups_by_name.items()], configuration


def ripple_groups() -> list[Group]:
    """Rebuild the complete static family in deterministic lane order."""
    return _definitions()[0]


def ripple_configuration() -> dict[str, Any]:
    """Return the deterministic member, phase, patch, and execution-row contract."""
    return _definitions()[1]
