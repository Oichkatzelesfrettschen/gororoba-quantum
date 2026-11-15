# Rocq replay and generator route

Retained replay bundles under `docs/evidence/` (the `cd-*` bundles, `formal_certificates`,
`c881_exhaustive`, `stiefel_witness`, `folding_proofs`) keep their bytes, and their READMEs describe
the route that ran when the bundle was written. This repository compiles no Rocq and runs no Rocq
workflow. gororoba-math holds the proof sources, the generators of the rendered sources, the toolchain
installer and the replay driver. This document is the single statement of the route that replaces the
names those READMEs carry; each affected row of [the documentation map](../README.md) links here.

## Where each removed name went

| Name in a retained README or record | Current route (paths in gororoba-math) |
| --- | --- |
| `scripts/rocq_kaggle_replay.py`, with `--only NAME` | `ci/replay_quantum_bundles.sh [--ledgers-only] [NAME...]`; a NAME is a directory of `docs/evidence/` that holds a `replay_rocq.sh`, or `TargetFlipN21` |
| `ci/rocq_toolchain.pin`, the opam switch of the replay | `ci/install_rocq.sh` builds the opam switch `rocq-9.3` (OCaml 5.5.1, rocq-core 9.3.0, rocq-stdlib 9.2.0); `rocq/open/opam/qualified-rocq-9.3.export` records the package set |
| the `proofs.yml` job `rocq` and the nightly Rocq job | no workflow here; the replay runs on demand, outside every admission gate, and `ci/check_rocq.sh` of gororoba-math compiles and kernel-checks `rocq/quantum` on its own pull requests |
| `scripts/stiefel_witness_certificate.py`, gate `core-275` | `ci/quantum-sources/stiefel_witness_certificate.py`, run with `--check` by `ci/check_quantum_sources.sh` |
| gate `core-067` (`target_flip_certificate --check`) | `ci/quantum-sources/target_flip_certificate.py`, run by `ci/check_quantum_sources.sh` |
| gate `sources-406` (`cd_sign_rocq_ast --check`) | `ci/quantum-sources/cd_sign_rocq_ast.py`, run by `ci/check_quantum_sources.sh` |
| gate `sources-411` (`cd_sign_source_ast --check`, the raw AST and source identity of `cd_sign`) | `ci/quantum-sources/cd_sign_source_ast.py`, run by `ci/check_quantum_sources.sh` |
| `scripts/math_source_generators.py` and the gates `sources-cd-tower-kernel-certificates-check`, `sources-a5-gaussian-certificates-check` and `sources-a5-gaussian-certificates-span-check` | `ci/check_quantum_sources.sh`, which renders each generated source of `rocq/quantum` again and requires it to equal the tracked file |
| gate `sources-a5-gaussian-certificates-span-driver-shellcheck` (`run_span_checks.sh`) | `ci/check.sh` of gororoba-math lints the tracked shell file `ci/quantum-sources/run_span_checks.sh` |

## Running it

Both scripts read this checkout and run from a gororoba-math checkout. `GOROROBA_QUANTUM` names this
repository's checkout:

```sh
GOROROBA_QUANTUM=PATH sh ci/check_quantum_sources.sh
GOROROBA_QUANTUM=PATH sh ci/replay_quantum_bundles.sh --ledgers-only
GOROROBA_QUANTUM=PATH opam exec --switch=rocq-9.3 -- sh ci/replay_quantum_bundles.sh [BUNDLE...]
```

`--ledgers-only` compares each `*.sha256` row that reads `proofs/NAME.v` with `rocq/quantum/NAME.v` and needs
no Rocq. Without it the script runs each bundle's `replay_rocq.sh` unchanged from a shadow root that holds a
copy of the bundle and of `rocq/quantum` as `proofs/`. A bundle whose script reads `GOROROBA_ROOT` (the
gororoba-open sources) needs that variable set. `ci/check_quantum_sources.sh` needs python-flint under
`PYTHON`. Both runs write only under a temporary directory.

## What stays in this repository

- Each retained generator that a ledger binds keeps its bytes as the record of the commit the ledger names
  ([AGENTS.md](../../AGENTS.md#layout-and-gates)); the live generator is the file of the same name in
  gororoba-math `ci/quantum-sources/`, and a change to a rendered source lands there, in the same commit
  as the source.
- `gororoba_quantum/math_sources.py`, `ci/gororoba_math.pin` and `ci/fetch_gororoba_math.sh` verify the
  sources that retained ledgers and `docs/state/research_state.json` cite, each against its recorded sha256.
- The `sha256sum -c` ledgers of the bundles (`sources-*` gates of `ci/gates.json`) check bundle bytes and
  fail on a difference; they re-derive nothing.
- A claim of `docs/state/research_state.json` for a gororoba-math source cites its pinned evidence, which
  `scripts/research_state.py --check` verifies. It names no replay or freshness gate of this repository.
