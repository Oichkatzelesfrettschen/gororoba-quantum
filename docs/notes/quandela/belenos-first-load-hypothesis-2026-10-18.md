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
