> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.sweep.util.linear_index_sweep.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.sweep.util.linear_index_sweep.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 97682180d5195e0eaa37fab6739c161c2177aa76bcad7475e5b47c47dd2aae24.

# exa.common.sweep.util.linear_index_sweep

linear_index_sweep(*parameter*, *length*)  
Produce an NdSweep over a dummy index.

Can be used in places where a “hardware sweep” is needed but not really meaningful.

Parameters:  
- **parameter** ([*Parameter*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Parameter.html#exa.common.data.parameter.Parameter "exa.common.data.parameter.Parameter")) – Data parameter this index is for.

- **length** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Number of integers in the dummy sweep.

Returns:  
Linear sweep over a parameter whose name is `parameter.name + _index` and whose data ranges from 0 to `length - 1` with steps of 1.

Return type:  
[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*Sweep*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Sweep.html#exa.common.data.parameter.Sweep "exa.common.data.parameter.Sweep"), …\]\]
