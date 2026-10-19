> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.start_stop_base_options.StartStopBaseOptions.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.start_stop_base_options.StartStopBaseOptions.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 7335943c805702d7132745f82dc3034aeb0ea033e348821d7f6b89f25ba05876.

# StartStopBaseOptions

Module: [`exa.common.control.sweep.option.start_stop_base_options`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.start_stop_base_options.html#module-exa.common.control.sweep.option.start_stop_base_options "exa.common.control.sweep.option.start_stop_base_options")

*class* StartStopBaseOptions(*start*, *stop*, *count=101*, *base=10*)  
Bases: [`SweepOptions`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.sweep_options.SweepOptions.html#exa.common.control.sweep.option.sweep_options.SweepOptions "exa.common.control.sweep.option.sweep_options.SweepOptions")

Range generation options.

Values are generated over the interval from base power start to base power stop. The number of values = count. These options are used only for exponential sweep range.

Attributes

|  |  |
|----|----|
| [`base`](#exa.common.control.sweep.option.start_stop_base_options.StartStopBaseOptions.base "exa.common.control.sweep.option.start_stop_base_options.StartStopBaseOptions.base") | Number, that is raised to the power start or stop. |
| [`count`](#exa.common.control.sweep.option.start_stop_base_options.StartStopBaseOptions.count "exa.common.control.sweep.option.start_stop_base_options.StartStopBaseOptions.count") | Number of values to generate. |
| [`data`](#exa.common.control.sweep.option.start_stop_base_options.StartStopBaseOptions.data "exa.common.control.sweep.option.start_stop_base_options.StartStopBaseOptions.data") | List of values for `parameter` |
| [`start`](#exa.common.control.sweep.option.start_stop_base_options.StartStopBaseOptions.start "exa.common.control.sweep.option.start_stop_base_options.StartStopBaseOptions.start") | The power for the start of the interval. |
| [`stop`](#exa.common.control.sweep.option.start_stop_base_options.StartStopBaseOptions.stop "exa.common.control.sweep.option.start_stop_base_options.StartStopBaseOptions.stop") | The power for the end of the interval. |

Methods

Parameters:  
- **start** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **stop** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **count** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **base** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

start*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*  
The power for the start of the interval.

stop*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*  
The power for the end of the interval.

count*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")* *= 101*  
Number of values to generate. Default to [`exa.common.control.sweep.option.constants.DEFAULT_COUNT`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.constants.DEFAULT_COUNT.html#exa.common.control.sweep.option.constants.DEFAULT_COUNT "exa.common.control.sweep.option.constants.DEFAULT_COUNT").

base*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")* *= 10*  
Number, that is raised to the power start or stop. Default to [`exa.common.control.sweep.option.constants.DEFAULT_BASE`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.constants.DEFAULT_BASE.html#exa.common.control.sweep.option.constants.DEFAULT_BASE "exa.common.control.sweep.option.constants.DEFAULT_BASE").

*property* data*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]*  
List of values for `parameter`

Inheritance

![Inheritance diagram of exa.common.control.sweep.option.start_stop_base_options.StartStopBaseOptions](https://docs.iqm.tech/4.7/iqm-exa-common/_images/inheritance-f603252eb8fddcde39550309ed29c0382eebc5f1.png)
