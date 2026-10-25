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
    if any("compilation_seed" in setting for setting in manifest["settings"]):
        raise AssertionError("a setting names a compilation seed")
    if manifest["min_detected_photons"] != 3 or manifest["mitigations"] != [] or manifest["max_duration"] != 300:
        raise AssertionError("the request departs from the design's fields")
    if sorted(rehearsal.rejections(manifest, circuit)) != ["herald photon", "perturbed unitary", "shifted source"]:
        raise AssertionError("a mutated request validates")


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
