> Full piece: [https://docs.openquantum.com/core-sdk/quickstart/](https://docs.openquantum.com/core-sdk/quickstart/)
> Retrieved 2026-10-17T05:09Z by scripts/capture_oq_docs.py --docs (urllib, pandoc);
> fetched HTML sha256 781169112b0f40264abfeca8ca2896e58fa876be4f23bd3ea1b2124a43fc63b7.

# Quick Start

Submit your first quantum job using the Core SDK in five steps.

## Step 1: Create an Open Quantum Account

Sign up at the [Open Quantum Portal](https://www.openquantum.com). You will receive free Spark credits to get started.

## Step 2: Generate an SDK Key

1.  Log in to the [Open Quantum Portal](https://www.openquantum.com).
2.  Go to the [SDK Keys](https://www.openquantum.com/keys) page.
3.  Click **Create SDK Key**.
4.  Copy the **Client ID** and **Client Secret** immediately.

Warning

The client secret is displayed only once at creation time. Store it in a secure location. If you lose it, delete the key and create a new one.

## Step 3: Set Environment Variables

Set your credentials as environment variables:

Linux / macOSWindows (PowerShell)

[](#__codelineno-0-1)`export`` ``OPENQUANTUM_CLIENT_ID``=``"s_your_client_id"`\
[](#__codelineno-0-2)`export`` ``OPENQUANTUM_CLIENT_SECRET``=``"your_client_secret"`\

[](#__codelineno-1-1)`$env:OPENQUANTUM_CLIENT_ID`` ``=`` ``"s_your_client_id"`\
[](#__codelineno-1-2)`$env:OPENQUANTUM_CLIENT_SECRET`` ``=`` ``"your_client_secret"`\

Tip

Add these to your shell profile (`.bashrc`, `.zshrc`) or use a `.env` file with a tool like `python-dotenv` to avoid setting them every session.

## Step 4: Create a QASM File

Create a file called `bell_state.qasm`:

[](#__codelineno-2-1)`OPENQASM 2.0;`\
[](#__codelineno-2-2)`include "qelib1.inc";`\
[](#__codelineno-2-3)`qreg q[2];`\
[](#__codelineno-2-4)`creg c[2];`\
[](#__codelineno-2-5)`h q[0];`\
[](#__codelineno-2-6)`cx q[0],q[1];`\
[](#__codelineno-2-7)`measure q[0] -> c[0];`\
[](#__codelineno-2-8)`measure q[1] -> c[1];`\

## Step 5: Submit the Job

Create a file called `run_job.py`:

[](#__codelineno-3-1)`import`` ``json`\
[](#__codelineno-3-2)`import`` ``os`\
[](#__codelineno-3-3)`from`` ``openquantum_sdk.auth`` ``import`` ``ClientCredentials``,`` ``ClientCredentialsAuth`\
[](#__codelineno-3-4)`from`` ``openquantum_sdk.clients`` ``import`` ``SchedulerClient``,`` ``JobSubmissionConfig`\
[](#__codelineno-3-5)\
[](#__codelineno-3-6)`auth`` ``=`` ``ClientCredentialsAuth``(`\
[](#__codelineno-3-7)`    ``creds``=``ClientCredentials``(`\
[](#__codelineno-3-8)`        ``client_id``=``os``.``environ``[``"OPENQUANTUM_CLIENT_ID"``],`\
[](#__codelineno-3-9)`        ``client_secret``=``os``.``environ``[``"OPENQUANTUM_CLIENT_SECRET"``],`\
[](#__codelineno-3-10)`    ``),`\
[](#__codelineno-3-11)`)`\
[](#__codelineno-3-12)\
[](#__codelineno-3-13)`scheduler`` ``=`` ``SchedulerClient``(``auth``=``auth``)`\
[](#__codelineno-3-14)\
[](#__codelineno-3-15)`config`` ``=`` ``JobSubmissionConfig``(`\
[](#__codelineno-3-16)`    ``backend_class_id``=``"rigetti:cepheus-1-108q"``,`\
[](#__codelineno-3-17)`    ``name``=``"Bell State Job"``,`\
[](#__codelineno-3-18)`    ``job_subcategory_id``=``"phys:oth"``,``  ``# Physics`\
[](#__codelineno-3-19)`    ``shots``=``128``,`\
[](#__codelineno-3-20)`    ``# input_format="qasm",  # default OpenQASM; set only if the backend requires another format`\
[](#__codelineno-3-21)`)`\
[](#__codelineno-3-22)\
[](#__codelineno-3-23)`job`` ``=`` ``scheduler``.``submit_job``(``config``,`` ``file_path``=``"bell_state.qasm"``)`\
[](#__codelineno-3-24)\
[](#__codelineno-3-25)`print``(``f``"Job ID: ``{``job``.``id``}``"``)`\
[](#__codelineno-3-26)`print``(``f``"Status: ``{``job``.``status``}``"``)`\
[](#__codelineno-3-27)\
[](#__codelineno-3-28)`output`` ``=`` ``scheduler``.``download_job_output``(``job``)`\
[](#__codelineno-3-29)`print``(``f``"Results: ``{``output``}``"``)`\
[](#__codelineno-3-30)\
[](#__codelineno-3-31)`# Optional: calibration snapshot`\
[](#__codelineno-3-32)`if`` ``job``.``calibration_data_url``:`\
[](#__codelineno-3-33)`    ``cal`` ``=`` ``scheduler``.``download_job_calibration``(``job``)`\
[](#__codelineno-3-34)`    ``print``(``f``"Calibration available (``{``len``(``json``.``dumps``(``cal``))``}`` chars)"``)`\
[](#__codelineno-3-35)\
[](#__codelineno-3-36)`scheduler``.``close``()`\

Run it:

[](#__codelineno-4-1)`python`` ``run_job.py`\

Input formats

The default is OpenQASM (`input_format="qasm"`). Some backends accept other formats via `input_format` when listed in their `supported_formats`. See [Job Submission](https://docs.openquantum.com/core-sdk/job-submission/#input-formats).

Monitor jobs from anywhere

Every job you submit is visible in the [Jobs](https://www.openquantum.com/jobs) page on the portal. If your code is running on a remote server, you can still check status, view results, download results, and (when present) **download calibration data** from the job **⋯** menu. See [Monitoring Jobs](https://docs.openquantum.com/portal/monitoring-jobs/) for details.

## Next Steps

- [Portal](https://docs.openquantum.com/portal/overview/) -- Submit jobs, monitor progress, manage keys and credits from the web UI.
- [Sample Circuits & Notebooks](https://docs.openquantum.com/getting-started/resources/) -- Ready-to-run QASM files and Colab notebooks.
- [Authentication](https://docs.openquantum.com/core-sdk/authentication/) -- Learn about all authentication options including saved accounts.
- [Core SDK Overview](https://docs.openquantum.com/core-sdk/overview/) -- Detailed guide to SchedulerClient and ManagementClient.
- [Qiskit Plugin](https://docs.openquantum.com/qiskit-plugin/getting-started/) -- Use Open Quantum with Qiskit circuits.
- [PennyLane Plugin](https://docs.openquantum.com/pennylane-plugin/overview/) -- Use Open Quantum with PennyLane circuits.
- [Cirq Plugin](https://docs.openquantum.com/cirq-plugin/overview/) -- Run Cirq circuits on Open Quantum.
- [Qrisp Plugin](https://docs.openquantum.com/qrisp-plugin/overview/) -- Run Qrisp programs on Open Quantum.
