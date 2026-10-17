> Full piece: [https://docs.openquantum.com/mcp/installation/](https://docs.openquantum.com/mcp/installation/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c4fa5583dbc6b2cfda5429a2e62787d4f46604edfdf029247dddd0f444427baa.

# Installation

## Install from PyPI

``` bash
pip install openquantum-mcp
```

This installs **`openquantum-mcp` 0.2.0** and its dependency **`openquantum-sdk`** (`>=1.0.0`).

Requires **Python 3.10 or later** (the official MCP Python library requires 3.10+). The sdist includes the unit tests. The wheel does not install them.

Optional explicit install of both packages:

``` bash
pip install openquantum-sdk openquantum-mcp
```

## Verify

``` bash
python -c "import openquantum_mcp; print(openquantum_mcp.__version__)"
python -m openquantum_mcp --version
python -m openquantum_mcp --help
```

These commands should print the package version and a short usage message, then exit. Do **not** start the server from a bare terminal for day-to-day use — it speaks MCP over stdio and is meant to be launched by an MCP client.

Confirm the console entry point is on your PATH (or use `python -m openquantum_mcp` in client config):

``` bash
which openquantum-mcp || which python
```

## Credentials

Create an SDK key in the portal: [SDK Keys](https://www.openquantum.com/keys). See [SDK Keys](https://docs.openquantum.com/portal/sdk-keys/) and [Authentication](https://docs.openquantum.com/core-sdk/authentication/).

Set one of:

``` bash
export OPENQUANTUM_CLIENT_ID="s_..."
export OPENQUANTUM_CLIENT_SECRET="..."
```

or:

``` bash
export OPENQUANTUM_SDK_KEY="/path/to/sdk-key.json"
```

The JSON key file must contain `client_id` and `client_secret`. If `OPENQUANTUM_SDK_KEY` is set but the path does not exist, the server fails with a clear error (it does not silently fall back).

Warning

Never commit secrets to git or paste them into shared chats. Prefer environment variables or your MCP client's secret storage.

## Optional environment variables

| Variable | Default | Meaning |
|----|----|----|
| `OPENQUANTUM_MCP_MAX_CREDITS` | `10` | Reject jobs whose estimated cost exceeds this many credits |
| `OPENQUANTUM_MCP_WAIT_TIMEOUT_SECONDS` | `600` | Default timeout for `wait_for_job` when `timeout_seconds` is omitted |
| `OPENQUANTUM_MCP_POLL_INTERVAL_SECONDS` | `5` | Default poll interval for `wait_for_job` when omitted |
| `OPENQUANTUM_MCP_PREP_TIMEOUT_SECONDS` | `300` | Max time to wait for job preparation to finish |
| `OPENQUANTUM_MCP_DEFAULT_SHOTS` | `128` | Default shots when `prepare_job` / `submit_job` omit `shots` |
| `OPENQUANTUM_MCP_DEFAULT_SUBCATEGORY` | `oth:oth` | Default `job_subcategory_id` when omitted |
| `OPENQUANTUM_MCP_MAX_RESULT_RAW_CHARS` | `8000` | Cap on raw result payload when `include_raw=true` |
| `OPENQUANTUM_MCP_MAX_CALIBRATION_RAW_CHARS` | `8000` | Cap on raw calibration payload |
| `OPENQUANTUM_ORGANIZATION_ID` | first membership | Billing org when a tool omits `organization_id` |
| `OPENQUANTUM_MANAGEMENT_URL` | production management URL | Override management API base (e.g. staging/dev). `OPENQUANTUM_MANAGEMENT_BASE` is still accepted |
| `OPENQUANTUM_SCHEDULER_URL` | production scheduler URL | Override scheduler API base. `OPENQUANTUM_SCHEDULER_BASE` is still accepted |
| `OPENQUANTUM_KEYCLOAK_BASE` | production id URL | Override Keycloak / token base |
| `OPENQUANTUM_KEYCLOAK_REALM` | `platform` | Keycloak realm for client-credentials tokens |

Auth variables (required; see [Credentials](#credentials)):

| Variable | Meaning |
|----|----|
| `OPENQUANTUM_CLIENT_ID` | SDK key client id |
| `OPENQUANTUM_CLIENT_SECRET` | SDK key secret |
| `OPENQUANTUM_SDK_KEY` | Path to JSON key file (`client_id` + `client_secret`) |

## Next steps

- [Client setup](https://docs.openquantum.com/mcp/client-setup/) — register the server in your agent
- [Tools & spend policy](https://docs.openquantum.com/mcp/tools/) — what the agent can call
