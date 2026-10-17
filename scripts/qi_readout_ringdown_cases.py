"""Post-readout frequency shift of every Tuna-17 qubit from a mid-circuit readout and a pre-delay ladder.

A dispersive readout drives the qubit's readout resonator; photons left in
it after the 800 ns measurement shift the qubit frequency by the AC Stark
shift 2 chi n(t), and n(t) decays at the resonator ring-down rate. Two
hypotheses separate by how the Ramsey rate of a qubit read mid-circuit
depends on the delay tau between the end of that readout and the Ramsey
sequence: a residual-photon tail (H2) adds S exp(-t / T) to the frequency t
after the readout ends, so the rate offset against an unread reference decays
with tau; a static detuning (H1) gives every tau the reference's rate.

Targets are one part of Tuna-17's bipartite coupling graph
(qi_coupler_zz_map.parts), so no two targets are coupled; the other part
holds the spectators, which stay in |0> and are read at the end only to
herald their excitation. Every neighbor of a target is a spectator in |0>, so
the parked-coupler ZZ adds one static rate to every arm of that target. The
series with part P as targets comes first and part Q is its role swap.

Circuit (cQASM 3.0, Tuna gate set, bit register of 2 n bits): readout arm tau
runs `barrier q`, `b[n + t] = measure q[t]` on every target t, `barrier q`,
then wait(tau), X90, wait(d), X90 (quadrature X, P1 = (1 + cos phi)/2) or
Y90 (quadrature Y, P1 = (1 + sin phi)/2), and wait(SETTLE_CYCLES) on every
target, then `barrier q` and `b[0:n-1] = measure q`. The reference arm puts
wait(40), the 800 ns readout length, in place of the mid-circuit
measurement. The barrier before the mid-circuit layer keeps the readouts
parallel, since Tuna's scheduler places multi-qubit measurements like any
other operation; the barrier after it ends every readout at cycle 40.
OpenSquirrel schedules each barrier domain as late as possible, and all
targets of a circuit carry one program, so the first X90 sits at cycle
40 + tau and the second gate at 40 + tau + d + 1 in every arm (--conformance
asserts these cycles). b[q] holds qubit q's final outcome, qubit 0 at the
rightmost character; b[n + t] holds target t's mid-circuit outcome.

SETTLE_CYCLES = 100 (2 us) separates the final readout from the mid-circuit
one: photons still in the resonator would otherwise change the final
readout's assignment in the short-tau, short-d circuits only, a bias of the
same exp(-tau / T) shape as H2 that the unread reference cannot cancel. A
ring-down of 500 ns leaves exp(-4) of its photons after 2 us. The
calibration circuits wait SETTLE_CYCLES before their readout too, so the
inverted assignment channel absorbs relaxation during the wait.

Every rate comes from all shots of a circuit. A target that the
mid-circuit readout leaves in |1> with probability eps runs the same
single-qubit unitary U as one left in |0>, and |<1|U|1>|^2 = |<0|U|0>|^2 for
every U in SU(2), so both quadratures read P1 = eps + (1 - 2 eps) p0: after
readout correction x and y scale by (1 - 2 eps), the visibility shrinks by
that factor, and the phase, every rate and every delta(tau) stay unbiased,
whatever eps is on each arm. QX, local and remote, returns its measurement
register: n characters ordered by qubit index, each qubit's last outcome, so
b[n + t] never reaches its result (docs/notes/quantum_inspire/qx-runs.md).
--analyze reads the final outcomes by qubit index from n or 2 n characters
and refuses any other width. Where 2 n characters return, it also reports the
estimate postselected on mid-circuit outcome 0, the postselected fraction,
and each delta's postselected-minus-all difference with standard error
sqrt(se_post^2 - se_all^2), the variance of a subset estimate's difference
from the full-sample estimate that contains it; a difference beyond its
error falsifies the invariance on that backend.

Rates come from the two delays DELAYS = (2, 77) cycles:
nu = wrap(phi(d2) - phi(d1)) / (d2 - d1), so each arm's fixed phase
(preparation, gate errors, readout rotation) cancels. The offset is taken on
the circle, delta(tau) = wrap(dphi(tau) - dphi(ref)) / (d2 - d1), so
|delta| / 2 pi < 1 / (2 x 75 x 20 ns) = 333 kHz is unambiguous whatever the
static detuning. With gates at cycle starts the qubit precesses from tau to
tau + d + 1 cycles after its readout ends, so under H2
delta(tau) = A exp(-tau / T) with A = S g(T),
g(T) = T (exp(-(d1 + 1) / T) - exp(-(d2 + 1) / T)) / (d2 - d1); d1 = 2
keeps the start of the tail inside the idle, where a d1 of several T would
put the tail into both delays' fixed phase and cancel it. d2 = 77 (1.54 us)
stays below the 2 us idle at which the coupler map kept visibility above 0.75
on 13 of 17 qubits; at visibility 0.8 and 8192 shots a delta carries about
3 kHz of shot-noise standard error.

The fit takes the six rates of a target (reference and five taus) with their
delta-method errors as independent observations. H1: every rate equals c
(5 degrees of freedom). H2: the reference rate is c and rate tau is
c + A exp(-tau / T) with T in T_BOUNDS = [5, 100] cycles, the ladder's
nonzero span (3 degrees of freedom). Fitting c makes the shared reference
enter both chi-squares exactly. T runs over a fixed geometric grid refined by
golden section, with (c, A) in closed form at each T, so a replay reproduces
the fit bytes. se(A) comes from the Fisher matrix of (c, A, T), or of (c, A)
with T at a bound. The analysis also reports the readout-end shift
S = A / g(T). A static offset of every readout arm fits as H2 with T at its
upper bound, which the rule classifies as an offset.

Decision rule, fixed before any data (DECISION_RULE, which every series
manifest and analysis also carries): A target is usable when every arm
reaches Ramsey visibility >= 0.3 at both delays. A usable target shows a
readout tail when chi2(H1) - chi2(H2) >= 13.82 (the 2-degree-of-freedom
chi-square quantile at p = 0.001), |A| >= 3 se(A), and the fitted T lies
below its 100-cycle upper bound; meeting the first two with T at that bound
classifies it as a static offset. A series reports 'readout tail detected'
when at least 50% of its usable targets show a tail, and 'not detected'
otherwise.

A series is 26 circuits, (5 readout arms + 1 reference) x 2 quadratures x
2 delays plus two readout-calibration circuits (every target in |0>, every
target in |1>), whose assignment channel is inverted per target before the
phases. batch-00 holds the calibration; then each delay and quadrature takes
two batches, the reference with tau 0 and 5, then tau 15, 40 and 100: 9
batches of at most qi_platform.HARDWARE_BATCH_CIRCUITS, one queued at a
time. delta(0) and delta(5) therefore compare circuits run under one
calibration at every setting; a frequency step between the paired batches
moves delta(15), delta(40) and delta(100) together, a pattern neither model
fits, and shows as a large chi2(H2). At 8192 shots and the 0.94 ms per shot
Tuna-17 measured, a job runs about 7.7 s against the 300 s limit.

The QX dry run keeps Tuna-17's coupling map on qubits 0-9 at 2048 shots; QX
has no detuning, coupling or resonator, so every delta must vanish and the
rule must report no tail.

Analyses write every float at SIGNIFICANT digits (qi_coupler_zz_map).

--write DIR writes DIR/readout_ringdown_{tuna_17,qx}_{P,Q}/ (batch-NN/ case
directories and cases.json); --check DIR regenerates them and compares
bytes; --conformance schedules the emitted circuits ALAP, evolves them under
injected omega_q, every Tuna-17 coupler J_ab and an injected post-readout
tail, and requires the analysis to recover the tail with it on and to report
none with it off; --analyze OUT RUN_DIR... analyzes the collected batches of
one series (--replay compares OUT with its recomputation); --sanity RUN_DIR
checks one collected batch before the next is submitted.

Usage: "$PYTHON" scripts/qi_readout_ringdown_cases.py
       (--write DIR | --check DIR | --conformance | --analyze OUT RUN_DIR... [--replay] | --sanity RUN_DIR)
       (DIR is the cases root, results/quantum_inspire/cases)
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import random
import sys
from pathlib import Path
from typing import Any

import numpy as np
from qi_coupler_zz_map import (
    CYCLE_SECONDS,
    MIN_VISIBILITY,
    backend_type,
    bit,
    edges,
    parts,
    quantized,
    retained_path,
    wrap,
)
from qi_platform import HARDWARE_BATCH_CIRCUITS

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from parallel import ordered_map  # noqa: E402

PROFILES: dict[str, dict[str, Any]] = {
    "tuna_17": {"identifier": "tuna_17", "qubits": 17, "shots": 8192, "directory": "readout_ringdown_tuna_17"},
    "qx": {"identifier": "QXsinglenodesimulator", "qubits": 10, "shots": 2048, "directory": "readout_ringdown_qx"},
}
SERIES = ("P", "Q")
TAUS = (0, 5, 15, 40, 100)
DELAYS = (2, 77)
SPAN = DELAYS[1] - DELAYS[0]
QUADRATURES = ("x", "y")
MEASURE_CYCLES = 40
SETTLE_CYCLES = 100
REFERENCE = "reference"
ARMS = (REFERENCE, *(f"tau{tau:03d}" for tau in TAUS))
# Per delay and quadrature: the reference shares a batch with the two shortest pre-delays.
ARM_GROUPS = ((REFERENCE, "tau000", "tau005"), ("tau015", "tau040", "tau100"))
BATCH = HARDWARE_BATCH_CIRCUITS
SECONDS_PER_SHOT = 0.94e-3
T_BOUNDS = (5.0, 100.0)
T_GRID = (*(T_BOUNDS[0] * (T_BOUNDS[1] / T_BOUNDS[0]) ** (k / 400) for k in range(400)), T_BOUNDS[1])
GOLDEN_STEPS = 100
DETECT_DELTA_CHI2 = 13.82
DETECT_SIGMA = 3.0
DETECT_FRACTION = 0.5
DECISION_RULE = (
    f"A target is usable when every arm reaches Ramsey visibility >= {MIN_VISIBILITY} at both delays. "
    f"A usable target shows a readout tail when chi2(H1) - chi2(H2) >= {DETECT_DELTA_CHI2} "
    f"(the 2-degree-of-freedom chi-square quantile at p = 0.001), |A| >= {DETECT_SIGMA:g} se(A), "
    f"and the fitted T lies below its {T_BOUNDS[1]:g}-cycle upper bound; meeting the first two with T "
    "at that bound classifies it as a static offset. A series reports 'readout tail detected' when at "
    f"least {DETECT_FRACTION:.0%} of its usable targets show a tail, and 'not detected' otherwise."
)
ESTIMATOR = (
    "Every rate and delta(tau) comes from all shots, read by qubit index; a target left in |1> after its "
    "mid-circuit readout scales both readout-corrected quadratures by (1 - 2 eps) and leaves the phase "
    "unbiased. Where the result carries the 2 n-bit register, the analysis also reports the estimate "
    "postselected on mid-circuit outcome 0 and each delta's difference from the all-shot estimate with "
    "standard error sqrt(se_post^2 - se_all^2)."
)
TO_HZ = 1 / (2 * math.pi * CYCLE_SECONDS)
Table = dict[tuple[str, str, int, int], tuple[float, float, float]]
Taus = list[int | None]


def arm_tau(arm: str) -> int | None:
    return None if arm == REFERENCE else int(arm[3:])


def circuit_name(arm: str, quadrature: str, delay: int) -> str:
    return f"{arm}-{quadrature}-d{delay:03d}.cq"


def header(nqubits: int) -> list[str]:
    return ["version 3.0", "", f"qubit[{nqubits}] q", f"bit[{2 * nqubits}] b", ""]


def final_measurement(nqubits: int) -> list[str]:
    return ["", "barrier q", f"b[0:{nqubits - 1}] = measure q", ""]


def ramsey_lines(nqubits: int, targets: list[int], arm: str, quadrature: str, delay: int) -> list[str]:
    tau = arm_tau(arm)
    lines = [*header(nqubits), "barrier q"]
    for t in targets:
        lines.append(f"wait({MEASURE_CYCLES}) q[{t}]" if tau is None else f"b[{nqubits + t}] = measure q[{t}]")
    lines.append("barrier q")
    for t in targets:
        if tau:
            lines.append(f"wait({tau}) q[{t}]")
        second = "X90" if quadrature == "x" else "Y90"
        lines += [f"X90 q[{t}]", f"wait({delay}) q[{t}]", f"{second} q[{t}]", f"wait({SETTLE_CYCLES}) q[{t}]"]
    return [*lines, *final_measurement(nqubits)]


def readout_lines(nqubits: int, targets: list[int], prepared: int) -> list[str]:
    flips = [f"X q[{t}]" for t in targets] if prepared else []
    settle = [f"wait({SETTLE_CYCLES}) q[{t}]" for t in targets]
    return [*header(nqubits), *flips, *settle, *final_measurement(nqubits)]


def members(profile: str, series: str) -> tuple[dict[str, Any], list[tuple[str, str]]]:
    settings = PROFILES[profile]
    backend = backend_type(str(settings["identifier"]))
    n = int(settings["qubits"])
    shots = int(settings["shots"])
    if n > backend["nqubits"]:
        raise SystemExit(f"{profile} needs {n} qubits; the backend type serves {backend['nqubits']}")
    if shots > backend["max_number_of_shots"]:
        raise SystemExit(f"{profile} needs {shots} shots; the backend type serves {backend['max_number_of_shots']}")
    bound = shots * SECONDS_PER_SHOT
    if bound > backend["job_execution_time_limit"] / 10:
        raise SystemExit(f"{profile}: {bound:.3g} s per job exceeds a tenth of the execution limit")
    pairs = edges(n)
    split = parts(pairs, n)
    targets = split[series]
    out = [
        ("readout-0.cq", "\n".join(readout_lines(n, targets, 0))),
        ("readout-1.cq", "\n".join(readout_lines(n, targets, 1))),
    ]
    for delay, quadrature, group in itertools.product(DELAYS, QUADRATURES, ARM_GROUPS):
        for arm in group:
            out.append(
                (circuit_name(arm, quadrature, delay), "\n".join(ramsey_lines(n, targets, arm, quadrature, delay)))
            )
    meta = {
        "backend": backend,
        "nqubits": n,
        "pairs": pairs,
        "series": series,
        "targets": targets,
        "spectators": split["Q" if series == "P" else "P"],
        "shots": shots,
        "execution_bound_seconds": bound,
    }
    return meta, out


def groups(ordered: list[tuple[str, str]]) -> list[list[tuple[str, str]]]:
    """batch-00 holds both readout references; each later batch holds one arm group at one delay and quadrature."""
    readouts = [item for item in ordered if item[0].startswith("readout")]
    rest = ordered[len(readouts) :]
    size = len(ARM_GROUPS[0])
    if size > BATCH or any(len(group) != size for group in ARM_GROUPS) or len(readouts) > BATCH:
        raise SystemExit(f"an arm group exceeds the {BATCH} circuits a hardware batch may hold")
    return [readouts, *(rest[i : i + size] for i in range(0, len(rest), size))]


def build(profile: str, series: str) -> dict[str, str]:
    meta, ordered = members(profile, series)
    files: dict[str, str] = {}
    batches = []
    for index, group in enumerate(groups(ordered)):
        directory = f"batch-{index:02d}"
        rows = []
        for name, text in group:
            files[f"{directory}/{name}"] = text
            rows.append(
                {
                    "file": name,
                    "kind": "readout" if name.startswith("readout") else "ramsey",
                    "sha256": hashlib.sha256(text.encode()).hexdigest(),
                }
            )
        case = {
            "schema": "qi-readout-ringdown-cases-v1",
            "backend": meta["backend"]["identifier"],
            "backend_type_id": meta["backend"]["id"],
            "nqubits": meta["nqubits"],
            "shots": meta["shots"],
            "series": series,
            "targets": meta["targets"],
            "circuits": rows,
        }
        files[f"{directory}/cases.json"] = json.dumps(case, indent=1) + "\n"
        batches.append(directory)
    summary = {
        "schema": "qi-readout-ringdown-series-v1",
        "backend": meta["backend"]["identifier"],
        "profile": profile,
        "series": series,
        "targets": meta["targets"],
        "spectators": meta["spectators"],
        "edges": [list(e) for e in meta["pairs"]],
        "taus_cycles": list(TAUS),
        "delays_cycles": list(DELAYS),
        "measure_cycles": MEASURE_CYCLES,
        "cycle_seconds": CYCLE_SECONDS,
        "quadratures": list(QUADRATURES),
        "unambiguous_offset_hz": quantized(TO_HZ * math.pi / SPAN),
        "t_bounds_cycles": list(T_BOUNDS),
        "shots": meta["shots"],
        "execution_bound_seconds": quantized(meta["execution_bound_seconds"]),
        "job_execution_time_limit_seconds": meta["backend"]["job_execution_time_limit"],
        "batch_limit": BATCH,
        "circuits": len(ordered),
        "batches": batches,
        "estimator": ESTIMATOR,
        "decision_rule": DECISION_RULE,
    }
    files["cases.json"] = json.dumps(summary, indent=1) + "\n"
    return files


def series_directory(profile: str, series: str) -> str:
    return f"{PROFILES[profile]['directory']}_{series}"


def mid_bits(width: int, nqubits: int) -> bool:
    """True for the 2 n-bit register, False for the n-character measurement register QX returns."""
    if width == 2 * nqubits:
        return True
    if width == nqubits:
        return False
    raise SystemExit(f"shots of {width} bits match neither the {2 * nqubits}-bit register nor {nqubits} qubits")


def tabulate(meta: dict[str, Any], shots_by_circuit: dict[str, list[str]]) -> tuple[Table, Table | None]:
    """(ones, kept, recorded) of every target, arm, quadrature and delay from all shots, and postselected.

    The postselected table keeps a readout arm's shots whose mid-circuit
    outcome of that target reads 0; it exists only for the 2 n-bit register.
    """
    n = meta["nqubits"]
    widths = {len(shot) for shots in shots_by_circuit.values() for shot in shots}
    if len(widths) != 1:
        raise SystemExit(f"the series mixes shot widths {sorted(widths)}")
    present = mid_bits(widths.pop(), n)
    table: Table = {}
    post: Table = {}
    for arm, quadrature, delay in itertools.product(ARMS, QUADRATURES, DELAYS):
        shots = shots_by_circuit[circuit_name(arm, quadrature, delay)]
        for t in meta["targets"]:
            table[(arm, quadrature, delay, t)] = (
                float(sum(bit(s, t) for s in shots)),
                float(len(shots)),
                float(len(shots)),
            )
            if present:
                kept = [s for s in shots if arm == REFERENCE or bit(s, n + t) == 0]
                post[(arm, quadrature, delay, t)] = (
                    float(sum(bit(s, t) for s in kept)),
                    float(len(kept)),
                    float(len(shots)),
                )
    return table, post if present else None


def phase(table: Table, arm: str, delay: int, target: int, e01: float, e10: float) -> tuple[float, float, float] | None:
    """atan2 phase, its delta-method variance and the visibility of one arm and delay."""
    expect = {}
    variance = {}
    scale = 1 - e01 - e10
    for quadrature in QUADRATURES:
        ones, kept, _ = table[(arm, quadrature, delay, target)]
        if kept <= 0:
            return None
        p = ones / kept
        expect[quadrature] = 2 * (p - e01) / scale - 1
        variance[quadrature] = 4 * p * (1 - p) / kept / scale**2
    x, y = expect["x"], expect["y"]
    r2 = x * x + y * y
    se2 = (y * y * variance["x"] + x * x * variance["y"]) / r2**2 if r2 > 0 else math.inf
    return math.atan2(y, x), se2, math.sqrt(r2)


def h2_at(tail: float, taus: Taus, rates: list[float], weights: list[float]) -> tuple[float, float, float]:
    """chi2, c and A of the weighted fit rate = c + A f with f = exp(-tau / T) (0 for the reference)."""
    f = [0.0 if tau is None else math.exp(-tau / tail) for tau in taus]
    sw = sum(weights)
    sf = sum(w * fi for w, fi in zip(weights, f, strict=True))
    sff = sum(w * fi * fi for w, fi in zip(weights, f, strict=True))
    sy = sum(w * y for w, y in zip(weights, rates, strict=True))
    sfy = sum(w * fi * y for w, fi, y in zip(weights, f, rates, strict=True))
    det = sw * sff - sf * sf
    a = (sw * sfy - sf * sy) / det
    c = (sff * sy - sf * sfy) / det
    chi2 = sum(w * (y - c - a * fi) ** 2 for w, y, fi in zip(weights, rates, f, strict=True))
    return chi2, c, a


def fit_h2(taus: Taus, rates: list[float], weights: list[float]) -> tuple[float, float, float, float]:
    """(chi2, c, A, T) minimizing chi2 over T_GRID, then golden section between the best point's neighbors."""
    profile = [h2_at(t, taus, rates, weights)[0] for t in T_GRID]
    k = min(range(len(T_GRID)), key=profile.__getitem__)
    low, high = T_GRID[max(k - 1, 0)], T_GRID[min(k + 1, len(T_GRID) - 1)]
    ratio = (math.sqrt(5) - 1) / 2
    left, right = high - ratio * (high - low), low + ratio * (high - low)
    f_left, f_right = h2_at(left, taus, rates, weights)[0], h2_at(right, taus, rates, weights)[0]
    for _ in range(GOLDEN_STEPS):
        if f_left <= f_right:
            high, right, f_right = right, left, f_left
            left = high - ratio * (high - low)
            f_left = h2_at(left, taus, rates, weights)[0]
        else:
            low, left, f_left = left, right, f_right
            right = low + ratio * (high - low)
            f_right = h2_at(right, taus, rates, weights)[0]
    candidates = [T_GRID[k], left, right, T_GRID[max(k - 1, 0)], T_GRID[min(k + 1, len(T_GRID) - 1)]]
    best = min(candidates, key=lambda t: h2_at(t, taus, rates, weights)[0])
    chi2, c, a = h2_at(best, taus, rates, weights)
    return chi2, c, a, best


def inverse(matrix: list[list[float]]) -> list[list[float]] | None:
    """Inverse of a 2 x 2 or 3 x 3 matrix by cofactors, so a replay needs no BLAS; None when singular."""
    if len(matrix) == 2:
        (a, b), (c, d) = matrix
        det = a * d - b * c
        return [[d / det, -b / det], [-c / det, a / det]] if det else None
    m = matrix
    cof = [
        [
            m[(i + 1) % 3][(j + 1) % 3] * m[(i + 2) % 3][(j + 2) % 3]
            - m[(i + 1) % 3][(j + 2) % 3] * m[(i + 2) % 3][(j + 1) % 3]
            for j in range(3)
        ]
        for i in range(3)
    ]
    det = sum(m[0][j] * cof[0][j] for j in range(3))
    return [[cof[j][i] / det for j in range(3)] for i in range(3)] if det else None


def h2_errors(taus: Taus, weights: list[float], a: float, tail: float) -> tuple[float, float | None]:
    """se(A) and se(T) from the Fisher matrix of (c, A, T); T held fixed at a bound or when A vanishes."""
    rows = []
    for tau in taus:
        f = 0.0 if tau is None else math.exp(-tau / tail)
        rows.append([1.0, f, 0.0 if tau is None else a * tau / tail**2 * f])
    fisher = [[sum(w * r[i] * r[j] for w, r in zip(weights, rows, strict=True)) for j in range(3)] for i in range(3)]
    if T_BOUNDS[0] < tail < T_BOUNDS[1] and a != 0:
        covariance = inverse(fisher)
        if covariance is not None and covariance[1][1] > 0 and covariance[2][2] > 0:
            return math.sqrt(covariance[1][1]), math.sqrt(covariance[2][2])
    fixed = inverse([row[:2] for row in fisher[:2]])
    if fixed is None or fixed[1][1] <= 0:
        return math.inf, None
    return math.sqrt(fixed[1][1]), None


def gain(tail: float) -> float:
    """g(T) = A / S: the rate offset at tau = 0 per unit of frequency shift S at the readout end."""
    return tail * (math.exp(-(DELAYS[0] + 1) / tail) - math.exp(-(DELAYS[1] + 1) / tail)) / SPAN


def analyze_target(target: int, table: Table, assignment: tuple[float, float]) -> dict[str, Any]:
    e01, e10 = assignment
    phases = {arm: [phase(table, arm, d, target, e01, e10) for d in DELAYS] for arm in ARMS}
    row: dict[str, Any] = {"target": target}
    turns = {}
    for arm in ARMS:
        first, second = phases[arm]
        if first is None or second is None:
            return {**row, "usable": False, "class": "none", "min_visibility": None}
        turns[arm] = (second[0] - first[0], first[1] + second[1], min(first[2], second[2]))
    reference = wrap(turns[REFERENCE][0]) / SPAN
    rates = {arm: reference + wrap(turns[arm][0] - turns[REFERENCE][0]) / SPAN for arm in ARMS}
    errors = {arm: math.sqrt(turns[arm][1]) / SPAN for arm in ARMS}
    taus: Taus = [arm_tau(arm) for arm in ARMS]
    values = [rates[arm] for arm in ARMS]
    # An exact (zero-variance) rate gets a large finite weight, so exact data stay solvable.
    weights = [1 / max(errors[arm], 1e-12) ** 2 for arm in ARMS]
    c1 = sum(w * y for w, y in zip(weights, values, strict=True)) / sum(weights)
    chi2_h1 = sum(w * (y - c1) ** 2 for w, y in zip(weights, values, strict=True))
    chi2_h2, c2, a, tail = fit_h2(taus, values, weights)
    se_a, se_t = h2_errors(taus, weights, a, tail)
    visibility = min(turns[arm][2] for arm in ARMS)
    usable = visibility >= MIN_VISIBILITY
    significant = chi2_h1 - chi2_h2 >= DETECT_DELTA_CHI2 and abs(a) >= DETECT_SIGMA * se_a
    label = "none" if not (usable and significant) else "offset" if tail >= T_BOUNDS[1] else "tail"
    return {
        **row,
        "rate_hz": {arm: rates[arm] * TO_HZ for arm in ARMS},
        "rate_se_hz": {arm: errors[arm] * TO_HZ for arm in ARMS},
        "delta_hz": {str(arm_tau(arm)): (rates[arm] - rates[REFERENCE]) * TO_HZ for arm in ARMS[1:]},
        "delta_se_hz": {str(arm_tau(arm)): math.hypot(errors[arm], errors[REFERENCE]) * TO_HZ for arm in ARMS[1:]},
        "visibility": {arm: turns[arm][2] for arm in ARMS},
        "min_visibility": visibility,
        "h1": {"chi2": chi2_h1, "dof": len(ARMS) - 1, "rate_hz": c1 * TO_HZ},
        "h2": {
            "chi2": chi2_h2,
            "dof": len(ARMS) - 3,
            "rate_hz": c2 * TO_HZ,
            "A_hz": a * TO_HZ,
            "A_se_hz": se_a * TO_HZ,
            "t_cycles": tail,
            "t_se_cycles": se_t,
            "t_at_bound": not T_BOUNDS[0] < tail < T_BOUNDS[1],
            "readout_end_shift_hz": a / gain(tail) * TO_HZ,
        },
        "delta_chi2": chi2_h1 - chi2_h2,
        "usable": usable,
        "class": label,
    }


def postselection_check(
    target: int, post: Table, every: dict[str, Any], assignment: tuple[float, float]
) -> dict[str, Any]:
    """Postselected fraction and deltas of one target, and their differences from the all-shot estimate."""
    fractions = {
        arm: sum(post[(arm, q, d, target)][1] for q in QUADRATURES for d in DELAYS)
        / sum(post[(arm, q, d, target)][2] for q in QUADRATURES for d in DELAYS)
        for arm in ARMS[1:]
    }
    selected = analyze_target(target, post, assignment)
    out: dict[str, Any] = {"fraction": fractions}
    if "delta_hz" not in selected or "delta_hz" not in every:
        return out
    difference = {}
    error = {}
    score = {}
    for tau, value in selected["delta_hz"].items():
        difference[tau] = value - every["delta_hz"][tau]
        error[tau] = math.sqrt(max(selected["delta_se_hz"][tau] ** 2 - every["delta_se_hz"][tau] ** 2, 0.0))
        score[tau] = difference[tau] / error[tau] if error[tau] > 0 else None
    return {
        **out,
        "delta_hz": selected["delta_hz"],
        "delta_se_hz": selected["delta_se_hz"],
        "class": selected["class"],
        "difference_hz": difference,
        "difference_se_hz": error,
        "difference_z": score,
    }


def analyze_table(
    meta: dict[str, Any], table: Table, assignment: dict[int, tuple[float, float]], post: Table | None = None
) -> dict[str, Any]:
    targets = [analyze_target(t, table, assignment[t]) for t in meta["targets"]]
    if post is not None:
        for row in targets:
            row["postselected"] = postselection_check(row["target"], post, row, assignment[row["target"]])
    usable = [row["target"] for row in targets if row["usable"]]
    tails = [row["target"] for row in targets if row["class"] == "tail"]
    detected = bool(usable) and len(tails) >= DETECT_FRACTION * len(usable)
    decision = {
        "usable_targets": usable,
        "tail_targets": tails,
        "offset_targets": [row["target"] for row in targets if row["class"] == "offset"],
        "verdict": "readout tail detected" if detected else "not detected",
    }
    out: dict[str, Any] = {"targets": targets, "decision": decision}
    if post is not None:
        scores = [
            abs(z) for row in targets for z in row["postselected"].get("difference_z", {}).values() if z is not None
        ]
        out["postselection_check"] = {"max_abs_difference_z": max(scores, default=None)}
    return out


GATES = {
    "X": np.array([[0, -1j], [-1j, 0]]),
    "X90": np.array([[1, -1j], [-1j, 1]]) / math.sqrt(2),
    "Y90": np.array([[1, -1], [1, 1]], dtype=complex) / math.sqrt(2),
}


def schedule(lines: list[str], nqubits: int) -> tuple[dict[int, list[tuple[int, str]]], list[int]]:
    """ALAP start cycle of every operation within each barrier domain, and the cycle of every barrier.

    qi_coupler_zz_map.schedule's rule (one cycle per gate, n per wait(n), every
    program of a domain ending at the domain's end) applied per `barrier q`
    domain, with a measurement lasting MEASURE_CYCLES.
    """
    domains: list[dict[int, list[tuple[str, int]]]] = [{q: [] for q in range(nqubits)}]
    for line in lines:
        words = line.split()
        if not words or line.startswith(("version", "qubit", "bit", "//")):
            continue
        if line == "barrier q":
            domains.append({q: [] for q in range(nqubits)})
            continue
        operand = words[-1]
        qubits = list(range(nqubits)) if operand == "q" else [int(operand[2:-1])]
        for q in qubits:
            if "measure" in words:
                domains[-1][q].append(("measure", MEASURE_CYCLES))
            elif words[0].startswith("wait("):
                domains[-1][q].append(("wait", int(words[0][5:-1])))
            else:
                domains[-1][q].append((words[0], 1))
    timeline: dict[int, list[tuple[int, str]]] = {}
    barriers = []
    offset = 0
    for index, program in enumerate(domains):
        if index:
            barriers.append(offset)
        length = max(sum(n for _, n in ops) for ops in program.values())
        for q, ops in program.items():
            start = offset + length - sum(n for _, n in ops)
            for name, duration in ops:
                if name != "wait":
                    timeline.setdefault(start, []).append((q, name))
                start += duration
        offset += length
    return timeline, barriers


class Evolution:
    """Exact evolution of an emitted circuit up to its final barrier, picklable for the process pool.

    H / hbar = sum_q (omega_q + s_q(t)) Z_q / 2 + sum_(a,b) J_ab Z_a Z_b / 2
    per 20 ns cycle, with gates at cycle starts. s_q(t) = S_q exp(-t / T_q)
    for t after q's mid-circuit readout ends, integrated over each cycle. H is
    diagonal, so the state takes the exact phase of every interval between
    operations at once. A mid-circuit measurement projects its qubit on
    outcome 0 and records that probability; with flip it then leaves the qubit
    in |1>, the trajectory of a post-readout excitation. Targets share no
    coupler and every spectator's Z is conserved, so a target's final
    marginal depends on its own trajectory only, and one evolution with every
    target flipped gives each target's excited trajectory.
    """

    def __init__(
        self,
        nqubits: int,
        omega: list[float],
        coupling: dict[tuple[int, int], float],
        tail: dict[int, tuple[float, float]],
        flip: bool = False,
    ) -> None:
        self.nqubits, self.omega, self.coupling, self.tail, self.flip = nqubits, omega, coupling, tail, flip

    def __call__(self, lines: list[str]) -> tuple[list[float], dict[int, float]]:
        n = self.nqubits
        timeline, barriers = schedule(lines, n)
        index = np.arange(1 << n)
        ones = (index[:, None] >> np.arange(n)) & 1
        z = 1 - 2 * ones
        coupled = np.zeros(1 << n)
        for (a, b), j in self.coupling.items():
            coupled = coupled + j * z[:, a] * z[:, b] / 2
        omega = np.array(self.omega)
        state = np.zeros(1 << n, dtype=complex)
        state[0] = 1
        ends: dict[int, int] = {}
        kept: dict[int, float] = {}
        clock = 0
        stop = barriers[-1]
        for cycle in [*sorted(c for c in timeline if c < stop), stop]:
            if cycle > clock:
                phi = omega * (cycle - clock)
                for q, end in ends.items():
                    amplitude, decay = self.tail.get(q, (0.0, 1.0))
                    if cycle > end and amplitude:
                        start = max(clock, end) - end
                        phi[q] += amplitude * decay * (math.exp(-start / decay) - math.exp(-(cycle - end) / decay))
                state = np.exp(-1j * ((z @ phi) / 2 + coupled * (cycle - clock))) * state
                clock = cycle
            if cycle == stop:
                break
            for q, name in timeline[cycle]:
                if name == "measure":
                    keep = ones[:, q] == 0
                    probability = float(np.sum(np.abs(state[keep]) ** 2))
                    state = np.where(keep, state, 0) / math.sqrt(probability)
                    kept[q] = probability
                    ends[q] = cycle + MEASURE_CYCLES
                    if not self.flip:
                        continue
                    name = "X"
                axis = n - 1 - q
                tensor = np.tensordot(GATES[name], state.reshape([2] * n), axes=([1], [axis]))
                state = np.moveaxis(tensor, 0, axis).reshape(-1)
        probabilities = np.abs(state) ** 2
        return [float(probabilities[ones[:, q] == 1].sum()) for q in range(n)], kept


def timing_problems(meta: dict[str, Any], texts: dict[str, str]) -> list[str]:
    """Cycles of the mid-circuit readout, both Ramsey gates and the final barrier in every emitted arm."""
    n = meta["nqubits"]
    problems = []
    for arm, quadrature, delay in itertools.product(ARMS, QUADRATURES, DELAYS):
        name = circuit_name(arm, quadrature, delay)
        timeline, barriers = schedule(texts[name].splitlines(), n)
        tau = arm_tau(arm) or 0
        expected_barriers = [0, MEASURE_CYCLES, MEASURE_CYCLES + tau + delay + 2 + SETTLE_CYCLES]
        if barriers != expected_barriers:
            problems.append(f"{name}: barriers at {barriers}, designed {expected_barriers}")
        for q in range(n):
            events = [(c, op) for c, ops in sorted(timeline.items()) for k, op in ops if k == q and c < barriers[-1]]
            if q not in meta["targets"]:
                designed: list[tuple[int, str]] = []
            else:
                second = "X90" if quadrature == "x" else "Y90"
                gates = [(MEASURE_CYCLES + tau, "X90"), (MEASURE_CYCLES + tau + delay + 1, second)]
                designed = gates if arm == REFERENCE else [(0, "measure"), *gates]
            if events != designed:
                problems.append(f"{name} q{q}: operations {events}, designed {designed}")
    return problems


EPS_FIXED = 0.03
EPS_RISE = 0.05


def eps_profiles() -> dict[str, dict[str, float]]:
    """Post-readout excitation per readout arm: none, fixed EPS_FIXED, and rising linearly in tau to EPS_RISE."""
    readout = ARMS[1:]
    return {
        "none": dict.fromkeys(readout, 0.0),
        "fixed": dict.fromkeys(readout, EPS_FIXED),
        "rising": {arm: EPS_RISE * (arm_tau(arm) or 0) / TAUS[-1] for arm in readout},
    }


def mixed_tables(
    meta: dict[str, Any],
    settings: list[tuple[str, str, int]],
    ground: list[tuple[list[float], dict[int, float]]],
    excited: list[tuple[list[float], dict[int, float]]],
    eps: dict[str, float],
) -> tuple[Table, Table]:
    """All-shot and postselected tables of exact probabilities at the profile's shots.

    The excitation is heralded: a target left in |1> reads 1 at its
    mid-circuit readout, so postselection removes it and the all-shot table
    mixes both trajectories.
    """
    shots = float(meta["shots"])
    table: Table = {}
    post: Table = {}
    for (arm, quadrature, delay), (p0, _), (p1, _) in zip(settings, ground, excited, strict=True):
        e = eps.get(arm, 0.0)
        for t in meta["targets"]:
            table[(arm, quadrature, delay, t)] = (((1 - e) * p0[t] + e * p1[t]) * shots, shots, shots)
            post[(arm, quadrature, delay, t)] = ((1 - e) * p0[t] * shots, (1 - e) * shots, shots)
    return table, post


def shot_strings(
    meta: dict[str, Any],
    settings: list[tuple[str, str, int]],
    ground: list[tuple[list[float], dict[int, float]]],
    excited: list[tuple[list[float], dict[int, float]]],
    eps: dict[str, float],
) -> dict[str, list[str]]:
    """2 n-character shots whose per-target (mid, final) counts round the exact probabilities."""
    n = meta["nqubits"]
    total = int(meta["shots"])
    out = {}
    for (arm, quadrature, delay), (p0, _), (p1, _) in zip(settings, ground, excited, strict=True):
        bits = [["0"] * (2 * n) for _ in range(total)]
        for t in meta["targets"]:
            heralded = round(total * eps.get(arm, 0.0))
            clean = total - heralded
            ones_clean, ones_heralded = round(clean * p0[t]), round(heralded * p1[t])
            column = [(0, 1)] * ones_clean + [(0, 0)] * (clean - ones_clean)
            column += [(1, 1)] * ones_heralded + [(1, 0)] * (heralded - ones_heralded)
            for shot, (mid, final) in zip(bits, column, strict=True):
                shot[n + t], shot[t] = str(mid), str(final)
        out[circuit_name(arm, quadrature, delay)] = ["".join(reversed(shot)) for shot in bits]
    return out


def all_shot_fields(report: dict[str, Any]) -> list[dict[str, Any]]:
    return [{k: v for k, v in row.items() if k != "postselected"} for row in report["targets"]]


def conformance_series(profile: str, series: str, rng: random.Random) -> str:
    """Recover an injected tail and report none without it, at the profile's shots, under post-readout excitation.

    (a) excitation of EPS_FIXED, or rising in tau to EPS_RISE, leaves every
    delta and every class unchanged and scales each readout arm's visibility
    by (1 - 2 eps); (b) with the full register, the postselected and all-shot
    deltas agree under excitation alone; (c) the QX profile reads the same
    all-shot analysis from n-character as from 2 n-character shots.
    """
    meta, ordered = members(profile, series)
    texts = dict(ordered)
    problems = timing_problems(meta, texts)
    if problems:
        raise SystemExit("conformance: " + "; ".join(problems[:5]))
    n = meta["nqubits"]
    name = f"conformance {profile} {series}"
    scale = 2 * math.pi * CYCLE_SECONDS
    omega = [scale * rng.uniform(-60e3, 60e3) for _ in range(n)]
    coupling = {e: scale * rng.uniform(-60e3, 60e3) for e in meta["pairs"]}
    # One target sits near the 333 kHz alias edge, so its arm rates straddle it.
    omega[meta["targets"][0]] = scale * 320e3
    injected = {
        t: (scale * rng.choice((-1, 1)) * rng.uniform(250e3, 400e3), rng.uniform(8.0, 25.0)) for t in meta["targets"]
    }
    settings = list(itertools.product(ARMS, QUADRATURES, DELAYS))
    programs = [texts[circuit_name(*setting)].splitlines() for setting in settings]
    zero = {q: (0.0, 0.0) for q in range(n)}
    profiles = eps_profiles()
    reports: dict[tuple[str, str], dict[str, Any]] = {}
    worst_delta = worst_visibility = worst_post = 0.0
    for label, tail in (("on", injected), ("off", {})):
        ground = ordered_map(Evolution(n, omega, coupling, tail), programs, min_items=1)
        excited = ordered_map(Evolution(n, omega, coupling, tail, flip=True), programs, min_items=1)
        for key, eps in profiles.items():
            table, post = mixed_tables(meta, settings, ground, excited, eps)
            reports[(label, key)] = analyze_table(meta, table, zero, post)
            for row, base in zip(reports[(label, key)]["targets"], reports[(label, "none")]["targets"], strict=True):
                if row["class"] != base["class"]:
                    raise SystemExit(f"{name}: eps {key} turns target {row['target']} from {base['class']}")
                for tau, value in row["delta_hz"].items():
                    worst_delta = max(worst_delta, abs(value - base["delta_hz"][tau]))
                for arm, value in row["visibility"].items():
                    expected = base["visibility"][arm] * (1 - 2 * eps.get(arm, 0.0))
                    worst_visibility = max(worst_visibility, abs(value - expected))
                if label == "off":
                    worst_post = max(worst_post, *(abs(v) for v in row["postselected"]["difference_hz"].values()))
        if profile == "qx" and label == "on":
            strings = shot_strings(meta, settings, ground, excited, profiles["fixed"])
            full_table, full_post = tabulate(meta, strings)
            full = analyze_table(meta, full_table, zero, full_post)
            short, absent = tabulate(meta, {k: [s[n:] for s in v] for k, v in strings.items()})
            same = all_shot_fields(analyze_table(meta, short, zero)) == all_shot_fields(full)
            if full_post is None or absent is not None or not same:
                raise SystemExit(f"{name}: n-character shots analyze differently from 2 n-character shots")
    worst_s = worst_t = worst_zero = 0.0
    smallest = math.inf
    for key in profiles:
        for row in reports[("on", key)]["targets"]:
            amplitude, decay = injected[row["target"]]
            if row["class"] != "tail":
                raise SystemExit(f"{name}: eps {key}: target {row['target']} classified {row['class']}")
            worst_s = max(worst_s, abs(row["h2"]["readout_end_shift_hz"] / (amplitude * TO_HZ) - 1))
            worst_t = max(worst_t, abs(row["h2"]["t_cycles"] / decay - 1))
            smallest = min(smallest, row["delta_chi2"])
        for row in reports[("off", key)]["targets"]:
            if row["class"] != "none":
                raise SystemExit(f"{name}: eps {key}: tail-free target {row['target']} classified {row['class']}")
            worst_zero = max(worst_zero, *(abs(v) for v in row["delta_hz"].values()))
        if reports[("on", key)]["decision"]["verdict"] != "readout tail detected":
            raise SystemExit(f"{name}: eps {key}: the injected tail is not detected")
        if reports[("off", key)]["decision"]["verdict"] != "not detected":
            raise SystemExit(f"{name}: eps {key}: a tail is detected without one")
    if max(worst_s, worst_t) > 1e-5 or max(worst_zero, worst_delta, worst_post) > 1e-3 or worst_visibility > 1e-9:
        raise SystemExit(
            f"{name}: S within {worst_s:.2g}, T within {worst_t:.2g}, tail-free delta {worst_zero:.2g} Hz, "
            f"eps moves delta {worst_delta:.2g} Hz and visibility {worst_visibility:.2g}, "
            f"postselection moves delta {worst_post:.2g} Hz"
        )
    return (
        f"{name}: {len(meta['targets'])} targets, timing as designed; tail on: S and T within "
        f"{max(worst_s, worst_t):.2g} relative, smallest delta chi2 {smallest:.3g}, detected; tail off: "
        f"|delta| <= {worst_zero:.2g} Hz, not detected; eps {EPS_FIXED} and rising to {EPS_RISE}: delta moves "
        f"<= {worst_delta:.2g} Hz, visibility (1 - 2 eps) within {worst_visibility:.2g}, postselected minus "
        f"all <= {worst_post:.2g} Hz" + ("; n- and 2 n-character shots agree" if profile == "qx" else "")
    )


SANITY_READOUT_ERROR = 0.2
SANITY_MID_ONE = 0.2
SANITY_SPECTATOR_ONE = 0.2


def sanity(run: Path, readout_error: float = SANITY_READOUT_ERROR) -> tuple[list[str], list[str]]:
    """Checks one collected batch must pass before the next batch is submitted, and what the result carried.

    Every job completed with its requested shots; every shot carries n
    characters (the measurement register) or the 2 n-bit register, and the
    notes record which; in a readout circuit every target's assignment error
    stays below readout_error (SANITY_READOUT_ERROR unless a series names its
    own guard, which the notes record); in a Ramsey circuit every spectator, held
    in |0>, reads 1 below SANITY_SPECTATOR_ONE and, where the 2 n-bit register
    returns, every target's mid-circuit outcome reads 1 below SANITY_MID_ONE. A
    failure stops the series before it spends more device time.
    """
    case = json.loads((run / "cases.json").read_text(encoding="utf-8"))
    collected = json.loads((run / "results.json").read_text(encoding="utf-8"))
    problems = []
    for row in collected["jobs"]:
        done = sum(r["shots_done"] for r in row["results"])
        if row["job"]["status"] != "completed" or done != case["shots"]:
            problems.append(f"{row['file']}: {row['job']['status']}, {done} of {case['shots']} shots")
    profile = next(name for name, settings in PROFILES.items() if settings["identifier"] == case["backend"])
    meta, _ = members(profile, case["series"])
    n = meta["nqubits"]
    seen = set()
    for row in case["circuits"]:
        path = run / "raw" / f"{row['file']}.json"
        if not path.exists():
            problems.append(f"{row['file']}: raw shots missing")
            continue
        shots = json.loads(path.read_text(encoding="utf-8"))
        widths = {len(s) for s in shots}
        if widths not in ({n}, {2 * n}):
            problems.append(f"{row['file']}: shot widths {sorted(widths)}, expected {n} or {2 * n}")
            continue
        seen |= widths
        present = widths == {2 * n}
        ones = {q: sum(bit(s, q) for s in shots) / len(shots) for q in range(n)}
        if row["kind"] == "readout":
            error = ones if row["file"] == "readout-0.cq" else {q: 1 - p for q, p in ones.items()}
            problems += [
                f"{row['file']} q{q}: error {error[q]:.3f}" for q in meta["targets"] if error[q] > readout_error
            ]
            continue
        if present and not row["file"].startswith(REFERENCE):
            for t in meta["targets"]:
                mid = sum(bit(s, n + t) for s in shots) / len(shots)
                if mid > SANITY_MID_ONE:
                    problems.append(f"{row['file']} q{t}: mid-circuit P1 {mid:.3f}")
        problems += [
            f"{row['file']} spectator q{q}: P1 {ones[q]:.3f}"
            for q in meta["spectators"]
            if ones[q] > SANITY_SPECTATOR_ONE
        ]
    notes = []
    for width in sorted(seen):
        if width == n:
            notes.append(f"register width {width}: measurement register only: mid-circuit outcomes absent")
        else:
            notes.append(f"register width {width}: full bit register: mid-circuit outcomes present")
    return problems, notes


def analyze(runs: list[Path]) -> dict[str, Any]:
    manifests = [json.loads((run / "cases.json").read_text(encoding="utf-8")) for run in runs]
    series_keys = ("schema", "backend", "backend_type_id", "nqubits", "shots", "series", "targets")
    for run, manifest in zip(runs, manifests, strict=True):
        if any(manifest[key] != manifests[0][key] for key in series_keys):
            raise SystemExit(f"{run}: its manifest differs from {runs[0]} in {', '.join(series_keys)}")
    backend = manifests[0]["backend"]
    profile = next(name for name, settings in PROFILES.items() if settings["identifier"] == backend)
    meta, ordered = members(profile, manifests[0]["series"])
    if [manifests[0][k] for k in ("nqubits", "shots", "targets")] != [meta[k] for k in ("nqubits", "shots", "targets")]:
        raise SystemExit(f"{runs[0]}: its manifest does not describe the {profile} {meta['series']} series")
    shots: dict[str, list[str]] = {}
    batch_of: dict[str, int] = {}
    for index, (run, manifest) in enumerate(zip(runs, manifests, strict=True)):
        for row in manifest["circuits"]:
            if row["file"] in shots:
                raise SystemExit(f"{run}: {row['file']} appears in more than one listed batch")
            shots[row["file"]] = json.loads((run / "raw" / f"{row['file']}.json").read_text(encoding="utf-8"))
            batch_of[row["file"]] = index
    missing = sorted(name for name, _ in ordered if name not in shots)
    if missing:
        raise SystemExit(f"the listed batches lack {', '.join(missing)}")
    zero, one = shots["readout-0.cq"], shots["readout-1.cq"]
    assignment = {
        t: (sum(bit(s, t) for s in zero) / len(zero), sum(1 - bit(s, t) for s in one) / len(one))
        for t in meta["targets"]
    }
    table, post = tabulate(meta, {name: shots[name] for name, _ in ordered if not name.startswith("readout")})
    return {
        "schema": "qi-readout-ringdown-analysis-v1",
        "profile": profile,
        "series": meta["series"],
        "runs": [retained_path(r) for r in runs],
        "estimator": ESTIMATOR,
        "decision_rule": DECISION_RULE,
        "mid_circuit_bits": "present" if post is not None else "absent",
        "arm_batches": {
            arm: sorted({batch_of[circuit_name(arm, q, d)] for q in QUADRATURES for d in DELAYS}) for arm in ARMS
        },
        "readout_assignment": {str(t): list(v) for t, v in assignment.items()},
        **analyze_table(meta, table, assignment, post),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--conformance", action="store_true")
    mode.add_argument("--analyze", type=Path, nargs="+", metavar=("OUT", "RUN_DIR"))
    mode.add_argument("--sanity", type=Path, metavar="RUN_DIR")
    parser.add_argument("--replay", action="store_true", help="with --analyze: compare OUT with the recomputation")
    parser.add_argument(
        "--sanity-readout-error",
        type=float,
        default=SANITY_READOUT_ERROR,
        help="with --sanity: the readout-circuit assignment-error guard for this series",
    )
    args = parser.parse_args()
    if args.sanity:
        problems, notes = sanity(args.sanity, args.sanity_readout_error)
        if args.sanity_readout_error != SANITY_READOUT_ERROR:
            notes.append(f"readout guard {args.sanity_readout_error} (default {SANITY_READOUT_ERROR})")
        for line in [*notes, *problems]:
            print(line)
        print(f"sanity {args.sanity.name}: {'FAIL' if problems else 'pass'}")
        return 1 if problems else 0
    if args.conformance:
        rng = random.Random(23)
        for profile, series in itertools.product(PROFILES, SERIES):
            print(conformance_series(profile, series, rng))
        return 0
    if args.analyze:
        out, *runs = args.analyze
        if not runs:
            raise SystemExit("--analyze needs OUT and at least one RUN_DIR")
        report = analyze(runs)
        text = json.dumps(quantized(report), indent=1) + "\n"
        if args.replay:
            if out.read_text(encoding="utf-8") != text:
                raise SystemExit(f"{out} differs from its recomputation")
            print(f"{out}: {len(report['targets'])} targets reproduce")
            return 0
        out.write_text(text, encoding="utf-8")
        print(f"{len(report['targets'])} targets, {report['decision']['verdict']} -> {out}")
        return 0
    if " ".join(DECISION_RULE.split()) not in " ".join(str(__doc__).split()):
        raise SystemExit("the module docstring does not state DECISION_RULE")
    count = 0
    for profile, series in itertools.product(PROFILES, SERIES):
        for name, text in build(profile, series).items():
            path = (args.write or args.check) / series_directory(profile, series) / name
            if args.write:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            elif path.read_text(encoding="utf-8") != text:
                raise SystemExit(f"{path} differs from its regeneration")
            count += 1
    print(f"qi readout ringdown: {count} files {'written' if args.write else 'match their regeneration'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
