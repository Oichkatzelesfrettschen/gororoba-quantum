"""Bias identity, forced blocks and block-profile census of the kernel-map nullity estimator N_hat.

The estimator (``pathion_kernel_map._pair_summary``, ``pathion_coset_block.pathion_coset_map_group``,
``pathion_parallel_coset.estimate``) reads the per-output contrasts c_obs(y) of one circuit pair and the ideal
contrasts c_ideal(y) = +-1 of the same circuit:

    V_hat = mean over bins of c_obs(y) sign(c_ideal(y)),    N_hat = (sum_y c_obs(y) / 2) / V_hat,

and N = (|B+| - |B-|) / 2 for the bin classes B+ = {y: c_ideal = +1} and B- = {y: c_ideal = -1}. With the class means
Vbar+ = mean over B+ of c_obs and Vbar- = mean over B- of -c_obs (so V_hat = (|B+| Vbar+ + |B-| Vbar-) / |B|) the
estimator obeys, for every c_obs and every block, whenever every bin is decided (|c_ideal| = 1):

    N_hat - N = |B+| |B-| / |B| * (Vbar+ - Vbar-) / V_hat.

Derivation. |B| (sum c_obs) = |B| (|B+| Vbar+ - |B-| Vbar-) and (|B+| - |B-|)(|B+| Vbar+ + |B-| Vbar-) differ by
2 |B+| |B-| (Vbar+ - Vbar-); dividing by 2 |B| V_hat gives the identity. A block of 2^d bins with N_b aligned pairs has
|B+| = 2^(d-1) + N_b and |B-| = 2^(d-1) - N_b, so the factor |B+||B-|/|B| is (4^(d-1) - N_b^2) / 2^d.

Forced reading. When B- is empty the factor vanishes: N_hat = |B+| / 2 = 2^(d-1) for any c_obs with |V_hat| above
``ZERO`` (the guard of the code), so a block whose pairs are all aligned reads 4 on 8 bins whatever the device did.
When B+ is empty the reading is -|B-| / 2. Every other block reads a function of the data.

Modes:
    "$PYTHON" nhat_bias.py --self-test            identity, mutation controls, loader agreement with the code
    "$PYTHON" nhat_bias.py --out DIR              write DIR/result.json (32-dimensional runs, census)
    "$PYTHON" nhat_bias.py --check DIR            recompute and compare with DIR/result.json
    NHAT_BIAS_SOURCE=CHECKOUT "$PYTHON" nhat_bias.py --wide RUN... --source-commit HASH --out-wide FILE
        the 64- and 128-dimensional runs; CHECKOUT is a tree that holds gororoba_quantum/pathion_wide_coset.py
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import math
import os
import re
import sys
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[4]
SOURCE = Path(os.environ.get("NHAT_BIAS_SOURCE", str(ROOT)))
sys.path.insert(0, str(SOURCE / "gororoba_quantum"))

import parallel  # noqa: E402
import pathion_coset_block as pcb  # noqa: E402
import pathion_kernel_map as pkm  # noqa: E402
import pathion_parallel_coset as ppc  # noqa: E402

SCHEMA = "nhat-bias-v1"
ZERO = pkm.ZERO
HERE = Path(__file__).resolve().parent
RUNS: dict[str, tuple[str, str]] = {
    "ibm_fez kernel map": ("results/live/2026-11-06T183538.809814Z", "kmap"),
    "ibm_fez coset map": ("results/live/2026-11-06T201037.234804Z", "cmap"),
    "ibm_marrakesh coset map": ("results/live/2026-11-06T200832.558771Z", "cmap"),
    "ibm_fez parallel coset": ("results/live/2026-11-07T042521.359670Z", "pcoset"),
    "ibm_kingston parallel coset": ("results/live/2026-11-07T042346.084449Z", "pcoset"),
}
OPERAND = r"e\d+(?:pe|me)\d+"
KMAP = re.compile(rf"^kmap_(?:(?P<kind>twin_|xor_)|flip(?P<flip>\d+)_)?(?P<op>{OPERAND})$")
CMAP = re.compile(rf"^(?P<fam>cmap|cflip|crep)_(?P<kind>twin_|xor_)?(?P<op>{OPERAND})_k(?P<k>\d+)$")
CONTROL = {None: "primary", "twin_": "twin", "xor_": "cocycle-free"}
# The pair compared in the block-profile claim: e1 + e24 (orbit V) against e1 + e18 (orbit VB).
PROFILE_PAIR = ("e1pe24", "e1pe18")
# The collector stores each measured law rounded to six decimals, so a per-replica N_hat rebuilt from collect.json
# differs from the collector's own summary by at most this much.
RECORD_ROUNDING = 1e-4


def expect(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def r12(value: float) -> float | None:
    """A float rounded to 12 decimals for the record; None for a value that is not finite."""
    return round(float(value), 12) if math.isfinite(float(value)) else None


@dataclass(frozen=True)
class Estimate:
    """The estimator of one contrast vector against its ideal signs, as the code computes it."""

    n_plus: int
    n_minus: int
    v_plus: float
    v_minus: float
    visibility: float
    half_sum: float
    n_hat: float

    @property
    def n_ideal(self) -> float:
        return (self.n_plus - self.n_minus) / 2.0

    @property
    def forced(self) -> bool:
        return self.n_plus == 0 or self.n_minus == 0

    def closed_form_bias(self) -> float:
        """|B+| |B-| / |B| (Vbar+ - Vbar-) / V_hat, zero when one class is empty."""
        if self.forced:
            return 0.0
        return (
            self.n_plus * self.n_minus / (self.n_plus + self.n_minus) * (self.v_plus - self.v_minus) / self.visibility
        )


def estimate(c_obs: np.ndarray, sign: np.ndarray) -> Estimate:
    """V_hat, half-sum and N_hat of ``pathion_coset_map_group.summarize``; every ideal bin must carry sign +-1."""
    expect(c_obs.ndim == 1 and c_obs.shape == sign.shape, "contrast and sign vectors differ in shape")
    expect(bool(np.all(np.abs(sign) == 1.0)), "every bin needs an ideal contrast of +1 or -1")
    plus, minus = sign > 0, sign < 0
    along = c_obs * sign
    visibility = float(np.mean(along))
    half_sum = float(c_obs.sum() / 2.0)
    return Estimate(
        n_plus=int(plus.sum()),
        n_minus=int(minus.sum()),
        v_plus=float(along[plus].mean()) if plus.any() else float("nan"),
        v_minus=float(along[minus].mean()) if minus.any() else float("nan"),
        visibility=visibility,
        half_sum=half_sum,
        n_hat=half_sum / visibility if abs(visibility) > ZERO else float("nan"),
    )


def exact_residual(c_obs: np.ndarray, sign: np.ndarray) -> Fraction:
    """N_hat - N - |B+||B-|/|B| (Vbar+ - Vbar-)/V_hat in exact rational arithmetic on the double-precision inputs."""
    c = [Fraction(float(x)) for x in c_obs]
    s = [int(x) for x in sign]
    n_plus, n_minus = s.count(1), s.count(-1)
    total = n_plus + n_minus
    along = [x * y for x, y in zip(c, s, strict=True)]
    v_plus = sum((a for a, y in zip(along, s, strict=True) if y > 0), Fraction(0)) / n_plus if n_plus else Fraction(0)
    v_minus = (
        sum((a for a, y in zip(along, s, strict=True) if y < 0), Fraction(0)) / n_minus if n_minus else Fraction(0)
    )
    visibility = sum(along, Fraction(0)) / total
    expect(visibility != 0, "an exactly zero visibility has no N_hat")
    n_hat = sum(c, Fraction(0)) / 2 / visibility
    return n_hat - Fraction(n_plus - n_minus, 2) - Fraction(n_plus * n_minus, total) * (v_plus - v_minus) / visibility


def equalize(c_obs: np.ndarray, sign: np.ndarray) -> np.ndarray:
    """c_obs with the B- bins rescaled so that Vbar- equals Vbar+ (the mutation that makes the contraction bin-flat)."""
    est = estimate(c_obs, sign)
    expect(not est.forced and est.v_minus != 0, "equalize needs two classes and a nonzero Vbar-")
    return np.where(sign < 0, c_obs * est.v_plus / est.v_minus, c_obs)


def contrast_of(plus: np.ndarray, minus: np.ndarray) -> np.ndarray:
    """c(y) = P_plus(s = 0 | y) - P_minus(s = 0 | y) of two 16-outcome (8-bin) laws, as ``pcb.output_contrast``."""
    return pcb.output_contrast(plus, minus)


# ----------------------------------------------------------------------------------------------- units of a run


@dataclass(frozen=True)
class Unit:
    """One circuit pair read over replicas: ideal signs per bin and observed contrasts per replica and bin."""

    key: str
    family: str
    operand: str
    control: str
    block: int | None
    sign: np.ndarray
    contrast: np.ndarray


def matched(pattern: re.Pattern[str], text: str) -> re.Match[str]:
    """The match of ``pattern`` on ``text``; a name the pattern does not describe raises."""
    found = pattern.match(text)
    if found is None:
        raise ValueError(f"unparsed circuit name {text!r}")
    return found


def run_units(kind: str, collect: Any) -> tuple[list[Unit], dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Units, the collect group, its ideal laws and the group object of one retained IBM run."""
    items = collect if isinstance(collect, list) else [collect]
    groups = [x for x in items if isinstance(x, dict) and "group" in x]
    expect(len(groups) == 1, f"expected one group entry, found {len(groups)}")
    entry = groups[0]
    factory = {
        "kmap": pkm.pathion_kernel_map_group,
        "cmap": pcb.pathion_coset_map_group,
        "pcoset": ppc.pathion_parallel_coset_group,
    }[kind]
    group = factory()
    expect(entry["group"] == group.name, f"{entry['group']} is not {group.name}")
    ideal = {m.name: np.asarray(m.ideal, dtype=float) for m in group.members}
    measured = {name: np.asarray(v, dtype=float) for name, v in entry["measured"].items()}
    units: list[Unit] = []
    names = sorted(name[: -len("_plus")] for name in measured if name.endswith("_plus"))
    for prefix in names:
        if f"{prefix}_minus" not in measured:
            continue
        plus, minus = measured[f"{prefix}_plus"], measured[f"{prefix}_minus"]
        if kind == "kmap":
            named = matched(KMAP, prefix)
            control = "mutation" if named["flip"] else CONTROL[named["kind"]]
            contrast_fn = pkm.output_contrast
            sign = np.sign(contrast_fn(ideal[f"{prefix}_plus"], ideal[f"{prefix}_minus"]))
            observed = np.array([contrast_fn(p, m) for p, m in zip(plus, minus, strict=True)])
            units.append(Unit(prefix, "kmap", named["op"], control, None, sign, observed))
            continue
        found = CMAP.match(prefix)
        if found is None:
            continue
        family = found["fam"]
        ip, im = ideal[f"{prefix}_plus"], ideal[f"{prefix}_minus"]
        if family == "cflip":
            plus, minus = (np.array([ppc.deflip(x) for x in arr]) for arr in (plus, minus))
            ip, im = ppc.deflip(ip), ppc.deflip(im)
        sign = np.sign(pcb.output_contrast(ip, im))
        observed = np.array([pcb.output_contrast(p, m) for p, m in zip(plus, minus, strict=True)])
        control = "cocycle-free" if found["kind"] == "xor_" else "twin" if found["kind"] == "twin_" else "primary"
        units.append(Unit(prefix, family, found["op"], control, int(found["k"]), sign, observed))
    return units, entry, ideal, {"group": group}


def analyze_unit(unit: Unit) -> dict[str, Any]:
    """Replica-mean estimate, per-replica estimates, the identity residuals and the forced-block statistics."""
    mean_c = unit.contrast.mean(axis=0)
    mean = estimate(mean_c, unit.sign)
    per = [estimate(row, unit.sign) for row in unit.contrast]
    rows = [mean_c, *unit.contrast]
    exact = max(abs(exact_residual(row, unit.sign)) for row in rows if abs(float(np.mean(row * unit.sign))) > 0)
    finite = [e for e in per if math.isfinite(e.n_hat)]
    float_residual = max(
        abs(e.n_hat - e.n_ideal - e.closed_form_bias()) for e in [mean, *per] if math.isfinite(e.n_hat)
    )
    replicas = unit.contrast.shape[0]
    along = unit.contrast * unit.sign
    if replicas >= 2:
        spread = along.std(axis=0, ddof=1) / math.sqrt(replicas)
        z_bins = along.mean(axis=0) / np.where(spread > 0, spread, np.nan)
        min_bin_z = float(np.nanmin(z_bins)) if np.isfinite(z_bins).any() else float("nan")
    else:
        min_bin_z = float("nan")
    gaps = [e.v_plus - e.v_minus for e in per if not e.forced]
    gap_mean = float(np.mean(gaps)) if gaps else float("nan")
    gap_se = float(np.std(gaps, ddof=1)) / math.sqrt(len(gaps)) if len(gaps) >= 2 else float("nan")
    n_hats = [e.n_hat for e in finite]
    return {
        "key": unit.key,
        "family": unit.family,
        "operand": unit.operand,
        "control": unit.control,
        "block": unit.block,
        "bins": int(unit.sign.size),
        "n_plus": mean.n_plus,
        "n_minus": mean.n_minus,
        "n_ideal": mean.n_ideal,
        "forced": mean.forced,
        "v_plus": r12(mean.v_plus),
        "v_minus": r12(mean.v_minus),
        "visibility": r12(mean.visibility),
        "n_hat": r12(mean.n_hat),
        "bias": r12(mean.n_hat - mean.n_ideal),
        "bias_closed_form": r12(mean.closed_form_bias()),
        "float_residual_max": float_residual,
        "exact_residual_max": str(exact),
        "replicas": replicas,
        "n_hat_mean_of_replicas": r12(float(np.mean(n_hats))) if n_hats else None,
        "n_hat_replica_se": r12(float(np.std(n_hats, ddof=1)) / math.sqrt(len(n_hats))) if len(n_hats) >= 2 else None,
        "n_hat_replicas": [r12(e.n_hat) for e in per],
        "visibility_replica_min": r12(min(e.visibility for e in per)),
        "visibility_replica_max": r12(max(e.visibility for e in per)),
        "class_gap_replica_mean": r12(gap_mean),
        "class_gap_replica_se": r12(gap_se),
        "forced_deviation_max": r12(max(abs(e.n_hat - e.n_ideal) for e in finite)) if mean.forced and finite else None,
        "forced_replicas_below_guard": sum(1 for e in per if not math.isfinite(e.n_hat)) if mean.forced else None,
        "min_bin_z": r12(min_bin_z),
        "sign_agreement": int(np.sum(np.sign(mean_c) == unit.sign)),
        "sign_count_half_sum": float(np.sum(np.sign(mean_c)) / 2.0),
    }


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def block_rows(units: list[dict[str, Any]], operand: str, control: str, family: str) -> list[dict[str, Any]]:
    rows = [u for u in units if u["operand"] == operand and u["control"] == control and u["family"] == family]
    return sorted(rows, key=lambda u: u["block"])


def operand_summary(units: list[dict[str, Any]], raw: list[Unit]) -> list[dict[str, Any]]:
    """Per operand and control of a coset run: block profile, forced share, and the 32-bin estimate of the same data."""
    out: list[dict[str, Any]] = []
    by_key = {u.key: u for u in raw}
    seen = sorted({(u["operand"], u["control"], u["family"]) for u in units if u["family"] != "kmap"})
    for operand, control, family in seen:
        blocks = block_rows(units, operand, control, family)
        mean_c = np.concatenate([by_key[b["key"]].contrast.mean(axis=0) for b in blocks])
        sign = np.concatenate([by_key[b["key"]].sign for b in blocks])
        full = estimate(mean_c, sign)
        forced = [b for b in blocks if b["forced"]]
        informative = [b for b in blocks if not b["forced"]]
        total = sum(b["n_hat"] for b in blocks)
        out.append(
            {
                "operand": operand,
                "control": control,
                "family": family,
                "blocks": [
                    {
                        "k": b["block"],
                        "n_ideal": b["n_ideal"],
                        "forced": b["forced"],
                        "n_hat": b["n_hat"],
                        "n_hat_mean_of_replicas": b["n_hat_mean_of_replicas"],
                        "n_hat_replica_se": b["n_hat_replica_se"],
                    }
                    for b in blocks
                ],
                "n_ideal": sum(b["n_ideal"] for b in blocks),
                "n_hat_block_sum": r12(total),
                "n_hat_block_sum_mean_of_replicas": r12(
                    float(np.mean([sum(b["n_hat_replicas"][i] for b in blocks) for i in range(blocks[0]["replicas"])]))
                ),
                "forced_blocks": len(forced),
                "informative_blocks": len(informative),
                "forced_part": sum(b["n_hat"] for b in forced),
                "informative_part": r12(sum(b["n_hat"] for b in informative)),
                "informative_ideal": sum(b["n_ideal"] for b in informative),
                "n_hat_32_bin": r12(full.n_hat),
                "v_plus_32_bin": r12(full.v_plus),
                "v_minus_32_bin": r12(full.v_minus),
                "bias_32_bin": r12(full.n_hat - full.n_ideal),
                "sign_count_nullity": float(np.sum(np.sign(mean_c)) / 2.0),
                "sign_agreement": int(sum(b["sign_agreement"] for b in blocks)),
            }
        )
    return out


def record_agreement(kind: str, entry: dict[str, Any], units: list[Unit]) -> float:
    """Largest difference between this module's per-replica N_hat and the collector's summary_per_replica value."""
    stored = entry["measured_statistics"]["summary_per_replica"]
    worst = 0.0
    for unit in units:
        key = f"{unit.key}_nullity_estimate" if kind == "kmap" or unit.family == "cmap" else None
        if key is None or key not in stored[0]:
            continue
        mine = [estimate(row, unit.sign).n_hat for row in unit.contrast]
        for value, record in zip(mine, stored, strict=True):
            theirs = float(record[key])
            if math.isnan(value) and math.isnan(theirs):
                continue
            worst = max(worst, abs(value - theirs))
    return worst


def stored_forced_corrected(kind: str, entry: dict[str, Any], units: list[dict[str, Any]]) -> dict[str, Any]:
    """The readout-corrected summary the collector stored for every forced cmap block, against its forced value."""
    corrected = entry["measured_summary_readout_corrected"]
    values = []
    for u in units:
        key = f"{u['key']}_nullity_estimate"
        if u["forced"] and u["family"] == "cmap" and key in corrected:
            values.append(abs(float(corrected[key]) - u["n_ideal"]))
    return {"blocks": len(values), "max_abs_deviation": r12(max(values)) if values else None}


def analyze_run(name: str) -> dict[str, Any]:
    rel, kind = RUNS[name]
    path = ROOT / rel / "collect.json"
    collect = json.loads(path.read_text())
    units, entry, _ideal, _ = run_units(kind, collect)
    analyzed = parallel.ordered_map(analyze_unit, units)
    record = {
        "name": name,
        "run": rel,
        "collect_sha256": sha256(path),
        "group": entry["group"],
        "backend": entry["backend"],
        "kind": kind,
        "replicas": analyzed[0]["replicas"],
        "units": analyzed,
        "agreement_with_collector_max": record_agreement(kind, entry, units),
        "stored_corrected_forced": stored_forced_corrected(kind, entry, analyzed),
    }
    if kind != "kmap":
        record["operands"] = operand_summary(analyzed, units)
    return record


# ----------------------------------------------------------------------------------------------- census


def block_profile(item: tuple[int, int, int], basis: tuple[int, ...]) -> tuple[int, ...]:
    """Aligned XOR pairs of e_i + t e_j in each coset of span(basis), cosets in ascending representative order."""
    i, j, t = item
    members = pcb.span(basis)
    reps = pcb.cosets(basis)
    k_matrix = pkm._left(i).T @ (t * pkm._left(j))
    m = i ^ j
    counts = dict.fromkeys(reps, 0)
    for k in range(pkm.DIM):
        if k < k ^ m and k_matrix[k ^ m, k] == k_matrix[k, k ^ m]:
            counts[min(k ^ v for v in members)] += 1
    return tuple(counts[r] for r in reps)


def operand_profile(item: tuple[int, int, int]) -> tuple[int, int, int, int, tuple[int, ...]]:
    """(i, j, t, aligned pairs, profile) of e_i + t e_j under its default 3-dimensional subspace."""
    profile = block_profile(item, pcb.default_basis(item))
    return item[0], item[1], item[2], sum(profile), profile


def operand_orbit(item: tuple[int, int, int]) -> str:
    sys.path.insert(0, str(ROOT / "docs/evidence/a5-exceptional-fibers/hardware-orbits"))
    hardware_orbits = importlib.import_module("hardware_orbits")
    return str(hardware_orbits.classify(hardware_orbits.two_term(*item))["orbit"])


def census() -> dict[str, Any]:
    """Block profiles of every two-term operand under its default tiling, and the orbit of every nullity-12 one."""
    operands = [(i, j, t) for i in range(1, pkm.DIM) for j in range(i + 1, pkm.DIM) for t in (1, -1)]
    profiles = parallel.ordered_map(operand_profile, operands)
    values = Counter(v for row in profiles for v in row[4])
    classes = Counter((row[3], tuple(sorted(row[4]))) for row in profiles)
    wide = [row for row in profiles if row[3] == 12]
    orbits = parallel.ordered_map(operand_orbit, [row[:3] for row in wide], min_items=2)
    table = Counter((tuple(sorted(row[4])), orbit) for row, orbit in zip(wide, orbits, strict=True))
    measured = {
        f"{pkm.operand_tag((i, j, t))}": {"profile": list(profile), "orbit": orbit}
        for (i, j, t, _n, profile), orbit in zip(wide, orbits, strict=True)
        if (i, j, t) in {(1, 18, 1), (17, 2, -1), (1, 24, 1)}
    }
    stored = json.loads((ROOT / "docs/evidence/pathion-kernel-map/census.json").read_text())["two_term_nullity_counts"]
    counted = Counter(row[3] for row in profiles)
    expect(
        {str(k): v for k, v in counted.items()} == stored, "aligned-pair counts differ from census.json nullity counts"
    )
    tilings = {
        f"{pkm.operand_tag(op)} basis {'-'.join(map(str, basis))}": list(block_profile(op, basis))
        for op, bases in (
            ((1, 18, 1), ((19, 1, 2), (19, 4, 8), (19, 2, 4), (19, 16, 1))),
            ((1, 24, 1), ((25, 1, 2), (25, 2, 4), (25, 4, 8), (25, 5, 2))),
        )
        for basis in bases
    }
    return {
        "operands": len(operands),
        "tilings": tilings,
        "block_value_counts": {str(k): v for k, v in sorted(values.items())},
        "classes": [{"nullity": n, "sorted_profile": list(p), "operands": c} for (n, p), c in sorted(classes.items())],
        "nullity_12_orbit_table": [
            {"sorted_profile": list(p), "orbit": o, "operands": c} for (p, o), c in sorted(table.items())
        ],
        "measured_nullity_12": measured,
    }


# ----------------------------------------------------------------------------------------------- claim summaries


def find(units: list[dict[str, Any]], key: str) -> dict[str, Any]:
    matches = [u for u in units if u["key"] == key]
    expect(len(matches) == 1, f"{key}: {len(matches)} units")
    return matches[0]


def kernel_map_claims(run: dict[str, Any]) -> dict[str, Any]:
    """Claim 2: the replica-mean full-map readings, their class means and the findings table's other aggregation."""
    rows = []
    for u in run["units"]:
        if u["control"] in ("primary", "twin"):
            row = {
                k: u[k]
                for k in (
                    "key",
                    "n_ideal",
                    "n_plus",
                    "n_minus",
                    "v_plus",
                    "v_minus",
                    "visibility",
                    "n_hat",
                    "bias",
                    "bias_closed_form",
                    "n_hat_mean_of_replicas",
                    "class_gap_replica_mean",
                    "class_gap_replica_se",
                    "sign_agreement",
                )
            }
            gap, se = u["class_gap_replica_mean"], u["class_gap_replica_se"]
            row["class_gap_t"] = r12(gap / se) if gap is not None and se else None
            row["class_gap_dof"] = u["replicas"] - 1
            rows.append(row)
    return {"readings": rows}


def profile_separation(run: dict[str, Any]) -> dict[str, Any]:
    """Claim 5 on one coset run: the profiles of e1 + e24 and e1 + e18 and their block-wise separation."""
    first, second = (
        next(o for o in run["operands"] if o["operand"] == tag and o["control"] == "primary" and o["family"] == "cmap")
        for tag in PROFILE_PAIR
    )
    rows: list[dict[str, Any]] = []
    for a, b in zip(first["blocks"], second["blocks"], strict=True):
        ua = find(run["units"], f"cmap_{PROFILE_PAIR[0]}_k{a['k']}")
        ub = find(run["units"], f"cmap_{PROFILE_PAIR[1]}_k{b['k']}")
        va, vb = np.array(ua["n_hat_replicas"], dtype=float), np.array(ub["n_hat_replicas"], dtype=float)
        n = len(va)
        diff = float(va.mean() - vb.mean())
        se_unpaired = math.hypot(float(va.std(ddof=1)), float(vb.std(ddof=1))) / math.sqrt(n)
        se_paired = float((va - vb).std(ddof=1)) / math.sqrt(n)
        rows.append(
            {
                "block_index": len(rows),
                "n_ideal": [a["n_ideal"], b["n_ideal"]],
                "forced": [a["forced"], b["forced"]],
                "difference": r12(diff),
                "se_unpaired": r12(se_unpaired),
                "z_unpaired": r12(diff / se_unpaired) if se_unpaired > 0 else None,
                "z_paired": r12(diff / se_paired) if se_paired > 0 else None,
            }
        )
    return {
        "operands": list(PROFILE_PAIR),
        "ideal_profiles": [[b["n_ideal"] for b in first["blocks"]], [b["n_ideal"] for b in second["blocks"]]],
        "measured_profiles": [[b["n_hat"] for b in first["blocks"]], [b["n_hat"] for b in second["blocks"]]],
        "blocks": rows,
        "min_bin_z": [
            r12(min(find(run["units"], f"cmap_{tag}_k{b['k']}")["min_bin_z"] for b in o["blocks"]))
            for tag, o in zip(PROFILE_PAIR, (first, second), strict=True)
        ],
    }


# ----------------------------------------------------------------------------------------------- mixing toy


def bit_flip_matrix(error: float, bits: int = 3) -> np.ndarray:
    """Independent symmetric misassignment of each of ``bits`` output bits with probability ``error``."""
    matrix = np.ones((1, 1))
    for _ in range(bits):
        matrix = np.kron(matrix, np.array([[1.0 - error, error], [error, 1.0 - error]]))
    return matrix


def mixing_toy() -> list[dict[str, Any]]:
    """Output-bit misassignment alone makes Vbar+ exceed Vbar- on a block whose classes differ in size.

    The block contrast of a symmetric channel on the output bits is c_obs = V0 T c_ideal with T the bit-flip matrix.
    A bin of the larger class has more neighbors of its own class, so the smaller class loses more contrast. The
    toy fixes V0 = 0.9 and reports Vbar+, Vbar- and N_hat of every block of the nullity-12 operand e1 + e24 (N_b = 2
    and 4) and of the null operand e1 + e17 (N_b = 0)."""
    rows: list[dict[str, Any]] = []
    for operand in ((1, 24, 1), (1, 17, 1)):
        basis = pcb.default_basis(operand)
        for k0 in pcb.cosets(basis):
            block = pcb.Block(f"k{k0}", operand, basis, k0)
            ideal = pcb.output_contrast(
                pcb.block_law(pcb.block_circuit(block, True)), pcb.block_law(pcb.block_circuit(block, False))
            )
            sign = np.sign(ideal)
            for error in (0.01, 0.02, 0.03):
                est = estimate(0.9 * bit_flip_matrix(error) @ ideal, sign)
                rows.append(
                    {
                        "operand": pkm.operand_tag(operand),
                        "block": k0,
                        "n_ideal": est.n_ideal,
                        "error": error,
                        "v_plus": r12(est.v_plus),
                        "v_minus": r12(est.v_minus),
                        "n_hat": r12(est.n_hat),
                    }
                )
    return rows


# ----------------------------------------------------------------------------------------------- wide runs


def wide_unit(item: tuple[str, int, Any]) -> dict[str, Any]:
    """Estimate of one placement's block: (operand key, placement, (sign, c_obs, block N_b label, block name))."""
    key, placement, payload = item
    sign, c_obs, name = payload
    est = estimate(c_obs, sign)
    return {
        "operand": key,
        "placement": placement,
        "block": name,
        "n_ideal": est.n_ideal,
        "forced": est.forced,
        "n_plus": est.n_plus,
        "n_minus": est.n_minus,
        "visibility": r12(est.visibility),
        "n_hat": r12(est.n_hat),
        "v_plus": r12(est.v_plus),
        "v_minus": r12(est.v_minus),
        "bias_closed_form": r12(est.closed_form_bias()),
        "float_residual": abs(est.n_hat - est.n_ideal - est.closed_form_bias()),
        "exact_residual": str(exact_residual(c_obs, sign)),
    }


def analyze_wide(run_dir: str, source_commit: str) -> dict[str, Any]:
    """Raw per-placement estimator readings of a retained wide run (64- and 128-dimensional operands)."""
    pw = importlib.import_module("pathion_wide_coset")
    wide_pcb = importlib.import_module("pathion_coset_block")
    path = SOURCE / run_dir / "collect.json"
    collect = json.loads(path.read_text())
    entry = [x for x in collect if isinstance(x, dict) and "group" in x][0]
    measured = {name: np.asarray(v, dtype=float) for name, v in entry["measured"].items()}
    items: list[tuple[str, int, Any]] = []
    for op in pw.WIDE_OPERANDS:
        plus_all, minus_all = measured[pw.member_name(op, "plus")], measured[pw.member_name(op, "minus")]
        for placement in range(pw.PLACEMENTS):
            block = op.block_at(placement)
            ideal_plus = wide_pcb.block_law_closed_form(block, True, cocycle_free=op.cocycle_free)
            ideal_minus = wide_pcb.block_law_closed_form(block, False, cocycle_free=op.cocycle_free)
            sign = np.sign(wide_pcb.output_contrast(ideal_plus, ideal_minus))
            c_obs = wide_pcb.output_contrast(plus_all[placement], minus_all[placement])
            items.append((op.key, placement, (sign, c_obs, pw.block_prefix(op, block))))
    units = parallel.ordered_map(wide_unit, items)
    operands = []
    for op in pw.WIDE_OPERANDS:
        mine = [u for u in units if u["operand"] == op.key]
        distinct = sorted({u["block"] for u in mine})
        per_block = {b: [u for u in mine if u["block"] == b] for b in distinct}
        block_summary = [
            {
                "block": b,
                "n_ideal": rows[0]["n_ideal"],
                "forced": rows[0]["forced"],
                "copies": len(rows),
                "n_hat_mean": r12(float(np.mean([u["n_hat"] for u in rows]))),
            }
            for b, rows in per_block.items()
        ]
        total = sum(b["n_hat_mean"] for b in block_summary)
        ideal_total = sum(b["n_ideal"] for b in block_summary)
        forced_part = sum(b["n_ideal"] for b in block_summary if b["forced"])
        operands.append(
            {
                "operand": op.key,
                "role": op.role,
                "dim": op.dim,
                "certified_nullity": op.nullity,
                "blocks": block_summary,
                "profile_n_ideal": [b["n_ideal"] for b in block_summary],
                "n_hat_total": r12(total),
                "n_ideal_total": ideal_total,
                "forced_blocks": sum(1 for b in block_summary if b["forced"]),
                "forced_part": forced_part,
                "informative_part": r12(total - forced_part),
                "informative_ideal": ideal_total - forced_part,
            }
        )
    return {
        "run": run_dir,
        "collect_sha256": sha256(path),
        "group": entry["group"],
        "backend": entry["backend"],
        "source_commit": source_commit,
        "units": units,
        "operands": operands,
        "float_residual_max": max(u["float_residual"] for u in units),
        "exact_residual_all_zero": all(Fraction(u["exact_residual"]) == 0 for u in units),
    }


# ----------------------------------------------------------------------------------------------- self-test


def synthetic(n_plus: int, n_minus: int, phase: float) -> tuple[np.ndarray, np.ndarray]:
    """A deterministic contrast vector and ideal sign vector with the requested class sizes."""
    sign = np.array([1.0] * n_plus + [-1.0] * n_minus)
    index = np.arange(n_plus + n_minus, dtype=float)
    magnitude = 0.35 + 0.2 * np.sin(1.7 * index + phase)
    return (magnitude + 0.04 * sign) * sign, sign


def perturbations(plus: np.ndarray, minus: np.ndarray) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Fixed count edits of an arm pair: swapped arms, cyclic shifts, geometric weights, an alternating pattern."""
    size = plus.size
    geometric = 0.5 ** np.arange(size, dtype=float)
    geometric /= geometric.sum()
    alternating = np.where(np.arange(size) % 2 == 0, 1.0, 3.0)
    alternating /= alternating.sum()
    return {
        "swapped arms": (minus, plus),
        "plus shifted by 3": (np.roll(plus, 3), minus),
        "minus shifted by 5": (plus, np.roll(minus, 5)),
        "geometric plus": (geometric, minus),
        "geometric both": (geometric, geometric[::-1].copy()),
        "alternating minus": (plus, alternating),
        "selector bits flipped": (np.roll(plus, 8), np.roll(minus, 8)),
    }


def self_test(history: bool = True) -> list[str]:
    """Return the failures; empty means the identity, the forced-block law and the mutation controls hold.

    history adds the loader-agreement check on the retained ibm_fez acquisitions; the on-demand gate runs it and the
    pull-request tests call self_test(history=False), which touches synthetic data only.
    """
    problems: list[str] = []
    # Identity: exact on a grid of class sizes and phases, in rational arithmetic.
    for n_plus, n_minus in ((4, 4), (6, 2), (2, 6), (7, 1), (16, 16), (20, 12), (12, 20), (28, 4)):
        for phase in (0.0, 0.9, 2.3):
            c_obs, sign = synthetic(n_plus, n_minus, phase)
            if exact_residual(c_obs, sign) != 0:
                problems.append(f"identity fails exactly at classes {n_plus}/{n_minus}, phase {phase}")
            est = estimate(c_obs, sign)
            if abs(est.n_hat - est.n_ideal - est.closed_form_bias()) > 1e-12:
                problems.append(f"identity residual above 1e-12 at classes {n_plus}/{n_minus}, phase {phase}")
    # Closed form of the block factor: (16 - N_b^2) / 8 on 8 bins and (256 - N^2) / 32 on 32 bins.
    for n_b in range(-3, 4):
        c_obs, sign = synthetic(4 + n_b, 4 - n_b, 0.4)
        est = estimate(c_obs, sign)
        factor = est.n_plus * est.n_minus / 8.0
        if abs(factor - (16 - n_b**2) / 8.0) > 1e-12:
            problems.append(f"block factor differs from (16 - N_b^2)/8 at N_b = {n_b}")
    # Mutation control 1: equalizing the class means drives the bias to zero; the unmutated bias is not zero.
    for n_plus, n_minus in ((16, 16), (20, 12), (6, 2)):
        c_obs, sign = synthetic(n_plus, n_minus, 0.3)
        before = estimate(c_obs, sign)
        if abs(before.n_hat - before.n_ideal) < 1e-3:
            problems.append(
                f"the control has no power at classes {n_plus}/{n_minus}: bias {before.n_hat - before.n_ideal}"
            )
        after_c = equalize(c_obs, sign)
        after = estimate(after_c, sign)
        if abs(after.n_hat - after.n_ideal) > 1e-12 or abs(after.v_plus - after.v_minus) > 1e-12:
            problems.append(f"equalizing leaves a bias {after.n_hat - after.n_ideal} at classes {n_plus}/{n_minus}")
    # Mutation control 2: perturbing the counts of a forced block leaves 4; the same edits move an informative block.
    forced = pcb.Block("forced", (1, 18, 1), pcb.default_basis((1, 18, 1)), 4)
    informative = pcb.Block("informative", (1, 18, 1), pcb.default_basis((1, 18, 1)), 0)
    laws = {}
    for label, block in (("forced", forced), ("informative", informative)):
        ip, im = pcb.block_law(pcb.block_circuit(block, True)), pcb.block_law(pcb.block_circuit(block, False))
        laws[label] = (ip, im, np.sign(pcb.output_contrast(ip, im)))
    moved = 0.0
    for label, (ip, im, sign) in laws.items():
        for edit, (plus, minus) in perturbations(ip, im).items():
            c_obs = pcb.output_contrast(plus, minus)
            if abs(float(np.mean(c_obs * sign))) <= ZERO:
                continue
            reading = estimate(c_obs, sign).n_hat
            if label == "forced" and abs(reading - 4.0) > 1e-12:
                problems.append(f"forced block reads {reading} under '{edit}'")
            if label == "informative":
                moved = max(moved, abs(reading - 0.0))
    if moved < 0.05:
        problems.append(f"the same edits move the informative block by only {moved}: the control has no power")
    # Loader agreement with the code: every replica of a coset run and of the full map through the group's summarize.
    retained = (("ibm_fez coset map", "cmap", RECORD_ROUNDING), ("ibm_fez kernel map", "kmap", None)) if history else ()
    for name, kind, bound in retained:
        path = ROOT / RUNS[name][0] / "collect.json"
        if not path.exists():
            continue
        units, entry, _ideal, extra = run_units(kind, json.loads(path.read_text()))
        for replica in range(units[0].contrast.shape[0]):
            # The selector-disconnected skeleton of the full map is read once; every other member per replica.
            dist = {n: np.asarray(v, dtype=float)[min(replica, len(v) - 1)] for n, v in entry["measured"].items()}
            summary = extra["group"].summarize(dist)
            for unit in units:
                code = summary[f"{unit.key}_nullity_estimate"]
                mine = estimate(unit.contrast[replica], unit.sign).n_hat
                if not (math.isnan(code) and math.isnan(mine)) and abs(code - mine) > 1e-9:
                    problems.append(f"{name} replica {replica}, {unit.key}: estimator {mine} differs from {code}")
        if bound is not None and record_agreement(kind, entry, units) > bound:
            problems.append(f"{name}: per-replica N_hat differs from the collector's summary beyond rounding")
    return problems


# ----------------------------------------------------------------------------------------------- driver


def build() -> dict[str, Any]:
    runs = [analyze_run(name) for name in RUNS]
    units_checked = sum(len(r["units"]) for r in runs)
    exact_zero = all(Fraction(u["exact_residual_max"]) == 0 for r in runs for u in r["units"])
    float_max = max(u["float_residual_max"] for r in runs for u in r["units"])
    forced = [u for r in runs for u in r["units"] if u["forced"]]
    kmap = next(r for r in runs if r["kind"] == "kmap")
    coset = [r for r in runs if r["kind"] != "kmap"]
    return {
        "schema": SCHEMA,
        "estimator": "N_hat = (sum c_obs / 2) / V_hat, V_hat = mean(c_obs * sign(c_ideal))",
        "aggregation": "replica-mean: c_obs is the mean over replicas of each replica's c(y); n_hat_mean_of_replicas "
        "is the mean of the per-replica N_hat, the aggregation of the findings tables",
        "runs": runs,
        "identity": {
            "units_checked": units_checked,
            "exact_residual_all_zero": exact_zero,
            "float_residual_max": float_max,
            "domain": "every bin decided with |c_ideal| = 1; |V_hat| above the code's guard of 1e-9",
        },
        "forced_blocks": {
            "units": len(forced),
            "max_deviation_from_forced_value": max(u["forced_deviation_max"] for u in forced),
            "replicas_below_guard": sum(u["forced_replicas_below_guard"] for u in forced),
            "visibility_replica_min": min(u["visibility_replica_min"] for u in forced),
            "visibility_replica_max": max(u["visibility_replica_max"] for u in forced),
            "stored_corrected": {r["name"]: r["stored_corrected_forced"] for r in coset},
        },
        "kernel_map": kernel_map_claims(kmap),
        "profile_separation": {r["name"]: profile_separation(r) for r in coset},
        "mixing_toy": mixing_toy(),
        "census": census(),
    }


def encode(record: dict[str, Any]) -> str:
    return json.dumps(record, indent=1, sort_keys=True, allow_nan=False) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--out", type=Path, help="directory that receives result.json")
    ap.add_argument("--check", type=Path, help="directory whose result.json is recomputed and compared")
    ap.add_argument("--wide", nargs="+", metavar="RUN", help="wide run directories, relative to the repository root")
    ap.add_argument("--source-commit", help="commit of the NHAT_BIAS_SOURCE tree, recorded with the wide readings")
    ap.add_argument("--out-wide", type=Path, help="file that receives the wide record")
    args = ap.parse_args()
    if args.self_test:
        problems = self_test()
        for line in problems:
            print(f"self-test: {line}", file=sys.stderr)
        print("self-test: " + ("failed" if problems else "passed"))
        return 1 if problems else 0
    if args.wide:
        if not args.source_commit or not args.out_wide:
            raise SystemExit("--wide needs --source-commit and --out-wide")
        record = {
            "schema": SCHEMA,
            "runs": [analyze_wide(run, args.source_commit) for run in args.wide],
        }
        args.out_wide.write_text(encode(record))
        return 0
    record = build()
    text = encode(record)
    if args.check:
        current = (args.check / "result.json").read_text()
        if current != text:
            print("result.json differs from a recomputation", file=sys.stderr)
            return 1
        print("result.json matches a recomputation")
        return 0
    if args.out:
        (args.out / "result.json").write_text(text)
        return 0
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
