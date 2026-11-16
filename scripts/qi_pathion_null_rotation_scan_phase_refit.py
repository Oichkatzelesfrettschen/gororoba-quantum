"""Exploratory refit of the retained Tuna-17 null rotation scan histograms under gate noise and a q12 phase.

The 30 data circuits of `pathion_null_rotation_scan_tuna_17` (10 data batches of 3 circuits, each batch between two
readout brackets) are read through the retained shots. Each circuit's 32 logical outcome counts are compared with a
density-matrix forward model of the retained b0 circuit (five region qubits, the arm's pulse rewrite, the gate-noise
terms below) pushed through the joint readout matrix that the mean of the two adjacent brackets defines. The
statistic is the Pearson chi-square of the 30 x 32 counts, with 30 x 31 degrees of freedom less the free parameters.

Models (every model is a fit of those counts; nothing else is read):

- exact_circuit: no free parameter; the exact pulses and CZ gates.
- exact_circuit_batch_retention: one retention per data batch contracts the exact law toward uniform.
- five_noise_terms: pulse amplitude and phase damping, CZ depolarizing, CZ amplitude damping and CZ phase damping.
- five_noise_terms_selector_flip: the five terms and a selector flip of probability `flip` when bit d0 reads 0.
- five_noise_terms_q12_z_after_pulse: the five terms and a z rotation of q12 after each of its pulses.
- cz_noise_flip_q12_z_after_pulse / cz_noise_flip_q12_z_after_cz: CZ damping and dephasing, the selector flip and
  a q12 z rotation after each pulse of q12, or after each CZ that touches q12.

Evidence class: exploratory post-hoc fit of retained shots; no provider job, no random draw, no preregistered
decision. A parameter that sits on a bound is reported as such (`at_bound`), and degrees of freedom count every
declared parameter. Every model carries its starts, bounds, step scales and difference step, and one rule for the
expected probability in the Pearson denominator (a floor of CLIP). `--check` replays the headline fits and requires
agreement within TOLERANCE, the reproducibility that the optimizer's own stopping tolerance supports across BLAS
builds, and that the stored search found no lower chi-square. `--profile` replays that search: a phase profile with
refinement for the two q12-phase models, four starts for each five-noise-term model and ten one-dimensional
retention profiles. The search draws no random number.

The forward model and the fits live in gororoba_quantum/gate_noise_histogram_fit.py and take the circuit and arm
tables as an explicit `Experiment`; this script selects the retained inputs of the series, declares the seven models
and holds the record, the replay and the command line.

Usage: `--write DIR` writes DIR/RECORD with the search; `--check DIR` replays the headline fits against DIR/RECORD;
`--profile DIR` replays the search; `--self-test` runs the simulator and optimizer against exact laws and planted
parameters.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from functools import cache
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "gororoba_quantum")]
import qi_pathion_null_rotation_scan_cases as rs  # noqa: E402
import qi_pathion_null_rotation_scan_noise as ns  # noqa: E402

import gate_noise_histogram_fit as gnf  # noqa: E402
from parallel import ordered_map  # noqa: E402

SCHEMA = "qi-pathion-null-rotation-scan-phase-refit-v2"
RECORD = "pathion_null_rotation_scan_tuna_17_phase_refit.json"
RUNS = "results/quantum_inspire/runs"
RUN_PREFIX = "2026-11-15T001929Z-pathion_null_rotation_scan_tuna_17-batch-"
TOLERANCE = 1e-5
CLIP = gnf.CLIP
FLIP_BIT = "d0"
FLIP_STATE = 0
Z_QUBIT = 12
BOUND_FRACTION = 1e-4

Observation = gnf.Observation
FitSpec = gnf.FitSpec
SearchResult = gnf.SearchResult


# Loading ------------------------------------------------------------------------------------------------------------


def verify_raw_files(directory: Path, listed: list[str]) -> None:
    """The raw directory of a run holds exactly the files its retained manifest lists, one `FILE.json` per circuit."""
    expected = sorted(f"{name}.json" for name in listed)
    raw = directory / "raw"
    actual = sorted(p.name for p in raw.iterdir()) if raw.is_dir() else []
    if actual != expected:
        raise ValueError(f"{directory.name}/raw holds {actual}, the manifest lists {expected}")


def run_directories() -> list[Path]:
    """The run directories the series plan names, each with the raw files its retained manifest lists."""
    runs: list[Path] = []
    for row in rs.batch_rows(rs.TUNA_SERIES):
        directory = ROOT / RUNS / f"{RUN_PREFIX}{row['batch'][-2:]}"
        manifest = json.loads((directory / "cases.json").read_text(encoding="utf-8"))
        listed = [circuit["file"] for circuit in manifest["circuits"]]
        planned = [circuit["file"] for circuit in row["circuits"]]
        if sorted(listed) != sorted(planned):
            raise ValueError(f"{directory.name} lists {sorted(listed)}, the series plan holds {sorted(planned)}")
        verify_raw_files(directory, listed)
        runs.append(directory)
    return runs


def observations() -> tuple[list[Observation], list[Path]]:
    """The 30 scan circuits with counts over the logical outcome index and the readout matrix of their brackets."""
    cc, pca, pcs = rs.cc, rs.pca, rs.pcs
    runs = run_directories()
    data = pca.read_series(runs, pcs.CASES_ROOT, rs.series_of, "data", rs.BATCH_FIELDS, pcs.load_run)
    shots, manifest = data["shots"], data["shared"]
    roles = {k: int(v) for k, v in manifest["templates"]["b0"]["roles"].items()}
    register = [int(q) for q in manifest["register"]]
    plan = {row["batch"]: row for row in rs.batch_rows(rs.TUNA_SERIES)}
    names = sorted(plan)
    brackets: dict[str, dict[int, tuple[float, float]]] = {}
    for b in names:
        if plan[b]["kind"] != "readout":
            continue
        assignment = cc.batch_assignment(shots, b, register)
        if assignment is None:
            raise ValueError(f"readout batch {b} of the retained series lacks its bracket pair")
        brackets[b] = assignment
    found: list[Observation] = []
    for position, batch in enumerate(names):
        row = plan[batch]
        if row["kind"] == "readout":
            continue
        before, after = brackets[names[position - 1]], brackets[names[position + 1]]
        mean = {q: ((before[q][0] + after[q][0]) / 2, (before[q][1] + after[q][1]) / 2) for q in register}
        for circuit in row["circuits"]:
            found.append(
                {
                    "batch": batch,
                    "kind": row["kind"],
                    "arm": rs.arm_of(circuit["file"]),
                    "counts": cc.coin_counts(shots[f"{batch}/{circuit['file']}"], roles),
                    "matrix": cc.readout_matrix(mean, roles),
                }
            )
    return found, runs


def data_digest(found: list[Observation]) -> str:
    payload = [
        {
            "batch": o["batch"],
            "arm": o["arm"],
            "counts": [int(c) for c in o["counts"]],
            "matrix": [[float(x) for x in row] for row in o["matrix"]],
        }
        for o in found
    ]
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


# Forward model inputs ---------------------------------------------------------------------------------------------


@cache
def experiment() -> gnf.Experiment:
    """The retained b0 circuit and the scan's arm table, as the explicit inputs of the forward model."""
    ref = rs.retained()
    return gnf.Experiment(
        ops=ref["ops"],
        region=ref["region"],
        roles=ref["roles"],
        keys=tuple(rs.KEYS),
        arms=rs.ARMS,
        scopes=rs.SCOPES,
        step=rs.STEP,
        selector="selector",
        flip_bit=FLIP_BIT,
        flip_state=FLIP_STATE,
    )


# Models ------------------------------------------------------------------------------------------------------------

NOISE_BOUNDS = {"pa": (0.0, 0.3), "pp": (0.0, 0.3), "cd": (0.0, 0.5), "ca": (0.0, 0.3), "cp": (0.0, 0.3)}
NOISE_START = {"pa": 0.003, "pp": 0.003, "cd": 0.02, "ca": 0.005, "cp": 0.005}
EXTRA_BOUNDS = {"flip": (0.0, 0.2), f"z{Z_QUBIT}": (-0.3, 0.3)}
EXTRA_START = {"flip": 0.02, f"z{Z_QUBIT}": 0.0}


def noise_spec(name: str, extra: tuple[str, ...]) -> FitSpec:
    """The noise-family fit: start values and step scales of the first exploratory sweep (scale = upper bound / 10)."""
    free = (*NOISE_BOUNDS, *extra)
    bounds = {**NOISE_BOUNDS, **EXTRA_BOUNDS}
    start = {**NOISE_START, **EXTRA_START}
    return FitSpec(
        name,
        free,
        tuple(start[k] for k in free),
        tuple(bounds[k][0] for k in free),
        tuple(bounds[k][1] for k in free),
        tuple(max(abs(bounds[k][1]), 1e-3) / 10 for k in free),
    )


def phase_spec(name: str, phase: str) -> FitSpec:
    """The CZ-damping fit with the selector flip and one q12 phase, as the exploratory phase sweep set it."""
    return FitSpec(
        name,
        ("ca", "cp", "flip", phase),
        (0.02, 0.03, 0.017, 0.0),
        (0.0, 0.0, 0.0, -0.4),
        (0.3, 0.3, 0.2, 0.4),
        (0.01, 0.01, 0.01, 0.03),
    )


SPECS = (
    noise_spec("five_noise_terms", ()),
    noise_spec("five_noise_terms_selector_flip", ("flip",)),
    noise_spec("five_noise_terms_q12_z_after_pulse", (f"z{Z_QUBIT}",)),
    phase_spec("cz_noise_flip_q12_z_after_pulse", f"z{Z_QUBIT}"),
    phase_spec("cz_noise_flip_q12_z_after_cz", f"c{Z_QUBIT}"),
)
EXACT = "exact_circuit"
RETENTION = "exact_circuit_batch_retention"
MODEL_NAMES = (EXACT, RETENTION, *(spec.name for spec in SPECS))


def contrast_chi2(found: list[Observation], predicted: list[np.ndarray]) -> tuple[float, dict[str, float]]:
    """Chi-square of the 30 selector contrasts against the model's, in total and by scan kind."""
    by_kind: dict[str, float] = {}
    for o, p in zip(found, predicted, strict=True):
        stat = rs.count_statistics(o["counts"])
        model = float(rs.selector_contrast(p[None, :])[0])
        by_kind[o["kind"]] = by_kind.get(o["kind"], 0.0) + ((stat["contrast"] - model) / stat["se"]) ** 2
    return float(sum(by_kind.values())), by_kind


def summary(
    found: list[Observation], predicted: list[np.ndarray], n_free: int, histogram: float, values: dict[str, float]
) -> dict[str, Any]:
    total, by_kind = contrast_chi2(found, predicted)
    return {
        "n_free": n_free,
        "dof": len(found) * (rs.NOUT - 1) - n_free,
        "histogram_chi2": histogram,
        "min_expected_probability": min(float(p.min()) for p in predicted),
        "contrast_chi2": total,
        "contrast_chi2_by_kind": dict(sorted(by_kind.items())),
        "values": {k: float(v) for k, v in values.items()},
    }


def exact_item(found: list[Observation]) -> tuple[str, dict[str, Any]]:
    histogram = float(np.sum(gnf.pearson(found, gnf.predict(experiment(), found, {})) ** 2))
    return EXACT, {"values": {}, "histogram_chi2": histogram, "optimizer_status": None}


def retention_item(found: list[Observation]) -> tuple[str, dict[str, Any]]:
    """The exact law contracted toward uniform by one retention per data batch (a free-retention contraction)."""
    return RETENTION, gnf.fit_retention(experiment(), found)


def config(name: str, found: list[Observation]) -> dict[str, Any]:
    """The free parameters of a model with their stored starts, step scales, difference step and bounds."""
    if name == EXACT:
        return {"free": [], "start": {}, "x_scale": {}, "diff_step": None, "bounds": {}}
    if name == RETENTION:
        free = [f"retention_{b}" for b in sorted({o["batch"] for o in found})]
        return {
            "free": free,
            "start": dict.fromkeys(free, gnf.RETENTION_START),
            "x_scale": dict.fromkeys(free, 1.0),
            "diff_step": None,
            "bounds": {k: list(gnf.RETENTION_BOUNDS) for k in free},
        }
    spec = next(s for s in SPECS if s.name == name)
    return {
        "free": list(spec.free),
        "start": dict(zip(spec.free, spec.start, strict=True)),
        "x_scale": dict(zip(spec.free, spec.x_scale, strict=True)),
        "diff_step": gnf.DIFF_STEP,
        "bounds": {k: [lo, hi] for k, lo, hi in zip(spec.free, spec.lower, spec.upper, strict=True)},
    }


def evaluate(found: list[Observation], name: str, values: dict[str, float]) -> dict[str, Any]:
    """The statistics of a model at one parameter point: chi-squares, degrees of freedom, smallest expected
    probability and the parameters that sit on a bound."""
    if name == RETENTION:
        exact = gnf.arm_laws(experiment(), gnf.arms_of(found), {})
        predicted = gnf.retained_laws(found, exact, values)
    else:
        predicted = gnf.predict(experiment(), found, values)
    histogram = float(np.sum(gnf.pearson(found, predicted) ** 2))
    bounds = config(name, found)["bounds"]
    record = summary(found, predicted, len(bounds), histogram, values)
    record["at_bound"] = [
        k
        for k, (lo, hi) in bounds.items()
        if values[k] <= lo + BOUND_FRACTION * (hi - lo) or values[k] >= hi - BOUND_FRACTION * (hi - lo)
    ]
    return record


def fit_all(found: list[Observation]) -> dict[str, dict[str, Any]]:
    """Every model's fit from its stored start; the independent fits map over the process pool, in declaration order."""
    results = dict(ordered_map(gnf.fit_item, [(experiment(), spec, found) for spec in SPECS], min_items=2))
    exact_name, exact = exact_item(found)
    retention_name, retention = retention_item(found)
    ordered = {exact_name: exact, retention_name: retention, **results}
    if tuple(ordered) != MODEL_NAMES:
        raise ValueError(f"fitted models {tuple(ordered)} differ from the declared {MODEL_NAMES}")
    return ordered


def search_all(found: list[Observation], stored: dict[str, dict[str, Any]]) -> dict[str, SearchResult]:
    """The search of every model; `stored` holds the fits from the stored starts."""
    searches: dict[str, SearchResult] = {
        EXACT: ({"method": "no free parameter", "starts": 0}, [], []),
        RETENTION: gnf.retention_search(experiment(), found),
    }
    for spec in SPECS:
        if spec.name.startswith("cz_noise"):
            searches[spec.name] = gnf.phase_search(experiment(), spec, found)
        else:
            searches[spec.name] = gnf.noise_search(experiment(), spec, found, stored[spec.name]["values"])
    return {name: searches[name] for name in MODEL_NAMES}


def headline_models(
    found: list[Observation], stored: dict[str, dict[str, Any]], searches: dict[str, SearchResult]
) -> dict[str, dict[str, Any]]:
    """Each model at the lowest chi-square of its stored-start fit and its search, with the start that produced it."""
    models: dict[str, dict[str, Any]] = {}
    for name in MODEL_NAMES:
        record, candidates, fits = searches[name]
        start = stored[name]
        label, _, values = min(
            [("stored start", start["histogram_chi2"], start["values"]), *candidates], key=lambda c: c[1]
        )
        headline = evaluate(found, name, values)
        converged = [start["histogram_chi2"], *fits] if name != EXACT else [start["histogram_chi2"]]
        block = {
            **record,
            "best_histogram_chi2": headline["histogram_chi2"],
            "best_minus_headline": 0.0,
            "spread_histogram_chi2": max(converged) - min(converged),
        }
        models[name] = {
            **config(name, found),
            **headline,
            "headline_start": label,
            "stored_start_histogram_chi2": start["histogram_chi2"],
            "stored_start_optimizer_status": start["optimizer_status"],
            "search": block,
        }
    return models


def replayed_models(
    found: list[Observation], stored: dict[str, dict[str, Any]], retained: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    """Each retained headline point evaluated again, beside the replayed fit from the stored start."""
    return {
        name: {
            **config(name, found),
            **evaluate(found, name, retained[name]["values"]),
            "headline_start": retained[name]["headline_start"],
            "stored_start_histogram_chi2": stored[name]["histogram_chi2"],
            "stored_start_optimizer_status": stored[name]["optimizer_status"],
        }
        for name in MODEL_NAMES
    }


def stored_minimum(search: dict[str, Any]) -> float | None:
    """The lowest chi-square that the stored statistics of a model's search hold: its start fits, its phase profile
    or the sum of its batch profiles; None for a model that ran no start."""
    if "start_histogram_chi2" in search:
        return float(min(search["start_histogram_chi2"]))
    if "profile_histogram_chi2" in search:
        return float(min(search["profile_histogram_chi2"]))
    if "batch_histogram_chi2" in search:
        return float(sum(search["batch_histogram_chi2"].values()))
    return None


def verify_search(models: dict[str, dict[str, Any]]) -> None:
    """No stored start, profile point or batch profile sum reaches a chi-square below the headline by more than the
    tolerance, the stored best stays at or above the headline, and the headline stands at or below the fit from the
    stored start."""
    problems = []
    for name, model in models.items():
        headline = model["histogram_chi2"]
        search = model["search"]
        slack = TOLERANCE * max(1.0, abs(headline))
        if search["best_histogram_chi2"] < headline - slack:
            problems.append(f"{name}: {search['best_histogram_chi2']!r} below the headline {headline!r}")
        lowest = stored_minimum(search)
        if lowest is None:
            if search.get("starts"):
                problems.append(f"{name}: {search['starts']} starts stored with no per-start statistic")
        elif lowest < headline - slack:
            problems.append(f"{name}: a stored search statistic {lowest!r} is below the headline {headline!r}")
        if headline > model["stored_start_histogram_chi2"] + slack:
            problems.append(f"{name}: headline {headline!r} above its stored-start fit")
    if problems:
        raise ValueError(f"the search found a lower minimum or the headline is not the lowest: {problems}")


# A model and the smaller model it contains: the smaller one's parameters absent from the larger stand at zero.
NESTING = (
    (RETENTION, EXACT),
    ("five_noise_terms", EXACT),
    ("five_noise_terms_selector_flip", "five_noise_terms"),
    ("five_noise_terms_q12_z_after_pulse", "five_noise_terms"),
    ("five_noise_terms_q12_z_after_pulse", "cz_noise_flip_q12_z_after_pulse"),
)
NESTING_ZERO = 1e-6


def verify_nesting(models: dict[str, dict[str, Any]]) -> None:
    """A larger model fits at least as well as the smaller model it contains, within the tolerance."""
    problems = []
    for larger, smaller in NESTING:
        big, small = models[larger], models[smaller]
        for key in small["free"]:
            if key in big["free"]:
                lower, upper = big["bounds"][key]
                if not lower <= small["values"][key] <= upper:
                    problems.append(f"{smaller} holds {key}={small['values'][key]!r} outside the bounds of {larger}")
            elif abs(small["values"][key]) > NESTING_ZERO:
                problems.append(f"{smaller} holds {key}={small['values'][key]!r}, so {larger} does not contain it")
        slack = TOLERANCE * max(1.0, abs(small["histogram_chi2"]))
        if big["histogram_chi2"] > small["histogram_chi2"] + slack:
            problems.append(
                f"{larger} reads {big['histogram_chi2']!r}, above the {smaller} model it contains "
                f"({small['histogram_chi2']!r})"
            )
    if problems:
        raise ValueError(f"the models break the nesting order: {problems}")


# Record -------------------------------------------------------------------------------------------------------------


def build(search: bool = True, retained: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    """The record. With `search`, every headline is the lowest point of the stored-start fit and the search; without
    it, the headline points of `retained` are evaluated again beside the replayed stored-start fits."""
    found, runs = observations()
    kinds = sorted({o["kind"] for o in found})
    if len(found) != 30 or kinds != ["all10", "all20", "bridge", "q4-10", "q8-10"]:
        raise ValueError(f"expected 30 scan circuits of five kinds, read {len(found)} of {kinds}")
    stored = fit_all(found)
    if search:
        models = headline_models(found, stored, search_all(found, stored))
        verify_nesting(models)
    elif retained is None:
        raise ValueError("a replay without the search needs the retained models")
    else:
        models = replayed_models(found, stored, retained)
    return {
        "schema": SCHEMA,
        "evidence_class": "exploratory post-hoc fit of retained shots; no provider job, no random draw",
        "series": rs.TUNA_SERIES,
        "runs": [run.name for run in runs],
        "data_sha256": data_digest(found),
        "observations": len(found),
        "outcomes_per_observation": rs.NOUT,
        "statistic": "Pearson chi-square of the 32 logical outcome counts of each circuit against the model law read "
        "through the mean of the two adjacent readout brackets; contrast_chi2 is the 30-circuit selector-contrast "
        "chi-square",
        "expected_probability_floor": CLIP,
        "floor_rule": "an expected probability below the floor enters the Pearson denominator as the floor, in every "
        "model; min_expected_probability is the smallest expected probability of a model at its headline point",
        "tolerance": TOLERANCE,
        "models": models,
    }


def render(record: dict[str, Any]) -> str:
    return json.dumps(record, indent=1, sort_keys=True, allow_nan=False) + "\n"


def write(directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / RECORD
    target.write_text(render(build()), encoding="utf-8")
    return target


def differences(retained: Any, fresh: Any, path: str = "") -> list[str]:
    """Every place where `fresh` leaves `retained`: other types, keys, text or integers, or floats beyond TOLERANCE."""
    if isinstance(retained, dict) and isinstance(fresh, dict):
        unpaired = sorted(set(retained) ^ set(fresh))
        if unpaired:
            return [f"{path or '.'}: keys {unpaired} on one side only"]
        found: list[str] = []
        for key in sorted(retained):
            found += differences(retained[key], fresh[key], f"{path}.{key}")
        return found
    if isinstance(retained, list) and isinstance(fresh, list):
        if len(retained) != len(fresh):
            return [f"{path or '.'}: length {len(retained)} -> {len(fresh)}"]
        found = []
        for index, (left, right) in enumerate(zip(retained, fresh, strict=True)):
            found += differences(left, right, f"{path}[{index}]")
        return found
    if isinstance(retained, float) and isinstance(fresh, float):
        close = abs(retained - fresh) <= TOLERANCE * max(1.0, abs(retained))
        return [] if close else [f"{path}: {retained!r} -> {fresh!r}"]
    same = type(retained) is type(fresh) and retained == fresh
    return [] if same else [f"{path or '.'}: {retained!r} -> {fresh!r}"]


def without_search(record: dict[str, Any]) -> dict[str, Any]:
    """The record with the search section of every model removed."""
    stripped = json.loads(json.dumps(record))
    for model in stripped["models"].values():
        model.pop("search", None)
    return stripped


def check(directory: Path, fresh: dict[str, Any] | None = None) -> None:
    """The headline points of the retained record evaluate again to the stored statistics, the fit from each stored
    start replays, no stored search found a lower minimum and the nesting order of the models holds.

    A difference raises ValueError listing the first of them. The search itself replays under `profile`."""
    retained = json.loads((directory / RECORD).read_text(encoding="utf-8"))
    if any("search" not in model for model in retained["models"].values()):
        raise ValueError(f"{directory / RECORD} stores no search section for a model")
    replay = build(search=False, retained=retained["models"]) if fresh is None else fresh
    found = differences(without_search(retained), replay)
    if found:
        raise ValueError(f"{directory / RECORD} differs from the replay in {len(found)} places: {found[:10]}")
    verify_search(retained["models"])
    verify_nesting(retained["models"])


def profile(directory: Path, fresh: dict[str, Any] | None = None) -> None:
    """Replay the whole search: the record equals it, no start beats a headline and the nesting order holds."""
    retained = json.loads((directory / RECORD).read_text(encoding="utf-8"))
    replay = build() if fresh is None else fresh
    problems = differences(retained, replay)
    if problems:
        raise ValueError(
            f"{directory / RECORD} differs from its search replay in {len(problems)} places: {problems[:10]}"
        )
    verify_search(replay["models"])
    verify_nesting(replay["models"])


# Self-test ----------------------------------------------------------------------------------------------------------

PLANTED = {"ca": 0.015, "cp": 0.035, f"z{Z_QUBIT}": -0.1}
PLANTED_ARMS = (rs.CENTER, "b0-rx-q4-p10", "b0-rx-q8-m10", "b0-rx-all-p20")
PLANTED_SHOTS = 1_000_000
PLANTED_RETENTION = 0.6


def planted_observations(values: dict[str, float]) -> list[Observation]:
    """Expected counts of the planted model through a perfect readout, one circuit per arm."""
    identity = np.eye(rs.NOUT)
    laws = gnf.arm_laws(experiment(), list(PLANTED_ARMS), values)
    return [
        {
            "batch": f"planted-{n}",
            "kind": "planted",
            "arm": arm,
            "counts": PLANTED_SHOTS * laws[arm],
            "matrix": identity,
        }
        for n, arm in enumerate(PLANTED_ARMS)
    ]


def self_test() -> str:
    """The simulator against the exact and noisy laws of the repository, then a planted parameter recovered."""
    exact_arms = (rs.RETAINED, rs.CENTER, "b0-rx-all-p20")
    exact = gnf.arm_laws(experiment(), list(exact_arms), {})
    for arm in exact_arms:
        gap = float(np.abs(exact[arm] - rs.forward_law(arm)).max())
        if gap > 1e-10:
            raise AssertionError(f"the simulator differs from forward_law on {arm} by {gap}")
    noise = (0.002, 0.003, 0.01, 0.004, 0.005)
    values = dict(zip(("pa", "pp", "cd", "ca", "cp"), noise, strict=True)) | {"delta": 0.05}
    reference = ns.noisy_law("b0-rx-q8-p10", noise, None, 0.0, cz_phase=0.05)
    gap = float(np.abs(gnf.law(experiment(), "b0-rx-q8-p10", values) - reference).max())
    if gap > 1e-9:
        raise AssertionError(f"the simulator differs from noisy_law by {gap}")
    matrix = gnf.flip_matrix(experiment(), 0.1)
    if float(np.abs(matrix.sum(axis=0) - 1.0).max()) > 1e-15:
        raise AssertionError("the selector flip is not a stochastic matrix")
    if not np.array_equal(matrix, rs.oc.selector_flip(rs.KEYS.index(FLIP_BIT), FLIP_STATE, 0.1)):
        raise AssertionError("the selector flip differs from the case module's")
    found = planted_observations(PLANTED)
    spec = FitSpec(
        "planted",
        ("ca", "cp", f"z{Z_QUBIT}"),
        (0.02, 0.03, 0.0),
        (0.0, 0.0, -0.4),
        (0.3, 0.3, 0.4),
        (0.01, 0.01, 0.03),
    )
    _, fit = gnf.fit_item((experiment(), spec, found))
    for key, truth in PLANTED.items():
        if abs(fit["values"][key] - truth) > 1e-4:
            raise AssertionError(f"planted {key}={truth} recovered as {fit['values'][key]}")
    if fit["histogram_chi2"] > 1.0:
        raise AssertionError(f"planted fit leaves chi-square {fit['histogram_chi2']}")
    blind = FitSpec("blind", ("ca", "cp"), (0.02, 0.03), (0.0, 0.0), (0.3, 0.3), (0.01, 0.01))
    _, miss = gnf.fit_item((experiment(), blind, found))
    if miss["histogram_chi2"] < 100.0 * max(fit["histogram_chi2"], 1.0):
        raise AssertionError(f"a model without the planted q12 phase fits it: {miss['histogram_chi2']}")
    exact = gnf.arm_laws(experiment(), list(PLANTED_ARMS), {})
    retained = [
        {
            "batch": "planted",
            "kind": "planted",
            "arm": arm,
            "counts": PLANTED_SHOTS * gnf.contract(exact[arm], PLANTED_RETENTION),
            "matrix": np.eye(rs.NOUT),
        }
        for arm in PLANTED_ARMS
    ]
    _, retention_chi2, retention = gnf.retention_profile_item(("planted", retained, exact))
    if abs(retention - PLANTED_RETENTION) > 1e-6 or retention_chi2 > 1e-3:
        raise AssertionError(f"planted retention {PLANTED_RETENTION} profiled as {retention} at {retention_chi2}")
    fake = {"histogram_chi2": 100.0, "stored_start_histogram_chi2": 100.0, "search": {"best_histogram_chi2": 100.0}}
    verify_search({"m": fake})
    verify_search(
        {
            "m": {
                **fake,
                "search": {
                    "best_histogram_chi2": 100.0,
                    "start_histogram_chi2": [100.0, 40000.0],
                    "starts": 2,
                },
            }
        }
    )
    for bad in (
        {"search": {"best_histogram_chi2": 99.0}},
        {"search": {"best_histogram_chi2": 100.0, "start_histogram_chi2": [100.0, 40000.0, 99.0]}},
        {"search": {"best_histogram_chi2": 100.0, "profile_histogram_chi2": [101.0, 99.0]}},
        {"search": {"best_histogram_chi2": 100.0, "batch_histogram_chi2": {"a": 60.0, "b": 39.0}}},
        {"search": {"best_histogram_chi2": 100.0, "starts": 4}},
        {"stored_start_histogram_chi2": 99.0},
    ):
        try:
            verify_search({"m": {**fake, **bad}})
        except ValueError:
            continue
        raise AssertionError(f"verify_search passes {bad}")
    largest_first = (
        "five_noise_terms_q12_z_after_pulse",
        "five_noise_terms_selector_flip",
        RETENTION,
        "cz_noise_flip_q12_z_after_pulse",
        "five_noise_terms",
        EXACT,
    )
    ordered = {
        name: {"free": [], "values": {}, "bounds": {}, "histogram_chi2": 10.0 * rank}
        for rank, name in enumerate(largest_first)
    }
    verify_nesting(ordered)
    ordered[RETENTION]["histogram_chi2"] = 1e9
    try:
        verify_nesting(ordered)
    except ValueError:
        pass
    else:
        raise AssertionError("verify_nesting passes a larger model that fits worse than the model it contains")
    return (
        f"qi_pathion_null_rotation_scan_phase_refit self-test: OK (noisy_law gap {gap:.1e}; planted q12 phase "
        f"{fit['values'][f'z{Z_QUBIT}']:+.5f} recovered, chi-square {fit['histogram_chi2']:.2e}, "
        f"{miss['histogram_chi2']:.0f} without it; planted retention {retention:.6f} profiled)"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", type=Path, metavar="DIR")
    mode.add_argument("--check", type=Path, metavar="DIR")
    mode.add_argument("--profile", type=Path, metavar="DIR")
    mode.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.write is not None:
        print(f"wrote {write(args.write)}")
    elif args.check is not None or args.profile is not None:
        try:
            if args.check is not None:
                check(args.check)
            else:
                profile(args.profile)
        except ValueError as error:
            print(error, file=sys.stderr)
            return 1
        print(f"{(args.check or args.profile) / RECORD} matches the replay")
    else:
        print(self_test())
    return 0


if __name__ == "__main__":
    sys.exit(main())
