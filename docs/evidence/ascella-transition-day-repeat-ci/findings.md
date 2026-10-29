# Ascella day-separated matched-mesh repeat: findings

One `qpu:ascella` job (`078ecca0-fb08-4cf1-960f-6c12301a19da`) ran the five settings of the
forward-packed context job again, with the same operators, parameters and compilation identifiers. It
started at 2026-10-29T10:00:49Z, **33.38 hours** after the baseline started
(2026-10-28T00:38:05Z). It ran for 16 provider seconds, returned 65,536 accepted events per setting
(327,680 in total) and was charged 1.131072 credits, its ceiling. The
[analysis](../../../results/quandela/runs/2026-10-29T093948Z-qpu_ascella-transition-matched-mesh-day-repeat/day-repeat-analysis.json)
and the [inventory](acquisition-inventory.json) bind the raw result, the request and the baseline sources.
For all five settings, the returned `computed_circuit` and `computed_input` serializations match the
baseline's, so the comparison is between matched meshes.

## Campaign lineage

The run is the fifth acquisition stage of the dimension-six transition program on Ascella. Each stage
was frozen before its own submission.

1. **[Cancellation and dimension-six pilot](../ascella-cancellation-transition-acquisition/findings.md).**
   The five cancellation settings passed. The twelve-setting pilot failed: identity inputs 2 and 5
   leaked 6.21 % and 4.85 %, and four Fourier-to-chirped inputs failed the 0.05 bound on total
   variation from the returned-mesh distribution. The 54-setting campaign therefore stays ineligible.
2. **[Context diagnostics](../ascella-transition-context-diagnostics/findings.md).** Seven jobs on
   five selected settings (singleton, forward-packed and reverse-packed). Leakage moved between
   contexts on matched meshes: identity input 5 measured 0.14 %, 1.94 % and 6.35 % in the three
   contexts.
3. **[Mesh and output-port diagnostics](../ascella-transition-mesh-port-diagnostics/findings.md).**
   Six jobs, eight new meshes per setting and output map, and twelve matched anchors. Matched
   identity-input-0 anchors differed from their singleton reference.
4. **This repeat.** The user requested it on 2026-10-27 ("repeat selected matched meshes tomorrow
   to measure drift"). The hosted scheduler held the job at its `latest_start` without sending it,
   and its [admission amendment](scheduler-admission.md) re-admitted it under the preregistered
   24-hour separation.

The same day, another workflow sent job `e13e5ed0` (the
[associator predecessor campaign](../ascella-associator-predecessor/README.md)) to the same
processor. It started at 08:31:14Z and ran for 104 s, ending about 87 minutes before this repeat. Its
fitted predecessor-carryover terms are inconclusive. Nothing in either record establishes whether one
job conditioned the other.

## Results

Leakage is the fraction of accepted events outside the setting's active logical ports, invalid
photon-number categories included. The intervals are 95 % simultaneous over the frozen
140-endpoint family, assuming IID accepted events within each setting.

| Setting | Baseline leakage | Repeat leakage | Leakage difference | Observed TV | TV interval |
|---|---:|---:|---|---:|---|
| identity input 2 | 0.229 % | 0.534 % | [+0.14 %, +0.48 %] | 0.0051 | [0.0012, 0.0109] |
| identity input 5 | 1.941 % | 0.208 % | [-1.99 %, -1.48 %] | 0.0186 | [0.0137, 0.0251] |
| Fourier-to-chirped input 4 | 0.198 % | 6.410 % | [+5.81 %, +6.62 %] | 0.0621 | [0.0287, 0.0976] |
| identity input 0 | 0.233 % | 0.150 % | [-0.21 %, +0.04 %] | 0.0009 | [0, 0.0043] |
| Fourier-to-chirped input 0 | 3.214 % | 0.655 % | [-2.92 %, -2.20 %] | 0.0267 | [0.0091, 0.0619] |

Four of five total-variation intervals exclude zero. Identity input 0 is consistent with no change.
The largest excess-leakage setting changed from job to job:
- In the baseline, Fourier-to-chirped input 0 (3.21 %) and identity input 5 (1.94 %) were high.
- In the repeat, both fell below 0.7 %, and Fourier-to-chirped input 4 rose to 6.41 %.

Fourier-to-chirped input 4 leaked 6.17 % in the original pilot, a value close to its 6.41 % here.
With one baseline and one repeat, the record shows two endpoints and no path between them.

## Interpretation

**Observed.**
- Matched digital meshes produce output distributions that differ between jobs 33 hours apart.
- The change concentrates in excess leakage of a few percent, which appears in a different subset
  of settings in each job.
- Earlier jobs on the same meshes, hours apart within one day, show changes of the same size:
  - identity input 5 moved from 0.14 % to 6.35 % between the singleton and reverse contexts;
  - matched identity-input-0 anchors differed from their singleton reference by total variation
    0.012 to 0.046.

**Hypotheses.** The record is consistent with two explanations, and its design cannot separate them.

- *Intermittent per-setting state.* A few-percent excess-leakage state switches on and off between
  jobs. Identical meshes enter and leave it in both directions, and Fourier-to-chirped input 4
  reaches about 6 % in two separate jobs.
- *Slow drift with calibration and context.* The applied controls or the source and detector
  response drift over hours to days, and recalibrations and job context move each setting
  differently.

Opposite leakage shifts across settings and comparable same-day changes fit both. A fixed-context
replicate of several jobs minutes apart tests the first. Large changes between those replicates
favor intermittency, and their absence leaves drift as the remaining account. A time series of
repeats at several separations tests the second through a dependence on elapsed time. Drift
therefore stays unresolved. The acquisition cannot identify the mechanism either way: applied analog
controls, source or detector response, or calibration events. Returned serialization records the
digital request only.

**What it does not establish.**
- A drift rate: one separation gives no slope, and the job-to-job variance at short separation is
  unmeasured.
- Qualification of the 54-setting campaign, which still needs a fresh, prospectively specified
  cohort.
- Any statement about incident-pulse loss, physical iteration order inside the packed job, or a
  bound on mutually unbiased bases.

## Follow-up acquisition

The day-separated comparison is complete, and no further scheduled run is needed to finish it. The
open question is whether 33-hour differences exceed same-day job-to-job variation. That needs its own
written case and the user's approval before any schedule is armed. A proposed form:
- three back-to-back forward-packed jobs, minutes apart, on the same five matched meshes;
- each job at the same 1.131072-credit ceiling, 3.39 credits in total;
- every job compared pairwise under the same 140-endpoint construction.

The between-replicate spread is the null against which this repeat's differences are judged. A
second day-separated repeat after that replicate turns the single separation into a series.
