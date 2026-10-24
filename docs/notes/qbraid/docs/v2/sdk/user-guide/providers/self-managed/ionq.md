> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/ionq.md](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/ionq.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 88ba6538928a093f7e03225927efab568b4390b43e3e46421953dbdc37cde6e1.

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

# IonQ (self-managed)

> Run on IonQ simulators and QPUs with your own IonQ API key, using the IonQProvider.

<Note>
  This page uses `IonQProvider` with your own IonQ account: jobs go straight to
  IonQ, and qBraid isn't involved. To run on IonQ with only a qBraid API
  key, see [IonQ on qBraid](https://docs.qbraid.com/v2/sdk/user-guide/providers/ionq).
</Note>

<Info>
  API Reference:
  [qbraid.runtime.ionq](https://qbraid.github.io/qBraid/stubs/qbraid.runtime.ionq.html)
</Info>

## Overview

The `qbraid.runtime.IonQProvider` provides support for IonQ's trapped-ion systems. This means that you can write quantum circuits in
Qiskit, Cirq, Amazon Braket, PennyLane, PyTKET, or any other library compatible with [OpenQASM](https://openqasm.com/) (version 2 or 3),
and run them on IonQ's simulators and trapped-ion quantum computers, all from within the [qBraid Runtime framework](https://docs.qbraid.com/v2/sdk/user-guide/runtime/components).

## Getting started

Before you begin, make sure you have an [IonQ Quantum Cloud](https://cloud.ionq.com/) account and API key.
For help, see IonQ's guide on [creating and managing API keys](https://docs.ionq.com/guides/managing-api-keys).

### Set up the qBraid-SDK

Install qBraid with the `ionq` extra from [PyPI](https://pypi.org/project/qbraid/) using pip:

```bash
pip install 'qbraid[ionq]'
```

<Info>
  *Note*: The qBraid-SDK requires Python 3.10 or greater. You can check your
  Python version by running `python --version` from the command line.
</Info>

We encourage doing this inside an environment management system, such as [virtualenv](https://virtualenv.pypa.io/en/latest/) or
[conda](https://docs.conda.io/en/latest/). Alternatively, you can bypass this step by using a pre-configured
[qBraid Lab environment](https://docs.qbraid.com/v2/lab/user-guide/environments).
See [qBraid-SDK installation and setup](https://docs.qbraid.com/v2/sdk/user-guide/overview#installation-and-setup) for more.

### Set up your environment

By default, qBraid will look in your local environment for a variable named `IONQ_API_KEY`, so if you've already followed IonQ's guide on
[setting up and managing your API keys](https://docs.ionq.com/guides/managing-api-keys), qBraid will automatically find it.

Alternatively, you can set a "temporary" environment variable from your command line:

```bash
export IONQ_API_KEY="your_api_key_here"
```

While we recommend setting an environment variable so that qBraid can find your API key, you can also pass in your API key explicitly
within your Python code, when creating the IonQ Provider object that authenticates your connection to the IonQ Cloud Platform. This might
be necessary if you've named your environment variable something other than `IONQ_API_KEY`, or if you are working from a Python environment
where accessing environment variables is not straightforward. You can import your key explicitly or load it from a file, and pass it into
the `IonQProvider()` object directly:

```python
import os
from qbraid.runtime import IonQProvider

# Load your API key from an environment variable named MY_IONQ_API_KEY
my_api_key = os.getenv("MY_IONQ_API_KEY")
provider = IonQProvider(my_api_key)
```

In the examples below, we show `IonQProvider()` initialized with no arguments and assume that qBraid will automatically find your API key,
but you can always use this approach instead.

## List available devices

Use the `IonQProvider` to list all of the devices to which you have access:

```python
from qbraid.runtime import IonQProvider

provider = IonQProvider()

devices = provider.get_devices()
```

Running this script should print the results below—something like this:

```python
[<qbraid.runtime.ionq.device.IonQDevice('qpu.harmony')>,
<qbraid.runtime.ionq.device.IonQDevice('qpu.aria-1')>,
<qbraid.runtime.ionq.device.IonQDevice('qpu.aria-2')>,
<qbraid.runtime.ionq.device.IonQDevice('qpu.forte-1')>,
<qbraid.runtime.ionq.device.IonQDevice('simulator')>]
```

If this works correctly then your qBraid-SDK installation is correct, your IonQ API key is valid, and you have access to the IonQ devices!

## Submit a circuit to the simulator

First, let’s try running a simple Bell state circuit on the ideal simulator. Here, we'll use 1000 shots, and give the circuit a name that
will show up in the [IonQ Cloud Console](https://cloud.ionq.com/jobs).

<Warning>
  Your input OpenQASM program should not include measurement statements.
  Measurement will be applied over all qubits at the end of the circuit,
  automatically. Mid-circuit measurements and partial measurements are not
  supported.
</Warning>

```python
from qbraid.runtime import IonQProvider

provider = IonQProvider()
device = provider.get_device("simulator")

# Define a Bell state circuit in qasm
qasm = """
OPENQASM 3.0;
qubit[2] q;
h q[0];
cx q[0], q[1];
"""

job = device.run(qasm, name="Hello many worlds!", shots=1000)
result = job.result()

print(result.data.get_counts())
```

This returns:

```
{'00': 500, '11': 500}
```

As expected, the ideal simulator creates a quantum state with a 50-50 probability of being measured as “00” or “11”.
To view the calculated probabilities for a circuit run on the simulator, use `result.data.get_probabilities()`.
You can return histogram data in decimal format for either of these `result.data` methods using argument `decimal=True`.

### Submit a circuit with noise

Get a list of all noise models supported by the IonQ simulator:

```python
print(device.profile.noise_models)
```

Then, to run a noisy simulation, simply specify a noise model and an optional random seed:

```python
job = device.run(qasm, shots=1000, noise={"model" : "aria-1", "seed": 42})
```

You can read more about simulation with noise models [here](https://docs.ionq.com/guides/simulation-with-noise-models).

## Submit a circuit to a QPU

You can view your access to IonQ systems in the “Backends” tab of the IonQ Cloud Console. Before submitting to any QPU,
we recommend testing your code on a simulator (including with noise model) and following the other steps in the
[QPU submission checklist](https://docs.ionq.com/guides/qpu-submission-checklist.mdx) to confirm your access and the QPU availability.

To run a circuit on a QPU, use the same setup as before, just with a different device ID:

```python
from qbraid.runtime import IonQProvider

provider = IonQProvider()
device = provider.get_device("qpu.aria-1")
```

Verify that the device is `ONLINE`:

```python
print(device.status())
```

View device characterization data including the connectivity, fidelity, timings, and more:

```python
print(device.profile.characterization)
```

Next, construct your quantum program, ensuring it aligns with the device’s [supported gateset](#supported-gates).
In this example, we'll define GHZ state circuit using OpenQASM 3:

```python
qasm = """
OPENQASM 3.0;
qubit[3] q;
h q[0];
cx q[0], q[1];
cx q[0], q[2];
"""
```

### Estimate Cost

You can use the `device.run()` method with the `dry_run=True` option to obtain a cost estimate for the anticipated job
without actually executing the program on a QPU.

```python
job = device.run(qasm, name="GHZ (Dry run)", shots=100, dry_run=True)

job.wait_for_final_state()

metadata = job.metadata()
cost_usd = metadata["cost_usd"]

print(f"Cost Estimate (USD): {cost_usd}")
```

If you plan to run your job with [debiasing](https://ionq.com/resources/debiasing-and-sharpening), be sure to include the
`error_mitigation` parameter in the preflight submission to ensure it is accounted for in the cost estimate:

```python
job = device.run(..., preflight=True, error_mitigation={"debias": True})
```

### Submit to QPU

When you are ready to submit the job on the QPU, simply set `preflight=False`, or don't specify any `preflight` value.
Optionally include job tags or other metadata for your convenience, specifying up to 10 key-value pairs.

```python
job = device.run(qasm, name="GHZ", shots=100, metadata={"key": "str_value"})
```

When submitting jobs to a QPU, your job may need to wait in the queue. You can print and record the job’s unique ID,
which can be used to retrieve the job (including its status and results) at a later time, see [Retrieve a job](#retrieve-a-job).

```python
print(job.id)
```

Check the status of your job:

```python
print(job.status())
```

Once the job is `COMPLETED`, you can retrieve the results:

```python
result = job.result()

counts = result.data.get_counts(decimal=True)

print(f"Counts: {counts}")

print(f"Details: {result.details}")
```

## Submit a multi-circuit job

The flexibility of qBraid-SDK allows you to write your circuit not just in OpenQASM, but in Qiskit, Cirq, Amazon Braket, PyTKET,
or any other [registered program type](https://docs.qbraid.com/v2/sdk/user-guide/programs#quantum-program-registry) that can be
[transpiled](https://docs.qbraid.com/v2/sdk/user-guide/transpiler) to qBraid's `qasm2` or `qasm3` format.

In this example, we'll install the `qiskit` and `cirq` extras,

```bash
pip install 'qbraid[qiskit,cirq]'
```

and submit a [multi-circuit job](https://docs.ionq.com/api-reference/v0.3/multicircuit-jobs) containing one of each program type:

```python
import cirq

from qbraid.runtime import IonQProvider
from qiskit import QuantumCircuit

provider = IonQProvider()
device = provider.get_device("simulator")

# Define a bell state in qiskit
qiskit_bell = QuantumCircuit(2)
qiskit_bell.h(0)
qiskit_bell.cx(0, 1)

# Define a bell state in cirq
cirq_bell = cirq.Circuit()
q0, q1 = cirq.LineQubit.range(2)
cirq_bell.append(cirq.H(q0))
cirq_bell.append(cirq.CNOT(q0, q1))

circuit_batch = [qiskit_bell, cirq_bell]

job = device.run(circuit_batch, shots=1000, noise={"model": "aria-1"})

result = job.result()
counts_batch = result.data.get_counts()

print("\n".join(f"Circuit {i}: {c}" for i, c in enumerate(counts_batch)))
```

This script submits two quantum circuits in a single job. When the job completes, it prints the counts for each circuit:

```bash
Circuit 0: {'00': 492, '01': 4, '10': 3, '11': 501}
Circuit 1: {'00': 482, '01': 6, '10': 6, '11': 506}
```

All of the necessary program type conversions are carried out automatically within the `device.run()` method. However, you can also perform
this "transpile" step manually, if needed (e.g. to inspect the ultimate OpenQASM submission format). This can be done as follows:

```python
from qbraid import transpile

qasm_batch = [transpile(circuit, "qasm2") for circuit in circuit_batch]

jobs = device.run(qasm_batch, shots=1000, ...)
```

qBraid offers native support for 10 major quantum programming libraries including 20+ inter-library conversions. For more details, including
how to configure your own custom conversions, refer to the [qBraid transpiler documentation](https://docs.qbraid.com/v2/sdk/user-guide/transpiler).

## Manage jobs

### Retrieve a job

You can retrieve results for a previously run job using its job ID. You can save the job ID after submitting a job
(as in the QPU example above) or copy it from the “ID” column in the “My Jobs” tab on the [IonQ Cloud Console](https://cloud.ionq.com/jobs).

```python
from qbraid.runtime import IonQJob, IonQProvider

job_id = "..."

provider = IonQProvider()

job = IonQJob(job_id, provider.session)

result = job.result()

print(result.data.get_counts())
```

### Cancel a job

You can cancel a job while it’s waiting in the queue:

```python
job.cancel()
```

## Visualize Results

To plot the results of a job, first, install the qBraid visualization extra:

```bash
pip install 'qbraid[visualization]'
```

You can visualize the histogram counts data using `plot_histogram`, or display the probability distribution with `plot_distribution`.

```python
from qbraid.visualization import plot_histogram

plot_histogram(counts)
```

The "counts" input may be either a single dictionary or a list of dictionaries for multi-circuit jobs. In the latter case, histogram data
for each circuit will be plotted side-by-side. The X-axis labels will display in decimal if you set `decimal=True` when retrieving measurement
counts with `get_counts()`. If `decimal=False` or left unspecified, the default quantum state labels in hexadecimal will be used.
See [Plot Experimental Results](https://docs.qbraid.com/v2/sdk/user-guide/visualization#plot-experimental-results) for more.

## Supported gates

For actual execution, gates will be compiled into optimal operations for our trapped ion hardware. For convenience,
IonQ provide a more expressive gateset for programming. However, not all gates supported by the OpenQASM 3 standard library
are accepted by IonQ backends. See full list of [supported gates](https://docs.ionq.com/api-reference/v0.3/writing-quantum-programs#supported-gates).

You can also view a list of the OpenQASM gates supported by a given device directly from an `IonQDevice`. For example:

```python
device = provider.get_device("qpu.forte-1")

print(device.profile.basis_gates)
```

Which would return:

```bash
{'swap', 'tdg', 't', 'gpi2', 'gpi', 'rz', 'sx', 'z', 's', 'sdg', 'zz', 'cx', 'rx', 'y', 'h', 'ry', 'x', 'sxdg'}
```

Note: the returned gateset includes both the abstract QIS and IonQ-native gates supported by the device; however, circuits must be constructed
using either exclusively QIS gates or exclusively native gates—you cannot mix the two within a single circuit. In the next section, we’ll
explore using IonQ native gates in greater detail.

## Native Gates

Building and submitting circuits using IonQ's hardware-native gateset enables you to bypass our compiler and optimizer, providing more control
and transparency than the default abstract gateset (though often at the cost of performance and convenience).

Before working with native gates in qBraid, we recommend reviewing our guides on [Getting Started with Native Gates](https://docs.ionq.com/guides/getting-started-with-native-gates)
and the [IonQ Native Gates API](https://docs.ionq.com/api-reference/v0.3/native-gates-api).

<Warning>
  This is an advanced-level feature. Using the hardware-native gate interface
  without a thorough understanding of quantum circuits is likely to result in
  less-optimal circuit structure and worse algorithmic performance overall than
  using our abstract gate interface.
</Warning>

IonQ's native gates are incorporated as a natural extension of the OpenQASM standard library within the `qbraid[ionq]` runtime integration.
qBraid supports the following IonQ native gates:

- `gpi(phi)`
- `gpi2(phi)`
- `ms(phi0, phi1, theta=0.25)` for Aria systems
- `zz(theta)` for Forte systems

For more details about these gate definitions and parameters, refer to the [native gates guide](https://docs.ionq.com/guides/getting-started-with-native-gates#introducing-the-native-gates).

<Tip>
  The parameters in the IonQ native gate specification are always defined in
  *turns*, not in radians. One turn is 2π radians.
</Tip>

Native gate circuits can then be built and executed as follows:

```python
from qbraid.runtime import IonQProvider

provider = IonQProvider(api_key="YOUR_API_KEY")

device = provider.get_device("simulator")

qasm = """
OPENQASM 3.0;
qubit[3] q;
gpi(0.5) q[0];
gpi2(0) q[1];
ms(0,0.5) q[1], q[2];
"""

job = device.run(qasm, shots=1000)
```

<Tip>
  Each quantum circuit submitted to the IonQ Cloud must use a consistent gateset
  throughout--you cannot mix and match native gates and abstract gates in the
  same circuit.
</Tip>

The `qbraid[ionq]` runtime integration does not currently support automatic transpilation from abstract to native gates, but we may add this
capability in the future. For now, we recommend following this general procedure (also described in IonQ's main [native gates guide](https://docs.ionq.com/guides/getting-started-with-native-gates#converting-to-native-gates))
or using a different SDK.

---

## Additional resources

_Great work!_ You successfully ran your first quantum circuits - _what next?_

Explore more resources for using qBraid:

- [API Reference](https://qbraid.github.io/qBraid/)
- [Source Code on GitHub](https://github.com/qBraid/qBraid)
- [Example Notebooks on GitHub](https://github.com/qBraid/qbraid-lab-demo)

Find examples for using IonQ systems with other quantum programming libraries:

- [IonQ Runtime Provider Notebook on GitHub](https://github.com/qBraid/qbraid-lab-demo/blob/main/Provider-Jobs/qbraid_runtime_ionq_provider.ipynb)
- [IonQ Samples Library on GitHub](https://github.com/ionq-samples/getting-started)
