"""Readiness and retained acquisitions reject topology and payload substitutions."""

import json
import math
import shutil
from pathlib import Path

import pytest
import qd_platform as qd


@pytest.mark.parametrize("changed", ["mode", "order"])
def test_native_readiness_rejects_phase_topology_change(changed: str) -> None:
    import perceval as pcvl

    circuit = {
        "architecture": {"symbols": ["phi0"], "couplers": [[0, math.pi / 2]]},
        "ops": [["BS", 0, 0], ["PS", 1, 1]],
    }
    live = pcvl.Circuit(2)
    if changed == "order":
        live.add(1, pcvl.PS(pcvl.P("phi0")))
    live.add(0, pcvl.BS.Rx(theta=math.pi / 2))
    if changed == "mode":
        live.add(0, pcvl.PS(pcvl.P("phi0")))
    processor = {"specs": {"architecture": pcvl.serialization.serialize(live)}}
    with pytest.raises(qd.PlatformError, match="architecture"):
        qd.live_mesh(processor, circuit, "qpu:ascella")


@pytest.mark.parametrize("mutation", ["value", "missing", "extra"])
def test_retained_repeat_rejects_changed_returned_payload(tmp_path: Path, mutation: str) -> None:
    root = Path(__file__).resolve().parents[2]
    source = root / "results/quandela/runs/belenos-order-repeat-block-0"
    directory = tmp_path / source.name
    shutil.copytree(source, directory)
    path = directory / "results.json"
    record = json.loads(path.read_text())
    if mutation == "value":
        record["data"]["payload"]["max_samples"] += 1
    elif mutation == "missing":
        del record["data"]["payload"]
    else:
        record["data"]["payload"]["unexpected"] = True
    path.write_text(json.dumps(record))
    with pytest.raises(qd.PlatformError, match="payload"):
        qd.run_facts(directory)
