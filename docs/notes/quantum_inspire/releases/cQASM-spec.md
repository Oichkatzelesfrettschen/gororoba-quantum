> Full piece: [https://github.com/QuTech-Delft/cQASM-spec/releases](https://github.com/QuTech-Delft/cQASM-spec/releases)
> Retrieved 2026-10-16T22:00Z by scripts/capture_qi_docs.py --releases (urllib, REST API);
> 2 releases, newest first, bodies verbatim; data in [cQASM-spec.json](cQASM-spec.json).

# cQASM-spec releases

## Feature release 3.0-beta2

Tag `3.0-beta2`, 2025-02-18T10:25:39Z: <https://github.com/QuTech-Delft/cQASM-spec/releases/tag/3.0-beta2>

### Added

- `init` non-unitary instruction
- `SWAP` two-qubit unitary instruction
- `barrier` and `wait` control instructions
- Gate modifiers
  - inverse `inv`
  - power `pow()`
  - control `ctrl`

## Feature release 3.0-beta1

Tag `3.0-beta1`, 2024-10-16T14:04:51Z: <https://github.com/QuTech-Delft/cQASM-spec/releases/tag/3.0-beta1>

The first (beta) release of the new cQASM language.

Main changes with respect to previous cQASM versions are:

- Case sensitive syntax
- Decoupled qubit and bit registers
- Qubit and bit register variable declarations
- `q` and `b` are no longer reserved characters
- Assignment of measurement outcomes to bit variables
- No component (e.g. translator/compiler/simulator) specific directives (for now)
- Single-line comments through double-slash notation (`//`), instead of the hashtag notation (`#`)

For a full description of the new language we refer to its [online specification](https://qutech-delft.github.io/cQASM-spec/).

> **Note**: that this version of cQASM is not backwards compatible with previous versions of the language.
