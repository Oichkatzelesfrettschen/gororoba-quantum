> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.get_waveform_parameters.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.get_waveform_parameters.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7528a33e28f833099bc7826b5188c93167fac9a5317739753bab0784a5cfdc88.

# iqm.pulse.gate_implementation.get_waveform_parameters

iqm.pulse.gate_implementation.get_waveform_parameters(*wave*, *label_prefix=''*)  
Parameters that are required to initialize the given Waveform class.

`n_samples` is handled separately since it is determined by the [`Instruction`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction") duration and channel sample rate, and thus is shared by all the waveforms of the Instruction.

Parameters:  
- **wave** ([*type*](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")*\[Waveform\]*) – waveform class

- **label_prefix** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – optional prefix for the parameter labels for providing additional information

Returns:  
parameters of `wave`, in the format expected by [`GateImplementation.parameters`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gate_implementation.GateImplementation.html#iqm.pulse.gate_implementation.GateImplementation.parameters "iqm.pulse.gate_implementation.GateImplementation.parameters"). Waveform parameters that have a defined default will be returned as `Setting` objects and those that do not have default as `Parameter` objects.

Return type:  
[*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), Setting \| Parameter\]
