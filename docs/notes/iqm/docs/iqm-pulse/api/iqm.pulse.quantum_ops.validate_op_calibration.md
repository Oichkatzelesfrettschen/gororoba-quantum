> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.validate_op_calibration.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.validate_op_calibration.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 10ddbb6c9eb71543d199a9fadd88d1e321c96868abcc05b7bbc3ce8a050ff681.

# iqm.pulse.quantum_ops.validate_op_calibration

iqm.pulse.quantum_ops.validate_op_calibration(*calibration*, *ops*)  
Validates quantum operation calibration data against the known quantum operations.

NOTE: calibration data parameters that have a defined default value are not required to be in the calibration data.

Parameters:  
- **calibration** (*OpCalibrationDataTree*) – quantum operation calibration data tree to validate

- **ops** (*QuantumOpTable*) – known quantum operations and their implementations

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – there is something wrong with the calibration data

Return type:  
*None*
