"""Design evidence of the Tuna-17 box-kite follow series, recomputed from retained records.

The follow series (scripts/box_kite_cases.py, FOLLOW_PLAN) rests on five
measured facts, each recomputed here from files the repository retains:

- timing: a least-squares fit of every completed Tuna-17 job's
  execution_time_in_seconds over its shots, CZ lines, one-qubit gate lines
  and wait cycles (results/quantum_inspire/runs/*/results.json against the
  circuit text beside it). The per-shot slope prices a shot; the fixed term
  prices a job.
- readout drift: e01 and e10 of every qubit in the pre-T0 batch and the
  three T0 batches, their spread over the T0 batches and a homogeneity
  chi-square per qubit. The spread on the LCU qubits sizes BRACKET_DRIFT_MAX.
- matchings: every induced matching of the admitted coupling graph (TUNA17
  without TUNA_EXCLUDED and TUNA_AVOIDED); the largest has three couplers and
  LCU_PAIRS is one of them, so no layout holds a fourth simultaneous pair.
- placement: every star walk (a control and three data neighbors in each data
  order) and path walk (a control and two) on the admitted graph that share
  no qubit or coupler, each scored by the coherent ZZ model below at a 60 ns
  and a 0.8 us CZ window; FOLLOW_WALK_LAYOUTS must be the pair whose worse
  score is best (ties to the lexicographically first placement).
- phase scale: the walk control's Bloch vector before its last H under the
  ZZ model, alone and with the targets' Ramsey detunings, at both CZ windows:
  the size of the phase the walk-y readout resolves. Detunings drift and each
  CZ adds its residual local phase, so it is a scale, not a prediction.

ZZ model: a pure state on the walk's qubits under H = sum over couplers
inside the walk of (2 pi zz_shift_hz / 4) Z_i Z_j (results/quantum_inspire/
coupler_zz_tuna_17_analysis.json), plus (2 pi omega_hz / 2) Z_q per qubit
when detuning is on; every one-qubit gate lasts 20 ns and every CZ the
window, and the phase accrues after each gate. Incoherent error is the
factor T0_R ** n_CZ, applied outside the model.

--write FILE writes the record; --check FILE recomputes it and compares
bytes; --self-test requires the model to reproduce analytic cases and each
selection rule to reject a mutated input.

Usage: "$PYTHON" scripts/box_kite_follow_design.py (--write FILE | --check FILE | --self-test)
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
import box_kite_cases as cases  # noqa: E402

import parallel  # noqa: E402

SCHEMA = "box-kite-follow-design-v1"
RUNS = ROOT / "results/quantum_inspire/runs"
ZZ_ANALYSIS = ROOT / "results/quantum_inspire/coupler_zz_tuna_17_analysis.json"
PRE_T0_RUNS = (
    "2026-10-17T152324Z-box_kite_tuna_pre-batch-00",
    "2026-10-17T152324Z-box_kite_tuna_t0-batch-00",
    "2026-10-17T152324Z-box_kite_tuna_t0-batch-01",
    "2026-10-17T152324Z-box_kite_tuna_t0-batch-02",
)
ONE_QUBIT_NS = 20e-9
CZ_WINDOWS = (60e-9, 8e-7)
SIGNIFICANT = 9
GATE = re.compile(r"(?m)^(H|X|Y|Z|S|Sdag|T|Tdag|X90|Y90|mX90|mY90|Rx|Ry|Rz)\b")
CZ_LINE = re.compile(r"(?m)^CZ ")
WAIT = re.compile(r"wait\((\d+)\)")


def sig(value: float) -> float:
    return float(f"{value:.{SIGNIFICANT}g}")


def tuna_jobs() -> list[tuple[int, float, int, int, int]]:
    """(shots, execution seconds, CZ lines, one-qubit gate lines, wait cycles) of every completed Tuna-17 job."""
    rows = []
    for results in sorted(RUNS.glob("*/results.json")):
        run = results.parent
        manifest = json.loads((run / "cases.json").read_text(encoding="utf-8"))
        if manifest.get("backend") != cases.TUNA_IDENTIFIER:
            continue
        for job in json.loads(results.read_text(encoding="utf-8"))["jobs"]:
            if job["job"]["status"] != "completed" or not job.get("results"):
                continue
            text = (run / job["file"]).read_text(encoding="utf-8")
            result = job["results"][0]
            rows.append(
                (
                    result["shots_done"],
                    result["execution_time_in_seconds"],
                    len(CZ_LINE.findall(text)),
                    len(GATE.findall(text)),
                    sum(int(n) for n in WAIT.findall(text)),
                )
            )
    return rows


def timing_fit(rows: list[tuple[int, float, int, int, int]]) -> dict[str, Any]:
    """Ordinary least squares t = c0 + n (c1 + c2 n_CZ + c3 n_1q + c4 wait_s) with standard errors."""
    data = np.array(rows, dtype=float)
    shots, seconds = data[:, 0], data[:, 1]
    design = np.column_stack(
        [np.ones_like(shots), shots, shots * data[:, 2], shots * data[:, 3], shots * data[:, 4] * 2e-8]
    )
    coef, *_ = np.linalg.lstsq(design, seconds, rcond=None)
    residual = seconds - design @ coef
    dof = len(seconds) - design.shape[1]
    cov = (residual @ residual / dof) * np.linalg.inv(design.T @ design)
    names = ("fixed_s", "per_shot_s", "per_shot_per_cz_s", "per_shot_per_one_qubit_s", "wait_time_ratio")
    return {
        "jobs": len(rows),
        "shots": sorted({int(s) for s in shots}),
        "coefficients": {
            n: {"value": sig(c), "se": sig(math.sqrt(v))} for n, c, v in zip(names, coef, np.diag(cov), strict=True)
        },
        "residual_sd_s": sig(float(residual.std())),
    }


def readout_drift() -> dict[str, Any]:
    """Per-qubit e01 and e10 of the pre-T0 and T0 batches, with the T0 spread and homogeneity chi-square."""
    batches: dict[str, dict[str, list[float]]] = {}
    for name in PRE_T0_RUNS:
        run = RUNS / name
        errors: dict[str, list[float]] = {}
        for prepared, key in ((0, "e01"), (1, "e10")):
            raw = json.loads((run / "raw" / f"readout-{prepared}.cq.json").read_text(encoding="utf-8"))
            ones = np.array([[s[-1 - q] == "1" for q in range(cases.TUNA_QUBITS)] for s in raw]).mean(axis=0)
            errors[key] = [sig(float(v if prepared == 0 else 1 - v)) for v in ones]
            errors[f"n_{key}"] = [float(len(raw))]
        batches[name] = errors
    t0 = [batches[name] for name in PRE_T0_RUNS[1:]]
    used = sorted(q for pair in cases.LCU_PAIRS for q in pair)
    per_qubit: dict[str, dict[str, dict[str, Any]]] = {}
    for q in range(cases.TUNA_QUBITS):
        row: dict[str, dict[str, Any]] = {}
        for key in ("e01", "e10"):
            values = np.array([b[key][q] for b in t0])
            n = np.array([b[f"n_{key}"][0] for b in t0])
            var = np.maximum(values * (1 - values) / n, 1e-12)
            mean = float((values / var).sum() / (1 / var).sum())
            row[key] = {
                "batches": [b[key][q] for b in [batches[name] for name in PRE_T0_RUNS]],
                "t0_spread": sig(float(values.max() - values.min())),
                "t0_chi2": sig(float(((values - mean) ** 2 / var).sum())),
            }
        per_qubit[str(q)] = row
    worst = max(float(per_qubit[str(q)][k]["t0_spread"]) for q in used for k in ("e01", "e10"))
    if worst >= cases.BRACKET_DRIFT_MAX:
        raise SystemExit(f"T0 readout spread {worst} on the LCU qubits reaches BRACKET_DRIFT_MAX")
    return {"runs": list(PRE_T0_RUNS), "used_qubits": used, "max_t0_spread_used": worst, "qubits": per_qubit}


def admitted_graph() -> tuple[list[int], dict[int, set[int]]]:
    out = set(cases.TUNA_EXCLUDED) | set(cases.TUNA_AVOIDED)
    nodes = [q for q in range(cases.TUNA_QUBITS) if q not in out]
    adj: dict[int, set[int]] = {q: set() for q in nodes}
    for a, b in cases.TUNA17:
        if a in adj and b in adj:
            adj[a].add(b)
            adj[b].add(a)
    return nodes, adj


def separated(groups: list[tuple[int, ...]], adj: dict[int, set[int]]) -> bool:
    """No qubit in two groups and no coupler between two groups."""
    for a, b in itertools.combinations(groups, 2):
        if set(a) & set(b) or any(y in adj[x] for x in a for y in b):
            return False
    return True


def matchings(adj: dict[int, set[int]]) -> dict[str, Any]:
    edges = sorted((a, b) for a in adj for b in adj[a] if a < b)
    best: list[tuple[tuple[int, int], ...]] = []
    for size in range(1, len(edges) + 1):
        found = [m for m in itertools.combinations(edges, size) if separated(list(m), adj)]
        if not found:
            break
        best = found
    if tuple(sorted(cases.LCU_PAIRS)) not in {tuple(sorted(m)) for m in best}:
        raise SystemExit("LCU_PAIRS is not a maximum induced matching of the admitted graph")
    return {"admitted_couplers": len(edges), "maximum_size": len(best[0]), "maximum_count": len(best)}


def zz_terms(place: list[int], zz: dict[tuple[int, int], float], detuning: dict[int, float] | None) -> np.ndarray:
    """Diagonal of the model Hamiltonian in rad/s on the computational basis of `place` (qubit 0 least significant)."""
    bits = (np.arange(2 ** len(place))[:, None] >> np.arange(len(place))) & 1
    signs = 1 - 2 * bits
    energy = np.zeros(2 ** len(place))
    for (a, b), shift in zz.items():
        if a in place and b in place:
            energy += 2 * math.pi * shift / 4 * signs[:, place.index(a)] * signs[:, place.index(b)]
    for q, omega in (detuning or {}).items():
        if q in place:
            energy += 2 * math.pi * omega / 2 * signs[:, place.index(q)]
    return energy


Ops = tuple[tuple[str, tuple[int, ...]], ...]


def walk_ops(triple: tuple[int, int, int]) -> Ops:
    """The lowered walk's gates up to its last H, as (name, logical qubits) with the control on qubit 0."""
    exemplar = cases.walk_exemplar(cases.load_census(), triple)
    circuit = cases.lower_for_tuna(
        cases.associator_walk(exemplar["i"], exemplar["j"], exemplar["k"], exemplar["omega"], exemplar["bits"])
    )
    return tuple(
        (inst.operation.name, tuple(circuit.find_bit(q).index for q in inst.qubits)) for inst in circuit.data[:-1]
    )


def walk_bloch(ops: Ops, place: list[int], window: float, energy: np.ndarray) -> tuple[float, float]:
    """<X_c> and <Y_c> of the walk control before its last H under the ZZ model."""
    n = len(place)
    psi = np.zeros(2**n, dtype=complex)
    psi[0] = 1
    index = np.arange(2**n)
    hadamard = np.array([[1, 1], [1, -1]]) / math.sqrt(2)
    for name, qubits in ops:
        if name == "cz":
            both = ((index >> qubits[0]) & 1) & ((index >> qubits[1]) & 1)
            psi = np.where(both == 1, -psi, psi)
            duration = window
        else:
            q = qubits[0]
            tensor = np.moveaxis(psi.reshape([2] * n), n - 1 - q, 0)
            gate = {"h": hadamard, "x": np.array([[0, 1], [1, 0]]), "z": np.diag([1, -1])}[name]
            psi = np.moveaxis(np.tensordot(gate, tensor, axes=1), 0, n - 1 - q).reshape(-1)
            duration = ONE_QUBIT_NS
        psi = np.exp(-1j * energy * duration) * psi
    coherence = complex(np.vdot(psi[index & 1 == 0], psi[index & 1 == 1]))
    return 2 * coherence.real, 2 * coherence.imag


def placement_score(item: tuple[Ops, list[int], dict[tuple[int, int], float]]) -> float:
    """The ZZ-only |<X_c>| of one walk placement, the worse of the two CZ windows."""
    ops, place, zz = item
    energy = zz_terms(place, zz, None)
    return min(abs(walk_bloch(ops, place, w, energy)[0]) for w in CZ_WINDOWS)


Pair = tuple[float, float, float, tuple[int, ...], tuple[int, ...]]


def best_pair(pairs: list[Pair]) -> Pair:
    """The (worse, star, path, star placement, path placement) row with the best worse score.

    Ties go to the better star score, then the better path score, then the lexicographically first placement.
    """
    return max(pairs, key=lambda row: (row[0], row[1], row[2], [-q for q in row[3] + row[4]]))


def placement(adj: dict[int, set[int]], zz: dict[tuple[int, int], float]) -> dict[str, Any]:
    """The separated star and path placements, scored by the ZZ-only |<X_c>| at both windows."""
    star_ops, path_ops = (walk_ops(triple) for triple, _ in cases.FOLLOW_WALKS)

    def walks(data_count: int) -> list[tuple[int, ...]]:
        return [(c, *d) for c in sorted(adj) for d in itertools.permutations(sorted(adj[c]), data_count)]

    star_walks, path_walks = walks(3), walks(2)
    scores = parallel.ordered_map(
        placement_score, [(star_ops, list(p), zz) for p in star_walks] + [(path_ops, list(p), zz) for p in path_walks]
    )
    stars = dict(zip(star_walks, scores[: len(star_walks)], strict=True))
    paths = dict(zip(path_walks, scores[len(star_walks) :], strict=True))
    pairs = [
        (min(stars[s], paths[p]), stars[s], paths[p], s, p) for s in stars for p in paths if separated([s, p], adj)
    ]
    if not pairs:
        raise SystemExit("no star and path walk fit on the admitted graph without a shared qubit or coupler")
    best = best_pair(pairs)
    chosen = {
        "star_14": [best[3][0], list(best[3][1:])],
        "path_4": [best[4][0], list(best[4][1:])],
    }
    declared = {name: [c, list(d)] for name, (c, d) in cases.FOLLOW_WALK_LAYOUTS.items()}
    if chosen != declared:
        raise SystemExit(f"FOLLOW_WALK_LAYOUTS {declared} differs from the scored choice {chosen}")
    return {
        "separated_combinations": len(pairs),
        "chosen": chosen,
        "star_scores": {" ".join(map(str, s)): sig(v) for s, v in sorted(stars.items()) if s[0] == best[3][0]},
        "path_scores": {" ".join(map(str, p)): sig(v) for p, v in sorted(paths.items()) if p[0] == best[4][0]},
    }


def phase_predictions(zz: dict[tuple[int, int], float], detuning: dict[int, float]) -> dict[str, Any]:
    out = {}
    for triple, layout in cases.FOLLOW_WALKS:
        control, data = cases.FOLLOW_WALK_LAYOUTS[layout]
        place = [control, *data]
        rows = {}
        for window in CZ_WINDOWS:
            for model, det in (("zz", None), ("zz_detuning", detuning)):
                x, y = walk_bloch(walk_ops(triple), place, window, zz_terms(place, zz, det))
                rows[f"{model}_{window * 1e9:g}ns"] = {
                    "x": sig(x),
                    "y": sig(y),
                    "phase_deg_from_omega": sig(math.degrees(math.atan2(y, -x))),
                }
        cz = cases.walk_exemplar(cases.load_census(), triple)["cnots"]
        out[layout] = {"cz": cz, "incoherent_factor": sig(cases.T0_R**cz), "models": rows}
    return out


def budget(fit: dict[str, Any]) -> dict[str, Any]:
    """Witnesses, replicas and the fitted execution seconds of the follow series at its shot count."""
    c = {k: v["value"] for k, v in fit["coefficients"].items()}
    files = cases.tuna_series()["box_kite_tuna_follow"]
    jobs = witnesses = replicas = 0
    seconds = 0.0
    for key, text in sorted(files.items()):
        if not key.endswith(".cq"):
            continue
        jobs += 1
        n = cases.FOLLOW_SHOTS
        seconds += c["fixed_s"] + n * (
            c["per_shot_s"]
            + c["per_shot_per_cz_s"] * len(CZ_LINE.findall(text))
            + c["per_shot_per_one_qubit_s"] * len(GATE.findall(text))
        )
    for key, text in files.items():
        if key.endswith("/cases.json"):
            for row in json.loads(text)["circuits"]:
                if row["kind"] == "witness":
                    witnesses += 1
                    replicas += len(row["replicas"])
    return {
        "batches": len(cases.FOLLOW_PLAN),
        "jobs": jobs,
        "witness_circuits": witnesses,
        "replicas": replicas,
        "shots_per_job": cases.FOLLOW_SHOTS,
        "fitted_execution_s": sig(seconds),
    }


def record() -> dict[str, Any]:
    analysis = json.loads(ZZ_ANALYSIS.read_text(encoding="utf-8"))
    zz = {(e["edge"][0], e["edge"][1]): e["zz_shift_hz"] for e in analysis["edges"]}
    detuning = {t["target"]: t["omega_hz"] for t in analysis["targets"]}
    nodes, adj = admitted_graph()
    fit = timing_fit(tuna_jobs())
    return {
        "schema": SCHEMA,
        "admitted_qubits": nodes,
        "timing": fit,
        "readout_drift": readout_drift(),
        "matchings": matchings(adj),
        "placement": placement(adj, zz),
        "phase_predictions": phase_predictions(zz, detuning),
        "budget": budget(fit),
    }


def dump(value: dict[str, Any]) -> str:
    return json.dumps(value, indent=1, sort_keys=True) + "\n"


def self_test() -> str:
    """Analytic model cases and mutated selection inputs."""
    nodes, adj = admitted_graph()
    triple = cases.FOLLOW_WALKS[0][0]
    place = [cases.FOLLOW_WALK_LAYOUTS["star_14"][0], *cases.FOLLOW_WALK_LAYOUTS["star_14"][1]]
    ops = walk_ops(triple)
    x, y = walk_bloch(ops, place, 6e-8, np.zeros(16))
    if abs(x + 1) > 1e-12 or abs(y) > 1e-12:
        raise AssertionError(f"the noiseless walk reads ({x}, {y}), not (omega, 0) = (-1, 0)")
    # A detuning on the control alone turns its Bloch vector by 2 pi omega T, T the time from its first H.
    omega = 1e5
    circuit = cases.lower_for_tuna(cases.associator_walk(2, 11, 3, -1, [0, 1, 3]))
    x, y = walk_bloch(ops, place, 6e-8, zz_terms(place, {}, {place[0]: omega}))
    phase = math.atan2(y, -x)
    first_h = next(
        n
        for n, inst in enumerate(circuit.data)
        if inst.operation.name == "h" and circuit.find_bit(inst.qubits[0]).index == 0
    )
    accrued = sum((6e-8 if inst.operation.name == "cz" else ONE_QUBIT_NS) for inst in circuit.data[first_h:-1])
    if abs(abs(phase) - 2 * math.pi * omega * accrued) > 1e-9:
        raise AssertionError(
            f"a control detuning gives phase {phase}, not 2 pi omega T = {2 * math.pi * omega * accrued}"
        )
    rejected = 0
    saved = cases.FOLLOW_WALK_LAYOUTS
    try:
        cases.FOLLOW_WALK_LAYOUTS = {"star_14": (11, (8, 13, 14)), "path_4": saved["path_4"]}
        try:
            placement(adj, {})
        except SystemExit:
            rejected += 1
    finally:
        cases.FOLLOW_WALK_LAYOUTS = saved
    saved_pairs = cases.LCU_PAIRS
    try:
        cases.LCU_PAIRS = ((1, 4), (10, 13), (11, 14))
        try:
            matchings(adj)
        except SystemExit:
            rejected += 1
    finally:
        cases.LCU_PAIRS = saved_pairs
    if rejected != 2:
        raise AssertionError(f"{2 - rejected} mutated selection inputs were accepted")
    # A strong star beside a weak path loses to a pair whose worse score is higher.
    lopsided: Pair = (0.5, 0.99, 0.5, (14, 11, 12, 16), (4, 1, 2))
    balanced: Pair = (0.9, 0.95, 0.9, (14, 12, 11, 16), (4, 2, 1))
    if best_pair([lopsided, balanced]) != balanced:
        raise AssertionError("placement selection ranks a pair above one with a better worse score")
    if not separated([(1, 4), (10, 13)], adj) or separated([(1, 4), (2, 8)], adj):
        raise AssertionError("separated() misreads a shared coupler")
    if cases.TUNA_EXCLUDED[0] in nodes:
        raise AssertionError("an excluded qubit entered the admitted graph")
    return "box-kite follow design: noiseless walk, control-detuning phase, selection mutations and maximin rule pass"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
        return 0
    text = dump(record())
    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(text, encoding="utf-8")
        print(f"box-kite follow design -> {args.write}")
        return 0
    if args.check.read_text(encoding="utf-8") != text:
        raise SystemExit(f"{args.check} differs from its recomputation")
    print(f"{args.check}: matches its recomputation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
