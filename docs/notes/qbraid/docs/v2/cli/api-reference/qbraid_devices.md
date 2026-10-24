> Full piece: [https://docs.qbraid.com/v2/cli/api-reference/qbraid_devices.md](https://docs.qbraid.com/v2/cli/api-reference/qbraid_devices.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 31e811d0b5415dc18685f1d268add3e77e14c2a61de7fedf303588ce9a5e7364.

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

# qbraid devices

> Browse quantum devices.

Browse and query quantum devices across providers.
Access quantum hardware and simulators from IonQ, IBM, AWS Braket,
Rigetti, QuEra, Pasqal, and more through the unified qBraid runtime.

Use this when you want to:

- Find available quantum devices and their current status
- Compare pricing, qubit counts, and queue depths
- Check device specifications before submitting jobs

**Usage**:

```console
$ qbraid devices [OPTIONS] COMMAND [ARGS]...
```

**Options**:

- `--help`: Show this message and exit.

**Commands**:

- `list`: List qBraid quantum devices.
- `get`: Get a qBraid quantum device.

## qbraid devices list

List qBraid quantum devices.

**Usage**:

```console
$ qbraid devices list [OPTIONS]
```

**Options**:

- `-s, --status <ONLINE|UNAVAILABLE|OFFLINE|RETIRED>`: Filter by status: ONLINE, UNAVAILABLE, OFFLINE, RETIRED
- `-t, --type <str>`: 'QPU'|'SIMULATOR'
- `-v, --vendor <aws|azure|ibm|ionq|qbraid>`: Filter by vendor: AWS, AZURE, IBM, IONQ, QBRAID
- `-p, --provider <aqt|aws|azure|equal1|ibm|iqm|ionq|nec|oqc|pasqal|quantinuum|quera|rigetti|qbraid>`: Filter by provider: AQT, AWS, AZURE, EQUAL1, IBM, IQM, IONQ, NEC, OQC, PASQAL, QUANTINUUM, QUERA, RIGETTI, QBRAID
- `--help`: Show this message and exit.

## qbraid devices get

Get a qBraid quantum device.

**Usage**:

```console
$ qbraid devices get [OPTIONS] {device_id}
```

**Arguments**:

- `device_id`: The QRN or ID of the device to get. [required]

**Options**:

- `--no-fmt`: Disable rich console formatting (output raw data) [default: True]
- `--help`: Show this message and exit.
