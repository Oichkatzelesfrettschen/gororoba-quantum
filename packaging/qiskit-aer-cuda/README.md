# Native Aer CUDA package

The PKGBUILD replaces the Arch `python-qiskit-aer` package with upstream
Aer 0.17.2 compiled for CUDA compute capability 8.9. Python metadata keeps
the distribution name `qiskit-aer` and version `0.17.2`, so the repository's
runtime pin and version lookup continue to address the installed package.
The `provides` and `conflicts` fields make pacman own the replacement.

The build uses the system Python 3.14 ABI, CUDA 13.4 toolkit, GCC, OpenBLAS,
and OpenMP. The dependency on `openblas` follows the actual owner of
`libopenblas.so.0`. The build downloads pinned source archives and uses a
private nlohmann-json 3.10.2 single header, matching the CPU package's
serialization compatibility boundary. The private header stays outside
the installed package. The build creates an isolated Python 3.14 environment
from eight pinned wheel sources. `build-requirements.txt` records the full
toolchain dependency set and hashes. `makepkg` checks every source hash;
`uv pip sync` installs the declared wheels offline. The isolated environment
excludes the host's undeclared setuptools plugins, including the global
setuptools-scm file finder that warns for fixed-version projects. Conan
and build-time dependency downloads stay disabled.

`AER_THRUST_BACKEND=CUDA` selects Aer native CUDA kernels.
`AER_CUDA_ARCH=8.9` fixes the target architecture. Optional cuQuantum,
MPI, and CUDA wheel dependencies remain disabled; the system CUDA toolkit
supplies the native build. The build uses half the available CPUs as compilation jobs, at least one, and treats
host and NVCC warnings as errors. Compiler failures require a recorded
source-level diagnosis before changing warning policy.

The retained patches repair explicit toolchain compatibility failures:

- Setuptools receives the SPDX license expression in place of the deprecated
  license classifier. The source manifest lists paths present in the archive.
- CMake uses `CUDAToolkit` and `Python` package discovery. The private JSON
  prefix survives both stages of upstream dependency lookup.
- CUDA and host compilation use C++20. CUDA 13's CCCL headers require at
  least C++17; system fmt 12.2 requires C++20 for its constexpr output-iterator
  constructor under NVCC. The C++17 native probe fails, and C++20 passes.
  Aer uses the exported `spdlog::spdlog` target so shared-library definitions,
  includes, and the fmt dependency reach the native compilation and linker.
- The SIMD alias selects the same vector types through specialization,
  preserving attributes. Two unused parameter names are removed.
- The CUDA binding compile preloads `pyconfig.h` macros before NVCC's implicit
  CUDA runtime header. Python's feature macros therefore precede glibc headers;
  host compilation retains the native header declarations.
- The isolated scikit-build tool uses CMake's current spelling of its existing
  unused-command-line option.
- Removed Thrust unary-function bases become explicit `argument_type` and
  `result_type` aliases. The three functor bodies remain byte-identical.
- Explicit casts retain the discarded `std::unique` return and the unsigned
  LAPACK workspace-query sentinel from Aer 0.17.2. The casts preserve the
  existing validation and matrix-product-state operations.
- The OpenMP threshold local carries `[[maybe_unused]]` because NVCC's device
  pass ignores its references inside host OpenMP pragmas. Threshold arithmetic
  and host parallel conditions remain unchanged.
- The 226 `-Werror=unused-parameter` diagnostics occurring under `-Wall -Wextra -Werror`
  are resolved by annotating unused arguments with `[[maybe_unused]]` in function
  headers and lambdas, or removing unused dummy parameter names across binding
  mixins, framework utilities, and quantum simulators.
- The 57 compiler diagnostics occurring under GCC 16.2.1 and NVCC 13.4 fatal warning flags:
  * 4 implicit fallthrough switch branches in `operations.hpp`, `noise_model.hpp`,
    and `state_controller.hpp` are resolved with explicit `break;` statements.
  * NVCC EDG frontend non-void return error in `noise_model.hpp::sample_channel` is
    resolved with an explicit `return cmatrix_t();`.
  * 14 redundant `std::move(pydata)` returns in pybind data mixins (pessimizing moves
    preventing Named Return Value Optimization) are converted to direct `return pydata;`.
  * 3 deprecated pybind11 `obj.get_type()` calls are replaced with `py::type::handle_of(obj)`.
  * OpenMP parallel for loop bounds declaration in `densitymatrix.hpp` is moved before
    the OpenMP pragma to prevent C++ scope warnings.
  * Base class copy constructor initializers are added in `DensityMatrix` and `UnitaryMatrix`.
  * 20 signed/unsigned comparison mismatches are resolved via explicit `static_cast`.
  * Deprecated copy-assignment warning in `Chunk` is resolved with `Chunk &operator=(const Chunk &) = default;`.
  * Thrust `iterator_traits<Iterator>::difference_type` is fully qualified in `thrust_kernels.hpp`.
  * Scoped diagnostic pragmas suppress false-positive dangling-reference warnings in JSON deserializers.

Aer declares spdlog 1.9.2. A native probe of that release's bundled fmt 8.0.1
fails GCC 16's dangling-reference and overlapping-copy diagnostics at `-O3`.
The package therefore uses the installed spdlog 1.17/fmt 12.2 headers with
their working C++20 dialect; the package patches preserve logging operations.

Upstream Aer retains its `-use_fast_math` CUDA flag. Double precision and
the build metadata identify distinct aspects of the qualified implementation.

Run the package build from a writable scratch directory containing the
PKGBUILD, smoke check, requirements lock, and six patches. Set `SRCDEST`,
`PKGDEST`, `BUILDDIR`, and `LOGDEST` to that directory when the host's global
makepkg cache requires elevated access. `makepkg --cleanbuild --force --log` builds the wheel,
installs the wheel under temporary storage for checks, and produces the
pacman archive. The check imports the staged package, requires native CPU
and GPU availability, and executes a bounded noisy measurement/reset/
feed-forward circuit with fixed double-precision density matrices and
shot branching disabled. The smoke test checks the analytic noisy law;
the retained full workload qualification remains an independent gate.

The package installs `qiskit_aer/native_cuda_build.json` beside its Python
modules. The metadata records source hashes, CMake options, compiler and
CUDA versions, Python ABI, warning policy, and dependency versions. Approval
records can bind the metadata digest and installed extension digest to
distinguish native builds that share the `0.17.2` distribution version.

Inspect the package file list, dependency metadata, linked shared
libraries, Python ABI, and CPU/GPU results before installation. Retain a
usable CPU rollback package with dependency metadata that matches the
installed BLAS owner. Install and rollback through pacman; direct wheel
installation would bypass package ownership. The package changes neither
the NVIDIA driver nor any system service.

Upstream build definitions:

- [Aer CMake 0.17.2](https://github.com/Qiskit/qiskit-aer/blob/0.17.2/CMakeLists.txt)
- [Aer Python build metadata](https://github.com/Qiskit/qiskit-aer/blob/0.17.2/pyproject.toml)
- [Aer distribution and CUDA requirements](https://github.com/Qiskit/qiskit-aer/blob/0.17.2/setup.py)
- [Arch JSON compatibility issue](https://github.com/Qiskit/qiskit-aer/issues/1742)
