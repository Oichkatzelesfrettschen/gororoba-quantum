"""Contracts of the low-CZ null-block case: the b0 replay, the role-map pins, the block laws, the series, the joint
readout statistics and the preregistered decisions.

Each test compiles only the committed SELECTION, never the 120-layout search (`--select` repeats that on demand).
Collected-run fixtures hold expected counts (largest remainder, no random draw) in qi_platform.collect's layout.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import pytest
import qi_pathion_coset_coin_cases as cc
import qi_pathion_one_cz_null_cases as oc

import pathion_coset_block as pcb
import qi_records


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_b0_replay_is_byte_equal_to_the_retained_circuit() -> None:
    digest = oc.replay_check()
    _expect(digest == oc.COIN_PINS["b0.cq"], "the replay digest differs from the pinned one")
    ref = oc.reference()
    _expect(ref["cz"] == 21 and ref["region"] == (2, 4, 8, 11, 12), "the retained b0 changed")


def test_pins_refuse_a_changed_retained_file(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(oc.COIN_PINS, "b0.cq", "0" * 64)
    oc.reference.cache_clear()
    try:
        with pytest.raises(ValueError, match="differs from the retained record"):
            oc.reference()
    finally:
        monkeypatch.undo()
        oc.reference.cache_clear()


@pytest.mark.parametrize("mode", oc.PIN_MODES)
@pytest.mark.parametrize("name", [n for n, _ in oc.LOW_CZ])
def test_selected_block_sits_on_its_pin(mode: str, name: str) -> None:
    ref = oc.reference()
    entry = oc.routed(mode, name)
    draw_index, layout = oc.SELECTION[(mode, name)]
    _expect(entry["transpiler_seed"] == oc.draw_values()[draw_index], f"{name}: seed is not the draw value")
    index = [n for n, _ in oc.LOW_CZ].index(name)
    _expect(
        index * oc.SEEDS_PER_BLOCK <= draw_index < (index + 1) * oc.SEEDS_PER_BLOCK, f"{name}: draw index off its slice"
    )
    _expect(entry["initial_layout"] == list(layout), f"{name}: initial layout departs from SELECTION")
    roles = entry["roles"]
    _expect(set(roles.values()) == set(ref["region"]), f"{name}: roles do not cover the region")
    _expect(roles["selector"] == ref["roles"]["selector"] and roles["coin"] == ref["roles"]["coin"], f"{name}: pin")
    if mode == "roles":
        _expect(roles == ref["roles"], f"{name}: the role map differs from b0's")
        _expect(entry["cz"] == 12, f"{name}: {entry['cz']} CZ")
    else:
        _expect(entry["cz"] == 6, f"{name}: {entry['cz']} CZ")


def test_pin_predicate_reads_the_final_layout() -> None:
    want = tuple(oc.want_layout())
    _expect(oc.pinned("roles", want), "b0's own layout fails the roles pin")
    swapped = (want[1], want[0], *want[2:])
    _expect(not oc.pinned("roles", swapped) and oc.pinned("selector_coin", swapped), "data swap is mis-read")
    moved = (*want[:3], want[4], want[3])
    _expect(not oc.pinned("selector_coin", moved), "a selector-coin swap passes the selector_coin pin")
    with pytest.raises(ValueError, match="unknown pin mode"):
        oc.pinned("none", want)


@pytest.mark.parametrize("name", [n for n, _ in oc.LOW_CZ])
def test_block_laws_match_the_cayley_dickson_map(name: str) -> None:
    """Each low-CZ block is a null block of the operand e1 + e17: its contrast restricts the module's six-qubit law,
    its routed law matches the logical coin law within the pi/36 grid rounding, and its selector contrast is zero."""
    block = oc.BLOCKS[name]
    _expect(pcb.contrast_restriction_error(block) < 1e-12, f"{name}: contrast restriction")
    _expect(pcb.aligned_in_block(block) == 0, f"{name}: the block holds aligned pairs")
    for mode in oc.PIN_MODES:
        entry = oc.routed(mode, name)
        plus, minus = pcb.coin_arm_laws(pcb.block_template(block, measure=False, coin=True))
        routed_plus, routed_minus = cc.arm_laws(entry["ideal"])
        gap = max(np.abs(plus - routed_plus).max(), np.abs(minus - routed_minus).max())
        _expect(gap < 0.05, f"{name} {mode}: grid rounding moved a law by {gap}")
        _expect(abs(entry["ideal_selector_contrast"]) < 1e-9, f"{name} {mode}: ideal selector contrast")
        _expect(abs(float(np.sum(entry["ideal_c"]))) < 0.05, f"{name} {mode}: ideal null sum")


def test_templates_run_through_the_coin_series_constants() -> None:
    _expect(oc.TEMPLATES == ("b0", "k4", "k8", "k12"), "template order")
    _expect(oc.KEYS == ("d0", "d1", "d2", "selector", "coin"), "role keys")
    _expect(oc.BLOCKS["b0"].coset == 0 and oc.BLOCKS["k4"].coset == 4, "cosets")
    labels = {n: pcb.output_labels(oc.BLOCKS[n]) for n in oc.TEMPLATES}
    _expect(sorted(sum(labels.values(), [])) == list(range(32)), "the four cosets do not tile the 32 algebra indices")


# Series, twins, decisions -----------------------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "results/quantum_inspire/cases"
TWIN_LOG = ROOT / "docs/evidence/pathion-kernel-map/conjectures/c2_one_cz_twins.txt"
SUBMIT = ROOT / "scripts/qi_pathion_one_cz_null_submit.sh"


@pytest.fixture(scope="module")
def built() -> dict[str, dict[str, str]]:
    return oc.build()


@pytest.fixture(scope="module")
def worlds(built: dict[str, dict[str, str]]) -> dict[str, dict[str, list[str]]]:
    files = built[oc.TUNA_SERIES]
    manifest = json.loads(files["batch-00/cases.json"])
    return {w: oc.synthetic_series(files, manifest, **kw) for w, kw in oc.WORLDS.items()}


@pytest.mark.audit
def test_the_committed_case_directory_reproduces_its_bytes() -> None:
    oc.check(CASES, operating=False)
    base = CASES / oc.TUNA_SERIES
    copies = [p / "b0.cq" for p in base.glob("batch-*") if (p / "b0.cq").exists()]
    _expect(len(copies) == 2, "b0 appears in its two base batches")
    _expect(all(c.read_bytes() == (oc.COIN_BATCH / "b0.cq").read_bytes() for c in copies), "b0 is the retained circuit")


@pytest.mark.audit
def test_the_stored_operating_characteristics_replay() -> None:
    oc.check(CASES)


def test_the_series_holds_fifty_six_jobs_in_nineteen_batches_within_the_platform_limits(
    built: dict[str, dict[str, str]],
) -> None:
    files = built[oc.TUNA_SERIES]
    series = json.loads(files["cases.json"])
    _expect([len(b["files"]) for b in series["batches"]] == [3] * 18 + [2], "batch sizes")
    shots = {}
    for batch in series["batches"]:
        manifest = json.loads(files[f"{batch['batch']}/cases.json"])
        _expect(manifest["shots"] <= 131072 and manifest["register"] == [2, 4, 8, 11, 12], "limits")
        shots[batch["batch"]] = (manifest["kind"], manifest["template"], manifest["shots"])
    kinds = [v[0] for v in shots.values()]
    _expect(kinds[:16].count("base") == 8 and kinds[:16].count("twin") == 8 and kinds[16:] == ["joint"] * 3, f"{kinds}")
    for kind, template, n in shots.values():
        want = (
            oc.JOINT_SHOTS
            if kind == "joint"
            else oc.CONTROL_SHOTS
            if (kind, template) == ("base", "b0")
            else oc.BATCH_SHOTS
        )
        _expect(n == want, f"{kind} {template}: {n} shots")
    qx = json.loads(built[oc.QX_SERIES]["cases.json"])
    _expect(
        [len(b["files"]) for b in qx["batches"]] == [5, 5, 2], "the QX control holds every circuit, five to a batch"
    )


def test_the_batch_order_is_a_palindrome_over_templates_and_kinds_with_each_template_in_both_rounds() -> None:
    order = oc.batch_order()
    _expect(len(order) == 16, "sixteen template batches")
    forward = [(t, k) for t, k, r in order if r == 0]
    mirror = [(t, k) for t, k, r in order if r == 1]
    _expect(mirror == forward[::-1], "the second round mirrors the first")
    for template in oc.TEMPLATES:
        for kind in ("base", "twin"):
            _expect([r for t, k, r in order if (t, k) == (template, kind)] == [0, 1], f"{template} {kind} replicates")


def test_every_twin_is_the_template_without_the_coin_hadamard(built: dict[str, dict[str, str]]) -> None:
    files = built[oc.TUNA_SERIES]
    by_file = {rel.split("/")[1]: text for rel, text in files.items() if rel.endswith(".cq") and "readout" not in rel}
    for name in oc.TEMPLATES:
        base_lines = [ln for ln in by_file[f"{name}.cq"].splitlines() if not ln.startswith("//")]
        for value in (0, 1):
            twin = oc.twin_entry(name, value)
            twin_lines = [ln for ln in by_file[oc.twin_file(name, value)].splitlines() if not ln.startswith("//")]
            _expect(twin["removed"] == ["rz", "sx", "rz"], f"{name}: removed {twin['removed']}")
            extra = [ln for ln in twin_lines if ln not in base_lines]
            _expect(extra == (["X q[2]"] if value else []), f"{name} coin {value}: added {extra}")
            _expect(
                sum(ln.startswith("CZ") for ln in twin_lines) == sum(ln.startswith("CZ") for ln in base_lines), "CZ"
            )
            kept = [ln for ln in base_lines if ln not in twin_lines]
            _expect(
                len(kept) == 3 and all(" q[2]" in ln for ln in kept),
                f"{name}: the base-only lines are the coin Hadamard",
            )
            ideal = twin["ideal"]
            coin = sum(ideal[i] for i in range(oc.NOUT) if (i >> oc.COIN) & 1)
            _expect(abs(coin - value) < 1e-9, f"{name} coin {value}: ideal coin read {coin}")


def test_a_run_that_is_not_a_coin_hadamard_refuses_the_twin() -> None:
    from qiskit import QuantumCircuit

    base = oc.series_plan()["templates"]["k4"]["circuit"]
    bad = base.copy()
    index = next(i for i, inst in enumerate(bad.data) if inst.operation.name == "sx")
    bad.data.pop(index)
    with pytest.raises(ValueError, match="not the Hadamard"):
        oc.coin_fixed(bad, 0)
    del QuantumCircuit


def test_the_series_templates_share_the_selector_and_coin_qubits_and_the_blocks_route_to_six_cz(
    built: dict[str, dict[str, str]],
) -> None:
    templates = json.loads(built[oc.TUNA_SERIES]["batch-00/cases.json"])["templates"]
    ref = oc.reference()["roles"]
    for name, t in templates.items():
        _expect(t["roles"]["selector"] == ref["selector"] and t["roles"]["coin"] == ref["coin"], f"{name}: roles")
    _expect([templates[n]["cz"] for n in oc.TEMPLATES] == [21, 6, 6, 6], "CZ counts")
    _expect(templates["b0"]["roles"] == ref, "b0 keeps its retained role map")


def test_the_calibration_circuits_prepare_every_basis_state_of_the_coin_the_selector_and_q12_with_x_gates_only(
    built: dict[str, dict[str, str]],
) -> None:
    files = built[oc.TUNA_SERIES]
    seen = set()
    for rel, text in files.items():
        if "/joint-" not in rel:
            continue
        gates = [line for line in text.splitlines() if line and line[0] not in "/vqb"]
        flipped = {int(re.search(r"\[(\d+)\]", g).group(1)) for g in gates if g.startswith("X ")}  # type: ignore[union-attr]
        _expect(flipped <= {2, 8, 12} and all(g.startswith("X ") for g in gates if "barrier" not in g), f"{rel}: gates")
        seen.add(tuple(int(q in flipped) for q in (2, 8, 12)))
    _expect(seen == set(oc.JOINT_PREPS), f"preparations {sorted(seen)}")
    batches = [{p for p in preps} for preps in oc.JOINT_BATCHES]
    for third in (0, 1):
        _expect(any({(1, 1, third), (0, 1, third)} <= b for b in batches), f"the matched pair at q12 = {third} splits")


def _twin_log() -> dict[str, dict[str, tuple[float, float]]]:
    table: dict[str, dict[str, tuple[float, float]]] = {}
    for line in TWIN_LOG.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^  (\S.*?)\s{2,}((?:[+-]\d\.\d+ / [+-]\d\.\d+\s*){4})$", line)
        if match:
            cells = re.findall(r"([+-]\d\.\d+) / ([+-]\d\.\d+)", match.group(2))
            table[match.group(1)] = dict(zip(oc.TEMPLATES, ((float(a), float(b)) for a, b in cells), strict=True))
    return table


def test_the_predicted_contrasts_equal_the_twin_simulation_log() -> None:
    log = _twin_log()
    over = next(k for k in log if k.startswith("X-axis error"))
    drop = next(k for k in log if k.startswith("selector dropout"))
    flip = next(k for k in log if k.startswith("selector flip"))
    for key, label, rows in (
        ("over_rotation", over, ("b0", "k4")),
        ("coin_dropout", drop, ("b0", "k4")),
        ("q12_correlation", flip, ("b0", "k4")),
    ):
        want = oc.PREDICTED[key]
        _expect(abs(log[label]["b0"][0] - want["s_b0"]) < 6e-5 + 1e-9, f"{key} s_b0")
        _expect(abs(log[label]["b0"][1] - want["t_b0"]) < 6e-5 + 1e-9, f"{key} t_b0 {log[label]['b0']} {want['t_b0']}")
        _expect(abs(log[label]["k4"][0] - want["s_k"]) < 4e-4, f"{key} s_k {log[label]['k4']}")
        _expect(abs(log[label]["k4"][1] - want["t_k"]) < 4e-4, f"{key} t_k")
        del rows
    worst = re.search(
        r"admitted set: .*max \|k4 s\| ([\d.]+), max \|k4 t\| ([\d.]+)", TWIN_LOG.read_text(encoding="utf-8")
    )
    if worst is None:
        raise AssertionError("the log states the admitted bound")
    _expect(abs(float(worst.group(1)) - oc.PREDICTED["over_rotation_y_axis"]["s_k"]) < 6e-5, "worst s_k")
    _expect(abs(float(worst.group(2)) - oc.PREDICTED["over_rotation_y_axis"]["t_k"]) < 6e-5, "worst t_k")


def test_the_design_sizes_the_series_from_the_coin_series_timings() -> None:
    plan = json.loads((CASES / oc.TUNA_SERIES / "prediction.json").read_text(encoding="utf-8"))["design"]
    _expect(plan["jobs"] == 56 and plan["batches"] == 19 and plan["shots_total"] == 2293760, f"{plan}")
    low, high = plan["execution_seconds_range"]
    _expect(1300 < low < high < 1600, f"seconds {plan['execution_seconds_range']}")
    _expect(
        plan["longest_job_seconds"] < plan["job_seconds_limit"] == 300, f"longest job {plan['longest_job_seconds']}"
    )
    _expect(plan["pause_seconds_total"] == 540, "eighteen pauses of 30 s")
    _expect(plan["pooled_se"]["b0_base"] < 0.002 and plan["pooled_se"]["twin"] < 0.003, f"{plan['pooled_se']}")


@pytest.mark.parametrize("world", list(oc.WORLDS))
def test_each_simulated_world_reads_its_preregistered_row(
    world: str, built: dict[str, dict[str, str]], worlds: dict[str, dict[str, list[str]]]
) -> None:
    manifest = json.loads(built[oc.TUNA_SERIES]["batch-00/cases.json"])
    result = oc.evaluate(worlds[world], manifest)
    _expect(result["decision"]["label"] == oc.WORLD_LABELS[world], f"{world}: {result['decision']}")
    json.dumps(result, allow_nan=False)


def test_the_calibration_statistics_recover_the_injected_readout_effects(
    built: dict[str, dict[str, str]], worlds: dict[str, dict[str, list[str]]]
) -> None:
    manifest = json.loads(built[oc.TUNA_SERIES]["batch-00/cases.json"])
    e10 = 0.06  # the synthetic assignment of q8 (register index 2): (0.04, 0.06)
    coin = oc.joint_statistics(worlds["coin_dropout"], manifest)["coin_dropout"]
    _expect(abs(coin["D"]["value"] - 0.0362 * (1 - e10)) < 2e-4, f"D {coin['D']}")
    _expect(len(coin["matched_pairs"]) == 2, "two matched pairs")
    q12 = oc.joint_statistics(worlds["q12_correlation"], manifest)["q12_correlation"]["G_by_selector"]
    for s, rate in (("selector_prepared_0", 0.04), ("selector_prepared_1", 0.06)):
        want = 0.036 * (1 - 2 * rate)
        _expect(abs(q12[s]["value"] - want) < 2e-4, f"G {s}: {q12[s]['value']} against {want}")
    clean = oc.joint_statistics(worlds["absent"], manifest)
    _expect(abs(clean["coin_dropout"]["D"]["value"]) < 1e-4, "clean device reads D = 0")
    with pytest.raises(ValueError, match="not all eight"):
        oc.joint_statistics({k: v for k, v in worlds["absent"].items() if "joint-111" not in k}, manifest)


def _rows(**kwargs: Any) -> dict[str, dict[str, list[tuple[float, float]]]]:
    """Batch estimates (two replicates each) from per-template base and twin values."""
    base = kwargs.get("base", {})
    twin = kwargs.get("twin", {})
    se_base = {t: 1 / np.sqrt(oc.CONTROL_SHOTS if t == "b0" else oc.BATCH_SHOTS) for t in oc.TEMPLATES}
    se_twin = np.sqrt(0.5 / oc.BATCH_SHOTS)
    return {
        t: {
            "base": [(base.get(t, 0.0), se_base[t])] * oc.REPLICATES,
            "twin": [(twin.get(t, 0.0), se_twin)] * oc.REPLICATES,
        }
        for t in oc.TEMPLATES
    }


def test_every_decision_label_has_a_row_and_the_deciding_labels_are_exactly_the_three_mechanism_rows() -> None:
    _expect(set(oc.OUTCOMES) >= set(oc.DECIDING), "every deciding label has an outcome")
    _expect(oc.DECIDING == ("zero", "b0_like", "superposition_only"), "deciding labels")
    for label, (outcome, effect) in oc.OUTCOMES.items():
        _expect(bool(outcome) and bool(effect), label)
        _expect(("falsifier" in effect) <= (label == "zero"), f"{label}: only the zero row names the falsifier")
    _expect("unmet" in oc.OUTCOMES["zero"][1] and "inconsistent" in oc.OUTCOMES["zero"][1], "the zero row's falsifier")


def test_the_decision_reads_each_preregistered_row_on_hand_built_estimates() -> None:
    offset = {"b0": 0.0164}
    zero = oc.decide_estimates(_rows(base=offset, twin={"b0": 0.0166}))
    _expect(zero["label"] == "zero", f"{zero['numbers']}")
    like = oc.decide_estimates(_rows(base={t: 0.0164 for t in oc.TEMPLATES}, twin={t: 0.017 for t in oc.TEMPLATES}))
    _expect(like["label"] == "b0_like", f"{like['numbers']}")
    absent = oc.decide_estimates(_rows())
    _expect(absent["label"] == "offset_absent" and not absent["decided"], "absent")
    only = oc.decide_estimates(_rows(base={t: 0.02 for t in oc.TEMPLATES}))
    _expect(only["label"] == "superposition_only", f"{only['numbers']}")
    between = oc.decide_estimates(
        _rows(
            base={"b0": 0.0164, "k4": 0.005, "k8": 0.005, "k12": 0.005},
            twin={"b0": 0.0166, "k4": 0.005, "k8": 0.005, "k12": 0.005},
        )
    )
    _expect(between["label"] == "intermediate" and not between["decided"], f"{between['numbers']['m_six_cz']}")
    negative = oc.decide_estimates(
        _rows(
            base={"b0": 0.0164, "k4": -0.01, "k8": -0.01, "k12": -0.01},
            twin={"b0": 0.0166, "k4": -0.01, "k8": -0.01, "k12": -0.01},
        )
    )
    _expect(negative["label"] == "unresolved", f"{negative['numbers']['m_six_cz']}")
    context = oc.decide_estimates(
        _rows(base={"b0": 0.0164, "k4": 0.012, "k8": 0.012, "k12": 0.012}, twin={"b0": 0.0166})
    )
    _expect(context["label"] == "unresolved_context", f"{context['label']}")


def _world_rows(world: str) -> dict[str, dict[str, list[tuple[float, float]]]]:
    """Batch estimates at the means of a PREDICTED world and the design standard errors."""
    mean = oc.PREDICTED[world]
    return _rows(
        base={t: mean["s_b0" if t == "b0" else "s_k"] for t in oc.TEMPLATES},
        twin={t: mean["t_b0" if t == "b0" else "t_k"] for t in oc.TEMPLATES},
    )


def test_the_rz_rotating_world_does_not_read_b0_like_at_the_band() -> None:
    """The X rotation before every single-qubit gate, Rz included, leaves the 6-CZ mean about 3.4 combined se below the
    b0 combination: outside the band of B0_LIKE_Z = 2, so it reads intermediate and refutes nothing."""
    _expect(oc.B0_LIKE_Z == 2.0 and "over_rotation_x_all_before" in oc.OUTSIDE_ADMITTED, "constants")
    result = oc.decide_estimates(_world_rows("over_rotation_x_all_before"))
    gap = result["numbers"]["r_minus_m"][0] / result["numbers"]["r_minus_m"][1]
    _expect(result["label"] == "intermediate" and gap > oc.B0_LIKE_Z, f"{result['label']} at {gap:.2f} se")
    _expect(not result["decided"] and result["a5_186"].startswith("unchanged"), "an intermediate row decides nothing")
    after = oc.decide_estimates(_world_rows("over_rotation_x_all_after"))
    _expect(after["label"] == "zero", f"{after['label']}")


def test_the_intermediate_label_sits_between_zero_and_b0_like_and_the_band_decides_it(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _expect("intermediate" in oc.OUTCOMES and "intermediate" not in oc.DECIDING, "the label is not deciding")
    _expect("intermediate" in oc.OUTCOMES["intermediate"][0], "the outcome text names the intermediate response")
    rows = _rows(
        base={"b0": 0.0164, **{t: 0.0113 for t in oc.LOW_NAMES}},
        twin={"b0": 0.0166, **{t: 0.0113 for t in oc.LOW_NAMES}},
    )
    narrow = oc.decide_estimates(rows)
    gap = narrow["numbers"]["r_minus_m"][0] / narrow["numbers"]["r_minus_m"][1]
    _expect(2.0 < gap < 3.0 and narrow["label"] == "intermediate", f"{narrow['label']} at {gap:.2f} se")
    monkeypatch.setattr(oc, "B0_LIKE_Z", 3.0)
    _expect(oc.decide_estimates(rows)["label"] == "b0_like", "a band of 3 se reads the same response as b0-like")


def test_heterogeneous_blocks_and_batches_are_unresolved_and_never_pooled_into_a_class() -> None:
    """Opposite 6-CZ blocks pool to zero and one large block pools to the b0 value; the bound refuses both."""
    opposite = _rows(base={"b0": 0.0164, "k4": 0.03, "k8": -0.03}, twin={"b0": 0.0166, "k4": 0.03, "k8": -0.03})
    _expect(oc.decide_estimates(opposite)["label"] == "unresolved_block", "opposite blocks")
    single = _rows(base={"b0": 0.0164, "k4": 0.03}, twin={"b0": 0.0166, "k4": 0.03})
    _expect(oc.decide_estimates(single)["label"] == "unresolved_block", "one large block")
    rows = _rows(base={"b0": 0.0164}, twin={"b0": 0.0166})
    se = rows["b0"]["base"][0][1]
    rows["b0"]["base"] = [(0.0164 + 4 * se, se), (0.0164 - 4 * se, se)]
    _expect(oc.decide_estimates(rows)["label"] == "unresolved_batch", "disagreeing replicate batches")


def test_the_operating_characteristics_state_the_chance_of_deciding_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    ocs = oc.operating_characteristics(draws=1500)
    over = ocs["over_rotation"]
    _expect(over.get("zero", 0.0) >= 0.9 and sum(v for k, v in over.items() if k != "zero") <= 0.1, f"{over}")
    _expect(ocs["coin_dropout"].get("b0_like", 0.0) >= 0.88, f"{ocs['coin_dropout']}")
    before = ocs["over_rotation_x_all_before"]
    _expect(before.get("b0_like", 0.0) <= 0.15 and before.get("intermediate", 0.0) >= 0.75, f"{before}")
    _expect(ocs["absent"].get("offset_absent", 0.0) >= 0.9 and not ocs["absent"].get("zero"), f"{ocs['absent']}")
    for world in ("over_rotation", "q12_correlation", "coin_dropout"):
        wrong = {k: v for k, v in ocs[world].items() if k in ("zero", "b0_like", "superposition_only")}
        _expect(max(wrong, key=lambda k: wrong[k]) == oc.WORLD_LABELS[world], f"{world}: {wrong}")
    stored = json.loads((CASES / oc.TUNA_SERIES / "prediction.json").read_text(encoding="utf-8"))
    nominal = stored["operating_characteristics"]["stationary"]["over_rotation"]
    _expect(nominal["zero"] >= 0.8, f"the over-rotation world decides in {nominal['zero']} of runs")
    _expect(stored["operating_characteristics"]["stationary"]["coin_dropout"]["b0_like"] >= 0.9, "dropout power")
    wrong = stored["operating_characteristics"]["stationary"]["over_rotation_x_all_before"].get("b0_like", 0.0)
    _expect(wrong < 0.1, f"the Rz-rotating world reads b0-like in {wrong} of runs")
    _expect(stored["outside_admitted_set"] == list(oc.OUTSIDE_ADMITTED), "the outside-the-set rows")
    for key in oc.OUTSIDE_ADMITTED:
        _expect(key in stored["operating_characteristics"]["stationary"], f"{key} has a stored row")
    monkeypatch.setattr(oc, "OC_SEED_INDEX", 0)
    first = oc.operating_characteristics(draws=300)
    _expect(first == oc.operating_characteristics(draws=300), "the operating characteristics are deterministic")


def test_a_coarser_standard_error_than_the_limit_is_flagged_in_the_calibration(
    built: dict[str, dict[str, str]], worlds: dict[str, dict[str, list[str]]], monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest = json.loads(built[oc.TUNA_SERIES]["batch-00/cases.json"])
    monkeypatch.setattr(oc, "JOINT_SE_LIMIT", 1e-5)
    result = oc.evaluate(worlds["over_rotation"], manifest)
    _expect(not result["calibration"]["classes"]["informative"], "the calibration reads uninformative")
    _expect(result["decision"]["label"] == "zero", "the decider does not depend on the calibration")


def test_the_classes_read_the_preregistered_thresholds() -> None:
    _expect(oc.classify_large(0.036, 0.002) and not oc.classify_large(0.02, 0.002), "large threshold")
    _expect(oc.classify_large(0.031, 0.002) and not oc.classify_large(0.0, 0.002), "large with se")
    _expect(oc.classify_small([(0.0, 0.002), (0.004, 0.0015)]) and not oc.classify_small([(0.01, 0.002)]), "small")


def _runs(
    root: Path, series: str, files: dict[str, str], shots: dict[str, list[str]], batches: list[str] | None = None
) -> list[Path]:
    """Collected run directories `<stamp>-<series>-batch-NN` for the listed batches from case files and shot lists."""
    cases_root = root / "cases" / series
    for rel, text in files.items():
        path = cases_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    runs = root / "runs"
    dirs = []
    for batch in sorted(batches or {r.split("/")[0] for r in files if r.startswith("batch-")}):
        case_batch = cases_root / batch
        cases = json.loads((case_batch / "cases.json").read_text(encoding="utf-8"))
        run = runs / f"2026-11-07T000000Z-{series}-{batch}"
        shutil.copytree(case_batch, run)
        (run / "raw").mkdir()
        submitted: list[dict[str, Any]] = []
        collected: list[dict[str, Any]] = []
        n = int(batch.removeprefix("batch-"))
        for k, row in enumerate(cases["circuits"]):
            listed = shots[f"{batch}/{row['file']}"]
            (run / "raw" / f"{row['file']}.json").write_text(json.dumps(listed), encoding="utf-8")
            job_id = 100 * n + k
            submitted.append({"file": row["file"], "job": job_id, "sha256": row["sha256"]})
            job = {
                "id": job_id,
                "created_on": f"2026-11-07T00:{n:02d}:00.000000Z",
                "status": "completed",
                "batch_job_id": 77 + n,
                "queued_at": f"2026-11-07T00:{n:02d}:{k:02d}.000000Z",
                "finished_at": f"2026-11-07T01:{n:02d}:{k:02d}.000000Z",
                "number_of_shots": cases["shots"],
            }
            results = [
                {
                    "job_id": job_id,
                    "shots_requested": cases["shots"],
                    "shots_done": cases["shots"],
                    "results": dict(sorted(Counter(listed).items())),
                }
            ]
            collected.append({"file": row["file"], "job": job, "results": results, "logs": ""})
        receipt = {
            "schema": "qi-submission-v2",
            "state": "enqueued",
            "approval": "fixture",
            "backend": cases["backend"],
            "backend_type_id": cases["backend_type_id"],
            "cases_sha256": qi_records.digest((run / "cases.json").read_bytes()),
            "batch_job": 77 + n,
            "shots": cases["shots"],
            "jobs": submitted,
        }
        (run / "submission.json").write_text(json.dumps(receipt), encoding="utf-8")
        (run / "results.json").write_text(
            json.dumps({"schema": "qi-collection-v1", "transactions": [], "jobs": collected}), encoding="utf-8"
        )
        dirs.append(run)
    return dirs


def test_analyze_scores_collected_batches_and_reports_an_incomplete_series(
    tmp_path: Path, built: dict[str, dict[str, str]], worlds: dict[str, dict[str, list[str]]]
) -> None:
    dirs = _runs(tmp_path, oc.TUNA_SERIES, built[oc.TUNA_SERIES], worlds["over_rotation"])
    result = oc.analyze(dirs, tmp_path / "cases")
    _expect(result["complete"] and result["claim_kind"] == "hardware acquisition", f"{result.get('batches')}")
    json.dumps(result, allow_nan=False)
    _expect(result["decision"]["label"] == "zero", f"{result['decision']}")
    _expect(not result["drift_covariate"]["references"]["flagged"], "drift")
    partial = oc.analyze(dirs[:3], tmp_path / "cases")
    _expect(not partial["complete"] and partial["batches"] == ["batch-00", "batch-01", "batch-02"], f"{partial}")
    sanity = oc.sanity(dirs[:8], tmp_path / "cases")
    _expect(sanity["batches"] == [f"batch-{n:02d}" for n in range(8)] and sanity["drift"], "sanity")
    with pytest.raises((ValueError, SystemExit), match="differs from"):
        shutil.copy(dirs[0] / "readout-0.cq", dirs[0] / "b0.cq")
        oc.analyze(dirs, tmp_path / "cases")


def _qx_shots(files: dict[str, str], uniform: str | None = None) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for batch in sorted({rel.split("/")[0] for rel in files if rel.startswith("batch-")}):
        manifest = json.loads(files[f"{batch}/cases.json"])
        for row in manifest["circuits"]:
            ideal = [1.0 / oc.NOUT] * oc.NOUT if row["file"] == uniform else row["ideal"]
            roles = manifest["templates"][row["template"]]["roles"]
            counts = oc.cc.largest_remainder(np.array(ideal), manifest["shots"])
            out[f"{batch}/{row['file']}"] = oc.cc.place_counts(counts, oc.KEYS, roles, manifest["nqubits"])
    return out


def test_the_qx_control_passes_on_the_ideal_laws_and_fails_on_a_wrong_circuit(
    tmp_path: Path, built: dict[str, dict[str, str]]
) -> None:
    files = built[oc.QX_SERIES]
    good = oc.analyze(_runs(tmp_path / "g", oc.QX_SERIES, files, _qx_shots(files)), tmp_path / "g" / "cases")
    _expect(good["claim_kind"] == oc.CONTROL_KIND and good["qx_control"]["pass"], f"{good['qx_control']}")
    _expect(len(good["qx_control"]["arms"]) == 12, "every base circuit and twin is controlled")
    bad_shots = _qx_shots(files, uniform="k4-coin1.cq")
    bad = oc.analyze(_runs(tmp_path / "w", oc.QX_SERIES, files, bad_shots), tmp_path / "w" / "cases")
    _expect(not bad["qx_control"]["pass"], "a uniform law in a twin slot passed")


def _stub(tmp_path: Path, failures: list[str]) -> tuple[Path, Path]:
    """A stand-in for qi_platform.py: it logs every call, refuses the first submits with the given messages, then
    accepts every call."""
    log = tmp_path / "calls.log"
    script = tmp_path / "platform.py"
    script.write_text(
        "import sys\n"
        f"LOG = {str(log)!r}\n"
        f"REFUSALS = {failures!r}\n"
        "with open(LOG, 'a', encoding='utf-8') as handle:\n"
        "    handle.write(' '.join(sys.argv[1:]) + '\\n')\n"
        "if sys.argv[1] == 'submit':\n"
        "    count = sum(1 for line in open(LOG, encoding='utf-8') if line.startswith('submit'))\n"
        "    if count <= len(REFUSALS):\n"
        "        sys.exit(REFUSALS[count - 1])\n",
        encoding="utf-8",
    )
    return script, log


def _submit(tmp_path: Path, failures: list[str], batches: int = 2) -> tuple[int, str, str]:
    series = tmp_path / "series"
    for n in range(batches):
        (series / f"batch-{n:02d}").mkdir(parents=True)
    script, log = _stub(tmp_path, failures)
    env = {
        "PATH": "/usr/bin:/bin",
        "QI_PYTHON": sys.executable,
        "QI_PLATFORM": str(script),
        "SANITY_COMMAND": "true",
        "QI_PAUSE_SLEEP": "0",
    }
    done = subprocess.run(
        ["sh", str(SUBMIT), "7", str(series), str(tmp_path / "runs"), "STAMP", "QUOTE"],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    return done.returncode, log.read_text(encoding="utf-8") if log.exists() else "", done.stderr


def test_the_submission_sequence_waits_out_the_reported_pause_and_keeps_one_batch_queued(tmp_path: Path) -> None:
    refusal = "the last hardware job finished less than 30 s ago; wait 17 more seconds so the platform can calibrate"
    code, calls, err = _submit(tmp_path, [refusal, refusal])
    _expect(code == 0, f"exit {code}: {err}")
    lines = calls.splitlines()
    kinds = [ln.split()[0] for ln in lines]
    _expect(kinds == ["submit", "submit", "submit", "collect", "submit", "collect"], f"{kinds}")
    _expect("sleep 18" in err, f"the wait follows the reported remainder: {err}")


def test_the_submission_sequence_stops_on_the_first_failure_and_after_ten_refusals(tmp_path: Path) -> None:
    code, calls, err = _submit(tmp_path, ["Quantum backend error"])
    _expect(code != 0 and calls.count("submit") == 1 and "collect" not in calls, f"{code} {calls} {err}")
    refusal = "wait 5 more seconds so the platform can calibrate"
    code, calls, err = _submit(tmp_path / "x", [refusal] * 12)
    _expect(code != 0 and calls.count("submit") == 10, f"{code} {calls.count('submit')} {err}")


def test_operating_characteristics_carry_the_band_into_spawned_workers() -> None:
    # 128 series per world exceed parallel.MIN_PARALLEL_ITEMS, so the labels come from spawned workers, which re-import
    # the module with the default band; the band argument must still decide every b0-like comparison.
    draws = 128
    narrow = oc.operating_characteristics(draws=draws, b0_like_z=0.0)
    wide = oc.operating_characteristics(draws=draws, b0_like_z=1e6)
    _expect(all("b0_like" not in shares for shares in narrow.values()), f"band 0 admits no b0-like series: {narrow}")
    _expect(any(shares.get("intermediate", 0.0) > 0 for shares in narrow.values()), "band 0 sends some to intermediate")
    _expect(
        all("intermediate" not in shares for shares in wide.values()),
        f"an unbounded band leaves no intermediate: {wide}",
    )
    _expect(oc.B0_LIKE_Z == 2.0, "the module default band stays 2.0")
