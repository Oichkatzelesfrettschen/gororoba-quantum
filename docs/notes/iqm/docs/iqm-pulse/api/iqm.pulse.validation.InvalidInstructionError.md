> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.validation.InvalidInstructionError.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.validation.InvalidInstructionError.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 967a0df0a781c4d5bba4c68ed0785b5f5433ef2a4e15a125eb854af2e5e3ceeb.

# iqm.pulse.validation.InvalidInstructionError

*exception* iqm.pulse.validation.InvalidInstructionError(*instruction*, *channel*, *issue_string='unknown reason'*)  
Raised when an instruction is malformed or not supported by the target instrument.

Parameters:  
- **instruction** ([*Instruction*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.playlist.instructions.Instruction.html#iqm.pulse.playlist.instructions.Instruction "iqm.pulse.playlist.instructions.Instruction")) – Offending instruction.

- **channel** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Name of the control channel it is on.

- **issue_string** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Explanation why it is invalid.

Return type:  
*None*
