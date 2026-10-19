> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a4065ca10be506ffafc7af85bb9cbb989a86f8ab4a4b6938770a6c084b32f50d.

# QuantumOp

Module: [`iqm.pulse.quantum_ops`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.html#module-iqm.pulse.quantum_ops "iqm.pulse.quantum_ops")

*class* iqm.pulse.quantum_ops.QuantumOp(*name*, *arity=1*, *params=\<factory\>*, *optional_params=\<factory\>*, *implementations=\<factory\>*, *symmetric=False*, *aggregator_class=None*, *default_implementation=''*, *defaults_for_locus=\<factory\>*, *unitary=None*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Describes a native quantum operation type.

*Quantum operations* (or “ops” in short), are simple, abstract, self-contained actions one can execute on a station as parts of a quantum circuit. They include quantum gates, measurements, and resets. They must have an unambiguous definition in terms of their *intended* effect on the computational subspace of the quantum subsystems (qubits, qudits, qumodes…) they act on. They are implemented on the hardware using [`instruction schedules`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.schedule.Schedule.html#iqm.pulse.playlist.schedule.Schedule "iqm.pulse.playlist.schedule.Schedule").

A QuantumOp can also be a *metaoperation*, which (in an idealized picture) has no effect on the quantum state, but affects the scheduling of the other ops. [`Execution barriers`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.barrier.Barrier.html#iqm.pulse.gates.barrier.Barrier "iqm.pulse.gates.barrier.Barrier") are an example of a metaoperation.

The ops can have any number of named parameters. For example, `PRX` is a two-parameter quantum gate family, whereas `CZ` is a single gate with no parameters.

A *locus* (plural: loci) is a `tuple[str, ...]` (an ordered sequence) of CHAD component names an instance of a quantum operation acts on. The locus consists of those QPU components that store the quantum information the operation acts on. For example, a `CZ` gate implemented using a flux pulse on the coupler connecting the qubits *does not* include the coupler in its locus, since the coupler is simply an implementation detail.

In a quantum circuit each operation type normally has several different loci. For example, you could have a `PRX` gate being used on qubits `{('QB1',), ('QB2',), ('QB5',)}`, or a `CZ` gate used on qubit pairs `{('QB1', 'QB3'), ('QB3', 'QB5',), ('QB1', 'QB5',)}`.

Each quantum operation can have any number of named *implementations*, each represented by a [`GateImplementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation") subclass. For example, we may have two implementations of the CZ gate, one with just a single flux pulse applied to the coupler, and another one with additional flux pulses applied to the qubits as well.

- operation defines the abstract intention (what)

- implementation defines the concrete method (how)

- locus defines the target of the operation (where)

The quantum operations are typically calibrated using specific calibration experiments that output the required calibration data. Each implementation of each operation can require its own, independent set of calibration data for each locus.

Attributes

|  |  |
|----|----|
| [`aggregator_class`](#iqm.pulse.quantum_ops.QuantumOp.aggregator_class "iqm.pulse.quantum_ops.QuantumOp.aggregator_class") | Class that implements the aggregation of `arity==1` factorizable sub-implementations into the full `arity > 1` implementation. |
| [`arity`](#iqm.pulse.quantum_ops.QuantumOp.arity "iqm.pulse.quantum_ops.QuantumOp.arity") | Number of locus components the operation acts on. |
| [`default_implementation`](#iqm.pulse.quantum_ops.QuantumOp.default_implementation "iqm.pulse.quantum_ops.QuantumOp.default_implementation") | Use this implementation of the op by default. |
| [`factorizable`](#iqm.pulse.quantum_ops.QuantumOp.factorizable "iqm.pulse.quantum_ops.QuantumOp.factorizable") | Whether the QuantumOp is factorizable. |
| [`symmetric`](#iqm.pulse.quantum_ops.QuantumOp.symmetric "iqm.pulse.quantum_ops.QuantumOp.symmetric") | True iff the effect of operation is symmetric in the quantum subsystems it acts on. |
| [`unitary`](#iqm.pulse.quantum_ops.QuantumOp.unitary "iqm.pulse.quantum_ops.QuantumOp.unitary") | Unitary matrix that represents the effect of this quantum operation in the computational basis, or `None` if the quantum operation is not unitary or the exact unitary is not known. |
| [`name`](#iqm.pulse.quantum_ops.QuantumOp.name "iqm.pulse.quantum_ops.QuantumOp.name") | Unique name of the operation. |
| [`params`](#iqm.pulse.quantum_ops.QuantumOp.params "iqm.pulse.quantum_ops.QuantumOp.params") | Maps names of required operation parameters to their allowed types. |
| [`optional_params`](#iqm.pulse.quantum_ops.QuantumOp.optional_params "iqm.pulse.quantum_ops.QuantumOp.optional_params") | Maps names of optional operation parameters to their allowed types. |
| [`implementations`](#iqm.pulse.quantum_ops.QuantumOp.implementations "iqm.pulse.quantum_ops.QuantumOp.implementations") | Maps implementation names to [`GateImplementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation") classes that provide them. |
| [`defaults_for_locus`](#iqm.pulse.quantum_ops.QuantumOp.defaults_for_locus "iqm.pulse.quantum_ops.QuantumOp.defaults_for_locus") | Overrides [`default_implementation`](#iqm.pulse.quantum_ops.QuantumOp.default_implementation "iqm.pulse.quantum_ops.QuantumOp.default_implementation") for some loci. |

Methods

|  |  |
|----|----|
| [`copy`](#iqm.pulse.quantum_ops.QuantumOp.copy "iqm.pulse.quantum_ops.QuantumOp.copy") | Make a copy of `self` with the given changes applied to the contents. |
| [`get_default_implementation_for_locus`](#iqm.pulse.quantum_ops.QuantumOp.get_default_implementation_for_locus "iqm.pulse.quantum_ops.QuantumOp.get_default_implementation_for_locus") | Get the default implementation for the given locus. |
| [`set_default_implementation`](#iqm.pulse.quantum_ops.QuantumOp.set_default_implementation "iqm.pulse.quantum_ops.QuantumOp.set_default_implementation") | Sets the given implementation as the default. |
| [`set_default_implementation_for_locus`](#iqm.pulse.quantum_ops.QuantumOp.set_default_implementation_for_locus "iqm.pulse.quantum_ops.QuantumOp.set_default_implementation_for_locus") | Set the locus-specific default implementation. |

Parameters:  
- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **arity** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **params** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*type*](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")*,* *...\]\]*)

- **optional_params** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*type*](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")*,* *...\]\]*)

- **implementations** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*type*](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")*\[*[*GateImplementation*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation")*\]\]*)

- **symmetric** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **aggregator_class** ([*type*](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")*\[*[*GateImplementation*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation")*\]* *\|* *None*)

- **default_implementation** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **defaults_for_locus** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[Locus,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

- **unitary** (*Callable\[...,* *np.ndarray\]* *\|* *None*)

name*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Unique name of the operation.

arity*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")* *= 1*  
Number of locus components the operation acts on. Each locus component corresponds to a quantum subsystem in the definition of the operation. The computational subspace always consists of the lowest two levels of the subsystem. Zero means the operation can be applied on any number of locus components.

Zero arity implies either that the operation is [`factorizable`](#iqm.pulse.quantum_ops.QuantumOp.factorizable "iqm.pulse.quantum_ops.QuantumOp.factorizable") (e.g. `measure`), or that its implementations do not require any calibration data (e.g. `barrier`).

params*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[type](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)"), ...\]\]*  
Maps names of required operation parameters to their allowed types.

optional_params*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[type](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)"), ...\]\]*  
Maps names of optional operation parameters to their allowed types.

implementations*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [type](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")\[[GateImplementation](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation")\]\]*  
Maps implementation names to [`GateImplementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation") classes that provide them. Each such class should describe the implementation in detail in its docstring.

symmetric*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")* *= False*  
True iff the effect of operation is symmetric in the quantum subsystems it acts on. Only meaningful if `self.arity != 1`.

aggregator_class*: [type](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")\[[GateImplementation](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")* *= None*  
Class that implements the aggregation of `arity==1` factorizable sub-implementations into the full `arity > 1` implementation. Iff None, the QuantumOp is not factorizable. See [`factorizable()`](#iqm.pulse.quantum_ops.QuantumOp.factorizable "iqm.pulse.quantum_ops.QuantumOp.factorizable").

default_implementation*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")* *= ''*  
Use this implementation of the op by default. Must exist in [`implementations`](#iqm.pulse.quantum_ops.QuantumOp.implementations "iqm.pulse.quantum_ops.QuantumOp.implementations").

defaults_for_locus*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[Locus, [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Overrides [`default_implementation`](#iqm.pulse.quantum_ops.QuantumOp.default_implementation "iqm.pulse.quantum_ops.QuantumOp.default_implementation") for some loci. Maps the locus to the gate implementation name that should be the default for that locus. If a locus is not found in this dict (by default, the dict is empty), [`default_implementation`](#iqm.pulse.quantum_ops.QuantumOp.default_implementation "iqm.pulse.quantum_ops.QuantumOp.default_implementation") applies. The listed implementations must all exist in [`implementations`](#iqm.pulse.quantum_ops.QuantumOp.implementations "iqm.pulse.quantum_ops.QuantumOp.implementations").

unitary*: Callable\[..., np.ndarray\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")* *= None*  
Unitary matrix that represents the effect of this quantum operation in the computational basis, or `None` if the quantum operation is not unitary or the exact unitary is not known. The Callable needs to take exactly the arguments given in [`params`](#iqm.pulse.quantum_ops.QuantumOp.params "iqm.pulse.quantum_ops.QuantumOp.params"), for example if `params={'angle': (float,), 'phase': (float,)}`, the function must have signature `f(angle: float, phase: float) -> np.ndarray`. For operations acting on more than 1 qubit, unitary should be given in the big-endian order, i.e. in the basis `np.kron(first_qubit_basis_ket, second_qubit_basis_ket)`.

*property* factorizable*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")*  
Whether the QuantumOp is factorizable.

A factorizable QuantumOp is implemented by aggregating independent single-subsystem operations, and the calibration for an `arity > 1` locus is derived from the ``` arity==1` locus calibrations (for example the ``measure ``` operation). See [`aggregator_class`](#iqm.pulse.quantum_ops.QuantumOp.aggregator_class "iqm.pulse.quantum_ops.QuantumOp.aggregator_class").

copy(*\*\*changes*)  
Make a copy of `self` with the given changes applied to the contents.

Return type:  
[*QuantumOp*](#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp")

set_default_implementation(*default*)  
Sets the given implementation as the default.

Parameters:  
**default** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – name of the new default implementation

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – `default` is unknown or is a special implementation.

Return type:  
*None*

get_default_implementation_for_locus(*locus*)  
Get the default implementation for the given locus.

If no locus-specific default is defined, returns the global default.

Parameters:  
**locus** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – Operation locus to check. For symmetric operations, checks for every locus permutation in [`defaults_for_locus`](#iqm.pulse.quantum_ops.QuantumOp.defaults_for_locus "iqm.pulse.quantum_ops.QuantumOp.defaults_for_locus") (starting with the original) before returning the global default.

Returns:  
Default implementation name for `locus`.

Return type:  
[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")

set_default_implementation_for_locus(*default*, *locus*)  
Set the locus-specific default implementation.

Parameters:  
- **default** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Name of the new default implementation for `locus`.

- **locus** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – Operation locus to set.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – if there is no implementation defined with the name `default` or `default` is a special implementation.

Return type:  
*None*

Inheritance

![Inheritance diagram of iqm.pulse.quantum_ops.QuantumOp](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-ef702556e60a7fbebf944b00c418b11540a18575.png)
