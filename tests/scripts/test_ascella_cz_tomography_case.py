"""Contracts of the Ascella postselected CZ process tomography request: the gate block, the folded settings, the
estimator and the analysis."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

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


def test_forecast_and_coverage_seeds_are_new_values_of_owned_draws() -> None:
    seeds, bootstrap = case.seed_plan()
    taken = {index for index, _ in seeds} | {bootstrap[0]}
    forecast = case.forecast_seeds()
    if len(forecast) != len(case.FORECAST_VARIANTS) or taken & {index for index, _ in forecast}:
        raise AssertionError("a forecast seed reuses a case seed or is missing")
    coverage = case.coverage_seeds()
    if len(coverage) != case.COVERAGE_DATASETS or case.COVERAGE_DATASETS < 200:
        raise AssertionError(f"{len(coverage)} coverage seeds")
    values = [value for _, value in forecast + coverage]
    if len({value for _, value in coverage}) != len(coverage) or 0 in values or case.COVERAGE_DRAW == case.DRAW:
        raise AssertionError("a coverage seed repeats, is zero, or shares the case draw")


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
    if study["datasets"] < 200 or "coverage_exact_binomial_interval" not in study:
        raise AssertionError("the coverage study lacks 200 datasets or its binomial interval")


def _choi_rates(choi: np.ndarray) -> np.ndarray:
    coefficients = np.array([float(np.real(np.trace(element @ choi))) for element in case.hermitian_basis()])
    return np.asarray(case.design_matrix() @ coefficients)


def test_depolarized_gate_is_recovered() -> None:
    """Outcome frequencies of (1 - p) CZ + p (completely depolarizing) give the analytic F = (1 - p) + p / 16."""
    p = 0.2
    vector = case.ideal_choi_vector()
    choi = (1 - p) * np.outer(vector, vector.conj()) + p * np.eye(16) / 4
    expected = (1 - p) + p / 16
    conditional = case.estimate(_choi_rates(choi))
    primary = case.estimate_rates(_choi_rates(choi))
    for found in (conditional["process_fidelity"], primary["process_fidelity"]):
        if abs(found - expected) > 1e-9:
            raise AssertionError(f"fidelity {found} against {expected}")


def test_absolute_rate_estimator_recovers_a_map_with_input_dependent_success() -> None:
    """A postselected map M rho M^dagger with M = CZ diag(1, .8, .6, .5) succeeds with an input-dependent probability.
    The rates of its Choi matrix give F = |Tr(CZ^dagger M)|^2 / (4 Tr(M^dagger M)) exactly under the primary
    estimator, while the per-setting normalization misses it."""
    operator = case.ideal_cz() @ np.diag([1.0, 0.8, 0.6, 0.5])
    vector = np.sum([np.kron(np.eye(4)[i], operator[:, i]) for i in range(4)], axis=0)
    choi = np.outer(vector, vector.conj())
    rates = _choi_rates(choi)
    expected = abs(np.trace(case.ideal_cz().conj().T @ operator)) ** 2 / (
        4 * np.real(np.trace(operator.conj().T @ operator))
    )
    primary = case.estimate_rates(rates)
    if abs(primary["process_fidelity"] - expected) > 1e-9:
        raise AssertionError(f"primary {primary['process_fidelity']} against {expected}")
    outcomes = rates.reshape(144, 4)
    conditional = case.estimate((outcomes / outcomes.sum(axis=1)[:, None]).reshape(-1))
    if abs(conditional["process_fidelity"] - expected) < 1e-3:
        raise AssertionError("the conditional estimator no longer differs, so the test shows nothing")


def _write_run(
    directory: Path,
    job: str,
    *,
    drop: int = 0,
    reverse: bool = False,
    transmittance: float = 5.82,
    hom: float = 87.54,
    hour: int = 0,
    entries: dict[int, dict] | None = None,
) -> None:
    raw = (case.FAMILY_DIR / job / "cases.json").read_bytes()
    manifest = json.loads(raw)
    (directory / "cases.json").write_bytes(raw)
    iterations = []
    for setting in manifest["settings"]:
        counts = {}
        for outcome, probability in enumerate(setting["ideal"]["outcome_probabilities"]):
            vector = [0] * case.MODES
            vector[case.C0 + outcome // 2] = 1
            vector[case.T0 + outcome % 2] = 1
            if round(4000 * probability):
                counts[",".join(str(v) for v in vector)] = round(4000 * probability)
        counts[",".join(["1"] * 3 + ["0"] * 9)] = 11
        iterations.append(
            {
                "iteration": {"compilation_seed": setting["compilation_seed"]},
                "counts": counts,
                "samples": sum(counts.values()),
                "result_fields": {"nb_shots_used": 10 * sum(counts.values())},
            }
        )
    for position, replacement in (entries or {}).items():
        iterations[position] = replacement
    iterations = iterations[: len(iterations) - drop]
    if reverse:
        iterations.reverse()
    (directory / "results.json").write_text(json.dumps({"iterations": iterations}))
    submission = {
        "perfs_at_plan": {"HOM (%)": hom, "Transmittance (%)": transmittance},
        "submitted_utc": f"2026-11-01T{hour:02d}:00:00+00:00",
    }
    (directory / "submission.json").write_text(json.dumps(submission))


def _runs(tmp_path: Path, **second: Any) -> list[Path]:
    runs = []
    for job in case.JOBS:
        run = tmp_path / job
        run.mkdir(parents=True)
        _write_run(run, job, **(second if job == case.JOBS[1] else {}))
        runs.append(run)
    return runs


def test_analysis_pools_both_jobs(tmp_path: Path) -> None:
    record = case.analyze(_runs(tmp_path), replicates=8)
    process = record["process"]
    if abs(process["process_fidelity"] - 1.0) > 1e-3 or process["bootstrap"]["replicates"] != 8:
        raise AssertionError(f"pooled ideal counts give {process}")
    low, high = process["process_fidelity_interval"]
    if not low <= high <= 1.0 + 1e-9 or record["excluded_by_cause"]["three_or_more_clicks"] != 144 * 11:
        raise AssertionError(f"interval {low}, {high}; exclusions {record['excluded_by_cause']}")
    if process["status"] != "decided" or abs(process["conditional_process_fidelity"] - 1.0) > 1e-3:
        raise AssertionError(
            f"pooling status {process['status']}, conditional {process['conditional_process_fidelity']}"
        )


def test_iterations_bind_by_echoed_seed_not_by_position(tmp_path: Path) -> None:
    straight = case.analyze(_runs(tmp_path / "a"), replicates=8)["process"]
    reversed_ = case.analyze(_runs(tmp_path / "b", reverse=True), replicates=8)["process"]
    if abs(straight["process_fidelity"] - reversed_["process_fidelity"]) > 1e-12:
        raise AssertionError("a reordered job gives another estimate")
    if straight["process_fidelity_interval"] != reversed_["process_fidelity_interval"]:
        raise AssertionError("a reordered job gives another interval")


def test_seed_binding_refuses_unknown_and_repeated_seeds(tmp_path: Path) -> None:
    manifest = json.loads((case.FAMILY_DIR / case.JOBS[1] / "cases.json").read_text())
    first = manifest["settings"][0]["compilation_seed"]
    repeated = {
        1: {"iteration": {"compilation_seed": first}, "counts": {"1": 1}, "result_fields": {"nb_shots_used": 5}}
    }
    absent = max(setting["compilation_seed"] for setting in manifest["settings"]) + 1
    unknown = {
        1: {"iteration": {"compilation_seed": absent}, "counts": {"1": 1}, "result_fields": {"nb_shots_used": 5}}
    }
    for label, bad in (("repeated", repeated), ("unknown", unknown)):
        runs = _runs(tmp_path / label, entries=bad)
        try:
            case.analyze(runs, replicates=8)
        except RuntimeError:
            continue
        raise AssertionError(f"a {label} echoed seed is accepted")


def test_a_run_must_equal_the_retained_case_and_the_runs_must_differ(tmp_path: Path) -> None:
    runs = _runs(tmp_path / "a")
    (runs[0] / "cases.json").write_bytes((runs[0] / "cases.json").read_bytes() + b" ")
    for pair in (runs, [runs[1], runs[1]]):
        try:
            case.analyze(pair, replicates=8)
        except RuntimeError:
            continue
        raise AssertionError("an edited case or a repeated job is accepted")


def test_partial_record_returns_undecided_and_counts_uncounted_entries(tmp_path: Path) -> None:
    entries = {70: {"missing": True}, 71: {"error": "worker failed"}, 69: {"malformed": "NoneType"}}
    record = case.analyze(_runs(tmp_path, entries=entries), replicates=8)
    kinds = record["uncounted_by_kind"]
    if record["process"] != "undecided" or kinds["missing"] != 1 or kinds["error"] != 1 or kinds["malformed"] != 1:
        raise AssertionError(f"partial record gives {record['process']} with {kinds}")
    cut = case.analyze(_runs(tmp_path / "cut", drop=3), replicates=8)
    if cut["process"] != "undecided" or cut["settings_with_counts"] != 141:
        raise AssertionError(f"truncated run gives {cut['process']}, {cut['settings_with_counts']}")


def test_pooling_scales_by_transmittance_and_flags_drift(tmp_path: Path) -> None:
    near = case.analyze(_runs(tmp_path / "near", transmittance=5.62), replicates=8)["process"]
    expected = case.shot_ratio(5.82) / case.shot_ratio(5.62)
    if near["status"] != "decided" or abs(near["pooling"]["scales"][case.JOBS[1]] - expected) > 1e-12:
        raise AssertionError(f"near pool {near['status']}, scales {near['pooling']['scales']}")
    far_hom = case.analyze(_runs(tmp_path / "hom", hom=80.0), replicates=8)["process"]
    far_gap = case.analyze(_runs(tmp_path / "gap", hour=20), replicates=8)["process"]
    far_t = case.analyze(_runs(tmp_path / "t", transmittance=6.5), replicates=8)["process"]
    if {far_hom["status"], far_gap["status"], far_t["status"]} != {"descriptive"}:
        raise AssertionError("a drifted pool is not descriptive")
