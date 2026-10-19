> Full piece: [https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.simplify_architecture.html](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.simplify_architecture.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 126be1a99fc4f134e0aed7157ff9b4d496310a1954694dd5f46e0fb6b5d9306d.

# iqm.iqm_client.transpile.simplify_architecture

iqm.iqm_client.transpile.simplify_architecture(*arch: DynamicQuantumArchitecture*, *\**, *remove_resonators: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)") = True*) → DynamicQuantumArchitecture  
Converts the given IQM Star quantum architecture into the equivalent simplified quantum architecture.

See [`iqm.iqm_client.transpile`](https://docs.iqm.tech/4.7/iqm-client/api/iqm.iqm_client.transpile.html#module-iqm.iqm_client.transpile "iqm.iqm_client.transpile") for the details.

Adds fictional gates, abstracts away their gate implementations. Returns `arch` itself if it does not contain computational resonators (in which case nothing will change).

Parameters:  
- **arch** (*DynamicQuantumArchitecture*) – quantum architecture to convert

- **remove_resonators** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – iff False, return the union of the simplified and real architectures

Returns:  
equivalent quantum architecture with fictional gates

Return type:  
*DynamicQuantumArchitecture*
