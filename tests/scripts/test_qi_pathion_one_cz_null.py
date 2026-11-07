"""Contracts of the low-CZ null-block routing: the b0 replay, the role-map pins and the block laws.

Each test compiles only the committed SELECTION, never the 120-layout search (`--select` repeats that on demand).
"""

from __future__ import annotations

import numpy as np
import pytest
import qi_pathion_coset_coin_cases as cc
import qi_pathion_one_cz_null_cases as oc

import pathion_coset_block as pcb


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
