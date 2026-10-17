> Full piece: [https://docs.openquantum.com/qrisp-plugin/examples/](https://docs.openquantum.com/qrisp-plugin/examples/)
> Retrieved 2026-10-17T05:09Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6c328e64d9b093def7b9ed75b764af9fde7c36ceb38db1bc62f77b5a7f051069.

# Examples

All examples assume `OPENQUANTUM_CLIENT_ID` and `OPENQUANTUM_CLIENT_SECRET` are set in the environment. Replace the backend `short_code` with the QPU you want to target.

## Bell State

[](#__codelineno-0-1)`from`` ``qrisp`` ``import`` ``QuantumVariable``,`` ``h``,`` ``cx`\
[](#__codelineno-0-2)`from`` ``qrisp_openquantum`` ``import`` ``OpenQuantumBackend`\
[](#__codelineno-0-3)\
[](#__codelineno-0-4)`oq`` ``=`` ``OpenQuantumBackend``(``backend``=``"rigetti:cepheus-1-108q"``,`` ``shots``=``1024``)`\
[](#__codelineno-0-5)\
[](#__codelineno-0-6)`qv`` ``=`` ``QuantumVariable``(``2``)`\
[](#__codelineno-0-7)`h``(``qv``[``0``])`\
[](#__codelineno-0-8)`cx``(``qv``[``0``],`` ``qv``[``1``])`\
[](#__codelineno-0-9)\
[](#__codelineno-0-10)`print``(``qv``.``get_measurement``(``backend``=``oq``,`` ``shots``=``1024``))`\
[](#__codelineno-0-11)`# {'00': 0.51, '11': 0.49}`\

Note

`get_measurement` returns **probabilities**, not shot counts. This is Qrisp's own normalization and applies to every backend (the probability outputs below follow the same convention). For integer counts, run a low-level `QuantumCircuit` with `QuantumCircuit.run(backend=oq, shots=...)`.

## GHZ State

[](#__codelineno-1-1)`from`` ``qrisp`` ``import`` ``QuantumVariable``,`` ``h``,`` ``cx`\
[](#__codelineno-1-2)`from`` ``qrisp_openquantum`` ``import`` ``OpenQuantumBackend`\
[](#__codelineno-1-3)\
[](#__codelineno-1-4)`oq`` ``=`` ``OpenQuantumBackend``(``backend``=``"ionq:forte-1"``,`` ``shots``=``2048``)`\
[](#__codelineno-1-5)\
[](#__codelineno-1-6)`qv`` ``=`` ``QuantumVariable``(``3``)`\
[](#__codelineno-1-7)`h``(``qv``[``0``])`\
[](#__codelineno-1-8)`cx``(``qv``[``0``],`` ``qv``[``1``])`\
[](#__codelineno-1-9)`cx``(``qv``[``1``],`` ``qv``[``2``])`\
[](#__codelineno-1-10)\
[](#__codelineno-1-11)`print``(``qv``.``get_measurement``(``backend``=``oq``,`` ``shots``=``2048``))`\
[](#__codelineno-1-12)`# {'000': 0.5, '111': 0.5}`\

## QuantumFloat Arithmetic

Qrisp's high-level types let you compute on quantum integers directly. The program compiles to a circuit, runs on hardware, and decodes back to integer outcomes.

[](#__codelineno-2-1)`from`` ``qrisp`` ``import`` ``QuantumFloat`\
[](#__codelineno-2-2)`from`` ``qrisp_openquantum`` ``import`` ``OpenQuantumBackend`\
[](#__codelineno-2-3)\
[](#__codelineno-2-4)`oq`` ``=`` ``OpenQuantumBackend``(``backend``=``"iqm:garnet"``,`` ``shots``=``1024``)`\
[](#__codelineno-2-5)\
[](#__codelineno-2-6)`a`` ``=`` ``QuantumFloat``(``3``)`\
[](#__codelineno-2-7)`b`` ``=`` ``QuantumFloat``(``3``)`\
[](#__codelineno-2-8)`a``[:]`` ``=`` ``3`\
[](#__codelineno-2-9)`b``[:]`` ``=`` ``4`\
[](#__codelineno-2-10)`c`` ``=`` ``a`` ``+`` ``b`\
[](#__codelineno-2-11)\
[](#__codelineno-2-12)`print``(``c``.``get_measurement``(``backend``=``oq``,`` ``shots``=``1024``))`\
[](#__codelineno-2-13)`# concentrates on 7`\

## Targeting a Simulator With Required Config

Some simulators require backend-specific configuration. The Quantum Rings simulator needs an `engine`:

[](#__codelineno-3-1)`from`` ``qrisp`` ``import`` ``QuantumVariable``,`` ``h``,`` ``cx`\
[](#__codelineno-3-2)`from`` ``qrisp_openquantum`` ``import`` ``OpenQuantumBackend`\
[](#__codelineno-3-3)\
[](#__codelineno-3-4)`oq`` ``=`` ``OpenQuantumBackend``(`\
[](#__codelineno-3-5)`    ``backend``=``"qr:gpu-gb10"``,`\
[](#__codelineno-3-6)`    ``shots``=``1024``,`\
[](#__codelineno-3-7)`    ``configuration_data``=``{``"engine"``:`` ``"amber_quantum_rings"``},`\
[](#__codelineno-3-8)`)`\
[](#__codelineno-3-9)\
[](#__codelineno-3-10)`qv`` ``=`` ``QuantumVariable``(``2``)`\
[](#__codelineno-3-11)`h``(``qv``[``0``])`\
[](#__codelineno-3-12)`cx``(``qv``[``0``],`` ``qv``[``1``])`\
[](#__codelineno-3-13)\
[](#__codelineno-3-14)`print``(``qv``.``get_measurement``(``backend``=``oq``,`` ``shots``=``1024``))`\

## Choosing Execution Plan and Priority

[](#__codelineno-4-1)`from`` ``qrisp_openquantum`` ``import`` ``OpenQuantumBackend`\
[](#__codelineno-4-2)\
[](#__codelineno-4-3)`oq`` ``=`` ``OpenQuantumBackend``(`\
[](#__codelineno-4-4)`    ``backend``=``"ionq:forte-1"``,`\
[](#__codelineno-4-5)`    ``shots``=``4096``,`\
[](#__codelineno-4-6)`    ``job_subcategory_id``=``"ml:qcl"``,`\
[](#__codelineno-4-7)`    ``execution_plan``=``"private"``,`\
[](#__codelineno-4-8)`    ``queue_priority``=``"priority"``,`\
[](#__codelineno-4-9)`    ``organization_id``=``"your-org-uuid"``,`\
[](#__codelineno-4-10)`    ``job_timeout_seconds``=``3600``,`\
[](#__codelineno-4-11)`)`\

See [Backend Discovery](https://docs.openquantum.com/core-sdk/backend-discovery/) to list available backends and their `short_code`s.
