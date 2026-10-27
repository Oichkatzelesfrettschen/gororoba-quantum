"""Local compiler receipts bind every campaign circuit and reject changed controls."""

import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import experiment_toolchain as toolchain
import pytest


@pytest.fixture
def campaign(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(toolchain, "ROOT", tmp_path)
    monkeypatch.setattr(toolchain, "compiler_configs", lambda: {"QXsinglenodesimulator": {"decomposition": []}})
    monkeypatch.setattr(toolchain.qi_stack, "live", lambda *args: False)
    for relative in toolchain.SOURCE_FILES:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("fixture source\n")
    directory = tmp_path / "cases/qx/fixture"
    directory.mkdir(parents=True)
    payload = "version 3.0\nqubit[2] q\nbit[2] b\nH q[0]\nbarrier q\nb[0] = measure q[1]\nb[1] = measure q[0]\n"
    (directory / "science.cq").write_text(payload)
    manifest = {
        "backend": "QXsinglenodesimulator",
        "backend_type_id": 1,
        "circuits": [{"file": "science.cq", "sha256": toolchain.digest(payload.encode())}],
    }
    encoded = json.dumps(manifest).encode()
    (directory / "cases.json").write_bytes(encoded)
    path = tmp_path / "cases/campaign.json"
    path.write_text(
        json.dumps(
            {
                "schema": "quantum-experiment-campaign-v1",
                "cases": [
                    {"provider": "qi", "backend": "qx", "path": "qx/fixture", "sha256": toolchain.digest(encoded)}
                ],
            }
        )
    )
    return path


def _rebind(campaign: Path, manifest: dict[str, Any]) -> None:
    path = campaign.parent / "qx/fixture/cases.json"
    encoded = json.dumps(manifest).encode()
    path.write_bytes(encoded)
    index = json.loads(campaign.read_bytes())
    index["cases"][0]["sha256"] = toolchain.digest(encoded)
    campaign.write_text(json.dumps(index))


def _receipt(campaign: Path, output: Path) -> dict[str, Any]:
    header, payloads = toolchain.inventory(campaign)
    rows = [
        {
            "case": path,
            "sha256": digest,
            "backend": backend,
            "compiler_config_sha256": toolchain.config_digest({"decomposition": []}),
            "passes": [],
            "libqasm": "ok",
            "compiled": "ok",
            "compiled_sha256": digest,
            "control_sequence_preserved": True,
            "control_changes": {},
            "gate_sequence_preserved": True,
            "gate_changes": {},
        }
        for path, (digest, backend) in payloads.items()
    ]
    pins = toolchain.qi_stack.pins()
    record = {
        **header,
        "toolchain": {"python": "3.13.7", "libqasm": pins["libqasm"], "opensquirrel": pins["opensquirrel"]},
        "circuits": rows,
    }
    output.write_text(json.dumps(record))
    return record


def test_inventory_binds_manifest_payload_backend_and_sources(campaign: Path) -> None:
    header, payloads = toolchain.inventory(campaign)
    if len(payloads) != 1 or len(header["manifests"]) != 1 or set(header["sources"]) != set(toolchain.SOURCE_FILES):
        raise RuntimeError("the compiler receipt needs the complete digest chain")
    if next(iter(payloads.values()))[1] != "QXsinglenodesimulator":
        raise RuntimeError("the QX campaign route must retain its compiler identity")


@pytest.mark.parametrize("mutation", ["manifest", "payload", "unlisted", "duplicate", "backend", "escape"])
def test_inventory_rejects_broken_digest_chains_and_paths(campaign: Path, mutation: str) -> None:
    directory = campaign.parent / "qx/fixture"
    manifest = json.loads((directory / "cases.json").read_bytes())
    if mutation == "manifest":
        (directory / "cases.json").write_text("{}")
    elif mutation == "payload":
        (directory / "science.cq").write_text("changed")
    elif mutation == "unlisted":
        (directory / "extra.cq").write_text("changed")
    elif mutation == "duplicate":
        manifest["circuits"].append(dict(manifest["circuits"][0]))
        _rebind(campaign, manifest)
    elif mutation == "backend":
        manifest["backend"] = "tuna_17"
        _rebind(campaign, manifest)
    else:
        external = campaign.parent / "external.cq"
        external.write_text("version 3.0")
        manifest["circuits"][0]["file"] = "../../external.cq"
        _rebind(campaign, manifest)
    with pytest.raises(ValueError, match="digest|inventory|twice|backend|escapes"):
        toolchain.inventory(campaign)


@pytest.mark.parametrize("mutation", ["missing-control", "changed-control", "source", "config", "rows", "runtime"])
def test_checker_requires_full_control_and_current_bindings(campaign: Path, tmp_path: Path, mutation: str) -> None:
    output = tmp_path / "receipt.json"
    record = _receipt(campaign, output)
    if toolchain.check(campaign, output) != 0:
        raise RuntimeError("the complete fixture should pass record admission")
    if mutation == "missing-control":
        del record["circuits"][0]["control_sequence_preserved"]
    elif mutation == "changed-control":
        record["circuits"][0]["control_changes"] = {"0": {"source": [["measure", 1]], "compiled": [["measure", 0]]}}
    elif mutation == "source":
        record["sources"][toolchain.SOURCE_FILES[0]] = "0" * 64
    elif mutation == "config":
        record["circuits"][0]["compiler_config_sha256"] = "0" * 64
    elif mutation == "rows":
        record["circuits"].append(record["circuits"][0])
    else:
        record["toolchain"]["libqasm"] = "changed"
    output.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="control|sources|configuration|duplicate|versions"):
        toolchain.check(campaign, output)


def test_compile_row_detects_changed_measurement_destinations(campaign: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    module = ModuleType("cqasm")
    submodule = ModuleType("cqasm.v3x")

    class Analyzer:
        def analyze_string_to_json(self, text: str) -> str:
            return '{"errors": []}'

    submodule.Analyzer = Analyzer  # type: ignore[attr-defined]
    module.v3x = submodule  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "cqasm", module)
    monkeypatch.setitem(sys.modules, "cqasm.v3x", submodule)
    monkeypatch.setattr(
        toolchain, "compile_circuit", lambda text, config: text.replace("b[0] = measure q[1]", "b[1] = measure q[1]")
    )
    _, payloads = toolchain.inventory(campaign)
    path, (sha256, backend) = next(iter(payloads.items()))
    row = toolchain.compile_row((path, sha256, backend, {"decomposition": []}))
    if row["control_sequence_preserved"] is not False or toolchain._admitted(row):
        raise RuntimeError("changing a measurement destination must fail compiler admission")


def test_compile_row_rejects_payload_changed_after_inventory(campaign: Path) -> None:
    _, payloads = toolchain.inventory(campaign)
    path, (sha256, backend) = next(iter(payloads.items()))
    (toolchain.ROOT / path).write_text("changed after inventory\n")
    with pytest.raises(ValueError, match="changed before compilation"):
        toolchain.compile_row((path, sha256, backend, {"decomposition": []}))


def test_generate_rejects_source_changes_before_receipt(
    campaign: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def changed_inputs(function: Any, arguments: Any, **kwargs: Any) -> list[Any]:
        (toolchain.ROOT / toolchain.SOURCE_FILES[0]).write_text("changed during compilation\n")
        return []

    monkeypatch.setattr(toolchain, "ordered_map", changed_inputs)
    output = tmp_path / "receipt.json"
    with pytest.raises(ValueError, match="inputs changed during compilation"):
        toolchain.generate(campaign, output)
    if output.exists():
        raise RuntimeError("a changing source must fail before a receipt is written")


def test_live_replay_uses_selected_campaign_and_output(
    campaign: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "receipt.json"
    _receipt(campaign, output)
    monkeypatch.setattr(toolchain.qi_stack, "live", lambda *args: True)
    calls = []

    def replay(arguments: list[str]) -> str:
        calls.append(arguments)
        Path(arguments[arguments.index("--out") + 1]).write_bytes(output.read_bytes())
        return ""

    monkeypatch.setattr(toolchain.qi_stack, "run", replay)
    toolchain.check(campaign, output)
    if len(calls) != 1 or calls[0][calls[0].index("--campaign") + 1] != str(campaign.resolve()):
        raise RuntimeError("live replay must compile the selected campaign")
