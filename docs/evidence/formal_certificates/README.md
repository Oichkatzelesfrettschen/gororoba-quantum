# Fold and terminal-channel proof certificates

These sources prove a scalar information-loss obstruction and a conditional
incompatibility of observed terminal means with a common appended binary
channel. The [dependency plan](../../notes/formal_evidence_dependencies.md)
separates remaining algebra, circuit, statistical and physical obligations.

| Source | Checked statement | Boundary |
| --- | --- | --- |
| [FoldAverageDescent.v](../../../proofs/FoldAverageDescent.v) | Every operation on averages alone fails to reproduce projected scalar-pair multiplication; average/detail coordinates have two inverse identities and are injective | Canonical rational pairs; the general Cayley-Dickson embedding and zero-product bridge remain open |
| [TerminalChannelSeparation.v](../../../proofs/TerminalChannelSeparation.v) | Rational binary-channel contraction, exact positive margin and conditional exclusion | Rational `Qeq` semantics; three exported assumption queries are closed |
| [TerminalChannelSeparationReal.v](../../../proofs/TerminalChannelSeparationReal.v) | The same contraction and exclusion for real-valued means, with an explicit interval lemma | Unknown physical probabilities may be real; standard real-foundation assumptions are retained below |

The fold source has eight closed assumption queries. The rational channel
source has three. Each of the real source's four queries lists exactly:

```text
ClassicalDedekindReals.sig_forall_dec
FunctionalExtensionality.functional_extensionality_dep
```

The full imported-library real kernel context additionally lists
`ClassicalDedekindReals.sig_not_dec` and `Classical_Prop.classic`.
Theorem-specific dependencies and the imported library context are different
evidence surfaces; both raw outputs are retained. The rational kernel
contexts list zero axioms. Every kernel check reports zero type-in-type
dependencies, unsafe fixpoints or assumed positivity.

The three kernel receipts preserve Rocq's emitted whitespace. Their local
`.gitattributes` entries disable whitespace checks for those exact output
files; source and documentation whitespace checks remain enabled.

## Data and inference boundary

The source fixes hardware counts `2964,4911` and replay counts `4067,4057`,
each divided by `8192`, from the retained
[terminal-channel record](../../../results/live/2026-10-12T055624.091217Z/terminal-channel-check.json).
The record's binary fractions convert exactly to those integers. Its
source hash is bound alongside the proof sources in `source_hashes.sha256`.
The existing raw-decoder/source-closure gates remain separate provenance
checks. A manual fixture correspondence is narrower than a Rocq-verified
parser for the original shot records.

Both exclusion theorems assume four true means lie within `21/1000` of the
observations. They prove the positive gap
`156109/1024000 = 0.1524501953125`. The proofs establish neither a coverage
probability nor independence, stationarity, calibration validity or replay
accuracy. A concentration theorem and certified numerical bound comparison
remain necessary before attaching a confidence level to this certificate.
The hypothesis appends one common stochastic channel to the replay means;
replacement readout and context-dependent instruments have different models.

## Replay

Use the toolchain `toolchain.txt` records, Rocq 9.2 with OCaml 5.5.0. The
receipts were first recorded under Rocq 9.1.1 with OCaml 5.4.0; a fresh
compile and kernel check under 9.2 reproduce every compile and kernel
receipt byte for byte, so the pin moved forward with the files unchanged.
Set `ROCQ` to that toolchain's executable when another version is first on
PATH, then run from the repository root:

```sh
ROCQ="${ROCQ:-rocq}" sh docs/evidence/formal_certificates/replay_rocq.sh
```

The script verifies retained hashes, copies only the three `.v` sources into
new temporary storage, compiles with `-q -w @all`, runs independent
`rocq check -silent -o` checks, and compares compiler/assumption and kernel
outputs byte-for-byte with the retained receipts. All warnings cause failure.
The exit trap removes only that invocation's temporary directory. Compiled
proof objects remain outside the repository.

`verification_receipt.json` records flags, versions, theorem assumptions and
exit statuses. `SHA256SUMS` binds the README, replay script, source-hash
manifest, receipt and raw outputs. Changing a theorem requires fresh
compilation, kernel checking, assumption inspection and receipt renewal.
