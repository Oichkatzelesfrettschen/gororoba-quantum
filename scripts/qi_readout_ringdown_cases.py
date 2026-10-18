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

The preregistered errors treat the batch's assignment e01, e10 as constants.
--sensitivity OUT RUN_DIR... writes a separate record that changes no verdict:
per target, the preregistered standard error beside the analytic error with
the binomial variances of e01 and e10 (from the readout-0 and readout-1
counts) carried through every quadrature, and the standard deviation over
CALIBRATION_REPLICATES joint resamplings of all readout and Ramsey counts.
The replicates' counts are drawn first from one seeded generator and then
analyzed through parallel.ordered_map, so pooled and serial runs write the
same bytes; with --replay the record is compared with its recomputation.
--sensitivity-self-test checks the contract on synthetic counts.

The decision rule scans T over T_BOUNDS, and under H1 (A = 0) T is
unidentified, so delta chi2 = chi2(H1) - chi2(H2) is a supremum over T whose
null law Wilks' chi-square reference with 2 degrees of freedom does not give.
--null-calibration OUT ANALYSIS... [--replicates N] simulates H1 per usable
target of each retained analysis record: the arm rates are independent
normals about one common rate with the preregistered per-arm errors of
analyze_target (the weights of its fit), and every replicate runs the same
fit_h2, h2_errors and both conjuncts of detects. The normal draws of a target
come first, in order, from one generator seeded by the string
NULL_SEED/series/target, then blocks of NULL_BLOCK replicates map through
parallel.ordered_map, each block one fit_h2_batch call that returns
fit_h2's bits for every replicate (docs/notes/build_host/vectorized-fits.md).
OUT
records the empirical 0.999 quantile with a binomial order-statistic
interval, the null rate of the full rule at DETECT_DELTA_CHI2, the sha256 of
the full statistic list, of its first NULL_PREFIX replicates and of the kept
top NULL_TAIL fraction, and each target's observed statistic against its
quantile; the preregistered verdict fields stay as analyzed. --replay
recomputes the first NULL_PREFIX replicates from the recorded seeds and
rebuilds every quantile from the kept tail; --null-self-test checks the
contract on synthetic weights and fit_h2_batch against fit_h2 on adversarial
rates; --null-equivalence ANALYSIS... [--replicates N] fits the first
NULL_EQUIVALENCE replicates of every target stream with both and requires
identical bits. calibrated_threshold(weights) returns the quantile for a
future case.

--write DIR writes DIR/readout_ringdown_{tuna_17,qx}_{P,Q}/ (batch-NN/ case
directories and cases.json); --check DIR regenerates them and compares
bytes; --conformance schedules the emitted circuits ALAP, evolves them under
injected omega_q, every Tuna-17 coupler J_ab and an injected post-readout
tail, and requires the analysis to recover the tail with it on and to report
none with it off; --analyze OUT RUN_DIR... analyzes the collected batches of
one series (--replay compares OUT with its recomputation); --sanity RUN_DIR
checks one collected batch before the next is submitted.

Usage: "$PYTHON" scripts/qi_readout_ringdown_cases.py
       (--write DIR | --check DIR | --conformance | --analyze OUT RUN_DIR... [--replay] | --sanity RUN_DIR
        | --sensitivity OUT RUN_DIR... [--replay] | --sensitivity-self-test
        | --null-calibration OUT [ANALYSIS...] [--replicates N] [--replay] | --null-self-test
        | --null-equivalence ANALYSIS... [--replicates N])
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
from typing import Any, NamedTuple

import numpy as np
import numpy.typing as npt
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
Fit = tuple[float, float, float, float]
Floats = npt.NDArray[np.float64]


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


# The batched fit repeats the arithmetic of h2_at and fit_h2 for many rate
# vectors that share one weight pattern, and returns the scalar fit's bits.
# Three rules carry the equality. Builtin sum() over floats is Neumaier-
# compensated (CPython 3.12 and later), so fsum_rows repeats its update over
# the arms in order. Python's x ** 2 calls libm pow, which differs from x * x
# in the last place when the exact square lies near a rounding midpoint, and
# numpy's exp and power dispatch to their own SIMD kernels on some CPUs, so
# every exp and square that varies by replicate goes through math.exp and
# math.pow. numpy's + - * / and comparisons are IEEE operations, identical to
# Python's float operations.
# Relative margin of the grid prune; libm pow and x * x differ by an ulp.
GRID_PRUNE = 2.0**-30
# Absolute margin per unit weight; it covers squares in the subnormal range.
GRID_FLOOR = 2.0**-1000


def fsum_rows(terms: list[Floats]) -> Floats:
    """sum(terms) elementwise as builtin sum() evaluates it: 0 + the first term, then CPython's Neumaier update."""
    total = 0.0 + terms[0]
    comp = np.zeros_like(total)
    for term in terms[1:]:
        step = total + term
        comp = comp + np.where(np.abs(total) >= np.abs(term), (total - step) + term, (term - step) + total)
        total = step
    return np.where((comp != 0) & np.isfinite(comp), total + comp, total)


def libm_map(function: Any, values: Floats, *extra: float) -> Floats:
    """function(value, *extra) for every element through the math module, the libm calls of the scalar code."""
    flat = values.ravel().tolist()
    mapped = map(function, flat, *(itertools.repeat(x) for x in extra))
    return np.fromiter(mapped, np.float64, len(flat)).reshape(values.shape)


def decay(tau: int | None, tails: Floats) -> Floats:
    """exp(-tau / T) of h2_at for every element of tails; exp(0) is exactly 1 in every C99 libm."""
    if tau is None:
        return np.zeros_like(tails)
    if tau == 0:
        return np.ones_like(tails)
    return libm_map(math.exp, -tau / tails)


def h2_at_batch(
    tails: Floats, taus: Taus, y: list[Floats], weights: list[float], sy: Floats
) -> tuple[Floats, Floats, Floats]:
    """h2_at(tails[n], taus, rates[n], weights) for every row n, from the arm columns y of rates and their sy."""
    f = [decay(tau, tails) for tau in taus]
    sw = sum(weights)
    sf = fsum_rows([w * fi for w, fi in zip(weights, f, strict=True)])
    sff = fsum_rows([w * fi * fi for w, fi in zip(weights, f, strict=True)])
    sfy = fsum_rows([w * fi * yi for w, fi, yi in zip(weights, f, y, strict=True)])
    det = sw * sff - sf * sf
    if not det.all():
        raise ZeroDivisionError("float division by zero")
    a = (sw * sfy - sf * sy) / det
    c = (sff * sy - sf * sfy) / det
    chi2 = fsum_rows([w * libm_map(math.pow, yi - c - a * fi, 2.0) for w, yi, fi in zip(weights, y, f, strict=True)])
    return chi2, c, a


def grid_argmin(taus: Taus, rates: Floats, weights: list[float]) -> npt.NDArray[np.intp]:
    """The first index of the minimum of h2_at over T_GRID for every row of rates.

    The T-only sums come from builtin sum() over Python floats. The profile
    is first evaluated with r * r for the squares; pow(r, 2) and r * r agree
    to an ulp, so every exact minimizer lies within GRID_PRUNE of the fast
    minimum, and only those grid points are recomputed with libm pow.
    """
    grid_f = [[0.0 if tau is None else math.exp(-tau / t) for tau in taus] for t in T_GRID]
    sw = sum(weights)
    sf = np.array([sum(w * fi for w, fi in zip(weights, row, strict=True)) for row in grid_f])
    sff = np.array([sum(w * fi * fi for w, fi in zip(weights, row, strict=True)) for row in grid_f])
    det = sw * sff - sf * sf
    if not det.all():
        raise ZeroDivisionError("float division by zero")
    f = list(np.array(grid_f).T)
    y = [column[:, None] for column in rates.T]
    sy = fsum_rows([w * yi for w, yi in zip(weights, y, strict=True)])
    sfy = fsum_rows([w * fi * yi for w, fi, yi in zip(weights, f, y, strict=True)])
    a = (sw * sfy - sf * sy) / det
    c = (sff * sy - sf * sfy) / det
    residuals = [yi - c - a * fi for yi, fi in zip(y, f, strict=True)]
    fast = fsum_rows([w * (r * r) for w, r in zip(weights, residuals, strict=True)])
    near = fast <= fast.min(axis=1, keepdims=True) * (1 + GRID_PRUNE) + sw * GRID_FLOOR
    exact = np.full(fast.shape, np.inf)
    exact[near] = fsum_rows([w * libm_map(math.pow, r[near], 2.0) for w, r in zip(weights, residuals, strict=True)])
    return np.argmin(exact, axis=1)


def fit_h2_batch(taus: Taus, rates: Floats, weights: list[float]) -> tuple[Floats, Floats, Floats, Floats]:
    """fit_h2 for every row of rates (replicates x arms): arrays of chi2, c, A and T.

    The golden section runs every row's step at once; each row takes the
    scalar branch f_left <= f_right, and np.argmin takes the first minimum
    as min(..., key=...) does.
    """
    with np.errstate(over="raise", invalid="raise", divide="raise"):
        y = [np.ascontiguousarray(column) for column in rates.T]
        sy = fsum_rows([w * yi for w, yi in zip(weights, y, strict=True)])

        def chi2_at(tails: Floats) -> Floats:
            return h2_at_batch(tails, taus, y, weights, sy)[0]

        grid = np.array(T_GRID)
        k = grid_argmin(taus, rates, weights)
        below, above = grid[np.maximum(k - 1, 0)], grid[np.minimum(k + 1, len(T_GRID) - 1)]
        low, high = below, above
        ratio = (math.sqrt(5) - 1) / 2
        left, right = high - ratio * (high - low), low + ratio * (high - low)
        f_left, f_right = chi2_at(left), chi2_at(right)
        for _ in range(GOLDEN_STEPS):
            shrink = f_left <= f_right
            high = np.where(shrink, right, high)
            low = np.where(shrink, low, left)
            point = np.where(shrink, high - ratio * (high - low), low + ratio * (high - low))
            value = chi2_at(point)
            left, right = np.where(shrink, point, right), np.where(shrink, left, point)
            f_left, f_right = np.where(shrink, value, f_right), np.where(shrink, f_left, value)
        candidates = np.stack([grid[k], left, right, below, above], axis=1)
        profile = np.stack([chi2_at(t) for t in candidates.T], axis=1)
        best = candidates[np.arange(len(rates)), np.argmin(profile, axis=1)]
        chi2, c, a = h2_at_batch(best, taus, y, weights, sy)
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


def h2_design(
    taus: Taus, weights: list[float], a: float, tail: float
) -> tuple[list[list[float]], list[list[float]] | None, bool]:
    """(design rows, covariance, T free): the Fisher inverse of (c, A, T), or of (c, A) with T at a bound or A zero."""
    rows = []
    for tau in taus:
        f = 0.0 if tau is None else math.exp(-tau / tail)
        rows.append([1.0, f, 0.0 if tau is None else a * tau / tail**2 * f])
    fisher = [[sum(w * r[i] * r[j] for w, r in zip(weights, rows, strict=True)) for j in range(3)] for i in range(3)]
    if T_BOUNDS[0] < tail < T_BOUNDS[1] and a != 0:
        covariance = inverse(fisher)
        if covariance is not None and covariance[1][1] > 0 and covariance[2][2] > 0:
            return rows, covariance, True
    fixed = inverse([row[:2] for row in fisher[:2]])
    if fixed is None or fixed[1][1] <= 0:
        return rows, None, False
    return rows, fixed, False


def h2_errors(taus: Taus, weights: list[float], a: float, tail: float) -> tuple[float, float | None]:
    """se(A) and se(T) from the Fisher matrix of (c, A, T); T held fixed at a bound or when A vanishes."""
    _, covariance, free = h2_design(taus, weights, a, tail)
    if covariance is None:
        return math.inf, None
    return math.sqrt(covariance[1][1]), math.sqrt(covariance[2][2]) if free else None


def gain(tail: float) -> float:
    """g(T) = A / S: the rate offset at tau = 0 per unit of frequency shift S at the readout end."""
    return tail * (math.exp(-(DELAYS[0] + 1) / tail) - math.exp(-(DELAYS[1] + 1) / tail)) / SPAN


def detects(delta_chi2: float, a: float, se_a: float) -> bool:
    """Both conjuncts of the tail rule: the chi2 gain of H2 over H1 and the significance of A."""
    return delta_chi2 >= DETECT_DELTA_CHI2 and abs(a) >= DETECT_SIGMA * se_a


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
    significant = detects(chi2_h1 - chi2_h2, a, se_a)
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


def sanity(
    run: Path, readout_error: float = SANITY_READOUT_ERROR, exempt: frozenset[int] = frozenset()
) -> tuple[list[str], list[str]]:
    """Checks one collected batch must pass before the next batch is submitted, and what the result carried.

    Every job completed with its requested shots; every shot carries n
    characters (the measurement register) or the 2 n-bit register, and the
    notes record which; in a readout circuit every target's assignment error
    stays below readout_error (SANITY_READOUT_ERROR unless a series names its
    own guard, which the notes record; a qubit in exempt is reported instead); in a Ramsey circuit every spectator, held
    in |0>, reads 1 below SANITY_SPECTATOR_ONE (a qubit in exempt is reported
    in the notes instead) and, where the 2 n-bit register
    returns, every target's mid-circuit outcome reads 1 below SANITY_MID_ONE (an
    exempt target is reported instead, since its readout error alone sets that
    rate). A
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
    exempt_notes: list[str] = []
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
                f"{row['file']} q{q}: error {error[q]:.3f}"
                for q in meta["targets"]
                if error[q] > readout_error and q not in exempt
            ]
            exempt_notes += [f"{row['file']} exempt q{q}: error {error[q]:.3f}" for q in meta["targets"] if q in exempt]
            continue
        if present and not row["file"].startswith(REFERENCE):
            for t in meta["targets"]:
                mid = sum(bit(s, n + t) for s in shots) / len(shots)
                if t in exempt:
                    exempt_notes.append(f"{row['file']} exempt q{t}: mid-circuit P1 {mid:.3f}")
                elif mid > SANITY_MID_ONE:
                    problems.append(f"{row['file']} q{t}: mid-circuit P1 {mid:.3f}")
        problems += [
            f"{row['file']} spectator q{q}: P1 {ones[q]:.3f}"
            for q in meta["spectators"]
            if ones[q] > SANITY_SPECTATOR_ONE and q not in exempt
        ]
        exempt_notes += [
            f"{row['file']} exempt spectator q{q}: P1 {ones[q]:.3f}" for q in meta["spectators"] if q in exempt
        ]
    notes = list(exempt_notes)
    for width in sorted(seen):
        if width == n:
            notes.append(f"register width {width}: measurement register only: mid-circuit outcomes absent")
        else:
            notes.append(f"register width {width}: full bit register: mid-circuit outcomes present")
    return problems, notes


def load_runs(
    runs: list[Path],
) -> tuple[str, dict[str, Any], list[tuple[str, str]], dict[str, list[str]], dict[str, int]]:
    """(profile, meta, circuits, shots by file, batch index by file) of the listed batches of one series."""
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
    return profile, meta, ordered, shots, batch_of


def analyze(runs: list[Path]) -> dict[str, Any]:
    profile, meta, ordered, shots, batch_of = load_runs(runs)
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


SENSITIVITY_METHOD = (
    "Beside the preregistered verdict, which stays as analyzed: the readout-0 and readout-1 counts give e01 and e10 "
    "binomial variances; the analytic column propagates them through every quadrature, phase, rate, delta and the "
    "minimum visibility with the one assignment pair shared by all arms, and through A as the central-difference "
    "derivative (half-step 1e-4) of the complete weighted fit, whose weights also depend on the assignment; "
    "the bootstrap column redraws every readout "
    "count and every Ramsey count binomially from the observed fractions, recomputes the assignment and the full "
    "analysis per replicate, and reports the standard deviation of each quantity (rates and deltas as offsets on "
    "the circle). The spread is the normal-theory standard deviation of a standard deviation over the replicates."
)
CALIBRATION_REPLICATES = 2000
CALIBRATION_SEED = 182
AGREEMENT_SIGMA = 3.0
RATE_PERIOD_HZ = 2 * math.pi / SPAN * TO_HZ
Counts = dict[int, tuple[int, int, int, int]]


class PhaseTerms(NamedTuple):
    """Phase and visibility of one arm and delay, each with its shot variance and its (e01, e10) gradient."""

    phase: float
    variance: float
    d_phase: list[float]
    visibility: float
    visibility_variance: float
    d_visibility: list[float]


def calibration_counts(targets: list[int], zero: list[str], one: list[str]) -> Counts:
    """(shots, ones) of readout-0 and (shots, zeros) of readout-1 per target: the counts behind e01 and e10."""
    return {t: (len(zero), sum(bit(s, t) for s in zero), len(one), sum(1 - bit(s, t) for s in one)) for t in targets}


def assignment_of(counts: Counts) -> dict[int, tuple[float, float]]:
    return {t: (k0 / n0, k1 / n1) for t, (n0, k0, n1, k1) in counts.items()}


def quadrature(p: float, kept: float, e01: float, e10: float) -> tuple[float, float, float, float]:
    """(v, dv/de01, dv/de10, shot variance) of v = 2 (p - e01) / (1 - e01 - e10) - 1."""
    scale = 1 - e01 - e10
    centered = p - e01
    return (
        2 * centered / scale - 1,
        2 * (centered - scale) / scale**2,
        2 * centered / scale**2,
        4 * p * (1 - p) / kept / scale**2,
    )


def phase_terms(table: Table, arm: str, delay: int, target: int, e01: float, e10: float) -> PhaseTerms | None:
    """atan2 phase and visibility of one arm and delay with their shot variances and (e01, e10) gradients."""
    values = {}
    for q in QUADRATURES:
        ones, kept, _ = table[(arm, q, delay, target)]
        if kept <= 0:
            return None
        values[q] = quadrature(ones / kept, kept, e01, e10)
    (x, xa, xb, xv), (y, ya, yb, yv) = values["x"], values["y"]
    r2 = x * x + y * y
    if r2 <= 0:
        return PhaseTerms(math.atan2(y, x), math.inf, [math.inf] * 2, 0.0, math.inf, [math.inf] * 2)
    r = math.sqrt(r2)
    return PhaseTerms(
        math.atan2(y, x),
        (y * y * xv + x * x * yv) / r2**2,
        [(-y * xa + x * ya) / r2, (-y * xb + x * yb) / r2],
        r,
        (x * x * xv + y * y * yv) / r2,
        [(x * xa + y * ya) / r, (x * xb + y * yb) / r],
    )


FIT_STEP = 1e-4


def fit_gradient(target: int, table: Table, e01: float, e10: float, field: str = "A_hz") -> list[float]:
    """d/d(e01, e10) of one H2 fit output (Hz) by central differences of the complete analyze_target.

    A change of e01 or e10 moves the rates and also every phase variance, hence
    the weights of the fit, so the derivative of the estimator contains a weight
    term that a gain vector at fixed weights lacks. Each component uses the
    half-step FIT_STEP = 1e-4 (clipped at zero): the assignment errors are
    0.005 to 0.3, so the O(step^2) truncation is below 1e-6 relative to the
    scale of the fit, and the step stays far above the 1e-12 relative
    tolerance of the golden-section search over T.
    """
    gradient = []
    for e in range(2):
        point = [e01, e10]
        lo, hi = list(point), list(point)
        lo[e] = max(point[e] - FIT_STEP, 0.0)
        hi[e] = point[e] + FIT_STEP
        low = analyze_target(target, table, (lo[0], lo[1]))["h2"][field]
        high = analyze_target(target, table, (hi[0], hi[1]))["h2"][field]
        gradient.append((high - low) / (hi[e] - lo[e]))
    return gradient


def calibrated_errors(
    target: int, table: Table, counts: tuple[int, int, int, int], variance_scale: float = 1.0
) -> dict[str, Any] | None:
    """Standard errors of one target with the readout-assignment error carried alongside the shot noise.

    e01 = k0 / n0 and e10 = k1 / n1 are binomial estimates from the batch's
    readout-0 and readout-1 circuits, with variances e (1 - e) / n times
    variance_scale. Every arm and delay inverts the same pair, so the
    calibration shift of a rate is the Jacobian J of its phase turn over SPAN
    times (d e01, d e10), common to the arms. A delta subtracts the
    reference's Jacobian before squaring; A is differentiated through the
    complete fit, weights included (fit_gradient), so its calibration variance
    is sum_e (dA/de)^2 var(e); the minimum visibility carries the
    gradient of its own arm and delay. Each calibrated variance adds that
    term to the preregistered shot variance. variance_scale 0 returns the
    preregistered errors, which analyze_target keeps as the verdict.
    """
    n0, k0, n1, k1 = counts
    e01, e10 = k0 / n0, k1 / n1
    variances = [variance_scale * e01 * (1 - e01) / n0, variance_scale * e10 * (1 - e10) / n1]
    base = analyze_target(target, table, (e01, e10))
    if "rate_hz" not in base:
        return None
    terms = {arm: [phase_terms(table, arm, d, target, e01, e10) for d in DELAYS] for arm in ARMS}
    jacobian = {}
    for arm in ARMS:
        first, second = terms[arm]
        if not (first is not None and second is not None):
            raise AssertionError
        jacobian[arm] = [(second.d_phase[e] - first.d_phase[e]) / SPAN for e in range(2)]
    shot = {arm: base["rate_se_hz"][arm] / TO_HZ for arm in ARMS}

    def calibration(vector: list[float]) -> float:
        return sum(vector[e] ** 2 * variances[e] for e in range(2))

    rate_se = {arm: math.sqrt(shot[arm] ** 2 + calibration(jacobian[arm])) * TO_HZ for arm in ARMS}
    delta_se = {
        str(arm_tau(arm)): math.sqrt(
            shot[arm] ** 2
            + shot[REFERENCE] ** 2
            + calibration([jacobian[arm][e] - jacobian[REFERENCE][e] for e in range(2)])
        )
        * TO_HZ
        for arm in ARMS[1:]
    }
    shift = fit_gradient(target, table, e01, e10)
    a_se = math.sqrt(base["h2"]["A_se_hz"] ** 2 + sum(shift[e] ** 2 * variances[e] for e in range(2)))
    lowest = min(
        (term for pair in terms.values() for term in pair if term is not None), key=lambda term: term.visibility
    )
    return {
        "rate_se_hz": rate_se,
        "delta_se_hz": delta_se,
        "A_se_hz": a_se,
        "min_visibility_shot_se": math.sqrt(lowest.visibility_variance),
        "min_visibility_se": math.sqrt(lowest.visibility_variance + calibration(lowest.d_visibility)),
    }


class Replicate:
    """One joint resampling, analyzed twice on the same Ramsey counts, picklable for the pool.

    "full" inverts the resampled assignment; "fixed" inverts the observed one,
    so the pair differs by the calibration draw alone and its ratio isolates
    the calibration term from the shot-noise error.
    """

    def __init__(self, targets: list[int], keys: list[tuple[str, str, int, int]], kept: list[float], shots: Counts):
        self.targets, self.keys, self.kept, self.shots = targets, keys, kept, shots

    def __call__(self, draw: tuple[list[tuple[int, int]], list[float]]) -> dict[str, dict[int, dict[str, Any]]]:
        readout, ones = draw
        table = {k: (o, n, n) for k, o, n in zip(self.keys, ones, self.kept, strict=True)}
        out: dict[str, dict[int, dict[str, Any]]] = {"full": {}, "fixed": {}}
        for t, (k0, k1) in zip(self.targets, readout, strict=True):
            n0, observed0, n1, observed1 = self.shots[t]
            for name, assignment in (("full", (k0 / n0, k1 / n1)), ("fixed", (observed0 / n0, observed1 / n1))):
                row = analyze_target(t, table, assignment)
                out[name][t] = (
                    {
                        "delta_hz": row["delta_hz"],
                        "rate_hz": row["rate_hz"],
                        "A_hz": row["h2"]["A_hz"],
                        "min_visibility": row["min_visibility"],
                        "class": row["class"],
                    }
                    if "rate_hz" in row
                    else {}
                )
        return out


def bootstrap_draws(
    targets: list[int], table: Table, counts: Counts, replicates: int, rng: random.Random
) -> tuple[list[tuple[str, str, int, int]], list[tuple[list[tuple[int, int]], list[float]]]]:
    """Every replicate's counts, drawn in one pass in generator order before any analysis runs.

    Readout counts follow Binomial(n0, e01) and Binomial(n1, e10) per target
    in target order; each Ramsey entry follows Binomial(kept, ones / kept) in
    sorted key order.
    """
    keys = sorted(k for k in table if k[3] in targets)
    draws = []
    for _ in range(replicates):
        readout = []
        for t in targets:
            n0, k0, n1, k1 = counts[t]
            readout.append((rng.binomialvariate(n0, k0 / n0), rng.binomialvariate(n1, k1 / n1)))
        ones = [float(rng.binomialvariate(int(table[k][1]), table[k][0] / table[k][1])) for k in keys]
        draws.append((readout, ones))
    return keys, draws


def circular_spread(values: list[float], observed: float, period: float | None) -> float:
    """Standard deviation of values about their mean, each taken as the (wrapped) offset from observed."""
    offsets = [v - observed for v in values]
    if period is not None:
        offsets = [(o + period / 2) % period - period / 2 for o in offsets]
    mean = sum(offsets) / len(offsets)
    return math.sqrt(sum((o - mean) ** 2 for o in offsets) / (len(offsets) - 1))


def paired_spread(
    full: list[dict[str, Any]],
    fixed: list[dict[str, Any]],
    field: str,
    observed: float,
    period: float | None,
    arm: str | None = None,
) -> tuple[float, float]:
    """Spreads of one replicate field under the resampled and the observed assignment."""
    return (
        circular_spread([r[field] if arm is None else r[field][arm] for r in full], observed, period),
        circular_spread([r[field] if arm is None else r[field][arm] for r in fixed], observed, period),
    )


def leaf(prereg: float, analytic: float, boot: float, fixed: float, replicates: int) -> dict[str, float]:
    """One standard error under the estimators; spread is boot / sqrt(2 (B - 1)), the normal-theory sd of an sd.

    bootstrap_shot_only redraws the Ramsey counts around the observed
    assignment, so bootstrap / bootstrap_shot_only is the resampled
    calibration term against analytic / preregistered.
    """
    spread = boot / math.sqrt(2 * (replicates - 1))
    return {
        "preregistered": prereg,
        "analytic": analytic,
        "bootstrap": boot,
        "bootstrap_shot_only": fixed,
        "bootstrap_spread": spread,
        "analytic_minus_bootstrap_in_spreads": (analytic - boot) / spread if spread > 0 else 0.0,
        "preregistered_minus_bootstrap_shot_only_in_spreads": (prereg - fixed) / spread if spread > 0 else 0.0,
        "calibration_ratio_analytic": analytic / prereg if prereg > 0 else 1.0,
        "calibration_ratio_bootstrap": boot / fixed if fixed > 0 else 1.0,
    }


def sensitivity(
    meta: dict[str, Any], table: Table, counts: Counts, replicates: int = CALIBRATION_REPLICATES
) -> dict[str, Any]:
    """Per-target preregistered, analytic-calibrated and bootstrap standard errors of delta, rate, A and visibility."""
    targets = list(meta["targets"])
    rng = random.Random(CALIBRATION_SEED)
    keys, draws = bootstrap_draws(targets, table, counts, replicates, rng)
    kept = [table[k][1] for k in keys]
    results = ordered_map(Replicate(targets, keys, kept, counts), draws, min_items=1)
    assignment = assignment_of(counts)
    rows = []
    for t in targets:
        base = analyze_target(t, table, assignment[t])
        analytic = calibrated_errors(t, table, counts[t])
        n0, k0, n1, k1 = counts[t]
        row: dict[str, Any] = {
            "target": t,
            "usable": base["usable"],
            "class": base["class"],
            "readout_counts": {"shots_0": n0, "ones_in_0": k0, "shots_1": n1, "zeros_in_1": k1},
            "e01": assignment[t][0],
            "e10": assignment[t][1],
            "e01_se": math.sqrt(assignment[t][0] * (1 - assignment[t][0]) / n0),
            "e10_se": math.sqrt(assignment[t][1] * (1 - assignment[t][1]) / n1),
        }
        rows.append(row)
        if analytic is None:
            continue
        full = [r["full"][t] for r in results]
        fixed = [r["fixed"][t] for r in results]
        row["class_fraction"] = sum(r["class"] == base["class"] for r in full) / replicates

        row["min_visibility_se"] = leaf(
            analytic["min_visibility_shot_se"],
            analytic["min_visibility_se"],
            *paired_spread(full, fixed, "min_visibility", base["min_visibility"], None),
            replicates,
        )
        row["A_se_hz"] = leaf(
            base["h2"]["A_se_hz"],
            analytic["A_se_hz"],
            *paired_spread(full, fixed, "A_hz", base["h2"]["A_hz"], None),
            replicates,
        )
        row["rate_se_hz"] = {
            arm: leaf(
                base["rate_se_hz"][arm],
                analytic["rate_se_hz"][arm],
                *paired_spread(full, fixed, "rate_hz", base["rate_hz"][arm], RATE_PERIOD_HZ, arm),
                replicates,
            )
            for arm in ARMS
        }
        row["delta_se_hz"] = {
            tau: leaf(
                base["delta_se_hz"][tau],
                analytic["delta_se_hz"][tau],
                *paired_spread(full, fixed, "delta_hz", base["delta_hz"][tau], RATE_PERIOD_HZ, tau),
                replicates,
            )
            for tau in base["delta_se_hz"]
        }
    return {"targets": rows, "agreement": agreement(rows)}


def agreement(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Analytic against bootstrap over every usable target's standard errors, and the calibration term's size.

    Rates and deltas are linear in the phase turns, so the analytic and
    bootstrap errors must agree within AGREEMENT_SIGMA spreads. A and the
    minimum visibility are nonlinear (a fit with T at a bound, a minimum over
    arms), so their entries also carry the preregistered-against-shot-only
    gap, which exists without any calibration term.
    """
    groups: dict[str, list[tuple[str, dict[str, float]]]] = {"linear": [], "nonlinear": []}
    for row in rows:
        if not row["usable"] or "delta_se_hz" not in row:
            continue
        name = f"Q{row['target']}"
        groups["linear"] += [(f"{name} delta {tau}", item) for tau, item in row["delta_se_hz"].items()]
        groups["linear"] += [(f"{name} rate {arm}", item) for arm, item in row["rate_se_hz"].items()]
        groups["nonlinear"] += [(f"{name} A", row["A_se_hz"]), (f"{name} min_visibility", row["min_visibility_se"])]
    out: dict[str, Any] = {"agreement_sigma": AGREEMENT_SIGMA}
    for kind, entries in groups.items():
        z = [abs(item["analytic_minus_bootstrap_in_spreads"]) for _, item in entries]
        baseline = [abs(item["preregistered_minus_bootstrap_shot_only_in_spreads"]) for _, item in entries]
        ratios = [item["calibration_ratio_analytic"] for _, item in entries]
        out[kind] = {
            "entries": len(entries),
            "analytic_beyond_agreement": [
                name for (name, _), score in zip(entries, z, strict=True) if score > AGREEMENT_SIGMA
            ],
            "max_abs_analytic_minus_bootstrap_in_spreads": max(z, default=0.0),
            "max_abs_preregistered_minus_bootstrap_shot_only_in_spreads": max(baseline, default=0.0),
            "calibration_ratio_analytic": {"min": min(ratios, default=1.0), "max": max(ratios, default=1.0)},
        }
    return out


def sensitivity_report(runs: list[Path]) -> dict[str, Any]:
    profile, meta, ordered, shots, _ = load_runs(runs)
    counts = calibration_counts(meta["targets"], shots["readout-0.cq"], shots["readout-1.cq"])
    table, _ = tabulate(meta, {name: shots[name] for name, _ in ordered if not name.startswith("readout")})
    return {
        "schema": "qi-readout-ringdown-calibration-sensitivity-v1",
        "profile": profile,
        "series": meta["series"],
        "runs": [retained_path(r) for r in runs],
        "method": SENSITIVITY_METHOD,
        "replicates": CALIBRATION_REPLICATES,
        "seed": CALIBRATION_SEED,
        **sensitivity(meta, table, counts),
    }


def synthetic_series() -> tuple[dict[str, Any], Table, Counts]:
    """Two targets with exact Ramsey probabilities at known rates behind a known assignment channel."""
    targets = [0, 1]
    counts: Counts = {0: (8192, 246, 8192, 1229), 1: (8192, 123, 8192, 983)}
    assignment = assignment_of(counts)
    table: Table = {}
    for t in targets:
        e01, e10 = assignment[t]
        for index, arm in enumerate(ARMS):
            rate = 0.012 + 0.0025 * index + 0.004 * t
            for delay in DELAYS:
                phi = rate * (delay + 1) + 0.3
                for q, trig in (("x", math.cos), ("y", math.sin)):
                    p = e01 + (1 - e01 - e10) * (1 + 0.9 * trig(phi)) / 2
                    table[(arm, q, delay, t)] = (float(round(8192 * p)), 8192.0, 8192.0)
    return {"targets": targets, "series": "S"}, table, counts


def frozen_weight_gradient(target: int, table: Table, e01: float, e10: float) -> list[float]:
    """dA/d(e01, e10) with the fit weights held at their observed values: the rates move, the weights do not."""
    base = analyze_target(target, table, (e01, e10))
    taus: Taus = [arm_tau(arm) for arm in ARMS]
    weights = [1 / max(base["rate_se_hz"][arm] / TO_HZ, 1e-12) ** 2 for arm in ARMS]
    out = []
    for e in range(2):
        values = []
        for sign in (-1, 1):
            point = [e01, e10]
            point[e] += sign * FIT_STEP
            row = analyze_target(target, table, (point[0], point[1]))
            rates = [row["rate_hz"][arm] / TO_HZ for arm in ARMS]
            values.append(fit_h2(taus, rates, weights)[2] * TO_HZ)
        out.append((values[1] - values[0]) / (2 * FIT_STEP))
    return out


def sensitivity_self_test() -> str:
    """Contract of the sensitivity analysis on synthetic counts.

    (a) variance_scale 0 returns the preregistered rate, delta and A errors and the
    shot-only visibility error; (b) the calibration term of every delta equals
    the finite-difference gradient of analyze_target's delta times the
    binomial errors of e01 and e10; (c) the A calibration shift equals the central-difference
    gradient of the complete fit, which differs from the gradient at frozen weights and does not
    depend on the step; (d) a replay of the same counts is identical and a mutated readout count changes the record.
    """
    meta, table, counts = synthetic_series()
    step = 1e-6
    for t in meta["targets"]:
        n0, k0, n1, k1 = counts[t]
        e01, e10 = k0 / n0, k1 / n1
        base = analyze_target(t, table, (e01, e10))
        zero = calibrated_errors(t, table, counts[t], 0.0)
        full = calibrated_errors(t, table, counts[t])
        if not (zero is not None and full is not None):
            raise AssertionError
        pairs = [(zero["A_se_hz"], base["h2"]["A_se_hz"]), (zero["min_visibility_se"], zero["min_visibility_shot_se"])]
        pairs += [(zero["rate_se_hz"][arm], base["rate_se_hz"][arm]) for arm in ARMS]
        pairs += [(zero["delta_se_hz"][tau], base["delta_se_hz"][tau]) for tau in base["delta_se_hz"]]
        for got, want in pairs:
            if not math.isclose(got, want, rel_tol=1e-9):
                raise SystemExit(f"sensitivity self-test: zero calibration variance gives {got}, preregistered {want}")
        up = analyze_target(t, table, (e01 + step, e10))
        right = analyze_target(t, table, (e01, e10 + step))
        for tau, value in base["delta_hz"].items():
            gradient = [(other["delta_hz"][tau] - value) / step for other in (up, right)]
            variance = gradient[0] ** 2 * e01 * (1 - e01) / n0 + gradient[1] ** 2 * e10 * (1 - e10) / n1
            expected = full["delta_se_hz"][tau] ** 2 - base["delta_se_hz"][tau] ** 2
            if not math.isclose(variance, expected, rel_tol=1e-3):
                raise SystemExit(
                    f"sensitivity self-test: delta {tau} calibration variance {expected}, gradient {variance}"
                )
        gradient = fit_gradient(t, table, e01, e10)
        coarse = [
            (
                analyze_target(t, table, (e01 + (e == 0) * 4e-4, e10 + (e == 1) * 4e-4))["h2"]["A_hz"]
                - analyze_target(t, table, (e01 - (e == 0) * 4e-4, e10 - (e == 1) * 4e-4))["h2"]["A_hz"]
            )
            / 8e-4
            for e in range(2)
        ]
        frozen = frozen_weight_gradient(t, table, e01, e10)
        shift = math.sqrt(max(full["A_se_hz"] ** 2 - base["h2"]["A_se_hz"] ** 2, 0.0))
        expected = math.sqrt(gradient[0] ** 2 * e01 * (1 - e01) / n0 + gradient[1] ** 2 * e10 * (1 - e10) / n1)
        frozen_shift = math.sqrt(frozen[0] ** 2 * e01 * (1 - e01) / n0 + frozen[1] ** 2 * e10 * (1 - e10) / n1)
        if not math.isclose(shift, expected, rel_tol=1e-6, abs_tol=1e-9):
            raise SystemExit(
                f"sensitivity self-test: A calibration shift {shift} differs from the fit gradient {expected}"
            )
        if any(not math.isclose(g, c, rel_tol=1e-3, abs_tol=1e-3) for g, c in zip(gradient, coarse, strict=True)):
            raise SystemExit(f"sensitivity self-test: fit gradient {gradient} is step dependent ({coarse})")
        if math.isclose(expected, frozen_shift, rel_tol=1e-3):
            raise SystemExit("sensitivity self-test: the synthetic fit does not separate weight dependence")
    first = sensitivity(meta, table, counts, 24)
    if sensitivity(meta, table, counts, 24) != first:
        raise SystemExit("sensitivity self-test: a replay of the same counts differs")
    n0, k0, n1, k1 = counts[0]
    changed = sensitivity(meta, table, {**counts, 0: (n0, k0, n1, k1 + 40)}, 24)
    if changed == first or changed["targets"][0]["e10"] == first["targets"][0]["e10"]:
        raise SystemExit("sensitivity self-test: a mutated readout count leaves the record unchanged")
    if changed["targets"][0]["delta_se_hz"] == first["targets"][0]["delta_se_hz"]:
        raise SystemExit("sensitivity self-test: a mutated readout count leaves the delta errors unchanged")
    return (
        "sensitivity self-test: zero calibration variance reproduces the preregistered errors; "
        "gradients match; mutation changes the record"
    )


NULL_SCHEMA = "qi-readout-ringdown-null-calibration-v1"
NULL_REPLICATES = 200000
NULL_SEED = 183
NULL_QUANTILE = (999, 1000)
NULL_TAIL = 0.01
NULL_PREFIX = 5000
NULL_CONFIDENCE = 0.95
NULL_DECIMALS = 6
# Replicates per fit_h2_batch call: enough rows to amortize numpy's per-call
# cost over the golden-section steps, few enough that the NULL_BLOCK x
# len(T_GRID) grid arrays stay in cache.
NULL_BLOCK = 2048
# Replicates per target that --null-equivalence fits with both paths.
NULL_EQUIVALENCE = 2000


class NullFit:
    """One H1 replicate: standard normals scaled by the per-arm errors, then the identical fit and both conjuncts.

    The fit is invariant to the common rate c, so c = 0 loses no generality.
    The statistic is rounded to NULL_DECIMALS so that records agree across
    libm builds.
    """

    def __init__(self, weights: list[float]):
        self.weights = weights
        self.sigmas = [1 / math.sqrt(w) for w in weights]
        self.taus: Taus = [arm_tau(arm) for arm in ARMS]

    def rates(self, z: tuple[float, ...]) -> list[float]:
        return [s * v for s, v in zip(self.sigmas, z, strict=True)]

    def statistic(self, rates: list[float], fit: Fit) -> tuple[float, bool]:
        """(rounded delta chi2, joint detection) of one replicate from its H2 fit."""
        chi2_h2, _, a, tail = fit
        c1 = sum(w * y for w, y in zip(self.weights, rates, strict=True)) / sum(self.weights)
        chi2_h1 = sum(w * (y - c1) ** 2 for w, y in zip(self.weights, rates, strict=True))
        se_a = h2_errors(self.taus, self.weights, a, tail)[0]
        delta = chi2_h1 - chi2_h2
        return round(delta, NULL_DECIMALS) + 0.0, detects(delta, a, se_a)

    def __call__(self, z: tuple[float, ...]) -> tuple[tuple[float, bool], Fit]:
        rates = self.rates(z)
        fit = fit_h2(self.taus, rates, self.weights)
        return self.statistic(rates, fit), fit


class NullBlock(NullFit):
    """NullFit over a block of replicates: one fit_h2_batch call, then the per-replicate statistic."""

    def fit_rows(self, rows: list[list[float]]) -> list[tuple[tuple[float, bool], Fit]]:
        columns = fit_h2_batch(self.taus, np.array(rows), self.weights)
        fits: list[Fit] = list(zip(*(column.tolist() for column in columns), strict=True))
        return [(self.statistic(rates, fit), fit) for rates, fit in zip(rows, fits, strict=True)]

    def __call__(self, block: list[tuple[float, ...]]) -> list[tuple[tuple[float, bool], Fit]]:  # type: ignore[override]
        return self.fit_rows([self.rates(z) for z in block])


def null_draws(replicates: int, stream: str) -> list[tuple[float, ...]]:
    """The standard normals of every replicate, drawn in order from Random(stream) before any fit."""
    rng = random.Random(stream)
    return [tuple(rng.gauss(0.0, 1.0) for _ in ARMS) for _ in range(replicates)]


def null_fits(weights: list[float], replicates: int, stream: str) -> list[tuple[tuple[float, bool], Fit]]:
    """(statistic, H2 fit) of each H1 replicate; NULL_BLOCK replicates share one batched fit."""
    if len(weights) != len(ARMS):
        raise SystemExit(f"null statistics need {len(ARMS)} arm weights, got {len(weights)}")
    draws = null_draws(replicates, stream)
    blocks = [draws[start : start + NULL_BLOCK] for start in range(0, replicates, NULL_BLOCK)]
    return [item for block in ordered_map(NullBlock(weights), blocks, min_items=1) for item in block]


def null_statistics(weights: list[float], replicates: int, stream: str) -> list[tuple[float, bool]]:
    """(delta chi2, joint detection) of each H1 replicate; all normals are drawn first from Random(stream)."""
    return [stat for stat, _ in null_fits(weights, replicates, stream)]


def statistic_lines(stats: list[tuple[float, bool]]) -> str:
    return "".join(f"{delta:.{NULL_DECIMALS}f} {int(joint)}\n" for delta, joint in stats)


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("ascii")).hexdigest()


def tail_text(values: list[float]) -> str:
    return "".join(f"{v:.{NULL_DECIMALS}f}\n" for v in values)


def binomial_ranks(n: int, p: float, confidence: float) -> tuple[int | None, int | None]:
    """Ranks (l, u) with P(B < l) <= (1 - confidence) / 2 and P(B >= u) <= (1 - confidence) / 2 for B ~ Binomial(n, p).

    B counts the observations at or below the true p-quantile, so the order
    statistics X_(l) and X_(u) bracket it with at least `confidence`
    coverage; None marks a side the n observations cannot bound.
    """
    sd = math.sqrt(n * p * (1 - p))
    start = max(0, int(n * p - 60 * sd) - 5)
    pmf = {
        k: math.exp(
            math.lgamma(n + 1)
            - math.lgamma(k + 1)
            - math.lgamma(n - k + 1)
            + k * math.log(p)
            + (n - k) * math.log1p(-p)
        )
        for k in range(start, n + 1)
    }
    half = (1 - confidence) / 2
    lower: int | None = None
    below = 0.0
    for k in range(start, n + 1):
        if below > half:
            break
        lower = k
        below += pmf[k]
    upper: int | None = None
    above = 0.0
    for k in range(n, start - 1, -1):
        above += pmf[k]
        if above > half:
            break
        upper = k
    return lower, upper


def wilson(count: int, n: int, z: float = 1.959964) -> list[float]:
    p = count / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return [max(0.0, centre - half), min(1.0, centre + half)]


def quantile_from_tail(tail: list[float], n: int) -> dict[str, Any]:
    """The 0.999 order statistic and its binomial interval, read from the sorted top of the n statistics."""
    base = n - len(tail)
    rank = -(-n * NULL_QUANTILE[0] // NULL_QUANTILE[1])
    lower, upper = binomial_ranks(n, NULL_QUANTILE[0] / NULL_QUANTILE[1], NULL_CONFIDENCE)
    if rank <= base or lower is None or lower <= base:
        raise SystemExit(f"the kept tail of {len(tail)} of {n} statistics does not reach the 0.999 interval")
    return {
        "rank": rank,
        "value": tail[rank - 1 - base],
        "rank_lower": lower,
        "lower": tail[lower - 1 - base],
        "rank_upper": upper,
        "upper": None if upper is None else tail[upper - 1 - base],
        "confidence": NULL_CONFIDENCE,
    }


def null_target_record(weights: list[float], replicates: int, stream: str) -> dict[str, Any]:
    """The calibration of one weight pattern: quantile, exceedance counts, hashes and the kept tail."""
    stats = null_statistics(weights, replicates, stream)
    values = sorted(delta for delta, _ in stats)
    kept = max(1, int(replicates * NULL_TAIL))
    tail = values[-kept:]
    over = sum(delta >= DETECT_DELTA_CHI2 for delta, _ in stats)
    joint = sum(j for _, j in stats)
    prefix = min(replicates, NULL_PREFIX)
    return {
        "weights": weights,
        "stream": stream,
        "replicates": replicates,
        "quantile": quantile_from_tail(tail, replicates),
        "threshold": DETECT_DELTA_CHI2,
        "delta_exceedances": over,
        "delta_rate": over / replicates,
        "delta_rate_interval": wilson(over, replicates),
        "joint_exceedances": joint,
        "joint_rate": joint / replicates,
        "joint_rate_interval": wilson(joint, replicates),
        "statistic_sha256": sha(statistic_lines(stats)),
        "prefix_replicates": prefix,
        "prefix_sha256": sha(statistic_lines(stats[:prefix])),
        "tail_sha256": sha(tail_text(tail)),
        "tail": tail,
        "_values": values,
    }


def calibrated_threshold(weights: list[float], replicates: int = NULL_REPLICATES, stream: str = "threshold") -> float:
    """Empirical null 0.999 quantile of delta chi2 for the arm weights of a future case.

    A new series case carries max(DETECT_DELTA_CHI2, this value) as its
    preregistered threshold; replicates must be at least 1000 so that the
    quantile has a bounded interval.
    """
    if replicates < 1000:
        raise SystemExit("calibrated_threshold needs at least 1000 replicates")
    values = sorted(delta for delta, _ in null_statistics(weights, replicates, stream))
    return values[-(-replicates * NULL_QUANTILE[0] // NULL_QUANTILE[1]) - 1]


def arm_weights(row: dict[str, Any]) -> list[float]:
    """The fit weights of analyze_target, recovered from the retained per-arm errors."""
    return [1 / max(row["rate_se_hz"][arm] / TO_HZ, 1e-12) ** 2 for arm in ARMS]


def observed_fields(row: dict[str, Any]) -> dict[str, Any]:
    """The observed statistic of one analysis row, as the calibration record states it (without the null count)."""
    a_se = row["h2"]["A_se_hz"]
    return {
        "delta_chi2": row["delta_chi2"],
        "a_sigma": abs(row["h2"]["A_hz"]) / a_se if a_se else math.inf,
        "preregistered_class": row["class"],
    }


def readjudication(verdict: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Preregistered against calibrated flags from the observed fields and the calibrated quantiles of the rows."""
    calibrated = [
        r["target"]
        for r in rows
        if r["observed"]["delta_chi2"] >= r["quantile"]["value"] and r["observed"]["a_sigma"] >= DETECT_SIGMA
    ]
    flagged = [r["target"] for r in rows if r["observed"]["preregistered_class"] != "none"]
    return {
        "preregistered_verdict": verdict,
        "preregistered_flagged": flagged,
        "calibrated_flagged": calibrated,
        "dropped_by_calibration": sorted(set(flagged) - set(calibrated)),
        "added_by_calibration": sorted(set(calibrated) - set(flagged)),
    }


def null_series(analysis: dict[str, Any], replicates: int) -> list[dict[str, Any]]:
    """The calibrated target records of one series' usable targets."""
    rows = []
    for row in analysis["targets"]:
        if not row["usable"]:
            continue
        stream = f"{NULL_SEED}/{analysis['series']}/{row['target']}"
        rec = null_target_record(arm_weights(row), replicates, stream)
        values = rec.pop("_values")
        rec["target"] = row["target"]
        rec["observed"] = {
            **observed_fields(row),
            "null_exceedances": sum(v >= row["delta_chi2"] for v in values),
        }
        rows.append(rec)
    return rows


def null_calibration(analyses: list[Path], replicates: int) -> dict[str, Any]:
    """The calibration record over the usable targets of the given analysis records, one per series."""
    series: dict[str, Any] = {}
    for path in analyses:
        text = path.read_bytes()
        analysis = json.loads(text)
        if analysis["profile"] != "tuna_17" or analysis["series"] in series:
            raise SystemExit(f"{path}: expected one tuna_17 analysis per series")
        rows = null_series(analysis, replicates)
        series[analysis["series"]] = {
            "analysis": retained_path(path),
            "analysis_sha256": hashlib.sha256(text).hexdigest(),
            "targets": rows,
            "readjudication": readjudication(analysis["decision"]["verdict"], rows),
        }
    return {
        "schema": NULL_SCHEMA,
        "method": (
            "H1 replicates: independent normal arm rates about one common rate with the preregistered per-arm errors "
            "of analyze_target, the identical fit_h2, h2_errors and both conjuncts of detects; the normal draws of a "
            "target come first, in order, from Random(stream), then the fits map through parallel.ordered_map."
        ),
        "seed": NULL_SEED,
        "quantile": NULL_QUANTILE[0] / NULL_QUANTILE[1],
        "decimals": NULL_DECIMALS,
        "series": dict(sorted(series.items())),
    }


def check_null_target(rec: dict[str, Any]) -> None:
    """Replays the first replicates of one target and rebuilds its quantile, interval and tail hash from the tail."""
    n, tail = rec["replicates"], rec["tail"]
    if tail != sorted(tail) or len(tail) != max(1, int(n * NULL_TAIL)):
        raise SystemExit(f"{rec['stream']}: the kept tail is not the sorted top {NULL_TAIL} of the statistics")
    if sha(tail_text(tail)) != rec["tail_sha256"]:
        raise SystemExit(f"{rec['stream']}: the kept tail does not match its hash")
    if quantile_from_tail(tail, n) != rec["quantile"]:
        raise SystemExit(f"{rec['stream']}: the quantile differs from its recomputation from the tail")
    count = min(n, NULL_PREFIX)
    if rec["prefix_replicates"] != count:
        raise SystemExit(f"{rec['stream']}: the prefix length is not {count}")
    if sha(statistic_lines(null_statistics(rec["weights"], count, rec["stream"]))) != rec["prefix_sha256"]:
        raise SystemExit(f"{rec['stream']}: the first {count} replicates differ from their recomputation")
    if rec["threshold"] != DETECT_DELTA_CHI2:
        raise SystemExit(f"{rec['stream']}: the threshold is not DETECT_DELTA_CHI2 = {DETECT_DELTA_CHI2}")
    over = rec["delta_exceedances"]
    if DETECT_DELTA_CHI2 >= tail[0] and over != sum(v >= DETECT_DELTA_CHI2 for v in tail):
        raise SystemExit(f"{rec['stream']}: the delta chi2 exceedance count differs from the kept tail")
    if DETECT_DELTA_CHI2 < tail[0] and over < len(tail):
        raise SystemExit(f"{rec['stream']}: the delta chi2 exceedance count is below the kept tail")
    if over / n != rec["delta_rate"] or rec["joint_exceedances"] / n != rec["joint_rate"]:
        raise SystemExit(f"{rec['stream']}: an exceedance rate differs from its count")
    if rec["delta_rate_interval"] != wilson(over, n) or rec["joint_rate_interval"] != wilson(
        rec["joint_exceedances"], n
    ):
        raise SystemExit(f"{rec['stream']}: an exceedance-rate interval differs from its Wilson recomputation")
    if rec["joint_exceedances"] > rec["delta_exceedances"]:
        raise SystemExit(f"{rec['stream']}: the joint rule fires more often than its delta chi2 conjunct")
    observed = rec["observed"]["delta_chi2"]
    if observed >= tail[0] and rec["observed"]["null_exceedances"] != sum(v >= observed for v in tail):
        raise SystemExit(f"{rec['stream']}: the observed exceedance count differs from the kept tail")
    if observed < tail[0] and rec["observed"]["null_exceedances"] < len(tail):
        raise SystemExit(f"{rec['stream']}: the observed exceedance count is below the kept tail")


def check_null_series(name: str, block: dict[str, Any], analysis: dict[str, Any]) -> int:
    """Checks one series block against its analysis: observed fields, readjudication, then each target's replay."""
    rows = {row["target"]: row for row in analysis["targets"] if row["usable"]}
    if sorted(rows) != sorted(rec["target"] for rec in block["targets"]):
        raise SystemExit(f"series {name}: the calibrated targets differ from the usable targets")
    for rec in block["targets"]:
        row = rows[rec["target"]]
        if rec["stream"] != f"{NULL_SEED}/{name}/{rec['target']}":
            raise SystemExit(f"series {name}: target {rec['target']} has a foreign stream")
        if not all(math.isclose(a, b, rel_tol=1e-9) for a, b in zip(rec["weights"], arm_weights(row), strict=True)):
            raise SystemExit(f"series {name}: target {rec['target']} weights differ from the analysis errors")
        observed = rec["observed"]
        if {k: v for k, v in observed.items() if k != "null_exceedances"} != observed_fields(row) or set(observed) != {
            *observed_fields(row),
            "null_exceedances",
        }:
            raise SystemExit(f"series {name}: target {rec['target']} observed fields differ from the analysis")
    if block["readjudication"] != readjudication(analysis["decision"]["verdict"], block["targets"]):
        raise SystemExit(f"series {name}: the readjudication differs from its recomputation")
    for rec in block["targets"]:
        check_null_target(rec)
    return len(block["targets"])


def check_null_record(record: dict[str, Any]) -> int:
    """Replays a calibration record against its analysis records; returns the number of targets checked."""
    if record["schema"] != NULL_SCHEMA or record["seed"] != NULL_SEED:
        raise SystemExit("the calibration record has another schema or seed")
    checked = 0
    for name, block in record["series"].items():
        path = ROOT / block["analysis"]
        text = path.read_bytes()
        if hashlib.sha256(text).hexdigest() != block["analysis_sha256"]:
            raise SystemExit(f"{path}: the analysis differs from the one the calibration used")
        checked += check_null_series(name, block, json.loads(text))
    return checked


def fit_bits(fit: Fit) -> tuple[str, ...]:
    """The exact bits of a fit, signed zeros included."""
    return tuple(float(v).hex() for v in fit)


def compare_fits(name: str, scalar: list[Fit], batched: list[Fit]) -> int:
    """The number of bit-identical fits; any difference stops with its largest absolute and relative size."""
    same = sum(fit_bits(x) == fit_bits(y) for x, y in zip(scalar, batched, strict=True))
    if same != len(scalar):
        gaps = [
            (abs(u - v), abs(u - v) / max(abs(u), abs(v)) if u != v else 0.0)
            for x, y in zip(scalar, batched, strict=True)
            for u, v in zip(x, y, strict=True)
            if float(u).hex() != float(v).hex()
        ]
        raise SystemExit(
            f"{name}: {len(scalar) - same} of {len(scalar)} batched fits differ from fit_h2; "
            f"max abs {max(g[0] for g in gaps):.3e}, max rel {max(g[1] for g in gaps):.3e}"
        )
    return same


def null_equivalence(weights: list[float], replicates: int, stream: str) -> int:
    """Fits the first replicates of a stream with NullFit and with NullBlock; returns the equal count."""
    scalar = ordered_map(NullFit(weights), null_draws(replicates, stream), min_items=1)
    batched = null_fits(weights, replicates, stream)
    same = compare_fits(stream, [fit for _, fit in scalar], [fit for _, fit in batched])
    if [stat for stat, _ in scalar] != [stat for stat, _ in batched]:
        raise SystemExit(f"{stream}: the batched statistics differ from NullFit")
    return same


def null_equivalence_report(analyses: list[Path], replicates: int) -> str:
    """Bitwise equality of fit_h2_batch and fit_h2 on the record stream of every usable target."""
    lines = []
    for path in analyses:
        analysis = json.loads(path.read_bytes())
        for row in analysis["targets"]:
            if row["usable"]:
                stream = f"{NULL_SEED}/{analysis['series']}/{row['target']}"
                same = null_equivalence(arm_weights(row), replicates, stream)
                lines.append(f"{stream}: {same} of {replicates} fits and statistics bit-identical")
    return "\n".join(lines)


def fsum_cases() -> list[list[float]]:
    """Sums whose builtin result depends on the compensation, the start value or the zero sign."""
    rng = random.Random(f"{NULL_SEED}/fsum")
    cases = [
        [-0.0, -0.0, -0.0],
        [0.0, -0.0, 1.0, -1.0],
        [1e16, 1.0, -1e16, 1.0],
        [1.0, 1e100, 1.0, -1e100],
        [3.0, -3.0, 2.0**-1074, -(2.0**-1074)],
        [1e308, -1e308, 1e-308, 2.0],
    ]
    cases += [[rng.gauss(0.0, 1.0) * 10 ** rng.uniform(-8, 8) for _ in ARMS] for _ in range(4000)]
    return cases


def batch_cases() -> list[tuple[str, list[float], list[list[float]]]]:
    """(name, weights, rate rows) on which fit_h2_batch must reproduce fit_h2 bit for bit.

    Null draws under three weight patterns (synthetic, equal, and one arm at
    the 1e-12 error clamp of arm_weights), all-zero and constant rates whose
    profile ties at every grid point and every golden step, and noise-free
    and noisy decays at both T bounds and on a grid point.
    """
    taus = [arm_tau(arm) for arm in ARMS]
    synthetic = [4.0e6, 3.0e6, 2.0e6, 2.5e6, 3.5e6, 1.5e6]
    patterns = {"synthetic": synthetic, "equal": [1.0] * len(ARMS), "clamped": [1e24, *synthetic[1:]]}
    cases = []
    for name, weights in patterns.items():
        fit = NullFit(weights)
        cases.append((name, weights, [fit.rates(z) for z in null_draws(256, f"{NULL_SEED}/batch/{name}")]))
    rng = random.Random(f"{NULL_SEED}/batch/shapes")
    shapes = [[0.0] * len(ARMS), [-0.0] * len(ARMS), [1e-3] * len(ARMS), [-2.5e-4] * len(ARMS)]
    for tail in (T_BOUNDS[0], T_GRID[200], T_BOUNDS[1], 2.0, 400.0):
        decay_rates = [1e-4 + (0.0 if tau is None else 3e-3 * math.exp(-tau / tail)) for tau in taus]
        shapes.append(decay_rates)
        shapes += [[r + rng.gauss(0.0, 5e-4) for r in decay_rates] for _ in range(8)]
    cases.append(("shapes", synthetic, shapes))
    return cases


def batch_self_test() -> str:
    """fit_h2_batch and NullBlock against the scalar fit on batch_cases; fsum_rows against builtin sum."""
    sums = fsum_cases()
    for terms in sums:
        mine = fsum_rows([np.array([t]) for t in terms])[0]
        if float(mine).hex() != float(sum(terms)).hex():
            raise SystemExit(f"null self-test: fsum_rows gives {mine!r} where sum() gives {sum(terms)!r} on {terms}")
    taus: Taus = [arm_tau(arm) for arm in ARMS]
    total = 0
    for name, weights, rows in batch_cases():
        block = NullBlock(weights)
        scalar = [fit_h2(taus, rates, weights) for rates in rows]
        batched = block.fit_rows(rows)
        total += compare_fits(f"null self-test {name}", scalar, [fit for _, fit in batched])
        if [stat for stat, _ in batched] != [block.statistic(r, fit) for r, fit in zip(rows, scalar, strict=True)]:
            raise SystemExit(f"null self-test {name}: NullBlock statistics differ from the scalar fit")
    singular = [1.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    raised = []
    try:
        fit_h2(taus, [0.0] * len(ARMS), singular)
    except ZeroDivisionError:
        raised.append("fit_h2")
    try:
        fit_h2_batch(taus, np.zeros((1, len(ARMS))), singular)
    except ZeroDivisionError:
        raised.append("fit_h2_batch")
    if len(raised) != 2:
        raise SystemExit(f"null self-test: only {raised} raise on a singular weight pattern")
    return (
        f"{total} batched fits and {len(sums)} sums bit-identical to fit_h2 and sum(); "
        "a singular weight pattern raises in both paths"
    )


def null_self_test() -> str:
    """Contract on synthetic weights: a record replays; a mutated seed, tail value or weight fails."""
    weights = [4.0e6, 3.0e6, 2.0e6, 2.5e6, 3.5e6, 1.5e6]
    stream = f"{NULL_SEED}/S/0"
    rec = null_target_record(weights, 1000, stream)
    rec.pop("_values")
    rec["observed"] = {
        "delta_chi2": rec["tail"][-1],
        "a_sigma": 4.0,
        "preregistered_class": "tail",
        "null_exceedances": 1,
    }
    check_null_target(rec)
    if null_statistics(weights, 40, stream) != null_statistics(weights, 40, stream):
        raise SystemExit("null self-test: a replay of the same seed differs")
    if not 0 <= rec["joint_exceedances"] <= rec["delta_exceedances"]:
        raise SystemExit("null self-test: the joint rule fires more often than its conjunct")
    lower, upper = binomial_ranks(1000, 0.999, NULL_CONFIDENCE)
    if lower is None or upper is not None or not 990 < lower < 1000:
        raise SystemExit(f"null self-test: ranks {lower}, {upper} are not the order-statistic interval of 1000")
    mutations = {
        "seed": {**rec, "stream": f"{NULL_SEED + 1}/S/0"},
        "tail": {**rec, "tail": rec["tail"][1:]},
        "weight": {**rec, "weights": [weights[0] * 1.001, *weights[1:]]},
        "tail value": {**rec, "tail": [*rec["tail"][:-1], rec["tail"][-1] + 0.5]},
        "threshold": {**rec, "threshold": DETECT_DELTA_CHI2 + 1},
        "delta count": {
            **rec,
            "delta_exceedances": rec["delta_exceedances"] + 1,
            "delta_rate": (rec["delta_exceedances"] + 1) / rec["replicates"],
        },
        "delta interval": {**rec, "delta_rate_interval": wilson(rec["delta_exceedances"] + 1, rec["replicates"])},
        "joint interval": {**rec, "joint_rate_interval": wilson(rec["joint_exceedances"] + 1, rec["replicates"])},
    }
    for name, bad in mutations.items():
        try:
            check_null_target(bad)
        except SystemExit:
            continue
        raise SystemExit(f"null self-test: a mutated {name} is accepted")
    sigma = [1 / math.sqrt(w) * TO_HZ for w in weights]
    analysis: dict[str, Any] = {
        "series": "S",
        "decision": {"verdict": "not detected"},
        "targets": [
            {
                "target": t,
                "usable": True,
                "class": cls,
                "delta_chi2": delta,
                "rate_se_hz": dict(zip(ARMS, sigma, strict=True)),
                "h2": {"A_hz": 4.0, "A_se_hz": 1.0},
            }
            for t, cls, delta in ((0, "tail", 40.0), (1, "none", 2.0))
        ],
    }
    block: dict[str, Any] = {"targets": null_series(analysis, 1000), "readjudication": {}}
    block["readjudication"] = readjudication("not detected", block["targets"])
    if block["readjudication"]["calibrated_flagged"] != [0] or block["readjudication"]["dropped_by_calibration"]:
        raise SystemExit("null self-test: the synthetic readjudication is not the expected one")
    check_null_series("S", block, analysis)

    def edited(change: dict[str, Any], target: int | None = None) -> dict[str, Any]:
        targets = [
            {**r, "observed": {**r["observed"], **change}} if r["target"] == target else r for r in block["targets"]
        ]
        return (
            {**block, "targets": targets}
            if target is not None
            else {**block, "readjudication": {**block["readjudication"], **change}}
        )

    series_mutations = {
        "a_sigma": edited({"a_sigma": 9.0}, 0),
        "observed delta": edited({"delta_chi2": 41.0}, 0),
        "observed class": edited({"preregistered_class": "offset"}, 0),
        "calibrated_flagged": edited({"calibrated_flagged": [0, 1]}),
        "dropped_by_calibration": edited({"dropped_by_calibration": [0]}),
        "added_by_calibration": edited({"added_by_calibration": [1]}),
        "preregistered_verdict": edited({"preregistered_verdict": "readout tail detected"}),
    }
    for name, bad in series_mutations.items():
        try:
            check_null_series("S", bad, analysis)
        except SystemExit:
            continue
        raise SystemExit(f"null self-test: a mutated {name} is accepted")
    return (
        "null self-test: replay reproduces; mutated seed, dropped tail value, changed weight, threshold, "
        "delta count, rate intervals, a_sigma and readjudication fields are rejected; " + batch_self_test()
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--conformance", action="store_true")
    mode.add_argument("--analyze", type=Path, nargs="+", metavar=("OUT", "RUN_DIR"))
    mode.add_argument("--sanity", type=Path, metavar="RUN_DIR")
    mode.add_argument("--sensitivity", type=Path, nargs="+", metavar=("OUT", "RUN_DIR"))
    mode.add_argument("--sensitivity-self-test", action="store_true")
    mode.add_argument("--null-calibration", type=Path, nargs="+", metavar=("OUT", "ANALYSIS"))
    mode.add_argument("--null-self-test", action="store_true")
    mode.add_argument("--null-equivalence", type=Path, nargs="+", metavar="ANALYSIS")
    parser.add_argument(
        "--replicates",
        type=int,
        help=f"with --null-calibration (default {NULL_REPLICATES}) or --null-equivalence (default {NULL_EQUIVALENCE})",
    )
    parser.add_argument(
        "--replay", action="store_true", help="with --analyze or --sensitivity: compare OUT with the recomputation"
    )
    parser.add_argument(
        "--sanity-exempt",
        type=lambda value: frozenset(int(item) for item in value.split(",")),
        default=frozenset(),
        help="with --sanity: comma-separated qubits whose readout error or spectator P1 the notes report, unguarded",
    )
    parser.add_argument(
        "--sanity-readout-error",
        type=float,
        default=SANITY_READOUT_ERROR,
        help="with --sanity: the readout-circuit assignment-error guard for this series",
    )
    args = parser.parse_args()
    if args.sanity:
        problems, notes = sanity(args.sanity, args.sanity_readout_error, args.sanity_exempt)
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
    if args.null_self_test:
        print(null_self_test())
        return 0
    if args.null_equivalence:
        print(null_equivalence_report(args.null_equivalence, args.replicates or NULL_EQUIVALENCE))
        return 0
    if args.null_calibration:
        args.replicates = NULL_REPLICATES if args.replicates is None else args.replicates
        out, *analyses = args.null_calibration
        if args.replay:
            checked = check_null_record(json.loads(out.read_text(encoding="utf-8")))
            print(f"{out}: {checked} targets replay")
            return 0
        if not analyses or args.replicates < 1000:
            raise SystemExit("--null-calibration needs OUT, at least one ANALYSIS and --replicates of at least 1000")
        out.write_text(json.dumps(null_calibration(analyses, args.replicates), indent=1) + "\n", encoding="utf-8")
        print(f"null calibration -> {out}")
        return 0
    if args.sensitivity_self_test:
        print(sensitivity_self_test())
        return 0
    if args.sensitivity:
        out, *runs = args.sensitivity
        if not runs:
            raise SystemExit("--sensitivity needs OUT and at least one RUN_DIR")
        text = json.dumps(quantized(sensitivity_report(runs)), indent=1) + "\n"
        if args.replay:
            if out.read_text(encoding="utf-8") != text:
                raise SystemExit(f"{out} differs from its recomputation")
            print(f"{out}: sensitivity reproduces")
            return 0
        out.write_text(text, encoding="utf-8")
        print(f"sensitivity -> {out}")
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
