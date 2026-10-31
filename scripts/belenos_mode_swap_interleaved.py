"""Belenos interleaved mode swap: the packed and swapped box-kite layouts alternate inside one job.

docs/design/belenos-mode-swap-interleaved-case.md fixes the request. Registry claim qd-belenos-packed-mode-swap found
that moving a packed sign block three of six 4-mode slots changes its single-click algebra-mode share a, but the
packed and swapped series ran as separate jobs about an hour apart, so placement and drift were confounded. Here each
block set k of box_kite_photonic_packed/job-0k runs as template iterations in the order packed, swapped, swapped,
packed (ABBA). The two repeats of one layout carry the same circuit parameters and the same compilation_seed, so they
request the same compiled mesh and their difference is drift; the packed-swapped difference is placement. Both
layouts put the six photons on chip modes 0, 4, 8, 12, 16 and 20, so one template circuit serves every iteration.

JOBS assigns block sets (0, 1), (2, 3) and (4,) to job-00, job-01 and job-02. Set 5 holds two photons, not six, and
stays out. Each set-layout takes one compilation seed: in job order, set order and layout order (packed, swapped),
indices 0 to 9 of the ANU QRNG draw docs/evidence/anu_qrng/draw-2026-10-31T043029Z.json, registered in
docs/evidence/qrng_seeds/allocations.json.

--check rebuilds the cases, compares them with the retained bytes, binds every iteration through
qd_platform.template_experiment, and requires each iteration's template unitary to equal the block-diagonal unitary of
the retained packed or swapped circuit.json within 1e-9. --build JOB writes a case. --analyze RUN writes the per-block
shares, the drift and placement statistics and the slot predictor of scripts/qd_packed_mode_swap_analysis.py.

Usage:
  "$PYTHON" scripts/belenos_mode_swap_interleaved.py [--check | --build JOB | --analyze RUN]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

from hypercomplex_cases import encoded, photonic_template  # noqa: E402
from qd_packed_mode_swap_analysis import decide  # noqa: E402
from qd_platform import sha256_bytes, template_experiment  # noqa: E402
from scipy.stats import chi2  # noqa: E402

from parallel import ordered_map  # noqa: E402

MODES = 24
SLOT_WIDTH = 4
FAMILY = "belenos_mode_swap_interleaved"
CASES = ROOT / "results/quandela/cases" / FAMILY
SOURCES = ROOT / "results/quandela/cases"
LAYOUTS = {"packed": "box_kite_photonic_packed", "swapped": "box_kite_photonic_packed_swapped"}
DESIGN = "docs/design/belenos-mode-swap-interleaved-case.md"
PLATFORM = "qpu:belenos"
JOBS = {"job-00": (0, 1), "job-01": (2, 3), "job-02": (4,)}
ORDER = ("packed", "swapped", "swapped", "packed")
SEED_DRAW = "docs/evidence/anu_qrng/draw-2026-10-31T043029Z.json"
# One seed per (set, layout) in job, set and layout order; both repeats of a layout take it.
COMPILATION_SEEDS = (41251, 50785, 63940, 45911, 11390, 34773, 25508, 5306, 15866, 64854)
SAMPLES_PER_ITERATION = 15000
SHOTS_PER_ITERATION = 45000
MAX_DURATION = 300
# A block whose share moves by more than Z_CRITICAL two-sample standard errors moved, the criterion of
# qd_packed_mode_swap_analysis.
Z_CRITICAL = 4.5
DRIFT_ALPHA = 0.01
TOLERANCE = 1e-9


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def q2(entry: list[str]) -> float:
    """The real number a + b sqrt(2) of a retained circuit entry [a, b]."""
    return float(Fraction(entry[0])) + float(Fraction(entry[1])) * math.sqrt(2)


def source(layout: str, block_set: int) -> tuple[dict[str, Any], dict[str, Any]]:
    directory = SOURCES / LAYOUTS[layout] / f"job-{block_set:02d}"
    manifest = json.loads((directory / "cases.json").read_text(encoding="utf-8"))
    circuit = json.loads((directory / "circuit.json").read_text(encoding="utf-8"))
    return manifest, circuit


def slot_unitaries(circuit: dict[str, Any]) -> dict[int, np.ndarray]:
    """The 4 x 4 real block of each slot, keyed by its first chip mode."""
    blocks = {}
    for component in circuit["components"]:
        at = int(component["at"])
        require(at % SLOT_WIDTH == 0, f"component at {at} is not slot-aligned")
        matrix = np.array([[q2(entry) for entry in row] for row in component["unitary"]])
        require(np.allclose(matrix.T @ matrix, np.eye(SLOT_WIDTH), atol=TOLERANCE), f"slot {at} is not orthogonal")
        blocks[at] = matrix
    return blocks


def full_unitary(blocks: dict[int, np.ndarray]) -> np.ndarray:
    full = np.eye(MODES, dtype=complex)
    for at, matrix in blocks.items():
        full[at : at + SLOT_WIDTH, at : at + SLOT_WIDTH] = matrix
    return full


def template(blocks: dict[int, np.ndarray]) -> tuple[dict[str, Any], dict[str, float]]:
    """Six independent 4-mode triangular meshes, one per slot, with globally numbered parameters; an empty slot takes
    the identity."""
    ops: list[list[Any]] = []
    parameters: dict[str, float] = {}
    for at in range(0, MODES, SLOT_WIDTH):
        mesh, values = photonic_template(blocks.get(at, np.eye(SLOT_WIDTH)).astype(complex))
        base = len(parameters)
        for kind, mode, index in mesh["ops"]:
            ops.append([kind, mode + at, None if index is None else index + base])
        for name, value in values.items():
            parameters[f"x{int(name[1:]) + base}"] = value
    return {"ops": ops, "parameters": len(parameters)}, parameters


def seed_index(job: str, block_set: int, layout: str) -> int:
    sets = [(name, s) for name, group in JOBS.items() for s in group]
    return 2 * sets.index((job, block_set)) + (0 if layout == "packed" else 1)


def rows(job: str) -> list[dict[str, Any]]:
    out = []
    for block_set in JOBS[job]:
        seen: dict[str, int] = {}
        for layout in ORDER:
            repeat = seen.get(layout, 0)
            seen[layout] = repeat + 1
            out.append({"block_set": block_set, "layout": layout, "repeat": repeat})
    return out


def build_setting(item: tuple[int, dict[str, Any], str]) -> tuple[dict[str, Any], dict[str, Any]]:
    index, row, job = item
    manifest, circuit = source(row["layout"], row["block_set"])
    blocks = slot_unitaries(circuit)
    mesh, parameters = template(blocks)
    full = full_unitary(blocks)
    photons = [mode for mode, n in enumerate(circuit["input_state"]) if n]
    setting = {
        "name": f"set{row['block_set']}-{row['layout']}-repeat{row['repeat']}",
        "observation_index": index,
        **row,
        "source": f"{LAYOUTS[row['layout']]}/job-{row['block_set']:02d}",
        "blocks": [
            {key: block[key] for key in ("config", "kind", "offset", "photons", "m", "t", "roles", "p_algebra")}
            for block in manifest["blocks"]
        ],
        "circuit_params": parameters,
        "compilation_seed": COMPILATION_SEEDS[seed_index(job, row["block_set"], row["layout"])],
        "column": [[float(value.real), float(value.imag)] for value in full[:, photons[0]]],
        "operator": encoded(full),
    }
    return {**mesh, "input_state": circuit["input_state"]}, setting


def documents(job: str) -> dict[str, bytes]:
    built = ordered_map(build_setting, [(index, row, job) for index, row in enumerate(rows(job))], min_items=1)
    shape = built[0][0]
    for index, (mesh, _) in enumerate(built):
        require(mesh == shape, f"iteration {index} needs another mesh or input than iteration 0")
    settings = [setting for _, setting in built]
    circuit = {
        "schema": "qd-template-circuit-v1",
        "modes": MODES,
        "input_state": shape["input_state"],
        "parameters": shape["parameters"],
        "ops": shape["ops"],
    }
    circuit_bytes = (json.dumps(circuit, indent=1) + "\n").encode()
    manifest = {
        "schema": "qd-hypercomplex-cases-v1",
        "family": FAMILY,
        "job": job,
        "platforms": [PLATFORM, "sim:belenos"],
        "command": "sample_count",
        "gate_form": "template",
        "iterations": len(settings),
        "min_detected_photons": 1,
        "max_samples": SAMPLES_PER_ITERATION * len(settings),
        "max_shots": SHOTS_PER_ITERATION * len(settings),
        "max_duration": MAX_DURATION,
        "mitigations": [],
        "output_modes": MODES,
        "design": DESIGN,
        "settings": settings,
        "circuit": {"file": "circuit.json", "sha256": sha256_bytes(circuit_bytes)},
        "preregistered": {
            "observable": "per block and iteration, a = (samples with exactly one click in the block's slot that "
            "land on an algebra mode) / (samples with exactly one click in the slot), the observable of "
            "scripts/qd_packed_mode_swap_analysis.py",
            "binding": "a result iteration binds to its setting by circuit_params and compilation_seed; the two "
            "repeats of one layout share both and bind in submission order",
            "mesh_identity": "the sha256 of each returned computed_circuit; the two repeats of a layout requested "
            "one mesh, and a repeat pair with different digests leaves its drift statistic descriptive",
            "drift": "per block and layout, z = (a_repeat1 - a_repeat0) / two-sample se; D = sum z^2 over blocks "
            "and layouts of mesh-identical pairs against chi-square with that many degrees of freedom; drift "
            f"detected when p < {DRIFT_ALPHA}",
            "placement": f"per block, z = (a_swapped - a_packed) / se on the pooled repeats; a block moved when "
            f"|z| > {Z_CRITICAL}",
            "slot_predictor": "decide() of scripts/qd_packed_mode_swap_analysis.py on the pooled packed and "
            "swapped shares: verdict block, slot, mixed or undetermined",
            "interpretation": "placement against drift for the residual of the packed box-kite series; a moved "
            "block with no drift places the residual on the chip modes",
        },
    }
    return {"cases.json": (json.dumps(manifest, indent=1) + "\n").encode(), "circuit.json": circuit_bytes}


def check_job(job: str) -> str:
    case = CASES / job
    retained = {name: (case / name).read_bytes() for name in ("cases.json", "circuit.json")}
    for name, data in documents(job).items():
        require(retained[name] == data, f"{case.relative_to(ROOT)}/{name} differs from the builder's bytes")
    manifest = json.loads(retained["cases.json"])
    circuit = json.loads(retained["circuit.json"])
    _, settings = template_experiment(manifest, circuit)
    require(len(settings) == 4 * len(JOBS[job]), f"{job}: {len(settings)} settings bound")
    import perceval as pcvl

    chip = pcvl.Circuit(MODES)
    parameters: dict[str, Any] = {}
    for kind, mode, index in circuit["ops"]:
        if kind == "BS":
            chip.add(mode, pcvl.BS.Rx(theta=parameters.setdefault(f"x{index}", pcvl.P(f"x{index}"))))
        else:
            chip.add(mode, pcvl.PS(parameters.setdefault(f"x{index}", pcvl.P(f"x{index}"))))
    for setting in settings:
        for name, parameter in parameters.items():
            parameter.set_value(setting["circuit_params"][name])
        unitary = np.asarray(chip.compute_unitary())
        _, retained_circuit = source(setting["layout"], setting["block_set"])
        expected = full_unitary(slot_unitaries(retained_circuit))
        require(np.abs(unitary - expected).max() < TOLERANCE, f"{setting['name']}: template unitary differs")
    return f"{FAMILY} {job}: {len(settings)} iterations bound to the retained packed and swapped unitaries"


def check() -> int:
    for line in ordered_map(check_job, sorted(JOBS), min_items=1):
        print(line)
    return 0


def build(job: str) -> int:
    out = CASES / job
    out.mkdir(parents=True, exist_ok=True)
    built = documents(job)
    for name, data in built.items():
        path = out / name
        require(not path.exists() or path.read_bytes() == data, f"{path.relative_to(ROOT)} differs from the rebuild")
        if not path.exists():
            path.write_bytes(data)
    print(f"{FAMILY} {job}: {out.relative_to(ROOT)} cases.json {sha256_bytes(built['cases.json'])}")
    return 0


def block_shares(setting: dict[str, Any], counts: dict[str, int]) -> list[dict[str, Any]]:
    parsed = [([int(v) for v in key.strip("|>").split(",")], count) for key, count in counts.items()]
    out = []
    for block in setting["blocks"]:
        offset, width = block["offset"], len(block["roles"])
        algebra = [k for k, role in enumerate(block["roles"]) if role != "dilation"]
        one = hit = 0
        for modes, count in parsed:
            window = modes[offset : offset + width]
            if sum(window) == 1:
                one += count
                hit += count if any(window[k] for k in algebra) else 0
        out.append({"key": (json.dumps(block["m"]), block["t"]), "slot": offset // SLOT_WIDTH, "n": one, "hit": hit})
    return out


def two_sample_z(first: tuple[int, int], second: tuple[int, int]) -> float | None:
    (h0, n0), (h1, n1) = first, second
    if not n0 or not n1:
        return None
    a0, a1 = h0 / n0, h1 / n1
    se = math.sqrt(a0 * (1 - a0) / n0 + a1 * (1 - a1) / n1)
    return (a1 - a0) / se if se > 0 else None


def analyze(run: Path) -> dict[str, Any]:
    manifest = json.loads((run / "cases.json").read_text(encoding="utf-8"))
    results = json.loads((run / "results.json").read_text(encoding="utf-8"))
    settings = manifest["settings"]
    pending: dict[str, list[int]] = {}
    for index, setting in enumerate(settings):
        key = json.dumps([setting["circuit_params"], setting["compilation_seed"]], sort_keys=True)
        pending.setdefault(key, []).append(index)
    bound: dict[int, dict[str, Any]] = {}
    uncounted = 0
    for entry in results.get("iterations") or []:
        if not entry.get("counts"):
            # qd_platform.result_summary writes a missing, malformed or error entry for an iteration a cut-short job
            # lost; it binds to nothing and its settings stay unbound.
            uncounted += 1
            continue
        request = entry.get("iteration") or {}
        key = json.dumps([request.get("circuit_params"), request.get("compilation_seed")], sort_keys=True)
        require(bool(pending.get(key)), "a result iteration binds to no remaining setting")
        bound[pending[key].pop(0)] = entry
    cells: dict[tuple[Any, ...], dict[str, Any]] = {}
    for index, entry in bound.items():
        setting = settings[index]
        if not entry.get("counts"):
            continue
        circuit = (entry.get("result_fields") or {}).get("computed_circuit")
        digest = hashlib.sha256(json.dumps(circuit, sort_keys=True).encode()).hexdigest() if circuit else None
        for share in block_shares(setting, entry["counts"]):
            cells[(share["key"], setting["layout"], setting["repeat"])] = {**share, "mesh": digest}
    blocks = sorted({key for key, _, _ in cells})
    drift_rows, statistic, dof = [], 0.0, 0
    for key in blocks:
        for layout in ("packed", "swapped"):
            first, second = cells.get((key, layout, 0)), cells.get((key, layout, 1))
            if first is None or second is None:
                continue
            z = two_sample_z((first["hit"], first["n"]), (second["hit"], second["n"]))
            same = first["mesh"] is not None and first["mesh"] == second["mesh"]
            drift_rows.append({"block": list(key), "layout": layout, "z": z, "same_mesh": same})
            if z is not None and same:
                statistic += z * z
                dof += 1
    pooled: dict[str, dict[tuple[str, int], dict[str, Any]]] = {"packed": {}, "swapped": {}}
    for key in blocks:
        for layout in ("packed", "swapped"):
            parts = [cells[(key, layout, r)] for r in (0, 1) if (key, layout, r) in cells]
            if parts:
                n, hit = sum(p["n"] for p in parts), sum(p["hit"] for p in parts)
                block = next(b for s in settings for b in s["blocks"] if (json.dumps(b["m"]), b["t"]) == key)
                pooled[layout][key] = {
                    "slot": parts[0]["slot"],
                    "p": float(Fraction(block["p_algebra"])),
                    "n": n,
                    "a": hit / n if n else None,
                    "hit": hit,
                }
    placement = []
    for key in blocks:
        if key in pooled["packed"] and key in pooled["swapped"]:
            p, s = pooled["packed"][key], pooled["swapped"][key]
            z = two_sample_z((p["hit"], p["n"]), (s["hit"], s["n"]))
            placement.append({"block": list(key), "from_slot": p["slot"], "to_slot": s["slot"], "z": z})
    moved = [row for row in placement if row["z"] is not None and abs(row["z"]) > Z_CRITICAL]
    complete = set(pooled["packed"]) == set(pooled["swapped"]) == set(blocks)
    try:
        slot = decide(pooled["packed"], pooled["swapped"]) if complete else None
    except ValueError as error:
        slot = {"verdict": "undetermined", "reason": str(error)}
    p_drift = float(chi2.sf(statistic, dof)) if dof else None
    return {
        "iterations_bound": len(bound),
        "iterations_uncounted": uncounted,
        "iterations_requested": len(settings),
        "drift": {
            "rows": drift_rows,
            "statistic": statistic,
            "dof": dof,
            "p_value": p_drift,
            "detected": None if p_drift is None else p_drift < DRIFT_ALPHA,
        },
        "placement": {"rows": placement, "moved": len(moved), "blocks": len(placement)},
        "slot_predictor": slot,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--check", action="store_true")
    group.add_argument("--build", choices=sorted(JOBS))
    group.add_argument("--analyze", type=Path)
    args = parser.parse_args()
    if args.build:
        return build(args.build)
    if args.analyze:
        record = analyze(args.analyze)
        (args.analyze / "analysis.json").write_text(json.dumps(record, indent=1, sort_keys=True) + "\n")
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
