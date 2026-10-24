> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/ibm.md](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/ibm.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 9b475ebd0a33f61959b4ed925b6ca9534f458bcb286ca3544e052a3a518bfd2f.

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

# IBM Quantum (self-managed)

> Install, authenticate, and submit jobs to IBM Quantum backends through the qBraid SDK using the QiskitRuntimeProvider and IBM Cloud CRN.

<Note>
  This page uses `QiskitRuntimeProvider` with your own IBM Quantum account:
  jobs go straight to IBM, and qBraid isn't involved. qBraid doesn't run jobs
  on IBM devices, so this is how to reach them from the qBraid SDK.
</Note>

<Info>
  API Reference:
  [qbraid.runtime.ibm](https://qbraid.github.io/qBraid/stubs/qbraid.runtime.ibm.html)
</Info>

## Installation & Setup

To interface with IBM Quantum backends, install the `qiskit` extra,

```bash
pip install 'qbraid[qiskit]'
```

and configure your [IBM credentials](https://github.com/Qiskit/qiskit-ibm-runtime?tab=readme-ov-file#account-setup).

<Info>
  When using the `ibm_cloud` channel, the `instance` value is your IBM Cloud
  **CRN** (Cloud Resource Name) — a string that looks like
  `crn:v1:bluemix:public:quantum-computing:<region>:a/<account-id>:<service-instance-id>::`.
  It identifies a Qiskit Runtime service instance in your IBM Cloud account and
  is not a qBraid identifier. You can find it in the [IBM Cloud console](https://cloud.ibm.com/)
  under the Qiskit Runtime service instance you want to use. Pair it with your
  IBM Cloud API key as the `token`.
</Info>

## Basic Usage

The `QiskitRuntimeProvider` allows you to easily submit jobs to IBM Quantum devices. There are several ways to initialize the provider:

1. Direct authentication with IBM Cloud:

```python
from qbraid.runtime import QiskitRuntimeProvider

provider = QiskitRuntimeProvider(
    channel="ibm_cloud",
    token="MY_IBM_CLOUD_API_KEY",
    instance="MY_IBM_CLOUD_CRN"
)
```

2. Authentication with IBM Quantum:

```python
provider = QiskitRuntimeProvider(
    channel="ibm_quantum",
    token="MY_IBM_QUANTUM_TOKEN"
)
```

3. Using environment variables:

```shell
export QISKIT_IBM_TOKEN="MY_IBM_CLOUD_API_KEY"
export QISKIT_IBM_INSTANCE="MY_IBM_CLOUD_CRN"
export QISKIT_IBM_CHANNEL="ibm_cloud"
```

4. Using credentials stored in `$HOME/.qiskit/qiskit-ibm.json`

When using environment variables or stored credentials, you can initialize the provider without any arguments:

```python
provider = QiskitRuntimeProvider()
```

Once initialized, you can list available devices and access their information:

```python
# Get list of available devices
provider.get_devices()
# [<qbraid.runtime.ibm.device.QiskitBackend('ibm_brisbane')>,
#  <qbraid.runtime.ibm.device.QiskitBackend('ibm_sherbrooke')>,
#  <qbraid.runtime.ibm.device.QiskitBackend('ibm_fez')>,
#  <qbraid.runtime.ibm.device.QiskitBackend('ibm_kyiv')>,
#  <qbraid.runtime.ibm.device.QiskitBackend('ibm_torino')>,
#  <qbraid.runtime.ibm.device.QiskitBackend('ibm_marrakesh')>]

# Select a specific device
device = provider.get_device('ibm_brisbane')

# View device metadata
device.metadata()
# {'device_id': 'ibm_brisbane',
#  'device_type': 'QPU',
#  'num_qubits': 127,
#  'instance': 'ibm-q/open/main',
#  'max_shots': 100000,
#  'status': 'ONLINE',
#  'queue_depth': 37}
```

Our chosen device is the IBM Osaka Backend, which we will now submit a Qiskit job to.

```python
from qiskit import QuantumCircuit

circuit = QuantumCircuit(2)
circuit.h(0)
job = device.run(circuit, shots=10)
```

So now we have `job` which is of type `QiskitJob`, which inherits from `QuantumJob`. To see the results, we can do the following:

```python
res = job.result()

res.data.get_counts()
# {'00': 6, '11': 4}

res.data.measurements
# array([[1, 1],
#        [0, 0],
#        [0, 0],
#        [1, 1],
#        [0, 0],
#        [1, 1],
#        [0, 0],
#        [1, 1],
#        [0, 0],
#        [0, 0]])
```

See how to visualize these results in the [Visualization](https://docs.qbraid.com/v2/sdk/user-guide/visualization#plot-experimental-results) section.
