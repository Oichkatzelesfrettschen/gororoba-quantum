> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.star.star.RoutingStar.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.star.star.RoutingStar.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 07dbd206fec2b064e6c6883f02392a1fd4866252aec20cc4681abe5c589d6c15.

# RoutingStar

Module: [`iqm.qaoa.transpiler.star.star`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.star.star.html#module-iqm.qaoa.transpiler.star.star "iqm.qaoa.transpiler.star.star")

*class* iqm.qaoa.transpiler.star.star.RoutingStar(*problem_bqm*, *qpu*, *initial_mapping=None*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/star/star.py#L36-L286)  
Bases: [`BaseRouting`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.BaseRouting.html#iqm.qaoa.transpiler.routing.BaseRouting "iqm.qaoa.transpiler.routing.BaseRouting")

Routing of a QAOA phase separator on the star topology.

The routing layers in [`RoutingStar`](#iqm.qaoa.transpiler.star.star.RoutingStar "iqm.qaoa.transpiler.star.star.RoutingStar") are relatively simple (just one gate in each layer). A layer is described by a tuple containing a string describing the gate and an integer describing the [`HardQubit`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.HardQubit.html#iqm.qaoa.transpiler.quantum_hardware.HardQubit "iqm.qaoa.transpiler.quantum_hardware.HardQubit") involved. The star QPUs don’t support *swap* gates. Instead, they use *move* gates.

Parameters:  
- **problem_bqm** ([*BinaryQuadraticModel*](https://docs.dwavequantum.com/en/latest/ocean/api_ref_dimod/models.html#dimod.binary.BinaryQuadraticModel "(in D-Wave Quantum Computing Products v9.5.0)")) – The optimization problem represented as `BinaryQuadraticModel`.

- **qpu** ([*StarQPU*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.StarQPU.html#iqm.qaoa.transpiler.quantum_hardware.StarQPU "iqm.qaoa.transpiler.quantum_hardware.StarQPU")) – The QPU representing the hardware qubit topology.

- **initial_mapping** ([*Mapping*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Mapping.html#iqm.qaoa.transpiler.routing.Mapping "iqm.qaoa.transpiler.routing.Mapping") *\|* *None*) – The starting mapping of the logical-to-hardware qubits.

Attributes

|  |  |
|----|----|
| [`layers`](#iqm.qaoa.transpiler.star.star.RoutingStar.layers "iqm.qaoa.transpiler.star.star.RoutingStar.layers") | The list of layers of the star routing object. |

Methods

|  |  |
|----|----|
| [`apply_directed_int`](#iqm.qaoa.transpiler.star.star.RoutingStar.apply_directed_int "iqm.qaoa.transpiler.star.star.RoutingStar.apply_directed_int") | Apply interaction between the resonator and an outer qubit. |
| [`apply_move_in`](#iqm.qaoa.transpiler.star.star.RoutingStar.apply_move_in "iqm.qaoa.transpiler.star.star.RoutingStar.apply_move_in") | Apply move gate (to move a qubit into the resonator). |
| [`apply_move_out`](#iqm.qaoa.transpiler.star.star.RoutingStar.apply_move_out "iqm.qaoa.transpiler.star.star.RoutingStar.apply_move_out") | Apply move gate (to move a qubit out of the resonator). |
| [`build_qiskit`](#iqm.qaoa.transpiler.star.star.RoutingStar.build_qiskit "iqm.qaoa.transpiler.star.star.RoutingStar.build_qiskit") | Build the entire QAOA circuit in [`qiskit`](https://quantum.cloud.ibm.com/docs/api/qiskit/index#module-qiskit "(in Qiskit v2.5)"). |
| [`count_move_gates`](#iqm.qaoa.transpiler.star.star.RoutingStar.count_move_gates "iqm.qaoa.transpiler.star.star.RoutingStar.count_move_gates") | Counts the number of move gates in the routing. |
| [`draw`](#iqm.qaoa.transpiler.star.star.RoutingStar.draw "iqm.qaoa.transpiler.star.star.RoutingStar.draw") | Plot all layers of the routing in batches of 9. |

*property* layers*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]*  
The list of layers of the star routing object.

apply_move_in(*qubit*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/star/star.py#L63-L82)  
Apply move gate (to move a qubit into the resonator).

Parameters:  
**qubit** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The [`HardQubit`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.HardQubit.html#iqm.qaoa.transpiler.quantum_hardware.HardQubit "iqm.qaoa.transpiler.quantum_hardware.HardQubit") whose logical qubit is moved to the central resonator.

Raises:  
- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the central resonator is already occupied by a logical qubit (so a different logical qubit can’t be moved there).

- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the target qubit doesn’t contain a logical qubit.

Return type:  
None

apply_move_out(*qubit*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/star/star.py#L84-L102)  
Apply move gate (to move a qubit out of the resonator).

Parameters:  
**qubit** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The [`HardQubit`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.HardQubit.html#iqm.qaoa.transpiler.quantum_hardware.HardQubit "iqm.qaoa.transpiler.quantum_hardware.HardQubit") where the logical qubit from the resonator is moved to.

Raises:  
- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the central resonator is empty, so nothing can’t be moved out of it.

- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the target qubit is already occupied by a different logical qubit.

Return type:  
None

apply_directed_int(*target*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/star/star.py#L104-L125)  
Apply interaction between the resonator and an outer qubit.

The resonator doesn’t support single-qubit gates, so the interaction has to be decomposed in such a way that the single-qubit rotation is applied to the outer `target` qubit.

Parameters:  
**target** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The [`HardQubit`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.HardQubit.html#iqm.qaoa.transpiler.quantum_hardware.HardQubit "iqm.qaoa.transpiler.quantum_hardware.HardQubit") that interacts with the central qubit.

Raises:  
- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the resonator is empty (so no interaction can be done).

- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the target qubit doesn’t correspond to any logical qubit.

Return type:  
None

count_move_gates()[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/star/star.py#L127-L144)  
Counts the number of move gates in the routing.

Counts both ‘move_in’ and ‘move_out’ gates in the routing. In theory, each ‘move_in’ gate should be followed by a corresponding ‘move_out’ gate, but this counts the gates separately because there might be as of yet unforseen situations in which this won’t be true anymore.

Returns:  
The number of ‘move_in’ and ‘move_out’ gates in the entire routing.

Return type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

build_qiskit(*betas*, *gammas*, *measurement=True*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/star/star.py#L146-L222)  
Build the entire QAOA circuit in [`qiskit`](https://quantum.cloud.ibm.com/docs/api/qiskit/index#module-qiskit "(in Qiskit v2.5)").

The [`RoutingStar`](#iqm.qaoa.transpiler.star.star.RoutingStar "iqm.qaoa.transpiler.star.star.RoutingStar") object contains all the information needed to create the phase separator part of the QAOA circuit. This method builds the rest of the circuit from it, i.e.:

1.  It initializes the qubits in the \\\| + \>\\ state by applying the Hadamard gate to all of them.

2.  It goes through the routing layers and applies the corresponding interactions (or move gates).

3.  It applies local fields.

4.  It applies the driver.

5.  It repeats steps 2-4 until it uses up all `betas` and `gammas`.

6.  It applies the measurements and a barrier before them.

Parameters:  
- **betas** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*) – The QAOA parameters to be used in the driver (*RX* gate).

- **gammas** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*) – The QAOA parameters to be used in the phase separator (*RZ* and *RZZ* gates).

- **measurement** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Should the circuit contain a layer of measurements or not?

Returns:  
A complete QAOA [`QuantumCircuit`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)").

Return type:  
[*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")

draw()[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/star/star.py#L224-L286)  
Plot all layers of the routing in batches of 9.

This creates a series of plots that are shown on the screen. Each plot contains 9 layers arranged in a 3x3 grid. Each layer is drawn using a custom procedure. It has the shape of the QPU topology with edges colored based on what is happening on them in the given layer.

- Teal highlight if a ‘move_in’ gate is applied.

- Plum highlight if a ‘move_out’ gate is applied.

- Green highlight if an ‘int’ gate is applied.

- No highlight (black) if nothing is happening along the edge.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the first element of the layers is neither of ‘int’, ‘move_in’ or ‘move_out’.

Return type:  
None

Inheritance

![Inheritance diagram of iqm.qaoa.transpiler.star.star.RoutingStar](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-bc96d86af7c1fd2e49d845899f9249cc4b01468d.png)
