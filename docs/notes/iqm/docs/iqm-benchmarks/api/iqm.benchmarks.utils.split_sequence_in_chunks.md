> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.split_sequence_in_chunks.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.split_sequence_in_chunks.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 e044ba90698c5f13e49eef8f1c5aad729c57b12b8acb6f64e39c797187245c30.

# iqm.benchmarks.utils.split_sequence_in_chunks

iqm.benchmarks.utils.split_sequence_in_chunks(*sequence_in: [Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]*, *split_size: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[Sequence](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]\]  
Split a given Sequence into chunks of a given split size, return as a List of Sequences.

Parameters:  
- **sequence_in** ([*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*) – The input list.

- **split_size** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The split size.

Returns:  
A List of Sequences.

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")\[[*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]\]
