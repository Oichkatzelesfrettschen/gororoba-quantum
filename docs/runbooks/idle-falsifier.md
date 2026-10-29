# Local idle falsifier: resumable parts and hosted-runner runs

`scripts/local_idle_falsifier.py` computes, for every audited run with a dynamic member, two exact laws per replica
and their TV distances to hardware ([evidence bundle](../evidence/local_idle_padding/README.md)). A four-qubit
replica's exact law holds several GB, so the sweep runs per run, and every route below writes one part per run
that the build host assembles into `result.json`.

## Numeric environment

`ci/run_gates.py` reruns retained summaries under `OPENBLAS_CORETYPE=Haswell` and
`NPY_DISABLE_CPU_FEATURES="X86_V4 AVX512_ICL AVX512_SPR"`, so every route that writes a part sets the same two
variables and `OPENBLAS_NUM_THREADS=1`, as `ci.yml` does.

## One host, resumable

```sh
export OPENBLAS_NUM_THREADS=1 OPENBLAS_CORETYPE=Haswell NPY_DISABLE_CPU_FEATURES="X86_V4 AVX512_ICL AVX512_SPR"
GOROROBA_WORKERS=2 systemd-run --user --scope -q --unit=idle-falsifier -p MemoryMax=14G -p MemorySwapMax=2G \
  "$PYTHON" -B scripts/local_idle_falsifier.py --runs all --parts PARTS --out OUT
```

`--parts PARTS` writes each run's full summary to `PARTS/RUN.json` as the run finishes, with the package versions
and the sha256 of every module that decides a summary (`PART_SOURCES`). A rerun reuses a part whose identity
matches and evaluates the rest, so a memory-cgroup kill costs only the run in progress. Measured on the 62 GiB build
host: two workers on the four-qubit segmented spectator run `2026-10-21T064222.721454Z` exceeded a 14 GiB cap plus
2 GiB of swap, while the 30 runs before it fit.

## Hosted runners

[.github/workflows/idle-falsifier.yml](../../.github/workflows/idle-falsifier.yml) runs one matrix job per audited
run (up to 20 at once, 355 minutes each) and uploads `PARTS/RUN.json` beside the runner's `lscpu` and
`/usr/bin/time -v` output. A push to a `compute/idle-falsifier/` branch runs the workflow file of the pushed commit:

```sh
git push origin HEAD:compute/idle-falsifier/SLUG
gh run download RUN_ID --dir DOWNLOADS
mkdir -p PARTS && cp DOWNLOADS/idle-part-*/*.json PARTS/
"$PYTHON" -B scripts/local_idle_falsifier.py --runs all --parts PARTS --parts-only \
  --out docs/evidence/local_idle_padding/result.json
```

`--parts-only` refuses to evaluate: a missing part, or one whose versions or sources differ from the checkout,
fails the assembly instead of starting a multi-hour local run. The repository is public, so the workflow's logs and
artifacts are public; it reads only files the pushed ref holds.
