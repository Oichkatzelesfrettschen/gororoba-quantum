> Full piece: [https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.EngineInitialisationError.html](https://docs.iqm.tech/4.7/iqm-exa-common/api/exa.common.errors.iqm_error.EngineInitialisationError.html)
> Retrieved 2026-10-19T06:06Z by scripts/capture_iqm_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 f024441f35b709576576142c96a2cad39d4f971aaa3b55f305c71ba997821812.

# exa.common.errors.iqm_error.EngineInitialisationError

*exception* EngineInitialisationError(*message="Station-control engine appears not initialized. A probable cause is that the job executor worker process failed to start. To find out what went wrong, please check station-control logs from the very beginning of the service startup. If station-control loggers are configured with 'verbose=True', each log message contains the module path; filtering by 'job_executor' will show all messages from the worker process, including possible errors. It is highly recommended to inspect the entire log for any preceding warnings or errors."*, *log_level=30*)  
Raised when the station control engine fails to initialize.

Parameters:  
- **message** ([*str*](https://docs.python.org/3.11/library/stdtypes.html#str "(in Python v3.11)"))

- **log_level** ([*int*](https://docs.python.org/3.11/library/functions.html#int "(in Python v3.11)"))
