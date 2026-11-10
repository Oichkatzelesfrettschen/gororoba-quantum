# Brief: the portable least-squares precision sweep and its six-host results (read-only review)

You review a Python sweep runner, its README claims and 439 retained JSON-lines rows. Work read-only with the tools
you have (Read, Grep, Glob; reads reach only files under the current directory). Change no file. Answer on
standard output as plain text under 150 lines; a harness captures it. Every path below is relative to the current
directory. Read each file this brief names before answering. If a file you need is missing, say which and continue
with the rest.

## What the change is

Five commits on top of `e2a694e7b` add a sweep that runs the least-squares backends of `fp_backends.py`
(float64 numpy/scipy, x87 80-bit, binary128 through numpy-quaddtype, arb) one configuration per child process under a
memory cap, on any host, and write one JSON row per configuration. Six host configurations ran it: a build host and
a Zen 4 machine (both Linux under WSL2), a Zen 4 Windows install, an AWS Sapphire Rapids VM, an OCI Neoverse N1
VM (Linux aarch64) and an Apple M1 (macOS).

Precomputed inputs, all under `docs/local/briefs/sweep-nemotron-inputs/`:

- `git-log.txt`: the five commits (`git log --oneline e2a694e7b..HEAD`).
- `diff-stat.txt`: the changed files.
- `diff-code-and-docs.patch`: the full diff of code, README and checklist (rows excluded). Read this first.
- `rows-summary.tsv`: one line per row of every `hosts/*.jsonl` file (file, line number, configuration, status, cap
  mechanism, thread count, scores). The score columns are `bits_correct_on_scores` and `process_fidelity_ulp64`.
- `host-records.json`: the host record, cap record, five input digests and input provenance of the first row of each
  file.
- `diff-full.patch`: the diff including rows, 1.8 MB; search it with Grep and never Read it whole.

Files under review (full relative paths):
`docs/evidence/least-squares-precision/fp_host.py` (new), `docs/evidence/least-squares-precision/fp_sweep.py` (rewritten), `docs/evidence/least-squares-precision/fp_export.py`,
`docs/evidence/least-squares-precision/README.md` (sections "Portable sweep across hosts" and "Results across hosts"),
`docs/evidence/least-squares-precision/hosts/sweep-checklist.md`, and `docs/evidence/least-squares-precision/hosts/*.jsonl` (rows; each line is several KB, so prefer Grep with a narrow
pattern or the summary file). Context: `docs/evidence/least-squares-precision/fp_backends.py` (unchanged), `docs/evidence/least-squares-precision/quad-falsification/*.json` (earlier
records), `scripts/qd_platform.py`, `scripts/ascella_cz_ensemble_case.py` and `AGENTS.md` (repository rules).
The `docs/local/` directory is ignored by git: open its files with Read and an exact path, because Glob and Grep may
skip ignored files.

## Rules the change must meet

- A row holds a public substrate profile: architecture, CPU model, SIMD dispatch, BLAS core and version, numpy and
  scipy versions, OS family. The exact kernel release, the distribution string and the memory size stay out; a host
  name, user name or local path never appears. The owner ruled this profile acceptable for public rows.
- A README sentence states only what rows or retained records support; a check that did not run is marked `not run`
  with its reason.

## Claims under review (each is a claim, not a fact; justify or falsify it)

1. `fp_sweep.py` runs on Linux, macOS and native Windows. Its cap mechanism (systemd scope with `memory.max` read
   back, `RLIMIT_AS` with a 2 GiB floor, or none) is recorded per row. The M1 rows record mechanism `none`,
   `enforced` false because its `RLIMIT_AS` probe failed, and the README says the M1 ran uncapped. For systemd rows
   `enforced` is the readback of a trial scope, and each measured child starts its own scope without readback.
   Falsifier: a row whose recorded cap differs from what applied, README prose that overstates it, or a path that
   cannot run on its named OS.
2. The thread ladder never exceeds the host's usable CPUs, and skipped configurations carry a correct reason.
   Falsifier: a row with `host.cpus_used` below its thread count, an x87 row run on non-x86 or on a 64-bit
   `long double`, or a skip reason that disagrees with `fp_host.x87_status`, `quad_status` or `quadblas_status`.
3. On the five hosts whose five input digests agree (every host except the M1), the arb normal-equation, binary128
   (SLEEF) and x87 configurations give identical scores on every pair of hosts that ran them, while no float64
   configuration through the BLAS has one score on every host. The M1 ran a different `observed_rate_columns`
   array, so the README treats it as a separate cohort (it reports differences in 12 of 16 arb configurations and
   all 8 SLEEF configurations) and draws no host-dependence conclusion from it. The README adds that the two
   `SkylakeX` hosts agree on 6 of the 10 float64 configurations they share. Falsifier: a non-BLAS configuration whose
   score differs between two hosts with equal digests, a float64 configuration with one score on every host, or
   wrong counts. Compute the counts from `rows-summary.tsv`.
4. `fp_host.quadblas_status` calls `numpy_quaddtype.get_quadblas_version()` and every quaddtype configuration
   requires it (`fp_sweep.configs`, field `needs`), because each calls `numpy_quaddtype.set_num_threads`
   (`fp_backends.py`), which raises `NotImplementedError` where the Windows wheel disables QuadBLAS. The retained
   Windows file holds 12 error rows (`NotImplementedError: QuadBLAS is disabled`), now correctly counted in the README.
   Falsifier: a configuration that reaches `set_num_threads` without the need, an error-row count other than 12, a
   probe that raises or skips on a host where QuadBLAS works.
5. Four of the five input digests are equal on all six hosts and `observed_rate_columns` differs on the M1. The
   README makes no claim about where in the array the M1 differs; the receipt that would show it is `not run`. The
   libm accept-reject explanation is labeled a hypothesis. Falsifier: a README sentence that asserts a difference
   count, a magnitude or a mechanism as measured, or a digest that the rows contradict.
6. Row hygiene: no row carries a hostname, user name, local path, kernel release, distribution string or memory size.
   `fp_export.py` validates `--host-label` as `fp_sweep.py` does. Known gap for you to judge: `cap.bytes` is
   `min(8 GiB, 0.6 x physical memory)`, so on the two hosts under 13.3 GB it implies the memory size. Falsifier: any
   such string or value in `hosts/*.jsonl` or `host-records.json`, or a label path that skips validation.
7. The README's "not run" entries are accurate: Windows `fp_export.py` (the producer imports `fcntl` through
   `scripts/qd_platform.py`), the M1 npz comparison receipt, the turion-linux host numpy 2.5.4 run, and a Windows rerun after
   the QuadBLAS probe. Falsifier: a README sentence that states one of these as measured.

## Questions to answer

- Which claim above fails, and where (file and line, or file and row line number)?
- Does any README sentence in the two sections still exceed what the rows or retained records support?
- Defects in `fp_host.py`, `fp_sweep.py` or `fp_export.py`: wrong skip logic, a probe that misreports, an unvalidated
  input, a row field the code writes that the README does not describe.
- Conjecture where nothing is posited: what else do the rows show about BLAS kernel selection (the `host.blas`
  `architecture` field against the float64 scores), with its falsifier.

## Report format

Rank findings by consequence. Tie every claim to a file:line, a row (`file`, `line` from `rows-summary.tsv`), or a
function name, and mark it proved, computed, measured or hypothesis. State what you could not check and why. Open
with the single most consequential finding. Print the report on standard output and write nothing else.
