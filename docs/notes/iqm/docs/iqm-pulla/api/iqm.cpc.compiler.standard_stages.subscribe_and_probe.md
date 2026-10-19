> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.subscribe_and_probe.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.subscribe_and_probe.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4fc18f294c3d027aebfaecdac260ecce0bcf2d4a5759351383687ec1f38e420d.

# iqm.cpc.compiler.standard_stages.subscribe_and_probe

iqm.cpc.compiler.standard_stages.subscribe_and_probe(*circuits*, *settings*, *context*, *additionally_subscribed_components*, *additionally_probed_components*, *probe_all=True*, *convert_terminal_measurements=True*)  
Add additional terminal measurements to the circuit and modify measurement instruction arguments.

The additional measurements can be subscribed to (i.e. they’d return measurement data) or be just probe pulses for potentially improving the terminal measurement fidelity in case the measurement calibration is not 100% factorizable.

In addition, the pass hashes all readout keys since there is a data processing limit for the readout key length. The keys should then be unmapped in the return data post-processing. The terminal measurements can also be converted to the `measure_fidelity` operation which is calibrated to maximize the fidelity while not necessarily being projective (QNDness is typically not important for the terminal measurement).

Parameters:  
- **circuits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*Circuit*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)")*\]*) – The circuits to compile.

- **settings** ([*SettingNode*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode "(in iqm-exa-common v29.0.0)")) – The settings tree.

- **context** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*) – The Compiler context.

- **additionally_subscribed_components** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – Additional components to measure in the terminal measurement (besides the ones explicitly measured in the circuit itself).

- **additionally_probed_components** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*) – Additional components to send the probe pulse to besides the ones explicitly measured in the circuit itself). The measurement data will not be collected from these components.

- **probe_all** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to send to probe pulse to all components in the terminal measurement (overrides `additionally_probed_components`).

- **convert_terminal_measurements** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to convert the terminal measurement data to the `measure_fidelity` operation that is calibrated to maximize the fidelity while not necessarily being QND. This option will be turned to `False` automatically if active reset is used (active reset is not reliable in the presence of leakage).

Returns:  
The circuits with the aforementioned modifications.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*Circuit*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)")\]
