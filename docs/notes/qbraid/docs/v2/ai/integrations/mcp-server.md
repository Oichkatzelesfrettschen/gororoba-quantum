> Full piece: [https://docs.qbraid.com/v2/ai/integrations/mcp-server.md](https://docs.qbraid.com/v2/ai/integrations/mcp-server.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 9c070d8dc4b29c898d103f4a5308779653ecb72bb119eaadb68f4e1e95853a13.

> ## Documentation Index
> Fetch the complete documentation index at: https://docs.qbraid.com/llms.txt
> Use this file to discover all available pages before exploring further.

> ## Agent Instructions
> Prefer the qBraid CLI for programmatic platform actions: pip install 'qbraid-cli>=0.12', then run `qbraid configure` once with an API key from https://account.qbraid.com/account/api-keys.
> When writing Python, prefer the qBraid SDK: `from qbraid.runtime import QbraidProvider` wraps devices, job submission (`device.run()`), and batch groups (`GroupJobSession`).
> Always install the latest packages (pip install -U qbraid qbraid-cli); do not pin versions from memory. qbraid-cli below 0.12.0 is incompatible with the current API.
> Device IDs use the QRN format vendor:provider:type:name (e.g. qbraid:qbraid:sim:qir-sv, rigetti:rigetti:qpu:cepheus-1-108q). Legacy underscore IDs are deprecated.
> The REST API base URL is https://api-v2.qbraid.com/api/v1, authenticated with an X-API-Key header.
> For endpoints without a dedicated wrapper, use `QbraidSessionV1` from `qbraid_core` — an authenticated session (`.get()`/`.post()`) that sets the X-API-Key header. Full spec: https://docs.qbraid.com/openapi-v2.json
> Free simulators cost no credits; QPU and GPU jobs consume credits. Surface the estimated cost to the user before submitting a paid job.
> For account signup, API keys, credits, and end-to-end action recipes, see https://qbraid.com/llms.txt.

# MCP Server

> Manage quantum devices, jobs, environments, and credits from Claude, Claude Code, ChatGPT, or Perplexity.

The qBraid MCP server gives AI clients live access to the qBraid platform
through the [Model Context Protocol](https://modelcontextprotocol.io). Connect
it once and your AI assistant can browse quantum devices, estimate costs,
submit and track jobs, and manage your account.

```text
https://mcp.qbraid.com/mcp
```

The server uses Streamable HTTP transport and authenticates through OAuth
with your qBraid account. No API key is needed.

## Connect your client

<Tabs>
  <Tab title="Claude">
    Custom connectors need a Pro, Max, Team, or Enterprise plan.

    <Steps>
      <Step title="Open the pre-filled connector dialog">
        Click [**Add qBraid to Claude**](https://claude.ai/new?modal=add-custom-connector&connectorName=qBraid&connectorUrl=https%3A%2F%2Fmcp.qbraid.com%2Fmcp#settings/customize-connectors).
        The **Add custom connector** dialog opens with the name and server
        URL already filled in. Claude shows a notice that an external link
        suggested the connector. That is expected. Review the URL and click
        **Add**.

        If the dialog doesn't open, go to **Settings → Connectors → Add
        custom connector** and paste the URL manually:

        ```text
        https://mcp.qbraid.com/mcp
        ```
      </Step>
      <Step title="Sign in">
        Click **Connect** and sign in with your qBraid account.
      </Step>
      <Step title="Enable it in a chat">
        In any conversation, open the **search and tools** menu and toggle
        **qBraid** on. The same connector also works in the Claude desktop
        app.
      </Step>
    </Steps>

  </Tab>
  <Tab title="Claude Code">
    Add the server from your terminal:

    ```bash
    claude mcp add --transport http qbraid https://mcp.qbraid.com/mcp
    ```

    Inside Claude Code, run `/mcp`, select **qbraid**, and complete the OAuth
    sign-in in your browser.

    Verify the connection:

    ```bash
    claude mcp list
    ```

    <Tip>Add `--scope user` to share the server across all your projects.</Tip>

  </Tab>
  <Tab title="ChatGPT">
    qBraid is an official plugin in ChatGPT. Open the
    [**qBraid plugin**](https://chatgpt.com/plugins/plugin_asdk_app_6a9b5284465c8191b6eba9a977d148a8),
    click **Install plugin**, and sign in with your qBraid account.

  </Tab>
  <Tab title="Perplexity">
    Custom connectors need a Pro, Max, or Enterprise plan.

    <Steps>
      <Step title="Open connector settings">
        Go to [Perplexity connector settings](https://www.perplexity.ai/account/connectors)
        and click **+ Custom connector**, then select **Remote**.
      </Step>
      <Step title="Add the server">
        Name it `qBraid` and paste the MCP server URL:

        ```text
        https://mcp.qbraid.com/mcp
        ```

        Choose **OAuth** authentication and **Streamable HTTP** transport.
      </Step>
      <Step title="Sign in">
        Save, then sign in with your qBraid account.
      </Step>
    </Steps>

  </Tab>
  <Tab title="Cursor">
    Click [**Add qBraid to Cursor**](cursor://anysphere.cursor-deeplink/mcp/install?name=qbraid&config=eyJ1cmwiOiJodHRwczovL21jcC5xYnJhaWQuY29tL21jcCJ9)
    to install in one click, or add this to `~/.cursor/mcp.json` yourself:

    ```json
    {
      "mcpServers": {
        "qbraid": { "url": "https://mcp.qbraid.com/mcp" }
      }
    }
    ```

    Cursor detects the server, runs the OAuth sign-in, and picks up the tools
    automatically.

  </Tab>
  <Tab title="VS Code">
    Click [**Add qBraid to VS Code**](https://vscode.dev/redirect/mcp/install?name=qbraid&config=%7B%22name%22%3A%22qbraid%22%2C%22type%22%3A%22http%22%2C%22url%22%3A%22https%3A%2F%2Fmcp.qbraid.com%2Fmcp%22%7D)
    to install in one click, or add this to `.vscode/mcp.json` in your
    workspace:

    ```json
    {
      "servers": {
        "qbraid": { "type": "http", "url": "https://mcp.qbraid.com/mcp" }
      }
    }
    ```

    VS Code prompts for the OAuth sign-in the first time Copilot uses the
    server.

  </Tab>
  <Tab title="Codex">
    Add the server, then sign in:

    ```bash
    codex mcp add qbraid --url https://mcp.qbraid.com/mcp
    codex mcp login qbraid
    ```

    The second command opens the OAuth sign-in in your browser. Verify with
    `codex mcp list`.

  </Tab>
  <Tab title="Other clients">
    Any MCP client that supports remote servers over Streamable HTTP with
    OAuth can connect. Point it at:

    ```text
    https://mcp.qbraid.com/mcp
    ```

    Desktop and command-line clients sign in automatically. Some web-based
    clients need their sign-in address added on our side first. These are
    already added:

    - Grok
    - Le Chat
    - Gemini Enterprise
    - Devin
    - v0
    - Poke
    - Make
    - n8n Cloud

    If sign-in ends on a page with a `redirect_mismatch` error,
    [submit a support request](https://account.qbraid.com/support) with the
    full URL of that page, and we will add your client.

  </Tab>
</Tabs>

## Available tools

<Accordion title="Browse 80+ tools by category">
  | Category          | Example tools                                                                       |
  | ----------------- | ----------------------------------------------------------------------------------- |
  | Quantum devices   | `list_quantum_devices`, `get_device_details`, `get_device_calibrations`             |
  | Quantum jobs      | `submit_quantum_job`, `estimate_job_cost`, `get_job_result`, `get_job_circuit_diagram` |
  | Circuits          | `validate_qasm`, `parse_qasm`, `convert_qasm`, `simulate_circuit`                   |
  | Compute           | `list_compute_profiles`, `start_server`, `stop_server`, `list_compute_instances`    |
  | Environments      | `list_environments`, `get_environment_details`, `build_kernel`                      |
  | Credits & billing | `get_my_credit_balance`, `list_billing_transactions`, `purchase_personal_credits`   |
  | Organizations     | `get_organization_details`, `invite_organization_members`, `transfer_organization_credits` |
  | Learning (qBook)  | `list_qbook_articles`, `create_qbook_course`, `enroll_in_qbook_course`              |
  | Files             | `list_files`, `read_file`                                                           |
  | Support           | `create_support_ticket`, `list_support_tickets`                                     |

Connected clients list the full catalog automatically. Read-only tools run
without confirmation; tools that spend credits or change state report
clearly what they will do first.

</Accordion>

## Example prompts

Once connected, try:

- "List the QPUs online right now and estimate the cost of 1000 shots of a 5-qubit GHZ circuit on the cheapest one."
- "Show my quantum jobs from this week and explain why any failed."
- "How many credits do I have left, and what did I spend the most on this month?"
- "Validate this QASM circuit and draw its diagram."

<Tip>
  Prefer working inside the qBraid platform? [AI
  Chat](https://docs.qbraid.com/v2/ai/user-guide/ai-chat) and [Agent
  Mode](https://docs.qbraid.com/v2/ai/user-guide/agent-mode) use this same MCP server with no setup.
</Tip>
