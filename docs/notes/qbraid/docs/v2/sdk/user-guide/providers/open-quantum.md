> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/providers/open-quantum.md](https://docs.qbraid.com/v2/sdk/user-guide/providers/open-quantum.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 d726be1c81c2f44223060228e898c33f54727287fa25b83d8ec249613c763200.

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

# Open Quantum

> How devices with openquantum: IDs work through qBraid: linking an Open Quantum account, how jobs are billed, and what they accept.

<Info>
  Using Open Quantum API credentials of your own, without qBraid? See [Open
  Quantum (self-managed)](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/openquantum).
</Info>

Devices whose ID starts with `openquantum:` run through [Open Quantum](https://www.openquantum.com/), using an Open Quantum account you link to qBraid. You still submit with `QbraidProvider` and your qBraid API key, and jobs appear in your qBraid [Quantum Jobs](https://docs.qbraid.com/v2/account/quantum-jobs). The difference is billing: **these jobs spend your Open Quantum credits, not qBraid credits.**

| Device ID                                | Vendor page                                     |
| :--------------------------------------- | :---------------------------------------------- |
| `openquantum:aqt:qpu:ibex-q1`            | [AQT](https://docs.qbraid.com/v2/sdk/user-guide/providers/aqt)         |
| `openquantum:ionq:qpu:forte-1`           | [IonQ](https://docs.qbraid.com/v2/sdk/user-guide/providers/ionq)       |
| `openquantum:ionq:qpu:forte-enterprise`  | [IonQ](https://docs.qbraid.com/v2/sdk/user-guide/providers/ionq)       |
| `openquantum:iqm:qpu:garnet`             | [IQM](https://docs.qbraid.com/v2/sdk/user-guide/providers/iqm)         |
| `openquantum:iqm:qpu:emerald`            | [IQM](https://docs.qbraid.com/v2/sdk/user-guide/providers/iqm)         |
| `openquantum:rigetti:qpu:cepheus-1-108q` | [Rigetti](https://docs.qbraid.com/v2/sdk/user-guide/providers/rigetti) |

## Before you submit

1. Connect an Open Quantum account in **Account > Profile > Integrations**. See [Open Quantum](https://docs.qbraid.com/v2/account/integrations/openquantum) for the steps.
2. Check that account's Open Quantum credit balance. Buying qBraid credits doesn't add to it.

Then submit as you would to any other device:

```python
from qbraid.runtime import QbraidProvider

provider = QbraidProvider()
device = provider.get_device("openquantum:iqm:qpu:garnet")

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

Programs can be written in any framework qBraid supports. qBraid converts them to OpenQASM before they reach Open Quantum.

## Execution plans

Open Quantum jobs submitted through qBraid run on Open Quantum's **public** execution plan. Requesting any other plan in `runtime_options` is refused before the job is created.

## Related links

- [Open Quantum integration](https://docs.qbraid.com/v2/account/integrations/openquantum): connecting an account, credit types, and troubleshooting
- [Run on qBraid](https://docs.qbraid.com/v2/sdk/user-guide/providers/getting-started): installing the SDK and saving your qBraid API key
- [Open Quantum (self-managed)](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/openquantum): `OpenQuantumProvider` with your own Open Quantum credentials
- [Open Quantum documentation](https://docs.openquantum.com/)
