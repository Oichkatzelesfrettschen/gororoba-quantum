# Hybrid Shor architecture for IBM Heron r2

This repository now carries a bounded, end-to-end Shor decomposition. The
classical host performs deterministic preprocessing, coefficient extraction,
resource admission, exact order validation, and factor extraction. An IBM
Heron r2 backend receives only the semiclassical order-finding circuit selected
after live calibration and compilation. The implementation submits a circuit
only through `live_run.py --submit`, after the written approval gate in
`AGENTS.md`.

The current executable frontier is `N = 15`, `a = 2`. That case provides a
faithful `|1>` order-finding input and a real continued-fraction decoder. Its
Mersenne arithmetic remains classically easy, so the result establishes
implementation conformance rather than quantum advantage. `N = 21` and
`N = 35` expose the generic synthesis boundary and the work needed to move it.

## Evidence levels

The project keeps four evidence levels separate.

1. **Exact host evidence.** Exhaustive basis-state checks prove each bounded
   modular permutation, each ANF reconstruction, each controlled multiplier,
   and every scratch-workspace restoration. Aer verifies the phase support and
   factor decoder.
2. **Compiler evidence.** FakeFez compilation measures width, CZ count, depth,
   layout, and recursive control-flow operation census against the pinned
   Qiskit stack. The pass callback separates high-level synthesis, basis
   translation, routing, and final optimization. The fake backend supplies a
   static target snapshot rather than a prediction of live noise.
3. **Live dry-run evidence.** `live_run.py` discovers the requested systems,
   refreshes their status, Targets, properties, and submission capabilities,
   derives the hybrid group's requirements from circuits built in the current
   process, removes degraded hardware from routing, validates each compiled
   operation, selects a valid layout, and runs local noise simulation. The dry
   run spends zero QPU time.
4. **QPU evidence.** A submitted and collected run measures the circuit on a
   calibrated device and replays its execution-time calibration. The first
   such run is record `results/live/2026-10-11T152922.787095Z` (ibm_kingston,
   job `db5qmqclf4us73c4e1ug`, 9 QPU seconds), approved on the written case
   in `results/live/2026-10-11T121402.617901Z/STEP3_CASE.md` and adjudicated
   from its lossless raw result in the record's `ADJUDICATION.md`.

The repository has submitted one hybrid-Shor QPU job. On hardware the
`N = 15`, `a = 2` order-finding circuit reads a factor yield of 0.4971
[0.4726, 0.5216] against the exact uniform null 0.2969 and an identity-null
yield of 0.0042 [0.0003, 0.0080]: admitted. The raw registers show the
pruned structure the plan predicts, two varying phase bits and six leading
zeros in every shot. The factor-yield endpoint is coarse: it agrees with the
execution-calibration replay (0.4955) while two of the six layouts carry a
coherent bias on the feed-forward-conditioned bit that the Pauli model does
not draw, and the folded-QPE conformance test on the same device reads 0.715
against the model's 0.899. The factor yield is also phase-insensitive: for a
power-of-two order the ideal outcome distribution of the order-finding
circuit does not depend on the conditional phases at all (the control is
entangled with orthogonal work states, so the second bit is uniform
whatever phase is applied; Martin-Lopez et al. 2012, page 2, for r = 2^p),
and every unit modulo 15 has order 2 or 4, so no N = 15 hybrid-Shor circuit
tests the feed-forward. The `order_finding.py` gate compares sampled
outcome frequencies for N = 15, a = 2 with and without conditional phases;
that finite check supports the stated theoretical boundary. The first
hardware record therefore establishes the
controlled arithmetic and the decoder on hardware and nothing about the
semiclassical inverse QFT; folded QPE, whose eigenstate inputs make the
second bit deterministic only under the correct conditional phase, is the
feed-forward test that record contains. For N = 21, a = 4 at two phase
bits (order 3), the [source notes](../docs/notes/1111.4147.md) propose
probabilities (3/8, 1/4, 1/8, 1/4) with feed-forward and
(3/8, 1/8, 1/8, 3/8) without it, in phase-index order (0, 1, 2, 3), a total
variation distance of 1/8. `qpe_diagnostics.py` derives the exact labeled
probabilities, checks circuit branches and sampled labels in phase-index
order `b0 + 2*b1`, and rejects a swapped-register mutation.
`order_finding.py` also checks the sampled frequencies against those labeled
laws. Order recovery is zero at two bits, so the proposed observable is the
labeled distribution; the
[hardware plan](HARDWARE_PLAN.md#hardware-evidence-and-next-cases)
tracks statistical admission and the separate approval boundary. The
[semiclassical-QFT source note](../docs/notes/quant-ph-9511007.md)
grounds the independent coherent-QPE comparison.

## Host and QPU boundary

The pipeline assigns each operation to the least expensive trustworthy
execution surface.

| Stage | Host responsibility | QPU responsibility |
|---|---|---|
| Problem admission | Reject primes, even values, perfect powers, invalid bases, and nontrivial gcd results | None |
| Arithmetic planning | Compute each repeated-square multiplier, extract coefficients, and count resources | None |
| Circuit construction | Build exact controlled permutations and inverse-QFT feedback | Execute the selected dynamic circuit |
| Outcome recovery | Form continued-fraction convergents, validate exact orders, reduce order multiples, and check factor divisibility | Return phase-bit counts |
| Evidence | Compare ideal, identity-null, uniform-null, noise-model, and measured distributions | Supply measurements only after approval |

`hybrid_shor.py` owns the credential-free boundary. Its `plan`, `simulate`, and
`decode` commands never construct `QiskitRuntimeService`. `live_run.py` owns
fresh calibration, compilation, local noise simulation, optional submission,
and collection. This split lets the host reject a problem or a synthesis before
any IBM account lookup or QPU action.

## Exact order-finding decomposition

For an odd composite `N` and a unit `a`, the work register uses

```text
n = bit_length(N)
m = 2*n
```

work qubits and phase bits, respectively. The work register starts in `|1>`.
Semiclassical round `j`, counted from zero, controls the permutation

```text
x -> a^(2^(m-j-1)) * x mod N                 for 0 <= x < N
x -> x                                      for N <= x < 2^n
```

on one recycled control qubit. The identity extension on invalid basis states
makes the map a permutation of the entire register. A measurement, reset, and
classically conditioned phase implement each remaining inverse-QFT step.

The host decoder receives an integer `y` in `[0, 2^m)`. It enumerates the
continued-fraction convergents of `y/2^m`, accepts a denominator only when
`a^r mod N = 1`, divides prime factors out of a valid multiple until it reaches
the exact order, and accepts `gcd(a^(r/2) +/- 1, N)` only after divisibility
checks. Circuit construction receives neither the reference order nor the
expected factors.

## Boolean coefficient bridge

Cayley-Dickson sign circuits and modular arithmetic share a compiler
representation even though they implement different groups. A Boolean truth
table `f(x)` has the algebraic normal form

```text
f(x) = XOR over S of c[S] * product over i in S of x[i].
```

The in-place Boolean Moebius transform extracts the coefficients:

```text
c[S] = XOR over T subset S of f(T).
```

`boolean_anf.py` implements the transform, exact evaluation, degree, and degree
histograms. Cayley-Dickson signs use `c[S]` as phase-polynomial coefficients.
`modular_arithmetic.py` applies the same transform independently to every
output bit of a modular permutation. The shared representation provides the
useful Cayley-Dickson connection: the algebra contributes a proven Boolean
coefficient language and exact compiler sentinels, while modular multiplication
supplies a distinct permutation family.

Cayley-Dickson basis products themselves remain signed XOR translations. Every
nonidentity translation moves zero, while modular multiplication fixes zero.
The signed translations also have exponent at most four. These invariants rule
out direct replacement of Shor's multiplier by a Cayley-Dickson product.

## Multiplier syntheses

### Signed Mersenne rotations

For `N = 2^n - 1`, multiplication by `2^k` rotates the `n` data bits. The
all-ones padding state remains fixed under rotation, so the rotation's wire
permutation implements the full-register extension. A controlled rotation
becomes a short Fredkin network. `N = 15`, `a = 2` uses three controlled swaps
for multiplication by two and two for multiplication by four.

Multiplication by `-2^k` rotates and then inverts every data bit for each
nonzero residue:

```text
NOT(rotate_k(x)) = (2^n - 1) - rotate_k(x) = -2^k*x mod (2^n - 1).
```

The order-finding builder prepares `|1>`, and every admitted multiplier is a
unit, so each circuit branch stays in `1 <= x < N`. The explicit
`nonzero_residues` domain admits the direct Fredkin-plus-CX network. For
`N = 15`, multipliers 14, 13, 11, and 7 use respectively 0, 3, 2, and 3
controlled swaps plus four controlled X gates and zero scratch qubits.

The full-register API preserves both `|0>` and the all-ones padding state.
Bit inversion alone exchanges those endpoints, so the exact synthesis appends
a controlled endpoint transposition with `2*n - 1` Gray-path basis edges. The
endpoint correction also uses zero scratch qubits. Profiles record the input
domain, controlled swaps, controlled X gates, correction edges, and maximum
control count, which keeps the subspace optimization separate from the exact
identity-padded contract.

A positive rotation has `T = 2^(n-gcd(n,k))` XOR-displacement fibers for
multiplier `2^k`, so any nonzero exact scaled LCU over signed XOR translations
has effective normalization at least T. The direct circuit and the LCU
dictionary therefore rank the positive rotation in opposite ways: the direct
circuit needs `n-gcd(n,k)` swaps while the effective LCU normalization grows
exponentially whenever `gcd(n,k)=1`. `FACTORING_NOTES.md` derives the bound and
its non-universal base boundary.

### ANF compute, swap, uncompute

The generic ANF circuit computes the forward output bits into `n` clean scratch
qubits, conditionally swaps the data and scratch registers, and evaluates the
inverse permutation from the new data to clear the scratch register. A monomial
of degree `d` becomes a controlled X with the phase control plus `d` data
controls. The resource ledger records forward and inverse term counts, maximum
degree, the degree histogram, controlled swaps, and the largest control set.

### Cycle transpositions on Gray paths

The scratch-free candidate decomposes the exact permutation into disjoint
cycles. Each cycle chooses the member with minimum total Hamming distance to
the other members as its pivot. A cycle `(p, v1, ..., vk)` becomes the ordered
transpositions `(p, v1), ..., (p, vk)`. A Hamming-distance `d` transposition
walks a Gray path forward and back with `2*d - 1` basis-edge swaps. Each edge
uses the phase control and open or closed controls on every unchanged data bit.

The cycle representation reduces logical width and logical operation count.
The scratch-free form makes every `N = 21` edge a five-control X: one phase
control plus the four unchanged data bits. Qiskit 2.5.2 lowers the six-qubit
candidate with `noaux_v24`; the circuit borrows zero dirty ancillas. The
resulting dense logical interaction demand meets a 156-qubit FakeFez graph
with 176 undirected edges, maximum degree three, and degree census 8 at degree
one, 100 at degree two, and 48 at degree three. The dense-interaction and
degree-three mismatch makes routing, not the 449-edge coefficient count alone,
decisive.

### One-clean cycle transpositions

`cycle_transpositions_1_clean` preserves the same cycles, pivots, Gray paths,
and open-control truth conditions. Each basis edge wraps its zero-valued data
controls in X gates and composes Qiskit's public
`synth_mcx_1_clean_kg24` circuit over one clean workspace qubit. The synthesis
turns each five-control X into six RCCX gates and one CCX gate, then restores
the workspace. Across the complete `N = 21` schedule, 449 basis edges become
2,694 RCCX and 449 CCX gates with zero opaque MCX gates.

Exact operator or statevector checks cover control values zero and one, every
five-bit input, and multipliers 2, 4, and 16. The expected packed output always
contains a zero workspace bit. `auto` selects the one-clean strategy for a
generic multiplier; identity and signed-Mersenne fast paths retain their
zero-workspace implementations. The CLI keeps scratch-free cycle and ANF
strategies explicit as falsifiers.

## Static call and flow map

`scripts/python_call_graph.py` parses the Python 3.11 grammar, compiler symbol
tables, imports, and stable direct calls. Its current complete repository map
contains 16 modules, 276 top-level functions, and 516 direct edges. The
`compile_evidence.main` reachable subgraph contains 39 functions and 50 edges;
the six declared roots jointly reach 135 functions and 234 edges. The relevant
load-bearing paths are:

```text
compile_evidence.main
  -> compile_evidence.capture
    -> compile_evidence._candidate_record
      -> compile_evidence._compile_candidate
        -> compile_evidence._build_source
          -> order_finding.order_finding_plan
            -> modular_arithmetic.multiplier_profile
          -> order_finding.factor_order_finding
            -> order_finding.order_finding_plan
            -> modular_arithmetic.append_controlled_modular_multiply
              -> modular_arithmetic._append_controlled_basis_transposition
                -> modular_arithmetic._append_controlled_basis_edge

hybrid_shor.main
  -> hybrid_shor._plan_payload
    -> order_finding.order_finding_plan
      -> modular_arithmetic.multiplier_profile
  -> hybrid_shor._simulate_payload
    -> order_finding.factor_order_finding
      -> order_finding.order_finding_plan
      -> modular_arithmetic.append_controlled_modular_multiply
```

GNU cflow 1.8 and cscope 15.9 provide negative controls rather than semantic
Python authority. A direct cflow run over the three path modules emits 200
parser diagnostics, including unterminated-string and false-redefinition
reports, and produces only 11 malformed graph lines. cscope builds an index, but
the documented caller query returns one definition-like lexical row. The AST
map therefore supplies the reproducible call graph; cflow and cscope establish
that C-family parsing cannot support a Python control-flow claim. The AST model
deliberately excludes nested callback bodies and dynamic Qiskit dispatch; the
retained aggregate-resource pass transitions supply runtime evidence for the
callback boundary. Each transition records a change in qubit count, recursive
depth, or recursive operation census. Named stage snapshots bind the synthesis
and routing boundaries without claiming a full structural digest of operation
order, arguments, parameters, control flow, or layout.

The parser controls run from the repository root:

```sh
FLOW_PROBE_DIRECTORY="$(mktemp -d)"
trap 'rm -r -- "$FLOW_PROBE_DIRECTORY"' EXIT
cflow --no-cpp --all gororoba_quantum/compile_evidence.py \
  gororoba_quantum/order_finding.py gororoba_quantum/modular_arithmetic.py \
  >"$FLOW_PROBE_DIRECTORY/cflow.out" 2>"$FLOW_PROBE_DIRECTORY/cflow.err"
cscope -bqk -f "$FLOW_PROBE_DIRECTORY/cscope.out" \
  gororoba_quantum/compile_evidence.py gororoba_quantum/order_finding.py \
  gororoba_quantum/modular_arithmetic.py
cscope -dL -3 append_controlled_modular_multiply \
  -f "$FLOW_PROBE_DIRECTORY/cscope.out"
```

## Leading-identity pruning

The host computes every repeated-square multiplier before it builds a circuit.
If the first `k` multipliers equal one, the first `k` semiclassical rounds
produce zero deterministically. Their feedback history is also all zero. The
circuit omits those rounds and leaves their classical bits at their initialized
zero values. The proof depends on the computed multiplier values rather than a
known order.

For `N = 15`, `a = 2`, and eight phase bits, the multiplier sequence is

```text
1, 1, 1, 1, 1, 1, 4, 2.
```

The circuit executes only the final two rounds. The paired identity null uses
the same two-round measurement, reset, and feedback schedule while replacing
the five Fredkin gates with identities. The control therefore isolates modular
arithmetic from the dynamic schedule.

Pinned FakeFez compilation uses Qiskit 2.5.2, qiskit-ibm-runtime 0.50.0,
optimization level 3, and seed 20261010:

| `N = 15` circuit | logical qubits | CZ | ISA depth | `if_else` | measurements | resets |
|---|---:|---:|---:|---:|---:|---:|
| Full eight-round source at `ed342fe` | 5 | 60 | 251 | 28 | 8 | 7 |
| Pruned primary | 5 | 60 | 183 | 1 | 2 | 1 |
| Schedule-matched identity null | 5 | 0 | 10 | 1 | 2 | 1 |

Pruning leaves CZ count unchanged because the five Fredkin gates remain. It
removes six measurements, six resets, 27 conditional branches, and the
associated unreported feed-forward latency. FakeFez supplies no classical
latency, so `live_run.py` marks a dynamic duration as
`lower_without_classical_latency`.

## Finite frontier

The coefficient and compile frontier uses `a = 2` and `m = 2*bit_length(N)`.

| Modulus and strategy | qubits | arithmetic coefficient count | FakeFez CZ | FakeFez depth | admission |
|---|---:|---:|---:|---:|---|
| `N = 15`, Mersenne rotation | 5 | 5 controlled swaps | 60 | 183 | executable conformance case |
| `N = 21`, Boolean target flips | 7 | 170 controlled cubes | 5,492 | 13,355 | default; noise admission pending |
| `N = 21`, one-clean cycle | 7 | 449 basis edges | 17,736 | 47,354 | retained synthesis control |
| `N = 21`, two-clean cycle control | 8 | 449 basis edges | 21,970 | 50,079 | ancilla-count causal control |
| `N = 21`, ANF | 11 | 866 ANF terms, 50 swaps | 48,895 | 116,968 | arity-distribution control |
| `N = 21`, scratch-free cycle | 6 | 449 basis edges | 63,818 | 210,473 | no-auxiliary falsifier |
| `N = 35`, ANF | 13 | 3,476 ANF terms, 72 swaps | unmeasured | unmeasured | conditional ceiling |
| `N = 35`, cycle | 7 | 1,037 basis edges | unmeasured | unmeasured | conditional ceiling |

The reference column uses seed 20261010. The Boolean target-flip circuit
reduces CZ by 69.0 percent and depth by 71.8 percent against the one-clean
cycle while preserving its seven-qubit, ten-round arithmetic contract.
`MODULAR_SYNTHESIS.md` derives the switch graph, exact XOR-cube optimizer,
finite Rocq certificate, eight-seed comparison, and smaller-precision
frontier. The compiler default selects the measured N=21 multipliers 2, 4,
and 16; wider generic arithmetic retains the cycle path.

The one-clean cycle circuit reduces CZ by
72.2 percent and depth by 77.5 percent against the scratch-free circuit. The
one-clean circuit reduces CZ by 63.7 percent and depth by 59.5 percent against
ANF while using seven rather than eleven logical qubits.

The ten-round schedule exposes each coefficient sum. Multiplier 2 contributes
53 basis edges once, multiplier 4 contributes 44 edges five times, and
multiplier 16 contributes 44 edges four times, so the cycle total is
`53 + 5*44 + 4*44 = 449`. The corresponding ANF totals are 92, 86, and 86,
which give `92 + 5*86 + 4*86 = 866` terms. The one-clean gate census then
follows directly as `6*449 = 2,694` RCCX gates plus 449 CCX gates.

The ANF coefficient histogram explains part of the crossover. The phase
control raises each monomial's control arity by one:

| ANF monomial degree | controlled-X controls | complete-schedule terms |
|---:|---:|---:|
| 1 | 2 | 140 |
| 2 | 3 | 212 |
| 3 | 4 | 320 |
| 4 | 5 | 194 |

ANF therefore places 672 of 866 terms, or 77.6 percent, below five controls.
The scratch-free cycle places all 449 edges at five controls. The five ANF
scratch qubits hold computed output data during the network; they do not remain
five continuously clean routing buffers. The corrected mechanism combines
control-arity distribution, synthesis-family selection, and topology routing.

The seed-20261010 pass trace separates the arithmetic coefficients from routing
amplification:

| Stage | scratch-free cycle | one-clean cycle |
|---|---:|---:|
| Source | 449 open-control MCX | 2,694 RCCX + 449 CCX |
| After high-level synthesis | 36,818 CX + 449 CRZ | unchanged explicit RCCX/CCX |
| Pre-routing tracked entanglers | 36,818 CX + 449 CRZ | 10,776 CZ |
| SabreLayout insertions | 13,202 swaps | 4,283 swaps |
| Post-routing basis translation | 77,322 CZ | 23,625 CZ |
| Final optimization | 63,818 CZ | 17,736 CZ |

The accounting subtracts the 36,818 HLS CX gates from the scratch-free final
CZ count and the 10,776 pre-routing CZ gates from the one-clean final count.
The final 46,082-CZ reduction then decomposes algebraically into a 26,042-gate
tracked synthesis reduction and a 20,040-gate residual. The residual includes
CRZ translation, routing, and final optimization, so it is not a pure SWAP
count. The independent swap reduction from 13,202 to 4,283 supplies the direct
routing evidence.

Eight fixed transpiler seeds, 20261010 through 20261017, preserve the CZ-count
ordering. Their bounded-sample means preserve the depth ordering shown below,
while one seed reverses the one-clean and two-clean depths:

| Candidate | CZ range | CZ mean | depth range | depth mean |
|---|---:|---:|---:|---:|
| one-clean cycle | 17,736-18,773 | 17,865.625 | 47,354-49,688 | 47,645.75 |
| two-clean cycle control | 20,966-22,115 | 21,622 | 49,284-51,170 | 50,250.5 |
| ANF | 48,895-58,358 | 52,010.25 | 116,968-134,193 | 122,437.25 |
| scratch-free cycle | 63,628-63,818 | 63,747 | 210,473-210,768 | 210,615.75 |

Seven one-clean seeds select the same initial layout, final layout, CZ count,
and depth. Seed 20261015 selects the sole alternate one-clean layout basin.
That seed gives the two-clean control depth 49,284 and the one-clean depth
49,688, so per-seed depth ordering reverses once while the one-clean depth mean
remains lower across the bounded seed set.
The two-clean and ANF candidates select eight distinct initial and final
layouts. The layout census provides a structural correlate for the one-clean
candidate's narrow compile distribution without claiming live-target stability.

One and two clean ancillas both reach 10,776 pre-routing CZ at the reference
seed. The two-clean circuit nevertheless needs 5,339 SabreLayout swaps and
finishes at 21,970 CZ, while the one-clean circuit needs 4,283 swaps and
finishes at 17,736 CZ. Ancilla count therefore changes physical embedding cost
non-monotonically even when abstract entangling-gate count matches. The compiler
must optimize synthesis family and routed interaction graph together.

`results/hw_estimate/n21_heavy_hex_mcx_workspace.json` retains the complete
coupling graph, versions, source hashes, layouts, aggregate-resource pass
transitions, stage snapshots, per-seed results, and summary statistics. The
one-clean result materially advances the generic compiler frontier but keeps
`N = 21` at compile-only status. Fresh noise simulation must establish a
positive decoder margin before any QPU proposal. The `N = 35` compile remains
deferred until `N = 21` crosses the decoder-margin admission gate; a larger
compile alone supplies little new information.

The ideal decoder and the uniform decoder null establish a second admission
surface:

| Case | ideal factor yield | uniform-null yield | ideal margin | shots for 99% ideal success |
|---|---:|---:|---:|---:|
| `N = 15`, `a = 2` | 0.500000 | 0.296875 | 0.203125 | 7 |
| `N = 21`, `a = 2` | 0.330943 | 0.144531 | 0.186411 | 12 |
| `N = 35`, `a = 2` | 0.330709 | 0.057617 | 0.273092 | 12 |

A raw factor count does not establish order finding because the exact decoder
accepts some uniformly random phase strings. `experiments.py` reports the
factor and order-recovery margins over both the schedule-matched identity null
and the exact uniform null.

## Runtime contract

`live_run.py` treats the hybrid circuit as dynamic when it contains control
flow, reset, or quantum work after any measurement. Static and dynamic circuits
enter separate client-side Sampler jobs. Runtime 0.50 rejects dynamical
decoupling on dynamic circuits, and its gate-twirling path rejects `if_else`, so
the dynamic job keeps both features disabled.

The live hybrid group requires five logical qubits, eight classical bits, two
dynamic circuits, and direct Target support for `if_else`, `measure`, and
`reset`. The runner derives these values from the primary and identity-null
circuits rather than from a backend-name table. A filtered copy of each fresh
Target removes excluded instruction placements before layout and routing; the
finished circuits then pass recursive support checks against the original
Target. A bounded-angle Target stops at routing admission because its parameter
bounds cannot be reproduced through Qiskit's public Target API; the rejection
does not suppress later viable systems. Pre-submission discovery reruns
deterministic selection across every fresh eligible system. Any change to the
approved backend, layout, replica placement, packed circuits, capabilities, or
used calibration values produces a revised submit-free record and QPY archive,
then stops for a new written case and explicit user approval. An unchanged
approved plan refreshes the selected system again immediately before the hybrid
batch and stops that batch when its status, admitted hardware, Target
properties, or timing constraints move.

Runtime 0.50 rounds automatic twirling upward when the requested shot count
cannot supply its target of 32 randomizations with at least 64 shots each.
Static twirled jobs therefore require at least 2,048 shots divisible by 32 and
set both twirling counts explicitly. The recorded shot count then equals the
executed product. The default 4,096-shot run uses 32 by 128 shots.

The integrated run record uses schema version 4, contract
`live-target-packed-replicas-v1`, and explicit states: `planned`,
`approval_required`, `submission_started`, `partially_submitted`, and
`submitted`. `approval_required` records the revised QPY digest and every
selection reason before the process exits with zero Runtime jobs. Each split
job refreshes hardware state and `usage()` before submission. The record
checkpoints unique recovery tags and an attempt marker before `Sampler.run()`,
then checkpoints every acquired job identifier before the next job. Collection
recovers a response-lost id only from one exact recovery-tag match and stops on
zero or multiple matches. Collection joins all classical registers in circuit
order and atomically replaces `collect.json`; each atomic replacement fsyncs
the file and directory. A declared source manifest makes the experiment digest
independent of Python import order.

The initial record stores `system_inventory`, eligible backend capability
snapshots, logical `circuit_requirements`, final packed
`execution_requirements`, and capability and routing decisions in
`selection_trace`. Submission adds one `revalidation` entry per fresh admission
pass. A changed pass writes `renewed_approval` and stops; an unchanged pass
materializes `planned_jobs` before the first job. Each backend-and-kind job
preserves every logical component of its fused groups, respects the
10-million-execution Sampler job bound, and records ordered member names, the
exact `isa.qpy` SHA-256, effective options, calibration stamps, and recovery
tags. Collection validates
the planned and accepted job ledgers as a one-to-one mapping for a complete
submission and as a subset for a partial submission. The same ledger names
every PUB and logical component without a recorded job id.

Each circuit runs as packed disjoint replicas (`packing.py`, and the
DESIGN_NOTES.md section on packed replicas): every replica of the primary and
of the identity null executes the same measurement, reset, and feedback
schedule on its own five qubits and its own `r<k>_phase` register, so one shot
returns one phase string per replica. Collection joins each replica's
register alone and decodes it alone.

`runtime_contracts.py` checks terminal versus mid-circuit measurement
classification, recursive physical operations, source-derived capability
admission, fixed-parameter and nested Target support, routing and replica
placement around excluded native CZ couplers, coherent Target/property
snapshots, complete packed-circuit fingerprints, isolated backend-probe
failures, bounded-angle backend isolation, changed-plan approval enforcement,
cross-system reselection, whole-group job-batch partitioning, every-batch change
detection, schema-4 JSON/QPY integrity, recovery-tag reconciliation,
planned-to-accepted job mapping, packed static and dynamic classification,
per-replica register order, rate keys, exact twirling shots, and source-digest
stability. A local client-side Sampler contract runs a packed three-replica
feed-forward circuit and recovers each replica's outcome from its own registers.

## Retained schema-2 single-layout dry run

`results/live/2026-10-10T200646.447516Z/` records the historical submit-free
planning path from source commit `2cc7379`. The process reads the
`ibm_kingston` calibration stamped `2026-10-10T12:54:29-07:00`, selects
transpiler seed `20261014` and initial layout `[93, 95, 92, 94, 79]`, compiles
the primary and schedule-matched identity null, and simulates both circuits
locally with the noise model derived from the same calibration.

| Hybrid-Shor dry-run quantity | Primary | Identity null |
|---|---:|---:|
| CZ gates | 58 | 0 |
| ISA depth | 184 | 10 |
| Noise-model factor yield | 0.493652 | 0.001465 |
| Noise-model order-recovery yield | 0.493652 | 0.001465 |

The exact uniform-null factor yield is `0.296875`, so the primary noise-model
factor yield has margin `0.196777` over the uniform null and `0.492188` over
the identity null. Its total-variation distance from the ideal distribution is
`0.023438`. The record stays in lifecycle state `planned`, carries no
`submission` object, and therefore records zero QPU jobs. The paired `isa.qpy`
archive contains the compiled circuits named by every JSON member.
The record predates schema 3, so it does not establish system inventory,
capability admission, filtered-Target routing, or cross-system revalidation.

## Pre-integration capability-admission record

`results/live/2026-10-10T220438.712726Z/` supplies the divergent pre-integration
schema-3 capability record from source commit `0205a61`. The record reports
`code_commit.sources_modified=false` for the `gororoba_quantum/` source scope,
lifecycle state `planned`, and no
`submission` object. Fez and Kingston pass live eligibility; Marrakesh reports
maintenance and remains in `system_inventory` as ineligible. The capability
snapshot records 156 qubits, dynamic-circuit support, and native `cz`,
`if_else`, `measure`, and `reset` on each system. The derived hybrid requirement
records five qubits, eight classical bits, two dynamic circuits, and direct
support for `if_else`, `measure`, and `reset`.

Kingston calibration `2026-10-10T13:54:45-07:00` wins with seed `20261010`
and layout `[79, 94, 74, 93, 73]`. The primary uses 60 CZ gates at depth 183;
the identity null uses zero CZ gates at depth 10. Their local noise-model factor
yields are `0.491943` and `0.001465`, with primary margin `0.195068` over the
uniform null and TVD `0.019775` from the ideal distribution. The paired QPY
archive contains all 31 circuits named by the seven group records. Those 31
circuits omit the seven `_isolated` crosstalk references in PR #11's 38-circuit
packed archive. The record
establishes discovery, capability admission, degraded-hardware routing, and
local simulation while recording zero QPU jobs. It does not establish replica
placement, variance decomposition, crosstalk measurement, statistical
admission, submission revalidation, or execution-time behavior.

## Replicated admission

`results/live/2026-10-10T222132.627032Z/` is the packed-replica schema-3 record
from code `02a5b4b`. The record replicates the same `ibm_kingston` compile on
seven disjoint five-qubit placements with
layout scores from 0.691 to 0.569, above the group's 0.8 floor of the best
(`Group.replica_floor`; the other groups keep the default 0.9, and an explicit
`--replica-floor` governs every group). Each
shot scores whether its phase string decodes to a verified factor, so the
variance decomposition and the intervals act on factor yield itself.

| Replicated noise-model quantity | Mean | 95% interval over 7 replicas |
|---|---:|---|
| Primary factor yield | 0.4919 | [0.4830, 0.5008] |
| Identity-null factor yield | 0.0078 | [0.0022, 0.0134] |
| Exact uniform-null factor yield | 0.2969 | exact |

The group's admission rule (`experiments.py`, roadmap item 5) admits a
yield when the primary lower bound exceeds the exact uniform-null yield and
the identity-null upper bound stays below that lower bound; the noise model
admits both factor and order-recovery yield. Each interval is the union of a
Student t interval over the replicas, which carries layout and shot variance,
and a Wilson interval over the pooled shots, which keeps shot uncertainty when
the replicas agree exactly, as an identity null reading zero everywhere would.
Seven replicas put the t multiplier at 2.45 against 4.30 at three, the
admission rule's main lever once hardware layout variance is real. The
primary and the identity null run as separate PUBs, so collect withholds the
verdict unless both ran under one calibration with no update inside their
shots. The noise model predicts layout variance in factor yield of 3.1e-5,
within shot noise (chi-squared p = 0.17); a measured excess is hardware
structure the model omits.

## Combined schema-4 qualification

`results/live/2026-10-10T232219.919322Z/` runs the post-review integrated
contract from source `584a78d`. The submit-free run uses `--max-pending 250`
after the default 25-job gate rejects both active systems. Kingston calibration
`2026-10-10T15:34:50-07:00` wins with seed `20261010`, layout
`[79, 94, 74, 93, 73]`, 60 primary CZ gates, and zero identity-null CZ gates.
The group's 0.8 floor places nine replicas and expands each packed dynamic
circuit to 72 classical bits.

| Schema-4 hybrid quantity | Mean | 95% interval over 9 replicas |
|---|---:|---|
| Primary factor yield | 0.4971 | [0.4901, 0.5040] |
| Identity-null factor yield | 0.0040 | [0.0013, 0.0068] |
| Exact uniform-null factor yield | 0.2969 | exact |

The factor and order-recovery admission rules both pass in the local noise
model. The complete QPY archive contains 38 uniquely named circuits, including
the hybrid isolated reference, and matches the schema-4 member and execution
requirements exactly. The record stays `planned` with `submission` absent, so
it records zero QPU jobs. The 250-job dry-run bound leaves default-policy
submission readiness unestablished. Its record SHA-256 is
`0c5b57a2db2d4e246908c5a05ccf1eadc0aa87629e2ac3950586f38ef7c55744`, and
its QPY SHA-256 is
`34111afea1e4940f69651ce3575c7946d0be2a6402c8c1e3aa6c66ba344cbc60`.

## Deficiencies and falsifiers

- **Truth-table scaling.** ANF extraction enumerates `2^n` inputs and the
  current guard bounds the method to eight data qubits. This method serves as a
  bounded exact compiler and oracle. It does not provide scalable RSA
  arithmetic.
- **Routed generic cost.** The one-clean `N = 21` circuit lowers depth from
  210,473 to 47,354 at the reference seed, but compiler depth does not establish
  useful noisy execution. A proposed synthesis earns admission only when fresh
  Target compilation and noise simulation produce a positive factor-yield
  margin over the uniform null.
- **Topology attribution.** The pass trace proves a large routed penalty on
  FakeFez and records the exact degree-three graph. The pass trace does not yet
  isolate topology from all other target-specific translation behavior. An
  all-to-all coupling control with the same basis and synthesis inputs supplies
  the missing causal comparison.
- **Concurrent feed-forward.** The dynamic job runs every packed replica of
  folded QPE and hybrid Shor in one PUB and their replica-0 copies together in
  the shared reference PUB, so neither PUB runs a single feed-forward stream;
  each PUB manifest records its `parallel_stream_count` (replica streams that
  carry feed-forward), `sequential_stage_count` (the deepest chain of
  feed-forward decisions along one stream, 1 for both groups), and
  `feed_forward_operation_count` (every control-flow operation, nested blocks
  included). Two measurements separate the candidate mechanisms:
  - *Schedule.* Every job requests the backend scheduler's per-PUB
    `circuit_duration`, which includes the classical latency the Target omits,
    and `packing_schedule` compares the packed PUB with the reference PUB of
    the same job. Serialized branches lengthen the packed schedule with the
    stream count, and so do serialized measurement, reset, or pulse-channel
    resources, since the packed PUB adds every replica's whole circuit; the
    comparison is exact and needs no shot statistics, and it measures a
    global packing scheduling cost rather than feed-forward alone.
  - *Fidelity.* `global_packing_crosstalk` compares packed replica 0's factor
    yield with the reference copy on the same qubits. The record keeps the z
    statistic (z below -3 is the degradation diagnostic; |z| at most 3 reads
    "the run detected no difference at this resolution"; zero per-shot
    variance in both arms leaves z undefined and says so) and adds the
    difference with its 95 percent interval and a two-one-sided equivalence
    test. For the Bernoulli factor indicator, `variance.difference_interval`
    uses Newcombe's hybrid score interval from two continuity-corrected
    Wilson intervals. For any other score with weights in [0, 1], the
    function uses the Hoeffding bound for independent shots and arms; the
    Bhatia-Davis variance bound alone establishes no score-interval coverage
    for weighted means. At n shots per arm and confidence 1 - alpha, the
    Hoeffding radius is `sqrt(log(2 / alpha) / n)`, with endpoints clipped
    to [-1, 1]. A 90 percent interval inside
    the preregistered margin of 0.03 reads `equivalent_within_0.03`, a 95
    percent interval below zero reads `packed_degradation_detected`, one
    above zero reads `packed_improvement_detected`, and anything else reads
    `difference_not_resolved`; the three flags are reported beside the
    verdict, so a loss the 95 percent interval resolves inside the margin
    stays visible. Every comparison also reports the Hoeffding 90 percent
    interval and its own within-margin flag, so a Bernoulli verdict can be
    compared with that wider distribution-free view. Exact enumeration of
    equal Bernoulli arms over true rates 0.005 to 0.995 puts Newcombe's
    95 percent false-detection probability below nominal at the enumerated
    sizes (0.0416 at 64 shots per arm, 0.0482 at 1024, 0.0488 at 4096), where
    the uncorrected interval exceeds nominal (0.0555 down to 0.0506). The
    finite enumeration establishes neither all-rate coverage nor a result
    for weighted scores. Verdicts are withheld below 64 shots per arm
    (`insufficient_shots`). One matched Bernoulli pair at 4096 shots and a
    yield near 0.5 gives the difference a standard deviation of 0.011, so
    Newcombe's 90 percent interval is about 0.0367 wide and a difference
    within about 0.012 of zero can establish equivalence. The Hoeffding
    interval at the same shot count has radius about 0.0270 and requires a
    difference within about 0.0030 of zero to fit the 0.03 margin. The
    historical pilot's factor-yield verdict belongs to its retained
    preregistered Bernoulli analysis; the later adjudication adds the
    Hoeffding sensitivity view without replacing that analysis.

  Collection joins the two into `packing_interpretation`. The schedule side
  compares scheduler residuals, each PUB's scheduled duration above its own
  execution-time Target bound, because the packed and reference PUBs hold
  different gate content and their raw durations differ by gate time alone.
  A larger packed residual is an unattributed global packing scheduling
  cost: feed-forward, measurement, reset, pulse-channel, and controller
  resources all scale with replica count, and only the matched
  dynamic/control ladder separates them; equal residuals with a detected
  yield loss are evidence consistent with quantum, measurement, or readout
  crosstalk; equal residuals with equivalent yields resolve no packing cost;
  a static group's residual difference excludes feed-forward. The scope is
  global only when the packed PUB carries both dynamic groups (a record whose
  groups landed on different backends compares each group with its own
  reference), and the reading identifies neither one group nor one physical
  mechanism.
  The identity null shares its PUB with folded QPE `s0` and the primary with
  `s1`; the two folded instances carry identical gate counts and
  measurement, reset, and branch schedules, so the null and the primary face
  matched concurrent workloads.
- **Dynamic duration.** Backend Targets omit classical feed-forward latency.
  A duration computed from the Target is a lower bound; the scheduler's
  `circuit_duration` from the first dynamic job replaces it. Each PUB's timing
  record carries `scheduler_residual_dt`, the `scheduled_circuit_duration_dt`
  minus the Target-derived `target_gate_lower_bound_dt`. The residual is a
  scheduler residual: feed-forward, alignment, measurement, reset, and
  controller time all contribute on a dynamic PUB. The bound comes from the
  Target in force when the PUB's shots began (the plan-time bound is kept
  beside it), so a calibration update between planning and execution does
  not enter the residual. Static and dynamic circuits run in separate jobs
  and no static PUB is a schedule-matched copy of a dynamic one, so the first
  dynamic job reports its residuals without attribution; the matched
  dynamic/control ladder below is the experiment that attributes them. A
  residual below zero is retained with `timing_status`
  `residual_below_target_bound` and no interpretation. Chunk
  wall-clock windows do not support this subtraction: a chunk spans every
  shot of one or more PUBs plus repetition delay and service overhead, so the
  windows serve calibration lookup and drift detection only.
- **Noise-model authority.** FakeFez and Aer validate construction and local
  option paths. They do not predict a drifting device. Only a submitted and
  collected run supplies hardware evidence.
- **Small-case interpretation.** `N = 15` remains a structured Mersenne case
  with classically known short arithmetic. A successful run proves the pipeline
  and hardware control path rather than computational advantage.
- **Compiler selection.** `auto` follows a bounded eight-seed `N = 21` race on
  the pinned FakeFez target. A new target, Qiskit release, or synthesis
  invalidates the selection when a repeated seeded compile reverses CZ,
  duration, or simulated factor-yield ordering.

## Roadmap

1. **All-to-all topology control.** Recompile the four `N = 21` candidates with
   the same synthesis methods, seeds, basis operations, and optimization level
   on a complete coupling graph. Compare pre-routing operations, routed
   operations, and final depth. The control attributes the crossover to
   heavy-hex only when the no-auxiliary disadvantage contracts materially while
   the source circuits remain identical.
2. **Three-clean M15 challenger.** Add an explicit
   `synth_mcx_n_clean_m15` cycle candidate with three clean ancillas. Verify
   every basis state and restored ancilla, then run the same seed matrix. The
   challenger survives only when its lower synthesis depth offsets its wider
   physical embedding; otherwise the result strengthens the non-monotonic
   ancilla finding.
3. **Target-weighted Gray paths.** Replace Hamming-only pivots and bit order
   with a deterministic cost derived from the admitted coupling subgraph and
   the selected MCX interaction graph. Keep the current pivot rule as a
   baseline. Accept the new path only when exact permutation checks pass and
   repeated routed compiles lower both CZ and depth.
4. **Per-multiplier mixed synthesis.** Compile multipliers 2, 4, and 16 as
   independent ANF, scratch-free, one-clean, and later three-clean candidates.
   Compose the lowest-cost compatible choices while sharing a bounded workspace
   register. Whole-circuit compilation must beat the one-clean baseline across
   the seed matrix; isolated multiplier wins alone do not qualify. The current
   four-way capture supplies the whole-circuit baseline and materially advances
   the previously uninstrumented per-multiplier item.
5. **Affine-skeleton extraction.** Measured and rejected
   (`MODULAR_SYNTHESIS.md`, "Affine-residual challenger";
   `results/hw_estimate/n21_affine_residual_challenger.json`). The valid form
   factors f = A r with A the full-rank linear part and r = A^-1 f a
   permutation synthesized by target flips, A promoted to Toffolis under the
   phase control; eight of the eleven units modulo 21 have a rank-4 linear
   part, including 11, the inverse of 2, so the method does not apply to them.
   For 2, 4, and 16 the whole ten-round circuit routes worse than the
   target-flip baseline on every seed (median routed CZ 6,130.5 against
   5,422), so the default stays `target_flip_1_clean` and the challenger
   compiles only when named.
6. **Fresh decoder-margin admission.** Compile the one-clean primary and its
   schedule-matched identity null against a fresh live Target, then run the
   calibration-derived noise model without submission. Advance `N = 21` only
   when replicated factor and order-recovery lower bounds exceed the exact
   uniform-null yield and the identity-null upper bounds remain below the
   primary lower bounds.
7. **Structured modular arithmetic.** Introduce reversible add, compare, and
   conditional-reduction blocks beyond the eight-bit truth-table guard. Cross-
   check every new block against the exhaustive permutation oracle at widths
   where both implementations fit, and retain explicit arithmetic and workspace
   resource formulas.
8. **`N = 35` admission.** Compile and simulate `N = 35` only after `N = 21`
   crosses the fresh decoder-margin gate. Preserve `N = 35` as a coefficient
   and scaling falsifier until then; a deeper compile without `N = 21` admission
   adds cost without resolving the active uncertainty.
9. **Dynamic latency evidence.** Measured from the backend scheduler tables
   the job returns with `scheduler_timing` on: the classical round trip is a
   broadcast of 533 dt on a two-stream PUB and 577 dt on a nine-stream PUB
   plus a 7 dt receive (2.16 to 2.34 us at 4 ns per dt), the control qubit's
   segment from first capture to the end of its reset spans 1,299 to 1,463
   dt, and the work qubits idle 1,380 to 2,380 dt across it
   (`adjudicate.py`, `feed_forward_segment`). The stream dependence of the
   broadcast, 44 dt for seven more streams, is the measured parallel
   feed-forward cost at the scheduler. The result is scheduler-defined
   feedback timing; an independent physical timing observable would be
   needed to claim more. The open question is the fidelity mechanism, not
   the latency (HARDWARE_PLAN.md, "Risks", the four-rung ladder). The
   submission approval gate and rolling QPU budget continue to govern every
   measurement.
10. **Signed-XOR coefficient certificates.** Solve the exact minimum-one-norm
    group-word LCU at `n = 3` through `n = 5` and retain primal reconstruction
    plus a matching linear-program dual bound. Extend the experiment only after
    a zero duality gap separates the unit-output-scale coefficient one-norm from
    the displacement floor. Keep the signed-XOR experiment separate from the
    direct arithmetic compiler because base-two rotation proves that effective
    normalization and direct gate count measure different resources.

## Replay commands

All commands run without QPU submission:

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
"$PYTHON" gororoba_quantum/factoring.py
"$PYTHON" gororoba_quantum/modular_arithmetic.py
"$PYTHON" gororoba_quantum/order_finding.py
"$PYTHON" gororoba_quantum/runtime_contracts.py
"$PYTHON" gororoba_quantum/hybrid_shor.py plan 15
"$PYTHON" gororoba_quantum/hybrid_shor.py simulate 15 --shots 256 --seed 7
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" scripts/python_call_graph.py
"$PYTHON" gororoba_quantum/compile_evidence.py \
  --out results/hw_estimate/n21_heavy_hex_mcx_workspace.json
```

`results/hw_estimate/hybrid_shor_fake_fez.json` preserves the historical
single-seed comparison. `n21_heavy_hex_mcx_workspace.json` records the
instrumented multi-seed comparison without overwriting the historical provenance.
`gororoba_quantum/live_run.py --out results/live` performs the fresh
calibration, compile, and local noise-simulation layer when invoked from the
repository root. The command omits `--submit` and therefore sends zero quantum
jobs.
