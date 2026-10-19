> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.optimizers.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.optimizers.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 933796d2c0241fb4ac41df1ad4de30dbb0b0375db887d33a92606f6983c33244.

# optimizers

Full path: iqm.cirq_iqm.optimizers

Circuit optimization classes.

Functions

|  |  |
|----|----|
| [`simplify_circuit`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.optimizers.simplify_circuit.html#iqm.cirq_iqm.optimizers.simplify_circuit "iqm.cirq_iqm.optimizers.simplify_circuit")(circuit, \*\[, ...\]) | Simplifies and optimizes the given circuit. |

Classes

|  |  |
|----|----|
| [`DropRZBeforeMeasurement`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.optimizers.DropRZBeforeMeasurement.html#iqm.cirq_iqm.optimizers.DropRZBeforeMeasurement "iqm.cirq_iqm.optimizers.DropRZBeforeMeasurement") | Drops z rotations that happen right before a z-basis measurement. |
| [`MergeOneParameterGroupGates`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.optimizers.MergeOneParameterGroupGates.html#iqm.cirq_iqm.optimizers.MergeOneParameterGroupGates "iqm.cirq_iqm.optimizers.MergeOneParameterGroupGates") | Merges adjacent gates belonging to the same parametrized gate family. |

Inheritance

![Inheritance diagram of iqm.cirq_iqm.optimizers](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-211a76168ca1132145cec8317ff7fbfc7079a334.png)
