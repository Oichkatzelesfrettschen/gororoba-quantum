# Open issue triage (read-only), main at 942319f

Method: issue bodies read in full; each named file grepped on main; branch
history checked with `git log --all --not main -- FILE` and
`git log --all -S KEYWORD -- FILE`. Effort: S under 1 h, M half day, L more.
Nothing was run (no gates, no dry runs, no hardware).

Branch note: the quantum-inspire files (`capture_qi_docs.py`,
`qi_ibm_noise_replay.py`, `qi_zero_divisor_cases.py`, `research_state.py`)
show unmerged commits only because PR #144 landed as a squash (942319f).
No branch holds a fix for any of the 17 issues.

| Issue | Script / file | Gap on main (file:line) | Branch fix | Effort | Kind | Triage note |
|---|---|---|---|---|---|---|
| #9 | scripts/codex_review_status.sh, scripts/resolve_answered_threads.sh | status script paginates thread comments (codex_review_status.sh:190, `first: 100, after`), fixed in 5dd4ee8 / 8376dab. resolve_answered_threads.sh:37 still reads `comments(last: 100)`, with a design argument at lines 26-29 that an answer lies inside the newest 100 | none needed | S (close, or cite the argument) | code, partly fixed | Status script: resolved. Resolver: the stated predicate argument holds for current answers; close with a reply, or note the residual |
| #62 | gororoba_quantum/verify.py (CSV from open_gororoba) | verify.py:58-61 defaults GOROROBA_ROOT to ~/Github/open_gororoba; ci/gates.json:2613-2616 lists `verify.py` under "excluded"; ci.yml has no open_gororoba checkout or generation step | none | L (cross-repo checkout and registry build in CI) | CI infrastructure | Real gap; gate stays excluded until a generated dataset job exists |
| #64 | docs/evidence/c881_exhaustive/replay_rocq.sh | ci/gates.json:2604-2606 excluded ("needs the Rocq toolchain"); ci.yml has no Rocq install or path-filtered job | none | M (path-filtered job, pinned Rocq 9.2 install, OCaml 5.5.0) | CI infrastructure | Real gap; the pinned toolchain install dominates the cost |
| #69 | scripts/n21_orbit_rca.py | no barrier construct in the file (grep: 0 hits); window arms are not barrier-equalized | none (e9bcfff touched the file, not this) | M | code, preregistration contract | Real gap; falsifier is local (window_roles couplings with Aer) |
| #70 | gororoba_quantum/qpu_planning.py:144-167 (window_durations) | takes the backend-wide max over `target["measure"]` and `target["reset"]` (lines 153-162) and returns the max, not the routed control's values | none | S (thread the control qubit into the callers) | code, latent | No effect on ibm_fez or ibm_kingston today (uniform durations per the issue); defect only on heterogeneous backends |
| #71 | scripts/n21_orbit_rca.py (signed_exposure, window_roles) | single-gap exposure model; no segment-by-segment simulation | none | L (archived ISA segment simulation, detuning fit) | research follow-up | Modeling extension, not a defect on current runs |
| #72 | scripts/n21_orbit_rca.py: raw_pubs (214-240), joint_quasistatic_fit (475-550) | item 1: raw_pubs checks only collect.json and raw/JOB/index.json (lines 216-222); no record.json submission.jobs or pub_name binding. item 2: static-only fit (lines 538-545) starts from the winning mean-plus-spread basin only | none (615091d is a different binding) | S-M | code, hardening | Item 1 is reachable only by copying another run's tree: a boundary reply plus a follow-up is the triage default. Item 2 does not reach a reported number (joint fit is skipped on every retained run) |
| #74 | scripts/patch_window_analysis.py | no calibration field read anywhere in the file (grep: 0 hits); cross-job comparisons are not gated | none | M | code | Real gap; reachable on any collected three-job patch run |
| #75 | gororoba_quantum/qpu_cases.py:324-334 | validator compares each dynamic PUB's classical_latency_seconds against stages x design["classical_latency_us"] (nominal), not the scenario latency that --cost-scenario (qpu_cases.py:218-223) writes | none | S-M | code | Real gap through the documented --cost-scenario CLI; the fix is to validate against the scenario value |
| #76 | gororoba_quantum/live_run.py:546, 1392-1401 (_choice_execution_kind), 1685 | dry-run classification now goes through _choice_execution_kind (uses _is_dynamic, line 3762) and capability_violations (line 546) | none | S to confirm | code, likely fixed | Not confirmed: the dry-run record path was not traced to its caller, and the falsifier was not run (not run). Confirm with a patch-window submit-free dry run before closing |
| #131 | scripts/local_member_cz_conformance.py:186-193, 295-304 | dynamic members land in `unchecked` with reason "mid-circuit measurement, reset or control flow" and are never audited for CZ | none | L (exact branch enumeration per member, declarations for the 62 names) | code plus audit design | Real gap; the proposed audit is a design task as much as a fix |
| #140 | scripts/d_locus_nullity.py:317-318 | `_require(rows == retained["rows"][:len(rows)])`: rows past the prefix are accepted as their own expected value | none | S (bind frame, kind, a_scale, b_scale from frame_draws, which need no rank work) | code | Reachable only by hand-editing result.json, which core-324 (full tier) already rejects. Triage default: boundary reply plus follow-up; the S fix is optional |
| #143 | scripts/n21_conjugation_noise.py:262-305 | check() recompiles only the chosen seed (line 282-297); per_seed_routed_cz is copied from the record (line 302) and checked only by its minimum (line 304) | none | M (--all-seeds replay, 144 compilations, about 5 min on two CPUs) | code | run() cannot produce the edited state, so the defect is in the verifier only. Boundary reply, or full-tier gate |
| #150 | scripts/capture_qi_docs.py:225-236 | check() reads only the rows each MANIFEST.json lists; no comparison of the file set with the manifest path set or the captured inventory | none | S-M | code | Reachable through a deleted or added page in docs/notes/quantum_inspire/site/, a repository-maintenance action; treat as a fix in a small PR |
| #152 | scripts/qi_ibm_noise_replay.py:586-615 | check() replays only body["additivity"][0] and body["teleport"][0] (lines 612-613) | none | M (full-tier replay of all entries) or L (exact shot-free recompute within pr tier) | code, gate strength | Real gate gap for code changes that alter only later stars or paths; fixable without a hardware run |
| #153 | scripts/qi_zero_divisor_cases.py:386-403 (batch layout), 660-695 (load_series, analyze) | readout pair is one batch (batch-01); analyze() takes zero, one = raw["readout-0.cq"], raw["readout-1.cq"] (lines 692-694) from the series-wide raw dict, so batch-00 shots get batch-01's assignment | none | M-L (three batches, load_series keyed by (batch, file), per-batch secondary(); the retained 221133Z replay must stay unchanged) | code, analysis defect | Real defect in the secondary estimators. Preregistered raw-count estimators are unaffected. Affects the next batched run |
| #154 | scripts/research_state.py:296-330 | checks job membership and the per-job sum of change (lines 307-309) only; no field-by-field comparison of transaction id, timestamp or domain with usage.json rows | none (the adapter exists on main; the transactions check is in 942319f) | S-M | code, latent | No retained run carries a transaction (usage.json has zero rows), so no current number moves. Reachable only by editing a collected results.json: boundary reply plus follow-up is the triage default |

## Summary by kind

- Code defects with a reachable interface (fix in the next push): #70 (latent), #74, #75, #152, #153, #150, #69.
- Hardening, boundary by triage default (reply plus follow-up issue): #72 item 1, #140, #143, #154.
- CI infrastructure: #62 (L), #64 (M).
- Research or analysis extension: #71 (L), #131 (audit design, L).
- Likely already fixed, confirm before closing: #76 (dry run not run), #9 (status script fixed; resolver behind a design argument).

## Effort total

S: #9 close, #70, #76 confirm, #140 (optional).
M: #64, #69, #74, #143, #152 (full-tier variant).
L: #62, #71, #131, #153 (M-L), #152 (exact variant).
