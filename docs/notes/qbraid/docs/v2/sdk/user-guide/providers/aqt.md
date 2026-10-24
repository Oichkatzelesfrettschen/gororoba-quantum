> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/providers/aqt.md](https://docs.qbraid.com/v2/sdk/user-guide/providers/aqt.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 bbd0bb1c43e682fbc20b3874998db400a6f1afb4f961bb62b512ce16093ee8e3.

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

# AQT

> Run on Alpine Quantum Technologies' IBEX Q1 trapped-ion QPU through qBraid, with only a qBraid API key.

<Info>
  Using your own AQT arnica account? See [AQT
  (self-managed)](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/aqt).
</Info>

## Devices on qBraid

[Alpine Quantum Technologies (AQT)](https://www.aqt.eu/)' IBEX Q1 is a 12-qubit trapped-ion QPU with all-to-all connectivity. It is on qBraid through two submission paths. Each path has its own device ID and billing.

| Device ID                    | Path                                                                      |
| :--------------------------- | :------------------------------------------------------------------------ |
| `openquantum:aqt:qpu:ibex-q1` | [Open Quantum](#through-open-quantum)    |
| `aws:aqt:qpu:ibex-q1`        | [Amazon Braket](#through-amazon-braket) |

Check each device's status and price in the [device catalog](https://account.qbraid.com/devices) before you submit. Not every path is online at once.

## Quick start

```python
from qbraid.runtime import QbraidProvider

provider = QbraidProvider()
device = provider.get_device("aws:aqt:qpu:ibex-q1")

bell = """
OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
bit[2] c;
h q[0];
cx q[0], q[1];
c = measure q;
"""

job = device.run(bell, shots=100)
print(job.result().data.get_counts())
```

Programs can be written in any framework qBraid supports.

## Through Amazon Braket

`aws:aqt:` devices go through Amazon Braket, billed in qBraid credits. Any two qubits can interact, so there is no coupling map to route around: [Calibrations](https://docs.qbraid.com/v2/sdk/user-guide/providers/calibrations) returns an empty edge list for IBEX Q1. These devices take [Braket runtime options](https://docs.qbraid.com/v2/sdk/user-guide/providers/aws#braket-runtime-options), and [Amazon Braket](https://docs.qbraid.com/v2/sdk/user-guide/providers/aws) covers what every Braket device has in common, including how counts are ordered.

## Through Open Quantum

`openquantum:aqt:` devices go through Open Quantum and spend credits from an Open Quantum account linked to qBraid, not qBraid credits. Link the account first, then submit as usual:

```python
device = provider.get_device("openquantum:aqt:qpu:ibex-q1")
job = device.run(bell, shots=100)
```

See [Open Quantum](https://docs.qbraid.com/v2/sdk/user-guide/providers/open-quantum) for linking an account and what these devices accept.

## Related links

- [Run on qBraid](https://docs.qbraid.com/v2/sdk/user-guide/providers/getting-started): installing the SDK and saving your qBraid API key
- [Batch & group jobs](https://docs.qbraid.com/v2/sdk/user-guide/providers/jobs): running several circuits as separate, batch, or group jobs
- [Amazon Braket](https://docs.qbraid.com/v2/sdk/user-guide/providers/aws): how `aws:*` devices compile and order bits
- [AQT (self-managed)](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/aqt): `AQTProvider` with your own arnica account
- [AQT](https://www.aqt.eu/)
