"""Real stdio transport exercises tools against a provider-isolated HTTP fixture."""

import json
import sys
import tempfile
from datetime import timedelta
from pathlib import Path
from typing import Any

import anyio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import TextContent

JOB = "01234567-89ab-cdef-0123-456789abcdef"


def test_stdio_tool_routes_redaction_output_isolation_and_concurrency() -> None:
    root = Path(__file__).resolve().parents[2]
    bootstrap = f"""
import os, sys, threading
sys.path.insert(0, {str(root / "scripts")!r})
import qd_platform as qd
import qd_mcp_server as app
event = threading.Event()
availability_started = threading.Event()
availability_reads = 0
concurrency_enabled = False
def forbid(*args, **kwargs):
    raise RuntimeError('provider access forbidden in transport test')
qd.OPENER.open = forbid
def get(route, auth=True):
    global availability_reads, concurrency_enabled
    os.write(1, b'QD_NATIVE_STDOUT_PROBE\\n')
    if route == '/api/platforms/public/explorer':
        if auth:
            raise RuntimeError('public route requested authentication')
        return [{{'name':'qpu:ascella','type':'qpu','status':'available'}}]
    if route == '/api/platforms/public':
        if auth:
            raise RuntimeError('public route requested authentication')
        return [{{'name':'qpu:ascella','type':'qpu','status':'available'}}]
    if route == '/api/platforms/qpu%3Aascella/processor':
        return {{'name':'qpu:ascella','specs':{{'architecture':'synthetic-chip','documentation':''}}}}
    if route == '/api/jobs/availability':
        availability_reads += 1
        if availability_reads > 1:
            availability_started.set()
            if not event.wait(20):
                raise RuntimeError('HTTP read blocked concurrent MCP request')
        return dict.fromkeys(qd.AVAILABILITY_KEYS, 0)
    if route == '/api/tokens/usage/report':
        return [{{'token_id':123,'usage':[{{'token_value':'synthetic-secret','nb_jobs':2}}]}}]
    if route == '/api/jobs/{JOB}/status':
        if concurrency_enabled and not availability_started.wait(20):
            raise RuntimeError('status read blocked concurrent availability request')
        event.set()
        return {{'status':'completed','shots':1}}
    if route == '/api/jobs/{JOB}/result':
        event.clear()
        concurrency_enabled = True
        return {{'nested':[{{'text':'x'*9000}}]}}
    raise RuntimeError('unexpected fixture GET '+route)
def request(method, route):
    if (method, route) != ('POST', '/api/jobs/{JOB}/cancel'):
        raise RuntimeError('unexpected fixture mutation')
    return {{'message':'synthetic cancellation'}}
app.get = qd.get = get
app.request = request
app.serve()
"""

    async def exercise(errorlog: Any) -> None:
        parameters = StdioServerParameters(command=sys.executable, args=["-I", "-W", "error", "-c", bootstrap])
        async with stdio_client(parameters, errlog=errorlog) as (reader, writer):
            async with ClientSession(reader, writer, read_timeout_seconds=timedelta(seconds=30)) as session:
                await session.initialize()
                definitions = {tool.name: tool for tool in (await session.list_tools()).tools}
                expected = {
                    "qd_platforms",
                    "qd_platform",
                    "qd_availability",
                    "qd_usage",
                    "qd_plan",
                    "qd_job_billing",
                    "qd_job_status",
                    "qd_job_result",
                    "qd_cancel_job",
                    "qd_simulate_local",
                }
                if set(definitions) != expected:
                    raise AssertionError(f"MCP tools differ: {set(definitions) ^ expected}")
                for name, tool in definitions.items():
                    if tool.annotations is None or tool.annotations.readOnlyHint != (name != "qd_cancel_job"):
                        raise AssertionError(f"incorrect mutation annotation for {name}")
                    if tool.inputSchema.get("additionalProperties") is not False:
                        raise AssertionError(f"undeclared arguments remain admitted by {name}")

                async def call(name: str, arguments: dict[str, Any]) -> Any:
                    result = await session.call_tool(name, arguments)
                    if result.isError:
                        raise AssertionError(f"{name} failed: {result.content}")
                    if not result.content or not isinstance(result.content[0], TextContent):
                        raise AssertionError(f"{name} returned an unexpected content type: {result.content}")
                    content = json.loads(result.content[0].text)
                    return content

                platforms = await call("qd_platforms", {})
                if platforms["public"] != [{"name": "qpu:ascella", "type": "qpu", "status": "available"}]:
                    raise AssertionError(f"public platform result changed: {platforms}")
                platform = await call("qd_platform", {"name": "qpu:ascella"})
                if platform["specs"]["architecture"] != {"stripped": True, "chars": 16}:
                    raise AssertionError(f"default platform read failed to strip bulk: {platform}")
                platform = await call("qd_platform", {"name": "qpu:ascella", "include_bulk": True})
                if platform["specs"]["architecture"] != "synthetic-chip":
                    raise AssertionError("include_bulk lost the architecture")
                occupancy = await call("qd_availability", {})
                if any(
                    occupancy[key] != 0
                    for key in (
                        "max_concurrent_jobs",
                        "max_jobs_in_queue",
                        "max_running_qt_jobs",
                        "num_concurrent_jobs",
                        "num_jobs_in_queue",
                        "num_running_qt_jobs",
                    )
                ):
                    raise AssertionError("queue guidance changed the token counters")
                queue = occupancy["platform_queue"]
                if queue["count"] is not None or queue["status"] != "requires-dashboard-session":
                    raise AssertionError("the global queue must remain unknown rather than inherit token occupancy")
                if queue["dashboard_url"] != "https://cloud.quandela.com/webide/":
                    raise AssertionError("the queue response must offer the authenticated dashboard")
                usage = await call("qd_usage", {})
                if usage != {"usage": [{"nb_jobs": 2}]}:
                    raise AssertionError(f"usage changed counters or exposed account identifiers: {usage}")
                status = await call("qd_job_status", {"job_id": JOB})
                if status != {"status": "completed", "shots": 1}:
                    raise AssertionError(f"job status changed: {status}")
                result = await call("qd_job_result", {"job_id": JOB})
                if result["nested"][0]["text"] != "x" * 8000 + "...":
                    raise AssertionError("nested result string escaped truncation")
                result = await call("qd_job_result", {"job_id": JOB, "include_raw": True})
                if result["nested"][0]["text"] != "x" * 9000:
                    raise AssertionError("include_raw changed the result")
                async with anyio.create_task_group() as group:
                    group.start_soon(call, "qd_availability", {})
                    group.start_soon(call, "qd_job_status", {"job_id": JOB})
                cancelled = await call("qd_cancel_job", {"job_id": JOB})
                if cancelled != {"job_id": JOB, "answer": {"message": "synthetic cancellation"}}:
                    raise AssertionError(f"cancellation response changed: {cancelled}")
                vacuum = await call("qd_simulate_local", {"real": [[1]], "input_photons": [0]})
                if vacuum["probabilities"] != {"|0>": 1.0}:
                    raise AssertionError(f"vacuum simulation changed its state: {vacuum}")
                failed = await session.call_tool("qd_platform", {"name": "qpu:fixture-failure"})
                if not failed.isError or "qd_platform:" not in str(failed.content):
                    raise AssertionError(f"tool failure lost its named error envelope: {failed}")
                for name, arguments in (
                    ("qd_job_status", {"job_id": "../../api/tokens"}),
                    ("qd_job_result", {"job_id": JOB, "include_raw": 1}),
                    ("qd_platform", {"name": "qpu:ascella", "hardware_config": {}}),
                ):
                    rejected = await session.call_tool(name, arguments)
                    if not rejected.isError or "Input validation error" not in str(rejected.content):
                        raise AssertionError(f"schema violation reached a tool: {name}: {rejected}")

    with tempfile.TemporaryFile(mode="w+") as errorlog:
        anyio.run(exercise, errorlog)
        errorlog.seek(0)
        diagnostics = errorlog.read()
    if "QD_NATIVE_STDOUT_PROBE" not in diagnostics:
        raise AssertionError("descriptor-one output failed to reach stderr")
    if "ResourceWarning" in diagnostics:
        raise AssertionError(f"stdio transport leaked a resource: {diagnostics}")
