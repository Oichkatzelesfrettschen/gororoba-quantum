> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.transpiler.transpile_insert_moves_into_circuit.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.transpiler.transpile_insert_moves_into_circuit.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 c1dcc2a0a81b1210bad6df188f0957962467d80a6c2bd157477378696600ee3c.

# iqm.cirq_iqm.transpiler.transpile_insert_moves_into_circuit

iqm.cirq_iqm.transpiler.transpile_insert_moves_into_circuit(*cirq_circuit: Circuit*, *device: [IQMDevice](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.devices.iqm_device.IQMDevice.html#iqm.cirq_iqm.devices.iqm_device.IQMDevice "iqm.cirq_iqm.devices.iqm_device.IQMDevice")*, *existing_moves: [ExistingMoveHandlingOptions](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.ExistingMoveHandlingOptions.html#iqm.iqm_client.transpile.ExistingMoveHandlingOptions "iqm.iqm_client.transpile.ExistingMoveHandlingOptions") = ExistingMoveHandlingOptions.KEEP*, *qubit_mapping: QubitMapping \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → Circuit  
Transpile the circuit to insert MOVE gates where needed.

Parameters:  
- **cirq_circuit** (*Circuit*) – Circuit to transpile.

- **device** ([*IQMDevice*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.devices.iqm_device.IQMDevice.html#iqm.cirq_iqm.devices.iqm_device.IQMDevice "iqm.cirq_iqm.devices.iqm_device.IQMDevice")) – Device to transpile for.

- **existing_moves** ([*ExistingMoveHandlingOptions*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.ExistingMoveHandlingOptions.html#iqm.iqm_client.transpile.ExistingMoveHandlingOptions "iqm.iqm_client.transpile.ExistingMoveHandlingOptions")) – How to handle existing MOVE gates, obtained from the IQM client library.

- **qubit_mapping** (*QubitMapping* *\|* *None*) – Mapping from qubit names in the circuit to the device.

Returns:  
Transpiled circuit.

Return type:  
Circuit
