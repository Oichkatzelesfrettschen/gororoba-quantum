> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.logger.logger.ExtraFormatter.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.logger.logger.ExtraFormatter.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 880c1a4740e88b8074f682e7ffed7c32715d7002e30f493ab8087d24961b04a1.

# ExtraFormatter

Module: [`exa.common.logger.logger`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.logger.logger.html#module-exa.common.logger.logger "exa.common.logger.logger")

*class* ExtraFormatter(*\*args*, *extra_info_getter=None*, *\*\*kwargs*)  
Bases: [`Formatter`](https://docs.python.org/3.11/library/logging.html#logging.Formatter "(in Python v3.11)")

Helper formatter class to pass in arbitrary extra information to log messages.

Initialize the formatter with specified format strings.

Initialize the formatter either with the specified format string, or a default as described above. Allow for specialized date formatting with the optional datefmt argument. If datefmt is omitted, you get an ISO8601-like (or RFC 3339-like) format.

Use a style parameter of ‘%’, ‘{’ or ‘\$’ to specify that you want to use one of %-formatting, [`str.format()`](https://docs.python.org/3.11/library/stdtypes.html#str.format "(in Python v3.11)") (`{}`) formatting or [`string.Template`](https://docs.python.org/3.11/library/string.html#string.Template "(in Python v3.11)") formatting in your format string.

Changed in version 3.2: Added the `style` parameter.

Attributes

Methods

|  |  |
|----|----|
| [`format`](#exa.common.logger.logger.ExtraFormatter.format "exa.common.logger.logger.ExtraFormatter.format") | Format the specified record as text. |

Parameters:  
**extra_info_getter** ([*Callable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")*\[\[\],* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*)

format(*record*)  
Format the specified record as text.

The record’s attribute dictionary is used as the operand to a string formatting operation which yields the returned string. Before formatting the dictionary, a couple of preparatory steps are carried out. The message attribute of the record is computed using LogRecord.getMessage(). If the formatting string uses the time (as determined by a call to usesTime(), formatTime() is called to format the event time. If there is exception information, it is formatted using formatException() and appended to the message.

Inheritance

![Inheritance diagram of exa.common.logger.logger.ExtraFormatter](https://docs.iqm.tech/4.7/iqm-exa-common/_images/inheritance-73f32c88521c965a6dd447896658976edfe8ffb8.png)
