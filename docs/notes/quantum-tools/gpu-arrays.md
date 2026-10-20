# torch, cupy, jax (and numba CUDA)

## NAME

torch 2.14.1, cupy 14.2.0, jax 0.9.0 (jaxlib self-built, CPU), numba 0.68.0
(with `numba.cuda`) -- array libraries that quimb, cotengra and autoray
dispatch to for GPU contraction.

## SYNOPSIS

```python
import torch, cupy
torch.tensor(a, device="cuda") @ torch.tensor(a, device="cuda")
cupy.asarray(a) @ cupy.asarray(a)
```

| Substrate | Status |
| --- | --- |
| Build host | python-pytorch-opt-cuda (torch 2.14.1, CUDA available on the RTX 4070 Ti), python-cupy 14.2.0 (one device), python-jax 0.9.0 with a CPU-only jaxlib, python-numba 0.68.0 with python-numba-cuda (`numba.cuda.is_available()` is True) |
| Kaggle | torch from the image (2.11.0+cu128 on the T4 probe, 2.11.0+cpu on the CPU probe); numba 0.68.0 is pinned by the `quantum-tools` group; cupy and jax are neither pinned nor recorded by the repository's probes |

The Arch package list shows python-pytorch-opt-cuda, python-cupy, python-jax,
python-jaxlib, python-optax and python-numba-cuda; the repository's own
requirements mention torch only for python-octonion and python-cayley-dickson
(gororoba_quantum/AGENTS.md, "Python stack on the build host").

## CAPABILITIES IN THIS REPOSITORY

- GPU tensor contraction: quimb circuits converted with
  `apply_to_arrays` run `local_expectation` on `torch` (CPU or CUDA) and on
  `cupy` and agree with numpy to 10 digits ([quimb.md](quimb.md), example).
- Complex128 matrix products on the GPU: the example below matches numpy.
- JAX on this host is CPU only: `jax.devices()` returns `['cpu']` and the
  library logs that an NVIDIA GPU may be present but a CUDA-enabled jaxlib is
  not installed. JAX is the only route a Kaggle TPU would serve, and the
  repository records that this account reaches no TPU through the CLI
  (`kaggle_kernel/AGENTS.md`).
- Aer's GPU path is separate: it uses its own CUDA build, not torch or cupy
  ([qiskit-aer.md](qiskit-aer.md)).

## API ENTRY POINTS

Entry points used here (the full namespaces are in the libraries' own
documentation):

- torch: `torch.tensor(x, device="cuda")`, `torch.cuda.is_available()`,
  `torch.einsum`, `Tensor.cpu().numpy()`.
- cupy: `cupy.asarray`, `cupy.asnumpy`, `cupy.cuda.runtime.getDeviceCount()`.
- jax: `jax.devices()`.

## EXAMPLES

Marked as a GPU example.

```python
# gpu
import importlib.metadata as md, logging, warnings
warnings.filterwarnings("ignore")
logging.disable(logging.CRITICAL)
import numpy as np
import torch, cupy
import jax

print("torch", md.version("torch"), "cuda available:", torch.cuda.is_available(), "|", torch.cuda.get_device_name(0))
print("cupy", md.version("cupy"), "devices:", cupy.cuda.runtime.getDeviceCount())
print("jax", md.version("jax"), "devices:", [d.platform for d in jax.devices()])

a = (np.random.default_rng(0).normal(size=(256, 256)) + 0j).astype(np.complex128)
ref = a @ a
t = (torch.tensor(a, device="cuda") @ torch.tensor(a, device="cuda")).cpu().numpy()
c = cupy.asnumpy(cupy.asarray(a) @ cupy.asarray(a))
print("complex128 matmul, torch-cuda vs numpy max dev:", float(abs(t - ref).max()) < 1e-10, " cupy:", float(abs(c - ref).max()) < 1e-10)
```

Output:

```text
torch 2.14.1 cuda available: True | NVIDIA GeForce RTX 4070 Ti
cupy 14.2.0 devices: 1
jax 0.9.0 devices: ['cpu']
complex128 matmul, torch-cuda vs numpy max dev: True  cupy: True
```

## INTEROP WITH QISKIT

Via NumPy: `Operator(...).data` and `Statevector(...).data` convert with
`torch.tensor` or `cupy.asarray`. quimb converts its own tensors
([quimb.md](quimb.md)). No Qiskit object accepts a GPU array directly.

## CPU AND GPU

| Library | Host | Kaggle GPU kernel |
| --- | --- | --- |
| torch | CUDA | CUDA from the image |
| cupy | CUDA | not installed by the repository |
| jax | CPU only | not recorded |
| numba CUDA | available; not exercised | not recorded |

## TRAPS

- `import torch` prints a `pynvml` deprecation warning (FutureWarning) on
  this host.
- A cupy import with an unwritable home directory fails creating its kernel
  cache (`PermissionError` on the cache path); set `CUPY_CACHE_DIR` for a
  sandbox.
- Mixing array types in one contraction raises `TypeError` (quimb with a torch
  network and a numpy operator, observed): convert the operator too.
- GPU timing figures need warm-up: the first call of each backend in the quimb
  example was several seconds slower than the second.
- Do not set `CUDA_VISIBLE_DEVICES=""` and expect `device="GPU"` Aer runs to
  work: they raise `RuntimeError: No CUDA device available!`.

## LICENSE

torch: Apache-2.0 and BSD/MIT/BSL components (package metadata); cupy: MIT;
jax and jaxlib: Apache-2.0; numba: BSD.
