> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.iqm_sampler.IQMResult.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.iqm_sampler.IQMResult.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 67cad4d0df08b50216c393236e473b4af45100b9b74b27c11691728f05585242.

# IQMResult

Module: [`iqm.cirq_iqm.iqm_sampler`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.iqm_sampler.html#module-iqm.cirq_iqm.iqm_sampler "iqm.cirq_iqm.iqm_sampler")

*class* iqm.cirq_iqm.iqm_sampler.IQMResult(*\**, *params: ParamResolver \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *measurements: [Mapping](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Mapping "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *records: [Mapping](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Mapping "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [ndarray](https://numpy.org/doc/stable/reference/generated/numpy.ndarray.html#numpy.ndarray "(in NumPy v2.5)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*, *metadata: [ResultMetadata](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.iqm_sampler.ResultMetadata.html#iqm.cirq_iqm.iqm_sampler.ResultMetadata "iqm.cirq_iqm.iqm_sampler.ResultMetadata")*)  
Bases: `ResultDict`

Stores the results of a quantum circuit execution on an IQM device.

Parameters:  
- **params** (*cirq.ParamResolver* *\|* *None*) – Parameter resolver used for this circuit, if any.

- **measurements** (*Mapping\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *np.ndarray\]* *\|* *None*) – Maps measurement keys to measurement results, which are 2-D arrays of dtype bool. shape == (repetitions, qubits).

- **records** (*Mapping\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *np.ndarray\]* *\|* *None*) – Maps measurement keys to measurement results, which are 3D arrays of dtype bool. shape == (repetitions, instances, qubits).

- **metadata** ([*ResultMetadata*](https://docs.iqm.tech/4.7/iqm-client/api/iqm.cirq_iqm.iqm_sampler.ResultMetadata.html#iqm.cirq_iqm.iqm_sampler.ResultMetadata "iqm.cirq_iqm.iqm_sampler.ResultMetadata")) – Metadata for the circuit execution results.

Attributes

Methods

Inheritance

![Inheritance diagram of iqm.cirq_iqm.iqm_sampler.IQMResult](https://docs.iqm.tech/4.7/iqm-client/_images/inheritance-7e8a63adeb44bbccdc70426e373a693dc3c851a1.png)
