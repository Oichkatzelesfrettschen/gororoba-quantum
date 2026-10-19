> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.option_converter.convert_to_options.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.option_converter.convert_to_options.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 1d3c03db0ef5fbfc9488081ca3725d3869d11cfee3d887822c89473e2f6e7377.

# exa.common.control.sweep.option.option_converter.convert_to_options

convert_to_options(*config*)  
Creates one of the options object based on configuration dictionary.

- If configuration has keys `start` and `stop`, [`StartStopOptions`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.start_stop_options.StartStopOptions.html#exa.common.control.sweep.option.start_stop_options.StartStopOptions "exa.common.control.sweep.option.start_stop_options.StartStopOptions") is created.

- If configuration has keys `start_exp` and `stop_exp`, [`StartStopBaseOptions`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.start_stop_base_options.StartStopBaseOptions.html#exa.common.control.sweep.option.start_stop_base_options.StartStopBaseOptions "exa.common.control.sweep.option.start_stop_base_options.StartStopBaseOptions") is created.

- If configuration has keys `center` and `span`, [`CenterSpanOptions`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.center_span_options.CenterSpanOptions.html#exa.common.control.sweep.option.center_span_options.CenterSpanOptions "exa.common.control.sweep.option.center_span_options.CenterSpanOptions") is created.

- If configuration has keys `center_exp` and `span_exp`, [`CenterSpanBaseOptions`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.center_span_base_options.CenterSpanBaseOptions.html#exa.common.control.sweep.option.center_span_base_options.CenterSpanBaseOptions "exa.common.control.sweep.option.center_span_base_options.CenterSpanBaseOptions") is created

- If configuration has keys `fixed`, [`FixedOptions`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.fixed_options.FixedOptions.html#exa.common.control.sweep.option.fixed_options.FixedOptions "exa.common.control.sweep.option.fixed_options.FixedOptions") is created.

Parameters:  
**config** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*Any*](https://docs.python.org/3.11/library/typing.html#typing.Any "(in Python v3.11)")*\]*) – Configuration dictionary.

Raises:  
**BadRequestError** – Error is raised if config has unsupported structure

Return type:  
[*SweepOptions*](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.control.sweep.option.sweep_options.SweepOptions.html#exa.common.control.sweep.option.sweep_options.SweepOptions "exa.common.control.sweep.option.sweep_options.SweepOptions")
