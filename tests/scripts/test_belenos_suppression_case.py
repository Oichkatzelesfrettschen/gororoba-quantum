"""Contracts of the Belenos suppression-law request: the exact suppressed set, the frozen case and its analysis."""

from __future__ import annotations

import copy
import json
import shutil
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


@pytest.mark.audit
def test_retained_job_files_equal_the_builders_bytes() -> None:
    """Replay of the retained case files: the builder reproduces every one byte for byte."""
    for job, files in case.documents(16, (16, 18, 20)).items():
        for name, data in files.items():
            if (case.CASES / job / name).read_bytes() != data:
                raise AssertionError(f"{job}/{name} differs from the builder's bytes")


def test_built_jobs_bind_to_the_template() -> None:
    from qd_platform import template_experiment

    start, sources = 16, (16, 18, 20)
    for job, files in case.documents(start, sources).items():
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


def _serial_mean_field(
    unitary: np.ndarray, emission: dict[tuple[int, ...], float], grid: int
) -> dict[tuple[int, ...], float]:
    """The phase average as one serial loop over patterns, cells and outputs, the arithmetic the item map reproduces."""
    import itertools
    import math

    out: dict[tuple[int, ...], float] = {}
    phases = np.exp(2j * np.pi * np.arange(grid) / grid)
    for pattern, weight in emission.items():
        inputs = [slot for slot, count in enumerate(pattern) if count]
        total = sum(pattern)
        cells = list(itertools.product(range(grid), repeat=len(inputs) - 1))
        outputs = case.compositions(total)
        factor = [math.factorial(total) / math.prod(math.factorial(c) for c in occ) for occ in outputs]
        mixtures: dict[tuple[int, ...], float] = {}
        for cell in cells:
            phi = np.concatenate(([1.0 + 0j], phases[list(cell)]))
            amplitude = unitary[:, inputs] @ (np.sqrt([pattern[j] for j in inputs]) * phi)
            probability = np.abs(amplitude) ** 2 / total
            for occ, scale in zip(outputs, factor, strict=True):
                term = scale * float(np.prod(probability ** np.asarray(occ)))
                mixtures[occ] = mixtures.get(occ, 0.0) + term / len(cells)
        for occ, value in mixtures.items():
            out[occ] = out.get(occ, 0.0) + weight * value
    return out


def test_mean_field_item_map_reproduces_the_serial_average() -> None:
    """Mapping the (pattern, cell) items and reducing in order matches a serial loop to rounding, key order included."""
    emission: dict[tuple[int, ...], float] = {
        (1, 0, 1, 0, 1, 0): 0.9,
        (2, 0, 1, 0, 1, 0): 0.07,
        (1, 0, 2, 0, 2, 0): 0.03,
    }
    unitary = case.window_unitary("periodic", SLOTS)
    mapped = case.mean_field_distribution(unitary, emission)
    serial = _serial_mean_field(unitary, emission, case.PHASE_GRID)
    if list(mapped) != list(serial) or max(abs(mapped[o] - serial[o]) for o in mapped) > 1e-15:
        raise AssertionError("the mapped phase average differs from the serial loop")


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


def _perfs() -> dict[str, Any]:
    """The performance record of the case's platform read, the figures the retained forecast uses."""
    return dict(case.processor(case.platform_read(case.CASES))["perfs"])


@pytest.fixture(autouse=True)
def _cached_forecast(monkeypatch: pytest.MonkeyPatch) -> None:
    """Share one computation of case.forecast among the analyses that read the same performance record."""
    cache: dict[str, Any] = _FORECASTS
    original = case.forecast

    def cached(perfs: Any, start: int, sources: tuple[int, ...]) -> Any:
        key = json.dumps([perfs, start, list(sources)], sort_keys=True)
        if key not in cache:
            cache[key] = original(perfs, start, sources)
        return cache[key]

    monkeypatch.setattr(case, "forecast", cached)


_FORECASTS: dict[str, Any] = {}


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
    # The manifest keeps its retained bytes, which the analysis binds by sha256.
    shutil.copyfile(case.CASES / name / "cases.json", run / "cases.json")
    (run / "results.json").write_text(json.dumps({"iterations": entries}))
    (run / "submission.json").write_text(json.dumps({"perfs_at_plan": _perfs()}))
    return run


def _analyze(tmp_path: Path, fractions: dict[str, float], iterations: int | None = None) -> dict[str, Any]:
    runs = [_run(tmp_path, job, fractions, iterations) for job in case.JOB_ORDER]
    return case.analyze(runs)


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
    if "hom_lower_bound" in decision:
        raise AssertionError("the HOM inverse of a point estimate carries no bound name")
    low, point, high = (decision[k] for k in ("hom_at_periodic_upper", "hom_at_periodic_mean", "hom_at_periodic_lower"))
    if not low <= point <= high or abs(point - 0.879) > 0.005:
        raise AssertionError(f"HOM inverses {low} {point} {high}")
    if (
        record["pooled"]["periodic"]["events"] != 4 * 400
        or record["excluded_events"]["periodic"]["outside_window"] == 0
    ):
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
    record = case.analyze([_run(single, "job-00", fractions)])
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
    base = case.analyze(runs["straight"])
    moved = case.analyze(runs["shuffled"])
    if moved["summary"] != base["summary"] or moved["pooled"] != base["pooled"]:
        raise AssertionError("reordering the result iterations moved counts between arms")
    short = case.analyze(runs["dropped"])
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
    with pytest.raises(ValueError, match="binds to 0 settings"):
        case.analyze([run])


def _runs(tmp_path: Path, fractions: dict[str, float]) -> list[Path]:
    runs = []
    for job in case.JOB_ORDER:
        parent = tmp_path / f"runs-{job}"
        parent.mkdir()
        runs.append(_run(parent, job, fractions))
    return runs


def _rewrite(run: Path, edit: Any) -> None:
    results = json.loads((run / "results.json").read_text(encoding="utf-8"))
    edit(results["iterations"])
    (run / "results.json").write_text(json.dumps(results))


@pytest.mark.parametrize("entry", [{"missing": True}, {"malformed": True}, {"error": "worker failed"}])
def test_cut_short_job_reads_undecided(tmp_path: Path, entry: dict[str, Any]) -> None:
    """qd_platform.result_summary appends an entry without counts or iteration for each lost iteration."""
    runs = _runs(tmp_path, {"periodic": 0.21, "control": 0.64})
    _rewrite(runs[1], lambda iterations: iterations.__setitem__(3, dict(entry)))
    record = case.analyze(runs)
    kind = next(iter(entry))
    if record["decision"]["verdict"] != "undecided" or record["uncounted_iterations"][kind] != 1:
        raise AssertionError(record["decision"], record["uncounted_iterations"])
    if record["summary"]["control"]["iterations"] != 3 or record["summary"]["periodic"]["iterations"] != 4:
        raise AssertionError(record["summary"])


def test_the_same_job_twice_is_refused(tmp_path: Path) -> None:
    fractions = {"periodic": 0.21, "control": 0.64}
    first, second = tmp_path / "first", tmp_path / "second"
    first.mkdir()
    second.mkdir()
    runs = [_run(first, "job-00", fractions), _run(second, "job-00", fractions)]
    with pytest.raises(ValueError, match="repeats job job-00"):
        case.analyze(runs)


def test_a_repeat_under_another_name_cannot_reuse_seeds(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A manifest retained next to the case still shares no compilation seed with another run."""
    runs = _runs(tmp_path, {"periodic": 0.21, "control": 0.64})
    family = tmp_path / "family"
    shutil.copytree(case.CASES, family)
    manifest = json.loads((family / "job-01/cases.json").read_text(encoding="utf-8"))
    original = json.loads((family / "job-00/cases.json").read_text(encoding="utf-8"))
    manifest["settings"][0]["compilation_seed"] = original["settings"][0]["compilation_seed"]
    (family / "job-01/cases.json").write_text(json.dumps(manifest))
    shutil.copyfile(family / "job-01/cases.json", runs[1] / "cases.json")
    monkeypatch.setattr(case, "CASES", family)
    with pytest.raises(ValueError, match="reuses compilation seeds"):
        case.analyze(runs)


def _swap_arms(manifest: dict[str, Any]) -> None:
    for setting in manifest["settings"]:
        setting["arm"] = "control" if setting["arm"] == "periodic" else "periodic"


def _rename_job(manifest: dict[str, Any]) -> None:
    manifest["job"] = "job-09"


def _empty_suppressed_set(manifest: dict[str, Any]) -> None:
    for setting in manifest["settings"]:
        setting["ideal"]["suppressed_outputs"] = []


def _move_window(manifest: dict[str, Any]) -> None:
    manifest["layout"]["window_start"] += 1


@pytest.mark.parametrize("edit", [_swap_arms, _rename_job, _empty_suppressed_set, _move_window])
def test_a_manifest_that_differs_from_the_retained_case_is_refused(tmp_path: Path, edit: Any) -> None:
    """The run-local cases.json carries the job identity, arm labels and suppressed set, so it equals a retained one."""
    runs = _runs(tmp_path, {"periodic": 0.21, "control": 0.64})
    manifest = json.loads((runs[0] / "cases.json").read_text(encoding="utf-8"))
    edit(manifest)
    (runs[0] / "cases.json").write_bytes((json.dumps(manifest, indent=1) + "\n").encode())
    with pytest.raises(ValueError, match="no manifest retained"):
        case.analyze(runs)


def test_a_manifest_with_other_bytes_is_refused(tmp_path: Path) -> None:
    runs = _runs(tmp_path, {"periodic": 0.21, "control": 0.64})
    manifest = json.loads((runs[0] / "cases.json").read_text(encoding="utf-8"))
    (runs[0] / "cases.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="no manifest retained"):
        case.analyze(runs)


def _submission(run: Path, edit: Any) -> None:
    path = run / "submission.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    edit(record)
    path.write_text(json.dumps(record))


def _drop_perfs(record: dict[str, Any]) -> None:
    del record["perfs_at_plan"]


def _keep_hom_only(record: dict[str, Any]) -> None:
    record["perfs_at_plan"] = {"HOM (%)": 88.6}


def _drop_per_mode(record: dict[str, Any]) -> None:
    del record["perfs_at_plan"]["Transmission per mode (%)"]


def _nan_hom(record: dict[str, Any]) -> None:
    record["perfs_at_plan"]["HOM (%)"] = float("nan")


def _short_t_out(record: dict[str, Any]) -> None:
    record["perfs_at_plan"]["Transmission per mode (%)"]["t_out"].pop()


@pytest.mark.parametrize("edit", [_drop_perfs, _keep_hom_only, _drop_per_mode, _nan_hom, _short_t_out])
def test_a_run_without_its_own_perfs_is_refused(tmp_path: Path, edit: Any) -> None:
    """The forecast of a run reads that run's perfs_at_plan; no retained or other run's figures stand in."""
    runs = _runs(tmp_path, {"periodic": 0.21, "control": 0.64})
    _submission(runs[1], edit)
    with pytest.raises(ValueError, match="perfs_at_plan"):
        case.analyze(runs)


def _zero_t_out(mode: int) -> Any:
    def edit(record: dict[str, Any]) -> None:
        record["perfs_at_plan"]["Transmission per mode (%)"]["t_out"][mode] = 0.0

    return edit


def test_a_dead_detector_outside_the_window_leaves_the_forecast_intact(tmp_path: Path) -> None:
    """The forecast reads t_out on the window modes and its maximum, so a zero elsewhere is a valid record."""
    runs = _runs(tmp_path, {"periodic": 0.21, "control": 0.64})
    start = json.loads((runs[1] / "cases.json").read_text(encoding="utf-8"))["layout"]["window_start"]
    _submission(runs[1], _zero_t_out(start + case.WINDOW))
    _submission(runs[1], _zero_t_out(start - 1))
    case.analyze(runs)


@pytest.mark.parametrize("offset", [0, case.WINDOW - 1])
def test_a_dead_detector_inside_the_window_is_refused(tmp_path: Path, offset: int) -> None:
    runs = _runs(tmp_path, {"periodic": 0.21, "control": 0.64})
    start = json.loads((runs[1] / "cases.json").read_text(encoding="utf-8"))["layout"]["window_start"]
    _submission(runs[1], _zero_t_out(start + offset))
    with pytest.raises(ValueError, match="perfs_at_plan"):
        case.analyze(runs)


def test_a_record_without_a_positive_t_out_is_refused(tmp_path: Path) -> None:
    runs = _runs(tmp_path, {"periodic": 0.21, "control": 0.64})
    for mode in range(case.MODES):
        _submission(runs[1], _zero_t_out(mode))
    with pytest.raises(ValueError, match="perfs_at_plan"):
        case.analyze(runs)


def test_the_hom_inverses_bracket_the_point_estimate(tmp_path: Path) -> None:
    """The inverses of the periodic mean and of its two one-sided limits order as the fractions do, descending."""
    runs = _runs(tmp_path, {"periodic": 0.20, "control": 0.64})
    spread = {"job-00": (0.14, 0.18), "job-01": (0.17, 0.20)}

    def vary(run: Path, fractions: tuple[float, float]) -> None:
        manifest = json.loads((run / "cases.json").read_text(encoding="utf-8"))
        results = json.loads((run / "results.json").read_text(encoding="utf-8"))
        seen = iter(fractions * 2)
        for setting, entry in zip(manifest["settings"], results["iterations"], strict=True):
            if setting["arm"] == "periodic":
                entry["counts"] = _counts(next(seen))
        (run / "results.json").write_text(json.dumps(results))

    for run in runs:
        vary(run, spread[json.loads((run / "cases.json").read_text(encoding="utf-8"))["job"]])
    decision = case.analyze(runs)["decision"]
    summary = case.analyze(runs)["summary"]["periodic"]
    low, point, high = (decision[k] for k in ("hom_at_periodic_upper", "hom_at_periodic_mean", "hom_at_periodic_lower"))
    if not (summary["lower"] < summary["mean"] < summary["upper"] and low < point < high):
        raise AssertionError((summary, low, point, high))
    forecasts = [case.run_forecast(run, json.loads((run / "cases.json").read_text(encoding="utf-8"))) for run in runs]
    if abs(case.interpolated_hom(summary["mean"], forecasts) - point) > 1e-12:
        raise AssertionError("the point estimate is not the inverse of the periodic mean")


def test_a_run_without_a_submission_record_is_refused(tmp_path: Path) -> None:
    runs = _runs(tmp_path, {"periodic": 0.21, "control": 0.64})
    (runs[0] / "submission.json").unlink()
    with pytest.raises(ValueError, match="submission.json is missing"):
        case.analyze(runs)


def test_the_forecast_follows_the_run_perfs(tmp_path: Path) -> None:
    """A run's own HOM moves the forecast of the analysis, so no fixed figure supplies it."""
    runs = _runs(tmp_path, {"periodic": 0.21, "control": 0.64})
    before = case.analyze(runs)["forecast"]["periodic"]["indistinguishable"]

    def lower_hom(record: dict[str, Any]) -> None:
        record["perfs_at_plan"]["HOM (%)"] -= 10.0

    for run in runs:
        _submission(run, lower_hom)
    after = case.analyze(runs)["forecast"]["periodic"]["indistinguishable"]
    if not after > before + 0.05:
        raise AssertionError((before, after))


@pytest.mark.parametrize("mutation", ["omit", "shift", "unit_key", "nan"])
def test_an_iteration_must_echo_its_circuit_params(tmp_path: Path, mutation: str) -> None:
    run = _run(tmp_path, "job-00", {"periodic": 0.21, "control": 0.64})

    def edit(iterations: list[dict[str, Any]]) -> None:
        params = iterations[1]["iteration"]
        if mutation == "omit":
            del params["circuit_params"]
        elif mutation == "shift":
            first = next(iter(params["circuit_params"]))
            params["circuit_params"][first] += 0.1
        elif mutation == "unit_key":
            params["circuit_params"].popitem()
        else:
            first = next(iter(params["circuit_params"]))
            params["circuit_params"][first] = float("nan")

    _rewrite(run, edit)
    with pytest.raises(ValueError, match="circuit_params"):
        case.analyze([run])


def test_an_iteration_below_the_event_floor_does_not_count(tmp_path: Path) -> None:
    runs = _runs(tmp_path, {"periodic": 0.21, "control": 0.64})
    _rewrite(runs[1], lambda iterations: iterations.__setitem__(0, {**iterations[0], "counts": _counts(0.0, 3)}))
    record = case.analyze(runs)
    if record["decision"]["verdict"] != "undecided" or len(record["below_event_floor"]) != 1:
        raise AssertionError(record["decision"], record["below_event_floor"])
    if record["below_event_floor"][0]["accepted"] != 3 or record["summary"]["control"]["iterations"] != 3:
        raise AssertionError(record["below_event_floor"])


def test_the_paired_contrast_is_a_second_rule(tmp_path: Path) -> None:
    """A periodic fraction under the absolute limit still fails when the control is not clearly above it."""
    record = _analyze(tmp_path, {"periodic": 0.48, "control": 0.55})
    decision = record["decision"]
    if not decision["absolute_rule"] or decision["contrast_rule"] or decision["suppression_observed"]:
        raise AssertionError(decision)
    if decision["verdict"] != "no suppression beyond the distinguishable and mean-field forecasts":
        raise AssertionError(decision)


def test_exclusions_are_reported_per_arm_and_iteration(tmp_path: Path) -> None:
    record = _analyze(tmp_path, {"periodic": 0.21, "control": 0.64})
    if set(record["excluded_events"]) != {"periodic", "control"}:
        raise AssertionError(record["excluded_events"])
    if any("excluded" not in row for rows in record["iterations"].values() for row in rows):
        raise AssertionError("an iteration lacks its exclusion tally")
    if record["excluded_events"]["periodic"]["outside_window"] != 4 * 3:
        raise AssertionError(record["excluded_events"])


def test_budget_models_a_fixed_part_and_a_shot_cost() -> None:
    healthy = case.modeled_seconds(case.SHOTS_PER_ITERATION, 4)
    degraded = case.modeled_seconds(case.SHOTS_PER_ITERATION, 4, case.DEGRADED_SECONDS_PER_SHOT)
    if not 104 < healthy < 105 or not 237 < degraded < 240 or degraded >= case.MAX_DURATION:
        raise AssertionError((healthy, degraded))
    if case.expected_seconds(case.SHOTS_PER_ITERATION, 4) != 180.0:
        raise AssertionError("expected seconds")
