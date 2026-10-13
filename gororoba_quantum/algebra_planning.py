"""Place complete static algebra families inside one disjoint execution job.

The family supplies sparse, reproducible execution rows and exact observables.
The existing runner owns calibration, compilation, placement, cost admission,
archive identity, and submission approval. Each family receives its own case.
"""

from __future__ import annotations

import math
from typing import Any

from qiskit import QuantumCircuit

from experiments import Group

FAMILIES = ("ripple", "rank-sector")


def family_definition(name: str) -> tuple[list[Group], dict[str, Any]]:
    if name == "ripple":
        from ripple_experiments import ripple_configuration, ripple_groups

        return ripple_groups(), ripple_configuration()
    if name == "rank-sector":
        from rank_sector_experiments import sector_configuration, sector_groups

        return sector_groups(), sector_configuration()
    raise ValueError(f"unknown static algebra family {name!r}")


def _bind_readout_controls(runtime: Any, choice: Any, definition: dict[str, Any]) -> None:
    """Prepare the physical writer of each routed atlas edge's measured bit.

    Edge templates may finish on different output wires despite their shared
    initial layout. Readout controls therefore follow the actual compiled
    measurement, before placement moves the complete lane as one pattern.
    """
    source_isas = {member.name: isa for member, isa in zip(choice.group.members, choice.isas, strict=True)}
    for index, member in enumerate(choice.group.members):
        metadata = definition.get("members", {}).get(member.name, {})
        source_name = metadata.get("readout_target")
        if source_name is None:
            continue
        if source_name not in source_isas:
            raise runtime.LiveRunError(f"{member.name}: readout control targets a member outside its lane")
        source = source_isas[source_name]
        writers = [qubits[0] for name, qubits in runtime._ops(source) if name == "measure"]
        if source.num_clbits != 1 or len(writers) != 1:
            raise runtime.LiveRunError(f"{member.name}: atlas readout target must have one measured output")
        bit = metadata.get("readout_value")
        if type(bit) is not int or bit not in (0, 1):
            raise runtime.LiveRunError(f"{member.name}: readout control requires a binary preparation")
        control = QuantumCircuit(source.num_qubits, 1, name=member.name)
        if bit:
            control.x(writers[0])
        control.measure(writers[0], 0)
        violations = runtime.target_violations(control, choice.snap.backend.target)
        if violations:
            raise runtime.LiveRunError(f"{member.name}: physical readout control violates the Target: {violations}")
        choice.isas[index] = control


def _validate_rows(runtime: Any, choices: list[Any], definition: dict[str, Any]) -> None:
    expected = definition.get("execution_row_count")
    if type(expected) is not int or expected <= 0:
        raise runtime.LiveRunError("static algebra row count must be a positive integer")
    if any(choice.group.execution_rows is None for choice in choices):
        raise runtime.LiveRunError("static algebra groups require explicit execution rows")
    rows = {row for choice in choices for row in choice.group.execution_rows or ()}
    if rows != set(range(expected)):
        raise runtime.LiveRunError("static algebra schedule differs from the complete declared execution rows")
    pubs = runtime.execution_pubs(choices)
    if len(pubs) != expected:
        raise runtime.LiveRunError("static algebra fusion changed the declared row count")
    names = [component.entry.name for pub in pubs for component in pub.components]
    required = [member.name for choice in choices for member in choice.group.members]
    if len(names) != len(set(names)) or set(names) != set(required):
        raise runtime.LiveRunError("static algebra fusion must execute each declared member exactly once")


def family_candidates(
    runtime: Any, snapshots: list[Any], args: Any, trace: dict[str, Any]
) -> list[tuple[list[Any], dict[str, Any]]]:
    """Search fresh backends with one replica per scientifically distinct lane."""
    groups, definition = family_definition(args.family)
    if args.max_replicas not in (None, 1):
        raise runtime.LiveRunError("static algebra lanes require --max-replicas 1")
    if args.optimize and args.replica_tiers != [1]:
        raise runtime.LiveRunError("static algebra lane designs require --replica-tiers 1")
    policy = runtime.ReplicaPolicy(args.replica_floor, 1, False, args.cross_group_buffer)
    candidates: list[tuple[list[Any], dict[str, Any]]] = []
    for snapshot in snapshots:
        backend_trace: dict[str, Any] = {}
        try:
            routed_sets = []
            for group in groups:
                routed_candidates = runtime.select_candidates(group, [snapshot], args.seeds, backend_trace)
                # Readout binding changes the scored physical instructions, so
                # the candidate limit follows binding and calibrated reranking.
                score_trace = backend_trace[group.name][snapshot.name]
                for row in score_trace:
                    if "joint_score" in row:
                        row["pre_readout_binding_joint_score"] = row.pop("joint_score")
                candidates_for_group = []
                for choice in routed_candidates:
                    candidate_trace = {"seed": choice.seed, "layout": choice.layout, "stage": "readout_bound_scoring"}
                    score_trace.append(candidate_trace)
                    try:
                        _bind_readout_controls(runtime, choice, definition)
                        scores = [runtime.layout_score(isa, choice.snap.backend.target) for isa in choice.isas]
                        joint = math.exp(sum(math.log(score) for score in scores) / len(scores))
                    except (runtime.LiveRunError, ValueError) as error:
                        candidate_trace["rejected"] = f"{type(error).__name__}: {error}"
                        continue
                    choice.member_scores = scores
                    choice.joint_score = joint
                    candidate_trace.update(member_scores=scores, joint_score=joint)
                    candidates_for_group.append(choice)
                candidates_for_group.sort(
                    key=lambda choice: (choice.joint_score, -choice.snap.pending_jobs), reverse=True
                )
                routed_sets.append(candidates_for_group[: args.optimizer_candidates])
            choices, placement = runtime.select_fusion_choices(routed_sets, policy)
            _validate_rows(runtime, choices, definition)
            pubs = runtime.execution_pubs(choices)
            if not pubs or any(pub.backend != snapshot.name or pub.kind != "static" for pub in pubs):
                raise runtime.LiveRunError("static algebra family must occupy one backend and static execution kind")
            if any(len(choice.replicas) != 1 for choice in choices):
                raise runtime.LiveRunError("static algebra lanes must retain one physical placement each")
            configuration = dict(definition)
            configuration.update(
                name=args.family,
                replica_cap=1,
                placement_contract="disjoint fixed lanes with explicit packed and isolated execution rows",
                placement=placement,
                measurement_sites={
                    entry.name: [list(qubits) for name, qubits in runtime._ops(entry.packed) if name == "measure"]
                    for choice in choices
                    for entry in choice.entries
                },
                dt_seconds=snapshot.backend.target.dt,
            )
            candidates.append((choices, configuration))
        except (runtime.LiveRunError, ValueError) as error:
            trace.setdefault("family_rejections", []).append({"backend": snapshot.name, "reason": str(error)})
        finally:
            trace.setdefault("algebra_backends", {})[snapshot.name] = backend_trace
    return candidates
