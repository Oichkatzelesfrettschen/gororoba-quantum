> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_metric.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_metric.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 8d2f986cedee7b72c26ce8bd4b46606c83bfa0747d9e18fcee523c654cda40d9.

# sabre_metric

Full path: iqm.qrisp_iqm.passes.routing.core.sabre_metric

Contains the code for efficiently computing the SABRE metric.

The metric computed here deviates from the original paper in some ways:

1.  The extended set are ALL remaining instructions that are not in the front layer.

2.  The instructions from the extended set are weighted with a decay mechanism depending on how many layers they are away from the front layer. If an instruction is in layer d (the front layer has d = 1), the weight is exp(-(d-2)/\_DECAY_FACTOR).

3.  The distance measure in the metric is taken to the power of 1.1. This has the effect that a pair of qubits that is already close together induces a stronger cost reduction if they are moved even closer compared to a pair that is far away. This is important because the instruction DAG is based on the Permeability DAG, which implies that the front-layer can contain instructions on the same qubit twice. This could yield the situation that the algorithm tries to move the qubit back and forth in order to improve the metric via either one or the other instruction.

For computing the metric, there are two implementations:

1.  [`compute_sabre_cost()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_sabre_cost.html#iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_sabre_cost "iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_sabre_cost") straight up computes the cost function

2.  [`compute_sabre_cost_change()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_sabre_cost_change.html#iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_sabre_cost_change "iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_sabre_cost_change") computes the cost change induced by a given SWAP more efficiently by only involving the instructions that actually contribute to the cost.

Functions

|  |  |
|----|----|
| [`compute_depth_array`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_depth_array.html#iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_depth_array "iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_depth_array")(front_layer_indices, ...) | Precompute the depth array. |
| [`compute_extended_set_prefactor`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_extended_set_prefactor.html#iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_extended_set_prefactor "iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_extended_set_prefactor")(extended_set, ...) | Precompute the prefactor of the extended set. |
| [`compute_front_layer_prefactor`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_front_layer_prefactor.html#iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_front_layer_prefactor "iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_front_layer_prefactor")(...) | Precompute the prefactor of the front layer. |
| [`compute_sabre_cost`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_sabre_cost.html#iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_sabre_cost "iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_sabre_cost")(topology, ...) | Computes the SABRE metric with the modifications mentioned in the preamble. |
| [`compute_sabre_cost_change`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_sabre_cost_change.html#iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_sabre_cost_change "iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_sabre_cost_change")(instruction_data, ...) | Compute the cost change induced by a given swap. |
| [`compute_sabre_cost_from_dag`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_sabre_cost_from_dag.html#iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_sabre_cost_from_dag "iqm.qrisp_iqm.passes.routing.core.sabre_metric.compute_sabre_cost_from_dag")(topology, ...) | Compute the SABRE cost from a given instruction DAG. |
| [`filter_involvement_list`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_metric.filter_involvement_list.html#iqm.qrisp_iqm.passes.routing.core.sabre_metric.filter_involvement_list "iqm.qrisp_iqm.passes.routing.core.sabre_metric.filter_involvement_list")(involvement_list, ...) | Produce a filtered copy of an involvement list. |
| [`find_involvement`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_metric.find_involvement.html#iqm.qrisp_iqm.passes.routing.core.sabre_metric.find_involvement "iqm.qrisp_iqm.passes.routing.core.sabre_metric.find_involvement")(instruction_data, ...) | Determine involvement lists for SABRE cost-change computation. |
| [`precompute_exp_depth`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.sabre_metric.precompute_exp_depth.html#iqm.qrisp_iqm.passes.routing.core.sabre_metric.precompute_exp_depth "iqm.qrisp_iqm.passes.routing.core.sabre_metric.precompute_exp_depth")(depth_array) | Precompute the decay factor from the depth array. |
