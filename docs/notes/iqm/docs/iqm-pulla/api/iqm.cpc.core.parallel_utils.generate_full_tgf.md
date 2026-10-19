> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.parallel_utils.generate_full_tgf.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.parallel_utils.generate_full_tgf.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 5f639dbc71ad52d60597c8e897af96b81be11c3c6546ec39cd39d7441f1389c3.

# iqm.cpc.core.parallel_utils.generate_full_tgf

iqm.cpc.core.parallel_utils.generate_full_tgf(*group_circuit_function*, *sub_sig=None*)  
Generate a full circuit generation function from a group-wise circuit generation function.

In the returned function, `group_circuit_function` is applied to every parallel group (circuit locus) within every parallelly runnable partition of the QPU (e.g. a color group). The resulting TimeBoxes are then combined into a single composite TimeBox, one per partition, such that the TimeBox for each circuit locus is scheduled with ALAP logic.

Parameters:  
- **group_circuit_function** ([*SubTGF*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.parallel_utils.SubTGF.html#iqm.cpc.core.parallel_utils.SubTGF "iqm.cpc.core.parallel_utils.SubTGF")) – The group-wise sub circuit function that acts on a single parallelly runnable group.

- **sub_sig** ([*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")) – Optionally override the signature of the group_circuit_function with this signature (used for backwards compatibility features).

Returns:  
The full circuit generation function.

Return type:  
[*FullTGF*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.parallel_utils.FullTGF.html#iqm.cpc.core.parallel_utils.FullTGF "iqm.cpc.core.parallel_utils.FullTGF")
