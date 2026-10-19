> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.validation.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.validation.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 bd2fd929b5b941db080190844e1074e92e01b61d42deaed3bdcd54abfc974c38.

# validation

Full path: iqm.iqm_client.validation

Validation related helper functions for IQMClient.

Functions

|  |  |
|----|----|
| [`validate_circuit_instructions`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.validation.validate_circuit_instructions.html#iqm.iqm_client.validation.validate_circuit_instructions "iqm.iqm_client.validation.validate_circuit_instructions")(architecture, ...) | Validate the given circuits against the given quantum architecture. |
| [`validate_circuit_moves`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.validation.validate_circuit_moves.html#iqm.iqm_client.validation.validate_circuit_moves "iqm.iqm_client.validation.validate_circuit_moves")(architecture, circuit) | Raise an error if the MOVE gates in the circuit are not valid in the given architecture. |
| [`validate_instruction`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.validation.validate_instruction.html#iqm.iqm_client.validation.validate_instruction "iqm.iqm_client.validation.validate_instruction")(architecture, instruction) | Validate an instruction against the dynamic quantum architecture. |
| [`validate_qubit_mapping`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.validation.validate_qubit_mapping.html#iqm.iqm_client.validation.validate_qubit_mapping "iqm.iqm_client.validation.validate_qubit_mapping")(architecture, circuits) | Validate the given qubit mapping. |
