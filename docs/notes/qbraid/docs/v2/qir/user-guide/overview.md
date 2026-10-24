> Full piece: [https://docs.qbraid.com/v2/qir/user-guide/overview.md](https://docs.qbraid.com/v2/qir/user-guide/overview.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 c3513670f4144b0a4d19a65c4104716e040e29d31649b5e825ccc28aa5001ac3.

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

<div
  style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
>
  <img
    src="/v2/qir/_static/qir_banner.png"
    alt="qBraid-QIR"
    style={{ width: "200", height: "auto", margin: "0" }}
    className="block dark:hidden"
  />
  <img
    src="/v2/qir/_static/qir_banner_dark.png"
    alt="qBraid-QIR"
    style={{ width: "200", height: "auto", margin: "0" }}
    className="hidden dark:block"
  />
</div>

<div style={{ textAlign: "center", marginTop: "-8px" }}>
  _qBraid-SDK extension providing support for QIR conversions._
</div>

## Motivation

<div style={{ display: "flex", alignItems: "center" }}>
  <p style={{ marginRight: "20px" }}>
    This project aims to make <a href="https://www.qir-alliance.org/">QIR</a>{" "}
    representations accessible via the qBraid-SDK{" "}
    <a href="#architecture-diagram">transpiler</a>, and by doing so, open the
    door to language-specific conversions from any and all high-level quantum
    languages [supported](https://docs.qbraid.com/v2/sdk/user-guide/overview/#supported-frontends) by{" "}
    <code>qbraid</code>.
    
    See QIR Alliance: <a href="https://www.qir-alliance.org/qir-book/concepts/why-do-we-need.html"> Why do we need it? </a>
  </p>

  <img
    src="/v2/qir/_static/qir_logo.png"
    alt="QIR Alliance"
    style={{ width: "140px", height: "auto", alignSelf: "flex-start" }}
  className="block dark:hidden"
  />
  <img
    src="/v2/qir/_static/qir_logo_dark.png"
    alt="QIR Alliance"
    style={{ width: "140px", height: "auto", alignSelf: "flex-start" }}
  className="hidden dark:block"
  />
</div>

## Installation

qBraid-QIR requires Python 3.10 or greater, and can be installed with pip as follows:

```shell
pip install qbraid-qir
```

### Optional dependencies

qBraid-QIR offers integrations that require extra (optional) dependencies, which can be installed as follows:

For Cirq to QIR conversions, install the `cirq` extra:

```shell
pip install 'qbraid-qir[cirq]'
```

For OpenQASM 3 to QIR conversions, install the `qasm3` extra:

```shell
pip install 'qbraid-qir[qasm3]'
```

For Qiskit to QIR conversions, install the `qiskit` extra:

```shell
pip install 'qbraid-qir[qiskit]'
```

For Squin to QIR conversions, install the `squin` extra:

```shell
pip install 'qbraid-qir[squin]'
```

### Install from source

You can also install from source by cloning this repository and running a pip install command
in the root directory of the repository:

```shell
git clone https://github.com/qBraid/qbraid-qir.git
cd qbraid-qir
pip install .
```

To include optional dependencies when installing from source, use the same "extras_require" format, e.g.

```shell
pip install '.[qiskit,cirq,qasm3,squin]'
```

## Check version

You can view the version of qbraid-qir you have installed within a Python shell as follows:

```python
In [1]: import qbraid_qir

In [2]: qbraid_qir.__version__
```

## Usage examples

### Qiskit conversions

```python
from qiskit import QuantumCircuit
from qbraid_qir.qiskit import qiskit_to_qir

qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

module = qiskit_to_qir(qc, name="bell")

ir = str(module)
```

### Cirq conversions

```python
import cirq
from qbraid_qir.cirq import cirq_to_qir

q0, q1 = cirq.LineQubit.range(2)

circuit = cirq.Circuit(
  cirq.H(q0),
  cirq.CNOT(q0, q1),
  cirq.measure(q0, q1)
)

module = cirq_to_qir(circuit, name="my-circuit")

ir = str(module)
```

### OpenQASM 3 conversions

```python
from qbraid_qir.qasm3 import qasm3_to_qir

program = """
OPENQASM 3;
include "stdgates.inc";

qubit[2] q;
bit[2] c;

h q[0];
cx q[0], q[1];

measure q[0] -> c[0];
measure q[1] -> c[1];
"""

module = qasm3_to_qir(program, name="my-program")

ir = str(module)
```

[Currently Supported Operations](https://github.com/qBraid/qbraid-qir/tree/main/qbraid_qir/qasm3/README.md)

### QIR to Squin conversions

```python
from qbraid_qir.squin import load
from pyqir import BasicQisBuilder, SimpleModule

mod = SimpleModule("bell", num_qubits=2, num_results=2)
qis = BasicQisBuilder(mod.builder)

qis.h(mod.qubits[0])
qis.cnot(mod.qubits[0], mod.qubits[1])

squin_kernel = load(mod._module)

squin_kernel.print()
```

## Architecture diagram

qBraid-SDK transpiler hub-and-spokes architecture with
qbraid-qir integration (left) mapped to language specific conversion step in QIR abstraction
[layers](https://www.qir-alliance.org/qir-book/concepts/why-do-we-need.html) (right).

<div
  style={{ display: "flex", justifyContent: "center", alignItems: "center" }}
>
  <img
    src="/v2/qir/_static/qir_architecture.png"
    width="150%"
    className="block dark:hidden"
  />
  <img
    src="/v2/qir/_static/qir_architecture_dark.png"
    width="150%"
    className="hidden dark:block"
  />
</div>

## Contributing

- Interested in contributing code, or making a PR? See
  [CONTRIBUTING.md](https://github.com/qBraid/qbraid-qir/blob/main/CONTRIBUTING.md)
- For feature requests and bug reports:
  [Submit an issue](https://github.com/qBraid/qbraid-qir/issues)
- For discussions, and specific questions about qBraid-QIR [join our discord community](https://discord.gg/TPBU2sa8Et)
- For questions that are more suited for a forum, post to
  [Quantum Computing Stack Exchange](https://quantumcomputing.stackexchange.com/)
  with the [`qbraid`](https://quantumcomputing.stackexchange.com/questions/tagged/qbraid) tag.

## Citation

If you use qBraid-QIR in your research, we kindly request that you cite it appropriately.
The BibTeX entry below is aligned with the latest stable release. For the most up-to-date
citation details, please refer to [CITATION.cff](https://github.com/qBraid/qbraid-qir/blob/main/CITATION.cff).

```tex
@software{Gupta_qBraid-QIR_Python_package_2026,
author = {Gupta, Harshit and Hill, Ryan James},
license = {Apache-2.0},
month = may,
title = {{qBraid-QIR: Python package for QIR conversions, integrations, and utilities.}},
url = {https://github.com/qBraid/qbraid-qir},
version = {0.6.0},
year = {2026}
}
```

## Acknowledgements

This project was conceived in cooperation with the Quantum Open Source Foundation ([QOSF](https://qosf.org/)).

<img
  src="/v2/qir/_static/qosf_logo.png"
  alt="Quantum Open Source Foundation"
  style={{ width: "100px", height: "auto", margin: "0" }}
/>

## License

[Apache-2.0 License](https://www.apache.org/licenses/LICENSE-2.0)
