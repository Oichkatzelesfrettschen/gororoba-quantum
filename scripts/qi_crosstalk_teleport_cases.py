"""cQASM 3.0 cases for Quantum Inspire backends: spectator-drive phase additivity and transported-pair teleportation.

Two experiments, each a transmon translation of a spin-qubit result:

- Spectator-drive phase additivity (Wu et al., Nat. Phys., doi:10.1038/s41567-026-03466-2).
  A target T runs X90, an explicit idle of WAIT_CYCLES 20 ns cycles, and the
  quadrature Y90, so its outcome probability P1 = (1 + sin phi)/2 reads the
  accumulated z rotation Rz(phi) with standard error 1/sqrt(shots) at every
  P1. Neighbors A and B either idle or apply
  DRIVE_PULSES X gates (an even count, so each returns to |0>) inside that
  idle. Configurations none, A, B and AB run as four circuits: batch-00
  holds none, A and B and batch-01 holds none and AB, so every shift
  subtracts an undriven reference measured in its own batch.
  The pairwise model of the paper sums phases, so the residual
  phi(AB) - phi(A) - phi(B) + phi(none) is the falsifier of pairwise
  additivity. Each driver's own outcome after its even X count reads the
  coherent rotation error that its excursions out of |0> carry into the
  target through any residual ZZ coupling. Every
  disjoint (T, A, B) star the coupling map admits runs in parallel.
- Transported-pair teleportation (Matsumoto et al., Nature 653, 391-397,
  doi:10.1038/s41586-026-10423-9). On a path I - P1 - P2 - D, P1 and P2 form
  a Bell pair, SWAP carries P2's half to D (the gate-based counterpart of
  conveyor shuttling), and I and P1 take a Bell-state measurement. The
  backends have no feed-forward, so the correction X^m(P1) Z^m(I) is applied
  to the recorded outcome of D: each input is a Pauli eigenstate measured in
  its own basis, where every Pauli correction either keeps or flips the
  outcome. The post-selected subset m(I) = m(P1) = 0 is the conditional
  protocol of the paper.

The ALAP scheduler of OpenSquirrel ends every qubit's program at the final
measurement, so a driver's X gates followed by wait(1) sit inside the target's
wait of WAIT_CYCLES = DRIVE_PULSES cycles. Tuna quantizes rotation angles to
pi/36; every gate here is a multiple of pi/2.

--write DIR writes each backend's series from the backend catalogue
snapshot: batch-NN/ directories of at most HARDWARE_BATCH_CIRCUITS circuits,
each a submittable case with its cases.json manifest (qubit roles,
configurations, shots), and a series cases.json listing the batches.
--check DIR regenerates every file in memory from the retained catalogue and
compares bytes and file sets, offline. --analyze RUN_DIR... [--out FILE]
writes the additivity and teleportation estimates from the collected raw
shots of every batch of one series.

--replay RUN_DIR... recomputes each retained single-batch analysis.json from
its raw shots and compares bytes, offline; --replay-series FILE RUN_DIR...
does the same for the analysis FILE of one batched series. --self-test checks the additivity-only
case, both retained backend bit-order conventions and the reduction of a
batched series to its single-batch analysis, using synthetic shots.

Usage: "$PYTHON" scripts/qi_crosstalk_teleport_cases.py
       (--write DIR | --check DIR | --analyze RUN_DIR... [--out FILE] | --replay RUN_DIR...
        | --replay-series FILE RUN_DIR... | --self-test)
       [--catalogue FILE]
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
from qi_platform import HARDWARE_BATCH_CIRCUITS  # noqa: E402

from parallel import ordered_map  # noqa: E402

CATALOGUE = ROOT / "docs/evidence/quantum_inspire/catalogue.json"
DRIVE_PULSES = 40
WAIT_CYCLES = DRIVE_PULSES
CONFIGS = ("none", "A", "B", "AB")
# Input label -> (preparation on I, rotation on D before measurement, which
# BSM bits flip the recorded outcome: "x" for m(P1), "z" for m(I)).
INPUTS = {
    "0": ([], [], ("x",)),
    "1": (["X"], [], ("x",)),
    "+": (["H"], ["H"], ("z",)),
    "+i": (["H", "S"], ["Sdag", "H"], ("x", "z")),
}
INPUT_ORDER = ("0", "1", "+", "+i")
# identifier -> (shots, run additivity, gate dialect)
BACKENDS = {
    "tuna_17": (16384, True, "tuna"),
    "tuna_9": (16384, True, "tuna"),
    "tuna_5": (16384, True, "tuna"),
    "QXsinglenodesimulator": (2048, True, "tuna"),
    "Rydberg": (1024, False, "rydberg"),
}
# The Ry emulator rejected the gate-model teleport case at execution; its
# native form (no bit register, RYD blockade gates) is not built, so build()
# emits no Ry case while analyze() still decodes the retained Ry runs.
NOT_GENERATED = {"Rydberg"}
# Emulators, whose analyses are controls rather than device results.
EMULATORS = {"QXsinglenodesimulator", "Rydberg"}


def edges(backend: dict[str, Any]) -> set[frozenset[int]]:
    return {frozenset(edge) for edge in backend["topology"]}


def neighbors(backend: dict[str, Any], qubit: int) -> list[int]:
    return sorted(q for e in edges(backend) if qubit in e for q in e if q != qubit)


def disjoint_stars(backend: dict[str, Any]) -> list[tuple[int, int, int]]:
    """Largest set of disjoint (T, A, B) with A and B coupled to T, smallest qubit indices first."""
    candidates = [
        (t, a, b) for t in range(backend["nqubits"]) for a, b in itertools.combinations(neighbors(backend, t), 2)
    ]
    return largest_disjoint(candidates)


def disjoint_paths(backend: dict[str, Any], limit: int) -> list[tuple[int, int, int, int]]:
    """Largest set (at most limit) of disjoint simple paths I - P1 - P2 - D."""
    candidates = []
    for p1 in range(backend["nqubits"]):
        for i in neighbors(backend, p1):
            for p2 in neighbors(backend, p1):
                for d in neighbors(backend, p2):
                    if len({i, p1, p2, d}) == 4:
                        candidates.append((i, p1, p2, d))
    return largest_disjoint(candidates, limit)


def largest_disjoint[T: tuple[int, ...]](candidates: list[T], limit: int | None = None) -> list[T]:
    """Maximum packing, or the first of size limit, by depth-first search in candidate order.

    A branch is cut when its uncovered qubits cannot hold more groups than the
    best packing found, so the result equals the exhaustive search's: the
    first packing in candidate order among those of maximum size.
    """
    best: list[T] = []
    qubits = frozenset(q for group in candidates for q in group)
    size = len(candidates[0]) if candidates else 1

    def search(start: int, used: frozenset[int], chosen: list[T]) -> bool:
        nonlocal best
        if len(chosen) > len(best):
            best = list(chosen)
            if limit is not None and len(best) >= limit:
                return True
        if len(chosen) + len(qubits - used) // size <= len(best):
            return False
        for index in range(start, len(candidates)):
            group = candidates[index]
            if used.isdisjoint(group):
                chosen.append(group)
                if search(index + 1, used | frozenset(group), chosen):
                    return True
                chosen.pop()
        return False

    search(0, frozenset(), [])
    return best


def gate(dialect: str, name: str, qubits: tuple[int, ...]) -> list[str]:
    """One logical gate in the dialect's instruction set."""
    q = ", ".join(f"q[{x}]" for x in qubits)
    if dialect == "rydberg":
        # The Rydberg emulator lists X, Z, Rx, Rz, T, S, H and CNOT.
        if name == "Sdag":
            return [f"Rz({-math.pi / 2:.15f}) {q}"]
        if name == "SWAP":
            a, b = qubits
            return [f"CNOT q[{a}], q[{b}]", f"CNOT q[{b}], q[{a}]", f"CNOT q[{a}], q[{b}]"]
    return [f"{name} {q}"]


def header(n: int) -> list[str]:
    return ["version 3.0", "", f"qubit[{n}] q", f"bit[{n}] b", ""]


def additivity_circuit(n: int, stars: list[tuple[int, int, int]], config: str) -> str:
    lines = header(n)
    for t, a, b in stars:
        driven = [q for q, role in ((a, "A"), (b, "B")) if role in config]
        lines.append(f"// star T={t} A={a} B={b} config={config}")
        lines += [f"X90 q[{t}]", f"wait({WAIT_CYCLES}) q[{t}]", f"Y90 q[{t}]"]
        for q in driven:
            lines += [f"X q[{q}]"] * DRIVE_PULSES + [f"wait(1) q[{q}]"]
    lines += ["", "barrier q", "b = measure q", ""]
    return "\n".join(lines)


def teleport_circuit(n: int, paths: list[tuple[int, int, int, int]], dialect: str) -> str:
    lines = header(n)
    for (i, p1, p2, d), label in zip(paths, INPUT_ORDER, strict=False):
        prep, rotate, _ = INPUTS[label]
        lines.append(f"// path I={i} P1={p1} P2={p2} D={d} input={label}")
        for name in prep:
            lines += gate(dialect, name, (i,))
        lines += gate(dialect, "H", (p1,)) + gate(dialect, "CNOT", (p1, p2))
        lines += gate(dialect, "SWAP", (p2, d))
        lines += gate(dialect, "CNOT", (i, p1)) + gate(dialect, "H", (i,))
        for name in rotate:
            lines += gate(dialect, name, (d,))
    if dialect == "rydberg":
        # The Rydberg emulator measures every qubit at the end and rejects measure statements.
        lines.append("")
    else:
        lines += ["", "barrier q", "b = measure q", ""]
    return "\n".join(lines)


def build(catalogue: dict[str, Any]) -> dict[str, dict[str, str]]:
    """identifier -> {relative path -> text}: batch-NN/ manifests and circuits plus the series cases.json.

    A batch holds at most HARDWARE_BATCH_CIRCUITS circuits, and a batch
    boundary is a calibration boundary. Every batch that carries a driven
    configuration also carries its own undriven reference, so each phase
    shift subtracts a reference measured under the same calibration:
    batch-00 holds none, A and B; batch-01 holds none, AB and teleport.
    """
    out: dict[str, dict[str, str]] = {}
    for backend in catalogue["backend_types"]:
        ident = backend["identifier"]
        if ident not in BACKENDS or ident in NOT_GENERATED:
            continue
        shots, additivity, dialect = BACKENDS[ident]
        n = backend["nqubits"]
        texts: dict[str, str] = {}
        groups: list[list[dict[str, str]]] = []
        common: dict[str, Any] = {
            "schema": "qi-crosstalk-teleport-cases-v2",
            "backend": ident,
            "backend_type_id": backend["id"],
            "nqubits": n,
            "shots": min(shots, backend["max_number_of_shots"]),
            "drive_pulses": DRIVE_PULSES,
            "wait_cycles": WAIT_CYCLES,
            "batch_limit": HARDWARE_BATCH_CIRCUITS,
        }
        if additivity:
            stars = disjoint_stars(backend)
            common["stars"] = [{"T": t, "A": a, "B": b} for t, a, b in stars]
            for config in CONFIGS:
                texts[f"additivity-{config}.cq"] = additivity_circuit(n, stars, config)
            groups = [
                [{"file": f"additivity-{c}.cq", "kind": "additivity", "config": c} for c in ("none", "A", "B")],
                [{"file": f"additivity-{c}.cq", "kind": "additivity", "config": c} for c in ("none", "AB")],
            ]
        paths = disjoint_paths(backend, len(INPUT_ORDER))
        # A star coupling map (Tuna-5) has no four-qubit path.
        common["paths"] = [
            {"I": i, "P1": p1, "P2": p2, "D": d, "input": label}
            for (i, p1, p2, d), label in zip(paths, INPUT_ORDER, strict=False)
        ]
        if paths:
            texts["teleport.cq"] = teleport_circuit(n, paths, dialect)
            teleport = {"file": "teleport.cq", "kind": "teleport"}
            if groups and len(groups[-1]) < HARDWARE_BATCH_CIRCUITS:
                groups[-1].append(teleport)
            else:
                groups.append([teleport])
        files: dict[str, str] = {}
        batches = []
        for index, rows in enumerate(groups):
            if len(rows) > HARDWARE_BATCH_CIRCUITS:
                raise AssertionError(f"{ident} batch {index} holds {len(rows)} circuits")
            name = f"batch-{index:02d}"
            for row in rows:
                row["sha256"] = hashlib.sha256(texts[row["file"]].encode()).hexdigest()
                files[f"{name}/{row['file']}"] = texts[row["file"]]
            files[f"{name}/cases.json"] = json.dumps({**common, "batch": name, "circuits": rows}, indent=1) + "\n"
            batches.append({"batch": name, "files": [row["file"] for row in rows]})
        series = {"schema": "qi-crosstalk-teleport-series-v1", "backend": ident, "batches": batches}
        files["cases.json"] = json.dumps(series, indent=1) + "\n"
        out[ident] = files
    return out


def write(directory: Path, catalogue: dict[str, Any]) -> None:
    for ident, files in build(catalogue).items():
        for name, text in files.items():
            path = directory / ident / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        print(f"{ident}: {sum(name.endswith('.cq') for name in files)} circuits")


def check(directory: Path, catalogue: dict[str, Any]) -> None:
    count = 0
    for ident, files in build(catalogue).items():
        retained = {p.relative_to(directory / ident).as_posix() for p in (directory / ident).rglob("*") if p.is_file()}
        if retained != set(files):
            raise SystemExit(f"{directory / ident}: files {sorted(retained ^ set(files))} differ from the regeneration")
        for name, text in files.items():
            path = directory / ident / name
            if path.read_text(encoding="utf-8") != text:
                raise SystemExit(f"{path}: differs from the regenerated case")
            count += 1
    print(f"qi cases: {count} files match their regeneration")


# The retained Ry diagnostic puts Q0 leftmost; QX and Tuna put it rightmost.
LEFTMOST_QUBIT_ZERO = {"Rydberg"}


def bit(shot: str, qubit: int, backend: str = "tuna_17") -> int:
    """The retained Ry diagnostic puts Q0 leftmost; QX and Tuna put it rightmost."""
    return int(shot[qubit if backend in LEFTMOST_QUBIT_ZERO else len(shot) - 1 - qubit])


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (centre - half, centre + half)


def phase_of(p1: float) -> float:
    """X90, Rz(phi), Y90 gives P1 = (1 + sin phi)/2; the binomial standard error of phi is 1/sqrt(n) at every P1.

    One quadrature reads sin(phi) only, so the phase is its principal branch,
    |phi| <= pi/2: a rotation beyond pi/2 folds back. star_report records each
    star's distance from the fold, and a phase whose |2 P1 - 1| exceeds
    BRANCH_LIMIT is flagged as branch-ambiguous rather than read as unique.
    """
    return math.asin(max(-1.0, min(1.0, 2 * p1 - 1)))


BRANCH_LIMIT = math.sin(1.2)


def two_proportion_z(k1: int, n1: int, k2: int, n2: int) -> float:
    p1, p2 = k1 / n1, k2 / n2
    pooled = (k1 + k2) / (n1 + n2)
    se = math.sqrt(pooled * (1 - pooled) * (1 / n1 + 1 / n2))
    return (p2 - p1) / se if se else 0.0


Acquisition = tuple[str, dict[str, Any], list[str]]


def star_report(star: dict[str, int], additivity: list[Acquisition], backend: str) -> dict[str, Any]:
    """Target phases, pairwise residual, driver crosstalk and driver-conditioned target phases for one star.

    additivity lists (batch, manifest row, shots) in manifest order. Each
    driven configuration's shift subtracts the undriven reference of its own
    batch; a single-batch run has one reference.
    """
    counts: dict[tuple[str, str], dict[str, int]] = {}
    n: dict[tuple[str, str], int] = {}
    batch_of: dict[str, str] = {}
    conditioned: dict[str, dict[str, Any]] = {}
    for batch, row, shots in additivity:
        config, key = row["config"], (batch, row["config"])
        n[key] = len(shots)
        counts[key] = {role: sum(bit(s, star[role], backend) for s in shots) for role in ("T", "A", "B")}
        # A driver-conditioned target phase separates a ZZ phase, which follows
        # the driver's state, from a drive-induced shift, which does not.
        conditioned[config] = {}
        if config == "none":
            continue
        batch_of[config] = batch
        for role in ("A", "B"):
            if role not in config:
                continue
            split = {}
            for outcome in (0, 1):
                sub = [s for s in shots if bit(s, star[role], backend) == outcome]
                if sub:
                    p1 = sum(bit(s, star["T"], backend) for s in sub) / len(sub)
                    split[str(outcome)] = {"shots": len(sub), "target_p1": p1, "target_phase_rad": phase_of(p1)}
            conditioned[config][str(star[role])] = split
    references = [batch for batch, config in counts if config == "none"]
    reference = {c: (batch_of[c], "none") for c in ("A", "B", "AB")}
    key_of = {c: (batch_of[c], c) for c in ("A", "B", "AB")} | {"none": (references[0], "none")}
    p = {c: counts[key_of[c]]["T"] / n[key_of[c]] for c in CONFIGS}
    phase = {c: phase_of(p[c]) for c in CONFIGS}
    shift = {c: phase[c] - phase_of(counts[reference[c]]["T"] / n[reference[c]]) for c in ("A", "B", "AB")}
    residual = shift["AB"] - shift["A"] - shift["B"]
    weight = {key: 0 for key in counts}
    for c, sign in (("AB", 1), ("A", -1), ("B", -1)):
        weight[key_of[c]] += sign
        weight[reference[c]] -= sign
    sigma = math.sqrt(sum(weight[key] ** 2 / n[key] for key in counts))
    drivers = {}
    for role in ("A", "B"):
        alone, both = key_of[role], key_of["AB"]
        k_single, k_both = counts[alone][role], counts[both][role]
        p_single = k_single / n[alone]
        driver: dict[str, Any] = {
            "qubit": star[role],
            "p1_driven_alone": p_single,
            "p1_driven_with_other": k_both / n[both],
            "simultaneous_change": k_both / n[both] - p_single,
            "simultaneous_change_z": two_proportion_z(k_single, n[alone], k_both, n[both]),
        }
        # An even X count returns an ideal driver to |0>. Depolarizing,
        # relaxation and readout error keep P1 at or below about 1/2, so a
        # larger P1 requires a coherent rotation error; for a pure per-gate
        # over-rotation eps, P1 = sin^2(DRIVE_PULSES eps / 2) and the smallest
        # solution bounds |eps| from below.
        if p_single > 0.5:
            driver["overrotation_lower_bound_rad_per_x"] = 2 * math.asin(math.sqrt(p_single)) / DRIVE_PULSES
        drivers[role] = driver
    largest = max(abs(2 * counts[key]["T"] / n[key] - 1) for key in counts)
    report: dict[str, Any] = {
        **star,
        "p1": p,
        "principal_branch": {
            "max_abs_sin_phi": largest,
            "margin_rad": math.pi / 2 - math.asin(min(1.0, largest)),
            "branch_ambiguous": largest > BRANCH_LIMIT,
        },
        "phase_rad": phase,
        "phase_shift_rad": shift,
        "additivity_residual_rad": residual,
        "residual_sigma_rad": sigma,
        "residual_z": residual / sigma,
        "drivers": drivers,
        "target_phase_by_driver_outcome": conditioned,
    }
    if len(references) > 1:
        report["reference_p1_by_batch"] = {
            batch: counts[(batch, "none")]["T"] / n[(batch, "none")] for batch in references
        }
    return report


def load_series(run_dirs: list[Path]) -> tuple[dict[str, Any], list[Acquisition]]:
    """The shared manifest fields and every acquisition of one series, keyed by (batch, file).

    A run directory holds one submitted batch; a manifest without a batch name
    is a single-batch run.
    """
    shared: dict[str, Any] | None = None
    acquisitions: list[Acquisition] = []
    seen: set[tuple[str, str]] = set()
    for run_dir in run_dirs:
        cases = json.loads((run_dir / "cases.json").read_text(encoding="utf-8"))
        fields = {k: v for k, v in cases.items() if k not in {"batch", "circuits", "schema"}}
        if shared is None:
            shared = fields
        elif fields != shared:
            raise SystemExit(f"{run_dir}/cases.json describes a different series")
        batch = cases.get("batch", "")
        for row in cases["circuits"]:
            if (batch, row["file"]) in seen:
                raise SystemExit(f"{run_dir}: {batch}/{row['file']} appears twice in the series")
            seen.add((batch, row["file"]))
            shots = json.loads((run_dir / "raw" / f"{row['file']}.json").read_text(encoding="utf-8"))
            acquisitions.append((batch, row, shots))
    if shared is None:
        raise SystemExit("a series needs at least one run directory")
    return shared, acquisitions


def analyze(run_dirs: list[Path]) -> dict[str, Any]:
    """Estimates from the raw shots run_dir/raw/<file>.json of every batch of one series."""
    cases, acquisitions = load_series(run_dirs)
    backend = cases["backend"]
    if backend not in BACKENDS:
        raise ValueError(f"unknown result bit order for backend {backend}")
    report: dict[str, Any] = {
        "schema": "qi-crosstalk-teleport-analysis-v2",
        "backend": cases["backend"],
        # The phase-domain residual, the driver crosstalk and conditioning
        # fields and their thresholds were fixed after the hardware data
        # arrived; cases.json preregistered the circuits only.
        "claim_kind": f"exploratory reanalysis, {'emulator control' if backend in EMULATORS else 'hardware'}",
        "config_order_note": "the four configurations ran as sequential jobs, so drift between jobs enters every "
        "cross-configuration difference",
    }
    if len(run_dirs) > 1:
        report["batch_note"] = (
            "each driven configuration's shift subtracts the reference of its own batch; the driver rows compare "
            "acquisitions across batches, so calibration drift between batches enters them"
        )
    if "stars" in cases:
        additivity = [a for a in acquisitions if a[1]["kind"] == "additivity"]
        configs = {row["config"] for _, row, _ in additivity}
        if configs != set(CONFIGS):
            raise SystemExit(f"the series holds configurations {sorted(configs)}; analyze every batch together")
        report["additivity"] = [star_report(star, additivity, backend) for star in cases["stars"]]
    tele = []
    # Tuna-5's star graph has no four-qubit path. Missing teleport data is
    # optional only when the manifest declares no teleportation paths.
    teleport = [shots for _, row, shots in acquisitions if row["file"] == "teleport.cq"]
    if cases["paths"] and not teleport:
        raise KeyError("teleport.cq")
    shots = teleport[0] if cases["paths"] else []
    for path in cases["paths"]:
        _, _, flips = INPUTS[path["input"]]
        corrected = post = post_ok = 0
        for s in shots:
            m_i, m_p1, d = bit(s, path["I"], backend), bit(s, path["P1"], backend), bit(s, path["D"], backend)
            flip = (m_p1 if "x" in flips else 0) ^ (m_i if "z" in flips else 0)
            # Inputs 0, + and +i map to outcome 0 after the basis rotation; input 1 maps to 1.
            want = 1 if path["input"] == "1" else 0
            corrected += (d ^ flip) == want
            if m_i == 0 and m_p1 == 0:
                post += 1
                post_ok += d == want
        tele.append(
            {
                **path,
                "corrected_fidelity": corrected / len(shots),
                "corrected_ci95": wilson(corrected, len(shots)),
                "postselected_fidelity": post_ok / post if post else None,
                "postselected_ci95": wilson(post_ok, post),
                "postselected_fraction": post / len(shots),
            }
        )
    report["teleport"] = tele
    # Each input ran on its own path, so no single channel has a Bloch-sphere
    # average; this mean assumes a path-independent channel and carries no
    # state-preparation or readout correction.
    axes = {"z": ("0", "1"), "x": ("+",), "y": ("+i",)}
    by_input = {t["input"]: t["corrected_fidelity"] for t in tele}
    if all(label in by_input for labels in axes.values() for label in labels):
        per_axis = [sum(by_input[label] for label in labels) / len(labels) for labels in axes.values()]
        report["teleport_cross_axis_mean_assuming_path_independence"] = sum(per_axis) / len(per_axis)
    return report


def write_series(directory: Path, files: dict[str, str], shots: dict[str, list[str]]) -> list[Path]:
    """Lay a generated series out as one run directory per batch, each circuit's raw shots from shots[file]."""
    runs = []
    for name in sorted({path.split("/")[0] for path in files if "/" in path}):
        run = directory / name
        (run / "raw").mkdir(parents=True)
        cases = json.loads(files[f"{name}/cases.json"])
        (run / "cases.json").write_text(json.dumps(cases))
        for row in cases["circuits"]:
            (run / "raw" / f"{row['file']}.json").write_text(json.dumps(shots[row["file"]]))
        runs.append(run)
    return runs


def series_fixture(directory: Path) -> None:
    """A Tuna-17 series whose two references carry the same shots reproduces the single-batch analysis."""
    catalogue = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    selected = [row for row in catalogue["backend_types"] if row["identifier"] == "tuna_17"]
    files = build({"backend_types": selected})["tuna_17"]
    for name, text in files.items():
        if name.endswith("cases.json") and "/" in name:
            if len(json.loads(text)["circuits"]) > HARDWARE_BATCH_CIRCUITS:
                raise AssertionError(f"{name} exceeds the hardware batch limit")
    pattern = ["00000000000000000", "00000000000000001", "10000000000010000", "01000000001100000"]
    shots = {
        f"additivity-{c}.cq": [pattern[(i + k) % len(pattern)] for i in range(k + 5)] for k, c in enumerate(CONFIGS)
    }
    shots["teleport.cq"] = pattern
    runs = write_series(directory / "series", files, shots)
    single = directory / "single"
    (single / "raw").mkdir(parents=True)
    manifest = json.loads(files["batch-00/cases.json"])
    del manifest["batch"]
    manifest["circuits"] = [{"file": f"additivity-{c}.cq", "kind": "additivity", "config": c} for c in CONFIGS]
    manifest["circuits"].append({"file": "teleport.cq", "kind": "teleport"})
    (single / "cases.json").write_text(json.dumps(manifest))
    for name, value in shots.items():
        (single / "raw" / f"{name}.json").write_text(json.dumps(value))
    merged, alone = analyze(runs), analyze([single])
    if "batch_note" not in merged or merged["additivity"][0].pop("reference_p1_by_batch", None) is None:
        raise AssertionError("a multi-batch series did not record its per-batch references")
    del merged["batch_note"]
    # batch-00's reference enters the A and B shifts and batch-01's the AB
    # shift, so the residual weighs the two independent references 2 and -1.
    n = {c: len(shots[f"additivity-{c}.cq"]) for c in CONFIGS}
    sigma = math.sqrt(1 / n["A"] + 1 / n["B"] + 1 / n["AB"] + 4 / n["none"] + 1 / n["none"])
    for star in merged["additivity"]:
        star.pop("reference_p1_by_batch", None)
        star.pop("residual_z")
        if not math.isclose(star.pop("residual_sigma_rad"), sigma):
            raise AssertionError("a series residual does not weigh its two references independently")
    for star in alone["additivity"]:
        star.pop("residual_z")
        star.pop("residual_sigma_rad")
    if merged != alone:
        raise AssertionError("a series with equal references differs from its single-batch analysis")
    for partial in ([runs[0], runs[0]], runs[:1]):
        try:
            analyze(partial)
        except SystemExit:
            pass
        else:
            raise AssertionError("a series accepted a repeated or missing batch")


def regression_fixture(backend: str) -> str:
    """Synthetic decoder inputs, without simulating or claiming circuit execution."""
    with tempfile.TemporaryDirectory(prefix="qi-teleport-analysis-fixture-") as scratch:
        directory = Path(scratch)
        if backend == "series":
            series_fixture(directory)
            return backend
        (directory / "raw").mkdir()
        if backend == "tuna_5":
            catalogue = json.loads(CATALOGUE.read_text(encoding="utf-8"))
            selected = [row for row in catalogue["backend_types"] if row["identifier"] == backend]
            files = build({"backend_types": selected})[backend]
            if any(name.endswith("teleport.cq") for name in files) or sum(n.endswith(".cq") for n in files) != 5:
                raise AssertionError("the Tuna-5 fixture no longer represents an additivity-only series")
            shots = ["00000", "00001", "00010", "00100", "01000", "10000"]
            runs = write_series(directory, files, {f"additivity-{c}.cq": shots for c in CONFIGS})
            cases = json.loads(files["batch-00/cases.json"])
            report = analyze(runs)
            if report["teleport"] or len(report["additivity"]) != len(cases["stars"]):
                raise AssertionError("an additivity-only manifest did not produce its complete analysis")
            # A declared teleportation path still requires the corresponding
            # acquisition; do not silently skip a genuinely missing circuit.
            for run in runs:
                manifest = json.loads((run / "cases.json").read_text())
                manifest["paths"] = [{"I": 0, "P1": 1, "P2": 2, "D": 3, "input": "0"}]
                (run / "cases.json").write_text(json.dumps(manifest))
            try:
                analyze(runs)
            except KeyError as error:
                if error.args != ("teleport.cq",):
                    raise
            else:
                raise AssertionError("a declared teleportation path accepted an absent acquisition")
            return backend
        paths: list[dict[str, Any]] = [
            {"I": 4 * index, "P1": 4 * index + 1, "P2": 4 * index + 2, "D": 4 * index + 3, "input": label}
            for index, label in enumerate(INPUT_ORDER)
        ]
        shots = []
        for m_i, m_p1, spectator in itertools.product((0, 1), repeat=3):
            state = [0] * 17
            state[16] = 1  # A nonsymmetric marker makes bit reversal observable.
            for path in paths:
                flips = INPUTS[path["input"]][2]
                flip = (m_p1 if "x" in flips else 0) ^ (m_i if "z" in flips else 0)
                state[path["I"]], state[path["P1"]], state[path["P2"]] = m_i, m_p1, spectator
                state[path["D"]] = int(path["input"] == "1") ^ flip
            encoded = "".join(map(str, state))
            shots.append(encoded if backend == "Rydberg" else encoded[::-1])
        cases = {
            "schema": "qi-crosstalk-teleport-cases-v1",
            "backend": backend,
            "nqubits": 17,
            "shots": len(shots),
            "paths": paths,
            "circuits": [{"file": "teleport.cq", "kind": "teleport"}],
        }
        (directory / "cases.json").write_text(json.dumps(cases))
        (directory / "raw/teleport.cq.json").write_text(json.dumps(shots))
        report = analyze([directory])
        for row in report["teleport"]:
            if (row["corrected_fidelity"], row["postselected_fidelity"], row["postselected_fraction"]) != (1, 1, 0.25):
                raise AssertionError(f"{backend} decoded a known teleportation outcome incorrectly")
        return backend


def self_test() -> None:
    backends = ["tuna_5", "tuna_17", "QXsinglenodesimulator", "Rydberg", "series"]
    if ordered_map(regression_fixture, backends, min_items=1) != backends:
        raise AssertionError("the decoder regressions did not complete")
    print(
        "qi crosstalk/teleport self-test: Tuna-5 additivity-only, missing acquisition, QX/Tuna/Ry bit order "
        "and batched-series reduction pass"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--analyze", type=Path, nargs="+", metavar="RUN_DIR", help="the batches of one series")
    mode.add_argument(
        "--replay-series",
        type=Path,
        nargs="+",
        metavar="FILE RUN_DIR",
        help="recompute the analysis FILE over the run directories of one series and compare bytes",
    )
    mode.add_argument("--replay", type=Path, nargs="+", help="recompute each run's analysis.json and compare bytes")
    parser.add_argument("--out", type=Path, help="with --analyze: the analysis file (default RUN_DIR/analysis.json)")
    mode.add_argument("--self-test", action="store_true")
    parser.add_argument("--catalogue", type=Path, default=CATALOGUE)
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.analyze:
        if len(args.analyze) > 1 and args.out is None:
            parser.error("--analyze over several batches needs --out")
        text = json.dumps(analyze(args.analyze), indent=1) + "\n"
        (args.out or args.analyze[0] / "analysis.json").write_text(text, encoding="utf-8")
        print(text, end="")
        return 0
    if args.replay_series:
        out, *runs = args.replay_series
        if not runs:
            parser.error("--replay-series needs FILE and at least one RUN_DIR")
        if out.read_text(encoding="utf-8") != json.dumps(analyze(runs), indent=1) + "\n":
            raise SystemExit(f"{out} differs from the recomputation over its {len(runs)} batches")
        print(f"{out}: {len(runs)} batches reproduce their series analysis")
        return 0
    if args.replay:
        for run in args.replay:
            if (run / "analysis.json").read_text(encoding="utf-8") != json.dumps(analyze([run]), indent=1) + "\n":
                raise SystemExit(f"{run}/analysis.json differs from its recomputation")
        print(f"qi analyses: {len(args.replay)} runs reproduce their analysis.json")
        return 0
    catalogue = json.loads(args.catalogue.read_text(encoding="utf-8"))
    if args.write:
        write(args.write, catalogue)
    else:
        check(args.check, catalogue)
    return 0


if __name__ == "__main__":
    sys.exit(main())
