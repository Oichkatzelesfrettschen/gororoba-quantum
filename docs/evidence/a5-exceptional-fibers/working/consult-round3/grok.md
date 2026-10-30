I'll read the brief and the three documents it names, then check those claims against the raw logs. No edits and no solver runs.The brief names three notes and five questions. I'll read those notes next, then check the stated failures and counts against the raw logs.The three notes disagree on a few timings and on how far the second prime and the W8 Hilbert function actually go. I'll check those against the logs before answering.The Kaggle summaries already split several timings from the brief. Next I’ll read the stage logs and the remaining summaries to see which step actually burned the time.The degree-2 receipts already separate product setup, the Gröbner basis, and reduction. I’ll read the driver and the timed-out stage logs to see which of those three the failures actually hit.The products-stage failures die inside `std(J + m P_d)`, after the products have already been built. The chart sentence that puts all 40 stalled jobs inside `minAssChar` does not match the logs.

## 1. What the failures actually are

The driver builds degree-d products and reduces each factor modulo `std(J)` before it starts the timer that matters. It then calls `std(Q)` on `Q = std(J)` plus every `t_k * P_i` (9 times the target count), and only afterwards reduces and, if the kernel is nonempty, checks membership. On every finished degree, `std(Q)` is almost the whole clock: X− degree 4 is 13,752 s of std against 89 s to build products and 607 s to reduce; E8 degree 2 is about 12,590 s of std against about 20–27 s to build products and about 50 s to reduce. Membership is a later stage. Degree 2 pays it because the quadrics are there (E8, about 1,120 s). Degrees 3 and 4 that finished have an empty kernel, and the driver skips membership.

| Job | What the log shows | Cause |
|---|---|---|
| VB degree 5 | `products_ms` 8.7 s, 10 generators, 266 targets, then exit 124 at 12 h wall, 10 h 35 min CPU, peak 12 GB | `std(Q)` on a 9×266-generator ideal. Products and the reduction modulo J were done. |
| Iso degree 4 | `products_ms` 32.3 s, 17 generators, 640 targets, then exit 124 at 36,002 s | Same `std(Q)`. The 30 GB box was not the limit. |
| W8 degree 3 | `products_ms` 444 s, 24 generators, 600 targets, then exit −9 at 18,999 s | Same `std(Q)`, killed by signal 9 inside the 30 GB Kaggle container. Timeout on this runner is exit 124. |
| Charts | All 41 printed `dim`. Radical printed on 9 Iso and 14 W8. Only W8 chart 10 printed primes (74 s). | 18 charts died inside `radical` (8 Iso, 10 W8). 22 died inside `minAssChar` (9 Iso, 13 W8). |
| TPU smoke | No status line under `distribute/out` or `runs` | Not checked. Singular never uses the TPU. |
| Older eliminations | Pivot saturation, `std(L)`, msolve, `minAssGTZ` logs stall from hours to 209 GB | The ideal is the full Rees or a dense coordinate change, not one graded piece. |

The 8.3 GB figure is not in `build/logs/mine/vb5/d5-products.log`. That file’s cgroup line is a 12 GB peak at the 12 h kill. The host W8 log `runs/w8_a3/out.log` records 600 products in 300 s and then stops; it has no 14 GB sample.

**Recommendation.** Stop forming `Q`. The open question at each degree is whether `h_d` equals the target count, which is already `dim(k[y]/K2)_d` once the lower-degree kernel is empty. The products `P_i` are reduced modulo `J` when `products_ms` prints. Write them and rank their classes in `M/mM`.

A constant relation `∑ a_i P_i ∈ J + mM` forces the same relation on the lowest `m`-adic forms, because multiplication by `t_k` raises order by 1. If those forms are linearly independent over `F_32009`, then `h_d` equals the target count and there is no new relation. That is one matrix whose column count is the monomials of a single degree in 9 variables. If the lowest degree is too small to hold that many independent forms, step up one order. Only an inconclusive filtration goes back to `std(Q)`.

**Falsifier.** On Iso degree 3 (`products_ms` 2.2 s, `h = 265` equal to 265 targets, kernel empty) or X− degree 4 (`products_ms` 89 s, `h = 240` equal to 240 targets), the lowest forms are linearly dependent. The certificate then does not fire on a degree already known to be independent, and it does not decide the open degrees.

## 2. Iso and W8 quadrics

`dim` is already known on every chart: affine 5 for Iso (projective 4), affine 6 for W8 (projective 5). No chart job exited −9, so 45 minutes of `radical` plus `minAssChar` stayed under the 30 GB Kaggle cap.

Iso’s quadric Gröbner basis is already in hand: `probes/pD_iso.log` reports projective dimension 4, degree 23, Hilbert function 17, 85, 265, 640, `std` size 81, and `facstd` one piece, with both timers reading 0 seconds. The global structure logs `runs/k2struct/iso.log` and `w8nm.log` are empty. Their first `RESULT` is printed only after `radical`, and Iso’s `std` is already known to be immediate, so those runs died in `radical` or never flushed. W8’s Hilbert function is already computed without a radical: `review-checks/claude/w8_a2-k2hf.log` gives projective dimension 5, degree 50, and 24, 156, 600, 1725. The 600 and 1,725 are values of `k[y]/K2`, which is why the killed degree-3 job had 600 targets. They are not a fiber Hilbert number.

The chart script and `iso.sing` compute the radical and then call `minAssChar` on the original ideal, and they do not write the radical. The X− recipe that finished in about a second was radical first, then `minAssChar` on the radical.

**Recommendation.** Three jobs, each capped at 30 GB.

1. Iso, one Kaggle CPU session, 12 h: `radical` of the existing 81-element basis, write it, then one `minAssChar` on that radical. `facstd` already returned one piece.
2. W8, one Kaggle CPU session, 12 h: `facstd` of the existing basis. If it splits, decompose the factors. If it returns one piece, the same radical-then-`minAssChar` job.
3. Charts only for what those two jobs do not finish. Split the script: write the radical and stop; then Gaussian-eliminate linear forms and run `minAssChar` on the image. The 22 charts whose radical already printed `1` skip the first half. W8 chart 10, with 37 degree-≤1 jet terms, finished the whole chain in 74 s and is the shape to aim at. Five concurrent 12 h sessions cover the rest.

**Falsifier.** The Iso radical job writes no `RESULT` line at 12 h, or a chart exits −9 before a new `RESULT` line. Either one retires that job. A `facstd` with several pieces retires the one-component reading of the Iso probe.

## 3. Strongest lever

The strongest lever is that, above the quadrics, every certified graded piece is exactly the quadric prediction, at both primes.

Kernel empty and `h_d` equal to the `K2` Hilbert value: X− degrees 3 and 4 (122, 240), X+ degree 3 at 32029 (122), Iso degree 3 at both primes (265), VB degrees 3 and 4 (80, 155). Degree 2 matches too, and the relations there are the quadrics themselves: E8 is 83 with 148 quadrics on all three Kaggle runs, W8 is 156 with 144 quadrics at 32029. X+ and X− have the same `K2` structure line for line, including radical 12, 45, 112, 225 and one prime (3, 12), in `xm.log` and `xp_p2.log`. VB’s degree-5 target count is already 266, and the third difference of 10, 34, 80, 155, 266 is 7, 7, the third difference of a degree-7 cubic.

That lets the program skip the membership stage on these degrees, skip a second-sign fiber run where the coefficient symmetry is already certified, and skip every retired elimination. For VB, the degree-5 comparison against 266 is the Hilbert test that can still put the degree-3 prime outside the fiber. The arc family in `build/arc/arc-report.md` already puts the degree-4 prime in the fiber and keeps the degree-3 prime open.

**Falsifier.** Any later degree whose certified `h_d` is strictly smaller than `dim(k[y]/K2)_d`, at either prime. One such degree removes the identification of the fiber with `V(K2)`.

## 4. Where the open work goes

Singular is single-threaded here: VB degree 5 used 10 h 35 min of CPU in 12 h of wall. Extra cores do not speed `std(Q)`. The TPU queue and the GPU hosts do not either. AWS `m7i-flex.large` has 8 GB, below the kill that already hit W8.

| Work | Substrate | Expected envelope | Why |
|---|---|---|---|
| Leading-form rank for VB degree 5, Iso degree 4, W8 degree 3 | Build host, `MemoryMax` 4 GB | Minutes after the products, which already finished in 9 s, 32 s, and 444 s | Decides `h_d` against 266, 640, and 600. No `std(Q)`. |
| VB degree 5 `std(Q)` only if that rank is inconclusive | Build host, `MemoryMax` 20 GB, 48 h | Peak already observed 12 GB; the 12 h cap is what stopped it | RAM is not the constraint. Kaggle’s 12 h session cannot hold it. Azure’s 4 vCPU is not a faster core. |
| W8 degree 3 `std(Q)` only if the rank is inconclusive | One Azure `Standard_FX4mds_v2`, 84 GB, its own case, 24 h first | Above the 30 GB SIGKILL. About `$13` at `$0.547/h` if stopped at 24 h | The only listed machine larger than the box that killed it. |
| Iso radical + `minAssChar`; W8 `facstd` | Kaggle CPU, two of the five sessions, 30 GB, 12 h | Iso `std` is already immediate; radical is the unmeasured part | Global structure runs produced no `RESULT` under the old 600 s budget. |
| Remaining chart radicals and decompositions | The other Kaggle CPU sessions, 30 GB, 12 h, five at a time | Under 30 GB for 45 min, observed | 18 radicals and 22 decompositions, as split above. |
| E8− `K2` structure | One Kaggle CPU hour, 8 GB | N+ finished in the 3 GB / 600 s budget: dimension 4, degree 11, radical Hilbert 16, 69, 195, 440, primes (4, 11) and (3, 4) | Same script on the 148 quadrics. The sign transport failed (span 41 of 42), so N− is its own ideal. |
| Remaining VB arc charts and kernel-plane limits | Build host, `MemoryMax` 8 GB, 30 min, as in `arc-report.md` | The degree-4 family already finished under that cap | These are the attaching maps. They wait on nothing in the cloud. |
| X beyond degree 4, and the same leading-form test | Build host, 4 GB, then Kaggle only if a real `std` is still required | Degree 4 already finished in 14,480 s and 30 GB | Symmetry covers X+ once the X− coefficient check is the one on record. |
| Component group in 96 unknowns; nullity-4 Gauss map | No cloud job yet | No runtime in these logs | The retained bundle record still lists both as residuals. A producer has to exist before a machine is chosen. |

**Falsifier for the Azure assignment.** W8 degree 3 has no `std_ms` line at 24 h, or RSS passes 70 GB. Stop. A larger machine repeats the same Buchberger input. **Falsifier for leaving VB on the host.** A rerun with `MemoryMax` 20 GB exits on memory rather than on the clock. Then it moves to the 84 GB VM.

## 5. What is wrong

This line in `a5-exceptional-fiber-findings.md` is wrong:

> 40 of 41 charts stopped at the 45-minute cap inside `minAssChar`; the charts give affine dimension 5 (Iso) and 6 (W8) with radical certificates on 9 and 14 charts; W8 chart 10 finished with one prime of affine dimension 6 and 37 linear generators

The counts 9, 14, and chart 10 match `distribute/out/a5-chart-iso/summary.json` and `a5-chart-w8nm/summary.json`. The locus does not. Eighteen charts printed `dim` and never printed `radical`, so they stopped in `radical`. Twenty-two printed `radical 1` and never printed a prime. The same over-assignment is in the brief’s failure table.

This line in `kernel-bundle-residuals.md` is unsupported:

> The quaternionic four-plane `xi_R` over `V_2(R^7)` is actually nontrivial

`docs/evidence/a5-kernel-bundles-residuals/` is not in the tree, and neither is `xi_real_type.py`, `g2_commutant.py`, or `nullity4_orbit_ranks.py`. The retained `bundle-invariants-result.json` still lists `individual_xi_real_type` with the boundary “the four-plane `xi_R` is not” decided, and the same file still lists the component group and the nullity-12 reductions as residuals. The homotopy step in the note is a standard surjection `π_5(S^5) → π_4(SU(2))`. The representation claim it rests on, self-dual rank 3 and anti-self-dual rank 0, has no producer log under `distribute/out` or `runs`. The nullity-4 table and the “96 unknowns” count are in the same position.

## Claims checked in the files

Checked and matching: X− degree 4 `h = 240`, kernel empty, 14,480 s (`a5-xm-d4`); Iso degree 3 `h = 265`, kernel empty, 1,837 s and the 32029 rerun 1,647 s; VB degree 4 `h = 155`, 5,184 s, peak about 2.40 GB (`vb4/receipt-d4.json`); E8 degree 2 `h = 83`, 148 relations, on `e8nm_p1` (13,827 s), `e8nm_p2` (13,743 s), and `e8np_p2` (13,823 s); W8 degree 2 at 32029 `h = 156`, 144 relations, 10,470 s; host E8 `std` 6,029 s and host W8 `std` 5,619 s; `K2` structures in `e8vb.log`, `e8np.log`, `xm.log`, and `xp_p2.log`; W8 Hilbert function 24, 156, 600, 1725; Iso probe 17, 85, 265, 640, degree 23; J radical and prime through the origin on the five `*_J.log` files; arc-report’s two primes, the degree-4 certificate, and the degree-3 non-certificate.

Checked and not matching: “40 of 41 inside `minAssChar`”; VB degree 5 “8.3 GB at 2.5 h” against a recorded 12 GB peak; the `xi_R` settlement against the retained residual list.
