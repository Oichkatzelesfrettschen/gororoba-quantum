# Maintainer: eirikr <eirikr@localhost>
#
# qiskit-aer with the CUDA Thrust backend and the cuQuantum libraries
# (cuStateVec for the statevector method, cuTensorNet for tensor_network).
# Derived from the python-qiskit-aer recipe in this tree; the differences are
# the CUDA build environment below and the dependency set.
#
# Build knobs (environment, all optional):
#   CUQUANTUM_ROOT  prefix holding include/ and lib/ of cuquantum (default /usr;
#                   point it at an extracted cuquantum package to build before
#                   the package is installed, with makepkg --nodeps)
#   AER_CUDA_ARCH   CMake FindCUDA arch list (default 8.9+PTX: sm_89 cubin and
#                   compute_89 PTX for Ada GPUs)
#   AER_BUILD_JOBS  parallel compile jobs (default half the CPUs)
_pkgname=qiskit-aer
pkgname=python-$_pkgname-cuda
pkgver=0.17.2
pkgrel=2
_nlohmann_json_ver=3.10.2
pkgdesc="Qiskit Aer with the CUDA GPU backend and cuStateVec/cuTensorNet (cuQuantum) for NVIDIA Ada GPUs"
arch=(x86_64)
url="https://github.com/Qiskit/qiskit-aer"
license=(Apache-2.0)
depends=(
    'cuda>=13'
    'cuda<14'
    cuquantum
    'cutensor>=2.8'
    blas
    lapack
    fmt
    spdlog
    python-dateutil
    python-numpy
    python-psutil
    python-qiskit
    python-scipy
    python-sympy
)
optdepends=(
    'openmp: parallelization with OpenMP'
    'python-cvxpy: support convex optimization'
    'python-dask: parallel computing with task scheduling'
    'python-distributed: distributed task scheduler for Dask'
)
makedepends=(
    cmake
    ipython
    ninja
    pybind11
    python-build
    python-installer
    python-scikit-build
    python-setuptools
)
provides=("python-qiskit-aer=$pkgver")
conflicts=(python-qiskit-aer)
source=(
    $_pkgname-$pkgver.tar.gz::https://github.com/Qiskit/$_pkgname/archive/$pkgver.tar.gz
    nlohmann-json-$_nlohmann_json_ver.tar.gz::https://github.com/nlohmann/json/archive/refs/tags/v$_nlohmann_json_ver.tar.gz
    aer-cccl3-unary-function.patch
)
b2sums=('49dafc4cba948b7e3d474b0b8c73075cc5135a7c8559eebc2c0d5578c19868b4dc0a1dd4e6ab199f67a3996eb35ea11c9e0d8da9d49835bd2d7119774f64d954'
        'e7da213fb75d528b1f5425822f5b598e882f232a67670aaae2d8f89c76e72ee23fa3344d1acfef2b0338a6a423d17b231b7e047ff064c984c2ec7783b721a22c'
        'cf3f6507317591e12fa4fed5601c76ff469900cf3d5ec3eadd682319dbc48b279acddbbd893090c8f6489fddaa1e7b5b997395c20d08aa5ee5cbdf2d0b6e1788')

prepare() {
    cd $_pkgname-$pkgver
    sed -i -e '/conan/d' -e '/cmake/d' -e '/ninja/d' pyproject.toml

    # Aer pins its pybind11 module to C++14. CUDA 13 ships CCCL 3 (thrust, cub),
    # whose headers #error below C++17 (cub/util_cpp_dialect.cuh), and nvcc
    # rejects fmt 12's constexpr accessor over std::back_insert_iterator, which
    # is a literal type only from C++20; the module therefore builds as C++20.
    sed -i -e 's/^\( *\)CXX_STANDARD 14$/\1CXX_STANDARD 20\n\1CUDA_STANDARD 20/' cmake/FindPybind11.cmake
    grep -q 'CUDA_STANDARD 20' cmake/FindPybind11.cmake

    # Aer's CMake prefers OpenBLAS whenever libopenblas is installed, which
    # leaves libopenblas.so.0 in the module's NEEDED list outside the blas and
    # lapack virtuals. Skipping that probe sends it to the generic BLAS and
    # LAPACK search (libblas.so, liblapack.so), the AOCL providers on this host.
    sed -i -e 's/^\t\tfind_package(BLAS QUIET)$/\t\tset(BLAS_FOUND FALSE)/' \
           -e 's/^\t\tunset(BLA_VENDOR)$/\t\tset(BLA_VENDOR "Generic")/' CMakeLists.txt
    grep -q 'set(BLAS_FOUND FALSE)' CMakeLists.txt
    grep -q 'set(BLA_VENDOR "Generic")' CMakeLists.txt

    # CCCL 3 removed thrust::unary_function; the three Aer functors that derive
    # from it take an equivalent AER::unary_function.
    patch -Np1 -i "$srcdir"/aer-cccl3-unary-function.patch
}

build() {
    # The header-only nlohmann_json from [extra] is unusable:
    # https://github.com/Qiskit/qiskit-aer/issues/1742
    local cmake_options=(
        -B build
        -D JSON_BuildTests=OFF
        -D CMAKE_BUILD_TYPE=None
        -D CMAKE_INSTALL_PREFIX=/usr
        -D CMAKE_INSTALL_LIBDIR=/usr
        -D JSON_MultipleHeaders=OFF
        -D CMAKE_POLICY_VERSION_MINIMUM=3.5
        -S json-$_nlohmann_json_ver
        -W no-dev
    )
    cmake "${cmake_options[@]}"
    cmake --build build --verbose
    DESTDIR=tmp cmake --install build

    local jobs="${AER_BUILD_JOBS:-$(( $(nproc) / 2 ))}"
    local cuquantum_root="${CUQUANTUM_ROOT:-/usr}"

    cd $_pkgname-$pkgver
    export DISABLE_CONAN=ON
    export CPATH="$srcdir/tmp/usr/include:$cuquantum_root/include:$CPATH"
    export LIBRARY_PATH="$cuquantum_root/lib:$LIBRARY_PATH"
    export nlohmann_json_DIR="$srcdir"/tmp/usr/cmake/nlohmann_json

    # CUDA Thrust backend with cuQuantum. Aer's CMake reads these variables
    # from the environment (CMakeLists.txt, AER_THRUST_BACKEND and the
    # non-wheel branch under AER_THRUST_BACKEND STREQUAL "CUDA").
    export CUDA_PATH=/opt/cuda
    export PATH="/opt/cuda/bin:$PATH"
    export CUDAHOSTCXX="${CUDAHOSTCXX:-/usr/bin/g++}"
    export AER_THRUST_BACKEND=CUDA
    export AER_CUDA_ARCH="${AER_CUDA_ARCH:-8.9+PTX}"
    export AER_ENABLE_CUQUANTUM=ON
    export CUQUANTUM_ROOT="$cuquantum_root"
    # Plain package name: the "gpu" name variants add pip nvidia-* requirements.
    export QISKIT_ADD_CUDA_REQUIREMENTS=false

    export MAKEFLAGS="-j$jobs"
    export CMAKE_BUILD_PARALLEL_LEVEL="$jobs"
    python -m build --wheel --no-isolation
}

package() {
    cd $_pkgname-$pkgver
    python -m installer --destdir="$pkgdir" dist/*.whl
    install -D -m644 LICENSE.txt "$pkgdir"/usr/share/licenses/$pkgname/LICENSE
}
