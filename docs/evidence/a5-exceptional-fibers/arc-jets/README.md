# Jets of formal arcs: E8-bar fiber-cone ranks through degree seven

The exact arc-jet ranks of the exceptional fiber from the E8-bar stratum of the 32-dimensional Cayley-Dickson
zero-divisor variety to the two signed boundary headers N- and N+ reach the quadratic-ideal upper bound in
degrees one to seven at 32009 and degrees five to seven at 32029. [jet_rank.py](jet_rank.py) retains degrees one
to six; its versioned successor
[jet_rank_v2.py](jet_rank_v2.py) adds degree seven. Both headers reach rank 2,718 from 3,000 arcs at each of the
primes 32009 and 32029, with every arc passing the slice-ideal and quadratic-relation checks. With K2 inside L,
this gives h_7 = HF(k[y]/K2, 7) = 2,718 and L_7 = (K2)_7. All 204 degree-seven classes of sqrt(K2)/K2 survive in
the fiber cone F(I) = k[y]/L. Together with the retained lower degrees, the defining ideal has no additional
homogeneous generator in degrees three to seven beyond the 148 quadrics.

Each header carries its own arcs, quadratic relation file and column bases. The N+ ranks are measured directly
on N+; the N+ upper bound at 32009 uses the retained sign transport of the N- degree-two membership receipt
(described below). Every equality holds over its named prime field. Characteristic zero and degrees eight and
above remain open.

## Method

Notation as in [../arcs/README.md](../arcs/README.md): R is the local ring of the slice V(J) at the origin, m_R its
maximal ideal, I = (G_1, ..., G_21) R and L the kernel of k[y_1, ..., y_21] -> sum_d I^d / m_R I^d. An arc
gamma: R -> k[[s]] through the origin has

    v = min_j val G_j(t(s)),  e = min_i val t_i(s),  G_j(t(s)) = s^v c_j(s).

Valuations multiply in k[[s]], so gamma(I^d) lies in (s^(d v)) and gamma(m_R I^d) = gamma(m_R) gamma(I^d) in
(s^(e + d v)). A form f in L_d has f(G) in m_R I^d, so f(c(s)) lies in (s^e): the coefficients of s^0, ..., s^(e - 1)
of f(c(s)) are linear functionals on k[y]_d that vanish on L_d. The rank of any set of them, on any set of columns,
is at most dim k[y]_d / L_d = h_d. The coefficient of s^0 is the limit-point test of ../arcs, which sees only
sqrt(L); the coefficient of s^1 sees the nilpotent directions. Every arc here has e = 2.

The lower bound needs only that the arc lies on V(J). Equality with HF(k[y]/K2, d) uses K2 inside L, the degree-two
receipts that ledger row A5-251 already rests on (`../witnesses.jsonl`, `k2-span` rows). For N- the rows of
`working/distribute/out/a5-e8-d2/e8nm_p1` (p = 32009) and `e8nm_p2` (p = 32029) each certify the 148 relations of
the K2 file the run uses (`membership_check` 148 checked, 0 failures, relation file digest equal to the K2 file's).
For N+ at p = 32029 the row of `e8np_p2` does the same for the N+ header (input `p32029-r9115/e8-np.sing`, relation
file `3c2294f7...`, the K2 file of the N+ run, 148 checked, 0 failures). The repository holds no degree-two receipt
of the N+ header at p = 32009: its K2 file `working/runs/e8_a2/e8_k2.rel` (`bbe9bb73...`) is the image of the N-
K2 file under the sign isomorphism t8, t9 -> -t8, -t9 (the `sign-isomorphism` row at 32009: every J and G generator
of the two headers agrees up to sign and the two K2 files have zero mutual remainders after the y signs), so K2
inside L for N+ at 32009 is the N- receipt carried by that isomorphism (A5-013), as in A5-079 and A5-082. At 32009
the N+ upper bound HF(k[y]/K2, d) therefore rests on that transport; the N+ jet ranks themselves, the lower bound,
are computed on the N+ header at both primes.

The arcs are Phi(w, rho, sigma, e_par, zeta) of ../arcs with polynomial parameters of four terms each. Six families
repeat in the order of `FAMILIES`: the valuations (2, 2, 2, 2) with e_par(0) away from 0 and +-1 (limits on the scroll
V(P2)); (4, 2, 2, 2) with e_par = -1 + s^4 (...) (limits on V(P1)), twice; and (1, 2, 2, 2) with e_par = -1 + s^k
(...), k = 1, 2, 1, whose limits lie on the quadric threefold of [A5-312](../quadric-census/README.md) that carries the
nilpotents of K2 and whose first jets have nonzero nilpotent coordinates y4, y6, y7, y12, y14. Each coefficient is
the fixed integer `int.from_bytes(sha256("idx:var:j")[:8], "big") mod p` (0 replaced by 1); every value is written
into the record, and no generator state or seed is involved. Each arc is checked against all 16 generators of J and
all 148 quadrics of K2 modulo s^e at working precision 70; no arc fails either check.

The coefficient rule decides only whether the rank reaches its bound, never whether the bound holds: every row is
an exact functional on k[y]_d / L_d whatever the arc. It is a reproducibility choice, taken instead of a quantum
random draw because the run needs thousands of generic points that `--check` regenerates byte for byte. Two simpler
rules failed by rank on the same code: coefficients periodic modulo 97 in the arc index repeat arcs and cap the
limit-point rank of each family at 97 (degree 5 plateaus at 613 and 516 with the earlier and the reweighted family
lists), and a rule exponential in the index alone puts all parameter points on one line. With the SHA-256 rule the
reweighted list reaches rank 722 at 600 arcs in degree 5 where the periodic rule had stopped at 516, and 952 at
1,000 arcs.

Columns are all monomials of degree d for d <= 4, and for d = 5, 6 and 7 the standard monomials of K2 from the retained
bases [../monomial-ladder/target-records/](../monomial-ladder/README.md) (sha256 in each record; the degree-five and degree-six `e8np-*` bases
come from `e8_target_rank.py prepare` on the N+ header and its K2 file). Degree-seven bases come from
[the basis successor](../monomial-ladder/e8_target_basis_v2.py), which computes the radical dimension as the exact
rank of the radical normal forms; four fresh Singular exports and their replays each give 2,718 standard
monomials, radical dimension 2,514 and nilpotent dimension 204. The functionals
vanish on K2_d, so their rank on a basis of k[y]_d / K2_d equals their rank on all of k[y]_d. A run adds arcs in
steps, takes the rank over F_p with python-flint `nmod_mat`, rewrites the record after every step and stops at the
first step whose rank reaches HF(k[y]/K2, d).

## Result

| Target | d | arcs | rows | rank | HF(sqrt(K2), d) | HF(K2, d) | statement | record |
|---|---|---|---|---|---|---|---|---|
| E8-bar -> N-, p = 32009 | 1 | 20 | 40 | 21 | 16 | 21 | h_1 = 21 | [d1](records/e8nm-p32009-d1.json) |
| E8-bar -> N-, p = 32009 | 2 | 100 | 200 | 83 | 69 | 83 | h_2 = 83 | [d2](records/e8nm-p32009-d2.json) |
| E8-bar -> N-, p = 32009 | 3 | 200 | 400 | 225 | 195 | 225 | h_3 = 225 | [d3](records/e8nm-p32009-d3.json) |
| E8-bar -> N-, p = 32009 | 4 | 500 | 1,000 | 495 | 440 | 495 | h_4 = 495 | [d4](records/e8nm-p32009-d4.json) |
| E8-bar -> N-, p = 32009 | 5 | 1,000 | 2,000 | 952 | 861 | 952 | h_5 = 952 | [d5](records/e8nm-p32009-d5.json) |
| E8-bar -> N-, p = 32009 | 6 | 1,800 | 3,600 | 1,666 | 1,526 | 1,666 | h_6 = 1,666 | [d6](records/e8nm-p32009-d6.json) |
| E8-bar -> N-, p = 32029 | 5 | 1,000 | 2,000 | 952 | 861 | 952 | h_5 = 952 | [d5](records/e8nm-p32029-d5.json) |
| E8-bar -> N-, p = 32029 | 6 | 1,800 | 3,600 | 1,666 | 1,526 | 1,666 | h_6 = 1,666 | [d6](records/e8nm-p32029-d6.json) |
| E8-bar -> N+, p = 32009 | 1 | 20 | 40 | 21 | 16 | 21 | h_1 = 21 | [d1](records/e8np-p32009-d1.json) |
| E8-bar -> N+, p = 32009 | 2 | 100 | 200 | 83 | 69 | 83 | h_2 = 83 | [d2](records/e8np-p32009-d2.json) |
| E8-bar -> N+, p = 32009 | 3 | 200 | 400 | 225 | 195 | 225 | h_3 = 225 | [d3](records/e8np-p32009-d3.json) |
| E8-bar -> N+, p = 32009 | 4 | 500 | 1,000 | 495 | 440 | 495 | h_4 = 495 | [d4](records/e8np-p32009-d4.json) |
| E8-bar -> N+, p = 32009 | 5 | 1,000 | 2,000 | 952 | 861 | 952 | h_5 = 952 | [d5](records/e8np-p32009-d5.json) |
| E8-bar -> N+, p = 32009 | 6 | 1,800 | 3,600 | 1,666 | 1,526 | 1,666 | h_6 = 1,666 | [d6](records/e8np-p32009-d6.json) |
| E8-bar -> N+, p = 32029 | 5 | 1,000 | 2,000 | 952 | 861 | 952 | h_5 = 952 | [d5](records/e8np-p32029-d5.json) |
| E8-bar -> N+, p = 32029 | 6 | 1,800 | 3,600 | 1,666 | 1,526 | 1,666 | h_6 = 1,666 | [d6](records/e8np-p32029-d6.json) |
| E8-bar -> N-, p = 32009 | 7 | 3,000 | 6,000 | 2,718 | 2,514 | 2,718 | h_7 = 2,718 | [d7](records/e8nm-p32009-d7.json) |
| E8-bar -> N-, p = 32029 | 7 | 3,000 | 6,000 | 2,718 | 2,514 | 2,718 | h_7 = 2,718 | [d7](records/e8nm-p32029-d7.json) |
| E8-bar -> N+, p = 32009 | 7 | 3,000 | 6,000 | 2,718 | 2,514 | 2,718 | h_7 = 2,718 | [d7](records/e8np-p32009-d7.json) |
| E8-bar -> N+, p = 32029 | 7 | 3,000 | 6,000 | 2,718 | 2,514 | 2,718 | h_7 = 2,718 | [d7](records/e8np-p32029-d7.json) |

For degrees one to six, the radical column is the fixed table `RADICAL_HF`; degree seven reads the measured
radical-normal-form rank 2,514 from its basis. Every record carries the value as `hf_radical`. The sign isomorphism
carries sqrt(K2) of N- onto sqrt(K2) of N+, so the table holds for both headers. The N+ records use the same
SHA-256 coefficient rule as the N- records, so their arc parameters, step counts and checkpoint ranks coincide
with the N- records, and the statement column of an N+ row at p = 32009 rests on K2 inside L by transport (above).

Degrees 1 to 5 reproduce the certified values (h_1 to h_5 = 21, 83, 225, 495, 952; ledger A5-078 to A5-080, A5-082
and A5-088 on the N+ header, with the same values on N-, the [n15-laptop](../n15-laptop/) record for h_4, A5-183,
A5-220) by a computation that shares no code with the truncated-rank engines, and each exceeds the radical value
that the limit points alone reach. Degree 6 replaces 1,581 <= h_6 <= 1,666 at 32009 and 1,554 <= h_6 <= 1,666 at
32029 (A5-251, N- and its transport to N+) by h_6 = 1,666 on both headers. Each statement holds over the named prime
field and says nothing about characteristic 0.

Costs on the workstation, four workers, one cell at a time inside a cgroup scope (wall time; largest resident set of
one process from `time -v`, measured once per cell). N-, 16 GB scope: degree 1 to 4 at 32009 4 s, 16 s, 31 s and
80 s (at most 0.42 GB); degree 5 167 s and degree 6 318 to 320 s at each prime (0.14 GB and 0.35 GB per process, at
most about 1.4 GB over four workers); the `--check` replay of the 32029 degree-6 record takes 251 s. N+, 8 GB scope
with no swap (`MemoryMax=8G`, `MemorySwapMax=0`): degree 1 to 4 at 32009 3 s, 15 s, 33 s and 81 s (largest resident
set 0.04, 0.04, 0.07 and 0.42 GB); degree 5 164 s at 32009 and 210 s at 32029 (0.14 GB per process); degree 6 358 s
at 32009 and 470 s at 32029 (0.35 GB per process, 346,536 and 346,424 kB, so at most about 1.4 GB over four workers).
The N+ run shared the workstation with other sessions' jobs (load average above 12 at the end of the run); both
headers run the same arithmetic up to the sign of t9, so the longer N+ degree-6 wall times are a load effect
(hypothesis, not separated by a measurement). The `--check` replays of the two N+ degree-6 records, run the same way with four workers, reproduced both records
identically (417 s at 32009 and 477 s at 32029, 0.35 GB per process, load average above 12). [resource-use.tsv](resource-use.tsv)
receipts every write and every degree-6 `--check` run: workers, `MemoryMax` of the scope, wall and CPU seconds
and maximum resident set of one process from `time -v`. The raw `time -v` reports name the interpreter by its
absolute path, so they stay in local scratch and the table carries their numbers. The `workers_basis` column is
`GOROROBA_WORKERS=4` where the launching script or shell exported it and `stated` where the four workers are the
launch setting this section reports and no retained script shows it; the CPU to wall ratio of those rows is 3.4 to 3.7,
which four busy workers give. The degree-5 `--check` replay of the N- record at 32009 reproduced it identically
(251 s, 0.14 GB per process); the degree-6 N- and N+ replays are in the same table.

The arc count needed grows with h_d: the rows at the stopping step are 1.78 to 2.41 per unit of rank in the N-
records (about two). The wall time per arc is 155 to 189 ms in the N- records, nearly constant from degree 1 to degree 6 at four workers,
and 148 to 261 ms in the N+ records (`elapsed_ms` divided by the arcs of each record), whose spread sits in the
degree-6 cells run under the host load noted above (hypothesis). That is an observation over these sixteen v1 records
and no law of the arc count: `compute` re-ranks the whole accumulated
matrix after every step, so the rank part of the time grows faster than linearly in the arcs, and no record
separates the arc generation from the rank computation.

## Degree-seven controls and costs

The digest-bound [basis producer](../monomial-ladder/e8_target_basis_v2.py) and its predecessor retain their bytes.
The producer's `replay` subcommand is a historical interface; current basis admission uses
[e8_target_basis_verify.py](../monomial-ladder/e8_target_basis_verify.py). The verifier checks the complete payload,
registered field and coordinates, both producer digests and every bound data source before replaying the exact
Singular export. The separate admission boundary preserves the basis-file identities that the arc records bind.

The successor preserves the coefficient enumeration, arc parametrization, functionals and finite-field rank of
`jet_rank.py`. Its `--control` replay reproduces the retained N- degree-six record at 32009 across 25 fields,
including every arc and checkpoint: 1,800 arcs and rank 1,666. The four degree-seven records share all arc entries
and checkpoint ranks between the two signs at the same prime, as the sign isomorphism predicts.

Each degree-seven cell stops at the first 100-arc checkpoint that reaches 2,718. The 6,000-arc budget and the
five-consecutive-zero-gain stall criterion remain unreached. A stalled record reports a lower bound, never a
proof of an additional relation. The 200-arc calibration measures rank 400 in 26.08 s, with 92,944 kB maximum
resident set. Its measured rate, a fourfold rank-growth allowance and 300 s of margin set a 3,430-second
per-cell deadline. The exact launch review is in [the run rulebook](../../../runbooks/run-rulebook.md#e8-bar-degree-seven-fiber-cone-ranks-from-arc-jets).

Four workers run each cell inside a 12 GiB resident-memory cgroup with swap disabled. Cells run serially on the
shared build host. Python 3.14.7, python-flint 0.9.0 and Singular 4.4.1 serve the ranks and basis exports.
The table reports the largest resident set of one process from GNU `time -v`, not the cgroup peak or the sum of
all workers:

| Header and prime | wall seconds | CPU seconds | maximum RSS kB | arcs | rank |
|---|---|---|---|---|---|
| N-, 32009 | 466.11 | 1451.40 | 887,368 | 3,000 | 2,718 |
| N-, 32029 | 476.71 | 1502.60 | 887,980 | 3,000 | 2,718 |
| N+, 32009 | 516.29 | 1623.77 | 887,564 | 3,000 | 2,718 |
| N+, 32029 | 502.16 | 1588.34 | 887,096 | 3,000 | 2,718 |

Every cell exits zero with all J and K2 checks passing. [resource-use.tsv](resource-use.tsv) retains the
sanitized receipts for the eight basis export/replay runs, the degree-six control, calibration and four writes.
The complete degree-seven `--check` replays are on-demand checks; the bounded tests exercise the successor's
stopping rules, failed premises, record mutations and v1 control comparison without replaying a retained matrix.

## Replay

```sh
PYTHON=${PYTHON:-python3}
"$PYTHON" docs/evidence/a5-exceptional-fibers/arc-jets/jet_rank.py --target e8nm-p32009 --degree 6 \
  --arcs 3000 --step 100 --write docs/evidence/a5-exceptional-fibers/arc-jets/records/e8nm-p32009-d6.json
"$PYTHON" docs/evidence/a5-exceptional-fibers/arc-jets/jet_rank.py \
  --check docs/evidence/a5-exceptional-fibers/arc-jets/records/e8nm-p32009-d6.json
```

`--check` recomputes a record from its own target, degree, arc count and step and compares every field except
`elapsed_ms`, the digests of the producer, the arc library, the header, the K2 relation file, `k2-hilbert.jsonl` and
the column basis included. Start Python with `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096`.

For degree seven, the versioned successor reuses the same exact arithmetic:

```sh
"$PYTHON" docs/evidence/a5-exceptional-fibers/monomial-ladder/e8_target_basis_verify.py \
  docs/evidence/a5-exceptional-fibers/monomial-ladder/target-records/e8nm-p32009-d7-basis.json
"$PYTHON" docs/evidence/a5-exceptional-fibers/arc-jets/jet_rank_v2.py --target e8nm-p32009 --degree 7 \
  --arcs 6000 --step 100 --stall-steps 5 \
  --write docs/evidence/a5-exceptional-fibers/arc-jets/records/e8nm-p32009-d7.json
"$PYTHON" docs/evidence/a5-exceptional-fibers/arc-jets/jet_rank_v2.py \
  --check docs/evidence/a5-exceptional-fibers/arc-jets/records/e8nm-p32009-d7.json
```

The v2 record binds both rank producers and its own degree-seven basis. Its check compares every field except
the elapsed time. The retained v1 producers and records keep their bytes.
The optional-Singular basis gate skips unless `GOROROBA_SINGULAR_REQUIRED=1`; an opted-in verifier failure fails
the gate. The direct verifier command above always requests the exact export replay.

## Falsifiers and what remains

- A rank above HF(k[y]/K2, d), or an arc whose jet violates a quadric of K2 modulo s^2, refutes K2 inside L or the
  code; neither occurs.
- An error in the valuation argument, for instance an arc with gamma(m_R) not inside (s^e); `jet_rows` takes e as
  the minimum valuation of the nine coordinates t_i, which generate m_R.
- The equalities through degree seven rest on K2 inside L at each prime. The jets bound h_d from below only and cannot prove
  h_d < HF(k[y]/K2, d); a plateau below the K2 value would have been a lower bound alone.
- Open: generators of L in degree eight and above, characteristic zero, and a direct degree-two membership
  receipt of the N+ header at p = 32009 (the upper bound there rests on the N- receipt and the sign isomorphism).

## Routes that did not close degree 6

The truncated rank r_N(6) of [../monomial-ladder/](../monomial-ladder/README.md) is exact once n^N meets I^6 inside
m_R I^6, and no certificate of that order exists. Two shortcuts were tested and fail. The truncated ideal is not a
graded subspace in the original, x, xs or xy coordinates of `e8_monomial_probe.py`: at order 8 its rank is 1,056
while the ranks of its homogeneous projections sum to 1,066 (original) and 1,094 (the other three), so no weight
grading turns truncation into an exact statement. The ideal is not primary to the maximal ideal of S, so Nakayama
cannot convert a stable truncation into m_S^c inside I: the closure-probe ranks
(`../monomial-ladder/records/e8-closure-probe-e8-nm-p32009.jsonl`, 114, 276, 569, 1,056, 1,817 at orders 5 to 9)
leave dim S/(I + m_S^N) = 68, 102, 145, 198, 262, whose second differences 9, 10, 11 grow, so S/I has dimension 3
(evidence from truncations, not a proof). The target-rank denominator of `e8_target_rank.py` grows from 588 at order
14 to 1,738 at order 15 in degree 6 (`../monomial-ladder/target-records/`), and the target rank from 28 to 55 of 140.
