> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/openquantum.md](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/openquantum.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 9d60fcc7b5c8b54bb2823301bb09cf0709ba8b92d51f57381fedc1e8239d0850.

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

# Open Quantum (self-managed)

> Run on Open Quantum's QPUs with your own Open Quantum API credentials, using the OpenQuantumProvider.

<Note>
  This page uses `OpenQuantumProvider` with your own Open Quantum credentials:
  jobs go straight to Open Quantum, and qBraid isn't involved. To run on Open
  Quantum's devices with your qBraid API key and a linked Open Quantum account,
  see [Open Quantum on qBraid](https://docs.qbraid.com/v2/sdk/user-guide/providers/open-quantum).
</Note>

<Info>
  API Reference:
  [qbraid.runtime.openquantum](https://qbraid.github.io/qBraid/stubs/qbraid.runtime.openquantum.html)
</Info>

## Overview

The `qbraid.runtime.OpenQuantumProvider` connects your own [Open Quantum](https://www.openquantum.com/) account to the QPUs it offers, such as IonQ Forte, IQM Garnet and Emerald, Rigetti Cepheus, and AQT IBEX Q1. Write circuits in any qBraid-supported framework; the provider converts them to OpenQASM and submits them, all from within the [qBraid Runtime framework](https://docs.qbraid.com/v2/sdk/user-guide/runtime/components). Jobs are billed to your Open Quantum account.

## Getting started

Before you begin, make sure you have:

1. An [Open Quantum](https://www.openquantum.com/) account, with its Terms of Use accepted. Jobs are refused until they are.
2. An Open Quantum API **client ID** and **client secret**. See Open Quantum's [installation guide](https://docs.openquantum.com/qbraid/installation/).

Install the qBraid SDK. The Open Quantum provider needs no extra:

```bash
pip install qbraid
```

## Authentication

Provide your credentials through environment variables:

```bash
export OPENQUANTUM_CLIENT_ID="your-client-id"
export OPENQUANTUM_CLIENT_SECRET="your-client-secret"
```

Then initialize the provider:

```python
from qbraid.runtime import OpenQuantumProvider

provider = OpenQuantumProvider()
```

You can also pass the credentials directly:

```python
provider = OpenQuantumProvider(client_id="your-client-id", client_secret="your-client-secret")
```

## List available devices

```python
devices = provider.get_devices()
print([device.id for device in devices])
```

Devices are addressed by Open Quantum's short codes, such as `ionq:forte-1`, `iqm:garnet` or `rigetti:cepheus-1-108q`:

```python
device = provider.get_device("iqm:garnet")
```

<Note>
  `device.status()` always reports `ONLINE`: Open Quantum doesn't publish a
  per-device status. Check availability in Open Quantum's own console.
</Note>

## Submitting jobs

```python
circuit = """
OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
bit[2] c;
h q[0];
cx q[0], q[1];
c = measure q;
"""

job = device.run(circuit, shots=100)
print(job.id)
```

Passing a list of circuits submits one Open Quantum job per circuit and returns a list of jobs.

### Execution plan and queue priority

Each Open Quantum job runs on an execution plan and a queue priority, which together set its price. By default the provider chooses the cheapest combination your account is offered. To choose, pass them by name:

```python
job = device.run(circuit, shots=100, execution_plan="PUBLIC", queue_priority="STANDARD")
```

| Option           | Values                                  |
| :--------------- | :-------------------------------------- |
| `execution_plan` | `"PUBLIC"`, `"PRIVATE"`                 |
| `queue_priority` | `"STANDARD"`, `"PRIORITY"`, `"INSTANT"` |

Open Quantum's [credit documentation](https://docs.openquantum.com/concepts/credits/) explains which credits each plan uses.

### Get a quote without submitting

Set `dry_run=True` to get Open Quantum's price quote for every plan and priority, without creating a job:

```python
quote = device.run(circuit, shots=100, dry_run=True)
```

## Retrieving results

```python
result = job.result()
print(result.data.get_counts())
```

`job.status()` reports the job's state, and `job.cancel()` cancels it.

## Configuration options

| Parameter         | Type   | Default                 | Description                                                  |
| :---------------- | :----- | :---------------------- | :----------------------------------------------------------- |
| `shots`           | `int`  | `100`                   | Number of shots.                                             |
| `name`            | `str`  | `"qBraid Job"`          | Job name shown in Open Quantum.                              |
| `execution_plan`  | `str`  | Cheapest offered        | `"PUBLIC"` or `"PRIVATE"`.                                   |
| `queue_priority`  | `str`  | Cheapest offered        | `"STANDARD"`, `"PRIORITY"` or `"INSTANT"`.                   |
| `dry_run`         | `bool` | `False`                 | Return the price quote instead of submitting.                |
| `organization_id` | `str`  | Your first organization | The Open Quantum organization to bill.                       |

## Related links

- [Open Quantum on qBraid](https://docs.qbraid.com/v2/sdk/user-guide/providers/open-quantum): the same devices with your qBraid API key and a linked Open Quantum account
- [Open Quantum documentation](https://docs.openquantum.com/)
- [Open Quantum: backends and targets](https://docs.openquantum.com/qbraid/backends-targets/)
