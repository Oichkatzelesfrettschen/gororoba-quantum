"""Ideal law of the encoded N=21 feedback pair through cQASM export and the QX emulator's semantics.

The two dynamic circuits of results/live/2026-10-17T003834.987727Z/isa.qpy
(n21_encoded_feedback, n21_encoded_no_feedback on ibm_kingston) run on seven
active qubits; snapshot_laws.restrict_circuit keeps them in ascending physical
order, and restricted qubit k sits on QX register qubit k. Both arms measure
q[5] into clbit 0 mid-circuit, reset q[5] and reuse it; the feedback arm then
applies Rz(-pi/2) to q[1] when clbit 0 reads 1. cQASM 3.0 has no
binary-controlled gate, so QX runs the feedback arm only in a
deferred-measurement form, and both arms get one:

- the mid-circuit measure of q[5] becomes CNOT q[5] -> q[7], a fresh ancilla
  (QX_ANCILLA) that no later gate touches, so the copy dephases q[5] exactly
  as the measurement does;
- the reset that immediately follows it becomes CNOT q[7] -> q[5]: q[5] and
  q[7] agree in the Z basis after the copy, so the second CNOT returns q[5]
  to |0> with the outcome kept on q[7] (a reset after a projective measure is
  an X conditioned on the outcome);
- the if_else on clbit 0 becomes the controlled body from q[7] (Rz(theta)
  controlled is Rz(theta/2), CNOT, Rz(-theta/2), CNOT on the target);
- every measurement moves to the end, each into its own classical bit
  (b[0] = measure q[7], b[1] = measure q[1]).

Every deferred program is unitary until its final measurements, so
qxelarator's `state` of the same program without them is deterministic and
gives the exact QX law. The no-feedback arm also runs natively: mid-circuit
`b[0] = measure q[5]`, `reset q[5]`, and a final `b[1] = measure q[1]`.
qxelarator 0.10.0's `reset` is not the cQASM reset: when the qubit carries
weight on |1>, every amplitude pair (a0x, a1x) becomes the nonnegative real
sqrt(|a0x|^2 + |a1x|^2), which drops the phase of the whole register. The
native arm's law follows that map (``branches``, reset model "qxelarator"),
which the retained phase probes and single-shot branch states pin.

Gates lower by explicit substitution (SX = H S H exactly, X, CZ, CNOT, Rz
unchanged) to the qx gate map of box_kite_cases.DIALECTS. QX results are the
measurement register, one character per qubit with qubit 0 rightmost, each
the qubit's last measured outcome; a reset leaves it unchanged
(docs/notes/quantum_inspire/qx-runs.md). Recorded value r = c0 + 2 c1, clbit 0
least significant, reads c0 from q[7] (deferred) or q[5] (native) and c1 from
q[1].

- ``--out FILE`` builds the forms, proves each stage's ideal law against the
  reference (dynamic_density with an empty noise model), writes the cQASM
  programs beside FILE, runs them and the reset probes on qxelarator through
  ``$QI_PYTHON`` (QX_SHOTS per seed, the exact state of each deferred program,
  single-shot native branch states), then writes the record and exits nonzero
  unless require_verdicts holds.
- ``--check FILE`` runs without qxelarator: it recomputes the reference,
  deferred, lowered and parsed laws, regenerates the programs and requires
  their bytes and sha256s, re-parses the retained programs with
  box_kite_cases.parse_cqasm, holds both reset models to the retained probe
  and branch states, and requires the verdicts: each deferred QX state's
  marginal equals the reference, the pooled deferred counts pass
  n21_exact_model_validation.compare (simultaneous Hoeffding radius at total
  tail TAIL, Bernstein radii on each arm score and the contrast), and the
  native counts fail the reference and pass the qxelarator reset model.
- ``--self-test`` requires corrupted cQASM lines, dropped-control deferrals, a
  flipped bit order, swapped clbits, moved shots and native counts drawn from
  the reference law to fail, the reset models to reproduce the
  dynamic_density law and the phase drop, and the stopgap writer to equal
  box_kite_cases.emit on an on-grid circuit byte for byte.

Usage:
    "$PYTHON" scripts/n21_qx_conformance.py --out docs/evidence/n21_qx_conformance/result.json
    "$PYTHON" scripts/n21_qx_conformance.py --check docs/evidence/n21_qx_conformance/result.json
    "$PYTHON" scripts/n21_qx_conformance.py --self-test
"""

# Module-level imports stay in the standard library: --out runs the --qx-worker
# mode of this file under $QI_PYTHON (Python 3.13 without qiskit-aer), and
# parallel.py's spawn pool re-imports this module in every worker there.
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import re
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import parallel  # noqa: E402

SCHEMA = "n21-qx-conformance-v1"
ISA = ROOT / "results/live/2026-10-17T003834.987727Z/isa.qpy"
RECORD = ISA.parent / "record.json"
QX_WIDTH = 10
QX_ANCILLA = 7
QX_SHOTS = 2048
BASE_SEED = 20261017
SEEDS = 12
TAIL = 1e-3
# Stages between the reference and the QX programs are exact up to float
# rounding; EXACT_TOL bounds every probability gap and 1 - fidelity.
EXACT_TOL = 1e-9
QXELARATOR = "0.10.0"
QI_PYTHON_DEFAULT = Path.home() / ".local/share/quantuminspire/venv/bin/python"
LOWERED = ("h", "s", "sdg", "x", "z", "cx", "cz", "rz")
MEASURE_LINE = re.compile(r"b\[(\d+)\] = measure q\[(\d+)\]")
RESET_LINE = re.compile(r"reset q\[(\d+)\]")
# QX result register probe: a reset after a measurement keeps the measured
# character, so q[0] reads 1 in every shot.
RESET_REGISTER_PROBE = "\n".join(
    ["version 3.0", "", "qubit[2] q", "bit[2] b", "", "X q[0]", "b[0] = measure q[0]", "reset q[0]", ""]
)
# QX reset phase probes, each a final state: q[0] in |1> beside q[1] in |->; q[0]
# already |0> beside q[1] in (|0> + i|1>)/sqrt2; a three-qubit entangled state
# with weight on both values of q[0].
_PROBE_HEADER = f"version 3.0\n\nqubit[{QX_WIDTH}] q\nbit[{QX_WIDTH}] b\n\n"
RESET_PHASE_PROBES = {
    "phase_minus": _PROBE_HEADER + "X q[0]\nX q[1]\nH q[1]\nreset q[0]\n",
    "already_zero": _PROBE_HEADER + "H q[1]\nS q[1]\nreset q[0]\n",
    "general": _PROBE_HEADER
    + "H q[0]\nRz(0.7) q[0]\nH q[1]\nRz(1.1) q[1]\nCNOT q[0], q[1]\nH q[2]\nCNOT q[1], q[2]\nRz(0.4) q[2]\n"
    + "H q[0]\nRz(0.3) q[0]\nreset q[0]\n",
}
# Single-shot runs of the native program up to its final measurement: each
# returns one mid-circuit branch's state.
BRANCH_SEEDS = 8

Circuit = Any


# ---------------------------------------------------------------- circuits


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_arms() -> list[dict[str, Any]]:
    """Each dynamic circuit restricted to its active qubits, with its record member and physical qubits."""
    from qiskit import qpy

    import snapshot_laws

    with ISA.open("rb") as handle:
        circuits = list(qpy.load(handle))
    members = {pub["name"]: pub["components"][0]["member"] for pub in json.loads(RECORD.read_text())["execution_pubs"]}
    arms = []
    for circuit in circuits:
        restricted, physical = snapshot_laws.restrict_circuit(circuit)
        branch = any(inst.operation.name == "if_else" for inst in restricted.data)
        arms.append(
            {
                "name": circuit.name,
                "member": members[circuit.name],
                "circuit": restricted,
                "physical": physical,
                "branch": branch,
            }
        )
    return arms


def serialize(circuit: Circuit) -> bytes:
    import io

    from qiskit import qpy

    buffer = io.BytesIO()
    qpy.dump(circuit, buffer)
    return buffer.getvalue()


def deserialize(payload: bytes) -> Circuit:
    import io

    from qiskit import qpy

    return qpy.load(io.BytesIO(payload))[0]


def _qubits(circuit: Circuit, instruction: Any) -> list[int]:
    return [circuit.find_bit(q).index for q in instruction.qubits]


def _condition(circuit: Circuit, operation: Any) -> tuple[int, int]:
    from qiskit.circuit import Clbit

    target, value = operation.condition
    if not isinstance(target, Clbit):
        raise ValueError(f"{circuit.name}: if_else reads {target!r}; deferral takes a single-clbit condition")
    return circuit.find_bit(target).index, int(value)


def defer(circuit: Circuit, body: str = "controlled") -> tuple[Circuit, dict[str, Any]]:
    """The deferred-measurement form on circuit.num_qubits + one ancilla per mid-circuit measure.

    body="controlled" applies each if_else body gate controlled by the ancilla
    that holds its clbit; "unconditional" and "removed" are the self-test's
    broken deferrals (control dropped, body dropped).
    """
    from qiskit import QuantumCircuit
    from qiskit.circuit import Gate

    data = [inst for inst in circuit.data if inst.operation.name != "barrier"]
    last_use: dict[int, int] = {}
    for position, inst in enumerate(data):
        for q in _qubits(circuit, inst):
            last_use[q] = position
    measured: set[int] = set()
    mid = []
    for position, inst in enumerate(data):
        if inst.operation.name == "measure":
            clbit = circuit.find_bit(inst.clbits[0]).index
            if clbit in measured:
                raise ValueError(f"{circuit.name}: clbit {clbit} is written twice")
            measured.add(clbit)
            if last_use[_qubits(circuit, inst)[0]] != position:
                mid.append(position)
    ancilla = {position: circuit.num_qubits + n for n, position in enumerate(mid)}
    out = QuantumCircuit(circuit.num_qubits + len(mid), circuit.num_clbits, global_phase=circuit.global_phase)
    holder: dict[int, int] = {}
    final: list[tuple[int, int]] = []
    consumed: set[int] = set()
    deferrals = []
    for position, inst in enumerate(data):
        if position in consumed:
            continue
        name = inst.operation.name
        qubits = _qubits(circuit, inst)
        if name == "measure":
            clbit = circuit.find_bit(inst.clbits[0]).index
            if position not in ancilla:
                final.append((qubits[0], clbit))
                continue
            a = ancilla[position]
            out.cx(qubits[0], a)
            holder[clbit] = a
            row: dict[str, Any] = {"measure": {"qubit": qubits[0], "clbit": clbit}, "ancilla": a, "reset": None}
            following = data[position + 1] if position + 1 < len(data) else None
            if following is not None and following.operation.name == "reset" and _qubits(circuit, following) == qubits:
                out.cx(a, qubits[0])
                consumed.add(position + 1)
                row["reset"] = f"CNOT q[{a}] -> q[{qubits[0]}]"
            deferrals.append(row)
            final.append((a, clbit))
        elif name == "reset":
            raise ValueError(f"{circuit.name}: reset of q{qubits} does not follow a deferred measure of that qubit")
        elif name == "if_else":
            clbit, value = _condition(circuit, inst.operation)
            if clbit not in holder:
                raise ValueError(
                    f"{circuit.name}: if_else reads clbit {clbit}, which no earlier deferred measure holds"
                )
            blocks = [(inst.operation.blocks[0], value)]
            if len(inst.operation.blocks) > 1 and inst.operation.blocks[1] is not None:
                blocks.append((inst.operation.blocks[1], 1 - value))
            for block, state in blocks:
                for inner in block.data:
                    if inner.operation.name == "barrier":
                        continue
                    if not isinstance(inner.operation, Gate):
                        raise ValueError(f"{circuit.name}: {inner.operation.name} inside an if_else body")
                    targets = [qubits[block.find_bit(q).index] for q in inner.qubits]
                    if body == "controlled":
                        out.append(inner.operation.control(1, ctrl_state=state), [holder[clbit], *targets])
                    elif body == "unconditional":
                        out.append(inner.operation, targets)
                    elif body != "removed":
                        raise ValueError(f"unknown body mode {body!r}")
                    deferrals.append(
                        {
                            "if_else": {"clbit": clbit, "value": state},
                            "control": holder[clbit],
                            "gate": inner.operation.name,
                            "targets": targets,
                            "body": body,
                        }
                    )
        elif name in ("while_loop", "for_loop", "switch_case", "box") or inst.clbits:
            raise ValueError(f"{circuit.name}: {name} is outside the deferral")
        else:
            out.append(inst.operation, qubits)
    for qubit, clbit in sorted(final, key=lambda pair: pair[1]):
        out.measure(qubit, clbit)
    return out, {"ancillas": sorted(ancilla.values()), "steps": deferrals}


def lower(circuit: Circuit) -> Circuit:
    """circuit over LOWERED gates, measure and reset by explicit substitution; every step is exact.

    SX = H S H with no phase; CRZ(theta) = Rz(theta/2) CNOT Rz(-theta/2) CNOT on
    the target. Barriers drop (the qx dialect writes none).
    """
    from qiskit import QuantumCircuit

    out = QuantumCircuit(circuit.num_qubits, circuit.num_clbits, global_phase=circuit.global_phase)
    for inst in circuit.data:
        name = inst.operation.name
        qubits = _qubits(circuit, inst)
        if name == "barrier":
            continue
        if name == "sx":
            out.h(qubits[0])
            out.s(qubits[0])
            out.h(qubits[0])
        elif name == "crz":
            if getattr(inst.operation, "ctrl_state", 1) != 1:
                raise ValueError("an open-controlled crz is outside the lowering")
            theta = float(inst.operation.params[0])
            out.rz(theta / 2, qubits[1])
            out.cx(qubits[0], qubits[1])
            out.rz(-theta / 2, qubits[1])
            out.cx(qubits[0], qubits[1])
        elif name in LOWERED:
            out.append(inst.operation, qubits)
        elif name == "measure":
            out.measure(qubits[0], circuit.find_bit(inst.clbits[0]).index)
        elif name == "reset":
            out.reset(qubits[0])
        else:
            raise ValueError(f"{name} is outside the lowering to the qx gate map")
    return out


# ---------------------------------------------------------------- cQASM


def emit_qx_unsnapped(circuit: Circuit, place: dict[int, int]) -> list[str]:
    """Stopgap for box_kite_cases.emit(circuit, place, dialect="qx", angle_grid=None).

    box_kite_cases.emit snaps every Rz to the pi/ANGLE_GRID grid and raises off
    it; the qx dialect's angle_grid=None opt-out prints each Rz angle from its
    float with the same .15f format. This writer reproduces that call's lines
    (DIALECTS["qx"] gate names, "G q[a], q[b]" for two-qubit gates, barriers
    omitted) so that swapping in the real call leaves every retained byte and
    sha256 unchanged; the self-test holds it to emit byte for byte on an
    on-grid circuit.
    """
    import box_kite_cases as cases

    names = cases.DIALECTS["qx"]
    lines = []
    for instruction in circuit.data:
        name = instruction.operation.name
        qubits = [place[circuit.find_bit(q).index] for q in instruction.qubits]
        if name == "barrier":
            continue
        if name not in names:
            raise ValueError(f"{name} is outside the qx gate map")
        if name in cases.TWO_QUBIT:
            lines.append(f"{names[name]} q[{qubits[0]}], q[{qubits[1]}]")
        elif name == "rz":
            lines.append(f"{names[name]}({float(instruction.operation.params[0]):.15f}) q[{qubits[0]}]")
        else:
            lines.append(f"{names[name]} q[{qubits[0]}]")
    return lines


def program(circuit: Circuit, comment: str) -> str:
    """Full QX program of a lowered circuit: header, gate segments, measure and reset lines in order."""
    import qi_zero_divisor_cases
    from qiskit import QuantumCircuit

    place = {q: q for q in range(circuit.num_qubits)}
    lines = [*qi_zero_divisor_cases.header(QX_WIDTH), f"// {comment}"]
    segment = QuantumCircuit(circuit.num_qubits)

    def flush() -> None:
        nonlocal segment
        lines.extend(emit_qx_unsnapped(segment, place))
        segment = QuantumCircuit(circuit.num_qubits)

    for inst in circuit.data:
        name = inst.operation.name
        qubits = _qubits(circuit, inst)
        if name == "measure":
            flush()
            lines.append(f"b[{circuit.find_bit(inst.clbits[0]).index}] = measure q[{qubits[0]}]")
        elif name == "reset":
            flush()
            lines.append(f"reset q[{qubits[0]}]")
        else:
            segment.append(inst.operation, qubits)
    flush()
    return "\n".join([*lines, ""])


def state_program(text: str) -> str:
    """The program without its trailing measurements, whose final state qxelarator returns intact."""
    lines = text.rstrip("\n").split("\n")
    while lines and MEASURE_LINE.fullmatch(lines[-1]):
        lines.pop()
    if any(MEASURE_LINE.fullmatch(line) or RESET_LINE.fullmatch(line) for line in lines):
        raise ValueError("a state program needs every measurement at the end and no reset")
    return "\n".join([*lines, ""])


def parse_program(text: str, num_clbits: int) -> Circuit:
    """A QX program back into a circuit: gate runs through box_kite_cases.parse_cqasm, measure and reset here."""
    import box_kite_cases as cases
    from qiskit import QuantumCircuit

    out = QuantumCircuit(QX_WIDTH, num_clbits)
    preamble = "\n".join(["version 3.0", f"qubit[{QX_WIDTH}] q", ""])
    run: list[str] = []

    def flush() -> None:
        if run:
            out.compose(cases.parse_cqasm(preamble + "\n".join(run) + "\n"), inplace=True)
            run.clear()

    for raw in text.split("\n"):
        line = raw.strip()
        measure, reset = MEASURE_LINE.fullmatch(line), RESET_LINE.fullmatch(line)
        if line.startswith(("version ", "qubit[", "bit[")):
            if line not in ("version 3.0", f"qubit[{QX_WIDTH}] q", f"bit[{QX_WIDTH}] b"):
                raise ValueError(f"declaration {line!r} differs from the QX program header")
        elif measure is not None:
            flush()
            if int(measure[1]) >= num_clbits:
                raise ValueError(f"{line!r} writes outside the circuit's {num_clbits} classical bits")
            out.measure(int(measure[2]), int(measure[1]))
        elif reset is not None:
            flush()
            out.reset(int(reset[1]))
        else:
            run.append(line)
    flush()
    return out


# ---------------------------------------------------------------- laws


def _terminal(circuit: Circuit) -> list[tuple[int, int]] | None:
    """(qubit, clbit) of every measurement when all of them close their qubits and no reset or branch occurs."""
    last: dict[int, int] = {}
    for position, inst in enumerate(circuit.data):
        if inst.operation.name in ("reset", "if_else"):
            return None
        for q in _qubits(circuit, inst):
            last[q] = position
    pairs = []
    for position, inst in enumerate(circuit.data):
        if inst.operation.name == "measure":
            qubit = _qubits(circuit, inst)[0]
            if last[qubit] != position:
                return None
            pairs.append((qubit, circuit.find_bit(inst.clbits[0]).index))
    return pairs


def law(payload: bytes) -> list[float]:
    """Pool worker: ideal recorded law, clbit 0 least significant.

    A circuit measured only at its end takes Statevector probabilities; one with
    a mid-circuit measure, reset or branch takes dynamic_density with an empty
    noise model, so the deferral proof compares two independent engines.
    """
    import numpy as np
    from qiskit.quantum_info import Statevector
    from qiskit_aer.noise import NoiseModel

    import dynamic_density
    import snapshot_laws

    circuit = deserialize(payload)
    pairs = _terminal(circuit)
    if pairs is None:
        restricted, _ = snapshot_laws.restrict_circuit(circuit)
        return [float(v) for v in dynamic_density.probabilities(restricted, NoiseModel())]
    if sorted(c for _, c in pairs) != list(range(circuit.num_clbits)):
        raise ValueError(f"{circuit.name}: measurements do not write each classical bit once")
    unitary = circuit.remove_final_measurements(inplace=False)
    by_clbit = [q for q, _ in sorted(pairs, key=lambda pair: pair[1])]
    probabilities = Statevector(unitary).probabilities(by_clbit)
    return [float(v) for v in np.asarray(probabilities)]


def statevector(payload: bytes) -> list[list[float]]:
    """Pool worker: Aer statevector of a measurement-free program, [re, im] per basis index."""
    from qiskit.quantum_info import Statevector

    data = Statevector(deserialize(payload)).data
    return [[float(v.real), float(v.imag)] for v in data]


def gap(a: list[float], b: list[float]) -> float:
    return max(abs(x - y) for x, y in zip(a, b, strict=True))


def score(values: list[float], law_: list[float]) -> float:
    return math.fsum(v * p for v, p in zip(values, law_, strict=True))


def bit(key: str, qubit: int) -> str:
    """The character of `qubit` in a QX key, qubit 0 at the rightmost character."""
    return key[len(key) - 1 - qubit]


def recorded(key: str, readout: list[int], reverse: bool = False) -> int:
    """Recorded value r = sum c_k 2^k, c_k the QX character of readout[k]; reverse reads qubit 0 leftmost."""
    return sum(int(key[q] if reverse else bit(key, q)) << k for k, q in enumerate(readout))


def counts_vector(histograms: list[dict[str, int]], readout: list[int], reverse: bool = False) -> list[int]:
    vector = [0] * 2 ** len(readout)
    for histogram in histograms:
        for key, count in histogram.items():
            if len(key) != QX_WIDTH or set(key) - {"0", "1"} or type(count) is not int or count < 0:
                raise ValueError(f"QX key {key!r} or count {count!r} is malformed")
            for q in range(QX_WIDTH):
                if q not in readout and bit(key, q) != "0":
                    raise ValueError(f"QX key {key!r} reads 1 on unmeasured qubit {q}")
            vector[recorded(key, readout, reverse)] += count
    return vector


def state_law(amplitudes: dict[str, list[float]], readout: list[int], idle: list[int]) -> list[float]:
    """Marginal law of a qxelarator state over the readout qubits; keys absent from the state carry zero."""
    out = [0.0] * 2 ** len(readout)
    for key, (re_, im) in amplitudes.items():
        if len(key) != QX_WIDTH or set(key) - {"0", "1"}:
            raise ValueError(f"QX state key {key!r} is malformed")
        weight = re_ * re_ + im * im
        if weight > EXACT_TOL and any(bit(key, q) != "0" for q in idle):
            raise ValueError(f"QX state carries weight {weight} on {key!r}, outside the active qubits")
        out[recorded(key, readout)] += weight
    return out


def fidelity(amplitudes: dict[str, list[float]], reference: list[list[float]]) -> float:
    """|<qx|aer>|^2; the cQASM drops the global phase, which the overlap's modulus ignores."""
    overlap = complex(0.0)
    for key, (re_, im) in amplitudes.items():
        ar, ai = reference[int(key, 2)]
        overlap += complex(re_, -im) * complex(ar, ai)
    return abs(overlap) ** 2


# ---------------------------------------------------------------- build


def off_grid(built: dict[str, Any]) -> dict[str, Any]:
    """Every Rz of the lowered deferred programs that box_kite_cases.snap_angle refuses, and the grid it enforces.

    The deferred form of each arm holds every Rz of its native form plus the
    controlled body's; instruction indices refer to the lowered deferred form.
    """
    import box_kite_cases as cases

    rows = []
    counts = {}
    for form in built["forms"]:
        if form["form"] != "deferred":
            continue
        arm, lowered = form["arm"], form["lowered"]
        total = failing = 0
        for position, inst in enumerate(lowered.data):
            if inst.operation.name != "rz":
                continue
            total += 1
            theta = float(inst.operation.params[0])
            try:
                cases.snap_angle(theta)
            except ValueError:
                failing += 1
                qubit = _qubits(lowered, inst)[0]
                physical = arm["physical"][qubit] if qubit < len(arm["physical"]) else None
                rows.append(
                    {
                        "circuit": arm["member"],
                        "instruction": position,
                        "gate": "rz",
                        "qx_qubit": qubit,
                        "physical_qubit": physical,
                        "value": repr(theta),
                    }
                )
        counts[arm["member"]] = {"rz": total, "off_grid": failing}
    return {
        "grid": f"pi/{cases.ANGLE_GRID}",
        "tolerance": cases.ANGLE_TOLERANCE,
        "counts": counts,
        "distinct_values": sorted({row["value"] for row in rows}, key=float),
        "rows": rows,
    }


def build() -> dict[str, Any]:
    """Every form, program text and ideal-law stage of both arms, computed in the repository interpreter."""
    arms = load_arms()
    forms = []
    for arm in arms:
        deferred, steps = defer(arm["circuit"])
        lowered_deferred = lower(deferred)
        readout = [q for q, _ in sorted(_final_measures(lowered_deferred), key=lambda pair: pair[1])]
        comment = (
            f"{arm['member']} deferred-measurement form; restricted qubit k on q[k] (physical "
            f"{arm['physical']}), ancilla q[{QX_ANCILLA}]; c0 = q[{readout[0]}], c1 = q[{readout[1]}]"
        )
        forms.append(
            {
                "arm": arm,
                "form": "deferred",
                "circuit": deferred,
                "lowered": lowered_deferred,
                "steps": steps,
                "readout": readout,
                "text": program(lowered_deferred, comment),
            }
        )
        if steps["ancillas"] != [QX_ANCILLA]:
            raise ValueError(f"{arm['member']}: deferral ancillas {steps['ancillas']}, not q[{QX_ANCILLA}]")
        if not arm["branch"]:
            native = lower(arm["circuit"])
            readout = [q for q, _ in sorted(_all_measures(native), key=lambda pair: pair[1])]
            comment = (
                f"{arm['member']} native form; restricted qubit k on q[k] (physical {arm['physical']}); "
                f"mid-circuit c0 = q[{readout[0]}], c1 = q[{readout[1]}]"
            )
            forms.append(
                {
                    "arm": arm,
                    "form": "native",
                    "circuit": arm["circuit"],
                    "lowered": native,
                    "steps": None,
                    "readout": readout,
                    "text": program(native, comment),
                }
            )
    return {"arms": arms, "forms": forms}


def _final_measures(circuit: Circuit) -> list[tuple[int, int]]:
    pairs = _terminal(circuit)
    if pairs is None:
        raise ValueError(f"{circuit.name}: the deferred form measures before its end")
    return pairs


def _all_measures(circuit: Circuit) -> list[tuple[int, int]]:
    return [
        (_qubits(circuit, inst)[0], circuit.find_bit(inst.clbits[0]).index)
        for inst in circuit.data
        if inst.operation.name == "measure"
    ]


def file_name(form: dict[str, Any]) -> str:
    return f"{form['arm']['member']}-{form['form']}.cq"


def stages(built: dict[str, Any], texts: dict[str, str]) -> dict[str, Any]:
    """Reference law of each arm and every stage's law and gap: deferred, lowered and parsed from texts."""
    arms, forms = built["arms"], built["forms"]
    jobs = [serialize(arm["circuit"]) for arm in arms]
    for form in forms:
        if form["form"] == "deferred":
            jobs.append(serialize(form["circuit"]))
        jobs.append(serialize(form["lowered"]))
        parsed = parse_program(texts[file_name(form)], form["circuit"].num_clbits)
        jobs.append(serialize(parsed))
    laws = parallel.ordered_map(law, jobs, min_items=2)
    reference = {arm["member"]: laws[n] for n, arm in enumerate(arms)}
    position = len(arms)
    out: dict[str, Any] = {"reference": reference, "forms": {}}
    for form in forms:
        member = form["arm"]["member"]
        row: dict[str, Any] = {}
        names = (["deferred"] if form["form"] == "deferred" else []) + ["lowered", "parsed"]
        for name in names:
            row[name] = {"law": laws[position], "max_gap": gap(laws[position], reference[member])}
            position += 1
        out["forms"][file_name(form)] = row
    return out


# ---------------------------------------------------------------- reset models


def branches(circuit: Circuit, reset_model: str) -> dict[int, Any]:
    """Unnormalized pure branch states of a circuit with projective measures, keyed by recorded value.

    reset_model "ideal" applies X to a branch whose qubit holds 1 and refuses a
    branch with weight on both values (a mixed reset); "qxelarator" is the
    observed qxelarator 0.10.0 map: zero weight on 1 leaves the state as it is,
    otherwise every amplitude pair (a0x, a1x) becomes sqrt(|a0x|^2 + |a1x|^2)
    on the 0 side with zero phase.
    """
    import numpy as np
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector

    n = circuit.num_qubits
    index = np.arange(2**n)
    states: dict[int, Any] = {0: Statevector.from_label("0" * n).data}
    segment = QuantumCircuit(n)

    def flush() -> None:
        nonlocal segment
        if segment.data:
            for key in states:
                states[key] = Statevector(states[key]).evolve(segment).data
        segment = QuantumCircuit(n)

    for inst in circuit.data:
        name = inst.operation.name
        qubits = _qubits(circuit, inst)
        if name not in ("measure", "reset"):
            segment.append(inst.operation, qubits)
            continue
        flush()
        one = ((index >> qubits[0]) & 1) == 1
        if name == "measure":
            clbit = circuit.find_bit(inst.clbits[0]).index
            split: dict[int, Any] = {}
            for key, vector in states.items():
                for outcome, mask in ((0, ~one), (1, one)):
                    projected = np.where(mask, vector, 0)
                    if np.vdot(projected, projected).real > 0:
                        split[(key & ~(1 << clbit)) | (outcome << clbit)] = projected
            states = split
            continue
        for key, vector in states.items():
            low, high = vector[~one], vector[one]
            if np.vdot(high, high).real == 0:
                continue
            reset = np.zeros_like(vector)
            if reset_model == "ideal":
                if np.vdot(low, low).real != 0:
                    raise ValueError("an ideal reset of a branch with weight on 0 and 1 is a mixture")
                reset[~one] = high
            elif reset_model == "qxelarator":
                reset[~one] = np.sqrt(np.abs(low) ** 2 + np.abs(high) ** 2)
            else:
                raise ValueError(f"unknown reset model {reset_model!r}")
            states[key] = reset
    flush()
    return states


def branch_law(item: tuple[bytes, str]) -> list[float]:
    """Pool worker: recorded law of a serialized circuit under a reset model, clbit 0 least significant."""
    import numpy as np

    payload, reset_model = item
    circuit = deserialize(payload)
    out = [0.0] * 2**circuit.num_clbits
    for key, vector in branches(circuit, reset_model).items():
        out[key] += float(np.vdot(vector, vector).real)
    return out


def law_item(item: tuple[str, bytes]) -> list[float]:
    """Pool worker: ("law", payload) through law, or (reset model, payload) through branch_law."""
    kind, payload = item
    return law(payload) if kind == "law" else branch_law((payload, kind))


def amplitudes_of(vector: Any) -> dict[str, list[float]]:
    """Normalized nonzero amplitudes of a QX_WIDTH-qubit vector in QX key form, qubit 0 rightmost."""
    import numpy as np

    norm = math.sqrt(float(np.vdot(vector, vector).real))
    return {
        format(n, f"0{QX_WIDTH}b"): [float(v.real) / norm, float(v.imag) / norm]
        for n, v in enumerate(vector)
        if abs(v) / norm > 1e-12
    }


def state_fidelity(a: dict[str, list[float]], b: dict[str, list[float]]) -> float:
    overlap = complex(0.0)
    for key, (re_, im) in a.items():
        if key in b:
            overlap += complex(re_, -im) * complex(*b[key])
    return abs(overlap) ** 2


def probe_models(item: tuple[str, dict[str, list[float]]]) -> dict[str, Any]:
    """Pool worker: fidelity of a retained QX state with each reset model's state of the same program."""
    text, qx_state = item
    circuit = parse_program(text, 0)
    row: dict[str, Any] = {}
    for model in ("qxelarator", "ideal"):
        try:
            (vector,) = branches(circuit, model).values()
        except ValueError as error:
            row[model] = str(error)
            continue
        row[model] = state_fidelity(qx_state, amplitudes_of(vector))
    return row


def native_branches(item: tuple[str, int, dict[str, Any]]) -> dict[str, Any]:
    """Pool worker: a retained QX branch state of the native program against each reset model's branch."""
    text, clbit_qubit, run = item
    circuit = parse_program(text, 1)
    key = next(iter(run["results"]))
    outcome = int(bit(key, clbit_qubit))
    row: dict[str, Any] = {"seed": run["seed"], "c0": outcome}
    for model in ("qxelarator", "ideal"):
        vector = branches(circuit, model)[outcome]
        row[model] = state_fidelity(run["state"], amplitudes_of(vector))
    return row


def branch_program(text: str) -> str:
    """The native program without its trailing measurements; its mid-circuit measure and reset remain."""
    lines = text.rstrip("\n").split("\n")
    while lines and MEASURE_LINE.fullmatch(lines[-1]):
        lines.pop()
    return "\n".join([*lines, ""])


# ---------------------------------------------------------------- QX runs


def sample_seed(position: int, n: int) -> int:
    """Seed of run n of the program at `position` in form order: each program draws its own stream."""
    return BASE_SEED + 1000 * position + n


def qx_jobs(texts: dict[str, str], forms: list[dict[str, Any]], seeds: int) -> list[dict[str, Any]]:
    jobs: list[dict[str, Any]] = [
        {"kind": "sample", "file": "reset-register-probe", "text": RESET_REGISTER_PROBE, "shots": 64,
         "seed": BASE_SEED}
    ]  # fmt: skip
    for name, text in RESET_PHASE_PROBES.items():
        jobs.append({"kind": "state", "file": f"reset-phase-probe-{name}", "text": text, "seed": BASE_SEED})
    for position, form in enumerate(forms):
        name = file_name(form)
        if form["form"] == "deferred":
            jobs.append({"kind": "state", "file": name, "text": state_program(texts[name]), "seed": BASE_SEED})
        else:
            for n in range(BRANCH_SEEDS):
                jobs.append(
                    {"kind": "branch", "file": name, "text": branch_program(texts[name]), "seed": BASE_SEED + n}
                )
        for n in range(seeds):
            jobs.append(
                {"kind": "sample", "file": name, "text": texts[name], "shots": QX_SHOTS,
                 "seed": sample_seed(position, n)}
            )  # fmt: skip
    return jobs


def run_qx(jobs: list[dict[str, Any]]) -> dict[str, Any]:
    """The QX jobs on qxelarator under $QI_PYTHON in a subprocess: this file's --qx-worker mode."""
    interpreter = os.environ.get("QI_PYTHON") or str(QI_PYTHON_DEFAULT)
    completed = subprocess.run(
        [interpreter, "-I", "-B", str(Path(__file__).resolve()), "--qx-worker"],
        input=json.dumps(jobs),
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise SystemExit(f"qxelarator worker under {interpreter} failed:\n{completed.stderr}")
    result: dict[str, Any] = json.loads(completed.stdout)
    return result


def qx_job(job: dict[str, Any]) -> Any:
    """Pool worker under $QI_PYTHON: a sampled histogram, a final state, or one shot's branch state and key."""
    import box_kite_qx_sweep as sweep  # its filter silences qxelarator's SWIG import warnings
    import qxelarator

    if job["kind"] == "sample":
        return sweep.emulate((job["text"], job["shots"], job["seed"]))
    result = qxelarator.execute_string(job["text"], iterations=1, seed=job["seed"])
    if isinstance(result, qxelarator.SimulationError):
        raise RuntimeError(f"qxelarator: {result}")
    state = {str(key): [float(v.real), float(v.imag)] for key, v in sorted(result.state.items())}
    if job["kind"] == "state":
        return state
    return {"results": {str(key): int(value) for key, value in result.results.items()}, "state": state}


def qx_worker() -> int:
    import platform
    from importlib import metadata

    jobs = json.loads(sys.stdin.read())
    if metadata.version("qxelarator") != QXELARATOR:
        raise SystemExit(f"qxelarator {metadata.version('qxelarator')} is installed; the check pins {QXELARATOR}")
    results = parallel.ordered_map(qx_job, jobs, min_items=2)
    versions = {name: metadata.version(name) for name in ("qxelarator", "libqasm", "qiskit")}
    environment = {"python": platform.python_version(), **versions, "workers": parallel.workers()}
    print(json.dumps({"environment": environment, "results": results}))
    return 0


def native_form(record: dict[str, Any]) -> dict[str, Any]:
    (row,) = [row for row in record["programs"] if row["form"] == "native"]
    return row


def reset_evidence(record: dict[str, Any], texts: dict[str, str]) -> dict[str, Any]:
    """Each reset model against the retained QX probe and branch states, and its law of the native program."""
    probes = record["qx"]["reset_phase_probes"]
    probe_rows = parallel.ordered_map(
        probe_models, [(RESET_PHASE_PROBES[name], probes[name]["amplitudes"]) for name in sorted(probes)], min_items=2
    )
    native = native_form(record)
    text = texts[native["file"]]
    runs = record["qx"]["native_branches"]
    branch_rows = parallel.ordered_map(
        native_branches, [(branch_program(text), native["readout"][0], run) for run in runs], min_items=2
    )
    parsed = serialize(parse_program(text, 2))
    laws = parallel.ordered_map(branch_law, [(parsed, "ideal"), (parsed, "qxelarator")], min_items=2)
    return {
        "probes": dict(zip(sorted(probes), probe_rows, strict=True)),
        "native_branches": branch_rows,
        "native_law": {"ideal": laws[0], "qxelarator": laws[1]},
    }


def require_reset_evidence(evidence: dict[str, Any], reference: list[float]) -> None:
    """The qxelarator model reproduces every retained QX state; the ideal reset differs where weight sat on 1."""
    for name, row in evidence["probes"].items():
        if abs(1.0 - row["qxelarator"]) > EXACT_TOL:
            raise ValueError(f"reset probe {name}: the qxelarator model's fidelity is {row['qxelarator']}")
    if evidence["probes"]["phase_minus"]["ideal"] > 0.5:
        raise ValueError("the ideal reset reproduces the |-> probe, which the qxelarator model must alone explain")
    if abs(1.0 - evidence["probes"]["already_zero"]["ideal"]) > EXACT_TOL:
        raise ValueError("the ideal reset differs from QX where the reset qubit holds no weight on 1")
    if {row["c0"] for row in evidence["native_branches"]} != {0, 1}:
        raise ValueError("the retained native branch states do not cover both mid-circuit outcomes")
    for row in evidence["native_branches"]:
        if abs(1.0 - row["qxelarator"]) > EXACT_TOL:
            raise ValueError(f"native branch seed {row['seed']}: qxelarator model fidelity {row['qxelarator']}")
        if (row["c0"] == 0) != (abs(1.0 - row["ideal"]) <= EXACT_TOL):
            raise ValueError(f"native branch seed {row['seed']}: the ideal reset fidelity {row['ideal']} breaks c0")
    if gap(evidence["native_law"]["ideal"], reference) > EXACT_TOL:
        raise ValueError("the branch stepper with an ideal reset leaves the dynamic_density reference")
    if gap(evidence["native_law"]["qxelarator"], reference) <= EXACT_TOL:
        raise ValueError("the qxelarator reset model leaves the native law at the reference")


def out(path: Path, seeds: int) -> dict[str, Any]:
    built = build()
    texts = {file_name(form): form["text"] for form in built["forms"]}
    staged = stages(built, texts)
    for name, row in staged["forms"].items():
        for stage, values in row.items():
            if values["max_gap"] > EXACT_TOL:
                raise SystemExit(f"{name}: the {stage} law differs from the reference by {values['max_gap']}")
    jobs = qx_jobs(texts, built["forms"], seeds)
    qx = run_qx(jobs)
    register = qx["results"][0]
    states: dict[str, Any] = {}
    probes: dict[str, Any] = {}
    native_runs: list[dict[str, Any]] = []
    histograms: dict[str, list[dict[str, Any]]] = {}
    for job, result in zip(jobs[1:], qx["results"][1:], strict=True):
        if job["file"].startswith("reset-phase-probe-"):
            name = job["file"].removeprefix("reset-phase-probe-")
            probes[name] = {"text_sha256": sha256(job["text"].encode()), "amplitudes": result}
        elif job["kind"] == "state":
            states[job["file"]] = {"sha256": sha256(job["text"].encode()), "seed": job["seed"], "amplitudes": result}
        elif job["kind"] == "branch":
            native_runs.append({"seed": job["seed"], "text_sha256": sha256(job["text"].encode()), **result})
        else:
            histograms.setdefault(job["file"], []).append({"seed": job["seed"], "counts": result})
    path.parent.mkdir(parents=True, exist_ok=True)
    for name, text in texts.items():
        (path.parent / name).write_text(text, encoding="utf-8")
    record: dict[str, Any] = {
        "schema": SCHEMA,
        "isa": {"path": ISA.relative_to(ROOT).as_posix(), "sha256": sha256(ISA.read_bytes())},
        "record": {"path": RECORD.relative_to(ROOT).as_posix(), "sha256": sha256(RECORD.read_bytes())},
        "qx_width": QX_WIDTH,
        "bit_order": (
            "QX keys hold one character per declared qubit, qubit 0 rightmost, each the qubit's last measured "
            "outcome; recorded value r = c0 + 2 c1 (clbit 0 least significant) reads c_k from readout[k]"
        ),
        "arms": [
            {
                "name": arm["name"],
                "member": arm["member"],
                "physical_qubits": arm["physical"],
                "reference_law": staged["reference"][arm["member"]],
            }
            for arm in built["arms"]
        ],
        "angle_grid": off_grid(built),
        "programs": [
            {
                "file": file_name(form),
                "member": form["arm"]["member"],
                "form": form["form"],
                "sha256": sha256(form["text"].encode()),
                "readout": form["readout"],
                "deferral": form["steps"],
                "stages": staged["forms"][file_name(form)],
            }
            for form in built["forms"]
        ],
        "qx": {
            "environment": qx["environment"],
            "opensquirrel": "not used: QX executes cQASM without compiler passes",
            "reset_register_probe": {"text_sha256": sha256(RESET_REGISTER_PROBE.encode()), "counts": register},
            "reset_phase_probes": probes,
            "native_branches": native_runs,
            "shots": QX_SHOTS,
            "seed_rule": (
                "sampled run n of the program at position p in programs order takes base_seed + 1000 p + n; "
                "state runs take base_seed; native branch run n takes base_seed + n"
            ),
            "base_seed": BASE_SEED,
            "seeds": seeds,
            "states": states,
            "samples": histograms,
        },
    }
    record["reset_model"] = reset_evidence(record, texts)
    record["comparison"] = compare_qx(record)
    path.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    try:
        require_verdicts(record)
    except ValueError as error:
        raise SystemExit(f"{path}: {error}") from error
    return record


# ---------------------------------------------------------------- comparison


def compare_qx(record: dict[str, Any], reverse: bool = False) -> dict[str, Any]:
    """QX laws against the reference and the qxelarator reset model.

    exact: each deferred program's QX state marginal against the reference.
    deferred_pair: pooled counts of both deferred programs against the
    reference; native_vs_reference: the deferred feedback and the native
    no-feedback counts against the reference; native_vs_reset_model: the same
    counts against the reference (feedback) and the qxelarator reset model's
    law (no-feedback). Each sampled comparison is
    n21_exact_model_validation.compare at total tail TAIL.
    """
    import n21_exact_model_validation as validation

    members, contracts = validation.endpoint(RECORD)
    reference = {arm["name"]: arm["reference_law"] for arm in record["arms"]}
    by_member = {arm["member"]: arm["name"] for arm in record["arms"]}
    programs = {row["file"]: row for row in record["programs"]}
    exact: dict[str, Any] = {}
    exact_laws: dict[str, list[float]] = {}
    for name, state in sorted(record["qx"]["states"].items()):
        row = programs[name]
        law_ = state_law(state["amplitudes"], row["readout"], [q for q in range(QX_ANCILLA + 1, QX_WIDTH)])
        exact_laws[row["member"]] = law_
        exact[name] = {"law": law_, "norm": math.fsum(law_), "max_gap": gap(law_, reference[by_member[row["member"]]])}
    vectors: dict[str, list[int]] = {}
    shots = None
    for position, row in enumerate(record["programs"]):
        runs = record["qx"]["samples"][row["file"]]
        seeds = [run["seed"] for run in runs]
        if seeds != [sample_seed(position, n) for n in range(record["qx"]["seeds"])]:
            raise ValueError(f"{row['file']}: seeds {seeds} break the seed rule")
        for run in runs:
            if sum(run["counts"].values()) != record["qx"]["shots"]:
                raise ValueError(f"{row['file']}: seed {run['seed']} holds {sum(run['counts'].values())} shots")
        vectors[row["file"]] = counts_vector([run["counts"] for run in runs], row["readout"], reverse)
        if shots is not None and sum(vectors[row["file"]]) != shots:
            raise ValueError("sampled programs hold different shot totals")
        shots = sum(vectors[row["file"]])
    if shots is None:
        raise ValueError("the record holds no sampled program")
    files = {(row["member"], row["form"]): row["file"] for row in record["programs"]}
    feedback, control = (by_member[term.member] for term in contracts[0].terms)
    feedback_member, control_member = (term.member for term in contracts[0].terms)

    def pooled(control_form: str, control_law: list[float]) -> dict[str, Any]:
        counts = {
            feedback: vectors[files[(feedback_member, "deferred")]],
            control: vectors[files[(control_member, control_form)]],
        }
        laws = {feedback: reference[feedback], control: control_law}
        return {
            "files": [files[(feedback_member, "deferred")], files[(control_member, control_form)]],
            **validation.compare({"shots": shots, "counts": counts}, laws, members, contracts),
        }

    model_law = record["reset_model"]["native_law"]["qxelarator"]
    contract = contracts[0]
    exact_scores = {term.member: score(list(term.values), exact_laws[term.member]) for term in contract.terms}
    reference_scores = {
        term.member: score(list(term.values), reference[by_member[term.member]]) for term in contract.terms
    }
    return {
        "exact": exact,
        "exact_contrast": math.fsum(term.sign * exact_scores[term.member] for term in contract.terms),
        "reference_scores": reference_scores,
        "reference_contrast": math.fsum(term.sign * reference_scores[term.member] for term in contract.terms),
        "reset_model_control_score": score(list(contract.terms[1].values), model_law),
        "deferred_pair": pooled("deferred", reference[control]),
        "native_vs_reference": pooled("native", reference[control]),
        "native_vs_reset_model": pooled("native", model_law),
    }


def require_verdicts(record: dict[str, Any]) -> None:
    """Deferred programs match the reference exactly and in sample; the native arm matches the reset model only."""
    comparison = record["comparison"]
    for name, row in comparison["exact"].items():
        if row["max_gap"] > EXACT_TOL or abs(row["norm"] - 1.0) > EXACT_TOL:
            raise ValueError(f"{name}: QX exact law gap {row['max_gap']} or norm {row['norm']} leaves {EXACT_TOL}")
    if abs(comparison["exact_contrast"] - comparison["reference_contrast"]) > EXACT_TOL:
        raise ValueError(f"QX exact contrast {comparison['exact_contrast']} differs from the reference")
    if not comparison["deferred_pair"]["passed"]:
        raise ValueError(f"deferred QX counts leave the radius: {comparison['deferred_pair']['failures']}")
    if not comparison["native_vs_reset_model"]["passed"]:
        raise ValueError(f"native QX counts leave the reset model: {comparison['native_vs_reset_model']['failures']}")
    if comparison["native_vs_reference"]["passed"]:
        raise ValueError("native QX counts pass the reference, which the qxelarator reset model excludes")


def _close(a: Any, b: Any, tol: float = EXACT_TOL) -> bool:
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(_close(a[k], b[k], tol) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_close(x, y, tol) for x, y in zip(a, b, strict=True))
    if isinstance(a, float) or isinstance(b, float):
        return isinstance(a, (int, float)) and isinstance(b, (int, float)) and abs(a - b) <= tol
    return bool(a == b)


def verify(record: dict[str, Any], directory: Path) -> dict[str, Any]:
    """Every claim of a record from the current circuits and the retained programs; raises on a difference."""
    if record.get("schema") != SCHEMA:
        raise ValueError(f"schema {record.get('schema')!r} is not {SCHEMA}")
    for key, path in (("isa", ISA), ("record", RECORD)):
        if record[key]["sha256"] != sha256(path.read_bytes()):
            raise ValueError(f"{record[key]['path']} differs from the input the record was built from")
    built = build()
    texts = {}
    for row, form in zip(record["programs"], built["forms"], strict=True):
        name = file_name(form)
        text = (directory / row["file"]).read_text(encoding="utf-8")
        if row["file"] != name or sha256(text.encode()) != row["sha256"]:
            raise ValueError(f"{row['file']}: retained bytes differ from the record's sha256")
        if text != form["text"]:
            raise ValueError(f"{name}: the current circuits export to other bytes than the retained program")
        if (row["readout"], row["deferral"], row["form"]) != (form["readout"], form["steps"], form["form"]):
            raise ValueError(f"{name}: readout map, deferral steps or form differ from the current construction")
        texts[name] = text
    staged = stages(built, texts)
    for arm in record["arms"]:
        if gap(arm["reference_law"], staged["reference"][arm["member"]]) > EXACT_TOL:
            raise ValueError(f"{arm['member']}: reference law differs from the recomputed one")
    for row in record["programs"]:
        for stage, values in staged["forms"][row["file"]].items():
            if values["max_gap"] > EXACT_TOL:
                raise ValueError(f"{row['file']}: the {stage} law differs from the reference by {values['max_gap']}")
        if not _close(row["stages"], staged["forms"][row["file"]]):
            raise ValueError(f"{row['file']}: retained stage laws differ from the recomputed ones")
    if record["angle_grid"] != off_grid(built):
        raise ValueError("the off-grid Rz list differs from the current lowering")
    qx = record["qx"]
    if qx["reset_register_probe"] != {"text_sha256": sha256(RESET_REGISTER_PROBE.encode()), "counts": {"01": 64}}:
        raise ValueError(f"register probe {qx['reset_register_probe']} does not keep the measured character")
    for name, probe in qx["reset_phase_probes"].items():
        if probe["text_sha256"] != sha256(RESET_PHASE_PROBES[name].encode()):
            raise ValueError(f"reset phase probe {name}: text differs from the probe that ran")
    native = native_form(record)
    for n, run in enumerate(qx["native_branches"]):
        if (run["seed"], run["text_sha256"]) != (BASE_SEED + n, sha256(branch_program(texts[native["file"]]).encode())):
            raise ValueError(f"native branch run {n}: seed or program differs from the branch program")
    evidence = reset_evidence(record, texts)
    member = {arm["member"]: arm["reference_law"] for arm in record["arms"]}[native["member"]]
    require_reset_evidence(evidence, member)
    if not _close(evidence, record["reset_model"]):
        raise ValueError("the retained reset-model evidence differs from the recomputed one")
    jobs = []
    for name, state in sorted(qx["states"].items()):
        text = state_program(texts[name])
        if state["sha256"] != sha256(text.encode()):
            raise ValueError(f"{name}: the state program's sha256 differs from the retained program's")
        jobs.append(serialize(parse_program(text, 0)))
    references = parallel.ordered_map(statevector, jobs, min_items=2)
    fidelities = {}
    for (name, state), reference in zip(sorted(qx["states"].items()), references, strict=True):
        value = fidelity(state["amplitudes"], reference)
        if abs(1.0 - value) > EXACT_TOL:
            raise ValueError(f"{name}: QX state fidelity {value} with the Aer statevector of its program")
        fidelities[name] = value
    comparison = compare_qx(record)
    if not _close(comparison, record["comparison"]):
        raise ValueError("the retained comparison differs from the recomputed one")
    require_verdicts(record)
    return {"comparison": comparison, "fidelities": fidelities}


# ---------------------------------------------------------------- self-test


def _reject(label: str, action: Callable[[], Any]) -> None:
    try:
        action()
    except ValueError:
        return
    raise AssertionError(f"{label} was accepted")


def qx_key(value: int, readout: list[int]) -> str:
    """The QX key whose readout qubits hold recorded value `value` and whose other qubits read 0."""
    key = ["0"] * QX_WIDTH
    for k, q in enumerate(readout):
        key[QX_WIDTH - 1 - q] = str((value >> k) & 1)
    return "".join(key)


def self_test() -> None:
    import box_kite_cases as cases
    import numpy as np
    from qiskit import QuantumCircuit

    # The stopgap equals box_kite_cases.emit on an on-grid circuit byte for byte.
    grid = QuantumCircuit(3)
    grid.h(0)
    grid.x(1)
    grid.z(2)
    grid.s(0)
    grid.sdg(1)
    grid.cx(0, 2)
    grid.cz(1, 2)
    for k in (-63, -17, -1, 0, 3, 32, 64, 127):
        grid.rz(k * math.pi / cases.ANGLE_GRID, k % 3)
    place = {0: 4, 1: 0, 2: 9}
    if emit_qx_unsnapped(grid, place) != cases.emit(grid, place, dialect="qx"):
        raise AssertionError("the stopgap writer differs from box_kite_cases.emit on an on-grid circuit")
    built = build()
    texts = {file_name(form): form["text"] for form in built["forms"]}
    staged = stages(built, texts)
    for name, row in staged["forms"].items():
        for stage, values in row.items():
            if values["max_gap"] > EXACT_TOL:
                raise AssertionError(f"{name}: honest {stage} law gap {values['max_gap']}")
    reference = staged["reference"]
    forms = {file_name(form): form for form in built["forms"]}
    feedback = next(form for form in built["forms"] if form["arm"]["branch"])
    native = next(form for form in built["forms"] if form["form"] == "native")
    feedback_name = file_name(feedback)
    clbits = feedback["circuit"].num_clbits

    # Corrupted cQASM lines, re-hashed so the law and the parser, not the digest, catch them.
    lines = texts[feedback_name].split("\n")
    # The middle CZ of the feedback program moves the law by 1/8; an early or the
    # last CZ acts where CZ and CNOT agree on the reachable states.
    cz_lines = [n for n, line in enumerate(lines) if line.startswith("CZ ")]
    middle_cz = cz_lines[len(cz_lines) // 2]
    copy_line = next(n for n, line in enumerate(lines) if line == f"CNOT q[5], q[{QX_ANCILLA}]")
    first_rz = next(n for n, line in enumerate(lines) if line.startswith("Rz("))
    corrupt_cz, corrupt_copy, unparseable, binary = lines.copy(), lines.copy(), lines.copy(), lines.copy()
    corrupt_cz[middle_cz] = corrupt_cz[middle_cz].replace("CZ ", "CNOT ", 1)
    corrupt_copy[copy_line] = f"CNOT q[5], q[{QX_ANCILLA + 1}]"
    unparseable[first_rz] = "Rz(0.1.2) q[1]"
    binary.insert(first_rz, "c-X q[7], q[1]")
    _reject("an unparseable Rz line", lambda: parse_program("\n".join(unparseable), clbits))
    _reject("a cQASM 1.0 binary-controlled line", lambda: parse_program("\n".join(binary), clbits))
    # Every law that must move off the reference, and the native program under both reset models, in one pool:
    # corrupted texts, deferrals that drop the control or the body (as circuits and as exported programs).
    moved: list[tuple[str, tuple[str, bytes]]] = [
        ("the middle CZ line rewritten as CNOT", ("law", serialize(parse_program("\n".join(corrupt_cz), clbits)))),
        ("the deferral copy onto another qubit", ("law", serialize(parse_program("\n".join(corrupt_copy), clbits)))),
    ]
    for body in ("unconditional", "removed"):
        broken, _ = defer(feedback["arm"]["circuit"], body=body)
        exported = parse_program(program(lower(broken), "broken"), clbits)
        moved += [
            (f"a deferral with the body {body}", ("law", serialize(broken))),
            (f"the exported {body} deferral", ("law", serialize(exported))),
        ]
    native_payload = serialize(parse_program(texts[file_name(native)], clbits))
    items = [item for _, item in moved] + [("ideal", native_payload), ("qxelarator", native_payload)]
    laws = parallel.ordered_map(law_item, items, min_items=2)
    for (label, _), law_ in zip(moved, laws, strict=False):
        shift = gap(law_, reference[feedback["arm"]["member"]])
        if shift <= EXACT_TOL:
            raise AssertionError(f"{label} left the law within {EXACT_TOL} ({shift})")
    # Reset models: the ideal stepper reproduces the dynamic_density law of the native program and refuses a
    # mixed reset; the qxelarator model turns |1>|-> into |0>|+> and keeps the phase when the qubit reads 0.
    ideal, model = laws[-2], laws[-1]
    if gap(ideal, reference[native["arm"]["member"]]) > EXACT_TOL:
        raise AssertionError("the ideal branch stepper leaves the native reference law")
    _reject(
        "an ideal reset of a superposition", lambda: branches(parse_program(RESET_PHASE_PROBES["general"], 0), "ideal")
    )
    (minus,) = branches(parse_program(RESET_PHASE_PROBES["phase_minus"], 0), "qxelarator").values()
    plus = {qx_key(0, [0]): [math.sqrt(0.5), 0.0], qx_key(1, [1]): [math.sqrt(0.5), 0.0]}
    if abs(1.0 - state_fidelity(amplitudes_of(minus), plus)) > EXACT_TOL:
        raise AssertionError("the qxelarator reset model does not drop the |-> phase")
    (zero,) = branches(parse_program(RESET_PHASE_PROBES["already_zero"], 0), "qxelarator").values()
    (zero_ideal,) = branches(parse_program(RESET_PHASE_PROBES["already_zero"], 0), "ideal").values()
    if abs(1.0 - state_fidelity(amplitudes_of(zero), amplitudes_of(zero_ideal))) > EXACT_TOL:
        raise AssertionError("the qxelarator reset model changes a qubit with no weight on 1")
    # Synthetic QX records in QX key form: draws from the reference laws (deferred programs) and the reset
    # model (native program) pass; a flipped bit order, swapped clbits, moved shots and native draws from
    # the reference law each fail their check.
    generator = np.random.default_rng(BASE_SEED)
    seeds = 4

    def synthetic(native_law: list[float]) -> dict[str, Any]:
        samples: dict[str, list[dict[str, Any]]] = {}
        states: dict[str, Any] = {}
        programs = []
        for position, (name, form) in enumerate(forms.items()):
            law_ = native_law if form["form"] == "native" else reference[form["arm"]["member"]]
            if form["form"] == "deferred":
                amplitudes = {qx_key(value, form["readout"]): [math.sqrt(p), 0.0] for value, p in enumerate(law_)}
                states[name] = {"amplitudes": amplitudes}
            runs = []
            for n in range(seeds):
                draw = generator.multinomial(QX_SHOTS, law_)
                histogram = {qx_key(value, form["readout"]): int(c) for value, c in enumerate(draw) if c}
                runs.append({"seed": sample_seed(position, n), "counts": histogram})
            samples[name] = runs
            programs.append({"file": name, "member": form["arm"]["member"], "form": form["form"],
                             "readout": form["readout"]})  # fmt: skip
        return {
            "arms": [
                {"name": arm["name"], "member": arm["member"], "reference_law": reference[arm["member"]]}
                for arm in built["arms"]
            ],
            "programs": programs,
            "reset_model": {"native_law": {"ideal": ideal, "qxelarator": model}},
            "qx": {"shots": QX_SHOTS, "seeds": seeds, "states": states, "samples": samples},
        }

    record = synthetic(model)
    record["comparison"] = compare_qx(record)
    require_verdicts(record)

    def verdicts(mutated: dict[str, Any], reverse: bool = False) -> None:
        mutated["comparison"] = compare_qx(mutated, reverse)
        require_verdicts(mutated)

    _reject("QX keys read with qubit 0 leftmost", lambda: verdicts(copy.deepcopy(record), reverse=True))
    swapped = copy.deepcopy(record)
    for row in swapped["programs"]:
        row["readout"] = row["readout"][::-1]
    _reject("clbits 0 and 1 read from each other's qubits", lambda: verdicts(swapped))
    shifted = copy.deepcopy(record)
    counts = shifted["qx"]["samples"][feedback_name][0]["counts"]
    keys = sorted(counts)
    counts[keys[0]] -= 400
    counts[keys[-1]] += 400
    _reject("400 shots moved between outcomes", lambda: verdicts(shifted))
    flipped = copy.deepcopy(record)
    flipped["qx"]["states"][feedback_name]["amplitudes"] = {
        key[::-1]: amplitude for key, amplitude in record["qx"]["states"][feedback_name]["amplitudes"].items()
    }
    _reject("a QX state written with qubit 0 leftmost", lambda: verdicts(flipped))
    _reject(
        "native counts drawn from the reference law", lambda: verdicts(synthetic(reference[native["arm"]["member"]]))
    )
    if abs(record["comparison"]["reference_contrast"] - 0.25) > EXACT_TOL:
        raise AssertionError(f"reference contrast {record['comparison']['reference_contrast']} is not 1/4")
    radius = record["comparison"]["deferred_pair"]["radius"]
    print(
        "n21 QX conformance self-test: stopgap equals emit on grid; corrupted lines, dropped-control deferrals, "
        "a flipped bit order, swapped clbits, shifted shots and reference-law native counts rejected at radius "
        f"{radius:.5f}; reset models reproduce the dynamic_density law and the qxelarator phase drop"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--qx-worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--seeds", type=int, default=SEEDS, help="with --out: QX runs of QX_SHOTS per program")
    args = parser.parse_args()
    if args.qx_worker:
        return qx_worker()
    if args.self_test:
        self_test()
        return 0
    if args.out is not None:
        record = out(args.out, args.seeds)
    else:
        record = json.loads(args.check.read_text(encoding="utf-8"))
        try:
            verify(record, args.check.parent)
        except ValueError as error:
            raise SystemExit(f"{args.check}: {error}") from error
    comparison = record["comparison"]
    native = comparison["native_vs_reference"]
    print(
        "n21 QX conformance: exact max gaps "
        + ", ".join(f"{name} {row['max_gap']:.2e}" for name, row in comparison["exact"].items())
        + f"; exact contrast {comparison['exact_contrast']:.12f} (reference {comparison['reference_contrast']:.12f})"
        + f"; deferred pair {comparison['deferred_pair']['shots']} shots per arm, max gap "
        + f"{max(r['max_gap'] for r in comparison['deferred_pair']['circuits'].values()):.5f} within radius "
        + f"{comparison['deferred_pair']['radius']:.5f}; native reset arm refuted at max gap "
        + f"{max(r['max_gap'] for r in native['circuits'].values()):.5f}, reset model max gap "
        + f"{max(r['max_gap'] for r in comparison['native_vs_reset_model']['circuits'].values()):.5f}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
