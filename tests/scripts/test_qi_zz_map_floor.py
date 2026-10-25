"""Pause-floor contract of the v2 Tuna ZZ plan on a synthetic three-batch v1 plan."""

from __future__ import annotations

import json
from typing import Any

import pytest
import qi_zz_map as v1
import qi_zz_map_floor as floor


def synthetic_v1(_catalogue: Any = None, _shots: Any = None) -> dict[str, str]:
    batches = [{"directory": f"batch-{n:03d}", "cases_sha256": ""} for n in range(3)]
    files: dict[str, str] = {}
    for batch in batches:
        path = f"{batch['directory']}/cases.json"
        files[path] = v1.json_text({"plan_schema": v1.PLAN_SCHEMA, "source_digests": {}})
        batch["cases_sha256"] = v1.digest(files[path])
    cost = {"batches": 3, "hardware_policy_pause_seconds": floor.CEILING_PAUSE_SECONDS}
    cost["minimum_interbatch_pause_seconds"] = 2 * floor.CEILING_PAUSE_SECONDS
    plan = {"schema": v1.PLAN_SCHEMA, "source_digests": {}, "batches": batches, "cost": cost}
    files["plan.json"] = v1.json_text(plan)
    return files


def test_minimum_is_the_ladder_floor_and_the_ceiling_its_top(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(v1, "build", synthetic_v1)
    files = floor.build()
    cost = json.loads(files["plan.json"])["cost"]
    if cost["minimum_interbatch_pause_seconds"] != 2 * 30 or cost["ceiling_interbatch_pause_seconds"] != 2 * 120:
        raise AssertionError(f"two intervals read {cost}, not a 60 s floor and a 240 s ceiling")
    for name, text in files.items():
        if name.endswith("cases.json") and json.loads(text)["plan_schema"] != floor.PLAN_SCHEMA:
            raise AssertionError(f"{name} keeps the v1 plan schema")


def test_a_ceiling_valued_minimum_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(v1, "build", synthetic_v1)
    files = floor.build()
    plan = json.loads(files["plan.json"])
    plan["cost"]["minimum_interbatch_pause_seconds"] = plan["cost"]["ceiling_interbatch_pause_seconds"]
    with pytest.raises(ValueError, match="ladder floor"):
        floor.validate_plan(plan, files)
