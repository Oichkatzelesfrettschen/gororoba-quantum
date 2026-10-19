> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.diff_cal_data.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.diff_cal_data.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6696694e476e31284d14167cd898e3a50b89e35a1aebea36ff6d59320e93467d.

# iqm.pulse.quantum_ops.diff_cal_data

iqm.pulse.quantum_ops.diff_cal_data(*cal_data*, *impl_parameters*, *optional_keys=()*, *path=()*)  
Compare GateImplementation calibration data to its parameters.

Parameters:  
- **cal_data** (*OILCalibrationData*) – Nested calibration data for a [`GateImplementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation") instance.

- **impl_parameters** (*NestedParams*) – Nested [`GateImplementation`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "iqm.pulse.gate_implementation.GateImplementation") parameters.

- **optional_keys** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\]*) – Additional allowed but not required parameter names. Only on top level.

- **path** ([*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\]*) – Pathname to the current nesting level.

Returns:  
Error message, or None if `cal_data` matches `impl_parameters`.

Return type:  
[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| *None*
