> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.validate_locus_calibration.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.validate_locus_calibration.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 3da94b413bc36ef464721bda2dc17743311f3c6e6f8b60201ebfe09e032dcf6d.

# iqm.pulse.quantum_ops.validate_locus_calibration

iqm.pulse.quantum_ops.validate_locus_calibration(*cal_data*, *impl*, *op*, *impl_name*, *locus*)  
Validates calibration for a particular gate implementation at particular locus.

Parameters:  
- **cal_data** (*OILCalibrationData*) – Calibration data tree for the locus.

- **impl** ([*type*](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")*\[*[*GateImplementation*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation")*\]*) – GateImplementation class that defines the required parameters.

- **op** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp")) – QuantumOp that impl implements.

- **impl_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – name of the implementation, for error messages.

- **locus** (*Locus*) – Locus of the operation

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – there is something wrong with the calibration data

Return type:  
*None*
