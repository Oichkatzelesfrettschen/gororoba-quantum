> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.CalibrationData.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.CalibrationData.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 8f502f98109cc6f27c0d3559f7ce485bf653f9961265dc67afa07913714b3514.

# iqm.error_reduction_tools.readout_characterization.data_processing.CalibrationData

*class* iqm.error_reduction_tools.readout_characterization.data_processing.CalibrationData  
Bases: [`TypedDict`](https://docs.python.org/3.11/library/typing.html#typing.TypedDict "(in Python v3.11)")

Calibration dataset container.

Attributes

|  |  |
|----|----|
| [`counts_by_prep`](#iqm.error_reduction_tools.readout_characterization.data_processing.CalibrationData.counts_by_prep "iqm.error_reduction_tools.readout_characterization.data_processing.CalibrationData.counts_by_prep") | Measurement counts grouped by preparation string. |
| [`measured_qubits`](#iqm.error_reduction_tools.readout_characterization.data_processing.CalibrationData.measured_qubits "iqm.error_reduction_tools.readout_characterization.data_processing.CalibrationData.measured_qubits") | Ordered list of qubit labels corresponding to each bit position in the measurement bitstrings. |

Methods

counts_by_prep*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]\]*  
Measurement counts grouped by preparation string.

measured_qubits*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Ordered list of qubit labels corresponding to each bit position in the measurement bitstrings.
