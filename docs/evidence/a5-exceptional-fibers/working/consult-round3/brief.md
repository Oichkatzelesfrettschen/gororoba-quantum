# Consult brief: A_5 exceptional fibers and the dimension-32 classification after the second distribution round

You review a computational algebraic-geometry program. Read this brief, then the three documents beside it:
`a5-exceptional-fiber-findings.md` (every method, result and hypothesis ledger of the fiber computations),
`dimension32-global-topology-program.md` (the open work program) and `kernel-bundle-residuals.md` (the kernel-bundle
residual results). Raw logs sit under `../distribute/out/` and `../runs/`. Read only; run no solver. Answer every
question at the end, with a falsifier for each recommendation, and mark which claims you checked in the files.

## Goal

Classify the dimension-32 (sedenion-doubling, `A_5`) two-sided rank strata topologically. Components, regularity and
kernel bundles on nullities 8, 12, 16 are done. The current item is attachments: how the kernel spheres `S(ker L_y)`
specialize along each closure incidence. Its algebraic core is the special fiber `F(I) = (+) I^d / m I^d` of the
Pfaffian kernel-coordinate ideal `I` at a boundary orbit, computed over `F_32009` (i = 10754) and `F_32029`
(i = 9115). From the fiber's reduced components, formal arcs and the kernel-plane limits along them give the attaching
maps.

## What works

- **Degree-by-degree membership rank** (fiber_cone_driver.py): products of d generators reduced modulo J, membership
  in J + m P_d in a global ordering, FLINT rank. It certifies h_d degree by degree.
- **Quadric ideal K2 structure**: `radical` then `minAssChar` in Singular decomposes X- in 1 s.
- **Formal arcs on the normalization** certify the degree-4 prime of E8-bar -> VB over F_32009.
- **Second prime** agrees on every count computed at both primes.

## Results, as of 2026-10-30 15:45 UTC

| Pair | h_1..h_d | Relations beyond K2 | Largest successful stage |
|---|---|---|---|
| X+-, X- | 15, 51, 122, 240 | none through degree 4 (240 is the K2 value) | degree 4: 14,480 s, Kaggle CPU |
| Iso | 17, 85, 265 | none through degree 3 | degree 3: 1,837 s |
| E8-bar -> N+ | 21, 83 (148 quadrics, both primes) | | degree 2: 13,823 s |
| E8-bar -> N- | 21, 83 (148 quadrics, both primes) | | degree 2: 13,827 s |
| W8 -> N- | 24, 156 (both primes) | | degree 2: 10,470 s (second prime) |
| E8-bar -> VB | 10, 34, 80, 155 | none through degree 4 | degree 4: 5,184 s, 2.4 GB |

K2 structure: X- and X+ (both primes): non-radical, radical h = 12, 45, 112, 225, one prime of projective dimension 3,
degree 12. E8-bar -> VB: radical, two primes (3, 3) and (3, 4). E8-bar -> N+: non-radical, primes (4, 11) and (3, 4).
Iso and W8: not finished.

## Failures of the last round, with their mechanisms

| Job | Outcome | Mechanism as read from the logs |
|---|---|---|
| E8-bar -> VB degree 5 (host, 15 GiB cap) | products stage timeout at 12 h (exit 124), 8.3 GB at 2.5 h | the d5 products Singular script: products of 5 generators reduced modulo J |
| Iso degree 4 (Kaggle CPU) | products stage timeout at 10 h | 640 targets, 17 generators |
| W8 -> N- degree 3 (Kaggle CPU, 30 GB) | SIGKILL after 18,999 s | memory; 600 targets, 24 generators; 14 GB on the host earlier |
| Iso charts (17) and W8 -> N- charts (24) | 40 of 41 stopped at the 45-minute cap inside `minAssChar` | each chart sets one y_i = 1 in K2, then radical, then minAssChar; radical finished on 9 Iso and 14 W8 charts; affine dimension 5 (Iso) and 6 (W8); W8 chart 10 finished: one prime, dimension 6, 37 linear generators |
| TPU smoke kernel | queued 24 h, never assigned | TPU queue |
| Every earlier global elimination (pivot saturation, msolve, std of candidate, minAssGTZ) | stalls from 2 h to 12 h, up to 209 GB | recorded in the findings note |

## Kernel-bundle residuals and nullity 4

- `xi_R` over `V_2(R^7)` is actually nontrivial (exact stabilizer action plus `pi_4(SU(3)) = 0`).
- Nullity-12 smaller reductions: topological `Sp(3)` exists; equivariant excluded on B9 and VB by one-signed weights;
  V pointwise yes, gluing open.
- Component group: `pi_0(K) = pi_0(Z_K(G_2))`, each transport slot `4 R + 4 R^7`, centralizer `GL(4) x GL(4)` per slot,
  96 unknowns.
- Nullity-4 strata: generic orbit rank 16, real moduli 11, 11, 9; classes come from the Gauss map into `Gr(2, C^16)`.

## Compute available

| Resource | Capacity | Limit or cost |
|---|---|---|
| Build host | 12 cores, 62 GB RAM (about 37 GB free with other jobs), RTX 4070 Ti 12 GB | systemd-oomd kills the session above 90 % RAM plus swap; every heavy job in a capped scope |
| Kaggle CPU | 5 concurrent sessions, 4 cores and 30 GB each, 12 h per session | weekly GPU 30 h, TPU 20 h; reset Fri 2026-10-30 17:00 PDT |
| Kaggle GPU host | 2 sessions, used as 4-core 29 GB hosts | Singular uses no GPU |
| Azure (trial credit, spending limit on) | two deallocated Standard_FX4mds_v2 VMs (4 vCPU, 84 GiB, 0.547 USD/h), eastus and westus2, 4-vCPU quota per region | one written case per run |
| AWS (free plan, 100 USD credit) | free-tier types only, largest m7i-flex.large (2 vCPU, 8 GiB) | session login expired |
| GitHub Actions | 4 CPU, 16 GB, 6 h per job | overflow |
| qBraid Lab | 100 free CPU hours, about 1.8 vCPU | needs a written case |

## Questions

1. Decompose each failure above to its first-principles cause. For the products-stage timeouts, what dominates: the
   number of products, the reduction modulo J, or the membership step? What cheaper formulation computes h_d, or
   decides the only open question per degree (whether F(I)_d is smaller than (k[y]/K2)_d), without forming all
   products?
2. The chart decompositions finished radical on 23 charts but stalled in `minAssChar`. Propose a decomposition route
   for the Iso and W8 quadric schemes that fits 45 minutes to 12 hours per job, with a stated memory estimate.
3. Which result here is the strongest structural lever? Name the pattern across pairs (for example K2 generating F(I)
   through every computed degree, the sign symmetry, agreement across primes) and what it lets the program skip.
4. Assign the open work (degree 3 for W8, degree 4 for Iso and X beyond, degree 5 for VB, chart decompositions,
   E8-bar -> N- K2 structure, arcs, kernel-plane limits, the component-group solve in 96 unknowns, the nullity-4 Gauss
   map) to the compute resources above, cloud first, with the expected time and memory of each job and the reason
   for its substrate.
5. Which conclusion in the three documents do you find unsupported or wrong? Quote the line.
