> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/visualization.md](https://docs.qbraid.com/v2/sdk/user-guide/visualization.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 703e97e825c5a3f2c1964c8958b31a03628080133c702639c8d649f9d761a22c.

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

# Visualization

> Draw circuit diagrams and plot experimental results, conversion graphs, and more.

<Info>
  API Reference:
  [qbraid.visualization](https://qbraid.github.io/qBraid/api/qbraid.visualization.html)
</Info>

## Draw Circuit Diagrams

qBraid's `circuit_drawer` function takes in any type of supported quantum circuit and draws the corresponding visualization.
Here's an example using `braket` and `cirq`:

```python
from qbraid import random_circuit
from qbraid.visualization import circuit_drawer

circuit = random_circuit("braket")
circuit_drawer(circuit)
# T  : |0| 1 |2|
#
# q0 : -C-C---S-
#       | |
# q1 : -Z-|-Z---
#         |
# q2 : -Z-X-----
#
# T  : |0| 1 |2|

circuit = random_circuit("cirq")
circuit_drawer(circuit)
# 0: ───────────×───Z───
#               │
# 1: ───iSwap───×───────
#       │
# 2: ───iSwap───Y───H───
```

### Draw OpenQASM 3 circuits

The `circuit_drawer` function accepts a string of OpenQASM 3 code and returns a matplotlib figure of the circuit:

```python
from qbraid.visualization import circuit_drawer

program = """
OPENQASM 3;
include "stdgates.inc";
qubit[2] q;
h q[0];
cx q[0], q[1];
"""

circuit_drawer(program)
```

**Note**: The above is the equivalent to calling `pyqasm.draw(..., output="mpl")`

## Plot Experimental Results

Gather the measurement counts and plot the histogram data for any `Result` constructed from `ResultData` of type `qbraid.runtime.GateModelResultData`:

```python
from qbraid.visualization import plot_histogram

counts = result.data.get_counts()
# {'00': 483, '01': 14, '10': 486, '11': 17}

plot_histogram(counts)
```

<div
  style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
>
  <img src="/v2/sdk/_static/histogram.png" width="70%"></img>
</div>

Or, using the same measurement counts data, plot the probability distribution:

```python
from qbraid.visualization plot_distribution

plot_distribution(counts)
```

<div
  style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
>
  <img src="/v2/sdk/_static/distribution.png" width="70%"></img>
</div>

Or, plot a batch of measurement counts for any `list[qbraid.runtime.GateModeResultData]`:

```python
batch_jobs = device.run_batch([circuit0, circuit1], shots=1000)

batch_results = [job.result() for job in batch_jobs]

batch_counts = [result.data.get_counts() for result in batch_results]
# e.g. [{'0': 136, '1': 864}, {'0': 166, '1': 834}]

plot_histogram(batch_counts)
```

<div
  style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
>
  <img src="/v2/sdk/_static/batch_counts.png" width="80%"></img>
</div>

Using the qBraid runtime job and results primitives, experimental data is returned in a standardized format,
facilitating straightforward comparisons and benchmarking of results across different providers and backends.

## Plot Transpiler Conversions

Plot all supported conversions between registered program types available through the `qbraid.transpiler`:

```python
from qbraid import ConversionGraph
from qbraid.visualization import plot_conversion_graph

graph = ConversionGraph()

plot_conversion_graph(graph, legend=True)
```

<div
  style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
>
  <img src="/v2/sdk/_static/conversion_graph.png" width="80%"></img>
</div>

## Plot Runtime Conversion Scheme

Plot the runtime conversion scheme for any `qbraid.runtime.QuantumDevice`.

The `QuantumDevice.scheme` defines the `qbraid.transpiler.ConversionScheme` that will be used to carry out the "transpile" step of the [Quantum Job Submission Process](https://docs.qbraid.com/v2/sdk/user-guide/runtime/components#quantum-job-submission-process).

```python
from qbraid import QbraidProvider
from qbraid.visualization import plot_runtime_conversion_scheme

provider = QbraidProvider()

device = provider.get_device("qbraid:qbraid:sim:qir-sv")

print(device.scheme)
```

By setting the maximum path depth to 1, we ensure the `ConversionGraph` includes only program types (nodes) that are directly connected to the target program type by a single conversion step (edge).

```python
device.update_scheme(max_path_depth=1)

plot_runtime_conversion_scheme(device)
```

<div
  style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
>
  <img src="/v2/sdk/_static/conversion_scheme_depth_1.png" width="80%"></img>
</div>

By setting the maximum path depth to 2, we can see how the `ConversionGraph` is expanded to include program types (nodes) that are at most two conversion steps (edges) away from the target program type.

```python
device.update_scheme(max_path_depth=2)

plot_runtime_conversion_scheme(device)
```

<div
  style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
>
  <img src="/v2/sdk/_static/conversion_scheme_depth_2.png" width="80%"></img>
</div>
