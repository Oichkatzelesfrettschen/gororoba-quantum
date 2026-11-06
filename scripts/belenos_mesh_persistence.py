"""Belenos per-seed mesh persistence: replay one retained mode-swap layout group after a recalibration.

The interleaved mode-swap case (docs/design/belenos-mode-swap-interleaved-case.md) measured, on 2026-10-31, the
single-click algebra-mode share of every packed block under four compiled meshes per layout (the primary seed, run
twice, and three replicate seeds). This case replays the packed layout of block set 4, the one set whose six blocks
are all half blocks (p_algebra 1/2, the class with the larger mesh error), with the same circuit parameters and
compilation seeds, and asks two questions in order:

1. Identity: does each seed return the mesh of its retained `computed_circuit` after the chip's recalibrations?
2. Persistence: when it does, does each mesh's deviation from its block's four-mesh mean recur?

Usage:
  belenos_mesh_persistence.py --build          write results/quandela/cases/belenos_mesh_persistence/job-00
  belenos_mesh_persistence.py --check          rebuild the case and compare it byte for byte
  belenos_mesh_persistence.py --power --seed qrng:<draw>#<index> --out PATH
  belenos_mesh_persistence.py --analyze RUN    write RUN/analysis.json from a collected run
  belenos_mesh_persistence.py --plan-check PLAN  refuse a scheduler plan outside the written case
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))
sys.path.insert(0, str(ROOT / "scripts"))

import belenos_mode_swap_interleaved as swap  # noqa: E402
from qd_platform import sha256_bytes  # noqa: E402
from scipy.stats import chi2  # noqa: E402

import qrng_seeds  # noqa: E402
from mesh_selection import centered, persistence, persistence_reading  # noqa: E402
from parallel import ordered_map  # noqa: E402

FAMILY = "belenos_mesh_persistence"
JOB = "job-00"
CASE = ROOT / "results/quandela/cases" / FAMILY / JOB
DESIGN = "docs/design/belenos-mesh-persistence-case.md"
SOURCE_CASES = ROOT / "results/quandela/cases" / swap.FAMILY
# Block set 4 is the only set whose six blocks are all half blocks; its packed layout ran in job-09 and job-10.
BLOCK_SET = 4
LAYOUT = "packed"
# The replay order keeps the retained relative order: primary, the three replicates, primary.
ORDER = (("primary", 0), ("replicate", 0), ("replicate", 1), ("replicate", 2), ("primary", 1))
MESHES = (("primary", None), ("replicate", 0), ("replicate", 1), ("replicate", 2))
RUN_GLOB = "*-qpu_belenos-belenos_mode_swap_interleaved-job-*"

# Identifiers, not new randomness: the seeds that reproduce the retained meshes.
PRIMARY_SEED = swap.COMPILATION_SEEDS[swap.seed_index(BLOCK_SET, LAYOUT)]

ALPHA = 0.05
DRIFT_ALPHA = 0.01
# A persistence slope below this fraction of a mesh's deviation recurring makes seed selection worthless.
USEFUL_SLOPE = 0.5
POWER_SLOPES = (0.0, 0.25, 0.5, 0.75, 1.0)
POWER_REPLICATES = 2000
# A slot-level detection change common to every mesh of a block; the centered statistic cancels it.
SLOT_SHIFT_SD = 0.03
READINGS = ("persists", "recurs below the useful slope", "redrawn", "indeterminate")
# Largest entry difference between two decoded mesh unitaries that still reads as one mesh. Phases rounded to
# single precision move an entry by 4.5e-7, and a difference of 1e-4 moves a share by at most 2e-4 against a
# binomial error near 0.005; the meshes of two seeds of one layout differ by at least 1.2 in the retained window.
MESH_TOLERANCE = 1e-4


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"{FAMILY}: {message}")


def retained_rows() -> list[dict[str, Any]]:
    """The packed set-4 setting rows of the retained mode-swap cases, in ORDER."""
    found: dict[tuple[str, int], dict[str, Any]] = {}
    for job in ("job-09", "job-10"):
        manifest = json.loads((SOURCE_CASES / job / "cases.json").read_text(encoding="utf-8"))
        for row in manifest["settings"]:
            if row["block_set"] == BLOCK_SET and row["layout"] == LAYOUT:
                found[(row["arm"], row["repeat"])] = row
    require(sorted(found) == sorted(ORDER), f"retained packed set-{BLOCK_SET} rows are {sorted(found)}")
    require(found[("primary", 0)]["compilation_seed"] == PRIMARY_SEED, "primary seed differs from the retained case")
    return [found[key] for key in ORDER]


def settings() -> list[dict[str, Any]]:
    """The replay settings: each retained row unchanged except its position in the new job and its name."""
    out = []
    for index, row in enumerate(retained_rows()):
        replay = {**row, "observation_index": index, "name": f"replay-{row['name']}"}
        for field in ("circuit_params", "compilation_seed", "blocks", "operator", "column", "source"):
            require(replay[field] == row[field], f"{row['name']}: {field} departs from the retained row")
        out.append(replay)
    return out


def preregistered() -> dict[str, Any]:
    return {
        "question": "whether each retained compilation seed of the packed set-4 layout group returns the mesh of its "
        "retained computed_circuit after the chip's recalibrations, and whether each mesh's deviation from its block's "
        "four-mesh mean recurs",
        "observable": swap.preregistered()["observable"],
        "identity": "per seed, the unitary decoded from the returned computed_circuit against the unitary decoded "
        "from the retained computed_circuit of the same circuit_params and compilation_seed; one mesh when the "
        f"largest entry difference is at most {MESH_TOLERANCE:g}, with the sha256 comparison of the serialized "
        "circuits recorded beside it; both primary repeats must return the primary mesh. Any mismatch reads 'seed "
        "does not reproduce its mesh' and withholds the persistence statistic",
        "drift": "per block, the two-sample z of the two new primary repeats; D = sum z^2 on 6 degrees of freedom; "
        f"drift detected at p < {DRIFT_ALPHA} withholds the persistence reading",
        "statistic": "per block b and mesh j (the pooled primary repeats, then each replicate), e = a - mean over "
        "the four meshes of a, in the retained window and in the new one; T = sum over b and j of e_old e_new",
        "null": "no persistence: within each block the new mesh labels are exchangeable; the exact one-sided "
        "p-value is the share of the 24^6 within-block relabelings with T at or above the observed T",
        "slope": "beta = T / sum e_old^2, the regression through the origin of e_new on e_old. For a slope b the "
        "residuals e_new - b e_old are exchangeable within each block and independent between blocks, and q(b) "
        "is the share of the 24^6 "
        "within-block relabelings of the residuals whose cross product with e_old lies at or below the observed "
        f"one; the one-sided {1 - ALPHA:.2f} upper bound on beta is the largest b with q(b) >= {ALPHA}",
        "reading": f"q({USEFUL_SLOPE}) < {ALPHA} places the upper bound on beta below {USEFUL_SLOPE}: recurs below "
        f"the useful slope when also p < {ALPHA}, redrawn when p >= {ALPHA}. With q({USEFUL_SLOPE}) >= {ALPHA}: "
        f"persists when p < {ALPHA} and beta >= {USEFUL_SLOPE}; indeterminate otherwise",
        "secondary": "the same T restricted to slots 4 and 5 (chip modes 16 to 23, the teleportation layout's modes) "
        "and with slot 5 excluded, reported without a reading",
    }


def documents() -> dict[str, bytes]:
    source = (SOURCE_CASES / "job-09" / "circuit.json").read_bytes()
    rows = settings()
    manifest = {
        "schema": "qd-hypercomplex-cases-v1",
        "family": FAMILY,
        "job": JOB,
        "platforms": [swap.PLATFORM, "sim:belenos"],
        "command": "sample_count",
        "gate_form": "template",
        "iterations": len(rows),
        "min_detected_photons": 1,
        "max_samples": swap.SAMPLES_PER_ITERATION * len(rows),
        "max_shots": swap.SHOTS_PER_ITERATION * len(rows),
        "max_duration": swap.MAX_DURATION,
        "mitigations": [],
        "output_modes": swap.MODES,
        "design": DESIGN,
        "settings": rows,
        "circuit": {"file": "circuit.json", "sha256": sha256_bytes(source)},
        "preregistered": preregistered(),
    }
    return {"cases.json": (json.dumps(manifest, indent=1) + "\n").encode(), "circuit.json": source}


def bound_seconds() -> float:
    """The duration bound of the mode-swap case for one 30,000-sample iteration, times the iterations."""
    return swap.iteration_seconds() * len(ORDER)


def credit_ceiling() -> float:
    return 1.0 + swap.SHOTS_PER_ITERATION * 1e-6


# The mode-swap job-00 whose lowest global efficiency (swap.MIN_GLOBAL_EFFICIENCY) the duration bound takes; its
# plan-time record transmittance scales that efficiency to another record (plan_check).
EFFICIENCY_RUN = "results/quandela/runs/2026-10-31T060538Z-qpu_belenos-belenos_mode_swap_interleaved-job-00"


def transmittance_floor(clock_mhz: float) -> float:
    """The record transmittance (%) at which the case's iterations still fit DURATION_MARGIN x MAX_DURATION.

    The measured swap.SECONDS_PER_ITERATION already holds its first MEASURED_SAMPLES samples at job-00's efficiency,
    and a slower record stretches those too, so the floor charges the whole measured iteration as setup and every one
    of SAMPLES_PER_ITERATION samples at 1 / (clock x efficiency). hypothesis: the global efficiency scales with the
    record's Transmittance (%) from job-00's plan-time value, which job-00's MIN_GLOBAL_EFFICIENCY accompanied."""
    slack = swap.DURATION_MARGIN * swap.MAX_DURATION / len(ORDER) - swap.SECONDS_PER_ITERATION
    require(slack > 0, "the measured iteration alone exceeds the duration margin")
    efficiency = swap.SAMPLES_PER_ITERATION / (clock_mhz * 1e6 * slack)
    retained = json.loads((ROOT / EFFICIENCY_RUN / "submission.json").read_text(encoding="utf-8"))["perfs_at_plan"]
    return float(retained["Transmittance (%)"]) * efficiency / swap.MIN_GLOBAL_EFFICIENCY


def plan_check(plan: Mapping[str, Any]) -> str:
    """Refuse a scheduler plan that leaves the written case: another case, platform or ceiling, an admitted status
    other than running, or a record whose clock and transmittance put the iterations past the duration margin."""
    require(plan.get("cases_sha256") == sha256_bytes((CASE / "cases.json").read_bytes()), "the plan holds another case")
    require(plan.get("platform") == "qpu:belenos", f"the plan targets {plan.get('platform')}")
    ceiling = plan.get("credit_ceiling")
    require(
        isinstance(ceiling, int | float) and not isinstance(ceiling, bool) and 0 <= ceiling <= credit_ceiling(),
        f"credit ceiling {ceiling!r} exceeds {credit_ceiling()}",
    )
    # qd_platform.plan always admits available and appends the statuses the case names, here running.
    admitted = plan.get("admitted_statuses")
    require(admitted in (["available"], ["available", "running"]), f"admitted statuses {admitted}")
    perfs = plan.get("perfs_at_plan") or {}
    figures = [perfs.get("Clock (MHz)"), perfs.get("Transmittance (%)")]
    require(
        all(isinstance(v, int | float) and not isinstance(v, bool) and math.isfinite(v) and v > 0 for v in figures),
        f"the record lacks a positive clock or transmittance: {figures!r}",
    )
    clock, transmittance = (float(v) for v in figures if isinstance(v, int | float))
    floor = transmittance_floor(clock)
    require(transmittance >= floor, f"transmittance {transmittance} % below the duration floor {floor:.2f} %")
    return f"plan inside the written case: transmittance {transmittance} % against the floor {floor:.2f} %"


def build(check_only: bool) -> int:
    require(bound_seconds() <= swap.DURATION_MARGIN * swap.MAX_DURATION, f"bound {bound_seconds():.0f} s too long")
    for name, data in documents().items():
        path = CASE / name
        if check_only:
            require(path.exists() and path.read_bytes() == data, f"{path.relative_to(ROOT)} differs from the rebuild")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print(f"{FAMILY} {JOB}: bound {bound_seconds():.0f} s, credit ceiling {credit_ceiling():.2f}")
    return 0


# Retained window -------------------------------------------------------------------------------------------------


def retained_group() -> dict[str, Any]:
    """Per block of the group: slot, the four retained mesh cells (hit, n) and their computed_circuit digests."""
    runs = sorted((ROOT / "results/quandela/runs").glob(RUN_GLOB))
    data = swap.collect_cells(swap.load_runs(runs))
    blocks = sorted(key for key, info in data["info"].items() if info["set"] == BLOCK_SET)
    out = []
    for key in blocks:
        cells = data["cells"]
        primary = [cells[(key, LAYOUT, "primary", r)] for r in (0, 1)]
        require(primary[0]["mesh"] == primary[1]["mesh"], f"retained primary repeats of {key} hold two meshes")
        meshes = [swap.merge(primary)] + [cells[(key, LAYOUT, "replicate", r)] for r in (0, 1, 2)]
        digests = [primary[0]["mesh"]] + [cells[(key, LAYOUT, "replicate", r)]["mesh"] for r in (0, 1, 2)]
        out.append(
            {
                "block": list(key),
                "slot": primary[0]["slot"],
                "cells": [{"hit": c["hit"], "n": c["n"]} for c in meshes],
                "primary_cells": [{"hit": c["hit"], "n": c["n"]} for c in primary],
                "digests": digests,
            }
        )
    first = out[0]["digests"]
    require(all(b["digests"] == first for b in out), "the blocks of one iteration report different digests")
    return {"blocks": out, "digests": first, "circuits": retained_circuits(runs, first)}


def circuit_digest(circuit: Any) -> str:
    return hashlib.sha256(json.dumps(circuit, sort_keys=True).encode()).hexdigest()


def retained_circuits(runs: Sequence[Path], digests: Sequence[str]) -> list[Any]:
    """The retained computed_circuit of each mesh in MESHES order, each held to the digest of its cells."""
    found: dict[tuple[str, int], Any] = {}
    for item in swap.load_runs(list(runs)):
        bound, _ = swap.bind_iterations(item["manifest"]["settings"], item["results"])
        for index, setting in enumerate(item["manifest"]["settings"]):
            if setting["block_set"] == BLOCK_SET and setting["layout"] == LAYOUT and index in bound:
                fields = bound[index].get("result_fields") or {}
                found[(setting["arm"], setting["repeat"])] = fields.get("computed_circuit")
    circuits = [found[(arm, repeat or 0)] for arm, repeat in MESHES]
    require(
        [circuit_digest(c) for c in circuits] == list(digests), "a retained computed_circuit departs from its digest"
    )
    return circuits


def mesh_unitary(circuit: Any) -> np.ndarray:
    """The unitary of a returned computed_circuit, decoded by Perceval's deserializer."""
    from perceval.serialization import deserialize

    return np.asarray(deserialize(circuit).compute_unitary())


def mesh_distance(first: Any, second: Any) -> float:
    """Largest entry difference between two computed circuits' unitaries: 0 for equal serialized circuits, and
    infinite for two mode counts."""
    if first == second:
        return 0.0
    a, b = mesh_unitary(first), mesh_unitary(second)
    return float(np.abs(a - b).max()) if a.shape == b.shape else math.inf


# Statistic ------------------------------------------------------------------------------------------------------
# The statistic lives in gororoba_quantum/mesh_selection.py (centered, persistence, persistence_reading); this
# script supplies the case's thresholds ALPHA and USEFUL_SLOPE.


def shares(cells: Sequence[Mapping[str, int]]) -> np.ndarray:
    return np.array([c["hit"] / c["n"] for c in cells])


# Power ----------------------------------------------------------------------------------------------------------
# Index 2 of docs/evidence/anu_qrng/draw-2026-11-01T054809Z.json (21344) is spent: it seeded the power record of
# this case under a slope bound the case no longer uses, and its reserved row in the seed ledger keeps the value
# out of later use.


def power_trial(item: tuple[np.ndarray, np.ndarray]) -> str:
    old, new = item
    return persistence_reading(persistence(old, new, ALPHA, USEFUL_SLOPE, bound=False), ALPHA, USEFUL_SLOPE)


def error_models(sigma: float, e_old: np.ndarray) -> list[tuple[str, np.ndarray, float]]:
    """The fresh-error models of the power record: a name, the error size of each block, and the share of the
    error variance that one term per mesh carries across all blocks."""
    flat = np.full(e_old.shape[0], sigma)
    spreads = e_old.std(axis=1, ddof=1)
    return [
        ("one error size for every block", flat, 0.0),
        ("each block's retained spread", spreads, 0.0),
        ("one error size, half of its variance shared by a mesh's blocks", flat, 0.5),
        ("one error size, all of its variance shared by a mesh's blocks", flat, 1.0),
    ]


def power(seed: Any, sigma: float) -> dict[str, Any]:
    """Reading frequencies under a persistence slope beta at the retained counts, per fresh-error model.

    The new true share of block b and mesh j is the retained block mean plus a slot shift d_b ~ N(0, SLOT_SHIFT_SD^2)
    plus beta e_old + sqrt(1 - beta^2) eta, then a binomial draw at the retained count of that cell (the primary cell
    pools two repeats). The fresh mesh error eta has the model's block size s_b and shared share w:
    eta = s_b (sqrt(w) u_j + sqrt(1 - w) v_bj) with u and v standard normal. Every model and slope draws from its
    own child of the seed."""
    group = retained_group()["blocks"]
    old = np.array([shares(b["cells"]) for b in group])
    counts = np.array([[c["n"] for c in b["cells"]] for b in group])
    e_old = centered(old)
    means = old.mean(axis=1, keepdims=True)
    models = error_models(sigma, e_old)
    children = iter(np.random.SeedSequence(seed).spawn(len(models) * len(POWER_SLOPES)))
    shape = (POWER_REPLICATES, *old.shape)
    out = []
    for name, sizes, shared in models:
        rows = []
        for beta in POWER_SLOPES:
            rng = np.random.default_rng(next(children))
            shift = rng.normal(0.0, SLOT_SHIFT_SD, (POWER_REPLICATES, old.shape[0], 1))
            per_mesh = rng.normal(0.0, 1.0, (POWER_REPLICATES, 1, old.shape[1]))
            per_cell = rng.normal(0.0, 1.0, shape)
            eta = sizes[:, None] * (math.sqrt(shared) * per_mesh + math.sqrt(1 - shared) * per_cell)
            truth = np.clip(means + shift + beta * e_old + math.sqrt(1 - beta**2) * eta, 0.0, 1.0)
            new = rng.binomial(np.broadcast_to(counts, shape), truth) / counts
            readings = ordered_map(power_trial, [(old, new[i]) for i in range(POWER_REPLICATES)], min_items=64)
            rows.append({"slope": beta, **{r: readings.count(r) / POWER_REPLICATES for r in READINGS}})
        out.append({"error": name, "block_sizes": [float(x) for x in sizes], "shared_share": shared, "rows": rows})
    return {"replicates": POWER_REPLICATES, "mesh_sigma": sigma, "slot_shift_sd": SLOT_SHIFT_SD, "models": out}


# Analysis -------------------------------------------------------------------------------------------------------


def analyze(run: Path) -> dict[str, Any]:
    raw = (run / "cases.json").read_bytes()
    require(raw == (CASE / "cases.json").read_bytes(), f"{run}/cases.json differs from the frozen case")
    manifest = json.loads(raw)
    results = json.loads((run / "results.json").read_text(encoding="utf-8"))
    bound, uncounted = swap.bind_iterations(manifest["settings"], results)
    require(len(bound) == len(ORDER) and not uncounted, f"{len(bound)} of {len(ORDER)} iterations returned counts")
    retained = retained_group()
    # block_shares returns a setting's blocks in slot order; the retained group is keyed by block, so cells match
    # by block key, never by position.
    # Each iteration's histogram reduces independently, so the reductions run through parallel.ordered_map.
    work = [(setting, bound[index]["counts"]) for index, setting in enumerate(manifest["settings"])]
    reduced = ordered_map(swap.iteration_shares, work, min_items=1)
    new_cells: dict[int, dict[tuple[str, int], dict[str, Any]]] = {}
    circuits = []
    for index, block_cells in enumerate(reduced):
        circuits.append((bound[index].get("result_fields") or {}).get("computed_circuit"))
        new_cells[index] = {share["key"]: share for share in block_cells}
    record: dict[str, Any] = {"schema": "belenos-mesh-persistence-v2", "run": run.name}
    unreported = [s["name"] for s, c in zip(manifest["settings"], circuits, strict=True) if not c]
    if unreported:
        # A result without computed_circuit carries no mesh to compare, which is no evidence of a changed mesh.
        record["reading"] = "an iteration returned no computed_circuit"
        record["unreported"] = unreported
        return record
    # The decoded unitary decides the identity, so a change of the provider's serialization alone keeps the mesh;
    # the digest comparison is recorded beside it.
    expected = [retained["circuits"][0], *retained["circuits"][1:], retained["circuits"][0]]
    identity = []
    for setting, circuit, kept in zip(manifest["settings"], circuits, expected, strict=True):
        distance = mesh_distance(circuit, kept)
        identity.append(
            {
                "setting": setting["name"],
                "same_mesh": distance <= MESH_TOLERANCE,
                "same_bytes": circuit_digest(circuit) == circuit_digest(kept),
                "unitary_distance": distance,
            }
        )
    record["identity"] = identity
    if not all(row["same_mesh"] for row in identity):
        record["reading"] = "seed does not reproduce its mesh"
        return record
    blocks = []
    old, new = [], []
    drift = 0.0
    for block in retained["blocks"]:
        key = (block["block"][0], block["block"][1])
        firsts = [new_cells[i][key] for i in range(len(ORDER))]
        empty = [manifest["settings"][i]["name"] for i in range(len(ORDER)) if firsts[i]["n"] == 0]
        if empty:
            # A share and a drift contrast need a count: an iteration without single-click counts in a block is a
            # missing cell, and the reading is withheld rather than computed on the cells that remain.
            record["reading"] = "an iteration returned no single-click counts in a block"
            record["missing"] = {"block": block["block"], "settings": empty}
            return record
        primary = swap.merge([firsts[0], firsts[4]])
        cells = [primary, firsts[1], firsts[2], firsts[3]]
        z = swap.two_sample_z((firsts[0]["hit"], firsts[0]["n"]), (firsts[4]["hit"], firsts[4]["n"]))
        # With both counts positive, two_sample_z returns None only for two equal and certain shares: no drift.
        drift += (z or 0.0) ** 2
        old.append(shares(block["cells"]))
        new.append(shares(cells))
        blocks.append({"block": block["block"], "slot": block["slot"], "old": list(old[-1]), "new": list(new[-1])})
    drift_p = float(chi2.sf(drift, len(blocks)))
    record.update({"blocks": blocks, "drift": {"statistic": drift, "dof": len(blocks), "p_value": drift_p}})
    if drift_p < DRIFT_ALPHA:
        record["reading"] = "drift within the new job withholds the reading"
        return record
    o, n = np.array(old), np.array(new)
    record["persistence"] = persistence(o, n, ALPHA, USEFUL_SLOPE)
    slots = np.array([b["slot"] for b in blocks])
    late = slots >= 4
    record["secondary"] = {
        "slots_4_and_5": persistence(o[late], n[late], ALPHA, USEFUL_SLOPE) if late.sum() >= 2 else None,
        "without_slot_5": persistence(o[slots != 5], n[slots != 5], ALPHA, USEFUL_SLOPE),
    }
    record["reading"] = persistence_reading(record["persistence"], ALPHA, USEFUL_SLOPE)
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--build", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--power", action="store_true")
    mode.add_argument("--analyze", type=Path, metavar="RUN")
    mode.add_argument("--plan-check", type=Path, metavar="PLAN")
    qrng_seeds.add_seed_argument(parser, "--seed", help="power-simulation seed, qrng:<draw>#<index>")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.build or args.check:
        return build(check_only=args.check)
    if args.plan_check:
        try:
            print(plan_check(json.loads(args.plan_check.read_text(encoding="utf-8"))))
        except (ValueError, OSError) as error:
            raise SystemExit(str(error)) from None
        return 0
    if args.power:
        if args.seed is None or args.out is None:
            parser.error("--power needs --seed and --out")
        # Every retained run of the mode-swap case carries the same half-block mesh sigma; the first in sorted
        # order supplies it and a run that disagrees stops the calculation.
        sigmas = [
            float(json.loads((run / "analysis.json").read_text())["mesh_variance"]["classes"]["half"]["sigma"])
            for run in sorted((ROOT / "results/quandela/runs").glob(RUN_GLOB))
        ]
        require(bool(sigmas) and len(set(sigmas)) == 1, f"the retained runs hold mesh sigmas {sorted(set(sigmas))}")
        sigma = sigmas[0]
        record = {
            "schema": "belenos-mesh-persistence-power-v2",
            "seed_source": qrng_seeds.seed_record(
                "scripts/belenos_mesh_persistence.py", "--seed", "belenos-mesh-persistence-power", args.seed_source
            ),
            "bound_seconds": bound_seconds(),
            "credit_ceiling": credit_ceiling(),
            "power": power(args.seed, sigma),
        }
        args.out.write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        return 0
    record = analyze(args.analyze)
    (args.analyze / "analysis.json").write_text(json.dumps(record, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(record["reading"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
