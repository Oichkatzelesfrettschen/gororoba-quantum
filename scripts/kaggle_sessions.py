"""Kaggle batch sessions: list a kernel's versions with their session ids, read the quota, cancel a session.

A batch kernel version runs as one Kaggle session, and its session id is the
version's ``scriptVersionId`` (the number in
``https://www.kaggle.com/code/OWNER/SLUG?scriptVersionId=ID``). Pushing a
new version does not end the old version's session, so a re-push can leave
several versions of one kernel running, each billing its machine.

No public interface returns a running version's id: the Kaggle CLI answers
for the slug's latest version only, and kagglesdk and the Kaggle MCP answer
for a version named as ``vN`` without its session id.
Kaggle's web API does, through
``kernels.KernelsService/ListKernelVersions``, which needs a signed-in
browser session. ``versions`` therefore copies the session files of the
local Firefox profile (cookies, certificate and key stores) into a private
temporary profile, loads the kernel page in headless Firefox, calls that
endpoint from the page with its XSRF token, prints every version's session
id, number, status and URL, and deletes the copy; no cookie value is
printed or written elsewhere. ``quota`` and ``cancel`` call the Kaggle MCP
server's ``get_accelerator_quota`` and ``cancel_notebook_session`` over HTTP
with the bearer header that ``~/.config/shell/kaggle-mcp-headers.sh``
prints (the Kaggle CLI's access token), so they work whether or not the
session has the MCP tools loaded. ``cancel-running OWNER/SLUG`` cancels
every running or queued version of a kernel and shows the quota after.

Usage (build host only; needs Firefox with a signed-in Kaggle session,
geckodriver and selenium):
    "$PYTHON" scripts/kaggle_sessions.py versions probablyeric/SLUG
    "$PYTHON" scripts/kaggle_sessions.py quota
    "$PYTHON" scripts/kaggle_sessions.py cancel SESSION_ID
    "$PYTHON" scripts/kaggle_sessions.py cancel-running probablyeric/SLUG
    "$PYTHON" scripts/kaggle_sessions.py --self-test
"""

from __future__ import annotations

import argparse
import configparser
import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
from typing import Any

MCP_URL = "https://www.kaggle.com/mcp"
HEADERS_HELPER = Path.home() / ".config/shell/kaggle-mcp-headers.sh"
SESSION_FILES = ("cookies.sqlite", "cookies.sqlite-wal", "cert9.db", "key4.db", "permissions.sqlite")
LIVE = {"RUNNING", "QUEUED", "NEW_SCRIPT"}
FETCH = """
const done = arguments[arguments.length - 1];
const xsrf = (document.cookie.match(/XSRF-TOKEN=([^;]+)/) || [])[1] || "";
fetch(arguments[0], {method: "POST", credentials: "include",
  headers: {"content-type": "application/json", "x-xsrf-token": decodeURIComponent(xsrf)},
  body: JSON.stringify(arguments[1])})
  .then(r => r.text().then(t => done([r.status, t]))).catch(e => done([0, String(e)]));
"""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def default_profile() -> Path:
    """The Firefox profile profiles.ini marks as the install default, else the one marked Default=1."""
    base = Path.home() / ".mozilla/firefox"
    ini = configparser.ConfigParser()
    ini.read(base / "profiles.ini")
    for section in ini.sections():
        if section.startswith("Install") and ini.has_option(section, "Default"):
            return base / ini.get(section, "Default")
    for section in ini.sections():
        if ini.get(section, "Default", fallback="0") == "1":
            return base / ini.get(section, "Path")
    raise SystemExit("no default Firefox profile in profiles.ini; pass --profile")


def _collect(node: Any, found: dict[str, Any]) -> None:
    """Record the first version number and every session object under node."""
    if isinstance(node, dict):
        if "versionNumber" in node and found["number"] is None:
            found["number"] = node["versionNumber"]
        if "kernelId" in node and "status" in node:
            found["sessions"].append(node)
        for value in node.values():
            _collect(value, found)
    elif isinstance(node, list):
        for value in node:
            _collect(value, found)


def session_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Every kernel-version session in a ListKernelVersions response: id, version number, status, created."""
    out = []
    for item in payload.get("items", []):
        found: dict[str, Any] = {"number": None, "sessions": []}
        _collect(item, found)
        for session in found["sessions"]:
            out.append(
                {
                    "session_id": int(session["id"]),
                    "version": found["number"],
                    "status": session["status"],
                    "created": session.get("dateCreated"),
                    "kernel_id": int(session["kernelId"]),
                }
            )
    return sorted(out, key=lambda row: row["session_id"])


def live_sessions(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The rows of session_items whose session still holds a machine: RUNNING, QUEUED or NEW_SCRIPT."""
    return [row for row in rows if row["status"] in LIVE]


def kernel_id(ref: str) -> int:
    """The kernel's numeric id from Kaggle's public API (`kaggle kernels pull -m` metadata)."""
    with tempfile.TemporaryDirectory() as scratch:
        subprocess.run(["kaggle", "kernels", "pull", "-m", "-p", scratch, ref], check=True, capture_output=True)
        metadata = json.loads((Path(scratch) / "kernel-metadata.json").read_text(encoding="utf-8"))
    require("id_no" in metadata, f"{ref}: metadata carries no numeric id_no")
    return int(metadata["id_no"])


def list_versions(ref: str, profile: Path) -> list[dict[str, Any]]:
    from selenium import webdriver
    from selenium.webdriver.firefox.options import Options

    owner, slug = ref.split("/")
    numeric = kernel_id(ref)
    with tempfile.TemporaryDirectory(prefix="kaggle-ff-") as scratch:
        for name in SESSION_FILES:
            if (profile / name).is_file():
                shutil.copy2(profile / name, Path(scratch) / name)
        cookies = Path(scratch) / "cookies.sqlite"
        require(cookies.is_file(), f"{profile}: no cookies.sqlite")
        with sqlite3.connect(cookies) as con:
            con.execute("PRAGMA wal_checkpoint(FULL)")
            signed = con.execute("select count(*) from moz_cookies where host like '%kaggle.com'").fetchone()[0]
        require(signed > 0, f"{profile}: no kaggle.com cookies; sign in to Kaggle in Firefox")
        options = Options()
        options.add_argument("-headless")
        options.add_argument("-profile")
        options.add_argument(scratch)
        driver = webdriver.Firefox(options=options)
        try:
            driver.get(f"https://www.kaggle.com/code/{owner}/{slug}")
            time.sleep(6)
            driver.set_script_timeout(60)
            status, text = driver.execute_async_script(
                FETCH, "/api/i/kernels.KernelsService/ListKernelVersions", {"kernelId": numeric}
            )
        finally:
            driver.quit()
    require(status == 200, f"ListKernelVersions answered HTTP {status}")
    return session_items(json.loads(text))


def mcp(tool: str, arguments: dict[str, Any]) -> Any:
    """Call one Kaggle MCP tool over streamable HTTP and return its decoded JSON text content."""
    headers = json.loads(subprocess.run(["sh", str(HEADERS_HELPER)], capture_output=True, text=True, check=True).stdout)
    headers.update({"Content-Type": "application/json", "Accept": "application/json, text/event-stream"})
    session: str | None = None

    def call(method: str, params: dict[str, Any], ident: int | None) -> Any:
        nonlocal session
        request_headers = dict(headers)
        if session:
            request_headers["Mcp-Session-Id"] = session
        body: dict[str, Any] = {"jsonrpc": "2.0", "method": method, "params": params}
        if ident is not None:
            body["id"] = ident
        request = urllib.request.Request(
            MCP_URL, data=json.dumps(body).encode(), headers=request_headers, method="POST"
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            session = response.headers.get("Mcp-Session-Id", session)
            text = response.read().decode()
        return parse_rpc(text)

    call(
        "initialize",
        {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "kaggle_sessions", "version": "1"},
        },
        1,
    )
    call("notifications/initialized", {}, None)
    reply = call("tools/call", {"name": tool, "arguments": arguments}, 2)
    require(reply is not None and "result" in reply, f"{tool}: {reply}")
    result = reply["result"]
    require(not result.get("isError"), f"{tool}: {result}")
    text = "".join(part.get("text", "") for part in result.get("content", []))
    return json.loads(text) if text.strip() else {}


def parse_rpc(text: str) -> Any:
    """A JSON-RPC reply sent as plain JSON or as a server-sent-events data line."""
    if not text.strip():
        return None
    if text.lstrip().startswith("{"):
        return json.loads(text)
    for line in text.splitlines():
        if line.startswith("data:"):
            return json.loads(line[5:])
    return None


def quota() -> dict[str, Any]:
    data = mcp("get_accelerator_quota", {"request": {}})
    out = {}
    for kind in ("gpu_quota", "tpu_quota"):
        entry = data.get(kind, {})
        seconds = {
            key: float(str(entry.get(key, "0s")).rstrip("s") or 0)
            for key in ("time_used", "time_reserved", "total_time_allowed")
        }
        out[kind] = {key: round(value / 3600, 2) for key, value in seconds.items()}
    out["refresh"] = data.get("quota_refresh_time")
    return out


def self_test() -> None:
    payload = {
        "items": [
            {"versionNumber": 1, "x": {"id": 11, "kernelId": 7, "status": "ERROR", "dateCreated": "a"}},
            {"versionNumber": 2, "x": [{"id": 12, "kernelId": 7, "status": "RUNNING", "dateCreated": "b"}]},
        ]
    }
    rows = session_items(payload)
    require(
        [(r["session_id"], r["version"], r["status"]) for r in rows] == [(11, 1, "ERROR"), (12, 2, "RUNNING")],
        f"{rows}",
    )
    require([r["session_id"] for r in live_sessions(rows)] == [12], "live filter")
    require(parse_rpc('event: message\ndata: {"id": 2, "result": {}}\n') == {"id": 2, "result": {}}, "SSE parse")
    require(parse_rpc('{"id": 1}') == {"id": 1}, "JSON parse")
    print("kaggle_sessions self-test: version parsing, the live-session filter and JSON-RPC decoding pass")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--profile", type=Path, help="Firefox profile directory with a signed-in Kaggle session")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("versions").add_argument("ref", help="OWNER/SLUG")
    sub.add_parser("quota")
    sub.add_parser("cancel").add_argument("session_id", type=int)
    sub.add_parser("cancel-running").add_argument("ref", help="OWNER/SLUG")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    require(args.command is not None, "name a command or --self-test")
    if args.command == "quota":
        print(json.dumps(quota(), indent=1))
        return 0
    if args.command == "cancel":
        mcp("cancel_notebook_session", {"request": {"kernelSessionId": args.session_id}})
        print(f"cancel requested for session {args.session_id}")
        return 0
    profile = args.profile or default_profile()
    rows = list_versions(args.ref, profile)
    owner, slug = args.ref.split("/")
    for row in rows:
        print(
            f"session {row['session_id']}  version {row['version']}  {row['status']:<20} {row['created']}  "
            f"https://www.kaggle.com/code/{owner}/{slug}?scriptVersionId={row['session_id']}"
        )
    if args.command == "cancel-running":
        live = live_sessions(rows)
        for row in live:
            mcp("cancel_notebook_session", {"request": {"kernelSessionId": row["session_id"]}})
            print(f"cancel requested for session {row['session_id']} (version {row['version']})")
        if live:
            print(json.dumps(quota(), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
