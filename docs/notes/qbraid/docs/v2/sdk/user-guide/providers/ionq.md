> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/providers/ionq.md](https://docs.qbraid.com/v2/sdk/user-guide/providers/ionq.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 dbba19777e76e452de257acf5a75f373daa1410267d4df1ee0fee43055fc91cf.

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

# IonQ

> Run on IonQ's Forte trapped-ion QPUs and the IonQ simulator through qBraid, with only a qBraid API key.

<Info>
  Using your own IonQ API key? See [IonQ
  (self-managed)](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/ionq).
</Info>

## Devices on qBraid

IonQ's trapped-ion systems are on qBraid through three submission paths. Each path has its own device IDs, billing, and runtime options.

| Device ID                               | Device                    | Path                                    |
| :-------------------------------------- | :------------------------ | :-------------------------------------- |
| `ionq:ionq:sim:simulator`               | IonQ simulator, 29 qubits | [Direct](#direct)                       |
| `ionq:ionq:qpu:forte-1`                 | Forte-1, 36 qubits        | [Direct](#direct)                       |
| `aws:ionq:qpu:forte-1`                  | Forte-1, 36 qubits        | [Amazon Braket](#through-amazon-braket) |
| `aws:ionq:qpu:forte-enterprise-1`       | Forte Enterprise-1        | [Amazon Braket](#through-amazon-braket) |
| `openquantum:ionq:qpu:forte-1`          | Forte-1, 36 qubits        | [Open Quantum](#through-open-quantum)   |
| `openquantum:ionq:qpu:forte-enterprise` | Forte Enterprise          | [Open Quantum](#through-open-quantum)   |

Check each device's status and price in the [device catalog](https://account.qbraid.com/devices) before you submit. Not every path is online at once.

## Quick start

Start on the simulator, which runs the same programs as the QPUs:

```python
from qbraid.runtime import QbraidProvider

provider = QbraidProvider()
device = provider.get_device("ionq:ionq:sim:simulator")

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

To run on a QPU, change the device ID. Programs can be written in any framework qBraid supports; qBraid converts them to OpenQASM before they reach IonQ.

## Direct

`ionq:` devices go from qBraid straight to IonQ, billed in qBraid credits. They accept these `runtime_options`, which qBraid passes to IonQ unchanged:

| Option             | Effect                                                                 |
| :----------------- | :--------------------------------------------------------------------- |
| `noise`            | On the simulator, a hardware noise model and optional seed. See below. |
| `error_mitigation` | IonQ's error mitigation settings, such as debiasing, on QPU jobs.      |
| `metadata`         | Key-value metadata stored with the IonQ job.                           |

Run the simulator with a hardware noise profile:

```python
job = device.run(
    bell,
    shots=1000,
    runtime_options={"noise": {"model": "aria-1", "seed": 42}},
)
```

Noise models include `ideal`, `harmony`, `harmony-1`, `harmony-2`, `aria-1`, `aria-2`, `forte-1` and `forte-enterprise-1`. See IonQ's guide to [simulation with noise models](https://docs.ionq.com/guides/simulation-with-noise-models).

## Through Amazon Braket

`aws:ionq:` devices go through Amazon Braket, billed in qBraid credits. They take [Braket runtime options](https://docs.qbraid.com/v2/sdk/user-guide/providers/aws#braket-runtime-options) rather than the direct options above. Debiasing, for example, is set with `device_parameters`:

```python
device = provider.get_device("aws:ionq:qpu:forte-1")

job = device.run(
    bell,
    shots=2500,  # Braket requires at least 2500 shots for debiasing
    runtime_options={"device_parameters": {"errorMitigation": "Debias"}},
)
```

[Amazon Braket](https://docs.qbraid.com/v2/sdk/user-guide/providers/aws) covers what every Braket device has in common, including how counts are ordered.

## Through Open Quantum

`openquantum:ionq:` devices go through Open Quantum and spend credits from an Open Quantum account linked to qBraid, not qBraid credits. Link the account first, then submit as usual:

```python
device = provider.get_device("openquantum:ionq:qpu:forte-1")
job = device.run(bell, shots=100)
```

See [Open Quantum](https://docs.qbraid.com/v2/sdk/user-guide/providers/open-quantum) for linking an account and what these devices accept.

## Related links

- [Run on qBraid](https://docs.qbraid.com/v2/sdk/user-guide/providers/getting-started): installing the SDK and saving your qBraid API key
- [Batch & group jobs](https://docs.qbraid.com/v2/sdk/user-guide/providers/jobs): running several circuits as separate, batch, or group jobs
- [IonQ (self-managed)](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/ionq): `IonQProvider` with your own IonQ API key, including IonQ's native gates
- [IonQ documentation](https://docs.ionq.com/)
