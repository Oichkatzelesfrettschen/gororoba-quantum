"""Record selection and per-candidate workers of the forward-model fits of the null rotation scan.

Each worker scores one candidate (or one pair) against the retained series and returns a JSON-ready row; the
scripts map them over their candidate lists through parallel.ordered_map and keep ordering, printing and writing.
The retained inputs load once per process (functools.cache), so a worker process reads them on its first item."""

import functools
import json
from typing import Any

import numpy as np
from scan_forward import HERE, ROOT, cc, laws, rs
from scipy.interpolate import RegularGridInterpolator

S = "2026-11-15T001929Z"
RUNS = ROOT / "results/quantum_inspire/runs"
NONE = ("none", None, None)
ANGLES = 2 * np.pi * (np.arange(8) + 0.5) / 8


@functools.cache
def analysis() -> dict[str, Any]:
    text = (ROOT / "results/quantum_inspire/pathion_null_rotation_scan_tuna_17_analysis.json").read_text()
    return dict(json.loads(text))


@functools.cache
def manifest() -> tuple[dict[str, int], list[int]]:
    """(roles, register) of the series, from one batch's cases.json."""
    man = json.loads((RUNS / f"{S}-pathion_null_rotation_scan_tuna_17-batch-01/cases.json").read_text())
    return {k: int(v) for k, v in man["templates"]["b0"]["roles"].items()}, [int(q) for q in man["register"]]


def bracket_matrix(guard: dict[str, Any]) -> np.ndarray:
    roles, register = manifest()
    mean = {q: tuple((guard["before"][str(q)][i] + guard["after"][str(q)][i]) / 2 for i in (0, 1)) for q in register}
    return np.asarray(cc.readout_matrix(mean, roles))


@functools.cache
def batches() -> tuple[tuple[Any, ...], ...]:
    """Per scan batch: name, arms, bracket matrix, contrasts, errors, center visibility, arm visibilities."""
    out = []
    for batch, row in analysis()["batch_rows"].items():
        if row["kind"] == "bridge":
            continue
        out.append(
            (
                batch,
                tuple(row["arms"]),
                bracket_matrix(row["guard"]),
                np.array([s["contrast"] for s in row["statistics"]]),
                np.array([s["se"] for s in row["statistics"]]),
                row["statistics"][row["arms"].index(rs.CENTER)]["visibility"],
                np.array([s["visibility"] for s in row["statistics"]]),
            )
        )
    return tuple(out)


@functools.cache
def count_batches() -> tuple[tuple[Any, ...], ...]:
    """Per scan batch: name, arms, bracket matrix, outcome counts (arm, outcome)."""
    roles, _ = manifest()
    out = []
    for batch, row in analysis()["batch_rows"].items():
        if row["kind"] == "bridge":
            continue
        directory = RUNS / f"{S}-pathion_null_rotation_scan_tuna_17-{batch}"
        counts = {}
        for f in (directory / "raw").iterdir():
            counts[rs.arm_of(f.name.removesuffix(".json"))] = np.asarray(
                cc.coin_counts(json.loads(f.read_text()), roles), float
            )
        out.append(
            (batch, tuple(row["arms"]), bracket_matrix(row["guard"]), np.stack([counts[a] for a in row["arms"]]))
        )
    return tuple(out)


@functools.cache
def mean_setup() -> tuple[np.ndarray, np.ndarray, float]:
    """(mean bracket matrix, uniform law through it, retention at which the exact center reads visibility 0.42)."""
    roles, register = manifest()
    guards = [r["guard"] for r in analysis()["batch_rows"].values()]
    mean = {
        q: tuple(float(np.mean([(g["before"][str(q)][i] + g["after"][str(q)][i]) / 2 for g in guards])) for i in (0, 1))
        for q in register
    }
    matrix = np.asarray(cc.readout_matrix(mean, roles))
    uniform = np.full(rs.NOUT, 1 / rs.NOUT) @ matrix.T
    center = laws(rs.CENTER, [(NONE, np.zeros(1))])[0] @ matrix.T
    grid = np.linspace(0.05, 1, 381)
    visible = np.array([rs.visibility(r * center + (1 - r) * uniform) for r in grid])
    return matrix, uniform, float(grid[np.abs(visible - 0.42).argmin()])


def scan_arms() -> list[str]:
    return [arm for arm in rs.ARM_NAMES if arm != rs.RETAINED]


# One shared or per-batch parameter (widened_worlds.py, widened_worlds_round2.py) ----------------------------------

SINGLE_THETAS = np.linspace(-0.35, 0.35, 281)
SINGLE_RETENTIONS = np.linspace(0.02, 1.0, 197)


def single_world(item: tuple[tuple[str, Any, Any], float]) -> dict[str, Any]:
    cand, mix = item
    thetas, retentions = SINGLE_THETAS, SINGLE_RETENTIONS
    table = {arm: laws(arm, [(cand, thetas)]) for arm in scan_arms()}
    chi = []
    for _batch, arms, matrix, c, e, cv, _vm in batches():
        center = np.stack([rs.read(rs.contract(table[rs.CENTER][:, None], r, mix)[:, 0], matrix) for r in retentions])
        pick = np.abs(rs.visibility(center) - cv).argmin(0)
        pred = np.stack(
            [
                [
                    rs.selector_contrast(
                        rs.read(rs.contract(table[a][t][None, None], retentions[pick[t]], mix)[0, 0], matrix)
                    )
                    for a in arms
                ]
                for t in range(len(thetas))
            ]
        )
        chi.append((((pred - c) / e) ** 2).sum(1))
    fwd, mir, tot = sum(chi[:4]), sum(chi[4:]), sum(chi)
    j = int(fwd.argmin())
    k = int(tot.argmin())
    per = [float(x.min()) for x in chi]
    return {
        "cand": str(cand),
        "mix": mix,
        "theta_fwd": round(float(thetas[j]), 4),
        "chi_fwd": round(float(fwd[j]), 1),
        "chi_mirror_at_fwd": round(float(mir[j]), 1),
        "theta_all": round(float(thetas[k]), 4),
        "chi_all": round(float(tot[k]), 1),
        "per_batch": [round(float(x[k]), 1) for x in chi],
        "chi_per_batch_param": round(sum(per), 1),
        "params": [round(float(thetas[int(x.argmin())]), 3) for x in chi],
        "per": [round(x, 1) for x in per],
    }


# Two shared parameters (widened_worlds_round3.py) -----------------------------------------------------------------

PAIR_GRID = np.linspace(-0.35, 0.35, 57)
PAIR_RETENTIONS = np.linspace(0.02, 1.0, 99)


def pair_world(item: tuple[tuple[str, Any, Any], tuple[str, Any, Any]]) -> dict[str, Any]:
    ca, cb = item
    ta, tb = [x.ravel() for x in np.meshgrid(PAIR_GRID, PAIR_GRID, indexing="ij")]
    retentions = PAIR_RETENTIONS
    table = {arm: laws(arm, [(ca, ta), (cb, tb)]) for arm in scan_arms()}
    chi = []
    visd = []
    for _batch, arms, matrix, c, e, cv, vm in batches():
        uniform = np.full(rs.NOUT, 1 / rs.NOUT) @ matrix.T
        center = table[rs.CENTER] @ matrix.T
        vis = rs.visibility(retentions[:, None, None] * center[None] + (1 - retentions[:, None, None]) * uniform)
        r = retentions[np.abs(vis - cv).argmin(0)][:, None]
        seen = [r * (table[a] @ matrix.T) + (1 - r) * uniform for a in arms]
        pred = np.stack([rs.selector_contrast(x) for x in seen], 1)
        chi.append((((pred - c) / e) ** 2).sum(1))
        visd.append(np.stack([rs.visibility(x) for x in seen], 1) - vm)
    fwd, mir, tot = sum(chi[:4]), sum(chi[4:]), sum(chi)
    j = int(fwd.argmin())
    k = int(tot.argmin())
    return {
        "A": str(ca),
        "B": str(cb),
        "fwd": [round(float(ta[j]), 3), round(float(tb[j]), 3)],
        "chi_fwd": round(float(fwd[j]), 1),
        "chi_mirror_at_fwd": round(float(mir[j]), 1),
        "all": [round(float(ta[k]), 3), round(float(tb[k]), 3)],
        "chi_all": round(float(tot[k]), 1),
        "per_batch": [round(float(x[k]), 1) for x in chi],
        "max_abs_visibility_miss": round(float(max(np.abs(v[k]).max() for v in visd)), 3),
    }


# All outcome counts (full_histogram_fit.py) -----------------------------------------------------------------------

HISTOGRAM_THETAS = np.linspace(-0.35, 0.35, 141)
HISTOGRAM_RETENTIONS = np.linspace(0.05, 1.0, 96)
HISTOGRAM_SHARES = (0.0, 0.25, 0.5, 0.75, 1.0)


def histogram_world(cand: tuple[str, Any, Any]) -> dict[str, Any]:
    thetas = HISTOGRAM_THETAS
    table = {arm: laws(arm, [(cand, thetas)]) for arm in scan_arms()}
    per = []
    par: list[Any] = []
    for _batch, arms, matrix, obs in count_batches():
        shots = obs.sum(1)[None, None, :, None]
        law = np.stack([table[a] for a in arms], 1)
        best: tuple[Any, ...] = (np.inf, None)
        for mix in HISTOGRAM_SHARES:
            for r in HISTOGRAM_RETENTIONS:
                p = rs.contract(law, r, mix) @ matrix.T
                chi = (((obs[None] - shots[0] * p) ** 2) / (shots[0] * p)).sum((1, 2))
                j = int(chi.argmin())
                if chi[j] < best[0]:
                    best = (float(chi[j]), (float(thetas[j]), float(r), mix))
        per.append(best[0])
        par.append(best[1])
    return {
        "cand": str(cand),
        "chi": round(sum(per), 0),
        "per": [round(x) for x in per],
        "theta": [round(p[0], 3) for p in par],
        "r": [round(p[1], 2) for p in par],
        "mix": [p[2] for p in par],
    }


# Parameters that follow the line (phase_resolved_fit.py, phase_resolved_two_source.py) ----------------------------


@functools.cache
def phase_data() -> dict[str, tuple[np.ndarray, float, float]]:
    """Per arm: the pooled phase-bin contrasts, the error of one bin, the mean q4 line amplitude."""
    rows = json.loads((HERE / "line_phase_bins.json").read_text())
    data = {}
    for arm in sorted({r["arm"] for r in rows if r["arm"] != rs.RETAINED}):
        v = [r for r in rows if r["arm"] == arm]
        data[arm] = (
            np.mean([r["bins"] for r in v], 0),
            2 * np.sqrt(np.mean([r["se"] ** 2 for r in v]) / len(v)),
            float(np.mean([r["q4_amp"] for r in v])),
        )
    return data


def q4_marginal(seen: np.ndarray) -> np.ndarray:
    d1 = rs.KEYS.index("d1")
    return np.asarray(
        seen.reshape(*seen.shape[:-1], *([2] * 5)).sum(tuple(-1 - i for i in range(5) if i != d1))[..., 1]
    )


PHASE_THETAS = np.linspace(-0.6, 0.6, 481)
PHASE_OFFSETS = np.linspace(-0.3, 0.3, 61)
PHASE_AMPLITUDES = np.linspace(0.0, 0.3, 31)


def phase_single(cand: tuple[str, Any, Any]) -> dict[str, Any]:
    matrix, uniform, r0 = mean_setup()
    data = phase_data()
    arms = list(data)
    thetas, ang = PHASE_THETAS, ANGLES
    con = {}
    p4 = {}
    for a in arms:
        seen = r0 * (laws(a, [(cand, thetas)]) @ matrix.T) + (1 - r0) * uniform
        con[a] = rs.selector_contrast(seen)
        p4[a] = q4_marginal(seen)
    best: tuple[Any, ...] = (np.inf, None)
    for u0 in PHASE_OFFSETS:
        for am in PHASE_AMPLITUDES if cand[0] != "none" else PHASE_AMPLITUDES[:1]:
            chi = 0.0
            chia = 0.0
            pred = {}
            for a in arms:
                slope = np.interp(u0 + 1e-3, thetas, p4[a]) - np.interp(u0 - 1e-3, thetas, p4[a])
                s = 1.0 if slope >= 0 else -1.0
                u = u0 + s * am * np.cos(ang)
                c = np.interp(u, thetas, con[a])
                pm = np.interp(u, thetas, p4[a])
                amp = abs(2 * np.mean(pm * np.exp(-1j * ang)))
                chi += float((((c - data[a][0]) / data[a][1]) ** 2).sum())
                chia += ((amp - data[a][2]) / 0.002) ** 2
                pred[a] = (c, amp)
            if chi + chia < best[0]:
                best = (chi + chia, chi, chia, float(u0), float(am), pred)
    return {
        "cand": str(cand),
        "total": round(best[0], 1),
        "chi_contrast_80": round(best[1], 1),
        "chi_q4amp_10": round(best[2], 1),
        "u0": best[3],
        "A": best[4],
        "pred": {a: [np.round(best[5][a][0], 4).tolist(), round(float(best[5][a][1]), 4)] for a in arms},
    }


TWO_GRID = np.linspace(-0.5, 0.5, 41)
TWO_OFFSETS = np.linspace(-0.3, 0.3, 25)
TWO_FIRST_AMPLITUDES = np.linspace(0.0, 0.2, 9)
TWO_SECOND_AMPLITUDES = np.linspace(-0.2, 0.2, 17)


def phase_pair(item: tuple[tuple[str, Any, Any], tuple[str, Any, Any]]) -> dict[str, Any]:
    ca, cb = item
    matrix, uniform, r0 = mean_setup()
    data = phase_data()
    arms = list(data)
    grid, ang = TWO_GRID, ANGLES
    ga, gb = [x.ravel() for x in np.meshgrid(grid, grid, indexing="ij")]
    a0, aa, b0, ab = [
        x.ravel()
        for x in np.meshgrid(TWO_OFFSETS, TWO_FIRST_AMPLITUDES, TWO_OFFSETS, TWO_SECOND_AMPLITUDES, indexing="ij")
    ]
    cos = np.cos(ang)
    chi = np.zeros(len(a0))
    chia = np.zeros(len(a0))
    preds = {}
    for a in arms:
        seen = r0 * (laws(a, [(ca, ga), (cb, gb)]) @ matrix.T) + (1 - r0) * uniform
        fc = RegularGridInterpolator((grid, grid), rs.selector_contrast(seen).reshape(41, 41))
        fp = RegularGridInterpolator((grid, grid), q4_marginal(seen).reshape(41, 41))
        res = []
        for sgn in (1.0, -1.0):
            ua = a0[:, None] + sgn * aa[:, None] * cos[None]
            ub = b0[:, None] + sgn * ab[:, None] * cos[None]
            pts = np.stack([ua.ravel(), ub.ravel()], 1)
            c = fc(pts).reshape(-1, 8)
            p = fp(pts).reshape(-1, 8)
            res.append((c, 2 * (p * np.exp(-1j * ang)[None]).mean(1)))
        pick = res[0][1].real >= res[1][1].real
        c = np.where(pick[:, None], res[0][0], res[1][0])
        amp = np.where(pick, np.abs(res[0][1]), np.abs(res[1][1]))
        chi += (((c - data[a][0][None]) / data[a][1]) ** 2).sum(1)
        chia += ((amp - data[a][2]) / 0.002) ** 2
        preds[a] = (c, amp)
    k = int((chi + chia).argmin())
    k2 = int(chi.argmin())
    return {
        "A": str(ca),
        "B": str(cb),
        "total": round(float(chi[k] + chia[k]), 1),
        "chi_contrast_80": round(float(chi[k]), 1),
        "chi_q4amp_10": round(float(chia[k]), 1),
        "params_a0_Aa_b0_Ab": [round(float(x[k]), 3) for x in (a0, aa, b0, ab)],
        "contrast_only_best": round(float(chi[k2]), 1),
        "contrast_only_params": [round(float(x[k2]), 3) for x in (a0, aa, b0, ab)],
        "pred": {a: [np.round(preds[a][0][k], 4).tolist(), round(float(preds[a][1][k]), 4)] for a in arms},
    }


# Fixed-parameter worlds (exact_pulse_residuals.py, d2_split_worlds.py, followup_predictions.py) --------------------


def exact_residual_batch(batch: str) -> dict[str, Any]:
    """Measured contrasts of one scan batch less the exact-pulse law of each gate-noise family."""
    row = analysis()["batch_rows"][batch]
    world = "pulse_x_before_all"
    zero = int(np.argmin(np.abs(rs.parameter_grid(world))))
    matrix = bracket_matrix(row["guard"])
    arms = tuple(row["arms"])
    c = np.array([s["contrast"] for s in row["statistics"]])
    e = np.array([s["se"] for s in row["statistics"]])
    cv = row["statistics"][arms.index(rs.CENTER)]["visibility"]
    line: dict[str, Any] = {
        "kind": row["kind"],
        "arms": arms,
        "measured": c.round(4).tolist(),
        "visibility": [round(s["visibility"], 3) for s in row["statistics"]],
        "exact": {},
    }
    for kind in rs.FIT_KINDS:
        model, _strength = rs.gate_fit_model(world, kind, arms, matrix, cv)
        m = model[zero]
        line["exact"][kind] = {
            "model": m.round(4).tolist(),
            "residual": (c - m).round(4).tolist(),
            "z": ((c - m) / e).round(1).tolist(),
        }
    return line


FIXED_WORLDS: dict[str, tuple[tuple[str, Any, Any], float]] = {
    "exact": (NONE, 0.0),
    "q12_phase": (("pulse", "zb", 12), -0.18),
    "coupler_8_12_phase": (("cz", (8, 12), None), -0.25),
}


def d2_split_world(name: str) -> dict[str, Any]:
    """Chi-square of the 24 retained d2 splits under one fixed world, each batch at its center visibility."""
    cand, value = FIXED_WORLDS[name]
    table = {arm: laws(arm, [(cand, np.array([value]))])[0] for arm in scan_arms()}
    grid = np.linspace(0.05, 1.0, 381)
    chi = 0.0
    rows = {}
    for batch, row in analysis()["batch_rows"].items():
        if row["kind"] == "bridge":
            continue
        matrix = bracket_matrix(row["guard"])
        uniform = np.full(rs.NOUT, 1 / rs.NOUT) @ matrix.T
        center = table[rs.CENTER] @ matrix.T
        cv = row["statistics"][row["arms"].index(rs.CENTER)]["visibility"]
        r = grid[np.abs(np.array([rs.visibility(x * center + (1 - x) * uniform) for x in grid]) - cv).argmin()]
        for arm, st in zip(row["arms"], row["statistics"], strict=True):
            model = float(rs.d2_split(r * (table[arm] @ matrix.T) + (1 - r) * uniform)[0])
            chi += ((st["d2_split"] - model) / st["d2_split_se"]) ** 2
            rows[f"{batch}/{arm}"] = [round(st["d2_split"], 4), round(model, 4)]
    return {"chi2_24": round(chi, 1), "measured_model": rows}


FOLLOWUP_Q4_STEPS = (-2, -1, 0, 1, 2, 3, 4)
FOLLOWUP_Q12_DEGREES = (-20, -10, 0, 10, 20)
FOLLOWUP_Q8_DEGREES = (-20, -10, 10, 20)


def followup_world(name: str) -> dict[str, Any]:
    """(contrast, d2 split) of the draft follow-up arms under one fixed world at the mean bracket."""
    matrix, uniform, r0 = mean_setup()
    cand, value = FIXED_WORLDS[name]
    base = [(cand, np.array([value]))]

    def read(arm: str, items: list[tuple[tuple[str, Any, Any], np.ndarray]]) -> tuple[float, float]:
        seen = r0 * (laws(arm, items)[0] @ matrix.T) + (1 - r0) * uniform
        return round(float(rs.selector_contrast(seen)), 4), round(float(rs.d2_split(seen)[0]), 4)

    for k in FOLLOWUP_Q4_STEPS:
        rs.ARMS[f"q4k{k}"] = ("Rx", "q4", k)
    q12 = {}
    for d in FOLLOWUP_Q12_DEGREES:
        injected = np.array([np.radians(d)])
        if name == "q12_phase":
            q12[str(d)] = read(rs.CENTER, [(cand, np.array([value]) + injected)])
        else:
            q12[str(d)] = read(rs.CENTER, [*base, (("pulse", "zb", 12), injected)])
    return {
        "q4": {str(5 * k): read(f"q4k{k}", base) for k in FOLLOWUP_Q4_STEPS},
        "q12_rz": q12,
        "q8_rz_after_cz_8_12": {
            str(d): read(rs.CENTER, [*base, (("czz", 8, (8, 12)), np.array([np.radians(d)]))])
            for d in FOLLOWUP_Q8_DEGREES
        },
    }
