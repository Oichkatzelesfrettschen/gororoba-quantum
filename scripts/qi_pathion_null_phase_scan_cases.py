"""Tuna-17 case for the null block's selector offset (row A5-186): injected phase scans on q12 and on q8 at
coupler 8-12, and an angle scan on q4, of the retained b0.

The injected X-rotation scan (scripts/qi_pathion_null_rotation_scan_cases.py, verdict unresolved_none) left two
elementary errors ahead of its preregistered worlds in an exploratory reading
(docs/notes/quantum_inspire/tuna17-null-rotation-scan-line-phase.md): a rotation about z before each pulse of q12
and a conditional-phase error of the CZ gates of coupler 8-12. Both give a selector contrast that is even in the
error with exact pulses, so the retained offset fixes a size and leaves the sign open, and the retained arms vary
pulse amplitudes alone. This module builds the case that injects known phases on both sides of that coupler.

Mechanism. Tuna-17 lists `Rz(angle)` among its native operations and gives native single-qubit gates 20 ns under
as-late-as-possible scheduling (docs/notes/quantum_inspire/site/kbase_tuna-operational-specifics.md). OpenSquirrel
0.9.1, the platform's compiler, keeps `Rz(0.0)` as its own instruction and its scheduler exporter gives every `Rz`,
zero angle included, one 20 ns cycle (quantify_scheduler_exporter.py). Every circuit but the bridge's plain arm
therefore carries the same nine `Rz`: one before each of q12's five pulses and one on q8 after each of the four CZ
gates of coupler 8-12, at angle 0 where the arm injects nothing, so the arms share one schedule whatever an `Rz`
costs. hypothesis: the control stack after the compiler keeps a zero-angle `Rz` as well; the bridge batches, which
hold the predecessor's unpadded center beside the padded one, measure what the padding changes. Under a phase theta
on q12 the z12 contrast against the injected phi is the curve of the exact circuit shifted by -theta; under a
conditional phase of coupler 8-12 the curve keeps a nonzero least value and the d2 split of the outer arms departs
from its center's; the z8c arms, a phase on q8 after each CZ of the coupler, separate the two worlds most and fit
a third error world, a phase on q8 itself, which otherwise reads as the coupler's phase.

Circuits. Every circuit is the retained b0 text with each X90 as Rx(pi/2). "b0-rx" is the predecessor's center arm
byte for byte (rs.arm_lines). Every "b0-rxz" arm adds the nine `Rz` and one rewrite: "-q4-mK" / "-pK" put q4's
eight pulses at 90 -+ K degrees, "-z12-mK" / "-pK" give the five q12 `Rz` the angle -+K degrees, "-z8c-mK" / "-pK"
give the four q8 `Rz` the angle -+K degrees. Angles are multiples of pi/36.

Series. Fourteen data batches [first arm, b0-rxz, second arm] in a forward round and a mirror round with the outer
arms exchanged: two bridge batches ([b0-rx, b0-rxz, b0-rx]), two batches of each z12 kind (+-10 and +-30 degrees),
four z8c batches (+-10 degrees) and two batches of each q4 kind (+-5 and +-10 degrees); a readout batch
[readout-0, readout-1] before and after every data batch supplies the assignment matrix and the readout admission
of the predecessor.

Decision. For each world of WORLDS, fit_batch() fits the world's one parameter to the three raw selector contrasts
of a z12 or z8c batch and to the d2 split of each outer arm less the center arm's, at the retention that reproduces
the center arm's visibility, for each noise model of noise_models() (the contraction shares of the predecessor's
MIX_FINE and CZ damping at multiples of CZ_DAMPING) and each readout flip of FLIP_GRID composed onto the batch's
assignment matrix; decide() sums the chi-squares over the admitted batches of the deciding kinds at the one noise
model and flip that make the sum least, and a deciding label also needs each deciding kind to agree with the
series. preregistered() states the rules and operating_characteristics() simulates them.

Usage: "$PYTHON" scripts/qi_pathion_null_phase_scan_cases.py
       (--write DIR | --check DIR | --sanity RUN_DIR... | --analyze RUN_DIR... --out FILE | --self-test)
Bit strings put qubit 0 at the rightmost character."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import tempfile
from functools import cache
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import beta as beta_law
from scipy.stats import chi2 as chi2_law

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import qi_pathion_null_rotation_scan_cases as rs  # noqa: E402

import elementary_error_laws as el  # noqa: E402
from parallel import ordered_map  # noqa: E402

cc, oc, pca, pcs, zd = rs.cc, rs.oc, rs.pca, rs.pcs, rs.zd

TUNA_SERIES = "pathion_null_phase_scan_tuna_17"
QX_SERIES = "pathion_null_phase_scan_qx"
SCHEMA = "qi-pathion-null-phase-scan-cases-v1"
SERIES_SCHEMA = "qi-pathion-null-phase-scan-series-v1"
ANALYSIS_SCHEMA = "qi-pathion-null-phase-scan-analysis-v1"
PREDECESSOR_ANALYSIS = "results/quantum_inspire/pathion_null_rotation_scan_tuna_17_analysis.json"
KEYS, NOUT, STEP = rs.KEYS, rs.NOUT, rs.STEP
# The predecessor's center arm, emitted unpadded, and the padded center of every data batch.
PLAIN, CENTER = rs.CENTER, "b0-rxz"
Q4, Q8, Q12 = 4, 8, 12
COUPLER = (8, 12)

# Arm -> (steps of pi/36 added to each q4 pulse angle, steps of pi/36 of the Rz before each q12 pulse, steps of
# pi/36 of the Rz on q8 after each CZ of coupler 8-12). Every arm but PLAIN carries all nine Rz.
ARMS: dict[str, tuple[int, int, int]] = {
    PLAIN: (0, 0, 0),
    CENTER: (0, 0, 0),
    "b0-rxz-q4-m10": (-2, 0, 0),
    "b0-rxz-q4-m5": (-1, 0, 0),
    "b0-rxz-q4-p5": (1, 0, 0),
    "b0-rxz-q4-p10": (2, 0, 0),
    "b0-rxz-z12-m30": (0, -6, 0),
    "b0-rxz-z12-m10": (0, -2, 0),
    "b0-rxz-z12-p10": (0, 2, 0),
    "b0-rxz-z12-p30": (0, 6, 0),
    "b0-rxz-z8c-m10": (0, 0, -2),
    "b0-rxz-z8c-p10": (0, 0, 2),
}
ARM_NAMES = tuple(ARMS)
# Scan kind -> (first arm, second arm) of its forward batch; the mirror batch exchanges them.
SCANS: dict[str, tuple[str, str]] = {
    "bridge": (PLAIN, f"{PLAIN}-repeat"),
    "z12-10": ("b0-rxz-z12-m10", "b0-rxz-z12-p10"),
    "z12-30": ("b0-rxz-z12-m30", "b0-rxz-z12-p30"),
    "z8c-10": ("b0-rxz-z8c-m10", "b0-rxz-z8c-p10"),
    "q4-near": ("b0-rxz-q4-m5", "b0-rxz-q4-p5"),
    "q4-far": ("b0-rxz-q4-m10", "b0-rxz-q4-p10"),
}
# The forward round; the mirror round runs it backwards with the outer arms exchanged. z8c appears twice per round.
FIRST_ROUND = ("bridge", "z12-10", "z8c-10", "q4-near", "z12-30", "q4-far", "z8c-10")
Z12_KINDS = ("z12-10", "z12-30")
DECIDING_KINDS = (*Z12_KINDS, "z8c-10")
Q4_KINDS = ("q4-near", "q4-far")

SCAN_SHOTS, READOUT_SHOTS, QX_SHOTS = rs.SCAN_SHOTS, rs.READOUT_SHOTS, rs.QX_SHOTS
QX_QUBITS, QX_BATCH_CIRCUITS = rs.QX_QUBITS, rs.QX_BATCH_CIRCUITS
PAUSE_CEILING = rs.PAUSE_CEILING
DESIGN_VISIBILITY = 0.42

AFTER_PULSE = "q12_phase_after_pulse"
Q8_PHASE = "q8_phase_at_coupler"
# Worlds of the decision: exact gates, a rotation about z before each pulse of q12, a conditional-phase error of
# each CZ of coupler 8-12, and a rotation about z on q8 after each CZ of coupler 8-12 (the error the z8c arms
# inject). Without the q8 world a q8 phase near +-0.1 rad or -0.17 rad read coupler_phase at expected values; with
# it those truths fit their own world and the coupler world lies 11 to 250 above. The parameter grid of the error
# worlds is in radians.
THETA = np.linspace(-0.50, 0.50, 501)
WORLDS: dict[str, np.ndarray] = {"exact": np.zeros(1), "q12_phase": THETA, "coupler_phase": THETA, Q8_PHASE: THETA}
ERROR_WORLDS = tuple(w for w in WORLDS if w != "exact")
# A placement outside the decision that forward_laws also simulates: a rotation about z after each q12 pulse gives
# the laws of q12_phase (every q12 operation between two pulses is diagonal, the first rotation acts on |0> and the
# last precedes a measurement in z), so the q12_phase label names a single-qubit phase at q12's pulses and leaves
# its placement open.
# World -> the error item of gororoba_quantum/elementary_error_laws.py.
WORLD_ITEMS: dict[str, tuple[str, Any, Any]] = {
    "exact": ("none", None, None),
    "q12_phase": ("pulse", "zb", Q12),
    "coupler_phase": ("cz", COUPLER, None),
    AFTER_PULSE: ("pulse", "za", Q12),
    Q8_PHASE: ("czz", Q8, COUPLER),
}
ADEQUACY_ALPHA = rs.ADEQUACY_ALPHA
# The least error world must lie at least this far below every other, after the gap is divided by the least world's
# chi-square per degree of freedom when that exceeds 1 (the Birge scale factor squared): a world that fits worse than
# its noise allows separates less. A no-phase null outside the fit's noise models (a selector flip beside CZ or pulse
# phase damping) read q12_phase in exploratory draws at 1.26 to 1.97 per degree of freedom, leading the next world by
# up to 45 in the unscaled sum and 29.0 scaled, while single q12 and coupler phases led by 24 to 384 scaled. On
# value 9 of OC_DRAW no scenario read a deciding label of another world at 30, 35 or 40
# (docs/evidence/qi-null-phase-scan-decision-probes/separation_calibration.json); on value 10 at 30, the null with
# flip 0.025 and CZ phase damping 0.13 read q12_phase in 1 of 500 series. The threshold is fixed at 40, where value 9
# left every q12 and coupler truth's counts unchanged and the cost falls on q8 phases of 0.17 rad and less.
SEPARATION = 40.0
# A deciding kind disagrees with the series' world when it reads another error world lower by more than this, the
# upper 0.01 point of chi-square with one degree of freedom. Fixed on value 0 of OC_DRAW for the two-error-world
# decision: at 0, single mechanisms read phase_mixed in up to 94 of 500 series (the +-10 degree z12 kind separates
# the error worlds by 3 to 48); at 6.63 in at most 7, and a series whose z12 and z8c batches follow different
# mechanisms reads a deciding label in 3 of 500 against 0. The q8 world joined after; the margin stays fixed.
KIND_MARGIN = 6.63
SEEN_CACHE: dict[tuple[str, tuple[str, ...], bytes, float, str], tuple[np.ndarray, np.ndarray, np.ndarray]] = {}
# Retention and visibility miss of a world's center arm per (world, damping, contraction share, matrix, center
# visibility); every arm tuple of the world at those arguments shares them.
RETENTION_CACHE: dict[tuple[str, float, float, bytes, float], tuple[np.ndarray, np.ndarray]] = {}
# Readout-flip nuisance: the selector read flips with probability f when d0 reads 0, the predecessor's readout world
# (a misread conditioned on another qubit's state, which the bracket circuits of all-0 and all-1 inputs do not
# measure). Every world is fitted at each f of FLIP_GRID composed onto each batch's own assignment matrix, one f per
# series and world, ties to the smaller f. Without it a true q12 or coupler phase beside a flip of 0.0166 to 0.042
# read none_adequate in 290 to 300 of 300 exploratory series; with it, its own label in 195 to 200 of 200
# (docs/evidence/qi-null-phase-scan-decision-probes/readout-flip/).
FLIP_GRID = tuple(round(0.0025 * k, 6) for k in range(25))
FLIP_QUBIT = KEYS.index("d0")
GUARD_LIMIT = rs.GUARD_LIMIT
Z_RESOLVE = rs.Z_RESOLVE
BATCH_FIELDS = rs.BATCH_FIELDS


# Circuits ---------------------------------------------------------------------------------------------------------


def arm_lines(arm: str, place: dict[int, int]) -> list[str]:
    """Instruction lines of an arm with physical qubit q written as place[q]."""
    if arm == PLAIN:
        return list(rs.arm_lines(PLAIN, place))
    q4_steps, z12_steps, z8c_steps = ARMS[arm]
    lines = []
    for gate, angle, qubits in rs.retained()["ops"]:
        where = ", ".join(f"q[{place[q]}]" for q in qubits)
        if gate == "X90":
            if qubits[0] == Q12:
                lines.append(f"Rz({z12_steps * STEP!r}) {where}")
            name = rs.rx_text(q4_steps if qubits[0] == Q4 else 0)
        else:
            name = gate if angle is None else f"{gate}({angle})"
        lines.append(f"{name} {where}")
        if gate == "CZ" and tuple(sorted(qubits)) == COUPLER:
            lines.append(f"Rz({z8c_steps * STEP!r}) q[{place[Q8]}]")
    return lines


def arm_operations(arm: str) -> list[tuple[str, float | None, tuple[int, ...]]]:
    """The operations arm_lines emits, on physical qubits, for the forward model."""
    if arm == PLAIN:
        return [(g, a, tuple(q)) for g, a, q in rs.retained()["ops"]]
    _, z12_steps, z8c_steps = ARMS[arm]
    ops: list[tuple[str, float | None, tuple[int, ...]]] = []
    for gate, angle, qubits in rs.retained()["ops"]:
        if gate == "X90" and qubits[0] == Q12:
            ops.append(("Rz", z12_steps * STEP, (Q12,)))
        ops.append((gate, angle, tuple(qubits)))
        if gate == "CZ" and tuple(sorted(qubits)) == COUPLER:
            ops.append(("Rz", z8c_steps * STEP, (Q8,)))
    return ops


def arm_note(arm: str) -> str:
    base = f"{rs.retained()['note']} every X90 as Rx(pi/2)"
    if arm == PLAIN:
        return base
    q4_steps, z12_steps, z8c_steps = ARMS[arm]
    parts = [
        f"Rz({z12_steps * 5:+d} degrees) before each pulse of q12",
        f"Rz({z8c_steps * 5:+d} degrees) on q8 after each CZ of coupler 8-12",
    ]
    if q4_steps:
        parts.insert(0, f"{q4_steps * 5:+d} degrees on q4")
    return f"{base}, " + ", ".join(parts)


def arm_text(arm: str, place: dict[int, int], nqubits: int) -> str:
    lines = zd.header(nqubits) + [arm_note(arm)]
    return "\n".join(lines + arm_lines(arm, place) + ["", "barrier q", "b = measure q", ""])


def center_check() -> None:
    """The plain arm equals the predecessor's center arm byte for byte."""
    region = rs.retained()["region"]
    place = {q: q for q in region}
    if arm_text(PLAIN, place, cc.NQUBITS) != rs.arm_text(PLAIN, place, cc.NQUBITS):
        raise ValueError("the plain arm differs from the predecessor's b0-rx")


# Forward model ----------------------------------------------------------------------------------------------------

# Gate noise of a truth: (pulse amplitude damping, pulse phase damping, CZ amplitude damping, CZ phase damping),
# each channel after its gate on every qubit it acts on.
Noise = tuple[float, float, float, float]


def outcome_qubits() -> list[int]:
    """Region qubits in the order of the logical outcome index, most significant first."""
    roles = rs.retained()["roles"]
    return [roles[key] for key in reversed(KEYS)]


def forward_laws(arm: str, world: str, thetas: np.ndarray, noise: Noise | None = None) -> np.ndarray:
    """Laws over the logical outcome index of an arm under a world, one row per value of `thetas`, from
    gororoba_quantum/elementary_error_laws.py: a state vector over the five region qubits, or a density matrix under
    `noise`. The world's error acts beside the arm's own Rz (q12_phase before each q12 pulse, after the injected Rz;
    coupler_phase as the conditional phase pi + theta of each CZ of coupler 8-12)."""
    if world not in WORLD_ITEMS:
        raise ValueError(f"unknown world {world}")
    q4_steps = ARMS[arm][0]
    args = (
        arm_operations(arm),
        rs.retained()["region"],
        outcome_qubits(),
        {Q4: math.pi / 2 + q4_steps * STEP},
        [(WORLD_ITEMS[world], np.asarray(thetas, dtype=float))],
    )
    if noise is None or not any(noise):
        return np.asarray(el.error_laws(*args), dtype=float)
    pulse_amplitude, pulse_phase, cz_amplitude, cz_phase = noise
    pulse_kraus = el.damping_kraus(pulse_amplitude, pulse_phase) if pulse_amplitude or pulse_phase else []
    cz_kraus = el.damping_kraus(cz_amplitude, cz_phase) if cz_amplitude or cz_phase else []
    return np.asarray(el.channel_laws(*args, pulse_kraus=pulse_kraus, cz_kraus=cz_kraus), dtype=float)


def forward_law(arm: str, world: str = "exact", theta: float = 0.0, noise: Noise | None = None) -> np.ndarray:
    return np.asarray(forward_laws(arm_of(arm), world, np.array([theta]), noise)[0])


# CZ damping of the predecessor's retained histograms: the CZ terms (amplitude 0.0194, phase 0.0311 per CZ qubit) of
# the refit with five noise terms and a selector flip of 0.0166, histogram chi-square 51,570 on 924 degrees of
# freedom against 182,795 on 920 for the exact circuit with ten per-batch retentions
# (results/quantum_inspire/pathion_null_rotation_scan_tuna_17_phase_refit.json of pull request 933, model
# five_noise_terms_selector_flip). The five terms without the flip fit phase 0.0323 at 51,767 on 925; the
# amplitude-to-phase ratios (0.623, 0.601) bracket this one's (0.613), and the fit scales it by 0 to 3.
CZ_DAMPING: Noise = (0.0, 0.0, 0.019, 0.031)
NO_NOISE: Noise = (0.0, 0.0, 0.0, 0.0)
# Noise models of the fit beside the contraction shares: CZ damping at multiples of CZ_DAMPING, each with a uniform
# contraction (share 0) at the retention that reproduces the center visibility. Laws are computed at every multiple:
# linear interpolation from a grid of 0.25 missed the arm laws by up to 0.0066, 2.4 contrast standard errors.
FIT_DAMPING = np.linspace(0.0, 3.0, 49)
# A noise model is eligible for a batch only when some retention reproduces its center visibility within this
# tolerance, 3 standard errors of a visibility at SCAN_SHOTS (the mean of four bin contrasts, each over a quarter of
# the shots, has the standard error of the whole-batch contrast, 1 / sqrt(shots)). Without it a model whose largest
# visibility lies below the batch's stayed eligible at retention 1.
VISIBILITY_TOLERANCE = Z_RESOLVE / math.sqrt(SCAN_SHOTS)
TABLE_VERSION = 2


def scaled(noise: Noise, factor: float) -> Noise:
    a, b, c, d = noise
    return (a * factor, b * factor, c * factor, d * factor)


# Noise-model sets of the fit: "all" is the preregistered fit; "contraction" keeps the contraction shares alone and
# serves tests that need no damped table.
MODEL_SETS = ("all", "contraction")


def noise_models(models: str = "all") -> tuple[str, ...]:
    """Names of the fit's noise models, in the order of the leading axis of seen_contrasts and fit_batch."""
    shares = tuple(f"contraction share {m:.4f}" for m in rs.MIX_FINE)
    return shares if models == "contraction" else (*shares, *(f"CZ damping x{k:.4f}" for k in FIT_DAMPING))


@cache
def table_directory() -> Path:
    """Scratch directory of the damped law tables, keyed by every input a table depends on: the bytes of the law
    module, the retained circuit, every arm's operations, every world's error item and the parameter grids."""
    key = json.dumps(
        [
            TABLE_VERSION,
            hashlib.sha256(Path(el.__file__).read_bytes()).hexdigest(),
            hashlib.sha256(rs.retained()["text"].encode()).hexdigest(),
            {arm: repr(arm_operations(arm)) for arm in ARM_NAMES},
            {world: repr(item) for world, item in WORLD_ITEMS.items()},
            [float(THETA[0]), float(THETA[-1]), len(THETA)],
            list(CZ_DAMPING),
            [float(k) for k in FIT_DAMPING],
        ],
        sort_keys=True,
    )
    root = Path(os.environ.get("GOROROBA_SCAN_TABLES") or Path(tempfile.gettempdir()) / "gororoba-quantum-phase-tables")
    path = root / hashlib.sha256(key.encode()).hexdigest()[:20]
    path.mkdir(parents=True, exist_ok=True)
    return path


@cache
def world_table(world: str, damping: float = 0.0) -> np.ndarray:
    """Laws of every arm on the world's parameter grid under CZ damping `damping` x CZ_DAMPING, shape (parameter,
    arm, outcome); a damped table is computed once and kept in table_directory()."""
    if not damping:
        return np.stack([forward_laws(arm, world, WORLDS[world]) for arm in ARM_NAMES], axis=1)
    path = table_directory() / f"{world}-{damping:.4f}.npy"
    if path.is_file():
        return np.asarray(np.load(path))
    noise = scaled(CZ_DAMPING, damping)
    table = np.stack([forward_laws(arm, world, WORLDS[world], noise) for arm in ARM_NAMES], axis=1)
    scratch = path.with_name(f".{path.name}.{os.getpid()}.npy")
    np.save(scratch, table)
    os.replace(scratch, path)
    return table


def table_item(item: tuple[str, float]) -> tuple[int, ...]:
    return tuple(world_table(*item).shape)


def build_tables() -> int:
    """Fill table_directory() with every damped table over the process pool, so later workers load them."""
    items = [(world, float(k)) for world in WORLDS for k in FIT_DAMPING if k]
    return len(ordered_map(table_item, items, min_items=2))


def center_retention(
    table: np.ndarray, matrix: np.ndarray, center_visibility: float, mix: float
) -> tuple[np.ndarray, np.ndarray]:
    """The retention per parameter at which the center arm reads `center_visibility`, and the distance per parameter
    from `center_visibility` to the range of center visibilities the retention grid reaches (0 inside it;
    interpolation clamps the retention at the grid's end outside it)."""
    center = table[:, [ARM_NAMES.index(CENTER)]]
    seen = np.stack(
        [rs.visibility(rs.read(rs.contract(center, float(r), mix), matrix))[:, 0] for r in rs.RETENTION_GRID]
    )
    retention = np.empty(seen.shape[1])
    for j in range(seen.shape[1]):
        order = np.argsort(seen[:, j])
        retention[j] = float(np.interp(center_visibility, seen[order, j], rs.RETENTION_GRID[order]))
    miss = np.maximum(0.0, np.maximum(center_visibility - seen.max(0), seen.min(0) - center_visibility))
    return retention, miss


def matched(
    table: np.ndarray,
    arms: tuple[str, ...],
    matrix: np.ndarray,
    center_visibility: float,
    mix: float,
    center: tuple[np.ndarray, np.ndarray] | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Raw selector contrasts of `arms` then the d2 split of each outer arm less the center arm's, shape (parameter,
    2 x arm - 1), then the retention and visibility miss of center_retention(), which `center` supplies when the
    caller holds them."""
    outer = [n for n, a in enumerate(arms) if a != CENTER]
    picked = [ARM_NAMES.index(arm_of(a)) for a in arms]
    retention, miss = center_retention(table, matrix, center_visibility, mix) if center is None else center
    read = rs.read(rs.contract(table[:, picked], retention, mix), matrix)
    split = rs.d2_split(read)[0]
    relative = split[..., outer] - split[..., [arms.index(CENTER)]]
    return np.concatenate([rs.selector_contrast(read), relative], axis=-1), retention, miss


def seen_contrasts(
    world: str, arms: tuple[str, ...], matrix: np.ndarray, center_visibility: float, models: str = "all"
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """matched() under every noise model of noise_models(): statistics, shape (model, parameter, 2 x arm - 1), then
    retentions and visibility misses, shape (model, parameter); the contraction shares of rs.MIX_FINE (interpolated
    from rs.MIX_GRID), then CZ damping at each FIT_DAMPING multiple. Results are kept per argument set; a simulation
    refits one set many times."""
    if models not in MODEL_SETS:
        raise ValueError(f"unknown noise-model set {models}")
    key = (world, arms, matrix.tobytes(), float(center_visibility), models)
    if key in SEEN_CACHE:
        return SEEN_CACHE[key]

    def center(damping: float, mix: float) -> tuple[np.ndarray, np.ndarray]:
        at = (world, damping, mix, key[2], key[3])
        if at not in RETENTION_CACHE:
            RETENTION_CACHE[at] = center_retention(world_table(world, damping), matrix, center_visibility, mix)
        return RETENTION_CACHE[at]

    shares = [
        matched(world_table(world), arms, matrix, center_visibility, float(mix), center(0.0, float(mix)))
        for mix in rs.MIX_GRID
    ]
    parts = [rs.fine_mix(np.stack([s[n] for s in shares])) for n in range(3)]
    if models != "contraction":
        damped = [
            matched(world_table(world, float(k)), arms, matrix, center_visibility, 0.0, center(float(k), 0.0))
            for k in FIT_DAMPING
        ]
        parts = [np.concatenate([parts[n], np.stack([d[n] for d in damped])]) for n in range(3)]
    SEEN_CACHE[key] = (parts[0], parts[1], parts[2])
    return SEEN_CACHE[key]


def fit_batch(
    arms: tuple[str, ...],
    contrasts: np.ndarray,
    errors: np.ndarray,
    matrix: np.ndarray,
    center_visibility: float,
    models: str = "all",
) -> dict[str, dict[str, np.ndarray]]:
    """Per world and contraction share, the least chi-square over the world's parameter of a batch's raw selector
    contrasts and relative d2 splits (`contrasts` and `errors` hold the three contrasts, then the d2 split of each
    outer arm less the center arm's): "chi2", "parameter", "retention" (one value per share) and "predicted"
    (share, 5). A noise model and parameter whose retentions cannot reproduce the center visibility within
    VISIBILITY_TOLERANCE take an infinite chi-square.

    The split enters relative to the batch's center because the predecessor's centers read a d2 split of
    +0.0083 +- 0.0017 that no world of this decision gives; the coupler world's split is odd in the injected phase
    and survives the subtraction. The statistics of one batch share shots and a center; the sum treats them as
    independent, which the case states as a limit of the bound."""
    rows: dict[str, dict[str, np.ndarray]] = {}
    take = np.arange(len(noise_models(models)))
    for world, grid in WORLDS.items():
        model, kept, miss = seen_contrasts(world, arms, matrix, center_visibility, models)
        curve = np.where(miss <= VISIBILITY_TOLERANCE, (((model - contrasts) / errors) ** 2).sum(-1), np.inf)
        best = curve.argmin(1)
        rows[world] = {
            "chi2": curve[take, best],
            "parameter": grid[best],
            "retention": kept[take, best],
            "predicted": model[take, best],
        }
    return rows


# Series -----------------------------------------------------------------------------------------------------------


def scan_arms(kind: str, replicate: int) -> list[str]:
    """Arms of a data batch: even replicates in the forward order, odd replicates mirrored."""
    first, last = SCANS[kind]
    return [first, CENTER, last] if replicate % 2 == 0 else [last, CENTER, first]


def batch_order() -> list[tuple[str, int]]:
    """(kind, replicate) of the fourteen data batches: FIRST_ROUND with even replicates, then the same list backwards
    with the odd replicate that mirrors each."""
    seen: dict[str, int] = {}
    first = []
    for kind in FIRST_ROUND:
        first.append((kind, 2 * seen.get(kind, 0)))
        seen[kind] = seen.get(kind, 0) + 1
    return first + [(kind, replicate + 1) for kind, replicate in reversed(first)]


def batch_rows(series_name: str) -> list[dict[str, Any]]:
    """The batches of a series. Tuna-17: a readout batch, then each data batch of batch_order followed by a readout
    batch. QX: every arm, three to a batch."""
    rows: list[dict[str, Any]] = []

    def data(arm: str) -> dict[str, Any]:
        q4_steps, z12_steps, z8c_steps = ARMS[arm_of(arm)]
        return {
            "file": f"{arm}.cq",
            "kind": "data",
            "template": "b0",
            "arm": {
                "q4_steps": q4_steps,
                "z12_steps": z12_steps,
                "z8c_steps": z8c_steps,
                "padded": arm_of(arm) != PLAIN,
            },
        }

    def add(kind: str, replicate: int | None, circuits: list[dict[str, Any]]) -> None:
        rows.append({"batch": f"batch-{len(rows):02d}", "kind": kind, "replicate": replicate, "circuits": circuits})

    if series_name == QX_SERIES:
        for start in range(0, len(ARM_NAMES), QX_BATCH_CIRCUITS):
            add("control", None, [data(a) for a in ARM_NAMES[start : start + QX_BATCH_CIRCUITS]])
        return rows
    brackets = [{"file": "readout-0.cq", "kind": "readout"}, {"file": "readout-1.cq", "kind": "readout"}]
    add("readout", None, brackets)
    for position, (kind, replicate) in enumerate(batch_order()):
        add(kind, replicate, [data(arm) for arm in scan_arms(kind, replicate)])
        add("readout", None, brackets if position % 2 else list(reversed(brackets)))
    return rows


def row_shots(row: dict[str, Any]) -> int:
    return READOUT_SHOTS if row["kind"] == "readout" else SCAN_SHOTS


def arm_of(file: str) -> str:
    return file.removesuffix(".cq").removesuffix("-repeat")


def batch_values(batch: dict[str, Any]) -> int:
    """Fitted values of a deciding batch: three contrasts, and two relative d2 splits when d2's qubit passed its
    guard."""
    return 5 if batch.get("split_admitted", True) else 3


def freedom(world: str, values: list[int], flip_fitted: bool = True) -> int:
    """Degrees of freedom of a world over deciding batches that hold `values` fitted values each: one fitted parameter
    per batch for an error world and none for the exact world, one noise model for the series, and one readout flip
    for the series when the flip is fitted."""
    return sum(v - (0 if world == "exact" else 1) for v in values) - 1 - (1 if flip_fitted else 0)


def adequacy_limit(world: str, values: list[int], flip_fitted: bool = True) -> float:
    """Chi-square bound of a world: its upper ADEQUACY_ALPHA point on freedom(world, values, flip_fitted)."""
    return float(chi2_law.ppf(1 - ADEQUACY_ALPHA, freedom(world, values, flip_fitted)))


def preregistered() -> dict[str, str]:
    return {
        "estimates": "per data circuit, the raw selector contrast P(s=0 | coin read 1) - P(s=0 | coin read 0) with "
        "its binomial standard error, the d2 split and the visibility of the center arm of each batch",
        "guard": "a data batch is admitted when e01 and e10 of each qubit the contrast reads (d0, d1, the selector "
        f"and the coin) change by at most {GUARD_LIMIT} between the readout batch before it and the one after; its "
        "d2 splits enter the fit only when d2's qubit passes the same bound, otherwise the batch is fitted on its "
        "three contrasts; the decision needs at least one admitted batch of each deciding kind (z12-10, z12-30 and "
        "z8c-10), otherwise it reads unresolved_guard",
        "control": "the inverse-variance mean of the center arm's contrast over the admitted batches exceeds "
        f"{Z_RESOLVE} standard errors; otherwise the decision reads offset_absent (within) or offset_reversed (below)",
        "fit": "for each world (exact gates, a rotation about z before each pulse of q12, a conditional-phase error "
        "of the CZ gates of coupler 8-12, a rotation about z on q8 after each CZ of coupler 8-12) one parameter per "
        "admitted deciding batch is fitted to its three contrasts and to the d2 split of each outer arm less its "
        "center arm's, at the retention that reproduces the batch's center visibility through its own bracket "
        "assignment; a noise model whose center reaches no visibility within "
        f"{VISIBILITY_TOLERANCE:.4f} ({Z_RESOLVE:g} over the square root of the circuit's {SCAN_SHOTS:,} shots) of the "
        "batch's does not fit that batch; the chi-squares are summed at the one "
        "noise model and readout flip that make the sum least, among the contraction shares of the predecessor's "
        "grid and CZ amplitude and phase damping of 0.019 and 0.031 per CZ qubit at multiples 0 to 3 in steps of "
        "1/16, and among probabilities that the selector reads flipped when d0 reads 0, composed onto each batch's "
        f"assignment matrix, from 0 to {FLIP_GRID[-1]:g} in steps of {FLIP_GRID[1]:g}, one per series and world, a "
        "tie keeping the smaller",
        "adequacy": f"a world is adequate when its sum is at most the upper {ADEQUACY_ALPHA} point (the "
        f"{100 * (1 - ADEQUACY_ALPHA):.1f}th percentile) of chi-square with one degree of freedom per fitted value "
        "(5 per deciding batch, 3 when its d2 splits are left out), less one per fitted parameter, one for the "
        "noise model and one for the readout flip",
        "readout_flip": "reported beside the label: each world's fitted readout flip, and the worlds whose flip "
        f"lies at the grid's end, {FLIP_GRID[-1]:g}, where the excess of a larger flip is outside the fit",
        "labels": "exact_parabola: the exact world, at its fitted readout flip, is adequate, so the deciding arms "
        "need no phase on or around q12 at this offset, and a fitted flip above 0 names a selector misread "
        "conditioned on d0 as a candidate cause; a phase whose center offset lies near the control's threshold can "
        f"read it; {', '.join(ERROR_WORLDS[:-1])} or {ERROR_WORLDS[-1]}: that "
        "world is adequate, its "
        f"sum lies at least {SEPARATION:g} times the larger of 1 and its sum per degree of freedom below every other "
        "error world's, and each deciding kind, summed over its "
        f"admitted replicates, reads that world at or below the upper {ADEQUACY_ALPHA} point of chi-square on its "
        f"own degrees of freedom and at most {KIND_MARGIN} above every other error world; phase_mixed: the sums "
        "prefer one error world and a kind does not; phase_unresolved: an error world is adequate and the least "
        "is closer to another; none_adequate: no world is adequate. q12_phase names a single-qubit phase at q12's "
        "pulses: a rotation about z after each pulse gives the same laws as one before each pulse",
        "sign": "reported with a deciding label: the fitted parameter of each admitted deciding batch, and the "
        "injected phase of least contrast from a parabola through the pooled z12 arms and centers",
        "d2_split": "also reported beside the label: the d2 split of every arm of the deciding kinds pooled over the "
        "admitted replicates whose d2 qubit passed its guard, beside the values each world predicts",
        "z8c": "reported beside the label: a weighted parabola through the z8c arms and their centers against the "
        "injected q8 phase",
        "bridge": "reported outside the label: the padded center's contrast less the mean of the two plain arms in "
        "each admitted bridge batch, pooled, and whether it lies within "
        f"{Z_RESOLVE} standard errors of zero",
        "q4_line": "reported outside the label: a weighted straight line through the origin of the contrast of each "
        "q4 arm less its batch center against q4's injected angle (-10, -5, +5, +10 degrees), with its chi-square, "
        "slope and the angle at which the pooled center plus the line reads zero; when the bridge reads within its "
        "bound and the slope of the new +-10 degree arms lies within "
        f"{Z_RESOLVE} standard errors of the slope of the predecessor's admitted q4 +-10 degree points, the same "
        "line is also reported with those points added",
        "visibility": "reported outside the label: each arm's visibility over its batch center's, beside the "
        "exact circuit's ratio",
        "line_phase": "outside this analysis: the shot-order fold of "
        "docs/evidence/qi-null-rotation-scan-line-phase/line_phase_split.py is run on the retained jobs afterwards "
        "and decides nothing",
        "ledger": f"A5-186 changes only on {', '.join(ERROR_WORLDS[:-1])} or {ERROR_WORLDS[-1]}, to the statement "
        "of that label; every other label reports the numbers",
    }


def series(backend: dict[str, Any], series_name: str, nqubits: int, place: dict[int, int]) -> dict[str, str]:
    ref = rs.retained()
    region = ref["region"]
    register = [place[q] for q in region]
    files: dict[str, str] = {}
    common = {
        "backend": backend["identifier"],
        "backend_type_id": backend["id"],
        "nqubits": nqubits,
        "region": list(region),
        "placement": {str(q): place[q] for q in region},
        "register": register,
        "guard_qubits": [place[ref["roles"][k]] for k in rs.GUARD_ROLES],
        "d2_guard_qubit": place[ref["roles"]["d2"]],
        "templates": {
            "b0": {
                "block": "b0",
                "operand": list(oc.OPERAND),
                "basis": list(oc.BASIS_VECTORS),
                "coset": 0,
                "cz": ref["cz"],
                "roles": {k: place[q] for k, q in ref["roles"].items()},
                "ideal_c": ref["ideal_c"],
            }
        },
        "retained_b0": {"cases_sha256": oc.COIN_PINS["cases.json"], "circuit_sha256": oc.COIN_PINS["b0.cq"]},
        "preregistered": preregistered(),
    }
    batches = []
    for row in batch_rows(series_name):
        shots = QX_SHOTS if series_name == QX_SERIES else row_shots(row)
        circuits: list[dict[str, Any]] = []
        for spec in row["circuits"]:
            record = dict(spec)
            if spec["kind"] == "readout":
                text = cc.readout_text(nqubits, spec["file"] == "readout-1.cq", register)
            else:
                arm = arm_of(spec["file"])
                text = arm_text(arm, place, nqubits)
                record["ideal"] = [round(float(x), 12) for x in forward_law(arm)]
            record["sha256"] = hashlib.sha256(text.encode()).hexdigest()
            circuits.append(record)
            files[f"{row['batch']}/{spec['file']}"] = text
        manifest = {
            "schema": SCHEMA,
            **common,
            "shots": shots,
            "batch": row["batch"],
            "kind": row["kind"],
            "replicate": row["replicate"],
            "circuits": circuits,
        }
        files[f"{row['batch']}/cases.json"] = json.dumps(manifest, indent=1) + "\n"
        batches.append({"batch": row["batch"], "kind": row["kind"], "files": [c["file"] for c in circuits]})
    files["cases.json"] = (
        json.dumps({"schema": SERIES_SCHEMA, "backend": backend["identifier"], "batches": batches}, indent=1) + "\n"
    )
    return files


def build() -> dict[str, dict[str, str]]:
    tuna, qx = zd.catalogue_check()
    region = rs.retained()["region"]
    rs.replay_check()
    center_check()
    return {
        TUNA_SERIES: series(tuna, TUNA_SERIES, cc.NQUBITS, {q: q for q in region}),
        QX_SERIES: series(qx, QX_SERIES, QX_QUBITS, {q: i for i, q in enumerate(region)}),
    }


def design() -> dict[str, Any]:
    """Jobs, shots, standard errors and seconds of the Tuna-17 series."""
    timing = oc.coin_timing()
    rows = batch_rows(TUNA_SERIES)
    jobs = sum(len(r["circuits"]) for r in rows)
    shots_total = sum(row_shots(r) * len(r["circuits"]) for r in rows)
    return {
        "contrast_se": round(1.0 / math.sqrt(SCAN_SHOTS), 6),
        "jobs": jobs,
        "batches": len(rows),
        "data_batches": sum(1 for r in rows if r["kind"] != "readout"),
        "shots_total": shots_total,
        "execution_seconds_range": [
            round(jobs * 2.6 + shots_total * 0.53e-3, 1),
            round(jobs * 2.6 + shots_total * timing["seconds_per_shot_max"], 1),
        ],
        "longest_job_seconds": round(2.6 + SCAN_SHOTS * timing["seconds_per_shot_max"], 1),
        "job_seconds_limit": 300,
        "pause_seconds_per_batch": PAUSE_CEILING,
        "pause_seconds_total": PAUSE_CEILING * (len(rows) - 1),
    }


# Decision ---------------------------------------------------------------------------------------------------------


def pooled(pairs: list[tuple[float, float]]) -> tuple[float, float]:
    value, error = oc.pooled(pairs)
    return float(value), float(error)


def relative_splits(batch: dict[str, Any]) -> tuple[list[float], list[float]]:
    """The d2 split of each outer arm of a batch less its center arm's, and the standard errors; a batch whose d2
    qubit failed its guard carries infinite errors, so its splits add nothing to a chi-square."""
    at = batch["arms"].index(CENTER)
    outer = [n for n in range(len(batch["arms"])) if n != at]
    values = [batch["splits"][n] - batch["splits"][at] for n in outer]
    if not batch.get("split_admitted", True):
        return values, [math.inf] * len(outer)
    errors = [math.hypot(batch["split_errors"][n], batch["split_errors"][at]) for n in outer]
    return values, errors


def screen(batches: list[dict[str, Any]]) -> tuple[str | None, list[dict[str, Any]], dict[str, Any]]:
    """The guard and center tests of decide(): a label that ends the decision before any fit, or None, then the
    admitted deciding batches and the numbers so far."""
    admitted = [b for b in batches if b["admitted"]]
    numbers: dict[str, Any] = {"admitted_batches": [b["name"] for b in admitted]}
    z12 = [b for b in admitted if b["kind"] in DECIDING_KINDS]
    if {b["kind"] for b in z12} != set(DECIDING_KINDS):
        return "unresolved_guard", z12, numbers
    centers = [(b["contrasts"][b["arms"].index(CENTER)], b["errors"][b["arms"].index(CENTER)]) for b in admitted]
    center = pooled(centers)
    numbers["center_contrast"] = list(center)
    if center[0] <= Z_RESOLVE * center[1]:
        return ("offset_reversed" if center[0] < -Z_RESOLVE * center[1] else "offset_absent"), z12, numbers
    return None, z12, numbers


def flipped(matrix: np.ndarray, flip: float) -> np.ndarray:
    """An assignment matrix with the selector read flipped at probability `flip` when d0 reads 0."""
    return matrix if flip == 0 else matrix @ oc.selector_flip(FLIP_QUBIT, 0, float(flip))


# Per world, the fit at the series' least sum over readout flip and noise model: "total", "flip", "model" (index into
# noise_models), and per deciding batch "chi2", "parameter" and "predicted".
Fitted = dict[str, dict[str, Any]]


def absorb(best: Fitted, flip: float, z12: list[dict[str, Any]], matrix_of: Any, models: str) -> None:
    """Fit every deciding batch at readout flip `flip` and keep, per world, the noise model of least sum when it lies
    below the sum `best` holds; flips are offered in increasing order, so a tie keeps the smaller."""
    fits = [
        fit_batch(
            tuple(b["arms"]),
            np.array([*b["contrasts"], *relative_splits(b)[0]]),
            np.array([*b["errors"], *relative_splits(b)[1]]),
            flipped(matrix_of(b), flip),
            b["center_visibility"],
            models,
        )
        for b in z12
    ]
    for w in WORLDS:
        chi = np.stack([f[w]["chi2"] for f in fits])
        total = chi.sum(0)
        j = int(total.argmin())
        if w not in best or total[j] < best[w]["total"]:
            best[w] = {
                "total": float(total[j]),
                "flip": flip,
                "model": j,
                "chi2": chi[:, j].copy(),
                "parameter": np.array([f[w]["parameter"][j] for f in fits]),
                "predicted": np.stack([f[w]["predicted"][j] for f in fits]),
            }


def clear_caches() -> None:
    SEEN_CACHE.clear()
    RETENTION_CACHE.clear()


def fit_flips(z12: list[dict[str, Any]], matrix_of: Any, models: str, flips: tuple[float, ...]) -> Fitted:
    """The fit of every world over `flips`; the caches are cleared after each flip, so one decision holds one flip's
    tables at a time."""
    best: Fitted = {}
    for flip in flips:
        absorb(best, flip, z12, matrix_of, models)
        clear_caches()
    return best


# Why a statistic reads null: every noise model, parameter and readout flip of a world leaves a batch's center
# visibility further from the world's reachable range than VISIBILITY_TOLERANCE, which fit_batch() scores as an
# infinite chi-square. Comparisons inside decide() keep the infinity; JSON has no infinity, so the numbers it returns
# hold null there and name the worlds.
UNREACHABLE_REASON = (
    "no noise model, parameter and readout flip of the listed worlds reproduces a deciding batch's center visibility "
    "within VISIBILITY_TOLERANCE, so their chi-square statistics are infinite; null marks an infinite statistic"
)


def finite_or_none(value: Any) -> Any:
    """`value` with each non-finite float replaced by None, through nested dicts, lists and tuples."""
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {k: finite_or_none(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [finite_or_none(v) for v in value]
    return value


def reportable(numbers: dict[str, Any], best: dict[str, float]) -> dict[str, Any]:
    """The numbers of decide() as JSON: unchanged while every world's least sum is finite, otherwise with null for each
    infinite statistic and an "unavailable" field naming the worlds and UNREACHABLE_REASON."""
    unreachable = sorted(w for w in WORLDS if not math.isfinite(best[w]))
    if not unreachable:
        return numbers
    return {**finite_or_none(numbers), "unavailable": {"worlds": unreachable, "reason": UNREACHABLE_REASON}}


def decide(
    batches: list[dict[str, Any]],
    matrix_of: Any,
    models: str = "all",
    margin: float | None = None,
    separation: float | None = None,
    flips: tuple[float, ...] = FLIP_GRID,
    fitted: Fitted | None = None,
) -> dict[str, Any]:
    """Label and numbers from data batches: each holds "name", "kind", "arms", "contrasts", "errors", "splits",
    "split_errors", "center_visibility", "admitted" and, optionally, "split_admitted" (default true); `matrix_of(batch)`
    is its assignment matrix. The readout flip is fitted over `flips` (a single value fixes it and frees no degree
    of freedom); `fitted` supplies a fit absorb() already made over `flips`."""
    label, z12, numbers = screen(batches)
    if label is not None:
        return {"label": label, "numbers": numbers}
    fit = fitted if fitted is not None else fit_flips(z12, matrix_of, models, flips)
    flip_fitted = len(flips) > 1
    values = [batch_values(b) for b in z12]
    best = {w: fit[w]["total"] for w in WORLDS}
    limit = {w: adequacy_limit(w, values, flip_fitted) for w in WORLDS}
    adequate = {w: best[w] <= limit[w] for w in WORLDS}
    names = [b["name"] for b in z12]
    numbers.update(
        chi2={w: round(best[w], 3) for w in WORLDS},
        adequacy_limit={w: round(limit[w], 3) for w in WORLDS},
        noise_model={w: noise_models(models)[fit[w]["model"]] for w in WORLDS},
        readout_flip={w: fit[w]["flip"] for w in WORLDS},
        flip_at_grid_end=sorted(w for w in WORLDS if flip_fitted and fit[w]["flip"] == flips[-1]),
        parameters={
            w: dict(zip(names, (float(x) for x in fit[w]["parameter"]), strict=True)) for w in WORLDS if w != "exact"
        },
        predicted={
            w: {n: [float(x) for x in row] for n, row in zip(names, fit[w]["predicted"], strict=True)} for w in WORLDS
        },
    )
    per_batch = {w: dict(zip(names, (float(x) for x in fit[w]["chi2"]), strict=True)) for w in WORLDS if w != "exact"}
    # Each deciding kind, summed over its admitted replicates: the series' world must fit it and the other error
    # world may undercut it by at most KIND_MARGIN.
    kind_chi2 = {
        w: {k: sum(per_batch[w][b["name"]] for b in z12 if b["kind"] == k) for k in DECIDING_KINDS} for w in per_batch
    }
    bound = {
        k: float(chi2_law.ppf(1 - ADEQUACY_ALPHA, sum(batch_values(b) - 1 for b in z12 if b["kind"] == k)))
        for k in DECIDING_KINDS
    }
    numbers.update(
        batch_chi2=per_batch,
        kind_chi2={w: {k: round(v, 3) for k, v in rows.items()} for w, rows in kind_chi2.items()},
        kind_limit={k: round(v, 3) for k, v in bound.items()},
        split_admitted=[b["name"] for b in z12 if b.get("split_admitted", True)],
    )

    def homogeneous(world: str) -> bool:
        slack = KIND_MARGIN if margin is None else margin
        return all(
            v <= bound[k] and all(v <= kind_chi2[other][k] + slack for other in ERROR_WORLDS if other != world)
            for k, v in kind_chi2[world].items()
        )

    # Every error world holds one parameter per batch and so the same bound, so the least sum is the only one that
    # can be adequate and separated from every other.
    lead = min(ERROR_WORLDS, key=lambda w: best[w])
    scale = max(1.0, best[lead] / freedom(lead, values, flip_fitted))
    needed = (SEPARATION if separation is None else separation) * scale
    numbers["separation_needed"] = round(needed, 3)
    if adequate["exact"]:
        label = "exact_parabola"
    elif adequate[lead] and all(best[lead] <= best[w] - needed for w in ERROR_WORLDS if w != lead):
        label = lead if homogeneous(lead) else "phase_mixed"
    elif any(adequate[w] for w in ERROR_WORLDS):
        label = "phase_unresolved"
    else:
        label = "none_adequate"
    return {"label": label, "numbers": reportable(numbers, best)}


def parabola_minimum(points: list[tuple[float, float, float]]) -> dict[str, float] | None:
    """Weighted parabola through (phi in degrees, contrast, error); its least point when it opens upward."""
    x = np.array([p[0] for p in points])
    y = np.array([p[1] for p in points])
    w = 1.0 / np.array([p[2] for p in points]) ** 2
    design_matrix = np.stack([np.ones_like(x), x, x * x], axis=1)
    normal = design_matrix.T @ (w[:, None] * design_matrix)
    coefficients = np.linalg.solve(normal, design_matrix.T @ (w * y))
    covariance = np.linalg.inv(normal)
    c, b, a = (float(v) for v in coefficients)
    if a <= 0:
        return None
    at = -b / (2 * a)
    gradient = np.array([0.0, -1 / (2 * a), b / (2 * a * a)])
    residual = y - design_matrix @ coefficients
    return {
        "phi_degrees": at,
        "phi_degrees_se": float(math.sqrt(gradient @ covariance @ gradient)),
        "least_contrast": c - b * b / (4 * a),
        "chi2": float((w * residual * residual).sum()),
        "freedom": len(points) - 3,
    }


def line_fit(points: list[tuple[float, float, float]], center: float) -> dict[str, float]:
    """Weighted line through the origin of (q4 degrees, contrast less its batch center, error)."""
    x = np.array([p[0] for p in points])
    y = np.array([p[1] for p in points])
    w = 1.0 / np.array([p[2] for p in points]) ** 2
    slope = float((w * x * y).sum() / (w * x * x).sum())
    error = float(1.0 / math.sqrt((w * x * x).sum()))
    return {
        "slope_per_degree": slope,
        "slope_se": error,
        "chi2": float((w * (y - slope * x) ** 2).sum()),
        "freedom": len(points) - 1,
        "zero_degrees": float(-center / slope) if slope else float("nan"),
    }


# Predictions ------------------------------------------------------------------------------------------------------


@cache
def predecessor_matrix() -> np.ndarray:
    """Assignment matrix at the mean bracket rates of the predecessor's ten data batches."""
    analysis = json.loads((ROOT / PREDECESSOR_ANALYSIS).read_text(encoding="utf-8"))
    guards = [r["guard"] for r in analysis["batch_rows"].values()]
    ref = rs.retained()

    def rate(q: int, i: int) -> float:
        return float(np.mean([(g["before"][str(q)][i] + g["after"][str(q)][i]) / 2 for g in guards]))

    mean: dict[int, tuple[float, float]] = {int(q): (rate(q, 0), rate(q, 1)) for q in ref["region"]}
    return np.asarray(cc.readout_matrix(mean, ref["roles"]))


TRUTHS: dict[str, tuple[str, float, float, Noise, str | None]] = {
    "exact gates": ("exact", 0.0, 0.0, NO_NOISE, "offset_absent"),
    "q12 phase -0.18 rad": ("q12_phase", -0.18, 0.0, NO_NOISE, "q12_phase"),
    "q12 phase +0.18 rad": ("q12_phase", 0.18, 0.0, NO_NOISE, "q12_phase"),
    "q12 phase -0.15 rad": ("q12_phase", -0.15, 0.0, NO_NOISE, "q12_phase"),
    "coupler 8-12 phase -0.25 rad": ("coupler_phase", -0.25, 0.0, NO_NOISE, "coupler_phase"),
    "coupler 8-12 phase +0.25 rad": ("coupler_phase", 0.25, 0.0, NO_NOISE, "coupler_phase"),
    "exact gates, selector flip 0.0166 when q12 reads 0": ("exact", 0.0, 0.0166, NO_NOISE, "exact_parabola"),
    "exact gates, selector flip 0.036 when q12 reads 0": ("exact", 0.0, 0.036, NO_NOISE, "exact_parabola"),
    "q12 phase -0.18 rad, selector flip 0.036": ("q12_phase", -0.18, 0.036, NO_NOISE, "q12_phase"),
    "coupler 8-12 phase -0.25 rad, selector flip 0.036": ("coupler_phase", -0.25, 0.036, NO_NOISE, "coupler_phase"),
    "q8 phase at coupler 8-12 -0.25 rad, selector flip 0.042": (Q8_PHASE, -0.25, 0.042, NO_NOISE, None),
    "q8 phase at coupler 8-12 -0.25 rad": (Q8_PHASE, -0.25, 0.0, NO_NOISE, Q8_PHASE),
    "q8 phase at coupler 8-12 -0.17 rad": (Q8_PHASE, -0.17, 0.0, NO_NOISE, None),
    "q8 phase at coupler 8-12 +0.10 rad": (Q8_PHASE, 0.10, 0.0, NO_NOISE, None),
    "q12 phase -0.15 rad with CZ damping": ("q12_phase", -0.15, 0.0, CZ_DAMPING, "q12_phase"),
    "coupler 8-12 phase -0.25 rad with CZ damping": ("coupler_phase", -0.25, 0.0, CZ_DAMPING, "coupler_phase"),
    "exact gates with CZ damping": ("exact", 0.0, 0.0, CZ_DAMPING, "offset_absent"),
    "q12 phase -0.15 rad with CZ damping x1.25": ("q12_phase", -0.15, 0.0, scaled(CZ_DAMPING, 1.25), None),
    "coupler 8-12 phase -0.25 rad with CZ damping x1.25": ("coupler_phase", -0.25, 0.0, scaled(CZ_DAMPING, 1.25), None),
    "q12 phase -0.15 rad with CZ damping x3": ("q12_phase", -0.15, 0.0, scaled(CZ_DAMPING, 3.0), None),
    "exact gates, selector flip 0.0166, CZ phase damping 0.10": ("exact", 0.0, 0.0166, (0.0, 0.0, 0.0, 0.10), None),
    "exact gates, selector flip 0.025, CZ phase damping 0.13": ("exact", 0.0, 0.025, (0.0, 0.0, 0.0, 0.13), None),
    "q8 phase at coupler 8-12 -0.25 rad, pulse phase damping 0.10": (Q8_PHASE, -0.25, 0.0, (0.0, 0.10, 0.0, 0.0), None),
    "q8 phase at coupler 8-12 -0.25 rad, CZ phase damping 0.12": (Q8_PHASE, -0.25, 0.0, (0.0, 0.0, 0.0, 0.12), None),
    "exact gates, selector flip 0.036, CZ phase damping 0.16": ("exact", 0.0, 0.036, (0.0, 0.0, 0.0, 0.16), None),
    "exact gates, selector flip 0.025, pulse phase damping 0.10": ("exact", 0.0, 0.025, (0.0, 0.10, 0.0, 0.0), None),
}
# Truths the prediction record states: world, parameter in radians, probability of a selector flip conditioned on
# d0 reading 0 (the predecessor's readout world, which the fit's FLIP_GRID absorbs), gate noise, and the label the
# self-test requires at expected values (None: reported, not required; the truth lies outside the fit's worlds or
# near the separation, where phase_unresolved and the truth's own label are both correct readings).


def truth_row(
    world: str, theta: float, matrix: np.ndarray, flip: float = 0.0, mix: float = 0.0, noise: Noise = NO_NOISE
) -> dict[str, dict[str, float]]:
    """Contrast and d2 split of every arm under a truth at the retention where its center reads the design
    visibility, and the center's visibility at that retention: a truth whose noise keeps the center below the design
    visibility at every retention is taken at the largest it reaches; `flip` is the probability that the selector
    read flips when d0 reads 0."""
    laws = np.stack([forward_law(arm, world, theta, noise) for arm in ARM_NAMES])[None]
    center = laws[:, [ARM_NAMES.index(CENTER)]]
    seen_matrix = matrix @ oc.selector_flip(KEYS.index("d0"), 0, flip)
    seen = np.array(
        [
            float(rs.visibility(rs.read(rs.contract(center, float(r), mix), seen_matrix))[0, 0])
            for r in rs.RETENTION_GRID
        ]
    )
    order = np.argsort(seen)
    if DESIGN_VISIBILITY <= seen.max():
        retention = float(np.interp(DESIGN_VISIBILITY, seen[order], rs.RETENTION_GRID[order]))
    else:
        retention = float(rs.RETENTION_GRID[seen.argmax()])
    read = rs.read(rs.contract(laws, retention, mix), seen_matrix)[0]
    contrast = rs.selector_contrast(read)
    split = rs.d2_split(read)[0]
    row = {
        arm: {"contrast": round(float(contrast[i]), 5), "d2_split": round(float(split[i]), 5)}
        for i, arm in enumerate(ARM_NAMES)
    }
    row[CENTER]["visibility"] = round(float(rs.visibility(read[[ARM_NAMES.index(CENTER)]])[0]), 5)
    return row


def planted_batches(row: dict[str, dict[str, float]]) -> list[dict[str, Any]]:
    """The fourteen data batches at a truth's expected contrasts and d2 splits, its center visibility and the design
    standard errors."""
    error = 1.0 / math.sqrt(SCAN_SHOTS)
    out = []
    for n, (kind, replicate) in enumerate(batch_order()):
        arms = scan_arms(kind, replicate)
        out.append(
            {
                "name": f"planted-{n}",
                "kind": kind,
                "arms": arms,
                "contrasts": [row[arm_of(a)]["contrast"] for a in arms],
                "errors": [error] * 3,
                "splits": [row[arm_of(a)]["d2_split"] for a in arms],
                "split_errors": [2 * error] * 3,
                "center_visibility": row[CENTER]["visibility"],
                "admitted": True,
            }
        )
    return out


def truth_batches(name: str) -> list[dict[str, Any]]:
    world, theta, flip, noise, _ = TRUTHS[name]
    return planted_batches(truth_row(world, theta, predecessor_matrix(), flip, noise=noise))


# Scenario -> (truth of the z12 batches, truth of the z8c batches); a mixed scenario draws the two from different
# mechanisms, every other scenario is one truth.
MIXED: dict[str, tuple[str, str]] = {
    "z12 from q12 phase -0.18, z8c from coupler phase -0.25": ("q12 phase -0.18 rad", "coupler 8-12 phase -0.25 rad"),
    "z12 from coupler phase -0.25, z8c from q12 phase -0.18": ("coupler 8-12 phase -0.25 rad", "q12 phase -0.18 rad"),
}


def scenario_batches(name: str) -> list[dict[str, Any]]:
    if name not in MIXED:
        return truth_batches(name)
    z12, z8c = (truth_batches(t) for t in MIXED[name])
    return [c if q["kind"] == "z8c-10" else q for q, c in zip(z12, z8c, strict=True)]


OC_DRAW = "docs/evidence/anu_qrng/draw-2026-11-15T084216Z.json"
# Value 0 of OC_DRAW calibrated KIND_MARGIN and value 1 recorded the characteristics of the two-error-world
# decision; values 2 through 7 seeded a reviewer's replication; value 8 recorded the three-error-world decision with
# an unscaled separation of 25, under which no-phase nulls outside the noise models read q12_phase in up to 48 of
# 500 series (a record the later writes replaced). Value 9 calibrated SEPARATION, value 10 recorded it at 30 (one
# null read q12_phase once in 500), value 11 recorded it at 40 with the readout flip fixed at 0, and value 12
# records the decision this module holds, with the readout flip fitted over FLIP_GRID.
OC_SEED_INDEX = 12
OC_SERIES = 500
# Scenarios of exact gates draw NULL_SERIES series, so that a count of 0 deciding labels bounds the rate at 0.06%
# (one-sided 95% Clopper-Pearson) where 500 series bound it at 0.60%; OC_CHUNK series make one work item.
NULL_SERIES = 5000
OC_CHUNK = 250
# A static d2 split added to every circuit of a simulated series, the size the predecessor's centers read.
OC_SPLIT_OFFSET = 0.0083


def oc_seed(index: int = OC_SEED_INDEX) -> int:
    from qrng_seeds import read_record

    return int(read_record(OC_DRAW)["values"][index])


def scenario_series(name: str) -> int:
    return NULL_SERIES if name in TRUTHS and TRUTHS[name][0] == "exact" else OC_SERIES


def wrong_labels(name: str) -> tuple[str, ...]:
    """Labels that misread a scenario: every error world for exact gates; for a single phase every other error world
    and exact_parabola, which states that no phase is needed; for a mixed scenario every error world and
    exact_parabola."""
    world = TRUTHS[name][0] if name in TRUTHS else None
    others = tuple(w for w in ERROR_WORLDS if w != world)
    return others if world == "exact" else (*others, "exact_parabola")


def upper_bound(count: int, series: int, confidence: float = 0.95) -> float:
    """One-sided Clopper-Pearson upper bound on a rate seen `count` times in `series` trials."""
    return 1.0 if count >= series else float(beta_law.ppf(confidence, count + 1, series - count))


def oc_worker(item: tuple[int, str, int, int, int, float, float, tuple[float, ...]]) -> dict[str, int]:
    """Label counts of series `start` to `stop` of one scenario: Gaussian contrasts and d2 splits at the design
    standard errors around the scenario's expected values, every batch admitted, a static d2 split of
    OC_SPLIT_OFFSET on every circuit. The generator is seeded with (seed, scenario position) and draws the
    scenario's whole series, so each series is fixed whatever the chunking and worker count. Every series is fitted
    at one readout flip before the next, so the caches hold one flip's tables at a time."""
    seed, name, position, start, stop, margin, separation, flips = item
    rng = np.random.default_rng([seed, position])
    matrix = predecessor_matrix()
    error = 1.0 / math.sqrt(SCAN_SHOTS)
    base = scenario_batches(name)
    noise = rng.standard_normal((scenario_series(name), len(base), 6))[start:stop]
    drawn = [
        [
            {
                **b,
                "contrasts": [v + error * noise[i, n, j] for j, v in enumerate(b["contrasts"])],
                "splits": [v + OC_SPLIT_OFFSET + 2 * error * noise[i, n, 3 + j] for j, v in enumerate(b["splits"])],
            }
            for n, b in enumerate(base)
        ]
        for i in range(stop - start)
    ]
    screened = [screen(s) for s in drawn]
    fits: list[Fitted] = [{} for _ in drawn]
    for flip in flips:
        for (label, z12, _), fit in zip(screened, fits, strict=True):
            if label is None:
                absorb(fit, flip, z12, lambda b: matrix, "all")
        clear_caches()
    tally: dict[str, int] = {}
    for s, fit in zip(drawn, fits, strict=True):
        label = decide(s, lambda b: matrix, margin=margin, separation=separation, flips=flips, fitted=fit)["label"]
        tally[label] = tally.get(label, 0) + 1
    return tally


def operating_characteristics(
    index: int = OC_SEED_INDEX,
    margin: float | None = None,
    separation: float | None = None,
    flips: tuple[float, ...] = FLIP_GRID,
) -> dict[str, Any]:
    """Label counts per scenario (every truth of TRUTHS and every mixed scenario), seeded from value `index` of
    OC_DRAW and mapped over the process pool in chunks of OC_CHUNK series, with the one-sided 95% Clopper-Pearson
    upper bound on the rate of a label of wrong_labels(); `margin` and `separation` replace
    KIND_MARGIN and SEPARATION for a calibration and `flips` replaces FLIP_GRID."""
    names = [*TRUTHS, *MIXED]
    seed = oc_seed(index)
    slack = KIND_MARGIN if margin is None else margin
    gap = SEPARATION if separation is None else separation
    build_tables()
    items = [
        (seed, name, n, start, min(start + OC_CHUNK, scenario_series(name)), slack, gap, flips)
        for n, name in enumerate(names)
        for start in range(0, scenario_series(name), OC_CHUNK)
    ]
    counts: dict[str, dict[str, int]] = {name: {} for name in names}
    for item, tally in zip(items, ordered_map(oc_worker, items, min_items=2), strict=True):
        for label, k in tally.items():
            counts[item[1]][label] = counts[item[1]].get(label, 0) + k
    wrong = {name: sum(counts[name].get(w, 0) for w in wrong_labels(name)) for name in names}
    return {
        "series_per_scenario": {name: scenario_series(name) for name in names},
        "qrng_draw": OC_DRAW,
        "seed_index": index,
        "kind_margin": slack,
        "separation": gap,
        "readout_flip_grid": list(flips) if len(flips) < 3 else [flips[0], round(flips[1] - flips[0], 6), flips[-1]],
        "static_d2_split": OC_SPLIT_OFFSET,
        "label_counts": {name: dict(sorted(counts[name].items())) for name in names},
        "wrong_deciding": {
            name: {"count": wrong[name], "upper_95": round(upper_bound(wrong[name], scenario_series(name)), 6)}
            for name in names
        },
    }


def expected_decision(name: str) -> dict[str, Any]:
    """A truth's expected contrasts and the decision on its planted batches."""
    world, theta, flip, noise, _ = TRUTHS[name]
    matrix = predecessor_matrix()
    row = truth_row(world, theta, matrix, flip, noise=noise)
    decision = decide(planted_batches(row), lambda b: matrix)
    return {
        "arms": row,
        "label_at_expected_values": decision["label"],
        "chi2_at_expected_values": decision["numbers"].get("chi2"),
        "readout_flip_at_expected_values": decision["numbers"].get("readout_flip"),
    }


def predictions() -> dict[str, Any]:
    build_tables()
    truths = dict(zip(TRUTHS, ordered_map(expected_decision, list(TRUTHS), min_items=2), strict=True))
    return {
        "schema": "qi-pathion-null-phase-scan-prediction-v3",
        "design": design(),
        "design_visibility": DESIGN_VISIBILITY,
        "readout": f"mean bracket rates of {PREDECESSOR_ANALYSIS}",
        "preregistered": preregistered(),
        "truths": truths,
        "operating_characteristics": operating_characteristics(),
        "limits": "contraction share 0 and the design visibility for every truth, or the largest visibility its "
        "noise reaches; Gaussian sampling noise with every batch admitted; the gate noise simulated is CZ damping at "
        "one ratio (multiples 1, 1.25 and 3) and the six phase-damping truths outside the fit's noise models; one "
        "readout flip per series: a flip that drifts during the series is outside the fit (exploratory draws: no "
        "deciding label on a drifting null, a true phase beside a flip drifting from 0 to 0.036 read its label in "
        "about half its series and none_adequate or phase_mixed otherwise); a flip above the grid's 0.06 is outside "
        "the fit",
    }


# CASE.md tables rendered from prediction.json between these markers; write() fills them and check() compares them,
# so the hand-written case cannot carry a stale number.
TABLE_BEGIN = "<!-- generated from prediction.json by scripts/qi_pathion_null_phase_scan_cases.py: {} -->"
TABLE_END = "<!-- end of generated table -->"
TABLE_ARMS = (CENTER, *(a for a in ARM_NAMES if a not in (PLAIN, CENTER)))


def signed(value: float) -> str:
    return "0" if round(value, 4) == 0 else f"{value:+.4f}"


def case_tables(record: dict[str, Any]) -> dict[str, str]:
    """The expected-contrast table of every truth and the label-count table of every scenario."""
    heads = ["center"]
    heads += [arm.removeprefix(f"{CENTER}-").replace("-m", " -").replace("-p", " +") for arm in TABLE_ARMS[1:]]
    truths = ["| truth | " + " | ".join(heads) + " | label | fitted flip |", "|---" * (len(heads) + 3) + "|"]
    for name in sorted(record["truths"]):
        row = record["truths"][name]
        cells = " | ".join(signed(row["arms"][arm]["contrast"]) for arm in TABLE_ARMS)
        label = row["label_at_expected_values"]
        flips = row["readout_flip_at_expected_values"]
        world = label if flips and label in flips else ("exact" if label == "exact_parabola" else None)
        flip = f"{flips[world]:g}" if flips and world else "-"
        truths.append(f"| {name} | {cells} | `{label}` | {flip} |")
    oc_record = record["operating_characteristics"]
    counts = oc_record["label_counts"]
    scenarios = [
        "| scenario | series | label counts | misreading labels (one-sided 95% upper bound) |",
        "|---|---|---|---|",
    ]
    for name in sorted(counts):
        tallies = ", ".join(f"`{k}` {v}" for k, v in sorted(counts[name].items()))
        wrong = oc_record["wrong_deciding"][name]
        scenarios.append(
            f"| {name} | {oc_record['series_per_scenario'][name]} | {tallies} | "
            f"{wrong['count']} (< {100 * wrong['upper_95']:.2f}%) |"
        )
    return {"truths": "\n".join(truths), "operating_characteristics": "\n".join(scenarios)}


def render_case(text: str, record: dict[str, Any]) -> str:
    """CASE.md text with each generated table replaced by its rendering from `record`."""
    for key, table in case_tables(record).items():
        begin = TABLE_BEGIN.format(key)
        if text.count(begin) != 1:
            raise ValueError(f"CASE.md holds {text.count(begin)} markers for the {key} table, not 1")
        start = text.index(begin) + len(begin)
        end = text.index(TABLE_END, start)
        text = f"{text[:start]}\n{table}\n{text[end:]}"
    return text


def write(directory: Path) -> None:
    for name, files in build().items():
        for rel, text in files.items():
            path = directory / name / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    record = predictions()
    (directory / TUNA_SERIES / "prediction.json").write_text(
        json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8"
    )
    case = directory / TUNA_SERIES / "CASE.md"
    case.write_text(render_case(case.read_text(encoding="utf-8"), record), encoding="utf-8")
    print(f"wrote {TUNA_SERIES} and {QX_SERIES} under {directory}")


def check(directory: Path) -> None:
    """The case directories hold exactly the built files; CASE.md, the hand-written case, is the one extra file, and
    its generated tables match the prediction record."""
    built = build()
    record = predictions()
    built[TUNA_SERIES]["prediction.json"] = json.dumps(record, indent=1, sort_keys=True) + "\n"
    for name, files in built.items():
        root = directory / name
        present = {
            p.relative_to(root).as_posix()
            for p in root.rglob("*")
            if p.is_file() and not p.name.startswith(".") and p.name != "CASE.md"
        }
        if present != set(files):
            raise ValueError(f"{root}: files differ from the build: {sorted(present ^ set(files))}")
        for rel, text in files.items():
            if (root / rel).read_text(encoding="utf-8") != text:
                raise ValueError(f"{root}/{rel} differs from the build")
    case = directory / TUNA_SERIES / "CASE.md"
    if not case.is_file():
        raise ValueError(f"{directory / TUNA_SERIES}/CASE.md is missing")
    text = case.read_text(encoding="utf-8")
    if render_case(text, record) != text:
        raise ValueError(f"{case}: a generated table differs from prediction.json")
    print(f"{directory}: {TUNA_SERIES} and {QX_SERIES} match the build")


# Analysis ---------------------------------------------------------------------------------------------------------


def series_of(run_dir: Path) -> str:
    stem = run_dir.name.rpartition("-batch-")[0]
    for name in (TUNA_SERIES, QX_SERIES):
        if stem.endswith(f"-{name}"):
            return name
    raise SystemExit(f"{run_dir.name} is not a run directory of {TUNA_SERIES} or {QX_SERIES}")


def evaluate(shots: dict[str, list[str]], manifest: dict[str, Any]) -> dict[str, Any]:
    """Preregistered decision and reported numbers from shot lists keyed "batch/file"."""
    roles = {k: int(v) for k, v in manifest["templates"]["b0"]["roles"].items()}
    register = [int(q) for q in manifest["register"]]
    guard = [int(q) for q in manifest["guard_qubits"]]
    d2_qubit = int(manifest["d2_guard_qubit"])
    plan = {row["batch"]: row for row in batch_rows(TUNA_SERIES)}
    names = sorted(plan)
    brackets = {b: cc.batch_assignment(shots, b, register) for b in names if plan[b]["kind"] == "readout"}
    if any(v is None for v in brackets.values()):
        raise ValueError("a readout batch lacks one of its two circuits")
    batches: list[dict[str, Any]] = []
    matrices: dict[str, np.ndarray] = {}
    rows: dict[str, Any] = {}
    for n, batch in enumerate(names):
        row = plan[batch]
        if row["kind"] == "readout":
            continue
        before, after = brackets[names[n - 1]], brackets[names[n + 1]]
        if before is None or after is None:
            raise ValueError(f"{batch} lacks a bracket")
        change = {
            str(q): {kind: abs(after[q][i] - before[q][i]) for i, kind in enumerate(("e01", "e10"))} for q in register
        }
        admitted = all(v <= GUARD_LIMIT for q in guard for v in change[str(q)].values())
        split_admitted = admitted and all(v <= GUARD_LIMIT for v in change[str(d2_qubit)].values())
        mean = {q: ((before[q][0] + after[q][0]) / 2, (before[q][1] + after[q][1]) / 2) for q in register}
        matrices[batch] = cc.readout_matrix(mean, roles)
        stats = [rs.circuit_statistics(shots[f"{batch}/{c['file']}"], roles) for c in row["circuits"]]
        arms = [arm_of(c["file"]) for c in row["circuits"]]
        rows[batch] = {
            "kind": row["kind"],
            "replicate": row["replicate"],
            "arms": arms,
            "statistics": stats,
            "guard": {
                "change": change,
                "admitted": admitted,
                "split_admitted": split_admitted,
                "before": {str(q): before[q] for q in register},
                "after": {str(q): after[q] for q in register},
            },
        }
        batches.append(
            {
                "name": batch,
                "kind": row["kind"],
                "arms": arms,
                "contrasts": [s["contrast"] for s in stats],
                "errors": [s["se"] for s in stats],
                "splits": [s["d2_split"] for s in stats],
                "split_errors": [s["d2_split_se"] for s in stats],
                "center_visibility": stats[arms.index(CENTER)]["visibility"],
                "admitted": admitted,
                "split_admitted": split_admitted,
            }
        )
    decision = decide(batches, lambda b: matrices[b["name"]])
    admitted_rows = [r for r in rows.values() if r["guard"]["admitted"]]
    split_rows = [id(r) for r in admitted_rows if r["guard"]["split_admitted"]]
    reported: dict[str, Any] = {}
    z_points: list[tuple[float, float, float]] = []
    z8_points: list[tuple[float, float, float]] = []
    q4_points: list[tuple[float, float, float]] = []
    split: dict[str, list[tuple[float, float]]] = {}
    bridge: list[tuple[float, float]] = []
    for r in admitted_rows:
        center = r["statistics"][r["arms"].index(CENTER)]
        if r["kind"] == "bridge":
            plain = [s for a, s in zip(r["arms"], r["statistics"], strict=True) if a == PLAIN]
            value, error = pooled([(s["contrast"], s["se"]) for s in plain])
            bridge.append((center["contrast"] - value, math.hypot(center["se"], error)))
            continue
        for arm, s in zip(r["arms"], r["statistics"], strict=True):
            q4_steps, z12_steps, z8c_steps = ARMS[arm]
            if r["kind"] in Z12_KINDS:
                z_points.append((5.0 * z12_steps, s["contrast"], s["se"]))
            elif r["kind"] in DECIDING_KINDS:
                z8_points.append((5.0 * z8c_steps, s["contrast"], s["se"]))
            elif arm != CENTER:
                q4_points.append(
                    (5.0 * q4_steps, s["contrast"] - center["contrast"], math.hypot(s["se"], center["se"]))
                )
            if r["kind"] in DECIDING_KINDS and id(r) in split_rows:
                split.setdefault(arm, []).append((s["d2_split"], s["d2_split_se"]))
    ratios: dict[str, list[float]] = {}
    for r in admitted_rows:
        center_visibility = r["statistics"][r["arms"].index(CENTER)]["visibility"]
        for arm, s in zip(r["arms"], r["statistics"], strict=True):
            if arm != CENTER:
                ratios.setdefault(arm, []).append(s["visibility"] / center_visibility)
    exact_center = float(rs.visibility(forward_law(CENTER)[None])[0])
    reported["visibility_ratio"] = {
        arm: {"measured": values, "exact": float(rs.visibility(forward_law(arm)[None])[0]) / exact_center}
        for arm, values in sorted(ratios.items())
    }
    agree = False
    if bridge:
        value, error = pooled(bridge)
        agree = abs(value) <= Z_RESOLVE * error
        reported["bridge"] = {"padded_less_plain_contrast": [value, error], "within_resolve": agree}
    if len(z_points) >= 4:
        reported["z12_parabola"] = parabola_minimum(z_points)
    if len(z8_points) >= 4:
        reported["z8c_parabola"] = parabola_minimum(z8_points)
    if split:
        reported["d2_split"] = {arm: list(pooled(v)) for arm, v in sorted(split.items())}
    if len(q4_points) >= 2 and "center_contrast" in decision["numbers"]:
        center_value = decision["numbers"]["center_contrast"][0]
        reported.update(q4_reports(q4_points, center_value, agree, retained_q4_points()))
    ledger = "unchanged; the numbers are reported"
    if decision["label"] in ERROR_WORLDS:
        ledger = f"changes to the statement of {decision['label']}"
    return {"batch_rows": rows, "decision": {**decision, "a5_186": ledger}, "reported": reported}


def q4_reports(
    points: list[tuple[float, float, float]],
    center: float,
    bridge_agrees: bool,
    retained: list[tuple[float, float, float]],
) -> dict[str, Any]:
    """The q4 line of the new arms and, when the bridge agrees, its slope comparison with the retained points; the
    bridge compares centers alone, so the retained points join the line only when the new +-10 degree slope also lies
    within Z_RESOLVE standard errors of theirs, and a padding that changes the slope keeps them apart."""
    out: dict[str, Any] = {"q4_line": line_fit(points, center)}
    far = [p for p in points if abs(p[0]) == 10.0]
    if not (bridge_agrees and far and retained):
        return out
    new, old = line_fit(far, center), line_fit(retained, center)
    gap = new["slope_per_degree"] - old["slope_per_degree"]
    gap_se = math.hypot(new["slope_se"], old["slope_se"])
    agrees = abs(gap) <= Z_RESOLVE * gap_se
    out["q4_slope_against_retained"] = {"difference": [gap, gap_se], "within_resolve": agrees}
    if agrees:
        out["q4_line_with_retained"] = line_fit(points + retained, center)
    return out


def retained_q4_points() -> list[tuple[float, float, float]]:
    """(q4 degrees, contrast less its batch center, error) of the predecessor's admitted q4 batches, whose center is
    the plain arm; they join the q4 line only when the bridge reads padded and plain centers alike and the slopes
    of the new and retained +-10 degree arms agree."""
    analysis = json.loads((ROOT / PREDECESSOR_ANALYSIS).read_text(encoding="utf-8"))
    points = []
    for row in analysis["batch_rows"].values():
        if row["kind"] != "q4-10" or not row["guard"]["admitted"]:
            continue
        center = row["statistics"][row["arms"].index(PLAIN)]
        for arm, s in zip(row["arms"], row["statistics"], strict=True):
            if arm != PLAIN:
                degrees = -10.0 if arm.endswith("-m10") else 10.0
                points.append((degrees, s["contrast"] - center["contrast"], math.hypot(s["se"], center["se"])))
    return points


def analyze(run_dirs: list[Path], case_root: Path | None = pcs.CASES_ROOT) -> dict[str, Any]:
    """Score collected batches of one series. A Tuna-17 series that holds fewer batches than the case reports its
    batch list only; a QX series reports the control verdict a Tuna-17 submission needs."""
    data = pca.read_series(run_dirs, case_root, series_of, "data", BATCH_FIELDS, pcs.load_run)
    shared, shots = data["shared"], data["shots"]
    emulator = shared["backend_type_id"] == 1
    expected = sorted(r["batch"] for r in batch_rows(QX_SERIES if emulator else TUNA_SERIES))
    held = sorted({k.split("/")[0] for k in shots})
    head: dict[str, Any] = {
        "schema": ANALYSIS_SCHEMA,
        "claim_kind": pcs.CONTROL_KIND if emulator else "hardware acquisition",
        "backend": shared["backend"],
        "batch_cases_sha256": data["digests"],
    }
    if emulator:
        head["qx_control"] = pca.control_report(data["arms"], cc.coin_counts)
    if held != expected:
        return {**head, "complete": False, "batches": held}
    if emulator:
        return {**head, "complete": True}
    return {**head, "complete": True, **evaluate(shots, shared)}


def sanity(run_dirs: list[Path], case_root: Path | None = pcs.CASES_ROOT) -> dict[str, Any]:
    """Bind each collected batch to the series case and report the readout drift between the brackets it is given."""
    loaded = []
    for run_dir in sorted(run_dirs, key=lambda p: p.name):
        cases = json.loads((run_dir / "cases.json").read_text(encoding="utf-8"))
        case_batch = None if case_root is None else case_root / series_of(run_dir) / cases["batch"]
        loaded.append(pcs.load_run(run_dir, case_batch))
    batches = [r["cases"]["batch"] for r in loaded]
    if len(set(batches)) != len(batches):
        raise SystemExit(f"a batch appears twice in {batches}")
    paired = [r for r in loaded if any(row["kind"] == "readout" for row in r["cases"]["circuits"])]
    return {"batches": batches, "drift": pcs.runs_drift(paired) if paired else None}


# Self-test --------------------------------------------------------------------------------------------------------


def self_test() -> str:
    """The emitter and the forward model agree with the predecessor, the padding changes no law, each injected Rz
    cancels its error, and each truth of TRUTHS with a required label reads it."""
    rs.replay_check()
    center_check()
    lines = []
    for arm, old in (
        (PLAIN, PLAIN),
        (CENTER, PLAIN),
        ("b0-rxz-q4-p10", "b0-rx-q4-p10"),
        ("b0-rxz-q4-m10", "b0-rx-q4-m10"),
    ):
        gap = float(np.abs(forward_law(arm) - rs.forward_law(old)).max())
        if gap > 1e-12:
            raise ValueError(f"{arm} differs from the predecessor's {old} forward law by {gap}")
    lines.append("plain, padded center and padded q4 +-10 arms equal the predecessor's forward laws")
    # An injected Rz(phi) cancels the error it mimics at -phi: the arm reads the exact center.
    for arm, (_, z12, z8c) in ARMS.items():
        if z12 or z8c:
            world, steps = ("q12_phase", z12) if z12 else (Q8_PHASE, z8c)
            gap = float(np.abs(forward_law(arm, world, -steps * STEP) - forward_law(CENTER)).max())
            if gap > 1e-12:
                raise ValueError(f"{arm} under {world} at {-steps * STEP} differs from the exact center by {gap}")
    lines.append("each injected Rz cancels the opposite q12 or q8 phase exactly")
    for arm in ARM_NAMES:
        gap = float(np.abs(forward_law(arm, AFTER_PULSE, -0.18) - forward_law(arm, "q12_phase", -0.18)).max())
        if gap > 1e-12:
            raise ValueError(f"{arm}: the after-pulse placement differs from the before-pulse one by {gap}")
    lines.append("a q12 phase after each pulse gives the laws of one before each pulse")
    build_tables()
    required = [name for name, truth in TRUTHS.items() if truth[4] is not None]
    for name, decision in zip(required, ordered_map(expected_decision, required, min_items=2), strict=True):
        got = decision["label_at_expected_values"]
        if got != TRUTHS[name][4]:
            raise ValueError(f"planted {name} reads {got}, not {TRUTHS[name][4]}")
        lines.append(f"planted {name}: {got}")
    for name, got in zip(MIXED, ordered_map(mixed_label, list(MIXED), min_items=2), strict=True):
        if got in ERROR_WORLDS:
            raise ValueError(f"{name} reads the deciding label {got}")
        lines.append(f"{name}: {got}")
    return "\n".join(lines)


def mixed_label(name: str) -> str:
    matrix = predecessor_matrix()
    return str(decide(scenario_batches(name), lambda b: matrix)["label"])


def report_text(report: dict[str, Any]) -> str:
    """The analysis report as JSON; a non-finite number outside decide()'s reportable() fields stops the write."""
    return json.dumps(report, indent=1, sort_keys=True, allow_nan=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--sanity", type=Path, nargs="+", metavar="RUN_DIR")
    mode.add_argument("--analyze", type=Path, nargs="+", metavar="RUN_DIR")
    mode.add_argument("--self-test", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.write:
        write(args.write)
    elif args.check:
        check(args.check)
    elif args.sanity:
        print(json.dumps(sanity(args.sanity), indent=1, sort_keys=True))
    elif args.analyze:
        if args.out is None:
            parser.error("--analyze needs --out")
        report = analyze(args.analyze)
        args.out.write_text(report_text(report), encoding="utf-8")
        print(f"wrote {args.out}")
        if "qx_control" in report and not (report["complete"] and report["qx_control"]["pass"]):
            return 1
    else:
        print(self_test())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
