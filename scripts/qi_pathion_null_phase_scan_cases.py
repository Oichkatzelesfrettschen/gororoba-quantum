"""Tuna-17 case for the null block's selector offset (row A5-186): an injected phase scan on q12 and an angle scan
on q4 of the retained b0.

The injected X-rotation scan (scripts/qi_pathion_null_rotation_scan_cases.py, verdict unresolved_none) left two
elementary errors ahead of its preregistered worlds in an exploratory reading
(docs/notes/quantum_inspire/tuna17-null-rotation-scan-line-phase.md): a rotation about z before each pulse of q12
and a conditional-phase error of the CZ gates of coupler 8-12. Both give a selector contrast that is even in the
error with exact pulses, so the retained offset fixes a size and leaves the sign open, and the retained arms vary
pulse amplitudes alone. This module builds the case that injects a known phase on q12.

Mechanism. Tuna-17 lists `Rz(angle)` among its native gates (site/kbase_tuna-operational-specifics.md) and its
compiler keeps each injected `Rz` as its own instruction (docs/evidence/quantum_inspire/toolchain-token-recovery.json).
hypothesis: the processor applies `Rz` as a frame update of zero duration, so an `Rz(phi)` before each of q12's five
pulses adds phi to whatever phase precedes that pulse and leaves the schedule, the pulse count and the CZ count of
the center arm; the provider publishes no pulse schedule. The analysis reports each arm's visibility over its
center's beside the exact circuit's ratio; a phase on q12 moves the z12 ratios too, so that comparison bounds a
finite duration of `Rz` and does not isolate it. Under a phase theta on q12 the contrast against phi is the
curve of an exact circuit shifted by -theta, with its least value at phi = -theta. Under a conditional phase of
coupler 8-12 the curve keeps a nonzero least value and the d2 split of the z12 arms departs from zero. With exact
gates the curve is even in phi with its least value, zero, at phi = 0.

Circuits. Every circuit is the retained b0 text with each X90 as Rx(pi/2) (the predecessor's center arm, emitted
byte for byte by its arm_lines) and one rewrite: "b0-rx-q4-mK" / "-pK" put q4's eight pulses at 90 -+ K degrees;
"b0-rx-z12-mK" / "-pK" put Rz(-+K degrees) before each pulse of q12. Angles are multiples of pi/36.

Series. Eight data batches [first arm, b0-rx, second arm] in a forward round and a mirror round with the outer
arms exchanged; a readout batch [readout-0, readout-1] before and after every data batch supplies the assignment
matrix and the readout admission of the predecessor.

Decision. For each world of WORLDS, fit_batch() fits the world's one parameter to the three raw selector contrasts
of a z12 batch and to the d2 split of each outer arm less the center arm's, at the retention that reproduces the
center arm's visibility, for each contraction share of the predecessor's MIX_FINE; decide() sums the chi-squares
over the admitted z12 batches at the one share that makes the sum least, and a deciding label also needs each z12
kind to agree with the series. The gate-noise families of the predecessor are outside this fit (their tables exist
for its worlds alone), which the case states as a limit. preregistered() states the rules and
operating_characteristics() simulates them under sampling noise.

Usage: "$PYTHON" scripts/qi_pathion_null_phase_scan_cases.py
       (--write DIR | --check DIR | --sanity RUN_DIR... | --analyze RUN_DIR... --out FILE | --self-test)
Bit strings put qubit 0 at the rightmost character."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from functools import cache
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import chi2 as chi2_law

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import qi_pathion_null_rotation_scan_cases as rs  # noqa: E402

cc, oc, pca, pcs, zd = rs.cc, rs.oc, rs.pca, rs.pcs, rs.zd

TUNA_SERIES = "pathion_null_phase_scan_tuna_17"
QX_SERIES = "pathion_null_phase_scan_qx"
SCHEMA = "qi-pathion-null-phase-scan-cases-v1"
SERIES_SCHEMA = "qi-pathion-null-phase-scan-series-v1"
ANALYSIS_SCHEMA = "qi-pathion-null-phase-scan-analysis-v1"
PREDECESSOR_ANALYSIS = "results/quantum_inspire/pathion_null_rotation_scan_tuna_17_analysis.json"
KEYS, NOUT, STEP, CENTER = rs.KEYS, rs.NOUT, rs.STEP, rs.CENTER
Q4, Q12 = 4, 12
COUPLER = (8, 12)

# Arm -> (steps of pi/36 added to each q4 pulse angle, steps of pi/36 of the Rz before each q12 pulse).
ARMS: dict[str, tuple[int, int]] = {
    CENTER: (0, 0),
    "b0-rx-q4-m5": (-1, 0),
    "b0-rx-q4-p5": (1, 0),
    "b0-rx-q4-p10": (2, 0),
    "b0-rx-q4-p15": (3, 0),
    "b0-rx-z12-m30": (0, -6),
    "b0-rx-z12-m10": (0, -2),
    "b0-rx-z12-p10": (0, 2),
    "b0-rx-z12-p30": (0, 6),
}
ARM_NAMES = tuple(ARMS)
# Scan kind -> (first arm, second arm) of its forward batch; the mirror batch exchanges them.
SCANS: dict[str, tuple[str, str]] = {
    "q4-near": ("b0-rx-q4-m5", "b0-rx-q4-p5"),
    "q4-far": ("b0-rx-q4-p10", "b0-rx-q4-p15"),
    "z12-10": ("b0-rx-z12-m10", "b0-rx-z12-p10"),
    "z12-30": ("b0-rx-z12-m30", "b0-rx-z12-p30"),
}
Z12_KINDS = ("z12-10", "z12-30")
Q4_KINDS = ("q4-near", "q4-far")

SCAN_SHOTS, READOUT_SHOTS, QX_SHOTS = rs.SCAN_SHOTS, rs.READOUT_SHOTS, rs.QX_SHOTS
QX_QUBITS, QX_BATCH_CIRCUITS = rs.QX_QUBITS, rs.QX_BATCH_CIRCUITS
PAUSE_CEILING = rs.PAUSE_CEILING
DESIGN_VISIBILITY = 0.42

# Worlds of the decision: exact gates, a rotation about z before each pulse of q12, a conditional-phase error of
# each CZ of coupler 8-12. The parameter grid of the two error worlds is in radians.
THETA = np.linspace(-0.50, 0.50, 501)
WORLDS: dict[str, np.ndarray] = {"exact": np.zeros(1), "q12_phase": THETA, "coupler_phase": THETA}
# A placement outside the decision that forward_laws also simulates: the rotation about z after each q12 pulse. Its
# laws equal those of q12_phase (every q12 operation between two pulses is diagonal, the first rotation acts on
# |0> and the last precedes a measurement in z), so the q12_phase label names a single-qubit phase at q12's pulses
# and leaves its placement open.
AFTER_PULSE = "q12_phase_after_pulse"
ADEQUACY_ALPHA = rs.ADEQUACY_ALPHA
SEPARATION = rs.SEPARATION
# A z12 kind disagrees with the series' world when it reads the other error world lower by more than this. At 0 a
# series whose +-10 degree batches follow a q12 phase and whose +-30 degree batches a coupler phase reads a
# deciding label in 50 of 500 simulated series and a single mechanism reads phase_mixed in 1 to 46; at 6.63 (the
# upper 0.01 point of chi-square with one degree of freedom) the counts are 257 and 1 to 2. The +-10 degree arms
# separate the two error worlds by about 13 per kind, so no margin serves both; 0 guards the ledger row.
KIND_MARGIN = 0.0
SEEN_CACHE: dict[tuple[str, tuple[str, ...], bytes, float], tuple[np.ndarray, np.ndarray]] = {}
GUARD_LIMIT = rs.GUARD_LIMIT
Z_RESOLVE = rs.Z_RESOLVE
BATCH_FIELDS = rs.BATCH_FIELDS


# Circuits ---------------------------------------------------------------------------------------------------------


def arm_lines(arm: str, place: dict[int, int]) -> list[str]:
    """Instruction lines of an arm with physical qubit q written as place[q]."""
    q4_steps, z12_steps = ARMS[arm]
    lines = []
    for gate, angle, qubits in rs.retained()["ops"]:
        where = ", ".join(f"q[{place[q]}]" for q in qubits)
        if gate == "X90":
            if qubits[0] == Q12 and z12_steps:
                lines.append(f"Rz({z12_steps * STEP!r}) {where}")
            name = rs.rx_text(q4_steps if qubits[0] == Q4 else 0)
        else:
            name = gate if angle is None else f"{gate}({angle})"
        lines.append(f"{name} {where}")
    return lines


def arm_note(arm: str) -> str:
    q4_steps, z12_steps = ARMS[arm]
    tail = ""
    if q4_steps:
        tail = f", {q4_steps * 5:+d} degrees on q4"
    if z12_steps:
        tail = f", Rz({z12_steps * 5:+d} degrees) before each pulse of q12"
    return f"{rs.retained()['note']} every X90 as Rx(pi/2){tail}"


def arm_text(arm: str, place: dict[int, int], nqubits: int) -> str:
    lines = zd.header(nqubits) + [arm_note(arm)]
    return "\n".join(lines + arm_lines(arm, place) + ["", "barrier q", "b = measure q", ""])


def center_check() -> None:
    """The center arm equals the predecessor's center arm byte for byte."""
    region = rs.retained()["region"]
    place = {q: q for q in region}
    if arm_text(CENTER, place, cc.NQUBITS) != rs.arm_text(CENTER, place, cc.NQUBITS):
        raise ValueError("the center arm differs from the predecessor's b0-rx")


# Forward model ----------------------------------------------------------------------------------------------------


def forward_laws(arm: str, world: str, thetas: np.ndarray) -> np.ndarray:
    """Laws over the logical outcome index of an arm under a world, one row per value of `thetas`: a state vector
    over the five region qubits. `q12_phase` rotates q12 by theta about z before each of its pulses, after the
    arm's own Rz; `coupler_phase` gives each CZ of coupler 8-12 the conditional phase pi + theta."""
    if world not in WORLDS and world != AFTER_PULSE:
        raise ValueError(f"unknown world {world}")
    ref = rs.retained()
    region = ref["region"]
    axis_of = {q: i for i, q in enumerate(region)}
    q4_steps, z12_steps = ARMS[arm]
    count = len(thetas)
    shape = (2,) * len(region)
    psi = np.zeros((count, *shape), dtype=complex)
    psi.reshape(count, -1)[:, 0] = 1.0
    index = np.indices(shape)
    zero = np.zeros(count)
    for gate, angle, qubits in ref["ops"]:
        if gate == "CZ":
            both = index[axis_of[qubits[0]]] * index[axis_of[qubits[1]]]
            extra = thetas if world == "coupler_phase" and tuple(sorted(qubits)) == COUPLER else zero
            phase = -np.exp(1j * extra).reshape(count, *([1] * len(region)))
            psi = psi * np.where(both[None] == 1, phase, 1.0)
            continue
        q = qubits[0]
        if gate == "Rz":
            unitary = np.broadcast_to(rs.rotation("z", float(angle or 0.0)), (count, 2, 2))
        else:
            pulse = rs.rotation("x", math.pi / 2 + (q4_steps * STEP if q == Q4 else 0.0))
            if q == Q12:
                frame = z12_steps * STEP + (thetas if world == "q12_phase" else zero)
                after = thetas if world == AFTER_PULSE else zero
                unitary = np.stack(
                    [
                        rs.rotation("z", float(a)) @ pulse @ rs.rotation("z", float(f))
                        for f, a in zip(frame, after, strict=True)
                    ]
                )
            else:
                unitary = np.broadcast_to(pulse, (count, 2, 2))
        moved = np.moveaxis(psi, axis_of[q] + 1, -1)
        low, high = moved[..., 0], moved[..., 1]
        u = unitary[:, :, :, None, None, None, None]
        psi = np.moveaxis(
            np.stack([u[:, 0, 0] * low + u[:, 0, 1] * high, u[:, 1, 0] * low + u[:, 1, 1] * high], axis=-1),
            -1,
            axis_of[q] + 1,
        )
    prob = np.abs(psi) ** 2
    order_axes = [0, *(axis_of[ref["roles"][key]] + 1 for key in reversed(KEYS))]
    return np.asarray(prob.transpose(order_axes).reshape(count, NOUT), dtype=float)


def forward_law(arm: str, world: str = "exact", theta: float = 0.0) -> np.ndarray:
    return np.asarray(forward_laws(arm, world, np.array([theta]))[0])


@cache
def world_table(world: str) -> np.ndarray:
    """Exact laws of every arm on the world's parameter grid, shape (parameter, arm, outcome)."""
    return np.stack([forward_laws(arm, world, WORLDS[world]) for arm in ARM_NAMES], axis=1)


def seen_contrasts(
    world: str, arms: tuple[str, ...], matrix: np.ndarray, center_visibility: float
) -> tuple[np.ndarray, np.ndarray]:
    """Raw selector contrasts of `arms`, then the d2 split of each outer arm less the center arm's, under a world
    through the assignment `matrix`, shape (share, parameter, 2 x arm - 1) over rs.MIX_FINE, and the retention used,
    shape (share, parameter): per contraction share and parameter value, the retention at which the world's center
    arm reads `center_visibility`. Results are kept per argument set; a simulation refits one set many times."""
    key = (world, arms, matrix.tobytes(), float(center_visibility))
    if key in SEEN_CACHE:
        return SEEN_CACHE[key]
    outer = [n for n, a in enumerate(arms) if a != CENTER]
    table = world_table(world)
    picked = [ARM_NAMES.index(a) for a in arms]
    center = table[:, [ARM_NAMES.index(CENTER)]]
    models, kept = [], []
    for mix in rs.MIX_GRID:
        seen = np.stack(
            [rs.visibility(rs.read(rs.contract(center, float(r), float(mix)), matrix))[:, 0] for r in rs.RETENTION_GRID]
        )
        retention = np.empty(seen.shape[1])
        for j in range(seen.shape[1]):
            order = np.argsort(seen[:, j])
            retention[j] = float(np.interp(center_visibility, seen[order, j], rs.RETENTION_GRID[order]))
        read = rs.read(rs.contract(table[:, picked], retention, float(mix)), matrix)
        split = rs.d2_split(read)[0]
        relative = split[..., outer] - split[..., [arms.index(CENTER)]]
        models.append(np.concatenate([rs.selector_contrast(read), relative], axis=-1))
        kept.append(retention)
    SEEN_CACHE[key] = (rs.fine_mix(np.stack(models)), rs.fine_mix(np.stack(kept)))
    return SEEN_CACHE[key]


def fit_batch(
    arms: tuple[str, ...], contrasts: np.ndarray, errors: np.ndarray, matrix: np.ndarray, center_visibility: float
) -> dict[str, dict[str, np.ndarray]]:
    """Per world and contraction share, the least chi-square over the world's parameter of a batch's raw selector
    contrasts and relative d2 splits (`contrasts` and `errors` hold the three contrasts, then the d2 split of each
    outer arm less the center arm's): "chi2", "parameter", "retention" (one value per share) and "predicted"
    (share, 5).

    The split enters relative to the batch's center because the predecessor's centers read a d2 split of
    +0.0083 +- 0.0017 that no world of this decision gives; the coupler world's split is odd in the injected phase
    and survives the subtraction. The statistics of one batch share shots and a center; the sum treats them as
    independent, which the case states as a limit of the bound."""
    rows: dict[str, dict[str, np.ndarray]] = {}
    take = np.arange(len(rs.MIX_FINE))
    for world, grid in WORLDS.items():
        model, kept = seen_contrasts(world, arms, matrix, center_visibility)
        curve = (((model - contrasts) / errors) ** 2).sum(-1)
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
    first, last = SCANS[kind]
    return [first, CENTER, last] if replicate == 0 else [last, CENTER, first]


def batch_order() -> list[tuple[str, int]]:
    """(kind, replicate) of the eight data batches: the four scans, then the same list backwards."""
    first = [(kind, 0) for kind in SCANS]
    return first + [(kind, 1) for kind, _ in reversed(first)]


def batch_rows(series_name: str) -> list[dict[str, Any]]:
    """The batches of a series. Tuna-17: a readout batch, then each data batch of batch_order followed by a readout
    batch. QX: every arm, three to a batch."""
    rows: list[dict[str, Any]] = []

    def data(arm: str) -> dict[str, Any]:
        q4_steps, z12_steps = ARMS[arm]
        return {
            "file": f"{arm}.cq",
            "kind": "data",
            "template": "b0",
            "arm": {"q4_steps": q4_steps, "z12_steps": z12_steps},
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
    return file.removesuffix(".cq")


def batch_values(batch: dict[str, Any]) -> int:
    """Fitted values of a z12 batch: three contrasts, and two relative d2 splits when d2's qubit passed its guard."""
    return 5 if batch.get("split_admitted", True) else 3


def adequacy_limit(world: str, values: list[int]) -> float:
    """Chi-square bound of a world over z12 batches that hold `values` fitted values each: one fitted parameter per
    batch for an error world and none for the exact world, and one contraction share for the series."""
    freedom = sum(v - (0 if world == "exact" else 1) for v in values) - 1
    return float(chi2_law.ppf(1 - ADEQUACY_ALPHA, freedom))


def preregistered() -> dict[str, str]:
    return {
        "estimates": "per data circuit, the raw selector contrast P(s=0 | coin read 1) - P(s=0 | coin read 0) with "
        "its binomial standard error, the d2 split and the visibility of the center arm of each batch",
        "guard": "a data batch is admitted when e01 and e10 of each qubit the contrast reads (d0, d1, the selector "
        f"and the coin) change by at most {GUARD_LIMIT} between the readout batch before it and the one after; its "
        "d2 splits enter the fit only when d2's qubit passes the same bound, otherwise the batch is fitted on its "
        "three contrasts; the decision needs at least one admitted batch of each z12 kind, otherwise it reads "
        "unresolved_guard",
        "control": "the inverse-variance mean of the center arm's contrast over the admitted batches exceeds "
        f"{Z_RESOLVE} standard errors; otherwise the decision reads offset_absent (within) or offset_reversed (below)",
        "fit": "for each world (exact gates, a rotation about z before each pulse of q12, a conditional-phase error "
        "of the CZ gates of coupler 8-12) one parameter per admitted z12 batch is fitted to its three contrasts and "
        "to the d2 split of each outer arm less its center arm's, at the "
        "retention that reproduces the batch's center visibility through its own bracket assignment; the chi-squares "
        "are summed at the one contraction share of the predecessor's grid that makes the sum least",
        "adequacy": f"a world is adequate when its sum is at most the upper {ADEQUACY_ALPHA} point (the "
        f"{100 * (1 - ADEQUACY_ALPHA):.1f}th percentile) of chi-square with one degree of freedom per fitted value "
        "(5 per z12 batch, 3 when its d2 splits are left out), less one per fitted parameter and one for the share",
        "labels": "exact_parabola: the exact world is adequate, so a phase on or around q12 is falsified as the "
        "cause of the offset; q12_phase or coupler_phase: that world is adequate, its sum lies at least "
        f"{SEPARATION} below the other error world's, and each z12 kind, summed over its admitted replicates, reads "
        f"that world at or below the upper {ADEQUACY_ALPHA} point of chi-square on its own degrees of freedom and "
        "no higher than the other error world; phase_mixed: the sums prefer one error world and a kind does not; "
        "phase_unresolved: an error world is adequate and the two are closer; none_adequate: no world is "
        "adequate. q12_phase names a single-qubit phase at q12's pulses: a rotation about z after each pulse gives "
        "the same laws as one before each pulse",
        "sign": "reported with a q12_phase or coupler_phase label: the fitted parameter of each admitted z12 batch, "
        "and the injected phase of least contrast from a parabola through the pooled z12 arms and centers",
        "d2_split": "also reported beside the label: the d2 split of the +10 and +30 degree z12 arms pooled over the "
        "admitted replicates, beside the values each world predicts",
        "q4_line": "reported outside the label: a weighted straight line through the contrast of each q4 arm less "
        "its batch center against q4's injected angle (-5, +5, +10, +15 degrees, 0 at the center), with its "
        "chi-square on 3 degrees of freedom, slope and the angle at which the pooled center plus the line reads zero",
        "visibility": "reported outside the label: each arm's visibility over its batch center's, beside the "
        "exact circuit's ratio; a phase on q12 moves the z12 ratios with the total phase, so the comparison bounds "
        "a finite duration of Rz and does not isolate it",
        "line_phase": "outside this analysis: the shot-order fold of "
        "docs/evidence/qi-null-rotation-scan-line-phase/line_phase_split.py is run on the retained jobs afterwards "
        "and decides nothing",
        "ledger": "A5-186 changes only on q12_phase or coupler_phase, to the statement of that label; every other "
        "label reports the numbers",
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


def decide(batches: list[dict[str, Any]], matrix_of: Any) -> dict[str, Any]:
    """Label and numbers from data batches: each holds "name", "kind", "arms", "contrasts", "errors", "splits",
    "split_errors", "center_visibility", "admitted" and, optionally, "split_admitted" (default true); `matrix_of(batch)`
    is its assignment matrix."""
    admitted = [b for b in batches if b["admitted"]]
    numbers: dict[str, Any] = {"admitted_batches": [b["name"] for b in admitted]}
    z12 = [b for b in admitted if b["kind"] in Z12_KINDS]
    if {b["kind"] for b in z12} != set(Z12_KINDS):
        return {"label": "unresolved_guard", "numbers": numbers}
    centers = [(b["contrasts"][b["arms"].index(CENTER)], b["errors"][b["arms"].index(CENTER)]) for b in admitted]
    center = pooled(centers)
    numbers["center_contrast"] = list(center)
    if center[0] <= Z_RESOLVE * center[1]:
        label = "offset_reversed" if center[0] < -Z_RESOLVE * center[1] else "offset_absent"
        return {"label": label, "numbers": numbers}
    fits = {
        b["name"]: fit_batch(
            tuple(b["arms"]),
            np.array([*b["contrasts"], *relative_splits(b)[0]]),
            np.array([*b["errors"], *relative_splits(b)[1]]),
            matrix_of(b),
            b["center_visibility"],
        )
        for b in z12
    }
    total = {w: np.sum([fits[b["name"]][w]["chi2"] for b in z12], axis=0) for w in WORLDS}
    share = {w: int(total[w].argmin()) for w in WORLDS}
    best = {w: float(total[w][share[w]]) for w in WORLDS}
    limit = {w: adequacy_limit(w, [batch_values(b) for b in z12]) for w in WORLDS}
    adequate = {w: best[w] <= limit[w] for w in WORLDS}
    numbers.update(
        chi2={w: round(best[w], 3) for w in WORLDS},
        adequacy_limit={w: round(limit[w], 3) for w in WORLDS},
        contraction_share={w: float(rs.MIX_FINE[share[w]]) for w in WORLDS},
        parameters={
            w: {b["name"]: float(fits[b["name"]][w]["parameter"][share[w]]) for b in z12}
            for w in WORLDS
            if w != "exact"
        },
        predicted={
            w: {b["name"]: [float(x) for x in fits[b["name"]][w]["predicted"][share[w]]] for b in z12} for w in WORLDS
        },
    )
    per_batch = {
        w: {b["name"]: float(fits[b["name"]][w]["chi2"][share[w]]) for b in z12} for w in WORLDS if w != "exact"
    }
    # Each z12 kind, summed over its admitted replicates: the series' world must fit it and the other error world
    # may undercut it by at most KIND_MARGIN.
    kind_chi2 = {
        w: {k: sum(per_batch[w][b["name"]] for b in z12 if b["kind"] == k) for k in Z12_KINDS} for w in per_batch
    }
    bound = {
        k: float(chi2_law.ppf(1 - ADEQUACY_ALPHA, sum(batch_values(b) - 1 for b in z12 if b["kind"] == k)))
        for k in Z12_KINDS
    }
    numbers.update(
        batch_chi2=per_batch,
        kind_chi2={w: {k: round(v, 3) for k, v in rows.items()} for w, rows in kind_chi2.items()},
        kind_limit={k: round(v, 3) for k, v in bound.items()},
        split_admitted=[b["name"] for b in z12 if b.get("split_admitted", True)],
    )

    def homogeneous(world: str, other: str) -> bool:
        return all(v <= bound[k] and v <= kind_chi2[other][k] + KIND_MARGIN for k, v in kind_chi2[world].items())

    if adequate["exact"]:
        label = "exact_parabola"
    elif adequate["q12_phase"] and best["q12_phase"] <= best["coupler_phase"] - SEPARATION:
        label = "q12_phase" if homogeneous("q12_phase", "coupler_phase") else "phase_mixed"
    elif adequate["coupler_phase"] and best["coupler_phase"] <= best["q12_phase"] - SEPARATION:
        label = "coupler_phase" if homogeneous("coupler_phase", "q12_phase") else "phase_mixed"
    elif adequate["q12_phase"] or adequate["coupler_phase"]:
        label = "phase_unresolved"
    else:
        label = "none_adequate"
    return {"label": label, "numbers": numbers}


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


def predecessor_matrix() -> np.ndarray:
    """Assignment matrix at the mean bracket rates of the predecessor's ten data batches."""
    analysis = json.loads((ROOT / PREDECESSOR_ANALYSIS).read_text(encoding="utf-8"))
    guards = [r["guard"] for r in analysis["batch_rows"].values()]
    ref = rs.retained()

    def rate(q: int, i: int) -> float:
        return float(np.mean([(g["before"][str(q)][i] + g["after"][str(q)][i]) / 2 for g in guards]))

    mean: dict[int, tuple[float, float]] = {int(q): (rate(q, 0), rate(q, 1)) for q in ref["region"]}
    return np.asarray(cc.readout_matrix(mean, ref["roles"]))


TRUTHS: dict[str, tuple[str, float, float, str]] = {
    "exact gates": ("exact", 0.0, 0.0, "offset_absent"),
    "q12 phase -0.18 rad": ("q12_phase", -0.18, 0.0, "q12_phase"),
    "q12 phase +0.18 rad": ("q12_phase", 0.18, 0.0, "q12_phase"),
    "q12 phase -0.15 rad": ("q12_phase", -0.15, 0.0, "q12_phase"),
    "coupler 8-12 phase -0.25 rad": ("coupler_phase", -0.25, 0.0, "coupler_phase"),
    "coupler 8-12 phase +0.25 rad": ("coupler_phase", 0.25, 0.0, "coupler_phase"),
    "exact gates, selector flip 0.0166 when q12 reads 0": ("exact", 0.0, 0.0166, "none_adequate"),
    "exact gates, selector flip 0.036 when q12 reads 0": ("exact", 0.0, 0.036, "none_adequate"),
}
# Truths the prediction record states: world, parameter in radians, probability of a selector flip conditioned on
# d0 reading 0 (the predecessor's readout world, outside this decision's worlds), label at expected values.


def truth_row(
    world: str, theta: float, matrix: np.ndarray, flip: float = 0.0, mix: float = 0.0
) -> dict[str, dict[str, float]]:
    """Contrast and d2 split of every arm under a truth at the retention where its center reads the design
    visibility; `flip` is the probability that the selector read flips when d0 reads 0."""
    laws = np.stack([forward_law(arm, world, theta) for arm in ARM_NAMES])[None]
    center = laws[:, [ARM_NAMES.index(CENTER)]]
    seen_matrix = matrix @ oc.selector_flip(KEYS.index("d0"), 0, flip)
    seen = np.array(
        [
            float(rs.visibility(rs.read(rs.contract(center, float(r), mix), seen_matrix))[0, 0])
            for r in rs.RETENTION_GRID
        ]
    )
    order = np.argsort(seen)
    retention = float(np.interp(DESIGN_VISIBILITY, seen[order], rs.RETENTION_GRID[order]))
    read = rs.read(rs.contract(laws, retention, mix), seen_matrix)[0]
    contrast = rs.selector_contrast(read)
    split = rs.d2_split(read)[0]
    return {
        arm: {"contrast": round(float(contrast[i]), 5), "d2_split": round(float(split[i]), 5)}
        for i, arm in enumerate(ARM_NAMES)
    }


def planted_batches(row: dict[str, dict[str, float]]) -> list[dict[str, Any]]:
    """The eight data batches at a truth's expected contrasts and d2 splits and the design standard errors."""
    error = 1.0 / math.sqrt(SCAN_SHOTS)
    out = []
    for n, (kind, replicate) in enumerate(batch_order()):
        arms = scan_arms(kind, replicate)
        out.append(
            {
                "name": f"planted-{n}",
                "kind": kind,
                "arms": arms,
                "contrasts": [row[a]["contrast"] for a in arms],
                "errors": [error] * 3,
                "splits": [row[a]["d2_split"] for a in arms],
                "split_errors": [2 * error] * 3,
                "center_visibility": DESIGN_VISIBILITY,
                "admitted": True,
            }
        )
    return out


OC_DRAW = rs.OC_DRAW
OC_SEED_INDEX = 4
OC_SERIES = 500
# A static d2 split added to every circuit of a simulated series, the size the predecessor's centers read.
OC_SPLIT_OFFSET = 0.0083


def operating_characteristics(matrix: np.ndarray) -> dict[str, Any]:
    """Label counts of OC_SERIES simulated series per truth: Gaussian contrasts and d2 splits at the design standard
    errors around the truth's expected values, every batch admitted, a static d2 split of OC_SPLIT_OFFSET on every
    circuit; seeded from value OC_SEED_INDEX of OC_DRAW. The last scenario draws its +-10 degree batches from a q12
    phase and its +-30 degree batches from a coupler phase."""
    from qrng_seeds import read_record

    rng = np.random.default_rng(int(read_record(OC_DRAW)["values"][OC_SEED_INDEX]))
    error = 1.0 / math.sqrt(SCAN_SHOTS)
    scenarios = {
        name: planted_batches(truth_row(world, theta, matrix, flip)) for name, (world, theta, flip, _) in TRUTHS.items()
    }
    by_q12, by_coupler = scenarios["q12 phase -0.18 rad"], scenarios["coupler 8-12 phase -0.25 rad"]
    scenarios["z12 +-10 from q12 phase -0.18, z12 +-30 from coupler phase -0.25"] = [
        c if q["kind"] == "z12-30" else q for q, c in zip(by_q12, by_coupler, strict=True)
    ]
    counts: dict[str, dict[str, int]] = {}
    for name, base in scenarios.items():
        noise = rng.standard_normal((OC_SERIES, len(base), 6))
        tally: dict[str, int] = {}
        for i in range(OC_SERIES):
            series_batches = [
                {
                    **b,
                    "contrasts": [v + error * noise[i, n, j] for j, v in enumerate(b["contrasts"])],
                    "splits": [v + OC_SPLIT_OFFSET + 2 * error * noise[i, n, 3 + j] for j, v in enumerate(b["splits"])],
                }
                for n, b in enumerate(base)
            ]
            label = decide(series_batches, lambda b: matrix)["label"]
            tally[label] = tally.get(label, 0) + 1
        counts[name] = dict(sorted(tally.items()))
    return {
        "series_per_truth": OC_SERIES,
        "qrng_draw": OC_DRAW,
        "seed_index": OC_SEED_INDEX,
        "static_d2_split": OC_SPLIT_OFFSET,
        "label_counts": counts,
    }


def predictions() -> dict[str, Any]:
    matrix = predecessor_matrix()
    truths: dict[str, Any] = {}
    for name, (world, theta, flip, _) in TRUTHS.items():
        row = truth_row(world, theta, matrix, flip)
        decision = decide(planted_batches(row), lambda b: matrix)
        truths[name] = {
            "arms": row,
            "label_at_expected_values": decision["label"],
            "chi2_at_expected_values": decision["numbers"].get("chi2"),
        }
    return {
        "schema": "qi-pathion-null-phase-scan-prediction-v1",
        "design": design(),
        "design_visibility": DESIGN_VISIBILITY,
        "readout": f"mean bracket rates of {PREDECESSOR_ANALYSIS}",
        "preregistered": preregistered(),
        "truths": truths,
        "operating_characteristics": operating_characteristics(matrix),
        "limits": "contraction share 0 and the design visibility for every truth; Gaussian sampling noise with "
        "every batch admitted; the gate-noise families, a drifting readout and a phase beside a readout offset are "
        "not simulated",
    }


def write(directory: Path) -> None:
    for name, files in build().items():
        for rel, text in files.items():
            path = directory / name / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    (directory / TUNA_SERIES / "prediction.json").write_text(
        json.dumps(predictions(), indent=1, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote {TUNA_SERIES} and {QX_SERIES} under {directory}")


def check(directory: Path) -> None:
    """The case directories hold exactly the built files; CASE.md, the hand-written case, is the one extra file."""
    built = build()
    built[TUNA_SERIES]["prediction.json"] = json.dumps(predictions(), indent=1, sort_keys=True) + "\n"
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
    if not (directory / TUNA_SERIES / "CASE.md").is_file():
        raise ValueError(f"{directory / TUNA_SERIES}/CASE.md is missing")
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
    q4_points: list[tuple[float, float, float]] = []
    split: dict[str, list[tuple[float, float]]] = {}
    for r in admitted_rows:
        center = r["statistics"][r["arms"].index(CENTER)]
        for arm, s in zip(r["arms"], r["statistics"], strict=True):
            q4_steps, z12_steps = ARMS[arm]
            if r["kind"] in Z12_KINDS:
                z_points.append((5.0 * z12_steps, s["contrast"], s["se"]))
                if z12_steps > 0 and id(r) in split_rows:
                    split.setdefault(arm, []).append((s["d2_split"], s["d2_split_se"]))
            elif arm != CENTER:
                q4_points.append(
                    (5.0 * q4_steps, s["contrast"] - center["contrast"], math.hypot(s["se"], center["se"]))
                )
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
    if len(z_points) >= 4:
        reported["z12_parabola"] = parabola_minimum(z_points)
    if split:
        reported["d2_split"] = {arm: list(pooled(v)) for arm, v in sorted(split.items())}
    if len(q4_points) >= 2 and "center_contrast" in decision["numbers"]:
        reported["q4_line"] = line_fit(q4_points, decision["numbers"]["center_contrast"][0])
    ledger = "unchanged; the numbers are reported"
    if decision["label"] in ("q12_phase", "coupler_phase"):
        ledger = f"changes to the statement of {decision['label']}"
    return {"batch_rows": rows, "decision": {**decision, "a5_186": ledger}, "reported": reported}


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
    """The emitter and the forward model agree with the predecessor, and each truth of TRUTHS reads its label."""
    rs.replay_check()
    center_check()
    lines = []
    for arm, old in (("b0-rx", "b0-rx"), ("b0-rx-q4-p10", "b0-rx-q4-p10")):
        gap = float(np.abs(forward_law(arm) - rs.forward_law(old)).max())
        if gap > 1e-12:
            raise AssertionError(f"{arm} differs from the predecessor's forward law by {gap}")
    lines.append("center and q4 +10 arms equal the predecessor's forward laws")
    # An injected Rz(phi) cancels a q12 phase of -phi: the arm reads the exact center.
    for steps in (-6, -2, 2, 6):
        arm = next(a for a, (q4, z12) in ARMS.items() if z12 == steps)
        gap = float(np.abs(forward_law(arm, "q12_phase", -steps * STEP) - forward_law(CENTER)).max())
        if gap > 1e-12:
            raise AssertionError(f"{arm} at a q12 phase of {-steps * STEP} differs from the exact center by {gap}")
    lines.append("an injected Rz cancels the opposite q12 phase exactly")
    matrix = predecessor_matrix()
    for name, (world, theta, flip, label) in TRUTHS.items():
        got = decide(planted_batches(truth_row(world, theta, matrix, flip)), lambda b: matrix)["label"]
        if got != label:
            raise AssertionError(f"planted {name} reads {got}, not {label}")
        lines.append(f"planted {name}: {got}")
    # The rotation about z after each q12 pulse gives the laws of the rotation before each pulse.
    for arm in ARM_NAMES:
        gap = float(np.abs(forward_law(arm, AFTER_PULSE, -0.18) - forward_law(arm, "q12_phase", -0.18)).max())
        if gap > 1e-12:
            raise AssertionError(f"{arm}: the after-pulse placement differs from the before-pulse one by {gap}")
    lines.append("a q12 phase after each pulse gives the laws of one before each pulse")
    # A series whose +-10 degree batches follow a q12 phase and whose +-30 degree batches a coupler phase.
    by_q12 = planted_batches(truth_row("q12_phase", -0.18, matrix))
    by_coupler = planted_batches(truth_row("coupler_phase", -0.25, matrix))
    mixed = [c if q["kind"] == "z12-30" else q for q, c in zip(by_q12, by_coupler, strict=True)]
    got = decide(mixed, lambda b: matrix)["label"]
    if got in ("q12_phase", "coupler_phase"):
        raise AssertionError(f"a series of two mechanisms reads the deciding label {got}")
    lines.append(f"z12 batches of two mechanisms: {got}")
    return "\n".join(lines)


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
        args.out.write_text(json.dumps(report, indent=1, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
        print(f"wrote {args.out}")
        if "qx_control" in report and not (report["complete"] and report["qx_control"]["pass"]):
            return 1
    else:
        print(self_test())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
