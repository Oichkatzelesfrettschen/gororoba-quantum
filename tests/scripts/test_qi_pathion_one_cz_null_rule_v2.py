"""Contracts of twin-control rule v2 of the Tuna-17 one-CZ null series and of the twin batch layout it reads.

The audit-marked test regenerates the stored operating characteristics (two simulations of 20,000 series per world
under the successor decision); the other tests read the stored record or build hand-made estimates.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pytest
import qi_pathion_one_cz_null_analysis as ana
import qi_pathion_one_cz_null_cases as oc
import qi_pathion_one_cz_null_rule_v2 as rule

ROOT = Path(__file__).resolve().parents[2]
PREDICTION = ROOT / "results/quantum_inspire/cases/pathion_one_cz_null_tuna_17/prediction.json"
SE_TWIN = math.sqrt(0.5 / oc.BATCH_SHOTS)
# Pooled standard error of b0's twin contrast over its two replicate batches.
SE_T0 = SE_TWIN / math.sqrt(oc.REPLICATES)
PLATFORM_CIRCUITS_PER_BATCH = 3


def _expect(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _rows(
    base: dict[str, float] | None = None, twin: dict[str, float] | None = None
) -> dict[str, dict[str, list[tuple[float, float]]]]:
    """Batch estimates (two replicates each) from per-template base and twin values at the design errors."""
    base, twin = base or {}, twin or {}
    se_base = {t: 1 / math.sqrt(oc.CONTROL_SHOTS if t == "b0" else oc.BATCH_SHOTS) for t in oc.TEMPLATES}
    return {
        t: {
            "base": [(base.get(t, 0.0), se_base[t])] * oc.REPLICATES,
            "twin": [(twin.get(t, 0.0), SE_TWIN)] * oc.REPLICATES,
        }
        for t in oc.TEMPLATES
    }


def _zero_block(s_b0: float, t_b0: float) -> dict[str, dict[str, list[tuple[float, float]]]]:
    return _rows(base={"b0": s_b0}, twin={"b0": t_b0})


def test_a_negative_twin_is_superposition_only_under_the_preregistered_rule_and_unresolved_under_rule_v2() -> None:
    rows = _zero_block(0.0164, -0.0164)
    old = oc.decide_estimates(rows)
    _expect(
        old["label"] == "superposition_only" and old["decided"], f"the preregistered rule: {old['numbers']['t_b0']}"
    )
    new = rule.decide_estimates(rows)
    _expect(new["label"] == rule.NEGATIVE_TWIN and not new["decided"], f"{new['label']}")
    _expect(new["outcome"] == rule.OUTCOMES[rule.NEGATIVE_TWIN][0], "the outcome text follows the label")
    _expect(new["numbers"] == ana.decide_estimates(rows)["numbers"], "the numbers are those of the v3 decision")


def test_the_superposition_only_row_needs_t0_within_three_standard_errors_of_zero() -> None:
    bound = oc.Z_RESOLVE * SE_T0
    for t0, label in (
        (0.0, "superposition_only"),
        (0.999 * bound, "superposition_only"),
        (-0.999 * bound, "superposition_only"),
        (-1.001 * bound, rule.NEGATIVE_TWIN),
    ):
        got = rule.decide_estimates(_zero_block(0.04, t0))["label"]
        _expect(got == label, f"t0 {t0 / SE_T0:+.3f} se reads {got}, not {label}")


def test_rule_v2_differs_from_the_preregistered_rule_only_on_a_superposition_only_reading_with_a_negative_twin() -> (
    None
):
    differing = 0
    for s0 in (0.0, 0.01, 0.0164, 0.04):
        for t0 in np.linspace(-0.04, 0.04, 81):
            for six in (0.0, 0.0164):
                rows = _rows(
                    base={"b0": s0, **{t: six for t in oc.LOW_NAMES}},
                    twin={"b0": float(t0), **{t: six for t in oc.LOW_NAMES}},
                )
                old, new = oc.decide_estimates(rows), rule.decide_estimates(rows)
                if old["label"] == new["label"]:
                    continue
                differing += 1
                _expect(old["label"] == "superposition_only" and new["label"] == rule.NEGATIVE_TWIN, f"{old['label']}")
                _expect(float(t0) < -oc.Z_RESOLVE * SE_T0, f"t0 {t0}")
    _expect(differing > 0, "the grid reaches the negative-twin region")


def test_every_v2_outcome_row_exists_and_only_the_inherited_rows_decide() -> None:
    _expect(set(rule.OUTCOMES) == set(oc.OUTCOMES) | {rule.NEGATIVE_TWIN}, "one new row")
    _expect(all(rule.OUTCOMES[k] == v for k, v in oc.OUTCOMES.items()), "the inherited rows are unchanged")
    _expect(
        rule.NEGATIVE_TWIN not in oc.DECIDING and rule.OUTCOMES[rule.NEGATIVE_TWIN][1].startswith("unchanged"), "row"
    )


def test_the_successor_decision_reaches_spawned_workers() -> None:
    # 128 series exceed parallel.MIN_PARALLEL_ITEMS, so the labels come from spawned workers that unpickle the rule.
    world = {rule.NEGATIVE_TWIN_WORLD: rule.NEGATIVE_TWIN_MEAN}
    successor = oc.operating_characteristics(draws=128, worlds=world, decide=rule.decide_estimates)
    _expect(successor[rule.NEGATIVE_TWIN_WORLD].get(rule.NEGATIVE_TWIN, 0.0) >= 0.8, f"{successor}")
    preregistered = oc.operating_characteristics(draws=128, worlds=world)
    _expect(preregistered[rule.NEGATIVE_TWIN_WORLD].get("superposition_only", 0.0) >= 0.8, f"{preregistered}")


def test_a_successor_decision_that_cannot_pickle_is_refused_before_any_draw() -> None:
    # ana.decide_estimates is a rebound copy: its name resolves to the predecessor's function, not to itself.
    with pytest.raises(ValueError, match="pickle by reference"):
        oc.operating_characteristics(draws=64, decide=ana.decide_estimates)


def _stored() -> dict[str, Any]:
    stored: dict[str, Any] = json.loads((ROOT / rule.RECORD).read_text(encoding="utf-8"))
    return stored


def test_the_stored_table_repeats_the_preregistered_one_and_adds_the_negative_twin_row() -> None:
    old = json.loads(PREDICTION.read_text(encoding="utf-8"))["operating_characteristics"]
    new = _stored()["operating_characteristics"]
    _expect(new["qrng_draw"] == old["qrng_draw"] and new["seed_index"] == old["seed_index"], "the seed is the case's")
    for table in ("stationary", "batch_drift_sd_0.003"):
        _expect(list(new[table])[: len(old[table])] == list(old[table]), "the inherited worlds draw first, in order")
        for world, shares in old[table].items():
            got = new[table][world]
            moved = {k for k in got.keys() | shares.keys() if got.get(k, 0.0) != shares.get(k, 0.0)}
            _expect(moved <= {"superposition_only", rule.NEGATIVE_TWIN}, f"{table} {world}: {sorted(moved)}")
            _expect(
                abs(
                    got.get("superposition_only", 0.0)
                    + got.get(rule.NEGATIVE_TWIN, 0.0)
                    - shares.get("superposition_only", 0.0)
                )
                < 2e-4,  # each stored share is rounded to four decimals
                f"{table} {world}: the negative-twin share comes out of the superposition-only share",
            )
    for table, floor in (("stationary", 0.95), ("batch_drift_sd_0.003", 0.8)):
        row = new[table][rule.NEGATIVE_TWIN_WORLD]
        _expect(row[rule.NEGATIVE_TWIN] >= floor and row.get("superposition_only", 0.0) < 0.02, f"{table}: {row}")
    _expect(
        not {"zero", "b0_like"} & new["stationary"][rule.NEGATIVE_TWIN_WORLD].keys(),
        "a negative twin decides no mechanism",
    )


@pytest.mark.audit
def test_the_stored_rule_v2_record_replays_its_bytes() -> None:
    _expect(rule.record_text() == (ROOT / rule.RECORD).read_text(encoding="utf-8"), "the record differs")


def test_twin_batches_hold_one_readout_reference_and_both_coin_twins() -> None:
    """The submitted layout reads each twin contrast inside one batch against one end of the readout bracket.

    A batch holds at most three circuits, so bracketing a twin pair (two twins and two readouts) needs four: the
    pair shares a batch against one readout, or a bracketed twin runs in a batch of its own."""
    rows = {row["batch"]: row for row in oc.batch_rows(oc.TUNA_SERIES)}
    twins = [r for r in rows.values() if r["kind"] == "twin"]
    _expect(len(twins) == 8, f"{len(twins)} twin batches")
    for row in twins:
        files = [c["file"] for c in row["circuits"]]
        readouts = [f for f in files if f.startswith("readout")]
        _expect(len(files) == PLATFORM_CIRCUITS_PER_BATCH and len(readouts) == 1, f"{row['batch']}: {files}")
        _expect(readouts == [f"readout-{row['replicate']}.cq"], f"{row['batch']} holds {readouts}")
        _expect({c["coin"] for c in row["circuits"] if c["kind"] == "data"} == {0, 1}, f"{row['batch']} coins")
    for row in (r for r in rows.values() if r["kind"] == "base"):
        files = [c["file"] for c in row["circuits"]]
        _expect(files[0] == "readout-0.cq" and files[-1] == "readout-1.cq", f"{row['batch']} is bracketed")
