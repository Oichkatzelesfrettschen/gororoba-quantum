"""Own-partner, within-three-hop and baseline terms of the idle readout phase rate.

The design is docs/design/heron-idle-readout-attribution.md.

For probe p of pair k the phase rate in a readout window is modeled as
delta_p = a_p own + c_p near + b f_other: own is 1 when the pair's partner reads, near when every other pair's
reader within three CZ hops of p reads, and f_other is the fraction of the 30 other pairs whose partner reads.
Two partitions of the pairs into classes A and B, each a 2-coloring of the three-hop pair conflict graph, put
every within-three-hop reader in the opposite class. Pattern a reads class A partners and holds class B quiet;
pattern b swaps them. Per partition, a probe of class X reads

    R_p = a_p + b n_same / 30    (its own class's pattern)
    Q_p = c_p + b n_opp / 30     (the opposite pattern)
    D_p = a_p + c_p + b          (the all-read arm)

and D_p - R_p - Q_p is zero under the model. Isolated probes, with no other pair's reader within three hops,
carry no near term, so 30 Q_p / n_opp estimates b there.

Every estimate runs on arrays with a leading replicate axis, so the observed estimate and every bootstrap replicate
go through one implementation: `estimate` on the observed laws is `estimate` on a one-replicate batch. Each law is
(..., 4) over outcomes o, with bit 0 the target's read and bit 1 the spectator's.
"""

from __future__ import annotations

import itertools
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gororoba_quantum"))

import numpy as np  # noqa: E402

import idle_penalty as ip  # noqa: E402

PAIRS = 31
OTHERS = PAIRS - 1
NEAR_HOPS = 3
# The class strings and member names are idle_penalty's, the campaign's single home for them.
PARTITIONS = ip.PARTITIONS
PATTERNS = ip.PATTERNS
RESOLVED_Z = 3.29
MATERIAL_KHZ = 0.5
SHARE_OWNERSHIP = 0.5
BOOTSTRAP_REPLICATES = 4000
# Attribution reads shares only over at least this many probes with a resolved all-read shift; a share interval
# exists only when at least FINITE_FRACTION of the replicates resolve some probe.
MIN_RESOLVED = 10
FINITE_FRACTION = 0.975
BOOTSTRAP_BLOCK = 250
REPLICATION_ALPHA = 1e-3
ROLES = (ip.TARGET, ip.SPECTATOR)


half_member = ip.half_member


@dataclass(frozen=True)
class Geometry:
    """Pin-order pair classes, isolation of each (pair, role) probe and the same-class counts per partition."""

    classes: dict[str, str]
    isolated: np.ndarray  # (PAIRS, 2) bool
    n_same: dict[str, np.ndarray]  # partition -> (PAIRS,) other pairs in the pair's own class

    @property
    def isolated_pairs(self) -> np.ndarray:
        return np.flatnonzero(self.isolated.any(axis=1))


def conflict_graph(paths: list[tuple[int, int]], couplers: list[tuple[int, int]]) -> set[tuple[int, int]]:
    """Pair-index edges joining pairs with any qubits within NEAR_HOPS CZ hops."""
    adjacency: dict[int, set[int]] = {}
    for a, b in couplers:
        adjacency.setdefault(a, set()).add(b)
        adjacency.setdefault(b, set()).add(a)

    def ball(qubit: int) -> set[int]:
        seen, frontier = {qubit}, {qubit}
        for _ in range(NEAR_HOPS):
            frontier = {n for q in frontier for n in adjacency.get(q, ())} - seen
            seen |= frontier
        return seen

    balls = [set().union(*(ball(q) for q in path)) for path in paths]
    return {(i, j) for i, j in itertools.combinations(range(len(paths)), 2) if balls[i] & set(paths[j])}


def geometry(paths: list[tuple[int, int]], couplers: list[tuple[int, int]]) -> Geometry:
    """Classes, isolation and counts for the pinned paths; refuses a partition that is not a proper coloring."""
    if len(paths) != PAIRS:
        raise ValueError(f"{len(paths)} paths, the partitions hold {PAIRS}")
    edges = conflict_graph(paths, couplers)
    for name, classes in PARTITIONS.items():
        clashes = [(i, j) for i, j in edges if classes[i] == classes[j]]
        if clashes:
            raise ValueError(f"partition {name} puts conflicting pairs {clashes} in one class")
    adjacency: dict[int, set[int]] = {}
    for a, b in couplers:
        adjacency.setdefault(a, set()).add(b)
        adjacency.setdefault(b, set()).add(a)
    isolated = np.zeros((PAIRS, 2), dtype=bool)
    for k, path in enumerate(paths):
        for role in ROLES:
            seen, frontier = {path[role]}, {path[role]}
            for _ in range(NEAR_HOPS):
                frontier = {n for q in frontier for n in adjacency.get(q, ())} - seen
                seen |= frontier
            readers = {other[1 - role] for j, other in enumerate(paths) if j != k}
            isolated[k, role] = not (seen & readers)
    n_same = {
        name: np.array([sum(classes[j] == classes[k] for j in range(PAIRS) if j != k) for k in range(PAIRS)])
        for name, classes in PARTITIONS.items()
    }
    return Geometry(dict(PARTITIONS), isolated, n_same)


def _p1(law: np.ndarray, bit: int) -> np.ndarray:
    return law[..., 1 << bit] + law[..., 3]


def _unfolded(law: np.ndarray, bit: int, refs: tuple[np.ndarray, np.ndarray]) -> np.ndarray:
    p1g, p0e = refs
    return ((1.0 - 2.0 * _p1(law, bit)) - (p0e - p1g)) / (1.0 - p1g - p0e)


def _phase(laws: dict[str, np.ndarray], stem: str, bit: int, refs: tuple[np.ndarray, np.ndarray]) -> tuple[Any, Any]:
    x = _unfolded(laws[stem.format(q="x")], bit, refs)
    y = _unfolded(laws[stem.format(q="y")], bit, refs)
    return np.arctan2(y, x), np.hypot(x, y)


def _khz(during: np.ndarray, reference: np.ndarray, idle_dt: int, dt: float) -> np.ndarray:
    wrapped = np.mod(during - reference + np.pi, 2 * np.pi) - np.pi
    return wrapped / (2 * np.pi * idle_dt * dt) / 1e3


def _unwrap(long_khz: np.ndarray, short_khz: np.ndarray, dt: float) -> np.ndarray:
    period = 1 / (ip.MEAS_DT * dt) / 1e3
    return long_khz + np.round((short_khz - long_khz) / period) * period


def contrasts(laws: dict[str, np.ndarray], dt: float, shots: int) -> dict[str, Any]:
    """Per (replicate, pair, role): D, its shot-noise standard error, and each partition's pattern shifts in kHz."""
    out: dict[str, Any] = {"D": [], "D_quiet": [], "null": [], "D_se": [], "S": {}}
    shifts: dict[tuple[str, str], list[np.ndarray]] = {}
    for bit in ROLES:
        head = ip.probe_prefix(bit)
        refs = (_p1(laws["idle_ground"], bit), 1.0 - _p1(laws["idle_excited"], bit))
        after, v_after = _phase(laws, f"{head}meas_after_{{q}}", bit, refs)
        quiet_short, _ = _phase(laws, f"{head}ramsey_{{q}}_{ip.SHORT_MEAS_DT}dt", bit, refs)
        during, v_during = _phase(laws, f"{head}meas_during_{{q}}", bit, refs)
        short, _ = _phase(laws, f"{head}meas_short_{{q}}", bit, refs)
        quiet_long, _ = _phase(laws, f"{head}ramsey_{{q}}_{ip.MEAS_DT}dt", bit, refs)
        short_khz = _khz(short, quiet_short, ip.SHORT_MEAS_DT, dt)
        out["D"].append(_unwrap(_khz(during, after, ip.MEAS_DT, dt), short_khz, dt))
        out["D_quiet"].append(_unwrap(_khz(during, quiet_long, ip.MEAS_DT, dt), short_khz, dt))
        out["null"].append(_khz(after, quiet_long, ip.MEAS_DT, dt))
        se_v = math.sqrt(2) / (math.sqrt(shots) * (1.0 - refs[0] - refs[1]))
        floor = np.maximum(np.minimum(v_during, v_after), 0.06)
        out["D_se"].append(se_v / floor / (2 * np.pi * ip.MEAS_DT * dt) / 1e3)
        for partition, pattern in itertools.product(PARTITIONS, PATTERNS):
            long_phase, _ = _phase(laws, half_member(bit, partition, pattern, "{q}"), bit, refs)
            short_phase, _ = _phase(laws, half_member(bit, partition, pattern, "{q}", short=True), bit, refs)
            shift = _unwrap(
                _khz(long_phase, after, ip.MEAS_DT, dt), _khz(short_phase, quiet_short, ip.SHORT_MEAS_DT, dt), dt
            )
            shifts.setdefault((partition, pattern), []).append(shift)
    for key in ("D", "D_quiet", "null", "D_se"):
        out[key] = np.stack(out[key], axis=-1)
    out["S"] = {key: np.stack(value, axis=-1) for key, value in shifts.items()}
    return out


def _own_other(geo: Geometry, partition: str, shifts: dict[tuple[str, str], np.ndarray]) -> tuple[Any, Any]:
    """R (own class reading) and Q (opposite class reading) per (replicate, pair, role)."""
    own = np.array([cls == "A" for cls in geo.classes[partition]])[None, :, None]
    a, b = shifts[(partition, "a")], shifts[(partition, "b")]
    return np.where(own, a, b), np.where(own, b, a)


def _b(geo: Geometry, q_per_partition: dict[str, np.ndarray], pairs: np.ndarray) -> np.ndarray:
    """Median over the given pair indices (replicate, n) of the pair's mean 30 Q / n_opp over its isolated roles,
    per partition, then the mean of the partitions' medians."""
    medians = []
    weight = geo.isolated.astype(float)
    for partition, q in q_per_partition.items():
        n_opp = (OTHERS - geo.n_same[partition])[None, :, None]
        per_role = OTHERS * q / n_opp
        per_pair = (per_role * weight[None]).sum(axis=-1) / np.maximum(weight.sum(axis=-1), 1)[None]
        medians.append(np.median(np.take_along_axis(per_pair, pairs, axis=1), axis=1))
    return np.mean(medians, axis=0)


def estimate(geo: Geometry, c: dict[str, Any], strata: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Every coefficient and cohort statistic per replicate; strata maps each stratum to its (replicate, n) pair
    indices (identity rows for the observed estimate)."""
    rq = {p: _own_other(geo, p, c["S"]) for p in PARTITIONS}
    q_only = {p: rq[p][1] for p in PARTITIONS}
    iso_all = np.concatenate([strata["isolated_A"], strata["isolated_B"]], axis=1)
    b = _b(geo, q_only, iso_all)
    b_class = {cls: _b(geo, q_only, strata[f"isolated_{cls}"]) for cls in ("A", "B")}
    bb = b[:, None, None]
    a = np.mean([rq[p][0] - bb * geo.n_same[p][None, :, None] / OTHERS for p in PARTITIONS], axis=0)
    near = np.mean([rq[p][1] - bb * (OTHERS - geo.n_same[p])[None, :, None] / OTHERS for p in PARTITIONS], axis=0)
    near = np.where(geo.isolated[None], np.nan, near)
    residual = np.mean([c["D"] - rq[p][0] - rq[p][1] for p in PARTITIONS], axis=0)
    chosen = np.concatenate([strata[name] for name in sorted(strata)], axis=1)

    def gather(values: np.ndarray) -> np.ndarray:
        return np.take_along_axis(values, chosen[:, :, None].repeat(2, axis=2), axis=1).reshape(len(values), -1)

    d, d_se, a_c, c_c, r_c = (gather(v) for v in (c["D"], c["D_se"], a, near, residual))
    resolved = np.abs(d) > RESOLVED_Z * d_se
    with np.errstate(invalid="ignore", divide="ignore"):
        shares = {
            "own_partner": _row_median(np.where(resolved, a_c / d, np.nan)),
            "within_three_hop": _row_median(np.where(resolved & ~np.isnan(c_c), c_c / d, np.nan)),
            "baseline": _row_median(np.where(resolved, b[:, None] / d, np.nan)),
        }
        median_residual = _row_median(r_c)
    return {
        "a": a,
        "c": near,
        "b": b,
        "b_A": b_class["A"],
        "b_B": b_class["B"],
        "residual": residual,
        "median_residual": median_residual,
        "resolved_count": resolved.sum(axis=1),
        **{f"share_{k}": v for k, v in shares.items()},
    }


def _row_median(values: np.ndarray) -> np.ndarray:
    """Median of each row's finite entries; NaN for a row with none (no resolved probe in that replicate)."""
    out = np.full(len(values), np.nan)
    filled = np.isfinite(values).any(axis=1)
    if filled.any():
        out[filled] = np.nanmedian(values[filled], axis=1)
    return out


def strata_of(geo: Geometry) -> dict[str, np.ndarray]:
    iso = set(geo.isolated_pairs.tolist())
    p1 = geo.classes["p1"]
    return {
        "isolated_A": np.array([k for k in range(PAIRS) if k in iso and p1[k] == "A"]),
        "isolated_B": np.array([k for k in range(PAIRS) if k in iso and p1[k] == "B"]),
        "other": np.array([k for k in range(PAIRS) if k not in iso]),
    }


def bootstrap_inputs(
    geo: Geometry, laws: dict[str, np.ndarray], shots: int, seed: int, replicates: int
) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
    """Every replicate's pair indices per stratum, then every member's multinomial resample, drawn from one generator
    in that fixed order before any estimate runs."""
    rng = np.random.default_rng(seed)
    base = strata_of(geo)
    strata = {name: rng.choice(idx, size=(replicates, len(idx)), replace=True) for name, idx in sorted(base.items())}
    resampled = {}
    for name in sorted(laws):
        law = np.clip(laws[name][0], 0.0, None)
        law = law / law.sum(axis=-1, keepdims=True)
        counts = rng.multinomial(shots, law, size=(replicates, *law.shape[:-1]))
        resampled[name] = counts / shots
    return strata, resampled


def _interval(values: np.ndarray) -> list[float]:
    finite = values[np.isfinite(values)]
    if len(finite) < FINITE_FRACTION * len(values):
        return [math.nan, math.nan]
    return [float(np.percentile(finite, 2.5)), float(np.percentile(finite, 97.5))]


def decide(geo: Geometry, observed: dict[str, np.ndarray], boot: dict[str, np.ndarray], full: dict[str, np.ndarray]):
    """The design's decisions from the observed estimate, the pair-resampled replicates and the shot-only replicates
    (full pair set) that give per-probe standard errors."""
    out: dict[str, Any] = {}
    b_iv, a_iv, bb_iv = _interval(boot["b"]), _interval(boot["b_A"]), _interval(boot["b_B"])
    agree = not (a_iv[1] < bb_iv[0] or bb_iv[1] < a_iv[0])
    out["b"] = {
        "value": float(observed["b"][0]),
        "interval": b_iv,
        "class_A": a_iv,
        "class_B": bb_iv,
        "class_agreement": agree,
        "verdict": ("present" if b_iv[0] > 0 or b_iv[1] < 0 else "absent or unresolved") if agree else "unresolved",
    }
    res_iv = _interval(boot["median_residual"])
    if res_iv[0] >= -MATERIAL_KHZ and res_iv[1] <= MATERIAL_KHZ:
        additivity = "additive"
    elif res_iv[0] > MATERIAL_KHZ or res_iv[1] < -MATERIAL_KHZ:
        additivity = "non-additive"
    else:
        additivity = "unresolved"
    out["additivity"] = {"median": float(observed["median_residual"][0]), "interval": res_iv, "verdict": additivity}
    if additivity == "non-additive":
        # The model that defines b failed, so decision 2 is withdrawn with the attribution and the labels.
        out["b"]["verdict"] = "withdrawn"
    shares = {key: _interval(boot[f"share_{key}"]) for key in ("own_partner", "within_three_hop", "baseline")}
    signs = {key: (1 if iv[0] > 0 else -1 if iv[1] < 0 else 0) for key, iv in shares.items()}
    resolved_count = int(observed["resolved_count"][0])
    if not agree:
        attribution = "unresolved"
    elif additivity == "non-additive":
        attribution = "withdrawn"
    elif resolved_count < MIN_RESOLVED or any(math.isnan(iv[0]) for iv in shares.values()):
        attribution = "unresolved"
    elif any(signs[x] * signs[y] < 0 for x, y in itertools.combinations(signs, 2)):
        attribution = "opposed"
    else:
        owners = [key for key, iv in shares.items() if iv[0] > SHARE_OWNERSHIP]
        attribution = owners[0] if len(owners) == 1 else "mixed"
    out["attribution"] = {
        "shares": {key: {"median": float(observed[f"share_{key}"][0]), "interval": iv} for key, iv in shares.items()},
        "resolved_probes": resolved_count,
        "verdict": attribution,
    }
    labels: dict[str, Any] = {}
    for name in ("a", "c"):
        value = observed[name][0]
        # c is structurally absent on isolated probes; their columns carry NaN in every replicate.
        applicable = ~np.isnan(value)
        replicates = full[name][:, applicable]
        se = np.full(value.shape, np.nan)
        lo, hi = se.copy(), se.copy()
        se[applicable] = replicates.std(axis=0)
        lo[applicable] = np.percentile(replicates, 2.5, axis=0)
        hi[applicable] = np.percentile(replicates, 97.5, axis=0)
        material = np.where((lo > MATERIAL_KHZ) | (hi < -MATERIAL_KHZ), "material", "indeterminate")
        material = np.where((lo >= -MATERIAL_KHZ) & (hi <= MATERIAL_KHZ), "negligible", material)
        labels[name] = {
            "value": np.where(applicable, value, np.nan).tolist(),
            "se": se.tolist(),
            "resolved": (applicable & (np.abs(np.nan_to_num(value)) > RESOLVED_Z * np.nan_to_num(se))).tolist(),
            "material": np.where(applicable, material, "not applicable").tolist(),
        }
    out["labels"] = labels
    out["withdrawn_labels"] = additivity == "non-additive"
    return out


def _block_estimates(
    item: tuple[Geometry, dict[str, np.ndarray], float, int, dict[str, np.ndarray]],
) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
    """One block of replicates: the pair-resampled estimate and the shot-only estimate on every pair."""
    geo, laws, dt, shots, strata = item
    c = contrasts(laws, dt, shots)
    count = len(next(iter(strata.values())))
    identity = {name: np.repeat(idx[None, :], count, axis=0) for name, idx in strata_of(geo).items()}
    return estimate(geo, c, strata), estimate(geo, c, identity)


def bootstrap_estimates(
    geo: Geometry,
    resampled: dict[str, np.ndarray],
    strata: dict[str, np.ndarray],
    dt: float,
    shots: int,
    pooled: bool = True,
) -> tuple[dict[str, np.ndarray], dict[str, np.ndarray]]:
    """Every replicate's estimates, computed in blocks of BOOTSTRAP_BLOCK replicates mapped through
    parallel.ordered_map (pooled) or in order (serial); each row depends only on its own inputs, so both give the
    same bits."""
    import parallel

    total = len(next(iter(strata.values())))
    items = [
        (
            geo,
            {name: law[start : start + BOOTSTRAP_BLOCK] for name, law in resampled.items()},
            dt,
            shots,
            {name: idx[start : start + BOOTSTRAP_BLOCK] for name, idx in strata.items()},
        )
        for start in range(0, total, BOOTSTRAP_BLOCK)
    ]
    blocks = parallel.ordered_map(_block_estimates, items) if pooled else [_block_estimates(item) for item in items]
    boot = {key: np.concatenate([block[0][key] for block in blocks]) for key in blocks[0][0]}
    full = {key: np.concatenate([block[1][key] for block in blocks]) for key in blocks[0][1]}
    return boot, full


def replication(c: dict[str, Any]) -> dict[str, Any]:
    """The probe's all-read shift, read again by the design's t-only rule on the observed pair means: negative
    against both quiet references with t below the one-sided REPLICATION_ALPHA quantile on PAIRS - 1 degrees of
    freedom, and the quiet null (after against Ramsey) not resolved by the two-sided test at the same alpha."""
    from scipy import stats

    dof = PAIRS - 1
    lower = float(stats.t.ppf(REPLICATION_ALPHA, dof))
    two_sided = float(stats.t.ppf(1 - REPLICATION_ALPHA / 2, dof))
    out: dict[str, Any] = {}
    for key in ("D", "D_quiet", "null"):
        pairs = np.asarray(c[key][0]).mean(axis=-1)
        mean, se = float(pairs.mean()), float(pairs.std(ddof=1) / math.sqrt(len(pairs)))
        out[key] = {"mean_khz": mean, "se_khz": se, "t": mean / se if se > 0 else math.nan}
    negative = all(out[key]["t"] < lower for key in ("D", "D_quiet"))
    null_present = abs(out["null"]["t"]) > two_sided
    out["verdict"] = "replicated" if negative and not null_present else "not replicated"
    return out


def analyze(
    geo: Geometry, laws: dict[str, np.ndarray], dt: float, shots: int, seed: int, replicates: int = BOOTSTRAP_REPLICATES
) -> dict[str, Any]:
    """Observed estimate, pair-cluster bootstrap and decisions. laws holds (1, PAIRS, 4) arrays per member."""
    identity = {name: idx[None, :] for name, idx in strata_of(geo).items()}
    c_observed = contrasts(laws, dt, shots)
    observed = estimate(geo, c_observed, identity)
    strata, resampled = bootstrap_inputs(geo, laws, shots, seed, replicates)
    boot, full = bootstrap_estimates(geo, resampled, strata, dt, shots)
    out = decide(geo, observed, boot, full)
    out["replication"] = replication(c_observed)
    return out


def synthetic_laws(
    geo: Geometry,
    a: np.ndarray,
    c: np.ndarray,
    b: float,
    dt: float,
    visibility: float = 0.8,
    pattern_offset_khz: dict[tuple[str, str], float] | None = None,
    during_extra_khz: float = 0.0,
) -> dict[str, np.ndarray]:
    """Exact laws of every member the analyzer reads, for planted a (PAIRS, 2), c (PAIRS, 2) and b, with ideal
    assignment and a common phase origin that every contrast cancels. pattern_offset_khz adds a rate to every probe
    of one (partition, pattern) PUB; during_extra_khz adds a rate to the all-read arms only, breaking additivity."""
    origin = 0.37
    offsets = pattern_offset_khz or {}

    def law(phase: np.ndarray, bit: int, quadrature: str) -> np.ndarray:
        projection = np.cos(phase) if quadrature == "x" else np.sin(phase)
        p1 = (1.0 - visibility * projection) / 2.0
        out = np.zeros((1, PAIRS, 4))
        out[0, :, 1 << bit] = p1
        out[0, :, 0] = 1.0 - p1
        return out

    def window_phase(rate_khz: np.ndarray, idle_dt: int) -> np.ndarray:
        return origin + 2 * np.pi * rate_khz * 1e3 * idle_dt * dt

    laws: dict[str, np.ndarray] = {}
    ground = np.zeros((1, PAIRS, 4))
    ground[..., 0] = 1.0
    excited = np.zeros((1, PAIRS, 4))
    excited[..., 3] = 1.0
    laws["idle_ground"], laws["idle_excited"] = ground, excited
    near = np.where(geo.isolated, 0.0, c)
    for bit in ROLES:
        head = ip.probe_prefix(bit)
        rates = {
            "meas_after": np.zeros(PAIRS),
            f"ramsey_{{q}}_{ip.SHORT_MEAS_DT}dt": np.zeros(PAIRS),
            f"ramsey_{{q}}_{ip.MEAS_DT}dt": np.zeros(PAIRS),
            "meas_during": a[:, bit] + near[:, bit] + b + during_extra_khz,
            "meas_short": a[:, bit] + near[:, bit] + b + during_extra_khz,
        }
        for stem, rate in rates.items():
            idle = ip.SHORT_MEAS_DT if "short" in stem or f"{ip.SHORT_MEAS_DT}dt" in stem else ip.MEAS_DT
            for q in ip.QUADRATURES:
                name = f"{head}{stem}" if "{q}" in stem else f"{head}{stem}_{{q}}"
                laws[name.format(q=q)] = law(window_phase(rate, idle), bit, q)
        for partition, pattern in itertools.product(PARTITIONS, PATTERNS):
            reads = np.array([cls == PATTERNS[pattern] for cls in geo.classes[partition]])
            n_reading = np.array([sum(reads[j] for j in range(PAIRS) if j != k) for k in range(PAIRS)], dtype=float)
            rate = np.where(reads, a[:, bit], near[:, bit]) + b * n_reading / OTHERS
            rate = rate + offsets.get((partition, pattern), 0.0)
            for short in (False, True):
                idle = ip.SHORT_MEAS_DT if short else ip.MEAS_DT
                for q in ip.QUADRATURES:
                    laws[half_member(bit, partition, pattern, q, short)] = law(window_phase(rate, idle), bit, q)
    return laws


def pinned_geometry() -> Geometry:
    """The geometry of the probe's 31 ordered pairs on Kingston's coupler graph."""
    case = (ROOT / "results/live/IDLE_PENALTY_REPEAT_CASE.md").read_text()
    pin = next(line for line in case.splitlines() if line.startswith("ibm_kingston:"))
    paths = [tuple(int(q) for q in path.split(",")) for path in pin.split(":", 1)[1].split("/")]
    targets = json.loads((ROOT / "docs/evidence/heron_platform/targets.json").read_text())
    couplers = [tuple(pair) for pair in targets["backends"]["ibm_kingston"]["instructions"]["cz"]["qargs"]]
    return geometry([(a, b) for a, b in paths], [(a, b) for a, b in couplers])


def _couplers(backend: str) -> list[tuple[int, int]]:
    targets = json.loads((ROOT / "docs/evidence/heron_platform/targets.json").read_text())
    return [(int(a), int(b)) for a, b in targets["backends"][backend]["instructions"]["cz"]["qargs"]]


def load_predicted(run: Path) -> tuple[Geometry, dict[str, np.ndarray], float, int]:
    """A dry run's noisy predictions as (1, PAIRS, 4) laws per member, with the geometry of its own replicas.

    The replicas' initial layouts must be the pinned paths the class strings index; geometry refuses a partition
    that is not a proper coloring of them.
    """
    import idle_penalty_report as report

    record = json.loads((run / "record.json").read_text())
    group = next(g for g in record["groups"] if g["group"] == "idle_readout")
    paths = report.role_map(group)
    geo = geometry(paths, _couplers(group["backend"]))
    laws = {
        m["name"]: np.asarray([[r["noisy"] for r in m["replicas"]]], dtype=float)
        for m in group["members"]
        if not m["reference"]
    }
    targets = json.loads((ROOT / "docs/evidence/heron_platform/targets.json").read_text())
    return geo, laws, float(targets["backends"][group["backend"]]["dt"]), int(record["shots"])


def _effective(body: str) -> str:
    """The retained-arm name a patterned replica's body stands for: the reader arm itself, or for a quiet template
    the reader arm of the same window, whose probe idle it repeats."""
    return body.replace("meas_short_quiet_", "meas_short_").replace("meas_quiet_", "meas_during_")


def patterned_exposure(timelines: dict[str, list[tuple[Any, Any]]], bodies: dict[str, tuple[str, ...]]) -> list[str]:
    """Departures of a patterned member's schedule from its classes: within a class every replica shares one
    schedule; every probe repeats its quiet Ramsey reference; a reading partner plays its whole train inside its
    probe's idle and a quiet partner reads only at the end; every quiet replica's probe idle contains every reading
    replica's train in absolute schedule time."""
    import idle_penalty_report as report

    reasons = []
    for name, names in bodies.items():
        replicas = timelines[name]
        probe = report._probe(name)
        gapped = [(report._gaps(t), report._gaps(sp)) for t, sp in replicas]
        for body in sorted(set(names)):
            classes = {gapped[k] for k, b in enumerate(names) if b == body}
            if len(classes) != 1:
                reasons.append(f"{name}: {len(classes)} distinct schedules among replicas running {body}")
        windows, trains = {}, {}
        for k, body in enumerate(names):
            arm = _effective(body)
            planned = report.planned_idles(arm)[probe]
            idles = [gap for _, gap in gapped[k][probe] if gap]
            if idles != planned:
                reasons.append(f"{name} replica {k}: probe idles {idles}, planned {planned}")
            reference = report.quiet_reference(arm)
            if reference not in timelines or report._gaps(timelines[reference][k][probe]) != gapped[k][probe]:
                reasons.append(f"{name} replica {k}: probe schedule differs from {reference}")
            probe_line, reader_line = replicas[k][probe], replicas[k][1 - probe]
            pulses = [i for i in probe_line if i[0] not in ("reset", "measure")]
            reads = [i for i in reader_line if i[0] == "measure"]
            if len(pulses) != 2:
                reasons.append(f"{name} replica {k}: {len(pulses)} probe pulses, planned 2")
                continue
            windows[k] = (pulses[0][2], pulses[1][1])
            between = reads[:-1]
            if "quiet" in body:
                if between:
                    reasons.append(f"{name} replica {k}: quiet partner reads {len(between)} times in the window")
                continue
            count = ip.SHORT_MEAS_COUNT if "short" in arm else ip.MEAS_COUNT
            if len(between) != count:
                reasons.append(f"{name} replica {k}: {len(between)} reader reads, planned {count}")
            elif not (windows[k][0] <= between[0][1] and between[-1][2] <= windows[k][1]):
                reasons.append(f"{name} replica {k}: reader train leaves the probe idle")
            else:
                trains[k] = (between[0][1], between[-1][2])
        for k, (start, end) in windows.items():
            if "quiet" not in names[k]:
                continue
            outside = [j for j, (t0, t1) in trains.items() if t0 < start or t1 > end]
            if outside:
                reasons.append(f"{name}: quiet replica {k} idle {start}-{end} misses the trains of replicas {outside}")
    return reasons


def load_measured(run: Path) -> tuple[Geometry, dict[str, np.ndarray], float, int, dict[str, Any]]:
    """A collected run's measured laws, after the collector refusals, the one-calibration rule and the exposure
    gate: the retained members through idle_penalty_report.exposure_violations, the patterned members through
    patterned_exposure, and every replica's compiled instructions against the service schedule."""
    import idle_penalty_report as report
    import scheduled_idle_replay
    from qiskit import qpy

    import law_encoding

    record = json.loads((run / "record.json").read_text())
    group = next(g for g in record["groups"] if g["group"] == "idle_readout")
    roles = report.role_map(group)
    geo = geometry(roles, _couplers(group["backend"]))
    names = [m["name"] for m in group["members"] if not m["reference"]]
    bodies = {m["name"]: tuple(m["replica_bodies"]) for m in group["members"] if m.get("replica_bodies")}
    collected = json.loads((run / "collect.json").read_text())
    block = next(c for c in collected if isinstance(c, dict) and c.get("group") == "idle_readout")
    for key in ("comparisons_withheld", "summary_unavailable", "calibration_dependent_summaries_unavailable"):
        if key in block:
            raise report.RefusedAnalysis(f"the collector set {key}: {block[key]}")
    executed = block["executed"]
    missing = [n for n in names if n not in executed or n not in block["measured"]]
    if missing:
        raise report.RefusedAnalysis(f"members without an execution record or law: {missing}")
    stamps = {executed[n].get("calibration") for n in names}
    straddling = [n for n in names if executed[n].get("calibration_changed_during_shots")]
    if None in stamps or straddling or len(stamps) != 1:
        raise report.RefusedAnalysis(f"calibrations {sorted(map(str, stamps))}, straddling {straddling}")
    files = report._raw_pub_files(run)
    with (run / "isa.qpy").open("rb") as stream:
        fused = {circuit.name: circuit for circuit in qpy.load(stream)}
    reasons = []
    for pub in record["execution_pubs"]:
        rows = scheduled_idle_replay.schedule_rows(files[pub["name"]])
        for component in pub["components"]:
            if component["group"] != "idle_readout":
                continue
            replicas = scheduled_idle_replay.component_replicas(record, component)
            for k, (qubits, registers) in enumerate(zip(replicas, component["registers_by_replica"], strict=True)):
                try:
                    scheduled_idle_replay.padded_replica(fused[pub["name"]], rows, qubits, registers, insert=False)
                except RuntimeError as error:
                    reasons.append(f"{component['member']} replica {k}: {error}")
    timelines = report.schedule_timelines(run, executed, names, roles)
    retained = [n for n in names if n not in bodies]
    reasons += report.exposure_violations({n: timelines[n] for n in retained})
    reasons += patterned_exposure(timelines, bodies)
    if reasons:
        raise report.RefusedAnalysis("scheduled exposure: " + "; ".join(reasons[:8]))
    laws = {
        n: np.asarray([[law_encoding.dense(stored) for stored in block["measured"][n]]], dtype=float) for n in names
    }
    targets = json.loads((ROOT / "docs/evidence/heron_platform/targets.json").read_text())
    identity = {"source": "measured", "calibration": stamps.pop(), "record_sha256": report._sha256(run / "record.json")}
    return geo, laws, float(targets["backends"][group["backend"]]["dt"]), int(record["shots"]), identity


def self_check(out: dict[str, Any]) -> list[str]:
    """The design's cohort-level null on predictions that carry no readout crosstalk; empty when it holds."""
    from scipy import stats

    misses = []
    low, high = out["b"]["interval"]
    if not low <= 0.0 <= high:
        misses.append(f"b interval {out['b']['interval']} excludes zero")
    for name in ("a", "c"):
        family = sum(label != "not applicable" for row in out["labels"][name]["material"] for label in row)
        resolved = int(np.sum(out["labels"][name]["resolved"]))
        ceiling = int(stats.binom.ppf(0.99, family, 0.001))
        if resolved > ceiling:
            misses.append(f"{resolved} of {family} {name}_p resolved, above the null's 99th percentile {ceiling}")
    if out["additivity"]["verdict"] != "additive":
        misses.append(f"additivity reads {out['additivity']['verdict']}")
    if out["attribution"]["verdict"] != "unresolved":
        misses.append(f"attribution reads {out['attribution']['verdict']}")
    return misses


def main(argv: list[str] | None = None) -> int:
    import argparse

    import qrng_seeds

    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("run", type=Path)
    parser.add_argument("--self-check", action="store_true", help="require the no-crosstalk null on predictions")
    qrng_seeds.add_seed_argument(parser, "--seed", help="bootstrap seed, qrng:<draw>#<index>")
    parser.add_argument("--replicates", type=int, default=BOOTSTRAP_REPLICATES)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    if args.seed is None:
        parser.error("--seed takes a qrng:<draw>#<index> value")
    import idle_penalty_report as report

    try:
        if args.self_check or not (args.run / "collect.json").exists():
            geo, laws, dt, shots = load_predicted(args.run)
            identity: dict[str, Any] = {"source": "predicted"}
        else:
            geo, laws, dt, shots, identity = load_measured(args.run)
    except report.RefusedAnalysis as refusal:
        print(f"refused: {refusal}")
        return 2
    out = analyze(geo, laws, dt, shots, args.seed, args.replicates)
    out["identity"] = identity | {"run": qrng_seeds.repo_relative(args.run), "seed": args.seed_source}
    text = json.dumps(out, indent=1, sort_keys=True, allow_nan=True) + "\n"
    if args.out:
        args.out.write_text(text)
    print(
        f"b {out['b']['value']:+.3f} kHz {out['b']['interval']}; additivity {out['additivity']['verdict']}; "
        f"attribution {out['attribution']['verdict']} over {out['attribution']['resolved_probes']} resolved probes"
    )
    if args.self_check:
        misses = self_check(out)
        if misses:
            print("self-check failed: " + "; ".join(misses))
            return 1
        print("self-check: b contains zero, resolved labels within the null, additive, attribution unresolved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
