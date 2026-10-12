# gororoba-quantum

Quantum circuits whose structure comes from the open_gororoba Cayley-Dickson
algebra kernel, targeting IBM Quantum Heron backends. Left multiplication by a
basis unit is a signed permutation of the 2^k basis states, so it is unitary on
k qubits; two algebraic defects the kernel measures classically become hardware
observables.

The [source index](docs/INDEX.md) separates hosted papers from ignored local copies.
The [source library](docs/README.md) retains licensed primary PDFs, per-paper notes,
download identities, and the [Koebisu rank-stratum research plan](docs/notes/koebisu_rank_stratum_research.md). The
[coordinated research roadmap](docs/RESEARCH_ROADMAP.md) records the cumulative
objectives, evidence boundaries, ownership, and ordered delivery gates.

The [current campaign preparation](results/ripple/CAMPAIGN_PREPARATION.md)
qualifies correction, ripple and rank-sector planning against the same audited
source closure:
106.290103040 nominal QPU seconds, 118.445463040 seconds under the declared
stress scenarios, and five job ceilings totaling 170 seconds within the user's
180-second cap. The exact written cases cover
[correction](results/live/2026-10-12T170742.727534Z/UNAPPROVED_CASE.md),
[ripple](results/live/2026-10-12T163354.310138Z/UNAPPROVED_CASE.md) and
[rank sectors](results/live/2026-10-12T163354.210407Z/UNAPPROVED_CASE.md).
Planning preserves every original row, control and within-PUB shot vector.

The [integrated campaign directive](gororoba_quantum/RIPPLE_CAMPAIGN.md)
connects the mathematical, scientific, visual and execution requests with their
evidence gates and owners. Correction runs first; ripple and rank retain
independent execution admission under the
[practical accuracy protocol](results/ripple/STATIC_PACKING_ACCURACY.md).
The user conditionally authorizes execution
after clean current-head Copilot review, passing checks, merged changes and
fresh source/calibration/QPY/dependency, quota and approval bindings. The
prepared correction pilot compared all three available systems and selected
Fez for four 8,192-shot PUBs in one dynamic job. Returned schedules still gate
its statistical decision. The [protocol](gororoba_quantum/MODEL_DISCRIMINATION.md)
separates modeled sensitivity from measured improvement.

The [historical atlas preparations](results/ripple/PREPARATION.md) retain the
197.022-second estimate and proposed 240-second combined ceiling. The
[correction preparation history](results/ripple/CORRECTION_PREPARATION.md)
preserves earlier renewals and the superseded backend-eligibility rejection.
The [completed folded-job audit](results/ripple/folded-job-review.md) provides
measured contrasts, model discrepancies and timing evidence. Historical
preparations and completed measurements remain distinct from the fresh cases.

## Contents

- `gororoba_quantum/cd_core.py` -- Cayley-Dickson sign table ported from
  cd_kernel, plus associator and zero-divisor enumeration.
- `gororoba_quantum/verify.py` -- fail-closed checks: the sign tensor against the
  kernel's hash-pinned multiplication tables, the zero-divisor corpus against
  the kernel CSV, norm multiplicativity, the exact C881 sign-row bridge, and
  phase-degree and Walsh-spectrum rules along the ladder.
- `gororoba_quantum/boolean_anf.py` and `modular_arithmetic.py` -- exact Boolean
  coefficient extraction, bounded Reed-Muller interpolation, quadratic polar
  rank, and controlled modular-permutation synthesis through signed Mersenne
  rotations, ANF networks, scratch-free cycle transpositions, or explicit
  one-clean-ancilla cycle transpositions, or bounded minimum-cost Boolean
  target flips. `target_flip.py` factors whole-register permutations before
  expanding their predicates; `proofs/TargetFlipN21.v` certifies the three
  scheduled N=21 multiplier witnesses.
- `gororoba_quantum/factoring.py`, `order_finding.py`, and `hybrid_shor.py` --
  classical admission and decoding around faithful `|1>` semiclassical order
  finding, plus a credential-free plan, simulation, and decode CLI.
- `gororoba_quantum/claim_boundaries.py` and `CLAIM_BOUNDARIES.md` -- executable
  finite witnesses and a sourced audit separating Walsh sampling, LCU arithmetic,
  and annihilator fibers from claims about hidden polynomials, exceptional
  Jordan mechanics, and global zero-divisor topology.
- `gororoba_quantum/sedenion_bundle.py` -- real normalized zero-product pairs,
  seven quaternion charts, SU(2) transition maps and Cayley-frame automorphisms.
- `gororoba_quantum/ripple_dynamics.py` -- exact finite associator recurrences,
  all seven signed box-kite graphs, and 672 local phase-circuit checks.
  [RIPPLE_DYNAMICS.md](gororoba_quantum/RIPPLE_DYNAMICS.md) derives the
  protocol and a single-job hardware proposal; [results/ripple](results/ripple/README.md)
  retains replayable evidence and a portable interactive visualization.
- `gororoba_quantum/annihilator_strata.py` -- exact signed two-term kernel census
  and published maximal-annihilator lift witnesses through dimension 256.
  `docs/notes/cayley_dickson_annihilator_sources.md` records primary
  theorems and the source-pinned Rust and Rocq work reused by the audit.
- `gororoba_quantum/rank_polynomials.py` and `rank_charts.py` -- exact
  spectral rank predicates and fixed-minor kernel charts for general coefficients.
- `gororoba_quantum/skew_schur_charts.py` -- exact dimension-32 reduced rank
  certificates, kernel lifts, sphere metrics, and polynomial pivot domains
  across all 30 doubly-pure coefficient directions.
- `gororoba_quantum/principal_skew_atlas.py` -- an explicit finite cover of
  every nonzero doubly-pure input, a conditioned initial pivot, exact principal
  refinement, and kernel-restricted overlap maps across changing ranks.
- `gororoba_quantum/schur_acceleration.py` -- exact first-order admission,
  complete affine acceleration certificates, and separating witnesses for
  second-order rank obstructions at dimension-32 centers.
- `gororoba_quantum/four_support_rank.py` and `four_support_geometry.py` --
  exact real ranks, connected smooth strata, complete kernel frames, closure
  maps, and a partner-incidence model on support `{1,10,18,25}`.
- `gororoba_quantum/four_support_doubling.py` -- structural ordinary-doubling
  frames and inverse maps for the same support at every higher stage.
- `gororoba_quantum/four_support_homology.py` -- an explicit finite CW model,
  integral cancellation certificates, and the restricted cohomology ring.
- `gororoba_quantum/rank_attachments.py`, `rank_path_topology.py`, and
  `integral_homology.py` -- exact polynomial attachment certificates, a proved
  restricted pair-space model, and integral homology with torsion certificates.
  [RANK_STRATUM_TOPOLOGY.md](gororoba_quantum/RANK_STRATUM_TOPOLOGY.md) gives
  the derivations, all-dimensional restricted construction, and global proof obligations.
- `gororoba_quantum/compile_evidence.py` -- reproducible multi-seed FakeFez
  compilation with pass-level synthesis, routing, layout, and topology capture.
- `gororoba_quantum/FACTORING_NOTES.md` -- what Cayley-Dickson structure can and
  cannot contribute to Shor's algorithm, against the RSA-2048 resource floor.
- `gororoba_quantum/HYBRID_SHOR.md` -- host/QPU boundary, coefficient
  derivations, bounded hardware frontier, evidence levels, falsifiers, and the
  roadmap beyond `N = 15`.
- `gororoba_quantum/MODULAR_SYNTHESIS.md` -- the N=21 impossibility
  falsification, exact target-flip method, Rocq boundaries, and precision frontier.
- `gororoba_quantum/HARDWARE_PLAN.md` -- the joint submission plan for every
  experiment group: claims and falsifiers, calibration-to-circuit pipeline,
  deciding statistics, QPU cost, and the path to the first submission.
- `gororoba_quantum/packing.py` and `variance.py` -- disjoint replica placement
  and packing of compiled circuits, and the shot, layout, and instance
  variance decomposition with replicate intervals.
- `gororoba_quantum/select_lcu.py` -- ancilla-selected left multiplication with
  equivalent DiagonalGate and direct Reed-Muller sign strategies, plus validated
  sparse pair-state preparation.
- `gororoba_quantum/predict.py` -- every algebraic prediction, from cd_sign and
  cd_multiply; no circuit builder imports it.
- `gororoba_quantum/designs.py` -- the four designs, checked by statevector and
  operator equality over every instance, including both SELECT sign strategies.
- `gororoba_quantum/experiments.py` -- experiment groups: a primary circuit, its
  controls, their ideals, and the summary of each design's observable.
- `gororoba_quantum/live_run.py` -- live system discovery, circuit-derived
  capability admission, degraded-hardware-filtered routing, recursive Target
  validation, ESP-and-coherence-ranked selection, joint disjoint replica placement,
  cross-group PUB fusion with namespaced result registers,
  direct pinned-system probing, approval-gated cross-system reselection, local
  noise simulation, gated client-side Sampler submission, and execution-time
  replay.
- `gororoba_quantum/QPU_OPTIMIZATION.md` -- matched folded-QPE and N=21
  feed-forward families, exact labeled laws, bounded statistical and charged-time
  optimization, invocation reservations, and artifact-bound unapproved cases.
- [Local simulation and precision](gororoba_quantum/LOCAL_COMPUTE.md) -- explicit
  CPU policy, precision-at-budget selection, finite cost scenarios, failed
  branching qualification, and separate CUDA/Aer capability evidence.
- `gororoba_quantum/runtime_contracts.py` -- credential-free checks for packed
  and fused static and dynamic circuits, joint placement, exact PUB
  cardinalities, capability and routing admission, recursive Target support,
  coherent calibration snapshots, bounded-angle system isolation,
  renewed-approval enforcement, every-job revalidation, submission recovery,
  archive integrity, per-replica result order, twirling shots, and
  source-manifest stability.
- `gororoba_quantum/DESIGN_NOTES.md` -- mechanism, prediction, observable, and
  falsifier for each design, and the live-calibration policy.
- `results/live/<UTC start>/` -- retained JSON and QPY evidence. Schema 7 adds
  observable contracts, bounded experiment selection, invocation budgets, and
  execution-cost approval binding to the fused-PUB timing and usage records. Earlier
  schemas remain historical evidence under `results/live/README.md`.
- `results/hw_estimate/` -- fixed ibm_fez design compiles and the replayable
  FakeFez modular-synthesis crossover capture.

## Designs

- Design A turns the octonion associator into a Fano Z-string read out as a
  deterministic measurement bit (3 qubits, ancilla-free).
- Design B turns a sedenion zero divisor into perfect destructive interference
  through a one-ancilla linear combination of unitaries (4 data qubits + 1
  ancilla), compiled to 46 CZ on ibm_fez.
- Design C measures the Walsh spectrum of the associator phase at dims 8, 16,
  and 32, with sign-flip and omitted-block controls. The high-bit exemplar
  escalates from a Bernstein-Vazirani character through a rank-2 quadratic to
  a non-flat cubic spectrum with exact closed-form probabilities.
- Design D sweeps the relative phase of design B's input and fits offset,
  visibility, and phase of the (1 - s cos phi)/2 fringe.

## Setup

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
cd gororoba_quantum
"$PYTHON" verify.py
"$PYTHON" designs.py
"$PYTHON" claim_boundaries.py
"$PYTHON" sedenion_bundle.py
"$PYTHON" annihilator_strata.py --max-dimension 256
"$PYTHON" factoring.py
"$PYTHON" target_flip.py
"$PYTHON" target_flip_certificate.py --check
"$PYTHON" modular_arithmetic.py
"$PYTHON" order_finding.py
"$PYTHON" compile_evidence.py --seeds 20261010 \
  --candidate one_clean_cycle >/dev/null
"$PYTHON" runtime_contracts.py
"$PYTHON" hybrid_shor.py plan 15
"$PYTHON" hybrid_shor.py simulate 15 --shots 256 --seed 7
"$PYTHON" live_run.py --out ../results/live
```

The final command reads live calibration and performs local compilation and
noise simulation. It omits `--submit` and sends zero quantum jobs. Every
`live_run.py --submit` invocation binds a written case to the user's authority
under `AGENTS.md`. The current campaign uses the recorded conditional authority
and retains the review, merge and live-binding gates above.

requirements.txt pins the tested numpy, qiskit, qiskit-aer, and
qiskit-ibm-runtime versions. The modules run as scripts from gororoba_quantum/,
which puts their sibling imports on sys.path; they form no installable package,
and pyproject.toml carries only lint and type-check configuration. The IBM Quantum credential
is read from the qiskit account store (`~/.qiskit/qiskit-ibm.json`), not from
this repository. The kernel ground-truth CSV is located through `GOROROBA_ROOT`
(default `~/Github/open_gororoba`); `verify.py` needs that checkout, the circuit
modules do not.
