> Full piece: [https://docs.qbraid.com/v2/lab/user-guide/quantum-devices.md](https://docs.qbraid.com/v2/lab/user-guide/quantum-devices.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 f8e77207e4d69e7a92d9507dac82d3421aa26b3923f754b12a1d9cea8789643d.

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

# Quantum Devices

> Monitor availability, status, and specifications of quantum devices and simulators.

The Quantum Devices sidebar provides a real-time view of quantum hardware and simulators available through qBraid.
Open it by clicking the **Devices** icon in the top-right of the Lab console.

## Device list

The sidebar displays all available quantum devices with their provider, name, and current status.
Click the **Search devices** bar to filter by device name.

<div
  style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
>
  <img
    src="/v2/lab/_static/devices_screenshot.png"
    alt="Quantum Devices sidebar with expanded device details"
    width="100%"
  />
</div>

## Status indicators

The colored dot next to each device name indicates its current status:

| Color | Status          | Meaning                                                                                 |
| ----- | --------------- | --------------------------------------------------------------------------------------- |
| Green | **ONLINE**      | Fully operational — accepting and executing jobs                                        |
| Grey  | **UNAVAILABLE** | Online but not currently executing — jobs are queued until the next availability window |
| Red   | **OFFLINE**     | Not operational or not accepting jobs — expected to return                              |
| Red   | **RETIRED**     | Permanently decommissioned                                                              |

Hover over the status dot to see a tooltip with the exact status label.

## Pricing

For detailed pricing information on available devices, visit the [Pricing](https://docs.qbraid.com/v2/home/pricing) page.

<Note>
  qBraid does not provide direct access to IBM devices. To run quantum jobs on
  IBM hardware, you must use your own IBM credentials. Jobs submitted to IBM
  devices will not appear in the Quantum Jobs sidebar.
</Note>

<Tip>
  For more details on submitting and managing quantum jobs, visit the [Quantum
  Jobs](https://docs.qbraid.com/v2/lab/user-guide/quantum-jobs) page.
</Tip>
