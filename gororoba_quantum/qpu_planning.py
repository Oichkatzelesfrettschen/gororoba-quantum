"""Calibration-bound experiment design above the existing Runtime execution path.

The runtime adapter supplies compilation, packing, and simulation. Keeping those
operations in live_run preserves its hardware admission and archive contracts;
the optimizer receives explicit scientific quantities and accounting units.
"""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import math
import threading
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.exceptions import QiskitError
from qiskit.transpiler import Target

import law_encoding
import local_compute
import measurement_sequence_analysis
import measurement_sequence_scatter
import msq_envelope
import msq_envelope_analysis
import msq_successor_analysis
import n21_exact_planning
import parallel
from diagnostic_experiments import (
    MSQ_ARM_STEPS,
    MSQ_DYNAMIC_STEPS,
    MSQ_FAMILY,
    MSQ_PREREADOUT_SECONDS,
    MSQ_SETTLE_SECONDS,
    MSQ_STEPS,
    MSQ_T1_MICROSECONDS,
    MSQ_THETA,
    MSQD_ARM_STEPS,
    MSQD_FAMILY,
    MSQE_FAMILY,
    MSQE_RESET_CONTROLS,
    MSQR_EQUILIBRIUM_SECONDS,
    MSQR_FAMILY,
    MSQR_READER_IDLE_SECONDS,
    MSQR_SENTINEL_ROWS,
    N21_FAMILIES,
    N21_OVERLAP_ARM,
    PATCH_FAMILIES,
    STATE_PREP_ARM_STEPS,
    STATE_PREP_DYNAMIC_ARMS,
    STATE_PREP_FAMILY,
    STATE_PREP_HISTORY_ARM,
    STATE_PREP_SOURCE_RECORD,
    family_contracts,
    folded_group,
    measurement_sequence_groups,
    msq_diagnostic_groups,
    msqe_groups,
    msqe_pattern_bits,
    msqr_groups,
    msqr_reader_stem,
    msqr_row_count,
    n21_group,
    n21_orbit_rca_group,
    state_prep_arms,
    state_prep_groups,
)
from experiment_optimizer import (
    EMPIRICAL_BERNSTEIN,
    BudgetContract,
    CandidatePlan,
    CostScenario,
    CovarianceBound,
    EmpiricalBernsteinDesign,
    JobCandidate,
    ObservableContract,
    ObservableTerm,
    ObservedPub,
    PubPrediction,
    analyze_observations,
    observation_power_radii,
    observed_empirical_bernstein,
    optimize,
    planned_empirical_bernstein,
)
from latency_recovery import (
    DEFAULT_LATENCY_DT,
    DEFAULT_WINDOW_DT,
    LATENCY_RECOVERY_FAMILY,
    latency_recovery_group,
    syndrome_window_violations,
)
from packing import Replica
from qpe_diagnostics import (
    compact_ideal_circuit,
    has_herald,
    herald_measurement,
    ideal_compiled_probabilities,
    n21_dose_key,
    n21_dose_name,
    n21_dose_violations,
    n21_ramsey_multiple,
    n21_segmented_key,
    n21_work_ramsey_key,
    oracle_key,
    phase_marginal,
)

# The ground Ramsey sweep's preregistered analysis. Its source closure (the
# analyzer and every scripts/ module it imports, transitively) joins the
# approval-bound design; experiment_digest covers gororoba_quantum/, so a
# change to any closure file makes the approved record's policy differ and
# the submission refuse with approval_required.
SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
RAMSEY_ANALYZER = SCRIPTS_DIR / "n21_spectator_ramsey.py"
# The segmented ground sweep's preregistered analysis, bound the same way
# under its own design key.
SEGMENTED_ANALYZER = SCRIPTS_DIR / "n21_q143_segmented_sweep.py"
# The segmented analyzer decodes every member through gororoba_quantum/
# modules after collection, so its closure follows imports into both
# directories and an amended module reads as an amended analysis.
MODULES_DIR = Path(__file__).resolve().parent


def scripts_closure(entry: Path, directories: tuple[Path, ...]) -> list[Path]:
    """entry and every module of directories its imports reach, at any nesting, sorted by name."""
    seen: dict[str, Path] = {}
    pending = [entry]
    while pending:
        path = pending.pop()
        if path.name in seen:
            continue
        seen[path.name] = path
        for node in ast.walk(ast.parse(path.read_text(), str(path))):
            names = (
                [alias.name for alias in node.names]
                if isinstance(node, ast.Import)
                else [node.module]
                if isinstance(node, ast.ImportFrom) and node.module and node.level == 0
                else []
            )
            for name in names:
                for directory in directories:
                    candidate = directory / f"{name.split('.')[0]}.py"
                    if candidate.is_file():
                        pending.append(candidate)
    return [seen[name] for name in sorted(seen)]


def ramsey_analyzer_closure() -> dict[str, Any]:
    """Per-file sha256 of the analyzer's scripts/ closure and the sha256 of that map's canonical JSON."""
    return analyzer_closure(RAMSEY_ANALYZER, (SCRIPTS_DIR,))


def observable_contract_records(contracts: Any) -> list[dict[str, Any]]:
    """The observable contracts as record.json stores them, each term's score values through law_encoding."""
    records = json.loads(json.dumps([asdict(contract) for contract in contracts]))
    for record in records:
        for term in record["terms"]:
            term["values"] = law_encoding.encode(term["values"])
    return records


def segmented_analyzer_closure() -> dict[str, Any]:
    """analyzer_closure of the segmented ground sweep's analysis over scripts/ and gororoba_quantum/."""
    return analyzer_closure(SEGMENTED_ANALYZER, (SCRIPTS_DIR, MODULES_DIR))


def analyzer_closure(entry: Path, directories: tuple[Path, ...]) -> dict[str, Any]:
    """Per-file sha256 of entry's closure over directories and the sha256 of that map's canonical JSON.

    Callers pass directories read from the module globals at call time, so a
    contract that points SCRIPTS_DIR at a modified copy hashes that copy.
    """
    files = {
        f"{path.parent.name}/{path.name}": hashlib.sha256(path.read_bytes()).hexdigest()
        for path in scripts_closure(entry, directories)
    }
    digest = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()
    return {"sha256": digest, "files": files}


def contract_configuration(family: str, configuration: dict[str, Any]) -> dict[str, Any]:
    """family_contracts' configuration keyword for a family whose contracts read its candidate's configuration.

    state-prep-control and the measurement-sequence families read their named qubits and
    n21-orbit-rca its herald outcome width there; prepare and live_run.approved_family_design both
    pass this, so a reused approved design rebuilds the approved contracts.
    """
    return (
        {"configuration": configuration}
        if family in (STATE_PREP_FAMILY, MSQ_FAMILY, MSQD_FAMILY, MSQE_FAMILY, MSQR_FAMILY, "n21-orbit-rca")
        else {}
    )


def settings(args: Any) -> dict[str, Any]:
    """Approval-bound design inputs, distinct from fluctuating quota readings.

    A declared preparation excitation, the empirical-Bernstein opt-in, a
    state-prep arm selection, the n21-orbit-rca initialization herald, its
    overlap split, its ground-control split, its window doses, its pinned layout, the latency-recovery delays and
    the envelope's layout width join them only when given, so a plan without them keeps its settings unchanged.
    """
    excitation = getattr(args, "prep_excitation", None)
    bernstein = {"empirical_bernstein": True} if getattr(args, "empirical_bernstein", False) else {}
    arms = getattr(args, "state_prep_arms", None)
    herald = {"init_herald": True} if getattr(args, "init_herald", False) else {}
    split = {"overlap_split": True} if getattr(args, "overlap_split", False) else {}
    ground = {"ground_control_split": True} if getattr(args, "ground_control_split", False) else {}
    windows = getattr(args, "ramsey_windows", None)
    ramsey = {"ramsey_windows": list(windows), "ramsey_analyzer_closure": ramsey_analyzer_closure()} if windows else {}
    sweep = getattr(args, "segmented_sweep", None)
    segmented = {"segmented_sweep": sweep, "segmented_analyzer_closure": segmented_analyzer_closure()} if sweep else {}
    doses = getattr(args, "window_doses_dt", None)
    dosed: dict[str, Any] = {"window_doses": list(doses)} if doses else {}
    if getattr(args, "detuning_sign", False):
        dosed["detuning_sign"] = True
    latency = {
        name: getattr(args, name) for name in ("latency_dt", "window_dt") if getattr(args, name, None) is not None
    }
    pin = getattr(args, "pin_layout", None)
    width = getattr(args, "layout_width", None)
    return (
        {
            name: getattr(args, name, default)
            for name, default in (
                ("family", None),
                ("optimize", False),
                ("objective", "minimum_charge"),
                ("cost_scenarios", []),
                ("shot_tiers", [2048, 4096, 8192, 16384]),
                ("shot_allocation", "uniform"),
                ("replica_tiers", [1, 2, 4]),
                ("optimizer_candidates", 6),
                ("model_shots", 32768),
                ("precision", 0.08),
                ("alpha", 0.05),
                ("power", 0.8),
                ("simulation_alpha", 0.01),
                ("job_overhead_seconds", 2.3),
                ("classical_latency_us", 20.0),
                ("reserve_seconds", 0.0),
                ("max_total_execution_seconds", None),
                ("patch_qubits", None),
                ("model_method", "sampled"),
                ("replica_variance_bound", None),
            )
        }
        | ({"prep_excitation": excitation} if excitation is not None else {})
        | bernstein
        | ({"state_prep_arms": list(arms)} if arms is not None else {})
        | herald
        | split
        | ground
        | ramsey
        | segmented
        | dosed
        | latency
        | ({"layout_width": width} if width is not None else {})
        | (
            {
                "pin_layout": {"backend": pin["backend"], "qubits": list(pin["qubits"])}
                | ({"replicas": [list(path) for path in pin["replicas"]]} if "replicas" in pin else {})
            }
            if pin is not None
            else {}
        )
    )


def budget_plan(runtime: Any, choices: list[Any], args: Any, usage: dict[str, Any]) -> dict[str, Any]:
    """Reserve all ceilings before any job starts, including unsent batches."""
    ceiling = getattr(args, "max_execution_seconds", None)
    jobs = []
    pub_shots = getattr(args, "pub_shots", None)
    if pub_shots is not None:
        names = [pub.name for pub in runtime.execution_pubs(choices)]
        if (
            not isinstance(pub_shots, dict)
            or len(names) != len(set(names))
            or set(pub_shots) != set(names)
            or any(type(value) is not int or value <= 0 for value in pub_shots.values())
        ):
            raise runtime.LiveRunError("shot allocation must assign a positive integer to every execution PUB exactly")
    for backend in sorted({choice.snap.name for choice in choices}):
        selected = [choice for choice in choices if choice.snap.name == backend]
        backend_shots = (
            {pub.name: pub_shots[pub.name] for pub in runtime.execution_pubs(selected)}
            if pub_shots is not None
            else None
        )
        for kind in ("dynamic", "static"):
            batches = (
                runtime.submission_batches(selected, kind, args.shots, pub_shots=backend_shots)
                if backend_shots is not None
                else runtime.submission_batches(selected, kind, args.shots)
            )
            for index, batch in enumerate(batches, 1):
                jobs.append(
                    {
                        "backend": backend,
                        "kind": kind,
                        "batch_index": index,
                        "pubs": len(batch),
                        "ceiling_seconds": ceiling,
                        **(
                            {
                                "shots": runtime.batch_shots(batch, args.shots, backend_shots),
                                "pub_names": [pub.name for pub in batch],
                            }
                            if pub_shots is not None
                            else {}
                        ),
                    }
                )
    total = None if ceiling is None else float(ceiling) * len(jobs)
    reserve = float(getattr(args, "reserve_seconds", 0.0))
    cap = getattr(args, "max_total_execution_seconds", None)
    remaining = usage.get("usage_remaining_seconds")
    reasons = []
    if usage.get("usage_limit_reached"):
        reasons.append("the instance reports its usage limit reached")
    if total is not None:
        if cap is not None and total > cap:
            reasons.append(f"combined execution ceiling {total} s exceeds invocation cap {cap} s")
        if remaining is not None and total + reserve > float(remaining):
            reasons.append(
                f"combined execution ceiling {total} s plus reserve {reserve} s exceeds remaining {remaining} s"
            )
    return {
        "jobs": jobs,
        "combined_ceiling_seconds": total,
        "reserve_seconds": reserve,
        "max_total_execution_seconds": cap,
        "remaining_seconds": remaining,
        "admitted": not reasons,
        "reasons": reasons,
        "reservation_scope": "invocation-local ceilings; external submissions can change shared quota",
    }


def window_durations(runtime: Any, snapshot: Any, controls: list[int] | None = None) -> tuple[int, int, float]:
    """Readout length and echo half-window in dt from the routed control's measure and reset.

    controls names the physical qubits of the routed control's mid-circuit
    measure and reset; their slowest measure and reset set the window. With controls
    None the backend's slowest qubit sets it, which bounds the window of every
    placement before routing names the control. The delay arm idles one
    readout length. The echo halves together cover 1.2 times the measure plus
    reset, so the second X precedes the second round and no tail of the window
    stays unechoed.
    """
    longest, rounded, dt = _longest_window_dt(runtime, snapshot, controls)
    return rounded(longest["measure"]), rounded(0.6 * (longest["measure"] + longest["reset"])), dt


def reset_window_dt(runtime: Any, snapshot: Any, controls: list[int] | None = None) -> int:
    """The control's reset length in dt, rounded up to granularity, over the sites window_durations reads.

    The overlap split's idle spectator idles the measure plus this reset
    length in place of both.
    """
    longest, rounded, _dt = _longest_window_dt(runtime, snapshot, controls)
    return rounded(longest["reset"])


def _longest_window_dt(
    runtime: Any, snapshot: Any, controls: list[int] | None
) -> tuple[dict[str, float], Callable[[float], int], float]:
    """Slowest measure and reset in dt over controls (every qubit when None), a granularity rounding and dt."""
    target = snapshot.backend.target
    granularity = max(1, int(target.granularity))
    longest = {}
    for name in ("measure", "reset"):
        table = target[name] if name in target.operation_names else {}
        sites = table.values() if controls is None else [table.get((qubit,)) for qubit in controls]
        durations = [
            float(properties.duration)
            for properties in sites
            if properties is not None and properties.duration is not None
        ]
        if (
            not durations
            or (controls is not None and len(durations) != len(controls))
            or target.dt is None
            or target.dt <= 0
        ):
            raise runtime.LiveRunError(f"the N=21 window arms need a calibrated {name} duration and dt")
        longest[name] = max(durations) / float(target.dt)

    def rounded(value: float) -> int:
        return granularity * math.ceil(value / granularity)

    return longest, rounded, float(target.dt)


def control_sites(runtime: Any, isas: list[Any]) -> list[tuple[tuple[str, int], ...]]:
    """Every measure and reset of each compiled window arm with its physical site, in instruction order.

    Only the QPE control is measured and reset after the initialization
    herald, whose measurements every qubit plays before the program and
    which the list leaves out. Routing can move the control between the
    rounds, so an arm's terminal readout can sit on another qubit than its
    mid-circuit measure and reset.
    """
    sites = []
    for isa in isas:
        program = isa.copy_empty_like()
        for instruction in isa.data:
            if not herald_measurement(isa, instruction):
                program.append(instruction)
        sites.append(tuple((name, qubits[0]) for name, qubits in runtime._ops(program) if name in ("measure", "reset")))
    return sites


def orbit_sites(sites: list[tuple[tuple[str, int], ...]], members: Any) -> list[tuple[tuple[str, int], ...]]:
    """The control_sites entries of the orbit arms, in member order.

    A spectator Ramsey arm of n21-orbit-rca reads qubit 2 at its end, and its
    reset_only reference resets the control before any measurement, so the
    window durations follow the orbit arms alone.
    """
    return [arm for arm, member in zip(sites, members, strict=True) if member.name.startswith("n21_orbit_")]


def ground_split(members: Any) -> bool:
    """Whether a group is the ground-control split, which holds spectator arms and no orbit arm."""
    names = [member.name for member in members]
    return not any(name.startswith("n21_orbit_") for name in names) and any(
        name.startswith("n21_spectator_idle_ground_") or n21_segmented_key(name) is not None for name in names
    )


def segmented_config_of(members: Any) -> dict[str, Any] | None:
    """The segmented ground sweep configuration a group's members carry, or None for any other group.

    Every member reads its segments into s<k>_read registers, so the
    segment count is the number of those registers.
    """
    keys = [(n21_segmented_key(member.name), member) for member in members]
    if not any(key is not None for key, _member in keys):
        return None
    if any(key is None for key, _member in keys):
        raise ValueError("a segmented sweep group holds members of another kind")
    counts = {sum(1 for register in member.circuit.cregs if register.name.endswith("_read")) for _key, member in keys}
    if len(counts) != 1:
        raise ValueError(f"segmented members read {sorted(counts)} segments; one count is planned")
    pres = {key[2] for key, _member in keys if key is not None and key[2]}
    if len(pres) > 1:
        raise ValueError(f"segmented backaction arms idle {sorted(pres)} dt; one pre-idle is planned")
    return {
        "delays_dt": sorted({key[1] for key, _member in keys if key is not None and not key[2]}),
        "segments": counts.pop(),
        "backaction_delays_dt": sorted({key[1] for key, _member in keys if key is not None and key[2]}),
        "backaction_pre_idle_dt": pres.pop() if pres else 0,
    }


def segmented_violations(sites: list[tuple[tuple[str, int], ...]], spectator: int) -> list[str]:
    """Reasons a segmented arm plays a mid-circuit measure or reset off the pinned spectator."""
    return [
        f"a segmented arm reads or resets qubits {sorted({qubit for _name, qubit in arm} - {spectator})}"
        for arm in sites
        if {qubit for _name, qubit in arm} != {spectator}
    ]


def ramsey_windows_of(members: Any) -> tuple[int, ...]:
    """The ground Ramsey sweep's idle multiples a group's member names carry; () for any other group."""
    found = (n21_ramsey_multiple(member.name) for member in members)
    return tuple(sorted({key[0] for key in found if key is not None}))


def n21_replica_tiers(args: Any) -> list[int]:
    """The replica tiers an N=21 family plans.

    The orbit-rca window analysis reads one replica's schedule and wires, so its window variants plan one. A
    window-dose sweep's doses are fixed dt values that no control's calibration sizes, and its replay and decisions
    read every replica, so it packs as many replicas as the tiers admit.
    """
    tiers = list(args.replica_tiers) if args.optimize else [args.max_replicas or 1]
    if args.family == "n21-orbit-rca" and not getattr(args, "window_doses_dt", None):
        tiers = [1]
    if args.max_replicas is not None:
        tiers = [tier for tier in tiers if tier <= args.max_replicas]
    return tiers


def window_doses_of(members: Any) -> tuple[int, ...]:
    """The window-dose sweep's doses in dt that a group's member names carry; () for any other group."""
    found = (n21_dose_key(member.name) for member in members)
    return tuple(sorted({key[1] for key in found if key is not None}))


def detuning_sign_of(members: Any) -> bool:
    """Whether a group is the detuning-sign test, which alone holds work Ramsey arms."""
    return any(n21_work_ramsey_key(member.name) is not None for member in members)


# A quarter-sized turn keeps every probed phase response inside (-pi, pi).
DOSE_ROLE_PROBE_RAD = 0.4


def _turned(isa: Any, physical: int | None, angle: float) -> Any:
    """isa reduced to its active qubits, with a Z turn of angle spread over physical's delays by duration."""
    from qiskit import QuantumCircuit

    def wires(instruction: Any) -> list[int]:
        return [isa.find_bit(qubit).index for qubit in instruction.qubits]

    active = sorted({q for inner in isa.data if inner.operation.name != "barrier" for q in wires(inner)})
    index = {q: k for k, q in enumerate(active)}
    held = sum(
        int(inner.operation.duration)
        for inner in isa.data
        if inner.operation.name == "delay" and physical in wires(inner)
    )
    out = QuantumCircuit(len(active))
    for register in isa.cregs:
        out.add_register(register)
    for inner in isa.data:
        qubits = wires(inner)
        if inner.operation.name == "barrier":
            kept = [index[q] for q in qubits if q in index]
            if kept:
                out.barrier(*kept)
        elif inner.operation.name == "delay":
            if physical in qubits and held:
                out.rz(angle * int(inner.operation.duration) / held, index[physical])
        else:
            out.append(inner.operation, [index[q] for q in qubits], inner.clbits)
    return out


def _probe_marginal(circuit: Any) -> np.ndarray:
    """The exact phase-register marginal of one reduced probe circuit."""
    from qiskit_aer.noise import NoiseModel

    import dynamic_density

    return phase_marginal(dynamic_density.probabilities(circuit, NoiseModel()))


def _orbit_read(marginal: np.ndarray) -> float:
    return float(
        (marginal[0] - marginal[2]) / (marginal[0] + marginal[2])
        - (marginal[1] - marginal[3]) / (marginal[1] + marginal[3])
    )


def _ramsey_read(marginal: np.ndarray) -> float:
    return float(marginal[0] - marginal[2])


def _responses(layout: list[int], pairs: list[tuple[Any, Any]], read: Callable[[np.ndarray], float]) -> list[list[int]]:
    """Per (cosine, sine) pair of compiled members, each logical qubit's phase response, in units of the probe turn on
    its initial physical qubit: -1, 0 or 1.

    Every probe circuit is independent, so the whole batch evaluates in one
    pooled map, and each pair's phase is atan2 of its sine and cosine reads.
    """
    turns: tuple[int | None, ...] = (None, *layout)
    circuits = [_turned(isa, physical, DOSE_ROLE_PROBE_RAD) for pair in pairs for physical in turns for isa in pair]
    reads = [read(marginal) for marginal in parallel.ordered_map(_probe_marginal, circuits, min_items=2)]
    out = []
    for k in range(len(pairs)):
        row = reads[2 * len(turns) * k : 2 * len(turns) * (k + 1)]
        base, *phases = (math.atan2(row[2 * j + 1], row[2 * j]) for j in range(len(turns)))
        signs = []
        for physical, phase in zip(layout, phases, strict=True):
            turn = math.remainder(phase - base, 2 * math.pi) / DOSE_ROLE_PROBE_RAD
            if abs(turn - round(turn)) > 0.05 or round(turn) not in (-1, 0, 1):
                raise ValueError(f"the probe turn on qubit {physical} moves the phase by {turn:.3f} turns")
            signs.append(round(turn))
        out.append(signs)
    return out


def dose_roles(choice: Any) -> dict[str, int]:
    """The logical index whose initial qubit holds each work role during the dose of a compiled detuning-sign plan.

    Routing the orbit's controlled swaps moves the work roles, so the roles
    come from the compiled arms: a Z turn of one initial physical qubit
    during the dose turns the orbit's quadrature pair by plus the turn on the
    qubit that holds the work bit for 16, by minus it on the qubit for 1,
    and leaves it on every other qubit (tests/gororoba_quantum/
    test_detuning_sign.py), evaluated exactly at every nonzero dose. Every
    dose must give the same roles.
    """
    isas = {member.name: isa for member, isa in zip(choice.group.members, choice.isas, strict=True)}
    layout = list(choice.layout)
    pairs = [
        (isas[n21_dose_name("window_dose", dose, False)], isas[n21_dose_name("window_dose_y", dose, False)])
        for dose in window_doses_of(choice.group.members)[1:]
    ]
    found = {tuple(signs) for signs in _responses(layout, pairs, _orbit_read)}
    if len(found) != 1:
        raise ValueError(f"the orbit arms hold the work roles on different qubits across doses: {sorted(found)}")
    (signs,) = found
    if sorted(signs) != [-1, 0, 0, 1]:
        raise ValueError(f"the orbit's dose responds to the initial qubits {layout} as {list(signs)}")
    return {"one": signs.index(-1), "sixteen": signs.index(1)}


def detuning_roles_choice(runtime: Any, candidate: Any, windows: dict[str, Any]) -> tuple[Any, dict[str, Any]]:
    """Rebuild a routed detuning-sign candidate with its Ramsey arms on the dose-time work qubits.

    The orbit arms keep their compiled circuits; only the Ramsey arms
    compile again, and each must turn with its own role's qubit alone.
    """
    roles = dose_roles(candidate)
    group = n21_orbit_rca_group(
        windows["window_delay_dt"],
        windows["echo_half_dt"],
        True,
        window_doses=window_doses_of(candidate.group.members),
        detuning_sign=True,
        dose_roles=roles,
    )
    previous = {member.name: isa for member, isa in zip(candidate.group.members, candidate.isas, strict=True)}
    if [member.name for member in group.members] != list(previous):
        raise runtime.LiveRunError("the dose-role rebuild changed the detuning-sign members")
    snapshot = candidate.snap
    if snapshot.admission_target is None:
        snapshot.admission_target = runtime.build_admission_target(snapshot)
    get_plugin = getattr(snapshot.backend, "get_translation_stage_plugin", None)
    compiler = MemberCompiler(snapshot.admission_target, candidate.seed, get_plugin() if get_plugin else None)
    # The Ramsey arms are independent compilations; ordered_map returns them in member order.
    ramsey = [member for member in group.members if n21_work_ramsey_key(member.name) is not None]
    fresh = iter(
        parallel.ordered_map(compiler, [(member.circuit, list(candidate.layout)) for member in ramsey], min_items=2)
    )
    isas = [
        next(fresh) if n21_work_ramsey_key(member.name) is not None else previous[member.name]
        for member in group.members
    ]
    compiled = {member.name: isa for member, isa in zip(group.members, isas, strict=True)}
    arms = [
        (member.name, key[0])
        for member in group.members
        if (key := n21_work_ramsey_key(member.name)) is not None and key[1] == "x" and key[2]
    ]
    pairs = [(compiled[name], compiled[name.replace("_x_d", "_y_d")]) for name, _ in arms]
    for (name, role), signs in zip(arms, _responses(list(candidate.layout), pairs, _ramsey_read), strict=True):
        if signs != [1 if logical == roles[role] else 0 for logical in range(len(candidate.layout))]:
            raise runtime.LiveRunError(f"{name} does not turn with the dose-time qubit of {role}")
    violations = [reason for isa in isas for reason in runtime.compiled_violations(isa, candidate.snap)]
    if violations:
        raise runtime.LiveRunError(str(violations))
    scores = [runtime.layout_score(isa, candidate.snap.backend.target) for isa in isas]
    if any(score <= 0 for score in scores):
        raise runtime.LiveRunError(f"{group.name}: layout score underflows to zero on layout {candidate.layout}")
    joint = math.exp(sum(math.log(score) for score in scores) / len(scores))
    rebuilt = runtime.Choice(group, candidate.snap, candidate.seed, candidate.layout, isas, scores, joint)
    return rebuilt, windows | {"dose_roles": roles}


def window_dose_timing_violations(runtime: Any, snapshot: Any, doses: tuple[int, ...]) -> None:
    """Raise unless every dose, and every echo quarter of it, plays as a Target delay."""
    target = snapshot.backend.target
    reasons = n21_dose_violations(doses, max(1, int(target.granularity)), max(1, int(target.min_length)))
    if reasons:
        raise runtime.LiveRunError(f"{snapshot.name}: " + "; ".join(reasons))


def spectator_controls(sites: list[tuple[tuple[str, int], ...]]) -> list[int]:
    """Physical qubits of the control's resets in the ground-control split's arms.

    Each immediate, idle and idle_ground arm resets the control once, after
    qubit 2's readout, so the reset sites name the control whose measure and
    reset durations size the idle.
    """
    controls: set[int] = set()
    for arm in sites:
        resets = [qubit for name, qubit in arm if name == "reset"]
        if len(resets) != 1:
            raise ValueError(f"a ground-control spectator arm lacks its single control reset: {arm}")
        controls.update(resets)
    return sorted(controls)


def candidate_controls(sites: list[tuple[tuple[str, int], ...]], members: Any) -> list[int]:
    """The control qubits that size a candidate's windows: the orbit window, or the spectator resets."""
    if ground_split(members):
        return spectator_controls(sites)
    return window_controls(orbit_sites(sites, members))


def window_controls(sites: list[tuple[tuple[str, int], ...]]) -> list[int]:
    """Physical qubits of the mid-circuit round: each arm's measures through its first reset.

    The window spans the round-1 readout and the reset that follows it, so
    the terminal readout's site stays out of the window durations.
    """
    window: set[int] = set()
    for arm in sites:
        names = [name for name, _ in arm]
        if "reset" not in names or names.index("reset") == 0:
            raise ValueError(f"a window arm lacks its mid-circuit measure and reset: {arm}")
        window.update(qubit for _, qubit in arm[: names.index("reset") + 1])
    return sorted(window)


def _control_windows(
    runtime: Any, candidate: Any, bound: tuple[int, int, float], reset_bound: int | None = None
) -> tuple[Any, dict[str, Any]]:
    """Resize one routed window candidate to its control's own measure and reset durations.

    The candidate was routed with the backend-wide bound. The windows come
    from the sites of the mid-circuit measure and reset. When they give the
    same windows, the routed candidate stands; otherwise every arm rebuilds
    with them and recompiles on the same seed and initial layout, and each
    recompiled arm must keep its ordered measure and reset sites.
    reset_bound, the backend-wide reset length of an overlap split
    (reset_window_dt), resizes to the control's own reset with the windows
    and enters them as reset_dt. A ground-control split reads its control
    from the spectator arms' resets (candidate_controls).
    """
    sites = control_sites(runtime, candidate.isas)
    ground = ground_split(candidate.group.members)
    ramsey = ramsey_windows_of(candidate.group.members)
    segmented = segmented_config_of(candidate.group.members)
    doses = window_doses_of(candidate.group.members)
    # A segmented arm never measures or resets the control after its
    # herald; the control is logical qubit 0's initial physical qubit.
    controls = (
        [candidate.isas[0].layout.initial_index_layout(filter_ancillas=True)[0]]
        if segmented is not None
        else candidate_controls(sites, candidate.group.members)
    )
    window_dt, half_dt, dt = window_durations(runtime, candidate.snap, controls)
    windows: dict[str, Any] = {"window_delay_dt": window_dt, "echo_half_dt": half_dt, "dt_seconds": dt}
    split = reset_bound is not None
    reset_dt = reset_window_dt(runtime, candidate.snap, controls) if split else None
    if split:
        windows["reset_dt"] = reset_dt
    if (window_dt, half_dt) == bound[:2] and reset_dt == reset_bound:
        return candidate, windows
    group = n21_orbit_rca_group(
        window_dt,
        half_dt,
        has_herald(candidate.group.members[0].circuit),
        not split and not doses and any(member.name.startswith("n21_spectator_") for member in candidate.group.members),
        overlap_split=split and not ground,
        reset_dt=reset_dt,
        ground_control_split=ground,
        ramsey_windows=ramsey,
        segmented=segmented,
        window_doses=doses,
        detuning_sign=detuning_sign_of(candidate.group.members),
    )
    isas = [
        runtime._compile(member.circuit, candidate.snap, candidate.seed, candidate.layout) for member in group.members
    ]
    violations = [reason for isa in isas for reason in runtime.compiled_violations(isa, candidate.snap)]
    if violations:
        raise runtime.LiveRunError(str(violations))
    moved = control_sites(runtime, isas)
    if moved != sites:
        raise runtime.LiveRunError(f"resized window arms moved the control from {sites} to {moved}")
    scores = [runtime.layout_score(isa, candidate.snap.backend.target) for isa in isas]
    if any(score <= 0 for score in scores):
        raise runtime.LiveRunError(f"{group.name}: layout score underflows to zero on layout {candidate.layout}")
    joint = math.exp(sum(math.log(score) for score in scores) / len(scores))
    resized = runtime.Choice(group, candidate.snap, candidate.seed, candidate.layout, isas, scores, joint)
    return resized, windows


def orbit_gate_counts(choice: Any) -> dict[str, dict[str, int]]:
    """CZ and sx counts of each routed orbit arm, a descriptive record of what removing the barriers changes.

    Without the window barriers the transpiler resynthesizes the two-qubit
    block around the window, so an unbracketed arm can differ from its
    bracketed twin in CZ count as well as in readout overlap.
    """
    return {
        member.name: {gate: int(isa.count_ops().get(gate, 0)) for gate in ("cz", "sx")}
        for member, isa in zip(choice.group.members, choice.isas, strict=True)
        if member.name.startswith("n21_orbit_")
    }


def pinned_orbit_layout(runtime: Any, snapshot: Any, pin: dict[str, Any]) -> list[int]:
    """The physical qubit of each n21-orbit-rca logical qubit on snapshot under --pin-layout.

    A pin names one backend and the qubits of the group's logical order, so
    another backend, a qubit outside the device or one the fresh calibration
    excludes refuses the snapshot rather than moving a role.
    """
    qubits = [int(qubit) for qubit in pin["qubits"]]
    if snapshot.name != pin["backend"]:
        raise runtime.LiveRunError(f"the pinned layout names {pin['backend']} qubits")
    outside = [qubit for qubit in qubits if qubit >= snapshot.backend.target.num_qubits]
    excluded = sorted(set(qubits) & set(snapshot.excluded_qubits))
    if outside or excluded:
        raise runtime.LiveRunError(f"pinned qubits {outside} lie outside the device; calibration excludes {excluded}")
    return qubits


def pinned_roles_violations(runtime: Any, choice: Any, layout: list[int]) -> list[str]:
    """Reasons a routed pinned candidate moves a role off its pinned qubit.

    Every arm must start logical qubit i on layout[i], touch no other
    qubit, and play the orbit window's measure and reset on the pinned
    control. Routing swaps among the work qubits stay part of the compiled
    program, which the QPY bytes and the approval bind.
    """
    reasons = []
    for member, isa in zip(choice.group.members, choice.isas, strict=True):
        initial = isa.layout.initial_index_layout(filter_ancillas=True)[: len(layout)]
        if initial != layout:
            reasons.append(f"{member.name}: the arm starts on {initial}, not the pinned layout {layout}")
        if outside := sorted(set(runtime._physical(isa)) - set(layout)):
            reasons.append(f"{member.name}: routing leaves the pinned layout through qubits {outside}")
    if segmented_config_of(choice.group.members) is not None:
        return reasons + segmented_violations(control_sites(runtime, choice.isas), layout[2])
    controls = candidate_controls(control_sites(runtime, choice.isas), choice.group.members)
    if controls != [layout[0]]:
        reasons.append(f"the orbit window plays on {controls}, not the pinned control {layout[0]}")
    return reasons


def control_timing_dt(target: Any, control: int) -> tuple[float, float]:
    """Measure and reset durations of one physical qubit in units of the Target's dt."""
    durations = []
    for operation in ("measure", "reset"):
        properties = target[operation].get((control,)) if operation in target.operation_names else None
        duration = getattr(properties, "duration", None)
        if not target.dt or not duration or duration <= 0:
            raise ValueError(f"no Target {operation} duration or dt for control {control}")
        durations.append(float(duration) / float(target.dt))
    return durations[0], durations[1]


def coherence_readout_qubits(isas: list[Any]) -> dict[str, int]:
    """Physical qubit read into each coherence clbit, identical across every compiled circuit.

    Routing may move the logical work qubits during the round-1 prefix, so the
    pinned roles name the initial layout only. No two-qubit gate follows the
    prefix's closing barrier, so the qubit measured into a work clbit is the
    one that held that logical qubit through the window.
    """
    from coherence_window import B0, READ_A, READ_B, SECTOR

    labels = {B0: "b0", READ_A: "read_a", READ_B: "read_b", SECTOR: "sector"}
    found: dict[str, int] | None = None
    for isa in isas:
        barrier = next(i for i, inst in enumerate(isa.data) if inst.operation.name == "barrier")
        if any(inst.operation.num_qubits > 1 and inst.operation.name != "barrier" for inst in isa.data[barrier:]):
            raise ValueError(f"{isa.name}: a two-qubit gate follows the round-1 prefix")
        reads: dict[str, set[int]] = {}
        for inst in isa.data:
            if inst.operation.name == "measure":
                clbit = isa.find_bit(inst.clbits[0]).index
                reads.setdefault(labels[clbit], set()).add(isa.find_bit(inst.qubits[0]).index)
        if set(reads) != set(labels.values()) or any(len(qubits) != 1 for qubits in reads.values()):
            raise ValueError(f"{isa.name}: each coherence clbit must be read from one physical qubit")
        mapping = {label: next(iter(qubits)) for label, qubits in reads.items()}
        if found is not None and mapping != found:
            raise ValueError(f"{isa.name}: readout qubits {mapping} differ from {found}")
        found = mapping
    if found is None:
        raise ValueError("no compiled coherence circuit")
    return found


# Patch embeddings compiled in full per backend after the prefilter, and the
# declared idle over which the prefilter charges each qubit's T2 decay: the
# window the families place between the round and the readout is a control
# measure plus reset, about 4 to 5 us on Heron r2.
PATCH_PREFILTER = 16
PATCH_PREFILTER_IDLE_S = 5e-6


def patch_layouts(snapshot: Any, limit: int) -> tuple[list[tuple[list[int], float]], int]:
    """Patch embeddings on one backend's admitted CZ graph, best error product first.

    Every injective map of PATCH_ROLES onto physical qubits that carries each
    PATCH_EDGES pair onto a CZ coupler (rustworkx VF2, non-induced) is a
    candidate, excluding qubits and couplers the calibration excludes. The
    prefilter is the product of (1 - measure error), (1 - sx error) and
    exp(-PATCH_PREFILTER_IDLE_S / T2) over the six qubits and (1 - cz error)
    over the five couplers; a qubit without a positive T2 scores zero. Ties
    break on the layout tuple, so one calibration always yields the same
    ordered list. The second value is the number of embeddings found.
    """
    import rustworkx as rx

    from patch_characterization import PATCH_EDGES, PATCH_ROLES

    target = snapshot.backend.target
    if "cz" not in target.operation_names:
        return [], 0
    excluded = set(snapshot.excluded_qubits)
    blocked = {tuple(sorted(edge)) for edge in snapshot.excluded_edges}
    couplers = {
        tuple(sorted(pair)) for pair in target["cz"] if not set(pair) & excluded and tuple(sorted(pair)) not in blocked
    }
    graph = rx.PyGraph()
    nodes = graph.add_nodes_from(range(target.num_qubits))
    graph.add_edges_from_no_data([(nodes[a], nodes[b]) for a, b in sorted(couplers)])
    pattern = rx.PyGraph()
    pattern.add_nodes_from(range(len(PATCH_ROLES)))
    pattern.add_edges_from_no_data(list(PATCH_EDGES))

    def error(operation: str, qargs: tuple[int, ...]) -> float:
        properties = target[operation].get(qargs) or target[operation].get(qargs[::-1])
        value = getattr(properties, "error", None)
        return float(value) if value is not None else 1.0

    def decay(qubit: int) -> float:
        properties = target.qubit_properties[qubit] if target.qubit_properties else None
        t2 = getattr(properties, "t2", None)
        return math.exp(-PATCH_PREFILTER_IDLE_S / float(t2)) if t2 is not None and t2 > 0 else 0.0

    scored = []
    for mapping in rx.vf2_mapping(graph, pattern, subgraph=True, induced=False, id_order=True):
        layout = [0] * len(PATCH_ROLES)
        for physical, role in mapping.items():
            layout[role] = int(physical)
        product = math.prod((1.0 - error("measure", (q,))) * (1.0 - error("sx", (q,))) * decay(q) for q in layout)
        product *= math.prod(1.0 - error("cz", (layout[a], layout[b])) for a, b in PATCH_EDGES)
        scored.append((-product, tuple(layout)))
    scored.sort()
    return [(list(layout), -negative) for negative, layout in scored[:limit]], len(scored)


def _patch_candidate(
    runtime: Any, snapshot: Any, layout: list[int], args: Any, delays: list[int]
) -> tuple[list[Any], dict[str, Any]]:
    """Compile the characterization groups on one patch of one snapshot, or raise why it is refused."""
    from coherence_window import coherence_groups
    from patch_characterization import PATCH_EDGES, PATCH_ROLES, patch_groups

    excluded = sorted(set(layout) & set(snapshot.excluded_qubits))
    edges = [(layout[a], layout[b]) for a, b in PATCH_EDGES]
    blocked = [edge for edge in edges if edge in snapshot.excluded_edges or edge[::-1] in snapshot.excluded_edges]
    if excluded or blocked:
        raise runtime.LiveRunError(f"calibration excludes patch qubits {excluded} or couplers {blocked}")
    # Exchange circuits use no two-qubit gate, so the declared couplers
    # must exist in the Target for neighbors to be physical neighbors.
    couplers = set(snapshot.backend.target["cz"]) if "cz" in snapshot.backend.target.operation_names else set()
    missing = [edge for edge in edges if edge not in couplers and edge[::-1] not in couplers]
    if missing:
        raise runtime.LiveRunError(f"the backend has no coupler for patch edges {missing}")
    # The reset-only reference and echo halves follow the patch control's own
    # measure and reset durations.
    target = snapshot.backend.target
    granularity = max(1, int(target.granularity))
    try:
        control_measure, control_reset = control_timing_dt(target, layout[0])
    except ValueError as error:
        raise runtime.LiveRunError(str(error)) from error
    measure_dt = granularity * math.ceil(control_measure / granularity)
    half_dt = granularity * math.ceil(0.6 * (control_measure + control_reset) / granularity)
    # The matched idle spans the control's measure and reset, the window
    # the measure_reset context places between the round and the readout.
    window_dt = granularity * math.ceil((control_measure + control_reset) / granularity)
    dt = float(target.dt)
    choices = []
    groups = (
        coherence_groups(window_dt) if args.family == "coherence-window" else patch_groups(delays, measure_dt, half_dt)
    )
    for group in groups:
        isas = [runtime._compile(member.circuit, snapshot, runtime.SEED_TRANSPILER, layout) for member in group.members]
        violations = [reason for isa in isas for reason in runtime.compiled_violations(isa, snapshot)]
        if violations:
            raise runtime.LiveRunError(str(violations))
        scores = [runtime.layout_score(isa, snapshot.backend.target) for isa in isas]
        if any(score <= 0 for score in scores):
            raise runtime.LiveRunError(f"{group.name}: layout score underflows to zero on patch {layout}")
        choices.append(
            runtime.Choice(
                group,
                snapshot,
                runtime.SEED_TRANSPILER,
                layout,
                isas,
                scores,
                math.exp(sum(math.log(score) for score in scores) / len(scores)),
            )
        )
    used = sorted({qubit for choice in choices for isa in choice.isas for qubit in runtime._physical(isa)})
    if set(used) - set(layout):
        raise runtime.LiveRunError(f"routing left the patch through qubits {sorted(set(used) - set(layout))}")
    readout: dict[str, int] = {}
    if args.family == "coherence-window":
        readout = coherence_readout_qubits([isa for choice in choices for isa in choice.isas])
    # The patch is reserved whole: an idle neighbor stays mapped so the
    # replica, the case and the collector name the same six qubits.
    pinned = sorted(set(used) | set(layout))
    replica = Replica(0, {qubit: qubit for qubit in pinned}, min(min(choice.member_scores) for choice in choices))
    for choice in choices:
        runtime._set_entries(choice, [replica], runtime.ReplicaPolicy(args.replica_floor, 1, False, True))
    runtime.execution_pubs(choices)
    timing: dict[str, Any] = (
        {
            "window_dt": window_dt,
            "control_measure_dt": round(control_measure),
            "control_reset_dt": round(control_reset),
            "readout_qubits": readout,
        }
        if args.family == "coherence-window"
        else {"delays_dt": delays, "measure_dt": measure_dt, "echo_half_dt": half_dt}
    )
    return choices, {
        "name": args.family,
        "patch_qubits": layout,
        "patch_roles": list(PATCH_ROLES),
        **timing,
        "dt_seconds": dt,
        "placement_contract": "one pinned patch; static and dynamic jobs",
    }


def patch_candidates(
    runtime: Any, snapshots: list[Any], args: Any, trace: dict[str, Any]
) -> list[tuple[list[Any], dict[str, Any]]]:
    """Compile the characterization groups on a declared patch, or on the best calibrated patches of every backend.

    With --patch-qubits the patch is fixed, so a snapshot whose fresh
    calibration excludes a patch qubit or exercised coupler is refused rather
    than re-placed. Without it, each eligible snapshot contributes its
    PATCH_PREFILTER best embeddings (patch_layouts); every compiled patch is
    ranked by its joint score, fewer pending jobs breaking ties, and the
    best --optimizer-candidates go to admission. The trace keeps every scored
    and refused patch, so a dry run and a submit on one calibration choose the
    same patch.
    """
    from patch_characterization import PATCH_DELAYS_DT, PATCH_ROLES

    delays = list(PATCH_DELAYS_DT)
    declared = args.patch_qubits is not None
    if declared:
        fixed = [int(qubit) for qubit in args.patch_qubits]
        if len(fixed) != len(PATCH_ROLES) or len(set(fixed)) != len(fixed):
            raise runtime.LiveRunError(f"--patch-qubits names {len(PATCH_ROLES)} distinct qubits: {PATCH_ROLES}")
    scored: list[tuple[float, int, list[Any], dict[str, Any]]] = []
    search = trace.setdefault("patch_search", [])
    prefilter_trace = trace.setdefault("patch_prefilter", {})
    for snapshot in snapshots:
        if declared:
            layouts: list[tuple[list[int], float | None]] = [(fixed, None)]
        else:
            ranked, found = patch_layouts(snapshot, PATCH_PREFILTER)
            layouts = [(layout, score) for layout, score in ranked]
            prefilter_trace[snapshot.name] = {
                "embeddings": found,
                "compiled": len(ranked),
                "cutoff_prefilter": ranked[-1][1] if ranked else None,
            }
        for layout, prefilter in layouts:
            try:
                choices, configuration = _patch_candidate(runtime, snapshot, layout, args, delays)
            except (runtime.LiveRunError, QiskitError, ValueError) as error:
                trace.setdefault("family_rejections", []).append(
                    {"backend": snapshot.name, "patch_qubits": layout, "reason": str(error)}
                )
                continue
            joint = math.exp(sum(math.log(choice.joint_score) for choice in choices) / len(choices))
            configuration["patch_selection"] = "declared" if declared else "calibration"
            search.append(
                {"backend": snapshot.name, "patch_qubits": layout, "prefilter": prefilter, "joint_score": joint}
            )
            scored.append((joint, -snapshot.pending_jobs, choices, configuration))
    if declared:
        return [(choices, configuration) for _, _, choices, configuration in scored]
    scored.sort(key=lambda item: (item[0], item[1], [-q for q in item[3]["patch_qubits"]]), reverse=True)
    return [(choices, configuration) for _, _, choices, configuration in scored[: args.optimizer_candidates]]


def state_prep_layout(args: Any) -> tuple[list[int], dict[str, Any]]:
    """The named qubits of state-prep-control and where they come from.

    --layout names them; otherwise they are the replica qubits of the
    retained n21-feedback-encoded dry run STATE_PREP_SOURCE_RECORD, which
    belong to that record's backend.
    """
    declared = getattr(args, "layout", None)
    if declared is not None:
        qubits = [int(qubit) for qubit in declared]
        source: dict[str, Any] = {"layout_source": "declared"}
    else:
        record = json.loads((Path(__file__).resolve().parent.parent / STATE_PREP_SOURCE_RECORD).read_text())
        replicas = [
            sorted(int(qubit) for qubit in replica["physical_qubits"])
            for group in record["groups"]
            for replica in group["replicas"]
        ]
        qubits = sorted(qubit for replica in replicas for qubit in replica)
        source = {
            "layout_source": STATE_PREP_SOURCE_RECORD,
            "layout_backend": record["groups"][0]["backend"],
            "source_replicas": replicas,
        }
    if not qubits or len(set(qubits)) != len(qubits) or any(qubit < 0 for qubit in qubits):
        raise ValueError(f"state-prep-control needs distinct nonnegative qubits, got {qubits}")
    return qubits, source


def state_prep_candidates(
    runtime: Any, snapshots: list[Any], args: Any, trace: dict[str, Any]
) -> list[tuple[list[Any], dict[str, Any]]]:
    """Compile every arm on its named qubit of each eligible snapshot, or record why the snapshot is refused.

    Each qubit's arms compile with initial layout [qubit] and stay there: a
    calibration that excludes a named qubit refuses the snapshot rather than
    moving the control off the qubits it characterizes.
    """
    try:
        qubits, source = state_prep_layout(args)
    except (OSError, KeyError, ValueError) as error:
        raise runtime.LiveRunError(f"state-prep-control layout: {error}") from error
    try:
        arms = state_prep_arms(getattr(args, "state_prep_arms", None))
    except ValueError as error:
        raise runtime.LiveRunError(f"state-prep-control arms: {error}") from error
    groups = state_prep_groups(qubits, arms)
    dynamic_arms = [arm for arm in arms if arm in STATE_PREP_DYNAMIC_ARMS]
    expected_kinds = sorted(["static"] * (len(arms) - len(dynamic_arms)) + ["dynamic"] * len(dynamic_arms))
    candidates = []
    for snapshot in snapshots:
        try:
            if "layout_backend" in source and snapshot.name != source["layout_backend"]:
                raise runtime.LiveRunError(f"the layout names {source['layout_backend']} qubits")
            outside = [qubit for qubit in qubits if qubit >= snapshot.backend.target.num_qubits]
            excluded = sorted(set(qubits) & set(snapshot.excluded_qubits))
            if outside or excluded:
                raise runtime.LiveRunError(f"qubits {outside} lie outside the device; calibration excludes {excluded}")
            choices = []
            for group in groups:
                qubit = int(group.name.rsplit("_q", 1)[1])
                isas = [
                    runtime._compile(member.circuit, snapshot, runtime.SEED_TRANSPILER, [qubit])
                    for member in group.members
                ]
                for isa in isas:
                    if runtime._physical(isa) != [qubit]:
                        raise runtime.LiveRunError(f"{group.name}: compiled onto {runtime._physical(isa)}")
                    violations = runtime.compiled_violations(isa, snapshot)
                    if violations:
                        raise runtime.LiveRunError(f"{group.name}: {violations}")
                scores = [runtime.layout_score(isa, snapshot.backend.target) for isa in isas]
                if any(score <= 0 for score in scores):
                    raise runtime.LiveRunError(f"{group.name}: layout score underflows to zero")
                choice = runtime.Choice(
                    group,
                    snapshot,
                    runtime.SEED_TRANSPILER,
                    [qubit],
                    isas,
                    scores,
                    math.exp(sum(math.log(score) for score in scores) / len(scores)),
                )
                runtime._set_entries(
                    choice,
                    [Replica(0, {qubit: qubit}, min(scores))],
                    runtime.ReplicaPolicy(args.replica_floor, 1, False, True),
                )
                choices.append(choice)
            pubs = runtime.execution_pubs(choices)
            kinds = sorted(pub.kind for pub in pubs)
            if kinds != expected_kinds:
                raise runtime.LiveRunError(f"the arms {list(arms)} fused into PUB kinds {kinds}, not {expected_kinds}")
        except (runtime.LiveRunError, QiskitError, ValueError) as error:
            trace.setdefault("family_rejections", []).append(
                {"backend": snapshot.name, "qubits": qubits, "reason": str(error)}
            )
            continue
        candidates.append(
            (
                choices,
                {
                    "name": STATE_PREP_FAMILY,
                    "qubits": qubits,
                    **source,
                    "arms": {arm: STATE_PREP_ARM_STEPS[arm] for arm in arms},
                    "placement_contract": (
                        "one pinned single-qubit placement per named qubit; every qubit runs each arm in the "
                        + (
                            "same shots; one dynamic x_history PUB, alone in its job"
                            if arms == (STATE_PREP_HISTORY_ARM,)
                            else "same shots; static "
                            + " and ".join(arm for arm in arms if arm not in dynamic_arms)
                            + " PUBs in that row order"
                            + (", dynamic " + " and ".join(dynamic_arms) + " PUBs" if dynamic_arms else "")
                        )
                    ),
                    "dt_seconds": snapshot.backend.target.dt,
                },
            )
        )
    return candidates[: args.optimizer_candidates]


def latency_recovery_candidates(
    runtime: Any, snapshots: list[Any], args: Any, trace: dict[str, Any]
) -> list[tuple[list[Any], dict[str, Any]]]:
    """Route the 34-member latency-recovery group on each snapshot, one placement per candidate.

    Delays are multiples of the backend's timing granularity, so L and W
    (--latency-dt and --window-dt, else the ibm_kingston design values) round
    up to it; the configuration records requested and effective values, and
    record_groups rebuilds the group from the effective ones. A routed
    candidate whose syndrome window holds an operation besides the two
    ancilla measurements is rejected. The analysis reads one replica's
    schedule, so the replica count is 1.
    """
    requested = (
        getattr(args, "latency_dt", None) or DEFAULT_LATENCY_DT,
        getattr(args, "window_dt", None) or DEFAULT_WINDOW_DT,
    )
    candidates: list[tuple[list[Any], dict[str, Any]]] = []
    routed: list[tuple[Any, dict[str, Any]]] = []
    for snapshot in snapshots:
        local: dict[str, Any] = {}
        try:
            target = snapshot.backend.target
            granularity = max(1, int(target.granularity))
            latency_dt, window_dt = (granularity * math.ceil(value / granularity) for value in requested)
            group = latency_recovery_group(latency_dt, window_dt)
            placed = runtime.select_candidates(group, [snapshot], args.seeds, local)
        except (runtime.LiveRunError, QiskitError, ValueError) as error:
            trace.setdefault("family_rejections", []).append({"backend": snapshot.name, "reason": str(error)})
            continue
        trace.setdefault(group.name, {}).update(local.get(group.name, {}))
        configuration = {
            "name": LATENCY_RECOVERY_FAMILY,
            "latency_dt": latency_dt,
            "window_dt": window_dt,
            "requested_latency_dt": requested[0],
            "requested_window_dt": requested[1],
            "granularity_dt": granularity,
            "dt_seconds": target.dt,
        }
        for placement in placed:
            try:
                for isa in placement.isas:
                    if moved := syndrome_window_violations(isa):
                        raise runtime.LiveRunError(f"{isa.name}: operations inside the syndrome window: {moved}")
            except (runtime.LiveRunError, ValueError) as error:
                trace.setdefault("family_rejections", []).append(
                    {"backend": snapshot.name, "seed": placement.seed, "layout": placement.layout, "reason": str(error)}
                )
                continue
            routed.append((placement, configuration))
    if not routed:
        raise runtime.LiveRunError(f"no backend routes the latency-recovery family: {trace.get('family_rejections')}")
    routed.sort(key=lambda item: -item[0].joint_score)
    for placement, configuration in routed[: args.optimizer_candidates]:
        trial = copy.copy(placement)
        policy = runtime.ReplicaPolicy(args.replica_floor, 1, False, True)
        if runtime._prepare_individual_candidate(trial, trace, policy):
            candidates.append(([trial], {**configuration, "replica_cap": 1}))
    return candidates


def measurement_delay(runtime: Any, snapshot: Any, physical_qubit: int) -> int:
    """Round the actual measurement writer's fresh duration to timing granularity."""
    target = snapshot.backend.target
    duration = target["measure"][(physical_qubit,)].duration
    if duration is None or target.dt is None or duration <= 0 or target.dt <= 0:
        raise runtime.LiveRunError("the ladder needs a positive calibrated measurement duration and dt")
    granularity = max(1, int(target.granularity))
    return granularity * math.ceil(float(duration) / float(target.dt) / granularity)


def rounded_delay(runtime: Any, snapshot: Any, seconds: float) -> int:
    """seconds in dt, rounded up to the Target's timing granularity; zero stays zero."""
    target = snapshot.backend.target
    if target.dt is None or target.dt <= 0:
        raise runtime.LiveRunError("the measurement-sequence idles need a positive Target dt")
    granularity = max(1, int(target.granularity))
    return granularity * math.ceil(seconds / float(target.dt) / granularity)


def floored_delay(runtime: Any, snapshot: Any, seconds: float) -> int:
    """seconds in dt, rounded down to the Target's timing granularity: an idle that must not exceed `seconds`."""
    target = snapshot.backend.target
    if target.dt is None or target.dt <= 0:
        raise runtime.LiveRunError("the measurement-sequence idles need a positive Target dt")
    granularity = max(1, int(target.granularity))
    return granularity * math.floor(seconds / float(target.dt) / granularity)


def settle_delay(runtime: Any, snapshot: Any) -> int:
    """MSQ_SETTLE_SECONDS in dt, rounded up to the Target's timing granularity."""
    return rounded_delay(runtime, snapshot, MSQ_SETTLE_SECONDS)


def prereadout_delay(runtime: Any, snapshot: Any) -> int:
    """MSQ_PREREADOUT_SECONDS in dt, rounded up to the Target's timing granularity."""
    return rounded_delay(runtime, snapshot, MSQ_PREREADOUT_SECONDS)


class MemberCompiler:
    """Transpile one (circuit, initial layout) onto the admission Target, as live_run._compile does for that layout.

    The worker receives the Target, the seed and the backend's default translation stage plugin
    rather than the backend: a runtime backend holds its service session, which stays in the
    parent. transpile reads the backend for nothing else once a Target is given.
    """

    def __init__(self, target: Target, seed: int, translation_method: str | None) -> None:
        self.target = target
        self.seed = seed
        self.translation_method = translation_method

    def __call__(self, item: tuple[QuantumCircuit, list[int]]) -> QuantumCircuit:
        import live_run

        circuit, layout = item
        try:
            return transpile(
                circuit,
                target=self.target,
                optimization_level=live_run.OPT_LEVEL,
                seed_transpiler=self.seed,
                initial_layout=layout,
                translation_method=self.translation_method,
            )
        except BaseException as error:
            if type(error).__name__ != "PanicException":
                raise
            raise live_run.CompilePanic(f"{circuit.name}: transpiler panic ({error})") from None


def measurement_sequence_candidates(
    runtime: Any, snapshots: list[Any], args: Any, trace: dict[str, Any]
) -> list[tuple[list[Any], dict[str, Any]]]:
    """Compile every member on its named qubit of each eligible snapshot, or record why the snapshot is refused.

    --layout names the qubits, one pinned placement each. The delay arm idles
    each step for the qubit's calibrated measure duration (measurement_delay),
    so groups are built per snapshot and the configuration records the
    durations that record_groups rebuilds them from. A calibration that
    excludes a named qubit refuses the snapshot.
    """
    diagnostic = args.family == MSQD_FAMILY
    relaxation = args.family == MSQR_FAMILY
    envelope = args.family in (MSQE_FAMILY, MSQR_FAMILY)
    declared = getattr(args, "layout", None)
    if declared is None and not envelope:
        raise runtime.LiveRunError(f"{args.family} needs --layout: it has no retained default qubits")
    qubits = [int(qubit) for qubit in declared] if declared is not None else []
    if envelope:
        width = int(args.layout_width)
        # Every member holds a terminal reset, so every PUB is dynamic: the main family's rows, two reset controls
        # and the width tier's patterns, and for the relaxation family its readers, equilibrium row and sentinels.
        expected_kinds = ["dynamic"] * (
            msqr_row_count(width)
            if relaxation
            else 4 * len(MSQ_STEPS)
            + 4
            + 1
            + len(MSQ_T1_MICROSECONDS)
            + 4 * len(MSQ_DYNAMIC_STEPS)
            + 4
            + len(MSQE_RESET_CONTROLS)
            + len(msqe_pattern_bits(width))
        )
    elif diagnostic:
        # Four signed unitary members, ro0 and ro1, all static: six PUBs whatever the qubit count.
        expected_kinds = ["static"] * 6
    else:
        expected_kinds = sorted(
            ["static"] * (4 * len(MSQ_STEPS) + 4 + 1 + len(MSQ_T1_MICROSECONDS))
            + ["dynamic"] * (4 * len(MSQ_DYNAMIC_STEPS) + 4)
        )
    candidates = []
    equilibrium_dt = 0
    for snapshot in snapshots:
        try:
            if envelope:
                if snapshot.name != msq_envelope.ENVELOPE_BACKEND:
                    raise runtime.LiveRunError(f"the envelope runs on {msq_envelope.ENVELOPE_BACKEND} only")
                envelope_calibration = msq_envelope.calibration_from_snapshot(snapshot)
                qubits = msq_envelope.layout_rule(
                    envelope_calibration["qubits"],
                    envelope_calibration["excluded"],
                    [tuple(edge) for edge in envelope_calibration["edges"]],
                    width,
                )
            outside = [qubit for qubit in qubits if qubit < 0 or qubit >= snapshot.backend.target.num_qubits]
            excluded = sorted(set(qubits) & set(snapshot.excluded_qubits))
            if outside or excluded:
                raise runtime.LiveRunError(f"qubits {outside} lie outside the device; calibration excludes {excluded}")
            prereadouts = {qubit: prereadout_delay(runtime, snapshot) for qubit in qubits}
            if diagnostic:
                delays, settles, t1_delays = {}, {}, [0]
                calibration = measurement_sequence_scatter.calibration_from_snapshot(snapshot)
                faults = measurement_sequence_scatter.layout_violations(
                    qubits, calibration["edges"], set(calibration["excluded"])
                )
                if faults:
                    raise runtime.LiveRunError("; ".join(faults))
                groups = msq_diagnostic_groups(qubits, prereadouts)
            else:
                delays = {qubit: measurement_delay(runtime, snapshot, qubit) for qubit in qubits}
                settles = {qubit: settle_delay(runtime, snapshot) for qubit in qubits}
                t1_delays = [
                    rounded_delay(runtime, snapshot, microseconds * 1e-6) for microseconds in MSQ_T1_MICROSECONDS
                ]
                if relaxation:
                    equilibrium_dt = rounded_delay(runtime, snapshot, MSQR_EQUILIBRIUM_SECONDS)
                    reader_idle_dt = floored_delay(runtime, snapshot, MSQR_READER_IDLE_SECONDS)
                    groups = msqr_groups(
                        qubits, delays, settles, prereadouts, t1_delays, equilibrium_dt, reader_idle_dt
                    )
                else:
                    build = msqe_groups if envelope else measurement_sequence_groups
                    groups = build(qubits, delays, settles, prereadouts, t1_delays)
            if snapshot.admission_target is None:
                snapshot.admission_target = runtime.build_admission_target(snapshot)
            get_plugin = getattr(snapshot.backend, "get_translation_stage_plugin", None)
            compiler = MemberCompiler(
                snapshot.admission_target, runtime.SEED_TRANSPILER, get_plugin() if get_plugin else None
            )
            # The members are independent compilations; ordered_map returns them in member order.
            work = [
                (member.circuit, [int(group.name.rsplit("_q", 1)[1])]) for group in groups for member in group.members
            ]
            compiled = iter(parallel.ordered_map(compiler, work, min_items=2))
            choices = []
            for group in groups:
                qubit = int(group.name.rsplit("_q", 1)[1])
                isas = [next(compiled) for _ in group.members]
                for member, isa in zip(group.members, isas, strict=True):
                    if runtime._physical(isa) != [qubit]:
                        raise runtime.LiveRunError(f"{group.name}: compiled onto {runtime._physical(isa)}")
                    violations = runtime.compiled_violations(isa, snapshot)
                    if violations:
                        raise runtime.LiveRunError(f"{group.name}: {violations}")
                    operations = isa.count_ops()
                    arm = member.name.split("_")[1]
                    # The envelope's terminal resets, the reset controls' mid-circuit reset and a reader's reset before
                    # its idle survive compilation.
                    reader = relaxation and arm.startswith("reader")
                    two_resets = arm in MSQE_RESET_CONTROLS or reader
                    resets_expected = (2 if two_resets else 1) if envelope else 0
                    if operations.get("reset", 0) != resets_expected:
                        raise runtime.LiveRunError(
                            f"{member.name}: compiled {operations.get('reset', 0)} resets, not {resets_expected}"
                        )
                    if arm in MSQE_RESET_CONTROLS:
                        measures, delays_expected, steps = 2, 1, 0
                    elif reader:
                        # The repeated measure member (N mid-circuit and one final measurement, one pre-readout
                        # idle), then the reader idle and the reader measurement.
                        steps = msqr_reader_stem(int(arm.removeprefix("reader")))[0]
                        measures, delays_expected = steps + 2, 2
                    elif arm.startswith("pat") or arm == "ro0":
                        measures, delays_expected, steps = 1, 1, 0
                    elif relaxation and arm == "eq":
                        measures, delays_expected, steps = 1, 2, 0
                    elif relaxation and arm.startswith("sent"):
                        # A sentinel is a delay-arm row: one idle per step and the pre-readout idle.
                        steps = MSQR_SENTINEL_ROWS[int(arm.removeprefix("sent")[1:])][0]
                        measures, delays_expected = 1, 1 + steps
                    elif arm == "t1":
                        index = int(member.name.split("_d")[1].split("_")[0])
                        measures, delays_expected = 1, 1 + int(t1_delays[index] > 0)
                        steps = 0
                    else:
                        steps = int(member.name.split("_n")[1].split("_")[0])
                        measures = {"measure": steps + 1, "delay": 1, "unitary": 1, "settle": steps + 1}[arm]
                        # Every member idles once before its final measurement.
                        delays_expected = 1 + (steps if arm in ("delay", "settle") else 0)
                    if operations.get("measure", 0) != measures or operations.get("delay", 0) != delays_expected:
                        raise runtime.LiveRunError(
                            f"{member.name}: the compiled circuit changed its measures or delays"
                        )
                    # A generic rx compiles to two sx; the barriers keep the unitary arm's rotations unmerged,
                    # where without them the run of rx gates fuses into one rotation of two sx in all.
                    if arm == "unitary" and (
                        operations.get("sx", 0) != 2 * steps or operations.get("barrier", 0) != steps - 1
                    ):
                        raise runtime.LiveRunError(f"{member.name}: the compiled rotations merged: {dict(operations)}")
                scores = [runtime.layout_score(isa, snapshot.backend.target) for isa in isas]
                if any(score <= 0 for score in scores):
                    raise runtime.LiveRunError(f"{group.name}: layout score underflows to zero")
                choice = runtime.Choice(
                    group,
                    snapshot,
                    runtime.SEED_TRANSPILER,
                    [qubit],
                    isas,
                    scores,
                    math.exp(sum(math.log(score) for score in scores) / len(scores)),
                )
                runtime._set_entries(
                    choice,
                    [Replica(0, {qubit: qubit}, min(scores))],
                    runtime.ReplicaPolicy(args.replica_floor, 1, False, True),
                )
                choices.append(choice)
            pubs = runtime.execution_pubs(choices)
            kinds = sorted(pub.kind for pub in pubs)
            if kinds != expected_kinds:
                raise runtime.LiveRunError(f"the members fused into PUB kinds {kinds}, not {expected_kinds}")
        except (runtime.LiveRunError, QiskitError, ValueError) as error:
            trace.setdefault("family_rejections", []).append(
                {"backend": snapshot.name, "qubits": qubits, "reason": str(error)}
            )
            continue
        if diagnostic:
            candidates.append(
                (
                    choices,
                    {
                        "name": MSQD_FAMILY,
                        "qubits": qubits,
                        "layout_source": "declared",
                        "main_qubits": [q for q in qubits if q in measurement_sequence_scatter.MSQD_MAIN_QUBITS],
                        "extra_qubits": [q for q in qubits if q not in measurement_sequence_scatter.MSQD_MAIN_QUBITS],
                        "arms": dict(MSQD_ARM_STEPS),
                        "total_rotation_rad": MSQ_THETA,
                        "steps": [16],
                        "prereadout_delay_dt": {str(qubit): dt for qubit, dt in prereadouts.items()},
                        "t1_delays_dt": t1_delays,
                        "selection_rule": measurement_sequence_scatter.SELECTION_RULE,
                        "floor_rule": measurement_sequence_scatter.FLOOR_RULE,
                        "plan_calibration": {str(q): calibration["qubits"][q] for q in qubits},
                        "placement_contract": (
                            "one pinned single-qubit placement per named qubit; every qubit runs each member in the "
                            "same shots; the six static PUBs hold the four signed unitary members, ro0 and ro1"
                        ),
                        "dt_seconds": snapshot.backend.target.dt,
                    },
                )
            )
            continue
        if envelope:
            candidates.append(
                (
                    choices,
                    {
                        "name": args.family,
                        "qubits": qubits,
                        "layout_source": "msq_envelope.layout_rule",
                        "layout_width": width,
                        "plan_calibration": {str(q): envelope_calibration["qubits"][q] for q in qubits},
                        "arms": dict(MSQ_ARM_STEPS),
                        "total_rotation_rad": MSQ_THETA,
                        "steps": list(MSQ_STEPS),
                        "measurement_delay_dt": {str(qubit): dt for qubit, dt in delays.items()},
                        "settle_delay_dt": {str(qubit): dt for qubit, dt in settles.items()},
                        "prereadout_delay_dt": {str(qubit): dt for qubit, dt in prereadouts.items()},
                        "t1_delays_dt": t1_delays,
                        "pattern_bits": [list(row) for row in msqe_pattern_bits(width)],
                        **(
                            {"equilibrium_delay_dt": equilibrium_dt, "reader_idle_delay_dt": reader_idle_dt}
                            if relaxation
                            else {}
                        ),
                        "placement_contract": (
                            "one single-qubit placement per qubit the layout rule keeps; every qubit runs each member "
                            "in the same shots; every member ends in a reset, so every PUB is dynamic"
                        ),
                        "dt_seconds": snapshot.backend.target.dt,
                    },
                )
            )
            continue
        candidates.append(
            (
                choices,
                {
                    "name": MSQ_FAMILY,
                    "qubits": qubits,
                    "layout_source": "declared",
                    "arms": dict(MSQ_ARM_STEPS),
                    "total_rotation_rad": MSQ_THETA,
                    "steps": list(MSQ_STEPS),
                    "measurement_delay_dt": {str(qubit): dt for qubit, dt in delays.items()},
                    "settle_delay_dt": {str(qubit): dt for qubit, dt in settles.items()},
                    "prereadout_delay_dt": {str(qubit): dt for qubit, dt in prereadouts.items()},
                    "t1_delays_dt": t1_delays,
                    "placement_contract": (
                        "one pinned single-qubit placement per named qubit; every qubit runs each member in the "
                        "same shots; static PUBs hold the one-step measure and every delay member, dynamic PUBs "
                        "the measure members with two or more steps"
                    ),
                    "dt_seconds": snapshot.backend.target.dt,
                },
            )
        )
    return candidates[: args.optimizer_candidates]


def family_candidates(
    runtime: Any, snapshots: list[Any], args: Any, trace: dict[str, Any]
) -> list[tuple[list[Any], dict[str, Any]]]:
    """Enumerate matched circuit sets; a folded family retains its exact physical mapping."""
    if args.family == "et-row":
        from et_planning import family_candidates as et_candidates

        return et_candidates(runtime, snapshots, args, trace)
    if args.family in ("ripple", "rank-sector"):
        import algebra_planning

        return algebra_planning.family_candidates(runtime, snapshots, args, trace)
    candidates: list[tuple[list[Any], dict[str, Any]]] = []
    if args.family in (*N21_FAMILIES, "n21-orbit-rca"):
        routed = []
        windows: dict[int, dict[str, Any]] = {}
        herald = bool(getattr(args, "init_herald", False))
        doses = tuple(getattr(args, "window_doses_dt", None) or ())
        if args.family == "n21-orbit-rca":
            # Window durations come from each backend's calibration, so each
            # snapshot routes its own group; per-snapshot traces merge by group.
            # A backend that lacks calibrated durations or rejects the group
            # leaves the others in the search; the trace records its reason.
            # Routing uses the backend-wide bound, and each routed candidate
            # then takes its control's own measure and reset durations.
            # A pinned layout compiles every arm from the named qubits and
            # keeps the identity replica, so the replica search cannot
            # permute the roles.
            # The overlap split replaces the window sweep and needs the
            # control's reset length beside the window durations.
            pin = getattr(args, "pin_layout", None)
            # The ground-control split holds spectator arms alone and also
            # idles the control's measure plus reset length.
            ground = bool(getattr(args, "ground_control_split", False))
            ramsey = tuple(getattr(args, "ramsey_windows", None) or ())
            sweep = getattr(args, "segmented_sweep", None)
            split = bool(getattr(args, "overlap_split", False)) or ground
            for snapshot in snapshots:
                local: dict[str, Any] = {}
                try:
                    pinned = None if pin is None else pinned_orbit_layout(runtime, snapshot, pin)
                    bound = window_durations(runtime, snapshot)
                    reset_bound = reset_window_dt(runtime, snapshot) if split else None
                    if doses:
                        window_dose_timing_violations(runtime, snapshot, doses)
                    group = n21_orbit_rca_group(
                        bound[0],
                        bound[1],
                        herald,
                        window_sweep=not split and not doses,
                        overlap_split=split and not ground,
                        reset_dt=reset_bound,
                        ground_control_split=ground,
                        ramsey_windows=ramsey,
                        segmented=sweep,
                        window_doses=doses,
                        detuning_sign=bool(getattr(args, "detuning_sign", False)),
                    )
                    placed = runtime.select_candidates(group, [snapshot], args.seeds, local, pinned)
                except (runtime.LiveRunError, QiskitError, ValueError) as error:
                    trace.setdefault("family_rejections", []).append({"backend": snapshot.name, "reason": str(error)})
                    continue
                trace.setdefault(group.name, {}).update(local.get(group.name, {}))
                for placement in placed:
                    try:
                        choice, window = _control_windows(runtime, placement, bound, reset_bound)
                        if getattr(args, "detuning_sign", False):
                            choice, window = detuning_roles_choice(runtime, choice, window)
                        if pinned is not None:
                            if moved := pinned_roles_violations(runtime, choice, pinned):
                                raise runtime.LiveRunError("; ".join(moved))
                            window = window | {"pin_layout": {"backend": snapshot.name, "qubits": pinned}}
                    except (runtime.LiveRunError, QiskitError, ValueError) as error:
                        trace.setdefault("family_rejections", []).append(
                            {
                                "backend": snapshot.name,
                                "seed": placement.seed,
                                "layout": placement.layout,
                                "reason": str(error),
                            }
                        )
                        continue
                    routed.append(choice)
                    windows[id(choice)] = window
            if not routed:
                raise runtime.LiveRunError(
                    f"no backend routes the N=21 window family: {trace.get('family_rejections')}"
                )
            routed.sort(key=lambda choice: -choice.joint_score)
        else:
            routed = runtime.select_candidates(
                n21_group(orbit=args.family == "n21-orbit-feedback", encoded=args.family == "n21-feedback-encoded"),
                snapshots,
                args.seeds,
                trace,
            )
        tiers = n21_replica_tiers(args)
        if not tiers:
            raise runtime.LiveRunError("replica tiers contain no placement within --max-replicas")
        for candidate in routed[: args.optimizer_candidates]:
            replica_sets: list[list[tuple[int, ...]]] = []
            for cap in sorted(set(tiers)):
                trial = copy.copy(candidate)
                policy = runtime.ReplicaPolicy(args.replica_floor, cap, False, True)
                pinned_replicas = (
                    [Replica(0, {qubit: qubit for qubit in candidate.layout}, min(candidate.member_scores))]
                    if "pin_layout" in windows.get(id(candidate), {})
                    else None
                )
                if runtime._prepare_individual_candidate(trial, trace, policy, pinned_replicas):
                    # A cap above the floor-admitted replica count places the
                    # same replicas as a smaller cap; one copy enters the search.
                    replicas = [tuple(replica.qubits) for replica in trial.replicas]
                    if replicas in replica_sets:
                        continue
                    replica_sets.append(replicas)
                    candidates.append(
                        (
                            [trial],
                            {
                                "name": args.family,
                                "replica_cap": cap,
                                **windows.get(id(candidate), {}),
                                **({"init_herald": True} if herald else {}),
                                **(
                                    {
                                        "overlap_split": True,
                                        "overlap_arm": N21_OVERLAP_ARM,
                                        "orbit_gate_counts": orbit_gate_counts(candidate),
                                    }
                                    if getattr(args, "overlap_split", False)
                                    else {
                                        "ground_control_split": True,
                                        **(
                                            {"ramsey_windows": list(args.ramsey_windows)}
                                            if getattr(args, "ramsey_windows", None)
                                            else {}
                                        ),
                                        **(
                                            {"segmented_sweep": args.segmented_sweep}
                                            if getattr(args, "segmented_sweep", None)
                                            else {}
                                        ),
                                    }
                                    if getattr(args, "ground_control_split", False)
                                    else {
                                        "window_doses": list(doses),
                                        **({"detuning_sign": True} if getattr(args, "detuning_sign", False) else {}),
                                    }
                                    if doses
                                    else {"window_sweep": True}
                                    if args.family == "n21-orbit-rca"
                                    else {}
                                ),
                            },
                        )
                    )
        return candidates
    if args.family in PATCH_FAMILIES:
        return patch_candidates(runtime, snapshots, args, trace)
    if args.family == STATE_PREP_FAMILY:
        return state_prep_candidates(runtime, snapshots, args, trace)
    if args.family in (MSQ_FAMILY, MSQD_FAMILY, MSQE_FAMILY, MSQR_FAMILY):
        return measurement_sequence_candidates(runtime, snapshots, args, trace)
    if args.family == LATENCY_RECOVERY_FAMILY:
        return latency_recovery_candidates(runtime, snapshots, args, trace)
    if args.family != "folded-qpe":
        raise runtime.LiveRunError(f"unknown family {args.family}")
    coherent = runtime.select_candidates(folded_group(("coherent",)), snapshots, args.seeds, trace)
    for candidate in coherent[: args.optimizer_candidates]:
        layout = candidate.layout[:5]
        try:
            archived = folded_group(("archived",))
            archived_isas = [
                runtime._compile(member.circuit, candidate.snap, candidate.seed, layout) for member in archived.members
            ]
            writers = {
                label: next(qubits[0] for name, qubits in runtime._ops(isa) if name == "measure")
                for label, isa in enumerate(archived_isas)
            }
            delay_dt = {label: measurement_delay(runtime, candidate.snap, writer) for label, writer in writers.items()}
            group = folded_group(("archived", "delay", "no_feed_forward"), delay_dt)
            isas = [
                *archived_isas,
                *(
                    runtime._compile(member.circuit, candidate.snap, candidate.seed, layout)
                    for member in group.members[4:]
                ),
            ]
            for label, isa in enumerate(isas[4:8]):
                delayed = [
                    isa.find_bit(instruction.qubits[0]).index
                    for instruction in isa.data
                    if instruction.operation.name == "delay"
                ]
                if delayed != [writers[label]]:
                    raise runtime.LiveRunError(
                        f"s{label}: delay route {delayed} differs from measurement wire {writers[label]}"
                    )
            violations = [reason for isa in isas for reason in runtime.compiled_violations(isa, candidate.snap)]
            if violations:
                raise runtime.LiveRunError(str(violations))
            scores = [runtime.layout_score(isa, candidate.snap.backend.target) for isa in isas]
            if any(score <= 0 for score in scores):
                raise runtime.LiveRunError(f"{group.name}: layout score underflows to zero on patch {layout}")
            dynamic = runtime.Choice(
                group,
                candidate.snap,
                candidate.seed,
                layout,
                isas,
                scores,
                math.exp(sum(math.log(score) for score in scores) / len(scores)),
            )
            trial = [copy.copy(candidate), dynamic]
            # One fixed layout isolates the measured device patch. Re-embedding a
            # delay arm changes the measurement duration it replaces; the family
            # therefore searches layouts but does not pool independent placements.
            used = sorted({qubit for choice in trial for isa in choice.isas for qubit in runtime._physical(isa)})
            replica = Replica(0, {qubit: qubit for qubit in used}, min(scores))
            for choice in trial:
                runtime._set_entries(choice, [replica], runtime.ReplicaPolicy(args.replica_floor, 1, False, True))
            runtime.execution_pubs(trial)
        except (runtime.LiveRunError, ValueError) as error:
            trace.setdefault("family_rejections", []).append(
                {"backend": candidate.snap.name, "seed": candidate.seed, "reason": str(error)}
            )
            continue
        candidates.append(
            (
                trial,
                {
                    "name": args.family,
                    "measurement_delay_dt": {str(label): duration for label, duration in delay_dt.items()},
                    "replaced_measurement_qubits": {str(label): writer for label, writer in writers.items()},
                    "shared_initial_layout": layout,
                    "extra_control": candidate.layout[5],
                    "placement_contract": "one fixed shared work register; separate static/dynamic jobs",
                    "measurement_seconds": {
                        str(label): candidate.snap.backend.target["measure"][(writer,)].duration
                        for label, writer in writers.items()
                    },
                    "measurement_sites": {
                        member.name: [list(qubits) for name, qubits in runtime._ops(isa) if name == "measure"]
                        for choice in trial
                        for member, isa in zip(choice.group.members, choice.isas, strict=True)
                    },
                    "interpretation_boundary": (
                        "shared initial mapping; coherent routing and terminal readout sites can differ"
                    ),
                    "dt_seconds": candidate.snap.backend.target.dt,
                },
            )
        )
    return candidates


# IBM's latest-updates changelog sets the repetition delay of Heron and
# Eagle QPUs to 20 us through 2 ms, while their configurations report a
# rep_delay_range starting at 0; a job below 20 us passes the service's range
# check and then ends without a shot loop (docs/notes/ibm_heron_platform.md).
REP_DELAY_FLOOR_SECONDS = {"Heron": 20e-6, "Eagle": 20e-6}


def repetition_delay(backend: Any, requested: float | None = None) -> float:
    """The repetition delay in seconds a job on backend runs at: requested, or the backend default.

    The SDK attributes carry seconds; configuration.to_dict uses wire
    microseconds. A requested value must lie in rep_delay_range, which IBM's
    repetition-rate guide names the supported interval and which changes
    over time, so every caller reads it from a fresh configuration. A
    selected value on a Heron or Eagle processor, the requested one or the
    backend default, also holds the changelog floor in
    REP_DELAY_FLOOR_SECONDS, which the configuration's range omits.
    """
    configuration = backend.configuration()
    value = getattr(configuration, "default_rep_delay", None)
    interval = getattr(configuration, "rep_delay_range", None)
    if (
        not getattr(configuration, "dynamic_reprate_enabled", False)
        or value is None
        or not math.isfinite(value)
        or value < 0
        or interval is None
        or len(interval) != 2
        or not interval[0] <= value <= interval[1]
    ):
        raise ValueError("cost planning requires a valid backend default repetition delay in seconds")
    low, high = float(interval[0]), float(interval[1])
    if requested is not None and (not math.isfinite(requested) or not low <= requested <= high):
        raise ValueError(f"repetition delay {requested} s lies outside the backend range [{low}, {high}] s")
    selected = float(value if requested is None else requested)
    processor = getattr(configuration, "processor_type", None)
    family = processor.get("family") if isinstance(processor, dict) else None
    floor = REP_DELAY_FLOOR_SECONDS.get(str(family))
    if floor is not None and selected < floor:
        source = "backend default" if requested is None else "requested"
        raise ValueError(f"{source} repetition delay {selected} s lies below the {family} floor of {floor} s")
    return selected


def repetition_delay_range(backend: Any) -> list[float] | None:
    """backend's rep_delay_range in seconds, or None for a fixed repetition rate."""
    configuration = backend.configuration()
    interval = getattr(configuration, "rep_delay_range", None)
    if not getattr(configuration, "dynamic_reprate_enabled", False) or interval is None or len(interval) != 2:
        return None
    return [float(interval[0]), float(interval[1])]


def shot_ceiling(backend: Any) -> int | None:
    """backend's configuration().max_shots, the per-PUB shot limit planning and each batch hold, or None."""
    value = getattr(backend.configuration(), "max_shots", None)
    return int(value) if value else None


def shot_ceiling_violations(backend: Any, shots: int) -> list[str]:
    """Why shots per PUB cannot run under backend's fresh max_shots."""
    ceiling = shot_ceiling(backend)
    return [f"{shots} shots per PUB exceed max_shots {ceiling}"] if ceiling is not None and shots > ceiling else []


def repetition_delay_violations(backend: Any, requested: float, planned_range: list[float] | None) -> list[str]:
    """Why requested cannot run on backend's fresh configuration, or why its allowed range moved since planning."""
    try:
        repetition_delay(backend, requested)
    except (ValueError, AttributeError) as error:
        return [f"repetition delay: {error}"]
    current = repetition_delay_range(backend)
    if planned_range is not None and current != planned_range:
        return [f"repetition delay range moved from {planned_range} s to {current} s since planning"]
    return []


def execution_contract(choices: list[Any], record: dict[str, Any]) -> dict[str, Any]:
    """Bind submitted repetition settings and selected cost inputs to approval."""
    backends = {choice.snap.name: choice.snap.backend for choice in choices}
    optimization = record.get("optimization", {})
    selected: dict[str, Any] = next(
        (
            candidate
            for candidate in optimization.get("candidates", [])
            if candidate["name"] == optimization.get("selected")
        ),
        {},
    )
    requested = record.get("policy", {}).get("rep_delay_seconds")
    return {
        "backends": [
            {
                "name": name,
                "repetition_delay_seconds": repetition_delay(backend)
                if getattr(backend.configuration(), "dynamic_reprate_enabled", False)
                else None,
            }
            if requested is None
            else {
                # A requested delay binds its value and the range it was admitted
                # in, so a moved range differs from the approved contract.
                "name": name,
                "repetition_delay_seconds": requested,
                "repetition_delay_source": "--rep-delay",
                "default_repetition_delay_seconds": repetition_delay(backend)
                if getattr(backend.configuration(), "dynamic_reprate_enabled", False)
                else None,
                "repetition_delay_range_seconds": repetition_delay_range(backend),
            }
            for name, backend in sorted(backends.items())
        ],
        "selected_job_costs": json.loads(json.dumps(selected.get("jobs", []))),
        "selected_cost_scenarios": json.loads(json.dumps(selected.get("cost_scenarios", []))),
        "selected_worst_case_charge_seconds": selected.get("worst_case_charge_seconds"),
        **({"pub_shots": dict(record["pub_shots"])} if "pub_shots" in record else {}),
    }


def admitted_family_candidates(
    runtime: Any, candidates: list[tuple[list[Any], dict[str, Any]]], trace: dict[str, Any]
) -> list[tuple[list[Any], dict[str, Any]]]:
    """Drop every candidate holding a group that runtime.group_admission_violations rejects on its snapshot.

    Family builders construct Choices from direct compiles, outside
    select_candidates, so this applies the predicate the pre-submit refresh
    applies; each rejection names its backend, group and violations.
    """
    admitted = []
    for choices, configuration in candidates:
        rejected = [
            f"{choice.group.name}: {'; '.join(violations)}"
            for choice in choices
            if (violations := runtime.group_admission_violations(choice.group, choice.snap.capabilities))
        ]
        if rejected:
            backends = ",".join(sorted({choice.snap.name for choice in choices}))
            trace.setdefault("family_rejections", []).append({"backend": backends, "reason": " | ".join(rejected)})
            continue
        admitted.append((choices, configuration))
    return admitted


# A worker pool starts slower than a handful of small circuits take, while one measurement-sequence member with 17
# classical bits enumerates 2**17 branches; the check parallelizes from this many circuits.
IDEAL_PARALLEL_MIN_ITEMS = 16


def compiled_ideal_key(replica: QuantumCircuit) -> str | None:
    """The exact key of a compiled replica's oracle input, or None for an object that is no circuit (module level for
    the pool); an unkeyed replica keeps a law of its own."""
    if not isinstance(replica, QuantumCircuit):
        return None
    return oracle_key(compact_ideal_circuit(replica))


def compiled_ideal_law(replica: QuantumCircuit) -> tuple[float, ...]:
    """The exact branch law of one compiled replica (module level for the pool)."""
    return ideal_compiled_probabilities(replica)


def check_compiled_ideals(runtime: Any, choices: list[Any]) -> None:
    """Prove every replica of every entry equals its labeled ideal, raising for the first entry in order that fails.

    The oracle runs once per distinct oracle input (qpe_diagnostics.oracle_key): compiled copies of one member on
    different physical qubits compact to one circuit and share its law, while each entry is still compared with its
    own labeled ideal. Keys and laws map through parallel.ordered_map; a serial proof widens the time between the
    pre-submit snapshot and the first batch beyond a calibration period.
    """
    names = [entry.name for choice in choices for entry in choice.entries for _ in entry.replicas]
    ideals = [entry.ideal for choice in choices for entry in choice.entries for _ in entry.replicas]
    replicas = [replica for choice in choices for entry in choice.entries for replica in entry.replicas]
    keyed = parallel.ordered_map(compiled_ideal_key, replicas, min_items=IDEAL_PARALLEL_MIN_ITEMS)
    inputs: dict[str, QuantumCircuit] = {}
    keys = []
    for index, (key, replica) in enumerate(zip(keyed, replicas, strict=True)):
        # Control flow has no key; such a replica keeps a law of its own.
        resolved = key if key is not None else f"unkeyed-{index}"
        inputs.setdefault(resolved, replica)
        keys.append(resolved)
    laws = dict(
        zip(
            inputs,
            parallel.ordered_map(compiled_ideal_law, list(inputs.values()), min_items=IDEAL_PARALLEL_MIN_ITEMS),
            strict=True,
        )
    )
    for name, key, ideal in zip(names, keys, ideals, strict=True):
        if not np.allclose(laws[key], ideal, rtol=0, atol=1e-10):
            raise runtime.LiveRunError(f"{name}: compiled labeled ideal differs from its exact oracle")


def prepare(
    runtime: Any, snapshots: list[Any], args: Any, usage: dict[str, Any], trace: dict[str, Any]
) -> tuple[list[Any], dict[str, Any]]:
    """Compile and simulate the bounded candidate set before choosing a shot tier."""
    if args.family == "folded-correction":
        import correction_planning

        return correction_planning.prepare(runtime, snapshots, args, usage, trace)
    excitation = getattr(args, "prep_excitation", None)
    if excitation is not None and args.family not in N21_FAMILIES:
        raise runtime.LiveRunError("--prep-excitation applies to the N21 families")
    candidates = admitted_family_candidates(runtime, family_candidates(runtime, snapshots, args, trace), trace)
    if not candidates:
        diagnostic = runtime._scrub_instances(runtime._jsonable(trace))
        raise runtime.LiveRunError(
            "the experiment family has no admitted routed candidate; "
            f"family={args.family!r}; selection_trace={json.dumps(diagnostic, sort_keys=True)}"
        )
    contracts = family_contracts(
        args.family,
        args.precision,
        args.alpha,
        args.power,
        **contract_configuration(args.family, candidates[0][1]),
    )
    plans: list[CandidatePlan] = []
    et_screens: dict[str, dict[str, Any]] = {}
    ownership: dict[str, tuple[list[Any], dict[str, Any], int]] = {}
    simulators: dict[int, Any] = {}
    tiers = sorted(set(args.shot_tiers if args.optimize else [args.shots]))
    # Tiers above a candidate backend's max_shots never reach a plan; the
    # trace keeps the dropped tiers beside the ceiling that dropped them.
    ceiling = min(
        (
            limit
            for choices, _configuration in candidates
            for choice in choices
            if (limit := shot_ceiling(choice.snap.backend)) is not None
        ),
        default=None,
    )
    if ceiling is not None and tiers[-1] > ceiling:
        trace["shot_ceiling"] = {"max_shots": ceiling, "dropped_tiers": [shots for shots in tiers if shots > ceiling]}
        tiers = [shots for shots in tiers if shots <= ceiling]
        if not tiers:
            raise runtime.LiveRunError(f"every shot tier exceeds max_shots {ceiling}: {trace['shot_ceiling']}")
    per_pub = getattr(args, "shot_allocation", "uniform") == "per-pub"
    if per_pub and (args.family not in ("et-row", "ripple", "rank-sector", *PATCH_FAMILIES) or not args.optimize):
        raise runtime.LiveRunError("per-PUB shot allocation requires an optimized algebra or patch family")
    if not per_pub and hasattr(args, "pub_shots"):
        del args.pub_shots
    model_method = getattr(args, "model_method", "sampled")
    variance_bound = getattr(args, "replica_variance_bound", None)
    if (model_method != "sampled" or variance_bound is not None) and args.family not in N21_FAMILIES:
        raise runtime.LiveRunError("--model-method exact and --replica-variance-bound apply to the N21 families")
    # Every endpoint of an opted-in N21 family plans its confidence and
    # detection radii under the empirical-Bernstein rule on the exact law's
    # variance; other families keep the data-free radii.
    bernstein: tuple[EmpiricalBernsteinDesign, ...] = ()
    if getattr(args, "empirical_bernstein", False):
        if args.family not in N21_FAMILIES or model_method != "exact":
            raise runtime.LiveRunError("--empirical-bernstein applies to the N21 families under --model-method exact")
        bernstein = tuple(EmpiricalBernsteinDesign(contract.name) for contract in contracts)
    exact_evidence: dict[int, dict[str, Any]] = {}
    for choices, _configuration in candidates:
        for choice in choices:
            if id(choice.snap) not in simulators:
                simulators[id(choice.snap)] = runtime.noise_simulator(
                    choice.snap.name, choice.snap.backend.target, choice.snap.properties, local_compute.settings(args)
                )

    # Aer releases the GIL while it simulates, so independent choices run on
    # threads. Each simulator already uses the policy's thread count, so the
    # pool runs only as many simulators as fit in the available CPUs. Each
    # pool thread reuses one simulator per snapshot, built from the
    # snapshot's cached noise model, for every choice it runs: local_compute.run
    # sets the device and method of each batch, and AerSimulator.from_backend
    # converts the whole-device Target to BackendProperties on every build. A
    # task returns the batch evidence its run appended, which joins the
    # snapshot simulator in serial order.
    # A declared initial excitation enters the sampled model and the exact
    # law alike, so the sampled falsifier tests the law the plan prices.
    excited = {"prep_excitation": excitation} if excitation else {}
    lane = threading.local()

    def simulate_choice(choice: Any) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        owned: dict[int, Any] = lane.__dict__.setdefault("simulators", {})
        simulator = owned.get(id(choice.snap))
        if simulator is None:
            simulator = owned[id(choice.snap)] = runtime.noise_simulator(
                choice.snap.name, choice.snap.backend.target, choice.snap.properties, local_compute.settings(args)
            )
        start = len(local_compute.batches(simulator))
        if args.family == "et-row":
            from et_planning import simulate as simulate_et

            noisy = simulate_et(runtime, choice, simulator, args.model_shots)
        else:
            noisy = runtime.simulate(choice, simulator, args.model_shots, **excited)
        return local_compute.batches(simulator)[start:], noisy

    ordered = [choice for choices, _configuration in candidates for choice in choices]
    concurrent = max(1, parallel.workers() // local_compute.settings(args)["threads"])
    with ThreadPoolExecutor(max_workers=concurrent) as pool:
        simulated = iter(list(pool.map(simulate_choice, ordered)))
    for candidate_index, (choices, configuration) in enumerate(candidates):
        predictions: dict[str, tuple[tuple[float, ...], ...]] = {}
        if args.family != "et-row":
            check_compiled_ideals(runtime, choices)
        for choice in choices:
            if args.family == "et-row":
                from et_planning import validate_ideals

                try:
                    validate_ideals(choice)
                except ValueError as error:
                    raise runtime.LiveRunError(str(error)) from error
            evidence, noisy = next(simulated)
            local_compute.append_batches(simulators[id(choice.snap)], evidence)
            predictions.update(
                {name: tuple(tuple(map(float, dist)) for dist in replicas) for name, replicas in noisy.items()}
            )
        if model_method == "exact":
            # A candidate whose exact law fails its sampled falsifier leaves the
            # search; the trace keeps the reason and the run continues.
            try:
                predictions, exact_evidence[candidate_index] = n21_exact_planning.exact_predictions(
                    choices,
                    {id(choice.snap): simulators[id(choice.snap)].options.noise_model for choice in choices},
                    predictions,
                    args.model_shots,
                    args.simulation_alpha,
                    contracts,
                    **excited,
                )
            except n21_exact_planning.ExactModelRejected as error:
                exact_evidence[candidate_index] = error.evidence
                trace.setdefault("model_rejections", []).append(
                    {"candidate": f"candidate-{candidate_index:03d}", "reason": str(error)}
                )
                continue
        for shots in [max(tiers)] if per_pub else tiers:
            jobs = []
            for backend_name in sorted({choice.snap.name for choice in choices}):
                selected = [choice for choice in choices if choice.snap.name == backend_name]
                backend = selected[0].snap.backend
                for kind in ("dynamic", "static"):
                    for index, batch in enumerate(runtime.submission_batches(selected, kind, shots), 1):
                        pubs = []
                        for pub in batch:
                            manifest = pub.manifest()
                            pubs.append(
                                PubPrediction(
                                    name=pub.name,
                                    member_distributions={
                                        component.entry.name: predictions[component.entry.name]
                                        for component in pub.components
                                    },
                                    scheduled_seconds=runtime.duration_s(pub.circuit, backend.target),
                                    repetition_delay_seconds=repetition_delay(
                                        backend, getattr(args, "rep_delay", None)
                                    ),
                                    classical_latency_seconds=manifest["sequential_stage_count"]
                                    * args.classical_latency_us
                                    * 1e-6,
                                    simulation_shots=None if model_method == "exact" else args.model_shots,
                                    classical_stage_count=manifest["sequential_stage_count"],
                                    duration_assumption=(
                                        "Target duration includes reset; dynamic classical latency is a declared "
                                        "per-stage planning assumption"
                                    ),
                                )
                            )
                        jobs.append(
                            JobCandidate(
                                name=f"{backend_name}/{kind}/{index}",
                                pubs=tuple(pubs),
                                shots=shots,
                                overhead_seconds=args.job_overhead_seconds,
                                max_execution_seconds=args.max_execution_seconds,
                                overhead_assumption=(
                                    "declared overhead; 2.3 s default is the retained dynamic job's non-circuit "
                                    "charge, not a backend guarantee"
                                ),
                            )
                        )
            if args.family in ("ripple", "rank-sector") and len(jobs) != 1:
                raise runtime.LiveRunError(
                    f"{args.family}: {shots} shots require {len(jobs)} jobs; the static family requires one job"
                )
            name = f"candidate-{candidate_index:03d}-shots-{shots}"
            try:
                covariance = (
                    n21_exact_planning.replica_covariance_bounds(
                        [pub for job in jobs for pub in job.pubs], contracts, variance_bound, shots
                    )
                    if variance_bound is not None
                    else ()
                )
            except ValueError as error:
                trace.setdefault("model_rejections", []).append({"candidate": name, "reason": str(error)})
                continue
            plans.append(
                CandidatePlan(
                    name=name,
                    jobs=tuple(jobs),
                    covariance_bounds=covariance,
                    empirical_bernstein=bernstein,
                    **(
                        {
                            "independent_pub_blocks": tuple(
                                tuple(
                                    pub.name
                                    for job in jobs
                                    for pub in job.pubs
                                    if {
                                        configuration["members"][member]["block"] for member in pub.member_distributions
                                    }
                                    == {block}
                                )
                                for block in range(configuration["blocks"])
                            ),
                            "pub_independence_assumption": configuration["sampling_assumption"],
                        }
                        if args.family == "et-row"
                        else {}
                    ),
                    proxy_metadata={
                        "backend": choices[0].snap.name,
                        "seed": choices[0].seed,
                        "replicas": len(choices[0].replicas),
                        "shots": shots,
                        "proxy_score": sum(choice.joint_score for choice in choices) / len(choices),
                    },
                )
            )
            ownership[name] = choices, configuration, shots
            if args.family == "et-row":
                from et_planning import calibrated_design

                et_screens[name] = calibrated_design(configuration, predictions)
    if not plans:
        raise runtime.LiveRunError(
            f"every candidate failed its model or covariance admission: {trace.get('model_rejections')}"
        )
    remaining = usage.get("usage_remaining_seconds")
    budget = BudgetContract(
        float(remaining) if remaining is not None else args.max_total_execution_seconds + args.reserve_seconds,
        args.reserve_seconds,
        args.max_total_execution_seconds,
    )
    policy = settings(args)
    scenarios = tuple(CostScenario(**scenario) for scenario in policy["cost_scenarios"])
    allocation_audits: dict[str, dict[str, Any]] = {}
    if per_pub:
        from pub_shot_allocation import allocate_plans

        couplings: dict[str, tuple[tuple[str, ...], ...]] = {}
        for candidate in plans:
            candidate_choices, configuration, _shots = ownership[candidate.name]
            row_pubs: dict[int, str] = {}
            metadata = configuration.get("members", {})
            for pub in runtime.execution_pubs(candidate_choices):
                for component in pub.components:
                    row = metadata.get(component.entry.name, {}).get("execution_row")
                    if row is not None:
                        if row in row_pubs and row_pubs[row] != pub.name:
                            raise runtime.LiveRunError("a declared execution row was split across PUBs")
                        row_pubs[row] = pub.name
            couplings[candidate.name] = tuple(
                tuple(row_pubs[row] for row in rows) for rows in configuration.get("matched_walk_rows", {}).values()
            )
        if args.family == "et-row":
            from et_planning import fixed_allocations

            allocated, allocation_audits = fixed_allocations(tuple(plans), ownership, runtime)
        else:
            allocated, allocation_audits = allocate_plans(
                tuple(plans),
                contracts,
                tuple(tiers),
                budget,
                simulation_alpha=args.simulation_alpha,
                objective=policy["objective"],
                cost_scenarios=scenarios,
                coupled_pubs=couplings,
                unscored_tier="smallest" if args.family in PATCH_FAMILIES else "largest",
            )
        for original, allocated_plan in zip(plans, allocated, strict=True):
            selected_choices, selected_configuration, _shots = ownership[original.name]
            ownership[allocated_plan.name] = (
                selected_choices,
                selected_configuration,
                max(allocation_audits[allocated_plan.name]["pub_shots"].values()),
            )
        plans = list(allocated)
    result = optimize(
        tuple(plans),
        contracts,
        budget,
        simulation_alpha=args.simulation_alpha,
        objective=policy["objective"],
        cost_scenarios=scenarios,
    )
    if args.family == "et-row":
        from experiment_optimizer import restrict_candidates

        result = restrict_candidates(
            result,
            {name for name, screen in et_screens.items() if screen["admitted"]},
            "ET calibrated inference fails at declared allocation",
        )
    # An infeasible dry run retains a concrete candidate and every rejection;
    # its state prevents that diagnostic archive from becoming a submission.
    retained = result.selected or plans[0].name
    choices, configuration, args.shots = ownership[retained]
    retained_plan = next(plan for plan in plans if plan.name == retained)
    retained_index = int(retained.split("-")[1])
    if per_pub:
        args.pub_shots = dict(allocation_audits[retained]["pub_shots"])
    metadata = {
        "family_configuration": configuration,
        **({"et_calibrated_design": et_screens[retained]} if args.family == "et-row" else {}),
        "observable_contracts": observable_contract_records(contracts),
        "optimization": result.as_dict()
        | {
            "retained_candidate": retained,
            "searched_routed_sets": len(candidates),
            "shot_tiers": tiers,
            "scope": (
                "bounded routed candidates with endpoint minima and costed whole-tier consolidation; "
                "global optimality is unclaimed"
                if per_pub
                else "bounded routed candidates and uniform shot tiers; global optimality is unclaimed"
            ),
        }
        | ({"et_calibrated_candidates": et_screens} if args.family == "et-row" else {}),
        "optimizer_settings": settings(args),
        **(
            {
                "exact_model": exact_evidence[retained_index]
                | {
                    "retained_candidate": retained,
                    "candidates": {
                        f"candidate-{index:03d}": {
                            key: evidence[key]
                            for key in ("max_gap", "passed", "failures", "arms", "contrasts", "replicas")
                        }
                        for index, evidence in sorted(exact_evidence.items())
                    },
                }
            }
            if retained_index in exact_evidence
            else {}
        ),
        **(
            {
                "covariance_bounds": json.loads(
                    json.dumps([asdict(bound) for bound in retained_plan.covariance_bounds])
                ),
                "covariance_falsifier": dict(n21_exact_planning.COVARIANCE_FALSIFIER),
            }
            if retained_plan.covariance_bounds
            else {}
        ),
        **(
            {
                "empirical_bernstein": {
                    "specification": dict(EMPIRICAL_BERNSTEIN),
                    "designs": [asdict(design) for design in retained_plan.empirical_bernstein],
                    "planned": planned_empirical_bernstein(retained_plan, contracts),
                }
            }
            if retained_plan.empirical_bernstein
            else {}
        ),
        **({"pub_shots": args.pub_shots, "shot_allocation": allocation_audits[retained]} if per_pub else {}),
        "optimization_budget": asdict(budget),
        "local_simulation_batches": (
            batches := [batch for simulator in simulators.values() for batch in local_compute.batches(simulator)]
        ),
        "compiled_ideal_validation": {
            "method": "branch-resolved statevector on active compiled replica wires",
            "absolute_tolerance": 1e-10,
            "noise_method": sorted({str(batch["method"]) for batch in batches}),
            "noise_policy": local_compute.settings(args)["method"],
            "all_candidates_passed": True,
        },
    }
    return choices, metadata


def measured_family(
    record: dict[str, Any],
    distributions: dict[str, list[np.ndarray]],
    executed: dict[str, Any],
    runtime: Any,
    *,
    correction_evidence: list[dict[str, Any]] | None = None,
    replica_registers: dict[str, dict[str, list[str]]] | None = None,
    shot_order: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """The family analysis of a collected record: the precision endpoints and, for measurement-sequence, the
    preregistered pinching decisions beside them.

    shot_order serves the measurement-sequence-relaxation family: "registers" holds the shot-ordered registers of
    the PUBs msq_successor_analysis.required_pubs names, "chunks" the executor's chunk_timing as lists of PUB
    indices, and "reason" why either could not be read; an absent entry withholds every qubit.

    The pinching analysis (measurement_sequence_analysis.collected) reads every member of both jobs through one
    readout correction, so it runs only when the members executed under one calibration
    (runtime._comparisons_withheld); otherwise it reports the reason.
    """
    analysis = _measured_contracts(
        record,
        distributions,
        executed,
        runtime,
        correction_evidence=correction_evidence,
        replica_registers=replica_registers,
    )
    name = record.get("family_configuration", {}).get("name")
    if name == MSQD_FAMILY:
        members = sorted(name for name in distributions if name.startswith("msq_"))
        reason = runtime._comparisons_withheld(members, executed) if members else "no measured members"
        if reason:
            return {**analysis, "scatter": {"schema": measurement_sequence_scatter.SCHEMA, "withheld": reason}}
        return {**analysis, "scatter": measurement_sequence_scatter.collected(record, distributions, executed)}
    if name == MSQE_FAMILY:
        members = sorted(name for name in distributions if name.startswith("msq"))
        reason = runtime._comparisons_withheld(members, executed) if members else "no measured members"
        if reason:
            return {**analysis, "envelope": {"schema": msq_envelope_analysis.SCHEMA, "withheld": reason}}
        return {**analysis, "envelope": msq_envelope_analysis.collected(record, distributions, executed)}
    if name == MSQR_FAMILY:
        members = sorted(name for name in distributions if name.startswith("msq"))
        reason = runtime._comparisons_withheld(members, executed) if members else "no measured members"
        if reason:
            return {**analysis, "relaxation": {"schema": msq_successor_analysis.SCHEMA, "withheld": reason}}
        evidence = shot_order or {}
        if evidence.get("reason"):
            return {
                **analysis,
                "relaxation": {"schema": msq_successor_analysis.SCHEMA, "withheld": str(evidence["reason"])},
            }
        return {
            **analysis,
            "relaxation": msq_successor_analysis.collected(
                record, distributions, executed, evidence.get("registers"), evidence.get("chunks")
            ),
        }
    if name != MSQ_FAMILY:
        return analysis
    members = sorted(name for name in distributions if name.startswith("msq_"))
    reason = runtime._comparisons_withheld(members, executed) if members else "no measured members"
    if reason:
        return {**analysis, "pinching": {"schema": measurement_sequence_analysis.SCHEMA, "withheld": reason}}
    return {**analysis, "pinching": measurement_sequence_analysis.collected(record, distributions, executed)}


def _measured_contracts(
    record: dict[str, Any],
    distributions: dict[str, list[np.ndarray]],
    executed: dict[str, Any],
    runtime: Any,
    *,
    correction_evidence: list[dict[str, Any]] | None = None,
    replica_registers: dict[str, dict[str, list[str]]] | None = None,
) -> dict[str, Any]:
    """Raw measured contrasts with simultaneous bounded-shot intervals across jobs.

    A record that declares covariance bounds carries an assumption the
    analysis tests on its own data: n21_exact_planning.covariance_falsifier
    reads replica_registers, each PUB's shot-ordered registers. The declared
    bounds apply only when every bound passes; otherwise, and whenever the
    registers are absent, every endpoint takes the Hoeffding
    arbitrary-dependence radius. ``replica_covariance`` records the branch,
    the falsifier rows and each directional endpoint's power condition at
    the observed shots under the applied radius. A record that carries an
    ``empirical_bernstein`` block applies its designs to the confidence and
    detection radii and reports every radius they compose under that key,
    and withholds the analysis when the block's ``specification`` differs
    from experiment_optimizer.EMPIRICAL_BERNSTEIN.
    """
    if record.get("family_configuration", {}).get("name") == "et-row":
        from et_planning import collected

        return collected(record, correction_evidence, executed, runtime)
    if record.get("family_configuration", {}).get("name") == "folded-correction":
        import correction_collection

        return correction_collection.analyze(record, correction_evidence, executed, runtime)
    contracts = record.get("observable_contracts", [])
    if not contracts:
        return {}
    required = sorted({term["member"] for contract in contracts for term in contract["terms"]})
    missing = sorted(set(required) - distributions.keys())
    if missing:
        return {"withheld": f"missing measured members {missing}"}
    missing_execution = sorted(set(required) - executed.keys())
    if missing_execution:
        return {"withheld": f"missing execution evidence {missing_execution}"}
    reason = runtime._comparisons_withheld(required, executed)
    if reason:
        return {"withheld": reason}
    endpoints = tuple(
        ObservableContract(
            **{key: value for key, value in contract.items() if key != "terms"},
            terms=tuple(
                ObservableTerm(term["member"], tuple(law_encoding.dense(term["values"])), term["sign"])
                for term in contract["terms"]
            ),
        )
        for contract in contracts
    )
    by_pub: dict[str, dict[str, tuple[tuple[float, ...], ...]]] = {}
    for member in required:
        by_pub.setdefault(executed[member]["pub"], {})[member] = tuple(
            tuple(map(float, distribution)) for distribution in distributions[member]
        )
    try:
        if "pub_shots" in record:
            shot_map = record["pub_shots"]
            if not isinstance(shot_map, dict) or any(
                type(value) is not int or value <= 0 for value in shot_map.values()
            ):
                raise ValueError("record PUB shots must be positive integers")
            declared_pubs = {pub["name"] for pub in record.get("execution_pubs", [])}
            if set(shot_map) != declared_pubs:
                raise ValueError("record PUB shot map differs from the complete execution manifest")
            for member in required:
                execution = executed[member]
                actual_shots = execution.get("shots")
                if type(actual_shots) is not int or actual_shots != shot_map.get(execution["pub"]):
                    raise ValueError(f"{member}: validated measured shots differ from the approved PUB allocation")
            pubs = tuple(ObservedPub(name, members, shot_map[name]) for name, members in by_pub.items())
        else:
            pubs = tuple(ObservedPub(name, members, int(record["shots"])) for name, members in by_pub.items())
        # The designs apply only under the rule the record preregistered; a
        # record whose rule differs from EMPIRICAL_BERNSTEIN withholds its
        # analysis, as the case renderer refuses to state it.
        block = record.get("empirical_bernstein")
        if block is not None and (not isinstance(block, dict) or block.get("specification") != EMPIRICAL_BERNSTEIN):
            raise ValueError(
                "record empirical-Bernstein specification differs from experiment_optimizer.EMPIRICAL_BERNSTEIN"
            )
        bernstein = tuple(EmpiricalBernsteinDesign(**design) for design in (block or {}).get("designs", []))
        bounds = record.get("covariance_bounds", [])
        if not bounds:
            analysis = analyze_observations(pubs, endpoints, (), bernstein).as_dict()
            return analysis | _bernstein_status(record, pubs, endpoints, (), bernstein, analysis)
        falsifier = n21_exact_planning.covariance_falsifier(record, replica_registers, distributions)
        # The record's planned allowance sized the run; collection replaces it
        # with the measured excess of the UCL over the declared projection.
        covariance = (
            ()
            if falsifier["branch"] == "hoeffding_fallback"
            else tuple(
                CovarianceBound(
                    bound["observable_name"],
                    bound["pub_name"],
                    tuple(bound["labels"]),
                    tuple(tuple(float(value) for value in row) for row in bound["matrix"]),
                    bound["assumption"],
                    variance_allowance=row["variance_used"] - row["declared_projection"],
                    falsifier_tail=row["tail"],
                )
                for bound, row in zip(bounds, falsifier["bounds"], strict=True)
            )
        )
        analysis = analyze_observations(pubs, endpoints, covariance, bernstein).as_dict()
        analysis["replica_covariance"] = falsifier | {
            "alpha_split": [
                {
                    "name": endpoint.name,
                    "alpha": endpoint.alpha,
                    "falsifier_tail": (
                        spent := math.fsum(b.falsifier_tail for b in covariance if b.observable_name == endpoint.name)
                    ),
                    "confidence_tail": endpoint.alpha - spent,
                }
                for endpoint in endpoints
            ],
            "power": _power_status(record, pubs, endpoints, covariance, analysis, bernstein),
        }
        return analysis | _bernstein_status(record, pubs, endpoints, covariance, bernstein, analysis)
    except ValueError as error:
        return {"withheld": f"invalid measured family data: {error}"}


def _bernstein_status(
    record: dict[str, Any],
    pubs: tuple[ObservedPub, ...],
    endpoints: tuple[ObservableContract, ...],
    covariance: tuple[CovarianceBound, ...],
    bernstein: tuple[EmpiricalBernsteinDesign, ...],
    analysis: dict[str, Any],
) -> dict[str, Any]:
    """The empirical-Bernstein block of an opted-in collection: every radius it composes and the power condition."""
    if not bernstein:
        return {}
    return {
        "empirical_bernstein": {
            "specification": record["empirical_bernstein"]["specification"],
            "endpoints": observed_empirical_bernstein(pubs, endpoints, covariance, bernstein),
            "power": _power_status(record, pubs, endpoints, covariance, analysis, bernstein),
        }
    }


def _power_status(
    record: dict[str, Any],
    pubs: tuple[ObservedPub, ...],
    endpoints: tuple[ObservableContract, ...],
    covariance: tuple[CovarianceBound, ...],
    analysis: dict[str, Any],
    bernstein: tuple[EmpiricalBernsteinDesign, ...] = (),
) -> list[dict[str, Any]]:
    """Each directional endpoint's detection plus power radius at the observed shots against its planned effect."""
    optimization = record.get("optimization", {})
    planned = {
        observable["name"]: observable
        for candidate in optimization.get("candidates", [])
        if candidate["name"] == optimization.get("selected")
        for observable in candidate["observables"]
    }
    radii = observation_power_radii(pubs, endpoints, covariance, bernstein)
    contracts = {contract.name: contract for contract in endpoints}
    rows = []
    for row in analysis["observables"]:
        name = row["name"]
        if name not in radii:
            continue
        effect = planned.get(name, {}).get("effect_used_for_power")
        total = row["detection_radius"] + radii[name]
        rows.append(
            {
                "name": name,
                "power": contracts[name].power,
                "planned_effect": effect,
                "detection_radius": row["detection_radius"],
                "power_radius": radii[name],
                "underpowered": None if effect is None else total > effect,
            }
        )
    return rows
