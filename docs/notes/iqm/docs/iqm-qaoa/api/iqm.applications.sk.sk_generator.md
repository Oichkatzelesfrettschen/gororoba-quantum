> Full piece: [https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.sk.sk_generator.html](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.sk.sk_generator.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 467f12ce7327e67f06c42bf82387244b06b8d28672879455f907488c7122de1d.

# sk_generator

iqm.applications.sk.sk_generator(*n*, *n_instances*, *distribution='gaussian'*, *seed=None*)[\[source\]](https://github.com/iqm-finland/sdk/blob/main/iqm_qaoa/src/iqm/applications/sk.py#L58-L93)  
The generator function for generating random SK model problem instances.

The generator yields [`SherringtonKirkpatrick`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.sk.SherringtonKirkpatrick.html#iqm.applications.sk.SherringtonKirkpatrick "iqm.applications.sk.SherringtonKirkpatrick") model problem instances using random `interaction_matrix`, created according to the input parameters.

- ‘gaussian’ -\> Gaussian distribution with mean 0 and standard deviation 1.

- ‘rademacher’ -\> Value +1 with probability 0.5 and value -1 with probability 0.5.

- ‘uniform’ -\> Uniform distribution between 0 and 1.

Parameters:  
- **n** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of qubits in the problem instance, also the `intraction_matrix` dimensions.

- **n_instances** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – The number of SK model instances to generate.

- **distribution** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – A string describing the distribution of the elements in the `interaction_matrix`. Possible distributions include ‘gaussian’ (also known as ‘normal’), ‘rademacher’ and ‘uniform’.

- **seed** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None* *\|* [*Generator*](https://numpy.org/doc/stable/reference/random/generator.html#numpy.random.Generator "(in NumPy v2.5)")) – Optional random seed for generating the problem instances.

Returns:  
An iterator of [`SherringtonKirkpatrick`](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.sk.SherringtonKirkpatrick.html#iqm.applications.sk.SherringtonKirkpatrick "iqm.applications.sk.SherringtonKirkpatrick") objects, corresponding to randomly-generated instances of the model.

Return type:  
[*Iterator*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Iterator "(in Python v3.11)")\[[*SherringtonKirkpatrick*](https://docs.iqm.tech/4.7/iqm-qaoa/api/iqm.applications.sk.SherringtonKirkpatrick.html#iqm.applications.sk.SherringtonKirkpatrick "iqm.applications.sk.SherringtonKirkpatrick")\]
