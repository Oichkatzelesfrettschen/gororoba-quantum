"""Fit candidate error mechanisms to a collected N=21 orbit feed-forward run.

The logical circuit is evolved exactly as a five-qubit density matrix:
control, the one-hot work bits for 1, 4 and 16, and a record qubit that
copies the first measurement. Copying the control into the record and then
dephasing both reproduces a projective measurement whose recorded bit drives
the feed-forward phase, so a classical flip channel on the record is an
assignment error that reaches both the stored bit and the correction. Each
model adds one mechanism to a two-parameter depolarizing baseline (one
strength per multiplier round) and is fitted to the eight measured cells of
both arms by maximum likelihood. The deviance G2 = 2 sum n log(n / N p)
ranks the mechanisms. Eight alternatives are compared in every pair, so a
deviance reduction counts at family-wise alpha 0.05 only above the
chi-square quantile at 0.05 / (8 x pairs) for the mechanism's added
parameters (Bonferroni across alternatives and pairs).

Physical roles come from the circuits that ran: the control is the writer of
the first measurement, and a Z probe inserted where each placed qubit's
scheduled window idle begins identifies, through exact branch probabilities
of the archived ISA, which qubit holds the work bit for 1 and which for 16.
Routing can move logical qubits away from their initial layout.

Window exposure is also fitted through the archived ISA itself:
window_segments lists the idle intervals each qubit plays across the
control's measurement-to-feed-forward window, CompiledLaw evaluates the exact
compiled law with one static detuning rotation per interval under the
depolarizing and assignment nuisances, and piecewise_fit compares the
piecewise exposure with the single gap at one rate per coupled qubit.

Usage: "$PYTHON" scripts/n21_orbit_rca.py RUN_DIR [--out FILE]; --check RUN_DIR regenerates
RUN_DIR/rca-mechanism-fit.json and requires agreement of the induced laws,
likelihoods, decisions and provenance. Each pair-mechanism parameter vector
must reproduce its own stored laws; optimizer coordinates are reported without imposing
a coordinate precision absent from the fitting procedure.

--between-arm RUN_DIR [--out FILE] evaluates the preregistered between-arm
contracts of an n21-orbit-rca run (contract_results): the window_delay phase
slope, the extra_readout dephasing bound and the window_echo restoration, at
family-wise alpha split over the three, each only when every member carries
one resolved coupling (admissibility). T2 and assignment rates come from
the calibration in force at each PUB's execution start where collect.json
retains it, else from plan time (execution_calibration); the report names
the source per member and this file's sha256, and --expected-analyzer-sha256
HEX refuses another analyzer.

A run planned with --init-herald measures every qubit into a herald
register before the program. window_roles drops the herald readouts and
their measure plays, so admissibility is that of the unheralded twin, and
--between-arm reports the herald admission beside it (herald_admission): a
level-0.05 test that every member spread of the initial excitation is at
most herald_bound(n), the spread that moves a magnitude contract by a
quarter of its minimum detectable deficit (B = 0.001361 at 27,648 shots;
derivation in herald_bound). Every member must read a herald qubit
through one assignment channel; a refused or unevaluable herald reads every
contract not_admissible. An admitted herald's simultaneous upper limits
leave the magnitude contracts a possible shift, contract_shift_upper_limit,
which counts against every magnitude contract's pass before it
decides, so a heralded pass holds for every spread the herald leaves
possible. --self-test-herald checks the sensitivity
coefficients, the twin roles on the retained schedule and the admission
test's operating characteristic. The mechanism fit reads unheralded runs.
"""

from __future__ import annotations

import argparse
import contextlib
import functools
import hashlib
import io
import json
import math
import sys
from collections import Counter
from collections.abc import Callable
from pathlib import Path
from typing import Any
from unittest import mock

import numpy as np
from scipy.optimize import minimize
from scipy.stats import chi2, norm

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gororoba_quantum"))

import ibm_account  # noqa: E402
import parallel  # noqa: E402

FAMILY_ALPHA = 0.05

CONTROL, ONE, FOUR, SIXTEEN, RECORD = range(5)
WORK = (ONE, FOUR, SIXTEEN)
DIMENSION = 32
REGISTER = "g0_r0_phase"

_I = np.eye(2, dtype=complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_Z = np.diag([1.0, -1.0]).astype(complex)
_H = np.array([[1, 1], [1, -1]], dtype=complex) / math.sqrt(2)


@functools.cache
def _embedding(qubits: tuple[int, ...], size: int = DIMENSION) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Rows, columns, and local output and input indices of every entry a gate on qubits occupies."""
    count = len(qubits)
    rows, columns, outs, ins = [], [], [], []
    for column in range(size):
        local_in = sum(((column >> qubit) & 1) << index for index, qubit in enumerate(qubits))
        rest = column
        for qubit in qubits:
            rest &= ~(1 << qubit)
        for local_out in range(1 << count):
            rows.append(rest | sum(((local_out >> index) & 1) << qubit for index, qubit in enumerate(qubits)))
            columns.append(column)
            outs.append(local_out)
            ins.append(local_in)
    return np.array(rows), np.array(columns), np.array(outs), np.array(ins)


def _embed(gate: np.ndarray, qubits: tuple[int, ...], size: int = DIMENSION) -> np.ndarray:
    """Full size x size operator for a gate on qubits (little-endian, qubit 0 least significant).

    Each (row, column) pair occurs once in the embedding, so the assignment
    places every gate entry exactly.
    """
    rows, columns, outs, ins = _embedding(qubits, size)
    full = np.zeros((size, size), dtype=complex)
    full[rows, columns] = gate[outs, ins]
    return full


def _cswap() -> np.ndarray:
    gate = np.eye(8, dtype=complex)
    gate[[3, 5]] = gate[[5, 3]]
    return gate


def _controlled_phase(angle: float) -> np.ndarray:
    return np.diag([1, 1, 1, np.exp(1j * angle)]).astype(complex)


def _cx() -> np.ndarray:
    gate = np.eye(4, dtype=complex)
    gate[[1, 3]] = gate[[3, 1]]
    return gate


class Evolution:
    def __init__(self) -> None:
        self.rho = np.zeros((DIMENSION, DIMENSION), dtype=complex)
        self.rho[0, 0] = 1.0

    def unitary(self, gate: np.ndarray, qubits: tuple[int, ...]) -> None:
        full = _embed(gate, qubits)
        self.rho = full @ self.rho @ full.conj().T

    def channel(self, kraus: list[np.ndarray], qubit: int) -> None:
        full = [_embed(operator, (qubit,)) for operator in kraus]
        self.rho = sum(operator @ self.rho @ operator.conj().T for operator in full)

    def branch_window(self, branch: int, angle: float, loss: float) -> None:
        """Phase and dephase the work bit for 1 only where the recorded first bit equals branch.

        loss scales the coherence of that bit by 1 - loss inside the branch.
        """
        selected = np.diag([1.0, 0.0] if branch == 0 else [0.0, 1.0]).astype(complex)
        other = np.eye(2, dtype=complex) - selected
        phase = np.diag([1.0, np.exp(1j * angle)]).astype(complex)
        # Local operators act on (ONE, RECORD) with ONE as the low bit.
        self.unitary(np.kron(selected, phase) + np.kron(other, _I), (ONE, RECORD))
        weight = min(max(loss, 0.0), 1.0) / 2
        if weight:
            kraus = [
                np.kron(other, _I) + np.kron(selected, math.sqrt(1 - weight) * _I),
                np.kron(selected, math.sqrt(weight) * _Z),
            ]
            full = [_embed(operator, (ONE, RECORD)) for operator in kraus]
            self.rho = sum(operator @ self.rho @ operator.conj().T for operator in full)

    def depolarize(self, strength: float, qubits: tuple[int, ...]) -> None:
        weight = max(0.0, min(1.0, strength))
        for qubit in qubits:
            self.channel(
                [math.sqrt(1 - 3 * weight / 4) * _I] + [math.sqrt(weight / 4) * pauli for pauli in (_X, _Y, _Z)],
                qubit,
            )


def _flip(read_one_given_zero: float, read_zero_given_one: float) -> list[np.ndarray]:
    a = min(max(read_one_given_zero, 0.0), 1.0)
    b = min(max(read_zero_given_one, 0.0), 1.0)
    return [
        np.diag([math.sqrt(1 - a), math.sqrt(1 - b)]).astype(complex),
        np.array([[0, math.sqrt(b)], [math.sqrt(a), 0]], dtype=complex),
    ]


def _dephase() -> list[np.ndarray]:
    return [np.diag([1.0, 0.0]).astype(complex), np.diag([0.0, 1.0]).astype(complex)]


def distribution(params: dict[str, float], feed_forward: bool, window: np.ndarray | None = None) -> np.ndarray:
    """Labeled law over y = b0 + 2 b1 under the parameterized error model.

    window, when given, is the 8x8 unitary the work qubits for 1, 4 and 16
    undergo between the first measurement and the second round.
    cphase_one applies a phase to the work bit for 1 when the recorded first
    bit is 1.
    """
    state = Evolution()
    state.unitary(_X, (ONE,))
    state.unitary(_H, (CONTROL,))
    state.unitary(_cswap(), (CONTROL, ONE, FOUR))
    state.unitary(_cswap(), (CONTROL, FOUR, SIXTEEN))
    state.depolarize(params.get("round1", 0.0), (CONTROL, *WORK))
    state.unitary(_H, (CONTROL,))
    state.unitary(_cx(), (CONTROL, RECORD))
    state.channel(_dephase(), CONTROL)
    state.channel(_dephase(), RECORD)
    # The window acts on the branch the measurement projected; an assignment
    # error then changes only the stored bit and the feed-forward decision.
    for branch in (0, 1):
        angle, loss = params.get(f"phase_b{branch}", 0.0), params.get(f"loss_b{branch}", 0.0)
        if angle or loss:
            state.branch_window(branch, angle, loss)
    state.channel(_flip(params["mid_e01"], params["mid_e10"]), RECORD)
    failure = min(max(params.get("reset_failure", 0.0), 0.0), 1.0)
    state.channel(
        [
            np.array([[1, 0], [0, 0]], dtype=complex),
            np.array([[0, math.sqrt(1 - failure)], [0, 0]], dtype=complex),
            np.array([[0, 0], [0, math.sqrt(failure)]], dtype=complex),
        ],
        CONTROL,
    )
    damping = min(max(params.get("window_t1", 0.0), 0.0), 1.0)
    dephasing = min(max(params.get("window_t2", 0.0), 0.0), 1.0)
    for qubit in WORK:
        if damping:
            state.channel(
                [
                    np.array([[1, 0], [0, math.sqrt(1 - damping)]], dtype=complex),
                    np.array([[0, math.sqrt(damping)], [0, 0]], dtype=complex),
                ],
                qubit,
            )
        if dephasing:
            state.channel([math.sqrt(1 - dephasing / 2) * _I, math.sqrt(dephasing / 2) * _Z], qubit)
    for qubit, key in ((ONE, "phase_one"), (SIXTEEN, "phase_sixteen")):
        if params.get(key):
            state.unitary(np.diag([1, np.exp(1j * params[key])]).astype(complex), (qubit,))
    if window is not None:
        state.unitary(window, (ONE, FOUR, SIXTEEN))
    if params.get("cphase_one"):
        state.unitary(_controlled_phase(params["cphase_one"]), (RECORD, ONE))
    state.unitary(_H, (CONTROL,))
    state.unitary(_cswap(), (CONTROL, FOUR, SIXTEEN))
    state.unitary(_cswap(), (CONTROL, ONE, FOUR))
    state.depolarize(params.get("round2", 0.0), (CONTROL, *WORK))
    if feed_forward:
        state.unitary(_controlled_phase(-math.pi / 2), (RECORD, CONTROL))
    if params.get("control_phase"):
        state.unitary(np.diag([1, np.exp(1j * params["control_phase"])]).astype(complex), (CONTROL,))
    state.unitary(_H, (CONTROL,))
    state.channel(_dephase(), CONTROL)
    state.channel(_flip(params["end_e01"], params["end_e10"]), CONTROL)
    diagonal = np.real(np.diag(state.rho))
    law = np.zeros(4)
    for index, weight in enumerate(diagonal):
        law[((index >> RECORD) & 1) + 2 * ((index >> CONTROL) & 1)] += weight
    return law / law.sum()


def is_orbit(name: str) -> bool:
    """Whether a member is an orbit member: every member except a spectator Ramsey member (SPECTATOR_MEMBERS).

    Records of n21-orbit-feedback name their pair without a variant, so the
    test names the spectators rather than listing the orbit variants.
    """
    return name not in SPECTATOR_MEMBERS


def _group(run: Path) -> dict[str, Any]:
    group: dict[str, Any] = json.loads((run / "record.json").read_text())["groups"][0]
    if len(group["replicas"]) != 1:
        raise RuntimeError("the RCA fit reads one replica; the n21-orbit-rca family plans one")
    return group


def raw_pubs(run: Path) -> list[dict[str, Any]]:
    """Raw PUB payloads in member order, bound to the submission manifest and the collection ledger.

    record.json's submission names the one job the run sent, each PUB's name
    and the member each PUB carries. collect.json, raw/<job>/index.json and
    every raw PUB must name that job and those PUBs in manifest order, and
    each raw file must match the sha256 collection retained, so a collection
    or raw tree taken from another run with the same PUB count is refused.
    """
    submitted = json.loads((run / "record.json").read_text())["submission"]["jobs"]
    if len(submitted) != 1:
        raise RuntimeError(f"the RCA fit reads one job; the record submitted {len(submitted)}")
    manifest = submitted[0]
    pubs = manifest["pubs"]
    members = [member["name"] for member in _group(run)["members"]]
    carried = [[component["member"] for component in pub["components"]] for pub in pubs]
    if carried != [[member] for member in members]:
        raise RuntimeError(f"the submitted PUBs carry {carried}, not the members {members} one per PUB")
    jobs = json.loads((run / "collect.json").read_text())[0]["jobs"]
    (job,) = jobs
    if job != manifest["job_id"]:
        raise RuntimeError(f"collect.json names job {job}; the record submitted {manifest['job_id']}")
    names = [pub["name"] for pub in pubs]
    timing = jobs[job].get("pub_timing")
    if timing is not None and sorted(timing) != sorted(names):
        raise RuntimeError(f"collect.json times PUBs {sorted(timing)}; the record submitted {names}")
    directory = run / "raw" / job
    index = json.loads((directory / "index.json").read_text())
    indexed = index["files"]
    ledger = jobs[job].get("raw")
    if index.get("job_id") != job or (ledger is not None and ledger["files"] != indexed):
        raise RuntimeError(f"raw/{job}/index.json differs from the collection's raw ledger")
    raw = sorted(name for name in indexed if name.startswith("pub_"))
    if raw != [f"pub_{position:02d}.json" for position in range(len(names))]:
        raise RuntimeError(f"raw/{job} holds {raw}; the record submitted {len(names)} PUBs")
    payloads = []
    for position, name in enumerate(names):
        path = directory / f"pub_{position:02d}.json"
        if hashlib.sha256(path.read_bytes()).hexdigest() != indexed[path.name]:
            raise RuntimeError(f"{path.name} differs from the sha256 retained by collection")
        payload = json.loads(path.read_text())
        if payload.get("pub_index") != position or payload.get("pub_name") != name:
            raise RuntimeError(
                f"{path.name} carries PUB {payload.get('pub_index')} {payload.get('pub_name')}; "
                f"the manifest places {name} at {position}"
            )
        payloads.append(payload)
    return payloads


def _circuits(run: Path) -> list[Any]:
    from qiskit import qpy

    submitted = json.loads((run / "record.json").read_text())["submission"]["qpy_archive_sha256"]
    if hashlib.sha256((run / "isa.qpy").read_bytes()).hexdigest() != submitted:
        raise RuntimeError("isa.qpy differs from the submitted circuit archive")

    with (run / "isa.qpy").open("rb") as handle:
        return list(qpy.load(handle))


def measured_pairs(run: Path) -> dict[str, dict[str, np.ndarray]]:
    """Counts per feed-forward pair, keyed by the member name without its arm suffix.

    PUB i carries the record's member i; the archived ISA confirms the order,
    since only the feed-forward member contains an if_else. Spectator
    Ramsey members carry no pair and stay out (is_orbit).
    """
    members = [member["name"] for member in _group(run)["members"]]
    circuits = _circuits(run)
    if len(circuits) != len(members):
        raise RuntimeError("archived circuits and record members differ in number")
    pairs: dict[str, dict[str, np.ndarray]] = {}
    for index, (name, circuit, payload) in enumerate(zip(members, circuits, raw_pubs(run), strict=True)):
        if not is_orbit(name):
            continue
        arm = "no_feedback" if name.endswith("_no_feedback") else "feedback"
        if ("if_else" in circuit.count_ops()) != (arm == "feedback"):
            raise RuntimeError(f"PUB {index} feed-forward structure differs from member {name}")
        bits = payload["registers"][REGISTER]["bitstrings"]
        tally = Counter(int(value[1]) + 2 * int(value[0]) for value in bits)
        pairs.setdefault(name.removesuffix("_" + arm), {})[arm] = np.array(
            [tally[label] for label in range(4)], dtype=float
        )
    return pairs


_VIRTUAL = frozenset({"rz", "barrier", "delay", "if_else"})


def _plays(payload: dict[str, Any]) -> list[tuple[int, int, str, int]]:
    """Pulse rows of the returned schedule; an absent or malformed table raises ValueError."""
    try:
        timing = payload["metadata"]["compilation"]["scheduler_timing"]["timing"]
        rows = [line.split(",") for line in timing.splitlines()]
        if not rows or any(len(row) < 6 for row in rows):
            raise ValueError("scheduler timing table is empty or malformed")
    except (KeyError, TypeError) as error:
        raise ValueError(f"scheduler timing is unavailable: {error}") from error
    return [
        (int(row[3]), int(row[4]), row[1].split("_")[0], int(row[2].removeprefix("Qubit ")))
        for row in rows
        if row[5] == "play" and row[2].startswith("Qubit ") and not row[1].startswith(("INIT", "FINI"))
    ]


def _probed(circuit: Any, positions: dict[int, int], angles: dict[int, float]) -> np.ndarray:
    """Exact compiled phase law with rz(angle) after the positions[q]-th physical pulse on each probed wire."""
    from qiskit import QuantumCircuit

    from qpe_diagnostics import ideal_compiled_probabilities, phase_marginal

    probed = QuantumCircuit(*circuit.qregs, *circuit.cregs)
    seen = dict.fromkeys(angles, 0)
    for instruction in circuit.data:
        probed.append(instruction)
        if instruction.operation.name in _VIRTUAL:
            continue
        for bit in instruction.qubits:
            qubit = circuit.find_bit(bit).index
            if qubit in angles:
                seen[qubit] += 1
                if seen[qubit] == positions[qubit]:
                    probed.rz(angles[qubit], qubit)
    return phase_marginal(ideal_compiled_probabilities(probed))


def _branch_law(feed_forward: bool, phases: dict[int, float]) -> np.ndarray:
    return np.array(
        distribution(_readout(0.0, 0.0) | {f"phase_b{b}": phase for b, phase in phases.items()}, feed_forward)
    )


def herald_program(circuit: Any) -> tuple[Any, dict[int, int]]:
    """circuit without its herald readouts, and per wire the number of herald readouts it plays first.

    Each herald readout is one measure play on its wire's drive channel
    (_plays keeps the drive channel only) and precedes every other physical
    instruction of that wire; a herald readout after one raises ValueError.
    """
    from qpe_diagnostics import herald_measurement

    program = circuit.copy_empty_like()
    prefix: dict[int, int] = {}
    started: set[int] = set()
    for instruction in circuit.data:
        wires = [circuit.find_bit(bit).index for bit in instruction.qubits]
        if herald_measurement(circuit, instruction):
            if wires[0] in started:
                raise ValueError(f"a herald readout on qubit {wires[0]} follows the program")
            prefix[wires[0]] = prefix.get(wires[0], 0) + 1
            continue
        program.append(instruction)
        if instruction.operation.name not in _VIRTUAL:
            started.update(wires)
    return program, prefix


def _without_prefix(plays: list[tuple[int, int, str, int]], prefix: dict[int, int]) -> list[tuple[int, int, str, int]]:
    """plays without each wire's first prefix[wire] pulses, which must be the herald's measure plays."""
    dropped: set[tuple[int, int, str, int]] = set()
    for wire, count in prefix.items():
        first = sorted(play for play in plays if play[3] == wire)[:count]
        if len(first) != count or any(name != "measure" for _start, _length, name, _wire in first):
            raise ValueError(f"the schedule's first pulses on qubit {wire} are not its {count} herald readouts")
        dropped.update(first)
    return [play for play in plays if play not in dropped]


def member_roles(
    feed_forward: bool, circuit: Any, payload: dict[str, Any], placed: list[int], strip_herald: bool = True
) -> dict[str, Any]:
    """window_roles of one member: control, terminal writer, coupling, windows and unresolved probes.

    strip_herald removes the herald readouts from the instructions and their
    measure plays from the schedule, so a heralded member reads the roles of
    its unheralded twin on the same schedule minus the herald prefix.
    """
    from qpe_diagnostics import ideal_compiled_probabilities, phase_marginal

    probe = 0.7
    branch_sets = ((0,), (1,), (0, 1))
    prefix: dict[int, int] = {}
    unresolved: list[str] = []
    if strip_herald:
        try:
            circuit, prefix = herald_program(circuit)
        except ValueError as error:
            unresolved.append(str(error))
    writers = [circuit.find_bit(i.qubits[0]).index for i in circuit.data if i.operation.name == "measure"]
    writer = writers[0]
    try:
        if unresolved:
            raise ValueError(unresolved[0])
        plays = _without_prefix(_plays(payload), prefix)
    except ValueError as error:
        # Counts and writers need no schedule; only window exposure does.
        return {
            "control": writer,
            "terminal": writers[-1],
            "coupling": {},
            "windows": {},
            "unresolved": unresolved or [str(error)],
        }
    opening = min(start for start, _length, name, wire in plays if wire == writer and name == "measure")
    base = phase_marginal(ideal_compiled_probabilities(circuit))
    windows: dict[int, dict[str, Any]] = {}
    positions: dict[int, int] = {}
    coupling: dict[int, dict[int, int]] = {}
    for qubit in placed:
        if qubit == writer:
            continue
        pulses = sorted((start, length, name) for start, length, name, wire in plays if wire == qubit)
        before = [start + length for start, length, _name in pulses if start + length <= opening]
        after = [start for start, _length, name in pulses if start >= opening and name != "x"]
        if not before or not after:
            continue
        windows[qubit] = {
            "before": max(before),
            "after": min(after),
            "x": [
                [start, length] for start, length, name in pulses if max(before) <= start < min(after) and name == "x"
            ],
        }
        # The probe counts circuit instructions while the schedule lists
        # pulses; the two align only where every instruction on the wire
        # plays one pulse (sx, x, cz), which the comparison requires.
        instructions = [
            instruction.operation.name
            for instruction in circuit.data
            if instruction.operation.name not in _VIRTUAL
            and qubit in [circuit.find_bit(bit).index for bit in instruction.qubits]
        ]
        if len(instructions) != len(pulses) or not set(instructions) <= {"sx", "x", "cz"}:
            unresolved.append(f"qubit {qubit} holds instructions that do not map one-to-one onto pulses")
            continue
        positions[qubit] = sum(1 for start, length, _name in pulses if start + length <= max(before))
        shift = _probed(circuit, positions, {qubit: probe})
        if np.allclose(shift, base, atol=1e-9):
            continue
        matches = [
            (sign, branches)
            for sign in (1, -1)
            for branches in branch_sets
            if np.allclose(shift, _branch_law(feed_forward, dict.fromkeys(branches, sign * probe)), atol=1e-9)
        ]
        if not matches or len({branches for _sign, branches in matches}) != 1:
            unresolved.append(f"a Z probe on qubit {qubit} matches no single window phase")
            continue
        signs = {sign for sign, _branches in matches}
        coupling[qubit] = {branch: (next(iter(signs)) if len(signs) == 1 else 0) for branch in matches[0][1]}
    if not coupling and not unresolved:
        unresolved.append("no placed qubit carries the work superposition in the window")
    ambiguous = [q for q, branches in coupling.items() if 0 in branches.values()]
    if ambiguous:
        anchor = ambiguous[0]
        coupling[anchor] = dict.fromkeys(coupling[anchor], 1)
        for qubit in ambiguous[1:]:
            joint = _probed(circuit, positions, {anchor: probe, qubit: probe})
            for sign in (1, -1):
                trial = {**coupling, qubit: dict.fromkeys(coupling[qubit], sign)}
                phases = {
                    b: sum(
                        probe * branches[b] for q, branches in trial.items() if q in (anchor, qubit) and b in branches
                    )
                    for b in (0, 1)
                }
                if np.allclose(joint, _branch_law(feed_forward, phases), atol=1e-9):
                    coupling[qubit] = trial[qubit]
                    break
            else:
                unresolved.append(f"a joint probe with qubit {anchor} fits neither relative sign of qubit {qubit}")
    return {
        "control": writer,
        "terminal": writers[-1],
        "coupling": coupling,
        "windows": windows,
        "unresolved": unresolved,
    }


def window_roles(run: Path) -> dict[str, dict[str, Any]]:
    """Physical control, branch couplings, and scheduled windows of each member.

    The window of a placed qubit runs from the end of its last pulse before
    the control's first measurement to its first non-X pulse after it; X
    pulses inside it are echo pulses. Work-only gates commute with the
    control's measurement, so the compiler can finish a multiplier after it,
    and which qubit holds the work superposition then depends on the member
    and on the recorded first bit. A Z rotation at the start of a qubit's
    window changes the exact compiled branch law as a phase of +/- the
    rotation on the work bit for 1 in branch 0, branch 1, or both; that
    match is the qubit's coupling. Without feed-forward the law is even in
    the phase, so a joint probe of two qubits fixes their relative sign.

    The control's first measurement is its first write of the phase register:
    an initialization herald's readouts and their measure plays leave the
    instructions and the schedule first (member_roles), so the herald plays
    no part in the windows, the probes or the one-to-one pulse comparison.
    Only orbit members carry a window coupling (is_orbit).
    """
    group = _group(run)
    placed = sorted(int(qubit) for qubit in group["replicas"][0]["physical_qubits"])
    return {
        member["name"]: member_roles(not member["name"].endswith("_no_feedback"), circuit, payload, placed)
        for member, circuit, payload in zip(group["members"], _circuits(run), raw_pubs(run), strict=True)
        if is_orbit(member["name"])
    }


def signed_exposure(
    run: Path, roles: dict[str, dict[str, Any]] | None = None
) -> dict[str, dict[int, dict[int, float]]]:
    """Per member and branch, the coupling-weighted signed idle time in dt of each window qubit.

    A quasi-static detuning adds phase in proportion to idle time inside the
    window; each echo X pulse reverses the sign of later idle time, and the
    probe coupling maps the qubit's phase onto the phase of the work bit for 1
    in the branches where the qubit holds the superposition.
    """
    return role_exposure(window_roles(run) if roles is None else roles)


def role_exposure(roles: dict[str, dict[str, Any]]) -> dict[str, dict[int, dict[int, float]]]:
    """signed_exposure of window_roles output already in hand."""
    exposure: dict[str, dict[int, dict[int, float]]] = {}
    for name, role in roles.items():
        member_exposure: dict[int, dict[int, float]] = {0: {}, 1: {}}
        for qubit, branches in role["coupling"].items():
            window = role["windows"][qubit]
            sign, cursor, total = 1.0, window["before"], 0.0
            # Idle time excludes each driven echo pulse; the sign flips after it.
            for start, length in window["x"]:
                total += sign * (start - cursor)
                sign, cursor = -sign, start + length
            idle = total + sign * (window["after"] - cursor)
            for branch, coupling_sign in branches.items():
                member_exposure[branch][qubit] = coupling_sign * idle
        exposure[name] = member_exposure
    return exposure


TARGET_SNAPSHOT = Path(__file__).resolve().parents[1] / "docs" / "evidence" / "heron_platform" / "targets.json"


def dt_source(run: Path) -> tuple[float, str]:
    """The backend sample time and its source.

    The family configuration's value comes first, then the retained Heron
    Target snapshot's dt for the record's backend (gates core-254 and
    core-255 recompute it from the live Targets), then the live backend
    Target, which needs the IBM service.
    """
    record = json.loads((run / "record.json").read_text())
    retained = record.get("family_configuration", {}).get("dt_seconds")
    if retained:
        return float(retained), "record family_configuration.dt_seconds"
    backend = record["groups"][0]["backend"]
    if TARGET_SNAPSHOT.exists():
        snapshot = json.loads(TARGET_SNAPSHOT.read_text())["backends"].get(backend, {})
        if snapshot.get("dt"):
            return float(snapshot["dt"]), f"docs/evidence/heron_platform/targets.json backends.{backend}.dt"
    from qiskit_ibm_runtime import QiskitRuntimeService

    return float(ibm_account.open_service(QiskitRuntimeService).backend(backend).target.dt), f"live {backend} Target dt"


def dt_seconds(run: Path) -> float:
    """The backend sample time (dt_source without its provenance)."""
    return dt_source(run)[0]


class JointObjective:
    """Deviance of the joint quasi-static detuning model over every pair at one parameter vector."""

    def __init__(
        self,
        pairs: dict[str, dict[str, np.ndarray]],
        readouts: dict[str, dict[str, float]],
        exposure: dict[str, dict[int, dict[int, float]]],
        names: list[str],
        dt_us: float,
    ) -> None:
        self.pairs, self.readouts, self.exposure, self.names, self.dt_us = pairs, readouts, exposure, names, dt_us

    def member_params(self, vector: np.ndarray, member: str) -> dict[str, float]:
        values = dict(zip(self.names, map(float, vector), strict=True))
        params = self.readouts[member] | {"round1": values["round1"], "round2": values["round2"]}
        for branch, entries in self.exposure[member].items():
            times = {qubit: value * self.dt_us for qubit, value in entries.items()}
            params[f"phase_b{branch}"] = sum(values[f"mean_{q}"] * t for q, t in times.items())
            params[f"loss_b{branch}"] = 1.0 - math.exp(-sum((values[f"sd_{q}"] * t) ** 2 for q, t in times.items()) / 2)
        return params

    def __call__(self, vector: np.ndarray) -> float:
        total = 0.0
        for pair, counts in self.pairs.items():
            for arm, feed_forward in (("feedback", True), ("no_feedback", False)):
                observed = counts[arm]
                law = distribution(self.member_params(vector, f"{pair}_{arm}"), feed_forward)
                expected = np.clip(law, 1e-12, None) * observed.sum()
                positive = observed > 0
                total += 2 * float(np.sum(observed[positive] * np.log(observed[positive] / expected[positive])))
        return total


class LocalSearch:
    """L-BFGS-B from one start inside fixed bounds: the minimum and its location."""

    def __init__(self, objective: Any, bounds: list[tuple[float, float]]) -> None:
        self.objective, self.bounds = objective, bounds

    def __call__(self, start: list[float]) -> tuple[float, list[float]]:
        result = minimize(self.objective, np.array(start), method="L-BFGS-B", bounds=self.bounds)
        return float(result.fun), [float(value) for value in result.x]


def _lowest(results: list[tuple[float, list[float]]]) -> tuple[float, list[float]]:
    """The first result of least deviance, as a serial scan with a strict comparison keeps it."""
    best = results[0]
    for result in results[1:]:
        if result[0] < best[0]:
            best = result
    return best


def static_refit(
    objective: Any,
    bounds: list[tuple[float, float]],
    winner: list[float],
    seeds: list[tuple[float, ...]],
    count: int,
) -> tuple[float, list[float]]:
    """The static-detuning-only optimum: spreads fixed at zero, searched from the full winner and every seed.

    Exposures of several microseconds wrap each mean phase, so the static
    model has a basin per period; a search from the full winner's means
    alone stays in that winner's basin, while the grid seeds reach the others.
    """
    zeros = [0.0] * count
    starts = [[*winner[: 2 + count], *zeros], *([0.12, 0.0, *means, *zeros] for means in seeds)]
    search = LocalSearch(objective, bounds[: 2 + count] + [(0.0, 0.0)] * count)
    return _lowest(parallel.ordered_map(search, starts, min_items=2))


def joint_quasistatic_fit(
    run: Path, pairs: dict[str, dict[str, np.ndarray]], readouts: dict[str, dict[str, float]]
) -> dict[str, Any]:
    """Fit a per-shot Gaussian detuning on each window qubit across every pair at once.

    For each member the phase of the work bit for 1 is sum_q mean_q s_q and
    the relative coherence is exp(-sum_q sd_q^2 s_q^2 / 2), with s_q the
    coupling-weighted signed exposure of physical qubit q and rates in
    radians per microsecond; the two depolarizing nuisances are shared.
    """
    roles = window_roles(run)
    unresolved = {name: role["unresolved"] for name, role in roles.items() if role["unresolved"]}
    if unresolved:
        return {"skipped": "window state is not a branch phase on the work bit for 1", "unresolved": unresolved}
    exposure = signed_exposure(run, roles)
    qubits = sorted({qubit for member in exposure.values() for branch in member.values() for qubit in branch})
    names = ["round1", "round2", *(f"mean_{q}" for q in qubits), *(f"sd_{q}" for q in qubits)]
    bounds = [(0.0, 1.0), (0.0, 1.0), *([(-5.0, 5.0)] * len(qubits)), *([(0.0, 5.0)] * len(qubits))]
    objective = JointObjective(pairs, readouts, exposure, names, dt_seconds(run) * 1e6)

    # Multi-microsecond exposures wrap the mean phase, so the mean rates have
    # many basins; a grid over both means seeds the local searches.
    import heapq
    import itertools

    # About 400 grid evaluations bound the seed search for any qubit count.
    points = max(3, round(400 ** (1 / len(qubits))))
    grid = [tuple(map(float, means)) for means in itertools.product(np.linspace(-4.5, 4.5, points), repeat=len(qubits))]
    landscape = parallel.ordered_map(
        objective, [np.array([0.12, 0.0, *means, *([0.0] * len(qubits))]) for means in grid], min_items=2
    )
    ranked = heapq.nsmallest(4, zip(landscape, grid, strict=True), key=lambda item: item[0])
    seeds = [means for _value, means in ranked]
    starts = [[0.12, 0.0, *means, *([spread] * len(qubits))] for means in seeds for spread in (0.0, 0.2)]
    best = _lowest(parallel.ordered_map(LocalSearch(objective, bounds), starts, min_items=2))
    static = static_refit(objective, bounds, best[1], seeds, len(qubits))
    cells = sum(len(counts) * 3 for counts in pairs.values())
    return {
        "parameters_rad_per_us": dict(zip(names, best[1], strict=True)),
        "deviance": best[0],
        "degrees_of_freedom": cells - len(names),
        "static_detuning_only_deviance": static[0],
        "signed_exposure_dt": {
            member: {str(branch): {str(q): t for q, t in entries.items()} for branch, entries in values.items()}
            for member, values in exposure.items()
        },
    }


_ONE_PLAY = frozenset({"sx", "x", "cz", "measure"})


def window_segments(circuit: Any, payload: dict[str, Any]) -> dict[str, Any]:
    """Idle intervals of each active qubit across the control's measurement-to-feed-forward window.

    The window opens at the control's first measurement play and closes at
    its first later play that is neither measurement nor reset, the pulse
    after which the feed-forward phase acts. Every idle interval between two
    consecutive pulses of a non-control wire that overlaps the window enters
    whole, so a work-only pulse inside the window splits that wire's exposure
    into the intervals before and after it. The single gap of window_roles,
    from the last pulse before the opening to the first non-X pulse after it,
    is the subset of intervals inside that span; its intervals always enter,
    so the piecewise set contains it. Each interval is [start, end, count] in
    dt, count being the pulses its wire plays before it. The control's window
    idles hold a measured basis state, on which a Z rotation is a
    branch-global phase. A wire whose instructions do not map one-to-one onto
    its pulses is unresolved; a missing schedule raises ValueError (_plays).
    """
    plays = _plays(payload)
    writer = next(circuit.find_bit(i.qubits[0]).index for i in circuit.data if i.operation.name == "measure")
    control = sorted((start, name) for start, _length, name, wire in plays if wire == writer)
    opening = min(start for start, name in control if name == "measure")
    later = [start for start, name in control if start >= opening and name not in ("measure", "reset")]
    if not later:
        raise ValueError("the control plays no pulse after its measurement and reset")
    closing = min(later)
    active = sorted(
        {circuit.find_bit(bit).index for i in circuit.data if i.operation.name != "barrier" for bit in i.qubits}
    )
    intervals: dict[int, list[list[int]]] = {}
    single: dict[int, list[list[int]]] = {}
    unresolved: list[str] = []
    for qubit in active:
        if qubit == writer:
            continue
        pulses = sorted((start, length, name) for start, length, name, wire in plays if wire == qubit)
        instructions = [
            i.operation.name
            for i in circuit.data
            if i.operation.name not in _VIRTUAL and qubit in [circuit.find_bit(bit).index for bit in i.qubits]
        ]
        if len(instructions) != len(pulses) or not set(instructions) <= _ONE_PLAY:
            unresolved.append(f"qubit {qubit} holds instructions that do not map one-to-one onto pulses")
            continue
        gaps: list[list[int]] = []
        end: int | None = None
        for count, (start, length, _name) in enumerate(pulses):
            if end is not None and start > end:
                gaps.append([end, start, count])
            end = start + length if end is None else max(end, start + length)
        before = [start + length for start, length, _name in pulses if start + length <= opening]
        after = [start for start, _length, name in pulses if start >= opening and name != "x"]
        spanned = [gap for gap in gaps if before and after and max(before) <= gap[0] and gap[1] <= min(after)]
        inside = [gap for gap in gaps if (gap[0] < closing and gap[1] > opening) or gap in spanned]
        if inside:
            intervals[qubit] = inside
        if spanned:
            single[qubit] = spanned
    return {
        "control": writer,
        "window": [opening, closing],
        "intervals": intervals,
        "single_gap": single,
        "unresolved": unresolved,
    }


class CompiledLaw:
    """Exact outcome law of an ISA circuit with rz(rate x duration) after chosen pulses, under nuisance channels.

    The circuit compiles once, on its active wires, into fused unitaries
    between insertions, measurements, resets and if_else blocks; a law then
    costs a few small matrix products per classical branch. insertions maps a
    physical qubit to (count, duration_us, rate_index) entries, each a Z
    rotation by rates[rate_index] x duration_us radians after that wire's
    count-th physical (non-virtual) instruction, the instruction count
    _probed uses. A measurement is terminal when no later instruction acts
    on its wire and mid-circuit otherwise, so extra_readout's repeated
    write of the first bit before the reset is mid-circuit. round1
    depolarizes every active wire where the first measurement stands in
    instruction order and round2 where the first terminal one does, the two
    multiplier rounds of distribution(); depolarizing commutes with
    single-qubit rotations, so its place relative to an insertion on the
    same wire is immaterial. A mid-circuit measurement's assignment flip
    (mid_e01, mid_e10) acts on the classical bit as it is written, so it
    reaches the if_else condition; a terminal measurement uses end_e01 and
    end_e10.
    """

    def __init__(self, circuit: Any, insertions: dict[int, list[tuple[int, float, int]]], rates: int) -> None:
        active = sorted(
            {circuit.find_bit(bit).index for i in circuit.data if i.operation.name != "barrier" for bit in i.qubits}
        )
        self.local = {qubit: index for index, qubit in enumerate(active)}
        self.size = 1 << len(active)
        self.clbits = circuit.num_clbits
        self.rates = rates
        indices = np.arange(self.size)
        bits = [(indices >> index) & 1 for index in range(len(active))]
        self.diffs = [np.subtract.outer(bit, bit).astype(float) for bit in bits]
        self.signs = [np.outer(1 - 2 * bit, 1 - 2 * bit).astype(float) for bit in bits]
        self.masks = [[np.outer(bit == value, bit == value).astype(float) for value in (0, 1)] for bit in bits]
        self.flipped = [indices ^ (1 << index) for index in range(len(active))]
        self.program: list[tuple[Any, ...]] = []
        pending = np.eye(self.size, dtype=complex)
        fused = False
        seen: Counter[int] = Counter()
        last = {
            circuit.find_bit(bit).index: position
            for position, instruction in enumerate(circuit.data)
            if instruction.operation.name not in ("barrier", "delay")
            for bit in instruction.qubits
        }
        rounds = 0
        placed = 0
        for position, instruction in enumerate(circuit.data):
            name = instruction.operation.name
            wires = [circuit.find_bit(bit).index for bit in instruction.qubits]
            if name in ("barrier", "delay"):
                continue
            if name in ("measure", "reset", "if_else") and fused:
                self.program.append(("unitary", pending))
                pending, fused = np.eye(self.size, dtype=complex), False
            if name == "measure":
                terminal = last[wires[0]] == position
                if rounds == 0:
                    self.program.append(("depolarize", rounds))
                    rounds += 1
                if terminal and rounds == 1:
                    self.program.append(("depolarize", rounds))
                    rounds += 1
                clbit = circuit.find_bit(instruction.clbits[0]).index
                self.program.append(("measure", self.local[wires[0]], clbit, int(terminal)))
            elif name == "reset":
                self.program.append(("reset", self.local[wires[0]]))
            elif name == "if_else":
                bit, value = instruction.operation.condition
                blocks = [self._block(block, wires) for block in instruction.operation.blocks]
                self.program.append(
                    ("if", circuit.find_bit(bit).index, int(value), blocks[0], blocks[1] if len(blocks) > 1 else None)
                )
            else:
                gate = _embed(instruction.operation.to_matrix(), tuple(self.local[w] for w in wires), self.size)
                pending, fused = gate @ pending, True
            if name in _VIRTUAL:
                continue
            for wire in wires:
                seen[wire] += 1
                for count, duration, index in insertions.get(wire, ()):
                    if count == seen[wire]:
                        if fused:
                            self.program.append(("unitary", pending))
                            pending, fused = np.eye(self.size, dtype=complex), False
                        self.program.append(("phase", self.local[wire], duration, index))
                        placed += 1
        if fused:
            self.program.append(("unitary", pending))
        if placed != sum(len(entries) for entries in insertions.values()):
            raise ValueError("an insertion names a pulse count its wire never reaches")

    def _block(self, block: Any, wires: list[int]) -> np.ndarray:
        unitary = np.eye(self.size, dtype=complex)
        for instruction in block.data:
            if instruction.operation.name in ("barrier", "delay"):
                continue
            if instruction.operation.name in ("measure", "reset", "if_else"):
                raise ValueError("an if_else block holds a non-unitary instruction")
            targets = tuple(self.local[wires[block.find_bit(bit).index]] for bit in instruction.qubits)
            unitary = _embed(instruction.operation.to_matrix(), targets, self.size) @ unitary
        return unitary

    def __call__(self, rates: np.ndarray, round1: float, round2: float, readout: dict[str, float]) -> np.ndarray:
        flips = ((readout["mid_e01"], readout["mid_e10"]), (readout["end_e01"], readout["end_e10"]))
        strengths = (round1, round2)
        start = np.zeros((self.size, self.size), dtype=complex)
        start[0, 0] = 1.0
        branches: dict[int, np.ndarray] = {0: start}
        for step in self.program:
            kind = step[0]
            if kind == "unitary":
                branches = {key: step[1] @ rho @ step[1].conj().T for key, rho in branches.items()}
            elif kind == "phase":
                factor = np.exp(1j * float(rates[step[3]]) * step[2] * self.diffs[step[1]])
                branches = {key: rho * factor for key, rho in branches.items()}
            elif kind == "depolarize":
                weight = min(max(strengths[step[1]], 0.0), 1.0)
                if weight:
                    for qubit in range(len(self.diffs)):
                        flip = self.flipped[qubit]
                        for key, rho in branches.items():
                            phased = rho * self.signs[qubit]
                            paulis = rho[np.ix_(flip, flip)] + phased[np.ix_(flip, flip)] + phased
                            branches[key] = (1 - 3 * weight / 4) * rho + (weight / 4) * paulis
            elif kind == "measure":
                _kind, qubit, clbit, which = step
                following: dict[int, np.ndarray] = {}
                for key, rho in branches.items():
                    for outcome in (0, 1):
                        projected = rho * self.masks[qubit][outcome]
                        if abs(np.trace(projected)) < 1e-15:
                            continue
                        error = min(max(flips[which][outcome], 0.0), 1.0)
                        for recorded, weight in ((outcome, 1 - error), (1 - outcome, error)):
                            if weight:
                                target = (key & ~(1 << clbit)) | (recorded << clbit)
                                following[target] = following.get(target, 0) + weight * projected
                branches = following
            elif kind == "reset":
                qubit, flip = step[1], self.flipped[step[1]]
                branches = {
                    key: rho * self.masks[qubit][0] + (rho * self.masks[qubit][1])[np.ix_(flip, flip)]
                    for key, rho in branches.items()
                }
            else:
                _kind, clbit, value, taken, otherwise = step
                for key, rho in branches.items():
                    block = taken if ((key >> clbit) & 1) == value else otherwise
                    if block is not None:
                        branches[key] = block @ rho @ block.conj().T
        law = np.zeros(1 << self.clbits)
        for key, rho in branches.items():
            law[key] += float(np.real(np.trace(rho)))
        return law


_NO_READOUT_ERROR = {"mid_e01": 0.0, "mid_e10": 0.0, "end_e01": 0.0, "end_e10": 0.0}


class CompileLaw:
    """A CompiledLaw of one (circuit, insertions, rates) item, required to equal the exact compiled law at rest.

    With every rate, nuisance and assignment error at zero the evaluator must
    reproduce qpe_diagnostics.ideal_compiled_probabilities on the same
    archived circuit.
    """

    def __call__(self, item: tuple[Any, dict[int, list[tuple[int, float, int]]], int]) -> CompiledLaw:
        from qpe_diagnostics import ideal_compiled_probabilities

        circuit, insertions, rates = item
        law = CompiledLaw(circuit, insertions, rates)
        rest = law(np.zeros(rates), 0.0, 0.0, _NO_READOUT_ERROR)
        if not np.allclose(rest, ideal_compiled_probabilities(circuit), rtol=0.0, atol=1e-9):
            raise RuntimeError(f"{circuit.name}: the compiled evaluator differs from the exact compiled law at rest")
        return law


class LawShift:
    """Whether one member's noiseless law moves when one rate steps away from a generic common point.

    A rate can act only jointly with another (a product of two branch
    phases), so the law is compared at a point where every rate is nonzero.
    """

    def __init__(self, laws: dict[str, CompiledLaw]) -> None:
        self.laws = laws

    def __call__(self, item: tuple[str, int, float, float]) -> bool:
        member, index, base, step = item
        law = self.laws[member]
        point = np.full(law.rates, base)
        moved = point.copy()
        moved[index] += step
        rest = law(point, 0.0, 0.0, _NO_READOUT_ERROR)
        return not np.allclose(law(moved, 0.0, 0.0, _NO_READOUT_ERROR), rest, atol=1e-9)


class ExposureObjective:
    """Deviance over every member of the exact-ISA static detuning law at [round1, round2, *free rates].

    Rates outside free stay at zero; readouts gives each member's assignment
    rates.
    """

    def __init__(
        self,
        laws: dict[str, CompiledLaw],
        counts: dict[str, np.ndarray],
        readouts: dict[str, dict[str, float]],
        free: list[int],
    ) -> None:
        self.laws, self.counts, self.readouts, self.free = laws, counts, readouts, free

    def members(self, vector: np.ndarray) -> dict[str, float]:
        values = [float(value) for value in vector]
        result = {}
        for name, law in self.laws.items():
            rates = np.zeros(law.rates)
            rates[self.free] = values[2:]
            observed = self.counts[name]
            expected = np.clip(law(rates, values[0], values[1], self.readouts[name]), 1e-12, None) * observed.sum()
            positive = observed > 0
            result[name] = 2 * float(np.sum(observed[positive] * np.log(observed[positive] / expected[positive])))
        return result

    def __call__(self, vector: np.ndarray) -> float:
        return sum(self.members(vector).values())


# A static detuning of a few hundred kHz bounds the rates, as in the joint
# quasi-static fit. Each coupled rate's grid holds an odd count of points, so
# zero is one, spaced at most a quarter of the detuning period of the
# qubit's longest interval, which places a point inside every phase basin of
# that interval; the product is capped, and the lowest points seed the local
# searches.
EXPOSURE_RATE_BOUND = 5.0
EXPOSURE_GRID_CAP = 32768
EXPOSURE_SEEDS = 12
# Grid deviances agree across BLAS builds to about 1e-11; seed ranking
# resolves them at this deviance step.
EXPOSURE_SEED_RESOLUTION = 1e-6
EXPOSURE_PROBES = ((0.41, 0.73), (-0.29, 1.13))


def coupled_rates(laws: dict[str, CompiledLaw], rates: int) -> list[int]:
    """Indices of the rates that move some member's noiseless law at either generic probe point."""
    probes = [(name, index, base, step) for index in range(rates) for base, step in EXPOSURE_PROBES for name in laws]
    moved = parallel.ordered_map(LawShift(laws), probes)
    return sorted({index for (_name, index, _base, _step), shift in zip(probes, moved, strict=True) if shift})


def grid_seeds(
    objective: ExposureObjective, longest_us: list[float], rounds: tuple[float, float]
) -> list[dict[int, float]]:
    """The EXPOSURE_SEEDS lowest grid points over the objective's free rates, keyed by rate index.

    Ranking rounds each deviance to EXPOSURE_SEED_RESOLUTION and breaks ties
    by grid order, so BLAS builds whose deviances differ at rounding level
    choose the same seeds and the local searches start in the same basins.
    """
    import heapq
    import itertools

    bound = EXPOSURE_RATE_BOUND
    points = [max(3, math.ceil(4 * bound * longest_us[index] / math.pi) + 1) for index in objective.free]
    if math.prod(points) > EXPOSURE_GRID_CAP:
        scale = (EXPOSURE_GRID_CAP / math.prod(points)) ** (1 / len(points))
        points = [max(3, int(count * scale)) for count in points]
    points = [count + 1 - count % 2 for count in points]
    grid = list(itertools.product(*(np.linspace(-bound, bound, count) for count in points)))
    landscape = parallel.ordered_map(objective, [np.array([*rounds, *rates]) for rates in grid], min_items=2)
    ranked = heapq.nsmallest(
        EXPOSURE_SEEDS,
        range(len(grid)),
        key=lambda index: (round(landscape[index] / EXPOSURE_SEED_RESOLUTION), index),
    )
    return [dict(zip(objective.free, map(float, grid[index]), strict=True)) for index in ranked]


def exposure_models(
    laws: dict[str, dict[str, CompiledLaw]],
    counts: dict[str, np.ndarray],
    readouts: dict[str, dict[str, float]],
    qubits: list[int],
    longest_us: dict[str, list[float]],
) -> dict[str, dict[str, Any]]:
    """Static detuning fits of every exposure model in laws, and the no-detuning law they all contain.

    Each model fits one rate per coupled qubit (coupled_rates) and the two
    depolarizing nuisances by deviance. The no-detuning fit comes first and
    its nuisances evaluate every model's rate grid; every model then searches
    from the same starts, zero and the grid seeds of all models, so
    deviances of different exposure placements compare optima found from
    identical starting points. A qubit whose rate moves no law adds no
    parameter. Starts are drawn before mapping, so pooled and serial runs
    return the same results.
    """
    reference = next(iter(laws.values()))
    rest = ExposureObjective(reference, counts, readouts, [])
    rest_starts = [[0.12, 0.0], [0.05, 0.05], [0.3, 0.1]]
    unit = [(0.0, 1.0), (0.0, 1.0)]
    rest_best = _lowest(parallel.ordered_map(LocalSearch(rest, unit), rest_starts, min_items=2))
    rounds = (rest_best[1][0], rest_best[1][1])
    objectives = {}
    seeds: list[dict[int, float]] = [{}]
    for label, members in laws.items():
        objectives[label] = ExposureObjective(members, counts, readouts, coupled_rates(members, len(qubits)))
        for seed in grid_seeds(objectives[label], longest_us[label], rounds):
            if seed not in seeds:
                seeds.append(seed)
    models: dict[str, dict[str, Any]] = {}
    for label, objective in objectives.items():
        bounds = unit + [(-EXPOSURE_RATE_BOUND, EXPOSURE_RATE_BOUND)] * len(objective.free)
        starts = [[*rounds, *(seed.get(index, 0.0) for index in objective.free)] for seed in seeds]
        best = _lowest(parallel.ordered_map(LocalSearch(objective, bounds), starts, min_items=2))
        names = ["round1", "round2", *(f"rate_{qubits[index]}_rad_per_us" for index in objective.free)]
        models[label] = {
            "fitted_qubits": [qubits[index] for index in objective.free],
            "uncoupled_qubits": [qubit for index, qubit in enumerate(qubits) if index not in objective.free],
            "starts": len(starts),
            "parameters": dict(zip(names, best[1], strict=True)),
            "deviance": best[0],
            "member_deviance": objective.members(np.array(best[1])),
        }
    models["no_detuning"] = {
        "parameters": dict(zip(["round1", "round2"], rest_best[1], strict=True)),
        "deviance": rest_best[0],
        "member_deviance": rest.members(np.array(rest_best[1])),
    }
    cells = sum(len(values) - 1 for values in counts.values())
    for label, model in models.items():
        model["parameters_count"] = len(model["parameters"])
        model["degrees_of_freedom"] = cells - model["parameters_count"]
        if label == "no_detuning":
            continue
        added = model["parameters_count"] - 2
        statistic = rest_best[0] - model["deviance"]
        model["likelihood_ratio_vs_no_detuning"] = {
            "statistic": statistic,
            "added_parameters": added,
            # Periodic rates break the regularity conditions of the chi-square limit.
            "nominal_chi2_p_value": float(chi2.sf(max(statistic, 0.0), added)) if added else None,
        }
    return models


def _insertions(
    table: dict[int, list[list[int]]], qubits: list[int], dt_us: float
) -> dict[int, list[tuple[int, float, int]]]:
    return {
        qubit: [(count, (end - start) * dt_us, qubits.index(qubit)) for start, end, count in gaps]
        for qubit, gaps in table.items()
    }


def unresolved_exposure(segments: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    """The skip record of a run whose segments omit an active wire's intervals, or None when every wire resolves.

    window_segments leaves out a wire whose instructions do not map one to
    one onto its pulses, so a fit over the remaining wires would describe a
    reduced model.
    """
    unresolved = {name: entry["unresolved"] for name, entry in segments.items() if entry["unresolved"]}
    if unresolved:
        return {"skipped": "an active wire's idle intervals are unresolved", "unresolved": unresolved}
    return None


def piecewise_fit(
    run: Path, pairs: dict[str, dict[str, np.ndarray]], readouts: dict[str, dict[str, float]]
) -> dict[str, Any]:
    """Static detuning fits with piecewise and single-gap window exposure through the exact archived ISA.

    Both models rotate each window qubit by one static rate times every idle
    interval they expose (window_segments), evaluated by CompiledLaw on the
    archived circuit, so the coupling of each qubit to the work register in
    each recorded branch follows from the circuit and needs no single-gap
    sign. The single gap's intervals are a subset of the piecewise ones and
    both carry one rate per coupled qubit, so their deviances differ through
    exposure placement and the coupled-qubit count (exposure_models).
    """
    group = _group(run)
    names = [member["name"] for member in group["members"]]
    circuits = _circuits(run)
    try:
        segments = {
            name: window_segments(circuit, payload)
            for name, circuit, payload in zip(names, circuits, raw_pubs(run), strict=True)
        }
    except ValueError as error:
        return {"skipped": str(error)}
    skipped = unresolved_exposure(segments)
    if skipped:
        return skipped
    dt, source = dt_source(run)
    dt_us = dt * 1e6
    qubits = sorted({qubit for entry in segments.values() for qubit in entry["intervals"]})
    counts = {f"{pair}_{arm}": values for pair, arms in pairs.items() for arm, values in arms.items()}
    tables = {"piecewise": "intervals", "single_gap": "single_gap"}
    items = [
        (circuit, _insertions(segments[name][table], qubits, dt_us), len(qubits))
        for table in tables.values()
        for name, circuit in zip(names, circuits, strict=True)
    ]
    compiled = parallel.ordered_map(CompileLaw(), items, min_items=2)
    laws = {
        label: dict(zip(names, compiled[position * len(names) : (position + 1) * len(names)], strict=True))
        for position, label in enumerate(tables)
    }
    longest = {
        label: [
            max(
                [(end - start) * dt_us for entry in segments.values() for start, end, _c in entry[table].get(q, [])],
                default=0.0,
            )
            for q in qubits
        ]
        for label, table in tables.items()
    }
    models = exposure_models(laws, counts, readouts, qubits, longest)
    pair_of = {name: name.removesuffix("_no_feedback").removesuffix("_feedback") for name in names}
    for model in models.values():
        model["pair_deviance"] = {
            pair: sum(value for name, value in model["member_deviance"].items() if pair_of[name] == pair)
            for pair in dict.fromkeys(pair_of.values())
        }
    return {
        "dt_seconds": dt,
        "dt_source": source,
        "segments": {
            name: {
                "control": entry["control"],
                "window_dt": entry["window"],
                "intervals_dt": {str(q): [[s, e] for s, e, _c in gaps] for q, gaps in entry["intervals"].items()},
                "single_gap_dt": {str(q): [[s, e] for s, e, _c in gaps] for q, gaps in entry["single_gap"].items()},
                "unresolved": entry["unresolved"],
            }
            for name, entry in segments.items()
        },
        "models": models,
        "piecewise_minus_single_gap_deviance": models["piecewise"]["deviance"] - models["single_gap"]["deviance"],
        "piecewise_added_parameters_over_single_gap": models["piecewise"]["parameters_count"]
        - models["single_gap"]["parameters_count"],
    }


class PhaseProfile:
    """Deviance of both arms at a fixed work phase, minimized over the depolarizing nuisances.

    L-BFGS-B starts from the work-phase fit's nuisances, so phase_interval's
    grid and a single-phase test evaluate the same profile.
    """

    def __init__(
        self, counts: dict[str, np.ndarray], readouts: dict[str, dict[str, float]], best: dict[str, Any]
    ) -> None:
        self.counts, self.readouts = counts, readouts
        self.names = [name for name, _low, _high in NUISANCE]
        self.bounds = [(low, high) for _name, low, high in NUISANCE]
        self.start = np.array([best["parameters"][name] for name in self.names])

    def objective(self, vector: np.ndarray, phase: float) -> float:
        params = dict(zip(self.names, map(float, vector), strict=True)) | {"phase_one": phase}
        return deviance(self.counts, params, self.readouts)

    def __call__(self, phase: float) -> float:
        return float(minimize(self.objective, self.start, args=(phase,), method="L-BFGS-B", bounds=self.bounds).fun)


def phase_interval(
    counts: dict[str, np.ndarray],
    readouts: dict[str, dict[str, float]],
    best: dict[str, Any],
    threshold: float = 3.84,
) -> list[list[float]]:
    """Profile-likelihood confidence set of the work phase as wrapped segments.

    Grid phases whose profiled deviance lies within threshold of the minimum
    form the set; contiguous runs become segments, and a run touching both
    -pi and pi joins into one segment across the wrap. The default 3.84 is
    the one-parameter chi-square 95 percent quantile to two decimals, the
    level the retained mechanism fits carry.
    """
    profile = PhaseProfile(counts, readouts, best)
    inside = [profile(float(phase)) <= best["deviance"] + threshold for phase in np.linspace(-math.pi, math.pi, 121)]
    grid = np.linspace(-math.pi, math.pi, 121)
    segments: list[list[float]] = []
    for index, accepted in enumerate(inside):
        if accepted and (index == 0 or not inside[index - 1]):
            segments.append([float(grid[index]), float(grid[index])])
        elif accepted:
            segments[-1][1] = float(grid[index])
    if len(segments) > 1 and inside[0] and inside[-1]:
        first = segments.pop(0)
        segments[-1][1] = first[1] + 2 * math.pi
    return segments


def _with_excess(readout: dict[str, float], params: dict[str, float]) -> dict[str, float]:
    combined = readout | params
    for key in ("mid_e01", "mid_e10", "end_e01", "end_e10"):
        combined[key] = readout[key] + params.get(f"{key}_excess", 0.0)
    return combined


def deviance(counts: dict[str, np.ndarray], params: dict[str, float], readouts: dict[str, dict[str, float]]) -> float:
    """Deviance of both arms; each arm's readout applies unless params fits it."""
    total = 0.0
    for arm, feed_forward in (("feedback", True), ("no_feedback", False)):
        observed = counts[arm]
        expected = np.clip(distribution(_with_excess(readouts[arm], params), feed_forward), 1e-12, None)
        expected = expected * observed.sum()
        positive = observed > 0
        total += 2 * float(np.sum(observed[positive] * np.log(observed[positive] / expected[positive])))
    return total


def _readout(read_one_given_zero: float, read_zero_given_one: float) -> dict[str, float]:
    return {
        "mid_e01": read_one_given_zero,
        "mid_e10": read_zero_given_one,
        "end_e01": read_one_given_zero,
        "end_e10": read_zero_given_one,
    }


def execution_calibration(run: Path) -> dict[str, dict[str, Any]]:
    """Per member, the placed-qubit calibration in force at its PUB's execution start, with its source.

    --collect retains placed_qubit_calibration at each PUB's execution start
    in collect.json's executed entry of the member; a member whose entry
    holds none reads the record's plan-time placed_qubit_calibration, and
    source names which one each member uses.
    """
    group = _group(run)
    executed: dict[str, Any] = {}
    for entry in json.loads((run / "collect.json").read_text())[1:]:
        if isinstance(entry, dict) and entry.get("group") == group.get("group"):
            executed |= entry.get("executed", {})
    calibrations = {}
    for member in group["members"]:
        record = executed.get(member["name"], {})
        values = record.get("placed_qubit_calibration")
        if values:
            calibrations[member["name"]] = {
                "source": "execution_start",
                "calibration": record.get("calibration"),
                "values": values,
            }
        else:
            calibrations[member["name"]] = {
                "source": "plan_time",
                "calibration": group.get("calibration"),
                "values": group.get("placed_qubit_calibration", {}),
            }
    return calibrations


def _assignment(values: dict[str, Any], qubit: int, properties: Any) -> tuple[float, float]:
    retained = values.get(str(qubit))
    if retained and {"prob_meas1_prep0", "prob_meas0_prep1"} <= retained.keys():
        return float(retained["prob_meas1_prep0"]), float(retained["prob_meas0_prep1"])
    # live_run.readout_flips uses the aggregate error for both directions
    # when a backend omits the asymmetric fields.
    if retained and "readout_error" in retained:
        return float(retained["readout_error"]), float(retained["readout_error"])
    if properties is None:
        raise RuntimeError(f"no retained calibration for qubit {qubit}; pass --readout")
    values = {item.name: float(item.value) for item in properties.qubits[qubit]}
    if "prob_meas1_prep0" in values and "prob_meas0_prep1" in values:
        return values["prob_meas1_prep0"], values["prob_meas0_prep1"]
    return values["readout_error"], values["readout_error"]


def member_readouts(run: Path, roles: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Assignment rates of each member's first and last measurement writers at its calibration.

    Each member reads execution_calibration: the values in force at its
    PUB's execution start, else the record's plan-time
    placed_qubit_calibration; a record that retains neither falls back to
    IBM properties at its calibration timestamp.
    """
    group = _group(run)
    calibrations = execution_calibration(run)
    properties = None
    if not all(
        str(qubit) in calibrations[name]["values"]
        for name, role in roles.items()
        for qubit in (role["control"], role["terminal"])
    ):
        from datetime import datetime, timedelta

        from qiskit_ibm_runtime import QiskitRuntimeService

        stamp = datetime.fromisoformat(group["calibration"])
        backend = ibm_account.open_service(QiskitRuntimeService).backend(group["backend"])
        # A historical query returns the newest snapshot strictly before its
        # datetime, so the query asks one second past the recorded stamp; the
        # current snapshot serves when no later calibration has landed.
        candidates = (backend.properties(datetime=stamp + timedelta(seconds=1)), backend.properties())
        properties = next((item for item in candidates if item is not None and item.last_update_date == stamp), None)
        if properties is None:
            raise RuntimeError(f"{group['backend']} properties at {stamp} are unavailable; pass --readout")
    readouts = {}
    for name, role in roles.items():
        mid = _assignment(calibrations[name]["values"], role["control"], properties)
        end = _assignment(calibrations[name]["values"], role["terminal"], properties)
        readouts[name] = {
            "control_qubit": role["control"],
            "terminal_qubit": role["terminal"],
            "mid_e01": mid[0],
            "mid_e10": mid[1],
            "end_e01": end[0],
            "end_e10": end[1],
        }
    return readouts


def _model_readout(entry: dict[str, Any]) -> dict[str, float]:
    return {key: float(entry[key]) for key in ("mid_e01", "mid_e10", "end_e01", "end_e10")}


MECHANISMS: dict[str, tuple[tuple[str, float, float], ...]] = {
    "baseline_depolarizing": (),
    "work_phase_one": (("phase_one", -math.pi, math.pi),),
    "work_phase_sixteen": (("phase_sixteen", -math.pi, math.pi),),
    "window_amplitude_damping": (("window_t1", 0.0, 1.0),),
    "window_dephasing": (("window_t2", 0.0, 1.0),),
    "reset_failure": (("reset_failure", 0.0, 1.0),),
    "control_phase": (("control_phase", -math.pi, math.pi),),
    # Assignment alternatives add an excess shared by both arms to each arm's
    # calibrated rate, so a zero excess recovers the baseline (nested models).
    "mid_readout_assignment": (("mid_e01_excess", 0.0, 0.5), ("mid_e10_excess", 0.0, 0.5)),
    "terminal_readout_assignment": (("end_e01_excess", 0.0, 0.5), ("end_e10_excess", 0.0, 0.5)),
}
NUISANCE = (("round1", 0.0, 1.0), ("round2", 0.0, 1.0))


def fit(
    counts: dict[str, np.ndarray],
    readouts: dict[str, dict[str, float]],
    extra: tuple[tuple[str, float, float], ...],
) -> dict[str, Any]:
    names = [name for name, _low, _high in NUISANCE + extra]
    bounds = [(low, high) for _name, low, high in NUISANCE + extra]

    def objective(vector: np.ndarray) -> float:
        return deviance(counts, dict(zip(names, (float(value) for value in vector), strict=True)), readouts)

    best: Any = None
    starts = [[0.1, 0.1] + [(low + high) / 2 for _name, low, high in extra]]
    starts += [[0.2, 0.2] + [low + (high - low) * fraction for _name, low, high in extra] for fraction in (0.3, 0.7)]
    for start in starts:
        result = minimize(objective, np.array(start), method="L-BFGS-B", bounds=bounds)
        if best is None or result.fun < best.fun:
            best = result
    params = dict(zip(names, (float(value) for value in best.x), strict=True))
    return {
        "parameters": params,
        "deviance": float(best.fun),
        "added_parameters": len(extra),
        "feedback_law": distribution(_with_excess(readouts["feedback"], params), True).tolist(),
        "no_feedback_law": distribution(_with_excess(readouts["no_feedback"], params), False).tolist(),
    }


def _check_exact_laws() -> None:
    for feed_forward, exact in ((True, (3, 2, 1, 2)), (False, (3, 1, 1, 3))):
        law = distribution(_readout(0.0, 0.0), feed_forward)
        if not np.allclose(law, [value / 8 for value in exact], atol=1e-12):
            raise RuntimeError(f"noiseless model law {law} differs from the exact N=21 law")
        if not np.allclose(distribution(_readout(0.0, 0.0), feed_forward, np.eye(8, dtype=complex)), law, atol=1e-12):
            raise RuntimeError("an identity window changed the noiseless law")
        params = _readout(0.02, 0.03) | {"round1": 0.1, "phase_one": 0.7}
        phase = np.diag([np.exp(0.7j) if index & 1 else 1.0 for index in range(8)]).astype(complex)
        windowed = distribution(params | {"phase_one": 0.0}, feed_forward, phase)
        if not np.allclose(windowed, distribution(params, feed_forward), atol=1e-12):
            raise RuntimeError("a window phase on the work qubit for 1 differs from phase_one")


class TwoBasins:
    """A static landscape with a shallow basin at mean -2 and a deep one at +2, spread penalized."""

    def __call__(self, vector: np.ndarray) -> float:
        round1, round2, mean, spread = (float(value) for value in vector)
        wells = 0.5 * math.exp(-((mean + 2) ** 2) / 0.1) + math.exp(-((mean - 2) ** 2) / 0.1)
        return (round1 - 0.12) ** 2 + round2**2 + spread**2 + 1.0 - wells


def _synthetic_run(directory: Path, collected: str, raw_names: list[str]) -> Path:
    """A two-member run submitting job J1 as PUBs P1 and P2; collection and raw use the given job and names."""
    directory.mkdir()
    members = ["pair_feedback", "pair_no_feedback"]
    pubs = [{"name": f"P{i + 1}", "components": [{"member": m}]} for i, m in enumerate(members)]
    record = {
        "groups": [{"replicas": [{}], "members": [{"name": m} for m in members]}],
        "submission": {"jobs": [{"job_id": "J1", "pubs": pubs}]},
    }
    (directory / "record.json").write_text(json.dumps(record))
    raw = directory / "raw" / collected
    raw.mkdir(parents=True)
    files: dict[str, str] = {}
    for position, name in enumerate(raw_names):
        path = raw / f"pub_{position:02d}.json"
        path.write_text(json.dumps({"pub_index": position, "pub_name": name, "registers": {}}))
        files[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (raw / "index.json").write_text(json.dumps({"job_id": collected, "files": files}))
    timing: dict[str, dict[str, Any]] = {name: {} for name in raw_names}
    (directory / "collect.json").write_text(
        json.dumps([{"jobs": {collected: {"pub_timing": timing, "raw": {"files": files}}}}])
    )
    return directory


def _check_manifest_binding() -> None:
    import tempfile

    with tempfile.TemporaryDirectory() as scratch:
        root = Path(scratch)
        if [payload["pub_name"] for payload in raw_pubs(_synthetic_run(root / "bound", "J1", ["P1", "P2"]))] != [
            "P1",
            "P2",
        ]:
            raise RuntimeError("a run bound to its manifest reads the wrong PUBs")
        for label, job, names in (("job", "J2", ["P1", "P2"]), ("order", "J1", ["P2", "P1"])):
            try:
                raw_pubs(_synthetic_run(root / label, job, names))
            except RuntimeError:
                continue
            raise RuntimeError(f"raw_pubs accepts a collection whose {label} differs from the submission manifest")


def _check_static_basins() -> None:
    """The full winner sits in the shallow basin; the seeded static refit reaches the deep one."""
    objective, bounds = TwoBasins(), [(0.0, 1.0), (0.0, 1.0), (-5.0, 5.0), (0.0, 5.0)]
    winner = [0.12, 0.0, -2.0, 0.3]
    single = LocalSearch(objective, bounds[:3] + [(0.0, 0.0)])([*winner[:3], 0.0])
    seeded = static_refit(objective, bounds, winner, [(-2.0,), (2.0,)], 1)
    if not single[0] - seeded[0] > 0.4 or abs(seeded[1][2] - 2.0) > 0.05:
        raise RuntimeError(f"static refit from every seed returns {seeded}; the winner's start alone gives {single}")


SYNTHETIC_DT_US = 4e-3
SYNTHETIC_RATES = (1.1, -2.3)
# Planted rates expose the work-only split by at least this total variation.
SYNTHETIC_MIN_TV = 0.1
SYNTHETIC_RATE_TOLERANCE = 0.01


def _window_member(
    closing: int, rates: tuple[float, float] | None = None, extra_readout: bool = False, stray: bool = False
) -> tuple[Any, dict[str, Any]]:
    """A three-qubit member and its returned schedule, with work qubit 1 pulsed inside the control's window.

    Qubit 0 measures at 10 dt, resets, and plays its feed-forward pulse at
    closing; qubit 1 plays a work-only sx at 200 dt inside the window, so its
    idle time splits into [8, 200] and [208, closing + 10], and qubit 2 idles
    over [8, closing + 10]. With rates, the circuit carries the static
    detuning rotation of every interval explicitly, independent of
    window_segments and CompiledLaw. extra_readout measures qubit 0 into the
    first bit a second time before its reset, as the extra_readout variant
    does, and stray adds an sx on qubit 2 that the schedule omits.
    """
    from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister

    circuit = QuantumCircuit(QuantumRegister(3, "q"), ClassicalRegister(4, "c"), name=f"window_{closing}")
    rows: list[tuple[str, int, int, int]] = []

    def pulse(name: str, qubit: int, start: int, length: int = 8) -> None:
        rows.append((name, qubit, start, length))

    def detune(qubit: int, duration: int) -> None:
        if rates is not None:
            circuit.rz(rates[qubit - 1] * duration * SYNTHETIC_DT_US, qubit)

    for qubit in range(3):
        circuit.sx(qubit)
        pulse("sx", qubit, 0)
    detune(1, 192)
    detune(2, closing + 2)
    circuit.rz(math.pi / 2, 1)
    circuit.rz(math.pi / 2, 2)
    circuit.measure(0, 0)
    pulse("measure", 0, 10, 400)
    if extra_readout:
        circuit.measure(0, 0)
    if stray:
        circuit.sx(2)
    circuit.sx(1)
    pulse("sx", 1, 200)
    detune(1, closing - 198)
    circuit.reset(0)
    pulse("reset", 0, 410, 400)
    circuit.sx(0)
    pulse("sx", 0, closing)
    with circuit.if_test((circuit.clbits[0], 1)):
        circuit.rz(math.pi / 2, 0)
    circuit.sx(0)
    pulse("sx", 0, closing + 8)
    circuit.sx(1)
    circuit.sx(2)
    pulse("sx", 1, closing + 10)
    pulse("sx", 2, closing + 10)
    for qubit, clbit in ((0, 1), (1, 2), (2, 3)):
        circuit.measure(qubit, clbit)
        pulse("measure", qubit, closing + 16 + 2 * min(qubit, 1), 400)
    timing = "\n".join(f"main,{name}_{q},Qubit {q},{start},{length},play" for name, q, start, length in rows)
    return circuit, {"metadata": {"compilation": {"scheduler_timing": {"timing": timing}}}}


class _TiedLandscape:
    """A rate landscape whose points tie in |rate 0| up to a rounding-level tilt along rate 1."""

    free = [0, 1]

    def __init__(self, tilt: float) -> None:
        self.tilt = tilt

    def __call__(self, vector: np.ndarray) -> float:
        return round(abs(float(vector[2])), 6) + self.tilt * float(vector[3])


def _check_seed_ranking() -> None:
    """Grid seeds stay the same when tied deviances move at rounding level, as across BLAS builds."""
    seeds = [grid_seeds(_TiedLandscape(tilt), [1.0, 1.0], (0.1, 0.0)) for tilt in (1e-11, -1e-11)]  # type: ignore[arg-type]
    if seeds[0] != seeds[1]:
        raise RuntimeError("a rounding-level change of tied grid deviances changes the grid seeds")


def _check_piecewise_exposure() -> None:
    """Segments split at a work-only pulse, the split moves the law, and a fit recovers the planted rates."""
    from qpe_diagnostics import ideal_compiled_probabilities

    members = {f"window_{closing}": closing for closing in (820, 1150)}
    qubits = [1, 2]
    laws: dict[str, dict[str, CompiledLaw]] = {"piecewise": {}, "single_gap": {}}
    counts: dict[str, np.ndarray] = {}
    longest = [0.0, 0.0]
    for name, closing in members.items():
        circuit, payload = _window_member(closing)
        segments = window_segments(circuit, payload)
        expected = {
            "window": [10, closing],
            "intervals": {1: [[8, 200, 1], [208, closing + 10, 2]], 2: [[8, closing + 10, 1]]},
            "single_gap": {1: [[8, 200, 1]], 2: [[8, closing + 10, 1]]},
        }
        if any(segments[key] != value for key, value in expected.items()):
            raise RuntimeError(f"window_segments of {name} returns {segments}, not {expected}")
        for label, table in (("piecewise", "intervals"), ("single_gap", "single_gap")):
            laws[label][name] = CompileLaw()((circuit, _insertions(segments[table], qubits, SYNTHETIC_DT_US), 2))
        longest = [max(longest[0], (closing - 198) * SYNTHETIC_DT_US), max(longest[1], (closing + 2) * SYNTHETIC_DT_US)]
        planted = np.array(SYNTHETIC_RATES)
        truth = np.array(ideal_compiled_probabilities(_window_member(closing, SYNTHETIC_RATES)[0]))
        piecewise = laws["piecewise"][name](planted, 0.0, 0.0, _NO_READOUT_ERROR)
        if not np.allclose(piecewise, truth, rtol=0.0, atol=1e-9):
            raise RuntimeError(f"{name}: the piecewise law at the planted rates differs from the explicit circuit")
        distance = 0.5 * float(np.abs(piecewise - laws["single_gap"][name](planted, 0.0, 0.0, _NO_READOUT_ERROR)).sum())
        if distance < SYNTHETIC_MIN_TV:
            raise RuntimeError(
                f"{name}: piecewise and single-gap laws differ by TV {distance:.4f} < {SYNTHETIC_MIN_TV:g}"
            )
        counts[name] = np.round(truth * 2**20)
        # The recorded first bit drives the if_else: recorded 0 leaves the
        # control's sx sx at |1>, recorded 1 adds rz(pi/2) between them.
        flipped = laws["piecewise"][name](planted, 0.0, 0.0, _NO_READOUT_ERROR | {"mid_e01": 0.2, "mid_e10": 0.3})
        marginal = [sum(flipped[key] for key in range(16) if key & 3 == low) for low in range(4)]
        if marginal[0] > 1e-12 or not math.isclose(marginal[3], marginal[1], rel_tol=1e-9):
            raise RuntimeError(f"{name}: a mid-circuit assignment flip misses the feed-forward condition: {marginal}")
        # A second readout of the projected control into the same bit draws
        # a fresh mid-circuit assignment flip and leaves the law unchanged.
        noisy = {"mid_e01": 0.2, "mid_e10": 0.3, "end_e01": 0.05, "end_e10": 0.07}
        repeated = CompileLaw()(
            (
                _window_member(closing, extra_readout=True)[0],
                _insertions(segments["intervals"], qubits, SYNTHETIC_DT_US),
                2,
            )
        )
        single = laws["piecewise"][name](planted, 0.1, 0.05, noisy)
        if not np.allclose(repeated(planted, 0.1, 0.05, noisy), single, rtol=0.0, atol=1e-12):
            raise RuntimeError(f"{name}: a repeated mid-circuit readout changes the law")
        if unresolved_exposure({name: segments}) is not None:
            raise RuntimeError(f"{name}: resolved segments skip the exposure fit")
        stray = window_segments(*_window_member(closing, stray=True))
        if 2 in stray["intervals"] or unresolved_exposure({name: stray}) is None:
            raise RuntimeError(f"{name}: an unscheduled instruction on qubit 2 still enters the exposure fit")
    readouts = dict.fromkeys(members, _NO_READOUT_ERROR)
    fitted = exposure_models({"piecewise": laws["piecewise"]}, counts, readouts, qubits, {"piecewise": longest})
    found = fitted["piecewise"]["parameters"]
    rates = [found.get(f"rate_{qubit}_rad_per_us", math.nan) for qubit in qubits]
    missed = [abs(rate - planted) for rate, planted in zip(rates, SYNTHETIC_RATES, strict=True)]
    if not all(miss <= SYNTHETIC_RATE_TOLERANCE for miss in missed):
        raise RuntimeError(f"the piecewise fit returns rates {rates}; the planted rates are {SYNTHETIC_RATES}")


def _check_differences() -> None:
    retained = {"law": [0.25, 0.75], "dof": 3, "flag": True, "source": "--readout"}
    if differences(retained, {**retained, "law": [0.25 + 1e-8, 0.75]}):
        raise RuntimeError("a rounding-level float change fails the regeneration check")
    _check_parameter_replay()
    for changed in ({"law": [0.26, 0.75]}, {"dof": 4}, {"flag": False}, {"dof": 3.0}, {"law": [0.25]}):
        if not differences(retained, {**retained, **changed}):
            raise RuntimeError(f"the regeneration check accepts {changed}")
    if not differences(retained, {key: value for key, value in retained.items() if key != "flag"}):
        raise RuntimeError("the regeneration check accepts a dropped key")


def _check_parameter_replay() -> None:
    readout = _readout(0.001, 0.006)
    readouts = dict.fromkeys(("feedback", "no_feedback"), readout)
    counts = {"feedback": np.array([300, 200, 100, 200]), "no_feedback": np.array([300, 100, 100, 300])}

    def report(parameters: dict[str, float]) -> dict[str, Any]:
        model = {
            "parameters": parameters,
            "deviance": deviance(counts, parameters, readouts),
            "improves_at_family_alpha": True,
            **{
                f"{arm}_law": distribution(_with_excess(readout, parameters), arm == "feedback").tolist()
                for arm in readouts
            },
        }
        return {
            "member_readout": {f"p_{arm}": readout for arm in readouts},
            "pairs": {
                "p": {
                    "measured_counts": {arm: values.tolist() for arm, values in counts.items()},
                    "models": {"control_phase": model},
                }
            },
        }

    parameters = {"round1": 0.17281242424172436, "round2": 0.17288122760296823, "control_phase": -0.4676820606691535}
    original = report(parameters)
    drifted = report(parameters | {"round2": 0.17287973432964707, "control_phase": -0.4676843006565198})
    if not differences(original, drifted):
        raise RuntimeError("the replay fixture fails to expose optimizer-coordinate drift")
    if replay_differences(original, drifted):
        raise RuntimeError("optimizer-coordinate drift with equivalent laws fails observable replay")
    positive_boundary = report(parameters | {"control_phase": math.pi})
    negative_boundary = report(parameters | {"control_phase": -math.pi})
    if replay_differences(positive_boundary, negative_boundary):
        raise RuntimeError("equivalent phase branch boundaries fail observable replay")
    corrupted = json.loads(json.dumps(original))
    corrupted["pairs"]["p"]["models"]["control_phase"]["parameters"]["control_phase"] = -0.4
    if not replay_differences(original, corrupted):
        raise RuntimeError("parameter changes unbound to recorded laws pass replay")
    if not replay_differences(original, report(parameters | {"control_phase": -0.4})):
        raise RuntimeError("changed observable laws pass replay")
    for invalid_value in (True, math.nan, -0.1, 1.1):
        corrupted = json.loads(json.dumps(original))
        corrupted["pairs"]["p"]["models"]["control_phase"]["parameters"]["round2"] = invalid_value
        if not parameter_law_differences(corrupted):
            raise RuntimeError(f"an out-of-domain parameter {invalid_value!r} passes replay")


CONTRACT_IDLE_DT = {
    "nominal": 1000,
    "window_delay": 1415,
    "window_delay_long": 1830,
    "extra_readout": 1400,
    "window_echo": 1000,
}
CONTRACT_SLOPE = 6e-4
# Exact expected counts at this depth resolve the phase aliases the slope
# test meets inside the rate bound.
CONTRACT_SHOTS = 65536
# window_delay windows: on the planted slope, off it, and on the alias one
# turn above it, where the nominal phase wraps past pi.
CONTRACT_OFF_SLOPE_DT = 1700
CONTRACT_WRAPPED_DT = 1949


def _contract_roles(coupling: dict[int, dict[int, int]]) -> dict[str, dict[str, Any]]:
    """window_roles output of a synthetic family whose members all couple as given, idle CONTRACT_IDLE_DT.

    window_echo's window holds two echo pulses. No-feedback members carry
    the global negation whenever the anchor, the lowest coupled qubit,
    couples negatively, as window_roles reports it.
    """
    anchor = next(iter(coupling[min(coupling)].values()))
    roles: dict[str, dict[str, Any]] = {}
    for variant, idle in CONTRACT_IDLE_DT.items():
        echoes = [[400, 8], [900, 8]] if variant == "window_echo" else []
        for arm in ARMS:
            flip = -1 if arm == "no_feedback" and anchor < 0 else 1
            roles[f"{orbit_pair(variant)}_{arm}"] = {
                "control": 0,
                "terminal": 0,
                "coupling": {q: {b: flip * sign for b, sign in branches.items()} for q, branches in coupling.items()},
                "windows": {q: {"before": 100, "after": 100 + idle + 8 * len(echoes), "x": echoes} for q in coupling},
                "unresolved": [],
            }
    return roles


def _check_between_arm() -> None:
    """Planted families pass every contract, fail each one alone, and fail admissibility by member."""
    import copy

    readout = _readout(0.001, 0.006)
    base = readout | {"round1": 0.05, "round2": 0.02}

    def pair(params: dict[str, float], control: dict[str, float] | None = None) -> dict[str, np.ndarray]:
        """Exact expected counts; control replaces params in the no-feedback arm."""
        laws = {"feedback": params, "no_feedback": params if control is None else control}
        return {arm: np.round(distribution(base | laws[arm], arm == "feedback") * CONTRACT_SHOTS) for arm in ARMS}

    # The coupling of -1 makes the coupling-weighted exposure negative, so
    # the slope the contract recovers is -CONTRACT_SLOPE per dt.
    nominal = pair({"phase_one": CONTRACT_SLOPE * CONTRACT_IDLE_DT["nominal"]})
    # window_delay_long loses work-bit coherence beyond window_delay, so the
    # ramp contract passes; no other contract reads it.
    pairs = {
        orbit_pair("nominal"): nominal,
        orbit_pair("window_delay"): pair({"phase_one": CONTRACT_SLOPE * CONTRACT_IDLE_DT["window_delay"]}),
        orbit_pair("window_delay_long"): pair(
            {"phase_one": CONTRACT_SLOPE * CONTRACT_IDLE_DT["window_delay_long"], "window_t2": 0.3}
        ),
        orbit_pair("extra_readout"): nominal,
        orbit_pair("window_echo"): nominal,
    }
    spectators = _spectator_reads(0.8, 0.4, 1.0, 0.0)
    roles = _contract_roles({7: {0: -1, 1: -1}})
    readouts = dict.fromkeys(roles, readout)
    t2_us = dict.fromkeys(ARMS, {7: 100.0})
    dt = SYNTHETIC_DT_US * 1e-6
    profiles = SlopeProfiles(pairs, readouts, phase_fits(pairs, readouts))
    orientation = admissibility(roles)["orientation"]
    results = contract_results(roles, pairs, readouts, dt, t2_us, profiles, spectators=spectators)
    json.dumps(results, sort_keys=True)
    passing = dict.fromkeys(CONTRACTS, "pass")
    if {name: result["status"] for name, result in results.items()} != passing:
        raise RuntimeError(f"a family planted on every contract returns {results}")
    if (
        contract_results(roles, pairs, readouts, dt, t2_us, profiles, nominal_t2_us=t2_us, spectators=spectators)
        != results
    ):
        raise RuntimeError("a nominal member at the extra_readout member's T2 changes the contracts")
    drifted = contract_results(
        roles,
        pairs,
        readouts,
        dt,
        t2_us,
        profiles,
        nominal_t2_us={**t2_us, "feedback": {7: 90.0}},
        spectators=spectators,
    )
    if drifted["extra_readout_contrast"].get("differing_t2_qubits") != {"feedback": [7]} or any(
        drifted[name] != results[name] for name in CONTRACTS if name != "extra_readout_contrast"
    ):
        raise RuntimeError(f"a nominal member at another T2 reads {drifted}")

    def delayed(window: int) -> dict[str, dict[str, Any]]:
        case = copy.deepcopy(roles)
        for arm in ARMS:
            case[f"{orbit_pair('window_delay')}_{arm}"]["windows"][7]["after"] = 100 + window
        return case

    off_slope = phase_slope_contract(profiles, delayed(CONTRACT_OFF_SLOPE_DT), orientation, dt, CONTRACT_ALPHA, False)
    if off_slope["status"] != "fail":
        raise RuntimeError(f"an off-slope window_delay passes the phase-slope contract: {off_slope}")
    # The planted window_delay phase is also the alias one turn up of a
    # nominal phase past pi, so the shared-slope test passes with one wrap
    # while the principal nominal phase predicts a different delay phase.
    wrapped = phase_slope_contract(profiles, delayed(CONTRACT_WRAPPED_DT), orientation, dt, CONTRACT_ALPHA, False)
    principal = math.remainder(wrapped["nominal_fit_phase"] * wrapped["exposure_ratio"], 2 * math.pi)
    principal_statistic = profiles.exact["window_delay"](principal) - profiles.minima[1]
    if (
        wrapped["status"] != "pass"
        or wrapped["nominal_phase_wraps"] != 1
        or principal_statistic <= off_slope["chi2_threshold"]
    ):
        raise RuntimeError(
            f"a wrapped nominal phase returns {wrapped['status']} at {wrapped['nominal_phase_wraps']} wraps; "
            f"the principal-branch rule's statistic is {principal_statistic:.2f}"
        )
    # The slope contract reads neither the extra_readout nor the window_echo
    # pair, so their cases evaluate the two magnitude contracts alone.
    dephased = pair({"phase_one": CONTRACT_SLOPE * CONTRACT_IDLE_DT["nominal"], "window_t2": 0.5})
    readout_case = readout_contract(pairs | {orbit_pair("extra_readout"): dephased}, roles, dt, t2_us, CONTRACT_ALPHA)
    echo_case = contrast_floor(dephased, nominal, (1.0, 1.0), CONTRACT_ALPHA)
    if readout_case["status"] != "fail" or echo_case["status"] != "fail":
        raise RuntimeError(f"dephased pairs pass the magnitude contracts: {readout_case}, {echo_case}")
    if readout_contract(pairs, roles, dt, {"feedback": {7: 100.0}}, CONTRACT_ALPHA)["status"] != "not_evaluable":
        raise RuntimeError("the readout contract evaluates without a retained T2 in every arm")
    # Only the no-feedback member of extra_readout idles longer, so only y
    # decays; the pair-mean factor overstates the feedback arm's decay bound.
    resting = pair({})
    arm_roles = copy.deepcopy(roles)
    arm_roles[f"{orbit_pair('extra_readout')}_feedback"]["windows"][7]["after"] = 100 + CONTRACT_IDLE_DT["nominal"]
    arm_roles[f"{orbit_pair('extra_readout')}_no_feedback"]["windows"][7]["after"] = (
        100 + CONTRACT_IDLE_DT["nominal"] + 347
    )
    arm_pairs = {orbit_pair("nominal"): resting, orbit_pair("extra_readout"): pair({}, {"window_t2": 0.4})}
    per_arm = readout_contract(arm_pairs, arm_roles, dt, dict.fromkeys(ARMS, {7: 1.0}), CONTRACT_ALPHA)
    mean_factor = math.exp(-347 / 2 * dt / 1e-6)
    pooled = contrast_floor(arm_pairs[orbit_pair("extra_readout")], resting, (mean_factor, mean_factor), CONTRACT_ALPHA)
    if per_arm["status"] != "pass" or per_arm["feedback_factor"] != 1.0 or pooled["status"] != "fail":
        raise RuntimeError(
            f"per-arm readout dephasing returns {per_arm}; the pair-mean factor returns {pooled['status']}"
        )
    # An echo that cancels the nominal phase at equal coherence lowers the
    # signed contrast difference beyond its one-sided limit; the magnitude
    # contract passes it.
    canceled = pair({})
    restored = contrast_floor(canceled, nominal, (1.0, 1.0), CONTRACT_ALPHA)
    (echo_signed, echo_variance), (nominal_signed, nominal_variance) = map(contrast_difference, (canceled, nominal))
    signed_upper = (
        echo_signed - nominal_signed + float(norm.ppf(1 - CONTRACT_ALPHA)) * math.sqrt(echo_variance + nominal_variance)
    )
    if restored["status"] != "pass" or signed_upper >= 0:
        raise RuntimeError(
            f"a phase-canceling echo returns {restored}; the signed contrast form's upper limit is {signed_upper:.4f}"
        )
    differing = copy.deepcopy(roles)
    name = f"{orbit_pair('nominal')}_no_feedback"
    differing[name]["coupling"] = {7: {0: 1, 1: 1}, 9: {1: 0}}
    differing[name]["unresolved"] = ["a joint probe with qubit 7 fits neither relative sign of qubit 9"]
    # A two-qubit coupling admits the no-feedback global negation; a relative
    # sign flip between the two qubits differs.
    relative = _contract_roles({7: {0: -1, 1: -1}, 9: {0: 1, 1: 1}})
    if not admissibility(relative)["admissible"]:
        raise RuntimeError("admissibility refuses a globally negated no-feedback coupling")
    echo = f"{orbit_pair('window_echo')}_no_feedback"
    relative[echo]["coupling"] = {7: {0: 1, 1: 1}, 9: {0: 1, 1: 1}}
    for case, members in ((differing, {name}), (relative, {echo})):
        admitted = admissibility(case)
        refused = contract_results(case, pairs, readouts, dt, t2_us, profiles)
        if admitted["admissible"] or set(admitted["differing"]) != members:
            raise RuntimeError(f"admissibility names {sorted(admitted['differing'])}, not {sorted(members)}")
        if any(
            result["status"] != "not_admissible" or result["differing"] != admitted["differing"]
            for result in refused.values()
        ):
            raise RuntimeError(f"a family with differing couplings evaluates a contract: {refused}")
    if admissibility(differing)["unresolved"] != {name: differing[name]["unresolved"]}:
        raise RuntimeError("admissibility omits a member's unresolved probe")
    single = {key: value for key, value in roles.items() if key.startswith(orbit_pair("nominal"))}
    absent = [f"{orbit_pair(variant)}_{arm}" for variant in ORBIT_VARIANTS[1:] for arm in ARMS]
    if admissibility(single)["missing"] != absent:
        raise RuntimeError("admissibility of the nominal pair alone names no missing member")
    law = PhaseLaw(readout, True)
    if not np.allclose(
        law(0.11, 0.83, -2.4),
        distribution(readout | {"round1": 0.11, "round2": 0.83, "phase_one": -2.4}, True),
        rtol=0.0,
        atol=1e-10,
    ):
        raise RuntimeError("the polynomial-trigonometric law differs from distribution() off its nodes")


def _spectator_reads(
    measured: float, measured_phase: float, reference: float, reference_phase: float, branch_turn: float = 0.0
) -> dict[str, dict[str, np.ndarray]]:
    """Exact expected spectator counts at CONTRACT_SHOTS: each kind's visibility and qubit-2 phase.

    Qubit 2 reads 1 in X with probability (1 - R cos phi) / 2 and in Y with
    (1 - R sin phi) / 2. The measured control bit splits the shots evenly,
    branch 1 turned by branch_turn about branch 0 and the two branches
    centered on phi; the unwritten reset_only bit reads 0.
    """
    reads: dict[str, dict[str, np.ndarray]] = {}
    for kind, visibility, phase in (
        ("measured", measured, measured_phase),
        ("reset_only", reference, reference_phase),
    ):
        reads[kind] = {}
        for quadrature in SPECTATOR_QUADRATURES:
            vector = np.zeros(4)
            branches = (
                ((0, phase - branch_turn / 2), (1, phase + branch_turn / 2)) if kind == "measured" else ((0, phase),)
            )
            for control, angle in branches:
                shots = CONTRACT_SHOTS // len(branches)
                projection = math.cos(angle) if quadrature == "x" else math.sin(angle)
                one = round((1 - visibility * projection) / 2 * shots)
                vector[control] += shots - one
                vector[control + 2] += one
            reads[kind][quadrature] = vector
    return reads


def _check_window_sweep() -> dict[str, str]:
    """Planted truths reach the preregistered ramp and spectator verdicts.

    Static detuning: the nominal, window_delay and window_delay_long pairs
    carry phases growing with their idles at equal coherence, and qubit 2's
    measured Ramsey a rotated phase at the reference's visibility, so both
    contracts fail. Monotonic dephasing: coherence falls with each added
    idle, and the ramp passes. Qubit-2 readout dephasing: the measured
    visibility 0.8 against 1.0 passes the spectator contract. Step: one loss
    at the first added idle, flat beyond it, fails the ramp while
    window_delay's magnitude lies below the nominal one (contrast_floor
    fails). A ramp that passes at margin zero fails at a margin above its
    upper limit's magnitude.
    """
    readout = _readout(0.001, 0.006)
    base = readout | {"round1": 0.05, "round2": 0.02}

    def pair(phase: float, loss: float) -> dict[str, np.ndarray]:
        params = base | {"phase_one": phase, "window_t2": loss}
        return {arm: np.round(distribution(params, arm == "feedback") * CONTRACT_SHOTS) for arm in ARMS}

    def ramp(losses: tuple[float, float, float], slope: float = 0.0) -> tuple[dict[str, Any], dict[str, Any]]:
        nominal, delay, long = (
            pair(slope * CONTRACT_IDLE_DT[variant], loss)
            for variant, loss in zip(("nominal", "window_delay", "window_delay_long"), losses, strict=True)
        )
        return magnitude_decline(long, delay, CONTRACT_ALPHA), contrast_floor(
            delay, nominal, (1.0, 1.0), CONTRACT_ALPHA
        )

    verdicts = {}
    static, static_step = ramp((0.0, 0.0, 0.0), CONTRACT_SLOPE)
    rotated = spectator_contract(_spectator_reads(1.0, 0.3, 1.0, 0.0), CONTRACT_ALPHA)
    if static["status"] != "fail" or static_step["status"] != "pass" or rotated["status"] != "fail":
        raise RuntimeError(f"a static detuning reads ramp {static}, floor {static_step}, spectator {rotated}")
    verdicts["static_detuning"] = "ramp fail, spectator fail"
    monotonic, _floor = ramp((0.0, 0.2, 0.4))
    if monotonic["status"] != "pass":
        raise RuntimeError(f"a monotonic dephasing fails the ramp: {monotonic}")
    verdicts["monotonic_dephasing"] = "ramp pass"
    dephased = spectator_contract(_spectator_reads(0.8, 0.4, 1.0, 0.0), CONTRACT_ALPHA)
    if dephased["status"] != "pass" or not math.isclose(dephased["measured_visibility"], 0.8, abs_tol=1e-4):
        raise RuntimeError(f"a qubit-2 readout dephasing fails the spectator contract: {dephased}")
    verdicts["spectator_dephasing"] = "spectator pass"
    step, step_floor = ramp((0.0, 0.3, 0.3))
    if step["status"] != "fail" or step_floor["status"] != "fail":
        raise RuntimeError(f"a one-time step reads ramp {step}, window_delay floor {step_floor}")
    verdicts["step"] = "ramp fail, window_delay below nominal"
    held = magnitude_decline(
        pair(0.0, 0.4), pair(0.0, 0.2), CONTRACT_ALPHA, -monotonic["upper_confidence_limit"] * 1.01
    )
    if held["status"] != "fail" or not held["herald_margin"] > 0:
        raise RuntimeError(f"a herald margin above the ramp's upper limit leaves it passing: {held}")
    from diagnostic_experiments import n21_orbit_rca_group, n21_orbit_variants, n21_spectator_members

    names = [member.name for member in n21_orbit_rca_group(415, 502, window_sweep=True).members]
    if (
        set(n21_orbit_variants(True)) != set(ORBIT_VARIANTS)
        or n21_spectator_members() != SPECTATOR_MEMBERS
        or [name for name in names if not is_orbit(name)] != list(SPECTATOR_MEMBERS)
    ):
        raise RuntimeError(f"the analyzer's orbit and spectator names differ from the planned members {names}")
    # Bitstrings put clbit 0 rightmost: "10" is qubit 2 read 1 with the control bit 0, label 2.
    module = sys.modules[__name__]
    synthetic = {"members": [{"name": "n21_orbit_nominal_feedback"}, *({"name": n} for n in SPECTATOR_MEMBERS)]}
    payloads = [{"registers": {REGISTER: {"bitstrings": ["01"]}}}] + [
        {"registers": {REGISTER: {"bitstrings": ["10", "00", "10"]}}} for _name in SPECTATOR_MEMBERS
    ]
    with (
        mock.patch.object(module, "_group", lambda _run: synthetic),
        mock.patch.object(module, "raw_pubs", lambda _run: payloads),
    ):
        tallied = spectator_counts(Path("."))
    if tallied is None or any(
        list(tallied[kind][quadrature]) != [1.0, 0.0, 2.0, 0.0]
        for kind in SPECTATOR_KINDS
        for quadrature in SPECTATOR_QUADRATURES
    ):
        raise RuntimeError(f"spectator_counts tallies {tallied}, not qubit 2 on clbit 1")
    if spectator_contract(None, CONTRACT_ALPHA)["status"] != "not_evaluable":
        raise RuntimeError("the spectator contract evaluates without spectator members")
    for planted in (0.0, 0.4, -2.5):
        turn = spectator_branch_phase(_spectator_reads(0.9, 0.3, 1.0, 0.0, planted)["measured"])
        if abs(turn["turn_rad"] - planted) > 5 * turn["standard_error_rad"] or turn["standard_error_rad"] > 0.05:
            raise RuntimeError(f"spectator_branch_phase reads {turn} for a planted turn of {planted} rad")
    rotated_only = spectator_contract(_spectator_reads(0.9, 0.3, 0.9, 0.3, 0.4), CONTRACT_ALPHA)
    if rotated_only["status"] != "pass":
        raise RuntimeError(f"a branch turn of 0.4 rad does not lower the pooled measured visibility: {rotated_only}")
    if (
        spectator_margin({"present": False}) != 0.0
        or spectator_margin(
            {
                "present": True,
                "admissible": True,
                "bits": {str(SPECTATOR_HERALD_BIT): {"excitation_spread_upper_limit": 0.002}},
            }
        )
        != 0.004
    ):
        raise RuntimeError("spectator_margin does not read twice the qubit-2 herald spread limit")
    return verdicts


def self_check() -> None:
    """Recover a known work phase from exact expected counts and reject the depolarizing baseline."""
    _check_exact_laws()
    _check_manifest_binding()
    _check_static_basins()
    _check_piecewise_exposure()
    _check_seed_ranking()
    _check_differences()
    _check_between_arm()
    verdicts = _check_window_sweep()
    readout = _readout(0.001, 0.006)
    truth = readout | {"round1": 0.1, "round2": 0.02, "phase_one": 0.5}
    counts = {
        arm: np.round(distribution(truth, feed_forward) * 4096)
        for arm, feed_forward in (("feedback", True), ("no_feedback", False))
    }
    arms = {"feedback": readout, "no_feedback": readout}
    phase = fit(counts, arms, MECHANISMS["work_phase_one"])
    baseline = fit(counts, arms, MECHANISMS["baseline_depolarizing"])
    if abs(phase["parameters"]["phase_one"] - 0.5) > 0.02 or phase["deviance"] > 0.05:
        raise RuntimeError(f"work-phase fit missed the planted phase: {phase['parameters']}")
    if baseline["deviance"] - phase["deviance"] < 3.84:
        raise RuntimeError("the depolarizing baseline fits a planted coherent phase")
    for feed_forward in (True, False):
        both = distribution(readout | {"phase_b0": 0.4, "phase_b1": 0.4}, feed_forward)
        if not np.allclose(both, distribution(readout | {"phase_one": 0.4}, feed_forward), atol=1e-12):
            raise RuntimeError("a phase in both recorded branches differs from an unconditional phase")
    half = distribution(readout | {"loss_b1": 0.5}, False)
    if np.allclose(half, distribution(readout, False), atol=1e-6):
        raise RuntimeError("branch dephasing leaves the no-feedback law unchanged")
    print(
        "N=21 orbit RCA: exact laws, manifest binding, seeded static basins, piecewise window exposure, "
        "regeneration tolerance, between-arm contracts and admissibility, planted-phase recovery, "
        f"branch-window, and baseline rejection checks pass; window sweep truths read {verdicts}"
    )


RETAINED = "rca-mechanism-fit.json"
SCHEMA_VERSION = "n21-orbit-rca-mechanism-fit-v2"


class PairFit:
    """Every mechanism fit of one feed-forward pair and its work-phase interval."""

    def __call__(
        self, item: tuple[dict[str, np.ndarray], dict[str, dict[str, float]]]
    ) -> tuple[dict[str, dict[str, Any]], list[list[float]]]:
        counts, arms = item
        models = {name: fit(counts, arms, extra) for name, extra in MECHANISMS.items()}
        return models, phase_interval(counts, arms, models["work_phase_one"])


def readout_sources(
    run: Path, roles: dict[str, dict[str, Any]], readout: tuple[float, float] | None
) -> dict[str, dict[str, Any]]:
    """Each member's assignment rates with their provenance: --readout's rates, or member_readouts."""
    if readout:
        writers = {qubit for role in roles.values() for qubit in (role["control"], role["terminal"])}
        if len(writers) != 1:
            raise SystemExit(f"--readout supplies one qubit's rates, but the members measure on {sorted(writers)}")
        fixed = _readout(*readout)
        return {name: fixed | {"source": "--readout"} for name in roles}
    return {
        name: entry | {"source": "retained placed-qubit calibration or properties at the record calibration"}
        for name, entry in member_readouts(run, roles).items()
    }


def build_report(run: Path, readout: tuple[float, float] | None) -> dict[str, Any]:
    """Every pair's mechanism fits and phase interval, and the joint fit, as rca-mechanism-fit.json holds them.

    The mechanism models place their depolarizing rounds and the window at
    the first measurement of the archived ISA, so a heralded run is refused;
    --between-arm evaluates it.
    """
    from qpe_diagnostics import has_herald

    if any(has_herald(circuit) for circuit in _circuits(run)):
        raise RuntimeError("the mechanism fit reads unheralded runs; --between-arm evaluates a heralded one")
    _check_exact_laws()
    pairs = measured_pairs(run)
    roles = window_roles(run)
    sources = readout_sources(run, roles, readout)
    readouts = {name: _model_readout(entry) for name, entry in sources.items()}
    report: dict[str, Any] = {"schema_version": SCHEMA_VERSION, "member_readout": sources, "pairs": {}}
    items = [
        (counts, {arm: readouts[f"{pair}_{arm}"] for arm in ("feedback", "no_feedback")})
        for pair, counts in pairs.items()
    ]
    for (pair, counts), (models, interval) in zip(
        pairs.items(), parallel.ordered_map(PairFit(), items, min_items=2), strict=True
    ):
        report["pairs"][pair] = {
            "measured_counts": {arm: values.astype(int).tolist() for arm, values in counts.items()},
            "models": models,
            "work_phase_95_interval": interval,
        }
        baseline = models["baseline_depolarizing"]["deviance"]
        comparisons = (len(MECHANISMS) - 1) * len(pairs)
        for model in models.values():
            threshold = float(chi2.ppf(1 - FAMILY_ALPHA / comparisons, max(1, model["added_parameters"])))
            model["family_wise_threshold"] = threshold
            model["improves_at_family_alpha"] = baseline - model["deviance"] > threshold
        print(f"{pair}: work phase {models['work_phase_one']['parameters']['phase_one']:+.3f} rad, 95% {interval}")
        for name, model in sorted(models.items(), key=lambda item: item[1]["deviance"])[:4]:
            params = ", ".join(f"{key}={value:.4f}" for key, value in model["parameters"].items())
            gain = baseline - model["deviance"]
            flag = "*" if model["improves_at_family_alpha"] else " "
            print(
                f"  {name:30s} G2={model['deviance']:8.2f} gain={gain:7.2f}{flag} "
                f"k+{model['added_parameters']}  {params}"
            )
    if len(pairs) > 1:
        joint = joint_quasistatic_fit(run, pairs, readouts)
        report["joint_quasistatic_detuning"] = joint
        if "skipped" in joint:
            print(f"joint quasi-static detuning skipped: {joint['skipped']}; {joint['unresolved']}")
        else:
            print(
                f"joint quasi-static detuning: G2={joint['deviance']:.2f} on {joint['degrees_of_freedom']} dof; "
                f"static-only G2={joint['static_detuning_only_deviance']:.2f}; {joint['parameters_rad_per_us']}"
            )
    piecewise = piecewise_fit(run, pairs, readouts)
    report["piecewise"] = piecewise
    if "skipped" in piecewise:
        print(f"exact-ISA window exposure skipped: {piecewise['skipped']}; {piecewise.get('unresolved', {})}")
    else:
        for label in ("piecewise", "single_gap", "no_detuning"):
            model = piecewise["models"][label]
            params = ", ".join(f"{key}={value:.4f}" for key, value in model["parameters"].items())
            print(f"exact-ISA {label:12s} G2={model['deviance']:8.2f} on {model['degrees_of_freedom']} dof  {params}")
        print(f"piecewise minus single-gap G2: {piecewise['piecewise_minus_single_gap_deviance']:+.3f}")
    return report


def serialize(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


# Finite-difference L-BFGS-B stopping points vary across numerical libraries.
# Compare the induced laws and likelihood at the retained replay precision;
# Pair-mechanism parameter-to-law consistency is checked at roundoff precision.
# Statistical significance establishes neither parameter identifiability nor
# the reproducibility of individual optimizer coordinates.
CHECK_REL_TOL = 1e-6
CHECK_ABS_TOL = 1e-6
# A fit's total deviance is stationary in its parameters at the optimum, so it
# reproduces to rounding, while its split across members and pairs moves at
# first order with the parameters' own rounding.
SPLIT_KEYS = ("member_deviance", "pair_deviance")
SPLIT_ABS_TOL = 1e-3


def differences(retained: Any, regenerated: Any, path: str = "") -> list[str]:
    """Paths where regenerated departs from retained: structure, keys, strings, integers and booleans
    exactly, floats within CHECK_REL_TOL or CHECK_ABS_TOL."""
    if isinstance(retained, dict) and isinstance(regenerated, dict):
        if retained.keys() != regenerated.keys():
            return [f"{path or '/'}: keys {sorted(retained.keys() ^ regenerated.keys())}"]
        return [item for key in retained for item in differences(retained[key], regenerated[key], f"{path}/{key}")]
    if isinstance(retained, list) and isinstance(regenerated, list):
        if len(retained) != len(regenerated):
            return [f"{path}: length {len(retained)} against {len(regenerated)}"]
        return [
            item
            for position, (old, new) in enumerate(zip(retained, regenerated, strict=True))
            for item in differences(old, new, f"{path}/{position}")
        ]
    if isinstance(retained, float) and isinstance(regenerated, float):
        split = any(f"/{key}/" in path for key in SPLIT_KEYS)
        if math.isclose(
            retained, regenerated, rel_tol=CHECK_REL_TOL, abs_tol=SPLIT_ABS_TOL if split else CHECK_ABS_TOL
        ):
            return []
        return [f"{path}: {retained!r} against {regenerated!r}"]
    if type(retained) is not type(regenerated) or retained != regenerated:
        return [f"{path}: {retained!r} against {regenerated!r}"]
    return []


def observable_view(report: dict[str, Any]) -> dict[str, Any]:
    """Observable replay view, retaining parameter names and comparing laws and deviances.

    The exposure models' rates are periodic, with basins of nearly equal
    deviance in several phase periods, so their values are masked as well,
    and so is the count of distinct grid seeds, which a near-tie among the
    lowest grid points decides; their deviances stay compared.
    """
    view: dict[str, Any] = json.loads(json.dumps(report))
    for pair in view["pairs"].values():
        for model in pair["models"].values():
            model["parameters"] = dict.fromkeys(model["parameters"])
    for name, model in view.get("piecewise", {}).get("models", {}).items():
        if name != "no_detuning":
            model["parameters"] = dict.fromkeys(model["parameters"])
            model["starts"] = None
    return view


def parameter_law_differences(report: dict[str, Any]) -> list[str]:
    """Require bounded pair-mechanism coordinates to reproduce their laws and likelihood."""
    found = []
    for pair_name, pair in report["pairs"].items():
        counts = {arm: np.asarray(values) for arm, values in pair["measured_counts"].items()}
        readouts = {
            arm: _model_readout(report["member_readout"][f"{pair_name}_{arm}"]) for arm in ("feedback", "no_feedback")
        }
        for name, model in pair["models"].items():
            parameters = model["parameters"]
            bounds = NUISANCE + MECHANISMS[name]
            path = f"/pairs/{pair_name}/models/{name}"
            if set(parameters) != {key for key, _low, _high in bounds} or any(
                isinstance(parameters[key], bool)
                or not isinstance(parameters[key], int | float)
                or not math.isfinite(parameters[key])
                or not low <= parameters[key] <= high
                for key, low, high in bounds
            ):
                found.append(f"{path}/parameters: coordinates differ from the bounded model")
                continue
            for arm, readout in readouts.items():
                expected = distribution(_with_excess(readout, parameters), arm == "feedback")
                recorded = np.asarray(model[f"{arm}_law"])
                if recorded.shape != expected.shape or not np.allclose(
                    recorded, expected, rtol=0.0, atol=64 * np.finfo(float).eps
                ):
                    found.append(f"{path}/{arm}_law: parameter vector disagrees with the recorded law")
            found.extend(differences(model["deviance"], deviance(counts, parameters, readouts), f"{path}/deviance"))
    return found


def replay_differences(retained: dict[str, Any], regenerated: dict[str, Any]) -> list[str]:
    """Validate both pair-mechanism parameterizations, then compare observable evidence."""
    return (
        parameter_law_differences(retained)
        + parameter_law_differences(regenerated)
        + differences(observable_view(retained), observable_view(regenerated))
    )


def check(run: Path) -> None:
    """Regenerate RUN's rca-mechanism-fit.json from its archived raw files and require it to agree.

    The retained file's readout provenance selects the readout: a file made
    with --readout supplies its own rates, and any other file reads the
    record's retained placed-qubit calibration.
    """
    retained = json.loads((run / RETAINED).read_text())
    sources = retained["member_readout"]
    readout = None
    if all(entry["source"] == "--readout" for entry in sources.values()):
        (first,) = {(entry["mid_e01"], entry["mid_e10"]) for entry in sources.values()}
        readout = first
    regenerated = json.loads(serialize(build_report(run, readout)))
    found = replay_differences(retained, regenerated)
    if found:
        raise SystemExit(f"{run / RETAINED} differs from the fit its archived raw files regenerate: {found[:5]}")
    print(
        f"{run / RETAINED}: pair-mechanism parameter laws verified; observable laws and likelihoods "
        f"regenerated from archived raw files within {CHECK_ABS_TOL:g}"
    )


BETWEEN_ARM_SCHEMA = "n21-orbit-between-arm-contracts-v2"
ORBIT_VARIANTS = ("nominal", "window_delay", "window_delay_long", "extra_readout", "window_echo")
ARMS = ("feedback", "no_feedback")
REFERENCE_MEMBER = "n21_orbit_nominal_feedback"
CONTRACTS = (
    "window_delay_phase_slope",
    "extra_readout_contrast",
    "window_echo_restoration",
    "window_delay_ramp",
    "spectator_window_dephasing",
)
# Spectator Ramsey members (diagnostic_experiments.n21_spectator_members):
# logical qubit 2 read in X or Y across the control's measurement or a
# reset_only idle of its length. Clbit 1 of the phase register holds the
# qubit-2 bit.
SPECTATOR_KINDS = ("measured", "reset_only")
SPECTATOR_QUADRATURES = ("x", "y")
SPECTATOR_MEMBERS = tuple(f"n21_spectator_{k}_{q}" for k in SPECTATOR_KINDS for q in SPECTATOR_QUADRATURES)
# The herald bit of logical qubit 2; its excitation maps |+> to |->.
SPECTATOR_HERALD_BIT = 2
# Bonferroni over the five contracts holds their family-wise error at FAMILY_ALPHA.
CONTRACT_ALPHA = FAMILY_ALPHA / len(CONTRACTS)
# A nominal pair exposed for under one sample time defines no phase slope.
MIN_SLOPE_EXPOSURE_DT = 1.0


def orbit_pair(variant: str) -> str:
    return f"n21_orbit_{variant}"


def normalized_coupling(coupling: dict[Any, dict[Any, Any]]) -> dict[int, dict[int, int]]:
    """A coupling with integer qubits, branches and signs, the form window_roles and its JSON both reduce to."""
    return {int(q): {int(b): int(sign) for b, sign in branches.items()} for q, branches in coupling.items()}


def coupling_json(coupling: dict[Any, dict[Any, Any]]) -> dict[str, dict[str, int]]:
    normalized = normalized_coupling(coupling)
    return {
        str(q): {str(b): sign for b, sign in sorted(branches.items())} for q, branches in sorted(normalized.items())
    }


def admissibility(roles: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Whether every family member carries one resolved, non-empty coupling, and which members break it.

    The contracts compare pairs through one map from window qubits to the
    work bit for 1, so every member of the ORBIT_VARIANTS pairs must be present, free
    of unresolved probes, and coupled exactly as the nominal feedback member.
    A no-feedback law is even in the work phase (window_roles), so a
    no-feedback member's signs are fixed only up to one global sign, which
    window_roles sets positive on its anchor qubit; such a member matches
    when its coupling or its global negation equals the reference, and
    orientation records the sign that maps it onto the reference.
    """
    expected = [f"{orbit_pair(variant)}_{arm}" for variant in ORBIT_VARIANTS for arm in ARMS]
    missing = [name for name in expected if name not in roles]
    reference = normalized_coupling(roles[REFERENCE_MEMBER]["coupling"]) if REFERENCE_MEMBER in roles else {}
    orientation: dict[str, int] = {}
    differing: dict[str, dict[str, dict[str, int]]] = {}
    for name, role in roles.items():
        coupling = normalized_coupling(role["coupling"])
        negated = {q: {b: -sign for b, sign in branches.items()} for q, branches in coupling.items()}
        if coupling and coupling == reference:
            orientation[name] = 1
        elif coupling and name.endswith("_no_feedback") and negated == reference:
            orientation[name] = -1
        else:
            differing[name] = coupling_json(coupling)
    unresolved = {name: list(role["unresolved"]) for name, role in roles.items() if role["unresolved"]}
    return {
        "admissible": not (missing or differing or unresolved),
        "reference_member": REFERENCE_MEMBER,
        "reference_coupling": coupling_json(reference),
        "orientation": orientation,
        "differing": differing,
        "unresolved": unresolved,
        "missing": missing,
    }


def not_admissible(admitted: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        name: {
            "status": "not_admissible",
            "differing": admitted["differing"],
            "unresolved": admitted["unresolved"],
            "missing": admitted["missing"],
        }
        for name in CONTRACTS
    }


def pair_phase_exposure(
    exposure: dict[str, dict[int, dict[int, float]]], orientation: dict[str, int], variant: str
) -> float:
    """Mean coupling-weighted signed exposure in dt over a pair's members and both recorded branches.

    Each member's exposure enters in the reference member's orientation, so
    a no-feedback member's global sign convention cancels.
    """
    values = [
        orientation[name] * sum(exposure[name][branch].values())
        for name in (f"{orbit_pair(variant)}_{arm}" for arm in ARMS)
        for branch in (0, 1)
    ]
    return sum(values) / len(values)


def arm_idle(roles: dict[str, dict[str, Any]], variant: str, arm: str, qubit: int) -> float:
    """Idle time in dt of one window qubit in one member, driven echo pulses excluded."""
    window = roles[f"{orbit_pair(variant)}_{arm}"]["windows"][qubit]
    return float(window["after"] - window["before"] - sum(length for _start, length in window["x"]))


def signed_contrast(counts: np.ndarray) -> tuple[float, float]:
    """p1 - p3 of one arm's labeled counts and its multinomial variance (p1 + p3 - (p1 - p3)^2) / n."""
    shots = float(counts.sum())
    one, three = float(counts[1]) / shots, float(counts[3]) / shots
    return one - three, (one + three - (one - three) ** 2) / shots


def contrast_difference(arms: dict[str, np.ndarray]) -> tuple[float, float]:
    """Feedback minus no-feedback signed contrast of one pair and its variance; the arms are separate PUBs."""
    feedback, feedback_variance = signed_contrast(arms["feedback"])
    control, control_variance = signed_contrast(arms["no_feedback"])
    return feedback - control, feedback_variance + control_variance


def contrast_magnitude(arms: dict[str, np.ndarray]) -> tuple[float, float]:
    """m = hypot(fb1 - fb3, nf3 - nf1), the pair's contrast with the work phase removed, and its variance.

    The noiseless law (distribution) gives fb1 - fb3 = c sin(phi) / 4 and
    nf3 - nf1 = c cos(phi) / 4 at work phase phi and work-bit coherence c, so
    the signed contrast difference c (sin(phi) + cos(phi)) / 4 moves with
    phi while m is c / 4. The delta method gives var(m) = (x^2 var x + y^2
    var y) / m^2 from each arm's multinomial variance; at m = 0 the gradient
    is undefined and var x + var y, the mean square of m at zero coherence,
    takes its place. hypot is biased upward at small m: when the sampling
    noise of x and y is comparable to m, E[m] exceeds c / 4, so a
    near-zero reference contrast overstates the coherence it bounds.
    """
    feedback, feedback_variance = signed_contrast(arms["feedback"])
    control, control_variance = signed_contrast(arms["no_feedback"])
    magnitude = math.hypot(feedback, control)
    if magnitude == 0.0:
        return magnitude, feedback_variance + control_variance
    variance = (feedback**2 * feedback_variance + control**2 * control_variance) / magnitude**2
    return magnitude, variance


def contrast_floor(
    test: dict[str, np.ndarray],
    reference: dict[str, np.ndarray],
    factors: tuple[float, float],
    alpha: float,
    margin: float = 0.0,
) -> dict[str, Any]:
    """One-sided test that a pair's contrast magnitude reaches the reference pair's, each arm scaled by its factor.

    x = fb1 - fb3 comes from the feedback PUB and y = nf3 - nf1 from the
    no-feedback PUB, so each decays by its own arm's factor and the bound is
    hypot(f_fb x_ref, f_nf y_ref). m_test - bound is normal to first order
    in the multinomial counts of four independent PUBs; the delta method
    gives the bound's variance (f_fb^4 x^2 var x + f_nf^4 y^2 var y) /
    bound^2, added to var m_test (contrast_magnitude). The contract fails
    only when the upper (1 - alpha) confidence limit lies below zero, so at
    the bound sampling noise fails it with probability alpha. The signed
    contrast difference of each pair is reported and decides nothing, since
    a work phase moves it.

    margin is subtracted from the statistic before the decision: a heralded
    run's initial-excitation spread can move m_test - bound by up to the
    herald's contract_shift_upper_limit (herald_admission), so a pass then
    holds for every spread the herald's simultaneous upper limits allow.
    """
    feedback_factor, control_factor = factors
    tested, tested_variance = contrast_magnitude(test)
    x, x_variance = signed_contrast(reference["feedback"])
    y, y_variance = signed_contrast(reference["no_feedback"])
    bound = math.hypot(feedback_factor * x, control_factor * y)
    if bound == 0.0:
        bound_variance = feedback_factor**2 * x_variance + control_factor**2 * y_variance
    else:
        bound_variance = (feedback_factor**4 * x**2 * x_variance + control_factor**4 * y**2 * y_variance) / bound**2
    statistic = tested - bound - margin
    error = math.sqrt(tested_variance + bound_variance)
    quantile = float(norm.ppf(1 - alpha))
    upper = statistic + quantile * error
    return {
        "status": "pass" if upper >= 0 else "fail",
        "contrast_magnitude": tested,
        "reference_contrast_magnitude": contrast_magnitude(reference)[0],
        "signed_contrast_difference": contrast_difference(test)[0],
        "reference_signed_contrast_difference": contrast_difference(reference)[0],
        "feedback_factor": feedback_factor,
        "no_feedback_factor": control_factor,
        "bound": bound,
        "statistic": statistic,
        "standard_error": error,
        "one_sided_quantile": quantile,
        "upper_confidence_limit": upper,
    } | ({"herald_margin": margin} if margin else {})


def magnitude_decline(
    test: dict[str, np.ndarray], reference: dict[str, np.ndarray], alpha: float, margin: float = 0.0
) -> dict[str, Any]:
    """One-sided test that a pair's contrast magnitude lies below the reference pair's.

    m_test - m_ref is normal to first order in the multinomial counts of the
    four independent PUBs, with variance var m_test + var m_ref
    (contrast_magnitude). The contract passes only when the upper (1 - alpha)
    confidence limit plus margin lies below zero, so a pair whose magnitude
    equals the reference's passes with probability at most alpha. margin, a
    heralded run's contract_shift_upper_limit, is added against the pass: a
    member spread of the initial excitation that the herald leaves possible
    cannot produce it.
    """
    tested, tested_variance = contrast_magnitude(test)
    bound, bound_variance = contrast_magnitude(reference)
    statistic = tested - bound
    error = math.sqrt(tested_variance + bound_variance)
    quantile = float(norm.ppf(1 - alpha))
    upper = statistic + quantile * error
    return {
        "status": "pass" if upper + margin < 0 else "fail",
        "contrast_magnitude": tested,
        "reference_contrast_magnitude": bound,
        "statistic": statistic,
        "standard_error": error,
        "one_sided_quantile": quantile,
        "upper_confidence_limit": upper,
    } | ({"herald_margin": margin} if margin else {})


def spectator_visibility(counts: dict[str, np.ndarray]) -> tuple[float, float, float, float]:
    """<X>, <Y>, R = hypot(<X>, <Y>) of qubit 2 and var R from one spectator kind's x and y counts.

    Each count vector runs over control + 2 * qubit-2 bit, so <Q> = P(bit 0)
    - P(bit 1) with multinomial variance (1 - <Q>^2) / n. The delta method
    gives var R = (X^2 var X + Y^2 var Y) / R^2; at R = 0, var X + var Y.
    """
    values = []
    for quadrature in SPECTATOR_QUADRATURES:
        vector = counts[quadrature]
        shots = float(vector.sum())
        expectation = float(vector[0] + vector[1] - vector[2] - vector[3]) / shots
        values.append((expectation, (1.0 - expectation**2) / shots))
    (x, x_variance), (y, y_variance) = values
    visibility = math.hypot(x, y)
    if visibility == 0.0:
        return x, y, visibility, x_variance + y_variance
    return x, y, visibility, (x**2 * x_variance + y**2 * y_variance) / visibility**2


def spectator_branch_phase(counts: dict[str, np.ndarray]) -> dict[str, Any]:
    """Qubit 2's phase turn between the measured control's recorded branches, with its normal-approximation SE.

    Each recorded control bit b selects the shots whose qubit-2 X and Y
    reads give (<X>_b, <Y>_b) and phase phi_b = atan2(<Y>_b, <X>_b); the
    turn phi_1 - phi_0, wrapped to (-pi, pi], estimates a ZZ coupling between
    the control and qubit 2 integrated over the window. The delta method
    gives var phi_b = (Y^2 var X + X^2 var Y) / R^4. The turn is descriptive
    and decides no contract.
    """
    phases = []
    for branch in (0, 1):
        values = []
        for quadrature in SPECTATOR_QUADRATURES:
            zero, one = float(counts[quadrature][branch]), float(counts[quadrature][branch + 2])
            shots = zero + one
            if shots == 0:
                return {"status": "not_evaluable", "reason": f"no shots record control bit {branch}"}
            expectation = (zero - one) / shots
            values.append((expectation, (1.0 - expectation**2) / shots))
        (x, x_variance), (y, y_variance) = values
        radius = x * x + y * y
        if radius == 0.0:
            return {"status": "not_evaluable", "reason": f"branch {branch} reads zero visibility"}
        phases.append((math.atan2(y, x), (y * y * x_variance + x * x * y_variance) / radius**2))
    turn = math.remainder(phases[1][0] - phases[0][0], math.tau)
    return {
        "status": "descriptive",
        "branch_phase_rad": [phases[0][0], phases[1][0]],
        "turn_rad": turn,
        "standard_error_rad": math.sqrt(phases[0][1] + phases[1][1]),
    }


def spectator_contract(
    spectators: dict[str, dict[str, np.ndarray]] | None, alpha: float, margin: float = 0.0
) -> dict[str, Any]:
    """One-sided test that qubit 2's visibility across the measured control lies below the reset_only reference.

    R_measured - R_reset_only is normal to first order in the four PUBs'
    multinomial counts (spectator_visibility); the contract passes when the
    upper (1 - alpha) confidence limit plus margin lies below zero. A static
    detuning of qubit 2 rotates (<X>, <Y>) and leaves R unchanged, so a pass
    names a coherence loss of qubit 2 that the control's measurement adds.
    margin is the R shift the spectator herald leaves possible
    (spectator_margin). A run without the four spectator members reads
    not_evaluable.
    """
    if spectators is None or set(spectators) != set(SPECTATOR_KINDS):
        return {"status": "not_evaluable", "reason": "the record holds no spectator Ramsey members"}
    read = {kind: spectator_visibility(spectators[kind]) for kind in SPECTATOR_KINDS}
    statistic = read["measured"][2] - read["reset_only"][2]
    error = math.sqrt(read["measured"][3] + read["reset_only"][3])
    quantile = float(norm.ppf(1 - alpha))
    upper = statistic + quantile * error
    return {
        "status": "pass" if upper + margin < 0 else "fail",
        **{
            f"{kind}_{label}": read[kind][index]
            for kind in SPECTATOR_KINDS
            for index, label in enumerate(("x_expectation", "y_expectation", "visibility"))
        },
        "statistic": statistic,
        "standard_error": error,
        "one_sided_quantile": quantile,
        "upper_confidence_limit": upper,
    } | ({"herald_margin": margin} if margin else {})


def spectator_counts(run: Path) -> dict[str, dict[str, np.ndarray]] | None:
    """Per spectator kind and quadrature, counts over control + 2 * qubit-2 bit; None without spectator members."""
    members = [member["name"] for member in _group(run)["members"]]
    if not set(SPECTATOR_MEMBERS) & set(members):
        return None
    found: dict[str, dict[str, np.ndarray]] = {}
    for name, payload in zip(members, raw_pubs(run), strict=True):
        if name not in SPECTATOR_MEMBERS:
            continue
        kind, quadrature = name.removeprefix("n21_spectator_").rsplit("_", 1)
        tally = Counter(int(value[1]) + 2 * int(value[0]) for value in payload["registers"][REGISTER]["bitstrings"])
        found.setdefault(kind, {})[quadrature] = np.array([tally[label] for label in range(4)], dtype=float)
    if any(set(found.get(kind, {})) != set(SPECTATOR_QUADRATURES) for kind in SPECTATOR_KINDS):
        raise RuntimeError(f"the record holds spectator members {sorted(found)}, not all of {SPECTATOR_MEMBERS}")
    return found


def spectator_margin(herald: dict[str, Any]) -> float:
    """The R shift an admitted spectator herald leaves possible; zero without one, whose contract is refused.

    The spectator admission tests the spread against herald_bound, the
    orbit's threshold; the margin, not that threshold, carries the spectator
    contract's protection.

    An initial excitation of qubit 2 maps |+> to |->, so an excited fraction
    eps scales (<X>, <Y>) by 1 - 2 eps; a member spread at most Delta moves
    each kind's R by at most 2 Delta, and the difference of the two kinds by
    at most 2 Delta with Delta the simultaneous upper limit of the qubit-2
    herald bit over the spectator members (herald_admission). Excitations of
    the other qubits leave qubit 2's state alone.
    """
    if not herald["present"] or not herald["admissible"]:
        return 0.0
    return 2.0 * float(herald["bits"][str(SPECTATOR_HERALD_BIT)]["excitation_spread_upper_limit"])


class PhaseFit:
    """The work_phase_one fit of one (counts, arm readouts) pair."""

    def __call__(self, item: tuple[dict[str, np.ndarray], dict[str, dict[str, float]]]) -> dict[str, Any]:
        counts, arms = item
        return fit(counts, arms, MECHANISMS["work_phase_one"])


def phase_fits(
    pairs: dict[str, dict[str, np.ndarray]], readouts: dict[str, dict[str, float]]
) -> dict[str, dict[str, Any]]:
    """work_phase_one fits of the nominal and window_delay pairs, the pairs the phase-slope contract compares."""
    variants = ("nominal", "window_delay")
    items = [
        (pairs[orbit_pair(variant)], {arm: readouts[f"{orbit_pair(variant)}_{arm}"] for arm in ARMS})
        for variant in variants
    ]
    return dict(zip(variants, parallel.ordered_map(PhaseFit(), items, min_items=2), strict=True))


# Odd grid size, so the periodic profile has an exact trigonometric
# interpolant; the dense search steps an eighth of a grid step in both
# arguments, and the lowest local minima are refined.
SLOPE_GRID = 121
SLOPE_DENSE_PER_STEP = 8
SLOPE_CANDIDATES = 3
_NODES = 0.5 - 0.5 * np.cos(np.pi * (2 * np.arange(5) + 1) / 10)
_PHASES = (0.0, 2 * math.pi / 3, 4 * math.pi / 3)


class PhaseLaw:
    """distribution() of one arm as an exact expansion in round1, round2 and phase_one.

    Each depolarizing round is affine in its strength on each of its four
    qubits, so the law is a polynomial of degree 4 in round1 and in round2,
    and phase_one acts once as diag(1, e^{i phi}) on the work bit for 1, so
    the law is a + b cos(phi) + c sin(phi) in it. Five Chebyshev nodes per
    strength and three phases determine the coefficients; construction
    requires the expansion to reproduce distribution() at an off-node point.
    """

    def __init__(self, readout: dict[str, float], feed_forward: bool) -> None:
        samples = np.array(
            [
                [
                    [
                        distribution(readout | {"round1": one, "round2": two, "phase_one": phase}, feed_forward)
                        for phase in _PHASES
                    ]
                    for two in _NODES
                ]
                for one in _NODES
            ]
        )
        inverse = np.linalg.inv(np.vander(_NODES, 5, increasing=True))
        trig = np.linalg.inv(np.array([[1.0, math.cos(phase), math.sin(phase)] for phase in _PHASES]))
        self.coefficients = np.einsum("ai,bj,tk,ijkc->abtc", inverse, inverse, trig, samples)
        probe = readout | {"round1": 0.37, "round2": 0.61, "phase_one": 1.3}
        if not np.allclose(self(0.37, 0.61, 1.3), distribution(probe, feed_forward), rtol=0.0, atol=1e-10):
            raise RuntimeError("the polynomial-trigonometric law differs from distribution()")

    def at_phase(self, phase: float) -> np.ndarray:
        return np.einsum("abtc,t->abc", self.coefficients, [1.0, math.cos(phase), math.sin(phase)])

    def __call__(self, round1: float, round2: float, phase: float) -> np.ndarray:
        powers = np.arange(5)
        return np.einsum("a,b,abc->c", round1**powers, round2**powers, self.at_phase(phase))


class FastPhaseProfile:
    """PhaseProfile of one pair evaluated through PhaseLaw: the same objective, start, method and bounds."""

    def __init__(
        self, counts: dict[str, np.ndarray], readouts: dict[str, dict[str, float]], best: dict[str, Any]
    ) -> None:
        self.counts = counts
        self.laws = {arm: PhaseLaw(readouts[arm], arm == "feedback") for arm in ARMS}
        self.start = np.array([best["parameters"][name] for name, _low, _high in NUISANCE])
        self.bounds = [(low, high) for _name, low, high in NUISANCE]

    def objective(self, vector: np.ndarray, tables: dict[str, np.ndarray]) -> float:
        powers = np.arange(5)
        one, two = float(vector[0]) ** powers, float(vector[1]) ** powers
        total = 0.0
        for arm, table in tables.items():
            observed = self.counts[arm]
            expected = np.clip(np.einsum("a,b,abc->c", one, two, table), 1e-12, None) * observed.sum()
            positive = observed > 0
            total += 2 * float(np.sum(observed[positive] * np.log(observed[positive] / expected[positive])))
        return total

    def __call__(self, phase: float) -> float:
        tables = {arm: law.at_phase(phase) for arm, law in self.laws.items()}
        return float(minimize(self.objective, self.start, args=(tables,), method="L-BFGS-B", bounds=self.bounds).fun)


def periodic_interpolant(values: np.ndarray, phases: np.ndarray) -> np.ndarray:
    """The trigonometric interpolant of values on the odd grid -pi + 2 pi j / N, evaluated at phases."""
    count = len(values)
    coefficients = np.fft.fft(values) / count
    frequencies = np.fft.fftfreq(count, 1.0 / count)
    return np.real(np.exp(1j * np.outer(phases + math.pi, frequencies)) @ coefficients)


class SlopeSum:
    """[D_n(phi) - D_n,min] + [D_d(r phi) - D_d,min] from two profiles and their minima."""

    def __init__(self, nominal: Any, delay: Any, minima: tuple[float, float], ratio: float) -> None:
        self.nominal, self.delay, self.minima, self.ratio = nominal, delay, minima, ratio

    def __call__(self, phi: float) -> float:
        return self.nominal(phi) - self.minima[0] + self.delay(self.ratio * phi) - self.minima[1]


class RefineSlope:
    """Bounded scalar minimum of the PhaseLaw slope sum within one grid step, and the exact sum there."""

    def __init__(self, fast: SlopeSum, exact: SlopeSum, step: float, span: float) -> None:
        self.fast, self.exact, self.step, self.span = fast, exact, step, span

    def __call__(self, center: float) -> tuple[float, float]:
        from scipy.optimize import minimize_scalar

        bounds = (max(-self.span, center - self.step), min(self.span, center + self.step))
        phi = float(minimize_scalar(self.fast, bounds=bounds, method="bounded", options={"xatol": 1e-6}).x)
        return self.exact(phi), phi


class SlopeProfiles:
    """The nominal and window_delay pairs' exact and PhaseLaw profiles, minima and periodic grid profiles.

    They depend on counts, readouts and fits alone, so families that differ
    only in their windows share them. Each minimum is the work_phase_one
    fit's deviance, the joint minimum over phase and nuisances.
    """

    def __init__(
        self,
        pairs: dict[str, dict[str, np.ndarray]],
        readouts: dict[str, dict[str, float]],
        fits: dict[str, dict[str, Any]],
    ) -> None:
        self.variants = ("nominal", "window_delay")
        self.counts = {variant: pairs[orbit_pair(variant)] for variant in self.variants}
        self.arms = {
            variant: {arm: readouts[f"{orbit_pair(variant)}_{arm}"] for arm in ARMS} for variant in self.variants
        }
        self.fits = fits
        self.exact = {v: PhaseProfile(self.counts[v], self.arms[v], fits[v]) for v in self.variants}
        self.fast = {v: FastPhaseProfile(self.counts[v], self.arms[v], fits[v]) for v in self.variants}
        self.minima = (fits["nominal"]["deviance"], fits["window_delay"]["deviance"])
        grid = [float(phase) for phase in -math.pi + 2 * math.pi * np.arange(SLOPE_GRID) / SLOPE_GRID]
        self.values = {v: np.array(parallel.ordered_map(self.fast[v], grid, min_items=2)) for v in self.variants}


def phase_slope_contract(
    profiles: SlopeProfiles,
    roles: dict[str, dict[str, Any]],
    orientation: dict[str, int],
    dt: float,
    alpha: float,
    render_set: bool,
) -> dict[str, Any]:
    """Likelihood-ratio test that the nominal and window_delay pairs share one static phase slope.

    A static detuning shared by the coupled qubits adds work phase in
    proportion to coupling-weighted exposure (pair_phase_exposure), so a
    slope s gives the nominal pair phase phi = s E_n and the window_delay
    pair phase r phi with r = E_d / E_n. Each pair's profiled deviance
    (PhaseProfile) is 2 pi periodic in its own phase, so every alias phi +
    2 pi k of the nominal phase is a distinct slope with its own window_delay
    prediction; |phi| <= EXPOSURE_RATE_BOUND (rad/us) times the nominal
    exposure time bounds k. The statistic is the minimum over that range of
    [D_n(phi) - D_n,min] + [D_d(r phi) - D_d,min], two free phases against
    one free slope, so the contract passes when it lies within the
    one-parameter chi-square quantile at 1 - alpha. Both pairs' uncertainty
    enters through their profiles. Aliases closer than the profiles resolve
    let a wrong slope pass, so the test's power falls as the bound and the
    exposures grow.

    Search: the trigonometric interpolants of the SlopeProfiles grids locate
    the local minima of the sum on a phi grid of SLOPE_DENSE_PER_STEP points
    per grid step in both arguments; the SLOPE_CANDIDATES lowest are refined
    by bounded scalar minimization of the PhaseLaw sum within one grid step,
    and the exact PhaseProfile sum at each refined phase decides. render_set
    adds window_delay's own confidence set on phase_interval's grid.
    """
    coupling = normalized_coupling(roles[REFERENCE_MEMBER]["coupling"])
    if any(set(branches) != {0, 1} or len(set(branches.values())) != 1 for branches in coupling.values()):
        return {
            "status": "not_evaluable",
            "reason": "a coupled qubit phases one recorded branch, or the two with opposite signs, "
            "so the window phase is not the unconditional work phase work_phase_one fits",
        }
    exposure = role_exposure(roles)
    nominal_exposure = pair_phase_exposure(exposure, orientation, "nominal")
    delay_exposure = pair_phase_exposure(exposure, orientation, "window_delay")
    if abs(nominal_exposure) < MIN_SLOPE_EXPOSURE_DT:
        return {
            "status": "not_evaluable",
            "reason": f"the nominal pair's signed exposure {nominal_exposure:g} dt defines no phase slope",
        }
    ratio = delay_exposure / nominal_exposure
    dt_us = dt * 1e6
    span = EXPOSURE_RATE_BOUND * abs(nominal_exposure) * dt_us
    step = 2 * math.pi / SLOPE_GRID / max(1.0, abs(ratio))
    dense = np.linspace(-span, span, max(3, math.ceil(2 * span * SLOPE_DENSE_PER_STEP / step) + 1))
    summed = periodic_interpolant(profiles.values["nominal"], dense) + periodic_interpolant(
        profiles.values["window_delay"], ratio * dense
    )
    local = [
        index
        for index in range(len(dense))
        if (index == 0 or summed[index] <= summed[index - 1])
        and (index == len(dense) - 1 or summed[index] <= summed[index + 1])
    ]
    centers = [float(dense[i]) for i in sorted(local, key=lambda i: (summed[i], i))[:SLOPE_CANDIDATES]]
    refine = RefineSlope(
        SlopeSum(profiles.fast["nominal"], profiles.fast["window_delay"], profiles.minima, ratio),
        SlopeSum(profiles.exact["nominal"], profiles.exact["window_delay"], profiles.minima, ratio),
        step,
        span,
    )
    refined = parallel.ordered_map(refine, centers, min_items=2)
    statistic, phi = min(refined)
    threshold = float(chi2.ppf(1 - alpha, 1))
    result: dict[str, Any] = {
        "status": "pass" if statistic <= threshold else "fail",
        "statistic": statistic,
        "chi2_threshold": threshold,
        "level": 1 - alpha,
        "nominal_phase": phi,
        "nominal_phase_wraps": round((phi - math.remainder(phi, 2 * math.pi)) / (2 * math.pi)),
        "window_delay_phase": ratio * phi,
        "slope_rad_per_dt": phi / nominal_exposure,
        "slope_rad_per_us": phi / (nominal_exposure * dt_us),
        "nominal_exposure_dt": nominal_exposure,
        "window_delay_exposure_dt": delay_exposure,
        "exposure_ratio": ratio,
        "nominal_phase_bound": span,
        "nominal_fit_phase": profiles.fits["nominal"]["parameters"]["phase_one"],
        "window_delay_fit_phase": profiles.fits["window_delay"]["parameters"]["phase_one"],
        "candidates": [{"nominal_phase": at, "statistic": value} for value, at in refined],
    }
    if render_set:
        result["confidence_set_grid_segments"] = phase_interval(
            profiles.counts["window_delay"], profiles.arms["window_delay"], profiles.fits["window_delay"], threshold
        )
    return result


def readout_contract(
    pairs: dict[str, dict[str, np.ndarray]],
    roles: dict[str, dict[str, Any]],
    dt: float,
    t2_us: dict[str, dict[int, float]],
    alpha: float,
    nominal_t2_us: dict[str, dict[int, float]] | None = None,
    margin: float = 0.0,
) -> dict[str, Any]:
    """extra_readout's contrast magnitude stays above the nominal one dephased over each arm's added idle time.

    In each arm, coupled qubit q idles t_q longer in the extra_readout member
    than in the nominal one (arm_idle, floored at zero since dephasing only
    lowers coherence), so that arm's contrast component decays by
    exp(-sum_q t_q / T2_q) over the coupled qubits, with T2_q of the arm's
    extra_readout member (arm_t2_us, keyed by arm); contrast_floor bounds the
    magnitude with the two arm factors at alpha. A coupling that holds only
    one of the work bits for 1 and 16 keeps one term, which raises the bound.
    The factor carries the added idle alone, so it holds only where the
    arm's nominal member executed at the same T2 (nominal_t2_us); a coupled
    qubit whose T2 differs between the two members dephases their common
    circuit unequally, and the contract is not_evaluable.
    """
    qubits = sorted(normalized_coupling(roles[REFERENCE_MEMBER]["coupling"]))
    absent = sorted({qubit for arm in ARMS for qubit in qubits if not t2_us.get(arm, {}).get(qubit)})
    if absent:
        return {"status": "not_evaluable", "reason": f"the record retains no T2 for coupled qubits {absent}"}
    if nominal_t2_us is not None:
        differing = {
            arm: [qubit for qubit in qubits if nominal_t2_us.get(arm, {}).get(qubit) != t2_us[arm][qubit]]
            for arm in ARMS
        }
        if any(differing.values()):
            return {
                "status": "not_evaluable",
                "reason": "the nominal and extra_readout members executed at different T2 on coupled qubits",
                "differing_t2_qubits": {arm: found for arm, found in differing.items() if found},
            }
    added = {
        arm: {
            qubit: max(0.0, arm_idle(roles, "extra_readout", arm, qubit) - arm_idle(roles, "nominal", arm, qubit))
            for qubit in qubits
        }
        for arm in ARMS
    }
    # Backend properties report T2 in microseconds (live_run.placed_qubit_calibration).
    factors = tuple(
        math.exp(-sum(added[arm][qubit] * dt / (t2_us[arm][qubit] * 1e-6) for qubit in qubits)) for arm in ARMS
    )
    result = contrast_floor(
        pairs[orbit_pair("extra_readout")], pairs[orbit_pair("nominal")], (factors[0], factors[1]), alpha, margin
    )
    return result | {
        "added_idle_dt": {arm: {str(qubit): added[arm][qubit] for qubit in qubits} for arm in ARMS},
        "t2_us": {arm: {str(qubit): t2_us[arm][qubit] for qubit in qubits} for arm in ARMS},
        "dt_seconds": dt,
    }


def contract_results(
    roles: dict[str, dict[str, Any]],
    pairs: dict[str, dict[str, np.ndarray]],
    readouts: dict[str, dict[str, float]],
    dt: float,
    t2_us: dict[str, dict[int, float]],
    profiles: SlopeProfiles | None = None,
    render_set: bool = False,
    nominal_t2_us: dict[str, dict[int, float]] | None = None,
    herald_margin: float = 0.0,
    spectators: dict[str, dict[str, np.ndarray]] | None = None,
    spectator_herald_margin: float = 0.0,
) -> dict[str, dict[str, Any]]:
    """Every between-arm contract's status and deciding numbers, each at CONTRACT_ALPHA.

    The contracts are preregistered, their statistics, levels and decision
    rules independent of any run's counts:
    window_delay_phase_slope (phase_slope_contract), extra_readout_contrast
    (readout_contract), and window_echo_restoration, which passes when the
    upper confidence limit of the window_echo contrast magnitude minus the
    nominal one reaches zero (contrast_floor at factors 1),
    window_delay_ramp, which passes when the window_delay_long magnitude lies
    below the window_delay one (magnitude_decline: a coherence loss that
    grows with the added idle; a one-time loss at the first added idle
    fails it), and spectator_window_dephasing (spectator_contract). A family
    that fails admissibility reports every contract not_admissible.
    herald_margin (a heralded run's contract_shift_upper_limit) counts
    against every magnitude contract's pass: subtracted from the floors'
    statistics and added to the ramp's upper limit; spectator_herald_margin
    counts against the spectator contract's pass.
    """
    admitted = admissibility(roles)
    if not admitted["admissible"]:
        return not_admissible(admitted)
    if profiles is None:
        profiles = SlopeProfiles(pairs, readouts, phase_fits(pairs, readouts))
    return {
        "window_delay_phase_slope": phase_slope_contract(
            profiles, roles, admitted["orientation"], dt, CONTRACT_ALPHA, render_set
        ),
        "extra_readout_contrast": readout_contract(
            pairs, roles, dt, t2_us, CONTRACT_ALPHA, nominal_t2_us, herald_margin
        ),
        "window_echo_restoration": contrast_floor(
            pairs[orbit_pair("window_echo")], pairs[orbit_pair("nominal")], (1.0, 1.0), CONTRACT_ALPHA, herald_margin
        ),
        "window_delay_ramp": magnitude_decline(
            pairs[orbit_pair("window_delay_long")], pairs[orbit_pair("window_delay")], CONTRACT_ALPHA, herald_margin
        ),
        "spectator_window_dephasing": spectator_contract(spectators, CONTRACT_ALPHA, spectator_herald_margin),
    }


def arm_t2_us(run: Path, variant: str = "extra_readout") -> dict[str, dict[int, float]]:
    """Per arm, T2 in microseconds of each placed qubit at the variant member's calibration.

    The extra_readout member holds the added idle the readout contract
    dephases, so its PUB's calibration (execution_calibration) sets T2; the
    nominal member's T2 must equal it (readout_contract).
    """
    calibrations = execution_calibration(run)
    return {
        arm: {
            int(qubit): float(values["T2"])
            for qubit, values in calibrations[f"{orbit_pair(variant)}_{arm}"]["values"].items()
            if "T2" in values
        }
        for arm in ARMS
    }


# Initialization herald admission. Herald bit k reads logical qubit k at its
# initial physical qubit before the program: the control, then the work bits
# for 1, 4 and 16 (qpe_diagnostics.n21_orbit_diagnostic).
HERALD_ROLES = ("control", "work_1", "work_4", "work_16")
# An excitation eps_k of herald bit k mixes eps_k of the excited law into a
# member, moving its arm's signed score s by eps_k (s_k - s). The exact ideal
# laws give |s_k - s| <= c_k m with c = 2 for the control (s_k = -s), 1 for
# work 1 (s_k = 0) and 2 for work 4 and 16 (s_k at another phase of the same
# magnitude); _check_herald_sensitivity verifies these coefficients.
HERALD_SENSITIVITY = (2.0, 1.0, 2.0, 2.0)
# contrast_magnitude reads m = c / 4 with work-bit coherence c <= 1.
CONTRAST_CEILING = 0.25
# The admission bound moves a magnitude contract by at most this fraction of
# its minimum detectable deficit.
HERALD_MDE_FRACTION = 0.25
MAGNITUDE_POWER = 0.8
HERALD_ALPHA = 0.05
HERALD_DESIGN_SHOTS = 27648


def magnitude_mde(shots: int) -> float:
    """Minimum detectable deficit of a magnitude contract at CONTRACT_ALPHA and MAGNITUDE_POWER.

    Each arm's labeled law puts 1/2 on outcomes 1 and 3 (the first bit is
    uniform), so the multinomial variance (p1 + p3 - s^2) / n of a signed
    score is at most 1 / (2 n), and the delta method gives var m <= 1 / (2 n)
    per pair. With factors at most 1, m_test - bound has variance at most
    1 / n, so the deficit the one-sided test at CONTRACT_ALPHA detects with
    power MAGNITUDE_POWER is (z_(1 - alpha) + z_power) / sqrt(n): 0.01905 at
    HERALD_DESIGN_SHOTS.
    """
    return float(norm.ppf(1 - CONTRACT_ALPHA) + norm.ppf(MAGNITUDE_POWER)) / math.sqrt(shots)


def herald_bound(shots: int) -> float:
    """Largest member spread B of the initial excitation on every herald bit that the admission accepts.

    A member-dependent excitation with spread Delta_k on herald bit k moves
    each pair's contrast vector by at most m sum_k c_k Delta_k
    (HERALD_SENSITIVITY; the arms' members differ, so x and y move by their
    own member's excitation and Minkowski's inequality bounds the vector).
    A magnitude contract's statistic m_test - bound then moves by at most
    (m_test + bound) sum_k c_k Delta_k <= 2 CONTRAST_CEILING sum_k c_k B =
    3.5 B with every Delta_k <= B. Holding that at HERALD_MDE_FRACTION of
    magnitude_mde gives B = 0.25 x 0.01905 / 3.5 = 0.001361 at
    HERALD_DESIGN_SHOTS. The same spread moves a pair's work phase by at
    most sum_k c_k B = 7 B radians, 0.0095 rad there. A common excitation of
    the control or work 1 scales both arms alike and leaves every contract's
    sign; a common excitation of work 4 or 16 enters each pair through its
    own phase, which the herald cannot separate from readout P(1|0).
    """
    return HERALD_MDE_FRACTION * magnitude_mde(shots) / (2 * CONTRAST_CEILING * sum(HERALD_SENSITIVITY))


def herald_counts(run: Path, select: Callable[[str], bool] = is_orbit) -> dict[int, dict[str, Any]] | None:
    """Per herald bit, its physical qubit and each selected member's (excited shots, shots); None unheralded.

    select picks the members by name: the orbit members, whose laws
    HERALD_SENSITIVITY bounds, by default.

    Each herald clbit's physical qubit is the wire of the archived ISA's
    measurement into it; every member must read bit k on the same qubit.
    Bitstrings put clbit 0 rightmost.
    """
    from qpe_diagnostics import HERALD_REGISTER, register_role

    members = [member["name"] for member in _group(run)["members"]]
    found: dict[int, dict[str, Any]] = {}
    heralded = []
    for name, circuit, payload in zip(members, _circuits(run), raw_pubs(run), strict=True):
        if not select(name):
            continue
        registers = [register for register in circuit.cregs if register_role(register.name) == HERALD_REGISTER]
        heralded.append(bool(registers))
        if not registers:
            continue
        (register,) = registers
        writer = {
            circuit.find_bit(i.clbits[0]).index: circuit.find_bit(i.qubits[0]).index
            for i in circuit.data
            if i.operation.name == "measure"
        }
        bits = payload["registers"][register.name]["bitstrings"]
        for k, clbit in enumerate(register):
            qubit = writer[circuit.find_bit(clbit).index]
            entry = found.setdefault(k, {"qubit": qubit, "members": {}})
            if entry["qubit"] != qubit:
                raise RuntimeError(f"{name} reads herald bit {k} on qubit {qubit}, another member on {entry['qubit']}")
            excited = sum(value[register.size - 1 - k] == "1" for value in bits)
            entry["members"][name] = (excited, len(bits))
    if any(heralded) and not all(heralded):
        raise RuntimeError("some members carry the initialization herald and others do not")
    return found if any(heralded) else None


def herald_admission(
    counts: dict[int, dict[str, Any]], contrasts: dict[int, float], bound: float, alpha: float = HERALD_ALPHA
) -> dict[str, Any]:
    """Whether the herald refutes a member spread of the initial excitation at most bound on any herald bit.

    With p10 = prob_meas1_prep0 and p01 = prob_meas0_prep1 of the qubit's
    common assignment channel (herald_report), herald bit k reads
    P(1) = (1 - eps) p10 + eps (1 - p01), so a difference of two members'
    rates is their excitation difference times the readout contrast
    r = 1 - p01 - p10, with the common p10 removed.
    Each ordered member pair (i, j) on each bit gets the Agresti-Caffo
    interval of p_i - p_j (one success and one failure added to each
    member; Agresti and Caffo, The American Statistician 54, 280 (2000)) at
    one-sided level alpha / K, K the bits times the ordered pairs, so all
    limits hold simultaneously at 1 - alpha. The run is herald-admissible
    unless some lower limit exceeds bound x r: a level-alpha test of the
    hypothesis that every spread is at most bound. The simultaneous upper
    limits bound each true spread, and the report states the contract shift
    they leave possible.
    """
    if any(len(entry["members"]) < 2 for entry in counts.values()):
        raise ValueError("a member spread needs at least two members on every herald bit")
    pairs = sum(len(entry["members"]) * (len(entry["members"]) - 1) for entry in counts.values())
    quantile = float(norm.ppf(1 - alpha / max(1, pairs)))
    bits: dict[str, Any] = {}
    refuted = False
    shift = 0.0
    for k, entry in sorted(counts.items()):
        contrast = contrasts[entry["qubit"]]
        rates = {name: excited / shots for name, (excited, shots) in entry["members"].items()}
        adjusted = {
            name: ((excited + 1) / (shots + 2), shots + 2) for name, (excited, shots) in entry["members"].items()
        }
        lower, upper = -math.inf, 0.0
        for first, (p_first, n_first) in adjusted.items():
            for second, (p_second, n_second) in adjusted.items():
                if first == second:
                    continue
                error = math.sqrt(p_first * (1 - p_first) / n_first + p_second * (1 - p_second) / n_second)
                lower = max(lower, p_first - p_second - quantile * error)
                upper = max(upper, p_first - p_second + quantile * error)
        threshold = bound * contrast
        fails = lower > threshold
        refuted |= fails
        shift += HERALD_SENSITIVITY[k] * upper / contrast
        bits[str(k)] = {
            "role": HERALD_ROLES[k],
            "qubit": entry["qubit"],
            "excited_fraction": rates,
            "spread": max(rates.values()) - min(rates.values()),
            "readout_contrast": contrast,
            "threshold": threshold,
            "spread_lower_limit": lower,
            "excitation_spread_upper_limit": upper / contrast,
            "status": "fail" if fails else "pass",
        }
    return {
        "present": True,
        "admissible": not refuted,
        "excitation_spread_bound": bound,
        "alpha": alpha,
        "one_sided_quantile": quantile,
        "comparisons": pairs,
        "bits": bits,
        "contract_shift_upper_limit": 2 * CONTRAST_CEILING * shift,
    }


def herald_report(
    run: Path, calibrations: dict[str, dict[str, Any]], select: Callable[[str], bool] = is_orbit
) -> dict[str, Any]:
    """herald_admission of RUN at herald_bound of its smallest member shot count, or {"present": False}.

    herald_admission removes prob_meas1_prep0 as common to the members, so
    every member reads each herald qubit through one assignment channel
    (prob_meas1_prep0, prob_meas0_prep1) in its calibration
    (execution_calibration). prob_meas1_prep0 counts the calibration's own
    initialization error with its discrimination error (qpu-information.md,
    initialization error), so only a channel shared by every member cancels
    from the member differences. A herald qubit whose members read differing
    or unretained channels leaves the herald not evaluable, which no
    contract reads past; the report names each member's calibration source.
    """
    counts = herald_counts(run, select)
    if not counts:
        return {"present": False}
    shots = min(n for entry in counts.values() for _excited, n in entry["members"].values())
    contrasts = {}
    differing = {}
    for entry in counts.values():
        qubit = entry["qubit"]
        values = {name: calibrations[name]["values"].get(str(qubit), {}) for name in entry["members"]}
        channels = {name: (item.get("prob_meas1_prep0"), item.get("prob_meas0_prep1")) for name, item in values.items()}
        if len(set(channels.values())) > 1 or None in next(iter(channels.values())):
            differing[str(qubit)] = {
                name: {"channel": list(channel), "source": calibrations[name]["source"]}
                for name, channel in channels.items()
            }
            continue
        ((p10, p01),) = set(channels.values())
        contrasts[qubit] = 1 - float(p10) - float(p01)
    if differing:
        return {
            "present": True,
            "evaluable": False,
            "admissible": False,
            "reason": "the members read a herald qubit through differing or unretained assignment channels",
            "differing_channels": differing,
            "shots": shots,
        }
    return herald_admission(counts, contrasts, herald_bound(shots)) | {"evaluable": True, "shots": shots}


def contract_gate(admitted: dict[str, Any], herald: dict[str, Any]) -> dict[str, dict[str, Any]] | None:
    """Every contract not_admissible behind a refused window or herald, else None for contracts to be read."""
    if not admitted["admissible"]:
        return not_admissible(admitted)
    if herald["present"] and not herald["admissible"]:
        return herald_refusal(herald)
    return None


def herald_refusal(herald: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Every contract not_admissible behind a heralded run that the herald does not admit."""
    if not herald["evaluable"]:
        reason = {"herald": "not_evaluable", "differing_channels": herald["differing_channels"]}
    else:
        reason = {
            "herald": "refused",
            "refused_bits": sorted(bit for bit, entry in herald["bits"].items() if entry["status"] == "fail"),
        }
    return {name: {"status": "not_admissible"} | reason for name in CONTRACTS}


def herald_margin(herald: dict[str, Any]) -> float:
    """The magnitude-contract margin of an admitted herald, its contract_shift_upper_limit; zero without a herald."""
    return float(herald["contract_shift_upper_limit"]) if herald["present"] else 0.0


def analyzer_sha256() -> str:
    """sha256 of this analyzer's bytes, which a written case names to bind its analysis."""
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def between_arm_report(run: Path, readout: tuple[float, float] | None) -> dict[str, Any]:
    """Admissibility and every between-arm contract of RUN, as --between-arm writes them.

    Admissibility needs only the archived circuits and returned schedules
    (window_roles); readouts, dt, T2 and the fits are read only for an
    admissible family. The report names the analyzer's sha256, the
    calibration each member reads (execution_calibration) and, for a
    heralded run, the herald admission beside admissibility; a heralded run
    the herald does not admit reads every contract not_admissible
    (herald_refusal).
    """
    roles = window_roles(run)
    admitted = admissibility(roles)
    calibrations = execution_calibration(run)
    report: dict[str, Any] = {
        "schema_version": BETWEEN_ARM_SCHEMA,
        "analyzer_sha256": analyzer_sha256(),
        "calibration": {
            name: {"source": entry["source"], "calibration": entry["calibration"]}
            for name, entry in calibrations.items()
        },
        "herald": herald_report(run, calibrations),
        "spectator_herald": herald_report(run, calibrations, lambda name: name in SPECTATOR_MEMBERS),
        "alpha": {
            "family_alpha": FAMILY_ALPHA,
            "split": "Bonferroni",
            "contracts": len(CONTRACTS),
            "per_contract_alpha": CONTRACT_ALPHA,
        },
        "admissibility": admitted,
    }
    gated = contract_gate(admitted, report["herald"])
    if gated is not None:
        report["contracts"] = gated
        return report
    pairs = measured_pairs(run)
    spectators = spectator_counts(run)
    sources = readout_sources(run, roles, readout)
    readouts = {name: _model_readout(entry) for name, entry in sources.items()}
    dt, source = dt_source(run)
    report |= {
        "member_readout": sources,
        "dt_seconds": dt,
        "dt_source": source,
        "measured_counts": {
            pair: {arm: values.astype(int).tolist() for arm, values in arms.items()} for pair, arms in pairs.items()
        },
        "contracts": contract_results(
            roles,
            pairs,
            readouts,
            dt,
            arm_t2_us(run),
            render_set=True,
            nominal_t2_us=arm_t2_us(run, "nominal"),
            herald_margin=herald_margin(report["herald"]),
            spectators=spectators,
            spectator_herald_margin=spectator_margin(report["spectator_herald"]),
        ),
    }
    # A spectator herald that the admission refuses or cannot evaluate
    # refuses the spectator contract alone; the orbit contracts read the
    # orbit herald.
    if report["spectator_herald"]["present"] and not report["spectator_herald"]["admissible"]:
        report["contracts"]["spectator_window_dephasing"] = herald_refusal(report["spectator_herald"])[
            "spectator_window_dephasing"
        ]
    if spectators is not None:
        report["spectator_counts"] = {
            kind: {quadrature: values.astype(int).tolist() for quadrature, values in reads.items()}
            for kind, reads in spectators.items()
        }
        report["spectator_branch_phase"] = spectator_branch_phase(spectators["measured"])
    return report


RETAINED_WINDOW_RUN = Path(__file__).resolve().parents[1] / "results" / "live" / "2026-10-13T083417.634585Z"
# The herald readouts sit after INIT and shift every later pulse by this
# many dt in the heralded copy of the retained schedule.
HERALD_SHIFT_DT = 400
HERALD_OC_REPLICATES = 400
HERALD_OC_SEED = 20261018
HERALD_OC_BASE_RATE = 0.006


def _check_herald_sensitivity() -> None:
    """|s_k - s| <= c_k m on the exact ideal laws, with equality for the control and work 1.

    Window phases come from Z rotations on the work bits for 1 and 16 after
    the control's reset; an excitation of herald bit k is an X on logical
    qubit k before the program.
    """
    from qiskit import QuantumCircuit

    from qpe_diagnostics import ideal_branch_probabilities, n21_orbit_diagnostic

    def vector(excited: int | None, phases: tuple[float, float]) -> np.ndarray:
        laws = []
        for feed_forward in (True, False):
            source = n21_orbit_diagnostic(feed_forward, "nominal")
            circuit = QuantumCircuit(*source.qregs, *source.cregs)
            if excited is not None:
                circuit.x(excited)
            for instruction in source.data:
                circuit.append(instruction)
                if instruction.operation.name == "reset":
                    circuit.rz(phases[0], 1)
                    circuit.rz(phases[1], 3)
            laws.append(np.asarray(ideal_branch_probabilities(circuit)))
        return np.array([laws[0][1] - laws[0][3], laws[1][3] - laws[1][1]])

    grid = [(a, b) for a in (0.0, 0.4, 0.7, 1.2, -2.5) for b in (0.0, 0.3, -1.1, 2.9)]
    ratios = []
    for phases in grid:
        nominal = vector(None, phases)
        magnitude = float(np.hypot(*nominal))
        moved = [float(np.hypot(*(vector(k, phases) - nominal))) / magnitude for k in range(4)]
        if any(ratio > c + 1e-9 for ratio, c in zip(moved, HERALD_SENSITIVITY, strict=True)):
            raise RuntimeError(f"phases {phases}: an excitation moves the contrast vector by {moved} of m")
        if abs(moved[0] - 2.0) > 1e-9 or abs(moved[1] - 1.0) > 1e-9:
            raise RuntimeError(f"phases {phases}: control and work-1 excitations move {moved[:2]}, not 2 and 1")
        ratios.append(moved)
    if max(max(row[2], row[3]) for row in ratios) < 1.5:
        raise RuntimeError("no window phase moves a work-4 or work-16 excitation near its coefficient")


def _shifted_roles(role: dict[str, Any], shift: int) -> dict[str, Any]:
    return role | {
        "windows": {
            q: {
                "before": w["before"] + shift,
                "after": w["after"] + shift,
                "x": [[start + shift, length] for start, length in w["x"]],
            }
            for q, w in role["windows"].items()
        }
    }


def _heralded_circuit(circuit: Any, order: list[int]) -> Any:
    """circuit after one herald readout per qubit of order, into g0_r0_herald, and a barrier over them."""
    from qiskit import ClassicalRegister, QuantumCircuit

    herald = ClassicalRegister(len(order), "g0_r0_herald")
    heralded = QuantumCircuit(*circuit.qregs, *circuit.cregs, herald, name=circuit.name + "_heralded")
    for k, qubit in enumerate(order):
        heralded.measure(qubit, herald[k])
    heralded.barrier(order)
    heralded.compose(circuit, inplace=True)
    return heralded


def _heralded_payload(payload: dict[str, Any], order: list[int], ones: list[int]) -> dict[str, Any]:
    """payload with herald measure plays after INIT, later rows HERALD_SHIFT_DT later, and herald bitstrings."""
    rows = payload["metadata"]["compilation"]["scheduler_timing"]["timing"].splitlines()
    init_end = max(int(r.split(",")[3]) + int(r.split(",")[4]) for r in rows if r.split(",")[1].startswith("INIT"))
    shifted = []
    for row in rows:
        fields = row.split(",")
        if not fields[1].startswith("INIT"):
            fields[3] = str(int(fields[3]) + HERALD_SHIFT_DT)
        shifted.append(",".join(fields))
    for qubit in order:
        shifted.append(f"main,measure_{qubit},Qubit {qubit},{init_end},180,play")
        shifted.append(f"main,measure_{qubit},AWGR0_{qubit},{init_end + 121},205,capture")
    shots = payload["registers"][REGISTER]["num_shots"]
    bitstrings = ["".join("1" if shot < ones[k] else "0" for k in reversed(range(len(order)))) for shot in range(shots)]
    copied = json.loads(json.dumps(payload))
    copied["metadata"]["compilation"]["scheduler_timing"]["timing"] = "\n".join(shifted)
    copied["registers"]["g0_r0_herald"] = {"bitstrings": bitstrings, "num_bits": len(order), "num_shots": shots}
    return copied


def _heralded_run(target: Path, ones: dict[str, list[int]], execution: set[str], e10_shift: float = 0.0) -> Path:
    """A heralded copy of RETAINED_WINDOW_RUN with planted herald counts and execution-start calibrations.

    Members named in execution carry placed_qubit_calibration in collect.json
    with every T2 scaled by 0.9 and prob_meas1_prep0 raised by e10_shift, so
    their source and values differ from plan time.
    """
    from qiskit import qpy

    source = RETAINED_WINDOW_RUN
    target.mkdir()
    record = json.loads((source / "record.json").read_text())
    group = record["groups"][0]
    circuits = _circuits(source)
    control = circuits[0].find_bit(next(i for i in circuits[0].data if i.operation.name == "measure").qubits[0]).index
    order = [control, *sorted(int(q) for q in group["replicas"][0]["physical_qubits"] if int(q) != control)]
    with (target / "isa.qpy").open("wb") as handle:
        qpy.dump([_heralded_circuit(circuit, order) for circuit in circuits], handle)
    digest = hashlib.sha256((target / "isa.qpy").read_bytes()).hexdigest()
    record["submission"]["qpy_archive_sha256"] = digest
    record["submission"]["jobs"][0]["qpy_archive_sha256"] = digest
    (target / "record.json").write_text(json.dumps(record))
    collect = json.loads((source / "collect.json").read_text())
    (job,) = collect[0]["jobs"]
    raw = target / "raw" / job
    raw.mkdir(parents=True)
    files = {}
    for position, (member, payload) in enumerate(zip(group["members"], raw_pubs(source), strict=True)):
        path = raw / f"pub_{position:02d}.json"
        path.write_text(json.dumps(_heralded_payload(payload, order, ones[member["name"]])))
        files[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (raw / "index.json").write_text(json.dumps({"job_id": job, "files": files}))
    collect[0]["jobs"][job]["raw"]["files"] = files
    for entry in collect[1:]:
        for name, executed in entry.get("executed", {}).items():
            if name in execution:
                executed["placed_qubit_calibration"] = {
                    qubit: values
                    | {"T2": 0.9 * values["T2"], "prob_meas1_prep0": values["prob_meas1_prep0"] + e10_shift}
                    for qubit, values in group["placed_qubit_calibration"].items()
                }
    (target / "collect.json").write_text(json.dumps(collect))
    return target


def _check_herald_twin_roles() -> dict[str, Any]:
    """A heralded member reads its unheralded twin's roles on the retained schedule minus the herald prefix.

    The retained window run's archived ISA and returned schedules form the
    twins; each heralded copy prepends one herald readout per placed qubit
    and a barrier, and its schedule plays the readouts after INIT and every
    later pulse HERALD_SHIFT_DT later. Couplings, unresolved probes and the
    shifted windows must equal the twin's, and with the prefix kept the
    roles must differ. The heralded copy as a run directory then yields the
    twin's admissibility, the herald verdict, the calibration sources and
    the analyzer digest, and the mechanism fit refuses it.
    """
    import tempfile

    group = _group(RETAINED_WINDOW_RUN)
    placed = sorted(int(q) for q in group["replicas"][0]["physical_qubits"])
    circuits = _circuits(RETAINED_WINDOW_RUN)
    payloads = raw_pubs(RETAINED_WINDOW_RUN)
    control = circuits[0].find_bit(next(i for i in circuits[0].data if i.operation.name == "measure").qubits[0]).index
    order = [control, *[q for q in placed if q != control]]
    for member, circuit, payload in zip(group["members"], circuits, payloads, strict=True):
        feed_forward = not member["name"].endswith("_no_feedback")
        twin = member_roles(feed_forward, circuit, payload, placed)
        heralded_circuit = _heralded_circuit(circuit, order)
        heralded_payload = _heralded_payload(payload, order, [0] * len(order))
        heralded = member_roles(feed_forward, heralded_circuit, heralded_payload, placed)
        if normalized_coupling(heralded["coupling"]) != normalized_coupling(twin["coupling"]) or heralded != (
            _shifted_roles(twin, HERALD_SHIFT_DT)
        ):
            raise RuntimeError(f"{member['name']}: the heralded roles {heralded} differ from the twin's {twin}")
        kept = member_roles(feed_forward, heralded_circuit, heralded_payload, placed, strip_herald=False)
        if kept == heralded:
            raise RuntimeError(f"{member['name']}: keeping the herald prefix leaves the roles unchanged")
    retained = between_arm_report(RETAINED_WINDOW_RUN, None)
    if retained["herald"] != {"present": False} or set(
        entry["source"] for entry in retained["calibration"].values()
    ) != {"plan_time"}:
        raise RuntimeError(f"the unheralded retained run reads {retained['herald']} and {retained['calibration']}")
    members = [member["name"] for member in group["members"]]
    shots = int(payloads[0]["registers"][REGISTER]["num_shots"])
    clean = {name: [20, 36, 8, 17] for name in members}
    execution = set(members[::2])
    excess = int(round(0.02 * shots))
    with tempfile.TemporaryDirectory() as scratch:
        run = _heralded_run(Path(scratch) / "clean", clean, execution)
        report = between_arm_report(run, None)
        roles = window_roles(run)
        twins = window_roles(RETAINED_WINDOW_RUN)
        if any(roles[name] != _shifted_roles(twins[name], HERALD_SHIFT_DT) for name in members):
            raise RuntimeError("the heralded run directory reads roles other than the shifted twins'")
        if report["admissibility"] != retained["admissibility"] or not report["herald"]["admissible"]:
            raise RuntimeError(f"the clean heralded run reads {report['admissibility']}, herald {report['herald']}")
        sources = {name: entry["source"] for name, entry in report["calibration"].items()}
        if sources != {name: "execution_start" if name in execution else "plan_time" for name in members}:
            raise RuntimeError(f"the calibration sources read {sources}")
        t2 = arm_t2_us(run)
        plan_t2 = {int(q): float(v["T2"]) for q, v in group["placed_qubit_calibration"].items()}
        for arm in ARMS:
            scale = 0.9 if f"{orbit_pair('extra_readout')}_{arm}" in execution else 1.0
            if any(not math.isclose(t2[arm][q], scale * plan_t2[q], rel_tol=1e-12) for q in plan_t2):
                raise RuntimeError(f"the {arm} arm reads T2 {t2[arm]} against plan {plan_t2} at scale {scale}")
        if report["analyzer_sha256"] != analyzer_sha256() or report["herald"]["shots"] != shots:
            raise RuntimeError("the report names another analyzer digest or herald shot count")
        if [entry["qubit"] for _bit, entry in sorted(report["herald"]["bits"].items())] != order:
            raise RuntimeError("the herald bits read other qubits than the readouts wrote")
        try:
            build_report(run, None)
        except RuntimeError as error:
            if "unheralded" not in str(error):
                raise
        else:
            raise RuntimeError("the mechanism fit accepted a heralded run")
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr), contextlib.suppress(SystemExit):
            main(["--between-arm", str(run), "--expected-analyzer-sha256", "0" * 64])
        if "differs from the expected" not in stderr.getvalue():
            raise RuntimeError("--expected-analyzer-sha256 accepted another analyzer digest")
        with contextlib.redirect_stdout(io.StringIO()):
            if main(["--between-arm", str(run), "--expected-analyzer-sha256", analyzer_sha256().upper()]) != 0:
                raise RuntimeError("--expected-analyzer-sha256 refused this analyzer's own digest")
        planted = {name: list(values) for name, values in clean.items()}
        planted[members[3]][0] += excess
        planted_run = _heralded_run(Path(scratch) / "planted", planted, set())
        refused = between_arm_report(planted_run, None)
        bits = refused["herald"]["bits"]
        if refused["herald"]["admissible"] or [bits[str(k)]["status"] for k in range(4)] != [
            "fail",
            "pass",
            "pass",
            "pass",
        ]:
            raise RuntimeError(f"a planted control excess of {excess} shots reads {refused['herald']}")
        # The retained window run is not window-admissible, so its reports
        # stop at that gate; contract_gate on an admissible window reads the
        # herald gate behind it.
        window = {"admissible": True}
        gated = contract_gate(window, refused["herald"])
        if (
            contract_gate(window, report["herald"]) is not None
            or gated is None
            or set(gated) != set(CONTRACTS)
            or any(
                entry != {"status": "not_admissible", "herald": "refused", "refused_bits": ["0"]}
                for entry in gated.values()
            )
        ):
            raise RuntimeError(f"a refused herald gates the contracts as {gated}")
        # One member under its own assignment channel leaves the herald not
        # evaluable, and the contracts not admissible behind it.
        channel = _heralded_run(Path(scratch) / "channel", clean, {members[1]}, e10_shift=0.001)
        shifted = herald_report(channel, execution_calibration(channel))
        gated = contract_gate(window, shifted)
        if (
            shifted["evaluable"]
            or set(shifted["differing_channels"]) != {str(q) for q in order}
            or gated is None
            or set(gated) != set(CONTRACTS)
            or any(
                entry["status"] != "not_admissible" or entry["herald"] != "not_evaluable" for entry in gated.values()
            )
        ):
            raise RuntimeError(f"a member-specific channel reads {shifted}, gating {gated}")
        # An extra_readout member at another T2 than its arm's nominal member
        # leaves the readout contract not evaluable in that arm alone.
        lone = _heralded_run(Path(scratch) / "t2", clean, {f"{orbit_pair('extra_readout')}_feedback"})
        readout_case = readout_contract(
            {}, window_roles(lone), dt_source(lone)[0], arm_t2_us(lone), CONTRACT_ALPHA, arm_t2_us(lone, "nominal")
        )
        if readout_case["status"] != "not_evaluable" or set(readout_case["differing_t2_qubits"]) != {"feedback"}:
            raise RuntimeError(f"an extra_readout member at its own T2 reads {readout_case}")
        # between_arm_report itself, behind an admissible window: a refused
        # herald stops it at contract_gate, and an admitted one hands
        # contract_results both members' T2.
        module = sys.modules[__name__]
        passed = {"admissible": True, "orientation": {}, "differing": {}, "unresolved": {}, "missing": []}
        seen: dict[str, Any] = {}

        def spy(*args: Any, **kwargs: Any) -> dict[str, dict[str, Any]]:
            seen.update(kwargs, t2_us=args[4])
            return {}

        with mock.patch.object(module, "admissibility", lambda _roles: passed):
            behind = between_arm_report(planted_run, None)["contracts"]
            with mock.patch.object(module, "contract_results", spy):
                between_arm_report(lone, None)
        if behind != herald_refusal(refused["herald"]):
            raise RuntimeError(f"between_arm_report reads {behind} behind a refused herald")
        if seen.get("t2_us") != arm_t2_us(lone) or seen.get("nominal_t2_us") != arm_t2_us(lone, "nominal"):
            raise RuntimeError(f"between_arm_report hands contract_results T2 {seen}")
    return {"shots": shots, "planted_excess": excess / shots}


def _check_herald_operating_characteristic() -> dict[str, float]:
    """Refusal rates of herald_admission at spreads 0, B, 2B and a planted large spread, seeded.

    Eight members on four bits at HERALD_DESIGN_SHOTS share the base rate
    HERALD_OC_BASE_RATE; one member carries the spread on the control bit.
    The test holds its level at spreads up to B and detects the large one.
    """
    bound = herald_bound(HERALD_DESIGN_SHOTS)
    rng = np.random.default_rng(HERALD_OC_SEED)
    names = [f"m{index}" for index in range(8)]
    rates: dict[str, float] = {}
    for label, spread in (("0", 0.0), ("B", bound), ("2B", 2 * bound), ("0.006", 0.006)):
        refusals = 0
        for _replicate in range(HERALD_OC_REPLICATES):
            counts = {}
            for k in range(4):
                probabilities = [HERALD_OC_BASE_RATE + (spread if k == 0 and index == 0 else 0.0) for index in range(8)]
                draws = rng.binomial(HERALD_DESIGN_SHOTS, probabilities)
                counts[k] = {
                    "qubit": k,
                    "members": {name: (int(d), HERALD_DESIGN_SHOTS) for name, d in zip(names, draws, strict=True)},
                }
            refusals += not herald_admission(counts, dict.fromkeys(range(4), 1.0), bound)["admissible"]
        rates[label] = refusals / HERALD_OC_REPLICATES
    if rates["0"] > HERALD_ALPHA or rates["B"] > HERALD_ALPHA or rates["0.006"] < 0.95:
        raise RuntimeError(f"the herald admission refuses at rates {rates}")
    return rates


def _check_herald_margin() -> float:
    """A magnitude contract that passes at margin zero fails once the herald margin exceeds its upper limit."""
    arms = {
        "feedback": np.array([1200.0, 2600.0, 1400.0, 1000.0]),
        "no_feedback": np.array([1000.0, 1400.0, 2600.0, 1200.0]),
    }
    plain = contrast_floor(arms, arms, (1.0, 1.0), CONTRACT_ALPHA)
    if plain["status"] != "pass" or "herald_margin" in plain:
        raise RuntimeError(f"an equal pair failed its own floor or carried a margin: {plain}")
    margin = plain["upper_confidence_limit"] * 1.01
    held = contrast_floor(arms, arms, (1.0, 1.0), CONTRACT_ALPHA, margin)
    if held["status"] != "fail" or held["herald_margin"] != margin:
        raise RuntimeError(f"a herald margin above the upper limit left the contract passing: {held}")
    if (
        herald_margin({"present": False}) != 0.0
        or herald_margin({"present": True, "contract_shift_upper_limit": margin}) != margin
    ):
        raise RuntimeError("herald_margin does not read the admitted herald's contract shift")
    return margin


def self_test_herald() -> None:
    """The herald's sensitivity coefficients, twin roles, run-directory report, margin and operating characteristic."""
    _check_herald_sensitivity()
    margin = _check_herald_margin()
    twin = _check_herald_twin_roles()
    rates = _check_herald_operating_characteristic()
    bound = herald_bound(HERALD_DESIGN_SHOTS)
    print(
        f"N=21 orbit herald: sensitivity (2, 1, 2, 2) holds on the exact laws; heralded members read their "
        f"twins' roles on the retained schedule minus the prefix and differ with it kept; the heralded run "
        f"reads the twin's admissibility, execution-start calibration sources and the analyzer digest, refuses "
        f"a {twin['planted_excess']:.3f} control excess at {twin['shots']} shots, and the mechanism fit refuses "
        f"it; at {HERALD_DESIGN_SHOTS} shots MDE {magnitude_mde(HERALD_DESIGN_SHOTS):.5f}, B {bound:.6f}, "
        f"refusal rates {rates}; a {margin:.5f} herald margin turns a passing magnitude contract into a failure"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path, nargs="?")
    parser.add_argument("--out", type=Path)
    parser.add_argument(
        "--readout",
        nargs=2,
        type=float,
        metavar=("P1G0", "P0G1"),
        help="control-qubit P(1|0) and P(0|1); default reads IBM properties at the record's calibration",
    )
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--check", action="store_true", help=f"regenerate RUN_DIR/{RETAINED} and require it to agree")
    parser.add_argument(
        "--between-arm",
        type=Path,
        metavar="RUN_DIR",
        help="evaluate the preregistered between-arm contracts of an n21-orbit-rca run; --out writes the report",
    )
    parser.add_argument(
        "--expected-analyzer-sha256",
        metavar="HEX",
        help="with --between-arm, refuse unless this analyzer's sha256 equals the digest a written case names",
    )
    parser.add_argument(
        "--self-test-herald",
        action="store_true",
        help="check the herald's sensitivity coefficients, its retained-schedule twin roles and its admission test",
    )
    arguments = parser.parse_args(argv)
    if arguments.self_test_herald:
        self_test_herald()
        return 0
    if arguments.expected_analyzer_sha256 is not None:
        if arguments.between_arm is None:
            parser.error("--expected-analyzer-sha256 applies with --between-arm")
        if arguments.expected_analyzer_sha256.lower() != analyzer_sha256():
            parser.error(
                f"this analyzer's sha256 {analyzer_sha256()} differs from the expected "
                f"{arguments.expected_analyzer_sha256}"
            )
    if arguments.self_check:
        self_check()
        return 0
    if arguments.between_arm is not None:
        if arguments.run is not None or arguments.check:
            parser.error("--between-arm names its own run directory and takes no RUN_DIR or --check")
        report = between_arm_report(arguments.between_arm, tuple(arguments.readout) if arguments.readout else None)
        print(f"analyzer sha256: {report['analyzer_sha256']}")
        print(f"admissibility: {'admissible' if report['admissibility']['admissible'] else 'not admissible'}")
        herald = report["herald"]
        if not herald["present"]:
            print("herald: absent")
        elif not herald["evaluable"]:
            print(f"herald: not evaluable ({herald['reason']})")
        else:
            print(f"herald: {'admissible' if herald['admissible'] else 'refused'}")
        for name, contract in report["contracts"].items():
            print(f"{name}: {contract['status']}")
        if arguments.out:
            arguments.out.write_text(serialize(report))
        return 0
    if arguments.run is None:
        parser.error("a run directory is required")
    if arguments.check:
        check(arguments.run)
        return 0
    report = build_report(arguments.run, tuple(arguments.readout) if arguments.readout else None)
    if arguments.out:
        arguments.out.write_text(serialize(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
