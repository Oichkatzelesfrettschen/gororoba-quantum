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
ranks the mechanisms; with six degrees of freedom in the data, a mechanism
that lowers G2 by more than 3.84 per added parameter improves the fit at
alpha 0.05.

Usage: "$PYTHON" scripts/n21_orbit_rca.py RUN_DIR [--out FILE]
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import minimize

CONTROL, ONE, FOUR, SIXTEEN, RECORD = range(5)
WORK = (ONE, FOUR, SIXTEEN)
DIMENSION = 32
REGISTER = "g0_r0_phase"

_I = np.eye(2, dtype=complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_Z = np.diag([1.0, -1.0]).astype(complex)
_H = np.array([[1, 1], [1, -1]], dtype=complex) / math.sqrt(2)


def _embed(gate: np.ndarray, qubits: tuple[int, ...]) -> np.ndarray:
    """Full 32x32 operator for a gate on qubits (little-endian, qubit 0 least significant)."""
    count = len(qubits)
    full = np.zeros((DIMENSION, DIMENSION), dtype=complex)
    for column in range(DIMENSION):
        local_in = sum(((column >> qubit) & 1) << index for index, qubit in enumerate(qubits))
        rest = column
        for qubit in qubits:
            rest &= ~(1 << qubit)
        for local_out in range(1 << count):
            amplitude = gate[local_out, local_in]
            if amplitude == 0:
                continue
            row = rest | sum(((local_out >> index) & 1) << qubit for index, qubit in enumerate(qubits))
            full[row, column] += amplitude
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


def measured_pairs(run: Path) -> dict[str, dict[str, np.ndarray]]:
    """Counts per feed-forward pair, keyed by the member name without its arm suffix.

    PUB i carries the record's member i; the archived ISA confirms the order,
    since only the feed-forward member contains an if_else.
    """
    from qiskit import qpy

    collected = json.loads((run / "collect.json").read_text())
    (job,) = collected[0]["jobs"]
    members = [member["name"] for member in json.loads((run / "record.json").read_text())["groups"][0]["members"]]
    with (run / "isa.qpy").open("rb") as handle:
        circuits = qpy.load(handle)
    if len(circuits) != len(members):
        raise RuntimeError("archived circuits and record members differ in number")
    pairs: dict[str, dict[str, np.ndarray]] = {}
    for index, (name, circuit) in enumerate(zip(members, circuits, strict=True)):
        arm = "no_feedback" if name.endswith("_no_feedback") else "feedback"
        if ("if_else" in circuit.count_ops()) != (arm == "feedback"):
            raise RuntimeError(f"PUB {index} feed-forward structure differs from member {name}")
        payload = json.loads((run / "raw" / job / f"pub_{index:02d}.json").read_text())
        bits = payload["registers"][REGISTER]["bitstrings"]
        tally = Counter(int(value[1]) + 2 * int(value[0]) for value in bits)
        pairs.setdefault(name.removesuffix("_" + arm), {})[arm] = np.array(
            [tally[label] for label in range(4)], dtype=float
        )
    return pairs


def phase_interval(counts: dict[str, np.ndarray], readout: dict[str, float], best: dict[str, Any]) -> list[float]:
    """Profile-likelihood 95 percent interval of the work phase: deviance within 3.84 of its minimum."""
    names = [name for name, _low, _high in NUISANCE]
    bounds = [(low, high) for _name, low, high in NUISANCE]
    start = np.array([best["parameters"][name] for name in names])
    inside = []
    for phase in np.linspace(-math.pi, math.pi, 121):

        def objective(vector: np.ndarray, phase: float = float(phase)) -> float:
            return deviance(counts, readout | dict(zip(names, map(float, vector), strict=True)) | {"phase_one": phase})

        if minimize(objective, start, method="L-BFGS-B", bounds=bounds).fun <= best["deviance"] + 3.84:
            inside.append(float(phase))
    return [min(inside), max(inside)] if inside else []


def deviance(counts: dict[str, np.ndarray], params: dict[str, float]) -> float:
    total = 0.0
    for arm, feed_forward in (("feedback", True), ("no_feedback", False)):
        observed = counts[arm]
        expected = np.clip(distribution(params, feed_forward), 1e-12, None) * observed.sum()
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


def calibrated_readout(run: Path) -> dict[str, Any]:
    """Control-qubit assignment rates at the record's calibration.

    The physical control qubit is the first entry of the replica's initial
    layout. A record that retains placed_qubit_calibration supplies P(1|0) and
    P(0|1) directly; an older record falls back to IBM properties at its
    calibration timestamp.
    """
    from datetime import datetime, timedelta

    from qiskit_ibm_runtime import QiskitRuntimeService

    group = json.loads((run / "record.json").read_text())["groups"][0]
    (replica,) = group["replicas"]
    qubit = int(replica["initial_layout"][0])
    retained = group.get("placed_qubit_calibration", {}).get(str(qubit))
    if retained and {"prob_meas1_prep0", "prob_meas0_prep1"} <= retained.keys():
        return {
            "backend": group["backend"],
            "calibration": group["calibration"],
            "control_qubit": qubit,
            "prob_meas1_prep0": retained["prob_meas1_prep0"],
            "prob_meas0_prep1": retained["prob_meas0_prep1"],
        }
    stamp = datetime.fromisoformat(group["calibration"])
    backend = QiskitRuntimeService().backend(group["backend"])
    # A historical query returns the newest snapshot strictly before its
    # datetime, so the query asks one second past the recorded stamp; the
    # current snapshot serves when no later calibration has landed.
    candidates = (backend.properties(datetime=stamp + timedelta(seconds=1)), backend.properties())
    properties = next((item for item in candidates if item is not None and item.last_update_date == stamp), None)
    if properties is None:
        raise RuntimeError(f"{group['backend']} properties at {stamp} are unavailable; pass --readout")
    values = {item.name: float(item.value) for item in properties.qubits[qubit]}
    return {
        "backend": group["backend"],
        "calibration": group["calibration"],
        "control_qubit": qubit,
        "prob_meas1_prep0": values["prob_meas1_prep0"],
        "prob_meas0_prep1": values["prob_meas0_prep1"],
    }


MECHANISMS: dict[str, tuple[tuple[str, float, float], ...]] = {
    "baseline_depolarizing": (),
    "work_phase_one": (("phase_one", -math.pi, math.pi),),
    "work_phase_sixteen": (("phase_sixteen", -math.pi, math.pi),),
    "window_amplitude_damping": (("window_t1", 0.0, 1.0),),
    "window_dephasing": (("window_t2", 0.0, 1.0),),
    "reset_failure": (("reset_failure", 0.0, 1.0),),
    "control_phase": (("control_phase", -math.pi, math.pi),),
    "mid_readout_assignment": (("mid_e01", 0.0, 0.5), ("mid_e10", 0.0, 0.5)),
    "terminal_readout_assignment": (("end_e01", 0.0, 0.5), ("end_e10", 0.0, 0.5)),
}
NUISANCE = (("round1", 0.0, 1.0), ("round2", 0.0, 1.0))


def fit(
    counts: dict[str, np.ndarray], readout: dict[str, float], extra: tuple[tuple[str, float, float], ...]
) -> dict[str, Any]:
    names = [name for name, _low, _high in NUISANCE + extra]
    bounds = [(low, high) for _name, low, high in NUISANCE + extra]

    def objective(vector: np.ndarray) -> float:
        params = dict(readout)
        params.update(zip(names, (float(value) for value in vector), strict=True))
        return deviance(counts, params)

    best: Any = None
    starts = [[0.1, 0.1] + [(low + high) / 2 for _name, low, high in extra]]
    starts += [[0.2, 0.2] + [low + (high - low) * fraction for _name, low, high in extra] for fraction in (0.3, 0.7)]
    for start in starts:
        result = minimize(objective, np.array(start), method="L-BFGS-B", bounds=bounds)
        if best is None or result.fun < best.fun:
            best = result
    params = dict(zip(names, (float(value) for value in best.x), strict=True))
    full = dict(readout) | params
    return {
        "parameters": params,
        "deviance": float(best.fun),
        "added_parameters": len(extra),
        "feedback_law": distribution(full, True).tolist(),
        "no_feedback_law": distribution(full, False).tolist(),
    }


def _check_exact_laws() -> None:
    for feed_forward, exact in ((True, (3, 2, 1, 2)), (False, (3, 1, 1, 3))):
        law = distribution(_readout(0.0, 0.0), feed_forward)
        if not np.allclose(law, [value / 8 for value in exact], atol=1e-12):
            raise RuntimeError(f"noiseless model law {law} differs from the exact N=21 law")


def self_check() -> None:
    """Recover a known work phase from exact expected counts and reject the depolarizing baseline."""
    _check_exact_laws()
    readout = _readout(0.001, 0.006)
    truth = readout | {"round1": 0.1, "round2": 0.02, "phase_one": 0.5}
    counts = {
        arm: np.round(distribution(truth, feed_forward) * 4096)
        for arm, feed_forward in (("feedback", True), ("no_feedback", False))
    }
    phase = fit(counts, readout, MECHANISMS["work_phase_one"])
    baseline = fit(counts, readout, MECHANISMS["baseline_depolarizing"])
    if abs(phase["parameters"]["phase_one"] - 0.5) > 0.02 or phase["deviance"] > 0.05:
        raise RuntimeError(f"work-phase fit missed the planted phase: {phase['parameters']}")
    if baseline["deviance"] - phase["deviance"] < 3.84:
        raise RuntimeError("the depolarizing baseline fits a planted coherent phase")
    print("N=21 orbit RCA: exact laws, planted-phase recovery, and baseline rejection checks pass")


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
    arguments = parser.parse_args(argv)
    if arguments.self_check:
        self_check()
        return 0
    if arguments.run is None:
        parser.error("a run directory is required")
    _check_exact_laws()
    pairs = measured_pairs(arguments.run)
    if arguments.readout:
        source: dict[str, Any] = {
            "prob_meas1_prep0": arguments.readout[0],
            "prob_meas0_prep1": arguments.readout[1],
            "source": "--readout",
        }
    else:
        source = calibrated_readout(arguments.run) | {"source": "backend properties at the record calibration"}
    readout = _readout(source["prob_meas1_prep0"], source["prob_meas0_prep1"])
    report: dict[str, Any] = {"control_readout": source, "pairs": {}}
    for pair, counts in pairs.items():
        models = {name: fit(counts, readout, extra) for name, extra in MECHANISMS.items()}
        interval = phase_interval(counts, readout, models["work_phase_one"])
        report["pairs"][pair] = {
            "measured_counts": {arm: values.astype(int).tolist() for arm, values in counts.items()},
            "models": models,
            "work_phase_95_interval": interval,
        }
        baseline = models["baseline_depolarizing"]["deviance"]
        print(f"{pair}: work phase {models['work_phase_one']['parameters']['phase_one']:+.3f} rad, 95% {interval}")
        for name, model in sorted(models.items(), key=lambda item: item[1]["deviance"])[:4]:
            params = ", ".join(f"{key}={value:.4f}" for key, value in model["parameters"].items())
            gain = baseline - model["deviance"]
            print(f"  {name:30s} G2={model['deviance']:8.2f} gain={gain:7.2f} k+{model['added_parameters']}  {params}")
    if arguments.out:
        arguments.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
