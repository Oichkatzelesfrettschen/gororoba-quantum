# Reconciliation: gororoba-quantum draft pull request 943 (A5 Rees v2 intake)

Head read by every reviewer: 4e844ba0d3f28565c75a8ed5a69a083770c92514 (branch a5-rees-v2-fiber-certificates). The brief is
[brief.md](brief.md).

Reviewers at that head:

- `codex` slug gpt-daybreak-blue-latest (the account cache lists this slug; no slug reads exactly gpt-daybreak-blue), reasoning
  effort high, read-only sandbox, one run (exit 0), 35 commands, all `sed -n` or `cat` of named files. The owner named this
  reviewer for the unit-replacement block (`unit_block.sing`, whose text is the block of lines 179-193 of the retained scripts).
  The raw report stays outside the repository.
- The Advisor, last, on the same head: no Advisor verdict is recorded in this record. Each finding below carries the verdict
  of the author of this record against the source; the Advisor column is empty and stays empty until the Advisor's text is
  attached.

Singular 4.4.1 (banner of Dec 6 2025 11:10:58, the banner of every retained log) ran every experiment below inside a memory-capped
scope on a compute host. The programs and their output are in the pull request body and in the retained directories named in the
dispositions; the counterexample scripts are small toy rings.

## Findings

| Finding (reviewer text, shortened) | Severity | Disposition | Resolution and commit | Advisor verdict |
|---|---|---|---|---|
| F1. A5-409's falsifier ("a completed modular Rees fiber for one of these ten rows within the same 300 s timeout and 16 GiB cap") is literally met by the Iso run, which is a different script. | serious | Survives, scoped | A5-409 keeps its status; the owner decides. The unit-replacement scripts met the numbers under an enforced 16 GiB scope and 300 s timeout (Iso to N- 12.1 s, 34 MB; X- to N- 10.2 s, 25 MB), on the weight slice and one root, not by `nullity16_rees_fibers.py`. | none recorded |
| F2. The checker verifies internal consistency, not execution provenance; the colon line is checked for presence only; relation indices are not range-checked; the replay shares script, build and method. | serious | Survives as a description | The README states what the checker tests (0de2ef8fb, 69a9a90a2). The colon-line count and the index range are not tightened here; A5-578 records that the two full runs have no replay. | none recorded |
| F3. README and A5-573 say the N+ relation lines are "bound by this run alone" after A5-580 regenerated them. | moderate | Survives | README fixed; A5-573 gains a dated sentence (69a9a90a2). | none recorded |
| F4. README names the pre-stripping pivot G_p where the script uses the stripped g_p. | sloppy | Survives | README reads g_p (69a9a90a2). | none recorded |
| F5. About 140 "redefining" warnings in each full log. | sloppy | Survives as a note | 139 lines, 108 distinct names, the same list in the four logs; every name is a `primdec.lib` procedure loaded at line 157. A script that loads only `matrix.lib`, `linalg.lib` and `primdec.lib` prints 139 lines and one without `primdec.lib` none. The one name the script calls is `minAssGTZ`, whose components give J, so its redefinition at load is the single warning on the path of every FIBER line; no loop temporary is among the names. README section "Log warnings" (75de1223a). | none recorded |
| F6. Unit stripping is sound; line 192 is the decisive guard; lines 184-189 are an extraction heuristic. | argument | Survives, scope kept | The claim is the fiber over the origin (the maximal ideal m); the global Rees ideals of the original and the stripped generators differ, as a toy ring prints (equal fibers at the origin, different global ideals). README and rows A5-572 to A5-575 say so (69a9a90a2). Line 192 tests, for every generator, c(0) != 0 at the working prime, that c involves s2 alone and the identity modulo J, so a unit check exists in each script. | none recorded |
| F7. Counterexample attempt to the unit-stripping claim. | attempt | No counterexample | A stripped non-unit changes the fiber on toy rings (zero ideal against (y2)); the guards reject it by construction (line 185 removes the s2 power from the candidate, line 192 rejects c(0) = 0, line 193 rejects a constant). A generator that lies in J sends the loop of line 185 into an endless loop (a toy ring prints the stage marker and no result until the timeout), which is a termination defect outside the retained runs: their logs print nonzero `UNIT terms left` for every generator. The logs bind the script digests, so the scripts keep their bytes; the successor script with a guard is proposed in issue 946. | none recorded |
| F8. Status words. | review | Each earned | A5-572 and A5-573 carry certified with one execution each and replay open (A5-578); the owner may weigh that. | none recorded |
| F9. Scope: no sentence promotes the five open gaps. | review | No overreach found | The second prime and root, characteristic 0, the full-run replay, the N+ and Iso producer cells and the header-slice identification stay open (A5-576 to A5-578, A5-583). | none recorded |

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

## Statement for the owner's pending decision on A5-409

The falsifier text of A5-409 is met literally, for incidences it lists (Iso to N-, X- to N-) at root 10754, by two unit-replacement
scripts on the weight slice, and the numeric thresholds hold under an enforced 16 GiB scope and 300 s timeout. It is not met by
`nullity16_rees_fibers.py`, whose elimination on the header slice still blocks as A5-409 records, and root 21255 is not run. Marking
A5-409 falsified asserts the route-independent claim, which the runs refute within the scope "weight-slice unit-replacement scripts,
root 10754, two of the ten rows", and a successor row would carry the new fact; keeping it stalled with a note asserts only the
route-specific claim and adds the Iso and X- results as an alternative route with the falsifier narrowed to
`nullity16_rees_fibers.py` under the original cap. Both readings are consistent with the evidence; the choice depends on whether
A5-409 describes the rows or its script, and it stays with the owner.
