> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/providers/iqm.md](https://docs.qbraid.com/v2/sdk/user-guide/providers/iqm.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 0d10f9a5569e71da826bd1db8456309c7a3ca91e57c164f9771c97aa04362f32.

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

# IQM

> Run on IQM's Garnet and Emerald superconducting QPUs through qBraid, with only a qBraid API key.

## Devices on qBraid

IQM's superconducting QPUs are on qBraid through two submission paths. Each path has its own device IDs and billing.

| Device ID                     | Device             | Path                                                                      |
| :---------------------------- | :----------------- | :------------------------------------------------------------------------ |
| `aws:iqm:qpu:garnet`          | Garnet, 20 qubits  | [Amazon Braket](#through-amazon-braket) |
| `aws:iqm:qpu:emerald`         | Emerald, 54 qubits | [Amazon Braket](#through-amazon-braket) |
| `openquantum:iqm:qpu:garnet`  | Garnet, 20 qubits  | [Open Quantum](#through-open-quantum)     |
| `openquantum:iqm:qpu:emerald` | Emerald, 54 qubits | [Open Quantum](#through-open-quantum)     |

Check each device's status and price in the [device catalog](https://account.qbraid.com/devices) before you submit.

## Quick start

```python
from qbraid.runtime import QbraidProvider

provider = QbraidProvider()
device = provider.get_device("aws:iqm:qpu:garnet")

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

## Through Amazon Braket

`aws:iqm:` devices go through Amazon Braket, billed in qBraid credits. Write standard gates on qubits `0..n-1`. Braket compiles them to IQM's two native gates, `prx` and `cz`, and chooses the physical qubits. [Amazon Braket](https://docs.qbraid.com/v2/sdk/user-guide/providers/aws#how-braket-compiles-your-circuit) explains the compilation, how your counts are ordered, and how to retrieve the compiled program to see which physical qubits your job ran on.

Garnet and Emerald report live calibration data through qBraid. [Calibrations](https://docs.qbraid.com/v2/sdk/user-guide/providers/calibrations) shows how to fetch it, plot the connectivity graph, and pick the best qubits for your circuit.

`aws:iqm:` devices take [Braket runtime options](https://docs.qbraid.com/v2/sdk/user-guide/providers/aws#braket-runtime-options). For example, IQM's dynamic circuits, with mid-circuit measurement, are a Braket experimental capability:

```python
job = device.run(
    program,
    shots=100,
    runtime_options={"experimental_capabilities": "ALL"},
)
```

## Through Open Quantum

`openquantum:iqm:` devices go through Open Quantum and spend credits from an Open Quantum account linked to qBraid, not qBraid credits. Link the account first, then submit as usual:

```python
device = provider.get_device("openquantum:iqm:qpu:garnet")
job = device.run(bell, shots=100)
```

See [Open Quantum](https://docs.qbraid.com/v2/sdk/user-guide/providers/open-quantum) for linking an account and what these devices accept.

## Related links

- [Run on qBraid](https://docs.qbraid.com/v2/sdk/user-guide/providers/getting-started): installing the SDK and saving your qBraid API key
- [Batch & group jobs](https://docs.qbraid.com/v2/sdk/user-guide/providers/jobs): running several circuits as separate, batch, or group jobs
- [Amazon Braket](https://docs.qbraid.com/v2/sdk/user-guide/providers/aws): compilation, bit ordering, and the compiled program for `aws:*` devices
- [Amazon Braket (self-managed)](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/aws): IQM devices with your own AWS account, including verbatim compilation
- [IQM documentation](https://docs.meetiqm.com/)
