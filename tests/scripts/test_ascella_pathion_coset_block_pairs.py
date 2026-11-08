"""Check the two-coset-block Ascella case against cd_core, the pair law and its packing budget."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import ascella_pathion_coset_block_pairs as case
import numpy as np

from parallel import ordered_map

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "results/quandela/cases/ascella_pathion_coset_block_pairs"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def test_sequence_is_a_palindrome_and_each_sign_setting_runs_in_both_slot_orientations() -> None:
    entries = case.sequence()
    case.check_sequence(entries)
    require(case.ITERATIONS == 52 and len(entries) == 52, f"{case.ITERATIONS} iterations")
    require(case.SEED_COUNT == 25, f"{case.SEED_COUNT} seeds")
    names = [design.name for design, _ in entries]
    require(names[0] == names[-1] == "anchor" and names[2] == names[-3] == "dark", "anchor and dark frame the job")
    require(names[25] == names[26] == "b-f-EE", "the null sits at the palindrome center")
    require(entries[-1] == entries[0] and entries[-2] == entries[1], "anchor requests repeat unchanged at the mirror")


def test_every_block_carries_its_arms_and_every_same_class_pair_and_group_is_present() -> None:
    coverage = case.check_coverage()
    for code in case.SIGN_BLOCKS:
        require({"T", "F", "N"} <= set(coverage[code]), f"block {code}: {coverage[code]}")
        require(("C" in coverage[code]) == (code != "c"), f"block {code}: cocycle-free arm {coverage[code]}")


def test_job_fits_the_packing_margin_inside_the_measured_shot_range() -> None:
    require(case.SHOTS <= case.MEASURED_MAX_SHOTS, "shots per iteration exceed the retained range")
    require(math.isclose(case.check_duration(), 52 * 3.2), f"expected seconds {case.check_duration()}")
    require(case.SHOTS / case.THROUGHPUT_BOUND < case.SECONDS_PER_ITERATION, "the throughput bound binds")


def test_binomial_error_of_a_fold_level_uses_the_twice_share_variance() -> None:
    errors = case.standard_errors()
    top = errors["L=0.75 two iterations"]
    require(math.isclose(top, math.sqrt(0.75 * 1.25 / (2 * case.SAMPLES))), "variance L (2 - L) / n")
    require(top < 0.002, f"pooled error {top} against the predecessor's 0.0017 to 0.0019")


def test_contrast_power_separates_the_predecessor_spread_from_no_spread() -> None:
    contrast = case.predecessor_record()["c8_contrast"]
    require(math.isclose(contrast, 0.0470, abs_tol=2e-4), f"predecessor contrast {contrast}")
    quiet = case.contrast_power(contrast, 0.01)
    require(quiet["reproduced_when_present"] > 0.95 and quiet["reproduced_when_absent"] < 0.05, f"{quiet}")
    noisy = case.contrast_power(contrast, 0.02)
    require(noisy["reproduced_when_present"] < quiet["reproduced_when_present"], "power falls with mesh spread")


def test_every_arm_item_matches_the_cd_core_product_and_separates_its_mutation() -> None:
    for design in case.DESIGNS:
        for code, arm in (design.first, design.second):
            item = case.resolve(code, arm)
            if arm in ("F", "C", "N"):
                require(abs(item.level - item.true_top_level) >= case.SEPARATION, f"{code} {arm}: separation")
            if arm == "D":
                require(abs(item.level) < 1e-12, f"{code}: kernel level {item.level}")
            if arm in ("E0", "E1"):
                require(math.isclose(item.level, 0.25, abs_tol=1e-12), f"{code} {arm}: null level {item.level}")
    for code, level in (("b", 0.75), ("f", (3 + math.sqrt(5)) / 8), ("p", 1.0)):
        item = case.resolve(code, "T")
        require(math.isclose(item.level, level, abs_tol=1e-12), f"{code}: top level {item.level}")


def build(arguments: tuple[str, int, str, str, str, str, str]) -> dict[str, object]:
    name, orientation, role, code_x, arm_x, code_y, arm_y = arguments
    return case.build_iteration((0, name, orientation, 0, 0, role, code_x, arm_x, code_y, arm_y, ""))


def test_pair_law_equals_slos_keeps_the_sentinels_empty_and_moves_items_with_the_slot() -> None:
    specs = [
        ("t", 0, "sign", "i", "T", "f", "T"),
        ("t", 1, "sign", "i", "T", "f", "T"),
        ("a", 0, "anchor", "p", "T", "q", "D"),
        ("d", 0, "dark", "p", "D", "q", "D"),
        ("m", 0, "sign", "b", "C", "i", "N"),
        ("e", 1, "null", "b", "E0", "f", "E1"),
    ]
    built = ordered_map(build, specs, min_items=1)
    for setting in built:
        law = np.array(setting["ideal_label_law"])
        column = np.array([complex(re, im) for re, im in setting["column"]])
        require(float(np.max(np.abs(law - np.abs(column[: case.ACTIVE]) ** 2))) < 1e-9, "law differs from column")
        require(float(np.max(np.abs(column[case.ACTIVE :]))) == 0.0, "a sentinel mode carries amplitude")
        slots = setting["slots"]
        levels = setting["ideal_levels"]
        require(math.isclose(2 * float(law[:4].sum()), slots["A"]["ideal_level"], abs_tol=1e-9), "slot A level")
        require(math.isclose(2 * float(law[4:8].sum()), slots["B"]["ideal_level"], abs_tol=1e-9), "slot B level")
        require(math.isclose(float(law.sum()), 1.0, abs_tol=1e-9), "law is not normalized")
        require(levels == [slots["A"]["ideal_level"], slots["B"]["ideal_level"]], "levels differ from slots")
    straight, swapped = built[0], built[1]
    require(straight["slots"]["A"]["code"] == swapped["slots"]["B"]["code"] == "i", "swap moves item 0")
    anchor = built[2]
    require(math.isclose(anchor["ideal_failure"], 0.5, abs_tol=1e-9), "anchor failure share")
    dark = built[3]
    require(math.isclose(dark["ideal_label_law"][case.FAILURE_MODE], 1.0, abs_tol=1e-9), "dark failure share")
    null = built[5]
    require(math.isclose(null["ideal_failure"], 0.75, abs_tol=1e-9), "null failure share")


def test_frozen_requests_match_each_other_the_draw_and_the_script_digests() -> None:
    sim = json.loads((CASES / "sim-00/cases.json").read_text(encoding="utf-8"))
    qpu = json.loads((CASES / "job-00/cases.json").read_text(encoding="utf-8"))
    require(sim["platforms"] == ["sim:ascella"] and qpu["platforms"] == ["qpu:ascella"], "platforms")
    differing = {key for key in sim if sim[key] != qpu[key]}
    require(differing == {"job", "platforms"}, f"manifests differ in {sorted(differing)}")
    require(qpu["iterations"] == case.ITERATIONS and qpu["max_shots"] == case.SHOTS * case.ITERATIONS, "budget")
    sources = qpu["seed_source"]["sources"]
    require(len(sources) == case.SEED_COUNT and len({s.split("#")[0] for s in sources}) == 1, "one draw")
    draw = json.loads((ROOT / sources[0].split(":")[1].split("#")[0]).read_text(encoding="utf-8"))["values"]
    for setting in qpu["settings"]:
        require(setting["compilation_seed"] == draw[setting["seed_index"]], f"{setting['name']}: seed")
    # The bound source bytes live at the pinned revision; scripts/frozen_case_sources.py --check (on-demand gate
    # core-ascella-predecessor-source-pin) proves them, so main's shared copies may move past the freeze.
    require(
        set(qpu["analysis_sources"]) >= {"scripts/ascella_pathion_coset_block_pairs.py", "scripts/qd_platform.py"},
        "analysis sources",
    )
    pins = json.loads((ROOT / "docs/evidence/quandela/frozen-case-source-pins.json").read_text(encoding="utf-8"))
    pinned = {row["case"] for row in pins["cases"]}
    for kind in ("sim-00", "job-00"):
        require(f"results/quandela/cases/ascella_pathion_coset_block_pairs/{kind}/cases.json" in pinned, f"{kind} pin")
    require(
        hashlib.sha256((CASES / "job-00/circuit.json").read_bytes()).hexdigest() == qpu["circuit"]["sha256"],
        "circuit digest",
    )
