"""Descriptive beat models of the ibm_fez qubit 143 ground Ramsey sweep (post hoc, not preregistered).

The preregistered analysis of the sweep (n21_spectator_ramsey.py, gate
core-603) reads a visibility that falls and revives, which no monotone
envelope describes. This module fits physical models of a two-frequency
coherence to the same herald-selected counts. Every result here is
descriptive: the models, the band and the comparisons were chosen after the
data were seen.

Signal. With t in microseconds and frequencies in MHz, each model predicts
the complex coherence S(t) = <X>(t) + i <Y>(t) of qubit 143 after its
preparation in |+>, written S = A exp(i phi) exp(-t / T) g(t) with g(0) = 1.
A rz(+theta) advances phi by +theta (n21_spectator_ramsey), so a level
whose energy rises by E in the drive frame contributes exp(-2 pi i E t).
Readout maps a true expectation mu to the measured one through the
qubit's asymmetric assignment channel, e0 = P(1 | 0) = prob_meas1_prep0
and e1 = P(0 | 1) = prob_meas0_prep1:

    mu_measured = (1 - e0 - e1) mu + (e1 - e0)

e0 and e1 enter as the published execution-start values, fixed: the
backend publishes no calibration shot count behind them. The coherence
amplitude stays physical (A <= 1).

X and Y of one delay come from separate PUBs of one job, whose execution
order the service does not guarantee, so pairing them into S(t) assumes no
drift between the two PUBs; the per-basis fits (basis_alone) test the beat
without that pairing.

Models, each g(t):
- single: exp(2 pi i f t), one frequency (the null of a beat).
- static: a exp(2 pi i f1 t) + (1 - a) exp(2 pi i (f1 + df) t), a classical
  mixture fixed within each shot (charge-parity splitting slower than the
  shot), a >= 1/2 the heavier component.
- telegraph: the frequency switches between f1 and f1 + df as a stationary
  two-state Markov process with total rate gamma and occupations (a, 1 - a)
  (Kubo-Anderson); g(t) = 1^T exp(M t) p with
  M = 2 pi i diag(f1, f1 + df) + W, W the rate matrix, p = (a, 1 - a).
  gamma -> 0 returns static; gamma >> 2 pi |df| narrows the line to the
  mean frequency.
- tls: qubit (two-level) times a two-level system with exchange coupling g
  and detuning Delta, H = fq n_q + ft n_t + g (sigma+ tau- + sigma- tau+),
  under the Lindblad dissipators of the qubit's calibrated T1, a qubit pure
  dephasing that sets T, and TLS relaxation gamma_tls toward its thermal
  population p; S comes from the full 4 x 4 density matrix. Without
  dissipation the coherence carries weight cos^2 theta at the upper and
  sin^2 theta at the lower dressed level in both TLS branches, so
  Omega = sqrt(Delta^2 + 4 g^2) = |df|, Delta = df (2 a - 1) and
  g = |df| sqrt(a (1 - a)), and p leaves the Ramsey signal unchanged.

Lattice. The idles are k T0 with T0 = 836 dt, so a shift of every
frequency by n / T0 (common mode) leaves every model's prediction unchanged
exactly, and a shift of df alone by n / T0 does so for single and static;
telegraph and tls break the relative alias only through their dissipative
mixing of the two components.

--self-check runs the planted truths; --check regenerates
RUN_DIR/beat-model.json and requires equal bytes; without --check the
report prints or writes to --out.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy.linalg import expm
from scipy.optimize import minimize
from scipy.stats import chi2

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gororoba_quantum"))

import n21_orbit_rca as rca  # noqa: E402
import n21_spectator_ramsey as ramsey  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "n21-q143-beat-model-v1"
RETAINED = "beat-model.json"
SPECTATOR = 143
DT_US = 0.004
WINDOW_DT = 836
T0_US = WINDOW_DT * DT_US
F0_MHZ = 1.0 / T0_US
# The alias enumeration band. A TLS coupling resolved as a beat needs
# Omega within the band the Ramsey idles can follow; 2 MHz bounds the
# relative alias search and the follow-up design's unaliased band.
BAND_MHZ = 2.0
MODELS = ("single", "static", "telegraph", "tls")
COMMON = ("amplitude", "t_us", "phi", "e0", "e1")
SPECIFIC = {
    "single": ("f_mhz",),
    "static": ("a", "f1_mhz", "df_mhz"),
    "telegraph": ("a", "f1_mhz", "df_mhz", "gamma_per_us"),
    "tls": ("a", "f1_mhz", "df_mhz", "gamma_tls_per_us"),
}
DESCRIPTIONS = {
    "single": "one frequency with an exponential envelope",
    "static": "classical two-frequency mixture fixed within each shot",
    "telegraph": "Kubo-Anderson two-state frequency switching at total rate gamma",
    "tls": "qubit exchange-coupled to a damped two-level system (Lindblad, 4 x 4 density matrix)",
}
# Profile grid over one relative-alias period and the search bounds.
PROFILE_POINTS = 240
FREQUENCY_STARTS = 48
T_BOUNDS = (1.0, 2000.0)
RATE_BOUNDS = (0.0, 50.0)
BOOTSTRAP_REPLICATES = 64
BOOTSTRAP_SEED = 20261020
# TLS populations the follow-up evaluation spans: p leaves the two-level
# Ramsey signal unchanged, so the fits read p = 0, while the Z swap depth
# (1 - p) 4 a (1 - a) and every design separation that uses it take their
# worst case over this grid.
POPULATION_GRID = (0.0, 0.25, 0.5, 0.75, 1.0)
# Transmon anharmonicity of the three-level check (MHz). Heron r2
# properties publish no anharmonicity (docs/notes/ibm_quantum/
# heron-r2-readout-resonator.md), so the check uses a typical fixed-frequency
# transmon value and reports the shift it predicts.
ANHARMONICITY_MHZ = -300.0
# Billed seconds of a job (n21 cost rule): fixed overhead plus, per shot,
# rep_delay, the INIT/FINI sequence and the compiled circuit duration.
JOB_OVERHEAD_S = 2.3
REP_DELAY_US = 50.0
INIT_FINI_US = 8.85


def names(model: str) -> tuple[str, ...]:
    return COMMON + SPECIFIC[model]


def bounds(model: str, data: Data) -> list[tuple[float | None, float | None]]:
    """Search bounds of a model's parameters.

    tls bounds T by 2 T1, the pure-dephasing floor. e0 and e1 are pinned at
    the published assignment errors: the backend reports them without
    their calibration shot count, so they enter as fixed values.
    """
    upper_t = min(T_BOUNDS[1], 2.0 * data.t1_us) if model == "tls" else T_BOUNDS[1]
    common: list[tuple[float | None, float | None]] = [
        (0.0, 1.0),
        (T_BOUNDS[0], upper_t),
        (None, None),
        (data.e0, data.e0),
        (data.e1, data.e1),
    ]
    specific: dict[str, list[tuple[float | None, float | None]]] = {
        "single": [(None, None)],
        "static": [(0.5, 1.0), (None, None), (None, None)],
        "telegraph": [(0.5, 1.0), (None, None), (None, None), RATE_BOUNDS],
        "tls": [(0.5, 1.0), (None, None), (None, None), (0.0, 10.0)],
    }
    return common + specific[model]


# Data ---------------------------------------------------------------------


class Data:
    """Herald-selected counts of one quadrature per point, the published assignment errors and T1.

    population is the TLS thermal population p the tls model evaluates
    with; the Ramsey coherence is independent of it, the Z swap is not.
    """

    def __init__(
        self,
        times: np.ndarray,
        bases: np.ndarray,
        zeros: np.ndarray,
        shots: np.ndarray,
        e0: float,
        e1: float,
        t1_us: float,
        population: float = 0.0,
    ) -> None:
        self.times = np.asarray(times, dtype=float)
        # 0 reads X, 1 reads Y after a |+> preparation; 2 reads Z after a
        # |1> preparation (design members only).
        self.bases = np.asarray(bases, dtype=np.int64)
        self.zeros = np.asarray(zeros, dtype=float)
        self.shots = np.asarray(shots, dtype=float)
        self.e0 = e0
        self.e1 = e1
        self.t1_us = t1_us
        self.population = population

    def replicate(self, zeros: np.ndarray) -> Data:
        return Data(self.times, self.bases, zeros, self.shots, self.e0, self.e1, self.t1_us, self.population)

    def subset(self, keep: np.ndarray) -> Data:
        return Data(
            self.times[keep],
            self.bases[keep],
            self.zeros[keep],
            self.shots[keep],
            self.e0,
            self.e1,
            self.t1_us,
            self.population,
        )

    def at_population(self, population: float) -> Data:
        return Data(self.times, self.bases, self.zeros, self.shots, self.e0, self.e1, self.t1_us, population)


def calibration_values(calibrations: dict[str, dict[str, Any]]) -> tuple[float, float, float]:
    """Published (e0, e1) and T1 of qubit 143, one value over every member."""
    found = {
        (
            float(entry["values"][str(SPECTATOR)]["prob_meas1_prep0"]),
            float(entry["values"][str(SPECTATOR)]["prob_meas0_prep1"]),
            float(entry["values"][str(SPECTATOR)]["T1"]),
        )
        for entry in calibrations.values()
    }
    if len(found) != 1:
        raise RuntimeError(f"members read qubit {SPECTATOR} under {len(found)} calibrations; one is modelled")
    ((e0, e1, t1),) = found
    return e0, e1, t1


def run_data(run: Path) -> tuple[Data, dict[str, Any]]:
    """The all-zero herald-selected reads of the sweep, with their exposures from the compiled schedules."""
    schedules, control, unresolved = ramsey.run_schedules(run)
    if unresolved:
        raise RuntimeError(f"{run}: unresolved schedules {sorted(unresolved)}")
    spectators = {int(schedule["spectator"]) for schedule in schedules.values()}
    if spectators != {SPECTATOR}:
        raise RuntimeError(f"{run} idles qubits {sorted(spectators)}, not {SPECTATOR}")
    reads, _conditioning, _bits = ramsey.run_reads(run, control)
    if reads is None:
        raise RuntimeError(f"{run} carries no initialization herald")
    e0, e1, t1 = calibration_values(rca.execution_calibration(run))
    rows = sorted(
        (int(schedules[name]["exposure_dt"]), name.rsplit("_", 1)[1], zeros, shots)
        for name, (zeros, shots) in reads["all_zero"].items()
    )
    data = Data(
        np.array([row[0] * DT_US for row in rows]),
        np.array([("x", "y").index(row[1]) for row in rows]),
        np.array([row[2] for row in rows]),
        np.array([row[3] for row in rows]),
        e0,
        e1,
        t1,
    )
    source = {
        "selection": "all_zero: shots whose initialization herald reads every pinned qubit 0",
        "points": [list(row) for row in rows],
        "exposure_dt": sorted({row[0] for row in rows}),
        "readout_fixed": {"e0_prob_meas1_prep0": e0, "e1_prob_meas0_prep1": e1},
        "t1_us": t1,
    }
    return data, source


# Models -------------------------------------------------------------------


def telegraph_kernel(a: float, f1: float, df: float, gamma: float, times: np.ndarray) -> np.ndarray:
    """1^T exp(M t) p of the stationary two-state frequency process at every time."""
    rate_out_1 = gamma * (1.0 - a)
    rate_out_2 = gamma * a
    generator = np.array(
        [
            [2j * math.pi * f1 - rate_out_1, rate_out_2],
            [rate_out_1, 2j * math.pi * (f1 + df) - rate_out_2],
        ]
    )
    propagators = expm(times[:, None, None] * generator[None, :, :])
    occupation = np.array([a, 1.0 - a], dtype=complex)
    return np.asarray(propagators.sum(axis=1) @ occupation)


def tls_hamiltonian(a: float, f1: float, df: float) -> tuple[float, float, float]:
    """(fq, ft, g) in MHz of the exchange pair whose Ramsey lines sit at f1 (weight a) and f1 + df.

    Observed frequencies are minus the dressed energies, the heavier line is
    the dressed level of qubit weight a, so Omega = |df|, Delta = df (2 a - 1),
    g = |df| sqrt(a (1 - a)) and the mean energy is -(f1 + df / 2).
    """
    mean = -(f1 + df / 2.0)
    delta = df * (2.0 * a - 1.0)
    coupling = abs(df) * math.sqrt(max(a * (1.0 - a), 0.0))
    return mean + delta / 2.0, mean - delta / 2.0, coupling


def _lindblad(hamiltonian: np.ndarray, jumps: list[np.ndarray]) -> np.ndarray:
    """Column-stacking Liouvillian of H (rad/us) and jump operators (sqrt rate/us)."""
    size = hamiltonian.shape[0]
    identity = np.eye(size)
    generator = -1j * (np.kron(identity, hamiltonian) - np.kron(hamiltonian.T, identity))
    for jump in jumps:
        product = jump.conj().T @ jump
        generator += np.kron(jump.conj(), jump) - 0.5 * np.kron(identity, product) - 0.5 * np.kron(product.T, identity)
    return np.asarray(generator)


def exchange_operators(levels: int) -> dict[str, np.ndarray]:
    """Qubit (levels-level transmon) times TLS operators, qubit index major."""
    lower = np.diag(np.sqrt(np.arange(1, levels)), 1).astype(complex)
    tls_lower = np.array([[0.0, 1.0], [0.0, 0.0]], dtype=complex)
    q_identity, t_identity = np.eye(levels), np.eye(2)
    return {
        "a": np.kron(lower, t_identity),
        "n": np.kron(lower.conj().T @ lower, t_identity),
        "tau": np.kron(q_identity, tls_lower),
        "nt": np.kron(q_identity, tls_lower.conj().T @ tls_lower),
        "levels": np.array(levels),
    }


def tls_signal(
    fq: float,
    ft: float,
    coupling: float,
    t2_us: float,
    t1_us: float,
    gamma_tls: float,
    population: float,
    times: np.ndarray,
    basis: str = "ramsey",
    levels: int = 2,
    anharmonicity: float = ANHARMONICITY_MHZ,
) -> np.ndarray:
    """Ramsey coherence <X> + i <Y> (basis "ramsey", |+> start) or <Z> (basis "z", |1> start) of the exchange pair.

    Qubit relaxation sqrt(1/T1) a, pure dephasing at rate 1/T2 - 1/(2 T1)
    through sqrt(rate / 2) (2 n - 1) on the two lowest levels, TLS
    relaxation toward population p at total rate gamma_tls; the TLS starts
    thermal, diag(1 - p, p).
    """
    ops = exchange_operators(levels)
    two_pi = 2.0 * math.pi
    a_op, n_op, tau, nt = ops["a"], ops["n"], ops["tau"], ops["nt"]
    hamiltonian = two_pi * (
        fq * n_op
        + 0.5 * anharmonicity * (n_op @ n_op - n_op)
        + ft * nt
        + coupling * (a_op.conj().T @ tau + a_op @ tau.conj().T)
    )
    dephasing = max(1.0 / t2_us - 0.5 / t1_us, 0.0)
    jumps = [math.sqrt(1.0 / t1_us) * a_op, math.sqrt(dephasing / 2.0) * (2.0 * n_op - np.eye(2 * levels))]
    if gamma_tls > 0.0:
        jumps.append(math.sqrt(gamma_tls * (1.0 - population)) * tau)
        if population > 0.0:
            jumps.append(math.sqrt(gamma_tls * population) * tau.conj().T)
    generator = _lindblad(hamiltonian, jumps)
    qubit = np.zeros((levels, levels), dtype=complex)
    if basis == "ramsey":
        qubit[:2, :2] = 0.5
    else:
        qubit[1, 1] = 1.0
    initial = np.kron(qubit, np.diag([1.0 - population, population]).astype(complex))
    size = 2 * levels
    states = expm(times[:, None, None] * generator[None, :, :]) @ initial.reshape(-1, order="F")
    # A C-order reshape of a column-stacked vector is rho transposed.
    rho = states.reshape(len(times), size, size).transpose(0, 2, 1)
    # 2 |0><1| on the qubit: Tr[rho (X + i Y)] = 2 rho_{1,0} summed over the TLS.
    if basis == "ramsey":
        return np.asarray(2.0 * (rho[:, 2, 0] + rho[:, 3, 1]))
    populations = np.real(np.einsum("kii->ki", rho))
    ground = populations[:, 0] + populations[:, 1]
    return np.asarray(2.0 * ground - 1.0 + 0j)


def coherence(model: str, params: np.ndarray, times: np.ndarray, t1_us: float, population: float = 0.0) -> np.ndarray:
    """S(t) = <X> + i <Y> of a |+> preparation."""
    amplitude, t_us, phi = params[0], params[1], params[2]
    rest = params[5:]
    if model == "tls":
        fq, ft, coupling = tls_hamiltonian(*rest[:3])
        shape = tls_signal(fq, ft, coupling, t_us, t1_us, rest[3], population, times)
        return np.asarray(amplitude * np.exp(1j * phi) * shape)
    envelope = amplitude * np.exp(1j * phi - times / t_us)
    if model == "single":
        return np.asarray(envelope * np.exp(2j * math.pi * rest[0] * times))
    a, f1, df = rest[0], rest[1], rest[2]
    if model == "static":
        return np.asarray(
            envelope * (a * np.exp(2j * math.pi * f1 * times) + (1.0 - a) * np.exp(2j * math.pi * (f1 + df) * times))
        )
    return np.asarray(envelope * telegraph_kernel(a, f1, df, rest[3], times))


def population_z(
    model: str, params: np.ndarray, times: np.ndarray, t1_us: float, population: float = 0.0
) -> np.ndarray:
    """<Z> after a |1> preparation: T1 decay for the frequency models, the exchange swap for tls."""
    if model == "tls":
        fq, ft, coupling = tls_hamiltonian(*params[5:8])
        return np.real(tls_signal(fq, ft, coupling, params[1], t1_us, params[8], population, times, basis="z"))
    return np.asarray(1.0 - 2.0 * np.exp(-times / t1_us))


def true_mean(model: str, params: np.ndarray, data: Data) -> np.ndarray:
    mean = np.empty(data.times.size)
    ramsey_points = data.bases < 2
    if ramsey_points.any():
        signal = coherence(model, params, data.times[ramsey_points], data.t1_us, data.population)
        mean[ramsey_points] = np.where(data.bases[ramsey_points] == 0, signal.real, signal.imag)
    if (~ramsey_points).any():
        mean[~ramsey_points] = population_z(model, params, data.times[~ramsey_points], data.t1_us, data.population)
    return mean


def measured_mean(model: str, params: np.ndarray, data: Data) -> np.ndarray:
    e0, e1 = params[3], params[4]
    return np.asarray((1.0 - e0 - e1) * true_mean(model, params, data) + (e1 - e0))


def negative_log_likelihood(params: np.ndarray, model: str, data: Data) -> float:
    """Binomial NLL of every point's zero count."""
    probability = 0.5 * (1.0 + measured_mean(model, params, data))
    if np.any(probability <= 0.0) or np.any(probability >= 1.0) or not np.all(np.isfinite(probability)):
        return 1e18
    counts = data.zeros * np.log(probability) + (data.shots - data.zeros) * np.log1p(-probability)
    return float(-counts.sum())


def saturated_nll(data: Data) -> float:
    """NLL at p = zeros / shots for every point."""
    total = 0.0
    for zeros, shots in zip(data.zeros, data.shots, strict=True):
        for count in (zeros, shots - zeros):
            if count > 0:
                total -= count * math.log(count / shots)
    return total


# Fitting ------------------------------------------------------------------


def search_scale(model: str) -> np.ndarray:
    """Search units per parameter: T searches as log T, the readout errors in 1e-3, frequencies and rates in 1e-2."""
    scale = {"amplitude": 1.0, "t_us": 1.0, "phi": 1.0, "e0": 1e-3, "e1": 1e-3, "a": 1.0}
    return np.array([scale.get(name, 1e-2) for name in names(model)])


def _to_search(params: np.ndarray, scale: np.ndarray) -> np.ndarray:
    search = np.array(params, dtype=float) / scale
    search[1] = math.log(params[1])
    return search


def _from_search(search: np.ndarray, scale: np.ndarray) -> np.ndarray:
    params = np.array(search, dtype=float) * scale
    params[1] = math.exp(search[1])
    return params


def _search_nll(search: np.ndarray, model: str, data: Data, scale: np.ndarray) -> float:
    return negative_log_likelihood(_from_search(search, scale), model, data)


def refine(
    model: str,
    data: Data,
    start: np.ndarray,
    fixed: dict[int, float] | None = None,
    window: dict[int, tuple[float, float]] | None = None,
) -> tuple[float, np.ndarray]:
    """Bounded L-BFGS-B from a start, restarted once from its own optimum.

    fixed pins parameters by index; window bounds parameters by index.
    """
    limits = bounds(model, data)
    for index, pair in (window or {}).items():
        limits[index] = pair
    initial = np.array(start, dtype=float)
    for index, value in (fixed or {}).items():
        initial[index] = value
        limits[index] = (value, value)
    for index, (low, high) in enumerate(limits):
        if low is not None:
            initial[index] = max(initial[index], low)
        if high is not None:
            initial[index] = min(initial[index], high)
    scale = search_scale(model)
    search_limits: list[tuple[float | None, float | None]] = []
    for index, (low, high) in enumerate(limits):
        if index == 1:
            search_limits.append((math.log(low) if low else None, math.log(high) if high else None))
        else:
            search_limits.append(
                (None if low is None else low / scale[index], None if high is None else high / scale[index])
            )
    point = _to_search(initial, scale)
    value = math.inf
    for _ in range(2):
        result = minimize(
            _search_nll,
            point,
            args=(model, data, scale),
            method="L-BFGS-B",
            bounds=search_limits,
            options={"maxiter": 4000, "ftol": 1e-15, "gtol": 1e-9},
        )
        point, value = np.asarray(result.x, dtype=float), float(result.fun)
    return value, _from_search(point, scale)


def corrected(data: Data, e0: float, e1: float) -> np.ndarray:
    """Readout-corrected true expectations of the Ramsey points at the calibration channel."""
    measured = 2.0 * data.zeros / data.shots - 1.0
    return np.asarray((measured - (e1 - e0)) / (1.0 - e0 - e1))


def pair_least_squares(
    times: np.ndarray, signal: np.ndarray, f1: np.ndarray, df: np.ndarray, t_us: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Batched complex least squares of signal (R, N) on two exponentials at every (f1, df) grid pair.

    Returns the residual (R, G) and the complex amplitudes c1, c2 (R, G).
    Each grid pair's 2 x 2 normal equations are solved in closed form, and
    every reduction runs over the last axis of an (R, G, N) array, so a
    row of a batch carries the bits of the same row solved alone.
    """
    damp = np.exp(-times / t_us)
    basis1 = damp[None, :] * np.exp(2j * math.pi * f1[:, None] * times[None, :])
    basis2 = damp[None, :] * np.exp(2j * math.pi * (f1 + df)[:, None] * times[None, :])
    g11 = np.sum(np.abs(basis1) ** 2, axis=-1)
    g22 = np.sum(np.abs(basis2) ** 2, axis=-1)
    g12 = np.sum(basis1.conj() * basis2, axis=-1)
    b1 = np.sum(basis1.conj()[None, :, :] * signal[:, None, :], axis=-1)
    b2 = np.sum(basis2.conj()[None, :, :] * signal[:, None, :], axis=-1)
    det = g11 * g22 - np.abs(g12) ** 2
    safe = np.where(det > 1e-12, det, 1.0)
    c1 = np.where(det > 1e-12, (g22 * b1 - g12 * b2) / safe, b1 / g11)
    c2 = np.where(det > 1e-12, (g11 * b2 - g12.conj() * b1) / safe, 0.0)
    fitted = c1[:, :, None] * basis1[None, :, :] + c2[:, :, None] * basis2[None, :, :]
    residual = np.sum(np.abs(signal[:, None, :] - fitted) ** 2, axis=-1)
    return residual, c1, c2


def complex_signal(data: Data, e0: float, e1: float) -> tuple[np.ndarray, np.ndarray]:
    """(times, X + i Y) of the Ramsey points; each time carries one X and one Y read."""
    values = corrected(data, e0, e1)
    times = np.unique(data.times[data.bases < 2])
    signal = np.empty(times.size, dtype=complex)
    for index, time in enumerate(times):
        at = data.times == time
        signal[index] = values[at & (data.bases == 0)][0] + 1j * values[at & (data.bases == 1)][0]
    return times, signal


def grid_frequencies(points: int) -> np.ndarray:
    return np.asarray(-0.5 * F0_MHZ + F0_MHZ * np.arange(points) / points)


class ProfilePoint:
    """static fit at fixed df from the best least-squares f1 start; module level so the pool pickles it."""

    def __init__(self, data: Data, t_us: float) -> None:
        self.data = data
        self.t_us = t_us

    def __call__(self, df: float) -> tuple[float, list[float]]:
        data = self.data
        e0, e1 = data.e0, data.e1
        times, signal = complex_signal(data, e0, e1)
        f1 = grid_frequencies(FREQUENCY_STARTS)
        residual, c1, c2 = pair_least_squares(times, signal[None, :], f1, np.full(f1.size, df), self.t_us)
        # The profiled hypothesis puts the heavier line at f1, so starts
        # whose heavier amplitude sits at f1 + df are excluded.
        ranked = np.where(np.abs(c1[0]) >= np.abs(c2[0]), residual[0], np.inf)
        best = int(np.argmin(ranked)) if np.isfinite(ranked).any() else int(np.argmin(residual[0]))
        c_heavy, c_light = complex(c1[0, best]), complex(c2[0, best])
        total = abs(c_heavy) + abs(c_light)
        weight = max(abs(c_heavy) / total, 0.5) if total > 0 else 1.0
        phase = math.atan2((c_heavy + c_light).imag, (c_heavy + c_light).real)
        start = np.array([min(total, 1.0), self.t_us, phase, e0, e1, weight, float(f1[best]), df])
        value, params = refine("static", data, start, {7: df})
        return value, [float(x) for x in params]


def profile_static(data: Data, t_us: float = 120.0) -> list[tuple[float, float, list[float]]]:
    """(df, NLL, parameters) of the static model over one relative-alias period of df."""
    grid = [float(x) for x in grid_frequencies(PROFILE_POINTS)]
    found = parallel.ordered_map(ProfilePoint(data, t_us), grid)
    return [(df, value, params) for df, (value, params) in zip(grid, found, strict=True)]


def local_minima(profile: list[tuple[float, float, list[float]]]) -> list[int]:
    """Indices of the periodic profile's strict local minima, lowest NLL first."""
    values = [row[1] for row in profile]
    size = len(values)
    found = [
        index
        for index in range(size)
        if values[index] < values[index - 1] and values[index] <= values[(index + 1) % size]
    ]
    return sorted(found, key=lambda index: values[index])


def fold(value: float) -> float:
    return math.remainder(value, F0_MHZ)


class StartRefine:
    """Free refit of a model from each of a list of starts, the lowest NLL kept; pool-picklable."""

    def __init__(self, model: str) -> None:
        self.model = model

    def __call__(self, item: tuple[Data, list[list[float]]]) -> tuple[float, list[float]]:
        data, starts = item
        return Refit()((self.model, data, starts))


class Refit:
    """(model, data, starts[, window]) -> the lowest refit over the starts; pool-picklable."""

    def __call__(self, item: tuple[Any, ...]) -> tuple[float, list[float]]:
        model, data, starts = item[:3]
        window = item[3] if len(item) > 3 else None
        found = [refine(model, data, np.array(start), window=window) for start in starts]
        value, params = min(found, key=lambda pair: pair[0])
        return value, [float(x) for x in params]


GRID_T_US = 120.0
GLOBAL_STARTS = 3


def grid_starts(signals: np.ndarray, times: np.ndarray, readout: list[tuple[float, float]]) -> tuple[list, list]:
    """Per replicate, the single and static starts of its batched least-squares grid.

    single: the GLOBAL_STARTS lowest local minima of the one-frequency
    residual over PROFILE_POINTS frequencies. static: the GLOBAL_STARTS
    lowest local minima over df of the residual minimized over
    FREQUENCY_STARTS heavier-line frequencies, with the heavier line at f1.
    """
    f_grid = grid_frequencies(PROFILE_POINTS)
    single_res, single_c, _ = pair_least_squares(times, signals, f_grid, np.zeros(f_grid.size), GRID_T_US)
    f1 = np.tile(grid_frequencies(FREQUENCY_STARTS), PROFILE_POINTS)
    df = np.repeat(f_grid, FREQUENCY_STARTS)
    pair_res, c1, c2 = pair_least_squares(times, signals, f1, df, GRID_T_US)
    heavy = np.abs(c1) >= np.abs(c2)
    ranked = np.where(heavy, pair_res, np.inf).reshape(len(signals), PROFILE_POINTS, FREQUENCY_STARTS)
    single_starts, static_starts = [], []
    for row, (e0, e1) in enumerate(readout):
        curve = single_res[row]
        minima = sorted(
            (k for k in range(curve.size) if curve[k] < curve[k - 1] and curve[k] <= curve[(k + 1) % curve.size]),
            key=lambda k: curve[k],
        )[:GLOBAL_STARTS]
        single_starts.append(
            [
                [
                    min(abs(complex(single_c[row, k])), 1.0),
                    GRID_T_US,
                    float(np.angle(single_c[row, k])),
                    e0,
                    e1,
                    float(f_grid[k]),
                ]
                for k in minima
            ]
        )
        best_f1 = np.argmin(ranked[row], axis=1)
        profile = ranked[row][np.arange(PROFILE_POINTS), best_f1]
        minima = sorted(
            (
                k
                for k in range(profile.size)
                if np.isfinite(profile[k])
                and profile[k] < profile[k - 1]
                and profile[k] <= profile[(k + 1) % profile.size]
            ),
            key=lambda k: profile[k],
        )[:GLOBAL_STARTS]
        chosen = []
        for k in minima:
            g = k * FREQUENCY_STARTS + int(best_f1[k])
            heavy_c, light_c = complex(c1[row, g]), complex(c2[row, g])
            total = abs(heavy_c) + abs(light_c)
            chosen.append(
                [
                    min(total, 1.0),
                    GRID_T_US,
                    float(np.angle(heavy_c + light_c)),
                    e0,
                    e1,
                    max(abs(heavy_c) / total, 0.5),
                    float(f1[g]),
                    float(df[g]),
                ]
            )
        static_starts.append(chosen)
    return single_starts, static_starts


def global_fits(replicates: list[Data]) -> list[dict[str, tuple[float, list[float]]]]:
    """single and static global fits of every replicate: batched grid starts, then pooled refinement."""
    starts_single: list = []
    starts_static: list = []
    for low in range(0, len(replicates), GRID_BLOCK):
        block = replicates[low : low + GRID_BLOCK]
        readout = [(d.e0, d.e1) for d in block]
        rows = [complex_signal(d, e0, e1) for d, (e0, e1) in zip(block, readout, strict=True)]
        times = rows[0][0]
        signals = np.array([row[1] for row in rows])
        single, static = grid_starts(signals, times, readout)
        starts_single += single
        starts_static += static
    single_fits = parallel.ordered_map(StartRefine("single"), list(zip(replicates, starts_single, strict=True)))
    static_fits = parallel.ordered_map(StartRefine("static"), list(zip(replicates, starts_static, strict=True)))
    return [{"single": a, "static": b} for a, b in zip(single_fits, static_fits, strict=True)]


GRID_BLOCK = 4
RATE_STARTS = (1e-4, 0.01, 0.05, 0.2)


def extend(model: str, static_params: np.ndarray, extra: float) -> np.ndarray:
    return np.concatenate([static_params, [extra]]) if model in ("telegraph", "tls") else np.array(static_params)


def rate_starts(model: str, static_params: np.ndarray) -> list[list[float]]:
    return [[float(x) for x in extend(model, static_params, rate)] for rate in RATE_STARTS]


def alias_candidates(df: float) -> list[float]:
    """Every df + n F0 inside the band |df| < BAND_MHZ, ascending."""
    low = math.ceil((-BAND_MHZ - df) / F0_MHZ)
    high = math.floor((BAND_MHZ - df) / F0_MHZ)
    return [df + n * F0_MHZ for n in range(low, high + 1)]


def alias_index(df: float, reference: float) -> int:
    return round((df - reference) / F0_MHZ)


# Information and intervals ------------------------------------------------


def fisher_information(model: str, params: np.ndarray, data: Data) -> np.ndarray:
    """Expected information of every parameter: binomial points plus the calibration counts.

    A read of p = (1 + mu) / 2 carries n / (1 - mu^2) about mu; the
    Jacobian of the measured mean is taken by central differences.
    """
    mean = measured_mean(model, params, data)
    jacobian = np.empty((data.times.size, params.size))
    for index in range(params.size):
        step = 1e-6 * max(1.0, abs(float(params[index])))
        upper, lower = params.copy(), params.copy()
        upper[index] += step
        lower[index] -= step
        jacobian[:, index] = (measured_mean(model, upper, data) - measured_mean(model, lower, data)) / (2 * step)
    information = jacobian.T @ ((data.shots / (1.0 - mean**2))[:, None] * jacobian)
    return np.asarray(information)


FIXED = ("e0", "e1")


def at_bound(model: str, params: np.ndarray, data: Data) -> list[str]:
    found = []
    for name, value, (low, high) in zip(names(model), params, bounds(model, data), strict=True):
        if name in FIXED:
            continue
        if (low is not None and abs(value - low) < 1e-6 * max(1.0, abs(low))) or (
            high is not None and abs(value - high) < 1e-6 * max(1.0, abs(high))
        ):
            found.append(name)
    return found


def wald(model: str, params: np.ndarray, data: Data) -> dict[str, Any]:
    """Wald errors of the parameters off their bounds; bounded ones read at_bound, unidentified ones None.

    The information is read in search units (search_scale, with T scaled by
    its own value), so the identifiability ratio compares directions of
    like scale rather than the units of microseconds and readout errors.
    """
    bounded = at_bound(model, params, data)
    free = [index for index, name in enumerate(names(model)) if name not in bounded and name not in FIXED]
    scale = search_scale(model)
    scale[1] = float(params[1])
    information = fisher_information(model, params, data) * np.outer(scale, scale)
    errors, condition = ramsey.wald_errors(information[np.ix_(free, free)])
    standard: dict[str, float | str | None] = {name: "fixed" if name in FIXED else "at_bound" for name in names(model)}
    for column, index in enumerate(free):
        error = errors[column]
        standard[names(model)[index]] = None if error is None else error * float(scale[index])
    return {"standard_errors": standard, "condition_number": condition, "at_bound": bounded}


# Report helpers -----------------------------------------------------------


def number(value: float, digits: int = 6) -> float:
    """value at `digits` significant digits; magnitudes below 1e-9 read 0."""
    if not math.isfinite(value):
        raise ValueError(f"non-finite value {value} in the report")
    if abs(value) < 1e-9:
        return 0.0
    return float(f"{value:.{digits}g}")


def rounded(value: Any, digits: int = 6) -> Any:
    if isinstance(value, bool) or value is None or isinstance(value, (int, str)):
        return value
    if isinstance(value, float):
        return number(value, digits)
    if isinstance(value, dict):
        return {key: rounded(item, digits) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [rounded(item, digits) for item in value]
    if isinstance(value, np.floating):
        return number(float(value), digits)
    raise TypeError(f"unserializable {type(value)}")


def parameters(model: str, params: np.ndarray) -> dict[str, float]:
    values = dict(zip(names(model), (float(x) for x in params), strict=True))
    values["phi"] = math.remainder(values["phi"], 2 * math.pi)
    for key in ("f_mhz", "f1_mhz"):
        if key in values:
            values[key] = fold(values[key])
    return values


def tls_physics(values: dict[str, float]) -> dict[str, Any]:
    fq, ft, coupling = tls_hamiltonian(values["a"], values["f1_mhz"], values["df_mhz"])
    return {
        "omega_khz": abs(values["df_mhz"]) * 1e3,
        "delta_qubit_minus_tls_khz": (fq - ft) * 1e3,
        "g_khz": coupling * 1e3,
        "swap_depth_by_population": {
            str(p): (1.0 - p) * 4.0 * values["a"] * (1.0 - values["a"]) for p in POPULATION_GRID
        },
    }


def information_criteria(nll: float, size: int, observations: float) -> dict[str, float]:
    return {"aic": 2.0 * nll + 2.0 * size, "bic": 2.0 * nll + size * math.log(observations)}


# Charge-parity band -------------------------------------------------------

# Koch et al., Phys. Rev. A 76, 042319 (2007), eq. (2.18): the charge
# dispersion of level m, eps_m = (-1)^m E_C 2^(4m+5) / m! sqrt(2/pi)
# (E_J / 2E_C)^(m/2 + 3/4) exp(-sqrt(8 E_J / E_C)); the two parities sit at
# n_g and n_g + 1/2, so f01 differs between them by |eps_1 - eps_0| |cos 2 pi n_g|.
# f01 = sqrt(8 E_J E_C) - E_C and E_C = -alpha to the same order.
PARITY_F01_GHZ = (4.5, 4.8, 5.1, 5.4)
PARITY_EC_GHZ = (0.28, 0.30, 0.32, 0.34)


def dispersion(level: int, ej: float, ec: float) -> float:
    return (
        (-1) ** level
        * ec
        * 2 ** (4 * level + 5)
        / math.factorial(level)
        * math.sqrt(2 / math.pi)
        * (ej / (2 * ec)) ** (level / 2 + 0.75)
        * math.exp(-math.sqrt(8 * ej / ec))
    )


def parity_band() -> dict[str, Any]:
    rows = []
    for f01 in PARITY_F01_GHZ:
        for ec in PARITY_EC_GHZ:
            ej = (f01 + ec) ** 2 / (8 * ec)
            rows.append(
                {
                    "f01_ghz": f01,
                    "ec_ghz": ec,
                    "ej_over_ec": ej / ec,
                    "max_splitting_khz": abs(dispersion(1, ej, ec) - dispersion(0, ej, ec)) * 1e6,
                }
            )
    splittings = [row["max_splitting_khz"] for row in rows]
    return {
        "status": "hypothetical sensitivity study: the grid spans generic fixed-frequency transmon parameters; "
        "Heron r2 properties publish no frequency or anharmonicity for 143, so no row describes 143",
        "source": "Koch et al. 2007 eq. 2.18",
        "grid": rows,
        "max_splitting_khz_range": [min(splittings), max(splittings)],
    }


# Analysis of the run ------------------------------------------------------


def shifted(params: np.ndarray, df: float) -> np.ndarray:
    moved = np.array(params, dtype=float)
    moved[7] = df
    return moved


def alias_table(data: Data, static: tuple[float, np.ndarray]) -> list[dict[str, Any]]:
    """Every relative alias of the static solution in the band, with each model's NLL there."""
    value, params = static
    candidates = alias_candidates(float(params[7]))
    items: list[tuple[str, Data, list[list[float]]]] = []
    for df in candidates:
        base = shifted(params, df)
        for model in ("telegraph", "tls"):
            items.append((model, data, rate_starts(model, base)))
    fitted = parallel.ordered_map(Refit(), items, min_items=2)
    rows = []
    for position, df in enumerate(candidates):
        base = shifted(params, df)
        telegraph = fitted[2 * position]
        tls = fitted[2 * position + 1]
        tls_values = parameters("tls", np.array(tls[1]))
        rows.append(
            {
                "n": alias_index(df, float(params[7])),
                "df_khz": df * 1e3,
                "static_delta_nll": negative_log_likelihood(base, "static", data) - value,
                "telegraph_delta_nll": telegraph[0] - value,
                "telegraph_gamma_per_us": telegraph[1][8],
                "tls_delta_nll": tls[0] - value,
                "tls_gamma_per_us": tls[1][8],
                "tls_physics": tls_physics(tls_values),
                "telegraph_params": telegraph[1],
                "tls_params": tls[1],
            }
        )
    return rows


def draw_replicates(model: str, params: np.ndarray, data: Data, count: int, rng: np.random.Generator) -> list[Data]:
    """count replicates of the run's counts under a fitted model, drawn in order."""
    probability = 0.5 * (1.0 + measured_mean(model, params, data))
    zeros = rng.binomial(data.shots.astype(np.int64)[None, :], probability[None, :], size=(count, data.shots.size))
    return [data.replicate(zeros[k].astype(float)) for k in range(count)]


def tail(statistics: list[float], observed: float) -> dict[str, Any]:
    exceed = sum(value >= observed for value in statistics)
    return {
        "replicates": len(statistics),
        "observed": observed,
        "exceeding": exceed,
        "p_value": (exceed + 1) / (len(statistics) + 1),
        "replicate_quantiles": {q: float(np.quantile(statistics, float(q))) for q in ("0.5", "0.9", "0.95", "0.99")},
        "replicate_max": max(statistics),
    }


def bootstrap(
    data: Data, single: tuple[float, np.ndarray], static: tuple[float, np.ndarray], observed: dict[str, float]
) -> dict[str, Any]:
    """Parametric-bootstrap calibration of the likelihood ratios whose chi-square law fails.

    single inside static leaves f2 unidentified at a = 1 (Davies); static
    inside telegraph sits on the boundary gamma = 0; tls and static are not
    nested. Every replicate is drawn before any fit; the single and static
    replicate fits run the batched least-squares grid and the pooled
    refinement that the observed statistic uses.
    """
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    under_single = draw_replicates("single", single[1], data, BOOTSTRAP_REPLICATES, rng)
    under_static = draw_replicates("static", static[1], data, BOOTSTRAP_REPLICATES, rng)
    fits = global_fits(under_single)
    rows = [complex_signal(d, d.e0, d.e1) for d in under_single]
    readout = [(d.e0, d.e1) for d in under_single]
    signals = np.array([row[1] for row in rows])
    batched = grid_starts(signals[:GRID_BLOCK], rows[0][0], readout[:GRID_BLOCK])
    grid_rows_equal = all(
        grid_starts(signals[k : k + 1], rows[0][0], readout[k : k + 1]) == ([batched[0][k]], [batched[1][k]])
        for k in range(GRID_BLOCK)
    )
    if not grid_rows_equal:
        raise RuntimeError("a batched grid row of the bootstrap replicates differs from the row solved alone")
    beat = [2.0 * (fit["single"][0] - fit["static"][0]) for fit in fits]
    static_fits = parallel.ordered_map(
        Refit(), [("static", replicate, [[float(x) for x in static[1]]]) for replicate in under_static]
    )
    items = []
    for replicate, (_value, params) in zip(under_static, static_fits, strict=True):
        for model in ("telegraph", "tls"):
            items.append((model, replicate, rate_starts(model, np.array(params))))
    extended = parallel.ordered_map(Refit(), items, min_items=2)
    switching = [
        2.0 * (static_fits[k][0] - min(extended[2 * k][0], static_fits[k][0])) for k in range(BOOTSTRAP_REPLICATES)
    ]
    exchange = [2.0 * (static_fits[k][0] - extended[2 * k + 1][0]) for k in range(BOOTSTRAP_REPLICATES)]
    return {
        "seed": BOOTSTRAP_SEED,
        "batched_grid_rows_equal_alone": grid_rows_equal,
        "single_vs_static_under_single": tail(beat, observed["single_vs_static"]),
        "static_vs_telegraph_under_static": tail(switching, observed["static_vs_telegraph"]),
        "static_vs_tls_under_static": tail(exchange, observed["static_vs_tls"]),
        "procedure": (
            "replicates drawn from the fitted null (points and calibration counts) before any fit; "
            "single and static refit globally (batched least-squares grid, pooled L-BFGS-B); "
            "telegraph and tls refit from the replicate's static fit at every RATE_STARTS rate"
        ),
    }


# Follow-up design ---------------------------------------------------------

# Designs as (basis, delay_dt) members at one shot count per PUB (runtime
# 0.48 deprecates differing pub.shots). The coprime lattices 693 = 11 x 63
# and 819 = 13 x 63 dt share gcd 63 dt = 0.252 us, so a complex (X, Y) read
# leaves frequencies unaliased over 1 / 0.252 us = 3.97 MHz, twice BAND_MHZ.
COPRIME_DT = (693, 819)
COPRIME_COUNTS = (12, 10)
LONG_DT = (15000, 30000, 60000, 90000)
DENSE_STEP_DT = 63
DENSE_COUNT = 140
TELEGRAPH_PROBES = (0.01, 0.03, 0.1)
# Herald-backaction controls: the same X and Y reads with no initialization
# herald, and with a fixed idle after the herald before the preparation, at
# a subset of the coprime delays. A beat that survives both arms unchanged
# is intrinsic to 143; one that moves with them follows the herald.
CONTROL_DT = (0, 2457, 4095, 6237, 8190)
POST_HERALD_IDLE_DT = 2000
PAIRED = (
    "X and Y (and Z) of each delay run as adjacent entries of one PUB's parameter sweep, so both quadratures of "
    "a delay share the PUB's shot interleaving and no inter-PUB drift separates them"
)


def coprime_delays() -> list[int]:
    return sorted({step * k for step, count in zip(COPRIME_DT, COPRIME_COUNTS, strict=True) for k in range(count + 1)})


def designs() -> dict[str, dict[str, Any]]:
    coprime = coprime_delays()
    ramsey_coprime = [(basis, delay) for delay in coprime for basis in ("x", "y")]
    swap = [("z", delay) for delay in coprime]
    long_block = [(basis, delay) for delay in LONG_DT for basis in ("x", "y", "z")]
    # Cost members of the controls: the no-herald arm at the base duration
    # (an upper bound, since it drops the herald) and the idle arm with its
    # fixed post-herald idle added to the delay.
    controls = [(basis, delay) for delay in CONTROL_DT for basis in ("x", "y")] + [
        (basis, delay + POST_HERALD_IDLE_DT) for delay in CONTROL_DT for basis in ("x", "y")
    ]
    return {
        "run_lattice": {
            "members": [(basis, WINDOW_DT * k) for k in range(7) for basis in ("x", "y")],
            "shots": 12288,
            "purpose": "the retained run's lattice, the reference whose relative aliases tie",
            "pairing": "retained: X and Y of a delay in separate PUBs of one job, in an execution order the "
            "service does not guarantee",
        },
        "dense": {
            "members": [(basis, DENSE_STEP_DT * k) for k in range(DENSE_COUNT + 1) for basis in ("x", "y")],
            "shots": 512,
            "purpose": "uniform 0.252 us complex Ramsey grid to 35.3 us",
            "pairing": PAIRED,
        },
        "coprime_swap": {
            "members": ramsey_coprime + swap,
            "shots": 2048,
            "purpose": "693 and 819 dt lattices (gcd 63 dt) in X and Y, plus Z after an X preparation (TLS swap), "
            "plus the no-herald and post-herald-idle control arms",
            "pairing": PAIRED,
            "controls": controls,
        },
        "coprime_swap_long": {
            "members": ramsey_coprime + swap + long_block,
            "shots": 2048,
            "purpose": "coprime_swap plus X, Y and Z at 60, 120, 240 and 360 us for the envelope and slow switching",
            "pairing": PAIRED,
            "controls": controls,
        },
    }


def design_data(members: list[tuple[str, int]], shots: int, template: Data) -> Data:
    times = np.array([delay * DT_US for _basis, delay in members])
    bases = np.array([("x", "y", "z").index(basis) for basis, _delay in members])
    return Data(
        times,
        bases,
        np.zeros(len(members)),
        np.full(len(members), float(shots)),
        template.e0,
        template.e1,
        template.t1_us,
    )


def asimov(model: str, params: np.ndarray, design: Data) -> Data:
    """Expected zero counts n p of a design under a model."""
    probability = 0.5 * (1.0 + measured_mean(model, params, design))
    return design.replicate(design.shots * probability)


class ExpectedLLR:
    """Expected log-likelihood ratio of a truth against the best alternative on a design; pool-picklable.

    On the Asimov counts the truth's NLL is the minimum over every
    parameter of its own model, so the alternative's minimum minus it is
    the summed binomial Kullback-Leibler divergence n KL(p_truth || p_alt)
    at the closest alternative: the mean log-likelihood ratio a run of
    the design draws.
    """

    def __call__(self, item: tuple[Any, ...]) -> float:
        truth_model, truth, alternative, starts, design = item[:5]
        window = item[5] if len(item) > 5 else None
        expected = asimov(truth_model, np.array(truth), design)
        own = negative_log_likelihood(np.array(truth), truth_model, expected)
        best, _params = Refit()((alternative, expected, starts, window))
        return max(best - own, 0.0)


def billed_seconds(members: list[tuple[str, int]], shots: int, base_dt: int) -> dict[str, float]:
    """The cost rule and the execution-time rule of a design's one job.

    rule: JOB_OVERHEAD_S + shots x (rep_delay + INIT/FINI + duration) per
    member; execution: shots x (rep_delay + duration), the retained run's
    circuits_execution_time measure, to which its charge added a fixed
    overhead.
    """
    durations = [(base_dt + delay) * DT_US for _basis, delay in members]
    execution = sum(shots * (REP_DELAY_US + duration) for duration in durations) * 1e-6
    rule = JOB_OVERHEAD_S + sum(shots * (REP_DELAY_US + INIT_FINI_US + d) for d in durations) * 1e-6
    return {"rule_s": rule, "execution_s": execution}


def evaluate_designs(
    data: Data, static: tuple[float, np.ndarray], aliases: list[dict[str, Any]], base_dt: int, charge_offset_s: float
) -> dict[str, Any]:
    """Per design: cost, expected alias separation, model-class separation and Fisher precision."""
    _value, params = static
    reference = float(params[7])
    alias_df = [row["df_khz"] * 1e-3 for row in aliases]
    tls_best = min(aliases, key=lambda row: row["tls_delta_nll"])
    tls_params = tls_best["tls_params"]
    results: dict[str, Any] = {}
    for label, spec in designs().items():
        design = design_data(spec["members"], spec["shots"], data)
        items: list[tuple[Any, ...]] = []
        pairs = []
        for df in alias_df:
            truth = [float(x) for x in shifted(params, df)]
            for other in alias_df:
                if other != df:
                    # The alternative's df stays inside its own alias cell,
                    # so the ratio measures separation from that alias and
                    # never a refit that drifts back to the truth's.
                    cell = {7: (other - 0.5 * F0_MHZ, other + 0.5 * F0_MHZ)}
                    start = [[float(x) for x in shifted(params, other)]]
                    items.append(("static", truth, "static", start, design, cell))
                    pairs.append((alias_index(df, reference), alias_index(other, reference)))
        static_start = [[float(x) for x in shifted(params, tls_params[7])]]
        for population in POPULATION_GRID:
            at_p = design.at_population(population)
            items.append(("tls", tls_params, "static", static_start, at_p))
            items.append(("static", static_start[0], "tls", [tls_params], at_p))
        for rate in TELEGRAPH_PROBES:
            best_static = [[float(x) for x in params]]
            items.append(("telegraph", [*best_static[0], rate], "static", best_static, design))
        found = parallel.ordered_map(ExpectedLLR(), items, min_items=2)
        alias_rows = [
            {"truth_n": a, "alternative_n": b, "expected_llr": v} for (a, b), v in zip(pairs, found, strict=False)
        ]
        tail_values = found[len(pairs) :]
        grid = len(POPULATION_GRID)
        tls_vs_static = tail_values[0 : 2 * grid : 2]
        static_vs_tls = tail_values[1 : 2 * grid : 2]
        telegraph_values = tail_values[2 * grid :]
        worst = min(alias_rows, key=lambda row: row["expected_llr"])
        precision = wald("static", np.array(params), design)["standard_errors"]
        cost = billed_seconds(spec["members"] + spec.get("controls", []), spec["shots"], base_dt)
        results[label] = {
            "purpose": spec["purpose"],
            "members": len(spec["members"]),
            "shots_per_member": spec["shots"],
            "delays_dt": sorted({delay for _basis, delay in spec["members"]}),
            "bases": sorted({basis for basis, _delay in spec["members"]}),
            "billed_rule_s": cost["rule_s"],
            "controls_billed_rule_s": (
                billed_seconds(spec["controls"], spec["shots"], base_dt)["rule_s"] - JOB_OVERHEAD_S
                if spec.get("controls")
                else 0.0
            ),
            "billed_execution_plus_run_offset_s": cost["execution_s"] + charge_offset_s,
            "alias_pair_llr": alias_rows,
            "worst_alias_pair": worst,
            "worst_alias_log10_posterior_odds": -worst["expected_llr"] / math.log(10.0),
            "pairing": spec["pairing"],
            "herald_controls": len(spec.get("controls", [])),
            "tls_truth_vs_static_llr_by_population": dict(
                zip((str(p) for p in POPULATION_GRID), tls_vs_static, strict=True)
            ),
            "static_truth_vs_tls_llr_by_population": dict(
                zip((str(p) for p in POPULATION_GRID), static_vs_tls, strict=True)
            ),
            "tls_truth_vs_static_llr": min(tls_vs_static),
            "static_truth_vs_tls_llr": min(static_vs_tls),
            "telegraph_truth_vs_static_llr": dict(
                zip((str(r) for r in TELEGRAPH_PROBES), telegraph_values, strict=True)
            ),
            "static_wald_at_fit": {key: precision[key] for key in ("a", "f1_mhz", "df_mhz", "t_us")},
        }
    return results


# Expected log-likelihood ratio a design must reach for every separation it
# targets: posterior odds of exp(-50) against the competitor at equal priors.
SEPARATION_LLR = 50.0


def recommend(results: dict[str, Any]) -> str:
    """Cheapest design with herald controls whose worst separations (TLS p over POPULATION_GRID) reach the target."""
    eligible = [
        label
        for label, row in results.items()
        if row["herald_controls"] > 0
        and min(row["worst_alias_pair"]["expected_llr"], row["tls_truth_vs_static_llr"], row["static_truth_vs_tls_llr"])
        >= SEPARATION_LLR
    ]
    if not eligible:
        raise RuntimeError("no design reaches the separation target")
    return min(eligible, key=lambda label: results[label]["billed_rule_s"])


def repeat_plan(design: str, cost: float) -> dict[str, Any]:
    return {
        "design": design,
        "repeats": 4,
        "spacing": "at least 60 min apart; the repeats are time-separated. A pair counts as two calibration "
        "cycles only when the execution-start calibration each run records (properties at execution) differs in "
        "identity and in 143's values; parameter monitoring runs about hourly and recalibrates only on a deviation "
        "(docs/notes/ibm_quantum/calibration-jobs.md), so 60 min alone does not guarantee a new calibration",
        "billed_rule_s_total": 4 * cost,
        "per_repeat_fit": "static, telegraph and tls at the resolved alias; record a, df, f1, g, Delta per repeat",
        "discriminators": {
            "charge_parity": "a near the same value in every repeat (1/2 at equal parity occupation) while df "
            "moves with the offset charge n_g; Z after X shows T1 decay without swap",
            "tls_exchange": "g = |df| sqrt(a (1 - a)) constant across repeats while Delta = df (2a - 1) and a wander "
            "with the TLS frequency; Z after X shows swap oscillation at Omega = |df| with depth "
            "(1 - p) 4 a (1 - a), absent only for a TLS held excited (p = 1)",
            "static_unexplained": "a, df and f1 constant across repeats and no Z swap",
        },
        "homogeneity_test": "chi-square of each per-repeat estimate against its inverse-variance mean "
        "(3 degrees of freedom for 4 repeats), at the family alpha of the follow-up case",
    }


# Report -------------------------------------------------------------------


def basis_alone(data: Data, static: tuple[float, np.ndarray]) -> dict[str, Any]:
    """single and static fitted to X alone and to Y alone, so no X/Y pairing across PUBs enters.

    One quadrature reads A e^(-t/T) times the cosine (X) or sine (Y) of the
    phase; a single damped sinusoid has 4 free parameters on 7 points, the
    static mixture 6. Its deviance against the saturated fit is chi-square
    with 3 degrees of freedom when one damped sinusoid describes the basis.
    """
    result: dict[str, Any] = {}
    for basis, label in ((0, "x"), (1, "y")):
        sub = data.subset(data.bases == basis)
        single_starts = [
            [0.9, 60.0, phase, data.e0, data.e1, float(f)]
            for f in grid_frequencies(FREQUENCY_STARTS)
            for phase in (0.0, math.pi / 2)
        ]
        static_starts = [[float(x) for x in static[1]]]
        single, static_fit = parallel.ordered_map(
            Refit(), [("single", sub, single_starts), ("static", sub, static_starts)], min_items=2
        )
        saturated = saturated_nll(sub)
        deviance = 2.0 * (single[0] - saturated)
        free = sub.times.size - 4
        result[label] = {
            "points": int(sub.times.size),
            "single_deviance": deviance,
            "single_degrees_of_freedom": free,
            "single_p_value": float(chi2.sf(deviance, free)),
            "static_deviance": 2.0 * (static_fit[0] - saturated),
            "static_degrees_of_freedom": sub.times.size - 6,
            "single_vs_static_lr": 2.0 * (single[0] - static_fit[0]),
        }
    return result


def run_costs(run: Path, exposures: list[int]) -> dict[str, Any]:
    """The run's base circuit duration (circuit_duration minus exposure) and its charge against both cost rules."""
    (job,) = sorted(path for path in (run / "raw").iterdir() if path.is_dir())
    metrics = json.loads((job / "job_metrics.json").read_text())
    bases = set()
    durations = []
    for path in sorted(job.glob("pub_*.json")):
        payload = json.loads(path.read_text())
        durations.append(int(payload["metadata"]["compilation"]["scheduler_timing"]["circuit_duration"]))
    names_in_order = [member["name"] for member in rca._group(run)["members"]]
    schedules, _control, _unresolved = ramsey.run_schedules(run)
    for name, duration in zip(names_in_order, durations, strict=True):
        bases.add(duration - int(schedules[name]["exposure_dt"]))
    if len(bases) != 1:
        raise RuntimeError(f"{run}: members carry base durations {sorted(bases)}")
    (base,) = bases
    shots = int(json.loads((run / "record.json").read_text())["shots"])
    members = [("x", int(schedules[name]["exposure_dt"])) for name in names_in_order]
    cost = billed_seconds(members, shots, base)
    charged = float(metrics["usage"]["qpu_charge_time_seconds"])
    execution = float(metrics["circuits_execution_time_ns"]) * 1e-9
    return {
        "base_duration_dt": base,
        "shots": shots,
        "qpu_charge_time_s": charged,
        "circuits_execution_time_s": execution,
        "rule_s": cost["rule_s"],
        "execution_rule_s": cost["execution_s"],
        "charge_minus_execution_s": charged - execution,
        "exposures_dt": exposures,
    }


def comparison(data: Data, fits: dict[str, tuple[float, np.ndarray]]) -> dict[str, Any]:
    observations = float(data.shots.sum())
    saturated = saturated_nll(data)
    rows = {}
    for model, (value, _params) in fits.items():
        size = len(names(model)) - len(FIXED)
        rows[model] = {
            "parameters": size,
            "negative_log_likelihood": value,
            "deviance_vs_saturated": 2.0 * (value - saturated),
            "degrees_of_freedom": data.times.size - size,
            **information_criteria(value, size, observations),
        }
    best_aic = min(row["aic"] for row in rows.values())
    best_bic = min(row["bic"] for row in rows.values())
    for row in rows.values():
        row["delta_aic"] = row["aic"] - best_aic
        row["delta_bic"] = row["bic"] - best_bic
    return {"bic_observations": observations, "models": rows}


def report(run: Path) -> dict[str, Any]:
    data, source = run_data(run)
    (fast,) = global_fits([data])
    single_fit, static_fit = fast["single"], fast["static"]
    single = (single_fit[0], np.array(single_fit[1]))
    profile = profile_static(data)
    minima = local_minima(profile)
    profiled = min(profile, key=lambda row: row[1])
    refined = refine("static", data, np.array(profiled[2]))
    static = min([refined, (static_fit[0], np.array(static_fit[1]))], key=lambda pair: pair[0])
    static_params = np.array(static[1])
    static_params[7] = fold(static_params[7])
    static = (negative_log_likelihood(static_params, "static", data), static_params)
    mirror = ProfilePoint(data, GRID_T_US)(fold(-float(static_params[7])))
    # The lowest profile minimum outside the fitted residue class.
    other_minimum = min(
        (k for k in minima if abs(fold(profile[k][0] - float(static_params[7]))) > 2.0 * F0_MHZ / PROFILE_POINTS),
        key=lambda k: profile[k][1],
    )
    aliases = alias_table(data, static)
    # The bootstrap refits each replicate at its own static alias, so the
    # observed statistics it calibrates are read at n = 0.
    (static_alias,) = [row for row in aliases if row["n"] == 0]
    telegraph_row = min(aliases, key=lambda row: row["telegraph_delta_nll"])
    tls_row = min(aliases, key=lambda row: row["tls_delta_nll"])
    telegraph = (static[0] + telegraph_row["telegraph_delta_nll"], np.array(telegraph_row["telegraph_params"]))
    tls = (static[0] + tls_row["tls_delta_nll"], np.array(tls_row["tls_params"]))
    fits = {"single": single, "static": static, "telegraph": telegraph, "tls": tls}
    observed = {
        "single_vs_static": 2.0 * (single[0] - static[0]),
        "static_vs_telegraph": 2.0 * (static[0] - min(static_alias["telegraph_delta_nll"] + static[0], static[0])),
        "static_vs_tls": 2.0 * (static[0] - min(static_alias["tls_delta_nll"] + static[0], static[0])),
        "static_vs_telegraph_best_alias": 2.0 * (static[0] - min(telegraph[0], static[0])),
        "static_vs_tls_best_alias": 2.0 * (static[0] - min(tls[0], static[0])),
    }
    costs = run_costs(run, source["exposure_dt"])
    calibrated = bootstrap(data, single, static, observed)
    design = evaluate_designs(data, static, aliases, costs["base_duration_dt"], costs["charge_minus_execution_s"])
    recommended = recommend(design)
    a_value = float(static_params[5])
    a_error = wald("static", static_params, data)["standard_errors"]["a"]
    output = {
        "schema_version": SCHEMA,
        "status": "descriptive: post hoc models of the preregistered sweep, outside its preregistration",
        "run": run.name,
        "source": source,
        "lattice": {
            "t0_dt": WINDOW_DT,
            "t0_us": T0_US,
            "f0_khz": F0_MHZ * 1e3,
            "band_mhz": BAND_MHZ,
            "common_mode": "every frequency shifted by n f0 predicts the same counts in every model (exact)",
            "relative_single_static": "df shifted by n f0 predicts the same counts in single and static (exact)",
            "relative_telegraph_tls": "df shifted by n f0 changes the prediction only through the dissipative "
            "mixing of the two lines (rate gamma or gamma_tls) and the swap readout",
        },
        "models": {
            model: {
                "description": DESCRIPTIONS[model],
                "parameter_names": list(names(model)),
                "estimates": parameters(model, params),
                **wald(model, params, data),
            }
            for model, (_value, params) in fits.items()
        },
        "tls_population": "unidentified: a two-level qubit's Ramsey coherence is independent of the TLS thermal "
        "population p (self-check tls); the fits read p = 0, and every follow-up separation that uses the Z swap "
        "takes its worst case over POPULATION_GRID",
        "tls_physics_at_best": tls_physics(parameters("tls", tls[1])),
        "static_profile": {
            "df_khz": [row[0] * 1e3 for row in profile],
            "delta_nll": [row[1] - static[0] for row in profile],
            "local_minima_khz": [profile[k][0] * 1e3 for k in minima[:6]],
            "local_minima_delta_nll": [profile[k][1] - static[0] for k in minima[:6]],
        },
        "residue_class": {
            "df_khz": float(static_params[7]) * 1e3,
            "mirror_df_khz": fold(-float(static_params[7])) * 1e3,
            "mirror_delta_nll": mirror[0] - static[0],
            "best_other_minimum_df_khz": profile[other_minimum][0] * 1e3,
            "best_other_minimum_delta_nll": profile[other_minimum][1] - static[0],
            "reading": "X and Y fix the residue class of df modulo f0, not its sign: the class of -df "
            "(the visibility-only twin) refits worse by mirror_delta_nll, while the aliases df + n f0 of "
            "either sign tie; every magnitude |df| of the visibility-only fit stays, each with one sign",
        },
        "aliases": [
            {key: value for key, value in row.items() if key not in ("telegraph_params", "tls_params")}
            for row in aliases
        ],
        "basis_alone": basis_alone(data, static),
        "parity_band": parity_band(),
        "equal_parity_occupation": {
            "a": a_value,
            "wald_error": a_error,
            "z_from_half": (a_value - 0.5) / a_error if isinstance(a_error, float) and a_error > 0 else None,
        },
        "comparison": comparison(data, fits),
        "likelihood_ratios": observed,
        "bootstrap": calibrated,
        "run_cost": costs,
        "follow_up": {
            "status": "descriptive design data; live_run and the planner carry no delay-member builder for it",
            "designs": design,
            "selection_rule": f"cheapest design whose worst alias-pair, tls-versus-static and "
            f"static-versus-tls expected log-likelihood ratios all reach {SEPARATION_LLR}",
            "recommended": recommended,
            "repeat_plan": repeat_plan(recommended, design[recommended]["billed_rule_s"]),
        },
    }
    return rounded(output)


def serialize(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


# Self-check ---------------------------------------------------------------

PLANT_STATIC = np.array([0.98, 130.0, -0.03, 0.0025, 0.0085, 0.65, 0.025, -0.09])
PLANT_SINGLE = np.array([0.97, 40.0, 0.1, 0.0025, 0.0085, 0.03])
PLANT_T1_US = 112.0


def _plant_data(model: str, params: np.ndarray) -> Data:
    members = designs()["run_lattice"]["members"]
    template = Data(np.zeros(1), np.zeros(1), np.zeros(1), np.ones(1), 0.0025, 0.0085, PLANT_T1_US)
    return asimov(model, params, design_data(members, 12288, template))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(f"self-check: {message}")


def _check_recovery() -> dict[str, Any]:
    """Asimov plants on the run's lattice: the global fits recover each truth up to its exact aliases."""
    static_data = _plant_data("static", PLANT_STATIC)
    single_data = _plant_data("single", PLANT_SINGLE)
    fits = global_fits([static_data, single_data])
    static = np.array(fits[0]["static"][1])
    single = np.array(fits[1]["single"][1])
    df_error = abs(fold(static[7] - PLANT_STATIC[7]))
    _require(df_error < 1e-4, f"static plant df recovered to {df_error} MHz modulo f0")
    _require(abs(static[5] - PLANT_STATIC[5]) < 2e-3, f"static plant a recovered as {static[5]}")
    _require(abs(fold(single[5] - PLANT_SINGLE[5])) < 1e-4, f"single plant f recovered as {single[5]}")
    return {"static_df_error_mhz": df_error, "static_a": float(static[5]), "single_f_mhz": float(single[5])}


def _check_aliases() -> dict[str, Any]:
    """Exact relative and common-mode aliases of static on the lattice; telegraph breaks the relative one."""
    data = _plant_data("static", PLANT_STATIC)
    base = negative_log_likelihood(PLANT_STATIC, "static", data)
    candidates = alias_candidates(float(PLANT_STATIC[7]))
    expected = math.floor((BAND_MHZ - PLANT_STATIC[7]) / F0_MHZ) - math.ceil((-BAND_MHZ - PLANT_STATIC[7]) / F0_MHZ) + 1
    _require(len(candidates) == expected, f"{len(candidates)} aliases enumerated, {expected} expected")
    _require(all(abs(df) < BAND_MHZ for df in candidates), "an alias outside the band")
    relative = max(abs(negative_log_likelihood(shifted(PLANT_STATIC, df), "static", data) - base) for df in candidates)
    common = PLANT_STATIC.copy()
    common[6] += 3 * F0_MHZ
    common_gap = abs(negative_log_likelihood(common, "static", data) - base)
    _require(relative < 1e-6 and common_gap < 1e-6, f"static aliases differ by {relative}, {common_gap}")
    switching = np.concatenate([PLANT_STATIC, [0.05]])
    moved = switching.copy()
    moved[7] += F0_MHZ
    broken = abs(
        negative_log_likelihood(moved, "telegraph", data) - negative_log_likelihood(switching, "telegraph", data)
    )
    _require(broken > 1e-3, f"telegraph relative alias held to {broken}")
    shift = switching.copy()
    shift[6] += F0_MHZ
    held = abs(
        negative_log_likelihood(shift, "telegraph", data) - negative_log_likelihood(switching, "telegraph", data)
    )
    _require(held < 1e-6, f"telegraph common-mode alias broke by {held}")
    return {
        "aliases_in_band": len(candidates),
        "static_relative_gap": relative,
        "static_common_gap": common_gap,
        "telegraph_relative_gap": broken,
        "telegraph_common_gap": held,
    }


def _check_telegraph_limits() -> dict[str, float]:
    """gamma -> 0 returns the static mixture; gamma >> 2 pi df narrows to the mean line (Kubo-Anderson)."""
    times = np.linspace(0.0, 20.0, 41)
    a, f1, df = 0.65, 0.025, -0.09
    static = a * np.exp(2j * math.pi * f1 * times) + (1 - a) * np.exp(2j * math.pi * (f1 + df) * times)
    slow = float(np.abs(telegraph_kernel(a, f1, df, 0.0, times) - static).max())
    gamma = 1e3
    mean = a * f1 + (1 - a) * (f1 + df)
    narrowed = np.exp(2j * math.pi * mean * times - a * (1 - a) * (2 * math.pi * df) ** 2 * times / gamma)
    fast = float(np.abs(telegraph_kernel(a, f1, df, gamma, times) - narrowed).max())
    _require(slow < 1e-12, f"telegraph at gamma 0 departs from static by {slow}")
    _require(fast < 1e-3, f"telegraph at gamma {gamma} departs from motional narrowing by {fast}")
    return {"gamma_zero_gap": slow, "motional_narrowing_gap": fast}


def _check_tls() -> dict[str, float]:
    """Closed exchange pair: the static two-line law, p-independence, the swap depth and the three-level shift."""
    times = np.linspace(0.0, 20.0, 81)
    a, f1, df = 0.65, 0.025, -0.09
    fq, ft, coupling = tls_hamiltonian(a, f1, df)
    lines = a * np.exp(2j * math.pi * f1 * times) + (1 - a) * np.exp(2j * math.pi * (f1 + df) * times)
    huge = 1e12
    cold = tls_signal(fq, ft, coupling, huge, huge, 0.0, 0.0, times)
    warm = tls_signal(fq, ft, coupling, huge, huge, 0.0, 0.3, times)
    law = float(np.abs(cold - lines).max())
    population = float(np.abs(warm - cold).max())
    fine = np.linspace(0.0, 1.0 / abs(df), 401)
    swap = np.real(tls_signal(fq, ft, coupling, huge, huge, 0.0, 0.0, fine, basis="z"))
    depth = float((swap.max() - swap.min()) / 2.0)
    cold3 = tls_signal(fq, ft, coupling, huge, huge, 0.0, 0.0, times, levels=3)
    warm3 = tls_signal(fq, ft, coupling, huge, huge, 0.0, 0.3, times, levels=3)
    _require(law < 1e-9, f"closed tls departs from the two-line law by {law}")
    _require(population < 1e-9, f"tls Ramsey signal moves with p by {population}")
    _require(abs(depth - 4 * a * (1 - a)) < 1e-3, f"swap depth {depth}, expected {4 * a * (1 - a)}")
    half = np.real(tls_signal(fq, ft, coupling, huge, huge, 0.0, 0.5, fine, basis="z"))
    half_depth = float((half.max() - half.min()) / 2.0)
    _require(abs(half_depth - 0.5 * 4 * a * (1 - a)) < 1e-3, f"swap depth at p = 1/2 reads {half_depth}")
    _require(float(np.abs(cold3 - cold).max()) < 1e-9, "three-level cold tls departs from two-level")
    return {
        "two_line_gap": law,
        "population_gap": population,
        "swap_depth": depth,
        "swap_depth_half_population": half_depth,
        "three_level_cold_gap": float(np.abs(cold3 - cold).max()),
        "three_level_warm_shift": float(np.abs(warm3 - warm).max()),
    }


def _check_batched_grid() -> dict[str, bool]:
    """Each row of a batched least-squares grid carries the bits of the same row solved alone."""
    rng = np.random.default_rng(7)
    data = _plant_data("static", PLANT_STATIC)
    replicates = draw_replicates("static", PLANT_STATIC, data, 3, rng)
    rows = [complex_signal(d, d.e0, d.e1) for d in replicates]
    times = rows[0][0]
    signals = np.array([row[1] for row in rows])
    f1 = np.tile(grid_frequencies(8), 16)
    df = np.repeat(grid_frequencies(16), 8)
    batch = pair_least_squares(times, signals, f1, df, GRID_T_US)
    equal = True
    for k in range(len(rows)):
        alone = pair_least_squares(times, signals[k : k + 1], f1, df, GRID_T_US)
        equal &= all(np.array_equal(b[k], s[0]) for b, s in zip(batch, alone, strict=True))
    readout = [(d.e0, d.e1) for d in replicates]
    starts = grid_starts(signals, times, readout)
    alone_starts = [grid_starts(signals[k : k + 1], times, readout[k : k + 1]) for k in range(len(rows))]
    same = all(
        starts[0][k] == alone_starts[k][0][0] and starts[1][k] == alone_starts[k][1][0] for k in range(len(rows))
    )
    _require(equal and same, "a batched grid row differs from the row solved alone")
    return {"rows_equal": equal, "starts_equal": same}


def self_check() -> dict[str, Any]:
    return {
        "recovery": _check_recovery(),
        "aliases": _check_aliases(),
        "telegraph_limits": _check_telegraph_limits(),
        "tls": _check_tls(),
        "batched_grid": _check_batched_grid(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("run", type=Path, nargs="?")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--self-check", action="store_true")
    parser.add_argument("--check", action="store_true", help=f"regenerate RUN_DIR/{RETAINED} and require equal bytes")
    arguments = parser.parse_args(argv)
    if arguments.self_check:
        print(json.dumps(rounded(self_check()), indent=2, sort_keys=True))
        return 0
    if arguments.run is None:
        parser.error("a run directory is required")
    produced = serialize(report(arguments.run))
    if arguments.check:
        retained = arguments.run / RETAINED
        if retained.read_text() != produced:
            raise SystemExit(f"{retained} differs from the report its archived raw files regenerate")
        print(f"{retained}: regenerated byte for byte")
        return 0
    if arguments.out:
        arguments.out.write_text(produced)
    else:
        print(produced, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
