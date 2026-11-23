"""Exact density-matrix model of the committed line-native Grover circuits, cut at iteration boundaries, and the
two-dimensional plane reduction of one noisy iteration.

Engine. A circuit of prx and cz gates on the three path qubits runs as a list of steps under scripts/iqm_sim.py's
noise: a depolarizing channel of parameter lam after every prx and cz (lam = 2 (1 - F) on one qubit and 4 (1 - F) / 3 on
two), and idle T1 and T2 relaxation over the ASAP schedule (prx 16 ns, cz 40 ns), the model of
iqm_grover_line.predicted. The channel of any run of steps is a 64 x 64 superoperator S acting on the row-major
vectorization of an 8 x 8 density matrix, so noise and the ideal unitary of the same steps stay side by side.

Plane. Let |m> be the marked basis state and |p> the uniform superposition of the other seven. The ideal Grover
iteration
G acts on span(|p>, |m>) as the Bloch rotation by 4 theta (sin theta = 1 / sqrt 8) about the y axis, and as -1 on the
six-dimensional complement. A plane block rho_P = (n I + x X + y Y + z Z) / 2 (basis p, m; z = rho_mm - rho_pp) has the
marked probability (n + z) / 2 and the maximally mixed state at n = 1/4, x = y = z = 0. The native circuit of k
iterations is cut after the 14 k-th cz (the cz of one iteration: two seven-cz CCZ networks); the cut state is
R_j |psi_j>, with psi_j the logical state after j iterations and R_j = U_native(through cut j) L_j^dagger a fixed
unitary
(L_j the logical unitary of Hadamards and j iterations), so Lambda_j = R_j^dagger S_j R_{j-1} is the noisy iteration
in the logical frame, equal to G when the noise is off.
"""

from __future__ import annotations

import cmath
import json
import math
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import numpy as np

PRX_NS = 16
CZ_NS = 40
CZ_PER_ITERATION = 14
THETA = math.asin(1 / math.sqrt(8))
PAULI = [
    np.eye(2, dtype=complex),
    np.array([[0, 1], [1, 0]], dtype=complex),
    np.array([[0, -1j], [1j, 0]], dtype=complex),
    np.array([[1, 0], [0, -1]], dtype=complex),
]


def prx_matrix(theta: float, phi: float) -> np.ndarray:
    c, s = math.cos(theta / 2), math.sin(theta / 2)
    return np.array([[c, -1j * cmath.exp(-1j * phi) * s], [-1j * cmath.exp(1j * phi) * s, c]])


def embed(ops: dict[int, np.ndarray]) -> np.ndarray:
    """The 8 x 8 operator with ops[p] on path position p (index bit p) and the identity elsewhere."""
    return np.kron(np.kron(ops.get(2, PAULI[0]), ops.get(1, PAULI[0])), ops.get(0, PAULI[0]))


def cz_signs(a: int, b: int) -> np.ndarray:
    return np.array([-1.0 if (i >> a) & (i >> b) & 1 else 1.0 for i in range(8)])


@dataclass(frozen=True)
class Step:
    """One gate with its depolarizing parameter, or one idle interval with its decay factors, in schedule order;
    part is the 1-based iteration cut the step belongs to (the tail after the last cut has part k + 1); end is the
    step's end time in ns on the ASAP schedule."""

    kind: str
    qubits: tuple[int, ...]
    part: int
    lam: float = 0.0
    angle: float = 0.0
    phase: float = 0.0
    population: float = 1.0
    coherence: float = 1.0
    phase_error: float = 0.0
    ns: int = 0
    zz: float = 0.0
    end: int = 0


def build_steps(
    circuit: dict[str, Any], calibration: Any, path: list[str], noisy: bool = True
) -> tuple[list[Step], list[int]]:
    """The circuit's steps under the model of iqm_grover_line.predicted (noisy) or the bare gates (not noisy), and the
    path position each measured bit reads."""
    clock = [0, 0, 0]
    cz_done = 0
    steps: list[Step] = []
    measured: list[int] = []

    def idle(p: int, until: int) -> None:
        if noisy and until > clock[p]:
            seconds = (until - clock[p]) * 1e-9
            t1 = calibration.values[f"characterization.model.{path[p]}.t1_time"]
            t2 = min(calibration.values[f"characterization.model.{path[p]}.t2_time"], 2 * t1)
            steps.append(
                Step(
                    "idle",
                    (p,),
                    cz_done // CZ_PER_ITERATION + 1,
                    population=math.exp(-seconds / t1),
                    coherence=math.exp(-seconds / t2),
                    ns=until - clock[p],
                    end=until,
                )
            )
        clock[p] = until

    for op in circuit["instructions"]:
        where = [path.index(q) for q in op["locus"]]
        part = cz_done // CZ_PER_ITERATION + 1
        if op["name"] == "prx":
            lam = calibration.prx_p(op["locus"][0]) if noisy else 0.0
            steps.append(
                Step(
                    "prx",
                    (where[0],),
                    part,
                    lam=lam,
                    angle=op["args"]["angle"],
                    phase=op["args"]["phase"],
                    ns=PRX_NS,
                    end=clock[where[0]] + PRX_NS,
                )
            )
            clock[where[0]] += PRX_NS
        elif op["name"] == "cz":
            start = max(clock[w] for w in where)
            for w in where:
                idle(w, start)
            lam = 4 * (1 - calibration.cz[frozenset(op["locus"])]) / 3 if noisy else 0.0
            steps.append(Step("cz", (where[0], where[1]), part, lam=lam, ns=CZ_NS, end=start + CZ_NS))
            for w in where:
                clock[w] = start + CZ_NS
            cz_done += 1
        elif op["name"] == "measure":
            measured = where
    end = max(clock)
    for p in range(3):
        idle(p, end)
    return steps, measured


def with_coherent_error(
    steps: list[Step], cz_phase: float = 0.0, prx_scale: float = 0.0, zz_hz: float = 0.0
) -> list[Step]:
    """The steps with every cz applying the conditional phase pi + cz_phase, every prx rotating by angle
    (1 + prx_scale) and the two path couplers carrying the always-on |11><11| phase of rotating-frame ZZ coupling
    zz_hz (cycles per second) over the elapsed time of the ASAP schedule. Gates of different qubits overlap in time,
    so each step carries the ZZ phase of the schedule time its end adds beyond every earlier step's end (the
    non-overlapping interval it closes, an idle gap included): the phases of all steps sum to the schedule length times
    2 pi zz_hz, and three parallel 16 ns gates accrue 16 ns."""
    out = []
    frontier = 0
    for s in steps:
        elapsed = max(s.end - frontier, 0)
        frontier = max(frontier, s.end)
        zz = 2 * math.pi * zz_hz * elapsed * 1e-9
        if s.kind == "cz":
            out.append(replace(s, phase_error=cz_phase, zz=zz))
        elif s.kind == "prx":
            out.append(replace(s, angle=s.angle * (1 + prx_scale), zz=zz))
        else:
            out.append(replace(s, zz=zz))
    return out


def paulis_on(qubits: tuple[int, ...]) -> list[np.ndarray]:
    out = [np.eye(8, dtype=complex)]
    for q in qubits:
        out = [embed({q: P}) @ o for o in out for P in PAULI]
    return out


def depolarize(rho: np.ndarray, qubits: tuple[int, ...], lam: float) -> np.ndarray:
    if lam == 0.0:
        return rho
    mixed = sum(P @ rho @ P.conj().T for P in paulis_on(qubits)) / 4 ** len(qubits)
    return (1 - lam) * rho + lam * mixed


def relax(rho: np.ndarray, p: int, population: float, coherence: float) -> np.ndarray:
    view = rho.reshape(-1, 2, 2, 2, 2, 2, 2)
    row, col = 3 - p, 6 - p

    def at(r: int, c: int) -> tuple[Any, ...]:
        index: list[Any] = [slice(None)] * 7
        index[row], index[col] = r, c
        return tuple(index)

    out = view.copy()
    out[at(0, 0)] = view[at(0, 0)] + (1 - population) * view[at(1, 1)]
    out[at(1, 1)] = population * view[at(1, 1)]
    out[at(0, 1)] = coherence * view[at(0, 1)]
    out[at(1, 0)] = coherence * view[at(1, 0)]
    return out.reshape(rho.shape)


def zz_phase(rho: np.ndarray, phase: float) -> np.ndarray:
    """rho under diag(exp(-i phase n_a n_b)) on the couplers (0, 1) and (1, 2)."""
    index = np.arange(8)
    n = [(index >> p) & 1 for p in range(3)]
    d = np.exp(-1j * phase * (n[0] * n[1] + n[1] * n[2]))
    return rho * np.outer(d, d.conj())


def unitary_of(step: Step) -> np.ndarray | None:
    if step.kind == "prx":
        return embed({step.qubits[0]: prx_matrix(step.angle, step.phase)})
    if step.kind == "cz":
        signs = cz_signs(*step.qubits).astype(complex)
        both = signs < 0
        signs[both] = -cmath.exp(1j * step.phase_error)
        return np.diag(signs)
    return None


def apply_steps(steps: list[Step], rho: np.ndarray) -> np.ndarray:
    """A batch (B, 8, 8) of density matrices through the noisy steps."""
    for step in steps:
        if step.kind == "idle":
            rho = relax(rho, step.qubits[0], step.population, step.coherence)
            if step.zz:
                rho = zz_phase(rho, step.zz)
            continue
        u = unitary_of(step)
        if u is None:
            raise ValueError(f"step kind {step.kind} has no unitary")
        rho = u @ rho @ u.conj().T
        rho = depolarize(rho, step.qubits, step.lam)
        if step.zz:
            rho = zz_phase(rho, step.zz)
    return rho


def superoperator(steps: list[Step]) -> np.ndarray:
    """The 64 x 64 matrix S with vec(out) = S vec(in), vec row-major."""
    basis = np.zeros((64, 8, 8), dtype=complex)
    for i in range(8):
        for j in range(8):
            basis[i * 8 + j, i, j] = 1
    return apply_steps(steps, basis).reshape(64, 64).T


def ideal_unitary(steps: list[Step]) -> np.ndarray:
    u = np.eye(8, dtype=complex)
    for step in steps:
        g = unitary_of(step)
        if g is not None:
            u = g @ u
    return u


def conjugation(u: np.ndarray) -> np.ndarray:
    """The superoperator rho -> u rho u^dagger."""
    return np.kron(u, u.conj())


def outcome_distribution(
    rho: np.ndarray, measured: list[int], path: list[str], calibration: Any, readout: bool = True
) -> np.ndarray:
    """Outcome probabilities (index sum(bit_q << q), bit q from the q-th measured qubit), through the
    herald-conditioned readout of each measured qubit unless readout is False (the state's own distribution)."""
    diagonal = np.real(np.diag(rho))
    read = np.zeros(8)
    for i in range(8):
        read[sum(((i >> p) & 1) << q for q, p in enumerate(measured))] += diagonal[i]
    for q, p in enumerate(measured if readout else []):
        e01, e10 = calibration.readout(path[p], heralded=True)
        confusion = np.array([[1 - e01, e10], [e01, 1 - e10]])
        read = np.einsum("rt,atb->arb", confusion, read.reshape(2 ** (2 - q), 2, 2**q)).reshape(8)
    return read


def cuts(steps: list[Step], k: int) -> list[list[Step]]:
    """The k iteration cuts followed by the tail."""
    return [[s for s in steps if s.part == j] for j in range(1, k + 2)]


def logical_frame(
    circuit: dict[str, Any],
    calibration: Any,
    path: list[str],
    marked: str,
    k: int,
    noisy: bool = True,
    cz_phase: float = 0.0,
    prx_scale: float = 0.0,
    zz_hz: float = 0.0,
) -> dict[str, Any]:
    """The cut superoperators, the logical-frame iteration channels Lambda_1 .. Lambda_k, the tail with the
    final unitary and the measured positions of a k-iteration circuit."""
    import iqm_grover_line as grover

    steps, measured = build_steps(circuit, calibration, path, noisy)
    if any(s.part > k + 1 for s in steps):
        raise ValueError(f"{circuit['name']}: more than {k} iterations of {CZ_PER_ITERATION} cz")
    reference = cuts(steps, k)
    parts = cuts(with_coherent_error(steps, cz_phase, prx_scale, zz_hz), k)
    logical = [grover.logical_unitary(grover.grover_ops(marked, j)) for j in range(k + 1)]
    native = [np.eye(8, dtype=complex)]
    for j in range(1, k + 1):
        native.append(ideal_unitary(reference[j - 1]) @ native[-1])
    frames = [native[j] @ logical[j].conj().T for j in range(k + 1)]
    lam = []
    for j in range(1, k + 1):
        s = superoperator(parts[j - 1])
        lam.append(conjugation(frames[j].conj().T) @ s @ conjugation(frames[j - 1]))
    return {
        "steps": steps,
        "parts": parts,
        "measured": measured,
        "frames": frames,
        "lambda": lam,
        "tail": superoperator(parts[k]),
        "tail_unitary": ideal_unitary(parts[k]),
    }


def plane_vectors(marked_index: int) -> tuple[np.ndarray, np.ndarray]:
    m = np.zeros(8, dtype=complex)
    m[marked_index] = 1
    p = np.ones(8, dtype=complex)
    p[marked_index] = 0
    return p / math.sqrt(7), m


def coords(op: np.ndarray, marked_index: int) -> np.ndarray:
    """(n, x, y, z) of the plane block of an 8 x 8 operator."""
    p, m = plane_vectors(marked_index)
    pp, mm, pm = (p.conj() @ op @ p).real, (m.conj() @ op @ m).real, p.conj() @ op @ m
    return np.array([pp + mm, 2 * pm.real, -2 * pm.imag, mm - pp])


def plane_operators(marked_index: int) -> tuple[list[np.ndarray], np.ndarray]:
    """The plane basis operators B_n, B_x, B_y, B_z (coords = unit vectors) and the normalized complement I_c / 6."""
    p, m = plane_vectors(marked_index)
    pp, mm = np.outer(p, p.conj()), np.outer(m, m.conj())
    pm, mp = np.outer(p, m.conj()), np.outer(m, p.conj())
    basis = [(pp + mm) / 2, (pm + mp) / 2, (-1j * pm + 1j * mp) / 2, (mm - pp) / 2]
    return basis, (np.eye(8) - pp - mm) / 6


def vec(op: np.ndarray) -> np.ndarray:
    return op.reshape(64)


def unvec(v: np.ndarray) -> np.ndarray:
    return v.reshape(8, 8)


def plane_map(channel: np.ndarray, marked_index: int) -> tuple[np.ndarray, np.ndarray]:
    """The affine plane map of one logical-frame channel: v' = M v + w (1 - n), M the 4 x 4 matrix of the plane
    block of the images of the plane basis operators, w the plane block of the image of the normalized
    complement (the first-order closure: the complement holds the leaked weight as the uniform state)."""
    basis, complement = plane_operators(marked_index)
    m = np.column_stack([coords(unvec(channel @ vec(b)), marked_index) for b in basis])
    w = coords(unvec(channel @ vec(complement)), marked_index)
    return m, w


def initial_vector() -> np.ndarray:
    """The plane vector of |s> = cos(theta) |p> + sin(theta) |m>."""
    return np.array([1.0, math.sin(2 * THETA), 0.0, -math.cos(2 * THETA)])


def step_affine(m: np.ndarray, w: np.ndarray, v: np.ndarray) -> np.ndarray:
    return m @ v + w * (1 - v[0])


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def plane_rotation_unitary(eps: float, marked_index: int) -> np.ndarray:
    """The unitary that rotates the plane by Bloch angle eps toward |m> and fixes the complement."""
    p, m = plane_vectors(marked_index)
    pp, mm = np.outer(p, p.conj()), np.outer(m, m.conj())
    return np.asarray(
        math.cos(eps / 2) * (pp + mm)
        + math.sin(eps / 2) * (np.outer(m, p.conj()) - np.outer(p, m.conj()))
        + np.eye(8)
        - pp
        - mm
    )


def plane_rotation(eps: float, marked_index: int) -> np.ndarray:
    """The 64 x 64 superoperator of plane_rotation_unitary."""
    return conjugation(plane_rotation_unitary(eps, marked_index))


def global_depolarizing(s: float) -> np.ndarray:
    """rho -> s rho + (1 - s) tr(rho) I / 8 as a 64 x 64 superoperator (s above 1 is the formal continuation)."""
    trace = np.eye(8).reshape(1, 64)
    return s * np.eye(64) + (1 - s) / 8 * (np.eye(8).reshape(64, 1) @ trace)


def marked_functional(
    measured: list[int], path: list[str], calibration: Any, marked_index: int, readout: bool
) -> np.ndarray:
    """The row vector f with P(marked outcome) = f . vec(final native state)."""
    f = np.zeros(64)
    for i in range(8):
        basis = np.zeros((8, 8), dtype=complex)
        basis[i, i] = 1
        f[i * 8 + i] = outcome_distribution(basis, measured, path, calibration, readout)[marked_index]
    return f


class Response:
    """The marked probability of every depth k <= K under the calibrated noisy path of the committed circuits and the
    excess channels of the plane family: before the first iteration nothing, after each iteration a rotation
    eps of the plane and a global depolarizing factor s, and at the end the depth-independent factor a on the
    probability above 1/8:  P_k = 1/8 + a (Q_k(s, eps) - 1/8). The circuits give the channels, so a change of the
    builder cannot change what the analysis reads."""

    def __init__(
        self,
        circuits: dict[int, dict[str, Any]],
        calibration: Any,
        path: list[str],
        marked: str,
        readout: bool = True,
        cz_phase: float = 0.0,
        prx_scale: float = 0.0,
        zz_hz: float = 0.0,
        noisy: bool = True,
    ) -> None:
        self.depths = sorted(circuits)
        top = self.depths[-1]
        self.index = sum(int(c) << q for q, c in enumerate(marked))
        frames = {}
        for k in self.depths:
            frames[k] = logical_frame_of(circuits[k], calibration, path, marked, k, noisy, cz_phase, prx_scale, zz_hz)
        self.lambdas = frames[top]["lambda"]
        start = frames[top]["frames"][0]
        self.start = vec(start.conj().T @ np.diag([1.0] + [0.0] * 7).astype(complex) @ start)
        self.readers = {}
        for k in self.depths:
            f = marked_functional(frames[k]["measured"], path, calibration, self.index, readout)
            self.readers[k] = f @ frames[k]["tail"] @ conjugation(frames[k]["frames"][k])

    def centered(self, s: float, eps: float) -> np.ndarray:
        """Q_k(s, eps) - 1/8 for every depth."""
        u = plane_rotation_unitary(eps, self.index)
        ud = u.conj().T
        rho = self.start
        out = []
        for j, lam in enumerate(self.lambdas, start=1):
            r = (lam @ rho).reshape(8, 8)
            r = u @ r @ ud
            r = s * r + ((1 - s) * np.trace(r) / 8) * np.eye(8)
            rho = r.reshape(64)
            if j in self.readers:
                out.append(float(np.real(self.readers[j] @ rho)) - 1 / 8)
        return np.array(out)

    def probabilities(self, a: float, s: float, eps: float) -> np.ndarray:
        return 1 / 8 + a * self.centered(s, eps)


def logical_frame_of(
    circuit: dict[str, Any],
    calibration: Any,
    path: list[str],
    marked: str,
    k: int,
    noisy: bool,
    cz_phase: float,
    prx_scale: float,
    zz_hz: float,
) -> dict[str, Any]:
    return logical_frame(circuit, calibration, path, marked, k, noisy, cz_phase, prx_scale, zz_hz)
