> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.validate_settings.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.validate_settings.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7ce34945428fb9601a2b3365bf458607ccd3ee649a2bcff56c4909e09cdd768c.

# iqm.cpc.compiler.standard_stages.validate_settings

iqm.cpc.compiler.standard_stages.validate_settings(*circuits*, *settings*)  
Validate the settings for circuit execution options (only some combinations make sense).

Raises an error if full MOVE gate tracking is used without move gate validation. Raises a warning if terminal measurements would be used with active reset.

Parameters:  
- **circuits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*Circuit*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)")*\]*) – The circuits to compiler.

- **settings** ([*SettingNode*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode "(in iqm-exa-common v29.0.0)")) – The settings tree to validate.

Returns:  
The circuits as they were.

Raises:  
[**CircuitError**](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.errors.CircuitError.html#iqm.cpc.compiler.errors.CircuitError "iqm.cpc.compiler.errors.CircuitError") – if full MOVE gate tracking is used without move gate validation.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*Circuit*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)")\]
