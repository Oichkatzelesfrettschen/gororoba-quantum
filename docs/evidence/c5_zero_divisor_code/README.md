# C5 zero-divisor code replay

The replay reconstructs the experiment that
[the C5 note](../../notes/c5-zero-divisor-code-falsification.md) reports, from
the sedenion sign table `gororoba_quantum/cd_core.py` alone, with fixed seeds.
The original implementation was never committed. The definitions below were
fixed before any count or error rate was computed; where the note leaves a
choice open, the most literal reading is taken and is not revised after the
results are known.

## Definitions fixed before computing

- **The 84-pair set.** `cd_core.sedenion_zero_divisor_corpus()` lists the 336
  ordered signed pairs `(e_i + t e_j)(e_k + s e_l) = 0` with disjoint index
  sets. The left factors are 84 distinct signed two-support vectors
  `a = e_i + t e_j` (42 index pairs x 2 signs), each with exactly 4 partners.
  The product vanishes in both orders, so the 84 vectors are the vertices of
  a 4-regular graph with 168 edges. The code has 84 messages, one per left
  factor `a_i`, ordered by `(i, j, t)` with `t = -1` before `t = +1`.
- **Pair and codeword.** Message `i` selects `(a_i, b_i)` where `b_i` is the
  partner of `a_i` that sorts first by `(k, l, s)` in the corpus, again with
  `s = -1` before `s = +1`. The transmitter sends the signed blade `b_i`
  scaled to unit norm, `x_i = b_i / sqrt(2)`. The note does not say how an
  edge picks its blade; the first partner is the literal choice that needs no
  further parameter.
- **Noise.** The receiver sees `v = x_i + sigma n` with `n` standard normal in
  16 dimensions. The replay evaluates `b_i + sqrt(2) sigma n`, which is
  `sqrt(2) v`, so every decoder compares the same quantities and the
  noiseless case stays in integer arithmetic.
- **Sigma grid.** The note names 0.01, 0.05, 0.10, 0.20 and 0.50 and says
  eight levels. The replay adds 0.001, 0.30 and 1.00 as the other three and
  adds sigma = 0 as a ninth, noiseless row.
- **Trials.** All 84 messages x 400 trials per sigma (`messages_simulated`,
  `trials_per_message`). The headline `ser_40` reads a seeded draw of 40
  messages without replacement from the 84, sorted (`subset_messages`);
  `ser_84` reads every trial and is retained as a second figure.
- **Annihilation decoder (C5).** `ihat = argmin_j ||L_{a_j} v||`, where
  `L_a` is the 16 x 16 left-multiplication matrix of `a`
  (`cd_core.left_mult_matrix`). An exact floating-point tie resolves to the
  lowest `j`. The 84 left factors fall into 42 pairs sharing the Gram matrix
  `L_a^T L_a` (`result.json`, `score_twins`), and
  `||L_a v||^2 = v^T L_a^T L_a v`, so the two factors of a pair score every
  received vector alike: their scores tie exactly or differ by rounding at
  every sigma, and the decoder cannot separate them.
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
  `a_j * b_i = 0` exactly (integer arithmetic through `cd_core.cd_multiply`).
  "Mean ties" is the mean over the 84 messages (the note's "3.9 per
  codeword" counts the correct annihilator among them).
- **Signature.** The set `{j : a_j * b_i = 0}` of message `i`; the count is
  the number of distinct sets over the 84 messages.
- **Distinct blade.** The number of distinct `b_i` over the 84 messages.
- **Seed.** `numpy.random.default_rng(314)`. Draw order: the 40-message
  subset, the random codebook, then one noise block per sigma in grid order,
  each shaped (84 messages, 400 trials, 16); the 40-message figures read the
  subset rows of that block. Every block is drawn before any decoding, and
  `parallel.ordered_map` decodes the sigma rows in grid order, so the result
  does not depend on the worker count.

## Control added after the first-partner results

The first-partner rule sends only 28 distinct blades, which hold every
decoder at 1 - 28/84 = 0.667 over all 84 messages, so it cannot separate
the decoder from collisions in the code book. After those results were
seen, the `matching` encoder was added: each left factor sends its mate in
the first perfect matching of the annihilation graph (depth-first in sorted
order, `perfect_matching`), giving 84 distinct blades, each still
annihilated by exactly 4 left factors. Both encoders see the same seeded
noise. It is a post-hoc control and enters no preregistered verdict.

## Result

Counts under the definitions above (`result.json`, `counts`):

| quantity | note | first_partner | matching |
|---|---|---|---|
| mean annihilator ties per codeword | 3.9 | 4.0 | 4.0 |
| distinct annihilator-set signatures | 35 | 28 | 42 |
| distinct transmitted blades | 57 | 28 | 84 |

The blade `b_i` is itself one of the 84 vertices, and every vertex has exactly
4 partners, so every tie count is 4 for any rule that picks `b_i` among the
partners of `a_i`; a mean of 3.9 cannot arise in that family. Picking the
second or last partner gives 28 distinct blades and the third gives 32, so
the note's 57 is reached by none of the tested rules.

Symbol error rate over the 40-message subset (`ser_40`; `ser_84` over all 84
messages is in `result.json`). MF is the matched filter over the encoder's
own codewords, profile the 84-component annihilation-profile decoder:

| sigma | random MF | first_partner C5 | first_partner MF | first_partner profile | matching C5 | matching MF | matching profile |
|---|---|---|---|---|---|---|---|
| 0 | 0.000 | 0.750 | 0.750 | 0.750 | 0.750 | 0.000 | 0.600 |
| 0.001 | 0.000 | 0.763 | 0.750 | 0.750 | 0.762 | 0.000 | 0.600 |
| 0.01 | 0.000 | 0.760 | 0.750 | 0.750 | 0.762 | 0.000 | 0.600 |
| 0.05 | 0.000 | 0.755 | 0.750 | 0.750 | 0.758 | 0.000 | 0.600 |
| 0.1 | 0.000 | 0.762 | 0.750 | 0.750 | 0.764 | 0.000 | 0.600 |
| 0.2 | 0.042 | 0.801 | 0.763 | 0.784 | 0.799 | 0.069 | 0.662 |
| 0.3 | 0.296 | 0.884 | 0.819 | 0.868 | 0.884 | 0.374 | 0.806 |
| 0.5 | 0.705 | 0.952 | 0.904 | 0.948 | 0.950 | 0.745 | 0.929 |
| 1 | 0.923 | 0.981 | 0.966 | 0.982 | 0.981 | 0.929 | 0.980 |

Over all 84 messages (`ser_84`), first_partner holds every decoder at
0.667 at sigma 0 (28 distinct blades) and the C5 decoder at 0.750 from
sigma 0.001 to 0.1; the subset reads 0.750 at sigma 0 because 30 of its 40
messages share a blade with a lower-index message. Under matching the
matched filter resolves all 84 blades without error at low noise while the
annihilation decoder errs at 0.751 over all 84 at sigma 0.01: each blade
has 4 exact annihilators and argmin no longer singles out the sender's. The
profile decoder errs at 0.500 over all 84 (0.600 on the subset), since 42
signatures cover 84 messages. The note's matched-filter floor (0.275) and
profile rate (0.575) reproduce under neither encoder.

## Replay

```sh
PYTHON="${PYTHON:-$(command -v python3)}"
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -W error docs/evidence/c5_zero_divisor_code/replay.py --check
(cd docs/evidence/c5_zero_divisor_code && sha256sum -c SHA256SUMS)
```

`result.json` retains major.minor interpreter and numpy versions; a changed
source, seed or runtime needs an explicit reviewed regeneration.
