> Full piece: [https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.ExperimentDefaultsConfiguration.html](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.ExperimentDefaultsConfiguration.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 640a47bc10c699817dbb8782815681086bb119dbc43e31174951f71358dfe657.

# ExperimentDefaultsConfiguration

Module: [`iqm.cpc.core.config`](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.html#module-iqm.cpc.core.config "iqm.cpc.core.config")

*class* iqm.cpc.core.config.ExperimentDefaultsConfiguration(*config*)  
Bases: [`object`](https://docs.python.org/3.11/library/functions.html#object "(in Python v3.11)")

Configuration for a specific `Experiment` subclass.

Parameters:  
**config** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* *Any\]*) – Configuration tree for the experiment.

Attributes

|  |  |
|----|----|
| [`controllers`](#iqm.cpc.core.config.ExperimentDefaultsConfiguration.controllers "iqm.cpc.core.config.ExperimentDefaultsConfiguration.controllers") | Default controller settings. |
| [`sweeps`](#iqm.cpc.core.config.ExperimentDefaultsConfiguration.sweeps "iqm.cpc.core.config.ExperimentDefaultsConfiguration.sweeps") | Default sweeps. |

Methods

controllers*: [dict](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")\[[str](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"), [Any](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")\]*  
Default controller settings.

sweeps*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[SweepDefaultsConfiguration](https://docs.iqm.tech/4.7/iqm-pulla/api/iqm.cpc.core.config.SweepDefaultsConfiguration.html#iqm.cpc.core.config.SweepDefaultsConfiguration "iqm.cpc.core.config.SweepDefaultsConfiguration")\]*  
Default sweeps.

Inheritance

![Inheritance diagram of iqm.cpc.core.config.ExperimentDefaultsConfiguration](https://docs.iqm.tech/4.7/iqm-pulla/_images/inheritance-2f10b93d42600ab72d224e7d5688b4518173d785.png)
