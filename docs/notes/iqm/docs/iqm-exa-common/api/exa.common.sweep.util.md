> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.sweep.util.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.sweep.util.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e857e6f55f886684eae7b5a84518681d37d5a522514c82b334ae787ba65875e2.

# util

Full path: exa.common.sweep.util

Generic utilities for converting sweep definitions from user-friendly format to canonic ones.

Module Attributes

|  |  |
|----|----|
| [`ParallelSweep`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.sweep.util.ParallelSweep.html#exa.common.sweep.util.ParallelSweep "exa.common.sweep.util.ParallelSweep") | One or more single-parameter sweeps executed in parallel, like the Python zip. |
| [`NdSweep`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.sweep.util.NdSweep.html#exa.common.sweep.util.NdSweep "exa.common.sweep.util.NdSweep") | Cartesian product of N ParallelSweeps. |
| [`Sweeps`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.sweep.util.Sweeps.html#exa.common.sweep.util.Sweeps "exa.common.sweep.util.Sweeps") | List of single or parallel Sweeps. |

Functions

|  |  |
|----|----|
| [`convert_sweeps_to_list_of_tuples`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.sweep.util.convert_sweeps_to_list_of_tuples.html#exa.common.sweep.util.convert_sweeps_to_list_of_tuples "exa.common.sweep.util.convert_sweeps_to_list_of_tuples")(sweeps) | Validate sweeps and convert it to format accepted by the station control. |
| [`linear_index_sweep`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.sweep.util.linear_index_sweep.html#exa.common.sweep.util.linear_index_sweep "exa.common.sweep.util.linear_index_sweep")(parameter, length) | Produce an NdSweep over a dummy index. |
