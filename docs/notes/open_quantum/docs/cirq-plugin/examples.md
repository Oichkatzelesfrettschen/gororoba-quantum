> Full piece: [https://docs.openquantum.com/cirq-plugin/examples/](https://docs.openquantum.com/cirq-plugin/examples/)
> Retrieved 2026-10-17T05:33Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 a3bddcd013c0f67c5725898aed86cfa6936d71bbcf60dcc7142732053fad11fe.

# Examples

All examples assume `OPENQUANTUM_CLIENT_ID` and `OPENQUANTUM_CLIENT_SECRET` are set in the environment. Replace the backend `short_code` with the QPU you want to target.

## Bell State

``` python
import cirq
from cirq_openquantum import OpenQuantumSampler

sampler = OpenQuantumSampler(backend="rigetti:cepheus-1-108q")

q = cirq.LineQubit.range(2)
circuit = cirq.Circuit([
    cirq.H(q[0]),
    cirq.CNOT(q[0], q[1]),
    cirq.measure(*q, key="m"),
])

result = sampler.run(circuit, repetitions=1024)
print(result.histogram(key="m"))
# Counter({0: ~512, 3: ~512})   # 00 and 11
```

## GHZ State

``` python
import cirq
from cirq_openquantum import OpenQuantumSampler

sampler = OpenQuantumSampler(backend="ionq:forte-1")

q = cirq.LineQubit.range(3)
circuit = cirq.Circuit([
    cirq.H(q[0]),
    cirq.CNOT(q[0], q[1]),
    cirq.CNOT(q[1], q[2]),
    cirq.measure(*q, key="m"),
])

result = sampler.run(circuit, repetitions=2048)
print(result.histogram(key="m"))
# concentrates on 0 (000) and 7 (111)
```

## Parameter Sweep

Because the sampler implements `run_sweep`, a `cirq.Sweepable` runs one circuit per parameter resolver — ideal for scanning a rotation angle.

``` python
import cirq
import sympy
from cirq_openquantum import OpenQuantumSampler

sampler = OpenQuantumSampler(backend="iqm:garnet")

theta = sympy.Symbol("theta")
q = cirq.LineQubit.range(1)
circuit = cirq.Circuit([cirq.rx(theta).on(q[0]), cirq.measure(q[0], key="m")])

sweep = cirq.Linspace("theta", start=0, stop=3.14159, length=5)
results = sampler.run_sweep(circuit, params=sweep, repetitions=1024)

for params, result in zip(sweep, results):
    ones = result.histogram(key="m")[1]
    print(params, "-> P(1) =", ones / 1024)
```

## Estimating an Expectation Value

Measure in the computational basis and fold the counts into a `<Z>` estimate.

``` python
import cirq
from cirq_openquantum import OpenQuantumSampler

sampler = OpenQuantumSampler(backend="ionq:forte-1")

q = cirq.LineQubit.range(1)
circuit = cirq.Circuit([cirq.ry(0.7).on(q[0]), cirq.measure(q[0], key="z")])

result = sampler.run(circuit, repetitions=4096)
hist = result.histogram(key="z")
exp_z = (hist[0] - hist[1]) / 4096
print("<Z> =", exp_z)
```

## Targeting a Simulator With Required Config

Some simulators require backend-specific configuration. The Quantum Rings simulator needs an `engine`:

``` python
import cirq
from cirq_openquantum import OpenQuantumSampler

sampler = OpenQuantumSampler(
    backend="qr:gpu-gb10",
    configuration_data={"engine": "amber_quantum_rings"},
)

q = cirq.LineQubit.range(2)
circuit = cirq.Circuit([cirq.H(q[0]), cirq.CNOT(q[0], q[1]), cirq.measure(*q, key="m")])

result = sampler.run(circuit, repetitions=1024)
print(result.histogram(key="m"))
```

## Choosing Execution Plan and Priority

``` python
from cirq_openquantum import OpenQuantumSampler

sampler = OpenQuantumSampler(
    backend="ionq:forte-1",
    job_subcategory_id="ml:qcl",
    execution_plan="private",
    queue_priority="priority",
    organization_id="your-org-uuid",
    job_timeout_seconds=3600,
)
```

See [Backend Discovery](https://docs.openquantum.com/core-sdk/backend-discovery/) to list available backends and their `short_code`s.
