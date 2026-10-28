# Ascella two-photon octonion-associator case

This is the written case for one qpu:ascella job. The job shows that the octonions are not associative, and it
shows it only through two-photon interference. The mathematics and ideal laws come from
[persona-corpus-verified-results.md](../notes/topics/persona-corpus-verified-results.md#ascella-the-octonion-associator-in-two-photon-interference).
[scripts/ascella_associator_case.py](../../scripts/ascella_associator_case.py) builds the frozen request in
[results/quandela/cases/ascella_two_photon_associator/job-00](../../results/quandela/cases/ascella_two_photon_associator/job-00/cases.json),
checks it, and analyses the collected run.

**Approval.** On 2026-10-28 the owner approved the case to run at the live HOM rather than wait for the 90 % floor,
and asked whether the low visibility needs a changed run, a calibration or a compensation. The section
[HOM below the floor](#hom-below-the-floor) answers that before any data exists. The job stays the same, and the
second decision is re-registered as an in-job visibility closure. Nothing has been sent.

## Mathematics

- The cd_core octonions are a normed algebra, so the left multiplication L_v by a unit octonion v is an orthogonal
  8 x 8 matrix.
- The map v -> L_v is not a homomorphism: L_a L_b x = a(bx) while L_(ab) x = (ab)x. The two differ by the
  associator.
- With a = (e6 + e7)/sqrt2 and b = (e5 + e7)/sqrt2, ab = (-e0 - e1 - e2 + e3)/2. Both L_a L_b and L_(ab) keep
  span(e0..e3), so each route is a 4 x 4 real orthogonal block.
- Two indistinguishable photons entering algebra modes 2 and 3 leave on two-click pairs given by two-photon
  permanents:
  - after L_a L_b, pairs {0,3} and {1,2}, 1/4 each;
  - after L_(ab), pairs {0,2} and {1,3}, 1/4 each;
  - the rest bunches, and threshold detectors read a bunch as one click.
- Distinguishable photons give the same law after both routes: each of the six pairs 1/8, plus bunching. So the
  associator is visible only through two-photon interference.
- The control takes a = (e1 + e2)/sqrt2 and b = (e1 + e3)/sqrt2. Both lie in the quaternions, which are
  associative, so L_a L_b = L_(ab) and the routes cannot differ.

## Request

`cases.json` sha256 `88ca9404e085a0f276c97bc65cd2047fa4ce60c0c022b27bc1e88d5371bc6ec0`; `circuit.json` sha256
`6fbd0669df30b6e66862212ff21978438557945bdc577ee3fd59730e684f221f`.

**Mode map.** Algebra modes 2, 0, 3, 1 sit on logical modes 0, 1, 2, 3. The two photons therefore enter logical
modes 0 and 2, which are connected source modes of qpu:ascella. In logical labels:
- the L_a L_b pairs are P+ = {03, 12};
- the L_(ab) pairs, and both control routes, are P- = {01, 23}.

**Circuit.** Every iteration binds the fixed four-mode Rx/phase template on modes 0..3 and the identity on modes
4..11. The twelve-entry input holds photons on modes 0 and 2. The job keeps `min_detected_photons` 2 and the
explicit empty mitigation list, and returns all twelve modes.

**Iterations.** Eight: the associator block, then the control block, each in the route order LaLb, Lab, Lab, LaLb.
Budgets are 2048 samples and 262144 shots per iteration (aggregate caps 16384 and 2097152), with `max_duration`
300 s.

**Eligibility.** A sample counts when exactly two modes click and both lie in modes 0..3. Every other sample is
tallied as excluded and reported.

## Endpoints and decisions (preregistered)

**Endpoint.** Per route, D = (n(P+) - n(P-))/n, where n counts eligible two-click events. Its standard error is
sqrt((q - D^2)/n), with q the share of events on P+ or P-. Then:
- Delta = D(LaLb) - D(Lab) on the associator block;
- Delta_control is the same on the control block.

**Model.** Two photons whose internal states overlap with M = Tr(rho_1 rho_2) give the exact mixture
M P_indistinguishable + (1 - M) P_distinguishable. Every route then reads D = +-f(M), with f(M) = M/(M + 1.5(1 - M)).
Specifically:
- L_a L_b on the associator block reads +f, and L_(ab) reads -f;
- both control routes read -f.

[E] Delta = 2f(M) is 1.65 at M = 0.875 and 2 at M = 1; Delta_control = 0 at every M.

**Decisions.**

1. **Associator realised:** Delta exceeds 5 standard errors and Delta_control lies within 0.05 of 0, or within
   3 standard errors if that is wider. Otherwise the run does not show it.
2. **Visibility closure:** C = Delta + 2 mean(D_control) lies within 0.05 of 0, or within 3 standard errors if
   that is wider. C vanishes at every photon overlap, because both blocks carry the same factor f(M); the decision
   needs no HOM figure. A departure means an error that depends on the route or the mesh: mesh phase error,
   mode-dependent loss, or distinguishability that differs between input pairs.
3. **Descriptive only:**
   - the compensated contrast Delta/(-2 mean D_control), which is 1 at every M;
   - the in-situ overlap M_eff = 1.5f/(1 + 0.5f) with f = -mean D_control;
   - the comparison |Delta - Delta_pred(V_HOM)| against the HOM read, with its earlier 0.05 tolerance;
   - the per-pair laws and the excluded share.

   These carry no decision.

Both decisions need all four ABBA iterations of both blocks; a truncated block leaves them undecided and keeps its
estimates as descriptive output. With 4096 eligible events per route, the standard error of Delta is about 0.011
and that of C about 0.016 at M = 0.875.

## HOM below the floor

The owner asked whether HOM below 90 % needs a changed run, and whether the job can be calibrated and compensated.
[E] figures come from `ascella_associator_case.py` and `persona_corpus_checks.py`.

**Decision 1 does not depend on the HOM.**
- Distinguishability only scales the contrast: Delta = 2f(M) is 1.64 at M = 0.873, 1.22 at 0.70 and 0.80 at 0.50.
- Even at 0.50 that is about 45 standard errors (145 at M = 0.875).
- The control's route difference is 0 at every M.
- No budget change is needed. At lower M, two-click events take a larger share of samples (0.53 at M = 0.875,
  0.60 at 0.60), so the counts grow rather than shrink.

**The old decision 2 depended on the HOM figure in ways the device does not control.** [E] dDelta/dV is 2.66 at
V = 0.875. Three effects consume the 0.05 tolerance without any device error:

1. **Calibration drift.** The two retained Ascella HOM reads, 87.28 % and 88.8 %, move Delta_pred by 0.041.
2. **g2 offset.** HOM visibility is not the photon overlap M: multiphoton emission (g2 1.9 % at the last read)
   lowers the visibility below M. [U] The relation is M ~ (V_HOM + g2)/(1 - g2) to first order (Ollivier et al.,
   PRL 126, 063602, 2021, not retained here). That correction is near 0.04 in V, or 0.1 in Delta.
3. **Different objects.** The HOM figure is measured on Quandela's own two-photon test, not on this compiled mesh,
   which is the same reason strategy rule 1 records ("the HOM figure measures the source's indistinguishability,
   not the mesh").

A run could therefore have failed decision 2 on a perfect mesh.

**Calibration is already inside the job.** The control block runs the same source, the same input pair and the
same detectors through a mesh whose two routes are identical. Its D is -f(M), so it measures the photon overlap in
situ, during the job, on the input pair that matters. Re-registering decision 2 as the closure
C = Delta + 2 mean D_control = 0 removes M from the test exactly:
- [E] C = 0 at M = 1, 0.888, 0.875, 0.80, 0.70, 0.576 and 0.50.
- [E] Synthetic counts at M = 0.6 pass the closure and recover M_eff = 0.600.
- [E] A control route replaced by the associator law fails it.

The ABBA order already brackets drift within each block.

**Compensation.** The compensated contrast Delta/(-2 mean D_control) equals 1 for every M under the mixture, so it
reports how much of the associator survives the mesh, with the source's distinguishability divided out.

**What cannot be compensated.**
- The cloud exposes no control of the source's spectral filter, delay or pulse settings, so the overlap itself
  cannot be raised from the request. The job measures it instead.
- Multiphoton events (g2) that lose a photon can enter as two-click events. They are not route-symmetric in
  general and are not removed by the closure.
- At g2 1.9 % and Ascella's few-percent transmittance, their share of two-click events is small, but it is
  unmeasured. The excluded three-click share, which `--analyze` reports, bounds their source.

**What changed.** Only the analysis and the preregistered block of `cases.json`, before any data exists. The circuit,
the eight iterations, the budgets, the credit ceiling and the procedure are unchanged.

## Written acquisition case

**What it measures.** Whether the qpu:ascella source and a compiled 4-mode mesh realise the two-photon law that
separates L_a L_b from L_(ab). Under a perfect source that law is fixed by the octonion associator, and under a
distinguishable source it vanishes. Both are measured against a quaternion control that must show no difference.

**Why simulation cannot answer it.** Local SLOS returns the ideal law, which the `--check` confirms to 1e-9 on the
Perceval unitary of every iteration. The question is the device:
- how much of the ideal Delta the actual photon pair's indistinguishability carries;
- whether the HOM figure in `perfs_at_plan` predicts that share for a compiled mesh rather than a single beam
  splitter;
- whether the mesh's phase errors, the residual of plans ascella-perturbed-compilation-case and
  ascella-heater-coupling-families, move two-photon laws as they move one-photon ones.

No retained Ascella job has sent two photons. Every retained qpu:ascella run used one photon and
`min_detected_photons` 1.

**Platform.** qpu:ascella: 12 modes, at most 6 photons, connected source modes 0, 2, 4, 6, 8 and 10, threshold
detectors and a 300 s `max_duration` ([quandela/README.md](../notes/quandela/README.md)). The fresh plan re-reads
all of this.

**Credits.** The ceiling is 1.262144 credits: the 1.0 per-job price plus 262144 billed shots at 1e-6. The service
bills the largest iteration's shot cap ([billing runbook](../runbooks/quandela-credit-optimization.md)). The
expected charge is the same or less. The monthly free grant is 200 credits, reset on the first of the month (UTC).

**Seconds.** The expected value is unmeasured; the bound passed to `plan` is 280 s against the 300 s
`max_duration`.
- One-photon Ascella iterations of 32768 samples took about 3 s each (job-04: 80 iterations in 243 s).
- A two-click sample needs both photons transmitted and detected. Belenos's two-photon pair job needed 69 shots per
  sample (347113 shots for 5000 samples).
- At up to 128 shots per sample and Ascella's one-photon rate, each iteration is a few seconds. If the source rate is
  far lower than that, the service stops at `max_duration`. The ABBA order then keeps every completed block
  balanced, and a truncated control block leaves decision 1 undecided rather than wrong.
- Perceval's `estimate_required_shots` at the plan gives the first two-photon timing point. The measured duration
  sizes any repeat.

**HOM rule: decided.**
- Strategy design rule 1 ([strategy.md](../notes/quandela/strategy.md)) holds two-photon cases until the live HOM
  exceeds `HOM_FLOOR` (90 %). The last Ascella read was 87.28 % ([preflight of 2026-10-24](../evidence/ascella-order-coefficients/case-preflight/preflight.json)),
  so `plan` will print the HOM warning.
- The owner approved submission at the live HOM on 2026-10-28.
- The closure above makes both decisions independent of the HOM figure. The warning is recorded, and the plan
  proceeds.

**Dark counts and multiphoton noise.**
- Detectors 8 to 11 carried most dark counts at the last read (9,908 of 12,159 per second). A dark count on modes
  4..11 makes a sample ineligible rather than mislabelled.
- A dark count inside modes 0..3 can move an event between P+ and P-. Its share is bounded by the excluded share
  times 4/8 and is reported.
- g2 (1.9 % at the last read) adds events with extra photons. Under `min_detected_photons` 2 these mostly show
  three clicks and are excluded.

**Untested path.** No Ascella job has carried two photons, a twelve-entry input with two 1s, or
`min_detected_photons` 2. An error is a live outcome, and on the retained evidence an errored job has cost nothing.

**Stopping rule.**
- A terminal error with no counted iteration allows one resubmission of the identical body under the same approval,
  from a fresh run directory, after `plan` passes again.
- A second error stops the case.
- A job that returned counts is never resubmitted under this approval.

**Procedure after approval.** Copy the request, plan, submit, collect and analyse:

```sh
export PYTHON="${PYTHON:-python3}"
export GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096
export QUANDELA_TOKEN_FILE="$HOME/.config/quandela/cloud-token"
RUN=results/quandela/runs/$(date -u +%Y-%m-%dT%H%M%SZ)-qpu_ascella-ascella_two_photon_associator-job-00
mkdir -p "$RUN"
cp results/quandela/cases/ascella_two_photon_associator/job-00/cases.json \
   results/quandela/cases/ascella_two_photon_associator/job-00/circuit.json "$RUN"/
CASE="--platform qpu:ascella --max-credits 1.262144 --expected-seconds 280 --per-job-credits 1.0"
"$PYTHON" scripts/qd_platform.py plan "$RUN" $CASE
"$PYTHON" scripts/qd_platform.py submit "$RUN" $CASE --approval "APPROVAL TEXT"
"$PYTHON" scripts/qd_platform.py collect "$RUN" --timeout 3600
"$PYTHON" scripts/ascella_associator_case.py --analyze "$RUN"
```

Before the submit, the plan must show:
- qpu:ascella available, with 0 running and 0 queued jobs on the token;
- the price per shot unchanged;
- source modes 0 and 2 connected;
- the live HOM, g2 and per-detector dark counts, which enter the analysis record.
- Perceval's `estimate_required_shots` for the 16384 samples within the 2097152-shot cap; `plan` refuses
  otherwise, and the case then needs a revised budget and a new approval.

`--analyze` writes both decisions, the closure, the compensated contrast and the in-situ overlap to `analysis.json`.
It also writes the descriptive HOM comparison, using the HOM figure that `submission.json` recorded at plan time
(`perfs_at_plan`). A decision whose inputs are missing reads `undecided`.

**Where to run it.** The submitting host needs the Quandela token file (`QUANDELA_TOKEN_FILE`) and network access to
`api.cloud.quandela.com`. The cloud session that prepared this case has neither, so the procedure runs on the build
host.

A run directory whose plan refuses leaves the tree before anything is committed. Every directory under
`results/quandela/runs/` reads as a sent job.

After collection, the retained run enters `docs/state/research_state.json`, the strategy run log and plan
`ascella-two-photon-associator-case` in the change that retains it.
