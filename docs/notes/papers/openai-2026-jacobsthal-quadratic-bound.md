# OpenAI 2026 -- A quadratic bound for Jacobsthal's function (openai/math family 021)

## Source copy and license

The [commit-pinned PDF](https://raw.githubusercontent.com/openai/math/7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a/preprints/A-quadratic-bound-for-Jacobsthals-function-September-25-2026/paper.pdf)
sits in the openai/math repository, whose root `LICENSE` is the Apache License 2.0 (sha256
`c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4` at the pinned commit). That file is a
repository-wide software license; the manuscript carries no source-specific CC BY 4.0 or CC0 grant, which the
`source_rights_policy` of [SOURCES.json](../../SOURCES.json) requires for a published copy. The PDF therefore stays
external: its optional personal reading copy is `docs/local_source_cache/openai-math-021-jacobsthal-quadratic-bound.pdf`,
and the registry records the SHA-256 of the bytes read and the reading scope.

Tag convention: [P] marks paper statements; [I] marks repository interpretation. Printed page numbers equal the
PDF page indices.

## Citation and provenance

- Author: "OpenAI" (no individual author). The openai/math README states that an unreleased internal OpenAI model
  produced the manuscripts, calls them "raw research data, rather than polished academic papers", and says some
  unformalized results "could have issues". The collection is unrefereed; its `history.md` records three
  withdrawals and fourteen revisions on 7 October 2026.
- Version read: the manuscript dated 25 September 2026 (PDF creation date 6 October 2026), as held at openai/math
  commit `7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a` (26 October 2026). A Crossref bibliographic search by title on
  27 October 2026 returned no record, so no journal version is established.
- Commit-pinned PDF, 83 pages, 824,106 bytes.
- SHA-256: `f80267eebc82a9b8905057b45b35ef8734485b2b0b7b809a3051c06240cf0b1e`
- Reading scope: pp. 1-6 (contents, introduction, conventions, Lemma 2.1) and pp. 73-74 (deduction of Theorem 1.1
  from Theorem 1.2) in full; the reference list for entries [2], [3], [5], [11], [14], [15], [17], [25], [29].
  Sections 2.1-10 and the appendices were read for section titles and result labels only; no proof step there was
  checked.

## Transcribed statements

- [P] Definitions (p. 2): `j(n)` is the least positive `m` such that every interval of `m` consecutive integers
  contains an integer coprime to `n`; `omega(n)` counts distinct prime divisors; `h(k) = sup j(n)` over `n` with
  `omega(n) <= k`. `h(k) - 1` is the greatest length of an interval covered by the divisibility classes of at most
  `k` primes. Erdos's `C(k) + 1` equals `h(k)`.
- [P] Theorem 1.1 (p. 2): an absolute constant `C > 0` gives `h(k) <= C k^2 / (log log(3k))^2` for every `k >= 1`.
- [P] History (p. 3): Iwaniec's linear-sieve error term gave order `k^2 log^2 k` for the primorial case; Vaughan
  proved `j(n) << omega(n)^2 (log(2 omega(n)))^4`; Iwaniec's shifted sieve removed two logarithms and gave
  `h(k) << k^2 log^2 k` for arbitrary prime sets. Hajdu and Saradha proved
  `j(P_k) = h(k)` for `k <= 23` and found `j(P_24) = 234 < 236 = h(24)`, so the primorial extremality question is
  separate from the quadratic bound. Ziller computed the maximum over arbitrary prime sets through 43 prime factors
  (reference [29], arXiv:1903.11973v2, Section 3). The lower bound of Ford, Green, Konyagin, Maynard and Tao,
  `j(P_k) >> k (log k)^2 log log log k / log log k`, remains far below Theorem 1.1.
- [P] Explicitness (p. 3): "the constant in Theorem 1.1 is not made explicit". Conventions (p. 5): the constants
  "need not be effective".
- [P] Covering form (p. 4): one prescribed residue class `a_p` per prime and the Chinese remainder theorem turn
  avoidance of all classes into coprimality with the product of the primes, so arbitrary classes and arbitrary
  translations occur together.
- [P] Theorem 1.2 (p. 4): with `L = log z`, `Y = floor(z^2 / L^2)`, `w = L / (log L)^2`, `B = L / log w` and
  `V_0 = prod_{p <= w} (1 - 1/p)`, absolute `c > 0` and `z_0` give, for every `z >= z_0` and every choice of classes
  `a_p mod p` for `p <= z`, at least `c Y V_0 / B^2` integers in `[1, Y]` that avoid every class.
- [P] Deduction (pp. 73-74): apply Theorem 1.2 at `z = A_0 k log k / log log k`; each divisor prime `q > z` removes
  at most `C_1 (1 + X / log X)` survivors with `X = Y / z`, and `A_0 > 2 C_1 / c_0` leaves a survivor for all large
  `k`; inclusion-exclusion handles the bounded range of `k`.

## Formal statement

The openai/math Lean catalogue ([`lean/docs/021.md`](https://raw.githubusercontent.com/openai/math/7ef5c0cc5ca4b0e072b7a050fca09ab24bc6fa3a/lean/docs/021.md))
names two Comparator challenges, both in the namespace `OAI.Erdos970`:

- [P] `ComparatorChallenges/Jacobsthal.lean` states `JacobsthalQuadratic`: there is `C > 0` such that for every
  `k > 0` some `m <= C k^2` satisfies `IsJacobsthalBound k m`, where `IsJacobsthalBound k m` says every `n > 0` with
  at most `k` prime factors has, for every integer `a`, some `i < m` with `a + i` coprime to `n`. Its
  `Jacobsthal.json` names the solution module `OAI.NumberTheory.Jacobsthal.Main`, the theorem
  `OAI.Erdos970.Erdos970Final.erdos_970_quadratic` and the permitted axioms `propext`, `Quot.sound` and
  `Classical.choice`.
- [P] `ComparatorChallenges/JacobsthalImproved.lean` states `JacobsthalIteratedLog`, the bound of Theorem 1.1 with
  the `(log log(3k))^2` divisor, as `erdos_970_iterated_log`.
- [I] The `sorry` in each challenge file is the challenge form; the Comparator checks a separate solution module
  against it. The Lean build and the Comparator run were not run here.

## Mapping to this repository

- [I] Notation. This paper's `h(k)` is the maximum over every modulus with at most `k` prime factors. Ziller's
  `h(k)` in [2007.01808.md](2007.01808.md) is the primorial value `j(P_k)`, which is also the largest element of his
  difference set `D(k)`. So `Ziller h(k) = j(P_k) <= h(k)` here, with equality for `k <= 23` by Hajdu and Saradha.
- [I] Problem. The Lean namespace places the bound under Erdos Problem 970, the size of the largest gap. The
  [primorial cover defects](../topics/primorial-cover-defects.md) concern Erdos Problem 854, the even gaps that never
  occur below that maximum ([erdos-854-consecutive-coprime-gaps.md](erdos-854-consecutive-coprime-gaps.md)). Both
  rest on the same covering of an interval by one residue class per prime.
- [I] Numbers. Theorem 1.1 has no explicit constant, so it bounds no instance at `k = 6, 8, 14`; Ziller's Table 1
  already gives exact `h(k)` through `k = 44`. The theorem fixes only the growth scale of the range in which
  missing gaps can sit.
- [I] Certified instances. The defect certificates of `gororoba_quantum/primorial_cover.py` depend on none of this
  paper's statements.

## Relevance

- [I] Calibration-aware compilation on IBM hardware: none.
- [I] Cayley-Dickson structure: none.
- [I] Factoring resource estimates: none.

## Boundaries

[I] No proof in Sections 2-11 or the appendices was checked, and the manuscript is unrefereed. Reference [29]
(Ziller, arXiv:1903.11973v2) is a different paper from the registered Ziller 2020 source (arXiv 2007.01808) and is
not registered here.
