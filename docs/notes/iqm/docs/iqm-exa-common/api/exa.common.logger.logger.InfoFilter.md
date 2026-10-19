> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.logger.logger.InfoFilter.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.logger.logger.InfoFilter.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 964ed88a7b38b35a07dc7cf580b529bf052292c092d8c0d4cac29958c75cc052.

# InfoFilter

Module: [`exa.common.logger.logger`](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.logger.logger.html#module-exa.common.logger.logger "exa.common.logger.logger")

*class* InfoFilter(*name=''*)  
Bases: [`Filter`](https://docs.python.org/3.11/library/logging.html#logging.Filter "(in Python v3.11)")

Helper class to filter log messages above INFO level.

Initialize a filter.

Initialize with the name of the logger which, together with its children, will have its events allowed through the filter. If no name is specified, allow every event.

Methods

|  |  |
|----|----|
| [`filter`](#exa.common.logger.logger.InfoFilter.filter "exa.common.logger.logger.InfoFilter.filter") | Determine if the specified record is to be logged. |

filter(*record*)  
Determine if the specified record is to be logged.

Returns True if the record should be logged, or False otherwise. If deemed appropriate, the record may be modified in-place.

Parameters:  
**record** ([*LogRecord*](https://docs.python.org/3.11/library/logging.html#logging.LogRecord "(in Python v3.11)"))

Return type:  
[*bool*](https://docs.python.org/3.11/library/functions.html#bool "(in Python v3.11)")

Inheritance

![Inheritance diagram of exa.common.logger.logger.InfoFilter](https://docs.iqm.tech/4.7/iqm-exa-common/_images/inheritance-580e166e73e60503386f4fe9e9ec0dda26030225.png)
