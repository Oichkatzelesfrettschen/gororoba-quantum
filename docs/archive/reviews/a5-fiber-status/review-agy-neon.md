Reviewer: `agy --model gemini-4-neon-high -p`, briefed as a red-teamer, 2026-11-22, on [brief.md](brief.md) at main `78c5e5c3a`. The text below is the reviewer's answer with local file links rewritten to repository-relative paths in code spans. Its labels "confirmed" are the reviewer's own; [reconciliation.md](reconciliation.md) records which were checked.

# A_5 Exceptional-Fiber Program: Red-Team Audit and Fastest Route to Completion

All findings are marked **confirmed** (verified in retained files), **likely** (derived from retained records with an explicit falsifier), or **unproven** (conjectural). Paths are relative to `gororoba-quantum` unless prefixed `gororoba-math:`.

---

## 1. Ten Strongest Results

| # | Result | Ledger IDs | Evidence Class | Why It Ranks |
|---|---|---|---|---|
| 1 | **Weight-slice fiber cones over $\mathbb{Q}(i)$ for all 10 nullity-8 $\to N_\pm$ incidences** ($K \subset L$ for all 10; $L=K$ in all degrees for `Iso`, `W8`, `E8-bar`; schemes explicit) | A5-446, A5-448, A5-457, A5-474, A5-475, A5-507 | Proved in char 0 (Singular 4.4.1) | Eliminates the modular transfer bottleneck (`A5-316`) on the weight slice without Rees Groebner elimination (**confirmed**). |
| 2 | **Complete scheme geometry of `E8-bar -> N+-` over $\mathbb{Q}(i)$** (toric normal CM fourfold $X_{11}$ + smooth scroll $S(1,1,2)$ meeting in $\mathbb{P}^2$, rank-1 square-zero nilradical on a rank-4 quadric threefold $Q^3$) | A5-451, A5-454, A5-501..504, A5-507, A5-512, A5-543, A5-549 | Proved in char 0 | Resolves the hardest non-reduced, non-equidimensional fiber into an exact toric polytope + scroll + nilradical (**confirmed**). |
| 3 | **Direct modular Rees saturation of `E8-bar -> N+-` across all 8 `(sign, prime, root)` cells + conjugation map $\Phi$** | A5-572, A5-573, A5-587, A5-588, A5-591, A5-592 | Certified modular / char-0 identity ($\Phi$) | Independently confirms $L=K$ (`148` quadrics, dim 5, mult 11) via direct elimination; $\Phi$ proves `N-(-r) = N+(r)` over $\mathbb{Q}[i]$ (**confirmed**). |
| 4 | **Real limit sets = whole holomorphic fiber on 26/33 incidences + $G_2(\mathbb{C})\times\mathbb{C}^*$ equivariance on 27/33** | A5-411, A5-412, A5-415, A5-417, A5-452 | Proved in char 0 (with Mumford + Basu-Roy) | Closes the bulk of Layer 4 on `B9`, `V^a+-`, `N+-` via Hermitian splitting $\ker C_z = \mathbb{C}z \oplus \ker A$ (**confirmed**). |
| 5 | **Same-sign and opposite-sign `X -> N+-` fiber cones over $\mathbb{Q}(i)$ on header slices** ($F(I)=\mathbb{Q}(i)[y_1,y_2,y_3]$ and monomial ideal $I=M \implies 69$ quadrics) | A5-270, A5-304, A5-305, A5-544 | Proved in char 0 | Only incidences proved all-degree over $\mathbb{Q}(i)$ directly on the original header slices (**confirmed**). |
| 6 | **Parametrized models of `W8` components ($C_{20}, C_{30}$) + Rocq rank-6 arc certificates** | A5-066, A5-456, `gororoba-math:rocq/quantum/A5W8ArcMatrixRanks.v` | Proved in char 0 / Machine-checked ($\mathbb{Z}[i]$) | Proves radicality and absolute primality of $W_8$'s two fivefolds without primary decomposition; Rocq certifies all eight $24\times 6$ arc Jacobians (**confirmed**). |
| 7 | **Linear symmetry Lie algebras over $\mathbb{Q}(i)$ and Levi surjection from basepoint stabilizer** ($\mathfrak{g}/\mathfrak{r}\cong\mathfrak{sl}_2$, split maximal tori of rank 4–6; `Iso` complexity-1) | A5-424, A5-426, A5-427, A5-348 | Proved in char 0 | Explains the `sl_2` multiplet structure of generators and proves `Iso` is a complexity-1 $T$-variety (**confirmed**). |
| 8 | **All-degree modular closure of `E8-bar -> VB` (`A5-005`, `A5-015`, `A5-016`)** (rational arcs hitting both minimal-degree threefolds $S_3, S_4$) | A5-005, A5-015, A5-016, `arcs-vb/README.md` | Proved modular (32009, 32029) | Resolves the long-open degree-3 component via order-2 arcs at $k_0=-9$ (**confirmed**). |
| 9 | **Machine-checked $G_2$ derivation span & Cayley-Dickson algebra foundations** | A5-453, A5-500, `gororoba-math:rocq/quantum/CdTowerG2DerivationSpan.v` | Machine-checked (Rocq 9.3.0) | Certifies the 14-dimensional $\mathfrak{g}_2$ derivations over every ring receiving $\mathbb{Z}[i]$ where $6$ is regular (**confirmed**). |
| 10 | **Exact counterexample refuting naive modular-to-char-0 truncated-rank transfer** | A5-316, `a5-char0-transfer/transfer_counterexample.py` | Proved counterexample | Prevented a false characteristic-0 claim; forced the direct weight-slice $\mathbb{Q}(i)$ breakthrough (**confirmed**). |

---

## 2. Completion Matrix & Attacks on C1–C3 and the Status Note

| Incidence / Stratum Pair | Layer 1 ($h_d$) | Layer 2 (all-$d$ $F(I)$) | Layer 3 (char 0) | Layer 4 (attaching/real) | Machine-checked |
|---|---|---|---|---|---|
| `8 -> 12` resolved (8 pairs: `B9`, `V`, `X+- -> Va+-`) | done (A5-402) | done (A5-402) | done (A5-402) | done on `B9/Va+-` (A5-411, A5-415); **partial** on `E8->V` (boost open, A5-415) | open (only `SchurKernelTransport.v`) |
| `8 -> 12` higher-order (`X+-, Iso, W8 -> VB`; `E8 -> Va+-`, 6 pairs) | done (A5-405) | done (A5-405) | done (A5-405, A5-413) | done on `Va+-` (A5-415); **partial** on `VB` (boost sampled, A5-419) | open |
| `E8-bar -> VB` (1 pair) | done mod $p$ (A5-107/113/286/287) | done mod $p$ (A5-005/015/016) | **partial** (A5-315 $d=2$ unretained) | **open** (A5-250, A5-428 boost sampled mod 32029) | open |
| `12 -> 16` (`B9, V, VB, Va+- -> N+-`, 8 pairs) | done (A5-407) | done (A5-407) | done (A5-407) | done (A5-412, A5-415) | open |
| `X+ -> N-`, `X- -> N+` (2 pairs) | done (A5-001) | done (A5-001) | done (A5-270) | done (A5-417) | open |
| `X+ -> N+`, `X- -> N-` (2 pairs) | done (A5-155..173) | **partial** (`X+` 32009 lacks $K_2$, A5-304) | done header (A5-305); **partial** weight (A5-474 $K\subset L$ only) | done (A5-417) | open |
| `Iso -> N+-` (2 pairs) | done (A5-119/125) | done (A5-007/067, A5-574) | done weight (A5-446/475); **partial** header (A5-293/294) | **partial** (A5-418 survives; needs slice bridge) | open |
| `W8 -> N+-` (2 pairs) | done (A5-066) | done (A5-008/066) | done weight (A5-448/475); **partial** header (A5-293) | **partial** (A5-418 survives; needs slice bridge) | **partial** (`A5W8ArcMatrixRanks.v`) |
| `E8-bar -> N+-` (2 pairs) | done (A5-335, A5-587) | **partial** header (A5-559 cond.; A5-571 open); done weight (A5-587) | done weight (A5-457/507); **partial** header (A5-346 $d\le 7$ lb) | **partial** (A5-418 survives; needs slice bridge) | open |
| Composed limits & global bundles (`8->12->16`, nullity 4/8) | n/a | n/a | **partial** (A5-420 mod $p$; A5-380..396) | **open** (A5-389 nullity-4, A5-396 ordinary class, A5-420 flat family) | **partial** (`CdTowerG2DerivationSpan.v`, `NullityTwelveQuadraticLocus.v`) |

### Corrections to the Orchestrator's Reading (C1–C3)

- **C1 breaks on three points (confirmed):** (1) Layer 2 at `32009` is *not* gap-free: `X+ -> N+` at `32009` has no retained $K_2$ or direct $L=K_2$ comparison (`A5-304`, [a5-exceptional-fiber-findings.md] (`docs/notes/topics/a5-exceptional-fiber-findings.md` L554-L555)), and `E8-bar -> N+` at `(32009, 21255)` lacks a degree-2 receipt (`A5-571` open), while `A5-559` is conditional on $K_2 \subset L$ and covers only one root per prime. (2) C1 conflates slices: `A5-270` and `A5-305` are **header-slice** proofs, whereas `A5-446/448/457/474/475` are **weight-slice** proofs; same-sign `X` has no weight-slice char-0 $L=K$ proof, and `A5-582` proves the two `E8-bar` quadric ideals are *unequal* in their coordinates (`A5-583` open). (3) C1 omits the 22 other incidences (`8->12`, `12->16`, already done over $\mathbb{Q}(i)$ except `E8->VB` and boost variation).
- **C2 has four factual errors (confirmed):** (1) **C2(c) is stale on `A5-016`:** the degree-3 component of `E8-bar -> VB` is **already proved** modulo 32009 and 32029 (`A5-016`, `A5-005`, [arcs-vb/README.md] (`docs/evidence/a5-exceptional-fibers/arcs-vb/README.md` L3-L10)); only char 0 and boost variation remain. (2) **C2(d) lists `A5-458` as open, but it is `superseded`** by `A5-475` (`proved`, [a5-kernel-attachments/README.md] (`docs/evidence/a5-kernel-attachments/README.md` L978-L996)). (3) **C2(d) overstates `A5-250`:** 26/33 incidences already have proved two-sided real limit sets (`A5-411/412/415/417`), leaving `E8->VB`, slice-bridging `A5-418`, boost variation on `V`/`VB`, composed-limit flatness (`A5-420`), and global attaching maps. (4) **C2 omits open rows** `A5-325` (`X-` vs `VB` germ isomorphism), `A5-542` (generic-$s_2$ Rees ideal), `A5-258`, `A5-259`, `A5-263`, `A5-283`, `A5-202`, `A5-242`; and most of the 52 `survives` structure / 48 method rows are hardware runs, diagnostic probes, or superseded intermediates, not open blockers.
- **C3 understates `gororoba-math` (confirmed):** While no fiber-cone identity is formalized, `gororoba-math:rocq/quantum/A5W8ArcMatrixRanks.v` already certifies all eight `W8` arc-limit Jacobians over $\mathbb{Z}[i]$, `SchurKernelTransport.v` certifies Schur kernel transport over any MathComp `fieldType`, and `NullityTwelveQuadraticLocus.v` certifies a real quadratic Schur locus.

### Stale Statements in [a5-exceptional-fiber-status.md] (`docs/notes/topics/a5-exceptional-fiber-status.md`) (confirmed)

1. **Row counts (L4, L30–32):** states 313 rows (94 certified, 56 proved); actual `ledger.tsv` has 570 rows (111 certified, 213 proved, 112 survives, 62 refuted, 37 superseded, 7 rejected, 15 open, 9 stalled, 4 boundary).
2. **Layer 1 `E8-bar` degree 6 (L36, L42–43, L56–58, L75):** claims 92/96 with `E8-bar` $d=6$ open (`1526 <= h_6 <= 1666`) and schedules membership of 140 forms; superseded by `A5-335`, `A5-559`, `A5-587`.
3. **Self-contradiction on `VB` and `Iso` (L37 vs L50–55, L76–77):** L37 marks `A5-005`, `A5-007`, `A5-009` proved, yet L50–55 and L76–77 still treat `A5-016` and `A5-067` as open and schedule arc/plane-family searches.
4. **Characteristic 0 (L38, L79):** omits all weight-slice $\mathbb{Q}(i)$ proofs (`A5-421`, `A5-446/448/457/474/475`) and schedules Kaggle $K_2$ lifts already completed in 60 s.
5. **Layer 4 real limits (L39, L80, L82):** claims real part is "not started" and `A5-272..276` are next; superseded by `kernel-limits/` and `A5-411/412/415/417`.
6. **Torus / `SL(2)` stabilizer (L67–68, L78):** calls it an unretained floating-point hypothesis; proved exactly over $\mathbb{Q}(i)$ in `A5-424/426/427` and Rocq (`A5-500`).

---

## 3. Distance to "A_5 Fully Solved" and Dependency DAG

Closing `dimension32-global-topology` requires eight theorems:
- **T1 (Done on weight slice / header X):** All 33 nullity-changing complex fibers over $\mathbb{Q}(i)$ — **missing:** `E8-bar -> VB` over $\mathbb{Q}(i)$ (T1a) and slice isomorphism `A5-583` linking header and weight slices (T1b).
- **T2 (Partial):** Fiber variation over full boundary orbits — **missing:** boost-orbit constancy/family on `V` and `VB` (6 incidences).
- **T3 (Partial):** Real two-sided limit sets for all 33 incidences (`A5-250`) — **missing:** `E8->VB`, boost-orbit `V`/`VB`, and promoting `A5-418` (`Iso, W8, E8 -> N+-`) once T1b holds.
- **T4 (Open):** Composed-limit compatibility (`8 -> 12 -> 16`, `A5-420`) — flat specialization over `VB` and limits through `B9`/`V`.
- **T5 (Partial):** Complete topological classification of stratum kernel bundles — **missing:** nullity-4 classification (`A5-389`) and ordinary (non-stable) class of nullity-8 bundles (`A5-396`).
- **T6 (Open):** Global gluing / attaching maps assembling the stratified bundle over $\mathcal{Z}(A_5)$.
- **T7 (Optional hygiene):** Receipt completeness (`A5-571`, `A5-577`, `X+` 32009 $K_2$) and independent non-Singular verification.
- **T8 (Optional formalization):** Machine-checked proofs of core certificates in `gororoba-math`.

```text
T1a (E8->VB char 0) ──► T2 (V/VB boost family) ──► T3 (real limits, all 33) ──┐
T1b (A5-583 slice map) ──────────────────────────► T3 & T4 (composed limits) ──┼──► T6 (global attaching maps)
T5a (A5-389 nullity-4) & T5b (A5-396 nullity-8) ───────────────────────────────┘
T7 (receipts + non-Singular check) ──► T8 (Rocq/Lean kernel replay)  [orthogonal audit track]
```

---

## 4. Coefficient Decomposition (Mechanisms vs Numerology)

1. **Exact Hilbert Numerator & $h$-Vector Decompositions (confirmed exact algebraic identities):**
   Dividing each retained numerator (`weight-slice-fiber-relations-result.json`, [e8-rees-fibers-v2-p32009/README.md] (`docs/evidence/a5-exceptional-fibers/working/runs/e8-rees-fibers-v2-p32009/README.md` L25-L29)) by $(1-t)^c$ yields:
   - **`E8->VB` ($n=10, c=6, d=4, e=7$):** $h=(1,6)$ is the Mayer-Vietoris sum of two minimal-degree threefolds $S_3\subset\mathbb{P}^5$ ($h=(1,2)$) and $S_4\subset\mathbb{P}^6$ ($h=(1,3)$) meeting in $\mathbb{P}^2$ ($h=(1)$): $(1+2t)+(1+3t)-(1-t)=1+6t$.
   - **`X-` same-sign ($n=15, c=11, d=4, e=12$):** $h=(1,11,-3,4,-1) = (1+8t+3t^2) + (1-t)(3t-3t^2+t^3)$, where $h_{\text{red}}=(1,8,3)$ gives `HF = 12,45,112,225` ([findings] (`docs/notes/topics/a5-exceptional-fiber-findings.md` L191)) and the remainder is $(1-t)(H(\mathbb{P}^2)-1)$, matching `A5-544` ($\dim(P/K_2)_d=\binom{d+2}{2}$).
   - **`E8->N+-` ($n=21, c=16, d=5, e=11$):** All 22 numerator coefficients (`1, 0, -148, ..., -21, 1`) factor as $(1-t)^{16}\cdot h(t)$ with $h=(1,16,-12,10,-5,1)$. Exact Mayer-Vietoris + nilradical decomposition:
     $$h_{E_8} = \underbrace{(1+7t+3t^2)}_{X_{11}} + \underbrace{(1-t)(1+3t)}_{S(1,1,2)} - \underbrace{(1-t)^2}_{\mathbb{P}^2} + \underbrace{(1-t)\big((1+t)-(1-t)^4\big)}_{R/K \cong \mathfrak{m}_{Q^3}}.$$
   - **`Iso` ($n=17, c=12, d=5, e=23$):** All 15 coefficients (`1, 0, -68, 452, ..., 10`) equal $(1-t)^{12}(1+12t+10t^2)$. Since $S/K$ is CM with $\deg h = 2$, $\mathrm{reg}(S/K)=2$ ($\mathrm{reg}(K)=3$), so $K$ has at most linear and quadratic syzygies.
   - **Universal CM identity:** On every CM reduced ring/component, $h_2 = \binom{c+1}{2} - q$: `VB` ($21-21=0$), `X- red` ($36-33=3$), `E8 X_11` ($28-25=3$), `Iso` ($78-68=10$), `W8` ($171-144=27$). *Falsifier:* any CM reduced component violating $h_2=\binom{c+1}{2}-q$. *Cheapest test:* already verified across all five; extend to $C_{20}, C_{30}$ and $C_{20}\cap C_{30}$ of `W8` in 1 s to decompose $h_{W_8}=(1,18,27,4)$ via Mayer-Vietoris (**likely**).

2. **Jacobi-Pfaffian Derivation of `detB` and Unit Polynomials (`A5-592`) — NEW, UNRECORDED (confirmed derivation):**
   In [e8-nm-p.v2-u-full.sing] (`docs/evidence/a5-exceptional-fibers/working/runs/e8-rees-fibers-v2-p32009/e8-nm-p.v2-u-full.sing` L142-L145), $B$ is $6\times 6$ skew-symmetric, so $\det(B) = \mathrm{Pf}(B)^2$. Writing $-1024(s_2^2-1)^2(s_2\mp i)^2 = (32i(s_2^2-1)(s_2\mp i))^2$ gives $\mathrm{Pf}(B) = \pm 32i(s_2^2-1)(s_2\mp i)$. By the **Jacobi-Pfaffian identity** for skew Schur complements $S = W/\det(B)$, every $4\times 4$ principal Pfaffian satisfies $\mathrm{Pf}_4(S) = \mathrm{Pf}_{10}(T_{1..6,I})/\mathrm{Pf}(B)$, hence
   $$\mathrm{Pf}_4(W) = \mathrm{Pf}(B)^4\,\mathrm{Pf}_4(S) = \mathrm{Pf}(B)^3\,\mathrm{Pf}_{10}(T_{1..6,I}) \propto (s_2^2-1)^3(s_2\mp i)^3\,\mathrm{Pf}_{10}(T_{1..6,I}).$$
   This **proves** why every single one of the 126 Pfaffians carries $(s_2^2-1)^3(s_2\mp i)^3$; exponent 4 on generators 10 and 16 (`A5-592`) is simply one extra factor of $(s_2^2-1)$ inside $\mathrm{Pf}_{10}(T_{1..6,I})$. *Falsifier:* any $\mathrm{Pf}_{10}(T_{1..6,I})$ failing to equal $\mathrm{Pf}_4(W)/\mathrm{Pf}(B)^3$ up to constant. *Cheapest test:* 5-line Singular/SymPy check (<2 s).

3. **Exact $V_4$-Representation Factorization of Last-Jump Block Splits (`A5-244`, `A5-269`, `A5-278`) — NEW, UNRECORDED (likely mechanism, confirmed character identity):**
   The repository rejected smooth $\mathbb{P}^1\times\mathbb{P}^1$ (`A5-271`) because $(d+1)^2, d(d+1), d(d+1), d^2$ misses `A5-244`, and `A5-278` left a mysterious "degree-dependent twist." Setting $E_d = 2\lfloor d/2\rfloor + 1$ and $O_d = 2\lceil d/2\rceil$ ($E_d+O_d = 2d+1$):
   - **`E8->VB` (`A5-269`)** is $V_1(d) = E_d\chi_0 \oplus O_d\chi_1$.
   - **`Iso/W8/X-` (`A5-244`)** is the **exact $V_4$-tensor product** $M_d = V_1(d) \otimes V_2(d)$ with $V_2(d) = E_d\chi_0 \oplus \frac{O_d}{2}\chi_2 \oplus \frac{O_d}{2}\chi_3$:
     - $\chi_0$: $E_d^2 = (2\lfloor d/2\rfloor+1)^2$; $\chi_1$: $E_d O_d = d(d+1)$; $\chi_2=\chi_3$: $(E_d+O_d)\frac{O_d}{2} = (2d+1)\lceil d/2\rceil$.
   - **Twist-free ring realization:** On `Iso/W8/X-`, slice variables carry $V_4$-characters $t_1,t_3\in\chi_0$, $t_2\in\chi_1$, $t_4,t_6\in\chi_2$, $t_5,t_7\in\chi_3$ ([findings] (`docs/notes/topics/a5-exceptional-fiber-findings.md` L102-L104)). The degree-$d$ piece of a **nodal conic** $R_1 = k[a,b_+,b_-]/(b_+b_-)$ ($a\in\chi_0, b_\pm\in\chi_1$) has exact character $V_1(d)$, and $R_2 = k[z,x,y]/(xy)$ ($z\in\chi_0, x\in\chi_2, y\in\chi_3$) has exact character $V_2(d)$ — **zero degree-dependent twist**, and degree $d$ instead of $2d$! *Falsifier:* actual pivot-complement basis of $W_{N-1}/W_N$ at $d=2,3$ failing to have the multiplication structure of $R_1$ (`VB`) or $R_1\otimes R_2$ (`Iso/W8/X-`). *Cheapest test:* dump last-jump quotient monomials in `fiber_rank` at $d=2,3$ (<60 s).

4. **Generator Counts `3, 15, 17, 21, 24`, Pfaffian Nesting, and `sl_2` Multiplets (confirmed):**
   At `N-`, `weight-slice-fiber-relations-result.json` shows exact Pfaffian subset chains `xp (3) ⊂ xm (15) ⊂ e8 (21)` and `xp (3) ⊂ iso (17) ⊂ w8 (24)`, reflecting closure containment. In `A5-426`, `W8` ($24$) minus `E8` ($21$) is exactly one spin-1 triplet $V_2$, while all four share one spin-3/2 quartet $V_3$. *Falsifier:* weight-slice generator spans not preserving this nesting under `N+`.

5. **Relation Counts `68, 69, 144, 148` & Closing Orders `3d+1`, `floor(7d/2)+1`:**
   - Relation counts decompose via $q = \binom{g+1}{2} - h_2^{\text{red}} - \dim(R/K)_2$: `X-` $= 33\text{ (red)} + 36\text{ (nil)} = 69$; `E8` $= 67\text{ (red)} + 81\text{ (nil)} = 148$. **Numerological coincidence (confirmed):** the near-equalities `68 vs 69` (`Iso` vs `X-`) and `144 vs 148` (`W8` vs `E8`) have completely different codimensions and nilpotent shares — no shared mechanism.
   - Closing orders `3d+1` (CM fibers `VB, Iso, W8`) vs `floor(7d/2)+1` (non-CM `X-`, `E8-bar` with even-$d$ plateaus, [findings] (`docs/notes/topics/a5-exceptional-fiber-findings.md` L481-L484)) correlate with CM vs non-CM/nilradical defect; the `7/2` slope mechanism remains **unproven** (falsifier: $X^-$ $d=7$ closing off $N=25$, or $E_8$ $d=6$ off $N=22$).

---

## 5. Novel Routes to Shorten the Remaining Path

1. **Close `A5-583` in <30 s via linear Plücker frame pullback (no blind `GL_21` search):**
   - *Mechanism:* Both header and weight slices sit at the same `N+-` basepoint $z_0$ and linearly embed $\mathbb{P}^{20}\hookrightarrow\mathbb{P}^{125}$ (`126 x 21` Nakayama matrices, [a5-kernel-attachments/README.md] (`docs/evidence/a5-kernel-attachments/README.md` L549-L553)). Because the slice-change biholomorphism $z \mapsto g(z)s(z)$ has $g(z_0)=I$ (`A5-415`), its action on $I/mI$ is purely the linear change of frame $F_{\text{wt}}^{-1} F_{\text{hdr}}$ on $\Lambda^4 \ker C_{z_0}$ pulled back through the two $126\times 21$ embedding matrices!
   - *Prediction:* The resulting $21\times 21$ invertible matrix $M$ over $\mathbb{Q}(i)$ (reduced mod 32009) maps weight-slice $K$ onto header-slice $K_2$ with mutual remainders `0, 0`.
   - *Falsifier:* Nonzero remainder after applying $M$, OR mismatch of `GL_21`-invariants (e.g., incidence of the 5 nilpotent forms with the scroll/singular locus) refuting `A5-583`.
   - *Cost / Host:* <30 s, <1 GB RAM on WSL workstation.

2. **Eliminate 9 degrees of $s_2$ in all Rees scripts via $\mathrm{Pf}_{10}(T_{1..6,I})$:**
   - *Mechanism:* By the Jacobi-Pfaffian identity (Deliverable 4.2), replacing $W = \det(B)D_m + X^T\mathrm{adj}(B)X$ + unit stripping ([e8-nm-p.v2-u-full.sing] (`docs/evidence/a5-exceptional-fibers/working/runs/e8-rees-fibers-v2-p32009/e8-nm-p.v2-u-full.sing` L144-L193)) by the $10\times 10$ principal Pfaffians $\mathrm{Pf}_{10}(T_{1..6,I})$ drops $\mathrm{Pf}(B)^3$ identically before polynomial expansion, removes the `A5-586` loop hazard, and keeps only the single extra $(s_2^2-1)$ on generators 10, 16.
   - *Prediction:* Byte-identical stripped generators $g_a$ (up to nonzero scalar), faster Pfaffian stage, and feasible direct Rees check for `W8` or char-0 `Iso`.
   - *Falsifier:* Any $\mathrm{Pf}_{10}(T_{1..6,I})$ failing $c\cdot\mathrm{Pf}_{10} \equiv g_a \pmod J$.
   - *Cost / Host:* <5 min to verify on Arm/WSL; potential speedup for `W8` Rees on WSL/AWS.

3. **Prove `E8-bar -> VB` in char 0 (`A5-005/015/016` over $\mathbb{Q}(i)$) in <10 min:**
   - *Mechanism:* The parametrization $\Phi(w,\rho,\sigma,k)$ and both families (`vb-generic`, `vb-special` at $k_0=-9$, [arcs-vb/README.md] (`docs/evidence/a5-exceptional-fibers/arcs-vb/README.md` L18-L35)) already have **rational coefficients**! Replay `vb_arcs.py` + `k2_cm.py` + retain `A5-315` quadrics over $\mathbb{Q}(i)$ (plus $K_2\subset L$ membership).
   - *Prediction:* $V(K_2)=V(P_1)\cup V(P_2)$ radical and CM over $\mathbb{Q}(i)$, both arc Jacobians rank 4 over $\mathbb{Q}(i) \implies L=K_2$ in char 0.
   - *Falsifier:* Drop in Jacobian rank or non-radicality over $\mathbb{Q}(i)$, or $K_2\not\subset L$.
   - *Cost / Host:* ~15 min (`A5-315` was 650 s), <2 GB on WSL.

4. **Parametric boost family over $\mathbb{Q}(i)(t)$ for all 6 `V`/`VB` incidences:**
   - *Mechanism:* Rationalize $c^2-s^2=1$ as $c=(1+t^2)/(1-t^2), s=2t/(1-t^2)$ and run `nakayama_rees_fibers` (`Iso, W8, X+- -> VB`) and `boost_e8_vb_quadrics` + rational arcs (`E8->VB`) over $\mathbb{Q}(i)(t)$ instead of sampling discrete boosts (`A5-419/428`).
   - *Prediction:* Generic fiber constant over $\mathbb{Q}(i)(t)$ with explicit bad-$t$ locus empty on real boosts $c>0$, also yielding the flat family over `VB` needed by `A5-420`.
   - *Falsifier:* Non-constant Nakayama rank, drop in projective equivalence on `E8->VB`, or special fiber jumping at a real boost.
   - *Cost / Host:* 1–2 h, <8 GB on WSL (1-parameter rational function field).

5. **Independent non-Singular cross-check of $L=K$ via Macaulay2 or `msolve`/FLINT + cofactor certificates:**
   - *Mechanism:* Export the `Q(i)` generators and relations of `Iso`, `W8`, `E8-bar` from `weight_slice_fiber_relations.py` and verify `A5-474` ($q(G)\in J+mI^2$), `A5-451` (`K:R = A`, `N^2 \subset K`), and `A5-457/475` (Jacobian ranks and prime vanishing) in **Macaulay2** or pure **python-flint** (for the linear/order-function parts, eliminating Singular from the trust chain of `A5-457/475`).
   - *Prediction:* Exact agreement on all invariants and ranks.
   - *Falsifier:* Any disagreement with Singular 4.4.1.
   - *Cost / Host:* <30 min on WSL.

6. **Decide `A5-278` (nodal-conic last-jump model) directly from `fiber_rank` pivots:**
   - *Mechanism:* Extract the $2d+1$ / $(2d+1)^2$ basis elements in $W_{N-1}/W_N$ at $d=2,3$ for `VB` and `Iso` and test the $R_1$ / $R_1\otimes R_2$ multiplication law directly.
   - *Prediction:* Basis splits into exact $V_4$-eigenvectors matching $k[a,b_+,b_-]/(b_+b_-)$ and $k[z,x,y]/(xy)$.
   - *Falsifier:* Different multiplication algebra or non-vanishing product $b_+ b_-$ / $xy$ in the top layer.
   - *Cost / Host:* <2 min on WSL.

7. **Close `A5-389` (nullity-4 kernel bundles) via the 8-family Gauss quadrics (`A5-469`) + compact-core $K$-theory:**
   - *Mechanism:* Lift `A5-463/464/469` from $\mathbb{F}_{32029}$ to $\mathbb{Q}$ (all 8 families—Plücker, $\mu$, $M(e_j)$, $N_1, N_2, N_3$—are rational!) and combine with the orbit stratification of `A5-552..564` to compute $H^*$/$K$-theory of the compact cores of the three nullity-4 strata, matching the `A5-380..396` template.
   - *Prediction:* Explicit Chern/Stiefel-Whitney classes and triviality verdict for all three nullity-4 strata.
   - *Falsifier:* Sampled quadric rank dropping over $\mathbb{Q}$ or missing orbit type outside `A5-561`.
   - *Cost / Host:* 2–6 h on WSL.

---

## 6. Proof Targets in `gororoba-math` (Build Order & Trusted Base)

Build order prioritizes small, high-leverage lemmas that close prose gaps in existing certificates:

| Order | Target | System | Scope | Trusted Base |
|---|---|---|---|---|
| 1 | **Conjugation isomorphism $\Phi$ (`A5-591`) & `detB` (`A5-592`)** | **Rocq** (`rocq/quantum`) | Ring automorphism $\Phi$ on $\mathbb{Z}[i][s_1..s_9]/(i^2+1)$; verify $D\Phi(C_-)D=-C_+$, $D\Phi(F_-)E=F_+$, $\det B = -1024(s_2^2-1)^2(s_2\mp i)^2$ by `vm_compute`/ring. | Rocq 9.3 kernel + `GaussianIntegerHom.v` (zero axioms). |
| 2 | **Jacobi-Pfaffian Schur identity** | **Lean 4** (`lean/GororobaMath`) | Formalize $\mathrm{Pf}_4(\det(B)S) = \mathrm{Pf}(B)^3 \mathrm{Pf}_{10}(T_{1..6,I})$ for $6\times 6$ skew $B$ over any commutative ring (Mathlib `Matrix.Pfaffian` / alternating forms). | Lean 4.35 kernel + Mathlib (`propext`, `Quot.sound`). |
| 3 | **$\mathbb{F}_p$ / $\mathbb{Z}[i]$ rank & left-inverse bridge to $\mathbb{Q}(i)$** | **Rocq** (`rocq/quantum`) | Extend `MatrixLeftInverseCertificate.v` to `Field` (clearing denominators in Rocq, removing the prose step in `A5W8ArcMatrixRanks.v:15-17`), and add `A5E8ArcMatrixRanks.v` + `A5IsoArcMatrixRanks.v` for `A5-457/475`. | Rocq 9.3 kernel + `CdTowerRing.v`. |
| 4 | **Exact polynomial-cofactor membership checker ($q(G) = \sum a_k J_k + \sum b_{ij} s_i P_j$)** | **Rocq** (`rocq/quantum`) | Verified sparse multivariate polynomial equality checker over $\mathbb{Z}[i]$ / $\mathbb{F}_p$ certifying $K \subset L$ (`A5-474`, `A5-305`, `E8->VB`) directly from exported Singular cofactors (no Groebner proof needed!). | Rocq 9.3 kernel + witness export (soundness independent of Singular!). |
| 5 | **Hermitian splitting & partner purity (`A5-398/399`)** | **Lean 4** | Formalize `ker C_z = C z (+) ker A(z, conj z)` over $\mathbb{C}$ using Mathlib inner-product spaces, plus `G_2(C)` equivariance from `CdTowerG2DerivationSpan`. | Lean 4.35 kernel + Mathlib classical axioms. |
| 6 | **L = K deduction lemma (rank-1 torsion-free nilradical, `A5-455/457`)** | **Lean 4** | Abstract commutative-algebra theorem: if $K \subset L \subset R = \sqrt{K}$, $R/K$ is rank-1 torsion-free over domain $S/A$, and valuation $v$ separates $L$ from $A$, then $L=K$. | Lean 4.35 kernel + Mathlib `Ideal.IsPrimary` / `Valuation`. |

---

## 7. Compute Plan (Using C4 Hosts & Retained Timings)

| Task | Host | Wall Time (Basis) | RAM | Approval? |
|---|---|---|---|---|
| **1. `A5-583` Plücker-frame linear map + mutual reduction** | WSL (16c/32t) | **<1 min** (comparable to `kcompare` 23 s) | <1 GB | No |
| **2. `A5-577` add `E8->N+`, `Iso->N-` modular cells to record** | WSL | **<2 min** (`weight_slice_fiber_relations.py` 60 s) | <1 GB | No |
| **3. `E8->VB` char 0 (`A5-315` retain + `vb_arcs` over $\mathbb{Q}(i)$)** | WSL | **~15 min** (`A5-315` ran 650 s; `vb_arcs` <5 s) | <2 GB | No |
| **4. `A5-278` nodal-conic pivot dump ($d=2,3$)** | WSL | **<2 min** (`Iso d=3` took 15 s) | <1 GB | No |
| **5. `A5-571` direct receipt `E8->N+` `(32009, 21255)`** | Arm host (4c/24 GB) or WSL | **~2.5 h** (`A5-570` took 2 h 33 min on 1 core) | <4 GB | No |
| **6. Parametric boost over $\mathbb{Q}(i)(t)$ (`V`/`VB`, 6 pairs)** | WSL (or Kaggle CPU <12 h) | **1–3 h** (`boost_e8_vb_quadrics` 20 min at 4 pts) | <8 GB | No (Kaggle standing <12 h) |
| **7. Non-Singular cross-check (Macaulay2/FLINT on `A5-457/474/475`)** | WSL | **~30 min** | <4 GB | No |
| **8. `A5-389` nullity-4 rational quadrics & core topology** | WSL / Kaggle CPU | **2–6 h** | <8 GB | No |
| **9. Optional: direct `W8` modular Rees with $\mathrm{Pf}_{10}$ + modulo colon** | **AWS `c8a.4xlarge` spot** ($0.25/h) only if WSL >12 h | **~8–24 h** (extrapolated from `E8` 6–7 h on Arm) | 16–32 GB | **Yes (owner approval)** |

**Key takeaway:** Almost the entire path to closing Layers 1–4 fits on the **WSL workstation** in **under one workday**, needing **zero AWS spend** unless optional `W8` direct Rees saturation is desired.

---

## 8. Red-Team Audit of Certified and Proved Claims (Ranked by Risk)

### Risk 1 (CRITICAL): The Unbridged Slice Divide (`A5-582` / `A5-583`) — confirmed
Weight-slice `K` and header-slice `K2` for `E8-bar -> N+-` are **distinct ideals in $\mathbb{F}_{32009}[y_1,\dots,y_{21}]$** (union rank 223/224, 133–134 nonzero remainders, `A5-582`). Yet `A5-423` and `A5-418` transfer results between slices via the *analytic* biholomorphism $z \mapsto g(z)s(z)$ over $\mathbb{C}$ (`A5-415`) without exhibiting an explicit `GL_21` matrix over $\mathbb{Q}(i)$ or $\mathbb{F}_p$. Until `A5-583` is closed (Route 1), the header-slice program (`A5-007/008/009`, `A5-559`) and the weight-slice char-0 program (`A5-446/448/457/475`) prove statements about **two unlinked presentations** of the germ.

### Risk 2 (CRITICAL): Single-Tool Monoculture on Singular 4.4.1 + Unretained Basis Files — confirmed
Every char-0 and modular ideal decomposition (`minAssGTZ`, `primdecGTZ`, `radical`), Rees saturation (`satstd` in `customstd.lib`, `quotient`/`modulo`), and Hilbert series in `A5-446/448/457/474/475/507/559/572..592` depends on **one exact build** (`Singular 4.4.1, Dec 6 2025 11:10:58`). Second-host replays (`A5-588`) test hardware determinism, not algorithmic correctness. Worse:
- The 52–60 MB `.hs.ssi`/`.sat.ssi` basis files are **not retained**, and `check_rees_fibers.py` explicitly verifies only log internal consistency, not independent mathematics ([e8-rees-fibers-v2-p32009/README.md] (`docs/evidence/a5-exceptional-fibers/working/runs/e8-rees-fibers-v2-p32009/README.md` L68-L70), [L137-L156] (`docs/evidence/a5-exceptional-fibers/working/runs/e8-rees-fibers-v2-p32009/README.md` L137-L156)).
- `e8-nm-p.v2-u-full.sing:203` trusts `satstd(H, u)` blindly without verifying `H ⊂ HS` (only the resumed `nm29-modstd` run added `CERT H_outside_HS 0`, [v3 README] (`docs/evidence/a5-exceptional-fibers/working/runs/e8-rees-fibers-v3-open-cells/README.md` L55)) and never verifies `u^k HS ⊂ H`. (Note: checking `ubad == 0` as sufficiency for `HS : u = HS` *is* sound even for inhomogeneous `H` in `wp`, by Noetherian induction on leading terms; the real gap is trusting `satstd` itself!)

### Risk 3 (HIGH): Hidden Premises in "L = K given K ⊂ L" (`A5-457`, `A5-475`, `A5-559`) — confirmed
1. **Conditional receipts:** `A5-559` (header-slice `E8-bar -> N+-`) assumes `K2 ⊂ L`, which still lacks a direct receipt at `N+`, `(32009, 21255)` (`A5-571` open), and `X+ -> N+` at `32009` has no `K2` file at all (`A5-304`).
2. **Primary-decomposition soundness:** The nilradical rank-1 deduction in `A5-454/455/457` and `A5-559` proves $R/K$ is torsion-free over $S/A$ by asserting that `primdecGTZ` returned **every** associated prime of $K$ (so none besides $A$ contains $A$). If `primdecGTZ` dropped a higher-codimension embedded prime inside $V(A)$, `R/K` could have torsion supported inside $V(A)$ and `L/K` could be nonzero while escaping the embedded arc family! Checking `K : A = R` (which `A5-547` does check!) is necessary, **not** sufficient to rule out an embedded prime strictly containing $A$ unless `K : A^\infty = R` or `Hom(S/m, R/K) = 0` — wait: `A5-547` checks $\dim(R/K)_d = \dim(S/A)_d$ in every degree (`N_K - N_R = N_A - (1-t)^21`) AND `R/K` is generated by a single element? No, `R/K` is generated by **five** linear forms $N$, not one! An arbitrary module with Hilbert function $\dim(S/A)_d$ ($d\ge 1$) CAN be $M_{\text{tf}} \oplus T$ if $M_{\text{tf}} \subsetneq \mathfrak{m}_A$! Thus `A5-454/457/559` **critically depends** on `primdecGTZ` completeness (mitigation: check `sat(K, A)` and verify `Ann(l mod K) = A` directly for one of the 5 nilpotent forms $l$ in Macaulay2!).
3. **Weight-0 truncation subtlety (`A5-474`):** Although `J + m(G_a G_b)` is homogeneous for `tw` with `tw(s_2)=0`, `A5-474`'s claim that polynomial membership equals local membership still rests on `minAssGTZ(J)` removing all components away from 0 (`weight_slice_fiber_relations.py`).

### Risk 4 (HIGH): Real-Arc / Zariski-Closure Audit Gap & Boost Blind Spot (`A5-411`, `A5-415`, `A5-452`) — confirmed
- `A5-452` explicitly concedes that its audit **did not verify** the identification of each computed Rees fiber with the fiber of the Zariski closure of the graph ([a5-kernel-attachments/README.md] (`docs/evidence/a5-kernel-attachments/README.md` L1321-L1323)); for non-reduced/multi-component fibers this relies on `J` being the exact reduced source closure through $z_0$ and `Proj F(I)` agreeing with the strict-transform exceptional divisor set-theoretically.
- On `V` and `VB` (6 incidences), $G_2(\mathbb{C})\times\mathbb{C}^*$ misses the boost direction ([README] (`docs/evidence/a5-kernel-attachments/README.md` L688-L690)), so `A5-411` does **not** exclude limits along off-slice arcs approaching $z_0$ along the boost!

### Risk 5 (MEDIUM): Modular-to-Char-0 Overreach & Ledger Status Inflation — confirmed
- `A5-005`..`A5-009` carry status `proved` in `ledger.tsv` while remaining **strictly modular** (except `A5-006` via `A5-305`), with `A5-009` depending on the conditional `A5-559`.
- `A5-315` (`E8->VB` quadrics over $\mathbb{Q}(i)$) is marked `survives` while its quadrics are **not retained** ([a5-kernel-attachments/README.md] (`docs/evidence/a5-kernel-attachments/README.md` L1229)).
- In `gororoba-math:rocq/quantum/A5W8ArcMatrixRanks.v:15-17`, passing from $\mathbb{Z}[i]$ to $\mathbb{Q}(i)$ and binding the literal matrices to the Cayley-Dickson Pfaffians remain unverified prose.

### Risk 6 (LOW-MEDIUM): Unproven Generic-$s_2$ & Boost-Invariance Generalizations — confirmed
`A5-542` (generic-$s_2$ Rees bidegrees) has **no tracked record** ([a5-kernel-attachments/README.md] (`docs/evidence/a5-kernel-attachments/README.md` L1131)), and `A5-427`'s boost action on `W8, Iso, X` holds only in a truncated quotient (weight margin 4, $s_2^6 = 0$, [L1271-L1273] (`docs/evidence/a5-kernel-attachments/README.md` L1271-L1273)).
