# Ascella mesh-persistence case: execution record and corrections

The [written case](ascella-pathion-mesh-persistence-case.md) keeps its bytes as the approved preregistration; it was
written before submission, so its sentences "Nothing has been submitted" (line 7) and "Both jobs: they wait for the
owner's approval of this case after the local review" (under "Not run") describe the state before the runs. This note
records what ran and corrects the case's pre-submission figures against the retained records.

## What ran

- `sim:ascella` gate job: `results/quandela/runs/2026-11-07T181127Z-sim_ascella-ascella_pathion_mesh_persistence-sim-00/`,
  submitted 18:11:27Z on 2026-11-07.
- `qpu:ascella` job `6bc382af-5a05-49f7-bb76-b3b731b23bec`: `results/quandela/runs/2026-11-07T182838Z-qpu_ascella-ascella_pathion_mesh_persistence-job-00/`,
  submitted 18:28:38Z under the owner's approval recorded in its `submission-state.json`. The case amendment (commit
  c77c801d7, 18:17:45Z) lies between the two submissions.
- Readings: ledger rows A5-200 to A5-203 and the pathion findings.

## Figures that differ from the case text

| Case text | Retained record |
| --- | --- |
| QPU body sha256 `e1a7e990497ae114...` ("Live state and cost", re-planned 18:17 UTC) | bound body sha256 `4cf27af0abeb3fc1a23b0fa10e0dc73abb924d1e29b956f51b1b50c11d66697d`, cases sha256 `9395bade9b3c16fa...` (`submission-state.json`); the case says the binding plan at submission replaces the quoted one |
| expected 84 x 3.2 = 268.8 s | measured duration 259 s (`results.json`, `data.duration`) |
| source-specification snapshot in `ASCELLA_SPEC` (`scripts/ascella_pathion_mesh_persistence.py`): HOM 0.8898, transmittance 0.0546, dark-count bound 0.0030 | snapshot at submission (`submission.json`, `perfs_at_plan`): HOM 0.8846, transmittance 0.0554; recomputed dark-count bound 0.00324, g2 and indistinguishability shift 0.002556 under both snapshots |

Both snapshots leave the source-specification shift an order of magnitude below the 0.07 to 0.11 mirror failures the
case measures, so the case's conclusion on that point holds.

## Corrections to derived records

- A5-200: "no drift within the job" means the replayed-anchor drift flag did not fire (anchors 1.027 and 1.028 in the
  two halves, inside the 0.03 band of the analysis); the half correlations carry no preregistered threshold.
- A5-201: the fresh-seed reading excludes a full carry of the original failures (carried fraction -0.06, 99 percent
  interval [-0.64, 0.51]); a carried fraction up to about one half is not excluded.
- A5-191: "every mesh carries its own fixed error" holds for the 52 replayed meshes; the replay arm cannot separate a
  per-mesh carrier from a per-shifter one, since the case's own prediction table gives high persistence under both.

Source: the read-only Codex review of the executed case and its adjudication (survivors F4, F1, F2, F8, F5), reviewed
by the Advisor before these corrections.
