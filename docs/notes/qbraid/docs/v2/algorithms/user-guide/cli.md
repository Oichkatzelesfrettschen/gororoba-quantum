> Full piece: [https://docs.qbraid.com/v2/algorithms/user-guide/cli.md](https://docs.qbraid.com/v2/algorithms/user-guide/cli.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 9c64f87f6eadbf129f0b4667be8dfa38b0a7a762c768affb2d9d9fdc659bcb31.

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

# CLI

## CLI Usage

qBraid Algorithms includes a command-line interface (CLI) for generating quantum algorithm subroutines.
These subroutines can either be saved in `.qasm` files or displayed directly in the terminal, providing
users with a convenient way to access and utilize quantum algorithms.

### Installation

To use the CLI, install with CLI dependencies:

```bash
pip install "qbraid-algorithms[cli]"
```

Or install from source:

```bash
pip install -e ".[cli]"
```

### Generate Subroutines

Generate quantum algorithm subroutines that can be included in other circuits:

- Generate QFT subroutine for 4 qubits

<CodeGroup>
```bash Command
qbraid-algorithms generate qft --qubits 4 --show
```

```output Output
QFT subroutine for 4 qubits generated successfully.
Output: /path/to/qft.qasm
Generated QASM:
--------------------------------------------------
OPENQASM 3.0;
include "stdgates.inc";


def qft(qubit[4] q) {
  int n = 4;
  for int[16] i in [0:n - 1] {
    h q[i];
    for int[16] j in [i + 1:n - 1] {
      int[16] k = j - i;
      cp(2 * pi / (1 << (k + 1))) q[j], q[i];
    }
  }

  for int[16] i in [0:(n >> 1) - 1] {
    swap q[i], q[n - i - 1];
  }
}
--------------------------------------------------
```

</CodeGroup>

- Generate IQFT subroutine for 3 qubits with custom name and show the circuit

<CodeGroup>
```bash Command 
qbraid-algorithms generate iqft -q 3 -o my_iqft.qasm --gate-name my_iqft --show
```

```output Output
QASM:
--------------------------------------------------
OPENQASM 3.0;
include "stdgates.inc";

def my_iqft(qubit[3] q) {
    int n = 3;

    for int[16] i in [0:n-1] {
        int[16] target = n - i - 1;
        for int[16] j in [0:(n - target - 2)] {
            int[16] control = n - j - 1;
            int[16] k = control - target;
            cp(-2 * pi / (1 << (k + 1))) q[control], q[target];
        }
        h q[target];
    }

    for int[16] i in [0:(n >> 1) - 1] {
        swap q[i], q[n - i - 1];
    }
}
--------------------------------------------------
```

</CodeGroup>

- Generate only the oracle for Bernstein-Vazirani

<CodeGroup>

```bash Command
qbraid-algorithms generate bernvaz -s "1001" --oracle-only --show
```

```output Output
Generating Bernstein-Vazirani oracle for secret '1001'...
Bernstein-Vazirani oracle generated successfully.
Output: /path/to/oracle.qasm
Secret string: 1001
Qubits needed: 4 + 1 ancilla
Generated QASM:
--------------------------------------------------
OPENQASM 3.0;
include "stdgates.inc";

def oracle(qubit[4] q, qubit[1] ancilla) {
    int[32] s = 9;
    int[16] n = 4;
    for int i in [0:n - 1] {
        if ((s >> i) & 1) {
            cx q[i], ancilla[0];
        }
    }
}

--------------------------------------------------
```

</CodeGroup>

- Generate a QPE subroutine for phase estimation:

<CodeGroup>
```bash Command 
qbraid-algorithms generate qpe --unitary-file gate.qasm --qubits 3 --show
```

```output Output
QPE subroutine for 3 qubits generated successfully.
Unitary file: /path/to/gate.qasm
Output: /path/to/qpe.qasm
Generated QASM:
--------------------------------------------------
OPENQASM 3.0;
include "stdgates.inc";
include "iqft.qasm";

gate custom_t q {
  p(pi / 4) q;
}

gate CU a, b {
  ctrl @ custom_t a, b;
}


def qpe(qubit[3] q, qubit[1] psi) {
    int n = 3;
    for int i in [0:n-1] {
        h q[i];
    }
    for int j in [0:n-1] {
        int[16] k = 1 << j;
        for int m in [0:k-1] {
            CU q[j], psi[0];
        }
    }
    iqft(q);

}
--------------------------------------------------
```

</CodeGroup>

### Help

Get help for any command:

```bash
qbraid-algorithms --help
qbraid-algorithms generate --help
qbraid-algorithms generate qft --help
qbraid-algorithms generate iqft --help
qbraid-algorithms generate bernvaz --help
```

### Examples

#### Complete Workflow

1. Generate a QFT subroutine:

   ```bash
   qbraid-algorithms generate qft --qubits 3
   ```

2. Generate a Bernstein-Vazirani oracle and view it:

   ```bash
   qbraid-algorithms generate bernvaz --secret "101" --oracle-only --show
   ```

3. Generate an IQFT circuit with custom output:
   ```bash
   qbraid-algorithms generate iqft --qubits 4 --output my_iqft_4.qasm --show
   ```
