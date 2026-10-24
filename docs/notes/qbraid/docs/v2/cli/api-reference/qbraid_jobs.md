> Full piece: [https://docs.qbraid.com/v2/cli/api-reference/qbraid_jobs.md](https://docs.qbraid.com/v2/cli/api-reference/qbraid_jobs.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 1aeee0fdaf6bd003d73b9fe38bbb2ce8831559f682a6241eec3d3eecf3c91f8a.

> ## Documentation Index
> Fetch the complete documentation index at: https://docs.qbraid.com/llms.txt
> Use this file to discover all available pages before exploring further.

> ## Agent Instructions
> Prefer the qBraid CLI for programmatic platform actions: pip install 'qbraid-cli>=0.12', then run `qbraid configure` once with an API key from https://account.qbraid.com/account/api-keys.
> When writing Python, prefer the qBraid SDK: `from qbraid.runtime import QbraidProvider` wraps devices, job submission (`device.run()`), and batch groups (`GroupJobSession`).
> Always install the latest packages (pip install -U qbraid qbraid-cli); do not pin versions from memory. qbraid-cli below 0.12.0 is incompatible with the current API.
> Device IDs use the QRN format vendor:provider:type:name (e.g. qbraid:qbraid:sim:qir-sv, rigetti:rigetti:qpu:cepheus-1-108q). Legacy underscore IDs are deprecated.
> The REST API base URL is https://api-v2.qbraid.com/api/v1, authenticated with an X-API-Key header.
> For endpoints without a dedicated wrapper, use `QbraidSessionV1` from `qbraid_core` — an authenticated session (`.get()`/`.post()`) that sets the X-API-Key header. Full spec: https://docs.qbraid.com/openapi-v2.json
> Free simulators cost no credits; QPU and GPU jobs consume credits. Surface the estimated cost to the user before submitting a paid job.
> For account signup, API keys, credits, and end-to-end action recipes, see https://qbraid.com/llms.txt.

# qbraid jobs

> Submit and track quantum computing jobs.

Monitor quantum jobs across all providers from a single interface.
View job status, results, and costs.

Use this when you want to:

- Check the status of submitted quantum jobs
- View results from completed experiments
- Track costs across providers
- Bundle related jobs into groups (qbraid jobs groups)

**Usage**:

```console
$ qbraid jobs [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--help`: Show this message and exit.

**Commands**:

- `submit`: Submit a quantum job.
- `list`: List quantum jobs.
- `get`: Get a qBraid Quantum Job.
- `groups`: Manage job groups.

## qbraid jobs submit

Submit a quantum job.

Submit a quantum program to a device on the qBraid platform.
The program can be provided as a file path or piped via stdin.

Examples:

```bash
qbraid jobs submit circuit.qasm -d qbraid:qbraid:sim:qir-sv --shots 100

cat circuit.qasm | qbraid jobs submit - -d qbraid:qbraid:sim:qir-sv -f qasm2

qbraid jobs submit program.ll -d qbraid:qbraid:sim:qir-sv --json
```

**Usage**:

```console
$ qbraid jobs submit [OPTIONS] {program}
```

**Arguments**:

- `program`: Path to a quantum program file, or '-' to read from stdin. [required]

**Options**:

- `-d, --device <str>`: Target device QRN (e.g. 'qbraid:qbraid:sim:qir-sv'). [required]
- `-f, --format <qasm2|qasm3|qir.bc|qir.ll|analog|pulser.sequence|quil|ionq.circuit.v0|problem>`: Program format. Required when reading from stdin. Auto-detected from file extension when omitted. Options: qasm2, qasm3, qir.bc, qir.ll, analog, pulser.sequence, quil, ionq.circuit.v0, problem
- `-s, --shots <int range>`: Number of shots to execute. [x&gt;=1]
- `-n, --name <str>`: Job name.
- `-t, --tags <str>`: Job tags as a JSON object (e.g. '&#123;&quot;experiment&quot;:&quot;bell&quot;&#125;').
- `--options <str>`: Runtime options as a JSON object.
- `--group <str>`: Group job QRN to associate this job with.
- `--json`: Output full job response as JSON (for programmatic use).
- `--help`: Show this message and exit.

## qbraid jobs list

List quantum jobs.

Lists quantum jobs submitted through the qBraid platform.

**Usage**:

```console
$ qbraid jobs list [OPTIONS]
```

**Options**:

- `-l, --limit <int>`: Limit the maximum number of results returned [default: 10]
- `-s, --status <INITIALIZING|QUEUED|VALIDATING|RUNNING|CANCELLING|CANCELLED|COMPLETED|FAILED|UNKNOWN|HOLD>`: Filter by status: INITIALIZING, QUEUED, VALIDATING, RUNNING, CANCELLING, CANCELLED, COMPLETED, FAILED, UNKNOWN, HOLD
- `-v, --vendor <aws|azure|ibm|ionq|qbraid>`: Filter by vendor: AWS, AZURE, IBM, IONQ, QBRAID
- `-p, --provider <aqt|aws|azure|equal1|ibm|iqm|ionq|nec|oqc|pasqal|quantinuum|quera|rigetti|qbraid>`: Filter by provider: AQT, AWS, AZURE, EQUAL1, IBM, IQM, IONQ, NEC, OQC, PASQAL, QUANTINUUM, QUERA, RIGETTI, QBRAID
- `--page <int>`: Page number for pagination [default: 1]
- `--help`: Show this message and exit.

## qbraid jobs get

Get a qBraid Quantum Job.

**Usage**:

```console
$ qbraid jobs get [OPTIONS] {job_id}
```

**Arguments**:

- `job_id`: The QRN or ID of the job to get. [required]

**Options**:

- `--no-fmt`: Disable rich console formatting (output raw data) [default: True]
- `--help`: Show this message and exit.

## qbraid jobs groups

Manage job groups.

A group bundles related jobs into one session so the runtime can
track aggregate cost and status. Submit into a group with
`qbraid jobs submit --group &lt;qrn&gt;`.

Quick start:

```bash
qbraid jobs groups create -n my-batch
qbraid jobs groups list
qbraid jobs groups info <qrn>
qbraid jobs groups jobs <qrn>
qbraid jobs groups close <qrn>     # no more submissions, jobs run
qbraid jobs groups cancel <qrn>    # cancel group + non-terminal jobs
qbraid jobs groups delete <qrn>    # remove the record
```

**Usage**:

```console
$ qbraid jobs groups [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--help`: Show this message and exit.

**Commands**:

- `list`: List your job groups.
- `info`: Show full details for one group.
- `create`: Create a new group.
- `close`: Close a group to new submissions.
- `cancel`: Cancel a group and its non-terminal jobs.
- `jobs`: List the jobs in a group.
- `delete`: Delete a group record.

### qbraid jobs groups list

List your job groups.

**Usage**:

```console
$ qbraid jobs groups list [OPTIONS]
```

**Options**:

- `-s, --status <str>`: Filter by status (OPEN/CLOSED/COMPLETED/FAILED/CANCELLED)
- `-p, --page <int range>`: Page number [x&gt;=1]
- `-l, --limit <int range>`: Results per page [x&gt;=1]
- `--help`: Show this message and exit.

### qbraid jobs groups info

Show full details for one group.

**Usage**:

```console
$ qbraid jobs groups info [OPTIONS] {qrn}
```

**Arguments**:

- `qrn`: Group QRN [required]

**Options**:

- `--help`: Show this message and exit.

### qbraid jobs groups create

Create a new group.

Returns the new group's QRN — pass it to `qbraid jobs submit --group`
to attach jobs into the group.

**Usage**:

```console
$ qbraid jobs groups create [OPTIONS]
```

**Options**:

- `-n, --name <str>`: Human-readable group name
- `-t, --tags <str>`: Comma-separated key=value tags (values stored as strings)
- `-m, --metadata <str>`: Comma-separated key=value metadata (values stored as strings)
- `--max-ttl <int range>`: Max time-to-live in seconds (1-86400) [1&lt;=x&lt;=86400]
- `--help`: Show this message and exit.

### qbraid jobs groups close

Close a group to new submissions.

Existing jobs continue running; only new submissions are blocked.

**Usage**:

```console
$ qbraid jobs groups close [OPTIONS] {qrn}
```

**Arguments**:

- `qrn`: Group QRN [required]

**Options**:

- `--help`: Show this message and exit.

### qbraid jobs groups cancel

Cancel a group and its non-terminal jobs.

**Usage**:

```console
$ qbraid jobs groups cancel [OPTIONS] {qrn}
```

**Arguments**:

- `qrn`: Group QRN [required]

**Options**:

- `-f, --force`: Skip confirmation
- `--help`: Show this message and exit.

### qbraid jobs groups jobs

List the jobs in a group.

Requires qbraid-core &gt;= 0.3.3 (the get_group_jobs helper).

**Usage**:

```console
$ qbraid jobs groups jobs [OPTIONS] {qrn}
```

**Arguments**:

- `qrn`: Group QRN [required]

**Options**:

- `--help`: Show this message and exit.

### qbraid jobs groups delete

Delete a group record.

Underlying jobs are not affected — cancel the group first if you want
to stop them. Idempotent: deleting an already-deleted group is a no-op.
Requires qbraid-core &gt;= 0.3.3 (the delete_group helper).

**Usage**:

```console
$ qbraid jobs groups delete [OPTIONS] {qrn}
```

**Arguments**:

- `qrn`: Group QRN [required]

**Options**:

- `-f, --force`: Skip confirmation
- `--help`: Show this message and exit.
