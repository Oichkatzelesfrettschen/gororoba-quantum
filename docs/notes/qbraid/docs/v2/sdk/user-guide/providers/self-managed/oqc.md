> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/oqc.md](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/oqc.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 6cab3b6678898c29212cbadd702133c3f5266f672d2863da413dba862a7dd566.

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

# OQC (self-managed)

> Run on OQC simulators and QPUs with your own OQC credentials, using the OQCProvider.

<Note>
  This page uses `OQCProvider` with your own OQC account: jobs go straight to
  OQC, and qBraid isn't involved. See [Self-managed
  providers](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed) for how this differs from [running on
  qBraid](https://docs.qbraid.com/v2/sdk/user-guide/providers/getting-started).
</Note>

<Info>
  API Reference:
  [qbraid.runtime.oqc](https://qbraid.github.io/qBraid/stubs/qbraid.runtime.oqc.html)
</Info>

This page offers a high-level guide on using qBraid's `OQCProvider`, `OQCDevice`, and `OQCJob` classes to submit and manage jobs on Oxford Quantum Circuits (OQC) QPUs and simulators.

## Installation & Setup

To interface with OQC devices, install the `oqc` extra:

```bash
pip install 'qbraid[oqc]'
```

You wil also need an [OQC access token](https://docs.oqc.app/account_management.html#access-tokens) to authenticate your connection to OQC's cloud services.
To obtain an access token, log in or create an account at https://cloud.oqc.app/, and follow the instructions on the "My Account" page to "Add Auth Token".

## Initializing the Provider

Begin by importing the `OQCProvider` and initializing it with your API token.
This token authenticates your access to the OQC cloud platform:

```python
from qbraid.runtime import OQCProvider

provider = OQCProvider("<YOUR_API_TOKEN>")
```

By default, the endpoint URL is set to `"https://cloud.oqc.app/"`. If needed, you can specify a custom endpoint:

```python
provider = OQCProvider(token="<YOUR_API_TOKEN>", url="https://example.cloud.oqc.app/")
```

## Listing Available Devices

Fetch a list of devices accessible through the provider. This provides an overview of the QPUs and simulators available to you:

```python
provider.get_devices()
# [<qbraid.runtime.oqc.device.OQCDevice('qpu:uk:2:d865b5a184')>,
# <qbraid.runtime.oqc.device.OQCDevice('qpu:jp:3:673b1ad43c')>]
```

## Accessing Device Details

Retrieve a specific device using its unique ID and examine details such as its profile, status, and scheduling information:

```python
device = provider.get_device("qpu:jp:3:673b1ad43c")

print(f"Profile: {device.profile}")
print(f"Status: {device.status().name}")

if not device.profile.simulator:
    print(f"Queue Depth: {device.queue_depth()}")
    print(f"Next Window: {device.get_next_window()}")

print(f"All Metadata: {device.metadata()}")
```

## Metrics, Optimizations, and Other Configuration Options

Tune your job submission with a variety of parameters, including shot count, repetition period, result formatting, and program optimizations.
These options allow precise control over job execution and output. Below is a detailed breakdown of each parameter:

- `shots`: The number of times the circuit is ran. The default value is 1000.
- `repetition_period`: The length of time in between shots. The default value is 200e-6 seconds and OQC strongly recommends that you use the default unless you thoroughly understand the potential impact.
- `results_format`: The two options for this are `'raw'` and `'binary'`.
- `metrics`: The type of metrics you want to be recorded. The only metrics related to a task are its optimized circuit and the corresponding instruction count. So, there are four options:
  1. `'default'`: Returns both metrics.
  2. `'empty'`: Returns no metrics.
  3. `'optimized_circuit'`: Returns the optimized qasm2 circuit.
  4. `'optimized_instruction_count'`: Returns the instruction count of the optimized circuit.
- `optimizations`: These are the optimizations you want to perform on the input program(s). OQC uses the [tKet optimization compiler](https://oqc.tech/oqc-integrates-tket), as it is integrated into their compiler pipeline. Documention on these are in the [pytket.passes documentation](https://tket.quantinuum.com/api-docs/passes.html), and below are the instructions to access them through `OQCDevice.run()`:
  | Option | TKET pass |
  | :----------------------------- | :------------------------------------ |
  | `'clifford_simplify'` | `CliffordSimp` |
  | `'context_simplify'` | `ContextSimp` |
  | `'decompose_controlled_gates'` | `DecomposeArbitrarilyControlledGates` |
  | `'default_mapping_pass'` | `DefaultMappingPass` |
  | `'empty'` | `Empty` |
  | `'full_peephole_optimise'` | `FullPeepholeOptimise` |
  | `'globalise_phased_x'` | `GlobalisePhasedX` |
  | `'kak_decomposition'` | `KAKDecomposition` |
  | `'one'` | `One` |
  | `'peephole_optimise_2q'` | `PeepholeOptimise2Q` |
  | `'remove_barriers'` | `RemoveBarriers` |
  | `'remove_discarded'` | `RemoveDiscarded` |
  | `'remove_redundancies'` | `RemoveRedundancies` |
  | `'simplify_measured'` | `SimplifyMeasured` |
  | `'three_qubit_squash'` | `ThreeQubitSquash` |
  | `'two'` | `Two` |

## Program Submission Specifications and Device Compatibility

- Any program type compatible with OpenQASM 3 (i.e. can be converted to OpenQASM 3 via `qbraid.transpile(program, "qasm3")`) can be passed directly to the `OQCDevice.run()` method.
- All `include` statements will be removed from transpiled OpenQASM 3 program upon submission, as they are not recognized by OQC.
- The default supported gates for all OQC devices include the entire OpenQASM 3 `stdgates.inc` gate set plus the `ecr` gate.
- For QPUs, submissions do not need to use "native gates."
- The Lucy Simulator is noiseless and does not support error mitigation.
- OpenQASM 3 programs with classical control operations are _not supported_.
- OpenQASM 3 programs containing pulse-level descriptions of gates and measurements (e.g. OpenPulse grammar) are _supported_.

## Bell Circuit Job Example

Submit an OpenQASM 3 bell circuit to the Lucy Simulator device:

```python
from qbraid.runtime import OQCProvider

# Token loaded automatically from "OQC_AUTH_TOKEN" environment variable
provider = OQCProvider()

device = provider.get_device("qpu:uk:2:d865b5a184")

program = """
OPENQASM 3;
qubit[2] q;
bit[2] c;
h q[0];
h q[1];
cx q[0], q[1];
c = measure q;
"""

job = device.run(
    program,
    shots=1000,
    repetition_period=100e-6,
    metrics='optimized_circuit',
    optimizations='default_mapping_pass'
)

print(job.id)
```

## Monitor Job Status

Inspect the job status, metrics, timings, and other metadata:

```python
>>> job.status()
<COMPLETED: 'job has successfully run'>
>>> job.metadata()
{'status': <COMPLETED: 'job has successfully run'>,
 'allow_support_access': False,
 'created_at': 'Wed, 27 Nov 2024 18:32:46 GMT',
 'qpu_id': 'qpu:uk:2:d865b5a184',
 'tag': None,
 'shots': 1000,
 'repetition_period': 0.0001,
 'results_format': 'binary',
 'metrics': 'optimized_circuit',
 'active_calibrations': [],
 'optimizations': 'default_mapping_pass',
 'error_mitigation': None,
 'errors': None,
 'timings': {'RECEIVER_DEQUEUED': '2024-11-27 18:32:47.142509+00:00',
  'RECEIVER_ENQUEUED': '2024-11-27 18:32:47.371945+00:00',
  'RECEIVER_FROM_COMPILER': '2024-11-27 18:32:47.371836+00:00',
  'RECEIVER_TO_COMPILER': '2024-11-27 18:32:47.142769+00:00',
  'SERVER_DEQUEUED': '2024-11-27 18:32:47.384944+00:00',
  'SERVER_ENQUEUED': '2024-11-27 18:32:47.123478+00:00',
  'SERVER_RECEIVED': '2024-11-27 18:32:47.079319+00:00'}}
>>> job.metrics()
{'optimized_circuit': 'OPENQASM 3;\nqubit[2] q;\nbit[2] c;\nh q[0];\nh q[1];\ncx q[0], q[1];\nc = measure q;\n',
 'optimized_instruction_count': None}
```

## Gather Job Results

Retrieve and analyze the results of your job:

```python
result = job.result()

result.data.get_counts()
# {'00': 250, '01': 235, '10': 264, '11': 251}
```

To plot the histogram counts and probability distribution, refer to the [Plot Experimental Results](https://docs.qbraid.com/v2/sdk/user-guide/visualization#plot-experimental-results) section in the visualization guide.
