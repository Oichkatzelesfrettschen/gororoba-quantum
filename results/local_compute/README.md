# Local compute qualification evidence

The bundle preserves a failed CPU branching qualification on FakeFez
circuits and separately records small CUDA capability probes. Every
benchmark run uses local simulation. The bundle establishes zero QPU
execution evidence and grants zero submission authorization.

[summary.json](summary.json) exposes the bounded results without expanding
the complete metadata. [manifest.json](manifest.json) records retained and
source hashes, lengths, evidence roles, and transformations. Gzip archives
preserve every source byte, with a fixed compression timestamp. The
[compute plan](../../gororoba_quantum/LOCAL_COMPUTE.md) connects these
observations to the implemented policy and remaining gates.

| Artifact | Role and status |
|---|---|
| `cpu_branching_inputs.qpy.gz` | Exact eighteen compiled circuit inputs |
| `cpu_branching_results.json.gz` | Initial checkpoint, intentionally interrupted during optional N=21 baseline2048; historical state stays `running` |
| `cpu_branching_qualification.json.gz` | Completed follow-up, state `failed`; paired counts, Aer metadata, comparisons, and noiseless-law checks |
| `cpu_branching_noise_semantic.json.gz` | Reconstructed UUID-free serialized FakeFez channels; legacy list-order digest |
| `cpu_branching_benchmark.py` | Historical benchmark generator; retained version includes the later semantic-noise digest correction |
| `cpu_branching_qualify.py` | Follow-up generator; records reconstruction and interruption boundaries |
| `cpu_branching_rca.py`, `cpu_branching_rca.json.gz` | Canonical-channel replay and completed fresh-instance non-reproduction across ten thread/batch cases |
| `cpu_branching_reuse_probe.py`, `cpu_branching_reuse_probe.json.gz` | Fifteen local replay cases: original simulator-reuse prefix and three fresh 32768-shot trials per family |
| `cpu_branching_reuse_analysis.py`, `cpu_branching_reuse_analysis.json.gz` | All-bin/contrast analysis that falsifies fresh-instance construction as a repair |
| `GPU_INVENTORY_OBSERVATIONS.json` | Transcription of command observations; loaded-library path reduced to basename |
| `verify_evidence.py` | Standard-library integrity and result-recomputation verifier |

The benchmark reports NumPy 2.5.4, Qiskit 2.5.2, Aer 0.17.2, and Runtime
0.50.0. The source HEAD appears in each raw report; dirty-source hashes are
absent. The HEAD alone therefore cannot establish a clean capture tree.
The historical scripts are source evidence, rather than an assertion that
a fresh execution produces byte-identical randomized results.

The completed paired 2048-shot folded run differs by `0.404296875` in one
`qpe_archived_s1` bin. Its simultaneous radius is
`0.14211860914345206`; the compatibility test fails. The eighteen noiseless
compiled laws pass their separate sampled oracle checks. The paired
comparison establishes disagreement without identifying which execution
configuration is incorrect. Branching remains disabled in the live runner.
The large N=21 branch-enabled run has an unmatched baseline; its elapsed
time establishes neither equivalence nor speedup. Timings have one
observation per configuration and uncontrolled concurrent host work.

The fresh-instance replay holds the archived circuit and canonically sorted
serialized channels fixed. Ten 2048-shot cases vary isolated/mixed/reversed
batches and thread/shot limits. They produce non-reproduction of the large
folded discrepancy. Each case constructs a fresh simulator; the original
benchmark reuses instances across warm-ups and tiers. The original failure
therefore remains open. The final RCA script adds input-digest and options
guards after its first completed JSON, with the same experimental schedule.
The retained script additionally checks exact Python/package versions and
configuration/properties fixture hashes before simulation, records replay
source hashes, and sorts imports. The original completed JSON stays intact.

The later full-family replay supplies fifteen complete cases. Fresh
32768-shot folded trials differ in `qpe_no_feed_forward_s3` by
`0.2327880859375` and `0.23284912109375`, above the simultaneous bin radius
`0.036897112495406385`. The reused 2048-shot batch differs from the retained
branch-off baseline by `0.23583984375`, above radius
`0.14758844998162554`. A fresh simulator therefore fails as a repair.
The analysis allocates familywise alpha `1e-6` across all 608 bin comparisons
and 504 contrast-term estimates. Complete shot totals and unchanged QPY
before/after hashes rule out truncated draws and serialized-circuit mutation
on those measured surfaces. Dynamic members report branching; eligible
static members report measurement sampling. The internal cause remains open.
The portable reuse runner includes post-capture version/fixture guards;
`cpu_branching_reuse_probe_executed.py.gz` preserves the executed source bytes.

The initial raw noise hash includes generated error UUIDs. The follow-up
reconstructs the pinned FakeFez channels and checks two independently
constructed models. Its UUID-free digest still depends on error-record
list ordering, which varies between processes. The stored noise file
reproduces that historical digest exactly. Future semantic replay sorts
complete channel records while preserving instruction/probability ordering
inside each channel. The retained scripts expose the older ordering check,
so a cross-process replay can reject an otherwise equivalent reconstruction.

The serialized channel file omits custom noise passes because
`NoiseModel.to_dict()` excludes them. Delay relaxation uses a
`RelaxationNoisePass` with T1, T2, and dt from the pinned FakeFez
fixture. The completed report retains fixture-file hashes; its scripts
reconstruct the pass through `live_run.noise_simulator`. Serialized channels
alone cannot replay the full delay model. The live runner records a scoped
`noise_serialized_channels_sha256` field and separately binds the relevant
calibration inputs.

The GPU inventory is explicitly transcribed from command outputs, rather
than a rerunnable capture script. CUDA/CuPy passes the documented tiny FP64
checks; installed Aer exposes CPU only. NVML reports a driver/library
mismatch. Torch import fails its warning gate before GPU arithmetic. Free
CUDA memory is a point-in-time observation, never a reserved resource.

Run integrity and numerical recomputation from the repository root:

```sh
(
  set -eu
  PYTHON="${PYTHON:-$(command -v python3)}"
  PYTHONWARNINGS=error PYTHONDONTWRITEBYTECODE=1 \
    "$PYTHON" results/local_compute/verify_evidence.py
  (cd results/local_compute && sha256sum -c SHA256SUMS)
)
```

The verifier reads local files, checks every retained/source digest, binds
QPY and noise bytes to the completed report, and independently recomputes
the reported sampled incompatibility. The verifier performs zero simulator
or network operations. Preserve the archives and run exploratory simulations
in a separate output directory; evidence files remain immutable inputs.

A bounded replay uses the corrected channel-order comparison and writes into
a fresh temporary directory. Run from the repository root:

```sh
(
  set -eu
  PYTHON="${PYTHON:-$(command -v python3)}"
  replay_directory="$(mktemp -d)"
  for name in cpu_branching_inputs.qpy cpu_branching_qualification.json cpu_branching_noise_semantic.json; do
    gzip -dc "results/local_compute/$name.gz" > "$replay_directory/$name"
  done
  export QISKIT_NUM_PROCS=2 GOROROBA_WORKERS=1
  export PYTHONWARNINGS=error PYTHONDONTWRITEBYTECODE=1
  "$PYTHON" results/local_compute/cpu_branching_rca.py \
    --repo "$PWD" --out "$replay_directory"
  printf 'Replay evidence: %s\n' "$replay_directory"
)
```

The script binds retained QPY and serialized-channel identities, rebuilds
the delay pass from the pinned fixture, and guards service/Sampler
constructors. The resulting experiment remains a bounded local replay.
A changed package or fixture can reject reconstruction; installation or
QPU execution stays outside that command.

Recompute the full-family comparison without a simulator or service:

```sh
(
  set -eu
  PYTHON="${PYTHON:-$(command -v python3)}"
  analysis_directory="$(mktemp -d)"
  for name in cpu_branching_inputs.qpy cpu_branching_qualification.json cpu_branching_reuse_probe.json; do
    gzip -dc "results/local_compute/$name.gz" > "$analysis_directory/$name"
  done
  PYTHONWARNINGS=error PYTHONDONTWRITEBYTECODE=1 \
    "$PYTHON" results/local_compute/cpu_branching_reuse_analysis.py \
    --repo "$PWD" --out "$analysis_directory"
  printf 'Recomputed analysis: %s\n' "$analysis_directory"
)
```

A repeated noisy reuse probe also needs the decompressed serialized-channel
file and the bounded environment shown above, then invokes
`cpu_branching_reuse_probe.py` with the same `--repo` and `--out` arguments.
The probe writes a separate result; it grants zero QPU authorization.
