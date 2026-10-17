> Full piece: [https://docs.openquantum.com/qiskit-plugin/examples/](https://docs.openquantum.com/qiskit-plugin/examples/)
> Retrieved 2026-10-17T05:09Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 404c46112a374eaa57ecbc8e4c3fcacf5f03e091aa58e9bcf762d79a5bfffbd5.

# Qiskit Plugin Examples

Common Qiskit workflows using the `openquantum-sdk[qiskit]` plugin.

Note

All examples assume you have valid credentials configured. See [Authentication](https://docs.openquantum.com/core-sdk/authentication/) for setup options.

## Bell State with Sampler

[](#__codelineno-0-1)`from`` ``openquantum_sdk.auth`` ``import`` ``ClientCredentials`\
[](#__codelineno-0-2)`from`` ``openquantum_sdk_qiskit`` ``import`` ``OpenQuantumService`\
[](#__codelineno-0-3)`from`` ``qiskit.circuit`` ``import`` ``QuantumCircuit`\
[](#__codelineno-0-4)\
[](#__codelineno-0-5)`service`` ``=`` ``OpenQuantumService``(`\
[](#__codelineno-0-6)`    ``creds``=``ClientCredentials``(`\
[](#__codelineno-0-7)`        ``client_id``=``"s_your_client_id"``,`\
[](#__codelineno-0-8)`        ``client_secret``=``"your_client_secret"``,`\
[](#__codelineno-0-9)`    ``),`\
[](#__codelineno-0-10)`)`\
[](#__codelineno-0-11)\
[](#__codelineno-0-12)`backend`` ``=`` ``service``.``return_backend``(``"rigetti:cepheus-1-108q"``)`\
[](#__codelineno-0-13)\
[](#__codelineno-0-14)`sampler`` ``=`` ``service``.``create_sampler``(`\
[](#__codelineno-0-15)`    ``backend``=``backend``,`\
[](#__codelineno-0-16)`    ``job_subcategory_id``=``"phys:oth"``,``  ``# Physics`\
[](#__codelineno-0-17)`)`\
[](#__codelineno-0-18)\
[](#__codelineno-0-19)`qc`` ``=`` ``QuantumCircuit``(``2``,`` ``2``)`\
[](#__codelineno-0-20)`qc``.``h``(``0``)`\
[](#__codelineno-0-21)`qc``.``cx``(``0``,`` ``1``)`\
[](#__codelineno-0-22)`qc``.``measure``([``0``,`` ``1``],`` ``[``0``,`` ``1``])`\
[](#__codelineno-0-23)\
[](#__codelineno-0-24)`job`` ``=`` ``sampler``.``run``([``qc``],`` ``shots``=``128``)`\
[](#__codelineno-0-25)`result`` ``=`` ``job``.``result``()`\
[](#__codelineno-0-26)`counts`` ``=`` ``result``[``0``]``.``data``.``meas``.``get_counts``()`\
[](#__codelineno-0-27)`print``(``f``"Bell state counts: ``{``counts``}``"``)`\
[](#__codelineno-0-28)\
[](#__codelineno-0-29)`service``.``close``()`\

## Expectation Value with Estimator

[](#__codelineno-1-1)`from`` ``openquantum_sdk.auth`` ``import`` ``ClientCredentials`\
[](#__codelineno-1-2)`from`` ``openquantum_sdk_qiskit`` ``import`` ``OpenQuantumService`\
[](#__codelineno-1-3)`from`` ``qiskit.circuit`` ``import`` ``QuantumCircuit`\
[](#__codelineno-1-4)`from`` ``qiskit.quantum_info`` ``import`` ``SparsePauliOp`\
[](#__codelineno-1-5)\
[](#__codelineno-1-6)`service`` ``=`` ``OpenQuantumService``(`\
[](#__codelineno-1-7)`    ``creds``=``ClientCredentials``(`\
[](#__codelineno-1-8)`        ``client_id``=``"s_your_client_id"``,`\
[](#__codelineno-1-9)`        ``client_secret``=``"your_client_secret"``,`\
[](#__codelineno-1-10)`    ``),`\
[](#__codelineno-1-11)`)`\
[](#__codelineno-1-12)\
[](#__codelineno-1-13)`backend`` ``=`` ``service``.``return_backend``(``"rigetti:cepheus-1-108q"``)`\
[](#__codelineno-1-14)\
[](#__codelineno-1-15)`estimator`` ``=`` ``service``.``create_estimator``(`\
[](#__codelineno-1-16)`    ``backend``=``backend``,`\
[](#__codelineno-1-17)`    ``job_subcategory_id``=``"phys:oth"``,``  ``# Physics`\
[](#__codelineno-1-18)`)`\
[](#__codelineno-1-19)\
[](#__codelineno-1-20)`qc`` ``=`` ``QuantumCircuit``(``2``)`\
[](#__codelineno-1-21)`qc``.``h``(``0``)`\
[](#__codelineno-1-22)`qc``.``cx``(``0``,`` ``1``)`\
[](#__codelineno-1-23)\
[](#__codelineno-1-24)`observable`` ``=`` ``SparsePauliOp``(``"ZZ"``)`\
[](#__codelineno-1-25)\
[](#__codelineno-1-26)`job`` ``=`` ``estimator``.``run``([(``qc``,`` ``observable``)])`\
[](#__codelineno-1-27)`result`` ``=`` ``job``.``result``()`\
[](#__codelineno-1-28)`print``(``f``"<ZZ> = ``{``result``[``0``]``.``data``.``evs``}``"``)`\
[](#__codelineno-1-29)\
[](#__codelineno-1-30)`service``.``close``()`\

## Multi-Circuit Batch with Sampler

[](#__codelineno-2-1)`from`` ``openquantum_sdk.auth`` ``import`` ``ClientCredentials`\
[](#__codelineno-2-2)`from`` ``openquantum_sdk_qiskit`` ``import`` ``OpenQuantumService`\
[](#__codelineno-2-3)`from`` ``qiskit.circuit`` ``import`` ``QuantumCircuit`\
[](#__codelineno-2-4)\
[](#__codelineno-2-5)`service`` ``=`` ``OpenQuantumService``(`\
[](#__codelineno-2-6)`    ``creds``=``ClientCredentials``(`\
[](#__codelineno-2-7)`        ``client_id``=``"s_your_client_id"``,`\
[](#__codelineno-2-8)`        ``client_secret``=``"your_client_secret"``,`\
[](#__codelineno-2-9)`    ``),`\
[](#__codelineno-2-10)`)`\
[](#__codelineno-2-11)\
[](#__codelineno-2-12)`backend`` ``=`` ``service``.``return_backend``(``"rigetti:cepheus-1-108q"``)`\
[](#__codelineno-2-13)\
[](#__codelineno-2-14)`sampler`` ``=`` ``service``.``create_sampler``(`\
[](#__codelineno-2-15)`    ``backend``=``backend``,`\
[](#__codelineno-2-16)`    ``job_subcategory_id``=``"oth:oth"``,`\
[](#__codelineno-2-17)`)`\
[](#__codelineno-2-18)\
[](#__codelineno-2-19)`# Circuit 1: Bell state`\
[](#__codelineno-2-20)`qc1`` ``=`` ``QuantumCircuit``(``2``,`` ``2``)`\
[](#__codelineno-2-21)`qc1``.``h``(``0``)`\
[](#__codelineno-2-22)`qc1``.``cx``(``0``,`` ``1``)`\
[](#__codelineno-2-23)`qc1``.``measure``([``0``,`` ``1``],`` ``[``0``,`` ``1``])`\
[](#__codelineno-2-24)\
[](#__codelineno-2-25)`# Circuit 2: GHZ state`\
[](#__codelineno-2-26)`qc2`` ``=`` ``QuantumCircuit``(``3``,`` ``3``)`\
[](#__codelineno-2-27)`qc2``.``h``(``0``)`\
[](#__codelineno-2-28)`qc2``.``cx``(``0``,`` ``1``)`\
[](#__codelineno-2-29)`qc2``.``cx``(``1``,`` ``2``)`\
[](#__codelineno-2-30)`qc2``.``measure``([``0``,`` ``1``,`` ``2``],`` ``[``0``,`` ``1``,`` ``2``])`\
[](#__codelineno-2-31)\
[](#__codelineno-2-32)`# Submit both circuits`\
[](#__codelineno-2-33)`job`` ``=`` ``sampler``.``run``([``qc1``,`` ``qc2``],`` ``shots``=``128``)`\
[](#__codelineno-2-34)`result`` ``=`` ``job``.``result``()`\
[](#__codelineno-2-35)\
[](#__codelineno-2-36)`print``(``f``"Bell state: ``{``result``[``0``]``.``data``.``meas``.``get_counts``()``}``"``)`\
[](#__codelineno-2-37)`print``(``f``"GHZ state:  ``{``result``[``1``]``.``data``.``meas``.``get_counts``()``}``"``)`\
[](#__codelineno-2-38)\
[](#__codelineno-2-39)`service``.``close``()`\

## Backend Selection and Filtering

[](#__codelineno-3-1)`from`` ``openquantum_sdk.auth`` ``import`` ``ClientCredentials`\
[](#__codelineno-3-2)`from`` ``openquantum_sdk_qiskit`` ``import`` ``OpenQuantumService`\
[](#__codelineno-3-3)\
[](#__codelineno-3-4)`service`` ``=`` ``OpenQuantumService``(`\
[](#__codelineno-3-5)`    ``creds``=``ClientCredentials``(`\
[](#__codelineno-3-6)`        ``client_id``=``"s_your_client_id"``,`\
[](#__codelineno-3-7)`        ``client_secret``=``"your_client_secret"``,`\
[](#__codelineno-3-8)`    ``),`\
[](#__codelineno-3-9)`)`\
[](#__codelineno-3-10)\
[](#__codelineno-3-11)`# List all online QPU backends`\
[](#__codelineno-3-12)`qpu_backends`` ``=`` ``service``.``backends``(``online``=``True``,`` ``device_type``=``"QPU"``)`\
[](#__codelineno-3-13)`for`` ``b`` ``in`` ``qpu_backends``:`\
[](#__codelineno-3-14)`    ``print``(``f``"``{``b``[``'short_code'``]``}``: ``{``b``[``'name'``]``}`` (queue: ``{``b``[``'queue_depth'``]``}``)"``)`\
[](#__codelineno-3-15)\
[](#__codelineno-3-16)`# Search by name`\
[](#__codelineno-3-17)`ionq`` ``=`` ``service``.``backends``(``name``=``"ionq"``)`\
[](#__codelineno-3-18)`for`` ``b`` ``in`` ``ionq``:`\
[](#__codelineno-3-19)`    ``print``(``f``"``{``b``[``'short_code'``]``}``: ``{``b``[``'name'``]``}``"``)`\
[](#__codelineno-3-20)\
[](#__codelineno-3-21)`service``.``close``()`\

## Using a Saved Account

[](#__codelineno-4-1)`from`` ``openquantum_sdk.auth`` ``import`` ``ClientCredentials`\
[](#__codelineno-4-2)`from`` ``openquantum_sdk_qiskit`` ``import`` ``OpenQuantumService`\
[](#__codelineno-4-3)\
[](#__codelineno-4-4)`# Save credentials once`\
[](#__codelineno-4-5)`OpenQuantumService``.``save_account``(`\
[](#__codelineno-4-6)`    ``name``=``"default"``,`\
[](#__codelineno-4-7)`    ``creds``=``ClientCredentials``(`\
[](#__codelineno-4-8)`        ``client_id``=``"s_your_client_id"``,`\
[](#__codelineno-4-9)`        ``client_secret``=``"your_client_secret"``,`\
[](#__codelineno-4-10)`    ``),`\
[](#__codelineno-4-11)`)`\
[](#__codelineno-4-12)\
[](#__codelineno-4-13)`# Load from saved account in future sessions`\
[](#__codelineno-4-14)`service`` ``=`` ``OpenQuantumService``.``from_saved_account``()`\
[](#__codelineno-4-15)\
[](#__codelineno-4-16)`# Or let it auto-load`\
[](#__codelineno-4-17)`service`` ``=`` ``OpenQuantumService``()`\
[](#__codelineno-4-18)\
[](#__codelineno-4-19)`backends`` ``=`` ``service``.``backends``()`\
[](#__codelineno-4-20)`print``(``f``"Found ``{``len``(``backends``)``}`` backends"``)`\
[](#__codelineno-4-21)\
[](#__codelineno-4-22)`service``.``close``()`\

## Related Pages

- [Getting Started](https://docs.openquantum.com/qiskit-plugin/getting-started/) -- Installation and first circuit.
- [Backends & Targets](https://docs.openquantum.com/qiskit-plugin/backends-targets/) -- Backend capabilities.
- [Sampler & Estimator](https://docs.openquantum.com/qiskit-plugin/sampler-estimator/) -- SamplerV2 and EstimatorV2 reference.
