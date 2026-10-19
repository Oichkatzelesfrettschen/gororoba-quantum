> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.timeit.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.utils.timeit.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f864dfa74e3eca6937cc5dab65873908b457d494a5475d3a2033c882c1e6aa3f.

# iqm.benchmarks.utils.timeit

iqm.benchmarks.utils.timeit(*f: [Callable](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")*) → [Callable](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")  
Decorator for calculating the amount of time a function takes to execute.

The decorated function returns a tuple where the first item is the original output, and the second item the execution time in seconds. Additionally, it will log the elapsed execution time on the DEBUG log level if it exceeds 1 second.

Parameters:  
**f** ([*Callable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")) – The function whose execution we wish to time.

Returns:  
Decorated function `f`.

Return type:  
[*Callable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")
