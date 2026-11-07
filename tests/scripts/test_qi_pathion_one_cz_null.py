"""Contracts of the low-CZ null-block case: the b0 replay, the role-map pins, the block laws, the series, the joint
readout statistics and the preregistered decisions.

Each test compiles only the committed SELECTION, never the 120-layout search (`--select` repeats that on demand).
Collected-run fixtures hold expected counts (largest remainder, no random draw) in qi_platform.collect's layout.
"""

from __future__ import annotations

import json
import re
import shutil
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


# Series, joint readout and decisions ------------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "results/quantum_inspire/cases"
LOG = ROOT / "docs/evidence/pathion-kernel-map/conjectures/c2_one_cz_mech.txt"


@pytest.fixture(scope="module")
def built() -> dict[str, dict[str, str]]:
    return oc.build()


@pytest.fixture(scope="module")
def worlds(built: dict[str, dict[str, str]]) -> dict[str, dict[str, list[str]]]:
    files = built[oc.TUNA_SERIES]
    manifest = json.loads(files["batch-00/cases.json"])
    return {w: oc.synthetic_series(files, oc.series_plan(), manifest, **kw) for w, kw in oc.WORLDS.items()}


def test_the_committed_case_directory_reproduces_its_bytes() -> None:
    oc.check(CASES)
    _expect(
        (CASES / oc.TUNA_SERIES / "batch-03" / "b0.cq").read_bytes() == (oc.COIN_BATCH / "b0.cq").read_bytes(), "b0"
    )


def test_the_series_holds_twenty_jobs_in_seven_batches_within_the_platform_limits(
    built: dict[str, dict[str, str]],
) -> None:
    files = built[oc.TUNA_SERIES]
    series = json.loads(files["cases.json"])
    _expect([len(b["files"]) for b in series["batches"]] == [3, 3, 2, 3, 3, 3, 3], "batch sizes")
    shots = []
    for batch in series["batches"]:
        manifest = json.loads(files[f"{batch['batch']}/cases.json"])
        _expect(manifest["shots"] <= 131072 and manifest["register"] == [2, 4, 8, 11, 12], "limits")
        shots.append(manifest["shots"])
    _expect(shots == [32768] * 3 + [65536] * 4, f"shots {shots}")
    qx = json.loads(built[oc.QX_SERIES]["cases.json"])
    _expect([len(b["files"]) for b in qx["batches"]] == [4], "the QX control holds every template in one batch")
    _expect(json.loads(built[oc.QX_SERIES]["batch-00/cases.json"])["shots"] == oc.QX_SHOTS, "QX shots")


def test_the_joint_circuits_prepare_every_basis_state_of_the_coin_the_selector_and_q12_with_x_gates_only(
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
        _expect(text.rstrip().endswith("b = measure q"), f"{rel}: measures all qubits")
    _expect(seen == set(oc.JOINT_PREPS), f"preparations {sorted(seen)}")


def test_the_series_templates_share_the_selector_and_coin_qubits_and_the_blocks_route_to_six_cz(
    built: dict[str, dict[str, str]],
) -> None:
    templates = json.loads(built[oc.TUNA_SERIES]["batch-03/cases.json"])["templates"]
    ref = oc.reference()["roles"]
    for name, t in templates.items():
        _expect(t["roles"]["selector"] == ref["selector"] and t["roles"]["coin"] == ref["coin"], f"{name}: roles")
    _expect([templates[n]["cz"] for n in oc.TEMPLATES] == [21, 6, 6, 6], "CZ counts")
    _expect(templates["b0"]["roles"] == ref, "b0 keeps its retained role map")


def _selector_log() -> dict[str, dict[str, float]]:
    sections: dict[str, dict[str, float]] = {}
    name = ""
    for line in LOG.read_text(encoding="utf-8").splitlines():
        head = re.match(r"^(\S+)  \(cz", line)
        if head:
            name = head.group(1)
            sections[name] = {}
        elif name and "selector contrast" in line:
            value = float(re.search(r"selector contrast ([+-]\d\.\d+)", line).group(1))  # type: ignore[union-attr]
            sections[name][line.strip().split("  ")[0]] = value
    return sections


def test_the_predicted_contrasts_equal_the_simulation_log() -> None:
    log = _selector_log()
    over, dropout = "X90 over-rotation +0.03", "selector readout, dropout on q8 when q2 = 1, x 0.0362"
    expected = oc.PREDICTED
    _expect(abs(log["b0"][over] - expected["over_rotation"]["b0"]) < 6e-5, "b0 over-rotation")
    _expect(abs(log["b0"][dropout] - expected["coin_dropout"]["b0"]) < 6e-5, "b0 dropout")
    for block in ("k4_sc", "k8_sc", "k12_sc"):
        _expect(abs(log[block][over] - expected["over_rotation"]["six_cz"]) < 6e-5, f"{block} over-rotation")
        _expect(abs(log[block][dropout] - expected["coin_dropout"]["six_cz"]) < 6e-5, f"{block} dropout")


def test_the_design_sizes_the_series_from_the_coin_series_timings() -> None:
    plan = json.loads((CASES / oc.TUNA_SERIES / "prediction.json").read_text(encoding="utf-8"))["design"]
    _expect(plan["jobs"] == 20 and plan["batches"] == 7 and plan["shots_total"] == 1048576, f"{plan}")
    _expect(abs(plan["selector_se"] - 1 / 256) < 1e-12, "selector se")
    for value in plan["model_size_in_se"].values():
        _expect(value >= 3.0, f"the 0.036 model reads {value} se")
    low, high = plan["execution_seconds_range"]
    _expect(500 < low < high < 700, f"seconds {plan['execution_seconds_range']}")


@pytest.mark.parametrize("world", list(oc.WORLDS))
def test_each_simulated_world_reads_its_preregistered_outcome(
    world: str, built: dict[str, dict[str, str]], worlds: dict[str, dict[str, list[str]]]
) -> None:
    manifest = json.loads(built[oc.TUNA_SERIES]["batch-00/cases.json"])
    result = oc.evaluate(worlds[world], manifest)
    _expect(result["decision"]["outcome"].startswith(oc.WORLD_OUTCOMES[world]), f"{world}: {result['decision']}")
    json.dumps(result, allow_nan=False)


def test_the_joint_statistics_recover_the_injected_readout_effects(
    built: dict[str, dict[str, str]], worlds: dict[str, dict[str, list[str]]]
) -> None:
    manifest = json.loads(built[oc.TUNA_SERIES]["batch-00/cases.json"])
    e10 = 0.06  # the synthetic assignment of q8 (register index 2): (0.04, 0.06)
    coin = oc.joint_statistics(worlds["coin_dropout"], manifest)["coin_dropout"]
    _expect(abs(coin["D"]["value"] - 0.0362 * (1 - e10)) < 2e-4, f"D {coin['D']}")
    _expect(abs(coin["by_selector"]["selector_prepared_0"]["value"]) < 1e-4, "no dropout of a prepared 0")
    q12 = oc.joint_statistics(worlds["q12_correlation"], manifest)["q12_correlation"]["G_by_selector"]
    for s, rate in (("selector_prepared_0", 0.04), ("selector_prepared_1", 0.06)):
        want = 0.036 * (1 - 2 * rate)
        _expect(abs(q12[s]["value"] - want) < 2e-4, f"G {s}: {q12[s]['value']} against {want}")
    clean = oc.joint_statistics(worlds["absent"], manifest)
    _expect(abs(clean["coin_dropout"]["D"]["value"]) < 1e-4, "clean device reads D = 0")
    with pytest.raises(ValueError, match="not all eight"):
        oc.joint_statistics({k: v for k, v in worlds["absent"].items() if "joint-111" not in k}, manifest)


def test_every_preregistered_row_decides_and_every_other_combination_is_unresolved() -> None:
    for (six, coin, q12), (outcome, effect) in oc.DECISIONS.items():
        got = oc.decide(True, True, six, coin, q12)
        _expect(got["outcome"] == outcome and got["a5_186"] == effect and got["decided"], f"{six} {coin} {q12}")
    for six in ("zero", "b0-like", "unresolved"):
        for coin in ("large", "small", "mid"):
            for q12 in ("large", "small", "mid"):
                got = oc.decide(True, True, six, coin, q12)
                _expect(got["decided"] == ((six, coin, q12) in oc.DECISIONS), f"{six} {coin} {q12}")
                if not got["decided"]:
                    _expect(got["outcome"].startswith("unresolved"), f"{six} {coin} {q12}: {got['outcome']}")
                    _expect(got["a5_186"].startswith("unchanged"), "an unresolved row leaves A5-186 unchanged")
    absent = oc.decide(False, True, "zero", "small", "small")
    _expect(absent["outcome"].startswith("offset absent") and absent["a5_186"] == "unchanged", f"{absent}")
    _expect(not absent["decided"], "an absent offset decides nothing")
    coarse = oc.decide(True, False, "zero", "small", "small")
    _expect(coarse["outcome"].startswith("uninformative") and not coarse["decided"], f"{coarse}")


def test_the_classes_read_the_preregistered_thresholds() -> None:
    _expect(oc.classify_large(0.036, 0.002) and not oc.classify_large(0.02, 0.002), "large threshold")
    _expect(oc.classify_large(0.031, 0.002) and not oc.classify_large(0.0, 0.002), "large with se")
    _expect(oc.classify_small([(0.0, 0.002), (0.004, 0.0015)]) and not oc.classify_small([(0.01, 0.002)]), "small")
    six = oc.six_cz_class({"k4": (0.001, 0.004), "k8": (-0.001, 0.004), "k12": (0.0, 0.004)}, (0.0164, 0.0039))
    _expect(six["class"] == "zero", f"{six}")
    like = oc.six_cz_class({"k4": (0.017, 0.004), "k8": (0.015, 0.004), "k12": (0.016, 0.004)}, (0.0164, 0.0039))
    _expect(like["class"] == "b0-like", f"{like}")
    between = oc.six_cz_class({"k4": (0.005, 0.004), "k8": (0.005, 0.004), "k12": (0.005, 0.004)}, (0.0164, 0.0039))
    _expect(between["class"] == "unresolved", f"{between}")


def test_a_coarser_standard_error_than_the_limit_is_uninformative(
    built: dict[str, dict[str, str]], worlds: dict[str, dict[str, list[str]]], monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest = json.loads(built[oc.TUNA_SERIES]["batch-00/cases.json"])
    monkeypatch.setattr(oc, "JOINT_SE_LIMIT", 1e-4)
    result = oc.evaluate(worlds["over_rotation"], manifest)
    _expect(
        not result["decision"]["informative"] and result["decision"]["outcome"].startswith("uninformative"), "joint"
    )
    monkeypatch.undo()
    monkeypatch.setattr(oc, "SELECTOR_SE_LIMIT", 1e-4)
    result = oc.evaluate(worlds["over_rotation"], manifest)
    _expect(not result["decision"]["informative"], "selector")


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
    _expect(result["decision"]["outcome"].startswith("over-rotation supported"), f"{result['decision']}")
    _expect(result["control"]["positive_at_3_se"] and result["classes"]["six_cz"] == "zero", f"{result['classes']}")
    _expect(not result["drift_covariate"]["references"]["flagged"], "drift")
    partial = oc.analyze(dirs[:3], tmp_path / "cases")
    _expect(not partial["complete"] and partial["batches"] == ["batch-00", "batch-01", "batch-02"], f"{partial}")
    sanity = oc.sanity(dirs[3:], tmp_path / "cases")
    _expect(sanity["batches"] == ["batch-03", "batch-04", "batch-05", "batch-06"] and sanity["drift"], "sanity")
    with pytest.raises((ValueError, SystemExit), match="differs from"):
        shutil.copy(dirs[4] / "k4.cq", dirs[3] / "b0.cq")
        oc.analyze(dirs, tmp_path / "cases")


def _qx_shots(files: dict[str, str], uniform: str | None = None) -> dict[str, list[str]]:
    manifest = json.loads(files["batch-00/cases.json"])
    out: dict[str, list[str]] = {}
    for row in manifest["circuits"]:
        ideal = [1.0 / oc.NOUT] * oc.NOUT if row["template"] == uniform else row["ideal"]
        roles = manifest["templates"][row["template"]]["roles"]
        counts = oc.cc.largest_remainder(np.array(ideal), manifest["shots"])
        out[f"batch-00/{row['file']}"] = oc.cc.place_counts(counts, oc.KEYS, roles, manifest["nqubits"])
    return out


def test_the_qx_control_passes_on_the_ideal_laws_and_fails_on_a_wrong_circuit(
    tmp_path: Path, built: dict[str, dict[str, str]]
) -> None:
    files = built[oc.QX_SERIES]
    good = oc.analyze(_runs(tmp_path / "g", oc.QX_SERIES, files, _qx_shots(files)), tmp_path / "g" / "cases")
    _expect(good["claim_kind"] == oc.CONTROL_KIND and good["qx_control"]["pass"], f"{good['qx_control']}")
    wrong = _qx_shots(files, uniform="k4")
    bad = oc.analyze(_runs(tmp_path / "w", oc.QX_SERIES, files, wrong), tmp_path / "w" / "cases")
    _expect(not bad["qx_control"]["pass"], "a uniform law in the k4 slot passed")
