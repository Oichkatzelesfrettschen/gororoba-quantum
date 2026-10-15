> Full piece: [https://quantum.cloud.ibm.com/docs/en/guides/qpu-information](https://quantum.cloud.ibm.com/docs/en/guides/qpu-information)

# View backend details

### Package versions

The code on this page was developed using the following requirements.
We recommend using these versions or newer.

```
qiskit-ibm-runtime~=0.47.0
```

This page explains how to find information about your available backends.

## List or filter backends

### List backends available to you

You can use either Qiskit or IBM Quantum Platform to view a list of backends available to you, or to search for a particular backend.

> **QPU names**
>
> QPUs hosted on IBM Cloud(R) have names that begin with `ibm_*`. All QPUs are given a city name - for example, `ibm_kingston`. This name does not indicate where the actual QPU is hosted.

### View backends with Qiskit

Use the [`QiskitRuntimeService.backends()`](https://quantum.cloud.ibm.com/docs/api/qiskit-ibm-runtime/qiskit-runtime-service#backends) method, as shown in the next code block. This method returns a list of [`IBMBackend`](https://quantum.cloud.ibm.com/docs/api/qiskit-ibm-runtime/ibm-backend) instances.

To run the following code, be sure you have already authenticated to the service. See [Set up your IBM Cloud account](https://quantum.cloud.ibm.com/docs/guides/cloud-setup) for more details.

```python
# Initialize your account
from qiskit_ibm_runtime import QiskitRuntimeService

service = QiskitRuntimeService()

service.backends()
```

Output:

```
[<IBMBackend('ibm_pittsburgh')>,
 <IBMBackend('ibm_boston')>,
 <IBMBackend('ibm_fez')>,
 <IBMBackend('ibm_miami')>,
 <IBMBackend('ibm_marrakesh')>,
 <IBMBackend('ibm_kingston')>]
```

To search for a specific backend, use the [`QiskitRuntimeService.backend()`](https://quantum.cloud.ibm.com/docs/api/qiskit-ibm-runtime/qiskit-runtime-service#backend) method (note that this is singular: *backend*), which takes the name of the backend as the input parameter and returns an [`IBMBackend`](https://quantum.cloud.ibm.com/docs/api/qiskit-ibm-runtime/ibm-backend) instance representing that particular backend:

```python
service.backend("ibm_fez")
```

Output:

```
<IBMBackend('ibm_fez')>
```

### View backends on IBM Quantum Platform

To view the backends you have access to, navigate to the list of backends on the [Compute resources page](https://quantum.cloud.ibm.com/computers) (note that your selected region might impact the QPUs listed). Click the filter icon and choose either "All my instances" or a specific instance name to see the available QPUs.

> **Note**
>
> If you are logged in to a specific instance or region, or if you initialized the service with a specific instance or region by using `QiskitRuntimeService()`, only the backends available to you on that instance or region are returned.

### Filter backends

### Filter by properties with Qiskit

You can filter the available backends by their [configuration](https://quantum.cloud.ibm.com/docs/api/qiskit-ibm-runtime/models-backend-configuration) or [status](https://quantum.cloud.ibm.com/docs/api/qiskit-ibm-runtime/models-backend-status). For more general filters, set the `filters` argument to a function that accepts a backend object and returns `True` if it meets your criteria. Refer to the [API documentation](https://quantum.cloud.ibm.com/docs/api/qiskit-ibm-runtime/qiskit-runtime-service#backends) for more details.

The following code returns only backends that fit these criteria and are available to you *on your currently selected instance*:

- Are real quantum devices (`simulator=False`)
- Are currently operational (`operational=True`)
- Have at least a hundred qubits (`min_num_qubits=100`)

```python
# Optionally pass in an instance, region, or both, to
# further filter the backends.
service = QiskitRuntimeService()

service.backends(simulator=False, operational=True, min_num_qubits=100)
```

Output:

```
[<IBMBackend('ibm_pittsburgh')>,
 <IBMBackend('ibm_boston')>,
 <IBMBackend('ibm_fez')>,
 <IBMBackend('ibm_miami')>,
 <IBMBackend('ibm_marrakesh')>,
 <IBMBackend('ibm_kingston')>]
```

A similar method is [`QiskitRuntimeService.least_busy()`](https://quantum.cloud.ibm.com/docs/api/qiskit-ibm-runtime/qiskit-runtime-service#least_busy), which takes the same filters as `backends()` but returns the backend that matches the filters and has the least number of jobs pending in the queue:

```python
service.least_busy(operational=True, min_num_qubits=100)
```

Output:

```
<IBMBackend('ibm_fez')>
```

### Filter by properties on IBM Quantum Platform

To view the backends you have access to, view the table on the [Compute resources page](https://quantum.cloud.ibm.com/computers). Click the filter icon to see filter options. You can filter by processor type and status. Note also that you can sort the table by any column by hovering over a column title, and then clicking the arrows that appear.

## Static backend information

Some information about a backend does not change regularly, such as its name, [version](#qpu-versioning), the number of qubits it has, its processor type (the bird family name, which indicates the [topology](#coupling-map) and approximate qubit count), and the types of features it supports. This information is available as attributes of the `backend` object. For a full list of attributes, see the [`IBMBackend` API documentation](https://quantum.cloud.ibm.com/docs/api/qiskit-ibm-runtime/ibm-backend).  Find more information on versioning in the [QPU versioning](#qpu-versioning) section below.

A backend's region (the location of the data center where your data and experiments will be hosted and processed) is listed in its detailed information card on the [Compute resources](https://quantum.cloud.ibm.com/computers) page on IBM Quantum Platform.

### View backend information with Qiskit

```python
backend = service.least_busy(operational=True, simulator=False)

print(
    f"Name: {backend.name}\n"
    f"Version: {backend.backend_version}\n"
    f"No. of programmable qubits: {backend.num_qubits}\n"
    f"Processor type: {backend.processor_type}\n"
)
```

Output:

```
Name: ibm_fez
Version: 1.3.37
No. of programmable qubits: 156
Processor type: {'family': 'Heron', 'revision': '2'}

```

### View backend information on IBM Quantum Platform

Navigate to the [Compute resources](https://quantum.cloud.ibm.com/computers) page to view a table of all QPUs, then click the name of any QPU to open its detailed information card. Find backend information under the Details section of the card.

### QPU versioning

Each QPU has a version number in the form X.Y.Z (major.minor.revision). A circuit compiled for a given version number is guaranteed to run on that QPU. If the revision number changes, the circuit will continue to run. If the major or minor number changes, the circuit is not guaranteed to run, although it may do so.

The revision version number will increment for fixes that do not break the existing compiled circuit.

The code example earlier in [this section](#static-backend-information) demonstrates how to find a backend's version. On IBM Quantum Platform, you can view the version on a QPU's detailed information card (click the QPU's name on the [Compute resources](https://quantum.cloud.ibm.com/computers) table to open the card).

The conditions under which a version or revision number can change are listed in the following table.

| Major version                                                            | Minor version                                                                                                           | Revision version                                      |
| ------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| Sample changes                                                           | Warmup / cool-down cycles                                                                                               | QPU software updates                                  |
| Major changes to the control electronics                                 | Swapping out some electronics, if the replacement appreciably affects operation                                         | Manual calibrations to improve fidelities             |
| Moving the QPU to a new location, if significant behavior changes result | Dropping a gate for some duration of time due to calibration issues, and corrections cannot readily be done in software | Small electronics changes that don't affect operation |
|                                                                          | Changing the direction of a CNOT gate                                                                                   |                                                       |

### Supported instructions

Each [processor family](https://quantum.cloud.ibm.com/docs/guides/processor-types) natively supports a limited set of instructions. This set includes single- and two-qubit gates, as well as non-unitary operations such as measure and reset. Every gate in the circuit must be translated (by the transpiler) to the elements of a QPU's supported instruction set before it can run on the QPU.

You can view the supported instruction sets for a QPU with Qiskit. The IBM Quantum Platform Compute resources page lists only the supported unitary gates (basis gates) for a QPU.

### Find supported instructions with Qiskit

```python
from qiskit_ibm_runtime import QiskitRuntimeService

service = QiskitRuntimeService()
backend = service.least_busy(operational=True, simulator=False)

print(f"Backend: {backend.name}")
print(f"    Processor type: {backend.processor_type}")
print(f"    Supported instructions: {backend.supported_instructions}")
```

Output:

```
Backend: ibm_kingston
```

```
    Processor type: {'family': 'Heron', 'revision': '2'}
    Supported instructions: ['cz', 'id', 'delay', 'measure', 'measure_2', 'reset', 'rz', 'sx', 'x', 'if_else', 'store']
```

### Find basis gates on IBM Quantum Platform

Navigate to the [Compute resources](https://quantum.cloud.ibm.com/computers) page to view a table of all QPUs, then click the name of any QPU to open its detailed information card. The basis gates for that QPU are listed in the Details section.

### Table of supported instructions

| Operation category       | Name                                                                                                                                                                                                                                                                                  |
| :----------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Single-qubit gates       | [`RZ`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.library.RZGate), [`SX`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.library.SXGate), [`X`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.library.XGate), [`ID`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.library.IGate), [`delay`](https://quantum.cloud.ibm.com/docs/api/qiskit/circuit#qiskit.circuit.Delay) |
| Two-qubit gates          | [`CZ`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.library.CZGate), [`ECR`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.library.ECRGate)                                                                                                                                                                      |
| Fractional gates         | [`RX`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.library.RXGate) (single-qubit), [`RZZ`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.library.RZZGate) (two-qubit)                                                                                                                                           |
| Non-unitary instructions | [`measure`](https://quantum.cloud.ibm.com/docs/api/qiskit/circuit#qiskit.circuit.Measure), [`reset`](https://quantum.cloud.ibm.com/docs/api/qiskit/circuit#qiskit.circuit.Reset), [`measure_*`](https://quantum.cloud.ibm.com/docs/guides/execute-dynamic-circuits#midcircuit), [`delay`](https://quantum.cloud.ibm.com/docs/api/qiskit/circuit#delay)                                                    |
| Control flow             | [`if_else`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.IfElseOp) (classical feedforward)                                                                                                                                                                                                         |

## Dynamic backend information

Backends also have properties that change whenever the backend is calibrated, such as qubit lifetime and operation error rates. Backend properties update after the calibration sequence completes. These properties can be used when optimizing quantum circuits or to construct noise models for a classical simulator. See the [Calibration jobs](https://quantum.cloud.ibm.com/docs/guides/calibration-jobs) guide for more information.

On IBM Quantum Platform, you can download calibration data as a CSV file. Click a QPU on the [Compute resources](https://quantum.cloud.ibm.com/computers) page to view its detailed information card, then click the download icon in the upper right corner of the Calibration data section.

> **Retrieve historical data**
>
> You can retrieve historical backend properties data in Qiskit with the following code:
>
> ```python
> backend.properties(datetime=<datetime>)
> ```

### Qubit properties

[Jump to the list of qubit properties](#view-qubit-properties)

`backend.properties().qubit_property()` returns information about the qubits' physical attributes. It contains a dictionary of various properties of the qubit, each paired with its value and the timestamp of the last calibration.

The following code examples demonstrate how to list all properties, or retrieve specific properties, of a particular qubit.

```python
# fundamental physical properties of qubit 1

backend = service.least_busy(operational=True, simulator=False)

backend.qubit_properties(1)
```

Output:

```
QubitProperties(t1=0.00022010760855770256, t2=0.0002363339150114578, frequency=None)
```

```python
# Retrieve qubit properties
qubit_index = backend.num_qubits - 1  # Replace with your qubit index
qubit_props = backend.properties().qubit_property(qubit_index)

# Access specific properties
t1 = qubit_props.get("T1", (None,))[0]
t2 = qubit_props.get("T2", (None,))[0]
readout_error = qubit_props.get("readout_error", (None,))[0]
prob_meas0_prep1 = qubit_props.get("prob_meas0_prep1", (None,))[0]
prob_meas1_prep0 = qubit_props.get("prob_meas1_prep0", (None,))[0]
readout_length = qubit_props.get("readout_length", (None,))[0]

print(f"Qubit {qubit_index} Properties:")
print(f"  T1: {t1} seconds")
print(f"  T2: {t2} seconds")
print(f"  Readout Error: {readout_error}")
print(f"  P(0 | 1): {prob_meas0_prep1}")
print(f"  P(1 | 0): {prob_meas1_prep0}")
print(f"  Readout Length: {readout_length} seconds")
```

#### View qubit properties

### \`T1\` (Relaxation time)

The $T_1$ time represents the average duration a qubit remains in its excited state $|1\rangle$ before decaying to its ground state $|0\rangle$ due to energy relaxation. This parameter is used to characterize the qubit's energy relaxation behavior, and is expressed in units of seconds (s).

View with Qiskit
`backend.properties().t1(<qubit>)`

View on IBM Quantum Platform
Calibration data section: Qubit dropdown menu; find the *$T_1$ median* value in the Details section

### \`T2\` (Dephasing time)

The $T_2$ time denotes the timescale over which a qubit maintains phase coherence of a superposition between the $|0\rangle$ and $|1\rangle$ states. It accounts for both energy relaxation and pure dephasing processes, providing insight into the qubit's coherence properties. $T_2$ is reported from a Hahn echo sequence.

View with Qiskit
`backend.properties().t2(<qubit>)`

View on IBM Quantum Platform
Calibration data section: Qubit dropdown menu; find the *$T_2$ median* value in the Details section

### Instruction properties

[Jump to the list of instruction properties](#view-instruction-properties)

The `backend.target` attribute is a [`qiskit.transpiler.Target`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.transpiler.Target) object: an object that contains all the information needed to transpile a circuit for that backend. This includes instruction errors and durations. For example, the following cell gets the properties for a [`cz` gate](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.library.CZGate) acting between a connected pair of qubits.

```python
# Get the cz gate properties for a connected pair of qubits
# (the first edge in this backend's coupling map)
edge = next(iter(backend.target["cz"]))
backend.target["cz"][edge]
```

The following cell shows the properties for a measurement operation (including the readout error) on qubit 0.

```python
backend.target["measure"][(0,)]
```

Output:

```
InstructionProperties(duration=1.66e-06, error=0.0126953125)
```

#### View instruction properties

### prob-meas0-prep1

This parameter indicates the probability of measuring a qubit in the $|0\rangle$ state when it was intended to be prepared in the $|1\rangle$ state, denoted as $P(0 | 1)$. It reflects errors in state preparation and measurement (SPAM), particularly measurement errors in superconducting qubits.

View with Qiskit
`backend.properties().qubit_property(<qubit>, 'prob_meas0_prep1')`

View on IBM Quantum Platform
Calibration data section: Qubit dropdown menu

### prob-meas1-prep0

Similarly, this parameter represents the probability of measuring a qubit in the $|1\rangle$ state when it was intended to be prepared in the $|0\rangle$ state, denoted as $P(1 | 0)$. Like `prob_meas0_prep1`, it reflects SPAM errors, with measurement errors being the predominant contributor in superconducting qubits.

View with Qiskit
`backend.properties().qubit_property(<qubit>, 'prob_meas0_prep0')`

View on IBM Quantum Platform
Calibration data section: Qubit dropdown menu

### 2Q error (Heron and Nighthawk: CZ, Eagle: ECR)

The two-qubit error per edge from the same batch of measurements used to calculate the [2Q median](#2q-error-median) error. **2Q error (best)** refers to the lowest two-qubit error on any edge of the device, also from this batch of measurements.

View with Qiskit
`backend.target['<instruction>'][<qubit 1>, <qubit 2>]`

View on IBM Quantum Platform
Calibration section: hover over the qubit connection in Map view, or find the value in Table view under the CZ error (Heron and Nighthawk) or ECR error (Eagle) column; find the value for *2Q error (best)* in the Details section

### Median 2Q error (Heron: CZ, Eagle: ECR)

[Average gate fidelity](https://quantum.cloud.ibm.com/docs/api/qiskit/quantum_info#average_gate_fidelity) of the two-qubit operation from randomized benchmarking. Measured in "isolation": batches with a minimum separation of two qubits between edges. This randomized benchmarking uses alternating layers of single-qubit Cliffords and two-qubit gates, and thus the final 2Q error value includes the error of the layer of single-qubit Cliffords.

Calculate with Qiskit
Follow the example in this [Qiskit Community GitHub notebook](https://github.com/qiskit-community/qiskit-device-benchmarking/blob/main/notebooks/device_rb_w_lf.ipynb)

View on IBM Quantum Platform
Details section; also find per-edge data in the Calibration data section

### 2Q error (layered)

Average error per layered gate (EPLG) in a chain of 100 qubits. Average EPLG measures the average gate error in a layered chain of $N$ qubits ($N$=100 here). It is derived from a similar quantity known as the layer fidelity (LF) where EPLG$_{100}$ = 4/5(1-LF$^{\frac{1}{99}}$) and layer fidelity is the process fidelity of the layered chain of $N$ qubits. For details, see the paper [Benchmarking quantum processor performance at scale](https://arxiv.org/abs/2311.05933). Note that in the paper EPLG is defined for process error, but for consistency with the individually reported gate errors here it is quoted for average gate error, thus the factor of 4/5.

On IBM Quantum Platform, the detailed information card for each QPU has a section called Two-qubit gate error (layered), which provides the expanded view of the lowest `two-qubit gate error (layered)` measured as a function of the number of qubits in the chain. The final value, at chain length 100, is the value presented in the Details section. In practice, six 100-qubit chains (pre-selected based on expected optimal performance) are measured, and the value reported for number of qubits `N` is the lowest error found in a subset length `N` chain searching over the six 100-qubit chains.

Calculate with Qiskit
Follow the example in this [Qiskit Community GitHub notebook](https://github.com/qiskit-community/qiskit-device-benchmarking/blob/main/notebooks/layer_fidelity_single_chain.ipynb)

View on IBM Quantum Platform
Details section, and an expanded view in the Two-qubit gate error (layered) section

### RZZ error (Heron)

Error in the RZZ gate averaged over the RZZ angles using a variant of randomized benchmarking for arbitrary unitaries.

View with Qiskit
Important: Be sure you have set `use_fractional_gates=True` when you load the backend, then you can use `backend.target['rzz'][<qubit 1>, <qubit 2>]`

View on IBM Quantum Platform
Calibration section: Select RZZ in the Connection dropdown menu and hover over the qubit connection in Map view. You can also select RZZ error in the Graph output dropdown menu in Graph view, or find the value in Table view under the RZZ error column

### ID error / √x (sx) error / Pauli-X error / RX error

Error in the finite-duration discrete one-qubit gates, measured from randomized benchmarking. The randomized benchmarking sequence includes SX, ID, and X gates, and it is assumed their errors are the same. The ID gate is a delay of duration equal to the duration of the √X and X gates. The RX gate is also the same duration as the √X and X gates with variable amplitude, and so it is reported as having the same error as these gates.

View with Qiskit
`backend.target['<instruction>'][<qubit 1>, ]`

View on IBM Quantum Platform
Calibration section: Qubit dropdown menu

### SX error (median)

[Average gate fidelity](https://quantum.cloud.ibm.com/docs/api/qiskit/quantum_info#average_gate_fidelity) of the √X (SX) gate from randomized benchmarking, measured simultaneously on all qubits. The randomized benchmarking sequence includes SX, ID, and X gates, and it is assumed their errors are the same.

View on IBM Quantum Platform
Details section

### Z-axis rotation (RZ) error

Error in the virtual RZ gate. Reported as all 0 since these are performed in software.

View with Qiskit
&#x20;`backend.target['<instruction>'][<qubit 1>, ]`

View on IBM Quantum Platform
Calibration section: Connection dropdown menu

### Readout error

The readout error quantifies the average probability of incorrectly measuring a qubit's state. It is commonly calculated as the mean of `prob_meas0_prep1` and `prob_meas1_prep0`, providing a single metric for measurement fidelity.

View with Qiskit
`backend.properties().readout_error(<qubit>)`

View on IBM Quantum Platform
Calibration data section: Qubit dropdown menu

### Readout error (median)

Fidelity of the readout operation. Readout error is measured by preparing the qubit in the $|0\rangle$ ($|1\rangle$) state and measuring the probability of an output in the $|1\rangle$ ($|0\rangle$) state. The reported value is the average of these two errors. The median is taken over all qubits.

View on IBM Quantum Platform
Calibration data section: Details section

### Single-qubit gate length

Duration of a single-qubit gate operation. Note that values shown on IBM Quantum Platform are in nanoseconds. Values returned in Qiskit are in seconds.

View with Qiskit
`backend.target['<instruction>'][<qubit 1>, ].duration`

View on IBM Quantum Platform
Calibration section: Qubit dropdown menu

### Gate length (2Q gates)

Duration of the two-qubit gate operation. Note that values shown on IBM Quantum Platform are in nanoseconds. Values returned in Qiskit are in seconds.

View with Qiskit
`backend.target['<instruction>'][<qubit 1>, <qubit 2> ].duration`

View on IBM Quantum Platform
Calibration section: Qubit dropdown menu

### Readout length

The readout length specifies the duration of the readout operation for a qubit. It measures the time from the initiation of the measurement pulse to the completion of signal digitization, after which the system is ready for the next operation. Understanding this parameter is crucial for optimizing circuit execution, especially when incorporating mid-circuit measurements.

View with Qiskit
For `measure`: `backend.properties().readout_length(<qubit>)` For `measure_2`: `backend.target['measure_2'][<qubit 1>, ].duration`&#x20;

View on IBM Quantum Platform
Calibration data section: Qubit dropdown menu

### Initialization error

The initialization error quantifies the percentage of the population in the $|1\rangle$ state after the default rep-delay and [qubit initialization procedure](https://quantum.cloud.ibm.com/docs/guides/repetition-rate-execution) when the prior experiment prepared the qubit in the $|1\rangle$ state. Note that this is subtly different than the quantity [`prob_meas1_prep0`](#prob-meas1-prep0), which measures the percentage of the measurements assigned to the $|1\rangle$ state. The latter is a measurement of both initialization error and the procedure of discriminating between the $|0\rangle$ and $|1\rangle$ states. In the limit of perfect measurement, the two quantities are the same.

View with Qiskit
`backend.properties().qubit_property(<qubit>, 'init_error')`

View on IBM Quantum Platform
Calibration data section: Qubit dropdown menu

### Additional properties

### Maximum circuits per second (MCPS)

Maximum circuits per second (MCPS) includes measurement, reset, and reinitialization of a circuit with a Hadamard gate and a single measurement.

View with Qiskit
`mcps = backend.configuration().mcps`

View on IBM Quantum Platform
Details section

### CLOPS (or CLOPS\_h)

Circuit layer operations per second (CLOPS) is a measure of how many layers of a 100x100 circuit (hardware-aware circuit) a QPU can execute per unit of time.

Calculate with Qiskit
Find the [CLOPS code](https://github.com/qiskit-community/qiskit-device-benchmarking/tree/main/qiskit_device_benchmarking/clops#readme) in the Qiskit Community GitHub

View on IBM Quantum Platform
Details section

### Status

With [`BackendStatus`](https://quantum.cloud.ibm.com/docs/api/qiskit-ibm-runtime/models-backend-status), you can find the QPU status (for example, `Active`, `Paused`, `Offline`) as well as the number of pending jobs.

View with Qiskit
`print(backend.status().status_msg)`, `print(backend.status().pending_jobs)`

View on IBM Quantum Platform
Details section

### Topology diagram or coupling map

A diagram that indicates the pairs of qubits that support two-qubit gate operations between them. This is also called the coupling map or connectivity. Qubits are represented as circles and the supported two-qubit gate operations are displayed as lines connecting the qubits.

View with Qiskit
`from qiskit.visualization import plot_gate_map` then `plot_gate_map(backend)`

View on IBM Quantum Platform
Calibration data section; Click on Expand for a larger view&#x20;

> **What does \`error = 1\` mean?**
>
> If the benchmarking of a qubit or edge does not succeed over the course of several days, whether due to poor data quality or other internal factors, the reported error value is considered stale and will be reported as 1. This is not an indication that the qubit or edge is necessarily non-working or that the error is 1; rather, the error is considered undefined and you should proceed with caution when operating that qubit or gate.

## Next steps

> **Recommendations**
>
> - Learn how to [build noise models](https://quantum.cloud.ibm.com/docs/guides/build-noise-models) to do noisy classical simulation.
> - Review the [Transpiler stages](https://quantum.cloud.ibm.com/docs/guides/transpiler-stages) topic to learn about how the transpiler uses backend properties for circuit optimization.
> - Review the [QiskitRuntime backend API](https://quantum.cloud.ibm.com/docs/api/qiskit-ibm-runtime/qiskit-runtime-service#backend) reference.
