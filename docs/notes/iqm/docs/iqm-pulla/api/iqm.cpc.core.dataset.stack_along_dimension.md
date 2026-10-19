> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.stack_along_dimension.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.dataset.stack_along_dimension.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7069746d2b4b1143963d9aea347b545cecbd058b4e6086407d59f164bea6bc20.

# iqm.cpc.core.dataset.stack_along_dimension

iqm.cpc.core.dataset.stack_along_dimension(*data*, *dimension=None*, *stack='stack'*)  
Stack (that is, combine) all other dimensions other than the given dimension into a single dimension.

The new dimension contains all the elements of the cartesian product over the other dimensions.

With the groupby method, can be used to use functions which do not accept n-dimensional arrays, and repeat it over all other dimensions. Afterward, one should unstack the result to return to the original dimensionality.

Example: .. code:

```
data # has dimensions d1, d2, d3.
stacked = stack_along_dimension(data, "d1", "the others")
for prod_element, array in stacked.groupby("the others", squeeze=False):
    # `prod_element` is one of the element tuples of d2 x d3.
    # `do_math` operates on d1 and accepts `array` has only dims=(d1,):
    result = do_math(array)
```

Parameters:  
- **data** (*DataArray*) – Input data to combine the new dimension into

- **dimension** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* [*Sequence*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Sequence "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – The dimension string which will be stacked along; defaults to None

- **stack** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – Name of the stack to insert into the DataArray provided, defaults to ‘stack’

Return type:  
*DataArray*
