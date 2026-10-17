"""Residual ZZ of every Tuna-17 coupler from one bipartite conditional-Ramsey configuration and its role swap.

Each coupling-map edge carries one flux-tunable coupler that the control
system parks between gates; the parked coupler leaves a diagonal residual
coupling, H / hbar = sum_q omega_q Z_q / 2 + sum_(a,b) J_ab Z_a Z_b / 2. A
target qubit A on the equator then winds at
nu_A(z) = omega_A + sum_k J_Ak s_k, s_k = +1 for neighbor outcome z_k = 0 and
-1 for z_k = 1, and J_Ak is half the shift of A's frequency when k flips
(gororoba_quantum/conditional_ramsey.py, conditional sectors).

H is diagonal, so every Z_k is conserved during the idle: a neighbor prepared
in |+> and read in Z at the end splits the shots into the sectors that
conditional Ramsey prepares separately. Tuna-17's coupling graph is
bipartite (parts), so one configuration makes every qubit of one part a
target and every qubit of the other a spectator in |+>, and conditioning each
target on all of its neighbors' outcomes fits every incident J at once: up to
2^4 sector rates against 1 + degree parameters, whose weighted residual tests
the pairwise, additive form (a three-body term or a drive-dependent shift
breaks it). No two targets are coupled, so no target sees another target's
unmeasured equator state. The role swap measures every coupler again from its
other end; J_ab = J_ba is the cross-check.

Circuit (cQASM 3.0, Tuna gate set): a target runs X90, wait(d), then X90
(quadrature X, P1 = (1 + cos phi)/2) or Y90 (quadrature Y,
P1 = (1 + sin phi)/2); a spectator runs X90 and wait(d + 1); a barrier
precedes the measurement of every qubit. OpenSquirrel schedules as late as
possible, so all X90 gates share one cycle and every spectator holds its Z
value through the whole idle. The rate comes from the two delays DELAYS
(20 ns cycles): nu = wrap(phi(d2) - phi(d1)) / (d2 - d1), so each sector's
fixed phase (preparation, the simultaneous X90 layer, readout rotation)
cancels, and |nu| / 2 pi < 1 / (2 (d2 - d1) 20 ns) = 333 kHz is unambiguous.

Per role assignment the configuration needs 2 quadratures x 2 delays = 4
circuits; with two readout-calibration circuits the case is 10 circuits,
submitted in batches of at most qi_platform.HARDWARE_BATCH_CIRCUITS, one batch
at a time, which keeps the account within the FAQ's three queued jobs per
hardware backend.

Analyses write every float at SIGNIFICANT digits: numpy builds linked to
different BLAS libraries disagree in the last ulp of solve and inv, and the
replays compare bytes.

--write DIR writes DIR/coupler_zz_tuna_17/ and the QX dry run DIR/coupler_zz_qx/
(batch-NN/ case directories and cases.json); --check DIR regenerates both and
compares bytes; --conformance schedules the emitted circuits
ALAP, evolves all 17 qubits under injected omega_q and every J_ab per cycle,
and requires the analysis to recover them; --analyze OUT RUN_DIR... analyzes
collected batches.

--analyze --replay compares OUT with its recomputation instead of writing it.
--explain-spectators OUT SPECTATOR_ANALYSIS ZZ_ANALYSIS splits each
spectator-drive phase shift of the crosstalk run into its coupler-ZZ part and
a drive-crosstalk residual (also with --replay).
--sanity RUN_DIR checks one collected batch (completion, readout errors,
spectator populations) before the next is submitted.

Usage: "$PYTHON" scripts/qi_coupler_zz_map.py
       (--write DIR | --check DIR | --conformance | --analyze OUT RUN_DIR... | --sanity RUN_DIR
        | --explain-spectators OUT SPECTATOR_ANALYSIS ZZ_ANALYSIS)
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
from qi_platform import HARDWARE_BATCH_CIRCUITS

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from parallel import ordered_map  # noqa: E402

CATALOGUE = ROOT / "docs/evidence/quantum_inspire/catalogue.json"
CYCLE_SECONDS = 20e-9
# The QX dry run keeps Tuna-17's coupling map restricted to qubits 0-9 (12
# couplers, still bipartite), since QX serves this account 10 qubits; QX has
# no residual coupling or detuning, so every rate it returns must vanish.
PROFILES: dict[str, dict[str, Any]] = {
    "tuna_17": {"identifier": "tuna_17", "qubits": 17, "shots": 16384, "directory": "coupler_zz_tuna_17"},
    "qx": {"identifier": "QXsinglenodesimulator", "qubits": 10, "shots": 2048, "directory": "coupler_zz_qx"},
}
DELAYS = (25, 100)
QUADRATURES = ("x", "y")
BATCH = HARDWARE_BATCH_CIRCUITS
SIGNIFICANT = 12
ROLES = ("P", "Q")
Table = dict[tuple[str, str, int, int, tuple[int, ...]], tuple[float, float]]


def backend_type(identifier: str) -> dict[str, Any]:
    catalogue = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    return next(b for b in catalogue["backend_types"] if b["identifier"] == identifier)


def edges(qubits: int) -> list[tuple[int, int]]:
    """Tuna-17's couplers among qubits 0 .. qubits - 1."""
    tuna = backend_type("tuna_17")
    return sorted({(min(e), max(e)) for e in tuna["topology"] if max(e) < qubits})


def neighbors(pairs: list[tuple[int, int]]) -> dict[int, list[int]]:
    out: dict[int, list[int]] = {}
    for a, b in pairs:
        out.setdefault(a, []).append(b)
        out.setdefault(b, []).append(a)
    return {q: sorted(v) for q, v in out.items()}


def parts(pairs: list[tuple[int, int]], nqubits: int) -> dict[str, list[int]]:
    """Two-coloring of the coupling graph from qubit 0; fails on an odd cycle."""
    adjacent = neighbors(pairs)
    color = {0: 0}
    stack = [0]
    while stack:
        q = stack.pop()
        for k in adjacent[q]:
            if k not in color:
                color[k] = 1 - color[q]
                stack.append(k)
            elif color[k] == color[q]:
                raise SystemExit(f"the coupling graph has an odd cycle through {q}-{k}")
    if len(color) != nqubits:
        raise SystemExit("the coupling graph is disconnected")
    return {"P": sorted(q for q in color if color[q] == 0), "Q": sorted(q for q in color if color[q] == 1)}


def header(nqubits: int) -> list[str]:
    return ["version 3.0", "", f"qubit[{nqubits}] q", f"bit[{nqubits}] b", ""]


def circuit_lines(nqubits: int, targets: list[int], quadrature: str, delay: int) -> list[str]:
    lines = header(nqubits)
    for q in range(nqubits):
        if q in targets:
            lines += [f"X90 q[{q}]", f"wait({delay}) q[{q}]", f"{'X90' if quadrature == 'x' else 'Y90'} q[{q}]"]
        else:
            lines += [f"X90 q[{q}]", f"wait({delay + 1}) q[{q}]"]
    return [*lines, "", "barrier q", "b = measure q", ""]


def readout_lines(nqubits: int, prepared: int) -> list[str]:
    flips = [f"X q[{q}]" for q in range(nqubits)] if prepared else []
    return [*header(nqubits), *flips, "", "barrier q", "b = measure q", ""]


def members(profile: str) -> tuple[dict[str, Any], list[tuple[str, str]]]:
    settings = PROFILES[profile]
    backend = backend_type(str(settings["identifier"]))
    n = int(settings["qubits"])
    if n > backend["nqubits"]:
        raise SystemExit(f"{profile} needs {n} qubits; the backend type serves {backend['nqubits']}")
    pairs = edges(n)
    split = parts(pairs, n)
    out = [("readout-0.cq", "\n".join(readout_lines(n, 0))), ("readout-1.cq", "\n".join(readout_lines(n, 1)))]
    for role, delay, quadrature in itertools.product(ROLES, DELAYS, QUADRATURES):
        name = f"targets-{role}-{quadrature}-d{delay:03d}.cq"
        out.append((name, "\n".join(circuit_lines(n, split[role], quadrature, delay))))
    meta = {"backend": backend, "nqubits": n, "pairs": pairs, "parts": split, "shots": int(settings["shots"])}
    return meta, out


def groups(ordered: list[tuple[str, str]]) -> list[list[tuple[str, str]]]:
    """Batches of at most BATCH circuits that keep each delay's x and y circuits together.

    atan2(y, x) combines the two quadratures as one simultaneous measurement,
    and a batch boundary is a calibration boundary; the readout circuits fill
    the remaining slots.
    """
    readouts = [item for item in ordered if item[0].startswith("readout")]
    pairs = [ordered[i : i + 2] for i in range(len(readouts), len(ordered), 2)]
    out = []
    for pair in pairs:
        batch = list(pair)
        while readouts and len(batch) < BATCH:
            batch.append(readouts.pop(0))
        out.append(batch)
    if readouts:
        out.append(readouts)
    return out


def build(profile: str) -> dict[str, str]:
    meta, ordered = members(profile)
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
            "schema": "qi-coupler-zz-cases-v1",
            "backend": meta["backend"]["identifier"],
            "backend_type_id": meta["backend"]["id"],
            "nqubits": meta["nqubits"],
            "shots": meta["shots"],
            "circuits": rows,
        }
        files[f"{directory}/cases.json"] = json.dumps(case, indent=1) + "\n"
        batches.append(directory)
    summary = {
        "schema": "qi-coupler-zz-map-v2",
        "backend": meta["backend"]["identifier"],
        "profile": profile,
        "edges": [list(e) for e in meta["pairs"]],
        "parts": meta["parts"],
        "delays_cycles": list(DELAYS),
        "cycle_seconds": CYCLE_SECONDS,
        "quadratures": list(QUADRATURES),
        "shots": meta["shots"],
        "batch_limit": BATCH,
        "circuits": len(ordered),
        "batches": batches,
    }
    files["cases.json"] = json.dumps(summary, indent=1) + "\n"
    return files


def bit(shot: str, qubit: int) -> int:
    return int(shot[len(shot) - 1 - qubit])


def retained_path(path: Path) -> str:
    """path relative to the repository root, so a retained record names no local directory."""
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        raise SystemExit(f"{path} lies outside the repository; retained analyses name repository paths") from None


def quantized(value: Any) -> Any:
    """value with every float rounded to SIGNIFICANT significant digits."""
    if isinstance(value, float):
        return float(f"{value:.{SIGNIFICANT}g}")
    if isinstance(value, dict):
        return {key: quantized(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [quantized(item) for item in value]
    return value


def wrap(angle: float) -> float:
    return (angle + math.pi) % (2 * math.pi) - math.pi


def fit_target(
    target: int, adjacent: list[int], table: Table, role: str, assignment: dict[int, tuple[float, float]]
) -> dict[str, Any]:
    """Sector rates of one target and the weighted fit nu(z) = omega + sum_k J_k s_k."""
    e01, e10 = assignment[target]
    rows = []
    for z in itertools.product((0, 1), repeat=len(adjacent)):
        phases = []
        for delay in DELAYS:
            expect = {}
            variance = {}
            for quadrature in QUADRATURES:
                ones, total = table.get((role, quadrature, delay, target, z), (0.0, 0.0))
                if total <= 0:
                    break
                p = ones / total
                expect[quadrature] = 2 * (p - e01) / (1 - e01 - e10) - 1
                variance[quadrature] = 4 * p * (1 - p) / total / (1 - e01 - e10) ** 2
            if len(expect) < 2:
                break
            x, y = expect["x"], expect["y"]
            r2 = x * x + y * y
            se2 = (y * y * variance["x"] + x * x * variance["y"]) / r2**2 if r2 > 0 else math.inf
            phases.append((math.atan2(y, x), se2, math.sqrt(r2)))
        if len(phases) < 2:
            continue
        span = DELAYS[1] - DELAYS[0]
        nu = wrap(phases[1][0] - phases[0][0]) / span
        se = math.sqrt(phases[0][1] + phases[1][1]) / span
        rows.append((z, nu, se, phases[0][2], phases[1][2]))
    # Each sector rate is known modulo 2 pi / span (666.7 kHz). The additive
    # model is invariant under a common shift by that period, so every sector
    # takes the branch nearest the circular mean of all sectors; J then reads
    # differences on one branch, and omega carries the common alias.
    span = DELAYS[1] - DELAYS[0]
    centre = math.atan2(sum(math.sin(r[1] * span) for r in rows), sum(math.cos(r[1] * span) for r in rows)) / span
    rows = [(z, centre + wrap((nu - centre) * span) / span, se, v1, v2) for z, nu, se, v1, v2 in rows]
    design = np.array([[1.0, *(1.0 if zk == 0 else -1.0 for zk in z)] for z, *_ in rows])
    # An exact (zero-variance) sector gets a large finite weight, so the conformance's exact data stay solvable.
    weights = np.array([1 / max(se, 1e-12) ** 2 for _, _, se, *_ in rows])
    rates = np.array([r[1] for r in rows])
    normal = design.T @ (weights[:, None] * design)
    coefficients = np.linalg.solve(normal, design.T @ (weights * rates))
    covariance = np.linalg.inv(normal)
    residual = rates - design @ coefficients
    to_hz = 1 / (2 * math.pi * CYCLE_SECONDS)
    return {
        "target": target,
        "role": role,
        "neighbors": adjacent,
        "omega_hz": float(coefficients[0]) * to_hz,
        "omega_se_hz": math.sqrt(covariance[0, 0]) * to_hz,
        "j_hz": {str(k): float(coefficients[i + 1]) * to_hz for i, k in enumerate(adjacent)},
        "j_se_hz": {str(k): math.sqrt(covariance[i + 1, i + 1]) * to_hz for i, k in enumerate(adjacent)},
        "sectors": len(rows),
        "additivity_chi2": float(np.sum(weights * residual**2)),
        "additivity_dof": len(rows) - len(adjacent) - 1,
        "min_visibility": min(min(r[3], r[4]) for r in rows),
    }


# End-quality rule, fixed after the Tuna-17 data: a target whose Ramsey
# visibility falls below MIN_VISIBILITY at some sector and delay, or whose
# pairwise-additive fit fails at p < MIN_ADDITIVITY_P, yields phases the
# delta-method error does not describe, so its ends are reported and excluded
# from the combined J.
MIN_VISIBILITY = 0.3
MIN_ADDITIVITY_P = 1e-3


def usable(target: dict[str, Any]) -> bool:
    from scipy.stats import chi2

    if target["min_visibility"] < MIN_VISIBILITY:
        return False
    dof = target["additivity_dof"]
    return dof <= 0 or float(chi2.sf(target["additivity_chi2"], dof)) >= MIN_ADDITIVITY_P


def analyze_table(meta: dict[str, Any], table: Table, assignment: dict[int, tuple[float, float]]) -> dict[str, Any]:
    adjacent = neighbors(meta["pairs"])
    targets = [fit_target(t, adjacent[t], table, role, assignment) for role in ROLES for t in meta["parts"][role]]
    for row in targets:
        row["usable"] = usable(row)
    edges_out = []
    for a, b in meta["pairs"]:
        ends = []
        for row in targets:
            other = b if row["target"] == a else a if row["target"] == b else None
            if other is not None:
                ends.append((row["j_hz"][str(other)], row["j_se_hz"][str(other)], row["target"], row["usable"]))
        good = [end for end in ends if end[3]]
        weights = [1 / max(se, 1e-12) ** 2 for _, se, _, _ in good]
        both = len(good) == 2
        difference = good[0][0] - good[1][0] if both else None
        difference_se = math.hypot(good[0][1], good[1][1]) if both else None
        combined = sum(w * j for w, (j, _, _, _) in zip(weights, good, strict=True)) / sum(weights) if good else None
        edges_out.append(
            {
                "edge": [a, b],
                "j_hz": combined,
                "j_se_hz": math.sqrt(1 / sum(weights)) if good else None,
                "zz_shift_hz": 2 * combined if combined is not None else None,
                "usable_ends": len(good),
                "ends": {str(t): {"j_hz": j, "j_se_hz": se, "usable": ok} for j, se, t, ok in ends},
                "end_difference_hz": difference,
                "end_difference_z": difference / difference_se if difference is not None and difference_se else None,
            }
        )
    return {"targets": targets, "edges": edges_out}


def tabulate(meta: dict[str, Any], shots_by_circuit: dict[str, list[str]]) -> Table:
    adjacent = neighbors(meta["pairs"])
    table: Table = {}
    for role, quadrature, delay in itertools.product(ROLES, QUADRATURES, DELAYS):
        shots = shots_by_circuit[f"targets-{role}-{quadrature}-d{delay:03d}.cq"]
        for target in meta["parts"][role]:
            grouped: dict[tuple[int, ...], list[int]] = {}
            for shot in shots:
                key = tuple(bit(shot, k) for k in adjacent[target])
                grouped.setdefault(key, []).append(bit(shot, target))
            for key, values in grouped.items():
                table[(role, quadrature, delay, target, key)] = (float(sum(values)), float(len(values)))
    return table


def schedule(lines: list[str], nqubits: int) -> tuple[int, dict[int, list[tuple[int, str]]]]:
    """ALAP start cycle of every gate: one cycle per gate, n per wait(n), all programs ending together."""
    program: dict[int, list[tuple[str, int]]] = {q: [] for q in range(nqubits)}
    for line in lines:
        words = line.split()
        if not words or line.startswith(("version", "qubit", "bit", "barrier", "b =", "//")):
            continue
        target = int(words[-1][2:-1])
        program[target].append(("wait", int(words[0][5:-1])) if words[0].startswith("wait(") else (words[0], 1))
    total = max(sum(n for _, n in ops) for ops in program.values())
    timeline: dict[int, list[tuple[int, str]]] = {}
    for q, ops in program.items():
        start = total - sum(n for _, n in ops)
        for name, length in ops:
            if name != "wait":
                timeline.setdefault(start, []).append((q, name))
            start += length
    return total, timeline


def exact_probabilities(lines: list[str], nqubits: int, omega: Any, coupling: dict[tuple[int, int], float]) -> Any:
    """Exact outcome probabilities over all 2^n strings under the injected diagonal Hamiltonian, per 20 ns cycle."""
    total, timeline = schedule(lines, nqubits)
    index = np.arange(1 << nqubits)
    z = 1 - 2 * ((index[:, None] >> np.arange(nqubits)) & 1)
    energy = (z @ omega) / 2
    for (a, b), j in coupling.items():
        energy = energy + j * z[:, a] * z[:, b] / 2
    step = np.exp(-1j * energy)
    gates = {
        "X": np.array([[0, -1j], [-1j, 0]]),
        "X90": np.array([[1, -1j], [-1j, 1]]) / math.sqrt(2),
        "Y90": np.array([[1, -1], [1, 1]], dtype=complex) / math.sqrt(2),
    }
    state = np.zeros(1 << nqubits, dtype=complex)
    state[0] = 1
    for cycle in range(total):
        for q, name in timeline.get(cycle, []):
            axis = nqubits - 1 - q
            tensor = np.tensordot(gates[name], state.reshape([2] * nqubits), axes=([1], [axis]))
            state = np.moveaxis(tensor, 0, axis).reshape(-1)
        state = step * state
    return np.abs(state) ** 2


class Evolution:
    """exact_probabilities with fixed parameters, picklable for the process pool."""

    def __init__(self, nqubits: int, omega: Any, coupling: dict[tuple[int, int], float]) -> None:
        self.nqubits, self.omega, self.coupling = nqubits, omega, coupling

    def __call__(self, lines: list[str]) -> Any:
        return exact_probabilities(lines, self.nqubits, self.omega, self.coupling)


def conformance(profile: str) -> str:
    """Recover injected omega_q and every J_ab from exact probabilities of the emitted circuits."""
    meta, ordered = members(profile)
    n = meta["nqubits"]
    rng = random.Random(11)
    scale = 2 * math.pi * CYCLE_SECONDS
    omega = np.array([scale * rng.uniform(-60e3, 60e3) for _ in range(n)])
    coupling = {e: scale * rng.uniform(-60e3, 60e3) for e in meta["pairs"]}
    # One target sits near the 333 kHz alias edge, so its sector rates straddle
    # it and the joint branch choice is exercised; its omega is compared
    # modulo the 666.7 kHz period.
    omega[meta["parts"]["P"][0]] = scale * 320e3
    period_hz = 1 / ((DELAYS[1] - DELAYS[0]) * CYCLE_SECONDS)
    adjacent = neighbors(meta["pairs"])
    texts = dict(ordered)
    index = np.arange(1 << n)
    table: Table = {}
    settings = list(itertools.product(ROLES, QUADRATURES, DELAYS))
    programs = [
        texts[f"targets-{role}-{quadrature}-d{delay:03d}.cq"].splitlines() for role, quadrature, delay in settings
    ]
    evolved = ordered_map(Evolution(n, omega, coupling), programs)
    for (role, quadrature, delay), probabilities in zip(settings, evolved, strict=True):
        for target in meta["parts"][role]:
            one = ((index >> target) & 1) == 1
            for key in itertools.product((0, 1), repeat=len(adjacent[target])):
                mask = np.ones(len(index), dtype=bool)
                for k, value in zip(adjacent[target], key, strict=True):
                    mask &= ((index >> k) & 1) == value
                table[(role, quadrature, delay, target, key)] = (
                    float(probabilities[mask & one].sum()) * 1e12,
                    float(probabilities[mask].sum()) * 1e12,
                )
    report = analyze_table(meta, table, {q: (0.0, 0.0) for q in range(n)})
    to_hz = 1 / (2 * math.pi * CYCLE_SECONDS)
    worst = 0.0
    if not all(row["usable"] for row in report["targets"]):
        raise SystemExit("conformance: an exact target fails the end-quality rule")
    for row in report["edges"]:
        for end in row["ends"].values():
            worst = max(worst, abs(end["j_hz"] - coupling[(row["edge"][0], row["edge"][1])] * to_hz))
    for row in report["targets"]:
        offset = row["omega_hz"] - float(omega[row["target"]]) * to_hz
        worst = max(worst, abs(offset - period_hz * round(offset / period_hz)))
    if worst > 1.0:
        raise SystemExit(f"conformance: recovered rates differ from the injected ones by {worst:.3g} Hz")
    couplers = len(report["edges"])
    return f"conformance {profile}: {couplers} couplers from both ends and {n} frequencies within {worst:.2g} Hz"


SANITY_READOUT_ERROR = 0.2
SANITY_SPECTATOR = (0.3, 0.7)


def sanity(run: Path) -> list[str]:
    """Checks one collected batch must pass before the next batch is submitted.

    Every job completed with its requested shots; in a readout circuit every
    qubit's assignment error stays below SANITY_READOUT_ERROR; in a Ramsey
    circuit every spectator, prepared in |+>, reads 1 with a probability inside
    SANITY_SPECTATOR. A failure stops the series before it spends more device
    time.
    """
    case = json.loads((run / "cases.json").read_text(encoding="utf-8"))
    collected = json.loads((run / "results.json").read_text(encoding="utf-8"))
    problems = []
    for row in collected["jobs"]:
        done = sum(r["shots_done"] for r in row["results"])
        if row["job"]["status"] != "completed" or done != case["shots"]:
            problems.append(f"{row['file']}: {row['job']['status']}, {done} of {case['shots']} shots")
    backend = case["backend"]
    profile = next(name for name, settings in PROFILES.items() if settings["identifier"] == backend)
    meta, _ = members(profile)
    for row in case["circuits"]:
        path = run / "raw" / f"{row['file']}.json"
        if not path.exists():
            problems.append(f"{row['file']}: raw shots missing")
            continue
        shots = json.loads(path.read_text(encoding="utf-8"))
        ones = [sum(bit(s, q) for s in shots) / len(shots) for q in range(meta["nqubits"])]
        if row["file"] in ("readout-0.cq", "readout-1.cq"):
            error = ones if row["file"] == "readout-0.cq" else [1 - p for p in ones]
            problems += [f"{row['file']} q{q}: error {e:.3f}" for q, e in enumerate(error) if e > SANITY_READOUT_ERROR]
        else:
            role = row["file"].split("-")[1]
            spectators = meta["parts"]["Q" if role == "P" else "P"]
            low, high = SANITY_SPECTATOR
            problems += [
                f"{row['file']} spectator q{q}: P1 {ones[q]:.3f}" for q in spectators if not low <= ones[q] <= high
            ]
    return problems


SPECTATOR_WINDOW_SECONDS = 40 * CYCLE_SECONDS
DRIVER_EXCITED_FRACTION = 0.5


def explain_spectators(spectator: dict[str, Any], zz: dict[str, Any]) -> dict[str, Any]:
    """Split each spectator-drive phase shift into the coupler-ZZ part this map predicts and a residual.

    A driver toggled by DRIVE_PULSES X gates through the 800 ns window
    spends DRIVER_EXCITED_FRACTION of it excited, so a coupler J moves the
    target's accumulated Rz phase by -2 (2 pi J) f t relative to the idle
    driver; whatever the measured single-driver shift exceeds that by is drive
    crosstalk (a.c.-Stark or pulse leakage), which this map does not contain.
    Inference, fixed after both data sets.
    """
    couplings = {tuple(sorted(e["edge"])): e for e in zz["edges"]}
    rows = []
    for star in spectator["additivity"]:
        for role in ("A", "B"):
            driver = star[role]
            edge = couplings[tuple(sorted((star["T"], driver)))]
            if edge["j_hz"] is None:
                continue
            predicted = -2 * 2 * math.pi * edge["j_hz"] * DRIVER_EXCITED_FRACTION * SPECTATOR_WINDOW_SECONDS
            predicted_se = 2 * 2 * math.pi * edge["j_se_hz"] * DRIVER_EXCITED_FRACTION * SPECTATOR_WINDOW_SECONDS
            measured = star["phase_shift_rad"][role]
            rows.append(
                {
                    "target": star["T"],
                    "driver": driver,
                    "j_hz": edge["j_hz"],
                    "measured_shift_rad": measured,
                    "zz_predicted_shift_rad": predicted,
                    "zz_predicted_se_rad": predicted_se,
                    "residual_rad": measured - predicted,
                }
            )
    return {"schema": "qi-spectator-zz-split-v1", "claim_kind": "inference, fixed after both data sets", "pairs": rows}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--conformance", action="store_true")
    mode.add_argument("--analyze", type=Path, nargs="+", metavar=("OUT", "RUN_DIR"))
    mode.add_argument("--sanity", type=Path, metavar="RUN_DIR")
    mode.add_argument("--explain-spectators", type=Path, nargs=3, metavar=("OUT", "SPECTATOR_ANALYSIS", "ZZ_ANALYSIS"))
    parser.add_argument("--replay", action="store_true", help="with --analyze: compare OUT with the recomputation")
    args = parser.parse_args()
    if args.explain_spectators:
        out, spectator_path, zz_path = args.explain_spectators
        split = explain_spectators(
            json.loads(spectator_path.read_text(encoding="utf-8")), json.loads(zz_path.read_text(encoding="utf-8"))
        )
        text = json.dumps(quantized(split), indent=1) + "\n"
        if args.replay:
            if out.read_text(encoding="utf-8") != text:
                raise SystemExit(f"{out} differs from its recomputation")
            print(f"{out}: {len(split['pairs'])} driver-target pairs reproduce")
            return 0
        out.write_text(text, encoding="utf-8")
        print(f"{len(split['pairs'])} driver-target pairs -> {out}")
        return 0
    if args.sanity:
        problems = sanity(args.sanity)
        for problem in problems:
            print(problem)
        print(f"sanity {args.sanity.name}: {'FAIL' if problems else 'pass'}")
        return 1 if problems else 0
    if args.conformance:
        for profile in PROFILES:
            print(conformance(profile))
        return 0
    if args.analyze:
        out, *runs = args.analyze
        backend = json.loads((runs[0] / "cases.json").read_text(encoding="utf-8"))["backend"]
        profile = next(name for name, settings in PROFILES.items() if settings["identifier"] == backend)
        meta, _ = members(profile)
        shots: dict[str, list[str]] = {}
        batch_of: dict[str, int] = {}
        for index, run in enumerate(runs):
            for row in json.loads((run / "cases.json").read_text(encoding="utf-8"))["circuits"]:
                if row["file"] in shots:
                    raise SystemExit(f"{run}: {row['file']} appears in more than one listed batch")
                shots[row["file"]] = json.loads((run / "raw" / f"{row['file']}.json").read_text(encoding="utf-8"))
                batch_of[row["file"]] = index
        # atan2 treats a delay's x and y circuits as one measurement; a pair
        # split across batches carries any calibration change between them.
        split_pairs = [
            f"{role}-d{delay:03d}"
            for role, delay in itertools.product(ROLES, DELAYS)
            if len({batch_of[f"targets-{role}-{q}-d{delay:03d}.cq"] for q in QUADRATURES}) > 1
        ]
        zero, one = shots["readout-0.cq"], shots["readout-1.cq"]
        assignment = {
            q: (sum(bit(s, q) for s in zero) / len(zero), sum(1 - bit(s, q) for s in one) / len(one))
            for q in range(meta["nqubits"])
        }
        report = {
            "schema": "qi-coupler-zz-analysis-v1",
            "profile": profile,
            "runs": [retained_path(r) for r in runs],
            "quadrature_pairs_across_batches": split_pairs,
            "readout_assignment": {str(q): list(v) for q, v in assignment.items()},
            **analyze_table(meta, tabulate(meta, shots), assignment),
        }
        text = json.dumps(quantized(report), indent=1) + "\n"
        if args.replay:
            if out.read_text(encoding="utf-8") != text:
                raise SystemExit(f"{out} differs from its recomputation")
            print(f"{out}: {len(report['edges'])} couplers reproduce")
            return 0
        out.write_text(text, encoding="utf-8")
        print(f"{len(report['edges'])} couplers -> {out}")
        return 0
    count = 0
    for profile, settings in PROFILES.items():
        for name, text in build(profile).items():
            path = (args.write or args.check) / str(settings["directory"]) / name
            if args.write:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8")
            elif path.read_text(encoding="utf-8") != text:
                raise SystemExit(f"{path} differs from its regeneration")
            count += 1
    print(f"qi coupler zz map: {count} files {'written' if args.write else 'match their regeneration'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
