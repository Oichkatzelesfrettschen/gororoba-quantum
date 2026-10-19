> Full piece: [https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qubit_selector.CalibrationDataManager.html](https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qubit_selector.CalibrationDataManager.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 8fa8caca3906315080218a74c74d0b1da3ace8db041c6261939fb84adab1fc5f.

# CalibrationDataManager

Module: [`iqm.qubit_selector.qubit_selector`](https://docs.iqm.tech/4.7/iqm-qubit-selector/api/iqm.qubit_selector.qubit_selector.html#module-iqm.qubit_selector.qubit_selector "iqm.qubit_selector.qubit_selector")

*class* iqm.qubit_selector.qubit_selector.CalibrationDataManager  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Manage calibration data retrieval for the QPU.

Methods

|  |  |
|----|----|
| [`get_calibration_fidelities`](#iqm.qubit_selector.qubit_selector.CalibrationDataManager.get_calibration_fidelities "iqm.qubit_selector.qubit_selector.CalibrationDataManager.get_calibration_fidelities") | Fetch the latest calibration fidelity data for the specified hardware. |

&nbsp;

get_calibration_fidelities(*backend*)  
Fetch the latest calibration fidelity data for the specified hardware.

Parameters:  
**backend** ([*IQMBackend*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qiskit_iqm.iqm_provider.IQMBackend.html#iqm.qiskit_iqm.iqm_provider.IQMBackend "(in IQM client v36.0.0)")) – The IQM backend instance.

Returns:  
A dictionary with calibration data for TQG, SQG, readout fidelities, T1, and T2 times.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]\]

Inheritance

![Inheritance diagram of iqm.qubit_selector.qubit_selector.CalibrationDataManager](https://docs.iqm.tech/4.7/iqm-qubit-selector/_images/inheritance-83a36a82c55a448de842b865650c08faa465cb24.png)
