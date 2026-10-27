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
        target = rehearsal.chip_operator(rehearsal.logical_unitary(label), rehearsal.LAYOUT)
        if float(np.max(np.abs(built - target))) > 1e-9:
            raise AssertionError(f"{label}: the template unitary departs from the ideal operator")
        output = protocol.propagate(built, {tuple(circuit["input_state"]): 1.0 + 0.0j})
        by_clicks: dict[tuple[int, ...], float] = {}
        for occupation, amplitude in output.items():
            key = tuple(1 if count else 0 for count in occupation)
            by_clicks[key] = by_clicks.get(key, 0.0) + abs(amplitude) ** 2
        accepted, correct = rehearsal.scored(label, by_clicks, rehearsal.LAYOUT)
        if abs(accepted - 1 / 18) > 1e-9 or abs(correct / accepted - 1.0) > 1e-9:
            raise AssertionError(f"{label}: propagate gives acceptance {accepted}, fidelity {correct / accepted}")
        processor = pcvl.Processor("SLOS", rehearsal.perceval_circuit(circuit, setting["circuit_params"]))
        processor.min_detected_photons_filter(3)
        processor.with_input(pcvl.BasicState(circuit["input_state"]))
        slos: dict[tuple[int, ...], float] = {}
        for state, probability in processor.probs()["results"].items():
            key = tuple(1 if count else 0 for count in state)
            slos[key] = slos.get(key, 0.0) + float(probability)
        accepted_slos, correct_slos = rehearsal.scored(label, slos, rehearsal.LAYOUT)
        if abs(accepted_slos - 1 / 18) > 1e-9 or abs(correct_slos / accepted_slos - 1.0) > 1e-9:
            raise AssertionError(
                f"{label}: SLOS gives acceptance {accepted_slos}, fidelity {correct_slos / accepted_slos}"
            )


def test_every_ideal_three_photon_accepted_pattern_implies_the_cnot_success_branch() -> None:
    for label in LABELS:
        clicks = rehearsal.ideal_clicks(label, rehearsal.LAYOUT)
        for vector, probability in clicks.items():
            outcome, _, _ = rehearsal.classify(vector, rehearsal.LAYOUT)
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


@pytest.mark.parametrize(
    ("name", "constant", "records"),
    [
        ("job-00", "COMPILATION_SEEDS", ["docs/evidence/anu_qrng/draw-2026-10-25T204252Z.json"]),
        (
            "job-01",
            "JOB_01_COMPILATION_SEEDS",
            [
                "docs/evidence/outshift_qrng/draw-2026-10-26T204106Z.json",
                "docs/evidence/anu_qrng/draw-2026-10-26T230602Z.json",
            ],
        ),
    ],
)
def test_case_seeds_are_the_registered_draw_values_in_index_order(name: str, constant: str, records: list[str]) -> None:
    seeds = rehearsal.CASE_SEEDS[name]
    _, blocks = rehearsal.CASE_DESIGNS[name]
    if getattr(rehearsal, constant) != seeds or len(seeds) != len(LABELS) * blocks or len(records) != blocks:
        raise AssertionError((name, seeds))
    rows = [
        row
        for row in json.loads((ROOT / "docs/evidence/qrng_seeds/allocations.json").read_text(encoding="utf-8"))[
            "allocations"
        ]
        if row["path"] == "scripts/qd_teleportation_rehearsal.py" and row["name"] == constant
    ]
    expected = [(record, index) for record in records for index in range(len(LABELS))]
    if [(row["record"], row["index"]) for row in rows] != expected or [row["value"] for row in rows] != list(seeds):
        raise AssertionError(f"the allocation rows differ from {constant} in block and index order")
    for row in rows:
        if json.loads((ROOT / row["record"]).read_text(encoding="utf-8"))["values"][row["index"]] != row["value"]:
            raise AssertionError("the draw record holds another value at a registered index")
    if set(seeds) & {seed for other, values_ in rehearsal.CASE_SEEDS.items() if other != name for seed in values_}:
        raise AssertionError(f"{name} shares a compilation seed with another case")


def test_retained_compilation_seeds_bind_the_job_00_request_and_body() -> None:
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
    derived = rehearsal.retained_derivation("job-00")
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
        if rehearsal.classify(vector, layout)[0] != expected:
            raise AssertionError((expected, rehearsal.classify(vector, layout)))
    if rehearsal.classify(clicks(q0, q1, b1), layout) != ("accepted", "1100", 1):
        raise AssertionError(rehearsal.classify(clicks(q0, q1, b1), layout))


def test_check_rederives_the_noise_model_and_accepts_the_retained_case() -> None:
    if rehearsal.check() != 0:
        raise AssertionError("check failed")


def planned_model(pooled_fidelity: float) -> dict[str, Any]:
    mean_score = rehearsal.retained_derivation("job-00")["mean_score"]
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
        rehearsal.simulate(tmp_path, rehearsal.JOBS["job-00"])
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
    monkeypatch.setattr(rehearsal, "live_model", lambda request=None: planned_model(0.635))
    admitted: dict[str, Any] = {}
    with pytest.raises(rehearsal.PlatformError, match="0.6350"):
        rehearsal.binding(job, admitted)(checked)
    if admitted:
        raise AssertionError(admitted)
    monkeypatch.setattr(rehearsal, "live_model", lambda request=None: planned_model(0.868))
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
    monkeypatch.setattr(rehearsal, "live_model", lambda request=None: planned_model(0.635))
    with pytest.raises(rehearsal.PlatformError):
        rehearsal.send(run, "approved")
    if (run / rehearsal.SUBMIT_MODEL).exists() or calls != ["snapshot", "observe", "submit"]:
        raise AssertionError(calls)
    monkeypatch.setattr(rehearsal, "live_model", lambda request=None: planned_model(0.868))
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
    def anchored(read: str | None = None) -> Any:
        if read != rehearsal.ANCHOR_READ:
            raise AssertionError(f"the anchor gate reads {read}")
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
    monkeypatch.setattr(
        rehearsal, "live_model", lambda request=None: planned_model(0.868 if inside["anchor"] else 0.635)
    )
    if rehearsal.main(["--submit", str(run), "approved", "--anchor"]) != 0:
        raise AssertionError("the anchor submission returns 0")
    record = json.loads((run / rehearsal.SUBMIT_MODEL).read_text(encoding="utf-8"))
    if record["gate"] != "anchor" or record["perfs_basis"] != rehearsal.ANCHOR_READ:
        raise AssertionError(record)
    if record["model"]["pooled_fidelity"] != 0.868 or record["live_model"]["pooled_fidelity"] != 0.635:
        raise AssertionError(record)


def test_a_manifest_classifies_its_events_under_its_own_layout() -> None:
    moved = (16, 17, 18, 19, 20, 21, 22, 23)
    manifest = copy.deepcopy(load("cases.json"))
    manifest["layout"]["chip_modes"] = list(moved)
    cells: dict[str, dict[str, int]] = {}
    for label in LABELS:
        clicks = [0] * rehearsal.MODES
        for mode, flag in zip(rehearsal.ANALYZER_MODES, "1100", strict=True):
            clicks[moved[mode]] = int(flag)
        clicks[moved[rehearsal.B0 if correct_raw(label, "1100") == 0 else rehearsal.B1]] = 1
        cells[label] = {",".join(str(count) for count in clicks): 100}
    iterations = [
        {
            "iteration": {"circuit_params": setting["circuit_params"]},
            "counts": cells[setting["label"]],
            "samples": 100,
            "result_fields": {"nb_shots_used": 1000},
        }
        for setting in manifest["settings"]
    ]
    record = rehearsal.analyze_results(manifest, {"partial": False, "iterations": iterations})
    if record["pooled"]["accepted"] != 600 or abs(record["pooled"]["fidelity"] - 1.0) > 1e-12:
        raise AssertionError(record["pooled"])
    _, rejected = rehearsal.tally(cells["+Z"], rehearsal.LAYOUT)
    if rejected["outside"] != 100:
        raise AssertionError("the moved events classify as accepted under another layout")


def test_a_case_anchored_at_its_own_read_refuses_the_anchor_gate() -> None:
    own = rehearsal.Request(
        "job-01",
        rehearsal.LAYOUT,
        rehearsal.JOB_01_COMPILATION_SEEDS,
        str((rehearsal.CASES / "job-01" / rehearsal.READ).relative_to(ROOT)),
    )
    job = rehearsal.Job(own, 900, 1_200_000, 2.2, 300.0)
    if not own.own_anchor or rehearsal.REQUESTS["job-00"].own_anchor:
        raise AssertionError("own_anchor does not tell the two anchors apart")
    with pytest.raises(ValueError, match="live gate applies"):
        rehearsal.perfs_gate(job, True)
    with rehearsal.perfs_gate(job, False):
        pass


def staged_case_tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, catalogue: dict[str, Any]) -> Path:
    """A repository root under tmp_path whose job-01 case holds `catalogue` as its platform read."""
    cases = tmp_path / "results/quandela/cases" / rehearsal.FAMILY
    read = cases / "job-01" / rehearsal.READ
    read.parent.mkdir(parents=True)
    read.write_text(json.dumps(catalogue), encoding="utf-8")
    monkeypatch.setattr(rehearsal, "ROOT", tmp_path)
    monkeypatch.setattr(rehearsal, "CASES", cases)
    return cases


def test_the_decision_rule_refuses_a_read_without_power_and_prepare_an_unseeded_case() -> None:
    low: dict[str, dict[str, Any]] = {name: {"pooled": 0.6} for name in rehearsal.ANCHOR_VARIANTS}
    low["fresh per-mode transmission"] = {"pooled": 0.6}
    low["anchor per-mode transmission"]["inputs"] = {
        label: {"sample_probability": 4e-5, "accepted_share": 0.08} for label in LABELS
    }
    with pytest.raises(protocol.ProtocolError, match="does not exceed the benchmark"):
        rehearsal.derive(low)
    with pytest.raises(ValueError, match="not a seeded case"):
        rehearsal.prepare("job-00")


def test_the_decision_rule_admits_only_its_retained_case(monkeypatch: pytest.MonkeyPatch) -> None:
    designs = {**rehearsal.CASE_DESIGNS, "job-01": (rehearsal.DECISION, 1)}
    monkeypatch.setattr(rehearsal, "CASE_DESIGNS", designs)
    with pytest.raises(ValueError, match="take the decision rule beyond"):
        rehearsal.check()
    with pytest.raises(ValueError, match="the decision rule admits only"):
        rehearsal.prepare("job-01")


def test_expected_seconds_reproduce_job_00_and_bound_the_job_by_max_duration() -> None:
    derived = rehearsal.retained_derivation("job-00")
    clock = json.loads((ROOT / rehearsal.ANCHOR_READ).read_text(encoding="utf-8"))["processors"][rehearsal.PLATFORM][
        "perfs"
    ]["Clock (MHz)"]
    if rehearsal.expected_seconds(derived, 900, clock) != rehearsal.JOBS["job-00"].expected_seconds:
        raise AssertionError("the seconds model departs from job-00's written case")
    if rehearsal.expected_seconds(derived, 15 * 900, clock) <= rehearsal.MAX_DURATION:
        raise AssertionError("fifteen times job-00's samples fit in max_duration")


# qd_classical_benchmark._require_optimal admits an inaccurate optimum and _free_postselection_bound certifies the
# bound from the projected witness, so cvxpy's inaccuracy warning on the moved layout's attempts carries no defect.
@pytest.mark.filterwarnings("ignore:Solution may be inaccurate:UserWarning")
def test_prepare_refuses_a_case_whose_expected_seconds_exceed_max_duration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cases = staged_case_tree(
        tmp_path, monkeypatch, json.loads((ROOT / rehearsal.ANCHOR_READ).read_text(encoding="utf-8"))
    )
    monkeypatch.setattr(rehearsal, "COMPILE_SECONDS", 60.0)
    monkeypatch.setattr(rehearsal, "box_bound", lambda probability, ratio: 0.7)
    with pytest.raises(ValueError, match="above max_duration"):
        rehearsal.prepare("job-01")
    if sorted(path.name for path in (cases / "job-01").iterdir()) != ["platform-read"]:
        raise AssertionError("a refused preparation retained a file")


@pytest.mark.filterwarnings("ignore:Solution may be inaccurate:UserWarning")
def test_prepare_derives_a_case_that_builds_checks_simulates_and_analyzes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    import perceval

    catalogue = json.loads((ROOT / rehearsal.ANCHOR_READ).read_text(encoding="utf-8"))
    dark = catalogue["processors"][rehearsal.PLATFORM]["perfs"]["Dark counts (detection/s)"]
    for mode in rehearsal.LAYOUT:
        dark[mode] = 10 * rehearsal.DARK_LIMIT
    cases = staged_case_tree(tmp_path, monkeypatch, catalogue)
    staged: list[dict[str, Any]] = []

    def estimate(self: Any, computation: Any, nsamples: int, param_values: Any = None) -> int:
        return 1000 * nsamples + len(staged)

    def payload(case_dir: Path, manifest: dict[str, Any], circuit: dict[str, Any], platform: str) -> dict[str, Any]:
        staged.append(manifest)
        for _ in manifest["settings"]:
            perceval.RemoteComputer.estimate_required_shots(
                None, None, manifest["max_samples"] // manifest["iterations"]
            )
        raise rehearsal.PlatformError("the estimate exceeds max_shots")

    monkeypatch.setattr(perceval.RemoteComputer, "estimate_required_shots", estimate)
    monkeypatch.setattr(rehearsal, "payload", payload)
    # The 64-vertex solve has its own test; a fixed stand-in keeps this sequence inside the call budget.
    monkeypatch.setattr(rehearsal, "box_bound", lambda probability, ratio: 0.70 + 0.1 * (ratio - 1.0))
    monkeypatch.setattr(rehearsal, "break_even_ratio", lambda probability, lower: {"status": "stub", "ratio": None})
    if rehearsal.prepare("job-01") != 0:
        raise AssertionError("prepare returns 0")
    rows = capsys.readouterr().out.strip().splitlines()[-2:]
    retained = {path.name: path.read_bytes() for path in (cases / "job-01").iterdir() if path.is_file()}
    if rehearsal.prepare("job-01") != 0 or capsys.readouterr().out.strip().splitlines()[-2:] != rows:
        raise AssertionError("a rerun of prepare derives other rows")
    if {path.name: path.read_bytes() for path in (cases / "job-01").iterdir() if path.is_file()} != retained:
        raise AssertionError("a rerun of prepare rewrote a retained file")
    if len(staged) != 1:
        raise AssertionError("a rerun of prepare estimated again")
    namespace: dict[str, Any] = {
        "Request": rehearsal.Request,
        "Job": rehearsal.Job,
        "JOB_01_COMPILATION_SEEDS": rehearsal.JOB_01_COMPILATION_SEEDS,
        "DESCRIPTIVE": rehearsal.DESCRIPTIVE,
        "REQUESTS": {},
        "JOBS": {},
    }
    for row in rows:
        exec(row, namespace)  # noqa: S102 - the rows prepare prints for the registering change
    job = namespace["JOBS"]["job-01"]
    if job.request.layout == rehearsal.LAYOUT or not job.request.own_anchor:
        raise AssertionError(job.request)
    if (job.request.rule, job.request.blocks) != (rehearsal.DESCRIPTIVE, 2):
        raise AssertionError(job.request)
    derived = rehearsal.retained_derivation("job-01")
    if job.samples != derived["samples_per_iteration"] or job.samples != rehearsal.DESCRIPTIVE_SAMPLES:
        raise AssertionError((job, derived))
    if job.shots != math.ceil((1000 * job.samples + 1) * rehearsal.SHOT_MARGIN / 100_000) * 100_000:
        raise AssertionError(job)
    clock = catalogue["processors"][rehearsal.PLATFORM]["perfs"]["Clock (MHz)"]
    seconds = rehearsal.expected_seconds(derived, job.samples, clock, 2)
    if job.credit_ceiling != round(1 + job.shots * 1e-6, 6) or job.expected_seconds != seconds or seconds > 300:
        raise AssertionError((job, seconds))
    monkeypatch.setitem(rehearsal.REQUESTS, "job-01", job.request)
    monkeypatch.setitem(rehearsal.JOBS, "job-01", job)
    monkeypatch.delitem(rehearsal.JOBS, "job-00")
    rehearsal.build(job)
    if rehearsal.check() != 0:
        raise AssertionError("check refuses the prepared case")
    manifest = json.loads((cases / "job-01" / "cases.json").read_text(encoding="utf-8"))
    if [s["compilation_seed"] for s in manifest["settings"]] != list(rehearsal.JOB_01_COMPILATION_SEEDS):
        raise AssertionError("the prepared case carries other seeds")
    order = [f"{s['block']}{s['label']}" for s in manifest["settings"]]
    if order != [f"A{label}" for label in LABELS] + [f"B{label}" for label in reversed(LABELS)]:
        raise AssertionError(order)
    with pytest.raises(ValueError, match="live gate applies"):
        rehearsal.main(["--plan", "job-01", "--anchor"])
    run = tmp_path / "run"
    rehearsal.simulate(run, job)
    rehearsal.analyze(run)
    record = json.loads((run / "analysis.json").read_text(encoding="utf-8"))
    if record["schema"] != "qd-teleportation-analysis-v2" or record["status"] != "complete":
        raise AssertionError(record["status"])
    if record["homogeneity"]["differ"] or len(record["iterations"]) != 12:
        raise AssertionError(record["homogeneity"])
    if [c["label"] for c in record["comparisons"]] != ["exceeds-under-assumptions"] * 2:
        raise AssertionError(record["comparisons"])
    if abs(record["pooled"]["accepted"] - derived["planned_accepted"]) > 0.02 * derived["planned_accepted"]:
        raise AssertionError((record["pooled"], derived["planned_accepted"]))


def test_a_partial_job_with_every_input_counted_stays_inconclusive() -> None:
    cells = {label: {event("1100", correct_raw(label, "1100")): 300} for label in LABELS}
    manifest, results = manifest_and_results(cells)
    results["partial"] = True
    record = rehearsal.analyze_results(manifest, results, manifest["frames"])
    if record["pooled"]["fidelity"] != 1.0 or record["verdict"] != "inconclusive":
        raise AssertionError((record["pooled"], record["verdict"]))
    if "descriptive" not in record["verdict_reason"]:
        raise AssertionError(record["verdict_reason"])


def test_the_negative_verdict_falls_below_the_smaller_candidate_bound() -> None:
    def record_at(correct: int) -> dict[str, Any]:
        cells = {
            label: {
                event("1100", correct_raw(label, "1100")): correct,
                event("1100", 1 - correct_raw(label, "1100")): 900 - correct,
            }
            for label in LABELS
        }
        manifest, results = manifest_and_results(cells)
        return rehearsal.analyze_results(manifest, results, manifest["frames"])

    between = record_at(603)
    benchmark, pooled = between["benchmark"], between["pooled"]
    upper = pooled["fidelity"] + pooled["radius"]
    if not benchmark["bound_at_reported_attempts"] < upper < benchmark["bound_at_modeled_attempts"]:
        raise AssertionError((benchmark, pooled))
    if between["verdict"] != "inconclusive":
        raise AssertionError(between["verdict"])
    if record_at(540)["verdict"] != "at-or-below-classical":
        raise AssertionError("a fidelity well below both bounds is not at-or-below-classical")


def test_check_refuses_a_registered_job_without_its_case(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    request = rehearsal.Request("job-01", rehearsal.LAYOUT, rehearsal.JOB_01_COMPILATION_SEEDS, rehearsal.ANCHOR_READ)
    monkeypatch.setattr(rehearsal, "CASES", tmp_path)
    monkeypatch.setitem(rehearsal.JOBS, "job-01", rehearsal.Job(request, 900, 1_200_000, 2.2, 120.0))
    monkeypatch.delitem(rehearsal.JOBS, "job-00")
    with pytest.raises(ValueError, match="has no cases.json"):
        rehearsal.check()


def descriptive_manifest() -> dict[str, Any]:
    """Job-00's settings run as two blocks, B mirrored, with job-01's seeds and a descriptive preregistration."""
    manifest = load("cases.json")
    first = [dict(setting, block="A") for setting in manifest["settings"]]
    second = [dict(setting, block="B") for setting in reversed(manifest["settings"])]
    settings = first + second
    for index, setting in enumerate(settings):
        setting["compilation_seed"] = rehearsal.JOB_01_COMPILATION_SEEDS[index]
        setting["observation_index"] = index
    manifest["settings"] = settings
    manifest["iterations"] = len(settings)
    planned = 1200
    manifest["preregistered"] = {
        "rule": rehearsal.DESCRIPTIVE,
        "alpha": 0.01,
        "planned_accepted": planned,
        "lambda": math.sqrt(8 * math.log(100) / planned),
        "homogeneity_alpha": 0.01,
        "sample_probability": manifest["preregistered"]["sample_probability"],
        "comparisons": [
            {"name": "two-copy", "bound": 0.75, "assumptions": ["a"]},
            {"name": "attempt-box", "bound": 0.7167, "ratio": 1.1, "assumptions": ["b"]},
        ],
    }
    return manifest


def descriptive_results(manifest: dict[str, Any], correct: dict[str, int], wrong: dict[str, int]) -> dict[str, Any]:
    """Per-iteration counts keyed by `block+label`: `correct` and `wrong` accepted events and 400 pattern rejections."""
    iterations = []
    for setting in manifest["settings"]:
        key = setting["block"] + setting["label"]
        good = correct_raw(setting["label"], "1100")
        counts = {event("1100", good): correct[key], event("1010", 0): 400}
        if wrong[key]:
            counts[event("1100", 1 - good)] = wrong[key]
        iterations.append(
            {
                "iteration": {
                    "circuit_params": setting["circuit_params"],
                    "compilation_seed": setting["compilation_seed"],
                },
                "counts": counts,
                "samples": sum(counts.values()),
                "result_fields": {"nb_shots_used": sum(counts.values()), "physical_perf": 0.01},
            }
        )
    return {"partial": False, "iterations": iterations}


def test_the_anytime_lower_bound_equals_the_hoeffding_radius_at_the_planned_count() -> None:
    lam = math.sqrt(8 * math.log(100) / 1200)
    bound = rehearsal.anytime_lower_bound(1000, 1200, lam, 0.01)
    if abs(bound - (1000 / 1200 - rehearsal.hoeffding_radius(0.01, 1200))) > 1e-12:
        raise AssertionError(bound)
    if rehearsal.anytime_lower_bound(500, 600, lam, 0.01) >= 500 / 600 - rehearsal.hoeffding_radius(0.01, 600) + 1e-9:
        raise AssertionError("a smaller count than planned is charged no more than the Hoeffding radius")


def test_descriptive_analysis_binds_blocks_by_seed_and_evaluates_the_comparisons(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(rehearsal, "break_even_ratio", lambda probability, lower: {"status": "stub", "ratio": None})
    manifest = descriptive_manifest()
    keys = [s["block"] + s["label"] for s in manifest["settings"]]
    correct = dict.fromkeys(keys, 90)
    wrong = dict.fromkeys(keys, 10)
    correct["B+Z"], wrong["B+Z"] = 70, 30
    results = descriptive_results(manifest, correct, wrong)
    results["iterations"].reverse()
    record = rehearsal.analyze_results(manifest, results, manifest["frames"])
    by_key = {row["block"] + row["label"]: row for row in record["iterations"]}
    if (by_key["B+Z"]["correct"], by_key["A+Z"]["correct"]) != (70, 90):
        raise AssertionError("block B's +Z iteration bound to block A's setting")
    pooled = record["pooled"]
    if pooled["accepted"] != 1200 or pooled["correct"] != 1060 or record["status"] != "complete":
        raise AssertionError(record["status"])
    labels = [c["label"] for c in record["comparisons"]]
    if labels != ["exceeds-under-assumptions", "exceeds-under-assumptions"]:
        raise AssertionError(record["comparisons"])
    if record["homogeneity"]["tests"]["+Z"]["status"] != "consistent":
        raise AssertionError(record["homogeneity"]["tests"]["+Z"])


def test_descriptive_analysis_vetoes_the_comparisons_when_blocks_differ(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(rehearsal, "break_even_ratio", lambda probability, lower: {"status": "stub", "ratio": None})
    manifest = descriptive_manifest()
    keys = [s["block"] + s["label"] for s in manifest["settings"]]
    correct, wrong = dict.fromkeys(keys, 95), dict.fromkeys(keys, 5)
    correct["B-X"], wrong["B-X"] = 40, 60
    record = rehearsal.analyze_results(manifest, descriptive_results(manifest, correct, wrong), manifest["frames"])
    if record["homogeneity"]["differ"] != ["-X"] or "blocks differ" not in record["status"]:
        raise AssertionError(record["homogeneity"])
    if {c["label"] for c in record["comparisons"]} != {"vetoed-blocks-differ"}:
        raise AssertionError(record["comparisons"])
    if record["break_even_ratio"]["status"] != "not-evaluated":
        raise AssertionError(record["break_even_ratio"])


def test_descriptive_analysis_of_a_partial_job_evaluates_no_comparison() -> None:
    manifest = descriptive_manifest()
    keys = [s["block"] + s["label"] for s in manifest["settings"]]
    results = descriptive_results(manifest, dict.fromkeys(keys, 95), dict.fromkeys(keys, 5))
    results["partial"] = True
    results["iterations"][11] = {"error": "canceled"}
    record = rehearsal.analyze_results(manifest, results, manifest["frames"])
    if {c["label"] for c in record["comparisons"]} != {"not-evaluated"} or record["status"] != (
        "partial job: descriptive counts only"
    ):
        raise AssertionError((record["status"], record["comparisons"]))
    if record["uncounted_iterations"] != ["error"] or record["homogeneity"]["tests"]["+Z"]["status"] != "untestable":
        raise AssertionError(record["homogeneity"])


def test_the_attempt_box_bound_takes_the_largest_of_its_64_vertices(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[dict[str, int]] = []

    def stand_in(attempts: dict[str, int]) -> float:
        seen.append(attempts)
        return sum(attempts.values()) / 1e15

    monkeypatch.setattr(rehearsal, "vertex_bound", stand_in)
    monkeypatch.setattr(rehearsal, "ordered_map", lambda function, items, min_items=1: [function(i) for i in items])
    probability = dict.fromkeys(LABELS, 1.0)
    value = rehearsal.box_bound(probability, 2.0)
    if len(seen) != 64 or len({tuple(sorted(a.items())) for a in seen}) != 64:
        raise AssertionError(len(seen))
    if abs(value - 6 * 2e12 / 1e15) > 1e-12:
        raise AssertionError(value)


@pytest.mark.audit
def test_the_certified_attempt_box_bound_at_ratio_1_1_bounds_an_interior_profile() -> None:
    probability = load("noise-model.json")["derived"]["sample_probability"]
    box = rehearsal.box_bound(probability, 1.1)
    if not 0.7166 < box < 0.7168:
        raise AssertionError(box)
    factors = (1.04, 0.97, 1.0, 1.08, 0.93, 1.02)
    inside = {label: round(1e12 * f / probability[label]) for label, f in zip(LABELS, factors, strict=True)}
    if rehearsal.vertex_bound(inside) > box + 1e-9:
        raise AssertionError("an interior attempt profile exceeds the vertex maximum")


def test_break_even_ratio_bisects_the_box_bound(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(rehearsal, "box_bound", lambda probability, ratio: 0.6 + 0.1 * ratio)
    found = rehearsal.break_even_ratio({}, 0.82)
    if found["status"] != "found" or abs(found["ratio"] - 2.2) > rehearsal.BREAK_EVEN_TOLERANCE:
        raise AssertionError(found)
    if rehearsal.break_even_ratio({}, 0.65)["status"] != "below-one":
        raise AssertionError("a lower bound under the center bound has no break-even ratio")
    if rehearsal.break_even_ratio({}, 0.95)["status"] != "at-least-ceiling":
        raise AssertionError("a lower bound above the ceiling's bound reports the ceiling")


def test_a_descriptive_case_admits_only_its_prepared_read(monkeypatch: pytest.MonkeyPatch) -> None:
    read = json.loads((ROOT / rehearsal.ANCHOR_READ).read_text(encoding="utf-8"))["processors"][rehearsal.PLATFORM]
    request = rehearsal.Request(
        "job-01", rehearsal.LAYOUT, rehearsal.JOB_01_COMPILATION_SEEDS, rehearsal.ANCHOR_READ, rehearsal.DESCRIPTIVE, 2
    )
    same = rehearsal.model_at(read["perfs"], request)
    if not same["inside_justified_range"] or same["perfs_sha256"] != same["prepared_perfs_sha256"]:
        raise AssertionError(same)
    changed = copy.deepcopy(read["perfs"])
    changed["g2 (%)"] = changed["g2 (%)"] + 0.1
    moved = rehearsal.model_at(changed, request)
    if moved["inside_justified_range"] or "differs from the prepared read" not in rehearsal.admission_failure(moved):
        raise AssertionError(moved)
