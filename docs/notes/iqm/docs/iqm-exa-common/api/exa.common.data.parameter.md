> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 027e6199868c9ee52824532d9c2d76856f7da0d63c1801847a8df1c67df51c4d.

# parameter

Full path: exa.common.data.parameter

Physical quantities and instrument settings.

A basic data structure in EXA is the [`Parameter`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Parameter.html#exa.common.data.parameter.Parameter "exa.common.data.parameter.Parameter"), which represents a single variable. The variable can be a high-level or low-level control knob of an instrument such as the amplitude of a pulse or a control voltage; a physical quantity such as resonance frequency; or an abstract concept like the number of averages in a measurement.

The Parameter is a simple structure with a name, label, unit and a datatype without much functionality. The [`Setting`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Setting.html#exa.common.data.parameter.Setting "exa.common.data.parameter.Setting") combines a Parameter and a *value* of the corresponding type. Like Parameters, Settings are lightweight objects that contain information but don’t do anything by themselves.

```
>>> from exa.common.data.parameter import Parameter, Setting
>>> p = Parameter('qubit_1.drive.pi_pulse.duration', 'Duration', 's')
>>> s = Setting(p, 1e-6)
>>> print(s)
Setting(Duration = 1e-06 s)
```

The Settings are immutable, which means that the value can’t be changed, we can only make a copy with another value. When assigning a new value to a Setting, the datatype of the value is validated against the expected datatype of the parameter.

```
>>> setting1 = p.set(500)  # an alternative way to transform a parameter into a setting
>>> setting2 = setting1.update(300)
>>> setting1.value
500
>>> setting2.value
300
>>> setting1.parameter == setting2.parameter
True
```

Module Attributes

|  |  |
|----|----|
| [`SettingValue`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.SettingValue.html#exa.common.data.parameter.SettingValue "exa.common.data.parameter.SettingValue") | Setting.value type system is wider than the one used by Observations. |
| [`SourceType`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.SourceType.html#exa.common.data.parameter.SourceType "exa.common.data.parameter.SourceType") | Type for Setting sources. |

Functions

|  |  |
|----|----|
| [`setting_value_to_observation`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.setting_value_to_observation.html#exa.common.data.parameter.setting_value_to_observation "exa.common.data.parameter.setting_value_to_observation")(value) | Temporary helper function for converting Setting values to Observation values. |

Classes

|  |  |
|----|----|
| [`CollectionType`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.CollectionType.html#exa.common.data.parameter.CollectionType "exa.common.data.parameter.CollectionType") | Parameter collection type. |
| [`DataType`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.DataType.html#exa.common.data.parameter.DataType "exa.common.data.parameter.DataType") | Parameter data type. |
| [`Parameter`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Parameter.html#exa.common.data.parameter.Parameter "exa.common.data.parameter.Parameter") | A basic data structure that represents a single variable. |
| [`Setting`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Setting.html#exa.common.data.parameter.Setting "exa.common.data.parameter.Setting") | Physical quantity represented as a Parameter attached to a numerical value. |
| [`Sweep`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.data.parameter.Sweep.html#exa.common.data.parameter.Sweep "exa.common.data.parameter.Sweep") | Base immutable class for sweeps. |

Inheritance

![Inheritance diagram of exa.common.data.parameter](https://docs.iqm.tech/4.7/iqm-exa-common/_images/inheritance-6d1300088fd6ca32879338646d4b917914bf6a2a.png)
