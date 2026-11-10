# Reconciliation: codex review of the portable least-squares precision sweep

Source review: `docs/local/reviews/codex-sweep.md` (range `e2a694e7b...315d929bb`). Every finding below was checked
against the source files and the rows in `docs/evidence/least-squares-precision/hosts/*-full.jsonl` before it was
accepted. Commands ran with `GLIBC_TUNABLES=glibc.rtld.optional_static_tls=4096 /usr/bin/python`. Fix commits, in
order: `068f1b71d` (public substrate profile in host rows), `549328395` (QuadBLAS capability probe), `5ba6b3791`
(README claims limited to what rows support). The Advisor verdict is recorded at the end by the session that owns the
pull request.

## Findings

1. **Different input digest on the M1 -- SURVIVES.** The first row of each full file holds `inputs_sha256`; a
   comparison against `build-host-full.jsonl` shows `[]` differing keys for zen4-wsl, zen4-windows,
   aws-sapphire-rapids and oci-a1-neoverse-n1, and `['observed_rate_columns']` for m1-macos. Scores confirm the
   reviewer's values: `m1-macos-full.jsonl:29` binary128 Householder, SLEEF, one thread, `bits_correct_on_scores`
   108.48790024014956 against `aws-sapphire-rapids-full.jsonl:17` 108.090673654462; `m1-macos-full.jsonl:49` arb 128
   bits 120.67179354384993 against `aws-sapphire-rapids-full.jsonl:27` 120.734901543572. Exhaustive comparison of
   the score fields: arb, 24 configurations shared by two or more hosts, 12 differ with the M1 and 0 without it (the
   M1 agrees at 256 bits); SLEEF, 8 shared, 8 differ with the M1 and 0 without; x87, 5 shared, 0 differ (the M1 ran
   no x87 row). The README claim (old lines 251-253, "the same error on every host where it runs") was false as
   written. Fix `5ba6b3791`: equality is scoped to the five hosts with equal digests and the M1 is a separate
   cohort. The reviewer's x87 count of 5 and SLEEF count of 8 reproduce.
2. **Host-record boundary -- SURVIVES, bounded by the owner ruling.** Row 1 of each file carried `os.release`
   (an exact kernel release string), `os.distribution` (a distribution string), `os.win32_ver` and
   `cap.mem_total_bytes`. The owner ruled a public substrate profile (architecture, CPU model, SIMD dispatch, BLAS
   core and version, numpy and scipy versions, OS family) and dropped kernel release, distribution string and memory
   size. Fix `068f1b71d`: `fp_host.os_info` and `fp_host.choose_cap` stop recording them; all 439 rows are rewritten
   by dropping those fields (round trip of untouched lines through `json.dumps` was byte-identical first, so only
   the dropped keys changed); `grep -c` for each host's kernel-release and distribution substrings and the memory
   byte values over `hosts/*.jsonl` returns 0. The second half also survives: `fp_export.py` accepted any
   `--host-label` while `fp_sweep.py:213-216` validated it; `fp_export.py` now calls `fp_host.label_error`
   (verified: a label containing this machine's hostname exits 2). Residual, bounded: `cap.bytes` is
   `min(8 GiB, 0.6 x memory)`, so on the two hosts under 13.3 GB (aws-sapphire-rapids and
   oci-a1-neoverse-n1) the cap size still implies the memory size; the cap is the limit that applied and
   cannot be rewritten without falsifying the record. The README table no longer names the EC2 instance class. The
   owner decides whether the cap size on those two hosts is acceptable.
3. **Cap prose -- SURVIVES.** `m1-macos-full.jsonl:1` has `cap.mechanism="none"`, `enforced=false`, and
   `cap.tried.rlimit.reason="RLIMIT_AS child failed: SubprocessError: Exception occurred in preexec_fn."`; the
   README said macOS falls to `RLIMIT_AS`. The per-child inference also holds: `fp_host.probe_systemd` reads a
   trial scope and `fp_sweep.child_command` (lines 105-112) starts each measured child in a new scope without
   readback, while `fp_sweep.py:242-250` copies the trial record into every row. Fix `5ba6b3791`: README states the
   M1 ran uncapped, that four hosts ran under a systemd scope, and that `enforced` is the trial scope's readback.
   No code change; a per-child readback would need a `fp_backends.py` change and a re-run of every systemd host,
   `not run`.
4. **QuadBLAS capability probe, count 12 -- SURVIVES.** `zen4-windows-full.jsonl:41-52` holds 12 rows whose
   `error` is `NotImplementedError: QuadBLAS is disabled` (6 thread counts x 2 families), each with 2 repeats; the
   README table said 6. The error comes from `numpy_quaddtype.set_num_threads` in `fp_backends.py:237,278`, which
   every quaddtype configuration calls, so `longdouble`-backend rows depend on it as well.
   `quad-falsification/zen4-windows.json:10` records `get_quadblas_version` raising the same error. Fix
   `549328395`: `fp_host.quadblas_status` plus a `quadblas` need on all quaddtype configurations; a monkeypatched
   `get_quadblas_version` raising `NotImplementedError` skipped 12 of 12 quaddtype configurations on a 4-CPU ladder (1, 2, 4), and a
   real call returned None locally in 1 microsecond. The README count is 12 (`5ba6b3791`, `549328395`). The
   retained Windows rows keep their error rows: a Windows rerun is `not run` (remote host).
5. **Missing M1 receipt -- SURVIVES (retained evidence missing).** `grep -rn "41,634\|41634" docs/evidence
   docs/notes docs/runbooks` finds only the README; no committed npz pair or receipt exists, and the only local
   `docs/local/fp-inputs.npz` is the build host's. The digest of `observed_rate_columns` hashes the point rates
   stacked with the replicate columns (`fp_host.input_digests`), so the rows cannot say the point column is
   identical. Fix `5ba6b3791`: the README states the four equal digests and the one differing digest, drops the
   41,634 / 6.4e-4 / "identical bit for bit" sentences, keeps the libm hypothesis labeled with a falsifier, and marks
   the comparison receipt `not run` because it needs the M1's npz.
6. **turion-linux SIGILL unretained -- SURVIVES; the Windows-export half is confirmed as supported.** Windows export: `fp_export.py`
   imports `ascella_cz_ensemble_case`, which imports `qd_platform` (`scripts/ascella_cz_ensemble_case.py:57`), and
   `scripts/qd_platform.py:105` imports `fcntl` at module scope; the Windows rows name `build-host` as exporter, so
   that "not run" is supported. turion-linux: `git log -S SIGILL` shows the term first enters in `315d929bb`;
   `quad-falsification/turion-linux.json` records numpy 2.5.3 and a matmul test, not a numpy 2.5.4 import failure.
   Fix `5ba6b3791`: the README names the retained 2.5.3 record and marks the 2.5.4 run `not run`, with no
   statement of a SIGILL as measured. A probe on the turion-linux host is `not run` (remote host).
7. **Stale portability text -- SURVIVES.** The README said wheel availability of numpy, scipy and python-flint on
   Windows, macOS arm64 and Linux aarch64 was unchecked; rows record `python-flint 0.9.0`, numpy 2.5.4 and scipy
   1.18.1 on all three (`zen4-windows-full.jsonl`, `m1-macos-full.jsonl`, `oci-a1-neoverse-n1-full.jsonl`, key
   `host.packages`), numpy-quaddtype 1.0.0 on Linux x86-64, Windows and macOS arm64, and `null` on the aarch64
   host (its 8 quaddtype rows skip with `ModuleNotFoundError`). The Python versions in the rows are 3.14.4,
   3.14.9 and 3.15.2, so "ran on 3.14.9 only" was stale too. Fix `5ba6b3791`. The README line "numpy-quaddtype
   publishes no Linux aarch64 wheel at any version" contradicted its own later "unverified" sentence and is now
   "not installed on the Neoverse host; existence of a wheel unverified".

## Additional defects found while checking

- README ulp range: "the scipy drivers 0.2 to 13.2" at one thread; the rows give scipy 0.2 to 6.8 (maximum over
  all thread counts 8.8) and 13.2 belongs to numpy lstsq on zen4-windows (`float64 numpy lstsq, OpenBLAS threads 1`
  = 13.200245314584535). Fixed in `5ba6b3791` (numpy lstsq 2.2 to 13.2, scipy drivers 0.2 to 6.8; pinv 2.2 to 14.8
  on the five digest-agreeing hosts, 0.2 on the M1).
- README bootstrap sentence ("comparable across the five hosts that agree"): zen4-windows matches on digests only
  because it ran the build host's npz (its own export is `not run`), so the sentence now names the four hosts that
  ran `fp_export.py` themselves (`5ba6b3791`).
- `git diff --check` reported `README.md:271` blank line at EOF; fixed in `5ba6b3791`.
- The 6-of-10 float64 agreement between zen4-wsl and aws-sapphire-rapids (the scipy drivers at one and two threads)
  reproduces: 30 shared float64 configurations, none with one score on every host. The README now states both.

## Claims the reviewer marked as surviving and the hypotheses

- Thread admission, x87 skips and the zero-identity-leak scan reproduce; the privacy scan covers hostname, user
  name and path strings, and the substrate-profile fix above covers the remaining host-fact classes.
- NumPy sampler hypothesis: stays a hypothesis in the README with its falsifier; the controlled-libm trace is
  `not run` (needs the M1 npz and a macOS build).
- OpenBLAS core conjecture (SkylakeX versus Zen): supported by the 6 equal scipy signatures between zen4-wsl and
  aws-sapphire-rapids, both `SkylakeX` in `host.blas.libraries`, against the build host (`Zen`); the falsifier
  (forcing `OPENBLAS_CORETYPE`) is `not run` and is not in the README.

## Not run, with reasons

- M1 npz comparison receipt: needs the M1 `fp-inputs.npz`; remote host.
- turion-linux numpy 2.5.4 probe: remote host.
- Windows rerun after the QuadBLAS probe: remote host.
- Per-child cgroup readback: needs a `fp_backends.py` change and a rerun on every systemd host.
- Tests: `git grep -n -e fp_sweep -e fp_host` over `tests/` finds none; no test covers these files.

## Gates

`ruff format --check`, `ruff check` and `mypy` through `ci/pinned_tool.py` on `fp_host.py`, `fp_sweep.py` and
`fp_export.py`: clean. `scripts/check_markdown_links.py`: 1083 files, every link resolves. `git diff --check`: clean.

## Nemotron (claude-free, nvidia/nemotron-3-ultra-550b-a55b) on 5ba6b3791

Report: docs/local/reviews/claude-free/claude-nvidia_nvidia_nemotron-3-ultra-550b-a55b.md. Its seven claim verdicts
agree with the rows (it counts 438 rows; the files hold 439).

| Finding | Disposition | Evidence |
|---|---|---|
| Medium: RLIMIT probe imports numpy before the mmap, conflating enforcement with OpenBLAS reservations; caused the M1 failure | Refuted | fp_host.py:234-244 maps cap + 256 MiB: an enforced RLIMIT_AS refuses it whatever numpy reserved, an unenforced one admits it, so the import cannot fake enforcement; it is deliberate, since sweep children import numpy under the same cap. The M1 failure is the SubprocessError raised from preexec_fn (setrlimit, fp_host.py:222-231, 261-262), before the child imports anything. |
| Low: cpu_flags reads numpy's private `_multiarray_umath.__cpu_features__` | Bounded | No public API exposes the dispatch features; the fallback records `unavailable`. |
| Low: probe scope RuntimeMaxSec 960 s | Bounded | The probe exits in milliseconds; the bound only caps a hung probe. |
| Low: fp_export.py needs fcntl, undocumented in --help | Bounded | README.md:228 and :255 state it. |
| Conjecture: SkylakeX core selected on Zen 4 and Sapphire Rapids, divergence from cache geometry and blocking | Hypothesis, recorded | Same falsifier the reconciliation lists as not run: OPENBLAS_CORETYPE forced on both hosts. |

## Advisor verdicts (advisor tool, last reviewer)

All seven codex findings confirmed as surviving; nothing in the rows contradicts them. Nemotron: the medium
RLIMIT/numpy finding's refutation confirmed (an enforced RLIMIT_AS refuses the cap + 256 MiB map whatever numpy
reserved, so the import can cause a false failure but never fake enforcement); the three low findings bounded; the
SkylakeX conjecture stays a hypothesis. The `cap.bytes` residual went to the owner, who ruled on 2026-11-09 to keep it: it is the limit the run applied.

# PR 808 round: codex-pr808.md (head 5ba6b3791), fixed on integration/gororoba-quantum-ultrareview at 314874c8d, 4404df81d

| Finding | Disposition | Evidence |
|---|---|---|
| 1. Required lanes never check fp_host.py, fp_sweep.py, fp_export.py; no tests | Survives | `ci/pr_checks.sh` lint and types lists lacked them. Fixed at 4404df81d: both lists name the three files; mypy then found a real defect (fp_export reused the loop name `inputs` for the prediction dict), renamed; `tests/scripts/test_least_squares_precision_sweep.py` (9 tests) covers the OS-family record, label refusal and exactly 12 (full) / 4 (quick) quaddtype skips. Lint, types, shellcheck -S error clean. |
| 2. Rows publish the macOS product version and the Windows release beyond OS family | Survives | 161 rows carried `host.os.mac_ver` or `host.os.release`. Fixed at 314874c8d: os_info records system and the WSL flag only; the rows drop exactly those keys (word diff shows only those removals; no digest pin of the three files). README table OS column reads macOS and Windows. Bounded: README lines 138-139 (quaddtype falsification table, on main before this PR) still name both product versions; outside this PR's diff. |
| 3. README claims pinned wheels in a venv on every host | Survives | Neoverse rows record numpy-quaddtype null. Fixed at 314874c8d: versions stated per host from `host.packages`; install method not claimed. |
| Claim 4 (QuadBLAS skip exact) | Confirmed | Now a test. |

Advisor pass on this round, applied: README quaddtype table rows relabeled by sweep label and OS family (e721896cd);
the former quaddtype record names named machines in the infrastructure chart. Residual for the owner: the four
`quad-falsification/` records on main carried machine names in file names and contents, and renaming or rewriting
them may break pins.

Final Advisor verdicts (PR rounds): every disposition confirmed. Vocabulary miss and Pearson-correlation refusal
bounded (the guard catches an omitted term, not a deliberate rename; typed preregistration schema is the full fix).
Guard scope: Quandela plan and submit (submit routes through plan; IQM and Quantum Inspire post through their own
modules). Host-name files on main go to the owner. Later commits: dada2f71a, 8860b0422, 7c0ed5dc4 (figures), 9e1233cca
(archive record). Contracts lane: 82 passed.

## Addendum: the second nemotron report on 5ba6b3791

Since the verdicts above, the owner ruled on the quaddtype residual: successor records under the sweep labels with
the OS family only (ee7cdd9a3), and the three build-host records relabeled the same way (c47a7a976).

A second claude-free launch on the same nemotron brief, filed locally as an aborted start, went on to write a full
report ([review-nemotron-second.md](review-nemotron-second.md)) that the reconciliation above never read. The report
records no head; its README citations (lines 260-268) fit 5ba6b3791, the head its brief names, so that head is
inferred. Each
finding was checked against the retained rows in `docs/evidence/least-squares-precision/hosts/*-full.jsonl` and the
source on the integration branch.

| Finding | Disposition | Evidence |
|---|---|---|
| README "every configuration run on two or more of them scores identically" is false: the x87 refinement steps differ | Bounded, fixed | The 3 `float64 pinv + k x87 refinement steps` configurations differ on build-host, zen4-wsl and aws-sapphire-rapids (worst score error 1.32 to 1.50 ulp). They start from the OpenBLAS pinv, so they belong with the float64 configurations, yet the README's count of 30 float64 configurations left them out (33 float64 configurations run on two or more hosts; none has one score on every host). The README paragraph now scopes the equality to configurations that bypass OpenBLAS, counts all 45 of them (24 arb, 16 binary128 including the 8 `longdouble`-backend configurations it had omitted, 5 x87; none differs), and states the 3 refined configurations separately, including that zen4-wsl and aws-sapphire-rapids agree on none of them |
| Only 2 of the 5 x87 configurations score identically | Refuted | The 5 shared pure-x87 configurations (Householder at 1, 2, 4 and 8 workers, normal equations) each have one score on every host that ran them; the report counted the refinement configurations as x87 |
| `wait_for_idle` takes `os.cpu_count()` rather than the admitted worker count | Bounded, by design | README.md documents the threshold as 0.5 x `os.cpu_count()`; the 1 minute load average is system-wide, so the logical CPU count is its scale, and each row records the threshold and the load at release |
| `label_error` checks hostname substrings of 3 or more characters only | Bounded | A 1- or 2-character hostname would reject almost every label; the label regex still bars paths, and the six retained labels were chosen by hand |
| Cap size implies memory on the two small hosts | Owner ruling | `cap.bytes` stays as the limit the run applied (2026-11-09) |
| Conjecture: float64 scores follow the OpenBLAS build, MAX_THREADS 64 on zen4-wsl and aws-sapphire-rapids against 24 on zen4-windows | Premise refuted; hypothesis open | No host record carries a MAX_THREADS field; the values the report reads are threadpoolctl's runtime `num_threads` (32, 2 and 24), which contradict its 64 for aws-sapphire-rapids. A dependence on the OpenBLAS build stays a hypothesis with the falsifier listed above (`OPENBLAS_CORETYPE` forced on both SkylakeX hosts) |

## Addendum: the tool versions of the PR-round codex review

The PR-round codex review ran the installed ruff 0.17.3 and mypy 2.4.0 and marked the pinned ruff 0.17.4 and mypy
2.4.1 not run, because its sandbox had no network to fetch them. The deviation sits in that brief
([brief-pr.md](brief-pr.md)), which named `/usr/bin/python`; `workspace/review-brief-template.md` in
gororoba-infrastructure names the pinned interpreter, which `ci/AGENTS.md` ("Host environments") builds as
`ci-py3.14.7` with ruff and mypy at their pins. The pinned lint and types lanes, run by the orchestrator, reported every
check passed, 944 files formatted and no mypy issue in 915 source files.
