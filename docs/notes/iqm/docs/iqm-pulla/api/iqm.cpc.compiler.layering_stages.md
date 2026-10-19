> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.layering_stages.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.layering_stages.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 8047f4421cf79abac8bff0920c0f75b5dc61b9ba9e4592b727ab3eb9d2b16cbc.

# layering_stages

Full path: iqm.cpc.compiler.layering_stages

Compiler stages and passes for layering quantum circuits and applying transformations on the layers.

Functions

|  |  |
|----|----|
| [`layer_circuits`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.layering_stages.layer_circuits.html#iqm.cpc.compiler.layering_stages.layer_circuits "iqm.cpc.compiler.layering_stages.layer_circuits")(circuits, components\[, ...\]) | Layer circuits into flux and non-flux layers. |
| [`layer_schedules`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.layering_stages.layer_schedules.html#iqm.cpc.compiler.layering_stages.layer_schedules "iqm.cpc.compiler.layering_stages.layer_schedules")(schedules, builder, components) | Extract flux and non-flux layers from the full schedule and apply the prescribed transformations to them. |
| [`resolve_layers`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.layering_stages.resolve_layers.html#iqm.cpc.compiler.layering_stages.resolve_layers "iqm.cpc.compiler.layering_stages.resolve_layers")(circuits, components, builder) | Resolve the layered circuits into TimeBoxes, while applying the prescribed transformations. |
| [`set_layer_transformations`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.layering_stages.set_layer_transformations.html#iqm.cpc.compiler.layering_stages.set_layer_transformations "iqm.cpc.compiler.layering_stages.set_layer_transformations")(circuits\[, ...\]) | Set layer transformations for the layered circuits. |

Classes

|  |  |
|----|----|
| [`CircuitLayer`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.layering_stages.CircuitLayer.html#iqm.cpc.compiler.layering_stages.CircuitLayer "iqm.cpc.compiler.layering_stages.CircuitLayer") | Represents CircuitOperations in a Circuit that can be executed consequently (or in parallel). |

Inheritance

![Inheritance diagram of iqm.cpc.compiler.layering_stages](https://docs.iqm.tech/4.7/iqm-pulla/_images/inheritance-4746cf0e9ee7bb8ee1379fe022379aca9a6f4a26.png)
