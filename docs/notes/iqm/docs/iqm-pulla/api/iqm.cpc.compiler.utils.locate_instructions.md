> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.utils.locate_instructions.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.utils.locate_instructions.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 8fc22c8713c9720c4333e35d4b81c11851d27d9edfb43d86ceabf49da14ee783.

# iqm.cpc.compiler.utils.locate_instructions

iqm.cpc.compiler.utils.locate_instructions(*schedule*, *instruction_type*, *min_duration=0*, *\**, *channels=None*)  
Locate specific instructions in a schedule.

Parameters:  
- **schedule** (*Schedule*) – The schedule to search.

- **instruction_type** ([*type*](https://docs.python.org/3.11/library/functions.html#type "(in Python v3.11)")*\[Instruction\]*) – The type of the instruction to search for.

- **min_duration** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The minimum duration of the instruction to search for (in samples).

- **channels** (*Iterable\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Names of channels in `schedule` to search. Iff None, search all the channels.

Returns:  
For each located instruction, a namedtuple containing the channel name, instruction index, and duration.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[InstructionLocation](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.utils.InstructionLocation.html#iqm.cpc.compiler.utils.InstructionLocation "iqm.cpc.compiler.utils.InstructionLocation")\]
