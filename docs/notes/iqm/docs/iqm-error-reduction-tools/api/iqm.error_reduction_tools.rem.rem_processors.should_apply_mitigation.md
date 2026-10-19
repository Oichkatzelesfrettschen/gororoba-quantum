> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_processors.should_apply_mitigation.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.rem.rem_processors.should_apply_mitigation.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4a7083bb607da4393256135e5b520933b9f308466ddf3f8c3fbf543327798f0c.

# iqm.error_reduction_tools.rem.rem_processors.should_apply_mitigation

iqm.error_reduction_tools.rem.rem_processors.should_apply_mitigation(*counts*, *max_entropy=28.0*, *force_mitigation=False*)  
Determine whether to apply mitigation based on distribution entropy.

Parameters:  
- **counts** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*\]*) – Dictionary mapping bitstrings to their measured counts.

- **max_entropy** ([*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")) – Maximum allowed Shannon entropy (in bits) of the counts distribution. Distributions with entropy above this threshold are considered too expensive to mitigate.

- **force_mitigation** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If True, always apply mitigation regardless of entropy.

Returns:  
Whether we should mitigate, estimated entropy of `counts`.

Return type:  
[tuple](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"), [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]
