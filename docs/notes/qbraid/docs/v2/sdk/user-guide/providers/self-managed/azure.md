> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/azure.md](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/azure.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 d1867b5e651cbdcfd6d2ce857c0b8ca4f51cc98ea714ef1af1c08aec7e6e0f8f.

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

# Azure Quantum (self-managed)

> Run on Azure Quantum devices with your own Azure Quantum workspace, using the AzureQuantumProvider.

<Note>
  This page uses `AzureQuantumProvider` with your own Azure Quantum account: jobs go straight to
  Azure Quantum, and qBraid isn't involved. See [Self-managed
  providers](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed) for how this differs from [running on
  qBraid](https://docs.qbraid.com/v2/sdk/user-guide/providers/getting-started).
</Note>

<Info>
  API Reference:
  [qbraid.runtime.azure](https://qbraid.github.io/qBraid/stubs/qbraid.runtime.azure.html)
</Info>

## Installation & Setup

To interface with Azure Quantum supported devices, install the `azure` extra:

```bash
pip install 'qbraid[azure]'
```

Then, follow the [Azure Quantum setup instructions](https://learn.microsoft.com/en-us/azure/quantum/how-to-create-workspace) to create a workspace and get your credentials.

## Authentication Methods

The `AzureQuantumProvider` integrates with Azure Quantum via the `azure-quantum` package. It connects to an [Azure Quantum Workspace](https://learn.microsoft.com/en-us/python/azure-quantum/azure.quantum.workspace), which manages your quantum resources.

### Using a Connection String

You can authenticate using an **Azure connection string**, which provides a direct way to access your workspace. First, retrieve your connection string by following [these instructions](https://learn.microsoft.com/en-us/azure/quantum/how-to-connect-workspace#copy-the-connection-string). Then, use it to initialize a `Workspace` object and pass it to `AzureQuantumProvider`:

```python
# Authenticate using a connection string
from azure.quantum import Workspace
from qbraid.runtime import AzureQuantumProvider

connection_string = "[Your connection string here]"
workspace = Workspace.from_connection_string(connection_string)

provider = AzureQuantumProvider(workspace=workspace)
```

### Using Environment Variables

To avoid hardcoding credentials in your code, you can store the connection string as an environment variable instead:

```bash
export AZURE_QUANTUM_CONNECTION_STRING="your-connection-string"
```

Then, initialize `AzureQuantumProvider` without passing explicit credentials:

```python
from qbraid.runtime import AzureQuantumProvider

provider = AzureQuantumProvider()  # Uses the environment variable
```

### Related Content

- [Access Keys - Azure Quantum | Microsoft Learn](https://learn.microsoft.com/en-us/azure/quantum/security-manage-access-keys?tabs=tabid-portal#connect-to-your-azure-quantum-workspace-with-a-connection-string)
- [Connect to your Azure Quantum workspace with the azure-quantum Python package](https://learn.microsoft.com/en-us/azure/quantum/how-to-connect-workspace?tabs=tabid-python1%2Ctabid-python)
- [Authenticate Python apps to Azure services by using the Azure SDK for Python](https://learn.microsoft.com/en-us/azure/developer/python/azure-sdk-authenticate)

## Basic Usage

Submit a Quantum Task to an Azure Quantum device using the `AzureQuantumProvider`:

```python
from qbraid.runtime import AzureQuantumProvider

provider = AzureQuantumProvider()  # Uses environment variables

# List available devices
provider.get_devices()
# [<qbraid.runtime.azure.device.AzureDevice('ionq.simulator')>,
#  <qbraid.runtime.azure.device.AzureDevice('ionq.qpu')>,
#  <qbraid.runtime.azure.device.AzureDevice('quantinuum.hqs-lt-s1')>,
#  <qbraid.runtime.azure.device.AzureDevice('quantinuum.hqs-lt-s2')>,
#  <qbraid.runtime.azure.device.AzureDevice('quantinuum.h1-1')>]

# Get a specific device
device = provider.get_device("ionq.simulator")

type(device)
# qbraid.runtime.azure.device.AzureDevice

device.metadata()
# {'device_id': 'ionq.simulator',
#  'device_type': 'SIMULATOR',
#  'num_qubits': 29,
#  'provider_name': 'IonQ',
#  'status': 'ONLINE'}
```

Now that we've instantiated our device, in this case the IonQ simulator on Azure Quantum, we can construct a quantum circuit and submit a task using the `.run` method:

```python
from qiskit import QuantumCircuit

circuit = QuantumCircuit(2)
circuit.h(0)
circuit.cx(0, 1)

job = device.run(circuit, shots=10)
```

We now have `job` which is of type `AzureQuantumTask`, which inherits from `QuantumJob`. To see the results:

```python
res = job.result()

res.data.get_counts()
# {'00': 5, '11': 5}

res.data.measurements
# array([[0, 0],
#        [1, 1],
#        [0, 0],
#        [1, 1],
#        [0, 0],
#        [1, 1],
#        [0, 0],
#        [1, 1],
#        [0, 0],
#        [1, 1]])
```

See how to visualize these results in the [Visualization](https://docs.qbraid.com/v2/sdk/user-guide/visualization#plot-experimental-results) section.

## Supported Providers

Azure Quantum provides access to quantum hardware and simulators from several providers:

- IonQ
- Quantinuum
- Rigetti
- Pasqal

Each provider may have different requirements and capabilities. Refer to the [Azure Quantum documentation](https://learn.microsoft.com/en-us/azure/quantum/) for more details about specific providers.

## Runtime Options

The `AzureQuantumDevice.run()` and `.submit()` methods accept an `input_params` keyword argument
that is passed through to the Azure Quantum backend. Each hardware provider supports different
options.

### Quantinuum

Quantinuum emulators and hardware support several input parameters for controlling
simulation type, noise models, and compiler optimization.

#### Simulator type

Quantinuum emulators support both state-vector (default) and stabilizer simulation:

```python
device = provider.get_device("quantinuum.sim.h2-1e")

# Use the stabilizer simulator (Clifford circuits only)
job = device.run(circuit, shots=100, input_params={"simulator": "stabilizer"})
```

#### Noise model

Disable the emulator's noise model for ideal simulation:

```python
job = device.run(circuit, shots=100, input_params={"error-model": False})
```

Customize individual noise parameters:

```python
job = device.run(
    circuit,
    shots=100,
    input_params={
        "error-params": {
            "p1": 4e-5,
            "p2": 3e-3,
            "p_meas": [3e-3, 3e-3],
            "p_init": 4e-5,
            "p_crosstalk_meas": 1e-5,
            "p_crosstalk_init": 3e-5,
        }
    },
)
```

#### Compiler options

Control TKET optimization level or disable optimization entirely:

```python
# Set optimization level (0, 1, or 2; default is 2)
job = device.run(circuit, shots=100, input_params={"tket-opt-level": 1})

# Disable optimization
job = device.run(circuit, shots=100, input_params={"no-opt": True})
```

See [Quantinuum provider](https://learn.microsoft.com/en-us/azure/quantum/provider-quantinuum) for full details.

### IonQ

IonQ devices on Azure support error mitigation and noise model simulation.

#### Error mitigation

Debiasing is enabled by default on Aria and Forte systems. To explicitly control it:

```python
device = provider.get_device("ionq.qpu.aria-1")

# Disable debiasing
job = device.run(circuit, shots=1000, input_params={"error-mitigation": {"debias": False}})
```

#### Noise model simulation

Run on the IonQ simulator with a hardware noise profile:

```python
device = provider.get_device("ionq.simulator")

job = device.run(
    circuit,
    shots=1000,
    input_params={
        "noise": {
            "model": "aria-1",
            "seed": 42,
        }
    },
)
```

Set `"model": "ideal"` for noiseless simulation (up to 29 qubits).

See [IonQ provider](https://learn.microsoft.com/en-us/azure/quantum/provider-ionq) for full details.

### Rigetti

Rigetti devices on Azure support compiler control and parameter substitutions.

#### Skip quilc compilation

When using native Quil or Quil-T programs, you can bypass the quilc compiler:

```python
device = provider.get_device("rigetti.qpu.ankaa-3")

job = device.submit(quil_program, shots=100, input_params={"skipQuilc": True})
```

#### Parameter substitutions

For parametrized Quil programs, provide values for declared variables:

```python
quil_program = """
DECLARE ro BIT[2]
DECLARE theta REAL[2]
RX(theta[0]) 0
RX(theta[1]) 1
MEASURE 0 ro[0]
MEASURE 1 ro[1]
"""

job = device.submit(
    quil_program,
    shots=100,
    input_params={
        "substitutions": {
            "theta": [[0.0, 3.14], [1.57, 3.14]]
        }
    },
)
```

See [Rigetti provider](https://learn.microsoft.com/en-us/azure/quantum/provider-rigetti) for full details.

### Options Reference

| Provider   | Parameter          | Type   | Description                                  |
| ---------- | ------------------ | ------ | -------------------------------------------- |
| Quantinuum | `simulator`        | `str`  | `"stabilizer"` or `"state-vector"` (default) |
| Quantinuum | `error-model`      | `bool` | Enable/disable noise model (default `True`)  |
| Quantinuum | `error-params`     | `dict` | Custom noise parameters                      |
| Quantinuum | `tket-opt-level`   | `int`  | TKET optimization level (0-2)                |
| Quantinuum | `no-opt`           | `bool` | Disable compiler optimization                |
| IonQ       | `error-mitigation` | `dict` | `{"debias": True/False}`                     |
| IonQ       | `noise`            | `dict` | `{"model": "aria-1", "seed": int}`           |
| Rigetti    | `skipQuilc`        | `bool` | Skip quilc compiler                          |
| Rigetti    | `substitutions`    | `dict` | Parameter values for Quil programs           |

### Via qBraid Runtime API

When submitting jobs through the [QbraidProvider](https://docs.qbraid.com/v2/sdk/user-guide/providers/getting-started), these same
options can be passed via the `runtimeOptions` field. The runtime API forwards them as `input_params`
to the Azure `device.run()` or `device.submit()` call:

```python
from qbraid.runtime import QbraidProvider

provider = QbraidProvider()

device = provider.get_device("azure:quantinuum:sim:h2-1e")

# Use stabilizer simulator with no noise
job = device.run(
    circuit,
    shots=100,
    runtime_options={"simulator": "stabilizer", "error-model": False},
)
```

```python
device = provider.get_device("azure:ionq:sim:simulator")

# Run with hardware noise model
job = device.run(
    circuit,
    shots=1000,
    runtime_options={"noise": {"model": "aria-1", "seed": 42}},
)
```
