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
submitted in batches of at most BATCH = 3, one batch at a time, which keeps
the account within the FAQ's three queued jobs per hardware backend.

--write DIR writes DIR/batch-NN/ case directories and cases.json; --check DIR
regenerates and compares bytes; --conformance schedules the emitted circuits
ALAP, evolves all 17 qubits under injected omega_q and every J_ab per cycle,
and requires the analysis to recover them; --analyze OUT RUN_DIR... analyzes
collected batches.

Usage: "$PYTHON" scripts/qi_coupler_zz_map.py (--write DIR | --check DIR | --conformance | --analyze OUT RUN_DIR...)
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

ROOT = Path(__file__).resolve().parents[1]
CATALOGUE = ROOT / "docs/evidence/quantum_inspire/catalogue.json"
BACKEND = "tuna_17"
CYCLE_SECONDS = 20e-9
DELAYS = (25, 100)
QUADRATURES = ("x", "y")
SHOTS = 16384
BATCH = 3
ROLES = ("P", "Q")
Table = dict[tuple[str, str, int, int, tuple[int, ...]], tuple[float, float]]


def tuna17() -> dict[str, Any]:
    catalogue = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    return next(b for b in catalogue["backend_types"] if b["identifier"] == BACKEND)


def edges(backend: dict[str, Any]) -> list[tuple[int, int]]:
    return sorted({(min(e), max(e)) for e in backend["topology"]})


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


def members() -> tuple[dict[str, Any], list[tuple[str, str]]]:
    backend = tuna17()
    n = backend["nqubits"]
    pairs = edges(backend)
    split = parts(pairs, n)
    out = [("readout-0.cq", "\n".join(readout_lines(n, 0))), ("readout-1.cq", "\n".join(readout_lines(n, 1)))]
    for role, quadrature, delay in itertools.product(ROLES, QUADRATURES, DELAYS):
        name = f"targets-{role}-{quadrature}-d{delay:03d}.cq"
        out.append((name, "\n".join(circuit_lines(n, split[role], quadrature, delay))))
    meta = {"backend": backend, "nqubits": n, "pairs": pairs, "parts": split}
    return meta, out


def build() -> dict[str, str]:
    meta, ordered = members()
    files: dict[str, str] = {}
    batches = []
    for start in range(0, len(ordered), BATCH):
        directory = f"batch-{start // BATCH:02d}"
        rows = []
        for name, text in ordered[start : start + BATCH]:
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
            "backend": BACKEND,
            "backend_type_id": meta["backend"]["id"],
            "nqubits": meta["nqubits"],
            "shots": SHOTS,
            "circuits": rows,
        }
        files[f"{directory}/cases.json"] = json.dumps(case, indent=1) + "\n"
        batches.append(directory)
    summary = {
        "schema": "qi-coupler-zz-map-v2",
        "backend": BACKEND,
        "edges": [list(e) for e in meta["pairs"]],
        "parts": meta["parts"],
        "delays_cycles": list(DELAYS),
        "cycle_seconds": CYCLE_SECONDS,
        "quadratures": list(QUADRATURES),
        "shots": SHOTS,
        "batch_limit": BATCH,
        "circuits": len(ordered),
        "batches": batches,
    }
    files["cases.json"] = json.dumps(summary, indent=1) + "\n"
    return files


def bit(shot: str, qubit: int) -> int:
    return int(shot[len(shot) - 1 - qubit])


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
    design = np.array([[1.0, *(1.0 if zk == 0 else -1.0 for zk in z)] for z, *_ in rows])
    # An exact (zero-variance) sector gets a large finite weight, so the conformance's exact data stay solvable.
    weights = np.array([1 / max(se, 1e-12) ** 2 for _, _, se, *_ in rows])
    nu = np.array([r[1] for r in rows])
    normal = design.T @ (weights[:, None] * design)
    coefficients = np.linalg.solve(normal, design.T @ (weights * nu))
    covariance = np.linalg.inv(normal)
    residual = nu - design @ coefficients
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


def analyze_table(meta: dict[str, Any], table: Table, assignment: dict[int, tuple[float, float]]) -> dict[str, Any]:
    adjacent = neighbors(meta["pairs"])
    targets = [fit_target(t, adjacent[t], table, role, assignment) for role in ROLES for t in meta["parts"][role]]
    edges_out = []
    for a, b in meta["pairs"]:
        ends = []
        for row in targets:
            other = b if row["target"] == a else a if row["target"] == b else None
            if other is not None:
                ends.append((row["j_hz"][str(other)], row["j_se_hz"][str(other)], row["target"]))
        weights = [1 / max(se, 1e-12) ** 2 for _, se, _ in ends]
        combined = sum(w * j for w, (j, _, _) in zip(weights, ends, strict=True)) / sum(weights)
        difference = ends[0][0] - ends[1][0]
        difference_se = math.hypot(ends[0][1], ends[1][1])
        edges_out.append(
            {
                "edge": [a, b],
                "j_hz": combined,
                "j_se_hz": math.sqrt(1 / sum(weights)),
                "zz_shift_hz": 2 * combined,
                "ends": {str(t): {"j_hz": j, "j_se_hz": se} for j, se, t in ends},
                "end_difference_hz": difference,
                "end_difference_z": difference / difference_se if difference_se > 0 else None,
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


def conformance() -> str:
    """Recover injected omega_q and every J_ab from exact probabilities of the emitted circuits."""
    meta, ordered = members()
    n = meta["nqubits"]
    rng = random.Random(11)
    scale = 2 * math.pi * CYCLE_SECONDS
    omega = np.array([scale * rng.uniform(-60e3, 60e3) for _ in range(n)])
    coupling = {e: scale * rng.uniform(-60e3, 60e3) for e in meta["pairs"]}
    adjacent = neighbors(meta["pairs"])
    texts = dict(ordered)
    index = np.arange(1 << n)
    table: Table = {}
    for role, quadrature, delay in itertools.product(ROLES, QUADRATURES, DELAYS):
        lines = texts[f"targets-{role}-{quadrature}-d{delay:03d}.cq"].splitlines()
        probabilities = exact_probabilities(lines, n, omega, coupling)
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
    for row in report["edges"]:
        for end in row["ends"].values():
            worst = max(worst, abs(end["j_hz"] - coupling[(row["edge"][0], row["edge"][1])] * to_hz))
    for row in report["targets"]:
        worst = max(worst, abs(row["omega_hz"] - float(omega[row["target"]]) * to_hz))
    if worst > 1.0:
        raise SystemExit(f"conformance: recovered rates differ from the injected ones by {worst:.3g} Hz")
    return f"conformance: {len(report['edges'])} couplers from both ends and {n} frequencies within {worst:.2g} Hz"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--conformance", action="store_true")
    mode.add_argument("--analyze", type=Path, nargs="+", metavar=("OUT", "RUN_DIR"))
    args = parser.parse_args()
    if args.conformance:
        print(conformance())
        return 0
    if args.analyze:
        out, *runs = args.analyze
        meta, _ = members()
        shots: dict[str, list[str]] = {}
        for run in runs:
            for row in json.loads((run / "cases.json").read_text(encoding="utf-8"))["circuits"]:
                shots[row["file"]] = json.loads((run / "raw" / f"{row['file']}.json").read_text(encoding="utf-8"))
        zero, one = shots["readout-0.cq"], shots["readout-1.cq"]
        assignment = {
            q: (sum(bit(s, q) for s in zero) / len(zero), sum(1 - bit(s, q) for s in one) / len(one))
            for q in range(meta["nqubits"])
        }
        report = {
            "schema": "qi-coupler-zz-analysis-v1",
            "runs": [r.as_posix() for r in runs],
            "readout_assignment": {str(q): list(v) for q, v in assignment.items()},
            **analyze_table(meta, tabulate(meta, shots), assignment),
        }
        out.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
        print(f"{len(report['edges'])} couplers -> {out}")
        return 0
    files = build()
    for name, text in files.items():
        path = (args.write or args.check) / name
        if args.write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        elif path.read_text(encoding="utf-8") != text:
            raise SystemExit(f"{path} differs from its regeneration")
    print(f"qi coupler zz map: {len(files)} files {'written' if args.write else 'match their regeneration'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
