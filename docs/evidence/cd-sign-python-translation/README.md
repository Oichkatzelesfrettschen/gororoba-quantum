# Certified translation of the cd_sign AST

This bundle connects a generic serialization of the Python source AST to
the target program proved by
[CdSignPythonSemantics.v](../../../proofs/CdSignPythonSemantics.v).
It adds an independent interpreter of the raw AST and proves that every
accepted translation certificate preserves execution under the specified
integer semantics. The original semantic node map therefore no longer
rests solely on the extractor's tests.

The proof is in
[CdSignAstTranslation.v](../../../proofs/CdSignAstTranslation.v). The
concrete source trees, their certificates, and the source-level sign
theorems are in
[CdSignSourceCertificate.v](../../../proofs/CdSignSourceCertificate.v).
The earlier proof and extractor retain their bytes.

## What the certificate establishes

[cd_sign_source_ast.py](../../../scripts/cd_sign_source_ast.py) parses
`cd_core.py` and serializes the selected function generically with
`ast.iter_fields`. Node tags, named fields, contexts, lists and typed
integer, Boolean, string and `None` atoms remain data. The exporter has
no map from Python constructs to target-language constructors. It retains
the complete function AST, including annotations and its docstring, and
the SHA-256 identity of the full source file.

Inside Rocq, `function_certificate` compares the function's positional
parameter names and executable body with an independently defined
quotation of the target term. Exact structural equality checks field
names, operand order, load/store contexts, operators and statement order.
Unsupported executable nodes cannot match the quotation.

The source interpreter dispatches directly on those raw node tags. It
does not invoke the target evaluator or translate a tree before running
it. Expression and block preservation are proved first. Certificate
soundness then yields the function-level theorem:

```text
function_certificate raw target = true
    -> source_run fuel raw args = run fuel target args
```

The result holds for every argument list and evaluator fuel value in the
declared integer abstraction. It preserves normal completion, returned
integers, abstract exceptions and fuel exhaustion, including short
circuiting and early returns.

| Public theorem | Conclusion |
| --- | --- |
| `expression_semantic_preservation` | Raw quotations of expressions preserve values and abstract failure |
| `block_semantic_preservation` | Raw quotations of statement blocks preserve outcomes at every fuel value |
| `function_certificate_sound` | An accepted certificate identifies the target's parameter order and executable body exactly |
| `function_semantic_preservation` | Accepted source and target have identical modeled execution outcomes |
| `cd_sign_source_returns_sigma` | For every level $k$, valid $p,q<2^k$, and fuel at least $k+7$, the raw source returns the tower sign |
| `cd_sign_source_spec` | The original all-integer-input specification, including abstract guard failures, holds for the raw source |
| `cd_sign_source_mutant_differs` | The high-low guard mutation returns $-1$ on the retained witness where the source and tower sign return $+1$ |

The concrete certificate also proves that the nominal source matches the
nominal target, the guard mutant matches its mutant target, and neither
that guard mutant nor a changed final shift matches the nominal target.
These are kernel-checked decisions. The Python tests separately check the
generic serialization, type distinctions, escaping, unique function
selection, source identity and mutation sensitivity.

## Remaining trust and scope

The semantic preservation theorem closes the translation between two
explicitly defined calculi. It does not prove that CPython implements
either calculus. The remaining boundaries are:

- **Parsing and serialization.** CPython's parser, selection of the named
  top-level definition, the generic serializer, file reading and SHA-256
  calculation remain externally checked. The `--check` mode compares the
  complete generated block and source digest; it is not a verified parser
  or a proved hashing implementation. The digest covers the source text of
  `cd_sign` and of every top-level statement binding a module-level name it
  reaches, transitively, in source order: the `integer_index` import,
  `_dimension`, `_index` and `cd_sign` itself. An edit to that closure, or a
  later top-level rebinding of one of its names, changes the digest; an edit
  elsewhere in `cd_core.py` does not. Selecting the closure by name is part
  of this externally checked step.
- **Primitive and helper contracts.** Both interpretations use mathematical
  integer arithmetic and the existing `_dimension` and `_index` contracts.
  The new proof does not formalize those helpers' Python implementations.
  The earlier [guard tests and source digests](../cd-sign-python-semantics/README.md#trust)
  remain relevant. Bare helper calls assume those fixed contracts.
- **Values and outcomes.** Booleans are represented numerically, and
  exceptions record occurrence rather than class, message or traceback.
  `_dimension`'s successful result is represented as zero because this
  program discards it; this is not a general semantics for Python `None`.
  The source-level specification is about exact integer arguments in that
  abstraction, with the original explicit fuel bound.
- **Function invocation.** The function view checks positional parameters
  and the executable body. It retains function names, annotations and the
  initial docstring as metadata. The theorem covers invocation after
  function definition, not module execution or annotation evaluation.
  Decorators, positional-only parameters, defaults, variadics, keyword-only
  parameters and nonempty type parameters are rejected by this view.
- **Implementation resources.** Evaluator fuel is not a bound on Python
  execution time or memory. Arbitrary Python objects, operator overrides,
  helper rebinding and CPython's C implementation are outside the theorem.

Consequently, the certified connection is from the retained raw AST to
the previous evaluator and then to the tower sign. The proof does not
remove the need to justify that the chosen integer abstraction describes
the intended Python execution.

The implementation was produced with AI assistance and independently
reviewed against the old evaluator, the concrete source and the stated
trust boundary. The kernel receipts determine which theorems were checked.

## Replay and source binding

The toolchain is Rocq 9.3.0, OCaml 5.5.1 and Stdlib 9.2.0, as recorded by
[toolchain.txt](toolchain.txt) and
[ci/rocq_toolchain.pin](../../../ci/rocq_toolchain.pin).

```sh
export PYTHON="${PYTHON:-python3}"
"$PYTHON" scripts/cd_sign_source_ast.py --check
ROCQ="${ROCQ:-rocq}" sh docs/evidence/cd-sign-python-translation/replay_rocq.sh
sha256sum -c docs/evidence/cd-sign-python-translation/source_hashes.sha256
```

The exporter runs on the repository's pinned Python interpreter. The
replay compiles all five proof modules in temporary storage with `-w @all`,
rejects warnings and unexpected compiler output, runs the seven queries
in [assumptions.v](assumptions.v), and independently kernel-checks the
source certificate and its dependencies. Raw outputs are compared with
[assumptions.txt](assumptions.txt) and [kernel.txt](kernel.txt).

The source ledger includes both exporters, all proof dependencies, the
replay script and the receipts. It leaves out `cd_core.py` itself, whose
bound bytes are the helper closure that the certificate's
`cd_sign_source_sha256` records and `sources-411` recomputes. The old exporter
is included because the new one imports its mutation constants. Source
gate `sources-411` checks the raw AST and source identity; gates
`sources-409` and `sources-410` check the replay script and bound bytes.
The nightly Rocq job runs the complete replay.
