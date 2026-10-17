> Full piece: [https://docs.openquantum.com/mcp/client-setup/](https://docs.openquantum.com/mcp/client-setup/)
> Retrieved 2026-10-17T05:09Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ca0c3320b07ae709c553b80d21ecf29f98bcc123b6107f931cc8082a4361fb70.

# Client setup

Register **`openquantum-mcp`** as a local MCP server. The process is the same for every host: run `python -m openquantum_mcp` (or `openquantum-mcp`) with your SDK credentials in the environment.

## Generic MCP config

Many clients use an `mcpServers` (or equivalent) map:

[](#__codelineno-0-1)`{`\
[](#__codelineno-0-2)`  ``"mcpServers"``:`` ``{`\
[](#__codelineno-0-3)`    ``"openquantum"``:`` ``{`\
[](#__codelineno-0-4)`      ``"command"``:`` ``"python"``,`\
[](#__codelineno-0-5)`      ``"args"``:`` ``[``"-m"``,`` ``"openquantum_mcp"``],`\
[](#__codelineno-0-6)`      ``"env"``:`` ``{`\
[](#__codelineno-0-7)`        ``"OPENQUANTUM_CLIENT_ID"``:`` ``"s_your_client_id"``,`\
[](#__codelineno-0-8)`        ``"OPENQUANTUM_CLIENT_SECRET"``:`` ``"your_client_secret"`\
[](#__codelineno-0-9)`      ``}`\
[](#__codelineno-0-10)`    ``}`\
[](#__codelineno-0-11)`  ``}`\
[](#__codelineno-0-12)`}`\

Tip

If the client cannot find `python`, set `command` to an **absolute path** to the interpreter where you ran `pip install openquantum-mcp` (for example `/Users/you/.venv/bin/python`).

Using a key file instead of inline secrets:

[](#__codelineno-1-1)`{`\
[](#__codelineno-1-2)`  ``"mcpServers"``:`` ``{`\
[](#__codelineno-1-3)`    ``"openquantum"``:`` ``{`\
[](#__codelineno-1-4)`      ``"command"``:`` ``"/absolute/path/to/python"``,`\
[](#__codelineno-1-5)`      ``"args"``:`` ``[``"-m"``,`` ``"openquantum_mcp"``],`\
[](#__codelineno-1-6)`      ``"env"``:`` ``{`\
[](#__codelineno-1-7)`        ``"OPENQUANTUM_SDK_KEY"``:`` ``"/absolute/path/to/sdk-key.json"`\
[](#__codelineno-1-8)`      ``}`\
[](#__codelineno-1-9)`    ``}`\
[](#__codelineno-1-10)`  ``}`\
[](#__codelineno-1-11)`}`\

## Claude (Desktop / Code)

Add the server to your Claude MCP settings (product UI or config file, depending on version). Use the generic `mcpServers` block above with absolute paths when possible.

After reload, confirm tools such as `list_backends` and `get_credits` appear for the Open Quantum server.

## Cursor

Add the same server definition to Cursor’s MCP configuration (Cursor Settings → MCP, or the project/user `mcp.json` your Cursor version uses). Restart or refresh MCP after saving.

## VS Code and other hosts

Any host that can launch a local stdio MCP server can use this package. Point it at `python -m openquantum_mcp` and pass credentials via `env`.

## Smoke test in chat

Once tools are connected, try:

1.  “List my Open Quantum organizations and credit balances.”
2.  “List online backends.”
3.  “Prepare a 2-qubit Bell state (OpenQASM) on \\backend\>, 128 shots, and show the quote — do not submit yet.”
4.  After reviewing cost: “Submit that preparation” (approve Full-credit spend only if you intend to).
5.  “Wait for the job, then summarize the counts.”

Long QPU queues are normal. If `wait_for_job` times out (default 10 minutes), ask the agent to wait again or check status with `get_job`.

## Troubleshooting

| Symptom | What to check |
|----|----|
| Server fails to start | Python 3.10+, `pip show openquantum-mcp`, absolute `command` path |
| Auth errors on every tool | `OPENQUANTUM_CLIENT_ID` / `SECRET` or `OPENQUANTUM_SDK_KEY` in the **MCP process** env (not only your shell) |
| `OPENQUANTUM_SDK_KEY` “does not exist” | Path typo or relative path that is wrong for the client’s working directory — use an **absolute** path to the JSON key file |
| Generic “Missing credentials” | No `CLIENT_ID`+`SECRET` and no `OPENQUANTUM_SDK_KEY` in the MCP `env` block (exporting only in your interactive shell is not enough) |
| Tools missing | Client reloaded after config change; server name unique |
| Unexpected spend blocked | See [Tools & spend policy](https://docs.openquantum.com/mcp/tools/) — Full credits need `confirm_spend=true`; costs over the cap are rejected |
| `wait_for_job` always ~10 minutes | Override per call with `timeout_seconds`, or set `OPENQUANTUM_MCP_WAIT_TIMEOUT_SECONDS` in the MCP process env |

## Next steps

- [Tools & spend policy](https://docs.openquantum.com/mcp/tools/)
- [Job lifecycle](https://docs.openquantum.com/concepts/job-lifecycle/)
- [Credits](https://docs.openquantum.com/concepts/credits/)
