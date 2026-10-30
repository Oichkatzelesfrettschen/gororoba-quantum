# Red-Team Review: final-plan-bundle.md

This is a detailed granular attack of the converged plan across all four pillars: arc families/Jacobian certificates, syzygy/Jacobian-dual probe, VB h4 diagnostic, and compute assignment.

---

## 1. Arc-Family Certificate (Method A: "degree-by-degree membership in J + m P_d")

**Core claim:** The Hilbert function h_d = dim(F(I) / m I^{d+}_t) is the exact degree of the exceptional fiber, obtained by multiplying "kbase" products from F(I)_t and projecting to the quotient by m, then taking F_p-rank.

**F1 — The "A is exact" banner is false.** The method computes dim(Σ_i I_a^{(t)} / m Σ_i I_a^{(t)}) but never proves the images span F(I) / m I_{d+}^t. The bundle never constructs a single matrix whose columns are genuine limits at a point. The text repeatedly says "h_d = rank" without constructing the limit set or ruling out a missing component. At line 118: "Deliverable per pair: dimension, degree, Hilbert series, components" — but the deliverable is a scalar rank over a finite field, not a certificate that every limit lies in the span.

**F2 — F_p-certification does not lift to characteristic zero.** The plan repeatedly declares "h3 = 122 for X-" because F_32009-rank is 122. The only justification is "F_p certifies only those degrees" and "char-0 claims need a second prime". But the bundle never proves that the fiber has the same number of components over every characteristic or that no component of different characteristic weight is collapsed mod p. The X- fiber has a one-dimensional kernel (from S0), but that tells nothing about whether a component of higher multiplicity or a component whose defining form reduces to a different polynomial mod p is present. A degree-bounded certificate requires a bound on the degree in which a characteristic-independent component would appear, which the bundle never provides.

**F3 — "K2 = (K2)_3" does not mean no missing cubic.** At line 159: "No cubic relation lies outside K2. F(I) agrees with k[y]/K2 through degree 3." This is nonsense. The ideal I = (G) in k[x,y]/I_Y defines Z. The fiber F(I) is a quotient of the Rees fiber over the point of Z. k[y]/K2 is a finite-dimensional graded algebra obtained by taking the ambient polynomial ring in the kernel coordinates and modding out the degree-2 relations. Agreeing through degree 3 means no independent cubic is in I that is cubic in y but not in the generating set G. But the fiber can have cubic relations that are combinations of lower-degree generators or that arise from syzygies of G whose coefficient ideal becomes nontrivial in degree 3. The method never checks whether the map F(I) -> k[y]/K2 is injective in degree 3 or whether the fiber has a component whose ideal is not contained in (K2)_3 but is killed by m I^{4}. 

**F4 — V(K2) is an upper bound on what the bundle explicitly states, but the bundle treats it like an equality.** Line 175: "V(K2) is an upper bound for the fiber until degree 3 or method B closes it." But the decision record also says at line 262 that V(K2) has a single prime of projective dimension 3 and degree 12 for X-, of projective dimension 4 and degree 11 for E8-bar->N+. The bundle never eliminates the possibility that the true fiber has more components that are contained in each K2-minimal prime or that the Hilbert polynomial of the fiber has a different leading coefficient than deg(V(K2)). The bundle never produces a scheme-equal certificate.

**F5 — "No missing component" is never proven.** The bundle assumes that if F_p-rank of N d-forms equals the number of products, then there is no missing component. But if a component has no generator in degree d, its class can be hidden. If it is a point in projective space, it is not seen by N d-forms at all. The bundle never checks whether G is saturated or whether the Rees algebra's special fiber is cone over the fiber.

**F6 — The degree-count itself relies on a hidden invariant.** The code counts "normal cubics" by taking N_f elements of F(I) and projecting to a quotient. The size of N must be independent of any generic linear section. The bundle does not show that N doesn't depend on the choice of general coordinates nor on the choice of the point s \in Z on Y. The plan assumes "one-point transport by H-transitivity" is valid, but line 108 rejects the assumption: the split boost has no kernel lift. If the point stabilizer action has nontrivial invariants in the fiber, the fiber decomposes into a sum of representations, and h_d is a sum of dimensions of homs. The bundle never checks the H-module structure of F(I).

**F7 — The degree-3 count for X- is "h3 = 122" but the bundle gives no reason why no quartic component should hide beyond degree 2.** If the fiber has a component of degree 4 and the bundle reports h3 = 122, the component is invisible in degree 3. If it has degree 3, the bundle claims it lies in K2, but the bundle never proves that. The certificate is a partial Hilbert function, not a full certificate.

**F8 — The "local syzygy" approach used in the original runs is explicitly rejected in lines 146 and 188, but the bundle still uses "local ds syzygy" as a cross-check. At line 189, S1 runs a different method but the bundle still quotes the local syzygy as a "cross-check" for X- and W8 even after admitting it killed in degree 3 at X-. The cross-check code is never rebuilt or rerun under the new constraints.

**F9 — Method A never produces a component-by-component description.** The deliverable per pair is supposed to be "components" (line 174), but the bundle only gives a number and an ideal generated by quadratics plus perhaps cubics. No component equations are produced.

**F10 — The X- run used a 72 GB cgroup cap and timed out. The 12G re-run succeeded because the memory cap was lowered, not because the problem changed.** This means the bundle's claim that the method is "exact" and "complete" is based on an underestimate of the needed memory.

---

## 2. Syzygy / Jacobian-dual Probe

**Core claim:** VB has a two-dimensional Jacobian dual presentation (two dim-3 minors of J and each component is a dim-3 scroll), and that the Jacobian matrix minors certify reduced support without saturation.

**S1-J1 — "Syzygy/Jacobian-dual presentation route only with verified hypotheses" is never verified.** Line 322, Section 8(2): "VB as a scheme route only with verified hypotheses." The bundle never verifies any hypothesis. The Jacobian matrix is never explicitly constructed from the partial fiber. The "syzygy" is never verified as a global syzygy (it is a local relation on the Rees algebra's generators, not a syzygy in the fiber). The bundle never writes the Jacobian matrix J and computes its minors. The "Jacobian-dual" is mentioned as a probe, but the bundle never outputs the Jacobian matrix nor asserts that its ideal equals the fiber.

**S1-J2 — The "two dim-3 primes" claim for VB is not justified by a computation.** Line 267: "E8-bar->VB's V(K2) is reducible, which rules out the irreducible 2 x 7 scroll hypothesis." That is a partial argument. The plan claims VB is two 3-planes (dim 3 in projective space), but the bundle never produces a decomposition of the fiber into components and does not compare that decomposition to any other candidate. The claim is inferred from "reducible" and "degree 11 (10+10)" but the degrees of the components are never stated.

**S1-J3 — "J minor-certifies reduced support" is not produced.** The bundle never outputs a matrix J whose minors are the generators of the fiber. The statement at line 332 that "leading minors certify reduced support per component without saturation" is asserted without exhibiting a single concrete Jacobian matrix. The bundle never exhibits a certificate file that contains a Jacobian matrix and proves the ideal generated by its minors equals the fiber ideal.

**S1-J4 — The "nonzero dim-sized Jacobian minor" is a vacuous condition unless J has those minors.** If every (d+1)-minor vanishes for rank d J, then the Jacobian ideal is zero. The bundle never checks whether J has rank d or d+1. It never computes the rank of J on the partial fiber basis.

**S1-J5 — The probe is not invariant under coordinate change on the ambient space of Y.** If one changes the presentation of the fiber by a linear change of coordinates on the ambient polynomial ring in y, the Jacobian matrix changes by a linear invertible transformation. The minors can change degree and the claim that the ideal equals the fiber must be invariant. The bundle never checks that the fiber ideal is invariant under coordinate changes or under the action of the torus group.

---

## 3. VB Degree-4 Diagnostic (VB h4 vs 155)

**Core claim:** The quadratic model has h2 = 34, so one expects h4 = (h2 in 2 variables) × (h_2 in 1 variable) = 54 × 12 = 648, hence h4 = 155, and h4 < 155 implies a new relation in degree 4 is missing.

**S2-D1 — This is a category error: h4 = dim(F(I)_4) is never a product.** The bundle computes h2 = 34 in the fiber (dim F(I) / m I^3). The quadratic model in line 332 uses a product h2 × h_2^t where h_2^t is a 1-variable Hilbert function from "the quadratic model in 1 y-variable". The bundle never defines h_2^t. Line 219 (the E8-bar N+ vs N- sign check) mentions "a quadratic-model count in t of 9 variables," but that is not the h_2 in 1 variable. Line 270 says VB degree 3 gives h4? No, line 270 says E8-bar degree 3 gives h3 = 80. The quadratic model is asserted in line 332 but never exhibited. The quadratic model is never built or checked against the fiber generators in degree 3. There is no evidence that the two generators of the degree-3 part of the fiber have degrees (h2 in t, h_2^t) whose product is 155.

**S2-D2 — The quadratic model is never proven.** The product h2 × h_2^t = 34 × 12 = 408 is not 155 as numbers, but the text asserts 54 × 12 = 648. The product is never derived from any single matrix whose row space is the fiber in degree 3. The quadratic model is never shown to be a subvariety of the fiber, nor is its degree compared to the fiber's degree. The fiber has a dimension of 3 in projective space (line 271: V(K2) proj dim 3, degree 7 for VB). The product 54 × 12 has no geometric meaning in relation to the fiber.

**S2-D3 — VB degree-4 "diagnostic" is not a falsifier, only a heuristic.** A false certificate h4 < 155 is a heuristic that "something is new" but it is not a falsifier of the fiber. The plan treats the quadratic model value 155 as if it were a prediction from a known decomposition. But line 332, 333 says VB h4 is "as a diagnostic" — i.e. a diagnostic, not a certificate. The plan's own stated deliverable at line 174 is "components," not a numeric upper bound.

**S2-D4 — The quadratic model was proposed by CX in the bundle but the bundle never commits to it.** Line 332: "VB h4 vs 155 (quadratic-model value) as a diagnostic: h4<155 exhibits a new relation; equality closes nothing." The bundle presents this as a possible diagnostic but it is not part of the final plan. Line 332 says neither the arc-families method nor the dense-family route claims to know the support of any pair. So the VB h4 probe is not a necessary part of the final plan — it is an optional heuristic. The plan's "converged" answer never includes it.

**S2-D5 — There is no "quadratic-model" ideal.** The bundle never defines a quadratic model ideal. The "quadratic-model" is supposed to be some ideal in 3 variables whose Hilbert function is a product, but no such ideal is specified. There is no proof that the fiber equals that model in any degree, nor that any difference certifies a missing component.

---

## 4. Compute Assignment

**Core claim:** Method B on Azure VM 2 is the best route because it avoids the local-syzygy memory killer, can handle the large fiber, and a 78 GB cap makes it the first complete receipt.

**S3-C1 — "Method B" can stall with the same memory killer as method A.** Line 322: "VB method B (8 GiB, 1 h cap), X- 16, Iso 24, E8-bar N+/N- 48 each, W8 64, E8-bar N- degree 2 24; 296 GiB admission, 1 s RSS sampling, per-job TERM/KILL, streaming receipts." But then at line 330, VM 2 W8 method B reached 13 GB RSS at ~20:38 UTC and the VM stopped answering ssh without any OOM in the kernel log. The cause was unidentified. Line 331 says VM 2 is deallocated, so that job never produced a receipt. The bundle never shows a running Method B job that has not died. The plan's claim that Method B is the "best" is contradicted by the only Method B run of any kind (W8) failing.

**S3-C2 — Azure VM 2's "deallocation by 21:00 UTC" is a resource constraint not a falsifier for correctness.** The plan uses AZURE_VM2_DONOR_CAP=78G (line 330). The bundle uses "16 GiB" as the host-cgroup target for short jobs (lines 138 and 197) and uses a 16 GiB cgroup for W8 method A success (line 130), because memory cap is the only available falsifier. The bundle's resource rules adopt the cgroup caps but never show that a 78G cgroup job has succeeded.

**S3-C3 — The plan never produces a certificate in any memory regime.** Every job so far is either partial (h_d segment) or incomplete (method B stalling). The plan states "completion comes only from method B" (line 198) but Method B is the only route that claims to produce a certificate, and its only run (W8 at 78 GB) aborted without a result. The bundle is incomplete by definition.

**S3-C4 — The "second-prime" plan relies on regeneration at p=32003 vs 32009 but the bundle never shows how to regenerate J from the Q(i) producer at the new prime.** Line 320: "The second-prime harness regenerates all nine inputs from the Q(i) producer." This is an unimplemented path. The bundle never shows code to regenerate J, G at a new prime. It is assumed the producer can be rerun for p=32029. The time cost of an F_32029 run is never measured.

**S3-C5 — The "dense-family arc sampler" is never built and depends on QRNG draws.** Line 321 and line 322: "Dense-family arc sampler unbuilt (needs QRNG draws + ledger rows)." The bundle does not contain a QRNG provider invocation or a ledger-file format in any file read. The QRNG draw is in the repo's "Seeds" policy (line 352), but the bundle never shows what a draw is and how it is incorporated into the arc-families sampler. The plan's core result (an exact arc family) depends on a QRNG draw. If the QRNG is not a uniform draw from the intended space, the arc family can be wrong. The bundle never audits the QRNG source.

**S3-C6 — The plan treats every h_d segment as "exact."** But each job is killed by either OOM or timeout. The partial h_d is exact only up to the killed degree. The bundle never measures the degree at which a memory cap is insufficient. It never measures whether a 78G cgroup would be sufficient for VB h4, nor whether E8-bar h3 can complete. All jobs are partial, and the bundle claims to have "exact" Hilbert functions, which is a false claim.

---

## Five Most Likely Silent Errors in the Reported Results

1. **The "h3 = 122 for X-" result is misleading because the method computes dim(F(I)/m I^4) and not dim(F(I)).** The fiber could have a quartic generator that is not in the span of the cubics and any relation of degree 3. The bundle never checks whether the module is generated in degree <= 3. The result is a partial Hilbert function, not a certificate.

2. **The E8-bar->VB "h = 10, 34, 80" is the output of a run that never produced the generator-ideal (G) as a list of forms.** The run used G as input but did not output G. The "21 quadric relations" at degree 2 is correct (line 235), but the relation-ideal may not equal (G). The bundle computes a quotient by G and then measures the dimension of the fiber, but never confirms that dim(F(I)) / dim(k[y]/K2) is 80. The bundle never checks whether std(L) equals the partial fiber ideal.

3. **The VB "h2 = 34 and V(K2) proj dim 3, degree 7" is an accidental coincidence that could be wrong.** The bundle never gives a basis for K2, nor does it show why K2 has 10 quadratic generators. The fiber ideal is compared to (K2)_2, but the bundle never proves that the fiber is contained in V(K2). The degree 3 job for E8-bar->VB succeeded but the fiber is not described componentwise. The "two dim-3 primes" claim is unverified.

4. **The "no missing cubic in W8" conclusion is a hallucination.** The bundle claims "h3 = 122" for X- and "h2 = 156" for W8, but never certifies that the fiber has no component supported on a lower-dimensional linear space. The bundle never checks that the ideal of the fiber equals the ideal of V(K2). The 144 quadric relations extracted by `probes/relations_nf.py` may come from G and not from the fiber.

5. **The plan assumes that every h_d segment is a certificate of the full fiber.** But the bundle never produces the scheme structure of the fiber, nor does it produce the generator ideal. The "certificates" are scalar integers and ideals without component equations. Any component-missing conclusion (e.g., "the fiber is a single dim 3 prime of degree 7") is unverified.

---

The converged plan fails because Method A never produces a certificate of the fiber, Method B stalls repeatedly, the Jacobian-dual probe is unimplemented, and the VB h4 diagnostic is an unmotivated heuristic. The plan's results are partial Hilbert functions that could be wrong and are never cross-checked against a full scheme equality.
