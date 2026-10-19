> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a88a0e5bbbde960d065ff6b765874865dd16615ec571ff8ccae4859ca7319435.

# passes

Full path: iqm.qrisp_iqm.passes

Transpilation passes for IQM-targeted circuit compilation.

Provides a composable `PassManager`-based transpilation pipeline with:

**Default pipeline**

- `create_iqm_pass_manager()` — factory for the complete plasma-sabre pipeline.

- `transpile_to_iqm()` — one-liner convenience wrapper.

**Individual passes**

- Layout: `plasma_layout()`, `vf2pp_layout()`

- Routing: `plasma_route()`

- Optimisation: [`commute_phases()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.commute_phases.html#module-iqm.qrisp_iqm.passes.commute_phases "iqm.qrisp_iqm.passes.commute_phases"), [`measurement_parallelization()`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.measurement_parallelization.html#module-iqm.qrisp_iqm.passes.measurement_parallelization "iqm.qrisp_iqm.passes.measurement_parallelization")

Subpackages and modules

|  |  |
|----|----|
| [`commute_phases`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.commute_phases.html#module-iqm.qrisp_iqm.passes.commute_phases "iqm.qrisp_iqm.passes.commute_phases")(\[preserve_unitary\]) | Create a pass that optimizes U3 gates by commuting phase information past SWAP gates. |
| [`default_pass_manager`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.default_pass_manager.html#module-iqm.qrisp_iqm.passes.default_pass_manager "iqm.qrisp_iqm.passes.default_pass_manager") | Default plasma-sabre PassManager for IQM-targeted transpilation. |
| [`measurement_parallelization`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.measurement_parallelization.html#module-iqm.qrisp_iqm.passes.measurement_parallelization "iqm.qrisp_iqm.passes.measurement_parallelization") | Combine consecutive measurements into single multi-qubit measurements. |
| [`routing`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.qrisp_iqm.passes.routing.html#module-iqm.qrisp_iqm.passes.routing "iqm.qrisp_iqm.passes.routing") | Routing and placement passes. |
