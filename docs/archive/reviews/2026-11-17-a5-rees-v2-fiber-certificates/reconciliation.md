# Reconciliation: gororoba-quantum draft pull request 943 (A5 Rees v2 intake)

Head read by every reviewer: 4e844ba0d3f28565c75a8ed5a69a083770c92514 (branch a5-rees-v2-fiber-certificates). The brief is
[brief.md](brief.md).

Reviewers at that head:

- `codex` slug gpt-daybreak-blue-latest (the account cache lists this slug; no slug reads exactly gpt-daybreak-blue), reasoning
  effort high, read-only sandbox, one run (exit 0), 35 commands, all `sed -n` or `cat` of named files. The owner named this
  reviewer for the unit-replacement block (`unit_block.sing`, whose text is the block of lines 179-193 of the retained scripts).
  The raw report stays outside the repository.
- The Advisor, last, on the same head (4e844ba0d): its verdict on each finding is in the section "Advisor verdicts" below;
  the table's last column refers to that section by finding number.

Singular 4.4.1 (banner of Dec 6 2025 11:10:58, the banner of every retained log) ran the experiments below on a compute host,
the long ones inside a memory-capped scope; the two library-load runs of F5 ran without a scope. The retained programs and logs
are the directories named in the dispositions; the toy-ring counterexample scripts and their output stayed outside the repository
and are not retained. `brief.md` is the reviewer's brief with its environment paragraph and local paths removed.

## Findings

| Finding (reviewer text, shortened) | Severity | Disposition | Resolution and commit | Advisor verdict |
|---|---|---|---|---|
| F1. A5-409's falsifier ("a completed modular Rees fiber for one of these ten rows within the same 300 s timeout and 16 GiB cap") is literally met by the Iso run, which is a different script. | serious | Survives, scoped | A5-409 keeps its status; the owner decides. The unit-replacement scripts met the numbers under an enforced 16 GiB scope and 300 s timeout (Iso to N- 12.1 s, 34 MB; X- to N- 10.2 s, 25 MB), on the weight slice and one root, not by `nullity16_rees_fibers.py`. | none recorded |
| F2. The checker verifies internal consistency, not execution provenance; the colon line is checked for presence only; relation indices are not range-checked; the replay shares script, build and method. | serious | Survives as a description | The README states what the checker tests (0de2ef8fb, 69a9a90a2). The colon-line count and the index range are not tightened here; A5-578 records that the two full runs have no replay. | none recorded |
| F3. README and A5-573 say the N+ relation lines are "bound by this run alone" after A5-580 regenerated them. | moderate | Survives | README fixed; A5-573 gains a dated sentence (69a9a90a2). | none recorded |
| F4. README names the pre-stripping pivot G_p where the script uses the stripped g_p. | sloppy | Survives | README reads g_p (69a9a90a2). | none recorded |
| F5. About 140 "redefining" warnings in each full log. | sloppy | Survives as a note | 139 lines, 108 distinct names, the same list in the four logs; every name is a `primdec.lib` procedure loaded at line 157. A script that loads only `matrix.lib`, `linalg.lib` and `primdec.lib` prints 139 lines and one without `primdec.lib` none. The one name the script calls is `minAssGTZ`, whose components give J, so it is the one redefined name that the script calls directly (what `minAssGTZ` calls in turn was not examined); no loop temporary is among the names. README section "Log warnings" (75de1223a). | none recorded |
| F6. Unit stripping is sound; line 192 is the decisive guard; lines 184-189 are an extraction heuristic. | argument | Survives, scope kept | The claim is the fiber over the origin (the maximal ideal m); the global Rees ideals of the original and the stripped generators differ, as a toy ring prints (equal fibers at the origin, different global ideals). README and rows A5-572 to A5-575 say so (69a9a90a2). Line 192 tests, for every generator, c(0) != 0 at the working prime, that c involves s2 alone and the identity modulo J, so a unit check exists in each script. | none recorded |
| F7. Counterexample attempt to the unit-stripping claim. | attempt | No counterexample | A stripped non-unit changes the fiber on toy rings (zero ideal against (y2)); the guards reject it by construction (line 185 removes the s2 power from the candidate, line 192 rejects c(0) = 0, line 193 rejects a constant). A generator that lies in J sends the loop of line 185 into an endless loop (a toy ring prints the stage marker and no result until the timeout), which is a termination defect outside the retained runs: their logs print nonzero `UNIT terms left` for every generator. The logs bind the script digests, so the scripts keep their bytes; the successor script with a guard is proposed in issue 946. | none recorded |
| F8. Status words. | review | Each earned | A5-572 and A5-573 carry certified with one execution each and replay open (A5-578); the owner may weigh that. | none recorded |
| F9. Scope: no sentence promotes the five open gaps. | review | No overreach found | The second prime and root, characteristic 0, the full-run replay, the N+ and Iso producer cells and the header-slice identification stay open (A5-576 to A5-578, A5-583). | none recorded |

## Advisor verdicts

The Advisor read the reviewer's findings with their justifications at head 4e844ba0d and returned these verdicts.

1. A5-409 falsifier met by other scripts: confirmed as measured; the status of the row is the owner's decision.
2. The checker tests internal consistency, not execution provenance: confirmed; the "self-checking" wording is corrected.
3. Stale "bound by this run alone" wording: confirmed; the README is corrected and A5-573 gains a dated sentence.
4. README pivot letter: confirmed; corrected to the stripped g_p.
5. The 139 "redefining" warnings: undecided at the review; the names are listed in the questions section. One redefined
   name, minAssGTZ, is called by the script and yields J; whether the redefinition is a second load of the same library
   is not examined (hypothesis: the library is loaded twice with identical bodies; decider: a run that loads it once
   returns the same J digest).
   2026-11-17: decided. The second load is line 157's `LIB "primdec.lib"`, since `matrix.lib` on line 1 loads `ring.lib` and
   `ring.lib` loads `primdec.lib`. The Iso -> N- script run as retained and with that load removed (no warning) gives the same
   J digest (`31858d4c...` of `string(J)`), the same `FIBER` lines and the same basis digest as the retained log; the README of
   `e8-rees-fibers-v2-p32009` carries the sentence and the scripts keep their bytes.
6. Claim 1, unit stripping: accepted for the fiber over the origin (the maximal ideal m), with two reads asked for and
   answered: every row and the README name the fiber over the origin, and line 192 of the script checks that each
   stripped factor is nonzero at the origin, involves s2 alone, and satisfies the identity modulo J.
7. Status words: accepted, conditional on the comparison in the next paragraph.
8. Scope: accepted, conditional on the same comparison.

Blocking items raised by the Advisor and their resolution: which K the certified rows compare against (resolved: A5-474
names the weight-slice set over Q(i); the Q(i)-to-modular comparison is row A5-584, ranks 148/148/148 and 68/68/68, drop
controls unequal); whether the transport check of the A5-570 receipt is the header-to-weight change of basis (resolved:
it is the t8/t9 sign flip between the N+ and N- header-slice sets; A5-583 stays open); rejection of a log without its
terminal FIBER line (resolved: the checker rejects it; three truncation mutants added, 16 in total; the script's
termination defect is issue 946); the review record (this file).

## Questions answered after the first reading

- Which object A5-474 names. The weight-slice relations over Q(i) (digests in the membership record and the weight-slice
  record), not the header-slice set. The rows A5-579 to A5-581 compared each script K with the modular regeneration of the same
  producer, so a step was missing between the Q(i) set and the modular set. `qi_reduction_compare.py` reduces the Q(i) lines at
  i = 10754 and finds the same span over F_32009 as the modular lines in all three cells (ranks 148, 148, 68; two drop controls
  unequal), recorded as A5-584; rows A5-579 to A5-581 and A5-457 name the K that was confirmed (719b6a658). Equal spans of degree-2
  generators are equal ideals; the header-slice K2 is another quadric ideal (A5-582).
- The "transport 0 0" line of the A5-570 post-check applies a sign change of the y coordinates by t8 and t9 parity between the
  N+ and N- header-slice relation sets, so it is not the change of basis between the header slice and the weight slice; A5-583
  stays open with its decider (8c4f6f290).
- Truncated logs. `log_verdict` rejects a log without its FIBER lines whether or not an `EXIT 0` follows (Singular exits 0 on
  SIGTERM, measured; `timeout` reports 124). The self-test and the toy test now carry three truncations, 16 mutations in all
  (0de2ef8fb). The launcher `run2.sh` only records the exit status and keeps its bytes.

## Hosted Codex round (head 1f8b865b3)

One thread (P1, `kcompare.py:121`): the cell loops of `kcompare.py` and `qi_reduction_compare.py` wait for each CPU-bound Singular
process before starting the next, which `AGENTS.md` ("Every CPU-bound loop over independent items runs through parallel.py") rejects.
Confirmed: the three cells (and the two regenerations per cell of the second script) are independent. Both scripts are bound
by digest (`sha256.txt` of the directory, and `qi-reduction.log` for the second), so `kcompare_v2.py` and
`qi_reduction_compare_v2.py` map the Singular runs and the reductions through `parallel.ordered_map` and print in cell order
(cf112b1f2). Their output equals the retained `prepare.log` and `QIRED` lines byte for byte; wall times on a compute host
are 39.8 s against 21.7 s and 128.5 s against 56.0 s; a fake-Singular test pins the bytes, the cell order and the stop at
a failing cell.

## Hosted Copilot round (head 1ddc65e13)

Two threads, both confirmed against the source, and one failing hosted lane.

- Thread 4596406398 (`run_kcompare.sh:19`): the launcher exits 0 and writes `kcompare.done` when a Singular cell exits
  nonzero or prints no verdict, because the captured status is never propagated and `grep ... || true` accepts missing result
  lines. The launcher is bound by digest, so `run_kcompare_v2.sh` is its successor. It passes a cell only when Singular exits 0
  and the log holds the whole `KCMP RESULT` line with `equal 1 control_drop_unequal 1 control_added_unequal 1` and the terminal
  `KCMP DONE` line, writes `kcompare.done` only after every cell passed, and otherwise stops at the first failing cell with
  `kcompare.failed` and status 1. `tests/test_a5_rees_kcompare_launcher.py` runs it against a fake Singular: a known-good run
  writes the marker; a Singular that exits 7, one that omits the verdict line, one that exits 0 after a SIGTERM without the
  terminal line (Singular exits 0 on SIGTERM; `timeout` reports 124 for a run past its limit) and a later failing cell each leave
  `kcompare.failed` and no `kcompare.done`. The README replay command points at the successor.
- Thread 4596406429 (`check_rees_fibers.py:172`): `log_verdict` does not reject a line whose stripped text starts with `?`
  (a Singular error diagnostic; Singular continues after it), though `run_singular` of `weight_slice_fiber_relations.py` does.
  `log_verdict` rejects it, the self-test and the toy test gain that known-bad mutant (17 mutations), and the four retained logs
  and the nine other retained logs of the two Rees directories (no line starting with `?`) still pass. The checker is bound
  by the `sha256.txt` of its directory, which `check()` verifies, so that row is refreshed and no other file pins its digest.
- Failing hosted `tests` lane (run on 1ddc65e13): one failure, `test_qi_successor_prints_cells_in_order_with_controls_unequal`
  took 16.82 s against the 10 s budget (a test fails at 1.5 times the budget); the three other tests of
  `tests/test_a5_rees_kcompare_parallel.py` took 11.96 s to 14.75 s. The file is new on this branch (cf112b1f2), so the branch
  introduced it and `origin/main` does not have it. Each test now runs on the iso-nm cell without the start delay of the fake
  (1.6 s to 3.5 s on a compute host) in the pull-request lane, and on all three cells marked `audit` (6 s to 7.3 s).
- The two failures of `tests/test_a5_weight_slice_fiber_relations.py` on a compute host are not from this branch: both are
  `audit` tests, both fail at `origin/main` (b7c2b373c) in a scratch worktree (the input digest of
  `nullity8-fiber-import-result.json` that the weight-slice record binds differs from the tracked file, which changed with
  f4b11e4a8 and a919eb929 on main), and that is a defect of main with its own repair.

## Statement for the owner's pending decision on A5-409

The falsifier text of A5-409 is met literally, for incidences it lists (Iso to N-, X- to N-) at root 10754, by two unit-replacement
scripts on the weight slice, and the numeric thresholds hold under an enforced 16 GiB scope and 300 s timeout. It is not met by
`nullity16_rees_fibers.py`, whose elimination on the header slice still blocks as A5-409 records, and root 21255 is not run. Marking
A5-409 falsified asserts the route-independent claim, which the runs refute within the scope "weight-slice unit-replacement scripts,
root 10754, two of the ten rows", and a successor row would carry the new fact; keeping it stalled with a note asserts only the
route-specific claim and adds the Iso and X- results as an alternative route with the falsifier narrowed to
`nullity16_rees_fibers.py` under the original cap. Both readings are consistent with the evidence; the choice depends on whether
A5-409 describes the rows or its script, and it stays with the owner.
