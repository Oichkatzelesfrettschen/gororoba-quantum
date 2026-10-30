`[O]` denotes a repository observation. `[I]` denotes an inference, proposed procedure, budget, or falsifier.

## Executive conclusion

[O] Method A computes an exact, bounded graded piece of the fiber cone over \(\mathbf F_{32009}\). Every completed degree therefore remains valid evidence. Method B and the candidate-ideal route both enter an unbounded mixed-variable standard-basis calculation after the pivot; six method-B attempts and one candidate-ideal attempt produced no complete fiber. [Decision record](~/Projects/IBMQuantum/docs/local/a5-failed-runs/decision-record.md:243)

[I] The next compute hour should buy either an independent relation-type bound or a dimension-certified family of genuine limits. Another unchanged saturation run only buys a seventh measurement of the same failure.

## 1. Diagnosis

[O] Method A fixes target degree \(d\) before Gröbner work. It forms only the degree-\(d\) target monomials, reduces every product modulo \(J\) factor by factor, computes \(\operatorname{std}(J+\mathfrak mP_d)\) in the source variables, and finishes with exact FLINT rank. [Driver](~/worktrees/IBMQuantum/a5-kernel-attachments/docs/evidence/a5-kernel-attachments/fiber_cone_driver.py:227) [Part B report](~/Projects/IBMQuantum/docs/local/a5-failed-runs/build/part-b-report.md:9)

[O] Method B instead computes \((H:g^\infty)\) before setting the source variables to zero. The mixed rings contain:

| Pair | Source variables | Target variables | Mixed variables |
|---|---:|---:|---:|
| E8bar-to-VB | 8 | 10 | 18 |
| X-minus | 7 | 15 | 22 |
| Iso | 6 | 17 | 23 |
| E8bar-to-N-plus/minus | 9 | 21 | 30 |
| W8-to-N-minus | 7 | 24 | 31 |

[O] The saturation must discover relations of unrestricted target degree while multiplying them by source polynomials. E8bar-to-VB proves that pivot size alone is not the cause: its pivot has only 9 terms, yet saturation stalled for 2 hours and `std(L)` stalled in the 18-variable candidate presentation. Iso used a 41-term pivot; X-minus used 64 terms. [Decision record](~/Projects/IBMQuantum/docs/local/a5-failed-runs/decision-record.md:243) [Part B report](~/Projects/IBMQuantum/docs/local/a5-failed-runs/build/part-b-report.md:31)

[O] Arithmetic occurs over a fixed prime field, so coefficient bit-length does not grow. The observed growth is monomial support, critical pairs, and sparse-matrix fill:

- The old 20-variable E8bar-to-VB graph retained roughly 49,000 pending pairs after peaking near 61,609.
- The msolve graph reached an \(86{,}010{,}243\times87{,}648{,}606\) degree-16 matrix and about 209 GB sampled RSS.
- E8bar-to-N-plus saturation reached 72 GB after 10 hours without passing the pivot stage. [TPU review](~/Projects/IBMQuantum/docs/local/a5-failed-runs/kaggle-tpu/review-codex.md:26) [Decision record](~/Projects/IBMQuantum/docs/local/a5-failed-runs/decision-record.md:252)

[O] Global `dp` ordering is still the correct observed choice. Local `ds` created 2,401 Schreyer generators and reached 83 GB before W8 \(h_2\), whereas global method A completed \(h_2\) in 94 minutes at 6.7 GB. [Decision record](~/Projects/IBMQuantum/docs/local/a5-failed-runs/decision-record.md:106)

[I] The mechanism is therefore unbounded saturation degree plus mixed source-target fill. More RAM changes the failure point; it does not change the asymptotic problem. The logs expose no terminal saturation degree, so assigning one would be fiction.

## 2. Reformulations ranked by expected value

### 1. Genuine arc families with an exact dimension certificate

[I] This route has the highest expected value because it can prove reduced-support equality without computing the Rees ideal.

For each minimal prime \(P_\alpha\) of \(\sqrt{K_2}\):

1. Construct an exact algebraic family \(x(s,u)\) with \(J(x)=0\), \(x(0,u)=0\), and generic \(x(s,u)\) in the intended nullity-8 stratum.
2. Compute
   \[
   \nu=\min_i\operatorname{ord}_sG_i(x),\qquad
   c_i(u)=\left.s^{-\nu}G_i(x(s,u))\right|_{s=0}.
   \]
3. Verify \(c(u)\neq0\) and every generator of \(P_\alpha\) vanishes on \(c(u)\).
4. In a chart \(c_q=1\), exhibit a nonzero \(d_\alpha\times d_\alpha\) minor of
   \(\partial(c_i/c_q)/\partial u_j\), where \(d_\alpha=\dim P_\alpha\).

[I] Irreducibility, containment, and equal image dimension then prove that the image is dense in \(V(P_\alpha)\). One family is required for every component.

[O] The current `dense-family` implementation correctly treats finite points as a support lower bound only. [Certificate code](~/worktrees/IBMQuantum/a5-kernel-attachments/docs/evidence/a5-kernel-attachments/fiber_certificates.py:168)

[I] Falsifiers: a nonzero coefficient of \(J(x)\); generic departure from the source-orbit open set; all leading \(G_i\) equal zero; failure of a component equation; or Jacobian rank below \(\dim P_\alpha\).

### 2. Exact curve sections as an arc-discovery instrument

[I] For a germ of dimension \(r\), intersect \(J\) with \(r-1\) reproducible linear forms through the origin, isolate the one-dimensional components through the origin, normalize each curve, and evaluate \(G\) in every DVR branch above the origin:

```singular
LIB "normal.lib";
ring R=32009,(t(1..e)),dp;
ideal C=J,L(1),...,L(r-1);
if (dim(std(C))!=1) { "bad_section"; quit; }
list normalization_data=normal(C);
```

[I] Each normalization branch supplies a uniformizer \(s\) and therefore a genuine limit point. A truncated jet satisfying \(J\bmod s^M\) is insufficient unless a Hensel or implicit-function certificate proves liftability.

[I] Finite sections remain discovery/lower-bound evidence. Replacing numeric section coefficients by parameters and proving the image-rank condition above turns the construction into a support certificate.

[I] Initial budget: X sections at 3–8 GiB and 15 minutes each; one symbolic three-parameter family at 8–16 GiB and 2 hours. Abort the route if normalization reaches the same frontier as saturation or every image rank stays below three.

### 3. Degree-truncated method A, but only after earning a proof bound

[O] A finite sequence \(h_1,\ldots,h_D\) does not bound future relation degrees. Regularity of \(S/K_2\) says nothing about the unknown kernel \(K_F\supseteq K_2\). [Decision record](~/Projects/IBMQuantum/docs/local/a5-failed-runs/decision-record.md:23)

[I] A proof-producing stop requires one of:

- a theorem, with verified hypotheses, giving relation type \(\operatorname{rt}(I)\le D\);
- an independently certified Hilbert series for \(F(I)\);
- a candidate algebra surjecting onto \(F(I)\) with independently proved equal Hilbert series;
- a verified Cohen–Macaulay/reduction-number theorem yielding \(\operatorname{rt}(I)\le r(I)+1\).

Then run every degree through \(D\), retaining cumulative relation files:

```sh
systemd-run --user --scope \
  -p MemoryMax=8G -p MemorySwapMax=0 \
  "$PYTHON" ~/worktrees/IBMQuantum/a5-kernel-attachments/docs/evidence/a5-kernel-attachments/fiber_cone_driver.py \
  --header HEADER.sing --degree D \
  --previous-relations relations-upto-dPREV.rel \
  --out OUT --prime 32009 --memory-gib 8 --timeout 7200
```

[I] Falsifier: a new relation above the proposed bound, or failure of any theorem hypothesis.

[I] `degBound=D; std(...)` alone is not a saturation certificate. Saturation can require a high power of \(g\) to reveal even a low target-degree relation. A Hilbert-driven stop is circular if the supplied Hilbert series comes from \(K_2\).

### 4. Syzygy and Jacobian-dual presentation

[I] Run the route first on E8bar-to-VB, then X-minus:

```macaulay2
A = (GF(32009)[t_1..t_e])/J;
I = ideal apply(G, g -> sub(g,A));
phi = syz gens I;
degrees source phi
```

[I] Check whether the presentation is linear, whether \(I\) is perfect of the required grade, the \(G_\ell\) Fitting-height conditions, Cohen–Macaulay hypotheses, and the reduction number. Only verified Morey–Ulrich-type hypotheses authorize a Jacobian-dual determinantal presentation.

[I] Without those hypotheses, the syzygy/Jacobian-dual equations define only a candidate \(L\). The candidate must pass the existing checks
\(H\subseteq L\subseteq\ker\phi\), \(L:g=L\), and equality of its special fiber with the proposed \(K\). [Candidate certificate](~/worktrees/IBMQuantum/a5-kernel-attachments/docs/evidence/a5-kernel-attachments/fiber_certificates.py:3)

[O] Linear type is already refuted: the measured nonzero quadratic relation ideals contradict a polynomial special fiber.

[I] Falsifiers: nonlinear presentation without an applicable generalized theorem; failed height conditions; failed colon/kernel checks; or syzygy computation reaching the same memory frontier.

### 5. One bounded Macaulay2 implementation comparison

[I] A bounded `ReesAlgebra` pilot is defensible because Macaulay2 begins with the symmetric-algebra presentation:

```macaulay2
needsPackage "ReesAlgebra";
A = (GF(32009)[t_1..t_e])/J;
I = ideal apply(G, g -> sub(g,A));
Rideal = reesIdeal(I,g);
Fideal = specialFiber(I,g);
```

[O] The installed package still saturates the symmetric ideal. Its declared `DegreeLimit`, `PairLimit`, and related options do not limit `reesIdeal`, so the pilot is an implementation/order comparison rather than a new completion theorem.

[I] Budget E8bar-to-VB at 8 GiB/2 hours and X-minus at 16 GiB/4 hours. Acceptance requires agreement with every certified \(h_d\) and \(K_2\). Timeout, memory exhaustion, or comparable basis growth ends the route.

### 6. Generic projective sections

[I] Generic sections can certify component degrees after component containment and coverage have been established:

```singular
ring Y=32009,(y(1..n)),dp;
ideal S=std(Component,L(1),...,L(dimComponent),y(q)-1);
vdim(S);
mult(S);
```

[I] Run the resulting zero-dimensional systems through Singular or msolve and repeat at a correctly regenerated second split prime. Section counts alone cannot establish component coverage; one component can be absent while another carries multiplicity.

### 7. SAGBI or initial-algebra degeneration

[I] Plain SAGBI on \(k[G_1,\ldots,G_n]\) computes relations \(f(G)=0\), whereas the fiber relation is \(f(G)\in J+\mathfrak mI^d\). Plain SAGBI therefore addresses the wrong algebra.

[I] A filtration-aware initial-Rees/SAGBI route becomes valid only after proving a flat degeneration and a finite SAGBI basis. Normaliz or 4ti2 becomes relevant only after that proof produces a semigroup presentation. A truncated SAGBI run remains diagnostic.

### 8. Multimodular reconstruction and Hensel lifting

[O] `fiber_inputs.py` can regenerate the inputs at \(p=32029\), root \(9115\). Replacing `32009` inside a specialized input is invalid. [Decision record](~/Projects/IBMQuantum/docs/local/a5-failed-runs/decision-record.md:242)

[I] Once any full modular ideal is available:

1. Repeat at several good split primes.
2. Require stable leading monomials and Hilbert series.
3. CRT/rationally reconstruct coefficients in \(\mathbf Q(i)\).
4. Verify all identities by exact substitution and ideal membership over \(\mathbf Q(i)\).

[I] Multimodular work detects bad primes and lifts a completed basis; it does not reduce the per-prime saturation frontier. Classical Hensel lifting offers little for the unresolved positive-dimensional ideal before such a basis exists.

## 3. What \(h_d\) and \(K_2\) decide now

[O] Every row below is certified only over \(\mathbf F_{32009}\). [Decision record](~/Projects/IBMQuantum/docs/local/a5-failed-runs/decision-record.md:181)

| Pair | Present conclusion | Exact extra fact closing reduced support |
|---|---|---|
| X-plus/minus | \(h=15,51,122\); \(K_2\) is nonradical; \(\sqrt{K_2}\) has one component of dimension 3, degree 12 | Prove \(\dim\operatorname{Proj}F=3\), equivalently construct one dense three-dimensional family of genuine limits. Irreducibility then forces support equality. Scheme equality still needs a relation bound or Rees certificate. |
| E8bar-to-VB | \(h=10,34,80\); \(K_2\) is radical with dimension-3 components of degrees 3 and 4 | Produce a dense rank-3 genuine-limit family in each component. Alternatively prove independently that the reduced fiber is pure dimension 3, contained in \(V(K_2)\), and has total degree 7 with component coverage. |
| E8bar-to-N-plus | \(h=21,83\); nonradical \(K_2\) has components \((4,11)\) and \((3,4)\) | Produce dense families of dimensions 4 and 3 in the respective components, or prove \(\sqrt{K_F}=\sqrt{K_2}\) directly. A dimension-4 witness alone says nothing about the lower-dimensional component. |
| E8bar-to-N-minus | Same measured \(h_1,h_2\), but a distinct input ideal | Same component analysis must be performed independently until an actual local/fiber isomorphism is proved. |
| Iso, W8 | Certified Hilbert segments, but radical/minimal-prime calculations did not finish in 600 seconds | First decompose \(\sqrt{K_2}\); then certify a dense genuine-limit family in every minimal component, or compute \(\sqrt{K_F}\) directly. |

[I] None of the present Hilbert segments decides reduced support by itself.

## 4. Arc-sampler receipt required for `support-equal`

[I] Extend the certificate format to bind:

- source-header SHA256 and field;
- exact section or explicit arc equations;
- branch prime and normalization/DVR map;
- proof that the branch lies in \(Y\), approaches the origin, and generically leaves the center;
- common valuation \(\nu\) and leading target coordinates;
- component-prime SHA256 and exact containment;
- parameter-space irreducibility;
- nonzero Jacobian minor or exact generic-fiber dimension;
- second-prime replay and separability check in positive characteristic.

[I] `fiber_certificates.py` may report `support-equal` only after every candidate component has such a receipt. Numeric samples alone must continue to report `support lower bound`.

## 5. Compute plan

| Rank | Substrate and work | Cap and deadline | Falsifier |
|---:|---|---|---|
| 1 | Host: finish radical/minimal-prime structure for \(K_2\); X arc-family discovery and dimension certificate | One job, 3–8 GiB initially; 15–60 min probes, at most 16 GiB/2 h for a symbolic family | Decomposition or family reaches the saturation-like frontier; image rank \(<3\) |
| 2 | Host: conditional relation-bound and syzygy/Jacobian-dual checks on VB, then X | 8 GiB/1 h VB; 16 GiB/2 h X | Required theorem hypotheses fail or syzygies show no smaller presentation |
| 3 | Host: one M2 symmetric-presentation pilot | 8 GiB/2 h VB; 16 GiB/4 h X | Same basis growth, timeout, or disagreement with certified degrees |
| 4 | Host or GitHub Actions: producer-regenerated second-prime method-A degrees and exact receipt verification | GitHub Actions 8–12 GiB, 30 min–2 h; host within the 24 GiB aggregate admission target | Any regenerated \(h_d\), relation dimension, or membership check differs |
| 5 | Kaggle CPU: one measured method-A degree, normalization batch, or zero-dimensional section | 24 GiB working budget; 10 h solver deadline within 12 h | Queue/setup/export cost loses to host, memory exceeds 30 GB, or outputs are not recoverable |
| 6 | Azure FX4mds_v2: only a reformulated computation whose host measurement requires more than 24 GiB | One 60–72 GiB job per VM, 6–10 h, zero swap, independent deallocation deadline | New formulation reproduces the post-pivot curve of the failed saturation |
| 7 | Kaggle TPU VM used as a large CPU host: several independent, receipt-producing reformulations only after smoke allocation | Keep aggregate RSS below roughly 296 GiB; 4 h pilot inside the 9 h session | Queue starvation, missing intermediate receipts, or another batch of unchanged timeouts |
| 8 | GitHub Actions: deterministic checks only | 16 GB runner ceiling | Any discovery job approaches the runner ceiling or ordinary pull-request latency |

[O] All host and Azure jobs require cgroup `MemoryMax`, `MemorySwapMax=0`, a live wall deadline, `MALLOC_ARENA_MAX=2`, and aggregate admission accounting. Kaggle requires a process-tree RSS watchdog. `RLIMIT_AS` is unsuitable. [Compute flags](~/Projects/IBMQuantum/docs/runbooks/compute-flags.md:46)

## 6. Stop doing

- [O] Stop extending unchanged Singular pivot saturation. Six runs ranging from the smallest VB case to E8bar at 72 GB/10 h stopped after the pivot.
- [O] Stop extending unchanged `std(L)` candidate-ideal runs. The 18-variable VB candidate failed before any colon or comparison check ran.
- [O] Stop full Rees-graph msolve elimination. The degree-16 matrix already consumed about 209 GB, while projected degree 19 exceeded the session envelope without a termination bound.
- [O] Stop local-`ds` syzygy routes. Global method A has already dominated them by orders of magnitude.
- [I] Stop W8 degree 3 unless a named finite-degree question needs \(h_3\). The computation cannot close the fiber without an independent bound.
- [O] Stop `minAssGTZ` on the large quadratic ideals. Radical followed by `minAssChar`, preferably in projective charts, is the supported route; GTZ densification remains an inference.
- [O] Stop every `prlimit --as` or inherited `RLIMIT_AS` memory cap.
- [O] Stop deadline extensions implemented by suspending `timeout`; replace the active timer while leaving the supervisor runnable.
- [I] Stop generic-line, finite-arc, or second-prime results from being described as completion evidence. Those procedures supply diagnostics, lower bounds, or arithmetic reproducibility until an explicit equality theorem closes the gap.

The strongest next milestone is a three-dimensional genuine-limit family dense in X’s unique reduced quadratic component. The certificate would settle X’s reduced attachment support at a fraction of the demonstrated saturation cost while preserving the unresolved nilpotent and characteristic-zero questions explicitly.

