> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.optimizers.simplify_circuit.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.optimizers.simplify_circuit.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 55b431227a9e0c376ed88df966a3582983eb5d29681fed91d628720bc265a266.

# iqm.cirq_iqm.optimizers.simplify_circuit

iqm.cirq_iqm.optimizers.simplify_circuit(*circuit: Circuit*, *\**, *max_iterations: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 20*, *drop_final_rz: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*) → Circuit  
Simplifies and optimizes the given circuit.

Currently it

- merges any neighboring gates belonging to the same one-parameter family

- merges all one-qubit rotations into phased X rotations followed by Z rotations

- pushes the Z rotations towards the end of the circuit as far as possible

- drops any empty Moments

This sequence of optimization passes is repeated until the circuit hits a fixed point, or `max_iterations` is exceeded.

Finally, it removes Z rotations that are immediately followed by a Z-basis measurement.

Parameters:  
- **circuit** (*Circuit*) – circuit to simplify

- **max_iterations** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – maximum number of simplification rounds

- **drop_final_rz** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – iff True, drop z rotations that have no successor operations

Returns:  
simplified circuit

Return type:  
*Circuit*
