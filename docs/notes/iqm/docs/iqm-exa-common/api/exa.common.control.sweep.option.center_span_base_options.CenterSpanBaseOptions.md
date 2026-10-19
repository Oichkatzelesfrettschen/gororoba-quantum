> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.center_span_base_options.CenterSpanBaseOptions.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.center_span_base_options.CenterSpanBaseOptions.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 5ac568a84beb4f4b189d8c53bcf104f5f51931b59d5c82df75f54bf70b7ef7a5.

# CenterSpanBaseOptions

Module: [`exa.common.control.sweep.option.center_span_base_options`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.center_span_base_options.html#module-exa.common.control.sweep.option.center_span_base_options "exa.common.control.sweep.option.center_span_base_options")

*class* CenterSpanBaseOptions(*center*, *span*, *count=101*, *base=10*, *asc=True*)  
Bases: [`SweepOptions`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.sweep_options.SweepOptions.html#exa.common.control.sweep.option.sweep_options.SweepOptions "exa.common.control.sweep.option.sweep_options.SweepOptions")

Range generation options.

Values are generated over the interval from base power start of the range with the center center and the size of span to base power end of the range with the center center and the size of span. The number of values = count. These options are used only for exponential sweep range.

Attributes

|  |  |
|----|----|
| [`asc`](#exa.common.control.sweep.option.center_span_base_options.CenterSpanBaseOptions.asc "exa.common.control.sweep.option.center_span_base_options.CenterSpanBaseOptions.asc") | Order of generated values. |
| `base` |  |
| [`count`](#exa.common.control.sweep.option.center_span_base_options.CenterSpanBaseOptions.count "exa.common.control.sweep.option.center_span_base_options.CenterSpanBaseOptions.count") | Number of values to generate. |
| [`data`](#exa.common.control.sweep.option.center_span_base_options.CenterSpanBaseOptions.data "exa.common.control.sweep.option.center_span_base_options.CenterSpanBaseOptions.data") | List of values for `parameter` |
| [`center`](#exa.common.control.sweep.option.center_span_base_options.CenterSpanBaseOptions.center "exa.common.control.sweep.option.center_span_base_options.CenterSpanBaseOptions.center") | Value of interval center for the power. |
| [`span`](#exa.common.control.sweep.option.center_span_base_options.CenterSpanBaseOptions.span "exa.common.control.sweep.option.center_span_base_options.CenterSpanBaseOptions.span") | Size of the interval for the power |

Methods

Parameters:  
- **center** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **span** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **count** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))

- **base** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") *\|* [*float*](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)"))

- **asc** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)"))

center*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*  
Value of interval center for the power.

span*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")*  
Size of the interval for the power

count*: [int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)")* *= 101*  
Number of values to generate. Default to [`exa.common.control.sweep.option.constants.DEFAULT_COUNT`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.constants.DEFAULT_COUNT.html#exa.common.control.sweep.option.constants.DEFAULT_COUNT "exa.common.control.sweep.option.constants.DEFAULT_COUNT").

asc*: [bool](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")* *= True*  
Order of generated values. Default to ascending

*property* data*: [list](https://docs.python.org/3.11/library/stdtypes.html#list "(in Python v3.11)")\[[int](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)") \| [float](https://docs.python.org/3.11/library/functions.html#float "(in Python v3.11)")\]*  
List of values for `parameter`

Inheritance

![Inheritance diagram of exa.common.control.sweep.option.center_span_base_options.CenterSpanBaseOptions](https://docs.iqm.tech/4.7/iqm-exa-common/_images/inheritance-19881abf65da346e14ab68da5d6e74a72aa434bc.png)
