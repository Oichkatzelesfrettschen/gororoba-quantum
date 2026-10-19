> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4b854d6b15b54acff383f8c400e4a26713e01284e83e322c088d3e4706ade6b5.

# routing

Full path: iqm.qrisp_iqm.passes.routing

Routing and placement passes.

This submodule contains passes for qubit layout and routing operations, including automatic placement algorithms (VF2++, SABRE) and manual layout options.

Subpackages and modules

|  |  |
|----|----|
| [`core`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.core.html#module-iqm.qrisp_iqm.passes.routing.core "iqm.qrisp_iqm.passes.routing.core") | Core routing algorithms and utilities. |
| [`plasma_layout`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.plasma_layout.html#module-iqm.qrisp_iqm.passes.routing.plasma_layout "iqm.qrisp_iqm.passes.routing.plasma_layout")(connectivity\[, effort, ...\]) | Create a layout pass that finds an initial qubit mapping. |
| [`plasma_route`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.plasma_route.html#module-iqm.qrisp_iqm.passes.routing.plasma_route "iqm.qrisp_iqm.passes.routing.plasma_route")(connectivity\[, effort, C, ...\]) | Create a pass that performs routing (SWAP insertion) on the existing layout. |
| [`vf2pp_layout`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.vf2pp_layout.html#module-iqm.qrisp_iqm.passes.routing.vf2pp_layout "iqm.qrisp_iqm.passes.routing.vf2pp_layout")(connectivity) | Create a pass that finds a qubit layout using VF2++ subgraph isomorphism. |
