# C5 zero-divisor code replay

The active [exact replay](replay-exact.py) succeeds the hash-bound [original](replay.py).
Its deterministic products and left matrices use the rational `cd_core` APIs;
its noisy decoding retains floating arrays. The active gate requires the complete
output to match the original `result.json` bytes. `SHA256SUMS` preserves the
original replay and result identities.

The replay reconstructs the experiment that
[the C5 note](../../notes/topics/c5-zero-divisor-code-falsification.md) reports, from
the sedenion sign table `gororoba_quantum/cd_core.py` alone, with fixed seeds.
The original implementation was never committed.

## Codebooks

- **table1, the note's code.** The note's messages are "the 84 zero-divisor
  pairs of the sedenion census", message `i` selecting the pair
  `(a_i, b_i)`. These are the 84 standard zero divisors of Reggiani's
  Table 1 ([source note](../../notes/papers/2411.18881.md)):
  `(e_i + e_j, e_k +- e_l)` with `1 <= i <= 6`, `9 <= j <= 15`,
  `i < k <= 7`, `9 <= l <= 15`, every one a row of
  `cd_core.sedenion_zero_divisor_corpus()`. `table1_rows()` selects them and
  sorts them by `(i, j, t, k, l, s)`, which fixes the message index and so
  the lowest-index tie rule. The note recorded no order; the kernel file
  `reggiani_standard_zero_divisor_pairs.csv` of open_gororoba lists the same
  84 rows in this order. The 84 pairs hold 34 distinct annihilators `a_i`
  and 57 distinct blades `b_i`. #314's falsifier names the note's counts
  and C5 rate; identifying the note's code with Table 1 is the replay's
  reading, and the counts it reproduces support it.
- **first_partner and matching, re-paired codebooks.** An earlier revision
  of this replay read the 84 messages as the 84 distinct left factors
  `a = e_i + t e_j` of the corpus, ordered by `(i, j, t)` with `t = -1`
  before `t = +1`, each with exactly 4 partners. `first_partner` sends the
  partner that sorts first by `(k, l, s)`; `matching` sends the mate in the
  first perfect matching of the annihilation graph (depth-first in sorted
  order, `perfect_matching`), giving 84 distinct blades. Neither is the
  note's code; both stay as alternative codebooks, and they draw nothing
  from the generator, so their rows are unchanged by table1.
- **Codeword.** The transmitter sends the signed blade `b_i` scaled to unit
  norm, `x_i = b_i / sqrt(2)`.
- **Noise.** The receiver sees `v = x_i + sigma n` with `n` standard normal in
  16 dimensions. The replay evaluates `b_i + sqrt(2) sigma n`, which is
  `sqrt(2) v`, so every decoder compares the same quantities and the
  noiseless case holds only the coefficients 0 and +-1, which floating
  point multiplies and adds exactly.
- **Sigma grid.** The note names 0.01, 0.05, 0.10, 0.20 and 0.50 and says
  eight levels. The replay adds 0.001, 0.30 and 1.00 as the other three and
  adds sigma = 0 as a ninth, noiseless row.
- **Trials.** All 84 messages x 400 trials per sigma (`messages_simulated`,
  `trials_per_message`). The headline `ser_40` reads a seeded draw of 40
  messages without replacement from the 84, sorted (`subset_messages`);
  `ser_84` reads every trial and is retained as a second figure.
- **Annihilation decoder (C5).** `ihat = argmin_j ||L_{a_j} v||`, where
  `L_a` is the 16 x 16 left-multiplication matrix of `a`
  (`cd_core.left_mult_matrix`), over the codebook's 84 annihilators. An
  exact floating-point tie resolves to the lowest `j`. Since
  `||L_a v||^2 = v^T L_a^T L_a v`, annihilators sharing the Gram matrix
  `L_a^T L_a` score every received vector alike at every sigma, and the
  decoder cannot separate their messages (`score_classes` in each
  codebook's `counts`).
- **Algebraic + matched filter.** `ihat = argmax_j <v, x_j>` over the 84
  codewords `x_j`; identical codewords tie exactly and resolve to the lowest
  `j`.
- **Random + matched filter.** 84 codewords drawn i.i.d. from the 16-D
  standard normal and normalized, matched filter `argmax_j <v, c_j>`, noise
  `sigma n` on a unit-norm codeword.
- **Profile decoder.** The note's rescue decodes by the whole 84-component
  annihilation profile. The replay takes the profile
  `p(v) = (||L_{a_j} v||)_j`, the noiseless template `p(x_i)` per message, and
  `ihat = argmin_i ||p(v) - p(x_i)||`, lowest `i` on ties.
- **Symbol error rate.** The fraction of trials whose decoded label differs
  from the sent label.
- **Tie.** For message `i`, the number of `j` among the 84 with
  `a_j * b_i = 0` exactly (`cd_core.cd_multiply` on coefficients 0 and +-1,
  exact in floating point),
  the sender included. `mean_ties` is the mean over the 84 messages and
  `mean_ties_excluding_sender` the same less one, the reading that matches
  the note's "3.9 per codeword".
- **Signature.** The set `{j : a_j * b_i = 0}` of message `i`; the count is
  the number of distinct sets over the 84 messages.
- **Distinct blade.** The number of distinct `b_i` over the 84 messages.
- **Seed.** `numpy.random.default_rng(314)`. Draw order: the 40-message
  subset, the random codebook, then one noise block per sigma in grid order,
  each shaped (84 messages, 400 trials, 16); the 40-message figures read the
  subset rows of that block. Every block is drawn before any decoding, and
  `parallel.ordered_map` decodes the sigma rows in grid order, so the result
  does not depend on the worker count.

## Result

Counts under the definitions above (`result.json`, `counts`):

| quantity | note | table1 | first_partner | matching |
|---|---|---|---|---|
| mean annihilator ties, sender excluded | 3.9 | 3.94 | 3.0 | 3.0 |
| distinct annihilator-set signatures | 35 | 35 | 28 | 42 |
| distinct transmitted blades | 57 | 57 | 28 | 84 |
| distinct annihilators (Gram classes) | -- | 34 (34) | 84 (42) | 84 (42) |

table1 reproduces all three of the note's counts. Its 84 messages share 34
annihilators, each its own Gram class. In exact arithmetic the messages
that share an annihilator score every received vector alike, so the
annihilation decoder can return at most 34 distinct messages and errs on
at least 50 of 84 (1 - 34/84 = 0.595) at every sigma; the retained run's
duplicate scores are bitwise equal. The blade a table1 message sends is
annihilated by 1 (17 messages) or 2 (67 messages) of the 34 distinct annihilators, 2 to 7 of
the 84 rows (`distinct_annihilators_per_message_histogram`, over message
rows; over the 57 distinct blades, 17 and 40). In the re-paired
codebooks every blade has exactly 4 annihilators and the 84 left factors
fall into 42 Gram pairs.

table1 symbol error rates, over the 40-message subset (`ser_40`) and all 84
messages (`ser_84`). MF is the matched filter over the codebook's own
codewords, profile the 84-component annihilation-profile decoder:

| sigma | random MF | C5 (40) | MF (40) | profile (40) | C5 (84) | MF (84) | profile (84) |
|---|---|---|---|---|---|---|---|
| 0 | 0.000 | 0.800 | 0.375 | 0.625 | 0.798 | 0.321 | 0.583 |
| 0.001 | 0.000 | 0.750 | 0.375 | 0.625 | 0.745 | 0.321 | 0.583 |
| 0.01 | 0.000 | 0.749 | 0.375 | 0.625 | 0.743 | 0.321 | 0.583 |
| 0.05 | 0.000 | 0.750 | 0.375 | 0.625 | 0.745 | 0.321 | 0.583 |
| 0.1 | 0.000 | 0.752 | 0.375 | 0.626 | 0.744 | 0.321 | 0.585 |
| 0.2 | 0.042 | 0.787 | 0.410 | 0.806 | 0.788 | 0.361 | 0.775 |
| 0.3 | 0.296 | 0.879 | 0.578 | 0.936 | 0.877 | 0.543 | 0.913 |
| 0.5 | 0.705 | 0.950 | 0.811 | 0.979 | 0.950 | 0.795 | 0.968 |
| 1 | 0.923 | 0.979 | 0.940 | 0.991 | 0.979 | 0.934 | 0.984 |

The matched filter's floor is the blade collisions: 27 of the 84 messages
send a blade a lower-index message also sends, 1 - 57/84 = 0.321 over all
84. The replay's subset holds 15 of them (0.375); the note's 0.275 is a
draw holding 11. The profile decoder errs on 49 of 84 messages at sigma 0
(0.583); the replay's subset holds 25 (0.625) and the note's 0.575 a draw
holding 23. Both figures depend on the unrecorded 40-message draw, and the
note's values lie within what table1 allows. The re-paired codebooks
cannot give the matched-filter figure: first_partner's 28 blades leave at
least 12 colliding messages in any 40 (0.300), and matching's matched
filter errs on none.

`ser_40_draw_sd` is the spread of `ser_40` over 40-message draws without
replacement from the retained trials, the finite-population standard
deviation of the mean of the per-message rates; table1's C5 reads 0.039 at
sigma 0.01.

The re-paired codebooks (`first_partner`, `matching` rows) show the same
decoder failure with distinct annihilators: under matching the matched
filter decodes all 84 blades without error at low noise while C5 errs at
0.751 over all 84 at sigma 0.01.

## Replay

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error docs/evidence/c5_zero_divisor_code/replay-exact.py --check
(cd docs/evidence/c5_zero_divisor_code && sha256sum -c SHA256SUMS)
```

`result.json` retains the Python and numpy major.minor releases as its
runtime identity, so a patch release of either replays under `--check`; a
changed source, seed or major.minor runtime needs an explicit reviewed
regeneration.
