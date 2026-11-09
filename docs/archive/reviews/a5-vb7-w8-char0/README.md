# Review of the E8-bar -> VB degree-7 and W8 characteristic-0 plan

`codex` (gpt-daybreak-blue-latest, high effort, workspace-write sandbox) read [brief.md](brief.md) on 2026-11-09 at
commit e97d7f285. It wrote [review-codex.md](review-codex.md) in 12 minutes and changed no other file, which
`git status` confirmed. The brief asked for an audit of `docs/design/a5-vb-degree7-and-w8-char0-plan.md` and an
adversarial reading of the open task list against the thesis that nothing more can be done on the present
foundations. The table checks each finding against the source.

| finding | verdict | evidence and resolution |
|---|---|---|
| 1. The Gaussian multi-modular test (product of primes above 2B) is false | survives | `(128 + 125*10754) % 32009 = 0` while abs(128 + 125i) < 179; at i -> -10754 the value is 256. The plan now checks both conjugate roots at every split prime |
| 2. Equal cofactor supports cannot certify a Q(i) lift | survives | `lift` has no canonical solution rule (A5-248). The plan now routes check 2 through a canonical degree-bounded RREF system, and `cofactor_support.py` stays a diagnostic. The lifts also measured 277 MB of cofactor text per prime |
| 3. W8 degree 5 needs check 3 at N = 16 | survives | the decision text said check 2 only; it now names check 3 at N = 16 for degree 5, which is running |
| 4. Launchers can report success after a failed child, and leave Singular's stdin open | survives | `run-lifts.sh` had `\|\| true`; `run-probes.sh` used a bare `wait`. `compute-flags.md` records that Singular 4.4.1 reads a non-terminal stdin. All three launchers now take stdin from /dev/null and write each child's exit status. The runs already made exited 0 with RESULT lines; the stdin rule cost them nothing because a non-interactive `sh` gives an asynchronous list /dev/null stdin. Boundary: `parallel.py` maps Python callables. These shell launchers start independent Singular processes and carry no Python loop |
| 5. The std share is 94.5 to 98.6 percent, not 99 | survives | recomputed from `seconds.total` in the nine records; the text is corrected |
| 6. Live pilot readings are written as if retained | survives | the lever table is labeled provisional. A lever enters an engine only through a retained N = 18 comparison binding producer, build, export digests and ranks |
| 7. The all-degree W8 argument omits the affine-cone bridge and the cycle argument | survives | both bridges are written into the plan; the status stays hypothesis |
| 8. The W8 cost basis is inconsistent | survives | the receipts record 6,559.6 s and 9,860.3 s for the product and standard-basis stages, against membership stages of 325.1 s and 575.4 s. The 5,619 s figure came from a consult table. The plan now uses the receipts and names the scaled direct W8 lift (about 136 h per prime) as unbounded |

The proposals that survive go into the task list:
- a deterministic variable-order screen with `groebner`;
- check 2 through a canonical linear system that reuses the retained W8 standard bases;
- the jet-parameter arcs of task 37 and an Iso point-blowup pilot for task 56, both on the small OCI host `lab-a1`
  (9.5 GiB budget);
- a sparse membership solver for task 110.

The review's verdict on the thesis: it is false for tasks 37, 42, 56, 75 and 115 and for the VB lever, each of which
has a bounded next computation. It holds for task 110 under the current algorithm, which needs a new solver, and for
task 113, which needs a streamed engine.

## Final review

`codex` (gpt-daybreak-blue-latest, high effort) read [brief-final.md](brief-final.md) at 84276830f. At the owner's
request it ran with approvals and the sandbox bypassed, computing only on the hosts and limits the brief allowed. It
wrote [review-codex-final.md](review-codex-final.md). The table checks each finding against the source.

| finding | verdict | evidence and resolution |
|---|---|---|
| 1. The scope document omits the item-6 deliverables | survives | `docs/state/plans/a5-kernel-attachments.json` marks limit-sets-8-to-12, limit-sets-into-nullity-16, compatibility and attaching-maps `todo`, and no task covered them. Tasks 126 to 131 now carry them, and the scope document gains an "Item-6 deliverables" section. Item 6 stays open |
| 2. A bare `wait` drops child failures; the degree-7 launcher accepts more cells than the budget | survives | `sh -c '(exit 1)& wait'` prints 0. Every launcher now waits on each PID and exits nonzero on any failure (a three-child test with one failing child exits 1). `run-cells-v13.sh` refuses more than four cells. The live laptop copies predate the fix, and their `.status` files and cell events are read directly |
| 3. The W8 N = 13 cost quotes the 114 s substage as the whole check | survives | `/usr/bin/time` gives 21:46 wall for the whole driver; the scope document now says so |
| 4. Engine v13 has no regression gate | survives | the degree-5 laptop validation (r = 255, blocks 75/50/65/65, 416 s) is one cell. Before v13 records enter the ledger, the retained N = 18 comparison and a test pinning the export byte equality at small N are owed (task 119) |

The measurements Codex made enter the plan as provisional pilots:
- `degBound = N` keeps the basis byte-identical and saves 12 percent at N = 13 and 33.5 percent at N = 15.
- On the laptop, `slimgb` beats `std` by 3.66 times at N = 13 and 3.87 times at N = 15.
- `groebner`'s default choice and `option(length)` are slower.
- Reversed variables are 1.81 times slower.

Its tool survey keeps Singular for the sparse standard basis, saturation and the Q(i) checks. It moves exact rank and
canonical RREF to FLINT, FFLAS-FFPACK and LinBox, or the GPU. It refutes msolve for J + m^N, and M4RI/M4RIE (F_2
only) for these primes.
