> Full piece: [https://docs.qbraid.com/v2/algorithms/user-guide/examples.md](https://docs.qbraid.com/v2/algorithms/user-guide/examples.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 26a0cbc30f27a784dcc597e6391e72c926f680a04cfe094a4c2cd530333e2f79.

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

# Usage Examples

## Key Features: Load algorithms as PyQASM modules and QASM files

qBraid Algorithms provides a collection of quantum algorithms that can be loaded
as [PyQASM](https://docs.qbraid.com/v2/pyqasm/user-guide/overview) modules, or
you can generate .qasm files to use them as subroutines in your own circuits.

### Loading Algorithms as PyQASM Modules

To load an algorithm as a [PyQASM module](https://docs.qbraid.com/v2/pyqasm/user-guide/overview#the-qasmmodule-object), use the `load_algorithm` function from the `qbraid_algorithms` package, passing algorithm-specific parameters. For example, to load the Quantum Fourier Transform (QFT) algorithm:

```python
from qbraid_algorithms import qft

qft_module = qft.load_algorithm(3) # Load QFT for 3 qubits
```

Now, you can perform operations with the PyQASM module, such as [unrolling](https://docs.qbraid.com/v2/pyqasm/user-guide/examples#inlining-and-unrolling), and
converting back to a QASM string:

```python
qft_module.unroll()
qasm_str = pyqasm.dumps(qft_module)
```

### Loading Algorithms as `.qasm` Files

In order to utilize algorithms as subroutines in your own circuits, use the
`generate_subroutine` function for your desired algorithm. By passing algorithm-specific parameters, and optionally a desired output path, you can
generate a .qasm file containing a subroutine for the parameterized circuit. For
example, to generate a QFT subroutine for 4 qubits:

```python
from qbraid_algorithms import qft, iqft
path = "path/to/output" # Specify your desired output path
qft.generate_subroutine(4) # Generate 4-qubit QFT in the current directory
iqft.generate_subroutine(4, path=path) # Generate 4-qubit IQFT in specified path

```

To utilize the generated subroutine in your own circuit, include the generated
.qasm file, and call the subroutine on a qubit register of the size specified
when generating the subroutine. For example, after running

```python
qft.generate_subroutine(4)
```

you can append `include "qft.qasm";` to your OpenQASM file, and call the
subroutine. For example:

```qasm
OPENQASM 3.0;
include "qft.qasm";

qubit[4] q;
bit[4] c;

qft(q);
measure q -> c;
```
