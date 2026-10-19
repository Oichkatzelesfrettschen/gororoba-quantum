> Full piece: [https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Waveform.html](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.Waveform.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 0797a1b0a9fe0d22635314c871d1f4e9168b00bdc6cde2baa892833ec2e561cd.

# Waveform

*class* iqm.models.playlist.waveforms.Waveform(*n_samples*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Describes the normalized shape of a real-valued control pulse.

The shape is described by a function \\f: \mathbb{R} \to \[-1, 1\]\\ that comes with an implicit sampling window. \\f\\ maps time (measured in units of the sampling window duration and relative to its center point) to the value of the pulse at that time.

Each Waveform subclass may have attributes that affect its shape. All time-like attributes are measured in units of the sampling window duration. The station method `non_timelike_attributes` may be used to define non-timelike attributes and their units (in addition to “s”, “Hz” has a special behaviour in that such attributes will be converted to the units of the inverse of duration). Providing type hints to the waveform attributes is mandatory, as they are used in parsing the information for the `GateImplementations`. Supported scalar attribute types are: `int`, `float`, `complex`, `str`, `bool`. In addition, `list[<scalar type>]` is supported for all the aforementioned scalar types, and also `numpy.ndarray`, in which case it is interpreted to contain complex numbers.

When the Waveform is used by an instrument it is typically sampled using the [`sample()`](#iqm.models.playlist.waveforms.Waveform.sample "iqm.models.playlist.waveforms.Waveform.sample") method, which converts it into an array of [`n_samples`](#iqm.models.playlist.waveforms.Waveform.n_samples "iqm.models.playlist.waveforms.Waveform.n_samples") equidistant samples, generated using the midpoint method, by evaluating the function \\f(t)\\ inside the sampling window \\t \in \[-1/2, 1/2\]\\. The instruments will discretize the values of the samples to a finite, instrument-dependent resolution, typically 14–16 bits.

Usually, it is sufficient for Waveforms to describe normalized waveforms (i.e. using the full value range \\\[-1, 1\]\\), not including a scaling prefactor in the defining expression. Instead, the scaling should be specified as a parameter of [`Instruction`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.Instruction.html#iqm.models.playlist.instructions.Instruction "iqm.models.playlist.instructions.Instruction") using the Waveform (e.g. [`IQPulse`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.IQPulse.html#iqm.models.playlist.instructions.IQPulse "iqm.models.playlist.instructions.IQPulse"), [`RealPulse`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.instructions.RealPulse.html#iqm.models.playlist.instructions.RealPulse "iqm.models.playlist.instructions.RealPulse")), thus allowing compilers to more efficiently re-use waveforms and utilize the available hardware support to perform such re-scaling in real time.

Module: [`iqm.models.playlist.waveforms`](https://docs.iqm.tech/4.7/iqm-data-definitions/api/iqm.models.playlist.waveforms.html#module-iqm.models.playlist.waveforms "iqm.models.playlist.waveforms")

Attributes

|  |  |
|----|----|
| [`n_samples`](#iqm.models.playlist.waveforms.Waveform.n_samples "iqm.models.playlist.waveforms.Waveform.n_samples") | Requested number of samples for the waveform. |

Methods

|  |  |
|----|----|
| [`non_timelike_attributes`](#iqm.models.playlist.waveforms.Waveform.non_timelike_attributes "iqm.models.playlist.waveforms.Waveform.non_timelike_attributes") | Mapping from waveform attributes to the units of their calibration data, unless that unit is second. |
| [`sample`](#iqm.models.playlist.waveforms.Waveform.sample "iqm.models.playlist.waveforms.Waveform.sample") | Sample the waveform. |

Parameters:  
**n_samples** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

n_samples*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")*  
Requested number of samples for the waveform. May be different from the duration (in samples) of the parent Instruction.

*static* non_timelike_attributes()  
Mapping from waveform attributes to the units of their calibration data, unless that unit is second.

Used to construct the parameters for the calibration data required by the waveform. By default all the waveform attributes are “timelike” (the unit for their calibration data is s). However, some waveform attributes can be dimensionless, e.g. the relative amplitudes in a sum of consisting of multiple terms, or frequency-like (calibration data has the unit ‘Hz’). If a Waveform subclass has non-timelike attributes, it needs to redefine this method.

When the Waveform is constructed, all timelike calibration data is converted to units of the sampling window duration, and all frequency-like calibration data into units of inverse sampling window duration.

Return type:  
[dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")\]

sample()  
Sample the waveform.

Contains the boilerplate code for determining the sample coordinates, the actual sampling happens in `_sample()`.

Returns:  
`self` sampled in the window \[-1/2, 1/2\]

Return type:  
*ndarray*
