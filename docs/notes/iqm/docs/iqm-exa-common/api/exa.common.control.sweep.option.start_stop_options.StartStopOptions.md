> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.start_stop_options.StartStopOptions.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.start_stop_options.StartStopOptions.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 500c5771c750602a4d400305cc0770eec83aab096118a4f19a780c4c7850963d.

# StartStopOptions

Module: [`exa.common.control.sweep.option.start_stop_options`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.start_stop_options.html#module-exa.common.control.sweep.option.start_stop_options "exa.common.control.sweep.option.start_stop_options")

*class* StartStopOptions(*start*, *stop*, *count=None*, *step=None*)  
Bases: [`SweepOptions`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.sweep_options.SweepOptions.html#exa.common.control.sweep.option.sweep_options.SweepOptions "exa.common.control.sweep.option.sweep_options.SweepOptions")

Range generation options.

Values are generated over the interval from start to stop. For linear sweep range the number of generated values can be based either on count or step. In case count is empty and step is not, step is used for calculating count. For exponential sweep range only count is used.

Attributes

|  |  |
|----|----|
| [`count`](#exa.common.control.sweep.option.start_stop_options.StartStopOptions.count "exa.common.control.sweep.option.start_stop_options.StartStopOptions.count") | Number of values to generate. |
| [`data`](#exa.common.control.sweep.option.start_stop_options.StartStopOptions.data "exa.common.control.sweep.option.start_stop_options.StartStopOptions.data") | List of values for `parameter` |
| [`step`](#exa.common.control.sweep.option.start_stop_options.StartStopOptions.step "exa.common.control.sweep.option.start_stop_options.StartStopOptions.step") | Size of spacing between values. |
| [`start`](#exa.common.control.sweep.option.start_stop_options.StartStopOptions.start "exa.common.control.sweep.option.start_stop_options.StartStopOptions.start") | Starting value of interval. |
| [`stop`](#exa.common.control.sweep.option.start_stop_options.StartStopOptions.stop "exa.common.control.sweep.option.start_stop_options.StartStopOptions.stop") | Stopping value of interval. |

Methods

Parameters:  
- **start** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") *\|* [*complex*](https://docs.python.org/3.11/library/functions.html#complex "(in Python v3.11)"))

- **stop** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") *\|* [*complex*](https://docs.python.org/3.11/library/functions.html#complex "(in Python v3.11)"))

- **count** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*)

- **step** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") *\|* [*complex*](https://docs.python.org/3.11/library/functions.html#complex "(in Python v3.11)") *\|* *None*)

start*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") \| [complex](https://docs.python.org/3.11/library/functions.html#complex "(in Python v3.11)")*  
Starting value of interval.

stop*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") \| [complex](https://docs.python.org/3.11/library/functions.html#complex "(in Python v3.11)")*  
Stopping value of interval.

count*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")* *= None*  
Number of values to generate. Must be non-negative. If count and step are empty, the default value of count is [`exa.common.control.sweep.option.constants.DEFAULT_COUNT`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.constants.DEFAULT_COUNT.html#exa.common.control.sweep.option.constants.DEFAULT_COUNT "exa.common.control.sweep.option.constants.DEFAULT_COUNT").

step*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") \| [complex](https://docs.python.org/3.11/library/functions.html#complex "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")* *= None*  
Size of spacing between values. Must be non-zero. If both count and step are not empty, only count is used

*property* data*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") \| [complex](https://docs.python.org/3.11/library/functions.html#complex "(in Python v3.11)")\]*  
List of values for `parameter`

Inheritance

![Inheritance diagram of exa.common.control.sweep.option.start_stop_options.StartStopOptions](https://docs.iqm.tech/4.7/iqm-exa-common/_images/inheritance-b9966336be196c0b8c3a08f1951b2e6affd2b20f.png)
