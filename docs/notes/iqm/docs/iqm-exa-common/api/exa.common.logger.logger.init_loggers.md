> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.logger.logger.init_loggers.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.logger.logger.init_loggers.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 635526663442bf25682b1ea9eca5223923a1051cdeb9085d0f154e981d70093e.

# exa.common.logger.logger.init_loggers

init_loggers(*loggers=None*, *default_level='INFO'*, *verbose=False*, *extra_info_getter=None*)  
Set the log level of given logger names.

Logs with INFO or DEBUG logging levels are written into stdout, and logs with other levels are written into stderr.

By default, the root logger uses WARNING level.

See Python’s logging module for possible logging levels.

Parameters:  
- **loggers** ([*dict*](https://docs.python.org/3.11/library/stdtypes.html#dict "(in Python v3.11)")*\[*[*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*,* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)") *\|* *None\]* *\|* *None*) – A mapping from logger name to (case insensitive) logging level. If logging level is None or empty string, `default_level` will be used for that logger. It is possible to fine tune logging for individual modules, since logger propagation is turned off. Overriding works both ways: a parent logger can have higher logging level than its descendants, and vice versa. For example, `{"sqlalchemy": None, "sqlalchemy.engine": "debug"}` will put “sqlalchemy” and its descendants (i.e. “sqlalchemy.dialects”, “sqlalchemy.dialects.sqlite”, etc.) into `default_level`, except for “sqlalchemy.engine” for which DEBUG level is defined. For the root logger, use empty string key, for example: `{"": "INFO"}`. If empty dict or None is given, only the root logger will be initialized to its default WARNING level.

- **default_level** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")) – The default level (case insensitive) to be used for logger names given with `loggers` for which a level is not specified.

- **verbose** ([*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")) – If False, :const:`BRIEF` format will be used for log messages, otherwise :const:`VERBOSE`.

- **extra_info_getter** ([*Callable*](https://docs.python.org/3.11/library/collections.abc.html#collections.abc.Callable "(in Python v3.11)")*\[\[\],* [*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)")*\]* *\|* *None*) – Optional callable to convey extra information to log messages. It will get called before each log message emission and the output will get appended to the log message.

Return type:  
*None*
