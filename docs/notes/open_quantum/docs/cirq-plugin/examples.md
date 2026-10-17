> Full piece: [https://docs.openquantum.com/cirq-plugin/examples/](https://docs.openquantum.com/cirq-plugin/examples/)
> Retrieved 2026-10-17T05:09Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a3bddcd013c0f67c5725898aed86cfa6936d71bbcf60dcc7142732053fad11fe.

# Examples

All examples assume `OPENQUANTUM_CLIENT_ID` and `OPENQUANTUM_CLIENT_SECRET` are set in the environment. Replace the backend `short_code` with the QPU you want to target.

## Bell State

[](#__codelineno-0-1)`import`` ``cirq`\
[](#__codelineno-0-2)`from`` ``cirq_openquantum`` ``import`` ``OpenQuantumSampler`\
[](#__codelineno-0-3)\
[](#__codelineno-0-4)`sampler`` ``=`` ``OpenQuantumSampler``(``backend``=``"rigetti:cepheus-1-108q"``)`\
[](#__codelineno-0-5)\
[](#__codelineno-0-6)`q`` ``=`` ``cirq``.``LineQubit``.``range``(``2``)`\
[](#__codelineno-0-7)`circuit`` ``=`` ``cirq``.``Circuit``([`\
[](#__codelineno-0-8)`    ``cirq``.``H``(``q``[``0``]),`\
[](#__codelineno-0-9)`    ``cirq``.``CNOT``(``q``[``0``],`` ``q``[``1``]),`\
[](#__codelineno-0-10)`    ``cirq``.``measure``(``*``q``,`` ``key``=``"m"``),`\
[](#__codelineno-0-11)`])`\
[](#__codelineno-0-12)\
[](#__codelineno-0-13)`result`` ``=`` ``sampler``.``run``(``circuit``,`` ``repetitions``=``1024``)`\
[](#__codelineno-0-14)`print``(``result``.``histogram``(``key``=``"m"``))`\
[](#__codelineno-0-15)`# Counter({0: ~512, 3: ~512})   # 00 and 11`\

## GHZ State

[](#__codelineno-1-1)`import`` ``cirq`\
[](#__codelineno-1-2)`from`` ``cirq_openquantum`` ``import`` ``OpenQuantumSampler`\
[](#__codelineno-1-3)\
[](#__codelineno-1-4)`sampler`` ``=`` ``OpenQuantumSampler``(``backend``=``"ionq:forte-1"``)`\
[](#__codelineno-1-5)\
[](#__codelineno-1-6)`q`` ``=`` ``cirq``.``LineQubit``.``range``(``3``)`\
[](#__codelineno-1-7)`circuit`` ``=`` ``cirq``.``Circuit``([`\
[](#__codelineno-1-8)`    ``cirq``.``H``(``q``[``0``]),`\
[](#__codelineno-1-9)`    ``cirq``.``CNOT``(``q``[``0``],`` ``q``[``1``]),`\
[](#__codelineno-1-10)`    ``cirq``.``CNOT``(``q``[``1``],`` ``q``[``2``]),`\
[](#__codelineno-1-11)`    ``cirq``.``measure``(``*``q``,`` ``key``=``"m"``),`\
[](#__codelineno-1-12)`])`\
[](#__codelineno-1-13)\
[](#__codelineno-1-14)`result`` ``=`` ``sampler``.``run``(``circuit``,`` ``repetitions``=``2048``)`\
[](#__codelineno-1-15)`print``(``result``.``histogram``(``key``=``"m"``))`\
[](#__codelineno-1-16)`# concentrates on 0 (000) and 7 (111)`\

## Parameter Sweep

Because the sampler implements `run_sweep`, a `cirq.Sweepable` runs one circuit per parameter resolver — ideal for scanning a rotation angle.

[](#__codelineno-2-1)`import`` ``cirq`\
[](#__codelineno-2-2)`import`` ``sympy`\
[](#__codelineno-2-3)`from`` ``cirq_openquantum`` ``import`` ``OpenQuantumSampler`\
[](#__codelineno-2-4)\
[](#__codelineno-2-5)`sampler`` ``=`` ``OpenQuantumSampler``(``backend``=``"iqm:garnet"``)`\
[](#__codelineno-2-6)\
[](#__codelineno-2-7)`theta`` ``=`` ``sympy``.``Symbol``(``"theta"``)`\
[](#__codelineno-2-8)`q`` ``=`` ``cirq``.``LineQubit``.``range``(``1``)`\
[](#__codelineno-2-9)`circuit`` ``=`` ``cirq``.``Circuit``([``cirq``.``rx``(``theta``)``.``on``(``q``[``0``]),`` ``cirq``.``measure``(``q``[``0``],`` ``key``=``"m"``)])`\
[](#__codelineno-2-10)\
[](#__codelineno-2-11)`sweep`` ``=`` ``cirq``.``Linspace``(``"theta"``,`` ``start``=``0``,`` ``stop``=``3.14159``,`` ``length``=``5``)`\
[](#__codelineno-2-12)`results`` ``=`` ``sampler``.``run_sweep``(``circuit``,`` ``params``=``sweep``,`` ``repetitions``=``1024``)`\
[](#__codelineno-2-13)\
[](#__codelineno-2-14)`for`` ``params``,`` ``result`` ``in`` ``zip``(``sweep``,`` ``results``):`\
[](#__codelineno-2-15)`    ``ones`` ``=`` ``result``.``histogram``(``key``=``"m"``)[``1``]`\
[](#__codelineno-2-16)`    ``print``(``params``,`` ``"-> P(1) ="``,`` ``ones`` ``/`` ``1024``)`\

## Estimating an Expectation Value

Measure in the computational basis and fold the counts into a `<Z>` estimate.

[](#__codelineno-3-1)`import`` ``cirq`\
[](#__codelineno-3-2)`from`` ``cirq_openquantum`` ``import`` ``OpenQuantumSampler`\
[](#__codelineno-3-3)\
[](#__codelineno-3-4)`sampler`` ``=`` ``OpenQuantumSampler``(``backend``=``"ionq:forte-1"``)`\
[](#__codelineno-3-5)\
[](#__codelineno-3-6)`q`` ``=`` ``cirq``.``LineQubit``.``range``(``1``)`\
[](#__codelineno-3-7)`circuit`` ``=`` ``cirq``.``Circuit``([``cirq``.``ry``(``0.7``)``.``on``(``q``[``0``]),`` ``cirq``.``measure``(``q``[``0``],`` ``key``=``"z"``)])`\
[](#__codelineno-3-8)\
[](#__codelineno-3-9)`result`` ``=`` ``sampler``.``run``(``circuit``,`` ``repetitions``=``4096``)`\
[](#__codelineno-3-10)`hist`` ``=`` ``result``.``histogram``(``key``=``"z"``)`\
[](#__codelineno-3-11)`exp_z`` ``=`` ``(``hist``[``0``]`` ``-`` ``hist``[``1``])`` ``/`` ``4096`\
[](#__codelineno-3-12)`print``(``"<Z> ="``,`` ``exp_z``)`\

## Targeting a Simulator With Required Config

Some simulators require backend-specific configuration. The Quantum Rings simulator needs an `engine`:

[](#__codelineno-4-1)`import`` ``cirq`\
[](#__codelineno-4-2)`from`` ``cirq_openquantum`` ``import`` ``OpenQuantumSampler`\
[](#__codelineno-4-3)\
[](#__codelineno-4-4)`sampler`` ``=`` ``OpenQuantumSampler``(`\
[](#__codelineno-4-5)`    ``backend``=``"qr:gpu-gb10"``,`\
[](#__codelineno-4-6)`    ``configuration_data``=``{``"engine"``:`` ``"amber_quantum_rings"``},`\
[](#__codelineno-4-7)`)`\
[](#__codelineno-4-8)\
[](#__codelineno-4-9)`q`` ``=`` ``cirq``.``LineQubit``.``range``(``2``)`\
[](#__codelineno-4-10)`circuit`` ``=`` ``cirq``.``Circuit``([``cirq``.``H``(``q``[``0``]),`` ``cirq``.``CNOT``(``q``[``0``],`` ``q``[``1``]),`` ``cirq``.``measure``(``*``q``,`` ``key``=``"m"``)])`\
[](#__codelineno-4-11)\
[](#__codelineno-4-12)`result`` ``=`` ``sampler``.``run``(``circuit``,`` ``repetitions``=``1024``)`\
[](#__codelineno-4-13)`print``(``result``.``histogram``(``key``=``"m"``))`\

## Choosing Execution Plan and Priority

[](#__codelineno-5-1)`from`` ``cirq_openquantum`` ``import`` ``OpenQuantumSampler`\
[](#__codelineno-5-2)\
[](#__codelineno-5-3)`sampler`` ``=`` ``OpenQuantumSampler``(`\
[](#__codelineno-5-4)`    ``backend``=``"ionq:forte-1"``,`\
[](#__codelineno-5-5)`    ``job_subcategory_id``=``"ml:qcl"``,`\
[](#__codelineno-5-6)`    ``execution_plan``=``"private"``,`\
[](#__codelineno-5-7)`    ``queue_priority``=``"priority"``,`\
[](#__codelineno-5-8)`    ``organization_id``=``"your-org-uuid"``,`\
[](#__codelineno-5-9)`    ``job_timeout_seconds``=``3600``,`\
[](#__codelineno-5-10)`)`\

See [Backend Discovery](https://docs.openquantum.com/core-sdk/backend-discovery/) to list available backends and their `short_code`s.
