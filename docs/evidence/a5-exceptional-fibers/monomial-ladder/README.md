# Truncated ranks of the fiber cone by monomial linear algebra

The fiber cone F(I) = ⊕ I^d / m_R I^d of a slice ring R that sits inside a power series ring P has
truncated ranks that need no standard basis. With n the maximal ideal of P, A_d the image of I^d and B_d
the image of m_R I^d in P / n^N,

    r_N(d) = dim A_d − dim B_d ≤ h_d = dim I^d / m_R I^d,

with equality once N is large, and h_d ≤ HF(k[y]/K2, d) because the defining ideal of F(I) contains K2.
A cell is exact when r_N(d) meets HF(k[y]/K2, d).

| File | Role |
|---|---|
| `x_same_ladder.py` | the slice ring of the same-sign incidences X− → N− (`xm-nm`) and X+ → N+ (`xp-np`), R = k[[t]] + (a, ρ, σ) k[[a, ρ, σ, w]], and the ladder on python-flint |
| `e8_ladder.py` | the slice ring R0 + R0 b of E8-bar → N− (`e8-nm`) and E8-bar → N+ (`e8-np`) inside the quadratic algebra P + P b, b² = X (X − s), with R0 = k[[t, ζ]] + (ρ, σ, a) P, and the ladder on python-flint |
| [e8_target_rank.py](e8_target_rank.py) | prepares an exact basis of (sqrt(K2)/K2)_d and computes its truncated image modulo the full m_R I^d closure; degree 5 is the 91-dimensional positive control and degree 6 the 140-dimensional frontier |
| [e8_loader_check.py](e8_loader_check.py) | writes or byte-compares `target-records/loader-check.json`, the order-4 loader agreement of the four E8 targets |
| `fast_ladder.py` | the same spaces with a batched float64 echelon over F_p (torch on CPU), exact for p < 2^15 |
| `fast_ladder_blocks.py`, `fast_ladder_blocks_resumable.py`, `ladder_checkpoint.py` | the same arithmetic with block storage; the resumable successor adds a verified checkpoint manifest and leaves the bytes of the first, which the order-34 record binds, unchanged |
| `monomial_probe.py` | test of whether the truncated I and m_R I of the same-sign X slice are spans of monomials |
| `monomial_certificate.py` | exact check that I equals the monomial ideal M (membership of every G_j and a rank over M / q M, then Nakayama) and the Singular script for the kernel L of k[y] → P[M T] / q P[M T] |
| `e8_monomial_probe.py` | the monomial-span test on the E8-bar slice in five coordinate systems (negative at order 7) |
| `e8_closure_probe.py`, `e8_closure_rank.py` | truncated and exact tests that the E8-bar slice ideal is an ideal of P + P b |
| `monomial_model.py` | Hilbert function of ⊕ M^d / q M^d for the monomial ideal M = w² (a, ρ, σ) + w (ρ, σ) (a, ρ, σ)² of P and q = (w², a, ρ, σ) P |
| `records/` | one JSON record per run; `flint-*` from the python-flint ladders, `float64-*` from `fast_ladder.py`, `monomial-probe-*` from the probe, `monomial-certificate-*`, `slice-ring-*`, `e8-ideal-closure-*` and `e8-fiber-cone-*` from the certificates |

## Same-sign X at p = 32009

Each row gives r_N(d) at the orders run; the last column is HF(k[y]/K2, d) of `../k2-hilbert.jsonl`.

| d | r_N(d) by order N | HF(k[y]/K2, d) |
|---|---|---|
| 1, 2, 3 | 15, 51, 122 at every order from 7, 10, 13 | 15, 51, 122 |
| 4 | 159 (16), 240 (18, 20, 22) | 240 |
| 5 | 201 (19), 417 (21, 23, 25) | 417 |
| 6 | 248 (22), 496 (24), 665 (26, 28) | 665 |
| 7 | 300 (25), 582 (27), 996 (29, 31) | 996 |
| 8 | 1,133 (32), 1,422 (34) | 1,422 |

Degrees 1 to 6 reproduce the certified values (ledger A5-167 and its neighbors). Degrees 7 and 8 meet
HF(k[y]/K2, d) = 996 and 1,422 (`records/x-same-k2-hilbert-d10.jsonl`); the certificate below proves
h_d = HF(k[y]/K2, d) in every degree, so these cells check the ladder against it.

Provenance of the float64 records. `float64-xm-nm-p32009-d8-n32.json` (degrees 1 to 8 at orders 11 to 32) and
`float64-e8-nm-p32009-d3-n14.json` carry the SHA-256 of `fast_ladder.py` and of the ring module in this directory
and the torch, numpy and scipy versions; they reproduce every value an earlier version of the engine had given
for those cells. `float64-xm-nm-p32009-d6-n28.json`, `-d7-n31.json` and `-d8-n34.json` come from that earlier
version and carry no source digest; the order-34 replay
with the hashed engine reproduced degrees 3 to 7 (122, 240, 417, 665, 996 at orders 19 to 31) and was killed in
the degree-8 cell twice: at a 20 GB cap, and under a 40 GB cap by the host's own out-of-memory killer at 24.7 GB
resident while other jobs filled the 54 GB machine. `fast_ladder_blocks.py` then replayed the order-34 cell:
`float64-blocks-xm-nm-p32009-d8-n34.json` carries the source digests and gives every row of the earlier record
(15, 51, 122, 240, 417, 665, 996, 1,422 for degrees 1 to 8; A = 12,507 and B = 11,085 at degree 8) at 13.0 GB peak
in 3,690 s on an 8-vCPU, 32 GB Azure D8ds_v6 (torch 2.15.0, 8 threads), with its step log and `time -v` output
beside it.

`fast_ladder_blocks.py` is the same arithmetic with block storage: the echelon form grows by row blocks and never
copies itself, a finished space is held as uint16, every step prints its rank and peak memory, the record is
rewritten after every degree and `--checkpoint` makes a run resumable. On the degree-5 cell at order 25 it gives
the rows of `fast_ladder.py` (417 at degree 5); a single comparison on one host (8 threads) read 2.86 GB peak
against 4.68 GB and 338 s against 478 s, measured once and not retained as a record, so no digest or receipt
backs those four numbers. `fast_ladder.py` and `fast_ladder_blocks.py` keep their bytes, so the digests in the
retained records hold. `fast_ladder_blocks_resumable.py` is the versioned successor of `fast_ladder_blocks.py`: it
imports the same echelon and replaces the driver. A resume of `fast_ladder_blocks.py` itself checks only that
checkpoint files exist, so resumes run through the successor, whose `--checkpoint` writes a manifest binding every
producer and input digest (the generator terms included), every parameter, and the dtype, shape and sha256 of each
saved array, and refuses any difference. The refusal logic is `ladder_checkpoint.py`, tested without torch in
`tests/test_a5_ladder_checkpoint.py`; the end-to-end resume of a tiny cell is
`tests/test_a5_fast_ladder_checkpoint.py`, which needs torch and is skipped under the pinned CI interpreter.
At p = 32029 the source-hashed records `float64-xm-nm-p32029-d7-n29.json` and `-d7-n31.json` give the same
ladder as p = 32009 through degree 7 (15, 51, 122, 240, 417, 665, 996, the last at orders 29 and 31). None of the certified statements rests on a float64 record: h_d comes from the certificate below.

The python-flint ladder and the float64 echelon agree on dim A, dim B and r of the cell both ran (degree 6,
order 26: 4,879, 4,214, 665).

## Monomial structure of the same-sign X slice

Notation: P = k[[a, ρ, σ, w]], R = k[[t]] + (a, ρ, σ) P inside P, I = (G_1, ..., G_15) R, and
M = w² (a, ρ, σ) + w (ρ, σ) (a, ρ, σ)², a monomial ideal of P. The extension of m_R to P is
q = (w², a, ρ, σ) P.

Computed. `monomial_probe.py` reduces spanning sets of the k-vector spaces I and m_R I modulo n^N; every row of
the reduced echelon form has one nonzero entry, so both truncated spaces are spans of monomials of P:

| Incidence | p | N | rank of I | rank of m_R I |
|---|---|---|---|---|
| X− → N− | 32009 | 12 | 973 | 958 |
| X− → N− | 32029 | 12 | 973 | 958 |
| X+ → N+ | 32009 | 12 | 973 | 958 |
| X+ → N+ | 32029 | 12 | 973 | 958 |
| X− → N− | 32009 | 14 | 1,788 | 1,773 |

The model. `monomial_model.py` computes the Hilbert function of the graded algebra
F_q(M) = ⊕_d M^d / q M^d, the fiber cone of the monomial ideal M of P taken with respect to q. It prints
15, 51, 122, 240, 417, 665, 996, 1422, 1955, 2607 for d = 1 to 10. `records/x-same-k2-hilbert-d10.jsonl` holds
HF(k[y]/K2, d) for d = 1 to 10 (X− at both primes, X+ at p = 32029, from `../k2_hilbert.py`): the same ten
numbers.

## Certificate: I = M, and the fiber cone is k[y]/K2 (A5-304)

`monomial_certificate.py` replaces the truncated evidence above by an exact argument over F_p.

1. G_j lies in M. On the parametrization G_j is a polynomial in a, ρ, σ, w and 1/(1 + w); H_j = (1 + w)^8 G_j
   is a polynomial with 5,290 terms over the 15 generators, 1 + w is a unit of P, and every monomial of every H_j
   lies in M.
2. I + q M = M. Since P = R + w R, M is a finite R-module and m_R M = (t, a, ρ, σ) M = q M. The monomials of M
   outside q M are among g and w g for the twelve minimal generators g, and 15 of them remain, a basis of M / q M.
   P acts on M / q M through k[w]/(w²), so the class of G_j is that of (1 − 8 w) H_j; the 15 classes have rank 15.
3. Nakayama's lemma over the local ring R gives I = M. Then I^d = M^d and m_R I^d = q M^d for d ≥ 1, so
   F(I) = k ⊕ ⊕_(d ≥ 1) M^d / q M^d: the subalgebra generated in degree 1 of P[M T] / q P[M T]. The map of the
   previous section is this identification, and it is an isomorphism.
4. The kernel L of k[y_1, ..., y_15] → P[M T] / q P[M T], y_j ↦ class of G_j, is computed in Singular by
   elimination from the toric presentation of the Rees algebra P[M T] (`records/monomial-certificate-*.sing`).
   L has 69 minimal generators, all quadrics, and L = K2 for the retained quadrics (each ideal reduces to zero
   modulo the other).

| Incidence | p | terms of H outside M | rank of the classes | L | time |
|---|---|---|---|---|---|
| X− → N− | 32009 | 0 | 15 | 69 quadrics, equal to K2 | 0.2 s |
| X− → N− | 32029 | 0 | 15 | 69 quadrics, equal to K2 | 0.2 s |
| X+ → N+ | 32029 | 0 | 15 | 69 quadrics, equal to K2 | 0.2 s |
| X+ → N+ | 32009 | 0 | 15 | not run: no retained K2 at this prime | |

Consequences at the three cells with a retained K2 comparison (the first three rows): F(I) = k[y]/K2 in every degree, so h_d = HF(k[y]/K2, d) for all d (15, 51, 122,
240, 417, 665, 996, 1,422, 1,955, 2,607, ...), dimension 4, multiplicity 12, and the ladder values above are
cross-checks of it. The defining ideal is generated by binomials and monomials in the monomial basis of M / q M;
in the coordinates y_j of the header it is K2.

What the certificate rests on, and what it does not cover:

- the identification of the completed local ring of the slice with R, proved in the next section;
- the field: the checks above are over F_32009 and F_32029; the same certificate over Q(i), with the G of the
  Q(i) producer, is `../../a5-char0-transfer/monomial_certificate_qi.py` (A5-305): I = M, L is 69 quadrics that
  reduce to K2 at both primes;
- the fiber cone of a monomial ideal need not be reduced, and this one is not: the nilpotents and the scheme
  structure of Proj F(I) = V_+(K2) are those of K2: saturated, nonreduced along one embedded plane ([arcs-x-same](../arcs-x-same/README.md), A5-303);
- nothing here transfers to another incidence. The E8-bar slice ideal is not a span of monomials in any of the
  five coordinate systems of `e8_monomial_probe.py` at order 7 (`records/e8-monomial-probe-e8-nm-p32009-n7.log`:
  rank 569 with 555 single-monomial rows in the original coordinates and 531 in the four others, rows of support up
  to 5), and no certificate of this kind exists for it.

## The slice ring is R (A5-306)

The certificate uses the completed local ring of the slice V(J) at the base point in the form
R = k[[t]] + (a, ρ, σ) P. Three facts give it.

1. The kernel of the parametrization is J. `records/slice-ring-*.sing` eliminate a, ρ, σ, w and u = 1/(1 + w)
   from the graph of the parametrization: the kernel has 12 generators, dimension 4 and multiplicity 6, and it
   equals the header's J in both directions (J has one component). So k[t_1, ..., t_9]/J is the image ring
   A_0 inside B = k[a, ρ, σ, w]_(1 + w), at both primes and both incidences.
2. B is finite over A_0, with one point over the origin. The coordinates give a, ρ and σ in A_0
   (t4 + t5 = (1 + w) ρ, t6 + t7 = ρ, t6 − t7 = (1 + w) σ, t4 − t5 = σ, and a = t1 ± t9), and
   t = w²/(1 + w) = −2 s t9 lies in A_0 with w² = t (1 + w), which the same Singular run confirms; so
   B = A_0 + w A_0 locally, and modulo the maximal ideal of A_0 the equation w² = t (1 + w) leaves only w = 0.
   The completion of A_0 is therefore its closure in P = k[[a, ρ, σ, w]].
3. That closure is R. It contains k[[t, a, ρ, σ]], w ρ, w σ and t2 = a w (w + 2)/(2 (1 + w)); writing
   (w + 2)/(2 (1 + w)) = α + β w with α a unit and β in k[[t]] gives a w (α + β t) = t2 − a β t, so a w lies in
   it, and with P = k[[t, a, ρ, σ]] ⊕ w k[[t, a, ρ, σ]] it contains (a, ρ, σ) P. Conversely every coordinate
   lies in R and R is closed.

Steps 2 and 3 are arguments, checked by Singular only at the equation w² = t (1 + w); step 1 is computed.

## E8-bar → N− at p = 32009

| d | r_N(d) by order N | HF(k[y]/K2, d) |
|---|---|---|
| 1 | 21 (8, 10) | 21 |
| 2 | 83 (10, 12) | 83 |
| 3 | 225 (14) | 225 |

These equal the certified values of the Gröbner-basis engine (A5-078 to A5-080 on the N+ header, the
same values on N−). The order-14 cell takes 265 s on 28 threads.

### Restrict the target, retain the complete denominator

Let C = k[y_1, ..., y_21], let L define F(I), and put H = sqrt(K2). The
[exact arc certificates](../arcs/README.md) and the retained quadratic membership
receipts give K2 ⊆ L ⊆ H. In each degree the exact sequence

    0 → (H/L)_d → (C/L)_d → (C/H)_d → 0

gives h_d = HF(C/H, d) + rank(phi), where
phi: (H/K2)_d → I^d/m_R I^d sends f to f(G). Its truncated image phi_N in
(P + P b)/(image(m_R I^d) + n^N) therefore gives

    HF(C/H, d) + rank(phi_N) ≤ h_d ≤ HF(C/K2, d).

This bound applies even when the full truncated rank r_N(d) is less than
HF(C/H, d). Only rank(phi_N) is added to that base dimension. The target dimensions
are 952 − 861 = 91 in degree 5 and 1,666 − 1,526 = 140 in degree 6. Degree 5
already has h_5 = 952 at both registered primes (A5-183/A5-220); it is a positive
control for this computation. The N14 target ranks below strengthen the
degree-six lower bound to 1,554 at both registered primes; the jet functionals of
[../arc-jets/](../arc-jets/README.md) close the cell at h_6 = 1,666 on both primes, for the N- and for the N+ header.

`e8_target_rank.py prepare` computes a global `dp` standard basis of K2 and of
P1 ∩ P2, exports the degree-d standard monomials modulo K2 and their normal forms
modulo P1 ∩ P2, and takes the coefficient kernel over F_p with python-flint. It
verifies K2 ⊆ P1 ∩ P2, the two Hilbert dimensions, independence of the target rows,
and their joint annihilation of the normal-form matrix. The targets are linear
combinations of standard monomials, not independent membership questions.

`run` first repeats the exact Singular export and compares the standard monomials
and radical normal forms with the prepared basis. A payload digest and a
self-consistent coefficient kernel alone cannot certify that algebraic map.
It then reuses the unchanged quadratic algebra and propagation of `e8_ladder.py`.
It propagates m_R by **all 21 original G** through degree d, then reduces the
91 or 140 target images against that complete denominator. Restricting the
denominator to those images changes the quotient and can produce a false lower
bound. Reaching target rank 91 or 140 proves equality with the K2 upper bound
in that degree. A zero target image or a plateau in N proves no exact membership
and provides no improved upper bound.

Target evaluation extracts common monomial factors and groups the remaining
terms by a variable's exponent before substituting G. A remaining factor of
y-degree c has order at least c times the minimum order of G, so its coefficient
needs only that much less precision. Each restored factor raises the cutoff
accordingly. This avoids expanding all standard-monomial products independently
and permits cancellations before the larger products form. The full denominator
propagation is unchanged.

After the [compute-flags review](../../../runbooks/compute-flags.md), prepare a
basis and run an order selected for the available memory and time budget:

```sh
E8_TARGET=docs/evidence/a5-exceptional-fibers/monomial-ladder/e8_target_rank.py
"$PYTHON" "$E8_TARGET" prepare --target e8nm-p32009 --degree 5 \
  --singular Singular --timeout 300 --out docs/local/e8nm-p32009-d5-basis.json
"$PYTHON" "$E8_TARGET" run docs/local/e8nm-p32009-d5-basis.json \
  --order 12 --max-matrix-mib 768 --out docs/local/e8nm-p32009-d5-n12.json
```

Use `--degree 6` for the frontier basis; `--target` also admits N+ and the second
registered prime. Each basis binds the field, root of −1, ordered G, K2 relation
bytes, degree-two membership receipt, component ideals, and retained dominant
arc certificates. A sign transport binds the N+ receipt where needed. A run
rejects changed inputs and records its own producer and ring-module digests,
Singular version, and fresh export's source and log digests. `--singular` selects
the binary in both commands; `--verification-timeout` bounds the run's export.
These retained proof premises are checked for identity and success, not replayed
by the target runner. Its output concerns only the selected finite field.

The matrix guard bounds the selected input and RREF arrays using the complete
ambient monomial count. It is a conservative preflight check, not a process RSS
limit; retain the external memory watchdog and wall-time limit. Every completed
denominator stage is printed to stderr, and preparation preserves its Singular
source and log. The bounded synthetic tests in
[`test_a5_e8_target_rank.py`](../../../../tests/test_a5_e8_target_rank.py) test the
quotient semantics, joint kernel, provenance failures and incomplete-run rules
without replaying retained research records.

`replay BASIS [RANK]` re-establishes the basis from the retained ideals; with a
rank record it also reruns the complete closure and compares ranks, bounds,
source identities, field and resource allowance. Only elapsed milliseconds
are excluded from the comparison. The retained record's own payload digest
and producer digest must match before replay. Omitting RANK checks a frontier
basis without launching its larger closure computation.

The retained exact target ranks are:

| Prime | Degree | Ambient order N | Target dimension | Target rank | Certified bound | Receipt |
|---|---|---|---|---|---|---|
| 32009 | 5 | 12 | 91 | 21 | 882 ≤ h_5 ≤ 952 | [rank](target-records/e8nm-p32009-d5-n12.json) |
| 32029 | 5 | 12 | 91 | 21 | 882 ≤ h_5 ≤ 952 | [rank](target-records/e8nm-p32029-d5-n12.json) |
| 32009 | 6 | 14 | 140 | 28 | 1,554 ≤ h_6 ≤ 1,666 | [rank](target-records/e8nm-p32009-d6-n14.json) |
| 32029 | 6 | 14 | 140 | 28 | 1,554 ≤ h_6 ≤ 1,666 | [rank](target-records/e8nm-p32029-d6-n14.json) |
| 32009 | 6 | 15 | 140 | 55 | 1,581 ≤ h_6 ≤ 1,666 | [rank](target-records/e8nm-p32009-d6-n15.json) |

Every row has status `lower_bound_only`. Here N uses weight one on w, ρ, σ,
ζ, a and b in the quadratic model; comparison with an order in the original
slice coordinates requires the explicit substitution. The full denominator
dimensions are 385 in the degree-five rows, 588 at degree six/order 14 and
1,738 at degree six/order 15. The stronger order-15 bound is specific to 32009;
that order has not been run at 32029.
The existing exact h_5 = 952 proves that all 91 degree-five directions survive
in the untruncated quotient. Thus the 70-dimensional kernel of phi_12 is an
actual positive-control example of truncation losing directions; it does not
give exact relations. The 112-dimensional kernel of the degree-six N14 map
and the 85-dimensional kernel at N15 likewise supply no membership certificate.

The bases at both primes are retained beside the rank records:
[32009 degree 5](target-records/e8nm-p32009-d5-basis.json),
[32009 degree 6](target-records/e8nm-p32009-d6-basis.json),
[32029 degree 5](target-records/e8nm-p32029-d5-basis.json), and
[32029 degree 6](target-records/e8nm-p32029-d6-basis.json). Their Singular exports
and verification logs are retained in the same directory. The on-demand gates
`core-a5-e8-target-rank`, `core-a5-e8-target-frontier`,
`core-a5-e8-target-second-prime` and `core-a5-e8-target-n15` bind these bases
and ranks to the producer.
The N+ header has the four matching bases (`e8np-p32009-d5-basis.json`, `e8np-p32009-d6-basis.json`,
`e8np-p32029-d5-basis.json`, `e8np-p32029-d6-basis.json`, each with its Singular export and log), written by
`e8_target_rank.py prepare` and read by the N+ jet-rank records of [../arc-jets/](../arc-jets/README.md); no target
rank is computed on them and no on-demand gate replays their Singular export.
The [validation record](target-records/validation.json) records successful
executions of the first three gates: both degree-five controls, both N14
degree-six ranks and all four bases. The N15 calculation completed under the
frozen producer and passed independent static provenance review; its on-demand
replay gate was not rerun because the original calculation approached the
1 GiB RSS limit. The validation also records 23 passing semantic tests,
Ruff, mypy and the focused ledger check.
The common finite-field bound is ledger A5-251; its transfer to N+ uses the
retained sign isomorphisms, and it makes no characteristic-zero claim.

[Operational costs](target-records/costs.json) retain the completed runs and
resource stops. Both N14 runs use two workers and finish in 51–62 seconds at
about 355 MiB sampled peak process-tree RSS. The N15 run finishes in 211 seconds
at 939 MiB under the 1 GiB RSS watchdog. An earlier one-worker N14 attempt hit
its 180-second wall limit after completing the denominator. These shared-host
observations are not a controlled performance comparison. The one higher-order
attempt stops the present resource study at N15.

The [four-target loader check](target-records/loader-check.json) covers both signs and both primes: the root,
sign, ordered J and G, successful input receipts, all 21 substituted G and vanishing of all 16 J at order 4. Each
case stores the repository-relative path and sha256 of every input that `e8_target_rank.bound_inputs` binds. Its
producer is [e8_loader_check.py](e8_loader_check.py), which repeats the input stage of `e8_target_rank.py run` and
writes the file; `--check` compares a fresh record byte for byte, and gate `core-a5-e8-loader-check` of
`ci/gates.json` runs that comparison on demand. It verifies loader compatibility and leaves the retained
sign-isomorphism proof as the premise for transferring a bound from N− to N+.

### The E8-bar slice ideal is an ideal of the larger ring (A5-309)

Write S = P + P b for the quadratic algebra that contains the slice ring R = R0 + R0 b; S = R + w R is finite
over R. `records/e8-ideal-closure-e8-nm-p32009.sing` works in the polynomial model of S (variables w, ρ, σ, ζ, a,
b and u = 1/(1 + w), modulo u (1 + w) = 1 and b² = F) at p = 32009:

- the header's J vanishes on the parametrization;
- m_R S is primary to the origin, with S / m_R S = k[w]/(w²) (colength 2), so quotients by it are local;
- I S / (m_R S) I S has dimension 21, and the 21 generators G_j span it over k (`e8_closure_rank.py`: the 21 normal
  forms have rank 21). Nakayama's lemma over R gives I = I S: the slice ideal is closed under multiplication by w;
- I S needs 16 generators over S.

Consequence: I^d = (I S)^d and m_R I^d = (m_R S)(I S)^d, so F(I) is the part of degree at least 1 of
S[I T] / (m_R S) S[I T], the Rees algebra of an ideal of a hypersurface ring reduced modulo an ideal of colength 2.
That is a finite presentation: `records/e8-fiber-cone-e8-nm-p32009.sing` computes its kernel L in k[y_1..y_21] by
two eliminations and compares it with K2. That run has not finished. The target ranks above give
1,581 ≤ h_6 ≤ 1,666 at p = 32009 and 1,554 ≤ h_6 ≤ 1,666 at p = 32029; the jet functionals of
[../arc-jets/](../arc-jets/README.md) reach rank 1,666 at both primes on the N- header and on the N+ header (the
`e8np-*` bases of `target-records/` supply the N+ columns), so h_6 = 1,666 there and L has no generator of degree 3
to 6 beyond K2; generators of L above degree 6 remain open. The truncated ranks of I and
I S agree at orders 5 to 9 (114, 276, 569, 1,056, 1,817; `e8_closure_probe.py`,
`records/e8-closure-probe-e8-nm-p32009.jsonl`), consistent with the exact result. The four closure runs (N− and N+ headers, both primes) give the same numbers, and
`records/slice-ring-e8-*.log` show that the kernel of the parametrization equals the header's J (one component)
in all four cases. Not checked for E8-bar: Q(i).
