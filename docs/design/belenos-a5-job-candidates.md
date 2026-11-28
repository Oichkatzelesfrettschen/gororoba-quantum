# Belenos jobs for the A_5 ledger

Design candidates only: nothing here is submitted, and every `--submit` waits for the owner's approval of a written case.
The capability facts live in [belenos-capabilities.md](../notes/quandela/belenos-capabilities.md); the rows are those of
[ledger.tsv](../evidence/a5-exceptional-fibers/ledger.tsv) with status open, stalled or boundary (29 rows: 13 open, 10 stalled,
6 boundary), read against the reconciliation of the 2026-11-27 red team (no IQP or sparse-SELECT shortcut; coset blocks of the
kernel map resolve on 2 to 4 qubits; A5-633 is proved for every n).

## Result

No Belenos job closes any of the 29 rows. One candidate (C1) moves a hardware property that no rank or Groebner run can measure
and would open a new row; the rest are rejected with their reason. The ledger shrinks only through classical engines: row
A5-332 (stalled at 41,000 s in Singular) already records Macaulay2 deciding the same weight-slice ideal prime in under 2 minutes
modulo 32009, and A5-258 and A5-283 are method changes to the same engines.

## Disposition of the 29 rows

| Rows | Content | Disposition |
|---|---|---|
| A5-327, 328, 329, 330, 331, 332, 404, 406, 409, 605 (stalled) | Groebner bases, Rees eliminations, syzygies, normalization and primary decomposition over F_p, stopped by memory or timeout | rejected: ideal membership and primary decomposition have no linear-optics encoding; boson sampling estimates permanents and quantum counting returns reduced point counts only (reconciliation Q3, Q4) |
| A5-258, 263, 283 (open); 264, 265, 266, 267 (boundary) | engine choices, zero-row shares, K2-span witnesses, membership, a run-level null, scan order | rejected: software and exact-arithmetic questions |
| A5-250, 254, 259, 278, 325, 389, 660 (open) | real-arc limit sets, Klein torus, A_6 stabilizer, Hilbert-dimension match, tangent cones, Gauss map, limiting kernels | rejected: symbolic or geometric statements decided by exact computation |
| A5-628, 646 (boundary) | literature readings of two papers' boost algebras | rejected |
| A5-242, 632 (open) | Heron device readings of the full kernel map and the complex kernel map; the falsifiers name an IBM run | not movable: L_a of A_5 is 32-dimensional and a unitary on 32 modes exceeds the 24-mode chip; a 16-dimensional block with a full-defect Gram spectrum dilates to 32 modes (Halmos); the claims concern Heron gate noise |
| A5-202 (open) | a static per-shifter map beyond per-mode efficiencies, on qpu:ascella | movable as a transfer to Belenos: candidate C1 |

## Candidates, ranked

### C1. Static per-shifter map on Belenos (hardware property; opens a new row)

- **Observation.** A5-202 reads r 0.446 for the gain map with the efficiency-only model at r 0.484, so the shifter map's own
  increment is r 0.055 (p 0.28) for gain and 0.213 (p 0.041) for offset on Ascella; the preregistered "carries" is confounded with
  the frozen per-mode efficiencies. The Belenos record holds many returned meshes with counts (belenos_mesh, bdsc_diagnostic).
- **Encoding.** A_5 coset blocks of L_a for a = e1 + e26 (8 blocks of 4 x 4 over the cosets of span{1, 26}; two blocks of rank 2,
  singular values {2, 2, 0, 0}, six orthogonal blocks with all singular values sqrt 2). With alpha = 2, V = B / alpha has Gram
  spectrum in {0, 1/2, 1}, so the exact Halmos dilation of `scripts/qd_box_kite_cases.py` (entries in Q(sqrt 2)) gives an
  8-mode unitary per block, three blocks per 24 modes. A photon prepared in a right singular vector of the block reads
  in-block probability sigma^2 / alpha^2: 1 on the support of a rank-2 block, 0 on its kernel, 0.5 on an orthogonal block. The
  preparation is a rotation inside the same mesh (U times a block orthogonal P), the photon enters a block's local mode 0, so each
  block's local mode 0 must sit on a source mode (0, 2, 4, 6, 8, 9, 12, 13, 16, 18, 20, 22).
- **Exact prediction.** [belenos_a5_block_prediction.json](../evidence/quandela/belenos_a5_block_prediction.json), written by
  `scripts/belenos_a5_block_prediction.py` (Perceval 1.3.1 SLOS equals the exact value to 1e-9 on every prepared input; the
  test file fixes the numbers). Global nullities 4 (e1 + e26), 8 (e1 + e10) and 0 (e1 + e17). A basis-mode photon reads 0.5 on
  every block, so a basis input cannot see the nullity (ledger row A5-371).
- **What the counts estimate.** The returned mesh's own propagation predicts each iteration's share; the statistic is the
  increment of r over the efficiency-only model on iterations with fresh seeds, the A5-202 statistic.
- **Falsifier.** A preregistered fresh-seed increment at alpha 0.005 that reads zero or negative (as A5-202 already does for the
  gain model, p 0.28). The offset increment (r 0.213) is the live hypothesis.
- **Offline gate before any approval.** Refit the frozen-map decision on the retained Belenos runs
  (`qd_belenos_mesh.static_cross_validation`, `efficiency_record`) and keep the candidate only if the offset increment reproduces
  there; the outage changed the chip (HOM 88.8 %, transmittance 5.37 % against 88.2 % and 5.23 % on 2026-11-07), so maps frozen
  before the outage are stale and the refit must use runs after it. The seeds come from an ANU draw (AGENTS.md "Seeds"); the draw
  file and indices are assigned when the case is written.
- **Samples and seconds.** The bdsc_stationarity shape: 24 iterations by 100,000 samples, 165 to 176 s, largest cap 200,000
  shots, at most 1.2 credits, one job; the case plans the first job as the measurement.
- **Why a classical rank does not answer.** The nullity is exact and known; the quantity under test is the chip's realization
  error of a known unitary, a hardware property.
- **Attack first.** The served mesh differs per source and per seed, so the per-shifter map cannot be separated from the
  per-mesh variance (std 0.0515) without many seeds; the 2026-11-28 runs read 0 of 15 presences on source 22 where the packet
  law predicted dozens, so the off-cone background is itself unstable; a fresh-seed test with 24 iterations has little power
  for an increment near r 0.05.

### Rejected candidates

| Candidate | Reason |
|---|---|
| C2. Basis-input intensity to read a nullity | constant 1/2 on every block of every operand (A5-371); carries no nullity information |
| C3. Prepared-input nullity of A_5 coset blocks as an A_5 result | the answer is the exact integer already proved (A5-633, every n); a job reproduces it with chip error, so it is the payload of C1 and no separate case |
| C4. Second moment of the singular values by a two-photon interference | the classical rank costs milliseconds; two photons cost about 74 shots per sample and run at HOM 88.8 %, below the 90 % floor |
| C5. Whole-matrix nullity of the 32-dimensional L_a | needs a 32-mode unitary, beyond the chip's 24 modes |
| C6. A certified bound that replaces a stalled Groebner or normalization run | no linear-optics encoding of ideal membership; boson sampling certifies permanents, not ideals |
| C7. The 16-dimensional kernel-direction certificate (A_4, x = (e1 + e10)/sqrt 2) | already designed and run to qualification (bdsc.md); it moves no A_5 row and stops at native compilation (M2) |

## Open items

- hypothesis: the offset increment of A5-202 reproduces on Belenos refits; the check is the offline gate above.
- not run: the refit of the frozen-map decision on post-outage Belenos runs.
- unsourced: the Belenos `t_out` per-mode figures of 2026-11-27 (the live record carries lists; the retained read is a class
  map only).
