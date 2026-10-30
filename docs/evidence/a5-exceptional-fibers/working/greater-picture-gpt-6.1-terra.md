The best next attempt is to construct **exact families of arcs for E8-bar→VB and X−**, then certify that their images are dense in every component of the quadratic upper bound. That route can establish reduced support without computing the full Rees ideal. It does not establish the fiber scheme, its multiplicities, or the attaching map itself.

The next scheme-level attempt should use independently justified relation bounds or a verified presentation of the Rees algebra. The current finite Hilbert-function measurements do not supply either bound. All computational recommendations below are proposals; this consultation ran no algebra jobs.

**Evidence labels:** “Observed” identifies a result recorded in the named file. “Inferred” identifies a mathematical consequence or a proposed experiment whose outcome remains open. Costs for new procedures are budgets, not measured runtimes.

## 1. Diagnosis

**Observed — [decision record, sections 5–9](~/Projects/IBMQuantum/docs/local/a5-failed-runs/decision-record.md:65):** Method A works one degree at a time. It reduces products modulo the slice ideal \(J\), computes a global standard basis of \(J+\mathfrak m I^d\), and takes an exact finite-field rank. Its measured sizes include:

- X−: 122 normal cubic products; \(h_3=122\) in 598 seconds.
- Iso: 265 normal cubic products; \(h_3=265\) in 1,054 seconds.
- E8-bar→N+: 231 quadratic products; \(h_2=83\) in 6,029 seconds.
- W8→N−: 300 quadratic products; \(h_2=156\) in 5,619 seconds, with 6.7 GB peak.
- E8-bar→VB: 80 normal cubic products; \(h_3=80\) in 406 seconds.

**Observed — [method-B template](~/Projects/IBMQuantum/docs/local/a5-failed-runs/templates/b_body.sing:1) and [decision record](~/Projects/IBMQuantum/docs/local/a5-failed-runs/decision-record.md:181):** Method B forms \(H=J+(g y_j-G_jy_q)\) in the combined slice and target variables and computes \(H:g^\infty\) before setting the slice variables to zero. VB has eight slice and ten target variables; its candidate-ideal computation stalled in 18 variables. The selected pivots contain 64 terms for X−, 41 for Iso, and nine for VB. E8-bar→N+ reached 72 GB during a ten-hour saturation attempt.

**Inferred:** The decisive difference is **all-degree elimination before specialization**. Saturation must resolve relations involving slice variables and target variables, including intermediate relations that disappear when the slice variables are set to zero. Method A discards that all-degree burden and asks only for one finite quotient. The combined variable count and repeated critical-pair reductions provide a concrete mechanism for the growth; the logs do **not** establish the saturation exponent or maximum degree needed for completion.

**Observed — [compute-flags runbook](~/Projects/IBMQuantum/docs/runbooks/compute-flags.md:1):** The older E8-bar→N+ graph elimination reached an F4 matrix of 407,116 by 432,548 at degree seven. The VB TPU-VM graph reached an 86,010,243 by 87,648,606 sparse matrix at degree 16 and approximately 209 GB sampled peak RSS; it returned no basis ([TPU review](~/Projects/IBMQuantum/docs/local/a5-failed-runs/kaggle-tpu/review-codex.md:1)). Those are graph-elimination measurements, not measurements of the pivot saturation’s hidden degree.

**Inferred:** Coefficient *bit-length* growth is not the explanation for these \(\mathbf F_{32009}\) runs: coefficients remain in a fixed finite field. Polynomial density, monomial count, pair selection and intermediate matrix size can grow enormously. Global `dp` helps the measured degree-wise membership problem; it does not guarantee a cheap saturation. Before attributing a future stall to a particular degree, retain `option(prot)` output or an equivalent solver trace with pair counts, leading degrees, RSS and elapsed time.

## 2. Ranked completion routes

### 1. Exact arc families and component dimensions — support certificate

**Inferred; first target VB, then X−.** For each prime component \(C\) of \(V(K_2)\), construct a rational parameter family of formal or algebraic curves \(t(s,u)\) satisfying
\[
t(0,u)=0,\quad J(t(s,u))=0,\quad
G(t(s,u))=s^e\bigl(F(u)+O(s)\bigr),\quad F(u)\ne0.
\]
The projective point \([F(u)]\) is then a genuine limit. Prove that its image is dense in \(C\). Since the certified quadrics contain the fiber, doing so for **every** minimal component proves equality of reduced projective supports.

A checkable pilot is:

```text
1. Choose polynomial or rational t_i(s,u), with denominators nonzero on a named open set.
2. In F_32009[u,s], reduce every J_i(t(s,u)); require exact zero.
3. Find the common lowest s-order e of the G_i and extract F_i(u).
4. Reduce every generator of C at F(u); require exact zero.
5. On the chart F_q != 0, compute the exact rank of
   d(F_i/F_q)/d(u_j) over F_32009(u).
6. Exhibit a nonzero maximal minor and an open parameter point satisfying
   all denominator and leading-coefficient conditions.
```

A Jacobian rank equal to \(\dim C\) proves image dimension at least \(\dim C\); containment gives the reverse inequality. In characteristic \(p\), a deficient Jacobian can reflect inseparability, so a low rank fails this certificate rather than proving the image too small. An alternative is an exact graph-ideal calculation proving the image dimension.

**Falsifiers:** a nonzero substituted \(J_i\); all leading \(F_i\) zero; a component polynomial nonzero on the family; a zero claimed maximal minor; or an image dimension smaller than the component dimension. A finite list of sampled points cannot establish density.

**Budget:** host, 3–8 GiB and 10–30 minutes per symbolic pilot; increase only after observing the actual polynomial sizes. VB has two known components of dimensions three and degrees three and four; X− has one arithmetic prime of dimension three and degree 12. Those small decompositions make them the best first targets. The dimensions and degrees belong to the **quadratic upper bound**, not yet the fiber ([decision record](~/Projects/IBMQuantum/docs/local/a5-failed-runs/decision-record.md:181)).

### 2. Lifted relations with a certified saturation-free presentation — scheme certificate

**Inferred:** The existing candidate criterion is sound if its checks finish. Construct a candidate \(L\) containing \(H\), verify by substitution that \(L\subseteq\ker(y_j\mapsto aG_j)\), and prove \(L:g=L\). Then \(L\) is the Rees ideal. Specialize \(t=0\) and compare the resulting ideal with the proposed fiber ideal. The implementation and exact checks are in [fiber_certificates.py](~/worktrees/IBMQuantum/a5-kernel-attachments/docs/evidence/a5-kernel-attachments/fiber_certificates.py:1).

The productive change is to seek a **structured presentation**, rather than immediately repeat `std(L)`: compute low-degree syzygies of \(G\), inspect their coefficient matrices, and test whether a Jacobian-dual or determinantal presentation has a theorem whose hypotheses can be checked for the actual quotient ring and ideal. Verify all hypotheses—including grade, dimension and torsion conditions—before invoking such a theorem. A Jacobian dual or linear-type claim does not follow from the measured \(h_d\).

**Falsifiers:** a proposed generator survives substitution, a required grade or depth hypothesis fails, `quotient(L,g)` contains an element outside \(L\), or the specialized ideal disagrees with a certified method-A degree.

**Budget:** VB first on the host, 3–8 GiB and 30–60 minutes for syzygy and hypothesis probes; only promote a presentation with a substantially smaller verified intermediate problem. **Observed:** the existing 18-variable `std(L)` timed out at 500 seconds and reached its 3 GiB cap after 14 minutes ([decision record](~/Projects/IBMQuantum/docs/local/a5-failed-runs/decision-record.md:243)).

### 3. Bounded degree calculations — scheme certificate only with an independent bound

**Inferred:** Let \(K\) be a candidate homogeneous fiber ideal. If an independent theorem or certificate proves that the actual kernel is generated in degrees at most \(D\), then method A through \(D\), together with equality \(K_d=\ker_d\) for every \(d\le D\), proves \(K=\ker\). A certified regularity bound for the **unknown kernel**, or another valid relation-type bound, can supply \(D\). Regularity of \(K_2\) alone cannot.

A practical experiment is to compute VB degree four using the driver, retaining the ordered monomials, exact normal forms, rank and relation witnesses. Compare its rank with 155, the recorded degree-four Hilbert value of the quadratic model. A smaller rank exhibits a new relation; equality supplies one further degree only.

**Falsifier:** \(h_4<155\) refutes the assertion that VB’s quadrics generate its relations through degree four. A result \(h_4=155\) does not prove an all-degree stop. A degree-truncated standard basis is similarly a proof only after a separately verified bound covers every potentially necessary relation and every reduction needed by the claimed certificate.

**Budget:** host, 4–8 GiB, initial 1-hour wall limit; the preceding cubic took 406 seconds. Escalate only with stage and memory measurements.

### 4. Initial algebra or SAGBI — conditional, potentially decisive

**Inferred:** Work with the subalgebra generated by \(G_i z\) in \((k[t]/J)[z]\), using an explicitly specified compatible valuation or term order. If a finite SAGBI basis is produced **and all subduction tests terminate at zero**, its initial algebra gives a presentation and Hilbert series of the Rees algebra. Deriving the special fiber additionally requires proving that the degeneration and specialization commute, for example through an appropriate flatness or filtered-module certificate.

**Falsifiers:** a nonzero unreduced subduction, an unverified infinite completion, or a specialization/Hilbert mismatch with method A. Matching leading monomials in a finite prefix is not a SAGBI certificate.

**Budget:** VB host, 3–8 GiB and 30 minutes for a feasibility probe. Defer larger pairs until a finite basis and specialization argument exist.

### 5. Linear sections, lines, alternate solvers and multiple primes — supporting tools

- **Inferred:** A generic projective linear section can help measure a candidate component’s dimension or degree. A certified section needs an exact genericity condition and must meet every relevant component; it does not by itself prove that an unknown fiber fills that component. A generic line in the **slice** may miss exceptional directions that require nonlinear or higher-order arcs.
- **Inferred:** M2 or msolve is useful if it implements a materially different presentation or an exact bounded linear-algebra problem. Changing the solver on the same full graph is a comparison experiment, with weak expected value given the retained failures.
- **Observed — [decision record](~/Projects/IBMQuantum/docs/local/a5-failed-runs/decision-record.md:174):** A second split prime requires regenerating \(J,G\) from the Gaussian-rational producer, rather than changing the prime in specialized input text. The input harness emitted \(p=32029\), root \(9115\), as well as the second root at \(32009\).
- **Inferred:** Matching primes is a valuable diagnostic, but neither two matching primes nor Hensel lifting alone proves the characteristic-zero answer. A characteristic-zero certificate needs exact lifted identities and a justified specialization/flatness argument, including excluded denominators and bad primes.

## 3. What the quadratic models already decide

**Observed — [decision record, quadratic structure table](~/Projects/IBMQuantum/docs/local/a5-failed-runs/decision-record.md:181):**

| Pair at the recorded point | Certified data over \(\mathbf F_{32009}\) | What closes reduced-support equality |
|---|---|---|
| X−, and X+ by the checked sign change | \(h_1,h_2,h_3=15,51,122\); \(V(K_2)\) has one arithmetic prime, dimension 3, degree 12; \(K_2\) is nonradical | A genuine limit family whose closure has dimension 3 inside that prime, or another proof that the fiber has dimension 3. |
| E8-bar→VB | \(10,34,80\); \(K_2\) is radical with two primes, both dimension 3, degrees 3 and 4 | A dense genuine limit family in **each** component, or an equivalent containment certificate for each. Dimension 3 alone could select only one component. |
| E8-bar→N+ | \(21,83\); \(K_2\) has primes of dimensions 4 and 3, degrees 11 and 4; \(K_2\) is nonradical | Dense genuine limits in both components. A dimension-4 family alone leaves the separate dimension-3 component unresolved. |
| E8-bar→N− | \(21,83\) | Compute and certify its own \(K_2\) decomposition, then cover each component. Matching \(h_1,h_2\) does not identify its ideal with N+. |
| W8→N−, and N+ by the checked sign change | \(24,156\); quadratic model dimension 5, degree 50; decomposition unfinished | Certified minimal primes plus a dense limit family in every component. |
| Iso | \(17,85,265\); decomposition unfinished; quadratic-scheme degree 23 | Certified minimal primes plus a dense limit family in every component. |

**Inferred:** The measurements alone decide reduced support for **none** of these nullity-8 pairs. In X−, irreducibility of the quadratic upper bound makes a dimension-three lower bound especially valuable. Arithmetic primality over \(\mathbf F_{32009}\) is not a claim of geometric irreducibility over its algebraic closure; base-field and geometric support must be named separately.

## 4. Arc sampler and certificate interface

**Observed:** The current [dense-family implementation](~/worktrees/IBMQuantum/a5-kernel-attachments/docs/evidence/a5-kernel-attachments/fiber_certificates.py:168) tests supplied points against component equations and returns a lower-bound status. It does not verify that supplied points came from arcs or compute image dimension. The earlier [build review](~/Projects/IBMQuantum/docs/local/a5-failed-runs/build/codex-review.md:1) identified a metadata-only equality defect; the inspected function now documents and implements the lower-bound restriction.

**Inferred — proposed contract:**

1. Store the exact input hash, prime and root, ordered \(J,G\), component ideals, parameter ring, arc formulas, denominators and open conditions.
2. Verify \(J(t(s,u))=0\) exactly. A truncated numerical or formal solution alone needs a separate exact lifting/existence proof.
3. Verify a common leading order and nonzero leading vector, then retain \(F(u)\) and the projective chart.
4. Verify component containment and an exact dimension witness: a nonzero Jacobian minor of the required size, or a certified image ideal and dimension.
5. Verify that the component list is complete and consists of the certified minimal primes of the upper bound. Require one valid dense-family witness per component.
6. Only after those checks return `support-equal`; otherwise return `support-lower-bound`, `refuted`, or `unverified`, with the failed check identified.

Random parameter values can discover candidate families or supply sanity checks; they cannot prove density. A deterministic symbolic family avoids a new random seed. If randomized exploration is later used, the repository’s QRNG provenance and provider-approval rules apply.

**Falsifier for the checker:** an empty point list, fabricated dimension metadata, a family with \(J(t)\ne0\), a vanishing claimed minor, an omitted upper-bound component, or a changed input digest must never return `support-equal`.

## 5. Compute assignment and stop rules

**Observed:** The host has 62 GiB RAM and had a memory-pressure incident; the program adopted approximately 24 GiB of reachable concurrent caps. Azure has one approximately 82 GiB FX4mds_v2 VM per listed region. Kaggle CPU has about 30 GB; the TPU VM supplied a much larger CPU-memory surface but had a queue exceeding six hours. These are recorded observations, not current availability ([lab map](~/Projects/IBMQuantum/docs/local/a5-failed-runs/lab-map.md:1)).

| Rank | Work and resource | Initial limit and decision |
|---|---|---|
| 1 | Host: VB/X exact arc and component probes | 3–8 GiB, 10–30 min each; serialize against other admitted caps. Continue only when an exact family or a useful dimension witness emerges. |
| 2 | Host: VB structured syzygy/presentation probe and degree four | 4–8 GiB, 1 h each; retain separate results. Degree four is diagnostic unless an independent bound emerges. |
| 3 | GitHub Actions: small deterministic certificate checks | 4 vCPU/16 GB runner; use only inputs and tests that fit its permitted classical-work scope. Recheck current runner limits and authorization before dispatch. |
| 4 | Azure: a new, demonstrably smaller structured computation or component decomposition | One job per VM, up to 70 GiB and 4 h initially, subject to a written case and current approval. The N+ saturation already consumed 10 h and 72 GB without completion. |
| 5 | Kaggle CPU: independent second-prime degree receipts | Per-session RSS watchdog below the approximately 30 GB limit, 4 h initial solver ceiling; retain each result promptly. A notebook session requires its written case and approval. |
| 6 | Kaggle TPU VM: only a redesigned, independently useful batch | A bounded four-hour session after exact smoke validation, explicit case and approval; sampled RSS thresholds, process-group deadlines and streamed receipts. Include queue time and setup in the comparison. Its TPU device does not accelerate Singular merely because the VM has a TPU. |

For each launch, review the actual binary’s flags and the [compute-flags checklist](~/Projects/IBMQuantum/docs/runbooks/compute-flags.md:179). Use cgroup `MemoryMax` and `MemorySwapMax=0` where available, `timeout` and recorded thread counts; avoid inherited `RLIMIT_AS`. The decision record’s last correction identifies an inherited 4 GiB hard address-space limit as the cause under investigation, and explicitly withdraws its earlier 16 GiB explanation.

## 6. Stop doing

- **Observed; stop repeating unchanged:** pivot saturations with larger caps as the main strategy. X−, Iso, VB and E8-bar→N+ have substantial failed attempts; W8’s VM outage left its run **incomplete**, so it does not establish a saturation stall.
- **Observed; stop repeating unchanged:** local `ds` syzygy and full Rees graph elimination. W8’s local route reached 83 GB before \(h_2\); VB’s TPU graph produced a huge degree-16 matrix without a basis.
- **Inferred:** Do not infer that any solver can *never* converge affordably. The evidence rejects these unchanged runs as a good next investment; a smaller presentation, verified theorem or measured algorithmic improvement changes the experiment.
- **Observed:** Do not repeat `minAssGTZ` as the first decomposition step on the recorded X−/Iso quadratic models; the record attributes its failure to generic-coordinate densification. Radical-first decomposition succeeded quickly for X−.
- **Inferred:** Stop treating additional matching \(h_d\), a generic line, finite samples, two primes, or regularity of \(K_2\) as a completion certificate. Each remains useful when it answers a stated finite or diagnostic question.

The recorded finite-field fibers are steps toward the kernel-limit problem. Even a completed exceptional-fiber support certificate still needs the appropriate map from those directions to limiting kernel planes before it supplies the full attaching data described in [purpose.md](~/Projects/IBMQuantum/docs/local/a5-failed-runs/purpose.md:1).

