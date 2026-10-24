> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/qudora.md](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/qudora.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 c014846866aab372987a4f08140821f403a8f7feaa0b13ea64f4b4c5573ab682.

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

# QUDORA (self-managed)

> Run on QUDORA trapped-ion systems with your own QUDORA Cloud token, using the QudoraProvider.

<Note>
  This page uses `QudoraProvider` with your own QUDORA account: jobs go straight to
  QUDORA, and qBraid isn't involved. See [Self-managed
  providers](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed) for how this differs from [running on
  qBraid](https://docs.qbraid.com/v2/sdk/user-guide/providers/getting-started).
</Note>

<Info>
  API Reference:
  [qbraid.runtime.qudora](https://qbraid.github.io/qBraid/stubs/qbraid.runtime.qudora.html)
</Info>

## Overview

The `qbraid.runtime.QudoraProvider` connects your own account to
[QUDORA](https://www.qudora.com/) trapped-ion quantum systems through the QUDORA Cloud REST API
(`https://api.qudora.com`). You can write quantum circuits in
[Qiskit](https://www.ibm.com/quantum/qiskit), [Cirq](https://quantumai.google/cirq), or any other
qBraid-supported framework; the provider transpiles them to OpenQASM and submits the program string
directly to the QUDORA Cloud, which compiles it server-side — all from within the
[qBraid Runtime framework](https://docs.qbraid.com/v2/sdk/user-guide/runtime/components).

This is a direct-REST, dependency-free integration: there is no vendor SDK to install. QUDORA's Cloud
API accepts OpenQASM 2 and OpenQASM 3 strings directly, and the `language` is auto-detected from each
program's header.

<Note>
  QUDORA devices are also available through the **qBraid platform** — accessed
  with `QbraidProvider` as a separate access point with its own device ids. The
  current QUDORA backends are simulators and are free to use — no qBraid credits
  are charged. Through the platform, a list of circuits runs as one job with
  `device.run(circuits, as_batch=True)`; see [Batch
  Jobs](https://docs.qbraid.com/v2/sdk/user-guide/providers/jobs#batch-jobs).
</Note>

## Getting started

Before you begin, make sure you have:

1. A **QUDORA Cloud** account.
2. A QUDORA API token (a Bearer token generated from the QUDORA cloud console).
3. Python >= 3.10

### Set up the qBraid-SDK

Install qBraid from [PyPI](https://pypi.org/project/qbraid/) using pip:

```bash
pip install qbraid
```

QUDORA support requires no extra dependencies — OpenQASM 2 / OpenQASM 3 transpilation and `pyqasm`
validation are part of the qBraid core.

<Info>
  *Note*: The qBraid-SDK requires Python 3.10 or greater. You can check your
  Python version by running `python --version` from the command line.
</Info>

## Authentication

The `QudoraProvider` authenticates to the QUDORA Cloud with a **Bearer API token**. Provide it via an
environment variable:

```bash
export QUDORA_API_TOKEN="your-api-token"
```

Then initialize the provider:

```python
from qbraid.runtime.qudora import QudoraProvider

provider = QudoraProvider()
```

You can also pass the token directly instead of using the environment variable, and optionally
override the API base URL:

```python
# token passed directly
provider = QudoraProvider(token="your-api-token")

# token with a custom base URL (defaults to https://api.qudora.com)
provider = QudoraProvider(token="your-api-token", base_url="https://api.qudora.com")
```

<Note>
  The base URL can also be set with the `QUDORA_BASE_URL` environment variable.
  When neither the argument nor the variable is provided, it defaults to
  `https://api.qudora.com`.
</Note>

## List available devices

Use the `QudoraProvider` to list the devices to which you have access:

```python
from qbraid.runtime.qudora import QudoraProvider

provider = QudoraProvider()

devices = provider.get_devices()
print(devices)
```

QUDORA devices are addressed by the backend's **username**. Get a specific device by its id:

```python
device = provider.get_device("<device-id>")

print(device.status())
# <DeviceStatus.ONLINE>
```

<Note>
  Use `get_devices()` to discover the exact device ids you have access to.
  QUDORA's current backends are trapped-ion **simulators** — **Qamelion** (32
  qubits) and the **QVLS-Q1 Emulator** (20 qubits). See [QUDORA's available
  backends](https://cloud.qudora.com/main/documentation#4-available-backends)
  for the up-to-date list and their specifications.
</Note>

## Submitting jobs

The `QudoraProvider` accepts circuits written in any qBraid-supported framework. `device.run()`
transpiles the circuit to an OpenQASM string, validates it with `pyqasm`, and submits it to the
QUDORA Cloud, which compiles it server-side.

### Create a circuit

```python
from qiskit import QuantumCircuit

# Bell state circuit
circuit = QuantumCircuit(2)
circuit.h(0)
circuit.cx(0, 1)
circuit.measure_all()
```

### Run a job

Use `device.run()` to transpile and submit a circuit:

```python
from qiskit import QuantumCircuit
from qbraid.runtime.qudora import QudoraProvider

provider = QudoraProvider()
device = provider.get_device("<device-id>")

circuit = QuantumCircuit(2)
circuit.h(0)
circuit.cx(0, 1)
circuit.measure_all()

job = device.run(circuit, shots=100)
print(f"Job ID: {job.id}")
```

### Batch submission

Submit multiple circuits in a single call. All circuits are bundled into one QUDORA job, subject to
the device's `max_programs_per_job` limit:

```python
from qiskit import QuantumCircuit
from qbraid.runtime.qudora import QudoraProvider

provider = QudoraProvider()
device = provider.get_device("<device-id>")

qc1 = QuantumCircuit(1)
qc1.h(0)
qc1.measure_all()

qc2 = QuantumCircuit(2)
qc2.h(0)
qc2.cx(0, 1)
qc2.measure_all()

job = device.run([qc1, qc2], shots=100)
print(f"Job ID: {job.id}")
```

<Note>
  All programs in a single batch job must use the same OpenQASM version. When
  submitting a list of circuits, the returned measurement counts will be a list
  of dictionaries, one per circuit.
</Note>

### Simulator noise settings

QUDORA's simulators accept per-job noise parameters through the `backend_settings` argument (see
[QUDORA's noise model details](https://cloud.qudora.com/main/documentation#appendix--noise-model-details)
for what each parameter controls). The accepted keys — and their defaults — are exposed by each
backend's settings schema, which you can inspect with `device.available_settings()`:

```python
# Discover the accepted backend settings and their defaults for this device
print(device.available_settings())
```

Pass the settings you want to override to `device.run()`:

```python
job = device.run(
    circuit,
    shots=100,
    backend_settings={
        "measurement_error_probability": 0.01,
        "single_qubit_gate_noise_strength": 0.001,
        "two_qubit_gate_noise_strength": 0.01,
        "dephasing_T2_time": 1.0,
    },
)
```

<Note>
  Use `device.available_settings()` to see which noise parameters a given
  backend supports and their default values, rather than assuming a fixed set of
  keys.
</Note>

## Retrieving results

```python
result = job.result()

# Measurement counts
print(result.data.get_counts())
# {'00': 51, '11': 49}

# Job metadata
print(f"Device: {result.device_id}")
print(f"Job ID: {result.job_id}")
print(f"Success: {result.success}")
```

### Check job status

```python
from qbraid.runtime.enums import JobStatus

status = job.status()
print(status)
# <JobStatus.COMPLETED>
```

### Cancel a job

```python
job.cancel()
```

<Note>
  Cancellation targets queued or ongoing jobs. Jobs already in a terminal state
  (`COMPLETED`, `FAILED`, `CANCELLED`) cannot be cancelled.
</Note>

## Configuration options

The `device.run()` method accepts the following keyword arguments:

| Parameter          | Type   | Default    | Description                                                               |
| ------------------ | ------ | ---------- | ------------------------------------------------------------------------- |
| `shots`            | `int`  | `100`      | Number of measurement shots per program.                                  |
| `name`             | `str`  | `"qbraid"` | Optional human-readable job label.                                        |
| `backend_settings` | `dict` | `{}`       | Optional QUDORA backend settings, such as the simulator noise parameters. |

Credentials are configured via environment variables:

| Variable           | Description                                                                     |
| ------------------ | ------------------------------------------------------------------------------- |
| `QUDORA_API_TOKEN` | Bearer API token for the QUDORA Cloud, generated from the QUDORA cloud console. |
| `QUDORA_BASE_URL`  | Optional base URL override (defaults to `https://api.qudora.com`).              |

## Full example

A complete end-to-end workflow submitting a GHZ state to a QUDORA device:

```python
from qiskit import QuantumCircuit
from qbraid.runtime.qudora import QudoraProvider

# 1. Initialize provider (reads QUDORA_API_TOKEN from the environment)
provider = QudoraProvider()

# 2. Get a device by its id (discover ids with provider.get_devices())
device = provider.get_device("<device-id>")
print(f"Device status: {device.status()}")

# 3. Define a GHZ state circuit
circuit = QuantumCircuit(3)
circuit.h(0)
circuit.cx(0, 1)
circuit.cx(1, 2)
circuit.measure_all()

# 4. Submit the job
job = device.run(circuit, shots=100)
print(f"Submitted job: {job.id}")

# 5. Retrieve results
result = job.result()
print(f"Counts: {result.data.get_counts()}")
# Expected output (approximate): {'000': ~50, '111': ~50}
```

## Related links

- [QUDORA](https://www.qudora.com/)
- [QUDORA Cloud Documentation](https://cloud.qudora.com/main/documentation)
- [QUDORA Available Backends](https://cloud.qudora.com/main/documentation#4-available-backends)
- [QUDORA Noise Model Details](https://cloud.qudora.com/main/documentation#appendix--noise-model-details)
- [QUDORA Cloud Console](https://cloud.qudora.com/)
- [QUDORA REST API Reference](https://api.qudora.com/docs)
