"""The QX twin builder and the map analyzer read Tuna ZZ plan schema v2 beside v1."""

import json
from pathlib import Path

import pytest
import qi_zz_map_analysis as analysis
import qi_zz_map_qx as qx
import qi_zz_map_qx_plans as plans


def test_v2_plan_builds_a_qx_twin_the_retained_builder_refuses(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unrecognized Tuna plan"):
        qx.build(plans.V2_SOURCE, catalogue=plans.DEADLINE_CATALOGUE)
    files = plans.build(plans.V2_SOURCE, catalogue=plans.DEADLINE_CATALOGUE)
    plans.write(tmp_path, files)
    plans.check(tmp_path, files)
    plan = json.loads(files["plan.json"])
    if plan["schema"] != qx.PLAN_SCHEMA or plan["sanity_policy"] != qx.POLICY:
        raise AssertionError("the v2 twin left the plan schema qi_zz_map_qx --analyze reads")
    if plan["source_tuna_plan_schema"] != "qi-zz-map-plan-v2" or len(plan["batches"]) != 139:
        raise AssertionError("the v2 twin lost its source schema or batching")


def test_qi_zz_map_qx_plans_self_test() -> None:
    plans.self_test()


@pytest.mark.parametrize("source", [plans.V1_SOURCE, plans.V2_SOURCE])
def test_analyzer_accepts_both_plan_schemas_up_to_the_acquisition(source: Path, tmp_path: Path) -> None:
    # Every plan-level check passes; the first missing input is the unacquired batch manifest.
    with pytest.raises(FileNotFoundError, match="batch-000"):
        analysis.read_complete_plan(source, tmp_path)


def test_analyzer_refuses_an_unknown_plan_schema(tmp_path: Path) -> None:
    plan = json.loads(plans.V2_SOURCE.read_bytes())
    plan["schema"] = "qi-zz-map-plan-v3"
    path = tmp_path / "plan.json"
    path.write_text(json.dumps(plan), encoding="utf-8")
    with pytest.raises(ValueError, match="unrecognized map plan"):
        analysis.read_complete_plan(path, tmp_path)
