> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.readout_mitigation.M3IQM.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.readout_mitigation.M3IQM.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 909c7aae9cc80fdf3d0be8cb1b34d095f3e609e7a2c23e603a085d588574c7b5.

# iqm.benchmarks.readout_mitigation.M3IQM

*class* iqm.benchmarks.readout_mitigation.M3IQM(*system: [IQMBackend](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend "(in IQM client v36.0.0)") \| [IQMFacadeBackend](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend.html#iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend "(in IQM client v36.0.0)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *iter_threshold: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") = 4096*)  
Bases: `M3Mitigation`

M3 readout mitigation class modified to work with IQM devices.

Methods

|  |  |
|----|----|
| `_custom_system_info`(system) | Custom system_info implementation for IQM systems. |
| `_grab_additional_cals`(qubits\[, shots, ...\]) | Grab missing calibration data from backend. |
| `_prepare_calibration_circuits`(qubits, ...) | Prepare REM calibration circuits based on the specified method. |
| `_submit_calibration_jobs`(trans_qcs, shots, ...) | Submit calibration circuits as jobs to the backend. |
| [`cals_from_system`](#iqm.benchmarks.readout_mitigation.M3IQM.cals_from_system "iqm.benchmarks.readout_mitigation.M3IQM.cals_from_system")(\[qubits, shots, method, ...\]) | Grab calibration data from system. |

Parameters:  
- **system** ([*IQMBackend*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend "(in IQM client v36.0.0)") *\|* [*IQMFacadeBackend*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend.html#iqm.qiskit_iqm.iqm_provider.IQMFacadeBackend "(in IQM client v36.0.0)") *\|* *None*)

- **iter_threshold** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

cals_from_system(*qubits: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\] \| [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\] \| [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *shots: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *method: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *initial_reset: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*, *cals_file: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *async_cal: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*, *cal_id: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *circuit_compilation_options: [CircuitCompilationOptions](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.models.CircuitCompilationOptions.html#iqm.iqm_client.models.CircuitCompilationOptions "(in IQM client v36.0.0)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Grab calibration data from system.

Parameters:  
- **qubits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]\]* *\|* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]* *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]* *\|* *None*) – Qubits over which to correct calibration data.

- **shots** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*) – Number of shots per circuit. min(1e4, max_shots).

- **method** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – Type of calibration, ‘balanced’ (default for hardware), ‘independent’ (default for simulators), or ‘marginal’.

- **initial_reset** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Use resets at beginning of calibration circuits.

- **cals_file** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – Output path to write JSON calibration data to.

- **async_cal** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Do calibration async in a separate thread.

- **cal_id** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – Calibration set ID to use when submitting calibration circuits.

- **circuit_compilation_options** ([*CircuitCompilationOptions*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.models.CircuitCompilationOptions.html#iqm.iqm_client.models.CircuitCompilationOptions "(in IQM client v36.0.0)") *\|* *None*) – Optional compilation options (e.g. active reset) to pass to `backend.run()`.

Raises:  
**M3Error** – Called while a calibration currently in progress.

Return type:  
None
