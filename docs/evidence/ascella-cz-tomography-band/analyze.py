"""Post-data decomposition of the Ascella CZ tomography reference band pair (2026-11-09) beside the retained pair
(2026-10-31). Every statistic here was chosen after the data arrived, so each one generates a hypothesis and none
decides a preregistered conjecture; the preregistered verdicts are those of
results/quandela/ascella-cz-tomography-reference-analysis.json.

Run from the repository root: ``"$PYTHON" docs/evidence/ascella-cz-tomography-band/analyze.py OUT.json``. The
output is deterministic (no random draw).

The sectors:

* Pearson split: the case's Pearson statistic (scripts/ascella_cz_tomography_reference_case.py ``pearson``) by
  cells whose linear-inversion prediction is below one event. The case's statistic centers each cell on its
  expected count E and divides by max(E, 1); no exact throughput/shape split of it exists, because a weighted
  projection onto each setting's expected vector is dominated by the negative-E cells the clip leaves at weight E^2.
  Two exact splits of nearby statistics stand in: per-setting event totals against the fit's totals, sum over
  settings of (T - S)^2 / S with S the unclipped expected total; and the clipped-center statistic, centered and
  divided by C = max(E, 1), split into throughput (T - sum C)^2 / sum C and within-setting shape.
* Z sector: CZ is diagonal, so for a two-photon event a qubit read out in Z keeps its prepared Z population whatever
  the photon overlap. Multiphoton emission, loss, threshold postselection and dark clicks admit eligible events that
  are not two-photon events and move those populations, so ``source_model_z`` predicts them per setting through the
  retained noise pipeline (``forecast_setting``, record variant) at the pair's plan read and the g2-aware overlap, and
  the residual after subtracting the prediction is the part the source model does not explain.
* Rail ratios: inputs 00, 01 and 11 succeed with 1/9 at every overlap and 10 with (5 - 4M)/9, so r(00)/r(01) is a
  target-rail transmission ratio and r(01)/r(11) a control-rail one; D = r(10) r(01) / (r(00) r(11)) from ZZ
  readouts alone and from all nine readouts.
* Two-click patterns: photons enter C0 and T0; for output modes i < j the indistinguishable probability is
  |U[i,C0] U[j,T0] + U[j,C0] U[i,T0]|^2 and the distinguishable one |U[i,C0] U[j,T0]|^2 + |U[j,C0] U[i,T0]|^2,
  mixed linearly in the overlap M (exact for two photons, multiphoton emission ignored). A maximum-likelihood fit
  over all 15 window pairs of all 144 settings gives one M and six relative detection efficiencies per pair of
  runs; a common efficiency cancels in the conditional distribution. A second fit (``g2_pattern_overlap``) adds
  Perceval's multiphoton source model at the plan read's g2 and transmittance.
"""

from __future__ import annotations

import importlib
import itertools
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import minimize, minimize_scalar
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[3]
BAND_GLOB = "2026-11-09T17*ascella_cz_tomography_reference-job-0*"
PROFILE_DELTA = 1.92  # half the 95 % chi-squared(1) quantile: a profile-likelihood interval
IDENTIFIED_SENSITIVITY = 0.05
BAND_ANALYSIS = "results/quandela/ascella-cz-tomography-reference-analysis.json"
RETAINED_VERDICTS = "results/quandela/cases/ascella_cz_tomography_reference/retained-conjecture-verdicts.json"
G2_GRID = np.linspace(0.84, 0.98, 15)  # total variation between the M = 0 and M = 1 pattern laws of a setting


def modules() -> tuple[Any, Any, Any]:
    for path in ("scripts", "gororoba_quantum"):
        if str(ROOT / path) not in sys.path:
            sys.path.insert(0, str(ROOT / path))
    case = importlib.import_module("ascella_cz_tomography_reference_case")
    return case, case.tomo, importlib.import_module("qd_records")


CASE, TOMO, RECORDS = modules()
ROWS = TOMO.schedule()
PAIRS = list(itertools.combinations(range(TOMO.WINDOW), 2))


def pairs_of_runs() -> dict[str, dict[str, Any]]:
    band = sorted(str(p.relative_to(ROOT)) for p in (ROOT / "results/quandela/runs").glob(BAND_GLOB))
    if len(band) != 2:
        raise RuntimeError(f"expected the two band runs, found {band}")
    return {
        "retained": {"runs": list(CASE.TOMOGRAPHY_RUNS), "loader": TOMO.load_run, "jobs": TOMO.JOBS},
        "band": {"runs": band, "loader": CASE.load_run, "jobs": CASE.JOBS},
    }


def tallies(spec: dict[str, Any]) -> dict[str, np.ndarray]:
    loaded = [spec["loader"](ROOT / run) for run in spec["runs"]]
    found: dict[str, dict[str, Any]] = {}
    for entry in loaded:
        found.update(entry["tallies"])
    pool = TOMO.pooling(loaded, spec["jobs"])
    jobs = spec["jobs"]
    return {
        "eligible": np.array([found[r["name"]]["eligible"] for r in ROWS], dtype=float),
        "samples": np.array([found[r["name"]]["samples"] for r in ROWS], dtype=float),
        "shots": np.array([found[r["name"]]["shots"] for r in ROWS], dtype=float),
        "scale": np.array([pool["scales"][jobs[TOMO.JOBS.index(r["job"])]] for r in ROWS]),
    }


def pearson_split(data: dict[str, np.ndarray]) -> dict[str, Any]:
    n, shots, scale = data["eligible"], data["shots"], data["scale"]
    rates = TOMO.absolute_rates(n, shots, scale)
    predicted = (TOMO.design_matrix() @ (TOMO.design_pseudoinverse() @ rates)).reshape(n.shape)
    expected = predicted * shots[:, None] / scale[:, None]
    cells = (n - expected) ** 2 / np.maximum(expected, 1.0)
    below = expected < 1.0
    clipped = np.maximum(expected, 1.0)
    total, clipped_total = n.sum(1), clipped.sum(1)
    within = clipped / clipped_total[:, None]
    throughput = (total - clipped_total) ** 2 / clipped_total
    shape = ((n - total[:, None] * within) ** 2 / clipped).sum(1)
    order = np.argsort(cells.sum(1))[::-1]
    return {
        "events": float(n.sum()),
        "pearson": float(cells.sum()),
        "cells_below_one_expected": int(below.sum()),
        "pearson_in_those_cells": float(cells[below].sum()),
        "observed_events_in_those_cells": float(n[below].sum()),
        "clipped_statistic": float(((n - clipped) ** 2 / clipped).sum()),
        "clipped_throughput_part": float(throughput.sum()),
        "clipped_shape_part": float(shape.sum()),
        "clipped_identity_gap": float(((n - clipped) ** 2 / clipped).sum() - throughput.sum() - shape.sum()),
        "total_count_pearson": float(((total - expected.sum(1)) ** 2 / expected.sum(1)).sum()),
        "median_relative_total_deviation": float(np.median(np.abs(total / expected.sum(1) - 1.0))),
        "top_settings": [
            {"setting": ROWS[s]["name"], "pearson": float(cells[s].sum()), "share": float(cells[s].sum() / cells.sum())}
            for s in order[:5]
        ],
        "process_fidelity": TOMO.estimate_rates(rates)["process_fidelity"],
    }


def gate_independent(data: dict[str, np.ndarray]) -> dict[str, Any]:
    n = data["eligible"]
    entries = []
    for s, r in enumerate(ROWS):
        for q in (0, 1):
            if r["basis"][q] != "Z":
                continue
            prepared = r["input"][q]
            target = {"0": 1.0, "1": 0.0}.get(prepared, 0.5)
            zero = n[s][[0, 1]].sum() if q == 0 else n[s][[0, 2]].sum()
            entries.append(
                {
                    "setting": r["name"],
                    "qubit": ("control", "target")[q],
                    "prepared": prepared,
                    "deviation": float(zero / n[s].sum() - target),
                }
            )
    eigen = [e for e in entries if e["prepared"] in "01"]
    equator = [e for e in entries if e["prepared"] not in "01"]
    groups: dict[str, list[float]] = {}
    for e in equator:
        groups.setdefault(f"{e['qubit']} {e['prepared']}", []).append(e["deviation"])
    return {
        "entries": entries,
        "bit_flip_mean": float(np.mean([abs(e["deviation"]) for e in eigen])),
        "bit_flip_max": float(max(abs(e["deviation"]) for e in eigen)),
        "equator_bias_by_state": {k: {"mean": float(np.mean(v)), "sd": float(np.std(v))} for k, v in groups.items()},
    }


def z_populations(n: np.ndarray) -> list[dict[str, Any]]:
    """The Z-readout entries of a (144, 4) table of eligible outcome weights, in schedule order."""
    entries = []
    for s, r in enumerate(ROWS):
        for q in (0, 1):
            if r["basis"][q] != "Z":
                continue
            prepared = r["input"][q]
            target = {"0": 1.0, "1": 0.0}.get(prepared, 0.5)
            zero = n[s][[0, 1]].sum() if q == 0 else n[s][[0, 2]].sum()
            entries.append({"setting": r["name"], "prepared": prepared, "deviation": float(zero / n[s].sum() - target)})
    return entries


def source_model_z(data: dict[str, np.ndarray], perfs: dict[str, Any], overlap: float) -> dict[str, Any]:
    """The Z-sector deviations the retained noise pipeline predicts per setting (record variant: Perceval source at
    the plan read's g2, transmittance and dark counts, at ``overlap``), their correlation with the measured ones, and
    the measured-minus-predicted residuals."""
    figures = {**TOMO.perf_figures(perfs), "hom": overlap}
    dark = [float(rate) for rate in perfs["Dark counts (detection/s)"]]
    predicted = np.array(
        [
            TOMO.forecast_setting((r, figures, dark))[CASE.FORECAST_RECORD_VARIANT]["eligible_probabilities"]
            for r in ROWS
        ]
    )
    model = z_populations(predicted)
    measured = z_populations(data["eligible"])
    out: dict[str, Any] = {"overlap": overlap}
    for kind, keep in (("bit_flip", "01"), ("equator_bias", "+i")):
        x = np.array([e["deviation"] for e in measured if e["prepared"] in keep])
        y = np.array([e["deviation"] for e in model if e["prepared"] in keep])
        out[kind] = {
            "pearson_r_measured_predicted": float(np.corrcoef(x, y)[0, 1]),
            "mean_abs_measured": float(np.abs(x).mean()),
            "mean_abs_predicted": float(np.abs(y).mean()),
            "mean_abs_residual": float(np.abs(x - y).mean()),
            "residual": [float(v) for v in x - y],
        }
    return out


def model_check_forecast(
    band: dict[str, Any], retained: dict[str, Any], split: dict[str, Any], data: dict[str, np.ndarray]
) -> dict[str, Any]:
    """Scalings of the retained pair's model-check statistic to the band pair's events, each over the band reference
    mean. None is a calibrated forecast: the retained statistic is mostly acquisition scatter (its reference mean),
    and every scaling here except the linear one carries that scatter as if it were systematic. The linear scaling
    multiplies the retained excess over its reference mean by the event ratio; the split scaling multiplies the
    retained cells below one expected event by its square and the rest by the ratio; the clip-aware scaling
    multiplies every retained count and expectation by the ratio and rescores them with the case's clip. The
    reference mean's own growth shows the clip inflating acquisition scatter faster than the events."""
    scale = band["mean_events_per_rate"] / retained["mean_events_per_rate"]
    reference = band["reference_mean"]
    excess = retained["pearson"] - retained["reference_mean"]
    low = split["pearson_in_those_cells"]
    n, shots, cell_scale = data["eligible"], data["shots"], data["scale"]
    rates = TOMO.absolute_rates(n, shots, cell_scale)
    expected = (TOMO.design_matrix() @ (TOMO.design_pseudoinverse() @ rates)).reshape(n.shape)
    expected = expected * shots[:, None] / cell_scale[:, None]
    rescored = float(((scale * n - scale * expected) ** 2 / np.maximum(scale * expected, 1.0)).sum())
    return {
        "event_scale": scale,
        "reference_mean_growth": reference / retained["reference_mean"],
        "retained_share_of_reference_mean": retained["reference_mean"] / retained["pearson"],
        "linear_excess_scaling_ratio": (reference + scale * excess) / reference,
        "split_whole_statistic_scaling_ratio": (scale**2 * low + scale * (split["pearson"] - low)) / reference,
        "clip_aware_whole_statistic_scaling_ratio": rescored / reference,
        "observed_ratio": band["ratio"],
    }


def share_excess(n: np.ndarray, q: np.ndarray) -> float:
    total = n.sum(1, keepdims=True)
    value = float(np.mean((n / total - q) ** 2 - q * (1 - q) / total))
    return float(np.sqrt(max(value, 0.0)))


def implied_share_error(data: dict[str, np.ndarray]) -> dict[str, Any]:
    """The RMS per-setting error of an eligible-outcome share beyond binomial, sqrt(mean over cells of (f - q)^2 -
    q (1 - q) / N), with f the measured conditional share and N the setting's eligible events, about three centers q:
    the in-sample linear-inversion prediction (clipped at zero), which absorbs part of the error it measures; the
    prediction of the projection onto physical maps; and the leave-one-cell-out prediction of the linear inversion.
    A setting cannot be left out whole (the design loses rank), so no center is fully out of sample, and the spread
    over centers bounds what the residual says about a physical per-seed scale."""
    n, shots, scale = data["eligible"], data["shots"], data["scale"]
    rates = TOMO.absolute_rates(n, shots, scale)
    design, inverse = TOMO.design_matrix(), TOMO.design_pseudoinverse()

    def shares(prediction: np.ndarray) -> np.ndarray:
        clipped = np.clip(prediction.reshape(n.shape), 0.0, None)
        return clipped / clipped.sum(1, keepdims=True)

    fitted = design @ (inverse @ rates)
    choi = TOMO.estimate_rates(rates)["projected_choi"]
    projected = design @ np.array([np.real(np.trace(b @ choi)) for b in TOMO.hermitian_basis()])
    deleted = rates - (rates - fitted) / (1.0 - np.diag(design @ inverse))
    q = shares(fitted)
    total = n.sum(1, keepdims=True)
    by_class = {}
    for name, (lo, hi) in {"extreme": (0.0, 0.15), "middle": (0.15, 0.85), "upper": (0.85, 1.01)}.items():
        mask = (q >= lo) & (q < hi)
        value = float(np.mean(((n / total - q) ** 2 - q * (1 - q) / total)[mask]))
        by_class[name] = {"cells": int(mask.sum()), "rms": float(np.sqrt(max(value, 0.0)))}
    return {
        "rms": share_excess(n, q),
        "rms_projected_center": share_excess(n, shares(projected)),
        "rms_leave_cell_out_center": share_excess(n, shares(deleted)),
        "by_predicted_share": by_class,
    }


def tomography_cell_growth(retained: dict[str, np.ndarray], band: dict[str, np.ndarray]) -> dict[str, Any]:
    """Band-over-retained growth of the case's Pearson cells, on each pair's own below-one-expected cells and on the
    cells in the same class in both pairs (the class is set per pair, so own-class sums compare different cells)."""

    def cells(data: dict[str, np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
        n, shots, scale = data["eligible"], data["shots"], data["scale"]
        rates = TOMO.absolute_rates(n, shots, scale)
        e = (TOMO.design_matrix() @ (TOMO.design_pseudoinverse() @ rates)).reshape(n.shape)
        e = e * shots[:, None] / scale[:, None]
        return (n - e) ** 2 / np.maximum(e, 1.0), e < 1.0

    (ca, la), (cb, lb) = cells(retained), cells(band)
    both_low, both_high = la & lb, ~la & ~lb
    return {
        "low_cells": {"retained": int(la.sum()), "band": int(lb.sum()), "common": int(both_low.sum())},
        "own_class_low_ratio": float(cb[lb].sum() / ca[la].sum()),
        "own_class_high_ratio": float(cb[~lb].sum() / ca[~la].sum()),
        "common_low_ratio": float(cb[both_low].sum() / ca[both_low].sum()),
        "common_high_ratio": float(cb[both_high].sum() / ca[both_high].sum()),
    }


def rail_ratios(data: dict[str, np.ndarray]) -> dict[str, Any]:
    n, shots, scale = data["eligible"], data["shots"], data["scale"]

    def rate(label: str, basis: str | None) -> float:
        picked = [s for s, r in enumerate(ROWS) if r["input"] == label and (basis is None or r["basis"] == basis)]
        return float(np.mean([n[s].sum() / shots[s] * scale[s] for s in picked]))

    out: dict[str, Any] = {}
    for key, basis in (("zz", "ZZ"), ("all_readouts", None)):
        r = {label: rate(label, basis) for label in ("00", "01", "10", "11")}
        d = r["10"] * r["01"] / (r["00"] * r["11"])
        out[key] = {
            "target_rail_ratio_r00_over_r01": r["00"] / r["01"],
            "control_rail_ratio_r01_over_r11": r["01"] / r["11"],
            "control_rate_ratio_r11_over_r01": r["11"] / r["01"],
            "rail_ratio_D": d,
            "overlap_from_D": (5.0 - d) / 4.0,
        }
    spread = {}
    for label in ("00", "01", "10", "11"):
        values = [n[s].sum() / shots[s] for s, r in enumerate(ROWS) if r["input"] == label]
        spread[label] = float(np.std(values) / np.mean(values))
    out["relative_spread_over_readouts"] = spread
    return out


def pattern_laws() -> tuple[np.ndarray, np.ndarray]:
    indistinguishable = np.zeros((len(ROWS), len(PAIRS)))
    distinguishable = np.zeros((len(ROWS), len(PAIRS)))
    c, t = TOMO.C0, TOMO.T0
    for s, r in enumerate(ROWS):
        u = TOMO.setting_unitary(r)
        for k, (i, j) in enumerate(PAIRS):
            indistinguishable[s, k] = abs(u[i, c] * u[j, t] + u[j, c] * u[i, t]) ** 2
            distinguishable[s, k] = abs(u[i, c] * u[j, t]) ** 2 + abs(u[j, c] * u[i, t]) ** 2
    return indistinguishable, distinguishable


def pattern_counts(runs: list[str]) -> tuple[np.ndarray, int]:
    index = {r["name"]: k for k, r in enumerate(ROWS)}
    counts = np.zeros((len(ROWS), len(PAIRS)))
    outside = 0
    for run in runs:
        record = RECORDS.read_run(ROOT / run)
        by_seed = {st["compilation_seed"]: st["name"] for st in record.manifest["settings"]}
        for entry in record.collected.get("iterations") or []:
            if not entry.get("counts"):
                continue
            s = index[by_seed[entry["iteration"]["compilation_seed"]]]
            for key, count in entry["counts"].items():
                on = [m for m, v in enumerate(TOMO.parse_state(key)) if v]
                if len(on) != 2:
                    continue
                if max(on) >= TOMO.WINDOW:
                    outside += count
                    continue
                counts[s, PAIRS.index((on[0], on[1]))] += count
    return counts, outside


def pattern_law(laws: tuple[np.ndarray, np.ndarray], overlap: float, efficiency: np.ndarray) -> np.ndarray:
    weight = np.array([efficiency[i] * efficiency[j] for i, j in PAIRS])
    p = (overlap * laws[0] + (1.0 - overlap) * laws[1]) * weight
    return p / p.sum(1, keepdims=True)


def negative_log_likelihood(counts: np.ndarray, law: np.ndarray) -> float:
    return -float((counts * np.log(np.maximum(law, 1e-300))).sum())


def two_click_patterns(laws: tuple[np.ndarray, np.ndarray], runs: list[str]) -> dict[str, Any]:
    counts, outside = pattern_counts(runs)

    def objective(x: np.ndarray) -> float:
        overlap = 1.0 / (1.0 + np.exp(-x[0]))
        return negative_log_likelihood(counts, pattern_law(laws, overlap, np.concatenate([[1.0], np.exp(x[1:])])))

    fit = minimize(objective, np.zeros(TOMO.WINDOW), method="Nelder-Mead", options={"maxiter": 20000})
    refined = minimize(objective, fit.x, method="BFGS")
    status = {"nelder_mead": bool(fit.success), "bfgs": bool(refined.success), "bfgs_message": str(refined.message)}
    if refined.fun <= fit.fun:
        fit = refined
    overlap = float(1.0 / (1.0 + np.exp(-fit.x[0])))
    efficiency = np.concatenate([[1.0], np.exp(fit.x[1:])])
    grid = np.linspace(0.5, 0.9999, 4000)
    profile = np.array([negative_log_likelihood(counts, pattern_law(laws, m, efficiency)) for m in grid]) - fit.fun
    inside = grid[profile <= PROFILE_DELTA]
    expected = pattern_law(laws, overlap, efficiency) * counts.sum(1, keepdims=True)
    per_setting = []
    for s in range(len(ROWS)):
        best = minimize_scalar(
            lambda m, s=s: -float((counts[s] * np.log(np.maximum(pattern_law(laws, m, efficiency)[s], 1e-300))).sum()),
            bounds=(0.0, 1.0),
            method="bounded",
        )
        per_setting.append(float(best.x))
    rails = [PAIRS.index((TOMO.C0 + a, TOMO.T0 + b)) for a in (0, 1) for b in (0, 1)]
    return {
        "window_two_click_events": float(counts.sum()),
        "two_clicks_outside_window": int(outside),
        "eligible_share_of_window_two_clicks": float(counts[:, rails].sum() / counts.sum()),
        "optimizer": status,
        "overlap": overlap,
        "overlap_profile_interval": [float(inside.min()), float(inside.max())],
        "efficiency_relative_to_C0": [float(e) for e in efficiency],
        "misfit_pearson": float(((counts - expected) ** 2 / np.maximum(expected, 1.0)).sum()),
        "misfit_pearson_below_one_expected": float(((counts - expected) ** 2)[expected < 1.0].sum()),
        "misfit_degrees_of_freedom": int(counts.size - len(ROWS) - TOMO.WINDOW),
        "per_setting_overlap": per_setting,
    }


def g2_pattern_overlap(
    runs: list[str], perfs: dict[str, Any], efficiency: list[float], grid: np.ndarray
) -> dict[str, Any]:
    """The two-click pattern overlap under Perceval's source model (``photon_distribution``: distinguishable noise
    photons at the plan read's g2) through threshold detection at the plan read's transmittance and per-mode dark
    click probabilities (``detected_clicks``), so three-photon events that lose a photon enter the two-click
    patterns. The relative efficiencies of the g2-free fit stay fixed; the overlap is the vertex of a parabola through
    the grid minimum and its neighbors."""
    counts, _ = pattern_counts(runs)
    g2 = float(perfs["g2 (%)"]) / 100.0
    transmittance = float(perfs["Transmittance (%)"]) / 100.0
    clock = float(perfs["Clock (MHz)"]) * 1e6
    dark = [float(rate) / clock for rate in perfs["Dark counts (detection/s)"]]
    weight = np.array([efficiency[i] * efficiency[j] for i, j in PAIRS])
    profile = []
    for overlap in grid:
        law = np.zeros((len(ROWS), len(PAIRS)))
        for s, r in enumerate(ROWS):
            photons = TOMO.photon_distribution(TOMO.setting_unitary(r), float(overlap), g2)
            for key, p in TOMO.detected_clicks(photons, transmittance, dark).items():
                on = [k for k, v in enumerate(key) if v]
                if len(on) == 2 and max(on) < TOMO.WINDOW:
                    law[s, PAIRS.index((on[0], on[1]))] += p
        law = law * weight
        profile.append(negative_log_likelihood(counts, law / law.sum(1, keepdims=True)))
    k = min(max(int(np.argmin(profile)), 1), len(grid) - 2)
    a, b, _ = np.polyfit(grid[k - 1 : k + 2], profile[k - 1 : k + 2], 2)
    return {"g2": g2, "transmittance": transmittance, "overlap": float(-b / (2 * a)), "grid": [float(m) for m in grid]}


def seeds_by_setting(runs: list[str]) -> dict[str, int]:
    out: dict[str, int] = {}
    for run in runs:
        for setting in RECORDS.read_run(ROOT / run).manifest["settings"]:
            out[setting["name"]] = int(setting["compilation_seed"])
    return out


def efficiency_corrected_fidelity(data: dict[str, np.ndarray], efficiency: list[float]) -> float:
    pair = np.array([efficiency[TOMO.C0 + a] * efficiency[TOMO.T0 + b] for a in (0, 1) for b in (0, 1)])
    rates = TOMO.absolute_rates(data["eligible"] / pair[None, :], data["shots"], data["scale"])
    return float(TOMO.estimate_rates(rates)["process_fidelity"])


def cross_run(found: dict[str, dict[str, Any]], laws: tuple[np.ndarray, np.ndarray]) -> dict[str, Any]:
    a, b = found["retained"]["gate_independent"]["entries"], found["band"]["gate_independent"]["entries"]
    out: dict[str, Any] = {}
    for kind, keep in (("bit_flip", "01"), ("equator_bias", "+i")):
        x = np.array([e["deviation"] for e in a if e["prepared"] in keep])
        y = np.array([e["deviation"] for e in b if e["prepared"] in keep])
        out[kind] = {"pearson_r": float(np.corrcoef(x, y)[0, 1]), "spearman_r": float(spearmanr(x, y)[0])}
    sensitivity = 0.5 * np.abs(laws[0] / laws[0].sum(1, keepdims=True) - laws[1] / laws[1].sum(1, keepdims=True)).sum(1)
    pa = np.array(found["retained"]["two_click_patterns"]["per_setting_overlap"])
    pb = np.array(found["band"]["two_click_patterns"]["per_setting_overlap"])
    identified = (sensitivity > IDENTIFIED_SENSITIVITY) & (pa > 0.01) & (pa < 0.99) & (pb > 0.01) & (pb < 0.99)
    out["per_setting_overlap"] = {
        "identified_settings": int(identified.sum()),
        "pearson_r_identified": float(np.corrcoef(pa[identified], pb[identified])[0, 1]),
        "pearson_r_all_including_unidentified": float(np.corrcoef(pa, pb)[0, 1]),
        "median_identified": {"retained": float(np.median(pa[identified])), "band": float(np.median(pb[identified]))},
        "sd_identified": {"retained": float(pa[identified].std()), "band": float(pb[identified].std())},
    }
    ma, mb = found["retained"]["two_click_patterns"], found["band"]["two_click_patterns"]
    events = mb["window_two_click_events"] / ma["window_two_click_events"]

    def parts(m: dict[str, Any]) -> tuple[float, float]:
        low = m["misfit_pearson_below_one_expected"]
        return low, m["misfit_pearson"] - low

    (la, ha), (lb, hb) = parts(ma), parts(mb)
    out["pattern_misfit_growth"] = {
        "event_ratio": events,
        "misfit_ratio": mb["misfit_pearson"] / ma["misfit_pearson"],
        "below_one_expected_ratio": lb / la,
        "at_least_one_expected_ratio": hb / ha,
    }
    ra, rb = found["retained"]["source_model_z"]["bit_flip"], found["band"]["source_model_z"]["bit_flip"]
    out["bit_flip_after_source_model"] = {
        "pearson_r": float(np.corrcoef(ra["residual"], rb["residual"])[0, 1]),
        "spearman_r": float(spearmanr(ra["residual"], rb["residual"])[0]),
    }
    sa, sb = found["retained"]["compilation_seeds"], found["band"]["compilation_seeds"]
    out["shared_compilation_seeds"] = sum(sa[name] == sb[name] for name in sa)
    return out


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        raise SystemExit("usage: analyze.py OUT.json")
    laws = pattern_laws()
    found: dict[str, dict[str, Any]] = {}
    datasets: dict[str, dict[str, np.ndarray]] = {}
    for name, spec in pairs_of_runs().items():
        data = datasets[name] = tallies(spec)
        patterns = two_click_patterns(laws, spec["runs"])
        perfs = CASE.plan_reads([spec["loader"](ROOT / run) for run in spec["runs"]])
        patterns["g2_aware"] = g2_pattern_overlap(spec["runs"], perfs, patterns["efficiency_relative_to_C0"], G2_GRID)
        found[name] = {
            "runs": spec["runs"],
            "pearson_split": pearson_split(data),
            "gate_independent": gate_independent(data),
            "rail_ratios": rail_ratios(data),
            "two_click_patterns": patterns,
            "efficiency_corrected_process_fidelity": efficiency_corrected_fidelity(
                data, patterns["efficiency_relative_to_C0"]
            ),
            "source_model_z": source_model_z(data, perfs, patterns["g2_aware"]["overlap"]),
            "implied_share_error": implied_share_error(data),
            "compilation_seeds": seeds_by_setting(spec["runs"]),
        }
    found["model_check_forecast"] = model_check_forecast(
        json.loads((ROOT / BAND_ANALYSIS).read_text(encoding="utf-8"))["overlap_estimates"]["overdispersion"],
        json.loads((ROOT / RETAINED_VERDICTS).read_text(encoding="utf-8"))["overlap_estimates"]["overdispersion"],
        found["retained"]["pearson_split"],
        datasets["retained"],
    )
    found["cross_run"] = cross_run(found, laws)
    found["cross_run"]["tomography_pearson_growth"] = tomography_cell_growth(datasets["retained"], datasets["band"])
    Path(argv[0]).write_text(json.dumps(found, indent=1, allow_nan=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
