> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.validate_circuits.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.standard_stages.validate_circuits.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4c03f75427410fd8f0a01b5e02b2d9488d9970a2df13f324fb146ad8fa442fb8.

# iqm.cpc.compiler.standard_stages.validate_circuits

iqm.cpc.compiler.standard_stages.validate_circuits(*circuits*, *builder*, *context*, *move_gate_validation=True*, *validate_prx=True*, *validate_calset=False*)  
Validate circuits and aggerate metrics data from them.

Parameters:  
- **circuits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*Circuit*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)")*\]*) – The circuits to compile.

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "(in iqm.pulse v15.0.0)")) – The ScheduleBuilder.

- **context** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*) – The compiler context.

- **move_gate_validation** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to do the move gate validation.

- **validate_prx** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to do the validation.

- **validate_calset** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to validate the calibration set (if the calibration point used is not from a calibration set, this validation might not make sense).

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*Circuit*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.circuit_operations.Circuit.html#iqm.pulse.circuit_operations.Circuit "(in iqm.pulse v15.0.0)")\]
