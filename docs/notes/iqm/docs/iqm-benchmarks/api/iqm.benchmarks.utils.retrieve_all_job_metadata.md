> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.retrieve_all_job_metadata.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.retrieve_all_job_metadata.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7f9ae52e553ee7df22d6c99b518e1d0de12d1e6ab5dc997f50ca0a228093c2ef.

# iqm.benchmarks.utils.retrieve_all_job_metadata

iqm.benchmarks.utils.retrieve_all_job_metadata(*iqm_jobs: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[JobV1\]*) → [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]\]  
Retrieve the metadata from a list of Job objects.

Uses `IQMJob.result()`, which waits for the job to finish before returning.

Parameters:  
**iqm_jobs** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[JobV1\]*) – The list of IQMJob objects.

Returns:  
Relevant metadata of all the IQMJob objects.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]\]
