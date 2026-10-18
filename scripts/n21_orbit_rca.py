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
one resolved coupling (admissibility).
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import minimize
from scipy.stats import chi2, norm

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gororoba_quantum"))

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


def distribution(params: dict[str, float], feed_forward: bool) -> np.ndarray:
    """Labeled law over y = b0 + 2 b1 under the parameterized error model."""
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
    since only the feed-forward member contains an if_else.
    """
    members = [member["name"] for member in _group(run)["members"]]
    circuits = _circuits(run)
    if len(circuits) != len(members):
        raise RuntimeError("archived circuits and record members differ in number")
    pairs: dict[str, dict[str, np.ndarray]] = {}
    for index, (name, circuit, payload) in enumerate(zip(members, circuits, raw_pubs(run), strict=True)):
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
    """Exact compiled branch law with rz(angle) after the positions[q]-th physical pulse on each probed wire."""
    from qiskit import QuantumCircuit

    from qpe_diagnostics import ideal_compiled_probabilities

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
    return np.array(ideal_compiled_probabilities(probed))


def _branch_law(feed_forward: bool, phases: dict[int, float]) -> np.ndarray:
    return np.array(
        distribution(_readout(0.0, 0.0) | {f"phase_b{b}": phase for b, phase in phases.items()}, feed_forward)
    )


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
    """
    from qpe_diagnostics import ideal_compiled_probabilities

    probe = 0.7
    branch_sets = ((0,), (1,), (0, 1))
    group = _group(run)
    placed = sorted(int(qubit) for qubit in group["replicas"][0]["physical_qubits"])
    roles: dict[str, dict[str, Any]] = {}
    for member, circuit, payload in zip(group["members"], _circuits(run), raw_pubs(run), strict=True):
        feed_forward = not member["name"].endswith("_no_feedback")
        writers = [circuit.find_bit(i.qubits[0]).index for i in circuit.data if i.operation.name == "measure"]
        writer = writers[0]
        try:
            plays = _plays(payload)
        except ValueError as error:
            # Counts and writers need no schedule; only window exposure does.
            roles[member["name"]] = {
                "control": writer,
                "terminal": writers[-1],
                "coupling": {},
                "windows": {},
                "unresolved": [str(error)],
            }
            continue
        opening = min(start for start, _length, name, wire in plays if wire == writer and name == "measure")
        base = np.array(ideal_compiled_probabilities(circuit))
        windows: dict[int, dict[str, Any]] = {}
        positions: dict[int, int] = {}
        coupling: dict[int, dict[int, int]] = {}
        unresolved: list[str] = []
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
                    [start, length]
                    for start, length, name in pulses
                    if max(before) <= start < min(after) and name == "x"
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
                            probe * branches[b]
                            for q, branches in trial.items()
                            if q in (anchor, qubit) and b in branches
                        )
                        for b in (0, 1)
                    }
                    if np.allclose(joint, _branch_law(feed_forward, phases), atol=1e-9):
                        coupling[qubit] = trial[qubit]
                        break
                else:
                    unresolved.append(f"a joint probe with qubit {anchor} fits neither relative sign of qubit {qubit}")
        roles[member["name"]] = {
            "control": writer,
            "terminal": writers[-1],
            "coupling": coupling,
            "windows": windows,
            "unresolved": unresolved,
        }
    return roles


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

    return float(QiskitRuntimeService().backend(backend).target.dt), f"live {backend} Target dt"


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


def _assignment(group: dict[str, Any], qubit: int, properties: Any) -> tuple[float, float]:
    retained = group.get("placed_qubit_calibration", {}).get(str(qubit))
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
    """Assignment rates of each member's first and last measurement writers at the record's calibration.

    A record that retains placed_qubit_calibration supplies P(1|0) and P(0|1)
    directly; an older record falls back to IBM properties at its
    calibration timestamp.
    """
    group = _group(run)
    properties = None
    writers = {qubit for role in roles.values() for qubit in (role["control"], role["terminal"])}
    if not all(str(qubit) in group.get("placed_qubit_calibration", {}) for qubit in writers):
        from datetime import datetime, timedelta

        from qiskit_ibm_runtime import QiskitRuntimeService

        stamp = datetime.fromisoformat(group["calibration"])
        backend = QiskitRuntimeService().backend(group["backend"])
        # A historical query returns the newest snapshot strictly before its
        # datetime, so the query asks one second past the recorded stamp; the
        # current snapshot serves when no later calibration has landed.
        candidates = (backend.properties(datetime=stamp + timedelta(seconds=1)), backend.properties())
        properties = next((item for item in candidates if item is not None and item.last_update_date == stamp), None)
        if properties is None:
            raise RuntimeError(f"{group['backend']} properties at {stamp} are unavailable; pass --readout")
    readouts = {}
    for name, role in roles.items():
        mid = _assignment(group, role["control"], properties)
        end = _assignment(group, role["terminal"], properties)
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


CONTRACT_IDLE_DT = {"nominal": 1000, "window_delay": 1415, "extra_readout": 1400, "window_echo": 1000}
CONTRACT_SLOPE = 6e-4
CONTRACT_SHOTS = 8192


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

    def pair(params: dict[str, float]) -> dict[str, np.ndarray]:
        return {arm: np.round(distribution(base | params, arm == "feedback") * CONTRACT_SHOTS) for arm in ARMS}

    # The coupling of -1 makes the coupling-weighted exposure negative, so
    # the slope the contract recovers is -CONTRACT_SLOPE per dt.
    nominal = pair({"phase_one": CONTRACT_SLOPE * CONTRACT_IDLE_DT["nominal"]})
    pairs = {
        orbit_pair("nominal"): nominal,
        orbit_pair("window_delay"): pair({"phase_one": CONTRACT_SLOPE * CONTRACT_IDLE_DT["window_delay"]}),
        orbit_pair("extra_readout"): nominal,
        orbit_pair("window_echo"): nominal,
    }
    roles = _contract_roles({7: {0: -1, 1: -1}})
    readouts = dict.fromkeys(roles, readout)
    t2_us = {7: 100.0}
    dt = SYNTHETIC_DT_US * 1e-6
    fits = phase_fits(pairs, readouts)

    def statuses(
        case: dict[str, dict[str, Any]], measured: dict[str, dict[str, np.ndarray]], t2: dict[int, float]
    ) -> dict[str, str]:
        results = contract_results(case, measured, readouts, dt, t2, fits)
        json.dumps(results, sort_keys=True)
        return {name: result["status"] for name, result in results.items()}

    passing = dict.fromkeys(CONTRACTS, "pass")
    found = statuses(roles, pairs, t2_us)
    if found != passing:
        raise RuntimeError(f"a family planted on every contract returns {found}")
    # A longer delay window moves the prediction off the planted phase, and
    # window dephasing lowers a pair's contrast magnitude.
    off_slope = copy.deepcopy(roles)
    for arm in ARMS:
        off_slope[f"{orbit_pair('window_delay')}_{arm}"]["windows"][7]["after"] += 600
    dephased = pair({"phase_one": CONTRACT_SLOPE * CONTRACT_IDLE_DT["nominal"], "window_t2": 0.5})
    for label, case, measured, expected in (
        ("off-slope window_delay", off_slope, pairs, "window_delay_phase_slope"),
        ("dephased extra_readout", roles, pairs | {orbit_pair("extra_readout"): dephased}, "extra_readout_contrast"),
        ("dephased window_echo", roles, pairs | {orbit_pair("window_echo"): dephased}, "window_echo_restoration"),
    ):
        found = statuses(case, measured, t2_us)
        if found != passing | {expected: "fail"}:
            raise RuntimeError(f"a {label} returns {found}; only {expected} must fail")
    # An echo that cancels the nominal phase at equal coherence lowers the
    # signed contrast difference beyond its one-sided limit; the magnitude
    # contract passes it.
    canceled = pair({})
    restored = contract_results(roles, pairs | {orbit_pair("window_echo"): canceled}, readouts, dt, t2_us, fits)
    (echo_signed, echo_variance), (nominal_signed, nominal_variance) = map(contrast_difference, (canceled, nominal))
    signed_upper = (
        echo_signed - nominal_signed + float(norm.ppf(1 - CONTRACT_ALPHA)) * math.sqrt(echo_variance + nominal_variance)
    )
    if restored["window_echo_restoration"]["status"] != "pass" or signed_upper >= 0:
        raise RuntimeError(
            f"a phase-canceling echo returns {restored['window_echo_restoration']}; "
            f"the signed contrast form's upper limit is {signed_upper:.4f}"
        )
    if statuses(roles, pairs, {})["extra_readout_contrast"] != "not_evaluable":
        raise RuntimeError("the readout contract evaluates without a retained T2")
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
        results = contract_results(case, pairs, readouts, dt, t2_us, fits)
        if admitted["admissible"] or set(admitted["differing"]) != members:
            raise RuntimeError(f"admissibility names {sorted(admitted['differing'])}, not {sorted(members)}")
        if any(
            result["status"] != "not_admissible" or result["differing"] != admitted["differing"]
            for result in results.values()
        ):
            raise RuntimeError(f"a family with differing couplings evaluates a contract: {results}")
    if admissibility(differing)["unresolved"] != {name: differing[name]["unresolved"]}:
        raise RuntimeError("admissibility omits a member's unresolved probe")
    single = {key: value for key, value in roles.items() if key.startswith(orbit_pair("nominal"))}
    absent = [f"{orbit_pair(variant)}_{arm}" for variant in ORBIT_VARIANTS[1:] for arm in ARMS]
    if admissibility(single)["missing"] != absent:
        raise RuntimeError("admissibility of the nominal pair alone names no missing member")


def self_check() -> None:
    """Recover a known work phase from exact expected counts and reject the depolarizing baseline."""
    _check_exact_laws()
    _check_manifest_binding()
    _check_static_basins()
    _check_piecewise_exposure()
    _check_seed_ranking()
    _check_differences()
    _check_between_arm()
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
        "branch-window, and baseline rejection checks pass"
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
    """Every pair's mechanism fits and phase interval, and the joint fit, as rca-mechanism-fit.json holds them."""
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


BETWEEN_ARM_SCHEMA = "n21-orbit-between-arm-contracts-v1"
ORBIT_VARIANTS = ("nominal", "window_delay", "extra_readout", "window_echo")
ARMS = ("feedback", "no_feedback")
REFERENCE_MEMBER = "n21_orbit_nominal_feedback"
CONTRACTS = ("window_delay_phase_slope", "extra_readout_contrast", "window_echo_restoration")
# Bonferroni over the three contracts holds their family-wise error at FAMILY_ALPHA.
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
    work bit for 1, so every member of the four pairs must be present, free
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


def pair_idle(roles: dict[str, dict[str, Any]], variant: str, qubit: int) -> float:
    """Mean idle time in dt of one window qubit over a pair's members, driven echo pulses excluded."""
    idles = []
    for arm in ARMS:
        window = roles[f"{orbit_pair(variant)}_{arm}"]["windows"][qubit]
        idles.append(window["after"] - window["before"] - sum(length for _start, length in window["x"]))
    return sum(idles) / len(idles)


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
    test: dict[str, np.ndarray], reference: dict[str, np.ndarray], factor: float, alpha: float
) -> dict[str, Any]:
    """One-sided test that a pair's contrast magnitude reaches factor times the reference pair's.

    m_test - factor m_reference (contrast_magnitude) is normal to first order
    in the multinomial counts of four independent PUBs, with variance
    var_test + factor^2 var_reference. The contract fails only when its upper
    (1 - alpha) confidence limit lies below zero, so at the bound sampling
    noise fails it with probability alpha. The signed contrast difference
    of each pair is reported and decides nothing, since a work phase moves it.
    """
    tested, tested_variance = contrast_magnitude(test)
    reference_value, reference_variance = contrast_magnitude(reference)
    statistic = tested - factor * reference_value
    error = math.sqrt(tested_variance + factor**2 * reference_variance)
    quantile = float(norm.ppf(1 - alpha))
    upper = statistic + quantile * error
    return {
        "status": "pass" if upper >= 0 else "fail",
        "contrast_magnitude": tested,
        "reference_contrast_magnitude": reference_value,
        "signed_contrast_difference": contrast_difference(test)[0],
        "reference_signed_contrast_difference": contrast_difference(reference)[0],
        "reference_factor": factor,
        "statistic": statistic,
        "standard_error": error,
        "one_sided_quantile": quantile,
        "upper_confidence_limit": upper,
    }


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


def phase_slope_contract(
    pairs: dict[str, dict[str, np.ndarray]],
    readouts: dict[str, dict[str, float]],
    roles: dict[str, dict[str, Any]],
    orientation: dict[str, int],
    fits: dict[str, dict[str, Any]],
    alpha: float,
    render_set: bool,
) -> dict[str, Any]:
    """window_delay's work phase lies on the nominal pair's static phase slope.

    A static detuning shared by the coupled qubits adds work phase in
    proportion to coupling-weighted exposure (pair_phase_exposure), so the
    nominal pair's fitted phase, taken on its principal branch, over its
    exposure gives the slope per dt, and the slope times window_delay's
    exposure predicts that pair's phase modulo 2 pi. The contract passes when
    the prediction lies in window_delay's profile-likelihood confidence set
    at 1 - alpha: its profiled deviance (PhaseProfile) exceeds the
    work-phase minimum by at most the one-parameter chi-square quantile.
    The nominal phase enters as a point estimate. render_set adds the set
    itself on phase_interval's grid.
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
    nominal_phase = fits["nominal"]["parameters"]["phase_one"]
    slope = nominal_phase / nominal_exposure
    predicted = math.remainder(slope * delay_exposure, 2 * math.pi)
    delay = orbit_pair("window_delay")
    arms = {arm: readouts[f"{delay}_{arm}"] for arm in ARMS}
    best = fits["window_delay"]
    threshold = float(chi2.ppf(1 - alpha, 1))
    statistic = PhaseProfile(pairs[delay], arms, best)(predicted) - best["deviance"]
    result: dict[str, Any] = {
        "status": "pass" if statistic <= threshold else "fail",
        "nominal_phase": nominal_phase,
        "nominal_exposure_dt": nominal_exposure,
        "slope_rad_per_dt": slope,
        "window_delay_exposure_dt": delay_exposure,
        "predicted_phase": predicted,
        "window_delay_phase": best["parameters"]["phase_one"],
        "profile_deviance_at_prediction": statistic,
        "chi2_threshold": threshold,
        "level": 1 - alpha,
    }
    if render_set:
        result["confidence_set_grid_segments"] = phase_interval(pairs[delay], arms, best, threshold)
    return result


def readout_contract(
    pairs: dict[str, dict[str, np.ndarray]],
    roles: dict[str, dict[str, Any]],
    dt: float,
    t2_us: dict[int, float],
    alpha: float,
) -> dict[str, Any]:
    """extra_readout's contrast magnitude stays above the nominal one dephased over the added idle time.

    Each coupled qubit q idles t_q longer in the extra_readout window than in
    the nominal one (pair_idle, floored at zero since dephasing only lowers
    coherence), so its coherence decays by exp(-t_q / T2_q); the bound is the
    nominal contrast magnitude times exp(-sum_q t_q / T2_q) over the coupled
    qubits, with T2 from the record's retained calibration. A coupling that
    holds only one of the work bits for 1 and 16 keeps one term, which
    raises the bound. contrast_floor decides at alpha.
    """
    qubits = sorted(normalized_coupling(roles[REFERENCE_MEMBER]["coupling"]))
    absent = [qubit for qubit in qubits if not t2_us.get(qubit)]
    if absent:
        return {"status": "not_evaluable", "reason": f"the record retains no T2 for coupled qubits {absent}"}
    added = {
        qubit: max(0.0, pair_idle(roles, "extra_readout", qubit) - pair_idle(roles, "nominal", qubit))
        for qubit in qubits
    }
    # Backend properties report T2 in microseconds (live_run.placed_qubit_calibration).
    exponent = sum(added[qubit] * dt / (t2_us[qubit] * 1e-6) for qubit in qubits)
    result = contrast_floor(
        pairs[orbit_pair("extra_readout")], pairs[orbit_pair("nominal")], math.exp(-exponent), alpha
    )
    return result | {
        "added_idle_dt": {str(qubit): added[qubit] for qubit in qubits},
        "t2_us": {str(qubit): t2_us[qubit] for qubit in qubits},
        "dt_seconds": dt,
    }


def contract_results(
    roles: dict[str, dict[str, Any]],
    pairs: dict[str, dict[str, np.ndarray]],
    readouts: dict[str, dict[str, float]],
    dt: float,
    t2_us: dict[int, float],
    fits: dict[str, dict[str, Any]] | None = None,
    render_set: bool = False,
) -> dict[str, dict[str, Any]]:
    """Every between-arm contract's status and deciding numbers, each at CONTRACT_ALPHA.

    The contracts are preregistered, their statistics, levels and decision
    rules independent of any run's counts:
    window_delay_phase_slope (phase_slope_contract), extra_readout_contrast
    (readout_contract), and window_echo_restoration, which passes when the
    upper confidence limit of the window_echo contrast magnitude minus the
    nominal one reaches zero (contrast_floor at factor 1). A family that
    fails admissibility reports every contract not_admissible.
    """
    admitted = admissibility(roles)
    if not admitted["admissible"]:
        return not_admissible(admitted)
    fits = phase_fits(pairs, readouts) if fits is None else fits
    return {
        "window_delay_phase_slope": phase_slope_contract(
            pairs, readouts, roles, admitted["orientation"], fits, CONTRACT_ALPHA, render_set
        ),
        "extra_readout_contrast": readout_contract(pairs, roles, dt, t2_us, CONTRACT_ALPHA),
        "window_echo_restoration": contrast_floor(
            pairs[orbit_pair("window_echo")], pairs[orbit_pair("nominal")], 1.0, CONTRACT_ALPHA
        ),
    }


def retained_t2_us(run: Path) -> dict[int, float]:
    """T2 in microseconds of each placed qubit the record's calibration retains."""
    retained = _group(run).get("placed_qubit_calibration", {})
    return {int(qubit): float(values["T2"]) for qubit, values in retained.items() if "T2" in values}


def between_arm_report(run: Path, readout: tuple[float, float] | None) -> dict[str, Any]:
    """Admissibility and every between-arm contract of RUN, as --between-arm writes them.

    Admissibility needs only the archived circuits and returned schedules
    (window_roles); readouts, dt, T2 and the fits are read only for an
    admissible family.
    """
    roles = window_roles(run)
    admitted = admissibility(roles)
    report: dict[str, Any] = {
        "schema_version": BETWEEN_ARM_SCHEMA,
        "alpha": {
            "family_alpha": FAMILY_ALPHA,
            "split": "Bonferroni",
            "contracts": len(CONTRACTS),
            "per_contract_alpha": CONTRACT_ALPHA,
        },
        "admissibility": admitted,
    }
    if not admitted["admissible"]:
        report["contracts"] = not_admissible(admitted)
        return report
    pairs = measured_pairs(run)
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
        "contracts": contract_results(roles, pairs, readouts, dt, retained_t2_us(run), render_set=True),
    }
    return report


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
    arguments = parser.parse_args(argv)
    if arguments.self_check:
        self_check()
        return 0
    if arguments.between_arm is not None:
        if arguments.run is not None or arguments.check:
            parser.error("--between-arm names its own run directory and takes no RUN_DIR or --check")
        report = between_arm_report(arguments.between_arm, tuple(arguments.readout) if arguments.readout else None)
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
