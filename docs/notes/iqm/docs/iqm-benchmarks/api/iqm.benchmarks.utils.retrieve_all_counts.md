> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.retrieve_all_counts.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.retrieve_all_counts.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 689ab93c58dcad325adc713d6925484522f4da0b99ed85f8878d1a9785b5e3e4.

# iqm.benchmarks.utils.retrieve_all_counts

iqm.benchmarks.utils.retrieve_all_counts(*iqm_jobs: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[JobV1\]*, *identifier: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]  
Retrieve the counts from a list of IQMJob objects.

Parameters:  
- **iqm_jobs** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[JobV1\]*) – The list of IQMJob objects.

- **identifier** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – a string identifying the job.

Returns:  
The counts of all the IQMJob objects.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")\]\]
