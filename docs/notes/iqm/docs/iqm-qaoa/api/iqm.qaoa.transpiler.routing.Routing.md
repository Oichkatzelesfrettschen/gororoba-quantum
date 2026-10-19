> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Routing.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Routing.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 38592dbb9d9521a0cbd9dba849ac23b42d09641a6260a2a3ca8eaf91622c0aa6.

# Routing

Module: [`iqm.qaoa.transpiler.routing`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.html#module-iqm.qaoa.transpiler.routing "iqm.qaoa.transpiler.routing")

*class* iqm.qaoa.transpiler.routing.Routing(*problem_bqm*, *qpu*, *initial_mapping=None*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/routing.py#L435-L720)  
Bases: [`BaseRouting`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.BaseRouting.html#iqm.qaoa.transpiler.routing.BaseRouting "iqm.qaoa.transpiler.routing.BaseRouting")

The ‘standard’ routing of a QAOA phase separator.

A [`Routing`](#iqm.qaoa.transpiler.routing.Routing "iqm.qaoa.transpiler.routing.Routing") object is intended to be directly used by a router during routing. This class is meant to be used for the relatively ‘standard’ routers which work by use *swap* gates and interaction gates to move the problem qubits around the QPU. To that end it maintains a list of [`Layer`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Layer.html#iqm.qaoa.transpiler.routing.Layer "iqm.qaoa.transpiler.routing.Layer") objects, a [`Graph`](https://networkx.org/documentation/stable/reference/classes/graph.html#networkx.Graph "(in NetworkX v3.7)") with the interactions not implemented yet and a [`Mapping`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Mapping.html#iqm.qaoa.transpiler.routing.Mapping "iqm.qaoa.transpiler.routing.Mapping") object that represents the current status of mapping between hardware and logical qubits.

A router interacts with a [`Routing`](#iqm.qaoa.transpiler.routing.Routing "iqm.qaoa.transpiler.routing.Routing") object by using the methods [`apply_swap()`](#iqm.qaoa.transpiler.routing.Routing.apply_swap "iqm.qaoa.transpiler.routing.Routing.apply_swap") and [`apply_int()`](#iqm.qaoa.transpiler.routing.Routing.apply_int "iqm.qaoa.transpiler.routing.Routing.apply_int"). Optionally also [`attempt_apply_int()`](#iqm.qaoa.transpiler.routing.Routing.attempt_apply_int "iqm.qaoa.transpiler.routing.Routing.attempt_apply_int"). If the problem BQM contains interactions of strength 0 (e.g., because of padding), those won’t be added into the list of layers. When the method [`apply_int()`](#iqm.qaoa.transpiler.routing.Routing.apply_int "iqm.qaoa.transpiler.routing.Routing.apply_int") is called on those interactions, it is skipped.

Parameters:  
- **problem_bqm** (*BinaryQuadraticModel*) – The optimization problem represented as `BinaryQuadraticModel`.

- **qpu** ([*QPU*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.QPU.html#iqm.qaoa.transpiler.quantum_hardware.QPU "iqm.qaoa.transpiler.quantum_hardware.QPU")) – The QPU representing the hardware qubit topology.

- **initial_mapping** ([*Mapping*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Mapping.html#iqm.qaoa.transpiler.routing.Mapping "iqm.qaoa.transpiler.routing.Mapping") *\|* *None*) – The starting mapping of the logical-to-hardware qubits.

Generally speaking, routing refers to the process of ‘moving’ the problem qubits around the QPU to allow the execution of the interactions between the problem qubits. The standard way to do this is with *swap* gates, but there are special variations e.g., if using *move* gates on a computational resonator.

Attributes

|  |  |
|----|----|
| [`layers`](#iqm.qaoa.transpiler.routing.Routing.layers "iqm.qaoa.transpiler.routing.Routing.layers") | The list of layers of the routing object. |

Methods

|  |  |
|----|----|
| [`apply_int`](#iqm.qaoa.transpiler.routing.Routing.apply_int "iqm.qaoa.transpiler.routing.Routing.apply_int") | Apply interaction gate at the earliest possible layer, add a new layer if necessary. |
| [`apply_swap`](#iqm.qaoa.transpiler.routing.Routing.apply_swap "iqm.qaoa.transpiler.routing.Routing.apply_swap") | Apply swap gate at the earliest possible layer, add a new layer if needed. |
| [`attempt_apply_int`](#iqm.qaoa.transpiler.routing.Routing.attempt_apply_int "iqm.qaoa.transpiler.routing.Routing.attempt_apply_int") | Softer version of [`apply_int()`](#iqm.qaoa.transpiler.routing.Routing.apply_int "iqm.qaoa.transpiler.routing.Routing.apply_int"). |
| [`build_qiskit`](#iqm.qaoa.transpiler.routing.Routing.build_qiskit "iqm.qaoa.transpiler.routing.Routing.build_qiskit") | Build the QAOA circuit from the [`Routing`](#iqm.qaoa.transpiler.routing.Routing "iqm.qaoa.transpiler.routing.Routing") (`self`) in [`qiskit`](https://quantum.cloud.ibm.com/docs/api/qiskit/index#module-qiskit "(in Qiskit v2.5)"). |
| [`count_swap_gates`](#iqm.qaoa.transpiler.routing.Routing.count_swap_gates "iqm.qaoa.transpiler.routing.Routing.count_swap_gates") | Counts the number of swap gates in all [`Layer`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Layer.html#iqm.qaoa.transpiler.routing.Layer "iqm.qaoa.transpiler.routing.Layer")s so far. |
| [`draw`](#iqm.qaoa.transpiler.routing.Routing.draw "iqm.qaoa.transpiler.routing.Routing.draw") | Plot all [`Layer`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Layer.html#iqm.qaoa.transpiler.routing.Layer "iqm.qaoa.transpiler.routing.Layer")s of the routing in batches of 9. |

*property* layers*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[Layer](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Layer.html#iqm.qaoa.transpiler.routing.Layer "iqm.qaoa.transpiler.routing.Layer")\]*  
The list of layers of the routing object.

apply_swap(*gate*, *attempt_int=False*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/routing.py#L473-L516)  
Apply swap gate at the earliest possible layer, add a new layer if needed.

Goes through the existing [`Layer`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Layer.html#iqm.qaoa.transpiler.routing.Layer "iqm.qaoa.transpiler.routing.Layer")s from the end and tries to apply a swap gate between the qubits defined in `gate` at the earliest possible [`Layer`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Layer.html#iqm.qaoa.transpiler.routing.Layer "iqm.qaoa.transpiler.routing.Layer"). That means, as early as possible without crossing any other swap or interaction acting on the same [`HardQubit`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.HardQubit.html#iqm.qaoa.transpiler.quantum_hardware.HardQubit "iqm.qaoa.transpiler.quantum_hardware.HardQubit")s.

Parameters:  
- **gate** (*HardEdge*) – An edge between two [`HardQubit`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.HardQubit.html#iqm.qaoa.transpiler.quantum_hardware.HardQubit "iqm.qaoa.transpiler.quantum_hardware.HardQubit")s where the swap should be applied.

- **attempt_int** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Boolean saying whether an interaction gate should be combined with the swap.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If there is no edge connecting the two hardware qubits in `gate` on the hardware graph.

Return type:  
None

apply_int(*gate*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/routing.py#L518-L569)  
Apply interaction gate at the earliest possible layer, add a new layer if necessary.

Goes through the existing [`Layer`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Layer.html#iqm.qaoa.transpiler.routing.Layer "iqm.qaoa.transpiler.routing.Layer")s from the end and tries to apply an interaction gate between the qubits defined in `gate` at the earliest possible [`Layer`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Layer.html#iqm.qaoa.transpiler.routing.Layer "iqm.qaoa.transpiler.routing.Layer"). That means, as early as possible without crossing any other swap or interaction acting on the same [`HardQubit`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.HardQubit.html#iqm.qaoa.transpiler.quantum_hardware.HardQubit "iqm.qaoa.transpiler.quantum_hardware.HardQubit")s. If an interaction has strength 0, it isn’t added!

Parameters:  
**gate** (*HardEdge*) – An edge between two [`HardQubit`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.HardQubit.html#iqm.qaoa.transpiler.quantum_hardware.HardQubit "iqm.qaoa.transpiler.quantum_hardware.HardQubit")s where the interaction should be applied.

Raises:  
- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If there is no edge connecting the two hardware qubits in `gate` on the hardware graph.

- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If there is no interaction to be applied between the two corresponding logical qubits.

Return type:  
None

attempt_apply_int(*gate*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/routing.py#L571-L587)  
Softer version of [`apply_int()`](#iqm.qaoa.transpiler.routing.Routing.apply_int "iqm.qaoa.transpiler.routing.Routing.apply_int").

It first checks if there is an interaction to be done and doesn’t do anything if there isn’t, as opposed to raising an error. This method is made for cases when it’s not clear whether an interaction has been applied between two logical qubits already.

Parameters:  
**gate** (*HardEdge*) – An edge between two [`HardQubit`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.HardQubit.html#iqm.qaoa.transpiler.quantum_hardware.HardQubit "iqm.qaoa.transpiler.quantum_hardware.HardQubit")s where the interaction should be applied.

Return type:  
None

count_swap_gates()[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/routing.py#L589-L598)  
Counts the number of swap gates in all [`Layer`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Layer.html#iqm.qaoa.transpiler.routing.Layer "iqm.qaoa.transpiler.routing.Layer")s so far.

Return type:  
[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")

build_qiskit(*betas*, *gammas*, *measurement=True*, *cancel_cnots=True*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/routing.py#L600-L684)  
Build the QAOA circuit from the [`Routing`](#iqm.qaoa.transpiler.routing.Routing "iqm.qaoa.transpiler.routing.Routing") (`self`) in [`qiskit`](https://quantum.cloud.ibm.com/docs/api/qiskit/index#module-qiskit "(in Qiskit v2.5)").

The [`Routing`](#iqm.qaoa.transpiler.routing.Routing "iqm.qaoa.transpiler.routing.Routing") (`self`) contains all the information needed to create the phase separator part of the QAOA circuit. This method builds the rest of the circuit from it, i.e.:

1.  It initializes the qubits in the \\\| + \>\\ state by applying the Hadamard gate to all of them.

2.  It applies the interactions by going through the [`Layer`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Layer.html#iqm.qaoa.transpiler.routing.Layer "iqm.qaoa.transpiler.routing.Layer")s of the [`Routing`](#iqm.qaoa.transpiler.routing.Routing "iqm.qaoa.transpiler.routing.Routing").

3.  It applies local fields.

4.  It applies the driver.

5.  It repeats steps 2-4 until it uses up all `betas` and `gammas`.

6.  It applies the measurements and barrier before them.

Parameters:  
- **betas** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*) – The QAOA parameters to be used in the driver (*RX* gate).

- **gammas** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*\]*) – The QAOA parameters to be used in the phase separator (*RZ* and *RZZ* gates).

- **measurement** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Should the circuit contain a layer of measurements or not?

- **cancel_cnots** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – The routing is likely to contain a *SWAP* gate followed by an *RZZ* gate (or vice versa). When decomposed into a particular basis gate set, these contain a pair of *CNOT* gates, which can be cancelled. Iff `cancel_cnots` is `True`, those will be cancelled already in [`build_qiskit()`](#iqm.qaoa.transpiler.routing.Routing.build_qiskit "iqm.qaoa.transpiler.routing.Routing.build_qiskit").

Returns:  
A complete QAOA [`QuantumCircuit`](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)").

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the lengths of the provided `betas` and `gammas` aren’t the same.

Return type:  
[*QuantumCircuit*](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.QuantumCircuit "(in Qiskit v2.5)")

draw()[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/routing.py#L686-L720)  
Plot all [`Layer`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Layer.html#iqm.qaoa.transpiler.routing.Layer "iqm.qaoa.transpiler.routing.Layer")s of the routing in batches of 9.

This creates a series of plots that are shown on the screen. Each plot contains 9 [`Layer`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Layer.html#iqm.qaoa.transpiler.routing.Layer "iqm.qaoa.transpiler.routing.Layer")s arranged in a 3x3 grid. Each [`Layer`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Layer.html#iqm.qaoa.transpiler.routing.Layer "iqm.qaoa.transpiler.routing.Layer") is drawn using [`draw()`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Layer.html#iqm.qaoa.transpiler.routing.Layer.draw "iqm.qaoa.transpiler.routing.Layer.draw"). Therefore, it has the shape of the QPU topology with edges colored based on what is happening on them in the given [`Layer`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Layer.html#iqm.qaoa.transpiler.routing.Layer "iqm.qaoa.transpiler.routing.Layer").

- Yellow highlight if a combination of swap and int is applied.

- Blue highlight if a swap gate is applied.

- Green highlight if an interaction gate is applied.

- No highlight (black) if nothing is happening along the edge.

Return type:  
None

Inheritance

![Inheritance diagram of iqm.qaoa.transpiler.routing.Routing](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-9029d6a246ce84c753408fe9d684d29159a9bdda.png)
