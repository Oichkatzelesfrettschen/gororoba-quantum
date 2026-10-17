> Full piece: [https://docs.openquantum.com/core-sdk/examples/](https://docs.openquantum.com/core-sdk/examples/)
> Retrieved 2026-10-17T05:09Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 ec3a8f5d8077dbc9349fc34933b416c86a0281679fb2d6d989a2fe8562684a8f.

# Core SDK Examples

Common workflows using the `openquantum-sdk` package.

Note

All examples assume you have valid SDK key credentials. See [Authentication](https://docs.openquantum.com/core-sdk/authentication/) for setup.

## Submit a QASM File from Disk

[](#__codelineno-0-1)`from`` ``openquantum_sdk.auth`` ``import`` ``ClientCredentials``,`` ``ClientCredentialsAuth`\
[](#__codelineno-0-2)`from`` ``openquantum_sdk.clients`` ``import`` ``SchedulerClient``,`` ``JobSubmissionConfig`\
[](#__codelineno-0-3)\
[](#__codelineno-0-4)`auth`` ``=`` ``ClientCredentialsAuth``(`\
[](#__codelineno-0-5)`    ``creds``=``ClientCredentials``(`\
[](#__codelineno-0-6)`        ``client_id``=``"s_your_client_id"``,`\
[](#__codelineno-0-7)`        ``client_secret``=``"your_client_secret"``,`\
[](#__codelineno-0-8)`    ``),`\
[](#__codelineno-0-9)`)`\
[](#__codelineno-0-10)\
[](#__codelineno-0-11)`scheduler`` ``=`` ``SchedulerClient``(``auth``=``auth``)`\
[](#__codelineno-0-12)\
[](#__codelineno-0-13)`config`` ``=`` ``JobSubmissionConfig``(`\
[](#__codelineno-0-14)`    ``backend_class_id``=``"rigetti:cepheus-1-108q"``,`\
[](#__codelineno-0-15)`    ``name``=``"File Upload Job"``,`\
[](#__codelineno-0-16)`    ``job_subcategory_id``=``"oth:oth"``,`\
[](#__codelineno-0-17)`    ``shots``=``128``,`\
[](#__codelineno-0-18)`)`\
[](#__codelineno-0-19)\
[](#__codelineno-0-20)`job`` ``=`` ``scheduler``.``submit_job``(``config``,`` ``file_path``=``"my_circuit.qasm"``)`\
[](#__codelineno-0-21)`output`` ``=`` ``scheduler``.``download_job_output``(``job``)`\
[](#__codelineno-0-22)`print``(``output``)`\
[](#__codelineno-0-23)\
[](#__codelineno-0-24)`scheduler``.``close``()`\

## Submit a QASM String

[](#__codelineno-1-1)`from`` ``openquantum_sdk.auth`` ``import`` ``ClientCredentials``,`` ``ClientCredentialsAuth`\
[](#__codelineno-1-2)`from`` ``openquantum_sdk.clients`` ``import`` ``SchedulerClient``,`` ``JobSubmissionConfig`\
[](#__codelineno-1-3)\
[](#__codelineno-1-4)`auth`` ``=`` ``ClientCredentialsAuth``(`\
[](#__codelineno-1-5)`    ``creds``=``ClientCredentials``(`\
[](#__codelineno-1-6)`        ``client_id``=``"s_your_client_id"``,`\
[](#__codelineno-1-7)`        ``client_secret``=``"your_client_secret"``,`\
[](#__codelineno-1-8)`    ``),`\
[](#__codelineno-1-9)`)`\
[](#__codelineno-1-10)\
[](#__codelineno-1-11)`scheduler`` ``=`` ``SchedulerClient``(``auth``=``auth``)`\
[](#__codelineno-1-12)\
[](#__codelineno-1-13)`qasm`` ``=`` ``"""`\
[](#__codelineno-1-14)`OPENQASM 2.0;`\
[](#__codelineno-1-15)`include "qelib1.inc";`\
[](#__codelineno-1-16)`qreg q[2];`\
[](#__codelineno-1-17)`creg c[2];`\
[](#__codelineno-1-18)`h q[0];`\
[](#__codelineno-1-19)`cx q[0],q[1];`\
[](#__codelineno-1-20)`measure q[0] -> c[0];`\
[](#__codelineno-1-21)`measure q[1] -> c[1];`\
[](#__codelineno-1-22)`"""`\
[](#__codelineno-1-23)\
[](#__codelineno-1-24)`config`` ``=`` ``JobSubmissionConfig``(`\
[](#__codelineno-1-25)`    ``backend_class_id``=``"rigetti:cepheus-1-108q"``,`\
[](#__codelineno-1-26)`    ``name``=``"String QASM Job"``,`\
[](#__codelineno-1-27)`    ``job_subcategory_id``=``"oth:oth"``,`\
[](#__codelineno-1-28)`    ``shots``=``128``,`\
[](#__codelineno-1-29)`)`\
[](#__codelineno-1-30)\
[](#__codelineno-1-31)`job`` ``=`` ``scheduler``.``submit_job``(``config``,`` ``file_content``=``qasm``.``encode``(``"utf-8"``))`\
[](#__codelineno-1-32)`output`` ``=`` ``scheduler``.``download_job_output``(``job``)`\
[](#__codelineno-1-33)`print``(``output``)`\
[](#__codelineno-1-34)\
[](#__codelineno-1-35)`scheduler``.``close``()`\

## List and Filter Backends

[](#__codelineno-2-1)`from`` ``openquantum_sdk.auth`` ``import`` ``ClientCredentials``,`` ``ClientCredentialsAuth`\
[](#__codelineno-2-2)`from`` ``openquantum_sdk.clients`` ``import`` ``ManagementClient`\
[](#__codelineno-2-3)\
[](#__codelineno-2-4)`auth`` ``=`` ``ClientCredentialsAuth``(`\
[](#__codelineno-2-5)`    ``creds``=``ClientCredentials``(`\
[](#__codelineno-2-6)`        ``client_id``=``"s_your_client_id"``,`\
[](#__codelineno-2-7)`        ``client_secret``=``"your_client_secret"``,`\
[](#__codelineno-2-8)`    ``),`\
[](#__codelineno-2-9)`)`\
[](#__codelineno-2-10)\
[](#__codelineno-2-11)`management`` ``=`` ``ManagementClient``(``auth``=``auth``)`\
[](#__codelineno-2-12)\
[](#__codelineno-2-13)`# List all backends`\
[](#__codelineno-2-14)`result`` ``=`` ``management``.``list_backend_classes``()`\
[](#__codelineno-2-15)`for`` ``bc`` ``in`` ``result``.``backend_classes``:`\
[](#__codelineno-2-16)`    ``status`` ``=`` ``"accepting jobs"`` ``if`` ``bc``.``accepting_jobs`` ``else`` ``"not accepting"`\
[](#__codelineno-2-17)`    ``print``(``f``"``{``bc``.``short_code``}`` (``{``bc``.``type``}``, ``{``bc``.``status``}``, ``{``status``}``)"``)`\
[](#__codelineno-2-18)\
[](#__codelineno-2-19)`# Filter by provider`\
[](#__codelineno-2-20)`ionq_backends`` ``=`` ``management``.``list_backend_classes``(``provider_id``=``"ionq"``)`\
[](#__codelineno-2-21)`for`` ``bc`` ``in`` ``ionq_backends``.``backend_classes``:`\
[](#__codelineno-2-22)`    ``print``(``f``"IonQ: ``{``bc``.``short_code``}`` - ``{``bc``.``name``}``"``)`\
[](#__codelineno-2-23)\
[](#__codelineno-2-24)`management``.``close``()`\

## Check Job Status

[](#__codelineno-3-1)`from`` ``openquantum_sdk.auth`` ``import`` ``ClientCredentials``,`` ``ClientCredentialsAuth`\
[](#__codelineno-3-2)`from`` ``openquantum_sdk.clients`` ``import`` ``SchedulerClient`\
[](#__codelineno-3-3)\
[](#__codelineno-3-4)`auth`` ``=`` ``ClientCredentialsAuth``(`\
[](#__codelineno-3-5)`    ``creds``=``ClientCredentials``(`\
[](#__codelineno-3-6)`        ``client_id``=``"s_your_client_id"``,`\
[](#__codelineno-3-7)`        ``client_secret``=``"your_client_secret"``,`\
[](#__codelineno-3-8)`    ``),`\
[](#__codelineno-3-9)`)`\
[](#__codelineno-3-10)\
[](#__codelineno-3-11)`scheduler`` ``=`` ``SchedulerClient``(``auth``=``auth``)`\
[](#__codelineno-3-12)\
[](#__codelineno-3-13)`job`` ``=`` ``scheduler``.``get_job``(``"your-job-uuid"``)`\
[](#__codelineno-3-14)`print``(``f``"Job: ``{``job``.``id``}``"``)`\
[](#__codelineno-3-15)`print``(``f``"Status: ``{``job``.``status``}``"``)`\
[](#__codelineno-3-16)`print``(``f``"Submitted: ``{``job``.``submitted_at``}``"``)`\
[](#__codelineno-3-17)\
[](#__codelineno-3-18)`if`` ``job``.``status`` ``==`` ``"Completed"`` ``and`` ``job``.``output_data_url``:`\
[](#__codelineno-3-19)`    ``output`` ``=`` ``scheduler``.``download_job_output``(``job``)`\
[](#__codelineno-3-20)`    ``print``(``f``"Results: ``{``output``}``"``)`\
[](#__codelineno-3-21)\
[](#__codelineno-3-22)`if`` ``job``.``calibration_data_url``:`\
[](#__codelineno-3-23)`    ``cal`` ``=`` ``scheduler``.``download_job_calibration``(``job``)`\
[](#__codelineno-3-24)`    ``print``(``f``"Calibration keys: ``{``list``(``cal``)`` ``if`` ``isinstance``(``cal``,`` ``dict``)`` ``else`` ``type``(``cal``)``}``"``)`\
[](#__codelineno-3-25)\
[](#__codelineno-3-26)`scheduler``.``close``()`\

## List Organization Jobs

[](#__codelineno-4-1)`from`` ``openquantum_sdk.auth`` ``import`` ``ClientCredentials``,`` ``ClientCredentialsAuth`\
[](#__codelineno-4-2)`from`` ``openquantum_sdk.clients`` ``import`` ``SchedulerClient`\
[](#__codelineno-4-3)\
[](#__codelineno-4-4)`auth`` ``=`` ``ClientCredentialsAuth``(`\
[](#__codelineno-4-5)`    ``creds``=``ClientCredentials``(`\
[](#__codelineno-4-6)`        ``client_id``=``"s_your_client_id"``,`\
[](#__codelineno-4-7)`        ``client_secret``=``"your_client_secret"``,`\
[](#__codelineno-4-8)`    ``),`\
[](#__codelineno-4-9)`)`\
[](#__codelineno-4-10)\
[](#__codelineno-4-11)`scheduler`` ``=`` ``SchedulerClient``(``auth``=``auth``)`\
[](#__codelineno-4-12)\
[](#__codelineno-4-13)`# List recent jobs (organization is auto-discovered)`\
[](#__codelineno-4-14)`result`` ``=`` ``scheduler``.``list_jobs``()`\
[](#__codelineno-4-15)`for`` ``job`` ``in`` ``result``.``jobs``:`\
[](#__codelineno-4-16)`    ``print``(``f``"``{``job``.``name``}``: ``{``job``.``status``}`` (``{``job``.``submitted_at``}``)"``)`\
[](#__codelineno-4-17)\
[](#__codelineno-4-18)`# Filter by status`\
[](#__codelineno-4-19)`completed`` ``=`` ``scheduler``.``list_jobs``(``status``=``"Completed"``)`\
[](#__codelineno-4-20)`for`` ``job`` ``in`` ``completed``.``jobs``:`\
[](#__codelineno-4-21)`    ``print``(``f``"Completed: ``{``job``.``name``}`` - ``{``job``.``credits_used``}`` credits"``)`\
[](#__codelineno-4-22)\
[](#__codelineno-4-23)`scheduler``.``close``()`\

## Use the CLI

The Core SDK includes a command-line interface:

[](#__codelineno-5-1)`python`` ``-m`` ``openquantum_sdk`` ``\`\
[](#__codelineno-5-2)`    ``--input`` ``circuit.qasm`` ``\`\
[](#__codelineno-5-3)`    ``--backend`` ``rigetti:cepheus-1-108q`` ``\`\
[](#__codelineno-5-4)`    ``--subcategory`` ``oth:oth`` ``\`\
[](#__codelineno-5-5)`    ``--shots`` ``128`` ``\`\
[](#__codelineno-5-6)`    ``--client-id`` ``"s_your_client_id"`` ``\`\
[](#__codelineno-5-7)`    ``--client-secret`` ``"your_client_secret"`` ``\`\
[](#__codelineno-5-8)`    ``--auto-approve`\

Or with an SDK key file:

[](#__codelineno-6-1)`python`` ``-m`` ``openquantum_sdk`` ``\`\
[](#__codelineno-6-2)`    ``--input`` ``circuit.qasm`` ``\`\
[](#__codelineno-6-3)`    ``--backend`` ``rigetti:cepheus-1-108q`` ``\`\
[](#__codelineno-6-4)`    ``--subcategory`` ``oth:oth`` ``\`\
[](#__codelineno-6-5)`    ``--shots`` ``128`` ``\`\
[](#__codelineno-6-6)`    ``--sdk-key`` ``credentials.json`\

The SDK key file is a JSON file with `client_id` and `client_secret` fields:

[](#__codelineno-7-1)`{`\
[](#__codelineno-7-2)`    ``"client_id"``:`` ``"s_your_client_id"``,`\
[](#__codelineno-7-3)`    ``"client_secret"``:`` ``"your_client_secret"`\
[](#__codelineno-7-4)`}`\

## Related Pages

- [Job Submission](https://docs.openquantum.com/core-sdk/job-submission/) -- Detailed `JobSubmissionConfig` reference.
- [Backend Discovery](https://docs.openquantum.com/core-sdk/backend-discovery/) -- Backend listing and filtering.
- [Authentication](https://docs.openquantum.com/core-sdk/authentication/) -- All authentication options.
