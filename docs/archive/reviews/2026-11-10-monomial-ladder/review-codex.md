Artifact: one-commit Python/JSON/Markdown evidence bundle at `b02ae8d34f99360094a1632b6546e7553847a315`, covering commutative algebra and exact finite-field linear algebra. I read the full diff and relevant parametrization sources.

## Findings, ranked by consequence

1. **FATAL, proved: A5-298 and A5-299 lack a source-bound producer record.**

   `fast_ladder.py:253` always emits `columns` and `map_nnz` in every row, while `fast_ladder.py:273` emits `generators` and does not emit `device`. The decisive degree-seven record instead contains `device`, omits `generators`, and omits both row fields: `float64-xm-nm-p32009-d7-n29.json:1`. All six X float64 records have that predecessor schema.

   The records carry no producer hash, commit, Torch version, or predecessor source. Therefore the current source cannot be identified as their producer. The raw numbers are internally consistent, and the degree-six float result agrees with python-flint, but that calibration does not bind the unverified degree-seven and degree-eight results.

   Consequence: ledger `A5-298:293` has a valid upper bound `996` but lacks a source-bound lower-bound computation. Ledger `A5-299:294` likewise does not yet certify `h_8 >= 1422`.

   Remedy: retain the exact predecessor source and its SHA-256, or replay the current hashed source and record source hash, dependency versions, dimensions, exactness bound, and output hash.

2. **SERIOUS, proved: the float64 exactness promise exceeds its checked input domain.**

   `fast_ladder.py:15` claims every sum has fewer than `2^17` terms. However, `fast_ladder.py:154` sums `self.rank` products, while `fast_ladder.py:169` permits rank growth without a `2^17` guard. The CLI also accepts unrestricted order and batch at `fast_ladder.py:291`.

   I found no unreduced-value path: sparse products at line 260 immediately enter `insert`, reduction ends with `remainder_` at line 155, and basis updates reduce at line 163.

   For the claimed retained sizes, the arithmetic bound itself is sound: X order 34 has `C(37,4)=66045 < 2^17` ambient monomials and maximum recorded rank 12,507; E8 order 14 records 14,756 columns. With `p=32009`, each product is below `2^30` and each relevant sum remains below `2^47`. The defect is the unchecked universal interface, compounded by the producer mismatch above.

3. **SERIOUS, proved: several long independent loops violate the repository’s mandatory parallelism rule.**

   `AGENTS.md:47` rejects serial CPU-bound loops over independent items. Independent generator/basis products run serially in `x_same_ladder.py:146`, `e8_ladder.py:195`, and `monomial_probe.py:49`. Independent multiplication-map construction also runs serially at `fast_ladder.py:251`.

   The later echelon insertions are stateful and are not part of this finding. The independent production stages must use `gororoba_quantum/parallel.py` or a documented repository-approved vectorized mechanism.

4. **SERIOUS, proved: A5-301 states an unbounded result from bounded computations.**

   `ledger.tsv:296` says the truncated spaces “modulo `n^N`” are monomial spans without bounding `N`. The records establish all four incidence/prime combinations through order 12, and only X-minus at 32009 through order 14; `monomial-probe-xm-nm-p32009-n14.json:3` identifies that sole order-14 case. The map row’s plural “same-sign slice ... through order 14” at `README.md:67` overstates the other three cases.

   Remedy: state “through order 12 in all four cases, and through order 14 for X-minus at 32009.” Treat persistence at higher order as a hypothesis.

5. **SLOPPY, proved: the E8 documentation confuses the slice ring with its ambient quadratic algebra.**

   `monomial-ladder/README.md:15` calls `P + P b` the slice ring. The implementation correctly states that the slice ring is
   `R = R0 + R0 b`, inside `P + P b`, at `e8_ladder.py:8`. For example, `w` belongs to `P` but not to `R0`. A5-300 has the same ambiguity at `ledger.tsv:295`.

6. **SLOPPY, proved: the “same host” performance comparison is absent from the records.**

   `monomial-ladder/README.md:38` and A5-302 claim the two degree-six runs used one host. The flint record contains only parameters, ranks, and 705.1 seconds at `flint-xm-nm-p32009-d6-n26.json:1`; the float record adds threads but no host identifier at `float64-xm-nm-p32009-d6-n26.json:1`. The rank agreement is recorded; the host-controlled speed comparison is not.

## Claim dispositions

1. **PROVED:** truncation cannot make `r_N(d)` overshoot if `A_d` and `B_d` are the exact images stated.

   Let `pi_N` be the ambient truncation. The natural map
   `I^d/m_R I^d -> pi_N(I^d)/pi_N(m_R I^d)` is surjective, with kernel
   `(I^d intersect (m_R I^d+n^N))/m_R I^d`. Hence
   `r_N(d)=dim(A_d/B_d) <= h_d`. The transition from order `N+1` to `N` is also surjective, so `r_N(d)` is nondecreasing. Artin-Rees/Krull intersection gives eventual equality because these completed ambient extensions are finite and separated.

   The recursion is exact: multiplication by a generator of order at least `ell` depends only on its source modulo `n^(N-ell)`. `x_same_ladder.py:136` and `e8_ladder.py:185` implement exactly that order schedule for both `A` and `B`.

2. **PROVED after correcting the ambient-ring wording:** the E8 recursion computes in `R0+R0b`, not the whole `P+Pb`. The basis at `e8_ladder.py:122` contains exactly `k[[t,zeta]]+(rho,sigma,a)P` and its `b` multiple, with the odd coefficient truncated one order earlier.

3. **PROVED only for the recorded dimensions, not for unrestricted accepted orders:** the float arithmetic bound above is sufficient for the retained cells. Current-source production of the decisive records remains unproved.

4. **PROVED as linear algebra; COMPUTED only at the retained orders:** a subspace is a monomial-coordinate span exactly when its unique reduced echelon basis consists of singleton rows. `monomial_probe.py:23` applies this to exact spanning sets `g*R` and `g*m_R`.

5. **PROVED and COMPUTED:** `monomial_model.py:19` enumerates the stated generators of
   `M=w^2(a,rho,sig)+w(rho,sig)(a,rho,sig)^2`; lines 46-56 count the monomials surviving multiplication by `(w^2,a,rho,sig)`. The bounded run printed:
   `15, 51, 122, 240, 417, 665, 996, 1422, 1955, 2607`.

6. **FALSIFIED as a certification claim:** the table numbers match the JSON contents, but A5-298/A5-299 claim more provenance than those records hold; A5-301 exceeds its measured order range; A5-302’s host comparison is absent.

## Independent checks

- **COMPUTED:** Python 3.14.9 with python-flint 0.9.0 ran X-minus, `p=32009`, degree 3, order 13:
  `A=361, B=239, r=122`, 3.0 seconds. This matches the retained ladder rows.
- **COMPUTED:** Ruff reported `All checks passed!`; format reported `5 files already formatted`; mypy reported `Success: no issues found in 5 source files`.
- **UNRUN:** the float replay failed before script execution because Torch required a writable temporary directory and the read-only sandbox supplied none.
- **MEASURED preservation:** final `git status --short` is empty; `HEAD` remains `b02ae8d34f99360094a1632b6546e7553847a315`; `origin/main` remains `1e302aed1ba0cbf0f6b95538ed0ccf9a4f5cc6b3`; `git diff --check origin/main...HEAD` is clean.

## New hypotheses

- **HYPOTHESIS:** `h_8=1422`, not merely `h_8>=1422`. Falsifier: any later `r_N(8)>=1423`. Cheapest decisive test: extend the exact K2 Hilbert calculation to degree 8; an upper count of 1422 closes the equality immediately.
- **HYPOTHESIS:** `h_9=1955` and `h_10=2607` at X-minus, 32009. Falsifier: a K2 upper count below either model value or a truncated rank above it. Cheapest test: compute `HF(k[y]/K2,d)` for degrees 8-10 before launching longer ladders.
- **HYPOTHESIS:** X-minus at 32029 also has `h_7=996`. Falsifier: an exact additional relation below degree 8. Cheapest decisive test: a source-bound degree-seven ladder at order 29, followed by comparison with the already retained K2 upper count 996.

Verdict: the truncated-image construction is mathematically sound and cannot overshoot. The PR does not yet earn its two new certified ledger claims because the decisive float64 records demonstrably came from an unidentified producer version. A current-source, hash-bound replay or retention of the exact predecessor source is the essential repair.
