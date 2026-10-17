> Full piece: [https://docs.openquantum.com/qrisp-plugin/examples/](https://docs.openquantum.com/qrisp-plugin/examples/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 6c328e64d9b093def7b9ed75b764af9fde7c36ceb38db1bc62f77b5a7f051069.

# Examples

All examples assume `OPENQUANTUM_CLIENT_ID` and `OPENQUANTUM_CLIENT_SECRET` are set in the environment. Replace the backend `short_code` with the QPU you want to target.

## Bell State

``` python
from qrisp import QuantumVariable, h, cx
from qrisp_openquantum import OpenQuantumBackend

oq = OpenQuantumBackend(backend="rigetti:cepheus-1-108q", shots=1024)

qv = QuantumVariable(2)
h(qv[0])
cx(qv[0], qv[1])

print(qv.get_measurement(backend=oq, shots=1024))
# {'00': 0.51, '11': 0.49}
```

Note

`get_measurement` returns **probabilities**, not shot counts. This is Qrisp's own normalization and applies to every backend (the probability outputs below follow the same convention). For integer counts, run a low-level `QuantumCircuit` with `QuantumCircuit.run(backend=oq, shots=...)`.

## GHZ State

``` python
from qrisp import QuantumVariable, h, cx
from qrisp_openquantum import OpenQuantumBackend

oq = OpenQuantumBackend(backend="ionq:forte-1", shots=2048)

qv = QuantumVariable(3)
h(qv[0])
cx(qv[0], qv[1])
cx(qv[1], qv[2])

print(qv.get_measurement(backend=oq, shots=2048))
# {'000': 0.5, '111': 0.5}
```

## QuantumFloat Arithmetic

Qrisp's high-level types let you compute on quantum integers directly. The program compiles to a circuit, runs on hardware, and decodes back to integer outcomes.

``` python
from qrisp import QuantumFloat
from qrisp_openquantum import OpenQuantumBackend

oq = OpenQuantumBackend(backend="iqm:garnet", shots=1024)

a = QuantumFloat(3)
b = QuantumFloat(3)
a[:] = 3
b[:] = 4
c = a + b

print(c.get_measurement(backend=oq, shots=1024))
# concentrates on 7
```

## Targeting a Simulator With Required Config

Some simulators require backend-specific configuration. The Quantum Rings simulator needs an `engine`:

``` python
from qrisp import QuantumVariable, h, cx
from qrisp_openquantum import OpenQuantumBackend

oq = OpenQuantumBackend(
    backend="qr:gpu-gb10",
    shots=1024,
    configuration_data={"engine": "amber_quantum_rings"},
)

qv = QuantumVariable(2)
h(qv[0])
cx(qv[0], qv[1])

print(qv.get_measurement(backend=oq, shots=1024))
```

## Choosing Execution Plan and Priority

``` python
from qrisp_openquantum import OpenQuantumBackend

oq = OpenQuantumBackend(
    backend="ionq:forte-1",
    shots=4096,
    job_subcategory_id="ml:qcl",
    execution_plan="private",
    queue_priority="priority",
    organization_id="your-org-uuid",
    job_timeout_seconds=3600,
)
```

See [Backend Discovery](https://docs.openquantum.com/core-sdk/backend-discovery/) to list available backends and their `short_code`s.
