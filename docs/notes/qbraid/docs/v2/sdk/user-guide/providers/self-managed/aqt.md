> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/aqt.md](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/aqt.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 d553c6fb8b2d0c56eee062e5c1cb26f28233d6a9e57e29eb6ad92fd9b7cd1947.

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

# AQT (self-managed)

> Run on AQT trapped-ion quantum processors with your own AQT arnica account, using the AQTProvider.

<Note>
  This page uses `AQTProvider` with your own AQT account: jobs go straight to
  AQT, and qBraid isn't involved. To run on AQT with only a qBraid API
  key, see [AQT on qBraid](https://docs.qbraid.com/v2/sdk/user-guide/providers/aqt).
</Note>

<Info>
  API Reference:
  [qbraid.runtime.aqt](https://qbraid.github.io/qBraid/stubs/qbraid.runtime.aqt.html)
</Info>

## Overview

The `qbraid.runtime.AQTProvider` connects your own account to
[Alpine Quantum Technologies (AQT)](https://www.aqt.eu/) trapped-ion quantum systems through the
[arnica cloud](https://www.aqt.eu/products/arnica/). You can write quantum circuits in
[Qiskit](https://www.ibm.com/quantum/qiskit) (or any other qBraid-supported framework); the provider
transpiles them to AQT's native gate set and executes them on AQT hardware such as the **IBEX** QPU,
all from within the [qBraid Runtime framework](https://docs.qbraid.com/v2/sdk/user-guide/runtime/components).

## Getting started

Before you begin, make sure you have:

1. An **AQT arnica** account with machine-to-machine (OIDC client-credentials) access.
2. Your arnica **client ID** and **client secret**.
3. Python >= 3.10

### Set up the qBraid-SDK

Install qBraid with the `aqt` extra from [PyPI](https://pypi.org/project/qbraid/) using pip:

```bash
pip install 'qbraid[aqt]'
```

This installs the required dependencies: `aqt-connector` and `qiskit`.

<Info>
  *Note*: The qBraid-SDK requires Python 3.10 or greater. You can check your
  Python version by running `python --version` from the command line.
</Info>

## Authentication

The `AQTProvider` authenticates to the arnica cloud non-interactively using OIDC **client
credentials** (machine-to-machine) — the interactive device/login flow is never triggered. Provide
your credentials via environment variables:

```bash
export AQT_CLIENT_ID="your-client-id"
export AQT_CLIENT_SECRET="your-client-secret"
```

Then initialize the provider:

```python
from qbraid.runtime.aqt import AQTProvider

provider = AQTProvider()
```

You can also pass credentials — or a pre-obtained access token — directly instead of using
environment variables:

```python
# client-credentials
provider = AQTProvider(client_id="your-client-id", client_secret="your-client-secret")

# or a pre-obtained bearer token
provider = AQTProvider(access_token="your-access-token")
```

## List available devices

Use the `AQTProvider` to list the devices to which you have access:

```python
from qbraid.runtime.aqt import AQTProvider

provider = AQTProvider()

devices = provider.get_devices()
print(devices)
```

AQT devices are addressed by a `"<workspace>/<resource>"` identifier. Get a specific device by its id:

```python
device = provider.get_device("<workspace>/<resource>")

print(device.status())
# <DeviceStatus.ONLINE>
```

<Note>
  Use `get_devices()` to discover the `"<workspace>/<resource>"` ids you have access to — for
  example, the **IBEX** QPU is exposed under its arnica workspace and resource.
</Note>

## Submitting jobs

The `AQTProvider` accepts circuits written in any qBraid-supported framework. `device.run()`
transpiles the circuit to AQT's native basis (`RZ`, `R`, `RXX`) via the `qiskit -> aqt_connector`
conversion, then submits it.

<Note>
  AQT enforces per-job limits: up to **2000 shots** per job and up to **2000
  operations** (gates) per circuit. Jobs that exceed either limit are rejected.
  The **IBEX** QPU provides **12 qubits**; a circuit wider than the device is
  rejected before submission.
</Note>

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
from qbraid.runtime.aqt import AQTProvider

provider = AQTProvider()
device = provider.get_device("<workspace>/<resource>")

circuit = QuantumCircuit(2)
circuit.h(0)
circuit.cx(0, 1)
circuit.measure_all()

job = device.run(circuit, shots=1000)
print(f"Job ID: {job.id}")
```

### Batch submission

Submit multiple circuits in a single call. All circuits are bundled into one arnica job:

```python
from qiskit import QuantumCircuit
from qbraid.runtime.aqt import AQTProvider

provider = AQTProvider()
device = provider.get_device("<workspace>/<resource>")

qc1 = QuantumCircuit(1)
qc1.h(0)
qc1.measure_all()

qc2 = QuantumCircuit(2)
qc2.h(0)
qc2.cx(0, 1)
qc2.measure_all()

job = device.run([qc1, qc2], shots=500)
print(f"Job ID: {job.id}")
```

<Note>
  When submitting a list of circuits, all are executed as a single batch job on
  arnica. The returned measurement counts will be a list of dictionaries, one
  per circuit.
</Note>

## Retrieving results

```python
result = job.result()

# Measurement counts (little-endian: qubit 0 is the rightmost bit)
print(result.data.get_counts())
# {'00': 512, '11': 488}

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

### Execution time

Retrieve the wall-clock run time (in seconds) for a completed job:

```python
print(f"Execution time: {job.execution_time_s()} seconds")
```

<Note>
  `execution_time_s()` is derived from the arnica `timing_data` as the `ongoing`
  → `finished` span (the time the job spent running, excluding queue wait). It
  returns `None` until the job has completed, and raises `AQTJobError` if a
  completed job's timing data is incomplete.
</Note>

## Configuration options

The `device.run()` method accepts the following keyword arguments:

| Parameter | Type  | Default    | Description                                         |
| --------- | ----- | ---------- | --------------------------------------------------- |
| `shots`   | `int` | `100`      | Number of measurement shots per circuit (max 2000). |
| `name`    | `str` | `"qbraid"` | Optional human-readable job label.                  |

Credentials are configured via environment variables:

| Variable            | Description                                                |
| ------------------- | ---------------------------------------------------------- |
| `AQT_CLIENT_ID`     | OIDC client ID for the arnica client-credentials flow.     |
| `AQT_CLIENT_SECRET` | OIDC client secret for the arnica client-credentials flow. |

## Full example

A complete end-to-end workflow submitting a GHZ state to an AQT device:

```python
from qiskit import QuantumCircuit
from qbraid.runtime.aqt import AQTProvider

# 1. Initialize provider (reads AQT_CLIENT_ID / AQT_CLIENT_SECRET from the environment)
provider = AQTProvider()

# 2. Get a device by its "<workspace>/<resource>" id
device = provider.get_device("<workspace>/<resource>")
print(f"Device status: {device.status()}")

# 3. Define a GHZ state circuit
circuit = QuantumCircuit(3)
circuit.h(0)
circuit.cx(0, 1)
circuit.cx(1, 2)
circuit.measure_all()

# 4. Submit the job
job = device.run(circuit, shots=1000)
print(f"Submitted job: {job.id}")

# 5. Retrieve results
result = job.result()
print(f"Counts: {result.data.get_counts()}")
# Expected output (approximate): {'000': ~500, '111': ~500}
```

## Related links

- [Alpine Quantum Technologies (AQT)](https://www.aqt.eu/)
- [AQT arnica Cloud](https://www.aqt.eu/products/arnica/)
- [AQT arnica API Reference](https://arnica.aqt.eu/api/v1/docs)
- [AQT Quantum SDK Connectors](https://www.aqt.eu/quantum-sdk-connectors/)
