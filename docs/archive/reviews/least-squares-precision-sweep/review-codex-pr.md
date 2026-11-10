# Adversarial review: pull request 808 portable least-squares sweep

Scope: `origin/main...5ba6b3791`, the pull-request body, three fix commits, three Python programs, README, and all
439 retained host rows. Field: numerical evidence, portable Python execution, public-record privacy, and CI gates.

## Ranked findings

1. **SERIOUS -- [proved] The required hosted lint and type checks never inspect the changed Python programs.**
   `ci/pr_checks.sh:54-75` limits both lanes to fixed code directories and fixed extra-file lists; none of
   `fp_host.py`, `fp_sweep.py`, or `fp_export.py` appears there. `git grep` also finds no test reference to
   `fp_host` or `fp_sweep`. The four required PR jobs can therefore pass while syntax, typing, privacy scrubbing,
   label validation, capability-to-grid mapping, or JSON-record behavior in the new programs regresses. The PR
   body's one-off checks do not provide a merge gate. Add all three files to `checked_files` and `typed_files`, and
   add bounded fixture tests for host-record redaction, label rejection, and QuadBLAS skip selection.

2. **SERIOUS -- [proved] The claimed OS-family-only public profile still publishes exact product releases.**
   `fp_host.py:373-382` writes `host.os.mac_ver` and `host.os.release`; `m1-macos-full.jsonl:1` contains the macOS product
   version, and `zen4-windows-full.jsonl:1` contains the Windows release. `README.md:194-199`, `fp_host.py:3-6`, the PR body, and the owner-bound
   reconciliation describe the allowed field as OS family, not product version. The scan did prove absence of a
   hostname, user name, local path, kernel release, distribution string, and recorded physical-memory field; the
   owner accepted `cap.bytes`. Drop `mac_ver` and `release`, or obtain an explicit owner ruling and state OS product
   version rather than OS family.

3. **SLOPPY -- [computed] The README reintroduces the portability overstatement that fix `5ba6b3791` claims to
   remove.** `README.md:247-249` says every host ran in a venv on pinned wheels including numpy-quaddtype 1.0.0.
   `oci-a1-neoverse-n1-full.jsonl:1` records `host.packages.numpy-quaddtype=null`, and `README.md:284-285` agrees that
   the package was absent. `README.md:241-243` also describes the build host's numpy-quaddtype as a source build,
   not a wheel, while no row proves venv use or installation source. State the three common pinned packages, then
   describe numpy-quaddtype per host; omit the unretained venv and wheel-origin claims.

## Claim verdicts

- **Claim 1 -- [proved and computed] PARTIAL.** Fixes for the M1 digest cohort, cap prose, QuadBLAS error handling,
  missing M1 receipt, and unretained turion-linux probe reproduce. The host-boundary fix remains incomplete because exact
  OS product releases survive, and the portability fix reintroduces a universal numpy-quaddtype wheel claim.
- **Claim 2 -- [computed] FALSE.** Recursive scanning found zero hostname, user-name, local-path, old kernel,
  distribution, or physical-memory fields, but exact macOS and Windows releases exceed the stated OS-family profile.
- **Claim 3 -- [computed] FALSE.** The row-derived counts, digest cohorts, equality counts, ulp ranges, and timings
  reproduce. The pinned-wheel sentence is contradicted by the rows. The M1 receipt, turion-linux 2.5.4 probe, Windows
  rerun, and per-child cgroup readback are disclosed as unrun or absent at the strength used.
- **Claim 4 -- [proved and computed] TRUE.** `fp_backends.py:233-239` and `fp_backends.py:274-284` are the only
  quaddtype solver paths and both call `set_num_threads`. `fp_sweep.py:78-83` assigns `quadblas` to all 12 full-grid
  quaddtype configurations at four CPUs and to no other configuration; a disabled status skips exactly those 12.

## Checks

- **[computed]** All 439 JSON rows parse. Full rows/skips/errors are `32/0/0`, `74/0/0`, `60/16/0`, `32/14/0`,
  `88/22/12`, and `88/0/0`; thread and x87 admission violations are empty.
- **[computed]** `git diff --check` and 1,083 Markdown links pass. Installed ruff 0.17.3 format/check and mypy 2.4.0
  pass on the three programs. Pinned ruff 0.17.4 and mypy 2.4.1 are not run because the sandbox cannot resolve PyPI.
- **[proved]** No committed test covers the new host probe, sweep grid, exporter validation, or QuadBLAS regression.

## Verdict

The retained numerical evidence is internally coherent and the QuadBLAS dependency mapping is exact. Pull request
808 is not ready for hosted review: required CI omits every changed Python program, and the public-profile and pinned-
wheel prose still exceed the retained evidence. Adding bounded CI coverage and correcting the two claims would leave
the seven-finding reconciliation defensible under the owner's `cap.bytes` ruling.
