> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/Configuration%20and%20Usage.html](https://docs.iqm.tech/4.7/iqm-pulla/Configuration%20and%20Usage.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 d172942797adf153a9ae28ead5092368e2d873f1d5d99f64d1a8c466cc7d78e4.

# Configuration and Usage

This notebook describes the basic concepts and configuration of pulse-level access.

```
from pprint import pprint
from IPython.core.display import HTML

from qiskit import QuantumCircuit, visualization
from qiskit.compiler import transpile

from iqm.iqm_client import IQMClient
from iqm.iqm_client.util import print_env_vars
from iqm.qiskit_iqm import IQMProvider
from iqm.qiskit_iqm.pulse_level_utils import qiskit_to_iqm, sweep_job_to_qiskit
from iqm.pulse.playlist.visualisation.base import inspect_playlist
```

## Basics

### IQM Client

An `IQMClient` object is conceptually an **IQM quantum computer client for connecting to the IQM server and constructing a circuit-to-pulse compiler**. It has

- a method for creating the compiler object

- a method for executing pulse-level instruction schedules (e.g. those created by the compiler)

- a method for executing circuits

A compiler object defines the specific **circuit-to-pulse compilation logic**. It consists of the following:

- Information about the QC (QPU topology, control channel properties etc.)

- Compilation stages, divided into circuit (and above)-level stages, pulse-level stages, finalization stages and return data post-processing stages

- Set of available circuit-level quantum operations (“native operations”) (including user-defined operations)

- Set of implementations for each native operation, including user-defined implementations

- Methods for manipulating the calibration, operations, and implementations

IQMClient can construct a standard compiler equivalent to the one used by the server side (IQM Server). You can also construct a compiler manually.

To create an instance of IQMClient, either you need to provide the URL of IQM Server and the authentication information explicitly to `IQMClient.__init__` or set the necessary environment variables as explained in the `Quick Start` notebook. Upon successful initialization, some configuration data is printed (the verbosity of such messages will be controlled by a debug level value).

```
print_env_vars()

client = IQMClient.from_url(
    "<IQM Server URL>",
    quantum_computer="<quantum computer name>",
    token="<your API token>",
)
```

Call the `get_standard_compiler()` method to get an instance of `Compiler`. One of the duties of the compiler is to provide the calibration defining the QPU’s operating point. By default, `get_standard_compiler()` fetches the default calibration set from the server (this network request takes a few moments), but the user can customize the calibration fetching using any sequence of **observation loading rules** via `get_standard_compiler(loading_rules=<my custom rules>)`

It may also be possible that, due to human error, the default calibration set stored on the server is invalid (or incompatible with your version of IQM Client or IQM Pulse). In that case `get_standard_compiler()` will fail.

```
# Define the standard compiler that loads the default calibration set as its initial operating point.
compiler = client.get_standard_compiler()

compiler.show_stages()
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

### Settings

The compiler handles the operation point via a `SettingNode` object that contains the entire calibration (HW-settings, gate implementation calibration, compilation options, and auxiliary characterization information) in a single editable tree structure. The settings tree will include any circuit parameters of a parametrized circuit in case that is what we are compiling. For this reason, the settings are generated per a circuit batch. To study the general structure of the Compiler settings tree we can now generate it for an empty placeholder circuit.

```
# Generate the settings for an empty list of circuits
settings = compiler.get_settings(circuits=[])

# Print it in HTML -- click on the subnodes open them up in the visualisation
settings
```

The `settings.controllers` node contains the operating point settings for the HW controllers in the backend. This includes, for example, settings for qubit drive frequencies and qubit and coupler flux parking voltages. The controllers node contains further subnodes for each physical component of the QPU, under which one can find the controllers related to that component. Additionally a general `options` controller defines certain QPU-wide settings.

```
# Print the controllers node -- click on the subnodes to open them up
settings.controllers
```

(controllers)

controllers: (Name: "controllers", class:SettingNode) 0

- QB1: (Name: "QB1", class:SettingNode) 1
  - drive: (Name: "QB1\_\_drive", class:SettingNode) 2
    |  |  |  |  |
    |:---|----|:---|:---|
    | , collection_type=, element_indices=None), value=False, read_only=False, path='controllers.QB1.drive.continuous_wave_enabled')"\>continuous_wave_enabled | False |  | Enable continuous wave mode |
    | , collection_type=, element_indices=None), value=True, read_only=False, path='controllers.QB1.drive.status')"\>status | True |  | Output on |
    | , collection_type=, element_indices=None), value=1.0, read_only=False, path='controllers.QB1.drive.continuous_wave_amplitude')"\>continuous_wave_amplitude | 1 |  | Scaling factor for CW output amplitude |
    | , collection_type=, element_indices=None), value=3893001948.56542, read_only=False, path='controllers.QB1.drive.frequency')"\>frequency | 3 893 | MHz | Frequency |

    - local_oscillator: (Name: "QB1\_\_drive.local_oscillator", class:SettingNode) 3
      |  |  |  |  |
      |:---|----|:---|:---|
      | , collection_type=, element_indices=None), value=None, read_only=False, path='controllers.QB1.drive.local_oscillator.phase')"\>phase | not set/auto | deg | Phase |
      | , collection_type=, element_indices=None), value=15, read_only=False, path='controllers.QB1.drive.local_oscillator.power')"\>power | 15 | dBm | Power |
      | , collection_type=, element_indices=None), value=False, read_only=False, path='controllers.QB1.drive.local_oscillator.status')"\>status | False |  | Output on |
      | , collection_type=, element_indices=None), value=None, read_only=False, path='controllers.QB1.drive.local_oscillator.frequency')"\>frequency | not set/auto | Hz | LO frequency |
    - awg: (Name: "QB1\_\_drive.awg", class:SettingNode) 3
      |  |  |  |  |
      |:---|----|:---|:---|
      | , collection_type=, element_indices=None), value=\[\], read_only=True, path='controllers.QB1.drive.awg.feedback_sources')"\>feedback_sources | \[ \] |  | Available feedback signal sources |
      | , collection_type=, element_indices=None), value=2.0, read_only=False, path='controllers.QB1.drive.awg.output_range')"\>output_range | 2 | V | DAC output range |
      | , collection_type=, element_indices=None), value=-295000000.0, read_only=False, path='controllers.QB1.drive.awg.intermediate_frequency')"\>intermediate_frequency | -295 | MHz | IQ intermediate frequency |
      | , collection_type=, element_indices=None), value=16, read_only=True, path='controllers.QB1.drive.awg.instruction_duration_min')"\>instruction_duration_min | 16 | samples | Minimum instruction duration |
      | , collection_type=, element_indices=None), value=True, read_only=False, path='controllers.QB1.drive.awg.status')"\>status | True |  | Enable output |
      | , collection_type=, element_indices=None), value=5.24e-07, read_only=False, path='controllers.QB1.drive.awg.trigger_delay')"\>trigger_delay | 524 | ns | Delay to correct trigger skew |
      | , collection_type=, element_indices=None), value=2400000000.0, read_only=True, path='controllers.QB1.drive.awg.sampling_rate')"\>sampling_rate | 2 400 | MHz | Sampling rate |
      | , collection_type=, element_indices=None), value=16, read_only=True, path='controllers.QB1.drive.awg.instruction_duration_granularity')"\>instruction_duration_granularity | 16 | samples | Instruction duration granularity |
      | , collection_type=, element_indices=None), value='hdawg', read_only=True, path='controllers.QB1.drive.awg.device_type')"\>device_type | "hdawg" |  | Device type |

      - mixer_correction: (Name: "QB1\_\_drive.awg.mixer_correction", class:SettingNode) 4
        |  |  |  |  |
        |:---|----|:---|:---|
        | , collection_type=, element_indices=None), value=0.0, read_only=False, path='controllers.QB1.drive.awg.mixer_correction.dc_bias_q')"\>dc_bias_q | 0 | V | LO suppression DC bias Q |
        | , collection_type=, element_indices=None), value=0.0, read_only=False, path='controllers.QB1.drive.awg.mixer_correction.phase_imbalance')"\>phase_imbalance | 0 | rad | I-Q phase imbalance |
        | , collection_type=, element_indices=None), value=1.0, read_only=False, path='controllers.QB1.drive.awg.mixer_correction.amplitude_imbalance')"\>amplitude_imbalance | 1 |  | Amplitude imbalance |
        | , collection_type=, element_indices=None), value=0.0, read_only=False, path='controllers.QB1.drive.awg.mixer_correction.dc_bias_i')"\>dc_bias_i | 0 | V | LO suppression DC bias I |
      - continuous_wave: (Name: "QB1\_\_drive.awg.continuous_wave", class:SettingNode) 4
        |  |  |  |  |
        |:---|----|:---|:---|
        | , collection_type=, element_indices=None), value=0.0, read_only=False, path='controllers.QB1.drive.awg.continuous_wave.amplitude')"\>amplitude | 0 |  | CW output amplitude scale |
        | , collection_type=, element_indices=None), value=False, read_only=False, path='controllers.QB1.drive.awg.continuous_wave.enabled')"\>enabled | False |  | Continuous wave mode enabled |
  - flux: (Name: "QB1\_\_flux", class:SettingNode) 2
    |  |  |  |  |
    |:---|----|:---|:---|
    | , collection_type=, element_indices=None), value=3.0517694540765916e-05, read_only=True, path='controllers.QB1.flux.voltage_resolution')"\>voltage_resolution | 30.5177 | μV | Bias voltage resolution |
    | , collection_type=, element_indices=None), value=-0.21586795337665216, read_only=False, path='controllers.QB1.flux.voltage')"\>voltage | -215.868 | mV | Bias voltage |
- QB2: (Name: "QB2", class:SettingNode) 1
  - drive: (Name: "QB2\_\_drive", class:SettingNode) 2
    |  |  |  |  |
    |:---|----|:---|:---|
    | , collection_type=, element_indices=None), value=False, read_only=False, path='controllers.QB2.drive.continuous_wave_enabled')"\>continuous_wave_enabled | False |  | Enable continuous wave mode |
    | , collection_type=, element_indices=None), value=True, read_only=False, path='controllers.QB2.drive.status')"\>status | True |  | Output on |
    | , collection_type=, element_indices=None), value=1.0, read_only=False, path='controllers.QB2.drive.continuous_wave_amplitude')"\>continuous_wave_amplitude | 1 |  | Scaling factor for CW output amplitude |
    | , collection_type=, element_indices=None), value=3894390434.844012, read_only=False, path='controllers.QB2.drive.frequency')"\>frequency | 3 894.39 | MHz | Frequency |

    - local_oscillator: (Name: "QB2\_\_drive.local_oscillator", class:SettingNode) 3
      |  |  |  |  |
      |:---|----|:---|:---|
      | , collection_type=, element_indices=None), value=None, read_only=False, path='controllers.QB2.drive.local_oscillator.phase')"\>phase | not set/auto | deg | Phase |
      | , collection_type=, element_indices=None), value=15, read_only=False, path='controllers.QB2.drive.local_oscillator.power')"\>power | 15 | dBm | Power |
      | , collection_type=, element_indices=None), value=False, read_only=False, path='controllers.QB2.drive.local_oscillator.status')"\>status | False |  | Output on |
      | , collection_type=, element_indices=None), value=None, read_only=False, path='controllers.QB2.drive.local_oscillator.frequency')"\>frequency | not set/auto | Hz | LO frequency |
    - awg: (Name: "QB2\_\_drive.awg", class:SettingNode) 3
      |  |  |  |  |
      |:---|----|:---|:---|
      | , collection_type=, element_indices=None), value=\[\], read_only=True, path='controllers.QB2.drive.awg.feedback_sources')"\>feedback_sources | \[ \] |  | Available feedback signal sources |
      | , collection_type=, element_indices=None), value=2.0, read_only=False, path='controllers.QB2.drive.awg.output_range')"\>output_range | 2 | V | DAC output range |
      | , collection_type=, element_indices=None), value=-295000000.0, read_only=False, path='controllers.QB2.drive.awg.intermediate_frequency')"\>intermediate_frequency | -295 | MHz | IQ intermediate frequency |
      | , collection_type=, element_indices=None), value=16, read_only=True, path='controllers.QB2.drive.awg.instruction_duration_min')"\>instruction_duration_min | 16 | samples | Minimum instruction duration |
      | , collection_type=, element_indices=None), value=True, read_only=False, path='controllers.QB2.drive.awg.status')"\>status | True |  | Enable output |
      | , collection_type=, element_indices=None), value=5.78e-07, read_only=False, path='controllers.QB2.drive.awg.trigger_delay')"\>trigger_delay | 578 | ns | Delay to correct trigger skew |
      | , collection_type=, element_indices=None), value=2400000000.0, read_only=True, path='controllers.QB2.drive.awg.sampling_rate')"\>sampling_rate | 2 400 | MHz | Sampling rate |
      | , collection_type=, element_indices=None), value=16, read_only=True, path='controllers.QB2.drive.awg.instruction_duration_granularity')"\>instruction_duration_granularity | 16 | samples | Instruction duration granularity |
      | , collection_type=, element_indices=None), value='hdawg', read_only=True, path='controllers.QB2.drive.awg.device_type')"\>device_type | "hdawg" |  | Device type |

      - mixer_correction: (Name: "QB2\_\_drive.awg.mixer_correction", class:SettingNode) 4
        |  |  |  |  |
        |:---|----|:---|:---|
        | , collection_type=, element_indices=None), value=0.0, read_only=False, path='controllers.QB2.drive.awg.mixer_correction.dc_bias_q')"\>dc_bias_q | 0 | V | LO suppression DC bias Q |
        | , collection_type=, element_indices=None), value=0.0, read_only=False, path='controllers.QB2.drive.awg.mixer_correction.phase_imbalance')"\>phase_imbalance | 0 | rad | I-Q phase imbalance |
        | , collection_type=, element_indices=None), value=1.0, read_only=False, path='controllers.QB2.drive.awg.mixer_correction.amplitude_imbalance')"\>amplitude_imbalance | 1 |  | Amplitude imbalance |
        | , collection_type=, element_indices=None), value=0.0, read_only=False, path='controllers.QB2.drive.awg.mixer_correction.dc_bias_i')"\>dc_bias_i | 0 | V | LO suppression DC bias I |
      - continuous_wave: (Name: "QB2\_\_drive.awg.continuous_wave", class:SettingNode) 4
        |  |  |  |  |
        |:---|----|:---|:---|
        | , collection_type=, element_indices=None), value=0.0, read_only=False, path='controllers.QB2.drive.awg.continuous_wave.amplitude')"\>amplitude | 0 |  | CW output amplitude scale |
        | , collection_type=, element_indices=None), value=False, read_only=False, path='controllers.QB2.drive.awg.continuous_wave.enabled')"\>enabled | False |  | Continuous wave mode enabled |
  - flux: (Name: "QB2\_\_flux", class:SettingNode) 2
    |  |  |  |  |
    |:---|----|:---|:---|
    | , collection_type=, element_indices=None), value=3.0517694540765916e-05, read_only=True, path='controllers.QB2.flux.voltage_resolution')"\>voltage_resolution | 30.5177 | μV | Bias voltage resolution |
    | , collection_type=, element_indices=None), value=-0.6240347913573094, read_only=False, path='controllers.QB2.flux.voltage')"\>voltage | -624.035 | mV | Bias voltage |
- QB3: (Name: "QB3", class:SettingNode) 1
  - drive: (Name: "QB3\_\_drive", class:SettingNode) 2
    |  |  |  |  |
    |:---|----|:---|:---|
    | , collection_type=, element_indices=None), value=False, read_only=False, path='controllers.QB3.drive.continuous_wave_enabled')"\>continuous_wave_enabled | False |  | Enable continuous wave mode |
    | , collection_type=, element_indices=None), value=True, read_only=False, path='controllers.QB3.drive.status')"\>status | True |  | Output on |
    | , collection_type=, element_indices=None), value=1.0, read_only=False, path='controllers.QB3.drive.continuous_wave_amplitude')"\>continuous_wave_amplitude | 1 |  | Scaling factor for CW output amplitude |
    | , collection_type=, element_indices=None), value=4097440314.279422, read_only=False, path='controllers.QB3.drive.frequency')"\>frequency | 4 097.44 | MHz | Frequency |

    - local_oscillator: (Name: "QB3\_\_drive.local_oscillator", class:SettingNode) 3
      |  |  |  |  |
      |:---|----|:---|:---|
      | , collection_type=, element_indices=None), value=None, read_only=False, path='controllers.QB3.drive.local_oscillator.phase')"\>phase | not set/auto | deg | Phase |
      | , collection_type=, element_indices=None), value=15, read_only=False, path='controllers.QB3.drive.local_oscillator.power')"\>power | 15 | dBm | Power |
      | , collection_type=, element_indices=None), value=False, read_only=False, path='controllers.QB3.drive.local_oscillator.status')"\>status | False |  | Output on |
      | , collection_type=, element_indices=None), value=None, read_only=False, path='controllers.QB3.drive.local_oscillator.frequency')"\>frequency | not set/auto | Hz | LO frequency |
    - awg: (Name: "QB3\_\_drive.awg", class:SettingNode) 3
      |  |  |  |  |
      |:---|----|:---|:---|
      | , collection_type=, element_indices=None), value=\[\], read_only=True, path='controllers.QB3.drive.awg.feedback_sources')"\>feedback_sources | \[ \] |  | Available feedback signal sources |
      | , collection_type=, element_indices=None), value=2.0, read_only=False, path='controllers.QB3.drive.awg.output_range')"\>output_range | 2 | V | DAC output range |
      | , collection_type=, element_indices=None), value=-295000000.0, read_only=False, path='controllers.QB3.drive.awg.intermediate_frequency')"\>intermediate_frequency | -295 | MHz | IQ intermediate frequency |
      | , collection_type=, element_indices=None), value=16, read_only=True, path='controllers.QB3.drive.awg.instruction_duration_min')"\>instruction_duration_min | 16 | samples | Minimum instruction duration |
      | , collection_type=, element_indices=None), value=True, read_only=False, path='controllers.QB3.drive.awg.status')"\>status | True |  | Enable output |
      | , collection_type=, element_indices=None), value=6.87e-07, read_only=False, path='controllers.QB3.drive.awg.trigger_delay')"\>trigger_delay | 687 | ns | Delay to correct trigger skew |
      | , collection_type=, element_indices=None), value=2400000000.0, read_only=True, path='controllers.QB3.drive.awg.sampling_rate')"\>sampling_rate | 2 400 | MHz | Sampling rate |
      | , collection_type=, element_indices=None), value=16, read_only=True, path='controllers.QB3.drive.awg.instruction_duration_granularity')"\>instruction_duration_granularity | 16 | samples | Instruction duration granularity |
      | , collection_type=, element_indices=None), value='hdawg', read_only=True, path='controllers.QB3.drive.awg.device_type')"\>device_type | "hdawg" |  | Device type |

      - mixer_correction: (Name: "QB3\_\_drive.awg.mixer_correction", class:SettingNode) 4
        |  |  |  |  |
        |:---|----|:---|:---|
        | , collection_type=, element_indices=None), value=0.0, read_only=False, path='controllers.QB3.drive.awg.mixer_correction.dc_bias_q')"\>dc_bias_q | 0 | V | LO suppression DC bias Q |
        | , collection_type=, element_indices=None), value=0.0, read_only=False, path='controllers.QB3.drive.awg.mixer_correction.phase_imbalance')"\>phase_imbalance | 0 | rad | I-Q phase imbalance |
        | , collection_type=, element_indices=None), value=1.0, read_only=False, path='controllers.QB3.drive.awg.mixer_correction.amplitude_imbalance')"\>amplitude_imbalance | 1 |  | Amplitude imbalance |
        | , collection_type=, element_indices=None), value=0.0, read_only=False, path='controllers.QB3.drive.awg.mixer_correction.dc_bias_i')"\>dc_bias_i | 0 | V | LO suppression DC bias I |
      - continuous_wave: (Name: "QB3\_\_drive.awg.continuous_wave", class:SettingNode) 4
        |  |  |  |  |
        |:---|----|:---|:---|
        | , collection_type=, element_indices=None), value=0.0, read_only=False, path='controllers.QB3.drive.awg.continuous_wave.amplitude')"\>amplitude | 0 |  | CW output amplitude scale |
        | , collection_type=, element_indices=None), value=False, read_only=False, path='controllers.QB3.drive.awg.continuous_wave.enabled')"\>enabled | False |  | Continuous wave mode enabled |
  - flux: (Name: "QB3\_\_flux", class:SettingNode) 2
    |  |  |  |  |
    |:---|----|:---|:---|
    | , collection_type=, element_indices=None), value=3.0517694540765916e-05, read_only=True, path='controllers.QB3.flux.voltage_resolution')"\>voltage_resolution | 30.5177 | μV | Bias voltage resolution |
    | , collection_type=, element_indices=None), value=0.5618562620999104, read_only=False, path='controllers.QB3.flux.voltage')"\>voltage | 561.856 | mV | Bias voltage |
- QB4: (Name: "QB4", class:SettingNode) 1
  - drive: (Name: "QB4\_\_drive", class:SettingNode) 2
    |  |  |  |  |
    |:---|----|:---|:---|
    | , collection_type=, element_indices=None), value=False, read_only=False, path='controllers.QB4.drive.continuous_wave_enabled')"\>continuous_wave_enabled | False |  | Enable continuous wave mode |
    | , collection_type=, element_indices=None), value=True, read_only=False, path='controllers.QB4.drive.status')"\>status | True |  | Output on |
    | , collection_type=, element_indices=None), value=1.0, read_only=False, path='controllers.QB4.drive.continuous_wave_amplitude')"\>continuous_wave_amplitude | 1 |  | Scaling factor for CW output amplitude |
    | , collection_type=, element_indices=None), value=3895637797.115004, read_only=False, path='controllers.QB4.drive.frequency')"\>frequency | 3 895.64 | MHz | Frequency |

    - local_oscillator: (Name: "QB4\_\_drive.local_oscillator", class:SettingNode) 3
      |  |  |  |  |
      |:---|----|:---|:---|
      | , collection_type=, element_indices=None), value=None, read_only=False, path='controllers.QB4.drive.local_oscillator.phase')"\>phase | not set/auto | deg | Phase |
      | , collection_type=, element_indices=None), value=15, read_only=False, path='controllers.QB4.drive.local_oscillator.power')"\>power | 15 | dBm | Power |
      | , collection_type=, element_indices=None), value=False, read_only=False, path='controllers.QB4.drive.local_oscillator.status')"\>status | False |  | Output on |
      | , collection_type=, element_indices=None), value=None, read_only=False, path='controllers.QB4.drive.local_oscillator.frequency')"\>frequency | not set/auto | Hz | LO frequency |
    - awg: (Name: "QB4\_\_drive.awg", class:SettingNode) 3
      |  |  |  |  |
      |:---|----|:---|:---|
      | , collection_type=, element_indices=None), value=\[\], read_only=True, path='controllers.QB4.drive.awg.feedback_sources')"\>feedback_sources | \[ \] |  | Available feedback signal sources |
      | , collection_type=, element_indices=None), value=2.0, read_only=False, path='controllers.QB4.drive.awg.output_range')"\>output_range | 2 | V | DAC output range |
      | , collection_type=, element_indices=None), value=-295000000.0, read_only=False, path='controllers.QB4.drive.awg.intermediate_frequency')"\>intermediate_frequency | -295 | MHz | IQ intermediate frequency |
      | , collection_type=, element_indices=None), value=16, read_only=True, path='controllers.QB4.drive.awg.instruction_duration_min')"\>instruction_duration_min | 16 | samples | Minimum instruction duration |
      | , collection_type=, element_indices=None), value=True, read_only=False, path='controllers.QB4.drive.awg.status')"\>status | True |  | Enable output |
      | , collection_type=, element_indices=None), value=5.84e-07, read_only=False, path='controllers.QB4.drive.awg.trigger_delay')"\>trigger_delay | 584 | ns | Delay to correct trigger skew |
      | , collection_type=, element_indices=None), value=2400000000.0, read_only=True, path='controllers.QB4.drive.awg.sampling_rate')"\>sampling_rate | 2 400 | MHz | Sampling rate |
      | , collection_type=, element_indices=None), value=16, read_only=True, path='controllers.QB4.drive.awg.instruction_duration_granularity')"\>instruction_duration_granularity | 16 | samples | Instruction duration granularity |
      | , collection_type=, element_indices=None), value='hdawg', read_only=True, path='controllers.QB4.drive.awg.device_type')"\>device_type | "hdawg" |  | Device type |

      - mixer_correction: (Name: "QB4\_\_drive.awg.mixer_correction", class:SettingNode) 4
        |  |  |  |  |
        |:---|----|:---|:---|
        | , collection_type=, element_indices=None), value=0.0, read_only=False, path='controllers.QB4.drive.awg.mixer_correction.dc_bias_q')"\>dc_bias_q | 0 | V | LO suppression DC bias Q |
        | , collection_type=, element_indices=None), value=0.0, read_only=False, path='controllers.QB4.drive.awg.mixer_correction.phase_imbalance')"\>phase_imbalance | 0 | rad | I-Q phase imbalance |
        | , collection_type=, element_indices=None), value=1.0, read_only=False, path='controllers.QB4.drive.awg.mixer_correction.amplitude_imbalance')"\>amplitude_imbalance | 1 |  | Amplitude imbalance |
        | , collection_type=, element_indices=None), value=0.0, read_only=False, path='controllers.QB4.drive.awg.mixer_correction.dc_bias_i')"\>dc_bias_i | 0 | V | LO suppression DC bias I |
      - continuous_wave: (Name: "QB4\_\_drive.awg.continuous_wave", class:SettingNode) 4
        |  |  |  |  |
        |:---|----|:---|:---|
        | , collection_type=, element_indices=None), value=0.0, read_only=False, path='controllers.QB4.drive.awg.continuous_wave.amplitude')"\>amplitude | 0 |  | CW output amplitude scale |
        | , collection_type=, element_indices=None), value=False, read_only=False, path='controllers.QB4.drive.awg.continuous_wave.enabled')"\>enabled | False |  | Continuous wave mode enabled |
  - flux: (Name: "QB4\_\_flux", class:SettingNode) 2
    |  |  |  |  |
    |:---|----|:---|:---|
    | , collection_type=, element_indices=None), value=3.0517694540765916e-05, read_only=True, path='controllers.QB4.flux.voltage_resolution')"\>voltage_resolution | 30.5177 | μV | Bias voltage resolution |
    | , collection_type=, element_indices=None), value=0.6465238319459756, read_only=False, path='controllers.QB4.flux.voltage')"\>voltage | 646.524 | mV | Bias voltage |
- QB5: (Name: "QB5", class:SettingNode) 1
  - drive: (Name: "QB5\_\_drive", class:SettingNode) 2
    |  |  |  |  |
    |:---|----|:---|:---|
    | , collection_type=, element_indices=None), value=False, read_only=False, path='controllers.QB5.drive.continuous_wave_enabled')"\>continuous_wave_enabled | False |  | Enable continuous wave mode |
    | , collection_type=, element_indices=None), value=True, read_only=False, path='controllers.QB5.drive.status')"\>status | True |  | Output on |
    | , collection_type=, element_indices=None), value=1.0, read_only=False, path='controllers.QB5.drive.continuous_wave_amplitude')"\>continuous_wave_amplitude | 1 |  | Scaling factor for CW output amplitude |
    | , collection_type=, element_indices=None), value=3897780416.464923, read_only=False, path='controllers.QB5.drive.frequency')"\>frequency | 3 897.78 | MHz | Frequency |

    - local_oscillator: (Name: "QB5\_\_drive.local_oscillator", class:SettingNode) 3
      |  |  |  |  |
      |:---|----|:---|:---|
      | , collection_type=, element_indices=None), value=None, read_only=False, path='controllers.QB5.drive.local_oscillator.phase')"\>phase | not set/auto | deg | Phase |
      | , collection_type=, element_indices=None), value=15, read_only=False, path='controllers.QB5.drive.local_oscillator.power')"\>power | 15 | dBm | Power |
      | , collection_type=, element_indices=None), value=False, read_only=False, path='controllers.QB5.drive.local_oscillator.status')"\>status | False |  | Output on |
      | , collection_type=, element_indices=None), value=None, read_only=False, path='controllers.QB5.drive.local_oscillator.frequency')"\>frequency | not set/auto | Hz | LO frequency |
    - awg: (Name: "QB5\_\_drive.awg", class:SettingNode) 3
      |  |  |  |  |
      |:---|----|:---|:---|
      | , collection_type=, element_indices=None), value=\[\], read_only=True, path='controllers.QB5.drive.awg.feedback_sources')"\>feedback_sources | \[ \] |  | Available feedback signal sources |
      | , collection_type=, element_indices=None), value=2.0, read_only=False, path='controllers.QB5.drive.awg.output_range')"\>output_range | 2 | V | DAC output range |
      | , collection_type=, element_indices=None), value=-295000000.0, read_only=False, path='controllers.QB5.drive.awg.intermediate_frequency')"\>intermediate_frequency | -295 | MHz | IQ intermediate frequency |
      | , collection_type=, element_indices=None), value=16, read_only=True, path='controllers.QB5.drive.awg.instruction_duration_min')"\>instruction_duration_min | 16 | samples | Minimum instruction duration |
      | , collection_type=, element_indices=None), value=True, read_only=False, path='controllers.QB5.drive.awg.status')"\>status | True |  | Enable output |
      | , collection_type=, element_indices=None), value=5.52e-07, read_only=False, path='controllers.QB5.drive.awg.trigger_delay')"\>trigger_delay | 552 | ns | Delay to correct trigger skew |
      | , collection_type=, element_indices=None), value=2400000000.0, read_only=True, path='controllers.QB5.drive.awg.sampling_rate')"\>sampling_rate | 2 400 | MHz | Sampling rate |
      | , collection_type=, element_indices=None), value=16, read_only=True, path='controllers.QB5.drive.awg.instruction_duration_granularity')"\>instruction_duration_granularity | 16 | samples | Instruction duration granularity |
      | , collection_type=, element_indices=None), value='hdawg', read_only=True, path='controllers.QB5.drive.awg.device_type')"\>device_type | "hdawg" |  | Device type |

      - mixer_correction: (Name: "QB5\_\_drive.awg.mixer_correction", class:SettingNode) 4
        |  |  |  |  |
        |:---|----|:---|:---|
        | , collection_type=, element_indices=None), value=0.0, read_only=False, path='controllers.QB5.drive.awg.mixer_correction.dc_bias_q')"\>dc_bias_q | 0 | V | LO suppression DC bias Q |
        | , collection_type=, element_indices=None), value=0.0, read_only=False, path='controllers.QB5.drive.awg.mixer_correction.phase_imbalance')"\>phase_imbalance | 0 | rad | I-Q phase imbalance |
        | , collection_type=, element_indices=None), value=1.0, read_only=False, path='controllers.QB5.drive.awg.mixer_correction.amplitude_imbalance')"\>amplitude_imbalance | 1 |  | Amplitude imbalance |
        | , collection_type=, element_indices=None), value=0.0, read_only=False, path='controllers.QB5.drive.awg.mixer_correction.dc_bias_i')"\>dc_bias_i | 0 | V | LO suppression DC bias I |
      - continuous_wave: (Name: "QB5\_\_drive.awg.continuous_wave", class:SettingNode) 4
        |  |  |  |  |
        |:---|----|:---|:---|
        | , collection_type=, element_indices=None), value=0.0, read_only=False, path='controllers.QB5.drive.awg.continuous_wave.amplitude')"\>amplitude | 0 |  | CW output amplitude scale |
        | , collection_type=, element_indices=None), value=False, read_only=False, path='controllers.QB5.drive.awg.continuous_wave.enabled')"\>enabled | False |  | Continuous wave mode enabled |
  - flux: (Name: "QB5\_\_flux", class:SettingNode) 2
    |  |  |  |  |
    |:---|----|:---|:---|
    | , collection_type=, element_indices=None), value=3.0517694540765916e-05, read_only=True, path='controllers.QB5.flux.voltage_resolution')"\>voltage_resolution | 30.5177 | μV | Bias voltage resolution |
    | , collection_type=, element_indices=None), value=-0.957553309769913, read_only=False, path='controllers.QB5.flux.voltage')"\>voltage | -957.553 | mV | Bias voltage |
- TC-3-5: (Name: "TC-3-5", class:SettingNode) 1
  - flux: (Name: "TC-3-5\_\_flux", class:SettingNode) 2
    |  |  |  |  |
    |:---|----|:---|:---|
    | , collection_type=, element_indices=None), value=9e-05, read_only=True, path='controllers.TC-3-5.flux.voltage_resolution')"\>voltage_resolution | 90 | μV | Bias voltage resolution |
    | , collection_type=, element_indices=None), value=-0.0375797785615527, read_only=False, path='controllers.TC-3-5.flux.voltage')"\>voltage | -37.5798 | mV | Bias voltage |

    - awg: (Name: "TC-3-5\_\_flux.awg", class:SettingNode) 3
      |  |  |  |  |
      |:---|----|:---|:---|
      | , collection_type=, element_indices=None), value=16, read_only=True, path='controllers.TC-3-5.flux.awg.instruction_duration_granularity')"\>instruction_duration_granularity | 16 | samples | Instruction duration granularity |
      | , collection_type=, element_indices=None), value=1.0, read_only=False, path='controllers.TC-3-5.flux.awg.output_range')"\>output_range | 1 | V | DAC output range |
      | , collection_type=, element_indices=None), value=16, read_only=True, path='controllers.TC-3-5.flux.awg.instruction_duration_min')"\>instruction_duration_min | 16 | samples | Minimum instruction duration |
      | , collection_type=, element_indices=None), value=True, read_only=False, path='controllers.TC-3-5.flux.awg.status')"\>status | True |  | Enable output |
      | , collection_type=, element_indices=None), value=5.3e-07, read_only=False, path='controllers.TC-3-5.flux.awg.trigger_delay')"\>trigger_delay | 530 | ns | Delay to correct trigger skew |
      | , collection_type=, element_indices=None), value=2400000000.0, read_only=True, path='controllers.TC-3-5.flux.awg.sampling_rate')"\>sampling_rate | 2 400 | MHz | Sampling rate |
      | , collection_type=, element_indices=None), value=\[\], read_only=True, path='controllers.TC-3-5.flux.awg.feedback_sources')"\>feedback_sources | \[ \] |  | Available feedback signal sources |
      | , collection_type=, element_indices=None), value='hdawg', read_only=True, path='controllers.TC-3-5.flux.awg.device_type')"\>device_type | "hdawg" |  | Device type |

      - precompensation: (Name: "TC-3-5\_\_flux.awg.precompensation", class:SettingNode) 4
        |  |  |  |  |
        |:---|----|:---|:---|
        | , collection_type=, element_indices=None), value=\[1.0\], read_only=False, path='controllers.TC-3-5.flux.awg.precompensation.fir_kernel')"\>fir_kernel | \[ 1 \] |  | FIR impulse response samples |
        | , collection_type=, element_indices=None), value=\[-0.00355422, -0.00826827, -0.01511899, -0.01599437\], read_only=False, path='controllers.TC-3-5.flux.awg.precompensation.amplitudes')"\>amplitudes | \[ -0.00355422 , -0.00826827 , -0.015119 , -0.0159944 \] |  | Precompensation amplitudes |
        | , collection_type=, element_indices=None), value=\[2.97626632e-06, 6.70519295e-07, 1.11508326e-07, 2.45160204e-08\], read_only=False, path='controllers.TC-3-5.flux.awg.precompensation.timeconstants')"\>timeconstants | \[ 2.97627e-06 , 6.70519e-07 , 1.11508e-07 , 2.4516e-08 \] |  | Precompensation timeconstants |
- TC-2-3: (Name: "TC-2-3", class:SettingNode) 1
  - flux: (Name: "TC-2-3\_\_flux", class:SettingNode) 2
    |  |  |  |  |
    |:---|----|:---|:---|
    | , collection_type=, element_indices=None), value=9e-05, read_only=True, path='controllers.TC-2-3.flux.voltage_resolution')"\>voltage_resolution | 90 | μV | Bias voltage resolution |
    | , collection_type=, element_indices=None), value=-0.07037831440337904, read_only=False, path='controllers.TC-2-3.flux.voltage')"\>voltage | -70.3783 | mV | Bias voltage |

    - awg: (Name: "TC-2-3\_\_flux.awg", class:SettingNode) 3
      |  |  |  |  |
      |:---|----|:---|:---|
      | , collection_type=, element_indices=None), value=16, read_only=True, path='controllers.TC-2-3.flux.awg.instruction_duration_granularity')"\>instruction_duration_granularity | 16 | samples | Instruction duration granularity |
      | , collection_type=, element_indices=None), value=1.0, read_only=False, path='controllers.TC-2-3.flux.awg.output_range')"\>output_range | 1 | V | DAC output range |
      | , collection_type=, element_indices=None), value=16, read_only=True, path='controllers.TC-2-3.flux.awg.instruction_duration_min')"\>instruction_duration_min | 16 | samples | Minimum instruction duration |
      | , collection_type=, element_indices=None), value=True, read_only=False, path='controllers.TC-2-3.flux.awg.status')"\>status | True |  | Enable output |
      | , collection_type=, element_indices=None), value=5e-07, read_only=False, path='controllers.TC-2-3.flux.awg.trigger_delay')"\>trigger_delay | 500 | ns | Delay to correct trigger skew |
      | , collection_type=, element_indices=None), value=2400000000.0, read_only=True, path='controllers.TC-2-3.flux.awg.sampling_rate')"\>sampling_rate | 2 400 | MHz | Sampling rate |
      | , collection_type=, element_indices=None), value=\[\], read_only=True, path='controllers.TC-2-3.flux.awg.feedback_sources')"\>feedback_sources | \[ \] |  | Available feedback signal sources |
      | , collection_type=, element_indices=None), value='hdawg', read_only=True, path='controllers.TC-2-3.flux.awg.device_type')"\>device_type | "hdawg" |  | Device type |

      - precompensation: (Name: "TC-2-3\_\_flux.awg.precompensation", class:SettingNode) 4
        |  |  |  |  |
        |:---|----|:---|:---|
        | , collection_type=, element_indices=None), value=\[1.0\], read_only=False, path='controllers.TC-2-3.flux.awg.precompensation.fir_kernel')"\>fir_kernel | \[ 1 \] |  | FIR impulse response samples |
        | , collection_type=, element_indices=None), value=\[-0.00362817, -0.00929551, -0.01643672, -0.01374434\], read_only=False, path='controllers.TC-2-3.flux.awg.precompensation.amplitudes')"\>amplitudes | \[ -0.00362817 , -0.00929551 , -0.0164367 , -0.0137443 \] |  | Precompensation amplitudes |
        | , collection_type=, element_indices=None), value=\[1.49010655e-06, 5.32712049e-07, 8.8959505e-08, 2.34737149e-08\], read_only=False, path='controllers.TC-2-3.flux.awg.precompensation.timeconstants')"\>timeconstants | \[ 1.49011e-06 , 5.32712e-07 , 8.89595e-08 , 2.34737e-08 \] |  | Precompensation timeconstants |
- TC-1-3: (Name: "TC-1-3", class:SettingNode) 1
  - flux: (Name: "TC-1-3\_\_flux", class:SettingNode) 2
    |  |  |  |  |
    |:---|----|:---|:---|
    | , collection_type=, element_indices=None), value=9e-05, read_only=True, path='controllers.TC-1-3.flux.voltage_resolution')"\>voltage_resolution | 90 | μV | Bias voltage resolution |
    | , collection_type=, element_indices=None), value=-0.0839404128487973, read_only=False, path='controllers.TC-1-3.flux.voltage')"\>voltage | -83.9404 | mV | Bias voltage |

    - awg: (Name: "TC-1-3\_\_flux.awg", class:SettingNode) 3
      |  |  |  |  |
      |:---|----|:---|:---|
      | , collection_type=, element_indices=None), value=16, read_only=True, path='controllers.TC-1-3.flux.awg.instruction_duration_granularity')"\>instruction_duration_granularity | 16 | samples | Instruction duration granularity |
      | , collection_type=, element_indices=None), value=1.0, read_only=False, path='controllers.TC-1-3.flux.awg.output_range')"\>output_range | 1 | V | DAC output range |
      | , collection_type=, element_indices=None), value=16, read_only=True, path='controllers.TC-1-3.flux.awg.instruction_duration_min')"\>instruction_duration_min | 16 | samples | Minimum instruction duration |
      | , collection_type=, element_indices=None), value=True, read_only=False, path='controllers.TC-1-3.flux.awg.status')"\>status | True |  | Enable output |
      | , collection_type=, element_indices=None), value=5e-07, read_only=False, path='controllers.TC-1-3.flux.awg.trigger_delay')"\>trigger_delay | 500 | ns | Delay to correct trigger skew |
      | , collection_type=, element_indices=None), value=2400000000.0, read_only=True, path='controllers.TC-1-3.flux.awg.sampling_rate')"\>sampling_rate | 2 400 | MHz | Sampling rate |
      | , collection_type=, element_indices=None), value=\[\], read_only=True, path='controllers.TC-1-3.flux.awg.feedback_sources')"\>feedback_sources | \[ \] |  | Available feedback signal sources |
      | , collection_type=, element_indices=None), value='hdawg', read_only=True, path='controllers.TC-1-3.flux.awg.device_type')"\>device_type | "hdawg" |  | Device type |

      - precompensation: (Name: "TC-1-3\_\_flux.awg.precompensation", class:SettingNode) 4
        |  |  |  |  |
        |:---|----|:---|:---|
        | , collection_type=, element_indices=None), value=\[1.0\], read_only=False, path='controllers.TC-1-3.flux.awg.precompensation.fir_kernel')"\>fir_kernel | \[ 1 \] |  | FIR impulse response samples |
        | , collection_type=, element_indices=None), value=\[-0.01139311, -0.05833012, -0.0036522, -0.01364289\], read_only=False, path='controllers.TC-1-3.flux.awg.precompensation.amplitudes')"\>amplitudes | \[ -0.0113931 , -0.0583301 , -0.0036522 , -0.0136429 \] |  | Precompensation amplitudes |
        | , collection_type=, element_indices=None), value=\[7.2259895e-07, 2.10931568e-08, 5.68728855e-08, 1.09834893e-07\], read_only=False, path='controllers.TC-1-3.flux.awg.precompensation.timeconstants')"\>timeconstants | \[ 7.22599e-07 , 2.10932e-08 , 5.68729e-08 , 1.09835e-07 \] |  | Precompensation timeconstants |
- TC-3-4: (Name: "TC-3-4", class:SettingNode) 1
  - flux: (Name: "TC-3-4\_\_flux", class:SettingNode) 2
    |  |  |  |  |
    |:---|----|:---|:---|
    | , collection_type=, element_indices=None), value=9e-05, read_only=True, path='controllers.TC-3-4.flux.voltage_resolution')"\>voltage_resolution | 90 | μV | Bias voltage resolution |
    | , collection_type=, element_indices=None), value=-0.1076191936327977, read_only=False, path='controllers.TC-3-4.flux.voltage')"\>voltage | -107.619 | mV | Bias voltage |

    - awg: (Name: "TC-3-4\_\_flux.awg", class:SettingNode) 3
      |  |  |  |  |
      |:---|----|:---|:---|
      | , collection_type=, element_indices=None), value=16, read_only=True, path='controllers.TC-3-4.flux.awg.instruction_duration_granularity')"\>instruction_duration_granularity | 16 | samples | Instruction duration granularity |
      | , collection_type=, element_indices=None), value=1.0, read_only=False, path='controllers.TC-3-4.flux.awg.output_range')"\>output_range | 1 | V | DAC output range |
      | , collection_type=, element_indices=None), value=16, read_only=True, path='controllers.TC-3-4.flux.awg.instruction_duration_min')"\>instruction_duration_min | 16 | samples | Minimum instruction duration |
      | , collection_type=, element_indices=None), value=True, read_only=False, path='controllers.TC-3-4.flux.awg.status')"\>status | True |  | Enable output |
      | , collection_type=, element_indices=None), value=5.3e-07, read_only=False, path='controllers.TC-3-4.flux.awg.trigger_delay')"\>trigger_delay | 530 | ns | Delay to correct trigger skew |
      | , collection_type=, element_indices=None), value=2400000000.0, read_only=True, path='controllers.TC-3-4.flux.awg.sampling_rate')"\>sampling_rate | 2 400 | MHz | Sampling rate |
      | , collection_type=, element_indices=None), value=\[\], read_only=True, path='controllers.TC-3-4.flux.awg.feedback_sources')"\>feedback_sources | \[ \] |  | Available feedback signal sources |
      | , collection_type=, element_indices=None), value='hdawg', read_only=True, path='controllers.TC-3-4.flux.awg.device_type')"\>device_type | "hdawg" |  | Device type |

      - precompensation: (Name: "TC-3-4\_\_flux.awg.precompensation", class:SettingNode) 4
        |  |  |  |  |
        |:---|----|:---|:---|
        | , collection_type=, element_indices=None), value=\[1.0\], read_only=False, path='controllers.TC-3-4.flux.awg.precompensation.fir_kernel')"\>fir_kernel | \[ 1 \] |  | FIR impulse response samples |
        | , collection_type=, element_indices=None), value=\[-0.00200975, -0.01081126\], read_only=False, path='controllers.TC-3-4.flux.awg.precompensation.amplitudes')"\>amplitudes | \[ -0.00200975 , -0.0108113 \] |  | Precompensation amplitudes |
        | , collection_type=, element_indices=None), value=\[2.56322554e-06, 5.73498401e-07\], read_only=False, path='controllers.TC-3-4.flux.awg.precompensation.timeconstants')"\>timeconstants | \[ 2.56323e-06 , 5.73498e-07 \] |  | Precompensation timeconstants |
- PL_RO-1: (Name: "PL_RO-1", class:SettingNode) 1
  - readout: (Name: "PL_RO-1\_\_readout", class:SettingNode) 2
    |  |  |  |  |
    |:---|----|:---|:---|
    | , collection_type=, element_indices=None), value=16, read_only=True, path='controllers.PL_RO-1.readout.instruction_duration_granularity')"\>instruction_duration_granularity | 16 | samples | Instruction duration granularity |
    | , collection_type=, element_indices=None), value=5450000000.0, read_only=False, path='controllers.PL_RO-1.readout.center_frequency')"\>center_frequency | 5 450 | MHz | Center frequency |
    | , collection_type=, element_indices=None), value=0, read_only=True, path='controllers.PL_RO-1.readout.integration_start_dead_time')"\>integration_start_dead_time | 0 | samples | Minimum delay for readout pulses |
    | , collection_type=, element_indices=None), value=0.75, read_only=False, path='controllers.PL_RO-1.readout.output_range')"\>output_range | 750 | mV | Signal output max range |
    | , collection_type=, element_indices=None), value=32, read_only=True, path='controllers.PL_RO-1.readout.instruction_duration_min')"\>instruction_duration_min | 32 | samples | Minimum instruction duration |
    | , collection_type=, element_indices=None), value=5e-07, read_only=False, path='controllers.PL_RO-1.readout.trigger_delay')"\>trigger_delay | 5e-07 |  | Delay after trigger |
    | , collection_type=, element_indices=None), value=1.5, read_only=False, path='controllers.PL_RO-1.readout.input_range')"\>input_range | 1.5 | V | Signal input range |
    | , collection_type=, element_indices=None), value=1800000000.0, read_only=True, path='controllers.PL_RO-1.readout.sampling_rate')"\>sampling_rate | 1 800 | MHz | Sampling rate |
    | , collection_type=, element_indices=None), value=256, read_only=True, path='controllers.PL_RO-1.readout.integration_stop_dead_time')"\>integration_stop_dead_time | 256 | samples | Minimum delay after integration |
    | , collection_type=, element_indices=None), value='uhfqa', read_only=True, path='controllers.PL_RO-1.readout.device_type')"\>device_type | "uhfqa" |  | Device type |

    - local_oscillator: (Name: "PL_RO-1\_\_readout.local_oscillator", class:SettingNode) 3
      |  |  |  |  |
      |:---|----|:---|:---|
      | , collection_type=, element_indices=None), value=None, read_only=False, path='controllers.PL_RO-1.readout.local_oscillator.phase')"\>phase | not set/auto | deg | Phase |
      | , collection_type=, element_indices=None), value=13, read_only=False, path='controllers.PL_RO-1.readout.local_oscillator.power')"\>power | 13 | dBm | Power |
      | , collection_type=, element_indices=None), value=True, read_only=False, path='controllers.PL_RO-1.readout.local_oscillator.status')"\>status | True |  | Output on |
      | , collection_type=, element_indices=None), value=None, read_only=False, path='controllers.PL_RO-1.readout.local_oscillator.frequency')"\>frequency | not set/auto | Hz | LO frequency |
  - twpa: (Name: "PL_RO-1\_\_twpa", class:SettingNode) 2
    |  |  |  |  |
    |:---|----|:---|:---|
    | , collection_type=, element_indices=None), value='TWPA_ST_B2_44D', read_only=True, path='controllers.PL_RO-1.twpa.twpa_id')"\>twpa_id | "TWPA_ST_B2_44D" |  | TWPA ID |
    | , collection_type=, element_indices=None), value=0.56, read_only=False, path='controllers.PL_RO-1.twpa.voltage_1')"\>voltage_1 | 560 | mV | Output voltage channel 10 |
    | , collection_type=, element_indices=None), value=True, read_only=False, path='controllers.PL_RO-1.twpa.status')"\>status | True |  | Output on |
    | , collection_type=, element_indices=None), value=14.5, read_only=False, path='controllers.PL_RO-1.twpa.power')"\>power | 14.5 | dBm | Power |
    | , collection_type=, element_indices=None), value=300, read_only=True, path='controllers.PL_RO-1.twpa.resistance')"\>resistance | 300 | ohm | Resistance |
    | , collection_type=, element_indices=None), value=-0.56, read_only=False, path='controllers.PL_RO-1.twpa.voltage_2')"\>voltage_2 | -560 | mV | Output voltage channel 11 |
    | , collection_type=, element_indices=None), value=10150000000.0, read_only=False, path='controllers.PL_RO-1.twpa.frequency')"\>frequency | 10.15 | GHz | LO frequency |
- counter: (Name: "counter", class:SettingNode) 1
  |  |  |  |  |
  |:---|----|:---|:---|
  | , collection_type=, element_indices=None), value=\[\], read_only=False, path='controllers.counter.subscribed_channels')"\>subscribed_channels | \[ \] |  | Subscribed channels |
  | , collection_type=, element_indices=None), value=None, read_only=True, path='controllers.counter.result')"\>result | not set/auto |  | Multi-qubit state probabilities |
- options: (Name: "options", class:SettingNode) 1
  |  |  |  |  |
  |:---|----|:---|:---|
  | , collection_type=, element_indices=None), value=100000, read_only=False, path='controllers.options.max_playlist_chunk_size')"\>max_playlist_chunk_size | 100 000 |  | Max playlist chunk size |
  | , collection_type=, element_indices=None), value=None, read_only=False, path='controllers.options.iterator')"\>iterator | not set/auto |  | Iteration |
  | , collection_type=, element_indices=None), value='QB3\_\_drive.awg', read_only=False, path='controllers.options.trigger_master')"\>trigger_master | "QB3\_\_drive.awg" |  | Trigger master controller name |
  | , collection_type=, element_indices=None), value=1000, read_only=False, path='controllers.options.averaging_bins')"\>averaging_bins | 1 000 |  | Number of bins to average the repetititions |
  | , collection_type=, element_indices=None), value=1.12e-06, read_only=False, path='controllers.options.end_delay')"\>end_delay | 1.12 | μs | Time after segment until next trigger |
  | , collection_type=, element_indices=None), value=1, read_only=False, path='controllers.options.chunk_size_multiplicity')"\>chunk_size_multiplicity | 1 |  | Chunk size multiplicity |
  | , collection_type=, element_indices=None), value=1000, read_only=False, path='controllers.options.playlist_repeats')"\>playlist_repeats | 1 000 |  | Number of playlist repeats |

```
# Further zoom into the drive node of QB1
settings.controllers.QB1.drive
```

(QB1\_\_drive)

QB1\_\_drive: (Name: "QB1\_\_drive", class:SettingNode) 0

|  |  |  |  |
|:---|----|:---|:---|
| , collection_type=, element_indices=None), value=False, read_only=False, path='controllers.QB1.drive.continuous_wave_enabled')"\>continuous_wave_enabled | False |  | Enable continuous wave mode |
| , collection_type=, element_indices=None), value=True, read_only=False, path='controllers.QB1.drive.status')"\>status | True |  | Output on |
| , collection_type=, element_indices=None), value=1.0, read_only=False, path='controllers.QB1.drive.continuous_wave_amplitude')"\>continuous_wave_amplitude | 1 |  | Scaling factor for CW output amplitude |
| , collection_type=, element_indices=None), value=3893001948.56542, read_only=False, path='controllers.QB1.drive.frequency')"\>frequency | 3 893 | MHz | Frequency |

- local_oscillator: (Name: "QB1\_\_drive.local_oscillator", class:SettingNode) 1
  |  |  |  |  |
  |:---|----|:---|:---|
  | , collection_type=, element_indices=None), value=None, read_only=False, path='controllers.QB1.drive.local_oscillator.phase')"\>phase | not set/auto | deg | Phase |
  | , collection_type=, element_indices=None), value=15, read_only=False, path='controllers.QB1.drive.local_oscillator.power')"\>power | 15 | dBm | Power |
  | , collection_type=, element_indices=None), value=False, read_only=False, path='controllers.QB1.drive.local_oscillator.status')"\>status | False |  | Output on |
  | , collection_type=, element_indices=None), value=None, read_only=False, path='controllers.QB1.drive.local_oscillator.frequency')"\>frequency | not set/auto | Hz | LO frequency |
- awg: (Name: "QB1\_\_drive.awg", class:SettingNode) 1
  |  |  |  |  |
  |:---|----|:---|:---|
  | , collection_type=, element_indices=None), value=\[\], read_only=True, path='controllers.QB1.drive.awg.feedback_sources')"\>feedback_sources | \[ \] |  | Available feedback signal sources |
  | , collection_type=, element_indices=None), value=2.0, read_only=False, path='controllers.QB1.drive.awg.output_range')"\>output_range | 2 | V | DAC output range |
  | , collection_type=, element_indices=None), value=-295000000.0, read_only=False, path='controllers.QB1.drive.awg.intermediate_frequency')"\>intermediate_frequency | -295 | MHz | IQ intermediate frequency |
  | , collection_type=, element_indices=None), value=16, read_only=True, path='controllers.QB1.drive.awg.instruction_duration_min')"\>instruction_duration_min | 16 | samples | Minimum instruction duration |
  | , collection_type=, element_indices=None), value=True, read_only=False, path='controllers.QB1.drive.awg.status')"\>status | True |  | Enable output |
  | , collection_type=, element_indices=None), value=5.24e-07, read_only=False, path='controllers.QB1.drive.awg.trigger_delay')"\>trigger_delay | 524 | ns | Delay to correct trigger skew |
  | , collection_type=, element_indices=None), value=2400000000.0, read_only=True, path='controllers.QB1.drive.awg.sampling_rate')"\>sampling_rate | 2 400 | MHz | Sampling rate |
  | , collection_type=, element_indices=None), value=16, read_only=True, path='controllers.QB1.drive.awg.instruction_duration_granularity')"\>instruction_duration_granularity | 16 | samples | Instruction duration granularity |
  | , collection_type=, element_indices=None), value='hdawg', read_only=True, path='controllers.QB1.drive.awg.device_type')"\>device_type | "hdawg" |  | Device type |

  - mixer_correction: (Name: "QB1\_\_drive.awg.mixer_correction", class:SettingNode) 2
    |  |  |  |  |
    |:---|----|:---|:---|
    | , collection_type=, element_indices=None), value=0.0, read_only=False, path='controllers.QB1.drive.awg.mixer_correction.dc_bias_q')"\>dc_bias_q | 0 | V | LO suppression DC bias Q |
    | , collection_type=, element_indices=None), value=0.0, read_only=False, path='controllers.QB1.drive.awg.mixer_correction.phase_imbalance')"\>phase_imbalance | 0 | rad | I-Q phase imbalance |
    | , collection_type=, element_indices=None), value=1.0, read_only=False, path='controllers.QB1.drive.awg.mixer_correction.amplitude_imbalance')"\>amplitude_imbalance | 1 |  | Amplitude imbalance |
    | , collection_type=, element_indices=None), value=0.0, read_only=False, path='controllers.QB1.drive.awg.mixer_correction.dc_bias_i')"\>dc_bias_i | 0 | V | LO suppression DC bias I |
  - continuous_wave: (Name: "QB1\_\_drive.awg.continuous_wave", class:SettingNode) 2
    |  |  |  |  |
    |:---|----|:---|:---|
    | , collection_type=, element_indices=None), value=0.0, read_only=False, path='controllers.QB1.drive.awg.continuous_wave.amplitude')"\>amplitude | 0 |  | CW output amplitude scale |
    | , collection_type=, element_indices=None), value=False, read_only=False, path='controllers.QB1.drive.awg.continuous_wave.enabled')"\>enabled | False |  | Continuous wave mode enabled |

The operation point can be modified by manipulating the settings values. For demonstration purposes, we now set the drive frequency of QB1 to 4 MHz. It should be noted that running a quantum computation with a modified operation point will probably result in non-sense data, unless you know what you’re doing! (But don’t worry, it is safe in the sense that other users will not be affected by the change you made).

```
# Set the QB1 drive frequency to 4 MHz
settings.controllers.QB1.drive.frequency = 4e6

# Print the drive node again to confirm the changed value
settings.controllers.QB1.drive
```

(QB1\_\_drive)

QB1\_\_drive: (Name: "QB1\_\_drive", class:SettingNode) 0

|  |  |  |  |
|:---|----|:---|:---|
| , collection_type=, element_indices=None), value=False, read_only=False, path='controllers.QB1.drive.continuous_wave_enabled')"\>continuous_wave_enabled | False |  | Enable continuous wave mode |
| , collection_type=, element_indices=None), value=True, read_only=False, path='controllers.QB1.drive.status')"\>status | True |  | Output on |
| , collection_type=, element_indices=None), value=1.0, read_only=False, path='controllers.QB1.drive.continuous_wave_amplitude')"\>continuous_wave_amplitude | 1 |  | Scaling factor for CW output amplitude |
| , collection_type=, element_indices=None), value=4000000.0, read_only=False, path='controllers.QB1.drive.frequency')"\>frequency | 4 000 | kHz | Frequency |

- local_oscillator: (Name: "QB1\_\_drive.local_oscillator", class:SettingNode) 1
  |  |  |  |  |
  |:---|----|:---|:---|
  | , collection_type=, element_indices=None), value=None, read_only=False, path='controllers.QB1.drive.local_oscillator.phase')"\>phase | not set/auto | deg | Phase |
  | , collection_type=, element_indices=None), value=15, read_only=False, path='controllers.QB1.drive.local_oscillator.power')"\>power | 15 | dBm | Power |
  | , collection_type=, element_indices=None), value=False, read_only=False, path='controllers.QB1.drive.local_oscillator.status')"\>status | False |  | Output on |
  | , collection_type=, element_indices=None), value=None, read_only=False, path='controllers.QB1.drive.local_oscillator.frequency')"\>frequency | not set/auto | Hz | LO frequency |
- awg: (Name: "QB1\_\_drive.awg", class:SettingNode) 1
  |  |  |  |  |
  |:---|----|:---|:---|
  | , collection_type=, element_indices=None), value=\[\], read_only=True, path='controllers.QB1.drive.awg.feedback_sources')"\>feedback_sources | \[ \] |  | Available feedback signal sources |
  | , collection_type=, element_indices=None), value=2.0, read_only=False, path='controllers.QB1.drive.awg.output_range')"\>output_range | 2 | V | DAC output range |
  | , collection_type=, element_indices=None), value=-295000000.0, read_only=False, path='controllers.QB1.drive.awg.intermediate_frequency')"\>intermediate_frequency | -295 | MHz | IQ intermediate frequency |
  | , collection_type=, element_indices=None), value=16, read_only=True, path='controllers.QB1.drive.awg.instruction_duration_min')"\>instruction_duration_min | 16 | samples | Minimum instruction duration |
  | , collection_type=, element_indices=None), value=True, read_only=False, path='controllers.QB1.drive.awg.status')"\>status | True |  | Enable output |
  | , collection_type=, element_indices=None), value=5.24e-07, read_only=False, path='controllers.QB1.drive.awg.trigger_delay')"\>trigger_delay | 524 | ns | Delay to correct trigger skew |
  | , collection_type=, element_indices=None), value=2400000000.0, read_only=True, path='controllers.QB1.drive.awg.sampling_rate')"\>sampling_rate | 2 400 | MHz | Sampling rate |
  | , collection_type=, element_indices=None), value=16, read_only=True, path='controllers.QB1.drive.awg.instruction_duration_granularity')"\>instruction_duration_granularity | 16 | samples | Instruction duration granularity |
  | , collection_type=, element_indices=None), value='hdawg', read_only=True, path='controllers.QB1.drive.awg.device_type')"\>device_type | "hdawg" |  | Device type |

  - mixer_correction: (Name: "QB1\_\_drive.awg.mixer_correction", class:SettingNode) 2
    |  |  |  |  |
    |:---|----|:---|:---|
    | , collection_type=, element_indices=None), value=0.0, read_only=False, path='controllers.QB1.drive.awg.mixer_correction.dc_bias_q')"\>dc_bias_q | 0 | V | LO suppression DC bias Q |
    | , collection_type=, element_indices=None), value=0.0, read_only=False, path='controllers.QB1.drive.awg.mixer_correction.phase_imbalance')"\>phase_imbalance | 0 | rad | I-Q phase imbalance |
    | , collection_type=, element_indices=None), value=1.0, read_only=False, path='controllers.QB1.drive.awg.mixer_correction.amplitude_imbalance')"\>amplitude_imbalance | 1 |  | Amplitude imbalance |
    | , collection_type=, element_indices=None), value=0.0, read_only=False, path='controllers.QB1.drive.awg.mixer_correction.dc_bias_i')"\>dc_bias_i | 0 | V | LO suppression DC bias I |
  - continuous_wave: (Name: "QB1\_\_drive.awg.continuous_wave", class:SettingNode) 2
    |  |  |  |  |
    |:---|----|:---|:---|
    | , collection_type=, element_indices=None), value=0.0, read_only=False, path='controllers.QB1.drive.awg.continuous_wave.amplitude')"\>amplitude | 0 |  | CW output amplitude scale |
    | , collection_type=, element_indices=None), value=False, read_only=False, path='controllers.QB1.drive.awg.continuous_wave.enabled')"\>enabled | False |  | Continuous wave mode enabled |

What about the other subnodes in the settings tree?

The `gates` and `gate_definitions` nodes concern the quantum operation calibration and definitions. The `gates` node includes calibration data for each operation (gate) defined in the compiler and their physcial implementations. As an example, the phased rotation (PRX) gate is defined on each qubit and is used to perform most single-qubit operations such as `X180`, `X90`, `Y180` and `Hadamard`. The calibration data for PRX for a single qubit consists of the `duration` of the associated microwave pulse, the I and Q pulse amplitudes and any additional parameters of the I and Q waveforms.

The `gate_definitions` node contains useful metadata for each operation and its implementations (for example the arity of the operation – how many locus components it acts upon – or whether the operation or its implementation is symmetric with respect to the order of its locus components). Most of this data is read only, meaning it cannot be changed like the drive frequency in the example above. However, an important customisable setting here is the default implementation information, which defines the implementation used for the quantum operation (in case the user does not manually specify another implementation in a compiler pass).

```
# Store the PRX default implementation name in a variable -- this is what we would be using to create PRX in circuits
default_prx = settings.gate_definitions.prx.default_implementation.value

# Print the associated calibration data for QB1
settings.gates.prx[default_prx].QB1
```

(gates.prx.drag_crf_sx.QB1)

gates.prx.drag_crf_sx.QB1: (Name: "gates.prx.drag_crf_sx.QB1", class:SettingNode) 0

|  |  |  |  |
|:---|----|:---|:---|
| , collection_type=, element_indices=None), value=2e-08, read_only=False, path='gates.prx.drag_crf_sx.QB1.duration')"\>duration | 20 | ns | pi pulse duration |
| , collection_type=, element_indices=None), value=0.46340708239125256, read_only=False, path='gates.prx.drag_crf_sx.QB1.amplitude_i')"\>amplitude_i | 0.463407 |  | pi pulse I channel amplitude |
| , collection_type=, element_indices=None), value=-0.0170831801697053, read_only=False, path='gates.prx.drag_crf_sx.QB1.amplitude_q')"\>amplitude_q | -0.0170832 |  | pi pulse Q channel amplitude |
| , collection_type=, element_indices=None), value=-0.005068370789407436, read_only=False, path='gates.prx.drag_crf_sx.QB1.rz_before')"\>rz_before | -5.06837 | mrad | RZ before IQ pulse |
| , collection_type=, element_indices=None), value=-0.005068370789407436, read_only=False, path='gates.prx.drag_crf_sx.QB1.rz_after')"\>rz_after | -5.06837 | mrad | RZ after IQ pulse |
| , collection_type=, element_indices=None), value=2e-08, read_only=False, path='gates.prx.drag_crf_sx.QB1.full_width')"\>full_width | 20 | ns | full_width of crf |
| , collection_type=, element_indices=None), value=0.0, read_only=False, path='gates.prx.drag_crf_sx.QB1.center_offset')"\>center_offset | 0 | s | center_offset of crf |

```
# SettingNode contains many utility methods. We could have fetched the same default implementation node by just calling:
default_prx_node = settings.get_gate_node_for_locus("prx", "QB1")

# Change a setting here (again, this would probably cause the gate to malfunction, but there is no need to worry about that for now)
default_prx_node.amplitude_i = 0.2

# Print the node and see the change taking effect
default_prx_node
```

(gates.prx.drag_crf_sx.QB1)

gates.prx.drag_crf_sx.QB1: (Name: "gates.prx.drag_crf_sx.QB1", class:SettingNode) 0

|  |  |  |  |
|:---|----|:---|:---|
| , collection_type=, element_indices=None), value=2e-08, read_only=False, path='gates.prx.drag_crf_sx.QB1.duration')"\>duration | 20 | ns | pi pulse duration |
| , collection_type=, element_indices=None), value=0.2, read_only=False, path='gates.prx.drag_crf_sx.QB1.amplitude_i')"\>amplitude_i | 0.2 |  | pi pulse I channel amplitude |
| , collection_type=, element_indices=None), value=-0.0170831801697053, read_only=False, path='gates.prx.drag_crf_sx.QB1.amplitude_q')"\>amplitude_q | -0.0170832 |  | pi pulse Q channel amplitude |
| , collection_type=, element_indices=None), value=-0.005068370789407436, read_only=False, path='gates.prx.drag_crf_sx.QB1.rz_before')"\>rz_before | -5.06837 | mrad | RZ before IQ pulse |
| , collection_type=, element_indices=None), value=-0.005068370789407436, read_only=False, path='gates.prx.drag_crf_sx.QB1.rz_after')"\>rz_after | -5.06837 | mrad | RZ after IQ pulse |
| , collection_type=, element_indices=None), value=2e-08, read_only=False, path='gates.prx.drag_crf_sx.QB1.full_width')"\>full_width | 20 | ns | full_width of crf |
| , collection_type=, element_indices=None), value=0.0, read_only=False, path='gates.prx.drag_crf_sx.QB1.center_offset')"\>center_offset | 0 | s | center_offset of crf |

```
# Change the default implementation of PRX
settings.gate_definitions.prx.default_implementation = "drag_gaussian_sx"

# Print the default QB1 PRX calibration node to see that it points to a different place this time (note that this other implementation is
# probably not calibrated yet, so we would have to provide the calibration data before using it).
settings.get_gate_node_for_locus("prx", "QB1")
```

(gates.prx.drag_gaussian_sx.QB1)

gates.prx.drag_gaussian_sx.QB1: (Name: "gates.prx.drag_gaussian_sx.QB1", class:SettingNode) 0

|  |  |  |  |
|:---|----|:---|:---|
| , collection_type=, element_indices=None), value=None, read_only=False, path='gates.prx.drag_gaussian_sx.QB1.duration')"\>duration | not set/auto | s | pi pulse duration |
| , collection_type=, element_indices=None), value=None, read_only=False, path='gates.prx.drag_gaussian_sx.QB1.amplitude_i')"\>amplitude_i | not set/auto |  | pi pulse I channel amplitude |
| , collection_type=, element_indices=None), value=None, read_only=False, path='gates.prx.drag_gaussian_sx.QB1.amplitude_q')"\>amplitude_q | not set/auto |  | pi pulse Q channel amplitude |
| , collection_type=, element_indices=None), value=None, read_only=False, path='gates.prx.drag_gaussian_sx.QB1.rz_before')"\>rz_before | not set/auto | rad | RZ before IQ pulse |
| , collection_type=, element_indices=None), value=None, read_only=False, path='gates.prx.drag_gaussian_sx.QB1.rz_after')"\>rz_after | not set/auto | rad | RZ after IQ pulse |
| , collection_type=, element_indices=None), value=None, read_only=False, path='gates.prx.drag_gaussian_sx.QB1.full_width')"\>full_width | not set/auto | s | full_width of tg |
| , collection_type=, element_indices=None), value=0.0, read_only=False, path='gates.prx.drag_gaussian_sx.QB1.center_offset')"\>center_offset | 0 | s | center_offset of tg |

Of the final two top-level subnodes `settings.stages` contains settings for the compilation loop itself (more about that later), whereas `settings.characterization` contains auxiliary information about QPU components and gates operating on them (for example `settings.characterization.model` contains certain estimated qubit and coupler Hamiltonian parameters).

## Compiling and running circuits

Now that we have an idea how the operation point is defined and manipulated, we can use it to compile a circuit, send the job for execution and view the returned data.

NOTE: `qiskit_to_iqm` is a utility function that combines `IQMClient.get_standard_compiler()` and transforming the Qiskit circuits into the IQM format in a single function call

```
backend = IQMProvider(
    "<IQM Server URL>",
    quantum_computer="<quantum computer name>",
    token="<your API token>",
).get_backend()

# Define a Qiskit circuit that produces a 3-qubit GHZ state
qc = QuantumCircuit(3, 3)
qc.h(0)
qc.cx(0, 1)
qc.cx(0, 2)
qc.measure_all()

# Transpile the circuit and convert it to the IQM representation
qc_transpiled = transpile(qc, backend=backend, layout_method='sabre', optimization_level=3)
circuits, compiler = qiskit_to_iqm(backend, qc_transpiled)

# Set the number of shots
shots = 1000
settings = compiler.get_settings(circuits=circuits)
settings.set_shots(shots)

# Use the original settings into compile
run_definition, context = compiler.compile(circuits=circuits, settings=settings)

# Visualize the compiled pulse schedule per control channel
HTML(inspect_playlist(run_definition.sweep_definition.playlist, [0]))
```

```
# Send the job for execution and plot the results
job_tracker = backend.client.submit_playlist(run_definition, context=context)
job_tracker.wait_for_completion()
qiskit_result = sweep_job_to_qiskit(job_tracker, shots=shots)

print(f"Qiskit result counts:\n{qiskit_result.get_counts()}\n")
visualization.plot_histogram(qiskit_result.get_counts())
```

```
[06-09 13:30:16;I] Waiting for job 019eabee-d28b-7631-b508-db3f8ea65927 to finish...
```

```
Qiskit result counts:
{'000': 430, '101': 26, '111': 359, '011': 59, '100': 34, '010': 47, '110': 40, '001': 5}
```

![](https://docs.iqm.tech/4.7/iqm-pulla/_images/6c3b979204deb0e583816fe00b7690e607779e369f0f00ae2decf9f705fabd5c.png)

## Complex readout

For the `constant` implementation of the `measure` operation, the readout type is controlled by the `acquisition_type` parameter, which is set to `"threshold"` by default. The full key in the calibration set dictionary is `f"gates.measure_fidelity.constant.{QUBIT}.acquisition_type"`, where `QUBIT` is the physical qubit name.

```
qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

backend = IQMProvider(
    "<IQM Server URL>",
    quantum_computer="<quantum computer name>",
    token="<your API token>",
).get_backend()

qc_transpiled = transpile(qc, backend=backend, layout_method='sabre', optimization_level=3)
circuits, compiler = qiskit_to_iqm(backend, qc_transpiled)
settings = compiler.get_settings(circuits=circuits)

# set shots to 10 as we just want to see the complex results
settings.set_shots(10)

# Change the terminal measure acquisition type to 'complex' for all qubits in the chip
for qubit in compiler.chip_topology.qubits_sorted:
    settings.get_gate_node_for_locus("measure_fidelity", qubit).acquisition_type = "complex"

job_definition, context = compiler.compile(circuits=circuits, settings=settings)
job_tracker = backend.client.submit_playlist(job_definition, context=context)
job_tracker.wait_for_completion()

# IQMClient.submit_playlist() returns a JobTracker object.
# The measurements are obtained using JobTracker.result() after JobTracker.wait_for_completion().

print(f"Raw results:\n{job_tracker.result().circuit_measurement_results}\n")
```

```
[06-09 13:30:21;I] Waiting for job 019eabee-e72c-74a2-85d7-8dd4a0923ff9 to finish...
```

```
Raw results:
[{'meas_2_1_0': [[(-0.01446533203125+0.03345675998263889j)], [(-0.012139892578125+0.032324896918402776j)], [(0.02777099609375+0.05449286566840278j)], [(-0.003976101345486111+0.039198811848958334j)], [(-0.020553249782986113+0.034390597873263894j)], [(-0.016215684678819446+0.039168294270833334j)], [(-0.011928982204861112+0.04144151475694444j)], [(0.02636650933159722+0.008171251085069445j)], [(-0.008439805772569444+0.04045274522569445j)], [(0.023914930555555557+0.007651095920138889j)]], 'meas_2_1_1': [[(0.007065836588541667+0.05047810872395834j)], [(0.009318712022569444+0.04854465060763889j)], [(0.043381754557291666+0.04046969943576389j)], [(0.013862440321180556+0.04511650933159722j)], [(0.014105224609375001+0.043074544270833334j)], [(0.006251356336805556+0.04327799479166667j)], [(0.004951985677083334+0.04745279947916667j)], [(0.035287136501736115+0.04382120768229167j)], [(0.019968668619791668+0.05060356987847223j)], [(0.038001166449652776+0.0524658203125j)]]}]
```
