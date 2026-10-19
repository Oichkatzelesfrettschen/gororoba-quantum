> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.utils.replace_instruction_in_place.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.utils.replace_instruction_in_place.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 680d84467fc0e5c33058f8d0f44cdad07d89fbd3a6936689f666d7550be04d2f.

# iqm.cpc.compiler.utils.replace_instruction_in_place

iqm.cpc.compiler.utils.replace_instruction_in_place(*schedule*, *channel_name*, *index*, *replacement*)  
Replace an instruction in a schedule with one or more instructions.

Parameters:  
- **schedule** (*Schedule*) – The schedule to modify.

- **channel_name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The name of the channel containing the instruction to replace.

- **index** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The index of the instruction to replace.

- **replacement** (*Iterable\[Instruction\]*) – Instructions to replace the original instruction with.

Returns:  
The modified schedule.

Return type:  
Schedule
