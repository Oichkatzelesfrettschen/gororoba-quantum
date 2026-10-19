> Full piece: [https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.conditional.CCPRX_Composite_DRAGCosineRiseFall.html](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.conditional.CCPRX_Composite_DRAGCosineRiseFall.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 85e48239a1b7d6f108fd2a56f35a640f6e66025d04d475ba96a5b6ef3df81066.

# CCPRX_Composite_DRAGCosineRiseFall

Module: [`iqm.pulse.gates.conditional`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.conditional.html#module-iqm.pulse.gates.conditional "iqm.pulse.gates.conditional")

*class* iqm.pulse.gates.conditional.CCPRX_Composite_DRAGCosineRiseFall(*parent*, *name*, *locus*, *calibration_data*, *builder*)  
Bases: [`CCPRX_Composite`](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.gates.conditional.CCPRX_Composite.html#iqm.pulse.gates.conditional.CCPRX_Composite "iqm.pulse.gates.conditional.CCPRX_Composite")

Conditional drag_crf pulse.

Attributes

|  |  |
|----|----|
| [`default_implementations`](#iqm.pulse.gates.conditional.CCPRX_Composite_DRAGCosineRiseFall.default_implementations "iqm.pulse.gates.conditional.CCPRX_Composite_DRAGCosineRiseFall.default_implementations") | Mapping from member operation names to the designated default implementation of that operation. |
| `id` | Unique str identifier, needed for certain caching properties. |
| `sub_implementations` | Single-component sub-implementations for factorizable gates with len(locus) \> 1, otherwise empty. |

Methods

Parameters:  
- **parent** ([*QuantumOp*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.quantum_ops.QuantumOp.html#iqm.pulse.quantum_ops.QuantumOp "iqm.pulse.quantum_ops.QuantumOp"))

- **name** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus** (*Locus*)

- **calibration_data** (*OILCalibrationData*)

- **builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "iqm.pulse.builder.ScheduleBuilder"))

default_implementations*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]* *= {'prx': 'drag_crf'}*  
Mapping from member operation names to the designated default implementation of that operation. Filling this attribute allows one to define a different default implementation from the common default in `builder.op_table` to be used in the context of this composite gate. If a member operation is not found in this dict as a key, the CompositeGate will use the common default as its default implementation.

Inheritance

![Inheritance diagram of iqm.pulse.gates.conditional.CCPRX_Composite_DRAGCosineRiseFall](https://docs.iqm.tech/4.7/iqm-pulse/_images/inheritance-cfaddeeb37040e11e753f3fdeb65ddb167b64460.png)
