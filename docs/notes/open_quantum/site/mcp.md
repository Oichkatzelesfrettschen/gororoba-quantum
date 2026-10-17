> Full piece: [https://www.openquantum.com/mcp](https://www.openquantum.com/mcp)
> Retrieved 2026-10-17T05:09Z by scripts/capture_oq_docs.py --site (urllib, pandoc);
> fetched HTML sha256 eaba47615c715b4f692cbf757d277825bbdd7895972b4542f9f70c4b90fb1b02.

# Run Quantum from Your AI Agent

Connect Claude, ChatGPT, Gemini, Grok, Cursor, and any MCP client to Open Quantum. Your agent can discover backends, submit circuits, and read results on real QPUs, using your own SDK key with credentials that stay on your machine.

[Get Started Free](https://www.openquantum.com/signup)[Read the Docs](https://docs.openquantum.com/mcp/overview/)

Your agent + Open Quantum MCP

## Works with the agents you already use

One server, every major MCP client. Pick your tool and follow its guide to add the Open Quantum server.

[](https://docs.anthropic.com/en/docs/claude-code/mcp)

ClaudeSetup guide[](https://platform.openai.com/docs/mcp)

ChatGPTSetup guide[](https://docs.cursor.com/context/mcp)

CursorSetup guide[](https://code.visualstudio.com/docs/copilot/chat/mcp-servers)

GitHub CopilotSetup guide[](https://google-gemini.github.io/gemini-cli/docs/tools/mcp-server.html)

Gemini CLISetup guide[](https://modelcontextprotocol.io/clients)

GrokSetup guide[](https://docs.windsurf.com/windsurf/cascade/mcp)

WindsurfSetup guide[](https://zed.dev/docs/ai/mcp)

ZedSetup guide[](https://docs.cline.bot/mcp/configuring-mcp-servers)

ClineSetup guide

Using something else? [Any client that speaks MCP works too.](https://modelcontextprotocol.io/clients)

## Quantum computing, as a tool your agent can call

`openquantum-mcp` is a local MCP server built on the Open Quantum Core SDK. It exposes the whole job lifecycle as MCP tools, so a compatible agent can go from "run this circuit on a real QPU" to summarized results without you hand-writing submission and polling code each time.

There is a single server for every client. Your agent talks to it over stdio, and it talks to Open Quantum with your SDK key. The key lives in the server process on your machine, so your secret is never handed to the agent vendor.

The server

Package  
openquantum-mcp

Command  
openquantum-mcp

Transport  
stdio (local)

Requires  
Python 3.10+

## What your agent can do

### Discover

List organizations, backends, and credit balances so the agent knows what is online and what it costs.

### Prepare & quote

Prepare a job and inspect the exact credit quote before anything is spent. No surprise charges.

### Submit

Send OpenQASM circuits to real QPUs from IonQ, Rigetti, IQM, and AQT, or to simulators.

### Wait & summarize

Poll long queues until completion, then summarize measurement counts and fetch calibration on demand.

## Example prompts

“Which quantum backends are online, and how many credits do I have?”

You have 50 Spark credits. Six backends are online: IonQ Forte-1 (36 qubits), Rigetti Cepheus-1 (108), IQM Garnet (20) and Emerald (54), AQT IBEX-Q1 (12), plus the Quantum Rings simulator.

“Run a 2-qubit Bell state on IonQ Forte-1 with 1024 shots. Show me the cost before you submit.”

Prepared on ionq:forte-1. Quote: 2 credits on the Public plan (Spark-eligible). Submitting now. Results: {"00": 503, "11": 521}.

“Submit this GHZ circuit to the cheapest online simulator and summarize the counts.”

Ran on the Quantum Rings simulator (free). Counts: {"000": 512, "111": 512}. A clean 3-qubit GHZ state.

“Did my last job finish? Summarize the measurement results.”

Job oq_7f3c completed on rigetti:cepheus-1. Top outcomes: 0000 at 41% and 1111 at 39%, with the rest spread across noise. Calibration is available on request.

## Spend stays under your control

- Quote before spend. Preparing a job returns the exact credit estimate and creates nothing. The agent sees the cost first.
- Free credits first. The auto plan prefers Public so your Spark credits apply when available, then the lowest cost option.
- Private spend is opt-in. Jobs that draw on Full credits require an explicit confirmation flag, so an agent cannot quietly escalate cost.
- Fully attributed. Every job is tagged as submitted via MCP, so you can see agent activity in your dashboard.

## Connect your agent in two steps

Install the server, then point your MCP client at it with your SDK key. The config below works for most clients; see each client's setup guide above for the exact location.

``` bash
pip install openquantum-mcp
```

``` json
{
  "mcpServers": {
    "openquantum": {
      "command": "openquantum-mcp",
      "env": {
        "OPENQUANTUM_CLIENT_ID": "s_your_client_id",
        "OPENQUANTUM_CLIENT_SECRET": "your_client_secret"
      }
    }
  }
}
```

[Get Your SDK Key](https://www.openquantum.com/signup)[Client Setup Guide](https://docs.openquantum.com/mcp/client-setup/)

## Go deeper

[](https://docs.openquantum.com/mcp/overview/)

### Overview

What the MCP server is and how it fits together.

Read[](https://docs.openquantum.com/mcp/client-setup/)

### Client setup

Wire up Claude, Cursor, GitHub Copilot, and other hosts.

Read[](https://docs.openquantum.com/mcp/tools/)

### Tools & spend policy

Every tool the server exposes and the credit safeguards.

Read

[](https://www.openquantum.com/signup)

\$50 Free Compute Credits

Every new Open Quantum account includes \$50 in free credits, refreshed every 90 days. Wire up your agent and run on real hardware at no cost, no credit card required.

Sign Up Free

## Frequently Asked Questions

What is the Model Context Protocol (MCP)?

Which agents and IDEs can I use?

What is the Open Quantum MCP server?

Will an agent spend my credits without asking?

Where do my credentials live?

How much does it cost?

What do I need to get started?
