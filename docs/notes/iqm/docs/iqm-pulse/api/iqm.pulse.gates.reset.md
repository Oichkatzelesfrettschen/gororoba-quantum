> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.reset.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.reset.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 76387fa347d973a78a857d07f62d077b54e95be6c8a11b5b336be8398476b9f5.

# reset

Full path: iqm.pulse.gates.reset

Qubit reset operations.

The reset operation is a non-unitary quantum channel that sets the state of a qubit to \\\|0\rangle\\.

Module Attributes

|  |  |
|----|----|
| [`RESET_MEASUREMENT_KEY`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.reset.RESET_MEASUREMENT_KEY.html#iqm.pulse.gates.reset.RESET_MEASUREMENT_KEY "iqm.pulse.gates.reset.RESET_MEASUREMENT_KEY") | Constant measurement key for the measure operation required in the fast-feedback reset gate (the double underscore emphasizes the fact that this label should not be manually used in fast feedback). |
| [`RESET_FEEDBACK_KEY`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.reset.RESET_FEEDBACK_KEY.html#iqm.pulse.gates.reset.RESET_FEEDBACK_KEY "iqm.pulse.gates.reset.RESET_FEEDBACK_KEY") | The feedback key used in fast-feedback reset gate (the double underscore emphasizes the fact that this label should not be manually used in fast feedback). |

Classes

|  |  |
|----|----|
| [`Reset_Conditional`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.reset.Reset_Conditional.html#iqm.pulse.gates.reset.Reset_Conditional "iqm.pulse.gates.reset.Reset_Conditional") | Conditional reset operation. |
| [`Reset_F0G1`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.reset.Reset_F0G1.html#iqm.pulse.gates.reset.Reset_F0G1 "iqm.pulse.gates.reset.Reset_F0G1") | Reset by driving the \\\|f0\rangle \leftrightarrow \|g1\rangle\\ transition. |
| [`Reset_F0G1_Composite`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.reset.Reset_F0G1_Composite.html#iqm.pulse.gates.reset.Reset_F0G1_Composite "iqm.pulse.gates.reset.Reset_F0G1_Composite") | Reset by applying a `prx_12(pi)` gate followed by the `lru.f0g1` operation. |
| [`Reset_Wait`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.reset.Reset_Wait.html#iqm.pulse.gates.reset.Reset_Wait "iqm.pulse.gates.reset.Reset_Wait") | Reset operation by relaxation (idling for a time comparable to the relaxation time of the component). |

Inheritance

![Inheritance diagram of iqm.pulse.gates.reset](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-13a7b012829394677a001e620f3b9665f3bc0cc6.png)
