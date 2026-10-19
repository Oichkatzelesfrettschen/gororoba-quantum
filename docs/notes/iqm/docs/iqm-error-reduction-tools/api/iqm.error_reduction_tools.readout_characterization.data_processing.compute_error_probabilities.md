> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.compute_error_probabilities.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.compute_error_probabilities.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e2e0bfea22ff4c588f1a1f862296d7db3ad5ee26fdb6ab9bd9313d844c777228.

# iqm.error_reduction_tools.readout_characterization.data_processing.compute_error_probabilities

iqm.error_reduction_tools.readout_characterization.data_processing.compute_error_probabilities(*data*)  
Compute single-qubit readout error probabilities from calibration data.

Calculates conditional error probabilities P(measured \| prepared) for each measured qubit, aggregating over all preparation strings. Returns per-qubit 2×2 column-stochastic assignment matrices that are directly compatible with `ReadoutErrorMitigation`.

Parameters:  
**data** ([*CalibrationData*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.CalibrationData.html#iqm.error_reduction_tools.readout_characterization.data_processing.CalibrationData "iqm.error_reduction_tools.readout_characterization.data_processing.CalibrationData")) – Calibration data.

Returns:  
Single-qubit error probabilities.

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – If calibration data is empty or `measured_qubits` is missing.

Return type:  
[*ErrorProbabilities*](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.data_processing.ErrorProbabilities.html#iqm.error_reduction_tools.readout_characterization.data_processing.ErrorProbabilities "iqm.error_reduction_tools.readout_characterization.data_processing.ErrorProbabilities")

Example

```
>>> result = compute_error_probabilities(data)
>>> # Directly usable by REM
>>> from src.iqm.error_reduction_tools.rem.mitigation import ReadoutErrorMitigation
>>> mitigator = ReadoutErrorMitigation(result["charact_data"])
>>> # Inspect individual qubit
>>> print(result["charact_data"]["QB1"])
```
