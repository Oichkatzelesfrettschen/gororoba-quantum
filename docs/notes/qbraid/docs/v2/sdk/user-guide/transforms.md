> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/transforms.md](https://docs.qbraid.com/v2/sdk/user-guide/transforms.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 c3801022d3b060e9b3813a8881ef124ad363563abe9480cf45c974d62b6e9191.

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

# Transforms

> Adapt quantum programs to specific hardware requirements.

In the qBraid-SDK, a "transpile" action refers to converting a quantum program from one type to another,
such as from Qiskit to Amazon Braket. In contrast, a "transform" action involves modifying a quantum program to meet specific
requirements dictated by the target device or API through which the program will be executed.

Let's delve into the various "transforms" employed to prepare a quantum program for execution on an IonQ backend.

We begin by constructing a simple Qiskit circuit that executes a controlled Y rotation:

```python
import numpy as np
from qiskit import QuantumCircuit

circuit = QuantumCircuit(2, 2)

circuit.cry(np.pi/4, 0, 1)

circuit.measure_all()
```

We then connect to the `IonQProvider` and retrieve the specifications for the IonQ Harmony device:

```python
from qbraid.runtime import IonQProvider

provider = IonQProvider()

device = provider.get_device("qpu.harmony")

device.profile.get("program_spec")
# <ProgramSpec('openqasm3', openqasm3.ast.Program)>

device.profile.get("basis_gates")
# { "x","y","z","rx","ry","rz","h","cx","s","sdg","t","tdg","sx","sxdg","swap" }
```

By reviewing the device's `TargetProfile`, we understand that in order to run a program on IonQ Harmony,
qBraid runtime requires that it be expressed as an `openqasm3.ast.Program` and utilize only the gates from
its defined basis gate set. Consequently, our first step is to transpile our `qiskit` program to the `openqasm3`
program type:

```python
from qbraid import transpile

qasm3_program = transpile(circuit, 'openqasm3')

type(qasm3_program)
# openqasm3.ast.Program
```

Next, we load the program into a qBraid `QuantumProgram` object and examine its string representation:

<CodeGroup>

```python Input
from qbraid import load_program

qprogram = load_program(qasm3_program)

print(qprogram.program)
```

```qasm Output
OPENQASM 3.0;
include "stdgates.inc";
bit[2] c;
bit[2] meas;
qubit[2] q;
cry(pi / 4) q[0], q[1];
barrier q[0], q[1];
meas[0] = measure q[0];
meas[1] = measure q[1];
```

</CodeGroup>

We can now apply a "transform" to this program, using our device object as argument,
ensuring it is represented exclusively in terms of gates supported by IonQ Harmony:

<CodeGroup>

```python Input
program.transform(device)

print(program.program)
```

```qasm Output
OPENQASM 3.0;
bit[2] b;
qubit[2] q;
ry(0.39269908169872414) q[1];
cx q[0], q[1];
ry(-0.39269908169872414) q[1];
cx q[0], q[1];
b[0] = measure q[0];
b[1] = measure q[1];
```

</CodeGroup>

Device-specific transforms are a crucial component of the qBraid runtime framework, applied as the final step
before a program is executed on a quantum backend.

We've just demonstrated how one can utilize these transforms independently, outside of a runtime protocol, which
may be beneficial for testing or local simulations. However, for qBraid runtime end-users, these steps are automatically
performed behind the scenes whenever the `QuantumDevice.run` method is invoked.
