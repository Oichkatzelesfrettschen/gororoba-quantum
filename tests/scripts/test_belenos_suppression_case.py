"""Contracts of the Belenos suppression-law request: the exact suppressed set, the frozen case and its analysis."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import belenos_suppression_case as case
import numpy as np
import pytest

SLOTS = (0, 2, 4)
# The twelve collision-free outputs of the six-mode Fourier matrix that three photons on ports 0, 2 and 4 never reach.
SUPPRESSED: tuple[tuple[int, ...], ...] = (
    (0, 1, 3),
    (0, 1, 4),
    (0, 2, 3),
    (0, 2, 5),
    (0, 3, 4),
    (0, 3, 5),
    (1, 2, 4),
    (1, 2, 5),
    (1, 3, 4),
    (1, 4, 5),
    (2, 4, 5),
    (2, 3, 5),
)


def test_periodic_input_suppresses_exactly_twelve_outputs() -> None:
    window = case.window_unitary("periodic", SLOTS)
    found = set(case.suppressed_set(window, SLOTS))
    if found != set(SUPPRESSED):
        raise AssertionError(f"suppressed set {sorted(found)}")
    if found != set(case.label_sum_rule()):
        raise AssertionError("the permanents disagree with the label-sum rule")
    law = case.indistinguishable_law(window, SLOTS)
    allowed = [out for out in case.triples() if out not in found]
    if len(allowed) != 8 or any(abs(law[out] - 1 / 24) > 1e-12 for out in allowed):
        raise AssertionError("an allowed output is not 1/24")
    if any(sum(out) % 3 for out in allowed):
        raise AssertionError("an allowed output has a label sum that is not a multiple of three")


def test_control_has_no_suppressed_output_and_shares_the_distinguishable_law() -> None:
    periodic, control = case.window_unitary("periodic", SLOTS), case.window_unitary("control", SLOTS)
    law = case.indistinguishable_law(control, SLOTS)
    if case.suppressed_set(control, SLOTS) or min(law.values()) < 4e-3:
        raise AssertionError(
            f"control suppressed set {case.suppressed_set(control, SLOTS)}, minimum {min(law.values())}"
        )
    flat_periodic, flat_control = case.distinguishable_law(periodic, SLOTS), case.distinguishable_law(control, SLOTS)
    if any(abs(flat_periodic[o] - 6 / 216) > 1e-12 or abs(flat_control[o] - 6 / 216) > 1e-12 for o in case.triples()):
        raise AssertionError("a distinguishable output is not uniform at 6 / 6^3")
    # Both arms program unitary matrices whose source columns are Fourier columns of their ports.
    transform = case.fourier(case.WINDOW)
    for arm, ports in case.ARMS.items():
        window = case.window_unitary(arm, SLOTS)
        if not np.allclose(window.conj().T @ window, np.eye(case.WINDOW), atol=1e-12):
            raise AssertionError(f"{arm} is not unitary")
        for slot, port in zip(SLOTS, sorted(ports), strict=True):
            if not np.allclose(window[:, slot], transform[:, port], atol=1e-12):
                raise AssertionError(f"{arm}: slot {slot} does not carry Fourier column {port}")


def test_smaller_fourier_choices_suppress_no_collision_free_output() -> None:
    """The mode counts below six give no suppressed collision-free three-photon output for any input."""
    import itertools

    for size in (3, 4, 5):
        unitary = case.fourier(size)
        for ports in itertools.combinations(range(size), 3):
            for out in itertools.combinations(range(size), 3):
                if abs(case.permanent(unitary[np.ix_(out, ports)])) < 1e-9:
                    raise AssertionError(f"m = {size}, input {ports} suppresses {out}")


def test_window_choice_and_seeds() -> None:
    catalogue = case.platform_read(case.CASES)
    if case.choose_window(catalogue) != (16, (16, 18, 20)):
        raise AssertionError(f"window {case.choose_window(catalogue)}")
    draw = json.loads((case.ROOT / case.DRAW).read_text(encoding="utf-8"))
    if list(case.COMPILATION_SEEDS) != draw["values"][:8] or len(set(case.COMPILATION_SEEDS)) != 8:
        raise AssertionError("compilation seeds are not the first eight values of the draw")
    if case.JOB_ORDER["job-00"] != ("periodic", "control", "control", "periodic"):
        raise AssertionError("job-00 is not an ABBA block")
    swapped = tuple("control" if arm == "periodic" else "periodic" for arm in case.JOB_ORDER["job-00"])
    if case.JOB_ORDER["job-01"] != swapped:
        raise AssertionError("job-01 does not swap the arms of job-00")


def test_retained_jobs_rebuild_and_bind() -> None:
    from qd_platform import template_experiment

    start, sources = 16, (16, 18, 20)
    for job, files in case.documents(start, sources).items():
        for name, data in files.items():
            if (case.CASES / job / name).read_bytes() != data:
                raise AssertionError(f"{job}/{name} differs from the builder's bytes")
        manifest, circuit = json.loads(files["cases.json"]), json.loads(files["circuit.json"])
        experiment, settings = template_experiment(manifest, circuit)
        if experiment is None or [s["arm"] for s in settings] != list(case.JOB_ORDER[job]):
            raise AssertionError(f"{job}: template binding")
        if manifest["min_detected_photons"] != 3 or manifest["max_duration"] > 300 or manifest["iterations"] != 4:
            raise AssertionError(f"{job}: budget fields")
        if circuit["input_state"] != case.source_state(sources):
            raise AssertionError(f"{job}: photons are not on the connected source modes")
        if any(circuit["input_state"][m] and m not in case.CONNECTED for m in range(case.MODES)):
            raise AssertionError(f"{job}: a photon enters an unconnected mode")
        for setting in settings:
            expected = [list(out) for out in SUPPRESSED] if setting["arm"] == "periodic" else []
            if sorted(setting["ideal"]["suppressed_outputs"]) != sorted(expected):
                raise AssertionError(f"{setting['name']}: suppressed outputs")


def test_slos_agrees_with_the_permanents_on_the_compiled_unitary() -> None:
    manifest = json.loads((case.CASES / "job-00/cases.json").read_text(encoding="utf-8"))
    circuit = json.loads((case.CASES / "job-00/circuit.json").read_text(encoding="utf-8"))
    for arm in case.ARMS:
        setting = next(s for s in manifest["settings"] if s["arm"] == arm)
        mass = case.check_slos(setting, circuit, 16)
        if abs(mass["collision_free"] - 1 / 3) > 1e-9:
            raise AssertionError(f"{arm}: collision-free mass {mass['collision_free']}")


def test_mean_field_average_is_exact_on_its_grid() -> None:
    emission: dict[tuple[int, ...], float] = {
        (1, 0, 1, 0, 1, 0): 0.9,
        (2, 0, 1, 0, 1, 0): 0.05,
        (1, 0, 2, 0, 2, 0): 0.05,
    }
    unitary = case.window_unitary("periodic", SLOTS)
    coarse = case.mean_field_distribution(unitary, emission)
    fine = case.mean_field_distribution(unitary, emission, case.PHASE_GRID + 3)
    if max(abs(coarse[o] - fine[o]) for o in coarse) > 1e-12:
        raise AssertionError("the mean-field phase average depends on the grid")
    if abs(sum(coarse.values()) - 1.0) > 1e-12:
        raise AssertionError("the mean-field distribution is not normalized")


@pytest.mark.audit
def test_full_check() -> None:
    if case.check() != 0:
        raise AssertionError("the frozen request does not check")


# ---------------------------------------------------------------- analysis


def _key(modes: set[int]) -> str:
    return ",".join("1" if mode in modes else "0" for mode in range(case.MODES))


def _state(slots: tuple[int, ...], start: int = 16) -> str:
    return _key({start + slot for slot in slots})


def _counts(fraction: float, events: int = 400) -> dict[str, int]:
    """Events split between the 12 suppressed and the 8 allowed outputs, plus events the selection excludes."""
    hits = round(fraction * events)
    counts: dict[str, int] = {}
    for index, out in enumerate(SUPPRESSED):
        counts[_state(out)] = hits // 12 + (1 if index < hits % 12 else 0)
    allowed = [o for o in case.triples() if o not in set(SUPPRESSED)]
    for index, out in enumerate(allowed):
        counts[_state(out)] = (events - hits) // 8 + (1 if index < (events - hits) % 8 else 0)
    counts[_key({0, 16, 17})] = 3
    return counts


def _entry(setting: dict[str, Any], fractions: dict[str, float]) -> dict[str, Any]:
    iteration = {"compilation_seed": setting["compilation_seed"], "circuit_params": setting["circuit_params"]}
    return {"counts": _counts(fractions[setting["arm"]]), "iteration": iteration}


def _run(
    tmp_path: Path,
    name: str,
    fractions: dict[str, float],
    iterations: int | None = None,
    order: list[int] | None = None,
) -> Path:
    manifest = json.loads((case.CASES / f"{name}/cases.json").read_text(encoding="utf-8"))
    entries = [_entry(setting, fractions) for setting in manifest["settings"][:iterations]]
    if order is not None:
        entries = [entries[k] for k in order]
    run = tmp_path / name
    run.mkdir()
    (run / "cases.json").write_text(json.dumps(manifest))
    (run / "results.json").write_text(json.dumps({"iterations": entries}))
    return run


def _analyze(tmp_path: Path, fractions: dict[str, float], iterations: int | None = None) -> dict[str, Any]:
    retained = json.loads((case.CASES / case.FORECAST).read_text(encoding="utf-8"))
    runs = [_run(tmp_path, job, fractions, iterations) for job in case.JOB_ORDER]
    return case.analyze(runs, retained)


def _forecast() -> dict[str, dict[str, float]]:
    retained = json.loads((case.CASES / case.FORECAST).read_text(encoding="utf-8"))["models"]
    return {arm: {m: retained[arm][m]["fraction"] for m in case.MODEL_NAMES} for arm in case.ARMS}


def test_tally_separates_the_excluded_causes() -> None:
    counts = _counts(0.5)
    counts[_state((0, 1, 2)).replace("1", "2", 1)] = 5
    counts[_key({16})] = 7
    tally = case.tally_iteration(counts, 16, {tuple(out) for out in SUPPRESSED})
    if tally["suppressed"] != 200 or tally["allowed"] != 200:
        raise AssertionError(f"accepted tally {tally}")
    if tally["outside_window"] < 3 or tally["collision"] != 5 or tally["fewer_than_three"] != 7:
        raise AssertionError(f"excluded tally {tally}")


def test_forecast_orders_the_models() -> None:
    forecast = _forecast()
    periodic, control = forecast["periodic"], forecast["control"]
    if periodic["ideal indistinguishable"] != 0.0:
        raise AssertionError("the ideal indistinguishable fraction is not zero")
    if not periodic["indistinguishable"] + 0.3 < min(periodic["distinguishable"], periodic["mean-field"]):
        raise AssertionError(f"the models do not separate: {periodic}")
    if max(abs(control[m] - control["indistinguishable"]) for m in case.MODEL_NAMES[1:]) > 0.1:
        raise AssertionError(f"the control separates the models: {control}")


def test_decision_reads_suppression_at_the_forecast(tmp_path: Path) -> None:
    forecast = _forecast()
    record = _analyze(
        tmp_path,
        {"periodic": forecast["periodic"]["indistinguishable"], "control": forecast["control"]["indistinguishable"]},
    )
    decision = record["decision"]
    if decision["verdict"] != "suppression at the level the indistinguishable forecast predicts":
        raise AssertionError(decision)
    if not decision["control_valid"] or not decision["suppression_observed"] or decision["level"] != "at":
        raise AssertionError(decision)
    if not 0.8 < decision["implied_hom"] < 0.95:
        raise AssertionError(f"implied HOM {decision['implied_hom']}")
    if record["pooled"]["periodic"]["events"] != 4 * 400 or record["excluded_events"]["outside_window"] == 0:
        raise AssertionError(record["pooled"])


@pytest.mark.parametrize(
    ("arm_fractions", "verdict"),
    [
        ({"periodic": 0.60, "control": 0.64}, "no suppression beyond the distinguishable and mean-field forecasts"),
        ({"periodic": 0.73, "control": 0.59}, "no suppression beyond the distinguishable and mean-field forecasts"),
        ({"periodic": 0.35, "control": 0.64}, "suppression weaker than the indistinguishable forecast"),
        ({"periodic": 0.06, "control": 0.64}, "suppression stronger than the indistinguishable forecast"),
        (
            {"periodic": 0.21, "control": 0.40},
            "invalid control: the detectors or the selection deplete or inflate the suppressed set",
        ),
    ],
)
def test_decision_separates_the_outcomes(tmp_path: Path, arm_fractions: dict[str, float], verdict: str) -> None:
    record = _analyze(tmp_path, arm_fractions)
    if record["decision"]["verdict"] != verdict:
        raise AssertionError(record["decision"])


def test_decision_waits_for_complete_arms(tmp_path: Path) -> None:
    forecast = _forecast()
    fractions = {
        "periodic": forecast["periodic"]["indistinguishable"],
        "control": forecast["control"]["indistinguishable"],
    }
    record = _analyze(tmp_path, fractions, iterations=3)
    if record["decision"]["verdict"] != "undecided" or record["decision"]["complete"]:
        raise AssertionError(record["decision"])
    single = tmp_path / "single"
    single.mkdir()
    retained = json.loads((case.CASES / case.FORECAST).read_text(encoding="utf-8"))
    record = case.analyze([_run(single, "job-00", fractions)], retained)
    if record["decision"]["verdict"] != "undecided":
        raise AssertionError("one job decides")


def test_manifest_preregisters_the_constants() -> None:
    manifest = json.loads((case.CASES / "job-00/cases.json").read_text(encoding="utf-8"))
    pre = copy.deepcopy(manifest["preregistered"])
    if (
        pre["alpha"] != case.ALPHA
        or pre["null_margin"] != case.NULL_MARGIN
        or pre["control_tolerance"] != case.CONTROL_TOLERANCE
    ):
        raise AssertionError(pre)


def test_result_iterations_bind_to_settings_by_seed(tmp_path: Path) -> None:
    """A reordered result and a dropped middle iteration leave every count in its own arm."""
    fractions = {"periodic": 0.20, "control": 0.64}
    retained = json.loads((case.CASES / case.FORECAST).read_text(encoding="utf-8"))
    straight = tmp_path / "straight"
    straight.mkdir()
    shuffled = tmp_path / "shuffled"
    shuffled.mkdir()
    dropped = tmp_path / "dropped"
    dropped.mkdir()
    runs = {
        "straight": [_run(straight, job, fractions) for job in case.JOB_ORDER],
        "shuffled": [_run(shuffled, job, fractions, order=[2, 0, 3, 1]) for job in case.JOB_ORDER],
        "dropped": [_run(dropped, job, fractions, order=[0, 2, 3]) for job in case.JOB_ORDER],
    }
    base = case.analyze(runs["straight"], retained)
    moved = case.analyze(runs["shuffled"], retained)
    if moved["summary"] != base["summary"] or moved["pooled"] != base["pooled"]:
        raise AssertionError("reordering the result iterations moved counts between arms")
    short = case.analyze(runs["dropped"], retained)
    periodic, control = short["pooled"]["periodic"], short["pooled"]["control"]
    if periodic["events"] != 3 * 400 or control["events"] != 3 * 400:
        raise AssertionError(f"dropped middle iteration: {short['pooled']}")
    if abs(periodic["fraction"] - 0.20) > 1e-9 or abs(control["fraction"] - 0.64) > 1e-9:
        raise AssertionError(f"counts moved between arms: {short['pooled']}")
    if short["decision"]["verdict"] != "undecided":
        raise AssertionError("a missing iteration still decides")


def test_unbound_result_iteration_is_refused(tmp_path: Path) -> None:
    run = _run(tmp_path, "job-00", {"periodic": 0.2, "control": 0.64})
    results = json.loads((run / "results.json").read_text(encoding="utf-8"))
    results["iterations"][1]["iteration"]["compilation_seed"] += 1
    (run / "results.json").write_text(json.dumps(results))
    retained = json.loads((case.CASES / case.FORECAST).read_text(encoding="utf-8"))
    with pytest.raises(ValueError, match="binds to 0 settings"):
        case.analyze([run], retained)
