> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.set_calibration_data_for_gate_implementation.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.set_calibration_data_for_gate_implementation.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 12ef3378771cf7898d9f6ea6983887713fae6ceb8955c6cb260db7c5c498d807.

# iqm.cpc.core.config.set_calibration_data_for_gate_implementation

iqm.cpc.core.config.set_calibration_data_for_gate_implementation(*gates*, *gate_name*, *impl_name*, *calib_data*)  
Add gate and/or implementation name and the corresponding calibration data to `gates`.

Parameters:  
- **gates** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*)

- **gate_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **impl_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **calib_data** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\],* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*)

Return type:  
None
