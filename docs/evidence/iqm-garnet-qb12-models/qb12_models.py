"""Five QB12 fault models compared on the retained sedenion Walsh job of the Garnet follow-up.

The e_10 null arm (s10-id) is the identity for every static QB12 state: QB11 and QB17 each meet QB12 in two CZs, CZ
squared is the identity, and every other gate between their prx layers is diagonal or acts on another qubit. In the
retained job QB11 and QB17 still read 1 five to nine times more often in the shots where QB12 reads 1. This script
certifies the identity of both null arms, then fits five models of a QB12 fault to the job's twelve sedenion circuits
and sixteen readout preparations by multinomial likelihood. It reports each model's deviance against the saturated
fit, its Akaike and Bayesian criteria, and its prediction of the s10-id table of QB11 and QB17 given QB12. It decides
nothing: the comparison is descriptive, written after the analysis of the job.

Every model carries the calibration's depolarizing PRX and CZ error (iqm_sim.Calibration on the job's retained set)
and its herald-conditioned readout of QB11, QB17 and QB16. A CZ's two-qubit depolarizing error enters as the same
parameter on each of its qubits, a stated approximation. QB12 is a three-level system so that leakage can be
represented: a prx acts on its {0, 1} subspace and level 2 reads as 1. QB12's two readout errors are free in every
model.

- readout: QB12 readout alone.
- static: a QB12 excited population p that the zeros herald keeps.
- frequency: p, a detuning eta that tilts the axis of each QB12 prx toward Z, a QB12 phase phi after each of its CZs,
  and a conditional-phase error delta on its CZs.
- transition: p and a QB12 bit flip of probability q after each of its CZs.
- leakage: p, a transfer 1 -> 2 of probability l after each QB12 CZ, and the phase theta2 that a partner in 1 takes
  against QB12 in 2 under a CZ.

Starting points form a fixed grid, so the fit draws no random number.

Usage: "$PYTHON" docs/evidence/iqm-garnet-qb12-models/qb12_models.py OUT.json
"""

from __future__ import annotations

import itertools
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import minimize

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import iqm_sim  # noqa: E402

from parallel import ordered_map  # noqa: E402

RUN = ROOT / "results/iqm/runs/2026-11-21T220406Z-garnet-grover-depth-sedenion-walsh-sedenion"
QUBITS = ["QB11", "QB12", "QB17", "QB16"]
DIMS = [2, 3, 2, 2]
FAULT = 1
SIZE = math.prod(DIMS)
ARMS = ["s5-id", "s5-row", "s5-trunc", "s10-id", "s10-row", "s10-trunc"]
SPACE: dict[str, list[tuple[str, float, float]]] = {
    "readout": [],
    "static": [("p", 0.0, 0.6)],
    "frequency": [("p", 0.0, 0.6), ("eta", -1.5, 1.5), ("phi", -math.pi, math.pi), ("delta", -math.pi, math.pi)],
    "transition": [("p", 0.0, 0.6), ("q", 0.0, 0.5)],
    "leakage": [("p", 0.0, 0.6), ("l", 0.0, 0.5), ("theta2", -math.pi, math.pi)],
}
READOUT = [("e01", 0.0, 0.6), ("e10", 0.0, 0.6)]
ROUND = 4


def embed(matrix: np.ndarray, position: int) -> np.ndarray:
    blocks = [np.eye(d, dtype=complex) for d in DIMS]
    blocks[position] = matrix
    out = blocks[0]
    for block in blocks[1:]:
        out = np.kron(out, block)
    return out


def lift(matrix: np.ndarray, position: int) -> np.ndarray:
    """A two-level operator on the {0, 1} subspace, the identity on level 2 of QB12."""
    if DIMS[position] == 2:
        return matrix
    out = np.eye(3, dtype=complex)
    out[:2, :2] = matrix
    return out


PAULI = [np.array([[0, 1], [1, 0]], dtype=complex), np.array([[0, -1j], [1j, 0]]), np.diag([1.0 + 0j, -1.0])]
LEVELS = list(itertools.product(*(range(d) for d in DIMS)))


def rotation(theta: float, phase: float, eta: float = 0.0) -> np.ndarray:
    axis = np.array([math.cos(phase), math.sin(phase), eta])
    norm = float(np.linalg.norm(axis))
    angle = theta * norm
    generator = sum(a * s for a, s in zip(axis / norm, PAULI, strict=True))
    return math.cos(angle / 2) * np.eye(2) - 1j * math.sin(angle / 2) * generator


def cz_phases(a: int, b: int, delta: float, theta2: float) -> np.ndarray:
    phases = np.ones(SIZE, dtype=complex)
    for index, level in enumerate(LEVELS):
        x, y = level[a], level[b]
        if FAULT in (a, b):
            partner, fault = (x, y) if b == FAULT else (y, x)
            if partner == 1 and fault == 1:
                phases[index] = -np.exp(1j * delta)
            elif partner == 1 and fault == 2:
                phases[index] = np.exp(1j * theta2)
        elif x == 1 and y == 1:
            phases[index] = -1
    return phases


def depolarizing(p: float, position: int) -> list[np.ndarray]:
    return [math.sqrt(1 - 3 * p / 4) * np.eye(SIZE)] + [
        math.sqrt(p / 4) * embed(lift(s, position), position) for s in PAULI
    ]


def read_case() -> tuple[list[dict[str, Any]], iqm_sim.Calibration]:
    cases = json.loads((RUN / "cases.json").read_text(encoding="utf-8"))
    job = next(j for j in cases["jobs"] if j["job"] == "sedenion")
    shots = json.loads((RUN / "raw/measurements.json").read_text(encoding="utf-8"))
    if len(shots) != len(job["circuits"]):
        raise SystemExit("the retained shots do not match the circuits of the sedenion job")
    circuits = []
    for entry, record in zip(job["circuits"], shots, strict=True):
        circuit = json.loads((RUN / entry["file"]).read_text(encoding="utf-8"))
        locus = [op for op in circuit["instructions"] if op["name"] == "measure"][-1]["locus"]
        counts = np.zeros(16)
        for shot in record["m"]:
            bits = [b[0] if isinstance(b, list) else b for b in shot]
            counts[sum(bits[locus.index(q)] << k for k, q in enumerate(QUBITS))] += 1
        name = Path(entry["file"]).stem
        circuits.append({"name": name, "ops": circuit["instructions"], "counts": counts})
    return circuits, iqm_sim.Calibration.from_directory(RUN / "calibration")


def ideal_identity_error(ops: list[dict[str, Any]]) -> float:
    """max |U - I| of the noiseless circuit on the qubit subspace, up to a global phase."""
    unitary = np.eye(SIZE, dtype=complex)
    for op in ops:
        where = [QUBITS.index(q) for q in op["locus"]]
        if op["name"] == "prx":
            gate = embed(lift(rotation(op["args"]["angle"], op["args"]["phase"]), where[0]), where[0])
            unitary = gate @ unitary
        elif op["name"] == "cz":
            unitary = np.diag(cz_phases(where[0], where[1], 0.0, 0.0)) @ unitary
    keep = [i for i, level in enumerate(LEVELS) if level[FAULT] < 2]
    block = unitary[np.ix_(keep, keep)]
    block = block * np.conj(block[0, 0]) / abs(block[0, 0])
    return float(np.max(np.abs(block - np.eye(len(keep)))))


class Model:
    def __init__(self, kind: str, circuits: list[dict[str, Any]], calibration: iqm_sim.Calibration) -> None:
        self.kind = kind
        self.names = [n for n, _, _ in SPACE[kind] + READOUT]
        self.bounds = [(lo, hi) for _, lo, hi in SPACE[kind] + READOUT]
        self.circuits = circuits
        self.prx_noise = {q: depolarizing(calibration.prx_p(q), QUBITS.index(q)) for q in QUBITS}
        self.cz_p = {pair: 4 * (1 - f) / 3 for pair, f in calibration.cz.items()}
        self.readout = {q: calibration.readout(q, heralded=True) for q in QUBITS}
        self.positions = list(range(SIZE))

    def probabilities(self, values: dict[str, float], ops: list[dict[str, Any]]) -> np.ndarray:
        p = values.get("p", 0.0)
        rho = np.zeros((SIZE, SIZE), dtype=complex)
        for start, weight in ((0, 1 - p), (1, p)):
            index = LEVELS.index((0, start, 0, 0))
            rho[index, index] = weight
        for op in ops:
            where = [QUBITS.index(q) for q in op["locus"]]
            if op["name"] == "prx":
                eta = values.get("eta", 0.0) if where[0] == FAULT else 0.0
                gate = embed(lift(rotation(op["args"]["angle"], op["args"]["phase"], eta), where[0]), where[0])
                rho = gate @ rho @ gate.conj().T
                rho = sum(k @ rho @ k.conj().T for k in self.prx_noise[op["locus"][0]])
            elif op["name"] == "cz":
                phases = cz_phases(where[0], where[1], values.get("delta", 0.0), values.get("theta2", 0.0))
                rho = phases[:, None] * rho * phases.conj()[None, :]
                pp = self.cz_p[frozenset(op["locus"])]
                for position in where:
                    rho = sum(k @ rho @ k.conj().T for k in depolarizing(pp, position))
                if FAULT in where:
                    rho = self.fault_channel(values, rho)
        populations = np.real(np.diag(rho))
        out = np.zeros(16)
        for index, level in enumerate(LEVELS):
            out[sum(min(b, 1) << k for k, b in enumerate(level))] += populations[index]
        for k, qubit in enumerate(QUBITS):
            e01, e10 = (values["e01"], values["e10"]) if k == FAULT else self.readout[qubit]
            confusion = np.array([[1 - e01, e10], [e01, 1 - e10]])
            out = np.einsum("rt,atb->arb", confusion, out.reshape(2 ** (3 - k), 2, 2**k)).reshape(16)
        return np.clip(out, 1e-12, None)

    def fault_channel(self, values: dict[str, float], rho: np.ndarray) -> np.ndarray:
        if self.kind == "frequency":
            gate = embed(np.diag([1, np.exp(1j * values["phi"]), 1]), FAULT)
            return gate @ rho @ gate.conj().T
        if self.kind == "transition":
            q = values["q"]
            flip = embed(lift(PAULI[0], FAULT), FAULT)
            return (1 - q) * rho + q * flip @ rho @ flip.conj().T
        if self.kind == "leakage":
            keep = embed(np.diag([1, math.sqrt(1 - values["l"]), 1]), FAULT)
            jump = np.zeros((3, 3), dtype=complex)
            jump[2, 1] = math.sqrt(values["l"])
            leak = embed(jump, FAULT)
            return keep @ rho @ keep.conj().T + leak @ rho @ leak.conj().T
        return rho

    def loglik(self, vector: np.ndarray) -> float:
        values = dict(zip(self.names, vector, strict=True))
        return float(sum(c["counts"] @ np.log(self.probabilities(values, c["ops"])) for c in self.circuits))


def fit(item: tuple[str, tuple[float, ...]]) -> dict[str, Any]:
    kind, start = item
    model = Model(kind, *read_case())
    result = minimize(lambda v: -model.loglik(v), np.array(start), method="L-BFGS-B", bounds=model.bounds)
    return {"kind": kind, "loglik": -float(result.fun), "x": [float(v) for v in result.x]}


def starts(kind: str) -> list[tuple[str, tuple[float, ...]]]:
    grid = [(lo + (hi - lo) / 4, lo + 3 * (hi - lo) / 4) for _, lo, hi in SPACE[kind]]
    readout = (0.05, 0.25)
    return [(kind, point + readout) for point in itertools.product(*grid)]


def marginals(probabilities: np.ndarray) -> list[float]:
    total = probabilities.sum()
    return [round(float(sum(probabilities[i] for i in range(16) if (i >> k) & 1) / total), ROUND) for k in range(4)]


def table(probabilities: np.ndarray) -> dict[str, list[float]]:
    """P(QB11, QB17 = 00, 01, 10, 11 | QB12 = 0 or 1)."""
    out = {}
    for fault in (0, 1):
        cells = [probabilities[a | fault << 1 | b << 2] for a, b in ((0, 0), (0, 1), (1, 0), (1, 1))]
        out[f"qb12={fault}"] = [round(float(c / sum(cells)), ROUND) for c in cells]
    return out


def main(out: Path) -> None:
    circuits, calibration = read_case()
    identity = {c["name"]: ideal_identity_error(c["ops"]) for c in circuits if "-id-" in c["name"]}
    if max(identity.values()) > 1e-9:
        raise SystemExit(f"a null arm is not the identity: {identity}")
    saturated = float(
        sum(c["counts"][c["counts"] > 0] @ np.log(c["counts"][c["counts"] > 0] / c["counts"].sum()) for c in circuits)
    )
    shots = int(sum(c["counts"].sum() for c in circuits))
    cells = 15 * len(circuits)
    fits = ordered_map(fit, [s for kind in SPACE for s in starts(kind)])
    report: dict[str, Any] = {}
    for kind in SPACE:
        best = max((f for f in fits if f["kind"] == kind), key=lambda f: f["loglik"])
        model = Model(kind, circuits, calibration)
        values = dict(zip(model.names, best["x"], strict=True))
        k = len(model.names)
        predictions = {c["name"]: model.probabilities(values, c["ops"]) for c in circuits}
        report[kind] = {
            "parameters": {n: round(v, ROUND) for n, v in values.items()},
            "deviance": round(2 * (saturated - best["loglik"]), 1),
            "df": cells - k,
            "aic": round(2 * k - 2 * best["loglik"], 1),
            "bic": round(k * math.log(shots) - 2 * best["loglik"], 1),
            "marginals": {name: marginals(p) for name, p in predictions.items()},
            "s10_id_table": {name: table(p) for name, p in predictions.items() if name.startswith("s10-id")},
        }
    observed = {c["name"]: marginals(c["counts"]) for c in circuits}
    tables = {c["name"]: table(c["counts"]) for c in circuits if c["name"].startswith("s10-id")}
    record = {
        "run": str(RUN.relative_to(ROOT)),
        "qubits": QUBITS,
        "calibration_set": calibration.set_id,
        "null_arm_identity_error": {n: float(f"{v:.1e}") for n, v in sorted(identity.items())},
        "shots": shots,
        "circuits": [c["name"] for c in circuits],
        "observed": {"marginals": observed, "s10_id_table": tables},
        "models": report,
        "note": "descriptive comparison written after the analysis of the job; it decides nothing",
    }
    out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(Path(sys.argv[1]))
