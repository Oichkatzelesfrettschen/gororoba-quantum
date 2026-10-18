# Belenos first-load hypothesis — Ferreton's notes on the 29dc6ef8 mesh-load finding (beamed to the Claude session 2026-10-18)

Beamed from the Ferreton session, 2026-10-18 ~15:10 PDT. Read-only analysis —
no jobs submitted, no branches touched from my side. For the Claude session
driving the Belenos campaign: take what's useful, discard the rest.

## What I'm reading in the screenshots

- Job-14 (singleton) and job-16's first two entries failed on mesh 29dc6ef8
  (TVD 0.819 / 0.814 / 0.823) when the job OPENED on that mesh.
- After one load of 14a96ca6, all 11 later 29dc6ef8 entries passed — and all
  11 14a96ca6 entries passed.
- Named shift axis: **mesh-load history within the job** — whether the service
  has loaded a mesh's configuration since the job opened on 29dc6ef8.
- The failing state is a fixed point (same wrong config each time: TVD 0.042
  between the two job-16 failures), not drift. Nearest served-mesh ideal is
  e3f757ed at 0.20 — a characterization mesh.
- Anomaly: D1/D2 also opened on 29dc6ef8 and PASSED at 1600 samples. Opening
  sample budget may be a second axis.
- Designed, unrun experiment (needs Eric's approval): open on 29dc6ef8 @1600
  samples, then 10000 on the same mesh, plus a mesh-switch block as positive
  control.

## Idea 1: The bridge result may collapse into first-mesh-loaded

PR #257's verdict was "form or dwell." The mesh-load axis is sharper: what if
the bridge job's iterated form simply never OPENED on 29dc6ef8, while Q1
(one-circuit, 10,000 samples) opened on it directly? Check the receipts: what
was the first mesh loaded in the bridge job (c2eea262)? If it wasn't 29dc6ef8,
"form-or-dwell" reduces to "first-mesh-loaded" — one axis instead of two
hypotheses. No new job needed.

## Idea 2: The e3f757ed lead is a smoking gun worth chasing

Failing histogram's nearest served-mesh ideal is a characterization mesh
(TVD 0.20). Hypothesis: the service serves a stale characterization config on
first load. Concrete step: fit the failing histograms against ALL served-mesh
ideals, not just e3f757ed — best match wins. If the best match is consistently
a characterization mesh, that's the Quandela bug report, nearly write-ready.
Also check timing: does the service run characterization meshes between user
jobs? A timing correlation would corroborate.

## Idea 3: D1/D2 — enumerate the differences BEFORE the experiment runs

D1/D2 opened on 29dc6ef8 @1600 and passed; job-14/16 opened @10000 and failed.
The designed experiment tests sample budget as the second axis — but first,
pull every differing covariate from existing data: timestamp, service
version/deploy marker, queue, job form, entry position, time of day. If D1/D2
ran before a deploy and 14/16 after, it's a regression, not a budget effect,
and the experiment would "confirm" the wrong axis. The contingency table
(first-mesh x sample-budget x pass/fail) over ALL campaign jobs is the free
version of this experiment. Run it before spending the job.

## Idea 4: Two cheap additions to the designed experiment

The current design (open 29dc6ef8@1600 -> 10000 same mesh -> mesh-switch
positive control) is clean. Consider:
- (a) A companion job that opens on a DIFFERENT mesh, then runs 29dc6ef8@10000.
  If it passes, "first-load" is confirmed as the specific trigger — not
  "29dc6ef8 is cursed."
- (b) A middle sample budget (e.g. 5000) on the open: is the budget axis binary
  or graded? Two points find a difference; three points find a threshold.

## Idea 5: The workaround and the bug report

- Workaround for all future campaigns: open every job on a sacrificial mesh
  (or prepend a mesh-switch block) until Quandela fixes the first-load path.
  One line in the strategy doc.
- Bug report: the contingency table + the fixed-point evidence (TVD 0.042
  between failures — same wrong config, not drift) + the characterization-mesh
  best-match = a report Quandela can act on. That's a contribution, not just
  a workaround.

## Compute before any new job (all free, all from existing data)

1. First-mesh-loaded -> pass/fail contingency table over every campaign job.
2. Failing histograms vs all served-mesh ideals (best-match config ID).
3. D1/D2 vs job-14/16 full covariate diff (timestamp, version, form, queue).
4. Bridge job (c2eea262) first-loaded mesh — the form-or-dwell collapse check.

## Resolution against the retained runs

The table and the scores come from `docs/evidence/quandela/belenos_light_cone.json`
(gate core-546). Submission times and receipt covariates come from each run's
`submission.json`. The stale-load sweep comes from the strategy note's
conjecture table, and Idea 2 states its limits. No job ran. Two facts in
the notes above need correcting: D1 and D2 opened at 1500 samples, not 1600,
and the bridge job c2eea262 is belenos_mesh job-09.

**Contingency table, every qpu:belenos job holding Q1's case.** A job's
opening entry is its first returned entry. Under the series rule, a TVD of at
most 0.20 passes and at least 0.50 fails.

| job (id) | submitted UTC | opening mesh, samples, form | first 29dc6ef8 entry | 29dc6ef8 entries after it |
|---|---|---|---|---|
| single/job-04 (7419efb8) | 10-17 21:37 | 29dc6ef8, 10000, single | fail 0.870 | none |
| single/job-04 (7af74302) | 10-18 02:55 | 29dc6ef8, 10000, single | fail 0.857 | none |
| job-08 (8d28f121) | 04:24 | e296b6a9, 10000, single | absent | none |
| job-09 (c2eea262) | 07:45 | 54aef849, 1500, iterated | pass 0.064 (entry 20) | none |
| job-10, D1 (aa4218f1) | 09:03 | 29dc6ef8, 1500, single | pass 0.137 | none |
| job-11, D3 (a5f0a8a4) | 09:04 | 14a96ca6, 10000, single | absent | none |
| job-12, D2 and D4 (c1eb1cbb) | 09:05 | 29dc6ef8, 1500, iterated | pass 0.060 | 5 of 5 pass at 10000, 1500, 40000, 1500 and 60000 (0.058 to 0.083) |
| job-13 (c0db42f6) | 15:53 | 29dc6ef8, 10000, single | fail 0.829 | none |
| job-14 (3d95587b) | 19:05 | 29dc6ef8, 10000, iterated | fail 0.823 | none |
| job-16 (46b810ae) | 19:36 | 29dc6ef8, 10000, iterated | fail 0.819 | entry 1 fails 0.814; 11 of 11 after a 14a96ca6 load pass |

The rule that fits all ten jobs: a job that opens on 29dc6ef8 with a
10000-sample entry fails, and in job-16 the failure held through a second
10000-sample entry until another mesh loaded. A job that opens on 29dc6ef8
with a 1500-sample entry passes, and in D2 the 10000-sample entry right after
it also passed. D2's later 40000 and 60000-sample passes each follow a fresh
1500-sample entry, so they fit a refresh by each 1500 entry just as well as
persistence from the opening, and they decide nothing about persistence.
Every job that opens on another mesh passes, at 1500 or 10000 samples. Among
the seven jobs that opened on 29dc6ef8, five opened at 10000 and failed and
two opened at 1500 and passed. Fisher's exact one-sided value is
1/C(7,2) = 0.048, but it is descriptive only: the rule was chosen after
seeing these same jobs, so the value is not a calibrated test. Significance
needs runs reserved in advance. Uncertainty is medium. The single-to-iterated replication
(D1 single, D2 iterated) raises confidence; the two 1500-sample openings
falling within two minutes of each other lowers it.

**Idea 1, form or dwell.** Resolved. The form drops out. Both forms pass when
they open at 1500 (D1 single, D2 iterated), and both fail when they open at
10000 (job-13 single, job-14 iterated). The bridge job c2eea262 opened on
54aef849 and reached 29dc6ef8 at its twentieth entry, so its pass is a
non-opening pass. PR #257's verdict, "form or dwell, mesh specific", reduces
to the opening entry's sample budget on 29dc6ef8, which matches the dwell
half: a longer first acquisition on that mesh.

**Idea 2, a stale characterization configuration.** Unsupported. e3f757ed
first appears in characterization job-04 (fa847dfd, submitted 03:04:59 UTC
on 10-18). The second Q1 failure (7af74302, 02:55) precedes it, so that
failure could not have served a stale e3f757ed load. The e3f757ed timing
comes from that run's `analysis.json` and `submission.json`. The full-ideal
sweep this idea asks for is in the strategy note's conjecture table: stale
load of an earlier complete mesh, refuted for the 135 meshes served to this
account, with best TVD 0.20 and 0.29 against a 0.012 shot floor. The
per-mesh sweep outputs are not retained as a replayable artifact, so these
two figures rest on the strategy note's record alone until a sweep replay
lands in `docs/evidence/quandela/`. Partial and mixed configurations stay
open.

**Idea 3, covariates.** Resolved for the recorded covariates. Every job ran
exqalibur 1.4.2 and perceval-quandela 1.3.1 at a 4.94 MHz clock. The receipt's
HOM, g2 and transmittance stay within 57.0 to 58.3 %, 0.9 to 1.1 % and 2.69
to 2.95 % for both passing and failing jobs; the first job reads HOM 92.6.
The failures interleave with the passes in time (fail 02:55, pass 09:03 to
09:05, fail 15:53), so a single deploy step cannot produce the split. The
service records no deploy marker or queue identity, so neither covariate can
be checked. The one confound left is time of day: no 10000-sample opening on
29dc6ef8 ran inside the 09:03 to 09:05 window.

**Idea 4, the designed experiment.** Its main arm already ran: job-12 opened
on 29dc6ef8 at 1500 and then ran 10000 with no switch, and passed. Repeating
it at another hour is the only new information it can give, and that is the
time-of-day control from Idea 3. Arm (a), open on another mesh and then run
29dc6ef8 at 10000, ran only after a failing 29dc6ef8 opening (job-16 entries 3
to 23), so the clean form stays open. Arm (b), a 5000-sample opening, stays
open and is the threshold measurement. Each arm needs its own job, because
the opening state exists only at job start, so the arms cost one credit
each.

**Idea 5, the procedure.** Only one opening has retained support: a
1500-sample entry on 29dc6ef8 itself (job-10, job-12), and job-12 alone shows
a 10000 entry passing right after it. An opening on another mesh is
untested as prevention. In job-09, 29dc6ef8 was reached at 1500, which passes
anyway. In job-16, the other mesh loaded only after the opening had failed,
so that shows recovery, not prevention. The cross-mesh warm-up stays
unlicensed until job C or an equivalent run passes. The bug report rests on
the table above, the stable failing histogram within the job-14 and job-16
episode (TVD 0.042 between job-14 and job-16 entry 0), and the refuted
complete-mesh sweep. Q1, job-13 and job-14 returned three different wrong
histograms, so the failure is a stable state only within one episode.

## Falsification plan

Each surviving claim is listed with its status and the result that would
falsify it. Each job below needs a written case approved before submission
and costs about one credit. The jobs run in the order listed, each planned
after the previous one is collected. Every job in the plan is reserved in
advance, so its readings count as confirmatory.

| claim | status | falsifier | cost |
|---|---|---|---|
| F1. On 29dc6ef8, the opening entry's sample budget sets the job's state | supported descriptively, 7 of 7 openings on 29dc6ef8 | job A1 (1500 opening) fails, or job A2 (10000 opening, same hour) passes | jobs A1 and A2 |
| F2. Time of day or service state, not budget, separates the openings | live confound | A1 passes and A2 fails when run back to back at an hour outside 09:03 to 09:05 UTC. A matched pair at one hour removes time as the difference | carried by A1 and A2 |
| F3. A good opening persists through consecutive large entries without a refresh | untested; D2 refreshed with a 1500 entry before each large entry | A1's second or third consecutive 10000-sample entry after the single 1500 opening fails | carried by A1 |
| F4. The budget axis is a threshold between 1500 and 10000 | open | job B opens on 29dc6ef8 at 5000. A pass or fail places the threshold. An intermediate TVD (0.20 to 0.50) is inconclusive, since it fits a graded response, intermittent switching or drift equally | 1 job |
| F5. An opening on another mesh prevents the 10000-sample failure on 29dc6ef8 | untested: job-09 reached 29dc6ef8 at 1500, and job-16 shows recovery after failure, not prevention | job C opens on 14a96ca6 at 1500, then 29dc6ef8 at 10000, and that entry fails | 1 job |
| F6. 29dc6ef8 is the only mesh with a budget-sensitive opening | consistent: 10000-sample openings on e296b6a9 (job-08) and 14a96ca6 (job-11) passed | a 10000-sample opening on another mesh fails | 0 jobs, already read |
| F7. The failing state is a stale complete mesh served earlier | refuted for the 135 meshes served to this account (best 0.20, floor 0.012; strategy note record, sweep not retained) | a shot-floor match to an earlier complete mesh, in a sweep retained as an artifact | offline |
| F8. The failing state is a stale partial or mixed configuration of earlier meshes | open, separate from F7 | a shot-floor fit to such a configuration supports it; no fit across the searched class leaves it unsupported | offline |
| F9. Within one episode, the failing state is a fixed wrong configuration | supported for job-14 and job-16 (TVD 0.042 and 0.052); Q1, job-13 and job-14 differ, so the state does not survive across episodes | a back-to-back repeat of a failing 10000 opening that moves more than 0.10 from its neighbor's histogram | carried by A2 |

Order: A1 and A2 run back to back at one hour, A1 first. A1 opens on
29dc6ef8 at 1500 and follows with three consecutive 10000-sample entries on
the same mesh. A2 opens on 29dc6ef8 at 10000. A1 passing and A2 failing
supports F1 and removes time of day as the difference. A1 failing, or A2
passing, makes the axis time or service state, and job B is then dropped.
Otherwise job B runs next, then job C, whose pass is what licenses the
warm-up procedure. Stop at any void or intermediate reading. The plan's
ceiling is four jobs, about 4 credits.
