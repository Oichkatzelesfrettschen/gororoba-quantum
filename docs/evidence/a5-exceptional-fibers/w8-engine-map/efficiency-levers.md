# Efficiency survey of the A_5 rank engine (Sonnet Explore agent, 2026-11-08, read-only; transcribed by the session)

Ranked levers (the agent's tags: TESTED, PROBE, IDEA; [M] measured, [C] computed, [H] hypothesis):
1. Dead rows of L (IDEA, exact): g*m = 0 in k[t]/(J+m^N) when deg g + deg m >= N; at W8 d=6, N=19 the rows of
   degree >= 17 (>= 16 for degree-3 generators) are zero but are stored dense. Up to about 2x on L (103 GiB); measure
   by counting order_walk levels on the d=6 export.
2. uint16 storage with per-panel float64 upcast (p < 2^15): L 103 -> 26 GiB, W 69 -> 17 GiB [C]; exactness unchanged.
3. Store only the free part of each RREF basis: factor 1 - rho (0.33 at rho 0.67); also cuts reduce/update flops.
4. In-place panel update at E:336-337: removes three B-sized temporaries (about 52 GiB at d=6 [C]).
5. Basis copy at E:1173: needs chunked or spilled `new`, an alias saves little because insert rebinds B.
6. --chunk (TESTED knob, optimum unmeasured): marshaling transient 121 B/entry x chunk x free.
7. GPU PLUQ / INT8 modular GEMM (PROBE, outside the repository: a local probe directory holding pluq.py and
   modgemm13.py; docs/design/gpu-exact-modular-linear-algebra.md): PLUQ n=16384 0.58 s vs FLINT 248 s on the laptop
   RTX 4090 (16 GiB); KMAX 32768 inner dimension; returns PLUQ, needs TRSM glue to RREF. Pays for the W8 d=6 closure
   (14-19 h CPU), not where the Singular export dominates (X- d5: export 99 %).
8. FFLAS/FFPACK and LinBox are installed as headers/libraries (no binding in the CI interpreter); IDEA.
9. Preflight terms (E:1086, E:1088): replace with measured 0.10 L walk and rho-based W.
Stream L by degree level (hold two adjacent levels): removes the 103 GiB residency at unchanged flops (IDEA).
L's density is recorded nowhere; Wiedemann does not fit the dense closure. No exact F_p linear algebra in gororoba-open.
Engine word size float64 (8 B/entry); python-flint 0.9.0 nmod_mat has no numpy constructor. cupy 14.2 and torch 2.15
with CUDA live in the system python3, not in the CI interpreter. OPENBLAS_NUM_THREADS is unset in every runner.

## Measured after the survey (2026-11-09, laptop, W8 N = 19 export qB.txt, D = 235,543)
Quotient monomials by degree 0..18: 1 7 28 84 209 455 896 1632 2793 4543 7084 10652 15457 21560 28609 35448 39922 38752
27411. Degree >= 17: 28.1 % (rows of L that vanish exactly for generators of minimum degree 2, since every term of g m
lies in m^19); degree >= 16: 45.0 % (minimum degree 3). Lever 1 is 1.4x to 1.8x on L, not 2x [computed].
Structural density of L if NF(g m) kept every term at degree >= deg m + deg_min(g): 0.31 (min degree 2) and 0.22
(min degree 3) [hypothesis: dp normal forms modulo the non-homogeneous J can lower degree; measure nnz on the d = 4
export before relying on it].
