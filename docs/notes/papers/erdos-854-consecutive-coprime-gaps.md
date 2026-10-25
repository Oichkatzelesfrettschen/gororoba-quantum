# Erdos Problem 854 -- missing even gaps between consecutive integers coprime to a primorial

## Pages and retrieval

Retrieved 2026-10-25T00:07Z from erdosproblems.com, maintained by T. F. Bloom. Each SHA-256 identifies the bytes
served at retrieval; the pages are mutable, and [SOURCES.json](../../SOURCES.json) records the receipts and
their reading scope. No page bytes are retained.

| Page | URL | SHA-256 of retrieved bytes |
|---|---|---|
| Problem 854 | https://www.erdosproblems.com/854 | `d540c46bff536508f0749281302183c4227bec975cf692f36f00a8600c77d940` |
| Discussion thread | https://www.erdosproblems.com/forum/thread/854 | `da865477ee8e922cf2790a05216cc8d3513eb06962f7ea502e6eab7134a9d591` |

The recommended citation printed on the page: T. F. Bloom, Erdos Problem #854, https://www.erdosproblems.com/854.

## Statement and status

Tag convention: [P] marks page statements; [I] marks repository interpretation.

- [P] Problem: let `n_k` be the `k`th primorial and `1 = a_1 < a_2 < ... < a_phi(n_k) = n_k - 1` the integers
  coprime to `n_k`. Estimate the smallest even integer not of the form `a_(i+1) - a_i`. Are there
  `>> max_i (a_(i+1) - a_i)` many even integers of that form?
- [P] Status: the page carries the tag `[Ob1]` and the label "number theory", and the forum comment of 29 Oct 2025
  reads "So that IS why is still marked as open". The page shows no solved or proved marker, lists "Proof
  expositions (0)" and "Proof claims (1)", "Formalised statement? No", and "This page was last edited 04 November
  2025". Status at retrieval: open.
- [P] Origin: asked by Erdos in Oberwolfach, "most likely in 1986". Erdos first thought that for large `k` every
  even `t <= max(a_(i+1) - a_i)` occurs as a gap, wrote in `[Ob1]` "perhaps this is false", and reported
  computations of Lacampagne and Selfridge showing that it fails for `n_k = 2*3*5*7*11*13` (`k = 6`), which "show
  some doubt on [his] conjecture"; he said it could fail for all or infinitely many `k`. He also asked for
  estimates of the number and the least index of the `j` attaining the maximal gap.
- [P] Literature cited by the page: `[Er85c,p.80]` and `[Ob1]` (an Oberwolfach report; a forum comment of
  21 Nov 2025 records that the `[Ob1]` reference did not load, and the site was updated in response);
  OEIS A389839 (the statement of this problem) and A048670 (the related version, with lower bounds; the forum
  comment says A389839 is bounded by A048670 plus two). The page cites no paper by Ziller or any other
  computation beyond Lacampagne and Selfridge.
- [P] Forum remark (Woett, 16 Oct 2025, a different variant): for all differences `a_i - a_j` with not
  necessarily consecutive terms, the smallest missing even integer is `(1 - o(1)) n_k` and conjecturally
  `n_k - (2 + o(1)) p_k`, the upper bound resting on a strengthened Goldbach assumption. A reply (StijnC,
  13 Aug 2025) notes the problem asks about consecutive gaps only, so the variant does not answer it.

## Mapping to this repository

- [I] [Ziller 2020](2007.01808.md) computes, for `k <= 44`, the smallest missing even gap `N_min(k) + 2` and every
  missing gap (Table 1, p. 12), confirming Lacampagne and Selfridge's `k = 6` case (missing gap 20), and states
  Conjecture 4.1 (`h(k - 1) <= N_min(k)`). The Erdos page does not cite it.
- [I] The page asks for an estimate of `N_min` and a count; Ziller's Corollary 2.8 gives the lower bound
  `N_min(k) >= 2k`, and his Table 1 gives data through `k = 44` with no value beyond.

## Boundaries

[I] The two pages were read as served on the retrieval date; the problem's status can change on the site. OEIS
A389839 and A048670 and the `[Er85c]` and `[Ob1]` sources were not retrieved.
