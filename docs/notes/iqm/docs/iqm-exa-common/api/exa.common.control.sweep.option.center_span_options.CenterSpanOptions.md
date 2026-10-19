> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.center_span_options.CenterSpanOptions.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.center_span_options.CenterSpanOptions.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 fce177dcd61899effe02e1e20bfd815263fd7cde7aa1d4ffc57721f68e4d9f75.

# CenterSpanOptions

Module: [`exa.common.control.sweep.option.center_span_options`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.center_span_options.html#module-exa.common.control.sweep.option.center_span_options "exa.common.control.sweep.option.center_span_options")

*class* CenterSpanOptions(*center*, *span*, *count=None*, *step=None*, *asc=True*)  
Bases: [`SweepOptions`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.sweep_options.SweepOptions.html#exa.common.control.sweep.option.sweep_options.SweepOptions "exa.common.control.sweep.option.sweep_options.SweepOptions")

Range generation options.

Values are generated over the interval with the center center and the size of span. For linear sweep range the number of generated values can be based either on count or step. In case count is empty and step is not, step is used for calculating count. For exponential sweep range only count is used.

Attributes

|  |  |
|----|----|
| [`asc`](#exa.common.control.sweep.option.center_span_options.CenterSpanOptions.asc "exa.common.control.sweep.option.center_span_options.CenterSpanOptions.asc") | Order of generated values. |
| [`count`](#exa.common.control.sweep.option.center_span_options.CenterSpanOptions.count "exa.common.control.sweep.option.center_span_options.CenterSpanOptions.count") | Number of values to generate. |
| [`data`](#exa.common.control.sweep.option.center_span_options.CenterSpanOptions.data "exa.common.control.sweep.option.center_span_options.CenterSpanOptions.data") | List of values for `parameter` |
| [`step`](#exa.common.control.sweep.option.center_span_options.CenterSpanOptions.step "exa.common.control.sweep.option.center_span_options.CenterSpanOptions.step") | Size of spacing between values. |
| [`center`](#exa.common.control.sweep.option.center_span_options.CenterSpanOptions.center "exa.common.control.sweep.option.center_span_options.CenterSpanOptions.center") | Value of interval center. |
| [`span`](#exa.common.control.sweep.option.center_span_options.CenterSpanOptions.span "exa.common.control.sweep.option.center_span_options.CenterSpanOptions.span") | Size of the interval. |

Methods

Parameters:  
- **center** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") *\|* [*complex*](https://docs.python.org/3.11/library/functions.html#complex "(in Python v3.11)"))

- **span** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") *\|* [*complex*](https://docs.python.org/3.11/library/functions.html#complex "(in Python v3.11)"))

- **count** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* *None*)

- **step** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") *\|* [*complex*](https://docs.python.org/3.11/library/functions.html#complex "(in Python v3.11)") *\|* *None*)

- **asc** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

center*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") \| [complex](https://docs.python.org/3.11/library/functions.html#complex "(in Python v3.11)")*  
Value of interval center.

span*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") \| [complex](https://docs.python.org/3.11/library/functions.html#complex "(in Python v3.11)")*  
Size of the interval.

count*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")* *= None*  
Number of values to generate. If count and step are empty, the default value of count is [`exa.common.control.sweep.option.constants.DEFAULT_COUNT`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.constants.DEFAULT_COUNT.html#exa.common.control.sweep.option.constants.DEFAULT_COUNT "exa.common.control.sweep.option.constants.DEFAULT_COUNT").

step*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") \| [complex](https://docs.python.org/3.11/library/functions.html#complex "(in Python v3.11)") \| [None](https://docs.python.org/3.11/library/constants.html#None "(in Python v3.11)")* *= None*  
Size of spacing between values.

asc*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")* *= True*  
Order of generated values. Default to ascending

*property* data*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)") \| [complex](https://docs.python.org/3.11/library/functions.html#complex "(in Python v3.11)")\]*  
List of values for `parameter`

Inheritance

![Inheritance diagram of exa.common.control.sweep.option.center_span_options.CenterSpanOptions](https://docs.iqm.tech/4.7/iqm-exa-common/_images/inheritance-c691bfdfd982bc871f9c1e708aedebfec67eac4f.png)
