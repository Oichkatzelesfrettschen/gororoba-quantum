> Full piece: [https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.reporting.generate_basis_labels.html](https://docs.iqm.tech/4.7/iqm-benchmarks/api/iqm.benchmarks.compressive_gst.mgst.reporting.reporting.generate_basis_labels.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d83f09a93f51e466dd7582e8460ee37f6d11bb573931664320301b7bd5b8904a.

# iqm.benchmarks.compressive_gst.mgst.reporting.reporting.generate_basis_labels

iqm.benchmarks.compressive_gst.mgst.reporting.reporting.generate_basis_labels(*pdim: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*, *basis: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)") = None*) → [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]  
Generate a list of labels for the Pauli basis or the standard basis.

Parameters:  
- **pdim** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")) – Physical dimension

- **basis** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None*) – Which basis the labels correspond to, currently default is standard basis and “Pauli” can be chosen for Pauli basis labels like “II”, “IX”, “XX”, …

Returns:  
A list of all string combinations for the given dimension and basis

Return type:  
[list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]
