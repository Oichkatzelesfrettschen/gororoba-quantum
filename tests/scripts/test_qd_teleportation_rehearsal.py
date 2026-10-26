"""Contract of the single-chip teleportation rehearsal: the template reproduces the ideal instrument, the retained
request is byte-stable and bound to its plan, the analysis scores a joint histogram, and malformed records refuse.
"""

from __future__ import annotations

import copy
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pytest
import qd_network_protocol as protocol
import qd_teleportation_rehearsal as rehearsal
from qd_classical_benchmark import attempts_benchmark
from qd_schedule import body_digest

ROOT = Path(__file__).resolve().parents[2]
CASE = rehearsal.CASES / "job-00"
LABELS = [label for label, *_ in protocol.SIX_STATES]
IDEAL = rehearsal.Variant("ideal", 1.0, 0.0, (1.0,) * rehearsal.MODES)


def load(name: str) -> Any:
    return json.loads((CASE / name).read_text(encoding="utf-8"))


def event(pattern: str, raw: int, extra: tuple[int, ...] = ()) -> str:
    """The count key of an event: the pattern on the analyzer modes, raw bit on b, and any further chip modes."""
    clicks = [0] * rehearsal.MODES
    for mode, flag in zip(rehearsal.ANALYZER_MODES, pattern, strict=True):
        clicks[rehearsal.LAYOUT[mode]] = int(flag)
    clicks[rehearsal.LAYOUT[rehearsal.B0 if raw == 0 else rehearsal.B1]] = 1
    for mode in extra:
        clicks[mode] = 1
    return ",".join(str(count) for count in clicks)


def manifest_and_results(cells: dict[str, dict[str, int]], shots: int = 1000) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest = load("cases.json")
    iterations = [
        {
            "iteration": {"circuit_params": setting["circuit_params"]},
            "counts": cells[setting["label"]],
            "samples": sum(cells[setting["label"]].values()),
            "result_fields": {"nb_shots_used": shots},
        }
        for setting in manifest["settings"]
    ]
    return manifest, {"partial": False, "iterations": iterations}


def correct_raw(label: str, pattern: str) -> int:
    """The raw receiver bit that decodes to the input's eigenvalue under the pattern's frame."""
    basis = next(basis for name, _, basis, _ in protocol.SIX_STATES if name == label)
    x, z = rehearsal.frames()[pattern]
    return rehearsal.expected_bit(label) ^ {"Z": x, "X": z, "Y": x ^ z}[basis]


def test_frame_table_matches_the_design() -> None:
    expected = {"1100": (1, 0), "0011": (1, 0), "1001": (1, 1), "0110": (1, 1)}
    if rehearsal.frames() != expected:
        raise AssertionError(rehearsal.frames())


def test_template_unitary_reproduces_the_ideal_instrument_through_propagate_and_slos() -> None:
    import perceval as pcvl

    manifest, circuit = load("cases.json"), load("circuit.json")
    for setting in manifest["settings"]:
        label = setting["label"]
        built = np.asarray(
            rehearsal.perceval_circuit(circuit, setting["circuit_params"]).compute_unitary(), dtype=complex
        )
        target = rehearsal.chip_operator(rehearsal.logical_unitary(label))
        if float(np.max(np.abs(built - target))) > 1e-9:
            raise AssertionError(f"{label}: the template unitary departs from the ideal operator")
        output = protocol.propagate(built, {tuple(circuit["input_state"]): 1.0 + 0.0j})
        by_clicks: dict[tuple[int, ...], float] = {}
        for occupation, amplitude in output.items():
            key = tuple(1 if count else 0 for count in occupation)
            by_clicks[key] = by_clicks.get(key, 0.0) + abs(amplitude) ** 2
        accepted, correct = rehearsal.scored(label, by_clicks)
        if abs(accepted - 1 / 18) > 1e-9 or abs(correct / accepted - 1.0) > 1e-9:
            raise AssertionError(f"{label}: propagate gives acceptance {accepted}, fidelity {correct / accepted}")
        processor = pcvl.Processor("SLOS", rehearsal.perceval_circuit(circuit, setting["circuit_params"]))
        processor.min_detected_photons_filter(3)
        processor.with_input(pcvl.BasicState(circuit["input_state"]))
        slos: dict[tuple[int, ...], float] = {}
        for state, probability in processor.probs()["results"].items():
            key = tuple(1 if count else 0 for count in state)
            slos[key] = slos.get(key, 0.0) + float(probability)
        accepted_slos, correct_slos = rehearsal.scored(label, slos)
        if abs(accepted_slos - 1 / 18) > 1e-9 or abs(correct_slos / accepted_slos - 1.0) > 1e-9:
            raise AssertionError(
                f"{label}: SLOS gives acceptance {accepted_slos}, fidelity {correct_slos / accepted_slos}"
            )


def test_every_accepted_pattern_implies_the_cnot_success_branch() -> None:
    for label in LABELS:
        clicks = rehearsal.ideal_clicks(label)
        for vector, probability in clicks.items():
            outcome, _, _ = rehearsal.classify(vector)
            if outcome == "accepted" and probability > 1e-12:
                logical = [vector[mode] for mode in rehearsal.LAYOUT]
                if sum(logical) != 3 or logical[rehearsal.H0] or logical[rehearsal.H1]:
                    raise AssertionError(f"{label}: accepted event {vector} clicks a herald")


def test_layout_obeys_the_source_dark_count_and_window_rules() -> None:
    layout = rehearsal.LAYOUT
    if any(layout[logical] not in rehearsal.CONNECTED for logical in rehearsal.SOURCES):
        raise AssertionError("a source photon sits on an unconnected input")
    t_out, dark, _ = rehearsal.read_perfs(load("platform-read/catalogue.json"))
    if 5 in layout or any(dark[mode] > rehearsal.DARK_LIMIT for mode in layout):
        raise AssertionError("the layout uses a mode with a high dark count")
    if rehearsal.choose_layout(t_out, dark) != layout:
        raise AssertionError("the retained platform read selects another layout")
    start = min(layout)
    if sorted(layout) != list(range(start, start + rehearsal.LOGICAL)):
        raise AssertionError("the layout is not eight consecutive chip modes")


def test_request_is_byte_stable_and_validates() -> None:
    job = rehearsal.JOBS["job-00"]
    first, second = rehearsal.documents(job), rehearsal.documents(job)
    if first != second:
        raise AssertionError("two builds differ")
    if first["circuit.json"] != (CASE / "circuit.json").read_bytes():
        raise AssertionError("circuit.json differs from the retained bytes")
    rehearsal.close(json.loads(first["cases.json"]), load("cases.json"), "cases.json")
    manifest, circuit = load("cases.json"), load("circuit.json")
    rehearsal.validate(manifest, circuit)
    if manifest["circuit"]["sha256"] != rehearsal.sha256_bytes((CASE / "circuit.json").read_bytes()):
        raise AssertionError("cases.json names another circuit.json")
    if [setting.get("compilation_seed") for setting in manifest["settings"]] != list(rehearsal.COMPILATION_SEEDS):
        raise AssertionError("the settings do not carry exactly the registered compilation seeds")
    if manifest["min_detected_photons"] != 3 or manifest["mitigations"] != [] or manifest["max_duration"] != 300:
        raise AssertionError("the request departs from the design's fields")
    expected = ["herald photon", "perturbed unitary", "shifted source", "unregistered compilation seed"]
    if sorted(rehearsal.rejections(manifest, circuit)) != expected:
        raise AssertionError("a mutated request validates")


def test_compilation_seeds_are_the_registered_draw_values_in_index_order() -> None:
    rows = [
        row
        for row in json.loads((ROOT / "docs/evidence/qrng_seeds/allocations.json").read_text(encoding="utf-8"))[
            "allocations"
        ]
        if row["path"] == "scripts/qd_teleportation_rehearsal.py" and row["name"] == "COMPILATION_SEEDS"
    ]
    if len(rows) != 6 or len({row["record"] for row in rows}) != 1:
        raise AssertionError(rows)
    values = json.loads((ROOT / rows[0]["record"]).read_text(encoding="utf-8"))["values"]
    if [row["index"] for row in rows] != list(range(6)) or [row["value"] for row in rows] != list(
        rehearsal.COMPILATION_SEEDS
    ):
        raise AssertionError("the allocation rows differ from COMPILATION_SEEDS in index order")
    if [values[row["index"]] for row in rows] != list(rehearsal.COMPILATION_SEEDS):
        raise AssertionError("the draw record holds other values at those indices")
    body = load("job-body.json")
    manifest = load("cases.json")
    for index, seed in enumerate(rehearsal.COMPILATION_SEEDS):
        mutated = copy.deepcopy(manifest)
        mutated["settings"][index]["compilation_seed"] = seed + 1
        with pytest.raises(ValueError, match="compilation_seed"):
            rehearsal.validate(mutated, load("circuit.json"))
    rehearsal.validate_body(body, manifest)


def test_layout_search_over_windows_equals_the_serial_search(monkeypatch: pytest.MonkeyPatch) -> None:
    t_out, dark, _ = rehearsal.read_perfs(load("platform-read/catalogue.json"))
    windows = [
        rehearsal.window_layout((start, t_out, dark, rehearsal.CONNECTED))
        for start in range(rehearsal.MODES - rehearsal.LOGICAL + 1)
    ]
    found = [key for key in windows if key is not None]
    if not found or tuple(min(found)[3]) != rehearsal.LAYOUT:
        raise AssertionError("the serial window search selects another layout")
    if rehearsal.choose_layout(t_out, dark) != rehearsal.LAYOUT:
        raise AssertionError("the pooled window search selects another layout")
    monkeypatch.setattr(rehearsal, "window_layout", lambda item: None)
    monkeypatch.setattr(rehearsal, "ordered_map", lambda function, items, min_items=1: [function(i) for i in items])
    with pytest.raises(rehearsal.PlatformError, match="no window"):
        rehearsal.choose_layout(t_out, dark)


def test_budget_follows_the_retained_derivation() -> None:
    derived = rehearsal.retained_derivation()
    job = rehearsal.JOBS["job-00"]
    expected = protocol.bernoulli_decision_count(
        0.01, 0.10, derived["mean_score"], derived["classical_bound"], derived["systematic_allowance"]
    )
    if derived["decision_count"] != expected or derived["classical_bound"] < 2.0 / 3.0:
        raise AssertionError(derived)
    if job.samples != derived["samples_per_iteration"] or job.samples * 6 * derived["least_accepted_share"] < expected:
        raise AssertionError("the sample budget does not yield the decision count of accepted outcomes")
    estimate = load("shot-estimate.json")
    if job.shots != estimate["shots_per_iteration"] or job.shots < estimate["largest"]:
        raise AssertionError("max_shots departs from the retained shot estimate")
    if job.credit_ceiling < rehearsal.PER_JOB_CREDITS + job.shots * rehearsal.PRICE_PER_SHOT - 1e-9:
        raise AssertionError("the credit ceiling is below the per-job price plus the shot ceiling")


def test_retained_plan_binds_the_retained_body() -> None:
    plan = load("plan-anchor.json")
    body = load("job-body.json")
    record = load("body-build.json")
    if body_digest(body) != plan["body_sha256_without_process_id"]:
        raise AssertionError("the plan names another body")
    if record["cases_sha256"] != plan["cases_sha256"] or record["sent"] or plan["sent"]:
        raise AssertionError("the body record and the plan disagree or claim a send")
    if record["job_body_sha256"] != rehearsal.sha256_bytes((CASE / "job-body.json").read_bytes()):
        raise AssertionError("body-build.json names another body")
    if plan["cases_sha256"] != rehearsal.sha256_bytes((CASE / "cases.json").read_bytes()):
        raise AssertionError("the plan names other case bytes")
    rehearsal.validate_body(body, load("cases.json"))


def test_ideal_simulated_results_score_unit_fidelity_and_beat_the_classical_bound() -> None:
    manifest = load("cases.json")
    results = rehearsal.simulated_results(manifest, load("circuit.json"), IDEAL)
    record = rehearsal.analyze_results(manifest, results, manifest["frames"])
    pooled = record["pooled"]
    if abs(pooled["fidelity"] - 1.0) > 1e-12 or record["verdict"] != "beats-classical":
        raise AssertionError(record["pooled"])
    if abs(record["benchmark"]["bound_at_reported_attempts"] - 2.0 / 3.0) > 1e-8 or pooled["accepted"] < 314:
        raise AssertionError(record["benchmark"])
    if record["benchmark"]["classical_bound"] < record["benchmark"]["bound_at_modeled_attempts"] - 1e-12:
        raise AssertionError(record["benchmark"])


def test_analysis_of_a_synthetic_histogram() -> None:
    cells: dict[str, dict[str, int]] = {}
    wrong_total = 0
    for index, label in enumerate(LABELS):
        wrong = 10 * (index % 3)
        wrong_total += wrong
        good = 100 - wrong
        counts: dict[str, int] = {}
        for pattern, share in (("1100", good // 2), ("0110", good - good // 2)):
            raw = correct_raw(label, pattern)
            counts[event(pattern, raw)] = share
        if wrong:
            counts[event("1001", 1 - correct_raw(label, "1001"))] = wrong
        counts[event("1010", 0)] = 7
        counts[event("1000", 0, extra=(rehearsal.LAYOUT[rehearsal.H0],))] = 5
        counts[event("1000", 0, extra=(0,))] = 2
        counts[event("1100", 0, extra=(0,))] = 3
        cells[label] = counts
    manifest, results = manifest_and_results(cells)
    record = rehearsal.analyze_results(manifest, results, manifest["frames"])
    expected_pooled = 1.0 - wrong_total / 600
    if abs(record["pooled"]["fidelity"] - expected_pooled) > 1e-12 or record["pooled"]["accepted"] != 600:
        raise AssertionError(record["pooled"])
    radius = math.sqrt(math.log(100) / (2 * 600))
    if abs(record["pooled"]["lower_bound"] - (expected_pooled - radius)) > 1e-12:
        raise AssertionError(record["pooled"])
    for index, label in enumerate(LABELS):
        row = record["inputs"][label]
        if abs(row["conditional_fidelity"] - (1.0 - 0.1 * (index % 3))) > 1e-12 or row["accepted"] != 100:
            raise AssertionError((label, row))
        if row["rejected"] != {"excess": 3, "outside": 2, "herald": 5, "receiver": 0, "pattern": 7}:
            raise AssertionError((label, row["rejected"]))
        if abs(row["accepted_per_shot"] - 0.1) > 1e-12:
            raise AssertionError((label, row))
    reported = attempts_benchmark({label: 1000 for label in LABELS}).certified
    modeled = rehearsal.model_benchmark(manifest["preregistered"]["sample_probability"], dict.fromkeys(LABELS, 117))
    benchmark = record["benchmark"]
    if abs(benchmark["bound_at_reported_attempts"] - reported) > 1e-12 or modeled <= reported + 1e-3:
        raise AssertionError(benchmark)
    if abs(benchmark["bound_at_modeled_attempts"] - modeled) > 1e-12 or benchmark["classical_bound"] != modeled:
        raise AssertionError(benchmark)
    if record["verdict"] != "beats-classical":
        raise AssertionError(record["verdict"])


def test_analysis_verdicts_follow_the_decision_rule() -> None:
    def verdict(wrong: int) -> str:
        cells = {
            label: {
                event("1100", correct_raw(label, "1100")): 300 - wrong,
                event("1100", 1 - correct_raw(label, "1100")): wrong,
            }
            for label in LABELS
        }
        manifest, results = manifest_and_results(cells)
        return str(rehearsal.analyze_results(manifest, results)["verdict"])

    if (verdict(0), verdict(150), verdict(90)) != ("beats-classical", "at-or-below-classical", "inconclusive"):
        raise AssertionError((verdict(0), verdict(150), verdict(90)))


def test_unequal_reported_attempts_raise_the_reported_bound() -> None:
    cells = {label: {event("1100", correct_raw(label, "1100")): 100} for label in LABELS}
    manifest, results = manifest_and_results(cells)
    for index, entry in enumerate(results["iterations"]):
        entry["result_fields"]["nb_shots_used"] = 100 * (1 + 4 * (index % 2))
    record = rehearsal.analyze_results(manifest, results)
    if record["benchmark"]["bound_at_reported_attempts"] <= 2.0 / 3.0 + 1e-6:
        raise AssertionError(record["benchmark"])


def test_refusals() -> None:
    cells = {label: {event("1100", correct_raw(label, "1100")): 50} for label in LABELS}
    manifest, results = manifest_and_results(cells)
    wrong_frame = {pattern: (x ^ 1, z) for pattern, (x, z) in rehearsal.frames().items()}
    with pytest.raises(protocol.ProtocolError, match="frame table"):
        rehearsal.analyze_results(manifest, results, wrong_frame)
    with pytest.raises(protocol.ProtocolError, match="lacks the joint Bell pattern"):
        protocol.joint_teleportation_scores({("+Z", "Z", "", 0): 5}, rehearsal.frames())
    with pytest.raises(protocol.ProtocolError, match="outside the frozen frame table"):
        protocol.joint_teleportation_scores({("+Z", "Z", "1010", 0): 5}, rehearsal.frames())
    short = copy.deepcopy(results)
    short["iterations"][0]["counts"]["0," * 23 + "0"] = 0
    short["iterations"][0]["counts"][event("1100", 0).replace("1", "0", 1)] = 4
    with pytest.raises(protocol.ProtocolError, match="fewer than 3 clicks"):
        rehearsal.analyze_results(manifest, short)
    unbound = copy.deepcopy(results)
    unbound["iterations"][2]["iteration"]["circuit_params"]["x0"] += 1.0
    with pytest.raises(protocol.ProtocolError, match="bind to exactly one"):
        rehearsal.analyze_results(manifest, unbound)
    with pytest.raises(protocol.ProtocolError, match="iterations, not 6"):
        rehearsal.analyze_results(manifest, {"iterations": results["iterations"][:5]})
    starved = copy.deepcopy(results)
    starved["iterations"][1]["result_fields"]["nb_shots_used"] = 10
    with pytest.raises(protocol.ProtocolError, match="below its"):
        rehearsal.analyze_results(manifest, starved)
    with pytest.raises(protocol.ProtocolError, match="24-mode occupation"):
        rehearsal.event_vector("1,0,1")
    with pytest.raises(protocol.ProtocolError, match="positive trials"):
        rehearsal.hoeffding_radius(0.01, 0)


def test_classification_reasons() -> None:
    layout = rehearsal.LAYOUT

    def clicks(*modes: int) -> list[int]:
        vector = [0] * rehearsal.MODES
        for mode in modes:
            vector[mode] = 1
        return vector

    q0, q1, a0, a1, b0, b1, h0, _ = layout
    outcomes = {
        "below": clicks(q0, q1),
        "excess": clicks(q0, q1, b0, b1),
        "outside": clicks(q0, q1, 0),
        "herald": clicks(q0, q1, h0),
        "receiver": clicks(q0, q1, a0),
        "pattern": clicks(q0, a0, b1),
    }
    for expected, vector in outcomes.items():
        if rehearsal.classify(vector)[0] != expected:
            raise AssertionError((expected, rehearsal.classify(vector)))
    if rehearsal.classify(clicks(q0, q1, b1)) != ("accepted", "1100", 1):
        raise AssertionError(rehearsal.classify(clicks(q0, q1, b1)))


def test_check_rederives_the_noise_model_and_accepts_the_retained_case() -> None:
    if rehearsal.check() != 0:
        raise AssertionError("check failed")


def planned_model(pooled_fidelity: float) -> dict[str, Any]:
    mean_score = rehearsal.retained_derivation()["mean_score"]
    return {
        "figures": {"hom": 0.8, "g2": 0.1, "transmittance": 0.001},
        "pooled_fidelity": pooled_fidelity,
        "mean_score": mean_score,
        "inside_justified_range": pooled_fidelity >= mean_score,
    }


def test_plan_outside_the_justified_range_retains_a_refusal_and_writes_no_plan(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    admitted = {
        "body": load("job-body.json"),
        "platform_at_plan": {"status": "available"},
        "credit_ceiling": 2.2,
        "estimated_shots": 1,
    }
    monkeypatch.setattr(rehearsal, "plan", lambda *args, **kwargs: admitted)
    (tmp_path / "cases.json").write_bytes((CASE / "cases.json").read_bytes())
    job = rehearsal.JOBS["job-00"]
    status = rehearsal.planned(job, tmp_path, "", planned_model(0.635))
    refusal = json.loads((tmp_path / "plan-refused.json").read_text(encoding="utf-8"))
    if status != 1 or (tmp_path / "plan.json").exists() or refusal["sent"] or "0.6350" not in refusal["refusal"]:
        raise AssertionError((status, sorted(path.name for path in tmp_path.iterdir()), refusal))
    if refusal["model"]["inside_justified_range"]:
        raise AssertionError(refusal["model"])
    status = rehearsal.planned(job, tmp_path, "", planned_model(0.868))
    if status != 0 or not (tmp_path / "plan.json").is_file():
        raise AssertionError("a plan inside the justified range is retained")


@pytest.mark.parametrize("held", ["cases.json", "circuit.json", "results.json", "submission.json", "raw"])
def test_simulate_refuses_a_directory_that_holds_a_request_or_result(tmp_path: Path, held: str) -> None:
    if held == "raw":
        (tmp_path / held).mkdir()
        (tmp_path / held / "kept.json").write_text("{}", encoding="utf-8")
    else:
        (tmp_path / held).write_text("kept", encoding="utf-8")
    with pytest.raises(ValueError, match=held):
        rehearsal.simulate(tmp_path)
    if sorted(path.name for path in tmp_path.iterdir()) != [held]:
        raise AssertionError(sorted(path.name for path in tmp_path.iterdir()))


def test_analysis_of_an_input_without_an_accepted_event_is_inconclusive() -> None:
    cells = {label: {event("1100", correct_raw(label, "1100")): 300} for label in LABELS}
    cells["+Z"] = {event("1010", 0): 900}
    manifest, results = manifest_and_results(cells)
    record = rehearsal.analyze_results(manifest, results, manifest["frames"])
    silent = record["inputs"]["+Z"]
    if silent["accepted"] != 0 or silent["rejected"]["pattern"] != 900 or silent["conditional_fidelity"] is not None:
        raise AssertionError(silent)
    if "no accepted event" not in silent["conditional_fidelity_reason"] or record["inputs_without_accepted"] != ["+Z"]:
        raise AssertionError(record["inputs_without_accepted"])
    pooled = record["pooled"]
    radius = math.sqrt(math.log(100) / (2 * 1500))
    if pooled["accepted"] != 1500 or pooled["inputs_pooled"] != 5 or abs(pooled["fidelity"] - 1.0) > 1e-12:
        raise AssertionError(pooled)
    if abs(pooled["radius"] - radius) > 1e-12 or record["verdict"] != "inconclusive":
        raise AssertionError((pooled, record["verdict"]))
    if record["success_rate_per_reported_shot"]["+Z"] != 0.0 or record["inputs"]["-Z"]["conditional_fidelity"] != 1.0:
        raise AssertionError(record["success_rate_per_reported_shot"])
    empty = {label: {event("1010", 0): 900} for label in LABELS}
    manifest, results = manifest_and_results(empty)
    record = rehearsal.analyze_results(manifest, results, manifest["frames"])
    pooled = record["pooled"]
    if pooled["fidelity"] is not None or pooled["lower_bound"] is not None or record["margin"] is not None:
        raise AssertionError(pooled)
    if record["verdict"] != "inconclusive" or len(record["inputs_without_accepted"]) != 6:
        raise AssertionError(record["verdict"])


def test_later_plan_attempts_write_beside_the_retained_records(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    admitted = {
        "body": load("job-body.json"),
        "platform_at_plan": {"status": "available"},
        "credit_ceiling": 2.2,
        "estimated_shots": 1,
    }
    monkeypatch.setattr(rehearsal, "plan", lambda *args, **kwargs: admitted)
    (tmp_path / "cases.json").write_bytes((CASE / "cases.json").read_bytes())
    job = rehearsal.JOBS["job-00"]
    for fidelity in (0.635, 0.868, 0.635, 0.868):
        rehearsal.planned(job, tmp_path, "", planned_model(fidelity))
    retained = {name: (tmp_path / name).read_bytes() for name in ("plan.json", "plan-refused.json")}
    rehearsal.planned(job, tmp_path, "", planned_model(0.868))
    if any((tmp_path / name).read_bytes() != data for name, data in retained.items()):
        raise AssertionError("a later attempt rewrote a retained plan record")
    names = sorted(path.name for path in tmp_path.iterdir() if path.name != "cases.json")
    refused = [name for name in names if name.startswith("plan-refused-")]
    admitted_later = [name for name in names if name.startswith("plan-") and not name.startswith("plan-refused")]
    if len(refused) != 1 or len(admitted_later) != 2:
        raise AssertionError(names)


def test_analysis_of_a_zero_shot_iteration_is_inconclusive_without_a_bound() -> None:
    cells = {label: {event("1100", correct_raw(label, "1100")): 300} for label in LABELS}
    cells["-X"] = {}
    manifest, results = manifest_and_results(cells)
    for entry in results["iterations"]:
        if not entry["counts"]:
            entry["result_fields"]["nb_shots_used"] = 0
    record = rehearsal.analyze_results(manifest, results, manifest["frames"])
    if record["inputs"]["-X"]["accepted_per_shot"] is not None or record["inputs"]["-X"]["shots"] != 0:
        raise AssertionError(record["inputs"]["-X"])
    benchmark = record["benchmark"]
    if benchmark["classical_bound"] is not None or benchmark["bound_at_reported_attempts"] is not None:
        raise AssertionError(benchmark)
    if record["verdict"] != "inconclusive" or "no shot" not in record["verdict_reason"] or record["margin"] is not None:
        raise AssertionError((record["verdict"], record["verdict_reason"]))


def staged_run(tmp_path: Path) -> Path:
    run = tmp_path / "run"
    run.mkdir()
    for name in rehearsal.STAGED:
        (run / name).write_bytes((CASE / name).read_bytes())
    return run


def test_submit_binding_refuses_a_departed_body_and_a_model_below_the_justified_range(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    job = rehearsal.JOBS["job-00"]
    checked = {"body": load("job-body.json")}
    monkeypatch.setattr(rehearsal, "live_model", lambda: planned_model(0.635))
    admitted: dict[str, Any] = {}
    with pytest.raises(rehearsal.PlatformError, match="0.6350"):
        rehearsal.binding(job, admitted)(checked)
    if admitted:
        raise AssertionError(admitted)
    monkeypatch.setattr(rehearsal, "live_model", lambda: planned_model(0.868))
    departed = copy.deepcopy(checked)
    departed["body"]["tags"] = ["departed"]
    with pytest.raises(rehearsal.PlatformError, match="differs from the retained body"):
        rehearsal.binding(job, admitted)(departed)
    process = copy.deepcopy(checked)
    process["body"]["process_id"] = "fresh"
    rehearsal.binding(job, admitted)(process)
    if admitted["pooled_fidelity"] != 0.868:
        raise AssertionError(admitted)


def test_submit_reads_the_platform_first_and_retains_the_admitting_model(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    run = staged_run(tmp_path)
    calls: list[str] = []

    def read(out: Path) -> None:
        calls.append("snapshot")
        out.mkdir(exist_ok=True)

    monkeypatch.setattr(rehearsal, "snapshot", read)
    monkeypatch.setattr(rehearsal, "observe", lambda out: calls.append("observe"))

    def submitted(case_dir: Path, platform: str, approval: str, *args: Any, verify: Any) -> dict[str, Any]:
        calls.append("submit")
        if case_dir != run or platform != rehearsal.PLATFORM or not approval:
            raise AssertionError((case_dir, platform, approval))
        if args != (2.2, 120.0, rehearsal.PER_JOB_CREDITS):
            raise AssertionError(args)
        verify({"body": load("job-body.json")})
        return {"job_id": "job-id", "platform": platform}

    monkeypatch.setattr(rehearsal, "submit", submitted)
    monkeypatch.setattr(rehearsal, "live_model", lambda: planned_model(0.635))
    with pytest.raises(rehearsal.PlatformError):
        rehearsal.send(run, "approved")
    if (run / rehearsal.SUBMIT_MODEL).exists() or calls != ["snapshot", "observe", "submit"]:
        raise AssertionError(calls)
    monkeypatch.setattr(rehearsal, "live_model", lambda: planned_model(0.868))
    if rehearsal.send(run, "approved") != 0:
        raise AssertionError("an admitted request returns 0")
    record = json.loads((run / rehearsal.SUBMIT_MODEL).read_text(encoding="utf-8"))
    if record["job_id"] != "job-id" or record["model"]["pooled_fidelity"] != 0.868:
        raise AssertionError(record)


def test_submit_refuses_a_run_directory_beyond_the_frozen_request(tmp_path: Path) -> None:
    run = staged_run(tmp_path)
    (run / "results.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="results.json"):
        rehearsal.staged(run)
    (run / "results.json").unlink()
    (run / "cases.json").write_bytes(b"{}")
    with pytest.raises(ValueError, match="names job None"):
        rehearsal.staged(run)


def test_partial_results_score_counted_iterations_and_stay_inconclusive() -> None:
    cells = {label: {event("1100", correct_raw(label, "1100")): 300} for label in LABELS}
    manifest, results = manifest_and_results(cells)
    results["partial"] = True
    results["iterations"][4] = {"missing": True}
    results["iterations"][5] = {"error": "worker stopped", "iteration": {}, "result_fields": {}}
    record = rehearsal.analyze_results(manifest, results, manifest["frames"])
    absent = [setting["label"] for setting in manifest["settings"][4:]]
    if record["inputs_without_counts"] != absent or record["uncounted_iterations"] != ["missing", "error"]:
        raise AssertionError((record["inputs_without_counts"], record["uncounted_iterations"]))
    if record["verdict"] != "inconclusive" or "ended partial" not in record["verdict_reason"]:
        raise AssertionError((record["verdict"], record["verdict_reason"]))
    if record["benchmark"]["classical_bound"] is not None or record["pooled"]["accepted"] != 1200:
        raise AssertionError(record["benchmark"])
    countless = rehearsal.analyze_results(manifest, {"partial": True, "counts": {}}, manifest["frames"])
    if countless["verdict"] != "inconclusive" or len(countless["inputs_without_counts"]) != 6:
        raise AssertionError(countless["inputs_without_counts"])
    results["partial"] = False
    with pytest.raises(rehearsal.ProtocolError):
        rehearsal.analyze_results(manifest, results, manifest["frames"])


def test_anchor_submission_reads_the_live_platform_and_gates_on_the_anchor_model(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from contextlib import contextmanager

    run = staged_run(tmp_path)
    inside = {"anchor": False}

    @contextmanager
    def anchored() -> Any:
        inside["anchor"] = True
        try:
            yield
        finally:
            inside["anchor"] = False

    def read(out: Path) -> None:
        if inside["anchor"]:
            raise AssertionError("the platform read ran under the anchor figures")
        out.mkdir(exist_ok=True)

    def observed(out: Path) -> None:
        if inside["anchor"]:
            raise AssertionError("the route observation ran under the anchor figures")

    def submitted(case_dir: Path, platform: str, approval: str, *args: Any, verify: Any) -> dict[str, Any]:
        if not inside["anchor"]:
            raise AssertionError("the anchor submission planned on the live figures")
        verify({"body": load("job-body.json")})
        return {"job_id": "job-id", "platform": platform}

    monkeypatch.setattr(rehearsal, "anchor_perfs", anchored)
    monkeypatch.setattr(rehearsal, "snapshot", read)
    monkeypatch.setattr(rehearsal, "observe", observed)
    monkeypatch.setattr(rehearsal, "submit", submitted)
    monkeypatch.setattr(rehearsal, "live_model", lambda: planned_model(0.868 if inside["anchor"] else 0.635))
    if rehearsal.main(["--submit", str(run), "approved", "--anchor"]) != 0:
        raise AssertionError("the anchor submission returns 0")
    record = json.loads((run / rehearsal.SUBMIT_MODEL).read_text(encoding="utf-8"))
    if record["gate"] != "anchor" or record["perfs_basis"] != rehearsal.ANCHOR_READ:
        raise AssertionError(record)
    if record["model"]["pooled_fidelity"] != 0.868 or record["live_model"]["pooled_fidelity"] != 0.635:
        raise AssertionError(record)
