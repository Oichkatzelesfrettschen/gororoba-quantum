> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/qperfect.md](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/qperfect.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 f444f3692c806a73aa03c2ce871b8325b056744ba649086523ab764adbeacb88.

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

# QPerfect (self-managed)

> Run on QPerfect's MIMIQ cloud emulator with your own MIMIQ account, using the QPerfectProvider.

<Note>
  This page uses `QPerfectProvider` with your own QPerfect account: jobs go straight to
  QPerfect, and qBraid isn't involved. See [Self-managed
  providers](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed) for how this differs from [running on
  qBraid](https://docs.qbraid.com/v2/sdk/user-guide/providers/getting-started).
</Note>

<Info>
  API Reference:
  [qbraid.runtime.qperfect](https://qbraid.github.io/qBraid/stubs/qbraid.runtime.qperfect.html)
</Info>

## Overview

The `qbraid.runtime.QPerfectProvider` connects your own account to
[QPerfect](https://www.qperfect.io/)'s **MIMIQ** high-performance quantum emulator through the MIMIQ
cloud. You can write quantum circuits in [Qiskit](https://www.ibm.com/quantum/qiskit),
[Cirq](https://quantumai.google/cirq), or any other qBraid-supported framework; the provider
transpiles them to a native MIMIQ circuit and submits them to the MIMIQ cloud — all from within the
[qBraid Runtime framework](https://docs.qbraid.com/v2/sdk/user-guide/runtime/components).

Unlike a raw-REST integration, MIMIQ is driven through QPerfect's own
[`mimiqcircuits`](https://pypi.org/project/mimiqcircuits/) SDK. The provider holds an authenticated
MIMIQ connection and forwards each job to it. Circuit conversion is handled by the transpiler's
`qiskit -> mimiq` edge (backed by the [`mimiq-qiskit`](https://pypi.org/project/mimiq-qiskit/)
package), so any qBraid-supported source reaches MIMIQ — and a native `mimiqcircuits.Circuit` passes
through unchanged, preserving noise models and MIMIQ-specific operations.

<Note>
  The MIMIQ emulator is also available through the **qBraid platform** —
  accessed with `QbraidProvider` as a separate access point with its own device
  id. The MIMIQ backend is a simulator and is free to use — no qBraid credits
  are charged.
</Note>

## Getting started

Before you begin, make sure you have:

1. A **QPerfect MIMIQ** account (email and password).
2. Python >= 3.10

### Set up the qBraid-SDK

QPerfect support ships as an optional extra. Install qBraid from
[PyPI](https://pypi.org/project/qbraid/) with the `qperfect` extra using pip:

```bash
pip install 'qbraid[qperfect]'
```

The `qperfect` extra pulls in the `mimiq-qiskit` converter (and, transitively, `mimiqcircuits` and
`qiskit`) that the provider and the `qiskit -> mimiq` transpiler edge rely on.

<Info>
  *Note*: The qBraid-SDK requires Python 3.10 or greater. You can check your
  Python version by running `python --version` from the command line.
</Info>

## Authentication

The `QPerfectProvider` signs in to the MIMIQ cloud with your MIMIQ account. Set the account email
and password as environment variables:

```bash
export QPERFECT_USERNAME="you@example.com"
export QPERFECT_PASSWORD="your-password"
```

Then initialize the provider:

```python
from qbraid.runtime.qperfect import QPerfectProvider

provider = QPerfectProvider()
```

You can also pass the credentials directly, or a MIMIQ refresh token from an earlier login:

```python
# account credentials passed directly
provider = QPerfectProvider(username="you@example.com", password="your-password")

# a refresh token (or set QPERFECT_API_TOKEN)
provider = QPerfectProvider(token="your-refresh-token")
```

<Note>
  MIMIQ refresh tokens last about a day. When both a token and account
  credentials are configured, the provider tries the token first and logs in
  with the credentials if MIMIQ rejects it, so set the credentials for anything
  long-running. Credentials are checked on first use, not when the provider is
  created.
</Note>

To use a different MIMIQ cloud, pass `url=` or set `QPERFECT_BASE_URL`. It defaults to
`https://mimiq.qperfect.io`.

## List available devices

MIMIQ exposes a single cloud emulator. Use the `QPerfectProvider` to list it:

```python
from qbraid.runtime.qperfect import QPerfectProvider

provider = QPerfectProvider()

devices = provider.get_devices()
print(devices)
```

Get the emulator by its id, `mimiq-emulator`:

```python
device = provider.get_device("mimiq-emulator")

print(device.status())
# <DeviceStatus.ONLINE>
```

<Note>
  MIMIQ has no device-status endpoint, so the emulator's status reflects
  **connection health**: it is `ONLINE` when the provider can authenticate a
  connection to the MIMIQ cloud, and `OFFLINE` otherwise. If an open connection
  drops, for example after a network error during a token refresh, the next
  `status()` call or job submission logs in again.
</Note>

## Submitting jobs

The `QPerfectProvider` accepts circuits written in any qBraid-supported framework. `device.run()`
transpiles the circuit to a native MIMIQ circuit and submits it to the MIMIQ cloud. A native
`mimiqcircuits.Circuit` may also be passed directly, in which case it is submitted as-is (preserving
any noise models or MIMIQ-specific operations).

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
from qbraid.runtime.qperfect import QPerfectProvider

provider = QPerfectProvider()
device = provider.get_device("mimiq-emulator")

circuit = QuantumCircuit(2)
circuit.h(0)
circuit.cx(0, 1)
circuit.measure_all()

job = device.run(circuit, shots=100)
print(f"Job ID: {job.id}")
```

### Choosing a simulation algorithm

For a single circuit, MIMIQ picks the backend itself (`"auto"`). Pin it with the `algorithm` option:
`"statevector"` (exact, memory-bound) or `"mps"` (matrix-product-state, scales with entanglement):

```python
# Matrix-product-state simulation, capped bond dimension
job = device.run(circuit, shots=100, algorithm="mps", bonddim=256)
```

### Batch submission

Submit multiple circuits in a single call. All circuits are bundled into one MIMIQ job. MIMIQ does
not accept `"auto"` for a batch, so a batch runs on `"mps"` unless you pass another `algorithm`:

```python
from qiskit import QuantumCircuit
from qbraid.runtime.qperfect import QPerfectProvider

provider = QPerfectProvider()
device = provider.get_device("mimiq-emulator")

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
  When submitting a list of circuits, the returned measurement counts will be a
  list of dictionaries, one per circuit, in submission order.
</Note>

### Simulation parameters

MIMIQ accepts per-job [simulation parameters](https://docs.qperfect.io/mimiqcircuits-python/manual/simulation_parameters.html)
as keyword arguments to `device.run()`. Common options include:

| Option       | Description                                                          |
| ------------ | -------------------------------------------------------------------- |
| `algorithm`  | Simulation backend: `"auto"` (default; `"mps"` for a batch), `"statevector"`, or `"mps"`. |
| `bonddim`    | Maximum bond dimension for the MPS backend (default `256`).          |
| `entdim`     | Maximum entangling dimension for the MPS backend (default `16`).     |
| `timelimit`  | Maximum wall-clock time (minutes) for the job.                       |
| `seed`       | Random seed for reproducible sampling.                               |
| `bitstrings` | Explicit list of bitstrings whose amplitudes should be returned.     |
| `noisemodel` | A MIMIQ noise model to apply during simulation.                      |

```python
job = device.run(
    circuit,
    shots=1000,
    algorithm="mps",
    bonddim=128,
    seed=42,
)
```

<Note>
  See QPerfect's [simulation parameters
  reference](https://docs.qperfect.io/mimiqcircuits-python/manual/simulation_parameters.html)
  for the full list of options and their defaults.
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

| Parameter   | Type  | Default    | Description                                                                    |
| ----------- | ----- | ---------- | ------------------------------------------------------------------------------ |
| `shots`     | `int` | `100`      | Number of samples per circuit (MIMIQ `nsamples`).                              |
| `name`      | `str` | `"qbraid"` | Optional human-readable job label.                                             |
| `algorithm` | `str` | `"auto"`   | Simulation backend: `"auto"`, `"statevector"`, or `"mps"`. A batch defaults to `"mps"`. |
| `**options` | —     | —          | Additional MIMIQ simulation parameters (`bonddim`, `seed`, `noisemodel`, ...). An unsupported option raises `ValueError` listing the supported ones. |

Credentials are configured via environment variables:

| Variable             | Description                                                                  |
| -------------------- | ---------------------------------------------------------------------------- |
| `QPERFECT_USERNAME`  | MIMIQ account email.                                                         |
| `QPERFECT_PASSWORD`  | MIMIQ account password.                                                      |
| `QPERFECT_API_TOKEN` | Optional MIMIQ refresh token (lasts about a day; tried before the login).    |
| `QPERFECT_BASE_URL`  | Optional MIMIQ cloud URL override (defaults to `https://mimiq.qperfect.io`). |

## Full example

A complete end-to-end workflow submitting a GHZ state to the MIMIQ emulator:

```python
from qiskit import QuantumCircuit
from qbraid.runtime.qperfect import QPerfectProvider

# 1. Initialize provider (reads QPERFECT_USERNAME / QPERFECT_PASSWORD from the environment)
provider = QPerfectProvider()

# 2. Get the MIMIQ emulator
device = provider.get_device("mimiq-emulator")
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

- [QPerfect](https://www.qperfect.io/)
- [MIMIQ Documentation](https://docs.qperfect.io/)
- [MIMIQ Simulation Parameters](https://docs.qperfect.io/mimiqcircuits-python/manual/simulation_parameters.html)
- [mimiqcircuits on PyPI](https://pypi.org/project/mimiqcircuits/)
- [mimiq-qiskit on PyPI](https://pypi.org/project/mimiq-qiskit/)
