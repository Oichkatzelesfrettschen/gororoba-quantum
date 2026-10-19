> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.layering_stages.CircuitLayer.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.layering_stages.CircuitLayer.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 8c3892db7713b0670f78dec2d624035203de566a7fe1a148043dd9492ef6869e.

# CircuitLayer

Module: [`iqm.cpc.compiler.layering_stages`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.layering_stages.html#module-iqm.cpc.compiler.layering_stages "iqm.cpc.compiler.layering_stages")

*class* iqm.cpc.compiler.layering_stages.CircuitLayer(*layer_type*, *locus_components*, *instructions=\<factory\>*, *transformations=\<factory\>*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Represents CircuitOperations in a Circuit that can be executed consequently (or in parallel).

Used to group together CircuitOperations that share a specific property.

Attributes

|  |  |
|----|----|
| [`layer_type`](#iqm.cpc.compiler.layering_stages.CircuitLayer.layer_type "iqm.cpc.compiler.layering_stages.CircuitLayer.layer_type") | Type of the layer, e.g. 'flux' or 'non-flux', shared between its member CircuitOperations. |
| [`locus_components`](#iqm.cpc.compiler.layering_stages.CircuitLayer.locus_components "iqm.cpc.compiler.layering_stages.CircuitLayer.locus_components") | Union of the loci of the CircuitOperations in this layer. |
| [`instructions`](#iqm.cpc.compiler.layering_stages.CircuitLayer.instructions "iqm.cpc.compiler.layering_stages.CircuitLayer.instructions") | ´.CircuitOperation\`\`. |
| [`transformations`](#iqm.cpc.compiler.layering_stages.CircuitLayer.transformations "iqm.cpc.compiler.layering_stages.CircuitLayer.transformations") | Transformation names to be applied for this layer when resolving it. |

Methods

|  |  |
|----|----|
| [`resolve`](#iqm.cpc.compiler.layering_stages.CircuitLayer.resolve "iqm.cpc.compiler.layering_stages.CircuitLayer.resolve") | Apply `self.transformations` to this layer and resolve it into a TimeBox. |

Parameters:  
- **layer_type** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **locus_components** ([*set*](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

- **instructions** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*CircuitOperation*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "(in iqm.pulse v15.0.0)")*\]*)

- **transformations** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]*)

layer_type*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Type of the layer, e.g. ‘flux’ or ‘non-flux’, shared between its member CircuitOperations.

locus_components*: [set](https://docs.python.org/3.11/library/stdtypes.html#set "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Union of the loci of the CircuitOperations in this layer.

instructions*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[CircuitOperation](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.CircuitOperation.html#iqm.pulse.builder.CircuitOperation "(in iqm.pulse v15.0.0)")\]*  
´.CircuitOperation\`\`. These should correspond to a transformation “gate” registered in `ScheduleBuilder`.

Type:  
Instruction (CircuitOperations) in this layer, ordered as in

Type:  
class

transformations*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]*  
Transformation names to be applied for this layer when resolving it.

resolve(*builder*)  
Apply `self.transformations` to this layer and resolve it into a TimeBox.

Parameters:  
**builder** ([*ScheduleBuilder*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.builder.ScheduleBuilder.html#iqm.pulse.builder.ScheduleBuilder "(in iqm.pulse v15.0.0)")) – The schedule builder.

Returns:  
The layer’s contents resolved into a TimeBox.

Return type:  
[*TimeBox*](https://docs.iqm.tech/4.7/iqm-pulse/api/iqm.pulse.timebox.TimeBox.html#iqm.pulse.timebox.TimeBox "(in iqm.pulse v15.0.0)")

.

Inheritance

![Inheritance diagram of iqm.cpc.compiler.layering_stages.CircuitLayer](https://docs.iqm.tech/4.7/iqm-pulla/_images/inheritance-3bd25b145a23719478fda2bd5e5a652c3ff45ad5.png)
