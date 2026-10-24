> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/aws.md](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/aws.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 dad009f19190688d684403d91230217b5fb7fcc50f011f9d70e9be011c56df26.

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

# Amazon Braket (self-managed)

> Run on Amazon Braket devices with your own AWS account, using the BraketProvider.

<Note>
  This page uses `BraketProvider` with your own Amazon Braket account: jobs go straight to
  Amazon Braket, and qBraid isn't involved. To run on Amazon Braket with only a qBraid API
  key, see [Amazon Braket on qBraid](https://docs.qbraid.com/v2/sdk/user-guide/providers/aws).
</Note>

<Info>
  API Reference:
  [qbraid.runtime.aws](https://qbraid.github.io/qBraid/stubs/qbraid.runtime.aws.html)
</Info>

## Installation & Setup

To interface with Amazon Braket [supported devices](https://docs.aws.amazon.com/braket/latest/developerguide/braket-devices.html),
install the `braket` extra:

```bash
pip install 'qbraid[braket]'
```

Then, follow [instructions](https://github.com/aws/amazon-braket-sdk-python#boto3-and-setting-up-aws-credentials)
to configure your AWS credentials.

## Basic Usage

Submit a Quantum Task to an AWS device using the `BraketProvider`:

```python
from qbraid.runtime import BraketProvider

provider = BraketProvider()

provider.get_devices()
# [<qbraid.runtime.aws.device.BraketDevice('.../qpu/rigetti/Ankaa-3')>,
#  <qbraid.runtime.aws.device.BraketDevice('.../qpu/quera/Aquila')>,
#  <qbraid.runtime.aws.device.BraketDevice('.../qpu/ionq/Aria-1')>,
#  <qbraid.runtime.aws.device.BraketDevice('.../qpu/ionq/Aria-2')>,
#  <qbraid.runtime.aws.device.BraketDevice('.../qpu/ionq/Forte-1')>,
#  <qbraid.runtime.aws.device.BraketDevice('.../qpu/ionq/Forte-Enterprise-1')>,
#  <qbraid.runtime.aws.device.BraketDevice('.../qpu/iqm/Garnet')>,
#  <qbraid.runtime.aws.device.BraketDevice('.../quantum-simulator/amazon/sv1')>,
#  <qbraid.runtime.aws.device.BraketDevice('.../quantum-simulator/amazon/tn1')>,
#  <qbraid.runtime.aws.device.BraketDevice('.../quantum-simulator/amazon/dm1')>]

device = provider.get_device("arn:aws:braket:::device/quantum-simulator/amazon/sv1")

type(device)
# qbraid.runtime.aws.device.BraketDevice

device.metadata()
# {'device_id': 'arn:aws:braket:::device/quantum-simulator/amazon/sv1',
#  'device_type': 'SIMULATOR',
#  'num_qubits': 34,
#  'provider_name': 'Amazon Braket',
#  'status': 'ONLINE',
#  'queue_depth': 0}
```

Now that we've instantiated our device, in this case the AWS SV1 simulator, we can construct a quantum circuit and submit a task using the `.run` method:

```python
from braket.circuits import Circuit

circuit = Circuit().h(0).cnot(0, 1)
job = device.run(circuit, shots=10)
```

We now have `job` which is of type `BraketQuantumTask`, which inherits from `QuantumJob`. To see the results,
we can do the following:

```python
res = job.result()

res.data.get_counts()
# {'00': 6, '11': 4}

res.data.measurements
# array([[0, 0],
#        [0, 0],
#        [1, 1],
#        [1, 1],
#        [0, 0],
#        [0, 0],
#        [0, 0],
#        [1, 1],
#        [0, 0],
#        [0, 0]])
```

See how to visualize these results in the [Visualization](https://docs.qbraid.com/v2/sdk/user-guide/visualization#plot-experimental-results) section.

## Runtime Options

The `BraketDevice.run()` method accepts additional keyword arguments that are passed through
to the underlying Amazon Braket SDK's `AwsDevice.run()`. These options let you control
device-specific behavior such as qubit rewiring, error mitigation, experimental capabilities, and more.

### Disable Qubit Rewiring

By default, Braket may remap the logical qubits in your circuit to physical qubits on the device.
To force the use of the exact qubits specified in your circuit, disable qubit rewiring:

```python
job = device.run(circuit, shots=1000, disable_qubit_rewiring=True)
```

Use this when you need an exact qubit placement preserved on a circuit that is not already using [verbatim compilation](https://docs.aws.amazon.com/braket/latest/developerguide/braket-openqasm-verbatim-compilation.html). A verbatim box serializes to physical qubits on its own and does not need this flag. Pulse-level gate definitions do require it.

### Verbatim Compilation

Wrap a block in a verbatim box to have it executed exactly as written, with no compiler optimization, gate rewriting, or qubit remapping. This matters for characterization work, where the compiler must not touch your gate sequence or qubit placement.

A verbatim box requires the device's native gates and physical qubits (`$0`, `$1`), not a declared register:

```python
device = provider.get_device("arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q")

program = """OPENQASM 3;

bit[1] c;

#pragma braket verbatim
box{
    rz(0.1) $0;
    rx(1.5707963267948966) $0;
}

c[0] = measure $0;
"""

job = device.run(program, shots=10)
```

The Braket SDK's circuit builder produces the same program. `add_verbatim_box` serializes to physical qubits on its own, so no extra flag is needed:

```python
import math

from braket.circuits import Circuit

inner = Circuit().rz(0, 0.1).rx(0, math.pi / 2)
circuit = Circuit().add_verbatim_box(inner)
circuit.measure(0)

job = device.run(circuit, shots=10)
```

<Note>
  Gates inside the box must be in the device's native set. On Rigetti that is `rx`, `rz` and `cz`; on IonQ it is `gpi`, `gpi2` and `ms`, where the third `ms` angle must be between 0 and 0.25.
</Note>

Submitting through the [QbraidProvider](https://docs.qbraid.com/v2/sdk/user-guide/providers/getting-started) instead lets you read back what the device compiled, which is how you confirm the box was honored:

```python
from qbraid.runtime import QbraidProvider

provider = QbraidProvider()
device = provider.get_device("aws:rigetti:qpu:cepheus-1-108q")

job = device.run(program, shots=10)
job.wait_for_final_state()

print(job.compiled_program().data)
```

```text
PRAGMA INITIAL_REWIRING "NAIVE"
DECLARE ro BIT[1]
PRAGMA PRESERVE_BLOCK
RZ(0.1) 0
RX(1.5707963267948966) 0
PRAGMA END_PRESERVE_BLOCK
MEASURE 0 ro[0]
```

The box became a `PRESERVE_BLOCK` with the gates untouched on physical qubit 0, and quilc pinned the placement with `INITIAL_REWIRING "NAIVE"` on its own.

### Error Mitigation (IonQ)

IonQ devices on Braket support error mitigation through debiasing, which creates
variations of your circuit to reduce the effects of hardware noise:

```python
from braket.error_mitigation import Debias

device = provider.get_device("arn:aws:braket:us-east-1::device/qpu/ionq/Aria-1")

job = device.run(
    circuit,
    shots=2500,  # Minimum 2500 shots required for debiasing
    device_parameters={"errorMitigation": Debias()},
)
```

### Experimental Capabilities

Some devices offer experimental features that must be explicitly enabled. For example,
QuEra Aquila supports tight atom geometries and local detuning, and IQM devices support
dynamic circuits with mid-circuit measurement:

```python
device = provider.get_device("arn:aws:braket:us-east-1::device/qpu/quera/Aquila")

job = device.run(
    program,
    shots=1000,
    experimental_capabilities="ALL",
)
```

See [Experimental Capabilities](https://docs.aws.amazon.com/braket/latest/developerguide/braket-experimental-capabilities.html) for a full list of available features per device.

### Parametric Circuits

For OpenQASM programs with input parameters, pass values at runtime:

```python
job = device.run(
    openqasm_program,
    shots=1000,
    inputs={"theta": 1.57, "phi": 0.785},
)
```

### Reservation ARN

If you have a [Braket Direct](https://aws.amazon.com/braket/direct/) reservation for
exclusive device access, provide the reservation ARN:

```python
job = device.run(
    circuit,
    shots=1000,
    reservation_arn="arn:aws:braket:us-east-1:123456789012:reservation/abc123",
)
```

### Tags

Attach metadata tags to your quantum tasks for tracking and organization:

```python
job = device.run(
    circuit,
    shots=1000,
    tags={"experiment": "bell-state", "team": "quantum-research"},
)
```

### Options Reference

| Parameter                   | Type               | Description                                    |
| --------------------------- | ------------------ | ---------------------------------------------- |
| `disable_qubit_rewiring`    | `bool`             | Force use of exact qubits without remapping    |
| `device_parameters`         | `dict`             | Device-specific config (e.g. error mitigation) |
| `experimental_capabilities` | `str`              | Set to `"ALL"` to enable experimental features |
| `inputs`                    | `dict[str, float]` | Parameter values for parametric circuits       |
| `reservation_arn`           | `str`              | Braket Direct reservation ARN                  |
| `tags`                      | `dict[str, str]`   | Metadata tags for the quantum task             |

### Via qBraid Runtime API

When submitting jobs through the [QbraidProvider](https://docs.qbraid.com/v2/sdk/user-guide/providers/getting-started), these same
options can be passed via the `runtimeOptions` field. The runtime API forwards them as keyword
arguments to the Braket `device.run()` call:

```python
from qbraid.runtime import QbraidProvider

provider = QbraidProvider()

device = provider.get_device("aws:quera:qpu:aquila")

job = device.run(
    program,
    shots=1000,
    runtime_options={"experimental_capabilities": "ALL"},
)
```

```python
device = provider.get_device("aws:ionq:qpu:aria-1")

job = device.run(
    circuit,
    shots=2500,
    runtime_options={"device_parameters": {"errorMitigation": "Debias"}},
)
```
