> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.create_ragged_data_index.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.compiler.post_process.create_ragged_data_index.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 3b40cb46e4bb9adbbf9e45dfc26d753efdabd2ef7512b2ca6b8697f37b56b84c.

# iqm.cpc.compiler.post_process.create_ragged_data_index

iqm.cpc.compiler.post_process.create_ragged_data_index(*run*)  
Adds `MultiIndex` to the trigger index dimension for accessing ragged data via the hard sweep values.

If there is a non-uniform number of readout triggers for n RO label across the segments of the playlist, the data cannot be reshaped into an N-dimensional box with the dims `(<hard sweep dimension 0>, <hard sweep dimension 1>, ...)`. The data is then “ragged” and the only meaningful way to index the data is along the readout trigger index dimension. In order to be able to use this ragged data meaningfully, the user often wants access it via the known dimensions of the experiment run, i.e. the sweeps. For this reason we attach the values the hard sweeps took in each segment where a trigger happened to the trigger index dimension.

An example: the playlist was generated from hard sweeps (there are no soft sweeps here): `[Sweep(parameter=param1, data=[0, 1]), Sweep(parameter=param2, data=[0.1, 0.2, 0.3])]`, which means there are 2 \* 3 = 6 segments. Let’s say for a given RO label `"QB1__key"` we have 1 RO trigger in the first segment, 1 trigger in the third, and 2 in the final one (the rest have no triggers for this label). Thus, the returned data has the length 4, i.e. the trigger index goes from 0 to 3. Taking into account the convention in ordering sweep dimensions, the values of the sweeps for these trigger indices are then:

0 =\> `(param2 = 0.1, param1 = 0)` (in the 1st segment, both params assume their first values) 1 =\> `(param2 = 0.3, param1 = 0)` (in the 3rd segment param2 has its 3rd value, while param1 is still in its 1st) 2 =\> `(param2 = 0.3, param1 = 1)` (in the last segment, both params have their final values) 3 =\> `(param2 = 0.3, param1 = 1)` (there were 2 triggers in the last segment, so this has the same values as 2.)

The `MultiIndex` allows then the data via the hard sweep values: `exp.last_run["<my label>_readout].sel({QB1::param1: 0})` gives the slice where `param1 == 0`

Parameters:  
**run** ([*RunResult*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.run_result.RunResult.html#iqm.cpc.core.run_result.RunResult "iqm.cpc.core.run_result.RunResult")) – The run result.

Returns:  
The RunResult with the ragged data variables now indexed.

Return type:  
[*RunResult*](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.run_result.RunResult.html#iqm.cpc.core.run_result.RunResult "iqm.cpc.core.run_result.RunResult")
