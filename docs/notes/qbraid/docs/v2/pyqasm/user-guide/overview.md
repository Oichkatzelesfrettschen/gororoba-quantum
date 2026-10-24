> Full piece: [https://docs.qbraid.com/v2/pyqasm/user-guide/overview.md](https://docs.qbraid.com/v2/pyqasm/user-guide/overview.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 d78945f36f195cd8c1629773f116055c46b4cb9f8d703f7fc3757493e40375e2.

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
    src="/v2/pyqasm/_static/pyqasm-light.svg"
    alt="PyQASM"
    style={{ width: "300px", height: "auto", margin: "5%" }}
    className="block dark:hidden"
  />
  <img
    src="/v2/pyqasm/_static/pyqasm-dark.svg"
    alt="PyQASM"
    style={{ width: "300px", height: "auto", margin: "5%" }}
    className="hidden dark:block"
  />
</div>

<div style={{ textAlign: "center", marginTop: "-8px" }}>
  _Python toolkit for OpenQASM program analysis, validation and compilation._
</div>

## Motivation

[OpenQASM](https://openqasm.com/) is a powerful language for expressing hybrid quantum-classical programs,
but it lacks a comprehensive tool supporting the full capabilities of the language. PyQASM aims to fill this
gap by building upon the [`openqasm3.parser`](https://github.com/openqasm/openqasm/blob/ast-py/v1.0.1/source/openqasm/openqasm3/parser.py),
and providing support for semantic analysis and utilities for program compilation.

## Installation

PyQASM requires Python 3.10 or greater, and can be installed with pip as follows:

```shell
pip install pyqasm
```

### Optional dependencies

PyQASM offers integrations that require extra (optional) dependencies, which can be installed as follows:

To use the [CLI tool](https://docs.qbraid.com/v2/pyqasm/user-guide/cli), install the `cli` extra:

```shell
pip install 'pyqasm[cli]'
```

To use the [circuit drawer tool](https://docs.qbraid.com/v2/pyqasm/user-guide/circuit-drawer), install the `visualization` extra:

```shell
pip install 'pyqasm[visualization]'
```

### Install from source

You can also install from source by cloning this repository and running a pip install command
in the root directory of the repository:

```shell
git clone https://github.com/qBraid/pyqasm.git
cd pyqasm
pip install .
```

To include optional dependencies when installing from source, use the same "extras_require" format, e.g.

```shell
pip install '.[cli,visualization]'
```

### Check version

You can view the version of pyqasm you have installed within a Python shell as follows:

```python
In [1]: import pyqasm

In [2]: pyqasm.__version__
```

## Using PyQASM

We will use simple QASM strings for demonstrating the core functionalities of `pyqasm` API.

A detailed overview of the supported QASM features can be found in the [Usage Examples](https://docs.qbraid.com/v2/pyqasm/user-guide/examples) section.

### `load` and `dump`

The `load` and `dump` functions are used to read QASM code from a file and write QASM code to a file, respectively.

- **`load`**: Reads QASM code from a file and returns a `QasmModule` object.
- **`dump`**: Writes QASM code from a `QasmModule` object to a file.

```python
import pyqasm

# ensure that the file exists and the path is correct
file_path = "example.qasm"

# Load QASM code from the file into a QasmModule object
module = pyqasm.load(file_path)

# Write QASM code from a QasmModule object to a file
pyqasm.dump(module, "output.qasm")
```

### `loads` and `dumps`

The `loads` and `dumps` functions are used to read QASM code from a string and write QASM code to a string, respectively.

- **`loads`**: Reads QASM code from a string and returns a `QasmModule` object.
- **`dumps`**: Writes QASM code from a `QasmModule` object to a string.

<CodeGroup>
```python Using loads and dumps
import pyqasm

qasm_code = """
OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
bit[2] c;
h q[0];
cx q[0], q[1];
c = measure q;
"""

# Load QASM code from a string into a QasmModule object

module = pyqasm.loads(qasm_code)

# Write QASM code from a QasmModule object to a string

qasm_code = pyqasm.dumps(module)

print(qasm_code)

````

```qasm Output
OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
bit[2] c;
h q[0];
cx q[0], q[1];
c = measure q;
````

</CodeGroup>

### The `QasmModule` object

The `QasmModule` object is the main data structure used to represent a QASM program. The two important
methods of the `QasmModule` object are `validate` and `unroll` -

- `validate` : Used to check the semantic validity of the QASM program represented by the `QasmModule` object.

<CodeGroup>
```python Using validate method
import pyqasm

qasm_str = """
OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
bit[2] c;
h q[0];
cx q[0], q[1];
c = measure q;
"""

module = pyqasm.loads(qasm_str)

module.validate()

````

```python Output
None
````

</CodeGroup>

Raises an exception if the program is not semantically valid and points out the error in the program.

<CodeGroup>
```python Using validate method with invalid QASM code
import pyqasm

qasm_str = """
OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
bit[2] c;
h q[0];
cx q[0], q[1];
c = measure q[3];
"""

module = pyqasm.loads(qasm_str)

module.validate()

````

```bash Output
Traceback (most recent call last):
  ...
ValidationError: Index 3 out of range for register of size 2 in qubit
````

To see the full capabilities of the semantic validation, refer to the [Usage Examples](https://docs.qbraid.com/v2/pyqasm/user-guide/examples) section.

</CodeGroup>

- `unroll` : Used to unroll the QASM program represented by the `QasmModule` object. Also performs semantic validation
  while unrolling the program.

<CodeGroup>
```python Using unroll method
import pyqasm

qasm_str = """
OPENQASM 3.0;
include "stdgates.inc";
qubit[5] q;
bit[5] c;
h q;
cx q[0], q[1];
c = measure q;
"""

module = pyqasm.loads(qasm_str)

module.unroll()

print(pyqasm.dumps(module))

````

```qasm Output
OPENQASM 3.0;
include "stdgates.inc";
qubit[5] q;
bit[5] c;
h q[0];
h q[1];
h q[2];
h q[3];
h q[4];
cx q[0], q[1];
c[0] = measure q[0];
c[1] = measure q[1];
c[2] = measure q[2];
c[3] = measure q[3];
c[4] = measure q[4];
````

</CodeGroup>

      A useful argument for the method is `external_gates` that takes in a list of gate names
      considered external to the program. Only the number of parameters and qubit arguments must
      be declared for validation but the body of the gate is not required in the program.

<CodeGroup>
    ```python Using external_gates
    import pyqasm
    qasm_str = """
    OPENQASM 3.0;
    include "stdgates.inc";
    gate custom (p1) q1, q2, q3 {
        // empty body
    }
    qubit[4] q;
    custom(pi / 2) q[0], q[1], q[2];
    cx q[1], q[2];
    """
    module = pyqasm.loads(qasm_str)
    module.unroll(external_gates=["custom"])

    print(pyqasm.dumps(module))
    ```

    ```qasm Output
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit[4] q;
    custom(1.5707963267948966) q[0], q[1], q[2];
    cx q[1], q[2];
    ```

</CodeGroup>

For more details about the `QasmModule` and its features, please refer to our
[API Reference](https://qbraid.github.io/pyqasm/stubs/pyqasm.QasmModule.html#pyqasm.QasmModule).

[Currently Supported Operations](https://github.com/qBraid/pyqasm/blob/main/src/README.md) for OpenQASM language
features supported, in progress, and planned for future support.

## Contributing

- Interested in contributing code, or making a PR? See
  [CONTRIBUTING.md](https://github.com/qBraid/pyqasm/blob/main/CONTRIBUTING.md)
- For feature requests and bug reports:
  [Submit an issue](https://github.com/qBraid/pyqasm/issues)
- For discussions, and specific questions about pyqasm, or
  other topics, [join our discord community](https://discord.gg/TPBU2sa8Et)
- For questions that are more suited for a forum, post to
  [Quantum Computing Stack Exchange](https://quantumcomputing.stackexchange.com/)
  with the [`pyqasm`](https://quantumcomputing.stackexchange.com/questions/tagged/pyqasm) tag.

## Citation

If you use PyQASM in your research, we kindly request that you cite it appropriately.
The BibTeX entry below is aligned with the latest stable release. For the most up-to-date
citation details, please refer to [CITATION.cff](https://github.com/qBraid/pyqasm/blob/main/CITATION.cff).

```tex
@software{Gupta_PyQASM_Python_package_2026,
author = {Gupta, Harshit and Hill, Ryan James},
license = {Apache-2.0},
month = jul,
title = {{PyQASM: Python toolkit for OpenQASM program analysis and compilation.}},
url = {https://github.com/qBraid/pyqasm},
version = {1.0.4},
year = {2026}
}
```

## License

[Apache-2.0 License](https://www.apache.org/licenses/LICENSE-2.0)
