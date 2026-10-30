Artifact: Python/Singular exact-algebra tooling, evidence record, and supporting prose. Full requested surface reviewed read-only.

## Correctness defects

- **FATAL — `dense-family` certifies equality from metadata alone.** [fiber_certificates.py:167](~/worktrees/IBMQuantum/a5-kernel-attachments/docs/evidence/a5-kernel-attachments/fiber_certificates.py:167) returns `support-equal` when callers supply matching dimension integers and any nonempty `argument`. Lines 190–207 require neither a sampled point nor a verified dimension artifact. An empty point list can therefore receive `support-equal`; [test_a5_fiber_cone_driver.py:48](~/worktrees/IBMQuantum/a5-kernel-attachments/tests/test_a5_fiber_cone_driver.py:48) reinforces the metadata-only acceptance. Require a digest-bound, verified per-component dimension certificate and evidenced contained loci.

- **SOUND — finite-field \(h_d\) is exact on the stated surface.** [fiber_cone_driver.py:225](~/worktrees/IBMQuantum/a5-kernel-attachments/docs/evidence/a5-kernel-attachments/fiber_cone_driver.py:225) selects quotient monomials, forms products spanning \(I^d\), and reduces them modulo \(\operatorname{std}(J+\mathfrak mP_d)\). Exact `nmod_mat` rank therefore computes \(\dim_{\mathbf F_p} I^d/\mathfrak mI^d\). [fiber_cone_driver.py:339](~/worktrees/IBMQuantum/a5-kernel-attachments/docs/evidence/a5-kernel-attachments/fiber_cone_driver.py:339) independently verifies every kernel-basis relation by exact membership.

- **SOUND — the candidate-ideal certificate remains conditional and defensible.** [fiber_certificates.py:97](~/worktrees/IBMQuantum/a5-kernel-attachments/docs/evidence/a5-kernel-attachments/fiber_certificates.py:97) checks the nonzerodivisor pivot, \(H\subseteq L\), \(L:g=L\), \(L\subseteq\ker\phi\), and fiber specialization equality. Line 16 correctly denies an unproved all-degree Hilbert conclusion.

## Process leaks and limit defects

- **SERIOUS — the claimed 16 GiB, one-worker envelope is unenforced.** [nullity16_rees_fibers.py:806](~/worktrees/IBMQuantum/a5-kernel-attachments/docs/evidence/a5-kernel-attachments/nullity16_rees_fibers.py:806) dispatches row analyses through `parallel.ordered_map(..., min_items=1)`. Four workers can launch four 16 GiB scopes concurrently. The producer neither forces one worker nor records the worker count at [nullity16_rees_fibers.py:848](~/worktrees/IBMQuantum/a5-kernel-attachments/docs/evidence/a5-kernel-attachments/nullity16_rees_fibers.py:848). Serialize analysis or record and document the aggregate resource contract.

- **SERIOUS — exceptional cleanup kills without reaping.** A SIGTERM-triggered `SystemExit`, `KeyboardInterrupt`, or other `communicate()` exception reaches [nullity16_rees_fibers.py:190](~/worktrees/IBMQuantum/a5-kernel-attachments/docs/evidence/a5-kernel-attachments/nullity16_rees_fibers.py:190), kills the process group, and unwinds without `wait()` or a second `communicate()`. The direct child can remain a zombie. Cleanup must always reap before re-raising.

- **SLOPPY — `killpg` races can mask the intended outcome.** [nullity16_rees_fibers.py:180](~/worktrees/IBMQuantum/a5-kernel-attachments/docs/evidence/a5-kernel-attachments/nullity16_rees_fibers.py:180) and line 193 allow `ProcessLookupError` if the child exits between the liveness check and signal. Catch that measured absence and still reap.

- **SLOPPY — the record misnames a cgroup memory ceiling as an address-space limit.** [nullity16_rees_fibers.py:851](~/worktrees/IBMQuantum/a5-kernel-attachments/docs/evidence/a5-kernel-attachments/nullity16_rees_fibers.py:851) records `singular_address_space_bytes`, while lines 157–165 apply `MemoryMax`, not `RLIMIT_AS`. Rename the field to describe cgroup memory accounting.

## Unsupported README or ledger claims

- **SERIOUS — the append-only ledger contradicts itself about the prior record.** [ledger.md:24](~/worktrees/IBMQuantum/a5-kernel-attachments/docs/evidence/a5-kernel-attachments/ledger.md:24) describes a retained 32003 record and two digests; [ledger.md:37](~/worktrees/IBMQuantum/a5-kernel-attachments/docs/evidence/a5-kernel-attachments/ledger.md:37) says that record was never retained and replaces the same path with 32009 bytes. Preserve the historical bytes under an immutable path or explicitly correct the earlier evidence status.

- **SERIOUS — resource measurements exceed the cited record.** [README.md:389](~/worktrees/IBMQuantum/a5-kernel-attachments/docs/evidence/a5-kernel-attachments/README.md:389) and [ledger.md:37](~/worktrees/IBMQuantum/a5-kernel-attachments/docs/evidence/a5-kernel-attachments/ledger.md:37) claim one-worker execution, 4 GiB trials, 2.5 GB resident usage, 83–227-second timings, and equivalence between `prlimit` and cgroups. The JSON records only a 16 GiB cgroup ceiling and 300-second timeout; it binds none of those additional observations. Retain a diagnostic receipt or remove/bound the claims.

- **SOUND —** the record supports eight completed fibers, ten timeouts at `modular_rees_fiber`, the listed ranks and fiber shapes, characteristic agreement, mutation degree change, `pass=false`, and the exclusions of real fibers and attaching maps.

## Repository-rule violations

- **SLOPPY — executable checks use prohibited `assert`.** [fiber_cone_driver.py:89](~/worktrees/IBMQuantum/a5-kernel-attachments/docs/evidence/a5-kernel-attachments/fiber_cone_driver.py:89), lines 217 and 300, plus [fiber_inputs.py:221](~/worktrees/IBMQuantum/a5-kernel-attachments/docs/evidence/a5-kernel-attachments/fiber_inputs.py:221), lines 225 and 240 violate the explicit “raise, never assert” rule. Line 240 lacks a preceding guard and changes failure behavior under `python -O`.

- **SLOPPY — source comments contain experimental chronology and deictic wording.** [nullity16_rees_fibers.py:59](~/worktrees/IBMQuantum/a5-kernel-attachments/docs/evidence/a5-kernel-attachments/nullity16_rees_fibers.py:59) embeds resource outcomes and says “that stage.” Measurements belong in evidence artifacts; mechanism comments must stand alone.

- Parallel-loop compliance: **none**. Independent row work uses `parallel.py`.
- QRNG/seed compliance: **none**. The changes introduce no randomness or seed.
- `git diff --check`: clean. No files were edited.

