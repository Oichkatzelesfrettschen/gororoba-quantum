> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_meta_functions.instruction_tuples_to_qc.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_meta_functions.instruction_tuples_to_qc.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1c07c3cb0482125b4d2252a79086b037d4fc1b1430ab482676cc5dec8a9b0dd7.

# iqm.qrisp_iqm.passes.routing.core.sabre_meta_functions.instruction_tuples_to_qc

iqm.qrisp_iqm.passes.routing.core.sabre_meta_functions.instruction_tuples_to_qc(*compiled_instruction_tuples: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[int16, int16, int16\]\]*, *instruction_list: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[Instruction \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")\]*, *original_qc: QuantumCircuit*, *num_physical_qubits: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → QuantumCircuit  
Turn a list of compiled instruction tuples back into a QuantumCircuit.

Uses the instruction list generated from `convert_qc_to_sparse_dag` together with compiled instruction tuples.

Parameters:  
- **compiled_instruction_tuples** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[int16,* *int16,* *int16\]\]*) – The list of compiled instruction tuples.

- **instruction_list** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[Instruction* *\|* *None\]*) – The list of instructions.

- **original_qc** (*QuantumCircuit*) – The QuantumCircuit which is the origin of both of the other arguments.

- **num_physical_qubits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – The number of physical qubits in the target topology. If greater than the original circuit’s qubit count, ancilla qubits are added so that physical qubit indices produced by routing are valid.

Returns:  
The transpiled QuantumCircuit.

Return type:  
*QuantumCircuit*
