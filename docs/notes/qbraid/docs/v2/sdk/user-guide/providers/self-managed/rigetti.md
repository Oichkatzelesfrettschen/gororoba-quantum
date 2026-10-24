> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/rigetti.md](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/rigetti.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 312212e5e69906b3a61484b9d488c77ef467952169d68111a2018808d56badc2.

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

# Rigetti (self-managed)

> Run on Rigetti quantum processors with your own Rigetti QCS account, using the RigettiProvider.

<Note>
  This page uses `RigettiProvider` with your own Rigetti account: jobs go straight to
  Rigetti, and qBraid isn't involved. To run on Rigetti with only a qBraid API
  key, see [Rigetti on qBraid](https://docs.qbraid.com/v2/sdk/user-guide/providers/rigetti).
</Note>

<Info>
  API Reference:
  [qbraid.runtime.rigetti](https://qbraid.github.io/qBraid/stubs/qbraid.runtime.rigetti.html)
</Info>

<Warning>
  On-demand access to Rigetti quantum systems (Ankaa, Cepheus) is restricted.
  You must contact [Rigetti](https://www.rigetti.com/contact) to request access
  credentials before using this provider.
</Warning>

## Prerequisites

Before getting started, ensure you have:

1. A **Rigetti QCS account** with an active refresh token (contact Rigetti to obtain access).
2. The **Forest SDK** installed locally — specifically the `quilc` compiler. The `qvm` simulator is optional.
3. Python > 3.10 and < 3.13

### Install the Forest SDK

The `quilc` compiler is required to compile Quil programs into the native gate set of the target QPU. Install it for your platform:

- **macOS / Linux**: Download from [qcs.rigetti.com/sdk-downloads](https://qcs.rigetti.com/sdk-downloads)
- **Docker**: `docker run --rm -p 5555:5555 rigetti/quilc -S`

Verify the installation:

```bash
quilc --version
```

## Installation & Setup

Install the `rigetti` extra:

```bash
pip install 'qbraid[rigetti]'
```

This installs the required dependencies: `pyquil` and `qcs-sdk-python`.

## Authentication

The `RigettiProvider` authenticates with Rigetti QCS using an **OAuth refresh token**. Set it as an environment variable (required):

```bash
export RIGETTI_REFRESH_TOKEN="your-refresh-token"
```

Then initialize the provider:

```python
from qbraid.runtime.rigetti import RigettiProvider

provider = RigettiProvider()
```

### Optional Environment Variables

| Variable             | Description             | Default                        |
| -------------------- | ----------------------- | ------------------------------ |
| `RIGETTI_CLIENT_ID`  | Custom OAuth client ID  | Rigetti default                |
| `RIGETTI_ISSUER`     | Custom OAuth issuer URL | Rigetti default                |
| `QCS_GRPC_ENDPOINT`  | QCS gRPC API endpoint   | `https://grpc.qcs.rigetti.com` |
| `QCS_QUILC_ENDPOINT` | quilc compiler endpoint | `tcp://127.0.0.1:5555`         |
| `QCS_QVM_ENDPOINT`   | QVM simulator endpoint  | `http://127.0.0.1:5000`        |

### Provider Setup

After initializing the provider, call `setup()` to manage the local quilc compiler process. This ensures quilc is running and ready to compile programs:

```python
provider = RigettiProvider()

# Start a local quilc process (default behavior)
provider.setup()

# Or, point to an existing quilc endpoint
provider.setup(quilc_endpoint="tcp://my-quilc-host:5555")
```

The `setup()` method accepts the following keyword arguments:

| Parameter        | Type   | Default | Description                                             |
| ---------------- | ------ | ------- | ------------------------------------------------------- |
| `quilc_endpoint` | `str`  | `None`  | Pre-existing quilc endpoint. Skips local process start. |
| `qvm_endpoint`   | `str`  | `None`  | Pre-existing QVM endpoint. Skips local process start.   |
| `grpc_endpoint`  | `str`  | `None`  | Override for the QCS gRPC endpoint.                     |
| `start_quilc`    | `bool` | `True`  | Auto-start local quilc if not already running.          |
| `start_qvm`      | `bool` | `False` | Auto-start local QVM if not already running.            |

## Getting Available Devices

List all quantum processors available through your QCS account:

```python
from qbraid.runtime.rigetti import RigettiProvider

provider = RigettiProvider()
provider.setup()

devices = provider.get_devices()
print(devices)
# [RigettiDevice('ankaa-3'), RigettiDevice('cepheus-108')]
```

Get a specific device by its processor ID:

```python
device = provider.get_device("ankaa-3")

print(device.status())
# <DeviceStatus.ONLINE>

# Get the list of live qubit IDs on the device
qubits = device.live_qubits()
print(f"Live qubits ({len(qubits)}): {qubits[:10]}...")
```

## Submitting Jobs

The `RigettiProvider` accepts programs written in [Quil](https://quil-lang.github.io/) using the `pyquil` library. Programs are compiled via `quilc` before submission to the QPU.

### Create a Program

```python
from pyquil import Program

# Bell state circuit
program = Program("""
DECLARE ro BIT[2]
H 0
CNOT 0 1
MEASURE 0 ro[0]
MEASURE 1 ro[1]
""")
```

### Run a Job

Use `device.run()` to compile and submit in one step:

```python
from pyquil import Program
from qbraid.runtime.rigetti import RigettiProvider

provider = RigettiProvider()
provider.setup()

device = provider.get_device("ankaa-3")

program = Program("""
DECLARE ro BIT[2]
H 0
CNOT 0 1
MEASURE 0 ro[0]
MEASURE 1 ro[1]
""")

job = device.run(program, shots=1000)
print(f"Job ID: {job.id}")
```

### Batch Submission

Submit multiple programs in a single call:

```python
from pyquil import Program
from qbraid.runtime.rigetti import RigettiProvider

provider = RigettiProvider()
provider.setup()

device = provider.get_device("ankaa-3")

programs = [
    Program("DECLARE ro BIT[1]\nH 0\nMEASURE 0 ro[0]"),
    Program("DECLARE ro BIT[1]\nX 0\nMEASURE 0 ro[0]"),
    Program("DECLARE ro BIT[1]\nH 0\nS 0\nMEASURE 0 ro[0]"),
]

jobs = device.run(programs, shots=500)
for job in jobs:
    print(f"Job ID: {job.id}")
```

## Retrieving Results

```python
result = job.result()

# Measurement counts as a dictionary
print(result.data.measurement_counts)
# {'00': 512, '11': 488}

# Job metadata
print(f"Device: {result.device_id}")
print(f"Job ID: {result.job_id}")
print(f"Success: {result.success}")
print(f"Duration (us): {result.execution_duration_microseconds}")
```

### Check Job Status

```python
from qbraid.runtime.enums import JobStatus

status = job.status()
print(status)
# <JobStatus.COMPLETED>
```

### Cancel a Job

```python
job.cancel()
```

<Note>
  Cancellation is best-effort. Jobs already in a terminal state (`COMPLETED`,
  `FAILED`, `CANCELLED`) cannot be cancelled.
</Note>

## Runtime Options

The `device.run()` method accepts an optional `runtime_options` dict to control compilation
and translation behavior:

```python
job = device.run(
    program,
    shots=1000,
    runtime_options={
        "compiler_timeout": 60,
        "prepend_default_calibrations": True,
        "passive_reset_delay_seconds": 1.0,
    },
)
```

### Options Reference

| Parameter                            | Type    | Description                                                                                                      |
| ------------------------------------ | ------- | ---------------------------------------------------------------------------------------------------------------- |
| `compiler_timeout`                   | `float` | quilc compilation timeout in seconds.                                                                            |
| `initial_rewiring`                   | `str`   | quilc qubit-placement strategy: `"NAIVE"`, `"PARTIAL"`, `"GREEDY"`, or `"RANDOM"`. Omit to keep quilc's default. |
| `prepend_default_calibrations`       | `bool`  | Prepend default calibration pulses during translation.                                                           |
| `passive_reset_delay_seconds`        | `float` | Delay between passive resets.                                                                                    |
| `allow_unchecked_pointer_arithmetic` | `bool`  | Disable runtime memory bounds checking (authorized access).                                                      |
| `allow_frame_redefinition`           | `bool`  | Allow frame definitions that differ from Rigetti defaults (authorized access).                                   |

### initial_rewiring

quilc chooses the logical-to-physical qubit mapping with its `INITIAL_REWIRING` strategy. The strategy is a Quil pragma rather than a compiler flag, so this option works by rewriting the submitted program: `PRAGMA INITIAL_REWIRING "<STRATEGY>"` is prepended before compilation.

```python
job = device.run(
    program,
    shots=1000,
    runtime_options={"initial_rewiring": "GREEDY"},
)
```

- **Omit the key** and the program is left untouched, so quilc's own default applies (`PARTIAL`, unless your qubit indices already satisfy the device's connectivity).
- **Why change it:** `PARTIAL` searches for a placement at a cost that grows steeply with qubit count and is independent of circuit depth — on Rigetti's 100+-qubit processors it can dominate compile time. On wide, shallow circuits `GREEDY` compiles roughly an order of magnitude faster with comparable output, and `NAIVE` is the fastest choice when the circuit is already laid out on the device's lattice. On deeper circuits `PARTIAL` costs about the same as `GREEDY` and produces better output, which is why the default is unchanged and this is opt-in.
- A program that already carries its own `PRAGMA INITIAL_REWIRING` keeps it — the runtime option is ignored with a logged warning, since two pragmas would silently change which strategy governs the program.
- Values are case-insensitive; an unrecognized strategy raises `ValueError` naming the supported set before anything is submitted.

## Full Example

A complete end-to-end workflow targeting the Ankaa-3 processor:

```python
import os
from pyquil import Program
from qbraid.runtime.rigetti import RigettiProvider

# 1. Set credentials (or export as env var beforehand)
os.environ["RIGETTI_REFRESH_TOKEN"] = "your-refresh-token"

# 2. Initialize provider and start quilc
provider = RigettiProvider()
provider.setup()

# 3. Get the target device
device = provider.get_device("ankaa-3")
print(f"Device status: {device.status()}")
print(f"Number of qubits: {len(device.live_qubits())}")

# 4. Define a GHZ state circuit
program = Program("""
DECLARE ro BIT[3]
H 0
CNOT 0 1
CNOT 1 2
MEASURE 0 ro[0]
MEASURE 1 ro[1]
MEASURE 2 ro[2]
""")

# 5. Submit the job
job = device.run(program, shots=1000)
print(f"Submitted job: {job.id}")

# 6. Retrieve results
result = job.result()
print(f"Counts: {result.data.measurement_counts}")
# Expected output (approximate): {'000': ~500, '111': ~500}
```

## Related Links

- [Rigetti QCS Documentation](https://docs.rigetti.com/)
- [PyQuil Documentation](https://pyquil-docs.rigetti.com/)
- [Quil Language Specification](https://quil-lang.github.io/)
- [Forest SDK Downloads](https://qcs.rigetti.com/sdk-downloads)
