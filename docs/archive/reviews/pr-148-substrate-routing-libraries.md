# Review: PR #148 kaggle/substrate-routing-libraries (head 2aa0559, local f930a62)

Scope: `git diff kaggle/ghost-error-scale...kaggle/substrate-routing-libraries`,
121 files, +20246/-2419, 65 commits. Read-only review; every probe ran in a
scratch clone or archive of f930a62 (`.../scratchpad/clone`, `.../head`), never
in a worktree.

Verdict: not mergeable as pushed. One CI break is this PR's own (sources-123/124,
root-relative links in the recaptured Kaggle site pages; f930a62 does not fix it),
one is inherited from #147 (core-339). Three Codex threads are all reachable and
all cheap. The larger debt is stale Kaggle-status text across the quantum-tools
manual (the qasm3 thread is one instance of about ten) and TPU/crossover claims
that cite runs the tree does not retain.

## 1. CI on head 2aa0559

Check runs (REST): shards 0, 2, 3, 5 green; shard 1 fails core-339 and
sources-124; shard 4 fails sources-123.

- **sources-123 / sources-124** (`docs/verify_sources.py`, link loop at line
  734-742). Introduced by 90f9585 "capture_kaggle_docs: retain kaggle.com/docs
  as Kaggle's own Markdown source": the `.md` source of each page carries
  root-relative links that resolve against https://www.kaggle.com/, which the
  capture docstring itself states. Base (kaggle/ghost-error-scale) and
  origin/main have zero broken links by the same regex. `verify_sources.py`
  stops at the first hit (CI hit api.md, a local rglob order hit mcp.md); the
  full set, enumerated with the same regex:

  | File | Target |
  | --- | --- |
  | docs/notes/kaggle/site/api.md (3x, lines 68, 164, 360) | `/settings` |
  | docs/notes/kaggle/site/mcp.md (line 96) | `/settings` |
  | docs/notes/kaggle/site/notebooks.md (line 125) | `scheduling-notebooks` (bare relative, no slash) |
  | docs/notes/kaggle/site/notebooks.md | `/static/images/docs/notebooks/kaggle-jupyter-server-panel.png` |
  | docs/notes/kaggle/site/notebooks.md | `/static/images/docs/notebooks/colab-connect-to-local-runtime.png` |
  | docs/notes/kaggle/site/notebooks.md | `/static/images/docs/notebooks/colab-backend-url.png` |
  | docs/notes/kaggle/site/organizations.md (2x) | `/groups` |
  | docs/notes/kaggle/site/organizations.md | `/model-gating-json-schema` |
  | docs/notes/kaggle/site/organizations.md (line 126) | `/settings` |

  13 links in 4 files, all inside the verbatim capture. No authored note is
  broken.

  **f930a62 does not fix it**: it touches only `docs/notes/kaggle/tpu-research.md`
  (+102). Reproduced: `python3 -W error docs/verify_sources.py` on f930a62 fails
  with the same ValueError.

  **Fix** (verified): the bytes are sha256-bound by `site/MANIFEST.json` and
  core-283, so rewriting links breaks the verbatim capture. Exempt the capture
  directory in the link loop the way `local_source_cache` is exempt:

  ```python
  # docs/verify_sources.py, line 736
  for note in library.rglob("*.md"):
      if library / "local_source_cache" in note.parents or library / "notes/kaggle/site" in note.parents:
          continue
  ```

  With that one line, on f930a62: `verify_sources.py` passes ("... and 1678 local
  links"), `docs/check_verify_sources.py` passes (120 tests), and the three
  lint gates on that file (gates.json `ruff check --no-cache`, `ruff format
  --check --no-cache`, `MYPYPATH=docs mypy --explicit-package-bases`) pass on the
  patched file as written above (ruff 0.14.11 reports it already formatted). A comment on the
  exemption should name the mechanism: the pages are kaggle.com's own Markdown,
  bound by MANIFEST.json, whose links resolve against https://www.kaggle.com/.
  (A narrower rule, skipping only `/`-prefixed targets, leaves the bare
  `scheduling-notebooks` link failing.) `cli/` links all resolve and need no
  exemption. Effort: 10 min.

- **core-339** (`scripts/ghost_error_scale.py --check`): "results/live/
  2026-10-11T152922.787095Z: docs/evidence/calibration/history/ibm_kingston/
  20261011T0757410700.json diagnostics differ". Reproduced on a `git archive` of
  kaggle/ghost-error-scale (1a099fe) alone, so it belongs to #147. Note 1a099fe
  has no check runs on GitHub (only an earlier `pull_request` run, ae4502d,
  green), so #147's head has not been through CI either.

- Locally re-run on f930a62 (host ruff 0.14.11, mypy 1.19.1 = CI pins), all
  green: core-001, core-002, core-250, core-253, core-280 (kaggle_run
  self-test), core-283, core-290 (`kaggle_run.py verify`), core-335, core-336,
  sources-216/217, sources-247/248/249/250. core-039 (mypy) fails locally on
  host-environment noise only (missing types-requests stubs, cd_phase_degree
  `Table?`); it is green on CI.
- `docs/notes/packages/manual/checks/run_examples.py --check` (host-only, not a
  gate): 66 examples run, 0 differ. Every example exits 0 (probed with a copy
  that appends the exit status).

## 2. Codex threads (verified against source)

### 4300637484 scripts/jax_bridge_sweep.py:115 "Reject JAX sweeps that fail Aer parity" -- reachable, fix

Lines 111-126: `parity = max(parity, ...)` is computed, then the replica's
distances are appended to `rows` unconditionally. The module docstring (lines
15-18) says "Before its distances count, every replica's factor-1 program is
compared with Aer's own density matrix", so the code does not do what the
interface promises. Reachable through the documented CLI (`--device tpu|gpu|cpu`):
a TPU's complex64 HIGHEST-precision path is exactly the case where a
discrepancy would appear and be averaged into `mean_tvd`.

Measured on the build host (JAX CPU, Kingston snapshot, `substrate_crossover`
chain circuits): numpy complex128 `evolve_numpy` vs Aer 1.1e-16 / 1.9e-10 /
4.3e-10 at 2/4/6 qubits (56/120/184 ops); JAX complex64 vs Aer 1.1e-7 / 9.3e-8 /
4.8e-8. A tolerance of 1e-5 gives two orders of headroom over complex64 and
still catches an export or contraction-order bug. This is an inference, rated
medium: those probe circuits carry no delay, so `export`'s thermal-relaxation
pass (jax_bridge.py lines 95-97) did not run, the probe used chain circuits
rather than the retained ghost replicas the sweep reads, and JAX ran on CPU,
not TPU. One delay-bearing retained replica through `export` plus
`aer_probabilities`, and the first TPU result, would confirm or move it.

Exact fix:

```python
# complex64 storage with Precision.HIGHEST contractions; Aer evolves in complex128.
PARITY_TOLERANCE = 1e-5
...
            gap = float(np.max(np.abs(jax_bridge.probabilities(programs[base], diagonals[base]) - reference)))
            parity = max(parity, gap)
            seconds["parity"] += time.perf_counter() - start
            if gap > PARITY_TOLERANCE:
                skipped[f"{m}#{k}"] = f"factor-1 probabilities differ from Aer by {gap:.3g} > {PARITY_TOLERANCE:g}"
                continue
```

and have `main()` return 1 when any run's `skipped_replicas` carries a parity
reason (or any `max_abs_probability_minus_aer > PARITY_TOLERANCE`), so a kernel
exit code records the failure. Record `parity_tolerance` in the output header. The measured 1e-7 figures
belong in the commit body, not the source comment.
Effort: 20 min. Reply `Fixed in <commit>`.

### 4300637493 docs/notes/packages/manual/checks/run_examples.py:49 "Fail examples whose subprocess exits unsuccessfully" -- reachable, fix

`run()` (lines 43-51) uses `check=False` and returns only `completed.stdout`;
`returncode` is discarded. `--check` is the documented interface
(manual/README.md line 39). Every retained example catches its own exception and
prints it, and all 66 exit 0 today, so treating a nonzero status as a failure
breaks nothing. Fix: return `(output, completed.returncode)` from `run`, and in
`main` count `returncode != 0` as a failure (print `exited N`), in `--write` mode
too, so a crashing example cannot be written back as its own expected output.
Alternative with the same effect and a self-describing record: append
`[exit N]\n` to the output when N != 0. Effort: 15 min. Reply `Fixed in <commit>`.

### 4300637500 docs/notes/quantum-tools/qiskit-qasm3-import.md:21 "stale absence claim vs PIN_GROUPS" -- reachable, fix (and wider than the thread)

`PIN_GROUPS["quantum-tools"]` (scripts/kaggle_run.py lines 104-109, commit
3a61aec) pins `qiskit-qasm3-import==0.6.0`, `openqasm3==1.0.1`,
`antlr4-python3-runtime==4.13.2`. These guides are bundled into every kernel
(`KERNEL_DOCS`), so the stale text is read inside kernels. Every stale statement
of the same class:

| File:line | Stale text | Correct state |
| --- | --- | --- |
| quantum-tools/qiskit-qasm3-import.md:21 | not installed by KERNEL_PINS or the group | pinned in `quantum-tools` (3 pins) |
| quantum-tools/README.md:174-176 | the group does not install it | pinned |
| qiskit-ecosystem.md:25-32 (item 1) | samplomatic, ibm-quantum-schemas, qiskit-mitigation unpinned; kernel resolves schemas 0.13 | all three pinned at host versions |
| qiskit-ecosystem.md:33-35 (item 2) | qasm3-import and openqasm3 in no Kaggle pin | pinned |
| qiskit-ecosystem.md:36-41 (item 3) | "the four substrate-crossover submissions that declare quantum-tools carry no retained output" | 163552Z (committed) declares the group and retains `pin_groups.json` with 12 installed versions; the four it means are untracked dirs |
| qiskit-ecosystem.md:85-86, 173-174 | Kaggle column `absent`; "add Kaggle pin" | pinned |
| quantum-tools/samplomatic.md:22, ibm-quantum-schemas.md:18 | "not pinned by name" | pinned by name |
| quantum-tools/qiskit-addon-utils.md:19, qiskit-mitigation.md:18 | "not installed by the repository" | pinned in the group |
| quantum-tools/stim.md:24 | "no kernel with the group has been run yet" | 163552Z installed stim 1.16.0 on a CPU kernel |
| mthree, galois, pyzx, lmfit, quimb, qiskit-experiments, qiskit-ibm-runtime .md rows; README "No Kaggle kernel has exercised the `quantum-tools` group" | "unmeasured on a kernel" | the 12-member group installed at its pins on CPU kernel 163552Z (`pin_groups.json`); the 8 pins added since (runtime deps, qasm3 trio, addon-utils, mitigation) have not run |
| quantum-tools/qiskit-aer.md:21 | `qiskit-aer-gpu-cu11` in KERNEL_PINS | CPU and TPU kernels take `CPU_KERNEL_PINS` (`qiskit-aer==0.17.2`) |
| quantum-tools/README.md:56 | "Kaggle GPU kernel: `push` default `NvidiaTeslaT4`" | `DEFAULT_MACHINE = "cpu"`; a GPU needs `--machine NvidiaTeslaT4` |

Fix: one docs commit rewriting these rows against PIN_GROUPS and the retained
163552Z `pin_groups.json`. Effort: 45 min. A gate that renders each note's Kaggle
row from PIN_GROUPS (the way core-347 renders the QI table) would stop the drift;
should-fix, 1-2 h.

## 3. Scripts

### scripts/kaggle_run.py (+388)

- `PIN_GROUPS` / `--with GROUP`: pins match the AGENTS.md host table. RUNNER
  writes a constraints file holding the kernel pins plus the image's numpy,
  scipy, jax, jaxlib, libtpu, then re-checks every pin with
  `importlib.metadata.version` and stops on a mismatch. Correct and
  deterministic. `pin_groups` is recorded in kernel_job.json and submission.json;
  kernel_main writes `pin_groups.json`. The 20-member group has never run on a
  kernel (the retained 163552Z ran the 12-member version at 85e190c); a numba
  0.68 / numpy-2.1.3-image or antlr conflict would surface only at first push.
- `kernel_pins`: CPU build on cpu and `Tpu*`. Correct.
- TPU notebook path: no `docker_image`, `docker_image_pinning_type: latest`, no
  notebook `kaggle` block; self-test asserts all of it.
- `require_no_live_version` / `require_no_live_shard`: refuse an accelerator
  push or accelerator shard run while any version is RUNNING/QUEUED/NEW_SCRIPT;
  a failed listing refuses. Self-tested with stubs (`_push_guard_self_test`).
  Consequence: every GPU/TPU push now needs headless Firefox, selenium,
  geckodriver and a signed-in Kaggle cookie on the host; documented in
  workflow.md. Boundary.
- `download_version` (collect): fixes the CLI's latest-version-only
  `kernels output`; path-escape check present. Good.
- **Size guard (should-fix).** `KERNEL_DOCS` bundles ~1.17 MB of Markdown
  (303 KB gzip) into every push. The committed T4 run 212614Z has a 1,030,695-byte
  `run.py`, above `KERNEL_SOURCE_LIMIT = 1_000_000`, whose comment says 706,414
  was accepted and 1,662,849 refused. `push()` applies no size check (only
  `shards` does, line 931), and the docs grew 149 KB raw since 0e16503, so a
  push at head is larger again. Apply the guard in `push`/`build_kernel`, update
  the comment's evidence to the accepted 1,030,695, and consider making
  `KERNEL_DOCS` opt-in (`--with-docs`) or compressing at zip level 9. 30 min.
- Docstring routing rule (12 static / 8 dynamic) matches substrates.md.
- Libraries.md says kaggle_run "runs every Kaggle job through the CLI"; collect
  and `latest_state` now go through kagglesdk. Minor stale line.

### scripts/kaggle_sessions.py (+288, new)

- `versions`/`quota`/`cancel`/`cancel-running`, `--self-test` is gate core-336.
  Copies cookie/cert/key stores into a TemporaryDirectory, deletes it, prints no
  cookie. `time.sleep(6)` before the fetch is a fixed wait (fragile on a slow
  page). `LIVE` omits any cancel-pending state the server may report; unknown
  whether one exists (boundary). The parser is a deep scan (`_collect`) that
  takes the first `versionNumber` per item, which holds for the observed payload
  only.
- `HEADERS_HELPER = ~/.config/shell/kaggle-mcp-headers.sh` binds the script to
  one host's shell layout; boundary (build-host-only tool, documented).
- The account name `probablyeric` appears in docstrings; origin/main already
  carries it in 214 files, so it is the repository's convention.

### scripts/substrate_crossover.py (+188, new)

- Deterministic workload (seeded rng per width, DFS chain on sorted couplers,
  `seed_simulator`). Serial timing loop is correct for a benchmark: pooling would
  perturb the timing; the docstring should say so, because AGENTS.md calls a
  serial loop over independent items a defect.
- `machine.logical_cpus` uses `os.cpu_count()`, not
  `parallel.available_cpus()`; the noise simulator sets no
  `max_parallel_threads` (Aer's default takes all host cores, which equals the
  4-CPU affinity on Kaggle). Minor.
- 202351Z failed with FileNotFoundError on ibm_kingston.json (no `--include`);
  the docstring now prescribes `--include`, so the CLI surface is right. The
  script could fail fast with a message naming `--include`.
- No gate: the 12/8 routing thresholds in AGENTS.md, kaggle_kernel/AGENTS.md and
  kaggle_run.py rest on two retained JSON files that nothing re-derives. AGENTS.md
  ("measured extraction/render checks join ci/gates.json") asks for a gate that
  recomputes the substrates.md table and the ratios from the two
  `substrate_crossover.json` files. Should-fix, 1 h.

### scripts/tpu_probe.py (+184, new)

- CX encoding (`control + 2*target`, qargs (0,2)) and the little-endian
  embedding are correct; reference is complex128.
- **Should-fix**: the hardware block, which tpu-research.md section 6 step 3
  calls "the kernel's first output" and the basis for cancelling a CPU session,
  is printed and written only at the very end (lines 177-179). If
  `jax.devices()` or the replay hangs or raises on a TPU VM (libtpu init, chips
  still claimed), the session produces nothing. Write and print `hardware` right
  after `hardware()`, then rewrite the file at the end. Also print on the
  ImportError path. 10 min.
- No tolerance on `max_abs_error_vs_numpy_complex128` (recorded only); acceptable
  for a probe.

### scripts/jax_bridge_sweep.py (+183) and gororoba_quantum/jax_bridge.py (+245), new

- Thread 4300637484 above.
- Parallelism rule: export plus the Aer parity per replica are CPU-bound
  independent items in a serial loop; `aer_probabilities` builds a new
  `noise_simulator` per replica (hoist per snapshot). Pool export+parity through
  `parallel.ordered_map` and keep only the batched JAX replay serial. 45 min.
- No behavioral gate for `jax_bridge.py`: only ruff/mypy (core-001/002/039). A
  CPU contract in CI (numpy `evolve_numpy` vs Aer on two small ISA circuits from
  the retained snapshot, tolerance 1e-9 as measured above; plus
  `stack_programs` padding invariance and `UnsupportedCircuit` on reset /
  if_else / post-measurement gates) is what AGENTS.md's "a new module joins the
  gate list" asks for. No sweep output is retained or cited anywhere. 1 h.

### scripts/algebra_package_tables.py (+280)

- 17 RELEASES, 3 BUILD_RECIPES, 4 RUNTIME_PINS, matching kaggle_kernel/AGENTS.md
  ("seventeen", "sixteen with --no-deps", numpy-quaternion as wheel). Wheel
  digests via `archive_digests`. Kingdon bitmask indexing and galgebra
  `g1 ^ g2` give the (1, e1, e2, e12) order the RELATIONS claim. sources-216/217
  green. `REPORTED_PACKAGES` lists nine algebra distributions, matching the
  "nine of the seventeen" claim.

### docs/notes/packages/manual/checks/*.py

- `algebra_interplay.py`, `albert_algebra.py`, `run_examples.py` all use
  `parallel.ordered_map`; gates sources-247..250 green. `run_examples.py` is
  host-only (needs the Arch stack), so it is not a gate: boundary, stated in its
  docstring.

### kaggle_kernel/kernel_main.py

- Prints the bundled guide list, writes `pin_groups.json`. Fine.

## 4. Docs

- **Voice/ASCII**: no non-ASCII bytes, em dashes or curly quotes in any authored
  added/modified file (site/ captures and results excluded); British spellings
  absent (`normalised` in pyquaternion.md is the upstream API name). Clean.
- **substrates.md "CPU against T4"**: every ratio checks against the two
  retained `substrate_crossover.json` (2.80, 12.77, 17.65; dynamic 2.86, 28.2).
  Two precision fixes: (a) "both qiskit 2.5.2 and qiskit-aer 0.17.2": both runs
  installed `qiskit-aer-gpu-cu11==0.17.2` (the CPU run predates
  `CPU_KERNEL_PINS`, commit 85e190c); say so. (b) T4 dynamic 8 qubits (19.4 s)
  ran faster than 6 (24.3 s), a non-monotone point from one best-of-2
  measurement that the 8-qubit dynamic threshold rests on; name it. The CPU
  machine (Intel Xeon 2.20) differs from the CPU-probe machine (AMD EPYC 7B12);
  Kaggle's CPU pool is heterogeneous, so the threshold is one draw.
- **tpu-research.md**:
  - Section 2 rows for `gororoba-tpu-probe` v1/v2, `-latest`, `-cli` and both
    `gororoba-tpu-mcp-probe` versions cite session software (Python, jax,
    glibc, libtpu, cores) from outputs the tree does not retain: 163111Z (v1)
    and 170035Z (v2) are untracked submission-only dirs, the MCP/editor routes
    have no run dir. Collect v1/v2 (`kaggle_run.py collect`, which now fetches by
    version label) and commit them, or mark the rows as unretained
    observations. Should-fix.
  - "After verification" table: status `QUEUED ... for at least 1 h 40 min`,
    while f930a62's "Queue behavior" says 5.5 h. Update the row to the latest
    measured duration. 5 min.
  - Summary still says "No TPU VM has executed yet": true as of the notes;
    `gororoba-tpu-probe-verified` (200737Z, session 359130889) is the pending
    confirmation.
- **AGENTS.md and kaggle_kernel/AGENTS.md** routing text (12 static / 8
  dynamic) is consistent with substrates.md inside this branch. Against
  origin/main: main's root AGENTS.md "Simulation on Kaggle" section (line 374)
  still says CPU below 11 qubits and GPU for 11 to 14, so the merge to main must
  rewrite it to 12/8 or the two sections contradict. `git merge-tree` (trivial
  mode, no writes) against origin/main shows 10 conflict hunks: AGENTS.md 1,
  ci/gates.json 4, docs/notes/kaggle/substrates.md 1, scripts/kaggle_run.py 4.
- AGENTS sections carried in three files stay byte-identical (core-250 green).
- libraries.md: "kaggle_run.py runs every Kaggle job through the CLI" is
  partly stale (kagglesdk for collect and status guard).

## 5. Dirty worktree

`docs/notes/kaggle/tpu-research.md` is no longer modified: f930a62 committed it.
Eight untracked dirs, none cited by any doc, none with collect.json except one:

| Dir | Kernel / version | Files | State | Action |
| --- | --- | --- | --- | --- |
| 160858Z substrate-crossover-t4 | v1 | submission + kernel only | never collected; superseded | collect if it ran (GPU billed), else trash-put; see the quota note below |
| 160901Z substrate-crossover-cpu | v1 | submission + kernel only | superseded by committed 163552Z (v2) | trash-put |
| 162059Z substrate-crossover-t4 | v2 | submission + kernel only | superseded | as 160858Z |
| 162124Z substrate-crossover-t4 | v3 | submission + kernel only | superseded | as 160858Z |
| 163111Z tpu-probe | v1, TpuV6E8 | submission + kernel only | cited indirectly by tpu-research section 2 | collect, commit |
| 170035Z tpu-probe | v2, TpuV5E8, image pin | submission + kernel + run.ipynb | cited indirectly by tpu-research sections 2, 3 | collect, commit |
| 200737Z tpu-probe-verified | v1, verified account | submission + kernel + run.ipynb | QUEUED on Kaggle | collect after it runs, then commit; it is the hardware-marker confirmation |
| 202351Z substrate-crossover-t4-gpu | v1 | collected: environment.json, exit.json `{"returncode": 1}`, hypercomplex.json, stdout/stderr | failed: ibm_kingston.json not bundled | uncited; superseded by 212614Z (v2 of the same slug); trash-put, or commit with a one-line note if failed runs are retained |

Live-session check: Kaggle MCP `get_accelerator_quota` read during this review
reports GPU `time_used` 0 s and `time_reserved` 0 s (refresh
2026-10-24T00:00Z, so the weekly reset has passed), and TPU 0/0. Nothing GPU is
billing now, so no t4 v1-v3 session is still running. Before choosing collect
or trash-put, run `"$PYTHON" scripts/kaggle_sessions.py versions
probablyeric/gororoba-substrate-crossover-t4` to see whether v1-v3 completed
with output worth retaining.

Every committed results/kaggle run dir carries collect.json, so a
submission-only dir does not match the convention. Where: the collected TPU
probes belong on this branch (their claims are here); commit 163111Z/170035Z in
the same change that rewrites tpu-research section 2 to cite them. The
four crossover t4/cpu v1-v3 pushes are also the origin of qiskit-ecosystem.md
item 3's "four submissions ... no retained output"; once they leave the tree,
that sentence must go too.

## 6. Ranked list

Must-fix before merge:
1. sources-123/124: exempt `docs/notes/kaggle/site/` in verify_sources.py's link
   loop (verified fix). 10 min.
2. core-339: fixed on #147, then merge #147 into this branch. Owner: #147.
3. Thread 4300637484: parity tolerance gate in jax_bridge_sweep.py. 20 min.
4. Thread 4300637493: nonzero exit fails run_examples. 15 min.
5. Thread 4300637500 plus every stale Kaggle-status row in section 2's table
   (about 15 statements across 12 files). 45 min.
6. Reconcile with origin/main when #148 retargets: 10 conflict hunks, and
   main's "Simulation on Kaggle" 11-qubit text to 12/8. 1 h.

Should-fix:
7. Size guard on `push` (run.py 1,030,695 B already above the 1,000,000 limit
   the code states); update the limit comment. 30 min.
8. tpu_probe.py writes the hardware block first. 10 min.
9. Collect and commit 163111Z, 170035Z (and 200737Z when it runs); fix the
   "1 h 40 min" row. 30 min plus queue time.
10. CPU contract gate for jax_bridge.py. 1 h.
11. Gate re-deriving substrates.md crossover table and the 12/8 thresholds from
    the retained JSON. 1 h.
12. jax_bridge_sweep export+parity through parallel.ordered_map; hoist the
    per-snapshot simulator. 45 min.
13. substrates.md: name the gpu-cu11 package and the non-monotone dynamic point.
    10 min.
14. Kaggle-row render gate from PIN_GROUPS. 1-2 h.

Boundary (reply, no push):
- kaggle_sessions.py: fixed 6 s page wait, LIVE status set, home-relative
  headers helper, Firefox requirement for accelerator pushes.
- run_examples.py is host-only and outside ci/gates.json by design.
- substrate_crossover serial loop (timing benchmark).
- Account name in docstrings (repository convention on main).

## 7. docs/* worktrees

All five branches are ancestors of both local kaggle/substrate-routing-libraries
(f930a62) and the pushed head 2aa0559 (`git merge-base --is-ancestor`, all yes);
all five worktrees are clean (0 porcelain lines); none has a remote branch
(`gh api repos/Oichkatzelesfrettschen/gororoba-quantum/branches --paginate`
lists no `docs/` branch).

| Branch | Head | Contained |
| --- | --- | --- |
| docs/algebra-package-manual | 89de898 | yes |
| docs/exotic-algebra-survey | b31f039 | yes |
| docs/qiskit-ecosystem-audit | 0c96d45 | yes |
| docs/quantum-tools-manual | bbe388e | yes |
| docs/kaggle-interfaces | 45c8f5c | yes |

Yes, all five can be deleted once #148 merges: their whole history is on the
pushed head, so nothing needs an `archive/` push. After the merge (and the
primary checkout's pull), remove each with `git worktree remove` (no
`--force`) and `git branch -d`; before the merge `git branch -d` refuses from
main, because the branches are not yet merged into its HEAD.

## 8. Not run

- Claim-by-claim check of docs/notes/kaggle/interfaces.md (605 lines), most of
  workflow.md, hypercomplex-stack.md and docs/notes/kaggle/README.md: not run;
  only targeted greps for CLI-surface staleness (`--with`, `--timeout`,
  `kernels output`, default machine), which found nothing stale there.
- docs/notes/packages/adjacent-algebras.md, interplay.md, candidates.md and the
  short per-package notes, and docs/notes/qiskit-ecosystem-install-plan.md: not
  claim-checked; the manual pages were checked only through run_examples
  (66/66) and gates sources-247..250.
- docs/evidence/algebra_packages/tables.json: not regenerated with `--extract`
  on the host; checked only through sources-216/217 (`--check`).
- kaggle_sessions.py live paths (`versions`, `quota`, `cancel`,
  `cancel-running`): not run; they need Firefox with a signed-in session and a
  token, and `cancel` writes. Only `--self-test` ran.
- The 20-pin `quantum-tools` group: never installed on any kernel; no push made
  (review is read-only).
- The full pr tier: not run; only the 19 gates touching this PR's files.
- Mechanical voice checks covered ASCII, curly quotes, em dashes and British
  spellings; prose voice of the 60+ new notes was sampled, not read in full.
