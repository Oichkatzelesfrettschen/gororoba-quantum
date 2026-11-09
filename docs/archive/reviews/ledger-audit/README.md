# Adversarial audit of the A_5 exceptional-fiber claim ledger, 2026-11-09

Three reviewers read one brief ([brief.md](brief.md)) against ledger commit 4635cc5a4, the head of draft PR 800:
[review-codex-medium.md](review-codex-medium.md) (Codex, medium effort, replayed the ledger, registry and sign-witness
checks), [review-codex-terra.md](review-codex-terra.md) (Codex, terra model, read selectively and marked 233 of 242 rows
`cannot check`) and [review-grok.md](review-grok.md) (Grok, recomputed Hilbert functions and re-read the W8 and VB
records). Local paths are scrubbed; the text is otherwise as written. This reconciliation checks every ranked finding
and every per-row verdict marked `defect` against the source on branch `a5/ledger-audit-and-engine-v12`, which sits at
main 6f5723b61; main added only documentation fixes since the reviewed commit. Row references use the ledger id
(`A5-NNN`) with the claim named at first use; `ledger.tsv` is
[../../../evidence/a5-exceptional-fibers/ledger.tsv](../../../evidence/a5-exceptional-fibers/ledger.tsv).

Verdicts: **survives** (fixed in this change), **refuted** (the cited source or a command output contradicts the
finding), **boundary** (real, outside this change; the follow-up is named), **fixed on main** (a commit after
4635cc5a4 already carries the repair).

## Codex-medium

1. Kernel-plane limit claim A5-029 has the falsifier "the limit computation" (finding 1): **survives**. The falsifier
   now names the exact Plucker limit of a rank-8 kernel basis along each certified generic arc family and the three
   refuting outcomes (`ledger.tsv`, A5-029); the status page layer-4 row carries the same criterion.
2. Four W8 degree-5 cells (A5-130, A5-136, A5-142, A5-148) read `open` in `claims.json` and `certified` in the ledger
   (finding 2): **survives**. `build_registry.py` read only `.json` and `.jsonl`, and `w8-n16-azure/` was no scan
   root; each `.out` there is one JSON line with the engine digest `7849cbc71ccf1787`, the canonical header digest,
   `d`, `N` and `r_N` (`w8-n16-azure/*/w8d5-n16*.out`). The scan now accepts `.out`, `w8-n16-azure` is a scan root
   (README row of `build_registry.py`), and `build_registry.py --check` with the full root list plus the new root
   reports `registry matches`. `git diff` of `claims.json` and `certificates.jsonl` shows two added certificates (one
   per prime) and the four W8 degree-5 cells moving from `open` to `certified`, nothing else. Test:
   `test_registry_binds_the_w8_degree_5_engine_stdout_records`.
3. The attaching layer is incomplete although the 92 of 96 recount is exact (finding 3): **boundary**. The status page
   states layer 4 "not started"; the follow-up is the first measured arc-limit computation (A5-029).
4. A5-070 (one-chart saturation of the Iso chart fits 11 GB) refuted by deaths under 5 and 10 GB address-space caps
   (finding 4): **survives**. `prlimit --as` caps reserved address space (`docs/runbooks/compute-flags.md`, section
   "Why the review exists"); the claim now names the tested caps, so its `refuted` status stands for the narrowed claim
   and the resident-set question is recorded as untested.
5. A5-041 (a certified candidate ideal verifies cheaply) refuted by one 3 GB, 14-minute presentation (finding 5):
   **survives**. The claim is narrowed to std of that 18-variable presentation; the general question stays open in the
   basis.
6. A5-241 (flatness failure of all-aligned coset blocks) combines 52 dependent blocks by a binomial tail and Fisher
   (finding 6): **survives**. The code applies a per-block seven-coordinate Hotelling test (`nhat_spectral.py`, lines
   128-146), which is sound; the README and the ledger row now call the binomial and Fisher values descriptive. The
   dependence-preserving run-level null is **boundary**: a new analysis over the retained runs.
7. Supersession direction (finding 7): **survives** for A5-040, A5-044, A5-052, A5-072, A5-073, A5-191 and A5-237 (see
   Grok 5); **refuted** for A5-094 and A5-100, which A5-183 and A5-220 already name in their `supersedes` column
   (`ledger.tsv` lines 183 and 220 at the reviewed commit).
8. `nhat_spectral.py --check` fails on one last digit (finding 8): **survives**, reproduced. A fresh run differs from
   `result_spectral.json` in one value, `flatness_hotelling_t2` 765.317510966224 against 765.317510966225, a
   BLAS-dependent last digit. `--check` now compares decoded records with a relative tolerance of 1e-12
   (`same_record`), `--check .` reads `ok: result_spectral.json reproduces`, and the retained record keeps its bytes.
   Test: `test_same_record_tolerates_the_last_binary_digit_of_a_float_only`.
9. Per-row defects A5-130, A5-136, A5-142, A5-148, A5-029, A5-041, A5-070, A5-241: as findings 1, 2, 5, 4 and 6 above.
10. Pattern table, conjectures and remaining-work table (degree-7 closing orders, last-jump law, VB degree-3 component,
    E8-bar degree 6, characteristic 0, open-row costs): **boundary**; none is a ledger defect. The closing-order and
    last-jump conjectures enter the A5-244 falsifier (Terra 6); the costs are the status page "What moves each layer
    next" table. The observation that second-prime ranks duplicate first-prime cells more often than any row states
    needs no row: the per-cell agreement is in `claims.json`.

## Codex-terra

1. A5-015 (the E8-bar to VB fiber contains the degree-4 component) rests on an interpolated family (finding 1):
   **survives**. `working/build/arc/arc-report.md`, "Exact family", states the leading vector is interpolated from 48
   numerical lifts per branch and tested on eight more, and that the symbolic Hensel lift did not finish. The row basis
   now says computed support certificate, not proof; the falsifier names the symbolic lift or a proved degree bound;
   the status page layer-4 row flags the family.
2. A5-014 (the fiber cone is Cohen-Macaulay, refuted if the analytic spread is 4 and 5) is a conditional refutation
   (finding 2): **survives**, with an extra defect the reviewer missed: the fibers column carried the same mislabel that
   A5-006 had, naming the 3-generator opposite-sign X pair (X+ to N-, X- to N+), whose fiber is the polynomial ring of
   A5-001, where the basis (the numerators of h = 15, 51, 122, 240) belongs to the same-sign pair. For E8-bar to N+ and N-,
   the arc certificates (`arcs/README.md`, "Lower bound" and "Reduced fiber") give L inside sqrt(K2) and K2 inside L,
   so the spread is 5 at both primes and the D'Cruz-Raghavan-Verma numerator 1, 16, -12, 10 refutes: A5-014 keeps `refuted`
   for that pair only. The same-sign X half moves to a new open row, A5-245, since the spread 4 needs an arc
   certificate that A5-022 lacks. I recomputed both numerators from the certified h values (21, 83, 225 and 15, 51,
   122, 240) and did not re-read the theorem statement itself.
3. A5-016 falsifier is positive-only (finding 3): **survives**. A relation vanishing on the degree-4 component says
   nothing about the degree-3 component, because every element of K2 lies in P1. The falsifier now reads: decided in
   favor by an arc family dominant onto V(P1), decided against by a relation of degree 7 or more (L agrees with K2
   through degree 6) that does not vanish on V(P1); a failed arc search decides nothing. The status page says so.
4. A5-022 names the X- fiber support while its basis covers V(K2) only, and A5-030 claims every reduced component
   while its basis covers one (finding 4): **survives** for both. Claims are narrowed to V(K2) of X- and to the
   components arcs reach; the falsifier of A5-030 as worded (a component no normalized arc reaches) was met by the
   degree-3 component of E8-bar to VB in the order-1 arcs (`arc-report.md`, "Verdicts"), which decides nothing about
   its presence in the fiber, and the basis now says so.
5. A5-041 and A5-070 resource observations promoted to refutations (finding 5): **survives**; see Codex-medium 4 and 5.
6. `supersedes` direction and A5-244's finished next cell (finding 6): **survives** for both. A5-244's cheapest next
   cell, X- degree 6, finished at 1,700 s and 5.7 GiB (`xm-lown/xmnm_d6_n22_p32009.json`); the falsifier now names X-
   degree 7 (closing N = 25, last jump 225 split 49/56/60/60 by the closed form) and Iso degree 7.
7. `h_d` described as a count of relations (finding 7): **fixed on main**: the status page at 6f5723b61, lines 16-18,
   reads "counts the independent degree-d classes of F(I)".
8. Rows labeled `any` or `all` over finite examples (finding 8): **survives** in part. Primes columns changed on A5-002
   (char0, since the basis is over Q), A5-003, A5-005, A5-006, A5-011, A5-012, A5-021, A5-027, A5-028, A5-029, A5-030 and
   A5-031; A5-004 (a theorem for any field), A5-013 (proved in every characteristic, `doubling_automorphism.py` reports 0
   failing basis pairs at dimensions 8, 16 and 32) and A5-023 and A5-025 (instances of A5-013) keep `any`.
9. 233 per-row verdicts `cannot check`: not findings; no defect is asserted, and the reviewer states the table is a
   coverage inventory. Rows with no other report remain as reviewed by the previous deep review
   ([../findings-deep/README.md](../findings-deep/README.md)).
10. Patterns, forecasts and open-row costs: **boundary**, as Codex-medium 10.

## Grok

1. A5-029 unsized and untestable (finding 1): **survives** (falsifier, as Codex-medium 1); the missing wall time and
   peak memory of one limit is **boundary**, recorded in the A5-029 basis as unmeasured.
2. Direction set unfinished at E8-bar degree 6 and the VB degree-3 component (finding 2): **boundary**; the status page
   already lists them as the open cells (A5-083, A5-089, A5-095, A5-101, A5-016) with the membership pilot as the
   cheapest decider. The recount 92 of 96 is confirmed by three reviewers.
3. A5-014 records a conditional as a refutation (finding 3): **survives**; see Codex-terra 2. The claim that K2 failing
   Cohen-Macaulay does not refute Cohen-Macaulayness of the further quotient F(I) is correct and is why the row used the
   numerator test and not the K2 lengths.
4. Eight survives rows with a falsifier that cannot fire (finding 4): **survives**. A5-010 (K2 Cohen-Macaulay for VB,
   Iso, W8) is promoted to `proved` at both primes: a finite length of the Artinian quotient makes the forms a system
   of parameters whatever their coefficients, and length equal to the degree is the Cohen-Macaulay criterion
   (`k2-cm.jsonl`: 7, 23, 50); the multiplicity criterion is standard and was not re-read here. A5-023 and A5-025 (sign
   correspondences) are promoted to `proved` as instances of A5-013. A5-011, A5-020, A5-021, A5-027 and A5-028 keep
   `survives` with falsifiers naming the hypotheses or replays that can fail; A5-021's argument (a Cohen-Macaulay F(I)
   has multiplicity at least 1 + h_1 - a = 7, the bound of every four-dimensional quotient) uses the degree-4 component
   at one prime, so its primes column is 32009. A5-005, A5-006 and A5-012: primes columns corrected (A5-012 basis read
   `survives` on a `proved` row and is corrected). A5-009 lists E8-bar to N+ twice in its fibers column: **boundary**,
   cosmetic, as in A5-033, A5-035 and A5-052.
5. `supersedes` backward on A5-073 and A5-237, empty on A5-040, A5-044, A5-052, A5-072 and A5-191 (finding 5):
   **survives**. The column now runs from the live successor to the replaced row: A5-063 names A5-073, A5-066 names
   A5-237, A5-058 names A5-072, A5-031 names A5-040 and A5-044, a new row A5-246 names A5-052, and A5-200 and A5-202
   name A5-191. A5-044's replacement, global membership in J + m P_d, has no row of its own, so A5-031 (its
   jet-truncated form) carries the pointer; a row for the untruncated route is **boundary**. `ledger.py --check` now
   rejects a `supersedes` target whose status is not `superseded`, a self
   reference, and a superseded row that no non-superseded row names (`check`, and
   `test_a_supersedes_pointer_runs_from_a_live_successor_to_a_superseded_row`).
6. Four W8 degree-5 certificates unbound, and `README.md` line 45 stale about `n16-laptop` (finding 6): **survives**
   for both. See Codex-medium 2; the `n16-laptop` row now says the root is scanned, `claims.json` binds the degree-4
   record (`certificates.jsonl` source `n16-laptop/e8nm_d4_n16_p32009.json`) and the degree-5 lower bound 742 below 952
   binds nothing. The K2-span half of the W8 and X (32009) sign witnesses is null (`witnesses.jsonl`): **boundary**;
   the generator-sign identity carries the isomorphism (A5-013), and the follow-up is a K2-span row for those three
   pairs.
7. A5-244 sends the next run at a finished cell (finding 7): **survives**; see Codex-terra 6.
8. Sound items (finding 8): no action.
9. Per-row defects A5-005, A5-006, A5-010, A5-011, A5-012, A5-014, A5-020, A5-021, A5-023, A5-025, A5-027, A5-028,
   A5-029, A5-040, A5-044, A5-052, A5-072, A5-073, A5-191, A5-237: as findings 1, 3, 4 and 5 above.
10. A5-004 (F(I) = k[y] exactly when the analytic spread is s) `cannot check` for nilpotents: **refuted**. A nonzero
    ideal Q of the polynomial domain k[y1..ys] has dim k[y]/Q < s, so dim F(I) = s forces Q = 0; no nilpotent keeps the
    dimension. The row stays `proved`.
11. Engine prefixes `130f35904d21f5b4` and `a197799d97287b78` absent from `replay/engine/`: **refuted**; the registry
    finds their bytes as `fiber_rank_v6.py` and `fiber_rank_v7.py` under the failed-runs root (21 and 6 certificates in
    `certificates.jsonl`).
12. Patterns, conjectures and the remaining-work table (E8-bar jump size missing r_17, degree-7 closing orders, the 91
    then 140 membership pilot, characteristic 0): **boundary**; the follow-ups are the A5-244 falsifier, the status
    page next-computation table and, for r_17, a retained intermediate of the E8-bar degree-5 ladder.

## Found during the reconciliation

- A5-014's fibers column carried the opposite-sign X pair for a basis computed on the same-sign pair, the mislabel
  that A5-006 had (Codex-terra 2).
- The status page and A5-052 quoted the Singular export at 97 to 99 percent of the E8-bar, X- and VB wall time. The
  `seconds` fields of the retained records read 96.9 and 96.0 percent (E8-bar degree 5, N = 18), 98.6 and 98.4 percent
  (VB degree 6, N = 20), 79.7 and 80.1 percent (X- degree 6, N = 22) and a closure share of 53 to 74 percent on Iso
  degree 6, W8 degree 5 and E8-bar degree 4. New row A5-246 records the split; the status page, the findings note and
  A5-052 carry the measured figures.
- The findings note's coverage bullet predated the registry growth; it now reads 88 of 96 cells, matching
  `claims.json`.
- `build_registry.py` walks directories in filesystem order (`os.walk`, lines 195-197), so two records that share a
  certificate key (the receipt-bound and unreceipted W8 runs, and two older pairs) resolve to whichever directory the
  filesystem lists first. Sorting the walk changes the `source` of two existing certificates, so it is left
  unchanged: **boundary**, follow-up a sorted walk in a change that regenerates those two rows.

## What survives

- Registry: scan roots plus `.out` records bind the W8 degree-5 cells; `claims.json` carries 88 certified cells.
- Ledger rows changed (40 rows plus two new): A5-002, A5-003, A5-005, A5-006, A5-010, A5-011, A5-012, A5-014, A5-015,
  A5-016, A5-020, A5-021, A5-022, A5-023, A5-025, A5-027, A5-028, A5-029, A5-030, A5-031, A5-040, A5-041, A5-044, A5-052,
  A5-058, A5-063, A5-066, A5-070, A5-072, A5-073, A5-130, A5-136, A5-142, A5-148, A5-191, A5-200, A5-202, A5-237, A5-241
  and A5-244; new A5-245 (open, same-sign X fiber cone Cohen-Macaulay) and A5-246 (survives, stage-time split).
- Status changes with reasons in the row basis: A5-010, A5-023, A5-025 from `survives` to `proved`. Ledger totals move
  from 90 certified, 32 proved, 53 survives, 44 refuted, 9 superseded, 6 rejected, 8 open (242 rows) to 90, 35, 51, 44,
  9, 6, 9 (244 rows); the status page counts follow.
- Code: `ledger.py` validates `supersedes` direction and completeness; `nhat_spectral.py --check` tolerates the last
  binary digit; `build_registry.py` reads engine-stdout `.out` records.

## Not decided

- Terra's 233 `cannot check` rows carry no verdict; the previous deep review and this one cover the rows above only.
- The D'Cruz-Raghavan-Verma theorem (arXiv math/0212119, Theorem 2.1) and the multiplicity criterion behind A5-010 are
  used as cited and were not re-read here.
- Whether the A5-015 interpolant equals the true Hensel output needs the symbolic lift or a proved degree bound
  (`arc-report.md`, "Step 3").

Advisor verdict (2026-11-09): the reconciliation stands, and the per-finding verdicts above are confirmed. Three
corrections reached the change that carries it. The characteristic-0 transfer's upper bound tests the degree-2
fiber relations q(G) in J + m I^2 over Q(i), not q(G) in J, which would reject correct lifts. Good reduction of J
alone does not give the lower bound; that needs good reduction of J + m^N at the closing N. The good-reduction test
(A5-247) compares against the retained headers the certificates bind, not only against fresh F_p runs. The
identification of Proj F(I) with the complex kernel limit set rests on the holomorphic-kernel identification, which
the kernel-attachments record establishes on retained samples only.
