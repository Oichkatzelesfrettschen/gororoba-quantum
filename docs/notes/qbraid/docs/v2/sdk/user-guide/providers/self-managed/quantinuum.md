> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/quantinuum.md](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/quantinuum.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 fd3c1b3371ee255fe7be0b68494ea9517fe384d1481f51b05717ac57f2907727.

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

# Quantinuum (self-managed)

> Run on Quantinuum trapped-ion devices with your own Quantinuum Nexus account, using the QuantinuumProvider.

<Note>
  This page uses `QuantinuumProvider` with your own Quantinuum account: jobs go straight to
  Quantinuum, and qBraid isn't involved. See [Self-managed
  providers](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed) for how this differs from [running on
  qBraid](https://docs.qbraid.com/v2/sdk/user-guide/providers/getting-started).
</Note>

<Info>
  API Reference:
  [qbraid.runtime.quantinuum](https://qbraid.github.io/qBraid/stubs/qbraid.runtime.quantinuum.html)
</Info>

## Overview

The `qbraid.runtime.QuantinuumProvider` provides support for Quantinuum's trapped-ion quantum systems
through the [Quantinuum Nexus](https://nexus.quantinuum.com/) platform. This means you can write quantum circuits using
[pytket](https://tket.quantinuum.com/), compile and execute them on Quantinuum's H-series processors and emulators,
all from within the [qBraid Runtime framework](https://docs.qbraid.com/v2/sdk/user-guide/runtime/components).

This page covers `QuantinuumProvider`, which runs against your own Nexus account. If you would rather
have the Nexus account managed by qBraid, see [Through qBraid](#through-qbraid) at the end. You need only a
qBraid API key.

## Device names

Quantinuum names hardware `<family>-<n>` and derives its other targets from it by suffix. The suffix is
the only thing distinguishing an emulator from the QPU it models, so it is worth reading carefully before
submitting:

| Name                         | Kind                                            |
| ---------------------------- | ----------------------------------------------- |
| `H1-1`, `H2-1`, `Helios-1`   | QPU                                             |
| `H1-1E`, `H2-1E`             | Device-hosted emulator (noise model of the QPU) |
| `H1-1LE`, `H2-1LE`           | Nexus-hosted emulator                           |
| `H1-Emulator`, `H2-Emulator` | Nexus-hosted emulator                           |
| `H1-1SC`, `H2-1SC`           | Syntax checker (validates without executing)    |

`device.profile.simulator` reflects this classification. `device.status()` reports `ONLINE`,
`UNAVAILABLE` (maintenance), or `OFFLINE`; Nexus-hosted emulators have no machine-status endpoint and
always report `ONLINE`.

## Getting started

Before you begin, make sure you have:

1. A **Quantinuum Nexus** account with valid credentials.
2. The **qnexus** CLI tool installed and authenticated (see [Authentication](#authentication) below).
3. Python >= 3.10

### Set up the qBraid-SDK

Install qBraid with the `quantinuum` extra from [PyPI](https://pypi.org/project/qbraid/) using pip:

```bash
pip install 'qbraid[quantinuum]'
```

This installs the required dependencies: `pytket`, `pytket-quantinuum`, and `qnexus`.

<Info>
  *Note*: The qBraid-SDK requires Python 3.10 or greater. You can check your
  Python version by running `python --version` from the command line.
</Info>

## Authentication

The `QuantinuumProvider` authenticates through the `qnexus` library. Before using the provider, you must
log in using the `qnexus` CLI:

```bash
qnx login
```

This opens a browser-based authentication flow and stores your credentials locally. Once authenticated,
the provider will automatically use your stored credentials. No API keys or environment variables are needed.

Then initialize the provider:

```python
from qbraid.runtime.quantinuum import QuantinuumProvider

provider = QuantinuumProvider()
```

## List available devices

Use the `QuantinuumProvider` to list all devices to which you have access:

```python
from qbraid.runtime.quantinuum import QuantinuumProvider

provider = QuantinuumProvider()

devices = provider.get_devices()
print(devices)
```

Get a specific device by its ID:

```python
device = provider.get_device("H1-1")

print(device.status())
# <DeviceStatus.ONLINE>
```

<Note>
  Devices with an "E" suffix (e.g., `H1-1E`) are emulators (simulators) that
  model the behavior of the corresponding hardware device.
</Note>

## Submitting jobs

The `QuantinuumProvider` accepts quantum programs written as pytket `Circuit` objects.

### Create a circuit

```python
from pytket.circuit import Circuit

# Bell state circuit
circuit = Circuit(2)
circuit.H(0)
circuit.CX(0, 1)
circuit.measure_all()
```

### Run a job

Use `device.run()` to compile and submit a circuit:

```python
from pytket.circuit import Circuit
from qbraid.runtime.quantinuum import QuantinuumProvider

provider = QuantinuumProvider()
device = provider.get_device("H1-1E")

circuit = Circuit(2)
circuit.H(0)
circuit.CX(0, 1)
circuit.measure_all()

job = device.run(circuit, shots=1000)
print(f"Job ID: {job.id}")
```

### Batch submission

Submit multiple circuits in a single call. All circuits are bundled into one Nexus job:

```python
from pytket.circuit import Circuit
from qbraid.runtime.quantinuum import QuantinuumProvider

provider = QuantinuumProvider()
device = provider.get_device("H1-1E")

circuits = [
    Circuit(1).H(0).measure_all(),
    Circuit(1).X(0).measure_all(),
    Circuit(2).H(0).CX(0, 1).measure_all(),
]

job = device.run(circuits, shots=500)
print(f"Job ID: {job.id}")
```

<Note>
  When submitting a list of circuits, all circuits are compiled and executed as
  a single batch job on Quantinuum Nexus. The returned `measurement_counts` will
  be a list of dictionaries, one per circuit.
</Note>

## Retrieving results

```python
result = job.result()

# Measurement counts
print(result.data.measurement_counts)
# {'00': 512, '11': 488}

# Job metadata
print(f"Device: {result.device_id}")
print(f"Job ID: {result.job_id}")
print(f"Success: {result.success}")
```

<Warning>
  Counts are keyed most-significant-bit first, matching qBraid's other
  providers. Nexus and pytket use least-significant-bit-first ordering
  internally, and qBraid converts on the way out, so a bitstring read here is
  reversed relative to the same result fetched through pytket directly.
</Warning>

<Warning>
  Your circuit must contain measurements. Quantinuum executes exactly the
  circuit you submit, so a circuit with no measurement instruction produces no
  counts. Some frameworks imply a final measure-all that does not survive
  conversion, so add measurements explicitly rather than relying on it.
</Warning>

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
  Cancellation is best-effort. Jobs already in a terminal state (`COMPLETED`,
  `FAILED`, `CANCELLED`) cannot be cancelled.
</Note>

### Execution time

You can retrieve the wall-clock execution time (in seconds) for a completed job:

```python
print(f"Execution time: {job.execution_time_s()} seconds")
```

## Configuration options

The `device.run()` method accepts additional keyword arguments to control compilation and project scoping:

| Parameter            | Type  | Default    | Description                                       |
| -------------------- | ----- | ---------- | ------------------------------------------------- |
| `shots`              | `int` | `1000`     | Number of measurement shots per circuit.          |
| `project_name`       | `str` | `"qbraid"` | Nexus project name to scope compile/execute jobs. |
| `optimisation_level` | `int` | `1`        | pytket optimization level (0-2).                  |

The `project_name` and `optimisation_level` parameters can also be set via environment variables:

| Variable                           | Default    | Description                                         |
| ---------------------------------- | ---------- | --------------------------------------------------- |
| `QUANTINUUM_NEXUS_PROJECT_NAME`    | `"qbraid"` | Default Nexus project name.                         |
| `QUANTINUUM_NEXUS_OPT_LEVEL`       | `1`        | Default pytket optimization level.                  |
| `QUANTINUUM_NEXUS_COMPILE_TIMEOUT` | `900`      | Seconds `run` waits for compilation before raising. |
| `QUANTINUUM_NEXUS_HTTP_TIMEOUT`    | `60`       | Per-request timeout on every Nexus HTTP call.       |

Nexus runs a submission as two jobs: a compile job, which `run` blocks on, and an execute job, which the
returned `QuantinuumJob` tracks. `QUANTINUUM_NEXUS_COMPILE_TIMEOUT` bounds that blocking wait, so a compile
stuck in the Nexus queue raises `QuantinuumDeviceError` rather than holding the calling thread
indefinitely. Raise it if you routinely submit large circuits.

A malformed value for any of these raises `QuantinuumDeviceError` naming the variable, rather than
surfacing later as an unrelated failure.

## Full example

A complete end-to-end workflow targeting a Quantinuum emulator:

```python
from pytket.circuit import Circuit
from qbraid.runtime.quantinuum import QuantinuumProvider

# 1. Initialize provider (assumes qnx login was run)
provider = QuantinuumProvider()

# 2. Get an emulator device
device = provider.get_device("H1-1E")
print(f"Device status: {device.status()}")

# 3. Define a GHZ state circuit
circuit = Circuit(3)
circuit.H(0)
circuit.CX(0, 1)
circuit.CX(1, 2)
circuit.measure_all()

# 4. Submit the job
job = device.run(circuit, shots=1000, optimisation_level=2)
print(f"Submitted job: {job.id}")

# 5. Retrieve results
result = job.result()
print(f"Counts: {result.data.measurement_counts}")
# Expected output (approximate): {'000': ~500, '111': ~500}
```

## Through qBraid

If you do not have a Nexus account, you can reach the same devices through `QbraidProvider`, where
the Nexus credentials are managed by qBraid. You need a [qBraid API key](https://account.qbraid.com) and nothing
else: no `qnexus` install, no `qnx login`:

```bash
pip install qbraid
export QBRAID_API_KEY="your_api_key_here"
```

Devices are addressed by their qBraid resource name rather than the Nexus device name:

```python
from qiskit import QuantumCircuit
from qbraid.runtime import QbraidProvider

provider = QbraidProvider()
device = provider.get_device("quantinuum:quantinuum:sim:h2-emulator")

circuit = QuantumCircuit(2)
circuit.h(0)
circuit.cx(0, 1)
circuit.measure_all()

job = device.run(circuit, shots=1000)
print(job.result().data.get_counts())
```

```
{'00': 496, '11': 504}
```

To see which are available to you:

```python
devices = [d for d in provider.get_devices() if d.profile.provider_name == "quantinuum"]
```

The bit-ordering and measurement notes above apply equally here. Two differences from the self-managed path:
circuits are submitted one per job rather than as a Nexus batch, and the `QUANTINUUM_NEXUS_*` variables
are set on the qBraid runtime rather than by you.

## Related links

- [Quantinuum Nexus](https://nexus.quantinuum.com/)
- [pytket Documentation](https://tket.quantinuum.com/)
- [pytket-quantinuum Extension](https://tket.quantinuum.com/extensions/pytket-quantinuum/)
