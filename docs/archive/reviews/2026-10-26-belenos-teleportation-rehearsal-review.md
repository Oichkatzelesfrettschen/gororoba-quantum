# Codex review: Belenos teleportation rehearsal and its job-01 case

Reviewer: Codex CLI 0.164.0, model `gpt-daybreak-blue-latest` at high reasoning effort, in a workspace-write sandbox
without network access, run on 2026-10-26 for 35 minutes against commit 9ab20e9 of pull request #560 in a disposable
detached worktree. The owner requested a deep peer review of the plan, the jobs and the submission; the brief is
[2026-10-26-belenos-teleportation-rehearsal-review-goal.md](2026-10-26-belenos-teleportation-rehearsal-review-goal.md).
The report follows verbatim, with its headings demoted one level, and then the disposition of each finding.

## Report

### Summary verdict

Job-01 is mechanically ready for the operator to take the fresh read and run `--prepare` on 2026-10-29: the request
threading, duration refusal, resumability, offline replays, seed provenance, and 77 required tests passed. Job-01 is
**not ready for owner approval or submission as a confirmatory C1 experiment**. The P0 blockers are: the verdict
overstates accepted-event fidelity as circuit-family conformance; threshold-accepted multiphoton sectors fall outside
the single-copy classical benchmark; F* and its `0.02` allowance do not bound stated model omissions; modeled attempts
do not bound the unknown exposure profile and the maximum benchmark is wrong for the negative verdict; event-level
independence is unestablished and partial results can receive definitive verdicts; own-read binding tests the published
record rather than physical chip readiness; free-form approval text does not prove owner approval; and the last live
read is not atomic with POST. Preparation can gather and retain the case-specific evidence, but the owner should not
approve submission until the claim, benchmark domain/attempt denominator, dependence/partial-result rules, systematic
bound, approval artifact, and residual live-record semantics are repaired or explicitly narrowed.

### Review scope and evidence convention

The reviewed artifacts span quantum-optical instrument modeling, statistical inference, retained-run provenance, and
submission tooling. Every statement below is labeled **verified** when it follows from a cited source or executed
offline check, and **inferred** when it is a consequence that was reasoned from verified premises. All commands used
the review brief's pinned Python environment when they invoked Python. The review contacted no provider or network
service and read no credential.

### 1. Plan and design

#### P0: the verdict does not establish the declared breadth of C1 local conformance

- **Location:** `docs/design/ascella-belenos-entanglement-teleportation.md:19`,
  `docs/design/ascella-belenos-entanglement-teleportation.md:297`,
  `docs/design/ascella-belenos-entanglement-teleportation.md:353`,
  `docs/state/plans/ascella-belenos-entanglement-teleportation.json:198`,
  `scripts/qd_teleportation_rehearsal.py:464`, and `scripts/qd_teleportation_rehearsal.py:985`.
- **Evidence, verified:** The C1 definition requires a qualified preparation/analyzer model, setting-to-count
  association, and registered tolerances. The design registers ideal acceptance `1/18` and conditional fidelity `1`,
  then says that `beats-classical` establishes C1. The plan repeats that interpretation, and the manifest calls the
  target “local conformance of the single-chip teleportation circuit family.” The analyzer binds each result to its
  input setting and records rejection categories, but `scripts/qd_teleportation_rehearsal.py:1012-1041` computes the
  verdict only from accepted-event pooled fidelity, a Hoeffding radius, a systematic allowance, and the classical
  bound. Neither acceptance-rate disagreement nor rejection-distribution disagreement can prevent
  `beats-classical`.
- **Evidence, verified:** An offline counterexample constructed six inputs with the documented 900 samples per input,
  five correct accepted events per input, and 895 invalid Bell-pattern events per input. The existing analyzer returned
  `{'samples_per_input': 900, 'verdict': 'beats-classical', 'fidelity': 1.0, 'accepted': 30,
  'pattern_rejections_per_input': 895, 'classical_bound': 0.6936680477754957,
  'radius': 0.2770430227115183, 'margin': 0.009288929512985877}`.
- **Consequence, inferred:** That record supports the narrower statement that accepted-event pooled conditional
  fidelity clears the applicable bound. It does not establish conformance of the preparation/analyzer family to all
  registered observables. The present C1 interpretation can therefore support an invalidly broad claim.
- **Smallest fix:** Narrow the rehearsal claim and manifest interpretation to “accepted-event pooled conditional
  fidelity exceeds the applicable classical bound; acceptance and rejection-distribution conformance remain
  unestablished.” If broad C1 conformance is required, preregister acceptance and rejection-category tolerances and
  require those checks before assigning C1.

The narrower question and falsifier are internally aligned. **Verified:**
`docs/design/ascella-belenos-entanglement-teleportation.md:455-462` asks for pooled conditional fidelity, which is what
`scripts/qd_teleportation_rehearsal.py:1012-1024` computes. The positive rule and falsifier at design lines 353-359
match the code at lines 1034-1041: the lower confidence bound minus the allowance above the classical bound produces
`beats-classical`; the upper confidence bound below the bound produces `at-or-below-classical`; other complete cases
produce `inconclusive`. **Verified:** `tests/scripts/test_qd_teleportation_rehearsal.py:295-308` exercises all three
verdicts, while lines 428-453 and 574-590 cover silent-input and partial-result handling. The plan confines job-00 to
C1 and excludes C2/C3 at plan lines 198-201; job-01 reuses that claim level at lines 226-229.

Item-specific check deferred: the complete rehearsal test file belongs to Item 7 and has not yet run.

### 2. Physics of the instrument

The ideal three-photon instrument is internally sound. **Verified:**
`scripts/qd_teleportation_rehearsal.py:237-245` loads `pcvl.catalog["postprocessed cnot"]`, requires a six-mode
unitary, and requires vacuum heralds `{4: 0, 5: 0}`; local catalogue inspection returned
`{'unitary_modes': 6, 'logical_modes': 4, 'heralds': {4: 0, 5: 0}, 'postselect':
'([0, 1] == 1 & [2, 3] == 1)'}`. Lines 274-285 embed those modes as `(a0,a1,b0,b1,h0,h1)`.
`scripts/qd_network_protocol.py:227-236` implements the two balanced beam splitters, lines 251-269 derive the
two-click Bell patterns, lines 343-362 derive teleportation frames and fidelities, and lines 365-370 decode Z as
`raw xor x`, X as `raw xor z`, and Y as `raw xor x xor z`. The derived table is `1100/0011 -> (1,0)` and
`1001/0110 -> (1,1)`. `scripts/qd_teleportation_rehearsal.py:314-336` thresholdizes mode occupations, requires
exactly three clicks, and accepts only one receiver click plus a registered Bell pattern after rejecting
outside-layout, herald, receiver, and Bell-pattern violations.

**Verified command:** with the mandated environment, the focused command
`MPLCONFIGDIR=/var/tmp PCVL_PERSISTENT_PATH=/var/tmp "$PYTHON" -m pytest -p no:cacheprovider -q` followed by the
three Bell-table/frame/decoder nodes in `tests/scripts/test_qd_network_protocol.py` and the four
frame/template/CNOT-success/classification nodes in `tests/scripts/test_qd_teleportation_rehearsal.py` returned
`7 passed in 1.69s`. An offline intermediate-state projection partitioned each propagated occupation by the catalogue
predicate before the analyzer. For all six Pauli inputs it returned CNOT-success norm `1/9`, failed-branch norm `8/9`,
accepted success probability `1/18`, accepted failed-branch probability `0`, and conditional fidelity `1`.

#### P0: threshold-accepted multiphoton inputs leave the single-copy classical benchmark's domain

- **Location:** `docs/design/ascella-belenos-entanglement-teleportation.md:178`,
  `scripts/qd_teleportation_rehearsal.py:314`, `scripts/qd_teleportation_rehearsal.py:662`,
  `scripts/qd_teleportation_rehearsal.py:676`, and `scripts/qd_teleportation_rehearsal.py:715`.
- **Evidence, verified:** The design states that accepted multiphoton sectors carrying extra input copies void the
  `2/3` benchmark and require a new derivation. `photon_distribution` enables Perceval's `g2` source model;
  `detected_clicks` maps every occupation `n >= 1` to a threshold click with probability
  `1-(1-eta)^n`; `classify` sees only those click flags. Perceval's local source distribution at `g2=0.011` assigns
  probability `0.005499659791...` separately to an extra photon on q, a, and b; the q sector carries another copy
  of the prepared input.
- **Evidence, verified:** An offline enumeration using the retained job-00 manifest and circuit called
  `photon_distribution(setting, circuit, hom=1.0, g2=0.011)`, thresholdized every output occupation, classified it,
  and divided accepted mass above three photons by all accepted mass. It returned `0.020997773` for +Z,
  `0.013788340` for -Z, and `0.025434297` for each X/Y input. Separate +Z four-photon projections added one photon
  to a0 or b0, partitioned the state by the catalogue postselection predicate, then propagated and scored each
  partition. The extra-a probe returned zero success-branch norm, failed-branch accepted probability
  `0.060185185185185126`, and correct probability `0.04629629629629626` (conditional fidelity `0.7692307692`). The
  extra-b probe returned zero success-branch norm, failed-branch accepted probability `0.07407407407407403`, and
  correct probability `0.009259259259259257` (conditional fidelity `0.125`). Thus ideal three-photon accepted events
  exclude a failed CNOT branch, while multiphoton threshold events can include one.
- **Consequence, inferred:** The current rule can report `beats-classical` for an accepted ensemble containing an
  input sector outside the single-copy Choi benchmark's domain. A small source probability does not by itself bound a
  postselected classical strategy, because the strategy may condition success on that sector. The registered `0.02`
  allowance has not been shown to upper-bound the best permitted multicopy measure-and-prepare strategy.
- **Smallest fix:** Derive and use a classical bound for the registered source mixture and permitted postselection,
  or suppress `beats-classical` until a registered bound proves that accepted extra-input-copy contamination cannot
  raise the classical optimum past the decision margin. Photon-number-resolving exclusion would also restore the
  single-copy domain, but the threshold record cannot provide that exclusion.

#### P2: the ideal-only CNOT-success test name claims the multiphoton domain too

- **Location:** `tests/scripts/test_qd_teleportation_rehearsal.py:102`.
- **Evidence, verified:** `test_every_accepted_pattern_implies_the_cnot_success_branch` calls only `ideal_clicks`,
  checks three logical clicks and zero herald clicks, and never exercises `g2` or thresholded multiphoton sectors.
  The verified extra-a and extra-b probes above are counterexamples outside that ideal sector.
- **Smallest fix:** Rename the test to
  `test_every_ideal_three_photon_accepted_pattern_implies_the_cnot_success_branch` and add a test documenting that a
  multiphoton accepted event can lie outside the catalogue postselection predicate.

`scripts/qd_teleportation_rehearsal.py:715-726` conditions variant scores on provider-visible events with at least
three clicks, while lines 751-754 weight pooled fidelity by each input's accepted share. **Verified:** threshold
detection and multiphoton emission therefore change the selected physical ensemble and its conditional fidelity.
**Inferred:** the three-click filter does not bias the explicitly defined success-weighted accepted-event estimand; it
defines that estimand. It does bias an interpretation as unconditional channel fidelity or an equal-input mean, and
threshold loss makes the selected sector input- and mode-dependent.

Item-specific check deferred: Item 7 owns the full rehearsal test files; only the seven focused physics tests ran
here.

### 3. Noise model and its omissions

#### P0: F* is a point-model forecast, not a lower bound over the stated omissions

- **Location:** `scripts/qd_teleportation_rehearsal.py:165`, `scripts/qd_teleportation_rehearsal.py:662`,
  `scripts/qd_teleportation_rehearsal.py:676`, `scripts/qd_teleportation_rehearsal.py:698`,
  `scripts/qd_teleportation_rehearsal.py:729`, `scripts/qd_teleportation_rehearsal.py:776`, and
  `docs/design/ascella-belenos-entanglement-teleportation.md:305`.
- **Evidence, verified:** `photon_distribution` uses one scalar indistinguishability and one `g2` value;
  `detected_clicks` applies independent per-mode loss and thresholding; `detection_efficiency` deterministically maps
  global transmittance and relative `t_out` to efficiencies. The three F* variants at lines 729-748 share the same
  scalar HOM and g2 and vary only perfect, uniform, or per-mode transmission. `derive` takes their minimum, floors it
  to `0.01`, and adds a fixed `0.02` after any fresh-read drop. The retained source-only, uniform-loss, and anchor
  per-mode pooled fidelities are `0.8820166801`, `0.8627356422`, and `0.8679104643`; the retained
  `noise-model.json:1-16,149-233` records F* `0.86`, leaving only `0.0027356422` between the minimum modeled point
  and the floor.
- **Evidence, verified:** The design at lines 305-311 says the model omits chip three-photon interference, service
  compilation, per-mode detector efficiency, and dark response, while lines 327-333 assert that `0.02` covers dark
  clicks and compilation phase error. The source comment at lines 165-166 says dark clicks are “bounded in justify,”
  but `justify` at lines 894-897 only calls `simulation` and `derive`; it computes no dark-count or phase-error bound.
  With identical fresh and anchor reads, the job-01 procedure at design lines 464-470 makes the allowance exactly
  `0.02`, so the own-read construction supplies no empirical cushion for the omitted terms.
- **Evidence, verified:** An offline sensitivity reran `variant_scores` with retained g2 and per-mode transmission.
  Pooled fidelity was `0.8679104643` at HOM `0.888`, `0.8302165225` at `0.838`, `0.8037466633` at `0.800`, and
  `0.7420110124` at `0.700`; a five-point scalar-HOM change produced a `0.0376939418` drop. A separate seeded
  Perceval probe used every retained compilation seed and `NoiseModel(..., phase_error=value)`: maximum uniform phase
  errors `0.015`, `0.03`, and `0.10` rad produced respective drops `0.0002764`, `0.0010401`, and `0.0114366`.
  This registered random-phase mechanism stays within `0.02` through `0.10` rad but is not a worst-case compilation
  bound. `docs/notes/quandela/literature.md:1231-1240,1301-1319` records residual phase scales through `0.1` rad,
  compile/calibration observable bias through `40%`, and retained Belenos discrepancies beyond static phase-noise
  fits; the case supplies no bound from actual service compilation to the tested random-error model.
- **Consequence, inferred:** Flooring is conservative only relative to the three computed transmission variants. A
  job can pass the live model gate while an unbounded preparation/analyzer compilation error or three-photon internal
  state makes the experiment underpowered or the C1 interpretation invalid. A scalar pairwise-HOM point estimate
  cannot bound the general three-photon internal-state Gram matrix or its collective phase.
- **Smallest fix:** Name F* a model forecast. Retain a systematic allowance only for terms with explicit derivations.
  Before submission, add preregistered three-photon-overlap and compiled-mesh sensitivity bounds whose joint effect
  stays below the allowance, or suppress C1/`beats-classical` when those bounds are absent. Make `justify` emit the
  actual bound calculation instead of a constant.

Dark response alone appears smaller under a declared sensitivity model. **Verified:** the layout rejects any window
mode above `100 Hz` at `scripts/qd_teleportation_rehearsal.py:608-645`; `100 / 4.94 MHz = 2.0243e-5` per pulse.
**Inferred under independent per-pulse dark clicks:** an offline exact convolution of the retained anchor rates changed
pooled fidelity from `0.8679104643` to `0.8672907517`, a `0.0006197126` drop. Setting every logical-window mode to
the permitted `100 Hz` changed it to `0.8606282692`, a `0.0072821951` drop. The `0.02` allowance covers those dark
sensitivities. **Verified limitation:** `docs/notes/quandela/literature.md:1206-1210` says the provider record lacks
coincidence-window, pump-gating, and per-iteration exposure semantics, so the independent per-pulse convolution is a
sensitivity study rather than a hardware-backed bound.

The model does include source g2, threshold loss, and nonuniform `t_out`, and flooring the minimum is conservative
for the three computed values. **Verified:** all variants reuse one scalar HOM at
`scripts/qd_teleportation_rehearsal.py:740-746`, so the unexplored domain is the broader multiphoton
distinguishability family rather than all optical noise.

Checks not run for this item: an arbitrary three-photon Gram-matrix scan, because the repository supplies no
registered parameterization; a worst-case compilation-error optimization, because only the pinned Perceval uniform
phase-error mechanism was registered; and a hardware-backed dark-window calculation, because the retained provider
record lacks the required timing semantics.

### 4. Classical bound

The single-copy SDP implementation is sound. **Verified:** `scripts/qd_classical_benchmark.py:155-193,239-310`
enforces positive Choi and partial-transpose cones, the trace-nonincreasing constraint, a projected dual certificate,
and a maximum `1e-6` primal/dual gap. For uniform Pauli-six inputs,
`sum p_i rho_i = I/2` and `sum p_i rho_i tensor rho_i = (I+SWAP)/6`, so every measure-and-prepare outcome has ratio
at most `(tr M/3)/(tr M/2)=2/3`; `tests/scripts/test_qd_classical_benchmark.py:48-54` verifies the certificate and an
achiever. Inverting the retained per-input sample probabilities produced attempt priors
`(+X,+Y,+Z,-X,-Y,-Z)=(.164933205,.162657794,.137594492,.165024846,.162653659,.207136005)` and certified
`B=0.6936680477754965` with gap `5.79e-9`; a 2028-strategy grid reached `0.6936680365661186`. **Verified command:**
five focused benchmark/rehearsal tests returned `5 passed in 1.97s`.

#### P0: modeled attempts do not upper-bound an unknown physical attempt profile

- **Location:** `scripts/qd_classical_benchmark.py:329`, `scripts/qd_teleportation_rehearsal.py:770`, and
  `scripts/qd_teleportation_rehearsal.py:945`.
- **Evidence, verified:** `attempts_benchmark` correctly treats actual attempts as input priors, but `model_benchmark`
  substitutes `samples_j / modeled_sample_probability_j`. Analysis reads `nb_shots_used`, which equals returned
  samples for these sample-limited iterations rather than optical attempts, and takes the maximum of the reported and
  modeled candidates. Equal returned counters give `0.6666666670`; the model gives `0.6936680478`. An equally
  compatible physical profile with twice as many Z attempts as each X/Y attempt gives `0.7500000004`; equal returned
  samples cannot exclude it when Z sample probability is half X/Y.
- **Consequence, inferred:** `max(2/3,0.6937)` compares two candidate profiles and does not upper-bound the classical
  optimum for an unknown exposure profile. A positive claim can therefore use a bound below the applicable optimum.
- **Smallest fix:** Require measured optical attempts/exposure per input, or maximize the SDP over preregistered and
  validated attempt-ratio bounds; otherwise return `inconclusive`. Keep the model value only as a power forecast.

#### P0: the maximum candidate bound is anti-conservative for the negative verdict

- **Location:** `scripts/qd_teleportation_rehearsal.py:1029`.
- **Evidence, verified:** The same maximum drives both verdict directions. An offline six-input, 900-sample synthetic
  record with pooled fidelity `0.67` returned radius `0.0206495677`, upper limit `0.6906495677`, equal-attempt bound
  `0.6666666670`, chosen modeled bound `0.6936680478`, and verdict `at-or-below-classical`. The upper confidence limit
  is above the equal-attempt candidate, so the record does not falsify that candidate.
- **Smallest fix:** Test `beats-classical` against a justified upper bound on the optimum and
  `at-or-below-classical` against a justified lower bound, naturally `2/3` for the single-copy Pauli-six ensemble;
  make the interval inconclusive.

Item 2's accepted extra-input-copy sector also lies outside `_projectors`' two-component inputs and `DIMS=(2,2)` at
`scripts/qd_classical_benchmark.py:69-78,115-122`. **Verified domain mismatch; inferred consequence:** the certificate
is numerically rigorous but proves a single-copy optimum, so it cannot cover those accepted events. The smallest fix
is the source-mixture benchmark or a rigorous accepted-contamination bound already stated in Item 2.

Checks not run: an SDP over uncertain attempt ratios and a multicopy/source-mixture classical benchmark.

### 5. Decision rule

**Verified:** `hoeffding_radius` at `scripts/qd_teleportation_rehearsal.py:938-942` implements
`sqrt(log(1/alpha)/(2n))`; `bernoulli_decision_count` at `scripts/qd_network_protocol.py:467-476` implements the stated
alpha/beta design count. For alpha `.01`, beta `.10`, F* `.86`, B `.693668048`, and allowance `.02`, the margin is
`.146331952`, raw count `313.3709483253`, and ceiling `314`; alpha and beta radii sum to `.1461853015`. The complete
verdict branches match the design, and absent/silent/zero-count inputs become inconclusive at rehearsal lines
1012-1083. **Verified command:** five focused tests returned `5 passed in 1.39s`.

#### P0: event-level independence, and therefore the advertised alpha and power, is unestablished

- **Location:** `scripts/qd_network_protocol.py:467`, `scripts/qd_teleportation_rehearsal.py:938`, and
  `docs/design/ascella-belenos-entanglement-teleportation.md:226`.
- **Evidence, verified:** Both functions expressly assume independent valid outcomes. The design distinguishes events,
  settings, compilations, jobs, and calibration epochs and warns that many counts inside few configurations provide
  few drift replicates. Job-01 runs one compiled block per input, while analysis at rehearsal lines 1008-1024 treats
  every accepted count as an independent Bernoulli observation.
- **Consequence, inferred:** Source drift, detector memory, or compiled-mesh error can correlate hundreds of events.
  Under perfect correlation, 314 null marginals behave as one draw, so the all-correct event has probability B rather
  than a Hoeffding tail; alpha `.01` and beta `.10` lack established operational meaning.
- **Smallest fix:** Randomize/interleave replicated blocks and analyze independent block/epoch units, or preregister a
  dependence-robust interval with a justified correlation bound. Until then, keep the pooled estimate descriptive and
  force the confirmatory verdict to `inconclusive`.

#### P0: a provider-marked partial result can receive a definitive verdict

- **Location:** `scripts/qd_teleportation_rehearsal.py:967`, `scripts/qd_teleportation_rehearsal.py:1034`, and
  `scripts/qd_platform.py:1663`.
- **Evidence, verified:** Analysis parses `partial`, but the verdict guard omits it. The platform summary defines an
  errored or cancelled job as partial while retaining counted iterations. An offline record with six complete perfect
  iterations and `partial=True` returned `accepted=1800`, no missing or silent inputs, and
  `verdict='beats-classical'`.
- **Consequence, inferred:** Error, cancellation, or max-duration censoring can yield a confirmatory verdict without a
  proof that stopping is outcome-independent.
- **Smallest fix:** Put `partial` in the unconditional `inconclusive` guard; retain partial counts only descriptively.

**Inferred conditional judgment:** unequal accepted counts alone do not invalidate Hoeffding for the realized-weight
average `sum(correct)/sum(accepted)` at rehearsal lines 1012-1015 if bounded outcomes are conditionally independent.
The present six compiled blocks establish neither that condition nor the physical-attempt weights needed by Item 4.
Use deterministic per-input accepted quotas or stratified intervals combined with a benchmark based on measured
attempt denominators.

Checks not run: no retained artifact supplies an event autocorrelation/drift bound, so effective sample size was not
estimated; no replacement interval was implemented.

### 6. Job-00 retained evidence

No new defect was found in retained-record integrity. **Verified commands:**
`"$PYTHON" scripts/qd_teleportation_rehearsal.py --analyze results/quandela/runs/2026-10-26T025336Z-qpu_belenos-teleportation_rehearsal-job-00 --check`
exited 0 with `analysis.json replays, verdict inconclusive`; `"$PYTHON" scripts/qd_rehearsal_secondary.py` on the
same run with `--check` exited 0 with `secondary-analysis.json replays`. Before/after SHA-256 values for analysis,
secondary analysis, results, submission, and submission-state were identical.

**Verified:** `docs/state/research_state.json:11093-11122` matches the job ID and time in `submission.json:15-24,162`,
anchor/live pooled fidelities `0.867910464` and `0.635379388` in `submit-model.json:2-24`, completed duration 292 s,
zero samples, 1,200,000 top-level shots, and 7,200,000 summed `shots_used` in `results.json:1050-1068`. Every input
has zero accepted events and the primary verdict is inconclusive at `analysis.json:128-159`; the secondary result is
`0/5400, degraded-as-recorded` at `secondary-analysis.json:139-145`. All six registry evidence hashes matched
`sha256sum`.

**Verified billing:** the iterated-job rule at `docs/runbooks/quandela-credit-optimization.md:24-31,141-143` is
`1 + 1e-6 * largest iteration max_shots`, used or unused. Each iteration cap is 1,200,000 at
`results.json:183-197,353-367,523-537,693-707,863-877,1033-1047`, hence 2.2 credits. The before/after cumulative
figures at `submission.json:163-186` and `results.json:1071-1094` differ by exactly 2.2 credits and one job. The
7,200,000 case cap is the six-iteration sum, not the billed basis. The repository defines that usage difference as
the charge at runbook lines 34-36; the increasing cumulative field is therefore not a balance.

Checks not run for this item: none required by the goal.

### 7. Job-01 machinery

#### P1: `--check` silently accepts a registered job whose retained case is absent

- **Location:** `scripts/qd_teleportation_rehearsal.py:1126`.
- **Evidence, verified:** The function says it checks every registered job, but lines 1126-1134 `continue` when the
  registered output lacks `cases.json`. An offline in-memory counterexample registered job-01 at its currently absent
  directory and called `check()`; it printed `missing_cases_json=True`, validated job-00, and returned `check_exit=0`.
- **Consequence, inferred:** A change can add the printed `REQUESTS`/`JOBS` registration but omit or misplace the
  retained case and still pass this gate.
- **Smallest fix:** Require `cases.json` for every `JOBS` entry and add a refusal test.

The remaining machinery is sound within offline coverage. **Verified:** commits `2d33736`, `7529352`, and `9ab20e9`
thread cases, derive/refuse duration, and add the brief. `Request` owns name/layout/seeds/anchor and `Job` owns the
request and budgets at rehearsal lines 175-215; build, validation, analysis, variants, simulation, model, plan, body,
binding, submission, and secondary analysis use the explicit request throughout lines 389-552, 732-897, 965-990,
1195-1555 and `scripts/qd_rehearsal_secondary.py:225-249,429-442`. The requested grep found remaining legacy constants
and `job-00` only in job-00 registration/compatible commands/tests, seed data, documentation, and the intentional
record-watch trigger; no registered job-01 path silently fell back to job-00.

**Verified:** `prepare` at rehearsal lines 1489-1538 derives before retaining, refuses inadequate power before a
write, refuses excessive duration before justification, compares a retained derivation on retry, reuses a retained
estimate, stages via a temporary directory, and prints executable rows. Tests at
`tests/scripts/test_qd_teleportation_rehearsal.py:700-770` prove refusal leaves no artifact and resume is byte-stable.
`expected_seconds` at lines 808-817 uses six 10-second compilations plus acquisition, 1.25 margin, and whole-minute
ceiling; the test reproduces job-00's 120 s. Own-anchor detection/refusal occurs at lines 190-193 and 1269-1275 and
precedes provider reads on send.

**Verified command:** the three required test files returned `77 passed in 11.27s`. `git diff --check
origin/main...HEAD` was empty. Pinned Ruff format/check and mypy on the six changed Python/test files returned
`6 files already formatted`, `All checks passed!`, and `Success: no issues found in 6 source files`.

Checks not run: real job-01 `--prepare`, provider reads, body/plan/submit, and real job-01 secondary replay; the own
platform read and case are pending and the review forbids provider commands.

### 8. Preregistration at the case's own read

#### P0: the own-read binding is a provider-record drift guard, not a chip-readiness test

- **Location:** `scripts/qd_teleportation_rehearsal.py:729`, `scripts/qd_teleportation_rehearsal.py:776`,
  `scripts/qd_teleportation_rehearsal.py:1287`, and `docs/design/ascella-belenos-entanglement-teleportation.md:464`.
- **Evidence, verified:** For an own-anchor request, fresh and anchor per-mode variants are identical, so `derive`
  makes the drift allowance zero and total allowance exactly `0.02`. With an unchanged provider record, `model_at`
  reconstructs the same anchor model and compares it to a floored threshold no greater by construction, so binding
  must pass. `docs/notes/quandela/calibration.md:42-52` says the performance object most likely describes the last
  published calibration rather than the chip at read time.
- **Consequence, inferred:** The gate becomes informative only when the published record changes; an unchanged stale
  record can admit a physically drifted chip and consume the full billed cap. The design's statement that binding
  refuses a chip that drifted below F* is stronger than the mechanism.
- **Smallest fix:** Say that binding refuses a *published performance record* whose modeled fidelity is below F*,
  label power/budget conditional on that model and Item 3's unresolved allowance, and include stale-record risk in
  the written case. A chip-drift guard needs an independently approved diagnostic or provider validity evidence.

Own-read preregistration is fixed before outcomes and therefore is not outcome-driven threshold shopping.
**Verified:** the observed verdict at rehearsal lines 1023-1041 compares data to the classical bound, not to F*;
F* controls modeled power and metadata binding. Prepare-to-submit changes in live status/cap/tariff/estimate, body
digest, or modeled fidelity refuse at `scripts/qd_platform.py:1232-1293,1427-1467` and rehearsal lines 1406-1450;
only drift hidden by an unchanged record remains invisible.

**Verified command output:** offline use of the retained job-00 rate model produced bound `.693668048`, allowance
`.02`, minimum share `.079911335371`, clock `4.94 MHz`; F* `.86/.80/.77/.76` respectively required decision counts
`314/901/2115/3126`, samples per input `900/2400/5600/8200`, and rounded durations `120/180/300/420` seconds. The
handoff table at `docs/archive/handoffs/belenos-recovery-watch.md:82-89` is correct under that model.

Raising the cap is unavailable: the Explorer contract limit is 300 s at
`docs/runbooks/quandela-credit-optimization.md:56-65`, enforced by `scripts/qd_platform.py:1261-1267`. A split is
possible but constitutes a different experiment. **Verified arithmetic:** at F*=.76, two contiguous three-input
jobs each round to 240 s; each adds a base credit under runbook lines 24-30 and 74-88. **Inferred:** a valid split
needs frozen allocations, multi-run aggregation, two approvals, and between-job-drift treatment. The current refusal
is sound for the one-job design.

#### P2: the refusal message overstates what failed

- **Location:** `docs/archive/handoffs/belenos-recovery-watch.md:132`.
- **Evidence, verified:** The table proves only that the one-job form exceeds 300 s under the retained rate model.
- **Smallest fix:** Replace “chip has not recovered enough for this case” with “the one-job form does not fit,” and
  state that a split requires a separately reviewed case.

Checks not run: a real job-01 read/prepare/plan/body/submit and any physical drift measurement.

### 9. Seeds

No P0/P1 seed defect was found. **Verified:**
`docs/evidence/outshift_qrng/draw-2026-10-26T204106Z.json:2-20` records six 16-bit values
`8608,30481,4339,55973,12504,37710` plus the raw response hash;
`scripts/qd_teleportation_rehearsal.py:140-144` assigns them in order to job-01; and
`docs/evidence/qrng_seeds/allocations.json:145-185` binds the same symbol, draw, indices, and values. The tests at
`tests/scripts/test_qd_teleportation_rehearsal.py:148-174` verify order, values, and cross-case non-overlap. The new
acquisition uses new meshes, so fresh seeds follow the repository rule.

`CONTROL_SEED=64095` is correctly a reproduction identifier, not fresh job-01 randomness. **Verified:** its ANU draw
and raw hash are at `docs/evidence/anu_qrng/draw-2026-10-26T014202Z.json:2-10`, with allocation at
`allocations.json:201-206`. The design at lines 417-453 freezes one named 999-table exploratory ensemble outside the
verdict. `scripts/qd_rehearsal_secondary.py:302-320,391-443` deterministically builds and records that ensemble and
applies it to the case named by the manifest; tests at lines 111-129 prove byte identity for equal inputs.
**Inferred:** a fresh draw would define a different Monte Carlo instrument rather than reproduce the frozen lens.

#### P2: the QRNG fallback rationale lacks retained failure receipts

- **Location:** `docs/notes/qrng/README.md:12` and
  `docs/design/ascella-belenos-entanglement-teleportation.md:478`.
- **Evidence, verified:** Source order is keyed ANU, keyless ANU, then Cisco Outshift. The design says keyed ANU
  returned success with empty data and keyless ANU timed out, but targeted repository search found only narrative
  statements, not scrubbed response/error receipts. The successful Outshift draw itself is fully retained.
- **Smallest fix:** Label those failures operator-observed and unretained; retain a scrubbed source/time/outcome
  receipt for future fallback events.

**Verified commands:** `anu_qrng.py check docs/evidence/anu_qrng` returned `20 draws admitted`;
`outshift_qrng.py check docs/evidence/outshift_qrng` returned `2 draws admitted`; and
`ci/seed_provenance.py --check` returned `284 seed literals accounted`.

Checks not run: none beyond the forbidden live QRNG reads; initial directory-less check invocations only printed
usage, then the documented directory-bearing commands above passed.

### 10. Submission-day procedure and failure modes

#### P0: free-form `APPROVAL` does not prove owner approval of the written case

- **Location:** `scripts/qd_teleportation_rehearsal.py:1608`, `scripts/qd_platform.py:1417`, and
  `docs/notes/quandela/README.md:335`.
- **Evidence, verified:** Policy requires owner approval of a written case, but the CLI forwards any third argument;
  `qd_platform.submit` checks only `approval.strip()`, records that string, then POSTs. Its offline self-test submits
  with literal text and no approval artifact at platform lines 2302-2352.
- **Consequence, verified:** A token holder can invoke `--submit RUN fabricated-text` and spend credits without
  evidence of the owner's approval.
- **Smallest fix:** Require and consume a single-use owner-approved artifact binding written-case path/hash, case/body
  digest, platform, samples/shots, seconds, credit ceiling, and gate; reject forged, mismatched, or consumed artifacts.

#### P0: the live binding has an unavoidable read-before-POST race

- **Location:** `scripts/qd_teleportation_rehearsal.py:1406` and `scripts/qd_platform.py:1443`.
- **Evidence, verified:** Submit replans and binding performs the final authenticated performance GET, but platform
  submission then reads usage, writes/fsyncs body and state files, and POSTs at lines 1444-1467. No provider atomic
  calibration-version precondition binds that GET to execution.
- **Consequence, inferred:** A published-record change after the final GET or before queued execution is unseen and can
  spend credits outside the admitted record state.
- **Smallest fix:** Document the residual race and the read-time-only guarantee. If the provider exposes a
  calibration/version precondition accepted by POST, bind it; another GET merely narrows the race.

The six steps otherwise have explicit failure handling. **Verified:** (1) the main-only workflow at
`.github/workflows/quandela-record-watch.yml:18-164` materializes a mode-600 temporary token, performs GET-only watch
classification, removes the token on success, and never submits; the assistant path reads no credential. (2)
Snapshot/prepare derives the case and refuses absent read, inadequate power, `estimate=None`, or duration above 300 s
at rehearsal lines 855-883 and 1489-1539; an estimate failure may retain only `noise-model.json` and resumes. (3)
Build/check refuses a retained layout inconsistent with the registered request at lines 1126-1172; a changed live
optimum does not silently relayout the frozen mesh. (4) Plan refuses status/duration/cost/occupancy/estimate problems
at `scripts/qd_platform.py:1232-1315`, retains `sent:false` refusal, replans on submit, and binding rejects body-digest
drift. (5) The written case must state rationale, backend, samples, shot/time/credit ceilings, but the P0 above leaves
approval unbound. (6) The checkpoint prevents reuse; an actual cutoff can consume the full largest-iteration ceiling
under `docs/runbooks/quandela-credit-optimization.md:24-31,141-143`; collection preserves error/cancelled/partial bytes.
Missing or silent inputs become inconclusive, while Item 5 documents the defect when `partial=True` still has counts
for all inputs.

Credential answer, **verified:** provider operations read `QUANDELA_TOKEN_FILE` inside
`scripts/qd_platform.py:230-301`; snapshot/body/plan/submit/collect therefore read a credential when an authorized
operator runs them. The watcher reads one only inside the protected GitHub environment and performs GETs. The human
assistant procedure reads none. The watcher has no submission path; manual submission has the free-form-approval path
above.

**Verified command:** `"$PYTHON" scripts/qd_record_watch.py --self-test` returned
`qd_record_watch self-test: held, changed, unscorable and missing records classify; the model runs only on a change`.

### Checks not run

- Live record-watch `check`, job-01 snapshot/prepare/body/plan/submit/collect, provider/MCP/network calls, credential
  reads, and `gh`: prohibited by the review brief.
- A real job-01 secondary replay: the own-read case does not yet exist.
- Three-photon Gram-matrix and worst-case compilation optimization: no registered parameterization/bound exists.
- A hardware-backed dark-window calculation and event autocorrelation/effective-sample estimate: retained records lack
  the timing and drift information.
- An optical-attempt uncertainty-set or multicopy/source-mixture classical SDP, and a dependence-robust replacement
  interval: absent from the current implementation.

## Disposition

Each finding was checked against the cited source before it changed anything. "Fixed" names the commit content of
#560; "open" waits on the owner's decision before job-01's written case, and the design's "Review of 2026-10-26"
paragraph carries it.

| finding | severity | disposition |
|---|---|---|
| verdict overstates C1 conformance | P0 | open. The design now states the narrower claim the verdict supports; preregistered acceptance and rejection-mix tolerances, or the narrow claim, are the owner's choice |
| threshold-accepted multiphoton sectors leave the single-copy benchmark | P0 | open. Confirmed in kind: `detected_clicks` thresholds every occupation and `classify` sees only clicks. A source-mixture bound or a registered contamination bound is new derivation work |
| CNOT-success test name claims the multiphoton domain | P2 | fixed: renamed `test_every_ideal_three_photon_accepted_pattern_implies_the_cnot_success_branch` |
| F* is a forecast, not a lower bound over the omissions | P0 | narrowed. F* sizes the budget and never enters the verdict, which compares `F_hat - r - 0.02` with B, so its inaccuracy costs power, not validity. The design names it a power forecast. The 0.02 allowance stays a stated, underived term (open) |
| modeled attempts do not upper-bound the unknown attempt profile | P0 | open. Confirmed: the service reports shots equal to samples and no optical attempts (Perceval #798 asks for count provenance) |
| the maximum candidate bound is anti-conservative for the negative verdict | P0 | fixed: `at-or-below-classical` now compares with the smaller candidate bound; `test_the_negative_verdict_falls_below_the_smaller_candidate_bound` reproduces the reviewer's 0.67 case as `inconclusive` |
| event-level independence unestablished | P0 | open. Confirmed: one compiled block per input, and the radius treats every accepted event as independent. Interleaved replicate blocks or a dependence-robust interval are a design change |
| a partial result can receive a definitive verdict | P0 | fixed: `partial` joins the `inconclusive` guard; `test_a_partial_job_with_every_input_counted_stays_inconclusive` |
| `--check` skips a registered job without its case | P1 | fixed: `check` refuses it; `test_check_refuses_a_registered_job_without_its_case` |
| own-read binding guards the published record, not the chip | P0 | fixed in the text: the design says `binding` refuses a changed published record, and an unchanged stale record passes by construction; the written case names that risk |
| handoff refusal message overstates the failure | P2 | fixed: a refusal means the one-job form does not fit; a split needs its own reviewed case |
| QRNG fallback lacks failure receipts | P2 | fixed in the text: the design labels both ANU failures operator-observed and unretained |
| free-form `APPROVAL` does not prove owner approval | P0 | open, repository-wide. `qd_platform.submit` records the approval text and binds the frozen body and the live model; an approval artifact the operator writes is no harder to forge than the text, so the control is the owner's written approval in the conversation the case quotes. Whether to bind a signed artifact is the owner's decision |
| read-before-POST race | P0 | documented: the design states that the gate holds at read time only; no provider precondition binds the read to execution |

Job-00's retained bytes and verdict replay unchanged after the fixes (`--check`, `--analyze RUN --check`,
`qd_rehearsal_secondary.py RUN --check`).
