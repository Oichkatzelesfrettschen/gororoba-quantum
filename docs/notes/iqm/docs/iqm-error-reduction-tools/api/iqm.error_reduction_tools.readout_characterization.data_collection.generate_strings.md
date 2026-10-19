> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_collection.generate_strings.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_collection.generate_strings.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b1200d9893c778131c29da471b62e40e24c499b36da648ce169c80b54a8d2349.

# iqm.error_reduction_tools.readout_characterization.data_collection.generate_strings

iqm.error_reduction_tools.readout_characterization.data_collection.generate_strings(*number_of_qubits*, *number_of_circuits*, *rgen*, *symmetrize=True*)  
Generate random preparation strings of ‘I’ and ‘X’ characters.

Each string encodes a preparation state for a multi-qubit system: ‘I’ = prepare `|0>`, ‘X’ = prepare `|1>` (via X gate).

Parameters:  
- **number_of_qubits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Length of each preparation string (number of qubits).

- **number_of_circuits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Total number of preparation strings to generate.

- **rgen** ([*Generator*](https://numpy.org/doc/stable/reference/random/generator.html#numpy.random.Generator "(in NumPy v2.5)")) – NumPy random number generator instance.

- **symmetrize** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If `True`, generates pairs of complementary strings (I↔X) to balance `|0>` and `|1>` preparations.

Returns:  
List of preparation strings, each of length `number_of_qubits`.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]
