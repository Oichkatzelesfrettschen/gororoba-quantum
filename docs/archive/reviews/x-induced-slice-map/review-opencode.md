I'll begin by establishing the tree state and reading the two commits under review.

Tree is clean at c96ea49f1. Now the ledger and its references.

Claim 1 looks plausible from the grep. Now verifying the main-side duplicate and the HEAD~1 scope.

Claim 1 confirmed; one whitespace regression already visible (lost final newline). Now the new construction script and its E8 predecessor.

Now the base module's remaining stages and the X run script, to test claims 2 and 4.

Now the X README table and the retained logs it cites.

Logs match the README table and row A5-644. Now the comparison program's parametrization (claim 5).

Now the full comparison program and both tests, to test claims 5 and 8.

Now the retained X records, digest list, gate entry, and the X test.

Now the gate entry, the kernel-attachment README section, and the X comparison record.

# Review of PR 1026, gororoba-quantum

Head c96ea49f1 on `a5-x-induced-slice-map`, two commits over `origin/main` ebca38361; 52 files, +6292/-61. Read-only: no file changed, no commit, push, stash, provider job or subagent; no Singular, Python or test suite run. One process deviation: a single `python3` call loaded `ci/gates.json` and printed nothing; the brief forbade Python and I used none afterwards.

## Findings, ranked

1. **Serial CPU-bound loops in the new run script.** `docs/evidence/a5-exceptional-fibers/working/runs/x-induced-slice-map/run_x_induced.sh:18-19` (`for s in xm xp`, `for mode in map relations high`), `:42`, and `:50-55` (six `check` and six `refute` calls) run 18 Singular processes serially. `AGENTS.md:47` says every CPU-bound loop over independent items runs through parallel.py and a serial loop is a defect review rejects. The E8 `run_induced.sh:19,22` has the same pre-existing pattern, so the new script follows precedent, but it is new code and the comparison program it feeds already uses `parallel.ordered_map`. Fix mechanically: one parallel command runner over the existing per-item inputs, which are already separate `.sing` files.

2. **Claim 7 is only partly supported: the X docstring does not state the forced scope.** `docs/evidence/a5-kernel-attachments/slice_module_map_comparison.py:32-36` describes `--family x`, gives c = 1/2 and -1/2, notes that i/2 did not occur, and says the scalar depends on the two normalizations, but never says the X identity is forced by A5-644 or that the run is no independent evidence. The README does (`docs/evidence/a5-kernel-attachments/README.md:1439`: "the identity is forced in the same way, so the run confirms A5-638, A5-640 and A5-644 together and is no independent evidence for any of them"), and ledger row A5-645 does. Add the sentence to the docstring.

3. **The other-root refutation guard is narrower than its name.** `run_x_induced.sh`'s `refute()` greps for FAIL and rejects only the exact line `RESULT transported modulo header 0 header modulo transported 0`. A FAIL with one direction zero and the other nonzero would pass `refute()`. The retained control logs show 35/31, so the recorded evidence fails for the transport reason; this is a hardening gap, not a wrong result. Require both entries nonzero (or the first) in the guard.

4. **Mutation tests do not pin the reason a mutation fails.** Every mutation test asserts only that `problems()` is non-empty (`tests/test_a5_slice_module_map_comparison.py:78` and `:144`), so a mutation that trips a different check would still pass. Manual analysis found each current mutation changes one checked field and fails for its named reason, so claim 8 holds today by inspection; the test would not catch a future mutation failing for another reason. Assert the expected message or field.

5. **Minor: the record prints signed residues while the ledger prints unsigned ones.** `x-slice-module-map-comparison-result.json` gives X- `[1,1,-16004]`, `[1,1,-16014]`, `[1,1,-16028]` and X+ `[1,1,16004]`, `[1,1,16014]`, `[1,1,16028]`; row A5-645 prints 16005, 16015, 16029 and 16004, 16014, 16028. Both are the same residue modulo 32009, 32029, 32057, `problems()` compares `value[2] % prime`, and `tests/test_a5_slice_module_map_comparison.py:108` covers the signed form. No defect; one value with two spellings.

6. **Minor: long commit subject.** `git log --format='%B' origin/main..HEAD | awk 'length($0)>72'` prints only the 85-character subject of c96ea49f1. All body lines are at most 72 columns and no AI trailer is present, so the body-width rule holds.

7. **No defect at head from the HEAD~1 newline loss.** HEAD~1 removed the trailing newline of `docs/archive/reviews/slice-module-map-comparison/README.md` (diff shows `\ No newline at end of file`); HEAD restores it (`od -c` ends `since.\n`). Only the intermediate commit is affected.

Rules checked with no break: pinned bytes (the E8 record `slice-module-map-comparison-result.json` and `quadric_and_germ_probes.py` are absent from the diff; no cited digest moved); text rules (ASCII, emoji-free, no Python line over 120 columns); commit rules (no AI trailer, body width); worktree placement under `~/worktrees/`.

## Claim status

1. **Confirmed.** `origin/main` ledger has A5-642 at line 532 (slice comparison) and 622 (covariance); HEAD has A5-643 at 532 and A5-642 at 624; an `awk` duplicate-id scan is empty. `git grep A5-642` returns covariance references only (`review-a8.md:21,22,32`; `connections-program.md:35,53,124`; covariance `README.md:71`; `status:119,144`) plus historical `review README:22`. HEAD~1 touches exactly three files.
2. **Confirmed.** `x_induced_slice_map.py` imports `header_frame`, `FRAME_LINES`, `HEADER_TAIL`, `HIGH_TEST`, `_read`, `_reduce` and `POSITIVE`; each is generic over the 15-coordinate header, and `POSITIVE` is validated against the piece grading before use. No 21-generator, 148-relation or E8-bar incidence enters.
3. **Confirmed.** All six map, six high, six relations, six check and six control logs show the README table and row A5-644 numbers. Only 33 s and 89 MiB are measured values absent from logs.
4. **Confirmed with finding 3.** The identity control is map-independent by design (vacuity guard); perturbed and swapped controls use the map and fail (2/4, 45/34); other-root runs fail 35/31.
5. **Confirmed by inspection.** The E8 record is not in the diff; TAGS E8 n=21, g=5, GG=25, R=`radical(sK)` reproduce the old literals; X gets 15, 3, 9, `minAssChar(sK)[1]`; `probes.MAPS` X rows pre-exist on main. Runtime byte-for-byte replay not run here (brief forbids computation).
6. **Confirmed.** Residues are plus or minus 1/2 modulo each prime; no control reports a scalar.
7. **Partly.** README:1439 and ledger A5-645 state the forced, no-independent-evidence scope; the docstring X paragraph (lines 32-36) omits it. Finding 2.
8. **Confirmed by inspection, with finding 4.** 22 E8 and 10 X mutations each change one checked field; the 51-passed status is the user's compute-host run, not rerun here.
9. **Confirmed.** `ci/gates.json` entry `core-a5-x-slice-module-map-comparison` replays the X record through `replay_check.py` and `slice_module_map_comparison.py --family x`; the no-Singular branch echoes a skip and exits 77, so it does not pass silently.

## Structural statement no record states

The check and other-root control logs are byte-identical across X- and X+ at each prime: `check-xm-p32009-r10754.log` equals `check-xp-p32009-r10754.log` (sha256 `ac487f52...`), the 32029 pair (`19c111d0...`), the 32057 pair (`31c49ca8...`), and `control-xm-p32009-r21255.log` equals `control-xp-p32009-r21255.log` (`727463ec...`), while the `.sing` scripts differ. So the six comparison cells carry three independent reduction tests, not six; only the scalar sign in the comparison record separates the two basepoints. Falsifier: any byte difference in a check or control log pair at the same prime. Cheapest test: `sha256sum` or `cmp` on those pairs in `docs/evidence/a5-exceptional-fibers/working/runs/x-induced-slice-map/`, already identical at this head.

## Process note

The single Python invocation loaded `ci/gates.json` and computed nothing scientific. No other Python ran, and no command touched the network, a provider or the repository state.
