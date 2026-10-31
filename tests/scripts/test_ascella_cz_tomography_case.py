"""Contracts of the Ascella postselected CZ process tomography request: the gate block, the folded settings, the
estimator and the analysis."""

from __future__ import annotations

import json
from pathlib import Path

import ascella_cz_tomography_case as case
import numpy as np


def test_retained_request_rebuilds_and_binds() -> None:
    if case.check() != 0:
        raise AssertionError("the frozen request does not check")


def test_ideal_process_fidelity_is_one() -> None:
    point = case.estimate(case.ideal_frequencies())
    if abs(point["process_fidelity"] - 1.0) > 1e-9 or abs(point["average_gate_fidelity"] - 1.0) > 1e-9:
        raise AssertionError(f"ideal fidelities {point['process_fidelity']}, {point['average_gate_fidelity']}")


def test_cz_block_is_diagonal_with_one_third_amplitude() -> None:
    block = case.coincidence_block(case.cz_unitary())
    if np.abs(block - np.diag([1.0, 1.0, 1.0, -1.0]) / 3).max() > 1e-9:
        raise AssertionError("the coincidence block of the CZ unitary is not diag(1, 1, 1, -1) / 3")
    probability = case.exact_outcomes(case.schedule()[0])[1]
    if abs(probability - 1 / 9) > 1e-12:
        raise AssertionError(f"success probability {probability}")


def test_schedule_covers_144_settings_in_two_balanced_jobs() -> None:
    rows = case.schedule()
    if len(rows) != 144 or len({row["name"] for row in rows}) != 144:
        raise AssertionError("the schedule does not hold 144 distinct settings")
    sizes = [len(case.job_rows(job)) for job in case.JOBS]
    if sizes != [72, 72]:
        raise AssertionError(f"job sizes {sizes}")
    for job in case.JOBS:
        inputs = {row["input"] for row in case.job_rows(job)}
        if len(inputs) != 8 or {label for pair in inputs for label in pair} != set(case.INPUT_STATES):
            raise AssertionError(f"{job}: inputs {sorted(inputs)}")


def test_seeds_come_once_from_the_retained_draw() -> None:
    seeds, bootstrap = case.seed_plan()
    values = [value for _, value in seeds] + [bootstrap[1]]
    draw = case.draw_values()
    if any(draw[index] != value for index, value in seeds + [bootstrap]):
        raise AssertionError("a seed differs from its draw index")
    if len(set(values)) != 145 or 0 in values or len({index for index, _ in seeds + [bootstrap]}) != 145:
        raise AssertionError("a seed repeats, is zero, or shares an index")
    for job in case.JOBS:
        manifest = json.loads((case.FAMILY_DIR / job / "cases.json").read_text())
        if manifest["compilation_seeds"]["draw"] != case.DRAW:
            raise AssertionError(f"{job} names another draw")
        if [s["compilation_seed"] for s in manifest["settings"]] != [
            draw[i] for i in manifest["compilation_seeds"]["indices"]
        ]:
            raise AssertionError(f"{job}: seeds differ from the draw at the named indices")


def test_forecast_seeds_are_new_values_of_the_owned_draw() -> None:
    seeds, bootstrap = case.seed_plan()
    taken = {index for index, _ in seeds} | {bootstrap[0]}
    forecast = case.forecast_seeds()
    if len(forecast) != len(case.FORECAST_VARIANTS) + case.COVERAGE_DATASETS:
        raise AssertionError(f"{len(forecast)} forecast seeds")
    if taken & {index for index, _ in forecast} or len({value for _, value in forecast}) != len(forecast):
        raise AssertionError("a forecast seed reuses a case seed or repeats")


def test_basic_interval_reflects_the_percentile_interval_about_the_point() -> None:
    values = list(np.linspace(0.70, 0.78, 201))
    found = case.intervals(0.80, values, 0.95)
    low, high = found["percentile"]
    if abs(found["basic"][0] - (1.60 - high)) > 1e-12 or abs(found["basic"][1] - (1.60 - low)) > 1e-12:
        raise AssertionError(f"basic interval {found['basic']} against percentile {found['percentile']}")


def test_retained_forecast_interval_kind_has_nominal_coverage() -> None:
    forecast = json.loads((case.FAMILY_DIR / case.FORECAST).read_text())
    study = forecast["coverage_study"]
    if forecast["interval"] != case.INTERVAL_KIND or study["coverage"][case.INTERVAL_KIND] < case.COVERAGE_FLOOR:
        raise AssertionError(f"coverage of the {case.INTERVAL_KIND} interval: {study['coverage']}")


def test_depolarized_gate_is_recovered() -> None:
    """Outcome frequencies of (1 - p) CZ + p (completely depolarizing) give the analytic F = (1 - p) + p / 16."""
    p = 0.2
    vector = case.ideal_choi_vector()
    choi = (1 - p) * np.outer(vector, vector.conj()) + p * np.eye(16) / 4
    coefficients = np.array([float(np.real(np.trace(element @ choi))) for element in case.hermitian_basis()])
    frequencies = case.design_matrix() @ coefficients
    point = case.estimate(frequencies)
    expected = (1 - p) + p / 16
    if abs(point["process_fidelity"] - expected) > 1e-9:
        raise AssertionError(f"fidelity {point['process_fidelity']} against {expected}")


def _write_run(directory: Path, job: str, scale: int, drop: int = 0) -> None:
    manifest = json.loads((case.FAMILY_DIR / job / "cases.json").read_text())
    (directory / "cases.json").write_text(
        json.dumps({k: manifest[k] for k in ("family", "job", "settings", "preregistered")})
    )
    iterations = []
    for setting in manifest["settings"]:
        counts = {}
        for outcome, probability in enumerate(setting["ideal"]["outcome_probabilities"]):
            vector = [0] * case.MODES
            vector[case.C0 + outcome // 2] = 1
            vector[case.T0 + outcome % 2] = 1
            if round(scale * probability):
                counts[",".join(str(v) for v in vector)] = round(scale * probability)
        counts[",".join(["1"] * 3 + ["0"] * 9)] = 11
        iterations.append({"counts": counts})
    (directory / "results.json").write_text(json.dumps({"iterations": iterations[: len(iterations) - drop]}))


def test_analysis_pools_both_jobs(tmp_path: Path) -> None:
    runs = []
    for job in case.JOBS:
        run = tmp_path / job
        run.mkdir()
        _write_run(run, job, 4000)
        runs.append(run)
    record = case.analyze(runs, replicates=8)
    process = record["process"]
    if abs(process["process_fidelity"] - 1.0) > 1e-3 or process["bootstrap"]["replicates"] != 8:
        raise AssertionError(f"pooled ideal counts give {process}")
    low, high = process["process_fidelity_interval"]
    if not low <= high <= 1.0 + 1e-9 or record["excluded_by_cause"]["three_or_more_clicks"] != 144 * 11:
        raise AssertionError(f"interval {low}, {high}; exclusions {record['excluded_by_cause']}")


def test_missing_iteration_leaves_the_estimate_undecided(tmp_path: Path) -> None:
    runs = []
    for job, drop in zip(case.JOBS, (0, 3), strict=True):
        run = tmp_path / job
        run.mkdir()
        _write_run(run, job, 4000, drop)
        runs.append(run)
    record = case.analyze(runs, replicates=8)
    if record["process"] != "undecided" or record["settings_with_counts"] != 141:
        raise AssertionError(f"truncated run gives {record['process']}, {record['settings_with_counts']}")
