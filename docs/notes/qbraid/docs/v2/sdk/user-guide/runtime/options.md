> Full piece: [https://docs.qbraid.com/v2/sdk/user-guide/runtime/options.md](https://docs.qbraid.com/v2/sdk/user-guide/runtime/options.md)
> Retrieved 2026-10-24T20:47Z by scripts/capture_qbraid_docs.py --docs (urllib);
> fetched bytes sha256 4892cf99bf43cc83a378bdb8d3fe6113b36eaca267abdf66d9d3c8778874946e.

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

# Runtime Options

> Settings applied at the device level that control the behavior of a device.run call

## Overview

Every `QuantumDevice` has a set of runtime options that control the behavior of the `device.run()` call.
These options govern which steps in the [job submission pipeline](https://docs.qbraid.com/v2/sdk/user-guide/runtime/components#quantum-job-submission-process)
are enabled, and can be updated using `device.set_options()`.

The four default options correspond to the pipeline steps that precede job submission:

| Option      | Default                 | Type                       | Description                                                              |
| ----------- | ----------------------- | -------------------------- | ------------------------------------------------------------------------ |
| `transpile` | `True`                  | `bool`                     | Convert the program to the device's target program type                  |
| `transform` | `True`                  | `bool`                     | Apply device-specific passes (e.g. gate decomposition, topology mapping) |
| `validate`  | `ValidationLevel.RAISE` | `ValidationLevel` or `int` | Verify the program satisfies device constraints                          |
| `prepare`   | `True`                  | `bool`                     | Serialize the program to the submission IR format                        |

```python
device.set_options(transform=False)
device.set_options(validate=False)
```

Each option corresponds to a step in the `apply_runtime_profile` pipeline invoked by `device.run()`:

```
run_input ─> transpile ─> transform ─> validate ─> prepare ─> submit
```

Disabling an option skips that step entirely. For example, setting `transform=False` means the program
will not undergo any device-specific gate set transformations before validation.

<Info>
  API Reference:{" "}
  <a
    href="https://sdk.qbraid.com/qBraid/stubs/qbraid.runtime.RuntimeOptions.html#qbraid.runtime.RuntimeOptions"
    target="_blank"
  >
    qbraid.runtime.RuntimeOptions &#8599;
  </a>
</Info>

## Transform

The `QuantumDevice.transform` step applies device-specific transformations to the program. This is where
gate decompositions, topology mapping, and other hardware-aware compilation passes are performed. The base
class implementation is a no-op — each provider overrides `transform()` with its own logic.

Setting `transform=False` skips this step:

```python
device.set_options(transform=False)
```

### IonQ

The `IonQDevice.transform` method decomposes the input OpenQASM program into the IonQ native gate set.
It loads the program, applies gate mappings (single-qubit, two-qubit, and three-qubit), and falls back to
`pyqasm.unroll()` if the initial transformation fails:

```python
from qbraid.runtime import QbraidProvider

provider = QbraidProvider()

device = provider.get_device("ionq:ionq:sim:simulator")

# By default, transform=True, so the circuit is automatically
# decomposed into the IonQ native gate set (gpi, gpi2, ms, zz, etc.)
job = device.run(qasm_program, shots=100)
```

To skip the IonQ gate decomposition and submit the program as-is:

```python
device.set_options(transform=False)

job = device.run(qasm_program, shots=100)
```

### IBM

The `QiskitBackend.transform` method runs the program through a Qiskit `PassManager`
to produce an ISA (Instruction Set Architecture) circuit compatible with the target backend.
By default, it uses `generate_preset_pass_manager(backend=...)`, but you can supply your own:

```python
from qiskit.transpiler import PassManager

device.set_options(pass_manager=my_custom_pass_manager)
```

See the [Provider-Specific Options](#provider-specific-options) section for more details on the `pass_manager` option.

### AWS

The `BraketDevice.transform` method applies provider-aware transformations. For IonQ devices accessed
through Amazon Braket, it routes the circuit through pytket for an expanded gate set, then applies
Braket-specific transformations. For other Braket-supported devices, it applies standard device transformations
through the `load_program` interface.

### Quobly

The `QbraidDevice.transform` method is a **no-op** for `qbraid:quobly:sim:alloy-forge`. Programs reach
Quobly's Alloy Forge emulator exactly as written, and decomposition into the native
`RX` / `RY` / `RZ` / `RZZ` gate set happens on Quobly's side after submission. An `h`/`cx` circuit is
therefore submitted as `h`/`cx`.

One consequence is worth knowing before you submit: because no coupling map is published for this
device, neither the transform nor the validate step routes a two-qubit gate between non-adjacent
qubits on its linear array. Such a gate still runs and still returns results under the indices you
wrote, but satisfying the connectivity costs extra native two-qubit gates, which the Pioneer noise
model charges for.
See [Quobly Alloy Forge](https://docs.qbraid.com/v2/sdk/user-guide/providers/quobly#native-gates-and-the-coupling-map).

## Validate

The validate step verifies that the run input satisfies all criteria for submission to the target device. This
includes checks such as ensuring the number of qubits in the circuit does not exceed the device's capacity, and
that the program conforms to the device's `ProgramSpec`.

Validation behavior is controlled by the `ValidationLevel` enum:

| Level                   | Value | Behavior                                            |
| ----------------------- | ----- | --------------------------------------------------- |
| `ValidationLevel.NONE`  | `0`   | No validation is performed                          |
| `ValidationLevel.WARN`  | `1`   | Warnings are issued if validation fails             |
| `ValidationLevel.RAISE` | `2`   | Exceptions are raised if validation fails (default) |

<Info>
  API Reference:{" "}
  <a
    href="https://sdk.qbraid.com/qBraid/stubs/qbraid.runtime.ValidationLevel.html#qbraid.runtime.ValidationLevel"
    target="_blank"
  >
    qbraid.runtime.ValidationLevel &#8599;
  </a>
</Info>

### Validation in action

By default, validation is set to `RAISE`. If a program violates device constraints, a
`ProgramValidationError` is raised:

```python
from qbraid.runtime import QbraidProvider

provider = QbraidProvider()

device = provider.get_device("aws:rigetti:qpu:cepheus-1-108q")

job = device.run(program, shots=100)
# ProgramValidationError: Number of qubits in the circuit (100) exceeds the device's capacity (84).
```

### Disabling validation

To skip validation entirely, set the validation level to `NONE`. You can use either the enum or
pass `False` as a shorthand:

```python
from qbraid.runtime import ValidationLevel

# Using the enum
device.set_options(validate=ValidationLevel.NONE)

# Or using the bool shorthand
device.set_options(validate=False)

job = device.run(program, shots=100)
```

### Downgrading to warnings

To receive warnings instead of errors, set the validation level to `WARN`:

```python
device.set_options(validate=ValidationLevel.WARN)

job = device.run(program, shots=100)
# UserWarning: Number of qubits in the circuit (100) exceeds the device's capacity (84).
```

### Re-enabling validation

To restore the default strict validation behavior:

```python
# Using the enum
device.set_options(validate=ValidationLevel.RAISE)

# Or using the bool shorthand
device.set_options(validate=True)
```

## Prepare

The prepare step serializes the quantum program into the intermediate representation (IR) required
for submission to the target device's API. This might produce a JSON payload, an OpenQASM string,
bytecode, or any other format expected by the provider.

The base class implementation delegates to `ProgramSpec.serialize()`, which is defined per-provider.
For example, Pasqal Pulser sequences are serialized into a JSON-based abstract representation, and
OpenQASM programs may be wrapped into a `Program` object with format and data fields.

Setting `prepare=False` skips this step, leaving the program in its current in-memory representation:

```python
device.set_options(prepare=False)
```

This can be useful during debugging or when you want to inspect the transformed program before
it gets serialized:

```python
# Disable prepare and submit to inspect the post-transform program
device.set_options(prepare=False)

# apply_runtime_profile runs transpile, transform, and validate
# but skips serialization
processed = device.apply_runtime_profile(program)
print(type(processed))  # Still a circuit object, not serialized IR
```

## Provider-Specific Options

Providers can extend the default options with their own fields. These additional options
are merged into the device's configuration at initialization and follow the same `set_options` interface.

### IBM `pass_manager`

The `QiskitBackend` adds a `pass_manager` option that accepts a Qiskit `PassManager` instance (or `None`).
When set, the custom pass manager is used during the transform step instead of the default preset pass manager:

```python
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import Optimize1qGates, CXCancellation

# Create a custom pass manager
custom_pm = PassManager([Optimize1qGates(), CXCancellation()])

device.set_options(pass_manager=custom_pm)

job = device.run(circuit, shots=100)
```

Reset to the default behavior by setting `pass_manager` back to `None`:

```python
device.set_options(pass_manager=None)
```

The `pass_manager` option includes a built-in validator that only accepts `None` or a `PassManager` instance.
Attempting to set it to any other type raises a `ValueError`.

## Advanced: RuntimeOptions

Under the hood, device options are managed by the `RuntimeOptions` class, a dataclass-like container
with dictionary-style access, dynamic field support, and custom validators. While `device.set_options()`
is the primary interface for users, understanding `RuntimeOptions` can be useful when
[writing a new provider](https://docs.qbraid.com/v2/sdk/user-guide/runtime/new-provider).

### Initializing with custom fields

```python
from qbraid.runtime.options import RuntimeOptions

options = RuntimeOptions(transpile=True, custom_field=42)

options["custom_field"]
# 42
```

### Adding dynamic fields

Fields can be added at any time using attribute or dictionary syntax:

```python
options["new_field"] = "hello"
options.another_field = 99

print(options)
# RuntimeOptions(transpile=True, custom_field=42, new_field='hello', another_field=99)
```

### Removing dynamic fields

Dynamic (non-default) fields can be deleted. Default fields cannot be removed:

```python
del options["new_field"]       # OK - dynamic field
del options["another_field"]   # OK - dynamic field
del options["transpile"]       # KeyError: Cannot delete default field 'transpile'.
```

### Setting validators

Validators are callables that return `True` for valid values. Once set, every update to the field is
checked against the validator:

```python
options = RuntimeOptions(threshold=0.5)
options.set_validator("threshold", lambda x: isinstance(x, float) and 0 <= x <= 1)

options.threshold = 0.8   # OK
options.threshold = 1.5   # ValueError: Value '1.5' is not valid for field 'threshold'.
options.threshold = "abc" # ValueError
```

If a validator already exists and the current value does not satisfy the new validator, a `ValueError`
is raised. You must update or delete the field first before replacing the validator:

```python
options = RuntimeOptions(count=5)
options.set_validator("count", lambda x: x > 0)

# This will raise because the current value 5 does not satisfy the new validator
options.set_validator("count", lambda x: x > 10)
# ValueError: Existing value '5' for field 'count' is not valid for the new validator.
```

### Merging options

Providers use `merge()` to combine custom options with the device defaults. The `override_validators`
parameter controls whether validators from the merged options replace existing ones:

```python
defaults = RuntimeOptions(transform=True, validate=2)
custom = RuntimeOptions(validate=0)

defaults.merge(custom, override_validators=False)

defaults["validate"]
# 0
```

This is what happens internally when you pass `options` to a `QuantumDevice` constructor, as
shown in the [IBM `pass_manager` example](#ibm-pass_manager).
