# Quandela Cloud quick start

Each step below names what it spends. Steps 1 to 4 spend nothing and need no
approval; step 5 sends a job, which waits for a written case and the user's
approval (README, "Use in this repository"). Every snippet runs under the
repository's `$PYTHON` with the Arch-packaged Perceval 1.3.1; the token file
is `~/.config/quandela/cloud-token`, named through `QUANDELA_TOKEN_FILE`.

## 1. Read the account and the platforms (no token for the public lists)

From an agent session, the `quandela` MCP server answers `qd_platforms`,
`qd_platform` (for example `sim:slos`, `qpu:belenos`), `qd_availability` and
`qd_usage`. From a shell, refresh the retained catalogue and its facts table:

```sh
export PYTHON="${PYTHON:-python3}"
QUANDELA_TOKEN_FILE="$HOME/.config/quandela/cloud-token" \
    "$PYTHON" scripts/qd_platform.py snapshot --out docs/evidence/quandela
"$PYTHON" scripts/qd_platform.py facts docs/evidence/quandela
"$PYTHON" scripts/qd_platform.py check docs/evidence/quandela \
    --agents AGENTS.md docs/notes/quandela/README.md
```

A changed table fails `check` until AGENTS.md and the README carry the new
facts table.

## 2. Simulate locally (free)

```python
import perceval as pcvl

processor = pcvl.Processor("SLOS", pcvl.BS())
processor.with_input(pcvl.BasicState([1, 1]))
print(processor.probs()["results"])  # |2,0>: 0.5, |0,2>: 0.5 (Hong-Ou-Mandel bunching)
sampler = pcvl.algorithm.Sampler(processor, max_shots_per_call=1000)
print(sampler.sample_count(1000)["results"])
```

`qd_simulate_local` runs the same backends for an agent: pass the circuit's
unitary as `real` and `imag` rows (`circuit.compute_unitary()` gives it) and
one 0 or 1 per mode as `input_photons`, for example `[1, 1]`. A noise model
(`pcvl.NoiseModel(transmittance=..., indistinguishability=..., g2=...)`) on a
local `Processor` reproduces a QPU's loss and photon quality figures from
`qd_platform`'s `perfs` before any remote job.

## 3. Connect Perceval to a platform without saving the token

```python
import os
from pathlib import Path

from perceval import QuandelaCommunicationLayer, RemoteComputer

token = Path(os.environ["QUANDELA_TOKEN_FILE"]).read_text(encoding="utf-8").strip()
qpu = RemoteComputer(QuandelaCommunicationLayer("qpu:belenos", token=token))
print(qpu.specs.constraints)  # max 24 modes, 12 photons
```

Constructing the computer reads the processor record (a GET). Perceval
never needs `RemoteConfig.save()`, which writes the token in plain text to
its persistent configuration.

## 4. Estimate shots and credits (free, client-side)

```python
import math

from perceval import BS, PS, BasicState, ExecutionFactory, Experiment

experiment = Experiment(BS() // PS(phi=math.pi / 4) // BS())
experiment.with_input(BasicState([1, 1]))
experiment.min_detected_photons_filter(2)
factory = ExecutionFactory(qpu, experiment, max_shots_per_call=1_000_000)
computation = factory.build_computation("sample_count")
computation.add_params(max_samples=10_000)
print(qpu.estimate_required_shots(computation, nsamples=10_000))
```

`estimate_required_shots` simulates the experiment against the platform's
transmittance and filter locally. On 2026-10-17 it answered 682042 shots for
10000 two-photon coincidences on `qpu:belenos`, which at 1e-06 credits per
shot is 0.68 credits; the per-job price the account's offer page shows adds
to it. A case quotes the estimate of its own experiment from a fresh
`qd_platform` read.

## 5. Send a job (after an approved case)

A retained case goes through the runner (README, "Runner"): `qd_platform.py
plan`, then `submit --approval`, then `collect`. The Perceval calls below are
what the runner wraps, for a notebook or an exploratory script.

```python
factory.default_job_name = "case-name"
qpu.start()
execution = factory.sample_count.execute_async(10_000)
# ... poll execution.status, or qd_job_status from an agent session
results = execution.get_results()
qpu.stop()
```

`max_shots_per_call` caps the shots one call may consume, so it is the
case's credit ceiling divided by the per-shot price. The token allows one
running and one queued job, and a job ends at 300 s. A simulator run on
`sim:belenos` or `sim:ascella` returns `computed_circuit` and
`computed_input`, which replay on the matching QPU without a second
compilation (`guide/user-guide/04-compilation.md`). The run then retains
what the README's last section lists under `results/quandela/runs/`.
