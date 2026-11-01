"""Belenos per-seed mesh persistence: replay one retained mode-swap layout group after a recalibration.

The interleaved mode-swap case (docs/design/belenos-mode-swap-interleaved-case.md) measured, on 2026-10-31, the
single-click algebra-mode share of every packed block under four compiled meshes per layout (the primary seed, run
twice, and three replicate seeds). This case replays the packed layout of block set 4, the one set whose six blocks
are all half blocks (p_algebra 1/2, the class with the larger mesh error), with the same circuit parameters and
compilation seeds, and asks two questions in order:

1. Identity: does each seed return its retained `computed_circuit` after the chip's recalibrations?
2. Persistence: when it does, does each mesh's deviation from its block's four-mesh mean recur?

Usage:
  belenos_mesh_persistence.py --build          write results/quandela/cases/belenos_mesh_persistence/job-00
  belenos_mesh_persistence.py --check          rebuild the case and compare it byte for byte
  belenos_mesh_persistence.py --power --seed qrng:<draw>#<index> --out PATH
  belenos_mesh_persistence.py --analyze RUN    write RUN/analysis.json from a collected run
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
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
from scipy.stats import chi2, t  # noqa: E402

import qrng_seeds  # noqa: E402
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
        "question": "whether each retained compilation seed of the packed set-4 layout group returns its retained "
        "computed_circuit after the chip's recalibrations, and whether each mesh's deviation from its block's "
        "four-mesh mean recurs",
        "observable": swap.preregistered()["observable"],
        "identity": "per seed, the sha256 of the returned computed_circuit against the retained digest of the same "
        "circuit_params and compilation_seed; both primary repeats must return the primary digest. Any mismatch "
        "reads 'seed does not reproduce its mesh' and withholds the persistence statistic",
        "drift": "per block, the two-sample z of the two new primary repeats; D = sum z^2 on 6 degrees of freedom; "
        f"drift detected at p < {DRIFT_ALPHA} withholds the persistence reading",
        "statistic": "per block b and mesh j (the pooled primary repeats, then each replicate), e = a - mean over "
        "the four meshes of a, in the retained window and in the new one; T = sum over b and j of e_old e_new",
        "null": "no persistence: within each block the new mesh labels are exchangeable; the exact one-sided "
        "p-value is the share of the 24^6 within-block relabelings with T at or above the observed T",
        "slope": "beta = T / sum e_old^2, the regression through the origin of e_new on e_old, with its one-sided "
        f"{1 - ALPHA:.2f} upper bound beta + t(0.95, dof) s / sqrt(sum e_old^2), s^2 the residual variance on "
        "24 - 6 - 1 = 17 degrees of freedom",
        "reading": f"persists when p < {ALPHA}; redrawn when p >= {ALPHA} and the upper bound on beta is below "
        f"{USEFUL_SLOPE}; indeterminate otherwise",
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
    per = swap.SECONDS_PER_ITERATION + (swap.SAMPLES_PER_ITERATION - swap.MEASURED_SAMPLES) / (
        swap.CLOCK_HZ * swap.MIN_GLOBAL_EFFICIENCY
    )
    return per * len(ORDER)


def credit_ceiling() -> float:
    return 1.0 + swap.SHOTS_PER_ITERATION * 1e-6


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
    return {"blocks": out, "digests": first}


# Statistic ------------------------------------------------------------------------------------------------------


def centered(shares: np.ndarray) -> np.ndarray:
    """Each block's shares minus its mean over the meshes (rows are blocks)."""
    return shares - shares.mean(axis=1, keepdims=True)


def relabeled_values(e_old: np.ndarray, e_new: np.ndarray) -> list[np.ndarray]:
    """Per block, T_b under each of the m! relabelings of the new meshes."""
    m = e_old.shape[1]
    perms = np.array(list(itertools.permutations(range(m))))
    return [e_new[b][perms] @ e_old[b] for b in range(e_old.shape[0])]


def exact_upper_p(per_block: Sequence[np.ndarray], observed: float) -> float:
    """P(sum of one independent draw per block >= observed), exact by splitting the blocks in two halves."""
    half = len(per_block) // 2

    def sums(parts: Sequence[np.ndarray]) -> np.ndarray:
        total = np.zeros(1)
        for values in parts:
            total = (total[:, None] + values[None, :]).ravel()
        return total

    left, right = sums(per_block[:half]), np.sort(sums(per_block[half:]))
    tol = 1e-12
    count = right.size - np.searchsorted(right, observed - left - tol, side="left")
    return float(count.sum() / (left.size * right.size))


def persistence(old: np.ndarray, new: np.ndarray) -> dict[str, Any]:
    """T, its exact within-block relabeling p-value and the slope with its one-sided upper bound."""
    e_old, e_new = centered(old), centered(new)
    observed = float((e_old * e_new).sum())
    p = exact_upper_p(relabeled_values(e_old, e_new), observed)
    sxx = float((e_old**2).sum())
    beta = observed / sxx
    dof = e_old.size - e_old.shape[0] - 1
    s2 = float(((e_new - beta * e_old) ** 2).sum()) / dof
    upper = beta + float(t.ppf(1 - ALPHA, dof)) * math.sqrt(s2 / sxx)
    return {"statistic": observed, "p_value": p, "slope": beta, "slope_upper": upper, "dof": dof}


def read(result: Mapping[str, Any]) -> str:
    if result["p_value"] < ALPHA:
        return "persists"
    if result["slope_upper"] < USEFUL_SLOPE:
        return "redrawn"
    return "indeterminate"


def shares(cells: Sequence[Mapping[str, int]]) -> np.ndarray:
    return np.array([c["hit"] / c["n"] for c in cells])


# Power ----------------------------------------------------------------------------------------------------------


def power_trial(item: tuple[np.ndarray, np.ndarray]) -> str:
    old, new = item
    return read(persistence(old, new))


def power(seed: Any, sigma: float) -> dict[str, Any]:
    """Reading frequencies under a persistence slope beta at the retained counts.

    The new true share of block b and mesh j is the retained block mean plus a slot shift d_b ~ N(0, SLOT_SHIFT_SD^2)
    plus beta e_old + sqrt(1 - beta^2) eta, eta ~ N(0, sigma^2) a fresh mesh error, then a binomial draw at the
    retained count of that cell (the primary cell pools two repeats)."""
    group = retained_group()["blocks"]
    old = np.array([shares(b["cells"]) for b in group])
    counts = np.array([[c["n"] for c in b["cells"]] for b in group])
    e_old = centered(old)
    means = old.mean(axis=1, keepdims=True)
    rows = []
    for beta, child in zip(POWER_SLOPES, np.random.SeedSequence(seed).spawn(len(POWER_SLOPES)), strict=True):
        rng = np.random.default_rng(child)
        shape = (POWER_REPLICATES, *old.shape)
        shift = rng.normal(0.0, SLOT_SHIFT_SD, (POWER_REPLICATES, old.shape[0], 1))
        eta = rng.normal(0.0, sigma, shape)
        truth = np.clip(means + shift + beta * e_old + math.sqrt(1 - beta**2) * eta, 0.0, 1.0)
        new = rng.binomial(np.broadcast_to(counts, shape), truth) / counts
        readings = ordered_map(power_trial, [(old, new[i]) for i in range(POWER_REPLICATES)], min_items=64)
        rows.append(
            {
                "slope": beta,
                **{r: readings.count(r) / POWER_REPLICATES for r in ("persists", "redrawn", "indeterminate")},
            }
        )
    return {"replicates": POWER_REPLICATES, "mesh_sigma": sigma, "slot_shift_sd": SLOT_SHIFT_SD, "rows": rows}


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
    new_cells: dict[int, dict[tuple[str, int], dict[str, Any]]] = {}
    digests = []
    for index, setting in enumerate(manifest["settings"]):
        entry = bound[index]
        circuit = (entry.get("result_fields") or {}).get("computed_circuit")
        digests.append(hashlib.sha256(json.dumps(circuit, sort_keys=True).encode()).hexdigest() if circuit else None)
        new_cells[index] = {share["key"]: share for share in swap.block_shares(setting, entry["counts"])}
    expected = [retained["digests"][0], *retained["digests"][1:], retained["digests"][0]]
    identity = [
        {"setting": s["name"], "same_mesh": d == e}
        for s, d, e in zip(manifest["settings"], digests, expected, strict=True)
    ]
    record: dict[str, Any] = {"schema": "belenos-mesh-persistence-v1", "identity": identity, "run": run.name}
    if not all(row["same_mesh"] for row in identity):
        record["reading"] = "seed does not reproduce its mesh"
        return record
    blocks = []
    old, new = [], []
    drift = 0.0
    for block in retained["blocks"]:
        key = (block["block"][0], block["block"][1])
        firsts = [new_cells[i][key] for i in range(len(ORDER))]
        primary = swap.merge([firsts[0], firsts[4]])
        cells = [primary, firsts[1], firsts[2], firsts[3]]
        z = swap.two_sample_z((firsts[0]["hit"], firsts[0]["n"]), (firsts[4]["hit"], firsts[4]["n"]))
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
    record["persistence"] = persistence(o, n)
    slots = np.array([b["slot"] for b in blocks])
    record["secondary"] = {
        "slots_4_and_5": persistence(o[slots >= 4], n[slots >= 4]) if (slots >= 4).sum() >= 2 else None,
        "without_slot_5": persistence(o[slots != 5], n[slots != 5]),
    }
    record["reading"] = read(record["persistence"])
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--build", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--power", action="store_true")
    mode.add_argument("--analyze", type=Path, metavar="RUN")
    qrng_seeds.add_seed_argument(parser, "--seed", help="power-simulation seed, qrng:<draw>#<index>")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.build or args.check:
        return build(check_only=args.check)
    if args.power:
        if args.seed is None or args.out is None:
            parser.error("--power needs --seed and --out")
        analysis = json.loads(
            next((ROOT / "results/quandela/runs").glob(RUN_GLOB)).joinpath("analysis.json").read_text()
        )
        sigma = float(analysis["mesh_variance"]["classes"]["half"]["sigma"])
        record = {
            "schema": "belenos-mesh-persistence-power-v1",
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
