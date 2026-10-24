> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/providers/getting-started.md](https://docs.qbraid.com/v2/sdk/user-guide/providers/getting-started.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 9883f72efd14410000affa771e03dea83fc1e199d71cae9b98966eb0e5d76d39.

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

# Run on qBraid

> Submit to every quantum device and simulator on qBraid with one qBraid API key, using the QbraidProvider.

<Info>
  API Reference:
  [qbraid.runtime.native](https://qbraid.github.io/qBraid/stubs/qbraid.runtime.native.html)
</Info>

`QbraidProvider` runs your circuits on any device in the [qBraid device catalog](https://account.qbraid.com/devices) with one qBraid API key. You need no account with the hardware vendor. Jobs are billed in qBraid credits and show up in your qBraid [Quantum Jobs](https://docs.qbraid.com/v2/account/quantum-jobs). The one exception is devices with `openquantum:` IDs, which need a linked [Open Quantum](https://docs.qbraid.com/v2/sdk/user-guide/providers/open-quantum) account and spend its credits. This is how most people use the qBraid SDK.

<Tip>
  Already have your own account with a vendor or cloud, such as an IonQ API key
  or an AWS account? See [Self-managed
  providers](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed).
</Tip>

## Devices on qBraid

Each vendor page lists that vendor's device IDs and how to get the most out of them through qBraid:

| Vendor                                                               | What's on qBraid                                                    |
| :------------------------------------------------------------------- | :------------------------------------------------------------------ |
| [Amazon Braket](https://docs.qbraid.com/v2/sdk/user-guide/providers/aws)                    | SV1 and DM1 simulators                                              |
| [AQT](https://docs.qbraid.com/v2/sdk/user-guide/providers/aqt)                              | IBEX Q1 trapped-ion QPU                                             |
| [IonQ](https://docs.qbraid.com/v2/sdk/user-guide/providers/ionq)                            | Forte trapped-ion QPUs and the IonQ simulator, with noise models    |
| [IQM](https://docs.qbraid.com/v2/sdk/user-guide/providers/iqm)                              | Garnet and Emerald superconducting QPUs                             |
| [GPU simulators](https://docs.qbraid.com/v2/sdk/user-guide/providers/gpu-simulators) | State-vector (35 qubits) and tensor-network (500 qubits) simulators |
| [QIR simulator](#basic-usage)                                 | 30-qubit state-vector simulator, used in the examples below         |
| [Quobly](https://docs.qbraid.com/v2/sdk/user-guide/providers/quobly)                        | Alloy Forge silicon spin-qubit emulator                             |
| [QuEra](https://docs.qbraid.com/v2/sdk/user-guide/providers/quera)                          | Aquila neutral-atom analog QPU                                      |
| [Rigetti](https://docs.qbraid.com/v2/sdk/user-guide/providers/rigetti)                      | Cepheus-1-108Q superconducting QPU                                  |

The [device catalog](https://account.qbraid.com/devices) is the live list, with each device's status and price. `provider.get_devices()` returns the same list from Python.

### Submission paths

The first part of a device ID says how qBraid reaches the device. Some vendors are reachable more than one way, and each vendor page has a section per path.

| Device ID starts with | Path                                                         | Billing                                    |
| :-------------------- | :----------------------------------------------------------- | :----------------------------------------- |
| `aws:`                | [Amazon Braket](https://docs.qbraid.com/v2/sdk/user-guide/providers/aws)            | qBraid credits                             |
| `openquantum:`        | [Open Quantum](https://docs.qbraid.com/v2/sdk/user-guide/providers/open-quantum)    | Credits in your linked Open Quantum account |
| Anything else         | Direct to the vendor, or a qBraid simulator                  | qBraid credits                             |

## Installation & Setup

Install the qBraid SDK:

```bash
pip install qbraid
```

<Warning>
  qbraid versions \<0.11 are _not_ compatible with qBraid API V2. See [migration guide](https://docs.qbraid.com/v2/api-reference/rest/migration).

To ensure compatibility with the new platform, use **qbraid** ≥ 0.11.0.

</Warning>

Next, obtain your qBraid API key:

1. Login or create an account at [account.qbraid.com](https://account.qbraid.com/).
2. Navigate to **Account** \> **API Keys** in the left-sidebar, and then click "Create API Key".

<Info>See also: [Account - API Keys](https://docs.qbraid.com/v2/account/api-keys)</Info>

### Save account to disk

Once you have your API key, you can save it locally in a configuration file `~/.qbraid/qbraidrc`, where `~` corresponds to your home (`$HOME`) directory:

<Warning>
  Account credentials are saved in plain text, so only do so if you are using a
  trusted device.
</Warning>

```python
from qbraid.runtime import QbraidProvider

provider = QbraidProvider(api_key='API_KEY')
provider.save_config()
```

Once the account is saved on disk, you can instantiate the provider without any arguments:

```python
provider = QbraidProvider()
```

### Load account from environment variables

Alternatively, the qBraid-SDK can discover credentials from environment variables:

```bash
export QBRAID_API_KEY='QBRAID_API_KEY'
```

## Basic Usage

Given a device "QRN" (qBraid Resource Name), a `QbraidDevice` object can be created as follows:

```python
from qbraid import QbraidProvider

provider = QbraidProvider()
provider.get_devices()
# [<qbraid.runtime.native.device.QbraidDevice('qbraid:qbraid:sim:qir-sv')>]

device = provider.get_device('qbraid:qbraid:sim:qir-sv')

type(device)
# <class 'qbraid.runtime.native.device.QbraidDevice'>
```

From here, class methods are available to get information about the device, execute quantum programs, access the wrapped device object directly, and more.

```python
device.metadata()
# {'device_id': 'qbraid:qbraid:sim:qir-sv',
#  'device_type': 'SIMULATOR',
#  'num_qubits': 30,
#  'status': 'ONLINE',
#  'queue_depth': 0}
```

Then you can submit quantum jobs to the device.

```python
run_input = [qiskit_circuit, braket_circuit, cirq_circuit, qasm3_str]

jobs = device.run(run_input, shots=100)

results = [job.result() for job in jobs]

print(results[0].data.get_counts())
# {'00': 50, '01': 2, '10': 47, '11': 1}
```

See how to visualize these results in the [Visualization](https://docs.qbraid.com/v2/sdk/user-guide/visualization#plot-experimental-results) section.

## Runtime Options

When submitting jobs through the `QbraidProvider`, you can pass provider-specific options using the `runtime_options` keyword argument. These options are forwarded directly to the underlying cloud provider's submission API, giving you access to device-specific features without needing to configure provider credentials yourself.

```python
job = device.run(circuit, shots=100, runtime_options={"key": "value"})
```

The `runtime_options` dictionary is passed through as-is to the provider backend:

- **Amazon Braket** (`aws:*`) devices: options are unpacked as keyword arguments to the Braket `device.run()` call
- **Azure Quantum** (`azure:*`) devices: options are passed as `input_params` to the Azure `device.run()` or `device.submit()` call
- **Other** devices: options are merged into the job submission payload

### qBraid Simulator Examples

Pass a `seed` to make a simulation reproducible. Two runs of the same circuit with the same
seed return identical measurement counts:

```python
device = provider.get_device("qbraid:qbraid:sim:qir-sv")

job = device.run(circuit, shots=100, runtime_options={"seed": 42})

print(job.result().data.get_counts())
# {'00': 48, '11': 52}
```

Submitting the same circuit again with `"seed": 42` returns those same counts. Change the
seed, or leave it out, and the simulator draws a fresh sample on every run.

This is useful for tutorials and course material where the output in the text should match
what the reader sees, for regression tests that assert on exact counts, and for sharing a
result someone else can reproduce.

The GPU simulators, `qbraid:qbraid:sim:gpu-sv` (state vector, up to 35 qubits) and
`qbraid:qbraid:sim:gpu-tn` (tensor network, up to 500 qubits), take `seed` the same way, alongside
their own options, such as `precision`, `method`, and `maxBondDim`:

```python
device = provider.get_device("qbraid:qbraid:sim:gpu-tn")

job = device.run(
    qasm3_str, shots=1000, runtime_options={"method": "mps", "maxBondDim": 256, "seed": 42}
)
```

See [GPU simulators](https://docs.qbraid.com/v2/sdk/user-guide/providers/gpu-simulators) for every option, their
limits, and their daily allowance.

### Vendor-specific options

Every `aws:` device takes the [Braket runtime options](https://docs.qbraid.com/v2/sdk/user-guide/providers/aws#braket-runtime-options). Options specific to a vendor's direct path are on its page: [IonQ](https://docs.qbraid.com/v2/sdk/user-guide/providers/ionq#direct), [Quobly](https://docs.qbraid.com/v2/sdk/user-guide/providers/quobly#runtime-options) and [Rigetti](https://docs.qbraid.com/v2/sdk/user-guide/providers/rigetti#runtime-options).

## Next Steps

- [Managing jobs](https://docs.qbraid.com/v2/sdk/user-guide/providers/managing-jobs): estimating cost, tracking a job, reading its cost and timing, and getting it back later
- [Batch & group jobs](https://docs.qbraid.com/v2/sdk/user-guide/providers/jobs): running several circuits as separate, batch, or group jobs
- [Calibrations](https://docs.qbraid.com/v2/sdk/user-guide/providers/calibrations): live calibration data for choosing qubits
- [Devices on qBraid](#devices-on-qbraid): the page for the vendor you want to run on
