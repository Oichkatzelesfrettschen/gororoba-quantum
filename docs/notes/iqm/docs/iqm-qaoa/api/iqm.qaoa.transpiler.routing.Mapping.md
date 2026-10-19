> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Mapping.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Mapping.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 be7882c32cce3e581be3d8c7347b4016982614c42ea9dfa4007275fd6a58c8ce.

# Mapping

Module: [`iqm.qaoa.transpiler.routing`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.html#module-iqm.qaoa.transpiler.routing "iqm.qaoa.transpiler.routing")

*class* iqm.qaoa.transpiler.routing.Mapping(*qpu*, *variables*, *partial_initial_mapping=None*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/routing.py#L60-L219)  
Bases: [`BaseMapping`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.BaseMapping.html#iqm.qaoa.transpiler.routing.BaseMapping "iqm.qaoa.transpiler.routing.BaseMapping")

Mapping between logical and hardware qubits.

It maintains two dictionaries: [`log2hard`](#iqm.qaoa.transpiler.routing.Mapping.log2hard "iqm.qaoa.transpiler.routing.Mapping.log2hard") and [`hard2log`](#iqm.qaoa.transpiler.routing.Mapping.hard2log "iqm.qaoa.transpiler.routing.Mapping.hard2log") which are mappings between logical and hardware qubits. They are always kept in sync. The names for the hardware and logical qubits are extracted from `qpu` and `problem_bqm` at initialization.

Parameters:  
- **qpu** ([*QPU*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.QPU.html#iqm.qaoa.transpiler.quantum_hardware.QPU "iqm.qaoa.transpiler.quantum_hardware.QPU")) – a [`QPU`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.QPU.html#iqm.qaoa.transpiler.quantum_hardware.QPU "iqm.qaoa.transpiler.quantum_hardware.QPU") object describing the topology of the QPU, used to get hardware qubits.

- **problem_bqm** – The `BinaryQuadraticModel` of the problem we’re trying to solve, used to get logical qubits.

- **partial_initial_mapping** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[HardQubit,* *LogQubit\]* *\|* *None*) – An optional dictionary that contains a partial mapping to use as a starting point. The keys should be [`HardQubit`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.HardQubit.html#iqm.qaoa.transpiler.quantum_hardware.HardQubit "iqm.qaoa.transpiler.quantum_hardware.HardQubit") and the values [`LogQubit`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.LogQubit.html#iqm.qaoa.transpiler.quantum_hardware.LogQubit "iqm.qaoa.transpiler.quantum_hardware.LogQubit").

- **variables** (*Iterable\[LogQubit\]*)

Raises:  
- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If there are more logical qubits than hardware qubits.

- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If `partial_initial_mapping` is provided, but it’s not bijective.

- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If `partial_initial_mapping` is provided, but it contains qubits not existing on the QPU.

Attributes

|  |  |
|----|----|
| [`hard2log`](#iqm.qaoa.transpiler.routing.Mapping.hard2log "iqm.qaoa.transpiler.routing.Mapping.hard2log") | The dictionary containing the mapping from hardware qubits to logical qubits. |
| [`log2hard`](#iqm.qaoa.transpiler.routing.Mapping.log2hard "iqm.qaoa.transpiler.routing.Mapping.log2hard") | The dictionary containing the mapping from logical qubits to hardware qubits. |

Methods

|  |  |
|----|----|
| [`move_hard`](#iqm.qaoa.transpiler.routing.Mapping.move_hard "iqm.qaoa.transpiler.routing.Mapping.move_hard") | Move a logical qubit from a one hardware qubit to a an unassigned hardware qubit on the QPU. |
| [`swap_hard`](#iqm.qaoa.transpiler.routing.Mapping.swap_hard "iqm.qaoa.transpiler.routing.Mapping.swap_hard") | Swap association between a pair of hardware qubits. |
| [`swap_log`](#iqm.qaoa.transpiler.routing.Mapping.swap_log "iqm.qaoa.transpiler.routing.Mapping.swap_log") | Swap association between a pair of logical qubits. |
| [`update`](#iqm.qaoa.transpiler.routing.Mapping.update "iqm.qaoa.transpiler.routing.Mapping.update") | Update the mapping based on the swap gates found in a [`Layer`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Layer.html#iqm.qaoa.transpiler.routing.Layer "iqm.qaoa.transpiler.routing.Layer") object. |

*property* hard2log*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[HardQubit, LogQubit \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")\]*  
The dictionary containing the mapping from hardware qubits to logical qubits.

*property* log2hard*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[TypeAliasForwardRef('~iqm.qaoa.transpiler.quantum_hardware.LogQubit'), TypeAliasForwardRef('~iqm.qaoa.transpiler.quantum_hardware.HardQubit')\]*  
The dictionary containing the mapping from logical qubits to hardware qubits.

swap_log(*gate*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/routing.py#L135-L148)  
Swap association between a pair of logical qubits.

Updates the dictionaries [`hard2log`](#iqm.qaoa.transpiler.routing.Mapping.hard2log "iqm.qaoa.transpiler.routing.Mapping.hard2log") and [`log2hard`](#iqm.qaoa.transpiler.routing.Mapping.log2hard "iqm.qaoa.transpiler.routing.Mapping.log2hard").

Parameters:  
**gate** (*LogEdge*) – The pair of logical qubits to swap.

Return type:  
None

swap_hard(*gate*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/routing.py#L150-L167)  
Swap association between a pair of hardware qubits.

Updates the dictionaries [`hard2log`](#iqm.qaoa.transpiler.routing.Mapping.hard2log "iqm.qaoa.transpiler.routing.Mapping.hard2log") and [`log2hard`](#iqm.qaoa.transpiler.routing.Mapping.log2hard "iqm.qaoa.transpiler.routing.Mapping.log2hard").

Parameters:  
**gate** (*HardEdge*) – The pair of hardware qubits to swap.

Return type:  
None

move_hard(*source_qubit*, *target_qubit*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/routing.py#L169-L205)  
Move a logical qubit from a one hardware qubit to a an unassigned hardware qubit on the QPU.

The target `target_qubit` must be mapped to `None` in [`hard2log`](#iqm.qaoa.transpiler.routing.Mapping.hard2log "iqm.qaoa.transpiler.routing.Mapping.hard2log") and (correspondingly) it must not appear among the values of [`log2hard`](#iqm.qaoa.transpiler.routing.Mapping.log2hard "iqm.qaoa.transpiler.routing.Mapping.log2hard"). The mapping dictionaries [`hard2log`](#iqm.qaoa.transpiler.routing.Mapping.hard2log "iqm.qaoa.transpiler.routing.Mapping.hard2log") and [`log2hard`](#iqm.qaoa.transpiler.routing.Mapping.log2hard "iqm.qaoa.transpiler.routing.Mapping.log2hard") are changed as follows:

- The value assigned to the key `source_qubit` in [`hard2log`](#iqm.qaoa.transpiler.routing.Mapping.hard2log "iqm.qaoa.transpiler.routing.Mapping.hard2log") changes to `None`. The value assigned to `target_qubit` changes to the previous value of `source_qubit`.

- The dictionary [`log2hard`](#iqm.qaoa.transpiler.routing.Mapping.log2hard "iqm.qaoa.transpiler.routing.Mapping.log2hard") is modified correspondingly. The value `source_qubit` is changed to `target_qubit`.

Parameters:  
- **source_qubit** (*HardQubit*) – The [`HardQubit`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.HardQubit.html#iqm.qaoa.transpiler.quantum_hardware.HardQubit "iqm.qaoa.transpiler.quantum_hardware.HardQubit") whose [`LogQubit`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.LogQubit.html#iqm.qaoa.transpiler.quantum_hardware.LogQubit "iqm.qaoa.transpiler.quantum_hardware.LogQubit") is being moved.

- **target_qubit** (*HardQubit*) – The [`HardQubit`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.HardQubit.html#iqm.qaoa.transpiler.quantum_hardware.HardQubit "iqm.qaoa.transpiler.quantum_hardware.HardQubit") where the [`LogQubit`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.quantum_hardware.LogQubit.html#iqm.qaoa.transpiler.quantum_hardware.LogQubit "iqm.qaoa.transpiler.quantum_hardware.LogQubit") is being moved.

Raises:  
- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the `target_qubit` is already assigned to a different logical qubit.

- [**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If the `source_qubit` is not assigned to any logical qubit.

Return type:  
None

update(*layer*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/qaoa/transpiler/routing.py#L207-L219)  
Update the mapping based on the swap gates found in a [`Layer`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Layer.html#iqm.qaoa.transpiler.routing.Layer "iqm.qaoa.transpiler.routing.Layer") object.

A convenience function that iterates over the gates in a [`Layer`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Layer.html#iqm.qaoa.transpiler.routing.Layer "iqm.qaoa.transpiler.routing.Layer") object and swaps the hardware qubits corresponding to swap gates.

Parameters:  
**layer** ([*Layer*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.qaoa.transpiler.routing.Layer.html#iqm.qaoa.transpiler.routing.Layer "iqm.qaoa.transpiler.routing.Layer")) – The layer whose swap gates are used.

Return type:  
None

Inheritance

![Inheritance diagram of iqm.qaoa.transpiler.routing.Mapping](https://docs.iqm.tech/4.7/iqm-qaoa/_images/inheritance-e29f48313d0c2df0490d09e32ab26666b8523785.png)
