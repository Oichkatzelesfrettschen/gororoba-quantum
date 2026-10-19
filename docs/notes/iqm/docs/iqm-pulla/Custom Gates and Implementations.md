> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/Custom%20Gates%20and%20Implementations.html](https://docs.iqm.tech/4.7/iqm-pulla/Custom%20Gates%20and%20Implementations.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 4a9e058cd6796952ff96c66eb4b55fe388f8ce6d96849622c10ade7f16dbc8a2.

# Custom Gates and Gate Implementations

This notebook demonstrates how to work with user-defined quantum operations and gate implementations that go beyond the standard gate set.

Each quantum operation is associated with at least one `GateImplementation` which translates circuit-level concepts to lower-level instructions accepted by IQM Server. This example shows how the user can

- Select a non-default implementation for a gate

- Add a custom implementation for an existing gate

- Add a custom gate and implementation by using existing gates as building blocks (composite gates)

- Define new pulse waveforms for implementations

## Environment setup

Please refer to the `Quick Start.ipynb` for basic usage, terminology, and environment setup. It is recommended to run also `Configuration and Usage.ipynb` and `Sweeps.ipynb` before this notebook.

```
from pprint import pprint
from IPython.core.display import HTML
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass

from qiskit import QuantumCircuit
from qiskit.compiler import transpile

from iqm.iqm_client.util import print_env_vars
from iqm.qiskit_iqm import IQMProvider
from iqm.qiskit_iqm.pulse_level_utils import get_qiskit_compiler, qiskit_to_iqm
from iqm.pulse.gates import PRX_Samples
from iqm.pulse.gates.prx import PRX_CustomWaveforms
from iqm.pulse.playlist.waveforms import Waveform
from iqm.pulse.gate_implementation import CompositeGate
from iqm.pulse.quantum_ops import QuantumOp
from iqm.pulse.playlist.visualisation.base import inspect_playlist
from exa.common.control.sweep.sweep import Sweep
from exa.common.control.sweep.option import CenterSpanOptions, StartStopOptions
```

```
print_env_vars()

provider = IQMProvider()
backend = provider.get_backend()
iqm_client = backend.client
```

```
def example_qiskit_circuit():
    qc = QuantumCircuit(2, 2)
    qc.x(0)
    qc.cx(0, 1)
    qc.h(0)
    qc.measure_all()

    transpiled_qc = transpile(qc, backend=backend, layout_method='sabre', optimization_level=3)
    return transpiled_qc

example_qiskit_circuit().draw(output='mpl', style='clifford', idle_wires=False)
```

![](https://docs.iqm.tech/4.7/iqm-pulla/_images/2dce1a4a924f839e38362755a02d5e933a2923439091cf836fef0fecdf74aec0.png)

```
iqm_client.get_standard_compiler().show_stages()
```

Circuit-level Stages (1)

**Stage 0: circuit_stage** Perform Circuit-level transformations.

[TABLE]

Pulse-level Stages (5)

**Stage 0: circuit_resolution** Resolve Circuits into TimeBoxes.

[TABLE]

**Stage 1: timebox_stage** Perform TimeBox-level transformations.

[TABLE]

**Stage 2: timebox_resolution** Resolve TimeBoxes into Schedules.

[TABLE]

**Stage 3: dynamical_decoupling** Apply dynamical decoupling sequences to idle qubits in the Schedules.

[TABLE]

**Stage 4: schedule_stage** Perform Schedule-level transformations.

[TABLE]

Finalization Stages (2)

**Stage 0: schedule_resolution** Translate Schedules into a hardware-executable Playlist.

[TABLE]

**Stage 1: job_creation** Package the Playlist and metadata into a job description to be submitted to IQM Server.

[TABLE]

Post-processing Stages (2)

**Stage 0: construct_run_result** Aggregate raw hardware data into a structured run result object.

[TABLE]

**Stage 1: construct_data_variables** Map measured counts and states to high-level user variables.

[TABLE]

## Custom gates: Composite gates

IQM Pulse allows the user to define composite gates: gates consisting of other gates. Composite gates are particularly useful because they allow reusing the calibrated of data of the other gates. Furthermore, it is possible to use unique calibration data for the member gates inside a composite gate.

Define a `prx` implementation that acts like a normal `prx`, except it implements `X` with 2 pulses with a 100 ns wait between them. The `__call__` method produces a TimeBox using IQM Pulse’s `ScheduleBuilder`. It is worth mentioning that the composite gate is not restricted to using only registered gates; it could equally well return a TimeBox with lower level instructions.

```
class StretchedX(CompositeGate):
    registered_gates = ('prx',)  # Use the standard prx as a building block

    def __call__(self, angle: float, phase: float):
        normal_prx = self.build("prx", self.locus)
        if angle != np.pi:
            return normal_prx(angle, phase)

        half = normal_prx(np.pi / 2, phase)
        return half + self.builder.wait(self.locus, 100e-9, rounding=True) + half
```

Register a new gate `custom_x`, which `StretchedX` implements, and make it compatible with the circuit-level `prx`, by declaring it having the same parameters. Then change the first `prx` in the IQM Pulse circuit to use the new implementation.

```
circuits, compiler = qiskit_to_iqm(backend, example_qiskit_circuit())
compiler.add_implementation('custom_x', 'StretchedX', StretchedX, quantum_op=QuantumOp('custom_x', params={'angle': (float,), 'phase': (float,)}))

c = circuits[0]
for inst in c.instructions:
    if inst.name == 'prx':
        inst.name = 'custom_x'

run_definition, _ = compiler.compile(circuits)
```

Inspecting the schedule, the `X` gate in the circuit is indeed split into two pulses with a wait in between:

```
HTML(inspect_playlist(run_definition.sweep_definition.playlist, [0]))
```

## Custom gates: Custom waveforms

Next, change the pulse waveforms of a PRX gate.

The quickest way to test how some waveform performs is probably to just provide `np.array` samples and use the dedicated custom samples PRX implementation `PRX_Samples`. However, providing some samples is not enough to actually use the new waveform. At least the I amplitude needs to be calibrated. This can be done very easily by reproducing the Rabi experiment.

Defining a triangular waveform, one can indeed calibrate a PRX gate with it. Probably not as good as the PRX waveform, but the compiler allows for highly customized waveforms.

```
# 40 points rising, 40 points falling
# NOTE: the number of samples define the duration of the pulse via the sampling rate (2GHz usually).
y_up = np.linspace(0, 1, 40, endpoint=False)
y_down = np.linspace(1, 0, 40)

y = np.concatenate((y_up, y_down))

plt.plot(y)
```

```
[<matplotlib.lines.Line2D at 0x7b7f418ccfd0>]
```

![](https://docs.iqm.tech/4.7/iqm-pulla/_images/63a44a37ad3bd05084097344781ca764f79c4ec4682d9a498bf9237a1b642f26.png)

```
compiler = get_qiskit_compiler(backend)

# Rabi circuit
qc = QuantumCircuit(1,1)
qc.x(0)
qc.measure(0,0)

compiler.add_implementation("prx", "samples", PRX_Samples)  # register a custom samples implementation of PRX
settings = compiler.get_settings(circuits=[qc])
settings.gate_definitions.prx.default_implementation = "samples"  # set the samples implementaion as the default
settings.gates.prx.samples.QB1.set_from_dict({  # provide the triangular samples as calibration data
    "amplitude_q": 0.0,  # we don't worry about calibrating Q amplitude here
    "i":{"samples": y},
    "q": {"samples": np.zeros(80)}
})
# run Rabi experiment to determine the amplitude_i
amp_sweep = Sweep(parameter=settings.gates.prx.samples.QB1.amplitude_i.parameter, data=StartStopOptions(0.0, 0.99, 100).data)
run_definition, context = compiler.compile(circuits=[qc], components=["QB1"], settings=settings, sweeps=[amp_sweep])
job_tracker = iqm_client.submit_playlist(run_definition, context=context)
job_tracker.wait_for_completion()
result = job_tracker.result_exa(compiler=compiler)
# plot the QB1 e state probability
result.dataset["QB1__c_1_0_0_excited_state_probability"].plot()
```

```
[06-08 17:48:22;I] Waiting for job 019ea7b4-bf15-7ae0-aab1-e1b74042d4ec to finish...
```

```
[<matplotlib.lines.Line2D at 0x7b7f1813f810>]
```

![](https://docs.iqm.tech/4.7/iqm-pulla/_images/d59cb1076ed2d79e17f86257b8b41fc4993becb4d886caca4483993fd7551072.png)

Next, pick the amplitude value corresponding to the half amplitude of the shown Rabi oscillations, and set it as the I amplitude via `settings.gates.prx.samples.QB1.amplitude_i = <half amplitude value>`.

### Parametrized waveforms

Most of the canonical gate implementations are not defined in terms of samples, but instead parametrized. How this works is that the gate implementation has the calibration parameter `duration` (see e.g. `settings.gates.prx.drag_crf.QB1`) given in seconds. And the waveform itself may have any number of additional parameters that define its form (e.g. `settings.gates.prx.drag_crf.QB1.full_width`). Users can of course also create a parametrized waveform and use it in the PRX gate.

The easiest way to do this is to inherit from the `PRX_CustomWaveforms` implementation while defining the I and Q parametrized waveforms.

```
@dataclass(frozen=True)
class RaisedCosine(Waveform):
    r"""Raised cosine pulse.

    .. math::
        f(t) = \frac{1}{2} (1 + \cos((t - c) \pi / w)) \quad \text{when} \: |t - c| \le w, 0 \: \text{otherwise}

    where :math:`c` is :attr:`center_offset`, and :math:`w` is :attr:`width`.
    The raised cosine has a finite support.

    Args:
        width: half-width of the support
        center_offset: center offset
    """

    width: float
    center_offset: float = 0.0

    def _sample(self, sample_coords: np.ndarray) -> np.ndarray:
        offset_coords = sample_coords - self.center_offset
        return np.where(
            np.abs(offset_coords) <= self.width,
            0.5 * (1 + np.cos(offset_coords * np.pi / self.width)),
            0.0,
        )


@dataclass(frozen=True)
class RaisedCosineDerivative(Waveform):
    r"""Scaled derivative of the RaisedCosine pulse.

    .. math::
        f(t) = -\sin((t - c) \pi / w) \quad \text{when} \: |t - c| \le w, 0 \: \text{otherwise}

    where :math:`c` is :attr:`center_offset`, and :math:`w` is :attr:`width`.

    Args:
        width: half-width of the support
        center_offset: center offset
    """

    width: float
    center_offset: float = 0.0

    def _sample(self, sample_coords: np.ndarray) -> np.ndarray:
        offset_coords = sample_coords - self.center_offset
        return np.where(
            np.abs(offset_coords) <= self.width,
            -0.5 * np.sin(offset_coords * np.pi / self.width),
            0.0,
        )


class PRX_RaisedCosine(PRX_CustomWaveforms, wave_i=RaisedCosine, wave_q=RaisedCosineDerivative):
    """Implementation of PRX using a raised cosine pulse."""

    center_offset: float = 0.0
```

The class attributes of the waveforms define the calibration data they require. The `PRX_CustomWaveforms` class adds some more. Add the new `prx` implementation to the compiler to check what calibration data it needs:

```
circuits, compiler = qiskit_to_iqm(backend, example_qiskit_circuit())

compiler.add_implementation('prx', 'raised_cosine', PRX_RaisedCosine)
settings = compiler.get_settings(circuits=example_qiskit_circuit())
settings.gates.prx.raised_cosine.QB1
```

(gates.prx.raised_cosine.QB1)

gates.prx.raised_cosine.QB1: (Name: "gates.prx.raised_cosine.QB1", class:SettingNode) 0

|  |  |  |  |
|:---|----|:---|:---|
| , collection_type=, element_indices=None), value=None, read_only=False, path='gates.prx.raised_cosine.QB1.duration')"\>duration | not set/auto | s | pi pulse duration |
| , collection_type=, element_indices=None), value=None, read_only=False, path='gates.prx.raised_cosine.QB1.amplitude_i')"\>amplitude_i | not set/auto |  | pi pulse I channel amplitude |
| , collection_type=, element_indices=None), value=None, read_only=False, path='gates.prx.raised_cosine.QB1.amplitude_q')"\>amplitude_q | not set/auto |  | pi pulse Q channel amplitude |
| , collection_type=, element_indices=None), value=None, read_only=False, path='gates.prx.raised_cosine.QB1.width')"\>width | not set/auto | s | width of rc |
| , collection_type=, element_indices=None), value=0.0, read_only=False, path='gates.prx.raised_cosine.QB1.center_offset')"\>center_offset | 0 | s | center_offset of rc |

Make one of the `prx` gates in the circuit use our new implementation:

```
circuits[0].instructions[0].implementation = "raised_cosine"
```

Compiling this circuit right now would fail with an error:

```
Error in stage "circuit" pass "map_implementations_for_loci": Circuit 0: No calibration data for 'prx.raised_cosine' at ('QB1',).
```

(The locus (‘QB1’,) may differ in your output due to the stochastic nature of routing.)

Of course the gate needs to be calibrated, see the prevous example of Rabi experiment on a triangular wave. Provided some placeholder calibration data:

```
custom_cal_data = {
    "duration": 40e-09,
    "amplitude_i": 0.1662,
    "amplitude_q": -0.00802,
    "width": 20e-9,
    "center_offset": 3e-9,
}

for qubit in compiler.chip_topology.qubits:
    settings.gates.prx.raised_cosine[qubit].set_from_dict(custom_cal_data)
```

Now the compilation succeeds and `raised_cosine` was used once. The schedule visualization allows to verify that the pulse shape is indeed different on the first `prx` instance.

```
playlist, context = compiler.compile(circuits, settings=settings)
pprint(context['circuit_metrics'][0].gate_loci["prx"])
```

```
{'drag_crf_sx': Counter({('QB10',): 2, ('QB9',): 1}),
 'raised_cosine': Counter({('QB9',): 1})}
```
