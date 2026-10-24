> Full piece: [https://docs.qbraid.com/v2/algorithms/user-guide/overview.md](https://docs.qbraid.com/v2/algorithms/user-guide/overview.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 e4d3d15220c0bb5bb672aeb5fc1169c80799536f682c8b09d1af063977a165af.

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
    src="/v2/algorithms/_static/algos_banner.png"
    alt="qBraid-ALGOS"
    style={{ width: "200", height: "auto", margin: "0" }}
    className="block dark:hidden"
  />
  <img
    src="/v2/algorithms/_static/algos_banner_dark.png"
    alt="qBraid-ALGOS"
    style={{ width: "200", height: "auto", margin: "0" }}
    className="hidden dark:block"
  />
</div>

<div style={{ textAlign: "center", marginTop: "-8px" }}>
  _Quantum Algorithms Library._
</div>

Python package for building, simulating, and benchmarking hybrid quantum-classical algorithms.

## Installation

qbraid-algorithms requires Python 3.11 or greater, and can be installed with pip as follows:

```bash
pip install qbraid-algorithms
```

### Install from source

You can also install from source by cloning this repository and running a pip install command
in the root directory of the repository:

```bash
git clone https://github.com/qBraid/qbraid-algorithms.git
cd qbraid-algorithms
pip3 install .
```

## Check version

You can view the version of qbraid-algorithms you have installed within a Python shell as follows:

```python
import qbraid_algorithms

qbraid_algorithms.__version__
```

## Supported Algorithms

<Tabs>
  <Tab title="Bernstein-Vazirani">
    <CodeGroup>
      ```python Usage
      from qbraid_algorithms import bernstein_vazirani
      secret_key = '01001'
      algo = bernstein_vazirani.generate_program(secret_key)
      print(algo)
      ```
      ```output Output
       OPENQASM 3.0;
       include "stdgates.inc";
       def bernvaz(qubit[5] q, qubit[1] ancilla) {
         int[32] s = 18;
         int[16] n = 5;
         for int i in [0:n - 1] {
           h q[i];
         }
         x ancilla[0];
         h ancilla[0];
         for int i in [0:n - 1] {
           if (s >> i & 1) {
             cx q[i], ancilla[0];
           }
         }
         for int i in [0:n - 1] {
           h q[i];
         }
       }
       qubit[5] q;
       qubit[1] ancilla;
       bit[5] b;
       bernvaz(q, ancilla);
       b = measure q;
      ```
    </CodeGroup>
  </Tab>
  <Tab title="Quantum Fourier Transform (QFT)">
    <CodeGroup>
      ```python Usage
      from qbraid_algorithms import qft
      algo = qft.generate_program(4)
      print(algo)
      ```
      ```output Output
       OPENQASM 3.0;
       include "stdgates.inc";
       def qft(qubit[4] q) {
         int n = 4;
         for int[16] i in [0:n - 1] {
           h q[i];
           for int[16] j in [i + 1:n - 1] {
             int[16] k = j - i;
             cp(2 * pi / (1 << k + 1)) q[j], q[i];
           }
         }
         for int[16] i in [0:(n >> 1) - 1] {
           swap q[i], q[n - i - 1];
         }
       }
       qubit[4] q;
       bit[4] b;
       qft(q);
       b = measure q;
      ```
    </CodeGroup>
  </Tab>
  <Tab title="Inverse QFT">
    <CodeGroup>
      ```python Usage
      from qbraid_algorithms import iqft
      algo = iqft.generate_program(4)
      print(algo)
      ```
      ```output Output
       OPENQASM 3.0;
       include "stdgates.inc";
       def iqft(qubit[4] q) {
         int n = 4;
         for int[16] i in [0:n - 1] {
           int[16] target = n - i - 1;
           for int[16] j in [0:n - target - 2] {
             int[16] control = n - j - 1;
             int[16] k = control - target;
             cp(-2 * pi / (1 << k + 1)) q[control], q[target];
           }
           h q[target];
         }
         for int[16] i in [0:(n >> 1) - 1] {
           swap q[i], q[n - i - 1];
         }
       }
       qubit[4] q;
       bit[4] b;
       iqft(q);
       b = measure q;
      ```
    </CodeGroup>
  </Tab>
  <Tab title="Quantum Phase Estimation">
    <CodeGroup>
      ```python Usage
      from qbraid_algorithms import qpe

      """
      Path to a qasm file defining the unitary gate U.

      Eg. -
      OPENQASM 3.0;
      include "stdgates.inc";

      gate custom_t q {
          p(pi/4) q;
      }
      """
      unitary_filepath = "gate.qasm"

      """
      Path to a qasm file defining the eigenstate preparation gate.

      Eg. -
      OPENQASM 3.0;
      include "stdgates.inc";

      gate prep q {
          x q;
      }
      """
      eigen_state_filepath = "eigen_state.qasm"

      algo = qpe.generate_program(num_qubits = 4, unitary_filepath=unitary_filepath,
                  psi_filepath=eigen_state_filepath)
      print(algo)
      ```
      ```output Output
       OPENQASM 3.0;
       include "stdgates.inc";
       def iqft(qubit[4] q) {
         int n = 4;
         for int[16] i in [0:n - 1] {
           int[16] target = n - i - 1;
           for int[16] j in [0:n - target - 2] {
             int[16] control = n - j - 1;
             int[16] k = control - target;
             cp(-2 * pi / (1 << k + 1)) q[control], q[target];
           }
           h q[target];
         }
         for int[16] i in [0:(n >> 1) - 1] {
           swap q[i], q[n - i - 1];
         }
       }
       gate custom_t q {
         p(pi / 4) q;
       }
       gate CU a, b {
         ctrl @ custom_t a, b;
       }
       def qpe(qubit[4] q, qubit[1] psi) {
         int n = 4;
         for int i in [0:n - 1] {
           h q[i];
         }
         for int j in [0:n - 1] {
           int[16] k = 1 << j;
           for int m in [0:k - 1] {
             CU q[j], psi[0];
           }
         }
         iqft(q);
       }
       qubit[4] q;
       qubit[1] psi;
       bit[4] b;
       gate prep_eigenstate q {
         x q;
       }
       qpe(q, psi);
       b = measure q;
      ```
    </CodeGroup>

  </Tab>
</Tabs>

See [API Reference](https://qbraid.github.io/qbraid-algorithms/api/qbraid_algorithms.html) for complete functionality of each algorithm module.
