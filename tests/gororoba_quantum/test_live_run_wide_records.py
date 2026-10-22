"""A 15-clbit segmented sweep on FakeFez records its ideal and noisy laws and its score values in their short exact
forms, and the approved-record comparison accepts that record for the unchanged plan and refuses it after a
one-entry edit of one member's law.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

import diagnostic_experiments
import law_encoding
import live_run
import qpu_planning
import qpu_planning_contracts as contracts_fixture

WIDE_SWEEP = contracts_fixture.SEGMENTED_SWEEP | {"delays_dt": [0, 693], "segments": 6}


@pytest.fixture(scope="module")
def planned() -> tuple[Any, dict[str, Any]]:
    with (
        patch.object(live_run, "QiskitRuntimeService", contracts_fixture._forbid_service),
        patch.object(live_run, "configure_sampler", contracts_fixture._forbid_service),
    ):
        _service, snapshot = contracts_fixture._fixture()
        pin = {"backend": snapshot.name, "qubits": contracts_fixture.PINNED_ORBIT_LAYOUT}
        arguments = contracts_fixture._args(
            "n21-orbit-rca", pin_layout=pin, ground_control_split=True, init_herald=True, segmented_sweep=WIDE_SWEEP
        )
        candidates = qpu_planning.family_candidates(live_run, [snapshot], arguments, {})
    if not candidates:
        raise AssertionError("FakeFez refuses the 15-clbit segmented sweep")
    (choice,), configuration = candidates[0]
    return choice, configuration


def approved_record(choice: Any) -> dict[str, Any]:
    noisy = {entry.name: [entry.ideal for _ in entry.replicas] for entry in choice.entries}
    group = live_run._choice_record(choice, noisy, "fixture", 1536) | live_run.choice_calibration_values(choice)
    pubs = [pub.manifest() for pub in live_run.execution_pubs([choice])]
    return {"groups": [live_run._json_value(group)], "execution_pubs": live_run._json_value(pubs)}


def test_wide_laws_take_their_support(planned: tuple[Any, dict[str, Any]]) -> None:
    choice, _configuration = planned
    record = approved_record(choice)
    for member, entry in zip(record["groups"][0]["members"], choice.entries, strict=True):
        if len(entry.ideal) != 1 << 15 or member["ideal"]["encoding"] != "support":
            raise AssertionError(f"{entry.name} stores {type(member['ideal']).__name__}")
        if law_encoding.dense(member["ideal"]) != [round(float(p), 12) for p in entry.ideal]:
            raise AssertionError(f"{entry.name}: the stored law expands to another law")
    if len(json.dumps(record)) > 1_000_000:
        raise AssertionError(f"the group record takes {len(json.dumps(record))} bytes")


def test_score_values_take_a_bit_table(planned: tuple[Any, dict[str, Any]]) -> None:
    _choice, configuration = planned
    contracts = diagnostic_experiments.family_contracts("n21-orbit-rca", 0.08, 0.05, 0.8, configuration=configuration)
    records = qpu_planning.observable_contract_records(contracts)
    for contract, stored in zip(contracts, records, strict=True):
        for term, kept in zip(contract.terms, stored["terms"], strict=True):
            if kept["values"]["encoding"] != "bits" or len(kept["values"]["table"]) != 2:
                raise AssertionError(f"{contract.name}: {kept['values']}")
            if tuple(law_encoding.dense(kept["values"])) != tuple(term.values):
                raise AssertionError(f"{contract.name}: the stored score expands to another score")


def test_comparison_accepts_the_plan_and_refuses_an_edit(planned: tuple[Any, dict[str, Any]], tmp_path: Path) -> None:
    choice, _configuration = planned
    (tmp_path / "isa.qpy").write_bytes(live_run.archive_bytes([choice]))
    record = approved_record(choice)
    if live_run.approved_choice_blockers(tmp_path, record, [choice]):
        raise AssertionError(live_run.approved_choice_blockers(tmp_path, record, [choice]))
    support = record["groups"][0]["members"][0]["ideal"]["support"]
    key = next(iter(support))
    support[key] = round(support[key] - 1e-6, 12)
    blockers = live_run.approved_choice_blockers(tmp_path, record, [choice])
    if not any("compiled members" in blocker for blocker in blockers):
        raise AssertionError(f"a one-entry law edit passed: {blockers}")
