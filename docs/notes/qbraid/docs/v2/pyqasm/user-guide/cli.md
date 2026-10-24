> Full piece: [https://docs.qbraid.com/v2/pyqasm/user-guide/cli.md](https://docs.qbraid.com/v2/pyqasm/user-guide/cli.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 0e4b1c8a3e0e3a2ed8ad8f61c8337b59c956a76e72674352352be32f75404f92.

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

# PyQASM CLI

To provide a more interactive experience for developers, PyQASM offers a
command-line interface (CLI) tool. The CLI tool can be installed as an extra
dependency by running the following command:

```shell
pip install 'pyqasm[cli]'
```

<Note>
  This feature is still in active development and may not be stable for
  production use
</Note>

Users can then verify their installation by running the following command:

<CodeGroup>

```shell Verify installation
pyqasm --help
```

```shell Output
Usage: pyqasm [OPTIONS] COMMAND [ARGS]...

The PyQASM CLI.

╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --version             -v        Show the version and exit.                                                     │
│ --install-completion            Install completion for the current shell.                                      │
│ --show-completion               Show completion for the current shell, to copy it or customize the             │
│                                 installation.                                                                  │
│ --help                -h        Show this message and exit.                                                    │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ validate   Validate OpenQASM files.                                                                            |
| unroll     Unroll OpenQASM files.                                                                                                               │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

</CodeGroup>

**Validate**

The `validate` functionality can be used to check QASM files. You can provide the path to
the QASM file or a directory as an argument to the `validate` command. The tool will then check the
semantic validity of the file(s) and return the results.

<Tabs>
<Tab title="Validate commands">
<CodeGroup>

```shell help command
pyqasm validate --help
```

```shell Output
Usage: pyqasm validate [OPTIONS] SRC_PATHS...

 Validate OpenQASM files.

╭─ Arguments ─────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    src_paths      SRC_PATHS...  Source file or directory paths to validate.                                   │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --skip       -s      TEXT  Files to skip during validation.                                                    │
│ --help       -h            Show this message and exit.                                                         │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

</CodeGroup>
</Tab>
<Tab title = "Validate QASM files">
<CodeGroup>

```shell Valid QASM file
$ pyqasm validate tests/cli/resources/valid1.qasm

Success: no issues found in 1 source file

```

```shell Invalid QASM file inside a dir
$ pyqasm validate tests/cli/resources/

tests/cli/resources/invalid1.qasm: error: Index 2 out of range for register of size 1 in qubit [validation]
Found errors in 1 file (checked 3 source files)
```

</CodeGroup>
</Tab>
</Tabs>

**Unroll**

The `unroll` functionality is used to expand all macros and modular structures in OpenQASM files into flat, low-level instructions that are directly executable by quantum devices or emulators. You can provide either the path to a specific QASM file or a directory containing multiple QASM files as an argument to the `unroll` command. By default, the unrolled file is saved with the following naming convention: `<original_qasm_filename>_unrolled`

<Tabs>
<Tab title = "Unroll commands">
<CodeGroup>

```shell help command
pyqasm unroll --help
```

```shell Output
Usage: pyqasm unroll [OPTIONS] SRC_PATHS...

 Unroll OpenQASM files.

╭─ Arguments ─────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    src_paths      SRC_PATHS...  Source file or directory paths to unroll.                                     │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --skip       -s      TEXT  Files to skip during unrolling.                                                     │
│ --overwrite                Overwrite original files instead of creating new ones.                              │
│ --output     -o      TEXT  Output file path (can only be used with a single input file).                       │
│ --help       -h            Show this message and exit.                                                         │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

</CodeGroup>
</Tab>
<Tab title = "Unrolling QASM files">
<CodeGroup>

```shell Unroll single QASM file
$ pyqasm unroll tests/cli/resources/valid1.qasm

Successfully unrolled 1 file
Checked 1 source file

```

```shell Unroll multiple QASM file inside a dir
$ pyqasm unroll tests/cli/resources/

Successfully unrolled 2 files
----------------------------------------------------------------------------------------------------
Failed to unroll: tests/cli/resources/invalid1.qasm

[validation-error] -> Index 2 out of range for register of size 1 in qubit

Error at line 8, column 0 in QASM file

 >>>>>> h q[2];
----------------------------------------------------------------------------------------------------
Failed to unroll 1 file
Checked 3 source files
```

</CodeGroup>
</Tab>
</Tabs>
