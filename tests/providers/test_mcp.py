"""The mcp server API the repository's stdio adapters (scripts/qd_mcp_server.py, scripts/iqm_mcp_server.py) build on.

The adapters subclass MCPServer and reach two private members, ``_tool_input_schema`` and ``_lowlevel_server``,
which no import names, so this file holds them to the pinned version.
"""

from __future__ import annotations

from typing import Any

import anyio
import pytest
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import Tool, ToolAnnotations


def server() -> MCPServer:
    instance = MCPServer("probe")

    @instance.tool(annotations=ToolAnnotations(read_only_hint=True, open_world_hint=False))
    async def double(value: int) -> int:
        """Twice the value."""
        return 2 * value

    @instance.tool(annotations=ToolAnnotations(read_only_hint=False, destructive_hint=True, idempotent_hint=True))
    async def refuse(reason: str) -> str:
        """Always fails."""
        raise ToolError(f"refused: {reason}")

    return instance


def test_listed_tools_carry_schema_and_annotations() -> None:
    tools: list[Tool] = anyio.run(server().list_tools)
    by_name = {tool.name: tool for tool in tools}
    if set(by_name) != {"double", "refuse"}:
        raise AssertionError(sorted(by_name))
    schema = by_name["double"].input_schema
    if schema.get("properties", {}).get("value", {}).get("type") != "integer" or schema.get("required") != ["value"]:
        raise AssertionError(schema)
    annotations = by_name["refuse"].annotations
    if annotations is None or not annotations.destructive_hint or annotations.read_only_hint:
        raise AssertionError(annotations)


def test_private_members_the_adapters_use() -> None:
    instance = server()
    schema = instance._tool_input_schema("double")
    if not isinstance(schema, dict) or "value" not in schema.get("properties", {}):
        raise AssertionError(schema)
    if instance._tool_input_schema("absent") is not None:
        raise AssertionError("an unknown tool must have no schema")
    core = instance._lowlevel_server
    if not callable(core.run) or core.create_initialization_options() is None:
        raise AssertionError("the low-level server lost run or create_initialization_options")


def test_call_tool_returns_results_and_raises_tool_errors() -> None:
    instance = server()

    async def call(name: str, arguments: dict[str, Any]) -> Any:
        return await instance.call_tool(name, arguments)

    result = anyio.run(call, "double", {"value": 21})
    if result.is_error or result.structured_content != {"result": 42} or result.content[0].text != "42":
        raise AssertionError(result)
    with pytest.raises(ToolError, match="refused: no"):
        anyio.run(call, "refuse", {"reason": "no"})
