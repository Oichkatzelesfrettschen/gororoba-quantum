> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.move.validate_move_instructions.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.move.validate_move_instructions.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 cd52391f5f85f315d6b37b56aa50956675811ad0383245aee3c999a5160b098c.

# iqm.pulse.gates.move.validate_move_instructions

iqm.pulse.gates.move.validate_move_instructions(*instructions*, *builder*, *validate_prx=True*)  
Circuit-level pass to prepare a circuit containing MOVE gates for compilation.

Validates that circuit conforms to the MOVE gate constraints.

Parameters:  
- **instructions** (*Iterable\[*[*CircuitOperation*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "iqm.pulse.builder.CircuitOperation")*\]*) – quantum circuit to validate

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder")) – schedule builder, encapsulating information about the station

- **validate_prx** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – whether to validate the circuit for PRX gates between MOVE sandwiches as well

Returns:  
`instructions`, unmodified

Raises:  
[**ValueError**](https://docs.python.org/3.11/library/exceptions.html#ValueError "(in Python v3.11)") – Circuit does not conform to MOVE constraints.

Return type:  
*Iterable*\[[*CircuitOperation*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "iqm.pulse.builder.CircuitOperation")\]
