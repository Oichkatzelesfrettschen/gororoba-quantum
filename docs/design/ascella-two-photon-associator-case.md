# Ascella two-photon octonion-associator case

This is the written case for one qpu:ascella job. The job shows that the octonions are not associative, and it
shows it only through two-photon interference. The mathematics and ideal laws come from
[persona-corpus-verified-results.md](../notes/topics/persona-corpus-verified-results.md#ascella-the-octonion-associator-in-two-photon-interference).
[scripts/ascella_associator_case.py](../../scripts/ascella_associator_case.py) builds the frozen request in
[results/quandela/cases/ascella_two_photon_associator/job-00](../../results/quandela/cases/ascella_two_photon_associator/job-00/cases.json),
checks it, and analyses the collected run. Nothing has been sent. The job waits for the owner's approval of this
case.

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

`cases.json` sha256 `4e402cdab702530f4654d272defb88b749fde0a6d24c56d979a0561e4b17ec10`; `circuit.json` sha256
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

**Model.** Under the two-photon mixture of visibility V, Delta_pred = 2V/(V + 1.5(1 - V)). V is the HOM fraction
the plan records at submission. The model ignores g2 and dark counts; their measured shares are reported.
[E] Delta_pred is 1.65 at V = 0.875 and 2 at V = 1, and Delta_control = 0 at every V.

**Decisions.**

1. **Associator realised:** Delta exceeds 5 standard errors and Delta_control lies within 0.05 of 0, or within
   3 standard errors if that is wider. Otherwise the run does not show it.
2. **Calibration sufficient:** |Delta - Delta_pred(V_HOM)| <= 0.05, or 3 standard errors if wider. A larger
   departure means Ascella's published HOM figure does not predict the compiled two-photon law. Mesh phase error
   and mode-dependent distinguishability are the named alternatives.
3. **Descriptive only:** the per-pair laws and the excluded share. These carry no decision.

With 4096 eligible events per route, the standard error of Delta is about 0.013 at V = 0.875. Both decisions are
then resolved well inside their tolerances.

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

**HOM rule: the owner's decision.**
- Strategy design rule 1 ([strategy.md](../notes/quandela/strategy.md)) holds two-photon cases until the live HOM
  exceeds `HOM_FLOOR` (90 %). The last Ascella read was 87.28 % ([preflight of 2026-10-24](../evidence/ascella-order-coefficients/case-preflight/preflight.json)),
  so `plan` will print the HOM warning.
- Unlike the Belenos block whose leak prompted the rule, this endpoint models V explicitly. A lower V lowers
  Delta_pred (1.65 at 0.875) but leaves both decisions valid.
- Recommendation: submit at the live V and record it, rather than wait for 90 %. If the owner prefers the rule as
  written, the case waits for a plan that reads above 90 % and is otherwise unchanged.

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

A run directory whose plan refuses leaves the tree before anything is committed. Every directory under
`results/quandela/runs/` reads as a sent job.

After collection, the retained run enters `docs/state/research_state.json`, the strategy run log and plan
`ascella-two-photon-associator-case` in the change that retains it.
