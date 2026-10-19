> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compiler.Compiler.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compiler.Compiler.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 cf2d1b1721a21a6be3ad25bd1a6c4aecc39ef5abce684909f18fed6823a610b8.

# Compiler

Module: [`iqm.cpc.compiler.compiler`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compiler.html#module-iqm.cpc.compiler.compiler "iqm.cpc.compiler.compiler")

*class* iqm.cpc.compiler.compiler.Compiler(*\**, *dut_label*, *chip_topology*, *software_version_set_id*, *component_mapping*, *station_control_settings*, *observation_handler*, *controller_mapping=None*, *gate_definitions=None*, *circuit_stages=None*, *pulse_stages=None*, *final_stages=None*, *pp_stages=None*, *compiler_options=None*, *name='IQM Compiler'*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Compile quantum circuits into jobs that can be submitted to a quantum computer.

Parameters:  
- **dut_label** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – DUT label of the chip being used.

- **chip_topology** (*ChipTopology*) – Connectivity of the quantum chip.

- **software_version_set_id** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – An integer ID representing the software versions in the current python environment.

- **component_mapping** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Mapping of logical QPU component names to physical QPU component names. `None` means the identity mapping.

- **station_control_settings** (*SettingNode*) – Settings for the station instrument controllers.

- **controller_mapping** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]\]* *\|* *None*) – Dictionary that maps physical QPU component names to their device controller names. The dictionary is of the form: `{<component_name>: {<operation_name>: <controller name>}}`, where operation is one of the following: “drive”, “readout”, “flux” (not all components have all operations supported).

- **gate_definitions** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *QuantumOp\]* *\|* *None*) – Names of quantum operations mapped to their definitions, see `QuantumOp`.

- **observation_handler** ([*ObservationHandler*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.observation.observation_handler.ObservationHandler.html#iqm.cpc.core.observation.observation_handler.ObservationHandler "iqm.cpc.core.observation.observation_handler.ObservationHandler")) – Observation handler.

- **circuit_stages** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*CompilationStage*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.CompilationStage.html#iqm.cpc.compiler.compilation_stage.CompilationStage "iqm.cpc.compiler.compilation_stage.CompilationStage")*\]* *\|* *None*) – Compilation stages to use in processing gate-level (and above) circuits. `None` means none. Note that meaningful circuit compilation requires at least some stages. These stages are sweepable in the compilation loop via their stage settings.

- **pulse_stages** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*CompilationStage*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.CompilationStage.html#iqm.cpc.compiler.compilation_stage.CompilationStage "iqm.cpc.compiler.compilation_stage.CompilationStage")*\]* *\|* *None*) – Compilation stages to use in processing TimeBox-level (and below) circuits. `None` means none. Note that meaningful circuit compilation requires at least some stages. These stages are sweepable in the compilation loop via their stage settings.

- **final_stages** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*CompilationStage*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.CompilationStage.html#iqm.cpc.compiler.compilation_stage.CompilationStage "iqm.cpc.compiler.compilation_stage.CompilationStage")*\]* *\|* *None*) – Compilation stages to use in creating the final circuit job definition. These stages are not sweepable.

- **pp_stages** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*CompilationStage*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.CompilationStage.html#iqm.cpc.compiler.compilation_stage.CompilationStage "iqm.cpc.compiler.compilation_stage.CompilationStage")*\]* *\|* *None*) – Post-processing stages to use.

- **compiler_options** ([*CompilerOptions*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compiler.CompilerOptions.html#iqm.cpc.compiler.compiler.CompilerOptions "iqm.cpc.compiler.compiler.CompilerOptions") *\|* *None*) – General options to define the compiler behaviour.

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The name of this compiler.

Methods

|  |  |
|----|----|
| [`add_implementation`](#iqm.cpc.compiler.compiler.Compiler.add_implementation "iqm.cpc.compiler.compiler.Compiler.add_implementation") | Adds a new implementation for a quantum operation (gate). |
| [`compile`](#iqm.cpc.compiler.compiler.Compiler.compile "iqm.cpc.compiler.compiler.Compiler.compile") | Run all compiler stages. |
| [`compiler_context`](#iqm.cpc.compiler.compiler.Compiler.compiler_context "iqm.cpc.compiler.compiler.Compiler.compiler_context") | Return initial compiler context dictionary. |
| [`finalize`](#iqm.cpc.compiler.compiler.Compiler.finalize "iqm.cpc.compiler.compiler.Compiler.finalize") | Run `self.final_stages`, i.e. finalize the payload to be sent for execution. |
| [`get_schedule_builder`](#iqm.cpc.compiler.compiler.Compiler.get_schedule_builder "iqm.cpc.compiler.compiler.Compiler.get_schedule_builder") | Get `ScheduleBuilder` for this compiler. |
| [`get_settings`](#iqm.cpc.compiler.compiler.Compiler.get_settings "iqm.cpc.compiler.compiler.Compiler.get_settings") | Build a settings tree for the Compiler. |
| [`post_process`](#iqm.cpc.compiler.compiler.Compiler.post_process "iqm.cpc.compiler.compiler.Compiler.post_process") | Run `self.pp_stages`. |
| [`run_stages`](#iqm.cpc.compiler.compiler.Compiler.run_stages "iqm.cpc.compiler.compiler.Compiler.run_stages") | Run the circuit- and pulses-level stages on the given data. |
| [`set_default_implementation`](#iqm.cpc.compiler.compiler.Compiler.set_default_implementation "iqm.cpc.compiler.compiler.Compiler.set_default_implementation") | Set the default implementation of a gate. |
| [`set_default_implementation_for_loci`](#iqm.cpc.compiler.compiler.Compiler.set_default_implementation_for_loci "iqm.cpc.compiler.compiler.Compiler.set_default_implementation_for_loci") | Set the default implementation for a gate for a specific loci. |
| [`show_stages`](#iqm.cpc.compiler.compiler.Compiler.show_stages "iqm.cpc.compiler.compiler.Compiler.show_stages") | Displays an interactive HTML representation of the compiler stages. |

get_settings(*circuits=None*, *timeboxes=None*, *circuit_stages=None*, *pulse_stages=None*, *final_stages=None*, *qubits=None*, *couplers=None*, *computational_resonators=None*, *create_characterization_nodes=True*)  
Build a settings tree for the Compiler.

The user can modify the returned settings tree (containing the default settings) as they wish, and then pass it to [`compile()`](#iqm.cpc.compiler.compiler.Compiler.compile "iqm.cpc.compiler.compiler.Compiler.compile"). One typical thing to set is the number of **shots** or repetitions of the executed circuit, which is easiest done using `SettingNode.set_shots()`.

Parameters:  
- **circuits** ([*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)") *\|* *None*) – Circuit-level input to be compiled.

- **timeboxes** ([*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)") *\|* *None*) – TimeBox-level input to be compiled. Either `circuits` or `timeboxes` must be provided.

- **circuit_stages** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*CompilationStage*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.CompilationStage.html#iqm.cpc.compiler.compilation_stage.CompilationStage "iqm.cpc.compiler.compilation_stage.CompilationStage")*\]* *\|* *None*) – Circuit-level (and above) compilation stages. If not provided, `self.circuit_stages` will be used.

- **pulse_stages** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*CompilationStage*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.CompilationStage.html#iqm.cpc.compiler.compilation_stage.CompilationStage "iqm.cpc.compiler.compilation_stage.CompilationStage")*\]* *\|* *None*) – TimeBox-level (and below) compilation stages. If not provided, `self.pulse_stages` will be used.

- **final_stages** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*CompilationStage*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.CompilationStage.html#iqm.cpc.compiler.compilation_stage.CompilationStage "iqm.cpc.compiler.compilation_stage.CompilationStage")*\]* *\|* *None*) – Station-control job finalization stages. If not provided, `self.final_stages` will be used.

- **qubits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Names of the qubits to get the settings for.

- **couplers** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Names of the couplers to get the settings for.

- **computational_resonators** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Names of the computational resonators to get the settings for.

- **create_characterization_nodes** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If `True`, characterization nodes will be added the to the settings. Characterization nodes are not required in the standard compilation and leaving them out can give some performance gains in these cases.

Returns:  
The settings tree.

Return type:  
[*SettingNode*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode "(in iqm-exa-common v29.0.0)")

compiler_context(*components*, *settings*, *\*\*kwargs*)  
Return initial compiler context dictionary.

Used automatically by [`compile()`](#iqm.cpc.compiler.compiler.Compiler.compile "iqm.cpc.compiler.compiler.Compiler.compile").

Parameters:  
- **components** ([*ComponentGrouping*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.ComponentGrouping.html#iqm.cpc.core.config.ComponentGrouping "iqm.cpc.core.config.ComponentGrouping") *\|* *None*)

- **settings** ([*SettingNode*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode "(in iqm-exa-common v29.0.0)"))

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]

compile(*circuits=None*, *timeboxes=None*, *components=None*, *settings=None*, *sweeps=None*, *context=None*)  
Run all compiler stages.

Initial context will be derived using [`compiler_context()`](#iqm.cpc.compiler.compiler.Compiler.compiler_context "iqm.cpc.compiler.compiler.Compiler.compiler_context") unless a custom context dictionary is provided.

Parameters:  
- **circuits** ([*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)") *\|* *None*) – Circuit-level input to be compiled.

- **timeboxes** ([*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)") *\|* *None*) – TimeBox-level input to be compiled. Either `circuits` or `timeboxes` must be provided. If this argument is provided, the stages in `self.circuit_stages` will not be run.

- **components** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\]\]* *\|* [*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\]\]\]* *\|* *None*) – Apply the circuits on these active components. If logical component names are used, `self.component_mapping` must contain logic for mapping them into physical ones. If `components` is `None`, the active components used in the circuits can be automatically resolved in a compiler pass.

- **settings** ([*SettingNode*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode "(in iqm-exa-common v29.0.0)") *\|* *None*) – The settings tree to use. If None, the default settings tree will be generated. See [`get_settings()`](#iqm.cpc.compiler.compiler.Compiler.get_settings "iqm.cpc.compiler.compiler.Compiler.get_settings").

- **sweeps** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*Sweep*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Sweep.html#exa.common.data.parameter.Sweep "(in iqm-exa-common v29.0.0)") *\|* [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Sweep*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Sweep.html#exa.common.data.parameter.Sweep "(in iqm-exa-common v29.0.0)")*,* *...\]\]* *\|* *None*) – The sweeps to perform in the job. If None, the job will consist of one trivial sweep spot.

- **context** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]* *\|* *None*) – Custom initial compiler context dictionary. Contents are updated into the default context given by [`compiler_context()`](#iqm.cpc.compiler.compiler.Compiler.compiler_context "iqm.cpc.compiler.compiler.Compiler.compiler_context").

Returns:  
Compiled data, final context.

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]\]

run_stages(*data*, *context*, *stages=None*, *sweeps=None*)  
Run the circuit- and pulses-level stages on the given data.

Circuit- and pulse-level stages can be swept as per the provided sweeps. The provided hard sweeps determine the dimensions of the final Playlist such that one segment (circuit) is generated per hard sweep spot.

Parameters:  
- **data** ([*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")) – The data to compile.

- **context** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*) – Custom initial compiler context dictionary.

- **stages** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*CompilationStage*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.CompilationStage.html#iqm.cpc.compiler.compilation_stage.CompilationStage "iqm.cpc.compiler.compilation_stage.CompilationStage")*\]* *\|* *None*) – compilation stages to be run on `data`. If not provided, `self.circuit stages + self.pulse_stages` will be used. Each stage may make modifications to `context` before it is passed to the next stage.

- **sweeps** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*Sweep*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Sweep.html#exa.common.data.parameter.Sweep "(in iqm-exa-common v29.0.0)") *\|* [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Sweep*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Sweep.html#exa.common.data.parameter.Sweep "(in iqm-exa-common v29.0.0)")*,* *...\]\]* *\|* *None*) – Sweeps to run on `data`. Can contain both hard and soft sweeps.

Returns:  
Processed data, final context.

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")\[[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\], [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]\]

finalize(*data*, *context*, *stages=None*)  
Run `self.final_stages`, i.e. finalize the payload to be sent for execution.

The final stages are not sweepable but their settings can be changed.

Parameters:  
- **data** ([*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")) – The circuit data for the final stages.

- **context** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*) – The compiler context.

- **stages** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*CompilationStage*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.CompilationStage.html#iqm.cpc.compiler.compilation_stage.CompilationStage "iqm.cpc.compiler.compilation_stage.CompilationStage")*\]* *\|* *None*) – The final stages to be run on `data`. If not provided, uses `self.final_stages`.

Returns:  
The finalized payload to be sent for execution and the compiler context.

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]\]

post_process(*data*, *context*, *stages=None*)  
Run `self.pp_stages`.

Post-processing stages are not sweepable and their settings cannot be changed, but one may still pass stateful effects via the context.

Parameters:  
- **context** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*) – The compiler context.

- **data** ([*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")) – The circuit data for the final stages.

- **stages** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*CompilationStage*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.CompilationStage.html#iqm.cpc.compiler.compilation_stage.CompilationStage "iqm.cpc.compiler.compilation_stage.CompilationStage")*\]* *\|* *None*) – The post-processing stages to be run on `data`. If not provided, uses `self.pp_stages`.

Returns:  
Human-readable result data and the compiler context.

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)"), [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]\]

set_default_implementation(*gate_name*, *implementation_name*)  
Set the default implementation of a gate.

Parameters:  
- **gate_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Name of the gate.

- **implementation_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Name of the implementation to set as the default.

Return type:  
None

set_default_implementation_for_loci(*gate_name*, *implementation_name*, *loci*)  
Set the default implementation for a gate for a specific loci.

Parameters:  
- **gate_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Name of the gate.

- **implementation_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Name of the implementation to set as the default for `loci`.

- **loci** ([*Iterable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterable "(in Python v3.11)")*\[*[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *...\]\]*) – Loci of the gate for which to set `implementation_name` as the default.

Return type:  
None

add_implementation(*op_name*, *impl_name*, *impl_class*, *\**, *set_as_default=False*, *overwrite=False*, *quantum_op=None*)  
Adds a new implementation for a quantum operation (gate).

Refreshes the compiler after adding a new implementation.

Parameters:  
- **op_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The name of the quantum operation for which to register a new implementation.

- **impl_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The “human-readable” name with which the new implementation will be found e.g. in settings.

- **impl_class** ([*type*](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")*\[*[*GateImplementation*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation "(in iqm.pulse v15.0.0)")*\]*) – The class of the new implementation to be added.

- **set_as_default** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – Whether to set the new implementation as the default implementation for the operation.

- **overwrite** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If True, replaces any existing implementation of the same name for the operation.

- **quantum_op** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "(in iqm.pulse v15.0.0)") *\|* *None*) – The quantum operation this gate represents. If a QuantumOp is given, it is used as is. If None is given and the same gate has been registered before, the previously registered properties are used. Existing operations cannot be replaced or modified.

Return type:  
None

show_stages(*pass_name=None*)  
Displays an interactive HTML representation of the compiler stages.

Parameters:  
**pass_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*)

Return type:  
[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")

get_schedule_builder(*settings=None*)  
Get `ScheduleBuilder` for this compiler.

Parameters:  
**settings** ([*SettingNode*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.setting_node.SettingNode.html#exa.common.data.setting_node.SettingNode "(in iqm-exa-common v29.0.0)") *\|* *None*) – Settings tree to use. If `None`, the default settings will be used.

Returns:  
ScheduleBuilder object.

Return type:  
[*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "(in iqm.pulse v15.0.0)")

Inheritance

![Inheritance diagram of iqm.cpc.compiler.compiler.Compiler](https://docs.iqm.tech/4.7/iqm-pulla/_images/inheritance-c49bbfbe4cb5b5a522f5a3563d594512a05fa7ce.png)
