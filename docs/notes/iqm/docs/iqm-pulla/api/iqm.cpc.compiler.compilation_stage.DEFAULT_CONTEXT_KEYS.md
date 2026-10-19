> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.DEFAULT_CONTEXT_KEYS.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.compilation_stage.DEFAULT_CONTEXT_KEYS.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b26872b1b2e1904f86563208ffbf7ac3b61cd6f9a1acaf7f6f5b8b2a1ee1c5a0.

# DEFAULT_CONTEXT_KEYS

iqm.cpc.compiler.compilation_stage.DEFAULT_CONTEXT_KEYS *= \['dut_label', 'components', 'timebox_input', 'builder', 'settings', 'component_mapping', 'chip_topology', 'circuit_metrics', 'mapped_readout_keys', 'readout_metrics', 'software_version_set_id', 'soft_sweeps', 'hard_sweeps'\]*  
Keys that always exist in the Compiler context. These keys can exist as compiler pass args. Any other contents of the context must be referenced through the context (i.e. having context as a pass function argument).
