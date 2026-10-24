> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/providers/rigetti.md](https://docs.qbraid.com/v2/sdk/user-guide/providers/rigetti.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 2ea573edb1990625cb59416bc57caa98f1a6a71684da095314894a61c2a2a194.

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

# Rigetti

> Run gate-model and timing-aware programs on Rigetti's Cepheus-1-108Q through qBraid, with only a qBraid API key and from any qBraid-supported framework.

<Info>
  Using your own Rigetti QCS account? See [Rigetti
  (self-managed)](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/rigetti).
</Info>

## Devices on qBraid

Rigetti's Cepheus-1-108Q is a 108-qubit superconducting QPU. It is on qBraid through three submission paths. Each path has its own device ID, billing, and compilation behavior.

| Device ID                                | Path                                    | Billing                                     |
| :--------------------------------------- | :-------------------------------------- | :------------------------------------------ |
| `rigetti:rigetti:qpu:cepheus-1-108q`     | Direct                                  | Per minute of execution, in qBraid credits  |
| `aws:rigetti:qpu:cepheus-1-108q`         | [Amazon Braket](#through-amazon-braket) | Per task and per shot, in qBraid credits    |
| `openquantum:rigetti:qpu:cepheus-1-108q` | [Open Quantum](#through-open-quantum)   | Open Quantum credits                        |

Most of this page covers the **direct submission path**, `rigetti:rigetti:qpu:cepheus-1-108q`, which goes from qBraid straight to Rigetti. You write a circuit in whichever framework you already use, hand it to `device.run()`, and qBraid handles conversion, compilation, submission and results.

The one thing about Cepheus that surprises people: **it has two different compilation paths, and which one your program takes depends on whether it contains timing instructions.** Everything else follows from that.

<Note>
  If you are working with delays or other timing operations, use the direct
  submission path documented here. Braket has no gate-level delay, and it
  compiles differently: see [Through Amazon Braket](#through-amazon-braket).
</Note>

## Quick start

A plain gate-model circuit needs nothing special. Write it however you like and submit:

```python
from qbraid.runtime import QbraidProvider
from qiskit import QuantumCircuit

provider = QbraidProvider()
device = provider.get_device("rigetti:rigetti:qpu:cepheus-1-108q")

circuit = QuantumCircuit(2, 2)
circuit.h(0)
circuit.cx(0, 1)
circuit.measure([0, 1], [0, 1])

job = device.run(circuit, shots=10)
job.wait_for_final_state()
print(job.result().data.get_counts())
# {'00': 2, '01': 1, '11': 7}
```

`H` and `CX` are not gates Cepheus can execute. You did not have to care, because this program took the **compiled path**.

## The two compilation paths

Whether your program is compiled for you, or has to arrive ready to run, depends entirely on whether it contains **Quil-T** instructions: Rigetti's timing and pulse-level operations, of which `DELAY` is the one most people meet first.

| Your program                                 | Path         | Compiler                                                 | You must write        |
| :------------------------------------------- | :----------- | :------------------------------------------------------- | :-------------------- |
| Gates only                                   | **compiled** | [quilc](https://github.com/quil-lang/quilc) nativizes it | any gates you like    |
| Contains a delay or other Quil-T instruction | **direct**   | quilc is skipped                                         | **native gates only** |

The reason is not a qBraid limitation. quilc is a gate-model compiler, and as Rigetti's docs put it plainly:

> Quil-T instructions are not supported by quilc or the QVM.

So a program containing `DELAY` cannot go through quilc at all. qBraid detects Quil-T automatically and routes such programs straight to the QCS translation service, which does accept timing instructions. Nothing is dropped and you do not set a flag. But because quilc is what would normally have nativized your gates, **that job is now yours**.

<Warning>
  If a program contains a delay and uses a non-native gate, it fails at translation. Rigetti names the instruction it could not execute:

```text
Translation failed for quantum processor 'Cepheus-1-108Q': ... message:
"input program error: Failed to schedule Quil program: at instruction 0 ("X 0"):
this instruction must be replaced or decomposed prior to compilation"
```

This is the single most common error on this device: your timing program reached the QPU with a gate it cannot execute, here `X 0`. See [Native gates](#native-gates) below.

</Warning>

## Native gates

When you take the direct path, these are the only instructions Cepheus-1-108Q accepts. The set comes from the device's own ISA:

| Instruction | Accepts              | Notes                               |
| :---------- | :------------------- | :---------------------------------- |
| `RX(θ)`     | **only ±π/2 and ±π** | any other angle has no calibration  |
| `RZ(θ)`     | **any angle**        | parametric, so no angle restriction |
| `CZ`        | —                    | the only two-qubit gate             |
| `I`         | —                    | identity                            |
| `MEASURE`   | —                    | readout                             |

The `RX` restriction is the one that catches people, and it follows from the calibrations: Rigetti publishes `DEFCAL`s for `RX` at exactly four angles (`±π/2` and `±π`), while `RZ` is defined parametrically (`DEFCAL RZ(%theta)`) and so takes any angle. A pulse only exists for those `RX` angles, which is why `RX(0)`, `RX(2π)` and `RX(π/4)` are rejected.

`RX(π)` is an `X`; `RX(π/2)` is a half rotation. Arbitrary single-qubit rotations are built from these plus `RZ`, which is exactly the decomposition quilc performs for you on the compiled path.

<Tip>
  Reaching for `X`? Use `RX(π)`: same operation, and it is native:

```python
circuit.rx(np.pi, 0)   # native
circuit.x(0)           # NOT native: fails at translation if the program has a delay
```

</Tip>

### Nativizing a Qiskit circuit automatically

For anything beyond a few gates, let Qiskit do the decomposition. The basis choice is the whole trick: use `["rz", "sx", "x", "cz"]`, because `sx` and `x` map exactly onto the calibrated `RX(π/2)` and `RX(π)` pulses. The seemingly natural `["rx", "rz", "cz"]` basis does not work, since Qiskit then emits `RX` at arbitrary angles, which the QPU rejects. Delays pass through transpilation untouched:

```python
from qiskit import QuantumCircuit, transpile

qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.delay(50, 0, unit="us")
qc.ry(0.7, 1)
qc.measure([0, 1], [0, 1])

native = transpile(qc, basis_gates=["rz", "sx", "x", "cz"], optimization_level=3)

job = device.run(native, shots=100)   # conversion to Quil happens automatically
```

Every gate in the transpiled circuit now lands on a calibrated pulse, so the program passes translation on the direct path with the delay intact. To inspect the exact Quil that will run, convert it yourself first: `qbraid.transpile(native, "pyquil")`.

## Choosing qubits with calibration data

Cepheus is not uniform. On a recent calibration snapshot, two-qubit CZ error ranged from 0.4% on the best edge to 50% on the worst, and readout error varied by an order of magnitude across the lattice. Which physical qubits your program lands on is worth controlling, and the [calibrations API](https://docs.qbraid.com/v2/sdk/user-guide/providers/calibrations) provides the data to control it with.

What happens to the qubit indices you wrote depends, once again, on the compilation path:

- **Compiled path:** quilc is free to move your circuit. If the indices you wrote already satisfy the device's connectivity, quilc's default is `NAIVE` rewiring, which keeps them where they are. If they do not, it falls back to `PARTIAL` rewiring, which chooses a placement using the gate fidelities Rigetti publishes in the device ISA. An unpinned circuit therefore already gets fidelity-aware placement; manual selection is for when you want it deterministic, or want to fold in metrics quilc does not weigh the way you do.
- **Direct path:** no rewiring of any kind. A Quil-T program executes on exactly the physical qubits it names, which makes it the strongest placement guarantee available.

### Scoring edges

The selection is one call. `best_qubits` fetches a fresh calibration snapshot and returns the
qubits maximizing estimated fidelity, folding each qubit's readout and single-qubit gate errors and
the edge's two-qubit gate error into one score:

```python
q0, q1 = device.best_qubits(2)
```

Folding readout in is the point, because the edge with the lowest CZ error is often not the best
place to run. On the snapshot used for the run below, the edge with the lowest raw CZ error
(0.40%) sat on a qubit with weak readout, and a readout-aware score selected a different edge,
(92, 101), with a slightly higher CZ error (0.89%) but readout errors of 1.4% and 1.0%. For
longer chains (`best_qubits(5)` returns a connected path, ready for Qiskit's `initial_layout`),
and for plotting the graph you are choosing from, see
[Choosing the best qubits](https://docs.qbraid.com/v2/sdk/user-guide/providers/calibrations#choosing-the-best-qubits).

### Pinning the circuit

Three ways to make the placement stick, in decreasing order of guarantee:

<CodeGroup>

```python pyQuil, direct path
# A clock-aligned DELAY makes this Quil-T, so quilc is bypassed and the
# program runs on exactly the qubits it names. Native gates required.
from pyquil import Program

program = Program(f"""DECLARE ro BIT[2]
RZ(pi/2) {q0}
RX(pi/2) {q0}
RZ(pi/2) {q0}
RZ(pi/2) {q1}
RX(pi/2) {q1}
RZ(pi/2) {q1}
CZ {q0} {q1}
RZ(pi/2) {q1}
RX(pi/2) {q1}
RZ(pi/2) {q1}
DELAY {q1} 3.2e-8
MEASURE {q0} ro[0]
MEASURE {q1} ro[1]
""")

job = device.run(program, shots=1000)
```

```python Qiskit, direct path
# Physical indices survive conversion when the circuit has a single
# register: qubit i maps to physical qubit i. The 32 ns delay makes the
# converted program Quil-T, same guarantee as the pyQuil version.
from qiskit import QuantumCircuit, transpile

qc = QuantumCircuit(max(q0, q1) + 1, 2)
qc.h(q0)
qc.cx(q0, q1)
qc.delay(32, q1, unit="ns")
qc.measure(q0, 0)
qc.measure(q1, 1)

native = transpile(qc, basis_gates=["rz", "sx", "x", "cz"], optimization_level=3)
job = device.run(native, shots=1000)
```

```python pyQuil, compiled path
# PRAGMA INITIAL_REWIRING pins placement without leaving the compiled
# path: quilc still nativizes your gates but keeps the identity mapping,
# inserting SWAPs only if you request a pair that is not coupled. Put it
# ahead of the first gate (DECLARE may precede it), or set it per run
# with runtime_options={"initial_rewiring": "NAIVE"} -- see Runtime
# options. For a hard no-touch guarantee on a region, wrap the region in
# PRAGMA PRESERVE_BLOCK ... PRAGMA END_PRESERVE_BLOCK instead.
from pyquil import Program

program = Program(f"""PRAGMA INITIAL_REWIRING "NAIVE"
DECLARE ro BIT[2]
H {q0}
CNOT {q0} {q1}
MEASURE {q0} ro[0]
MEASURE {q1} ro[1]
""")

job = device.run(program, shots=1000)
```

</CodeGroup>

<Warning>
  `DELAY` durations must line up with the QPU's sequencer clock, or translation
  rejects the program with `duration not aligned to sequencer clock: 1e-8`. A 10
  ns delay is rejected; 32 ns is accepted. When using a delay purely as a Quil-T
  marker, 3.2e-8 seconds is a safe choice.
</Warning>

Run on hardware, the Bell pair on the score-selected edge (92, 101) returned

```python
job.result().data.get_counts()
# {'00': 480, '11': 423, '01': 58, '10': 39}
```

a correlated fraction of 90.3% at 1000 shots, against roughly 95% predicted from the calibration data alone. The gap is decoherence and crosstalk the snapshot does not capture, which is the right way to read these scores: a ranking, not a forecast.

<Tip>
  Calibration data is refreshed roughly hourly and the ranking moves with it, so
  select your qubits shortly before you submit, not once per project.
</Tip>

## Reading the counts

Bitstrings from this device follow **declared-register order, left to right**: the first character of each counts key is `ro[0]`, the second is `ro[1]`, and so on. A program that excites only the qubit measured into `ro[0]` returns `{'10': N}`.

<Warning>
  This is the opposite convention from Braket-backed devices (`aws:*`), where
  qBraid counts are little-endian with `c[0]` as the **rightmost** bit. If you
  run the same circuit on `rigetti:rigetti:qpu:cepheus-1-108q` and
  `aws:rigetti:qpu:cepheus-1-108q`, asymmetric outcomes appear bit-reversed
  relative to each other. Account for this before comparing distributions across
  the two routes.
</Warning>

If your program declares multiple readout registers, they are concatenated in alphabetical register-name order.

### The compiled program

For completed jobs, the native Quil that quilc actually produced — after nativization and any rewiring — is served by the `GET /jobs/{job_qrn}/compiled-program` endpoint, in the same `{format, data}` shape as the submitted program (here always `quil`):

```python
job.wait_for_final_state()
compiled = job.compiled_program()
print(compiled.data)
```

`compiled_program()` returns `None` for jobs with no stored compiled program (not yet complete, or submitted before this feature).

On the compiled path this is the authoritative record of which physical qubits your circuit ran on and what quilc did to your gates. On the direct (Quil-T) path it is your program as submitted, since quilc is bypassed.

## Timing operations

A delay is what makes a program Quil-T. This is a T1 (energy relaxation) measurement: excite the qubit, wait, and see whether it is still excited:

<CodeGroup>

```python Qiskit
import numpy as np
from qbraid.runtime import QbraidProvider
from qiskit import QuantumCircuit

provider = QbraidProvider()
device = provider.get_device("rigetti:rigetti:qpu:cepheus-1-108q")

circuit = QuantumCircuit(1, 1)
circuit.rx(np.pi, 0)               # native, NOT circuit.x(0)
circuit.delay(500, 0, unit="us")   # makes this a Quil-T program
circuit.measure(0, 0)

job = device.run(circuit, shots=10)
job.wait_for_final_state()
print(job.result().data.get_counts())
# {'0': 9, '1': 1}  -- mostly relaxed to |0> during the 500 us delay
```

```python pyQuil
from pyquil import Program
from qbraid.runtime import QbraidProvider

provider = QbraidProvider()
device = provider.get_device("rigetti:rigetti:qpu:cepheus-1-108q")

program = Program(
    "DECLARE ro BIT[1]",
    "RX(pi) 0",           # native, NOT "X 0"
    "DELAY 0 0.0005",     # 0.0005 seconds = 500 us
    "MEASURE 0 ro[0]",
)

job = device.run(program, shots=10)
job.wait_for_final_state()
print(job.result().data.get_counts())
# {'0': 9, '1': 1}
```

</CodeGroup>

Both submit the same thing. In Quil, `DELAY 0 0.0005` delays qubit 0 by 0.0005 **seconds**; Qiskit's `delay(500, 0, unit="us")` converts to exactly that.

Relaxation is probabilistic, so your counts will differ run to run. A stray `'1'` at 500 us is the physics, not a bug. That variation is exactly what a T1 sweep measures.

<Tip>
  Passing each instruction as its own string, as above, sidesteps a common trap: pyQuil rejects a flat instruction that starts with whitespace (`expected a command or a gate`), so an indented triple-quoted block of plain instructions fails even though it looks fine.

The exception is a block that is _meant_ to be indented, such as a `DEFCAL` or `DEFFRAME` body. Those must arrive as **one** string, indentation included; passed as separate arguments they fail with `failed to parse arguments for DEFCAL`. See [prepend_default_calibrations](#prepend_default_calibrations) for that shape.

</Tip>

To sweep T1, vary the delay and submit one job per point:

```python
delays_us = [0, 50, 100, 200, 400, 800]
jobs = []

for t in delays_us:
    circuit = QuantumCircuit(1, 1)
    circuit.rx(np.pi, 0)
    circuit.delay(t, 0, unit="us")  # keep this even at t=0 -- see below
    circuit.measure(0, 0)
    jobs.append((t, device.run(circuit, shots=1000)))

for t, job in jobs:
    job.wait_for_final_state()
    counts = job.result().data.get_counts()
    p_excited = counts.get("1", 0) / sum(counts.values())
    print(f"{t:>4} us -> P(1) = {p_excited:.3f}")
```

<Warning>
  Keep the `delay` call at `t = 0` rather than skipping it. A circuit with no
  delay is not a Quil-T program, so your zero point would be nativized by quilc
  while every other point bypasses it, leaving a baseline compiled differently
  from the data it anchors. `delay(0)` emits `DELAY 0 0` and keeps every point
  on the same path.
</Warning>

<Note>
  Cepheus-1-108Q is billed **per minute of execution**, prorated with no
  minimum. A delay is execution time, so a long delay costs more than a short
  one. Individual jobs on this device typically run for tens to hundreds of
  milliseconds. See [Pricing](https://docs.qbraid.com/v2/home/pricing).
</Note>

## Which framework?

The device itself accepts three run input types: **pyQuil**, **OpenQASM 2** and **OpenQASM 3**. Qiskit appears throughout this page only because it is the most widely used, not because it is special. It is converted to QASM like anything else.

That means **any framework qBraid can convert to QASM works here**, not just the two shown. Cirq, Amazon Braket, PennyLane, pytket and the rest all reach `qasm2`/`qasm3` on the [ConversionGraph](https://docs.qbraid.com/v2/sdk/user-guide/transpiler), and `device.run()` handles the conversion:

<CodeGroup>

```python Cirq
import cirq

q = cirq.LineQubit.range(2)
circuit = cirq.Circuit([cirq.H(q[0]), cirq.CNOT(q[0], q[1]), cirq.measure(*q, key="m")])
job = device.run(circuit, shots=10)
```

```python Braket
from braket.circuits import Circuit

# .measure() is required here -- see the note below
circuit = Circuit().h(0).cnot(0, 1).measure(0).measure(1)
job = device.run(circuit, shots=10)
```

```python PennyLane
import pennylane as qml

with qml.tape.QuantumTape() as circuit:
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    qml.sample(wires=[0, 1])

job = device.run(circuit, shots=10)
```

</CodeGroup>

If your framework has a path to `qasm2` or `qasm3` on the ConversionGraph, it will run on Cepheus. Write in whichever one you already use.

<Warning>
  **Measure explicitly.** Some frameworks measure implicitly when run on their own simulators, and that implicitness does not survive conversion. An Amazon Braket circuit written as `Circuit().h(0).cnot(0, 1)` converts to QASM with no `measure` statement, so the program reaches the QPU with nothing to read out. It runs, then fails when the results are parsed:

```text
No declared registers found in ro_sources. ro_sources keys: []
```

Add the measurements yourself and the job returns counts as expected.

</Warning>

<Tip>
  `device.supported_run_inputs()` lists every program type alias this device accepts, judged under its own conversion configuration — the fastest answer to "will my framework work here?". For the exact Python type behind each alias, `QPROGRAM_REGISTRY` maps each framework to the object `device.run()` accepts, which is not always the one you would guess (PennyLane, for instance, takes a `QuantumTape` rather than a `QNode`):

```python
from qbraid.programs import QPROGRAM_REGISTRY

print(QPROGRAM_REGISTRY["pennylane"])   # <class 'pennylane.tape.tape.QuantumTape'>
print(QPROGRAM_REGISTRY["cirq"])        # <class 'cirq.circuits.circuit.Circuit'>
print(sorted(QPROGRAM_REGISTRY))        # every framework qBraid knows
```

</Tip>

### When to reach for pyQuil

The one thing QASM cannot express is **Quil-T beyond a simple delay**: `FENCE`, `PULSE`, frame-level `DELAY 0 "rf" 1e-6`, or your own `DEFCAL` calibrations. Those have no vocabulary in Qiskit or QASM, so there is nothing for the transpiler to convert. pyQuil is Rigetti's native language, so nothing is translated and those features have first-class syntax.

An ordinary `delay` is the exception: it converts cleanly from Qiskit, so a T1 or T2 experiment does not require pyQuil.

<Tip>
  Not sure which path your program will take? Ask before you spend a job:

```python
from qbraid.runtime.rigetti.device import contains_quil_t
from pyquil import Program

contains_quil_t(Program("RX(pi) 0\nDELAY 0 0.0005"))   # True  -> direct path, native gates required
contains_quil_t(Program("H 0\nCNOT 0 1"))              # False -> compiled path, quilc handles it
```

</Tip>

## Runtime options

Three options are passed as a dict through `runtime_options`. The first two belong to Rigetti's [translation service](https://docs.rigetti.com/qcs/guides/the-lifecycle-of-a-program), the stage that turns your native-gate program into pulses, and apply on both paths; the third belongs to the quilc stage, so it acts only on the [compiled path](#the-two-compilation-paths). Unrecognized keys are ignored.

| Option                         | Type  | Default | Effect                                                                                             |
| :----------------------------- | :---- | :------ | :------------------------------------------------------------------------------------------------- |
| `passive_reset_delay_seconds`  | float | Rigetti | How long to wait for qubits to relax to \|0⟩ before each shot.                                     |
| `prepend_default_calibrations` | bool  | `True`  | If `False`, Rigetti's default calibrations are **not** prepended.                                  |
| `initial_rewiring`             | str   | quilc   | Qubit-placement strategy for quilc: `NAIVE`, `PARTIAL`, `GREEDY`, or `RANDOM`. Compiled path only. |

### passive_reset_delay_seconds

Between shots, qubits are left to relax back to |0⟩ on their own, a **passive** reset. This option sets how long the QPU waits for that.

Rigetti documents it as "the delay between passive resets, in seconds" and does not publish a default or a recommended range, so the figures below are **measurements from a single run on one qubit**, included to show the shape of the trade-off. Treat them as illustrative; your own numbers will differ with the qubit, the calibration and the day.

**The delay is paid once per shot, and you are billed for it.** The same 20-shot program, changing nothing else:

| `passive_reset_delay_seconds` | Execution observed | Cost observed |
| :---------------------------- | :----------------- | :------------ |
| `0.000001` (1 µs)             | 15 ms              | ~3 credits    |
| `0.01` (10 ms)                | 215 ms             | ~43 credits   |

The 200 ms difference is exactly 20 shots × 10 ms, which is the part that generalizes: **the delay is per shot**, and this device is billed [per minute of execution](https://docs.qbraid.com/v2/home/pricing). Multiply by your shot count before raising it.

What the wait buys is a cleaner starting state. Relaxation is what clears the previous shot. Measuring a qubit at shot start, after a program that deliberately leaves it excited:

| Reset before each shot | Still excited at shot start (observed)   |
| :--------------------- | :--------------------------------------- |
| 1 µs                   | ~5% (the previous shot bleeding through) |
| 1 ms                   | ~1.5% (indistinguishable from baseline)  |

A control that never excited the qubit read 0%, so the 5% was leftover state rather than readout error. Again: one qubit, one run. The effect is the point, not the percentages.

So the trade runs both ways:

- **Raise it** for circuits sensitive to initialization, where a few percent of shots starting in the wrong state would matter.
- **Lower it** to finish sooner and pay less. The floor is what your circuit can tolerate.

```python
job = device.run(
    circuit,
    shots=1000,
    runtime_options={"passive_reset_delay_seconds": 0.0001},  # 100 us
)
```

<Note>
  The translation service rejects delays above roughly **67 ms**, reporting
  `waveform duration of 1e-1s exceeds maximum allowed duration of
  6.7108864e-2s`. That ceiling comes from the service's own error rather than
  published documentation, so do not rely on the exact figure.
</Note>

### prepend_default_calibrations

By default Rigetti prepends its calibration set to every program: the `DEFFRAME` and `DEFCAL` definitions that give `RX`, `RZ`, `CZ` and `MEASURE` their actual pulse shapes. Those definitions are the only reason a gate means anything on hardware.

**Leave this one alone.** It enables nothing, and setting it to `False` only breaks things.

To **override a calibration**, include your own `DEFCAL` and keep this option at its default. Your definition is used in place of Rigetti's. A `DEFCAL` that turns `RX(pi)` into a no-op shows this plainly: the qubit is left in |0⟩ rather than excited.

```python
from pyquil import Program

# A DEFCAL body must be indented, so pass the block as ONE string --
# not as separate arguments (see the note under Timing operations).
program = Program(
    """DEFCAL RX(pi) 0:
    NOP
DECLARE ro BIT[1]
RX(pi) 0
DELAY 0 0
MEASURE 0 ro[0]
"""
)

job = device.run(program, shots=20)   # no runtime_options needed
job.wait_for_final_state()
print(job.result().data.get_counts())
# {'0': 19, '1': 1}   -- the RX did nothing.
# Without the custom DEFCAL the same program reads {'0': 1, '1': 19}.
```

Setting `prepend_default_calibrations=False` only _removes_ the defaults. Your program must then carry a complete calibration set of its own, and there is no practical way to do that here: Rigetti's set defines frames across far more qubits than Cepheus exposes, so submitting it is rejected before it reaches the QPU.

```text
ProgramValidationError: Number of qubits in the circuit (300) exceeds the device's capacity (108)
```

Without a calibration set, translation fails instead, with Rigetti's reason:

```text
input program error: program has no defined frames
```

<Note>
  Custom `DEFFRAME`s are constrained regardless: only `INITIAL-FREQUENCY` and
  `CHANNEL-DELAY` may differ from Rigetti's defaults. Changing anything else,
  such as `SAMPLE-RATE` or `HARDWARE-OBJECT`, is rejected (`frame 0
  "Transmon-0_charge_tx" differs from Rigetti-provided definition`). Rigetti
  restricts the flag that lifts this to [certain
  users](https://docs.rs/qcs/latest/qcs/qpu/translation/struct.TranslationOptions.html),
  and it is not enabled for qBraid. Treat the default frames as fixed and
  confine your customization to `DEFCAL`s.
</Note>

### initial_rewiring

Unlike the two options above, this one acts at the **quilc stage**, so it applies only on the compiled path — a Quil-T program skips quilc and ignores it. It selects the strategy quilc uses to map your logical qubits onto physical ones: the same choice [Choosing qubits](#choosing-qubits-with-calibration-data) describes making with a hand-written `PRAGMA INITIAL_REWIRING`, injected for you per run. A pragma your program already carries takes precedence.

```python
job = device.run(
    circuit,
    shots=1000,
    runtime_options={"initial_rewiring": "GREEDY"},
)
```

Why reach for it: quilc's default `PARTIAL` searches for a placement at a cost that grows steeply with qubit count and is independent of circuit depth, so on a 100+-qubit program the search can dominate compile time. On wide, shallow circuits `GREEDY` compiles roughly an order of magnitude faster with comparable output, and `NAIVE` is fastest when your indices already sit on the lattice. On deeper circuits `PARTIAL` costs about the same as `GREEDY` and produces better output — which is why omitting the key keeps quilc's default. An unrecognized strategy raises `ValueError` naming the supported set before anything is submitted.

## Through Amazon Braket

`aws:rigetti:qpu:cepheus-1-108q` goes through Amazon Braket and is billed per task and per shot, in qBraid credits. Braket compiles your circuit itself, so the two compilation paths above don't apply, and Braket has no gate-level delay. [Amazon Braket](https://docs.qbraid.com/v2/sdk/user-guide/providers/aws) covers how Braket compiles your circuit, how counts are ordered, and how to retrieve the compiled Quil. These devices take [Braket runtime options](https://docs.qbraid.com/v2/sdk/user-guide/providers/aws#braket-runtime-options), such as `disable_qubit_rewiring`.

## Through Open Quantum

`openquantum:rigetti:qpu:cepheus-1-108q` goes through Open Quantum and spends credits from an Open Quantum account linked to qBraid, not qBraid credits. See [Open Quantum](https://docs.qbraid.com/v2/sdk/user-guide/providers/open-quantum) for linking an account and what these devices accept.

## Troubleshooting

Every failure at the translation stage arrives as a `RigettiJobError` naming the processor, followed by Rigetti's own reason, which is the part that tells you what to fix:

```text
Translation failed for quantum processor 'Cepheus-1-108Q': ... message:
"input program error: Failed to schedule Quil program: at instruction 0 ("X 0"):
this instruction must be replaced or decomposed prior to compilation"
```

Read to the end of the line. Rigetti names the offending instruction, here `X 0`, which is not native.

| Rigetti's reason                                         | What happened                                                                                                                                                                                                                                                  |
| :------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `at instruction N (...): must be replaced or decomposed` | A non-native gate reached the QPU, because your program contains a delay and so skipped quilc. Replace `X` with `RX(π)`, `H`/`CX` with `RX`/`RZ`/`CZ` decompositions, or drop the delay to get the compiled path back. Also covers `RX` at a non-native angle. |
| `program has no defined frames`                          | You set `prepend_default_calibrations=False` without supplying a calibration set. Drop the option; see [above](#prepend_default_calibrations).                                                                                                                 |
| `duration not aligned to sequencer clock`                | A `DELAY` duration the hardware clock cannot represent, such as 10 ns. Use a coarser value; 32 ns (`3.2e-8`) is a safe marker delay. See [Pinning the circuit](#pinning-the-circuit).                                                                          |
| `waveform duration ... exceeds maximum allowed duration` | `passive_reset_delay_seconds` is above the 67.1 ms cap.                                                                                                                                                                                                        |
| `frame ... differs from Rigetti-provided definition`     | A `DEFFRAME` of yours changes something other than `INITIAL-FREQUENCY` or `CHANNEL-DELAY`.                                                                                                                                                                     |

Failures elsewhere in the pipeline:

| Message                                                               | Cause                                                                                                                                         |
| :-------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------- |
| `quilc failed to compile the program ...`                             | The gate-model path could not nativize your circuit. The message carries quilc's own reason.                                                  |
| `Number of qubits in the circuit (300) exceeds the device's capacity` | You are submitting Rigetti's full calibration set. See [prepend_default_calibrations](#prepend_default_calibrations).                         |
| Delay silently missing from results                                   | You are on `aws:rigetti:qpu:cepheus-1-108q`, not the direct submission path. Braket has no gate-level delay. Use `rigetti:rigetti:qpu:cepheus-1-108q`. |

## Related links

- [Pricing](https://docs.qbraid.com/v2/home/pricing): Cepheus-1-108Q is billed per minute of execution
- [Device calibrations](https://docs.qbraid.com/v2/sdk/user-guide/providers/calibrations): coupling maps, calibration data, and best-chain search
- [Run on qBraid](https://docs.qbraid.com/v2/sdk/user-guide/providers/getting-started): installation, authentication, runtime options
- [Rigetti (self-managed)](https://docs.qbraid.com/v2/sdk/user-guide/providers/self-managed/rigetti): `RigettiProvider` with your own QCS credentials
- [Rigetti: Quil-T](https://pyquil-docs.rigetti.com/en/stable/quilt.html): the timing/pulse extension to Quil
- [Rigetti: Getting started with Quil-T](https://pyquil-docs.rigetti.com/en/stable/quilt_getting_started.html): why Quil-T programs must be nativized by hand
- [Rigetti: The Quil compiler](https://pyquil-docs.rigetti.com/en/stable/compiler.html): what quilc does, and qubit rewiring
- [Rigetti: The lifecycle of a program](https://docs.rigetti.com/qcs/guides/the-lifecycle-of-a-program): compilation vs translation on QCS
- [Rigetti: TranslationOptions](https://docs.rs/qcs/latest/qcs/qpu/translation/struct.TranslationOptions.html): the full set of translation options
- [quilc](https://github.com/quil-lang/quilc): the open-source Quil compiler
