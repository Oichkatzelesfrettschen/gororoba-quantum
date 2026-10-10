# Hybrid Shor architecture for IBM Heron

This repository now carries a bounded, end-to-end Shor decomposition. The
classical host performs deterministic preprocessing, coefficient extraction,
resource admission, exact order validation, and factor extraction. An IBM
Heron backend receives only the semiclassical order-finding circuit selected
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
   modular permutation, each ANF reconstruction, and each synthesized
   controlled multiplier. Aer verifies the phase support and factor decoder.
2. **Compiler evidence.** FakeFez compilation measures width, CZ count, depth,
   and control-flow structure against the pinned Qiskit stack. The fake backend
   supplies a static target snapshot rather than a prediction of live noise.
3. **Live dry-run evidence.** `live_run.py` reads fresh backend Targets and
   properties, excludes degraded qubits and edges, selects layouts, and runs
   local noise simulation. The dry run spends zero QPU time.
4. **QPU evidence.** A submitted and collected run measures the circuit on a
   calibrated device and replays its execution-time calibration. This level
   remains absent until the user approves a written submission case.

The repository has submitted zero hybrid-Shor QPU jobs.

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

## Three multiplier syntheses

### Mersenne rotation

For `N = 2^n - 1`, multiplication by a power of two rotates the `n` data bits.
The all-ones invalid state also remains fixed under rotation, so the same wire
permutation implements the required full-register extension. A controlled
rotation becomes a short Fredkin network. `N = 15`, `a = 2` uses three
controlled swaps for multiplication by two and two for multiplication by four.

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

The cycle representation reduces logical width and often reduces logical gate
count. Heron routing decides the useful circuit. The `N = 21` compile shows why
a logical count cannot select the winner: 449 cycle edges route to more CZ gates
and greater depth than 866 ANF terms. `auto` therefore selects ANF on the
bounded generic frontier while the CLI keeps both candidates explicit.

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
| `N = 21`, ANF | 11 | 866 ANF terms, 50 swaps | 48,895 | 116,968 | compile-only rejection surface |
| `N = 21`, cycle | 6 | 449 basis edges | 63,818 | 210,473 | refutes gate-count-only selection |
| `N = 35`, ANF | 13 | 3,476 ANF terms, 72 swaps | unmeasured | unmeasured | conditional ceiling |
| `N = 35`, cycle | 7 | 1,037 basis edges | unmeasured | unmeasured | conditional ceiling |

The `N = 21` result blocks QPU admission under the current synthesis. The
`N = 35` compile remains deferred until a structural change lowers the `N = 21`
cost; a larger compile alone supplies little new information.

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

Runtime 0.50 rounds automatic twirling upward when the requested shot count
cannot supply its target of 32 randomizations with at least 64 shots each.
Static twirled jobs therefore require at least 2,048 shots divisible by 32 and
set both twirling counts explicitly. The recorded shot count then equals the
executed product. The default 4,096-shot run uses 32 by 128 shots.

The run record uses schema version 3 and explicit states: `planned`,
`submission_started`, `partially_submitted`, and `submitted`. Each split job
refreshes `usage()` before submission. Every acquired job identifier reaches an
atomic checkpoint before the next job. Collection joins all classical
registers in circuit order and atomically replaces `collect.json`. A declared
source manifest makes the experiment digest independent of Python import order.

Each circuit runs as packed disjoint replicas (`packing.py`, and the
DESIGN_NOTES.md section on packed replicas): every replica of the primary and
of the identity null executes the same measurement, reset, and feedback
schedule on its own five qubits and its own `r<k>_phase` register, so one shot
returns one phase string per replica. Collection joins each replica's
register alone and decodes it alone.

`runtime_contracts.py` checks terminal versus mid-circuit measurement
classification, recursively discovers physical operations inside control-flow
blocks, verifies global bit order for multiple classical registers, verifies
the pruned primary and null operation counts, enforces exact twirling shots,
runs a packed three-replica feed-forward circuit through the local
client-side Sampler and recovers each replica's own outcome from its
registers, and proves digest stability.

## Retained live-calibration dry run

`results/live/2026-10-10T200646.447516Z/` records the complete submit-free
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

## Replicated admission

`results/live/2026-10-10T214318.070235Z/` (code `b447626`) replicates the
same `ibm_kingston` compile on three disjoint five-qubit placements with
layout scores 0.691, 0.628, and 0.627, above the 0.9 floor of the best. Each
shot scores whether its phase string decodes to a verified factor, so the
variance decomposition and the intervals act on factor yield itself.

| Replicated noise-model quantity | Mean | 95% interval over 3 replicas |
|---|---:|---|
| Primary factor yield | 0.4975 | [0.4850, 0.5099] |
| Identity-null factor yield | 0.0050 | [-0.0094, 0.0195] |
| Exact uniform-null factor yield | 0.2969 | exact |

The group's admission rule (`experiments.py`, roadmap item 5) admits a
yield when the primary lower bound exceeds the exact uniform-null yield and
the identity-null upper bound stays below that lower bound; the noise model
admits both factor and order-recovery yield. Each interval is the union of a
Student t interval over the replicas, which carries layout and shot variance,
and a Wilson interval over the pooled shots, which keeps shot uncertainty when
the replicas agree exactly, as an identity null reading zero everywhere would.
With three replicas the t multiplier is 4.30, so a replica count is the
admission rule's main lever once hardware layout variance is real. The noise model predicts no layout variance in factor yield beyond shot
noise (chi-squared p = 0.66); a measured excess is hardware structure the
model omits.

## Deficiencies and falsifiers

- **Truth-table scaling.** ANF extraction enumerates `2^n` inputs and the
  current guard bounds the method to eight data qubits. This method serves as a
  bounded exact compiler and oracle. It does not provide scalable RSA
  arithmetic.
- **Routed generic cost.** The `N = 21` circuits exceed the useful noisy depth
  by orders of magnitude. A proposed synthesis earns admission only when fresh
  Target compilation and noise simulation produce a positive factor-yield
  margin over the uniform null.
- **Concurrent feed-forward.** Packed replicas run three or more independent
  `if_else` branches in one shot. Aer and the local Sampler execute them
  concurrently; the hardware's handling of simultaneous feed-forward,
  including whether it serializes their latency, is unmeasured until a
  packed dynamic job returns. The isolated reference on replica 0's qubits
  measures any cost packing adds, and a factor yield on packed replica 0 more
  than three standard deviations below the isolated copy falsifies parallel
  feed-forward at no cost.
- **Dynamic duration.** Backend Targets omit classical feed-forward latency.
  Any duration claim for the hybrid circuit remains a lower bound until a QPU
  execution span measures the complete schedule.
- **Noise-model authority.** FakeFez and Aer validate construction and local
  option paths. They do not predict a drifting device. Only a submitted and
  collected run supplies hardware evidence.
- **Small-case interpretation.** `N = 15` remains a structured Mersenne case
  with classically known short arithmetic. A successful run proves the pipeline
  and hardware control path rather than computational advantage.
- **Compiler selection.** `auto` follows one bounded `N = 21` race. A new
  target, Qiskit release, or synthesis invalidates that decision when a repeated
  seeded compile reverses CZ, duration, or simulated factor-yield ordering.

## Roadmap

1. **Target-aware mixed synthesis.** Compile ANF and cycle candidates for each
   unique multiplier, then permit a per-multiplier mixture. Select by calibrated
   duration and simulated decoder margin. Reject the idea when the mixed circuit
   fails to beat whole-circuit ANF across repeated transpiler seeds.
2. **Affine-skeleton extraction.** Separate constant and degree-one ANF terms
   into an optimized X/CNOT network and synthesize only the nonlinear residual.
   The Cayley-Dickson work motivates this split because its useful sign circuits
   expose low-degree Boolean structure directly. Retain the method only when
   exact permutation checks pass and `N = 21` routed cost falls.
3. **Target-weighted Gray paths.** Replace Hamming-only cycle pivots and paths
   with costs derived from the selected coupling subgraph and native controlled
   gate decomposition. Retain Hamming minimization as the deterministic
   baseline and compare the complete routed circuit.
4. **Structured modular arithmetic.** Introduce reversible add, compare, and
   conditional-reduction blocks for widths beyond the truth-table guard. Cross-
   check every new block against the exhaustive permutation oracle at widths
   where both implementations fit.
5. **Statistical admission.** Implemented as the `hybrid_shor_mod15` admission
   rule over replicated factor and order-recovery yields: the primary lower
   bound must exceed the exact uniform-null yield and the identity-null upper
   bound must stay below the primary lower bound. A QPU result is interpreted
   only through this verdict.
6. **Dynamic latency evidence.** Record execution spans and compare them with
   scheduled gate duration. Attribute the residual to service and classical
   control only after repeated jobs show a stable separation.
7. **`N = 21` rescope gate.** Recompile the complete circuit after each
   arithmetic change. Advance `N = 21` to a proposed QPU case only when fresh
   local noise simulation preserves a positive decoder margin and the written
   QPU-time case fits the rolling budget.
8. **`N = 35` admission.** Compile and simulate `N = 35` only after `N = 21`
   crosses the preceding gate. Preserve `N = 35` as a coefficient-level
   falsifier until then.

## Replay commands

All commands run without QPU submission:

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
cd gororoba_quantum
"$PYTHON" factoring.py
"$PYTHON" modular_arithmetic.py
"$PYTHON" order_finding.py
"$PYTHON" runtime_contracts.py
"$PYTHON" hybrid_shor.py plan 15
"$PYTHON" hybrid_shor.py simulate 15 --shots 256 --seed 7
```

`results/hw_estimate/hybrid_shor_fake_fez.json` records the pinned compiler
measurements above. `live_run.py --out ../results/live` performs the fresh
calibration, compile, and local noise-simulation layer. The command omits
`--submit` and therefore sends zero quantum jobs.
