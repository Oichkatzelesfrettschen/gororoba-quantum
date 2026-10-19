> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.ExistingMoveHandlingOptions.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.ExistingMoveHandlingOptions.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4e14f715e0885840ba4ee6fc8a060c112282ad1e996cbe0a599bd878c3d05fc6.

# ExistingMoveHandlingOptions

Module: [`iqm.iqm_client.transpile`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.html#module-iqm.iqm_client.transpile "iqm.iqm_client.transpile")

*class* iqm.iqm_client.transpile.ExistingMoveHandlingOptions(*value*)  
Bases: [`str`](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [`Enum`](https://docs.python.org/3.11/library/enum.html#enum.Enum "(in Python v3.11)")

Options for how [`transpile_insert_moves()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.transpile_insert_moves.html#iqm.iqm_client.transpile.transpile_insert_moves "iqm.iqm_client.transpile.transpile_insert_moves") should handle existing MOVE instructions in the circuit.

Attributes

|  |  |
|----|----|
| [`KEEP`](#iqm.iqm_client.transpile.ExistingMoveHandlingOptions.KEEP "iqm.iqm_client.transpile.ExistingMoveHandlingOptions.KEEP") | Strict mode. |
| [`TRUST`](#iqm.iqm_client.transpile.ExistingMoveHandlingOptions.TRUST "iqm.iqm_client.transpile.ExistingMoveHandlingOptions.TRUST") | Lenient mode. |
| [`REMOVE`](#iqm.iqm_client.transpile.ExistingMoveHandlingOptions.REMOVE "iqm.iqm_client.transpile.ExistingMoveHandlingOptions.REMOVE") | Removes existing MOVE instructions from the circuit using [`transpile_remove_moves()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.transpile_remove_moves.html#iqm.iqm_client.transpile.transpile_remove_moves "iqm.iqm_client.transpile.transpile_remove_moves"), and then does the same as TRUST. |

Methods

KEEP *= 'keep'*  
Strict mode. The circuit, including existing MOVE instructions in it, is validated first. Then, any fictional two-qubit gates in the circuit are implemented with qubit-resonator gates.

TRUST *= 'trust'*  
Lenient mode. Same as KEEP, but does not validate the circuit first. Will attempt to fix any apparent user errors in the circuit by adding extra MOVE gates.

REMOVE *= 'remove'*  
Removes existing MOVE instructions from the circuit using [`transpile_remove_moves()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.transpile_remove_moves.html#iqm.iqm_client.transpile.transpile_remove_moves "iqm.iqm_client.transpile.transpile_remove_moves"), and then does the same as TRUST. This may produce a more optimized end result.

Inheritance

![Inheritance diagram of iqm.iqm_client.transpile.ExistingMoveHandlingOptions](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-efd680d97d0e4cef8dcdf771a366f569ae01f3c6.png)
