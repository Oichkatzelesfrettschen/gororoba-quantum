# Adversarial review: Belenos three-photon suppression-law case

Target: branch `quandela/belenos-suppression-law-case`, commits c1c9baace, a3646b788 and 50e367900 on top of
5cb08d53f. Diff read in full for the design document, the case script, the literature and source entries and the
ledger rows; retained JSON read where a finding needed it. Nothing was sent to a provider.

**Artifact and field.** A written hardware case (design document), its builder, checker and preregistered analysis
(`scripts/belenos_suppression_case.py`), and the frozen request files. The fields are linear-optics many-boson
interference (permanents, threshold detection, partial distinguishability), small-sample statistics, and
provider-budget engineering for Quandela qpu:belenos.

## Deterministic checks (all run in the worktree)

| Check | Result |
|---|---|
| `belenos_suppression_case.py --check` | exit 0: two jobs bound, suppressed set of 12 equals the label-sum rule, collision-free mass 0.333333 in both arms |
| `pytest tests/scripts/test_belenos_suppression_case.py` | 20 passed |
| `ci/seed_provenance.py --check`, `--shrink`, `--runtime` | all exit 0 (317 seed literals accounted; runtime ledger matches) |
| `test_hypercomplex_libraries.py -k retained_inventory` | 9 passed |
| pinned `ruff format --check`, `ruff check`, `mypy` on both Python files | clean |
| `git diff --check` | clean |
| sha256 of both `cases.json`, both `circuit.json`, `catalogue.json` | match the digests the design document cites |

## Findings, worst first

### 1. SERIOUS: a partial job crashes the preregistered analysis instead of reading "undecided"

- **Barb.** The design promises "Undecided: fewer than four complete iterations", but the code never reaches the
  verdict when a job is cut short.
- **Grounding.** `qd_platform.result_summary` (scripts/qd_platform.py:1928-1931, 1988-1990) appends one
  `{"missing": true}` entry per unanswered iteration of a partial job. A `malformed` entry can also arrive without an
  `iteration` dict. `bound_setting` reads no `compilation_seed` from such an entry, finds 0 matches and raises. The
  retained teleportation job-01 run
  (`results/quandela/runs/2026-10-30T202246Z-qpu_belenos-teleportation_rehearsal-job-01/results.json`) ends with
  exactly `{"missing": true}` after it hit `max_duration`. A synthetic probe gave job-01 three counted iterations
  plus one missing entry, and `analyze` raised
  `ValueError: a result iteration with compilation_seed None binds to 0 settings`.
- **Remedy.** Skip and tally the uncounted kinds (`missing`, `malformed`, `error`) before binding, the way
  `qd_teleportation_rehearsal.py:1079` (`UNCOUNTED`) and :1150 do. Report them as excluded iterations. Let
  `decide` return "undecided" on the four-iteration rule. Add a test that uses the retained missing-entry shape.

### 2. SERIOUS: the analysis accepts the same job twice and decides on pseudo-replicates

- **Barb.** The design says "every compilation seed counts once", but uniqueness is enforced per run, not across runs.
- **Grounding.** In `analyze`, the `bound` set is created inside the per-run loop. A probe ran
  `analyze([run-job-00, run-job-00])` and returned 4 iterations per arm with `complete: true`, from 2 distinct
  iterations per arm. The duplicated values halve the apparent spread and double the dof. The design invites the
  case: "a repeat of one job fits inside that budget". A repeat of a partial job-00 carries the same eight seeds and
  would be pooled with its partial original.
- **Remedy.** Require exactly one run per job name (`manifest["job"]`) and enforce global seed uniqueness across
  runs. Preregister how a repeat replaces a failed job: the repeat's run supersedes the original, never pools with
  it. If the repeat needs fresh compilation randomness, it takes new QRNG seeds.

### 3. SERIOUS for the secondary endpoints: compile error biases s upward, so the level verdict, the implied HOM and the "overlap mapping" falsifier are confounded

- **Barb.** Limits says compile error shows up as "the between-iteration spread the interval carries". It is a
  one-sided bias, because s is bounded below by the ideal 0.
- **Grounding.** I perturbed F by exp(i eps H) with random Hermitian H, 200 draws per eps, ideal indistinguishable
  photons:

  | single-photon column TVD | mean s | sd of s |
  |---|---|---|
  | 0.010 | 0.001 | 0.001 |
  | 0.026 | 0.007 | 0.003 |
  | 0.052 | 0.029 | 0.015 |
  | 0.078 | 0.065 | 0.027 |
  | 0.102 | 0.114 | 0.055 |

  The mean shift is about twice the spread. The retained Belenos one-photon record reads dark blocks at
  a = 0.005 to 0.050 (docs/notes/quandela/README.md, packed dark/bright blocks), so a shift of 0.01 to 0.07 on s is
  realistic. At a slope of about -1.1 per unit HOM (hom_curve 0.85 to 0.90), a shift of +0.03 reads as about -0.025
  HOM. The g2 sensitivity adds about +-0.03 in s (0.188 at half g2, 0.246 at double).
- **Consequences.**
  - "Resolves the effective HOM to about 0.01" is unsupported.
  - "Wrong about the Perceval overlap mapping if s_periodic leaves 0.21 +- 0.05" is not a clean falsifier, because
    compile error and g2 move s by the same order.
  - "The result also measures the effective three-photon indistinguishability" overclaims.
  - The primary decision against 0.502 is unaffected.
- **Remedy.** Each counted iteration returns its served mesh in `result_fields.computed_circuit`. The repository
  decodes it already (`photonic_compilation_audit._elements`, `qd_belenos_mesh.decode`). Recompute each iteration's
  forecast on the served 6x3 submatrix, and preregister that the level and implied-HOM endpoints use it.
  Otherwise, demote the implied HOM to a lower bound, drop the 0.01 resolution claim, and restate the overlap
  falsifier with compile error and g2 named as confounders.

### 4. SLOPPY: no floor on accepted events, so a truncated iteration counts as "complete" with full weight

- **Grounding.** `decide` counts every iteration with at least one accepted event. A probe replaced one job-01 control
  iteration with 3 accepted events. It entered `iterations` with fraction 0.0, and `complete` stayed true. The
  unweighted t interval gives it the weight of a 400-event iteration. The design's word "complete" is never defined
  in code.
- **Remedy.** Preregister a floor, for example at least 200 accepted events (half of `SAMPLES_PER_ITERATION`), for an
  iteration to count. Report sub-floor iterations separately.

### 5. SLOPPY: the timing mechanism is wrong; the 180 s figure survives only through its measured floor

- **Barb.** The design says "the modeled acquisition is 2.4 s per iteration ... so compilation dominates". Retained
  runs say acquisition is the larger term.
- **Grounding.** I fitted fixed time plus shots times per-shot cost over retained qpu:belenos runs:

  | Runs | Fixed time per iteration | Per-shot cost |
  |---|---|---|
  | bdsc_stationarity (24 iterations, 2.4 M shots, 166 s) and bdsc_qualification (12 iterations, 3.6 M shots, 90 s) | 6.6 to 6.9 s | 2.9 µs, one-photon |
  | teleportation job-01 (three photons, `min_detected_photons` 3, 11 counted iterations, 24.9 M shots, cut at 300 s) | 6.9 s, taken from the BDSC fit | 9 to 9.7 µs |
  | teleportation job-00 (degraded chip, 7.2 M shots, 0 samples, 292 s) | 6.9 s, taken from the BDSC fit | about 35 µs |

  At the 1,182,561-shot estimate, an iteration takes about 18 to 21 s and four take about 75 to 86 s. At the
  1.5 M cap and the brief's 12.8 µs bound, an iteration takes 26.1 s and four take 104 s. In the degraded regime an
  iteration takes about 59 s and four take about 236 s. That is above the 180 expected seconds but below the 300 s
  `max_duration`, so no job is cut off in any measured regime.

  The teleportation job-01 case used the same clock model as `expected_seconds` (10 s plus samples over clock times
  three-click probability). It predicted 240 s and was cut at 300 s with 11 of 12 iterations
  (ascella-belenos-entanglement-teleportation.md:515-520). That is a direct falsification of the clock model. This
  case escapes only because `ITERATION_SECONDS` 27.3 is the max() floor.
- **Remedy.** Replace the acquisition term with fixed time plus `max_shots` times the per-shot cost, citing the runs
  above. State 300 s as the worst case per job. Delete "compilation dominates".

### 6. SLOPPY: "expected 2.2 to 2.5 credits" contradicts the billing rule the code enforces

- **Grounding.**
  - scripts/qd_platform.py:1314 says "A job bills its largest iteration's max_shots" and computes the ceiling from it.
  - Teleportation job-00 charged 2.2 credits, its full ceiling (teleportation design document, "Result of job-00").
  - The case's own `plan` returned `estimated_credits` 2.5.
- **Remedy.** State 2.5 credits per job, 5.0 for the case, and 7.5 if one job is repeated (still under 8).

### 7. SLOPPY: the strongest null available, the paired contrast, is left out of the decision

- **Grounding.** Every |F_jk| equals 1/sqrt6. So for distinguishable photons, s_control - s_periodic is identically 0
  for any per-mode detection efficiencies and any g2 (retained forecast: -1.1e-16). The design states this fact
  ("Detector inhomogeneity therefore moves the periodic and control fractions of a distinguishable source together")
  and then decides on absolute forecasts that depend on the t_out detection model. The contrast is +0.436 for
  indistinguishable photons, 0 for distinguishable photons and -0.138 for the mean-field sampler, so a lower bound
  above 0 rejects both alternatives without the detector model.
- **Remedy.** Make "lower 99 % bound of the paired contrast >= margin" co-primary with the absolute rule, or the
  primary rule. Keep the absolute rule as the model-level statement.

### 8. SLOPPY: job-01 queues behind job-00 with no yield gate

- **Grounding.** The design submits both jobs back to back ("runs one job at a time and queues one"). The teleportation
  precedent spent 2.2 credits on a job with 0 samples in a degraded state. `plan` refuses a degraded record at live
  figures, because Perceval returns no finite estimate (scripts/qd_platform.py:1334-1336). The residual risk is a chip
  that degrades without a record update.
- **Remedy.** Submit job-01 only after job-00's collect shows a preregistered minimum yield, for example at least
  half of the 1600 accepted events.

### 9. SLOPPY: excluded events are pooled across arms and runs

- **Grounding.** `excluded` in `analyze` sums over all iterations. The Limits section says a setting-dependent
  detector or selection factor is bounded by the control check, but an arm-dependent exclusion rate cannot be seen
  in the record.
- **Remedy.** Report exclusions per arm and per iteration.

### 10. SLOPPY: the cyclic label-sum form is attributed to a source read abstract-only, whose own note covers a different input

- **Grounding.** literature.md entry 33 summarizes the 2010 law as "n bosons on the n input ports". The case uses
  m = 6 modes with n = 3 photons on a period-2 input. I believe the m = p n periodic generalization is stated in
  later Tichy et al. work (the 2012 New J. Phys. paper or 1312.3080); verify against the paper body. No correctness
  consequence: the set is computed from permanents and verified independently below.
- **Remedy.** Cite the law's periodic form only after reading the derivation, or say "agrees numerically with the
  label-sum rule" without attributing the m/n form.

### 11. COSMETIC: the control is setting-independent only for full or symmetric distinguishability

- **Grounding.** With one photon fully distinguishable and the other two identical, the periodic s is 0.75 for
  each choice of photon. The control s is 0.50 (photon on Fourier port 0 or 2) or 0.75 (port 1). A source whose
  demultiplexed time bins differ in overlap shifts the control forecast. At HOM 0.879 the shift is likely inside the
  0.10 control tolerance.
- **Remedy.** Name per-source overlap asymmetry in Limits.

### 12. COSMETIC: the mean-field definition remains unverified against the paper, and it does not bind

- **Grounding.**
  - An independent implementation of the stated definition gives s = 0.7241 at the ideal point.
  - A continuous-phase Monte Carlo with 2e4 draws gives 0.7249, which confirms that the 7-point grid is exact.
  - The definition (n bosons in one random-phase superposition of the input ports, multinomial output) matches my
    recollection of Tichy et al. 2014. My confidence in that match is about 75 %; reading the sampler section raises
    or lowers it.
  - The binding null is the distinguishable 0.602, so the mean-field row cannot change the primary decision. The
    design already says this.
- **Remedy.** None required before submission; the read the design asks for stands.

## SOUND

- **Suppressed set.** I recomputed it independently with permanents: the 12 outputs 013, 014, 023, 025, 034, 035,
  124, 125, 134, 145, 235 and 245. The other 8 outputs have probability 1/24 each, and the collision-free mass is
  1/3. The set is invariant under transpose, complex conjugation and output-order reversal of F, so a
  row-versus-column or mode-reversal convention mismatch on the server cannot move it. With threshold detectors a
  three-photon three-click event is necessarily collision-free, so the eligibility rule selects exactly the
  permanent-law events plus the g2 and loss terms the click model carries. The catalogue confirms
  `detector: threshold`. The retained three-photon Belenos counts hold only 0/1 entries, with 6 four-click events in
  13,200.
- **Control.** The control has no zero permanent: minimum 0.00463, collision-free mass 1/3, ideal s 0.667. It uses
  the same chip input modes 16, 18 and 20, the same six detectors and the same template, and differs only in the
  programmed columns. The design argues correctly that an input or output phase scramble would not serve as a control.
- **Fourier-size claims.** Fourier sizes 3, 4 and 5 have no collision-free zero for any input triple. Nine modes give
  54 of 84 (0.643) and twelve modes 144 of 220 (0.655).
- **Iteration binding.** It uses server-echoed fields: `result_summary` copies `entry["iteration"]` from the answer
  (scripts/qd_platform.py:1961), not by position. Retained Belenos results carry `compilation_seed` and
  `circuit_params` per iteration. A reordered answer cannot move counts between arms; the failure is limited to
  findings 1 and 2.
- **Shot cap.** Teleportation job-01 realized 0.84 to 1.12 times its per-iteration estimate. The cap here is 1.27
  times the estimate, and `plan` refuses when the live estimate exceeds `max_shots`.
- **Statistical power.** t(0.99, 3 dof) = 4.541. The expected upper bound is 0.208 + 4.541 * 0.0101 = 0.254 against
  the 0.502 threshold. The bound crosses the threshold only if the per-iteration sd reaches about 0.11, more than
  five times the binomial 0.020. Type I error under the distinguishable null needs a mean about 8 standard errors
  low. The t rule is valid and powerful here; the weak point is the analysis plumbing.
- **Gates.** Seed ledger rows, the QRNG draw file and the library inventory are consistent, and every gate listed
  above passes.

## Steelman

The physics core is right and stronger than the document says. With one photon distinguishable and two identical,
the periodic s is 0.75, above the distinguishable 0.60. Pairwise interference alone therefore raises the suppressed
fraction, and an upper bound at or below 0.50 requires a substantial fully indistinguishable three-photon component.
The decision certifies genuine three-photon interference against distinguishable, partially distinguishable and
mean-field alternatives, and the design should say so. The choices of window, layout, seeds and template are
reproducible from retained bytes, and `--check` rebuilds every file bit for bit. The margin between forecast and
null (0.21 against 0.50) leaves the primary decision robust to every confounder found here.

## Verdict

**Fit after named fixes.** The primary claim, that suppression exceeds the distinguishable and mean-field
forecasts, stands on verified permanents and has power near 1. The analysis is preregistered, so its defects must
be fixed before submission, not after collection:

- Skip uncounted iterations instead of raising (finding 1).
- Accept one run per job, with global seed uniqueness (finding 2).
- Preregister a floor on accepted events per iteration (finding 4).

The design document needs these corrections:

- State the compile-error bias and demote or re-ground the implied-HOM and level endpoints (finding 3).
- Replace the seconds mechanism (finding 5).
- Correct the credit expectation to 2.5 per job (finding 6).

Making the paired contrast co-primary (finding 7) and gating job-01 on job-00's yield (finding 8) are strongly
recommended. A trustworthy result then needs one more demonstration: the analysis run on a synthetic partial and
duplicated record returns "undecided" and refuses, respectively, instead of raising or pooling.
