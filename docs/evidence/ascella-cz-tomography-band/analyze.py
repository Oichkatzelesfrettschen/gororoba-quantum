"""Post-data decomposition of the Ascella CZ tomography reference band pair (2026-11-09) beside the retained pair
(2026-10-31). Every statistic here was chosen after the data arrived, so each one generates a hypothesis and none
decides a preregistered conjecture; the preregistered verdicts are those of
results/quandela/ascella-cz-tomography-reference-analysis.json.

Run from the repository root: ``"$PYTHON" docs/evidence/ascella-cz-tomography-band/analyze.py OUT.json``. The
output is deterministic (no random draw).

The sectors:

* Pearson split: the case's Pearson statistic (scripts/ascella_cz_tomography_reference_case.py ``pearson``) by
  cells whose linear-inversion prediction is below one event, and the clipped statistic split into per-setting
  throughput and within-setting outcome shape.
* Gate-independent sector: CZ is diagonal, so a qubit read out in Z keeps its prepared Z population whatever the
  gate, the photon overlap or the dephasing; outcome index is 2 * control + target.
* Rail ratios: inputs 00, 01 and 11 succeed with 1/9 at every overlap and 10 with (5 - 4M)/9, so r(00)/r(01) is a
  target-rail transmission ratio and r(01)/r(11) a control-rail one; D = r(10) r(01) / (r(00) r(11)) from ZZ
  readouts alone and from all nine readouts.
* Two-click patterns: photons enter C0 and T0; for output modes i < j the indistinguishable probability is
  |U[i,C0] U[j,T0] + U[j,C0] U[i,T0]|^2 and the distinguishable one |U[i,C0] U[j,T0]|^2 + |U[j,C0] U[i,T0]|^2,
  mixed linearly in the overlap M (exact for two photons, multiphoton emission ignored). A maximum-likelihood fit
  over all 15 window pairs of all 144 settings gives one M and six relative detection efficiencies per pair of
  runs; a common efficiency cancels in the conditional distribution.
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
IDENTIFIED_SENSITIVITY = 0.05  # total variation between the M = 0 and M = 1 pattern laws of a setting


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
    shape = ((n - total[:, None] * within) ** 2 / np.maximum(total[:, None] * within, 1.0)).sum(1)
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
    fit = minimize(objective, fit.x, method="BFGS")
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
        "overlap": overlap,
        "overlap_profile_interval": [float(inside.min()), float(inside.max())],
        "efficiency_relative_to_C0": [float(e) for e in efficiency],
        "misfit_pearson": float(((counts - expected) ** 2 / np.maximum(expected, 1.0)).sum()),
        "misfit_degrees_of_freedom": int(counts.size - len(ROWS) - TOMO.WINDOW),
        "per_setting_overlap": per_setting,
    }


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
    out["pattern_misfit_growth"] = {
        "event_ratio": events,
        "misfit_ratio": mb["misfit_pearson"] / ma["misfit_pearson"],
        "event_ratio_squared": events**2,
    }
    return out


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        raise SystemExit("usage: analyze.py OUT.json")
    laws = pattern_laws()
    found: dict[str, dict[str, Any]] = {}
    for name, spec in pairs_of_runs().items():
        data = tallies(spec)
        patterns = two_click_patterns(laws, spec["runs"])
        found[name] = {
            "runs": spec["runs"],
            "pearson_split": pearson_split(data),
            "gate_independent": gate_independent(data),
            "rail_ratios": rail_ratios(data),
            "two_click_patterns": patterns,
            "efficiency_corrected_process_fidelity": efficiency_corrected_fidelity(
                data, patterns["efficiency_relative_to_C0"]
            ),
        }
    found["cross_run"] = cross_run(found, laws)
    Path(argv[0]).write_text(json.dumps(found, indent=1, allow_nan=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
