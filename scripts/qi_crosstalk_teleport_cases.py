"""cQASM 3.0 cases for Quantum Inspire backends: spectator-drive phase additivity and transported-pair teleportation.

Two experiments, each a transmon translation of a spin-qubit result:

- Spectator-drive phase additivity (Wu et al., Nat. Phys., doi:10.1038/s41567-026-03466-2).
  A target T runs X90, an explicit idle of WAIT_CYCLES 20 ns cycles, and the
  quadrature Y90, so its outcome probability P1 = (1 + sin phi)/2 reads the
  accumulated z rotation Rz(phi) with standard error 1/sqrt(shots) at every
  P1. Neighbors A and B either idle or apply
  DRIVE_PULSES X gates (an even count, so each returns to |0>) inside that
  idle. Configurations none, A, B and AB run as four circuits of one batch.
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

--write DIR writes each backend's circuits and a cases.json manifest (qubit
roles, configurations, expected ideal outcomes, shots) from the backend
catalogue snapshot. --check DIR regenerates every file in memory from the
retained catalogue and compares bytes, offline. --analyze RESULTS writes the
additivity and teleportation estimates from collected raw shots.

--replay RUN_DIR... recomputes each retained analysis.json from its raw
shots and compares bytes, offline.

Usage: "$PYTHON" scripts/qi_crosstalk_teleport_cases.py
       (--write DIR | --check DIR | --analyze RUN_DIR | --replay RUN_DIR...) [--catalogue FILE]
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
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
    """identifier -> {file name -> text}, including cases.json."""
    out: dict[str, dict[str, str]] = {}
    for backend in catalogue["backend_types"]:
        ident = backend["identifier"]
        if ident not in BACKENDS:
            continue
        shots, additivity, dialect = BACKENDS[ident]
        n = backend["nqubits"]
        files: dict[str, str] = {}
        cases: dict[str, Any] = {
            "schema": "qi-crosstalk-teleport-cases-v1",
            "backend": ident,
            "backend_type_id": backend["id"],
            "nqubits": n,
            "shots": min(shots, backend["max_number_of_shots"]),
            "drive_pulses": DRIVE_PULSES,
            "wait_cycles": WAIT_CYCLES,
            "circuits": [],
        }
        if additivity:
            stars = disjoint_stars(backend)
            cases["stars"] = [{"T": t, "A": a, "B": b} for t, a, b in stars]
            for config in CONFIGS:
                name = f"additivity-{config}.cq"
                files[name] = additivity_circuit(n, stars, config)
                cases["circuits"].append({"file": name, "kind": "additivity", "config": config})
        paths = disjoint_paths(backend, len(INPUT_ORDER))
        if not paths:
            # A star coupling map (Tuna-5) has no four-qubit path.
            cases["paths"] = []
            files["cases.json"] = finish(cases, files)
            out[ident] = files
            continue
        cases["paths"] = [
            {"I": i, "P1": p1, "P2": p2, "D": d, "input": label}
            for (i, p1, p2, d), label in zip(paths, INPUT_ORDER, strict=False)
        ]
        files["teleport.cq"] = teleport_circuit(n, paths, dialect)
        cases["circuits"].append({"file": "teleport.cq", "kind": "teleport"})
        files["cases.json"] = finish(cases, files)
        out[ident] = files
    return out


def finish(cases: dict[str, Any], files: dict[str, str]) -> str:
    for row in cases["circuits"]:
        row["sha256"] = hashlib.sha256(files[row["file"]].encode()).hexdigest()
    return json.dumps(cases, indent=1) + "\n"


def write(directory: Path, catalogue: dict[str, Any]) -> None:
    for ident, files in build(catalogue).items():
        (directory / ident).mkdir(parents=True, exist_ok=True)
        for name, text in files.items():
            (directory / ident / name).write_text(text, encoding="utf-8")
        print(f"{ident}: {len(files) - 1} circuits")


def check(directory: Path, catalogue: dict[str, Any]) -> None:
    count = 0
    for ident, files in build(catalogue).items():
        for name, text in files.items():
            path = directory / ident / name
            if path.read_text(encoding="utf-8") != text:
                raise SystemExit(f"{path}: differs from the regenerated case")
            count += 1
    print(f"qi cases: {count} files match their regeneration")


def bit(shot: str, qubit: int) -> int:
    """Bit of a QX or Tuna result string, whose rightmost character is qubit 0 (the Ry emulator reverses it)."""
    return int(shot[len(shot) - 1 - qubit])


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (centre - half, centre + half)


def phase_of(p1: float) -> float:
    """X90, Rz(phi), Y90 gives P1 = (1 + sin phi)/2; the binomial standard error of phi is 1/sqrt(n) at every P1."""
    return math.asin(max(-1.0, min(1.0, 2 * p1 - 1)))


def two_proportion_z(k1: int, n1: int, k2: int, n2: int) -> float:
    p1, p2 = k1 / n1, k2 / n2
    pooled = (k1 + k2) / (n1 + n2)
    se = math.sqrt(pooled * (1 - pooled) * (1 / n1 + 1 / n2))
    return (p2 - p1) / se if se else 0.0


def star_report(star: dict[str, int], raw: dict[str, list[str]]) -> dict[str, Any]:
    """Target phases, pairwise residual, driver crosstalk and driver-conditioned target phases for one star."""
    counts: dict[str, dict[str, int]] = {}
    n: dict[str, int] = {}
    conditioned: dict[str, dict[str, Any]] = {}
    for config in CONFIGS:
        shots = raw[f"additivity-{config}.cq"]
        n[config] = len(shots)
        counts[config] = {role: sum(bit(s, star[role]) for s in shots) for role in ("T", "A", "B")}
        # A driver-conditioned target phase separates a ZZ phase, which follows
        # the driver's state, from a drive-induced shift, which does not.
        conditioned[config] = {}
        for role in ("A", "B"):
            if role not in config:
                continue
            split = {}
            for outcome in (0, 1):
                sub = [s for s in shots if bit(s, star[role]) == outcome]
                if sub:
                    p1 = sum(bit(s, star["T"]) for s in sub) / len(sub)
                    split[str(outcome)] = {"shots": len(sub), "target_p1": p1, "target_phase_rad": phase_of(p1)}
            conditioned[config][str(star[role])] = split
    p = {c: counts[c]["T"] / n[c] for c in CONFIGS}
    phase = {c: phase_of(p[c]) for c in CONFIGS}
    shift = {c: phase[c] - phase["none"] for c in ("A", "B", "AB")}
    residual = shift["AB"] - shift["A"] - shift["B"]
    sigma = math.sqrt(sum(1 / n[c] for c in CONFIGS))
    drivers = {}
    for role in ("A", "B"):
        k_single, k_both = counts[role][role], counts["AB"][role]
        p_single = k_single / n[role]
        row: dict[str, Any] = {
            "qubit": star[role],
            "p1_driven_alone": p_single,
            "p1_driven_with_other": k_both / n["AB"],
            "simultaneous_change": k_both / n["AB"] - p_single,
            "simultaneous_change_z": two_proportion_z(k_single, n[role], k_both, n["AB"]),
        }
        # An even X count returns an ideal driver to |0>. Depolarizing,
        # relaxation and readout error keep P1 at or below about 1/2, so a
        # larger P1 requires a coherent rotation error; for a pure per-gate
        # over-rotation eps, P1 = sin^2(DRIVE_PULSES eps / 2) and the smallest
        # solution bounds |eps| from below.
        if p_single > 0.5:
            row["overrotation_lower_bound_rad_per_x"] = 2 * math.asin(math.sqrt(p_single)) / DRIVE_PULSES
        drivers[role] = row
    return {
        **star,
        "p1": p,
        "phase_rad": phase,
        "phase_shift_rad": shift,
        "additivity_residual_rad": residual,
        "residual_sigma_rad": sigma,
        "residual_z": residual / sigma,
        "drivers": drivers,
        "target_phase_by_driver_outcome": conditioned,
    }


def analyze(run_dir: Path) -> dict[str, Any]:
    """Estimates from raw shots in run_dir/raw/<file>.json (a list of bit strings per circuit)."""
    cases = json.loads((run_dir / "cases.json").read_text(encoding="utf-8"))
    raw = {row["file"]: json.loads((run_dir / "raw" / f"{row['file']}.json").read_text()) for row in cases["circuits"]}
    report: dict[str, Any] = {
        "schema": "qi-crosstalk-teleport-analysis-v2",
        "backend": cases["backend"],
        # The phase-domain residual, the driver crosstalk and conditioning
        # fields and their thresholds were fixed after the hardware data
        # arrived; cases.json preregistered the circuits only.
        "claim_kind": "exploratory reanalysis, hardware",
        "config_order_note": "the four configurations ran as sequential jobs, so drift between jobs enters every "
        "cross-configuration difference",
    }
    if "stars" in cases:
        report["additivity"] = [star_report(star, raw) for star in cases["stars"]]
    tele = []
    # A star coupling map (Tuna-5) has no four-qubit path and so no teleport circuit.
    shots = raw.get("teleport.cq", [])
    for path in cases["paths"] if shots else []:
        _, _, flips = INPUTS[path["input"]]
        corrected = post = post_ok = 0
        for s in shots:
            m_i, m_p1, d = bit(s, path["I"]), bit(s, path["P1"]), bit(s, path["D"])
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path)
    mode.add_argument("--check", type=Path)
    mode.add_argument("--analyze", type=Path)
    mode.add_argument("--replay", type=Path, nargs="+", help="recompute each run's analysis.json and compare bytes")
    parser.add_argument("--catalogue", type=Path, default=CATALOGUE)
    args = parser.parse_args()
    if args.analyze:
        text = json.dumps(analyze(args.analyze), indent=1) + "\n"
        (args.analyze / "analysis.json").write_text(text, encoding="utf-8")
        print(text, end="")
        return 0
    if args.replay:
        for run in args.replay:
            if (run / "analysis.json").read_text(encoding="utf-8") != json.dumps(analyze(run), indent=1) + "\n":
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
