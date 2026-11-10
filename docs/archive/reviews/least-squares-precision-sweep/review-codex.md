# Adversarial review: portable least-squares precision sweep

Scope: `e2a694e7b...315d929bb`, read-only review of the portable runner, exporter, README claims, and all 374
full-run rows from six host configurations. The audit used exhaustive comparisons; it made no random draw and
consumed no QRNG index.

## Ranked findings

1. **SERIOUS -- [computed] The central cross-host equality claim is false as written.** `README.md:251-253` says
   arb, SLEEF binary128, and x87 give the same per-quantity error on every host where they run. The M1 used different
   `observed_rate_columns` bytes, and its errors differ: binary128 Householder at one thread scores
   108.48790024014956 in `hosts/m1-macos-full.jsonl:29` versus 108.090673654462 in
   `hosts/aws-sapphire-rapids-full.jsonl:17`; arb at 128 bits scores 120.67179354384993 in
   `hosts/m1-macos-full.jsonl:49` versus 120.734901543572 in `hosts/aws-sapphire-rapids-full.jsonl:27`. Exhaustive
   comparison found differences in all eight shared SLEEF configurations and shared arb configurations at 64, 128,
   and 192 bits; x87 had zero differences. Remedy: qualify equality by identical input digest and report the M1
   cohort separately. Comparing arithmetic errors across different problems does not establish host invariance.
2. **SERIOUS -- [proved] The public rows contain host facts that the workspace guide reserves for the private
   infrastructure repository.** The guide says the infrastructure chart owns every host and a public file needing a
   host fact points there (`<workspace>/AGENTS.md:61-65`), and a fact naming a host belongs
   there (`<workspace>/AGENTS.md:69-71`). Every row embeds the public label, exact kernel
   release, distribution, CPU model, CPU and memory counts, SIMD dispatch, BLAS architecture, and package fingerprint;
   `fp_host.host_record` assembles these fields (`fp_host.py:451-470`), for example in
   `hosts/aws-sapphire-rapids-full.jsonl:1` and `hosts/oci-a1-neoverse-n1-full.jsonl:1`. The exhaustive string scan found
   no credential, username, hostname, or absolute local path, but the broader boundary still fails. Remedy: keep the
   detailed record in gororoba-infrastructure and publish a digest-bound, nonidentifying substrate profile.
   `fp_export.py:38` also accepts an unvalidated exporter label, unlike `fp_sweep.py:213-216`, so a future NPZ can
   inject a hostname into every row.
3. **SERIOUS -- [computed] The cap prose overstates macOS behavior and per-row enforcement evidence.**
   `README.md:180-184` says macOS falls to `RLIMIT_AS`; the M1 rows record `mechanism="none"`, `enforced=false`, after
   the RLIMIT probe failed in `preexec_fn` (`hosts/m1-macos-full.jsonl:1`). The row is truthful; the README is not.
   For systemd, `probe_systemd` reads a trial scope (`fp_host.py:267-291`), while each measured child starts a new
   scope without readback (`fp_sweep.py:105-112`); the trial result is copied into every row
   (`fp_sweep.py:242-250`). Thus `enforced=true` is measured for the trial and inferred for each run. Remedy: describe
   the M1 as uncapped, rename the field to express probe evidence, or emit each measured child's cgroup readback.
4. **SERIOUS -- [computed] Windows QuadBLAS absence is a capability skip, not twelve repeated solver failures.**
   `fp_host.quad_status` only constructs the SLEEF dtype (`fp_host.py:185-193`), although the retained Windows record
   shows `get_quadblas_version()` raises `NotImplementedError: QuadBLAS is disabled`
   (`quad-falsification/zen4-windows.json:10-11`). `hosts/zen4-windows-full.jsonl:41-52` therefore records twelve
   failed rows with two repeats each. The README table calls these “6 QuadBLAS errors” (`README.md:246`); the count is
   12 error rows. Remedy: add `quadblas_status()` calling public `numpy_quaddtype.get_quadblas_version()` and make only
   SLEEF configurations require it. The call measured 0.0000021 s locally; a 1x1 contiguous matmul fallback measured
   0.0000871 s. An installed capability probe is cheaper and sounder than a `sys.platform` proxy.
5. **SERIOUS -- [measured claim, retained evidence insufficient] The rows prove which digest differs, not where inside
   the array it differs.** The first row of each full file proves Zen 4 WSL, Sapphire Rapids, and Neoverse N1 match the
   build host on all five digests, while M1 differs only on `observed_rate_columns`
   (`hosts/build-host-full.jsonl:1`, `hosts/zen4-wsl-full.jsonl:1`, `hosts/aws-sapphire-rapids-full.jsonl:1`,
   `hosts/oci-a1-neoverse-n1-full.jsonl:1`, `hosts/m1-macos-full.jsonl:1`). No committed NPZ pair or comparison receipt
   supports `README.md:256-258` claims that the point column is identical, exactly 41,634 replicate rates differ, and
   the maximum difference is 6.4e-4. Remedy: retain a digest-bound receipt with shapes, point equality,
   differing-index count, and maximum absolute difference.
6. **SLOPPY -- [proved] The two “not run” explanations have unequal evidence.** Windows export is supported: its rows
   name `build-host` as exporter (`hosts/zen4-windows-full.jsonl:1`), and `fp_export.py` imports
   `ascella_cz_ensemble_case`, which imports `qd_platform` (`scripts/ascella_cz_ensemble_case.py:55-58`), whose
   top-level `fcntl` import is unavailable on Windows (`scripts/qd_platform.py:98-106`). The turion-linux SIGILL statement
   (`README.md:265-266`) has no retained command, log, row, or receipt in this change. The existing turion-linux record
   documents NumPy 2.5.3 and a quaddtype matmul test (`quad-falsification/turion-linux.json:1-10`). Retain the NumPy 2.5.4
   SIGILL probe before presenting it as measured.
7. **SLOPPY -- [computed] The portability section contains stale uncertainty.** `README.md:202-205` says python-flint
   availability on Windows, macOS arm64, and Linux aarch64 is unchecked, but those rows record python-flint 0.9.0 and
   successful arb runs (`hosts/zen4-windows-full.jsonl:65-88`, `hosts/m1-macos-full.jsonl:45-60`,
   `hosts/oci-a1-neoverse-n1-full.jsonl:25-32`). Replace the pre-run statement with the measured wheel matrix.

## Claims that survive

- **[computed] Thread admission survives.** `fp_sweep.py:223-241` bounds the grid by
  `min(os.cpu_count(), parallel.workers())`; exhaustive parsing found zero thread variables above `host.cpus_used`.
  `fp_host.thread_ladder` (`fp_host.py:116-124`) produces the recorded ladders.
- **[computed] x87 skips survive.** Exhaustive parsing found zero executed x87 rows on non-x86 or
  `longdouble_nmant != 63`. The reasons agree with `fp_host.x87_status` (`fp_host.py:174-182`): M1 skips 16, Neoverse
  skips 6, and Windows skips 22.
- **[computed] The float64 claim survives only in its universal sense.** Among 30 configurations shared by at least
  two hosts, zero had one signature on every host. Six SciPy configurations had an exact Sapphire-Rapids/Zen4-WSL
  pair, so “moves with the host” must not mean every pair differs (`README.md:251-255`).
- **[computed] Direct identity leakage was absent.** The recursive JSON-string scan found zero `/home/`, `/Users/`,
  Windows user-profile paths, email-like strings, credentials, account identifiers, usernames, or hostname fields.
  This proves only those string classes, not the broader host-fact policy in finding 2.

## NumPy sampler hypothesis

**[hypothesis, source-compatible]** `resampled_rates` calls `Generator.multinomial` and
`Generator.negative_binomial` (`scripts/ascella_cz_tomography_case.py:671-693`). NumPy function
`random_multinomial` delegates to binomial draws; `random_binomial_btpe` uses `floor`, `sqrt`, and `log`;
`random_negative_binomial` draws gamma then calls `random_poisson`, whose PTRS path uses `log` and `floor`
(`numpy/random/src/distributions/distributions.c`: named functions). The source does not supply the proposed
falsifier; it makes platform-libm accept/reject divergence plausible but does not identify Apple libm as the cause.
A retained trace of the first divergent draw or a build using one controlled math implementation would test it.

## Additional BLAS-kernel conjecture

**[hypothesis]** Within the Linux x86 wheel cohort, selected OpenBLAS core and driver appear more predictive of
rounding than CPU vendor. Sapphire Rapids and Zen 4 WSL both report runtime architecture `SkylakeX` and have identical
SciPy `gelsd`, `gelsy`, and `gelss` signatures at one and two threads, while the build host reports `Zen` and differs
(`hosts/aws-sapphire-rapids-full.jsonl:1`, `hosts/zen4-wsl-full.jsonl:1`, `hosts/build-host-full.jsonl:1`). Falsifier:
force `OPENBLAS_CORETYPE=Haswell` or `Zen` on one Linux wheel host and retain the same signatures, or force the same
core, wheel, inputs, driver, and thread count on another Linux host and obtain different signatures.

## Reproducible command results

- `git diff --check e2a694e7b...HEAD` reports `README.md:271: new blank line at EOF.`
- Full rows/skips/errors: Sapphire Rapids `32/0/0`, build `74/0/0`, M1 `60/16/0`, Neoverse `32/14/0`, Windows
  `88/22/12`, Zen 4 WSL `88/0/0`.
- Signatures: arb differs on M1 at 64/128/192 bits; SLEEF `cross_host_configs=8, diffs=8`; x87
  `cross_host_configs=5, diffs=0`; float64 `cross_host_configs=30, all_equal=0`, with six exact
  Sapphire-Rapids/Zen4-WSL pairs.
- Thread/privacy output: `THREAD_X87_VIOLATIONS []`; `SENSITIVE_HITS_COUNT 0`.

## Verdict

The runner executes on the named OS/arch families, bounds its thread grid, records honest skip reasons, and retains
useful numerical evidence. The narrative is not ready to merge: it compares M1 errors across different input bytes
while claiming host invariance, publishes host fingerprints contrary to the workspace boundary, overstates cap
enforcement, counts twelve Windows errors as six, and leaves the strongest macOS and turion-linux measurements without
durable receipts. The smallest defensible repair scopes equality by input digest, records the missing receipts, makes
QuadBLAS a probed capability, and moves or sanitizes the host record.
