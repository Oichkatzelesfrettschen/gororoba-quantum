# Pull request 822 read-only review

Reviewed `d5ff68e2...416b28f1` with Python 3.14.9 and Singular 4.4.1. Audit elapsed: 16m 37s.

## Ranked findings

1. **High — [proved] `nfmodStd` does not provide the exact certificate claimed for these inputs.**  
   [README.md:114](docs/evidence/a5-char0-transfer/README.md:114) says the final test establishes that the reconstructed result is the input ideal’s standard basis. The installed library instead:

   - rejects primes dividing input denominators or leading coefficients and primes with unsuitable minimal-polynomial factorization ([nfmodstd.lib:52](/usr/share/singular/LIB/nfmodstd.lib:52), [nfmodstd.lib:148](/usr/share/singular/LIB/nfmodstd.lib:148));
   - discards minority leading-monomial patterns as unlucky primes and reconstructs from the remaining primes ([nfmodstd.lib:864](/usr/share/singular/LIB/nfmodstd.lib:864));
   - tests at an additional finite-field prime that the candidate and input generate the same ideal modulo that prime ([nfmodstd.lib:697](/usr/share/singular/LIB/nfmodstd.lib:697));
   - finally proves only that every input generator reduces to zero by the candidate and that the candidate is a Gröbner basis of its own ideal ([nfmodstd.lib:572](/usr/share/singular/LIB/nfmodstd.lib:572)). It does not prove in characteristic zero that every candidate generator belongs to the input ideal.

   [Computed] The relevant rings use global `dp`, and the retained `G` has mixed total degrees. Singular’s modular-standard-basis documentation calls global inhomogeneous output “with high probability”; exactness follows additionally only for homogeneous input or a local ordering ([modstd.lib:34](/usr/share/singular/LIB/modstd.lib:34)). The README must describe the modular result as probabilistic until reverse membership is certified exactly.

2. **High — [proved] The direct and modular Iso records do not establish that their Q(i) relation spaces are equal.**  
   [quadrics-iso-nm.json:1](docs/evidence/a5-char0-transfer/quadrics-iso-nm.json:1) and [quadrics-iso-nm-modular.json:1](docs/evidence/a5-char0-transfer/quadrics-iso-nm-modular.json:1) retain identical dimensions and reductions but retain neither Q(i) rows nor a canonical RREF digest. Two different Q(i) RREFs can differ by `32009*32029` in a free entry and reduce identically at both primes.

   [Computed] Re-parsing the modular log produced:

   ```text
   targets 153 raw_relations 68 rref_dimension 68 max_denominator 1 has_imaginary True
   prime 32009 k2_dimension 68 bad_denominators 0 echelon_equal True mutation_detected True
   prime 32029 k2_dimension 68 bad_denominators 0 echelon_equal True mutation_detected True
   ```

   [Proved] The mutation at [quadric_lift.py:213](docs/evidence/a5-char0-transfer/quadric_lift.py:213) proves that the comparator notices one selected `+1` perturbation. It does not prove producer correctness or equality between the two Q(i) outputs.

   [Computed] The cheapest decisive check is one direct Iso rerun that records a canonical Q(i) RREF digest, followed by comparison with the RREF recoverable from the retained modular log. The retained direct run took 1,507 seconds, so that check exceeded this review’s five-minute computation limit.

3. **High — [proved] E8-bar to VB was compared at 32029 only, not at both primes.**  
   [quadrics-e8-vb.json:13](docs/evidence/a5-char0-transfer/quadrics-e8-vb.json:13) contains one prime. `SOURCES["e8-vb"]` likewise contains only 32029 ([quadric_lift.py:41](docs/evidence/a5-char0-transfer/quadric_lift.py:41)). The README and ledger correctly disclose that boundary ([README.md:153](docs/evidence/a5-char0-transfer/README.md:153), [ledger.tsv:294](docs/evidence/a5-exceptional-fibers/ledger.tsv:294)). Claim 3 is therefore falsified as worded, while the repository text is bounded correctly.

   [Proved] The producer route does match: `e8-vb` selects the Nakayama route at [fiber_inputs.py:60](docs/evidence/a5-kernel-attachments/fiber_inputs.py:60), and both header emission and the Q(i) driver call `_nakayama_inputs` ([fiber_inputs.py:149](docs/evidence/a5-kernel-attachments/fiber_inputs.py:149), [reduction_check.py:54](docs/evidence/a5-char0-transfer/reduction_check.py:54)).

4. **High — [proved] This branch still relies on the externally refuted “check 3” transfer criterion.**  
   [Hypothesis, supplied by the brief] The counterexample lives on another branch and was not independently replayed here. This checkout still presents good reduction of `J + m^N` as the lower-bound transfer mechanism at [a5-char0-and-kernel-limits.md:40](docs/notes/topics/a5-char0-and-kernel-limits.md:40), incorporates it into the proposition at [a5-char0-and-kernel-limits.md:56](docs/notes/topics/a5-char0-and-kernel-limits.md:56), and points to that dependency at [README.md:13](docs/evidence/a5-char0-transfer/README.md:13). Ledger rows A5-249 and A5-277 accurately report basis comparisons, but those computations cannot retain their advertised transfer role if the criterion is refuted.

5. **Medium — [proved] Abrupt stops can still lose logs.**  
   Singular stdout is streamed through `tee`, but Singular stderr and `/usr/bin/time -v` remain in the driver’s `communicate()` pipe ([runner.py:40](docs/evidence/a5-char0-transfer/kaggle/runner.py:40), [nullity16_rees_fibers.py:174](docs/evidence/a5-kernel-attachments/nullity16_rees_fibers.py:174)). An outer timeout or Kaggle cancellation can kill the driver before that buffered stderr reaches any retained file. Git fetch and package installation also run before `driver.log` opens and without retained output ([runner.py:79](docs/evidence/a5-char0-transfer/kaggle/runner.py:79), [runner.py:105](docs/evidence/a5-char0-transfer/kaggle/runner.py:105)).

   [Proved] A child return code is recorded only when the wrapper survives through [runner.py:128](docs/evidence/a5-char0-transfer/kaggle/runner.py:128). The test checks arithmetic and `last_line`; it does not exercise an abrupt stop ([test_a5_kaggle_kernels.py:62](tests/test_a5_kaggle_kernels.py:62)).

6. **Medium — [computed] The E8 stop stage is retained, but the memory-cause attribution is not.**  
   [summary.json:10](docs/evidence/a5-char0-transfer/kaggle/a5-char0-e8-quadrics/output/summary.json:10) records `rc=1`, 27,718.2 driver seconds, and the last stage. [driver.log:1](docs/evidence/a5-char0-transfer/kaggle/a5-char0-e8-quadrics/output/driver.log:1) records Singular status 137. [singular.log:635](docs/evidence/a5-char0-transfer/kaggle/a5-char0-e8-quadrics/output/singular.log:635) proves execution entered `std(Q)` after all 231 products.

   [Hypothesis] Exit 137 is consistent with an OOM kill but does not identify the killer. The retained files contain neither a cgroup `oom_kill` delta nor a memory peak. W8 has no retained output directory, so [README.md:109](docs/evidence/a5-char0-transfer/README.md:109)’s workstation-memory statement also lacks a retained record. The cheapest decisive evidence is before/after `memory.events`, `memory.peak`, and streamed stderr.

7. **Medium — [measured] The new Singular script contains a substantial serial loop over independent work.**  
   Products `P[i]` and the `SliceM[k]*P[i]` generators are constructed serially at [quadric_lift.py:56](docs/evidence/a5-char0-transfer/quadric_lift.py:56). The E8 log reaches product 231 at Singular time 107 and starts `std(Q)` at 823, leaving 716 seconds in serial generator construction. The loop does not use `gororoba_quantum/parallel.py`, contrary to the repository rule for CPU-bound independent items.

8. **Low — [proved] `git diff --check` reports an added blank line at EOF.**  
   The defect is at [README.md:158](docs/evidence/a5-char0-transfer/README.md:158).

## Claims 1–8 disposition

1. **[Computed/partly falsified]** Each Iso output reduces to K2 at both primes; equality of the two Q(i) spaces is unrecorded. Coefficient reduction, denominator rejection, RREF comparison, and the selected mutation operate as described at [quadric_lift.py:89](docs/evidence/a5-char0-transfer/quadric_lift.py:89) and [quadric_lift.py:131](docs/evidence/a5-char0-transfer/quadric_lift.py:131).
2. **[Proved false as an exact claim]** `nfmodStd` supplies a high-probability result for these global inhomogeneous inputs, not the asserted exact reverse-membership certificate.
3. **[Proved false at 32009; proved at 32029]** The Nakayama producer route matches, but only the 32029 K2 comparison exists.
4. **[Computed with boundary]** Both E8-bar to N-minus and W8 to N-minus retain no algebraic verdict. The E8 stage and exit are retained; the OOM cause and W8 workstation stop are hypotheses.
5. **[Partly proved]** Limit arithmetic, file streaming, heartbeats, and wrapper-surviving return codes work. Setup failures, stderr, and external cancellation leave log-loss paths.
6. **[Computed]** An in-memory regeneration found code and metadata byte-equal for all five kernels. The E8 override is documented at [make_kernels.py:19](docs/evidence/a5-char0-transfer/kaggle/make_kernels.py:19); commit `07ecf27e...` contains the E8 arguments and stage instrumentation.
7. **[Computed/proved]** New ledger rows A5-294 and A5-315 agree with their JSON records and use `survives`. The broader check-3 dependency remains in the characteristic-zero transfer prose.
8. **[Computed/partly falsified]** A sensitive-pattern scan across all 25 changed files returned zero token, key, email, host-home-path, or account-identifier matches. Public GitHub and Kaggle owner slugs are allowed. The independent Singular loops violate the parallelization rule.

## Verification and publication boundary

- **[Computed]** Manual runner assertions passed for timeout rewriting, limit arithmetic, failure classification, and retained last-stage reading.
- **[Measured]** Pytest could not start because the read-only environment provides no writable temporary directory; it failed before test collection.
- **[Measured]** Final worktree observations match the initial observations: HEAD `416b28f1`, base `d5ff68e2`, and the unrelated untracked `docs/archive/reviews/2026-11-11-char0-quadrics/` remains present.
- **[Computed]** No retained file in this pull-request diff must leave a public repository. The retained files contain no credential or prohibited identifier detected by the bounded scan.

