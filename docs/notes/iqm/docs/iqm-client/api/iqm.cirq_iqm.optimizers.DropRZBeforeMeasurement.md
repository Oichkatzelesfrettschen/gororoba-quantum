> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.optimizers.DropRZBeforeMeasurement.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.optimizers.DropRZBeforeMeasurement.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 66abf04cba33ea0d59bd332122beff332919f0aa12305d2659a4c88da72a67a4.

# DropRZBeforeMeasurement

Module: [`iqm.cirq_iqm.optimizers`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.optimizers.html#module-iqm.cirq_iqm.optimizers "iqm.cirq_iqm.optimizers")

*class* iqm.cirq_iqm.optimizers.DropRZBeforeMeasurement(*drop_final: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = False*)  
Bases: `PointOptimizer`

Drops z rotations that happen right before a z-basis measurement.

These z rotations do not affect the result of the measurement, so we may ignore them.

Parameters:  
**drop_final** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – iff True, drop also any z rotation at the end of the circuit (since it’s not followed by a measurement, it cannot affect them)

Methods

|  |  |
|----|----|
| [`optimization_at`](#iqm.cirq_iqm.optimizers.DropRZBeforeMeasurement.optimization_at "iqm.cirq_iqm.optimizers.DropRZBeforeMeasurement.optimization_at") | Describes how to change operations near the given location. |

optimization_at(*circuit: Circuit*, *index: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *op: Operation*) → PointOptimizationSummary \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")  
Describes how to change operations near the given location.

Parameters:  
- **circuit** (*Circuit*) – The circuit to improve.

- **index** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The index of the moment with the operation to focus on.

- **op** (*Operation*) – The operation to focus improvements upon.

Returns:  
A description of the optimization to perform, or else None if no change should be made.

Return type:  
*PointOptimizationSummary* \| None

Inheritance

![Inheritance diagram of iqm.cirq_iqm.optimizers.DropRZBeforeMeasurement](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-3b4668c370c8fb4d22e849218693f0f950017dfe.png)
