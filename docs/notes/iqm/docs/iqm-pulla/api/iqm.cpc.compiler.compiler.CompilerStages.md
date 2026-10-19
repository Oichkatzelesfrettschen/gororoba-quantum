> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compiler.CompilerStages.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compiler.CompilerStages.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 83daae497a49bee4bf75818fe68ca15a4d7f923281f4e1c0f5c0c11a67edc4fe.

# CompilerStages

Module: [`iqm.cpc.compiler.compiler`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compiler.html#module-iqm.cpc.compiler.compiler "iqm.cpc.compiler.compiler")

*class* iqm.cpc.compiler.compiler.CompilerStages(*circuit_stages*, *pulse_stages*, *final_stages*, *pp_stages*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Combines all compilation stages under a single object for easy access.

Attributes

|  |  |
|----|----|
| [`circuit_stages`](#iqm.cpc.compiler.compiler.CompilerStages.circuit_stages "iqm.cpc.compiler.compiler.CompilerStages.circuit_stages") | Circuit-level (and above) stages. |
| [`pulse_stages`](#iqm.cpc.compiler.compiler.CompilerStages.pulse_stages "iqm.cpc.compiler.compiler.CompilerStages.pulse_stages") | Pulse-level stages. |
| [`final_stages`](#iqm.cpc.compiler.compiler.CompilerStages.final_stages "iqm.cpc.compiler.compiler.CompilerStages.final_stages") | Final stages. |
| [`pp_stages`](#iqm.cpc.compiler.compiler.CompilerStages.pp_stages "iqm.cpc.compiler.compiler.CompilerStages.pp_stages") | Post-processing stages. |

Methods

Parameters:  
- **circuit_stages** ([*StagesList*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.StagesList.html#iqm.cpc.compiler.compilation_stage.StagesList "iqm.cpc.compiler.compilation_stage.StagesList"))

- **pulse_stages** ([*StagesList*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.StagesList.html#iqm.cpc.compiler.compilation_stage.StagesList "iqm.cpc.compiler.compilation_stage.StagesList"))

- **final_stages** ([*StagesList*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.StagesList.html#iqm.cpc.compiler.compilation_stage.StagesList "iqm.cpc.compiler.compilation_stage.StagesList"))

- **pp_stages** ([*StagesList*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.StagesList.html#iqm.cpc.compiler.compilation_stage.StagesList "iqm.cpc.compiler.compilation_stage.StagesList"))

circuit_stages*: [StagesList](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.StagesList.html#iqm.cpc.compiler.compilation_stage.StagesList "iqm.cpc.compiler.compilation_stage.StagesList")*  
Circuit-level (and above) stages.

pulse_stages*: [StagesList](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.StagesList.html#iqm.cpc.compiler.compilation_stage.StagesList "iqm.cpc.compiler.compilation_stage.StagesList")*  
Pulse-level stages.

final_stages*: [StagesList](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.StagesList.html#iqm.cpc.compiler.compilation_stage.StagesList "iqm.cpc.compiler.compilation_stage.StagesList")*  
Final stages.

pp_stages*: [StagesList](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.StagesList.html#iqm.cpc.compiler.compilation_stage.StagesList "iqm.cpc.compiler.compilation_stage.StagesList")*  
Post-processing stages.

Inheritance

![Inheritance diagram of iqm.cpc.compiler.compiler.CompilerStages](https://docs.iqm.tech/4.7/iqm-pulla/_images/inheritance-3d8698ab61478e9337816a08e3e44bd34c73b907.png)
