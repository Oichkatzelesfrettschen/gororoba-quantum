"""Fringe amplitude ratios of the Fez and Kingston ripple atlas edges: structure against shot noise, and its predictors.

The runs, lanes, executed replicas and per-edge observations are those of
scripts/atlas_coherent_families.py: 84 box-kite edges, each an 8-point phase
sweep phi_k = k pi/4, on 7 lanes of 5 physical qubits, from ibm_fez
results/live/2026-10-13T025444.603480Z and ibm_kingston
results/live/2026-10-15T031229.371738Z. An edge whose 8 points ran under more
than one calibration is excluded and listed, as there.

Observable. Each edge's 8 zero-outcome probabilities p_k fit by least
squares to a + c cos phi_k + s sin phi_k; the fringe contrast is
b = sqrt(c^2 + s^2). The amplitude ratio of an edge is R = b_hw / b_replay and
the fitted quantity its logarithm y = log R
(atlas_coherent_families.observables), where b_replay is the contrast of the
calibration-bound execution replay: NoiseModel.from_backend under the
calibration the edge ran under, every gate with its reported depolarizing
error and thermal relaxation over its duration, and each qubit's asymmetric
readout channel. The ideal contrast is 1/2 on every edge, so log(2 b_hw) is
the total loss and y the part of it the calibrated channels leave
unexplained. The structure statistics are reported for both normalizations;
the replay one carries the comparison because the replay's own loss
log(2 b_replay) differs between edges by more than the shot noise, and the
``replay_loss`` model tests whether the hardware loss follows it.

Noise. live_run samples the replay at the run's own shots, so both contrasts
carry binomial noise. c and s are linear in the points (rows of the fit's
pseudo-inverse), so var(log b) = sum_k (c dc/dp_k + s ds/dp_k)^2 / b^4 *
p_k (1 - p_k) / n_k, per point shots n_k, and sigma_y^2 = sigma_hw^2 +
sigma_replay^2. The estimator log b-hat is biased upward by about
(sigma_c^2 + sigma_s^2) / (2 b^2) <= 4e-4 at b >= 0.3 and 1024 shots, below
2 percent of sigma_y. Every lane checks the propagated sigma against a
parametric bootstrap: BOOTSTRAP binomial draws of each hardware and replay
point at its probability and shots, refitted.

Structure. Per lane, with w = 1 / sigma^2: the weighted mean, Q = sum w (y -
ybar)^2 against chi-square with n - 1 degrees of freedom and its upper tail
p-value, and the excess scatter tau^2 = max(0, (Q - (n - 1)) / (sum w - sum
w^2 / sum w)), the DerSimonian-Laird estimate of the edge-to-edge spread
shot noise does not explain. The structure block covers every lane of the
selected runs; it reads only recorded probabilities.

Predictors, each a column over the lane's edges, computed on the executed
replica by exact 5-qubit density-matrix evolution in circuit order (every
qubit's own pulses keep their executed order; operations on other qubits
commute with a channel on q):

- ``idle_relaxation``: the replay simulates the ISA circuit, which carries
  no delay, so a qubit waiting between its pulses stays ideal there. The
  executed schedule (scheduler_timing play rows, start and duration in dt)
  gives every gap between the end of one pulse on q and the start of the
  next, and for the measured qubit the gap to its measurement. The column is
  log(b / b0) with zero-temperature thermal relaxation over each gap at the
  snapshot T1 and T2 (T2 capped at 2 T1, as NoiseModel.from_backend does),
  where b0 is the noiseless contrast. A qubit that waits in |0> loses
  nothing. The column is a parameter-free prediction: ``idle_relaxation``
  at coefficient 1 is the loss the replay omits. The reported T2 comes from
  a Hahn echo (docs/notes/ibm_quantum/qpu-information.md), and these runs
  execute with dynamical decoupling and twirling off, so a free idle gap
  dephases at the Ramsey rate, at least the echo rate; a coefficient above 1
  is the expected direction. ``idle_amplitude_damping`` (T1 alone, coherence
  exp(-t/2T1)) and ``idle_dephasing`` (pure dephasing at 1/T2 - 1/2T1 alone)
  split the column.
- ``cz_depolarizing``: log(b / b0) with one depolarizing channel after each
  executed CZ at lambda = (4/3) r_c, the two-qubit depolarizing parameter
  whose average infidelity 3 lambda / 4 equals the reported CZ error r_c. A
  coefficient kappa is the CZ factor c - 1 of a run whose CZ errors are c
  times the reported ones, to the extent log b is linear in lambda.
- ``sx_depolarizing``: the same after each sx and x at lambda = 2 r_q, the
  single-qubit parameter with infidelity lambda / 2.
- ``readout``: log((1 - 2E) / (1 - E)), E = e01 + e10 of the measured qubit:
  the contrast change when every readout flip doubles.
- ``replay_loss``: log(2 b_replay), the replay's own loss; y = beta L means
  every calibrated channel scaled by 1 + beta. L carries the replay's shot
  noise, which enters the residual as (1 + beta) times sigma_replay; the
  least-squares beta is attenuated by it.
- ``measured_qubit``: one constant per measured physical qubit.
- a lane constant: a per-lane depolarizing factor, uniform over the edges.

Coherent families. The ideal fringe has the maximal contrast 1/2, so every
coherent error lowers log b at second order:
y_e = a + sum_j K_ej theta_j^2 with K the log-contrast curvature
atlas_coherent_families.lane_fit computes from +-h shifts of each column.
With u_j = theta_j^2 >= 0 the model is linear and fits by bounded least
squares (scipy.optimize.lsq_linear, method bvls) for detuning, cz_phase, zz,
zz_symmetric, sx_amplitude and axis_tilt, each with a lane constant. The fit
fixes magnitudes only; every sign pattern of the active columns is then
resimulated on every edge, which gives the contrast without the diagonal
second-order approximation and the phase shift those magnitudes imply.

Scoring. Every model fits by least squares and scores by leave-one-edge-out
RMS against its leave-one-out noise floor, the RMS over held-out edges of the
held-out variance plus the prediction's variance propagated linearly from
the training edges, exactly as atlas_coherent_families scores phases; a
bounded fit propagates through its active columns. Rank (singular values
above 1e-6 of the largest) and condition are reported for the full design
and every fold, each column scaled to unit norm so that columns in kHz^2,
rad^2 and the unit constant compare by collinearity; a model is unidentified
when its design or any fold falls short of full numerical rank or a fold
trains on no more edges than the model has columns. The predicted idle
relaxation also scores with no fitted parameter (``idle_relaxation_predicted``,
residual y - Lambda) and with a held-out constant. Several models per lane
are compared, so the lowest score is an exploratory selection. The idle
split and the two-column idle + CZ models stand outside the falsifiers
below and are exploratory; a fitted coefficient outside the physical domain
(below -1, a negative error rate) marks collinearity between the columns,
not a model.

Replay omission check. The replay's loss log(2 b_replay) is compared per
edge with the loss of the calibrated channels alone, cz_depolarizing +
sx_depolarizing + log(1 - E), each gate's whole reported error taken as
depolarizing and E the readout contrast factor. If the replay charged idle
relaxation, the difference would sit near Lambda on every edge; the
chi-square of the difference against sigma_replay is reported under both
readings (``replay_channel_check``).

Falsifiers, fixed before any fit ran:

- the shot-noise floor is refuted on a lane when the bootstrap standard
  deviation of y differs from the propagated sigma by more than 10 percent
  on any edge;
- a lane's ratios are consistent with a lane constant when Q lies at or
  below the 99th percentile of chi-square with n - 1 degrees of freedom
  (p >= 0.01); the model step then reduces to reporting that constant;
- a model other than the lane constant (the baseline, which carries no flag)
  is refuted on a lane when its leave-one-out RMS is at or above the
  lane constant's, and accounts for the structure when its leave-one-out RMS
  is at most 1.5 times its own floor;
- the parameter-free idle prediction is refuted when the chi-square of
  y - Lambda over n edges exceeds its 99th percentile, and its edge structure
  is refuted when y - Lambda about its mean exceeds the 99th percentile with
  n - 1 degrees of freedom;
- a coherent amplitude fit is inconsistent with the calibration when a fitted
  magnitude exceeds its gate-error bound (atlas_coherent_families.gate_bounds),
  and a bounded family cannot account for the structure when its contrast
  reach at the bound is below the lane's excess scatter tau;
- a coherent amplitude fit is refuted by the phase when, at its best sign
  pattern, the resimulated phase shifts leave a residual (lane constant
  removed) at or above the RMS of the measured offsets about their lane
  mean;
- the diagonal second-order model fails at the fitted magnitudes when the
  resimulated log contrast at any sign pattern differs from K u by more than
  the lane's contrast shot-noise RMS; its linear score is then no test of
  the family.

Self-checks in every lane: the noiseless density-matrix probability of every
point equals atlas_coherent_families.probability within 1e-12, and the
executed pulse starts paired here equal those of
atlas_coherent_families.timed_replica.

``--runs`` and ``--lanes`` (default 4, or ``all``) select the fitted lanes.
Edges are simulated through parallel.ordered_map (GOROROBA_WORKERS caps the
pool). ``--self-test`` checks the thermal and depolarizing channels against
qiskit_aer.noise on a random two-qubit state, the noiseless density matrix
against the statevector on Fez lane 4, the bootstrap against the propagated
sigma, and recovers planted cases on Fez lane 4 through the model step:
synthetic counts at a lane-constant ratio pass the structure test, a planted
2 x idle relaxation is flagged and recovered, and planted sx_amplitude
magnitudes resimulated through the replicas are recovered from their
contrast. ``--check FILE`` requires every file FILE names to hold its
sha256, reruns its lanes (or the ``--runs``/``--lanes`` subset), requires the
rerun to read only named files, and requires every number to agree as
atlas_coherent_families --check requires.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import atlas_coherent_families as acf  # noqa: E402
import atlas_detuning_map as atlas  # noqa: E402
import numpy as np  # noqa: E402
from qiskit import QuantumCircuit  # noqa: E402
from qiskit.quantum_info import Operator  # noqa: E402
from scipy import optimize, stats  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "atlas-fringe-amplitudes-v1"
PHASES = acf.PHASES
BOOTSTRAP = 2000
BOOTSTRAP_SEED = 20261016
BOOTSTRAP_RTOL = 0.1
STRUCTURE_P = 0.01
ACCOUNTS_FACTOR = 1.5
DENSITY_TOLERANCE = 1e-12
ACTIVE = 1e-12
CZ_DEPOLARIZING = 4.0 / 3.0
SQ_DEPOLARIZING = 2.0
COHERENT = acf.SINGLE
COLUMNS = ("idle_relaxation", "cz_depolarizing", "sx_depolarizing", "readout", "replay_loss")
IDLE_PARTS = {"idle": "both", "damping": "damping", "dephasing": "dephasing"}
# Density-matrix variant -> the log-contrast column it gives.
VARIANTS = (
    ("idle", "idle_relaxation"),
    ("damping", "idle_amplitude_damping"),
    ("dephasing", "idle_dephasing"),
    ("cz", "cz_depolarizing"),
    ("sx", "sx_depolarizing"),
)
# Linear models: name -> (predictor columns, lane constant). measured_qubit
# carries one indicator per measured qubit and no separate constant.
LINEAR: dict[str, tuple[tuple[str, ...], bool]] = {
    "lane_constant": ((), True),
    "measured_qubit": (("measured_qubit",), False),
    **{name: ((name,), False) for name in COLUMNS},
    **{f"{name}_plus_constant": ((name,), True) for name in COLUMNS},
    "idle_amplitude_damping_and_dephasing": (("idle_amplitude_damping", "idle_dephasing"), False),
    "idle_amplitude_damping_and_dephasing_plus_constant": (("idle_amplitude_damping", "idle_dephasing"), True),
    "idle_relaxation_and_cz_depolarizing": (("idle_relaxation", "cz_depolarizing"), False),
    "idle_relaxation_and_cz_depolarizing_plus_constant": (("idle_relaxation", "cz_depolarizing"), True),
}
# A schedule: the Timed replica, each compact instruction's executed end in
# seconds (nan for virtual gates), and per compact instruction the idle gaps
# (qubit, seconds) that follow it on its qubits.
Schedule = tuple[acf.Timed, list[float], dict[int, list[tuple[int, float]]]]
require = acf.require


def schedule(circuit: QuantumCircuit, rows: list[list[str]], dt: float) -> Schedule:
    """The executed replica with each pulse's end and the idle gap after it on each of its qubits.

    Each qubit's play rows, in start order, pair with its non-virtual
    instructions as atlas_coherent_families.timed_replica pairs them; the
    rows that remain on the measured qubit are its measurement, which starts
    at the first of them.
    """
    timed = acf.timed_replica(circuit, rows, dt)
    compact, starts, _, measured, active = timed
    plays: dict[int, list[tuple[int, int, str]]] = defaultdict(list)
    for row in rows:
        if row[5] != "play" or row[1].startswith(("INIT", "FINI")) or not row[2].startswith("Qubit "):
            continue
        qubit = int(row[2].split()[1])
        if qubit in active:
            plays[qubit].append((int(row[3]), int(row[4]), row[1].split("_")[0]))
    for qubit in plays:
        plays[qubit].sort()
    cursor: dict[int, int] = defaultdict(int)
    ends: list[float] = []
    pulses: dict[int, list[tuple[int, float, float]]] = defaultdict(list)
    for k, inst in enumerate(compact.data):
        if math.isnan(starts[k]):
            ends.append(math.nan)
            continue
        qubits = [compact.find_bit(q).index for q in inst.qubits]
        edges = set()
        for q in qubits:
            start, duration, label = plays[active[q]][cursor[active[q]]]
            cursor[active[q]] += 1
            require(
                label == inst.operation.name, f"qubit {active[q]}: {label} where the replica has {inst.operation.name}"
            )
            require(start * dt == starts[k], f"qubit {active[q]}: start {start * dt} against {starts[k]}")
            edges.add((start + duration) * dt)
        require(len(edges) == 1, f"{inst.operation.name} on {qubits} ends at different times {edges}")
        ends.append(edges.pop())
        for q in qubits:
            pulses[q].append((k, starts[k], ends[k]))
    remaining = plays[active[measured]][cursor[active[measured]] :]
    require(bool(remaining) and all(label == "measure" for _, _, label in remaining), "the measurement is not last")
    for qubit in active:
        if qubit != active[measured]:
            require(cursor[qubit] == len(plays[qubit]), f"qubit {qubit}: executed pulses remain unpaired")
    gaps: dict[int, list[tuple[int, float]]] = defaultdict(list)
    for q, sequence in pulses.items():
        following = [start for _, start, _ in sequence[1:]]
        if q == measured:
            following.append(remaining[0][0] * dt)
        for (k, _, end), next_start in zip(sequence, following, strict=False):
            gap = next_start - end
            require(gap > -1e-15, f"qubit {active[q]}: pulses overlap by {-gap:.3e} s")
            if gap > 0:
                gaps[k].append((q, gap))
    return timed, ends, gaps


def axis(n: int, q: int) -> int:
    """Ket tensor axis of compact qubit q: Qiskit's qubit 0 is the least significant bit, the last C-order axis."""
    return n - 1 - q


def block(n: int, qubits: tuple[int, ...], ket: tuple[int, ...], bra: tuple[int, ...]) -> tuple[Any, ...]:
    index: list[Any] = [slice(None)] * (2 * n)
    for q, i, j in zip(qubits, ket, bra, strict=True):
        index[axis(n, q)] = i
        index[n + axis(n, q)] = j
    return tuple(index)


def unitary(rho: np.ndarray, matrix: np.ndarray, q: int, n: int) -> np.ndarray:
    a = axis(n, q)
    rho = np.moveaxis(np.tensordot(matrix, rho, axes=([1], [a])), 0, a)
    return np.moveaxis(np.tensordot(rho, matrix.conj().T, axes=([n + a], [0])), -1, n + a)


def thermal(rho: np.ndarray, q: int, n: int, t1: float, t2: float, seconds: float, part: str = "both") -> np.ndarray:
    """Zero-temperature relaxation of qubit q over seconds: amplitude damping, then dephasing to exp(-t/T2) coherence.

    part "damping" keeps the amplitude damping alone (coherence exp(-t/2T1));
    part "dephasing" keeps the pure dephasing alone, coherence
    exp(-t (1/T2 - 1/2T1)) and no population change.
    """
    t2 = min(t2, 2 * t1)
    decay = 0.0 if part == "dephasing" else 1 - math.exp(-seconds / t1)
    rate = {"both": 1 / t2, "damping": 1 / (2 * t1), "dephasing": 1 / t2 - 1 / (2 * t1)}[part]
    coherence = math.exp(-seconds * rate)
    out = rho.copy()
    out[block(n, (q,), (0,), (0,))] += decay * rho[block(n, (q,), (1,), (1,))]
    out[block(n, (q,), (1,), (1,))] *= 1 - decay
    out[block(n, (q,), (0,), (1,))] *= coherence
    out[block(n, (q,), (1,), (0,))] *= coherence
    return out


def depolarize(rho: np.ndarray, qubits: tuple[int, ...], n: int, strength: float) -> np.ndarray:
    """(1 - lambda) rho + lambda I/d (x) Tr_qubits rho, d = 2^len(qubits)."""
    basis = list(itertools.product((0, 1), repeat=len(qubits)))
    traced = sum(rho[block(n, qubits, b, b)] for b in basis)
    out = (1 - strength) * rho
    for b in basis:
        out[block(n, qubits, b, b)] += strength * traced / len(basis)
    return out


class Channels:
    """Error parameters of one edge's calibration: T1, T2, sx and x error per compact qubit, CZ error per coupler."""

    def __init__(self, snapshot: dict[str, Any], active: list[int]) -> None:
        errors = {(op, tuple(r["qargs"])): r["error"] for op in ("sx", "x", "cz") for r in snapshot["instructions"][op]}
        self.t1 = [snapshot["qubits"][p]["t1"] for p in active]
        self.t2 = [snapshot["qubits"][p]["t2"] for p in active]
        self.gate = {op: [errors[(op, (p,))] for p in active] for op in ("sx", "x")}
        self.cz: dict[tuple[int, int], float] = {}
        for a in range(len(active)):
            for b in range(a + 1, len(active)):
                error = errors.get(("cz", (active[a], active[b])), errors.get(("cz", (active[b], active[a]))))
                if error is not None:
                    self.cz[a, b] = float(error)
        self.flips = [snapshot["qubits"][p]["e01"] + snapshot["qubits"][p]["e10"] for p in active]


def density_probability(sched: Schedule, channels: Channels | None, variant: str) -> float:
    """P(measured qubit reads 0) of the replica under one channel set: none, an IDLE_PARTS variant, cz or sx."""
    (compact, _, _, measured, _), _, gaps = sched
    n = compact.num_qubits
    rho = np.zeros((2,) * (2 * n), dtype=complex)
    rho[(0,) * (2 * n)] = 1.0
    for k, inst in enumerate(compact.data):
        name = inst.operation.name
        qubits = tuple(compact.find_bit(q).index for q in inst.qubits)
        if name == "cz":
            sign = np.ones((2,) * n)
            sign[block(n, qubits, (1, 1), (1, 1))[:n]] = -1.0
            rho = rho * np.multiply.outer(sign, sign)
        else:
            rho = unitary(rho, Operator(inst.operation).data, qubits[0], n)
        if channels is None:
            continue
        if variant == "cz" and name == "cz":
            pair = (min(qubits), max(qubits))
            require(pair in channels.cz, f"coupler {pair} carries no reported CZ error")
            rho = depolarize(rho, qubits, n, CZ_DEPOLARIZING * channels.cz[pair])
        elif variant == "sx" and name in ("sx", "x"):
            rho = depolarize(rho, qubits, n, SQ_DEPOLARIZING * channels.gate[name][qubits[0]])
        elif variant in IDLE_PARTS:
            for q, seconds in gaps.get(k, []):
                rho = thermal(rho, q, n, channels.t1[q], channels.t2[q], seconds, IDLE_PARTS[variant])
    populations = np.real(np.diag(rho.reshape(2**n, 2**n)))
    return float(np.sum(populations[(np.arange(2**n) >> measured) & 1 == 0]))


class EdgeColumns:
    """Noiseless density-matrix probabilities and the idle, CZ and sx log-contrast columns of one edge."""

    def __call__(self, item: tuple[list[Schedule], Channels]) -> dict[str, Any]:
        points, channels = item
        noiseless = [density_probability(s, None, "none") for s in points]
        base, _ = atlas.fringe(noiseless)
        out: dict[str, Any] = {"noiseless": noiseless, "contrast": base}
        for variant, name in VARIANTS:
            contrast, _ = atlas.fringe([density_probability(s, channels, variant) for s in points])
            out[name] = math.log(contrast / base)
        out["idle_seconds"] = sum(seconds for s in points[:1] for gaps in s[2].values() for _, seconds in gaps)
        return out


def fringe_rows() -> np.ndarray:
    phi = np.arange(PHASES) * math.pi / 4
    return np.linalg.pinv(np.column_stack([np.ones(PHASES), np.cos(phi), np.sin(phi)]))


def edge_noise(series: list[dict[str, Any]]) -> dict[str, float]:
    """Propagated sigma of log b for the hardware and the replay fringes of one edge."""
    hardware = [p["hardware"] for p in series]
    replay = [p["replay"] for p in series]
    shots = [p["shots"] for p in series]
    hw = acf.fringe_errors(hardware, [p * (1 - p) / n for p, n in zip(hardware, shots, strict=True)])[0]
    rep = acf.fringe_errors(replay, [p * (1 - p) / n for p, n in zip(replay, shots, strict=True)])[0]
    return {"hardware": hw, "replay": rep}


def bootstrap_sd(series: list[dict[str, Any]], rng: np.random.RandomState) -> float:
    """Standard deviation of log(b_hw / b_replay) over binomial redraws of every point at its probability and shots.

    The draws come from the legacy RandomState stream (Mersenne Twister with the
    legacy binomial algorithm), which numpy freezes across releases. The
    Generator.binomial algorithm changed between numpy 2.1 and 2.5, so a
    Generator-seeded bootstrap differs by build and a retained record from
    another host cannot replay byte for byte.
    """
    rows = fringe_rows()
    shots = np.array([p["shots"] for p in series])
    draws = []
    for key in ("hardware", "replay"):
        p = np.array([q[key] for q in series])
        points = rng.binomial(shots, p, size=(BOOTSTRAP, PHASES)) / shots
        c, s = points @ rows[1], points @ rows[2]
        draws.append(0.5 * np.log(c * c + s * s))
    return float(np.std(draws[0] - draws[1], ddof=1))


class EdgeBootstrap:
    """Pool worker: the bootstrap standard deviation of one edge from its (series, seed) item."""

    def __call__(self, item: tuple[list[dict[str, Any]], list[int]]) -> float:
        return bootstrap_sd(item[0], np.random.RandomState(item[1]))


def structure(y: np.ndarray, sigma: np.ndarray) -> dict[str, Any]:
    """Weighted mean, chi-square against a constant, its p-value and the DerSimonian-Laird excess scatter."""
    w = 1 / np.square(sigma)
    mean = float(np.sum(w * y) / np.sum(w))
    q = float(np.sum(w * np.square(y - mean)))
    dof = len(y) - 1
    tau2 = max(0.0, (q - dof) / float(np.sum(w) - np.sum(np.square(w)) / np.sum(w)))
    p_value = float(stats.chi2.sf(q, dof))
    return {
        "weighted_mean": round(mean, 6),
        "standard_deviation": round(float(np.std(y, ddof=1)), 6),
        "noise_rms": round(acf.rms(sigma), 6),
        "chi2": round(q, 6),
        "dof": dof,
        "chi2_per_dof": round(q / dof, 6),
        "p_value": round(p_value, 9),
        "excess_scatter": round(math.sqrt(tau2), 6),
        "structure_present": bool(p_value < STRUCTURE_P),
    }


def lane_keys(series: acf.Series, lane: int) -> tuple[list[Any], list[Any]]:
    keys = [key for key in series if key[0] == lane]
    excluded = [key for key in keys if len({p["calibration"] for p in series[key]}) > 1]
    return [key for key in keys if key not in excluded], excluded


def lane_structure(backend: str, lane: int, series: acf.Series) -> dict[str, Any]:
    """Observable, propagated and bootstrap noise, and structure statistics of one lane from recorded probabilities."""
    included, excluded = lane_keys(series, lane)
    summaries = [acf.observables(series[key]) for key in included]
    noise = [edge_noise(series[key]) for key in included]
    y = np.array([s["log_contrast_ratio"] for s in summaries])
    sigma = np.array([s["contrast_noise"] for s in summaries])
    total = np.array([math.log(2 * atlas.fringe([p["hardware"] for p in series[key]])[0]) for key in included])
    replay = np.array([math.log(2 * atlas.fringe([p["replay"] for p in series[key]])[0]) for key in included])
    sigma_hw = np.array([v["hardware"] for v in noise])
    seed = [BOOTSTRAP_SEED, sorted(acf.RUNS).index(backend), lane]
    items = [(series[key], [*seed, e]) for e, key in enumerate(included)]
    boot = np.array(parallel.ordered_map(EdgeBootstrap(), items, min_items=2))
    ratio = boot / sigma
    return {
        "backend": backend,
        "lane": lane,
        "edges": [{"kite": k[1], "source": k[2], "target": k[3]} for k in included],
        "excluded_edges": [{"kite": k[1], "source": k[2], "target": k[3]} for k in excluded],
        "log_ratio": [round(float(v), 6) for v in y],
        "ratio": [round(math.exp(float(v)), 6) for v in y],
        "sigma": [round(float(v), 6) for v in sigma],
        "sigma_hardware": [round(float(v), 6) for v in sigma_hw],
        "sigma_replay": [round(v["replay"], 6) for v in noise],
        "bootstrap_over_propagated": [round(float(v), 6) for v in ratio],
        "noise_floor_validated": bool(np.max(np.abs(ratio - 1)) <= BOOTSTRAP_RTOL),
        "replay_loss": [round(float(v), 6) for v in replay],
        "replay_normalized": structure(y, sigma),
        "ideal_normalized": structure(total, sigma_hw),
    }


def design_checks(design: np.ndarray) -> dict[str, Any]:
    """Rank and condition of the column-normalized design and of every leave-one-out fold.

    Columns carry different units (kHz^2, rad^2, a unit constant), so each is
    scaled to unit norm first; the rank and condition then measure collinearity,
    not units. The condition of a design (or of the worst fold) whose rank falls
    short of the column count is null: its smallest singular value is rounding
    noise, so the ratio is inf or about 1e16 by BLAS build and carries no
    collinearity measure beyond the reported rank.
    """
    n, p = design.shape

    def normalized(matrix: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(matrix, axis=0)
        return matrix / np.where(norms > 0, norms, 1.0)

    rank, condition = acf.design_rank(normalized(design))
    folds = [acf.design_rank(normalized(np.delete(design, held, axis=0))) for held in range(n)]
    out: dict[str, Any] = {
        "rank": rank,
        "condition": acf.finite(condition) if rank == p else None,
        "fold_rank_min": min(r for r, _ in folds),
        "fold_condition_max": acf.finite(max(c for _, c in folds)) if all(r == p for r, _ in folds) else None,
    }
    if rank < p:
        out["unidentified"] = f"rank {rank} of {p} columns"
    elif n - 1 <= p:
        out["unidentified"] = f"{n - 1} training edges per fold for {p} columns"
    elif out["fold_rank_min"] < p:
        out["unidentified"] = f"leave-one-out fold rank {out['fold_rank_min']} of {p} columns"
    return out


def solve(design: np.ndarray, target: np.ndarray, lower: np.ndarray | None) -> np.ndarray:
    if lower is None:
        return np.linalg.lstsq(design, target, rcond=None)[0]
    result = optimize.lsq_linear(design, target, bounds=(lower, np.inf), method="bvls", tol=1e-14)
    return np.asarray(result.x)


def score(design: np.ndarray, target: np.ndarray, noise: np.ndarray, lower: np.ndarray | None = None) -> dict[str, Any]:
    """Least-squares fit (bounded below by lower) and its leave-one-edge-out RMS against the propagated floor."""
    n, p = design.shape
    entry: dict[str, Any] = {"columns": p}
    if p:
        entry |= design_checks(design)
        if "unidentified" in entry:
            return entry
    parameters = solve(design, target, lower) if p else np.zeros(0)
    loo, variance = [], []
    for held in range(n):
        keep = [k for k in range(n) if k != held]
        fit = solve(design[keep], target[keep], lower) if p else np.zeros(0)
        loo.append(target[held] - design[held] @ fit)
        # The prediction variance propagates through the columns the fold's own
        # bounded fit leaves off their lower bound.
        active = [j for j in range(p) if lower is None or not math.isfinite(lower[j]) or fit[j] > ACTIVE]
        weights = design[held, active] @ np.linalg.pinv(design[np.ix_(keep, active)]) if active else np.zeros(n - 1)
        variance.append(noise[held] ** 2 + float(np.sum(np.square(weights) * np.square(noise[keep]))))
    residual = target - design @ parameters
    entry |= {
        "parameters": [round(float(v), 9) for v in parameters],
        "fit_rms": round(acf.rms(residual), 6),
        "chi2": round(float(np.sum(np.square(residual / noise))), 6),
        "dof": n - p,
        "leave_one_out_rms": round(acf.rms(loo), 6),
        "leave_one_out_noise_floor": round(float(math.sqrt(np.mean(variance))), 6),
    }
    entry["accounts"] = bool(entry["leave_one_out_rms"] <= ACCOUNTS_FACTOR * entry["leave_one_out_noise_floor"])
    return entry


def linear_design(name: str, columns: dict[str, np.ndarray], measured: list[int]) -> np.ndarray:
    predictors, constant = LINEAR[name]
    blocks: list[np.ndarray] = []
    for predictor in predictors:
        if predictor == "measured_qubit":
            levels = sorted(set(measured))
            blocks.append(np.array([[float(m == level) for level in levels] for m in measured]))
        else:
            blocks.append(columns[predictor][:, None])
    if constant:
        blocks.append(np.ones((len(measured), 1)))
    return np.hstack(blocks)


def lane_fit(
    backend: str,
    lane: int,
    series: acf.Series,
    executed: atlas.Executed,
    observed: dict[str, Any],
    retained: dict[str, Any] | None,
    families: tuple[str, ...] = COHERENT,
    coherent: dict[str, Any] | None = None,
    amplitude_models: bool = True,
) -> dict[str, Any]:
    """Predictor columns, linear and coherent amplitude models of one lane; coherent reuses an acf.lane_fit output."""
    included, _ = lane_keys(series, lane)
    if coherent is None:
        coherent = acf.lane_fit(backend, lane, series, executed, None, retained, families=families, fit=False)
    require(coherent["edges"] == observed["edges"], f"{backend} lane {lane}: edge sets differ from the coherent fit")
    schedules = [[schedule(*executed.replica(p["name"]), executed.dt) for p in series[key]] for key in included]
    active = schedules[0][0][0][4]
    snapshots = {
        c: json.loads(acf.snapshot_path(backend, c).read_text(encoding="utf-8")) for c in coherent["calibrations"]
    }
    channels = [Channels(snapshots[series[key][0]["calibration"]], active) for key in included]
    results = parallel.ordered_map(EdgeColumns(), list(zip(schedules, channels, strict=True)), min_items=2)
    timed = [[s[0] for s in points] for points in schedules]
    statevector = [[acf.probability(t, {}) for t in points] for points in timed]
    mismatch = max(
        abs(a - b) for r, sv in zip(results, statevector, strict=True) for a, b in zip(r["noiseless"], sv, strict=True)
    )
    require(mismatch < DENSITY_TOLERANCE, f"{backend} lane {lane}: density matrix misses the statevector by {mismatch}")
    measured = [points[0][0][4][points[0][0][3]] for points in schedules]
    y = np.array(observed["log_ratio"])
    sigma = np.array(observed["sigma"])
    columns = {name: np.array([r[name] for r in results]) for _, name in VARIANTS}
    columns["readout"] = np.array(
        [
            math.log((1 - 2 * c.flips[s[0][0][3]]) / (1 - c.flips[s[0][0][3]]))
            for c, s in zip(channels, schedules, strict=True)
        ]
    )
    columns["replay_loss"] = np.array(observed["replay_loss"])
    readout_factor = np.array([math.log(1 - c.flips[s[0][0][3]]) for c, s in zip(channels, schedules, strict=True)])
    calibrated = columns["cz_depolarizing"] + columns["sx_depolarizing"] + readout_factor
    difference = columns["replay_loss"] - calibrated
    sigma_replay = np.array(observed["sigma_replay"])
    without_idle = float(np.sum(np.square(difference / sigma_replay)))
    with_idle = float(np.sum(np.square((difference - columns["idle_relaxation"]) / sigma_replay)))
    replay_check = {
        "calibrated_channel_loss": [round(float(v), 6) for v in calibrated],
        "replay_minus_calibrated": [round(float(v), 6) for v in difference],
        "mean_difference": round(float(np.mean(difference)), 6),
        "chi2_replay_omits_idle": round(without_idle, 6),
        "p_replay_omits_idle": round(float(stats.chi2.sf(without_idle, len(difference))), 9),
        "chi2_replay_charges_idle": round(with_idle, 6),
        "p_replay_charges_idle": round(float(stats.chi2.sf(with_idle, len(difference))), 9),
    }
    models: dict[str, Any] = {}
    for name, (predictors, _) in LINEAR.items():
        design = linear_design(name, columns, measured)
        noise = sigma
        if "replay_loss" in predictors:
            # y = h - r and L = r + log 2 share the replay's noise r, so the
            # residual h - (1 + beta) r carries (1 + beta) sigma_replay.
            beta = solve(design, y, None)[0]
            noise = np.hypot(observed["sigma_hardware"], (1 + beta) * np.array(observed["sigma_replay"]))
        models[name] = score(design, y, noise)
    idle = columns["idle_relaxation"]
    models["idle_relaxation_predicted"] = score(np.zeros((len(y), 0)), y - idle, sigma)
    models["idle_relaxation_predicted_plus_constant"] = score(np.ones((len(y), 1)), y - idle, sigma)
    residual = y - idle
    predicted: dict[str, Any] = {
        "chi2": round(float(np.sum(np.square(residual / sigma))), 6),
        "p_value": round(float(stats.chi2.sf(np.sum(np.square(residual / sigma)), len(y))), 9),
        "residual_structure": structure(residual, sigma),
    }
    predicted["refuted"] = bool(predicted["p_value"] < STRUCTURE_P)
    reference = models["lane_constant"]["leave_one_out_rms"]
    for name, entry in models.items():
        if name != "lane_constant" and "leave_one_out_rms" in entry:
            entry["refuted"] = bool(entry["leave_one_out_rms"] >= reference)
    offsets = np.array(coherent["measured_offset_rad"])
    phase_reference = acf.rms(offsets - np.mean(offsets))
    contrast_noise = acf.rms(sigma)
    tau = observed["replay_normalized"]["excess_scatter"]
    amplitude: dict[str, Any] = {}
    if amplitude_models:
        bases = parallel.ordered_map(acf.EdgeResponse([]), timed, min_items=2)
        amplitude = coherent_models(coherent, timed, bases, y, sigma, offsets, phase_reference, contrast_noise, tau)
    for entry in amplitude.values():
        if "leave_one_out_rms" in entry:
            entry["refuted"] = bool(entry["leave_one_out_rms"] >= reference)
    return {
        "backend": backend,
        "lane": lane,
        "physical_qubits": active,
        "calibrations": coherent["calibrations"],
        "edges": observed["edges"],
        "measured_qubit": measured,
        "executed_cz": coherent["executed_cz"],
        "idle_seconds": [round(r["idle_seconds"], 12) for r in results],
        "density_statevector_mismatch": mismatch,
        "columns": {name: [round(float(v), 9) for v in values] for name, values in columns.items()},
        "log_ratio": observed["log_ratio"],
        "sigma": observed["sigma"],
        "excess_scatter": tau,
        "measured_offset_rad": coherent["measured_offset_rad"],
        "phase_lane_mean_fit_rms_rad": round(phase_reference, 6),
        "idle_prediction": predicted,
        "replay_channel_check": replay_check,
        "models": models,
        "coherent_models": amplitude,
    }


def coherent_models(
    coherent: dict[str, Any],
    timed: list[list[acf.Timed]],
    bases: list[dict[str, Any]],
    y: np.ndarray,
    sigma: np.ndarray,
    offsets: np.ndarray,
    phase_reference: float,
    contrast_noise: float,
    tau: float,
) -> dict[str, Any]:
    """Bounded fits of y = a + K u per coherent family, then every sign pattern of the fitted magnitudes resimulated."""
    n = len(y)
    plans: dict[str, dict[str, Any]] = {}
    items: list[tuple[list[acf.Timed], dict[acf.Column, float], float, float]] = []
    for family, summary in coherent["families"].items():
        curvature = np.array(summary["contrast_curvature"])
        width = curvature.shape[1]
        keys = acf.columns_for(
            family, len(coherent["physical_qubits"]), [tuple(c) for c in coherent["couplers_compact"]]
        )
        keep = [j for j in range(width) if np.max(np.abs(curvature[:, j])) > ACTIVE]
        design = np.hstack([curvature[:, keep], np.ones((n, 1))])
        lower = np.array([0.0] * len(keep) + [-np.inf])
        entry = score(design, y, sigma, lower)
        entry["fitted_columns"] = [k[1] if isinstance(k[1], int) else list(k[1]) for k in (keys[j] for j in keep)]
        bound = summary.get("gate_error_bound")
        if bound is not None:
            entry["contrast_reach_at_bound"] = summary["contrast_reach_at_bound"]
            entry["reach_covers_excess_scatter"] = bool(summary["contrast_reach_at_bound"] >= tau)
        plans[family] = {"entry": entry}
        if "parameters" not in entry:
            continue
        u = np.array(entry["parameters"][:-1])
        magnitudes = np.sqrt(np.maximum(u, 0))
        entry["magnitudes"] = [round(float(v), 6) for v in magnitudes]
        if bound is not None:
            entry["magnitudes_exceeding_gate_error_bound"] = [
                entry["fitted_columns"][i] for i, j in enumerate(keep) if magnitudes[i] > bound[j]
            ]
        on = [i for i in range(len(keep)) if u[i] > ACTIVE]
        patterns = list(itertools.product((1, -1), repeat=len(on)))
        plans[family] |= {"first": len(items), "patterns": patterns, "on": on, "keep": keep, "keys": keys}
        for pattern in patterns:
            errors = {keys[keep[i]]: sign * float(magnitudes[i]) for sign, i in zip(pattern, on, strict=True)}
            items.extend((timed[e], errors, bases[e]["contrast"], bases[e]["phase"]) for e in range(n))
    simulated = parallel.ordered_map(acf.Resimulate(), items, min_items=2)
    out: dict[str, Any] = {}
    for family, plan in plans.items():
        entry = plan["entry"]
        out[f"{family}_curvature_plus_constant"] = entry
        if "patterns" not in plan:
            continue
        constant = entry["parameters"][-1]
        quadratic = np.array(coherent["families"][family]["contrast_curvature"])[:, plan["keep"]] @ np.array(
            entry["parameters"][:-1]
        )
        rows: list[dict[str, Any]] = []
        for k, pattern in enumerate(plan["patterns"]):
            shifts = simulated[plan["first"] + k * n : plan["first"] + (k + 1) * n]
            phase = np.array([atlas.wrap(offsets[e] - shifts[e][0]) for e in range(n)])
            contrast = np.array([s[1] for s in shifts])
            rows.append(
                {
                    "signs": list(pattern),
                    "phase_residual_rms_rad": acf.rms(phase - np.mean(phase)),
                    "contrast_residual_rms": acf.rms(y - constant - contrast),
                    "diagonal_error_max": float(np.max(np.abs(contrast - quadratic))),
                }
            )
        best = min(rows, key=lambda r: (r["phase_residual_rms_rad"], rows.index(r)))
        entry["resimulated"] = {
            "patterns": len(rows),
            "active_columns": [entry["fitted_columns"][i] for i in plan["on"]],
            "best_signs": best["signs"],
            "phase_residual_rms_best_rad": round(best["phase_residual_rms_rad"], 6),
            "phase_residual_rms_worst_rad": round(max(r["phase_residual_rms_rad"] for r in rows), 6),
            "contrast_residual_rms_best_signs": round(best["contrast_residual_rms"], 6),
            "contrast_residual_rms_range": [
                round(min(r["contrast_residual_rms"] for r in rows), 6),
                round(max(r["contrast_residual_rms"] for r in rows), 6),
            ],
            "diagonal_error_max": round(max(r["diagonal_error_max"] for r in rows), 6),
        }
        entry["refuted_by_phase"] = bool(best["phase_residual_rms_rad"] >= phase_reference)
        entry["diagonal_model_holds"] = bool(entry["resimulated"]["diagonal_error_max"] <= contrast_noise)
    return out


def run_inputs(backends: list[str], fits: list[dict[str, Any]], coherent_lanes: bool) -> dict[str, str]:
    paths = [acf.RETAINED_DETUNING] if coherent_lanes else []
    for backend in backends:
        paths += acf.run_inputs(backend)
    for fit in fits:
        paths += [acf.snapshot_path(fit["backend"], c) for c in fit["calibrations"]]
    return acf.digests(paths)


def run(backends: list[str], lanes: list[int]) -> dict[str, Any]:
    retained = {fit["lane"]: fit for fit in json.loads(acf.RETAINED_DETUNING.read_text(encoding="utf-8"))["lanes"]}
    structures: list[dict[str, Any]] = []
    fits: list[dict[str, Any]] = []
    for backend in backends:
        series = acf.series_for(backend)
        observed = {lane: lane_structure(backend, lane, series) for lane in range(acf.LANES)}
        structures += observed.values()
        if not lanes:
            continue
        executed = atlas.Executed(acf.RUNS[backend])
        for lane in lanes:
            fit = lane_fit(
                backend, lane, series, executed, observed[lane], retained[lane] if backend == "ibm_fez" else None
            )
            fits.append(fit)
            summary = {name: model.get("leave_one_out_rms") for name, model in fit["models"].items()}
            print(json.dumps({"backend": backend, "lane": lane, "loo": summary}), flush=True)
    return {
        "schema": SCHEMA,
        "runs": {b: acf.RUNS[b].relative_to(ROOT).as_posix() for b in backends},
        "inputs": run_inputs(backends, fits, bool(lanes)),
        "bootstrap": {"draws": BOOTSTRAP, "seed": BOOTSTRAP_SEED},
        "models": {name: {"columns": list(cols), "lane_constant": c} for name, (cols, c) in LINEAR.items()},
        "structure": structures,
        "lanes": fits,
    }


def planted_counts(series: list[dict[str, Any]], log_ratio: float, rng: np.random.Generator) -> list[dict[str, Any]]:
    """The edge with its hardware points replaced by binomial draws from the replay fringe scaled by exp(log_ratio)."""
    rows = fringe_rows()
    replay = np.array([p["replay"] for p in series])
    a, c, s = rows @ replay
    phi = np.arange(PHASES) * math.pi / 4
    scaled = a + math.exp(log_ratio) * (c * np.cos(phi) + s * np.sin(phi))
    out = []
    for point, probability in zip(series, scaled, strict=True):
        counts = rng.binomial(point["shots"], probability)
        out.append(point | {"hardware": counts / point["shots"]})
    return out


# A planted idle coefficient whose edge spread, about 3 x 0.013 on Fez lane
# 4, exceeds the 0.024 shot noise, so the structure test can see it.
PLANTED_IDLE = 3.0
# Planted sx amplitude (compact column, value) on qubit 58, below its 0.029
# gate-error bound, with a lane constant.
PLANTED_SX = ((3, -0.02),)
PLANTED_CONSTANT = -0.15


def self_test() -> int:
    """Channel algebra, density matrix against statevector, bootstrap, and planted structure on Fez lane 4."""
    from qiskit.quantum_info import DensityMatrix, random_density_matrix
    from qiskit_aer.noise import depolarizing_error, thermal_relaxation_error

    rho = random_density_matrix(4, seed=7)
    tensor = rho.data.reshape((2,) * 4)
    for q in (0, 1):
        expected = rho.evolve(thermal_relaxation_error(80e-6, 60e-6, 3e-6).to_quantumchannel(), [q]).data
        got = thermal(tensor, q, 2, 80e-6, 60e-6, 3e-6).reshape(4, 4)
        require(np.max(np.abs(got - expected)) < 1e-12, f"thermal relaxation on qubit {q} differs from qiskit_aer")
        expected = rho.evolve(depolarizing_error(0.03, 1).to_quantumchannel(), [q]).data
        got = depolarize(tensor, (q,), 2, 0.03).reshape(4, 4)
        require(np.max(np.abs(got - expected)) < 1e-12, f"depolarizing on qubit {q} differs from qiskit_aer")
    expected = rho.evolve(depolarizing_error(0.03, 2).to_quantumchannel(), [0, 1]).data
    require(
        np.max(np.abs(depolarize(tensor, (0, 1), 2, 0.03).reshape(4, 4) - expected)) < 1e-12, "two-qubit depolarizing"
    )
    flipped = DensityMatrix(rho.data).evolve(Operator.from_label("IX")).data
    require(
        np.max(np.abs(unitary(tensor, Operator.from_label("X").data, 0, 2).reshape(4, 4) - flipped)) < 1e-12, "axis"
    )
    print("thermal relaxation, one- and two-qubit depolarizing and qubit order equal qiskit_aer within 1e-12")

    retained = {fit["lane"]: fit for fit in json.loads(acf.RETAINED_DETUNING.read_text(encoding="utf-8"))["lanes"]}
    backend, lane = "ibm_fez", 4
    series = acf.fez_series()
    executed = atlas.Executed(acf.RUNS[backend])
    observed = lane_structure(backend, lane, series)
    worst = float(np.max(np.abs(np.array(observed["bootstrap_over_propagated"]) - 1)))
    print(f"{backend} lane {lane}: bootstrap sd / propagated sigma within {worst:.3f} of 1 on 12 edges")
    require(observed["noise_floor_validated"], f"bootstrap departs from the propagated sigma by {worst:.3f}")
    coherent = acf.lane_fit(
        backend, lane, series, executed, None, retained[lane], families=("sx_amplitude",), fit=False
    )
    fit = lane_fit(backend, lane, series, executed, observed, retained[lane], coherent=coherent, amplitude_models=False)
    print(f"density matrix against statevector: {fit['density_statevector_mismatch']:.1e}")
    included, _ = lane_keys(series, lane)
    idle = np.array(fit["columns"]["idle_relaxation"])
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    cases = {"constant": np.full(len(included), -0.2), "idle_x3": -0.05 + PLANTED_IDLE * idle}
    for case, planted in cases.items():
        synthetic = {key: planted_counts(series[key], float(v), rng) for key, v in zip(included, planted, strict=True)}
        result = lane_structure(backend, lane, synthetic)
        stats_ = result["replay_normalized"]
        print(f"planted {case}: chi2/dof {stats_['chi2_per_dof']:.2f}, p {stats_['p_value']:.2e}")
        if case == "constant":
            require(not stats_["structure_present"], "a planted lane-constant ratio is flagged as structure")
        else:
            require(stats_["structure_present"], f"planted {PLANTED_IDLE} x idle relaxation is not flagged")
            y = np.array(result["log_ratio"])
            design = np.column_stack([idle, np.ones(len(y))])
            kappa, _ = np.linalg.lstsq(design, y, rcond=None)[0]
            spread = float(np.std(idle))
            error = float(np.sqrt(np.linalg.inv(design.T @ design)[0, 0])) * stats_["noise_rms"]
            print(
                f"  idle coefficient {kappa:.3f} (planted {PLANTED_IDLE}, standard error {error:.3f}, "
                f"idle spread {spread:.4f})"
            )
            require(abs(kappa - PLANTED_IDLE) <= 3 * error, f"planted idle coefficient recovered as {kappa:.3f}")
    # Coherent recovery: the exact log contrast of an injected sx amplitude
    # on one column at a time, plus a constant, through the bounded fit.
    prepared = [[timed_replica_of(executed, p) for p in series[key]] for key in included]
    bases = parallel.ordered_map(acf.EdgeResponse([]), prepared, min_items=2)
    sigma = np.array(observed["sigma"])
    for column, value in PLANTED_SX:
        injected = {("sx_amplitude", column): value}
        items = [(prepared[e], injected, bases[e]["contrast"], bases[e]["phase"]) for e in range(len(included))]
        shifts = parallel.ordered_map(acf.Resimulate(), items, min_items=2)
        contrast = np.array([shift[1] for shift in shifts]) + PLANTED_CONSTANT
        offsets = np.array([shift[0] for shift in shifts])
        reference = acf.rms(offsets - np.mean(offsets))
        models = coherent_models(coherent, prepared, bases, contrast, sigma, offsets, reference, acf.rms(sigma), 0.0)
        entry = models["sx_amplitude_curvature_plus_constant"]
        recovered = dict(zip(entry["fitted_columns"], entry["magnitudes"], strict=True))
        squared = dict(zip(entry["fitted_columns"], entry["parameters"][:-1], strict=True))
        constant = entry["parameters"][-1]
        resimulated = entry["resimulated"]
        print(
            f"planted sx_amplitude {value} on qubit {column}: magnitudes {recovered}, constant {constant:.4f}, "
            f"phase residual at the best signs {resimulated['phase_residual_rms_best_rad']:.1e} rad"
        )
        require(abs(recovered[column] - abs(value)) <= 0.1 * abs(value), f"qubit {column} recovered as {recovered}")
        # An uninjected column's squared magnitude u_j is its share of the
        # contrast loss; it stays below a tenth of the injected value^2.
        others = [v for q, v in squared.items() if q != column]
        require(all(v <= 0.1 * value**2 for v in others), f"uninjected sx_amplitude u recovered as {others}")
        require(abs(constant - PLANTED_CONSTANT) < 0.01, f"planted constant recovered as {constant}")
        sign = resimulated["best_signs"][resimulated["active_columns"].index(column)]
        require(sign == (1 if value > 0 else -1), f"qubit {column}: best sign {sign} for a planted {value}")
    print("self-test passed")
    return 0


def timed_replica_of(executed: atlas.Executed, point: dict[str, Any]) -> acf.Timed:
    return acf.timed_replica(*executed.replica(point["name"]), executed.dt)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs", default="ibm_fez,ibm_kingston")
    parser.add_argument("--lanes", default="4")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    backends = args.runs.split(",")
    require(set(backends) <= set(acf.RUNS), f"--runs names a backend outside {sorted(acf.RUNS)}")
    lanes = list(range(acf.LANES)) if args.lanes == "all" else [int(v) for v in args.lanes.split(",") if v]
    if args.check:
        retained = json.loads(args.check.read_text(encoding="utf-8"))
        require(retained.get("schema") == SCHEMA, f"{args.check}: schema {retained.get('schema')}, expected {SCHEMA}")
        for name, digest in retained["inputs"].items():
            path = ROOT / name
            require(path.is_file() and acf.sha256(path) == digest, f"{name}: sha256 differs from {args.check}")
        named = [(fit["backend"], fit["lane"]) for fit in retained["lanes"]]
        selected = [(b, lane) for b, lane in named if b in backends and lane in lanes]
        require(bool(selected), f"{args.check}: holds none of the selected lanes")
        for backend in sorted({b for b, _ in selected}):
            fresh = run([backend], [lane for b, lane in selected if b == backend])
            unnamed = sorted(set(fresh["inputs"]) - set(retained["inputs"]))
            require(not unnamed, f"{args.check}: the rerun read files the result does not name: {unnamed}")
            for block in ("bootstrap", "models"):
                acf.compare(retained[block], fresh[block], f"{block}")
            for name, path in fresh["runs"].items():
                acf.compare(retained["runs"].get(name), path, f"runs.{name}")
            for kind in ("structure", "lanes"):
                by_lane = {item["lane"]: item for item in fresh[kind]}
                for item in retained[kind]:
                    if item["backend"] == backend and (kind == "structure" or item["lane"] in by_lane):
                        acf.compare(item, by_lane[item["lane"]], f"{backend} {kind} lane {item['lane']}")
        print(f"{args.check}: lanes {selected} and the structure of {sorted({b for b, _ in selected})} reproduced")
        return 0
    require(args.out is not None, "--out is required")
    result = run(backends, lanes)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
