> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/providers/quobly.md](https://docs.qbraid.com/v2/sdk/user-guide/providers/quobly.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 842d22e48e0fac2b0d8f7e0a42a8bc00ecf766496755d1bb00d1ce059c8518af.

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

# Quobly Alloy Forge

> Running circuits against Quobly's silicon spin-qubit emulator through the QbraidProvider, with and without the Pioneer hardware noise model.

<Info>
  Device ID: `qbraid:quobly:sim:alloy-forge` &nbsp;·&nbsp; 10 qubits
  &nbsp;·&nbsp; silicon spin qubits &nbsp;·&nbsp; free to run &nbsp;·&nbsp; accessed through
  [`QbraidProvider`](https://docs.qbraid.com/v2/sdk/user-guide/providers/getting-started)
</Info>

Alloy Forge is Quobly's physics-based emulator of **Pioneer**, their 10-qubit silicon spin-qubit
QPU. Quobly builds qubits from electron spins in silicon, manufactured on standard CMOS processes,
so the error model the emulator reproduces is a semiconductor one rather than the superconducting
or trapped-ion behavior you may be used to.

The emulator goes wider than the hardware: **10 qubits**, in both noiseless and noisy modes, on a
**linear nearest-neighbor** coupling map.

<Note>
  Alloy Forge currently costs **0 credits** to run. You still need a qBraid API key, but no
  Quobly account and no payment. See [Pricing](https://docs.qbraid.com/v2/home/pricing).
</Note>

## Quick start

```python
from qbraid.runtime import QbraidProvider
from qiskit import QuantumCircuit

provider = QbraidProvider()
device = provider.get_device("qbraid:quobly:sim:alloy-forge")

circuit = QuantumCircuit(2)
circuit.h(0)
circuit.cx(0, 1)
circuit.measure_all()

job = device.run(circuit, shots=200)
print(job.result().data.get_counts())
# {'00': 106, '11': 92, '01': 1, '10': 1}
```

One thing in that output surprises almost everyone: the distribution is **not clean**, because
[noise is on by default](#noise-is-on-by-default).

## Runtime options

Alloy Forge takes three device options. They are passed as a dict through **`runtime_options`**,
not as keyword arguments:

| Option  | Type   | Default  | Effect                                                     |
| :------ | :----- | :------- | :--------------------------------------------------------- |
| `shots` | int    | —        | 1 to **1000**. Passed directly to `run()`, not in the dict. |
| `noise` | bool   | `True`   | Apply the Pioneer hardware noise model.                    |
| `seed`  | int    | `None`   | Seed the sampler. Makes noisy runs exactly reproducible.   |

<Warning>
  **Device options do not go in the signature.** This raises `TypeError`:

```python
job = device.run(circuit, shots=200, noise=False)
# TypeError: QbraidDevice.submit() got an unexpected keyword argument 'noise'
```

Put them in `runtime_options` instead:

```python
job = device.run(circuit, shots=200, runtime_options={"noise": False, "seed": 42})
```

`shots` is the exception — it is a first-class argument of `run()`. The options documented on the
[Runtime Options](https://docs.qbraid.com/v2/sdk/user-guide/runtime/options) page (`transpile`, `transform`, `validate`,
`prepare`) are a different thing again: those are pipeline steps, set with `device.set_options()`.

</Warning>

### noise is on by default

Unlike most simulators on qBraid, Alloy Forge applies its hardware noise model unless you tell it
not to. A plain `device.run(circuit, shots=200)` is a **noisy** run.

```python
ideal = device.run(circuit, shots=200, runtime_options={"noise": False})
noisy = device.run(circuit, shots=200, runtime_options={"noise": True})
```

The distinction is the point of the device — a noiseless run of a Bell pair gives you exactly two
outcomes, while the noisy run shows what Pioneer's silicon spin qubits would actually return.

### seed makes noisy runs reproducible

Two runs with the same `seed` return bit-identical counts, noise included:

```python
opts = {"noise": True, "seed": 42}
device.run(circuit, shots=1000, runtime_options=opts).result().data.get_counts()
# {'00': 513, '11': 484, '10': 3}
device.run(circuit, shots=1000, runtime_options=opts).result().data.get_counts()
# {'00': 513, '11': 484, '10': 3}
```

Use it for anything you need to reproduce: notebooks, tests, tutorials, recorded demos.

## Reading the results

### Counts match your circuit's width

Results come back at your circuit's own width — a two-qubit circuit returns two-bit keys.

Qubit ordering is **little-endian**: qubit 0 is the **rightmost** bit.

```python
circuit = QuantumCircuit(3)
circuit.x(2)
circuit.measure_all()

device.run(circuit, shots=100, runtime_options={"noise": False}).result().data.get_counts()
# {'100': 100}
#   ^ qubit 2
```

## Native gates and the coupling map

Pioneer's native gate set is **`RX`, `RY`, `RZ`** for single-qubit rotations and **`RZZ`** for the
two-qubit interaction. `RZZ` is only physically available between **adjacent** qubits on the
linear array: 0–1, 1–2, 2–3, and so on.

You do not have to write circuits in that gate set. Decomposition happens **inside the emulator**,
after submission:

```python
device.transform(qasm)  # returns the program unchanged -- this is a no-op for Alloy Forge
```

Unlike Rigetti or IonQ, qBraid does not rewrite your gates for this device. An `h`/`cx` circuit
reaches Quobly as `h`/`cx` and Quobly transpiles it to `RX`/`RY`/`RZ`/`RZZ` on its side.

<Note>
  **You do not have to route your own circuits.** A two-qubit gate on non-adjacent qubits is
  accepted and runs, and the counts come back under the qubit indices you wrote.

That is not free, though. To satisfy the connectivity constraint the transpiler places your
logical qubits wherever the chain allows, which can be a long way from the indices you named —
Alloy Forge then reports each bit at the position of the physical qubit that carried it, and
qBraid maps it back for you before returning the result.

What a non-local circuit does cost is **native two-qubit gates**, and the noise model charges for
every one of them. Measured against the Pioneer target:

| Circuit | Two-qubit gates written | `RZZ` after transpilation |
| :------ | ----------------------: | ------------------------: |
| GHZ-6, along the chain  |  5 |  5 |
| GHZ-9, along the chain  |  8 |  8 |
| Star on 8 qubits        |  7 | 22 |
| QFT on 6 qubits         | 15 | 66 |

A chain costs exactly what you wrote. A star costs about three times as much, and a QFT more than
four. If a circuit can be expressed along neighboring pairs `(i, i+1)`, that is the version worth
running — not for correctness, but for fidelity.

</Note>

A GHZ state written as a nearest-neighbor ladder satisfies that constraint with no routing at all:

```python
def ghz(n: int) -> QuantumCircuit:
    qc = QuantumCircuit(n)
    qc.h(0)
    for i in range(n - 1):
        qc.cx(i, i + 1)     # every pair is adjacent
    qc.measure_all()
    return qc
```

## Execution time

Alloy Forge integrates the physics shot by shot, so **the shot count dominates the wall clock**,
more than circuit width does. The same 4-qubit GHZ circuit:

| Shots  | Wall clock |
| :----- | :--------- |
| 100    | 32 s       |
| 1000   | 136 s      |

Roughly 20 seconds of fixed overhead plus a per-shot cost. Across a 2-to-9 qubit GHZ sweep at 200
shots, individual jobs ran from 22 s to 89 s.

<Tip>
  Develop at 100–200 shots and raise it only for the final run. Batch submission is not supported
  on this device (`profile.batch_job_support` is `False`), so a sweep is sequential — budget the
  wall clock before you launch one.
</Tip>

## Example: measuring noise accumulation

Growing a GHZ chain one qubit at a time is a direct read on how quickly the Pioneer error model
accumulates. The metric is the share of shots landing in `|0…0⟩` or `|1…1⟩`, which is 100% for an
ideal GHZ state.

```python
from qbraid.runtime import QbraidProvider
from qiskit import QuantumCircuit

device = QbraidProvider().get_device("qbraid:quobly:sim:alloy-forge")
SHOTS = 200

for n in range(2, 10):
    qc = QuantumCircuit(n)
    qc.h(0)
    for i in range(n - 1):
        qc.cx(i, i + 1)
    qc.measure_all()

    job = device.run(qc, shots=SHOTS, runtime_options={"noise": True, "seed": 1234})
    counts = job.result().data.get_counts()
    population = (counts.get("0" * n, 0) + counts.get("1" * n, 0)) / SHOTS
    print(f"GHZ-{n}: {population:.1%}")
```

Measured on the live device:

| Qubits | Noiseless | Pioneer noise model |
| -----: | :-------- | :------------------ |
|      2 | 100%      | 100%                |
|      3 | 100%      | 98.0%               |
|      4 | 100%      | 92.5%               |
|      5 | 100%      | 84.0%               |
|      6 | 100%      | 78.0%               |
|      7 | 100%      | 62.5%               |
|      8 | 100%      | 47.5%               |
|      9 | 100%      | 29.5%               |

The noiseless column is flat at 100% by construction; the noisy column is the emulator's answer to
"how big a GHZ state can Pioneer hold together?"

## Troubleshooting

| Symptom                                                              | Cause                                                                                                                                           |
| :------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------- |
| `TypeError: submit() got an unexpected keyword argument 'noise'`      | Device options belong in `runtime_options={...}`, not the `run()` signature. See [Runtime options](#runtime-options).                            |
| Counts are narrower or wider than you expected                        | Results come back at your circuit's own width, little-endian. See [Reading the results](#counts-match-your-circuit’s-width).                      |
| A "noiseless" run has extra outcomes                                  | `noise` defaults to `True`. Pass `runtime_options={"noise": False}`.                                                                             |
| A non-local circuit is noisier than you expected                      | Satisfying the linear connectivity costs extra `RZZ` gates. See [Native gates and the coupling map](#native-gates-and-the-coupling-map).                                        |
| Results differ between identical runs                                 | Noise is stochastic. Pass a `seed` to fix it.                                                                                                   |
| A sweep is taking far longer than expected                            | Wall clock scales with shots, and batch submission is unsupported. See [Execution time](#execution-time).                                        |

## Related links

- [QbraidProvider](https://docs.qbraid.com/v2/sdk/user-guide/providers/getting-started): installation, authentication, device discovery
- [Runtime Options](https://docs.qbraid.com/v2/sdk/user-guide/runtime/options): the pipeline options set with `set_options()`
- [Pricing](https://docs.qbraid.com/v2/home/pricing): Alloy Forge is free to run
- [Quantum jobs](https://docs.qbraid.com/v2/lab/user-guide/quantum-jobs): tracking submissions in qBraid Lab
- [Quobly](https://quobly.io): silicon spin qubits on standard CMOS processes
