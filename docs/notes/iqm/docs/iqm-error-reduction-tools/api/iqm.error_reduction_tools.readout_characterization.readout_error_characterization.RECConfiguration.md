> Full piece: [https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration.html](https://docs.iqm.tech/4.7/iqm-error-reduction-tools/api/iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 75a9966a1b56146a0741e9936f30ad87e3e33d0e52bdae42578e8ef04ddcf57d.

# iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration

*class* iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration(*num_circuits=50*, *shots=10000*, *qubits=None*, *seed=None*, *symmetrize=True*, *equatorial_randomization=True*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Configuration for a readout error characterization (REC) experiment.

All parameters have sensible defaults so `RECConfiguration()` is valid and immediately usable.

Attributes

|  |  |
|----|----|
| [`equatorial_randomization`](#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration.equatorial_randomization "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration.equatorial_randomization") | When `True`, randomizes the phase angle of every X gate to average out coherent phase errors. |
| [`num_circuits`](#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration.num_circuits "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration.num_circuits") | Number of calibration circuits to generate |
| [`qubits`](#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration.qubits "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration.qubits") | Qubit names to characterize. |
| [`seed`](#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration.seed "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration.seed") | Random seed for reproducible circuit generation. |
| [`shots`](#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration.shots "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration.shots") | Total measurement shots distributed across all circuits. |
| [`symmetrize`](#iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration.symmetrize "iqm.error_reduction_tools.readout_characterization.readout_error_characterization.RECConfiguration.symmetrize") | When `True`, generates complementary preparation pairs so that each qubit is prepared in `|0⟩` and `|1⟩` equally often. |

Methods

|                 |                     |
|-----------------|---------------------|
| `__eq__`(other) | Return self==value. |
| `__repr__`()    | Return repr(self).  |

Parameters:  
- **num_circuits** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **shots** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **qubits** ([*list*](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*)

- **seed** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*)

- **symmetrize** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

- **equatorial_randomization** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

num_circuits*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")* *= 50*  
Number of calibration circuits to generate

shots*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")* *= 10000*  
Total measurement shots distributed across all circuits. Each circuit receives `shots // num_circuits` shots.

qubits*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\] \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")* *= None*  
Qubit names to characterize.

Non-operational qubits (those without a calibrated `measure` gate) are always excluded: they cannot be characterized or have readout error mitigation applied.

- `None` (default): qubits are not pinned. When used standalone, this characterizes every operational qubit on the QPU; in the `REMWorkflow` it lets the workflow infer the qubits from the measured qubits of the input circuits.

- `list[str]`: characterize exactly these qubit names, minus any that are not operational.

seed*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")* *= None*  
Random seed for reproducible circuit generation. `None` produces non-deterministic results.

symmetrize*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")* *= True*  
When `True`, generates complementary preparation pairs so that each qubit is prepared in `|0⟩` and `|1⟩` equally often.

equatorial_randomization*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")* *= True*  
When `True`, randomizes the phase angle of every X gate to average out coherent phase errors.
