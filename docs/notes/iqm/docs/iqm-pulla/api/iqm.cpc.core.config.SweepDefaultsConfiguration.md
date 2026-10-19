> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.SweepDefaultsConfiguration.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.SweepDefaultsConfiguration.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 836488b38367156951ca96f3f69c68c0537892394dc16c7902bddab6c7add413.

# SweepDefaultsConfiguration

Module: [`iqm.cpc.core.config`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.html#module-iqm.cpc.core.config "iqm.cpc.core.config")

*class* iqm.cpc.core.config.SweepDefaultsConfiguration(*config*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Default sweep configuration.

See [`convert_to_options()`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.option_converter.convert_to_options.html#exa.common.control.sweep.option.option_converter.convert_to_options "(in iqm-exa-common v29.0.0)") for the rest of the options.

Parameters:  
**config** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *Any\]*) – Sweep configuration tree.

Attributes

|  |  |
|----|----|
| [`name`](#iqm.cpc.core.config.SweepDefaultsConfiguration.name "iqm.cpc.core.config.SweepDefaultsConfiguration.name") | Sweep name. |
| [`type`](#iqm.cpc.core.config.SweepDefaultsConfiguration.type "iqm.cpc.core.config.SweepDefaultsConfiguration.type") | Sweep type. |
| [`parameter`](#iqm.cpc.core.config.SweepDefaultsConfiguration.parameter "iqm.cpc.core.config.SweepDefaultsConfiguration.parameter") | Name of the parameter being swept. |
| [`options`](#iqm.cpc.core.config.SweepDefaultsConfiguration.options "iqm.cpc.core.config.SweepDefaultsConfiguration.options") | Rest of the sweep options. |

Methods

name*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Sweep name.

type*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Sweep type.

parameter*: [str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*  
Name of the parameter being swept.

options*: [SweepOptions](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.sweep_options.SweepOptions.html#exa.common.control.sweep.option.sweep_options.SweepOptions "(in iqm-exa-common v29.0.0)")*  
Rest of the sweep options.

Inheritance

![Inheritance diagram of iqm.cpc.core.config.SweepDefaultsConfiguration](https://docs.iqm.tech/4.7/iqm-pulla/_images/inheritance-9806ffff8fd0cc2fb84dca8f02566b3761a2a65f.png)
