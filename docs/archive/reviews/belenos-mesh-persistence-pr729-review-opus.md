# Opus review of pull request #729 at 5deb80f95

Adversarial review of `5deb80f95` against `origin/main`. Every file was read with `git show`. All computations were
read-only scratch runs under the ignored `docs/local/` directory.

## Defects, most severe first

**1. The slope bound is liberal for "redrawn", and the power table hides it**
(`scripts/belenos_mesh_persistence.py:239-243`, `:283`; design document lines 96-106).

- The upper bound `beta + t(0.95, 17) sqrt(s^2 / Sxx)` pools a single residual variance over all six blocks. It is
  invalid in principle whenever the fresh mesh error has a different standard deviation in each slot.
- The retained per-block standard deviations run from 0.028 to 0.082, and the mode-swap case's slot homogeneity
  test gives p 2.5e-8.
- The blocks with large |e_old| are also the noisy ones, so the regression through the origin understates the
  variance of the slope estimate. The bound is too low, which makes the test liberal for "redrawn".
- `power()` draws one sigma for every block, so the power run cannot see it.
- Evidence (3,000 simulated jobs, each block's fresh error at its retained standard deviation rescaled to the
  pooled 0.0515): P(redrawn | beta 0.5) is 0.071 against a nominal 5 %; P(persists | beta 0.5) is 0.69 against the
  claimed 0.80. With the unscaled standard deviations the figures are 0.085 and 0.63. With a flat sigma the run
  reproduces 0.044 and 0.81. Size at beta 0 stays at 0.048 to 0.050, because the relabeling p-value needs
  exchangeability within a block only.
- Fix: a per-block-variance (weighted) or sandwich standard error, or a relabeling-based bound; a power simulation
  with a per-slot sigma; a restated table.

**2. The identity reading can be triggered without the mesh changing** (`:313-323`).

- The check hashes the serialized `:PCVL:zip:` string. A change in Perceval, the serializer or zlib gives "seed
  does not reproduce its mesh" for an identical mesh, and the design document treats that reading as answering the
  program question.
- A missing `computed_circuit` hashes to None, which becomes `same_mesh` false and the same final reading.
- Fix: deserialize and compare the decoded parameters or unitary within a tolerance, keeping the byte digest as a
  secondary field; a missing field reads "identity undetermined".

**3. The block-matching test cannot fail under the mutation it targets**
(`tests/scripts/test_belenos_mesh_persistence.py:113-135`).

- The fixture uses `300 + 40 i + 25 j`, so after centering every block has the same row. Pairing the blocks in
  reverse order still gives slope 1.0 and p 5.2e-9.
- Fix: a distinct deviation pattern per block, with slope 1 asserted for key matching and a slope other than 1 for
  positional matching.

**4. Other test gaps found by mutation thinking.**

- `slope_upper` and `dof` are never checked with a nonzero residual; a changed `dof`, `t.ppf(ALPHA)` or a dropped
  `sqrt` all pass.
- No combination in the brute-force fixture sums exactly to the observed value, so `side="right"` or a removed
  tolerance passes.
- The drift statistic is 0 in the fixture, so the drift threshold, its degrees of freedom and the withhold path go
  untested.
- An identity mismatch is tested on replicate 0 only, never on the second primary repeat or a missing field.
- The secondary restrictions are never asserted.

**5. The document misstates what happens at beta 0.25, and "persists" has no slope floor**
(design document lines 105-106 and 145; `read`, `:247-252`).

- The document calls beta near 0.25 "the region where one job leaves the answer indeterminate". The power table
  gives indeterminate 0.384, persists 0.2905, redrawn 0.3255.
- "persists" establishes beta above 0 only. So 29 % of runs at a persistence the document itself calls not worth
  selecting would open the 8 to 10 credit teleportation case.
- Fix: a lower-bound condition on "persists", or a gate of the second case on the beta interval, or corrected text.

**6. Minor rule items.**

- `bound_seconds` (`:149-154`) re-implements `swap.iteration_seconds()`.
- `--power` reads sigma from an unsorted `next(glob(...))` (`:370`); all nine `analysis.json` files hold
  0.05150455979158212 today, and the choice is nondeterministic.
- `drift += (z or 0.0) ** 2` keeps 6 degrees of freedom when a z is undefined (conservative), and a block with
  `n = 0` raises ZeroDivisionError instead of withholding.

## Invalid in principle, conservative or negligible here

- **Mesh error shared across slots.** The independent relabeling over 24^6 assumes blocks are independent within one
  compiled mesh. For these retained deviations the effect of a shared component is conservative, because the sum of
  squared column sums (0.0439) is below the sum of squared deviations (0.0579); simulated size is 0.054, 0.038 and
  0.023 at shared shares 0, 0.5 and 0.9. It would turn liberal if the retained deviations were coherent across
  slots.
- **Attenuation.** Old binomial noise attenuates the slope; the reliability is about 0.99.
- **Same iteration order in both windows.** A shared within-job drift adds a common pattern equivalent to a beta of
  about 0.003 at the retained drift size.
- **Sign-flip test labels.** A and B are jobs, so the uncentered product absorbs a mean term of about +0.0006
  against a null standard deviation of about 0.0074: conservative for both tests.
- **Sign-flip null against the chance model.** The script's chance model predicts drops in correctness as large as
  those observed; the document's "short of significance, exploratory" framing is the most the test supports, and
  0.015625 is the test's floor of 1/64.

## Checks that found nothing

- Code against the preregistration: T, the relabeling enumeration, the tolerance and tie direction, beta, the 17
  degrees of freedom, the drift D on 6 degrees of freedom and the secondary slot masks match `preregistered()` and
  the design document.
- `documents()` rebuilds `cases.json` and `circuit.json` byte for byte; the retained table, the pooled standard
  deviation 0.0567, the binomial standard errors and the retained drift (D 13.13, p 0.041) reproduce.
- `power(21344, 0.0515...)` reproduces `belenos-mesh-persistence-power.json` exactly; clipping never binds.
- The QRNG ledger row for draw `054809Z` index 2 (value 21344) is present and unique.
- The bound is 257.1 s against the 270 s margin; the credit ceiling is 1.09; the script has no submit path.
- The corrected numbers of the design investigation and the herald analysis follow from the JSON records. The -Z
  claim of five leading patterns at 8 % to 16 % each was not checked: the per-pattern shares are not in the record.
- The first-principles JSON only gains fields, the new document has its map row, and no mock outcome enters the
  analysis.
