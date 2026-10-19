> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.models.CircuitCompilationOptions.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.models.CircuitCompilationOptions.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6aca7b7462094f36ac80abfa44edcb4a0fc766002113186017c07a063db5b364.

# CircuitCompilationOptions

Module: [`iqm.iqm_client.models`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.models.html#module-iqm.iqm_client.models "iqm.iqm_client.models")

*class* iqm.iqm_client.models.CircuitCompilationOptions(*max_circuit_duration_over_t2: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *heralding_mode: HeraldingMode = HeraldingMode.NONE*, *move_gate_validation: MoveGateValidationMode = MoveGateValidationMode.STRICT*, *move_gate_frame_tracking: MoveGateFrameTrackingMode = MoveGateFrameTrackingMode.FULL*, *active_reset_cycles: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *dd_mode: DDMode = DDMode.DISABLED*, *dd_strategy: DDStrategy \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Various discrete options for quantum circuit compilation to pulse schedule.

Attributes

|  |  |
|----|----|
| [`active_reset_cycles`](#iqm.iqm_client.models.CircuitCompilationOptions.active_reset_cycles "iqm.iqm_client.models.CircuitCompilationOptions.active_reset_cycles") | Number of active `reset` operations inserted at the beginning of each circuit for each active qubit. |
| [`dd_mode`](#iqm.iqm_client.models.CircuitCompilationOptions.dd_mode "iqm.iqm_client.models.CircuitCompilationOptions.dd_mode") | Control whether dynamical decoupling should be enabled or disabled during the execution. |
| [`dd_strategy`](#iqm.iqm_client.models.CircuitCompilationOptions.dd_strategy "iqm.iqm_client.models.CircuitCompilationOptions.dd_strategy") | A particular dynamical decoupling strategy to be used during the execution. |
| [`heralding_mode`](#iqm.iqm_client.models.CircuitCompilationOptions.heralding_mode "iqm.iqm_client.models.CircuitCompilationOptions.heralding_mode") | Heralding mode to use during the execution. |
| [`max_circuit_duration_over_t2`](#iqm.iqm_client.models.CircuitCompilationOptions.max_circuit_duration_over_t2 "iqm.iqm_client.models.CircuitCompilationOptions.max_circuit_duration_over_t2") | Server-side circuit disqualification threshold. |
| [`move_gate_frame_tracking`](#iqm.iqm_client.models.CircuitCompilationOptions.move_gate_frame_tracking "iqm.iqm_client.models.CircuitCompilationOptions.move_gate_frame_tracking") | MOVE gate frame tracking mode for circuit compilation. |
| [`move_gate_validation`](#iqm.iqm_client.models.CircuitCompilationOptions.move_gate_validation "iqm.iqm_client.models.CircuitCompilationOptions.move_gate_validation") | MOVE gate validation mode for circuit compilation. |

Methods

Parameters:  
- **max_circuit_duration_over_t2** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") *\|* *None*)

- **heralding_mode** (*HeraldingMode*)

- **move_gate_validation** (*MoveGateValidationMode*)

- **move_gate_frame_tracking** (*MoveGateFrameTrackingMode*)

- **active_reset_cycles** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*)

- **dd_mode** (*DDMode*)

- **dd_strategy** (*DDStrategy* *\|* *None*)

max_circuit_duration_over_t2*: [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")* *= None*  
Server-side circuit disqualification threshold. The job is rejected on the server if any circuit in it is estimated to take longer than the shortest T2 time of any qubit used in the circuit, multiplied by this value. Setting this value to `0.0` turns off circuit duration checking. `None` tells the server to use its default value in the check.

heralding_mode*: HeraldingMode* *= 'none'*  
Heralding mode to use during the execution.

move_gate_validation*: MoveGateValidationMode* *= 'strict'*  
MOVE gate validation mode for circuit compilation. This options is ignored on devices that do not support MOVE and for circuits that do not contain MOVE gates.

move_gate_frame_tracking*: MoveGateFrameTrackingMode* *= 'full'*  
MOVE gate frame tracking mode for circuit compilation. This options is ignored on devices that do not support MOVE and for circuits that do not contain MOVE gates.

active_reset_cycles*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")* *= None*  
Number of active `reset` operations inserted at the beginning of each circuit for each active qubit. `None` means active reset is not used but instead reset is done by waiting (relaxation). Integer values smaller than 1 result in neither active nor reset by wait being used, in which case any reset operations must be explicitly added in the circuit.

dd_mode*: DDMode* *= 'disabled'*  
Control whether dynamical decoupling should be enabled or disabled during the execution.

dd_strategy*: DDStrategy \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")* *= None*  
A particular dynamical decoupling strategy to be used during the execution.

Inheritance

![Inheritance diagram of iqm.iqm_client.models.CircuitCompilationOptions](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-d32d84a8057deaddf7cdff97cf604c714dc15439.png)
