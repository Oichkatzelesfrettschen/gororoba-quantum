"""Replay the Quantum Inspire spectator-drive and teleportation circuits under the retained IBM Kingston noise model.

The cases of scripts/qi_crosstalk_teleport_cases.py ran on a transmon chip
whose coupler and drive crosstalk the experiment probes. The Kingston noise
model of calibration_snapshot.noise_simulator holds an independent depolarizing
and thermal-relaxation channel per gate and an independent readout channel per
qubit, so a circuit's reduced state on a qubit set evolves independently of
every qubit outside it. The replay therefore simulates each star (T, A, B) and
each teleport path (I, P1, P2, D) as its own density matrix on a chosen
Kingston embedding, and a star's target phase shift and additivity residual
have the exact value zero under this model; any nonzero exact shift is a
property of the replay, not of the device.

What the replay does:

- The retained cQASM files are parsed (X90, Y90, X, H, S, Sdag, CNOT, SWAP,
  wait) and the gates on one group's qubits become a Qiskit circuit: X90 is
  rx(pi/2), Y90 is ry(pi/2), wait(n) is a delay of n * 20 ns converted to the
  Target's dt.
- The embedding of each group is the lowest-cost candidate of the snapshot's
  coupling map, groups disjoint, chosen greedily in cost order. A star costs
  the readout error of its three qubits, three sx errors on T and the 40-X
  driver error on A and B; a path costs its readout errors and the cz errors
  of its edges weighted by the gates that use them (cz on I-P1 and P1-P2 once,
  P2-D three times for the SWAP).
- Each circuit transpiles at optimization level 0 against the snapshot Target
  with a fixed seed, so driver X gates stay in place. An explicit ALAP pass
  then inserts delay instructions so every qubit's last operation ends when
  the final measurement starts, which places the drivers' X gates inside the
  target's idle as on the hardware. Kingston's X lasts 32 ns against 20 ns on
  Tuna, so 40 driver X gates span 1.28 us against the target's 0.8 us wait.
- Aer's density-matrix run saves the exact outcome distribution before
  measurement; the replay applies each qubit's readout channel to it
  analytically, giving shot-free predictions, and samples the same circuit with
  the Tuna shot count. The sampled counts pass through the same
  estimators as the exact distribution: phase asin(2 P1 - 1), shifts against
  the undriven configuration, the additivity residual, driver P1, and
  corrected and post-selected teleport fidelity.

Modes: --run writes the full replay JSON; --check requires the recorded
cases and analysis digests and every measured Tuna-17 column to match the
retained run, then replays every star and path on the CPU and compares each
exact prediction, duration and native gate count with the retained JSON, with
sampled counts at reduced shots checked against the exact values; --refresh-measured rewrites the
measured columns, summary and analysis digest from the current analysis.json
and leaves every Kingston prediction untouched.

Usage: "$PYTHON" scripts/qi_ibm_noise_replay.py (--run | --check | --refresh-measured) [--out FILE]
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import re
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import qi_crosstalk_teleport_cases as qi  # noqa: E402

import calibration_snapshot  # noqa: E402
import parallel  # noqa: E402
import snapshot_laws  # noqa: E402

SCHEMA = "qi-ibm-noise-replay-v1"
RUN_DIR = ROOT / "results/quantum_inspire/runs/2026-10-16T211635Z-tuna_17"
SNAPSHOT = ROOT / "docs/evidence/calibration/ibm_kingston.json"
OUT = ROOT / "results/quantum_inspire/ibm_noise_replay/tuna_17-ibm_kingston.json"
SEED = 20261016
CYCLE_SECONDS = 20e-9
CHECK_SHOTS = 2048
# Exact distributions are deterministic double-precision reductions; sampled
# values must agree with them within this many binomial standard errors.
SIGMAS = 6.0
EXACT_TOLERANCE = 1e-7
GATE_LINE = re.compile(r"^(\w+)(?:\((\d+)\))?\s+(q\[\d+\](?:,\s*q\[\d+\])*)$")

Gate = tuple[str, int | None, tuple[int, ...]]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_cqasm(text: str) -> list[Gate]:
    """Gate instructions of a cQASM 3.0 file in program order; declarations, barrier and measure are skipped."""
    gates: list[Gate] = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(("//", "version", "qubit", "bit", "barrier", "b =")):
            continue
        match = GATE_LINE.match(line)
        if match is None:
            raise ValueError(f"unparsed cQASM line: {line!r}")
        name, count, operands = match.groups()
        qubits = tuple(int(x) for x in re.findall(r"q\[(\d+)\]", operands))
        gates.append((name, int(count) if count else None, qubits))
    return gates


def restrict(gates: list[Gate], labels: Sequence[int]) -> list[Gate]:
    """The gates acting on the label set; a gate never straddles groups of a disjoint packing."""
    keep = set(labels)
    out = []
    for gate in gates:
        inside = [q in keep for q in gate[2]]
        if any(inside) and not all(inside):
            raise ValueError(f"gate {gate} straddles the group {sorted(keep)}")
        if all(inside):
            out.append(gate)
    return out


def logical_circuit(gates: list[Gate], labels: Sequence[int], dt: float) -> Any:
    """Qiskit circuit on len(labels) qubits; local qubit k is the group's k-th label."""
    from qiskit import QuantumCircuit

    local = {label: k for k, label in enumerate(labels)}
    circuit = QuantumCircuit(len(labels))
    for name, count, qubits in gates:
        q = [local[x] for x in qubits]
        if name == "X90":
            circuit.rx(math.pi / 2, q[0])
        elif name == "Y90":
            circuit.ry(math.pi / 2, q[0])
        elif name == "X":
            circuit.x(q[0])
        elif name == "H":
            circuit.h(q[0])
        elif name == "S":
            circuit.s(q[0])
        elif name == "Sdag":
            circuit.sdg(q[0])
        elif name == "CNOT":
            circuit.cx(q[0], q[1])
        elif name == "SWAP":
            circuit.swap(q[0], q[1])
        elif name == "wait":
            assert count is not None
            cycles = count * CYCLE_SECONDS / dt
            if abs(cycles - round(cycles)) > 1e-9:
                raise ValueError(f"wait({count}) is not a whole number of dt")
            circuit.delay(round(cycles), q[0], unit="dt")
        else:
            raise ValueError(f"no Qiskit mapping for {name}")
    return circuit


class Chip:
    """Reads of the snapshot that embedding costs and the ALAP pass need."""

    def __init__(self, snapshot: dict[str, Any]) -> None:
        self.dt = snapshot["dt"]
        rows = snapshot["instructions"]
        self.duration: dict[tuple[str, tuple[int, ...]], float] = {}
        self.error: dict[tuple[str, tuple[int, ...]], float] = {}
        for op, entries in rows.items():
            for row in entries:
                self.duration[(op, tuple(row["qargs"]))] = row["duration"]
                self.error[(op, tuple(row["qargs"]))] = row["error"]
        self.readout = [(q["e10"] + q["e01"]) / 2 for q in snapshot["qubits"]]
        cz: dict[frozenset[int], list[float]] = {}
        for row in rows["cz"]:
            cz.setdefault(frozenset(row["qargs"]), []).append(row["error"])
        self.cz = {edge: sum(v) / len(v) for edge, v in cz.items()}
        adjacency: dict[int, list[int]] = {}
        for edge in self.cz:
            a, b = sorted(edge)
            adjacency.setdefault(a, []).append(b)
            adjacency.setdefault(b, []).append(a)
        self.neighbors = {q: sorted(v) for q, v in adjacency.items()}

    def single(self, op: str, qubit: int) -> float:
        return self.error[(op, (qubit,))]

    def star_cost(self, t: int, a: int, b: int) -> float:
        drive = qi.DRIVE_PULSES
        return (
            self.readout[t]
            + self.readout[a]
            + self.readout[b]
            + 3 * self.single("sx", t)
            + drive * (self.single("x", a) + self.single("x", b))
        )

    def path_cost(self, i: int, p1: int, p2: int, d: int) -> float:
        return (
            sum(self.readout[q] for q in (i, p1, p2, d))
            + self.cz[frozenset((i, p1))]
            + self.cz[frozenset((p1, p2))]
            + 3 * self.cz[frozenset((p2, d))]
        )


def embed(chip: Chip, stars: int, paths: int) -> tuple[list[tuple[int, int, int]], list[tuple[int, int, int, int]]]:
    """Lowest-cost disjoint stars and paths of the coupling map, each family packed greedily in cost order."""
    star_candidates = sorted(
        (chip.star_cost(t, a, b), (t, a, b))
        for t, nbrs in chip.neighbors.items()
        for a, b in itertools.combinations(nbrs, 2)
    )
    path_candidates = sorted(
        (chip.path_cost(i, p1, p2, d), (i, p1, p2, d))
        for p1, nbrs in chip.neighbors.items()
        for i in nbrs
        for p2 in nbrs
        if p2 != i
        for d in chip.neighbors[p2]
        if d not in (i, p1, p2)
    )

    def pack[T: tuple[int, ...]](candidates: list[tuple[float, T]], count: int) -> list[T]:
        chosen: list[T] = []
        used: set[int] = set()
        for _, group in candidates:
            if len(chosen) == count:
                break
            if used.isdisjoint(group):
                chosen.append(group)
                used.update(group)
        if len(chosen) < count:
            raise ValueError("the coupling map holds fewer disjoint groups than the cases need")
        return chosen

    return pack(star_candidates, stars), pack(path_candidates, paths)


def schedule_alap(circuit: Any, chip: Chip, clbits: int, physical: Sequence[int]) -> Any:
    """Copy of a transpiled circuit with delays that end every qubit's last operation at the measurement.

    Operation durations come from the snapshot (delays carry their own dt
    count); a multi-qubit operation starts when its latest-ending operand
    allows, and each operand idles through the gap. The result saves the
    outcome probabilities of the physical qubits (local bit k is physical[k])
    and measures them into clbits.
    """
    from qiskit import QuantumCircuit

    ops = []
    for instruction in circuit.data:
        name = instruction.operation.name
        if name in ("barrier", "measure"):
            continue
        qubits = tuple(circuit.find_bit(q).index for q in instruction.qubits)
        if name == "delay":
            dur = int(instruction.operation.params[0])
        else:
            seconds = chip.duration[(name, qubits)]
            dur = round(seconds / chip.dt)
            if abs(seconds / chip.dt - dur) > 1e-6:
                raise ValueError(f"{name}{qubits} lasts {seconds} s, not a whole number of dt")
        ops.append((instruction, qubits, dur))
    # Reverse sweep: time measured back from the measurement.
    back: dict[int, int] = {}
    span: list[int] = []
    for _, qubits, dur in reversed(ops):
        end = max(back.get(q, 0) for q in qubits)
        span.append(end + dur)
        for q in qubits:
            back[q] = end + dur
    span.reverse()
    total = max(back.values(), default=0)
    out = QuantumCircuit(circuit.num_qubits, clbits)
    free = dict.fromkeys(back, 0)
    for (instruction, qubits, dur), start_back in zip(ops, span, strict=True):
        start = total - start_back
        for q in qubits:
            if start > free[q]:
                out.delay(start - free[q], q, unit="dt")
            free[q] = start + dur
        out.append(instruction.operation, list(qubits))
    for q, finish in free.items():
        if finish < total:
            out.delay(total - finish, q, unit="dt")
    out.save_probabilities(list(physical), label="p")
    for k, q in enumerate(physical):
        out.measure(q, k)
    return out


def apply_readout(probs: np.ndarray, flips: Sequence[tuple[float, float]]) -> np.ndarray:
    """Outcome distribution after each qubit's channel [[1 - e10, e10], [e01, 1 - e01]]; bit k counts from the right."""
    k = len(flips)
    tensor = probs.reshape((2,) * k)
    for bit, (e10, e01) in enumerate(flips):
        axis = k - 1 - bit
        confusion = np.array([[1 - e10, e01], [e10, 1 - e01]])
        tensor = np.moveaxis(np.tensordot(confusion, tensor, axes=([1], [axis])), 0, axis)
    return np.asarray(tensor.reshape(-1))


class Replay:
    """Callable over group tasks; each task simulates on the snapshot restricted to its own qubits."""

    def __init__(self, snapshot: dict[str, Any], shots: int, seed: int) -> None:
        self.snapshot = snapshot
        self.shots = shots
        self.seed = seed

    def __call__(self, task: dict[str, Any]) -> dict[str, Any]:
        from qiskit import transpile

        # The noise model is local to each qubit and gate, so the group's
        # snapshot restriction (ascending physical order) carries the same
        # channels as the full device while Aer assembles three or four
        # qubits instead of 156.
        physical = task["physical"]
        active = sorted(physical)
        local = [active.index(q) for q in physical]
        sub = snapshot_laws.restrict(self.snapshot, active)
        target = calibration_snapshot.build_target(sub)
        simulator = calibration_snapshot.noise_simulator(sub, "CPU")
        chip = Chip(sub)
        flips = [(self.snapshot["qubits"][q]["e10"], self.snapshot["qubits"][q]["e01"]) for q in physical]
        runs = {}
        for name, gates in task["circuits"].items():
            logical = logical_circuit([(g[0], g[1], tuple(g[2])) for g in gates], task["labels"], chip.dt)
            compiled = transpile(
                logical, target=target, initial_layout=local, optimization_level=0, seed_transpiler=self.seed
            )
            scheduled = schedule_alap(compiled, chip, len(physical), local)
            result = simulator.run(scheduled, shots=self.shots, seed_simulator=self.seed).result()
            exact = apply_readout(np.asarray(result.data(0)["p"], dtype=float), flips)
            counts = {key: int(value) for key, value in sorted(result.get_counts().items())}
            runs[name] = {
                "exact": exact.tolist(),
                "counts": counts,
                "duration_dt": scheduled_duration(scheduled, chip),
                "native_gates": dict(sorted(compiled.count_ops().items())),
            }
        return {"id": task["id"], "runs": runs}


def scheduled_duration(circuit: Any, chip: Chip) -> int:
    """Length in dt of the longest qubit timeline of a scheduled circuit."""
    clock: dict[int, int] = {}
    for instruction in circuit.data:
        name = instruction.operation.name
        if name in ("save_probabilities", "measure", "barrier"):
            continue
        qubits = tuple(circuit.find_bit(q).index for q in instruction.qubits)
        dur = (
            int(instruction.operation.params[0]) if name == "delay" else round(chip.duration[(name, qubits)] / chip.dt)
        )
        start = max(clock.get(q, 0) for q in qubits)
        for q in qubits:
            clock[q] = start + dur
    return max(clock.values(), default=0)


def bit_of(index: int, k: int) -> int:
    return (index >> k) & 1


def star_estimates(dists: dict[str, list[float]], roles: dict[str, int]) -> dict[str, Any]:
    """Phase, shifts, residual and driver P1 of a star from per-config distributions; local bits are T, A, B."""
    local = {"T": 0, "A": 1, "B": 2}
    p: dict[str, float] = {}
    drivers: dict[str, dict[str, float]] = {}
    for config in qi.CONFIGS:
        dist = dists[config]
        marginal = {role: sum(v for i, v in enumerate(dist) if bit_of(i, k)) for role, k in local.items()}
        p[config] = marginal["T"]
        drivers[config] = {str(roles[role]): marginal[role] for role in ("A", "B")}
    phase = {c: math.asin(max(-1.0, min(1.0, 2 * p[c] - 1))) for c in qi.CONFIGS}
    shift = {c: phase[c] - phase["none"] for c in ("A", "B", "AB")}
    return {
        "p1": p,
        "phase_rad": phase,
        "phase_shift_rad": shift,
        "additivity_residual_rad": shift["AB"] - shift["A"] - shift["B"],
        "driver_p1": drivers,
    }


def path_estimates(dist: list[float], label: str) -> dict[str, float]:
    """Corrected and post-selected teleport fidelity from an outcome distribution; local bits are I, P1, P2, D."""
    _, _, flips = qi.INPUTS[label]
    want = 1 if label == "1" else 0
    corrected = post = post_ok = 0.0
    for index, value in enumerate(dist):
        m_i, m_p1, d = bit_of(index, 0), bit_of(index, 1), bit_of(index, 3)
        flip = (m_p1 if "x" in flips else 0) ^ (m_i if "z" in flips else 0)
        if (d ^ flip) == want:
            corrected += value
        if m_i == 0 and m_p1 == 0:
            post += value
            if d == want:
                post_ok += value
    return {
        "corrected_fidelity": corrected,
        "postselected_fidelity": post_ok / post if post else math.nan,
        "postselected_fraction": post,
    }


def counts_distribution(counts: dict[str, int], k: int) -> list[float]:
    """Empirical outcome distribution over k local bits; bit b is character k - 1 - b of a key."""
    total = sum(counts.values())
    dist = [0.0] * (1 << k)
    for key, n in counts.items():
        dist[int(key, 2)] += n / total
    return dist


def build_tasks(
    cases: dict[str, Any], run_dir: Path, snapshot: dict[str, Any], stars: int | None, paths: int | None
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    chip = Chip(snapshot)
    star_cases = cases["stars"][:stars]
    path_cases = cases["paths"][:paths]
    star_phys, path_phys = embed(chip, len(cases["stars"]), len(cases["paths"]))
    star_phys, path_phys = star_phys[: len(star_cases)], path_phys[: len(path_cases)]
    programs = {
        row["file"]: parse_cqasm((run_dir / row["file"]).read_text(encoding="utf-8")) for row in cases["circuits"]
    }
    tasks: dict[str, dict[str, Any]] = {}
    layout: dict[str, Any] = {"stars": [], "paths": []}
    for star, phys in zip(star_cases, star_phys, strict=True):
        labels = [star["T"], star["A"], star["B"]]
        key = f"star-T{star['T']}"
        tasks[key] = {
            "id": key,
            "labels": labels,
            "physical": list(phys),
            "circuits": {f"additivity-{c}.cq": restrict(programs[f"additivity-{c}.cq"], labels) for c in qi.CONFIGS},
        }
        layout["stars"].append({**star, "physical": dict(zip("TAB", phys, strict=True)), "cost": chip.star_cost(*phys)})
    for path, route in zip(path_cases, path_phys, strict=True):
        labels = [path["I"], path["P1"], path["P2"], path["D"]]
        key = f"path-I{path['I']}"
        tasks[key] = {
            "id": key,
            "labels": labels,
            "physical": list(route),
            "circuits": {"teleport.cq": restrict(programs["teleport.cq"], labels)},
        }
        layout["paths"].append(
            {**path, "physical": dict(zip(("I", "P1", "P2", "D"), route, strict=True)), "cost": chip.path_cost(*route)}
        )
    return tasks, layout


def replay(
    run_dir: Path, snapshot: dict[str, Any], shots: int, seed: int, stars: int | None, paths: int | None
) -> dict[str, Any]:
    """Exact and sampled predictions for the cases of run_dir, with the measured estimates beside them."""
    cases = json.loads((run_dir / "cases.json").read_text(encoding="utf-8"))
    measured = json.loads(
        (run_dir / "analysis.json").read_text(encoding="utf-8")
    )  # measured Tuna estimates, reported beside the predictions
    tasks, layout = build_tasks(cases, run_dir, snapshot, stars, paths)
    outputs = parallel.ordered_map(Replay(snapshot, shots, seed), list(tasks.values()), min_items=1)
    results = {out["id"]: out for out in outputs}
    additivity = []
    for entry in layout["stars"]:
        runs = results[f"star-T{entry['T']}"]["runs"]
        roles = {"T": entry["T"], "A": entry["A"], "B": entry["B"]}
        files = {c: runs[f"additivity-{c}.cq"] for c in qi.CONFIGS}
        tuna = next(row for row in measured["additivity"] if row["T"] == entry["T"])
        additivity.append(
            {
                **entry,
                "duration_dt": {c: files[c]["duration_dt"] for c in qi.CONFIGS},
                "exact": star_estimates({c: files[c]["exact"] for c in qi.CONFIGS}, roles),
                "sampled": star_estimates({c: counts_distribution(files[c]["counts"], 3) for c in qi.CONFIGS}, roles),
                "tuna_17": strip(tuna, ("T", "A", "B")),
            }
        )
    teleport = []
    for entry in layout["paths"]:
        run_ = results[f"path-I{entry['I']}"]["runs"]["teleport.cq"]
        tuna = next(row for row in measured["teleport"] if row["I"] == entry["I"])
        teleport.append(
            {
                **entry,
                "duration_dt": run_["duration_dt"],
                "native_gates": run_["native_gates"],
                "exact": path_estimates(run_["exact"], entry["input"]),
                "sampled": path_estimates(counts_distribution(run_["counts"], 4), entry["input"]),
                "tuna_17": strip(tuna, ("I", "P1", "P2", "D", "input")),
            }
        )
    return {"additivity": additivity, "teleport": teleport}


def strip(row: dict[str, Any], keys: Sequence[str]) -> dict[str, Any]:
    return {k: v for k, v in row.items() if k not in keys}


def measured(record: dict[str, Any]) -> dict[str, Any]:
    """The record with its Tuna-17 measured blocks, summary and analysis digest taken from RUN_DIR/analysis.json.

    The Kingston predictions depend only on the circuits and the calibration
    snapshot; the measured columns beside them come from the current analysis,
    so a changed analysis refreshes them without a new simulation.
    """
    analysis = json.loads((RUN_DIR / "analysis.json").read_text(encoding="utf-8"))
    body = {
        "additivity": [
            {**row, "tuna_17": strip(next(m for m in analysis["additivity"] if m["T"] == row["T"]), ("T", "A", "B"))}
            for row in record["additivity"]
        ],
        "teleport": [
            {
                **row,
                "tuna_17": strip(
                    next(m for m in analysis["teleport"] if m["I"] == row["I"]), ("I", "P1", "P2", "D", "input")
                ),
            }
            for row in record["teleport"]
        ],
    }
    source = {**record["source_run"], "analysis_sha256": sha256(RUN_DIR / "analysis.json")}
    return {**record, "source_run": source, "summary": summarize(body), **body}


def versions() -> dict[str, str]:
    import qiskit
    import qiskit_aer

    return {
        "python": sys.version.split()[0],
        "qiskit": qiskit.__version__,
        "qiskit_aer": qiskit_aer.__version__,
        "numpy": np.__version__,
    }


def summarize(body: dict[str, Any]) -> dict[str, Any]:
    stars = body["additivity"]
    paths = body["teleport"]
    return {
        "max_abs_exact_phase_shift_rad": max(abs(v) for s in stars for v in s["exact"]["phase_shift_rad"].values()),
        "max_abs_exact_additivity_residual_rad": max(abs(s["exact"]["additivity_residual_rad"]) for s in stars),
        "max_exact_driver_p1_after_40_x": max(
            v for s in stars for c in ("A", "B", "AB") for v in s["exact"]["driver_p1"][c].values()
        ),
        "max_abs_tuna_phase_shift_rad": max(abs(v) for s in stars for v in s["tuna_17"]["phase_shift_rad"].values()),
        "max_abs_tuna_additivity_residual_rad": max(abs(s["tuna_17"]["additivity_residual_rad"]) for s in stars),
        "exact_corrected_fidelity": {p["input"]: p["exact"]["corrected_fidelity"] for p in paths},
        "tuna_corrected_fidelity": {p["input"]: p["tuna_17"]["corrected_fidelity"] for p in paths},
    }


def run(out: Path, shots: int | None) -> None:
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    cases = json.loads((RUN_DIR / "cases.json").read_text(encoding="utf-8"))
    shots = shots or cases["shots"]
    body = replay(RUN_DIR, snapshot, shots, SEED, None, None)
    record = {
        "schema": SCHEMA,
        "backend": snapshot["backend"],
        "calibration": snapshot["calibration"],
        "snapshot_sha256": sha256(SNAPSHOT),
        "source_run": {
            "backend": cases["backend"],
            "cases_sha256": sha256(RUN_DIR / "cases.json"),
            "analysis_sha256": sha256(RUN_DIR / "analysis.json"),
            "circuits": {row["file"]: row["sha256"] for row in cases["circuits"]},
        },
        "shots": shots,
        "seed": SEED,
        "versions": versions(),
        "summary": summarize(body),
        **body,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(record["summary"], indent=1))
    print(f"wrote {out}")


def close(sampled: float, exact: float, shots: int, sigmas: float = SIGMAS) -> bool:
    """A sampled proportion within sigmas binomial standard errors of its exact value, floored near 0 and 1."""
    return abs(sampled - exact) <= sigmas * math.sqrt(max(exact * (1 - exact), 1.0 / shots) / shots)


def compare(name: str, new: Any, old: Any, problems: list[str]) -> None:
    """Append one problem per leaf where a replayed value leaves the retained one by more than EXACT_TOLERANCE."""
    if isinstance(old, dict):
        if not isinstance(new, dict) or set(new) != set(old):
            problems.append(f"{name}: keys differ from the retained record")
            return
        for key in old:
            compare(f"{name}.{key}", new[key], old[key], problems)
    elif isinstance(old, float):
        both_nan = isinstance(new, float) and math.isnan(new) and math.isnan(old)
        if not both_nan and not abs(new - old) <= EXACT_TOLERANCE:
            problems.append(f"{name}: {new} differs from retained {old}")
    elif new != old:
        problems.append(f"{name}: {new} differs from retained {old}")


def check(retained: Path) -> None:
    """Replay of every star and path against the retained JSON, sampled counts at reduced shots against exact values."""
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    record = json.loads(retained.read_text(encoding="utf-8"))
    if record["schema"] != SCHEMA:
        raise SystemExit(f"{retained}: schema {record['schema']} is not {SCHEMA}")
    if record["snapshot_sha256"] != sha256(SNAPSHOT):
        raise SystemExit(f"{retained}: calibration snapshot digest differs from {SNAPSHOT.name}")
    cases = json.loads((RUN_DIR / "cases.json").read_text(encoding="utf-8"))
    if record["source_run"]["cases_sha256"] != sha256(RUN_DIR / "cases.json"):
        raise SystemExit(f"{retained}: source cases differ from {RUN_DIR.name}")
    if record["source_run"]["analysis_sha256"] != sha256(RUN_DIR / "analysis.json"):
        raise SystemExit(
            f"{retained}: recorded analysis digest differs from {RUN_DIR.name}/analysis.json; run --refresh-measured"
        )
    if record != measured(record):
        raise SystemExit(f"{retained}: measured Tuna-17 columns differ from {RUN_DIR.name}/analysis.json")
    # The replayed bytes, the manifest digest and the record's circuit map agree.
    if set(record["source_run"]["circuits"]) != {row["file"] for row in cases["circuits"]}:
        raise SystemExit(f"{retained}: recorded circuits differ from the {RUN_DIR.name} manifest")
    for row in cases["circuits"]:
        text = (RUN_DIR / row["file"]).read_text(encoding="utf-8")
        digest = hashlib.sha256(text.encode()).hexdigest()
        if not digest == row["sha256"] == record["source_run"]["circuits"][row["file"]]:
            raise SystemExit(f"{retained}: circuit {row['file']} differs from the replayed one")
    body = replay(RUN_DIR, snapshot, CHECK_SHOTS, SEED, None, None)
    problems: list[str] = []
    for family, key in (("additivity", "T"), ("teleport", "I")):
        if [row[key] for row in body[family]] != [row[key] for row in record[family]]:
            raise SystemExit(f"{retained}: {family} entries differ from the replayed cases")
    for new, old in zip(body["additivity"], record["additivity"], strict=True):
        tag = f"star T={new['T']}"
        if new["physical"] != old["physical"]:
            problems.append(f"{tag}: embedding differs from the retained one")
        for field in ("duration_dt", "exact"):
            compare(f"{tag} {field}", new[field], old[field], problems)
        for config in qi.CONFIGS:
            if not close(new["sampled"]["p1"][config], new["exact"]["p1"][config], CHECK_SHOTS):
                problems.append(f"{tag}: sampled p1[{config}] disagrees with its exact value")
    for new, old in zip(body["teleport"], record["teleport"], strict=True):
        tag = f"path I={new['I']}"
        if new["physical"] != old["physical"]:
            problems.append(f"{tag}: embedding differs from the retained one")
        for field in ("duration_dt", "native_gates", "exact"):
            compare(f"{tag} {field}", new[field], old[field], problems)
        if not close(new["sampled"]["corrected_fidelity"], new["exact"]["corrected_fidelity"], CHECK_SHOTS):
            problems.append(f"{tag}: sampled corrected fidelity disagrees with its exact value")
    if problems:
        raise SystemExit(f"{retained}: " + "; ".join(problems))
    worst = max(abs(row["exact"]["additivity_residual_rad"]) for row in body["additivity"])
    print(
        f"qi ibm noise replay: {len(body['additivity'])} stars and {len(body['teleport'])} paths match "
        f"{retained.name}; largest exact residual {worst:.2e} rad"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--run", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--refresh-measured", action="store_true")
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--shots", type=int, default=None)
    args = parser.parse_args()
    if args.run:
        run(args.out, args.shots)
    elif args.refresh_measured:
        record = measured(json.loads(args.out.read_text(encoding="utf-8")))
        args.out.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
        print(f"refreshed the measured columns of {args.out}")
    else:
        check(args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
