# cd_sign Python-semantics proof

[CdSignPythonSemantics.v](../../../proofs/CdSignPythonSemantics.v) proves,
for every Cayley-Dickson dimension 2^k, that the Python function
`cd_core.cd_sign` returns the tower sign sigma_k of
[CdTowerBasisSign.v](../../../proofs/CdTowerBasisSign.v). It does so by
running the function's own syntax tree under a Rocq semantics of the
Python subset that function uses. Every sign proof built on sigma (the
[tower basis-sign](../cd-tower-basis-sign/README.md),
[sign-row ANF](../cd-sign-row-anf/README.md),
[associator-phase ANF](../cd-associator-anf/README.md) and
[census](../cd-associator-census/README.md) bundles) therefore reaches the
Python source through a proof for every k. Before, it reached it through
the finite bridge `tower_bridge.py`, which compares sigma with cd_sign
through dimension 64 and stays as an independent cross-check.

## From the source to the term

[cd_sign_rocq_ast.py](../../../scripts/cd_sign_rocq_ast.py) reads
`gororoba_quantum/cd_core.py` with `ast.parse` and writes `cd_sign_ast`
into the `.v` file, one Rocq constructor per ast node, between generated
markers:

- **Statements:** `Expr`, `Assign` to one name, `AugAssign` of a name, `If`,
  `While` without `else`, `Pass` and `Return`.
- **Expressions:** `Name`, int `Constant`, `BinOp` (`Sub`, `RShift`),
  `UnaryOp` (`Not`, `USub`), `BoolOp` (`And`), `Compare` with one operator,
  and `Call` of a bare name with positional arguments.

The extractor rejects any other node with an error rather than dropping it.
The one node it omits is the leading docstring, which becomes `__doc__` and
runs no statement (Language Reference chapter 8, footnote 4). It writes the
same term a second time with the high-low branch's `if q != 0:` guard
removed, as `cd_sign_mutant_ast`. That is the mutation
`scripts/cd_phase_degree.py --mutate high-low-unconditional` makes.

The term is built from the syntax tree, not from CPython bytecode. The
syntax tree is the level at which the Language Reference defines Python's
semantics. The `ast` module documents that the abstract syntax can change
between releases, so the extractor check runs on every pull request, and
the extractor rejects a node it does not map. For cd_sign's own definition, `ast.dump` is byte-identical under Python
3.13.15 (the Quantum Inspire interpreter's minor version) and 3.14.8. The
compiled bytecode is not identical: it has 95 instructions under 3.13.15
and 100 under 3.14.8, with different `co_code` digests. The extractor writes
the same Rocq term under 3.11.17, 3.13.15 and 3.14.8.

## Semantics

Values are integers. Python's False and True are 0 and 1, which is how
Booleans behave as numbers (Language Reference 3.2.4.1). The evaluator
follows these sections of the Language Reference:

| Construct | Section | Rule the evaluator implements |
| --- | --- | --- |
| Unary arithmetic `-x`, `not x` | 6.6, 6.11 | negation; `not` returns a bool from the operand's truth value |
| Subtraction | 6.7 | integer difference |
| Right shift | 6.8 | floor division by 2^n; a negative count raises ValueError (Library Reference, "Bitwise Operations on Integer Types") |
| Comparisons | 6.10, 6.10.1 | one operator, returns a bool |
| `and` | 6.11 | returns x when x is false, else y |
| Expression, assignment, augmented assignment, `pass`, `return` | 7.1, 7.2, 7.2.1, 7.4, 7.6 | one local scope; an unbound name raises |
| `if`, `while` | 8.1, 8.2 | branch and repeat on the test's truth value |

Each nested block and each further loop iteration spends one unit of fuel.
`builtin` gives the two guard calls their behavior on int arguments, as
written in cd_core:

- `_dimension` raises unless dim >= 1 and dim & (dim - 1) = 0;
- `_index` raises unless 0 <= index < dim, and otherwise returns index.

| Theorem | Statement |
| --- | --- |
| `cd_sign_returns_sigma` | for every k, p, q < 2^k and fuel >= k + 7: cd_sign(2^k, p, q) returns sigma_k(p, q) |
| `cd_sign_raises_dimension` | a dim failing the `_dimension` guard raises |
| `cd_sign_raises_index` | with a valid dim, an index failing the `_index` guard raises |
| `dimension_guard_pow` | the `_dimension` guard admits exactly dim = 2^(log2 dim) |
| `cd_sign_spec` | for every int dim, p, q: returns sigma_(log2 dim)(p, q) when all three guards pass and raises otherwise |
| `cd_sign_mutant_differs` | the mutant returns -1 at e_1 e_0 in dimension 2, where sigma_1(1, 0) = 1 and cd_sign returns 1 |

The induction runs over the remaining levels. `body_step` evaluates one
iteration with half = 2^j in the four branches of the if/elif chain. Each
branch either returns, or leaves p, q, sign and half in the state that
`cd_sign_loop` recurses on one level down. `loop_spec` chains the
iterations, and `cd_sign_loop_sigma` of the tower bundle turns the result
into sigma.

## Trust

The theorems rest on the type theory that `rocq check` re-verifies
([kernel.txt](kernel.txt)), identical to the other Cayley-Dickson bundles'.
Beyond the kernel, the proofs use the definitions and proved lemmas of
Corelib and Stdlib 9.2.0: integer and natural-number arithmetic through
`lia`, `Z.land`, `Z.shiftr`, `Z.log2` and `Z.testbit` with their lemmas,
and `String.eqb`. Each of the six assumption queries in
[assumptions.v](assumptions.v) prints `Closed under the global context`
([assumptions.txt](assumptions.txt)).

Three readings remain outside the proof, each with a check that fails when
it breaks:

- **The node map.** The pytest contract
  [test_cd_sign_rocq_ast.py](../../../tests/scripts/test_cd_sign_rocq_ast.py)
  fails when the embedded term differs from the source. It also fails when
  the mutation or a changed shift count leaves the term unchanged, and when
  an unsupported construct is not rejected.
- **The guard clauses.** The same contract pins the `ast.dump` digests of
  `_dimension` and `_index`, on Python 3.13 or later. It checks both guards
  against the Rocq clauses on every int dim and index from -3 to 70.
- **The evaluator's reading of the Language Reference sections above.**

The theorems cover arguments of exact type int. Python lets an int subclass
override every operator, so an object that passes `isinstance(dim, int)`
need not compute as an integer: a subclass whose `&` returns 0 passes a
power-of-two test at dim 6, and one whose `>>` returns 0 skips the loop
and returns +1 for e_1 e_1 in dimension 4, where sigma is -1.
`_dimension` therefore tests `type(dim) is not int` before it applies any
operator to dim, which rejects bool and every int subclass, IntEnum
included. `_index` passes each index through `operator.index`, which since
Python 3.10 returns an exact int and reads an int subclass's value without
calling its overrides. Every call that reaches the loop therefore applies
int's own operators to ints, the domain the theorems cover. The contract
checks both guards against these subclasses.

`Raised` records that an exception occurs, not its class, message or
traceback; the pytest contract pins ValueError for every guard rejection.
A fuel bound counts evaluator steps and is no bound on Python's time or
memory.

Executable semantics of Python exist: K-Python, Dwight Guth's semantics of
Python 3.3 in the K framework (Illinois M.S. thesis,
https://github.com/runtimeverification/python-semantics, to which
github.com/kframework/python-semantics redirects), and lambda-py, from Politz
et al., "Python: The Full Monty", OOPSLA 2013
(https://doi.org/10.1145/2509136.2509536). Neither targets Rocq 9.3, so
this proof depends on neither. The evaluator here covers only the
constructs cd_sign uses, and proves its result for every input.

## Certified source-AST successor

The [source-AST translation bundle](../cd-sign-python-translation/README.md)
adds a generic serialization of the complete Python AST, an independently
defined interpreter of that raw tree, and a Rocq proof that every accepted
translation certificate preserves the target evaluator's modeled execution.
It lifts the sign and guard theorems here to the retained raw source AST.
The semantic node map is therefore covered by a proof between two explicit
integer calculi. CPython parsing, generic serialization, the fixed helper
contracts and their correspondence to Python execution retain the stated
external trust. This earlier proof and extractor keep their original bytes.

## Replay

```sh
ROCQ="${ROCQ:-rocq}" sh docs/evidence/cd-sign-python-semantics/replay_rocq.sh
export PYTHON="${PYTHON:-python3}"
"$PYTHON" scripts/cd_sign_rocq_ast.py --check
sha256sum -c docs/evidence/cd-sign-python-semantics/source_hashes.sha256
```

`replay_rocq.sh`:

- requires the banner of [toolchain.txt](toolchain.txt): Rocq 9.3.0 on
  OCaml 5.5.1, the switch of `ci/rocq_toolchain.pin`;
- compiles the three proof sources and [assumptions.v](assumptions.v) in
  temporary storage with `-w @all`, and fails on any warning or compiler
  output;
- runs `rocq check`, and compares the outputs byte for byte with the
  receipts.

The replay takes about 45 s on the build host, and the ci.yml job
rocq-replay runs it. Gate sources-406 runs the extractor check, and
`source_hashes.sha256` binds the proof sources, the extractor and the
receipts. `"$PYTHON" scripts/cd_sign_rocq_ast.py --write` regenerates both
terms after an edit to cd_sign; the proofs then have to be replayed.
