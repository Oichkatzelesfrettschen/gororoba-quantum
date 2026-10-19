> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.optimizers.MergeOneParameterGroupGates.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.optimizers.MergeOneParameterGroupGates.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1c7b5788497840e4c0908a396a754b290ecc4f685630aacec2ba2e578975e48c.

# MergeOneParameterGroupGates

Module: [`iqm.cirq_iqm.optimizers`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.optimizers.html#module-iqm.cirq_iqm.optimizers "iqm.cirq_iqm.optimizers")

*class* iqm.cirq_iqm.optimizers.MergeOneParameterGroupGates(*post_clean_up: Callable\[\[Sequence\[cirq.Operation\]\], cirq.OP_TREE\] = \<function PointOptimizer.\<lambda\>\>*)  
Bases: `PointOptimizer`

Merges adjacent gates belonging to the same parametrized gate family.

The merged gates have to act on the same sequence of qubits. This optimizer only works with gate families that are known to be one-parameter groups.

For now, all the families are assumed to be periodic with a period of 4.

Attributes

|                          |     |
|--------------------------|-----|
| `GATE_MERGING_TOLERANCE` |     |
| `ONE_PARAMETER_FAMILIES` |     |
| `PERIOD`                 |     |

Methods

|  |  |
|----|----|
| [`optimization_at`](#iqm.cirq_iqm.optimizers.MergeOneParameterGroupGates.optimization_at "iqm.cirq_iqm.optimizers.MergeOneParameterGroupGates.optimization_at") | Describes how to change operations near the given location. |

Parameters:  
**post_clean_up** (*Callable\[\[Sequence\[cirq.Operation\]\],* *cirq.OP_TREE\]*)

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

![Inheritance diagram of iqm.cirq_iqm.optimizers.MergeOneParameterGroupGates](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-1eed24cfb2492b802b23e2be9dcbf22b1f1d3c37.png)
