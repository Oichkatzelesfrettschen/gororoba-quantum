> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.sweep.util.convert_sweeps_to_list_of_tuples.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.sweep.util.convert_sweeps_to_list_of_tuples.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 b3be7cde07867df014ec5a5b789ebae7f96aa8183e4d249f4fb33642412868bd.

# exa.common.sweep.util.convert_sweeps_to_list_of_tuples

convert_sweeps_to_list_of_tuples(*sweeps*)  
Validate sweeps and convert it to format accepted by the station control.

Converts a more lax sweep definition to a strict NdSweep. The sweeps themselves are the same, except single Sweep instances are turned into a ParallelSweep containing a single Sweep.

Verify that:

- `sweeps` elements are either Sweep or ParallelSweep

- ParallelSweep elements are Sweep

- ParallelSweep contains at least one element

- ParallelSweep component Sweeps all have equal-length data

Parameters:  
**sweeps** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*Sweep*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Sweep.html#exa.common.data.parameter.Sweep "exa.common.data.parameter.Sweep") *\|* [*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")*\[*[*Sweep*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Sweep.html#exa.common.data.parameter.Sweep "exa.common.data.parameter.Sweep")*,* *...\]\]*) – More user-friendly definition of a list of sweeps.

Returns:  
Converted `sweeps`.

Raises:  
[**ValidationError**](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.ValidationError.html#exa.common.errors.iqm_error.ValidationError "exa.common.errors.iqm_error.ValidationError") – `sweeps` does not follow the contract.

Return type:  
[*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*tuple*](https://docs.python.org/3.11/library/stdtypes.html#tuple "(in Python v3.11)")\[[*Sweep*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Sweep.html#exa.common.data.parameter.Sweep "exa.common.data.parameter.Sweep"), …\]\]
