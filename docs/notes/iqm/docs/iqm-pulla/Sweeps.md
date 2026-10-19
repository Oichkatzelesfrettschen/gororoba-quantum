> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/Sweeps.html](https://docs.iqm.tech/4.7/iqm-pulla/Sweeps.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f60e4d4fbec67bd4e5549f571ca3b7a81061754e130e939b0f4fadb76f26e398.

# Sweeps

This notebooks explains *sweeping* in pulse-level execution, that is, performing a loop over a `settings` value. It is recommended to run `Configuration and Usage.ipynb` before this notebook.

```
%matplotlib inline
```

```
import numpy as np
from copy import deepcopy
from IPython.core.display import HTML

from qiskit import QuantumCircuit

from iqm.iqm_client.util import print_env_vars
from iqm.qiskit_iqm import IQMProvider
from iqm.qiskit_iqm.pulse_level_utils import get_qiskit_compiler
from iqm.pulse.playlist.visualisation.base import inspect_playlist
from iqm.pulse.timebox import TimeBox
from iqm.pulse.builder import ScheduleBuilder
from iqm.pulse.playlist.schedule import Segment, Schedule
from iqm.pulse.playlist.instructions import Block
```

```
print_env_vars()

backend = IQMProvider(
    "<IQM Server URL>",
    quantum_computer="<quantum computer name>",
    token="<your API token>",
).get_backend()

iqm_client = backend.client
```

## Qiskit Compiler

When running Qiskit circuits through IQM pulse-level execution, one way is to first transpile the circuit manually in your notebook/script, convert the circuit to the IQM representation, and finally compile the circuit to pulse level for execution.

However, when working on the pulse level, one usually wants to control the routing and transpilation exactly (e.g. route to specific qubits in the chip), whereas the Qiskit transpiler is stochastic in nature. For facilitating pulse-level access in the context of Qiskit, one can use the function `get_qiskit_compiler`. It returns an IQM compiler which contains compiler passes which handle transpilation and conversion to IQM format, so that users may just provide native Qiskit `QuantumCircuit`s directly. It also allows easy routing to a subset of a chip.

```
compiler = get_qiskit_compiler(backend)

# Show the settings for the transpilation stage pass
compiler.get_settings(circuits=[]).stages.qiskit_transpilation.parallelize_and_transpile
```

(stages.qiskit_transpilation.parallelize_and_transpile)

stages.qiskit_transpilation.parallelize_and_transpile: (Name: "stages.qiskit_transpilation.parallelize_and_transpile", class:SettingNode) 0

|  |  |  |  |
|:---|----|:---|:---|
| , collection_type=, element_indices=None), value=True, read_only=False, path='stages.qiskit_transpilation.parallelize_and_transpile.perform_move_routing')"\>perform_move_routing | True |  | perform_move_routing |
| , collection_type=, element_indices=None), value=True, read_only=False, path='stages.qiskit_transpilation.parallelize_and_transpile.optimize_single_qubits')"\>optimize_single_qubits | True |  | optimize_single_qubits |
| , collection_type=, element_indices=None), value=False, read_only=False, path='stages.qiskit_transpilation.parallelize_and_transpile.ignore_barriers_in_1qb_optimization')"\>ignore_barriers_in_1qb_optimization | False |  | ignore_barriers_in_1qb_optimization |
| , collection_type=, element_indices=None), value=True, read_only=False, path='stages.qiskit_transpilation.parallelize_and_transpile.remove_final_rzs')"\>remove_final_rzs | True |  | remove_final_rzs |
| , collection_type=, element_indices=None), value=None, read_only=False, path='stages.qiskit_transpilation.parallelize_and_transpile.existing_moves_handling')"\>existing_moves_handling | not set/auto |  | existing_moves_handling |
| , collection_type=, element_indices=None), value=0, read_only=False, path='stages.qiskit_transpilation.parallelize_and_transpile.optimization_level')"\>optimization_level | 0 |  | optimization_level |
| , collection_type=, element_indices=None), value=None, read_only=False, path='stages.qiskit_transpilation.parallelize_and_transpile.seed_transpiler')"\>seed_transpiler | not set/auto |  | seed_transpiler |
| , collection_type=, element_indices=None), value=None, read_only=False, path='stages.qiskit_transpilation.parallelize_and_transpile.num_processes')"\>num_processes | not set/auto |  | num_processes |

```
# Display the docstring for the stage pass
compiler.show_stages(pass_name="parallelize_and_transpile")
```

Circuit-level Stages (3)

**Stage 0: qiskit_transpilation** Transpile and route Qiskit circuits to the correct architecture.

[TABLE]

**Stage 1: qiskit_to_iqm** Convert Qiskit circuits into the internal circuit representation.

[TABLE]

**Stage 2: circuit_stage** Perform Circuit-level transformations.

[TABLE]

Pulse-level Stages (5)

**Stage 0: circuit_resolution** Resolve Circuits into TimeBoxes.

[TABLE]

**Stage 1: timebox_stage** Perform TimeBox-level transformations.

[TABLE]

**Stage 2: timebox_resolution** Resolve TimeBoxes into Schedules.

[TABLE]

**Stage 3: dynamical_decoupling** Apply dynamical decoupling sequences to idle qubits in the Schedules.

[TABLE]

**Stage 4: schedule_stage** Perform Schedule-level transformations.

[TABLE]

Finalization Stages (2)

**Stage 0: schedule_resolution** Translate Schedules into a hardware-executable Playlist.

[TABLE]

**Stage 1: job_creation** Package the Playlist and metadata into a job description to be submitted to IQM Server.

[TABLE]

Post-processing Stages (2)

**Stage 0: construct_run_result** Aggregate raw hardware data into a structured run result object.

[TABLE]

**Stage 1: construct_data_variables** Map measured counts and states to high-level user variables.

[TABLE]

```
# Compile a Qiskit circuit while fixing some of the transpilation features
qc = QuantumCircuit(2, 2)
qc.x(0)
qc.x(0)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

settings = compiler.get_settings(circuits=[qc])
settings.stages.qiskit_transpilation.parallelize_and_transpile.seed_transpiler = 1  # fix the seed for more deterministic behaviour
settings.stages.qiskit_transpilation.parallelize_and_transpile.optimize_single_qubits = False  # do not remove the two redundant x(0)s

run_definition, context = compiler.compile(
    circuits=[qc],
    components=["QB3", "QB5"],  # this routes the circuit to qubits QB3 and QB5
    settings=settings
)

# Visualize
HTML(inspect_playlist(run_definition.sweep_definition.playlist, [0]))
```

It should be noted that the transpilation options exposed in `settings.stages.qiskit_transpilation.parallelize_and_transpile` are not exhaustive. For highly customized transpilation one should still transpile manually and avoid the Qiskit compiler.

## Sweeps

The specified circuit will be executed with the specified values, resulting in a data point for each different value of the swept quantity. Every setting in the settings tree is in principle sweepable (sweeping some of them makes little sense in practice, but is still *doable*).

### Example: Investigate spectator errors

For optimal QPU performance, each physical component should be “parked” to a flux voltage value that minimizes parasitic interactions with the neighbouring components. The parking is part of the standard calibration of an IQM QPU, but we can investigate its effects by running a two-qubit gate on a connected pair while sweeping a neighbouring coupler’s flux voltage. We should see the gate performance getting worse as we get further away from the correct parking voltage.

Create four circuits to prepare the four states `|00>`, `|01>` `|10>` and `|11>` and then perform a CNOT gate between the two qubits. CNOT should map `|10>` to `|11>` and `|11>` to `|10>`, while leaving the other two states intact. We can measure the probability of being in the correct state in all of these cases, which gives us a rough estimate of how much the bad parking affected the gate operation (it should be noted that this is not a scientifically sound method of state/process tomography, but just a simple example for educational purposes).

```
compiler = get_qiskit_compiler(backend)

# Prepare |00>
qc1 = QuantumCircuit(2, 2)
qc1.cx(0,1)
qc1.measure([0,1], [0,1])

# Prepare |10>
qc2 = QuantumCircuit(2, 2)
qc2.x(0)
qc2.cx(0,1)
qc2.measure([0,1], [0,1])

# Prepare |01>
qc3 = QuantumCircuit(2, 2)
qc3.x(1)
qc3.cx(0,1)
qc3.measure([0,1], [0,1])

# Prepare |11>
qc4 = QuantumCircuit(2, 2)
qc4.x(0)
qc4.x(1)
qc4.cx(0,1)
qc4.measure([0,1], [0,1])

circuits=[qc1, qc2, qc3, qc4]

# First compile without sweeps
settings = compiler.get_settings(circuits=circuits)
run_definition, context = compiler.compile(
    circuits=circuits,
    components=["QB3", "QB5"],  # run on the pair 3-5
    settings=settings
)

# Run the circuits
job_tracker = iqm_client.submit_playlist(run_definition, context=context)
job_tracker.wait_for_completion()

# Instead of the default `job.result()` run the post-processing stages in `compiler` to get the return data in an Xarray Dataset
result = job_tracker.result_exa(compiler=compiler)
result.dataset
```

```
[06-08 17:00:40;I] Waiting for job 019ea789-16f8-78d3-acfd-4da3602d4435 to finish...
```

\<xarray.Dataset\> Size: 72kB\
Dimensions:                                 (circuit_index: 4,\
                                             repetitions: 1000, counter_index: 4)\
Coordinates:\
  \* circuit_index                           (circuit_index) int64 32B 0 1 2 3\
  \* repetitions                             (repetitions) int64 8kB 0 1 ... 999\
  \* counter_index                           (counter_index) int64 32B 0 1 2 3\
Data variables:\
    QB3\_\_c_2_0_0_state_single_shot          (circuit_index, repetitions) float64 32kB ...\
    QB5\_\_c_2_0_1_state_single_shot          (circuit_index, repetitions) float64 32kB ...\
    QB3\_\_c_2_0_0_readout                    (circuit_index) float64 32B 0.052...\
    QB5\_\_c_2_0_1_readout                    (circuit_index) float64 32B 0.124...\
    QB3\_\_c_2_0_0_excited_state_probability  (circuit_index) float64 32B 0.009...\
    QB5\_\_c_2_0_1_excited_state_probability  (circuit_index) float64 32B 0.070...\
    counter.result                          (counter_index, circuit_index) float64 128B ...

xarray.Dataset

Dimensions:

- circuit_index: 4
- repetitions: 1000
- counter_index: 4

Coordinates: (3)

circuit_index

(circuit_index)

int64

0 1 2 3

parameter :  
name='circuit_index' label='Circuit index' unit='' data_type=\<DataType.FLOAT: 1\> collection_type=\<CollectionType.SCALAR: 0\> element_indices=None

units :  

standard_name :  
circuit_index

long_name :  
Circuit index

array(\[0, 1, 2, 3\])

repetitions

(repetitions)

int64

0 1 2 3 4 5 ... 995 996 997 998 999

parameter :  
name='repetitions' label='Averaging bin' unit='' data_type=\<DataType.FLOAT: 1\> collection_type=\<CollectionType.SCALAR: 0\> element_indices=None

units :  

standard_name :  
repetitions

long_name :  
Averaging bin

array(\[  0,   1,   2, ..., 997, 998, 999\], shape=(1000,))

counter_index

(counter_index)

int64

0 1 2 3

parameter :  
name='counter_index' label='Counter state index' unit='' data_type=\<DataType.FLOAT: 1\> collection_type=\<CollectionType.SCALAR: 0\> element_indices=None

standard_name :  
counter_index

long_name :  
Counter state index

units :  

array(\[0, 1, 2, 3\])

Data variables: (7)

QB3\_\_c_2_0_0_state_single_shot

(circuit_index, repetitions)

float64

0.0 0.0 1.0 0.0 ... 1.0 1.0 1.0 1.0

parameter :  
name='QB3\_\_c_2_0_0_state_single_shot' label='QB3\_\_c_2_0_0statesingleshot' unit='' data_type=\<DataType.FLOAT: 1\> collection_type=\<CollectionType.SCALAR: 0\> element_indices=None

standard_name :  
QB3\_\_c_2_0_0_state_single_shot

long_name :  
QB3\_\_c_2_0_0statesingleshot

units :  

array(\[\[0., 0., 1., ..., 0., 0., 0.\],\
       \[1., 1., 1., ..., 1., 1., 1.\],\
       \[0., 0., 0., ..., 0., 0., 0.\],\
       \[1., 1., 1., ..., 1., 1., 1.\]\], shape=(4, 1000))

QB5\_\_c_2_0_1_state_single_shot

(circuit_index, repetitions)

float64

0.0 0.0 1.0 0.0 ... 0.0 1.0 0.0 0.0

parameter :  
name='QB5\_\_c_2_0_1_state_single_shot' label='QB5\_\_c_2_0_1statesingleshot' unit='' data_type=\<DataType.FLOAT: 1\> collection_type=\<CollectionType.SCALAR: 0\> element_indices=None

standard_name :  
QB5\_\_c_2_0_1_state_single_shot

long_name :  
QB5\_\_c_2_0_1statesingleshot

units :  

array(\[\[0., 0., 1., ..., 0., 0., 0.\],\
       \[1., 1., 1., ..., 0., 1., 1.\],\
       \[1., 1., 1., ..., 1., 1., 1.\],\
       \[0., 0., 0., ..., 1., 0., 0.\]\], shape=(4, 1000))

QB3\_\_c_2_0_0_readout

(circuit_index)

float64

0.052 0.91 0.055 0.91

parameter :  
name='QB3\_\_c_2_0_0_readout' label='Averaged readout data' unit='' data_type=\<DataType.FLOAT: 1\> collection_type=\<CollectionType.SCALAR: 0\> element_indices=None

standard_name :  
QB3\_\_c_2_0_0_readout

long_name :  
QB3\_\_c_2_0_0 Averaged readout data

units :  
V

array(\[0.052, 0.91 , 0.055, 0.91 \])

QB5\_\_c_2_0_1_readout

(circuit_index)

float64

0.124 0.877 0.87 0.14

parameter :  
name='QB5\_\_c_2_0_1_readout' label='Averaged readout data' unit='' data_type=\<DataType.FLOAT: 1\> collection_type=\<CollectionType.SCALAR: 0\> element_indices=None

standard_name :  
QB5\_\_c_2_0_1_readout

long_name :  
QB5\_\_c_2_0_1 Averaged readout data

units :  
V

array(\[0.124, 0.877, 0.87 , 0.14 \])

QB3\_\_c_2_0_0_excited_state_probability

(circuit_index)

float64

0.009398 0.9928 0.01284 0.9928

parameter :  
name='QB3\_\_c_2_0_0_excited_state_probability' label='QB3\_\_c_2_0_0 excited state probability' unit='' data_type=\<DataType.FLOAT: 1\> collection_type=\<CollectionType.SCALAR: 0\> element_indices=None

standard_name :  
QB3\_\_c_2_0_0_excited_state_probability

long_name :  
QB3\_\_c_2_0_0 excited state probability

units :  

array(\[0.00939828, 0.99277937, 0.01283668, 0.99277937\])

QB5\_\_c_2_0_1_excited_state_probability

(circuit_index)

float64

0.07035 0.922 0.914 0.08844

parameter :  
name='QB5\_\_c_2_0_1_excited_state_probability' label='QB5\_\_c_2_0_1 excited state probability' unit='' data_type=\<DataType.FLOAT: 1\> collection_type=\<CollectionType.SCALAR: 0\> element_indices=None

standard_name :  
QB5\_\_c_2_0_1_excited_state_probability

long_name :  
QB5\_\_c_2_0_1 excited state probability

units :  

array(\[0.07034608, 0.92196336, 0.9140466 , 0.08844153\])

counter.result

(counter_index, circuit_index)

float64

0.859 0.043 0.092 ... 0.017 0.099

parameter :  
name='counter.result' label="Multi-qubit state probabilities for \['QB3\_\_c_2_0_0', 'QB5\_\_c_2_0_1'\]" unit='' data_type=\<DataType.FLOAT: 1\> collection_type=\<CollectionType.NDARRAY: 2\> element_indices=None

units :  

standard_name :  
counter.result

long_name :  
Multi-qubit state probabilities for \['QB3\_\_c_2_0_0', 'QB5\_\_c_2_0_1'\]

array(\[\[0.859, 0.043, 0.092, 0.049\],\
       \[0.089, 0.047, 0.853, 0.041\],\
       \[0.017, 0.08 , 0.038, 0.811\],\
       \[0.035, 0.83 , 0.017, 0.099\]\])

Indexes: (3)

- circuit_index

  PandasIndex

  
  PandasIndex(Index(\[0, 1, 2, 3\], dtype='int64', name='circuit_index'))

- repetitions

  PandasIndex

  
  PandasIndex(Index(\[  0,   1,   2,   3,   4,   5,   6,   7,   8,   9,\
         ...\
         990, 991, 992, 993, 994, 995, 996, 997, 998, 999\],\
        dtype='int64', name='repetitions', length=1000))

- counter_index

  PandasIndex

  
  PandasIndex(Index(\[0, 1, 2, 3\], dtype='int64', name='counter_index'))

Attributes: (0)

```
# In the result dataset, find the bit string probabilities from the data variable "counter.result", and pick the result
# corresponding to each of the four created circuits. Compare the obtained result to the expected theoretical result.
result_for_00 = result.dataset["counter.result"].isel({"circuit_index": 0}).data
print(f"|00> should be mapped to [1.0, 0.0, 0.0, 0.0], we got {result_for_00}, the error is {1-result_for_00[0]}")
result_for_10 = result.dataset["counter.result"].isel({"circuit_index": 1}).data
print(f"|10> should be mapped to [0.0, 0.0, 0.0, 1.0], we got {result_for_10}, the error is {1-result_for_10[3]}")
result_for_01 = result.dataset["counter.result"].isel({"circuit_index": 2}).data
print(f"|01> should be mapped to [0.0, 1.0, 0.0, 0.0], we got {result_for_01}, the error is {1-result_for_01[1]}")
result_for_11 = result.dataset["counter.result"].isel({"circuit_index": 3}).data
print(f"|11> should be mapped to [0.0, 0.0, 1.0, 0.0], we got {result_for_11}, the error is {1-result_for_11[2]}")
```

```
|00> should be mapped to [1.0, 0.0, 0.0, 0.0], we got [0.859 0.089 0.017 0.035], the error is 0.14100000000000001
|10> should be mapped to [0.0, 0.0, 0.0, 1.0], we got [0.043 0.047 0.08  0.83 ], the error is 0.17000000000000004
|01> should be mapped to [0.0, 1.0, 0.0, 0.0], we got [0.092 0.853 0.038 0.017], the error is 0.14700000000000002
|11> should be mapped to [0.0, 0.0, 1.0, 0.0], we got [0.049 0.041 0.811 0.099], the error is 0.18899999999999995
```

```
# Define the sweep over the couper flux voltage (centered at the correct value, span 0.5V, 30 points)
settings = compiler.get_settings(circuits=circuits)
voltage = settings.controllers["TC-2-3"].flux.voltage
voltage_sweep = voltage.sweep(np.linspace(-0.5, 0.5, 30) + voltage.value)

# Compile and execute
run_definition, context = compiler.compile(
    circuits=circuits,
    components=["QB3", "QB5"],  # run on the pair 3-5
    settings=settings,
    sweeps=[voltage_sweep]
)

# Run the circuits
job_tracker = iqm_client.submit_playlist(run_definition, context=context)
job_tracker.wait_for_completion()
result = job_tracker.result_exa(compiler=compiler)
```

```
[06-08 17:00:54;I] Waiting for job 019ea789-4cce-7df0-816b-fc8e0aeb76ec to finish...
```

```
# Plot the resulting errors as a function of the flux voltage with native Xarray plotting (Matplotlib)
error_for_00 = 1.0 - result.dataset["counter.result"].isel({"circuit_index": 0, "counter_index": 0})
error_for_10 = 1.0 - result.dataset["counter.result"].isel({"circuit_index": 1, "counter_index": 3})
error_for_01 = 1.0 - result.dataset["counter.result"].isel({"circuit_index": 2, "counter_index": 1})
error_for_11 = 1.0 - result.dataset["counter.result"].isel({"circuit_index": 3, "counter_index": 2})
cumulative_error = error_for_00 + error_for_10 + error_for_01 + error_for_11
cumulative_error.plot()
```

```
[<matplotlib.lines.Line2D at 0x749583c084d0>]
```

![](https://docs.iqm.tech/4.7/iqm-pulla/_images/71378d2ec75c342a2b413a489d24bebc0744a85706a834fe312c87d853944b31.png)

### Example: Parametric circuits and multi-dimensional sweeps

You might have wondered why `compiler.get_settings(circuits)` requires the circuits as an argument. The reason is that the circuit can be a function that creates the actual circuits. The arguments of the circuit generation function then become settings and are thus sweepable, like any other settings.

Compilation also works with multiple sweeps and sweep settings in parallel.

```
def _my_circuit(n_cz: int = 0) -> list[QuantumCircuit]:
    """Perform ``n_cz`` CZ gates on a pair of qubits."""
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.h(1)
    for _ in range(n_cz):
        qc.cz(0, 1)
    qc.measure_all()
    return [qc]

settings = compiler.get_settings(circuits=_my_circuit)

# n_cz is now a setting in circuit
settings.stages.circuit_generation.circuit
```

(circuit)

circuit: (Name: "circuit", class:SettingNode) 0

|  |  |  |  |
|:---|----|:---|:---|
| , collection_type=, element_indices=None), value=0, read_only=False, path='stages.circuit_generation.circuit.n_cz')"\>n_cz | 0 |  | n_cz |

```
# Sweep over n_cz
n_cz_sweep = settings.stages.circuit_generation.circuit.n_cz.sweep([1,2,3])

# Sweep over the default PRX amplitude in parallel for the two qubits such that in a single sweep we sweep both amplitudes
amp_sweep = tuple(
    settings.get_gate_node_for_locus("prx", q).amplitude_i.sweep([0.1, 0.2]) for q in ["QB3", "QB5"]
)

# Compile with both sweeps. With multiple sweeps like this the "Cartesian product" of the sweep dimensions is executed,
# such that:
# 1st sweep spot: (n_cz=1, amps=0.1)
# 2nd sweep spot: (n_cz=2, amps=0.1)
# ...
# 4th sweep spot: (n_cz=1, amps=0.2)
# ...
# 6th sweep spot: (n_cz=3, amps=0.2)

run_definition, context = compiler.compile(
    circuits=_my_circuit,
    components=["QB3", "QB5"],
    sweeps=[amp_sweep, n_cz_sweep]
)
HTML(inspect_playlist(run_definition.sweep_definition.playlist, list(range(6))))
```

### Example: Advanced pulse-level access with TimeBox inputs

IQM Client enables pulse-level access for circuits written on the gate level (e.g. Qiskit circuits), but there are phenomena that simply cannot be studied with a gate-level circuit. For this reason, IQM Client allows compiling circuits written in the native IQM TimeBox intermediate representation.

As an example, compile and run a single-qubit circuit that consists of

1.  measuring a qubit,

2.  performing an X180 gate, and

3.  measuring again,

but make the X180 pulse coincide with the first measurement. Then sweep the exact timing of the drive pulse relative to the beginning of the probe instruction. Of course, reading out a qubit while driving an X rotation probably breaks both of the operations and not achieve an X180 rotation. But sweeping the offset from the probe’s start, at some point the actual physical probe pulse has ended and the qubit is projected to the ground state and *can* perform the X180 rotation. *If* there is some buffer at the end of the probe instruction (after the physical probe pulse has ended), a more efficient timing is achievable by overlapping the X180 with the probe instruction.

Performing this experiment in the circuit-level is simply impossible. The measurement operation will block its locus (QB1) for its full duration when compiling from the gate-level (as it should for consistent operation), so it cannot overlap with the drive pulse. But working natively in the pulse-level it can!

```
def _drive_and_probe_overlap_circuit(builder: ScheduleBuilder, offset: int) -> list[TimeBox]:
    """
    Drive and probe pulse overlapping in a circuit.

    Args:
        builder: The ScheduleBuilder (Compiler's default tool for pulse-level compilation).
        offset: When the drive pulse starts relative from the start of the probe pulse. In integer samples (sampling rate 2 GHz).
    """
    m1 = TimeBox.composite(builder.measure(("QB1",))(key="m1"))
    m2 = TimeBox.composite(builder.measure(("QB1",))(key="m2"))
    prx = builder.prx(("QB1",)).rx(np.pi)
    # Put PRX "inside" the probe TimeBox so the instructions overlap
    drive_channel_name = builder.get_drive_channel("QB1")
    prx_instruction = prx.atom[drive_channel_name][0]
    probe_schedule = deepcopy(builder.resolve_timebox(m1, neighborhood=0))  # deepcopy, otherwise the cached result would get altered
    probe_schedule[drive_channel_name] = Segment([Block(offset), prx_instruction])
    probe_and_prx_box = TimeBox.atomic(probe_schedule, locus_components=("QB1",), label="probe and prx for QB1")
    return [probe_and_prx_box + m2]

compiler = iqm_client.get_standard_compiler()
settings = compiler.get_settings(timeboxes=_drive_and_probe_overlap_circuit)
offset_sweep = settings.stages.circuit_generation.circuit.offset.sweep(320 + 64*np.arange(60))

run_definition, context = compiler.compile(
    timeboxes=_drive_and_probe_overlap_circuit,
    components=["QB1"],
    sweeps=[offset_sweep],
)

# Inspect the playlist and see that the drive pulse overlaps with the probe instruction and moves to the right with the sweep
HTML(inspect_playlist(run_definition.sweep_definition.playlist, list(range(60))))
```

```
job_tracker = iqm_client.submit_playlist(run_definition, context=context)
job_tracker.wait_for_completion()
result = job_tracker.result_exa(compiler=compiler)

# Plot the QB1 excited state probability in the second measurement
result.dataset["QB1__m2_excited_state_probability"].plot()
```

```
[06-08 17:01:59;I] Waiting for job 019ea78a-4e1e-7593-98c4-2a0f3b8f6e74 to finish...
```

```
[<matplotlib.lines.Line2D at 0x749571205e50>]
```

![](https://docs.iqm.tech/4.7/iqm-pulla/_images/cd1fc63b13a565f13815993d77dde9ecadeb489a6d42852f274156021fa9f29c.png)
