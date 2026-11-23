Reviewer: `codex exec`, model `gpt-daybreak-blue-latest`, reasoning effort high, read-only sandbox, codex-cli 0.171.0, 2026-11-22, on [brief.md](brief.md) at main `78c5e5c3a`. The text below is the reviewer's answer with local absolute paths rewritten to repository-relative paths.

# A_5 exceptional-fiber state audit

## Verdict

**Confirmed.** C1 is correct only with “on the weight slice” kept explicit: layers 1–2 are complete over both retained primes for the six fiber classes, and all ten incidences into \(N^\pm\) have all-degree \(Q(i)\) presentations on the weight slice (A5-001, 005–009, 270, 305, 446, 448, 457, 474, 475, 559, 587).

**Refuted in part.** C2 overstates the residue. A5-016 already proves the degree-3 component of \(E8\text{-bar}\to VB\); A5-458 is superseded by A5-475; A5-571 and A5-577 are receipt/provenance gaps, not missing fiber mathematics. The 52 structure and 48 method `survives` rows include hardware observations, performance methods, and optional explanatory conjectures; they are not collectively prerequisites for global topology.

**Confirmed.** C3 holds. The proof trees contain algebraic and matrix-certificate machinery, but no fiber-cone, Rees, Hilbert-function, or ideal-equality theorem. Even `A5W8ArcMatrixRanks.v` leaves passage from Gaussian-integer independence to \(Q(i)\) in prose (`rocq/quantum/A5W8ArcMatrixRanks.v:1-16`).

The current checker reports 570 rows: 213 proved, 111 certified, 112 survives, 62 refuted, 37 superseded, 15 open, 9 stalled, 7 rejected, 4 boundary.

## 1. Ten strongest results

1. **All modular fiber cones:** all six classes have all-degree presentations at both primes, including the previously difficult \(E8\text{-bar}\to N^\pm\) and \(E8\text{-bar}\to VB\). **Certified modular/proved** (A5-001, 005–009, 304, 559, 587). This closes layers 1–2 over the retained finite fields.
2. **Ten \(Q(i)\) weight-slice fibers:** opposite/same-sign X, Iso, W8, and E8-bar have all-degree presentations. **Proved in characteristic 0** (A5-270, 305, 446, 448, 457, 474, 475). This is the strongest layer-3 result.
3. **Real limits for 14 incidences \(8\to12\):** the real slice-germ limit set equals the whole holomorphic fiber. **Proved in characteristic 0** (A5-411; mechanism at `docs/evidence/a5-kernel-attachments/README.md:397-464`).
4. **Real limits for eight incidences \(12\to16\):** planes, conics, and points are realized and exhaustive, with orbit transport at \(N^\pm\). **Proved in characteristic 0** (A5-412, 415; README:466-496).
5. **Full X attachments into \(N^\pm\):** opposite-sign \(P^2\) and same-sign degree-12 threefolds are the global real limit sets. **Proved in characteristic 0** (A5-417).
6. **E8-bar open-cell Rees closure:** eight sign/prime/root cells give 148 quadrics, dimension 5, multiplicity 11, \(L=K\), with cross-host reproduction. **Certified modular** (A5-587, 588; `.../e8-rees-fibers-v3-open-cells/README.md:8-32,66-70`).
7. **E8-bar conjugation mechanism:** \(\Phi\) transports the two signs and explains the sign/root pairing; determinant and unit factors have closed forms. **Certified exact \(Q[i]\)/modular** (A5-591, 592; README:57-64).
8. **W8 geometry:** the fiber is the reduced union of degree-20 and degree-30 fivefolds, all-degree over both primes and \(Q(i)\) on the weight slice. **Proved/certified** (A5-066, 448, 475).
9. **Iso geometry:** a prime Cohen–Macaulay fourfold of degree 23 with all-degree presentation. **Proved/certified** (A5-058, 059, 067, 446, 475).
10. **Nonreduced fibers resolved structurally:** same-sign X has an embedded-plane nilradical; E8-bar has a rank-one nilradical over a quadric threefold. **Proved in characteristic 0/modular** (A5-451, 454, 544, 547).

## 2. Completion matrix

`D/P/O` mean done/partial/open. Sign-conjugate incidences form one row. “MC” means machine-checked fiber mathematics.

| Incidence or stratum pair | L1 | L2 | L3 | L4 | MC |
|---|---|---|---|---|---|
| E8-bar→B9 | D A5-402 | D | D | D A5-411/415 | O |
| E8-bar→V | D A5-402 | D | D | P A5-411/414 | O |
| E8-bar→VB | D A5-005 | D | P A5-315 | O A5-250/276 | O |
| E8-bar→\(V^a_\pm\) | D A5-405 | D | D | D A5-411/413/415 | O |
| Iso→B9 | D A5-402 | D | D | D A5-411/415 | O |
| Iso→VB | D A5-405 | D | D | P A5-411/419 | O |
| W8→B9 | D A5-402 | D | D | D A5-411/415 | O |
| W8→VB | D A5-405 | D | D | P A5-411/419 | O |
| X±→B9 | D A5-402 | D | D | D A5-411/415 | O |
| X±→VB | D A5-405 | D | D | P A5-411/419 | O |
| X+→\(V^a_+\), X−→\(V^a_-\) | D A5-402 | D | D | D A5-411/415 | O |
| B9→N± | D A5-408 | D | D | D A5-412/415 | O |
| V→N± | D A5-408 | D | D | D A5-412/415 | O |
| VB→N± | D A5-408 | D | D | D A5-412/415 | O |
| \(V^a_\pm\)→N± | D A5-408 | D | D | D A5-412/415 | O |
| X opposite-sign→N | D A5-001 | D | D A5-270 | D A5-417 | O |
| X same-sign→N | D A5-006 | D | D A5-305 | D A5-417 | O |
| Iso→N± | D A5-007 | D | P: weight D A5-446/475 | P A5-418 | O |
| W8→N± | D A5-008 | D | P: weight D A5-448/475 | P A5-418 | P: arc ranks only |
| E8-bar→N± | D A5-009/587 | D | P: weight D A5-457; slice map O A5-583 | P A5-418 | O |
| Nullity-4 kernel bundles | O A5-389 | O | O | O | O |

### Stale status-note statements

Every stale current-status passage is identifiable:

- The 313-row count and all totals are obsolete (`a5-exceptional-fiber-status.md:3-4,30-39`).
- “Only E8-bar degree 6 remains” is obsolete; A5-335, 339, 559 close it (`status.md:41-43,56-58`).
- A5-005 merely “survives” and A5-016 remains open are obsolete; both are proved (`status.md:49-55`).
- The proposed characteristic-zero rank-transfer campaign is superseded for the ten weight-slice cells by A5-474/475/457; header-slice transport remains open (`status.md:38,79`).
- “No two-sided real certificate” and “real part not started” are false after A5-411/412/417 (`status.md:39,80,82-83`).
- Iso/C30 and degree-3-component roadmap items are complete; the export wall is no longer a completion dependency (`status.md:63,75-78`).
- The \(SL_2\) part is now exact in A5-381; the rank-3 torus remains unproved (A5-255), narrowing `status.md:64-69`.

## 3. Distance to “fully solved”

A finite completion theorem suite is:

- **T1:** characteristic-zero fiber cones for all 33 incidences, with explicit independence of transverse slice. Missing: \(E8\text{-bar}\to VB\) over \(Q(i)\), and explicit header/weight transport, especially A5-583.
- **T2:** global two-sided real-limit theorem for all incidences. Missing: E8-bar→VB, the VB/V orbit directions, and Iso/W8/E8-bar→N certification (A5-250, 418, 419).
- **T3:** componentwise compatibility of composed attachments. A5-420 proves containment and sections; its flat-family/whole-section clause remains unproved.
- **T4:** nullity-4 Gauss-image equations, charts, transitions, stabilizer jumps, and bundle class (A5-389).
- **T5:** formal certificate checking for the finite algebraic claims. Entirely missing at fiber-cone level.

DAG: algebra and closure poset → T1; kernel-bundle classification T4 runs in parallel; T1 → T2; T1+T2+T4 → T3 → `dimension32-global-topology`; T5 can certify each completed node. A5-254 and A5-278 explain symmetry and ladder behavior but are not logically required for this DAG.

## 4. Coefficient decomposition

- **Confirmed mechanism:** for \(g\) generators and \(q\) quadratic relations, \(h_2=\binom{g+1}{2}-q\). Thus \((g,q,h_2)=(15,69,51),(17,68,85),(21,148,83),(24,144,156)\) (A5-305, 446, 457, 448). The counts are linear-algebra dimensions, not numerology.
- **Confirmed mechanism:** Iso’s long numerator factors as \((t-1)^{12}(10t^2+12t+1)\); codimension \(17-5=12\), and \(1+12+10=23\), its multiplicity (A5-446). W8 similarly gives \((t-1)^{18}(4t^3+27t^2+18t+1)\), summing to 50 (A5-448). E8-bar gives \((t-1)^{16}(t^5-5t^4+10t^3-12t^2+16t+1)\), summing to 11 (A5-457).
- **Confirmed geometry:** \(50=20+30\) and \(7=3+4\) are sums of degrees of equidimensional components (A5-448, 005). E8-bar’s extra degree-4 component has smaller dimension, so it does not add to multiplicity 11 (A5-451). Multiplicities 12 and 23 are respectively one top-dimensional component with embedded nilpotents and one prime component (A5-544, 446).
- **Unproven mechanism:** \(2d+1\) and \((2d+1)^2\) equal \(h^0(\mathbf P^1,\mathcal O(2d))\) and \(h^0(\mathbf P^1\times\mathbf P^1,\mathcal O(2d,2d))\). This is only a dimension match until ruling actions are exhibited (A5-278). Test the retained final quotient module for commuting actions; failure refutes it.
- **Numerological hypothesis:** closing orders \(3d+1\) and \(\lfloor7d/2\rfloor+1\) have extensive finite support but lack a valuation theorem (A5-244, 260, 269). The cheapest falsifier is the next untested ladder below the known all-degree Hilbert value.
- **Confirmed mechanism:** the determinant/unit factors record the noninvertible divisor of the pivot chart and its conjugate under \(\Phi\), rather than a new multiplicity law (A5-591/592).

## 5. Fast routes

1. **A5-583:** derive the \(21\times21\) map from the constant term of the actual transverse-slice coordinate change; predict mutual ideal reduction to zero; falsifier: singular map or failed containment; minutes–hours on WSL.
2. First compare GL\(_{21}\)-invariants—radical linear span, associated-prime dimensions/degrees, nilradical annihilator. Any mismatch refutes A5-583 before map construction; under one hour on WSL.
3. **E8-bar→VB over \(Q(i)\):** lift the already dominant component arc families and repeat the order-function argument of A5-457, avoiding a full Rees elimination; prediction \(L=K\); falsifier: a component prime not reached; 1–6 h on WSL.
4. **A5-250/419:** prove a local product theorem for the missing V/VB orbit direction, then reuse curve selection; prediction slice fibers remain exhaustive; falsifier: a boost-direction limit outside the slice fiber; symbolic hours on WSL.
5. **A5-420:** construct the componentwise flat family over VB and check specialization of both E8-bar components; prediction whole reduced section; falsifier: component loss or multiplicity jump; Kaggle CPU if under 12 h.
6. **A5-389:** eliminate one stratum, one Pfaffian chart, modulo one prime first; exploit the sign/stabilizer symmetry before lifting. Use a one-hour WSL pilot; schedule Kaggle only after measured extrapolation.
7. **A5-278:** retain the final quotient matrices and solve directly for one or two commuting \(\mathfrak{sl}_2\) actions; minutes–hours on WSL.
8. Use \(\Phi\) to halve every remaining E8 sign/root calculation; a differing transported relation is its immediate falsifier (A5-591).

## 6. Proof targets

**Rocq, in build order:** finite-field/Gaussian matrix-rank checker → sparse polynomial identity and ideal-membership checker → verified normal-form/Gröbner certificate checker → \(\Phi\) as a ring automorphism with matrix/Pfaffian transport → generated instances for A5-474, 475, 583 and 587. Trusted base: Rocq kernel, Stdlib, explicit certificate data; Singular becomes an untrusted certificate producer.

**Lean, in build order:** fiber cone and Rees special-fiber definitions → localization/polynomial-ring equivalence (`README.md:538-565`) → invariance under Nakayama-generator changes and GL maps → radical/component/torsion-free criteria used to prove \(L=K\) → Hilbert-series/multiplicity lemmas → constructible-closure, curve-selection, equivariance and attachment compatibility. Trusted base: Lean kernel and Mathlib. Existing Cayley-Dickson files supply algebra, not these geometric conclusions.

## 7. Compute plan

| Task | Host | Estimate |
|---|---|---|
| A5-577 record cells | WSL | under 1 min; existing regenerations took 23 s and 5 s (A5-580/581) |
| A5-571 second-root receipt | WSL | 2.5–3 h, one core |
| A5-583 invariants/map | WSL | under 1 h / up to 4 h |
| E8-bar→VB \(Q(i)\) structure | WSL | 1–6 h |
| A5-278 module actions | WSL | under 2 h |
| A5-250/420 symbolic certificates | WSL, then Kaggle | 2–12 h per bounded case |
| A5-389 first chart | WSL pilot | 1 h benchmark; extrapolate before scheduling |
| Large A5-389 elimination | AWS only if needed | c8a.4xlarge after owner approval; cost from C4 is brief-supplied, not independently verified |

## 8. Red-team risks

1. **High:** weight-slice/header-slice identification. Equal Hilbert data do not imply GL-equivalence; A5-582 proves the retained quadratic subspaces differ. A5-583 is decisive.
2. **High:** “characteristic zero” is sometimes weight-slice-only. Modular agreement at two primes alone proves no lift (`a5-char0-and-kernel-limits.md:50-79`).
3. **High:** Singular 4.4.1 is the sole algebra engine for most ideal, radical, saturation, and primary-decomposition claims; independent formal certificate checking is absent.
4. **Medium-high:** \(L=K\) depends on both inclusions, exact truncation/localization, component coverage, and torsion-free nilradical arguments. A5-474 covers \(K\subseteq L\); the order-function rows cover the reverse only under their map hypotheses.
5. **Medium:** A5-587’s basis files are not retained, only digests (`e8-rees-fibers-v3-open-cells/README.md:41-55`); cross-host repetition still uses Singular.
6. **Medium:** A5-591 computes C/F/J identities, while consequences for \(T,W\), and Pfaffians are algebraic deductions rather than separately checked instances.
7. **Medium:** A5-411/412 rely on constructible closure, curve selection, and source-orbit density; global V/VB directions remain outside the proved local product.
8. **Ledger integrity:** A5-260 and A5-269 still contain falsifier prose saying degree 7 is untested even though their bases record completed degree-7 runs. This is stale metadata, not a mathematical contradiction.
