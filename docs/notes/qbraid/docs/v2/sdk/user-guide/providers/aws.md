> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/providers/aws.md](https://docs.qbraid.com/v2/sdk/user-guide/providers/aws.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 0dbb88d34a28fcaa8e412299cfbabcd9c8417a7ed02401f0ef3cfb1bf1daa71f.

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

# Amazon Braket

> The Amazon Braket submission path: how compilation, qubit placement, bit ordering, and Braket runtime options work for every aws:* device on qBraid, plus Braket's SV1 and DM1 simulators.

<Info>
  Using your own AWS account? See [Amazon Braket
  (self-managed)](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/aws).
</Info>

Every device whose ID starts with `aws:` goes through Amazon Braket, using qBraid's AWS account. You need only a qBraid API key, and jobs are billed in qBraid credits. Each vendor's page covers what's specific to its devices; this page covers what every `aws:*` device has in common.

| Device ID                        | Device                                                            |
| :------------------------------- | :---------------------------------------------------------------- |
| `aws:aws:sim:sv1`                | SV1 state-vector simulator, up to 34 qubits                       |
| `aws:aws:sim:dm1`                | DM1 density-matrix simulator, up to 17 qubits |
| `aws:aqt:qpu:ibex-q1`            | [AQT](https://docs.qbraid.com/v2/sdk/user-guide/providers/aqt) IBEX Q1                   |
| `aws:ionq:qpu:forte-1`           | [IonQ](https://docs.qbraid.com/v2/sdk/user-guide/providers/ionq) Forte-1                 |
| `aws:ionq:qpu:forte-enterprise-1` | [IonQ](https://docs.qbraid.com/v2/sdk/user-guide/providers/ionq) Forte Enterprise-1     |
| `aws:iqm:qpu:garnet`             | [IQM](https://docs.qbraid.com/v2/sdk/user-guide/providers/iqm) Garnet                    |
| `aws:iqm:qpu:emerald`            | [IQM](https://docs.qbraid.com/v2/sdk/user-guide/providers/iqm) Emerald                   |
| `aws:quera:qpu:aquila`           | [QuEra](https://docs.qbraid.com/v2/sdk/user-guide/providers/quera) Aquila                |
| `aws:rigetti:qpu:cepheus-1-108q` | [Rigetti](https://docs.qbraid.com/v2/sdk/user-guide/providers/rigetti) Cepheus-1-108Q    |

SV1 and DM1 are Amazon's own simulators, available only through this path.

```python
from qbraid.runtime import QbraidProvider

provider = QbraidProvider()
device = provider.get_device("aws:aws:sim:sv1")

bell = """
OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
bit[2] c;
h q[0];
cx q[0], q[1];
c = measure q;
"""

job = device.run(bell, shots=100)
print(job.result().data.get_counts())
```

## How Braket compiles your circuit

When you submit to an `aws:*` device, qBraid converts your circuit to OpenQASM, relays it to Amazon Braket, and Braket's service compiles it for the target hardware: decomposition to the device's native gates, mapping your logical qubits onto physical qubits, and routing. You write standard gates against qubits `0..n-1`; the compiler decides where they run.

For example, [IQM](https://docs.qbraid.com/v2/sdk/user-guide/providers/iqm) Emerald and Garnet execute exactly two native gates, `prx` (phased x-rotation) and `cz`. An `rx(θ)` becomes a single `prx(θ, 0)`, an `ry(θ)` becomes `prx(θ, π/2)`, `cx` becomes a `prx`-conjugated `cz`, and `rz` costs nothing at all — it is applied virtually, by adjusting the phase of subsequent `prx` pulses.

## Bit ordering and classical registers

Two facts determine how to read your counts:

1. **Explicit classical-register mappings are honored.** A program with `c[1] = measure q[0];` returns bits in classical-register order, not qubit order.
2. **qBraid counts are little-endian: `c[0]` is the rightmost bit.** Amazon Braket natively reports `c[0]` leftmost; qBraid reverses each key to match the convention used by Qiskit.

Concretely, running `x q[0]` on a two-qubit circuit on IQM Emerald:

```python
qasm = """
OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
bit[2] c;
x q[0];
c[0] = measure q[0];
c[1] = measure q[1];
"""

job = device.run(qasm, shots=10)
job.wait_for_final_state()
print(job.result().data.get_counts())
# {'01': 10}   <- c[1] c[0], so c[0]=1 is the rightmost bit
```

Swapping the mapping (`c[1] = measure q[0]; c[0] = measure q[1];`) flips the result to `{'10': 10}` — the register mapping, not the qubit index, is what the bitstring follows.

<Note>
  Results are always reported in your circuit's logical/classical frame. Even
  though the compiler may place your two-qubit circuit on, say, physical qubits
  21 and 34 of a 54-qubit lattice, the returned bitstrings are indexed by your
  classical bits, with the physical placement undone. To see where your circuit
  actually ran, retrieve the compiled program below.
</Note>

## Retrieving the compiled program

For completed jobs on IQM and Rigetti devices, the program that actually executed on the QPU — native gates on **physical** qubits, plus the measurement mapping back to your classical bits — is stored alongside your submitted program and results, and served by a dedicated endpoint:

```text
GET /jobs/{job_qrn}/compiled-program
```

The response has the same `{format, data}` shape as the submitted program (`GET /jobs/{job_qrn}/program`), so you always know what language you are reading — `qasm3` for IQM, `quil` for Rigetti. From the job:

```python
job.wait_for_final_state()
compiled = job.compiled_program()
print(compiled.format)   # "qasm3"
print(compiled.data)
```

`compiled_program()` returns `None` when no compiled program exists — the job is not yet complete, it predates this feature, or the device does not report one. A batch job returns a list, one program per circuit in submission order.

For the `x q[0]` example above on IQM Emerald, this returns:

```text
OPENQASM 3.0;
bit[2] c;
#pragma braket verbatim
box {
prx(1.0*pi,0) $21;
}
c[1] = measure $34;
c[0] = measure $21;
```

Everything the compiler decided is visible here: logical `q[0]` was placed on physical qubit `$21` (the `$` prefix denotes physical qubits), idle `q[1]` on `$34`, the `x` was compiled to a single `prx`, and the trailing `measure` statements record exactly which physical qubit feeds each classical bit.

<Note>
  Each job is compiled independently, against the device's calibration at
  execution time. Two submissions of the identical circuit may land on different
  physical qubits. If your experiment needs a fixed placement, use verbatim
  compilation through [self-managed Amazon Braket](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/aws), or
  check the compiled program after each run.
</Note>

## Braket runtime options

The `runtime_options` dict on `device.run()` is forwarded as keyword arguments to Braket's own [`AwsDevice.run`](https://amazon-braket-sdk-python.readthedocs.io/en/latest/_apidoc/braket.aws.aws_device.html), so Braket-specific submission options work through qBraid:

| Option                      | Effect                                                                                                                               |
| :-------------------------- | :----------------------------------------------------------------------------------------------------------------------------------- |
| `disable_qubit_rewiring`    | Ask Braket not to remap your qubit indices to different physical qubits.                                                             |
| `device_parameters`         | Vendor-specific device parameter overrides, passed through to the Braket task.                                                       |
| `experimental_capabilities` | Set to `"ALL"` to enable Braket experimental capabilities (e.g. local detuning on analog devices, dynamic circuits where supported). |

```python
job = device.run(
    circuit,
    shots=100,
    runtime_options={"disable_qubit_rewiring": True},
)
```

<Warning>
  `disable_qubit_rewiring` is documented by AWS for **Rigetti** devices, and AWS
  notes that some providers ignore it (IonQ and AQT, for instance, always run
  all-to-all or verbatim). Its behavior on IQM devices is not documented by AWS.
  When exact physical placement matters, verify it via the compiled program
  rather than assuming the flag was honored.
</Warning>

### Verbatim compilation

Amazon Braket supports [verbatim compilation](https://docs.aws.amazon.com/braket/latest/developerguide/braket-constructing-circuit.html#verbatim-compilation) — `#pragma braket verbatim` boxes containing native gates on explicit physical qubits, which skip the compiler entirely — on IQM, Rigetti, IonQ, and AQT devices. Verbatim boxes do **not** currently survive the QbraidProvider conversion pipeline: submit verbatim circuits through [self-managed Amazon Braket](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/aws) with your own AWS credentials, where Braket `Circuit` objects are passed to the service unmodified.

## Related links

- [Amazon Braket (self-managed)](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/aws): `BraketProvider` with your own AWS account, including verbatim compilation
- [Device calibrations and connectivity](https://docs.qbraid.com/v2/sdk/user-guide/providers/calibrations): live calibration data for choosing qubits
- [Runtime Options](https://docs.qbraid.com/v2/sdk/user-guide/runtime/options): device-level options common to all providers
- [Pricing](https://docs.qbraid.com/v2/home/pricing): per-task \+ per-shot pricing for Braket-backed devices
- [AWS: Verbatim compilation](https://docs.aws.amazon.com/braket/latest/developerguide/braket-openqasm-verbatim-compilation.html)
- [AWS: OpenQASM support on Braket](https://docs.aws.amazon.com/braket/latest/developerguide/braket-openqasm-supported-features.html)
