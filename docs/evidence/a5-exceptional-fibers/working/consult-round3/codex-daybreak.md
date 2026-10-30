The review covers computational algebraic geometry over finite fields, exact Hilbert-function calculations, positive-dimensional primary decomposition, and topology inferred from kernel bundles. I read all three named documents and the bounded raw logs; I ran no solver and changed no file.

## 1. Failure mechanisms and a cheaper \(h_d\) test

The label “products stage” is misleading. The failures occur inside the same wrapper, but product construction is rarely the expensive operation.

| Failure | First-principles cause | Evidence |
|---|---|---|
| E8-bar to VB, degree 5 | `std(J + mP_5)` suffers Gröbner-basis fill-in after \(8\times266=2128\) maximal-ideal multiples are appended. The 266 products themselves took 8.723 s. The remaining 12 hours occurred after product construction. | [d5-products.log](~/Projects/IBMQuantum/docs/local/a5-failed-runs/build/logs/mine/vb5/d5-products.log:1) records 266 targets, 8.723 s of products, exit 124, and a 12 GiB peak. The brief’s 8.3 GB at 2.5 hours is an intermediate observation, not the peak. |
| Iso, degree 4 | The same `std(J + mP_4)` explosion. Its 640 products took 32.260 s, under 0.1% of the ten-hour budget. | [d4-products.log](~/Projects/IBMQuantum/docs/local/a5-failed-runs/distribute/out/a5-iso-d4/iso_p1/d4/d4-products.log:1). |
| W8 to N-minus, degree 3 | The 600 products took 443.657 s. The subsequent standard basis for \(J+mP_3\), containing \(7\times600=4200\) maximal-ideal multiples before basis growth, exhausted the 30 GB session and received signal 9 after 18,999 s. | [d3-products.log](~/Projects/IBMQuantum/docs/local/a5-failed-runs/distribute/out/a5-p2-w8/w8_p2/d3/d3-products.log:1) and [summary.json](~/Projects/IBMQuantum/docs/local/a5-failed-runs/distribute/out/a5-p2-w8/summary.json:18). |
| Chart runs | Twenty-three charts completed `radical`; decomposition of those radicals then stalled. Seventeen charts did not even emit the radical-completion marker. Positive-dimensional characteristic-set decomposition, plus radical computation on the remaining charts, exceeds 45 minutes. | Iso has 9 radical markers; W8 has 14, including the sole completed chart. |
| TPU smoke job | Queue admission failed. Singular cannot use the TPU, so even successful assignment would merely provide a CPU host. | The recorded job remained unassigned for 24 hours. |
| Pivot saturation | Saturation of a global Rees presentation creates elimination fill-in and reached 72 GB without completing. Raising RAM only enlarges the same search. | [findings, lines 49–60](~/Projects/IBMQuantum/docs/local/a5-failed-runs/consult-round3/a5-exceptional-fiber-findings.md:49). |
| Candidate-ideal verification | Computing `std(L)` in 18 variables is another global Gröbner basis, not a cheap containment check. | [findings, lines 62–63](~/Projects/IBMQuantum/docs/local/a5-failed-runs/consult-round3/a5-exceptional-fiber-findings.md:62). |
| Full Rees graph with msolve | Macaulay-matrix growth is fatal: degree 16 reached roughly \(86\text{M}\times88\text{M}\) and 209 GB. | [findings, lines 65–67](~/Projects/IBMQuantum/docs/local/a5-failed-runs/consult-round3/a5-exceptional-fiber-findings.md:65). |
| Direct `minAssGTZ` | The generic-coordinate/global-basis route densifies the presentation. The timeout is measured; densification as the precise cause remains an inference rather than an instrumented result. | [findings, lines 69–70](~/Projects/IBMQuantum/docs/local/a5-failed-runs/consult-round3/a5-exceptional-fiber-findings.md:69). |

Successful jobs confirm the diagnosis: `std_ms` accounts for approximately 95–99% of the wrapper time for Iso degree 3, X-minus degree 4, W8 degree 2, E8-bar degree 2, and VB degree 4. The separate relation-membership check is smaller and never started in the three failed degrees.

Recommendation: replace `std(J+mP_d)` with a matrix-free kernel test for
\[
\phi_d:(k[y]/K_2)_d\longrightarrow I^d/\mathfrak mI^d.
\]
Use the \(K_2\)-normal monomials as the domain basis, represent multiplication by the \(G_i\) through sparse multiplication operators in an \(m\)-adic Macaulay-dual computation, and impose the annihilation constraints for \(\mathfrak mI^d\) without materializing the ideal \(J+\mathfrak mP_d\). A certified left inverse or nonzero full-rank minor proves that no new degree-\(d\) relation exists; rank loss returns an explicit relation. Jet truncation must carry an Artin–Rees or stabilization certificate—repeated numerical stability alone is insufficient.

Falsifier: the method fails to reproduce every existing certified value \(34,80,155\), \(51,122,240\), \(85,265\), \(83\), and \(156\), or its claimed full-rank certificate fails direct substitution into \(I^d/\mathfrak mI^d\).

For E8-bar to VB, an even cheaper route exists: certify arcs dominating the degree-3 component. Since \(K_2\) is radical and the degree-4 component is already reached, dominance on both components would make the fiber support all of \(V(K_2)\). A homogeneous fiber ideal strictly larger than the radical ideal \(K_2\) would remove part of that support, so this establishes equality in every degree and retires degree 5.

Falsifier: the remaining charts fail to reach the degree-3 prime, or a proposed arc fails exact containment or generic-rank checks.

## 2. Iso and W8 decomposition route

Recommendation:

1. Abandon 41 independent coordinate-chart decompositions. Select a generic linear form \(\ell\), dehomogenize at \(\ell=1\), and prove coverage using saturation and degree accounting. Add a second generic chart only if the first saturation leaves a component in \(\ell=0\).
2. Compute and retain the radical once per chosen chart.
3. Run a factorizing standard-basis decomposition such as `facstd` on that radical, then run `minAssChar` independently on the smaller branches. Verify that the branch intersections recover the radical.
4. For W8, first homogenize and verify the linear prime from chart 10, then quotient or saturate it away. The residual is the actual hard problem; asking `minAssChar` to rediscover the known linear component in every chart wastes most of the search.
5. Admit the result only after every returned prime contains \(K_2\), the intersection equals the radical, and dimension and degree sums match the projective Hilbert data.

Estimated envelopes, explicitly not measurements because the chart logs contain no per-process RSS:

- Iso branches: 3–12 hours, estimated 8–24 GiB each.
- W8 residual branches: 6–12 hours, estimated 16–48 GiB each.
- Azure cap: 64 GiB per VM, leaving operating-system headroom on the 84 GiB machines.
- A 45-minute pilot remains useful only to identify which factorization branches are cheap; it is not a decomposition attempt.

Falsifier: `facstd` returns one branch with essentially the original basis complexity, a branch reaches 12 hours or 64 GiB without a factor, saturation exposes a missed component, or the reconstructed intersection/dimension/degree checks fail.

## 3. Strongest structural lever

The strongest proved lever is the exact sign symmetry:

- X-plus is obtained from X-minus.
- W8 to N-plus is obtained from W8 to N-minus.
- E8-bar does not obey that symmetry.

That exact coefficient identity removes two entire fiber computations and their arc/decomposition replays. Its falsifier is a single generator or germ-ideal coefficient that fails the stated substitution; the documents report that this occurs for E8-bar through the rank-41-of-42 mismatch.

The most valuable surviving pattern is broader but remains conjectural: every computed degree agrees with \(k[y]/K_2\). The pattern lets each new degree ask only whether \(\phi_d\) has a kernel, rather than recomputing a global Rees ideal. For radical \(K_2\), dominant arcs on every component can replace all later degree checks. For nonradical X-minus and E8-bar to N-plus, arcs certify only reduced support; the nilpotent structure still needs a scheme-level certificate.

Second-prime agreement is a robustness check, not a structural theorem and not a characteristic-zero proof. Its falsifier is any differing Hilbert value or component invariant at another good prime.

## 4. Cloud-first assignment

All Azure items require separate written cases. The assignments authorize no launch.

| Work | Substrate and envelope | Reason and stop/falsifier |
|---|---|---|
| W8 degree 3 | Azure eastus, 12 h, 64 GiB | Only listed machine above the observed 30 GB failure. Run the matrix-free formulation first. Stop if it exceeds 64 GiB, fails known degree 2, or produces no certifiable rank progress by 12 h. |
| Iso degree 4 | Azure westus2, 12 h, 48 GiB | Ten-hour Kaggle failure was time-bound after 32 s of products. Stop on failure to reproduce degrees 2–3 or absence of a rank/kernel certificate. |
| X beyond degree 4 | Azure after Iso, 12 h, 32–48 GiB; compute X-minus only | Sign symmetry eliminates X-plus. Stop if known \(h_4=240\) does not replay or the new formulation reaches the cap without a certificate. |
| VB degree 5 | Hold rather than rerun. Assign remaining arc charts to Kaggle CPU or qBraid first. Azure fallback: 12 h, 24 GiB. | Dominating the degree-3 component would settle all degrees. Run degree 5 only if the arc route is falsified. |
| Iso/W8 decompositions | Both Azure VMs, one factor branch per VM, 12 h and 64 GiB | Positive-dimensional decomposition needs memory headroom and independent branches. Stop conditions are the decomposition falsifiers above. |
| E8-bar to N-minus \(K_2\) structure | Kaggle CPU, 2 h, 8 GiB initial cap; extend to 12 h/24 GiB only with progress | N-plus and VB structures fit small measured caps. Falsifier: radical/minimal-prime stages exceed the pilot without producing a retained intermediate. |
| Remaining VB arcs and X-minus arc | Kaggle CPU sessions; qBraid for low-memory long charts; estimate 1–6 h and under 8 GiB per chart | Independent exact charts parallelize naturally and require CPU, not GPU. Falsifier: containment, branch smoothness, or generic-rank failure. |
| Kernel-plane limits | Kaggle CPU, estimate 0.5–2 h and under 8 GiB per arc family; host only for final short replay | Exact `cd_core` kernel and valuation linear algebra should be small. Falsifier: generic nullity differs from 8, the normalized limit depends on truncation order, or Plücker coordinates fail the Grassmannian relations. |
| Component group, 96 unknowns | Kaggle CPU for equation construction and linear reductions, 1–4 h/16 GiB; Azure 12 h/64 GiB only for the residual polynomial branches | Stage the problem before any Gröbner search. Falsifier: a component outside the visible \(S_3\times\mathbb Z_2\), or failure of a candidate to transport every kernel representative. |
| Nullity-4 Gauss map | Kaggle CPU for pooled sampling, 1–6 h/8 GiB per stratum; Azure for exact transition and class calculations, 4–12 h/32 GiB | Sampling locates charts; exact transitions establish classes. Falsifier: rank above the claimed generic 16, a transition outside the claimed structure group, or differing characteristic classes on overlapping charts. |

AWS’s 8 GiB maximum is unsuitable for every failed algebra job. GitHub Actions should run only bounded verification below six hours and 16 GB. The build host should retain short exact replays and validation; its 37 GB free-memory observation does not provide safe headroom for W8 or decompositions under the session-wide OOM policy.

## 5. Unsupported conclusion

The clearest wrong line is:

> “40 of 41 charts stopped at the 45-minute cap inside `minAssChar`”

—[a5-exceptional-fiber-findings.md:215](~/Projects/IBMQuantum/docs/local/a5-failed-runs/consult-round3/a5-exceptional-fiber-findings.md:215)

The same sentence says only 9 Iso and 14 W8 charts produced radical certificates. The raw summaries agree: 23 timed-out charts emitted `radical 1`, 17 emitted only their dimension, and W8 chart 10 completed. Therefore the evidence supports:

- 23 charts reached `minAssChar` and timed out there;
- 17 timed out before radical completion;
- one completed.

Calling all 40 failures `minAssChar` failures assigns a measured bottleneck to 17 runs that never established entry into that stage.

Falsifier of this correction: raw stage logs showing that those 17 jobs entered `minAssChar` before emitting the radical marker. The supplied summaries contain no such evidence.

## Claims checked in the files

Checked directly against raw files:

- target counts and product times for VB degree 5, Iso degree 4, and W8 degree 3;
- exit 124 versus signal 9;
- VB degree-5 12 GiB peak;
- successful-stage time division among product construction, `std`, final reduction, membership, and linear algebra;
- certified Hilbert values in retained receipts;
- counts of chart radical markers and the sole completed W8 chart;
- the documents’ open/settled status for arcs, kernel-plane limits, component group, and nullity-4 work.

Read and logically reviewed, but not replayed:

- the exact sign-symmetry coefficient checks;
- minimal-prime dimensions and degrees;
- formal-arc interpolation and dominance;
- second-prime input regeneration;
- the stabilizer computation supporting nontriviality of \(\xi_R\);
- the 96-variable centralizer reduction.

Those claims remain record claims in this review because the instructions prohibited solver runs. The review performed only read commands and made no file edit.

