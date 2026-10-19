> Full piece: [https://docs.iqm.tech/4.7/iqm-client/user_guide_qiskit.html](https://docs.iqm.tech/4.7/iqm-client/user_guide_qiskit.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 9e739648028a605019b02338f98d3509befb031e3938618f8697203eb1e97c5e.

# Qiskit on IQM user guide

This guide illustrates the main features of the Qiskit adapter of IQM Client. You are encouraged to run the demonstrated code snippets and check the output yourself.

Note

IQM provides access to its quantum computers via IQM Resonance – IQM’s quantum cloud service. Please head over [to our website](https://iqm.tech/products/iqm-resonance/) to learn more.

## Installation

Note

If you have previously installed the (now deprecated) `qiskit-iqm` package in your Python environment, you should first uninstall it with `$ uv pip uninstall qiskit-iqm`. In this case, you should also include the `--force-reinstall` option in the `iqm-client` installation command.

The recommended way is to install the optional `qiskit` feature of the `iqm-client` distribution package directly from the Python Package Index (PyPI):

``` bash
$ uv pip install "iqm-client[qiskit]"
```

After installation, the Qiskit adapter can be imported in your Python code as follows:

``` python
from iqm import qiskit_iqm
```

## Authentication

There are two options to authenticate:

1.  Set the `IQM_TOKEN` environment variable to the API token obtained from the IQM Server web dashboard.

2.  Pass the `token` parameter to [`IQMProvider`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMProvider.html#iqm.qiskit_iqm.iqm_provider.IQMProvider "iqm.qiskit_iqm.iqm_provider.IQMProvider"). This will be forwarded to [`IQMClient`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.iqm_client.IQMClient.html#iqm.iqm_client.iqm_client.IQMClient "iqm.iqm_client.iqm_client.IQMClient"). For an example, see [bell_measure.py](https://raw.githubusercontent.com/iqm-finland/sdk/refs/heads/main/iqm_client/src/iqm/qiskit_iqm/examples/bell_measure.py)

## Hello, world!

Here’s a quick and easy way to run a small computation on an IQM quantum computer to check that things are set up correctly.

1.  Login to the web dashboard with your credentials. If you’re using the IQM Resonance cloud service, go to [IQM Resonance](https://resonance.iqm.tech).

2.  Upon your first visit, you can generate your unique, non-recoverable API token directly from the Dashboard page by selecting `Generate token`. It’s important to copy the token immediately from the window, as you won’t be able to do so once the window is closed. If you lose your token, you have the option to regenerate it at any time. However, be aware that regenerating your API token will invalidate any previously generated token.

3.  Store your API token in the environment variable `IQM_TOKEN`.

4.  Download one of the demo notebooks from [IQM Academy](https://www.iqmacademy.com/tutorials/) or the [bell_measure.py example file](https://raw.githubusercontent.com/iqm-finland/sdk/refs/heads/main/iqm_client/src/iqm/qiskit_iqm/examples/bell_measure.py) (Save Page As…)

5.  Install the IQM Qiskit adapter as instructed below.

6.  Run the Jupyter notebook (or run `python bell_measure.py --url https://<IQM Server URL>` if you decided to go for the Python script).

7.  If you’re connecting to a real quantum computer, the output should show almost half of the measurements resulting in ‘00000’ and almost half in ‘11111’ - if this is the case, things are set up correctly!

You can find a video guide on how to set things up [here](https://www.iqmacademy.com/tutorials/resonance/). More ready-to-run examples can also be found at [IQM Academy](https://www.iqmacademy.com/tutorials/).

## Running quantum circuits on an IQM quantum computer

In this section we demonstrate the practicalities of using the Qiskit adapter to execute quantum circuits on an IQM quantum computer.

### Executing a circuit

Let’s consider the following quantum circuit which prepares and measures a GHZ state:

``` python
from qiskit import QuantumCircuit

circuit = QuantumCircuit(3)
circuit.h(0)
circuit.cx(0, 1)
circuit.cx(0, 2)
circuit.measure_all()

print(circuit.draw(output='text'))
```

```
        ┌───┐           ░ ┌─┐
   q_0: ┤ H ├──■────■───░─┤M├──────
        └───┘┌─┴─┐  │   ░ └╥┘┌─┐
   q_1: ─────┤ X ├──┼───░──╫─┤M├───
             └───┘┌─┴─┐ ░  ║ └╥┘┌─┐
   q_2: ──────────┤ X ├─░──╫──╫─┤M├
                  └───┘ ░  ║  ║ └╥┘
meas: 3/═══════════════════╩══╩══╩═
                           0  1  2
```

To run this circuit on an IQM quantum computer you need to initialize an [`IQMProvider`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMProvider.html#iqm.qiskit_iqm.iqm_provider.IQMProvider "iqm.qiskit_iqm.iqm_provider.IQMProvider") instance with the IQM Server URL (and possibly a quantum computer name, if there are several), use it to retrieve an [`IQMBackend`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend "iqm.qiskit_iqm.iqm_provider.IQMBackend") instance representing the quantum computer, and use Qiskit’s [`transpile()`](https://quantum.cloud.ibm.com/docs/api/qiskit/compiler#qiskit.compiler.transpile "(in Qiskit v2.5)") function followed by [`IQMBackend.run`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend.run "iqm.qiskit_iqm.iqm_provider.IQMBackend.run") as usual. `shots` denotes the number of times the quantum circuit(s) are sampled:

``` python
from qiskit import transpile
from iqm.qiskit_iqm import IQMProvider

iqm_server_url = "https://<IQM SERVER>"  # Replace this with the correct URL
quantum_computer = "<NAME>"
token = "<YOUR TOKEN>"
provider = IQMProvider(iqm_server_url, quantum_computer=quantum_computer, token=token)
backend = provider.get_backend()

transpiled_circuit = transpile(circuit, backend=backend)
job = backend.run(transpiled_circuit, shots=1000)
```

Note

As of `qiskit >= 1.0`, Qiskit no longer supports `execute()`. Instead you should first transpile the circuit and then run it, as shown in the code above. See the [Transpilation](#transpilation) section to learn how to transpile circuits in various ways.

Note

If you want to inspect the circuits that are sent to the device, use the `circuit_callback` keyword argument of [`IQMBackend.run`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend.run "iqm.qiskit_iqm.iqm_provider.IQMBackend.run"). See also [Inspecting circuits before submitting them for execution](#inspecting-circuits-before-submitting-them-for-execution) for inspecting the actual run request sent for execution.

Note

As of `iqm-client >= 30.1.0`, structured quality metrics and calibration data are available to `IQMTarget` for improved transpilation. To import the latest valid quality metric data corresponding to the default calibration set into `IQMTarget`, set `use_metrics` to `True` when initializing the class.

You can optionally provide IQMBackend specific options as additional keyword arguments to [`IQMBackend.run`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend.run "iqm.qiskit_iqm.iqm_provider.IQMBackend.run"), documented at [`IQMBackend.create_circuit_job_definition()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend.create_circuit_job_definition "iqm.qiskit_iqm.iqm_provider.IQMBackend.create_circuit_job_definition"). For example, you can enable heralding measurements using `circuit_compilation_options` as follows:

``` python
from iqm.iqm_client import CircuitCompilationOptions, HeraldingMode

job = backend.run(transpiled_circuit, shots=1000, circuit_compilation_options=CircuitCompilationOptions(heralding_mode=HeraldingMode.ZEROS))
```

### Calibration

The calibration data for an IQM quantum computer is stored in a *calibration set*. An [`IQMBackend`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend "iqm.qiskit_iqm.iqm_provider.IQMBackend") instance always corresponds to a specific calibration set, so that its transpilation target uses only those QPU components (qubits and computational resonators) and gates which are available in that calibration set. The server default calibration set will be used by default, but you can also use a different calibration set by specifying the `calibration_set_id` parameter to [`IQMProvider.get_backend()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMProvider.html#iqm.qiskit_iqm.iqm_provider.IQMProvider.get_backend "iqm.qiskit_iqm.iqm_provider.IQMProvider.get_backend") or [`IQMBackend`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend "iqm.qiskit_iqm.iqm_provider.IQMBackend"). If the server default calibration set has changed after you have created the backend, the backend will still use the original default calibration set when submitting circuits for execution. When this happens you will get a warning. You will need to create a new backend if you want to use the new default calibration set instead.

### Inspecting the results

The results of a job that was executed on the IQM quantum computer, represented as a [`Result`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.result.Result "(in Qiskit v2.5)") instance, can be inspected using the usual Qiskit methods:

``` python
result = job.result()
print(result.get_counts())
print(result.get_memory())
```

The result comes with some metadata, such as the contents of the request that produced it. The executed circuit batch (in the native IQM format) can be found in `result.circuits`, and various execution parameters can be found in `result.parameters`:

``` python
print(result.parameters.shots)
print(result.parameters.calibration_set_id)
```

```
1000
1320eae6-f4e2-424d-b299-ef82d556d2c3
```

Another piece of useful metadata are the timestamps of the various steps of processing the job. The timestamps are stored in the list `result.timeline`. The actual job processing has three main steps,

- `compilation` where the circuits are converted to instruction schedules,

- `execution` where the instruction schedules are executed and the measurement results are returned, and

- `post_processing` where the results are converted to the format expected by the client.

The list contains a timestamp for the start and end of each step. For example, the timestamp of starting the circuit compilation is stored with the status `compilation_started`. In the same way the other steps have their own timestamps with statuses consisting of the step name and a `_started` or `_ended` suffix. In addition to processing step timestamps, there are also timestamps for the job itself, `created` for when the job request was accepted by the server and `completed` for when the job processing was finished.

If the processing of the job is terminated before it is complete, for example due to an error, the timestamps of processing steps that were not taken are not present.

For example:

``` python
print(result.timeline)
```

### Backend properties

The [`IQMBackend`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend "iqm.qiskit_iqm.iqm_provider.IQMBackend") instance we created above provides all the standard backend functionality that one expects from a backend in Qiskit. For this example, I am connected to an IQMBackend that features a 5-qubit chip with star-like connectivity:

```
      QB1
       |
QB2 - QB3 - QB4
       |
      QB5
```

Let’s examine its basis gates and the coupling map through the `backend` instance

``` python
print(f'Native operations of the backend: {backend.operation_names}')
print(f'Coupling map of the backend: {backend.coupling_map}')
```

```
Native operations of the backend: ['id', 'r', 'cz', 'measure']
Coupling map of the backend: [[0, 2], [2, 0], [1, 2], [2, 1], [2, 3], [3, 2], [2, 4], [4, 2]]
```

Note that for IQMBackends the identity gate `id` is not actually a gate that is executed on the device and is simply omitted. At IQM we identify qubits by their names, e.g. ‘QB1’, ‘QB2’, etc. as demonstrated above. In Qiskit, qubits are identified by their indices in the quantum register, as you can see from the printed coupling map above. Most of the time you do not need to deal with IQM-style qubit names when using Qiskit, however when you need, the methods [`IQMBackendBase.qubit_name_to_index()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase.qubit_name_to_index "iqm.qiskit_iqm.iqm_backend.IQMBackendBase.qubit_name_to_index") and [`IQMBackendBase.index_to_qubit_name()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_backend.IQMBackendBase.html#iqm.qiskit_iqm.iqm_backend.IQMBackendBase.index_to_qubit_name "iqm.qiskit_iqm.iqm_backend.IQMBackendBase.index_to_qubit_name") can become handy.

### Classically controlled gates

Some IQM quantum computers support classically controlled gates, that is, gates that are executed conditionally depending on the result of a measurement preceding them in the quantum circuit. This support currently has several limitations:

- Only the `x`, `y`, `rx`, `ry` and `r` gates can be classically controlled.

- The gates can only be conditioned on one classical bit, and the only control available is to apply the gate if the bit is 1, and apply an identity gate if the bit is 0.

- The availability of the controlled gates depends on the instrumentation of the quantum computer.

The classical control can be applied on a circuit instruction using [`if_test()`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit#if_test "(in Qiskit v2.5)"):

``` python
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

qr = QuantumRegister(2, 'q')
cr = ClassicalRegister(1, 'c')
circuit = QuantumCircuit(qr, cr)

circuit.h(0)
circuit.measure(0, cr[0])
with circuit.if_test((cr[0], 1)):
    circuit.x(1)  # apply X gate on qubit 1 if cr[0] is 1
circuit.measure_all()

print(circuit.draw(output='text'))
```

```
        ┌───┐┌─┐                           ░ ┌─┐
   q_0: ┤ H ├┤M├───────────────────────────░─┤M├───
        └───┘└╥┘  ┌──────  ┌───┐ ───────┐  ░ └╥┘┌─┐
   q_1: ──────╫───┤ If-0  ─┤ X ├  End-0 ├──░──╫─┤M├
              ║   └──╥───  └───┘ ───────┘  ░  ║ └╥┘
              ║ ┌────╨────┐                   ║  ║
   c: 1/══════╩═╡ c_0=0x1 ╞═══════════════════╬══╬═
              0 └─────────┘                   ║  ║
meas: 2/══════════════════════════════════════╩══╩═
                                              0  1
```

The first measurement operation stores its result in the classical register `c`. If the result is 1, the `X` gate will be applied. If it is zero, an identity gate of corresponding duration is applied instead.

Executing the above circuit should result in the counts being approximately 50/50 split between the ‘00 0’ and ‘11 1’ bins of the histogram (even though the state itself is never entangled).

Note

`if_test` blocks cannot be nested.

### Resetting qubits

The [`qiskit.circuit.Reset`](https://quantum.cloud.ibm.com/docs/api/qiskit/circuit#qiskit.circuit.Reset "(in Qiskit v2.5)") operation can be used to reset qubits to the \\\|0\rangle\\ state. It is currently implemented as a (projective) measurement followed by a classically controlled X gate conditioned on the result, and is only available if the quantum computer supports classically controlled gates.

``` python
from qiskit import QuantumCircuit

circuit = QuantumCircuit(1, 1)
circuit.h(0)
circuit.reset(0)
circuit.measure(0, 0)

print(circuit.draw(output='text'))
```

```
     ┌───┐     ┌─┐
  q: ┤ H ├─|0>─┤M├
     └───┘     └╥┘
c: 1/═══════════╩═
                0
```

In the above example, the Hadamard gate prepares a uniform superposition of the \\\|0\rangle\\ and \\\|1\rangle\\ states, and the reset then collapses it back into the \\\|0\rangle\\ state. Executing the circuit should result in (mostly) zeros being measured.

### Inspecting circuits before submitting them for execution

It is possible to inspect the final circuits that would be submitted for execution before actually submitting them, which can be useful for debugging purposes. This can be done using [`IQMBackend.create_circuit_job_definition()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend.create_circuit_job_definition "iqm.qiskit_iqm.iqm_provider.IQMBackend.create_circuit_job_definition"), which returns a `RunRequest` containing the circuits and other data. The method accepts the same parameters as [`IQMBackend.run`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend.run "iqm.qiskit_iqm.iqm_provider.IQMBackend.run").

``` python
# inspect the run_request without submitting it for execution
circuit_job = backend.create_circuit_job_definition(transpiled_circuit, shots=10)
print(circuit_job)

# the following two calls submit exactly the same run request for execution on the server
backend.run(transpiled_circuit, shots=10)
backend.client.submit_circuit_job(circuit_job)
```

It is also possible to print a run request when it is actually submitted by setting the environment variable `IQM_CLIENT_DEBUG=1`.

## Transpilation

In this section we study how the circuit gets transpiled in more detail.

### Basic transpilation

You can use the default Qiskit transpiler on IQM quantum computers with both the Crystal and the Star architectures. Starting from the [GHZ circuit](#ghz-circuit) we created above:

``` python
from qiskit.compiler import transpile

transpiled_circuit = transpile(circuit, backend=backend, layout_method='sabre', optimization_level=3)
print(transpiled_circuit.draw(output='text', idle_wires=False))
```

```
global phase: 3π/2
          ┌─────────────┐                  ┌─────────────┐ ░       ┌─┐
q_2 -> 5  ┤ R(π/2,3π/2) ├──────────■───────┤ R(π/2,5π/2) ├─░───────┤M├
          ├─────────────┤          │       └─────────────┘ ░ ┌─┐   └╥┘
q_0 -> 10 ┤ R(π/2,3π/2) ├─■────────■───────────────────────░─┤M├────╫─
          ├─────────────┤ │ ┌─────────────┐                ░ └╥┘┌─┐ ║
q_1 -> 15 ┤ R(π/2,3π/2) ├─■─┤ R(π/2,5π/2) ├────────────────░──╫─┤M├─╫─
          └─────────────┘   └─────────────┘                ░  ║ └╥┘ ║
  meas: 3/════════════════════════════════════════════════════╩══╩══╩═
                                                            0  1  2
```

Under the hood the Qiskit transpiler uses the [`IQMDefaultSchedulingPlugin`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.transpiler_plugins.IQMDefaultSchedulingPlugin.html#iqm.qiskit_iqm.transpiler_plugins.IQMDefaultSchedulingPlugin "iqm.qiskit_iqm.transpiler_plugins.IQMDefaultSchedulingPlugin") plugin that automatically adapts the transpiled circuit to the IQMBackend. In particular,

- if `optimization_level > 0`, the plugin will use the [`IQMOptimizeSingleQubitGates`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_transpilation.IQMOptimizeSingleQubitGates.html#iqm.qiskit_iqm.iqm_transpilation.IQMOptimizeSingleQubitGates "iqm.qiskit_iqm.iqm_transpilation.IQMOptimizeSingleQubitGates") pass to optimize single-qubit gates, and

- for devices that have the IQM Star architecture, the plugin will use the [`IQMNaiveResonatorMoving`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_naive_move_pass.IQMNaiveResonatorMoving.html#iqm.qiskit_iqm.iqm_naive_move_pass.IQMNaiveResonatorMoving "iqm.qiskit_iqm.iqm_naive_move_pass.IQMNaiveResonatorMoving") pass to automatically insert [`MoveGate`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.move_gate.MoveGate.html#iqm.qiskit_iqm.move_gate.MoveGate "iqm.qiskit_iqm.move_gate.MoveGate") instructions as needed.

Alternatively, you can use the `transpile_to_IQM()` function for more precise control over the transpilation process as documented below.

It is also possible to use one of our other pre-defined transpiler plugins as an argument to [`transpile()`](https://quantum.cloud.ibm.com/docs/api/qiskit/compiler#qiskit.compiler.transpile "(in Qiskit v2.5)"), for example `transpile(circuit, backend=backend, scheduling_method="only_move_routing_keep")`. Additionally, you can use any of our transpiler passes to define your own [`qiskit.transpiler.PassManager`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.transpiler.PassManager "(in Qiskit v2.5)") if you want to assemble custom transpilation procedures manually.

### Computational resonators

The IQM Star architecture includes computational resonators as additional QPU components, and uses qubit-resonator gates instead of two-qubit gates. These include [`MoveGate`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.move_gate.MoveGate.html#iqm.qiskit_iqm.move_gate.MoveGate "iqm.qiskit_iqm.move_gate.MoveGate") which moves qubit states to and from the resonators.

The standard Qiskit transpiler does not know how to compile qubit-resonator gates. This is why IQMBackend provides the Qiskit transpiler a *simplified* transpilation target in which the resonators and MOVE gates have been abstracted away, and replaced with fictional two-qubit gates that directly connect qubits that can be made to interact via a resonator. It then uses [`IQMDefaultSchedulingPlugin`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.transpiler_plugins.IQMDefaultSchedulingPlugin.html#iqm.qiskit_iqm.transpiler_plugins.IQMDefaultSchedulingPlugin "iqm.qiskit_iqm.transpiler_plugins.IQMDefaultSchedulingPlugin") to re-introduce resonators and add [`MOVE gates`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.move_gate.MoveGate.html#iqm.qiskit_iqm.move_gate.MoveGate "iqm.qiskit_iqm.move_gate.MoveGate") between qubits and resonators as necessary at the scheduling stage.

IQMDefaultSchedulingPlugin is executed automatically when you use the Qiskit transpiler. Starting from the [GHZ circuit](#ghz-circuit) we created above:

``` python
from qiskit.compiler import transpile
from iqm.qiskit_iqm import IQMProvider

resonator_backend = IQMProvider("https://resonance.iqm.tech", quantum_computer="sirius").get_backend()
transpiled_circuit = transpile(circuit, resonator_backend)

print(transpiled_circuit.draw(output='text', idle_wires=False))
```

```
           ┌─────────────┐┌───────┐                  ┌───────┐                ░ ┌─┐
  q_0 -> 0 ┤ R(π/2,3π/2) ├┤0      ├──────────────────┤0      ├────────────────░─┤M├──────
           ├─────────────┤│       │   ┌─────────────┐│       │                ░ └╥┘┌─┐
  q_1 -> 1 ┤ R(π/2,3π/2) ├┤       ├─■─┤ R(π/2,5π/2) ├┤       ├────────────────░──╫─┤M├───
           ├─────────────┤│  Move │ │ └─────────────┘│  Move │┌─────────────┐ ░  ║ └╥┘┌─┐
  q_2 -> 2 ┤ R(π/2,3π/2) ├┤       ├─┼────────■───────┤       ├┤ R(π/2,5π/2) ├─░──╫──╫─┤M├
           └─────────────┘│       │ │        │       │       │└─────────────┘ ░  ║  ║ └╥┘
resonators ───────────────┤1      ├─■────────■───────┤1      ├───────────────────╫──╫──╫─
                          └───────┘                  └───────┘                   ║  ║  ║
   meas: 3/══════════════════════════════════════════════════════════════════════╩══╩══╩═
                                                                             0  1  2
```

### Custom transpilation

As an alternative to the native Qiskit transpiler integration, you can use the [`transpile_to_IQM()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_naive_move_pass.transpile_to_IQM.html#iqm.qiskit_iqm.iqm_naive_move_pass.transpile_to_IQM "iqm.qiskit_iqm.iqm_naive_move_pass.transpile_to_IQM") function. It is meant for users who want at least one of the following:

- more fine grained control over the transpilation process without having to figure out which IQM transpiler plugin to use,

- transpile Star architecture circuits that already contain qubit-resonator gates, or

- force the transpiler to use a strict subset of qubits on the device.

For example, if you want to transpile the circuit with `optimization_level=0` but also apply the single qubit gate optimization pass, you can do one of the following, equivalent things:

``` python
from iqm.qiskit_iqm import transpile_to_IQM

transpile_to_IQM(circuit, backend=backend, optimization_level=0, perform_move_routing=False, optimize_single_qubits=True)
```

``` python
transpile(circuit, backend=backend, optimization_level=0, scheduling_method='only_rz_optimization')
```

Similarly, if you want to transpile a native Star architecture circuit that already contains [`MoveGate`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.move_gate.MoveGate.html#iqm.qiskit_iqm.move_gate.MoveGate "iqm.qiskit_iqm.move_gate.MoveGate") instances (that act on a qubit and a computational resonator), you can do the following:

``` python
from iqm.iqm_client.transpile import ExistingMoveHandlingOptions
from iqm.qiskit_iqm import IQMCircuit, transpile_to_IQM

move_circuit = IQMCircuit(3)
move_circuit.h(0)
move_circuit.move(0, 1)
move_circuit.h(2)
move_circuit.cz(2, 1)
move_circuit.h(2)
move_circuit.move(0, 1)

# Using transpile() does not work here, as the circuit already contains a MoveGate
transpiled_circuit = transpile_to_IQM(move_circuit, backend=resonator_backend, existing_moves_handling=ExistingMoveHandlingOptions.KEEP)
print(transpiled_circuit.draw(output='text', idle_wires=False))
```

```
         ┌─────────────┐┌───────┐   ┌───────┐
q_0 -> 0 ┤ R(π/2,3π/2) ├┤0      ├───┤0      ├───────────────
         ├─────────────┤│       │   │       │┌─────────────┐
q_2 -> 1 ┤ R(π/2,3π/2) ├┤  Move ├─■─┤  Move ├┤ R(π/2,5π/2) ├
         └─────────────┘│       │ │ │       │└─────────────┘
q_1 -> 6 ───────────────┤1      ├─■─┤1      ├───────────────
                        └───────┘   └───────┘
```

And if you want force the compiler to use a strict subset of qubits on the device, you can do the following:

``` python
qubits = [4, 3, 8]
qubit_index_to_name = {i: backend.index_to_qubit_name(q) for i, q in enumerate(qubits)}
# or
# qubits = ['QB5', 'QB4', 'QB9']
# qubit_index_to_name = dict(enumerate(qubits))

transpiled_circuit = transpile_to_IQM(circuit, backend=backend, restrict_to_qubits=qubits)
print(transpiled_circuit.draw(output='text', idle_wires=False))
```

```
global phase: 3π/2
         ┌─────────────┐   ┌─────────────┐                ░    ┌─┐
q_1 -> 0 ┤ R(π/2,3π/2) ├─■─┤ R(π/2,5π/2) ├────────────────░────┤M├───
         ├─────────────┤ │ └─────────────┘                ░ ┌─┐└╥┘
q_0 -> 1 ┤ R(π/2,3π/2) ├─■────────■───────────────────────░─┤M├─╫────
         ├─────────────┤          │       ┌─────────────┐ ░ └╥┘ ║ ┌─┐
q_2 -> 2 ┤ R(π/2,3π/2) ├──────────■───────┤ R(π/2,5π/2) ├─░──╫──╫─┤M├
         └─────────────┘                  └─────────────┘ ░  ║  ║ └╥┘
 meas: 3/════════════════════════════════════════════════════╩══╩══╩═
                                                             0  1  2
```

Then, provide the [`IQMBackend.run`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend.run "iqm.qiskit_iqm.iqm_provider.IQMBackend.run") method a mapping from the qubit indices used in the transpiled circuit to the qubits on the device, like this:

``` python
job = backend.run(transpiled_circuit, qubit_index_to_name=qubit_index_to_name)
```

### Using custom IQM transpiler plugins

For the native integration of the custom IQM transpiler passes with the Qiskit transpiler, we have implemented several scheduling plugins for the Qiskit transpiler. These plugins can be used as the `scheduling_method` string argument for [`transpile()`](https://quantum.cloud.ibm.com/docs/api/qiskit/compiler#qiskit.compiler.transpile "(in Qiskit v2.5)"). The mapping between these strings and the classes that implement the plugins is defined in the `pyproject.toml` file of this package. The documentation of these plugins in found in the respective plugin classes.

If you are unsure which plugin to use, you can use [`transpile_to_IQM()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_naive_move_pass.transpile_to_IQM.html#iqm.qiskit_iqm.iqm_naive_move_pass.transpile_to_IQM "iqm.qiskit_iqm.iqm_naive_move_pass.transpile_to_IQM") with the appropriate arguments. This function determines which plugin to use based on the backend and the provided arguments. Note that the Qiskit transpiler automatically uses the [`IQMDefaultSchedulingPlugin`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.transpiler_plugins.IQMDefaultSchedulingPlugin.html#iqm.qiskit_iqm.transpiler_plugins.IQMDefaultSchedulingPlugin "iqm.qiskit_iqm.transpiler_plugins.IQMDefaultSchedulingPlugin") when the backend is an IQMBackend.

## Batch execution of circuits

It is possible to submit multiple circuits to be executed, as a batch. In many cases this is more time efficient than running the circuits one by one. Batch execution has some restrictions: all the circuits must be executed for the same number of shots. For starters, let’s construct two circuits preparing and measuring different Bell states:

``` python
qc_1 = QuantumCircuit(2)
qc_1.h(0)
qc_1.cx(0, 1)
qc_1.measure_all()

qc_2 = QuantumCircuit(2)
qc_2.h(0)
qc_2.x(1)
qc_2.cx(0, 1)
qc_2.measure_all()
```

Now, we can run them together in a batch:

``` python
transpiled_qcs = transpile([qc_1, qc_2], backend=backend, initial_layout=[0, 2])
job = backend.run(transpiled_qcs, shots=1000)
print(job.result().get_counts())
```

The batch execution functionality can be used to run a parameterized circuit for various concrete values of parameters:

``` python
import numpy as np
from qiskit.circuit import Parameter

circuit = QuantumCircuit(2)
theta = Parameter('theta')
theta_range = np.linspace(0, np.pi / 2, 3)

circuit.h(0)
circuit.cx(0, 1)
circuit.rz(theta, [0, 1])
circuit.cx(0, 1)
circuit.h(0)
circuit.measure_all()


transpiled_circuit = transpile(circuit, backend=backend, layout_method='sabre', optimization_level=3)
circuits = [transpiled_circuit.assign_parameters({theta: n}) for n in theta_range]
job = backend.run(circuits, shots=1000)
print(job.result().get_counts())
```

Note that it is important to transpile the parameterized circuit before binding the values to ensure a consistent qubit measurements across circuits in the batch.

## Multiplexed measurements

When multiple measurement instructions are present in a circuit, the measurements may be multiplexed, meaning the measurement pulses would be simultaneously executed on the quantum hardware, if possible. Multiplexing requires the measurement instructions to form a convex subgraph, i.e. not have other instructions between them acting on the same qubits.

You don’t have to do anything special to enable multiplexing, it is automatically attempted by the circuit-to-pulse compiler on the server side. However, you can ensure multiplexing (whenever possible on the hardware level) by putting a `barrier` instruction before and after a group of measurements. This prevents the transpiler from inserting any other instructions between the measurements. There is no concept of multiplexed or simultaneous measurements in Qiskit, so the circuit diagram will not indicate any multiplexing:

```
         ░ ┌─┐       ░
   q_0: ─░─┤M├───────░─
         ░ └╥┘┌─┐    ░
   q_1: ─░──╫─┤M├────░─
         ░  ║ └╥┘┌─┐ ░
   q_2: ─░──╫──╫─┤M├─░─
         ░  ║  ║ └╥┘ ░
meas: 3/════╩══╩══╩═══
            0  1  2
```

## Simulation

In this section we show how to simulate the execution of quantum circuits on IQM quantum computers.

Note

Since the simulation happens locally, you do not need access to an actual quantum computer.

### Noisy simulation of quantum circuit execution

The execution of circuits can be simulated locally, with a noise model to mimic the real hardware as much as possible. To this end, the Qiskit adapter provides the class [`IQMFakeBackend`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMFakeBackend.html#iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMFakeBackend "iqm.qiskit_iqm.fake_backends.iqm_fake_backend.IQMFakeBackend") that can be instantiated with properties of a certain QPU, e.g. using functions such as [`IQMFakeAdonis()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.fake_backends.fake_adonis.IQMFakeAdonis.html#iqm.qiskit_iqm.fake_backends.fake_adonis.IQMFakeAdonis "iqm.qiskit_iqm.fake_backends.fake_adonis.IQMFakeAdonis"), [`IQMFakeApollo()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.fake_backends.fake_apollo.IQMFakeApollo.html#iqm.qiskit_iqm.fake_backends.fake_apollo.IQMFakeApollo "iqm.qiskit_iqm.fake_backends.fake_apollo.IQMFakeApollo") and [`IQMFakeAphrodite()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.fake_backends.fake_aphrodite.IQMFakeAphrodite.html#iqm.qiskit_iqm.fake_backends.fake_aphrodite.IQMFakeAphrodite "iqm.qiskit_iqm.fake_backends.fake_aphrodite.IQMFakeAphrodite") that represent specific IQM quantum architectures with pre-defined, representative noise models.

``` python
from iqm.qiskit_iqm import IQMFakeAdonis

circuit = QuantumCircuit(2)
circuit.h(0)
circuit.cx(0, 1)
circuit.measure_all()

backend = IQMFakeAdonis()
transpiled_circuit = transpile(circuit, backend=backend)
job = backend.run(transpiled_circuit, shots=1000)
print(job.result().get_counts())
```

Above, we use an [`IQMFakeAdonis()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.fake_backends.fake_adonis.IQMFakeAdonis.html#iqm.qiskit_iqm.fake_backends.fake_adonis.IQMFakeAdonis "iqm.qiskit_iqm.fake_backends.fake_adonis.IQMFakeAdonis") instance to run a noisy simulation of `circuit` on a simulated 5-qubit Adonis chip. The noise model includes relaxation (\\T_1\\) and dephasing (\\T_2\\), gate infidelities and readout errors. If you want to customize the noise model instead of using the default one provided by [`IQMFakeAdonis()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.fake_backends.fake_adonis.IQMFakeAdonis.html#iqm.qiskit_iqm.fake_backends.fake_adonis.IQMFakeAdonis "iqm.qiskit_iqm.fake_backends.fake_adonis.IQMFakeAdonis"), you can create a copy of the IQMFakeBackend instance with an updated error profile:

``` python
error_profile = backend.error_profile
error_profile.t1s['QB2'] = 30000.0  # Change T1 time of QB2 as example
custom_fake_backend = backend.copy_with_error_profile(error_profile)
```

### Running a quantum circuit on a facade backend

Circuits can be executed against a *mock environment*: an IQM Server that has no real quantum computer hardware. Results from such executions are just random bits. This may be useful when developing and testing software integrations.

Note

IQM Resonance typically provides a mock environment for each real quantum computer it has. For example, the name `"garnet"` refers to a real quantum computer named Garnet, whereas `"garnet:mock"` refers to the corresponding mock environment.

On-premises users should ask their admin whether a mock environment is available, and which IQM Server URL to use.

The Qiskit adapter contains [`IQMFacadeBackend`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend.html#iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend "iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend"), which allows to combine a mock remote execution with a local noisy quantum circuit simulation. This way you can both validate your integration as well as get an idea of the expected circuit execution results.

To run a circuit this way, use `IQMProvider.get_backend()` with one of the backend names `facade_adonis, facade_apollo, facade_aphrodite, facade_deneb` or `facade_garnet` to obtain a facade backend. `facade_adonis, facade_apollo, facade_aphrodite` represent typical Crystal 5, Crystal 20 and Crystal 54 architecture QPUs, whereas `facade_deneb` and `facade_garnet` represent the corresponding IQM Resonance quantum computers more specifically. The provider must be initialized with the URL of a quantum computer with the corresponding static quantum architecture (i.e. names of qubits, their connectivity, and the native gateset should match the desired architecture).

Important

When using a facade backend, the IQM Server URL of `IQMProvider` should always point to a mock environment rather than a real quantum computer, as the execution results from the server will be discarded and replaced by a locally simulated result generated by Qiskit Aer. If you use a real quantum computer with a facade backend, you will just waste your credits and/or computation time.

``` python
from qiskit import transpile, QuantumCircuit
from iqm.qiskit_iqm import IQMProvider

circuit = QuantumCircuit(2)
circuit.h(0)
circuit.cx(0, 1)
circuit.measure_all()

iqm_server_url = "https://resonance.iqm.tech"
quantum_computer = "garnet:mock"  # Replace this with the correct mock env name
provider = IQMProvider(iqm_server_url, quantum_computer=quantum_computer)
backend = provider.get_backend('facade_garnet')
transpiled_circuit = transpile(circuit, backend=backend)
job = backend.run(transpiled_circuit, shots=1000)
print(job.result().get_counts())
```

Note

When a classical register is added to the circuit, Qiskit fills it with classical bits of value 0 by default. If the register is not used later, and the circuit is submitted to the IQM Server, the results will not contain those 0-filled bits. To make sure the facade backend returns results in the same format as a real IQM Server, [`IQMFacadeBackend.run()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend.html#iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend.run "iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend.run") checks for the presence of unused classical registers, and fails with an error if there are any.
