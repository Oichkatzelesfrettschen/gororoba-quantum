> Full piece: [https://docs.openquantum.com/qiskit-plugin/sampler-estimator/](https://docs.openquantum.com/qiskit-plugin/sampler-estimator/)
> Retrieved 2026-10-17T05:09Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1438e8ce041a9086f88979fdaca5dbfec138d4dd561b354f6a9277d4d8624c5b.

# Sampler & Estimator

The Qiskit plugin provides `OQSampler` (SamplerV2) and `OQEstimator` (EstimatorV2) primitives that submit circuits to Open Quantum for execution.

## OQSampler (SamplerV2)

`OQSampler` implements Qiskit's `BaseSamplerV2` interface. It submits circuits to Open Quantum and returns measurement results as `BitArray` objects.

### Creating a Sampler

Use `service.create_sampler()`:

[](#__codelineno-0-1)`from`` ``openquantum_sdk.auth`` ``import`` ``ClientCredentials`\
[](#__codelineno-0-2)`from`` ``openquantum_sdk_qiskit`` ``import`` ``OpenQuantumService`\
[](#__codelineno-0-3)\
[](#__codelineno-0-4)`service`` ``=`` ``OpenQuantumService``(`\
[](#__codelineno-0-5)`    ``creds``=``ClientCredentials``(`\
[](#__codelineno-0-6)`        ``client_id``=``"s_your_client_id"``,`\
[](#__codelineno-0-7)`        ``client_secret``=``"your_client_secret"``,`\
[](#__codelineno-0-8)`    ``),`\
[](#__codelineno-0-9)`)`\
[](#__codelineno-0-10)\
[](#__codelineno-0-11)`backend`` ``=`` ``service``.``return_backend``(``"rigetti:cepheus-1-108q"``)`\
[](#__codelineno-0-12)\
[](#__codelineno-0-13)`sampler`` ``=`` ``service``.``create_sampler``(`\
[](#__codelineno-0-14)`    ``backend``=``backend``,`\
[](#__codelineno-0-15)`    ``job_subcategory_id``=``"phys:oth"``,``  ``# Physics`\
[](#__codelineno-0-16)`    ``verbose``=``False``,``                  ``# default; True prints progress and credit cost`\
[](#__codelineno-0-17)`    ``job_timeout_seconds``=``86400``,``      ``# default, one day`\
[](#__codelineno-0-18)`)`\

`verbose` and `job_timeout_seconds` are the same on every Open Quantum plugin. Both default as above. Omit them to inherit the values already set on the backend from `return_backend`. `create_estimator` accepts the same two arguments. `backend.run(..., verbose=, job_timeout_seconds=)` overrides them for one submission.

### Running the Sampler

[](#__codelineno-1-1)`from`` ``qiskit.circuit`` ``import`` ``QuantumCircuit`\
[](#__codelineno-1-2)\
[](#__codelineno-1-3)`qc`` ``=`` ``QuantumCircuit``(``2``,`` ``2``)`\
[](#__codelineno-1-4)`qc``.``h``(``0``)`\
[](#__codelineno-1-5)`qc``.``cx``(``0``,`` ``1``)`\
[](#__codelineno-1-6)`qc``.``measure``([``0``,`` ``1``],`` ``[``0``,`` ``1``])`\
[](#__codelineno-1-7)\
[](#__codelineno-1-8)`job`` ``=`` ``sampler``.``run``([``qc``],`` ``shots``=``128``)`\
[](#__codelineno-1-9)`result`` ``=`` ``job``.``result``()`\
[](#__codelineno-1-10)\
[](#__codelineno-1-11)`# Access the first pub result`\
[](#__codelineno-1-12)`pub_result`` ``=`` ``result``[``0``]`\
[](#__codelineno-1-13)`bit_array`` ``=`` ``pub_result``.``data``.``meas`\
[](#__codelineno-1-14)`counts`` ``=`` ``bit_array``.``get_counts``()`\
[](#__codelineno-1-15)`print``(``counts``)`\

Expected output:

[](#__codelineno-2-1)`{``'00'``:`` ``507``,`` ``'11'``:`` ``517``}`\

### Shots Configuration

Specify shots per run:

[](#__codelineno-3-1)`job`` ``=`` ``sampler``.``run``([``qc``],`` ``shots``=``4096``)`\

If `shots` is not specified, it defaults to 100.

### Parameter Binding

The sampler supports parameterized circuits with automatic binding:

[](#__codelineno-4-1)`from`` ``qiskit.circuit`` ``import`` ``QuantumCircuit``,`` ``Parameter`\
[](#__codelineno-4-2)\
[](#__codelineno-4-3)`theta`` ``=`` ``Parameter``(``"theta"``)`\
[](#__codelineno-4-4)\
[](#__codelineno-4-5)`qc`` ``=`` ``QuantumCircuit``(``1``,`` ``1``)`\
[](#__codelineno-4-6)`qc``.``rx``(``theta``,`` ``0``)`\
[](#__codelineno-4-7)`qc``.``measure``(``0``,`` ``0``)`\
[](#__codelineno-4-8)\
[](#__codelineno-4-9)`# Single parameter value`\
[](#__codelineno-4-10)`job`` ``=`` ``sampler``.``run``([(``qc``,`` ``[``0.5``])],`` ``shots``=``128``)`\
[](#__codelineno-4-11)\
[](#__codelineno-4-12)`# Multiple parameter values`\
[](#__codelineno-4-13)`import`` ``numpy`` ``as`` ``np`\
[](#__codelineno-4-14)`values`` ``=`` ``np``.``linspace``(``0``,`` ``np``.``pi``,`` ``5``)`\
[](#__codelineno-4-15)`job`` ``=`` ``sampler``.``run``([(``qc``,`` ``values``.``reshape``(``-``1``,`` ``1``))],`` ``shots``=``128``)`\

### Export Format

Control the QASM export format:

[](#__codelineno-5-1)`# Use OpenQASM 2 instead of the default OpenQASM 3`\
[](#__codelineno-5-2)`job`` ``=`` ``sampler``.``run``([``qc``],`` ``shots``=``128``,`` ``export_format``=``"qasm2"``)`\

## OQEstimator (EstimatorV2)

`OQEstimator` implements Qiskit's `BaseEstimatorV2` interface. It computes expectation values of observables by delegating to Qiskit's `BackendEstimatorV2` with an Open Quantum backend.

### Creating an Estimator

[](#__codelineno-6-1)`estimator`` ``=`` ``service``.``create_estimator``(`\
[](#__codelineno-6-2)`    ``backend``=``backend``,`\
[](#__codelineno-6-3)`    ``job_subcategory_id``=``"phys:oth"``,``  ``# Physics`\
[](#__codelineno-6-4)`)`\

### Running the Estimator

[](#__codelineno-7-1)`from`` ``qiskit.circuit`` ``import`` ``QuantumCircuit`\
[](#__codelineno-7-2)`from`` ``qiskit.quantum_info`` ``import`` ``SparsePauliOp`\
[](#__codelineno-7-3)\
[](#__codelineno-7-4)`qc`` ``=`` ``QuantumCircuit``(``2``)`\
[](#__codelineno-7-5)`qc``.``h``(``0``)`\
[](#__codelineno-7-6)`qc``.``cx``(``0``,`` ``1``)`\
[](#__codelineno-7-7)\
[](#__codelineno-7-8)`observable`` ``=`` ``SparsePauliOp``(``"ZZ"``)`\
[](#__codelineno-7-9)\
[](#__codelineno-7-10)`job`` ``=`` ``estimator``.``run``([(``qc``,`` ``observable``)],`` ``precision``=``0.01``)`\
[](#__codelineno-7-11)`result`` ``=`` ``job``.``result``()`\
[](#__codelineno-7-12)\
[](#__codelineno-7-13)`print``(``f``"Expectation value: ``{``result``[``0``]``.``data``.``evs``}``"``)`\

### Precision

The `precision` parameter controls the target precision for the expectation value estimate:

[](#__codelineno-8-1)`# Higher precision (more shots internally)`\
[](#__codelineno-8-2)`job`` ``=`` ``estimator``.``run``([(``qc``,`` ``observable``)],`` ``precision``=``0.001``)`\
[](#__codelineno-8-3)\
[](#__codelineno-8-4)`# Lower precision (fewer shots, faster)`\
[](#__codelineno-8-5)`job`` ``=`` ``estimator``.``run``([(``qc``,`` ``observable``)],`` ``precision``=``0.1``)`\

### Multiple Observables

[](#__codelineno-9-1)`obs_zz`` ``=`` ``SparsePauliOp``(``"ZZ"``)`\
[](#__codelineno-9-2)`obs_xx`` ``=`` ``SparsePauliOp``(``"XX"``)`\
[](#__codelineno-9-3)\
[](#__codelineno-9-4)`job`` ``=`` ``estimator``.``run``([`\
[](#__codelineno-9-5)`    ``(``qc``,`` ``obs_zz``),`\
[](#__codelineno-9-6)`    ``(``qc``,`` ``obs_xx``),`\
[](#__codelineno-9-7)`])`\
[](#__codelineno-9-8)`result`` ``=`` ``job``.``result``()`\
[](#__codelineno-9-9)\
[](#__codelineno-9-10)`print``(``f``"<ZZ> = ``{``result``[``0``]``.``data``.``evs``}``"``)`\
[](#__codelineno-9-11)`print``(``f``"<XX> = ``{``result``[``1``]``.``data``.``evs``}``"``)`\

## Direct Construction

You can also construct the primitives directly without `service.create_sampler()` or `service.create_estimator()`:

[](#__codelineno-10-1)`from`` ``openquantum_sdk_qiskit`` ``import`` ``OQSampler``,`` ``OQEstimator`\
[](#__codelineno-10-2)\
[](#__codelineno-10-3)`sampler`` ``=`` ``OQSampler``(`\
[](#__codelineno-10-4)`    ``backend``=``backend``,`\
[](#__codelineno-10-5)`    ``scheduler``=``service``.``scheduler``,`\
[](#__codelineno-10-6)`    ``config``=``{`\
[](#__codelineno-10-7)`        ``"backend_class_id"``:`` ``"rigetti:cepheus-1-108q"``,`\
[](#__codelineno-10-8)`        ``"job_subcategory_id"``:`` ``"phys:oth"``,``  ``# Physics`\
[](#__codelineno-10-9)`    ``},`\
[](#__codelineno-10-10)`    ``export_format``=``"qasm3"``,`\
[](#__codelineno-10-11)`)`\
[](#__codelineno-10-12)\
[](#__codelineno-10-13)`estimator`` ``=`` ``OQEstimator``(`\
[](#__codelineno-10-14)`    ``backend``=``backend``,`\
[](#__codelineno-10-15)`    ``scheduler``=``service``.``scheduler``,`\
[](#__codelineno-10-16)`    ``config``=``{`\
[](#__codelineno-10-17)`        ``"backend_class_id"``:`` ``"rigetti:cepheus-1-108q"``,`\
[](#__codelineno-10-18)`        ``"job_subcategory_id"``:`` ``"phys:oth"``,``  ``# Physics`\
[](#__codelineno-10-19)`    ``},`\
[](#__codelineno-10-20)`    ``export_format``=``"qasm3"``,`\
[](#__codelineno-10-21)`)`\

## Related Pages

- [Getting Started](https://docs.openquantum.com/qiskit-plugin/getting-started/) -- Install and first circuit.
- [Backends & Targets](https://docs.openquantum.com/qiskit-plugin/backends-targets/) -- Backend capabilities.
- [Examples](https://docs.openquantum.com/qiskit-plugin/examples/) -- Complete Qiskit workflows.
