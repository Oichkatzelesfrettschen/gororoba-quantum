"""qiskit-ibm-runtime local paths the repository calls: fake backends, the client-side executor Sampler, option
models, backend models, mid-circuit measurement and samplomatic twirling. Nothing here reads an account."""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime.circuit import MidCircuitMeasure
from qiskit_ibm_runtime.executor_sampler import Sampler
from qiskit_ibm_runtime.fake_provider import FakeFez, FakeManilaV2
from qiskit_ibm_runtime.models import BackendConfiguration, BackendProperties
from qiskit_ibm_runtime.options_models import SamplerOptions
from qiskit_ibm_runtime.options_models.twirling import TwirlingOptions
from qiskit_ibm_runtime.utils.backend_converter import convert_to_target
from samplomatic import build
from samplomatic.transpiler import generate_boxing_pass_manager


def test_fake_backend_targets_carry_durations_for_scheduling() -> None:
    backend = FakeFez()
    if backend.num_qubits != 156 or backend.target.dt is None:
        raise AssertionError((backend.num_qubits, backend.target.dt))
    circuit = QuantumCircuit(2, 2)
    circuit.h(0)
    circuit.cx(0, 1)
    circuit.delay(320, 1, "dt")
    circuit.measure([0, 1], [0, 1])
    compiled = transpile(
        circuit,
        backend=backend,
        initial_layout=[3, 4],
        scheduling_method="alap",
        optimization_level=1,
    )
    if compiled.layout.initial_index_layout()[:2] != [3, 4] or compiled.estimate_duration(backend.target) <= 0:
        raise AssertionError("layout or schedule lost")


def test_executor_sampler_runs_locally_on_a_fake_backend() -> None:
    circuit = QuantumCircuit(2, 2)
    circuit.x(0)
    circuit.cx(0, 1)
    circuit.measure([0, 1], [0, 1])
    backend = FakeManilaV2()
    pub = Sampler(mode=backend).run([transpile(circuit, backend)], shots=64).result()[0]
    counts = pub.data.c.get_counts()
    if sum(counts.values()) != 64 or max(counts, key=lambda key: counts[key]) != "11":
        raise AssertionError(counts)


def test_option_models_and_twirling_defaults() -> None:
    options = SamplerOptions()
    twirling = TwirlingOptions()
    if not isinstance(twirling.strategy, str) or not twirling.group:
        raise AssertionError(twirling)
    if options.model_dump() != SamplerOptions(**options.model_dump()).model_dump():
        raise AssertionError("SamplerOptions does not round-trip through model_dump")


def test_backend_models_rebuild_a_target_from_documents() -> None:
    backend = FakeManilaV2()
    properties = BackendProperties.from_dict(backend.properties().to_dict())
    configuration = BackendConfiguration.from_dict(backend.configuration().to_dict())
    if properties.faulty_qubits() or not all(properties.is_qubit_operational(q) for q in range(backend.num_qubits)):
        raise AssertionError("the Manila snapshot has no faulty qubit")
    if not 0 < properties.readout_error(0) < 1 or not 0 < properties.gate_error("sx", 0) < 1:
        raise AssertionError("error rates out of range")
    if not {"T1", "T2"} <= set(properties.qubit_property(0)):
        raise AssertionError(properties.qubit_property(0))
    target = convert_to_target(configuration, properties)
    if target.num_qubits != backend.num_qubits or set(target["cx"]) != set(backend.target["cx"]):
        raise AssertionError("the rebuilt target's cx edges differ from the backend's")


def test_mid_circuit_measure_is_a_measurement_instruction() -> None:
    circuit = QuantumCircuit(1, 1)
    circuit.append(MidCircuitMeasure(), [0], [0])
    if circuit.data[0].operation.num_qubits != 1 or circuit.data[0].operation.num_clbits != 1:
        raise AssertionError(circuit.data[0].operation)


def test_samplomatic_boxing_builds_a_parameterized_twirl() -> None:
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.cx(0, 1)
    compiled = transpile(circuit, basis_gates=["rz", "sx", "x", "cz"], optimization_level=1)
    options = TwirlingOptions()
    boxed = generate_boxing_pass_manager(
        enable_gates=True,
        enable_measures=False,
        twirling_strategy=options.strategy.replace("-", "_"),
        inject_noise_site="after",
        add_tags="none",
        twirling_group=options.group,
    ).run(compiled)
    template, samplex = build(boxed)
    values = np.asarray(
        samplex.sample(None, num_randomizations=8, rng=np.random.default_rng(), max_workers=1)["parameter_values"]
    )
    if values.shape != (8, template.num_parameters) or template.num_parameters == 0:
        raise AssertionError(f"parameter_values {values.shape} for {template.num_parameters} template parameters")
    if len({row.tobytes() for row in values}) < 2:
        raise AssertionError("eight randomizations drew one twirl")
