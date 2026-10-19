> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.CircuitOperationList.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.CircuitOperationList.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 050503b63e4b0b1780e24cd42991f63e2166c80699846b165adf8b6b1eedcb9f.

# CircuitOperationList

Module: [`iqm.pulse.circuit_operations`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.html#module-iqm.pulse.circuit_operations "iqm.pulse.circuit_operations")

*class* iqm.pulse.circuit_operations.CircuitOperationList(*contents=()*, *\**, *qubits=None*, *num_qubits=0*, *table=None*)  
Bases: [`list`](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")

List of [`CircuitOperation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "iqm.pulse.builder.CircuitOperation") objects representing a quantum circuit.

The class is used to work with CircuitOperations directly. It is mostly meant as convenience to enable easy creation of circuits, calculations of their properties, and mapping them onto physical qubits. In addition to the circuit contents, this class has two important attributes: `qubits` and `table`.

`qubits` defines the list of qubits which are allowed to be in the loci of all the CircuitOperations present in the list. Think about it as Qiskit’s QuantumRegister.

`table` is a `QuantumOpTable`, which contains all the [`QuantumOp`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp") s which are allowed in the circuit. In most cases, the table is simply taken to contain all the default operations defined in [`iqm.pulse`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.html#module-iqm.pulse "iqm.pulse"). When you use this class with a [`ScheduleBuilder`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"), it is good practice to set `table = builder.op_table`. The QuantumOpTable is mutable, so any additional registered gates can automatically be usable in any CircuitOperationList associated with that ScheduleBuilder instance.

The fundamental use of the class would be to first define a new instance:

``` python
circuit = CircuitOperationList(num_qubits=2)
```

The `num_qubits` parameter populates the `qubits` attribute with qubits QB1-QBn, in this case `['QB1', 'QB2']`.

Alternatively, you can provide `qubits` directly:

``` python
circuit = CircuitOperationList(qubits=['QB1', 'QB2'])
```

To add your own QuantumOpTable, initialize like this:

``` python
circuit = CircuitOperationList(num_qubits=2, table=my_table)
```

Remembering that the table is mutable.

If you already have a list of CircuitOperations, you can initialize with it:

``` python
circuit = CircuitOperationList(circuit_ops, table=my_table)
circuit.find_qubits()
```

Calling the [`find_qubits()`](#iqm.pulse.circuit_operations.CircuitOperationList.find_qubits "iqm.pulse.circuit_operations.CircuitOperationList.find_qubits") method populates the `qubits` attribute with the qubits found in loci of the operations in the original circuit. If the list is empty, it will set `qubits` to an empty list, which most of the time is not what you want to do.

The class has the `__add__`, `__mul__` and `__getitem__` methods redefined, which means `circuit * 3`, `circuit1 + circuit2` and `circuit[0:4]` will produce a CircuitOperationList with the same `qubits` and `table` attributes as the original.

To add a `prx` operation to the list, call:

``` python
circuit.add_op('prx', [0], angle, phase, impl_name='drag_crf')
```

The class also has shortcut methods defined, so the above can be shortened to

``` python
circuit.prx(angle, phase, 0, impl_name='drag_crf')
```

which is exactly the same syntax as in Qiskit, with the addition of the implementation name which usually does not need to be used. The names of the shortcut methods are taken from the attached `table` at init. All the operations with non-zero arity will be added as shortcuts.

If all the operations in the circuit are unitary, you can calculate the unitary propagator of the entire circuit by calling:

``` python
U = circuit.get_unitary()
```

The dimension of the unitary will always be defined by the `qubits` attribute. In particular, if your circuit contains 3 qubits, `'QB1', 'QB2', 'QB3'`, but you only add gates to the first two, the resulting unitary will still be an 8x8 matrix, corresponding to the three qubits `'QB1', 'QB2', 'QB3'`, in the big endian convention. With no operations affecting `'QB3'`, the action of the unitary on this qubit is identity.

To map the circuit onto physical qubits, all you need to do is call:

``` python
physical_circuit = circuit.map_loci(physical_qubits)
```

This will create a copy of the circuit, with all the placeholder qubits replaced by the physical qubits, with the order defined by the `qubits` attribute. For example, if `qubits = ['QB1', 'Alice', 'ZZZ']`, and `physical_qubits = ['QB2', 'QB5', 'QB10']`, all occurrences of `'QB1'` will be mapped to `'QB2'`, `'Alice'` to `'QB5'` and `'ZZZ'` to `'QB10'`. The original circuit is not modified, so you can create many copies with different physical qubits, which is helpful when running parallel experiments on a large chip.

Parameters:  
- **contents** (*Iterable\[*[*CircuitOperation*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "iqm.pulse.builder.CircuitOperation")*\]*) – Circuit operations to initialize the circuit with. Can be left out.

- **qubits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – Qubits allowed to be used in operation loci in the circuit.

- **num_qubits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of qubits in the circuit, will initialize `qubits` with `['QB1', 'QB2', ...]`. Ignored if `qubits` is given.

- **table** (*QuantumOpTable* *\|* *None*) – Allowed quantum operations.

Attributes

|                    |     |
|--------------------|-----|
| `qubits`           |     |
| `prx`              |     |
| `prx_12`           |     |
| `cz`               |     |
| `move`             |     |
| `measure`          |     |
| `measure_fidelity` |     |
| `measure_012`      |     |
| `cc_prx`           |     |
| `u`                |     |
| `rz`               |     |
| `id`               |     |

Methods

|  |  |
|----|----|
| [`add_op`](#iqm.pulse.circuit_operations.CircuitOperationList.add_op "iqm.pulse.circuit_operations.CircuitOperationList.add_op") | Adds a new `CircuitOperation` to the circuit. |
| [`add_qubits`](#iqm.pulse.circuit_operations.CircuitOperationList.add_qubits "iqm.pulse.circuit_operations.CircuitOperationList.add_qubits") | Adds generic placeholder qubits from 1 to n. |
| [`barrier`](#iqm.pulse.circuit_operations.CircuitOperationList.barrier "iqm.pulse.circuit_operations.CircuitOperationList.barrier") | Add barrier to the circuit. |
| [`compose`](#iqm.pulse.circuit_operations.CircuitOperationList.compose "iqm.pulse.circuit_operations.CircuitOperationList.compose") | A safer way to add circuits together, but will probably take time. |
| [`count_ops`](#iqm.pulse.circuit_operations.CircuitOperationList.count_ops "iqm.pulse.circuit_operations.CircuitOperationList.count_ops") | Count each type of operation in the circuit. |
| [`find_qubits`](#iqm.pulse.circuit_operations.CircuitOperationList.find_qubits "iqm.pulse.circuit_operations.CircuitOperationList.find_qubits") | Set attribute qubits to qubits in the loci of operations in the list. |
| [`get_unitary`](#iqm.pulse.circuit_operations.CircuitOperationList.get_unitary "iqm.pulse.circuit_operations.CircuitOperationList.get_unitary") | Calculate the overall unitary implemented by a sequence of CircuitOperations. |
| [`map_loci`](#iqm.pulse.circuit_operations.CircuitOperationList.map_loci "iqm.pulse.circuit_operations.CircuitOperationList.map_loci") | Creates a new list of `CircuitOperation` s with locus mapped onto physical qubits. |

find_qubits()  
Set attribute qubits to qubits in the loci of operations in the list.

Return type:  
*None*

add_qubits(*n*)  
Adds generic placeholder qubits from 1 to n.

Parameters:  
**n** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

Return type:  
*None*

get_unitary(*qubit_names=None*)  
Calculate the overall unitary implemented by a sequence of CircuitOperations.

Parameters:  
- **self** – list of CircuitOperations in order

- **qubit_names** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Optionally, the ordering of the qubits.

Returns:  
Array describing the action of the circuit in big endian convention.

Return type:  
[*ndarray*](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")

add_op(*name*, *locus_indices*, *\*args*, *impl_name=None*)  
Adds a new `CircuitOperation` to the circuit.

Appends a new [`CircuitOperation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "iqm.pulse.builder.CircuitOperation") at the end of the list. The `CircuitOperation` is created using a [`QuantumOp`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp") name from the QuantumOpTable attached to the CircuitOperationList. The locus of that [`CircuitOperation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "iqm.pulse.builder.CircuitOperation") is built from the qubits stored in `qubits`, by selecting the qubits at indices given by `locus_indices`. For example, if `qubits` is `['QB1', 'QB2', 'QB4']`, and the `locus_indices` is `[2, 1]`, the locus of the new [`CircuitOperation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "iqm.pulse.builder.CircuitOperation") will be `('QB4', 'QB2')`. All arguments for the values of the params of the requested [`QuantumOp`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp") need to be provided.

Parameters:  
- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Name of the `QuantumOp` which will generate a new `CircuitOperation`.

- **locus_indices** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – Indices of the qubits in the attribute .qubits which will become the locus of the operation.

- **args** – Any arguments the CircuitOperation needs, must correspond to the params of the `QuantumOp`.

- **impl_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – Name of the implementation to use when converting the `CircuitOperation` into a `Timebox` later.

Return type:  
*None*

barrier(*\*locus_indices*)  
Add barrier to the circuit.

Return type:  
*None*

compose(*other*, *locus_indices=None*)  
A safer way to add circuits together, but will probably take time.

All the [`CircuitOperation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "iqm.pulse.builder.CircuitOperation") s from the `'other'` list are appended to the end of this list. The wire `k` of the second circuit is connected to wire `locus_indices[k]` of the first. This is achieved by mapping the locus of each operation in the second circuit onto the qubits of the first.

For example, if the `qubits` of the first list are `['QB1', 'QB2']`, the second list has `['QB3', 'QB4']`, and the locus_indices argument is `[1,0]`, all the operations in the second list will have their `'QB3'` mapped to `'QB2'` and `'QB4'` mapped to `'QB1'`.

Parameters:  
- **other** – Second CircuitOperationList. Must have less or equal qubits than this one.

- **locus_indices** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]* *\|* *None*) – Indices of the qubits in this CircuitOperationList onto which the qubits in the second circuit ar mapped.

Returns:  
Self, with new operations added.

Return type:  
[*Self*](https://docs.python.org/3.11/library/typing.html#typing.Self "(in Python v3.11)")

count_ops()  
Count each type of operation in the circuit.

Returns:  
Counter mapping operation names to numbers of times they occur in the circuit.

Return type:  
[*Counter*](https://docs.python.org/3.11/library/collections.html#collections.Counter "(in Python v3.11)")

map_loci(*locus*, *make_circuit=True*)  
Creates a new list of `CircuitOperation` s with locus mapped onto physical qubits.

Creates a fresh list of fresh [`CircuitOperation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "iqm.pulse.builder.CircuitOperation") s with fresh arguments. If `locus` is provided, it needs to have the same length as the total number of qubits across the circuit, and the qubits will then be mapped onto the new locus. If it is not provided, this is identical to a deepcopy of the original list.

Parameters:  
- **locus** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – List of new qubits to replace the qubits in the loci of the operations in the circuit.

- **make_circuit** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If True, creates a [`CircuitOperationList`](#iqm.pulse.circuit_operations.CircuitOperationList "iqm.pulse.circuit_operations.CircuitOperationList"). If False, it is just a list.

Returns:  
New CircuitOperationList with loci mapped onto new locus.

Return type:  
[*CircuitOperationList*](#iqm.pulse.circuit_operations.CircuitOperationList "iqm.pulse.circuit_operations.CircuitOperationList") \| [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*CircuitOperation*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "iqm.pulse.builder.CircuitOperation")\]

Inheritance

![Inheritance diagram of iqm.pulse.circuit_operations.CircuitOperationList](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-90ef2a69a55a001433e6e0154acbbafb62fd92f2.png)
