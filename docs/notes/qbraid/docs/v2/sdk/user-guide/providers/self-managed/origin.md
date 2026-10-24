> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/origin.md](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/origin.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 da2637960ed019238cda8f8421796b5908742ae52e886768ff1f6e5194f58d13.

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

# Origin Quantum (self-managed)

> Run on Origin Quantum simulators and processors with your own QCloud API key, using the OriginProvider.

<Note>
  This page uses `OriginProvider` with your own Origin Quantum account: jobs go straight to
  Origin Quantum, and qBraid isn't involved. See [Self-managed
  providers](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed) for how this differs from [running on
  qBraid](https://docs.qbraid.com/v2/sdk/user-guide/providers/getting-started).
</Note>

<Info>
  API Reference:
  [qbraid.runtime.origin](https://qbraid.github.io/qBraid/stubs/qbraid.runtime.origin.html)
</Info>

## Overview

The `qbraid.runtime.OriginProvider` provides support for OriginQ's quantum computing systems
through the [OriginQ QCloud](https://qcloud.originqc.com.cn/) platform. This means you can write quantum programs using
[PyQPanda3](https://pyqpanda-toturial.readthedocs.io/), and run them on OriginQ's cloud-based simulators and quantum processors,
all from within the [qBraid Runtime framework](https://docs.qbraid.com/v2/sdk/user-guide/runtime/components).

## Getting started

Before you begin, make sure you have:

1. An **OriginQ QCloud** account and API key.
2. Python >= 3.10

### Set up the qBraid-SDK

Install qBraid with the `origin` extra from [PyPI](https://pypi.org/project/qbraid/) using pip:

```bash
pip install 'qbraid[origin]'
```

This installs the required dependency: `pyqpanda3`.

<Info>
  *Note*: The qBraid-SDK requires Python 3.10 or greater. You can check your
  Python version by running `python --version` from the command line.
</Info>

## Authentication

By default, qBraid will look for an environment variable named `ORIGIN_API_KEY`.
Set it from your command line:

```bash
export ORIGIN_API_KEY="your_api_key_here"
```

Alternatively, you can pass your API key directly when creating the provider:

```python
from qbraid.runtime.origin import OriginProvider

provider = OriginProvider(api_key="your_api_key_here")
```

In the examples below, we initialize `OriginProvider()` with no arguments and assume that qBraid
will automatically find your API key from the environment.

## List available devices

Use the `OriginProvider` to list all devices to which you have access:

```python
from qbraid.runtime.origin import OriginProvider

provider = OriginProvider()

devices = provider.get_devices()
print(devices)
```

You can also filter to show only hardware (QPU) devices:

```python
devices = provider.get_devices(hardware_only=True)
```

Get a specific device by its ID:

```python
device = provider.get_device("full_amplitude")

print(device.status())
# <DeviceStatus.ONLINE>
```

### Available simulators

OriginQ provides several cloud-based quantum simulators:

| Simulator ID        | Max Qubits | Description                   |
| ------------------- | ---------- | ----------------------------- |
| `full_amplitude`    | 35         | Full amplitude simulation.    |
| `partial_amplitude` | 68         | Partial amplitude simulation. |
| `single_amplitude`  | 200        | Single amplitude simulation.  |

## Submitting jobs

The `OriginProvider` accepts quantum programs as PyQPanda3 `QProg` objects.

### Create a program

```python
from pyqpanda3.core import QProg, H, CNOT, measure

# Bell state circuit
prog = QProg(2)
q = prog.qubits()
prog << H(q[0]) << CNOT(q[0], q[1]) << measure(0, 0) << measure(1, 1)
```

### Run a job

Use `device.run()` to submit a program:

```python
from pyqpanda3.core import QProg, H, CNOT, measure
from qbraid.runtime.origin import OriginProvider

provider = OriginProvider()
device = provider.get_device("full_amplitude")

prog = QProg(2)
q = prog.qubits()
prog << H(q[0]) << CNOT(q[0], q[1]) << measure(0, 0) << measure(1, 1)

job = device.run(prog, shots=1000)
print(f"Job ID: {job.id}")
```

### Batch submission

Submit multiple programs in a single call:

```python
from pyqpanda3.core import QProg, H, X, measure
from qbraid.runtime.origin import OriginProvider

provider = OriginProvider()
device = provider.get_device("full_amplitude")

prog1 = QProg(1)
prog1 << H(prog1.qubits()[0]) << measure(0, 0)

prog2 = QProg(1)
prog2 << X(prog2.qubits()[0]) << measure(0, 0)

jobs = device.run([prog1, prog2], shots=500)
for job in jobs:
    print(f"Job ID: {job.id}")
```

<Note>
  For simulator backends, batch inputs are submitted as individual jobs. For QPU
  backends, batch inputs are submitted as a single job using the native batch
  API.
</Note>

## Retrieving results

```python
result = job.result()

# Measurement probabilities
print(result.data.get_probabilities())
# {'00': 0.5, '11': 0.5}

# Measurement counts (when available)
print(result.data.measurement_counts)

# Job metadata
print(f"Device: {result.device_id}")
print(f"Job ID: {result.job_id}")
print(f"Success: {result.success}")
```

<Note>
  Depending on the backend, results may be returned as probabilities,
  measurement counts, or both. Use `result.data.get_probabilities()` to retrieve
  probability distributions and `result.data.measurement_counts` for shot-based
  counts.
</Note>

### Check job status

```python
from qbraid.runtime.enums import JobStatus

status = job.status()
print(status)
# <JobStatus.COMPLETED>
```

<Warning>
  Job cancellation is not supported by the OriginQ provider. Calling
  `job.cancel()` will raise an error.
</Warning>

## Full example

A complete end-to-end workflow targeting the full amplitude simulator:

```python
import os
from pyqpanda3.core import QProg, H, CNOT, measure
from qbraid.runtime.origin import OriginProvider

# 1. Set credentials (or export as env var beforehand)
os.environ["ORIGIN_API_KEY"] = "your_api_key_here"

# 2. Initialize provider
provider = OriginProvider()

# 3. Get the target device
device = provider.get_device("full_amplitude")
print(f"Device status: {device.status()}")

# 4. Define a GHZ state circuit
prog = QProg(3)
q = prog.qubits()
prog << H(q[0]) << CNOT(q[0], q[1]) << CNOT(q[1], q[2])
prog << measure(0, 0) << measure(1, 1) << measure(2, 2)

# 5. Submit the job
job = device.run(prog, shots=1000)
print(f"Submitted job: {job.id}")

# 6. Retrieve results
result = job.result()
print(f"Probabilities: {result.data.get_probabilities()}")
# Expected output (approximate): {'000': 0.5, '111': 0.5}
```

## Related links

- [OriginQ QCloud Platform](https://qcloud.originqc.com.cn/)
- [PyQPanda3 Documentation](https://pyqpanda-toturial.readthedocs.io/)
