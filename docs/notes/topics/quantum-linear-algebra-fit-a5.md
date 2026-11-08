# Quantum linear algebra against the A_5 fiber computations: 2024-2026 survey and fit

Status: survey of 2026-11-05. Companion records: [finite-field-qlsa-alternatives.md](finite-field-qlsa-alternatives.md)
(a finite-field QLSA proposal and its refutation) and `docs/local/hhl-falsify/verdict.md` (the real-amplitude HHL/QSVT
pipeline at N = 32); paths under `docs/local/` name the A_5 session's ignored run records, whose numbers this note
restates. Identifiers were resolved through the arXiv API on 2026-11-05. Every cited paper has a note under
[notes/papers/](../papers/) and an entry in [SOURCES.json](../../SOURCES.json) (GSLW 1806.01838 was registered
before); its PDF and a Markdown transcription sit under `computer-science/quantum-algorithms/` in
gororoba-documents-public for the six CC-licensed versions and in gororoba-documents-private for the rest. The
statements below were read in those transcriptions at the cited pages; 2609.28901 pages 1-12 and 2608.23929 pages
1-16 were also read as page images.

## Verdict

No quantum algorithm published through 2026-11-05 shortens any computation the A_5 fiber program has in flight, on
the hardware the account reaches (Heron r2, 156 physical qubits, no error correction) or on a fault-tolerant machine
of any size now projected. Confidence high. It drops with a polynomial-time quantum algorithm for exact rank, standard
bases or Hilbert functions over F_p that has a proven speedup over O(n^omega) elimination at 10^4 columns or more, or
over Buchberger/F4 on positive-dimensional ideals. No source in the arXiv record supplies one.

The mismatch is structural, not a matter of scale. The fiber program needs exact outputs in F_p (ranks, normal forms,
relation spaces, prime components). The quantum linear algebra literature splits into two families. Neither delivers
exact F_p outputs with a speedup:

1. Real-amplitude solvers (HHL, QSVT, adiabatic and kernel-reflection QLSS). They prepare a normalized state
   proportional to A^-1 b to precision epsilon. Their cost is linear in the condition number, and the program's
   matrices are singular by construction.
2. Exact finite-field circuits. These are reversible elimination circuits and Fourier sampling over F_p^n. They run
   the same arithmetic count as classical elimination, and their purpose is to serve as a subroutine inside Grover or
   Simon searches. They do not make linear algebra faster.

## Fit by in-flight computation

Stage costs come from `docs/local/scope-n18/scope.md` and from
[a5-exceptional-fiber-findings.md](a5-exceptional-fiber-findings.md).

| In-flight computation | Dominant stage (measured) | Output it needs | Quantum candidate that would have to touch the stage | Why it misses |
|---|---|---|---|---|
| E8-bar -> N- degree 5 at N = 18 (r_18 against the per-block targets 215, 197, 270, 270) | single-threaded Singular std of J + m^N: 96 % of wall at N = 17 (43,900 s), forecast ~29 h at N = 18 | reduced standard basis over F_p, then exact rank | none exists for standard bases. The only quantum polynomial-system work is Macaulay-matrix HHL (Chen-Gao 1712.06239; Ding-Gheorghiu-Gilyen-Hallgren-Li 2111.00405; Li 2510.05588) and Grover-XL (Faugere et al. 1712.07211) | these find a solution point of a zero-dimensional system with few solutions. 2111.00405 proves a condition-number lower bound in the solution's Hamming weight, under which Grover search beats Chen-Gao "in many (if not all) cases". The fiber program needs the quotient k[t]/(J + m^N) of a positive-dimensional germ, which has no solution point to sample |
| W8 -> N- degree 5 at N = 16 (r_16 against 4116) | closure (echelon over F_p) and products; preflight 97.8 GiB | exact F_p rank per character block | reversible Gaussian elimination over any GF(p^l) (Lee-Jeong-Kim 2609.28901) | it uses O(n^2 m) field multiplications and additions, the same count as classical elimination (its Table 3 against the classical O(n^2 m)). Its construction covers full-rank matrices; rank-deficient input "is doable, but substantially complicates the construction" (footnote 1), and the rank is the unknown here. Its data register alone is l ceil(log2 p) m n qubits, 15 qubits per F_32009 entry. The W8 run at N = 12 has 5,152 columns in block 0 and 98,280 products over four blocks (`docs/local/w8-d5-probe/n12.out`), so one block's register is about 15 x 5,152 x 24,570 = 1.9 x 10^9 logical qubits before arithmetic workspace, against 156 physical qubits on Heron r2 |
| Exact degree-5 membership on the 91-dimensional space sqrt(K2)_5 / K2_5 (E8-bar) | membership of degree-5 products in J + m P_5: a standard basis again | exact membership in F_p | same as the std row | same as the std row |
| Decomposition of K2 : P (W8) and prime decomposition of the Iso K2 | minAssGTZ / minAssChar beyond 40,000 s | prime components over F_p | none. Kedlaya's zeta-function algorithm (math/0411623) is polynomial in g and log q for curves only. Point-count approximation over F_q (Maeda-Yano 2608.23929) takes one Laurent polynomial | the Iso primality proof (`docs/local/iso-section-probe/`) already reduces to 23-point sections that Singular settles in about 1 s. 2608.23929 bounds its error by epsilon q^(n + s/2 - rho), where s is the number of monomials and rho the rank of the augmented support matrix. A dense quadric in 17 variables has s = 153 monomials, and homogeneity makes the first row of U dependent on the others, so rho <= 17 and the error scale is at least epsilon q^76.5, against at most (q - 1)^17 torus points. The paper counts torus points of one polynomial; its concluding remarks give no a-priori reduction to ordinary affine counting, whose approximation it shows #P-hard for systems (Appendix D). K2 is a system of 68 to 148 quadrics |
| Characteristic-zero Q(i) replays (arc certificates, degree-2 lifts by rational reconstruction) | Singular over Q(i) with coefficient growth | exact identities over Q(i) | none; the exact-arithmetic quantum circuits are finite-field only | out of scope for every family above |
| Kernel-plane limits of the 32 x 32 L_y along arcs | 32 x 32 kernels over a Laurent-series ring, microseconds per point | exact kernels | HHL/QSVT at N = 32 | refuted in `docs/local/hhl-falsify/verdict.md`: L_y is singular on the zero-divisor locus (rank 20, 24 or 28), so it has infinite kappa; a generic L_a needs 497 Pauli terms and 9 LCU ancillas; and the output is magnitudes without signs |

## The 2024-2026 real-amplitude solvers, for the record

The asymptotics of the quantum linear-system problem (QLSP) are now settled.

| Result | Statement | Consequence for the program |
|---|---|---|
| Costa, An, Sanders, Su, Babbush, Berry 2111.08152 | discrete-adiabatic QLSS in O(kappa log(1/epsilon)), optimal | kappa is infinite on the zero-divisor locus |
| Jennings, Lostaglio, Pallister, Sornborger, Subasi 2305.11352 (PRX Quantum 6, 040373, 2025) | randomized adiabatic QLSS, rigorous bound 837 kappa block-encoding calls at epsilon = 10^-10 | same |
| Dalzell 2406.12086 | kernel reflection; 56 kappa + 1.05 kappa ln(1/epsilon) + o(kappa) | same |
| Low, Su 2410.18178 (Quantum 10, 2041, 2026) | Theta(1/sqrt(p)) queries to the state oracle, near-optimal in kappa | same |
| Mori, Kikuchi, Benedetti, Rosenkranz 2601.16697; Patel 2609.22445 | lower bound Omega(kappa sqrt(s) log(1/epsilon)) in the sparse-access model; 2609.22445 calls it near-optimal | the dense 32 x 32 L_a (s = 32) and the dense closure blocks gain nothing from sparsity |
| Tu et al. 2502.11239 | fault-tolerant estimate: an HHL advantage over conjugate gradient appears near N = 2^33 to 2^48 with about 10^5 physical qubits at physical error 10^-5 | the program's real-valued matrices are 32 x 32, and its large matrices are over F_p |
| Morales et al. 2411.02522 | survey and taxonomy of the post-HHL solvers | reference |
| Chia, Gilyen, Li, Lin, Tang, Wang 1910.06151 | dequantization of QSVT for low-rank inputs under sampling access | removes the exponential advantage wherever the input is close to low rank |

## Other recent finite-field quantum algorithms

| Result | What it computes | Relation to the program |
|---|---|---|
| Jordan et al. 2408.08292 (Nature 646, 831, 2025), decoded quantum interferometry (DQI) | approximate optimization (optimal polynomial intersection, max-LINSAT) over F_p, reduced to decoding | targets NP-hard approximation, whereas the fiber program's linear algebra is exact and classically polynomial; no matching problem |
| Buhrman, Spalek quant-ph/0409035 | matrix-product verification over any integral domain in O(n^(5/3)) time, against Freivalds O(n^2) | a polynomial speedup through a Szegedy quantum walk. It needs quantum random access to the matrices, and the membership receipts verify in seconds classically |
| Belovs 1103.0842 | span program for the rank problem | query complexity only; no time-efficient F_p solver |
| van Dam quant-ph/0405081 | zeta zeros as eigenvalues of efficient unitaries (Fermat hypersurfaces) | no unitary is known for the fiber schemes |

## The part already on quantum hardware, and the qubit-native field

The Iso section argument draws its generic linear forms from ANU QRNG files (`draw-2026-11-05T182851Z.json` and the
three later draws, recorded in `docs/local/iso-section-probe/coefficients*.json`). The strata verification
(`docs/evidence/a5-zero-divisor-strata/verify_strata_independent.py`) also takes QRNG seeds. These are the program's
quantum-hardware inputs, and they serve the seed rule of AGENTS.md. The mathematics needs only genericity: the forms
must avoid a proper closed set, which a uniform choice does with probability at least 1 - deg/p.

A probe in the qubit-native field F_2 fails the mutation test of
[algebra_circuit_rules.md](../algebra_circuit_rules.md#hardware-probes) by construction. Reduction mod 2 sends every
structure constant +-1 to 1, which erases the sign cocycle that creates the zero divisors. Ranks of
`cd_core.left_mult_matrix(32, a)` show it: the invertible a = e_0 + e_1 and e_24 + e_18 and the zero divisors
e_29 +- e_5, e_9 +- e_23 and e_1 +- e_10 have real ranks 32, 32, 20, 28 and 24, F_3 ranks equal to the real ones, and F_2
rank 16 for every one of them. An F_2 probe therefore returns the same kernel whether or not a is a zero divisor. F_3 keeps the signs, but it costs two qubits per trit
and needs a non-native Fourier transform over Z_3, and no fiber question depends on the 4-, 8- or 16-dimensional
instances that fit.

The acceleration lever is classical. `scope.md` records the engine v11 quotient-mode product and closure loops as
serial (`fiber_rank_v11.py` around lines 861-909 and 1166-1189), which bears on the W8 closure-bound runs.

## Addendum 2026-11-07: the t-space slice ladder

The Iso fiber question moves off the 23-variable blowup chart, which failed in six formulations (ledger A5-070,
A5-071, A5-174, A5-176, A5-181, A5-205), onto a six-variable test. K2 holds the quadratic relations of F(I)
(`k2_hilbert.py`), and k[y]/K2 is a five-dimensional domain (A5-058 to A5-060). F(I) = k[y]/K2 therefore holds exactly
when the analytic spread is 5. That happens exactly when the origin lies on the closure of
V(J, l1(G), ..., l4(G)) minus V(I) for generic forms l1..l4 in the t-variables. The junk through the origin
saturates away by the linear form t2 (A5-068). The preregistration and the controls (X+ and X- with k = 2 and 3,
Iso with k = 3 and 5) live in `docs/evidence/a5-exceptional-fibers/structure/arcs-iso-w8/tslice/`.

The ladder's dominant stage is a saturation, Qk : t2^inf in dp, followed by evaluation at the origin. It falls in the
standard-basis row of the fit table, so the verdict above applies unchanged. A search of arXiv for 2026-09-01 to
2026-11-07 returned no quantum algorithm for standard bases, saturation, Macaulay-matrix rank or exact rank over a
finite field. It ran on 2026-11-07 for quantum together with Groebner, Macaulay matrix, polynomial system, finite
field, matrix rank or Gaussian elimination. The finite-field result it found, Imran 2610.28368, gives hidden
parabolic subgroups of GL_n over finite chain rings by Fourier sampling. That is a hidden-subgroup problem rather than
an elimination problem.

The quantum hardware's part in the ladder is its forms. The ladder decides only for forms generic with respect to a
possible lower-dimensional E0 and to the exceptional divisor. A form drawn uniformly from the ANU QRNG avoids each
closed bad set with probability at least 1 - deg/p, where deg is the degree of the bad set in the form coefficients.
For the k = 4 slice that degree depends on deg(E0), which the record does not bound, so a single "on" carries no
numerical confidence. Independently drawn form sets at each prime are the available strengthening; the controls and
the first k = 4 rows share one draw across both primes.
